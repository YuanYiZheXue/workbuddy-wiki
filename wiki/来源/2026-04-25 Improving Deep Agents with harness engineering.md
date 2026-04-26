---
type: source
tags: [agent, harness, langchain, trace-analysis, self-verification]
sources: [raw/Improving Deep Agents with harness engineering.md]
created: 2026-04-25
updated: 2026-04-25, Improving Deep Agents with harness engineering
---

# Improving Deep Agents with Harness Engineering

> 来源：
> 原文：https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering
> 作者：Vivek Trivedy（LangChain）

## 一句话摘要

只改 Harness 不改模型，把 LangChain 编码 Agent 在 Terminal Bench 2.0 上从 Top 30 提升到 Top 5——核心手段是 Trace 分析 + Self-verification + Middleware 三板斧。

## 实验设置

- **基准**：Terminal Bench 2.0（89 个任务，涵盖机器学习、调试、生物学等）
- **工具**：LangSmith（追踪）+ Harbor（编排沙箱）+ Daytona（沙箱环境）
- **模型**：固定用 `gpt-5.2-codex`，只改 harness
- **起点分**：52.8%（默认 prompt + 标准工具/middleWare）
- **终点分**：66.5%（+13.7 分）

## Harness 上可以拧的「旋钮」

文章把 Harness 组件压缩到三个可操作维度：

| 旋钮 | 内容 |
|------|------|
| **System Prompt** | 解决问题的引导方式 |
| **Tools** | 可用工具集 |
| **Middleware**（钩子/中间件） | model 和 tool 调用前后的钩子 |

## 实际有效的改进

### 1. Build & Self-Verify（构建 + 自我验证）

**失败模式**：Agent 写完代码 → 重读自己的代码 → 确认「看起来 OK」→ 停止。没有真正测试。

**解决方案**：在 system prompt 里注入明确的 4 步工作流：

1. **Planning & Discovery**：读任务、扫描代码库、制定初始计划
2. **Build**：以实现验证为目标写代码，写测试（happy path + edge case）
3. **Verify**：运行测试、读完整输出、对比原始需求（不是对比自己的代码）
4. **Fix**：分析错误、重读原始规格、修复问题

**PreCompletionChecklistMiddleware**：在 Agent 退出前拦截，强制跑一遍验证清单（类似 Ralph Wiggum Loop 的验证版）。

### 2. Giving Agents Context about their Environment（环境上下文引导）

三个子手段：

- **LocalContextMiddleware**：Agent 启动时扫描 `cwd` 及父子目录，运行 `bash` 找可用工具（如 Python 安装）——帮助 Agent「登入」环境
- **Teaching Agents to Write Testable Code**：在 prompt 里强调工作将按程序化测试评分，迫使 Agent 写可被验证的代码（避免「看起来对」但实测失败）
- **Time Budgeting**：注入时间预算警告，nudge Agent 在完成工作和转向验证之间切换（Agent 不擅长时间估计）

> **Harness 工程师的目的**：准备和交付上下文，让 Agent 可以自主完成任务。

### 3. Encouraging Agents to Step Back & Reconsider Plans（防止死循环）

**失败模式**：Agent 决定一个方案后变得短视，对同一错误方案做微小变体循环（doom loop），某些 trace 中达 10+ 次。

**LoopDetectionMiddleware**：通过 tool call 钩子追踪每文件的编辑次数。同一文件编辑 N 次后，注入提示：「…consider reconsidering your approach」。

> 注意：这是针对**当今模型缺陷**的设计启发。随着模型改进，这类 guardrail 可能变得不必要。

### 4. Choosing How Much Compute to Spend on Reasoning（推理预算）

`gpt-5.2-codex` 有 4 种推理模式：`low` / `medium` / `high` / `xhigh`。

**Reasoning Sandwich（推理三明治）**：
- 规划阶段：`xhigh`
- 实现阶段：`high`
- 验证阶段：`xhigh`

| 策略 | 分数 |
|------|------|
| 全程 `xhigh` | 53.9%（超时太多） |
| 全程 `high` | 63.6% |
| Reasoning Sandwich | **66.5%** |

**未来方向**：自适应推理（Claude、Gemini 已支持模型自主决定推理预算）；多模型 harness（规划用大模型，实现用小模型 handoff）。

## Trace Analyzer Skill（追踪分析技能）

把「分析跨 run 的错误并改进 harness」变成可复现的流程：

1. 从 LangSmith 获取实验 trace
2. 并行启动错误分析 Agent → 主 Agent 综合发现 + 建议
3. 聚合反馈，针对性修改 harness

类似 Boosting（机器学习）：专注于前一轮做错的样本。人类可以在第 3 步参与验证，防止过拟合到特定任务。

## 实践要点（Practical Takeaways）

1. **Context Engineering on Behalf of Agents** — 帮 Agent 做上下文工程（目录结构、可用工具、编码最佳实践、问题解决策略）
2. **Help Agents Self-Verify** — 激进地 prompt Agent 验证自己的工作
3. **Tracing as Feedback Signal** — Trace 让 Agent 自我评估和调试
4. **Detect and Fix Bad Patterns Short Term** — 针对当今模型缺陷设计 guardrail，但预期它们会随模型改进而过时
5. **Tailor Harnesses to Models** — 不同模型需要不同 prompt 策略，要为每个模型跑几轮 harness 迭代

## 与前面文章的关系

| 本文贡献 | 与前面文章的关联 |
|----------|----------------|
| Trace 分析 → 迭代改进 harness | 对应「What Harness Engineering Actually Means」中的「根据错误改进 AGENTS.md」 |
| Self-verification loop | 对应「Anatomy of Agent Harness」中的 Self-verification 原语 |
| Middleware/hooks | 是 Harness 原语的具象实现（在 ReAct 循环里插入钩子） |
| Progressive Disclosure | LangChain 的 Skills 机制正是渐进式披露的实现 |

## 相关概念

- [[概念/Agent Harness|Agent Harness]]
- [[概念/自我验证循环]]
- [[概念/上下文工程]]
- [[概念/渐进式披露]]

## 相关实体

- [[实体/LangChain]]
- [[实体/Vivek Trivedy]]
- [[实体/LangSmith]]
- [[实体/Terminal Bench]]


## 相关页面
- [[实体/LangChain]]
- [[实体/Vivek Trivedy]]
- [[对比/Agent Harness 设计对比]]
- [[对比/长期记忆方案对比]]
- [[实体/LangSmith]]
- [[实体/Terminal Bench]]
- [[概念/上下文工程]]
- [[概念/渐进式披露]]
- [[概念/自我验证循环]]