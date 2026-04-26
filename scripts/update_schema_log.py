#!/usr/bin/env python3
"""
更新 workbuddy-wiki-schema.md 中的日志相关说明
适配新的 wiki/log/ 目录结构
"""

import re

FILE = "workbuddy-wiki-schema.md"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 更新"操作"章节中的步骤2
old1 = "2. 读取 `wiki/log.md` 最近几条记录，了解近期操作"
new1 = "2. 读取 `wiki/log/index.md` 了解近期操作（点击日期链接查看详情）"
content = content.replace(old1, new1)

# 2. 更新"Lint"章节中对 log.md 的引用（如有）
old2 = "`wiki/log.md`"
new2 = "`wiki/log/index.md`（或对应日期文件 `wiki/log/YYYY-MM-DD.md`）"
content = content.replace(old2, new2)

# 3. 更新"索引和日志"章节，描述新的目录结构
old3 = """## 索引和日志

两个特殊文件帮助 WorkBuddy（和你）在 Wiki 增长时导航：

**index.md**——内容目录，每个页面一行，附一句话简介。按类别组织。WorkBuddy 在每次摄取时更新它。

**log.md**——按时间顺序的操作记录。每次 ingest、query、lint 都追加一条。方便回顾 Wiki 的演进历史。"""

new3 = """## 索引和日志

两类文件帮助 WorkBuddy（和你）在 Wiki 增长时导航：

**wiki/index.md**——内容目录，每个页面一行，附一句话简介。按类别组织。WorkBuddy 在每次摄取时更新它。

**wiki/log/**——按日期组织的操作日志目录：
- `wiki/log/index.md`：总索引，按日期列出所有日志条目
- `wiki/log/YYYY-MM-DD.md`：当天的所有操作记录
- 每次 ingest、query、lint 都追加到对应日期的文件中
- 方便回顾 Wiki 的演进历史，且单文件不会无限增长"""

content = content.replace(old3, new3)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("OK: 已更新 workbuddy-wiki-schema.md")
print("  - 操作章节：wiki/log.md -> wiki/log/index.md")
print("  - 索引和日志章节：描述新的 wiki/log/ 目录结构")
