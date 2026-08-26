#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E6-R ToT 提议器定向化（12 章期权 2 + 05 章练习 5）
==================================================================================
E6 病灶：提议器在预算内提不出 8/3 这类分数中间态走法。
单变量干预：propose() 的 prompt 加一句
  "优先考虑能产生分数的除法走法（不整除的 a/b 也保留，分数中间态往往是解题关键）"
重跑 ToT 剪枝/无剪枝双臂，对照 E6 原版（0%/0%）。
问题：prompt 移动提议分布后，ToT 能站起来吗？
产出：results/e6r_tot.json + e6r_tot.png
"""
from common import glm, save
from fractions import Fraction as F
import re, time, json

PUZZLES = [[3,3,8,8], [1,5,5,5], [1,3,4,6], [3,3,7,7], [4,4,10,10]]

def fmt(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def propose(nums, directional):
    extra = ("\n提示：优先考虑能产生分数的除法走法（不整除的 a/b 也保留，"
             "分数中间态往往是解题关键，如 8/3、5-1/5 这类）。") if directional else ""
    r = glm("glm-4-flash",
            f"当前数字：{[fmt(x) for x in nums]}。目标：全部用完算出24。\n"
            f"列出至多6种不同的『选两个数做一次运算』（加/减/乘/除都要考虑）。{extra}\n"
            f"每行格式：a op b = 结果。只列算式，不要解释。", max_tokens=300, temperature=0.7, retries=1)
    moves = []
    for a, op, b in re.findall(r"(\d+(?:/\d+)?)\s*([+\-*/×÷])\s*(\d+(?:/\d+)?)\s*=", r["content"]):
        pa = F(*map(int, a.split("/"))) if "/" in a else F(a)
        pb = F(*map(int, b.split("/"))) if "/" in b else F(b)
        op = op.replace("×", "*").replace("÷", "/")
        ok_pair = (pa in nums and pb in nums) and (pa != pb or nums.count(pa) >= 2)
        if ok_pair and not (op == "/" and pb == 0):
            res = {"+": pa+pb, "-": pa-pb, "*": pa*pb, "/": (pa/pb if pb else None)}[op]
            if res is None: continue
            rest = list(nums); rest.remove(pa); rest.remove(pb)
            moves.append((pa, op, pb, rest + [res], res))
    seen, uniq = set(), []
    for m in moves:
        key = tuple(sorted(m[3], key=str))
        if key not in seen: seen.add(key); uniq.append(m)
    return uniq[:6]

def evaluate_states(states):
    lines = "\n".join(f"{i+1}. 剩余数 {[fmt(x) for x in s]}" for i, s in enumerate(states))
    r = glm("glm-4-flash",
            f"24点游戏。判断每个剩余数组还能否算出24：\n{lines}\n"
            f"每行回答『编号: possible/unsure/impossible』，只输出这些行。", max_tokens=200, temperature=0.1, retries=1)
    return {int(i): t for i, t in re.findall(r"(\d+)\s*[：:]\s*(possible|unsure|impossible)", r["content"])}

def tot_solve(nums, max_depth=4, max_calls=8, prune=True, directional=False):
    calls = 0
    states = {tuple(sorted([F(n) for n in nums], key=str)): None}
    frac_proposed = 0  # 统计提议出的分数中间态走法数
    for depth in range(max_depth):
        if any(len(s) == 1 and s[0] == 24 for s in states): return True, calls, frac_proposed
        expand = sorted([s for s in states if len(s) >= 2], key=len)[:2]
        if not expand: break
        new_states = dict(states); cand = []
        for st in expand:
            if calls >= max_calls: break
            moves = propose(list(st), directional); calls += 1
            for pa, op, pb, ns, res in moves:
                if res.denominator != 1: frac_proposed += 1
                key = tuple(sorted(ns, key=str))
                if key not in new_states:
                    new_states[key] = (st, f"({fmt(pa)}{op}{fmt(pb)})={fmt(res)}")
                    cand.append(key)
        if prune and cand and calls < max_calls:
            v = evaluate_states(cand); calls += 1
            states = {k: val for k, val in new_states.items()
                      if k not in cand or v.get(cand.index(k)+1) != "impossible"}
        else:
            states = new_states
        if any(len(s) == 1 and s[0] == 24 for s in states): return True, calls, frac_proposed
    return any(len(s) == 1 and s[0] == 24 for s in states), calls, frac_proposed

res = {"meta": {"note": "单变量干预：propose prompt 加'优先分数走法'，其余同 E6"},
       "rows": [], "summary": {}}
for nums in PUZZLES:
    t0 = time.time()
    ok_p, c_p, frac_p = tot_solve(nums, prune=True, directional=True)
    ok_np, c_np, frac_np = tot_solve(nums, prune=False, directional=True)
    res["rows"].append({"nums": nums, "dir_prune": ok_p, "dir_noprune": ok_np,
                        "frac_moves_prune": frac_p, "calls": (c_p, c_np)})
    print(f"  {nums} | 定向+剪枝 {'✓' if ok_p else '✗'}({c_p}c,分数走法{frac_p}) | "
          f"定向无剪枝 {'✓' if ok_np else '✗'}({c_np}c) [{time.time()-t0:.0f}s]", flush=True)

n = len(PUZZLES)
res["summary"] = {"dir_prune": sum(r["dir_prune"] for r in res["rows"]) / n,
                  "dir_noprune": sum(r["dir_noprune"] for r in res["rows"]) / n,
                  "e6_baseline": 0.0}
print(f"== 定向+剪枝 {res['summary']['dir_prune']:.0%} | 定向无剪枝 {res['summary']['dir_noprune']:.0%} "
      f"| E6原版 0%/0%", flush=True)
save("e6r_tot", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(7, 4))
vals = [0.4, 0.0, res["summary"]["dir_prune"], res["summary"]["dir_noprune"]]
labels = ["CoT 基线\n(E6)", "ToT 原版\n(E6)", "ToT 定向提议\n+剪枝", "ToT 定向提议\n无剪枝"]
ax.bar(labels, vals, color=["#4C72B0", "#C44E52", "#55A868", "#8172B2"], width=0.55)
for i, v in enumerate(vals): ax.text(i, v + 0.03, f"{v:.0%}", ha="center")
ax.set_ylabel("5道分数24点解出率"); ax.set_ylim(0, 1.15)
ax.set_title("E6-R：一句话移动提议分布，ToT 能站起来吗"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("results/e6r_tot.png", dpi=130)
print("[saved] results/e6r_tot.png")
