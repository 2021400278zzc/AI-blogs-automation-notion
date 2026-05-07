"""
博客控制器 - 核心业务逻辑
"""

import time
from typing import Optional, List, Dict, Any

from models.article import Article, ArticleStatus
from services.grok_service import get_grok_service
from services.notion_service import get_notion_service, image_block
from services.image_service import get_image_service
from utils.markdown_parser import MarkdownParser
from utils.slug_generator import generate_slug
from views.console_view import ConsoleView


class BlogController:
    """博客控制器 - 管理博客生成和发布的完整流程"""

    def __init__(self):
        self.grok = get_grok_service()
        self.notion = get_notion_service()
        self.image_service = get_image_service()
        self.parser = MarkdownParser()
        self.view = ConsoleView()

    def generate_topic(self) -> str:
        """
        生成博客选题

        Returns:
            选题标题
        """
        self.view.print_step(1, 7, "自动选题")
        topic = self.grok.generate_topic()
        self.view.print_success(f"选定主题: {topic}")
        return topic

    def research_topic(self, topic: str) -> str:
        """
        搜索主题相关信息

        Args:
            topic: 主题

        Returns:
            研究资料
        """
        self.view.print_step(2, 7, "搜索最新信息")
        research = self.grok.search_latest_info(topic)
        self.view.print_success(f"获取研究资料: {len(research)} 字符")
        return research

    def generate_article(self, topic: str, research: str) -> Article:
        """
        生成文章

        Args:
            topic: 主题
            research: 研究资料

        Returns:
            文章对象
        """
        self.view.print_step(3, 7, "生成文章")
        article_data = self.grok.generate_article(topic, research)

        article = Article.from_dict(article_data)
        article.status = ArticleStatus.GENERATING
        article.slug = generate_slug(article.title)

        self.view.print_success("文章生成完成")
        self.view.print_info(f"标题: {article.title}")
        self.view.print_info(f"分类: {article.category}")
        self.view.print_info(f"标签: {', '.join(article.tags)}")

        return article

    def generate_cover(self, article: Article) -> Optional[str]:
        """
        生成文章封面

        Args:
            article: 文章对象

        Returns:
            封面图片 URL 或 None
        """
        self.view.print_step(4, 7, "生成封面图片")

        try:
            image_info = self.image_service.generate_cover_image(
                article.title,
                article.summary
            )

            if image_info and image_info.is_ready:
                article.cover_url = image_info.url
                self.view.print_success(f"封面图片: {image_info.url}")
                return image_info.url
            else:
                self.view.print_warning("封面图片生成失败，继续发布...")
                return None
        except Exception as e:
            self.view.print_warning(f"封面图片生成失败: {e}，继续发布...")
            return None

    def parse_markdown(self, article: Article) -> List[Dict]:
        """
        解析 Markdown 为 Notion Block

        Args:
            article: 文章对象

        Returns:
            Block 列表
        """
        self.view.print_step(5, 7, "解析 Markdown")
        blocks = self.parser.parse(article.content_markdown)
        article.blocks = blocks
        self.view.print_success(f"解析完成: {len(blocks)} 个 Block")
        return blocks

    def inject_images(self, article: Article) -> List[Dict]:
        """
        注入图片到 Block 列表

        Args:
            article: 文章对象

        Returns:
            处理后的 Block 列表
        """
        self.view.print_step(6, 7, "注入插图")

        new_blocks = []
        image_count = 0

        # 如果文章blocks中包含插图标记，尝试生成图片
        for i, block in enumerate(article.blocks):
            if block.get("type") == "IMAGE_PLACEHOLDER":
                # 获取上下文生成图片
                section_context = self._get_section_context(article.blocks, i)
                prompt = f"Technology illustration about {section_context}"

                # 尝试生成图片
                try:
                    image_url = self.image_service._generate_image(
                        prompt,
                        f"section_{image_count}"
                    )
                    image_count += 1

                    if image_url:
                        new_blocks.append(image_block(image_url))
                except:
                    # 如果图片生成失败，跳过这个图片
                    pass  # 不添加图片块，直接跳过
            else:
                new_blocks.append(block)

        article.blocks = new_blocks
        self.view.print_success(f"插图注入完成 ({image_count} 张)")
        return new_blocks

    def publish_to_notion(self, article: Article) -> Optional[str]:
        """
        发布文章到 Notion

        Args:
            article: 文章对象

        Returns:
            文章 URL 或 None
        """
        self.view.print_step(7, 7, "发布到 Notion")

        try:
            # 创建页面
            page = self.notion.create_page(article)

            # 添加内容块
            self.notion.append_blocks(page['id'], article.blocks)

            article.status = ArticleStatus.PUBLISHED
            article.notion_page_id = page['id']
            article.notion_page_url = page['url']

            self.view.print_publish_success(page['url'])
            return page['url']

        except Exception as e:
            article.status = ArticleStatus.FAILED
            self.view.print_error(f"发布失败: {e}")
            raise

    def run_full_flow(self, topic: str = None, manual_content: Dict = None) -> Optional[str]:
        """
        运行完整的自动化流程

        Args:
            topic: 可选的指定主题
            manual_content: 可选的手动指定内容

        Returns:
            发布的文章 URL 或 None
        """
        try:
            self.view.print_header("🚀 开始自动化博客生成流程")

            # 步骤 1-3: 选题、搜索、生成文章
            if manual_content:
                self.view.print_info("使用手动指定的内容")
                article = Article.from_dict(manual_content)
                article.slug = generate_slug(article.title)
            else:
                if not topic:
                    topic = self.generate_topic()
                research = self.research_topic(topic)
                article = self.generate_article(topic, research)

            # 步骤 4: 生成封面
            self.generate_cover(article)

            # 步骤 5: 解析 Markdown
            self.parse_markdown(article)

            # 步骤 6: 注入图片
            self.inject_images(article)

            # 步骤 7: 发布到 Notion
            return self.publish_to_notion(article)

        except Exception as e:
            self.view.print_error(f"流程执行失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def preview_article(self, topic: str = None) -> Optional[Article]:
        """
        预览文章（仅生成，不发布）

        Args:
            topic: 可选的主题

        Returns:
            文章对象或 None
        """
        try:
            if not topic:
                topic = self.grok.generate_topic()
                self.view.print_info(f"选定主题: {topic}")

            research = self.grok.search_latest_info(topic)
            article = self.grok.generate_article(topic, research)

            return Article.from_dict(article)

        except Exception as e:
            self.view.print_error(f"生成失败: {e}")
            return None

    def _get_section_context(self, blocks: List[Dict], index: int) -> str:
        """获取当前位置的上下文信息"""
        # 向前查找最近的标题
        for i in range(index - 1, -1, -1):
            block_type = blocks[i].get("type", "")
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                rich_text = blocks[i].get(block_type, {}).get("rich_text", [])
                if rich_text:
                    return rich_text[0].get("text", {}).get("content", "")
        return "blog content"
