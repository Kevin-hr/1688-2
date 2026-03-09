import json
import os
from src.agents.web_scraper_agent import WebScraperAgent

class TaskRouter:
    """
    任务路由器，负责解析用户输入并调用相应的 Agent 执行任务。
    """
    def __init__(self):
        self.scraper = WebScraperAgent()

    async def route(self, task_input):
        """
        根据用户输入分发任务。
        """
        print(f"[Router] 正在解析任务: {task_input}")
        
        # 简单模拟关键字提取，实际场景中通常由 OpenClaw 的 LLM 预处理
        keyword = task_input.replace("去1688搜索", "").replace("搜索", "").strip()
        
        if not keyword:
            return {"status": "failed", "error": "未提供搜索关键字"}
        
        print(f"[Router] 识别到关键字: {keyword}")
        
        try:
            # 步骤 1: 搜索获取链接列表
            urls = await self.scraper.scrape_1688(keyword, limit=5)
            
            if not urls:
                return {"status": "failed", "error": "未找到相关商品链接"}
                
            results = []
            # 步骤 2: 遍历链接并抓取深度详情
            for i, url in enumerate(urls):
                print(f"[Router] 正在处理第 ({i+1}/{len(urls)}) 个商品详情...")
                try:
                    data = await self.scraper.scrape_product_detail(url)
                    if data:
                        results.append(data)
                except Exception as e:
                    print(f"[Router] 获取链接 {url} 详情出错: {e}")
            
            return {
                "status": "success",
                "keyword": keyword,
                "count": len(results),
                "save_path": os.path.abspath("1688_products")
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    import asyncio
    import sys
    
    router = TaskRouter()
    user_input = sys.argv[1] if len(sys.argv) > 1 else "猫咪玩具"
    result = asyncio.run(router.route(user_input))
    print(json.dumps(result, indent=2, ensure_ascii=False))
