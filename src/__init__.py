"""
1688-2 1688自动化采集工具包
===========================

主要模块:
    - api: 统一API封装 (Ali1688API)
    - modules: 最小子模块集合
    - task_router: 任务路由器
    - agents.web_scraper_agent: 网页抓取Agent
    - utils.excel_exporter: Excel导出
    - utils.ozon_transformer: Ozon数据转换
    - utils.file_manager: 文件管理

快速开始:
    from src import Ali1688API
    from src.modules import clean_title, translate_to_ru, calculate_price

    # 使用统一API
    api = Ali1688API()
    result = await api.search("猫玩具", limit=5)

    # 使用最小子模块
    title = clean_title("爆款猫咪玩具")
    ru_name = translate_to_ru(title)
    price = calculate_price(10, 500)
"""

# 统一API
from src.api import Ali1688API, search, scrape_url, export_excel, to_ozon

# 任务路由
from src.task_router import TaskRouter

# 工具模块
from src.utils.excel_exporter import ExcelExporter
from src.utils.ozon_transformer import OzonTransformer
from src.utils.file_manager import FileManager
from src.agents.web_scraper_agent import WebScraperAgent

# 最小子模块
from src.modules import (
    # 文件名清洗
    FilenameSanitizer, sanitize,
    # 标题清洗
    TitleCleaner, clean_title,
    # 单位转换
    UnitConverter, OzonUnitConverter,
    convert_weight, convert_dimension,
    # 翻译
    Translator, translate, translate_to_ru, translate_to_en,
    # 价格计算
    PriceCalculator, calculate_price,
    # 图片下载
    ImageDownloader, download_image, download_images,
    # 字段映射
    FieldMapper, CategoryMapper,
    map_attributes, infer_category,
    # 目录创建
    DirCreator, create_product_dir,
    # 详情保存
    DetailSaver, save_details,
    # Excel样式
    ExcelStyler, get_styler, Colors,
)

__version__ = "1.3.2"

__all__ = [
    # 统一API
    "Ali1688API",
    "TaskRouter",
    "ExcelExporter",
    "OzonTransformer",
    "FileManager",
    "WebScraperAgent",
    # 便捷函数
    "search",
    "scrape_url",
    "export_excel",
    "to_ozon",
    # 最小子模块
    "FilenameSanitizer",
    "sanitize",
    "TitleCleaner",
    "clean_title",
    "UnitConverter",
    "OzonUnitConverter",
    "convert_weight",
    "convert_dimension",
    "Translator",
    "translate",
    "translate_to_ru",
    "translate_to_en",
    "PriceCalculator",
    "calculate_price",
    "ImageDownloader",
    "download_image",
    "download_images",
    "FieldMapper",
    "CategoryMapper",
    "map_attributes",
    "infer_category",
    "DirCreator",
    "create_product_dir",
    "DetailSaver",
    "save_details",
    "ExcelStyler",
    "get_styler",
    "Colors",
]
