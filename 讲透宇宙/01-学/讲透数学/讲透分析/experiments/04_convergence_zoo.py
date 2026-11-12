# -*- coding: utf-8 -*-
"""收敛速度动物园：二分（1阶）/牛顿（2阶）/割线（1.618阶）求 √2。

04 章 · 分析转代码 配套实验。纯标准库。

收敛阶 p 的定义：e_{n+1} ≈ C·e_n^p ⟹ log e_{n+1} ≈ p·log e_n
实测相邻误差的 log 比 = 阶数。

跑法: python3 -u experiments/04_convergence_zoo.py
"""
import math


def bisect(f, a, b, n):
    for _ in range(n):
        m = (a + b) / 2
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
    return (a + b) / 2


def newton(f, df, x0, n):
    x = x0
    for _ in range(n):
        x = x - f(x) / df(x)
    return x


def secant(f, x0, x1, n):
    a, b = x0, x1
    for _ in range(n):
        fa, fb = f(a), f(b)
        c = b - fb * (b - a) / (fb - fa)
        a, b = b, c
    return b


def track_errors(iterates, exact):
    """误差序列：触及机器精度地板(1e-14)即截断——之后是噪声不是数学。"""
    out = []
    for x in iterates:
        e = abs(x - exact)
        if e < 1e-14:
            break
        out.append(e)
    return out


def order_from(errs):
    """实测阶数：e2 ≈ C·e1^p ⟹ p = log(e2)/log(e1)（相邻对均值）。"""
    ratios = []
    for e1, e2 in zip(errs, errs[1:]):
        if 0 < e2 < 1 and 0 < e1 < 1:
            ratios.append(math.log(e2) / math.log(e1))
    return sum(ratios) / len(ratios) if ratios else float("nan")


def main():
    f = lambda x: x * x - 2
    df = lambda x: 2 * x
    exact = math.sqrt(2)

    print("=" * 62)
    print("收敛速度动物园：求 √2（收敛阶 = 数值世界的利率）")
    print("=" * 62)

    # 二分：误差每步减半（1 阶）
    xs, a, b = [], 1.0, 2.0
    for _ in range(30):
        m = (a + b) / 2
        xs.append(m)
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
    eB = track_errors(xs, exact)
    print(f"二分法:   最后误差 {eB[-1]:.2e}   实测阶 ≈ {order_from(eB):.2f}（理论 1）")

    # 牛顿：误差平方（2 阶）
    xs, x = [], 1.5
    for _ in range(8):
        x = x - f(x) / df(x)
        xs.append(x)
    eN = track_errors(xs, exact)
    print(f"牛顿法:   最后误差 {eN[-1]:.2e}   实测阶 ≈ {order_from(eN):.2f}（理论 2）")

    # 割线：φ 阶
    a_, b_, xs = 1.0, 2.0, []
    for _ in range(12):
        fa, fb = f(a_), f(b_)
        if fb == fa or abs(fb) < 1e-15:
            break                       # 已收敛到机器精度，再除就是噪声
        c = b_ - fb * (b_ - a_) / (fb - fa)
        a_, b_ = b_, c
        xs.append(c)
    eS = track_errors(xs, exact)
    print(f"割线法:   最后误差 {eS[-1]:.2e}   实测阶 ≈ {order_from(eS):.2f}（理论 φ≈1.618）")
    print()
    print("牛顿误差序列（平方自乘的目击）：")
    for e in eN[:6]:
        print(f"  {e:.3e}")
    print("→ 每步有效位数×2：1e-1 → 1e-2 → 1e-4 → 1e-8 → 1e-16（double 到顶）")
    print()
    print("利率表（达到 1e-12 各需几步）：")
    for name, errs in (("二分", eB), ("割线", eS), ("牛顿", eN)):
        steps = next((i + 1 for i, e in enumerate(errs) if e < 1e-12), None)
        print(f"  {name}: {steps} 步")
    print("→ 阶数的差 = 步数的指数差——收敛阶为什么是数值分析的货币 💡")


if __name__ == "__main__":
    main()
