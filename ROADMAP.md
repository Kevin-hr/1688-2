# 1688-2 项目路线图

> 1688 AI 自动化采集 Agent - Ozon Global 上架工具

## 项目概述

本项目专注于「采集即可上架（Scrape to List）」策略，面向 Ozon Global 跨境电商卖家，提供从 1688 商品采集到 Ozon 标准格式输出的完整自动化流程。

---

## 功能模块清单

| 模块 | 路径 | 功能描述 | 状态 |
|------|------|---------|------|
| **主入口** | `main.py` | 命令行入口，支持关键词搜索/URL直抓两种模式 | ✅ 完成 |
| **任务路由** | `src/task_router.py` | 解析用户输入，调度采集和导出流程 | ✅ 完成 |
| **网页抓取** | `src/agents/web_scraper_agent.py` | Playwright 驱动浏览器，自动登录+搜索+详情抓取 | ✅ 完成 |
| **文件管理** | `src/utils/file_manager.py` | 创建目录结构，保存 Markdown 详情，多线程下载图片 | ✅ 完成 |
| **Ozon 转换** | `src/utils/ozon_transformer.py` | 标题清洗、单位转换、字段映射、翻译、JSON导出 | ✅ 完成 |
| **Excel 导出** | `src/utils/excel_exporter.py` | 格式化 Excel 报表（深蓝表头、斑马纹、自适应列宽） | ✅ 完成 |
| **1688 登录** | `login_1688.py` | 手动扫码登录，持久化 Cookie | ✅ 完成 |
| **统一API** | `src/api.py` | Ali1688API 封装所有功能 | ✅ 完成 |
| **CLI工具** | `cli.py` | 命令行接口 | ✅ 完成 |
| **包初始化** | `src/__init__.py` | 统一导出模块 | ✅ 完成 |

---

## 功能测试结果

| 功能 | 状态 | 说明 |
|------|------|------|
| Excel 导出 | ✅ 通过 | 格式化Excel生成成功 |
| Ozon JSON 转换 | ✅ 通过 | 标题清洗、翻译(中→俄/英)、单位转换正常 |
| 文件管理 | ✅ 通过 | 目录创建、文件名清洗、详情保存正常 |
| 统一API封装 | ✅ 通过 | Ali1688API 类正常工作 |
| CLI工具 | ✅ 通过 | search/scrape/convert/export 命令正常 |
| 关键词搜索 | ❌ 失败 | 1688 反爬虫检测触发，返回"系统错误" |
| URL 直抓 | ❌ 失败 | 同上，需登录后测试 |
| 图片下载 | ⏳ 待爬虫成功后测试 | 历史数据中images目录为空 |

---

## 已封装的功能

### 1. Python API

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

### 2. CLI 命令

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

---

## 待解决问题

### 1688 反爬虫问题

当前关键词搜索和URL直抓均失败，返回"系统错误，请稍后重试"。

**可能原因：**
1. 1688 反爬虫检测触发
2. Cookie 会话过期
3. IP 被临时封禁

**建议解决方案：**
1. 重新运行 `python login_1688.py` 刷新登录状态
2. 添加代理IP支持
3. 增加请求间隔时间
4. 使用更真实的浏览器指纹

---

## 阶段完成情况

### Phase 1: 功能排查与测试
- [x] Excel 导出测试
- [x] Ozon JSON 转换测试
- [x] 文件管理功能测试
- [x] API 封装测试
- [x] CLI 工具测试
- [x] 关键词搜索测试（发现反爬问题）
- [ ] URL 直抓测试（需登录）
- [ ] 图片下载测试（需爬虫成功）

### Phase 2: 封装与优化
- [x] 统一 API 封装 (src/api.py)
- [x] CLI 工具封装 (cli.py)
- [x] 模块统一导出 (src/__init__.py)
- [ ] 添加单元测试
- [ ] 优化代码结构
- [ ] 增加错误处理

### Phase 3: 文档完善
- [x] 更新 README.md（添加API和CLI使用说明）
- [ ] 详细 API 文档
- [ ] 使用教程

---

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M1 | 所有功能排查测试完成 | 🔄 85% |
| M2 | 反爬问题解决 | ⏳ 待开始 |
| M3 | 模块封装完成 | ✅ 完成 |
| M4 | 文档完善完成 | 🔄 进行中 |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 爬虫 | Playwright |
| 数据处理 | pandas, openpyxl |
| 翻译 | translators |
| 异步 | asyncio |
| 持久化 | JSON, Excel |

---

## 相关文档

- `README.md` - 项目完整文档
- `PROJECT_REVIEW.md` - 专业阶段项目回顾
- `docs/MVP_DELIVERY_PLAN.md` - MVP 交付计划
