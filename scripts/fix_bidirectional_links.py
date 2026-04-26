#!/usr/bin/env python3
"""
自动修复 wiki/ 中的双向链接问题
- 为缺失的反向链接添加反向链接
- 将指向 raw/ 的悬空链接转换为 sources: 字段
"""

import re
import sys
from pathlib import Path

WIKI_DIR = Path("wiki")
EXCLUDE_DIRS = {"log", ".obsidian", "发布"}


def extract_wikilinks(content):
    """提取内容中的所有 wikilink"""
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
    # 直接匹配
    for ext in ['.md', '']:
        candidate = wiki_dir / f"{page_name}{ext}"
        if candidate.exists():
            return candidate
    # 在子目录中搜索
    for subdir in ['概念', '实体', '来源', '对比', '统筹']:
        d = wiki_dir / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.suffix == '.md' and page_name in f.stem:
                return f
    return None


def get_page_type(file_path):
    """判断页面类型（概念/实体/来源/对比）"""
    parts = file_path.parts
    for part in parts:
        if part in ['概念', '实体', '来源', '对比', '统筹']:
            return part
    return None


def append_reverse_link(file_path, reverse_link, page_type):
    """向页面追加反向链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查链接是否已存在
    if reverse_link in content:
        return False  # 已存在

    # 确定追加到哪个 section
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

        # 找到目标 section
        if line.strip() == target_section:
            section_found = True
            # 向后找到 section 结束（下一个 ## 或文件末尾）
            j = i + 1
            while j < len(lines) and not lines[j].startswith('## '):
                new_lines.append(lines[j])
                j += 1
            # 在 section 末尾追加链接
            new_lines.append(f"- {reverse_link}")
            appended = True
            i = j
            continue

        i += 1

    if not section_found:
        # 没找到 section，在文件末尾添加
        new_lines.append('')
        new_lines.append(target_section)
        new_lines.append(f"- {reverse_link}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    return True


def fix_dangling_raw_links(file_path):
    """将指向 raw/ 的悬空链接转换为 sources: 字段"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找指向 raw/ 的 wikilinks
    raw_links = re.findall(r'\[\[(raw/[^\]]+)\]\]', content)
    if not raw_links:
        return []

    # 提取文件名（不含路径）
    sources = []
    for link in raw_links:
        fname = link.split('/')[-1]
        if fname.endswith('.md'):
            fname = fname[:-3]
        sources.append(fname)

    # 更新 frontmatter 中的 sources: 字段
    frontmatter_match = re.search(r'---\n(.*?)\n--', content, flags=re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        if 'sources:' in frontmatter:
            # 已有 sources: 字段，追加
            pass  # 复杂，先跳过
        else:
            # 添加 sources: 字段
            new_frontmatter = frontmatter + '\nsources: ' + ', '.join(sources)
            content = content.replace(frontmatter, new_frontmatter)

    # 删除指向 raw/ 的 wikilinks
    for link in raw_links:
        content = content.replace(f'[[{link}]]', '')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return raw_links


def main():
    print("正在重新检查双向链接...")
    issues = []

    # 收集所有问题（复用 check_bidirectional_links.py 的逻辑）
    all_files = list(WIKI_DIR.rglob("*.md"))
    all_files = [f for f in all_files if not any(ex in f.parts for ex in EXCLUDE_DIRS)]

    for md_file in all_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        links = extract_wikilinks(content)

        for link in links:
            target_file = find_page_file(link)
            if target_file is None:
                issues.append({
                    'type': '悬空链接',
                    'source': md_file,
                    'target': link
                })
                continue

            # 检查反向链接（跳过 index.md）
            if md_file.stem == 'index':
                continue

            source_name = md_file.stem
            if not has_reverse_link(target_file, source_name):
                issues.append({
                    'type': '缺失反向链接',
                    'source': md_file,
                    'target': target_file,
                    'link': link
                })

    # 分类
    missing = [i for i in issues if i['type'] == '缺失反向链接']
    dangling = [i for i in issues if i['type'] == '悬空链接']

    print(f"发现问题：{len(issues)} 个")
    print(f"  - 缺失反向链接：{len(missing)} 个")
    print(f"  - 悬空链接：{len(dangling)} 个")

    # 自动修复缺失的反向链接
    print("\n正在自动修复缺失的反向链接...")
    fixed = 0
    for issue in missing:
        target_file = issue['target']
        source_file = issue['source']
        page_type = get_page_type(target_file)

        reverse_link = f"[[{source_file.stem}]]"
        if append_reverse_link(target_file, reverse_link, page_type):
            fixed += 1

    print(f"  ✓ 已修复 {fixed} 个缺失的反向链接")

    # 处理悬空链接
    print("\n正在处理悬空链接...")
    raw_fixed = 0
    other_dangling = []
    for issue in dangling:
        if issue['target'].startswith('raw/'):
            links_removed = fix_dangling_raw_links(issue['source'])
            raw_fixed += len(links_removed)
        else:
            other_dangling.append(issue)

    print(f"  ✓ 已处理 {raw_fixed} 个指向 raw/ 的链接")
    if other_dangling:
        print(f"  ⚠ 还有 {len(other_dangling)} 个其他悬空链接需要手动处理")

    print(f"\n完成！建议运行 git diff 检查修改是否正确")


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


if __name__ == "__main__":
    main()
