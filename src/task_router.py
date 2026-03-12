"""
任务路由器 (Task Router) — v1.3.0
-----------------------------------
负责解析用户输入（自然语言指令或结构化参数），
调用 WebScraperAgent 执行采集，
最后通过 ExcelExporter 和 OzonTransformer 生成双格式输出。

v1.3.0 改进：
  ✅ 使用 async with 管理 WebScraperAgent 的单一浏览器 Session
  ✅ 搜索 + 详情抓取全程复用同一个浏览器，消除重复启停开销

输出格式（每次采集）：
  - 1688_products/{商品名}/detail.md      — Markdown 详情
  - 1688_products/{商品名}/images/        — 商品图片
  - 1688_products/*.xlsx                  — 格式化 Excel 报表
  - 1688_products/ozon_export.json        — Ozon Global 标准 JSON
"""

import json
import os
from src.agents.web_scraper_agent import WebScraperAgent
from src.utils.excel_exporter import ExcelExporter       # Excel 报表导出器
from src.utils.ozon_transformer import OzonTransformer   # Ozon 字段标准化转换器


class TaskRouter:
    """
    任务路由器，负责解析用户输入并调用相应的 Agent 执行任务。
    支持两种路由模式：
      - route(instruction):     自然语言指令 → 关键词搜索
      - route_url(url):         直接抓取单品详情页
    """

    def __init__(self):
        # 初始化各依赖模块
        self.scraper = WebScraperAgent()
        self.exporter = ExcelExporter()          # 初始化 Excel 导出器
        self.transformer = OzonTransformer()     # 初始化 Ozon 转换器

    async def route(self, task_input, limit=5, sort_type=None):
        """
        根据自然语言指令分发关键词搜索任务。
        使用 async with 管理单一浏览器 Session
        """
        print(f"[Router] 正在解析任务: {task_input}")

        # 简单关键字提取（后续可接 LLM 预处理）
        keyword = task_input.replace("去1688搜索", "").replace("搜索", "").strip()

        if not keyword:
            return {"status": "failed", "error": "未提供搜索关键字"}

        print(f"[Router] 识别到关键字: {keyword}  |  采集上限: {limit} |  排序: {sort_type or '默认'}")

        try:
            # 使用 async with 管理单一浏览器 Session
            async with self.scraper as agent:
                # 步骤 1: 搜索获取链接列表
                urls = await agent.scrape_1688(keyword, limit=limit, sort_type=sort_type)

                if not urls:
                    return {"status": "failed", "error": "未找到相关商品链接"}

                results = []
                # 步骤 2: 遍历链接并抓取深度详情（复用同一浏览器）
                for i, url in enumerate(urls):
                    print(f"[Router] 正在处理第 ({i+1}/{len(urls)}) 个商品详情...")
                    try:
                        data = await agent.scrape_product_detail(url)
                        if data:
                            results.append(data)
                    except Exception as e:
                        print(f"[Router] 获取链接 {url} 详情出错: {e}")

            # 浏览器在 async with 退出时自动关闭
            return self._export_results(results, f"1688_{keyword[:10]}")

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def route_url(self, url):
        """
        直接根据指定 URL 采集单个商品详情（单品直抓模式）。

        参数:
            url: 1688 商品详情页 URL

        返回:
            含有 status/count/save_path/excel_path/ozon_json_path 的结果字典
        """
        print(f"[Router] [单品模式] 正在直抓: {url}")

        try:
            async with self.scraper as agent:
                data = await agent.scrape_product_detail(url)
                if not data:
                    return {"status": "failed", "error": "详情页抓取失败，请检查 URL 或登录状态"}

            return self._export_results([data], "1688_single")

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _export_results(self, results, filename_prefix="1688"):
        """
        将采集结果导出为 Excel 报表和 Ozon JSON 两种格式。

        参数:
            results: 采集到的商品字典列表
            filename_prefix: Excel 文件名前缀

        返回:
            含有 status/count/save_path/excel_path/ozon_json_path 的结果字典
        """
        save_path = os.path.abspath("1688_products")
        excel_path = None
        ozon_json_path = None

        if not results:
            return {
                "status": "success",
                "count": 0,
                "save_path": save_path,
                "excel_path": None,
                "ozon_json_path": None,
                "warning": "未能成功采集到任何商品数据",
            }

        # 步骤 3: 导出 Excel 报表
        try:
            print(f"[Router] 正在导出 Excel 报表...")
            excel_path = self.exporter.export(
                results,
                filename=f"{filename_prefix}_商品采集报表.xlsx"
            )
        except Exception as e:
            print(f"[Router] Excel 导出失败: {e}")

        # 步骤 4: 转换并导出 Ozon JSON
        try:
            print(f"[Router] 正在生成 Ozon Global 标准 JSON...")
            ozon_products = self.transformer.transform_batch(results)
            ozon_json_path = self.transformer.export_json(ozon_products)
        except Exception as e:
            print(f"[Router] Ozon JSON 导出失败: {e}")

        return {
            "status": "success",
            "count": len(results),
            "save_path": save_path,
            "excel_path": excel_path,
            "ozon_json_path": ozon_json_path,
        }


if __name__ == "__main__":
    import asyncio
    import sys

    router = TaskRouter()
    user_input = sys.argv[1] if len(sys.argv) > 1 else "猫咪玩具"
    result = asyncio.run(router.route(user_input))
    print(json.dumps(result, indent=2, ensure_ascii=False))
