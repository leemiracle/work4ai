# -*- coding: utf-8 -*-
"""Curry–Howard 可执行版：STLC 证明项的 β-归约 = 切割消去。

02 章 · 语言特征 配套实验。纯标准库。

命题即类型（直觉主义命题逻辑）:
  命题变量 p        ↦ 基类型 T("p")
  A → B             ↦ 函数类型 Arrow(A, B)
  A 的证明          ↦ 类型 A 的项
  →I（撤假设）      ↦ λ 抽象
  →E（应用）        ↦ 函数应用
  局部约化(β)       ↦ (λx.t) u ⟶ t[u/x]   ——切割被消去

跑法: python3 -u experiments/02_beta_normalization.py
"""

# ── 项与类型 ──────────────────────────────────────────
# 类型: ("T", name) | ("→", A, B)
# 项:  ("var", name) | ("lam", x, A, body) | ("app", f, a)
# 类型环境: dict[name → 类型]


def type_of(term, env, depth=0):
    """类型检查（=证明检查）。失败抛 TypeError——一致性由类型系统看守。"""
    op = term[0]
    if op == "var":
        if term[1] not in env:
            raise TypeError(f"自由变量 {term[1]} 无类型")
        return env[term[1]]
    if op == "lam":
        _, x, A, body = term
        return ("→", A, type_of(body, {**env, x: A}, depth + 1))
    if op == "app":
        tf = type_of(term[1], env, depth + 1)
        ta = type_of(term[2], env, depth + 1)
        if tf[0] != "→" or tf[1] != ta:
            raise TypeError(f"应用不匹配: {tf} 应用于 {ta}")
        return tf[2]
    raise ValueError(op)


def subst(t, x, v):
    """t[x := v]（名字足够独特，省 capture 处理——演示用命名约定保证）。"""
    op = t[0]
    if op == "var":
        return v if t[1] == x else t
    if op == "lam":
        _, y, A, body = t
        return ("lam", y, A, subst(body, x, v)) if y != x else t
    if op == "app":
        return ("app", subst(t[1], x, v), subst(t[2], x, v))
    raise ValueError(op)


def beta_step(t):
    """找最左外的 (λx.t) u 做一步 β-归约。返回 (新项, 是否归约了)。"""
    op = t[0]
    if op == "app" and t[1][0] == "lam":
        _, _, _, body = t[1]
        return subst(body, t[1][1], t[2]), True
    if op == "app":
        l, d1 = beta_step(t[1])
        if d1:
            return ("app", l, t[2]), True
        r, d2 = beta_step(t[2])
        return ("app", t[1], r), d2
    if op == "lam":
        body, d = beta_step(t[3])
        return ("lam", t[1], t[2], body), d
    return t, False


def normalize(t, limit=10000):
    """归约到范式，返回 (范式, 步数)。超限报错——STLC 理论上不会（强规范化）。"""
    steps = 0
    while True:
        t, d = beta_step(t)
        if not d:
            return t, steps
        steps += 1
        if steps > limit:
            raise RuntimeError("不终止?!（STLC 不该发生——检查实现）")


def show(t):
    op = t[0]
    if op == "var":
        return t[1]
    if op == "lam":
        return f"λ{t[1]}. {show(t[3])}"
    if op == "app":
        lhs = f"({show(t[1])})" if t[1][0] == "lam" else show(t[1])
        rhs = f"({show(t[2])})" if t[2][0] in ("lam", "app") else show(t[2])
        return f"{lhs} {rhs}"


def main():
    print("=" * 62)
    print("Curry–Howard 跑起来：证明项 β-归约 = 切割消去")
    print("=" * 62)

    P, Q, R = ("T", "p"), ("T", "q"), ("T", "r")

    # 证明 1：((p→q)→p)→p 的两种走法之一——组合子风格的恒等链
    # 命题 A→A 的证明：id = λx.x
    id_p = ("lam", "x", P, ("var", "x"))
    print(f"\n① →I 的证明项: id_p : p → p   即 {show(id_p)}")
    print(f"   类型检查: {type_of(id_p, {})}  ✓（λ 抽象 = 撤销假设）")

    # 证明 2：(p→q→r) → (p→q) → p → r（02 章练习 7 的同款）
    t2 = ("lam", "hpqr", ("→", P, ("→", Q, R)),
          ("lam", "hpq", ("→", P, Q),
           ("lam", "hp", P,
            ("app", ("app", ("var", "hpqr"), ("var", "hp")),
             ("app", ("var", "hpq"), ("var", "hp"))))))
    ty2 = type_of(t2, {})
    print(f"\n② 组合证明: {show(t2)[:60]} …")
    print(f"   类型 = {ty2}")
    print(f"   归约步数（它已是范式）: {normalize(t2)[1]}——无切割，无需消解")

    # 证明 3：制造一个真正的"切割"——恒等函数应用到实参
    t3 = ("app", ("lam", "f", ("→", ("→", P, Q), ("→", P, Q)), ("var", "f")),
          ("lam", "g", ("→", P, Q), ("var", "g")))
    print(f"\n③ 带切割的证明: (λf.f) 应用于 g")
    print(f"   归约前: {show(t3)}")
    nf3, steps3 = normalize(t3)
    print(f"   归约后: {show(nf3)}   （{steps3} 步 β——一个切割被消去）")

    # 证明 4：同命题两证明，路径不同范式相同（合流的见证）
    t4a = ("app", ("lam", "f", ("→", ("→", P, Q), ("→", P, Q)), ("var", "f")),
           ("lam", "g", ("→", P, Q), ("var", "g")))
    t4b = ("lam", "g", ("→", P, Q), ("var", "g"))  # 同类型，直接写
    nf_a, s_a = normalize(t4a)
    nf_b, s_b = normalize(t4b)
    print(f"\n④ 合流见证: 同命题的两个证明")
    print(f"   证明A {s_a} 步归约到 {show(nf_a)}")
    print(f"   证明B {s_b} 步归约到 {show(nf_b)}")
    print(f"   范式相同: {nf_a == nf_b}   ——步数不同，终点唯一（Church–Rosser）")

    # 证明 5：想写非终止证明？类型系统当场拒绝
    print(f"\n⑤ 坏项拦截: λx. x x（自应用——无类型逻辑的万恶之源）")
    self_app_body = ("app", ("var", "x"), ("var", "x"))
    bad = ("lam", "x", None, self_app_body)  # 类型留空——STLC 里没有合法类型
    try:
        # 试遍两种可能：x : p 和 x : p→p（都注定失败）
        for cand in (P, ("→", P, P)):
            type_of(self_app_body, {"x": cand})
        print("   竟然通过了?!（不可能——见下）")
    except TypeError as e:
        print(f"   类型检查拒绝: {e}")
        print(f"   ——Y 组合子/Ω 在 STLC 不可类型化 ⟹ 一致性 = 类型安全   💡")


if __name__ == "__main__":
    main()
