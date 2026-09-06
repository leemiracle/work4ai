# -*- coding: utf-8 -*-
"""完备化即构造：可计算实数（2⁻ⁿ 精度柯西列）的最小实现。

03 章 · 可构造与结构 配套实验。纯标准库（分数精确算术）。

实数 = 精度供应合同：函数 n ↦ 有理数 qₙ，承诺 |qₙ − x| ≤ 2⁻ⁿ
√2 用整数开方（逐位二分）履约——它是对象，不是数。

跑法: python3 -u experiments/03_constructive_reals.py
"""
from fractions import Fraction


class CReal:
    """可计算实数：柯西列 modulus 2^-n 的合同持有者。"""

    def __init__(self, supply):
        self.supply = supply          # n -> Fraction，|q_n - x| <= 2^-n

    def approx(self, n):
        return self.supply(n)

    def _binop(self, other, op_q):
        # 加/减的合同：|a±b - (aₙ±bₙ)| ≤ 2⁻ⁿ+2⁻ⁿ = 2·2⁻ⁿ ⟹ 先各取 n+1 位
        return CReal(lambda n: op_q(self.supply(n + 1), other.supply(n + 1)))

    def __add__(self, o):
        return self._binop(o, lambda a, b: a + b)

    def __sub__(self, o):
        return self._binop(o, lambda a, b: a - b)

    def __mul__(self, o):
        # |a·b - aₙbₙ| ≤ |a||b-aₙ| + |bₙ||a-aₙ| + ... 需要幅值界：
        # 先取 m 位估幅值 |a|,|b| ≤ M，再取 n 位 → 误差 ≤ 2M·2^{-n+1}
        def supply(n):
            M = max(abs(self.supply(4)), abs(o.supply(4)), Fraction(1)) + 1
            k = n + M.numerator.bit_length() + 2     # 幅值补偿的位数
            return self.supply(k) * o.supply(k)
        return CReal(supply)

    def show(self, n):
        """按需打印：x 的 2^-n 精度有理近似。"""
        return self.approx(n)


def sqrt2_supply(n):
    """√2 的履约：整数二分求 a 使 a² ≤ 2·4ⁿ < (a+1)² ⟹ a/2ⁿ 距 √2 ≤ 2⁻ⁿ。"""
    scale = 1 << n          # 2^n
    target = 2 * scale * scale
    lo, hi = 0, scale * 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= target:
            lo = mid
        else:
            hi = mid - 1
    return Fraction(lo, scale)


def pi_supply(n):
    """π 的履约：Leibniz 级数（慢但合同诚实：截断误差 ≤ 下一项）。"""
    # 需要 |S - π| ≤ 2^-n：Leibniz 余项 ≤ 1/(2N+3)，取 N 使其 ≤ 2^-(n+1)
    need = Fraction(1, 2 ** (n + 3))   # ×4 后仍 ≤ 2^-n
    N = 1
    while Fraction(1, 2 * N + 3) > need:
        N += 1
    s = Fraction(0)
    for k in range(N):
        s += Fraction((-1) ** k, 2 * k + 1)
    return 4 * s   # Leibniz 收敛到 π/4


def main():
    print("=" * 62)
    print("完备化即构造：可计算实数（2⁻ⁿ 精度合同）")
    print("=" * 62)
    r2 = CReal(sqrt2_supply)
    pi = CReal(pi_supply)
    print(f"√2 的合同履约：")
    for n in (2, 5, 10, 20, 40):
        print(f"  2^-{n:<3}精度: {r2.show(n)}  (≈{float(r2.show(n)):.12f})")
    print(f"π 的合同履约（Leibniz 慢但诚实）:")
    for n in (2, 4, 8):
        print(f"  2^-{n:<3}精度: ≈{float(pi.show(n)):.8f}")
    print()
    print("域运算（合同级联）：")
    s = r2 + r2
    p = r2 * r2
    print(f"  √2+√2 在 2⁻²⁰ 精度: {float(s.show(20)):.10f}（应≈2.8284271247）")
    print(f"  √2×√2 在 2⁻²⁰ 精度: {float(p.show(20)):.10f}（应≈2.0000000000）")
    print("  → 每次运算重新谈判合同（多要一位精度补偿）——完备化的算法面容")
    print()
    print("Specker 警示（03 章）：")
    print("  可计算实数构成域 ✓，但**不完备**：存在可计算递增有理列收敛到不可计算实。")
    print("  「极限存在」≠「极限可计算」——分析转代码的第一道裂缝 💡")


if __name__ == "__main__":
    main()
