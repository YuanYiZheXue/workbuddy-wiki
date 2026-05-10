"""
统一知识代理 (Unified Knowledge Agent)
========================================
三层协同：MemPalace (记忆) + RAG (语义) + GraphRAG (推理)

三层分工：
  Layer 1 — MemPalace (记忆层)
    角色：身份、偏好、长期事实、跨会话上下文
    来源：mempalace MCP 的 KG 查询 + 语义搜索
    触发词：用户是谁、之前做过什么、偏好是什么

  Layer 2 — RAG / wiki_indexer (语义层)
    角色：文档级语义搜索，找"相关内容的片段"
    来源：d:/Obsidian_KN/philosophy/wiki/ 中的 157 个 md 文件
    技术：ChromaDB + OpenAI embeddings
    触发词：XX是什么意思、怎么理解、有什么关联

  Layer 3 — GraphRAG / knowledge_graph (推理层)
    角色：实体间多跳关系推理，回答"XX通过YY影响ZZ"类问题
    来源：从 wiki 内容构建的知识图谱（实体 + 关系）
    技术：自定义图结构 + BFS/DFS 遍历
    触发词：为什么、如何导致、关系是什么、有什么影响

QueryRouter 根据查询类型分发，三层结果统一融合为 context。

用法示例：
  agent = UnifiedKnowledgeAgent()
  result = await agent.query("老子'柔弱胜刚强'和'不敢为天下先'是什么关系？")
  print(result.response)
"""

import re
import json
import time
import httpx
import chromadb
from pathlib import Path
from typing import Literal, Optional

# ── 本地模块 ──────────────────────────────────────────────
from wiki_indexer import WikiIndexer
from knowledge_graph import KnowledgeGraph


# ═══════════════════════════════════════════════════════════
# QueryRouter — 查询类型判断与分发
# ═══════════════════════════════════════════════════════════

QueryType = Literal["identity", "semantic", "graph", "hybrid", "simple"]

PATTERN_IDENTITY = re.compile(
    r"(我是谁|我的名字|我的偏好|之前做过|还记得|记得我|我的职业|我的工作)", re.I
)
PATTERN_GRAPH = re.compile(
    r"(关系|影响|导致|因果|关联|为什么|如何通过|作用于|传导|链条|路径)", re.I
)
PATTERN_SEMANTIC = re.compile(
    r"(是什么|什么意思|如何理解|怎么理解|概念|定义|对比|区别|相同)", re.I
)


def classify_query(query: str) -> QueryType:
    """判断查询属于哪一层"""
    if PATTERN_IDENTITY.search(query):
        return "identity"
    if PATTERN_GRAPH.search(query):
        return "graph"
    if PATTERN_SEMANTIC.search(query):
        return "semantic"
    # 默认混合：既检索文档也查图谱
    return "hybrid"


# ═══════════════════════════════════════════════════════════
# ContextFusion — 多层上下文融合
# ═══════════════════════════════════════════════════════════

def fuse_context(
    identity_ctx: str,
    semantic_ctx: str,
    graph_ctx: str,
    query_type: QueryType,
) -> str:
    """将三层上下文合并为统一提示上下文"""
    parts = []

    if identity_ctx:
        parts.append(f"[身份记忆]\n{identity_ctx}")
    if query_type in ("semantic", "hybrid") and semantic_ctx:
        parts.append(f"[知识文档]\n{semantic_ctx}")
    if query_type in ("graph", "hybrid") and graph_ctx:
        parts.append(f"[关系推理]\n{graph_ctx}")

    if not parts:
        return "（未找到相关上下文）"

    return "\n\n".join(parts)


# ═══════════════════════════════════════════════════════════
# UnifiedKnowledgeAgent — 统一入口
# ═══════════════════════════════════════════════════════════

class UnifiedKnowledgeAgent:
    """
    三层知识系统统一查询入口。

    参数：
      wiki_dir    — wiki 根目录（默认 d:/Obsidian_KN/philosophy/wiki）
      mempalace_url — MemPalace MCP HTTP URL（可选，默认走本地 MCP stdio）
      openai_key  — OpenAI API key（环境变量 OPENAI_API_KEY）
    """

    def __init__(
        self,
        wiki_dir: str = r"d:\Obsidian_KN\philosophy\wiki",
        mempalace_url: str = "http://localhost:8080",
    ):
        self.wiki_dir = Path(wiki_dir)
        self.mempalace_url = mempalace_url

        # 初始化 RAG 层（嵌入用 sentence-transformers，本地无需 API key）
        self.rag = WikiIndexer(wiki_dir=self.wiki_dir)

        # 初始化 GraphRAG 层
        self.graph = KnowledgeGraph()

        # 状态
        self._initialized = False

    # ── 公开 API ──────────────────────────────────────────

    async def initialize(self):
        """初始化：索引 wiki + 构建图谱"""
        print("[Agent] 初始化 RAG 层...")
        await self.rag.index_wiki()
        print("[Agent] 初始化 GraphRAG 层...")
        self.graph.build_from_wiki(self.wiki_dir)
        self._initialized = True
        print(
            f"[Agent] 初始化完成！文档 {len(self.rag.documents)} 篇，"
            f"图谱 {self.graph.node_count} 个节点，{self.graph.edge_count} 条边"
        )

    async def query(
        self,
        user_query: str,
        *,
        top_k_semantic: int = 5,
        top_k_graph: int = 5,
        max_context_tokens: int = 4000,
    ) -> "QueryResult":
        """
        统一查询入口。

        返回 QueryResult（含 response, contexts, layers_hit, meta）
        """
        if not self._initialized:
            await self.initialize()

        qt = classify_query(user_query)

        # ── 三层并行查询 ──
        t0 = time.time()

        identity_task = self._query_identity(user_query)
        semantic_task = self.rag.search(user_query, top_k=top_k_semantic)
        graph_task = self.graph.query(user_query, top_k=top_k_graph)

        identity_raw, semantic_raw, graph_raw = await self._gather(
            identity_task, semantic_task, graph_task
        )

        # ── 上下文融合 ──
        identity_ctx = identity_raw
        semantic_ctx = self._format_semantic(semantic_raw, max_context_tokens)
        graph_ctx = self._format_graph(graph_raw, max_context_tokens)
        fused = fuse_context(identity_ctx, semantic_ctx, graph_ctx, qt)

        elapsed = time.time() - t0

        return QueryResult(
            query=user_query,
            query_type=qt,
            response=fused,        # 可进一步接 LLM 生成最终回答
            layers_hit=[k for k in ["identity", "semantic", "graph"]
                         if qt in ("hybrid", k)],
            contexts={
                "identity": identity_ctx,
                "semantic": semantic_ctx,
                "graph": graph_ctx,
            },
            meta={
                "elapsed_s": round(elapsed, 3),
                "docs_found": len(semantic_raw),
                "nodes_found": graph_raw.get("node_count", 0),
            },
        )

    # ── 内部方法 ──

    async def _gather(self, *tasks):
        """顺序执行（同步函数直接取值，异步函数 await）"""
        results = []
        for t in tasks:
            if hasattr(t, "__await__"):
                results.append(await t)
            else:
                results.append(t)
        return results

    async def _query_identity(self, query: str) -> str:
        """
        查询 MemPalace 身份记忆层。

        通过 MemPalace MCP HTTP bridge（或直接调用 MCP stdio 协议）。
        这里用 httpx 查本地 bridge。

        如果 bridge 不可用，降级到本地 MemPalace KG JSON 文件。
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(
                    self.mempalace_url + "/kg/query",
                    json={"query": query},
                )
                if r.status_code == 200:
                    data = r.json()
                    return self._parse_mempalace_response(data)
        except Exception:
            pass

        # 降级：直接读 MemPalace palace.json
        return self._read_local_memory()

    def _parse_mempalace_response(self, data: dict) -> str:
        """解析 MemPalace HTTP bridge 返回"""
        facts = data.get("facts", [])
        if not facts:
            return ""
        return "\n".join(
            f"- {f.get('subject', '')} —{f.get('predicate', '')}→ "
            f"{f.get('object', '')}"
            for f in facts
        )

    def _read_local_memory(self) -> str:
        """读 MemPalace 本地 palace.json 作为降级"""
        palace_file = self.wiki_dir.parent / ".mempalace" / "palace.json"
        if not palace_file.exists():
            return ""
        try:
            with open(palace_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 提取实体和关系
            entities = data.get("entities", {})
            triples = data.get("triples", [])
            lines = [f"实体：{e}" for e in entities.keys()]
            lines += [
                f"关系：{s} —{p}→ {o}" for s, p, o in triples
            ]
            return "\n".join(lines[:20])  # 限制长度
        except Exception:
            return ""

    def _format_semantic(
        self, results: list, max_tokens: int
    ) -> str:
        """将 RAG 检索结果格式化为文本"""
        if not results:
            return ""
        chunks = []
        for r in results:
            meta = r.get("metadata", {})
            chunk = (
                f"【{meta.get('title', '未知')}】\n"
                f"{r['text'][:500]}\n"
                f"来源：{meta.get('source', '')}"
            )
            chunks.append(chunk)

        joined = "\n\n---\n\n".join(chunks)
        if len(joined) > max_tokens * 4:  # 粗估 token
            joined = joined[: max_tokens * 4]
        return joined

    def _format_graph(
        self, results: dict, max_tokens: int
    ) -> str:
        """将 GraphRAG 查询结果格式化为文本"""
        if not results:
            return ""

        lines = []
        paths = results.get("paths", [])
        communities = results.get("communities", [])

        if paths:
            lines.append("## 关系路径")
            for i, p in enumerate(paths[:5], 1):
                nodes = p.get("nodes", [])
                rels = p.get("relations", [])
                path_str = " → ".join(
                    f"{n}({r})"
                    for n, r in zip(nodes, rels + [nodes[-1] if nodes else ""])
                )
                lines.append(f"  {i}. {path_str}")

        if communities:
            lines.append("\n## 概念群落")
            for c in communities[:3]:
                members = ", ".join(c.get("members", [])[:8])
                lines.append(f"  [{c.get('name', '')}] {members}")

        text = "\n".join(lines)
        if len(text) > max_tokens * 4:
            text = text[: max_tokens * 4]
        return text


# ═══════════════════════════════════════════════════════════
# QueryResult — 查询结果数据结构
# ═══════════════════════════════════════════════════════════

class QueryResult:
    def __init__(
        self,
        query: str,
        query_type: QueryType,
        response: str,
        layers_hit: list[str],
        contexts: dict,
        meta: dict,
    ):
        self.query = query
        self.query_type = query_type
        self.response = response
        self.layers_hit = layers_hit
        self.contexts = contexts
        self.meta = meta

    def __str__(self) -> str:
        return (
            f"[QueryResult | type={self.query_type} | "
            f"layers={self.layers_hit} | "
            f"elapsed={self.meta.get('elapsed_s')}s]\n"
            f"{self.response}"
        )
