"""
文件管理器模块 (File Manager) — v1.3.0
-----------------------------------------
负责在本地文件系统中创建商品目录结构、保存 Markdown 详情文件、下载并保存商品图片。

v1.3.0 改进：
  ✅ 多线程并行下载 — 使用 concurrent.futures.ThreadPoolExecutor 并行下载图片
  ✅ 指数退避重试 — 下载失败时自动重试（最多 3 次），每次间隔递增
  ✅ 下载进度提示 — 实时显示并行下载状态

目录结构约定（每次采集后在 base_path 下生成）：
  base_path/
  └── {商品名称}/
      ├── detail.md        — Markdown 格式的商品详情报告
      └── images/
          ├── img_0.jpg    — 第1张主图
          ├── img_1.jpg    — 第2张主图
          └── ...          — 最多5张
"""

import os  # 操作系统接口，用于目录创建和路径拼接
import requests  # HTTP 请求库，用于下载图片
import re  # 正则表达式，用于过滤文件名中的非法字符
import time  # 时间库，用于重试间隔
from concurrent.futures import ThreadPoolExecutor, as_completed  # 多线程并行下载


class FileManager:
    """
    文件管理器 — 负责创建商品存储目录、保存文本详情和下载图片。

    每个商品独立一个子目录，目录名为商品标题（经过文件名合法化处理）。
    图片下载采用多线程并行 + 指数退避重试机制，提升下载效率和稳定性。
    """

    # 多线程下载配置
    MAX_DOWNLOAD_WORKERS = 5  # 并行下载线程数
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_BASE_DELAY = 1.0  # 重试基础延迟（秒），实际延迟 = base * 2^attempt
    DOWNLOAD_TIMEOUT = 15  # 单张图片下载超时（秒）

    def __init__(self, base_path="1688_products"):
        """
        初始化文件管理器，创建根目录（若不存在）。

        参数:
            base_path: 所有商品数据的根存储目录，默认 '1688_products'
        """
        self.base_path = base_path  # 根目录路径

        # 若根目录不存在则自动创建
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def sanitize_filename(self, filename):
        """
        过滤并清洗文件名中的非法字符，确保跨平台（Windows/macOS/Linux）可用。

        Windows 不允许的文件名字符：\\ / * ? : " < > |
        此函数将上述字符全部替换为空字符串。

        参数:
            filename: 原始文件名字符串（通常为商品标题）

        返回:
            清洗后的合法文件名字符串
        """
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def create_product_dir(self, product_name):
        """
        为指定商品创建独立的存储目录和图片子目录。

        目录结构：
          {base_path}/{sanitized_product_name}/
          └── images/

        参数:
            product_name: 商品名称（通常为从网页抓取到的原始标题）

        返回:
            (product_dir, image_dir) 元组：
              product_dir — 商品根目录的完整路径
              image_dir   — 图片子目录的完整路径
        """
        sanitized_name = self.sanitize_filename(product_name)
        product_dir = os.path.join(self.base_path, sanitized_name)
        image_dir = os.path.join(product_dir, "images")

        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        return product_dir, image_dir

    def _download_single_image(self, url, folder, filename, retries=None):
        """
        下载单张图片，带指数退避重试机制和内容验证。

        重试策略：
          - 第1次失败 → 等待 1 秒后重试
          - 第2次失败 → 等待 2 秒后重试
          - 第3次失败 → 放弃，返回失败

        验证：
          - 检查文件大小（< 5KB 视为无效图片）
          - 检查图片文件头（JPEG: FFD8, PNG: 8950）

        参数:
            url:      图片 HTTPS URL
            folder:   目标保存目录
            filename: 保存文件名
            retries:  最大重试次数，默认使用类级配置

        返回:
            (filename, True/False, error_msg) 三元组
        """
        if retries is None:
            retries = self.MAX_RETRIES

        last_error = None
        for attempt in range(retries + 1):
            try:
                response = requests.get(url, timeout=self.DOWNLOAD_TIMEOUT)

                if response.status_code == 200:
                    # 检查内容是否有效
                    content = response.content
                    if len(content) < 5120:  # 小于 5KB 可能是占位图
                        last_error = f"文件太小 ({len(content)} bytes)，疑似无效图片"
                        if attempt < retries:
                            delay = self.RETRY_BASE_DELAY * (2**attempt)
                            print(
                                f"[Downloader] ⚠️ {filename} {last_error}，{delay:.0f}秒后重试 ({attempt + 1}/{retries})"
                            )
                            time.sleep(delay)
                            continue
                        return (filename, False, last_error)

                    # 检查文件头魔数
                    if len(content) >= 2:
                        magic = content[:2]
                        if magic not in [b"\xff\xd8", b"\x89\x50"]:  # JPEG 或 PNG
                            last_error = f"无效图片格式: {magic.hex()}"
                            if attempt < retries:
                                delay = self.RETRY_BASE_DELAY * (2**attempt)
                                print(
                                    f"[Downloader] ⚠️ {filename} {last_error}，{delay:.0f}秒后重试 ({attempt + 1}/{retries})"
                                )
                                time.sleep(delay)
                                continue
                            return (filename, False, last_error)

                    filepath = os.path.join(folder, filename)
                    with open(filepath, "wb") as f:
                        f.write(content)
                    return (filename, True, None)
                else:
                    last_error = f"HTTP {response.status_code}"

            except requests.exceptions.Timeout:
                last_error = "请求超时"
            except requests.exceptions.ConnectionError:
                last_error = "连接失败"
            except Exception as e:
                last_error = str(e)

            # 指数退避：delay = base × 2^attempt
            if attempt < retries:
                delay = self.RETRY_BASE_DELAY * (2**attempt)
                print(
                    f"[Downloader] ⚠️ {filename} 下载失败({last_error})，{delay:.0f}秒后重试 ({attempt + 1}/{retries})"
                )
                time.sleep(delay)

        return (filename, False, last_error)

    def save_image(self, url, folder, filename):
        """
        从指定 URL 下载图片并保存到本地（单线程版本，兼容旧接口）。

        参数:
            url:      图片 HTTPS URL
            folder:   图片保存目标目录
            filename: 保存文件名

        返回:
            True — 下载成功 / False — 下载失败
        """
        _, success, error = self._download_single_image(url, folder, filename)
        if not success:
            print(f"[FileManager] ❌ 图片下载最终失败 {url}: {error}")
        return success

    def download_images_parallel(self, image_urls, folder, max_count=5):
        """
        多线程并行下载多张图片，带重试和进度汇总。

        使用 ThreadPoolExecutor 并行提交所有下载任务，
        as_completed 逐个收取结果并打印进度。

        参数:
            image_urls: 图片 URL 列表
            folder:     图片保存目标目录
            max_count:  最多下载图片数量，默认 5

        返回:
            (成功数, 失败数) 元组
        """
        urls_to_download = image_urls[:max_count]
        total = len(urls_to_download)

        if total == 0:
            print("[Downloader] 无图片需要下载。")
            return (0, 0)

        print(
            f"[Downloader] 开始并行下载 {total} 张图片（{self.MAX_DOWNLOAD_WORKERS} 线程）..."
        )

        success_count = 0
        fail_count = 0

        # 使用线程池并行下载
        with ThreadPoolExecutor(max_workers=self.MAX_DOWNLOAD_WORKERS) as executor:
            # 提交所有下载任务
            future_to_info = {}
            for i, url in enumerate(urls_to_download):
                filename = f"img_{i}.jpg"
                future = executor.submit(
                    self._download_single_image, url, folder, filename
                )
                future_to_info[future] = (i, url, filename)

            # 逐个收取完成的任务结果
            for future in as_completed(future_to_info):
                idx, url, filename = future_to_info[future]
                try:
                    fname, ok, error = future.result()
                    if ok:
                        success_count += 1
                        print(
                            f"[Downloader] ✅ ({success_count}/{total}) {fname} 下载成功"
                        )
                    else:
                        fail_count += 1
                        print(f"[Downloader] ❌ {fname} 最终失败: {error}")
                except Exception as e:
                    fail_count += 1
                    print(f"[Downloader] ❌ {filename} 线程异常: {e}")

        print(f"[Downloader] 下载完成：成功 {success_count}，失败 {fail_count}")
        return (success_count, fail_count)

    def save_details(self, product_dir, details):
        """
        将商品详情保存为 Markdown 格式的 detail.md 文件。

        输出文件格式示例：
          # 猫咪静音球不吵人自嗨解闷玩具

          **价格**: ¥3.70
          **来源链接**: https://detail.1688.com/offer/828676752814.html

          ## 详细描述/规格属性
          - **材质**: EVA发泡
          - **颜色**: 随机发货

        参数:
            product_dir: 商品目录路径
            details:     商品信息字典，需包含 title/price/url/description 字段
        """
        filepath = os.path.join(product_dir, "detail.md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {details.get('title', '商品详情')}\n\n")
            f.write(f"**价格**: {details.get('price', 'N/A')}\n")
            f.write(f"**来源链接**: {details.get('url', 'N/A')}\n\n")
            f.write("## 详细描述/规格属性\n")
            f.write(details.get("description", "暂无详细描述。"))
