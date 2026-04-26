---
type: entity
tags: [framework, langchain, harness, evaluation]
sources:
  - "[[来源/2026-04-25 The Anatomy of an Agent Harness]]"
  - "[[来源/2026-04-25 Improving Deep Agents with harness engineering]]"
  - "[[来源/2026-04-25 工程技术：在智能体优先的世界中利用 Codex]]"
created: 2026-04-25
---

# LangChain

> 用于构建 LLM 应用的框架，也是 Agent Harness 工程的重要实践者。

## 简介

LangChain 是一个用于构建大语言模型应用的 Python/JavaScript 框架。提供链（Chains）、代理（Agents）、记忆（Memory）、工具调用（Tool Calling）等抽象层，帮助开发者快速构建 LLM 应用。

## 与 Wiki 主题的关系

- 发表了 **The Anatomy of an Agent Harness**（Vivek Trivedy），系统阐述 Agent = Model + Harness 理论框架
- 发表了 **Improving Deep Agents with harness engineering**（LangChain 团队），展示只改 Harness 不改模型带来的性能提升
- 开发了 **LangSmith** — Agent 评估与可观测性平台，是 Trace 分析的核心工具
- OpenAI 的 Codex 工程团队在文章中参考了 LangChain 的 Harness 工程理念

## 核心产品

- **LangChain** — LLM 应用开发框架
- **LangSmith** — Agent 评估、追踪、调试平台
- **LangServe** — 将 LLM 链部署为 API 的服务

## 相关概念

- [[概念/上下文工程]]
- [[概念/Agent Harness|Agent Harness]]
- [[概念/自我验证循环]] — LangChain 实践中的 Generator + Evaluator 架构

## 相关实体

- [[实体/Vivek Trivedy]] — The Anatomy of an Agent Harness 作者
- [[实体/LangSmith]] — LangChain 旗下评估平台

- [[Anthropic]]
- [[Agent Harness 设计对比]]
- [[Agent 评估方法对比]]
- [[Prompt 工程方法对比]]
- [[2026-04-25 Effective harnesses for long-running agents]]
- [[2026-04-25 Improving Deep Agents with harness engineering]]
- [[2026-04-25 The Anatomy of an Agent Harness]]
- [[2026-04-25 What Harness Engineering Actually Means]]
- [[Ralph Wiggum 循环]]
- [[上下文工程]]
- [[上下文腐烂]]
- [[渐进式披露]]
- [[自我验证循环]]
- [[长运行 Agent]]
- [[LangSmith]]
- [[Vivek Trivedy]]
- [[2026-04-25 工程技术：在智能体优先的世界中利用 Codex]]