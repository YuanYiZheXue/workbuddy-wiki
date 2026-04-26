# MEMORY.md - 长期记忆

## 项目背景

- **主仓库**：`d:\Obsidian_KN\知识库构建`，Git 远程 `origin`(GitHub) + `gitee`(Gitee) 双远程同步
- **Wiki Schema**：`workbuddy-wiki-schema.md`，当前版本 v0.6.0
- **子知识库架构**：主仓库 + 多子分支（kb/philosophy、kb/math、kb/computer-ai、kb/finance），各子分支独立 Obsidian vault
- **WorkBuddy 账号**：元一（数字分身），哲学底层为「元一思想四极飞轮」

## 子知识库列表

| 分支 | 工作空间 | 知识库名 | Agent | 状态 |
|------|----------|----------|-------|------|
| `kb/philosophy` | `d:/Obsidian_KN/哲学思想` | 哲学 | 哲哲 📕 | ✅ 已配置 |
| `kb/math` | `d:/Obsidian_KN/数学` | 数学 | 数数 📐 | ✅ 已配置 |
| `kb/computer-ai` | `d:/Obsidian_KN/理工` | 计算机与AI | 算算 💻 | ✅ 已配置 |
| `kb/finance` | `d:/Obsidian_KN/金融交易` | 金融 | 金金 💹 | ✅ 已配置 |

## 关键路径

- **脚本备份目录**：`D:\Obsidian_KN\scripts\`（存放 `setup_kb_branch_v2.py` 等脚本备份，只做增量不做删除）
- **主仓库脚本目录**：`d:\Obsidian_KN\知识库构建\scripts\`
- **`setup_kb_branch_v2.py`**：v8，硬编码 `REPO_DIR`，`--force` 只覆盖配置文件永不删目录

## 已知坑

- PowerShell 不支持 `&&`，用 `;` 分隔命令
- PowerShell 中文路径编码问题：`execute_command` 调用 Python 脚本传中文参数会乱码，需用户自己在终端跑
- `setup_kb_branch_v2.py` 的 `--force` 会删除整个工作空间（已修复为只覆盖配置文件）
- gitee 推送需手动检查，有时落后 GitHub 一个提交

## 用户偏好

- 指令化沟通，偏好短命令快速确认
- 「先稳定后变更」策略，系统稳定前暂缓结构调整
- 子知识库配置：不加 `--force`，纯增量零删除
- Git 操作：双远程（GitHub + Gitee）必须同步
