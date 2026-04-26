"""
主 WorkBuddy：推送元数据（全局视图、分支更新状态等）到 main 分支
使用方法：python scripts/push_meta.py
"""

import subprocess
import os
from pathlib import Path
from datetime import datetime

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

def push_meta():
    print("=== 推送元数据到 main 分支 ===\n")
    
    # 1. 确保在 main 分支
    print("1. 确保在 main 分支...")
    current = run_git(["branch", "--show-current"])
    if current != "main":
        print(f"当前在 {current} 分支，切换到 main...")
        if run_git(["checkout", "main"]) is None:
            return False
    
    # 2. 生成全局视图
    print("\n2. 生成全局视图...")
    result = subprocess.run(
        ["python", "scripts/get_knowledge_base_index.py"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=os.getcwd()
    )
    if result.returncode != 0:
        print(f"生成全局视图失败：{result.stderr}")
        return False
    print("✅ 生成全局视图成功")
    
    # 3. 检查是否有变更
    print("\n3. 检查变更...")
    status = run_git(["status", "--porcelain", "wiki/统筹/"])
    if not status:
        print("✅ 元数据无变更，无需推送")
        return True
    
    print(f"发现变更：\n{status}")
    
    # 4. 提交变更
    print("\n4. 提交变更...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if run_git(["add", "wiki/统筹/"]) is None:
        return False
    
    commit_msg = f"chore(meta): 更新元数据 {timestamp}"
    if run_git(["commit", "-m", commit_msg]) is None:
        # 可能没有变更
        print("提示：可能没有实际变更")
        return True
    
    # 5. 推送到远程
    print("\n5. 推送到远程...")
    if run_git(["push", "origin", "main"]) is None:
        return False
    
    print("\n✅ 元数据推送成功")
    return True

if __name__ == "__main__":
    push_meta()
