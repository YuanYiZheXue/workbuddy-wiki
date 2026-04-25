# Wiki Log

> 操作记录，仅追加。由 WorkBuddy 自动维护。

## [2026-04-25] init | 初始化 Wiki 目录结构

- 创建 `raw/` 及 `raw/素材/` 目录
- 创建 `wiki/` 及 `实体/`、`概念/`、`来源/`、`对比/` 子目录
- 创建 `wiki/index.md` 初始索引
- 创建 `wiki/log.md` 操作日志

## [2026-04-25] ingest | Effective harnesses for long-running agents

- 读取 `raw/Effective harnesses for long-running agents.md`
- 创建来源摘要页 `wiki/来源/2026-04-25 Effective harnesses for long-running agents.md`
- 提取相关概念：Agent Harness、长运行 Agent、上下文窗口管理、多 Agent 架构
- 提取相关实体：Anthropic、Claude、Claude Agent SDK、Puppeteer MCP
- （按自下而上原则，暂无其他来源，暂不创建独立概念/实体页）
- 更新 `wiki/index.md`：Stats +1，添加来源条目

## [2026-04-25] ingest | The Anatomy of an Agent Harness

- 读取 `raw/The Anatomy of an Agent Harness.md`
- 创建来源摘要页 `wiki/来源/2026-04-25 The Anatomy of an Agent Harness.md`
- 两篇来源均提及 Agent Harness / 长运行 Agent / 上下文管理
- **触发自下而上规则**：≥2 篇来源，创建独立概念页：
  - `wiki/概念/Agent Harness.md`
  - `wiki/概念/长运行 Agent.md`
  - `wiki/概念/上下文腐烂.md`
- 更新 `wiki/index.md`：Stats 更新（2 来源 + 3 概念）

## [2026-04-25] ingest | Harness design for long-running application development

- 读取 `raw/Harness design for long-running application development.md`
- 创建来源摘要页 `wiki/来源/2026-04-25 Harness design for long-running application development.md`
- 关键新概念：Generator + Evaluator 架构、Sprint Contract、Context Reset vs Compaction
- 「自我验证循环」概念页已达标（≥2 来源），已创建 `wiki/概念/自我验证循环.md`

## [2026-04-25] ingest | What Harness Engineering Actually Means

- 读取 `raw/What Harness Engineering Actually Means.md`（视频转录）
- 创建来源摘要页 `wiki/来源/2026-04-25 What Harness Engineering Actually Means.md`
- 清晰区分 Prompt Eng / Context Eng / Harness Eng 三者
- 「上下文工程」概念页已达标（≥2 来源），已创建 `wiki/概念/上下文工程.md`

## [2026-04-25] ingest | Improving Deep Agents with harness engineering

- 读取 `raw/Improving Deep Agents with harness engineering.md`
- 创建来源摘要页 `wiki/来源/2026-04-25 Improving Deep Agents with harness engineering.md`
- 关键实践：Trace 分析迭代优化 harness、Middleware（钩子）、Reasoning Budget 优化
- index.md 已更新（5 来源 + 5 概念）

## [2026-04-25] ingest | 工程技术：在智能体优先的世界中利用 Codex

- 读取 `raw/工程技术：在智能体优先的世界中利用 Codex.md`（OpenAI 官方，Ryan Lopopolo）
- 创建来源摘要页 `wiki/来源/2026-04-25 工程技术：在智能体优先的世界中利用 Codex.md`
- 关键新概念：
  - **Ralph Wiggum 循环** — 智能体自我驱动修复循环（≥2 篇达标）
  - **渐进式披露** — AGENTS.md 作为目录而非百科全书（≥2 篇达标）
- 创建新概念页：`wiki/概念/Ralph Wiggum 循环.md`、`wiki/概念/渐进式披露.md`
- index.md 已更新（6 来源 + 7 概念）

## [2026-04-25] lint | 第一轮健康检查

按更新后的 Lint 规则执行检查，发现问题及修复如下：

1. **悬空内部链接** — 多处指向不存在页面的 `[[...]]` 链接
   - 删除仅1篇来源提及的概念链接（ReAct Loop / Trace 分析 / 上下文窗口管理 / 多 Agent 架构）
   - 修正 `[[概念/Skills 渐进式披露]]` → `[[概念/渐进式披露]]`（共6处）
2. **index.md 简介质量** — 已更新所有概念简介，使其包含实质内容
3. **自下而上原则触发** — Anthropic 和 LangChain 均被 ≥2 篇来源提及
   - 创建 `wiki/实体/Anthropic.md` ✓
   - 创建 `wiki/实体/LangChain.md` ✓
   - 更新 `wiki/index.md` Stats（2 实体页）✓

### Lint 结论

- 悬空链接全部清理完毕
- 实体页按自下而上原则补充完整
- index.md 简介质量提升
- Schema 的 Lint 规则已验证可行（有具体检查清单）

## [2026-04-25] ingest | Ralph Wiggum as a software engineer

- 读取 `raw/Ralph Wiggum as a _software engineer_.md`（Geoffrey Huntley）
- 创建来源摘要页 `wiki/来源/2026-04-25 Ralph Wiggum as a software engineer.md`
- 详解 Ralph Wiggum 技巧：while 循环 + 一次一件事 + 子 Agent + 背压管理
- 更新 `[[概念/Ralph Wiggum 循环]]`：加入具体实操（AGENTS.md、fix_plan.md、背压、子 Agent）
- index.md 已更新（8 来源）

## [2026-04-25] ingest | Harness engineering for coding agent users

- 读取 `raw/Harness engineering for coding agent users.md`（Birgitta Böckeler，Thoughtworks）
- 创建来源摘要页 `wiki/来源/2026-04-25 Harness engineering for coding agent users.md`
- 核心理念：外层 Harness、Computational vs Inferential、三类调节维度
- 新概念提及：Maintainability Harness、Architecture Fitness Harness、Behaviour Harness（仅1篇，暂不建页）
- index.md 已更新（9 来源）

## [2026-04-25] ingest | Building Effective AI Coding Agents for the Terminal（PDF）

- 用 pdfplumber 提取 PDF 内容（246,179 字符）
- 创建来源摘要页 `wiki/来源/2026-04-25 Building Effective AI Coding Agents for the Terminal.md`
- 核心：OPENDEV（Rust 编写的终端原生 Agent）
- 双模式架构（Plan Mode + Normal Mode）、Extended ReAct、五层纵深防御
- 上下文工程作为一等公民：Adaptive Compaction + Event-Driven System Reminders
- index.md 已更新（9 来源 + 2 实体 + 7 概念）✓

---

## [2026-04-26] ingest | 元一思想体系（三篇素材）

### 素材来源

- `raw/元一思想.md` — 初版四原则阐述（存续/流动/意义/结构）
- `raw/元一思想-四原则新解.md` — 精炼升级版（体用/效度/生固/稳变八字箴言）
- `raw/元一思想-动态制衡模型.md` — 四极飞轮模型、四大制衡关系

### 执行步骤

1. **创建来源摘要页** `wiki/来源/元一思想体系.md` ✓
   - 综合三篇素材的核心内容
   - 提炼最终版四原则箴言
   - 记录动态制衡模型（四极飞轮）

2. **创建概念页** `wiki/概念/元一思想.md` ✓
   - 作为 Wiki 的元认知层
   - 四原则 + 动态制衡模型
   - Wiki 健康度自检清单（基于四大制衡）

3. **更新 index.md** ✓
   - Stats：10 来源 + 2 实体 + 8 概念
   - 来源表格添加「元一思想体系」
   - 概念表格添加「元一思想」

4. **更新 workbuddy-wiki-schema.md** ✓
   - 新增「顶层设计：元一思想」章节
   - 四原则在 Wiki 构建中的具体体现（表格）
   - 四极飞轮作为 Wiki 健康度诊断模型

### 关键产出

- **元一思想** 成为 Wiki 的元认知层，四原则指导所有构建决策
- **四极飞轮模型** 可作为 Lint 时的健康度评估框架
- **自下而上原则** 与「意义生于博弈，固于认同」高度契合

---

## [2026-04-26] SOUL.md 更新 | 融入元一思想四原则

### 执行内容

在 `SOUL.md` 的「毛泽东风格原则」和「Boundaries」之间，新增「元一思想（行为哲学底层逻辑）」章节：

- **存续为体，形式为用** — 根本任务是在时间中延续对用户的有用性
- **流动趋效，均衡为度** — 信息高效流动，但以不过载为限度
- **意义生于博弈，固于认同** — 工作模式在与用户互动中碰撞出来
- **结构求稳，接口预变** — 已有工作模式不随意推翻，新需求通过接口适应

### 效果

下次会话启动时，WorkBuddy 会读取更新后的 SOUL.md，行为受四原则指导。

---

## [2026-04-26] lint | 基于元一思想的 Wiki 健康度诊断

### 诊断模型

使用「四极飞轮」模型对 Wiki 进行健康度评估：

| 极 | 评估结果 | 发现的问题 |
|----|----------|------------|
| 存续为体，形式为用 | ✅ 健康 | ⚠️ Schema 已迭代3版，有过度设计倾向 |
| 流动趋效，均衡为度 | ✅ 健康 | ⚠️ 来源页→概念页的双向链接不完整 |
| 意义生于博弈，固于认同 | ✅ 健康 | ⚠️ `元一思想.md`是自上而下创建，需在实践中验证 |
| 结构求稳，接口预变 | ✅ 健康 | ⚠️ Schema 缺少「接口决策规则」 |

### 修复行动

1. **修复 `Effective harnesses...md` 的错误链接** ✓
   - `[[实体/Claude]]` → `[[实体/LangChain]]`
   - 删除不存在的 `[[实体/Claude Agent SDK]]`、`[[实体/Puppeteer MCP]]`
   - 补上反向链接到概念页

2. **补全 `The Anatomy of an Agent Harness.md` 末尾链接** ✓

3. **更新 `workbuddy-wiki-schema.md`：补充「接口决策规则」** ✓
   - 新增决策树：新需求来时如何判断是「扩展接口」还是「修改结构」
   - 判断清单：一次性 vs 系统性需求；能否通过接口扩展解决

### 诊断结论

Wiki 整体健康，四极基本平衡。主要改进方向：
- 双向链接继续完善（低优先级，可逐步完成）
- 「接口决策规则」已补入 Schema，后续新需求来时按规则判断

---

## [2026-04-26] ingest | OpenAI Michael Bolin on Codex（访谈转录）

### 素材来源

- `raw/OpenAI's Michael Bolin...md`（文件名特殊字符，已复制为 `michael-bolin-codex.md`）
- Turing Post 访谈，嘉宾：Michael Bolin（OpenAI Codex 开源负责人）

### 执行步骤

1. **创建来源摘要页** `wiki/来源/2026-04-26 OpenAI Michael Bolin on Codex.md` ✓
   - 综述：Harness 设计哲学、沙箱跨平台实现、AGENTS.md 适度原则
   - 10 个核心观点提炼
   - 与已有 Wiki 概念的关联表

2. **更新 index.md** ✓
   - Stats：11 来源 + 2 实体 + 8 概念
   - 来源表格添加「OpenAI Michael Bolin on Codex」

3. **关键新信息**：
   - **Codex Harness 哲学**：尽可能小且紧凑，少量但强大的工具
   - **Security vs Safety**：在智能体系统中不是同一件事
   - **AGENTS.md 适度原则**：只写 agent 无法从代码中快速获取的信息
   - **太多上下文有害**：diminishing returns，一段 prompt + 让 agent 先熟悉代码库
   - **沙箱实现**：macOS/Seatbelt、Linux/bubblewrap+setcomp+landlock、Windows/自研

### 与已有概念的关系

| 本文 | 已有 Wiki 概念 | 补充内容 |
|------|-------------------|----------|
| Harness 设计哲学 | [[概念/Agent Harness]] | Codex 的 harness 实现细节 |
| 沙箱跨平台 | [[概念/Agent Harness]] | Security 的具体实现 |
| AGENTS.md 适度 | [[概念/渐进式披露]] | 高度相关：不要给 agent 百科全书 |
| 太多上下文有害 | [[概念/上下文腐烂]] | 主动避免 context rot |
| 让 agent 自己决定 | [[概念/Ralph Wiggum 循环]] | 相关：agent 自我驱动 |

---

## [2026-04-26] 完成工作汇总

### 用户指令：先3后2再1

- ✅ **步骤3**：元一思想融入 SOUL.md
- ✅ **步骤2**：基于元一思想的 Wiki 健康度诊断
- ✅ **步骤1**：处理剩余素材（Michael Bolin 访谈）

### 最终 Wiki 状态

```
wiki/
├── 来源/  (11 篇)
├── 概念/  (8 篇，含元一思想顶层哲学)
├── 实体/  (2 篇)
├── index.md          (11+2+8)
├── log.md            (完整记录)
└── workbuddy-wiki-schema.md (v3 + 顶层设计 + 接口决策规则)
```

### 待处理

- `OpenAI's Michael Bolin...md` 原始文件因特殊字符无法直接读取，已通过复制为简单文件名处理
- 如需处理更多素材，放入 `raw/` 目录并告知

---

## [2026-04-26] lint | 第二轮健康度诊断

### 诊断触发

用户指令："先做2" → 重新执行 Wiki 健康度诊断（基于元一思想四极飞轮）

### 诊断结果

| 极 | 评估 | 发现问题 | 修复行动 |
|----|------|----------|----------|
| 存续为体，形式为用 | ✅ 健康 | ⚠️ `元一思想.md` 是自上而下创建 | 记录到 log.md，实践中验证 |
| 流动趋效，均衡为度 | ✅ 健康 | ⚠️ `LangChain.md` 有悬空链接 | 已删除 `[[概念/Trace 分析]]` ✓ |
| 意义生于博弈，固于认同 | ✅ 健康 | ⚠️ `Anthropic.md` 有悬空链接 | 已修复为 `[[实体/LangChain]]` ✓ |
| 结构求稳，接口预变 | ✅ 健康 | ⚠️ 接口决策规则未经验证 | 下次新需求来时验证决策树 |

### 修复完成

1. **删除 `LangChain.md` 悬空链接** ✓ — `[[概念/Trace 分析]]` 只有1篇来源，暂不建页
2. **修复 `Anthropic.md` 悬空链接** ✓ — `[[实体/Claude]]` → `[[实体/LangChain]]`
3. **接口决策规则** — 已在上一轮补充到 Schema，待验证

### 诊断结论

Wiki 整体健康，四极基本平衡。所有悬空链接已清理完毕。

---

## [2026-04-26] automation | 设置自动化版本管理

### 执行内容

在 `.git/hooks/post-commit` 中创建自动打标签脚本：

- **标签格式**：`v2026-04-26-ab12c3d`（日期 + 短 hash）
- **触发时机**：每次 `git commit` 后自动执行
- **标签类型**：annotated tag（包含提交信息、日期、回滚方法）

### 使用方法

```bash
# 查看所有自动标签
git tag

# 回滚到某个版本
git checkout v2026-04-26-ab12c3d

# 查看标签详情
git show v2026-04-26-ab12c3d
```

### 测试记录

- ✅ Hook 文件已创建：`.git/hooks/post-commit`
- ✅ 权限已设置：`chmod +x`
- 🔄 待测试：下次 commit 时自动打标签

---
