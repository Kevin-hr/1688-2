import asyncio
import os
from playwright.async_api import async_playwright
from src.utils.file_manager import FileManager

class WebScraperAgent:
    """
    网页抓取 Agent，负责执行 1688 搜索和商品详情提取。
    """
    def __init__(self, save_path="1688_products", user_data_dir=".openclaw/user_data"):
        self.file_manager = FileManager(save_path)
        self.user_data_dir = user_data_dir
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)

    async def scrape_1688(self, keyword, limit=10):
        """
        在 1688 上搜索关键字，并提取商品详情页链接。
        """
        async with async_playwright() as p:
            # 使用持久化上下文以利用登录状态
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                args=["--disable-blink-features=AutomationControlled"] # 规避自动化检测
            )
            page = await context.new_page()
            
            try:
                print("[Scraper] 正在访问 1688 首页以确保会话激活...")
                await page.goto("https://www.1688.com/", wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(2)
                
                import urllib.parse
                # 1688 搜索参数可能需要 GBK 编码
                try:
                    encoded_kw = urllib.parse.quote(keyword, encoding='gbk')
                except:
                    encoded_kw = urllib.parse.quote(keyword)
                
                search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded_kw}"
                
                print(f"[Scraper] 正在直接导航至搜索 URL: {search_url}")
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                print("[Scraper] 搜索页面已加载。正在等待结果...")
                await asyncio.sleep(5)
                
                # 向下滚动以触发懒加载
                print("[Scraper] 正在向下滚动以触发懒加载...")
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)
                
                # 验证当前 URL
                print(f"[Scraper] 导航后的 URL: {page.url}")
                
                # 使用多种可能的选择器匹配搜索结果
                result_selectors = [".sm-offer-item", "[data-offer-id]", ".offer-list-row", ".m-offer-item", ".offer-item", ".common-offer-item", ".img-container", ".search-offer-item"]
                items = []
                for selector in result_selectors:
                    try:
                        items = await page.query_selector_all(selector)
                        if items:
                            print(f"[Scraper] 使用选择器 {selector} 找到 {len(items)} 个结果")
                            break
                    except:
                        continue
                
                if not items:
                    print("[Scraper] 仍未找到条目。尝试更大幅度的滚动...")
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(3)
                    for selector in result_selectors:
                        items = await page.query_selector_all(selector)
                        if items:
                            print(f"[Scraper] 深度滚动后使用选择器 {selector} 找到 {len(items)} 个结果")
                            break
                
                if not items:
                    print("[Scraper] 未找到条目。正在保存失败调试截图...")
                    await page.screenshot(path="debug_final_fail.png")
            except Exception as e:
                print(f"[Scraper] 导航或选择失败: {e}。正在保存截图以供诊断。")
                await context.close()
                return []
            
            if not items:
                print("[Scraper] 等待后仍无条目。正在保存截图。")
                await page.screenshot(path="debug_search_no_items.png")
                await context.close()
                return []
            
            urls = []
            for i, item in enumerate(items[:limit]):
                # 提取商品详情链接
                href = await item.get_attribute('href')
                if not href:
                    link_el = await item.query_selector('a')
                    if link_el:
                        href = await link_el.get_attribute('href')
                
                print(f"[Scraper] 条目 {i} 原始链接: {href}")
                if href:
                    if not href.startswith('http'):
                        href = 'https:' + href
                    # 过滤并验证是否为有效的详情页链接
                    if 'detail.1688.com' in href or 'page.1688.com' in href or 'detail.m.1688.com' in href:
                        urls.append(href)
                        print(f"[Scraper] 已验证链接: {href}")
                    else:
                        print(f"[Scraper] 链接被过滤 (不匹配详情页模式)")
            
            await context.close()
            return urls

    async def scrape_product_detail(self, url):
        """
        抓取单个商品详情页的信息和图片。
        """
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await context.new_page()
            
            try:
                print(f"[Scraper] 正在抓取详情页: {url}")
                # 针对移动端页面推荐使用 domcontentloaded，因为会有持续的网络活动
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(5) # 等待 JS 渲染核心内容
                
                # 提取标题
                title = "未知商品"
                title_selectors = [
                    '.title-content', '.offer-title', '.module-title', '.title-inner',
                    'meta[property="og:title"]', '.d-title', 'h1', '.title-text', 
                    '.title-first-column'
                ]
                for sel in title_selectors:
                    try:
                        t = await page.get_attribute(sel, 'content') if 'meta' in sel else await page.inner_text(sel)
                        # 规避抓取到店名（通常包含公司或地域名称）
                        if t and t.strip() and len(t.strip()) > 5: 
                            title = t.strip()
                            if "有限公司" not in title and "店" not in title:
                                break
                    except: continue

                # 提取价格
                price = "N/A"
                price_selectors = [
                    '.price-value', '.offer-price', '.current-price', '.price-num', 
                    '.value', '.price-text', '.price'
                ]
                for sel in price_selectors:
                    try:
                        p_text = await page.inner_text(sel)
                        if p_text and p_text.strip():
                            price = p_text.strip()
                            break
                    except: continue

                # 提取属性详情
                attributes = {}
                attr_rows = await page.query_selector_all('.prop-item, .attribute-item, .obj-content, .offer-attr-item, .detail-attribute-item')
                for row in attr_rows:
                    try:
                        # 修复：query_selector 仅支持一个参数，将所有候选器合并为逻辑 OR
                        name_el = await row.query_selector('.prop-name, .attribute-name, .obj-title, .attr-name')
                        val_el = await row.query_selector('.prop-value, .attribute-value, .obj-desc, .attr-value')
                        if name_el and val_el:
                            name_text = await name_el.inner_text()
                            val_text = await val_el.inner_text()
                            attributes[name_text.strip()] = val_text.strip()
                    except: continue

                # 提取图片
                image_urls = []
                img_els = await page.query_selector_all('.tab-trigger img, .detail-gallery-img, .swipe-image img, .slider-img img')
                for img in img_els:
                    src = await img.get_attribute('src')
                    if src:
                        # 转换为较大尺寸的图片链接
                        src = src.replace('.60x60', '.400x400').replace('.40x40', '.400x400')
                        if not src.startswith('http'): src = 'https:' + src
                        image_urls.append(src)
                
                # 图片去重
                image_urls = list(dict.fromkeys(image_urls))

                product_info = {
                    "title": title,
                    "price": price,
                    "url": url,
                    "attributes": attributes,
                    "images": image_urls,
                    "description": "\n".join([f"- **{k}**: {v}" for k, v in attributes.items()])
                }
                
                # 保存数据
                product_dir, image_dir = self.file_manager.create_product_dir(title)
                self.file_manager.save_details(product_dir, product_info)
                
                # 下载图片（限制前 5 张）
                for i, img_url in enumerate(image_urls[:5]):
                    self.file_manager.save_image(img_url, image_dir, f"img_{i}.jpg")
                    
                print(f"[Scraper] 成功抓取商品: {title[:30]}")
                await context.close()
                return product_info
                
            except Exception as e:
                print(f"[Scraper] 抓取详情页出错 {url}: {e}")
                await page.screenshot(path="debug_detail_fail.png")
                await context.close()
                return None
