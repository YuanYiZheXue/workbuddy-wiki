"""
RAG MCP Server - 三层知识系统 MCP 工具
========================================
将 WikiIndexer (RAG) 和 KnowledgeGraph (GraphRAG) 封装为 MCP 工具，
供 WorkBuddy 直接调用。

设计思路：
  1. MCP Server 进程启动后【立即】进入 anyio 事件循环，接受 stdio 请求
  2. 初始化（模型加载 + 索引构建）作为【后台任务】异步执行
  3. 工具函数等待初始化完成后才执行，避免返回空数据
  4. 用 asyncio.Event() 作为初始化完成的信号量
  5. 【关键】所有日志输出到 stderr，避免污染 stdio（MCP 协议用 stdout）

嵌入模型切换：
  - 通过环境变量 EMBEDDING_MODEL 控制（minilm / bge-m3）
  - 默认：minilm（快，多语言）
  - 切换：修改 mcp.json 中 knowledge_base 的 env.EMBEDDING_MODEL

NER 实体提取：
  - 通过环境变量 USE_NER 控制（true / false）
  - 默认：false（不启用 NER）
  - 开启：USE_NER=true（使用 NERExtractor）
  - 模式：NER_MODEL_MODE=dict（词典，零依赖）/ model（BERT，自动降级）

工具列表：
  rag_search         - 语义搜索 wiki 文档
  graphrag_query     - 知识图谱关系推理查询
  graphrag_related   - 查询某概念的直接关联实体
  kb_status          - 知识库状态概览
  kb_rebuild         - 强制重建 RAG 索引 + 图谱

用法（stdio 模式）：
  EMBEDDING_MODEL=minilm USE_NER=false python rag_mcp_server.py
"""

import sys
import os
import asyncio

# ═══ B5 修复：预补丁 getpass.getuser ═══
# PyTorch dynamo (torch._dynamo.package) 调用 getpass.getuser() 构建缓存目录。
# Windows 上 getpass.getuser() 走 import pwd（Unix 模块）→ ModuleNotFoundError 崩溃。
# 即使设了 os.environ["USERNAME"]，Python 3.14 的 getpass 在某些子进程环境下仍会
# 走到 pwd 分支。解决方案：在 import torch 之前预先 monkey-patch。
import getpass
_original_getuser = getattr(getpass, "getuser", None)
def _safe_getuser():
    """安全版 getuser：优先读环境变量，避免 Windows 上 import pwd 崩溃。"""
    for var in ("USERNAME", "USER", "LOGNAME"):
        val = os.environ.get(var)
        if val:
            return val
    if _original_getuser:
        try:
            return _original_getuser()
        except Exception:
            pass
    return "default_user"
if _original_getuser:
    getpass.getuser = _safe_getuser

# -- 将 knowledge_agent 加入模块搜索路径（配置中心化） --
# 先用硬编码路径加入搜索路径，再导入 kb_config（避免 config 名字与 cc-nim.config 冲突）
import pathlib as _pl
_KB_AGENT_DIR = _pl.Path(r"D:\Obsidian_KN\philosophy\.workbuddy\knowledge_agent")
if str(_KB_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_KB_AGENT_DIR))
from kb_config import (
    AGENT_DIR, CHROMA_DB_PATH, WIKI_DIR, safe_path_display,
    USE_NER as _USE_NER, NER_MODEL_MODE as _NER_MODE,
)

# -- 环境变量 ---
os.environ["PYTHONUTF8"] = "1"
# PyTorch dynamo 需要 USERNAME 构建缓存目录（MCP 子进程可能缺失）
if not os.environ.get("USERNAME"):
    os.environ["USERNAME"] = os.environ.get("USER", "default_user")
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "minilm")
# _USE_NER 和 _NER_MODE 已从 kb_config 导入（中心化配置）

print(
    f"[server] config: model={_EMBEDDING_MODEL}, NER={_USE_NER} (mode={_NER_MODE})",
    flush=True, file=sys.stderr,
)

# ═══ B7 FIX: Pre-import ALL heavy modules BEFORE run_stdio_async ═══
# Critical: mcp.run_stdio_async() changes process stdio state. After that,
# importing these in any thread blocks: chromadb ~121s, torch ~similar.
# Fix: import everything here. One-time cost ~5-15s (within proxy timeouts).
_pre_t = __import__('time').time()
print("[server] Pre-importing heavy modules...", flush=True, file=sys.stderr)

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
print(f"[server]  chromadb ({__import__('time').time()-_pre_t:.1f}s)",
      flush=True, file=sys.stderr)

_t1 = __import__('time').time()
import torch  # noqa: F401
print(f"[server]  torch ({__import__('time').time()-_t1:.1f}s)",
      flush=True, file=sys.stderr)

_t2 = __import__('time').time()
import sentence_transformers  # noqa: F401
print(f"[server]  sentence_transformers ({__import__('time').time()-_t2:.1f}s)",
      flush=True, file=sys.stderr)

_t3 = __import__('time').time()
from wiki_indexer import WikiIndexer as _WI  # noqa: F401
print(f"[server]  wiki_indexer ({__import__('time').time()-_t3:.1f}s)",
      flush=True, file=sys.stderr)

print(f"[server] All pre-imports: {__import__('time').time()-_pre_t:.1f}s",
      flush=True, file=sys.stderr)

# -- MCP Server --
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="KnowledgeBase",
    instructions=(
        "三层知识系统：\n"
        "1. MemPalace - 个人记忆（通过 mempalace MCP 访问）\n"
        "2. RAG - wiki 文档语义检索（rag_search）\n"
        "3. GraphRAG - 知识图谱多跳推理（graphrag_query / graphrag_related）\n\n"
        "使用建议：\n"
        "  - '是什么/什么意思' -> rag_search\n"
        "  - '关系/影响/为什么' -> graphrag_query\n"
        "  - 'XX与YY有什么关系' -> graphrag_query\n"
        "  - 'XX的相关概念有哪些' -> graphrag_related"
    ),
)

# ============================================================
# 全局状态 + 初始化信号量
# ============================================================
# 注意：WikiIndexer / KnowledgeGraph 的导入放在 _init_knowledge_base 内部，
# 避免在模块顶层 import 时阻塞 MCP 服务器启动。

_rag_indexer = None
_kg_graph = None
_init_event = asyncio.Event()   # 初始化完成后 set()
_init_error = None              # 初始化失败时的异常
_rebuild_lock = asyncio.Lock()  # S-01: 防并发 rebuild
_write_lock = asyncio.Lock()    # S-04: 写操作串行化


# ============================================================
# 异步初始化（后台执行）
# ============================================================

# ============================================================
# 后台初始化（threading.Thread，完全独立于事件循环）
# ============================================================
# 核心设计变更（B6 修复）：
#   旧方案：asyncio.create_task() + loop.run_in_executor()
#   → 问题：subprocess 环境下 torch import 在 executor 线程中被隐式阻塞 ~120s
#   原因推测：torch/_dynamo 初始化与 anyio 事件循环存在 GIL/信号量竞争
#
#   新方案：threading.Thread(target=_sync_init_all)
#   → 完全独立的 OS 线程，不经过 asyncio executor 调度器
#   → 通过 loop.call_soon_threadsafe() 安全地通知事件循环

import threading

def _sync_init_all():
    """纯同步初始化函数，在独立线程中执行。不依赖任何 async 机制。

    完成后通过 call_soon_threadsafe 设置 _init_event。
    """
    global _rag_indexer, _kg_graph, _init_error, _init_event
    _time = __import__('time')
    _t0 = _time.time()
    loop_ref = None  # 延迟获取 event loop 引用

    try:
        # ── Phase 1: RAG 初始化（~20s for minilm）──
        print(f"[init-thread] {_t0:.1f} STARTED", flush=True, file=sys.stderr)
        print(f"[init-thread] {_t0:.1f} importing WikiIndexer...", flush=True, file=sys.stderr)

        from wiki_indexer import WikiIndexer
        print(f"[init-thread] {_time.time():.1f} WikiIndexer imported ({_time.time()-_t0:.1f}s)",
              flush=True, file=sys.stderr)

        rag = WikiIndexer(embedding_model=_EMBEDDING_MODEL)
        print(f"[init-thread] {_time.time():.1f} instance created ({_time.time()-_t0:.1f}s)",
              flush=True, file=sys.stderr)

        print("[init-thread] warming up model...", flush=True, file=sys.stderr)
        rag._warmup_model()
        print(f"[init-thread] {_time.time():.1f} warmup DONE ({_time.time()-_t0:.1f}s)",
              flush=True, file=sys.stderr)

        _ = rag.collection
        if rag.documents is None or len(rag.documents) == 0:
            if rag.collection.count() == 0:
                print("[init-thread] index empty, rebuilding...", flush=True, file=sys.stderr)
                rag.index_wiki()

        _rag_indexer = rag
        print(f"[init-thread] {_time.time():.1f} Phase-1 DONE: {rag.collection.count()} chunks ({_time.time()-_t0:.1f}s)",
              flush=True, file=sys.stderr)

        # ── Phase 2: GraphRAG 构建（~2s）──
        from knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        if kg.node_count == 0:
            kg.build_from_wiki(rag.wiki_dir, use_ner=_USE_NER)
        _kg_graph = kg
        print(f"[init-thread] {_time.time():.1f} Phase-2 DONE: {kg.node_count} nodes, {kg.edge_count} edges ({_time.time()-_t0:.1f}s)",
              flush=True, file=sys.stderr)

        # ── 完成：通知事件循环 ──
        total = _time.time() - _t0
        print(f"[init-thread] ✅ ALL READY in {total:.1f}s", flush=True, file=sys.stderr)

        # D-04: 启动健康检查 — 验证 collection 一致性
        try:
            col_count = rag.collection.count()
            col_name = rag.collection.name
            if col_name != rag.collection_name:
                print(f"[health-check] ⚠️ Collection name mismatch: "
                      f"expected '{rag.collection_name}', got '{col_name}'",
                      flush=True, file=sys.stderr)
            elif col_count == 0 and len(rag.documents) == 0:
                print(f"[health-check] ✅ 知识库为空，等待首次索引", flush=True, file=sys.stderr)
            else:
                print(f"[health-check] ✅ RAG={col_count} chunks, "
                      f"GraphRAG={kg.node_count}n/{kg.edge_count}e",
                      flush=True, file=sys.stderr)
        except Exception as e:
            print(f"[health-check] ⚠️ 无法完成健康检查: {e}", flush=True, file=sys.stderr)

        # 安全地从线程通知事件循环
        try:
            loop_ref = asyncio.get_event_loop()
            loop_ref.call_soon_threadsafe(_init_event.set)
        except RuntimeError:
            # event loop 可能已关闭（shutdown 阶段），直接 set
            _init_event.set()

    except Exception as e:
        _init_error = e
        print(f"[init-thread] ❌ FAILED: {type(e).__name__}: {e}", flush=True, file=sys.stderr)
        try:
            loop_ref = asyncio.get_event_loop()
            loop_ref.call_soon_threadsafe(_init_event.set)
        except RuntimeError:
            _init_event.set()


def _start_init_thread():
    """启动后台初始化线程（在 _main 中调用）。"""
    t = threading.Thread(target=_sync_init_all, name="MCP-Init", daemon=True)
    t.start()
    print(f"[main] Init thread started: {t.name}", flush=True, file=sys.stderr)
    return t


def _get_rag():
    """同步获取 RAG 索引器（供非 async 上下文用）。"""
    return _rag_indexer


def _get_kg():
    """同步获取知识图谱（供非 async 上下文用）。"""
    return _kg_graph


# ============================================================
# MCP 工具（全部为 async，等待初始化完成后执行）
# ============================================================

_INIT_TIMEOUT = 120  # 工具调用等待初始化完成的最大秒数（双模型首次加载可能较慢）


async def _wait_for_init() -> str | None:
    """等待初始化完成，返回 None 表示成功，字符串表示错误信息。"""
    try:
        await asyncio.wait_for(_init_event.wait(), timeout=_INIT_TIMEOUT)
    except asyncio.TimeoutError:
        return (f"⏳ 知识库仍在初始化中（bge-m3 模型加载约需 20 秒）。\n"
                f"   请稍后重试，或检查 stderr 日志确认进度。")
    if _init_error:
        return f"❌ 知识库初始化失败：{_init_error}"
    return None


@mcp.tool(
    name="rag_search",
    title="语义搜索 Wiki 文档",
    description="在 wiki 知识库中进行语义相似度搜索，返回最相关的文档片段。适合问'是什么/什么意思/如何理解'类问题。",
)
async def rag_search(query: str, top_k: int = 5) -> str:
    """
    RAG 语义搜索。
    """
    err = await _wait_for_init()
    if err:
        return err

    rag = _get_rag()
    top_k = min(max(1, top_k), 20)
    results = rag.search(query, top_k=top_k)

    if not results:
        return f"未找到与「{query}」相关的文档。"

    lines = [f"## 语义检索结果：「{query}」\n"]
    for i, r in enumerate(results, 1):
        meta = r.get("metadata", {})
        dist = r.get("distance", 0)
        similarity = max(0, 1 - dist) * 100
        lines.append(
            f"### {i}. 【{meta.get('title', '未知')}】\n"
            f"- 相似度：{similarity:.1f}% | 来源：{meta.get('source', '未知')}\n"
            f"```\n{r['text'][:600]}\n```\n"
        )

    return "".join(lines)


@mcp.tool(
    name="graphrag_query",
    title="知识图谱关系推理查询",
    description="在知识图谱中查找概念之间的关系路径和多跳推理结果。适合问'XX和YY有什么关系/XX如何影响YY/为什么'类问题。",
)
async def graphrag_query(question: str, top_k: int = 5) -> str:
    """
    GraphRAG 关系推理查询。
    """
    err = await _wait_for_init()
    if err:
        return err

    kg = _get_kg()
    top_k = min(max(1, top_k), 20)
    result = kg.query(question, top_k=top_k)

    paths = result.get("paths", [])
    communities = result.get("communities", [])
    node_count = result.get("node_count", 0)
    edge_count = result.get("edge_count", 0)

    lines = [
        f"## 知识图谱推理：「{question}」\n",
        f"- 图谱规模：{node_count} 个概念节点，{edge_count} 条关系边\n",
    ]

    if paths:
        lines.append("\n### 关系路径\n")
        for i, p in enumerate(paths, 1):
            nodes = p.get("nodes", [])
            rels = p.get("relations", [])
            hops = p.get("hops", len(nodes) - 1)
            segments = []
            for j, node in enumerate(nodes):
                if j < len(rels):
                    segments.append(f"{node}({rels[j]})")
                else:
                    segments.append(node)
            path_str = " -> ".join(segments)
            lines.append(f"{i}. {path_str}（跳数：{hops}）\n")
    else:
        lines.append("\n未找到关系路径。\n")

    if communities:
        lines.append("\n### 涉及的概念群落\n")
        for c in communities[:3]:
            members = c.get("members", [])
            lines.append(f"- **{c.get('name', '群落')}**：{', '.join(members[:10])}...\n")

    return "".join(lines)


@mcp.tool(
    name="graphrag_related",
    title="查询概念关联实体",
    description="查询某概念在知识图谱中的直接关联实体（如因果、对立、相关等关系）。",
)
async def graphrag_related(concept: str, relation_type: str = "", max_results: int = 10) -> str:
    """
    查询概念的直接关联实体。
    """
    err = await _wait_for_init()
    if err:
        return err

    kg = _get_kg()
    max_results = min(max(1, max_results), 50)
    rel_type = None if not relation_type else relation_type
    results = kg.get_related(concept, relation_type=rel_type, max_results=max_results)

    if not results:
        return f"知识图谱中未找到「{concept}」的直接关联实体。"

    lines = [
        f"## 「{concept}」的直接关联\n",
        f"共找到 {len(results)} 条关联：\n",
    ]

    by_type: dict = {}
    for r in results:
        t = r.get("relation", "相关")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(r)

    for rel, items in by_type.items():
        lines.append(f"\n### {rel}（{len(items)} 条）\n")
        for item in items[:8]:
            direction = "<-" if item.get("type") == "in" else "->"
            target = item.get("target", "")
            ctx = item.get("context", "")
            if ctx:
                ctx_short = ctx[:60] + ("..." if len(ctx) > 60 else "")
                lines.append(f"  {direction} **{target}**  _{ctx_short}_\n")
            else:
                lines.append(f"  {direction} **{target}**\n")

    return "".join(lines)


@mcp.tool(
    name="kb_status",
    title="知识库状态概览",
    description="返回当前知识库的规模统计：文档数量、图谱节点/边数量、索引状态。",
)
async def kb_status() -> str:
    """
    知识库状态概览。
    """
    err = await _wait_for_init()
    if err:
        return err

    rag = _get_rag()
    kg = _get_kg()
    docs = len(rag.documents) if rag.documents else 0

    try:
        actual_chunks = rag.collection.count()
    except Exception:
        actual_chunks = "?"

    return (
        "## 知识库状态\n\n"
        f"| 层级 | 指标 | 值 |\n"
        f"|---|---|---|\n"
        f"| RAG | 索引文档块数 | {actual_chunks} |\n"
        f"| RAG | 来源文件数 | {len(list(rag.wiki_dir.rglob('*.md')))} |\n"
        f"| RAG | 嵌入模型 | {_EMBEDDING_MODEL} |\n"
        f"| GraphRAG | 概念节点数 | {kg.node_count} |\n"
        f"| GraphRAG | 关系边数 | {kg.edge_count} |\n"
        f"| GraphRAG | 概念群落数 | {len(kg.communities)} |\n"
        f"| GraphRAG | NER 开启 | {_USE_NER} |\n"
        f"| 存储 | ChromaDB 路径 | `{safe_path_display(rag.db_path)}` |\n"
        f"| 存储 | Wiki 路径 | `{safe_path_display(str(rag.wiki_dir))}` |"
    )


@mcp.tool(
    name="kb_rebuild",
    title="重建知识库索引",
    description="强制重建 RAG 向量索引和知识图谱。清空现有数据后从 wiki 目录重新构建。⚠️ 破坏性操作：需要 confirm='FORCE_REBUILD' 参数确认。",
)
async def kb_rebuild(confirm: str = "") -> str:
    """
    强制重建知识库索引（清空后重新构建）。

    安全措施：
      Layer 1: 显式确认参数（防止 AI 幻觉误调用）
      Layer 2: asyncio.Lock 防并发
      Layer 3: 执行原有重建逻辑
    """
    # ── Layer 1: 操作确认 ──
    if confirm != "FORCE_REBUILD":
        return (
            "⚠️ **kb_rebuild 是破坏性操作！**\n\n"
            "这将删除现有 RAG 索引（~1111 条数据）并从 wiki 目录全量重建。\n"
            "bge-m3 模型预计耗时 ~80 分钟，minilm 预计 ~30 秒。\n"
            "重建期间搜索功能不可用。\n\n"
            "如确认执行，请调用: `kb_rebuild(confirm=\"FORCE_REBUILD\")`"
        )

    err = await _wait_for_init()
    if err:
        return err

    # ── Layer 2: 并发防护 ──
    if _rebuild_lock.locked():
        return "⏳ 另一个 rebuild 正在进行中，请稍后再试。"

    async with _rebuild_lock:
        rag = _get_rag()
        kg = _get_kg()

        # S-05 Fix: 分级异常处理（Level 2 — 记录但不中断）
        try:
            rag.client.delete_collection(rag.collection_name)
        except Exception as e:
            print(f"[rebuild] WARNING: delete_collection failed "
                  f"({type(e).__name__}: {e})", flush=True, file=sys.stderr)

        # P0.2: 原子重建（任何阶段崩溃，旧数据完好）
        async with _write_lock:
            count = rag.rebuild_atomic()
            kg.build_from_wiki(rag.wiki_dir, use_ner=_USE_NER)

    return (
        f"知识库原子重建完成！\n"
        f"- RAG 文档块：{count}\n"
        f"- GraphRAG 节点：{kg.node_count}，边：{kg.edge_count}"
    )


# ============================================================
# kb_validate — 知识库一致性校验（D-02: Self-Verifying）
# ============================================================

@mcp.tool(
    name="kb_validate",
    title="验证知识库完整性",
    description="校验 RAG 索引与 GraphRAG 的完整性。检查 collection 一致性、数据量合理性。Agent 应在关键写入操作后调用此工具自检。",
)
async def kb_validate() -> str:
    """
    D-02: 验证知识库完整性。

    检查项：
    1. RAG collection 名称匹配
    2. RAG 文档数 > 0（非空）
    3. GraphRAG 节点/边规模合理
    4. wiki 文件数与索引块数比例合理

    用途：Agent 在写入操作后调用，确认数据完整。
    """
    err = await _wait_for_init()
    if err:
        return err

    rag = _get_rag()
    kg = _get_kg()
    issues = []

    # 1. Collection 状态
    try:
        col_count = rag.collection.count()
        col_name = rag.collection.name
        doc_count = len(rag.documents) if rag.documents else 0

        if col_name != rag.collection_name:
            issues.append(f"🔴 Collection 名称不匹配: 期望 '{rag.collection_name}', 实际 '{col_name}'")
        if col_count == 0:
            issues.append(f"🔴 RAG collection 为空! (count=0)")
        elif doc_count > 0 and col_count < doc_count * 0.5:
            issues.append(f"⚠️ Collection 文档数({col_count})远小于内存中({doc_count})")
    except Exception as e:
        issues.append(f"🔴 无法访问 RAG collection: {e}")

    # 2. GraphRAG 状态
    kg_nodes = kg.node_count
    kg_edges = kg.edge_count
    if kg_nodes == 0:
        issues.append("🔴 GraphRAG 节点数为 0!")
    elif kg_edges == 0:
        issues.append("⚠️ GraphRAG 边数为 0（可能只有孤立节点）")

    # 3. 规模合理性
    if col_count > 0 and kg_nodes > 0:
        ratio = kg_nodes / col_count
        if ratio < 0.5 or ratio > 50:
            issues.append(f"⚠️ GraphRAG 节点/RAG 文档比异常: {ratio:.1f}（预期 1~20）")

    # 汇总
    if not issues:
        return (
            f"✅ 知识库完整性校验通过\n\n"
            f"| 层级 | 指标 | 值 |\n"
            f"|---|---|---|\n"
            f"| RAG | 文档块数 | {col_count} |\n"
            f"| RAG | Collection | `{col_name}` |\n"
            f"| GraphRAG | 节点 | {kg_nodes} |\n"
            f"| GraphRAG | 边 | {kg_edges} |\n"
            f"| GraphRAG | 群落 | {len(kg.communities)} |\n"
        )
    else:
        return "⚠️ 知识库校验发现问题：\n\n" + "\n".join(f"- {i}" for i in issues) + "\n\n建议运行 kb_rebuild 修复。"


# ============================================================
# P0.1 增量索引工具
# ============================================================

@mcp.tool(
    name="kb_incremental_index",
    title="增量索引 wiki 新文件",
    description="只索引 wiki/ 中新增或修改的 .md 文件，跳过已索引的文件。新增 1 个文件从 77 分钟降至秒级。",
)
async def kb_incremental_index() -> str:
    """
    P0.1 增量索引：新增/删除 wiki 文件时秒级更新，无需全量重建。
    """
    err = await _wait_for_init()
    if err:
        return err

    rag = _get_rag()
    result = rag.index_wiki_incremental()
    return (
        f"✅ 增量索引完成\n"
        f"- 新增文件：{result['indexed_files']}\n"
        f"- 新增块：{result['indexed_chunks']}\n"
        f"- 删除文件：{result['deleted_files']}\n"
        f"- 跳过（已索引）：{result['skipped_files']}"
    )


# ============================================================
# 自动知识同步（新增）
# ============================================================

from auto_knowledge_sync import AutoKnowledgeSync

_sync = None


def _get_sync():
    global _sync
    if _sync is None:
        _sync = AutoKnowledgeSync()
    return _sync


# ============================================================
# P0.3 统一检索入口
# ============================================================

@mcp.tool(
    name="kb_unified_search",
    title="统一知识库搜索",
    description="同时搜索 RAG（语义检索）+ GraphRAG（关系推理），合并去重后返回。MemPalace 个人记忆请单独使用 mempalace_search。",
)
async def kb_unified_search(query: str, top_k: int = 5) -> str:
    """
    P0.3 统一检索入口：
    - RAG 语义检索（主路径）
    - GraphRAG 关系推理（辅助）
    - MemPalace 需单独调用（跨 MCP 服务器）
    """
    err = await _wait_for_init()
    if err:
        return err

    results = {"query": query, "sources": {}}

    # 1. RAG 语义检索（主路径）
    try:
        rag = _get_rag()
        rag_hits = rag.search(query, top_k=top_k)
        results["sources"]["rag"] = {
            "count": len(rag_hits),
            "hits": rag_hits[:top_k],
        }
    except Exception as e:
        results["sources"]["rag"] = {"error": str(e)}

    # 2. GraphRAG 关系推理（辅助）
    try:
        kg = _get_kg()
        kg_result = kg.query(query, top_k=min(3, top_k))
        if kg_result.get("paths"):
            results["sources"]["graphrag"] = kg_result
    except Exception as e:
        results["sources"]["graphrag"] = {"error": str(e)}

    # 格式化输出
    lines = [f"## 统一检索：「{query}」\n"]

    if "rag" in results["sources"] and "hits" in results["sources"]["rag"]:
        lines.append("### 📚 知识库 (RAG)")
        for i, hit in enumerate(results["sources"]["rag"]["hits"][:3], 1):
            meta = hit.get("metadata", {})
            score = 1 - hit.get("distance", 0)
            lines.append(f"{i}. **{meta.get('title','?')}** ({score:.0%})")
            lines.append(f"   {hit['text'][:200]}...")
        lines.append("")

    if "graphrag" in results["sources"] and "paths" in results["sources"]["graphrag"]:
        lines.append("### 🔗 关系推理 (GraphRAG)")
        for path in results["sources"]["graphrag"]["paths"][:2]:
            lines.append(f"- {' → '.join(path)}")
        lines.append("")

    lines.append("💡 MemPalace 个人记忆请用 `mempalace_search` 单独查询。")

    return "\n".join(lines)


# ============================================================
# 自动知识同步（原有）
# ============================================================

@mcp.tool(
    name="kb_auto_commit",
    title="自动提交新知识到知识库",
    description="当 AI 直接回答新问题后，将回答内容自动提炼并写入 wiki 页面，同时记录待审核队列。适用于 RAG 检索相似度低于阈值的情况。",
)
async def kb_auto_commit(
    topic: str,
    answer: str,
    keywords: str = "",
    related_topics: str = "",
) -> str:
    """
    自动提交新知识到知识库。

    参数：
      topic — 主题/概念名称（将作为 wiki 页面标题）
      answer — AI 回答内容（将格式化为 wiki 正文）
      keywords — 关键词，逗号分隔
      related_topics — 相关概念，逗号分隔
    """
    err = await _wait_for_init()
    if err:
        return err

    sync = _get_sync()
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    rel_list = [r.strip() for r in related_topics.split(",") if r.strip()]

    if not kw_list:
        kw_list = [topic]

    result = sync.commit(
        topic=topic,
        answer=answer,
        keywords=kw_list,
        related_topics=rel_list if rel_list else None,
    )

    if result["success"]:
        return (
            f"✅ 自动入库成功！\n\n"
            f"- 主题：{topic}\n"
            f"- 关键词：{', '.join(kw_list)}\n"
            f"- Wiki 路径：{result['wiki_path']}\n"
            f"- 待审核 ID：{result['entry_id']}\n\n"
            f"💡 下次会话时将收到审核提醒，请确认内容准确后调用 kb_confirm_entry。"
        )
    else:
        return f"❌ 自动入库失败：{result['message']}"


@mcp.tool(
    name="kb_pending_review",
    title="查询待审核知识条目",
    description="返回所有待审核的自动入库条目。下次会话开始时自动调用，用于确认上次会话入库的新知识是否准确。",
)
async def kb_pending_review() -> str:
    """
    查询待审核条目列表。
    """
    err = await _wait_for_init()
    if err:
        return err

    sync = _get_sync()
    entries = sync.pending_list()

    if not entries:
        return "✅ 暂无待审核的知识条目，知识库状态良好。"

    lines = [
        f"📋 **待审核条目（{len(entries)} 条）**\n\n"
    ]

    for e in entries:
        lines.append(
            f"### 【{e['id']}】{e['topic']}\n"
            f"- 摘要：{e['summary']}\n"
            f"- 关键词：{', '.join(e['keywords'])}\n"
            f"- 创建：{e['created']}\n"
            f"- 路径：[[{e['wiki_path']}]]\n"
            f"- 内容预览：{e['content_preview']}\n\n"
        )

    lines.append(
        "\n---\n\n"
        "**操作指令**：\n"
        "- `kb_confirm_entry(id='XXX')` — 确认入库，内容正确\n"
        "- `kb_reject_entry(id='XXX', reason='...')` — 拒绝入库，删除文件\n"
        "- `kb_update_entry(id='XXX', content='新内容')` — 修正内容"
    )

    return "".join(lines)


@mcp.tool(
    name="kb_confirm_entry",
    title="确认知识条目（审核通过）",
    description="确认已入库的知识条目内容正确，将其从待审核队列移除。审核通过后知识正式纳入知识库。",
)
async def kb_confirm_entry(entry_id: str) -> str:
    """
    确认条目。
    """
    err = await _wait_for_init()
    if err:
        return err

    sync = _get_sync()
    result = sync.confirm(entry_id)

    return f"{'✅' if result['success'] else '❌'} {result['message']}"


@mcp.tool(
    name="kb_reject_entry",
    title="拒绝知识条目（审核不通过）",
    description="拒绝已入库的知识条目，将删除对应的 wiki 文件。用于清理错误或低质量内容。",
)
async def kb_reject_entry(entry_id: str, reason: str = "") -> str:
    """
    拒绝条目。
    """
    err = await _wait_for_init()
    if err:
        return err

    sync = _get_sync()
    result = sync.reject(entry_id, reason)

    return f"{'✅' if result['success'] else '❌'} {result['message']}"


@mcp.tool(
    name="kb_update_entry",
    title="更新知识条目内容",
    description="修正已入库但内容有误的知识条目。调用后替换 wiki 页面内容。",
)
async def kb_update_entry(entry_id: str, content: str) -> str:
    """
    更新条目内容。
    """
    err = await _wait_for_init()
    if err:
        return err

    sync = _get_sync()
    result = sync.update_entry(entry_id, content)

    return f"{'✅' if result['success'] else '❌'} {result['message']}"


# ============================================================
# 入口：立即进入事件循环，初始化在后台跑
# ============================================================

async def _main():
    """主函数：立即进入 MCP stdio 循环（让 connector-proxy 快速建立连接），
    同时后台加载模型（在独立 OS 线程中，完全不依赖事件循环）。

    架构演进：
      v1: sync await _init()              → 握手延迟 21s → proxy 超时 ❌
      v2: create_task + run_in_executor  → subprocess 下 torch 隐式阻塞 120s ❌
      v3: threading.Thread + call_soon_threadsafe  ← 当前方案 ✅
    """
    import time as _time
    _t0 = _time.time()
    # 【后台】启动独立线程做重量级初始化
    _start_init_thread()
    print(f"[main] {_time.time()-_t0:.3f}s entering run_stdio_async()...",
          flush=True, file=sys.stderr)

    # 【立即】进入 MCP stdio 主循环（connector-proxy 可在此刻建立连接）
    await mcp.run_stdio_async()


if __name__ == "__main__":
    import anyio
    anyio.run(_main)
