import asyncio
import os
import json
from src.agents.web_scraper_agent import WebScraperAgent
from src.utils.ozon_transformer import OzonTransformer
from src.utils.file_manager import FileManager

async def run_audit():
    print("🎯 Starting Real Product Audit v1.0...")
    
    # 真实有效的符合 Ozon 规则的 1688 商品 URL
    product_url = "https://detail.1688.com/offer/952473803779.html"
    
    agent = WebScraperAgent()
    transformer = OzonTransformer()
    file_mgr = FileManager()
    
    try:
        # 1. 启动浏览器
        await agent.start()
        
        # 2. 执行抓取 (包含自动截图功能)
        print(f"🕵️ Scraping: {product_url}")
        product_data = await agent.scrape_product_detail(product_url)
        
        if not product_data:
            print("❌ Scraping failed!")
            return

        print(f"✅ Scraped: {product_data['title']}")
        print(f"📸 Screenshot proof saved to: {product_data.get('screenshot_proof')}")
        
        # 3. 数据转换
        print("🔄 Transforming to Ozon format...")
        ozon_data = transformer.map_to_ozon(product_data)
        
        # 4. 导出 JSON
        output_path = os.path.join("1688_products", "ozon_audit_export.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"products": [ozon_data]}, f, ensure_ascii=False, indent=2)
            
        print(f"📦 Audit export saved: {output_path}")
        
        # 5. 校验图片（打印前 5 张，确认无 SVG）
        print("\n🖼️ Image Check (Top 5):")
        for i, img in enumerate(ozon_data['images'][:5]):
            print(f"  [{i+1}] {img}")
            if ".svg" in img or ".tps" in img:
                print("  ⚠️ ALERT: Found invalid image format!")

    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(run_audit())
