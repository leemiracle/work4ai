#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
季节性需求与峰荷定价（对应 00 章✨美之时刻 / 02 章 RevPAR / 03 章峰荷定理 /
04 章走廊①）。纯 numpy。

模型：酒店双季市场（旺季/淡季各 1 单位时段），运营边际成本 0，
容量成本 r=25/单位（按峰值容量一次投入）：
  旺季需求 Q_h = 100 - p_h；淡季需求 Q_l = 60 - p_l
  容量 K = max(Q_h, Q_l)；利润 Π = p_h·Q_h + p_l·Q_l - r·K

对比（闭式，见 03 章推导）：
  统一定价（p 两季同价）：p=46.25, K=53.75, Π=1778.125, W=3317.19
  峰荷分价：p_l=30, p_h=62.5, K=37.5, Π=2306.25, W=3459.375
断言：
  A. 两组闭式与数值格点最优一致
  B. 分价利润↑、所需容量↓（省 30%）、总福利↑ —— 效率与利润同向
  C. 分价价格序：p_h > p_统一 > p_l
  D. 12 个月正弦负荷演示：容量按峰值定 -> 谷底闲置率的数量级
"""
import numpy as np

Qh = lambda p: 100 - p
Ql = lambda p: 60 - p
r = 25.0

# ---------- A. 两组定价的闭式与格点复核 ----------
# 统一定价：max_p  p*(Qh+Ql) - r*max(Qh,Ql)；Qh>Ql 恒成立（p<=60 时）
def profit_uniform(p):
    return p * (Qh(p) + Ql(p)) - r * Qh(p)   # 峰值=旺季
p_grid = np.linspace(0.01, 60, 600_001)
prof_u = np.array([profit_uniform(p) for p in p_grid[::60]])  # 粗扫
p_u_num = p_grid[::60][int(np.argmax(prof_u))]
# 闭式：d/dp [p(160-2p) - r(100-p)] = 160-4p+r = 0 -> p=(160+r)/4=46.25
p_u = (160 + r) / 4
K_u = Qh(p_u); PI_u = profit_uniform(p_u)
W_u = PI_u + 0.5 * (100 - p_u) ** 2 + 0.5 * (60 - p_u) ** 2    # 利润+两季CS
print(f"[A1] 统一定价: p={p_u:.4f}, K={K_u:.4f}, Pi={PI_u:.4f}, W={W_u:.4f} "
      f"(格点 p={p_u_num:.4f})")
assert abs(p_u - 46.25) < 1e-12 and abs(K_u - 53.75) < 1e-12
assert abs(PI_u - 1778.125) < 1e-9
assert abs(p_u_num - p_u) < 0.2, "统一价格点复核失败"

# 峰荷分价：淡季 p_l=30（无容量费，纯垄断最优点）；旺季 p_h=(100+r)/2=62.5
p_l = 30.0
p_h = (100 + r) / 2
K_p = Qh(p_h); PI_p = p_h * Qh(p_h) + p_l * Ql(p_l) - r * K_p
W_p = PI_p + 0.5 * (100 - p_h) ** 2 + 0.5 * (60 - p_l) ** 2
# 数值复核：双变量粗格点
pg = np.linspace(5, 90, 86)
PH, PL = np.meshgrid(pg, pg, indexing="ij")
mask = (Qh(PH) >= Ql(PL)) & (Qh(PH) >= 0) & (Ql(PL) >= 0)
P_profit = np.where(mask, PH * Qh(PH) + PL * Ql(PL) - r * np.maximum(Qh(PH), Ql(PL)), -1e9)
i, j = np.unravel_index(int(np.argmax(P_profit)), P_profit.shape)
print(f"[A2] 峰荷分价: p_h={p_h:.4f}, p_l={p_l:.4f}, K={K_p:.4f}, "
      f"Pi={PI_p:.4f}, W={W_p:.4f} (格点 p_h={pg[i]:.1f}, p_l={pg[j]:.1f})")
assert abs(p_h - 62.5) < 1e-12 and abs(K_p - 37.5) < 1e-12
assert abs(PI_p - 2306.25) < 1e-9
assert abs(pg[i] - p_h) < 1.5 and abs(pg[j] - p_l) < 1.5, "分价格点复核失败"

# ---------- B. 三重比较 ----------
d_K = (K_u - K_p) / K_u
print(f"\n[B] 利润: {PI_u:.2f} -> {PI_p:.2f} (+{(PI_p/PI_u-1):.1%})")
print(f"[B] 容量: {K_u:.2f} -> {K_p:.2f} (-{d_K:.1%})  —— 峰值投资省下三成")
print(f"[B] 总福利: {W_u:.2f} -> {W_p:.2f} (+{(W_p/W_u-1):.2%})")
assert PI_p > PI_u, "分价利润应上升"
assert K_p < K_u - 10, "分价所需容量应显著下降"
assert abs(d_K - 0.3023) < 0.01, "容量节省应约 30%"
assert W_p > W_u, "分价总福利应上升（统一价的容量错配被释放）"
# 分价后淡季价格必须低于运营成本之上的任何统一价——容量费不记淡季账
assert p_l < p_u < p_h, "价格序应为 p_l < p_统一 < p_h"

# ---------- C. 价格序断言（含在 B 中打印） ----------
print(f"[C] 价格序: 淡季 {p_l:.2f} < 统一 {p_u:.2f} < 旺季 {p_h:.2f} —— "
      f"容量账单寄给高峰")

# ---------- D. 12 个月正弦负荷演示 ----------
months = np.arange(1, 13)
demand_m = 50 + 25 * np.sin(2 * np.pi * (months - 4) / 12)   # 峰在 7 月
capacity = demand_m.max()
util = demand_m / capacity
print(f"\n[D] 正弦月度需求: 峰值 {demand_m.max():.0f} (7月), 谷值 "
      f"{demand_m.min():.0f} (1月)")
print(f"[D] 按峰值定容 -> 年均利用率 {util.mean():.1%}, 谷月仅 {util.min():.1%}")
print("    [D 表] " + " ".join(f"{u:.0%}" for u in util))
assert 0.65 < util.mean() < 0.68, "正弦负荷年均利用率应为 2/3 邻域"
assert abs(util.min() - 1/3) < 1e-9 and util.max() == 1.0

print("\n[ALL ASSERTS PASSED] 峰荷定价三重红利：利润↑30%、容量投资↓30%、"
      "总福利↑——")
print("『全年最贵的那间房和最空的那间房是同一间』，分价让这间房的账本各归各位。")
