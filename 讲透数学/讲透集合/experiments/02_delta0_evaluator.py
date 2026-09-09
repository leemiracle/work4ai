# -*- coding: utf-8 -*-
"""Δ₀ 公式求值器——量词预算与绝对性的可执行演示。

02 章 · 语言特征 配套实验。纯标准库。

公式 AST:
  ("in", x, y)            x ∈ y          （原子）
  ("eq", x, y)            x = y          （原子）
  ("not", φ) / ("and", φ, ψ) / ("or", φ, ψ)
  ("bexists", v, rng, φ)  ∃v∈rng φ       （受限——Δ₀ 允许）
  ("bforall", v, rng, φ)  ∀v∈rng φ       （受限——Δ₀ 允许）
  ("exists", v, φ)        ∃v φ           （无界——Σ₁，破坏 Δ₀）
  ("forall", v, φ)        ∀v φ           （无界——Π₁，破坏 Δ₀）

变量用字符串名，环境 dict 提供；rng 也是变量名（指向一个集合参数）。
宇宙 U 是一个 frozenset：无界量词的范围 = U（"当前宇宙"）。

跑法: python3 -u experiments/02_delta0_evaluator.py
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


def is_delta0(f):
    """量词预算 lint：一切量词受限 ⟹ Δ₀。"""
    op = f[0]
    if op in ("in", "eq"):
        return True
    if op in ("not",):
        return is_delta0(f[1])
    if op in ("and", "or"):
        return is_delta0(f[1]) and is_delta0(f[2])
    if op in ("bexists", "bforall"):
        return is_delta0(f[3])
    if op in ("exists", "forall"):
        return False
    raise ValueError(op)


def evalf(f, env, U):
    """在'宇宙' U（frozenset，全体对象）里求值公式 f。"""
    op = f[0]
    if op == "in":
        return env[f[1]] in env[f[2]]
    if op == "eq":
        return env[f[1]] == env[f[2]]
    if op == "not":
        return not evalf(f[1], env, U)
    if op == "and":
        return evalf(f[1], env, U) and evalf(f[2], env, U)
    if op == "or":
        return evalf(f[1], env, U) or evalf(f[2], env, U)
    if op == "bexists":
        _, v, rng, body = f
        return any(evalf(body, {**env, v: t}, U) for t in env[rng])
    if op == "bforall":
        _, v, rng, body = f
        return all(evalf(body, {**env, v: t}, U) for t in env[rng])
    if op == "exists":
        _, v, body = f
        return any(evalf(body, {**env, v: t}, U) for t in U)
    if op == "forall":
        _, v, body = f
        return all(evalf(body, {**env, v: t}, U) for t in U)
    raise ValueError(op)


# ── 公式库 ─────────────────────────────────────────────
# "x 传递"：∀y∈x ∀z∈y (z ∈ x)
TRANSITIVE = ("bforall", "y", "x",
              ("bforall", "z", "y", ("in", "z", "x")))
# "x 的 ∈ 线性"：∀y∈x ∀z∈x (y∈z ∨ y=z ∨ z∈y)
LINEAR = ("bforall", "y", "x",
          ("bforall", "z", "x",
           ("or", ("in", "y", "z"),
            ("or", ("eq", "y", "z"), ("in", "z", "y")))))
ORDINAL = ("and", TRANSITIVE, LINEAR)
# 无界 Σ₁："∃y (x ∈ y)"——不属于任何东西的只能是宇宙顶
UNB_EXISTS_SUP = ("exists", "y", ("in", "x", "y"))


def main():
    vs = build_v(5)          # V₅ = 65536 个元素，依然可构造
    V4, V5 = vs[4], vs[5]

    print("=" * 62)
    print("① Δ₀ 求值：在 V₄ 里数序数")
    print("=" * 62)
    print(f"「x 是序数」是 Δ₀？ {is_delta0(ORDINAL)}")
    ordinals = [x for x in V4 if evalf(ORDINAL, {"x": x}, V4)]
    print(f"V₄ 里的序数: {len(ordinals)} 个（0,1,2,3——V₄=V₃∪P(V₃) 装得下序数 3={{0,1,2}}）")
    print(f"  对照：V₄ 有 {len(V4)} 个元素，只有 {len(ordinals)} 个是序数——Δ₀ 精准挑出了它们")
    non_trans_linear = [x for x in V4 if evalf(TRANSITIVE, {"x": x}, V4) and not evalf(LINEAR, {"x": x}, V4)]
    print(f"  传递但不线性的'差一点序数': {len(non_trans_linear)} 个（如 {{{{∅}}}}={{1}}——∈ 只偏序不线序）")
    print()

    print("=" * 62)
    print("② 绝对性对照：同一个参数，两个宇宙")
    print("=" * 62)
    # 参数 V₃ 同时 ∈ V₄ 和 ∈ V₅——两宇宙都认识的"公共对象"
    param = vs[3]
    print(f"参数 x = V₃（|V₃|=4），x∈V₄? {param in V4}，x∈V₅? {param in V5}")
    print()
    print("Δ₀ 公式「x 是序数」:")
    t4 = evalf(ORDINAL, {"x": param}, V4)
    t5 = evalf(ORDINAL, {"x": param}, V5)
    print(f"  V₄ 中真值 = {t4}   V₅ 中真值 = {t5}   ⟹ 绝对 ✓（真值与宇宙无关）")
    print()
    print("Δ₀ 公式「x 传递」:")
    t4 = evalf(TRANSITIVE, {"x": param}, V4)
    t5 = evalf(TRANSITIVE, {"x": param}, V5)
    print(f"  V₄ 中真值 = {t4}   V₅ 中真值 = {t5}   ⟹ 绝对 ✓")
    print()
    print(f"无界 Σ₁ 公式「∃y (x∈y)」是 Δ₀？ {is_delta0(UNB_EXISTS_SUP)}")
    u4 = evalf(UNB_EXISTS_SUP, {"x": param}, V4)
    u5 = evalf(UNB_EXISTS_SUP, {"x": param}, V5)
    verdict = "翻转 ✗" if u4 != u5 else "未翻转（巧合）"
    print(f"  V₄ 中真值 = {u4}   V₅ 中真值 = {u5}   ⟹ {verdict}")
    print(f"  原因：含 V₃ 的集合最小是 {{V₃}}⊆V₄ ⟹ ∈V₅；V₄ 里没有 y∋V₃")
    print(f"  ——无界量词在问'整个宇宙'，宇宙换了答案就换   💡")
    print()

    print("=" * 62)
    print("③ 量词预算 lint：静态判定 Δ₀")
    print("=" * 62)
    tests = [
        ("x 是序数", ORDINAL),
        ("x 传递", TRANSITIVE),
        ("∃y x∈y（无界）", UNB_EXISTS_SUP),
        ("「x 空」（受限 ¬∃y∈x）：", ("not", ("bexists", "y", "x", ("eq", "y", "y")))),
        ("「∀y x∈y」（无界）", ("forall", "y", ("in", "x", "y"))),
    ]
    for name, f in tests:
        print(f"  {name:<26} Δ₀? {is_delta0(f)}")


if __name__ == "__main__":
    main()
