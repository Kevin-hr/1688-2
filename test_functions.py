"""
功能测试脚本 - 测试 Excel 导出和 Ozon JSON 导出
"""
import sys
import os
import io

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.excel_exporter import ExcelExporter
from src.utils.ozon_transformer import OzonTransformer

# 测试数据
TEST_PRODUCTS = [
    {
        "title": "猫咪静音球不吵人自嗨解闷玩具",
        "price": "¥3.70",
        "url": "https://detail.1688.com/offer/828676752814.html",
        "attributes": {
            "材质": "EVA发泡",
            "颜色": "随机发货",
            "尺寸": "5cm",
            "重量": "50g"
        },
        "images": [
            "https://cbu01.alicdn.com/img/ibank/O1CN01xyz123_!!828676752814.jpg"
        ]
    },
    {
        "title": "逗猫棒羽毛玩具",
        "price": "¥8.50",
        "url": "https://detail.1688.com/offer/123456789.html",
        "attributes": {
            "材质": "羽毛+塑料",
            "颜色": "红色",
            "长度": "30cm"
        },
        "images": []
    }
]

def test_excel_exporter():
    """测试 Excel 导出功能"""
    print("=" * 60)
    print("测试 1: Excel 导出功能")
    print("=" * 60)

    exporter = ExcelExporter(output_dir="1688_products")

    try:
        filepath = exporter.export(TEST_PRODUCTS, filename="测试_商品采集报表.xlsx")
        if filepath and os.path.exists(filepath):
            print(f"✅ Excel 导出成功: {filepath}")
            return True
        else:
            print("❌ Excel 导出失败：文件未生成")
            return False
    except Exception as e:
        print(f"❌ Excel 导出异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ozon_transformer():
    """测试 Ozon JSON 转换功能"""
    print("\n" + "=" * 60)
    print("测试 2: Ozon JSON 转换功能")
    print("=" * 60)

    transformer = OzonTransformer()

    try:
        # 测试单个商品转换
        ozon_product = transformer.map_to_ozon(TEST_PRODUCTS[0])
        print(f"✅ 单个商品转换成功")
        print(f"   offer_id: {ozon_product.get('offer_id')}")
        print(f"   name (俄文): {ozon_product.get('name', '')[:30]}...")
        print(f"   weight_g: {ozon_product.get('weight_g')}")
        print(f"   depth_mm: {ozon_product.get('depth_mm')}")

        # 测试批量转换
        ozon_products = transformer.transform_batch(TEST_PRODUCTS)
        print(f"\n✅ 批量转换成功: {len(ozon_products)} 件商品")

        # 测试 JSON 导出
        json_path = transformer.export_json(ozon_products, output_dir="1688_products")
        if json_path and os.path.exists(json_path):
            print(f"✅ JSON 导出成功: {json_path}")
            return True
        else:
            print("❌ JSON 导出失败：文件未生成")
            return False

    except Exception as e:
        print(f"❌ Ozon 转换异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_manager():
    """测试文件管理器功能"""
    print("\n" + "=" * 60)
    print("测试 3: 文件管理器功能")
    print("=" * 60)

    from src.utils.file_manager import FileManager

    fm = FileManager(base_path="1688_products/test_output")

    try:
        # 测试目录创建
        product_dir, image_dir = fm.create_product_dir("测试商品")
        print(f"✅ 目录创建成功: {product_dir}")

        # 测试文件名清洗
        dirty_name = '测试商品<>:"/\\|*?'
        clean_name = fm.sanitize_filename(dirty_name)
        print(f"✅ 文件名清洗: '{dirty_name}' -> '{clean_name}'")

        # 测试详情保存
        test_details = {
            "title": "测试商品",
            "price": "¥10.00",
            "url": "https://test.com",
            "description": "- **材质**: 塑料\n- **颜色**: 红色"
        }
        fm.save_details(product_dir, test_details)
        print(f"✅ 详情保存成功")

        return True
    except Exception as e:
        print(f"❌ 文件管理器异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("1688-2 项目功能测试")
    print("=" * 60 + "\n")

    results = {}

    # 测试 Excel 导出
    results["Excel导出"] = test_excel_exporter()

    # 测试 Ozon 转换
    results["Ozon转换"] = test_ozon_transformer()

    # 测试文件管理
    results["文件管理"] = test_file_manager()

    # 输出汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("✅ 全部测试通过！" if all_passed else "❌ 存在失败项"))
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
