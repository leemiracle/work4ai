#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拉弗曲线：弹性与收入峰值（对应 00 章反直觉速览 / 03 章拉弗峰 /
04 章走廊②）。纯 numpy。

模型：应税收入对净留成有常数弹性（劳动供给/避税/迁移），税率为 τ 时
基数 B(τ) = B0·(1−τ)^ε，税收 T(τ) = τ·B(τ)。峰值位置：
  τ* = 1/(1+ε)
  ε=0    -> 峰消失（单调：税率越高收入越高，无行为反应的世界）
  ε=0.4  -> τ* ≈ 71.4%（顶层收入弹性的 Saez 传统经验值）
  ε=1.0  -> τ* = 50%

断言：
  A. 三种弹性的格点峰 == 闭式 τ*（分辨率 < 0.005）
  B. ε=0 时 T(τ) 在区间内严格单调上升（无峰）
  C. ε=0.4 时：税率从 0.90 降到 0.70，收入不降反升（高税率区的拉弗命题）
"""
import numpy as np

B0 = 100.0
tau = np.linspace(0.0, 0.95, 1901)          # 分辨率 0.0005

def revenue(tau_grid, eps):
    return tau_grid * B0 * (1 - tau_grid) ** eps

# ---------- A. 峰位闭式 vs 格点 ----------
print("[A] 弹性 -> 收入峰值税率（闭式 1/(1+ε) vs 格点 argmax）")
for eps, expect in [(0.0, None), (0.4, 1 / 1.4), (1.0, 0.5)]:
    T = revenue(tau, eps)
    tau_hat = tau[int(np.argmax(T))]
    if expect is None:
        print(f"    ε={eps:.1f}: 格点峰在右边界 {tau_hat:.3f}（无峰，单调世界）")
        assert tau_hat == tau[-1], "ε=0 应单调递增至边界"
    else:
        print(f"    ε={eps:.1f}: 格点峰 {tau_hat:.4f} vs 闭式 {expect:.4f}")
        assert abs(tau_hat - expect) < 0.005, f"ε={eps} 峰位偏离闭式"

# ---------- B. ε=0 单调性 ----------
T0 = revenue(tau, 0.0)
diffs = np.diff(T0)
print(f"\n[B] ε=0: T(τ)=100τ 在 [0,0.95] 严格单调上升（增量最小 "
      f"{diffs.min():.4f} > 0）——峰完全是行为反应的产物")
assert (diffs > 0).all(), "ε=0 时应无内部峰"

# ---------- C. 高税率区：减税增收 ----------
T_04 = revenue(tau, 0.4)
T90 = 0.90 * B0 * (1 - 0.90) ** 0.4
T70 = 0.70 * B0 * (1 - 0.70) ** 0.4
T_pk = T_04.max()
print(f"\n[C] ε=0.4: T(0.90)={T90:.2f} < T(0.70)={T70:.2f} "
      f"（+{(T70/T90-1):.0%}）—— 高税率区减税增收")
assert T70 > T90 * 1.1, "0.70 税率收入应显著高于 0.90（拉弗命题现场）"
print(f"[C] 峰值收入 T_max={T_pk:.2f} @ τ={tau[int(np.argmax(T_04))]:.3f}"
      f"；税率越过峰后每加 1pp 都同时损失基数与收入")
assert T_pk >= T70 and T_pk >= T90

print("\n[ALL ASSERTS PASSED] 拉弗峰的位置只有一个参数说了算：弹性。")
print("ε→0 峰消失（单调世界），ε=0.4 峰在 71%——『税率之辩』的正确打开")
print("方式是『弹性之辩』：可税基数跑得越快，最优税率越低。")
