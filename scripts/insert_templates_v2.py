from pathlib import Path

filepath = r'd:\Obsidian_KN\知识库构建\workbuddy-wiki-schema.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已插入
if '新对话启动模板' in content:
    print('提示：新对话启动模板已存在，无需插入')
else:
    # 在「会话管理」小节的末尾（--- 之前）插入新内容
    # 找到「会话管理」小节的末尾
    import re
    
    # 方法：找到 "### 会话管理" 之后，下一个 "---" 之前的内容
    pattern = r'(### 会话管理.*?)(### Ingest)'
    
    replacement = '''### 会话管理

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

### 新对话启动模板

每次开启新对话时，使用 `wiki/统筹/新对话启动模板.md` 中的模板。

**主知识库模板**：
```
新对话开始。

请按以下顺序读取文件，了解上下文：

1. 读取 `SOUL.md` — 了解你的身份和行为准则
2. 读取 `IDENTITY.md` — 确认你的名字和角色
3. 读取 `USER.md` — 了解用户是谁
4. 读取 `workbuddy-wiki-schema.md` — 了解 Wiki 方法和约定
5. 读取 `wiki/log/index.md` — 了解近期操作
6. 读取 `wiki/log/[今天日期].md` — 了解今天的工作进度（如果文件存在）
7. 读取 `.workbuddy/memory/MEMORY.md` — 获取跨会话重要事实

读取完成后，简要汇报：
- 当前 Wiki 规模（从 `wiki/index.md`）
- 昨天做了什么（从 `wiki/log/`）
- 今天继续做什么
```

**子知识库模板**：
```
新对话开始。

请按以下顺序读取文件，了解上下文：

1. 读取 `SOUL.md` — 了解你的身份和行为准则
2. 读取 `IDENTITY.md` — 确认你的名字和角色
3. 读取 `USER.md` — 了解用户是谁
4. 读取 `workbuddy-wiki-schema.md` — 了解 Wiki 方法和约定
5. 读取 `wiki/log/index.md` — 了解近期操作
6. 读取 `wiki/log/[今天日期].md` — 了解今天的工作进度（如果文件存在）
7. 读取 `.workbuddy/memory/MEMORY.md` — 获取跨会话重要事实
8. 读取 `wiki/统筹/跨知识库协作指南.md` — 了解跨知识库协作流程

读取完成后，简要汇报：
- 当前知识库规模（从 `wiki/index.md`）
- 昨天做了什么（从 `wiki/log/`）
- 今天继续做什么
- 如何与主知识库协作（从 `wiki/统筹/跨知识库协作指南.md`）
```

### 新工作空间配置

当创建新工作空间时，需要配置新 Agent 的身份：

1. **拷贝配置文件**：`workbuddy-wiki-schema.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`
2. **修改 `SOUL.md`**：更新角色定位、元一思想的应用场景
3. **修改 `IDENTITY.md`**：更新名字、生物、表情
4. **复用 `USER.md`**：用户是同一个人
5. **创建 `.gitignore`**：只递交 `wiki/index.md` 和 `wiki/统筹/`
6. **验证新 Agent**：问它"我们的 Wiki 方法是什么？"、"你如何与主知识库协作？"

详细步骤见 `wiki/统筹/新工作空间配置指南.md`。

---

'''

    new_content = content.replace('### Ingest（摄取）', replacement + '### Ingest（摄取）')
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('OK: 已插入「新对话启动模板」和「新工作空间配置」到 workbuddy-wiki-schema.md')
    else:
        print('ERROR: 无法插入内容，未找到插入位置')
