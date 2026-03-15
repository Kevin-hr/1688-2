
import asyncio
import sys
from src.agents.web_scraper_agent import WebScraperAgent

async def test_selectors():
    """
    验证 1688 选择器是否失效的核心脚本。
    测试目标：标题、价格、属性表格、主图。
    """
    test_urls = [
        "https://detail.1688.com/offer/710603780520.html", # 示例1: 电子产品类
        "https://detail.1688.com/offer/566971549514.html", # 示例2: 玩具类
    ]
    
    agent = WebScraperAgent()
    await agent.start()
    print("🔍 启动 1688 选择器稳定性探测...")
    
    results = []
    for url in test_urls:
        print(f"\n📡 正在探测: {url}")
        try:
            # 开启无头模式进行快速验证
            res = await agent.scrape_product_detail(url)
            
            check = {
                "url": url,
                "title": "✅" if res.get("title") else "❌",
                "price": "✅" if res.get("price") else "❌",
                "attributes": "✅" if res.get("attributes") else "❌",
                "images": "✅" if res.get("images") else "❌",
            }
            results.append(check)
            
            if "❌" in check.values():
                print(f"⚠️  警告: 部分选择器失效! {check}")
            else:
                print(f"✨  通过: 所有核心字段解析成功。")
                
        except Exception as e:
            print(f"🔴 崩溃: {url} -> {e}")
            results.append({"url": url, "error": str(e)})

    print("\n" + "="*40)
    print("📊 探测汇总报告:")
    for r in results:
        print(r)
    print("="*40)

if __name__ == "__main__":
    asyncio.run(test_selectors())
