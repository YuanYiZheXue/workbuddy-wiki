import subprocess, os, sys

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

git = r"C:\Program Files\Git\bin\git.exe"
os.chdir(r"d:\Obsidian_KN\哲学思想")

# 1. 取消暂存workspace.json
subprocess.run([git, "reset", "HEAD", ".obsidian/workspace.json"])

# 2. 暂存所有删除
subprocess.run([git, "add", "-A"])

# 3. 提交
subprocess.run([git, "commit", "-m", "clean: 完全清除raw/跟踪文件"])

# 4. 推送
subprocess.run([git, "push", "origin", "fix/remove-pdf:kb/philosophy"])
subprocess.run([git, "push", "gitee", "fix/remove-pdf:kb/philosophy"])

print("完成")
