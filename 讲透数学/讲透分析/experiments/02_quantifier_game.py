# -*- coding: utf-8 -*-
"""ε-δ 作为可执行对局：逐点 vs 一致连续的 δ 探测。

02 章 · 语言特征 配套实验。纯标准库。

连续:    ∀x ∀ε ∃δ ∀y   —— δ 可以依赖 x
一致连续: ∀ε ∃δ ∀x ∀y   —— 一个 δ 通吃全域
x² 在 ℝ: δ(ε,x) = ε/(2|x|+1)——x 越大 δ 越小，全局 δ 不存在

跑法: python3 -u experiments/02_quantifier_game.py
"""


def delta_for(f, x, eps, x_probe_lo, x_probe_hi):
    """对局应答方：二分搜索最大可行 δ（窗口半径，探测限于 [lo,hi]）。"""
    def feasible(d):
        for sgn in (+1, -1):
            y = x + sgn * d
            if x_probe_lo <= y <= x_probe_hi and abs(f(y) - f(x)) >= eps:
                return False
        return True
    lo, hi = 1e-9, min(5.0, (x_probe_hi - x_probe_lo) / 2)
    for _ in range(60):                     # δ 二分：凸函数下单调可行
        mid = (lo + hi) / 2
        if feasible(mid):
            lo = mid
        else:
            hi = mid
    return lo


def main():
    f = lambda x: x * x
    g = lambda x: 2 * x          # 线性对照：Lipschitz ⟹ 全局 δ 存在
    EPS = 0.1

    print("=" * 62)
    print("ε-δ 对局：对手固定 ε=0.1，应答方给 δ")
    print("=" * 62)
    print(f"{'x':>8} {'δ(x²)':>10} {'δ(2x)':>10}   （探测窗 [x-5, x+5]）")
    for x in (0.5, 2, 8, 32, 128, 512):
        d_sq = delta_for(f, x, EPS, x - 5, x + 5)
        d_li = delta_for(g, x, EPS, x - 5, x + 5)
        print(f"{x:>8} {d_sq:>10.4f} {d_li:>10.4f}")
    print()
    print("读数：")
    print("  · 线性函数 2x：δ ≈ ε/2 = 0.05 处处成立——全局 δ 存在 ⟹ 一致连续 ✓")
    print("  · x²：δ 随 x 增大持续缩水（理论 δ ≈ ε/(2x)）——每个点都有 δ（连续 ✓）")
    print("    但 inf_x δ(x) = 0——量词 ∀x∀ε∃δ 的 δ 被允许逐点挑，")
    print("    换成 ∀ε∃δ∀x 就挑不出来了 ⟹ 不一致连续（经典 x² 事实的数值实拍）")
    print()
    print("=" * 62)
    print("对照：有界闭区间上一切连续函数自动一致连续（Heine-Cantor）")
    print("=" * 62)
    print(f"{'区间':>14} {'x² 的最小 δ':>12}")
    for lo, hi in ((0, 1), (0, 10), (0, 100)):
        dmin = min(delta_for(f, x, EPS, lo, hi)
                   for x in [lo + (hi - lo) * k / 40 for k in range(41)])
        print(f"[{lo},{hi}]".rjust(14), f"{dmin:>12.5f}")
    print("→ 有界闭区间上 min δ > 0（紧性把逐点 δ 兑换成全局 δ）——")
    print("  Heine-Cantor 定理 = 03 章「紧性=无穷兑换有限」的语言学前传 💡")


if __name__ == "__main__":
    main()
