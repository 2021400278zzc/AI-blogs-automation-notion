"""
文章视图 - 负责文章展示相关
"""

import os
from datetime import datetime
from typing import Dict, Any
from models.article import Article


class ArticleView:
    """文章视图"""

    @staticmethod
    def format_article_markdown(article: Article) -> str:
        """
        将文章格式化为 Markdown 字符串

        Args:
            article: 文章对象

        Returns:
            Markdown 格式字符串
        """
        lines = [
            f"# {article.title}",
            "",
            f"**摘要:** {article.summary}",
            "",
            f"**分类:** {article.category}",
            "",
            f"**标签:** {', '.join(article.tags)}",
            "",
            f"**日期:** {article.created_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            article.content_markdown
        ]
        return "\n".join(lines)

    @staticmethod
    def save_to_file(article: Article, filename: str = None) -> str:
        """
        保存文章到文件

        Args:
            article: 文章对象
            filename: 文件名（可选）

        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = int(datetime.now().timestamp())
            safe_title = "".join(c if c.isalnum() else "_" for c in article.title[:30])
            filename = f"article_{safe_title}_{timestamp}.md"

        content = ArticleView.format_article_markdown(article)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        return filename

    @staticmethod
    def to_dict(article: Article) -> Dict[str, Any]:
        """
        将文章转换为字典

        Args:
            article: 文章对象

        Returns:
            字典格式
        """
        return {
            'title': article.title,
            'summary': article.summary,
            'category': article.category,
            'tags': article.tags,
            'content_markdown': article.content_markdown,
            'slug': article.slug,
            'cover_url': article.cover_url,
            'word_count': article.word_count,
            'status': article.status.value,
            'created_at': article.created_at.isoformat(),
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'notion_page_url': article.notion_page_url,
        }
