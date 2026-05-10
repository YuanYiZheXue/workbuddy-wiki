"""
KnowledgeGraph — GraphRAG 推理层（networkx 版）
=====================================================
从 wiki 内容构建知识图谱，支持：
  - 实体提取（中文概念词 + wiki 标题 + NER 可选）
  - 关系推理（wikilink / 语义相似 / 共现 / NER 关系）
  - 多跳查询（"A 如何影响 B"）
  - 社区发现（Louvain 算法）

依赖：
  - networkx 3.0+（图操作）
  - python-louvain（社区发现，可选）
  - transformers（NER 模型模式，可选）

用法：
  kg = KnowledgeGraph()
  kg.build_from_wiki(Path("d:\\Obsidian_KN\\philosophy\\wiki"))
  result = kg.query("柔弱胜刚强 与 不敢为天下先 有什么关系？")
"""

import re
import json
import sys
import math
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from collections import defaultdict

import networkx as nx

# 尝试导入 Louvain 社区发现
try:
    from community import best_partition

    _HAVE_LOUVAIN = True
except ImportError:
    _HAVE_LOUVAIN = False

# 尝试导入 NER 提取器
try:
    from ner_extractor import NERExtractor

    _HAVE_NER = True
except ImportError:
    _HAVE_NER = False
    print(
        "[KnowledgeGraph] ⚠️ NER 模块 (ner_extractor) 导入失败，"
        "NER 功能将不可用。如需 NER，请确保 ner_extractor.py 存在且无依赖缺失。",
        flush=True, file=sys.stderr,
    )

# ════════════════════════════════════════════════════════
# 关系类型
# ════════════════════════════════════════════════════════

RELATION_TYPES = [
    "因果",  # A 导致 B
    "对立",  # A 与 B 对立
    "包含",  # A 包含 B / A 体现 B
    "相关",  # A 与 B 相关（弱关联）
    "传承",  # A 传承 B
    "对比",  # A 对比 B
    "引用",  # A 引用 B
]

# ════════════════════════════════════════════════════════
# 实体 & 关系提取器
# ════════════════════════════════════════════════════════


class EntityExtractor:
    """
    从 markdown 文本中提取实体和关系。

    实体来源：
      1. Wiki 内链 [[目标]] — 高置信度关系
      2. ## / ### 标题 — 独立概念
      3. NER 模型（可选，需 transformers）
      4. 常用模式匹配 — 因果/对立/对比句式

    关系来源：
      1. [[A|B]] / [[A]] 内链 — "A 引用 B"
      2. 因果句式：A 导致 B / A 使得 B / A 促使 B
      3. 对立句式：A 与 B 相反 / A 而非 B
      4. 包含句式：A 是 B / A 体现 B / A 包含 B
      5. 共现：同一段落中出现的两个概念 → "相关"
    """

    # 关系句式模板（中文 NLP，无需模型）
    # P1 增强 (2026-05-08)：补充哲学文本和工程文档中高频句式
    REL_PATTERNS: list[tuple[str, str, str]] = [
        # 因果（原 + P1 补充）
        (r"(.+?)导致(.+?)", "因果", "导致"),
        (r"(.+?)使得(.+?)", "因果", "使"),
        (r"(.+?)促使(.+?)", "因果", "促"),
        (r"(.+?)造成(.+?)", "因果", "致"),
        (r"(.+?)从而(.+?)", "因果", "从"),
        (r"(.+?)因此(.+?)", "因果", "因"),
        (r"(.+?)由(.+?)产生", "因果", "生"),
        (r"(.+?)源于(.+?)", "因果", "源"),          # P1: 哲学常用
        (r"(.+?)根植于(.+?)", "因果", "根"),         # P1: 哲学/技术
        (r"(.+?)催生了(.+?)", "因果", "催"),         # P1: 技术演化
        (r"(.+?)推动了(.+?)", "因果", "推"),         # P1: 影响/推动
        # 对立
        (r"(.+?)与(.+?)相反", "对立", "反"),
        (r"(.+?)而非(.+?)", "对立", "非"),
        (r"(.+?)区别于(.+?)", "对立", "别"),
        (r"(.+?)不是(.+?)", "对立", "非"),
        (r"(.+?)强(.+?)弱", "对立", "强弱"),
        (r"(.+?)与(.+?)对立", "对立", "立"),         # P1: 显式对立
        (r"(.+?)与(.+?)矛盾", "对立", "盾"),         # P1: 矛盾关系
        # 包含（原 + P1 补充）
        (r"(.+?)是(.+?)的体现", "包含", "体现"),
        (r"(.+?)体现了(.+?)", "包含", "体现"),
        (r"(.+?)属于(.+?)", "包含", "属"),
        (r"(.+?)归于(.+?)", "包含", "归"),
        (r"(.+?)是(.+?)的一种", "包含", "种"),       # P1: IS-A 关系
        (r"(.+?)是(.+?)之一", "包含", "之一"),       # P1: 子集关系
        (r"(.+?)包括(.+?)", "包含", "括"),           # P1: 正向包含
        (r"(.+?)蕴含(.+?)", "包含", "蕴"),           # P1: 逻辑蕴含
        # 传承/对比/类比（原 + P1 补充）
        (r"(.+?)传承(.+?)", "传承", "承"),
        (r"(.+?)与(.+?)对比", "对比", "比"),
        (r"(.+?)相比(.+?)", "对比", "比"),
        (r"(.+?)类似于(.+?)", "类比", "似"),         # P1 新增类型：类比
        (r"(.+?)犹如(.+?)", "类比", "犹"),           # P1
        (r"(.+?)借鉴(.+?)", "传承", "鉴"),           # P1: 借鉴/继承变体
        (r"(.+?)基于(.+?)", "传承", "基"),           # P1: 基于（技术栈依赖）
        (r"(.+?)依赖(.+?)", "依赖", "赖"),           # P1 新增类型：依赖
    ]

    # 内链正则
    WIKI_LINK_RE = re.compile(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]")
    HEADING_RE = re.compile(r"^(?:#{1,3})\s+(.+)$", re.MULTILINE)
    ENTITY_CHAR_RE = re.compile(r"[\u4e00-\u9fff]{2,5}")  # 2-5 字中文词

    # P0 fix: 噪声节点黑名单 — 模板残留 / 元标记 / QA段落头 被误当实体提取
    # 来源：2026-05-08 全量heading审计（grep wiki/ 概念/ 下所有 ##/### 统计）
    NOISE_HEADINGS: frozenset[str] = frozenset({
        # ── Wiki 模板段落头（workbuddy-wiki-schema 标准字段）──
        "关联概念", "相关概念", "相关链接", "相关页面", "相关实体",
        "来源", "来源路径",
        # ── QA 模板段落头（QA_TEMPLATE 标准字段）──
        "问题", "回答",
        # ── 元标记（TODO/状态标记，非实体概念）──
        "待深化", "待补充",
        # ── ADR / 工程文档残留（元信息段落头）──
        "修复", "记录", "根因", "测试用例",
        # ── 用户标注风格头（元一笔记体系标注，非知识实体）──
        "元一笔记", "用户原创洞察", "用户的哲学贡献",
        "用户理解", "用户提问", "核心洞察（用户贡献）",
    })

    # 文件名级噪声（非概念的 .md 文件名）
    NOISE_FILENAMES: frozenset[str] = frozenset({
        "index", "待补充", "模板", "template",
    })

    # P2-B: 同义词别名映射（合并近义实体，减少碎片节点）
    # 格式：{规范名: [别名列表]}  — 构建时将别名重定向到规范名
    SYNONYM_ALIASES: dict[str, list[str]] = {
        "道德经": ["老子", "道德经思想", "德道经"],
        "GraphRAG": ["graphrag", "Graph RAG"],
        "MCP协议": ["MCP", "Model Context Protocol"],
        "ChromaDB": ["chromadb", "chroma"],
        "networkx": ["NetworkX", "nx"],
        "香农信息论": ["信息论", "通信的数学理论", "香农理论"],
        "元一思想": ["元一", "四原则"],
    }

    @classmethod
    def is_noise(cls, name: str) -> bool:
        """判断名称是否为噪声节点（模板残留/元标记/非实体）。

        P0 设计决策（2026-05-08）：
          - 单字中文概念（如「道」「德」「气」「仁」）是合法实体 → 不过滤
          - 只有非中文的单字符（标点/符号/空串）才视为噪声
        """
        stripped = name.strip()
        if stripped in cls.NOISE_HEADINGS:
            return True
        if stripped in cls.NOISE_FILENAMES:
            return True
        # P1.1 补充：过滤测试文档（名称含 test/测试）
        if re.search(r'test|测试', stripped, re.I):
            return True
        # 空串 → 噪声
        if len(stripped) == 0:
            return True
        # 单字符：仅非中文且非英文字母的算噪声
        # 保护：单字中文概念（道/德/气/仁）、单字母测试实体（A/B/X）
        if len(stripped) == 1:
            if '\u4e00' <= stripped <= '\u9fff':
                return False  # 中文概念
            if stripped.isalpha():
                return False  # 英文字母
            return True   # 标点/符号/数字
        return False

    def __init__(self, use_ner: bool = False, ner_model_mode: str = "dict"):
        self._known_entities: set[str] = set()
        self.use_ner = use_ner and _HAVE_NER
        if self.use_ner:
            use_model = (ner_model_mode == "model")
            self._ner = NERExtractor(use_model=use_model)
            if use_model:
                print("[KnowledgeGraph] NER 模式：BERT 模型（首次推理需 ~3s 加载）",
                      flush=True, file=sys.stderr)
            else:
                print("[KnowledgeGraph] NER 模式：词典（零依赖，快速）",
                      flush=True, file=sys.stderr)

    def set_known_entities(self, names: set[str]):
        """预先注入已知概念名（如 wiki 目录名、文件名）"""
        self._known_entities = names

    def extract_from_file(
        self, path: Path, content: str
    ) -> tuple[list[dict], list[dict]]:
        """
        从单个文件提取实体和关系。

        返回：(nodes, edges)
          nodes: [{id, name, aliases, content}]
          edges: [{src, rel, tgt, weight, context}]
        """
        nodes_dict: dict[str, dict] = {}
        edges: list[dict] = []
        paragraphs = content.split("\n\n")

        # P1-B: 解析 frontmatter tags（用于后续同标签关系推断）
        entity_tags: list[str] = self._extract_frontmatter_tags(content)

        # 1. 从文件名提取实体名（P0: 过滤噪声文件名）
        entity_name = path.stem
        if entity_name not in ("", "index") and not self.is_noise(entity_name):
            nodes_dict[entity_name] = {
                "id": self._node_id(entity_name),
                "name": entity_name,
                "aliases": [],
                "content": content[:200],
                "tags": entity_tags,  # P1-B: 挂载标签
            }

        # 2. 从 wikilink 提取引用关系（P0: 过滤噪声目标）
        for link_target in self.WIKI_LINK_RE.findall(content):
            link_target = link_target.strip()
            if link_target == entity_name:
                continue
            if self.is_noise(link_target):
                continue
            if link_target not in nodes_dict:
                nodes_dict[link_target] = {
                    "id": self._node_id(link_target),
                    "name": link_target,
                    "aliases": [],
                    "content": "",
                }
            edges.append({
                "src": entity_name,
                "rel": "引用",
                "tgt": link_target,
                "weight": 0.8,
                "context": f"文件中引用：{link_target}",
            })

        # 3. 从标题提取子概念（P0: 过滤模板残留噪声标题）
        for heading in self.HEADING_RE.findall(content):
            heading = heading.strip()
            # 去掉 "#" 后缀编号
            heading = re.sub(r"\s*#+$", "", heading)
            if len(heading) >= 2 and heading != entity_name and not self.is_noise(heading):
                if heading not in nodes_dict:
                    nodes_dict[heading] = {
                        "id": self._node_id(heading),
                        "name": heading,
                        "aliases": [],
                        "content": "",
                    }
                # 同一文件内的标题层级关系
                edges.append({
                    "src": entity_name,
                    "rel": "包含",
                    "tgt": heading,
                    "weight": 0.5,
                    "context": "同文件子概念",
                })

        # 4. NER 实体提取（可选，P0: 过滤噪声）
        if self.use_ner:
            ner_entities = self._ner.extract(content)
            for ent_text, ent_type in ner_entities:
                if ent_text not in nodes_dict and len(ent_text) >= 2 and not self.is_noise(ent_text):
                    nodes_dict[ent_text] = {
                        "id": self._node_id(ent_text),
                        "name": ent_text,
                        "aliases": [],
                        "content": "",
                        "type": ent_type,
                    }

        # 5. 从句式提取关系
        for para in paragraphs:
            para = para.strip()
            if len(para) < 5:
                continue
            self._extract_relation_patterns(para, edges, nodes_dict)

        # 6. 共现关系（同一段落中出现的多个已知概念）
        self._extract_cooccurrence(paragraphs, nodes_dict, edges)

        return list(nodes_dict.values()), edges

    def _extract_relation_patterns(
        self, para: str, edges: list[dict], nodes_dict: dict
    ):
        for pattern_str, rel_type, rel_name in self.REL_PATTERNS:
            for m in re.finditer(pattern_str, para):
                groups = m.groups()
                if len(groups) >= 2:
                    a, b = groups[0].strip(), groups[1].strip()
                    # 过滤太短或太长的实体
                    if len(a) < 2 or len(b) < 2:
                        continue
                    if len(a) > 20 or len(b) > 20:
                        continue
                    # P0: 过滤噪声实体
                    if self.is_noise(a) or self.is_noise(b):
                        continue
                    for entity_name in (a, b):
                        if entity_name not in nodes_dict:
                            nodes_dict[entity_name] = {
                                "id": self._node_id(entity_name),
                                "name": entity_name,
                                "aliases": [],
                                "content": "",
                            }
                    # 避免重复边
                    edge_exists = any(
                        e["src"] == a and e["rel"] == rel_type and e["tgt"] == b
                        for e in edges
                    )
                    if not edge_exists:
                        edges.append({
                            "src": a,
                            "rel": rel_type,
                            "tgt": b,
                            "weight": 0.6,
                            "context": para[:80],
                        })

    def _extract_cooccurrence(
        self, paragraphs: list[str], nodes_dict: dict, edges: list[dict]
    ):
        """同一段落中出现的多个已知实体 → 相关关系。

        P2-A 增强（2026-05-08）：增加单节点共现度上限，
        防止高频词（如「道德经」）产生过多弱相关边。
        """
        all_entity_names = list(nodes_dict.keys())
        # P2: 跟踪每个节点的共现边数，超过上限则停止新增
        coocc_count: dict[str, int] = defaultdict(int)
        MAX_COOCC_PER_NODE = 50  # P2.1 提升上限：单节点最大共现邻居数（原15）

        for para in paragraphs:
            found = [
                name for name in all_entity_names
                if name in para and len(name) >= 2
            ]
            if len(found) < 2:
                continue
            for i, a in enumerate(found):
                for b in found[i + 1 :]:
                    # P2-A: 度数检查
                    if coocc_count.get(a, 0) >= MAX_COOCC_PER_NODE:
                        continue
                    if coocc_count.get(b, 0) >= MAX_COOCC_PER_NODE:
                        continue
                    edge_exists = any(
                        (e["src"] == a and e["tgt"] == b)
                        or (e["src"] == b and e["tgt"] == a)
                        for e in edges
                    )
                    if not edge_exists:
                        edges.append({
                            "src": a,
                            "rel": "相关",
                            "tgt": b,
                            "weight": 0.3,
                            "context": "同段共现",
                        })
                        coocc_count[a] += 1
                        coocc_count[b] += 1

    # P1-B: Frontmatter tags 解析
    _FM_RE = re.compile(r'^---\s*\n(.+?)\n---\s*\n', re.DOTALL | re.MULTILINE)
    _TAGS_RE = re.compile(r'^tags:\s*\[(.+?)\]', re.MULTILINE)

    @classmethod
    def _extract_frontmatter_tags(cls, content: str) -> list[str]:
        """从 wiki 内容的 YAML frontmatter 中提取 tags 列表。"""
        fm_match = cls._FM_RE.match(content)
        if not fm_match:
            return []
        fm_text = fm_match.group(1)
        tag_match = cls._TAGS_RE.search(fm_text)
        if not tag_match:
            return []
        try:
            # 解析 ["tag1", "tag2", ...] 格式
            raw = tag_match.group(1)
            import ast
            tags = ast.literal_eval(f'[{raw}]')
            if isinstance(tags, list):
                return [t.strip().strip('"') for t in tags if isinstance(t, str)]
        except (ValueError, SyntaxError):
            # 降级：简单分割
            raw = tag_match.group(1)
            tags = [t.strip().strip('"').strip("'") for t in raw.split(",")]
            return [t for t in tags if t]
        return []

    @staticmethod
    def _node_id(name: str) -> str:
        return hashlib.md5(name.encode()).hexdigest()[:12]


# ════════════════════════════════════════════════════════
# KnowledgeGraph — 核心类（networkx 版）
# ════════════════════════════════════════════════════════

class KnowledgeGraph:
    """
    从 wiki 构建知识图谱，支持多跳推理和社区发现。

    内部结构（networkx 版）：
      self.G: nx.DiGraph  — 有向图（存储节点 + 边）
      self.communities: list[list[str]] — 社区列表
      self._nodes_by_name: dict[str, str] — 节点名 → 节点 ID
    """

    def __init__(self):
        self.G = nx.DiGraph()
        self.communities: list[list[str]] = []
        self._nodes_by_name: Optional[dict] = None
        self._use_ner = False

    @property
    def node_count(self) -> int:
        return self.G.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self.G.number_of_edges()

    # ── 构建 ──────────────────────────────────────────────

    def build_from_wiki(self, wiki_dir: Path, *, force: bool = False, use_ner: bool = False):
        """
        从 wiki 目录构建完整知识图谱。

        流程：
          1. 扫描所有 .md 文件
          2. 对每个文件提取实体 + 关系
          3. 合并全局图谱
          4. 执行社区发现（Louvain 或 Label Propagation）

        参数：
          use_ner — 是否使用 NER 模型提取实体（需要 transformers）
        """
        if not force and self.node_count > 0:
            print("[KnowledgeGraph] 已有图谱，跳过构建（force=True 强制重建）",
                  flush=True, file=sys.stderr)
            return

        self.G.clear()
        self.communities.clear()
        self._nodes_by_name = None
        self._use_ner = use_ner

        # 读取 NER 模式配置
        _ner_mode = "dict"
        try:
            from kb_config import NER_MODEL_MODE as _ner_mode
        except ImportError:
            pass

        # 预收集所有已知概念名（文件名）
        extractor = EntityExtractor(use_ner=use_ner, ner_model_mode=_ner_mode)
        known = set()
        for f in wiki_dir.rglob("*.md"):
            if f.name != "index.md" and not any(
                p.startswith("log/") for p in f.relative_to(wiki_dir).parts
            ):
                known.add(f.stem)
        extractor.set_known_entities(known)

        # P2.1: 文档级共现跟踪
        from collections import defaultdict
        doc_entities = defaultdict(set)   # file_path → 实体名集合
        entity_tags = defaultdict(set)   # 实体名 → 标签集合

        file_count = 0
        for f in wiki_dir.rglob("*.md"):
            if f.name == "index.md":
                continue
            if any(p.startswith("log/") for p in f.relative_to(wiki_dir).parts):
                continue

            try:
                content = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    content = f.read_text(encoding="gbk")
                except Exception:
                    continue

            nodes, edges = extractor.extract_from_file(f, content)

            # P2.1: 跟踪文档级共现和标签
            for node in nodes:
                doc_entities[f].add(node["name"])
                if node.get("tags"):
                    for tag in node["tags"]:
                        entity_tags[node["name"]].add(tag)

            # 添加节点（含属性）
            for node in nodes:
                node_id = node["id"]
                if not self.G.has_node(node_id):
                    self.G.add_node(node_id, **node)
                elif node.get("content"):
                    # 补充 content 和 tags（P1 fix: wikilink先创建的空节点需补充tags）
                    self.G.nodes[node_id]["content"] = node["content"]
                    if node.get("tags"):
                        self.G.nodes[node_id]["tags"] = node["tags"]

            # B10 fix: 使 _name_to_id() 的惰性缓存 nodes_by_name 失效，
            # 否则首次构建后不再更新，后续文件的节点名全部无法解析 → 边静默丢弃
            self._nodes_by_name = None

            # 添加边
            for e in edges:
                src_id = self._name_to_id(e["src"])
                tgt_id = self._name_to_id(e["tgt"])
                if src_id and tgt_id:
                    self.G.add_edge(
                        src_id,
                        tgt_id,
                        rel=e["rel"],
                        weight=e.get("weight", 1.0),
                        context=e.get("context", ""),
                    )

            file_count += 1

        # ════════════════════════════════════════════
        # P1 后处理：增强边语义
        # ════════════════════════════════════════════
        self._infer_tag_relations()      # P1-B: 同标签关联
        self._infer_directory_hierarchy(wiki_dir)  # P1-B: 目录层次

        # ════════════════════════════════════════════
        # P2 后处理：图密度增强
        # ════════════════════════════════════════════
        self._merge_synonym_aliases()   # P2-B: 别名合并
        self._infer_bridge_edges()      # P2-C: 二跳桥接

        # ══════════════════════════════════════
        # P2.1: 文档级共现 + 标签共现
        # ══════════════════════════════════════
        # 文档级共现（同一文档出现的概念 → 相关边）
        print("[KnowledgeGraph] P2.1: 文档级共现边...", flush=True, file=sys.stderr)
        doc_coocc = defaultdict(int)
        for doc_path, entities in doc_entities.items():
            entities = list(entities)
            for i, a in enumerate(entities):
                for b in entities[i+1:]:
                    key = tuple(sorted([a, b]))
                    doc_coocc[key] += 1

        added = 0
        for (a, b), count in doc_coocc.items():
            if count < 2:  # 至少共同出现在 2 个位置
                continue
            a_id = self._name_to_id(a)
            b_id = self._name_to_id(b)
            if a_id and b_id and not self.G.has_edge(a_id, b_id):
                self.G.add_edge(a_id, b_id, rel="相关", weight=0.2, context=f"文档共现({count})")
                added += 1
        print(f"[KnowledgeGraph] P2.1: 文档级共现新增 {added} 条边", flush=True, file=sys.stderr)

        # 标签共现（共享标签的概念 → 相关边）
        print("[KnowledgeGraph] P2.1: 标签共现边...", flush=True, file=sys.stderr)
        tag_entities = defaultdict(set)
        for entity, tags in entity_tags.items():
            for tag in tags:
                tag_entities[tag].add(entity)

        added = 0
        for tag, entities in tag_entities.items():
            entities = list(entities)
            for i, a in enumerate(entities):
                for b in entities[i+1:]:
                    a_id = self._name_to_id(a)
                    b_id = self._name_to_id(b)
                    if a_id and b_id and not self.G.has_edge(a_id, b_id):
                        self.G.add_edge(a_id, b_id, rel="相关", weight=0.4, context=f"共享标签:{tag}")
                        added += 1
        print(f"[KnowledgeGraph] P2.1: 标签共现新增 {added} 条边", flush=True, file=sys.stderr)

        # 社区发现
        self._detect_communities()

        print(
            f"[KnowledgeGraph] 构建完成：{self.node_count} 个节点，"
            f"{self.edge_count} 条边，{len(self.communities)} 个概念群落",
            flush=True, file=sys.stderr,
        )

    # ── 查询 ──────────────────────────────────────────────

    def query(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        知识图谱查询。

        分析问题类型，返回对应推理结果：
          - 直连关系（1-hop）
          - 传导路径（n-hop）
          - 社区归属

        返回结构：
          {
            "paths": [...],        # 关系路径
            "communities": [...], # 涉及的概念群落
            "node_count": N,
            "edge_count": N,
          }
        """
        # 1. 提取问题中的关键概念
        concepts = self._extract_concepts_from_text(question)
        if not concepts:
            return {
                "paths": [],
                "communities": [],
                "node_count": self.node_count,
                "edge_count": self.edge_count,
            }

        # 2. 在图中找到这些概念的节点
        matched = [self._fuzzy_match(c) for c in concepts]
        matched = [m for m in matched if m]

        # 3. 收集关系路径
        paths = []
        for i, a in enumerate(matched):
            for b in matched[i + 1 :]:
                path = self._find_relation_path(a, b, max_hops=3)
                if path:
                    paths.append(path)

        # 4. 收集涉及的概念群落
        communities = []
        for node_name in matched:
            for community in self.communities:
                if node_name in community:
                    communities.append({
                        "name": f"{community[0][:5]}",
                        "members": community[:12],
                    })
                    break

        # 去重
        seen_comm = set()
        unique_communities = []
        for c in communities:
            key = c["name"]
            if key not in seen_comm:
                seen_comm.add(key)
                unique_communities.append(c)

        return {
            "paths": paths[:top_k],
            "communities": unique_communities[:3],
            "node_count": self.node_count,
            "edge_count": self.edge_count,
        }

    def get_related(
        self,
        concept: str,
        *,
        relation_type: Optional[str] = None,
        max_results: int = 10,
    ) -> list[dict]:
        """
        获取与某概念直接相关的实体。

        参数：
          concept — 概念名
          relation_type — 限定关系类型（如 "因果"、"对立"）
          max_results — 最大返回数
        """
        node_name = self._fuzzy_match(concept)
        if not node_name:
            return []

        results = []
        node_id = self._name_to_id(node_name)

        if not node_id:
            return []

        # 出边（node_name → other）
        for tgt_id in self.G.successors(node_id):
            edge_data = self.G[node_id][tgt_id]
            rel = edge_data.get("rel", "相关")
            if relation_type and rel != relation_type:
                continue
            tgt_name = self.G.nodes[tgt_id].get("name", tgt_id)
            results.append({
                "type": "out",
                "target": tgt_name,
                "relation": rel,
                "context": edge_data.get("context", ""),
            })

        # 入边（other → node_name）
        for src_id in self.G.predecessors(node_id):
            edge_data = self.G[src_id][node_id]
            rel = edge_data.get("rel", "相关")
            if relation_type and rel != relation_type:
                continue
            src_name = self.G.nodes[src_id].get("name", src_id)
            results.append({
                "type": "in",
                "target": src_name,
                "relation": rel,
                "context": edge_data.get("context", ""),
            })

        return results[:max_results]

    # ── 推理算法 ──────────────────────────────────────────

    def _find_relation_path(
        self, src: str, tgt: str, max_hops: int = 3
    ) -> Optional[dict]:
        """BFS 找两点间最短关系路径（networkx 实现）"""
        src_id = self._name_to_id(src)
        tgt_id = self._name_to_id(tgt)

        if not src_id or not tgt_id:
            return None

        if src_id == tgt_id:
            return {"nodes": [src], "relations": [], "path": src, "hops": 0}

        try:
            # networkx 最短路径
            path_ids = nx.shortest_path(self.G, source=src_id, target=tgt_id)
            nodes = [self.G.nodes[nid].get("name", nid) for nid in path_ids]
            relations = []
            for i in range(len(path_ids) - 1):
                edge_data = self.G[path_ids[i]][path_ids[i + 1]]
                relations.append(edge_data.get("rel", "相关"))

            return {
                "nodes": nodes,
                "relations": relations,
                "path": " → ".join(nodes),
                "hops": len(nodes) - 1,
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def _detect_communities(self):
        """
        社区发现。

        优先使用 Louvain 算法（需要 python-louvain），
        否则降级为 Label Propagation。
        """
        if self.G.number_of_nodes() == 0:
            return

        # 转为无向图（社区发现不考虑边方向）
        G_und = self.G.to_undirected()

        if _HAVE_LOUVAIN:
            # Louvain 算法
            partition = best_partition(G_und)
            # 按社区分组
            comm_dict: dict[int, list[str]] = defaultdict(list)
            for node_id, comm_id in partition.items():
                node_name = self.G.nodes[node_id].get("name", node_id)
                comm_dict[comm_id].append(node_name)
            self.communities = list(comm_dict.values())
        else:
            # Label Propagation（networkx 内置）
            from networkx.algorithms.community import label_propagation_communities

            communities_gen = label_propagation_communities(G_und)
            self.communities = [list(c) for c in communities_gen]

    # ── P1 后处理：关系推断增强 ───────────────────────────

    def _infer_tag_relations(self):
        """P1-B: 从 frontmatter tags 推断「同标签」关联边。

        共享 tag 的两个实体 → 新增 rel="同标签" 边（weight=0.5）。
        比纯共现更有语义（tags 是作者显式标注的分类信号）。
        """
        # 收集所有带 tags 的节点
        tag_to_nodes: dict[str, list[str]] = defaultdict(list)
        for node_id, data in self.G.nodes(data=True):
            tags = data.get("tags", [])
            if tags:
                name = data.get("name", node_id)
                for tag in tags:
                    tag_to_nodes[tag].append(name)

        # 为每个 tag 内的节点对创建同标签边
        tag_edge_count = 0
        for tag, members in tag_to_nodes.items():
            if len(members) < 2:
                continue
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    # 避免重复边（仅同rel类型去重，允许不同类型并行边）
                    src_id = self._name_to_id(a)
                    tgt_id = self._name_to_id(b)
                    if not src_id or not tgt_id:
                        continue
                    # P1 fix: 只跳过同类型的已有边，允许「引用」+「同标签」共存
                    has_same_rel = False
                    if self.G.has_edge(src_id, tgt_id):
                        existing_rel = self.G[src_id][tgt_id].get("rel", "")
                        if existing_rel == "同标签":
                            has_same_rel = True
                    if has_same_rel:
                        continue
                    self.G.add_edge(
                        src_id, tgt_id,
                        rel="同标签",
                        weight=0.5,
                        context=f"共享tag: {tag}",
                    )
                    tag_edge_count += 1

        if tag_edge_count > 0:
            print(f"[KnowledgeGraph] P1: 同标签推断新增 {tag_edge_count} 条边",
                  flush=True, file=sys.stderr)

    def _infer_directory_hierarchy(self, wiki_dir: Path):
        """P1-B: 从 wiki 目录结构推断「属于」层次关系。

        子目录中的文件 → 与目录名建立「包含/归属」关系。
        例如 wiki/概念/xxx.md → xxx 属于 概念 命名空间。
        """
        dir_edge_count = 0
        for f in wiki_dir.rglob("*.md"):
            if f.name == "index.md":
                continue
            try:
                rel_parts = f.relative_to(wiki_dir).parts
            except ValueError:
                continue
            if len(rel_parts) <= 1:
                continue  # 根目录文件，无父目录

            dir_name = rel_parts[0]  # 父目录名 = 命名空间
            entity_name = f.stem

            # 跳过噪声和非目标
            if EntityExtractor.is_noise(dir_name) or EntityExtractor.is_noise(entity_name):
                continue
            if dir_name == entity_name:
                continue

            src_id = self._name_to_id(entity_name)
            # 目录名使用精确匹配（避免模糊命中如"概念"→"我的概念"）
            dir_node_id = self.nodes_by_name.get(dir_name)
            if not dir_node_id:
                # 目录名作为虚拟节点加入
                dir_node_id = EntityExtractor._node_id(dir_name)
                if not self.G.has_node(dir_node_id):
                    self.G.add_node(dir_node_id, name=dir_name, aliases=[], content="")

            if not src_id:
                continue
            if self.G.has_edge(src_id, dir_node_id):
                continue

            self.G.add_edge(
                src_id, dir_node_id,
                rel="归属于",
                weight=0.4,
                context=f"目录层次: {dir_name}/",
            )
            dir_edge_count += 1

        if dir_edge_count > 0:
            print(f"[KnowledgeGraph] P1: 目录层次推断新增 {dir_edge_count} 条边",
                  flush=True, file=sys.stderr)

    def _merge_synonym_aliases(self):
        """P2-B: 同义词别名合并——将别名节点的边重定向到规范节点。

        对于 SYNONYM_ALIASES 中定义的每个规范名：
          - 如果别名节点和规范节点都存在 → 别名节点的边重定向到规范节点
          - 删除孤立化的别名节点（保留其 name → canonical_id 映射供查询兼容）
        """
        merged_count = 0
        for canonical, aliases in EntityExtractor.SYNONYM_ALIASES.items():
            canon_id = self.nodes_by_name.get(canonical)
            if not canon_id:
                continue  # 规范节点不存在，跳过

            for alias in aliases:
                alias_id = self.nodes_by_name.get(alias)
                if not alias_id or alias_id == canon_id:
                    continue

                # 重定向别名节点的所有出边到规范节点
                for _, tgt_id, data in list(self.G.out_edges(alias_id, data=True)):
                    if not self.G.has_edge(canon_id, tgt_id) or \
                       self.G[canon_id][tgt_id].get("rel") != data.get("rel"):
                        self.G.add_edge(canon_id, tgt_id,
                                        rel=data.get("rel", "相关"),
                                        weight=data.get("weight", 0.5),
                                        context=f"别名合并({alias}→{canonical}): {data.get('context','')}")
                        merged_count += 1

                # 重定向入边
                for src_id, _, data in list(self.G.in_edges(alias_id, data=True)):
                    if not self.G.has_edge(src_id, canon_id) or \
                       self.G[src_id][canon_id].get("rel") != data.get("rel"):
                        self.G.add_edge(src_id, canon_id,
                                        rel=data.get("rel", "相关"),
                                        weight=data.get("weight", 0.5),
                                        context=f"别名合并({alias}→{canonical})")
                        merged_count += 1

                # 删除别名节点
                self.G.remove_node(alias_id)
                self._nodes_by_name = None  # 使缓存失效

        if merged_count > 0:
            print(f"[KnowledgeGraph] P2: 别名合并重定向 {merged_count} 条边",
                  flush=True, file=sys.stderr)

    def _infer_bridge_edges(self):
        """P2-C: 二跳桥接——共享邻居的两个非直连节点间建立弱桥接边。

        检测两种模式：
          1. 出边二跳：A → X → B（A的二跳后继）
          2. 共引模式：A → X ← B（A和B共同指向X，co-citation）
        """
        bridge_count = 0
        succ = {n: set(self.G.successors(n)) for n in self.G.nodes()}
        pred = {n: set(self.G.predecessors(n)) for n in self.G.nodes()}

        # 模式1：出边二跳
        processed_pairs = set()
        for node_id in list(self.G.nodes()):
            two_hop = set()
            for s in succ.get(node_id, []):
                two_hop.update(succ.get(s, []))
            two_hop.discard(node_id)
            two_hop -= succ.get(node_id, set())

            for target in two_hop:
                pair = tuple(sorted([node_id, target]))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)
                if self.G.has_edge(node_id, target) or self.G.has_edge(target, node_id):
                    continue
                src_name = self.G.nodes[node_id].get("name", "")
                tgt_name = self.G.nodes[target].get("name", "")
                if not src_name or not tgt_name:
                    continue
                self.G.add_edge(node_id, target, rel="桥接",
                                weight=0.15, context="二跳出边")
                bridge_count += 1
                if bridge_count >= 500:
                    break
            if bridge_count >= 500:
                break

        # 模式2：共引桥接（A→X 且 B→X 但 A-B 无边）
        # 只在 bridge_count < 500 时继续
        if bridge_count < 500:
            # 收集所有被引用次数≥2的节点作为潜在桥梁
            in_degree = dict(self.G.in_degree())
            bridges = [n for n, d in in_degree.items() if d >= 2]
            for x in bridges:
                # x 的所有前驱（指向 x 的节点）
                citers = list(pred.get(x, []))
                if len(citers) < 2:
                    continue
                for i, a in enumerate(citers):
                    for b in citers[i + 1:]:
                        pair = tuple(sorted([a, b]))
                        if pair in processed_pairs:
                            continue
                        processed_pairs.add(pair)
                        if self.G.has_edge(a, b) or self.G.has_edge(b, a):
                            continue
                        aname = self.G.nodes[a].get("name", "")
                        bname = self.G.nodes[b].get("name", "")
                        if not aname or not bname:
                            continue
                        self.G.add_edge(a, b, rel="共引桥接",
                                        weight=0.12, context=f"共同引用: {self.G.nodes[x].get('name','')}")
                        bridge_count += 1
                        if bridge_count >= 700:
                            break
                    if bridge_count >= 700:
                        break
                if bridge_count >= 700:
                    break

        if bridge_count > 0:
            print(f"[KnowledgeGraph] P2: 桥接边新增 {bridge_count} 条",
                  flush=True, file=sys.stderr)

    # ── 内部工具 ──────────────────────────────────────────

    def _extract_concepts_from_text(self, text: str) -> list[str]:
        """从文本中提取可能是概念名的中文词组。

        B12 fix（2026-05-08）：原实现用 re.findall 贪婪非重叠匹配，
        导致「道和上善若水有什么关系」中「上善若水」被吞入 5 字串
        「道和上善若」。改为滑动窗口枚举所有 1~5 字中文子串，逐一查表。
        """
        concepts = list(EntityExtractor.WIKI_LINK_RE.findall(text))

        # B12: 滑动窗口提取所有 1~5 字中文子串，查 nodes_by_name
        chinese_chars = [c for c in text if '\u4e00' <= c <= '\u9fff']
        for i in range(len(chinese_chars)):
            for j in range(i + 1, min(i + 6, len(chinese_chars) + 1)):
                candidate = ''.join(chinese_chars[i:j])
                if candidate in self.nodes_by_name:
                    concepts.append(candidate)

        return list(dict.fromkeys(concepts))  # 去重保留顺序

    @property
    def nodes_by_name(self) -> dict[str, str]:
        """节点名 → 节点 ID 的反向索引"""
        if self._nodes_by_name is None:
            self._nodes_by_name = {
                self.G.nodes[nid].get("name", nid): nid for nid in self.G.nodes()
            }
        return self._nodes_by_name

    def _name_to_id(self, name: str) -> Optional[str]:
        """将节点名转换为节点 ID。"""
        if name in self.nodes_by_name:
            return self.nodes_by_name[name]
        # 模糊匹配
        for known_name, nid in self.nodes_by_name.items():
            if name in known_name or known_name in name:
                return nid
        return None

    def _fuzzy_match(self, name: str) -> Optional[str]:
        """模糊匹配：精确 → 部分包含 → None，返回节点名。"""
        node_id = self._name_to_id(name)
        if node_id:
            return self.G.nodes[node_id].get("name", node_id)
        return None

    def export_json(self, path: Path):
        """导出图谱为 JSON（可用于可视化）"""
        data = {
            "nodes": [
                {"id": nid, **self.G.nodes[nid]}
                for nid in self.G.nodes()
            ],
            "edges": [
                {"source": u, "target": v, **self.G[u][v]}
                for u, v in self.G.edges()
            ],
            "communities": [
                {"id": i, "members": c}
                for i, c in enumerate(self.communities)
            ],
            "meta": {
                "node_count": self.node_count,
                "edge_count": self.edge_count,
                "community_count": len(self.communities),
            },
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[KnowledgeGraph] 已导出到 {path}", flush=True, file=sys.stderr)

    def export_viz_data(self) -> dict:
        """P3: 导出 D3 力导图可视化所需的结构化数据。

        返回 dict，包含：
          - nodes: D3 力导节点（含 id/name/community/degree/type）
          - edges: D3 边（source/target 为索引，含 rel/weight）
          - communities: 群落列表（用于着色）
          - stats: 图谱统计摘要
          - rel_types: 边类型分布
        """
        # 构建节点 → 索引映射（D3 force 要求边用整数索引引用节点）
        node_list = []
        node_idx = {}  # node_id → index in node_list
        for nid in self.G.nodes():
            data = self.G.nodes[nid]
            node_idx[nid] = len(node_list)
            degree = self.G.degree(nid)
            node_list.append({
                "id": nid,
                "name": data.get("name", nid),
                "degree": degree,
                "type": data.get("type", "concept"),
            })

        # 为节点分配群落颜色
        comm_color = {}  # node_id → community_id
        for cid, members in enumerate(self.communities):
            for mname in members:
                mid = self._name_to_id(mname)
                if mid:
                    comm_color[mid] = cid

        for node in node_list:
            node["community"] = comm_color.get(node["id"], -1)

        # 构建边（使用整数索引）
        edges = []
        rel_dist = defaultdict(int)
        for u, v, data in self.G.edges(data=True):
            edges.append({
                "source": node_idx[u],
                "target": node_idx[v],
                "rel": data.get("rel", "相关"),
                "weight": data.get("weight", 0.5),
            })
            rel_dist[data.get("rel", "相关")] += 1

        # 统计摘要
        degrees = [self.G.degree(n) for n in self.G.nodes()]
        density = (2.0 * self.edge_count) / (self.node_count * (self.node_count - 1)) if self.node_count > 1 else 0

        return {
            "nodes": node_list,
            "edges": edges,
            "communities": [
                {"id": i, "size": len(c), "members": c[:10]}
                for i, c in enumerate(self.communities)
            ],
            "stats": {
                "node_count": self.node_count,
                "edge_count": self.edge_count,
                "community_count": len(self.communities),
                "density": round(density, 4),
                "avg_degree": round(sum(degrees) / len(degrees), 1) if degrees else 0,
                "max_degree": max(degrees) if degrees else 0,
                "rel_types": dict(rel_dist),
            },
        }


# ════════════════════════════════════════════════════════
# 测试入口
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from pathlib import Path

    kg = KnowledgeGraph()
    wiki_dir = Path("d:/Obsidian_KN/philosophy/wiki")
    print("构建知识图谱...")
    kg.build_from_wiki(wiki_dir, use_ner=False)
    print(f"完成！节点数：{kg.node_count}，边数：{kg.edge_count}")

    # 测试查询
    result = kg.query("柔弱胜刚强 与 无为 有什么关系？")
    print(f"查询到 {len(result['paths'])} 条路径")
