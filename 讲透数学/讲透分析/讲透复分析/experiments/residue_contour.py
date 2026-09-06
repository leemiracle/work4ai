# -*- coding: utf-8 -*-
"""
residue_contour.py — 留数定理数值现场（对应 00/03/04 章，走廊①）

三方对照计算两个经典实轴积分：
  例1  ∫_{-∞}^{∞} dx/(1+x²)          = π        （被积 = 1/(1+z²) 的实轴限制）
  例2  ∫_{-∞}^{∞} cos(x)/(1+x²) dx   = π/e      （留数定理经典应用；quad 侧为震荡积分）

三条路线：
  A) 留数引擎：上半平面极点 z0 处 Res(g/h) = g(z0)/h'(z0)，积分 = 2πi·ΣRes
  B) scipy.integrate.quad 实轴直接积分（分实虚部）
  C) 围道闭合演示：上半圆围道的弧段积分实测 |∫arc| ≈ πR/(R²-1) → 0（闭合合法性）

自验证断言：
  A 对解析值的误差 < 1e-12（留数法是公式代入，可达机器精度级）
  B 对解析值的误差 < 1e-8
  R=100 时弧段积分模 < 0.05（围道闭合误差 O(1/R) 量级实测）

运行：python3 -u experiments/residue_contour.py
依赖：numpy, scipy
"""
import warnings

import numpy as np
from scipy.integrate import IntegrationWarning, quad

# 裸 quad 啃无穷震荡必然触发子区间耗尽警告——那是教学点本身（例2 B 行），不当噪音放行
warnings.filterwarnings("ignore", category=IntegrationWarning)


def residue_simple_pole(g, h, z0, dz=1e-6):
    """一阶极点留数 Res(g/h, z0) = g(z0)/h'(z0)，数值导数版。

    03 章 1.2 的'一次代入一次求导'——留数提取完全机械化。
    """
    hp = (h(z0 + dz) - h(z0 - dz)) / (2 * dz)          # h'(z0) 中心差分
    return g(z0) / hp


def real_integral_via_residue(g, h, upper_poles):
    """留数引擎：∫_{-∞}^{∞} g(x)/h(x) dx = 2πi · Σ Res(上半平面)。"""
    return 2j * np.pi * sum(residue_simple_pole(g, h, z0) for z0 in upper_poles)


def quad_real_imag(integrand, lo=-np.inf, hi=np.inf):
    """quad 不吃复值被积：拆实虚部各积一次。"""
    re = quad(lambda x: np.real(integrand(x)), lo, hi, limit=200)[0]
    im = quad(lambda x: np.imag(integrand(x)), lo, hi, limit=200)[0]
    return re + 1j * im


def quad_fourier(f, w=1.0):
    """QAWF 路线：∫₀^∞ f(x)cos(wx)dx 的专用积分器（QUADPACK QAWF）。

    通用自适应 quad 直接啃 ∫e^{ix}/(1+x²) 只到 ~3e-5（无穷多振荡周期，
    子区间耗尽——IntegrationWarning 现场即教学点：震荡积分是 quad 的弱区）。
    QAWF 是为 Fourier 尾巴设计的，可达 1e-11 级。
    """
    return quad(f, 0.0, np.inf, weight="cos", wvar=w, limit=500)[0]


def arc_contribution(integrand, R, n=20000):
    """上半圆弧 z=Re^{iθ}, θ∈[0,π] 的数值积分（composite trapezoid, 向量化）。"""
    theta = np.linspace(0.0, np.pi, n)
    z = R * np.exp(1j * theta)
    vals = integrand(z) * (1j * R * np.exp(1j * theta))   # f(z) dz, dz = iRe^{iθ}dθ
    return np.trapezoid(vals, theta)


# ─────────────────────────── 例 1：∫ dx/(1+x²) = π ───────────────────────────
g1 = lambda z: np.ones_like(z) * 1.0 if np.ndim(z) else 1.0
h1 = lambda z: 1 + z**2

res_engine1 = real_integral_via_residue(g1, h1, upper_poles=[1j])
res_quad1 = quad_real_imag(lambda x: 1.0 / (1.0 + x**2))
exact1 = np.pi

print("例1  ∫ dx/(1+x²) ，解析值 π = {:.15f}".format(exact1))
print("  A 留数引擎  = {:.15f}   |误差| = {:.2e}".format(res_engine1.real, abs(res_engine1 - exact1)))
print("  B quad      = {:.15f}   |误差| = {:.2e}".format(res_quad1.real, abs(res_quad1 - exact1)))

assert abs(res_engine1 - exact1) < 1e-12, "留数引擎失准（应达公式级精度）"
assert abs(res_quad1 - exact1) < 1e-8, "quad 失准"

# ──────────────────────── 例 2：∫ cos(x)/(1+x²) dx = π/e ────────────────────────
# 复被积 e^{iz}/(1+z²)：上半极点 i 处 Res = e^{-1}/(2i) ⟹ ∫ e^{ix}/(1+x²)dx = π/e（实）
g2 = lambda z: np.exp(1j * z)
h2 = lambda z: 1 + z**2

res_engine2 = real_integral_via_residue(g2, h2, upper_poles=[1j])
# quad 侧两档：裸自适应（弱区现场）→ QAWF 傅里叶专用（真实实力）
f2 = lambda x: 1.0 / (1.0 + x**2)
res_quad2_naive = quad_real_imag(lambda x: np.exp(1j * x) / (1.0 + x**2)).real
res_quad2_qawf = 2.0 * quad_fourier(f2, w=1.0)          # 偶函数：全轴 = 2×半轴
exact2 = np.pi / np.e

print("\n例2  ∫ cos(x)/(1+x²) dx ，解析值 π/e = {:.15f}".format(exact2))
print("  A 留数引擎      = {:.15f}   |误差| = {:.2e}".format(res_engine2.real, abs(res_engine2 - exact2)))
print("  B quad 裸自适应 = {:.15f}   |误差| = {:.2e}  ← 震荡弱区（子区间耗尽）".format(
    res_quad2_naive, abs(res_quad2_naive - exact2)))
print("  B' quad QAWF    = {:.15f}   |误差| = {:.2e}  ← Fourier 专用积分器".format(
    res_quad2_qawf, abs(res_quad2_qawf - exact2)))

assert abs(res_engine2 - exact2) < 1e-12, "留数引擎失准（例2）"
assert abs(res_quad2_qawf - exact2) < 1e-8, "QAWF 失准（例2）"
assert abs(res_quad2_naive - exact2) < 1e-3, "裸 quad 连 1e-3 都没到（震荡弱区判据）"

# ───────────────────── C 围道闭合演示：弧段贡献 → 0（O(1/R)） ─────────────────────
print("\nC 围道闭合演示：上半圆弧段贡献 |∫arc|（理论界 πR/(R²-1)）")
for R in (10.0, 30.0, 100.0):
    arc1 = arc_contribution(lambda z: 1.0 / (1.0 + z**2), R)
    bound = np.pi * R / (R * R - 1)
    print("  R={:6.1f}  |∫arc| = {:.6e}   理论界 = {:.6e}".format(R, abs(arc1), bound))
    if R == 100.0:
        assert abs(arc1) < 0.05, "弧段贡献未按 O(1/R) 衰减"
        assert abs(arc1) <= bound * 1.05, "超出理论界（不该发生）"

print("\n[ALL ASSERTS PASSED] 留数引擎两例达公式级精度；QAWF 达 1e-8；围道闭合 O(1/R) 实测成立。")
print("带走一句（04 章）：留数定理把'积分'变成'数极点+代公式'——裸 quad 在震荡积分")
print("上的挣扎（例2 B 行）对留数引擎不存在（A 行零误差），专用积分器 QAWF 也只是追平。")
