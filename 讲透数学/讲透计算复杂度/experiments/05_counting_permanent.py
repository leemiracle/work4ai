#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_counting_permanent.py — #P 的体感：permanent vs 行列式（05 章）

Valiant 1979：0/1 矩阵的 permanent（= 完美匹配数，#P-完全）与
行列式（P，高斯消元）的公式只差每置换的正负号——计算命运天壤之别。
本实验在小规模上蛮力对照两者，并断言 permanent 恰等于完美匹配计数。

断言：permanent(M) == 蛮力数出的完美匹配数（逐实例验证）；
      det(M) 与 permanent(M) 数值无规律关联（差距可指数）。
"""
import itertools
import random
from fractions import Fraction


def permanent_bf(m) -> int:
    """蛮力 permanent：Σ_σ Π_i m[i][σ(i)]，n! 次乘加。"""
    n = len(m)
    total = 0
    for perm in itertools.permutations(range(n)):
        prod = 1
        for i in range(n):
            prod *= m[i][perm[i]]
        total += prod
    return total


def perfect_matchings_bf(m) -> int:
    """数完美匹配：枚举行到列的双射且全为 1。"""
    n = len(m)
    cnt = 0
    for perm in itertools.permutations(range(n)):
        if all(m[i][perm[i]] == 1 for i in range(n)):
            cnt += 1
    return cnt


def det_exact(m) -> Fraction:
    """整数精确行列式（分数高斯消元，Bareiss 可选，小规模够用）。"""
    n = len(m)
    a = [[Fraction(v) for v in row] for row in m]
    sign, result = 1, Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign = -sign
        result *= a[col][col]
        inv = a[col][col]
        for r in range(col + 1, n):
            factor = a[r][col] / inv
            if factor:
                for c in range(col, n):
                    a[r][c] -= factor * a[col][c]
    return sign * result


def main():
    random.seed(42)
    print("n | permanent(=匹配数) | det | 猜想核对")
    print("--|-------------------|-----|---------")
    for n in range(2, 8):
        for trial in range(3):
            m = [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]
            per, mat = permanent_bf(m), perfect_matchings_bf(m)
            det = det_exact(m)
            assert per == mat, f"permanent {per} ≠ 匹配数 {mat}！"
            if trial == 0:
                print(f"{n} | {per:>17} | {det:>3} | per==匹配数 ✓")
    # 演示"判定在 P、计数 #P-完全"的最小对照
    m = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]        # 有完美匹配
    assert perfect_matchings_bf(m) == 2
    print("\n对照: 判定'存在完美匹配' ∈ P（霍普克洛夫特-卡普）；")
    print("      数出匹配数 = permanent 是 #P-完全（Valiant 1979）——")
    print("      同一张邻接矩阵，'有吗'与'有几个'隔开整个 #P 世界。")
    print("断言通过：permanent 恒等于完美匹配计数；与 det 无数值关联。")


if __name__ == "__main__":
    main()
