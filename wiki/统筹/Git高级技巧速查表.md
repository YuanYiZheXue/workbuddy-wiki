---
title: Git 高级技巧速查表
type: 统筹
tags:
  - Git
  - 速查表
  - 高级技巧
created: 2026-04-27
---

# Git 高级技巧速查表

> 本文档整理 Git 高级命令和技巧，用于日常开发和 Wiki 管理。

## 基础回顾

| 场景 | 命令 |
|------|------|
| 查看状态 | `git status --short` |
| 暂存所有变更 | `git add -A` |
| 提交 | `git commit -m "message"` |
| 推送到远程 | `git push origin main` |
| 获取远程更新 | `git fetch --all` |
| 查看远程差异 | `git log --oneline HEAD..origin/main` |
| 查看标签 | `git tag` |
| 回滚到标签 | `git checkout <tag>` |
| 查看最近提交 | `git log --oneline -5` |
| 查看远程仓库 | `git remote -v` |

---

## 1. Stash（暂存未完成工作）

| 场景 | 命令 | 说明 |
|------|------|------|
| 暂存当前修改 | `git stash` | 把未提交的修改保存到 stash 栈 |
| 暂存并添加消息 | `git stash push -m "消息"` | 带描述的 stash |
| 查看 stash 列表 | `git stash list` | 显示所有 stash |
| 恢复最近的 stash | `git stash pop` | 恢复并删除 stash |
| 恢复指定的 stash | `git stash pop stash@{2}` | 恢复第 3 个 stash |
| 恢复但不删除 stash | `git stash apply` | 恢复但保留 stash |
| 删除 stash | `git stash drop stash@{0}` | 删除指定的 stash |
| 清空所有 stash | `git stash clear` | 删除所有 stash |

**使用场景**：
- 需要切换分支但当前修改未完成
- 需要拉取远程更新但本地有未提交修改

---

## 2. Reflog（引用日志，用于恢复误删）

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看引用日志 | `git reflog` | 显示所有 HEAD 移动记录 |
| 查看某分支的 reflog | `git reflog <branch>` | 显示指定分支的 reflog |
| 恢复到某个 reflog 条目 | `git reset --hard HEAD@{2}` | 恢复到 2 步前的状态 |
| 从 reflog 创建分支 | `git branch recovered HEAD@{3}` | 从 reflog 条目创建新分支 |

**使用场景**：
- 误删了分支或提交
- `git reset --hard` 后想恢复
- 想查看某次操作前的状态

**示例：恢复误删的分支**
```bash
# 1. 查看 reflog，找到删除前的 commit
git reflog

# 2. 从 reflog 创建新分支
git branch recovered HEAD@{5}

# 3. 切换到恢复的分支
git checkout recovered
```

---

## 3. Rebase（变基，用于整理提交历史）

| 场景 | 命令 | 说明 |
|------|------|------|
| 交互式 rebase 最近 3 个提交 | `git rebase -i HEAD~3` | 修改、合并、重排提交 |
| Rebase 到主分支 | `git rebase main` | 把当前分支的修改"移"到 main 最新提交之后 |
| 继续 rebase（解决冲突后） | `git rebase --continue` | 继续 rebase 过程 |
| 中止 rebase | `git rebase --abort` | 取消 rebase，恢复到开始前的状态 |
| 跳过当前提交 | `git rebase --skip` | 跳过当前有冲突的提交 |

**交互式 rebase 命令**：
```
pick    = 使用提交（默认）
reword  = 使用提交，但修改提交消息
edit    = 使用提交，但停下来修改内容
squash  = 合并到前一个提交，保留消息
fixup   = 合并到前一个提交，丢弃消息
drop    = 删除提交
```

**使用场景**：
- 整理提交历史（合并零碎提交）
- 修改提交消息
- 保持线性历史（避免过多的 merge commit）

**⚠️ 警告**：不要 rebase 已经推送到远程的提交（会改写历史）。

---

## 4. Cherry-pick（精选提交，用于跨分支复用代码）

| 场景 | 命令 | 说明 |
|------|------|------|
| 应用某个提交到当前分支 | `git cherry-pick <commit-hash>` | 把指定提交"复制"到当前分支 |
| 应用多个连续提交 | `git cherry-pick <start>^..<end>` | 应用从 start 到 end 的所有提交 |
| 应用但不提交 | `git cherry-pick --no-commit <hash>` | 只应用修改，不自动提交 |
| 继续 cherry-pick（解决冲突后） | `git cherry-pick --continue` | 继续 cherry-pick 过程 |
| 中止 cherry-pick | `git cherry-pick --abort` | 取消 cherry-pick |

**使用场景**：
- 把修复 bug 的提交应用到多个分支
- 把某个功能提交复制到当前分支
- 避免合并整个分支，只取需要的提交

**示例：把 hotfix 提交应用到多个分支**
```bash
# 1. 在 main 分支上修复 bug，提交 hash 是 abc123

# 2. 切换到 release 分支
git checkout release

# 3. 只应用这个修复提交
git cherry-pick abc123

# 4. 切换到 old-version 分支
git checkout old-version

# 5. 同样应用这个修复
git cherry-pick abc123
```

---

## 5. Worktree（工作树，用于同时在多个分支工作）

| 场景 | 命令 | 说明 |
|------|------|------|
| 创建新的工作树 | `git worktree add <path> <branch>` | 在指定路径创建新工作树 |
| 创建新分支并工作树 | `git worktree add -b <new-branch> <path> main` | 基于 main 创建新分支和工作树 |
| 列出所有工作树 | `git worktree list` | 显示所有工作树 |
| 删除工作树 | `git worktree remove <path>` | 删除指定工作树 |
| 清理已删除的工作树 | `git worktree prune` | 清理已删除工作树的残留信息 |

**使用场景**：
- 需要同时在不同分支上工作（不用频繁切换分支）
- 在当前分支工作时，需要紧急修复另一个分支的 bug
- 在不同目录并行开发多个功能

**示例：并行开发多个功能**
```bash
# 1. 在主工作区开发 feature-A

# 2. 创建新工作树开发 feature-B
git worktree add ../feature-B-worktree feature-B

# 3. 在另一个终端打开 ../feature-B-worktree，开发 feature-B

# 4. 完成后删除工作树
git worktree remove ../feature-B-worktree
```

---

## 6. Reset（重置，用于撤销提交）

| 场景 | 命令 | 说明 |
|------|------|------|
| 软重置（保留修改在暂存区） | `git reset --soft HEAD~1` | 撤销提交，修改保留在暂存区 |
| 混合重置（保留修改在工作区） | `git reset --mixed HEAD~1` | 撤销提交和暂存，修改保留在工作区（默认模式） |
| 硬重置（丢弃所有修改） | `git reset --hard HEAD~1` | 撤销提交、暂存、工作区修改（⚠️ 危险） |
| 重置到远程状态 | `git reset --hard origin/main` | 强制同步到远程 main 分支 |

**⚠️ 警告**：`git reset --hard` 会丢弃所有未提交的修改，使用前确保已 stash 或提交。

---

## 7. Clean（清理未跟踪文件）

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看将要删除的文件（dry-run） | `git clean -n` | 显示将要删除的文件，但不删除 |
| 删除未跟踪文件 | `git clean -f` | 强制删除未跟踪文件 |
| 删除未跟踪目录 | `git clean -fd` | 强制删除未跟踪文件和目录 |
| 交互式清理 | `git clean -i` | 交互式选择要删除的文件 |

**使用场景**：
- 清理编译产物、临时文件
- 移除意外添加到工作区的文件

---

## 8. Bisect（二分查找，用于定位引入 bug 的提交）

| 场景 | 命令 | 说明 |
|------|------|------|
| 开始二分查找 | `git bisect start` | 启动二分查找 |
| 标记当前提交为有 bug | `git bisect bad` | 标记当前提交引入了 bug |
| 标记某个历史提交为无 bug | `git bisect good <commit>` | 标记某个提交是正常的 |
| 标记当前提交为无 bug | `git bisect good` | 标记当前提交正常 |
| 结束二分查找 | `git bisect reset` | 结束查找，恢复到开始前的状态 |
| 自动化二分查找 | `git bisect run <test-command>` | 用脚本自动运行测试 |

**使用场景**：
- 不知道哪个提交引入了 bug
- 需要快速定位问题提交

**示例：定位引入 bug 的提交**
```bash
# 1. 开始二分查找
git bisect start

# 2. 标记当前提交有 bug
git bisect bad

# 3. 标记一个已知正常的旧提交
git bisect good v1.0

# 4. Git 会自动切换到中间的提交，测试它
#    如果有 bug: git bisect bad
#    如果正常: git bisect good

# 5. 重复步骤 4，直到找到引入 bug 的提交

# 6. 结束查找
git bisect reset
```

---

## 9. Alias（别名，用于简化常用命令）

| 场景 | 命令 | 说明 |
|------|------|------|
| 创建别名 | `git config --global alias.<short> <long>` | 创建 Git 命令别名 |
| 查看所有别名 | `git config --global --get-regexp alias` | 显示所有别名 |

**推荐别名**：
```bash
# 1. 查看简洁日志
git config --global alias.lg "log --oneline --graph --decorate --all"

# 2. 查看状态（简短格式）
git config --global alias.st "status --short"

# 3. 撤销上次提交（保留修改）
git config --global alias.undo "reset --soft HEAD~1"

# 4. 放弃所有本地修改
git config --global alias.discard "reset --hard HEAD"

# 5. 查看所有分支（带最后提交信息）
git config --global alias.branches "branch -v"
```

**使用别名**：
```bash
git lg          # 代替 git log --oneline --graph --decorate --all
git st          # 代替 git status --short
git undo        # 代替 git reset --soft HEAD~1
```

---

## 10. Hooks（钩子，用于自动化流程）

| Hook | 触发时机 | 典型用途 |
|------|----------|----------|
| `pre-commit` | 提交前 | 运行 linter、测试 |
| `prepare-commit-msg` | 提交消息编辑前 | 自动生成提交消息模板 |
| `commit-msg` | 提交消息编辑后 | 验证提交消息格式 |
| `post-commit` | 提交后 | 发送通知、触发 CI |
| `pre-push` | 推送前 | 运行测试、防止推送失败 |
| `post-merge` | 合并后 | 自动安装依赖 |

**使用场景**：
- 自动运行测试（防止推送失败代码）
- 自动打标签（符合规范的提交自动打版本标签）
- 验证提交消息格式（符合 Conventional Commits）

**示例：创建 pre-commit hook 运行 linter**
```bash
# 1. 创建 pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running linter..."
npm run lint
if [ $? -ne 0 ]; then
  echo "Lint failed. Aborting commit."
  exit 1
fi
EOF

# 2. 添加执行权限
chmod +x .git/hooks/pre-commit
```

---

## 11. Submodule（子模块，用于管理依赖仓库）

| 场景 | 命令 | 说明 |
|------|------|------|
| 添加子模块 | `git submodule add <repo-url> <path>` | 添加子模块到指定路径 |
| 克隆包含子模块的仓库 | `git clone --recurse-submodules <repo-url>` | 克隆仓库并初始化子模块 |
| 初始化子模块 | `git submodule init` | 初始化子模块配置 |
| 更新子模块 | `git submodule update` | 更新子模块到记录的 commit |
| 拉取子模块最新内容 | `git submodule update --remote` | 更新子模块到远程最新 |
| 在子模块中工作 | `cd <submodule-path>` | 子模块是独立的 Git 仓库 |

**使用场景**：
- 管理第三方库依赖
- 多仓库项目（如主仓库 + 文档仓库）

---

## 12. Blame（追责，用于查看代码修改历史）

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看文件每行是谁修改的 | `git blame <file>` | 显示每行的作者、日期、commit |
| 查看文件某几行的修改历史 | `git blame -L 10,20 <file>` | 只显示第 10-20 行 |
| 忽略空白修改 | `git blame -w <file>` | 忽略空白修改（格式化） |

**使用场景**：
- 查找某行代码是谁写的
- 了解某段代码的修改历史

---

## 13. Diff（差异，用于查看修改内容）

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看未暂存的修改 | `git diff` | 显示工作区和暂存区的差异 |
| 查看已暂存的修改 | `git diff --cached` | 显示暂存区和最后一次提交的差异 |
| 查看两个提交的差异 | `git diff <commit1> <commit2>` | 显示两个提交之间的差异 |
| 查看两个分支的差异 | `git diff <branch1>..<branch2>` | 显示两个分支的差异 |
| 查看某个文件的修改历史 | `git log -p <file>` | 显示某个文件的每次修改内容 |

---

## 14. Restore（恢复，Git 2.23+ 推荐替代 checkout）

| 场景 | 命令 | 说明 |
|------|------|------|
| 恢复工作区的修改（丢弃修改） | `git restore <file>` | 丢弃工作区中某个文件的修改 |
| 恢复所有工作区的修改 | `git restore .` | 丢弃工作区所有修改 |
| 恢复暂存区的文件（取消暂存） | `git restore --staged <file>` | 把文件从暂存区移回工作区 |

**⚠️ 警告**：`git restore` 会丢弃修改，使用前确保已 stash 或提交。

---

## 15. 实用技巧

### 15.1 修改最后一次提交
```bash
# 修改提交消息
git commit --amend -m "新的提交消息"

# 追加修改到最后一次提交（不修改消息）
git add <file>
git commit --amend --no-edit
```

### 15.2 撤销已推送的提交（安全方式）
```bash
# 1. 创建反向提交（推荐，不改写历史）
git revert <commit-hash>

# 2. 推送反向提交
git push origin main
```

### 15.3 临时保存凭证（避免每次输入密码）
```bash
# 缓存凭证 1 小时
git config --global credential.helper 'cache --timeout=3600'

# 永久保存凭证（不推荐，除非是私人电脑）
git config --global credential.helper store
```

### 15.4 忽略已跟踪文件的修改
```bash
# 忽略已跟踪文件的修改（不提交）
git update-index --assume-unchanged <file>

# 恢复跟踪
git update-index --no-assume-unchanged <file>
```

### 15.5 清理远程已删除的分支
```bash
# 清理本地远程跟踪分支（远程已删除的分支）
git remote prune origin

# 查看将要清理的分支（dry-run）
git remote prune origin --dry-run
```

### 15.6 查看某次提交的详细内容
```bash
# 查看某次提交的修改内容
git show <commit-hash>

# 只查看某次提交修改的文件列表
git show --name-only <commit-hash>
```

### 15.7 比较两个分支的文件差异
```bash
# 列出两个分支中不同的文件
git diff --name-only branch1..branch2

# 列出某个文件在两个分支中的差异
git diff branch1..branch2 -- <file-path>
```

---

## 16. Wiki 管理专用技巧

### 16.1 快速回滚到某个标签
```bash
# 查看所有标签
git tag

# 切换到某个标签（只读模式）
git checkout <tag>

# 基于某个标签创建新分支（可修改）
git checkout -b <new-branch> <tag>
```

### 16.2 查看某天的提交
```bash
# 查看 2026-04-27 的所有提交
git log --oneline --after="2026-04-27 00:00" --before="2026-04-27 23:59"
```

### 16.3 查找包含某个关键词的提交
```bash
# 在提交消息中查找
git log --oneline --grep="feat:"

# 在代码修改中查找
git log -p -S "关键词"
```

### 16.4 统计贡献者提交次数
```bash
# 统计每个贡献者的提交次数
git shortlog -sn

# 查看某个贡献者的提交
git log --author="贡献者名" --oneline
```

---

## 17. 故障排查

### 17.1 修复 "fatal: not a git repository"
```bash
# 确保在正确的目录
pwd

# 初始化 Git 仓库
git init
```

### 17.2 修复 "error: failed to push some refs"
```bash
# 先拉取远程更新
git pull --rebase origin main

# 解决冲突（如果有）
# 然后推送
git push origin main
```

### 17.3 修复 "fatal: refusing to merge unrelated histories"
```bash
# 强制合并两个不相关的历史
git pull origin main --allow-unrelated-histories
```

### 17.4 取消已暂存的文件
```bash
# 取消暂存单个文件
git restore --staged <file>

# 取消暂存所有文件
git restore --staged .
```

---

## 更新记录

| 日期 | 变更内容 |
|------|----------|
| 2026-04-27 | 初始化文档，整理 17 类 Git 高级技巧 |
