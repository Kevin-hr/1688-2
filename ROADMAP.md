# 1688-2 项目路线图

> 1688 AI 自动化采集 Agent - Ozon Global 上架工具

## 项目概述

本项目专注于「采集即可上架（Scrape to List）」策略，面向 Ozon Global 跨境电商卖家，提供从 1688 商品采集到 Ozon 标准格式输出的完整自动化流程。

---

## 功能模块清单

| 模块 | 路径 | 功能描述 | 状态 |
|------|------|---------|------|
| **主入口** | `main.py` | 命令行入口 | ✅ |
| **CLI工具** | `cli.py` | 命令行接口 | ✅ |
| **统一API** | `src/api.py` | Ali1688API 封装 | ✅ |
| **任务路由** | `src/task_router.py` | 解析输入，调度流程 | ✅ |
| **网页抓取** | `src/agents/web_scraper_agent.py` | Playwright 浏览器自动化 | ⚠️ 反爬问题 |
| **文件管理** | `src/utils/file_manager.py` | 目录结构，图片下载 | ✅ |
| **Ozon 转换** | `src/utils/ozon_transformer.py` | 标题清洗、单位转换、翻译、JSON导出 | ✅ |
| **Excel 导出** | `src/utils/excel_exporter.py` | 格式化报表 | ✅ |
| **1688 登录** | `login_1688.py` | 手动扫码登录 | ✅ |

---

## 最小子模块 (`src/modules/`)

每个子模块独立封装，可单独使用：

| # | 模块 | 功能 | 状态 |
|---|------|------|------|
| 1 | `filename_sanitizer.py` | 文件名清洗 | ✅ |
| 2 | `title_cleaner.py` | 标题清洗(去除营销词) | ✅ |
| 3 | `unit_converter.py` | 单位转换(CM→MM, KG→G) | ✅ |
| 4 | `translator.py` | 翻译(中→俄/英) | ✅ |
| 5 | `price_calculator.py` | Ozon价格计算 | ✅ |
| 6 | `image_downloader.py` | 图片下载(多线程+重试) | ✅ |
| 7 | `field_mapper.py` | 字段映射 | ✅ |
| 8 | `dir_creator.py` | 目录创建 | ✅ |
| 9 | `detail_saver.py` | 详情保存(Markdown) | ✅ |
| 10 | `excel_styler.py` | Excel样式 | ✅ |

---

## 功能测试结果

| 功能 | 状态 | 说明 |
|------|------|------|
| Excel 导出 | ✅ | 格式化Excel生成成功 |
| Ozon JSON 转换 | ✅ | 标题清洗、翻译(中→俄/英)、单位转换正常 |
| 文件管理 | ✅ | 目录创建、文件名清洗、详情保存正常 |
| 统一API封装 | ✅ | Ali1688API 类正常工作 |
| CLI工具 | ✅ | search/scrape/convert/export 命令正常 |
| 最小子模块 | ✅ | 10个子模块全部测试通过 |
| 关键词搜索 | ❌ | 1688 反爬虫检测触发 |
| URL 直抓 | ❌ | 同上 |
| 图片下载 | ⏳ | 需爬虫成功后测试 |

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

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M1 | 最小子模块拆分封装 | ✅ 完成 |
| M2 | API和CLI封装 | ✅ 完成 |
| M3 | 反爬问题解决 | ⏳ 待开始 |
| M4 | 文档完善 | 🔄 进行中 |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 爬虫 | Playwright |
| 数据处理 | pandas, openpyxl |
| 翻译 | translators |
| 异步 | asyncio |

---

## 相关文档

- `README.md` - 项目完整文档
- `PROJECT_REVIEW.md` - 专业阶段项目回顾
