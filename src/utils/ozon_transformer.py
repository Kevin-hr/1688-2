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
