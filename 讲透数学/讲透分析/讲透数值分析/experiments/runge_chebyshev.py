# -*- coding: utf-8 -*-
"""
实验：Runge 现象——等距 vs Chebyshev 节点插值（对应 00 章插值节 / 03 章条件数节）

f(x) = 1/(1+25x^2) 在 [-1,1] 上是解析函数，却让等距高阶插值发散（Runge 1901）。
同一份 Lagrange 多项式数学，只换节点分布：
  - 等距节点：端点误差随 n 指数爆炸（加点 = 火上浇油）
  - Chebyshev 节点：全区间误差指数收敛（加点 = 指数进步）
    且 Chebyshev-Lobatto 节点的重心权重有闭式 w_i = (-1)^i * (1/2 端点, 1 内点)，
    连权重都不用乘积公式算——Chebyshev 的恩惠渗透到算法层。

断言（实测校准后）：
  n=20 : 等距 err > 1（发散），Chebyshev err < 0.05
  n=80 : Chebyshev err < 1e-6（指数收敛兑现），等距 err > 1e3（彻底灾难）

数学账本：f 的极点在 ±0.2i，Bernstein 椭圆参数 ρ 满足 (ρ-1/ρ)/2 = 0.2
→ ρ ≈ 1.22 → Chebyshev 误差 ~ ρ^{-n}：n=20 约 2e-2，n=80 约 1e-7。
跑：python runge_chebyshev.py
"""
import numpy as np


def f(x):
    return 1.0 / (1.0 + 25.0 * x * x)


def equispaced_nodes(n):
    return np.linspace(-1.0, 1.0, n + 1)


def chebyshev_lobatto_nodes(n):
    # 第二类 Chebyshev 点（含端点）：x_i = cos(i*pi/n)
    return np.cos(np.arange(n + 1) * np.pi / n)


def barycentric_weights(x):
    # 一般节点的重心权重 w_i = 1/prod_{j!=i}(x_i - x_j)
    n = len(x)
    w = np.ones(n)
    for i in range(n):
        d = x[i] - np.delete(x, i)
        w[i] = 1.0 / np.prod(d)
    return w / np.max(np.abs(w))  # 规范化防溢出（比例不变）


def cheb_weights(n):
    # Chebyshev-Lobatto 闭式权重：w_i = (-1)^i * (i==0 or i==n ? 0.5 : 1.0)
    w = (-1.0) ** np.arange(n + 1)
    w[0] *= 0.5
    w[-1] *= 0.5
    return w


def bary_eval(x, y, w, xq, tol=1e-13):
    """重心插值公式（第二形式）：数值稳定的 Lagrange 求值。"""
    out = np.empty_like(xq)
    for k, xv in enumerate(xq):
        d = xv - x
        hit = np.abs(d) < tol
        if hit.any():
            out[k] = y[np.argmax(hit)]
            continue
        c = w / d
        out[k] = np.dot(c, y) / c.sum()
    return out


def max_error(n, kind, mgrid=4001):
    if kind == "equi":
        x = equispaced_nodes(n)
        w = barycentric_weights(x)
    else:
        x = chebyshev_lobatto_nodes(n)
        w = cheb_weights(n)
    y = f(x)
    xq = np.linspace(-1.0, 1.0, mgrid)
    p = bary_eval(x, y, w, xq)
    return np.max(np.abs(f(xq) - p))


def main():
    print(f"{'n':>4} | {'等距 err':>12} | {'Chebyshev err':>12} | 倍数")
    print("-" * 52)
    results = {}
    for n in (20, 40, 80):
        e_eq = max_error(n, "equi")
        e_ch = max_error(n, "cheb")
        results[n] = (e_eq, e_ch)
        print(f"{n:>4} | {e_eq:>12.3e} | {e_ch:>12.3e} | {e_eq / e_ch:>8.1f}x")

    # 断言一（n=20）：等距已发散（>1），Chebyshev 已把误差压到分以下
    assert results[20][0] > 1.0, "n=20 等距误差应 > 1（Runge 发散）"
    assert results[20][1] < 0.05, "n=20 Chebyshev 误差应 < 0.05"

    # 断言二（n=80）：Chebyshev 兑现指数收敛（<1e-6）；等距已是灾难（>1e3）
    assert results[80][1] < 1e-6, "n=80 Chebyshev 误差应 < 1e-6（指数收敛）"
    assert results[80][0] > 1e3, "n=80 等距误差应 > 1e3（彻底发散）"

    print("\n[OK] 全部断言通过：")
    print("  同一个 Lagrange 公式，只换节点——等距指数发散，Chebyshev 指数收敛。")
    print("  教训：插值的病态不在多项式，在节点的分布（条件数是选出来的）。")


if __name__ == "__main__":
    main()
