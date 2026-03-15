"""
1688 扫码登录模块 (Login Module)
----------------------------------
启动 Playwright 持久化浏览器，引导用户完成 1688.com 的手动扫码登录，
并将登录后的 Cookie 和 Session 状态持久化到本地用户数据目录。
<<<<<<< HEAD

使用方式：
  python login_1688.py

执行后：
  1. 自动弹出浏览器并跳转至 1688 登录页
  2. 用手机淘宝/支付宝扫描页面上的二维码完成登录
  3. 脚本检测到登录成功后等待 5 秒确保 Cookie 写入完整
  4. 关闭浏览器，Cookie 已保存在 .openclaw/user_data/ 目录
  5. 后续运行 main.py 时无需重复登录
"""

import asyncio  # 异步 IO 库
import os       # 操作系统接口，用于目录操作
from playwright.async_api import async_playwright  # Playwright 异步 API


async def login():
    """
    启动浏览器进行手动扫码登录，并将登录状态持久化到本地。

    检测登录成功的两种方式（任一满足即判定成功）：
      1. URL 跳转离开登录域名（说明已重定向到个人中心/首页）
      2. 页面上出现用户特征元素（如头像/昵称等）

    注意：为安全考虑，本函数不会自动处理验证码，请人工完成交互。
    """
    # 持久化用户数据目录：存储登录后的 Cookie、Session、LocalStorage 等
    user_data_dir = ".openclaw/user_data"

    # 若目录不存在则创建（首次运行时）
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    async with async_playwright() as p:
        print("[Login] 正在启动浏览器进行手动登录...")

        # 使用持久化上下文启动浏览器：
        # - user_data_dir 存储本次登录后的所有浏览状态
        # - headless=False 必须保持有头模式，用户需要看到二维码页面
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # 有头模式，用户需要手动操作浏览器
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]  # 规避自动化特征检测
        )
        page = await context.new_page()

        # 导航至 1688 登录页面（会显示扫码二维码）
        await page.goto("https://login.1688.com/member/signin.htm")

        # 控制台提示用户操作步骤
        print("\n" + "=" * 50)
        print("请在弹出的浏览器窗口中完成扫码登录。")
        print("完成登录后，脚本会自动检测并保存状态。")
        print("建议在登录成功后稍等几秒，确保 Cookie 已完全写入。")
        print("=" * 50 + "\n")

        # 轮询检测登录状态（每 2 秒检查一次）
        while True:
            try:
                current_url = page.url

                # 检测方式 1：URL 不再包含登录域名，说明已成功跳转
                if ("login.1688.com" not in current_url
                        and "signin.htm" not in current_url):
                    print(f"[Login] 检测到重定向至: {current_url}")
                    print("[Login] 登录似乎成功！等待 5 秒以同步 Cookie...")
                    await asyncio.sleep(5)  # 等待浏览器将 Cookie 完整写入磁盘
                    break

                # 检测方式 2：页面出现登录后特有的用户特征元素
                # .reg-link  — 注册/登录成功后的链接
                # .member-nick — 登录后显示的昵称元素
                is_logged_in = await page.query_selector(".reg-link, .member-nick")
                if is_logged_in:
                    print("[Login] 发现用户特征元素。登录成功！")
                    await asyncio.sleep(5)  # 等待 Cookie 写入完成
                    break

            except Exception:
                # 页面导航过程中查询元素可能抛出异常，忽略并继续检测
                pass

            # 每隔 2 秒轮询一次，避免 CPU 空转
            await asyncio.sleep(2)

        print("[Login] 正在关闭浏览器并保存会话状态...")
        await context.close()  # 关闭时 Playwright 自动将 Session 写入 user_data_dir
        # 避免 emoji 编码问题
        print(f"[Login] [OK] 登录状态已保存至: {os.path.abspath(user_data_dir)}")
        print("[Login] 现在可以运行 main.py 开始采集。")


if __name__ == "__main__":
    asyncio.run(login())
=======
升级：增加 Cookie 有效性预检逻辑 (Cookie Health Check)。
"""

import asyncio
import os
from playwright.async_api import async_playwright

USER_DATA_DIR = ".openclaw/user_data"

async def check_login_status():
    """
    预检登录状态 (Health Check)。
    如果不启动浏览器界面，仅通过 headless 模式尝试访问个人中心，
    判断 Cookie 是否依然有效。
    """
    if not os.path.exists(USER_DATA_DIR):
        print("[Login Check] ❌ 未找到用户数据目录，请先运行 login() 进行首次登录。")
        return False

    print("[Login Check] 正在检查 Cookie 有效性...")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=True, # 无头模式
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()
        
        try:
            # 访问一个需要登录才能看到的页面，例如个人中心或进货单
            await page.goto("https://work.1688.com/", wait_until="domcontentloaded", timeout=15000)
            
            # 检查是否被重定向回登录页
            if "login.1688.com" in page.url or "signin" in page.url:
                print("[Login Check] ⚠️ Cookie 已失效，需要重新登录。")
                await context.close()
                return False
            
            # 检查关键元素
            # 1688 工作台通常会有 "我的阿里" 或类似的用户信息
            content = await page.content()
            if "登录" in content and "注册" in content and "退出" not in content:
                 print("[Login Check] ⚠️ 页面包含登录提示，Cookie 可能已失效。")
                 await context.close()
                 return False

            print("[Login Check] ✅ Cookie 有效，无需重新登录。")
            await context.close()
            return True
            
        except Exception as e:
            print(f"[Login Check] 检查过程异常: {e}")
            await context.close()
            return False

async def login():
    """
    启动浏览器进行手动扫码登录。
    """
    # 先检查是否已经登录且有效
    if await check_login_status():
        print("[Login] 检测到有效会话，您可以直接运行 main.py。")
        choice = input("是否强制重新登录？(y/n): ")
        if choice.lower() != 'y':
            return

    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

    async with async_playwright() as p:
        print("[Login] 正在启动浏览器进行手动登录...")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()

        await page.goto("https://login.1688.com/member/signin.htm")

        print("\n" + "=" * 50)
        print("请在弹出的浏览器窗口中完成扫码登录。")
        print("脚本会自动检测跳转。")
        print("=" * 50 + "\n")

        # 轮询检测
        while True:
            try:
                if "login.1688.com" not in page.url and "signin" not in page.url:
                     print(f"[Login] 检测到跳转至: {page.url}")
                     print("[Login] 登录成功！正在保存状态...")
                     await asyncio.sleep(5)
                     break
                await asyncio.sleep(1)
            except:
                pass

        await context.close()
        print(f"[Login] [OK] 登录状态已更新至: {os.path.abspath(USER_DATA_DIR)}")

if __name__ == "__main__":
    # 支持命令行参数选择模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        asyncio.run(check_login_status())
    else:
        asyncio.run(login())
>>>>>>> release/v1.3.3-hotfix
