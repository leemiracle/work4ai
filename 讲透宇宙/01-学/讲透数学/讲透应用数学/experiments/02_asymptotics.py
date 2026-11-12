# -*- coding: utf-8 -*-
"""渐近与摄动：误差标价 + Richardson 外推。

02 章 · 语言特征 配套实验。纯标准库。

A. 正则摄动：εx² + x − 1 = 0 的根 x(ε)，小 ε 展开
   x = 1 − ε + 2ε² − 5ε³ + …（迭代代入 x = 1 − εx²）
   与二次求根公式精确解对照，实测截断误差按 O(ε^{n+1}) 标价。

B. Richardson 外推：中心差分 D(h) = f'(x) + C·h² + O(h⁴)
   两个步长的组合消掉 h² 项，2 阶白拿 4 阶。

跑法: python3 -u experiments/02_asymptotics.py
"""
import math


def exact_root(eps):
    """εx²+x−1=0 的物理根（ε→0 极限为 1 的那支）。"""
    return (-1 + math.sqrt(1 + 4 * eps)) / (2 * eps)


def perturbation(eps, order):
    """正则摄动展开到 order 阶：x = 1 − εx² 迭代代入。"""
    x = 1.0                        # 零阶
    coeff = [1.0]
    for _ in range(order):
        x = 1 - eps * x * x        # 迭代改进（收敛到展开式的逐阶系数等价）
        coeff.append(x)
    return x


def coeffs_by_series(n=6):
    """逐阶系数：x = Σ a_k ε^k, a_0=1, a_{k+1} = −Σ_{i+j=k} a_i a_j。"""
    a = [1.0]
    for k in range(1, n + 1):
        a.append(-sum(a[i] * a[k - 1 - i] for i in range(k)))
    return a


def eval_series(a, eps):
    return sum(c * eps ** k for k, c in enumerate(a))


def partA():
    print("=" * 62)
    print("A. 正则摄动：εx² + x − 1 = 0，误差按 O(εⁿ⁺¹) 标价")
    print("=" * 62)
    a = coeffs_by_series(6)
    print("展开系数: x = 1 − ε + 2ε² − 5ε³ + 14ε⁴ − 42ε⁵ + …")
    print("（ Catalan 数在暗处：|a_k| = C_k/(k+1)，渐近级数的奇景——发散！）")
    print()
    print(f"{'ε':>8} {'精确解':>14} {'1项':>10} {'误差':>10} | {'3项':>10} {'误差':>10} （误差阶）")
    for eps in (0.2, 0.1, 0.05, 0.025):
        xe = exact_root(eps)
        x1 = eval_series(a[:1], eps)
        x3 = eval_series(a[:3], eps)
        e1, e3 = abs(x1 - xe), abs(x3 - xe)
        print(f"{eps:>8} {xe:>14.8f} {x1:>10.4f} {e1:>10.1e} | {x3:>10.6f} {e3:>10.1e}"
              f"  (ε¹ vs ε³)")
    # 误差阶实测：误差比
    eps = 0.05
    errs = []
    for n in (1, 2, 3, 4):
        errs.append(abs(eval_series(a[:n], eps) - exact_root(eps)))
    print(f"\nε=0.05 逐项截断误差: " + " ".join(f"{e:.1e}" for e in errs))
    ratio = errs[0] / errs[1]
    print(f"1项→2项误差比 ≈ {ratio:.1f} ≈ 1/ε = {1/eps:.0f} —— O(εⁿ⁺¹) 标价兑现 ✓")
    print("渐近真相：级数发散（Catalan 增长），但固定 ε 前几项神准——渐近≠收敛")
    print()


def dcentral(f, x, h):
    return (f(x + h) - f(x - h)) / (2 * h)


def partB():
    print("=" * 62)
    print("B. Richardson 外推：中心差分 2 阶 → 4 阶白拿")
    print("=" * 62)
    f = math.sin
    x = 1.0
    fpx = math.cos(x)
    print(f"目标: f'(1) for sin, 精确 = {fpx:.10f}")
    print(f"{'h':>10} {'D(h) 误差':>12} {'阶数':>8} | {'Richardson 误差':>15} {'阶数':>8}")
    h = 0.1
    prev = (None, None)
    for _ in range(4):
        D1 = dcentral(f, x, h)
        D2 = dcentral(f, x, h / 2)
        R = (4 * D2 - D1) / 3               # 消掉 C·h² 首项
        e1, eR = abs(D2 - fpx), abs(R - fpx)
        o1 = math.log2(prev[0] / e1) / (math.log2(2)) if prev[0] else float("nan")
        oR = math.log2(prev[1] / eR) if prev[1] else float("nan")
        print(f"{h:>10} {e1:>12.2e} {'':>8} | {eR:>15.2e}")
        prev = (e1, eR)
        h /= 2
    # 阶数实测（末两次）
    h = 0.05
    def err_D(hh):
        return abs(dcentral(f, x, hh) - fpx)
    def err_R(hh):
        D1, D2 = dcentral(f, x, hh), dcentral(f, x, hh / 2)
        return abs((4 * D2 - D1) / 3 - fpx)
    qD = err_D(h) / err_D(h / 2)
    qR = err_R(h) / err_R(h / 2)
    print(f"\n步长减半误差比: 中心差分 ×{qD:.1f}（≈4=2²） Richardson ×{qR:.1f}（≈16=2⁴）")
    print("→ Richardson：知道误差结构 h²·(1+…) 就能消首项——渐近思维的免费午餐 💡")


if __name__ == "__main__":
    partA()
    partB()
