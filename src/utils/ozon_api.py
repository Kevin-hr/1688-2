"""
Ozon Seller API 集成组件 (v1.3.1)
----------------------------------
处理与 Ozon Global Seller API 的直接通信。
读取本地存放的 `ozon_export.json` 里的商品列表并推送到 Ozon 草稿箱中。

改进 (v1.3.1):
  - 添加 tenacity 重试机制 (3次+指数退避)
  - 添加 logging 日志记录
  - 改进错误处理，抛出异常而非静默返回
  - 添加 tqdm 进度条显示

用户需要在项目根目录的 .env 文件中提供（不要把这俩加入版本控制库）：
  OZON_CLIENT_ID=xxxxx
  OZON_API_KEY=xxxxx
"""

import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ==================== 日志配置 ====================
def setup_logger(name: str = "OzonApi") -> logging.Logger:
    """配置并返回日志记录器"""
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出 (logs/ozon_api.log)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "ozon_api.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class OzonApiError(Exception):
    """Ozon API 自定义异常"""
    pass


class OzonApiManager:
    """
    Ozon Seller API 管理器。
    用于执行 JSON 数据的直接上架流。

    改进 (v1.3.1):
      - 添加重试机制
      - 添加日志记录
      - 改进错误处理
    """

    # 重试配置
    MAX_RETRIES = 3
    RETRY_MIN_WAIT = 1  # 最小等待秒数
    RETRY_MAX_WAIT = 10  # 最大等待秒数

    def __init__(self, logger: logging.Logger = None):
        """
        初始化对象，并加载必要的环境变量中的 Ozon API 凭据。

        参数:
            logger (logging.Logger): 可选的日志记录器实例
        """
        # 从本地加载 .env 文件，其中需存放 API Key 和 Client ID
        load_dotenv()
        self.client_id = os.getenv("OZON_CLIENT_ID")
        self.api_key = os.getenv("OZON_API_KEY")

        # 日志记录器
        self.logger = logger or setup_logger("OzonApi")

        if not self.client_id or not self.api_key:
            error_msg = "未找到 Ozon API 凭证。请在根目录下的 .env 文件中配置 OZON_CLIENT_ID 和 OZON_API_KEY。"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.base_url = "https://api-seller.ozon.ru"

        # 构造请求头，Client ID 和 API Key 缺一不可且格式需严格对应
        self.headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        self.logger.info(f"OzonApiManager 初始化完成，Client ID: {self.client_id[:4]}****")

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError, TimeoutError)),
        reraise=True
    )
    def _make_request(self, endpoint: str, payload: dict) -> dict:
        """
        发送 API 请求（带重试机制）

        参数:
            endpoint: API 端点
            payload: 请求数据

        返回:
            API 响应数据

        异常:
            OzonApiError: 请求失败时抛出
        """
        self.logger.debug(f"请求端点: {endpoint}, 数据条数: {len(payload.get('items', []))}")

        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=30)
            resp_data = response.json()

            if response.status_code == 200:
                self.logger.info(f"API 请求成功，状态码: {response.status_code}")
                return resp_data
            else:
                error_msg = f"API 请求失败，状态码: {response.status_code}, 响应: {json.dumps(resp_data, indent=2)}"
                self.logger.error(error_msg)
                raise OzonApiError(error_msg)

        except requests.RequestException as e:
            self.logger.warning(f"网络请求异常 (重试中): {e}")
            raise
        except json.JSONDecodeError as e:
            error_msg = f"JSON 解析失败: {e}"
            self.logger.error(error_msg)
            raise OzonApiError(error_msg)

    def upload_products(self, json_path: str, show_progress: bool = True):
        """
        将被处理好的 JSON 格式商品列表推送到 Ozon 平台。

        参数:
            json_path (str): 采集和转换好的 ozon_export.json 本地路径。
            show_progress (bool): 是否显示进度条，默认 True

        返回:
            str 或 int: 成功调用 Ozon 接口后返回的 task_id，出错查询则返回 None。

        异常:
            OzonApiError: 严重错误时抛出
        """
        self.logger.info(f"开始上传商品，文件路径: {json_path}")

        # 尝试导入 tqdm
        try:
            from tqdm import tqdm
            has_tqdm = True
        except ImportError:
            has_tqdm = False
            self.logger.warning("未安装 tqdm，跳过进度条显示")

        if not os.path.exists(json_path):
            error_msg = f"JSON 数据文件不存在: {json_path}"
            self.logger.error(error_msg)
            raise OzonApiError(error_msg)

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.info(f"成功读取 JSON 文件，包含 {len(data.get('products', []))} 个商品")
        except Exception as e:
            error_msg = f"无法读取或加载 JSON 文件: {e}"
            self.logger.error(error_msg)
            raise OzonApiError(error_msg)

        products = data.get("products", [])
        if not products:
            warning_msg = "数据包中未包含任何有效的商品(products)数据"
            self.logger.warning(warning_msg)
            print(f"[OzonAPI] ⚠️ {warning_msg}")
            return None

        # Ozon API 一次 `product/import` 接口调用最多支持 100 个 items 的创建
        original_count = len(products)
        if len(products) > 100:
            self.logger.warning(f"单次最多上传100个，截断 {len(products) - 100} 个商品")
            print(f"[OzonAPI] ⚠️ 警告: 单次最多上传100个，多余的商品已被自动截断。")
            products = products[:100]

        # 组装符合 Ozon API /v3/product/import 规范的商品元组序列
        items = []

        # 进度条
        iterator = tqdm(products, desc="构建商品数据") if has_tqdm and show_progress else products

        for p in iterator:
            # 1. 动态获取类目 ID
            category_id = p.get("custom_category_id") or p.get("description_category_id") or 17027487

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
                "type_id": int(category_id), # 新版 API 必需字段
                "images": p.get("images", [])[:10],
            }

            # 只有在 category_id 有效时才添加 description_category_id
            if int(category_id) > 0:
                item["description_category_id"] = int(category_id)

            item["attributes"] = p.get("attributes_mapped_api", [])  # 预留属性注入口
            items.append(item)

        payload = {
            "items": items
        }

        endpoint = f"{self.base_url}/v3/product/import"
        self.logger.info(f"正在向 Ozon 提交商品上传队列，当前队列数: {len(items)}")

        try:
            # 调用带重试的请求方法
            resp_data = self._make_request(endpoint, payload)

            if resp_data.get("result"):
                task_id = resp_data.get("result", {}).get("task_id")
                success_msg = f"上传任务接受成功！Ozon 队列 Task ID: {task_id}"
                self.logger.info(success_msg)
                print(f"[OzonAPI] ✅ {success_msg}")

                # 记录成功日志到文件
                self.logger.info(f"成功上传 {len(items)}/{original_count} 个商品，Task ID: {task_id}")
                return task_id
            else:
                error_msg = f"API 返回无 result 字段: {json.dumps(resp_data, indent=2)}"
                self.logger.error(error_msg)
                raise OzonApiError(error_msg)

        except OzonApiError:
            # 重新抛出已记录的异常
            raise
        except Exception as e:
            error_msg = f"网络连接或接口调取遇到严重异常: {e}"
            self.logger.error(error_msg)
            raise OzonApiError(error_msg)

    def get_task_status(self, task_id: int) -> dict:
        """
        获取上传任务的详细状态信息。

        参数:
            task_id (int): Ozon 返回的任务 ID

        返回:
            dict: 包含状态信息的字典
        """
        endpoint = f"{self.base_url}/v1/product/import/info"
        payload = {"task_id": int(task_id)}
        
        try:
            resp_data = self._make_request(endpoint, payload)
            return resp_data.get("result", {})
        except Exception as e:
            self.logger.error(f"获取任务状态失败: {e}")
            return {}

    def poll_task_status(self, task_id: int, interval: int = 5, timeout: int = 60) -> dict:
        """
        轮询任务状态，直到完成或超时。

        参数:
            task_id (int): 任务 ID
            interval (int): 轮询间隔（秒）
            timeout (int): 超时时间（秒）

        返回:
            dict: 最终的状态信息
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"开始轮询 Task {task_id} 状态，间隔 {interval}s，超时 {timeout}s")
        
        while time.time() - start_time < timeout:
            status_info = self.get_task_status(task_id)
            items = status_info.get("items", [])
            
            if not items:
                self.logger.warning(f"Task {task_id} 未返回任何商品状态")
                time.sleep(interval)
                continue
                
            # 检查是否所有商品都有最终状态
            # status 常值: "pending", "imported", "failed"
            all_ready = True
            for item in items:
                if item.get("status") == "pending":
                    all_ready = False
                    break
            
            if all_ready:
                self.logger.info(f"Task {task_id} 处理完成")
                return status_info
                
            self.logger.info(f"Task {task_id} 处理中... (已耗时 {int(time.time() - start_time)}s)")
            time.sleep(interval)
            
        self.logger.warning(f"Task {task_id} 状态轮询超时")
        return self.get_task_status(task_id)
