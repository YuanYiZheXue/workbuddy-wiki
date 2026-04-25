# 编码 Agent 架构对比

> 汲取自 `wiki/来源/` 中多篇素材的综合对比。

## 引言

编码 Agent（Coding Agent）的架构设计直接影响其可靠性、可维护性和扩展性。本文对比 Anthropic、OpenDev、LangChain、Codex 四大主流框架在编码 Agent 架构上的设计选择。

---

## 对比维度

| 维度 | Anthropic | OpenDev | LangChain | Codex |
|------|-----------|---------|-----------|-------|
| **架构类型** | Harness-based（外部循环） | Agent Loop（事件驱动） | LCEL Chain（声明式） | REPL Loop（代码执行） |
| **上下文管理** | 显式状态机（checkpoints） | 隐式上下文窗口 | 显式 Memory 对象 | 隐式（代码执行历史） |
| **工具调用** | Tool Use（显式） | Function Calling（显式） | Tool/Chain（显式） | Code Execution（隐式） |
| **记忆管理** | WorkBuddy Memory（文件持久化） | 无原生支持 | Memory 模块（向量存储） | 无原生支持 |
| **评估方法** | Harness Engineering（外循环评估） | 人工评估 | LangSmith（追踪+评估） | 无原生支持 |
| **可观测性** | Harness 全链路追踪 | 日志 | LangSmith（可视化） | 无原生支持 |
| **扩展性** | 高（Harness 可替换） | 中（依赖 OpenDev 平台） | 高（LCEL 可组合） | 低（依赖 Codex 模型） |

---

## 分析

### Anthropic：Harness-Based 架构

**核心理念**：Agent 是"在循环中调用的 LLM"，Harness 是"管理循环的软件"。

**架构图**：
```
User Input
    ↓
Harness（外循环）
    ↓
LLM（Claude）
    ↓
Tool Use（工具调用）
    ↓
Harness（处理结果）
    ↓
下一轮循环...
```

**优势**：
- 状态管理清晰（checkpoints）
- 可观测性强（全链路追踪）
- 可扩展性好（Harness 可替换）

**劣势**：
- 实现复杂（需要写 Harness 代码）
- 性能开销（外循环）

**适用场景**：需要高可靠性、可观测性的生产环境。

---

### OpenDev：Agent Loop 架构

**核心理念**：Agent 是"事件驱动的循环"，通过 Function Calling 调用工具。

**架构图**：
```
User Input
    ↓
Agent Loop（事件驱动）
    ↓
LLM（GPT-4）
    ↓
Function Calling（工具调用）
    ↓
Agent Loop（处理结果）
    ↓
下一轮循环...
```

**优势**：
- 实现简单（依赖 OpenDev 平台）
- 生态丰富（大量第三方工具）

**劣势**：
- 状态管理不清晰（隐式上下文窗口）
- 可观测性弱（依赖日志）
- 扩展性受限（依赖 OpenDev 平台）

**适用场景**：快速原型、依赖 OpenDev 生态的应用。

---

### LangChain：LCEL Chain 架构

**核心理念**：Agent 是"可组合的 Chain"，通过 LCEL（LangChain Expression Language）声明式定义。

**架构图**：
```
User Input
    ↓
Chain（LCEL 声明式）
    ↓
LLM（多种模型）
    ↓
Tool/Chain（工具调用）
    ↓
Chain（处理结果）
    ↓
下一轮循环...
```

**优势**：
- 灵活性强（LCEL 可组合）
- 生态丰富（大量第三方 Chain）
- 可观测性好（LangSmith）

**劣势**：
- 学习曲线陡（LCEL 语法）
- 性能开销（Chain 抽象）

**适用场景**：需要灵活组合、快速迭代的研究环境。

---

### Codex：REPL Loop 架构

**核心理念**：Agent 是"在 REPL 中运行的代码"，通过代码执行实现工具调用。

**架构图**：
```
User Input
    ↓
REPL Loop（代码执行）
    ↓
LLM（Codex）
    ↓
Code Execution（代码执行）
    ↓
REPL Loop（处理结果）
    ↓
下一轮循环...
```

**优势**：
- 实现简单（依赖代码执行）
- 自然表达（代码即工具）

**劣势**：
- 状态管理不清晰（隐式执行历史）
- 安全性风险（代码执行）
- 可观测性弱（依赖日志）

**适用场景**：代码生成、代码执行任务。

---

## 核心差异

### 1. 状态管理方式

| 框架 | 状态管理方式 | 优势 | 劣势 |
|------|--------------|------|------|
| Anthropic | 显式状态机（checkpoints） | 清晰、可观测 | 实现复杂 |
| OpenDev | 隐式上下文窗口 | 简单 | 不清晰 |
| LangChain | 显式 Memory 对象 | 灵活 | 需要手动管理 |
| Codex | 隐式执行历史 | 简单 | 不清晰 |

### 2. 工具调用方式

| 框架 | 工具调用方式 | 优势 | 劣势 |
|------|--------------|------|------|
| Anthropic | Tool Use（显式） | 清晰、可控 | 需要手动定义 |
| OpenDev | Function Calling（显式） | 生态丰富 | 依赖平台 |
| LangChain | Tool/Chain（显式） | 灵活、可组合 | 学习曲线陡 |
| Codex | Code Execution（隐式） | 自然表达 | 安全性风险 |

### 3. 记忆管理方式

| 框架 | 记忆管理方式 | 优势 | 劣势 |
|------|--------------|------|------|
| Anthropic | WorkBuddy Memory（文件持久化） | 持久化、可观测 | 需要手动管理 |
| OpenDev | 无原生支持 | - | 需要手动实现 |
| LangChain | Memory 模块（向量存储） | 自动、智能 | 依赖向量存储 |
| Codex | 无原生支持 | - | 需要手动实现 |

---

## 选择建议

### 选择 Anthropic 的场景

- 需要高可靠性、可观测性的生产环境
- 需要显式状态管理
- 需要自定义 Harness

### 选择 OpenDev 的场景

- 快速原型
- 依赖 OpenDev 生态
- 不需要复杂状态管理

### 选择 LangChain 的场景

- 需要灵活组合
- 快速迭代
- 依赖 LangChain 生态

### 选择 Codex 的场景

- 代码生成、代码执行任务
- 不需要复杂状态管理
- 不需要高可观测性

---

## 元一思想视角

用**元一思想**四原则分析：

| 原则 | 分析 |
|------|------|
| **存续为体，形式为用** | Anthropic 的 Harness 架构最符合——形式（Harness）服务于存续（可靠运行），但不过度设计。 |
| **流动趋效，均衡为度** | LangChain 的 LCEL 最灵活——信息流动快，但容易过载（Chain 太多）。需要均衡。 |
| **意义生于博弈，固于认同** | OpenDev 的生态最丰富——意义在与开发者的博弈中产生，但需要认同平台约束。 |
| **结构求稳，接口预变** | Anthropic 的 Harness 最稳定——结构（Harness 循环）不变，接口（Tool Use）可扩展。 |

**推荐选择**：
- **生产环境**：Anthropic（Harness 架构）
- **研究环境**：LangChain（LCEL 灵活性）
- **快速原型**：OpenDev（生态丰富）
- **代码任务**：Codex（自然表达）

---

## 参考资料

- [[来源/2026-04-25 Anthropic building effective agents]]
- [[来源/2026-04-25 Building Effective AI Coding Agents for the Terminal]]
- [[来源/2026-04-25 Effective harnesses for long-running agents]]
- [[来源/2026-04-25 What Harness Engineering Actually Means]]
- [[概念/Harness 工程]]
- [[概念/上下文工程]]

---

*本文是「对比」系列的第5篇。前4篇：[[对比/Agent Harness 设计对比]]、[[对比/上下文工程方法对比]]、[[对比/长期记忆方案对比]]、[[对比/Wiki 构建方法论对比]]。*
