# -*- coding: utf-8 -*-
import pandas as pd
import os

class ExcelExporter:
    """Excel导出工具"""
    
    def export(self, data, filename):
        """
        导出数据到Excel文件
        
        Args:
            data (list): 包含字典的列表数据
            filename (str): 输出文件名或路径
            
        Returns:
            str: 导出的文件绝对路径
        """
        if not data:
            print("没有数据可导出")
            return None
            
        try:
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 处理输出路径
            output_path = os.path.abspath(filename)
            output_dir = os.path.dirname(output_path)
            
            # 确保目录存在
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 导出Excel
            df.to_excel(output_path, index=False)
            
            return output_path
            
        except Exception as e:
            print(f"导出Excel失败: {e}")
            raise e
