#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_time_hierarchy.py — 时间谱系定理的预算体感（01 章）

固定运算预算 B，对每个增长率 f 求"预算内可处理的最大输入规模"。
谱系定理保证 DTIME(f) ⊊ DTIME(f·log f·loglog f)——本实验展示这个
"严格分离"在实践预算里意味着什么：相邻增长率之间是数量级的鸿沟。

断言：同一预算下，多项式谱系的相邻层可解规模严格分离（比值 > 10）。
"""
import math

GROWTHS = [
    ("n",       lambda n: n),
    ("n·log₂n", lambda n: n * max(1, math.ceil(math.log2(n)))),
    ("n²",      lambda n: n * n),
    ("n³",      lambda n: n ** 3),
    ("2ⁿ",      lambda n: 2 ** n),
]

BUDGETS = [10 ** 6, 10 ** 9]


def max_solvable(cost, budget: int) -> int:
    """二分搜索最大的 n 使 cost(n) ≤ budget（cost 单调不减）。"""
    lo, hi = 1, 2
    while cost(hi) <= budget:
        hi *= 2
        if hi > 10 ** 12:
            return hi
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if cost(mid) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return lo


def main():
    rows = []
    for budget in BUDGETS:
        row = [max_solvable(f, budget) for _, f in GROWTHS]
        rows.append((budget, row))
        print(f"\n预算 B = 10^{int(math.log10(budget))}:")
        for (name, _), n in zip(GROWTHS, row):
            print(f"    {name:>8} → 可解规模 n* ≈ {n:.0e}")

    # 断言一：同一预算下，相邻多项式层的可解规模分离至少一个数量级
    for budget, row in rows:
        for i in range(len(row) - 2):          # 多项式侧相邻比较（2ⁿ 另算）
            ratio = row[i] / row[i + 1]
            assert ratio >= 10, f"预算{budget}: {GROWTHS[i][0]} vs {GROWTHS[i+1][0]} 分离不足一个量级"
    # 断言二（层级的主课）：预算 ×1000 时——多项式类的 n* 涨 ≥10 倍；
    #                       2ⁿ 的 n* 只按对数爬（≤2 倍）——指数世界对预算麻木
    small, big = rows[0][1], rows[1][1]
    for i in range(len(GROWTHS) - 1):
        assert big[i] / small[i] >= 10, f"{GROWTHS[i][0]}: 预算×1000 应换来 n*×10+"
    assert big[-1] / small[-1] <= 2, "2ⁿ 的 n* 不该对预算敏感"
    print("\n断言通过：① 同预算下相邻增长率差 ≥1 个数量级；")
    print("② 预算×1000：n 的 n*×1000、n² 的 n*×~32、n³ 的 n*×10——2ⁿ 的 n* 只 +10 左右。")
    print("谱系定理的'严格包含'落到预算上：多项式层随预算爬坡，指数层原地踏步。")
    print("注意：实验给直觉，不给证明——谱系定理断言的是存在性分离。")


if __name__ == "__main__":
    main()
