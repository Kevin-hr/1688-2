# 项目进度与任务追踪 (Task Board)

## 当前版本: v1.2.0

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

### 🏃 进行中 (In Progress)
- [ ] 优化 `WebScraperAgent`：将搜索与抓取操作重构为**单一 Playwright Session**，提升效率
- [ ] 定期维护 1688 DOM 元素的 CSS 映射关系（属性抓取为空的根因）

### 📅 计划中 (To-Do)
- [ ] 消除硬编码的 `asyncio.sleep`，引入智能 `wait_for_selector` 判断
- [ ] 引入 `FileManager` 的图片**多线程下载**及重试容错机制
- [ ] `OzonTransformer` 接入翻译 API（中文标题 → 俄文/英文，Ozon 真正要求的语言）
- [ ] 对接 Ozon Seller API，实现 JSON → 直接上架自动化（终极目标）
