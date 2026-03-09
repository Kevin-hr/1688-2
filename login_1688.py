import asyncio
import os
from playwright.async_api import async_playwright

async def login():
    """
    启动浏览器进行手动扫码登录，并将登录状态持久化到本地。
    """
    user_data_dir = ".openclaw/user_data"
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    async with async_playwright() as p:
        print("[Login] 正在启动浏览器进行手动登录...")
        # 启动持久化上下文，保存登录 Cookie
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"] # 规避自动化检测
        )
        page = await context.new_page()
        
        # 导航至 1688 登录页面
        await page.goto("https://login.1688.com/member/signin.htm")
        
        print("\n" + "="*50)
        print("请在弹出的浏览器窗口中完成扫码登录。")
        print("完成登录后，脚本会自动检测并保存状态。")
        print("建议在登录成功后稍等几秒，确保 Cookie 已完全写入。")
        print("="*50 + "\n")

        # 循环检测登录状态
        while True:
            try:
                current_url = page.url
                # 如果 URL 不再包含登录关键词，说明可能已跳转至个人中心或首页
                if "login.1688.com" not in current_url and "signin.htm" not in current_url:
                    print(f"[Login] 检测到重定向至: {current_url}")
                    print("[Login] 登录似乎成功！等待 5 秒以同步 Cookie...")
                    await asyncio.sleep(5)
                    break
                
                # 检查页面是否包含登录后的特征元素
                is_logged_in = await page.query_selector(".reg-link, .member-nick")
                if is_logged_in:
                    print("[Login] 发现用户特征元素。登录成功！")
                    await asyncio.sleep(5)
                    break
            except Exception:
                pass
            
            await asyncio.sleep(2)

        print("[Login] 正在关闭浏览器并保存会话状态...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(login())
