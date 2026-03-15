<<<<<<< HEAD
"""
Ozon 商品数据标准化转换器 (Ozon Transformer) — v1.3.0
------------------------------------------------------
将从 1688 采集的原始数据，清洗并映射为 Ozon Global 平台的标准上架字段格式。

核心功能：
1. 标题清洗 - 去除 1688 营销牛皮词（厂家直销、一件代发等）
2. 单位转换 - 自动将 CM → MM，KG → G（Ozon 物流计算要求）
3. 字段映射 - 将中文属性键名映射到 Ozon 标准英文字段
4. ✨ 多语言翻译 - 中文标题自动翻译为俄文/英文（Google Translate 免费 API）
5. JSON 导出 - 输出 ozon_export.json，可对接 ERP 或手动导入

v1.3.0 改进：
  ✅ 新增翻译模块 — 使用 `translators` 库（免费，无需 API Key）
  ✅ 翻译结果缓存 — 避免重复翻译相同文本
  ✅ 翻译失败降级 — 翻译失败时保留中文原文 + 警告标记

参考: PROJECT_REVIEW.md - "Scrape to List" (采集即可上架) 策略
"""

import re
import json
import os


class OzonTransformer:
    """
    1688 → Ozon Global 商品数据标准化转换器。

    支持标题清洗、单位转换、属性映射和多语言翻译（中→俄/英）。
    """

    # ------------------------------------------------------------------ #
    # 1688 标题中常见的营销垃圾词（用于清洗标题）
    # ------------------------------------------------------------------ #
    MARKETING_BUZZWORDS = [
        # 销售话术
        "厂家直销", "一件代发", "批发", "工厂直销", "源头直供",
        "爆款", "爆爆款", "超级爆款", "抖音爆款", "网红款",
        "热销", "热卖", "畅销", "好评如潮", "超值",
        "特价", "限时特价", "秒杀价", "清仓", "亏本价",
        # 品质描述（夸张）
        "高品质", "超高品质", "精品", "顶级", "奢华",
        "超耐用", "超耐咬", "超大", "加大", "大号",
        # 快递/发货
        "包邮", "顺丰包邮", "三天达", "次日达", "极速发货",
        # 其他
        "新款", "新品", "2024年新款", "2025年新款", "2026年新款",
        "跨境", "出口款", "外贸款", "OEM", "ODM",
        "可定制", "支持定制", "可印logo", "可印LOGO",
        "买1发2", "买二发三", "买3发5",
    ]

    # ------------------------------------------------------------------ #
    # 中文属性键名 → Ozon 标准英文字段映射
    # ------------------------------------------------------------------ #
    ATTRIBUTE_MAP = {
        # 物理规格
        "重量": "weight_g",
        "净重": "weight_g",
        "毛重": "gross_weight_g",
        "长": "length_mm",
        "宽": "width_mm",
        "高": "height_mm",
        "长度": "length_mm",
        "宽度": "width_mm",
        "厚度": "height_mm",
        "尺寸": "dimensions",
        "规格": "dimensions",
        # 商品属性
        "颜色": "color",
        "颜色分类": "color",
        "材质": "material",
        "面料": "material",
        "适用年龄": "age_group",
        "品牌": "brand",
        "型号": "model",
        "产品类别": "category",
        "功能": "features",
        "使用场景": "use_scenario",
        # 包装
        "包装重量": "package_weight_g",
        "包装尺寸": "package_dimensions",
        "件数": "quantity_per_pack",
        "套装": "is_set",
        # 供应链
        "最小起订量": "min_order_qty",
        "起批量": "min_order_qty",
        "发货地": "ship_from",
        "供应商": "supplier",
    }

    # ------------------------------------------------------------------ #
    # Ozon 标准属性 ID 映射 (v1.4.0 增强)
    # 用于直接构造 API 负载中的 attributes 列表
    # ------------------------------------------------------------------ #
    OZON_ATTRIBUTE_IDS = {
        "brand": 31,                # 品牌
        "material": 8229,           # 材质
        "color": 10091,             # 颜色
        "target_audience": 9163,    # 目标人群
        "type": 8229,               # 类型 (通常与材质公用或动态查表)
        "model": 77,                # 型号
        "origin_country": 4389,     # 原产国 (通常设为 "China")
        "package_qty": 84,          # 包装件数
    }

    # ------------------------------------------------------------------ #
    # Ozon 品类关键词映射（根据商品标题自动推断品类）
    # ------------------------------------------------------------------ #
    CATEGORY_KEYWORDS = {
        "猫": "Pet Supplies / Cat Toys",
        "狗": "Pet Supplies / Dog Toys",
        "宠物": "Pet Supplies",
        "玩具": "Toys & Games",
        "球": "Sports & Outdoors / Balls",
        "手机": "Electronics / Mobile Phones",
        "耳机": "Electronics / Headphones",
    }

    def __init__(self):
        """
        初始化转换器，加载翻译引擎。
        """
        # 翻译缓存，避免重复翻译相同文本
        self._translation_cache = {}
        # 翻译库可用性标志
        self._translator_available = self._check_translator()

    def _check_translator(self):
        """
        检测翻译库 (translators) 是否已安装。
        未安装时打印提示，降级为不翻译模式。

        返回:
            True — 翻译库可用 / False — 翻译库不可用
        """
        try:
            import translators
            return True
        except ImportError:
            print(
                "[OzonTransformer] ⚠️ 翻译库 'translators' 未安装，标题将保留中文。\n"
                "                   安装命令: pip install translators"
            )
            return False

    def translate_text(self, text, target_lang="ru"):
        """
        将中文文本翻译为目标语言（默认俄文）。

        翻译策略：
          1. 优先使用 Google 翻译
          2. Google 失败时回退到 Bing 翻译
          3. 全部失败时返回原文 + ⚠️ 标记

        参数:
            text:        待翻译的中文文本
            target_lang: 目标语言代码（'ru' = 俄文, 'en' = 英文）

        返回:
            翻译后的文本字符串
        """
        if not self._translator_available:
            return f"⚠️ [需手动翻译] {text}"

        if not text or not text.strip():
            return text

        # 检查缓存（按 text+target_lang 组合做 key）
        cache_key = f"{text}|{target_lang}"
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]

        import translators as ts

        # 多引擎回退翻译
        translation_engines = ["google", "bing", "baidu"]
        for engine in translation_engines:
            try:
                result = ts.translate_text(
                    text,
                    translator=engine,
                    from_language="zh",
                    to_language=target_lang,
                )
                if result and result.strip():
                    self._translation_cache[cache_key] = result.strip()
                    return result.strip()
            except Exception as e:
                print(f"[Translator] {engine} 翻译失败: {e}，尝试下一个引擎...")
                continue

        # 全部引擎失败，返回原文并标记
        fallback = f"⚠️ [翻译失败] {text}"
        self._translation_cache[cache_key] = fallback
        return fallback

    def clean_title(self, raw_title: str, max_length: int = 200) -> str:
        """
        清洗 1688 商品标题：
        - 去除营销垃圾词
        - 移除非法字符和多余空格
        - 确保不破坏核心品牌和关键词
        """
        if not raw_title:
            return "Untitled Product"
            
        title = raw_title
        # 批量替换垃圾词
        for word in self.MARKETING_BUZZWORDS:
            title = title.replace(str(word), "")

        # 正则清理冗余
        title = re.sub(r"[\[\]【】()（）]", " ", title) # 括号通常包含营销信息
        title = re.sub(r"\s+", " ", title) # 压缩空格
        
        # 截断（考虑到 Python 字符串切片语法，使用 int 索引避免 lint 报错）
        clean_res = title.strip()
        if len(clean_res) > max_length:
            clean_res = clean_res[0:max_length]
            
        return clean_res if len(clean_res) > 5 else raw_title[0:min(len(raw_title), max_length)]

    def convert_units(self, attributes: dict) -> dict:
        """
        Ozon 单位标准化转换：
        - 重量：kg → g（×1000），g 保留
        - 尺寸：cm → mm（×10），mm 保留

        参数:
            attributes: 原始属性字典（中文键名）

        返回:
            转换后的属性字典
        """
        converted = dict(attributes)

        for key, value in attributes.items():
            value_str = str(value).strip().lower()

            # 重量转换：kg → g
            kg_match = re.search(r"([\d.]+)\s*kg", value_str, re.IGNORECASE)
            g_match = re.search(r"([\d.]+)\s*g(?!b)", value_str, re.IGNORECASE)

            if "重" in key or "weight" in key.lower():
                if kg_match:
                    grams = float(kg_match.group(1)) * 1000
                    converted[key] = f"{grams:.0f}g"
                elif g_match:
                    pass  # 已经是 g，保留

            # 尺寸转换：cm → mm
            cm_match = re.search(r"([\d.]+)\s*cm", value_str, re.IGNORECASE)
            mm_match = re.search(r"([\d.]+)\s*mm", value_str, re.IGNORECASE)

            if any(dim in key for dim in ["长", "宽", "高", "厚", "尺寸", "规格"]):
                if cm_match:
                    mm = float(cm_match.group(1)) * 10
                    converted[key] = value_str.replace(
                        cm_match.group(0), f"{mm:.0f}mm"
                    )
                elif mm_match:
                    pass  # 已经是 mm，保留

        return converted

    def calculate_price(self, cny_price: float, weight_g: float) -> str:
        """
        基于成本预估模型的 Ozon 卢布定价机制
        包含：采购价、国内物流、国际物流、汇率与毛利率
        """
        exchange_rate_cny_to_rub = 13.0  # 1 CNY ≈ 13 RUB (固定参考值)
        profit_margin = 0.40             # 预期毛利率 40%
        domestic_shipping_cny = 3.0      # 国内快递成本预估
        intl_shipping_per_kg_cny = 45.0  # 国际物流成本 (约45元/KG)

        if not cny_price or cny_price <= 0:
            cny_price = 10.0 # 无抓取到价格时的防错兜底采购价

        # 重量换算为千克
        weight_kg = (weight_g or 500) / 1000.0
        intl_shipping_cny = weight_kg * intl_shipping_per_kg_cny

        total_cost_cny = cny_price + domestic_shipping_cny + intl_shipping_cny
        final_price_rub = total_cost_cny * exchange_rate_cny_to_rub * (1 + profit_margin)
        
        return str(int(final_price_rub))

    def map_to_ozon(self, product: dict) -> dict:
        """
        将 1688 商品数据映射为 Ozon Global 标准上架字段结构。
        包含自动翻译标题为俄文和英文。

        参数:
            product: 原始 1688 商品字典

        返回:
            Ozon 标准格式的商品字典
        """
        raw_title = product.get("title", "未知商品")
        raw_attrs = product.get("attributes", {})
        source_url = product.get("url", "")

        # 1. 清洗标题
        clean_title = self.clean_title(raw_title)

        # 2. 翻译标题（中文 → 俄文 + 英文）
        title_ru = self.translate_text(clean_title, target_lang="ru")
        title_en = self.translate_text(clean_title, target_lang="en")
        print(f"[Translator] 中文: {clean_title[:40]}")
        print(f"[Translator] 俄文: {title_ru[:40]}")
        print(f"[Translator] 英文: {title_en[:40]}")

        # 3. 转换单位
        converted_attrs = self.convert_units(raw_attrs)

        # 4. 映射属性到英文字段
        ozon_attrs = {}
        unmapped_attrs = {}

        for cn_key, value in converted_attrs.items():
            en_key = None
            for pattern, target_field in self.ATTRIBUTE_MAP.items():
                if pattern in cn_key:
                    en_key = target_field
                    break

            if en_key:
                ozon_attrs[en_key] = value
            else:
                unmapped_attrs[cn_key] = value

        # 5. 提取物理规格 (并补充基于品类的合理兜底尺寸避免暴雷)
        default_weight, default_l, default_w, default_h = 500, 200, 200, 100
        if "猫" in raw_title or "狗" in raw_title or "玩具" in raw_title:
            default_weight, default_l, default_w, default_h = 200, 150, 100, 50
        elif "手机" in raw_title or "数码" in raw_title or "电子" in raw_title:
            default_weight, default_l, default_w, default_h = 400, 180, 100, 50
        elif "衣" in raw_title or "服饰" in raw_title or "裤" in raw_title:
            default_weight, default_l, default_w, default_h = 300, 300, 200, 50

        weight_g = self._extract_number(
            ozon_attrs.get("weight_g", "") or ozon_attrs.get("gross_weight_g", ""),
            fallback=default_weight
        )
        length_mm = self._extract_number(ozon_attrs.get("length_mm", ""), fallback=default_l)
        width_mm = self._extract_number(ozon_attrs.get("width_mm", ""), fallback=default_w)
        height_mm = self._extract_number(ozon_attrs.get("height_mm", ""), fallback=default_h)

        # 6. 推断价格
        raw_price = product.get("price", "N/A")
        cny_price = self._extract_number(raw_price, fallback=0.0)

        # 7. 从 URL 中提取 offer_id
        offer_id_match = re.search(r"offerId=(\d+)", source_url)
        if not offer_id_match:
            # 尝试从路径中提取 offer ID（新版 URL 格式）
            offer_id_match = re.search(r"/offer/(\d+)\.html", source_url)
        offer_id = f"1688-{offer_id_match.group(1)}" if offer_id_match else f"1688-{abs(hash(source_url)) % 100000}"

        # 8. 自动推断 Ozon 品类
        suggested_category = "General"
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in raw_title:
                suggested_category = category
                break

        # 9. 构造 Ozon API 标准属性列表 (Complex Attributes)
        # Ozon 要求属性以 {"complex_id": 0, "id": xxx, "values": [{"value": "xxx"}]} 格式提交
        api_attributes = []
        
        # 遍历已知的映射 ID 进行增强填充
        known_mappings = {
            "material": self.OZON_ATTRIBUTE_IDS.get("material"),
            "brand": self.OZON_ATTRIBUTE_IDS.get("brand"),
            "color": self.OZON_ATTRIBUTE_IDS.get("color"),
            "model": self.OZON_ATTRIBUTE_IDS.get("model"),
        }

        for attr_key, attr_id in known_mappings.items():
            val = ozon_attrs.get(attr_key)
            if val and attr_id:
                api_attributes.append({
                    "id": attr_id,
                    "values": [{"value": str(val)}]
                })

        # 默认必填项补全 (原产国)
        api_attributes.append({
            "id": self.OZON_ATTRIBUTE_IDS.get("origin_country", 4389),
            "values": [{"value": "China"}]
        })

        # 10. 组装 Ozon 标准字段
        ozon_product = {
            # ---- 核心字段 ----
            "offer_id": offer_id,
            "name": title_ru,                   # ✨ 俄文标题（Ozon 主语言）
            "name_en": title_en,                # ✨ 英文标题（备用）
            "name_cn": clean_title,             # 清洗后的中文标题（内部参考）
            "name_raw_1688": raw_title,         # 原始标题（溯源）
            "price_cny": cny_price,
            "price_rub": self.calculate_price(cny_price, weight_g),

            # ---- Ozon 物流必填 ----
            "weight_g": weight_g,
            "depth_mm": length_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,

            # ---- 分类 ----
            "suggested_ozon_category": suggested_category,

            # ---- 图片 ----
            "images": product.get("images", []),

            # ---- 属性集 ----
            "attributes_mapped": ozon_attrs,
            "attributes_unmapped": unmapped_attrs,
            "attributes_mapped_api": api_attributes, # ✨ 直接喂给 API 的格式

            # ---- 溯源 ----
            "source_url_1688": source_url,
            "vat": "0", 
        }

        return ozon_product

    def transform_batch(self, products: list) -> list:
        """
        批量转换商品列表。

        参数:
            products: 原始 1688 商品字典列表

        返回:
            Ozon 标准格式商品列表
        """
        ozon_list = []
        for i, product in enumerate(products):
            try:
                ozon_item = self.map_to_ozon(product)
                ozon_list.append(ozon_item)
                print(f"[OzonTransformer] ({i+1}/{len(products)}) 转换完成: {ozon_item['offer_id']}")
            except Exception as e:
                import traceback
                print(f"[OzonTransformer] 转换失败 ({i+1}): {e}")
                traceback.print_exc()
        return ozon_list

    def export_json(self, ozon_products: list, output_dir: str = "1688_products") -> str:
        """
        将 Ozon 标准商品列表导出为 ozon_export.json 文件。

        参数:
            ozon_products: Ozon 标准格式商品列表
            output_dir: 输出目录

        返回:
            导出文件的完整路径
        """
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "ozon_export.json")

        export_data = {
            "platform": "Ozon Global",
            "source": "1688.com",
            "total_products": len(ozon_products),
            "export_note": "物流体积与预估售价机制已激活",
            "translation_note": "name(俄文) 和 name_en(英文) 为自动翻译，建议人工校对后使用",
            "products": ozon_products,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"[OzonTransformer] ✅ Ozon 导出完成: {output_path}")
        print(f"[OzonTransformer] 共 {len(ozon_products)} 件商品")
        return output_path

    @staticmethod
    def _extract_number(text: str, fallback=0.0):
        """
        从字符串中提取第一个数字。

        参数:
            text: 输入字符串
            fallback: 未找到时的默认返回值

        返回:
            提取到的浮点数，或 fallback
        """
        if not text:
            return fallback
        match = re.search(r"[\d.]+", str(text))
        return float(match.group()) if match else fallback
=======
# -*- coding: utf-8 -*-
"""
Ozon 数据转换模块 (OzonTransformer)
----------------------------------
负责将 1688 采集的数据清洗、翻译并映射为 Ozon V3 API 标准格式。
"""

import json
import os
import re
from src.modules.unit_converter import UnitConverter
# 尝试导入翻译器，如果不存在则降级
try:
    from src.modules.translator import Translator
except ImportError:
    Translator = None

class OzonTransformer:
    """
    Ozon 数据转换器
    
    职责：
    1. 清洗标题 (去除营销词)。
    2. 转换单位 (CM->MM, KG->G)。
    3. 翻译文本 (中->俄/英)。
    4. 映射字段到 Ozon V3 import 结构。
    """
    
    def __init__(self):
        self.converter = UnitConverter()
        self.translator = Translator() if Translator else None

    def map_to_ozon(self, data: dict) -> dict:
        """
        将采集的 1688 数据映射为 Ozon 商品结构。
        """
        print("OzonTransformer: 正在转换数据...")
        
        # 1. 基础字段清洗
        original_title = data.get("title", "")
        clean_title = self._clean_title(original_title)
        
        # 2. 翻译
        if self.translator:
            try:
                name_ru = self.translator.translate_to_ru(clean_title)
                desc_ru = self.translator.translate_to_ru(data.get("description", "")[:200]) # 限制长度
            except Exception as e:
                print(f"OzonTransformer: 翻译失败 - {e}")
                name_ru = clean_title
                desc_ru = data.get("description", "")
        else:
            name_ru = clean_title
            desc_ru = data.get("description", "")

        # 3. 价格处理 (假设 1688 价格是 CNY，Ozon 需要 RUB/USD，这里简单透传，实际需汇率转换)
        # Ozon API 要求 price 是字符串或数字
        price = data.get("price", "100")
        
        # 4. 尺寸重量处理
        # 尝试从 attributes 中寻找包装尺寸/重量
        attrs = data.get("attributes", {})
        weight_g = 0
        width_mm = 0
        height_mm = 0
        depth_mm = 0
        
        for k, v in attrs.items():
            if "重" in k:
                weight_g = self.converter.convert_weight(v)
            if "尺寸" in k or "规格" in k:
                # 简单处理：假设是长宽高
                # 实际可能需要更复杂的解析，这里简化为单一维度
                dim = self.converter.convert_dimension(v)
                width_mm = dim
                height_mm = dim
                depth_mm = dim

        # 默认值兜底
        if weight_g == 0: weight_g = 500
        if width_mm == 0: width_mm = 100
        if height_mm == 0: height_mm = 100
        if depth_mm == 0: depth_mm = 100

        # 5. 图片处理 (过滤 SVG/TPS)
        valid_images = [
            img for img in data.get("images", [])
            if not img.lower().endswith('.svg') and not img.lower().endswith('.tps')
        ]
        
        # 6. 构建 Ozon Item 结构 (V3 /v2/product/import)
        # 参考 Ozon API 文档
        item = {
            "offer_id": data.get("url", "").split("/")[-1].replace(".html", "") or "1688_item",
            "name": name_ru,
            "price": price,
            "vat": "0", # 免税
            "barcode": "",
            "description_category_id": 17028760, # 示例：猫玩具类目ID
            "type_id": 17028760, # 必须字段：通常与 category_id 相同或相关
            "primary_image": valid_images[0] if valid_images else "",
            "images": valid_images,
            "weight": weight_g,
            "width": width_mm,
            "height": height_mm,
            "depth": depth_mm,
            "dimension_unit": "mm",
            "weight_unit": "g",
            "currency_code": "CNY", # 或者 RUB
            "attributes": [
                # 示例属性
                {
                    "complex_id": 0,
                    "id": 85, # Brand
                    "values": [{"dictionary_value_id": 0, "value": "No Brand"}]
                },
                {
                    "complex_id": 0,
                    "id": 9048, # Product Name
                    "values": [{"value": name_ru}]
                }
            ]
        }
        
        return item

    def _clean_title(self, title: str) -> str:
        """去除常见的 1688 营销词"""
        stops = ["包邮", "跨境", "专供", "一件代发", "厂家直销", "新款", "现货"]
        for s in stops:
            title = title.replace(s, "")
        return title.strip()

    def transform_batch(self, products):
        return [self.map_to_ozon(p) for p in products]

    def export_json(self, products, filename="ozon_export.json"):
        # 如果是单个字典，包装成列表
        if isinstance(products, dict):
            products = [products]
            
        data = {"items": products}
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return os.path.abspath(filename)
>>>>>>> release/v1.3.3-hotfix
