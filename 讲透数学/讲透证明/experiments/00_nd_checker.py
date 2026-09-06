# -*- coding: utf-8 -*-
"""自然演绎证明检查器——"证明是可检查的树"的第一性原理。

00 章 · 体系结构 配套实验。纯标准库。

公式: ("p", x) | ("→", A, B) | ("∧", A, B) | ("∨", A, B) | ("⊥",)
证明树（节点 = 规则应用）:
  ("hyp", id, A)                  假设 id : A（叶子）
  ("→I", id, sub)                 撤销 id 的假设，得 A→B（sub 得 B）
  ("→E", f, a)                    f : A→B 与 a : A 得 B
  ("∧I", a, b) / ("∧E1", a) / ("∧E2", a)
  ("∨I1", a) / ("∨I2", a)         A 得 A∨B / B 得 A∨B
  ("∨E", d, x, c1, y, c2)         d : A∨B；c1 在 x:A 下得 C；c2 在 y:B 下得 C ⟹ C
  ("⊥E", sub, C)                  ⊥ 得任意 C
  ("RAA", id, sub, A)             sub 在 id:¬A 下得 ⊥ ⟹ A（经典）

check(node) → (结论, 开放假设集)。任何规则错用当场抛 NDError。

跑法: python3 -u experiments/00_nd_checker.py
"""


class NDError(Exception):
    pass


def check(n):
    """返回 (结论公式, 开放假设 frozenset{（id,公式）}）。"""
    op = n[0]
    if op == "hyp":
        _, i, A = n
        return A, frozenset({(i, A)})
    if op == "→I":
        _, i, sub = n
        concl, hyps = check(sub)
        target = [h for h in hyps if h[0] == i]
        if not target:
            raise NDError(f"→I 想撤销假设 [{i}]，但子证明中不存在其未撤销副本")
        A = target[0][1]
        rest = frozenset(h for h in hyps if h[0] != i)
        return ("→", A, concl), rest
    if op == "→E":
        _, f, a = n
        cf, hf = check(f)
        ca, ha = check(a)
        if cf[0] != "→" or cf[1] != ca:
            raise NDError(f"→E 前提不匹配: {fml(cf)} 应用于 {fml(ca)}")
        return cf[2], hf | ha
    if op == "∧I":
        ca, ha = check(n[1])
        cb, hb = check(n[2])
        return ("∧", ca, cb), ha | hb
    if op == "∧E1":
        c, h = check(n[1])
        if c[0] != "∧":
            raise NDError(f"∧E1 需要合取式，得到 {fml(c)}")
        return c[1], h
    if op == "∧E2":
        c, h = check(n[1])
        if c[0] != "∧":
            raise NDError(f"∧E2 需要合取式，得到 {fml(c)}")
        return c[2], h
    if op == "∨I1":
        c, h = check(n[1])
        return ("∨", c, n[2]), h
    if op == "∨I2":
        c, h = check(n[1])
        return ("∨", n[2], c), h
    if op == "∨E":
        _, d, x, c1, y, c2 = n
        cd, hd = check(d)
        if cd[0] != "∨":
            raise NDError(f"∨E 需要析取式，得到 {fml(cd)}")
        A, B = cd[1], cd[2]
        r1, h1 = check(c1)
        r2, h2 = check(c2)
        if (x, A) not in h1:
            raise NDError(f"∨E 左支未开放假设 [{x}:{fml(A)}]")
        if (y, B) not in h2:
            raise NDError(f"∨E 右支未开放假设 [{y}:{fml(B)}]")
        if r1 != r2:
            raise NDError(f"∨E 两支结论不同: {fml(r1)} vs {fml(r2)}")
        rest = (h1 - {(x, A)}) | (h2 - {(y, B)}) | hd
        return r1, rest
    if op == "⊥E":
        c, h = check(n[1])
        if c != ("⊥",):
            raise NDError(f"⊥E 需要 ⊥，得到 {fml(c)}")
        return n[2], h
    if op == "RAA":
        _, i, sub, A = n
        concl, hyps = check(sub)
        want = (i, ("→", A, ("⊥",)))       # ¬A = A→⊥
        if concl != ("⊥",):
            raise NDError(f"RAA 子证明需得 ⊥，得到 {fml(concl)}")
        if want not in hyps:
            raise NDError(f"RAA 未开放假设 [{i}:{fml(want[1])}]")
        return A, frozenset(h for h in hyps if h != want)
    raise NDError(f"未知规则 {op}")


def fml(A):
    if A[0] == "p":
        return A[1]
    if A == ("⊥",):
        return "⊥"
    if A[0] == "→":
        return f"({fml(A[1])} → {fml(A[2])})"
    if A[0] == "∧":
        return f"({fml(A[1])} ∧ {fml(A[2])})"
    if A[0] == "∨":
        return f"({fml(A[1])} ∨ {fml(A[2])})"
    return "?"


def verify(name, proof, expect=None):
    try:
        concl, hyps = check(proof)
        if hyps:
            raise NDError(f"仍有开放假设: {sorted(hyps)}")
        if expect is not None and concl != expect:
            raise NDError(f"结论是 {fml(concl)}，期望 {fml(expect)}")
        print(f"  ✓ {name}: ⊢ {fml(concl)}")
        return True
    except NDError as e:
        print(f"  ✗ {name}: 拒绝 —— {e}")
        return False


def main():
    p, q, r = ("p", "p"), ("p", "q"), ("p", "r")
    IMP = lambda a, b: ("→", a, b)
    NOT = lambda a: IMP(a, ("⊥",))

    print("=" * 62)
    print("① 合法证明三连")
    print("=" * 62)
    # 恒等：p → p（→I 撤假设）
    id_proof = ("→I", "h", ("hyp", "h", p))
    verify("恒等 p→p", id_proof, IMP(p, p))

    # 组合：(p→q)→((q→r)→(p→r))
    comp = ("→I", "hpq",
            ("→I", "hqr",
             ("→I", "hp",
              ("→E", ("hyp", "hqr", IMP(q, r)),
               ("→E", ("hyp", "hpq", IMP(p, q)), ("hyp", "hp", p))))))
    verify("组合 (p→q)→((q→r)→(p→r))", comp)

    # 经典：¬¬p → p（RAA 的力量）
    nnp = ("→I", "hnn",                        # hnn : ¬¬p
           ("RAA", "hn",                        # 撤 hn : ¬p
            ("⊥E",                              # 需要一个 ⊥ —— 由 hnn 应用到 ¬p 得到
             ("→E", ("hyp", "hnn", NOT(NOT(p))), ("hyp", "hn", NOT(p))),
             ("⊥",)),
            p))
    verify("经典否定消除 ¬¬p→p", nnp, IMP(NOT(NOT(p)), p))

    print()
    print("=" * 62)
    print("② 坏证明两连（检查器当场拦截）")
    print("=" * 62)
    # 坏 1：→E 前提交换（把 p 应用到 (p→q) 上）
    bad1 = ("→I", "hpq", ("→I", "hp",
            ("→E", ("hyp", "hp", p), ("hyp", "hpq", IMP(p, q)))))
    verify("坏证明：→E 参数交换", bad1)   # 应被拒
    # 坏 2：∨E 左支假设被 →I 提前撤销（双重撤销事故）
    d = ("hyp", "d", ("∨", p, q))
    c1 = ("→I", "x", ("hyp", "x", p))
    c2 = ("→I", "y", ("hyp", "y", q))
    bad2 = ("∨E", d, "x", c1, "y", c2)
    verify("坏证明：∨E 假设被提前撤销", bad2)   # 应被拒

    print()
    print("=" * 62)
    print("③ 断言汇总")
    print("=" * 62)
    ok = (verify("", id_proof, IMP(p, p)) and verify("", comp) and verify("", nnp))
    bad = (not verify("", bad1)) and (not verify("", bad2))
    print(f"  合法三连全过: {ok}   坏证明全拦: {bad}")
    print("  ——证明=可检查的树：证明助手产业的第一性原理 💡")


if __name__ == "__main__":
    main()
