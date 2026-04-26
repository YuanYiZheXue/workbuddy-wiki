---
type: source
tags: [agent, harness, long-running, anthropic, claude]
sources: [raw/Effective harnesses for long-running agents.md]
created: 2026-04-25
updated: 2026-04-25, Effective harnesses for long-running agents
---

# Effective harnesses for long-running agents

> 来源：
> 原文：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
> 作者：Justin Young（Anthropic）

## 一句话摘要

Anthropic 提出用「初始化 Agent + 编码 Agent」双 Agent 架构，配合 feature list、progress file、git commit 等工件，解决长运行 Agent 跨上下文窗口持续工作的难题。

## 核心问题

长运行 Agent 的两个失败模式：
1. **一次性做太多** — Agent 试图一步到位完成整个应用，导致上下文耗尽，下一会话接手时状态不明
2. **过早宣布完成** — 项目进行到一半，新 Agent 实例看到已有进展就宣布任务完成

根本原因：每个新会话从零开始，没有上一会话的记忆。

## 解决方案：双 Agent 架构

### Initializer Agent（初始化 Agent）
- 第一次会话使用专用 prompt
- 建立环境：`init.sh` 启动脚本
- 创建 `claude-progress.txt` 进度日志
- 生成初始 git commit
- 编写完整的 feature list（JSON 格式，所有功能初始标记为 `passes: false`）

### Coding Agent（编码 Agent）
- 后续每次会话使用不同 prompt
- 一次只做一个功能
- 会话结束时：git commit + 更新 progress file
- 只修改 feature list 中的 `passes` 字段，不删除或编辑测试用例

## 关键组件

### Feature List（功能列表）
- JSON 格式，每个功能包含：category、description、steps、passes
- 用 JSON 而非 Markdown，因为模型不太可能不当修改 JSON
- 例如克隆 claude.ai 时生成了 200+ 个功能项

### Incremental Progress（增量进展）
- 一次只做一个功能
- 会话结束前确保代码处于「干净状态」：无重大 bug、代码有序、有文档
- 类似「可以合并到 main 分支」的代码质量

### Testing（测试）
- 明确提示 Agent 使用浏览器自动化工具（如 Puppeteer MCP）做端到端测试
- Claude 通过 Puppeteer MCP 截图，验证功能是否真正工作
- 局限性：无法看到浏览器原生 alert 模态框

## 每个会话的标准流程

1. `pwd` 确认工作目录
2. 读取 git log 和 progress file 了解最近工作
3. 读取 feature list，选择最高优先级的未完成功能
4. 运行 `init.sh` 启动开发服务器
5. 做基础端到端测试，确认环境未损坏
6. 开始实现新功能
7. 结束时 git commit + 更新 progress file

## 相关概念

- [[概念/Agent Harness|Agent Harness]]
- [[概念/长运行 Agent]]

## 相关实体

- [[实体/Anthropic]]
- [[实体/LangChain]]
- [[概念/Agent Harness]]
- [[概念/长运行 Agent]]
- [[概念/上下文腐烂]]


## 相关页面
- [[实体/Anthropic]]
- [[对比/上下文工程方法对比]]
- [[对比/模型选择策略对比]]
- [[对比/编码 Agent 架构对比]]
- [[对比/长期记忆方案对比]]
- [[实体/LangChain]]
- [[概念/上下文腐烂]]
- [[概念/长运行 Agent]]