#!/usr/bin/env python3
"""lab10 · PCTL 定量检查：线性方程组与价值迭代（10 章 §三/§四）。
E1 DTMC：s0 --0.5--> s0, --0.3--> s1(target), --0.2--> s2(死态)。
   手推锚点（10 章 §三）：p0 = 0.5·p0 + 0.3 ⇒ p0 = 0.6——DTMC 的 P(F φ) 是解线性方程组，
   不是采样估计；np.linalg.solve 与手推逐位一致。
E2 MDP：s0 上动作 A{0.5 s0, 0.3 s1, 0.2 s2} 与 B{0.9 s0, 0.1 s2}。
   手推锚点：max 概率 = 恒选 A ⇒ 同样 0.6（B 把概率漏进死态，任何混合都不优于 A）；
   价值迭代逐轮逼近 0.6（打印前几轮的值，章内手推块对照）。
E3 PCTL 语义：P≥0.6 [F target] 为真 / P>0.6 [F target] 为假——定量保证的"边界"现场。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
import numpy as np


def dtmc_reach(Q, r):
    """解 (I−Q)p = r。Q: 瞬态子矩阵（非吸收态间的转移），r: 一步进入 target 的概率列。"""
    n = Q.shape[0]
    return np.linalg.solve(np.eye(n) - Q, r)


def mdp_reach(actions, n, target, dead, tol=1e-12, trace=None):
    """价值迭代：p[s] = max_a Σ_t P_a[s,t]·p[t]；p[target]=1、p[dead]=0 不更新。"""
    p = np.zeros(n)
    p[target] = 1.0
    it = 0
    while True:
        q = p.copy()
        for s in range(n):
            if s in (target, dead):
                continue
            p[s] = max(float(a[s] @ q) for a in actions)
        it += 1
        if trace is not None and it <= 5:
            trace.append((it, p.copy()))
        if np.max(np.abs(p - q)) < tol:
            return p


print("=" * 68)
print("E1 · DTMC：P(F target) = 解线性方程组")
print("=" * 68)
print("模型：s0 --0.5--> s0（自环），--0.3--> s1=target，--0.2--> s2=死态")
print("手推（10 章 §三）：p0 = 0.5·p0 + 0.3  ⇒  0.5·p0 = 0.3  ⇒  p0 = 0.6")
Q = np.array([[0.5]])            # 瞬态子矩阵：只有 s0
r = np.array([0.3])              # s0 一步跳进 target 的概率
p0 = dtmc_reach(Q, r)[0]
print(f"  np.linalg.solve((I−Q), r) → p0 = {p0:.10f}（vs 手推 0.6，|偏差| {abs(p0 - 0.6):.1e}）")
assert abs(p0 - 0.6) < 1e-12
print("→ E1 自检通过：方程组解与手推逐位一致——模型检查是【算】出来的，不是采样采出来的")

print("\n" + "=" * 68)
print("E2 · MDP：max 概率 = 价值迭代（调度器 = 策略）")
print("=" * 68)
A = np.array([[0.5, 0.3, 0.2], [0, 1, 0], [0, 0, 1]])   # 动作 A：有 0.3 直达 target
B = np.array([[0.9, 0.0, 0.1], [0, 1, 0], [0, 0, 1]])   # 动作 B：永远到不了 target
trace = []
p = mdp_reach([A, B], 3, target=1, dead=2, trace=trace)
print("手推（10 章 §四）：动作 B 把概率漏进死态 ⇒ 任何混合都不优于恒选 A ⇒ max p0 = 0.6")
for it, vals in trace:
    print(f"  第 {it} 轮：p = ({vals[0]:.6f}, {vals[1]:.0f}, {vals[2]:.0f})")
print(f"  收敛：p0 = {p[0]:.10f}（vs 手推 0.6，|偏差| {abs(p[0] - 0.6):.1e}）")
assert abs(p[0] - 0.6) < 1e-9
print("→ E2 自检通过：MDP 的定量检查 = 对动作取 max 的不动点迭代（与 13 章 μ-演算同一思想）")

print("\n" + "=" * 68)
print("E3 · PCTL 的定量语义：边界现场")
print("=" * 68)
print(f"  P>=0.6 [F target]：{p0 >= 0.6}（恰在边界上成立）")
print(f"  P>0.6  [F target]：{p0 > 0.6 + 1e-12}（严格大于不成立）")
print("  —— P≤p 这类定量保证是'算出精确概率再比大小'，与 SAT 的'有/无反例'是两种世界观（50 章的 P 格 vs NP 格）")
assert p0 >= 0.6 and not p0 > 0.6 + 1e-12
print("\nlab10 全部自检通过")
