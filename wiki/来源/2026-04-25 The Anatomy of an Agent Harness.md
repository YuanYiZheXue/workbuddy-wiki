---
type: source
tags: [agent, harness, langchain, filesystem, sandbox, context-rot]
sources: [raw/The Anatomy of an Agent Harness.md]
created: 2026-04-25
updated: 2026-04-25, The Anatomy of an Agent Harness
---

# The Anatomy of an Agent Harness

> 来源：
> 原文：https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
> 作者：Vivek Trivedy（LangChain）

## 一句话摘要

Agent = Model + Harness。Harness 是为模型包裹的外部系统，提供文件系统、沙箱、上下文管理等基础设施，使模型智能真正变成可自主工作的引擎。

## 核心公式

> **The model contains the intelligence and the harness is the system that makes that intelligence useful.**

## 为什么需要 Harness

模型开箱只能：
- 接收文本/图片/音频/视频
- 输出文本

模型**无法**开箱做到：
- 跨交互维持持久状态
- 执行代码
- 获取实时知识
- 搭建环境、安装包来完成工作

这些都是 **Harness 级功能**。

## Harness 的核心组件

### 1. Filesystem（文件系统）
> 最基础的 Harness 原语（primitive）

- Agent 获得工作区来读取数据、代码和文档
- 工作可以增量添加和卸载，不需要全部塞进上下文
- **文件系统是天然的协作面**——多个 Agent 和人类可以通过共享文件协调（Agent Teams 架构依赖此）
- Git 为文件系统增加版本控制：追踪工作、回滚错误、分支实验

### 2. Bash + Code Exec（代码执行）
> 给模型一台电脑，让它自己想办法

- ReAct 循环中，模型通过工具调用执行动作
- 与其让用户为每种可能动作预建工具，不如给 Agent 一个通用工具：bash
- 模型可以通过代码即时设计自己的工具，而不是被约束在固定工具集里

### 3. Sandbox（沙箱）
> 给 Agent 安全的运行环境

- 本地执行 Agent 生成的代码有风险，单个本地环境无法扩展到大量 Agent 工作负载
- 沙箱提供隔离的执行环境，可按需创建、分发到多任务、工作完成后销毁
- 好的环境附带好的默认工具：预装语言运行时、git/testing CLI、浏览器（用于 web 交互和验证）

### 4. Battling Context Rot（对抗上下文腐烂）
> Context Rot：随着上下文窗口填满，模型推理和完成任务的能力下降

Harness 的应对策略：
- **Compaction**：当上下文窗口接近填满时，智能地卸载和总结现有内容，让 Agent 继续工作
- **Tool call offloading**：将超过阈值的大工具输出保留头部和尾部 token，完整输出卸载到文件系统
- **Skills（渐进式披露）**：避免启动时加载过多工具/MCP 服务器导致性能下降，按需加载

### 5. Long Horizon Autonomous Execution（长视野自主执行）
> 让 Agent 在长时间跨度内自主、正确地完成复杂工作

依赖前面所有原语的复合效应：
- **Filesystem + git**：跨会话追踪工作，新 Agent 快速了解最新进展
- **Ralph Loop**：拦截模型的退出尝试，在干净的上下文窗口中重新注入原始 prompt，强制 Agent 继续工作（每次迭代从头开始但有历史状态）
- **Planning + Self-verification**：模型将目标分解为步骤，每完成一步通过测试套件或自我评估验证正确性

## Harness 与模型训练的耦合

- 今天的 Agent 产品（Claude Code、Codex）在训练时就把模型和 Harness 放在循环里一起 post-train
- 这形成了反馈循环：有用原语被发现 → 加入 Harness → 训练下一代模型
- 副作用：模型可能 overfit 到特定 Harness，换一个 Harness 性能反而下降（见 Terminal Bench 2.0 榜单，Opus 4.6 在不同 Harness 中分数差异巨大）
- **结论：最好的 Harness 不一定是被 post-train 的那个，而是为你的任务优化过的那个**

## 未来方向（LangChain 正在探索）

- 编排数百个 Agent 并行工作在同一个代码库
- Agent 分析自己的 trace 来识别并修复 Harness 级失败模式
- Harness 动态组装正确的工具和上下文（just-in-time），而不是预配置

## 与上一篇的关系

本文是理论框架；上一篇（Anthropic 实践）是本文理论的具体落地——Initializer Agent + Coding Agent 双架构、feature list、progress file 都是 FileSystem + Planning + Self-verification 原语的具体实现。

## 相关概念

- [[概念/Agent Harness|Agent Harness]]
- [[概念/上下文腐烂]]
- [[概念/长运行 Agent]]
- [[概念/渐进式披露]]

## 相关实体

- [[实体/LangChain]]
- [[实体/Vivek Trivedy]]
## 相关概念

- [[概念/Agent Harness]]
- [[概念/长运行 Agent]]
- [[概念/上下文腐烂]]
- [[概念/自我验证循环]]

## 相关实体

- [[实体/Anthropic]]（对比参考）



## 相关页面
- [[LangChain]]
- [[Vivek Trivedy]]
- [[Agent Harness 设计对比]]
- [[2026-04-25 Karpathy AI+Obsidian知识库教程]]
- [[Anthropic]]
- [[上下文腐烂]]
- [[渐进式披露]]
- [[自我验证循环]]
- [[长运行 Agent]]