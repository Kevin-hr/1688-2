# Tasks

- [ ] Task 1: 创建 AI 导航器组件 (AI Navigator)
  - [ ] SubTask 1.1: 创建 `src/agents/components/ai_navigator.py`。
  - [ ] SubTask 1.2: 实现 `solve_captcha(page)` 接口 (Mock 实现，预留 VLM 调用位置)。
  - [ ] SubTask 1.3: 实现拟人化鼠标轨迹生成算法 `human_mouse_move(start, end)`。

- [ ] Task 2: 升级 WebScraperAgent 支持混合模式
  - [ ] SubTask 2.1: 在 `WebScraperAgent` 中初始化 `AINavigator`。
  - [ ] SubTask 2.2: 在 `scrape_product_detail` 中增加反爬检测逻辑 (检测 "验证码"、"滑块")。
  - [ ] SubTask 2.3: 实现从 RPA 模式到 AI 模式的自动切换 (Failover 机制)。

- [ ] Task 3: 增强 Extractor 的容错性
  - [ ] SubTask 3.1: 优化 `Extractor`，允许接收 AI 提供的结构化文本（如 LLM 从截图解析的 JSON）。

# Task Dependencies
- Task 2 依赖 Task 1。
- Task 3 可并行开发。
