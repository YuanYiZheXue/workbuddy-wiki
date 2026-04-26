---
type: concept
tags: [agent, long-running, context-window]
sources: [来源/2026-04-25 Effective harnesses for long-running agents, 来源/2026-04-25 The Anatomy of an Agent Harness]
created: 2026-04-25
updated: 2026-04-25
---

# 长运行 Agent

## 定义

需要跨多个上下文窗口、持续工作数小时甚至数天的 Agent。核心挑战：每个新会话从零开始，没有上一会话的记忆。

## 两个主要失败模式

1. **一次性做太多（one-shot）** — Agent 试图一步到位，导致上下文耗尽，下一会话接手时状态不明
2. **过早宣布完成** — 新 Agent 实例看到已有进展就宣布任务完成

## 解决方案（Anthropic 双 Agent 架构）

### Initializer Agent
- 第一次会话专用 prompt
- 建立环境：`init.sh`、`claude-progress.txt`、初始 git commit
- 编写完整 feature list（JSON 格式，初始全标记为 `passes: false`）

### Coding Agent
- 后续每次会话不同 prompt
- 一次只做一个功能
- 会话结束：git commit + 更新 progress file
- 只修改 `passes` 字段，不删除测试用例

## 长视野执行的关键要素（LangChain 框架）

- **持久状态**：文件系统 + git 跨会话追踪工作
- **Ralph Loop**：干净上下文重新注入原始 prompt，强制继续工作
- **Planning + Self-verification**：分解目标、每步验证

## 与 Wiki 方法的联系

Wiki 方法本质上解决了同样的问题——跨会话知识持久化：
- Wiki = 持久状态（类比 feature list + progress file）
- Ingest = 增量进展（类比一次只做一个功能）
- Lint = 自我验证（类比测试循环）

## 相关概念

- [[概念/Agent Harness|Agent Harness]]
- [[概念/上下文腐烂]]
- [[概念/元一思想]] — 「结构求稳」的具体实践

- [[实体/Anthropic]]
- [[实体/Claude Agent SDK]]
- [[来源/2026-04-25 Effective harnesses for long-running agents]]
- [[来源/2026-04-25 Harness design for long-running application development]]
- [[来源/2026-04-25 The Anatomy of an Agent Harness]]
- [[概念/Ralph Wiggum 循环]]
- [[概念/上下文腐烂]]
- [[概念/自我验证循环]]
- [[实体/LangChain]]
- [[概念/元一思想]]
## 相关实体

- [[实体/Anthropic]]
- [[实体/LangChain]]
