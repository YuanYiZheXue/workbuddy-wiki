---
title: "子知识库 Git 操作规范"
summary: "统一各子知识库 agent 的 Git 提交流程与双远程同步规范 v1.1"
created: 2026-04-27
updated: 2026-04-27
version: "v1.1"
---

# 子知识库 Git 操作规范

> 本文档适用于所有子知识库 agent（哲哲/数数/算算/金金）。
> 各子知识库 `.workbuddy/` 目录下有简化版指南，指向本文档。

---

## 仓库结构

| 子知识库 | 工作空间路径 | 分支名 | Agent |
|---------|-------------|--------|-------|
| 哲学 | `d:/Obsidian_KN/哲学思想` | `kb/philosophy` | 哲哲 |
| 数学 | `d:/Obsidian_KN/数学` | `kb/math` | 数数 |
| 计算机与AI | `d:/Obsidian_KN/理工` | `kb/computer-ai` | 算算 |
| 金融 | `d:/Obsidian_KN/金融交易` | `kb/finance` | 金金 |

- **主仓库**：`d:\Obsidian_KN\知识库构建`（分支 `main`）
- **双远程**：`origin`（GitHub，公开）+ `gitee`（Gitee，**私有，仅作者可访问**），必须同步推送
- **子知识库本质**：主仓库的**分支**，不是独立仓库，远程地址与主仓库相同
- **Gitee 私有说明**：Gitee 仓库内容为私有，外部用户无法访问，仅作为个人备份使用

---

## Git 环境

### ⚠️ Git 命令路径（重要）

PowerShell 环境中 `git` 可能不在 PATH，**推荐使用完整路径调用**：

```powershell
& "C:\Program Files\Git\bin\git.exe" <args>
```

> **所有下文命令示例均使用完整路径**。如果 agent 环境中 `git` 可直接调用，可简化为 `git`。

### Python 环境
- **命令**：`python`（系统默认）
- **注意**：PowerShell 中 `python` 可能指向 Anaconda，需确认版本
- **验证**：`python --version`

### PowerShell 注意事项
- **不支持 `&&`**，用 `;` 分隔命令
- **中文路径编码问题**：`execute_command` 传中文参数会乱码，需在终端手动运行

---

## 远程仓库地址

子知识库是主仓库的分支，远程地址与主仓库**完全相同**。

### 查看当前远程地址
```powershell
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/哲学思想" remote -v
```

### 标准远程地址（主仓库）

| 远程名 | 地址 | 可见性 |
|--------|------|----------|
| `origin` (GitHub) | `https://github.com/YuanYiZheXue/workbuddy-wiki.git` | **公开** |
| `gitee` (Gitee) | `https://gitee.com/yuanyizhexue/workbuddy-wiki.git` | **私有**（仅作者可访问） |

> 注意：实际推送时使用带 token 的地址（由 `git remote set-url` 配置），
> agent 只需确认 `git remote -v` 显示 `origin` 和 `gitee` 两个远程即可。

### 配置远程地址（如缺失）

```powershell
# 添加 GitHub 远程
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" remote add origin https://github.com/YuanYiZheXue/workbuddy-wiki.git

# 添加 Gitee 远程
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" remote add gitee https://gitee.com/yuanyizhexue/workbuddy-wiki.git
```

---

## 标准提交流程

### 1. 检查状态
```powershell
# 查看工作区状态
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" status --short

# 查看最近提交
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" log --oneline -5
```

### 2. 暂存与提交
```powershell
# 暂存所有变更
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" add -A

# 提交（消息用中文，简洁描述）
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" commit -m "类型: 简要描述"
```

**提交消息规范**：
- 格式：`类型: 简要描述`
- 类型：`docs`（文档）、`feat`（新功能）、`fix`（修复）、`refactor`（重构）
- 示例：`docs: 新增XX笔记`、`fix: 修正XX错误`

### 3. 双远程同步推送
```powershell
# 推送到 GitHub
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" push origin 分支名

# 推送到 Gitee
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" push gitee 分支名
```

**关键**：两个远程都要推，不能只推一个。

### 4. 验证同步
```powershell
# 查看远程状态
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" remote -v

# 查看未推送的提交
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" log --oneline origin/分支名..HEAD
```

---

## 首次推送流程（重要）

> 子知识库第一次推送时，远程可能已有内容（无关历史），需要处理。

### 情况 A：远程分支不存在（推荐）
```powershell
# 直接推送，设置上游跟踪
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" push -u origin 分支名
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" push -u gitee 分支名
```

### 情况 B：远程已有内容，历史无关
```powershell
# 先拉取远程内容（允许无关历史）
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" pull origin 分支名 --allow-unrelated-histories

# 如果有冲突，编辑冲突文件后：
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" add -A
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" commit -m "merge: 合并无关历史"

# 再推送
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" push origin 分支名
```

### 情况 C：冲突太多，想强制推送（⚠️ 风险）
```powershell
# 强制推送会覆盖远程历史，仅在确认远程内容可丢弃时使用
& "C:\Program Files\Git\bin\git.exe" -C "子知识库路径" push origin 分支名 --force
```

> **建议**：首次推送优先用情况 A 或 B，避免 `--force`。

---

## 常用命令速查

| 场景 | 命令 |
|------|------|
| 查看状态 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" status --short` |
| 暂存所有 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" add -A` |
| 提交 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" commit -m "消息"` |
| 推 GitHub | `& "C:\Program Files\Git\bin\git.exe" -C "路径" push origin 分支名` |
| 推 Gitee | `& "C:\Program Files\Git\bin\git.exe" -C "路径" push gitee 分支名` |
| 拉取更新 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" pull origin 分支名` |
| 查看历史 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" log --oneline -10` |
| 查看差异 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" diff` |
| 查看远程 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" remote -v` |
| 撤销暂存 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" reset HEAD 文件名` |
| 丢弃修改 | `& "C:\Program Files\Git\bin\git.exe" -C "路径" checkout -- 文件名` |

---

## 配置文件：`.gitignore`（防止素材目录被上传）

子知识库根目录应存在 `.gitignore` 文件，排除不必要文件。

### 标准 `.gitignore` 模板

```
# Obsidian 临时文件
.obsidian/workspace*
.obsidian/cache
.obsidian/*.json.bak

# WorkBuddy 记忆文件（可选，如需同步则注释掉）
# .workbuddy/memory/

# 素材目录（如不需要上传）
wiki/素材/

# Python
__pycache__/
*.pyc
*.pyo

# 系统文件
.DS_Store
Thumbs.db

# 临时文件
*.tmp
*.bak
*.swp
```

> **验证**：如果 `wiki/素材/` 已被提交到远程，需要先删除远程内容：
> ```powershell
> & "C:\Program Files\Git\bin\git.exe" -C "路径" rm -r --cached wiki/素材/
> & "C:\Program Files\Git\bin\git.exe" -C "路径" commit -m "fix: 移除素材目录"
> ```

---

## 配置文件：`.gitattributes`（修复换行符警告）

子知识库根目录应存在 `.gitattributes` 文件，统一换行符处理。

### 标准 `.gitattributes` 模板

```
# 自动处理换行符
* text=auto

# 强制文本文件使用 LF 换行符（跨平台统一）
*.md text eol=lf
*.txt text eol=lf
*.py text eol=lf
*.ps1 text eol=lf
*.json text eol=lf
*.yaml text eol=lf
*.yml text eol=lf

# 二进制文件（不转换）
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.pdf binary
*.zip binary
```

> **应用**：添加 `.gitattributes` 后，需要重新规范化换行符：
> ```powershell
> & "C:\Program Files\Git\bin\git.exe" -C "路径" add --renormalize .
> & "C:\Program Files\Git\bin\git.exe" -C "路径" commit -m "fix: 规范化换行符"
> ```

---

## 已知坑与注意事项

### 1. Git 命令路径
- **问题**：PowerShell 中 `git` 可能不在 PATH
- **解决**：使用完整路径 `& "C:\Program Files\Git\bin\git.exe"`

### 2. PowerShell 中文路径编码
- **问题**：`execute_command` 调用 Python 脚本传中文参数会乱码
- **解决**：用户需在终端手动运行，或避免中文参数

### 3. PowerShell 不支持 `&&`
- **问题**：`git add -A && git commit -m "xx"` 会报错
- **解决**：用 `;` 分隔命令

### 4. 双远程必须同步
- **问题**：只推一个远程，导致 GitHub/Gitee 不一致
- **解决**：每次推送都要推两个远程

### 5. 分支名要准确
- **问题**：推错分支，或分支不存在
- **解决**：确认当前分支：`& "C:\Program Files\Git\bin\git.exe" -C "路径" branch --show-current`

### 6. 提交前先拉取
- **问题**：远程有更新，直接推送会失败
- **解决**：推送前先拉取：`& "C:\Program Files\Git\bin\git.exe" -C "路径" pull origin 分支名`

### 7. 首次推送冲突
- **问题**：远程已有内容，历史无关，pull 时冲突多
- **解决**：参考「首次推送流程」，优先用 `--allow-unrelated-histories`

### 8. 换行符警告
- **问题**：每次 `git add` 都有 CRLF 警告
- **解决**：添加 `.gitattributes` 配置，运行 `git add --renormalize .`

### 9. 素材目录被上传
- **问题**：`wiki/素材/` 被提交到远程
- **解决**：添加 `.gitignore`，运行 `git rm -r --cached wiki/素材/`

---

## 脚本路径

### setup_kb_branch_v2.py
- **主仓库路径**：`d:\Obsidian_KN\知识库构建\scripts\setup_kb_branch_v2.py`
- **备份路径**：`D:\Obsidian_KN\scripts\setup_kb_branch_v2.py`
- **版本**：v8
- **功能**：自动化创建子知识库分支和工作空间
- **注意**：`--force` 只覆盖配置文件，永不删目录

---

## 子知识库 Agent 操作指引

### 哲哲（哲学）
- 路径：`d:/Obsidian_KN/哲学思想`
- 分支：`kb/philosophy`
- 提交类型：主要是 `docs`

### 数数（数学）
- 路径：`d:/Obsidian_KN/数学`
- 分支：`kb/math`
- 提交类型：主要是 `docs`

### 算算（计算机与AI）
- 路径：`d:/Obsidian_KN/理工`
- 分支：`kb/computer-ai`
- 提交类型：`docs` + `feat`

### 金金（金融）
- 路径：`d:/Obsidian_KN/金融交易`
- 分支：`kb/finance`
- 提交类型：`docs` + `feat`（金融数据分析）

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-04-27 | v1.0 | 初版建立 |
| 2026-04-27 | v1.1 | 修复 5 个问题：Git 路径、远程地址、首次推送流程、换行符、.gitignore |

---

## 相关链接

- [[统筹/Git高级技巧速查表]]
- [[统筹/工具能力建设顶层设计]]
