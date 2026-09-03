#!/usr/bin/env python3
"""E6 · work4ai 图健康度实测（活案例：本仓库自己就是 proto-graph）

讲透Graph Ch10 的核心实验。把全仓 markdown 文件当作节点、文件间相对链接当作
类型未定化的边（vanja.io: "你的 wikilinks 就是边"），实测：

  1. 规模：节点数（.md 文件）、边数（指向仓内 .md 的相对链接）
  2. 孤儿率：入度=0 的非 README 文件占比（AGENTS.md 健康线: 孤儿率 <10%）
  3. Hub：入度 Top10（全仓的"交通枢纽"）
  4. 链接纪律：断链（指向不存在的 .md）数量

纯 stdlib 实现（不依赖 networkx）。输出: E6_result.json + 控制台摘要。
敏感目录（.gitignore 内）不入图：.agent/ dual-chat/ xkernel-llm-constraints/
.research/ .workbuddy-ai/ 及所有隐藏目录。
"""
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # work4ai 仓库根

EXCLUDE_DIRS = {
    ".git", ".agent", ".research", ".workbuddy-ai", "dual-chat",
    "xkernel-llm-constraints", "node_modules", "__pycache__", ".opencode",
}

# markdown 链接: [text](path.md) 或 [text](path.md#anchor)，排除 http 外链
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(?!https?://|#)([^)#\s]+\.md)(?:#[^)\s]*)?\s*\)", re.I)

nodes, edges_from = [], defaultdict(list)   # edges_from[src_rel] = [dst_rel,...]
broken = []                                  # 断链 [(src, dst_raw)]

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        nodes.append(rel)
        try:
            text = open(full, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in LINK_RE.finditer(text):
            dst_raw = m.group(1).strip()
            dst_full = os.path.normpath(os.path.join(dirpath, dst_raw))
            if os.path.isfile(dst_full):
                edges_from[rel].append(os.path.relpath(dst_full, ROOT))
            else:
                broken.append((rel, dst_raw))

# 外部克隆仓（自带 readme/内部链接，不是本仓自产知识卡）——单独分层，
# 否则会污染 AGENTS.md 健康线（健康线针对自产内容）。
EXTERNAL_PREFIX = ("Karpathy经典代码精读" + os.sep + "repos" + os.sep,)


def is_external(rel: str) -> bool:
    return rel.startswith(EXTERNAL_PREFIX)


def layer_stats(node_list, edge_list):
    """返回一层的图指标（节点/边/孤儿率/hub）。"""
    deg = Counter()
    for _, d in edge_list:
        deg[d] += 1
    orph = [n for n in node_list if deg[n] == 0 and os.path.basename(n) != "README.md"]
    return {
        "nodes": len(node_list),
        "edges": len(edge_list),
        "avg_in_degree": round(len(edge_list) / max(len(node_list), 1), 3),
        "orphan_non_readme": len(orph),
        "orphan_rate": f"{len(orph) / max(len(node_list), 1):.1%}",
        "healthy_lt_10pct": len(orph) / max(len(node_list), 1) < 0.10,
        "hubs_top10": deg.most_common(10),
    }


node_set = set(nodes)
all_edges = [(s, d) for s, ds in edges_from.items() for d in ds]

own_nodes = [n for n in nodes if not is_external(n)]
own_edges = [(s, d) for s, d in all_edges if not is_external(s) and not is_external(d)]
ext_nodes = [n for n in nodes if is_external(n)]

own = layer_stats(own_nodes, own_edges)
ext = layer_stats(ext_nodes, [(s, d) for s, d in all_edges if is_external(s) and is_external(d)])

# 孤儿按顶层目录聚类（Ch10 治理债定位：哪个知识单元欠了挂网债）
own_deg = Counter()
for _, d in own_edges:
    own_deg[d] += 1
own_orphans_all = [n for n in own_nodes if own_deg[n] == 0 and os.path.basename(n) != "README.md"]
orphans_by_topdir = Counter(n.split(os.sep)[0] for n in own_orphans_all)
own_by_topdir = Counter(n.split(os.sep)[0] for n in own_nodes)

result = {
    "experiment": "E6 work4ai proto-graph health check",
    "root": "work4ai (git repo, 脱敏目录已排除)",
    "date": "2026-08-26",
    "graph_full": {
        "nodes": len(nodes),
        "edges": len(all_edges),
        "density": round(len(all_edges) / (len(nodes) * (len(nodes) - 1)), 6),
        "avg_in_degree": round(len(all_edges) / len(nodes), 3),
    },
    "layer_own_content": own,          # 自产知识卡（对标 AGENTS.md 健康线）
    "layer_external_clones": ext,      # Karpathy经典代码精读/repos/ 等外部克隆
    "orphans_by_topdir": orphans_by_topdir.most_common(),
    "own_files_by_topdir": own_by_topdir.most_common(15),
    "note": "健康线只对标自产层：外部克隆仓的 readme 天然是叶子节点，计入会虚高孤儿率",
    "broken_links_total": len(broken),
    "orphan_samples_own": sorted(own_orphans_all)[:15],
    "broken_samples": broken[:10],
}
with open(os.path.join(HERE, "E6_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("=" * 72)
print("E6 · work4ai 图健康度实测（proto-graph 照镜子，双层统计）")
print("=" * 72)
print(f"[全图]   节点 {len(nodes)} · 边 {len(all_edges)} · 平均入度 {result['graph_full']['avg_in_degree']}"
      f" · 密度 {result['graph_full']['density']}")
print(f"[自产层] 节点 {own['nodes']} · 边 {own['edges']} · 平均入度 {own['avg_in_degree']}")
print(f"         孤儿 {own['orphan_non_readme']} 个 = {own['orphan_rate']}"
      f" → 健康线 <10%: {'✅ 达标' if own['healthy_lt_10pct'] else '❌ 超标'}")
print(f"[克隆层] 节点 {ext['nodes']} · 内部边 {ext['edges']}（外部语料，不参与健康线）")
print(f"\n断链（指向不存在的 .md，全图）: {len(broken)} 条")
print("\n孤儿按顶层目录 Top12（治理债排行）:")
for d, c in orphans_by_topdir.most_common(12):
    tot = own_by_topdir.get(d, 0)
    print(f"  {c:>4}/{tot:<4} ⊘ {d}（{c/tot:.0%} 孤儿率）")
print("\n自产层入度 Top10（知识卡宇宙的交通枢纽）:")
for n, d in own["hubs_top10"]:
    print(f"  {d:>4} ← {n}")
print("\n自产层孤儿样本（前 15，挂网补链的候选）:")
for n in result["orphan_samples_own"]:
    print(f"  ⊘ {n}")
print("\n落盘: E6_result.json")
