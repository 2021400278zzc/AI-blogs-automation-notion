"""
Slug 生成工具
"""

import re
import time


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
