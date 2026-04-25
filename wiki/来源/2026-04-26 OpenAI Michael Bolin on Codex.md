---
date: 2026-04-26
type: 访谈转录
tags: [Codex, Harness, OpenAI, 沙箱, 开发者工作流]
sources: [raw/michael-bolin-codex.md]
original: https://www.youtube.com/watch?v=6BAqgT3qe98
---

# 来源摘要：OpenAI's Michael Bolin on Codex

## 素材概览

| 字段 | 内容 |
|------|------|
| 来源 | Turing Post 访谈（视频转录） |
| 嘉宾 | Michael Bolin — OpenAI Codex 开源负责人 |
| 时间 | 2026-03-14 发布 |
| 核心话题 | Harness 设计哲学、沙箱安全、Codex 如何改变开发者工作流 |

## 核心观点

### 1. Harness 到底是什么？

> "The harness is the bit that calls out to the model, samples the model, and gives it the context... then it gets that response — often that's a tool call."

Harness 的核心循环：
1. 调用模型
2. 采样模型输出
3. 给模型提供上下文和可用工具
4. 执行模型返回的工具调用
5. 把结果返回给模型

**Codex 的 Harness 设计哲学：尽可能小且紧凑**
- 只给 agent 少量但**非常强大**的工具
- 不提供显式的"读取文件"工具 → 而是给一个终端，让 agent 用 `cat`/`sed` 等命令自己读取
- 理由：让 agent **自己决定最佳路径**，而不是被过度指引

### 2. 安全 vs 安全（Security vs Safety）

Michael 强调这是两个不同概念（业界常混用）：

| 概念 | 含义 | Codex 中的实现 |
|------|------|-------------------|
| **Security（安全）** | 控制 agent 能访问哪些文件/执行哪些命令 | 沙箱机制：只能读这些文件夹、只能写这些文件夹 |
| **Safety（安全性）** | 确保模型建议的工具调用本身是"安全的" | 在模型训练时注入的安全对齐 |

**Harness 主要负责 Security**，Safety 更多由模型本身保证。

### 3. 沙箱实现（跨平台）

| 操作系统 | 沙箱技术 |
|----------|----------|
| macOS | Seatbelt（苹果原生） |
| Linux | bubblewrap + setcomp + landlock |
| Windows | OpenAI 自研沙箱（代码在开源 repo 中） |

用户 fork Codex 时，所有安全规则已经"内置"（baked in）。

### 4. Codex 发布与增长

- **2025年4月** — Codex 首次发布（基于 GPT-3/4o mini）
- **2025年8月** — GPT-5 发布 + CLI 刷新 → 开始真正增长
- **2025年夏末秋初** — VS Code 扩展发布 → VS Code 使用量超过 CLI
- **2026年初** — Codex App 发布 → 真正起飞

**使用量**：年初至今增长 **5x**。

### 5. Codex App：新的"任务控制"界面

不是传统的 IDE 插件，而是一个**并行管理多个 agent 对话**的界面：

- 浏览 agent 生成的 diff
- 一键打开终端（Command+J）
- 不需要把所有代码都打开（打破传统 IDE 的预期）
- **核心价值**：在多个 agent 之间组织和切换（这是当前很多用户的 top priority）

### 6. 如何改变开发者工作流

**变化1：吞吐量大幅提升**
- 可以同时运行多个 agent（Michael 个人同时开 5 个 Codex clone）
- 并行处理多个工作流
- 会议间隙的 5 分钟也能推进任务

**变化2：重新重视最佳实践**
- TDD（测试驱动开发）— 以前"值得吗？"，现在"显然值得"
- 文档 — 以前可能不写，现在 AGENTS.md 成为标准
- 代码审查 — Codex 做了大量代码审查工作，节省了时间

**变化3：优化新内循环**
- 开发者现在花时间优化"如何与 agent 协作"的工作流
- 把重复任务变成 skill 共享给团队
- 这是全新的技能，大家都在摸索

### 7. AGENTS.md 应该写什么？

**Codex 团队的做法：适度（modest）原则**

- AGENTS.md 应该包含**人类新人入职时需要知道的东西**
- 不要试图写一份与源代码平行的文档（容易重复、容易不一致）
- Agent 大部分时间应该在**读代码**（rip grep），形成自己的意见
- 只放那些 agent **无法从代码中快速获取**的信息：
  - 如何运行测试
  - 哪些测试更重要
  - 代码约定（style guide）

> "We try not to overdo it. Let the agent decide the best way forward."

### 8. 上下文工程：太多上下文可能有害

Michael 的经验：
- 对于较大的任务，他写 **about a paragraph**（约一段）的 prompt
- 让 Codex 先熟悉代码库（familiarize itself）
- 可以适当给文件指针，但很多时候 Codex 自己搜索得很好
- **太多上下文可能让 agent 变差**（diminishing returns）

**最佳实践**：
- 文件和文件夹命名清晰（agent 搜索代码时更重要）
- 好的架构 → agent 会遵循并维持它
- 差的架构 → agent 也会复制差的模式

### 9. 模型 vs Harness：哪个更重要？

Michael 的立场：**中间派**

> "The model is going to dominate... but there's still a lot of room for innovation in the harness."

- 更强的模型确实把 Codex 推到了新高度
- 但没有合适的 harness，那些模型无法可靠、安全地运行在开发者的机器上
- Harness 的任务是**尽可能小**，让模型自己闪耀

### 10. 未来方向

**更少的工具，但更强大的工具**
- 当前：给 agent 很多专门工具
- 未来：少量但非常强大的工具（如终端工具，让 agent 像人类一样使用计算机）

**Memory 是关键领域**
- 当前每次对话都从零开始（需要 AGENTS.md 和上下文填充）
- 未来：agent 能记住上次对话的内容

**多 agent 系统**
- Codex 团队正在探索 agent 跨机器协作
- Harness 不再只是单机进程，而是网络中的协调者

## 与已有 Wiki 概念的关联

| 本文概念 | 已有 Wiki 概念 | 关系 |
|------------|-------------------|------|
| Harness 设计哲学（小而精） | [[概念/Agent Harness]] | 补充：Codex 的 harness 实现细节 |
| 沙箱与跨平台安全 | [[概念/Agent Harness]] | 补充：Security 的具体实现 |
| AGENTS.md 适度原则 | [[概念/渐进式披露]] | 高度相关：不要给 agent 百科全书 |
| 太多上下文有害 | [[概念/上下文腐烂]] | 补充：主动避免 context rot |
| 让 agent 自己决定 | [[概念/Ralph Wiggum 循环]] | 相关：agent 自我驱动，而非过度指引 |
| 代码审查自动化 | [[概念/自我验证循环]] | 补充：Codex 的代码审查实践 |

## 提炼的可操作要点

1. **AGENTS.md 写什么？** 只写 agent 无法从代码中快速获取的信息（测试命令、重要测试、代码约定）
2. **工具设计原则**：少量但强大的工具 > 大量专门工具（让 agent 自己决定如何使用）
3. **避免上下文过载**：一段 prompt + 让 agent 先熟悉代码库，而不是一次性塞入所有信息
4. **沙箱是 Security 的核心**：不要让 agent 在无约束环境中运行
5. **架构质量直接影响 agent 输出**：agent 会遵循并维持已有的架构模式

## 引用来源

- `raw/michael-bolin-codex.md` — 完整转录（约 21 分钟）
- 原始视频：https://www.youtube.com/watch?v=6BAqgT3qe98
