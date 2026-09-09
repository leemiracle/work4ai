#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""magent_analyze.py — 多 Agent 拓扑实验分析（控制机本地跑，读 traces.jsonl + summary.json）

产出：
  1. 拓扑×难度通过率矩阵 + 预算效率（calls/tokens per solved）
  2. 失败模式量化：同质趋同 / 认知投降 / 权威收敛 / 循环失控 / 错误类型分布
  3. T2b 角色分化检验（persona → 输出长度/tactic 分布）
"""
import json, sys
from collections import Counter, defaultdict

TRACES = sys.argv[1] if len(sys.argv) > 1 else "traces.jsonl"
SUMMARY = sys.argv[2] if len(sys.argv) > 2 else "summary.json"

events = [json.loads(l) for l in open(TRACES)]
ver = [e for e in events if e.get("verify_ok") is not None]   # 带验证结果的记录
try:
    S = json.load(open(SUMMARY)); results = S["results"]
except Exception:
    results = []

print(f"events={len(events)} verified_records={len(ver)} "
      f"ptok={sum(e['prompt_toks'] for e in events)} ctok={sum(e['completion_toks'] for e in events)}")

# ---- 1. 拓扑×难度通过率 ----
print("\n== 1. 拓扑 × 难度通过率 ==")
mat = defaultdict(lambda: [0, 0])
for r in results:
    k = (r["topology"], r["level"])
    mat[k][1] += 1
    if r["solved"]: mat[k][0] += 1
print(f"{'topology':<10} {'L1':>6} {'L2':>6} {'L3':>6} {'total':>8} {'calls/solved':>12} {'toks/solved':>12}")
agg = defaultdict(lambda: [0, 0, 0, 0])
for (topo, lvl), (ok, n) in sorted(mat.items()):
    agg[topo][0] += ok; agg[topo][1] += n
for topo in sorted(agg):
    ok, n = agg[topo][0], agg[topo][1]
    calls = sum(r["calls"] for r in results if r["topology"] == topo)
    toks = sum(r.get("wall_s", 0) for r in results if r["topology"] == topo)
    tok_used = sum(e["prompt_toks"] + e["completion_toks"] for e in ver if e["topology"] == topo)
    lv = "/".join(f"{mat[(topo,l)][0]}/{mat[(topo,l)][1]}" for l in (1,2,3) if (topo,l) in mat)
    eff = f"{calls/ok:.1f}" if ok else "inf"
    teff = f"{tok_used/ok:.0f}" if ok else "inf"
    print(f"{topo:<10} {lv:>12} {ok}/{n:>6} {eff:>12} {teff:>12}")

# ---- 2. 失败模式 ----
print("\n== 2. 失败模式量化 ==")
# 2a. 同质趋同（T3）：8 采样的唯一证明数
u = [r["unique_proofs"] for r in results if r["topology"] == "indep"]
if u: print(f"[同质趋同-T3] unique/8 = {u} → mean {sum(u)/len(u):.2f}（8=完全多样, 1=完全趋同）")
# 2b. T2 辩论修订：identical_to_self / follow_first
ids = [r["identical_to_self"] for r in results if r["topology"] == "debate"]
ff = [r["follow_first_agent"] for r in results if r["topology"] == "debate"]
if ids:
    print(f"[认知投降-debate] revised==self: {sum(ids)}/{3*len(ids)} ({sum(ids)/(3*len(ids)):.0%})")
    print(f"[权威收敛-debate] revised==agent-A: {sum(ff)}/{3*len(ff)} ({sum(ff)/(3*len(ff)):.0%})")
    r1 = sum(1 for r in results if r["topology"]=="debate" and r.get("solved_round1"))
    ra = sum(1 for r in results if r["topology"]=="debate" and r["solved"])
    print(f"[辩论增益] round1 pass {r1} → +修订 pass {ra}（增益 {'+' if ra>r1 else ''}{ra-r1}）")
ids2 = [r["identical_to_self"] for r in results if r["topology"] == "role"]
if ids2: print(f"[认知投降-role] revised==self: {sum(ids2)}/{3*len(ids2)}")
# 2c. T1 循环失控：相邻轮 solver 输出相同
t1ev = [e for e in ver if e["topology"] == "manager" and e["agent"] == "solver"]
loops = 0
for p in set(e["prob"] for e in t1ev):
    seq = [e["out_norm"] for e in sorted([e for e in t1ev if e["prob"] == p], key=lambda x: x["call_idx"])]
    for a, b in zip(seq, seq[1:]):
        if a and a == b: loops += 1
print(f"[循环失控-manager] 相邻轮证明完全相同: {loops} 次")
# 2d. 错误类型分布（全部失败验证）
errs = Counter()
for e in ver:
    if e["verify_ok"] is False:
        r = e["verify_reason"]
        if r == "sorry": errs["sorry(未完成)"] += 1
        elif "timeout" in r: errs["lean超时"] += 1
        elif "unknown identifier" in r or "unknown constant" in r: errs["未知标识符"] += 1
        elif "application of function" in r or "type mismatch" in r: errs["类型不匹配"] += 1
        elif "unsolved goals" in r: errs["未解决目标"] += 1
        elif "syntax" in r: errs["语法错误"] += 1
        else: errs["其他"] += 1
print(f"[错误类型分布] {dict(errs)}")

# ---- 3. T2b 角色分化 ----
print("\n== 3. 角色偏置（信息不对称微实验） ==")
role_ev = [e for e in ver if e["topology"] == "role" and e["agent"].startswith("solver-")]
if role_ev:
    by = defaultdict(list)
    for e in role_ev: by[e["agent"]].append(e)
    for a, es in sorted(by.items()):
        lens = [len(e["out_norm"]) for e in es]
        tactics = Counter(t for e in es for t in
                          ("induction", "simp", "omega", "decide", "rw ", "exact", "ring", "linarith", "constructor")
                          if t in e["out_norm"])
        top3 = ", ".join(f"{k}×{v}" for k, v in tactics.most_common(3))
        print(f"  {a:<22} 输出均值长 {sum(lens)/len(lens):6.0f} | tactics: {top3}")
else:
    print("  （无 role 事件）")

# ---- 4. 每 call 延迟与 token 概况 ----
lat = [e["latency_s"] for e in events if e["latency_s"] > 0]
if lat:
    lat.sort()
    print(f"\n[延迟] n={len(lat)} p50={lat[len(lat)//2]:.1f}s max={lat[-1]:.1f}s")
print("\n== summary（来自远端） ==")
if results:
    for r in results[:5]: print(" ", {k: v for k, v in r.items() if k != "first_error"})
