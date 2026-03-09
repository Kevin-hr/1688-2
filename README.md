# 1688 AI 自动化采集 Agent

> 高效的 1688.com 电商自动化商品检索与数据采集工具，由 OpenClaw LLM 驱动。

## 简介 (Introduction)
本工具专为自动化执行 1688 电商平台的商品检索和资源获取而设计。它能够自动登录（持久化会话）、检索关键词、解析商品详细的属性与规格，并将高质量的首图下载至本地目录，最后导出标准化的 Markdown 数据报告。

## 核心特性 (Features)
- 🤖 **LLM 指令支持**：支持简单的自然语音指令解析。
- 🔍 **商品检索提取**：通过无头浏览器自动化提取页面数据，规避反爬风控检测。
- 📦 **结构化存储**：按商品名称创建独立文件夹，保存 Markdown 报告及图片资产。
- 🛡️ **安全登录持久化**：支持手动扫码后自动保存并持久化 Cookie 状态，无需重复登录。

## 安装与配置 (Installation)

1. 克隆代码库：
   ```bash
   git clone https://github.com/用户名/1688-2.git
   cd 1688-2
   ```

2. 安装依赖 (使用 Python 3.10+)：
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. 首次配置登录：
   ```bash
   python login_1688.py
   # 按照控制台提示，完成浏览器扫码登录，程序将自动保存会话状态
   ```

## 快速使用 (Quick Start)

通过终端传递一句话指令即可启动自动化采集工作流：

```bash
python main.py "去1688搜索猫咪玩具"
```

## 数据输出格式 (Output FORMAT)
成功执行后，会在根目录下生成 `1688_products/` 文件夹：
```text
1688_products/
├── 商品名称A/
│   ├── detail.md (包含商品价格、链接、具体规格熟悉)
│   └── images/ (包含最多5张无水印大图)
└── 商品名称B/
    ├── detail.md
    └── images/
```

## 注意事项 (Important Notes)
1. **反爬策略更新**：1688 的 DOM 结构可能随时发生变化，`query_selector` 可能需要定期维护。
2. **频率限制**：推荐每个关键词提取最多限制在前 10 项，避免被平台判定高频访问封号。
3. 请遵守相应的法律法规，勿做违规高并发爬取。
