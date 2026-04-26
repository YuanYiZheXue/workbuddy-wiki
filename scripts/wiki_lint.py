#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wiki Lint 工具 - 健康检查
按 workbuddy-wiki-schema.md Lint 章节规范检查
结果输出到 lint_report.txt
"""

import os
import re
from pathlib import Path

WIKI_ROOT = r"d:\Obsidian_KN\哲学思想\wiki"

VALID_FIELDS = {
    "title", "sources", "tags", "type", "date",
    "created", "updated", "author", "status", "summary"
}

def read_file_safe(fp):
    for enc in ("utf-8", "gbk", "cp936"):
        try:
            with open(fp, "r", encoding=enc) as f:
                return f.read()
        except:
            continue
    return ""

def get_frontmatter(body_text):
    if not body_text.startswith("---"):
        return {}, body_text
    parts = body_text.split("---", 2)
    if len(parts) < 3:
        return {}, body_text
    fm_text = parts[1].strip()
    body = parts[2].strip()
    fm = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm, body

def collect_all_pages(wiki_root):
    """收集所有现存页面名（不含扩展名，含相对路径形式）"""
    pages = set()
    for root, _, fnames in os.walk(wiki_root):
        # 跳过隐藏目录
        dirs = [d for d in os.listdir(root) if not d.startswith(".")]
        for fn in fnames:
            if fn.endswith(".md"):
                full = os.path.join(root, fn)
                # 不含扩展名
                pages.add(fn[:-3])
                # 相对路径形式（用 /）
                rel = os.path.relpath(full, wiki_root)
                rel = rel.replace("\\", "/")[:-3]
                pages.add(rel)
    return pages

def extract_wikilinks(body):
    """提取 [[页面名]] 或 [[页面名|显示文本]]"""
    pattern = r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]'
    return re.findall(pattern, body)

def check1_frontmatter_spelling(md_files, report):
    report.write("=" * 60 + "\n")
    report.write("[检查1] Frontmatter 拼写检查\n")
    report.write("=" * 60 + "\n")
    issues = []
    for fp in md_files:
        text = read_file_safe(fp)
        fm, _ = get_frontmatter(text)
        if not fm:
            continue
        for key in fm:
            if key not in VALID_FIELDS:
                suggestion = ""
                if key in ("sourses", "sourse", "source"):
                    suggestion = "(应为 sources:)"
                elif key in ("tgas", "tag", "tags_"):
                    suggestion = "(应为 tags:)"
                elif key in ("tpye", "tyep", "ype"):
                    suggestion = "(应为 type:)"
                msg = f"  [拼写] {os.path.basename(fp)} -- 未知字段 '{key}' {suggestion}\n"
                issues.append(msg)
    if issues:
        for i in issues:
            report.write(i)
        report.write(f"\n  共 {len(issues)} 个拼写问题\n")
    else:
        report.write("  [OK] 所有 frontmatter 字段拼写正确\n")
    return issues

def check2_dangling_links(md_files, wiki_root, report):
    report.write("\n" + "=" * 60 + "\n")
    report.write("[检查2] 悬空内部链接\n")
    report.write("=" * 60 + "\n")
    issues = []
    all_pages = collect_all_pages(wiki_root)
    for fp in md_files:
        text = read_file_safe(fp)
        _, body = get_frontmatter(text)
        links = extract_wikilinks(body)
        for link in links:
            link = link.strip()
            found = False
            for page in all_pages:
                if page.endswith(link) or link.endswith(page) or page == link:
                    found = True
                    break
            if not found:
                msg = f"  [悬空] {os.path.basename(fp)} -- 链接 [[{link}]] 无对应页面\n"
                issues.append(msg)
    if issues:
        for i in issues:
            report.write(i)
        report.write(f"\n  共 {len(issues)} 个悬空链接\n")
    else:
        report.write("  [OK] 所有内部链接均有对应页面\n")
    return issues

def check5_index_quality(index_path, report):
    report.write("\n" + "=" * 60 + "\n")
    report.write("[检查5] index.md 简介质量\n")
    report.write("=" * 60 + "\n")
    issues = []
    text = read_file_safe(index_path)
    # 查找 | - **名称** — 简介 | 形式的条目
    pattern = r'\|\s*\*\*(.+?)\*\*\s*—\s*(.+?)\s*\|'
    matches = re.findall(pattern, text)
    for name, desc in matches:
        desc = desc.strip()
        name = name.strip()
        if desc == "" or desc == name or len(desc) < 8:
            msg = f"  [简介] `{name}` -- 简介过短或重复标题: [{desc}]\n"
            issues.append(msg)
    if issues:
        for i in issues:
            report.write(i)
        report.write(f"\n  共 {len(issues)} 个简介问题\n")
    else:
        report.write("  [OK] index.md 所有简介均有实质内容\n")
    return issues

def check6_orphan_pages(md_files, wiki_root, report):
    report.write("\n" + "=" * 60 + "\n")
    report.write("[检查6] 孤儿页面（无任何页面链接到它）\n")
    report.write("=" * 60 + "\n")
    # 先收集所有被引用的链接
    all_links = set()
    for fp in md_files:
        text = read_file_safe(fp)
        _, body = get_frontmatter(text)
        links = extract_wikilinks(body)
        for link in links:
            all_links.add(link.strip())

    orphans = []
    for fp in md_files:
        page_name = os.path.basename(fp)[:-3]
        if page_name.startswith("2026-") or page_name == "index":
            continue
        is_referenced = False
        for link in all_links:
            link = link.strip()
            if link.endswith(page_name) or page_name.endswith(link) or link == page_name:
                is_referenced = True
                break
        if not is_referenced:
            msg = f"  [孤儿] `{page_name}` -- 没有被其他页面链接\n"
            orphans.append(msg)
    if orphans:
        for o in orphans:
            report.write(o)
        report.write(f"\n  共 {len(orphans)} 个孤儿页面\n")
    else:
        report.write("  [OK] 没有孤儿页面\n")
    return orphans

def main():
    wiki_root = WIKI_ROOT
    md_files = []
    for root, dirs, fnames in os.walk(wiki_root):
        # 跳过 .workbuddy 等隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in fnames:
            if fn.endswith(".md") and "log" not in root:
                md_files.append(os.path.join(root, fn))

    report_path = os.path.join(wiki_root, "..", "scripts", "lint_report.txt")
    report_path = os.path.abspath(report_path)
    with open(report_path, "w", encoding="utf-8") as report:
        report.write("Wiki Lint 检查报告\n")
        report.write("=" * 60 + "\n")
        report.write(f"扫描到 {len(md_files)} 个 markdown 文件\n\n")

        all_issues = []
        all_issues.extend(check1_frontmatter_spelling(md_files, report))
        all_issues.extend(check2_dangling_links(md_files, wiki_root, report))
        # 检查5：index.md 简介质量
        index_path = os.path.join(wiki_root, "index.md")
        all_issues.extend(check5_index_quality(index_path, report))
        # 检查6：孤儿页面
        all_issues.extend(check6_orphan_pages(md_files, wiki_root, report))

        report.write("\n" + "=" * 60 + "\n")
        report.write(f"Lint 完成：发现 {len(all_issues)} 个问题\n")
        report.write("=" * 60 + "\n")

    print(f"Lint 报告已保存到: {report_path}")
    print(f"共发现 {len(all_issues)} 个问题，详见报告文件")

if __name__ == "__main__":
    main()
