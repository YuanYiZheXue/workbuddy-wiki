# Wiki Index

> 本文件由 WorkBuddy 在每次 ingest 后自动更新。
> 人工也可直接编辑。

## Stats

| 项目 | 数量 |
|------|------|
| 来源摘要页 | 11 |
| 实体页 | 2 |
| 概念页 | 8 |
| 对比页 | 0 |
| 总计 | 21 |

---

## 来源摘要

| 页面 | 简介 | 日期 |
|------|------|------|
| [[来源/2026-04-25 Effective harnesses for long-running agents]] | Anthropic 双 Agent 架构解决长运行 Agent 跨上下文窗口难题 | 2026-04-25 |
| [[来源/2026-04-25 The Anatomy of an Agent Harness]] | Agent = Model + Harness，详解 Harness 五大核心原语 | 2026-04-25 |
| [[来源/2026-04-25 Harness design for long-running application development]] | Generator + Evaluator 架构：从设计到全栈开发的三 Agent 系统 | 2026-04-25 |
| [[来源/2026-04-25 What Harness Engineering Actually Means]] | 清晰区分 Prompt/Context/Harness Engineering 三者 | 2026-04-25 |
| [[来源/2026-04-25 Improving Deep Agents with harness engineering]] | 只改 Harness 不改模型，Terminal Bench 分数从 Top30 到 Top5 | 2026-04-25 |
| [[来源/2026-04-25 工程技术：在智能体优先的世界中利用 Codex]] | OpenAI 用 Codex 无人写代码构建百万行产品，Ralph Wiggum 循环实践 | 2026-04-25 |
| [[来源/2026-04-25 Ralph Wiggum as a software engineer]] | Geoffrey Huntley 的 Ralph Wiggum 技巧详解：while 循环 + 子 Agent + 背压管理 | 2026-04-25 |
| [[来源/2026-04-25 Harness engineering for coding agent users]] | 外层 Harness 框架：Computational vs Inferential、三类调节维度 | 2026-04-25 |
| [[来源/2026-04-25 Karpathy AI+Obsidian知识库教程]] | Obsidian + Claude Code 构建知识库教程（飞书导出不完整，仅头部） | 2026-04-25 |
| [[来源/2026-04-25 Building Effective AI Coding Agents for the Terminal]] | OPENDEV：Rust 编写的终端原生 Agent，双模式架木 + 上下文工程 | 2026-04-25 |
| [[来源/元一思想体系]] | 元一思想完整体系：四原则箴言 + 动态制衡模型 | 2026-04-26 |
| [[来源/2026-04-26 OpenAI Michael Bolin on Codex]] | Codex 开源负责人访谈：小而精的 Harness、沙箱跨平台、AGENTS.md 适度原则 | 2026-04-26 |

---

## 实体

| 页面 | 简介 |
|------|------|
| [[实体/Anthropic]] | Claude 大模型开发方，发表长运行 Agent 双 Agent 架构实践 |
| [[实体/LangChain]] | LLM 应用框架，系统阐述 Agent = Model + Harness 理论 |

---

## 概念

| 页面 | 简介 |
|------|------|
| [[概念/Agent Harness|Agent Harness]] | Agent = Model + Harness；五大原语：文件系统/代码执行/沙箱/上下文管理/长视野执行 |
| [[概念/长运行 Agent]] | 跨多上下文窗口持续工作；Anthropic 双 Agent 架构主要解决对象 |
| [[概念/上下文腐烂]] | Context Rot；上下文窗口填满后推理能力下降，需 Compaction/Offloading |
| [[概念/自我验证循环]] | Generator + Evaluator 架构；生成与评估分离，强制验证后再继续 |
| [[概念/上下文工程]] | 决定给模型什么上下文；Harness Engineering 的内部组成部分（LangChain） |
| [[概念/Ralph Wiggum 循环]] | OpenAI Codex 实践；PR → 自我审查 → 响应反馈 → 循环直到通过 |
| [[概念/渐进式披露]] | 给智能体地图而非百科全书；AGENTS.md 作为目录，按需深入 |
| [[概念/元一思想]] | Wiki 的顶层哲学：体用/效度/生固/稳变 四原则 + 四极飞轮 |

## 对比（1 个页面）

| 页面 | 简介 |
|------|------|
| [[对比/Agent Harness 设计对比]] | Anthropic vs OpenDev vs LangChain 的 Harness 设计哲学对比 |
