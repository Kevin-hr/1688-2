import os
import requests
import re

class FileManager:
    """
    文件管理器，负责创建目录、保存文本详情和下载图片。
    """
    def __init__(self, base_path="1688_products"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def sanitize_filename(self, filename):
        """
        过滤文件名中的非法字符。
        """
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def create_product_dir(self, product_name):
        """
        为每个商品创建独立的存储目录和图片子目录。
        """
        sanitized_name = self.sanitize_filename(product_name)
        product_dir = os.path.join(self.base_path, sanitized_name)
        image_dir = os.path.join(product_dir, "images")
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            
        return product_dir, image_dir

    def save_image(self, url, folder, filename):
        """
        从 URL 下载并保存图片。
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(os.path.join(folder, filename), "wb") as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"图片下载失败 {url}: {e}")
        return False

    def save_details(self, product_dir, details):
        """
        将商品详情（标题、价格、属性等）保存为 Markdown 文件。
        """
        with open(os.path.join(product_dir, "detail.md"), "w", encoding="utf-8") as f:
            f.write(f"# {details.get('title', '商品详情')}\n\n")
            f.write(f"**价格**: {details.get('price', 'N/A')}\n")
            f.write(f"**来源链接**: {details.get('url', 'N/A')}\n\n")
            f.write("## 详细描述/规格属性\n")
            f.write(details.get('description', '暂无详细描述。'))
