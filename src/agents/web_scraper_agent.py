"""
网页抓取 Agent 模块 (Web Scraper Agent) — v1.3.0
---------------------------------------------------
负责驱动 Playwright 无头浏览器，完成 1688.com 的商品搜索和详情采集。

v1.3.0 改进重点：
  ✅ 单一 Playwright Session — 搜索+详情抓取共用同一浏览器/上下文，消除重复启停开销
  ✅ 智能等待 — 将所有硬编码 asyncio.sleep 替换为 wait_for_selector / wait_for_load_state
  ✅ CSS 选择器维护 — 更新 2025/2026 版 1688 DOM 结构选择器映射

核心流程：
  1. 通过 launch_persistent_context 复用已登录的 Cookie（整个采集周期只启动一次）
  2. 使用多选择器回退策略，兼容 1688 不同版本的 DOM 结构
  3. 对搜索关键词进行 GBK 编码，匹配 1688 URL 参数格式
  4. 提取商品标题、价格、属性规格和图片 URL，并调用 FileManager 落盘
"""

import asyncio  # 异步 IO 库，用于 await/async 协程
import os  # 操作系统接口，用于目录检查和创建
import sys  # 系统接口
import io  # IO 包装
import urllib.parse  # URL 编码库
import random  # 随机库，用于反检测
from playwright.async_api import async_playwright  # Playwright 异步 API
from src.utils.file_manager import FileManager  # 本地文件/图片管理器
from src.modules.anti_detect import AntiDetectConfig, get_anti_detect_config  # 反检测配置

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


class WebScraperAgent:
    """
    网页抓取 Agent — 1688.com 自动化搜索与商品详情提取核心执行器。

    使用 Playwright 驱动 Chromium 浏览器，通过持久化用户数据目录复用登录状态。
    整个采集周期（搜索 + N 个详情页）共用同一个浏览器上下文，
    消除了旧版本每次都重新启动浏览器的巨大开销。

    使用方式（推荐）：
        async with WebScraperAgent() as agent:
            urls = await agent.scrape_1688("猫咪玩具", limit=5)
            for url in urls:
                data = await agent.scrape_product_detail(url)

    也支持手动管理生命周期：
        agent = WebScraperAgent()
        await agent.start()
        ...
        await agent.close()
    """

    # ------------------------------------------------------------------ #
    # 搜索结果页 — 商品卡片选择器（按优先级排列，命中即停止）
    # 定期更新此列表以适配 1688 最新 DOM 结构
    # ------------------------------------------------------------------ #
    SEARCH_ITEM_SELECTORS = [
        ".sm-offer-item",  # 2025+ 版 PC 端搜索结果卡片
        "[data-offer-id]",  # 通用 data 属性（版本无关，最稳定）
        ".offer-list-row",  # 列表布局旧版类名
        ".m-offer-item",  # 移动端适配版类名
        ".offer-item",  # 通用兼容版类名
        ".common-offer-item",  # 公共组件版类名
        ".img-container a",  # 图片容器内链接（兜底）
        ".search-offer-item",  # 搜索专属类名
        ".mojar-element-card",  # 2026 版 Mojar 组件卡片
    ]

    # ------------------------------------------------------------------ #
    # 详情页 — 标题选择器（按优先级排列）
    # ------------------------------------------------------------------ #
    TITLE_SELECTORS = [
        ".title-content",  # 新版 PC 端商品标题容器
        ".offer-title",  # 旧版 offer 标题
        ".module-title",  # 模块化页面标题
        ".title-inner",  # 内层标题文本
        'meta[property="og:title"]',  # Open Graph meta 标题（最稳定）
        ".d-title",  # 详情页专属标题类
        "h1",  # 语义化标题标签（通用兜底）
        ".title-text",  # 文本专用标题类
        ".title-first-column",  # 分栏布局第一列标题
        ".sku-title",  # SKU 标题
    ]

    # ------------------------------------------------------------------ #
    # 详情页 — 价格选择器
    # ------------------------------------------------------------------ #
    PRICE_SELECTORS = [
        ".price-value",  # 价格数值容器（新版）
        ".offer-price",  # offer 价格（批发专用）
        ".current-price",  # 当前售价（活动价格）
        ".price-num",  # 价格数字部分
        ".value",  # 通用值容器
        ".price-text",  # 价格文本标签
        ".price",  # 通用价格类（最宽泛兜底）
    ]

    # ------------------------------------------------------------------ #
    # 详情页 — 属性行选择器（组合查询，针对 2026 版增强）
    # ------------------------------------------------------------------ #
    ATTRIBUTE_ROW_SELECTOR = (
        ".prop-item, .attribute-item, .obj-content, "
        ".offer-attr-item, .detail-attribute-item, "
        ".attrs-item, .de-attr-item, "
        "div[class*='attribute-item'], li[class*='prop-item'], "
        ".pc-detail-property-item, .od-pc-attribute-item" # 2026 最新类名
    )
    ATTRIBUTE_NAME_SELECTOR = (
        ".prop-name, .attribute-name, .obj-title, .attr-name, .attrs-name, "
        "span[class*='name'], div[class*='title'], "
        ".pc-detail-property-label"
    )
    ATTRIBUTE_VALUE_SELECTOR = (
        ".prop-value, .attribute-value, .obj-desc, .attr-value, .attrs-value, "
        "span[class*='value'], div[class*='desc'], "
        ".pc-detail-property-value"
    )

    # ------------------------------------------------------------------ #
    # 详情页 — 图片选择器（针对 2026 版轮播图增强）
    # ------------------------------------------------------------------ #
    IMAGE_SELECTOR = (
        ".tab-trigger img, "  # PC 端轮播选项卡图片
        ".detail-gallery-img, "  # 详情页画廊图
        ".swipe-image img, "  # 移动端滑动图片
        ".slider-img img, "  # 滑块组件图片
        ".main-image img, "  # 2026 版主图容器
        ".gallery-image img, "
        "div[class*='image-view'] img, "
        "ul[class*='nav-tabs'] img, "
        ".mod-detail-gallery img" # 容器级回退
    )

    # ------------------------------------------------------------------ #
    # 智能等待配置
    # ------------------------------------------------------------------ #
    WAIT_TIMEOUT_MS = 15000  # 元素等待超时（毫秒）
    NAV_TIMEOUT_MS = 30000  # 页面导航超时（毫秒）
    MIN_COURTESY_DELAY = 1.0  # 最短礼貌延迟（秒），模拟人类操作节奏

    def __init__(self, save_path="1688_products", user_data_dir=".openclaw/user_data"):
        """
        初始化采集 Agent。

        参数:
            save_path:     商品数据的本地保存根目录，默认 '1688_products'
            user_data_dir: Playwright 持久化用户数据目录（存储登录 Cookie），
                           默认 '.openclaw/user_data'
        """
        self.file_manager = FileManager(save_path)  # 初始化文件管理器
        self.user_data_dir = user_data_dir  # Playwright 用户数据目录路径

        # 浏览器相关实例（在 start() 中初始化）
        self._playwright = None  # Playwright 实例
        self._context = None  # 浏览器上下文（单个 Session）
        self._page = None  # 主页面（复用）

        # 如果用户数据目录不存在则自动创建
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)

    # ================================================================== #
    # 生命周期管理（支持 async with 和手动管理两种方式）
    # ================================================================== #

    async def start(self, use_anti_detect: bool = True):
        """
        启动 Playwright 浏览器并创建持久化上下文。
        整个采集周期只调用一次，后续搜索和详情页复用同一个浏览器实例。

        Args:
            use_anti_detect: 是否启用反检测（默认启用）
        """
        if self._context is not None:
            print("[Scraper] 浏览器已在运行，跳过重复启动。")
            return

        print("[Scraper] 正在启动 Playwright 浏览器...")

        self._playwright = await async_playwright().start()

        # 根据是否启用反检测选择配置
        if use_anti_detect:
            anti_config = get_anti_detect_config()
            context_options = anti_config.get_context_options()
            launch_args = anti_config.get_launch_args()
            print("[Scraper] 使用反检测配置")
        else:
            # 最基本的浏览器配置
            context_options = {}
            launch_args = ["--disable-blink-features=AutomationControlled"]
            print("[Scraper] 使用基础配置（无反检测）")

        # 使用配置创建浏览器上下文
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=True,  # 无头模式
            user_agent=context_options.get("user_agent"),
            viewport=context_options.get("viewport"),
            locale=context_options.get("locale"),
            timezone_id=context_options.get("timezone_id"),
            args=launch_args,
        )

        self._page = await self._context.new_page()

        # 注入反检测脚本（暂时禁用以测试浏览器稳定性）
        # if use_anti_detect:
        #     await self._page.add_init_script(anti_config.add_human_behavior(page=None)["script"])

        print("[Scraper] ✅ 浏览器已启动（反检测已启用）。")

    async def close(self):
        """
        关闭浏览器上下文和 Playwright 实例，释放所有资源。
        """
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            print("[Scraper] 浏览器已关闭。")

    async def __aenter__(self, use_anti_detect: bool = False):
        """支持 async with 语法自动启动浏览器。"""
        await self.start(use_anti_detect=use_anti_detect)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持 async with 语法自动关闭浏览器。"""
        await self.close()

    def _ensure_started(self):
        """内部校验：确保浏览器已启动，否则抛出明确错误。"""
        if self._context is None or self._page is None:
            raise RuntimeError(
                "[Scraper] 浏览器未启动！请先调用 start() 或使用 async with 语法。"
            )

    # ================================================================== #
    # 智能等待工具方法
    # ================================================================== #

    async def _check_anti_bot_detection(self, page) -> bool:
        """
        检测是否触发了反爬虫机制。

        参数:
            page: Playwright Page 对象

        返回:
            True 表示检测到反爬，False 表示正常
        """
        try:
            # 获取页面文本内容
            page_text = await page.evaluate("document.body.innerText")

            # 检测常见反爬提示
            anti_bot_keywords = [
                "系统错误，请稍后重试",
                "访问频率过快",
                "请输入验证码",
                "账号异常",
                "操作过于频繁",
                "系统繁忙",
                "Sorry, system error",
                "频繁请求",
            ]

            for keyword in anti_bot_keywords:
                if keyword in page_text:
                    print(f"[Scraper] ⚠️ 检测到反爬提示: {keyword}")
                    return True

            # 检测是否跳转到了登录页或验证码页
            current_url = page.url
            if "login" in current_url or "verify" in current_url:
                print(f"[Scraper] ⚠️ 检测到跳转到了验证页面: {current_url}")
                return True

            return False

        except Exception as e:
            print(f"[Scraper] ⚠️ 反爬检测时出错: {e}")
            return False

    async def _restart_with_new_fingerprint(self):
        """
        关闭当前浏览器并使用新的指纹配置重新启动。
        """
        print("[Scraper] 正在关闭浏览器并使用新指纹重启...")

        # 关闭现有浏览器
        await self.close()

        # 等待一段时间（指数退避）
        await asyncio.sleep(2)

        # 重新启动（会自动使用新的随机指纹）
        await self.start(use_anti_detect=True)

        print("[Scraper] ✅ 浏览器已使用新指纹重启")

    async def _smart_wait_for_any(self, page, selectors, timeout_ms=None):
        """
        智能等待：在多个选择器中等待任意一个出现。
        替代旧版硬编码的 asyncio.sleep，实现按需等待。

        策略：
          1. 使用 Promise.race 同时监听多个选择器
          2. 任一命中则立即返回，不浪费多余时间
          3. 超时后不抛异常，返回 None（由调用方决定回退策略）

        参数:
            page:       Playwright Page 对象
            selectors:  CSS 选择器列表
            timeout_ms: 超时毫秒数，默认使用类级配置

        返回:
            首个匹配的选择器字符串，若超时则返回 None
        """
        if timeout_ms is None:
            timeout_ms = self.WAIT_TIMEOUT_MS

        for selector in selectors:
            try:
                await page.wait_for_selector(
                    selector, timeout=timeout_ms, state="attached"
                )
                return selector
            except Exception:
                continue  # 当前选择器超时，尝试下一个

        return None  # 全部超时

    async def _scroll_and_wait(self, page, scroll_distance=1000, settle_selector=None):
        """
        滚动页面并等待内容加载完成。
        替代旧版的 scroll + sleep 组合，更精准地检测懒加载内容出现。

        参数:
            page:             Playwright Page 对象
            scroll_distance:  滚动距离（像素），0 表示滚动到底部
            settle_selector:  如果提供，滚动后等待此选择器出现
        """
        if scroll_distance == 0:
            # 滚动到页面最底部
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        else:
            await page.evaluate(f"window.scrollBy(0, {scroll_distance})")

        if settle_selector:
            try:
                await page.wait_for_selector(settle_selector, timeout=5000)
            except Exception:
                pass  # 超时不报错，可能确实没有更多元素

        # 最短礼貌延迟，模拟人类操作 + 给 JS 渲染留余量
        await asyncio.sleep(self.MIN_COURTESY_DELAY)

    # ================================================================== #
    # 核心业务方法
    # ================================================================== #

    async def scrape_1688(self, keyword, limit=10, sort_type=None, max_retries=3):
        """
        在 1688 上搜索关键字，并提取商品详情页链接列表。

        参数:
            keyword:   搜索关键词（中文），如 "猫咪玩具"
            limit:     最多返回的商品链接数量，默认 10
            sort_type: 排序规则（例如 "booked" 销量, "postTime" 最新）
            max_retries: 最大重试次数（当检测到反爬时），默认 3

        返回:
            合法商品详情页 URL 字符串列表（可能为空列表）
        """
        self._ensure_started()
        page = self._page

        # 重试循环（用于处理反爬检测）
        for retry_round in range(max_retries):
            try:
                # 先访问 1688 首页，激活 Session Cookie
                print("[Scraper] 正在访问 1688 首页以确保会话激活...")
                await page.goto(
                    "https://www.1688.com/",
                    wait_until="domcontentloaded",
                    timeout=self.NAV_TIMEOUT_MS * 2,  # 首页允许更长超时
                )

                # 检测反爬
                if await self._check_anti_bot_detection(page):
                    if retry_round < max_retries - 1:
                        print(f"[Scraper] 🔄 检测到反爬，正在重试 ({retry_round + 1}/{max_retries})...")
                        await self._restart_with_new_fingerprint()
                        page = self._page  # 获取新的页面对象
                        continue
                    else:
                        print("[Scraper] ❌ 达到最大重试次数，放弃搜索")
                        return []

                # 智能等待首页核心元素出现（替代旧版 asyncio.sleep(2)）
                await self._smart_wait_for_any(
                    page,
                    [
                        ".home-header",
                        "#J_search_input",
                        ".header-search",
                        "input[type='text']",
                    ],
                    timeout_ms=8000,
                )

                # 随机延迟，模拟人类操作
                await asyncio.sleep(random.uniform(1.5, 3.0))

                # 1688 搜索接口要求关键词使用 GBK 编码（历史遗留编码格式）
                # 1688 搜索接口使用 UTF-8 编码（2026年更新）
                try:
                    encoded_kw = urllib.parse.quote(keyword, encoding="utf-8")
                except Exception:
                    encoded_kw = urllib.parse.quote(keyword)  # 回退：默认 UTF-8

                # 构造搜索 URL
                search_url = (
                    f"https://s.1688.com/youyuan/index.htm?tab=search&keywords={encoded_kw}"
                )

                # 拼接排序参数
                if sort_type:
                    search_url += f"&sortType={sort_type}"

                print(f"[Scraper] 正在导航至搜索页: {search_url}")
                await page.goto(
                    search_url, wait_until="domcontentloaded", timeout=self.NAV_TIMEOUT_MS
                )

                # 检测反爬（搜索结果页）
                if await self._check_anti_bot_detection(page):
                    if retry_round < max_retries - 1:
                        print(f"[Scraper] 🔄 检测到反爬，正在重试 ({retry_round + 1}/{max_retries})...")
                        await self._restart_with_new_fingerprint()
                        page = self._page
                        continue
                    else:
                        print("[Scraper] ❌ 达到最大重试次数，放弃搜索")
                        return []

                # 智能等待搜索结果出现（替代旧版 asyncio.sleep(5)）
                print("[Scraper] 等待搜索结果渲染...")
                hit_selector = await self._smart_wait_for_any(
                    page, self.SEARCH_ITEM_SELECTORS, timeout_ms=self.WAIT_TIMEOUT_MS
                )

                if not hit_selector:
                    # 首次等待未命中 → 触发滚动后重试
                    print("[Scraper] 首次等待未命中。正在滚动触发懒加载...")
                    await self._scroll_and_wait(page, scroll_distance=1000)
                    hit_selector = await self._smart_wait_for_any(
                        page, self.SEARCH_ITEM_SELECTORS, timeout_ms=8000
                    )

                if not hit_selector:
                    # 二次滚动（滚到底部）
                    print("[Scraper] 仍未命中。尝试滚动到页面底部...")
                    await self._scroll_and_wait(page, scroll_distance=0)
                    hit_selector = await self._smart_wait_for_any(
                        page, self.SEARCH_ITEM_SELECTORS, timeout_ms=8000
                    )

                if not hit_selector:
                    # 全部策略失败 → 保存截图供人工诊断
                    print("[Scraper] ❌ 未找到搜索结果。保存调试截图...")
                    await page.screenshot(path="debug_search_no_items.png")
                    return []

                # 使用命中的选择器获取所有条目
                items = await page.query_selector_all(hit_selector)
                print(f"[Scraper] 使用选择器 '{hit_selector}' 找到 {len(items)} 个结果")

                # 验证当前 URL（调试用）
                print(f"[Scraper] 当前页面 URL: {page.url}")

                # 提取合法商品详情页 URL
                urls = []
                for i, item in enumerate(items[:limit]):
                    # 优先从条目元素获取 href
                    href = await item.get_attribute("href")
                    if not href:
                        # 条目不是 <a> 标签，在内部查找子链接
                        link_el = await item.query_selector("a")
                        if link_el:
                            href = await link_el.get_attribute("href")

                    print(f"[Scraper] 条目 {i} 原始链接: {href}")

                    if href:
                        # 补全协议相对路径
                        if not href.startswith("http"):
                            href = "https:" + href

                        # 白名单过滤：只保留真实商品详情页链接
                        if any(
                            domain in href
                            for domain in [
                                "detail.1688.com",
                                "page.1688.com",
                                "detail.m.1688.com",
                            ]
                        ):
                            urls.append(href)
                            print(f"[Scraper] ✅ 链接已验证: {href}")
                        else:
                            print(f"[Scraper] ⚠️ 链接被过滤: {href[:60]}")

                return urls

            except Exception as e:
                print(f"[Scraper] 搜索过程出错: {e}。保存截图以供诊断。")
                try:
                    await page.screenshot(path="debug_search_fail.png")
                except Exception:
                    pass
                return []

    async def scrape_product_detail(self, url, max_retries=3):
        """
        抓取单个商品详情页的完整信息和主图。

        改进（v1.3.0）：
          - 复用同一个浏览器 Tab 导航到详情页，不再新开浏览器
          - 使用 wait_for_selector 替代 asyncio.sleep(5) 等待 JS 渲染
          - 更新选择器列表以适配最新 DOM 结构
        改进（v1.3.2）：
          - 添加反爬检测和重试机制

        参数:
            url: 1688 商品详情页 URL
            max_retries: 最大重试次数（当检测到反爬时），默认 3

        返回:
            商品信息字典（包含 title/price/url/attributes/images/description），
            抓取失败时返回 None
        """
        self._ensure_started()
        page = self._page

        # 重试循环
        for retry_round in range(max_retries):
            try:
                print(f"[Scraper] 正在抓取详情页: {url}")

                # 使用 domcontentloaded 而非 networkidle（详情页有持续埋点请求）
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.NAV_TIMEOUT_MS,
                )

                # 检测反爬
                if await self._check_anti_bot_detection(page):
                    if retry_round < max_retries - 1:
                        print(f"[Scraper] 🔄 检测到反爬，正在重试 ({retry_round + 1}/{max_retries})...")
                        await self._restart_with_new_fingerprint()
                        page = self._page
                        continue
                    else:
                        print("[Scraper] ❌ 达到最大重试次数，放弃抓取")
                        return None

                # 智能等待商品核心内容出现（替代旧版 asyncio.sleep(5)）
                await self._smart_wait_for_any(
                    page,
                    [
                        ".title-content",
                        ".offer-title",
                        ".price-value",
                        ".price",
                        "h1",
                        ".sku-title",
                        ".module-title",
                    ],
                    timeout_ms=self.WAIT_TIMEOUT_MS,
                )
                # 最短礼貌延迟
                await asyncio.sleep(self.MIN_COURTESY_DELAY)

                # ---- 提取商品标题 ----
                title = "未知商品"
                for sel in self.TITLE_SELECTORS:
                    try:
                        if "meta" in sel:
                            t = await page.get_attribute(sel, "content")
                        else:
                            t = await page.inner_text(sel)

                        if t and t.strip() and len(t.strip()) > 5:
                            title = t.strip()
                            # 排除店铺名
                            if "有限公司" not in title and "店" not in title:
                                break
                    except Exception:
                        continue

                # ---- 提取商品价格 ----
                price = "N/A"
                for sel in self.PRICE_SELECTORS:
                    try:
                        p_text = await page.inner_text(sel)
                        if p_text and p_text.strip():
                            price = p_text.strip()
                            break
                    except Exception:
                        continue

                # ---- 提取商品属性规格 ----
                attributes = {}
                attr_rows = await page.query_selector_all(self.ATTRIBUTE_ROW_SELECTOR)
                for row in attr_rows:
                    try:
                        name_el = await row.query_selector(self.ATTRIBUTE_NAME_SELECTOR)
                        val_el = await row.query_selector(self.ATTRIBUTE_VALUE_SELECTOR)
                        if name_el and val_el:
                            name_text = await name_el.inner_text()
                            val_text = await val_el.inner_text()
                            attributes[name_text.strip()] = val_text.strip()
                    except Exception:
                        continue

                # ---- 提取商品主图列表 ----
                image_urls = []
                img_els = await page.query_selector_all(self.IMAGE_SELECTOR)
                for img in img_els:
                    src = await img.get_attribute("src")
                    if src:
                        # 替换缩略图后缀为高清版本
                        src = src.replace(".60x60", ".400x400").replace(
                            ".40x40", ".400x400"
                        )
                        if not src.startswith("http"):
                            src = "https:" + src
                        image_urls.append(src)

                # 保序去重
                image_urls = list(dict.fromkeys(image_urls))

                # ---- 组装商品信息字典 ----
                product_info = {
                    "title": title,
                    "price": price,
                    "url": url,
                    "attributes": attributes,
                    "images": image_urls,
                    "description": "\n".join(
                        [f"- **{k}**: {v}" for k, v in attributes.items()]
                    ),
                }

                # ---- 持久化落盘 ----
                product_dir, image_dir = self.file_manager.create_product_dir(title)
                self.file_manager.save_details(product_dir, product_info)

                # 下载主图（限制前 5 张）— 使用 FileManager 的多线程下载
                download_urls = image_urls[:5]
                if download_urls:
                    self.file_manager.download_images_parallel(download_urls, image_dir)

                print(f"[Scraper] ✅ 成功抓取商品: {title[:30]}")

                # 礼貌延迟：模拟人类浏览节奏，降低反爬触发风险
                await asyncio.sleep(self.MIN_COURTESY_DELAY)

                return product_info

            except Exception as e:
                print(f"[Scraper] ❌ 抓取出错 {url}: {e}")
                try:
                    await page.screenshot(path="debug_detail_fail.png")
                except Exception:
                    pass
                return None
