---
type: source
tags: [opendev, rust, terminal agent, context engineering]
sources: [raw/Building Effective AI Coding Agents for the Terminal.pdf, raw/building-effective-ai-agents-txt.txt]
created: 2026-04-25, Building Effective AI Coding Agents for the Terminal.pdf
---

# Building Effective AI Coding Agents for the Terminal

> 来源：
> GitHub：https://github.com/opendev-to/opendev
> 作者：Nghi D. Qui（OpenDev）

## 一句话摘要

OPENDEV 是一个开元的、用 Rust 编写的终端原生 AI 编码 Agent，采用复台 AI 系统架木（compound AI system）：Plan Mode（只读子 Agent 规划）+ Normal Mode（完整工具执行）， Lazy Tool Discovery、Adaptive Context Compaction 和事件驱动的系统提醒来应对长视野开发。

## 核心理念

### 复台 AI 系统架木（Compound AI System）

> "State-of-the-art AI results are increasingly achieved by systems that compose multiple models, retrievers, and tools."

OPENDEV 不是单一 LLM 调用，而是 Agents 和 Workflows 的结构化编排，每一层独立绑定到用户配置的 LLM。

**四层架木：**
1. **Entry & UI Layer** 一解析参数、目举四个共享管理器（Config、Session、Mode、Approval）
2. **Agent Layer** 一分配专门化模型角色，惰性初始化
3. **Tool & Context Layer** 一工具注册表派发、上下文工积管理
4. **Persistence Layer** 一跨会话持久化（Config、Conversation History、Provider Cache、Operation Log）

### 双模式架木：Plan Mode + Normal Mode

**Plan Mode（规划模式）：**
- 派发一个 Planner 子 Agent（只读工具）
- 探索代码库、分析模式、产出结构化计划文件（7个部分：goal/context/files-to-modify/new-files/implementation-steps/verification-criteria/risks）
- 用户批准后，系统转到 Normal Mode 执行

**Normal Mode（执行模式）：**
- 完整工具访问
- 按 planned steps 执行
- 遇意外结果时，可再次派发 Planner 子 Agent 修订计划

**为什么用子 Agent 做规划？**
- 早期设计用 state machine 切换主 Agent 进出 plan mode，但 Agent 有时会卡在只读状态
- 当前设计把规划委托给子 Agent，主 Agent 全程保持在 Normal Mode
- 优势：(1) 不会卡住 (2) 可并发派发其他子 Agent (3) 工具表面更小，认知负载更低

### Extended ReAct 执行管道

标准 ReAct 循环扩展为四个阶段：
1. **Pre-check & Compaction** 一检育 token 利用率，应用上下文压缩
2. **Thinking（可选）** 一分离 deliberation 与 action，提升推理质量
3. **Self-critique（可选）** 一 action 前的自我批评
4. **Action** 一 tool calls，通过 Tool Registry 派发

### 上下文工程（Context Engineering）作为一等公民

**Adaptive Context Compaction（自适应上下文压缩）**
- 多阶段压缩管道：上下文窗口快满时，逐步压缩旧 observation
- 与 Anthropic 的 compaction 理念一致，但是事件驱动 + 优先级排序

**Event-Driven System Reminders（事件驱动系统提醒）**
- 应对 instruction fade-out（指令遇渐遗忘）
- 不在 system prompt 里堆所有规则，而是在决策点注入目标引导
- 条件化 prompt 组合管道：独立、优先级排序的 section，只在上下文相关时加载（渐进式披露）

**Memory Pipeline（记忆管道）**
- 跨会话积累项目特定知识
- playbook.md 存储学到的策略，随反馈演进
- instruction fade-out 通过事件驱动提醒来对抗

### 五层纵深防御安全架木

| 层 | 位置 | 机制 |
|---|---|---|
| L1: Prompt-Level Guardrails | system prompt | security policy、action safety、read-before-edit、git workflow、error recovery |
| L2: Schema-Level Tool Restrictions | tool schema | plan-mode whitelist、per-subagent allowed_tools、MCP discovery gating |
| L3: Runtime Approval System | 运行时 | Manual/Semi-Auto/Auto 三档、pattern/command/prefix/danger rules、持久化权限 |
| L4: Tool-Level Validation | 工具执行前 | DANGEROUS_PATTERNS 黑名单、stale-read detection、output truncation、timeouts |
| L5: Lifecycle Hooks | 全生命周期 | pre-tool blocking（exit code 2）、argument mutation、JSON stdin protocol |

失败模式：单 layer 失败不 compromise 系统（纵深防御）

### Lazy Tool Discovery（惰性工具发现）

- 工具不预加载，通过 MCP（Model Context Protocol）运行时发现
- Tool Registry 派发到专门 handler（文件操作、进程执行、Web 访问）
- Skills System：三级层级（built-in、project、user），惰性注入可复用、领域特定的 prompt 模板

### 设计演进（Lessons Learned）

1. **Eager Build vs Lazy Build** 一早期用 lazy prompt building（第一次 run_sync() 时构建 system prompt），导致 first-call 延迟 + MCP 工具注册后不出现在 prompt 里。改为 Eager Build：__init__() 时立即构建 system prompt 和 tool schemas。
2. **单类参数化 vs 类层次结构** 一早期为每种 Agent 类型建子类（PlannerAgent、CodeExplorerAgent 等），导致 diamond problem（需要混合能力时）。改为单类 MainAgent，通过构造参数（allowed_tools、_subagent_system_prompt、is_subagent 标侨）实现行为变化。
3. **Subagent 编译管道** 一从硬编码子 Agent 构造，改为 SubAgentSpec（TypedDict）→ register_subagent() → 运行时惰性实列化。用户可通过配置文件定义自定义子 Agent。

## 与现有概念的关系

- [[概念/Agent Harness|Agent Harness]] 一 OPENDEV 是 Agent = Model + Harness 的完整实现案例
- [[概念/上下文工程]] 一上下文工程作为一等公民，多阶段压缩 + 事件驱动提醒
- [[概念/自我验证循环]] 一 Extended ReAct 管道的可选 Self-critique 阶段
- [[概念/Ralph Wiggum 循环]] 一 OPENDEV 有类似"循环"但更结构化（双模式 + 子 Agent 派发）
- [[概念/渐进式披露]] 一条件化 prompt 组合管道，只在上下文相关时加载 section

## 关键引用

- OPENDEV GitHub：https://github.com/opendev-to/opendev
- Compound AI Systems：[103] Zaharia et al.
- Model Routing：[62] 相关研究
- Context Engineering 理论：[39, 56] 近期工作
- Anthropic Effective Harnesses：[18] 双 Agent 架木


## 相关页面
- [[对比/Agent Harness 设计对比]]
- [[对比/上下文工程方法对比]]
- [[对比/模型选择策略对比]]
- [[对比/编码 Agent 架构对比]]
- [[对比/长期记忆方案对比]]
- [[概念/Ralph Wiggum 循环]]
- [[概念/上下文工程]]
- [[概念/渐进式披露]]
- [[概念/自我验证循环]]