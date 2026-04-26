#!/usr/bin/env python3
"""正确提取第一份完整内容（截止到第二份#版权信息之前）。"""
with open(r'd:\Obsidian_KN\金融交易\raw\蜡烛图精解-合并.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找第二个"# 版权信息"的位置（第二份开始）
copyright_positions = []
for i, line in enumerate(lines):
    if line.strip() == '# 版权信息':
        copyright_positions.append(i)

print(f"找到 {len(copyright_positions)} 处 '# 版权信息'")
for p in copyright_positions:
    print(f"  行 {p}: {lines[p].strip()}")

if len(copyright_positions) >= 2:
    second_start = copyright_positions[1]
    print(f"\n第二份起始行: {second_start}")
    clean_lines = lines[:second_start]
else:
    print("未找到第二份，使用全文")
    clean_lines = lines

output_path = r'd:\Obsidian_KN\金融交易\raw\蜡烛图精解-去重版.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print(f"\n干净版本已写入: {output_path}")
print(f"行数: {len(clean_lines)}")

import re
h1_in_clean = [l.strip() for l in clean_lines if re.match(r'^# [^#]', l)]
print(f"一级标题数: {len(h1_in_clean)}")
for h in h1_in_clean:
    print(f"  {h}")
