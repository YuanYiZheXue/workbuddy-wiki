#!/usr/bin/env python3
"""
检查 wiki/ 中所有页面的双向链接
输出缺失的反向链接报告
"""

import re
from pathlib import Path

WIKI_DIR = Path("wiki")
EXCLUDE_DIRS = {"log", ".obsidian", "发布"}

def extract_wikilinks(content):
    """提取内容中的所有 wikilink：[[页面]] 或 [[页面|显示文本]]"""
    # 匹配 [[...]]，但不匹配代码块中的
    # 简单处理：去掉代码块后再提取
    # 去掉 ``` 代码块
    cleaned = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # 去掉行内代码
    cleaned = re.sub(r'`.*?`', '', cleaned)

    links = re.findall(r'\[\[([^\]]+)\]\]', cleaned)
    result = []
    for link in links:
        if '|' in link:
            page = link.split('|')[0].strip()
        else:
            page = link.strip()
        # 去掉路径前缀（如 "概念/元一思想" -> "元一思想"）
        # 但保留跨知识库链接的完整路径
        result.append(page)
    return result


def find_page_file(page_name, wiki_dir=WIKI_DIR):
    """在 wiki/ 目录中查找页面对应的文件"""
    # 先尝试直接匹配文件名
    for ext in ['.md', '']:
        candidate = wiki_dir / f"{page_name}{ext}"
        if candidate.exists():
            return candidate

    # 搜索子目录
    for subdir in ['概念', '实体', '来源', '对比', '统筹']:
        candidate = wiki_dir / subdir / f"{page_name}.md"
        if candidate.exists():
            return candidate
        # 也尝试匹配页面名称（可能文件名有日期前缀）
        if (wiki_dir / subdir).exists():
            for f in (wiki_dir / subdir).iterdir():
                if f.suffix == '.md' and page_name in f.stem:
                    return f

    return None


def has_reverse_link(file_path, source_page_name):
    """检查 file_path 是否有指向 source_page_name 的链接"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查各种形式的反向链接
    patterns = [
        rf'\[\[{re.escape(source_page_name)}\]\]',
        rf'\[\[.*?\|.*?{re.escape(source_page_name)}.*?\]\]',
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False


def check_bidirectional_links():
    """检查所有页面的双向链接"""
    issues = []

    # 遍历所有 markdown 文件
    for md_file in WIKI_DIR.rglob("*.md"):
        # 跳过排除目录
        if any(excluded in md_file.parts for excluded in EXCLUDE_DIRS):
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        links = extract_wikilinks(content)

        for link in links:
            # 查找链接目标文件
            target_file = find_page_file(link)
            if target_file is None:
                # 悬空链接
                issues.append({
                    'type': '悬空链接',
                    'source': md_file,
                    'target': link,
                    'message': f'链接目标不存在：[[{link}]]'
                })
                continue

            # 检查是否有反向链接
            source_page_name = md_file.stem
            if not has_reverse_link(target_file, source_page_name):
                issues.append({
                    'type': '缺失反向链接',
                    'source': md_file,
                    'target': target_file,
                    'link': link,
                    'message': f'缺失反向链接：{md_file.name} -> {target_file.name}'
                })

    return issues


def main():
    print("正在检查双向链接...")
    issues = check_bidirectional_links()

    if not issues:
        print("  ✓ 所有双向链接完整！")
        return

    # 按类型分组输出
    missing_reverse = [i for i in issues if i['type'] == '缺失反向链接']
    dangling = [i for i in issues if i['type'] == '悬空链接']

    print(f"\n检查发现 {len(issues)} 个问题：")
    print(f"  - 缺失反向链接：{len(missing_reverse)} 个")
    print(f"  - 悬空链接：{len(dangling)} 个")

    print("\n--- 缺失反向链接 ---")
    for issue in missing_reverse[:20]:  # 只显示前20个
        print(f"  {issue['source'].name} -> [[{issue['link']}]] (缺失反向)")

    if len(missing_reverse) > 20:
        print(f"  ... 还有 {len(missing_reverse) - 20} 个")

    print("\n--- 悬空链接 ---")
    for issue in dangling[:20]:
        print(f"  {issue['source'].name}: [[{issue['target']}]]")

    if len(dangling) > 20:
        print(f"  ... 还有 {len(dangling) - 20} 个")


if __name__ == "__main__":
    main()
