"""
主 WorkBuddy：合并知识库分支的更新（主要是跨知识库链接）
使用方法：python scripts/merge_cross_kb_links.py [branch_name]
示例：python scripts/merge_cross_kb_links.py kb/philosophy
"""

import subprocess
import sys
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
        print(f"错误：{result.stderr}")
        return None
    return result.stdout.strip() if capture else True

def merge_branch(branch_name):
    print(f"=== 合并分支：{branch_name} ===\n")
    
    # 1. fetch 最新代码
    print("1. 获取远程更新...")
    if run_git(["fetch", "origin", branch_name]) is None:
        return False
    
    # 2. 检查是否有更新
    print("2. 检查更新...")
    log_result = run_git([
        "log", 
        f"HEAD..origin/{branch_name}",
        "--oneline",
        "--no-merges"
    ])
    
    if not log_result:
        print("✅ 已经是最新，无需合并")
        return True
    
    commits = log_result.split('\n')
    print(f"发现 {len(commits)} 个新提交：")
    for commit in commits[:5]:
        print(f"   {commit}")
    if len(commits) > 5:
        print(f"   ... 还有 {len(commits) - 5} 个提交")
    
    # 3. 合并更新
    print(f"\n3. 合并 origin/{branch_name}...")
    if run_git(["merge", f"origin/{branch_name}", "--no-edit"]) is None:
        print("合并冲突！请手动解决")
        return False
    
    print("✅ 合并成功")
    
    # 4. 推送到远程
    print("\n4. 推送到远程...")
    if run_git(["push", "origin", "main"]) is None:
        return False
    
    print("✅ 推送成功")
    return True

def merge_all_kb_branches():
    print("=== 合并所有知识库分支 ===\n")
    
    # 1. fetch 所有分支
    print("1. 获取远程更新...")
    run_git(["fetch", "--all"])
    
    # 2. 获取所有 kb/ 分支
    all_branches = run_git(["branch", "-r"])
    if not all_branches:
        return False
    
    kb_branches = [b.strip() for b in all_branches.split('\n') 
                    if 'kb/' in b and 'HEAD' not in b]
    
    if not kb_branches:
        print("未找到任何 kb/ 分支")
        return False
    
    print(f"找到 {len(kb_branches)} 个知识库分支：\n")
    
    # 3. 逐个合并
    success_count = 0
    for branch in kb_branches:
        print(f"\n{'='*50}")
        if merge_branch(branch):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ 合并完成：{success_count}/{len(kb_branches)} 个分支")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 合并指定分支
        branch_name = sys.argv[1]
        merge_branch(branch_name)
    else:
        # 合并所有 kb/ 分支
        merge_all_kb_branches()
