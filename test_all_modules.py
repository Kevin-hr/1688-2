# -*- coding: utf-8 -*-
"""
1688 采集工具 - 测试脚本
用于验证所有模块是否正常工作
"""

import asyncio
import sys
import os

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.task_router import TaskRouter
from src.utils.ozon_transformer import OzonTransformer
from src.utils.excel_exporter import ExcelExporter
from src.modules.translator import Translator


async def test_scraper():
    """测试采集功能"""
    print("\n" + "="*50)
    print("测试1: URL采集模式")
    print("="*50)

    router = TaskRouter()
    test_url = "https://detail.1688.com/offer/566971549514.html"

    try:
        result = await router.route_url(test_url)
        print(f"状态: {result.get('status')}")
        print(f"数量: {result.get('count', 0)}")
        print(f"Excel: {result.get('excel_path', 'N/A')}")
        print(f"Ozon: {result.get('ozon_json_path', 'N/A')}")
        return result.get('status') == 'success'
    except Exception as e:
        print(f"❌ 采集失败: {e}")
        return False


def test_transformer():
    """测试Ozon转换"""
    print("\n" + "="*50)
    print("测试2: Ozon转换")
    print("="*50)

    # 模拟商品数据
    test_products = [
        {
            "title": "测试商品",
            "price": "99.00",
            "url": "https://detail.1688.com/test.html",
            "attributes": {"颜色": "红色", "尺寸": "大"},
            "images": ["https://test.com/img1.jpg"]
        }
    ]

    try:
        transformer = OzonTransformer()
        ozon_products = transformer.transform_batch(test_products)
        print(f"转换成功: {len(ozon_products)} 个商品")

        # 保存测试
        json_path = transformer.export_json(ozon_products)
        print(f"JSON保存: {json_path}")
        return True
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False


def test_excel():
    """测试Excel导出"""
    print("\n" + "="*50)
    print("测试3: Excel导出")
    print("="*50)

    test_products = [
        {
            "title": "测试商品1",
            "price": "99.00",
            "url": "https://detail.1688.com/test1.html",
            "attributes": {"颜色": "红色"},
        },
        {
            "title": "测试商品2",
            "price": "199.00",
            "url": "https://detail.1688.com/test2.html",
            "attributes": {"颜色": "蓝色"},
        }
    ]

    try:
        exporter = ExcelExporter()
        path = exporter.export(test_products, "test_report.xlsx")
        print(f"Excel保存: {path}")
        return True
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        return False


def test_translator():
    """测试翻译功能"""
    print("\n" + "="*50)
    print("测试4: 翻译功能")
    print("="*50)

    try:
        translator = Translator()
        if not translator._available:
            print("⚠️ translators库未安装，跳过翻译测试")
            return True

        result_ru = translator.translate_to_ru("猫咪玩具")
        result_en = translator.translate_to_en("猫咪玩具")
        print(f"中→俄: 猫咪玩具 → {result_ru}")
        print(f"中→英: 猫咪玩具 → {result_en}")
        return True
    except Exception as e:
        print(f"❌ 翻译失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("="*50)
    print("1688 采集工具 - 功能测试")
    print("="*50)

    results = {
        "Ozon转换": test_transformer(),
        "Excel导出": test_excel(),
        "翻译功能": test_translator(),
        "URL采集": await test_scraper(),
    }

    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    for name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有测试通过!")
    else:
        print("⚠️ 部分测试失败，请检查")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
