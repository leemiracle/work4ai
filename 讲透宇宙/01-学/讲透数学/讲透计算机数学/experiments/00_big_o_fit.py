# -*- coding: utf-8 -*-
"""大 O 实测与停机对角化:计算机数学的两条腿一次跑完。

00-体系结构.md(反直觉·加速定理背景)与 04-计算机数学转代码.md(实测 vs 理论)配套实验。
纯标准库,自带断言自验证。

Part 1  大 O 拟合:快排/归并(n log n)与冒泡(n²)计时,
        最小二乘拟合两条理论曲线,断言拟合优度排序正确——
        「大 O 不是玄学,是可实测的几何」。
Part 2  停机对角化玩具:对任意候选判定器 H,构造 D=「问 H(D),反着做」,
        逻辑表逐格检查,断言三个判定器全被反杀——
        亲手执行 1936 年图灵的「构造性不可能证明」。

跑法: python experiments/00_big_o_fit.py
"""

import random
import statistics
import time

# ─────────────────────────── Part 1: 大 O 拟合 ───────────────────────────


def bubble(a):
    a = a[:]
    n = len(a)
    for i in range(n):
        done = True
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                done = False
        if done:
            break
    return a


def quick(a):
    if len(a) <= 1:
        return a[:]
    p = a[len(a) // 2]
    lo = [x for x in a if x < p]
    eq = [x for x in a if x == p]
    hi = [x for x in a if x > p]
    return quick(lo) + eq + quick(hi)


def merge(a):
    if len(a) <= 1:
        return a[:]
    m = len(a) // 2
    l, r = merge(a[:m]), merge(a[m:])
    out, i, j = [], 0, 0
    while i < len(l) and j < len(r):
        if l[i] <= r[j]:
            out.append(l[i]); i += 1
        else:
            out.append(r[j]); j += 1
    return out + l[i:] + r[j:]


def timeit_med(fn, a, reps=3):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn(a)
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts)


def fit_r2(xs, ys, basis):
    """最小二乘拟合 y ≈ c·basis(x) + b,返回 R²。basis: 向量基函数。"""
    n = len(xs)
    f = [basis(x) for x in xs]
    fm, ym = sum(f) / n, sum(ys) / n
    vf = sum((v - fm) ** 2 for v in f)
    c = sum((f[k] - fm) * (ys[k] - ym) for k in range(n)) / vf
    b = ym - c * fm
    ss_res = sum((ys[k] - (c * f[k] + b)) ** 2 for k in range(n))
    ss_tot = sum((y - ym) ** 2 for y in ys)
    return 1 - ss_res / ss_tot


def part1():
    print("=" * 66)
    print("Part 1 · 大 O 实测:计时曲线 vs n·log n / n² 理论曲线")
    print("=" * 66)
    rng = random.Random(42)
    sizes_log = [5_000, 10_000, 20_000, 40_000, 80_000]     # n log n 档
    sizes_sq = [600, 1_200, 2_400, 4_800]                    # n² 档

    rows = []
    for name, fn, sizes in (("快排", quick, sizes_log),
                            ("归并", merge, sizes_log),
                            ("冒泡", bubble, sizes_sq)):
        xs, ys = [], []
        for n in sizes:
            a = [rng.randrange(10 * n) for _ in range(n)]
            t = timeit_med(fn, a)
            xs.append(n); ys.append(t)
        r2_nlogn = fit_r2(xs, ys, lambda x: x * (x.bit_length()))
        r2_n2 = fit_r2(xs, ys, lambda x: x * x)
        rows.append((name, r2_nlogn, r2_n2))
        line = "  ".join(f"n={n:<6}t={t:.4f}s" for n, t in zip(xs, ys))
        print(f"{name:<4} {line}")
        print(f"      R²(n·log n)={r2_nlogn:.4f}   R²(n²)={r2_n2:.4f}")

    print()
    print("断言:每算法的正确模型 R²>0.9,且正确模型严格胜出错误模型")
    for name, r_log, r_sq in rows:
        if name == "冒泡":
            assert r_sq > 0.90 and r_sq > r_log, (name, r_sq, r_log)
        else:
            assert r_log > 0.90 and r_log > r_sq, (name, r_log, r_sq)
    print("  ✓ 快排/归并贴住 n·log n,冒泡贴住 n²——大 O 是可实测的几何\n")


# ─────────────────────────── Part 2: 停机对角化 ───────────────────────────


def simulate(prog, steps=200):
    """玩具程序 = 状态转移函数:state→next 或 None(停机)。返回 'halts'/'runs'。"""
    s = 0
    for _ in range(steps):
        s = prog(s)
        if s is None:
            return "halts"
    return "runs"


def make_diagonal(H):
    """D = 对角机器:先冻结 H 对 D 的判定,然后**反着做**。

    构造次序(避免无穷回归的关键):H 只做静态分析(不执行被测程序),
    所以 H(D) 可以先算;D 的转移规则由这个冻结判定决定:
    预测 runs → D 立即停(错);预测 halts → D 永动(错)。
    """
    cell = {"pred": "halts"}                     # 观察期缺省(H 不执行 D,读不到这步)

    def D(s):
        return None if cell["pred"] == "runs" else s + 1

    cell["pred"] = H(D)                          # 冻结判定,此后 D 行为完全确定
    D.pred = cell["pred"]                        # 携带判定,供反杀核验读取
    return D


def part2():
    print("=" * 66)
    print("Part 2 · 停机对角化玩具:任何判定器 H 都会被 D=「反着做」反杀")
    print("=" * 66)

    def finite(s):                               # 一步即停
        return None
    def forever(s):                              # 永动
        return s + 1

    deciders = {
        "H₁ 偶 id 玄学(纯迷信)": lambda p: "halts" if id(p) % 2 == 0 else "runs",
        "H₂ 白名单保守(只信认识 finite)": lambda p: "halts" if p is finite else "runs",
        "H₃ 乐观全停(平凡程序全判对)": lambda p: "runs" if p is forever else "halts",
    }

    print("为什么 H 只能静态分析?若 H 靠『模拟 D』判定——D 的行为取决于 H 的判定,")
    print("H 的判定又要跑 D——观察引发无穷回归。这正是本实验第一版的真实事故:")
    print("『边跑边问』的判定器在自指面前当场爆栈。而图灵的论证更强:")
    print("**无论 H 多聪明,只要它敢给出明确判定,反着做的 D 就能反杀。**\n")

    trivial_scores = []
    for label, H in deciders.items():
        score = (H(finite) == "halts") + (H(forever) == "runs")
        D = make_diagonal(H)
        pred, actual = D.pred, simulate(D, 200)
        defeated = pred != actual
        print(f"{label}")
        print(f"    平凡程序得分 {score}/2;对角机器 D:预测 {pred:5} 实际 {actual:5}"
              f" → {'反杀 ✓' if defeated else 'D 躲过了?!'}")
        print()
        trivial_scores.append(score)
        assert defeated, "对角化失败——这不该发生"

    assert max(trivial_scores) == 2, "至少应有一个判定器在平凡程序上全对(H₃)"

    print("读数:")
    print("  · H₃ 在平凡程序上 2/2 全对——照样被 D 反杀:不可能性不是因为启发式不够好,")
    print("    而是『给出判定 ⟹ 存在反例机器』的逻辑必然。")
    print("  · 这就是图灵 1936 的构造性不可能证明:不是抽象论证,是")
    print("    【亲手造一台骗过你的机器】。测试永远不能穷尽的数学根源。\n")


if __name__ == "__main__":
    part1()
    part2()
    print("ALL OK")
