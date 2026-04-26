"""
为新的知识库创建 Git 分支，并配置 .gitignore
使用方法：python scripts/setup_kb_branch.py <branch_name> <workspace_dir>
示例：python scripts/setup_kb_branch.py kb/philosophy d:/Obsidian_KN/哲学知识库
"""

import subprocess
import sys
import os
from pathlib import Path

def run_git(cmd, cwd=None):
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=cwd or os.getcwd()
    )
    if result.returncode != 0:
        print(f"Git 命令失败：{' '.join(cmd)}")
        print(f"错误：{result.stderr}")
        return False
    print(f"成功：{' '.join(cmd)}")
    if result.stdout.strip():
        print(result.stdout)
    return True

def setup_kb_branch(branch_name, workspace_dir):
    # 1. 在主仓库中创建新分支
    main_repo = os.getcwd()
    print(f"1. 在主仓库创建分支：{branch_name}")
    if not run_git(["checkout", "-b", branch_name]):
        # 分支可能已存在，尝试切换
        if not run_git(["checkout", branch_name]):
            print("错误：无法创建或切换分支")
            return False
    
    # 2. 删除不需要的目录（只保留 wiki/index.md 和 wiki/统筹/）
    print("\n2. 清理分支内容（只保留索引和统筹）")
    dirs_to_remove = [
        "wiki/概念", "wiki/实体", "wiki/来源", 
        "wiki/对比", "wiki/log"
    ]
    for d in dirs_to_remove:
        if Path(d).exists():
            import shutil
            shutil.rmtree(d)
            print(f"  已删除：{d}")
    
    # 3. 提交清理后的内容
    print("\n3. 提交清理后的内容")
    if not run_git(["add", "."]):
        return False
    if not run_git(["commit", "-m", f"feat({branch_name}): 初始化知识库分支，只保留索引"]):
        print("提示：可能没有内容需要提交")
    
    # 4. 推送到远程
    print(f"\n4. 推送到远程分支：{branch_name}")
    if not run_git(["push", "-u", "origin", branch_name]):
        return False
    
    # 5. 切回 main 分支
    print("\n5. 切回 main 分支")
    run_git(["checkout", "main"])
    
    # 6. 创建新工作空间目录并克隆
    print(f"\n6. 创建新工作空间：{workspace_dir}")
    workspace_path = Path(workspace_dir)
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True)
        
        # 克隆仓库到新目录
        main_repo_path = main_repo
        run_git(["clone", main_repo_path, str(workspace_path)])
        
        # 切换到新分支
        os.chdir(workspace_path)
        run_git(["checkout", branch_name])
        
        # 创建 .gitignore
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
        
        # 提交 .gitignore
        run_git(["add", ".gitignore"])
        run_git(["commit", "-m", "chore: 添加 .gitignore，只递交索引文件"])
        run_git(["push", "origin", branch_name])
        
        print(f"\n✅ 新工作空间已创建：{workspace_dir}")
        print(f"   分支：{branch_name}")
        print(f"   请打开 WorkBuddy，选择该目录作为工作空间")
    else:
        print(f"提示：目录已存在 {workspace_dir}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python scripts/setup_kb_branch.py <branch_name> <workspace_dir>")
        print("示例：python scripts/setup_kb_branch.py kb/philosophy d:/Obsidian_KN/哲学知识库")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    workspace_dir = sys.argv[2]
    
    # 确保在主仓库目录中
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    setup_kb_branch(branch_name, workspace_dir)
