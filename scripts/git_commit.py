#!/usr/bin/env python3
"""
使用 Python subprocess 运行 git 命令（绕过 PowerShell 环境问题）
"""

import subprocess
import sys

def git_commit(message):
    """提交当前修改"""
    commands = [
        ["git", "add", "wiki/"],
        ["git", "commit", "-m", message],
    ]

    for cmd in commands:
        print(f"运行：{' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=r"d:\Obsidian_KN\知识库构建", capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            print(f"错误：{result.stderr}")
            return False
        print(result.stdout)

    print("\n提交成功！")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python git_commit.py <commit message>")
    else:
        git_commit(" ".join(sys.argv[1:]))
