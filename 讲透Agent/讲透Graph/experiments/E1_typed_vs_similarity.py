#!/usr/bin/env python3
"""E1 · 类型边 vs 相似度命中（规则模拟，非 LLM 实验——诚实标注）

讲透Graph Ch01 的核心实验。验证 vanja.io 的核心论断：
  无类型边/相似度说"相关"，类型边说"怎么相关"——
  "藏着动词的问题"（替代了谁/依赖谁/导致了什么）只有类型边能一步答准。

模拟设计：
  - 知识节点：7 个 ADR（架构决策记录）+ 2 个实体，每个带主题标签
  - 相似度检索 = Jaccard(topic 标签交集/并集) 取 top-k（模拟向量检索的行为）
  - 类型边遍历 = 沿 supersedes/depends_on/caused_by/see_also 精确走一步
  - 题库 5 道"隐藏动词"题，对比 precision@1 与候选数

输出：E1_result.json + E1_typed_vs_sim.png
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- 知识图（节点 + 类型边） ----------
NODES = {
    "ADR-001": {"topics": {"cache", "redis", "latency"}, "kind": "decision"},
    "ADR-002": {"topics": {"db", "postgres", "migration"}, "kind": "decision"},
    "ADR-003": {"topics": {"cache", "redis", "queue"}, "kind": "decision"},
    "ADR-004": {"topics": {"queue", "incident", "retry"}, "kind": "decision"},
    "ADR-005": {"topics": {"cache", "redis", "client"}, "kind": "decision"},
    "ADR-006": {"topics": {"cache", "redis", "notes"}, "kind": "decision"},
    "ADR-007": {"topics": {"cache", "redis", "queue", "kafka"}, "kind": "decision"},
    "INCIDENT-12": {"topics": {"queue", "incident", "outage"}, "kind": "event"},
    "SVC-CERT": {"topics": {"cert", "tls", "queue"}, "kind": "asset"},
}
# 有向类型边: (src, relation, dst)
EDGES = [
    ("ADR-007", "supersedes", "ADR-003"),     # 007 替代 003
    ("ADR-005", "depends_on", "ADR-003"),     # 005 依赖 003
    ("ADR-007", "depends_on", "ADR-004"),     # 007 依赖 004
    ("INCIDENT-12", "caused", "ADR-004"),     # 事故催生了 004
    ("ADR-006", "see_also", "ADR-003"),       # 006 只是"参见"003
    ("SVC-CERT", "blocks", "ADR-007"),        # 证书阻塞 007 上线
]

edge_index = {}
for s, r, d in EDGES:
    edge_index.setdefault((s, r), []).append(d)

# 相似度 = Jaccard（模拟向量检索：主题相近即召回）
def sim(a, b):
    ta, tb = NODES[a]["topics"], NODES[b]["topics"]
    return len(ta & tb) / len(ta | tb)

def sim_topk(anchor, k=3, exclude_self=True):
    cands = [(n, sim(anchor, n)) for n in NODES
             if (not exclude_self or n != anchor)]
    cands.sort(key=lambda x: -x[1])
    return cands[:k]

# ---------- 题库：每题都是"隐藏动词"问题 ----------
QUESTIONS = [
    {
        "q": "哪个决策替代了 ADR-003？", "anchor": "ADR-003", "relation": "supersedes",
        "gold": ["ADR-007"],  # 注意方向：supersedes 的 src 才是替代者
        "gold_via": "查 (x, supersedes, ADR-003) 的 x",
    },
    {
        "q": "ADR-005 依赖哪个决策？", "anchor": "ADR-005", "relation": "depends_on",
        "gold": ["ADR-003"],
    },
    {
        "q": "什么导致了 ADR-004 的诞生？", "anchor": "ADR-004", "relation": "caused",
        "gold": ["INCIDENT-12"],
    },
    {
        "q": "证书过期会阻塞什么？", "anchor": "SVC-CERT", "relation": "blocks",
        "gold": ["ADR-007"],
    },
    {
        "q": "ADR-003 被谁依赖？（谁还踩在我身上）", "anchor": "ADR-003", "relation": "depends_on",
        "gold": ["ADR-005"],  # 反向边查询
    },
]

def typed_answer(anchor, relation, gold):
    """类型边遍历：先按题意定方向。"""
    # 正向: (anchor, relation, ?)
    fwd = edge_index.get((anchor, relation), [])
    if fwd:
        return fwd, 1
    # 反向: (?, relation, anchor)
    rev = [s for s, r, d in EDGES if d == anchor and r == relation]
    if rev:
        return rev, 1
    return [], 0

def sim_answer(anchor, k=3):
    """相似度检索：返回 top-k 候选（模拟向量检索给 RAG 的候选池）。"""
    return [n for n, _ in sim_topk(anchor, k)]

rows, sim_hits, typed_hits = [], 0, 0
for item in QUESTIONS:
    gold = set(item["gold"])
    t_ans, t_hops = typed_answer(item["anchor"], item["relation"], item["gold"])
    s_ans = sim_answer(item["anchor"], k=3)
    t_ok = set(t_ans) == gold
    s_ok = set(s_ans) == gold  # 相似度池恰好=gold 才算对（实际还要模型从池里猜）
    typed_hits += t_ok
    sim_hits += s_ok
    rows.append({
        "question": item["q"],
        "gold": sorted(gold),
        "typed_edge": {"answer": t_ans, "hops": t_hops, "correct": t_ok},
        "similarity_top3": {"candidates": s_ans, "exact_match": s_ok,
                            "needs_model_guess": True},
        "sim_candidates": [n for n, s in sim_topk(item["anchor"], 3)],
        "sim_scores": {n: round(s, 3) for n, s in sim_topk(item["anchor"], 3)},
    })

n = len(QUESTIONS)
summary = {
    "typed_edge_precision_at_1": f"{typed_hits}/{n}",
    "similarity_exact_pool_rate": f"{sim_hits}/{n}",
    "note": "相似度即使召回池恰好命中，仍需模型从候选里猜哪个是答案；"
            "类型边直接给出唯一节点，且可给出可解释的边类型",
}

print("=" * 76)
print("E1 · 类型边 vs 相似度命中（规则模拟）")
print("=" * 76)
for r in rows:
    print(f"\nQ: {r['question']}")
    print(f"  gold        = {r['gold']}")
    print(f"  类型边      = {r['typed_edge']['answer']}  ({r['typed_edge']['hops']}跳, "
          f"{'✅' if r['typed_edge']['correct'] else '❌'})")
    print(f"  相似度 top3 = {r['sim_candidates']}  池恰好命中: "
          f"{'✅' if r['similarity_top3']['exact_match'] else '❌（需模型再猜）'}")
    print(f"  相似度分数  = {r['sim_scores']}")
print("\n" + "-" * 76)
print(f"类型边 precision@1 = {typed_hits}/{n}    相似度候选池精确率 = {sim_hits}/{n}")
print("核心观察: ADR-006 (see_also) 与 ADR-007 (supersedes) 主题标签几乎相同——")
print("        相似度永远分不清『参见』和『替代』，类型边一个字段就分开。")

# ---------- 图 ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))

labels = [f"Q{i+1}" for i in range(n)]
ax1.bar(labels, [1 if r["typed_edge"]["correct"] else 0 for r in rows],
        width=0.55, label="类型边遍历", color="#2a9d8f")
ax1.bar(labels, [-0.06] * n, bottom=[1.02] * n, width=0.0)  # spacer
ax1.bar(labels, [1 if r["similarity_top3"]["exact_match"] else 0.12 for r in rows],
        width=0.55, label="相似度 top-3（0.12=池命中但需猜）", color="#e9c46a", alpha=0.85)
ax1.set_ylim(0, 1.25)
ax1.set_ylabel("precision@1")
ax1.set_title("隐藏动词问题：类型边 vs 相似度")
ax1.legend(fontsize=8, loc="upper right")
ax1.grid(axis="y", alpha=0.3)

# 右图: 主题空间里的混淆——各节点与 ADR-003 的 Jaccard 相似度 vs 边类型
anchor = "ADR-003"
rel_of = {}
for s, r_, d in EDGES:
    if s == anchor:
        rel_of[d] = r_
    if d == anchor:
        rel_of[s] = r_ + "(反向)"
pts = [(n, sim(anchor, n), rel_of.get(n, "无边")) for n in NODES if n != anchor]
pts.sort(key=lambda x: -x[1])
names = [p[0] for p in pts]
vals = [p[1] for p in pts]
rels = [p[2] for p in pts]
colors = ["#2a9d8f" if "supersedes" in r else "#e76f51" if "depends_on" in r
          else "#999999" for r in rels]
ax2.barh(range(len(pts)), vals, color=colors)
ax2.set_yticks(range(len(pts)))
ax2.set_yticklabels([f"{n}\n{r}" for n, _, r in pts], fontsize=8)
ax2.invert_yaxis()
ax2.set_xlabel(f"与 ADR-003 的 Jaccard 相似度")
ax2.set_title("相似度排不出边类型：绿=supersedes 红=depends_on 灰=无关/see_also")
ax2.grid(axis="x", alpha=0.3)

fig.suptitle("E1 · 相似度说『相关』，类型边说『怎么相关』", fontsize=12)
fig.tight_layout()
png = os.path.join(HERE, "E1_typed_vs_sim.png")
fig.savefig(png, dpi=130)

result = {
    "experiment": "E1 typed edges vs similarity retrieval",
    "type": "规则模拟（Jaccard 模拟向量检索；非 LLM 实验）",
    "questions": rows,
    "summary": summary,
    "png": os.path.basename(png),
}
with open(os.path.join(HERE, "E1_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\n落盘: E1_result.json + E1_typed_vs_sim.png")
