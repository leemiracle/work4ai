#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财政乘数三连测（对应 00 章✨美之时刻 Haavelmo / 03 章凯恩斯交叉与稳定器 /
04 章走廊①）。纯 numpy。

模型：凯恩斯交叉 Y = C + I + G，C = c·(Y − T)；c = 0.8，I = 100。
  A. 一次性总量税（T0=50）：支出乘数 = 1/(1−c) = 5
     ΔG=10 -> ΔY = 50（迭代 200 步收敛断言）
  B. 比例税（T = 0.25·Y）：乘数 = 1/(1−c(1−t)) = 1/0.4 = 2.5
     自动稳定器：投资冲击 ±10 的产出振幅从 100 压到 50（减半）
  C. Haavelmo（1945）：ΔG = ΔT = 10 同时加 -> ΔY = 10 恰（乘数恒为 1，
     与 c 无关的恒等式：1/(1−c) − c/(1−c) = 1）
"""
import numpy as np

c, I0, T0, G_base = 0.8, 100.0, 50.0, 200.0

def converge(dI=0.0, dG=0.0, dT=0.0, t=0.0, steps=300, Y_init=0.0):
    """凯恩斯交叉迭代：dT 为一次性税增量，t 为比例税率（总量税取 0）。"""
    Y = Y_init
    for _ in range(steps):
        Y = c * (1 - t) * Y + (I0 + dI + G_base + dG - c * (T0 + dT))
    return Y

# ---------- A. 一次性总量税：乘数 = 5 ----------
Y_before = converge()
Y_after = converge(dG=10.0)
mult_lump = (Y_after - Y_before) / 10.0
Y_closed = (I0 + G_base - c * T0) / (1 - c)
print(f"[A] 总量税世界: Y={Y_before:.4f}（闭式 {Y_closed:.4f}）; "
      f"ΔG=10 -> Y={Y_after:.4f}, 乘数={mult_lump:.4f}（闭式 1/(1-c)=5）")
assert abs(Y_before - Y_closed) < 1e-6, "迭代未收敛到闭式"
assert abs(mult_lump - 5.0) < 1e-6, "总量税支出乘数应为 5"

# ---------- B. 比例税：自动稳定器（乘数减半） ----------
t = 0.25
mult_prop = 1 / (1 - c * (1 - t))
# 比例税世界（总量税=0）的振幅由 converge(dI=±10, t=t) 直接迭代给出
amp_lump = abs(converge(dI=10.0) - converge(dI=-10.0))
amp_prop = abs(converge(dI=10.0, t=t) - converge(dI=-10.0, t=t))
print(f"\n[B] 比例税 t={t}: 乘数闭式 = 1/(1-c(1-t)) = {mult_prop:.4f}")
print(f"[B] 投资冲击 ±10 的产出振幅: 无税 {amp_lump:.2f} vs 比例税 {amp_prop:.2f}"
      f"（自动稳定器把放大倍数从 5 压到 2.5）")
assert abs(mult_prop - 2.5) < 1e-12, "比例税乘数应为 1/0.4=2.5"
assert abs(amp_lump - 100.0) < 1e-6 and abs(amp_prop - 50.0) < 1e-6, \
    "自动稳定器应把振幅从 100 压到 50"

# ---------- C. Haavelmo：平衡预算乘数 = 1 ----------
dG = dT = 10.0
Y_bb = converge(dG=dG, dT=dT)
delta_Y = Y_bb - Y_before
eff_G, eff_T = 1 / (1 - c), -c / (1 - c)
print(f"\n[C] ΔG=ΔT={dG:.0f}: Y 从 {Y_before:.4f} -> {Y_bb:.4f}, "
      f"ΔY={delta_Y:.6f}（Haavelmo：恰为 1×ΔG）")
print(f"[C] 分解: 支出效应 {dG*eff_G:.1f} + 税收效应 {dT*eff_T:.1f} = "
      f"{dG*eff_G + dT*eff_T:.1f} —— 5 + (-4) = 1，与 c 无关的恒等式")
assert abs(delta_Y - dG) < 1e-6, "平衡预算乘数应恰为 1"
assert abs((eff_G + eff_T) - 1.0) < 1e-12, "乘数之和恒为 1 的恒等式失败"

print("\n[ALL ASSERTS PASSED] 乘数=漏出的倒数（1/(1-c)=5）；比例税让经济")
print("'变钝'（5->2.5，这就是自动稳定器）；平衡预算乘数恒为 1——")
print("加税花钱的单位乘数，是财政学最著名的恒等式级定理（Haavelmo 1945）。")
