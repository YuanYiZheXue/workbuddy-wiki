#!/usr/bin/env python3
"""
将多个 epub 文件提取内容并合并为一个 Markdown 文件。
epub 是 zip 格式，解压后读取 OEBPS 目录下的 HTML/XHTML 内容。
"""

import zipfile
import os
import re
from pathlib import Path
from html.parser import HTMLParser

class HTMLToMarkdown(HTMLParser):
    """简易 HTML -> Markdown 转换器，专注保留正文结构。"""
    def __init__(self):
        super().__init__()
        self.result = []
        self.current_tag = []
        self.skip_tags = {'script', 'style', 'nav', 'head'}
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in self.skip_tags:
            self.skip_depth += 1
            return
        if self.skip_depth > 0:
            return
        if tag in ('h1', 'h2', 'h3', 'h4'):
            level = int(tag[1])
            self.current_tag.append(('#', level))
        elif tag == 'p':
            self.current_tag.append(('p', None))
        elif tag == 'br':
            self.result.append('\n')
        elif tag == 'b' or tag == 'strong':
            self.result.append('**')
        elif tag == 'i' or tag == 'em':
            self.result.append('*')
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            if src:
                self.result.append(f'![{alt}]({src})')

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip_depth -= 1
            return
        if self.skip_depth > 0:
            return
        if tag in ('h1', 'h2', 'h3', 'h4'):
            content = ''.join(self.result)
            level = int(tag[1])
            prefix = '#' * level
            self.result = [f'\n{prefix} {content.strip()}\n\n']
        elif tag == 'b' or tag == 'strong':
            self.result.append('**')
        elif tag == 'i' or tag == 'em':
            self.result.append('*')

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        text = data.strip()
        if text:
            self.result.append(text)

    def get_markdown(self):
        md = ''.join(self.result)
        # 清理多余空行
        md = re.sub(r'\n{3,}', '\n\n', md)
        return md.strip()


def find_content_files(epub_path):
    """解压 epub，找到所有内容 HTML 文件，按阅读顺序排列。"""
    content_files = []
    with zipfile.ZipFile(epub_path, 'r') as zf:
        names = zf.namelist()
        # 找 OEBPS 或类似目录下的 HTML 文件
        html_files = [n for n in names if n.endswith(('.html', '.xhtml', '.htm')) and 'OEBPS' in n]
        if not html_files:
            html_files = [n for n in names if n.endswith(('.html', '.xhtml', '.htm'))]
        # 尝试按文件名排序（通常 001, 002...）
        html_files.sort()
        for hf in html_files:
            with zf.open(hf) as f:
                content = f.read().decode('utf-8', errors='ignore')
                content_files.append((hf, content))
    return content_files


def merge_epubs(epub_paths, output_path):
    """合并多个 epub 的内容到一个 Markdown 文件。"""
    all_markdown = []
    for epub_path in epub_paths:
        print(f"处理: {os.path.basename(epub_path)}")
        try:
            html_files = find_content_files(epub_path)
            for filepath, html_content in html_files:
                parser = HTMLToMarkdown()
                parser.feed(html_content)
                md = parser.get_markdown()
                if md:
                    all_markdown.append(md)
        except Exception as e:
            print(f"  错误: {e}")

    combined = '\n\n---\n\n'.join(all_markdown)
    # 写文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# 蜡烛图精解：股票和期货交易的永恒技术（典藏版）\n\n")
        f.write(combined)
    print(f"\n合并完成: {output_path}")
    print(f"总字符数: {len(combined)}")


if __name__ == '__main__':
    base = r"d:\Obsidian_KN\金融交易\raw"
    epub_files = [
        os.path.join(base, "蜡烛图精解： 股票和期货交易的永恒技术（典藏版） ( etc.) (Z-Library).epub"),
        os.path.join(base, "蜡烛图精解： 股票和期货交易的永恒技术（典藏版） ( etc.) (Z-Library) 1.epub"),
        os.path.join(base, "蜡烛图精解： 股票和期货交易的永恒技术（典藏版） ( etc.) (Z-Library) 2.epub"),
        os.path.join(base, "蜡烛图精解： 股票和期货交易的永恒技术（典藏版） ( etc.) (Z-Library) 3.epub"),
    ]
    output = os.path.join(base, "蜡烛图精解-合并.md")
    merge_epubs(epub_files, output)
