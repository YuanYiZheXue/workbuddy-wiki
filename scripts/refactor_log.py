#!/usr/bin/env python3
"""
重构 wiki/log.md -> wiki/log/ 目录结构
每个日期一个文件，wiki/log/index.md 作为总索引
"""

import re
import shutil
from pathlib import Path

LOGFILE = "wiki/log.md"
OUTDIR = "wiki/log"


def parse_log_file(filepath=LOGFILE):
    """按日期解析 log.md，返回 {日期: 内容} 字典"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    entries = {}
    current_date = None
    current_lines = []

    for line in content.split("\n"):
        # 检测日期标题行：## [2026-04-25] ...
        m = re.match(r'^## \[(\d{4}-\d{2}-\d{2})\]', line)
        if m:
            # 保存上一段
            if current_date and current_lines:
                entries[current_date] = "\n".join(current_lines).strip()
            current_date = m.group(1)
            current_lines = [line]
        else:
            if current_date:
                current_lines.append(line)

    # 保存最后一段
    if current_date and current_lines:
        entries[current_date] = "\n".join(current_lines).strip()

    return entries


def write_all_log_files(entries, output_dir=OUTDIR):
    """将每个日期的日志写入单独文件，并返回日期列表"""
    log_dir = Path(output_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    dates = []
    for date, body in sorted(entries.items()):
        filepath = log_dir / f"{date}.md"
        content = f"---\ndate: {date}\ntype: log\n---\n\n{body}\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK: {filepath}")
        dates.append(date)

    return dates


def write_log_index(dates, output_path=Path(OUTDIR) / "index.md"):
    """写入日志总索引"""
    lines = []
    lines.append("# Wiki Log Index")
    lines.append("")
    lines.append("> 操作记录索引，按日期排列。由 WorkBuddy 自动维护。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 最新的日期排在最前面
    for date in sorted(dates, reverse=True):
        lines.append(f"- [[{date}]]")

    lines.append("")
    lines.append("---")
    lines.append("")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  OK: {output_path}")


def main():
    print("正在解析 wiki/log.md ...")
    entries = parse_log_file()
    print(f"  解析到 {len(entries)} 个日期的日志")

    for d in sorted(entries.keys()):
        print(f"    {d}: {len(entries[d])} 字符")

    print("\n正在写入按日期分组的日志文件...")
    dates = write_all_log_files(entries)

    print("\n正在写入索引文件...")
    write_log_index(dates)

    # 备份原文件
    backup_path = Path(f"{LOGFILE}.bak")
    shutil.copy2(LOGFILE, backup_path)
    print(f"\n  OK 已备份原文件到：{backup_path}")
    print(f"\n下一步：")
    print(f"  1. 检查 wiki/log/ 目录下的文件内容是否正确")
    print(f"  2. 确认无误后，删除 wiki/log.md")
    print(f"  3. 更新引用了 wiki/log.md 的其他文件中的链接")


if __name__ == "__main__":
    main()
