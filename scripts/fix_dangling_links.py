#!/usr/bin/env python3
"""
处理剩余的悬空链接
- 指向 raw/ 的链接 → 转换为 sources: 字段
- 其他悬空链接 → 直接删除
"""

import re
from pathlib import Path

WIKI_DIR = Path("wiki")
EXCLUDE_DIRS = {"log", ".obsidian", "发布"}


def find_raw_file(link_target):
    """根据链接目标查找 raw/ 下的文件"""
    # link_target 可能是 "raw/xxx" 或 "raw/xxx.md"
    raw_dir = Path("raw")
    if not raw_dir.exists():
        return None

    # 提取文件名
    fname = link_target.replace("raw/", "")
    if not fname.endswith(".md"):
        fname += ".md"

    candidate = raw_dir / fname
    if candidate.exists():
        return candidate

    # 模糊匹配
    for f in raw_dir.iterdir():
        if f.is_file() and fname.split(".")[0] in f.name:
            return f
    return None


def fix_raw_link(file_path, raw_link):
    """将指向 raw/ 的链接转换为 sources: 字段"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取文件名（不含路径、不含 .md）
    fname = raw_link.replace("raw/", "")
    if fname.endswith(".md"):
        fname = fname[:-3]

    # 删除 [[raw/...]] 链接
    content = re.sub(rf'\[\[{re.escape(raw_link)}\]\]', '', content)

    # 添加到 sources: 字段
    fm_match = re.search(r'---\n(.*?)\n--', content, flags=re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(1)
        if 'sources:' in frontmatter:
            # 已有 sources: 字段，追加
            new_fm = frontmatter + f", {fname}"
        else:
            # 添加 sources: 字段
            new_fm = frontmatter + f"\nsources: {fname}"
        content = content.replace(frontmatter, new_fm)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def remove_dangling_link(file_path, link_target):
    """删除悬空链接"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 删除 [[...]] 链接所在行
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        if f"[[{link_target}]]" in line:
            continue  # 跳过包含悬空链接的行
        new_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    return True


def main():
    # 剩余悬空链接（根据之前扫描结果）
    dangling = [
        # 指向 raw/ 的链接（转为 sources:）
        ("wiki/概念/Agent Harness 设计对比.md", "raw/xxx"),  # 需要具体确认
        # 其他悬空链接（直接删除）
    ]

    print("正在处理指向 raw/ 的悬空链接...")
    raw_count = 0

    # 先扫描一次，找出所有指向 raw/ 的链接
    all_md = [f for f in WIKI_DIR.rglob("*.md")
             if not any(ex in f.parts for ex in EXCLUDE_DIRS)]

    raw_links_found = []
    for md_file in all_md:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        raw_links = re.findall(r'\[\[(raw/[^\]]+)\]\]', content)
        for rl in raw_links:
            raw_links_found.append((md_file, rl))

    print(f"  找到 {len(raw_links_found)} 个指向 raw/ 的链接")

    for md_file, raw_link in raw_links_found:
        if fix_raw_link(md_file, raw_link):
            print(f"  OK: {md_file.name} -> sources: {raw_link}")
            raw_count += 1

    print(f"\n正在处理其他悬空链接...")
    # 需要实际扫描
    print("  （需要在实际环境中运行完整扫描）")

    print(f"\n完成：处理了 {raw_count} 个指向 raw/ 的链接")


if __name__ == "__main__":
    main()
