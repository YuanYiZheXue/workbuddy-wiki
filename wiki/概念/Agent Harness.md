---
type: concept
tags: [agent, harness, langchain, anthropic]
sources: [来源/2026-04-25 Effective harnesses for long-running agents, 来源/2026-04-25 The Anatomy of an Agent Harness]
created: 2026-04-25
updated: 2026-04-25
---

# Agent Harness

## 定义

> **Agent = Model + Harness**
> The model contains the intelligence and the harness is the system that makes that intelligence useful.

Harness 是为模型包裹的外部系统，提供模型开箱无法做到的能力：持久状态、代码执行、实时知识获取、环境搭建。

## 核心原语（Primitives）

### 1. Filesystem（文件系统）
- 最基础的 Harness 原语
- Agent 获得工作区读写能力
- 工作可以增量卸载，不需要全部塞进上下文
- **文件系统是天然的协作面**——多个 Agent 和人类通过共享文件协调
- Git 叠加版本控制：追踪工作、回滚、分支实验

### 2. Bash + Code Exec（代码执行）
- 给 Agent 通用目的工具，而不是预定义工具集
- 模型可以通过代码即时设计自己的工具
- 相当于"给模型一台电脑"

### 3. Sandbox（沙箱）
- 提供隔离的安全执行环境
- 可按需创建、分发到多任务、工作完销毁
- 附带默认工具：预装运行时、git/testing CLI、浏览器

### 4. Context Management（上下文管理）
- **Compaction**：上下文窗口接近满时，智能卸载和总结
- **Tool call offloading**：大工具输出卸载到文件系统，只保留头尾 token
- **Skills / 渐进式披露**：避免启动时加载过多工具导致性能下降

### 5. Long Horizon Execution（长视野执行）
- **Filesystem + git**：跨会话追踪工作
- **Ralph Loop**：拦截退出尝试，干净上下文重新注入原始 prompt
- **Planning + Self-verification**：分解目标、每步验证

## 与 Wiki 方法的映射

| Harness 原语 | Wiki 方法中的对应 |
|--------------|----------------|
| Filesystem as collaboration surface | Wiki 本身就是文件系统上的协作面 |
| Git for progress tracking | `log.md` + git 历史 |
| Progressive disclosure (Skills) | WorkBuddy 按需加载 Skills |
| Self-verification loops | Lint 工作流 |
| Leave clean state | Ingest 结束时 index/log/memory 都已更新 |

## 相关概念

- [[概念/上下文工程]]
- [[概念/上下文腐烂]]
- [[概念/长运行 Agent]]
- [[概念/渐进式披露]]
- [[概念/元一思想]] — 顶层设计哲学

## 相关实体

- [[实体/LangChain]]
- [[实体/Anthropic]]
