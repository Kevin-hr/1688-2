"""
目录创建模块 - 商品目录结构创建
"""

import os
from typing import Tuple

from src.modules.filename_sanitizer import FilenameSanitizer


class DirCreator:
    """
    目录创建器

    创建商品存储目录结构:
    {base_path}/
        {product_name}/
            detail.md
            images/
    """

    def __init__(self, base_path: str = "1688_products"):
        """
        初始化

        Args:
            base_path: 基础目录路径
        """
        self.base_path = base_path
        self.sanitizer = FilenameSanitizer()

    def create(self, product_name: str) -> Tuple[str, str]:
        """
        创建商品目录

        Args:
            product_name: 商品名称

        Returns:
            (商品目录路径, 图片目录路径)
        """
        # 清洗文件名
        safe_name = self.sanitizer.sanitize(product_name)

        # 创建路径
        product_dir = os.path.join(self.base_path, safe_name)
        image_dir = os.path.join(product_dir, "images")

        # 创建目录
        os.makedirs(image_dir, exist_ok=True)

        return product_dir, image_dir

    def get_product_path(self, product_name: str) -> str:
        """获取商品目录路径"""
        safe_name = self.sanitizer.sanitize(product_name)
        return os.path.join(self.base_path, safe_name)

    def get_image_path(self, product_name: str, filename: str = None) -> str:
        """获取图片目录或文件路径"""
        _, image_dir = self.create(product_name)
        if filename:
            return os.path.join(image_dir, filename)
        return image_dir


# 便捷函数
def create_product_dir(product_name: str, base_path: str = "1688_products") -> Tuple[str, str]:
    """快速创建商品目录"""
    creator = DirCreator(base_path)
    return creator.create(product_name)


if __name__ == "__main__":
    # 测试
    creator = DirCreator("test_output")

    test_names = [
        "正常商品名称",
        "商品<>:/\\|*?名称",
        "A" * 300,
    ]

    print("目录创建测试:")
    for name in test_names:
        product_dir, image_dir = creator.create(name)
        print(f"商品: {name}")
        print(f"  目录: {product_dir}")
        print(f"  图片: {image_dir}")
        print()
