"""
AI 内容生成服务
基于通用 LLM 服务，支持 OpenAI 兼容格式和 Claude 格式
"""

import json
import re
from typing import Dict

import config
from services.llm_service import get_llm_service


class GrokService:
    """AI 内容生成服务（保留原名以兼容现有代码）"""

    def __init__(self):
        self.llm = get_llm_service()

    def chat(self, prompt: str, temperature: float = None) -> str:
        return self.llm.chat(prompt, temperature=temperature)

    def generate_topic(self) -> str:
        prompt = """作为一位资深的科技博客编辑，请帮我生成一个当前最热门的 AI/科技领域博客选题。

要求：
1. 选题要有时效性，最好是近期热门话题
2. 选题要有深度，能够写出 2000 字以上的文章
3. 选题要适合技术博客读者，既要有技术深度又要通俗易懂
4. 只返回选题标题，不要其他内容
5. 标题要吸引人，包含关键词

请直接返回选题标题："""

        return self.chat(prompt).strip().strip('"').strip("'").strip()

    def search_latest_info(self, topic: str) -> str:
        prompt = f"""请搜索并总结关于"{topic}"的最新信息。

要求：
1. 提供该主题的最新进展和关键信息
2. 列出重要的技术细节或数据
3. 如有相关人物或公司，请一并说明
4. 整理成结构化的要点形式
5. 确保信息准确可靠

请整理关键信息："""

        return self.chat(prompt)

    def generate_article(self, topic: str, research: str) -> Dict:
        prompt = f"""请根据以下主题和研究资料，撰写一篇高质量的科技博客文章。

主题：{topic}

研究资料：
{research}

要求：
1. 文章字数不少于 2000 字
2. 使用标准 Markdown 格式
3. 包含 H1 主标题、H2 章节标题、H3 小节标题
4. 内容结构清晰，逻辑连贯
5. 在适当位置插入 [插图] 标记（每个 H2 章节后插入一个）
6. 包含引言、正文（多个章节）、总结
7. 使用列表、代码块等丰富排版
8. 语言专业但不晦涩，适合技术博客读者

请输出以下 JSON 格式（不要包含 markdown 代码块标记）：

{{
"title": "文章标题",
"summary": "文章摘要（100字左右）",
"category": "文章分类（如：人工智能、前端开发、后端技术等）",
"tags": ["标签1", "标签2", "标签3"],
"content_markdown": "完整的 Markdown 文章内容"
}}"""

        response = self.chat(prompt, temperature=0.8)

        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            raise RuntimeError("无法解析生成的文章JSON")

    def generate_cover_prompt(self, title: str, summary: str) -> str:
        prompt = f"""根据以下文章信息，生成一个用于 AI 绘画的封面图片提示词。

文章标题：{title}
文章摘要：{summary}

要求：
1. 提示词用于生成科技风格的封面图
2. 深色背景，现代感强
3. 无文字、无水印
4. 高品质、专业感
5. 适合作为博客文章封面
6. 提示词使用英文，便于 AI 绘画工具理解
7. 提示词要详细，包含风格、色调、构图等要素

请直接返回图片生成提示词（英文）："""

        cover_prompt = self.chat(prompt, temperature=0.9).strip()
        base_style = config.COVER_IMAGE_STYLE
        return f"{cover_prompt}. {base_style}"

    def generate_section_image_prompt(self, section_title: str, section_content: str) -> str:
        prompt = f"""根据以下章节内容，生成一个用于 AI 绘画的插图提示词。

章节标题：{section_title}
章节内容：{section_content[:500]}...

要求：
1. 提示词用于生成章节配图
2. 风格与文章整体一致（科技感、现代）
3. 能够直观表达章节主题
4. 无文字、无水印
5. 提示词使用英文

请直接返回图片生成提示词（英文）："""

        return self.chat(prompt, temperature=0.9).strip()


_grok_service = None


def get_grok_service() -> GrokService:
    global _grok_service
    if _grok_service is None:
        _grok_service = GrokService()
    return _grok_service
