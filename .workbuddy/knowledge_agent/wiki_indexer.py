"""
WikiIndexer — RAG 语义检索层
===============================
将 d:\\Obsidian_KN\\philosophy\\wiki 中的 markdown 文件向量化，
存入 ChromaDB（持久化），支持语义相似度搜索。

技术栈：
  - ChromaDB 1.5.8（持久化存储）
  - sentence-transformers（本地嵌入模型，支持多模型切换）
  - Python 3.14

嵌入模型切换：
  - 通过 __init__ 的 embedding_model 参数选择
  - 不同模型使用不同的 collection 名称，互不干扰
  - 可选：minilm（默认，快）、bge-m3（多语言，质量高）

用法：
  indexer = WikiIndexer(embedding_model="bge-m3")
  indexer.index_wiki()          # 一次性索引
  results = indexer.search("老子柔弱胜刚强")  # 语义搜索
"""

import re
import sys
import hashlib
import gc
import chromadb
from pathlib import Path
from typing import Optional
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# ═════════════════════════════════════════════════════
# 嵌入模型配置
# ═════════════════════════════════════════════════════

SUPPORTED_MODELS = {
    "minilm": {
        "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
        "dimension": 384,
        "description": "多语言快训模型（默认），384维，速度快",
    },
    "bge-small": {
        "model_name": "BAAI/bge-small-zh-v1.5",
        "dimension": 512,
        "description": "中文高质量小模型，512维，速度快，中文语义优",
    },
    "bge-m3": {
        "model_name": "BAAI/bge-m3",
        "dimension": 1024,
        "description": "多语言高质量大模型，1024维，加载慢(~28s)，仅按需使用",
    },
}


def _get_embedding_function(model_key: str):
    """根据模型 key 返回对应的 SentenceTransformer embedding function（懒加载）。"""
    if model_key not in SUPPORTED_MODELS:
        raise ValueError(
            f"不支持的模型：{model_key}。"
            f"可选：{', '.join(SUPPORTED_MODELS.keys())}"
        )
    model_name = SUPPORTED_MODELS[model_key]["model_name"]
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )


# ═════════════════════════════════════════════════════
# C-01 路径配置（模块级，Python 3.14 兼容：类体 try/except 内赋值的变量
# 对方法闭包不可见，必须提升到模块级）
# ═════════════════════════════════════════════════════
try:
    from kb_config import CHROMA_DB_PATH as _CFG_DB, WIKI_DIR as _CFG_WIKI
    _DB_PATH = str(_CFG_DB)
    _DEFAULT_WIKI_DIR = str(_CFG_WIKI)
except ImportError:
    _DB_PATH = r"d:\Obsidian_KN\philosophy\.workbuddy\chroma_db"
    _DEFAULT_WIKI_DIR = r"d:\Obsidian_KN\philosophy\wiki"

# ═════════════════════════════════════════════════════
# WikiIndexer — 核心类
# ═════════════════════════════════════════════════════

class WikiIndexer:
    """
    wiki 文档向量化 + 语义检索。

    ChromaDB 持久化路径：d:\\Obsidian_KN\\philosophy\\.workbuddy\\chroma_db
    不同嵌入模型使用不同 collection，互不干扰。
    """

    # 类级引用（指向模块级变量）
    DB_PATH = _DB_PATH

    def __init__(
        self,
        wiki_dir: str = "",  # C-01: 默认从 config 获取
        db_path: Optional[str] = None,
        embedding_model: str = "minilm",  # "minilm" | "bge-m3"
    ):
        self.wiki_dir = Path(wiki_dir or _DEFAULT_WIKI_DIR)
        self.db_path = db_path or self.DB_PATH
        self.embedding_model = embedding_model

        # collection 名称包含模型标识，避免不同模型互相覆盖
        self.collection_name = f"philosophy_wiki_{embedding_model}"

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = None
        self.documents: list[dict] = []
        self._embedding_function = None

    def _warmup_model(self):
        """预热嵌入模型（大模型首次加载需 15-20s，提前触发避免超时）。"""
        import sys
        if self._embedding_function is None:
            model_name = SUPPORTED_MODELS[self.embedding_model]["model_name"]
            print(f"[warmup] 正在加载嵌入模型 {self.embedding_model} ({model_name})...",
                  flush=True, file=sys.stderr)
            t0 = __import__('time').time()
            self._embedding_function = _get_embedding_function(self.embedding_model)
            # 触发一次实际嵌入以完成权重加载（sentence-transformers 懒加载）
            try:
                self._embedding_function(["warmup"])
            except Exception as e:
                # S-05 Fix: 分级异常（Level 1 — 预期内可恢复）
                # warmup 探针失败不致命，首次真正使用时会重试，但必须记录
                print(f"[warmup] WARNING: probe failed ({type(e).__name__}: {e}), "
                      f"will retry on first real call", flush=True, file=sys.stderr)
            elapsed = __import__('time').time() - t0
            print(f"[warmup] 模型就绪（{elapsed:.1f}s）", flush=True, file=sys.stderr)

    @property
    def collection(self):
        """T-04 Fix: 显式前置条件检查。

        v3 架构中 _sync_init_all() 已在 Phase 1 调用 _warmup_model()。
        如果到达这里 _embedding_function 仍为 None，说明 init 流程异常 ——
        与其隐式触发 18s 阻塞的 warmup，不如立即失败并给出明确诊断。
        """
        if self._collection is None:
            # T-04: 不再隐式调用 _warmup_model()
            if self._embedding_function is None:
                raise RuntimeError(
                    "Collection accessed before warmup_model(). "
                    "In v3 architecture, _sync_init_all() must call "
                    "_warmup_model() explicitly before any collection access. "
                    "If this error occurs, the init thread may have failed "
                    "(check stderr for [init-thread] logs)."
                )

            try:
                # 先不带 embedding_function 拿已有 collection
                self._collection = self.client.get_collection(
                    name=self.collection_name,
                )
            except chromadb.errors.NotFoundError:
                # 不存在则创建（使用已预热的 ef）
                self._collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self._embedding_function,
                    metadata={"description": f"philosophy wiki docs ({self.embedding_model})"},
                )

        # D-01: 名称断言 — 防止裸 ChromaDB API 污染
        # 任何 agent 通过任何路径获取 collection 后，必须名称匹配。
        # 不匹配 → 立即报错，阻止错误数据写入。
        if self._collection is not None:
            actual_name = self._collection.name
            if actual_name != self.collection_name:
                raise RuntimeError(
                    f"🔴 FATAL: Collection name mismatch!\n"
                    f"   Expected: '{self.collection_name}'\n"
                    f"   Actual:   '{actual_name}'\n"
                    f"   This means code bypassed WikiIndexer and used a raw ChromaDB client.\n"
                    f"   Fix: always use WikiIndexer API, never raw chromadb.PersistentClient.\n"
                    f"   See: .workbuddy/memory/KB-DEFENSE-DESIGN.md"
                )
        return self._collection

    # ── 索引构建 ──────────────────────────────────────────

    def index_wiki(
        self,
        batch_size: int = 10,
        force_rebuild: bool = False,
    ) -> int:
        """
        扫描 wiki_dir 中的所有 .md 文件，向量化并存入 ChromaDB。

        参数：
          batch_size — 每批提交数量（默认 10，大模型如 bge-m3 用小批次防内存泄漏）
          force_rebuild — True 时先清空现有索引重新构建

        返回：索引的文档块总数
        """
        if force_rebuild:
            try:
                self.client.delete_collection(self.collection_name)
                self._collection = None
            except Exception:
                pass

        md_files = [
            f for f in self.wiki_dir.rglob("*.md")
            if not any(p.startswith("log/") for p in f.relative_to(self.wiki_dir).parts)
            and f.name != "index.md"
        ]

        ids_to_index = []
        docs_to_index = []
        metadatas = []

        for f in md_files:
            content = self._read_md(f)
            if not content.strip():
                continue

            doc_id = self._file_id(f)
            chunks = self._chunk_content(content)

            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_c{i}"
                ids_to_index.append(chunk_id)
                docs_to_index.append(chunk)
                metadatas.append({
                    "source": str(f.relative_to(self.wiki_dir)),
                    "title": self._extract_title(f, content),
                    "word_count": len(chunk),
                })

        total = 0
        for i in range(0, len(ids_to_index), batch_size):
            self.collection.upsert(
                ids=ids_to_index[i : i + batch_size],
                documents=docs_to_index[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )
            total += len(ids_to_index[i : i + batch_size])
            gc.collect()  # 防止大模型（如 bge-m3）嵌入时内存累积泄漏

        self.documents = docs_to_index
        print(
            f"[WikiIndexer] 索引完成：{total} 个文本块，"
            f"来自 {len(md_files)} 个文件（模型：{self.embedding_model}）",
            flush=True,
            file=sys.stderr,
        )
        # D-02: 写入后自动校验一致性
        self._validate_consistency()
        return total

    def index_wiki_batched(self, precompute_batch: int = 200, collection=None) -> int:
        """
        D-03: 高效全量索引 — 大模型专用（bge-m3 等）。
        
        与 index_wiki() 的区别：
        - index_wiki(): 逐批 upsert → HNSW 索引每批重建 → 随规模指数变慢
        - index_wiki_batched(): 预计算所有嵌入 → 一次性 add → 线性耗时
        
        适用场景：bge-m3（567M参数/1024维）等大模型重建。
        小模型（minilm/bge-small）用 index_wiki() 即可。
        
        Agent 须知：任何需要重建 bge-m3 索引的任务，直接调用此方法。
        禁止绕过 WikiIndexer 使用裸 ChromaDB client + 手动 encode。
        参见：MEMORY.md 踩坑 #32, KB-DEFENSE-DESIGN.md
        
        参数：
          collection: 可选，指定目标 collection（用于原子重建等场景）
                       如果为 None，使用 self.collection（默认行为）
        """
        if self._embedding_function is None:
            raise RuntimeError("index_wiki_batched() requires _warmup_model() first")
        
        # 确定目标 collection
        if collection is None:
            collection = self.collection  # 原有逻辑（会触发名称断言）
        # 如果传入了 collection，直接使用（跳过名称断言）

        md_files = [
            f for f in self.wiki_dir.rglob("*.md")
            if not any(p.startswith("log/") for p in f.relative_to(self.wiki_dir).parts)
            and f.name != "index.md"
        ]

        ids_to_index = []
        docs_to_index = []
        metadatas = []

        for f in md_files:
            content = self._read_md(f)
            if not content.strip():
                continue
            doc_id = self._file_id(f)
            chunks = self._chunk_content(content)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_c{i}"
                ids_to_index.append(chunk_id)
                docs_to_index.append(chunk)
                metadatas.append({
                    "source": str(f.relative_to(self.wiki_dir)),
                    "title": self._extract_title(f, content),
                    "word_count": len(chunk),
                })

        total_chunks = len(ids_to_index)
        print(
            f"[WikiIndexer:batched] 准备索引 {total_chunks} 个文本块，"
            f"来自 {len(md_files)} 个文件",
            flush=True, file=sys.stderr,
        )

        # Phase 1: 分批预计算嵌入（CPU 密集型，防止 OOM）
        import time
        all_embeddings = []
        t0 = time.time()
        for i in range(0, total_chunks, precompute_batch):
            batch = docs_to_index[i:i + precompute_batch]
            batch_emb = self._embedding_function(batch)
            if hasattr(batch_emb, 'tolist'):
                batch_emb = batch_emb.tolist()
            all_embeddings.extend(batch_emb)
            elapsed = time.time() - t0
            progress = min(i + precompute_batch, total_chunks)
            print(
                f"[WikiIndexer:batched] 编码进度: {progress}/{total_chunks} "
                f"({progress*100/total_chunks:.1f}%, {elapsed:.0f}s)",
                flush=True, file=sys.stderr,
            )
            gc.collect()

        encode_time = time.time() - t0
        print(
            f"[WikiIndexer:batched] 编码完成: {total_chunks} 条, "
            f"{encode_time:.0f}s ({encode_time/60:.1f}min)",
            flush=True, file=sys.stderr,
        )

        # Phase 2: 一次性写入（避免 upsert 的 HNSW 逐批重建）
        t0 = time.time()
        collection.add(
            ids=ids_to_index,
            documents=docs_to_index,
            embeddings=all_embeddings,
            metadatas=metadatas,
        )
        write_time = time.time() - t0
        print(
            f"[WikiIndexer:batched] 写入完成: {total_chunks} 条, "
            f"{write_time:.1f}s",
            flush=True, file=sys.stderr,
        )

        self.documents = docs_to_index
        # D-02: 写入后自动校验一致性（仅当使用默认 collection 时）
        if collection is None:
            # 使用默认 collection，执行完整校验
            self._validate_consistency()
        else:
            # 使用外部传入的 collection（如影子集合），跳过名称检查
            col_count = collection.count()
            doc_count = len(self.documents)
            if doc_count > 0 and col_count == 0:
                raise RuntimeError(
                    f"🔴 Consistency check FAILED: collection is empty!\n"
                    f"   Expected {doc_count} documents, but collection.count() = {col_count}\n"
                    f"   This means the write operation did not persist.\n"
                    f"   Check ChromaDB path and permissions."
                )
            print(
                f"[WikiIndexer] ✅ 影子集合写入成功: {col_count} 文档, "
                f"collection='{collection.name}'",
                flush=True, file=sys.stderr,
            )
        return total_chunks

    def _validate_consistency(self) -> bool:
        """
        D-02: 写入后一致性校验。

        检查：
        1. collection 存在且有数据
        2. collection 名称匹配期望值

        若发现不一致，抛出 RuntimeError 阻止继续运行。
        Agent 无需手动调用 — index_wiki() / index_wiki_batched() 自动调用。
        """
        # 名称断言（复用 collection property 中的逻辑）
        col = self.collection
        actual_name = col.name
        if actual_name != self.collection_name:
            raise RuntimeError(
                f"🔴 Consistency check FAILED: name mismatch\n"
                f"   Expected: '{self.collection_name}'\n"
                f"   Actual:   '{actual_name}'"
            )

        col_count = col.count()
        doc_count = len(self.documents)
        if doc_count > 0 and col_count == 0:
            raise RuntimeError(
                f"🔴 Consistency check FAILED: collection is empty!\n"
                f"   Expected {doc_count} documents, but collection.count() = {col_count}\n"
                f"   This means the write operation did not persist.\n"
                f"   Check ChromaDB path and permissions."
            )

        print(
            f"[WikiIndexer] ✅ 一致性校验通过: {col_count} 文档, "
            f"collection='{actual_name}'",
            flush=True, file=sys.stderr,
        )
        return True

    # ── 增量索引 (P0.1) ──────────────────────────────────

    def index_wiki_incremental(self) -> dict:
        """
        P0.1 增量索引：只处理 wiki/ 中新增或删除的 .md 文件。

        判断依据：source 路径是否在 collection 中。
        - 新文件：source 不在 collection 中 → index
        - 文件删除：source 在但磁盘文件已不存在 → 删旧 chunks
        - 文件未改：跳过

        Returns:
            {"indexed_files": int, "indexed_chunks": int,
             "deleted_files": int, "skipped_files": int}
        """
        import hashlib

        # 1. 获取已索引的文件 → chunk_ids 映射
        existing = {}  # source → list of chunk ids
        result = self.collection.get(include=["metadatas"])
        if result["ids"]:
            for i, meta in enumerate(result["metadatas"]):
                source = meta.get("source", "")
                if source:
                    if source not in existing:
                        existing[source] = []
                    existing[source].append(result["ids"][i])

        # 2. 计算当前 wiki 文件列表
        all_md = [
            f for f in self.wiki_dir.rglob("*.md")
            if not any(p.startswith("log/") for p in f.relative_to(self.wiki_dir).parts)
            and f.name != "index.md"
        ]

        current_sources = set()
        new_ids = []
        new_docs = []
        new_metas = []
        indexed_files = 0
        skipped_files = 0

        for f in all_md:
            content = self._read_md(f)
            if not content.strip():
                continue
            rel = str(f.relative_to(self.wiki_dir))
            current_sources.add(rel)

            if rel not in existing:
                # 新文件 → 索引
                chunks = self._chunk_content(content)
                doc_id = self._file_id(f)
                for i, chunk in enumerate(chunks):
                    new_ids.append(f"{doc_id}_c{i}")
                    new_docs.append(chunk)
                    new_metas.append({
                        "source": rel,
                        "title": self._extract_title(f, content),
                        "word_count": len(chunk),
                    })
                indexed_files += 1
            else:
                skipped_files += 1

        # 3. 找到被删除的文件
        deleted_ids = []
        deleted_files = 0
        for rel in existing:
            if rel not in current_sources:
                deleted_ids.extend(existing[rel])
                deleted_files += 1

        # 4. 执行写入
        if deleted_ids:
            self.collection.delete(ids=deleted_ids)
            print(
                f"[WikiIndexer:incremental] 删除 {deleted_files} 个文件的 "
                f"{len(deleted_ids)} 个块",
                flush=True, file=sys.stderr,
            )

        if new_ids:
            self.collection.add(
                ids=new_ids,
                documents=new_docs,
                metadatas=new_metas,
            )
            print(
                f"[WikiIndexer:incremental] 新增 {indexed_files} 个文件, "
                f"{len(new_ids)} 个块",
                flush=True, file=sys.stderr,
            )

        self._validate_consistency()
        return {
            "indexed_files": indexed_files,
            "indexed_chunks": len(new_ids),
            "deleted_files": deleted_files,
            "skipped_files": skipped_files,
        }

    # ── 原子重建 (P0.2) ──────────────────────────────────

    def rebuild_atomic(self) -> int:
        """
        P0.2 原子重建：影子 collection → 写入 → 验证 → 切换。

        任何阶段崩溃：
        - 旧 collection 不变（正在使用中）
        - 影子 collection 残留（下次重建时清理）

        返回：重建的文档块总数
        """
        import time
        t0 = time.time()

        shadow_name = f"{self.collection_name}_shadow_{int(time.time())}"

        # Phase 1: 创建影子 collection
        try:
            self.client.delete_collection(shadow_name)
        except Exception:
            pass

        shadow_col = self.client.create_collection(
            name=shadow_name,
            embedding_function=self._embedding_function,
            metadata={"description": f"shadow for {self.collection_name}"},
        )

        # Phase 2: 在影子中构建（传入 shadow_col）
        try:
            count = self.index_wiki_batched(precompute_batch=200, collection=shadow_col)
            # Phase 3: 验证影子数据
            if shadow_col.count() < 10:
                raise RuntimeError(
                    f"Shadow collection too small: {shadow_col.count()} chunks. "
                    f"Expected at least 10."
                )
            elapsed = time.time() - t0
            print(
                f"[WikiIndexer:atomic] 影子构建完成: {count} 块 "
                f"({elapsed:.1f}s)",
                flush=True, file=sys.stderr,
            )
        except Exception as e:
            # 失败 → 删除影子，保留原 collection
            try:
                self.client.delete_collection(shadow_name)
            except Exception:
                pass
            raise RuntimeError(
                f"Atomic rebuild failed, original data preserved: {e}"
            )

        # Phase 4: 原子切换 — 从影子读数据，写入新 collection

        # 4a. 删除旧 collection（如果存在）
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

        # 4b. 创建新的正式 collection
        self._collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_function,
        )

        # 4c. 从影子迁移数据到新 collection
        shadow_data = shadow_col.get(
            include=["documents", "metadatas", "embeddings"]
        )
        if shadow_data["ids"]:
            self._collection.add(
                ids=shadow_data["ids"],
                documents=shadow_data["documents"],
                metadatas=shadow_data["metadatas"],
                embeddings=shadow_data["embeddings"],
            )
            print(
                f"[WikiIndexer:atomic] 数据迁移完成: "
                f"{len(shadow_data['ids'])} 块",
                flush=True, file=sys.stderr,
            )

        # Phase 5: 清理影子
        try:
            self.client.delete_collection(shadow_name)
            print(
                f"[WikiIndexer:atomic] 影子已清理: {shadow_name}",
                flush=True, file=sys.stderr,
            )
        except Exception:
            pass

        total = time.time() - t0
        final_count = self._collection.count()
        print(
            f"[WikiIndexer:atomic] ✅ 原子重建完成: "
            f"{final_count} 块 ({total:.1f}s)",
            flush=True, file=sys.stderr,
        )

        self._validate_consistency()
        return final_count

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_source: Optional[str] = None,
    ) -> list[dict]:
        """
        语义相似度搜索。

        参数：
          query — 查询文本
          top_k — 返回数量
          filter_source — 限定来源目录（如 "概念/"）

        返回：[{text, distance, metadata}, ...]
        """
        where = None
        if filter_source:
            where = {"source": {"$contains": filter_source}}

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                hits.append({
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                })
        return hits

    # ── 内部工具 ──────────────────────────────────────────

    @staticmethod
    def _read_md(path: Path) -> str:
        """读取 markdown 文件，清理 YAML frontmatter"""
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="gbk")
            except Exception:
                return ""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                text = parts[2]
        return text.strip()

    @staticmethod
    def _file_id(path: Path) -> str:
        return hashlib.md5(str(path).encode()).hexdigest()[:16]

    @staticmethod
    def _extract_title(path: Path, content: str) -> str:
        name = path.stem
        if name not in ("", "index"):
            return name
        m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return m.group(1).strip() if m else (name or "无标题")

    @staticmethod
    def _chunk_content(content: str, chunk_size: int = 500) -> list[str]:
        """按 markdown 标题分块，块大小约 chunk_size，重叠 50 字"""
        paragraphs = re.split(r"\n(?=##?\s)", content)
        chunks, current, overlap = [], "", 50
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) <= chunk_size:
                current += "\n" + para
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = (current[-overlap:] if current else "") + "\n" + para
        if current.strip():
            chunks.append(current.strip())
        return chunks or [content[:chunk_size]]


# ═════════════════════════════════════════════════════
# 命令行入口（用于测试）
# ═════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Wiki 索引工具")
    parser.add_argument(
        "--model",
        choices=list(SUPPORTED_MODELS.keys()),
        default="minilm",
        help="嵌入模型（minilm=快，bge-m3=质量高）",
    )
    parser.add_argument("--rebuild", action="store_true", help="强制重建索引")
    args = parser.parse_args()

    indexer = WikiIndexer(embedding_model=args.model)
    print(f"使用模型：{args.model}（{SUPPORTED_MODELS[args.model]['description']}）")
    count = indexer.index_wiki(force_rebuild=args.rebuild)
    print(f"完成！共索引 {count} 个文本块。")
