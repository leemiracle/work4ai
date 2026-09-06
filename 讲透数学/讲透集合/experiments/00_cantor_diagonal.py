# -*- coding: utf-8 -*-
"""对角论证生成器——集合论的引擎三次点火。

00 章 · 体系结构 配套实验。纯标准库，无第三方依赖。

跑法: python3 -u experiments/00_cantor_diagonal.py

三连演示:
  ① |N| = |Q|   分数不比整数多（对角走格盘枚举一切既约分数）
  ② |N| < |R|   任何实数枚举都能被"反实数"逃逸（二进制对角翻转）
  ③ |X| < |P(X)| Cantor 定理：任何 f:X->P(X) 都有逃逸集（罗素悖论的驯化版）
"""
from fractions import Fraction
from itertools import islice
from math import gcd


def enumerate_q():
    """对角枚举一切非负既约分数：沿反对角线扫格盘，跳过非既约。

    格点 (p, q) 按对角线 p+q=1,2,3,... 逐条扫——这就是"对角"的本义。
    """
    d = 1
    while True:
        for p in range(d + 1):
            q = d - p
            if q == 0:
                continue  # 分母为零，跳过
            if gcd(p, q) != 1:
                continue  # 非既约（0/2 与 0/1 重复），跳过
            yield Fraction(p, q)
        d += 1


def part1_q_countable():
    print("=" * 62)
    print("① |N| = |Q| —— 分数和整数一样多")
    print("=" * 62)
    qs = list(islice(enumerate_q(), 20))
    print(f"对角枚举前 20 个非负既约分数:")
    print("  " + ", ".join(str(f) for f in qs))
    # 验证双射性：枚举无重复（既约保证）、且任意给定分数会在有限步内出现
    target = Fraction(17, 23)
    for i, f in enumerate(enumerate_q()):
        if f == target:
            print(f"定位测试: 17/23 出现在枚举的第 {i} 位（对角线 d=40 上）")
            break
    print("→ 每个分数都有编号 ⟹ |Q| ≤ |N|；又 N ⊆ Q ⟹ |N| = |Q|   ✅\n")


def flip(b):
    return "1" if b == "0" else "0"


def part2_reals_uncountable():
    print("=" * 62)
    print("② |N| < |R| —— 任何实数枚举都会被反实数逃逸")
    print("=" * 62)
    # 造一个"看起来很密"的 [0,1) 实数枚举：二进制小数 0.b1b2b3...
    # 第 n 个数故意让第 n 位多样化（n mod 3 → 001 循环），证明对角法不挑枚举
    def nth_real_bits(n):
        return "".join("1" if ((k * 7 + n) % 5 == 0) else ("0" if (n + k) % 3 else "1")
                       for k in range(12))

    enum = [nth_real_bits(n) for n in range(12)]
    print("假设有人声称枚举了 [0,1) 的全体实数，前 12 个（二进制位）:")
    for i, bits in enumerate(enum):
        print(f"  r_{i} = 0.{bits}")
    anti = "".join(flip(enum[n][n]) for n in range(12))
    print(f"反实数 d = 0.{anti}")
    print("逐位比对：d 与 r_n 在第 n 位必然相反")
    for n in range(12):
        mark = "≠" if anti[n] != enum[n][n] else "="  # 按构造恒为 ≠
        print(f"  d 第 {n} 位 {anti[n]} {mark} r_{n} 第 {n} 位 {enum[n][n]}")
    print("→ d ∉ {r_n}，但它明明是 [0,1) 里的实数 ⟹ 枚举永不完备   ✅")
    print("→ 同一台机器: 罗素悖论 / 哥德尔不完备 / 停机问题   💡\n")


def part3_cantor_theorem():
    print("=" * 62)
    print("③ Cantor 定理 |X| < |P(X)| —— 任何 f:X→P(X) 都有逃逸集")
    print("=" * 62)
    X = ["a", "b", "c", "d"]
    # 任意（这里故意造一个"很聪明"的）f：让每个像集都尽量贴近全空间
    f = {
        "a": {"a", "b", "c"},
        "b": {"b", "c", "d"},
        "c": {"a", "c"},
        "d": set(),
    }
    S = {x for x in X if x not in f[x]}   # 逃逸集 S = {x : x ∉ f(x)}
    print(f"X = {X}")
    for x in X:
        print(f"  f({x}) = {sorted(f[x]) if f[x] else '∅'}")
    print(f"逃逸集 S = {{x ∈ X : x ∉ f(x)}} = {sorted(S)}")
    print("见证检查：S ≠ f(x₀) 的见证元素 x₀ =")
    for x in X:
        inside = x in S
        infx = x in f[x]
        print(f"  x₀={x}: x₀∈S? {'是' if inside else '否'} | x₀∈f(x₀)? {'是' if infx else '否'}"
              f" ⟹ S 与 f({x}) 在 {x} 上不同")
    print("→ S 与每个 f(x) 都有元素分歧 ⟹ S 不在 f 的值域里")
    print("→ 没有 X→P(X) 的满射 ⟹ |X| < |P(X)|，对任何 X（有限/无穷）   ✅")
    print("→ 把 X 换成全体集合: S 就是罗素集——悖论被驯化成定理   💡\n")


if __name__ == "__main__":
    part1_q_countable()
    part2_reals_uncountable()
    part3_cantor_theorem()
    print("三台点火完毕：同一台对角机器，三个层级的'逃逸'。")
