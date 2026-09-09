# -*- coding: utf-8 -*-
"""Euler 示性数的三张面孔:组合 / 几何 / 代数。

00 章·体系结构 与 04 章·转代码 配套实验。纯标准库。

面孔1(组合): χ = V − E + F        —— 多面体与曲面格点三角剖分
面孔2(亏格): χ = 2 − 2g           —— 球面 g=0 ⟹ 2;环面 g=1 ⟹ 0
面孔3(代数): χ = b0 − b1 + b2 − … —— 单纯复形的 Betti 数交错和(Euler–Poincaré)

跑法: python3 -u experiments/00_euler_characteristic.py
"""
from itertools import combinations

# ---------------- 面孔 1:经典多面体 V−E+F ----------------
# 数据:顶点坐标仅示意;棱/面用索引表(计数用)
POLYHEDRA = {
    "四面体":   (4,  6,  4),
    "立方体":   (8, 12,  6),
    "八面体":   (6, 12,  8),
    "二十面体": (12, 30, 20),
}

# ---------------- 面孔 2:曲面格点三角剖分 ----------------
def torus_grid(m=12, n=9):
    """环面三角剖分:m×n 格点 (i,j)~(i+m,j+n)。返回 (V,E,F) 计数。

    直觉:把方形纸先卷成圆筒、再弯成轮胎;格点在两对边处被「粘合」。
    顶点 m*n;每格 2 个三角形 ⟹ 面 2mn;每格 3 条边、每边被 2 格共享 ⟹ 棱 3mn。
    """
    V = m * n
    F = 2 * m * n
    E = 3 * m * n
    return V, E, F

def sphere_grid():
    """球面剖分:二十面体表面(12 顶点/30 棱/20 面)。

    细分不变性:任何细分 χ 守恒(细分是拓扑形变),故取最简剖分即可。
    """
    return 12, 30, 20

def genus2_cw():
    """亏格 2 曲面(双环面):标准八边形粘合的 CW 计数。

    构造:八边形按边词 a b a⁻¹ b⁻¹ c d c⁻¹ d⁻¹ 成对同向粘合——
    8 条边两两粘成 4 条棱,8 个角粘成 1 个顶点,面就是八边形本身。
    χ(M#N) = χ(M)+χ(N)−2:两个环面各挖一盘再缝合 ⟹ 0+0−2 = −2。
    """
    return 1, 4, 1   # V, E, F(CW 胞腔计数,χ = 1−4+1 = −2)

# ---------------- 面孔 3:单纯复形 Betti 数(GF(2)) ----------------
def boundary_matrix(simplices, k):
    """C_k 的边界矩阵 ∂_k:行=C_{k-1} 单纯形,列=C_k 单纯形,GF(2) 系数。

    ∂(单纯形) = 所有「去掉一个顶点」的面之和(模 2)。
    """
    faces = [s for s in simplices if len(s) == k]          # C_{k-1}:k 个顶点
    cols = [s for s in simplices if len(s) == k + 1]       # C_k:k+1 个顶点
    face_index = {s: i for i, s in enumerate(faces)}
    mat = []
    for face in faces:
        row = []
        for s in cols:
            cnt = sum(1 for v in s if (s - {v}) == face)   # 面是否为 s 的边界片
            row.append(cnt % 2)
        mat.append(row)
    return mat

def gf2_rank(mat):
    """GF(2) 高斯消元求秩。"""
    A = [r[:] for r in mat]
    rank, rows, cols = 0, len(A), len(A[0]) if A else 0
    for c in range(cols):
        piv = next((r for r in range(rank, rows) if A[r][c]), None)
        if piv is None:
            continue
        A[rank], A[piv] = A[piv], A[rank]
        for r in range(rows):
            if r != rank and A[r][c]:
                A[r] = [(x ^ y) for x, y in zip(A[r], A[rank])]
        rank += 1
    return rank

def betti(simplices, k):
    """b_k = dim ker ∂_k − rank ∂_{k+1}  (GF(2),有限复形)。"""
    n_cols = sum(1 for s in simplices if len(s) == k + 1)  # dim C_k
    r_k = gf2_rank(boundary_matrix(simplices, k))          # rank ∂_k
    r_k1 = gf2_rank(boundary_matrix(simplices, k + 1))     # rank ∂_{k+1}
    return (n_cols - r_k) - r_k1

# ---------------- 三个复形(顶点用 frozenset) ----------------
def simplex_sphere_boundary():
    """S² 的单纯模型:四面体的表面(4 个三角面,不含内部 3-单纯形)。"""
    V = range(4)
    faces = [frozenset(c) for c in combinations(V, 3)]
    edges = [frozenset(c) for c in combinations(V, 2)]
    verts = [frozenset({v}) for v in V]
    return verts + edges + faces

def simplex_torus(m=4, n=4):
    """环面三角剖分:标准 m×n 格点两两粘边(顶点 (i,j) 按 (i+m, j+n) 等同)。

    每个方格切两刀成两个三角形;m,n ≥ 3 时无退化单纯形。
    计数:V=mn, E=3mn, F=2mn ⟹ χ=0;Betti 应为 (1,2,1)。
    """
    def vid(i, j):
        return (i % m) * n + (j % n)          # 粘合:坐标 mod (m,n)
    verts = [frozenset({vid(i, j)}) for i in range(m) for j in range(n)]
    edges, faces = set(), set()
    for i in range(m):
        for j in range(n):
            a, b, c, d = vid(i, j), vid(i + 1, j), vid(i, j + 1), vid(i + 1, j + 1)
            for tri in ((a, b, c), (b, d, c)):
                assert len({a, b, c, d}) == 4, "m,n 过小导致退化三角形"
                faces.add(frozenset(tri))
                for e in combinations(sorted(tri), 2):
                    edges.add(frozenset(e))
    return verts + [frozenset(e) for e in edges] + [frozenset(f) for f in faces]

def simplex_circle(n=6):
    """S¹:多边形边界。"""
    verts = [frozenset({i}) for i in range(n)]
    edges = [frozenset({i, (i + 1) % n}) for i in range(n)]
    return verts + edges

# ---------------- main ----------------
def main():
    print("=" * 64)
    print("面孔 1:多面体 χ = V − E + F")
    print("=" * 64)
    for name, (V, E, F) in POLYHEDRA.items():
        print(f"  {name:<6} χ = {V}−{E}+{F} = {V - E + F}")
    assert all(V - E + F == 2 for V, E, F in POLYHEDRA.values()), "凸多面体应全为 2"
    print("  → 凸多面体 χ ≡ 2(与球面同胚:欧拉多面体公式=拓扑不变量)")

    print()
    print("=" * 64)
    print("面孔 2:曲面 χ = 2 − 2g(亏格 g=洞的个数)")
    print("=" * 64)
    V, E, F = sphere_grid()
    print(f"  球面细分格点:χ = {V}−{E}+{F} = {V - E + F}   (期望 2)")
    assert V - E + F == 2
    V, E, F = torus_grid()
    print(f"  环面 m×n 格点:χ = {V}−{E}+{F} = {V - E + F}     (期望 0)")
    assert V - E + F == 0
    V, E, F = genus2_cw()
    print(f"  双环面八边形粘合:χ = {V}−{E}+{F} = {V - E + F:+d}   (期望 −2)")
    assert V - E + F == -2
    print("  → χ 把「洞的个数」压缩成一个数:g = (2−χ)/2")

    print()
    print("=" * 64)
    print("面孔 3:单纯复形 Betti 数交错和(Euler–Poincaré)")
    print("=" * 64)
    for name, cx, expect in [
        ("圆 S¹",     simplex_circle(),        (1, 1, 0)),
        ("球面 S²",   simplex_sphere_boundary(), (1, 0, 1)),
        ("环面 T²",   simplex_torus(),          (1, 2, 1)),
    ]:
        bs = [betti(cx, k) for k in range(3)]
        chi = bs[0] - bs[1] + bs[2]
        print(f"  {name}:Betti = {bs}   χ = {chi:+d}")
        assert tuple(bs) == expect, f"{name} Betti 应为 {expect},实得 {bs}"
    print("  → 圆(1 个 1 维洞)/球面(1 个空腔)/环面(2 个圆环洞+1 个空腔)")
    print("     三张面孔在数字上重合:V−E+F = 2−2g = Σ(−1)^k b_k")
    print()
    print("结论:χ 同时是组合对象、几何对象、代数对象——")
    print("      这就是「不变量」思想的现场表演(00 章 §七)。")


if __name__ == "__main__":
    main()
