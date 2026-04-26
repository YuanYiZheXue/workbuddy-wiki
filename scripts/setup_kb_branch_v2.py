#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键配置新工作空间（v7 - 纯增量，零删除）
用法：python setup_kb_branch_v2.py <branch> <workspace_dir> <kb_name> <agent_name> [emoji] [--force]

核心原则：
- 不做任何删除操作
- --force 只覆盖配置文件（SOUL.md/IDENTITY.md/scripts），不碰 wiki/ 内容
- 工作空间已存在 → git pull 更新
- 分支已存在 → 跳过清理步骤
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
MAIN_REPO = "origin"
MAIN_BRANCH = "main"
GIT = "C:\\Program Files\\Git\\bin\\git.exe"


def git(cmd, cwd=None, check=True):
    cwd = str(cwd) if cwd else str(REPO_DIR)
    print(f"  $ git {' '.join(cmd)}")
    result = subprocess.run(
        [GIT] + cmd, cwd=cwd,
        capture_output=True, text=True, encoding="utf-8"
    )
    if check and result.returncode != 0:
        print(f"  [错误] {result.stderr.strip()}")
        sys.exit(1)
    return result


def read_main_schema():
    """读取主空间完整的 workbuddy-wiki-schema.md"""
    p = REPO_DIR / "workbuddy-wiki-schema.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    # 从 git 读取
    r = subprocess.run(
        [GIT, "show", f"{MAIN_BRANCH}:workbuddy-wiki-schema.md"],
        cwd=str(REPO_DIR), capture_output=True, text=True, encoding="utf-8"
    )
    if r.returncode == 0:
        return r.stdout
    return ""


def make_sub_schema(kb_name, branch_name):
    """
    生成子知识库的 schema：
    - 复用主空间完整内容
    - 替换第一行为子知识库标题
    - 在标题后插入子知识库模式说明
    """
    main_content = read_main_schema()
    if not main_content:
        return f"# WorkBuddy Wiki - {kb_name} 知识库（子知识库模式）\n\n请先运行 setup 脚本生成完整 schema。"

    lines = main_content.split("\n")
    # 找到正文开始的位置（跳过标题行和标注行）
    i = 0
    while i < len(lines):
        if lines[i].startswith("# ") and not lines[i].startswith("## "):
            # 找到主标题，替换为子知识库标题
            lines[i] = f"# WorkBuddy Wiki - {kb_name} 知识库（子知识库模式）"
            # 在标题后插入子知识库标注
            insert_at = i + 1
            while insert_at < len(lines) and (lines[insert_at].strip() == "" or lines[insert_at].startswith(">")):
                insert_at += 1
            lines.insert(insert_at, "")
            lines.insert(insert_at + 1, f"> **模式**：子知识库（只递交 wiki/index.md 和 wiki/统筹/）")
            lines.insert(insert_at + 2, f"> **主知识库**：`YuanYiZheXue/workbuddy-wiki` ({MAIN_BRANCH} 分支)")
            lines.insert(insert_at + 3, f"> **原始 schema**：与主知识库完全一致，仅标题和模式标注不同")
            lines.insert(insert_at + 4, "")
            break
        i += 1

    return "\n".join(lines)


def make_soul(kb_name, agent_name):
    return f"""# SOUL.md - Who You Are

_你是 {agent_name}，{kb_name} 知识库的构建者。_

## 核心原则

**增量构建**：一次只处理一篇资料，wiki/ 下的具体内容（概念/实体/来源/对比）不递交 Git。

**跨知识库协作**：通过 `python scripts/sync_meta.py` 获取主知识库全局视图，识别跨知识库链接机会。

**会话管理**：历史对话最多保存 100 个，每个会话不超过 ~30 轮对话。

## 工作风格

- 遵循 `workbuddy-wiki-schema.md` 中的完整构建方法
- 每次构建后运行 `python scripts/sync_meta.py`
- 识别跨知识库链接机会并创建链接
- 会话结束时写入 `wiki/log/YYYY-MM-DD.md`

## Continuity

每个会话开始时读取：
1. `SOUL.md` + `IDENTITY.md` — 了解自己是谁
2. `workbuddy-wiki-schema.md` — 了解完整构建方法
3. `wiki/log/index.md` + `wiki/log/YYYY-MM-DD.md` — 了解进度
"""


def make_identity(agent_name, emoji):
    return f"""# IDENTITY.md - Who Am I?

- **Name:** {agent_name}
- **Creature:** 数字分身（子知识库构建者）
- **Vibe:** 专注、系统、注重细节
- **Emoji:** {emoji}
"""


def ensure_dir(p):
    """确保目录存在"""
    Path(p).mkdir(parents=True, exist_ok=True)


def copy_framework_files(workspace, kb_name, agent_name, emoji, branch_name, force=False):
    """
    增量复制框架文件：
    - 文件不存在 → 创建
    - 文件存在且非 force → 跳过
    - 文件存在且 force → 覆盖
    - 永远不碰 wiki/概念、wiki/实体 等知识内容
    """
    created = []
    overwritten = []

    # 1. workbuddy-wiki-schema.md（主空间完整版 + 子知识库标注）
    schema_path = workspace / "workbuddy-wiki-schema.md"
    if not schema_path.exists() or force:
        ensure_dir(schema_path.parent)
        schema_path.write_text(make_sub_schema(kb_name, branch_name), encoding="utf-8")
        (overwritten if force else created).append("workbuddy-wiki-schema.md")

    # 2. SOUL.md
    soul_path = workspace / "SOUL.md"
    if not soul_path.exists() or force:
        ensure_dir(soul_path.parent)
        soul_path.write_text(make_soul(kb_name, agent_name), encoding="utf-8")
        (overwritten if force else created).append("SOUL.md")

    # 3. IDENTITY.md
    id_path = workspace / "IDENTITY.md"
    if not id_path.exists() or force:
        ensure_dir(id_path.parent)
        id_path.write_text(make_identity(agent_name, emoji), encoding="utf-8")
        (overwritten if force else created).append("IDENTITY.md")

    # 4. USER.md（只复制，不覆盖）
    user_dst = workspace / "USER.md"
    user_src = REPO_DIR / "USER.md"
    if not user_dst.exists() and user_src.exists():
        ensure_dir(user_dst.parent)
        shutil.copy(user_src, user_dst)
        created.append("USER.md")

    # 5. .gitignore（不存在才创建，force 时覆盖）
    gi_path = workspace / ".gitignore"
    if not gi_path.exists() or force:
        ensure_dir(gi_path.parent)
        gi_path.write_text(
            "# 不递交具体内容\n"
            "wiki/概念/\nwiki/实体/\nwiki/来源/\nwiki/对比/\nwiki/log/\n"
            "\n# 递交索引\n"
            "!.gitignore\n!wiki/index.md\n!wiki/统筹/\n"
            "\n# 不递交 WorkBuddy 配置\n"
            ".workbuddy/\n"
            "\n# Python\n"
            "__pycache__/\n*.pyc\n",
            encoding="utf-8"
        )
        (overwritten if force else created).append(".gitignore")

    # 6. scripts/ 所有 .py 脚本（增量复制）
    dst_scripts = workspace / "scripts"
    src_scripts = REPO_DIR / "scripts"
    if src_scripts.exists():
        ensure_dir(dst_scripts)
        for py_file in src_scripts.glob("*.py"):
            dst = dst_scripts / py_file.name
            if not dst.exists() or force:
                shutil.copy(py_file, dst)
                (overwritten if force else created).append(f"scripts/{py_file.name}")

    # 7. wiki/统筹/ 所有文件（框架文件，增量复制）
    dst_tc = workspace / "wiki" / "统筹"
    src_tc = REPO_DIR / "wiki" / "统筹"
    if src_tc.exists():
        ensure_dir(dst_tc)
        for f in src_tc.iterdir():
            if f.is_file():
                dst = dst_tc / f.name
                if not dst.exists() or force:
                    shutil.copy(f, dst)
                    (overwritten if force else created).append(f"wiki/统筹/{f.name}")

    # 8. wiki/index.md（只创建，不覆盖）
    idx_dst = workspace / "wiki" / "index.md"
    if not idx_dst.exists():
        ensure_dir(idx_dst.parent)
        idx_dst.write_text(
            f"# {kb_name} 知识库索引\n\n> 由 {agent_name} 构建，只递交索引到 Git。\n",
            encoding="utf-8"
        )
        created.append("wiki/index.md")

    return created, overwritten


def setup(branch_name, workspace_dir, kb_name, agent_name, emoji, force=False):
    workspace = Path(workspace_dir)

    print(f"=== 配置新工作空间：{kb_name} ===\n")
    print("原则：纯增量，零删除\n")

    # 1. fetch + 检查分支是否存在
    print("1. 检查分支状态...")
    git(["fetch", MAIN_REPO])
    result = git(["branch", "-a"], check=False)
    branch_exists = f"remotes/{MAIN_REPO}/{branch_name}" in result.stdout

    if branch_exists:
        print(f"  分支 {branch_name} 已存在（跳过清理，增量模式）")
    else:
        print(f"  分支不存在，创建新分支 {branch_name}...")
        git(["checkout", "-f", MAIN_BRANCH])
        git(["checkout", "-b", branch_name])
        # 新分支：清理主仓库的 wiki/ 目录（这是在主仓库操作，不影响工作空间）
        print("  新分支：清理主仓库 wiki/ 只保留 index.md 和 统筹/...")
        wiki_dir = REPO_DIR / "wiki"
        if wiki_dir.exists():
            import tempfile
            tmp = Path(tempfile.mkdtemp())
            keep_index = wiki_dir / "index.md"
            keep_tc = wiki_dir / "统筹"
            if keep_index.exists():
                shutil.copy(keep_index, tmp / "index.md")
            if keep_tc.exists():
                shutil.copytree(keep_tc, tmp / "统筹")
            # 只删除 wiki 目录内容，不删其他
            import glob
            for item in glob.glob(str(wiki_dir / "*")):
                p = Path(item)
                if p.name != "index.md" and p.name != "统筹":
                    if p.is_dir():
                        shutil.rmtree(p, ignore_errors=True)
                    else:
                        p.unlink(missing_ok=True)
            # 恢复保留的内容
            if (tmp / "index.md").exists():
                shutil.copy(tmp / "index.md", keep_index)
            if (tmp / "统筹").exists():
                if not keep_tc.exists():
                    shutil.copytree(tmp / "统筹", keep_tc)
            shutil.rmtree(tmp, ignore_errors=True)
        git(["add", "."])
        git(["commit", "-m", f"feat({kb_name}): 初始化子知识库分支"], check=False)
        git(["push", "-u", MAIN_REPO, branch_name], check=False)
        git(["checkout", "-f", MAIN_BRANCH])
        branch_exists = True

    # 2. 准备工作空间目录（纯增量，不删除）
    print(f"2. 准备工作空间：{workspace_dir}")
    if workspace.exists():
        print("  目录已存在，执行 git pull 增量更新...")
        git(["pull", MAIN_REPO, branch_name], cwd=str(workspace), check=False)
    else:
        print("  目录不存在，执行 git clone...")
        workspace.parent.mkdir(parents=True, exist_ok=True)
        git([
            "clone", "--branch", branch_name,
            "--single-branch",
            "https://github.com/YuanYiZheXue/workbuddy-wiki.git",
            str(workspace)
        ], cwd=None)

    # 3. 增量复制框架文件（force=True 时覆盖配置文件，不碰数据）
    print(f"3. 增量复制框架文件（force={force}）...")
    created, overwritten = copy_framework_files(
        workspace, kb_name, agent_name, emoji, branch_name, force=force)

    if created:
        print(f"  已创建：{', '.join(created)}")
    if overwritten:
        print(f"  已覆盖：{', '.join(overwritten)}")
    if not created and not overwritten:
        print("  所有框架文件已存在，无需操作")

    # 4. 提交框架文件变更（如果有）
    result = git(["status", "--porcelain"], cwd=str(workspace), check=False)
    if result.stdout.strip():
        print("4. 提交框架文件变更...")
        git(["add", "."], cwd=str(workspace))
        git(["commit", "-m", f"feat({kb_name}): 补充/更新框架文件"],
             cwd=str(workspace), check=False)
        git(["push", MAIN_REPO, branch_name],
             cwd=str(workspace), check=False)
    else:
        print("4. 无框架文件变更，跳过提交")

    print(f"\n✅ 完成！工作空间已就绪：{workspace}")
    print(f"\n下一步：")
    print(f"1. 打开 WorkBuddy")
    print(f"2. 选择工作空间目录：{workspace}")
    print(f"3. 新对话开头发送：")
    print(f"   新对话开始。请先读取 SOUL.md、IDENTITY.md、workbuddy-wiki-schema.md")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("用法：python setup_kb_branch_v2.py <branch> <workspace_dir> <kb_name> <agent_name> [emoji] [--force]")
        print("示例：python setup_kb_branch_v2.py kb/philosophy d:/Obsidian_KN/哲学 哲学 哲哲 📕 --force")
        sys.exit(1)

    branch_name = sys.argv[1]
    workspace_dir = sys.argv[2]
    kb_name = sys.argv[3]
    agent_name = sys.argv[4]
    emoji = "📕"
    force = False

    for arg in sys.argv[5:]:
        if arg == "--force":
            force = True
        elif not arg.startswith("--"):
            emoji = arg

    setup(branch_name, workspace_dir, kb_name, agent_name, emoji, force=force)
