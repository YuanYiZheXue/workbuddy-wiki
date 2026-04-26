import os
import re
import codecs

wiki_root = r"d:\Obsidian_KN\哲学思想\wiki"

# 收集所有存在的页面（多种格式）
existing_pages = set()
page_paths = {}  # 页面名（不含路径和.md） -> 相对路径（不含.md）

for root, dirs, files in os.walk(wiki_root):
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, wiki_root)
            rel_path_norm = rel_path.replace('\\', '/')
            page_name = f[:-3]  # 去掉 .md
            
            # 添加多种格式到 existing_pages
            existing_pages.add(page_name)            # 纯文件名：道
            existing_pages.add(rel_path_norm[:-3])   # 相对路径（去.md）：概念/道
            existing_pages.add(rel_path_norm)        # 相对路径（保留.md）：概念/道.md
            
            # 也添加反斜杠版本（以防万一）
            existing_pages.add(rel_path.replace('/', '\\')[:-3])
            
            page_paths[page_name] = rel_path_norm[:-3]

# 检查链接
broken_links = []
checked_links = set()

for root, dirs, files in os.walk(wiki_root):
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, wiki_root).replace('\\', '/')
            
            with codecs.open(filepath, 'r', 'utf-8') as fp:
                content = fp.read()
            
            # 查找所有 [[ ]] 链接（忽略代码块）
            lines = content.split('\n')
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                
                if in_code_block:
                    continue
                
                matches = re.findall(r'\[\[([^\]]+)\]\]', line)
                for link in matches:
                    # 去掉 | 后的显示文本
                    link = link.split('|')[0].strip()
                    
                    if not link:
                        continue
                    
                    if link in checked_links:
                        continue
                    checked_links.add(link)
                    
                    # 检查链接是否存在（尝试多种格式）
                    found = False
                    
                    # 格式1：直接匹配（道 或 概念/道）
                    if link in existing_pages:
                        found = True
                    
                    # 格式2：加 .md 后缀再匹配
                    if not found and (link + '.md') in existing_pages:
                        found = True
                    
                    # 格式3：文件名匹配（不含路径）
                    if not found:
                        link_name = link.split('/')[-1]  # 如果是 概念/道，取 道
                        if link_name in existing_pages:
                            found = True
                    
                    if not found:
                        broken_links.append((rel_path, link))

# 生成报告
report = []
report.append("---\n")
report.append("date: 2026-04-26\n")
report.append("type: lint报告\n")
report.append("tags: [统筹, lint, 健康检查]\n")
report.append("---\n")
report.append("# Wiki Lint 报告\n")
report.append(f"> 检查时间：2026-04-26\n")
report.append(f"> Wiki根目录：{wiki_root}\n")
report.append(f"> 总页面数：{len(existing_pages)}\n")
report.append(f"> 唯一链接数：{len(checked_links)}\n")
report.append(f"> 悬空链接数：{len(broken_links)}\n")
report.append("\n---\n")

if broken_links:
    report.append("## ⚠️ 悬空链接列表\n")
    report.append(f"共 {len(broken_links)} 个悬空链接：\n")
    report.append("\n| 来源文件 | 悬空链接 | 建议 |\n")
    report.append("|-----------|----------|------|\n")
    
    for src, link in broken_links:
        suggestion = ""
        if link in ['守中', '气', '清静', '天下正', '帛书与通行本差异']:
            suggestion = "建议创建概念页"
        elif link.startswith('概念/') or link.startswith('来源/'):
            suggestion = "路径格式问题，检查文件是否存在"
        else:
            suggestion = "待评估"
        
        report.append(f"| `{src}` | `[[{link}]]` | {suggestion} |\n")
else:
    report.append("## ✅ 没有悬空链接！\n")

report.append("\n---\n")
report.append("## 修复记录\n")
report.append("\n### 已修复\n")
report.append("- [x] Frontmatter格式统一\n")
report.append("- [x] 空链接格式修复\n")
report.append("- [x] lint脚本逻辑修复（支持多种路径格式）\n")
report.append("\n### 待修复\n")
if broken_links:
    report.append(f"- [ ] 处理 {len(broken_links)} 个悬空链接\n")
else:
    report.append("- [x] 所有悬空链接已处理\n")

# 写入报告
report_path = os.path.join(wiki_root, '统筹', 'lint-report.md')
with codecs.open(report_path, 'w', 'utf-8') as f:
    f.write(''.join(report))

print(f"[完成] Lint报告已生成：{report_path}")
print(f"   悬空链接数：{len(broken_links)}")
