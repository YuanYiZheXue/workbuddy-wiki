#!/usr/bin/env python3
"""
AI Prompt 模板：识别跨知识库链接机会
"""

import os
from pathlib import Path
import yaml

def generate_ai_prompt_for_cross_kb_links(global_view_yaml):
    """
    根据全局视图，生成 AI Prompt 用于识别跨知识库链接机会
    """

    # 读取全局视图
    with open(global_view_yaml, "r", encoding="utf-8") as f:
        global_view = yaml.safe_load(f)

    # 构建 Prompt
    prompt = """你是一个知识库链接专家。请根据以下全局视图，识别需要创建跨知识库链接的机会。

## 全局视图

"""

    # 添加概念、实体、对比的信息
    for category in ["概念", "实体", "对比"]:
        prompt += f"### {category}页\n\n"
        for page_path, kb_list in global_view[category].items():
            if len(kb_list) > 1:  # 只在多个知识库中出现的页面才需要跨库链接
                prompt += f"- **{page_path}** 在以下知识库中出现：{', '.join(kb_list)}\n"

        prompt += "\n"

    prompt += """## 任务

请输出需要创建跨知识库链接的机会，格式如下：

```yaml
跨知识库链接机会:
  - 源页面: wiki/概念/上下文工程.md
    目标页面: 计算机/概念/上下文工程.md
    显示文本: 上下文工程（计算机）
    理由: 同一概念在不同知识库中的表述
  - 源页面: 计算机/概念/上下文工程.md
    目标页面: wiki/概念/上下文工程.md
    显示文本: 上下文工程（Wiki）
    理由: 同一概念在不同知识库中的表述
```

## 约束

1. 每个页面最多创建 5 个跨知识库链接
2. 只链接最相关、最重要的跨知识库页面
3. 显示文本必须有明确含义（例如："上下文工程（计算机）"）
4. 确保双向链接都创建
"""

    return prompt

def main():
    # 生成 AI Prompt
    prompt = generate_ai_prompt_for_cross_kb_links("wiki/统筹/全局视图.yaml")

    # 保存 Prompt 到文件
    output_path = Path("wiki/统筹/ai_prompt_识别跨库链接机会.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"AI Prompt 已保存到：{output_path}")

    # 同时打印到控制台
    print("\n" + "="*80)
    print("生成的 AI Prompt：")
    print("="*80)
    print(prompt)

if __name__ == "__main__":
    main()
