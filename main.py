import asyncio
import sys
import os
from src.task_router import TaskRouter  # 修复：Python import 不带 .py 后缀

async def main():
    """
    程序主入口，接收用户指令并进行分发。
    """
    if len(sys.argv) < 2:
        print("用法: python main.py \"<指令>\"")
        print("示例: python main.py \"去1688搜索猫咪玩具\"")
        return

    instruction = sys.argv[1]
    print(f"--- 1688 AI 自动化 Agent 已启动 ---")
    print(f"用户指令: {instruction}")
    
    # 初始化任务路由并执行指令
    router = TaskRouter()
    result = await router.route(instruction)
    
    # 处理执行结果
    if result["status"] == "success":
        print("\n--- 任务成功完成 ---")
        print(f"找到商品数量: {result['count']}")
        print(f"数据保存路径: {result['save_path']}")
    else:
        print("\n--- 任务失败 ---")
        print(f"错误信息: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
