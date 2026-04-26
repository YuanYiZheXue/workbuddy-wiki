---
type: comparison
tags: [harness, anthropic, opendev, langchain, architecture]
sources:
  - "[[来源/2026-04-25 The Anatomy of an Agent Harness]]"
  - "[[来源/2026-04-25 Building Effective AI Coding Agents for the Terminal]]"
  - "[[实体/LangChain]]"
created: 2026-04-26
---

# Agent Harness 设计对比

> 对比 Anthropic、OpenDev、LangChain 三者的 Agent Harness 设计哲学与实现。

## 一句话总结

| 来源 | 核心设计哲学 |
|------|--------------|
| **Anthropic** | Agent = Model + Harness；5个核心原语（Filesystem、Bash、Sandbox、Context Rot、Long Horizon） |
| **OpenDev** | 复合 AI 系统架构；四层架构，Plan Mode + Normal Mode 双模式，Lazy Tool Discovery |
| **LangChain** | LLM 应用开发框架；提供 Chain、Agent、Memory、Tool Calling 抽象层 |

---

## 对比维度

### 1. 架构设计

| 维度 | Anthropic Harness | OpenDev | LangChain |
|------|-------------------|---------|-----------|
| **架构类型** | 原语组合（5个核心原语） | 四层架构（Entry、Agent、Tool、Persistence） | 框架抽象（Chain、Agent、Memory） |
| **核心组件** | Filesystem、Bash、Sandbox、Context Rot、Long Horizon | Session → Agent → Workflow → LLM（四层层次） | LangChain、LangSmith、LangServe |
| **模型绑定** | 训练时把模型和 Harness 放在循环里一起 post-train | 每层独立绑定到用户配置的 LLM（细粒度模型选择） | 支持多种模型提供商（通过 LLM 抽象） |

### 2. 上下文管理

| 维度 | Anthropic Harness | OpenDev | LangChain |
|------|-------------------|---------|-----------|
| **Context Rot 应对** | Compaction、Tool call offloading、Skills（渐进式披露） | Adaptive Context Compaction（逐步减少旧观察） | Memory 抽象层（Buffer、Summary、Vector） |
| **上下文窗口管理** | 智能卸载和总结现有内容 | 渐进式压缩，优先保留最近观察 | 依赖开发者选择合适的 Memory 类型 |
| **跨会话记忆** | Filesystem + git（持久化到文件系统） | 自动化记忆系统（accumulate project-specific knowledge） | Memory 抽象层（可配置不同后端） |

### 3. 执行模式

| 维度 | Anthropic Harness | OpenDev | LangChain |
|------|-------------------|---------|-----------|
| **执行模式** | Long Horizon Autonomous Execution（长视野自主执行） | Plan Mode（只读子 Agent 规划）+ Normal Mode（完整工具执行） | Agent 执行循环（ReAct、Plan-and-Execute 等） |
| **规划与执行分离** | Planning + Self-verification（模型将目标分解为步骤，每步验证） | 双 Agent 架构（Planning Agent + Execution Agent） | 支持多种执行策略（通过 Agent 类型选择） |
| **安全控制** | Sandbox（隔离执行环境） | 严格安全控制（防止破坏性操作） | 依赖开发者实现（无内置沙箱） |

### 4. 工具管理

| 维度 | Anthropic Harness | OpenDev | LangChain |
|------|-------------------|---------|-----------|
| **工具发现** | Skills（渐进式披露，避免启动时加载过多工具） | Lazy Tool Discovery（按需初始化工具） | Tool Calling（预定义工具集） |
| **工具扩展** | 通过 Skills 扩展（按需加载） | 工具注册表派发（Tool Registry） | 通过 Tool 抽象扩展（自定义 Tool） |
| **MCP 支持** | 支持（通过 Skills 按需加载 MCP 服务器） | 支持（作为工具的一部分） | 支持（通过 Tool 抽象） |

### 5. 记忆与持久化

| 维度 | Anthropic Harness | OpenDev | LangChain |
|------|-------------------|---------|-----------|
| **跨会话记忆** | Filesystem + git（持久化到文件系统） | 自动化记忆系统（跨会话积累项目特定知识） | Memory 抽象层（可配置不同后端） |
| **记忆类型** | 文件系统（Markdown）、git 版本控制 | Config、Conversation History、Provider Cache、Operation Log | Buffer Memory、Summary Memory、Vector Memory |
| **记忆检索** | 文件系统搜索、git 历史 | 事件驱动的系统提醒（counteract instruction fade-out） | 依赖 Vector Store（如 FAISS、Chroma） |

### 6. 评估与可观测性

| 维度 | Anthropic Harness | OpenDev | LangChain |
|------|-------------------|---------|-----------|
| **评估平台** | 无专门平台（依赖外部工具） | 无专门平台（开源，可自行扩展） | **LangSmith**（Agent 评估、追踪、调试平台） |
| **可观测性** | 依赖外部工具（如 Terminal Bench） | 操作日志（Operation Log） | LangSmith（Trace 分析、评估指标） |
| **基准测试** | Terminal Bench（评估 Harness 性能） | Terminal Bench、LongCLI-Bench | 无专门基准（依赖用户自行评估） |

---

## 设计哲学对比

### Anthropic：原语组合

- **核心理念**：Agent = Model + Harness；Harness 中的每个组件都编码了一个关于「模型不能独自做什么」的假设
- **设计原则**：提供一组核心原语（Filesystem、Bash、Sandbox、Context Rot、Long Horizon），让 Agent 通过组合这些原语完成复杂任务
- **优缺点**：
  - ✅ 原语清晰，易于理解和扩展
  - ✅ 与模型训练耦合（post-train 时把模型和 Harness 放在循环里）
  - ❌ 可能 overfit 到特定 Harness（换一个 Harness 性能下降）

### OpenDev：复合 AI 系统

- **核心理念**：State-of-the-art AI results are increasingly achieved by systems that compose multiple models, retrievers, and tools（复合 AI 系统）
- **设计原则**：四层架构（Entry、Agent、Tool、Persistence），每层独立绑定到用户配置的 LLM，支持细粒度模型选择
- **优缺点**：
  - ✅ 细粒度模型选择（平衡成本、延迟、能力）
  - ✅ 双模式执行（Plan Mode + Normal Mode）
  - ❌ 架构复杂，需要更多工程投入

### LangChain：框架抽象

- **核心理念**：提供一组抽象层（Chain、Agent、Memory、Tool Calling），帮助开发者快速构建 LLM 应用
- **设计原则**：框架化、模块化、可扩展
- **优缺点**：
  - ✅ 生态丰富，社区活跃
  - ✅ LangSmith 提供强大的评估与可观测性
  - ❌ 抽象层过多，可能引入额外复杂度
  - ❌ 性能依赖开发者实现（无内置优化）

---

## 适用场景

| 场景 | 推荐选择 | 理由 |
|------|----------|------|
| **终端原生 Agent** | OpenDev | 专为终端环境设计，支持长视野开发任务 |
| **IDE 集成 Agent** | Anthropic Harness | 与模型训练耦合，性能优化更好 |
| **快速原型开发** | LangChain | 生态丰富，抽象层完善，开发速度快 |
| **生产级部署** | Anthropic Harness 或 OpenDev | 需要细粒度控制和性能优化 |
| **评估与可观测性** | LangChain（LangSmith） | 专门的评估平台，Trace 分析强大 |

---

## 关键洞察

1. **Harness 设计不是一成不变的**：随着模型改进，Harness 中的假设会过时——要定期审视、去掉不再承重（load-bearing）的部分（来自 Anthropic 的 Harness 设计实践）

2. **最好的 Harness 不一定是被 post-train 的那个**：而是为你的任务优化过的那个（Anthropic 文章结论）

3. **上下文管理是核心挑战**：三者的上下文管理策略不同，但都面临「如何在有限上下文窗口中高效管理信息」的问题

4. **评估与可观测性是刚需**：LangChain 的 LangSmith 是三家中最成熟的评估平台，其他两家需要追赶

---

## 相关概念

- [[概念/Agent Harness]]
- [[概念/上下文工程]]
- [[概念/渐进式披露]]
- [[概念/自我验证循环]]

## 相关实体

- [[实体/Anthropic]]
- 
- [[实体/LangChain]]
- [[实体/LangSmith]]

## 相关来源

- [[来源/2026-04-25 The Anatomy of an Agent Harness]]
- [[来源/2026-04-25 Building Effective AI Coding Agents for the Terminal]]
- [[来源/2026-04-25 Improving Deep Agents with harness engineering]]


## 相关页面
- [[对比/模型选择策略对比]]
- [[对比/编码 Agent 架构对比]]
- [[实体/Anthropic]]
- [[实体/LangChain]]
- [[实体/LangSmith]]
- [[来源/2026-04-25 Building Effective AI Coding Agents for the Terminal]]
- [[来源/2026-04-25 Improving Deep Agents with harness engineering]]
- [[来源/2026-04-25 The Anatomy of an Agent Harness]]
- [[概念/Agent Harness]]
- [[概念/上下文工程]]
- [[概念/渐进式披露]]
- [[概念/自我验证循环]]