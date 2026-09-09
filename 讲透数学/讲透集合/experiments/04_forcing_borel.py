# -*- coding: utf-8 -*-
"""力迫=迭代对角化 + Borel code 解释器——集合论转代码双实验。

04 章 · 转代码 配套实验。纯标准库。

跑法: python3 -u experiments/04_forcing_borel.py
"""
from fractions import Fraction


# ═══════════════════════════════════════════════════════
# 实验 A：Borel code 解释器（描述集合论的程序观）
# 空间 = ℚ（有理数），基础开集 = 开区间
# ═══════════════════════════════════════════════════════
# code 语法树:
#   ("interval", a, b)      开区间 (a,b)，a/b 为 Fraction
#   ("compl", c)            补
#   ("union", c1, c2)       并
#   ("bigunion", mk, n)     前可数并 ⋃_{k<n} mk(k)——演示用截断 n，注释见半可判定说明


def borel_member(code, x):
    """判定 x ∈ Borel(code)。树递归。"""
    op = code[0]
    if op == "interval":
        _, a, b = code
        return a < x < b
    if op == "compl":
        return not borel_member(code[1], x)
    if op == "union":
        return borel_member(code[1], x) or borel_member(code[2], x)
    if op == "bigunion":
        _, mk, n = code
        return any(borel_member(mk(k), x) for k in range(n))
    raise ValueError(op)


def singleton(q):
    """{q} 的 Borel code：(-∞,q) ∪ (q,∞) 的补。"""
    return ("compl", ("union", ("interval", Fraction(-10**9), q),
                      ("interval", q, Fraction(10**9))))


def partA_borel():
    print("=" * 62)
    print("实验 A：Borel code 解释器（ℚ 上的 Borel 集即程序）")
    print("=" * 62)
    # S = {1/k : k ≥ 1}——可数多个单点集的并
    S_code = ("bigunion", lambda k: singleton(Fraction(1, k + 1)), 200)
    tests = [Fraction(1, 3), Fraction(1, 10), Fraction(2, 7), Fraction(1), Fraction(0)]
    print("集合 S = {1/k : k≥1}（可数并 code，演示截断 k<200）")
    for x in tests:
        print(f"  {str(x):>5} ∈ S ? {borel_member(S_code, x)}")
    print()
    print("半可判定现象（02 章 Σ₁ 的直投影）:")
    print("  x = 2/7：演示截断下'不在'的判定依赖截断上限——完整可数并的判定中，")
    print("  '在'一侧必然停机（找到 k 即停），'不在'一侧要搜尽无穷多个 k。")
    print("  ⟹ Borel code 的成员判定天然是半可判定的——这就是可定义性层级的计算代价 💡")
    print()


# ═══════════════════════════════════════════════════════
# 实验 B：力迫 = 迭代对角化（Rasiowa–Sikorski 的算法内核）
# 条件 = 实数位的有限片段；密集集 = "逃离第 i 个可计算序列"的要求
# ═══════════════════════════════════════════════════════

def computable_seq(i):
    """第 i 个'可计算序列'（演示用可数族：i 的二进制位模式周期延拓等）。"""
    if i == 0:
        return lambda n: 0                      # 全 0
    if i == 1:
        return lambda n: 1                      # 全 1
    if i == 2:
        return lambda n: n % 2                  # 0101…
    # 一般 i：i+1 的二进制表示做周期
    bits = bin(i + 1)[2:]
    return lambda n: int(bits[n % len(bits)])


def partB_forcing():
    print("=" * 62)
    print("实验 B：力迫 = 迭代对角化（Cohen 式泛型构造）")
    print("=" * 62)
    N = 24          # 实数位长（演示用有限窗口；真泛型是 ω 位）
    K = 12          # 要逃离的可计算序列个数
    seqs = [computable_seq(i) for i in range(K)]

    print(f"条件 = {N} 位实数的有限片段；密集集 D_i = 强迫 g ≠ 第 i 个可计算序列")
    print(f"逃离目标（可计算序列族，共 {K} 个）:")
    for i in range(K):
        preview = "".join(str(seqs[i](n)) for n in range(10))
        print(f"  a_{i} = {preview}…")

    # 迭代对角化：第 i 轮选一个"新鲜"坐标（对角线+1 错位），令 g 的该位 ≠ aᵢ 的该位
    g = {}
    witnesses = {}
    for i in range(K):
        n = i + 1  # 对角线坐标 1,2,3,…（0 位留给 D_0 之外的要求）
        while n in g:            # 该位已被先前轮次占用 → 后移
            n += 1
        g[n] = 1 - seqs[i](n)    # 强迫：g(n) ≠ aᵢ(n)
        witnesses[i] = n
    # 补满未定位（全部置 0——这些位不被任何要求约束）
    for n in range(N):
        g.setdefault(n, 0)

    bits = "".join(str(g[n]) for n in range(N))
    print(f"\n构造出的'泛型' g = {bits}")
    print(f"（在逃离约束之外的位置，g 的取值是自由的——演示里填 0）")
    print("\n验证：g 逃逸每个 aᵢ（找到见证坐标）:")
    ok = 0
    for i in range(K):
        n = witnesses[i]
        assert g[n] != seqs[i](n)
        ok += 1
    print(f"  {ok}/{K} 个序列全部被逃逸 ✓（见证坐标 = 对角线错位 {sorted(witnesses.values())[:8]}…）")
    print()
    print("对照领悟:")
    print("  · 单轮'选位翻转' = 一次对角论证（00 章实验③的逃逸集）")
    print("  · 串联 K 轮逐个满足密集集 = Rasiowa–Sikorski（可数密集集可算法相遇）")
    print("  · 完整力迫把 K→ω 再跑到不可数个密集集——那里算法断供，靠存在性论证")
    print("  · 所以：对角论证是力迫的一步特例，力迫是对角化的超穷串联 💡")
    print()
    print("推论验证：g 不等于任何可计算序列 ⟹ g 本身非可计算")
    print(f"  （每个可计算序列都在逃逸名单上；g 逃逸了全部 {K} 个演示成员）")


if __name__ == "__main__":
    partA_borel()
    partB_forcing()
