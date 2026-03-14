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
- ⚡ **API 可靠性** (v1.3.1+)：
  - 3次重试 + 指数退避
  - 日志记录 (`logs/ozon_api.log`)
  - 进度条显示

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
| v1.3.0 | 2026-03-14 | **统一API封装** + MCP服务器支持 + 模块化重构 |
| v1.3.1 | 2026-03-14 | **Ozon API 改进**：添加重试机制(3次+指数退避)、日志记录(logs/ozon_api.log)、进度条、异常抛出 |
| v1.3.2 | 2026-03-14 | **反爬机制增强**：添加反爬虫检测、3次重试+更换指纹机制、随机延迟优化 |

## API 使用 (Python)

### 方式一：统一 API (推荐)

```python
from src import Ali1688API

api = Ali1688API()

# 关键词搜索
result = await api.search("猫玩具", limit=5)

# URL 直抓
result = await api.scrape_url("https://detail.1688.com/offer/xxx.html")

# 导出 Excel
excel_path = api.export_excel(products, "output.xlsx")

# 转换为 Ozon 格式
ozon_products = api.to_ozon(products)
```

### 方式二：便捷函数

```python
from src import search, scrape_url, export_excel, to_ozon

# 直接调用
result = await search("猫玩具", limit=3)
ozon = to_ozon(products)
```

## CLI 使用

```bash
# 关键词搜索
python cli.py search -k "猫玩具" -n 5

# URL 直抓
python cli.py scrape -u "https://detail.1688.com/offer/xxx.html"

# 转换为 Ozon 格式
python cli.py convert -i input.json -o ozon_export.json

# 导出为 Excel
python cli.py export -i input.json -o output.xlsx
```

## MCP 服务器 (v1.4.0 新增)

项目提供 MCP 服务器，可集成到 Claude Code 等 AI 工具中使用。

### 启动 MCP 服务器

```bash
# 安装依赖
pip install fastmcp

# 启动服务器（stdio 模式）
python mcp_server.py
```

### MCP 工具列表

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `search_1688` | 关键词搜索采集 | keyword, limit |
| `scrape_1688_url` | URL 单品采集 | url |
| `transform_1688_to_ozon` | 转换为 Ozon 格式 | products_json |
| `export_1688_to_excel` | 导出 Excel | products_json, filename |
| `upload_ozon` | 上传到 Ozon | json_path |
| `list_ozon_products` | 获取商品列表 | - |
| `get采集状态` | 获取采集状态 | - |

### 注册到 Claude Code

在 `~/.claude/mcp.json` 中添加：

```json
{
  "1688-scraper": {
    "command": "python",
    "args": ["C:/Users/52648/Documents/GitHub/1688-2/mcp_server.py"]
  }
}
```

## 模块列表

| 模块 | 路径 | 功能 |
|------|------|------|
| `Ali1688API` | `src/api.py` | 统一 API 封装 |
| `TaskRouter` | `src/task_router.py` | 任务路由 |
| `WebScraperAgent` | `src/agents/web_scraper_agent.py` | 网页抓取 |
| `ExcelExporter` | `src/utils/excel_exporter.py` | Excel 导出 |
| `OzonTransformer` | `src/utils/ozon_transformer.py` | Ozon 转换 |
| `OzonApiManager` | `src/utils/ozon_api.py` | Ozon API 上传 |
| `FileManager` | `src/utils/file_manager.py` | 文件管理 |

### 最小子模块 (`src/modules/`)

每个子模块都可单独导入使用：

```python
from src.modules import (
    # 标题清洗
    clean_title,
    # 翻译
    translate_to_ru, translate_to_en,
    # 单位转换
    convert_weight, convert_dimension,
    # 价格计算
    calculate_price,
    # 字段映射
    map_attributes, infer_category,
    # 图片下载
    download_images,
    # 目录和文件
    create_product_dir, save_details,
    # 文件名清洗
    sanitize,
)

# 清洗标题（去除营销词）
title = clean_title("超耐咬爆款猫咪玩具一件代发包邮")

# 翻译为俄文
ru_name = translate_to_ru(title)

# 翻译为英文
en_name = translate_to_en(title)

# 单位转换
weight_g = convert_weight("500g")      # 500.0
dimension_mm = convert_dimension("10cm") # 100.0

# 计算 Ozon 售价
price_rub = calculate_price(10.0, 500)  # 10元, 500g

# 字段映射
mapped, unmapped = map_attributes({"材质": "塑料", "颜色": "红色"})

# 推断品类
category = infer_category("猫咪静音球玩具")

# 下载图片
download_images(urls, "images/")

# 创建目录
product_dir, image_dir = create_product_dir("商品名称")

# 保存详情
save_details(product_dir, details)
```

| 子模块 | 功能 |
|--------|------|
| `FilenameSanitizer` | 文件名清洗 |
| `TitleCleaner` | 标题清洗（去除营销词） |
| `UnitConverter` | 单位转换（CM→MM, KG→G） |
| `Translator` | 多引擎翻译（中→俄/英） |
| `PriceCalculator` | Ozon 价格计算 |
| `ImageDownloader` | 图片下载（多线程+重试） |
| `FieldMapper` | 字段映射 |
| `CategoryMapper` | 品类推断 |
| `DirCreator` | 目录创建 |
| `DetailSaver` | 详情保存（Markdown） |
| `ExcelStyler` | Excel 样式 |

## Ozon API 配置

### 配置凭证

在项目根目录创建或编辑 `.env` 文件：

```bash
# .env 文件
OZON_CLIENT_ID=你的ClientID
OZON_API_KEY=你的API密钥
```

**获取方式**：
1. 登录 [Ozon Seller](https://seller.ozon.ru)
2. 进入"设置" → "API密钥"
3. 创建/复制 Client ID 和 API Key

### 上传到 Ozon

```bash
# 方式一：直接上传（使用已采集的 ozon_export.json）
python upload_to_ozon.py

# 方式二：指定文件路径
python upload_to_ozon.py 1688_products/ozon_export.json

# 方式三：全自动采集+上传
python auto_publish.py -q "猫玩具" -p 1000 -c 17027484
```

## 日志文件

v1.3.1+ 版本自动记录 API 调用日志：

```bash
# 查看日志
type logs\ozon_api.log

# 或实时查看
tail -f logs/ozon_api.log
```

**日志内容**：
- API 请求/响应
- 上传结果
- 错误信息
- 重试记录

## 注意事项 (Notes)

1. **price_rub 字段需人工换算**：当前仅提供 CNY 原价，上架前请乘以当日 CNY/RUB 汇率。
2. **商品名翻译**：`name` 字段为清洗后的中文标题，Ozon 真正要求俄文/英文，建议接入翻译 API。
3. **反爬维护**：1688 DOM 可能随时变化，`query_selector` 需定期检查更新。
4. **频率限制**：单次建议采集不超过 10 件，避免高频访问被封号。
5. **API 重试**：v1.3.1+ 版本内置 3 次重试（指数退避），网络不稳定时会自动重试。
