# -*- coding: utf-8 -*-
"""
hydrogen_levels.py — 氢原子径向薛定谔方程的打靶法数值解
对应章：讲透原子分子物理 03-可构造与结构（走廊1）/ 04-转代码（打靶法现场）

物理：原子单位 (ℏ = m_e = e = 1)，l = 0（s 态）
    u''(r) = 2[V(r) - E] u(r),  V(r) = -1/r
    边界：u(0)=0, u'(0)=1（归一化任意）；束缚态要求 u(r→∞) → 0

方法：RK4 积分 + 二分能量（本征值处 u(r_max) 的发散方向翻转）
     节点定理：第 (n-1) 个态恰有 (n-1) 个节点——量子数是拓扑

验证（断言）：
    |E1 + 0.5  | < 1e-4   (解析 E_n = -1/(2n²))
    |E2 + 0.125| < 1e-4
    E1 × 27.211386 ≈ -13.6057 eV（对照 NIST 电离能 13.605693 eV）
    基态 0 节点、第一激发态 1 节点
"""
import numpy as np

HARTREE_EV = 27.211386  # 1 Hartree = 27.211386 eV

def shoot(E, rmax, dr, eps=1e-5):
    """给定能量 E，RK4 积分径向方程，返回 (u_end, u 数组, r 数组)。"""
    def deriv(r, y):
        u, du = y
        return np.array([du, 2.0 * (-1.0 / r - E) * u])
    r = eps
    y = np.array([eps, 1.0])          # u(r) ~ r 近核行为
    rs, us = [r], [y[0]]
    n = int((rmax - eps) / dr)
    h = (rmax - eps) / n
    for i in range(n):
        k1 = deriv(r, y)
        k2 = deriv(r + h/2, y + h/2 * k1)
        k3 = deriv(r + h/2, y + h/2 * k2)
        k4 = deriv(r + h, y + h * k3)
        y = y + h/6 * (k1 + 2*k2 + 2*k3 + k4)
        r += h
        rs.append(r)
        us.append(y[0])
    return y[0], np.array(us), np.array(rs)

def bisect_level(Elo, Ehi, rmax, dr, tol=1e-10):
    """二分能量使 u(rmax) 符号翻转 → 返回本征能量 E*。"""
    lo, hi = Elo, Ehi
    flo, _, _, = shoot(lo, rmax, dr)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        fmid, _, _ = shoot(mid, rmax, dr)
        if abs(fmid) == 0.0 or (hi - lo) < tol:
            return mid
        if flo * fmid < 0:
            hi = mid
        else:
            lo, flo = mid, fmid
    return 0.5 * (lo + hi)

def count_nodes(u, r, r_cut):
    """在物理窗口 r < r_cut 内统计节点数（窗口内再用 1% 峰值掩码）。

    打靶解的远端必被本征值残差 (~1e-10) 驱动的发散分量污染：
    物理解先衰减到阈值以下、发散分量后涨回来并跨零——产生假节点。
    第 n 束缚态的物理范围 ~2n² a₀，窗口取 r_cut = 12 (1s) / 30 (2s)
    时窗口内物理解幅值仍 ≥ 峰值的 1e-4，发散分量远未起势。
    """
    sel = r < r_cut
    w = np.abs(u[sel])
    mask = w > 0.01 * np.max(w)
    s = np.sign(u[sel][mask])
    return int(np.sum(s[1:] * s[:-1] < 0))

if __name__ == "__main__":
    print("=" * 62)
    print("氢原子 s 态能级：打靶法 (原子单位)")
    print("=" * 62)

    # 基态 1s：E ∈ [-0.6, -0.4]，波函数定域，rmax=40 足够
    E1 = bisect_level(-0.6, -0.4, rmax=40.0, dr=0.002)
    _, u1, r1 = shoot(E1, 40.0, 0.002)
    n1 = count_nodes(u1, r1, r_cut=12.0)

    # 第一激发态 2s：E ∈ [-0.16, -0.11]，波函数延伸远，rmax=70
    E2 = bisect_level(-0.16, -0.11, rmax=70.0, dr=0.002)
    _, u2, r2 = shoot(E2, 70.0, 0.002)
    n2 = count_nodes(u2, r2, r_cut=30.0)

    exact1, exact2 = -0.5, -0.125
    print(f"E1 (数值) = {E1:.8f} Ha   | 解析 = {exact1:.8f} Ha   | 误差 = {abs(E1-exact1):.2e}")
    print(f"E1 (eV)   = {E1*HARTREE_EV:.4f} eV  | NIST 电离能 = 13.6057 eV")
    print(f"E2 (数值) = {E2:.8f} Ha   | 解析 = {exact2:.8f} Ha   | 误差 = {abs(E2-exact2):.2e}")
    print(f"节点数：基态 u1 → {n1}（期望 0）  |  第一激发态 u2 → {n2}（期望 1）")
    print("节点定理：量子数 n-1 = 节点数——谱的排序=波函数的拓扑。")

    # ─── 断言自验 ───
    assert abs(E1 - exact1) < 1e-4, f"E1 误差过大: {E1}"
    assert abs(E2 - exact2) < 1e-4, f"E2 误差过大: {E2}"
    assert abs(E1 * HARTREE_EV + 13.6057) < 0.01, "E1 换算 eV 与 NIST 不符"
    assert n1 == 0, f"基态节点数异常: {n1}"
    assert n2 == 1, f"2s 节点数异常: {n2}"
    print()
    print("[ALL ASSERTS PASSED] 打靶法在两个态上同时复现解析谱与节点定理。")
