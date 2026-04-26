# 子知识库 Git 操作指南（修订版）

> ⚠️ **核心原则：只提交，不覆盖。只提交 wiki/ 和 scripts/，不提交 raw/。**

---

## 一、禁止操作（红线）

以下操作**绝对禁止**执行：

| 操作 | 原因 |
|------|------|
| `git init` | 仓库已存在，重新初始化会丢失历史 |
| `git checkout` / `git switch` | 会覆盖本地未提交的修改 |
| `git reset --hard` | 会丢失本地修改 |
| `git clean -fd` | 会删除未跟踪文件 |
| `Remove-Item ... -Recurse -Force` | 直接删除文件，不可恢复 |
| `git add raw/` 或 `git add -A` | **raw/ 目录禁止提交** |

---

## 二、唯一允许的提交流程

### 前提确认

1. 工作目录 `d:/Obsidian_KN/金融交易` 已经是正确的 git 仓库
2. 当前分支是 `kb/finance`
3. 只提交 `wiki/` 和 `scripts/` 两个目录

### 标准流程

```powershell
# 1. 检查状态（只检查，不修改）
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" status --short

# 2. 只添加允许的文件
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" add wiki/ scripts/

# 3. 检查暂存区（确认没有 raw/）
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" status --short

# 4. 提交
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" commit -m "feat(金融): <描述>"

# 5. 推送到双远程
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" push gitee kb/finance
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" push origin kb/finance
```

---

## 三、本次错误操作复盘（2026-04-26）

### 错误 1：`git init` 覆盖了原有仓库

**操作**：
```powershell
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" init
```

**后果**：原有 git 历史丢失，`master` 分支指向丢失。

**正确做法**：仓库已存在，不需要 `init`。如果不确定，先用 `git status` 检查。

---

### 错误 2：`git checkout -b kb/finance gitee/kb/finance` 覆盖了本地文件

**操作**：
```powershell
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" checkout -b kb/finance gitee/kb/finance
```

**后果**：远程分支的内容覆盖了本地未提交的修改。

**正确做法**：
- 不要切换分支
- 如果必须切换，先 `git stash` 保存本地修改
- 更安全的做法：永远不切换分支，只在当前分支提交

---

### 错误 3：`Remove-Item '.temp-backup' -Recurse -Force` 删除了备份

**操作**：
```powershell
Remove-Item 'd:/Obsidian_KN/金融交易/.temp-backup' -Recurse -Force
```

**后果**：临时备份目录被永久删除。

**正确做法**：不要删除任何本地文件。如果需要清理，告诉用户手动处理。

---

### 错误 4：把 `raw/` 加入了 git 暂存区

**操作**：
```powershell
& "C:\Program Files\Git\bin\git.exe" -C "d:/Obsidian_KN/金融交易" add -A
```

**后果**：`raw/` 目录（包含大文件）被加入暂存区。

**正确做法**：
- 永远不要用 `git add -A`
- 只用 `git add wiki/ scripts/`
- 如果误加了，用 `git reset raw/` 移除

---

## 四、`.gitignore` 配置

确保 `.gitignore` 包含以下规则（禁止提交 raw/）：

```
# 不提交原始资料
raw/

# 不提交临时文件
.temp-backup/
__pycache__/
*.pyc
```

---

## 五、安全检查清单

每次提交前，必须确认：

- [ ] 没有执行 `git init`（仓库已存在）
- [ ] 没有执行 `git checkout` / `git switch`（不切换分支）
- [ ] 没有执行 `git reset --hard`（不强制重置）
- [ ] 暂存区只有 `wiki/` 和 `scripts/`（用 `git status` 确认）
- [ ] 没有 `raw/` 目录下的文件
- [ ] 没有执行任何 `Remove-Item ... -Force`（不删除本地文件）

---

## 六、分支策略

- **主仓库**（哲学/数学/计算机/金融）：`main` 分支
- **金融子知识库**：`kb/finance` 分支
- **工作目录**：`d:/Obsidian_KN/金融交易`
- **永远在这个目录下工作，永远不切换分支**

---

*最后更新：2026-04-26（金金修订）*
