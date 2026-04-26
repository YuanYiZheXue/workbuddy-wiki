---
type: source
tags: [harness-engineering, prompt-engineering, context-engineering, louis-bouchard]
sources: [raw/What Harness Engineering Actually Means.md]
created: 2026-04-25
updated: 2026-04-25, What Harness Engineering Actually Means
---

# What Harness Engineering Actually Means

> 来源：
> 视频：https://www.youtube.com/watch?v=zYerCzIexCg
> 作者：Louis-François Bouchard（What's AI）

## 一句话摘要

清晰区分 Prompt Engineering、Context Engineering 和 Harness Engineering 三者：分别是「问什么」、「给什么上下文」和「整个系统如何运作」。

## 核心概念区分

### Prompt Engineering
- **定义**：如何向模型提问
- **范围**：单条 prompt 的措辞、结构、示例
- **类比**：汽车的燃料（没有它车跑不了，但只有燃料造不出好车）

### Context Engineering
- **定义**：为了让模型能够自信地回答，应该往上下文窗口里放什么
- **范围**：检索什么、排除什么、如何总结、何时 evict
- **类比**：汽车的操作手册和仪表盘信息（让驾驶员（模型）知道当前状态）
- **关键洞察**：更大的上下文窗口不等于更好的性能（噪声更多 = 上下文腐烂更快）

### Harness Engineering
- **定义**：整个系统如何运作——模型周围的环境
- **范围**：可用工具、权限、携带状态、必须通过的测试、捕获的日志、重试次数、检查点、护栏、review、阻止系统漂移到无意义输出的 eval
- **类比**：汽车的方向盘、刹车、车道边界、维护计划、警告灯、「门不会在高速公路上掉下来」

> **Context engineering lives inside harness engineering. 但两者不是同一件事。**

## 关键论点

### 为什么 Harness Engineering 现在重要？

1. **Agents 已经足够好到有用了，但还不够可靠到可以信任它们独立工作**
2. **模型能力提升 → 瓶颈从「它能生成代码吗？」变成「我能让它在可控制的真实系统中可靠地表现吗？」**
3. Cursor 和 Claude Code 流行的原因：**不只是模型，而是整个系统**

### 核心心态转变

> 每次 Agent 犯错，不要只是希望下次更好。**设计环境让它不能以同样方式再犯同样的错误。**

具体做法：
- 根据真实错误行为改进 `AGENTS.md` / `CLAUDE.md`
- 添加脚本、linter、检查、工具，让 Agent 可以验证和修复自己的工作
- **这把负担从「等待下一个模型发布」移回「构建者当下可以做什么」**

### Progressive Disclosure（渐进式披露）的重要性

- 把整个公司知识库塞进一个巨大的 agent 文件 → Agent 不会变聪明，通常变得更糟
- 更多噪声、更多上下文腐烂、更多东西被静默忽略
- **更好的模式**：前面放一个短的 map，更深的 truth source 只在需要时拉入
- 这就是 Harness 里面的 Context Engineering

## Mitchell Hashimoto 命名了这件事

2026 年 2 月初，Mitchell Hashimoto 给了这件事一个名字：**Harness Engineering**。

作者认为这个命名框架是术语流行起来的原因——它给了人们一个概念把手。

## 实际影响

### 编程者的工作正在转移（不是消失）

- 更少时间手动敲每一行代码
- **更多时间设计「栖息地」**：让 Agent 可以在其中做有用工作而不会搞砸周围一切
- 更多机器可读的文档、更多 eval、更多沙箱、更多权限边界、更多结构化测试、更多日志/追踪/可重放性

### 可靠性的真实工作

- 记忆仍然会断
- 验证仍然会漏掉东西
- 工具使用仍然会产生安全风险
- **Harness 深度是真实的**：你的 harness 变成它自己的产品，有它自己的 bug 和漂移
- 人类注意力变成真正稀缺的资源

→ 需要让可靠性进入系统本身。因为我们无法永远手动审查所有东西。

## 与 Wiki 方法的映射

| 本文理念 | Wiki 方法对应 |
|----------|--------------|
| Harness = 方向盘+刹车+护栏 | Wiki 的 index/log/memory 构成护栏系统 |
| 根据错误改进 AGENTS.md | WorkBuddy 与用户共同演进 Schema |
| Progressive Disclosure | WorkBuddy Skills：按需加载，不挤满上下文 |
| 把可靠性建进系统 | Wiki 持久化知识，不依赖模型记忆 |
| 人类设计栖息地 | 用户负责方向，WorkBuddy 负责苦力活 |

## 相关概念

- [[概念/Agent Harness|Agent Harness]]
- [[概念/上下文腐烂]]
- [[概念/渐进式披露]]
- [[概念/上下文工程]]

## 相关实体

- [[实体/Anthropic]]（Claude Code）
- [[实体/LangChain]]（Mitchell Hashimoto 提及）
- [[实体/Cursor]]


## 相关页面
- [[实体/Anthropic]]
- [[对比/上下文工程方法对比]]
- [[对比/编码 Agent 架构对比]]
- [[概念/渐进式披露]]
- [[实体/Cursor]]
- [[实体/LangChain]]
- [[概念/上下文工程]]
- [[概念/上下文腐烂]]