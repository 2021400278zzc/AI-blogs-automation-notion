"""
Markdown 解析器
将 Markdown 转换为 Notion Block 格式
"""

import re
from typing import List, Dict, Tuple, Optional
from services import notion_service as nc


class MarkdownParser:
    """Markdown 解析器"""

    def __init__(self):
        self.image_placeholders = []  # 记录 [插图] 位置

    def parse(self, markdown: str) -> List[Dict]:
        """
        解析 Markdown 为 Notion Block 列表

        Args:
            markdown: Markdown 文本

        Returns:
            Notion Block 列表
        """
        blocks = []
        lines = markdown.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 跳过空行
            if not stripped:
                i += 1
                continue

            # 代码块
            if stripped.startswith("```"):
                code_block, i = self._parse_code_block(lines, i)
                if code_block:
                    blocks.append(code_block)
                continue

            # 表格
            if "|" in stripped and i + 1 < len(lines) and "---" in lines[i + 1]:
                table_block, i = self._parse_table(lines, i)
                if table_block:
                    blocks.append(table_block)
                continue

            # H1
            if stripped.startswith("# "):
                blocks.append(nc.heading_1(stripped[2:].strip()))
                i += 1
                continue

            # H2
            if stripped.startswith("## "):
                blocks.append(nc.heading_2(stripped[3:].strip()))
                i += 1
                continue

            # H3
            if stripped.startswith("### "):
                blocks.append(nc.heading_3(stripped[4:].strip()))
                i += 1
                continue

            # 引用
            if stripped.startswith("> "):
                quote_text, i = self._parse_quote(lines, i)
                if quote_text:
                    blocks.append(nc.quote(quote_text))
                continue

            # 无序列表
            if stripped.startswith("- ") or stripped.startswith("* "):
                list_items, i = self._parse_unordered_list(lines, i)
                blocks.extend(list_items)
                continue

            # 有序列表
            if re.match(r'^\d+\.', stripped):
                list_items, i = self._parse_ordered_list(lines, i)
                blocks.extend(list_items)
                continue

            # 分割线
            if stripped == "---" or stripped == "***" or stripped == "___":
                blocks.append(nc.divider())
                i += 1
                continue

            # Callout
            if stripped.startswith("[!NOTE]") or stripped.startswith("[!TIP]"):
                icon = "💡"
                if "[WARNING]" in stripped:
                    icon = "⚠️"
                elif "[!IMPORTANT]" in stripped:
                    icon = "🔴"
                text = re.sub(r'\[!\w+\]', '', stripped).strip()
                blocks.append(nc.callout(text, icon))
                i += 1
                continue

            # 插图标记
            if stripped == "[插图]":
                blocks.append({"type": "IMAGE_PLACEHOLDER"})
                i += 1
                continue

            # 普通段落
            paragraph_text, i = self._parse_paragraph(lines, i)
            if paragraph_text:
                blocks.append(nc.paragraph(paragraph_text))

        return blocks

    def _parse_code_block(self, lines: List[str], start: int) -> Tuple[Optional[Dict], int]:
        """解析代码块"""
        line = lines[start].strip()
        match = re.match(r'^```(\w+)?', line)
        language = match.group(1) if match and match.group(1) else "plain text"

        code_lines = []
        i = start + 1

        while i < len(lines):
            if lines[i].strip() == "```":
                i += 1
                break
            code_lines.append(lines[i])
            i += 1

        code_content = "\n".join(code_lines)
        return nc.code_block(code_content, language), i

    def _parse_table(self, lines: List[str], start: int) -> Tuple[Optional[Dict], int]:
        """解析表格"""
        rows = []
        i = start

        while i < len(lines) and "|" in lines[i]:
            line = lines[i].strip()
            # 跳过分隔行
            if "---" in line and "|" in line:
                i += 1
                continue

            # 解析单元格
            cells = [cell.strip() for cell in line.split("|")]
            cells = [c for c in cells if c]  # 移除空单元格
            if cells:
                rows.append(cells)
            i += 1

        if rows:
            return nc.table_block(rows, has_header=True), i
        return None, start + 1

    def _parse_quote(self, lines: List[str], start: int) -> Tuple[Optional[str], int]:
        """解析引用块"""
        quote_lines = []
        i = start

        while i < len(lines) and lines[i].strip().startswith("> "):
            quote_lines.append(lines[i].strip()[2:])
            i += 1

        return "\n".join(quote_lines), i

    def _parse_unordered_list(self, lines: List[str], start: int) -> Tuple[List[Dict], int]:
        """解析无序列表"""
        items = []
        i = start

        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.startswith("- "):
                items.append(nc.bulleted_list_item(stripped[2:]))
            elif stripped.startswith("* "):
                items.append(nc.bulleted_list_item(stripped[2:]))
            elif not stripped:
                i += 1
                continue
            else:
                break
            i += 1

        return items, i

    def _parse_ordered_list(self, lines: List[str], start: int) -> Tuple[List[Dict], int]:
        """解析有序列表"""
        items = []
        i = start

        while i < len(lines):
            stripped = lines[i].strip()
            match = re.match(r'^\d+\.\s*(.+)', stripped)
            if match:
                items.append(nc.numbered_list_item(match.group(1)))
            elif not stripped:
                i += 1
                continue
            else:
                break
            i += 1

        return items, i

    def _parse_paragraph(self, lines: List[str], start: int) -> Tuple[str, int]:
        """解析段落（可能包含多行）"""
        para_lines = []
        i = start

        while i < len(lines):
            stripped = lines[i].strip()

            # 遇到特殊格式停止
            if not stripped or stripped.startswith("#") or stripped.startswith("- "):
                break
            if stripped.startswith("* ") or stripped.startswith("> "):
                break
            if re.match(r'^\d+\.', stripped):
                break
            if stripped.startswith("```") or stripped == "[插图]":
                break

            para_lines.append(stripped)
            i += 1

        return " ".join(para_lines), i

    def find_image_positions(self, blocks: List[Dict]) -> List[int]:
        """
        查找所有插图标记的位置

        Args:
            blocks: Block 列表

        Returns:
            插图标记的索引列表
        """
        positions = []
        for i, block in enumerate(blocks):
            if block.get("type") == "IMAGE_PLACEHOLDER":
                positions.append(i)
        return positions


def parse_markdown(markdown: str) -> List[Dict]:
    """
    便捷函数：解析 Markdown

    Args:
        markdown: Markdown 文本

    Returns:
        Notion Block 列表
    """
    parser = MarkdownParser()
    return parser.parse(markdown)
