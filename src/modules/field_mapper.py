"""
字段映射模块 - 中文属性到Ozon标准字段的映射
"""

from typing import Dict, List, Tuple


class FieldMapper:
    """
    字段映射器

    将 1688 中文属性键名映射到 Ozon 标准英文字段
    """

    # 中文属性 → Ozon 标准字段
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

    # Ozon 属性 ID (用于 API)
    OZON_ATTRIBUTE_IDS = {
        "brand": 31,
        "material": 8229,
        "color": 10091,
        "target_audience": 9163,
        "model": 77,
        "origin_country": 4389,
        "package_qty": 84,
    }

    def __init__(self, custom_map: Dict[str, str] = None):
        """
        初始化映射器

        Args:
            custom_map: 自定义映射（追加到默认映射）
        """
        self.attribute_map = dict(self.ATTRIBUTE_MAP)
        if custom_map:
            self.attribute_map.update(custom_map)

    def map(self, attributes: Dict[str, str]) -> Tuple[Dict, Dict]:
        """
        映射属性字典

        Args:
            attributes: 原始中文属性字典

        Returns:
            (映射成功的字典, 未映射的字典)
        """
        mapped = {}
        unmapped = {}

        for cn_key, value in attributes.items():
            en_key = self._find_mapping(cn_key)
            if en_key:
                mapped[en_key] = value
            else:
                unmapped[cn_key] = value

        return mapped, unmapped

    def _find_mapping(self, cn_key: str) -> str:
        """查找映射"""
        # 精确匹配
        if cn_key in self.attribute_map:
            return self.attribute_map[cn_key]

        # 包含匹配
        for pattern, target in self.attribute_map.items():
            if pattern in cn_key:
                return target

        return None

    def to_ozon_api_format(self, mapped_attrs: Dict) -> List[Dict]:
        """
        转换为 Ozon API 格式

        Args:
            mapped_attrs: 已映射的属性字典

        Returns:
            Ozon API 格式的属性列表
        """
        api_attrs = []

        for key, value in mapped_attrs.items():
            attr_id = self.OZON_ATTRIBUTE_IDS.get(key)
            if attr_id:
                api_attrs.append({
                    "id": attr_id,
                    "values": [{"value": str(value)}]
                })

        # 添加默认原产国
        if "origin_country" not in mapped_attrs:
            api_attrs.append({
                "id": self.OZON_ATTRIBUTE_IDS.get("origin_country", 4389),
                "values": [{"value": "China"}]
            })

        return api_attrs


class CategoryMapper:
    """品类映射器"""

    # 关键词 → Ozon 品类
    CATEGORY_MAP = {
        "猫": "Pet Supplies / Cat Toys",
        "狗": "Pet Supplies / Dog Toys",
        "宠物": "Pet Supplies",
        "玩具": "Toys & Games",
        "球": "Sports & Outdoors / Balls",
        "手机": "Electronics / Mobile Phones",
        "耳机": "Electronics / Headphones",
        "服装": "Apparel",
        "鞋": "Footwear",
        "包": "Bags & Luggage",
    }

    def __init__(self, custom_map: Dict[str, str] = None):
        self.category_map = dict(self.CATEGORY_MAP)
        if custom_map:
            self.category_map.update(custom_map)

    def map(self, title: str) -> str:
        """
        从标题推断品类

        Args:
            title: 商品标题

        Returns:
            Ozon 品类路径
        """
        for keyword, category in self.category_map.items():
            if keyword in title:
                return category

        return "General"


# 便捷函数
def map_attributes(attributes: Dict[str, str]) -> Tuple[Dict, Dict]:
    """快速映射属性"""
    mapper = FieldMapper()
    return mapper.map(attributes)


def infer_category(title: str) -> str:
    """快速推断品类"""
    mapper = CategoryMapper()
    return mapper.map(title)


if __name__ == "__main__":
    # 测试
    mapper = FieldMapper()
    category_mapper = CategoryMapper()

    # 属性映射测试
    attrs = {
        "材质": "EVA发泡",
        "颜色": "红色",
        "重量": "500g",
        "尺寸": "20cm",
        "自定义字段": "测试值",
    }

    mapped, unmapped = mapper.map(attrs)
    print("属性映射测试:")
    print(f"原始: {attrs}")
    print(f"映射: {mapped}")
    print(f"未映射: {unmapped}")

    print()

    # 品类推断测试
    titles = [
        "猫咪静音球玩具",
        "宠物狗粮",
        "手机充电器",
    ]

    print("品类推断测试:")
    for title in titles:
        category = category_mapper.map(title)
        print(f"'{title}' -> {category}")
