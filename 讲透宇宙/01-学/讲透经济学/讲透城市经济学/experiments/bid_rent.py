#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alonso 竞租模型：单中心城市的土地分配（对应 00 章 §2 / 03 章 §2 / 04 章走廊①）。

三个用地者在距中心 x 处的竞租曲线（指数衰减，交通/通勤成本越高衰减越快）：
  商务 R_c = 100·exp(-1.2x) | 住宅 R_h = 60·exp(-0.5x) | 工业 R_m = 35·exp(-0.25x)
农业用地只出保底租金 R_ag = 4。均衡 = 三条曲线的上包络，交点即用地边界。
断言：
  A. 均衡租金（上包络）随距离严格递减——离中心越近地越贵，是结果不是原因；
  B. 用地顺序 = 通勤/运输强度排序：商务→住宅→工业→农业（四环结构）；
  C. 边界距离由相邻曲线交点闭式解给出，数值残差≈0；
  D. 政策实验（通勤成本下降，b_h: 0.5→0.35）：住宅竞租变平 → 城市外扩、
     边缘租金上涨、中心（住宅部分）相对贬值——竞租模型版"郊区化"。
"""
import numpy as np

A_c, b_c = 100.0, 1.20
A_h, b_h = 60.0, 0.50
A_m, b_m = 35.0, 0.25
R_ag = 4.0

Rc = lambda x: A_c * np.exp(-b_c * x)
Rh = lambda x, b=b_h: A_h * np.exp(-b * x)
Rm = lambda x: A_m * np.exp(-b_m * x)

# ---------- 均衡 = 上包络 ----------
def envelope(x, b=b_h):
    x = np.atleast_1d(np.asarray(x, dtype=float))
    return np.maximum.reduce([Rc(x), Rh(x, b), Rm(x), np.full_like(x, R_ag)])

x = np.linspace(0, 12, 2401)
env = envelope(x)

# A. 单调递减
diffs = np.diff(env)
assert (diffs <= 1e-12).all(), "均衡租金应随距离非增"
print(f"[A] 均衡租金从中心 {env[0]:.1f} 单调衰减到远郊 {env[-1]:.1f}（=农业租金 {R_ag}）")

# B. 用地顺序：四环
def winner(x0, b=b_h):
    vals = {"商务": Rc(x0), "住宅": Rh(x0, b), "工业": Rm(x0), "农业": R_ag}
    return max(vals, key=vals.get)

rings = [(0.0, "商务"), (1.5, "住宅"), (4.0, "工业"), (10.0, "农业")]
print("[B] 用地环带:", " → ".join(f"x={xi:.1f}:{w}" for xi, w in rings))
for xi, w in rings:
    assert winner(xi) == w, f"x={xi} 应为 {w}，实为 {winner(xi)}"
assert b_c > b_h > b_m, "衰减率排序 = 通勤/运输强度排序（竞租模型的发动机）"

# C. 边界闭式解：相邻曲线交点
def crossing(A1, b1, A2, b2):
    return np.log(A1 / A2) / (b1 - b2)

x_ch, x_hm, x_mag = crossing(A_c, b_c, A_h, b_h), crossing(A_h, b_h, A_m, b_m), crossing(A_m, b_m, R_ag, 0.0)
print(f"[C] 边界: 商务|住宅 x={x_ch:.3f}, 住宅|工业 x={x_hm:.3f}, 工业|农业 x={x_mag:.3f}（城市半径）")
for xb, (f1, f2) in [(x_ch, (Rc, lambda x: Rh(x))), (x_hm, (lambda x: Rh(x), Rm)), (x_mag, (Rm, lambda x: np.full_like([xb], R_ag)))]:
    r1, r2 = np.atleast_1d(f1(xb)), np.atleast_1d(f2(xb))
    assert abs(r1[0] - r2[0]) < 1e-9, "边界处相邻竞租应相等"
assert 0 < x_ch < x_hm < x_mag, "边界应嵌套（否则环序崩塌）"

# ---------- D. 政策实验：通勤成本下降（b_h 0.5 → 0.35） ----------
b_new = 0.35
x_hm_new = crossing(A_h, b_new, A_m, b_m)
x_mag_new = crossing(A_m, b_m, R_ag, 0.0)
edge_old, edge_new = float(Rh(x_hm, b_h)), float(Rh(x_hm, b_new))
print(f"\n[D] 通勤成本下降（住宅竞租斜率 b_h {b_h}→{b_new}）：")
print(f"  住宅|工业边界外移: {x_hm:.3f} → {x_hm_new:.3f}（城市扩张 {x_hm_new - x_hm:+.3f}）")
print(f"  原工业环内缘（x={x_hm:.2f}）住宅租金: {edge_old:.1f} → {edge_new:.1f}（边缘升值 {edge_new - edge_old:+.1f}）")
print(f"  中心住宅租金不变 {A_h:.0f}（截距不动），但梯度变平 → 中心相对贬值")
assert x_hm_new > x_hm and edge_new > edge_old, "郊区化的两个签名：边界外移+边缘升值"

# 土地市场出清校验：均衡下每点租金 = 最高意愿支付（无套利）
mid = 3.0
assert abs(envelope(mid)[0] - max(Rc(mid), Rh(mid), Rm(mid), R_ag)) < 1e-9
print(f"\n均衡检验: 每一英里土地都归出价最高者，租金 = 次高意愿之上的赢家通吃价——")
print(f"城市没有'中心崇拜'，只有'省下来的通勤费愿意换成多少租金'。")
print("\nALL ASSERTIONS PASSED")
