#!/usr/bin/env python3
"""
自动修复 wiki/ 中的双向链接问题
- 为缺失的反向链接添加反向链接
- 将指向 raw/ 的悬空链接转换为 sources: 字段
"""

import re
import json
from pathlib import Path

WIKI_DIR = Path("wiki")
EXCLUDE_DIRS = {"log", ".obsidian", "发布"}


def extract_wikilinks(content):
    """提取内容中的所有 [[...]] 链接"""
    cleaned = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    cleaned = re.sub(r'`.*?`', '', cleaned)
    links = re.findall(r'\[\[([^\]]+)\]\]', cleaned)
    result = []
    for link in links:
        if '|' in link:
            page = link.split('|')[0].strip()
        else:
            page = link.strip()
        result.append(page)
    return result


def find_page_file(page_name, wiki_dir=WIKI_DIR):
    """在 wiki/ 目录中查找页面对应的文件"""
    for ext in ['.md', '']:
        candidate = wiki_dir / f"{page_name}{ext}"
        if candidate.exists():
            return candidate
    for subdir in ['概念', '实体', '来源', '对比', '统筹']:
        d = wiki_dir / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.suffix == '.md' and page_name in f.stem:
                return f
    return None


def get_page_type(file_path):
    """判断页面类型"""
    parts = file_path.parts
    for part in parts:
        if part in ['概念', '实体', '来源', '对比', '统筹']:
            return part
    return None


def has_reverse_link(file_path, source_page_name):
    """检查 file_path 是否有指向 source_page_name 的链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    patterns = [
        rf'\[\[{re.escape(source_page_name)}\]\]',
        rf'\[\[.*?\|.*?{re.escape(source_page_name)}.*?\]\]',
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False


def append_reverse_link(file_path, reverse_link, page_type):
    """向页面追加反向链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if reverse_link in content:
        return False

    section_map = {
        '概念': '## 相关概念',
        '实体': '## 相关实体',
        '来源': '## 相关页面',
        '对比': '## 相关页面',
        '统筹': '## 相关页面'
    }
    target_section = section_map.get(page_type, '## 相关页面')

    lines = content.split('\n')
    new_lines = []
    i = 0
    section_found = False
    appended = False

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        if line.strip() == target_section:
            section_found = True
            j = i + 1
            while j < len(lines) and not lines[j].startswith('## '):
                new_lines.append(lines[j])
                j += 1
            new_lines.append(f"- {reverse_link}")
            appended = True
            i = j
            continue
        i += 1

    if not section_found:
        new_lines.append('')
        new_lines.append(target_section)
        new_lines.append(f"- {reverse_link}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    return True


def scan_issues():
    """扫描所有双向链接问题，返回 (missing_reverse, dangling)"""
    missing = []
    dangling = []

    all_files = list(WIKI_DIR.rglob("*.md"))
    all_files = [f for f in all_files
                 if not any(ex in f.parts for ex in EXCLUDE_DIRS)]

    for md_file in all_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        links = extract_wikilinks(content)

        for link in links:
            target_file = find_page_file(link)
            if target_file is None:
                dangling.append({
                    'source': md_file,
                    'target': link
                })
                continue

            if md_file.stem == 'index':
                continue

            source_name = md_file.stem
            if not has_reverse_link(target_file, source_name):
                missing.append({
                    'source': md_file,
                    'target': target_file,
                    'link': link
                })

    return missing, dangling


def main():
    print("正在扫描双向链接问题...")
    missing, dangling = scan_issues()

    print(f"扫描完成：")
    print(f"  - 缺失反向链接：{len(missing)} 个")
    print(f"  - 悬空链接：{len(dangling)} 个")

    if not missing and not dangling:
        print("  OK: 所有双向链接完整！")
        return

    # 自动修复缺失的反向链接
    if missing:
        print(f"\n正在自动修复缺失的反向链接...")
        fixed = 0
        for issue in missing:
            target_file = issue['target']
            source_file = issue['source']
            page_type = get_page_type(target_file)
            if not page_type:
                continue
            reverse_link = f"[[{source_file.stem}]]"
            if append_reverse_link(target_file, reverse_link, page_type):
                fixed += 1
        print(f"  OK: 已修复 {fixed} 个缺失的反向链接")

    # 报告悬空链接（暂不自动修复）
    if dangling:
        print(f"\n悬空链接（暂不自动修复）：")
        raw_links = [d for d in dangling if d['target'].startswith('raw/')]
        other_links = [d for d in dangling if not d['target'].startswith('raw/')]
        print(f"  - 指向 raw/ 的链接：{len(raw_links)} 个（建议转为 sources: 字段）")
        print(f"  - 其他悬空链接：{len(other_links)} 个")
        # 只显示前10个
        for d in other_links[:10]:
            print(f"    {d['source'].name}: [[{d['target']}]]")
        if len(other_links) > 10:
            print(f"    ... 还有 {len(other_links) - 10} 个")

    print(f"\n建议：运行 git diff 检查修改是否正确")


if __name__ == "__main__":
    main()
