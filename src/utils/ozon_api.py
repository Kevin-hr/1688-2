# -*- coding: utf-8 -*-
"""
Ozon API 管理模块 (OzonApiManager)
---------------------------------
负责与 Ozon Seller API 进行交互，处理商品上传、状态查询和任务轮询 (真实 API 实现)。
"""

import json
import time
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class OzonApiManager:
    """
    Ozon API 管理器类 (真实实现)
    
    职责：
    1. 封装 Ozon API 调用（商品导入、状态检查）。
    2. 提供任务状态的轮询机制。
    3. 处理 API 认证和错误重试。
    """
    
    BASE_URL = "https://api-seller.ozon.ru"
    
    def __init__(self):
        self.client_id = os.getenv("OZON_CLIENT_ID")
        self.api_key = os.getenv("OZON_API_KEY")
        
        if not self.client_id or not self.api_key:
            print("⚠️ 警告: 未配置 OZON_CLIENT_ID 或 OZON_API_KEY，API 调用将失败。")
        
        self.headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def upload_products(self, json_path: str):
        """
        上传商品数据到 Ozon (/v2/product/import)。
        
        参数:
            json_path (str): 包含 Ozon 格式商品数据的 JSON 文件路径。
            
        返回:
            str: Ozon 返回的任务 ID (task_id)。
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON 文件不存在: {json_path}")
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 确保数据格式符合 Ozon 要求 (通常是 {"items": [...]})
        # 如果我们的文件是列表，可能需要包装一下
        if isinstance(data, list):
            payload = {"items": data}
        elif "items" in data:
            payload = data
        elif "products" in data: # 兼容旧格式
             payload = {"items": data["products"]}
        else:
             # 假设它是单个商品字典
             payload = {"items": [data]}

        url = f"{self.BASE_URL}/v3/product/import"
        
        print(f"OzonApi: 正在上传商品数据 ({len(payload.get('items', []))} 个商品)...")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            task_id = str(result.get("result", {}).get("task_id"))
            print(f"OzonApi: 上传成功! Task ID: {task_id}")
            return task_id
        except Exception as e:
            print(f"❌ OzonApi: 上传失败 - {e}")
            if 'response' in locals():
                print(f"   响应内容: {response.text}")
            return None
    
    def get_task_status(self, task_id: str):
        """
        查询导入任务的状态 (/v1/product/import/info)。
        
        参数:
            task_id (str): 任务 ID。
            
        返回:
            dict: 任务状态详情。
        """
        url = f"{self.BASE_URL}/v1/product/import/info"
        payload = {"task_id": int(task_id)}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json().get("result", {})
            # 兼容性处理：有时 API 不返回 result 而是直接返回数据
            if not result:
                result = response.json()
            return result
        except Exception as e:
            print(f"❌ OzonApi: 查询状态失败 - {e}")
            return {"status": "error", "error": str(e)}

    def poll_task_status(self, task_id: str, timeout: int = 300, interval: int = 5):
        """
        轮询任务状态，直到任务完成或超时。
        """
        if not task_id:
            return None
            
        print(f"🔄 OzonApi: 开始轮询任务 {task_id} (超时={timeout}s, 间隔={interval}s)...")
        start_time = time.time()
        
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(f"⚠️ 轮询超时: 已超过 {timeout} 秒。")
                return self.get_task_status(task_id)
            
            status_info = self.get_task_status(task_id)
            status = status_info.get("status", "unknown")
            
            # 打印简要进度
            items = status_info.get("items", [])
            total_items = len(items) if items else 0
            processed_items = sum(1 for item in items if item.get("status") in ["imported", "failed"])
            print(f"   当前状态: {status} | 进度: {processed_items}/{total_items}")

            # 检查终止状态
            # Ozon 状态通常是 pending -> imported / failed
            if status in ["imported", "failed"]:
                print(f"✅ 任务 {task_id} 已完成，最终状态: {status}")
                return status_info
            
            time.sleep(interval)
