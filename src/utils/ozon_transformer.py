"""
Ozon 商品数据标准化转换器 (Ozon Transformer)
----------------------------------------------
将从 1688 采集的原始数据，清洗并映射为 Ozon Global 平台的标准上架字段格式。

核心功能：
1. 标题清洗 - 去除 1688 营销牛皮词（厂家直销、一件代发等）
2. 单位转换 - 自动将 CM → MM，KG → G（Ozon 物流计算要求）
3. 字段映射 - 将中文属性键名映射到 Ozon 标准英文字段
4. JSON 导出 - 输出 ozon_export.json，可对接 ERP 或手动导入

参考: PROJECT_REVIEW.md - "Scrape to List" (采集即可上架) 策略
"""

import re
import json
import os


class OzonTransformer:
    """
    1688 → Ozon Global 商品数据标准化转换器。
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

    def clean_title(self, raw_title: str, max_length: int = 200) -> str:
        """
        清洗 1688 商品标题：
        - 去除营销垃圾词
        - 去除多余标点和空格
        - 截断至 Ozon 最大标题长度（200字符）

        参数:
            raw_title: 原始 1688 标题
            max_length: Ozon 标题最大字符数，默认 200

        返回:
            清洗后的标题字符串
        """
        title = raw_title
        # 逐个去除营销词
        for word in self.MARKETING_BUZZWORDS:
            title = title.replace(word, "")

        # 去除多余标点：连续的逗号/顿号/空格
        title = re.sub(r"[,，、\s]{2,}", " ", title)
        # 去除首尾标点
        title = re.sub(r"^[\s,，、！!]+|[\s,，、！!]+$", "", title)
        # 截断
        title = title[:max_length].strip()

        return title if title else raw_title[:max_length]

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
                    # 已经是 g，保留原值
                    pass

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
                    # 已经是 mm，保留原值
                    pass

        return converted

    def map_to_ozon(self, product: dict) -> dict:
        """
        将 1688 商品数据映射为 Ozon Global 标准上架字段结构。

        Ozon 标准字段:
            - name: 商品标题（英文/俄文建议人工翻译，目前保留中文清洗版本）
            - offer_id: 供应商 SKU（用 1688 offer ID 生成）
            - price: RUB 价格（CNY 价格 × 汇率，此处标记需手动换算）
            - vat: 税率（宠物类通常 20%）
            - weight: 重量（克）
            - depth/width/height: 尺寸（毫米）
            - images: 商品图片 URL 列表
            - attributes: 其他属性
            - category_id: Ozon 品类（需人工核对）
            - source_url: 1688 来源链接（用于溯源）

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

        # 2. 转换单位
        converted_attrs = self.convert_units(raw_attrs)

        # 3. 映射属性到英文字段
        ozon_attrs = {}
        unmapped_attrs = {}  # 未匹配的属性保留原样供人工核查

        for cn_key, value in converted_attrs.items():
            en_key = None
            # 模糊匹配：遍历映射表找到包含关键词的键
            for pattern, target_field in self.ATTRIBUTE_MAP.items():
                if pattern in cn_key:
                    en_key = target_field
                    break

            if en_key:
                ozon_attrs[en_key] = value
            else:
                unmapped_attrs[cn_key] = value

        # 4. 提取物理规格（weight / dimensions）
        weight_g = self._extract_number(
            ozon_attrs.get("weight_g", "") or ozon_attrs.get("gross_weight_g", ""),
            fallback=None
        )
        length_mm = self._extract_number(ozon_attrs.get("length_mm", ""), fallback=None)
        width_mm = self._extract_number(ozon_attrs.get("width_mm", ""), fallback=None)
        height_mm = self._extract_number(ozon_attrs.get("height_mm", ""), fallback=None)

        # 5. 推断价格（标注为 CNY，需人工换算 RUB）
        raw_price = product.get("price", "N/A")
        cny_price = self._extract_number(raw_price, fallback=0.0)

        # 6. 从 URL 中提取 offer_id
        offer_id_match = re.search(r"offerId=(\d+)", source_url)
        offer_id = f"1688-{offer_id_match.group(1)}" if offer_id_match else f"1688-{abs(hash(source_url)) % 100000}"

        # 7. 自动推断 Ozon 品类
        suggested_category = "Pet Supplies"  # 默认
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in raw_title:
                suggested_category = category
                break

        # 8. 组装 Ozon 标准字段
        ozon_product = {
            # ---- 核心字段 ----
            "offer_id": offer_id,
            "name": clean_title,
            "name_raw_1688": raw_title,        # 保留原始标题供对照
            "price_cny": cny_price,
            "price_rub": "⚠️ 需手动换算（CNY × 当日汇率）",

            # ---- Ozon 物流必填 ----
            "weight_g": weight_g,
            "depth_mm": length_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,

            # ---- 分类 ----
            "suggested_ozon_category": suggested_category,

            # ---- 图片 ----
            "images": product.get("images", []),

            # ---- 已映射属性 ----
            "attributes_mapped": ozon_attrs,

            # ---- 未映射属性（人工核查）----
            "attributes_unmapped": unmapped_attrs,

            # ---- 溯源 ----
            "source_url_1688": source_url,
            "vat": "0.20",  # 俄罗斯 20% VAT（宠物品类，需核对）
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
                print(f"[OzonTransformer] 转换失败 ({i+1}): {e}")
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
            "export_note": "price_rub 字段需根据当日 CNY/RUB 汇率手动换算后才可上架",
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
        从字符串中提取第一个数字（整数或浮点数）。

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
