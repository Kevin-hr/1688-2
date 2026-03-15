from src.agents.components.navigator import Navigator
from src.agents.components.extractor import Extractor
from src.agents.components.downloader import Downloader
from src.agents.components.ai_navigator import AINavigator
import os
import asyncio
from login_1688 import check_login_status

class WebScraperAgent:
    def __init__(self, headless: bool = False, extension_path: str = None):
        self.navigator = Navigator(headless=headless, extension_path=extension_path)
        self.extractor = Extractor()
        self.downloader = Downloader()
        self.ai_navigator = None # 延迟初始化，依赖 page 对象

    async def start(self):
        print("WebScraperAgent started.")
        await self.navigator.start_browser()
        # 浏览器启动后，初始化 AI 导航器
        if self.navigator.page:
            self.ai_navigator = AINavigator(self.navigator.page)
    
    async def scrape_product_detail(self, url: str):
        print(f"Scraping product detail from {url}")
        
        # 1. 导航
        page_content = await self.navigator.navigate_to(url)
        
        if not page_content:
            print("❌ 页面加载失败")
            return {}

        # === 2. 混合架构检测 (RPA -> Agent) ===
        # 检查是否触发验证码
        if "验证" in page_content and "nc_1_n1z" in page_content:
            print("⚠️ [Risk] 检测到滑块验证码，切换至 AI Agent 模式...")
            if self.ai_navigator:
                success = await self.ai_navigator.solve_captcha()
                if success:
                    print("✅ [AI] 验证码通过，重新加载页面...")
                    await self.navigator.page.reload()
                    await asyncio.sleep(3)
                    page_content = await self.navigator.page.content()
                else:
                    print("❌ [AI] 验证码突破失败，请人工介入。")
                    return {}

        # 3. 视觉存证 (Visual Proof)
        product_id = url.split("/")[-1].replace(".html", "")
        save_dir = os.path.join("1688_products", product_id)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            
        proof_path = os.path.join(save_dir, "scrape_visual_proof.png")
        if self.navigator.page:
            try:
                await self.navigator.page.screenshot(path=proof_path, full_page=False)
                print(f"📸 视觉存证已保存: {proof_path}")
            except Exception as e:
                print(f"❌ 截图失败: {e}")
        
        # 4. 解析数据
        product_data = self.extractor.parse_product_detail(page_content, url)
        
        # 5. 下载图片
        images = product_data.get("images", [])
        local_images = []
        if images:
            print(f"Found {len(images)} images, starting download...")
            tasks = []
            for i, img_url in enumerate(images):
                filename = f"{product_id}_{i}.jpg"
                tasks.append(self.downloader.download_image(img_url, product_id, filename))
            
            results = await asyncio.gather(*tasks)
            local_images = [r for r in results if r]
            
        product_data["local_images"] = local_images
        product_data["screenshot_proof"] = os.path.abspath(proof_path)
        
        return product_data

    async def close(self):
        print("WebScraperAgent closing.")
        await self.navigator.close_browser()
