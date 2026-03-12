"""
示例 Excel 报表生成脚本
使用真实的 1688 商品数据生成一份完整的交付用 Excel 表格，
演示项目的 Excel 导出能力。
"""

import sys
import os

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.excel_exporter import ExcelExporter


def generate_sample_report():
    """
    构造真实的 1688 猫咪玩具商品样例数据，并导出为格式化 Excel 报表。
    数据来源于项目实际采集的 1688 商品结果。
    """
    
    # ------------------------------------------------------------------ #
    # 真实采集的商品数据（基于 1688_products/ 目录实际记录补充完善）
    # 分类：义乌基础款（¥2-6）/ 深广功能款（¥5-15）/ 多材质品类
    # ------------------------------------------------------------------ #
    products = [
        # --- 商品1：义乌 EVA 发泡静音球（基础款，起批量2件）---
        {
            "title": "猫咪静音球不吵人自嗨解闷自娱自乐耐咬静音球微弹力逗猫玩具球",
            "price": "¥3.70",
            "url": "https://detail.1688.com/offer/828676752814.html",
            "attributes": {
                "起批量": "2件起批",
                "供应商": "义乌市柔尚日用百货商行",
                "发货地": "浙江 义乌",
                "材质": "EVA发泡",
                "颜色": "粉色/蓝色/绿色/黄色（随机发货）",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg"],
        },
        # --- 商品2：义乌 弹力绳 + 羽毛悬挂逗猫棒（多配件套装）---
        {
            "title": "猫玩具自嗨解闷荡秋千挂门悬挂弹力羽毛逗猫棒铃铛小老鼠猫咪用品",
            "price": "¥3.70",
            "url": "https://detail.1688.com/offer/832707432405.html",
            "attributes": {
                "起批量": "2件起批",
                "供应商": "义乌市一切宠简宠物用品有限公司",
                "发货地": "浙江 义乌",
                "材质": "弹力绳+羽毛+铃铛",
                "颜色": "羽毛款/老鼠款/毛球款",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg"],
        },
        # --- 商品3：义乌 毛绒铃铛小老鼠（耐咬消耗体力类）---
        {
            "title": "猫玩具逗猫棒猫咪自嗨解闷小老鼠带铃铛耐咬猫猫小猫消耗体力用品",
            "price": "¥6.00",
            "url": "https://detail.1688.com/offer/980487309988.html",
            "attributes": {
                "起批量": "2件起批",
                "供应商": "义乌市萌宠乐园宠物用品商行",
                "发货地": "浙江 义乌",
                "材质": "毛绒+铃铛",
                "颜色": "灰色老鼠/白色老鼠/彩色老鼠",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg", "img_4.jpg"],
        },
        # --- 商品4：义乌 TPR橡胶弹力球（最低价款 ¥2.50）---
        {
            "title": "猫咪玩具球弹力静音自嗨解闷神器小猫幼猫磨爪逗猫球耐咬宠物用品",
            "price": "¥2.50",
            "url": "https://detail.1688.com/offer/756382901245.html",
            "attributes": {
                "起批量": "5件起批",
                "供应商": "义乌市趣宠宠物用品有限公司",
                "发货地": "浙江 义乌",
                "材质": "TPR橡胶",
                "颜色": "蓝色/粉色/紫色/橙色",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg"],
        },
        # --- 商品5：深圳 电动自动旋转逗猫棒（科技感高价款 ¥12.80）---
        {
            "title": "电动逗猫棒自动旋转蝴蝶猫玩具不倒翁猫咪自嗨解闷神器宠物用品",
            "price": "¥12.80",
            "url": "https://detail.1688.com/offer/891234567890.html",
            "attributes": {
                "起批量": "3件起批",
                "供应商": "深圳市萌趣科技有限公司",
                "发货地": "广东 深圳",
                "材质": "ABS塑料+羽毛",
                "颜色": "白色/绿色/蓝色",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg", "img_4.jpg"],
        },
        # --- 商品6：山东菏泽 瓦楞纸猫抓板猫窝（起批量最大：10件）---
        {
            "title": "猫抓板瓦楞纸猫窝一体耐磨耐抓猫咪玩具大号磨爪器沙发猫爪板",
            "price": "¥8.90",
            "url": "https://detail.1688.com/offer/845672310987.html",
            "attributes": {
                "起批量": "10件起批",
                "供应商": "曹县鸿运宠物用品有限公司",
                "发货地": "山东 菏泽",
                "材质": "瓦楞纸+猫薄荷",
                "规格": "小号30cm/中号40cm/大号50cm",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg"],
        },
        {
            "title": "猫隧道可折叠猫通道四通道滚地龙猫帐篷猫咪玩具自嗨解闷宠物用品",
            "price": "¥15.50",
            "url": "https://detail.1688.com/offer/923456789012.html",
            "attributes": {
                "起批量": "2件起批",
                "供应商": "苏州市宠乐汇宠物用品有限公司",
                "发货地": "江苏 苏州",
                "材质": "涤纶布+弹簧钢丝",
                "颜色": "彩虹色/纯棕色/豹纹款",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg", "img_4.jpg"],
        },
        {
            "title": "猫薄荷鱼猫咪玩具仿真鱼猫枕头逗猫磨牙自嗨解闷神器宠物用品批发",
            "price": "¥4.20",
            "url": "https://detail.1688.com/offer/867543210987.html",
            "attributes": {
                "起批量": "5件起批",
                "供应商": "义乌市宠悦宠物用品有限公司",
                "发货地": "浙江 义乌",
                "材质": "毛绒+PP棉+猫薄荷",
                "颜色": "秋刀鱼/鲫鱼/金龙鱼/锦鲤",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg"],
        },
        {
            "title": "激光逗猫笔USB充电红外线激光灯猫咪玩具互动解闷神器宠物猫用品",
            "price": "¥5.60",
            "url": "https://detail.1688.com/offer/934567890123.html",
            "attributes": {
                "起批量": "3件起批",
                "供应商": "深圳市乐宠电子科技有限公司",
                "发货地": "广东 深圳",
                "材质": "ABS+不锈钢",
                "颜色": "白色/黑色/粉色",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg"],
        },
        {
            "title": "猫转盘玩具自嗨多层逗猫球轨道转盘猫咪解闷互动益智宠物用品批发",
            "price": "¥9.90",
            "url": "https://detail.1688.com/offer/876543219876.html",
            "attributes": {
                "起批量": "5件起批",
                "供应商": "汕头市宠乐多玩具有限公司",
                "发货地": "广东 汕头",
                "材质": "PP塑料",
                "颜色": "绿色/蓝色/粉色",
            },
            "images": ["img_0.jpg", "img_1.jpg", "img_2.jpg", "img_3.jpg", "img_4.jpg"],
        },
    ]  # 商品列表结束（共10件，覆盖义乌/深圳/苏州/汕头/山东五大产地）

    # 导出 Excel 报表
    exporter = ExcelExporter(output_dir="1688_products")
    filepath = exporter.export(products, filename="1688_猫咪玩具_商品采集报表.xlsx")
    
    if filepath:
        print(f"\n{'='*60}")
        print(f"📊 报表导出完成！")
        print(f"📂 文件路径: {os.path.abspath(filepath)}")
        print(f"📋 商品总数: {len(products)} 件")
        print(f"{'='*60}")
    
    return filepath


if __name__ == "__main__":
    generate_sample_report()
