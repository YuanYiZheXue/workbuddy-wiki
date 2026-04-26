---
type: source
tags: [ralph wiggum, loop, coding agent, geoffrey huntley]
sources: [raw/Ralph Wiggum as a _software engineer_.md]
created: 2026-04-25, Ralph Wiggum as a _software engineer_
---

# Ralph Wiggum as a "software engineer"

> 来源：
> 原文：https://ghuntley.com/ralph/
> 作者：Geoffrey Huntley

## 一句话摘要

Ralph Wiggum 不是一个AI，而是一个**技巧**：用一个 `while` 循环不断地把 prompt 喂给编码 Agent，让它 autonomously 工作。文章详细描述了如何用这个技巧从零构建一个全新的编程语言（CURSED），以及调优 prompt 的系统方法。

## 核心理念

### Ralph Wiggum 技巧的本质

> **"The technique is deterministically bad in an undeterministic world."**

Ralph 在最纯粹的形式下就是一个 Bash while 循环：
```bash
while :; do cat PROMPT.md | claude-code ; done
```

- 不依赖 Agent 框架，任何不限制 tool call 数量的工具都能用
- Ralph 会测试你——每次 Ralph 走错方向，不是工具的错，而是需要"调音"（tune Ralph）
- **信仰最终一致性（eventual consistency）**——Ralph 最终会做对

### 一个循环只做一件事（One Item Per Loop）

这是最重要的原则：**每次循环只让 Ralph 做一件事**。

- 上下文窗口约 170k tokens，必须尽可能少用
- 用 `@fix_plan.md` 和规格文件（specs/）来确定性地分配上下文
- 随着项目进展可以放松这个限制，但一旦跑偏就要收回到"只做一件事"

### 用子 Agent 扩展上下文（Subagents）

Ralph 的核心思维：**主上下文窗口只做调度器**，昂贵的分析工作交给子 Agent。

> "Your task is to implement... using parrallel subagents."

- 搜索文件系统、写文件 → 可以用多个子 Agent
- 构建/测试 → 只用1个子 Agent（避免背压/backpressure）
- 子 Agent 是扩展上下文窗口的实际手段

### 反向压力（Backpressure）

代码生成现在很便宜，难的是**确保 Ralph 生成了正确的东西**。

- 用类型系统、测试、静态分析器作为反向压力
- 动态类型语言必须接入静态分析器（如 Erlang 的 Dialyzer、Python 的 Pyrefly）
- 每次实现功能后立即跑测试（future loops 不会记得为什么要写这个测试）

### 不假设未实现（Don't Assume It's Not Implemented）

Ralph 的常见失败模式：`ripgrep` 搜索结果导致 LLM 错误判断某功能还未实现。

- 修复方法：在 prompt 里写"搜索代码库（不要假设未实现），用子 Agent 做"
- 非确定性是 Ralph 的阿喀琉斯之踵

### AGENTS.md / PROMPT.md 的调优

没有完美的 prompt，只有不断调优的 prompt。

- prompt 是随着观察 LLM 行为而演进的，不能照搬别人的
- CURSED 的 prompt 演进过程：观察 → 发现坏行为 → 在 prompt 里竖牌子（"SLIDE DOWN, DON'T JUMP, LOOK AROUND"）
- Ralph 最终会只想着那些"牌子"，这时你就得到了不感觉有缺陷的新 Ralph

### TODO 列表与 fix_plan.md

- `fix_plan.md` 是优先级排序的待办列表，由子 Agent 维护
- Ralph 跑完 TODO 或跑偏时，删除 TODO 列表，让 Ralph 重新生成一个新的
- 人类的作用是判断：是 `git reset --hard` 重来，还是写新 prompt 救回 Ralph？

## 与现有概念的关系

- 本文是对 **[[概念/Ralph Wiggum 循环]]** 最详细的操作指南
- **[[概念/自我验证循环]]** — Ralph 的"测试后立即验证"是自我验证的实操版
- **[[概念/渐进式披露]]** — `@fix_plan.md`、`@specs/*` 是渐进式披露的实践
- **[[概念/上下文腐烂]]** — 170k 上下文窗口限制，需要子 Agent 和 fix_plan.md 来应对

## 关键引用

- Ralph Wiggum 技巧原始页面：https://ghuntley.com/ralph/
- CURSED 项目：https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md
- Venture Beat 报道：https://venturebeat.com/technology/how-ralph-wiggum-went-from-the-simpsons-to-the-biggest-name-in-ai-right-now


## 相关页面
- [[概念/Agent Harness]]
- [[概念/Ralph Wiggum 循环]]
- [[概念/上下文工程]]
- [[概念/上下文腐烂]]
- [[概念/渐进式披露]]
- [[概念/自我验证循环]]