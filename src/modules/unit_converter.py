# -*- coding: utf-8 -*-
"""
单位转换模块 (Unit Converter)
----------------------------
负责处理 Ozon 要求的单位转换逻辑 (CM -> MM, KG -> G)。
"""

import re

class UnitConverter:
    """
    单位转换器
    
    Ozon 要求：
    - 尺寸: 毫米 (mm)
    - 重量: 克 (g)
    
    1688 通常提供:
    - 尺寸: 厘米 (cm) 或 米 (m)
    - 重量: 千克 (kg) 或 克 (g)
    """
    
    @staticmethod
    def convert_dimension(value_str: str) -> int:
        """
        将尺寸字符串转换为毫米 (mm) 整数。
        支持格式: "10cm", "0.5m", "100", "10*20*30cm" (取最大值或按需处理)
        
        这里假设传入的是单边长度。
        """
        if not value_str:
            return 0
            
        # 归一化
        s = str(value_str).lower().strip()
        
        # 提取数字
        match = re.search(r"([\d\.]+)", s)
        if not match:
            return 0
            
        number = float(match.group(1))
        
        if "mm" in s:
            return int(number)
        elif "cm" in s:
            return int(number * 10)
        elif "m" in s and "mm" not in s and "cm" not in s: # 避免误判
            return int(number * 1000)
        else:
            # 默认视为 cm (1688 常用)
            return int(number * 10)

    @staticmethod
    def convert_weight(value_str: str) -> int:
        """
        将重量字符串转换为克 (g) 整数。
        支持格式: "1kg", "500g", "0.5kg"
        """
        if not value_str:
            return 0
            
        s = str(value_str).lower().strip()
        
        match = re.search(r"([\d\.]+)", s)
        if not match:
            return 0
            
        number = float(match.group(1))
        
        if "kg" in s:
            return int(number * 1000)
        elif "g" in s and "kg" not in s:
            return int(number)
        else:
            # 默认视为 kg (如果数值很小可能是 kg，数值很大可能是 g，这里保守默认 kg)
            # 或者根据经验，1688 属性栏通常是 kg
            return int(number * 1000)
