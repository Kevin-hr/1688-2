"""
Ozon 一键全自动化铺货核心调度流 (Auto Publisher)
-------------------------------------------------
专为 OpenClaw Agent 打造的端到端调度入口。
输入：1688 URL, 目标价格 (卢布), 目标类目 ID
输出：执行全套抓取、解析、翻译、图片下载任务，并最终调用 API 推送到 Ozon 平台。
"""

import sys
import argparse
import asyncio
from src.task_router import TaskRouter
from src.utils.ozon_api import OzonApiManager
import json

async def auto_publish(query: str, price_rub: str, category_id: int):
    """
    一键采集并发布的主线流程。支持直接传入 URL 或自然语言搜索词。
    """
    print("=" * 60)
    print(f"🚀 Ozon Auto Publisher —— 开始一键式全自动处理")
    print(f"🔍 目标输入: {query}")
    print(f"💰 目标定价: {price_rub} 卢布")
    print(f"📁 目标类目: {category_id}")
    print("=" * 60)
    
    # 1. 采集流程 (Agent + 免头爬虫)
    router = TaskRouter()
    print("\n[Step 1 & 2] 正在剥离页面与解析底层数据...")
    
    # 判断是 URL 还是搜索关键字
    if "http://" in query or "https://" in query:
        scrape_res = await router.route_url(query)
    else:
        # LLM 级自然语言意图预提取：判断排序倾向
        sort_type = None
        if "销量最高" in query or "卖得最好" in query or "最火" in query:
            sort_type = "booked"  # 1688 成交量排序代号
            print("🚀 检测到意图：优先寻找【销量最高】的货源")
        elif "最新" in query or "刚上架" in query or "追新" in query:
            sort_type = "postTime"  # 1688 最新发布排序代号
            print("🆕 检测到意图：优先寻找【最新上架】的货源")
            
        keyword = query.replace("我想找一款", "").replace("帮我找", "").replace("搜索", "")
        keyword = keyword.replace("销量最高的", "").replace("最新的", "").replace("追新上架的", "").replace("卖得最好的", "").strip()
        print(f"🕵️ 提取到搜素关键字: {keyword} (将自动为您挑选列表第一个商品上架)")
        scrape_res = await router.route(keyword, limit=1, sort_type=sort_type)
    
    if scrape_res.get("status") != "success":
        print(f"❌ 采集失败: {scrape_res.get('error')}")
        return False
        
    ozon_json_path = scrape_res.get("ozon_json_path")
    if not ozon_json_path:
        print("❌ 未能成功生成 Ozon JSON 格式文件。")
        return False
        
    print("\n[Step 3 & 4] 数据流洗涤完毕，已通过机器翻译完成本地化组装。")
    print(f"📁 数据集路径: {ozon_json_path}")
    
    # 我们需要在上传前，将用户指定的定价与类目，强制覆写覆盖到导出的 JSON 指标中
    # 因为 MVP 阶段是静态的占位符
    try:
        with open(ozon_json_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
            
        # 覆写目标值
        for item in export_data.get('products', []):
            item['custom_price_rub'] = price_rub
            item['custom_category_id'] = category_id
            
        with open(ozon_json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"⚠️ JSON 重写发生错误（可能部分自定义字段未能生效）: {e}")
    
    # 2. Ozon API 推送流程
    print("\n[Step 5] 启动封包与 Ozon Backend 的数据链连接...")
    try:
        ozon_manager = OzonApiManager()
    except ValueError as e:
        print(f"❌ API 凭据鉴定未通过: {e}")
        return False
        
    task_id = ozon_manager.upload_products(ozon_json_path)
    
    # 3. 反馈归环
    print("\n" + "=" * 60)
    if task_id:
        print(f"✅ 任务完成！任务已成功提交至 Ozon 开发组队列，内部任务追踪 ID: {task_id}。")
        return True
    else:
        print("❌ 尾盘提交遇到阻断。上游平台未发回任务 ID，请翻阅上述 Log 或查对凭证。")
        return False

def parse_args():
    parser = argparse.ArgumentParser(description="Ozon Auto Publisher Pipeline")
    parser.add_argument("--query", "-q", type=str, required=True, help="1688 商品 URL 或 自然语言搜索词 (如: 猫咪玩具)")
    parser.add_argument("--price", "-p", type=str, default="1000", help="预期的卢布售价")
    parser.add_argument("--category", "-c", type=int, default=17027484, help="分配的商品类目 ID (数字)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(auto_publish(args.query, args.price, args.category))
