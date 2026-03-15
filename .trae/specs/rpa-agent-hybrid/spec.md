# RPA + AI Agent 混合架构优化 Spec

## Why
当前的 1688 自动化方案主要依赖传统的 RPA (Playwright)，在面对复杂的滑动验证码 (x82y) 和动态 DOM 结构变化时显得脆弱。
虽然引入了 CDP 反检测，但在需要“像人一样思考和操作”的场景（如登录验证、异常处理）下，仍需 AI Agent 的介入。
混合架构结合了 RPA 的**高效率**与 AI Agent 的**高智能**，是解决 1688 风控的最佳实践。

## What Changes
- **引入 Browser-use 思想**: 在 `src/agents/components/` 中新增 `ai_navigator.py`，作为 Playwright 的增强层。
- **混合驱动模式**:
    - **Fast Mode (RPA)**: 对于常规页面加载和数据提取，继续使用高效的 Playwright + CDP。
    - **Smart Mode (Agent)**: 当检测到验证码、登录墙或 DOM 解析失败时，自动切换到 AI 驱动模式，调用 VLM (如 GPT-4o-V/Claude-3.5-Computer-Use) 进行视觉理解和操作。
- **依赖更新**: 需要引入 `langchain` 或 `browser-use` 相关库（本项目暂通过模拟接口实现，避免引入过重依赖）。

## Impact
- **Affected Specs**: `src/agents/web_scraper_agent.py`, `src/agents/components/navigator.py`
- **New Components**: `src/agents/components/ai_navigator.py`

## ADDED Requirements
### Requirement: AI 辅助导航
当 RPA 导航遇到阻碍（如页面包含 "滑块"、"验证" 关键词）时，系统 SHALL 能够调用 AI Agent 接口尝试解决。

#### Scenario: 滑块验证
- **WHEN** 页面出现滑块验证码
- **THEN** `WebScraperAgent` 捕获特征，暂停 RPA 流程
- **AND** 切换至 `AINavigator`，截图发送给 VLM，获取滑块缺口坐标
- **AND** 生成拟人化轨迹完成拖拽

## MODIFIED Requirements
### Requirement: 混合解析策略增强
`Extractor` SHALL 支持从 AI 视觉分析结果中提取数据（作为 JSON 和 DOM 均失败后的 T2 级兜底）。

## Architecture Diagram
```mermaid
graph TD
    User[用户指令] --> Router[TaskRouter]
    Router --> Scraper[WebScraperAgent]
    
    subgraph "Hybrid Core"
        Scraper --> |常规任务| RPANav[Navigator (CDP)]
        Scraper --> |异常/验证| AINav[AINavigator (VLM)]
        
        RPANav --> Extractor[Extractor]
        AINav --> Extractor
    end
    
    Extractor --> |JSON/DOM| Data[结构化数据]
```
