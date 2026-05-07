#!/usr/bin/env python3
"""
AI 自动化博客系统主入口 (MVC架构)

完整流程：
1. 自动选题
2. 搜索最新信息
3. 生成文章
4. 生成封面图片
5. 上传到 Notion
"""

import sys
import time
from datetime import datetime
from typing import Optional

from controllers.blog_controller import BlogController
from models.article import Article
from views.console_view import ConsoleView
from views.article_view import ArticleView


def interactive_mode():
    """交互模式"""
    view = ConsoleView()
    controller = BlogController()
    article_view = ArticleView()

    while True:
        view.show_menu()
        choice = view.get_input("请选择 (1-4): ")

        if choice == "1":
            controller.run_full_flow()

        elif choice == "2":
            topic = view.get_input("请输入主题: ")
            if topic:
                controller.run_full_flow(topic=topic)
            else:
                view.print_error("主题不能为空")

        elif choice == "3":
            topic = view.get_input("请输入主题（留空自动生成）: ")
            article = controller.preview_article(topic)

            if article:
                view.print_article_summary(article)
                view.print_article_preview(article.content_markdown)

                if view.confirm("是否保存到文件"):
                    filename = article_view.save_to_file(article)
                    view.print_success(f"已保存到: {filename}")

        elif choice == "4":
            view.print_info("再见！")
            break

        print("\n" + "-" * 50)


def demo_mode():
    """演示模式：使用示例内容发布文章"""
    view = ConsoleView()
    view.print_header("🎬 演示模式")

    # 示例文章内容
    sample_content = {
        "title": "人工智能在2025年的发展趋势",
        "summary": "本文探讨了2025年AI领域的最新发展趋势，包括大语言模型、多模态AI和边缘计算等热点话题。",
        "category": "人工智能",
        "tags": ["AI", "人工智能", "技术趋势", "机器学习"],
        "content_markdown": """# 人工智能在2025年的发展趋势

## 引言

人工智能正在以前所未有的速度发展。2025年，我们见证了AI技术在多个领域的突破性进展。

[插图]

## 大语言模型的演进

大语言模型（LLM）在过去一年取得了显著进步：

- 模型规模持续扩大，参数量达到新高度
- 多语言支持能力显著增强
- 推理能力和逻辑思维能力大幅提升
- 代码生成和调试能力更加成熟

### 主要突破

1. **上下文长度扩展**：支持更长的上下文窗口
2. **多模态融合**：文本、图像、音频的统一理解
3. **效率优化**：推理速度和成本持续优化

[插图]

## 多模态AI的崛起

多模态AI成为2025年最受关注的领域之一：

> 多模态AI能够理解并生成文本、图像、音频和视频内容，开启了人机交互的新纪元。

主要应用场景包括：
- 智能内容创作
- 自动化设计辅助
- 教育和培训
- 医疗影像分析

[插图]

## 边缘计算与AI的结合

边缘AI在2025年迎来了爆发式增长：

| 特性 | 云端AI | 边缘AI |
|------|--------|--------|
| 延迟 | 较高 | 低 |
| 隐私 | 需传输数据 | 本地处理 |
| 成本 | 高 | 较低 |
| 可用性 | 依赖网络 | 离线可用 |

### 应用案例

```python
# 边缘AI推理示例
def edge_inference(model, input_data):
    # 本地处理，无需云端
    result = model.predict(input_data)
    return result
```

[插图]

## AI在行业的应用

### 医疗健康
- 精准诊断和治疗方案推荐
- 药物研发加速
- 个性化健康管理

### 金融服务
- 智能风控和反欺诈
- 自动化投资顾问
- 智能客服升级

### 制造业
- 预测性维护
- 质量检测自动化
- 供应链优化

[插图]

## 挑战与机遇

[!NOTE] AI发展面临的主要挑战包括数据隐私、算法偏见、就业影响等问题。

机遇同样巨大：
- 生产力的大幅提升
- 创新的加速
- 个性化服务的普及
- 科学研究的新突破

## 未来展望

展望2026年及以后：

1. **通用人工智能（AGI）**的研究将持续推进
2. **具身智能**将在机器人领域取得突破
3. **AI安全和对齐**成为核心议题
4. **绿色AI**关注能源效率

---

## 总结

2025年是AI发展的关键一年。技术的快速进步正在重塑我们的生活和工作方式。作为开发者和技术爱好者，我们应该积极拥抱变化，同时关注AI发展带来的社会影响。

未来已来，让我们共同见证AI的下一个黄金时代！
"""
    }

    controller = BlogController()
    controller.run_full_flow(manual_content=sample_content)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="AI 自动化博客系统 (MVC架构)")
    parser.add_argument(
        "--topic", "-t",
        type=str,
        help="指定文章主题"
    )
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="运行演示模式（使用示例内容）"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="运行交互模式"
    )

    args = parser.parse_args()

    view = ConsoleView()
    view.print_header("🤖 AI 自动化博客系统 v2.0 (MVC架构)")

    if args.demo:
        demo_mode()
    elif args.interactive:
        interactive_mode()
    elif args.topic:
        controller = BlogController()
        controller.run_full_flow(topic=args.topic)
    else:
        # 默认运行完整流程
        controller = BlogController()
        controller.run_full_flow()


if __name__ == "__main__":
    main()
