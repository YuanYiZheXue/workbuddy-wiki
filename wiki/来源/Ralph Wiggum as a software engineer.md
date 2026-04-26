---
date: 2026-04-26
type: 来源
tags: [ralph-wiggum, coding-agent, loop, bootstrap]
source: https://ghuntley.com/ralph/
author: Geoffrey Huntley
published: 2025-07-14
description: Ralph Wiggum 技术详解：如何用 Bash 循环构建编程语言和复杂系统
---

# Ralph Wiggum as a "software engineer"

（本页面由 AI 根据原始资料自动生成，请人工审核）

## 核心论点

Ralph Wiggum 不是一个人物，而是一种技术——一个 Bash 循环：
```
while :; do cat PROMPT.md | claude-code ; done
```

Ralph 可以替代大多数公司的外包工作（针对 Greenfield 项目）。它正在构建一种全新的编程语言（CURSED），而且这种语言不在 LLM 的训练数据中。

## 关键概念

### 1. Ralph 的本质

- **Bash 循环**：最简单的 Ralph 形式
- **确定性中的非确定性**：在一个不确定的世界中，Ralph 技术在确定性方面表现出色
- **单一责任**：每个循环只做一件事（one item per loop）

### 2. 上下文窗口管理

- **问题**：上下文窗口约 170k tokens，使用越多，输出质量越差
- **解决方案**：不要填满主上下文窗口，而是生成子代理（subagents）
- **主上下文窗口应该作为调度器**：调度其他子代理执行昂贵的工作

### 3. 不要假设它没有实现

- 代码搜索（如 `ripgrep`）可能是非确定性的
- 常见失败场景：LLM 运行 `ripgrep` 后错误地认为代码没有实现
- **解决方案**：在 PROMPT 中添加"在做出更改前搜索代码库（不要假设项目未实现）"

### 4. 两阶段：生成 + 背压（Backpressure）

#### 阶段一：生成
- 代码生成现在很便宜
- Ralph 生成的代码完全在你的控制之下（通过技术标准库和规范）

#### 阶段二：背压
- 确保 Ralph 生成了正确的东西
- 通过类型系统、测试、静态分析器等提供背压
- **关键**：轮子必须转得快（快速反馈循环）

### 5. 捕捉测试的重要性

- 因为 Ralph 每个循环只做一件事，每个循环都有新的上下文窗口
- 至关重要的是在那一刻要求 Ralph 写出测试的意义和重要性
- **原因**：未来的循环将没有推理在它们的上下文窗口中

### 6. 不要作弊

- Claude 有内在的偏见去做最小化和占位符实现
- **解决方案**：在 PROMPT 中添加"不要实现占位符或简单实现。我们要完整实现。做它，否则我会对你大喊大叫"
- 如果 Ralph 忽略了这个"标志"，运行更多 Ralph 来识别占位符和最小实现，并将其转换为未来 Ralph 循环的待办事项列表

### 7. TODO 列表

- Ralph 会运行完待办事项列表中的事情，或者完全偏离轨道
- **关键**：TODO 列表是你在密切关注的
- 如果 Ralph 偏离了，就扔掉 TODO 列表，重新生成一个新的

### 8. 循环回来是一切

- 以 Ralph 可以循环回来的方式编程
- 例如：添加额外的日志记录，以便能够调试问题

### 9. Ralph 可以把自己送到大学

- `@AGENT.md` 是循环的核心
- 当 Ralph 发现一个学习点时，允许它自我改进
- **关键**：捕捉推理（更新 `@fix_plan.md`、`@AGENT.md`）

### 10. 你会醒来发现代码库坏了

- 有时 Ralph 会破坏代码库
- **决策**：是 `git reset --hard` 更容易，还是需要提出一系列新的提示来拯救 Ralph？
- **经验**：有时将编译错误文件扔给 Gemini，要求 Gemini 为 Ralph 创建一个计划

## 与 Wiki 主题的联系

### 与「自我验证循环」的关系

Ralph Wiggum 循环本质上是「自我验证循环」的极端形式：
- **自我验证循环**（Anthropic/LangChain 语境）：Generator + Evaluator 架构
- **Ralph Wiggum 循环**（Geoffrey Huntley 语境）：Bash 循环 + 持续迭代

**本质相同**：强制智能体验证自己的工作再继续，而不是一路生成到底。

### 与「上下文工程」的关系

Ralph Wiggum 技术是上下文工程的一个极端案例：
- **核心问题**：如何管理上下文窗口，让它不溢出？
- **Ralph 的答案**：每个循环只做一件事，使用子代理处理昂贵的工作

### 与「元一思想」的关系

Ralph Wiggum 技术体现了元一思想的多个原则：
- **存续为体**：Ralph 的目的是完成项目，不是为了完美而存在
- **形式为用**：Bash 循环是"形式"，可以调整（调整 PROMPT.md）
- **流动趋效**：每个循环只做一件事，提高效率
- **结构求稳**：`@AGENT.md`、`@fix_plan.md` 提供稳定结构

## 可提取的知识点

- [x] Ralph Wiggum 技术定义（Bash 循环）
- [x] 上下文窗口管理策略（子代理）
- [x] 背压（Backpressure）概念
- [x] TODO 列表管理
- [x] 自我改进机制

## 待解决问题

- [ ] CURSED 编程语言的具体实现细节（需要更多资料）
- [ ] Ralph 技术在不同项目类型中的适用性
- [ ] 如何判断什么时候该 `git reset --hard`，什么时候该继续调试

## 引用来源

- 原始资料：`raw/Ralph Wiggum as a _software engineer_.md`
- 作者网站：https://ghuntley.com/ralph/
- 相关视频：https://www.youtube.com/watch?v=4Nna09dG_c0
- 相关视频：https://www.youtube.com/watch?v=O2bBWDoxO4s

## 相关概念

- [[概念/Ralph Wiggum 循环]] — 同一核心理念的不同表述
- [[概念/自我验证循环]] — 强制智能体验证自己的工作
- [[概念/上下文工程]] — 如何管理上下文窗口
- [[概念/Agent Harness]] — Ralph 技术是一种特殊的 Harness

## 相关实体

-  — 文章作者
-  — Ralph 技术使用的工具
