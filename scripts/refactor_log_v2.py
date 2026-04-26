#!/usr/bin/env python3
"""
重构 wiki/log.md -> wiki/log/ 目录结构（修复版）
每个日期一个文件，同一个日期的多条日志合并到同一个文件
"""

import re
import shutil
from pathlib import Path

LOGFILE = "wiki/log.md"
OUTDIR = "wiki/log"


def parse_log_file(filepath=LOGFILE):
    """
    正确解析 log.md
    返回: (header, {日期: 完整内容})
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    header = ""
    entries_by_date = {}   # {日期: [条目1内容, 条目2内容, ...]}
    current_date = None
    current_entry_lines = []

    for line in content.split("\n"):
        # 检测日期标题行
        m = re.match(r"^## \[(\d{4}-\d{2}-\d{2})\]", line)
        if m:
            # 保存上一段（当前条目）
            if current_date and current_entry_lines:
                entry_text = "\n".join(current_entry_lines).strip()
                if current_date not in entries_by_date:
                    entries_by_date[current_date] = []
                entries_by_date[current_date].append(entry_text)

            # 开始新条目
            current_date = m.group(1)
            current_entry_lines = [line]
        else:
            if current_date:
                current_entry_lines.append(line)

    # 保存最后一个条目
    if current_date and current_entry_lines:
        entry_text = "\n".join(current_entry_lines).strip()
        if current_date not in entries_by_date:
            entries_by_date[current_date] = []
        entries_by_date[current_date].append(entry_text)

    return header, entries_by_date


def write_daily_log_file(date, entries_list, output_dir=OUTDIR):
    """将某一天的所有条目写入一个文件"""
    log_dir = Path(output_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    filepath = log_dir / f"{date}.md"

    # 合并当天所有条目，用 --- 分隔
    body = "\n---\n".join(entries_list)

    content = f"---\ndate: {date}\ntype: log\n---\n\n{body}\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    char_count = len(body)
    print(f"  OK: {filepath.name} ({char_count} 字符, {len(entries_list)} 个条目)")
    return date


def write_log_index(dates, output_path=Path(OUTDIR) / "index.md"):
    """写入日志总索引"""
    lines = []
    lines.append("# Wiki Log Index")
    lines.append("")
    lines.append("> 操作记录索引，按日期排列。由 WorkBuddy 自动维护。")
    lines.append("")
    lines.append("---")
    lines.append("")

    for date in sorted(dates, reverse=True):
        lines.append(f"- [[{date}]]")

    lines.append("")
    lines.append("---")
    lines.append("")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  OK: index.md")


def main():
    print("正在解析 wiki/log.md ...")
    header, entries_by_date = parse_log_file()

    print(f"  解析到 {len(entries_by_date)} 个日期")
    total_entries = sum(len(v) for v in entries_by_date.values())
    print(f"  共 {total_entries} 个日志条目")

    for date in sorted(entries_by_date.keys()):
        print(f"    {date}: {len(entries_by_date[date])} 个条目")

    print("\n正在写入按日期分组的日志文件...")
    dates = []
    for date, entries_list in sorted(entries_by_date.items()):
        write_daily_log_file(date, entries_list)
        dates.append(date)

    print("\n正在写入索引文件...")
    write_log_index(dates)

    # 备份原文件
    backup_path = Path(f"{LOGFILE}.bak")
    shutil.copy2(LOGFILE, backup_path)
    print(f"\n  OK 已备份原文件到：{backup_path}")
    print(f"\n下一步：")
    print(f"  1. 检查 wiki/log/ 目录下的文件内容是否正确")
    print(f"  2. 确认无误后，删除 wiki/log.md")
    print(f"  3. 更新 workbuddy-wiki-schema.md 中的日志相关说明")


if __name__ == "__main__":
    main()
