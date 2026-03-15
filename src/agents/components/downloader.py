# -*- coding: utf-8 -*-
"""
下载器模块 (Downloader)
----------------------
负责网络资源的下载和本地文件系统的存储管理 (Requests 实现)。
"""

import os
import requests
import asyncio
import aiofiles

class Downloader:
    """
    下载器类 (异步实现)
    
    职责：
    1. 管理下载目录的创建。
    2. 下载图片、视频等静态资源。
    3. 处理文件命名和冲突。
    """
    
    def __init__(self, download_dir: str = "1688_products"):
        """
        初始化下载器。
        
        参数:
            download_dir (str): 文件保存的根目录。
        """
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"Downloader: 创建根目录 {self.download_dir}")

    async def download_image(self, url: str, folder_name: str, filename: str) -> str:
        """
        从指定 URL 下载图片。
        
        参数:
            url (str): 图片的网络地址。
            folder_name (str): 商品专属文件夹名。
            filename (str): 保存的文件名。
            
        返回:
            str: 图片保存的绝对路径，失败返回 None。
        """
        # 构建完整路径
        save_dir = os.path.join(self.download_dir, folder_name, "images")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            
        filepath = os.path.join(save_dir, filename)
        
        if os.path.exists(filepath):
            print(f"Downloader: 文件已存在，跳过 {filename}")
            return filepath

        print(f"Downloader: 正在下载 {url} -> {filename}")
        
        try:
            # 使用 asyncio.to_thread 运行同步的 requests (简化依赖，或者可以用 aiohttp)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url, timeout=10))
            
            if response.status_code == 200:
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(response.content)
                return filepath
            else:
                print(f"Downloader: 下载失败 {url}, 状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"Downloader: 下载异常 {url} - {e}")
            return None
