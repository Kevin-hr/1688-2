"""
Ozon Seller API 集成组件 (MVP)
----------------------------------
处理与 Ozon Global Seller API 的直接通信。
读取本地存放的 `ozon_export.json` 里的商品列表并推送到 Ozon 草稿箱中。
用户需要在项目根目录的 .env 文件中提供（不要把这俩加入版本控制库）：
  OZON_CLIENT_ID=xxxxx
  OZON_API_KEY=xxxxx
"""

import os
import json
import requests
from dotenv import load_dotenv

class OzonApiManager:
    """
    Ozon Seller API 管理器。
    用于执行 JSON 数据的直接上架流。
    """
    
    def __init__(self):
        """
        初始化对象，并加载必要的环境变量中的 Ozon API 凭据。
        """
        # 从本地加载 .env 文件，其中需存放 API Key 和 Client ID
        load_dotenv()
        self.client_id = os.getenv("OZON_CLIENT_ID")
        self.api_key = os.getenv("OZON_API_KEY")
        
        if not self.client_id or not self.api_key:
            raise ValueError("未找到 Ozon API 凭证。请在根目录下的 .env 文件中配置 OZON_CLIENT_ID 和 OZON_API_KEY。")
            
        self.base_url = "https://api-seller.ozon.ru"
        
        # 构造请求头，Client ID 和 API Key 缺一不可且格式需严格对应
        self.headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
    def upload_products(self, json_path: str):
        """
        将被处理好的 JSON 格式商品列表推送到 Ozon 平台。
        由于是 MVP 版本，这里将做简单的数据转换来验证联通性。
        
        参数:
            json_path (str): 采集和转换好的 ozon_export.json 本地路径。
            
        返回:
            str 或 int: 成功调用 Ozon 接口后返回的 task_id，出错查询则返回 None。
        """
        if not os.path.exists(json_path):
            print(f"[OzonAPI] ❌ JSON 数据文件不存在: {json_path}")
            return None
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[OzonAPI] ❌ 无法读取或加载 JSON 文件: {e}")
            return None
            
        products = data.get("products", [])
        if not products:
            print("[OzonAPI] ⚠️ 数据包中未包含任何有效的商品(products)数据。")
            return None
            
        # Ozon API 一次 `product/import` 接口调用最多支持 100 个 items 的创建
        # 为了保证 MVP 测试的安全，这强制做最多100个的截断保护
        if len(products) > 100:
            print("[OzonAPI] ⚠️ 警告: 单次最多上传100个，多余的商品已被自动截断。")
            products = products[:100]
            
        # 组装符合 Ozon API /v3/product/import 规范的商品元组序列
        items = []
        for p in products:
            # 1. 动态获取类目 ID (优先从 JSON 中获取自定义或建议类目)
            # 如果 json 中有 custom_category_id 则使用，否则使用占位符
            category_id = p.get("custom_category_id") or 17027484 
            
            # 2. 动态获取定价 (已经由 Transformer 计算好并由 auto_publish 可能覆写)
            price_rub = p.get("custom_price_rub") or p.get("price_rub", "1000")
            
            # 3. 动态获取物流参数
            weight = p.get("weight_g", 100)
            depth = p.get("depth_mm", 100)
            width = p.get("width_mm", 100)
            height = p.get("height_mm", 100)
            
            # 按 Ozon Import 数据结构映射
            item = {
                "offer_id": p.get("offer_id", "Unknown"),
                "name": p.get("name", "未命名商品"),
                "depth": int(depth),
                "width": int(width),
                "height": int(height),
                "dimension_unit": "mm",
                "weight": int(weight),
                "weight_unit": "g",
                "price": str(price_rub),
                "vat": "0",             # 默认设为 0 (免税)
                "category_id": int(category_id),
                "images": p.get("images", [])[:10],
                "description_category_id": int(category_id),
                "attributes": p.get("attributes_mapped_api", []) # 预留属性注入口
            }
            items.append(item)
            
        payload = {
            "items": items
        }
        
        endpoint = f"{self.base_url}/v3/product/import"
        print(f"[OzonAPI] 正在向 Ozon 提交商品上传队列，当前队列数: {len(items)} ...")
        
        try:
            # 将组装好的 payload POST 到 Ozon 对应 API，加入超时安全机制
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=30)
            resp_data = response.json()
            
            if response.status_code == 200:
                task_id = resp_data.get("result", {}).get("task_id")
                print(f"[OzonAPI] ✅ 上传任务接受成功！Ozon 队列 Task ID: {task_id}")
                return task_id
            else:
                print(f"[OzonAPI] ❌ 接口请求返回错误码 ({response.status_code}): {json.dumps(resp_data, indent=2)}")
                return None
                
        except Exception as e:
            print(f"[OzonAPI] ❌ 网络连接或接口调取遇到严重异常: {e}")
            return None
