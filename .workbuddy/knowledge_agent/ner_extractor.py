"""
NERExtractor — 中文命名实体识别（知识图谱实体提取）
=====================================================
用 transformers 加载中文 BERT 模型，对文本进行 Token 级 NER 标注，
提取知识图谱所需的实体节点。

依赖：
  - transformers 4.30+
  - torch 2.0+
  - 模型：shibing624/bert4ner-base-chinese（推荐，简体中文，F1=95%）
         或 ckiplab/bert-base-chinese-ner（繁体中文备选）

用法：
  extractor = NERExtractor(use_model=True)
  entities = extractor.extract("苹果公司发布了新手机")
  # → [("苹果公司", "ORG"), ("乔布斯", "PER")]

模型对比（2026-05-07 实测）：
  模型                          简体哲学召回  加载速度  特点
  shibing624/bert4ner-base      55%          3s       简体原生，人民日报训练
  ckiplab/bert-base-chinese-ner 55%          2.6s     繁体中文，碎片化分词
"""

import re
from pathlib import Path
from typing import Optional


# ════════════════════════════════════════════════════
# 默认模型与标签映射
# ════════════════════════════════════════════════════

_DEFAULT_MODEL = "shibing624/bert4ner-base-chinese"

# 各模型的标签 → 统一标签映射
_LABEL_MAP = {
    # shibing624/bert4ner 的标签
    "PER": "PER", "LOC": "LOC", "ORG": "ORG", "TIME": "TIME",
    # ckiplab 的标签
    "PERSON": "PER", "GPE": "LOC", "DATE": "TIME",
    "WORK_OF_ART": "MISC", "CARDINAL": "MISC",
    # 通用兜底
    "MISC": "MISC",
}

# 统一标签的中文描述
_LABEL_DESC = {
    "PER": "人物", "LOC": "地点", "ORG": "机构",
    "TIME": "时间", "MISC": "其他",
}


# ════════════════════════════════════════════════════
# NERExtractor — 核心类
# ════════════════════════════════════════════════════

class NERExtractor:
    """
    中文命名实体识别器。

    支持两种模式：
      1. 词典模式（默认，零依赖，启动快）
      2. 模型模式（需 transformers，准确率高）

    切换方式：
      extractor = NERExtractor(use_model=True)  # 使用 BERT 模型
      extractor = NERExtractor(use_model=False) # 使用词典（默认）

    注意：
      - 模式模式首次运行会下载模型（~400MB），需联网
      - 推荐模型：shibing624/bert4ner-base-chinese（简体中文 F1=95%）
      - 词典模式准确率中等（~70%），但零成本、零延迟
    """

    def __init__(
        self,
        use_model: bool = False,
        model_name: str = _DEFAULT_MODEL,
    ):
        self.use_model = use_model
        self.model_name = model_name
        self._tokenizer = None
        self._model = None

        # 词典模式：内置常见实体词典（可扩展）
        self._dict = self._load_dict()

    # ── 公共接口 ──────────────────────────────

    def extract(self, text: str, merge_overlap: bool = True) -> list[tuple[str, str]]:
        """
        从文本中提取命名实体。

        参数：
          text — 输入文本
          merge_overlap — 是否合并重叠实体（默认 True）

        返回：[(实体文本, 实体类型), ...]
          类型：PER（人物）/ LOC（地点）/ ORG（机构）/ TIME（时间）/ MISC（其他）
        """
        if self.use_model:
            return self._extract_by_model(text, merge_overlap)
        else:
            return self._extract_by_dict(text, merge_overlap)

    def extract_from_file(self, file_path: Path, content: Optional[str] = None) -> list[tuple[str, str]]:
        """从文件中提取实体。"""
        if content is None:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                return []

        entities = self.extract(content)

        stem = file_path.stem
        if stem and stem not in [e[0] for e in entities]:
            entities.append((stem, "MISC"))

        return entities

    # ── 模型模式 ──────────────────────────────

    def _load_model(self):
        """懒加载 BERT NER 模型。"""
        if self._model is not None:
            return
        try:
            from transformers import pipeline
            print(f"[NER] 加载模型：{self.model_name}", flush=True, file=sys.stderr)
            self._ner_pipe = pipeline(
                "ner",
                model=self.model_name,
                aggregation_strategy="simple",
            )
            print(f"[NER] 模型就绪：{self.model_name}", flush=True, file=sys.stderr)
            self._model = True  # B11 fix: 防止 _load_model() 重复加载
        except Exception as e:
            print(f"[NER] 模型加载失败：{e}，降级为词典模式",
                  flush=True, file=sys.stderr)
            self.use_model = False

    def _normalize_label(self, raw_label: str) -> str:
        """将不同模型的标签统一到标准集。"""
        return _LABEL_MAP.get(raw_label.upper(), "MISC")

    def _clean_entity_text(self, text: str) -> str:
        """清理实体文本（去除子词空格等）。"""
        # 去除 BERT 分词产生的字间空格
        return text.replace(" ", "")

    def _extract_by_model(self, text: str, merge_overlap: bool) -> list[tuple[str, str]]:
        """用 BERT NER 模型提取实体。"""
        self._load_model()
        try:
            results = self._ner_pipe(text)
            entities = []
            seen = set()  # 去重
            for r in results:
                clean_text = self._clean_entity_text(r["word"])
                label = self._normalize_label(r["entity_group"])
                if clean_text and clean_text not in seen:
                    seen.add(clean_text)
                    entities.append((clean_text, label))
            return entities
        except Exception as e:
            print(f"[NER] 模型推理失败：{e}，降级为词典模式",
                  flush=True, file=sys.stderr)
            self.use_model = False
            return self._extract_by_dict(text, merge_overlap)

    # ── 词典模式 ──────────────────────────────

    def _load_dict(self) -> dict:
        """加载内置实体词典。格式：{ "词语": "类型" }"""
        orgs = [
            "苹果公司", "腾讯", "阿里巴巴", "百度", "华为",
            "Google", "Microsoft", "Amazon", "Meta",
            "清华大学", "北京大学", "复旦大学",
            "道家", "儒家", "法家", "墨家", "释家",
        ]
        pers = [
            "老子", "孔子", "孟子", "庄子", "荀子",
            "毛泽东", "邓小平", "习近平",
            "乔布斯", "马斯克", "比尔盖茨",
            "香农", "图灵", "冯诺依曼",
        ]
        locs = [
            "中国", "美国", "北京", "上海", "深圳",
            "欧洲", "亚洲", "非洲", "美洲",
        ]

        d = {}
        for w in orgs: d[w] = "ORG"
        for w in pers: d[w] = "PER"
        for w in locs: d[w] = "LOC"
        return d

    def _extract_by_dict(self, text: str, merge_overlap: bool) -> list[tuple[str, str]]:
        """用词典 + 正则提取实体。"""
        entities = []

        # 1. 词典匹配
        for word, label in self._dict.items():
            if word in text:
                entities.append((word, label))

        # 2. 正则补充
        for m in re.finditer(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*", text):
            entities.append((m.group(), "MISC"))

        for m in re.finditer(r"([\u4e00-\u9fff]{2,3})(?:说|认为|指出|表示)", text):
            entities.append((m.group(1), "PER"))

        return entities

    # ── 扩展词典（用户可调用） ─────────────────

    def add_entity(self, word: str, label: str):
        """向词典中添加自定义实体。"""
        self._dict[word] = label

    def save_dict(self, path: Path):
        """将当前词典保存到文件。"""
        with open(path, "w", encoding="utf-8") as f:
            for word, label in self._dict.items():
                f.write(f"{word}\t{label}\n")

    def load_dict(self, path: Path):
        """从文件加载词典。"""
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t", 1)
                if len(parts) == 2:
                    self._dict[parts[0]] = parts[1]


import sys

# ════════════════════════════════════════════════════
# 测试入口
# ════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    os.environ.setdefault("USERNAME", "11010")
    os.environ.setdefault("PYTHONUTF8", "1")

    print("=" * 50)
    print("  NERExtractor 测试")
    print("=" * 50)

    # 模式1：词典模式
    print("\n--- 词典模式 ---")
    extractor = NERExtractor(use_model=False)
    texts = [
        "老子是春秋时期的思想家，道家学派创始人。",
        "香农在1948年发表了《通信的数学理论》。",
    ]
    for t in texts:
        print(f"\n  文本：{t}")
        for w, l in extractor.extract(t):
            print(f"    {l}: {w}")

    # 模式2：模型模式（如果可用）
    print("\n--- 模型模式 ---")
    try:
        extractor_m = NERExtractor(use_model=True)
        for t in texts:
            print(f"\n  文本：{t}")
            for w, l in extractor_m.extract(t):
                print(f"    [{_LABEL_DESC.get(l, l)}] {w}")
    except Exception as e:
        print(f"  模型模式跳过：{e}")
