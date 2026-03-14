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
| 反爬机制 | ✅ | 3次重试+更换指纹机制 (v1.3.2) |
| 关键词搜索 | 🔄 | 反爬增强后待测试 |
| URL 直抓 | 🔄 | 反爬增强后待测试 |
| 图片下载 | ⏳ | 需爬虫成功后测试 |

---

## 待解决问题

### 1688 反爬虫问题（v1.3.2 已改进）

**已添加的改进（v1.3.2）：**
1. ✅ 反爬虫检测：自动识别"系统错误，请稍后重试"等提示
2. ✅ 3次重试机制：检测到反爬后自动更换指纹重试
3. ✅ 随机延迟：模拟人类操作节奏 (1.5-3秒随机)
4. ✅ 浏览器指纹：随机User-Agent、分辨率、时区、语言

**待测试：**
- 运行测试验证改进效果

**如果仍有问题：**
1. 重新运行 `python login_1688.py` 刷新登录状态
2. 添加代理IP支持
3. 等待更长时间后重试

---

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M1 | 最小子模块拆分封装 | ✅ 完成 |
| M2 | API和CLI封装 | ✅ 完成 |
| M3 | 反爬问题解决 | ⏳ 待开始 |
| M4 | 文档完善 | ✅ 完成 |
| M5 | **Ozon API 可靠性增强** | ✅ 完成 (v1.3.1) |

### v1.3.1 更新内容

| 改进项 | 说明 |
|--------|------|
| 重试机制 | tenacity 库，3次+指数退避 (1s→2s→4s) |
| 日志记录 | logging 模块，输出到 logs/ozon_api.log |
| 进度条 | tqdm 库，显示上传进度 |
| 异常处理 | 自定义 OzonApiError 异常 |
| API 凭证 | 已配置客户 Client ID: 4030037 |

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
