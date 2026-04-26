import os

root = r"d:\Obsidian_KN\哲学思想\wiki"

# 收集所有存在的md文件（不含.md后缀）
existing = set()
for r, ds, fs in os.walk(root):
    for f in fs:
        if f.endswith('.md'):
            # 相对路径（不含.md）
            rel = os.path.relpath(os.path.join(r, f), root).replace('\\', '/')[:-3]
            existing.add(rel)
            # 纯文件名（不含.md）
            existing.add(f[:-3])

# 检查报告中的悬空链接是否真实存在
check_list = [
    '统筹/全局视图',
    '概念/动中有静静中有动',
    '概念/有为',
    '概念/无为之术',
    '概念/道法自然',
    '概念/天地不仁',
    '概念/柔弱胜刚强',
    '概念/庄子',
    '概念/儒家',
    '概念/佛家',
]

print("检查疑似误报的悬空链接：")
print("-" * 50)
for item in check_list:
    found = item in existing
    print(f"{'[存在]' if found else '[缺失]'} {item}")
    
print("\n总结：")
print(f"  存在: {sum(1 for i in check_list if i in existing)}")
print(f"  不存在: {sum(1 for i in check_list if i not in existing)}")
