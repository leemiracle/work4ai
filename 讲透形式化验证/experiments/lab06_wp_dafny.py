#!/usr/bin/env python3
"""lab06 · 最弱前置条件：三条规则手推 + z3 验证义务（06 章 §二）。
程序（无前置条件）:
    if (x > y) { r = x } else { r = y }
    后置 Q: r>=x ∧ r>=y        → WP 可证（z3: unsat 取反 → valid）
    后置 Q': r>x               → 不可证（z3 给反模型；x≥y 的取值皆可踩爆）
手推锚点（章内§二）:
    WP(then 分支, Q) = (x≥x ∧ x≥y) ⟸ 卫 x>y  ⇒ 化简为 x≥y ✓
    WP(else 分支, Q) = (y≥x ∧ y≥y) ⟸ 卫 ¬(x>y) 即 y≥x ✓
Dafny 对照: experiments/max.dfy 的 method Max 同款程序，Dafny 内部
就是算 WP → 义务喂 Z3；本 lab 把这条流水线裸露出来手推一遍。
"""
from z3 import Ints, Implies, And, Solver, Not, unsat


def wp_max(post_kind):
    x, y = Ints("x y")
    g_then = x > y          # 卫条件
    # then: r:=x → Q[x/r]（赋值规则：后置里的 r 逐个替换成 x）
    if post_kind == "max":
        # Q: r>=x ∧ r>=y 代入 r=x → (x>=x ∧ x>=y)；代入 r=y → (y>=x ∧ y>=y)
        q_then = And(x >= x, x >= y)
        q_else = And(y >= x, y >= y)
    else:                    # post_kind == "strict"（Q': r>x，错误的强后置）
        q_then = x > x       # x>x 恒假——then 分支必违反
        q_else = y > x       # 取 x=y 即被踩爆——else 分支也守不住
    # WP(if) = (g→WP_then) ∧ (¬g→WP_else)（if 规则：两个卫蕴含拼合）
    return And(Implies(g_then, q_then), Implies(Not(g_then), q_else))


def check_valid(wp_expr):
    """验证义务: WP 为永真式？⟺ 取反后不可满足（z3: unsat → valid）。"""
    s = Solver(); s.add(Not(wp_expr))
    r = s.check()
    # unsat ⇒ 取反无模型 ⇒ WP 永真 ⇒ 该后置自动可证；
    # 否则 sat，模型即"WP 不成立"的具体 x,y——设计错误的第一现场
    return (r == unsat), (None if r == unsat else s.model())


def selftest():
    ok, _ = check_valid(wp_max("max"))
    assert ok, "max 后置应可证"
    ok2, model = check_valid(wp_max("strict"))
    assert not ok2 and model is not None
    print("Q: r>=x ∧ r>=y  → VALID（WP 手推两条分支化简见 docstring）")
    print(f"Q': r>x         → 不可证, 反模型: {model}（x≥y 即踩爆：x>y 时 r=x、x=y 时 r=y，都不严格大）")
    print("lab06 自检通过")


if __name__ == "__main__":
    selftest()
