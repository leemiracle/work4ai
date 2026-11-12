# -*- coding: utf-8 -*-
"""L 层级与 Mostowski 塌缩——可构造性的可执行走查。

03 章 · 可构造与结构 配套实验。纯标准库。

跑法: python3 -u experiments/03_constructible_L.py
"""
from itertools import combinations

EMPTY = frozenset()


def powerset(s):
    xs = list(s)
    out = []
    for r in range(len(xs) + 1):
        out.extend(frozenset(c) for c in combinations(xs, r))
    return frozenset(out)


def build_v(n):
    vs = [EMPTY]
    for _ in range(n):
        vs.append(powerset(vs[-1]))
    return vs


# ── Part 1: Def 算子的有限实现 ─────────────────────────
# Def(M) = {X ⊆ M : X 由带参数的公式定义}
# 有限 M 上的诚实实现：枚举"参数析取公式" x=p1 ∨ ... ∨ x=pk（pi ∈ M）
# ——参数析取公式已经覆盖一切子集，故有限时 Def(M) = P(M)


def def_finite(M):
    """有限 M 上的 Def(M)：以参数析取公式实现（诚实版——只用到一种公式形状，
    但已证明（对有限 M）足以定义一切子集）。"""
    xs = sorted(M, key=lambda s: (len(s), sorted(map(repr, s), key=str)))  # 稳定序
    defined = set()
    # 枚举参数组（即 S 的所有子集的元素清单）→ 每组是一条析取公式
    for r in range(len(xs) + 1):
        for combo in combinations(xs, r):
            defined.add(frozenset(combo))  # 公式 "x=p1∨…∨x=pk" 定义出的子集
    return frozenset(defined)


def part1_L_vs_V():
    print("=" * 62)
    print("① 有限层：L_n 与 V_n 完美重合")
    print("=" * 62)
    vs = build_v(4)
    ls = [EMPTY]
    for i in range(4):
        ls.append(def_finite(ls[-1]))
    print("层 |  |V_n|  |L_n|   L_n == V_n ?")
    for n in range(5):
        same = ls[n] == vs[n]
        print(f"V{n}/L{n} |  {len(vs[n]):>4}  {len(ls[n]):>4}    {same}")
    print()
    print("原因：有限 M 上带参数的一切子集皆可定义（参数析取公式 x=p1∨…∨x=pk）")
    print("——L 与 V 的分歧不是'从小就有'，是无穷现象")
    print()
    print("ω 悬崖的账本（不可执行，只记账）:")
    print("  L_ω = V_ω = 全体遗传有限集, |·| = ℵ₀")
    print("  |L_{ω+1}| = |Def(L_ω)| ≤ ℵ₀    （公式=有限字符串，只有可数多条描述）")
    print("  |V_{ω+1}| = |P(V_ω)| = 2^ℵ₀    （幂集不讲道理，全收）")
    print("  ——从 ω+1 层起，L 永远只拿 V 的'可描述骨架'   💡")
    print()


# ── Part 2: Mostowski 塌缩器 ───────────────────────────
# 输入：图的邻接表 nodes: dict[node -> frozenset[node]]（边 y→x 表示 y ∈ x 方向自定）
# 这里约定 members[x] = x 的成员集合（x 的"下桥"）。良基 = 无环，外延 = 成员相同则同一节点


def mostowski_collapse(members):
    """良基外延结构的塌缩：节点 ↦ frozenset。

    members: dict[node, iterable[node]]（节点到其成员）
    返回 dict[node, frozenset]。
    良基性：递归必须有底——检测到环抛 ValueError。
    外延性：不同节点成员相同 ⟹ 塌缩像相同（塌缩不再是单射，如实报告）。
    """
    memo = {}
    def collapse(x, trail):
        if x in memo:
            return memo[x]
        if x in trail:
            raise ValueError(f"非良基：沿 ∈ 链回到 {x}（无限下降链/环）")
        out = frozenset(collapse(y, trail | {x}) for y in members[x])
        memo[x] = out
        return out
    for x in members:
        collapse(x, frozenset())
    return memo


def part2_collapse():
    print("=" * 62)
    print("② Mostowski 塌缩：良基外延图 ⟹ 唯一传递集合")
    print("=" * 62)
    # 图 A：三个节点 a0=∅, a1={a0}, a2={a0,a1} —— 应塌缩成序数 2 = {0,1,2}
    membersA = {"a0": [], "a1": ["a0"], "a2": ["a0", "a1"]}
    imgA = mostowski_collapse(membersA)
    zero, one, two = imgA["a0"], imgA["a1"], imgA["a2"]
    print(f"图 A: a0=[] a1=[a0] a2=[a0,a1]")
    print(f"  塌缩: a0 ↦ ∅   a1 ↦ {{∅}}   a2 ↦ {two == frozenset({EMPTY, frozenset({EMPTY})}) and '{∅,{∅}}' or two}")
    print(f"  a2 的像正好是序数 2 ✓（节点身份=成员树=身份证）")
    print()

    # 图 B：外延但换个画法——同构的图必须塌缩出同一个集合（唯一性）
    membersB = {"z": ["y", "x"], "x": [], "y": ["x"]}
    imgB = mostowski_collapse(membersB)
    print(f"图 B（换画法: z∋y,x; y∋x; x=∅）: z 塌缩 ⟹ 与图 A 的 a2 相同？ {imgB['z'] == two}")
    print(f"  ——同构的良基外延结构塌缩到同一个传递集合（唯一性）✓")
    print()

    # 图 C：非外延——两个节点成员相同（身份证重号），塌缩把她们粘合
    membersC = {"u": [], "v": [], "w": ["u", "v"]}
    imgC = mostowski_collapse(membersC)
    print(f"图 C（非外延: u,v 成员都是∅——重号）: 塌缩 u ↦ {imgC['u']}, v ↦ {imgC['v']}")
    print(f"  u 与 v 塌缩像相同：{imgC['u'] == imgC['v']}（外延性破坏 ⟹ 映射非单射，")
    print(f"  w 的像 = {imgC['w'] == one and '{∅}（u,v 被粘合成一个成员）' or imgC['w']}）")
    print(f"  ——集合世界里'成员相同'就是'同一个'，重号必须合并   💡")
    print()

    # 图 D：非良基——自环，塌缩必须报错
    membersD = {"s": ["s"]}
    try:
        mostowski_collapse(membersD)
        print("图 D（自环 s∋s）: 竟然塌缩成功?!（不可能，检查实现）")
    except ValueError as e:
        print(f"图 D（自环 s∋s）: 塌缩拒绝执行 —— {e}")
        print(f"  ——良基性是集合表示的入场券；x∈x 的世界要等非良基集合论（共归纳）")


if __name__ == "__main__":
    part1_L_vs_V()
    part2_collapse()
