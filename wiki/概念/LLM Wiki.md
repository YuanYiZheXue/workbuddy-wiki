---
title: "LLM Wiki"
created: 2026-05-01
source_count: 2
status: ready
type: concept
tags:
  - "知识管理"
  - "Karpathy"
  - "LLM"
---

## 摘要

LLM Wiki 是一套「以 Markdown 为载体、LLM 为维护者、人类为监督者」的知识管理模式，核心是**知识编译层**——把零散的原始素材通过 LLM 持续整理成结构化、可复用、可进化的 Wiki。

---

## 核心定义

> LLM Wiki 不是 RAG 的替代品，而是**知识编译层**——提前编译知识，而非临时检索合成。

**关键特性**：
- 知识是有复合效应的（compounding）：交叉引用已经存在，矛盾已经被标记
- 结论不藏在聊天记录里，而是沉淀在 Wiki 中
- 越用越完善（查询→合成→回写→优化闭环）

---

## 三层架构

### 第一层：Raw Sources（原始素材层）
- **原则**：只读不改，保留溯源能力
- **内容**：文档、论文、PR、会议记录、图片、数据集
- **对应我们的实现**：`raw/` 目录（已设置 NTFS 只读保护 ✅）

### 第二层：Wiki 结构化知识层
- **原则**：LLM 主导，人类审核
- **内容**：摘要页、概念页、实体页、对比分析
- **对应我们的实现**：`wiki/` 目录

### 第三层：Schema 规则定义层
- **原则**：约束 LLM，避免混乱
- **内容**：操作规则、语法检查规则、摄入流程、lint 清单
- **对应我们的实现**：`workbuddy-wiki-schema.md` ✅

---

## 与 RAG 的核心区别

| 维度 | LLM Wiki | 基础 RAG |
|------|----------|-----------|
| 核心定位 | 知识编译层，持续维护 | 查询时检索合成，即时响应 |
| 工作方式 | 提前编译，持续更新 | 查询时检索 chunk，实时合成 |
| 优势 | 知识可积累、可溯源、可读性强 | 灵活高效，适合实时查询 |
| 劣势 | 需要维护 | 结论不积累，聊天记录易丢失 |

**结论**：两者互补，不是替代关系。LLM Wiki 解决「知识积累」问题，RAG 解决「实时查询」问题。

---

## Karpathy 的 8 步工作流

1. **数据摄入**：raw/ → Wiki（用 ingest prompt 约束 LLM）
2. **前端展示**：Obsidian 作为「Wiki IDE」
3. **问答交互**：小体量无需复杂 RAG
4. **结果回写**：查询→合成→回写 Wiki（闭环）
5. **质量校验**：LLM 自检查，人类做终审
6. **工具扩展**：循序渐进（Obsidian → qmd → GraphRAG）
7. **模型微调**：Wiki 内容作为合成数据
8. **团队协作**：权限管控 + PR 审核

---

## 与 WorkBuddy Wiki Schema 的对比

WorkBuddy Wiki Schema 已经吸收了 Karpathy 的核心思想，并加入了：
- 道德经十原则（含第0条「自知者明」元原则）
- 元一思想四极飞轮
- Ralph Wiggum 循环（自我验证）
- 渐进式披露（Progressive Disclosure）
- Ingest/Lint/Query 标准流程

**差异**：
- Karpathy 用 `AGENTS.md` 作为规则文件；我们用 `workbuddy-wiki-schema.md`
- Karpathy 强调 Claude Code 工具；我们用 WorkBuddy
- 我们加入了「知止不殆」「日损」「无为而治」等道德经原则

---

## 关键洞察

### 知识编译层 vs 临时检索
RAG：每次查询都重新发现知识，没有积累
LLM Wiki：知识编译一次，然后保持更新

### Schema 层的重要性
很多人搭 LLM Wiki 失败，就是因为少了 Schema 层（操作手册）。没有它，LLM 会：
- 乱建页面
- 乱改内容
- 遗漏引用
- 格式混乱

### 循序渐进的工具采用
| Wiki 体量 | 工具配置 |
|-----------|-----------|
| <100 页面 | Obsidian + Markdown + Claude Code + Git |
| 100-500 页面 | 添加 qmd（轻量搜索）|
| >500 页面 | 添加 GraphRAG（强化关系检索）|

---

## 引用来源

- [[2026-05-01 Karpathy的LLM Wiki深度拆解]]
- Karpathy 原始 gist：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## 待补充

- [ ] Karpathy 原始 gist 的详细研读
- [ ] Claude Code 的 `--ingest`、`--lint` 参数具体用法
- [ ] Microsoft GraphRAG 的实际落地成本评估
