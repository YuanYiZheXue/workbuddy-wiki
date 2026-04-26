import re

filepath = r'd:\Obsidian_KN\知识库构建\workbuddy-wiki-schema.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 在「### Ingest（摄取）」之前插入「### 会话管理」小节
new_section = """
### 会话管理

WorkBuddy 历史对话最多保存 **100 个**。超过后最早的历史会被丢弃。

**影响**：
- 每个会话不要超过 ~30 轮对话（预留 buffer）
- 长任务应拆分为多个会话
- 会话结束时，关键信息必须写入持久化文件（log、memory、index）

**建议工作流**：
1. 每 ~3 个对话开启新对话
2. 新对话开头：`新对话开始。请先读取 wiki/log/index.md 和最新的 wiki/log/YYYY-MM-DD.md，了解上次工作进度，然后继续。`
3. 会话结束前，确保所有重要信息已写入 `wiki/log/YYYY-MM-DD.md` 和 `.workbuddy/memory/YYYY-MM-DD.md`

> **注意**：此约束与 Agent 配置相关。其他知识库的 Agent 应根据自己的历史对话保存上限调整策略。

---

"""

# 在 `### Ingest（摄取）` 之前插入
insert_marker = "\n### Ingest（摄取）"
if insert_marker in content:
    new_content = content.replace(insert_marker, new_section + "\n### Ingest（摄取）", 1)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("OK: 已插入「会话管理」小节到 workbuddy-wiki-schema.md")
else:
    print("ERROR: 找不到插入标记")
