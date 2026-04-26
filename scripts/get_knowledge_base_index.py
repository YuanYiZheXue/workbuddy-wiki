#!/usr/bin/env python3
"""
获取所有知识库的索引，构建全局视图
"""

import os
from pathlib import Path
import re
import yaml

# 知识库注册表
KNOWLEDGE_BASES = [
    "wiki",
    "哲学",
    "计算机",
    "数学"
]

def get_index(kb_name):
    """获取指定知识库的 index.md 内容"""
    index_path = Path(kb_name) / "index.md"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def parse_index(index_content):
    """解析 index.md，提取概念、实体、对比的页面路径"""
    result = {
        "概念": [],
        "实体": [],
        "对比": []
    }

    lines = index_content.split("\n")
    current_section = None

    for line in lines:
        # 识别 section（可能包含数量，如 "## 实体（7 个页面）"）
        if line.startswith("## "):
            if "概念" in line and "概念" not in line.split("概念")[1]:  # 避免匹配到 "相关概念"
                current_section = "概念"
            elif "实体" in line:
                current_section = "实体"
            elif "对比" in line:
                current_section = "对比"
            elif "来源" in line:
                current_section = None  # 来源摘要不需要解析
            else:
                current_section = None

        # 提取表格中的 Wikilink（格式：| [[页面路径]] | ... | 或 | [[页面路径|显示文本]] | ... |）
        if current_section and "| [[" in line:
            # 提取 [[...]] 中的内容
            matches = re.findall(r'\[\[([^\]]+)\]\]', line)
            for match in matches:
                # match 可能是 "页面路径|显示文本" 或 "页面路径"
                page_path = match.split("|")[0].strip()
                if page_path not in result[current_section]:
                    result[current_section].append(page_path)

    return result

def build_global_view():
    """构建全局视图"""
    global_view = {
        "概念": {},
        "实体": {},
        "对比": {}
    }

    for kb in KNOWLEDGE_BASES:
        index_content = get_index(kb)
        if index_content:
            parsed = parse_index(index_content)
            for category in ["概念", "实体", "对比"]:
                for page_path in parsed[category]:
                    if page_path not in global_view[category]:
                        global_view[category][page_path] = []
                    if kb not in global_view[category][page_path]:
                        global_view[category][page_path].append(kb)

    return global_view

def save_global_view(global_view, output_file="wiki/统筹/全局视图.yaml"):
    """保存全局视图到 YAML 文件"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(global_view, f, allow_unicode=True, default_flow_style=False)

    print(f"全局视图已保存到：{output_file}")

def main():
    global_view = build_global_view()
    save_global_view(global_view)

    # 打印统计信息
    for category in ["概念", "实体", "对比"]:
        count = len(global_view[category])
        multi_kb = sum(1 for v in global_view[category].values() if len(v) > 1)
        print(f"{category}：{count} 个页面，其中 {multi_kb} 个在多个知识库中")

if __name__ == "__main__":
    main()
