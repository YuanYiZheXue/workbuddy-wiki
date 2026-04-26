# WorkBuddy Wiki - 哲学 知识库

> **版本**：从主知识库同步
> **状态**：子知识库（只递交 wiki/index.md）
> **主知识库**：`YuanYiZheXue/workbuddy-wiki` (main 分支)

这是一种利用 WorkBuddy 构建 **哲学** 知识库的模式，架构与主知识库一致，
但只递交索引文件到 Git，具体内容不递交。

---

## 架构

有三层：

**原始资料**——你精心策划的源文档集合。WorkBuddy 从中读取但从不修改它们。

**Wiki**——由 WorkBuddy 生成的 Markdown 文件目录。摘要、实体页面、概念页面、对比、概览。
- **注意**：本知识库只递交 `wiki/index.md` 到 Git，具体内容（概念/实体/来源/对比）不递交。

**Schema**——本文件，告诉 WorkBuddy 这是子知识库，需与主知识库协作。

---

## 操作

### 每次会话启动

WorkBuddy 在每次会话开始时，应先了解当前状态，再开始工作：

1. 读取 `SOUL.md` 了解你的身份
2. 读取 `IDENTITY.md` 确认你的名字
3. 读取 `USER.md` 了解用户是谁
4. 读取本文件（`workbuddy-wiki-schema.md`）确认这是子知识库
5. 读取 `wiki/log/index.md` 了解近期操作
6. 读取 `wiki/log/[今天日期].md` 了解今天的工作进度
7. 读取 `wiki/统筹/跨知识库协作指南.md` 了解协作流程

### Ingest（摄取）

**核心原则：一次只处理一篇资料（增量原则）。**

1. WorkBuddy 阅读原始资料
2. 创建 `wiki/来源/YYYY-MM-DD 标题.md` 摘要页
3. 更新相关的实体页和概念页
4. 更新 `wiki/index.md`
5. 追加 `wiki/log/[今天日期].md`

### 会话管理

WorkBuddy 历史对话最多保存 **100 个**。超过后最早的历史会被丢弃。

**影响**：
- 每个会话不要超过 ~30 轮对话（预留 buffer）
- 长任务应拆分为多个会话
- 会话结束时，关键信息必须写入持久化文件（log、memory、index）

**建议工作流**：
1. 每 ~3 个对话开启新对话
2. 新对话开头：`新对话开始。请先读取 wiki/log/index.md 和最新的 wiki/log/YYYY-MM-DD.md，了解上次工作进度，然后继续。`
3. 会话结束前，确保所有重要信息已写入 `wiki/log/YYYY-MM-DD.md`

### 元数据同步

每次构建后，运行：
```bash
python scripts/sync_meta.py
```

### 跨知识库链接

识别跨知识库链接机会：
```bash
python scripts/generate_ai_prompt_cross_kb_links.py
```

创建跨知识库链接：
```bash
python scripts/apply_cross_kb_links.py
```

然后递交更新到分支：
```bash
git add wiki/index.md wiki/统筹/ wiki/概念/ wiki/实体/
git commit -m "feat(哲学): 更新索引和跨知识库链接"
git push origin kb/philosophy
```

---

**最后更新**：2026-04-26
