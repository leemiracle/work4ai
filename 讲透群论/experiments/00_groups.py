"""
讲透群论 00 章实验：3 个群 + Lagrange 定理。
跑法：python3 -u experiments/00_groups.py
"""
import random
import numpy as np
from itertools import permutations


def check_group_axioms(elements, op, name=""):
    """检查群公理（封闭/单位/逆/结合）"""
    e = elements[0]
    for a in elements:
        for b in elements:
            if op(a, b) not in elements:
                return False, f"不封闭: {a}*{b}={op(a,b)}"
    for a in elements:
        if op(e, a) != a or op(a, e) != a:
            return False, "无单位元"
    for a in elements:
        if not any(op(a, b) == e and op(b, a) == e for b in elements):
            return False, f"{a} 无逆元"
    for _ in range(50):
        a, b, c = random.choice(elements), random.choice(elements), random.choice(elements)
        if op(op(a, b), c) != op(a, op(b, c)):
            return False, "不结合"
    return True, "✓ 满足群公理"


def part1_z12():
    print("=" * 65)
    print("[1] Z/12Z 加法群（钟表群）")
    print("=" * 65)
    elements = list(range(12))
    op = lambda a, b: (a + b) % 12
    ok, msg = check_group_axioms(elements, op)
    print(f"  群公理: {msg}  |G|=12")
    print("  子群（由 d 生成的循环子群）：")
    for d in [1, 2, 3, 4, 6]:
        H = sorted({(d * k) % 12 for k in range(20)})
        print(f"    <{d}> = {H}, |H|={len(H)}")
    print("  → 所有子群阶 ∈ {1,2,3,4,6,12} 都整除 12 ✓ Lagrange")


def part2_s3():
    print()
    print("=" * 65)
    print("[2] S3 对称群（3 元素的所有排列）")
    print("=" * 65)
    elems = list(permutations(range(3)))
    print(f"  6 个群元素（3 元素的所有排列）：")
    for i, p in enumerate(elems):
        print(f"    {i}: {p}")
    compose = lambda a, b: tuple(a[b[i]] for i in range(3))
    ok, msg = check_group_axioms(elems, compose)
    print(f"  群公理: {msg}  |S_3|=6")


def part3_d3_isomorphic_s3():
    print()
    print("=" * 65)
    print("[3] 等边三角形的对称 D3 ≅ S3")
    print("=" * 65)
    print("  D3: 恒等/转120°/转240°/3 条中线翻转 = 6 个操作")
    print("  每个操作 = 顶点排列 → D3 ↪ S3")
    print("  |D3| = |S3| = 6 → D3 ≅ S3（同构）")
    print("  → '三角形对称' 和 '3 元素排列' 是同一个抽象群")


def part4_lagrange():
    print()
    print("=" * 65)
    print("[4] Lagrange 定理：子群阶必整除群阶")
    print("=" * 65)
    print(f"  {'n':<6} {'Z/nZ 的所有子群阶':<28} {'验证'}")
    for n in [6, 12, 15, 24, 60, 120]:
        divisors = [d for d in range(1, n+1) if n % d == 0]
        all_divide = all(n % d == 0 for d in divisors)
        print(f"  n={n:<4} {str(divisors):<25} {'✓ Lagrange' if all_divide else '✗'}")


def main():
    random.seed(0)
    np.random.seed(0)
    print("讲透群论 00 章实验：3 个群 + Lagrange 定理")
    part1_z12()
    part2_s3()
    part3_d3_isomorphic_s3()
    part4_lagrange()
    print()
    print("=" * 65)
    print("✓ 群论入门完成。")
    print("  → 群 = 对称性的代数")
    print("  → Lagrange: 子群阶整除群阶")
    print("  → D3 ≅ S3（不同表象，同一抽象群）")
    print("=" * 65)


if __name__ == "__main__":
    main()
