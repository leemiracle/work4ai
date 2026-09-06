#!/usr/bin/env python3
"""lab11 · 稀疏引擎：scipy.sparse 上量到十万态 + 价值迭代停机判据陷阱（11 章 §二/§四）。
模型：一维公平随机游走（赌徒破产）。状态 i∈{0..N}，i=0 吸收（输）、i=N 吸收（赢）、i→i±1 各半。
闭式解（精确对拍锚点）：P(F 赢 | i) = i/N——数学当测试用例。

E1 稀疏直接解（Storm 的"稀疏引擎"路线）：(I−Q)p = r 的三对角稀疏线性求解，
   N=10⁵ 态 0.05 秒、全状态误差 <1e-9——"十万态秒级"由【直接解】兑现（11 章 §二）。
   （计划原稿想用价值迭代跑十万态——实测不可行，见 E2 的复杂度；先跑后写、如实改道。）
E2 价值迭代 = 另一台引擎，两个诚实教训（11 章 §四）：
   ① 扫描数 = Θ(N²)：信息每轮只推一步（相邻两态），N=400 需 11.9 万轮；
   ② 停机陷阱：'相邻两轮差 <1e-6'判停机时真误差仍 ~1e-2（收缩率→1 时判据失真）——
      这正是 Storm 默认区间迭代 / sound VI 的存在理由（Baier et al. 2017）。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
import time

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

TOL_DIRECT = 1e-9
STOP_DIFF = 1e-6        # E2 的（不可靠）停机阈值——陷阱现场的主角


def build_walk_tridiag(n):
    """内部态 1..n−1 的 (I−Q) 三对角矩阵与右端 r（一步进 target 的概率）。"""
    inner = n - 1
    Q = diags([0.5 * np.ones(inner - 1), 0.5 * np.ones(inner - 1)], [-1, 1],
              shape=(inner, inner))
    A = (diags([np.ones(inner)], [0]) - Q).tocsc()
    r = np.zeros(inner)
    r[-1] = 0.5                       # 态 n−1 有 0.5 概率一步跳进 target=n
    return A, r


def sparse_direct(n):
    """E1：稀疏直接解。返回 (p, 耗时秒)。p[k] 对应态 k+1。"""
    A, r = build_walk_tridiag(n)
    t0 = time.time()
    p = spsolve(A, r)
    return p, time.time() - t0


def value_iteration(n, stop_diff=STOP_DIFF, sweep_cap=None):
    """E2：Jacobi 式价值迭代（每轮全状态用旧值）。返回 (p, 扫描数, 耗时)。"""
    p = np.zeros(n + 1)
    p[n] = 1.0
    idx = np.arange(1, n)
    t0 = time.time()
    sweeps = 0
    while True:
        q = p.copy()
        p[idx] = 0.5 * q[idx - 1] + 0.5 * q[idx + 1]
        sweeps += 1
        if np.abs(p[idx] - q[idx]).max() < stop_diff:
            break
        if sweep_cap is not None and sweeps >= sweep_cap:
            break
    return p, sweeps, time.time() - t0


print("=" * 68)
print("E1 · 稀疏直接解：十万态 0.05 秒（闭式解 i/N 当测试用例）")
print("=" * 68)
N = 100_000
p, dt = sparse_direct(N)
closed = np.arange(1, N) / N
err1 = np.abs(p - closed).max()
print(f"模型：赌徒破产随机游走，N={N:,} 态（三对角稀疏，nnz≈{3 * (N - 2):,}）")
print(f"手推锚点（11 章 §二）：闭式解 P(F 赢|i) = i/N；方程 (I−Q)p = r 一步求解")
print(f"  spsolve：{dt:.2f} 秒；全状态最大误差 = {err1:.2e}（vs 闭式解，容差 {TOL_DIRECT}）")
assert err1 < TOL_DIRECT, err1
print("→ E1 自检通过：稀疏直接解十万态秒级、误差压进 1e-9——'上量'由直接引擎兑现")

print("\n" + "=" * 68)
print("E2 · 价值迭代：Θ(N²) 扫描数 + 停机判据陷阱")
print("=" * 68)
N2 = 400
p2, sweeps, dt2 = value_iteration(N2)
true_err = np.abs(p2[1:N2] - np.arange(1, N2) / N2).max()
print(f"模型同上，N={N2}，停机条件'相邻两轮差 < {STOP_DIFF}'：")
print(f"  扫描数 = {sweeps:,}（sweeps/N² = {sweeps / N2 ** 2:.2f}——Θ(N²)：信息每轮只推一步，"
      f"从边界传到中心要 ~N/2 轮的平方量级）")
print(f"  耗时 {dt2:.2f} 秒；停机时【真】误差（vs 闭式解）= {true_err:.2e}")
print(f"  陷阱：停机阈值 {STOP_DIFF}，真误差 {true_err:.1e}——相差 {true_err / STOP_DIFF:.0f} 倍")
print("  原因：吸收链的价值迭代收缩率 →1（谱半径随 N 增大），'两轮差小'≠'离真解近'")
print("  ——这正是 Storm 默认区间迭代 / sound VI 的动机：给概率上下界而非裸点估计")
assert sweeps > 0.5 * N2 ** 2, sweeps
assert true_err > 100 * STOP_DIFF, true_err
print("→ E2 自检通过（两条诚实断言：Θ(N²) 扫描、真误差≫停机阈值）——引擎选择不是性能细节，是正确性细节")

print("\nlab11 全部自检通过")
