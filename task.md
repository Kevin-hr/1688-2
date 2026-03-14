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
- [x] (Day 9) ✅ **更新 CSS 选择器映射** — 适配 2025/2026 版 1688 DOM 结构
- [x] (Day 9) ✅ **引入图片多线程下载** — `FileManager` 并行化
- [x] (Day 9) ✅ **`OzonTransformer` 接入翻译 API** — 中俄外语翻译（Google/Bing/Baidu）
- [x] (Day 11) ✅ **新建 `selector_test.py` 稳定性探测工具**
- [x] (Day 11) ✅ **完成项目进度审计与 v1.4.0 并行开发路线规划**

### 开发流程 (Development Workflow)
- **任务驱动**：使用 `task.md` 跟踪进度。
- **验证优先**：每次重大修改后必须运行验证脚本。

## 多 Agent 协作规范 (Multi-Agent Collaboration)
- **加锁机制**：在开始任何修改前，必须先 `view_file` 读取 `task.md` 的最新状态。
- **原子任务**：严禁多个 Agent 同时修改同一个 `.py` 文件。若需修改，必须先在 `task.md` 的「进行中」领任务。
- **状态同步**：任务完成后，立即更新 `task.md` 并写清楚修改了哪些行/函数。
- **决策记录**：重大架构调整（如 API 结构变化）必须在 `PROJECT_REVIEW.md` 的“架构决策日志”中记录。

### 🏃 进行中 (In Progress)
- [ ] **路径 A**：修复 `selector_test.py` 逻辑并完成 1688 全局探测 (由 Agent-QA 领用)
- [ ] **路径 B**：完善 `OzonTransformer` 中的 Ozon Attribute ID 映射，特别是 Brand/Color 字段 (由 Agent-Dev 领用)
- [ ] **路径 D**：建立多 Agent 协作审计日志，防止冲突 (由 PM Agent 领用)

### 📅 计划中 (To-Do)
- [ ] 对接 Ozon Seller API，实现 JSON → 直接上架自动化（需 API Key 验证联通性）
- [ ] 引入 `src/agents/web_scraper_agent.py` 的微重构成单一职能类
