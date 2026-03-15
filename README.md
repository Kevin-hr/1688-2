# 1688 商品采集工具 (1688-2)

> 1688.com 商品数据采集工具，支持一键采集、Ozon Global 上架

## 功能特性

| 功能 | 说明 | 状态 |
|------|------|------|
| URL采集 | 单品详情页抓取 | ✅ |
| 关键词搜索 | 批量商品搜索 | ⚠️ 受1688限制 |
| Excel导出 | 格式化报表生成 | ✅ |
| Ozon转换 | 转换为Ozon上架格式 | ✅ |
| 翻译功能 | 中→俄/英翻译 | ✅ |
| Ozon上传 | API上传到Ozon | ✅ 已验证成功 |

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

在项目根目录创建 `.env` 文件：

```env
# Ozon API 凭证 (从 Seller后台 → 设置 → API获取)
OZON_CLIENT_ID=your_client_id
OZON_API_KEY=your_api_key
```

## 使用方式

### 方式一：命令行模式

```bash
# URL采集 (推荐)
python main.py --url "https://detail.1688.com/offer/566971549514.html"

# 关键词搜索
python main.py --keyword "猫玩具" --limit 5

# 自然语言模式
python main.py "去1688搜索猫咪玩具"
```

### 方式二：MCP服务器

注册 MCP 服务：

```json
// ~/.claude/mcp.json
{
  "mcpServers": {
    "1688-scraper": {
      "command": "python",
      "args": ["C:/Users/52648/Documents/GitHub/1688-2/mcp_server.py"],
      "env": {}
    }
  }
}
```

MCP 工具列表：

| 工具 | 功能 |
|------|------|
| `search_1688` | 关键词搜索 |
| `scrape_1688_url` | URL单品抓取 |
| `transform_1688_to_ozon` | 转换为Ozon格式 |
| `export_1688_to_excel` | 导出Excel |
| `upload_ozon` | 上传Ozon |
| `list_ozon_products` | 查询Ozon商品 |
| `get采集状态` | 获取采集状态 |

### 方式三：CLI调用

```bash
# URL采集
python mcp_server.py --mode cli --url "https://detail.1688.com/offer/xxx.html"

# 关键词搜索
python mcp_server.py --mode cli --keyword "猫玩具" --limit 3
```

## 输出文件

采集结果保存在 `1688_products/` 目录：

```
1688_products/
├── 1688_single_商品采集报表.xlsx   # Excel报表
├── ozon_export.json                # Ozon JSON
└── {商品名称}/
    ├── detail.md                   # 商品详情
    └── images/                     # 商品图片
        ├── img_0.jpg
        ├── img_1.jpg
        └── ...
```

## 项目结构

```
1688-2/
├── main.py                      # 主入口
├── mcp_server.py                # MCP服务器
├── test_all_modules.py          # 测试脚本
├── .env                         # 环境变量
├── src/
│   ├── task_router.py           # 任务路由器
│   ├── agents/
│   │   └── web_scraper_agent.py # 浏览器采集
│   ├── utils/
│   │   ├── ozon_api.py         # Ozon API
│   │   ├── ozon_transformer.py  # 格式转换
│   │   ├── excel_exporter.py   # Excel导出
│   │   └── file_manager.py     # 文件管理
│   └── modules/
│       ├── translator.py        # 翻译模块
│       ├── anti_detect.py      # 反检测配置
│       └── ...
└── logs/                        # 日志目录
    ├── mcp_server.log
    └── ozon_api.log
```

## 测试

```bash
python test_all_modules.py
```

## 注意事项

1. **关键词搜索限制**: 1688搜索API需要登录，关键词搜索可能受限
2. **推荐方式**: 使用URL采集模式，更稳定
3. **图片下载**: 每次采集最多下载5张图片
4. **Ozon上传**: 需要有效的API凭证才能上传

## 更新日志

### v1.3.3 (2026-03-15) - Ozon 联调大获全胜
- **API 协议修复**: 补全必需的 `type_id` 字段，实现从 JSON 到 Ozon 卖家后台的成功上传。
- **采集存证系统**: 自动生成 `scrape_visual_proof.png` 截图，为所有抓取数据提供视觉证据。
- **图像净化工程**: 引入图片黑名单机制，自动屏蔽 SVG/TPS 等非商品高清图。
- **单位转换增强**: 深度兼容 m/cm/mm 等多种长度单位。
- **Windows 兼容性**: 完美过滤文件路径中的 NUL/CON/AUX 等保留字符。

### v1.3.2 (2026-03-14)
- 优化浏览器为 headless=True + Stealth 模式
- 增加3个备选搜索URL策略
- 重新启用反检测脚本注入
- 添加MCP日志记录
- 添加CLI命令行模式
