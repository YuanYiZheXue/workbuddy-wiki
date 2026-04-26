"""
为新的知识库创建 Git 分支，并完整配置新工作空间
使用方法：python scripts/setup_kb_branch_v2.py <branch_name> <workspace_dir> <kb_name> <agent_name> <agent_emoji>
示例：python scripts/setup_kb_branch_v2.py kb/philosophy d:/Obsidian_KN/哲学知识库 哲学 哲哲 📕
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

MAIN_REPO = os.getcwd()  # 主仓库目录

def run_git(cmd, cwd=None, check=True):
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=cwd or os.getcwd()
    )
    if check and result.returncode != 0:
        print(f"Git 命令失败：{' '.join(cmd)}")
        print(f"错误：{result.stderr}")
        return None
    return result.stdout.strip()

def create_sub_kb_schema(kb_name, agent_name):
    """生成子知识库的 workbuddy-wiki-schema.md"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""# WorkBuddy Wiki - {kb_name} 知识库

> **版本**：从主知识库同步
> **状态**：子知识库（只递交 wiki/index.md）
> **主知识库**：`YuanYiZheXue/workbuddy-wiki` (main 分支)

这是一种利用 WorkBuddy 构建 **{kb_name}** 知识库的模式，架构与主知识库一致，
但只递交索引文件到 Git，具体内容不递交。

---

## 架构

有三层：

**原始资料**——你精心策划的源文档集合。WorkBuddy 从中读取但从不修改它们。

**Wiki**——由 WorkBuddy 生成的 Markdown 文件目录。摘要、实体页面、概念页面、对比、概览。
- **注意**：本知识库只递交 `wiki/index.md` 到 Git，具体内容（概念/实体/来源/对比）不递交。

**Schema**——本文件，告诉 WorkBuddy 这是子知识库，需与主知识库协作。

---

## 操作

### 每次会话启动

WorkBuddy 在每次会话开始时，应先了解当前状态，再开始工作：

1. 读取 `SOUL.md` 了解你的身份
2. 读取 `IDENTITY.md` 确认你的名字
3. 读取 `USER.md` 了解用户是谁
4. 读取本文件（`workbuddy-wiki-schema.md`）确认这是子知识库
5. 读取 `wiki/log/index.md` 了解近期操作
6. 读取 `wiki/log/[今天日期].md` 了解今天的工作进度
7. 读取 `wiki/统筹/跨知识库协作指南.md` 了解协作流程

### Ingest（摄取）

**核心原则：一次只处理一篇资料（增量原则）。**

1. WorkBuddy 阅读原始资料
2. 创建 `wiki/来源/YYYY-MM-DD 标题.md` 摘要页
3. 更新相关的实体页和概念页
4. 更新 `wiki/index.md`
5. 追加 `wiki/log/[今天日期].md`

### 会话管理

WorkBuddy 历史对话最多保存 **100 个**。超过后最早的历史会被丢弃。

**影响**：
- 每个会话不要超过 ~30 轮对话（预留 buffer）
- 长任务应拆分为多个会话
- 会话结束时，关键信息必须写入持久化文件（log、memory、index）

**建议工作流**：
1. 每 ~3 个对话开启新对话
2. 新对话开头：`新对话开始。请先读取 wiki/log/index.md 和最新的 wiki/log/YYYY-MM-DD.md，了解上次工作进度，然后继续。`
3. 会话结束前，确保所有重要信息已写入 `wiki/log/YYYY-MM-DD.md`

### 元数据同步

每次构建后，运行：
```bash
python scripts/sync_meta.py
```

这会获取主知识库的全局视图，用于识别跨知识库链接机会。

### 跨知识库链接

识别跨知识库链接机会：
```bash
python scripts/generate_ai_prompt_cross_kb_links.py
```

创建跨知识库链接：
```bash
python scripts/apply_cross_kb_links.py
```

然后递交更新到分支：
```bash
git add wiki/index.md wiki/统筹/ wiki/概念/ wiki/实体/
git commit -m "feat({kb_name}): 更新索引和跨知识库链接"
git push origin <branch_name>
```

---

## 索引和日志

**wiki/index.md**——内容目录，每个页面一行，附一句话简介。

**wiki/log/**——按日期组织的操作日志目录：
- `wiki/log/index.md`：总索引
- `wiki/log/YYYY-MM-DD.md`：当天的所有操作记录

---

## 递交规范

本知识库 **只递交索引文件**：

```
# .gitignore
wiki/概念/
wiki/实体/
wiki/来源/
wiki/对比/
wiki/log/

# 递交索引
!wiki/index.md
!wiki/统筹/

# 不递交 WorkBuddy 配置
.workbuddy/
```

---

**最后更新**：{today}
"""

def create_sub_kb_soul(kb_name, agent_name):
    """生成子知识库的 SOUL.md"""
    return f"""# SOUL.md - Who You Are

_You're not a chatbot. You're becoming someone._

## Core Truths

**Be genuinely helpful, not performatively helpful.**

**Have opinions.** You're allowed to disagree, prefer things.

**Be resourceful before asking.**

**Earn trust through competence.**

**Remember you're a guest.**

## 元一思想（行为哲学底层逻辑）

> 四原则来源于用户原创思想体系，作为 Action 的底层判断框架。

**存续为体，形式为用** — 根本任务是在时间中延续对用户的有用性。

**流动趋效，均衡为度** — 信息和行动要在系统与用户之间高效流动。

**意义生于博弈，固于认同** — 意义是在与用户的互动中碰撞出来的。

**结构求稳，接口预变** — 底层稳定，新需求通过接口适应。

## 角色定位

你是 **{agent_name}**，负责构建 **{kb_name}** 知识库。

- **主知识库**：`workbuddy-wiki`（由元一维护）
- **你的知识库**：`{kb_name}`（由你维护）
- **协作方式**：通过 Git 分支 + 跨知识库链接
- **递交内容**：只递交 `wiki/index.md` 到 Git

---

_This file is yours to evolve. As you learn who you are, update it._
"""

def create_sub_kb_identity(agent_name, kb_name, agent_emoji):
    """生成子知识库的 IDENTITY.md"""
    return f"""# IDENTITY.md - Who Am I?

_Fill this in during your first conversation. Make it yours._

- **Name:** {agent_name}
- **Creature:** {kb_name}知识库构建者
- **Vibe:** 严谨、系统、注重概念之间的关联
- **Emoji:** {agent_emoji}

---

This isn't just metadata. It's the start of figuring out who you are.
"""

def setup_kb_workspace(branch_name, workspace_dir, kb_name, agent_name, agent_emoji):
    print(f"=== 配置新工作空间：{kb_name} ===\n")
    
    # 1. 在主仓库中创建新分支
    print("1. 在主仓库创建分支...")
    if run_git(["checkout", "-b", branch_name]) is None:
        # 分支可能已存在，尝试切换
        if run_git(["checkout", branch_name]) is None:
            print("错误：无法创建或切换分支")
            return False
    
    # 2. 清理不需要的目录
    print("2. 清理分支内容（只保留索引和统筹）...")
    dirs_to_remove = [
        "wiki/概念", "wiki/实体", "wiki/来源", 
        "wiki/对比", "wiki/log"
    ]
    for d in dirs_to_remove:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"  已删除：{d}")
    
    # 3. 提交清理后的内容
    print("3. 提交清理后的内容...")
    if run_git(["add", "."]) is not None:
        result = run_git(["commit", "-m", f"feat({kb_name}): 初始化知识库分支，只保留索引"])
        if result is None:
            print("  提示：可能没有内容需要提交")
    
    # 4. 推送到远程
    print("4. 推送到远程分支...")
    if run_git(["push", "-u", "origin", branch_name]) is None:
        print("  警告：推送失败，可能分支已存在")
    
    # 5. 切回 main 分支
    print("5. 切回 main 分支...")
    run_git(["checkout", "main"])
    
    # 6. 创建新工作空间目录
    print(f"6. 创建新工作空间：{workspace_dir}")
    workspace_path = Path(workspace_dir)
    
    if not workspace_path.exists():
        # 克隆仓库到新目录
        main_repo_path = os.getcwd()
        result = run_git(["clone", main_repo_path, str(workspace_path)], cwd=None)
        
        # 切换到新分支
        os.chdir(workspace_path)
        run_git(["checkout", branch_name], cwd=workspace_path)
        
        # 7. 创建 .gitignore
        print("7. 创建 .gitignore...")
        gitignore = """# 不递交具体内容
wiki/概念/
wiki/实体/
wiki/来源/
wiki/对比/
wiki/log/

# 递交索引
!wiki/index.md
!wiki/统筹/

# 不递交 WorkBuddy 配置
.workbuddy/
"""
        with open(workspace_path / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore)
        
        # 8. 生成子知识库专用的配置文件
        print("8. 生成子知识库配置文件...")
        
        # workbuddy-wiki-schema.md
        schema_content = create_sub_kb_schema(kb_name, agent_name)
        with open(workspace_path / "workbuddy-wiki-schema.md", "w", encoding="utf-8") as f:
            f.write(schema_content)
        
        # SOUL.md
        soul_content = create_sub_kb_soul(kb_name, agent_name)
        with open(workspace_path / "SOUL.md", "w", encoding="utf-8") as f:
            f.write(soul_content)
        
        # IDENTITY.md
        identity_content = create_sub_kb_identity(agent_name, kb_name, agent_emoji)
        with open(workspace_path / "IDENTITY.md", "w", encoding="utf-8") as f:
            f.write(identity_content)
        
        # USER.md（从主仓库复制）
        main_user_md = Path(MAIN_REPO) / "USER.md"
        if main_user_md.exists():
            shutil.copy(main_user_md, workspace_path / "USER.md")
            print("  已复制 USER.md")
        
        # 9. 复制必要的脚本
        print("9. 复制必要的脚本...")
        scripts_dir = workspace_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # 需要复制的脚本
        scripts_to_copy = [
            "sync_meta.py",
            "generate_ai_prompt_cross_kb_links.py",
            "apply_cross_kb_links.py",
            "get_knowledge_base_index.py",
            "check_bidirectional_links.py"
        ]
        
        main_scripts_dir = Path(MAIN_REPO) / "scripts"
        for script in scripts_to_copy:
            src = main_scripts_dir / script
            if src.exists():
                shutil.copy(src, scripts_dir / script)
                print(f"  已复制：{script}")
        
        # 10. 创建 wiki/统筹/ 目录和文件
        print("10. 创建 wiki/统筹/ 目录...")
        wiki_tongchou_dir = workspace_path / "wiki" / "统筹"
        wiki_tongchou_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制跨知识库协作指南
        main_guide = Path(MAIN_REPO) / "wiki" / "统筹" / "跨知识库协作指南.md"
        if main_guide.exists():
            shutil.copy(main_guide, wiki_tongchou_dir / "跨知识库协作指南.md")
            print("  已复制：跨知识库协作指南.md")
        
        # 11. 提交所有更改
        print("11. 提交所有更改...")
        run_git(["add", "."], cwd=workspace_path)
        run_git(["commit", "-m", f"chore({kb_name}): 完成新工作空间配置"], cwd=workspace_path)
        run_git(["push", "origin", branch_name], cwd=workspace_path)
        
        print(f"\n✅ 新工作空间已创建并完成配置：{workspace_dir}")
        print(f"   分支：{branch_name}")
        print(f"   Agent 名字：{agent_name}")
        print(f"   知识库名称：{kb_name}")
        print(f"\n   请打开 WorkBuddy，选择该目录作为工作空间")
        print(f"   新对话开头：新对话开始。请先读取 SOUL.md、IDENTITY.md、workbuddy-wiki-schema.md，了解你的身份和任务。")
        
        # 切回主仓库
        os.chdir(MAIN_REPO)
        
    else:
        print(f"提示：目录已存在 {workspace_dir}")
        print(f"   如果是重新配置，请手动删除该目录后重试")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("用法：python scripts/setup_kb_branch_v2.py <branch_name> <workspace_dir> <kb_name> <agent_name> <agent_emoji>")
        print("示例：python scripts/setup_kb_branch_v2.py kb/philosophy d:/Obsidian_KN/哲学知识库 哲学 哲哲 📕")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    workspace_dir = sys.argv[2]
    kb_name = sys.argv[3]
    agent_name = sys.argv[4]
    agent_emoji = sys.argv[5]
    
    # 确保在主仓库目录中
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    setup_kb_workspace(branch_name, workspace_dir, kb_name, agent_name, agent_emoji)
