#!/usr/bin/env python3
"""lab13 · μ-演算不动点：LTS 上的迭代求解（13 章 §三/§四）。
LTS：s0 -a-> s1 -a-> s2 -b-> s3；标签：s2 ⊨ p、s3 ⊨ q。
公式1 μX.(p ∨ <a>X) = "沿 a 可达 p"：从 s0 两步 a 到 s2(p) ⇒ {s0,s1,s2}
  手推锚点：μ 从 ∅ 起三轮放大 {s2}→{s1,s2}→{s0,s1,s2}（最小不动点=从种子沿 <a> 倒着灌）。
公式2 νY.(q ∧ [a]Y) = "q 且所有 a 后继仍满足 Y"：迭代收窄到 {s3}
  手推锚点：ν 从全集起四轮收窄 S→{s2,s3}→{s3}（最大不动点=从全集沿约束一层层削）。
公式3（对照）νY.(q ∧ [a]Y) 换成 μ 版 μX.(q ∧ [a]X)：s3 无 a 后继（[a]X 空真）且 ⊨q ⇒ {s3}；
  而若把 [a] 换 <a>：μX.(q ∧ <a>X) = ∅——对比出 box/diamond 与 μ/ν 的四种组合味道。
E2 CCS 手推（13 章 §一）：两进程 P = a.(b.0 + c.0)、Q = a.b.0 + a.c.0
  —— 前缀强绑定 vs 先选择后前缀：并行组合后与 a.(b.0+c.0) 的互模拟关系手推（进程树同构判定）。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from itertools import product

LTS = {
    "trans": {("s0", "a", "s1"), ("s1", "a", "s2"), ("s2", "b", "s3")},
    "labels": {"s0": set(), "s1": set(), "s2": {"p"}, "s3": {"q"}},
    "states": ["s0", "s1", "s2", "s3"],
}


def mu_p_or_diamond():
    """μX.(p ∨ <a>X)：从 ∅ 起，X ↦ {s: p(s)} ∪ {s: ∃a 到 X 中状态}，迭代至不动点。"""
    S, T, L = set(LTS["states"]), LTS["trans"], LTS["labels"]
    X = set()
    trail = []
    while True:
        nxt = {s for s in S if "p" in L.get(s, set())} | \
              {s for s in S if any((s, "a", t) in T and t in X for t in S)}
        trail.append(sorted(nxt))
        if nxt == X:
            return X, trail
        X = nxt


def nu_q_and_box():
    """νY.(q ∧ [a]Y)：从全集起，Y ↦ {s∈Y: q(s)} ∩ {s: 所有 a 后继都在 Y}，迭代至不动点。"""
    S, T, L = set(LTS["states"]), LTS["trans"], LTS["labels"]
    Y = set(S)
    trail = [sorted(Y)]
    while True:
        nxt = {s for s in Y if "q" in L.get(s, set())} & \
              {s for s in Y if all(t in Y for (s0, act, t) in T if s0 == s and act == "a")}
        trail.append(sorted(nxt))
        if nxt == Y:
            return Y, trail
        Y = nxt


def diamond_fp(kind, atom):
    """X ↦ {atom 态} ∪ {a 出边进 X 的态} 的不动点：kind='mu' 从 ∅ 放大 / 'nu' 从全集收窄。"""
    S, T, L = set(LTS["states"]), LTS["trans"], LTS["labels"]
    X = set() if kind == "mu" else set(S)
    while True:
        nxt = ({s for s in S if atom in L.get(s, set())} |
               {s for s in S if any((s, "a", t) in T and t in X for t in S)})
        if kind == "nu":
            nxt &= X
        if nxt == X:
            return X
        X = nxt


# ---- E2：CCS 前缀与选择的绑定手推 ----
def next_of(P):
    """CCS 语法树的单步转移：('pref', a, Q) → [(a, Q)]；('sum', P, Q) → 两支转移之并。"""
    if P[0] == "pref":
        return [(P[1], P[2])]
    if P[0] == "sum":
        return next_of(P[1]) + next_of(P[2])
    return []                      # nil：无转移


def bisimilar(p1, p2, seen=None):
    """标准互模拟博弈判定（双向）：每个单步转移都要能被对方同动作、递归地匹配。"""
    if seen is None:
        seen = set()
    if (p1, p2) in seen:
        return True                # 循环假设成立（余归纳）
    seen = seen | {(p1, p2)}
    for src, dst in ((p1, p2), (p2, p1)):
        for a, r_src in next_of(src):
            if not any(a2 == a and bisimilar(r_src, r_dst, seen)
                       for a2, r_dst in next_of(dst)):
                return False
    return True


print("=" * 68)
print("E1 · μ/ν 交替不动点：同一 LTS 上的放大与收窄")
print("=" * 68)
X, t1 = mu_p_or_diamond()
Y, t2 = nu_q_and_box()
print("LTS：s0 -a-> s1 -a-> s2 -b-> s3；s2 ⊨ p、s3 ⊨ q")
print(f"μX.(p ∨ <a>X) 迭代（从 ∅ 放大）：" + " → ".join(str(x) for x in t1))
print(f"  = {{s0,s1,s2}}：s2 是 p 种子，<a> 把 s1、s0 沿 a 倒着灌进——'沿 a 可达 p'")
print(f"νY.(q ∧ [a]Y) 迭代（从全集收窄）：" + " → ".join(str(y) for y in t2))
print(f"  = {{s3}}：s0/s1 无 q 首轮出局；s2 有 p 无 q 出局；s3 无 a 后继（[a]Y 空真）幸存")
assert X == {"s0", "s1", "s2"} and Y == {"s3"}
assert t1[:3] == [["s2"], ["s1", "s2"], ["s0", "s1", "s2"]]
print("→ E1 自检通过：μ 三轮放大 / ν 收窄到不动点，与 13 章 §四手推表逐行一致")

r_mu_q = diamond_fp("mu", "q")
r_nu_p = diamond_fp("nu", "p")
print("\n对照（同形换 μ/ν，味道立变）：")
print(f"  μX.(q ∨ <a>X) = {sorted(r_mu_q)}"
      "——q 的种子只有 s3，而无人经 a 指向 s3，一轮即停：μ 问'从种子灌得到谁'")
print(f"  νY.(p ∨ <a>Y) = {sorted(r_nu_p)}"
      "——s3 无 p 又无 a 出边，ν 首轮削掉：ν 问'谁配得上留在最大自洽集里'")
print("  μ 从小往大灌、ν 从大往小削——同一函数方程的两种问法（13 章 §二）")
assert r_mu_q == {"s3"} and r_nu_p == {"s0", "s1", "s2"}

print("\n" + "=" * 68)
print("E2 · CCS 手推：前缀的括号改变一切")
print("=" * 68)
P = ("pref", "a", ("sum", ("pref", "b", ("nil",)), ("pref", "c", ("nil",))))   # a.(b.0 + c.0)
Q = ("sum", ("pref", "a", ("pref", "b", ("nil",))),                            # a.b.0 + a.c.0
     ("pref", "a", ("pref", "c", ("nil",))))
IDEM = ("sum", ("pref", "a", ("nil",)), ("pref", "a", ("nil",)))              # a.0 + a.0
ONE = ("pref", "a", ("nil",))                                                  # a.0
COMM = ("sum", ("pref", "a", ("nil",)), ("pref", "b", ("nil",)))               # a.0 + b.0
MCOMM = ("sum", ("pref", "b", ("nil",)), ("pref", "a", ("nil",)))              # b.0 + a.0
print("P = a.(b.0 + c.0)：先做 a，再做 b/c 的选择——a 之后处于【同时提供 b、c】的状态")
print("Q = a.b.0 + a.c.0：先选路线（都以 a 开头）——a 之后要么只会 b、要么只会 c")
print(f"  P 与 Q 互模拟：{bisimilar(P, Q)}"
      "  —— Milner 经典反例：攻击者把 P 引到'双选态'后出 b（或 c），")
print("     防守者跟到 Q 的单支态就再也接不住另一动作——前缀的括号改变一切")
print(f"  对照真例：a.0 + a.0 ≡ a.0（选择幂等）：{bisimilar(IDEM, ONE)}"
      f"｜a.0 + b.0 ≡ b.0 + a.0（交换）：{bisimilar(COMM, MCOMM)}")
assert not bisimilar(P, Q)
assert bisimilar(IDEM, ONE) and bisimilar(COMM, MCOMM)
print("→ E2 自检通过：一负两正，互模拟博弈的攻防读法见 13 章 §一")

print("\nlab13 全部自检通过")
