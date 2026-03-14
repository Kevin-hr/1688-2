"""
反检测配置模块 - 增强爬虫的反检测能力
"""

import random
import secrets


class AntiDetectConfig:
    """
    反检测配置

    提供多种反检测策略以绕过网站的反爬机制
    """

    # User-Agent 列表（随机选择）
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # Chrome on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]

    # 屏幕分辨率
    SCREEN_SIZES = [
        (1920, 1080),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1280, 720),
    ]

    # 语言设置
    LANGUAGES = [
        "zh-CN,zh;q=0.9,en;q=0.8",
        "zh-CN,zh;q=0.9",
        "zh,en;q=0.9,en-US;q=0.8",
    ]

    # 时区
    TIMEZONES = [
        "Asia/Shanghai",
        "Asia/Hong_Kong",
        "Asia/Chongqing",
    ]

    def __init__(self):
        pass

    def get_random_user_agent(self) -> str:
        """随机获取 User-Agent"""
        return random.choice(self.USER_AGENTS)

    def get_random_screen_size(self) -> tuple:
        """随机获取屏幕分辨率"""
        return random.choice(self.SCREEN_SIZES)

    def get_random_language(self) -> str:
        """随机获取语言设置"""
        return random.choice(self.LANGUAGES)

    def get_random_timezone(self) -> str:
        """随机获取时区"""
        return random.choice(self.TIMEZONES)

    def get_launch_args(self) -> list:
        """
        获取浏览器启动参数

        包含多种反检测配置
        """
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",  # 避免共享内存问题
            "--no-sandbox",  # 禁用沙箱（某些环境需要）
            "--disable-setuid-sandbox",
            "--disable-web-security",  # 禁用同源策略
            "--allow-running-insecure-content",  # 允许混合内容
            "--disable-extensions",
            "--disable-plugins",
            "--disable-default-apps",
            "--disable-sync",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
        ]
        return args

    def get_viewport_config(self) -> dict:
        """获取随机视口配置"""
        width, height = self.get_random_screen_size()
        return {
            "width": width,
            "height": height,
            "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
            "is_mobile": False,
            "has_touch": False,
        }

    def get_context_options(self) -> dict:
        """
        获取浏览器上下文配置

        包含指纹伪装
        """
        viewport = self.get_viewport_config()

        return {
            "viewport": viewport,
            "user_agent": self.get_random_user_agent(),
            "locale": "zh-CN",
            "timezone_id": self.get_random_timezone(),
            "languages": self.get_random_language(),
            "permissions": ["geolocation", "notifications"],
            "extra_http_headers": {
                "Accept-Language": self.get_random_language(),
            },
        }

    @staticmethod
    def add_human_behavior(page) -> dict:
        """
        添加人类行为脚本

        返回可在页面中执行的脚本
        """
        # 注入反检测脚本
        script = """
        // 修改 navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // 修改 plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // 修改 languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en']
        });

        // 添加 chrome 对象
        window.chrome = {
            runtime: {}
        };

        // 修改 permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // 修改 permissions
        Object.defineProperty(navigator, 'permissions', {
            value: {
                query: (params) => {
                    if (params.name === 'notifications') {
                        return Promise.resolve({ state: 'default' });
                    }
                    return Promise.resolve({ state: 'prompt' });
                }
            }
        });
        """
        return {"script": script}


# 全局配置实例
_config = None


def get_anti_detect_config() -> AntiDetectConfig:
    """获取反检测配置实例"""
    global _config
    if _config is None:
        _config = AntiDetectConfig()
    return _config


if __name__ == "__main__":
    # 测试
    config = AntiDetectConfig()

    print("反检测配置测试:")
    print(f"User-Agent: {config.get_random_user_agent()[:50]}...")
    print(f"屏幕: {config.get_random_screen_size()}")
    print(f"语言: {config.get_random_language()}")
    print(f"时区: {config.get_random_timezone()}")
    print(f"启动参数: {len(config.get_launch_args())} 个")
