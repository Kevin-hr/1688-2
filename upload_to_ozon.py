"""
Ozon 自动化上架执行脚本 (MVP)
----------------------------------
这是一个独立的命令行工具脚本，将采集解析生成的 ozon_export.json 文件一键推送到关联的 Ozon Global 账户的草稿箱或线上库中。

运行前前提：
  需确保当前目录下存在 `.env` 文件，内容类似如下，并不要将此暴露或提交：
    OZON_CLIENT_ID=替换为你的 Client ID
    OZON_API_KEY=替换为你的 API Key

命令行快速用法:
    python upload_to_ozon.py [目标 JSON 文件路径]

默认用法（如果不传路径参数的话，自动寻找采集出的默认 JSON 文件）:
    python upload_to_ozon.py ./1688_products/ozon_export.json
"""

import sys
import os
from src.utils.ozon_api import OzonApiManager

def main():
    """
    脚本入口函数。
    读取系统传入参数或者使用默认路径，然后启动上传动作。
    """
    print("=" * 55)
    print(" 🚀 Ozon Global 自动上架桥接工具 (MVP) v1.0")
    print("=" * 55)
    
    # 步骤 1: 获取要上传的基于 Ozon 标准产生的 JSON 字典文件路径
    # 默认寻找 1688_products 文件夹下面的输出数据
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = os.path.abspath(os.path.join("1688_products", "ozon_export.json"))
        
    print(f"📁 被指定的数据集文件: {json_path}")
    
    # 步骤 2: 实例化 Ozon API 管理器对象
    # 会自动查找系统变量或本地 `.env` 文件获取用户凭信，若缺失抛出提示
    try:
        ozon_manager = OzonApiManager()
    except ValueError as e:
        print(f"❌ 环境或凭据初始化失败: {e}")
        print("💡 💡 请准备一份对应的 `.env` 文件以补充授权！")
        sys.exit(1)
        
    # 步骤 3: 真正的执行上传流水线
    print("⏳ 开始接轨 Ozon Cloud，等待接口回传...")
    task_id = ozon_manager.upload_products(json_path)
    
    # 步骤 4: 回显上传的进程或者错误提醒
    if task_id:
        print(f"🎉 成功！推送任务已启动，Ozon平台正在解析数据流...")
        print(f"   查询追踪的 Task ID 为 = {task_id}")
    else:
        print("⚠️ 发送动作中止，有异常发生！请向上一级检查错误日志输出与接口报错内容。")

if __name__ == "__main__":
    main()
