#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
传输线方程数值实验 —— 讲透无线电物理 GB/T 14040
对应章：00-体系结构 §4.1（λ/4 阻抗反转）/ 03-可构造与结构 §2.4（周期刚性）/
       04-无线电物理转代码 走廊①

方法：相量域前向/反向波数值传播（逐步累乘相位元，非一步闭式），
     与闭式公式 Z_in(d) = Z0(ZL + j Z0 tan βd)/(Z0 + j ZL tan βd) 对账。
断言：Γ=1/3、VSWR=2、λ/4 反转 100Ω→25Ω、λ/2 周期、λ/4 变换器匹配、|Γ|² 功率守恒。
运行：python transmission_line.py
"""
import numpy as np

Z0 = 50.0 + 0j      # 主线特征阻抗
ZL = 100.0 + 0j     # 负载（失配 2:1）
lam = 1.0           # 波长（归一化单位）
beta = 2 * np.pi / lam


def reflection_coefficient(zl, z0):
    """负载反射系数 Γ = (ZL-Z0)/(ZL+Z0)。"""
    return (zl - z0) / (zl + z0)


def vswr(gamma):
    """驻波比 VSWR = (1+|Γ|)/(1-|Γ|)。"""
    return (1 + abs(gamma)) / (1 - abs(gamma))


def z_in_analytic(d, zl=ZL, z0=Z0):
    """闭式输入阻抗：Z_in(d) = Z0 (ZL + j Z0 tan βd)/(Z0 + j ZL tan βd)。"""
    t = np.tan(beta * d)
    return z0 * (zl + 1j * z0 * t) / (z0 + 1j * zl * t)


def z_in_numeric(d, zl=ZL, z0=Z0, n_steps=200000):
    '''数值构造：从负载出发，把前向/反向波相量沿传播方向逐步累乘 e^{jβdz}，
    在输入端取 V/I 之比。与闭式公式独立（逐步累乘 vs 一步 tan），互为对账。'''
    dz = d / n_steps
    phase = np.exp(1j * beta * dz)          # 每步的相位元
    g = reflection_coefficient(zl, z0)
    v_fwd, v_bwd = 1.0 + 0j, g              # 负载处前向=1，反向=Γ·前向
    for _ in range(n_steps):                 # 向源方向推进：前向波超前、反向波滞后
        v_fwd *= phase
        v_bwd /= phase
    v = v_fwd + v_bwd
    i = (v_fwd - v_bwd) / z0
    return v / i


def quarter_wave_transformer(zl, z0):
    """λ/4 阻抗变换器：Zq = sqrt(Z0·ZL)，变换后输入端匹配。"""
    return np.sqrt(z0 * zl)


def main():
    # ── ① 反射系数与驻波比（00 章 §4）──
    g = reflection_coefficient(ZL, Z0)
    print(f"① ZL=100Ω/Z0=50Ω：Γ = {g.real:.6f}（理论 1/3），VSWR = {vswr(g):.6f}（理论 2）")
    assert abs(g - 1/3) < 1e-12, "Γ 应为 1/3"
    assert abs(vswr(g) - 2.0) < 1e-12, "VSWR 应为 2"

    # ── ② 反射功率守恒（03 章 §2.3 能量刚性）──
    p_refl = abs(g) ** 2
    print(f"② 反射功率占比 |Γ|² = {p_refl:.6f}（理论 1/9 ≈ 0.1111）")
    assert abs(p_refl - 1/9) < 1e-12, "反射功率应为 1/9"

    # ── ③ λ/4 阻抗反转（00 章 §4.1 反直觉发现）──
    z_quarter_num = z_in_numeric(lam / 4)
    z_quarter_ana = z_in_analytic(lam / 4)
    print(f"③ λ/4 处：数值 Z_in = {z_quarter_num.real:.4f}Ω | 闭式 = {z_quarter_ana.real:.4f}Ω"
          f"（理论 Z0²/ZL = 25Ω：100Ω 负载被'倒'成 25Ω）")
    assert abs(z_quarter_num - 25.0) < 1e-3, "λ/4 处应为 Z0²/ZL=25Ω"
    assert abs(z_quarter_ana - 25.0) < 1e-9, "闭式 λ/4 应精确 25Ω"

    # ── ④ λ/2 周期性：传输线"透明"（03 章 §2.4 刚性）──
    z_half_num = z_in_numeric(lam / 2)
    print(f"④ λ/2 处：数值 Z_in = {z_half_num.real:.4f}Ω（理论 = ZL = 100Ω：半波长透明）")
    assert abs(z_half_num - ZL) < 1e-3, "λ/2 处应重现负载 100Ω"

    # ── ⑤ λ/4 变换器匹配设计（04 章 走廊① 三行代码出数）──
    zq = quarter_wave_transformer(ZL, Z0)
    z_after = z_in_analytic(lam / 4, zl=ZL, z0=zq)  # 经 λ/4、Zq 线看 ZL
    g_after = reflection_coefficient(z_after, Z0)
    print(f"⑤ λ/4 变换器：Zq = sqrt(50×100) = {zq.real:.4f}Ω，"
          f"变换后 Γ_in = {abs(g_after):.2e}（理论 0：完美匹配）")
    assert abs(g_after) < 1e-12, "λ/4 变换器应完美匹配"

    # ── ⑥ 数值 vs 闭式全线对账（04 章：数值构造与解析互验）──
    ds = np.linspace(0.01, 0.49, 200) * lam
    err = max(abs(z_in_numeric(d, n_steps=2000) - z_in_analytic(d)) for d in ds)
    print(f"⑥ 200 点全线数值-闭式最大偏差 = {err:.2e}（< 1e-3）")
    assert err < 1e-3, "数值与闭式应在全线吻合"

    print("\n[ALL ASSERTS PASSED] 传输线四刚性事实全部实测成立：")
    print("  Γ/VSWR 公式级精确；|Γ|² 功率账本守恒；λ/4 阻抗反转；λ/2 周期透明；λ/4 变换器归零匹配。")
    print("带走一句（00 章）：传输线不是导线是波导——直流思维在射频失效，")
    print("四分之一波长把阻抗世界变成负一次方。")


if __name__ == "__main__":
    main()
