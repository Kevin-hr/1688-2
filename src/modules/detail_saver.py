"""
详情保存模块 - 商品详情保存为Markdown
"""

import os
from typing import Dict


class DetailSaver:
    """
    详情保存器

    将商品信息保存为 Markdown 格式
    """

    def __init__(self, encoding: str = "utf-8"):
        """
        初始化

        Args:
            encoding: 文件编码
        """
        self.encoding = encoding

    def save(self, product_dir: str, details: Dict) -> str:
        """
        保存商品详情

        Args:
            product_dir: 商品目录路径
            details: 商品信息字典

        Returns:
            保存的文件路径
        """
        filepath = os.path.join(product_dir, "detail.md")

        with open(filepath, "w", encoding=self.encoding) as f:
            # 标题
            title = details.get("title", "商品详情")
            f.write(f"# {title}\n\n")

            # 价格
            price = details.get("price", "N/A")
            f.write(f"**价格**: {price}\n")

            # 来源链接
            url = details.get("url", "N/A")
            f.write(f"**来源链接**: {url}\n\n")

            # 详细描述
            f.write("## 详细描述/规格属性\n")

            description = details.get("description")
            if description:
                f.write(description)
            else:
                # 从属性生成描述
                attrs = details.get("attributes", {})
                if attrs:
                    for key, value in attrs.items():
                        f.write(f"- **{key}**: {value}\n")
                else:
                    f.write("暂无详细描述。\n")

        return filepath

    def save_batch(self, products: Dict) -> Dict[str, str]:
        """
        批量保存多个商品

        Args:
            products: 商品字典 {name: details}

        Returns:
            {name: filepath} 映射
        """
        results = {}
        for name, details in products.items():
            # 从 details 中提取 title
            if "title" not in details:
                details["title"] = name

            # 导入 DirCreator
            from src.modules.dir_creator import DirCreator
            creator = DirCreator()
            product_dir, _ = creator.create(name)

            filepath = self.save(product_dir, details)
            results[name] = filepath

        return results


# 便捷函数
def save_details(product_dir: str, details: Dict) -> str:
    """快速保存详情"""
    saver = DetailSaver()
    return saver.save(product_dir, details)


if __name__ == "__main__":
    # 测试
    saver = DetailSaver()

    test_details = {
        "title": "测试商品",
        "price": "¥10.00",
        "url": "https://test.com/product/123",
        "attributes": {
            "材质": "塑料",
            "颜色": "红色",
            "重量": "500g"
        }
    }

    # 创建测试目录
    os.makedirs("test_output/detail_test", exist_ok=True)

    filepath = saver.save("test_output/detail_test", test_details)
    print(f"已保存到: {filepath}")

    # 显示内容
    print("\n文件内容:")
    print("-" * 40)
    with open(filepath, "r", encoding="utf-8") as f:
        print(f.read())
