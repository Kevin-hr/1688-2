"""
1688-2 1688自动化采集工具包
===========================

提供从1688商品采集到Ozon Global上架的完整流程支持。

主要模块:
    - api: 统一API封装
    - task_router: 任务路由器
    - agents.web_scraper_agent: 网页抓取Agent
    - utils.excel_exporter: Excel导出
    - utils.ozon_transformer: Ozon数据转换
    - utils.file_manager: 文件管理

快速开始:
    from src import 1688API
    api = 1688API()
    result = await api.search("猫玩具", limit=5)
"""

from src.api import Ali1688API, search, scrape_url, export_excel, to_ozon
from src.task_router import TaskRouter
from src.utils.excel_exporter import ExcelExporter
from src.utils.ozon_transformer import OzonTransformer
from src.utils.file_manager import FileManager
from src.agents.web_scraper_agent import WebScraperAgent

__version__ = "1.3.0"

__all__ = [
    "Ali1688API",
    "TaskRouter",
    "ExcelExporter",
    "OzonTransformer",
    "FileManager",
    "WebScraperAgent",
    "search",
    "scrape_url",
    "export_excel",
    "to_ozon",
]
