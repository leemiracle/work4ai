# -*- coding: utf-8 -*-
"""Gauss-Bonnet 三连测:同一本账的三种曲率记法。

00 章 · 体系结构 / 04 章 · 转代码 配套实验。纯标准库。

三幕:
  幕一  多面体角亏(Descartes):Σ(2π−顶点处平面角) = 2π·χ —— GB 的离散原型
  幕二  球面三角形(Girard 1629):内角和−π = 面积(单位球 K=+1)
  幕三  双曲三角形(Poincaré 圆盘 K=−1):蒙特卡洛测面积 ≈ π−内角和(GB 的双曲版)

曲率符号一眼对账:欧氏 0 / 球面 + / 双曲 − —— 角盈的正负号是曲率的指纹。

跑法: python 讲透数学/讲透几何学/experiments/00_gauss_bonnet.py
"""

import math
import random

TOL = 1e-9


# ---------------------------------------------------------------- 幕一 ----
def act1_polyhedra():
    print("=" * 64)
    print("幕一 · 多面体角亏(Descartes 定理):Σ角亏 = 2π·χ")
    print("=" * 64)
    # (名称, V, E, F, 每顶点棱数 m, 每面边数 n)——正多面体每面全等、每顶点等价
    solids = [
        ("正四面体",   4,  6,  4, 3, 3),
        ("立方体",     8, 12,  6, 3, 4),
        ("正八面体",   6, 12,  8, 4, 3),
        ("正十二面体", 20, 30, 12, 3, 5),
        ("正二十面体", 12, 30, 20, 5, 3),
    ]
    print(f"{'立体':>8} {'χ=V−E+F':>10} {'角亏/顶点':>12} {'Σ角亏/(2π)':>14}")
    for name, V, E, F, m, n in solids:
        chi = V - E + F
        vertex_angle_sum = m * (n - 2) * math.pi / n      # 顶点处平面角和
        defect = 2 * math.pi - vertex_angle_sum            # 角亏
        ratio = defect * V / (2 * math.pi)
        print(f"{name:>8} {chi:>10} {defect:>12.4f} {ratio:>14.6f}")
        assert abs(ratio - chi) < TOL, f"{name}: Descartes 失败"
    print("→ 五种正多面体全部通过:Σ角亏 = 2π·χ(欧拉示性数)✓\n")


# ---------------------------------------------------------------- 幕二 ----
def act2_sphere():
    print("=" * 64)
    print("幕二 · 球面三角形(Girard):单位球上 面积 = 内角和 − π")
    print("=" * 64)
    # 三直角三角形(octant):三条两两垂直的大圆弧围成,面积理论值 4π/8 = π/2
    A = B = C = math.pi / 2
    excess = A + B + C - math.pi
    area = 4 * math.pi / 8
    print(f"三直角三角形: 内角和={A + B + C:.6f}  盈余={excess:.6f}  面积={area:.6f}")
    assert abs(excess - area) < TOL, "Girard 失败"
    # 一般极三角形:北极 + 赤道经度 0/θ 两点 —— 面积恰为 θ(月形上半)
    print(f"{'极角 θ':>8} {'内角和':>10} {'盈余=面积':>12}")
    for theta_deg in (30, 60, 90, 120):
        theta = math.radians(theta_deg)
        angles = theta + math.pi / 2 + math.pi / 2       # 极点角 θ + 两赤道直角
        e = angles - math.pi                              # = θ
        print(f"{theta_deg:>7}° {angles:>10.6f} {e:>12.6f}")
        assert abs(e - theta) < TOL
    print("→ 盈余=面积逐例成立;内角和全部 >π ✓(正曲率的指纹)\n")


# ---------------------------------------------------------------- 幕三 ----
class GeodesicSide:
    """Poincaré 圆盘的一条测地边(弧或直径),能判侧、能取端点切向。

    两点 a,b 的测地线:若 a,b 与原点共线 ⟹ 直径段;否则是与单位圆正交的圆弧。
    正交圆:圆心 c 满足 c·a=(|a|²+1)/2 与 c·b=(|b|²+1)/2,半径²=|c|²−1。
    """

    def __init__(self, a, b):
        self.a, self.b = a, b
        det = a[0] * b[1] - a[1] * b[0]
        if abs(det) < 1e-12:                     # 共线 ⟹ 直径
            self.diameter = True
            return
        self.diameter = False
        r1 = (a[0] ** 2 + a[1] ** 2 + 1) / 2
        r2 = (b[0] ** 2 + b[1] ** 2 + 1) / 2
        self.c = ((r1 * b[1] - r2 * a[1]) / det,
                  (a[0] * r2 - b[0] * r1) / det)
        self.r2 = self.c[0] ** 2 + self.c[1] ** 2 - 1   # R² = |c|²−1

    def side(self, p):
        """p 在边的哪一侧(符号;0 视为正)。"""
        if self.diameter:
            d = (self.b[0] - self.a[0], self.b[1] - self.a[1])
            cross = d[0] * (p[1] - self.a[1]) - d[1] * (p[0] - self.a[0])
            return 1.0 if cross >= 0 else -1.0
        v = (p[0] - self.c[0]) ** 2 + (p[1] - self.c[1]) ** 2 - self.r2
        return 1.0 if v >= 0 else -1.0

    def tangent_at(self, v, toward):
        """边在端点 v 处、指向 toward 的单位切向量(共形度量⟹双曲角=欧氏角)。"""
        if self.diameter:
            d = (toward[0] - v[0], toward[1] - v[1])
            n = math.hypot(*d)
            return (d[0] / n, d[1] / n)
        dx, dy = v[0] - self.c[0], v[1] - self.c[1]
        for t in ((-dy, dx), (dy, -dx)):
            if t[0] * (toward[0] - v[0]) + t[1] * (toward[1] - v[1]) > 0:
                n = math.hypot(*t)
                return (t[0] / n, t[1] / n)
        n = math.hypot(dx, dy)
        return (-dy / n, dx / n)


def act3_hyperbolic():
    print("=" * 64)
    print("幕三 · 双曲三角形(Poincaré 圆盘,K=−1):面积 = π − 内角和")
    print("=" * 64)
    random.seed(42)
    cases = [
        ((-0.5, 0.0), (0.5, 0.0), (0.0, 0.5)),    # 含一条直径边
        ((-0.6, -0.2), (0.3, 0.4), (0.1, -0.55)), # 三条弧边
        ((-0.75, 0.0), (0.75, 0.0), (0.0, 0.75)), # 顶点更近边界(角和更小)
    ]
    print(f"{'case':>5} {'内角和':>9} {'π−角和':>10} {'MC面积':>9} {'相对误差':>9}")
    for k, verts in enumerate(cases):
        sides = [GeodesicSide(verts[i], verts[(i + 1) % 3]) for i in range(3)]

        # 顶点角:两条相邻边在顶点处的切向夹角(取指向各自另一端)
        ang_sum = 0.0
        for i in range(3):
            v = verts[i]
            prev_t = sides[(i - 1) % 3].tangent_at(v, verts[(i - 1) % 3])
            next_t = sides[i].tangent_at(v, verts[(i + 1) % 3])
            dot = max(-1.0, min(1.0,
                       prev_t[0] * next_t[0] + prev_t[1] * next_t[1]))
            ang_sum += math.acos(dot)
        theo = math.pi - ang_sum

        # 蒙特卡洛:包围盒采样,落入测地三角形则累加面积密度 4/(1−|z|²)²
        xs, ys = [v[0] for v in verts], [v[1] for v in verts]
        xlo, xhi = min(xs) - 0.15, max(xs) + 0.15
        ylo, yhi = min(ys) - 0.15, max(ys) + 0.15
        n_tot, acc = 400000, 0.0
        for _ in range(n_tot):
            p = (random.uniform(xlo, xhi), random.uniform(ylo, yhi))
            inside = all(
                sides[i].side(p) == sides[i].side(verts[(i + 2) % 3])
                for i in range(3))
            if inside:
                acc += 4.0 / (1.0 - (p[0] ** 2 + p[1] ** 2)) ** 2
        mc_area = acc / n_tot * (xhi - xlo) * (yhi - ylo)
        err = abs(mc_area - theo) / theo
        print(f"{k:>5} {ang_sum:>9.4f} {theo:>10.4f} {mc_area:>9.4f} {err:>9.3%}")
        assert ang_sum < math.pi, "双曲三角形内角和必须 <π"
        assert err < 0.08, f"蒙特卡洛误差过大: {err:.2%}"
    print("→ 内角和全部 <π,且 蒙特卡洛面积 ≈ π−内角和 ✓(负曲率的指纹)")
    print("  对照:球面 角和>π/盈余=面积;双曲 角和<π/亏损=面积——")
    print("  Gauss-Bonnet 在 K=+1、0(幕一)、−1 三种世界记的是同一本账 💡")


if __name__ == "__main__":
    act1_polyhedra()
    act2_sphere()
    act3_hyperbolic()
    print("\n全部断言通过:GB 三连测 ALL OK")
