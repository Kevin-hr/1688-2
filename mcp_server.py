# -*- coding: utf-8 -*-
"""
1688 商品采集 MCP 服务器
========================
提供 1688 商品搜索和采集的 MCP 接口

使用方式:
    # 启动服务器
    python mcp_server.py

    # 或注册到 MCP 配置
    # 在 ~/.claude/mcp.json 中添加
"""

import os
import asyncio
import json
from typing import Optional, List, Dict
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

# 尝试导入 FastMCP，如果不存在则使用标准库
try:
    from fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False
    print("Warning: fastmcp not installed. Using stdio server instead.")

from src.task_router import TaskRouter
from src.agents.web_scraper_agent import WebScraperAgent
from src.utils.ozon_transformer import OzonTransformer
from src.utils.ozon_api import OzonApiManager
from src.utils.excel_exporter import ExcelExporter
from src.utils.file_manager import FileManager


# 项目路径
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "1688_products"


def setup_mcp():
    """创建并配置 MCP 服务器"""

    if HAS_FASTMCP:
        mcp = FastMCP("1688-scraper")
    else:
        # 基础实现
        mcp = None

    return mcp


async def search_products(keyword: str, limit: int = 5) -> Dict:
    """
    搜索 1688 商品

    Args:
        keyword: 搜索关键词
        limit: 最多返回商品数量

    Returns:
        包含商品列表和文件路径的字典
    """
    router = TaskRouter()
    result = await router.route(keyword, limit=limit)
    return result


async def scrape_product(url: str) -> Dict:
    """
    通过 URL 采集单个商品

    Args:
        url: 1688 商品详情页 URL

    Returns:
        包含商品数据的字典
    """
    router = TaskRouter()
    result = await router.route_url(url)
    return result


def transform_to_ozon(products: List[Dict]) -> Dict:
    """
    将采集的商品转换为 Ozon 格式

    Args:
        products: 商品列表

    Returns:
        Ozon 格式的商品数据
    """
    transformer = OzonTransformer()
    ozon_products = transformer.transform_batch(products)
    return ozon_products


def export_excel(products: List[Dict], filename: str = None) -> str:
    """
    导出商品到 Excel

    Args:
        products: 商品列表
        filename: 文件名（可选）

    Returns:
        Excel 文件路径
    """
    exporter = ExcelExporter(output_dir=str(OUTPUT_DIR))
    if filename and not filename.endswith('.xlsx'):
        filename += '.xlsx'
    filepath = exporter.export(products, filename=filename)
    return filepath


def upload_to_ozon(json_path: str = None) -> Dict:
    """
    将 ozon_export.json 中的商品上传到 Ozon

    Args:
        json_path: ozon_export.json 文件路径（可选，默认使用_OUTPUT_DIR/ozon_export.json）

    Returns:
        上传结果字典
    """
    if json_path is None:
        json_path = str(OUTPUT_DIR / "ozon_export.json")

    try:
        api_manager = OzonApiManager()
        task_id = api_manager.upload_products(json_path)
        return {
            "status": "success",
            "task_id": task_id,
            "json_path": json_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "json_path": json_path
        }


def get_ozon_products() -> List[Dict]:
    """
    获取当前 ozon_export.json 中的商品列表

    Returns:
        商品列表
    """
    json_path = OUTPUT_DIR / "ozon_export.json"
    if not json_path.exists():
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('products', [])


# ========== FastMCP Server ==========
if HAS_FASTMCP:
    mcp = FastMCP("1688-scraper")

    @mcp.tool()
    async def search_1688(keyword: str, limit: int = 5) -> str:
        """
        搜索 1688 商品并采集详细信息

        Args:
            keyword: 搜索关键词，如 "猫玩具"、"宠物用品"
            limit: 最多采集的商品数量，默认 5

        Returns:
            JSON 格式的采集结果，包含商品数量和文件路径
        """
        result = await search_products(keyword, limit)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def scrape_1688_url(url: str) -> str:
        """
        通过 URL 采集单个 1688 商品详情

        Args:
            url: 1688 商品详情页 URL，如 "https://detail.1688.com/offer/566971549514.html"

        Returns:
            JSON 格式的商品详情
        """
        result = await scrape_product(url)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    def transform_1688_to_ozon(products_json: str) -> str:
        """
        将 1688 商品数据转换为 Ozon Global 上架格式

        Args:
            products_json: 商品列表的 JSON 字符串

        Returns:
            Ozon 格式的 JSON 字符串
        """
        try:
            products = json.loads(products_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON input"}, ensure_ascii=False)

        result = transform_to_ozon(products)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    def export_1688_to_excel(products_json: str, filename: str = None) -> str:
        """
        将商品数据导出为 Excel 报表

        Args:
            products_json: 商品列表的 JSON 字符串
            filename: 输出的文件名（可选）

        Returns:
            Excel 文件路径
        """
        try:
            products = json.loads(products_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON input"}, ensure_ascii=False)

        filepath = export_excel(products, filename)
        return json.dumps({"excel_path": filepath}, ensure_ascii=False)

    @mcp.tool()
    def get采集状态() -> str:
        """
        获取最近一次采集的状态和输出文件列表

        Returns:
            JSON 格式的状态信息
        """
        files = []
        if OUTPUT_DIR.exists():
            for f in OUTPUT_DIR.glob("*.xlsx"):
                files.append({"name": f.name, "size": f.stat().st_size})
            for f in OUTPUT_DIR.glob("*.json"):
                files.append({"name": f.name, "size": f.stat().st_size})

        result = {
            "output_dir": str(OUTPUT_DIR),
            "files": files,
            "total_files": len(files)
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    def upload_ozon(json_path: str = None) -> str:
        """
        将商品上传到 Ozon Global

        Args:
            json_path: ozon_export.json 文件路径（可选，默认自动查找）

        Returns:
            JSON 格式的上传结果
        """
        result = upload_to_ozon(json_path)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    def list_ozon_products() -> str:
        """
        获取当前 Ozon 上架商品列表

        Returns:
            JSON 格式的商品列表
        """
        products = get_ozon_products()
        return json.dumps({
            "count": len(products),
            "products": products
        }, indent=2, ensure_ascii=False)


# ========== CLI Entry Point ==========
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="1688 MCP Server")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("command", nargs="?", help="Command: serve")
    args = parser.parse_args()

    if HAS_FASTMCP:
        print(f"Starting 1688 MCP Server on port {args.port}...")
        mcp.run(transport="stdio")
    else:
        print("FastMCP not installed. Server cannot start.")
        print("Install with: pip install fastmcp")
