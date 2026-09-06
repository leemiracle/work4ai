# -*- coding: utf-8 -*-
"""
无限深势阱能级：两种数值方法 vs 解析解
对应章：讲透理论物理/00-体系结构（2.3 量子力学支柱）、03-可构造与结构（1.3 格点档）、04-转代码（走廊②）

物理：一维无限深势阱 [0, L]，自然单位 (ℏ = m = L = 1)：
  解析能级  E_n = n² π² / 2,  n = 1, 2, 3, ...
方法A：有限差分——哈密顿算符离散化为三对角矩阵，本征值即数值能级（走廊②最小标本）
方法B：打靶法——把薛定谔方程当初值问题积分，调节能量直到波函数在右边界归零
断言：两种方法前 5 个能级与解析解的相对误差均 < 1e-3（0.1%）
"""
import numpy as np

L, N = 1.0, 4000                      # 阱宽与内点数
h = L / (N + 1)                       # 格距
n_levels = 5
analytic = np.array([(n * np.pi) ** 2 / 2 for n in range(1, n_levels + 1)])

# ── 方法A：有限差分（三对角哈密顿）──
main = np.full(N, 1.0) / h ** 2       # 对角：H = -(1/2)u''，V=0 ⟹ 对角 = 1/h²
off = np.full(N - 1, -0.5) / h ** 2   # 次对角：-1/(2h²)
try:
    from scipy.linalg import eigvalsh_tridiagonal
    eigA = eigvalsh_tridiagonal(main, off, select='i', select_range=(0, n_levels - 1))
except ImportError:                    # 纯 numpy 备胎：稠密化（N 较小时可用）
    H = np.diag(main) + np.diag(off, 1) + np.diag(off, -1)
    eigA = np.linalg.eigvalsh(H)[:n_levels]

# ── 方法B：打靶法（Numerov 六阶精度）──
def shoot(E):
    """Numerov 积分 u'' = -2E·u（振荡解），返回 u(L)（边界要求为 0）。
    标准公式（f ≡ u''/u）：u_{n+1}(1 - h²f_{n+1}/12) = 2u_n(1 + 5h²f_n/12) - u_{n-1}(1 - h²f_{n-1}/12)"""
    u0, u1 = 0.0, 1e-5                # 左边界 u(0)=0，起点一小步
    f = -2.0 * E                      # V=0 区域
    q0 = q1 = q2 = f
    for i in range(1, N + 1):
        u2 = (2 * u1 * (1 + 5 * h * h * q1 / 12) - u0 * (1 - h * h * q0 / 12)) / (1 - h * h * q2 / 12)
        u0, u1, q0, q1 = u1, u2, q1, q2
    return u1

eigB = []
for n in range(1, n_levels + 1):
    lo, hi = analytic[n - 1] * 0.9, analytic[n - 1] * 1.1   # 解析值附近夹逼
    for _ in range(80):                                     # 二分收敛
        mid = 0.5 * (lo + hi)
        if shoot(mid) * shoot(lo) < 0: hi = mid
        else: lo = mid
    eigB.append(0.5 * (lo + hi))
eigB = np.array(eigB)

# ── 对拍与断言 ──
errA, errB = np.abs(eigA - analytic) / analytic, np.abs(eigB - analytic) / analytic
print(f"{'n':>3} {'解析 E_n':>12} {'有限差分':>14} {'相对误差':>11} {'打靶法':>14} {'相对误差':>11}")
for n in range(n_levels):
    print(f"{n+1:>3} {analytic[n]:>12.6f} {eigA[n]:>14.6f} {errA[n]:>11.2e} {eigB[n]:>14.6f} {errB[n]:>11.2e}")

assert np.all(errA < 1e-3), f"有限差分超差: {errA}"
assert np.all(errB < 1e-3), f"打靶法超差: {errB}"
print("\n[ALL ASSERTS PASSED] 束缚⟹量子化：两种独立数值方法都复现 E_n ∝ n²（前5能级误差<0.1%）")
print("带走一句（03章）：第一档的解析谱给第三档的数值当裁判——对拍是理论物理数值工作的标准姿势。")
