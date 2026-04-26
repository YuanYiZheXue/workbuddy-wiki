#!/usr/bin/env python3
"""
处理所有剩余的双向链接问题（无 Unicode 字符版）
1. 将指向 raw/ 的链接转为 sources: 字段
2. 删除其他悬空链接
3. 最终验证
"""

import re
from pathlib import Path

WIKI_DIR = Path("wiki")
EXCLUDE_DIRS = {"log", ".obsidian", "发布"}


def find_page_file(page_name, wiki_dir=WIKI_DIR):
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


def fix_raw_links_in_file(file_path):
    """将文件中指向 raw/ 的 wikilinks 转为 sources: 字段，返回处理数量"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_links = re.findall(r'\[\[(raw/[^\]]+)\]\]', content)
    if not raw_links:
        return 0

    sources = []
    for link in raw_links:
        fname = link.replace("raw/", "")
        if fname.endswith(".md"):
            fname = fname[:-3]
        if fname not in sources:
            sources.append(fname)
    
    # 删除 [[raw/...]] 链接
    new_content = content
    for link in raw_links:
        new_content = new_content.replace(f"[[{link}]]", "")
    
    # 更新 frontmatter 中的 sources: 字段
    fm_match = re.search(r'---\n(.*?)\n--', new_content, flags=re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        if "sources:" in fm:
            # 已存在 sources: 字段，追加
            new_fm = fm.rstrip() + ", " + ", ".join(sources)
            new_content = new_content.replace(fm, new_fm)
        else:
            # 新增 sources: 字段
            new_fm = fm + f"\nsources: " + ", ".join(sources)
            new_content = new_content.replace(fm, new_fm)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    return len(raw_links)


def remove_dangling_links_in_file(file_path):
    """删除文件中的悬空链接（指向不存在的页面），返回删除数量"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    all_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    removed = 0
    new_content = content
    
    for link in all_links:
        page = link.split("|")[0].strip()
        if not find_page_file(page):
            new_content = new_content.replace(f"[[{link}]]", "")
            removed += 1
    
    if removed > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
    return removed


def scan_bidirectional_issues():
    """扫描所有双向链接问题，返回 (missing_reverse, dangling)"""
    missing = []
    dangling = []
    
    all_files = [f for f in WIKI_DIR.rglob("*.md") 
                if not any(ex in f.parts for ex in EXCLUDE_DIRS)]
    
    for md_file in all_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in links:
            page = link.split("|")[0].strip()
            target = find_page_file(page)
            if target is None:
                dangling.append((md_file, link))
            elif md_file.stem != "index":
                # 检查反向链接
                with open(target, "r", encoding="utf-8") as f2:
                    target_content = f2.read()
                reverse_pattern = re.escape(md_file.stem)
                if not re.search(rf'\[\[.*?{reverse_pattern}.*?\]\]', target_content):
                    missing.append((md_file, target, link))
                    
    return missing, dangling


def main():
    print("=== 综合修复双向链接问题 ===")
    print("")
    
    # 1. 处理指向 raw/ 的链接
    print("[1/3] 处理指向 raw/ 的链接...")
    raw_total = 0
    for md_file in WIKI_DIR.rglob("*.md"):
        if any(ex in md_file.parts for ex in EXCLUDE_DIRS):
            continue
        count = fix_raw_links_in_file(md_file)
        if count > 0:
            print(f"  {md_file.name}: 处理了 {count} 个 raw/ 链接")
            raw_total += count
    print(f"  总计：{raw_total} 个")
    print("")
    
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
    print(f"  总计：{dangling_total} 个")
    print("")
    
    # 3. 最终验证
    print("[3/3] 最终验证...")
    missing, dangling = scan_bidirectional_issues()
    print(f"  缺失反向链接：{len(missing)} 个")
    print(f"  悬空链接：{len(dangling)} 个")
    print("")
    
    if not missing and not dangling:
        print("=== 修复完成！所有双向链接已完整 ===")
    else:
        print("=== 修复完成（有少量剩余问题）===")
        if missing:
            print(f"  缺失反向链接（前5个）：")
            for src, tgt, lnk in missing[:5]:
                print(f"    {src.name} -> [[{lnk}]]")
        if dangling:
            print(f"  悬空链接（前5个）：")
            for src, lnk in dangling[:5]:
                print(f"    {src.name}: [[{lnk}]]")


if __name__ == "__main__":
    main()
