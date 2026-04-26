import pypdf

reader = pypdf.PdfReader(r"d:\Obsidian_KN\哲学思想\raw\长沙马王堆帛书.pdf")
print(f"总页数: {len(reader.pages)}\n")

full_text = []
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    full_text.append(f"=== 第 {i+1} 页 ===\n{text}")

output = "\n\n".join(full_text)
with open(r"d:\Obsidian_KN\哲学思想\raw\_boshu_content.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("内容已写入 _boshu_content.txt")
print(f"总字符数: {len(output)}")
