# 1688 AI 自动化采集 Agent

> 高效的 1688.com 电商自动化商品检索、数据采集与 **Ozon Global 上架** 工具，由 OpenClaw LLM 驱动。

## 简介 (Introduction)

本工具专为「**采集即可上架（Scrape to List）**」策略而设计，面向 **Ozon Global** 跨境电商卖家。  
它能够自动登录（持久化会话）、关键词搜索或单品直抓、解析商品详细属性与规格，下载高质量图片，并输出两种格式的标准化数据：
- 📊 **Excel 采购报表**（格式化，可直接用于内部采购对账）  
- 🛒 **Ozon 标准 JSON**（字段已自动清洗映射，可接 ERP 或直接导入 Ozon）

## 核心特性 (Features)

- 🤖 **双模式采集**：`--keyword` 批量搜索 / `--url` 单品精准直抓
- 🔍 **多选择器回退**：适应 1688 频繁变化的 DOM 结构，提高抓取成功率
- 🛒 **Ozon 字段映射** (`OzonTransformer`)：
  - 自动清洗标题中的 1688 营销垃圾词（爆款/一件代发/包邮等）
  - 自动单位换算：**CM → MM**，**KG → G**（Ozon 物流计算标准）
  - 自动推断 Ozon 品类（宠物/玩具/电子等）
  - 输出结构化 `ozon_export.json`
- 📊 **格式化 Excel 报表**：深蓝表头、斑马纹、自适应列宽、冻结首行
- 🛡️ **反检测登录**：Playwright 持久化 Cookie，无需重复扫码

## 安装与配置 (Installation)

```bash
git clone https://github.com/Kevin-hr/1688-2.git
cd 1688-2
pip install -r requirements.txt
playwright install chromium

# 首次登录（手动扫码，Cookie 自动持久化）
python login_1688.py
```

## 快速使用 (Quick Start)

```bash
# 批量关键词搜索（采集5件商品）
python main.py --keyword "猫玩具" --limit 5
python main.py -k "猫咪玩具" -n 3

# 单品 URL 直抓（精准采集指定商品）
python main.py --url "https://detail.1688.com/offer/566971549514.html"
python main.py -u "https://detail.1688.com/offer/566971549514.html"

# 旧版指令模式（向后兼容）
python main.py "去1688搜索猫咪玩具"
```

## 数据输出格式 (Output)

每次采集后，在 `1688_products/` 目录生成以下文件：

```text
1688_products/
├── 商品名A/
│   ├── detail.md              # Markdown 详情报告
│   └── images/                # 商品图片（最多5张）
├── 商品名B/
│   ├── detail.md
│   └── images/
├── 1688_猫玩具_商品采集报表.xlsx  # 格式化 Excel 报表（采购用）
└── ozon_export.json           # ✨ Ozon Global 标准上架 JSON
```

### `ozon_export.json` 样例字段

```json
{
  "offer_id": "1688-828676752814",
  "name": "猫咪静音球不吵人自嗨解闷玩具",
  "name_raw_1688": "超耐咬爆款猫咪静音球...一件代发批发包邮",
  "price_cny": 3.7,
  "price_rub": "⚠️ 需手动换算（CNY × 当日汇率）",
  "weight_g": 50.0,
  "depth_mm": 50.0,
  "width_mm": 50.0,
  "height_mm": 50.0,
  "suggested_ozon_category": "Pet Supplies / Cat Toys",
  "images": ["..."],
  "attributes_mapped": { "material": "EVA发泡", "color": "随机发货" },
  "source_url_1688": "https://detail.1688.com/offer/828676752814.html",
  "vat": "0.20"
}
```

## 版本历史 (Changelog)

| 版本 | 日期 | 主要功能 |
|------|------|---------|
| v1.0.0 | 2026-03 | 基础搜索 + 图片下载 + Markdown 报告 |
| v1.1.0 | 2026-03-10 | Excel 格式化导出 + 样例生成脚本 |
| v1.2.0 | 2026-03-10 | **OzonTransformer（标题清洗/单位转换/字段映射）+ 双模式参数 + ozon_export.json** |

## 注意事项 (Notes)

1. **price_rub 字段需人工换算**：当前仅提供 CNY 原价，上架前请乘以当日 CNY/RUB 汇率。
2. **商品名翻译**：`name` 字段为清洗后的中文标题，Ozon 真正要求俄文/英文，建议接入翻译 API。
3. **反爬维护**：1688 DOM 可能随时变化，`query_selector` 需定期检查更新。
4. **频率限制**：单次建议采集不超过 10 件，避免高频访问被封号。
