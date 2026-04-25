---
title: "Ralph Wiggum 循环"
created: 2026-04-25
sources:
  - "[[来源/2026-04-25 Harness design for long-running application development]]"
  - "[[来源/2026-04-25 工程技术：在智能体优先的世界中利用 Codex]]"
tags: [自我修复, 验证循环, Agent Harness]
---

# Ralph Wiggum 循环

> 命名来自 [ghuntley.com/loop/](https://ghuntley.com/loop/)，描述智能体打开 PR → 自我审查 → 响应反馈 → 循环直到所有审查通过的行为模式。

## 定义

智能体**自我驱动修复循环**：不是人类在循环里，而是智能体自己在循环里——它打开 PR，自己审查自己的更改，自己响应反馈，循环直到通过。

## 运作方式（来自 Codex 工程实践）

1. 智能体根据任务提示，编写代码并打开 PR
2. 智能体**在本地审核其自身的更改**
3. 在本地和云端请求额外的特定智能体审查
4. 对任何（智能体或人类给出的）反馈做出响应
5. 循环往复，直到所有智能体审核人员都满意
6. 智能体自己压缩并合并 PR

## 关键特征

- **人类可以审核 PR，但非必须** — 随着系统成熟，逐渐转为智能体对智能体的审核
- **纠错成本低，等待成本高** — 在高吞吐量系统中，让智能体快速迭代比阻塞等待人类审查更高效
- **睡眠友好** — 单次 Codex 运行可持续工作 6+ 小时（人类睡眠时间）

## 与「自我验证循环」的关系

两者是同一核心理念的不同表述：
- **自我验证循环**（Anthropic/LangChain 语境）：Generator + Evaluator 架构，生成与评估分离
- **Ralph Wiggum 循环**（OpenAI Codex 语境）：PR-driven 的自我修复循环

本质相同：**强制智能体验证自己的工作再继续**，而不是一路生成到底。

## 对 Wiki 方法的启示

Ingest 流程可以借鉴这个循环：
- WorkBuddy 创建/更新 wiki 页面后，应该自己检查一下：index 更新了吗？log 追加了吗？交叉引用正确吗？
- 对应 `workbuddy-wiki-schema.md` 里的"结束时确保干净状态"

## 来源

- [[来源/2026-04-25 Harness design for long-running application development]] — Generator + Evaluator 架构
- [[来源/2026-04-25 工程技术：在智能体优先的世界中利用 Codex]] — OpenAI Codex 团队实践，详细描述了 Ralph Wiggum 循环
