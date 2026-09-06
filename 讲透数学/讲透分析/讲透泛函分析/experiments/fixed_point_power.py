# -*- coding: utf-8 -*-
"""
泛函分析两台构造引擎的数值现场（对应 03-可构造与结构 §二§三 / 04-转代码 走廊1&3）

(a) Banach 不动点：x = cos(x)（Dottie 数 ≈0.7390851）
    —— 定理四件套（存在/唯一/算法/速率）中"速率"的实测：
       误差几何衰减，渐近压缩率 = sin(x*) ≈ 0.6736（理论值）
(b) 幂法（谱逼近的最小化身）：随机对称阵主特征值
    —— Rayleigh 商收敛至 numpy.linalg.eigvalsh 参考值，相对误差 < 1e-8
       收敛率由谱间隙 (λ2/λ1)^k 控制（03 章 §三 "特征信息藏在迭代动力学里"）

运行：python experiments/fixed_point_power.py
"""
import numpy as np
from scipy.optimize import brentq

# ─────────────────────────────────────────────────────────────
# (a) Banach 不动点：x = cos(x)
# ─────────────────────────────────────────────────────────────
x_star = brentq(lambda x: np.cos(x) - x, 0.0, 1.0, xtol=1e-15)
q_theory = np.sin(x_star)            # 渐近压缩率：|cos'(x*)| = sin(x*)

xs, x = [], 1.0
for n in range(100):
    xs.append(x)
    x = np.cos(x)
xs = np.array(xs)
err = np.abs(xs - x_star)

# 先验误差界（不需要 x* 的可计算版）：‖x_n − x*‖ ≤ q^n/(1−q)·‖x_1 − x_0‖
q_bound = 0.68                       # 全局安全上界（sin ≤ 0.68 on [0,1]）
e0 = abs(xs[1] - xs[0])
a_priori = np.array([q_bound**n * e0 / (1 - q_bound) for n in range(100)])

print("═" * 62)
print("(a) Banach 不动点  x = cos(x)")
print(f"  参考不动点 x*        = {x_star:.12f}")
print(f"  理论渐近压缩率 sin(x*) = {q_theory:.6f}")
print(f"  e_0={err[0]:.3e}  e_10={err[10]:.3e}  e_50={err[50]:.3e}  e_99={err[99]:.3e}")
with np.errstate(divide="ignore", invalid="ignore"):
    ratios = err[1:] / err[:-1]
valid = err[:-1] > 1e-13                 # 收敛到机器精度后比率失去意义
asym = ratios[valid][-20:].mean()
print(f"  实测渐近衰减率（末20步均值）= {asym:.6f}")
ok_a1 = err[99] < 1e-12
ok_a2 = 0.60 < asym < 0.69
ok_a3 = np.all(err <= a_priori + 1e-15)   # 先验界全程成立
print(f"  断言1: e_99 < 1e-12                -> {ok_a1}")
print(f"  断言2: 渐近率∈(0.60,0.69)          -> {ok_a2}")
print(f"  断言3: 误差全程 ≤ 先验界           -> {ok_a3}")
assert ok_a1 and ok_a2 and ok_a3, "(a) Banach 不动点断言失败"

# ─────────────────────────────────────────────────────────────
# (b) 幂法：随机对称阵的模最大特征值
# ─────────────────────────────────────────────────────────────
rng = np.random.default_rng(0)
n = 6
B = rng.standard_normal((n, n))
A = (B + B.T) / 2                    # 对称化：谱实、Rayleigh 商即特征值估计

v = rng.standard_normal(n)
v /= np.linalg.norm(v)
r_hist = []
for k in range(5000):
    v = A @ v
    v /= np.linalg.norm(v)
    r_hist.append(v @ A @ v)         # Rayleigh 商
lam_power = r_hist[-1]

eigvals = np.linalg.eigvalsh(A)      # 升序
lam_ref = eigvals[np.argmax(np.abs(eigvals))]   # 模最大者（幂法的目标）
rel_err = abs(lam_power - lam_ref) / abs(lam_ref)
gap = np.sort(np.abs(eigvals))[::-1]
ratio_gap = gap[1] / gap[0] if gap[0] > 0 else 0.0
rate_bound = ratio_gap**2            # Rayleigh 商误差 O((λ2/λ1)^{2k})

print("═" * 62)
print("(b) 幂法 Rayleigh 商 vs eigvalsh")
print(f"  eigvalsh 谱           = {np.round(eigvals, 6)}")
print(f"  模最大特征值（参考）  = {lam_ref:.12f}")
print(f"  幂法 Rayleigh 商      = {lam_power:.12f}")
print(f"  谱间隙比 |λ2/λ1|      = {ratio_gap:.4f}（Rayleigh 收敛率 ~ {rate_bound:.2e}/步）")
for k in (10, 100, 1000, 5000):
    print(f"  r_{k:<5d}               = {r_hist[k-1]:.12f}")
ok_b = rel_err < 1e-8
print(f"  断言4: 相对误差 < 1e-8             -> {ok_b}（实测 {rel_err:.2e}）")
assert ok_b, "(b) 幂法断言失败"

print("═" * 62)
print("全部断言通过 ✅  （03章：不动点=构造引擎；04章：走廊1&3 数值现场）")
