"""
单位转换模块 - Ozon物流单位标准化转换
"""


class UnitConverter:
    """
    单位转换器

    - 重量: kg → g (×1000)
    - 尺寸: cm → mm (×10)
    """

    def __init__(self):
        pass

    @staticmethod
    def convert_weight(value: str) -> float:
        """
        重量转换为克

        Args:
            value: 字符串形式的重量，如 "500g", "0.5kg", "500"

        Returns:
            克为单位的浮点数
        """
        import re

        if not value:
            return 0.0

        value_str = str(value).strip().lower()

        # 匹配 kg
        kg_match = re.search(r"([\d.]+)\s*kg", value_str)
        if kg_match:
            return float(kg_match.group(1)) * 1000

        # 匹配 g
        g_match = re.search(r"([\d.]+)\s*g", value_str)
        if g_match:
            return float(g_match.group(1))

        # 纯数字，默认g
        try:
            return float(value_str)
        except:
            return 0.0

    @staticmethod
    def convert_dimension(value: str) -> float:
        """
        尺寸转换为毫米

        Args:
            value: 字符串形式的尺寸，如 "10cm", "100mm", "0.5m", "10"

        Returns:
            毫米为单位的浮点数
        """
        import re

        if not value:
            return 0.0

        value_str = str(value).strip().lower()

        # 匹配 m (米) - 需要放在 cm 之前匹配
        m_match = re.search(r"([\d.]+)\s*m(?!m)", value_str)
        if m_match:
            return float(m_match.group(1)) * 1000

        # 匹配 cm
        cm_match = re.search(r"([\d.]+)\s*cm", value_str)
        if cm_match:
            return float(cm_match.group(1)) * 10

        # 匹配 mm
        mm_match = re.search(r"([\d.]+)\s*mm", value_str)
        if mm_match:
            return float(mm_match.group(1))

        # 纯数字，默认mm
        try:
            return float(value_str)
        except:
            return 0.0

    @staticmethod
    def format_weight(grams: float) -> str:
        """格式化为重量字符串"""
        if grams >= 1000:
            return f"{grams/1000:.2f}kg"
        return f"{grams:.0f}g"

    @staticmethod
    def format_dimension(mm: float) -> str:
        """格式化为尺寸字符串"""
        return f"{mm:.0f}mm"


class OzonUnitConverter(UnitConverter):
    """Ozon专用单位转换器"""

    def convert_attributes(self, attributes: dict) -> dict:
        """
        批量转换属性字典中的单位

        Args:
            attributes: 原始属性字典

        Returns:
            转换后的属性字典
        """
        import re

        converted = dict(attributes)

        for key, value in attributes.items():
            value_str = str(value).strip().lower()

            # 重量转换
            if "重" in key or "weight" in key.lower():
                grams = self.convert_weight(value_str)
                if grams > 0:
                    converted[key] = self.format_weight(grams)

            # 尺寸转换
            if any(dim in key for dim in ["长", "宽", "高", "厚", "尺寸", "规格"]):
                mm = self.convert_dimension(value_str)
                if mm > 0:
                    converted[key] = self.format_dimension(mm)

        return converted


# 便捷函数
def convert_weight(value: str) -> float:
    """快速重量转换"""
    return UnitConverter.convert_weight(value)


def convert_dimension(value: str) -> float:
    """快速尺寸转换"""
    return UnitConverter.convert_dimension(value)


if __name__ == "__main__":
    # 测试
    converter = OzonUnitConverter()

    # 重量测试
    weights = ["500g", "0.5kg", "1000 g", "500"]
    for w in weights:
        result = converter.convert_weight(w)
        print(f"'{w}' -> {result}g")

    print()

    # 尺寸测试
    dimensions = ["10cm", "100mm", "15 cm", "50"]
    for d in dimensions:
        result = converter.convert_dimension(d)
        print(f"'{d}' -> {result}mm")

    print()

    # 批量转换测试
    attrs = {
        "重量": "0.5kg",
        "尺寸": "20cm",
        "材质": "塑料",
        "颜色": "红色"
    }
    converted = converter.convert_attributes(attrs)
    print(f"原始: {attrs}")
    print(f"转换: {converted}")
