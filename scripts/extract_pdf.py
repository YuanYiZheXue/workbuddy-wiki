#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 PDF 文本内容并保存"""

import sys
from pypdf import PdfReader

def extract_pdf(pdf_path, output_path, max_pages=None):
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        if max_pages is None:
            max_pages = total_pages
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_path.split('/')[-1]}\n\n")
            f.write(f"总页数: {total_pages}\n\n---\n\n")
            
            for i in range(min(max_pages, total_pages)):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    f.write(f"## 第{i+1}页\n\n")
                    f.write(text)
                    f.write("\n\n---\n\n")
            
            if max_pages < total_pages:
                f.write(f"\n[注：仅提取前{max_pages}页，共{total_pages}页]\n")
        
        print(f"提取完成：{output_path}")
        return True
    except Exception as e:
        print(f"错误：{e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python extract_pdf.py <pdf_path> <output_path> [max_pages]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    success = extract_pdf(pdf_path, output_path, max_pages)
    sys.exit(0 if success else 1)
