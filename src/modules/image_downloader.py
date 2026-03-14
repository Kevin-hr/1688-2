"""
图片下载模块 - 多线程并行下载
"""

import os
import time
import requests
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class ImageDownloader:
    """
    图片下载器

    特性：
    - 多线程并行下载
    - 指数退避重试
    - 进度跟踪
    """

    DEFAULT_MAX_WORKERS = 5
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 15

    def __init__(
        self,
        max_workers: int = None,
        max_retries: int = None,
        timeout: int = None
    ):
        """
        初始化下载器

        Args:
            max_workers: 最大并行下载数
            max_retries: 最大重试次数
            timeout: 下载超时(秒)
        """
        self.max_workers = max_workers or self.DEFAULT_MAX_WORKERS
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def download(
        self,
        url: str,
        folder: str,
        filename: str = None,
        retry_delay: float = 1.0
    ) -> Tuple[str, bool, Optional[str]]:
        """
        下载单张图片

        Args:
            url: 图片URL
            folder: 保存目录
            filename: 保存文件名（默认从URL提取）
            retry_delay: 重试基础延迟

        Returns:
            (filename, success, error_message)
        """
        # 生成文件名
        if not filename:
            filename = self._extract_filename(url)

        # 确保目录存在
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        # 重试循环
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout, stream=True)

                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return (filename, True, None)

                last_error = f"HTTP {response.status_code}"

            except requests.exceptions.Timeout:
                last_error = "超时"
            except requests.exceptions.ConnectionError:
                last_error = "连接失败"
            except Exception as e:
                last_error = str(e)

            # 指数退避
            if attempt < self.max_retries:
                delay = retry_delay * (2 ** attempt)
                time.sleep(delay)

        return (filename, False, last_error)

    def download_batch(
        self,
        urls: List[str],
        folder: str,
        max_count: int = 5,
        prefix: str = "img_"
    ) -> Tuple[int, int]:
        """
        批量下载图片

        Args:
            urls: 图片URL列表
            folder: 保存目录
            max_count: 最大下载数量
            prefix: 文件名前缀

        Returns:
            (成功数, 失败数)
        """
        urls = urls[:max_count]
        total = len(urls)

        if total == 0:
            return (0, 0)

        print(f"[Downloader] 开始下载 {total} 张图片...")

        success_count = 0
        fail_count = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for i, url in enumerate(urls):
                filename = f"{prefix}{i}.jpg"
                future = executor.submit(self.download, url, folder, filename)
                futures[future] = (i, url, filename)

            for future in as_completed(futures):
                i, url, filename = futures[future]
                try:
                    fname, ok, error = future.result()
                    if ok:
                        success_count += 1
                        print(f"[Downloader] ✅ ({success_count}/{total}) {fname}")
                    else:
                        fail_count += 1
                        print(f"[Downloader] ❌ {fname}: {error}")
                except Exception as e:
                    fail_count += 1
                    print(f"[Downloader] ❌ {filename}: {e}")

        print(f"[Downloader] 完成: 成功 {success_count}, 失败 {fail_count}")
        return (success_count, fail_count)

    @staticmethod
    def _extract_filename(url: str) -> str:
        """从URL提取文件名"""
        # 尝试从路径提取
        path = url.split("?")[0]
        filename = os.path.basename(path)

        # 如果没有扩展名，添加 .jpg
        if "." not in filename:
            filename += ".jpg"

        return filename

    @staticmethod
    def upgrade_image_url(url: str, size: str = "400x400") -> str:
        """
        升级图片URL为高清版本

        Args:
            url: 原始URL
            size: 目标尺寸

        Returns:
            升级后的URL
        """
        # 1688 缩略图升级
        for suffix in [".60x60", ".40x40", ".100x100", ".200x200"]:
            url = url.replace(suffix, f".{size}")

        # 添加协议
        if url.startswith("//"):
            url = "https:" + url

        return url


# 便捷函数
def download_image(url: str, folder: str, filename: str = None) -> bool:
    """快速下载单张图片"""
    downloader = ImageDownloader()
    _, success, _ = downloader.download(url, folder, filename)
    return success


def download_images(urls: List[str], folder: str, max_count: int = 5) -> Tuple[int, int]:
    """快速批量下载"""
    downloader = ImageDownloader()
    return downloader.download_batch(urls, folder, max_count)


if __name__ == "__main__":
    # 测试
    downloader = ImageDownloader()

    # URL 升级测试
    test_urls = [
        "https://cbu01.alicdn.com/img/ibank/O1CN01xyz123_!!828676752814.60x60.jpg",
        "https://cbu01.alicdn.com/img/ibank/O1CN01xyz123_!!828676752814.jpg",
    ]

    print("URL 升级测试:")
    for url in test_urls:
        upgraded = downloader.upgrade_image_url(url)
        print(f"原始: {url}")
        print(f"升级: {upgraded}")
        print()
