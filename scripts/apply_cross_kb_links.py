#!/usr/bin/env python3
"""
自动创建跨知识库链接
"""

import os
from pathlib import Path
import re

def extract_page_path(wikilink):
    """从 Wikilink 中提取页面路径"""
    if "|" in wikilink:
        return wikilink.split("[[")[1].split("|")[0].strip()
    else:
        return wikilink.split("[[")[1].split("]]")[0].strip()

def extract_display_text(wikilink):
    """从 Wikilink 中提取显示文本"""
    if "|" in wikilink:
        return wikilink.split("|")[1].split("]]")[0].strip()
    else:
        # 如果没有显示文本，使用页面名称
        page_path = wikilink.split("[[")[1].split("]]")[0].strip()
        return page_path.split("/")[-1].replace(".md", "")

def add_cross_kb_link_to_file(file_path, link, section="## 相关概念"):
    """
    在指定文件中添加跨知识库链接
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"文件不存在：{file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查链接是否已经存在
    if link in content:
        print(f"链接已存在：{link} 在 {file_path}")
        return False

    # 查找 section
    if section not in content:
        # 如果 section 不存在，添加到文件末尾
        content += f"\n{section}\n\n- {link}\n"
    else:
        # 如果 section 存在，在 section 后添加链接
        lines = content.split("\n")
        new_lines = []
        section_found = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == section:
                section_found = True
                # 查找下一个空行或非列表项
                for j in range(i+1, len(lines)):
                    if lines[j].strip() == "" or not lines[j].startswith("- "):
                        # 在空行或非列表项前插入链接
                        new_lines.append(f"- {link}")
                        break
                else:
                    # 如果到了文件末尾，直接添加
                    new_lines.append(f"- {link}")

        content = "\n".join(new_lines)

    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"已添加链接：{link} 到 {file_path}")
    return True

def apply_cross_kb_links(links_opportunities_yaml):
    """
    根据跨知识库链接机会，自动创建链接
    """
    import yaml

    # 读取链接机会
    with open(links_opportunities_yaml, "r", encoding="utf-8") as f:
        opportunities = yaml.safe_load(f)

    # 应用每个链接机会
    for opp in opportunities.get("跨知识库链接机会", []):
        source_page = opp["源页面"]
        target_page = opp["目标页面"]
        display_text = opp.get("显示文本", "")

        # 构建 Wikilink
        if display_text:
            link = f"[[{target_page}|{display_text}]]"
        else:
            link = f"[[{target_page}]]"

        # 在源页面中添加链接
        add_cross_kb_link_to_file(source_page, link)

        # 创建反向链接
        target_display_text = opp.get("反向显示文本", "")
        if target_display_text:
            reverse_link = f"[[{source_page}|{target_display_text}]]"
        else:
            reverse_link = f"[[{source_page}]]"

        # 在目标页面中添加反向链接
        add_cross_kb_link_to_file(target_page, reverse_link)

def main():
    # 假设 AI 生成的链接机会保存在这个文件中
    links_opportunities_yaml = "wiki/统筹/跨知识库链接机会.yaml"

    if not Path(links_opportunities_yaml).exists():
        print(f"文件不存在：{links_opportunities_yaml}")
        print("请先运行 generate_ai_prompt_cross_kb_links.py 生成 AI Prompt，然后让 AI 生成链接机会")
        return

    apply_cross_kb_links(links_opportunities_yaml)

if __name__ == "__main__":
    main()
