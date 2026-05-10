import os
import re
import codecs

wiki_root = r"d:\Obsidian_KN\哲学思想\wiki"

# 收集所有存在的页面（去掉扩展名）
existing_pages = set()
for root, dirs, files in os.walk(wiki_root):
    for f in files:
        if f.endswith('.md'):
            # 保留相对路径，但去掉扩展名
            rel_path = os.path.relpath(os.path.join(root, f), wiki_root)
            # 去掉 .md 扩展名
            page_name = rel_path[:-3]
            existing_pages.add(page_name)
            # 也加入纯文件名（不含路径），因为 [[ ]] 可能只写文件名
            existing_pages.add(f[:-3])

print(f"已索引 {len(existing_pages)} 个页面\n")

# 收集所有 [[ ]] 链接
links = set()
broken_links = []

for root, dirs, files in os.walk(wiki_root):
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            with codecs.open(filepath, 'r', 'utf-8') as fp:
                content = fp.read()
                # 查找所有 [[ ]] 链接
                matches = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link in matches:
                    # 去掉 | 后的显示文本
                    link = link.split('|')[0].strip()
                    links.add(link)
                    
                    # 检查链接是否存在
                    # 先检查完整路径
                    link_path = link + '.md'
                    found = False
                    
                    # 检查各种可能路径
                    possible_paths = [
                        os.path.join(wiki_root, link_path),
                        os.path.join(wiki_root, '概念', link_path),
                        os.path.join(wiki_root, '来源', link_path),
                        os.path.join(wiki_root, '统筹', link_path),
                        os.path.join(wiki_root, '发布', link_path),
                        os.path.join(wiki_root, 'log', link_path),
                    ]
                    
                    for p in possible_paths:
                        if os.path.exists(p):
                            found = True
                            break
                    
                    # 也检查链接是否在 existing_pages 中
                    if link in existing_pages:
                        found = True
                    
                    if not found:
                        broken_links.append((os.path.join(root, f), link))

print(f"找到 {len(links)} 个唯一链接")
print(f"悬空链接数量: {len(broken_links)}\n")

if broken_links:
    print("=== 悬空链接列表 ===")
    for src, link in broken_links:
        rel_src = os.path.relpath(src, wiki_root)
        print(f"  来源: {rel_src}")
        print(f"  链接: [[{link}]]")
        print()
else:
    print("✅ 没有悬空链接！")
