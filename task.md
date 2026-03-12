# 项目进度与任务追踪 (Task Board)

## 当前版本: v1.3.0

### 🟢 已完成 (Done)
- [x] (Day 1) 修复 `main.py` L4 致命的 from import 语法崩溃 Bug
- [x] (Day 1) 修复 `web_scraper_agent.py` 错误的 query_selector 传参机制 Bug
- [x] (Day 1) 修改 `file_manager.py` 使导出的 `.md` 使用全中文字段
- [x] (Day 3) 创建项目文档规范说明书与 README.md 简介
- [x] (Day 3) 添加 `.gitignore` 并发布到 GitHub Release v1.0.0
- [x] (Day 5) ✅ 新增 `ExcelExporter` 模块（格式化 xlsx，深蓝表头/斑马纹/冻结行）
- [x] (Day 5) ✅ 将 Excel 导出集成至 `TaskRouter` 工作流
- [x] (Day 5) ✅ 录制完整项目演示视频（动画 WebP → MP4 转换）
- [x] (Day 5) ✅ 发布 GitHub Release v1.1.0
- [x] (Day 7) ✅ **新增 `OzonTransformer` 模块** — 标题清洗 + 单位转换 + Ozon 字段映射
- [x] (Day 7) ✅ **输出 `ozon_export.json`** — Ozon Global 标准上架 JSON
- [x] (Day 7) ✅ **升级 `main.py`** — 支持 `--keyword/-k`, `--url/-u`, `--limit/-n` 参数
- [x] (Day 7) ✅ **新增 `route_url()` 方法** — 单品 URL 直抓模式
- [x] (Day 7) ✅ **重构 `_export_results()`** — 双格式导出（Excel + Ozon JSON）
- [x] (Day 9) ✅ **重构 `WebScraperAgent` 为单一 Playwright Session** — 搜索+详情复用同一浏览器，消除多次启停开销
- [x] (Day 9) ✅ **消除硬编码 `asyncio.sleep`** — 替换为智能 `wait_for_selector` 多选择器竞速策略
- [x] (Day 9) ✅ **更新 CSS 选择器映射** — 适配 2025/2026 版 1688 DOM 结构，新增 `.mojar-element-card` 等选择器
- [x] (Day 9) ✅ **引入图片多线程下载** — `FileManager` 使用 `ThreadPoolExecutor` 并行下载 + 指数退避重试（最多3次）
- [x] (Day 9) ✅ **`OzonTransformer` 接入翻译 API** — 中文标题自动翻译俄文/英文（Google/Bing/Baidu 三引擎回退）

### 🏃 进行中 (In Progress)
- [ ] 持续维护 1688 DOM 选择器映射（版本变化时需手动更新选择器列表）

### 📅 计划中 (To-Do)
- [x] 对接 Ozon Seller API，实现 JSON → 直接上架自动化（终极目标，需 API Key）
