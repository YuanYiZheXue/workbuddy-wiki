---
title: Obsidian-CLI 高级技巧速查表
type: 统筹
tags:
  - Obsidian
  - CLI
  - 速查表
  - 自动化
created: 2026-04-27
---

# Obsidian-CLI 高级技巧速查表

> Obsidian 1.12+ 官方 CLI 工具，可从终端控制 Obsidian，实现脚本编写、自动化和与外部工具集成。
> 
> **前置要求**：Obsidian 1.12.4+，在设置 → 常规中开启「Command line interface」。

---

## 基础命令

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看版本 | `obsidian version` | 验证 CLI 是否可用 |
| 查看帮助 | `obsidian help` | 显示所有可用命令 |
| 打开 vault | `obsidian open vault="知识库构建"` | 打开指定 vault |
| 打开指定文件 | `obsidian open file="笔记名"` | 打开指定笔记 |
| 新建窗口打开 | `obsidian open file="笔记名" new-window` | 新窗口打开 |

> **注意**：Obsidian CLI 是 GUI 的远程遥控器，执行命令时后台需要运行 Obsidian。

---

## 1. 日记自动化

| 场景 | 命令 | 说明 |
|------|------|------|
| 打开当天日记 | `obsidian daily` | 一键打开当天日记 |
| 追加待办任务 | `obsidian daily:append content="- [ ] 记得去遛狗" open` | 给当天日记追加任务并打开 |
| 统计当日待办总数 | `obsidian tasks daily total` | 统计当天日记中的任务数 |
| 标记任务完成 | `obsidian tasks daily done` | 标记当天日记任务为完成 |

**使用场景**：
- 每天早上自动打开日记
- AI Agent 自动记录每日笔记
- 快速添加待办任务

**示例：AI 自动记录每日工作**
```bash
# 让 AI 自动追加今日工作记录到日记
obsidian daily:append content="## $(date +%H:%M) 工作记录\n- 完成了 XXX" open
```

---

## 2. 文件管理

| 场景 | 命令 | 说明 |
|------|------|------|
| 创建笔记 | `obsidian create name="笔记名" content="# 标题\n内容"` | 创建新笔记 |
| 读取笔记 | `obsidian read file="笔记名"` | 读取笔记内容 |
| 追加内容 | `obsidian append file="笔记名" content="追加的内容"` | 追加内容到笔记末尾 |
| 重命名文件 | `obsidian rename file="旧名" new-name="新名"` | 重命名笔记 |
| 删除文件 | `obsidian delete file="笔记名"` | 删除笔记（谨慎使用） |

**使用场景**：
- AI Agent 自动创建/更新笔记
- 批量处理笔记内容
- 自动化知识库维护

**示例：AI 自动总结并写回**
```bash
# 1. 读取笔记内容
CONTENT=$(obsidian read file="项目笔记")

# 2. AI 处理内容（伪代码）
SUMMARY=$(ai_summarize "$CONTENT")

# 3. 写回总结
obsidian append file="项目笔记" content="\n\n## AI 总结\n$SUMMARY"
```

---

## 3. 搜索增强

| 场景 | 命令 | 说明 |
|------|------|------|
| 搜索匹配路径 | `obsidian search query="关键词"` | 只返回匹配的文件路径 |
| 搜索带上下文 | `obsidian search:context query="关键词" limit=10` | 返回匹配内容 + 上下文 |
| 在指定 vault 搜索 | `obsidian search query="关键词" vault="知识库构建"` | 指定 vault 搜索 |

**使用场景**：
- 快速查找相关笔记
- AI Agent 先搜索再读取（减少读取文件数）
- 构建 RAG 系统的检索环节

**示例：先搜索再读取（高效 RAG）**
```bash
# 1. 搜索相关笔记
obsidian search query="Git 技巧" vault="知识库构建"

# 2. 根据搜索结果，只读取相关笔记
obsidian read file="Git高级技巧速查表"
```

---

## 4. 任务管理

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看所有待办 | `obsidian tasks` | 显示所有未完成任务 |
| 查看指定文件任务 | `obsidian tasks file="笔记名"` | 显示指定文件中的任务 |
| 查看当日任务 | `obsidian tasks daily` | 显示当天日记中的任务 |
| 统计任务总数 | `obsidian tasks total` | 统计所有未完成任务数 |

---

## 5. 插件管理

| 场景 | 命令 | 说明 |
|------|------|------|
| 列出所有插件 | `obsidian plugin list` | 显示所有插件状态 |
| 启用插件 | `obsidian plugin:enable id=插件ID` | 启用指定插件 |
| 禁用插件 | `obsidian plugin:disable id=插件ID` | 禁用指定插件 |
| 重载插件 | `obsidian plugin:reload id=插件ID` | 重载指定插件（开发用） |

**使用场景**：
- 插件开发者快速调试（重载插件，无需重启 Obsidian）
- 自动化启用/禁用插件

**示例：插件开发快速重载**
```bash
# 修改插件代码后，一键重载
obsidian plugin:reload id=my-plugin
```

---

## 6. 开发者命令

| 场景 | 命令 | 说明 |
|------|------|------|
| 打开开发者工具 | `obsidian dev:console` | 打开浏览器开发者工具 |
| 截图当前界面 | `obsidian dev:screenshot path="ui-test.png"` | 截取 Obsidian 当前界面 |
| 执行 JavaScript | `obsidian dev:eval code="app.vault.getFiles()"` | 在 Obsidian 中执行 JS 代码 |
| 捕获错误日志 | `obsidian dev:errors` | 显示最近的错误 |

**使用场景**：
- 插件/主题开发调试
- UI 自动化测试（截图对比）
- 执行自定义 JS 脚本

---

## 7. 多 Vault 操作

> **重要**：多 vault 操作时，`vault=` 参数必须放在**所有参数最前面**。

| 场景 | 命令 | 说明 |
|------|------|------|
| 在指定 vault 操作 | `obsidian vault="知识库构建" open` | 打开指定 vault |
| 在指定 vault 创建笔记 | `obsidian vault="知识库构建" create name="新笔记"` | 在指定 vault 创建笔记 |
| 在指定 vault 搜索 | `obsidian vault="知识库构建" search query="关键词"` | 在指定 vault 搜索 |

**错误示例**（❌ 不要这样写)：
```bash
obsidian open vault="知识库构建" file="笔记名"   # 错误：vault 参数位置不对
```

**正确示例**(✅)：
```bash
obsidian vault="知识库构建" open file="笔记名"   # 正确：vault 在最前面
```

---

## 8. 高级自动化技巧

### 8.1 AI Agent 对接 Obsidian（RAG 全流程）

```bash
# 1. 用户提问："Git 高级技巧有哪些？"

# 2. AI 先搜索相关笔记
obsidian search query="Git 高级技巧" vault="知识库构建"

# 3. 根据搜索结果，读取相关笔记
obsidian read file="Git高级技巧速查表" vault="知识库构建"

# 4. AI 处理内容，生成回答

# 5. 将回答追加到日记（记录对话）
obsidian daily:append content="## AI 回答\nGit 高级技巧包括..." open
```

### 8.2 批量处理笔记（结合 shell 脚本）

```bash
# 批量给笔记添加标签
for file in $(obsidian search query="Git" vault="知识库构建"); do
  obsidian append file="$file" content="\ntags: [Git]"
done
```

### 8.3 定时自动备份（结合 cron）

```bash
# 每天凌晨 2 点自动 git 备份 Obsidian vault
# crontab -e
0 2 * * * cd /path/to/vault && git add -A && git commit -m "auto: daily backup" && git push
```

---

## 9. 常见问题避坑

### 9.1 命令无法识别

**原因**：环境变量未生效。

**解决**：
- Mac：`source ~/.zprofile` 或重启终端
- Windows：重启 Obsidian，重新开启 CLI 功能

### 9.2 Windows 中文乱码

**原因**：Obsidian 1.12.4 以下版本的 bug。

**解决**：升级到 Obsidian 1.12.4+。

### 9.3 多 Vault 操作失败

**原因**：`vault=` 参数位置不对。

**解决**：确保 `vault=` 在所有参数最前面。

### 9.4 CLI 命令执行后无反应

**原因**：Obsidian 未运行。

**解决**：先打开 Obsidian，再执行 CLI 命令。

---

## 10. PowerShell 环境注意事项

| 问题 | 解决方案 |
|------|----------|
| `obsidian` 命令找不到 | 重启 PowerShell，或手动添加 Obsidian 到 PATH |
| 中文参数乱码 | 确保 Obsidian 1.12.4+，使用 UTF-8 编码 |
| 执行后无输出 | 检查 Obsidian 是否正在运行 |

**PowerShell 示例**：
```powershell
# 打开当天日记
obsidian daily

# 追加内容（注意转义）
obsidian daily:append content="`- [ ] 待办任务" open
```

---

## 更新记录

| 日期 | 变更内容 |
|------|----------|
| 2026-04-27 | 初始化文档，整理 Obsidian-CLI 10 类高级技巧 |
