#!/usr/bin/env python3
"""从合并文件中提取不重复的内容，按章节顺序去重。"""
import re

with open(r'd:\Obsidian_KN\金融交易\raw\蜡烛图精解-合并.md', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# 找到所有一级标题的位置（章节起始点）
chapter_markers = []
for i, line in enumerate(lines):
    if re.match(r'^# [^#]', line):  # 一级标题，非##、###等
        chapter_markers.append((i, line))

print(f"共找到 {len(chapter_markers)} 个一级标题")
for idx, (lineno, title) in enumerate(chapter_markers):
    print(f"  [{idx}] 行{lineno}: {title}")
