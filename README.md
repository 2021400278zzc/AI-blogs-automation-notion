# 🤖 AI Automated Blog System

<a href="README.md">English</a> | <a href="README_CN.md">中文</a>

---

An AI-powered fully automated blog content production system: auto topic selection → information search → article generation → cover & illustration generation → image hosting upload → publish to Notion.

## ✨ Features

- **AI Topic Selection** — Automatically generates trending tech topics
- **AI Article Generation** — Supports OpenAI, DeepSeek, Groq, Grok2API, Ollama, Claude and more
- **AI Image Generation** — Supports Pollinations (free), DALL-E, Stability AI, Replicate
- **Auto Image Upload** — Uploads to image hosting, no Notion external image expiration issues
- **Rich Text Formatting** — Markdown → Notion Block conversion with full formatting support
- **Auto Illustrations** — AI-generated section images inserted at `[插图]` markers
- **Web Dashboard** — React + TailwindCSS frontend for visual management
- **CLI & API** — Command-line interface + REST API (FastAPI)

## 📋 Prerequisites

This project depends on the following two repositories. Please deploy them first:

| Component | Repository | Description |
|-----------|-----------|-------------|
| **Image Hosting** | [Image](https://github.com/2021400278zzc/Image) | Telegraph-based image hosting service. Deploy this to get `IMAGE_UPLOAD_URL` and `IMAGE_AUTH_CODE` |
| **Notion Blog Backend** | [NotionNext](https://github.com/2021400278zzc/NotionNext) | Notion-powered blog framework. Deploy this and create a Notion database for articles |

> ⚠️ Both repositories must be properly deployed before this system can work end-to-end.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│               Presentation Layer                 │
│  main.py (CLI) │ api_server.py (API) │ React UI  │
├──────────────────────────────────────────────────┤
│               Controller Layer                   │
│  BlogController — Business logic & workflow      │
├──────────────────────────────────────────────────┤
│                Service Layer                     │
│  GrokService │ LLMService │ ImageService         │
│  NotionService │ UploaderService                 │
├──────────────────────────────────────────────────┤
│                 Model Layer                      │
│  Article │ ImageInfo                             │
├──────────────────────────────────────────────────┤
│                 Utils Layer                      │
│  MarkdownParser │ slug_generator                 │
└──────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <this-repo-url>
cd notion自动化博文编写

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual values (see [Configuration](#configuration) below).

### 3. Verify Configuration

```bash
python config.py
```

### 4. Run

```bash
# Auto mode - full pipeline (auto topic -> generate -> publish)
python main.py

# Specify a topic
python main.py -t "AI trends in 2026"

# Interactive mode
python main.py -i

# Demo mode (sample content)
python main.py -d

# Web dashboard (API server + React frontend)
python api_server.py
# Then visit http://localhost:8000
```

## ⚙️ Configuration

All configuration is managed via the `.env` file. See `.env.example` for the full template.

### Required

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | API key for text generation (OpenAI / DeepSeek / Groq / etc.) |
| `NOTION_TOKEN` | Notion Integration Token ([Get it here](https://www.notion.so/my-integrations)) |
| `NOTION_DATABASE_ID` | Notion database ID (from the database URL) |

### LLM Provider

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai` or `claude` |
| `LLM_API_URL` | OpenAI | API endpoint URL |
| `LLM_MODEL` | `gpt-4o` | Model name |
| `LLM_TEMPERATURE` | `0.7` | Generation temperature |
| `LLM_MAX_TOKENS` | `4096` | Max output tokens |

For Claude, use `CLAUDE_*` variables instead.

**Supported OpenAI-compatible providers:**

| Provider | LLM_API_URL | Model Examples |
|----------|-------------|---------------|
| OpenAI | `https://api.openai.com/v1/chat/completions` | gpt-4o, gpt-4o-mini |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` | deepseek-chat |
| Groq | `https://api.groq.com/openai/v1/chat/completions` | llama-3.3-70b-versatile |
| Grok2API | `https://grok2api.com/v1/chat/completions` | grok-2 |
| Ollama | `http://localhost:11434/v1/chat/completions` | llama3, qwen2 |

### Image Generation

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_PROVIDER` | `pollinations` | `pollinations` (free), `openai`, `stability`, `replicate`, `custom` |
| `POLLINATIONS_API_URL` | Pollinations URL | Free image generation, no API key needed |

### Image Hosting

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_UPLOAD_URL` | `https://tc.741568.xyz/upload` | Upload URL (from [Image](https://github.com/2021400278zzc/Image)) |
| `IMAGE_AUTH_CODE` | `1024` | Authorization code for image hosting |

### Article

| Variable | Default | Description |
|----------|---------|-------------|
| `ARTICLE_MIN_LENGTH` | `2000` | Minimum article length (characters) |
| `COVER_IMAGE_STYLE` | Tech style, dark bg... | Cover image style prompt |

## 📁 Project Structure

```
.
├── main.py              # CLI entry point
├── api_server.py        # FastAPI REST API server
├── config.py            # Global configuration (.env reader)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── frontend/            # React + TailwindCSS web dashboard
│   ├── src/             # Frontend source code
│   └── dist/            # Built frontend assets
├── controllers/         # Business logic layer
│   └── blog_controller.py
├── services/            # External API service layer
│   ├── grok_service.py  # Content generation orchestration
│   ├── llm_service.py   # LLM adapter (OpenAI/Claude)
│   ├── notion_service.py # Notion API interaction
│   ├── image_service.py  # Image generation service
│   └── uploader_service.py # Image hosting upload
├── models/              # Data entity layer
│   ├── article.py       # Article model with status management
│   └── image.py         # ImageInfo model
├── views/               # Presentation layer
│   ├── console_view.py  # Console output & user interaction
│   └── article_view.py  # Article formatting & file export
└── utils/               # Utility layer
    ├── markdown_parser.py # Markdown -> Notion Block converter
    └── slug_generator.py  # URL slug generator
```

## 🔄 Workflow

```
1. Topic Selection    -> AI generates trending topic
2. Information Search -> AI searches for latest information
3. Article Generation -> AI writes structured Markdown article
4. Cover Generation   -> AI creates cover image
5. Illustration       -> AI generates section images for [插图] markers
6. Image Upload       -> Upload all images to image hosting
7. Markdown Parsing   -> Convert Markdown to Notion Blocks
8. Notion Publishing  -> Create page and append blocks
```

## 🕐 Scheduled Tasks

### Linux/Mac (Cron)

```bash
crontab -e
# Run every 6 hours
0 */6 * * * cd /path/to/project && /usr/bin/python3 main.py >> cron.log 2>&1
```

### Windows (Task Scheduler)

```powershell
schtasks /create /tn "AutoBlog" /tr "python F:\path\to\main.py" /sc hourly /mo 6
```

## 🔒 Security Notes

- **Never** commit `.env` to version control (already in `.gitignore`)
- **Never** hardcode API keys in source code
- Rotate API keys periodically
- Limit Notion Integration permissions to only the required database

## 📜 License

MIT
