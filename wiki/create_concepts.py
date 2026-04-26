import os
import codecs

wiki_root = r"d:\Obsidian_KN\哲学思想\wiki"

# 要创建的概念列表
concepts = [
    '有为', '无为之术', '道法自然', '天地不仁', '柔弱胜刚强',
    '反者道之动', '无不为', '辅万物之自然', '知足知止', '知止',
    '知足不辱', '守静笃', '水', '无为而无不为', '慈', '俭',
    '善执生者', '生生之厚', '物壮则老', '人道vs天道',
    '帛书与通行本差异', '清静', '天下正',
    '信息茧房突破四步法', '大脑清理机制', '以身观身以邦观邦',
    '见小曰明', '动中有静静中有动'
]

created = 0
for name in concepts:
    file_path = os.path.join(wiki_root, '概念', f'{name}.md')
    
    # 检查是否已存在
    if os.path.exists(file_path):
        print(f'[跳过] {name}（已存在）')
        continue
    
    # 构建内容
    content = f"""---
title: "{name}"
type: concept
tags: [概念, 道德经]
created: 2026-04-26
sources: [[待补充]]
---

# {name}

> （待补充核心定义）

---

## 核心内涵

（待补充）

---

## 道德经关联

（待补充）

---

## 关联概念

（待补充）
"""
    
    # 写入文件
    try:
        with codecs.open(file_path, "w", "utf-8") as f:
            f.write(content)
        created += 1
        print(f'[创建] {name}')
    except Exception as e:
        print(f'[失败] {name}: {e}')

print(f"\n完成：共创建 {created} 个概念页")
