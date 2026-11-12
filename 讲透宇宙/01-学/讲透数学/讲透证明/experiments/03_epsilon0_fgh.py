# -*- coding: utf-8 -*-
"""ε₀ 账本：序数记法、快速增长层级与 Gentzen 定价。

03 章 · 可构造与结构 配套实验。纯标准库。

序数记法（Cantor 布局法，限于 ε₀ 以下）:
  ()                    = 0
  ((α1,c1),(α2,c2),…)   = ω^α1·c1 + ω^α2·c2 + …（末项允许有限数 ω^0·k）
  基本列作用于末项（Wainer 约定）:
    (ω^β)[n]   = n+1                若 β=1
    (ω^β)[n]   = ω^δ·(n+1)          若 β=δ+1
    (ω^β)[n]   = ω^{β[n]}           若 β 为极限
    γ+ω^β·c[n] = γ+ω^β·(c-1)+(ω^β)[n]   若 c≥2

跑法: python3 -u experiments/03_epsilon0_fgh.py
"""
import math

# ── 序数记法 ──────────────────────────────────────────


def norm_cnf(terms):
    d = {}
    for a, c in terms:
        if c > 0:
            d[a] = d.get(a, 0) + c
    out = sorted(((a, c) for a, c in d.items() if c > 0),
                 key=lambda t: (tuple((cnf_key(e), c) for e, c in t[0]), t[1]),
                 reverse=True)
    return tuple(out)


def cnf_key(a):
    return tuple((cnf_key(e), c) for e, c in a)


def cnf_cmp(a, b):
    ka, kb = cnf_key(a), cnf_key(b)
    return (ka > kb) - (ka < kb)


def cnf_add(a, b):
    if not b:
        return a
    kept = [t for t in a if cnf_cmp(t[0], b[0][0]) > 0]
    return norm_cnf(list(kept) + list(b))


def omega_pow(a):
    return ((a, 1),)


def finite(n):
    return () if n == 0 else (((), n),)


ZERO = ()
ONE = finite(1)          # ω^0
TWO = finite(2)
OMEGA = omega_pow(ONE)   # ω^1 = ω
OMEGA_OMEGA = omega_pow(OMEGA)   # ω^ω


def show_cnf(a):
    if not a:
        return "0"
    parts = []
    for e, c in a:
        if e == ZERO:
            parts.append(str(c))
        else:
            base = "ω" if e == ONE else f"ω^({show_cnf(e)})"
            parts.append(base if c == 1 else f"{base}·{c}")
    return " + ".join(parts)


def is_succ(a):
    return bool(a) and a[-1][0] == ZERO


def pred_of(a):
    last_e, last_c = a[-1]
    tail = list(a[:-1])
    if last_c > 1:
        return norm_cnf(tail + [(last_e, last_c - 1)])
    return norm_cnf(tail)


def wpow_seq(beta, n):
    """(ω^β)[n]。"""
    if beta == ONE:
        return finite(n + 1)
    if is_succ(beta):
        return norm_cnf([(pred_of(beta), n + 1)])
    return omega_pow(fund_seq(beta, n))


def fund_seq(a, n):
    """极限序数 α 的基本列 α[n]——作用于末项（Wainer 约定）。"""
    assert a and not is_succ(a), "极限序数才有基本列"
    last_e, last_c = a[-1]
    rest = list(a[:-1])
    assert last_e != ZERO
    if last_c > 1:
        return norm_cnf(rest + [(last_e, last_c - 1)] + list(wpow_seq_inner(last_e, n)))
    return norm_cnf(rest + list(wpow_seq_inner(last_e, n)))


def wpow_seq_inner(beta, n):
    return wpow_seq(beta, n)


# ── 快速增长层级（有限 α 用闭式快车道 + 递归骨架）────────


SIZE_CAP = 500_000_000   # 中间量守卫：指数超过 5×10⁸（结果≈50MB+）报"增长墙"


def F(alpha, n):
    """F_α(n)：先走有限层的快车道，序数层按定义递归。"""
    if not alpha:
        return n + 1
    if is_succ(alpha):
        if len(alpha) == 1 and alpha[0][0] == ZERO:   # 纯有限序数 α=k
            return F_finite(alpha[0][1], n)
        return F_iter(pred_of(alpha), n)
    # 极限序数
    return F(fund_seq(alpha, n), n)


def F_iter(beta, n):
    """F_{β+1}(n) = F_β^n(n)。"""
    for _ in range(n):
        if n > SIZE_CAP:
            raise RuntimeError(f"增长墙：中间量已达 {n.bit_length()} 个二进制位，拒绝继续")
        n = F(beta, n)
    return n


def F_finite(k, n):
    """F_k(n) 有限层的快车道：F_0=n+1, F_1=2n, F_2=2ⁿ·n, F_{k≥3}=迭代。"""
    if k == 0:
        return n + 1
    if k == 1:
        return 2 * n
    if k == 2:
        return (1 << n) * n       # 闭式：精确且快
    for _ in range(n):
        if n > SIZE_CAP:
            raise RuntimeError(f"增长墙：中间量已达 {n.bit_length()} 个二进制位，拒绝继续")
        n = F_finite(k - 1, n)
    return n


def report(name, fn):
    try:
        v = fn()
        if isinstance(v, int) and v.bit_length() > 10 ** 5:
            digits = v.bit_length() * math.log10(2)
            print(f"  {name} = 2^{v.bit_length()-1} 级大数 ≈ 10^{digits:.2e}（{digits:,.0f} 位数）")
        else:
            print(f"  {name} = {v}")
    except RuntimeError as e:
        print(f"  {name} —— {e}")


def part1_ordinals():
    print("=" * 62)
    print("① 序数记法与算术（ε₀ 以下）")
    print("=" * 62)
    for name, a in [("0", ZERO), ("1", ONE), ("2", TWO), ("ω", OMEGA),
                    ("ω·2", norm_cnf([(ONE, 2)])), ("ω²", omega_pow(TWO)),
                    ("ω^ω", OMEGA_OMEGA), ("ω^ω·3+ω²·2+5", norm_cnf([(OMEGA_OMEGA, 3), (omega_pow(OMEGA), 2), (ZERO, 5)]))]:
        print(f"  {name:>16} = {show_cnf(a)}")
    print()
    print("  序数加法不交换:")
    print(f"    1 + ω  = {show_cnf(cnf_add(ONE, OMEGA))}")
    print(f"    ω + 1  = {show_cnf(cnf_add(OMEGA, ONE))}")
    print("  基本列（Wainer 约定，作用于末项）:")
    print(f"    ω[3]        = {show_cnf(fund_seq(OMEGA, 3))}")
    print(f"    ω²[3]       = {show_cnf(fund_seq(omega_pow(TWO), 3))}")
    print(f"    (ω^ω)[3]    = {show_cnf(fund_seq(OMEGA_OMEGA, 3))}")
    print(f"    (ω·2)[3]    = {show_cnf(fund_seq(norm_cnf([(ONE, 2)]), 3))}")
    print("  塔顶 ε₀ = sup(ω, ω^ω, ω^ω^ω, …)——本记法写不出它，这正是 Gentzen 定理的入口")
    print()


def part2_fgh():
    print("=" * 62)
    print("② 快速增长层级 F_α：从温顺到暴烈")
    print("=" * 62)
    print("  F_0(n)=n+1   F_1(n)=2n   F_2(n)=2ⁿ·n   F_3(n)=F_2⁽ⁿ⁾(n) …")
    print()
    report("F_1(3)", lambda: F_finite(1, 3))
    report("F_2(3)", lambda: F_finite(2, 3))
    report("F_2(10)", lambda: F_finite(2, 10))
    report("F_3(3)", lambda: F_finite(3, 3))
    report("F_3(4)", lambda: F_finite(3, 4))
    report("F_4(3)", lambda: F_finite(4, 3))
    print()
    report("F_ω(3)", lambda: F(OMEGA, 3))
    print("    ——F_ω(3)=F_{ω[3]}(3)=F_4(3)：第三步就撞墙（每层迭代都在乘方）")
    print()
    print("  Gentzen 定价账本:")
    print("    PA ⊢ 'F_α 是全函数' ⟺ α < ε₀")
    print("    F_1/F_2 温顺可证；F_3 起每加一层都指数级超车；")
    print("    F_ε₀ 恰好落在 PA 之外——'PA 的一致性 = ε₀ 良基'在增长层级上着陆   💡")


if __name__ == "__main__":
    part1_ordinals()
    part2_fgh()
