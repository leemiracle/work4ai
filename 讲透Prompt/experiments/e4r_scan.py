#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E4-R 错误相关性扫描：SC 什么时候有害？（12 章期权 5）
==================================================================================
E4 反例（相遇题 5:4 投错）的假设：错误**同源**（系统性偏差）时 SC 有害，错误**独立**时 SC 有益。
设计：两组题各 4 道 × greedy + 9 采样：
  clean 组：多步计算但语义无歧义（错误应当五花八门 → SC 应受益）
  trap 组：有系统性陷阱（整数偏好/单位/题意歧义 → 错误应当抱团 → SC 受害）
每题记录：greedy 对错、9 采样票型 top-share（最高票占比）、多数票对错。
判据假设：top-share 高 & 多数票错 → 系统性偏差（SC 危险区）
产出：results/e4r_scan.json + e4r_scan.png
"""
from common import glm, save
import re, time
from collections import Counter

CLEAN = [  # 语义无歧义，多步计算
    ("一项工程甲队单独做10天完成，乙队单独做15天完成，两队合作需要几天完成？", 6),
    ("小明早上以每小时6千米的速度步行2小时，然后以每小时10千米的速度骑车1.5小时。全程共走了多少千米？", 27),
    ("一件商品成本200元，标价400元，打7折出售。利润是多少元？", 80),
    ("一个长方体长5厘米宽4厘米高3厘米，表面积是多少平方厘米？", 94),
]
TRAP = [  # 系统性陷阱：整数偏好 / 单位 / 题意歧义
    ("甲乙两地相距360千米，快车每小时行60千米，慢车每小时行40千米，两车同时相向而行，几小时后相遇？（允许小数）", 3.6),  # 整数偏好陷阱（E4 同款）
    ("一根绳子长3米，先剪去1.5米，再剪去剩下的1/3。这根绳子还剩多少米？", 1.0),  # "1/3 是全长的还是剩下的"歧义
    ("商品先涨价50%再降价50%，最终价格是原价的百分之几？", 75),  # 直觉 100% 陷阱
    ("小明今年12岁，爸爸年龄是他的3倍。几年后爸爸年龄是小明的2倍？", 12),  # 试值偏好陷阱
]

PROMPT = "{q}\n请一步一步思考，最后单独一行写'答案是：X'。"

def parse_answer(out):
    m = re.findall(r"答案[是为：:]*\s*(-?\d+(?:\.\d+)?)", out)
    if m: return m[-1]
    nums = re.findall(r"-?\d+(?:\.\d+)?", out)
    return nums[-1] if nums else None

def to_f(p):
    try: return float(p)
    except: return None

res = {"rows": []}
for group, tasks in [("clean", CLEAN), ("trap", TRAP)]:
    for q, gold in tasks:
        r = glm("glm-4-flash", PROMPT.format(q=q), max_tokens=512, temperature=0.1, retries=1)
        g_ok = abs((to_f(parse_answer(r["content"])) or -999) - gold) < 1e-6
        vals = []
        for _ in range(9):
            r = glm("glm-4-flash", PROMPT.format(q=q), max_tokens=512, temperature=0.8, retries=1)
            v = to_f(parse_answer(r["content"]))
            if v is not None: vals.append(round(v, 3))
            time.sleep(0.05)
        c = Counter(vals)
        top, cnt = (c.most_common(1)[0] if c else (None, 0))
        maj_ok = abs(top - gold) < 1e-6 if top is not None else False
        row = {"group": group, "q": q[:16], "gold": gold, "greedy": g_ok,
               "top": top, "top_share": cnt / max(len(vals), 1),
               "uniq": len(c), "maj_ok": maj_ok,
               "votes": dict(c.most_common(4))}
        res["rows"].append(row)
        print(f"  [{group}] {q[:14]}… gold={gold} greedy={g_ok} top={top}({cnt}/9) "
              f"maj={'✓' if maj_ok else '✗'} 票型={dict(c.most_common(3))}", flush=True)

import statistics as st
for g in ("clean", "trap"):
    rows = [r for r in res["rows"] if r["group"] == g]
    res[f"summary_{g}"] = {
        "greedy_acc": sum(r["greedy"] for r in rows) / len(rows),
        "maj_acc": sum(r["maj_ok"] for r in rows) / len(rows),
        "avg_top_share": st.mean(r["top_share"] for r in rows),
        "avg_uniq": st.mean(r["uniq"] for r in rows)}
    s = res[f"summary_{g}"]
    print(f"== {g}: greedy {s['greedy_acc']:.0%} → 多数票 {s['maj_acc']:.0%} | "
          f"平均 top-share {s['avg_top_share']:.2f} | 平均不同答案数 {s['avg_uniq']:.1f}", flush=True)

save("e4r_scan", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, metric, title in [(axes[0], "top_share", "票型集中度（top-share）"), (axes[1], "uniq", "不同答案数（多样性）")]:
    data = [[r[metric] for r in res["rows"] if r["group"] == g] for g in ("clean", "trap")]
    bp = ax.boxplot(data, labels=["clean 组\n(语义无歧义)", "trap 组\n(系统性陷阱)"], patch_artist=True)
    for patch, col in zip(bp["boxes"], ["#55A868", "#C44E52"]): patch.set_facecolor(col)
    ax.set_title(title); ax.grid(axis="y", alpha=.3)
plt.suptitle("E4-R：错误相关性扫描——trap 组票型更集中（错误抱团）", y=1.02)
plt.tight_layout(); plt.savefig("results/e4r_scan.png", dpi=130, bbox_inches="tight")
print("[saved] results/e4r_scan.png")
