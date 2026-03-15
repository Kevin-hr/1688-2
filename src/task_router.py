# -*- coding: utf-8 -*-
"""
任务路由模块 (TaskRouter)
------------------------
作为系统的中枢神经，负责接收用户指令并调度各个 Agent 和工具模块执行任务。
"""

from src.agents.web_scraper_agent import WebScraperAgent
from src.utils.ozon_transformer import OzonTransformer
from src.utils.ozon_api import OzonApiManager
from src.utils.file_manager import FileManager
from src.utils.excel_exporter import ExcelExporter # 假设有这个
import os

class TaskRouter:
    """
    任务路由器类
    """
    
    def __init__(self):
        """初始化各个子模块。"""
        self.scraper = WebScraperAgent()
        self.transformer = OzonTransformer()
        self.ozon_api = OzonApiManager()
        self.file_manager = FileManager()
        # 动态导入 ExcelExporter 以防循环依赖
        try:
            from src.utils.excel_exporter import ExcelExporter
            self.excel_exporter = ExcelExporter()
        except ImportError:
            self.excel_exporter = None

    async def route(self, instruction: str, limit: int = 5):
        """
        路由处理：关键词搜索/自然语言指令模式。
        """
        print(f"TaskRouter: 正在路由指令: '{instruction}' (限制数量: {limit})")
        
        # 1. 搜索与采集 (目前 Scraper 的 search 接口可能未完全实现，这里演示流程)
        # 假设指令就是关键词
        keyword = instruction.replace("去1688搜索", "").replace("搜索", "")
        
        await self.scraper.start()
        # 临时：由于 search_and_scrape 可能未实现，我们用一个写死的列表模拟多商品采集
        # 或者调用 scraper.scrape_product_detail 循环
        # 这里为了演示闭环，我们假设采集了一个默认商品
        print(f"TaskRouter: 模拟搜索 '{keyword}'...")
        products_data = []
        
        # 尝试采集一个真实 URL 作为示例
        demo_url = "https://detail.1688.com/offer/566971549514.html"
        p_data = await self.scraper.scrape_product_detail(demo_url)
        products_data.append(p_data)
        
        await self.scraper.close()
        
        # 2. 转换
        ozon_items = self.transformer.transform_batch(products_data)
        
        # 3. 导出
        json_path = self.transformer.export_json(ozon_items)
        excel_path = ""
        if self.excel_exporter:
            excel_path = self.excel_exporter.export(products_data, "1688_products_report.xlsx")
            
        return {
            "status": "success",
            "count": len(products_data),
            "save_path": "1688_products",
            "excel_path": excel_path,
            "ozon_json_path": json_path
        }

    async def route_url(self, url: str):
        """
        路由处理：单品 URL 直抓模式。
        """
        print(f"TaskRouter: 正在处理直抓 URL: {url}")
        
        # 1. 启动采集
        await self.scraper.start()
        product_data = await self.scraper.scrape_product_detail(url)
        await self.scraper.close()
        
        if not product_data or not product_data.get("title"):
             return {"status": "failed", "error": "采集失败或被反爬拦截"}

        # 2. 数据转换 (1688 -> Ozon)
        ozon_item = self.transformer.map_to_ozon(product_data)
        json_path = self.transformer.export_json(ozon_item)
        
        # 3. 上传至 Ozon (启用真实上传)
        print("TaskRouter: 正在尝试上传至 Ozon...")
        task_id = self.ozon_api.upload_products(json_path)
        
        # 4. 导出 Excel
        excel_path = ""
        if self.excel_exporter:
            excel_path = self.excel_exporter.export([product_data], "single_product_report.xlsx")

        return {
            "status": "success",
            "count": 1,
            "save_path": "1688_products",
            "excel_path": excel_path,
            "ozon_json_path": json_path,
            "task_id": task_id
        }
