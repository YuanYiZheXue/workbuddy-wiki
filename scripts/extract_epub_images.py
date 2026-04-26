#!/usr/bin/env python3
"""
从 epub 文件中提取 Images 文件夹到 raw/Images/
epub 本质是 zip，图片通常在 OEBPS/Images/ 或 Images/
"""
import zipfile
import os
import shutil

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw')
IMAGES_DIR = os.path.join(RAW_DIR, 'Images')

def extract_images_from_epub(epub_path, output_dir):
    """从单个 epub 文件中提取图片"""
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    
    with zipfile.ZipFile(epub_path, 'r') as zf:
        # 列出所有文件，找到图片文件
        image_files = [f for f in zf.namelist() 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
        
        print(f"  在 {os.path.basename(epub_path)} 中找到 {len(image_files)} 张图片")
        
        for img_path in image_files:
            # 取文件名（不含路径）
            img_name = os.path.basename(img_path)
            if not img_name:
                continue
            
            # 避免重复：如果已存在则跳过
            out_path = os.path.join(output_dir, img_name)
            if os.path.exists(out_path):
                continue
            
            # 提取图片
            with zf.open(img_path) as src, open(out_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    
    return count

def main():
    # 找到所有 epub 文件
    epub_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith('.epub')]
    
    if not epub_files:
        print("未找到 epub 文件")
        return
    
    total = 0
    for epub in epub_files:
        epub_path = os.path.join(RAW_DIR, epub)
        print(f"处理: {epub}")
        count = extract_images_from_epub(epub_path, IMAGES_DIR)
        total += count
        print(f"  提取了 {count} 张新图片")
    
    print(f"\n完成！共提取 {total} 张图片到：{IMAGES_DIR}")
    
    # 列出提取的图片
    if os.path.exists(IMAGES_DIR):
        images = os.listdir(IMAGES_DIR)
        print(f"Images 目录共有 {len(images)} 个文件")
        for img in sorted(images)[:10]:
            print(f"  - {img}")
        if len(images) > 10:
            print(f"  ... 还有 {len(images)-10} 个文件")

if __name__ == '__main__':
    main()
