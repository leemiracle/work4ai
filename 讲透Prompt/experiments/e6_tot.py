#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E6 ToT 实验：24点游戏 BFS vs 平铺 CoT（Yao et al. 2023, 2305.10601）
==================================================================================
问题：需要"回头"的搜索题（分数中间态 8/(3-8/3)），一次性 CoT 和树搜索差距多大？
5 道全分数运算经典题（本地 Fraction 暴力验证可解）：
  [3,3,8,8] 8/(3-8/3)=24 | [1,5,5,5] 5*(5-1/5) | [1,3,4,6] 6/(1-3/4)
  [3,3,7,7] 7*(3+3/7)    | [4,4,10,10] (10*10-4)/4
设计：
  a) CoT 基线：每题 3 样本 T=0.7，抽末尾等式机械验证是否=24（裁判是 Fraction，不是模型）
  b) ToT mini：Python 驱动 BFS，模型只做两件事——提议下一步运算 / 评估剩余数可能性，
     每题模型调用 ≤8 次，深度 ≤4
产出：results/e6_tot.json + e6_tot.png
"""
from common import glm, save
from fractions import Fraction as F
from itertools import permutations
import re, time

PUZZLES = [[3,3,8,8], [1,5,5,5], [1,3,4,6], [3,3,7,7], [4,4,10,10]]

# ---------- 机械裁判：暴力验证可解性 ----------
def solvable(nums):
    def rec(xs):
        if len(xs) == 1:
            return xs[0] == 24
        for i in range(len(xs)):
            for j in range(len(xs)):
                if i == j: continue
                rest = [xs[k] for k in range(len(xs)) if k not in (i, j)]
                a, b = xs[i], xs[j]
                for r in (a+b, a-b, a*b) + ((a/b,) if b != 0 else ()):
                    if rec(rest + [r]): return True
        return False
    return rec([F(n) for n in nums])

# ---------- CoT 基线 ----------
COT_PROMPT = ("用数字 {nums} 通过加、减、乘、除和括号算出 24，每个数恰好用一次。\n"
              "请推理并给出完整算式，最后单独一行写'最终：(...) = 24'。")
def cot_solve(nums):
    """3 样本投票前的"任一解出"判定；等式机械验证（只允许数字和运算符字符）"""
    for _ in range(3):
        r = glm("glm-4-flash", COT_PROMPT.format(nums=nums), max_tokens=512, temperature=0.7)
        m = re.findall(r"最终[：:]\s*([0-9+\-*/().×÷\s]+?)=\s*24", r["content"])
        for expr in m:
            expr = expr.replace("×", "*").replace("÷", "/").strip().rstrip("=").strip()
            if not re.fullmatch(r"[0-9+\-*/().\s]+", expr): continue
            try:
                if eval(expr) == 24: return True, expr
            except Exception: pass
    return False, None

# ---------- ToT：模型提议 + 模型评估 + 机械裁判 ----------
def fmt(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def propose(nums):
    """让模型提议 ≤6 种第一步运算。返回 [(a, op, b)]，机械过滤非法组合。"""
    r = glm("glm-4-flash",
            f"当前数字：{[fmt(x) for x in nums]}。目标：全部用完算出24。\n"
            f"列出至多6种不同的『选两个数做一次运算』（包括做除法产生分数的走法）。\n"
            f"每行格式：a op b = 结果。只列算式，不要解释。", max_tokens=300, temperature=0.7)
    moves = []
    for a, op, b in re.findall(r"(\d+(?:/\d+)?)\s*([+\-*/×÷])\s*(\d+(?:/\d+)?)\s*=", r["content"]):
        pa = F(*map(int, a.split("/"))) if "/" in a else F(a)
        pb = F(*map(int, b.split("/"))) if "/" in b else F(b)
        op = op.replace("×", "*").replace("÷", "/")
        if pa in nums and pb in nums and pa != pb or (pa == pb and nums.count(pa) >= 2):
            if op == "/" and pb == 0: continue
            res = {"+": pa+pb, "-": pa-pb, "*": pa*pb, "/": (pa/pb if pb else None)}[op]
            if res is None: continue
            rest = list(nums); rest.remove(pa); rest.remove(pb)
            moves.append((pa, op, pb, rest + [res], res))
    # 去重（按新状态）
    seen, uniq = set(), []
    for m in moves:
        key = tuple(sorted(m[3], key=str))
        if key not in seen: seen.add(key); uniq.append(m)
    return uniq[:6]

def evaluate_states(states):
    """一次调用评估所有候选状态：每行 '编号: possible/unsure/impossible'。返回 {编号: 标签}"""
    lines = "\n".join(f"{i+1}. 剩余数 {[fmt(x) for x in s]}" for i, s in enumerate(states))
    r = glm("glm-4-flash",
            f"24点游戏。判断每个剩余数组还能否算出24（心算/估算即可）：\n{lines}\n"
            f"每行回答『编号: possible/unsure/impossible』，只输出这些行。", max_tokens=200, temperature=0.1)
    verdict = {}
    for i, tag in re.findall(r"(\d+)\s*[：:]\s*(possible|unsure|impossible)", r["content"]):
        verdict[int(i)] = tag
    return verdict

def tot_solve(nums, max_depth=4, max_calls=8, prune=True):
    calls = 0
    states = {tuple(sorted([F(n) for n in nums], key=str)): None}  # state -> 父(用于表达式回溯)
    for depth in range(max_depth):
        done = [s for s in states if len(s) == 1 and s[0] == 24]
        if done: return True, states, calls
        # 选 ≤2 个状态扩展（数字少的优先）
        expand = sorted([s for s in states if len(s) >= 2], key=len)[:2]
        if not expand: break
        new_states = dict(states)
        cand_states = []
        for st in expand:
            if calls >= max_calls: break
            moves = propose(list(st)); calls += 1
            for pa, op, pb, ns, res in moves:
                key = tuple(sorted(ns, key=str))
                if key not in new_states:
                    new_states[key] = (st, f"({fmt(pa)}{op}{fmt(pb)})={fmt(res)}")
                    cand_states.append(key)
        if prune and cand_states and calls < max_calls:
            v = evaluate_states(cand_states); calls += 1
            # 保留：旧状态 + possible/unsure 新状态；impossible 剔除
            states = {k: val for k, val in new_states.items()
                      if k not in cand_states or v.get(cand_states.index(k)+1) != "impossible"}
        else:
            states = new_states
        if any(len(s) == 1 and s[0] == 24 for s in states):
            return True, states, calls
    return any(len(s) == 1 and s[0] == 24 for s in states), states, calls

res = {"meta": {"model": "glm-4-flash", "puzzles": PUZZLES}, "rows": [], "summary": {}}

for nums in PUZZLES:
    ok_sol = solvable(nums)
    t0 = time.time()
    cot_ok, cot_expr = cot_solve(nums)
    tot_ok, _, tot_calls = tot_solve(nums)
    tot_np_ok, _, tot_np_calls = tot_solve(nums, prune=False)
    res["rows"].append({"nums": nums, "solvable": ok_sol,
                        "cot": cot_ok, "cot_expr": cot_expr,
                        "tot": tot_ok, "tot_calls": tot_calls,
                        "tot_noprune": tot_np_ok, "tot_noprune_calls": tot_np_calls})
    print(f"  {nums} 可解={ok_sol} | CoT {'✓' if cot_ok else '✗'} | "
          f"ToT {'✓' if tot_ok else '✗'}({tot_calls}c) | ToT无剪枝 {'✓' if tot_np_ok else '✗'}({tot_np_calls}c) [{time.time()-t0:.0f}s]", flush=True)

n = len(PUZZLES)
res["summary"] = {"cot_any3": sum(r["cot"] for r in res["rows"]) / n,
                  "tot": sum(r["tot"] for r in res["rows"]) / n,
                  "tot_noprune": sum(r["tot_noprune"] for r in res["rows"]) / n}
print(f"== CoT(3样本) {res['summary']['cot_any3']:.0%} | ToT(BFS+剪枝) {res['summary']['tot']:.0%} | "
      f"ToT(无剪枝) {res['summary']['tot_noprune']:.0%}", flush=True)
save("e6_tot", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(7, 4))
vals = [res["summary"]["cot_any3"], res["summary"]["tot"], res["summary"]["tot_noprune"]]
ax.bar(["CoT 基线\n（3样本任一解出）", "ToT\n（提议+评估+剪枝）", "ToT-无剪枝\n（纯提议BFS）"], vals,
       color=["#4C72B0", "#55A868", "#8172B2"], width=0.5)
for i, v in enumerate(vals): ax.text(i, v + 0.03, f"{v:.0%}", ha="center")
ax.set_ylabel("5道分数24点解出率"); ax.set_ylim(0, 1.15)
ax.set_title("E6 ToT：弱评估器把搜索变成了负资产"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("results/e6_tot.png", dpi=130)
print("[saved] results/e6_tot.png")
