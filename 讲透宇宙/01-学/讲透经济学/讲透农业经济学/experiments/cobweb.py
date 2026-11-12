#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蛛网模型：为什么农产品价格会"画蜘蛛网"（对应 00 章 §2 / 03 章 §2 / 04 章走廊①）。

Ezekiel（1938）：农产品供给决策在生产前做出、收入在后——
本期供给量由上期价格决定（天真预期），本期价格由本期供需决定：
  Q_s,t = a_s + b_s·P_{t-1}（播种决策看去年的价）
  Q_d,t = a_d − b_d·P_t（收获时价格让市场出清）
⇒ 一阶差分 P_{t+1} = (a_d − a_s − b_s·P_t)/b_d，特征根 λ = −b_s/b_d。

断言：
  A. 收敛区制（b_s<b_d）：价格振荡收敛于闭式稳态 P*，且每期振幅按 |λ|=b_s/b_d 精确衰减；
  B. 临界区制（b_s=b_d）：等幅永久振荡（|λ|=1，二周期环）；
  C. 发散区制（b_s>b_d）：振幅指数放大——需求越刚性（b_d 小）越易发散，
     这解释"猪周期"为何剧烈：猪肉需求价格弹性低；
  D. 适应性预期（ λ_e 调整）可驯服发散：把"看去年的价"换成"逐步修正预期"，
     2×2 线性系统谱半径 <1，模拟收敛。
参数：需求 Q=100−2P（b_d=2），供给截距 a_s=10。
"""
import numpy as np

a_d, b_d, a_s = 100.0, 2.0, 10.0

def cobweb(b_s, P0, T, adaptive=None):
    """天真预期动力系统；adaptive=λ_e 时用适应性预期（返回价格序列）。"""
    P = np.empty(T + 1); P[0] = P0
    if adaptive is None:
        for t in range(T):
            P[t + 1] = (a_d - a_s - b_s * P[t]) / b_d
    else:
        lam = adaptive
        e = P0                                  # 供给方预期价格
        for t in range(T):
            P[t] = (a_d - a_s - b_s * e) / b_d
            e = e + lam * (P[t] - e)
        P[T] = (a_d - a_s - b_s * e) / b_d
    return P

def steady(b_s):
    return (a_d - a_s) / (b_d + b_s)            # 闭式稳态

P0 = 45.0

print("== A. 收敛区制（b_s=1，供给比需求平缓）==")
b_s = 1.0
P = cobweb(b_s, P0, 40); Ps = steady(b_s)
print(f"  稳态 P* = (a_d−a_s)/(b_d+b_s) = {Ps:.2f}，模拟末值 {P[-1]:.6f}")
assert abs(P[-1] - Ps) < 1e-6
err = np.abs(P[1:6] - Ps)
ratios = (P[4:20] - Ps) / (P[3:19] - Ps)        # 一步比 = 特征根 λ = −b_s/b_d
assert np.allclose(ratios, -b_s / b_d, atol=1e-9), "振幅每期按 |b_s/b_d| 精确衰减"
print(f"  振幅每期乘 |λ| = b_s/b_d = {b_s/b_d:.2f}（精确特征根，非拟合）")

print("\n== B. 临界区制（b_s=2，|λ|=1）==")
P = cobweb(2.0, P0, 40); Ps = steady(2.0)
amp = np.abs(P[10:] - Ps)
assert np.allclose(amp, abs(P0 - Ps), atol=1e-9), "等幅振荡，振幅永不衰减"
print(f"  P*={Ps:.2f} 上下 {abs(P0 - Ps):.2f} 的永久二周期环：丰收价跌→减产价涨→又丰收")

print("\n== C. 发散区制（b_s=3.5，需求刚性）==")
P = cobweb(3.5, P0, 12); Ps = steady(3.5)
print(f"  P* = {Ps:.2f}（理论稳态存在却不可及）")
print("  轨迹: " + " → ".join(f"{p:.1f}" for p in P))
assert np.abs(P[-1] - Ps) > 10 * np.abs(P0 - Ps), "振幅指数放大"
print(f"  12 期后偏离放大到初偏离的 {np.abs(P[-1] - Ps) / np.abs(P0 - Ps):.0f} 倍")
print("  反直觉：使周期爆炸的不是供给刚性，而是需求刚性——猪肉没有替代品，")
print("  供给稍多价格就暴跌（b_d 小→分母小→振幅大）——'猪贱伤农'与'猪贵伤民'交替")

print("\n== D. 适应性预期驯服发散（b_s=3.5 保持不变）==")
lam = 0.3
M = np.array([[-b_s * lam / b_d, -b_s * (1 - lam) / b_d],
              [lam, 1 - lam]])                  # 状态 (P_t, e_t)
rho = max(abs(np.linalg.eigvals(M)))
P = cobweb(3.5, P0, 60, adaptive=lam)
print(f"  2×2 系统谱半径 ρ = {rho:.3f} < 1 → 收敛；模拟末值 {P[-1]:.4f} vs P* = {steady(3.5):.2f}")
assert rho < 1 and abs(P[-1] - steady(3.5)) < 1e-3
print("  养殖户不再'看去年的价'而是逐步修正预期，同样的供给弹性下市场自稳——")
print("  信息与预期形成机制本身就是稳定政策（能繁母猪存栏量公开发布的制度逻辑）")

print("\nALL ASSERTIONS PASSED")
