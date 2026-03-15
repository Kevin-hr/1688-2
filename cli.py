#!/usr/bin/env python
"""
1688-2 CLI 工具
提供命令行接口调用各个功能模块
"""

import argparse
import asyncio
import sys
import os
import io
import json

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.api import Ali1688API
from src.utils.ozon_transformer import OzonTransformer
from src.utils.excel_exporter import ExcelExporter


def cmd_search(args):
    """执行关键词搜索"""
    api = Ali1688API(output_dir=args.output or "1688_products")

    async def run():
        result = await api.search(args.keyword, limit=args.limit)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return result

    return asyncio.run(run())


def cmd_scrape(args):
    """执行 URL 直抓"""
    api = Ali1688API(output_dir=args.output or "1688_products")

    async def run():
        result = await api.scrape_url(args.url)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return result

    return asyncio.run(run())


def cmd_convert(args):
    """转换现有数据为 Ozon 格式"""
    # 读取输入 JSON
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
            products = data if isinstance(data, list) else data.get("products", [])
    else:
        print("错误: 请提供 --input 参数指定输入文件")
        return 1

    # 转换
    transformer = OzonTransformer()
    ozon_products = transformer.transform_batch(products)

    # 输出
    if args.output:
        transformer.export_json(ozon_products, output_dir=os.path.dirname(args.output) or "1688_products")
        print(f"已导出到: {args.output}")
    else:
        print(json.dumps(ozon_products, indent=2, ensure_ascii=False, default=str))

    return 0


def cmd_export(args):
    """导出为 Excel"""
    # 读取输入 JSON
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
            products = data if isinstance(data, list) else data.get("products", [])
    else:
        print("错误: 请提供 --input 参数指定输入文件")
        return 1

    # 导出
    exporter = ExcelExporter(output_dir=os.path.dirname(args.output) or "1688_products")
    filename = os.path.basename(args.output) if args.output else "output.xlsx"
    result = exporter.export(products, filename=filename)

    print(f"已导出到: {result}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="1688-2 1688采集工具 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 关键词搜索
  python cli.py search -k "猫玩具" -n 5

  # URL 直抓
  python cli.py scrape -u "https://detail.1688.com/offer/xxx.html"

  # 转换为 Ozon 格式
  python cli.py convert -i input.json -o ozon_export.json

  # 导出为 Excel
  python cli.py export -i input.json -o output.xlsx
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # search 命令
    search_parser = subparsers.add_parser("search", help="关键词搜索采集")
    search_parser.add_argument("-k", "--keyword", required=True, help="搜索关键词")
    search_parser.add_argument("-n", "--limit", type=int, default=5, help="采集数量")
    search_parser.add_argument("-o", "--output", help="输出目录")
    search_parser.set_defaults(func=cmd_search)

    # scrape 命令
    scrape_parser = subparsers.add_parser("scrape", help="URL 直抓")
    scrape_parser.add_argument("-u", "--url", required=True, help="商品详情页 URL")
    scrape_parser.add_argument("-o", "--output", help="输出目录")
    scrape_parser.set_defaults(func=cmd_scrape)

    # convert 命令
    convert_parser = subparsers.add_parser("convert", help="转换为 Ozon 格式")
    convert_parser.add_argument("-i", "--input", required=True, help="输入 JSON 文件")
    convert_parser.add_argument("-o", "--output", help="输出 JSON 文件")
    convert_parser.set_defaults(func=cmd_convert)

    # export 命令
    export_parser = subparsers.add_parser("export", help="导出为 Excel")
    export_parser.add_argument("-i", "--input", required=True, help="输入 JSON 文件")
    export_parser.add_argument("-o", "--output", help="输出 Excel 文件")
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
