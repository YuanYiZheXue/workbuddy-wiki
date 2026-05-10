"""
Auto Knowledge Sync — 知识库自动入库模块
==========================================
当 AI 回答新知识时（检索相似度 < 阈值），自动完成：
  1. 内容提炼与格式化
  2. Wiki 页面自动创建/更新
  3. 入库日志记录（待审核队列）
  4. 可选：触发索引重建

核心原则：
  - 新知识入库后需要「下次会话审核确认」
  - 避免低质量内容污染知识库
  - 保持 wiki 格式规范（workbuddy-wiki-schema）

用法：
  from auto_knowledge_sync import AutoKnowledgeSync
  sync = AutoKnowledgeSync()
  result = sync.commit(
      topic="MCP协议",
      answer="MCP是...",
      keywords=["JSON-RPC", "stdio", "工具注册"]
  )
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from string import Template  # C-02 Fix: 替代 .format() 防注入

# ═══════════════════════════════════════════════════════════
# 常量配置（C-01 Fix: 从 config.py 引入，不再硬编码）
# ═══════════════════════════════════════════════════════════
try:
    from kb_config import WIKI_DIR as _WIKI_DIR_FROM_CONFIG
    WIKI_ROOT = _WIKI_DIR_FROM_CONFIG
except ImportError:
    # fallback: 保持向后兼容
    WIKI_ROOT = Path(r"d:\Obsidian_KN\philosophy\wiki")


# ═══════════════════════════════════════════════════════════
# 常量配置
# ═══════════════════════════════════════════════════════════

# C-01 Fix: WIKI_ROOT 已在文件顶部从 config.py 引入（fallback 到硬编码）

# Wiki Schema 前置模板（C-02 Fix: string.Template 替代 str.format）
# Template 只替换 $var，不解释 {} 嵌套结构 → 天然免疫 format string 注入
WIKI_TEMPLATE = Template("""---
title: "$title"
summary: "$summary"
created: $created
tags: [$tags]
---

# ${title}

${content}

---

## 相关页面

${related_links}

## 来源

- 首次入库：自动同步（$created）
- 原始问答关键词：$keywords_str
""")

# Q&A 专属模板（用户提问自动入库，与概念类模板隔离）
QA_TEMPLATE = Template("""---
title: "$title"
type: qa
date: $date
tags: [$tags]
source: $source
---

## 问题

$question

## 回答

$answer

---

## 来源
- 入库时间：$date
- 来源类型：$source
- 关键词：$keywords_str
""")

# 派生路径常量
CONCEPT_DIR = WIKI_ROOT / "概念"
QA_DIR = WIKI_ROOT / "问答"  # Q&A 专属命名空间（与概念/隔离）
IMPORT_LOG = WIKI_ROOT / "log" / "auto_import_log.md"
AUTO_IMPORT_JSON = WIKI_ROOT / "log" / "auto_import_pending.json"

# C-03 Fix: Windows 保留设备名黑名单
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

# ═══════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════

@dataclass
class ImportEntry:
    """入库条目（待审核）"""
    id: str              # 唯一 ID（时间戳）
    topic: str           # 主题
    summary: str         # 摘要
    keywords: list[str]  # 关键词
    content: str         # 正文内容
    created: str          # 创建时间
    status: str           # pending / confirmed / rejected
    wiki_path: str        # wiki 文件路径
    notes: str           # 备注（审核意见等）


# ═══════════════════════════════════════════════════════════
# 核心类
# ═══════════════════════════════════════════════════════════

class AutoKnowledgeSync:
    """
    自动知识同步器。

    工作流程：
      1. commit() — 接收回答内容，创建 wiki 页面，记录待审核日志
      2. pending_list() — 返回待审核条目列表
      3. confirm() — 确认条目（从待审核移除，可选触发重建）
      4. reject() — 拒绝条目（删除 wiki 文件，移除日志）
      5. update_entry() — 修改已入库内容
    """

    def __init__(self, dry_run: bool = False):
        self.wiki_root = WIKI_ROOT
        self.concept_dir = CONCEPT_DIR
        self.import_log = IMPORT_LOG
        self.pending_file = AUTO_IMPORT_JSON
        self.dry_run = dry_run  # T-03 Fix: 测试/审计模式，不写真实文件

        # 确保目录存在（dry_run 模式下跳过）
        if not self.dry_run:
            CONCEPT_DIR.mkdir(parents=True, exist_ok=True)
            (WIKI_ROOT / "log").mkdir(parents=True, exist_ok=True)

    # ── 核心：提交新知识 ───────────────────────────────────

    def commit(
        self,
        topic: str,
        answer: str,
        keywords: list[str],
        related_topics: Optional[list[str]] = None,
        auto_rebuild: bool = False,
    ) -> dict:
        """
        提交新知识到知识库。

        参数：
          topic — 主题/概念名称（将用于 wiki 文件名）
          answer — AI 回答内容（将被格式化为 wiki 页面）
          keywords — 关键词列表（用于标签和检索）
          related_topics — 相关概念（自动生成关联链接）
          auto_rebuild — 是否自动触发索引重建

        返回：
          {
            "success": bool,
            "entry_id": str,
            "wiki_path": str,
            "message": str
          }
        """
        try:
            # 1. 提炼内容
            summary = self._extract_summary(answer)
            content = self._format_content(answer, keywords)
            tags = ", ".join(f'"{k}"' for k in keywords[:5])
            keywords_str = "、".join(keywords)

            # 2. 构建 wiki 页面
            wiki_filename = self._sanitize_filename(topic)
            wiki_path = self.concept_dir / f"{wiki_filename}.md"

            # 3. 生成相关页面链接
            if related_topics:
                related_links = "\n".join(
                    f"- [[{t}]]" for t in related_topics
                )
            else:
                related_links = "- （暂无关联页面）"

            # 4. 生成 wiki 内容（C-02 Fix: Template.substitute 替代 .format）
            created = datetime.now().strftime("%Y-%m-%d")
            wiki_content = WIKI_TEMPLATE.substitute(
                title=topic,
                summary=summary,
                created=created,
                tags=tags,
                content=content,
                related_links=related_links,
                keywords_str=keywords_str,
            )

            # T-03 Fix: dry_run 模式 — 不写真实文件
            if self.dry_run:
                return {
                    "success": True,
                    "entry_id": "dry-run",
                    "wiki_path": f"[DRY-RUN] would write to {self.concept_dir / f'{wiki_filename}.md'}",
                    "message": "DRY-RUN: no files written (preview mode)",
                }

            # 检查是否已存在
            exists = wiki_path.exists()
            wiki_path.write_text(wiki_content, encoding="utf-8")

            # 5. 记录待审核日志
            entry_id = datetime.now().strftime("%Y%m%d%H%M%S")
            entry = ImportEntry(
                id=entry_id,
                topic=topic,
                summary=summary,
                keywords=keywords,
                content=answer,
                created=created,
                status="pending",
                wiki_path=str(wiki_path.relative_to(self.wiki_root)),
                notes="",
            )

            self._save_pending_entry(entry)

            # 6. 更新文本日志
            self._append_import_log(topic, summary, wiki_path, entry_id)

            # 7. 可选：触发索引重建
            if auto_rebuild:
                # 注意：重建在 MCP Server 外部需要单独处理
                pass

            return {
                "success": True,
                "entry_id": entry_id,
                "wiki_path": str(wiki_path),
                "message": f"{'已更新' if exists else '已创建'} wiki/{wiki_path.relative_to(self.wiki_root)}，待下次会话审核确认。",
            }

        except Exception as e:
            return {
                "success": False,
                "entry_id": None,
                "wiki_path": None,
                "message": f"自动入库失败：{e}",
            }

    # ── Q&A 专用：用户提问自动入库（自动确认） ─────────────

    def commit_qa(
        self,
        question: str,
        answer: str,
        source: str = "reasoning",
        keywords: Optional[list[str]] = None,
    ) -> dict:
        """
        提交用户问答到 wiki/问答/ 目录（自动确认，不进 pending 队列）。

        与 commit() 的核心区别：
          - 写入 QA_DIR（问答/）而非 CONCEPT_DIR（概念/）
          - 使用 QA_TEMPLATE（含问题+回答双栏格式）
          - 自动确认状态，无需人工审核
          - 适合「联网解答后离线复用」场景

        参数：
          question  — 用户原始问题
          answer    — AI 完整回答
          source    — 来源类型：web_search / knowledge_base / reasoning
          keywords  — 关键词列表（可选，自动提取）

        返回：
          {"success": bool, "wiki_path": str, "message": str}
        """
        try:
            # 确保目录存在
            if not self.dry_run:
                QA_DIR.mkdir(parents=True, exist_ok=True)

            # 1. 关键词处理
            if not keywords:
                keywords = self._extract_keywords(question, answer)
            tags = ", ".join(f'"{k}"' for k in keywords[:8])
            keywords_str = "、".join(keywords)
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            # 2. 文件名：Q- 前缀 + 问题摘要
            title = f"Q: {question[:60]}{'…' if len(question) > 60 else ''}"
            wiki_filename = f"Q-{self._sanitize_filename(question[:50])}.md"
            wiki_path = QA_DIR / wiki_filename

            # 3. 生成内容
            qa_content = QA_TEMPLATE.substitute(
                title=title,
                date=date_str,
                tags=tags,
                source=source,
                question=question.strip(),
                answer=answer.strip(),
                keywords_str=keywords_str,
            )

            # T-03: dry_run 模式
            if self.dry_run:
                return {
                    "success": True,
                    "wiki_path": f"[DRY-RUN] would write to {QA_DIR / wiki_filename}",
                    "message": "DRY-RUN: no files written",
                }

            # 4. 检查是否已存在（去重）
            exists = wiki_path.exists()
            wiki_path.write_text(qa_content, encoding="utf-8")

            # P0.1: 写入文件后自动触发增量索引（非阻塞，失败不抛异常）
            try:
                from wiki_indexer import WikiIndexer
                _rag_inc = WikiIndexer()
                _rag_inc._warmup_model()
                _inc_result = _rag_inc.index_wiki_incremental()
                print(
                    f"[auto-sync] 增量索引完成: "
                    f"新增 {_inc_result['indexed_files']} 文件/"
                    f"{_inc_result['indexed_chunks']} 块",
                    flush=True, file=sys.stderr,
                )
            except Exception as _inc_e:
                print(
                    f"[auto-sync] 增量索引失败（不影响主流程）: {_inc_e}",
                    flush=True, file=sys.stderr,
                )

            # 5. 记录到文本日志（confirmed 状态）
            entry_id = datetime.now().strftime("%Y%m%d%H%M%S")
            self._append_import_log(
                title, self._extract_summary(answer, 80),
                wiki_path, entry_id, status="qa_confirmed"
            )

            action = "已更新" if exists else "已入库"
            return {
                "success": True,
                "wiki_path": str(wiki_path.relative_to(self.wiki_root)),
                "message": f"{action} 问答/{wiki_path.relative_to(QA_DIR)} [自动确认]",
            }

        except Exception as e:
            return {
                "success": False,
                "wiki_path": None,
                "message": f"Q&A 入库失败：{e}",
            }

    # ── 审核相关 ───────────────────────────────────────────

    def pending_list(self) -> list[dict]:
        """返回所有待审核条目。"""
        entries = self._load_pending_entries()
        return [
            {
                "id": e.id,
                "topic": e.topic,
                "summary": e.summary,
                "keywords": e.keywords,
                "created": e.created,
                "wiki_path": e.wiki_path,
                "content_preview": e.content[:200] + "..." if len(e.content) > 200 else e.content,
            }
            for e in entries if e.status == "pending"
        ]

    def confirm(self, entry_id: str, notes: str = "") -> dict:
        """
        确认条目：标记为已审核，可选触发索引重建。

        返回：{"success": bool, "message": str}
        """
        entries = self._load_pending_entries()
        for e in entries:
            if e.id == entry_id:
                e.status = "confirmed"
                e.notes = notes
                self._save_all_entries(entries)
                self._append_import_log(
                    e.topic, e.summary,
                    Path(self.wiki_root / e.wiki_path),
                    e.id,
                    status="confirmed"
                )
                return {
                    "success": True,
                    "message": f"已确认「{e.topic}」，内容审核通过。"
                }
        return {"success": False, "message": f"未找到条目 ID：{entry_id}"}

    def reject(self, entry_id: str, reason: str = "") -> dict:
        """
        拒绝条目：删除 wiki 文件，标记为已拒绝。

        返回：{"success": bool, "message": str}
        """
        entries = self._load_pending_entries()
        for e in entries:
            if e.id == entry_id:
                # 删除 wiki 文件
                wiki_file = self.wiki_root / e.wiki_path
                if wiki_file.exists():
                    wiki_file.unlink()

                e.status = "rejected"
                e.notes = reason
                self._save_all_entries(entries)
                self._append_import_log(
                    e.topic, e.summary, wiki_file, e.id,
                    status=f"rejected: {reason}"
                )
                return {
                    "success": True,
                    "message": f"已拒绝「{e.topic}」，文件已删除。"
                }
        return {"success": False, "message": f"未找到条目 ID：{entry_id}"}

    def update_entry(self, entry_id: str, content: str, notes: str = "") -> dict:
        """
        更新已入库内容（修正用）。

        返回：{"success": bool, "message": str}
        """
        entries = self._load_pending_entries()
        for e in entries:
            if e.id == entry_id:
                # 重新提炼并写入
                keywords = e.keywords
                summary = self._extract_summary(content)
                tags = ", ".join(f'"{k}"' for k in keywords[:5])
                keywords_str = "、".join(keywords)

                related_links = "- （暂无关联页面）"
                wiki_content = WIKI_TEMPLATE.substitute(
                    title=e.topic,
                    summary=summary,
                    created=e.created,
                    tags=tags,
                    content=self._format_content(content, keywords),
                    related_links=related_links,
                    keywords_str=keywords_str,
                )

                wiki_file = self.wiki_root / e.wiki_path
                wiki_file.write_text(wiki_content, encoding="utf-8")

                e.content = content
                e.notes = notes
                self._save_all_entries(entries)

                return {
                    "success": True,
                    "message": f"已更新「{e.topic}」内容。"
                }
        return {"success": False, "message": f"未找到条目 ID：{entry_id}"}

    # ── 内部工具 ───────────────────────────────────────────

    def _extract_summary(self, text: str, max_len: int = 100) -> str:
        """从文本中提取摘要（前 N 字或第一句）。"""
        text = text.strip()
        if len(text) <= max_len:
            return text

        # 尝试找第一句完整的话
        m = re.search(r'^[^。！？]+[。！？]', text, re.MULTILINE)
        if m:
            summary = m.group(0).strip()
            if len(summary) <= max_len:
                return summary

        return text[:max_len].rstrip("，、.") + "..."

    @staticmethod
    def _extract_keywords(question: str, answer: str, top_n: int = 8) -> list[str]:
        """
        从问题和回答中自动提取关键词。

        策略：
          1. 从问题中提取名词性短语（2-6字中文/英文术语）
          2. 从回答中补充高频技术词
          3. 去重并截断到 top_n
        """
        import re

        keywords = []

        # 从问题中提取：连续中文（2-6字）+ 英文术语
        q_cn = re.findall(r'[\u4e00-\u9fff]{2,6}', question)
        q_en = re.findall(r'[A-Za-z][A-Za-z0-9_]{2,20}', question)
        keywords.extend(q_cn[:4])
        keywords.extend(q_en[:3])

        # 从回答中补充：加粗内容或常见模式
        bold_matches = re.findall(r'\*\*(.+?)\*\*', answer)
        if bold_matches:
            keywords.extend([b for b in bold_matches if 1 < len(b) < 15][:3])

        # 去重 + 过滤太短 + 截断
        seen = set()
        result = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen and len(kw) > 1:
                seen.add(kw_lower)
                result.append(kw)
                if len(result) >= top_n:
                    break

        return result or ["通用"]

    def _format_content(self, answer: str, keywords: list[str]) -> str:
        """
        将回答格式化为 wiki 正文。

        策略：
          - 按段落分割，保留原有结构
          - 代码块和列表保持原样
          - 关键词用 **加粗** 突出
        """
        # 关键词加粗
        content = answer.strip()
        for kw in keywords[:3]:
            if kw in content and len(kw) > 2:
                content = content.replace(kw, f"**{kw}**")

        return content

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """清理文件名（C-03 Fix: 移除非法字符、保留名、控制字符、截断长度）。

        防御矩阵：
          - NULL 字节 (\\x00)     → 删除（防止字符串截断攻击）
          - 控制字符 (\\x01-\\x1f) → 删除
          - Windows 非法字符       → 替换为 '-'
          - Windows 保留设备名      → 前缀 '_' 避免
          - 超长名 (>200字符)       → 截断
        """
        # Step 1: 移除控制字符（包括 NULL）
        name = re.sub(r'[\x00-\x1f\x7f]', '', name)
        # Step 2: 替换非法字符和空白
        name = re.sub(r'[<>:"/\\|?*\s]', '-', name)
        # Step 3: 处理 Windows 保留名（不区分大小写）
        stem = name.rsplit('.', 1)[0] if '.' in name else name
        if stem.upper() in _RESERVED_NAMES:
            name = f"_{name}"
        # Step 4: 截断（保留 .md 后缀，远低于 Windows MAX_PATH=260）
        max_len = 200
        if len(name) > max_len:
            base, ext = name.rsplit('.', 1) if '.' in name else (name, '')
            name = base[:max_len - len(ext) - 1] + '.' + ext if ext else base[:max_len]
        return name.strip('-') or "untitled"

    def _save_pending_entry(self, entry: ImportEntry):
        """追加单个条目到待审核列表。"""
        entries = self._load_pending_entries()
        entries.append(entry)
        self._save_all_entries(entries)

    def _load_pending_entries(self) -> list[ImportEntry]:
        """加载所有条目（从 JSON 文件）。"""
        if not self.pending_file.exists():
            return []
        try:
            data = json.loads(self.pending_file.read_text(encoding="utf-8"))
            return [ImportEntry(**item) for item in data]
        except Exception:
            return []

    def _save_all_entries(self, entries: list[ImportEntry]):
        """保存所有条目到 JSON 文件。"""
        data = [asdict(e) for e in entries]
        self.pending_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _append_import_log(
        self,
        topic: str,
        summary: str,
        wiki_path: Path,
        entry_id: str,
        status: str = "pending"
    ):
        """追加文本日志。"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        log_line = f"| {timestamp} | {status:10} | [[{topic}]] | {summary[:50]}... | {entry_id} |\n"

        if self.import_log.exists():
            content = self.import_log.read_text(encoding="utf-8")
            # 追加到表格末尾（表格结束行之后）
            if "| ---" in content:
                parts = content.rsplit("| ---", 1)
                content = parts[0] + "| ---\n" + log_line
            else:
                content += "\n" + log_line
        else:
            content = f"""# 自动入库日志

> 本文件记录所有自动入库的知识条目。
> 待审核 → 确认/拒绝 循环确保知识库质量。

---

| 时间 | 状态 | 主题 | 摘要 | 条目ID |
|---|---|---|---|---|
| --- | --- | --- | --- | --- |
{log_line}"""

        self.import_log.write_text(content, encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# 便捷入口（支持命令行调用）
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法：")
        print("  python auto_knowledge_sync.py commit <topic> <answer> <keywords>")
        print("  python auto_knowledge_sync.py pending")
        print("  python auto_knowledge_sync.py confirm <entry_id>")
        print("  python auto_knowledge_sync.py reject <entry_id>")
        sys.exit(1)

    sync = AutoKnowledgeSync()
    cmd = sys.argv[1]

    if cmd == "pending":
        for e in sync.pending_list():
            print(f"[{e['id']}] {e['topic']} - {e['summary']}")

    elif cmd == "commit" and len(sys.argv) >= 5:
        topic = sys.argv[2]
        answer = sys.argv[3]
        keywords = sys.argv[4].split(",")
        result = sync.commit(topic, answer, keywords)
        print(result["message"])

    elif cmd in ("confirm", "reject") and len(sys.argv) >= 3:
        entry_id = sys.argv[2]
        if cmd == "confirm":
            result = sync.confirm(entry_id)
        else:
            result = sync.reject(entry_id)
        print(result["message"])

    else:
        print("参数不足或命令错误")
        sys.exit(1)
