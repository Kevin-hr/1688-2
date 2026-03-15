# -*- coding: utf-8 -*-
"""
1688 AI 自动化采集 Agent — 主入口 (v1.3.0)
-------------------------------------------
支持两种模式：
  1. 关键词批量搜索模式：python main.py --keyword "猫玩具" --limit 5
  2. 单品 URL 直抓模式：python main.py --url "https://detail.1688.com/offer/566971549514.html"

输出文件（统一保存至 1688_products/ 目录）：
  - {商品名}/detail.md       # Markdown 详情报告
  - {商品名}/images/         # 商品图片（最多5张）
  - 1688_*_商品采集报表.xlsx  # 格式化 Excel 报表
  - ozon_export.json         # ✨ Ozon Global 标准上架 JSON
"""

import asyncio
import argparse
import os
import sys
import io

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

from src.task_router import TaskRouter


def parse_args():
    """
    解析命令行参数。
    支持关键词搜索模式和单品 URL 直抓模式。
    """
    parser = argparse.ArgumentParser(
        description="1688 AI 自动化采集 Agent — Ozon Global 上架辅助工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 关键词搜索 (批量采集)
  python main.py --keyword "猫玩具" --limit 5
  python main.py -k "猫咪玩具" -n 3

  # 单品 URL 直抓 (精准)
  python main.py --url "https://detail.1688.com/offer/566971549514.html"
  python main.py -u "https://detail.1688.com/offer/566971549514.html"

  # 传统指令模式 (兼容旧版)
  python main.py "去1688搜索猫咪玩具"
        """,
    )

    parser.add_argument(
        "--keyword", "-k", type=str, default=None, help="搜索关键词，例如: '猫玩具'"
    )
    parser.add_argument(
        "--url",
        "-u",
        type=str,
        default=None,
        help="1688 商品详情页 URL（单品直抓模式）",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=5,
        help="关键词模式下最多采集的商品数量，默认 5",
    )
    # 兼容旧版：第一个位置参数作为自然语言指令
    parser.add_argument(
        "instruction",
        nargs="?",
        default=None,
        help="自然语言指令（兼容旧版），例如: '去1688搜索猫咪玩具'",
    )

    return parser.parse_args()


async def main():
    """
    程序主入口。根据参数选择搜索模式并分发任务。
    """
    args = parse_args()

    router = TaskRouter()

    # ---------- 模式判断 ----------
    if args.url:
        # 模式 A：单品 URL 直抓
        print(f"--- 1688 AI Agent [单品直抓模式] ---")
        print(f"目标 URL: {args.url}")
        result = await router.route_url(args.url)

    elif args.keyword:
        # 模式 B：关键词批量搜索
        print(f"--- 1688 AI Agent [关键词搜索模式] ---")
        print(f"关键词: {args.keyword}  |  采集数量: {args.limit}")
        instruction = f"去1688搜索{args.keyword}"
        result = await router.route(instruction, limit=args.limit)

    elif args.instruction:
        # 模式 C：旧版自然语言指令（兼容）
        print(f"--- 1688 AI Agent [自然语言模式] ---")
        print(f"指令: {args.instruction}")
        result = await router.route(args.instruction)

    else:
        print("❌ 请至少提供一个参数。使用 --help 查看帮助。")
        print("示例: python main.py --keyword '猫玩具' --limit 5")
        return

    # ---------- 输出结果 ----------
    print("\n" + "=" * 60)
    if result.get("status") == "success":
        print(f"✅ 任务完成！")
        print(f"   商品数量   : {result.get('count', 1)}")
        print(f"   数据目录   : {result.get('save_path', 'N/A')}")
        if result.get("excel_path"):
            print(f"   Excel 报表  : {result['excel_path']}")
        if result.get("ozon_json_path"):
            print(f"   Ozon JSON  : {result['ozon_json_path']}")
    else:
        print(f"❌ 任务失败: {result.get('error', '未知错误')}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
