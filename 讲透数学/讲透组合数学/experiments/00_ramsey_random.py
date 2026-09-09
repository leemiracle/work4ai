# -*- coding: utf-8 -*-
"""Ramsey 的蒙特卡洛实拍 + 生成函数的系数提取。

00/04 章 配套实验。纯标准库(random/itertools/math)。

Part 1  Ramsey:概率方法的可执行化身
  · R(3,3)=6 的两半:K₅ 存在逃逸染色(理论 12/1024 ≈ 1.17%),K₆ 无处可逃
  · 单色 K₄ 频率表:阈值随 n 的爬升(真值 R(4,4)=18,随机染色远够不着)
  · Erdős 随机下界 vs 已知真值:第一矩法给出的下界与事实的差距 = 显式构造的难
Part 2  生成函数:把序列装进函数,再取回来
  · F(x)=x/(1-x-x²) 系数(卷积迭代)vs Binet 闭式
  · Catalan:递推 vs 闭式 C_n = C(2n,n)/(n+1)

跑法: python experiments/00_ramsey_random.py
"""

import itertools
import math
import random

TRIANGLES = {}   # n -> 三角形边三元组列表
K4S = {}         # n -> K4 的顶点四元组列表


def triangles(n):
    if n not in TRIANGLES:
        TRIANGLES[n] = list(itertools.combinations(range(n), 3))
    return TRIANGLES[n]


def k4s(n):
    if n not in K4S:
        K4S[n] = list(itertools.combinations(range(n), 4))
    return K4S[n]


def edges(n):
    return list(itertools.combinations(range(n), 2))


def has_mono_kt(n, t, colors):
    """colors: dict 边->0/1。检查是否存在单色 K_t。"""
    subsets = triangles(n) if t == 3 else [k for k in k4s(n) if t == 4]
    if t == 3:
        return any(colors[(a, b)] == colors[(b, c)] == colors[(a, c)]
                   for a, b, c in subsets)
    return any(len({colors[(a, b)] for a, b in itertools.combinations(s, 2)}) == 1
               for s in subsets)


def random_coloring(n, rng):
    es = edges(n)
    return dict(zip(es, (rng.randint(0, 1) for _ in es)))


def part1_ramsey():
    rng = random.Random(20260906)
    bar = "=" * 64
    print(bar)
    print("Part 1 · Ramsey 蒙特卡洛:R(3,3)=6 的两半")
    print(bar)

    # K5:逃逸染色(无单色三角形)的经验频率 —— 理论值 12/1024
    trials = 40000
    escaped = sum(1 for _ in range(trials)
                  if not has_mono_kt(5, 3, random_coloring(5, rng)))
    p_emp = escaped / trials
    p_theory = 12 / 1024
    print(f"K₅ 随机染色 {trials} 次:逃逸 {escaped} 次")
    print(f"  经验频率 {p_emp:.5f} vs 理论 12/1024 = {p_theory:.5f}"
          f"(相对偏差 {abs(p_emp - p_theory) / p_theory:.1%})")
    assert escaped >= 1, "K₅ 必然存在逃逸染色(R(3,3)=6 的下半场)"
    assert abs(p_emp - p_theory) / p_theory < 0.10, "经验频率应贴近 12/1024"

    # K6:必中(R(3,3)=6 的上半场)
    trials6 = 3000
    hits = sum(1 for _ in range(trials6)
               if has_mono_kt(6, 3, random_coloring(6, rng)))
    print(f"K₆ 随机染色 {trials6} 次:含单色三角形 {hits} 次(必然)")
    assert hits == trials6, "R(3,3)=6 ⇒ K₆ 无处可逃"
    print("→ 无序必藏序:K₅ 还能靠 C₅ 双五边形染色逃逸(约 1.17%),")
    print("  K₆ 起任意染色必含单色三角——规模强加秩序。\n")

    print("-" * 64)
    print("单色 K₄ 频率表(随机染色,样本 1500)")
    print(f"{'n':>4} {'P(含单色K₄)':>12}   E[单色K₄数]=C(n,4)/32")
    for n in (6, 8, 10, 12, 14):
        tr = 1500
        cnt = sum(1 for _ in range(tr)
                  if has_mono_kt(n, 4, random_coloring(n, rng)))
        print(f"{n:>4} {cnt / tr:>12.3f}   {math.comb(n, 4) / 32:>10.2f}")
    print("→ 期望值 C(n,4)/32 在 n=14 已达 31;而 R(4,4)=18 意味着 K₁₇ 仍存在")
    print("  完全逃逸的染色——稀有事件,随机采样摸不到(第一矩法失明区)。\n")

    print("-" * 64)
    print("Erdős 随机下界 vs 已知真值(第一矩法:要求 C(n,t)·2^{1-C(t,2)} < 1)")
    print(f"{'t':>3} {'随机下界 n*+1':>12} {'已知 R(t,t)≥':>12}   差距")
    for t, true_lb in ((3, 6), (4, 8), (5, 43)):
        n_star = 1
        while math.comb(n_star + 1, t) * 2 ** (1 - math.comb(t, 2)) < 1:
            n_star += 1
        print(f"{t:>3} {n_star + 1:>12} {true_lb:>12}   "
              f"随机证明只到真值的 {100 * (n_star + 1) // true_lb}%")
    print("→ 差距=显式构造的难度:随机图轻易做到的事,写下来的图差指数级。")

    # 阶段断言:t=4 时第一矩法至少给出 R(4,4) ≥ 7(经典真值 18)
    n4 = 1
    while math.comb(n4 + 1, 4) * 2 ** (1 - math.comb(4, 2)) < 1:
        n4 += 1
    assert n4 + 1 >= 6


def part2_generating_functions():
    bar = "=" * 64
    print()
    print(bar)
    print("Part 2 · 生成函数:装进去,取回来")
    print(bar)

    # F(x) = x/(1-x-x^2):系数 = [0,1,1,2,3,5,...](Fibonacci 偏移一位)
    N = 30
    a = [0] * (N + 1)
    a[1] = 1
    for n in range(2, N + 1):
        a[n] = a[n - 1] + a[n - 2]          # 系数递推=函数方程的逐项比对
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    print("F(x)=x/(1-x-x²) 的系数 vs Binet 闭式 (φⁿ-ψⁿ)/√5:")
    for n in (5, 10, 20, 30):
        binet = (phi ** n - psi ** n) / math.sqrt(5)
        print(f"  n={n:>2}: 系数 {a[n]:>8} | Binet {binet:>12.4f}")
        assert abs(a[n] - binet) < 1e-6, "生成函数系数必须逐项命中闭式"

    # Catalan:C(x) = 1 + x·C(x)² ⇒ c_{n+1} = Σ c_i c_{n-i};闭式 C(2n,n)/(n+1)
    M = 20
    c = [0] * (M + 1)
    c[0] = 1
    for n in range(M):
        c[n + 1] = sum(c[i] * c[n - i] for i in range(n + 1))
    print("\nC(x)=(1-√(1-4x))/(2x) 的系数 vs 闭式 C(2n,n)/(n+1):")
    for n in (5, 10, 15, 20):
        closed = math.comb(2 * n, n) // (n + 1)
        print(f"  n={n:>2}: 递推 {c[n]:>10} | 闭式 {closed:>10}")
        assert c[n] == closed, "Catalan 递推与闭式必须逐项相等"
    print("→ 递推(离散)与闭式(连续)在每一个系数上合流——")
    print("  「把序列装进函数」不是比喻,是逐项可断言的机器检查。")


if __name__ == "__main__":
    part1_ramsey()
    part2_generating_functions()
    print("\n[ALL ASSERTS PASSED] Ramsey 蒙特卡洛 + 生成函数系数提取 全部命中。")
