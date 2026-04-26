"""
新工作空间：获取主 WorkBuddy 推送的元数据（全局视图等）
使用方法：python scripts/sync_meta.py
"""

import subprocess
import os
from pathlib import Path

def run_git(cmd, check=True, capture=True):
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=capture,
        text=True,
        encoding='utf-8',
        cwd=os.getcwd()
    )
    if check and result.returncode != 0:
        print(f"Git 命令失败：{' '.join(cmd)}")
        if result.stderr:
            print(f"错误：{result.stderr}")
        return None
    return result.stdout.strip() if capture else True

def sync_meta():
    print("=== 获取元数据 ===\n")
    
    # 1. 确保在正确的分支
    print("1. 检查当前分支...")
    current = run_git(["branch", "--show-current"])
    print(f"   当前分支：{current}")
    
    # 2. 获取 main 分支的更新
    print("\n2. 获取 main 分支的元数据...")
    if run_git(["fetch", "origin", "main"]) is None:
        return False
    
    # 3. 检出 main 分支的 wiki/统筹/ 目录
    print("\n3. 检出 wiki/统筹/ 目录...")
    if run_git(["checkout", "origin/main", "--", "wiki/统筹/"]) is None:
        print("提示：可能没有 wiki/统筹/ 目录")
    else:
        print("✅ 获取 wiki/统筹/ 成功")
    
    # 4. 检查是否有更新
    print("\n4. 检查更新内容...")
    status = run_git(["status", "--porcelain", "wiki/统筹/"])
    if not status:
        print("✅ 元数据已是最新")
        return True
    
    print(f"发现更新：\n{status}")
    
    # 5. 提交更新（可选）
    print("\n5. 提交元数据更新...")
    if run_git(["add", "wiki/统筹/"]) is None:
        return False
    
    timestamp = subprocess.run(
        ["git", "log", "-1", "--format=%ci"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    ).stdout.strip()
    
    commit_msg = f"chore(meta): 同步主仓库元数据"
    if run_git(["commit", "-m", commit_msg]) is None:
        print("提示：可能没有内容需要提交")
        return True
    
    # 6. 推送到当前分支
    print("\n6. 推送到远程...")
    if run_git(["push", "origin", current]) is None:
        return False
    
    print("\n✅ 元数据同步成功")
    return True

if __name__ == "__main__":
    sync_meta()
