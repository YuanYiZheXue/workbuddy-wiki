---
type: source
tags: [harness, martin fowler, birgitta böckeler, coding agent]
sources: [raw/Harness engineering for coding agent users.md]
created: 2026-04-25, Harness engineering for coding agent users
---

# Harness Engineering for Coding Agent Users

> 来源：
> 原文：https://martinfowler.com/articles/harness-engineering.html
> 作者：Birgitta Böckeler（Thoughtworks）

## 一句话摘要

为编码 Agent 用户定义"外层 Harness"：通过前馈引导（feedforward guides）和反馈传感器（feedback sensors）来构建对 Agent 的信任。提出 Computational vs Inferential 的分类，以及可维护性/架构适配/行为三类 Harness。

## 核心理念

### 术语界定：Agent = Model + Harness

在编码 Agent 的语境下，Harness 分为两层：
- **内层 Harness**：编码 Agent 自带的（system prompt、代码检索机制、编排系统）
- **外层 Harness**：用户为特定用例构建的定制层 ← 本文焦点

> "A well-built outer harness serves two goals: it increases the probability that the agent gets it right in the first place, and it provides a feedback loop that self-corrects as many issues as possible."

### Computational vs Inferential

两个执行类型的引导和传感器：

| 类型 | 特征 | 例子 |
|------|------|--------|
| **Computational** | 确定性、快，CPU 执行 | 测试、linter、类型检查、结构分析 |
| **Inferential** | 语义分析、AI 代码审查、"LLM as judge" | 代码审查 Agent、设计审查 |

- Computational 便宜又快，可以每次改动都跑
- Inferential 更贵且非确定，但能提供丰富的引导和有价值的判断
- 好的 Harness 设计是混合使用两者

### Steering Loop（方向盘循环）

人类的 job 是**通过迭代 Harness 来引导 Agent**。

每次问题重复出现时，应该改进前馈控制和反馈控制，使问题在未来更少发生（甚至防止它发生）。

> "Whenever an issue happens multiple times, the feedforward and feedback controls should be improved."

Agent 可以帮助构建 Harness：写结构测试、从观察模式中生成规则草案、搭建定制 linter、从代码库考古中创建 how-to 指南。

### 时机：把质量左移（Shift Left）

受持续集成/持续交付的启发，按成本、速度和关键性分布检查和审查：

**变更生命周期中的前馈和反馈：**
- 提交前就能跑的（快、便宜）：linter、快速测试套件、基础代码审查 Agent
- 提交后流水线里跑的（更贵）：变异测试、更全面的代码审查
- 持续运行的（监控漂移）：死代码检测、测试覆盖率质量分析、依赖扫描

### 三类调节维度

Harness 调节代码库朝向期望状态，可分为三类：

#### 1. Maintainability Harness（可维护性 Harness）
调节内部代码质量。
- Computational 传感器可靠地捕捉：重复代码、圈复杂度、测试覆盖率缺失、架构漂移、风格违规
- LLM 可以部分解决需要语义判断的问题（语义重复代码、过度工程化），但昂贵且概率性
- **目前最成熟的 Harness 类型**

#### 2. Architecture Fitness Harness（架构适配 Harness）
定义和检查应用的架构特征（Fitness Functions）。
- 前馈：描述性能需求的 Skill、性能测试作为反馈
- 前馈：描述可观测性编码规范的 Skill（如日志标准）
- 反馈：让 Agent 反思可用日志质量的 Skill

#### 3. Behaviour Harness（行为 Harness）
**房间里的 elephant**——如何引导和感知应用功能行为是否符合需要？
- 目前大多数人的做法：功能规格（各种详细程度）+ AI 生成的测试套件 + 人工测试
- 问题：对 AI 生成的测试的信任过度
- approved fixtures 模式有一定帮助，但不是完整答案
- **目前最薄弱的 Harness 类型**

### Harnessability（可 Harness 性）

不是每个代码库都同样适合 Harness。

- 强类型语言天然有类型检查作为传感器
- 明确定义的模块边界支持架构约束规则
- 框架（如 Spring）抽象掉细节，Agent 不需要担心，因此隐式提高成功率
- **Greenfield vs Legacy**：Greenfield 团队可以从第1天就烘焙 Harnessability；Legacy 团队最需要 Harness，但也最难构建

### Harness Templates（Harness 模板）

大多数企业有几种常见的服务拓扑（业务服务、事件处理服务、数据仪表盘），覆盖 80% 的需求。

- 这些拓扑已经在服务模板中固化
- 未来可能演化为 **Harness 模板**：一套引导和传感器的捆绑包，将编码 Agent 约束到拓扑的结构、约定和技术栈
- 问题：模板实例化后会与上游改进脱节（类似服务模板的问题），且非确定性引导/传感器更难测试

## 与现有概念的关系

- 本文是对 **[[概念/Agent Harness|Agent Harness]]** 的深入扩展，特别是"外层 Harness"
- **[[概念/上下文工程]]** — 前馈引导的设计属于上下文工程的一部分
- **[[概念/自我验证循环]]** — 反馈传感器本质是自我验证循环
- 新概念：**Harnessability**、**Steering Loop**、**Behaviour Harness**

## 关键引用

- Anthropic 的双 Agent 架构：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Stripe 的 minions：https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents
- Approved Fixtures 模式：https://lexler.github.io/augmented-coding-patterns/patterns/approved-fixtures/
- Architecture Fitness Function：https://www.thoughtworks.com/en-de/radar/techniques/architectural-fitness-function


## 相关页面
- [[上下文工程]]
- [[自我验证循环]]