# -*- coding: utf-8 -*-
"""椭圆曲线群律:素域 F_p 上「一条曲线 = 一个群」的现场实测。

00 章·体系结构(美之时刻④)/ 04 章·代数几何转代码 配套实验。纯标准库。

E: y² = x³ + ax + b over F_p,点加 = 割线/切线几何规则的代数化:
  P+Q = 「连线第三交点」关于 x 轴的镜像;单位元是无穷远点 O。
本脚本逐条断言:封闭性/交换律/逆元/结合律抽查、群阶落 Hasse 界内。

跑法: python experiments/00_elliptic_curve.py
"""
from math import isqrt

P, A, B = 97, 2, 3          # E: y² = x³+2x+3 over F_97(判别式非零,非奇异)
INF = None                   # 无穷远点 O = 群单位元


def discriminant_ok():
    """非奇异检查:4a³+27b² ≠ 0 (mod p)——奇点=群律崩塌区(04 章反直觉①)。"""
    return (4 * A**3 + 27 * B**2) % P != 0


def on_curve(pt):
    if pt is INF:
        return True
    x, y = pt
    return (y * y - (x**3 + A * x + B)) % P == 0


def all_points():
    """暴力点枚举:O 加上所有满足方程的 (x,y) ∈ F_p²。"""
    pts = [INF]
    for x in range(P):
        rhs = (x**3 + A * x + B) % P
        for y in range(P):
            if (y * y) % P == rhs:
                pts.append((x, y))
    return pts


def add(p1, p2):
    """割线/切线规则:P+Q = 连线第三交点的镜像。"""
    if p1 is INF:
        return p2
    if p2 is INF:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return INF                                  # 垂直线:第三交点在无穷远
    if p1 == p2:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P     # 切线斜率
    else:
        lam = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P      # 割线斜率
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def mul(k, pt):
    """标量乘 kP(双加法)——ECC 的核心原语。"""
    res = INF
    while k:
        if k & 1:
            res = add(res, pt)
        pt = add(pt, pt)
        k >>= 1
    return res


def main():
    assert discriminant_ok(), "判别式为零:曲线奇异,群律不成立"
    pts = all_points()
    N = len(pts)

    print("=" * 64)
    print(f"E: y² = x³ + {A}x + {B}  over  F_{P}")
    print("=" * 64)

    # ── 群公理逐条实测 ──────────────────────────────────────
    # 1) 封闭性:任意两点之和仍在曲线上(全对断言,97 点规模可暴力)
    for p1 in pts:
        for p2 in pts:
            assert on_curve(add(p1, p2)), f"封闭性失败: {p1}+{p2}"
    print(f"[1] 封闭性: {N}×{N} 全对检查通过(几何连线规则永不跑出曲线)")

    # 2) 单位元与逆元
    assert all(add(INF, p) == p for p in pts), "单位元失效"
    assert all(add(p, (p[0], (-p[1]) % P)) is INF for p in pts if p != INF), "逆元失效"
    print("[2] 单位元 O / 逆元 (x,-y): 通过")

    # 3) 交换律(全对) + 结合律(抽查)
    assert all(add(p1, p2) == add(p2, p1) for p1 in pts for p2 in pts), "交换律失效"
    g = pts[1] if pts[0] is INF and len(pts) > 1 else pts[0]
    h, k_ = pts[2], pts[3]
    assert add(add(g, h), k_) == add(g, add(h, k_)), "结合律抽查失败"
    print(f"[3] 交换律(全对) / 结合律(抽查 {g}+{h}+{k_}): 通过")

    # ── 群阶与 Hasse 界 ─────────────────────────────────────
    lo, hi = P + 1 - 2 * isqrt(P), P + 1 + 2 * isqrt(P)
    print()
    print(f"[4] 群阶 N = {N}(暴力点计数)")
    print(f"    Hasse 界: [{lo}, {hi}]  (|N-(p+1)| ≤ 2√p ≈ {2*isqrt(P)})")
    assert lo <= N <= hi, f"Hasse 界被击穿: N={N}"
    print("    N 落界内 ✓ —— 上同调机器(ζ 函数)的结论,小素数域就能摸到")

    # ── Lagrange:元素阶整除群阶;标量乘原语 ──────────────────
    order_g = 1
    q = g
    while q is not INF:
        q = add(q, g)
        order_g += 1
    assert N % order_g == 0, f"Lagrange 失败: |g|={order_g} 不整除 N={N}"
    assert mul(order_g, g) is INF and mul(0, g) is INF and mul(1, g) == g
    print(f"[5] 生成元阶 |g| = {order_g} 整除 N={N}(Lagrange);标量乘 kP 自检通过")
    print()
    print("结论:方程的解集自己就是一个交换群 —— 「一条曲线 = 一个群」实证完毕")


if __name__ == "__main__":
    main()
