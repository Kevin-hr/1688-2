
import sys
import json
from src.utils.ozon_api import OzonApiManager

def main():
    if len(sys.argv) < 2:
        print("用法: python check_task_status.py <task_id>")
        sys.exit(1)
        
    task_id = sys.argv[1]
    print(f"🔍 正在查询 Task ID: {task_id} 的状态...")
    
    try:
        ozon_manager = OzonApiManager()
        status_info = ozon_manager.get_task_status(task_id)
        
        print("\n" + "="*50)
        print(f"📊 任务详情")
        print("="*50)
        print(json.dumps(status_info, indent=2, ensure_ascii=False))
        print("="*50 + "\n")
        
        items = status_info.get("items", [])
        if items:
            print(f"📦 商品处理进度: {len(items)} 个商品")
            for i, item in enumerate(items):
                offer_id = item.get("offer_id", "N/A")
                status = item.get("status", "unknown")
                errors = item.get("errors", [])
                
                status_icon = "⏳" if status == "pending" else "✅" if status == "imported" else "❌"
                print(f"[{i+1}] {status_icon} {offer_id}: {status}")
                if errors:
                    for err in errors:
                        print(f"    ⚠️ 错误: {err.get('message')} (Code: {err.get('code')})")
        else:
            print("⚠️ 未发现商品处理记录，可能任务正在初始化中或 ID 无效。")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    main()
