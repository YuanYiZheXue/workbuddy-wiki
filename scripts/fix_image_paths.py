#!/usr/bin/env python3
"""
修复 raw 目录下 md 文件中的图片路径
将 ../Images/xxx.png 改为 Images/xxx.png
"""
import os
import re

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw')

def fix_image_paths(filepath):
    """修复单个文件中的图片路径"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换图片路径：../Images/ -> Images/
    # 匹配 ![...](../Images/xxx.png) 或 ![](../Images/xxx.png)
    pattern = r'!\[([^\]]*)\]\(\.\./Images/'
    replacement = r'![\1](Images/'
    
    new_content = re.sub(pattern, replacement, content)
    
    count = len(re.findall(pattern, content))
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  [OK] {os.path.basename(filepath)}：修复了 {count} 处图片路径")
    else:
        print(f"  (无需要修复的路径) {os.path.basename(filepath)}")
    
    return count

def main():
    raw_dir = os.path.abspath(RAW_DIR)
    md_files = [f for f in os.listdir(raw_dir) if f.endswith('.md')]
    
    print(f"检查 raw/ 目录下的 md 文件...")
    total = 0
    for md in md_files:
        filepath = os.path.join(raw_dir, md)
        count = fix_image_paths(filepath)
        total += count
    
    print(f"\n完成！共修复 {total} 处图片路径")
    print("图片路径已从 ../Images/ 改为 Images/")

if __name__ == '__main__':
    main()
