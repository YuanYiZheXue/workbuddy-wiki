---
title: "Karpathy的LLM Wiki深度拆解：从理念到落地，如何构建可进化的知识底座"
source: "https://zhuanlan.zhihu.com/p/2024921762337398826"
author: "乐小野要卷卷卷腹 KU Leuven 理学硕士"
published: 2026-04-07
created: 2026-05-01
tags:
  - "LLM Wiki"
  - "Karpathy"
  - "知识管理"
  - "Obsidian"
  - "clippings"
---

## 摘要

Karpathy 提出的 LLM Wiki 是一套「以 Markdown 为载体、LLM 为维护者、人类为监督者」的知识管理模式，核心是**知识编译层**——把零散的原始素材通过 LLM 持续整理成结构化、可复用、可进化的 Wiki。解决 RAG「每次查询都要重新合成、有用结论藏在聊天记录里」的痛点。

---

## 核心架构（三层）

### 1. Raw Sources 原始素材层
- **原则**：只读不改，保留溯源能力
- **目录**：`raw/docs/`、`raw/prs/`、`raw/incidents/`、`raw/meetings/`、`raw/images/`、`raw/others/`
- **命名规范**：`日期_主题_来源`

### 2. Wiki 结构化知识层
- **原则**：LLM 主导，人类审核
- **目录**：`wiki/overview.md`、`wiki/glossary.md`、`wiki/concepts/`、`wiki/entities/`、`wiki/incidents/`、`wiki/decisions/`、`wiki/links.md`
- **文件模板**：含 frontmatter（status、owners、source_count、last_reviewed、sensitivity）

### 3. Schema 规则定义层
- **核心文件**：`AGENTS.md`（LLM 操作手册）
- **作用**：告诉 LLM「怎么维护 Wiki」，避免乱建页面、乱改内容
- **关键规则**：禁止修改 raw/、优先更新现有页面、必须引用来源、不确定内容标记为「待补充/疑问」

---

## 与 RAG / GraphRAG 的区别

| 维度 | LLM Wiki | 基础 RAG | GraphRAG |
|------|----------|-----------|-----------|
| 核心定位 | 知识编译层，持续维护 | 查询时检索合成 | 提取实体关系，强化关联检索 |
| 工作方式 | 提前编译，持续更新 | 查询时检索 chunk | 构建图结构 |
| 优势 | 知识可积累、可溯源 | 灵活高效 | 擅长大规模关系推理 |
| 劣势 | 需要维护 | 结论不积累 | 实现复杂 |

---

## Karpathy 的 8 步工作流

1. **数据摄入**：raw/ → Wiki，用 ingest prompt 约束 LLM
2. **前端展示**：Obsidian 作为「Wiki IDE」（双向链接、图谱视图）
3. **问答交互**：小体量无需复杂 RAG，LLM 直接读 Wiki 文件
4. **结果回写**：查询→合成→回写 Wiki，形成闭环
5. **质量校验**：LLM 自检查，人类做终审
6. **工具扩展**：循序渐进（Obsidian → qmd → GraphRAG）
7. **模型微调**：Wiki 内容作为合成数据，用于微调
8. **团队协作**：权限管控 + PR 审核 + 多工具集成

---

## 关键洞察

### 「知识编译层」概念
RAG 是「每次查询都重新发现知识」，LLM Wiki 是「提前编译一次，然后保持更新」。知识是有复合效应的——交叉引用已经存在，矛盾已经被标记，综合结论已经反映所有已读内容。

### Schema/AGENTS.md 的重要性
很多人搭 LLM Wiki 失败，就是因为少了 Schema 层。没有操作手册，LLM 会乱建页面、乱改内容、遗漏引用。

### 循序渐进的工具采用
- 初期（<100 页面）：Obsidian + Markdown + Claude Code + Git
- 中期（100-500 页面）：添加 qmd（轻量搜索）
- 后期（>500 页面）：添加 GraphRAG（强化关系检索）

### 结果回写循环
查询的优质结果可以回写到 Wiki 中，形成「查询→合成→回写→优化」的闭环。这是 LLM Wiki 最核心的优势之一。

---

## 与 WorkBuddy Wiki Schema 的对比

| 维度 | Karpathy LLM Wiki | WorkBuddy Wiki Schema |
|------|-------------------|----------------------|
| 原始素材层 | raw/ (只读) | raw/ (只读) ✅ |
| 结构化知识层 | wiki/ | wiki/ ✅ |
| 规则定义层 | AGENTS.md | workbuddy-wiki-schema.md ✅ |
| 人类角色 | 监督者、审核者 | 资料来源、探索方向、提问者 ✅ |
| LLM 角色 | 维护者 | 编写并维护所有内容 ✅ |
| 结果回写 | 支持（diff → 审核 → 回写） | 支持（Ralph Wiggum 循环）✅ |
| 质量校验 | lint prompt | Lint（健康检查 + 垃圾回收）✅ |

**结论**：WorkBuddy Wiki Schema 已经吸收了 Karpathy 的核心思想，并加入了道德经原则和元一思想，形成更完整的体系。

---

## 待补充/疑问

- [ ] Karpathy 的原始 gist 内容是否需要进一步研读？
- [ ] Claude Code 的具体用法（--ingest、--lint 参数）
- [ ] Microsoft GraphRAG 的实际落地成本

---

## 引用来源

- 原始文章：https://zhuanlan.zhihu.com/p/2024921762337398826
- Karpathy gist：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Obsidian 官方文档：https://help.obsidian.md/
- Microsoft GraphRAG：https://learn.microsoft.com/en-us/graph/rag/overview
