"""
MCP Knowledge Base Server - Centralized Configuration
====================================================
Single source of truth for all paths and settings.
All modules import from here instead of hardcoding paths.

Environment variable override:
  PHILOSOPHY_ROOT - Project root directory (fallback: D:\\Obsidian_KN\\philosophy)
  MCP_DEBUG       - Set "true" to expose internal details in kb_status
  USE_NER         - Enable NER entity extraction ("true"/"false", default "false")
  NER_MODEL_MODE  - NER backend: "dict" (default, zero-dep) / "model" (BERT, auto-falls back to dict if unavailable)
"""

from pathlib import Path
import os

# ═══ 项目根目录 ═══
_PROJECT_ROOT = Path(os.environ.get(
    "PHILOSOPHY_ROOT",
    r"D:\Obsidian_KN\philosophy"
))

# ═══ 路径定义 ═══
AGENT_DIR = _PROJECT_ROOT / ".workbuddy" / "knowledge_agent"
CHROMA_DB_PATH = _PROJECT_ROOT / ".workbuddy" / "chroma_db"
WIKI_DIR = _PROJECT_ROOT / "wiki"

# ═══ 运行时开关 ═══
DEBUG_MODE = os.environ.get("MCP_DEBUG", "").lower() == "true"

# ═══ NER 配置 ═══
USE_NER = os.environ.get("USE_NER", "false").lower() == "true"
NER_MODEL_MODE = os.environ.get("NER_MODEL_MODE", "dict").lower()  # "dict" | "model"


def safe_path_display(p: str | Path) -> str:
    """在生产环境中隐藏绝对路径细节，仅显示末两级目录。

    调试模式 (MCP_DEBUG=true) 下返回完整路径。
    """
    p_str = str(p)
    if DEBUG_MODE:
        return p_str
    parts = Path(p_str).parts
    if len(parts) >= 2:
        return f".../{parts[-2]}/{parts[-1]}"
    return f".../{parts[-1]}"
