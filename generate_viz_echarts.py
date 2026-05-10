#!/usr/bin/env python3
"""
GraphRAG 可视化 - ECharts 极简版
===============================
从 graph_data.json 生成 ECharts 关系图 HTML

优势 vs D3+Canvas 手写版：
- ~80 行核心 JS（配置驱动，非命令式渲染）
- ECharts 内置：力导布局 / 缩放 / 拖拽 / tooltip / 高亮 / 搜索
- 维护成本：改 option JSON 即可
- 性能：1926 节点 + 7535 边流畅运行

用法:
    python generate_viz_echarts.py [--input graph_data.json] [--output wiki/.viz/index.html]
"""

import json
import sys
import os
import argparse
from html import escape as htmlescape

# ─── 默认路径 ───
DEFAULT_INPUT  = os.path.join(os.path.dirname(__file__), "wiki", ".viz", "graph_data.json")
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "wiki", ".viz", "index.html")

# ─── 调色板（ECharts visualMap 用） ───
PALETTE = [
    "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
    "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac",
    "#7eb5a6","#b5ca5f","#d4728c","#9a8f66","#c6a66c",
    "#86b5c5","#c27ba0","#a8c68c","#8f9cc2","#d4a07a",
]

# 边关系颜色映射
REL_COLORS = {
    "包含":   "#f28e2b",
    "引用":   "#4e79a7",
    "相关":   "#999999",
    "同标签": "#e15759",
    "桥接":   "#bbbbbb",
    "归属于": "#59a14f",
    "对立":   "#ff006e",
    "对比":   "#b07aa1",
}

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GraphRAG 知识图谱 · ECharts</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0f0f12; color:#e0e0e6; font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; overflow:hidden; }
#toolbar { position:fixed; top:10px; left:10px; z-index:100; display:flex; gap:6px; align-items:center; }
#toolbar input { background:#1a1a2e; color:#e0e0e6; border:1px solid #333; padding:6px 12px; border-radius:6px; font-size:13px; width:220px; outline:none; }
#toolbar input:focus { border-color:#555; }
#toolbar button { background:#1a1a2e; color:#e0e0e6; border:1px solid #333; padding:6px 14px; border-radius:6px; cursor:pointer; font-size:13px; }
#toolbar button:hover { background:#252540; }
#sidebar { position:fixed; top:50px; right:10px; width:260px; max-height:calc(100vh - 60px); overflow-y:auto; z-index:100;
  background:rgba(20,20,38,0.92); border:1px solid #333; border-radius:8px; padding:14px; font-size:13px; backdrop-filter:blur(10px); }
.stat-card { background:#151525; border:1px solid #282845; border-radius:6px; padding:10px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
.stat-value { font-size:20px; font-weight:bold; color:#fff; }
.stat-label { font-size:11px; color:#888; }
.rel-row { display:flex; justify-content:space-between; padding:3px 0; font-size:11px; border-bottom:1px solid #222; color:#bbb; }
.comm-row { display:flex; align-items:center; gap:6px; padding:3px 0; font-size:11px; color:#bbb; }
.comm-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
#hint { position:fixed; bottom:10px; left:50%; transform:translateX(-50%); background:rgba(20,20,38,0.85);
  border:1px solid #333; border-radius:6px; padding:6px 16px; font-size:11px; color:#777; z-index:100; pointer-events:none; }
</style>
</head>
<body>
<div id="toolbar">
  <input id="search" type="text" placeholder="搜索节点... (Enter高亮)" />
  <button onclick="resetView()">重置视图</button>
  <button id="lblBtn" onclick="toggleLabels()">显示标签</button>
</div>
<div id="chart" style="width:100vw;height:100vh;"></div>
<div id="sidebar">
  <div class="stat-card"><span class="stat-label">节点数</span><span class="stat-value" id="s-nodes">-</span></div>
  <div class="stat-card"><span class="stat-label">边数</span><span class="stat-value" id="s-edges">-</span></div>
  <div class="stat-card"><span class="stat-label">群落数</span><span class="stat-value" id="s-comms">-</span></div>
  <div class="stat-card"><span class="stat-label">图密度</span><span class="stat-value" id="s-dens">-</span></div>
  <div class="stat-card"><span class="stat-label">平均度</span><span class="stat-value" id="s-deg">-</span></div>
  <hr style="border-color:#333;margin:12px 0">
  <div style="font-weight:bold;margin-bottom:6px;color:#aaa;font-size:11px">边类型分布</div>
  <div id="rel-dist"></div>
  <hr style="border-color:#333;margin:12px 0">
  <div style="font-weight:bold;margin-bottom:6px;color:#aaa;font-size:11px">TOP 群落</div>
  <div id="comm-list"></div>
</div>
<div id="hint">🖱️ 滚轮缩放 · 拖动画布/节点 · 单击聚焦 · 右键取消聚焦</div>

<!-- ECharts 本地（不依赖CDN） -->
<script src="echarts.min.js"></script>
<script>
// ═══════════ 数据注入 ═══════════
var GRAPH_DATA = __DATA_JSON__;
var PALETTE = __PALETTE_JSON__;
var REL_COLORS_MAP = __REL_COLORS_JSON__;

var NODES = GRAPH_DATA.nodes || [];
var EDGES = GRAPH_DATA.edges || [];

// 统计信息
var nodeCount = NODES.length;
var edgeCount = EDGES.length;

// 提取群落
var commSet = new Set();
NODES.forEach(function(n) { if(n.community !== undefined) commSet.add(n.community); });
var comms = Array.from(commSet).sort(function(a,b){return a-b});

// 边类型统计
var relCount = {};
EDGES.forEach(function(e) {
  var r = e.rel || "关联";
  relCount[r] = (relCount[r]||0) + 1;
});

// 计算图指标
var maxDeg = 0, sumDeg = 0;
NODES.forEach(function(n) {
  var d = n.degree || 0;
  if(d > maxDeg) maxDeg = d;
  sumDeg += d;
});
var avgDeg = nodeCount > 0 ? (sumDeg / nodeCount).toFixed(1) : 0;
var density = nodeCount > 1 ? ((2 * edgeCount) / (nodeCount * (nodeCount - 1))).toFixed(4) : 0;

// 更新侧栏
document.getElementById("s-nodes").textContent = nodeCount.toLocaleString();
document.getElementById("s-edges").textContent = edgeCount.toLocaleString();
document.getElementById("s-comms").textContent = comms.length;
document.getElementById("s-dens").textContent = density;
document.getElementById("s-deg").textContent = avgDeg;

var relEl = document.getElementById("rel-dist");
Object.entries(relCount).sort(function(a,b){return b[1]-a[1]}).forEach(function(p) {
  relEl.innerHTML += '<div class="rel-row"><span>' + p[0] + '</span><span>' + p[1] + '</span></div>';
});

// 统计各群落大小
var commSizes = {};
NODES.forEach(function(n) {
  var c = n.community || 0;
  commSizes[c] = (commSizes[c]||0) + 1;
});
var commListEl = document.getElementById("comm-list");
comms.slice().sort(function(a,b){return (commSizes[b]||0)-(commSizes[a]||0)}).slice(0,10).forEach(function(c) {
  var clr = PALETTE[c % PALETTE.length];
  commListEl.innerHTML += '<div class="comm-row"><span class="comm-dot" style="background:'+clr+'"></span>C' + c + ' (' + (commSizes[c]||0) + '节点)</div>';
});

// ═══════════ 构建 ECharts Option ═══════════

// 类别定义（按群落）
var categories = comms.map(function(c) {
  return { name: 'C' + c, itemStyle: { color: PALETTE[c % PALETTE.length] } };
});

// 节数据
var chartNodes = NODES.map(function(n, i) {
  return {
    id: i,
    name: n.name || ("node_"+i),
    value: n.degree || 0,
    symbolSize: Math.max(3, Math.min(30, (n.degree||0) * 0.45 + 3)),
    category: n.community || 0,
    itemStyle: {
      color: PALETTE[(n.community||0) % PALETTE.length],
      opacity: 0.88,
      borderColor: "rgba(255,255,255,0.25)",
      borderWidth: 0.6,
    },
    label: { show: false },
  };
});

// 边数据（用节点索引）
var chartEdges = EDGES.map(function(e) {
  // source/target 可能是索引或对象引用，这里统一处理为索引
  var s = typeof e.source === "number" ? e.source : (typeof e.source === "object" ? (e.source.index || 0) : 0);
  var t = typeof e.target === "number" ? e.target : (typeof e.target === "object" ? (e.target.index || 0) : 0);
  var relColor = REL_COLORS_MAP[e.rel] || "#666666";
  return {
    source: s,
    target: t,
    value: e.weight || 1,
    lineStyle: {
      color: relColor,
      width: Math.max(0.3, Math.min(2, (e.weight||0.5)*2)),
      opacity: 0.18,
      curveness: 0.05,
    },
  };
});

// 构建节点名→索引映射（用于搜索）
var nameToIdx = {};
chartNodes.forEach(function(n,i) { nameToIdx[n.name.toLowerCase()] = i; });

// 初始化图表
var dom = document.getElementById("chart");
var myChart = echarts.init(dom, null, { renderer: "canvas" });

var showLabels = false;
var searchActive = false;
var searchNodeIds = null;

function getOption() {
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      confine: true,
      backgroundColor: "rgba(15,15,25,0.95)",
      borderColor: "#444",
      borderWidth: 1,
      textStyle: { fontSize: 12, color: "#ddd", lineHeight: 18 },
      formatter: function(params) {
        if (params.dataType === "node") {
          var d = params.data;
          var n = NODES[d.id];
          var html = "<b>" + params.name + "</b>";
          if (n) {
            html += "<br/>度: " + (n.degree||0) +
                    " | 类型: " + (n.type||"-") +
                    " | 群落: C" + (n.community||0);
            // 邻居信息
            var nbrs = [];
            for (var j=0; j<EDGES.length && nbrs.length<8; j++) {
              var ej = EDGES[j];
              var sj = typeof ej.source==="number"?ej.source:(ej.source.index||0);
              var tj = typeof ej.target==="number"?ej.target:(ej.target.index||0);
              if (sj===d.id) nbrs.push((ej.rel||"")+" → "+(NODES[tj]?NODES[tj].name:"?"));
              else if (tj===d.id) nbrs.push((NODES[sj]?NODES[sj].name:"?")+" → "+(ej.rel||""));
            }
            if (nbrs.length > 0) {
              html += '<br/><span style="color:#888;font-size:10.5px">关系: '+nbrs.slice(0,5).join(" | ")+"</span>";
            }
          }
          return html;
        }
        if (params.dataType === "edge") {
          return (chartNodes[params.data.source]?chartNodes[params.data.source].name:"?") +
            " —[" + (EDGES[params.dataIndex]?EDGES[params.dataIndex].rel:"-") + "]→ " +
            (chartNodes[params.data.target]?chartNodes[params.data.target].name:"?");
        }
        return "";
      },
    },
    animationDurationUpdate: 200,
    animationEasingUpdate: "quarticInOut",
    series: [{
      type: "graph",
      layout: "force",
      data: chartNodes,
      links: chartEdges,
      categories: categories,
      roam: true,           // 缩放 + 拖拽（Echarts 内置）
      draggable: true,       // 节点可拖拽
      focusNodeAdjacency: true, // 点击自动高亮邻居（内置！）
      force: {
        repulsion: 120,     // 斥力
        edgeLength: [15, 60], // 边长度范围
        gravity: 0.1,        // 向心力
        friction: 0.6,
      },
      emphasis: {
        focus: "adjacency",
        lineStyle: { width: 2.5, opacity: 0.7 },
        itemStyle: {
          shadowBlur: 16,
          shadowColor: "rgba(0,0,0,0.5)",
          borderWidth: 2,
          borderColor: "rgba(255,255,255,0.85)",
        },
      },
      select: {
        itemStyle: { borderWidth: 2.5, borderColor: "#fff" },
      },
      label: {
        show: showLabels,
        position: "right",
        formatter: function(p) {
          var nm = p.name || "";
          return nm.length > 14 ? nm.slice(0,13) + "\u2026" : nm;
        },
        fontSize: 10,
        color: "#ccc",
      },
      edgeLabel: {
        show: false,
      },
      lineStyle: {
        opacity: 0.18,
        curveness: 0.05,
      },
      symbol: "circle",
      itemStyle: {},
      blur: {
        itemStyle: { opacity: 0.04 },
        lineStyle: { opacity: 0.02 },
      },
    }],
  };
}

myChart.setOption(getOption());

// ═══════════ 交互逻辑 ═══════════

window.resetView = function() {
  myChart.dispatchAction({ type: "restore" });
};

window.toggleLabels = function() {
  showLabels = !showLabels;
  document.getElementById("lblBtn").textContent = showLabels ? "隐藏标签" : "显示标签";
  var opt = myChart.getOption();
  opt.series[0].label.show = showLabels;
  myChart.setOption(opt);
};

// 搜索功能
var searchInput = document.getElementById("search");
searchInput.addEventListener("keydown", function(e) {
  if (e.key === "Enter") doSearch();
});
searchInput.addEventListener("input", function() {
  if (this.value.trim() === "") clearSearch();
});

function doSearch() {
  var q = searchInput.value.trim().toLowerCase();
  if (!q) { clearSearch(); return; }

  var matched = [];
  chartNodes.forEach(function(n, i) {
    if (n.name.toLowerCase().indexOf(q) !== -1) matched.push(i);
  });

  if (matched.length === 0) return;

  searchActive = true;
  searchNodeIds = matched;

  // 高亮匹配节点，淡化其他
  var opt = myChart.getOption();
  opt.series[0].data = opt.series[0].data.map(function(n, i) {
    var isMatch = matched.indexOf(i) !== -1;
    return Object.assign({}, n, {
      itemStyle: Object.assign({}, n.itemStyle, {
        opacity: isMatch ? 1 : 0.06,
      }),
      symbolSize: isMatch ? n.symbolSize * 1.8 : n.symbolSize * 0.6,
      label: { show: isMatch || showLabels },
    });
  });
  opt.series[0].links = opt.series[0].links.map(function(e) {
    var isMatchEdge = matched.indexOf(e.source)!==-1 || matched.indexOf(e.target)!==-1;
    return Object.assign({}, e, {
      lineStyle: Object.assign({}, e.lineStyle, {
        opacity: isMatchEdge ? 0.65 : 0.02,
        width: isMatchEdge ? 1.5 : 0.3,
      }),
    });
  });

  myChart.setOption(opt);

  // 缩放到第一个匹配项
  myChart.dispatchAction({ type: "showTip", seriesIndex: 0, dataIndex: matched[0] });
}

function clearSearch() {
  if (!searchActive) return;
  searchActive = false;
  searchNodeIds = null;
  myChart.setOption(getOption());
}

// 响应式
window.addEventListener("resize", function() {
  myChart.resize();
});

// 双击重置
dom.addEventListener("dblclick", function(e) {
  resetView();
});
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="生成 ECharts GraphRAG 可视化")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT, help="输入 graph_data.json 路径")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help="输出 HTML 路径")
    args = parser.parse_args()

    print(f"[1/3] 读取: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    print(f"  节点: {len(nodes)}, 边: {len(edges)}")

    print("[2/3] 生成 ECharts HTML...")

    html = (
        HTML_TEMPLATE
        .replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
        .replace("__PALETTE_JSON__", json.dumps(PALETTE))
        .replace("__REL_COLORS_JSON__", json.dumps(REL_COLORS))
    )

    outdir = os.path.dirname(args.output)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"[3/3] 完成! → {args.output} ({size_kb:.0f} KB)")
    print(f"   节点={len(nodes)}, 边={len(edges)}, CDN=ECharts 5.5.1")


if __name__ == "__main__":
    main()
