#!/usr/bin/env python3
"""E5 · 每跳精度乘法灾难（per-hop accuracy multiplicative collapse）

讲透Graph Ch07 的核心实验（行为模拟，非 LLM 实验——诚实标注）。
动机：图遍历的链路正确率 = 每跳准确率的连乘。vanja.io 的工程格言：
"数 hops，别数 top-10"——本实验把这句格言变成数字。

三问：
  Q1 链路正确率：每跳 p，k 跳链整体走对的概率 p^k 是多少？
  Q2 期望重试：要走通一次 k 跳链，平均要试多少次？（几何分布 1/p^k）
  Q3 对照：单跳 top-10 检索命中 0.90 vs 5 跳图遍历每跳 0.98，谁赢？

输出：experiments/E5_result.json + E5_perhop.png
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Q1/Q2: 链路正确率与期望重试 ----
hops = list(range(1, 11))          # 1..10 跳
per_hop = [0.99, 0.95, 0.90, 0.80]  # 每跳准确率
chain = {p: [round(p ** k, 4) for k in hops] for p in per_hop}
retries = {p: [round(1 / p ** k, 1) for k in hops] for p in per_hop}

# ---- Q3: 单跳检索 vs 图遍历 对照 ----
# 扁平检索：top-10 命中率 0.90，一次到位
# 图遍历：5 跳，每跳 0.98（单看每跳几乎完美）
flat_hit, graph_k, graph_p = 0.90, 5, 0.98
graph_hit = graph_p ** graph_k
verdict = "图遍历赢" if graph_hit > flat_hit else "扁平检索赢"

# ---- 控制台报告 ----
print("=" * 72)
print("E5 · 每跳精度乘法灾难")
print("=" * 72)
print(f"{'k跳':>4} | " + " | ".join(f"p={p:<5}" for p in per_hop) + "   (链路正确率)")
print("-" * 72)
for i, k in enumerate(hops):
    print(f"{k:>4} | " + " | ".join(f"{chain[p][i]:<7.4f}" for p in per_hop))
print("-" * 72)
print(f"{'期望重试次数 (试几次能走通一次):':>30}")
for i, k in enumerate(hops):
    if k in (1, 3, 5, 8, 10):
        print(f"  k={k:>2}: " + " | ".join(f"p={p}: {retries[p][i]:<8.1f}" for p in per_hop))
print("-" * 72)
print(f"Q3 对照: 单跳top-10命中 {flat_hit:.2f}  vs  {graph_k}跳×每跳{graph_p} = {graph_hit:.4f} → {verdict}")
print("结论: 每跳 0.98 的『几乎完美』在 5 跳后只剩 ~" + f"{graph_hit:.0%}"
      + "；长链先救单跳精度或缩短链路，再谈别的。")

# ---- 图: 双子图 ----
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8))
for p in per_hop:
    ax1.plot(hops, chain[p], marker="o", ms=4, label=f"每跳 p={p}")
ax1.axhline(0.5, color="gray", ls="--", lw=0.8)
ax1.text(9.6, 0.52, "50% 抛硬币线", fontsize=8, color="gray", ha="right")
ax1.set_xlabel("链长 k（跳数）")
ax1.set_ylabel("链路正确率 $p^k$")
ax1.set_title("乘法灾难：每跳 0.9，10 跳只剩 %.1f%%" % (100 * 0.9 ** 10))
ax1.legend(fontsize=8)
ax1.grid(alpha=0.3)

for p in per_hop:
    ax2.semilogy(hops, retries[p], marker="s", ms=4, label=f"每跳 p={p}")
ax2.set_xlabel("链长 k（跳数）")
ax2.set_ylabel("期望重试次数（对数轴）")
ax2.set_title("走通一次的期望试验次数 $1/p^k$")
ax2.legend(fontsize=8)
ax2.grid(alpha=0.3, which="both")

fig.suptitle("E5 · 图遍历的可靠性是链式乘法——数 hops，别数 top-10", fontsize=12)
fig.tight_layout()
png = os.path.join(HERE, "E5_perhop.png")
fig.savefig(png, dpi=130)

result = {
    "experiment": "E5 per-hop accuracy multiplicative collapse",
    "type": "行为模拟（非 LLM 实验）",
    "hops": hops,
    "per_hop": per_hop,
    "chain_accuracy": chain,
    "expected_retries": retries,
    "Q3_flat_vs_graph": {
        "flat_top10_hit": flat_hit,
        "graph": {"hops": graph_k, "per_hop": graph_p, "chain_hit": round(graph_hit, 4)},
        "verdict": verdict,
    },
    "highlights": {
        "p0.90_k10": round(0.9 ** 10, 4),
        "p0.95_k8": round(0.95 ** 8, 4),
        "p0.99_k8": round(0.99 ** 8, 4),
        "p0.80_k8_retry": round(1 / 0.8 ** 8, 1),
    },
    "png": os.path.basename(png),
}
with open(os.path.join(HERE, "E5_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n落盘: E5_result.json + E5_perhop.png")
