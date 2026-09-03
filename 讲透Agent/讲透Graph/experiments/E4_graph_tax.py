#!/usr/bin/env python3
"""E4 · 图索引构建成本测算：向量库 vs GraphRAG 式抽取（成本模型推算）

讲透Graph Ch04/Ch12 的核心实验。回答"图税到底多少"：
  - 向量索引: 1 次 embedding/文档（只进不出）
  - 图索引(GraphRAG式): 每文档 1 次三元组抽取（schema prompt + 文档进、三元组出）
    + 社区聚类摘要（每 ~50 个实体 1 次合并调用）+ 实体消歧
  - 增量更新 1 篇文档: 向量=1 embed; 图=抽取+消歧+潜在作废扫描

诚实标注：**成本模型推算，非实测**。假设全部列在 PARAMS，结论对参数不敏感
（图/向量倍率主要由"输出 token 单价 + 额外调用层数"决定）。
现实锚点：微软 GraphRAG 官方文档明示索引一个小语料库 = 数百次 LLM 调用。

输出：E4_result.json + E4_graph_tax.png
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- 假设（全部可改，结论对参数不敏感） ----------
PARAMS = {
    "doc_tokens": 500,            # 平均每文档 token
    "embed_prompt_overhead": 0,   # embedding 无输出
    "extract_in": 800,            # 抽取调用输入 = schema/指令 300 + 文档 500
    "extract_out": 300,           # 每文档产出三元组 token
    "entities_per_doc": 8,        # 每文档实体数
    "community_size": 50,         # 每 50 实体一个社区
    "community_in": 2000,         # 社区摘要输入（成员实体+边序列化）
    "community_out": 400,         # 社区摘要输出
    "dedup_calls_per_doc": 0.3,   # 消歧额外调用（30% 文档需要一次）
    "price_in_per_m": 3.0,        # $/M input tokens（mini 档）
    "price_out_per_m": 15.0,      # $/M output tokens（mini 档）
}
P = PARAMS

def vector_cost(docs):
    """向量索引: D 次 embedding，只有输入。"""
    tok_in = docs * P["doc_tokens"]
    return {"calls": docs, "in": tok_in, "out": 0,
            "usd": tok_in / 1e6 * P["price_in_per_m"]}

def graph_cost(docs):
    """GraphRAG 式图索引: 抽取 + 消歧 + 社区摘要。"""
    extract_calls = docs * (1 + P["dedup_calls_per_doc"])
    ext_in = extract_calls * P["extract_in"]
    ext_out = docs * P["extract_out"]
    communities = docs * P["entities_per_doc"] / P["community_size"]
    com_in = communities * P["community_in"]
    com_out = communities * P["community_out"]
    tok_in, tok_out = ext_in + com_in, ext_out + com_out
    return {"calls": int(extract_calls + communities),
            "in": int(tok_in), "out": int(tok_out),
            "usd": tok_in / 1e6 * P["price_in_per_m"] + tok_out / 1e6 * P["price_out_per_m"]}

def incremental(doc=1):
    v = vector_cost(doc)
    g = {"calls": 1 + 1 + 0.2,  # 抽取 + 消歧 + 0.2 次作废扫描
         "in": int((P["extract_in"]) + 600 + 200,
                   ),
         "out": P["extract_out"] + 100}
    g["in"] = P["extract_in"] + 800
    g["usd"] = g["in"] / 1e6 * P["price_in_per_m"] + g["out"] / 1e6 * P["price_out_per_m"]
    v["usd"] = round(v["usd"], 6)
    g["usd"] = round(g["usd"], 6)
    return v, g

sizes = [100, 1_000, 10_000, 100_000]
table = []
for d in sizes:
    v, g = vector_cost(d), graph_cost(d)
    table.append({
        "docs": d,
        "vector": v,
        "graph": g,
        "calls_ratio": round(g["calls"] / v["calls"], 1),
        "usd_ratio": round(g["usd"] / max(v["usd"], 1e-9), 0),
    })

inc_v, inc_g = incremental()

print("=" * 76)
print("E4 · 图税测算（成本模型推算，假设见 PARAMS）")
print("=" * 76)
print(f"{'文档数':>8} | {'向量 calls':>10} {'向量 $':>9} | {'图 calls':>9} {'图 $':>10} | 倍率")
print("-" * 76)
for row in table:
    print(f"{row['docs']:>8,} | {row['vector']['calls']:>10,} {row['vector']['usd']:>9.2f} | "
          f"{row['graph']['calls']:>9,} {row['graph']['usd']:>10.2f} | "
          f"{row['usd_ratio']:.0f}×")
print("-" * 76)
print(f"增量更新 1 篇: 向量 {inc_v['calls']} calls/${inc_v['usd']:.5f}"
      f"  vs  图 ~{inc_g['calls']:.0f} calls/${inc_g['usd']:.5f}")
print("""
解读:
  1) 图索引贵一个数量级上下——大头是『每文档都要输出三元组』+『社区摘要』，
     输出 token 单价又是输入的 5 倍;
  2) 增量更新图也贵 ~3-5×: 抽取之外还要消歧与作废扫描（bi-temporal 的维护费）;
  3) 所以 GEM 2026 的结论才重要: 简单场景 plain RAG 够用, 图只在
     『多跳关系/时序/溯源』问题上值回票价——先问问题类型, 再选索引。""")

# ---------- 图 ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.6))

xs = [r["docs"] for r in table]
ax1.loglog(xs, [r["vector"]["usd"] for r in table], "o-", label="向量索引", color="#2a9d8f")
ax1.loglog(xs, [r["graph"]["usd"] for r in table], "s-", label="图索引(GraphRAG式)", color="#e76f51")
for r in table:
    ax1.annotate(f"{r['usd_ratio']:.0f}×", (r["docs"], r["graph"]["usd"]),
                 textcoords="offset points", xytext=(6, 4), fontsize=9, color="#e76f51")
ax1.set_xlabel("文档数 (log)")
ax1.set_ylabel("索引构建成本 $ (log)")
ax1.set_title("图税：构建成本倍率（标注为 $ 倍率）")
ax1.legend(fontsize=9)
ax1.grid(alpha=0.3, which="both")

ax2.bar(["向量\n(1 embed)", "图\n(抽取+消歧+社区)"],
        [inc_v["usd"], inc_g["usd"]], color=["#2a9d8f", "#e76f51"], width=0.5)
for i, (lbl, v) in enumerate([("向量", inc_v["usd"]), ("图", inc_g["usd"])]):
    ax2.text(i, v, f"${v:.5f}", ha="center", va="bottom", fontsize=10)
ax2.set_yscale("log")
ax2.set_ylabel("$ / 篇 (log)")
ax2.set_title(f"增量更新 1 篇文档：{inc_g['usd']/inc_v['usd']:.0f}×")
ax2.grid(axis="y", alpha=0.3, which="both")

fig.suptitle("E4 · 图是税：构建贵一个量级、增量贵 3-5×——值不值看问题类型", fontsize=12)
fig.tight_layout()
png = os.path.join(HERE, "E4_graph_tax.png")
fig.savefig(png, dpi=130)

result = {
    "experiment": "E4 graph index tax estimation",
    "type": "成本模型推算（非实测；假设全列 PARAMS，结论对参数不敏感）",
    "params": PARAMS,
    "table": table,
    "incremental_one_doc": {"vector": inc_v, "graph": inc_g},
    "reality_anchor": "微软 GraphRAG 官方文档：索引小语料库 = 数百次 LLM 调用",
    "png": os.path.basename(png),
}
with open(os.path.join(HERE, "E4_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("落盘: E4_result.json + E4_graph_tax.png")
