---
date: 2026-04-26
type: 来源
tags: [michael-bolin, codex, openai, interview, transcript]
source: https://www.youtube.com/watch?v=6BAqgT3qe98
author: Turing Post
published: 2026-03-14
description: Michael Bolin（OpenAI Codex 开源负责人）访谈转录——关于 Harness、Agent 循环、安全沙箱
---

# Michael Bolin on Codex — 访谈转录

（本页面由 AI 根据原始资料自动生成，请人工审核）

## 核心论点

关于"模型和 harness 哪个更重要"的问题，Michael Bolin 持中间立场。更强的模型显然将 Codex 推向了新的高度，但如果没有正确的 harness，这些模型无法可靠、安全地在实际开发者的机器上运行。

## 关键概念

### 1. Harness 是什么？

- **Harness 是让编码智能体实际运作的工程层**：智能体循环、沙箱化、工具编排、决定智能体应该有多少自由的设计决策
- **没有 harness，模型无法可靠地运行**：特别是在真实开发者的机器上安全运行

### 2. Codex 的 Harness 设计原则

#### 尽可能小和紧凑
- Codex 的 harness 设计得尽可能小和紧凑
- 原因：减少攻击面，提高安全性

#### 沙箱化和安全
- Codex 跨操作系统处理沙箱化
- **安全 ≠ 安保**：安全是系统的可靠性；安保是防止恶意攻击
- Codex 在两者上都投入了大量工作

#### 文档、测试、仓库结构突然更重要
- 当智能体成为代码库的贡献者时，清晰的文档和测试突然变得更重要
- 智能体需要理解仓库结构和测试套件

### 3. 上下文工程与 Prompting

#### 太多上下文可能让智能体变得更差
- 这是 Codex 工程团队的重要发现
- 需要在提供足够上下文和避免过度填充之间找到平衡

#### 为 Codex 进行 Prompting
- 不需要过度详细的 prompt
- 让模型自己决定最佳路径
- Codex 插件（Claude Code）可能不是最佳选择

### 4. 多智能体系统、工具和未来

#### 未来的工具可能更少但更强大
- Michael 相信未来可能涉及更少的工具，但更强大的工具
- 让智能体自己决定使用哪些工具

#### 软件工程师在智能体时代的作用
- 工程师仍然需要：智能体无法 100% 替代人类
- 但 Ralph 技术可以替代大多数公司的外包工作（针对 Greenfield 项目）

## 与 Wiki 主题的联系

### 与「Agent Harness」的关系

Michael Bolin 的访谈详细解释了 Agent Harness 的概念：
- **Harness 是让智能体实际运作的工程层**
- **没有 harness，模型无法可靠地运行**
- 这与 Anthropic 的"Agent = Model + Harness"理念一致

### 与「上下文工程」的关系

Michael 提到"太多上下文可能让智能体变得更差"：
- 这与上下文工程的核心问题一致：如何管理上下文窗口，让它不溢出？
- Codex 工程团队在上下文管理上投入了大量工作

### 与「元一思想」的关系

Michael Bolin 的观点体现了元一思想的多个原则：
1. **存续为体**：Codex 的目的是帮助开发者完成项目，不是为了完美而存在
2. **形式为用**：Harness 设计得尽可能小和紧凑（"形式"服务于"存续"）
3. **流动趋效**：上下文工程管理需要平衡信息量和智能体性能
4. **结构求稳**：沙箱化提供稳定安全保障，但 harness 设计可以迭代

## 可提取的知识点

- [x] Harness 的定义和重要性
- [x] Codex 的 Harness 设计原则（小、紧凑、安全）
- [x] 安全 ≠ 安保
- [x] 太多上下文可能让智能体变得更差
- [x] 未来的工具可能更少但更强大
- [x] 软件工程师在智能体时代的作用

## 待解决问题

- [ ] 如何确定"正确"的 harness 大小？
- [ ] 如何平衡上下文数量和智能体性能？
- [ ] 如何让智能体更好地理解仓库结构和测试套件？

## 引用来源

- 原始资料：`raw/michael-bolin-codex.md`（YouTube 视频转录）
- 视频链接：https://www.youtube.com/watch?v=6BAqgT3qe98
- Turing Post：https://www.turingpost.com/

## 相关概念

- [[概念/Agent Harness]] — Michael Bolin 详细解释的概念
- [[概念/上下文工程]] — Michael 提到太多上下文可能让智能体变得更差
-  — Codex 跨操作系统处理的议题

## 相关实体

-  — 访谈嘉宾，OpenAI Codex 开源负责人
-  — Michael Bolin 所在的公司
-  — Michael Bolin 领导的开源项目


## 相关页面
- [[概念/Agent Harness]]
- [[概念/上下文工程]]