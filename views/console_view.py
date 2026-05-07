"""
控制台视图 - 负责控制台输出
"""

import sys
import os
from typing import Dict, Any, List, Optional
from models.article import Article

# 处理Windows控制台编码问题
if sys.platform.startswith('win') and sys.version_info >= (3, 10):
    # Python 3.10+ 支持reconfigure
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

class ConsoleView:
    """控制台视图"""

    @staticmethod
    def print_header(text: str):
        """打印标题"""
        print("\n" + "=" * 50)
        # 处理可能的编码问题
        try:
            print(text)
        except UnicodeEncodeError:
            # 如果有编码问题，移除emoji并使用纯文本
            clean_text = text.replace("🤖", "AI自动化博客系统")
            clean_text = clean_text.replace("🚀", "自动化博客系统")
            clean_text = clean_text.replace("🎬", "演示模式")
            clean_text = clean_text.replace("🎮", "交互模式")
            print(clean_text)
        print("=" * 50)

    @staticmethod
    def print_step(step_num: int, total: int, text: str):
        """打印步骤信息"""
        try:
            print(f"\n📝 步骤 {step_num}/{total}: {text}")
        except UnicodeEncodeError:
            print(f"\n步骤 {step_num}/{total}: {text}")

    @staticmethod
    def print_success(text: str):
        """打印成功信息"""
        try:
            print(f"✅ {text}")
        except UnicodeEncodeError:
            print(f"[成功] {text}")

    @staticmethod
    def print_warning(text: str):
        """打印警告信息"""
        try:
            print(f"⚠️  {text}")
        except UnicodeEncodeError:
            print(f"[警告] {text}")

    @staticmethod
    def print_error(text: str):
        """打印错误信息"""
        try:
            print(f"❌ {text}")
        except UnicodeEncodeError:
            print(f"[错误] {text}")

    @staticmethod
    def print_info(text: str):
        """打印普通信息"""
        print(f"  {text}")

    @staticmethod
    def print_article_summary(article: Article):
        """打印文章摘要信息"""
        print("\n" + "-" * 50)
        print("文章信息")
        print("-" * 50)
        print(f"标题: {article.title}")
        print(f"摘要: {article.summary}")
        print(f"分类: {article.category}")
        print(f"标签: {', '.join(article.tags)}")
        print(f"字数: {article.word_count}")
        print("-" * 50)

    @staticmethod
    def print_article_preview(content: str, max_length: int = 2000):
        """打印文章预览"""
        print("\n" + "=" * 50)
        print("文章内容预览")
        print("=" * 50)
        print(content[:max_length])
        if len(content) > max_length:
            print("\n... (内容已截断)")
        print("=" * 50)

    @staticmethod
    def print_blocks_info(count: int):
        """打印块信息"""
        try:
            print(f"✅ 解析完成: {count} 个 Block")
        except UnicodeEncodeError:
            print(f"解析完成: {count} 个 Block")

    @staticmethod
    def print_publish_success(url: str):
        """打印发布成功信息"""
        print("\n" + "=" * 50)
        try:
            print("✅ 自动化流程完成！")
        except UnicodeEncodeError:
            print("自动化流程完成！")
        print(f"文章 URL: {url}")
        print("=" * 50)

    @staticmethod
    def show_menu():
        """显示交互菜单"""
        print("\n" + "=" * 50)
        try:
            print("🎮 交互模式")
        except UnicodeEncodeError:
            print("交互模式")
        print("=" * 50)
        print("1. 自动生成完整文章")
        print("2. 指定主题生成文章")
        print("3. 仅生成文章内容（不发布）")
        print("4. 退出")
        print("=" * 50)

    @staticmethod
    def get_input(prompt: str) -> str:
        """获取用户输入"""
        return input(f"\n{prompt}").strip()

    @staticmethod
    def confirm(prompt: str) -> bool:
        """确认提示"""
        choice = input(f"\n{prompt} (y/n): ").strip().lower()
        return choice == 'y'

    @staticmethod
    def print_progress(current: int, total: int, text: str = ""):
        """打印进度信息"""
        print(f"  [{current}/{total}] {text}")