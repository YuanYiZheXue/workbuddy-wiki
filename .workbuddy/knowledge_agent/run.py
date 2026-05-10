"""
三层知识系统 — 主入口
=======================
直接运行此脚本测试三层协同效果：

  python run.py "老子'柔弱胜刚强'和'不争之德'是什么关系？"

或交互模式：
  python run.py --interactive
"""

import sys
import asyncio
from pathlib import Path

# ── 核心模块 ──────────────────────────────────────────────
from unified_agent import UnifiedKnowledgeAgent


WIKI_DIR = r"d:\Obsidian_KN\philosophy\wiki"
GRAPH_EXPORT = r"d:\Obsidian_KN\philosophy\.workbuddy\knowledge_agent\graph_export.json"


async def main(query: str | None = None):
    agent = UnifiedKnowledgeAgent(
        wiki_dir=WIKI_DIR,
        # openai_key: 默认从环境变量 OPENAI_API_KEY 读取
    )

    # 初始化（三层全部加载）
    await agent.initialize()

    # 可选：导出图谱用于可视化
    agent.graph.export_json(Path(GRAPH_EXPORT))
    print(f"  图谱已导出: {GRAPH_EXPORT}")

    if query:
        # 单次查询
        result = await agent.query(query)
        print_result(result)
    else:
        # 交互模式
        print("\n[三层知识系统] 输入你的问题，输入 q 退出：")
        while True:
            try:
                q = input("\n你> ").strip()
                if q.lower() in ("q", "quit", "exit"):
                    break
                if not q:
                    continue
                result = await agent.query(q)
                print_result(result)
            except (KeyboardInterrupt, EOFError):
                break


def print_result(result):
    print("\n" + "═" * 60)
    print(f"【查询类型】{result.query_type}")
    print(f"【触发层】{result.layers_hit}")
    print(f"【耗时】{result.meta['elapsed_s']}s")
    print(f"【文档命中】{result.meta['docs_found']}")
    print(f"【图谱节点命中】{result.meta['nodes_found']}")
    print("─" * 60)
    print(result.response)
    print("═" * 60)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--interactive" in args:
        asyncio.run(main())
    else:
        query = " ".join(a for a in args if not a.startswith("--")) or None
        asyncio.run(main(query))
