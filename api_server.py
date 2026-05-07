"""
FastAPI Web 服务器
为前端提供 REST API 接口
"""

import os
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("temp/articles", exist_ok=True)
    os.makedirs("temp/images", exist_ok=True)
    yield


app = FastAPI(
    title="AI 自动化博客系统",
    description="AI Blog Automation API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARTICLES_DIR = os.path.join("temp", "articles")
os.makedirs(ARTICLES_DIR, exist_ok=True)

tasks_status: Dict[str, Dict[str, Any]] = {}


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]


def _is_masked(value: str) -> bool:
    return "****" in value


def _get_config_dict():
    import config as cfg
    return {
        "llm": {
            "provider": cfg.LLM_PROVIDER,
            "api_url": cfg.LLM_API_URL,
            "api_key": _mask(cfg.LLM_API_KEY),
            "model": cfg.LLM_MODEL,
            "temperature": cfg.LLM_TEMPERATURE,
            "max_tokens": cfg.LLM_MAX_TOKENS,
            "top_p": cfg.LLM_TOP_P,
            "claude_api_url": cfg.CLAUDE_API_URL,
            "claude_api_key": _mask(cfg.CLAUDE_API_KEY),
            "claude_model": cfg.CLAUDE_MODEL,
            "claude_max_tokens": cfg.CLAUDE_MAX_TOKENS,
            "claude_temperature": cfg.CLAUDE_TEMPERATURE,
        },
        "image": {
            "provider": cfg.IMAGE_PROVIDER,
            "pollinations_api_url": cfg.POLLINATIONS_API_URL,
            "pollinations_width": cfg.POLLINATIONS_WIDTH,
            "pollinations_height": cfg.POLLINATIONS_HEIGHT,
            "api_url": cfg.IMAGE_API_URL,
            "api_key": _mask(cfg.IMAGE_API_KEY),
            "model": cfg.IMAGE_MODEL,
            "size": cfg.IMAGE_SIZE,
            "quality": cfg.IMAGE_QUALITY,
            "stability_api_url": cfg.STABILITY_API_URL,
            "stability_api_key": _mask(cfg.STABILITY_API_KEY),
            "stability_model": cfg.STABILITY_MODEL,
            "replicate_api_url": cfg.REPLICATE_API_URL,
            "replicate_api_key": _mask(cfg.REPLICATE_API_KEY),
            "replicate_model": cfg.REPLICATE_MODEL,
            "custom_api_url": cfg.CUSTOM_IMAGE_API_URL,
            "custom_api_key": _mask(cfg.CUSTOM_IMAGE_API_KEY),
            "custom_model": cfg.CUSTOM_IMAGE_MODEL,
        },
        "notion": {
            "token": _mask(cfg.NOTION_TOKEN),
            "database_id": cfg.NOTION_DATABASE_ID,
        },
        "upload": {
            "url": cfg.IMAGE_UPLOAD_URL,
            "auth_code": cfg.IMAGE_AUTH_CODE,
        },
        "article": {
            "min_length": cfg.ARTICLE_MIN_LENGTH,
            "cover_image_style": cfg.COVER_IMAGE_STYLE,
        },
    }


class TopicRequest(BaseModel):
    topic: Optional[str] = None


class ArticleUpdateRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    content_markdown: Optional[str] = None
    cover_url: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    model_config = {"extra": "allow"}


class GenerateImageRequest(BaseModel):
    prompt: Optional[str] = None
    article_id: Optional[str] = None
    image_type: Optional[str] = "cover"


def _save_article(article_data: Dict[str, Any]) -> str:
    article_id = article_data.get("id") or str(uuid.uuid4())
    article_data["id"] = article_id
    article_data["updated_at"] = datetime.now().isoformat()

    filepath = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)

    return article_id


def _load_article(article_id: str) -> Optional[Dict[str, Any]]:
    filepath = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _list_articles() -> List[Dict[str, Any]]:
    articles = []
    if not os.path.exists(ARTICLES_DIR):
        return articles
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(ARTICLES_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                articles.append(data)
    articles.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return articles


def _delete_article(article_id: str) -> bool:
    filepath = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def _run_generate_task(task_id: str, topic: Optional[str]):
    try:
        tasks_status[task_id] = {"status": "running", "step": "选题中...", "progress": 10}

        import importlib
        import config as cfg
        importlib.reload(cfg)
        from services.grok_service import GrokService
        from services.llm_service import LLMService

        llm = LLMService()
        grok = GrokService()

        if not topic:
            tasks_status[task_id] = {"status": "running", "step": "AI 选题中...", "progress": 20}
            topic = grok.generate_topic()

        tasks_status[task_id] = {"status": "running", "step": f"搜索「{topic[:30]}」相关资料...", "progress": 35}
        research = grok.search_latest_info(topic)

        tasks_status[task_id] = {"status": "running", "step": "生成文章中...", "progress": 55}
        article_data = grok.generate_article(topic, research)

        article_data["status"] = "draft"
        article_data["cover_url"] = None

        from utils.slug_generator import generate_slug
        article_data["slug"] = generate_slug(article_data.get("title", "untitled"))

        tasks_status[task_id] = {"status": "running", "step": "生成封面中...", "progress": 75}

        try:
            from services.image_service import ImageService
            image_service = ImageService()
            cover_info = image_service.generate_cover_image(
                article_data.get("title", ""),
                article_data.get("summary", "")
            )
            if cover_info and cover_info.is_ready:
                article_data["cover_url"] = cover_info.url
        except Exception as img_err:
            print(f"封面生成失败: {img_err}")

        article_id = _save_article(article_data)

        tasks_status[task_id] = {
            "status": "completed",
            "step": "生成完成",
            "progress": 100,
            "article_id": article_id,
        }

    except Exception as e:
        tasks_status[task_id] = {
            "status": "failed",
            "step": f"生成失败: {str(e)}",
            "progress": 0,
            "error": str(e),
        }


def _run_generate_image_task(task_id: str, article_id: str, image_type: str, prompt: Optional[str]):
    try:
        tasks_status[task_id] = {"status": "running", "step": "生成图片中...", "progress": 30}

        import importlib
        import config as cfg
        importlib.reload(cfg)
        from services.image_service import ImageService
        from services.grok_service import GrokService

        image_service = ImageService()
        grok = GrokService()

        article = _load_article(article_id)
        if not article:
            tasks_status[task_id] = {"status": "failed", "step": "文章不存在", "progress": 0, "error": "Article not found"}
            return

        if not prompt:
            if image_type == "cover":
                prompt = grok.generate_cover_prompt(article.get("title", ""), article.get("summary", ""))
            else:
                prompt = f"Technology illustration about {article.get('title', 'blog content')}, modern style, dark background"

        tasks_status[task_id] = {"status": "running", "step": "图片生成中...", "progress": 60}

        image_url = image_service._generate_image(prompt, image_type)

        if image_url:
            if image_type == "cover":
                article["cover_url"] = image_url
            _save_article(article)

            tasks_status[task_id] = {
                "status": "completed",
                "step": "图片生成完成",
                "progress": 100,
                "image_url": image_url,
            }
        else:
            tasks_status[task_id] = {
                "status": "failed",
                "step": "图片生成失败",
                "progress": 0,
                "error": "Image generation returned no URL",
            }

    except Exception as e:
        tasks_status[task_id] = {
            "status": "failed",
            "step": f"图片生成失败: {str(e)}",
            "progress": 0,
            "error": str(e),
        }


def _run_publish_task(task_id: str, article_id: str):
    try:
        tasks_status[task_id] = {"status": "running", "step": "解析 Markdown...", "progress": 20}

        import importlib
        import config as cfg
        importlib.reload(cfg)
        from services.notion_service import get_notion_service
        from services.image_service import get_image_service
        from utils.markdown_parser import MarkdownParser
        from models.article import Article, ArticleStatus

        article_data = _load_article(article_id)
        if not article_data:
            tasks_status[task_id] = {"status": "failed", "step": "文章不存在", "progress": 0, "error": "Article not found"}
            return

        article = Article.from_dict(article_data)
        article.status = ArticleStatus.PUBLISHED

        if not article.slug:
            from utils.slug_generator import generate_slug
            article.slug = generate_slug(article.title)

        tasks_status[task_id] = {"status": "running", "step": "解析文章内容...", "progress": 35}

        parser = MarkdownParser()
        blocks = parser.parse(article.content_markdown)
        article.blocks = blocks

        tasks_status[task_id] = {"status": "running", "step": "注入插图...", "progress": 50}

        image_service = get_image_service()
        new_blocks = []
        image_count = 0
        for i, block in enumerate(article.blocks):
            if block.get("type") == "IMAGE_PLACEHOLDER":
                section_context = "blog content"
                for j in range(i - 1, -1, -1):
                    bt = article.blocks[j].get("type", "")
                    if bt in ["heading_1", "heading_2", "heading_3"]:
                        rt = article.blocks[j].get(bt, {}).get("rich_text", [])
                        if rt:
                            section_context = rt[0].get("text", {}).get("content", "")
                            break
                try:
                    from services.notion_service import image_block
                    prompt = f"Technology illustration about {section_context}"
                    image_url = image_service._generate_image(prompt, f"section_{image_count}")
                    image_count += 1
                    if image_url:
                        new_blocks.append(image_block(image_url))
                except:
                    pass
            else:
                new_blocks.append(block)
        article.blocks = new_blocks

        tasks_status[task_id] = {"status": "running", "step": "发布到 Notion...", "progress": 75}

        notion = get_notion_service()
        page = notion.create_page(article)
        notion.append_blocks(page["id"], article.blocks)

        article_data["status"] = "published"
        article_data["notion_page_id"] = page["id"]
        article_data["notion_page_url"] = page["url"]
        article_data["slug"] = article.slug
        _save_article(article_data)

        tasks_status[task_id] = {
            "status": "completed",
            "step": "发布成功",
            "progress": 100,
            "page_url": page["url"],
        }

    except Exception as e:
        tasks_status[task_id] = {
            "status": "failed",
            "step": f"发布失败: {str(e)}",
            "progress": 0,
            "error": str(e),
        }


# ============ API 路由 ============

@app.get("/api/config")
def get_config():
    try:
        return _get_config_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config")
def update_config(req: ConfigUpdateRequest):
    try:
        req_data = req.model_dump()
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if not os.path.exists(env_path):
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("")

        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        env_dict: Dict[str, str] = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env_dict[key.strip()] = value.strip()

        mapping = {
            "llm_provider": "LLM_PROVIDER",
            "llm_api_url": "LLM_API_URL",
            "llm_api_key": "LLM_API_KEY",
            "llm_model": "LLM_MODEL",
            "llm_temperature": "LLM_TEMPERATURE",
            "llm_max_tokens": "LLM_MAX_TOKENS",
            "llm_top_p": "LLM_TOP_P",
            "claude_api_url": "CLAUDE_API_URL",
            "claude_api_key": "CLAUDE_API_KEY",
            "claude_model": "CLAUDE_MODEL",
            "claude_max_tokens": "CLAUDE_MAX_TOKENS",
            "claude_temperature": "CLAUDE_TEMPERATURE",
            "image_provider": "IMAGE_PROVIDER",
            "image_api_url": "IMAGE_API_URL",
            "image_api_key": "IMAGE_API_KEY",
            "image_model": "IMAGE_MODEL",
            "image_size": "IMAGE_SIZE",
            "image_quality": "IMAGE_QUALITY",
            "notion_token": "NOTION_TOKEN",
            "notion_database_id": "NOTION_DATABASE_ID",
            "cover_image_style": "COVER_IMAGE_STYLE",
            "article_min_length": "ARTICLE_MIN_LENGTH",
        }

        for field_name, env_key in mapping.items():
            value = req_data.get(field_name)
            if value is not None and not _is_masked(str(value)):
                env_dict[env_key] = str(value)

        with open(env_path, "w", encoding="utf-8") as f:
            f.write("# AI 自动化博客系统环境变量配置\n")
            f.write("# 由前端配置页面自动生成\n\n")
            for key, value in env_dict.items():
                f.write(f"{key}={value}\n")

        import importlib
        import config as cfg
        importlib.reload(cfg)

        import services.llm_service as llm_mod
        import services.grok_service as grok_mod
        import services.image_service as img_mod
        import services.notion_service as notion_mod
        llm_mod._llm_service = None
        grok_mod._grok_service = None
        img_mod._image_service = None
        notion_mod._notion_service = None

        return {"message": "配置已更新并保存到 .env 文件", "success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles")
def list_articles():
    try:
        articles = _list_articles()
        summaries = []
        for a in articles:
            summaries.append({
                "id": a.get("id"),
                "title": a.get("title", ""),
                "summary": a.get("summary", ""),
                "category": a.get("category", ""),
                "tags": a.get("tags", []),
                "status": a.get("status", "draft"),
                "cover_url": a.get("cover_url"),
                "notion_page_url": a.get("notion_page_url"),
                "updated_at": a.get("updated_at"),
                "word_count": len(a.get("content_markdown", "")),
            })
        return {"articles": summaries, "total": len(summaries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/articles/generate")
def generate_article(req: TopicRequest):
    try:
        task_id = str(uuid.uuid4())
        tasks_status[task_id] = {"status": "pending", "step": "准备中...", "progress": 0}

        thread = threading.Thread(
            target=_run_generate_task,
            args=(task_id, req.topic),
            daemon=True,
        )
        thread.start()

        return {"task_id": task_id, "message": "文章生成任务已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
def get_task_status(task_id: str):
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_status[task_id]


@app.get("/api/articles/{article_id}")
def get_article(article_id: str):
    article = _load_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.put("/api/articles/{article_id}")
def update_article(article_id: str, req: ArticleUpdateRequest):
    article = _load_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = req.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            article[key] = value

    _save_article(article)
    return {"message": "文章已更新", "article": article}


@app.delete("/api/articles/{article_id}")
def delete_article(article_id: str):
    if not _delete_article(article_id):
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "文章已删除"}


@app.post("/api/articles/{article_id}/publish")
def publish_article(article_id: str):
    try:
        task_id = str(uuid.uuid4())
        tasks_status[task_id] = {"status": "pending", "step": "准备发布...", "progress": 0}

        thread = threading.Thread(
            target=_run_publish_task,
            args=(task_id, article_id),
            daemon=True,
        )
        thread.start()

        return {"task_id": task_id, "message": "发布任务已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/articles/{article_id}/generate-image")
def regenerate_image(article_id: str, req: GenerateImageRequest):
    try:
        task_id = str(uuid.uuid4())
        tasks_status[task_id] = {"status": "pending", "step": "准备生成图片...", "progress": 0}

        thread = threading.Thread(
            target=_run_generate_image_task,
            args=(task_id, article_id, req.image_type or "cover", req.prompt),
            daemon=True,
        )
        thread.start()

        return {"task_id": task_id, "message": "图片生成任务已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    try:
        articles = _list_articles()
        total = len(articles)
        published = sum(1 for a in articles if a.get("status") == "published")
        drafts = sum(1 for a in articles if a.get("status") == "draft")
        total_words = sum(len(a.get("content_markdown", "")) for a in articles)

        config_ok = True
        config_errors = []
        try:
            import config as cfg
            if not cfg.LLM_API_KEY and not cfg.CLAUDE_API_KEY:
                config_errors.append("LLM API Key 未配置")
            if not cfg.NOTION_TOKEN:
                config_errors.append("Notion Token 未配置")
            if not cfg.NOTION_DATABASE_ID:
                config_errors.append("Notion Database ID 未配置")
            if config_errors:
                config_ok = False
        except:
            config_ok = False
            config_errors.append("配置加载失败")

        return {
            "total_articles": total,
            "published": published,
            "drafts": drafts,
            "total_words": total_words,
            "config_ok": config_ok,
            "config_errors": config_errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
    if os.path.isdir(frontend_dist):
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = os.path.join(frontend_dist, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(frontend_dist, "index.html"))

    uvicorn.run(app, host="0.0.0.0", port=8000)
