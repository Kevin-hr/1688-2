# -*- coding: utf-8 -*-
"""
浏览器导航模块 (Navigator)
-------------------------
负责管理 Playwright 浏览器实例的生命周期、页面导航以及反检测脚本注入。
升级：增加 CDP Session 支持，用于更深度的反爬对抗。
"""

import asyncio
from playwright.async_api import async_playwright

class Navigator:
    """
    浏览器导航器类 (Playwright + CDP 实现)
    
    职责：
    1. 启动和关闭 Playwright 浏览器实例。
    2. 利用 CDP (Chrome DevTools Protocol) 移除 `webdriver` 特征。
    3. 处理页面跳转、Cookie 管理和加载等待。
    """
    
    def __init__(self, headless: bool = False, extension_path: str = None):
        """
        初始化导航器。
        
        参数:
            headless (bool): 是否以无头模式运行浏览器，默认为 False (有界面)。
            extension_path (str): 插件路径（可选）。
        """
        self.headless = headless
        self.extension_path = extension_path
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.client = None # CDP Session

    async def start_browser(self):
        """
        启动 Playwright 浏览器实例并建立 CDP 会话。
        """
        print(f"Navigator: 正在启动浏览器 (headless={self.headless})...")
        self.playwright = await async_playwright().start()
        
        # 启动 Chrome/Chromium
        # 增加更多反检测参数
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certifcate-errors",
            "--ignore-certifcate-errors-spki-list",
        ]
        
        if self.extension_path:
             print(f"Navigator: 加载插件 -> {self.extension_path}")
             args.append(f"--disable-extensions-except={self.extension_path}")
             args.append(f"--load-extension={self.extension_path}")

        # 注意：加载插件时不能使用 headless=True (Chrome 限制)
        if self.extension_path and self.headless:
            print("Navigator: 警告 - 加载插件时强制禁用 headless 模式")
            self.headless = False

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=args
        )
        
        # 创建上下文
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            ignore_https_errors=True
        )
        
        self.page = await self.context.new_page()
        
        # 建立 CDP 会话
        try:
            self.client = await self.context.new_cdp_session(self.page)
            # 使用 CDP 移除 webdriver 特征 (比 JS 注入更底层)
            await self.client.send("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            })
            print("Navigator: CDP 反检测脚本注入成功。")
        except Exception as e:
            print(f"Navigator: CDP 会话建立失败 - {e}")

        print("Navigator: 浏览器启动成功。")

    async def navigate_to(self, url: str):
        """
        导航至指定的 URL，并等待关键元素加载。
        """
        if not self.page:
            await self.start_browser()
            
        print(f"Navigator: 正在跳转至 {url}")
        try:
            # 导航并等待网络空闲
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 模拟人类随机等待
            await asyncio.sleep(2)
            
            # 滚动页面以触发懒加载 (模拟人类分段滚动)
            await self._human_scroll()
            
            # 获取页面内容
            content = await self.page.content()
            return content
            
        except Exception as e:
            print(f"Navigator: 导航失败 - {e}")
            return ""

    async def _human_scroll(self):
        """模拟人类分段滚动"""
        if not self.page: return
        
        try:
            # 获取页面高度
            total_height = await self.page.evaluate("document.body.scrollHeight")
            viewport_height = await self.page.evaluate("window.innerHeight")
            
            current_position = 0
            while current_position < total_height:
                # 随机滚动距离
                scroll_step = 300 + 100 # 300-400px
                current_position += scroll_step
                
                await self.page.evaluate(f"window.scrollTo(0, {current_position})")
                
                # 随机停顿
                await asyncio.sleep(0.5) 
                
                # 更新高度 (应对无限加载)
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height > total_height:
                    total_height = new_height
                    
                # 别滚到底就不动了，滚两三屏通常够了
                if current_position > 3000: 
                    break
                    
        except Exception as e:
            print(f"Navigator: 滚动异常 - {e}")

    async def close_browser(self):
        """
        关闭浏览器实例并释放资源。
        """
        print("Navigator: 正在关闭浏览器...")
        if self.client:
            try:
                await self.client.detach()
            except:
                pass
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self.client = None
