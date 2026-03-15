"""
1688 扫码登录模块 (Login Module)
----------------------------------
启动 Playwright 持久化浏览器，引导用户完成 1688.com 的手动扫码登录，
并将登录后的 Cookie 和 Session 状态持久化到本地用户数据目录。
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
