# 🤖 AI 自动化博客系统

<a href="README.md">English</a> | <a href="README_CN.md">中文</a>

---

AI 驱动的全自动化博客内容生产系统：自动选题 → 搜索最新信息 → 生成文章 → 生成封面与插图 → 上传图床 → 发布到 Notion。

## ✨ 功能特性

- **AI 自动选题** — 自动生成科技热点话题
- **AI 文章生成** — 支持 OpenAI、DeepSeek、Groq、Grok2API、Ollama、Claude 等
- **AI 图片生成** — 支持 Pollinations（免费）、DALL-E、Stability AI、Replicate
- **自动上传图床** — 图片上传至图床，避免 Notion 外链图片过期问题
- **富文本排版** — Markdown → Notion Block 转换，完整格式支持
- **自动插图** — AI 生成章节配图，在 `[插图]` 标记处自动插入
- **Web 管理面板** — React + TailwindCSS 前端，可视化操作
- **CLI & API** — 命令行界面 + REST API（FastAPI）

## 📋 前置条件

本项目依赖以下两个仓库，请先部署：

| 组件 | 仓库 | 说明 |
|------|------|------|
| **图床** | [Image](https://github.com/2021400278zzc/Image) | 基于 Telegraph 的图床服务，部署后可获得 `IMAGE_UPLOAD_URL` 和 `IMAGE_AUTH_CODE` |
| **Notion 博客后台** | [NotionNext](https://github.com/2021400278zzc/NotionNext) | 基于 Notion 的博客框架，部署后创建 Notion 文章数据库 |

> ⚠️ 必须先完成上述两个仓库的部署，本系统才能端到端正常运行。

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────┐
│                  表示层                           │
│  main.py (CLI) │ api_server.py (API) │ React UI  │
├──────────────────────────────────────────────────┤
│                  控制器层                         │
│  BlogController — 业务逻辑与流程编排              │
├──────────────────────────────────────────────────┤
│                  服务层                           │
│  GrokService │ LLMService │ ImageService         │
│  NotionService │ UploaderService                 │
├──────────────────────────────────────────────────┤
│                  模型层                           │
│  Article │ ImageInfo                             │
├──────────────────────────────────────────────────┤
│                  工具层                           │
│  MarkdownParser │ slug_generator                 │
└──────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 克隆与安装

```bash
git clone <本仓库地址>
cd notion自动化博文编写

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置值（详见下方 [配置说明](#配置说明)）。

### 3. 验证配置

```bash
python config.py
```

### 4. 运行

```bash
# 自动模式 — 全流程（自动选题 → 生成 → 发布）
python main.py

# 指定主题
python main.py -t "2026年人工智能发展趋势"

# 交互模式
python main.py -i

# 演示模式（示例内容）
python main.py -d

# Web 管理面板（API 服务 + React 前端）
python api_server.py
# 访问 http://localhost:8000
```

## ⚙️ 配置说明

所有配置通过 `.env` 文件管理，完整模板见 `.env.example`。

### 必填项

| 变量 | 说明 |
|------|------|
| `LLM_API_KEY` | 文本生成 API 密钥（OpenAI / DeepSeek / Groq 等） |
| `NOTION_TOKEN` | Notion Integration Token（[在此获取](https://www.notion.so/my-integrations)） |
| `NOTION_DATABASE_ID` | Notion 数据库 ID（从数据库页面 URL 获取） |

### LLM 提供商配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_PROVIDER` | `openai` | `openai` 或 `claude` |
| `LLM_API_URL` | OpenAI | API 地址 |
| `LLM_MODEL` | `gpt-4o` | 模型名称 |
| `LLM_TEMPERATURE` | `0.7` | 生成温度 |
| `LLM_MAX_TOKENS` | `4096` | 最大输出 token 数 |

使用 Claude 时，请改用 `CLAUDE_*` 系列变量。

**支持的 OpenAI 兼容提供商：**

| 提供商 | LLM_API_URL | 模型示例 |
|--------|-------------|----------|
| OpenAI | `https://api.openai.com/v1/chat/completions` | gpt-4o, gpt-4o-mini |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` | deepseek-chat |
| Groq | `https://api.groq.com/openai/v1/chat/completions` | llama-3.3-70b-versatile |
| Grok2API | `https://grok2api.com/v1/chat/completions` | grok-2 |
| Ollama | `http://localhost:11434/v1/chat/completions` | llama3, qwen2 |

### 图片生成配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `IMAGE_PROVIDER` | `pollinations` | `pollinations`（免费）、`openai`、`stability`、`replicate`、`custom` |
| `POLLINATIONS_API_URL` | Pollinations 地址 | 免费图片生成，无需 API Key |

### 图床配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `IMAGE_UPLOAD_URL` | `https://tc.741568.xyz/upload` | 图床上传地址（来自 [Image](https://github.com/2021400278zzc/Image)） |
| `IMAGE_AUTH_CODE` | `1024` | 图床授权码 |

### 文章配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ARTICLE_MIN_LENGTH` | `2000` | 文章最小字数 |
| `COVER_IMAGE_STYLE` | 科技风格，深色背景... | 封面图片风格描述 |

## 📁 项目结构

```
.
├── main.py              # 命令行入口
├── api_server.py        # FastAPI REST API 服务器
├── config.py            # 全局配置（.env 读取）
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
├── frontend/            # React + TailwindCSS Web 管理面板
│   ├── src/             # 前端源码
│   └── dist/            # 构建产物
├── controllers/         # 控制器层 — 业务逻辑
│   └── blog_controller.py
├── services/            # 服务层 — 外部 API 交互
│   ├── grok_service.py  # 内容生成编排
│   ├── llm_service.py   # LLM 适配层（OpenAI/Claude）
│   ├── notion_service.py # Notion API 交互
│   ├── image_service.py  # 图片生成服务
│   └── uploader_service.py # 图床上传服务
├── models/              # 模型层 — 数据实体
│   ├── article.py       # 文章模型（含状态管理）
│   └── image.py         # 图片信息模型
├── views/               # 视图层 — 界面展示
│   ├── console_view.py  # 控制台输出与用户交互
│   └── article_view.py  # 文章格式化与文件导出
└── utils/               # 工具层 — 辅助函数
    ├── markdown_parser.py # Markdown → Notion Block 转换器
    └── slug_generator.py  # URL slug 生成器
```

## 🔄 运行流程

```
1. 自动选题    -> AI 生成热点话题
2. 搜索信息    -> AI 搜索最新相关资料
3. 生成文章    -> AI 撰写结构化 Markdown 文章
4. 生成封面    -> AI 创建封面图片
5. 生成插图    -> AI 为 [插图] 标记生成章节配图
6. 上传图床    -> 将所有图片上传至图床
7. Markdown 解析 -> 将 Markdown 转换为 Notion Block
8. 发布到 Notion -> 创建页面并追加内容块
```

## 🕐 定时任务

### Linux/Mac（Cron）

```bash
crontab -e
# 每6小时运行一次
0 */6 * * * cd /path/to/project && /usr/bin/python3 main.py >> cron.log 2>&1
```

### Windows（任务计划程序）

```powershell
schtasks /create /tn "AutoBlog" /tr "python F:\path\to\main.py" /sc hourly /mo 6
```

## 🔒 安全注意事项

- **切勿**将 `.env` 文件提交到版本控制（已在 `.gitignore` 中）
- **切勿**在源代码中硬编码 API 密钥
- 定期更换 API 密钥
- 限制 Notion Integration 权限范围，仅授权所需数据库

## 📜 开源协议

MIT
