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
| **网页抓取** | `src/agents/web_scraper_agent.py` | Playwright 浏览器自动化 | ✅ (带视觉存证) |
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
| 最小子模块 | ✅ | 12个子模块全部测试通过 (v1.3.3) |
| 反爬机制 | ✅ | 3次重试+更换指纹机制 (v1.3.2) |
| 关键词搜索 | ✅ | 已验证：Cookie过期问题已解决 |
| URL 直抓 | ✅ | 已验证：图片94张+属性2项 (v1.3.2) |
| Stealth模式 | ✅ | headless+反检测脚本注入 (v1.3.2) |
| 文件名清洗 | ✅ | 过滤Windows保留名 (v1.3.3) |
| 图片过滤 | ✅ | 自动过滤 SVG/TPS 为主图采集 (v1.3.3) |
| 视觉存证 | ✅ | 抓取时自动生成 proof 截图 (v1.3.3) |
| Ozon 上传 | ✅ | 真实上传验证 Task ID 成功 (v1.3.3) |

---

## 待解决问题

### 1688 登录状态问题（已解决）

**问题原因**：Cookie 过期
**解决方法**：运行 `python login_1688.py` 扫码登录

### Bug 修复（v1.3.3）

| 问题 | 修复 |
|------|------|
| 单位转换 0.5m 返回 0.0 | 添加米(m)单位支持 |
| 文件名 NUL 未过滤 | 添加 Windows 保留名检测 |

### 已知限制

1. **price_rub 需手动换算**：当前仅提供 CNY 原价
2. **商品名翻译**：name 字段为清洗后的中文，建议接入翻译 API

---

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M1 | 最小子模块拆分封装 | ✅ 完成 |
| M2 | API和CLI封装 | ✅ 完成 |
| M5 | **Ozon API 可靠性增强** | ✅ 完成 (v1.3.1) |
| M6 | **Ozon API 真实上架验证 (联调胜利)** | ✅ 完成 (v1.3.3) |

### v1.3.1 更新内容

| 改进项 | 说明 |
|--------|------|
| 重试机制 | tenacity 库，3次+指数退避 (1s→2s→4s) |
| 日志记录 | logging 模块，输出到 logs/ozon_api.log |
| 进度条 | tqdm 库，显示上传进度 |
| 异常处理 | 自定义 OzonApiError 异常 |
| API 凭证 | 已配置客户 Client ID: 4030037 |

### v1.3.3 更新内容 (2026-03-15)

| 核心特性 | 技术细节 |
|----------|----------|
| **API 协议对齐** | 补全必需的 `type_id` 字段，实现 /v3/product/import 成功上传 |
| **图像质量工程** | 增加黑名单 (`.svg`, `.tps`)，提升 Ozon 主图审核通过率 |
| **证据驱动开发** | `scrape_visual_proof.png` 提供真实的采集现场视觉证据 |
| **全链路验证** | `force_audit.py` 成功上传猫玩具，获得 ID `3934075371` |

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
