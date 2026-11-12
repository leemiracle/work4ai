#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E1 参数实验：temperature / top_p 对输出的影响（指南 introduction/settings 的实证）
==============================================================================
问题：指南说"temperature 越小越确定，越大越随机"——到底有多确定/多随机？
设计（本地 Qwen2.5-0.5B，可控可复现）：
  A. 开放生成多样性：prompt="用一句话描写春天。" × 12 次采样
     temperature ∈ {0.0(贪心), 0.7, 1.5} → 统计互异输出数（去空白后）
  B. 事实任务稳定性：prompt="把'书'翻译成英文，只输出单词。" × 12 次 → 正确率/一致率
  C. top_p 核采样：temperature=1.2 固定，top_p ∈ {0.1, 0.9, 1.0} × 12 次 → 互异数
产出：results/e1_params.json + e1_params.png
"""
from common import local_qwen, save
from collections import Counter

OPEN_P = "用一句话描写春天。"
FACT_P = "把中文词翻译成英文，只输出英文单词，不要其它内容。\n词：书"
N = 12

def diversity(temp, top_p=1.0):
    outs = local_qwen(OPEN_P, max_new_tokens=30, temperature=temp, top_p=top_p,
                      num_return=N)
    outs = [o.strip().split("\n")[0] for o in outs]
    return outs, len(set(outs))

def fact_stability(temp, top_p=1.0):
    outs = local_qwen(FACT_P, max_new_tokens=6, temperature=temp, top_p=top_p,
                      num_return=N)
    outs = [o.strip().split()[0].strip(".,。") if o.strip() else "" for o in outs]
    acc = sum(o.lower().startswith("book") for o in outs) / N
    return outs, acc, Counter(outs).most_common(1)[0][0]

res = {"meta": {"model": "Qwen2.5-0.5B-Instruct(local CPU)", "N": N, "seed": 42},
       "A_temperature_diversity": {}, "B_fact_stability": {}, "C_top_p": {}}

print("== A. temperature → 开放生成多样性 ==")
for t in [0.0, 0.7, 1.5]:
    outs, d = diversity(t)
    res["A_temperature_diversity"][str(t)] = {"distinct": d, "examples": outs[:3]}
    print(f"  temp={t}: 互异输出 {d}/{N}")

print("== B. temperature → 事实任务稳定性 ==")
for t in [0.0, 0.7, 1.5]:
    outs, acc, mode = fact_stability(t)
    res["B_fact_stability"][str(t)] = {"acc": acc, "mode": mode,
                                       "dist": dict(Counter(outs))}
    print(f"  temp={t}: 正确率 {acc:.0%}，众数 {mode!r}")

print("== C. top_p（temperature=1.2 固定）→ 核采样截断 ==")
for p in [0.1, 0.9, 1.0]:
    outs, d = diversity(1.2, top_p=p)
    res["C_top_p"][str(p)] = {"distinct": d, "examples": outs[:3]}
    print(f"  top_p={p}: 互异输出 {d}/{N}")

save("e1_params", res)

# ---- 可视化 ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
ts = ["0.0", "0.7", "1.5"]
axes[0].bar(ts, [res["A_temperature_diversity"][t]["distinct"] for t in ts],
            color="#4C72B0")
axes[0].set_title("A 温度→开放生成互异数"); axes[0].set_xlabel("temperature")
axes[1].bar(ts, [res["B_fact_stability"][t]["acc"] for t in ts], color="#55A868")
axes[1].set_title("B 温度→翻译正确率"); axes[1].set_xlabel("temperature")
axes[1].set_ylim(0, 1.05)
ps = ["0.1", "0.9", "1.0"]
axes[2].bar(ps, [res["C_top_p"][p]["distinct"] for p in ps], color="#C44E52")
axes[2].set_title("C top_p→互异数(temp=1.2)"); axes[2].set_xlabel("top_p")
for ax in axes: ax.set_ylabel("互异输出数 / 正确率")
plt.tight_layout(); plt.savefig("results/e1_params.png", dpi=130)
print("[saved] results/e1_params.png")
