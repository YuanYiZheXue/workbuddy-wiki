"""
主 WorkBuddy：检查各知识库分支是否有更新
使用方法：python scripts/check_kb_updates.py
"""

import subprocess
import os
from pathlib import Path

def run_git(cmd, check=True):
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=os.getcwd()
    )
    if check and result.returncode != 0:
        print(f"Git 命令失败：{' '.join(cmd)}")
        print(f"错误：{result.stderr}")
        return None
    return result.stdout.strip()

def check_kb_updates():
    print("=== 检查知识库分支更新 ===\n")
    
    # 1. fetch 所有远程分支
    print("1. 获取远程更新...")
    run_git(["fetch", "--all"])
    
    # 2. 获取所有 kb/ 分支
    print("2. 检查各知识库分支...")
    all_branches = run_git(["branch", "-r"])
    kb_branches = [b.strip() for b in all_branches.split('\n') 
                    if 'kb/' in b and 'HEAD' not in b]
    
    if not kb_branches:
        print("未找到任何 kb/ 分支")
        return
    
    print(f"找到 {len(kb_branches)} 个知识库分支：\n")
    
    # 3. 检查每个分支是否有新提交
    updates = {}
    for branch in kb_branches:
        # 比较 main 和分支的差异
        log_result = run_git([
            "log", 
            "main.." + branch, 
            "--oneline", 
            "--no-merges"
        ])
        
        if log_result:
            commits = log_result.split('\n')
            updates[branch] = commits
            print(f"✅ {branch}：有 {len(commits)} 个新提交")
            for commit in commits[:3]:  # 只显示前3个
                print(f"   {commit}")
            if len(commits) > 3:
                print(f"   ... 还有 {len(commits) - 3} 个提交")
        else:
            print(f"   {branch}：无新提交")
    
    # 4. 保存结果到文件
    if updates:
        result_file = Path("wiki/统筹/分支更新状态.yaml")
        with open(result_file, "w", encoding="utf-8") as f:
            f.write("# 知识库分支更新状态\n")
            f.write("# 由 check_kb_updates.py 自动生成\n\n")
            for branch, commits in updates.items():
                f.write(f"{branch}:\n")
                for commit in commits:
                    f.write(f"  - {commit}\n")
        print(f"\n更新状态已保存到：{result_file}")
        return updates
    else:
        print("\n✅ 所有知识库分支都是最新的")
        return {}

if __name__ == "__main__":
    check_kb_updates()
