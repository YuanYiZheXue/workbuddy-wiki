---
type: source
tags: [agent, harness, generator-evaluator, anthropic, multi-agent]
sources: [raw/Harness design for long-running application development.md]
created: 2026-04-25
updated: 2026-04-25
---

# Harness Design for Long-Running Application Development

> 来源：[[raw/Harness design for long-running application development]]
> 原文：https://www.anthropic.com/engineering/harness-design-long-running-apps
> 作者：Prithvi Rajasekaran（Anthropic Labs）

## 一句话摘要

受 GAN（生成对抗网络）启发，用 Generator + Evaluator 双 Agent 架构解决主观设计质量不可量化的问题，并扩展到全栈开发的三 Agent 架构（Planner + Generator + Evaluator）。

## 背景与动机

早期工作（initializer + coding agent）通过 prompt engineering 和 harness 设计提升了性能，但仍有天花板。两类问题持续存在：
1. **上下文腐烂 + 上下文焦虑**：模型在长任务中失去连贯性，或在接近上下文限制时提前结束工作
2. **自我评估偏差**：Agent 对自己生成的作品倾向于自信地赞美，即使质量平庸

## 核心架构：Generator + Evaluator

### 与 GAN 的类比
- GAN：生成器 vs 判别器 → Agent 版本：Generator vs Evaluator
- 关键：让评估者变得「怀疑」，比让生成器批判自己工作效果好得多

### Frontend Design 实验

四条评估标准（写入 evaluator prompt）：
1. **Design quality**：整体感 vs 零件拼凑
2. **Originality**：自定义决策 vs 模板默认布局（惩罚「AI 味」模式）
3. **Craft**：技术执行（排版层次、间距一致性、色彩和谐）
4. **Functionality**：可用性独立于美学

- Evaluator 使用 Playwright MCP 直接与实时页面交互后评分（不是评静态截图）
- 每次迭代通常推动生成器向更有特色的方向发展
- 5-15 次迭代，完整运行耗时可达 4 小时
- 第 10 次迭代出现「创意跳跃」：整个重构设计方案（如 3D 房间画廊）

## 扩展到全栈开发：三 Agent 架构

### Planner Agent
- 将 1-4 句 prompt 扩展为完整产品规格
- 刻意保持高层级（避免过早指定技术细节导致错误级联）
- 寻找机会将 AI 功能编织进产品规格
- 可使用 frontend-design skill 制定视觉设计语言

### Generator Agent
- 按 sprint 工作，一次一个功能
- 技术栈：React + Vite + FastAPI + SQLite/PostgreSQL
- 每个 sprint 结束时自我评估，然后用 git commit

### Evaluator Agent
- 使用 Playwright MCP 以用户方式点击运行中的应用
- 测试 UI 功能、API 端点和数据库状态
- 每条标准有硬性阈值，任一条不达标则 sprint 失败
- 反馈非常具体，生成器可直接依据反馈行动

### Sprint Contract（Sprint 契约）
- 每个 sprint 前，generator 和 evaluator 协商「完成」的定义
- 弥补产品规格的高层级与实际可测试实现之间的鸿沟
- 两者迭代直到达成一致

## Context Reset vs Compaction

- **Compaction**：在原地总结前面的对话，保持连续性，但上下文焦虑可能持续
- **Context Reset**：完全清空上下文窗口，用结构化 handoff 传递上一 Agent 的状态
- Opus 4.5 有强烈上下文焦虑，必须用它 + context reset
- Opus 4.6 基本消除了该行为，可以去掉 context reset，用 Claude Agent SDK 的自动 compaction

## 迭代 Harness：简化实验

**去掉 sprint 构造**：Opus 4.6 能力提升，不再需要 sprint 分解。Generator 可以原生处理连续工作。

**保留 planner 和 evaluator**：
- 去掉 planner → generator 范围不足，生成功能更少的应用
- Evaluator 的价值取决于任务是否超出模型 solo 可靠能力的边界（边界外有价值，边界内是额外开销）

**关键启示**：Harness 中的每个组件都编码了一个关于「模型不能独自做什么」的假设。这些假设值得压力测试——可能不正确，且随着模型改进会迅速过时。

## 与 Wiki 方法的映射

| 本文实践 | Wiki 方法对应 |
|----------|--------------|
| Planner 生成规格 → generator 执行 | Ingest：先讨论关键要点，再创建摘要页 |
| Sprint contract 协商 | Query 前先读 index.md 了解已有知识 |
| Evaluator 验证 → 反馈到 generator | Lint：健康检查，发现矛盾和过时信息 |
| Context reset + handoff artifact | WorkBuddy Memory：跨会话持久化状态 |
| 迭代简化 harness | Schema 共同演进：去掉不再必要的 guardrail |

## 相关概念

- [[概念/Agent Harness|Agent Harness]]
- [[概念/长运行 Agent]]
- [[概念/自我验证循环]]
- [[概念/上下文腐烂]]
- [[概念/Skills 渐进式披露]]

## 相关实体

- [[实体/Anthropic]]
- [[实体/Claude Agent SDK]]
- [[实体/Playwright MCP]]
