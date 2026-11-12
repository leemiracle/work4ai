# -*- coding: utf-8 -*-
"""
direct_method_fem.py —— 直接法的可执行现场（对应 00/03/04 章）

变分问题:  J[v] = ∫₀¹ ( ½|v'|² - f v ) dx → min,  v(0)=v(1)=0
取 f=2,真解 u* = x(1-x) (即 -u'' = 2 的狄氏边值),J* = -1/6。

本脚本演示:
  1. 直接法的离散化执行:P1 有限元上直接极小化 J(驻点方程 = 离散 Euler-Lagrange,
     即刚度方程 K u = F)——不解连续方程,离散化的是"泛函"本身
  2. Γ-收敛的最小实例:网格加密族 J_h → J,数值极小 u_h → u*
     (H¹ 半范误差 O(h),L² 误差 O(h²))
  3. 能量单调性:J(u*) ≤ J(u_h)(连续极小是下界,离散极小逼近但不超过)
  4. 驻点残差 ‖K u_h − F‖ ≈ 0(变分解的"单元测试")

运行:  python3 -u direct_method_fem.py
依赖:  numpy
"""
import numpy as np

F_LOAD = 2.0          # 载荷 f ≡ 2
J_STAR = -1.0 / 6.0   # 真解能量 J(u*) 解析值


def u_exact(x):
    """真解 u* = x(1-x)"""
    return x * (1.0 - x)


def solve_fem(n_elem):
    """P1 有限元直接极小化 J[v](自由节点 = 内部 n_elem-1 个)。

    刚度矩阵 K=(1/h)·tridiag(−1,2,−1),载荷 F_i = ∫ f φ_i = f·h(线性元精确)。
    解 K u = F 即离散 Euler-Lagrange 方程 —— J 在 V_h 上的极小元。
    """
    n_int = n_elem - 1                      # 内部自由度
    h = 1.0 / n_elem
    K = (np.diag(2.0 * np.ones(n_int)) +
         np.diag(-1.0 * np.ones(n_int - 1), 1) +
         np.diag(-1.0 * np.ones(n_int - 1), -1)) / h
    F = F_LOAD * h * np.ones(n_int)         # 线性基函数载荷(梯形对线性精确)
    u_int = np.linalg.solve(K, F)
    resid = np.linalg.norm(K @ u_int - F, ord=np.inf)
    u = np.concatenate(([0.0], u_int, [0.0]))
    energy = 0.5 * u_int @ (K @ u_int) - F @ u_int   # J(u_h) = ½uᵀKu − Fᵀu
    return u, h, energy, resid


def errors(u_h, h):
    """细网格上数值积分:L² 误差与 H¹ 半范误差(vs 真解)。"""
    m = 16                                   # 每单元细分子格
    xs, l2_sq, h1_sq = [], 0.0, 0.0
    for i in range(len(u_h) - 1):
        slope = (u_h[i + 1] - u_h[i]) / h    # u_h' 在单元内为常数
        sub = np.linspace(0.0, h, m + 1)
        dx = h / m
        for j in range(m):
            xm = sub[j] + 0.5 * dx           # 中点积分
            x = i * h + xm
            l2_sq += (np.interp(x, [i * h, (i + 1) * h],
                                [u_h[i], u_h[i + 1]]) - u_exact(x)) ** 2 * dx
            h1_sq += (slope - (1.0 - 2.0 * x)) ** 2 * dx   # u*' = 1−2x
    return np.sqrt(l2_sq), np.sqrt(h1_sq)


def main():
    print("=" * 72)
    print("直接法×有限元:J[v]=∫(½v'² − 2v) → min,v(0)=v(1)=0;真解 u*=x(1-x)")
    print("=" * 72)
    print(f"{'N':>5} {'h':>9} {'L2误差':>12} {'H1半范误差':>12} "
          f"{'H1相邻比':>8} {'J(u_h)':>12} {'J*−J(u_h)':>12}")
    print("-" * 72)

    ns = [8, 16, 32, 64, 128, 256]
    rows = []
    for n in ns:
        u, h, energy, resid = solve_fem(n)
        assert resid < 1e-9, f"驻点残差过大: {resid}"          # 断言④
        assert energy >= J_STAR - 1e-12, "能量违反下界 J* ≤ J(u_h)"  # 断言③
        l2, h1 = errors(u, h)
        ratio = (rows[-1][2] / h1) if rows else float("nan")
        rows.append((n, l2, h1, energy))
        print(f"{n:>5} {h:>9.4f} {l2:>12.3e} {h1:>12.3e} "
              f"{ratio:>8.2f} {energy:>12.6f} {J_STAR - energy:>12.3e}")

    # 断言①:H¹ 误差相邻比 ≈ 2(理论 O(h) 一阶收敛;Γ-收敛的定量指纹)
    for k in range(2, len(rows)):
        r = rows[k - 1][2] / rows[k][2]
        assert 1.7 < r < 2.3, f"H¹ 相邻收敛比偏离 2: {r:.3f}"

    # 断言②:最细网格 H¹ 误差 < 最粗的 1/10(实际约 1/32)
    assert rows[-1][2] < rows[0][2] / 10.0, "加密网格未达到收敛预期"

    print("-" * 72)
    print(f"全部断言通过 ✓   H¹ 误差比(粗→细) = {rows[0][2] / rows[-1][2]:.1f}× "
          f"(一阶收敛,理论 32×)")
    print("解读:直接法给存在性,Γ-收敛给正确性,线性代数给解——三层一个脚本。")
    print("     J(u_h) → J* 单调逼近但恒 ≥ J*:极小化序列的 lim inf 语法在数值侧显形。")


if __name__ == "__main__":
    main()
