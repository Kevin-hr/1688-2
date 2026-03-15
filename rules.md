# 项目开发规范 (Project Rules)

## 注释与文档 (Comments & Documentation)
- **强制中文注释**：所有代码文件（Python, JavaScript 等）必须包含详细的中文注释。
- **文档语言**：所有项目文档（README, PRD, 任务单等）应优先使用中文编写，或提供中文版本。
- **代码结构**：逻辑复杂的函数必须在函数头部添加中文说明。

## 开发流程 (Development Workflow)
- **任务驱动**：使用 `task.md` 跟踪进度。
- **验证优先**：每次重大修改后必须运行验证脚本。

## 🤖 多 Agent 协作规范 (Multi-Agent Protocol)
- **禁止并发写**：严禁多个 Agent 同时修改同一个文件。必须在 `task.md` 中标明“由 [Agent ID/Role] 领用”。
- **先读后写**：修改前必须 `view_file` 确认最新代码，防止覆盖他人提交。
- **提交规范**：每次代码修改需对应更新 `task.md` 中的「已完成」项。
- **冲突仲裁**：若发现代码逻辑冲突，以 `PROJECT_REVIEW.md` 中的“架构决策”为最高准则。
