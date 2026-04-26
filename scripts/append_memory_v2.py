import os

p = r"d:\Obsidian_KN\知识库构建\.workbuddy\memory\2026-04-26.md"
content = open(p, encoding="utf-8").read()

extra = """

---

## [2026-04-26] enhance | setup_kb_branch_v2.py v2~v7 迭代（纯增量零删除）

### 背景
用户要创建子知识库工作空间，脚本 `setup_kb_branch_v2.py` 经过 6 次迭代（v2~v7），
最终稳定在 v7：**纯增量，零删除**。

### 踩坑记录（v2~v6 的问题）

| 版本 | 问题 | 修复 |
|------|------|--------|
| v2 | 克隆到临时目录再 move → Windows 跨磁盘失败 | 直接 clone 到目标路径 |
| v2 | .git 目录文件被锁定 → shutil.rmtree 失败 | 用 robocopy /MIR 清空后再删 |
| v3 | 分支已存在时 git checkout 被未跟踪文件阻挡 | git checkout -f 强制切换 |
| v4 | 清理 wiki/ 时删除了子知识库索引目录 | 只保留 index.md + 统筹/，用临时目录备份恢复 |
| v5 | --force 会删除用户已有的 wiki/ 内容 | 只在【分支新创建】时清理，已存在分支跳过 |
| v5 | 工作空间已存在时直接报错退出 | 已存在 → git pull 增量更新，不重新 clone |
| v6 | 子知识库的 schema 是简化版，子 Agent 不知道怎么建 Wiki | 复制主空间【完整版】schema，只改标题 + 加标注 |
| v6 | scripts/ 只复制了 5 个脚本，不够全 | 复制 scripts/ 下【所有】.py 文件 |

### v7（当前稳定版）核心原则

1. **纯增量，零删除** — 不做任何删除操作
2. **`--force` 只覆盖配置文件**，不碰 wiki/ 知识内容
3. **工作空间已存在** → `git pull` 增量更新
4. **分支已存在** → 跳过清理步骤
5. **子知识库 schema = 主空间完整版 + 子知识库标注**
6. **框架文件全量复制**（scripts/ 所有 .py、wiki/统筹/ 所有文件）
7. **知识内容永远不碰**（wiki/概念、wiki/实体、wiki/来源、wiki/对比）

### 踩坑经验已写入脚本注释

`setup_kb_branch_v2.py` 顶部注释包含完整的 v2~v7 踩坑记录。

### 文件清单

- **修改**：`scripts/setup_kb_branch_v2.py`（v7，附完整踩坑经验注释）
- **修改**：`workbuddy-wiki-schema.md`（主空间，已从 git 历史恢复完整版）

---

## [2026-04-26] git | 检查并清理多余分支

### 检查结果

**远程分支**：
- `origin/main` ✅ 保留
- `origin/kb/philosophy` ✅ 保留（子知识库分支）
- `gitee/main` ✅ 保留（Gitee 远程）

**本地分支**：
- `main` ✅ 保留
- `kb/philosophy` ✅ 保留

**结论**：无多余分支，无需清理。

---

**最后更新**：2026-04-26 16:50
"""

# 去掉旧的最后更新行，加新的
import re
content = re.sub(r"\*\*最后更新\*\*：.*", "", content).strip()
content = content + extra

open(p, "w", encoding="utf-8").write(content)
print("OK: 已追加今日经验到 memory/2026-04-26.md")
