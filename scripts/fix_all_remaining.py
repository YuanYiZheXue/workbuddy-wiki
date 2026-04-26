#!/usr/bin/env python3
"""
处理剩余的所有双向链接问题
1. 将指向 raw/ 的链接转为 sources: 字段
2. 删除其他悬空链接
3. 最终验证：再次扫描双向链接
"""

import re
import subprocess
from pathlib import Path

WIKI_DIR = Path("wiki")
EXCLUDE_DIRS = {"log", ".obsidian", "发布"}

def find_git():
    """查找 git.exe 路径"""
    # 常见安装位置
    candidates = [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    # 尝试 where git
    try:
        r = subprocess.run(["where", "git"], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return "git"  # fallback


def fix_raw_links_in_file(file_path, dry_run=False):
    """将文件中指向 raw/ 的 wikilinks 转为 sources: 字段，返回处理的链接数"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_links = re.findall(r'\[\[(raw/[^\]]+)\]\]', content)
    if not raw_links:
        return 0

    sources = []
    for link in raw_links:
        fname = link.replace("raw/", "").replace(".md", "")
        if fname not in sources:
            sources.append(fname)

    if dry_run:
        return len(raw_links)

    # 删除 [[raw/...]] 链接
    new_content = content
    for link in raw_links:
        new_content = new_content.replace(f"[[{link}]]", "")

    # 更新 frontmatter 中的 sources: 字段
    fm_match = re.search(r'---\n(.*?)\n--', new_content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        if "sources:" in fm:
            # 已有 sources，追加
            new_fm = fm.rstrip() + ", " + ", ".join(sources)
        else:
            new_fm = fm + f"\nsources: " + ", ".join(sources)
        new_content = new_content.replace(fm, new_fm)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return len(raw_links)


def remove_dangling_links_in_file(file_path, dry_run=False):
    """删除文件中其他悬空链接，返回删除的数量"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 找到所有 wikilink
    all_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    removed = 0

    for link in all_links:
        # 提取页面名称
        if "|" in link:
            page = link.split("|")[0].strip()
        else:
            page = link.strip()

        # 检查目标是否存在
        if not find_page_file(page):
            if dry_run:
                removed += 1
            else:
                content = content.replace(f"[[{link}]]", "")
                removed += 1

    if not dry_run and removed > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return removed


def find_page_file(page_name, wiki_dir=WIKI_DIR):
    """查找页面文件"""
    for ext in [".md", ""]:
        candidate = wiki_dir / f"{page_name}{ext}"
        if candidate.exists():
            return candidate
    for subdir in ["概念", "实体", "来源", "对比", "统筹"]:
        d = wiki_dir / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.suffix == ".md" and page_name in f.stem:
                return f
    return None


def main():
    print("=== 综合修复双向链接问题 ===\n")

    # 1. 处理指向 raw/ 的链接
    print("[1/3] 处理指向 raw/ 的链接...")
    raw_total = 0
    for md_file in WIKI_DIR.rglob("*.md"):
        if any(ex in md_file.parts for ex in EXCLUDE_DIRS):
            continue
        count = fix_raw_links_in_file(md_file, dry_run=True)
        if count > 0:
            print(f"  {md_file.name}: {count} 个 raw/ 链接")
            fix_raw_links_in_file(md_file)
            raw_total += count
    print(f"  ✓ 处理了 {raw_total} 个 raw/ 链接\n")

    # 2. 删除其他悬空链接
    print("[2/3] 删除其他悬空链接...")
    dangling_total = 0
    for md_file in WIKI_DIR.rglob("*.md"):
        if any(ex in md_file.parts for ex in EXCLUDE_DIRS):
            continue
        count = remove_dangling_links_in_file(md_file)
        if count > 0:
            print(f"  {md_file.name}: 删除了 {count} 个悬空链接")
            dangling_total += count
    print(f"  ✓ 删除了 {dangling_total} 个悬空链接\n")

    # 3. 最终验证
    print("[3/3] 最终验证...")
    # 复用 check_bidirectional_links.py 的逻辑
    issues = []
    for md_file in WIKI_DIR.rglob("*.md"):
        if any(ex in md_file.parts for ex in EXCLUDE_DIRS):
            continue
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in links:
            page = link.split("|")[0].strip() if "|" in link else link.strip()
            if not find_page_file(page):
                issues.append((md_file.name, link))

    print(f"  剩余问题：{len(issues)} 个")
    if issues:
        print("\n剩余问题（前10个）：")
        for fname, link in issues[:10]:
            print(f"  {fname}: [[{link}]]")
        if len(issues) > 10:
            print(f"  ...还有 {len(issues) - 10} 个")

    print("\n=== 修复完成 ===")
    print(f"  处理 raw/ 链接：{raw_total} 个")
    print(f"  删除悬空链接：{dangling_total} 个")
    print(f"  剩余问题：{len(issues)} 个")


if __name__ == "__main__":
    main()
