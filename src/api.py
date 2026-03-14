"""
1688-2 统一 API 封装
提供简洁的函数接口调用各个功能模块
"""

import asyncio
import os
from typing import List, Dict, Optional

from src.agents.web_scraper_agent import WebScraperAgent
from src.task_router import TaskRouter
from src.utils.excel_exporter import ExcelExporter
from src.utils.ozon_transformer import OzonTransformer
from src.utils.file_manager import FileManager


class Ali1688API:
    """
    1688 采集工具统一 API

    使用示例:
        api = Ali1688API()

        # 关键词搜索
        result = await api.search("猫玩具", limit=5)

        # URL 直抓
        result = await api.scrape_url("https://detail.1688.com/offer/xxx.html")

        # 导出 Excel
        excel_path = api.export_excel(products, "output.xlsx")

        # 转换为 Ozon 格式
        ozon_products = api.to_ozon(products)
    """

    def __init__(self, output_dir: str = "1688_products"):
        """
        初始化 API

        Args:
            output_dir: 商品数据输出目录
        """
        self.output_dir = output_dir
        self.router = TaskRouter()
        self.exporter = ExcelExporter(output_dir=output_dir)
        self.transformer = OzonTransformer()
        self.file_manager = FileManager(base_path=output_dir)

    async def search(
        self,
        keyword: str,
        limit: int = 5,
        sort_type: Optional[str] = None
    ) -> Dict:
        """
        关键词搜索采集

        Args:
            keyword: 搜索关键词
            limit: 最多采集商品数
            sort_type: 排序类型 (booked=销量, postTime=最新)

        Returns:
            采集结果字典
        """
        instruction = f"去1688搜索{keyword}"
        return await self.router.route(instruction, limit=limit, sort_type=sort_type)

    async def scrape_url(self, url: str) -> Dict:
        """
        URL 直抓采集

        Args:
            url: 1688 商品详情页 URL

        Returns:
            采集结果字典
        """
        return await self.router.route_url(url)

    def export_excel(self, products: List[Dict], filename: str = None) -> str:
        """
        导出为 Excel 报表

        Args:
            products: 商品列表
            filename: 输出文件名

        Returns:
            Excel 文件路径
        """
        return self.exporter.export(products, filename=filename)

    def to_ozon(self, products: List[Dict], export_json: bool = True) -> List[Dict]:
        """
        转换为 Ozon 标准格式

        Args:
            products: 商品列表
            export_json: 是否导出 JSON 文件

        Returns:
            Ozon 格式商品列表
        """
        ozon_products = self.transformer.transform_batch(products)

        if export_json:
            self.transformer.export_json(ozon_products, output_dir=self.output_dir)

        return ozon_products

    def save_product_details(self, product: Dict, product_name: str = None) -> str:
        """
        保存商品详情为 Markdown

        Args:
            product: 商品信息字典
            product_name: 商品目录名（默认使用标题）

        Returns:
            保存的文件路径
        """
        name = product_name or product.get("title", "unknown")
        product_dir, image_dir = self.file_manager.create_product_dir(name)
        self.file_manager.save_details(product_dir, product)
        return product_dir


# 便捷函数
async def search(keyword: str, limit: int = 5) -> Dict:
    """
    快速搜索函数

    Args:
        keyword: 搜索关键词
        limit: 采集数量

    Returns:
        采集结果
    """
    api = Ali1688API()
    return await api.search(keyword, limit=limit)


async def scrape_url(url: str) -> Dict:
    """
    快速 URL 采集函数

    Args:
        url: 1688 商品 URL

    Returns:
        采集结果
    """
    api = Ali1688API()
    return await api.scrape_url(url)


def export_excel(products: List[Dict], filename: str = None) -> str:
    """
    快速 Excel 导出函数

    Args:
        products: 商品列表
        filename: 输出文件名

    Returns:
        Excel 文件路径
    """
    api = Ali1688API()
    return api.export_excel(products, filename)


def to_ozon(products: List[Dict], export_json: bool = True) -> List[Dict]:
    """
    快速 Ozon 转换函数

    Args:
        products: 商品列表
        export_json: 是否导出 JSON

    Returns:
        Ozon 格式列表
    """
    api = Ali1688API()
    return api.to_ozon(products, export_json)


if __name__ == "__main__":
    import json

    async def demo():
        """演示用法"""
        api = Ali1688API()

        # 示例：导出已有数据为 Excel 和 Ozon JSON
        demo_products = [
            {
                "title": "测试商品",
                "price": "¥10.00",
                "url": "https://test.com",
                "attributes": {"材质": "塑料"},
                "images": []
            }
        ]

        print("导出 Excel...")
        excel_path = api.export_excel(demo_products, "demo.xlsx")
        print(f"Excel: {excel_path}")

        print("\n转换为 Ozon 格式...")
        ozon_list = api.to_ozon(demo_products)
        print(json.dumps(ozon_list, indent=2, ensure_ascii=False))

    asyncio.run(demo())
