import os
import codecs

wiki_root = r"d:\Obsidian_KN\哲学思想\wiki"

# 收集所有存在的页面
existing = set()
for r, ds, fs in os.walk(wiki_root):
    for f in fs:
        if f.endswith('.md'):
            rel = os.path.relpath(os.path.join(r, f), wiki_root).replace('\\', '/')[:-3]
            existing.add(rel)
            existing.add(f[:-3])

# 应创建的概念列表（从lint报告中提取）
should_create = [
    '有为', '无为之术', '道法自然', '天地不仁', '柔弱胜刚强',
    '反者道之动', '反也者道之动', '无不为', '辅万物之自然', '知足知止',
    '知止', '知足不辱', '柔弱虚静', '俗人昭昭我独昏昏', '万物并作吾以观复',
    '为学日益为道日损', '为学者日益闻道者日损', '不出于户知天下', '小国寡民',
    '大制不割', '天之道损有余而补不足', '能辅万物之自然', '三宝', '知其雄守其雌',
    '有无相生', '守静笃', '水', '无为而无不为', '道域', '观', '势', '慈',
    '俭', '善执生者', '生生之厚', '物壮则老', '人道vs天道', '完全心流状态',
    '庖丁解牛', '弱反而强', '思想传承的双重考验', '道家衍生科技', '道家科技体系',
    '道德经与模拟信号处理', '动中取静', '一步到位直接自我提升', '两种能量模式',
    '温水煮青蛙式蚕食的应对', '假需求', '以身观身以邦观邦', '见小曰明',
    '帛书与通行本差异', '清静', '天下正',
    '信息茧房突破四步法', '大脑清理机制', '对话4', '对话5', '动中有静静中有动'
]

# 创建概念页
created = 0
for name in should_create:
    if name in existing:
        continue
    
    # 构建内容
    content = []
    content.append('---\n')
    content.append(f'title: "{name}"\n')
    content.append('type: concept\n')
    content.append('tags: [概念, 道德经]\n')
    content.append('created: 2026-04-26\n')
    content.append('sources: [[待补充]]\n')
    content.append('---\n\n')
    content.append(f'# {name}\n\n')
    content.append('> （待补充核心定义）\n\n')
    content.append('---\n\n')
    content.append('## 核心内涵\n\n（待补充）\n\n')
    content.append('## 道德经关联\n\n（待补充）\n\n')
    content.append('## 关联概念\n\n（待补充）\n')
    
    # 写入文件
    file_path = os.path.join(wiki_root, '概念', f'{name}.md')
    try:
        with codecs.open(file_path, 'w', 'utf-8') as f:
            f.write(''.join(content))
        created += 1
        print(f'[创建] {name}')
    except Exception as e:
        print(f'[失败] {name}: {e}')

print(f"\n完成：共创建 {created} 个概念页")
print(f"剩余悬空链接请手动处理（庄子、儒家、佛家等未来扩展）")
