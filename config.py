"""
AI 自动化博客系统配置文件
支持从 .env 文件和环境变量读取配置
适配主流 AI 模型格式：OpenAI兼容格式、Claude格式等
图片生成支持多种模型格式配置
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        load_dotenv(override=True)
except ImportError:
    pass


_config_warnings = []


def _get_env(key: str, default: str = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and not value:
        _config_warnings.append(f"环境变量 {key} 未设置，请在 .env 文件或系统环境中配置")
        return ""
    return value


# ============ LLM 配置（文本生成） ============
# 支持的提供商: openai, claude, custom
LLM_PROVIDER = _get_env("LLM_PROVIDER", "openai")

# --- OpenAI 兼容格式（适用于 OpenAI、DeepSeek、Groq、Grok2API、Ollama 等） ---
LLM_API_URL = _get_env("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
LLM_API_KEY = _get_env("LLM_API_KEY", "", required=True)
LLM_MODEL = _get_env("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(_get_env("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(_get_env("LLM_MAX_TOKENS", "4096"))
LLM_TOP_P = float(_get_env("LLM_TOP_P", "1.0"))

# --- Claude 格式 ---
CLAUDE_API_URL = _get_env("CLAUDE_API_URL", "https://api.anthropic.com/v1/messages")
CLAUDE_API_KEY = _get_env("CLAUDE_API_KEY", "")
CLAUDE_MODEL = _get_env("CLAUDE_MODEL", "claude-sonnet-4-20250514")
CLAUDE_MAX_TOKENS = int(_get_env("CLAUDE_MAX_TOKENS", "4096"))
CLAUDE_TEMPERATURE = float(_get_env("CLAUDE_TEMPERATURE", "0.7"))

# ============ 图片生成模型配置 ============
# 支持的提供商: pollinations, openai, stability, replicate, custom
IMAGE_PROVIDER = _get_env("IMAGE_PROVIDER", "pollinations")

# --- Pollinations.ai（免费，无需API Key） ---
POLLINATIONS_API_URL = _get_env("POLLINATIONS_API_URL", "https://image.pollinations.ai/prompt/")
POLLINATIONS_WIDTH = int(_get_env("POLLINATIONS_WIDTH", "1024"))
POLLINATIONS_HEIGHT = int(_get_env("POLLINATIONS_HEIGHT", "576"))

# --- OpenAI DALL-E 格式 ---
IMAGE_API_URL = _get_env("IMAGE_API_URL", "https://api.openai.com/v1/images/generations")
IMAGE_API_KEY = _get_env("IMAGE_API_KEY", "")
IMAGE_MODEL = _get_env("IMAGE_MODEL", "dall-e-3")
IMAGE_SIZE = _get_env("IMAGE_SIZE", "1024x1024")
IMAGE_QUALITY = _get_env("IMAGE_QUALITY", "standard")
IMAGE_N = int(_get_env("IMAGE_N", "1"))

# --- Stability AI 格式 ---
STABILITY_API_URL = _get_env("STABILITY_API_URL", "https://api.stability.ai/v2beta/image/generate")
STABILITY_API_KEY = _get_env("STABILITY_API_KEY", "")
STABILITY_MODEL = _get_env("STABILITY_MODEL", "stable-diffusion-xl")
STABILITY_WIDTH = int(_get_env("STABILITY_WIDTH", "1024"))
STABILITY_HEIGHT = int(_get_env("STABILITY_HEIGHT", "576"))

# --- Replicate 格式 ---
REPLICATE_API_URL = _get_env("REPLICATE_API_URL", "https://api.replicate.com/v1/predictions")
REPLICATE_API_KEY = _get_env("REPLICATE_API_KEY", "")
REPLICATE_MODEL = _get_env("REPLICATE_MODEL", "stability-ai/sdxl")

# --- 自定义图片生成API（OpenAI兼容格式） ---
CUSTOM_IMAGE_API_URL = _get_env("CUSTOM_IMAGE_API_URL", "")
CUSTOM_IMAGE_API_KEY = _get_env("CUSTOM_IMAGE_API_KEY", "")
CUSTOM_IMAGE_MODEL = _get_env("CUSTOM_IMAGE_MODEL", "")

# ============ Notion 配置 ============
NOTION_TOKEN = _get_env("NOTION_TOKEN", "", required=True)
NOTION_DATABASE_ID = _get_env("NOTION_DATABASE_ID", "", required=True)

# ============ 图床配置 ============
IMAGE_UPLOAD_URL = _get_env("IMAGE_UPLOAD_URL", "https://tc.741568.xyz/upload")
IMAGE_AUTH_CODE = _get_env("IMAGE_AUTH_CODE", "1024")
IMAGE_UPLOAD_PARAMS = {
    "authCode": IMAGE_AUTH_CODE,
    "serverCompress": "true",
    "uploadChannel": "telegram",
    "uploadNameType": "default",
    "autoRetry": "true",
    "uploadFolder": ""
}

# ============ 文章生成配置 ============
ARTICLE_MIN_LENGTH = int(_get_env("ARTICLE_MIN_LENGTH", "2000"))
COVER_IMAGE_STYLE = _get_env("COVER_IMAGE_STYLE", """科技风格，深色背景，现代感，无文字，简约设计，高品质，专业感""")

# ============ 系统配置 ============
BATCH_SIZE = int(_get_env("BATCH_SIZE", "100"))
TEMP_DIR = _get_env("TEMP_DIR", "temp")
IMAGES_DIR = _get_env("IMAGES_DIR", "temp/images")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# ============ 向后兼容（旧配置自动映射） ============
# 如果用户仍使用旧的 GROK_* 配置，自动映射到新配置
_GROK_API_URL = _get_env("GROK_API_URL", "")
_GROK_API_KEY = _get_env("GROK_API_KEY", "")
_GROK_MODEL = _get_env("GROK_MODEL", "")
if _GROK_API_URL and not _get_env("LLM_API_URL", ""):
    LLM_API_URL = _GROK_API_URL
    LLM_PROVIDER = "openai"
if _GROK_API_KEY and not _get_env("LLM_API_KEY", ""):
    LLM_API_KEY = _GROK_API_KEY
if _GROK_MODEL and not _get_env("LLM_MODEL", ""):
    LLM_MODEL = _GROK_MODEL


def validate_config():
    missing = []

    if LLM_PROVIDER == "openai" and not LLM_API_KEY:
        missing.append("LLM_API_KEY")
    elif LLM_PROVIDER == "claude" and not CLAUDE_API_KEY:
        missing.append("CLAUDE_API_KEY")

    if not NOTION_TOKEN:
        missing.append("NOTION_TOKEN")
    if not NOTION_DATABASE_ID:
        missing.append("NOTION_DATABASE_ID")

    if missing:
        raise ValueError(
            f"缺少必要的配置项: {', '.join(missing)}\n"
            "请在项目根目录创建 .env 文件并配置\n"
            "参考 .env.example 文件"
        )


def print_config_info():
    print("=" * 50)
    print("配置信息")
    print("=" * 50)
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"LLM API URL: {LLM_API_URL}")
    print(f"LLM Model: {LLM_MODEL}")
    print(f"LLM API Key: {'*' * 10 if LLM_API_KEY else '未设置'}")
    if LLM_PROVIDER == "claude":
        print(f"Claude API URL: {CLAUDE_API_URL}")
        print(f"Claude Model: {CLAUDE_MODEL}")
        print(f"Claude API Key: {'*' * 10 if CLAUDE_API_KEY else '未设置'}")
    print(f"Image Provider: {IMAGE_PROVIDER}")
    print(f"Image Model: {IMAGE_MODEL if IMAGE_PROVIDER == 'openai' else IMAGE_PROVIDER}")
    print(f"Notion Token: {'*' * 10 if NOTION_TOKEN else '未设置'}")
    print(f"Notion Database ID: {NOTION_DATABASE_ID[:10] + '...' if NOTION_DATABASE_ID else '未设置'}")
    print(f"Image Upload URL: {IMAGE_UPLOAD_URL}")
    print(f"Temp Dir: {TEMP_DIR}")
    print(f"Images Dir: {IMAGES_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    validate_config()
    print_config_info()
