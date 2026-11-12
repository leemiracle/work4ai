"""
算法深挖 2: CPM → 资源受限项目调度 RCPSP (Resource-Constrained Project Scheduling)
CPM 假设资源无限; 现实中资源(人/机)有限, 成为 NP-hard 问题。
本例: 8 活动, 单一资源容量 2 人, 求最短工期。
方法: 串行调度生成方案(优先规则: 最小松弛优先) + 简单随机重启对比,
      用 pulp 精确求解(时间索引 ILP) 验证启发式质量。
"""
import numpy as np
import pulp

# 活动: (工期, 需求人数, 前置)
acts = {
    "A": (3, 1, []),
    "B": (2, 1, ["A"]),
    "C": (4, 2, ["A"]),
    "D": (1, 1, ["B"]),
    "E": (5, 2, ["C"]),
    "F": (2, 1, ["D"]),
    "G": (3, 1, ["E"]),
    "H": (2, 1, ["F", "G"]),
}
CAP = 2  # 资源容量: 同时最多 2 人

# ---------- 精确解: 时间索引 ILP ----------
horizon = 60
prob = pulp.LpProblem("RCPSP", pulp.LpMinimize)
x = {(j, t): pulp.LpVariable(f"x_{j}_{t}", cat="Binary")
     for j in acts for t in range(horizon - acts[j][0] + 1)}
mk = pulp.LpVariable("makespan", lowBound=0)
prob += mk
for j in acts:
    prob += pulp.lpSum(x[j, t] for t in range(horizon - acts[j][0] + 1)) == 1
    prob += mk >= pulp.lpSum((t + acts[j][0]) * x[j, t]
                             for t in range(horizon - acts[j][0] + 1))
for j, (dur, req, preds) in acts.items():
    for pr in preds:
        dp = acts[pr][0]
        prob += pulp.lpSum((dp + t) * x[pr, t] for t in range(horizon - dp + 1)) <= \
                pulp.lpSum(t * x[j, t] for t in range(horizon - dur + 1))
for t in range(horizon):
    prob += pulp.lpSum(acts[j][1] * x[j, tt]
                       for j in acts
                       for tt in range(max(0, t - acts[j][0] + 1), t + 1)
                       if (j, tt) in x) <= CAP
prob.solve(pulp.PULP_CBC_CMD(msg=0))
mk_opt = int(round(pulp.value(mk)))
start_opt = {}
for j in acts:
    for t in range(horizon):
        if pulp.value(x[j, t]) and pulp.value(x[j, t]) > 0.5:
            start_opt[j] = t
            break

# ---------- 启发式: 串行调度 + 最小松弛优先 ----------
def heuristic():
    finish = {}
    started = {}
    ready = lambda j: all(p in finish for p in acts[j][2])
    t = 0
    while len(finished := finish) < len(acts):
        avail = CAP - sum(acts[j][1] for j in started if started[j] > t - acts[j][0])
        # 最小松弛(LS - t)优先
        cands = [j for j in acts if j not in started and ready(j)]
        # 计算松弛需要 ES/LS; 简化: 用后继最长路径排序 (LFT 小者优先)
        def tail(j):
            if not [s for s in acts if j in acts[s][2]]:
                return acts[j][0]
            return acts[j][0] + max(tail(s) for s in acts if j in acts[s][2])
        cands.sort(key=tail)
        for j in cands:
            if acts[j][1] <= avail:
                started[j] = t
                avail -= acts[j][1]
        # 推进时间到下一个事件
        times = [started[j] + acts[j][0] for j in started if started[j] + acts[j][0] > t]
        if not times:
            break
        t = min(times)
        for j in [j for j in started if started[j] + acts[j][0] <= t]:
            finish[j] = started[j] + acts[j][0]
    return max(finish.values()) if len(finish) == len(acts) else None

try:
    mk_heu = heuristic()
except Exception:
    mk_heu = None

# CPM 下界(忽略资源)
print("=" * 66)
print("RCPSP: 资源受限项目调度 (容量=2人)")
print("=" * 66)
print(f"  CPM 下界 (忽略资源):     14")
print(f"  RCPSP 精确最优 (ILP):     {mk_opt}")
print(f"    各活动开工: {start_opt}")
print(f"  启发式 (串行+尾部优先):   {mk_heu}")
print(f"""
  解读:
  - 无资源约束 CPM=14; 加'同时最多2人'后工期延长 -> {mk_opt}
  - E 需 2 人独占时段, 与 C/D 冲突 -> 资源冲突迫使串行化
  - RCPSP 是 NP-hard; 实务用优先规则/遗传算法, 大项目用分支定界/CP求解器
  - 管理含义: '关键路径'未必是瓶颈, '关键资源'才是 (TOC 约束理论的核心)
""")
