"""
文章数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class ArticleStatus(Enum):
    """文章状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class Article:
    """文章实体类"""
    title: str = ""
    summary: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    content_markdown: str = ""
    slug: str = ""
    cover_url: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    notion_page_id: Optional[str] = None
    notion_page_url: Optional[str] = None
    blocks: List[Dict[str, Any]] = field(default_factory=list)

    def to_notion_properties(self) -> Dict[str, Any]:
        """转换为 Notion 页面属性"""
        # 确保 status 是 select 类型
        status_value = "Published" if self.status == ArticleStatus.PUBLISHED else "Draft"
        
        # 确保 category 是 select 类型，如果为空则设为默认值
        category_value = self.category if self.category else "技术"
        
        return {
            "title": {
                "title": [{"text": {"content": self.title}}]
            },
            "type": {
                "select": {"name": "Post"}
            },
            "status": {
                "select": {"name": status_value}
            },
            "summary": {
                "rich_text": [{"text": {"content": self.summary}}]
            },
            "category": {
                "select": {"name": category_value}
            },
            "tags": {
                "multi_select": [{"name": tag} for tag in self.tags]
            },
            "slug": {
                "rich_text": [{"text": {"content": self.slug}}]
            },
            "date": {
                "date": {"start": self.created_at.strftime("%Y-%m-%d")}
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """从字典创建文章对象"""
        article = cls(
            title=data.get('title', ''),
            summary=data.get('summary', ''),
            category=data.get('category', ''),
            tags=data.get('tags', []),
            content_markdown=data.get('content_markdown', ''),
            slug=data.get('slug', ''),
            cover_url=data.get('cover_url'),
        )
        if 'status' in data:
            article.status = ArticleStatus(data.get('status'))
        return article

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'summary': self.summary,
            'category': self.category,
            'tags': self.tags,
            'content_markdown': self.content_markdown,
            'slug': self.slug,
            'cover_url': self.cover_url,
            'status': self.status.value,
            'notion_page_id': self.notion_page_id,
            'notion_page_url': self.notion_page_url,
        }

    @property
    def word_count(self) -> int:
        """计算文章字数"""
        return len(self.content_markdown)
