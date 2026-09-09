# -*- coding: utf-8 -*-
"""DPLL SAT 求解器:Herbrand 桥之后的命题世界(04 章 · 代码走廊 A)。

理论现场:
  · 命题逻辑可判定(Post 1921),但"可判定 ≠ 算得动"(Cook–Levin 1971:NP-完全)
  · DPLL(1960/62)= 单位传播 + 纯文字 + 回溯 —— 工业 CDCL 求解器的祖师爷
  · 随机 3-SAT 相变:子句/变元比 α≈4.26 处可满足率断崖(统计物理预言,实验可拍)

跑法: python3 -u experiments/00_dpll_sat.py
依赖: 纯标准库

表示约定: 变元 = 正整数 1..n;文字 = 变元(正极性)或其相反数(负极性);
          赋值表同时记 lit 与 -lit 两个键(赋 True/False),便于 O(1) 查询文字真值。
"""

import random
from itertools import product


# ---------- DPLL 核心 ----------

def lit_value(lit, assignment):
    """文字在当前赋值下的真值;变元未赋值返回 None。"""
    if lit in assignment:
        return assignment[lit]
    if -lit in assignment:
        return not assignment[-lit]
    return None


def simplify(clauses, assignment):
    """按赋值化简子句集。返回 (新子句集);含空子句(冲突)时返回 None。"""
    out = []
    for c in clauses:
        kept, satisfied = [], False
        for l in c:
            v = lit_value(l, assignment)
            if v is True:          # 子句已被满足,整体丢弃
                satisfied = True
                break
            if v is False:         # 假文字,删去
                continue
            kept.append(l)
        if satisfied:
            continue
        if not kept:               # 全体文字为假 → 空子句 → 冲突
            return None
        out.append(tuple(kept))
    return tuple(out)


def dpll(clauses, assignment=None):
    """DPLL:单位传播 → 纯文字消去 → 分裂回溯。返回赋值表(dict)或 None(UNSAT)。"""
    assignment = dict(assignment or {})

    while True:
        clauses = simplify(clauses, assignment)
        if clauses is None:
            return None
        if not clauses:
            return assignment
        # 1) 单位传播:单文字子句强制赋真
        unit = next((c[0] for c in clauses if len(c) == 1), None)
        if unit is not None:
            assignment[unit], assignment[-unit] = True, False
            continue
        # 2) 纯文字:只以一种极性出现的文字,赋真不会吃亏
        lits = {l for c in clauses for l in c}
        pure = next((l for l in lits if -l not in lits), None)
        if pure is not None:
            assignment[pure], assignment[-pure] = True, False
            continue
        break

    # 3) 分裂:挑一个最短子句的首文字,先试真,失败回溯试假
    branch_lit = min(clauses, key=len)[0]
    for trial in (branch_lit, -branch_lit):
        branch = dict(assignment)
        branch[trial], branch[-trial] = True, False
        result = dpll(clauses, branch)
        if result is not None:
            return result
    return None


# ---------- 对拍与验收 ----------

def brute_force(clauses, n_vars):
    """暴力枚举 2^n 个赋值——对拍基准。"""
    for bits in product([True, False], repeat=n_vars):
        model = {i + 1: bits[i] for i in range(n_vars)}
        if all(any(model[l] if l > 0 else not model[-l] for l in c) for c in clauses):
            return model
    return None


def model_satisfies(clauses, dpll_assignment):
    """验收 DPLL 产出的赋值表:每个子句至少一文字为真。"""
    return all(any(lit_value(l, dpll_assignment) is True for l in c) for c in clauses)


def random_3sat(n, alpha, rng):
    """随机 3-SAT:n 个变元、α·n 个子句,每子句 3 个不同变元的随机极性。"""
    return tuple(
        tuple(v * rng.choice((1, -1)) for v in rng.sample(range(1, n + 1), 3))
        for _ in range(int(alpha * n))
    )


def main():
    rng = random.Random(42)

    print("=" * 64)
    print("实验 1 · 正确性:DPLL vs 暴力枚举 对拍(100 个随机实例)")
    print("=" * 64)
    for i in range(100):
        n = rng.randint(3, 8)
        cls = random_3sat(n, rng.uniform(2.0, 6.0), rng)
        m_dpll, m_brute = dpll(cls), brute_force(cls, n)
        assert (m_dpll is None) == (m_brute is None), f"实例{i}:SAT/UNSAT 判定不一致"
        if m_dpll is not None:
            assert model_satisfies(cls, m_dpll), f"实例{i}:DPLL 模型验收失败"
    print("  100/100 对拍一致 ✓(assert 全过:判定一致 + 模型可验收)")

    print()
    print("=" * 64)
    print("实验 2 · 3-SAT 相变:扫描 α=子句/变元比,统计可满足率(n=40,每档 60 例)")
    print("=" * 64)
    print(f"{'α':>6} {'可满足率':>8}")
    rates = {}
    for alpha in (3.0, 3.5, 4.0, 4.26, 4.5, 5.0, 6.0):
        sat = sum(1 for _ in range(60) if dpll(random_3sat(40, alpha, rng)) is not None)
        rates[alpha] = sat / 60
        tag = " ← 相变点附近" if abs(alpha - 4.26) < 0.3 else ""
        print(f"{alpha:>6.2f} {rates[alpha]:>8.2f}{tag}")

    print()
    print("读数:")
    print("  · α 小(约束稀疏):几乎全可满足;α 大(约束稠密):几乎全不可满足")
    print("  · 断崖在 α ≈ 4.26(随机 3-SAT 相变点)——\"存在模型\"这个事实本身在相变,")
    print("    与 02 章紧致性遥相呼应:有限世界与无限世界各自的\"有模型\"戏剧")
    print("  · 相变区恰是计算最难区;工业实例多为结构化实例(在相变区外),")
    print("    这是 CDCL 求解器能横行产业的原因(04 章性能工程注)")

    assert rates[3.0] > rates[6.0], "相变方向异常:稀疏区应更可满足"
    print("\n断言校验:稀疏区可满足率 > 稠密区 ✓")


if __name__ == "__main__":
    main()
