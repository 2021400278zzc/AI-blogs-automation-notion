"""
Notion API 服务封装
属于 Model/Service 层
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from notion_client import Client as NotionClient

import config
from models.article import Article


class NotionService:
    """Notion 博客服务封装"""

    def __init__(self):
        self.client = NotionClient(auth=config.NOTION_TOKEN)
        self.database_id = config.NOTION_DATABASE_ID

    def create_page(self, article: Article) -> Dict[str, Any]:
        """
        创建博客文章页面

        Args:
            article: 文章实体对象

        Returns:
            创建的页面信息
        """
        properties = article.to_notion_properties()

        try:
            # 为处理SSL问题，添加SSL上下文配置
            import ssl
            import urllib3
            from notion_client import Client
            
            # 禁用SSL验证（仅用于测试环境，生产环境请谨慎使用）
            import os
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                cover={"external": {"url": article.cover_url}} if article.cover_url else None
            )
            article.notion_page_id = page['id']
            article.notion_page_url = page['url']
            return page
        except Exception as e:
            raise RuntimeError(f"Notion 页面创建失败: {e}")

    def append_blocks(self, page_id: str, blocks: List[Dict]):
        """
        分批添加内容块到页面

        Args:
            page_id: 页面 ID
            blocks: 内容块列表
        """
        # Notion API 限制每次最多 100 个块
        for i in range(0, len(blocks), config.BATCH_SIZE):
            batch = blocks[i:i + config.BATCH_SIZE]
            try:
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=batch
                )
            except Exception as e:
                raise RuntimeError(f"添加块失败: {e}")

    def get_page(self, page_id: str) -> Dict:
        """获取页面信息"""
        return self.client.pages.retrieve(page_id=page_id)

    def update_page(self, page_id: str, properties: Dict):
        """更新页面属性"""
        return self.client.pages.update(page_id=page_id, properties=properties)

    def delete_page(self, page_id: str):
        """归档页面（Notion API 不支持真正删除）"""
        return self.client.pages.update(
            page_id=page_id,
            archived=True
        )


# 辅助函数：创建各种块类型

def text_block(text: str) -> Dict:
    """创建文本块"""
    return {
        "object": "block",
        "type": "text",
        "text": {
            "content": text
        }
    }


def paragraph(text: str) -> Dict:
    """创建段落块"""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def heading_1(text: str) -> Dict:
    """创建 H1 标题"""
    return {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def heading_2(text: str) -> Dict:
    """创建 H2 标题"""
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def heading_3(text: str) -> Dict:
    """创建 H3 标题"""
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def bulleted_list_item(text: str) -> Dict:
    """创建无序列表项"""
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def numbered_list_item(text: str) -> Dict:
    """创建有序列表项"""
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def quote(text: str) -> Dict:
    """创建引用块"""
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def code_block(text: str, language: str = "plain text") -> Dict:
    """创建代码块"""
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "language": language
        }
    }


def image_block(url: str, caption: str = "") -> Dict:
    """创建图片块"""
    block = {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {"url": url}
        }
    }
    if caption:
        block["image"]["caption"] = [{"type": "text", "text": {"content": caption}}]
    return block


def callout(text: str, icon: str = "💡") -> Dict:
    """创建 Callout 块"""
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"emoji": icon}
        }
    }


def divider() -> Dict:
    """创建分隔线"""
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }


def table_block(rows: List[List[str]], has_header: bool = True) -> Dict:
    """
    创建表格块

    Args:
        rows: 表格行数据，每行是单元格列表
        has_header: 是否有表头

    Returns:
        表格块
    """
    if not rows:
        return None

    table_width = len(rows[0])
    table_rows = []

    for row in rows:
        table_rows.append({
            "type": "table_row",
            "table_row": {
                "cells": [[{"type": "text", "text": {"content": cell}}] for cell in row]
            }
        })

    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": has_header,
            "has_row_header": False,
            "children": table_rows
        }
    }


def generate_slug(title: str) -> str:
    """
    生成文章 slug

    Args:
        title: 文章标题

    Returns:
        生成的 slug
    """
    # 转换为小写，替换特殊字符为连字符
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    # 添加时间戳保证唯一性
    timestamp = str(int(time.time()))
    return f"{slug}-{timestamp}"


# 单例实例
_notion_service = None


def get_notion_service() -> NotionService:
    """获取 NotionService 单例"""
    global _notion_service
    if _notion_service is None:
        _notion_service = NotionService()
    return _notion_service
