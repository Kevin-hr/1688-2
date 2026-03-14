"""
1688-2 最小子模块集合
===================

每个模块都可独立使用:

文件名清洗:
    from src.modules import FilenameSanitizer, sanitize

标题清洗:
    from src.modules import TitleCleaner, clean_title

单位转换:
    from src.modules import UnitConverter, OzonUnitConverter
    from src.modules import convert_weight, convert_dimension

翻译:
    from src.modules import Translator, translate, translate_to_ru, translate_to_en

价格计算:
    from src.modules import PriceCalculator, calculate_price

图片下载:
    from src.modules import ImageDownloader, download_image, download_images

字段映射:
    from src.modules import FieldMapper, CategoryMapper
    from src.modules import map_attributes, infer_category

目录创建:
    from src.modules import DirCreator, create_product_dir

详情保存:
    from src.modules import DetailSaver, save_details

Excel样式:
    from src.modules import ExcelStyler, get_styler, Colors
"""

# 核心模块
from src.modules.filename_sanitizer import FilenameSanitizer, sanitize
from src.modules.title_cleaner import TitleCleaner, clean_title
from src.modules.unit_converter import UnitConverter, OzonUnitConverter
from src.modules.unit_converter import convert_weight, convert_dimension
from src.modules.translator import Translator, translate, translate_to_ru, translate_to_en
from src.modules.price_calculator import PriceCalculator, calculate_price
from src.modules.image_downloader import ImageDownloader, download_image, download_images
from src.modules.field_mapper import FieldMapper, CategoryMapper
from src.modules.field_mapper import map_attributes, infer_category
from src.modules.dir_creator import DirCreator, create_product_dir
from src.modules.detail_saver import DetailSaver, save_details
from src.modules.excel_styler import ExcelStyler, get_styler, Colors

__version__ = "1.3.0"

__all__ = [
    # 文件名清洗
    "FilenameSanitizer",
    "sanitize",
    # 标题清洗
    "TitleCleaner",
    "clean_title",
    # 单位转换
    "UnitConverter",
    "OzonUnitConverter",
    "convert_weight",
    "convert_dimension",
    # 翻译
    "Translator",
    "translate",
    "translate_to_ru",
    "translate_to_en",
    # 价格计算
    "PriceCalculator",
    "calculate_price",
    # 图片下载
    "ImageDownloader",
    "download_image",
    "download_images",
    # 字段映射
    "FieldMapper",
    "CategoryMapper",
    "map_attributes",
    "infer_category",
    # 目录创建
    "DirCreator",
    "create_product_dir",
    # 详情保存
    "DetailSaver",
    "save_details",
    # Excel样式
    "ExcelStyler",
    "get_styler",
    "Colors",
]
