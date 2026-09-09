# -*- coding: utf-8 -*-
"""消解反驳检查器 + 迷你 DPLL——SAT 求解器 = 命题证明搜索器。

04 章 · 证明转代码 配套实验。纯标准库。

子句 = frozenset of 文字；文字 = (var: str, pol: bool)
消解规则: 从 C∪{x} 与 D∪{¬x} 得 C∪D（对 x 消解）

跑法: python3 -u experiments/04_resolution_cdl.py
"""
from itertools import combinations


def lit(s, pol=True):
    return (s, pol)


def show_clause(C):
    if not C:
        return "□"
    parts = [(x if p else f"¬{x}") for x, p in sorted(C)]
    return "(" + " ∨ ".join(parts) + ")"


def resolve(C, D, var):
    """在 var 上消解。成功返回新子句，失败返回 None。"""
    pos_C = (var, True) in C
    neg_C = (var, False) in C
    pos_D = (var, True) in D
    neg_D = (var, False) in D
    if not ((pos_C and neg_D) or (neg_C and pos_D)):
        return None
    new = (C - {(var, True), (var, False)}) | (D - {(var, True), (var, False)})
    return new


def php_clauses(pigeons, holes):
    """鸽笼公式 PHP(m,n)：m 鸽 n 笼，每鸽有笼 + 每笼至多一鸽。m>n 时 UNSAT。
    变量 p_{i,j} = 鸽 i 在笼 j。"""
    clauses = []
    for i in range(pigeons):
        clauses.append(frozenset({(f"p{i}_{j}", True) for j in range(holes)}))
    for j in range(holes):
        for i1, i2 in combinations(range(pigeons), 2):
            clauses.append(frozenset({(f"p{i1}_{j}", False), (f"p{i2}_{j}", False)}))
    return clauses


def partA_resolution_check():
    print("=" * 62)
    print("① 消解反驳检查器：PHP(2,1) 逐条验链")
    print("=" * 62)
    # PHP(2,1): (p0_0) (p1_0) (¬p0_0 ∨ ¬p1_0)
    c1 = frozenset({lit("p0_0")})
    c2 = frozenset({lit("p1_0")})
    c3 = frozenset({lit("p0_0", False), lit("p1_0", False)})
    print(f"初始子句: {show_clause(c1)}  {show_clause(c2)}  {show_clause(c3)}")
    r1 = resolve(c1, c3, "p0_0")
    assert r1 is not None
    print(f"消解步 1: {show_clause(c1)} 与 {show_clause(c3)} 在 p0_0 上 ⟹ {show_clause(r1)}")
    r2 = resolve(r1, c2, "p1_0")
    assert r2 is not None
    print(f"消解步 2: {show_clause(r1)} 与 {show_clause(c2)} 在 p1_0 上 ⟹ {show_clause(r2)}")
    print(f"空子句落地: {r2 == frozenset()}   ——UNSAT 的消解证明完成 ✓")
    print("（证明系统的'证明'也是数据：这条链就是可独立检查的证明证书）")
    print()


def unit_prop(cs, assign, stats):
    """单元传播。返回 (新子句集, 赋值)；冲突时返回 (None, assign)。"""
    while True:
        if any(len(c) == 0 for c in cs):
            stats["conflict"] += 1
            return None, assign
        unit = next((c for c in cs if len(c) == 1), None)
        if unit is None:
            return cs, assign
        x, p = next(iter(unit))
        if x in assign:
            if assign[x] != p:
                stats["conflict"] += 1
                return None, assign          # 同变量反向单元——冲突
            cs = [c for c in cs if c != unit]  # 已满足的单元子句，剔掉
            continue
        stats["prop"] += 1
        assign = {**assign, x: p}
        cs = [c2 - {(x, not p)} for c2 in cs if (x, p) not in c2]


def dpll_solve(clauses, stats):
    """带外层传播包装的求解入口（含变量赋值合并）。"""
    assign0 = {}
    def go(cs, assign):
        cs, assign = unit_prop(cs, assign, stats)
        if cs is None or any(len(c) == 0 for c in cs):
            return None
        vs = {x for c in cs for x, _ in c}
        if not vs:
            return assign
        v = sorted(vs)[0]
        for pol in (True, False):
            stats["decide"] += 1
            cs2 = [c - {(v, not pol)} for c in cs if (v, pol) not in c]
            r = go(cs2, dict(assign))
            if r is not None:
                r[v] = pol
                return r
        return None
    return go([frozenset(c) for c in clauses], assign0)


def partB_dpll():
    print("=" * 62)
    print("② 迷你 DPLL：可满足求解与 UNSAT 判定")
    print("=" * 62)
    sat_instance = [
        frozenset({lit("a"), lit("b")}),
        frozenset({lit("a", False), lit("c")}),
        frozenset({lit("b", False), lit("c", False), lit("d")}),
        frozenset({lit("d", False)}),
    ]
    print("实例 1（可满足）:")
    for c in sat_instance:
        print(f"   {show_clause(c)}")
    stats = {"decide": 0, "prop": 0, "conflict": 0}
    model = dpll_solve(sat_instance, stats)
    print(f"   模型: {model}   [决策 {stats['decide']} / 传播 {stats['prop']} / 冲突 {stats['conflict']}]")
    check = all(any(model.get(x, None) == p for x, p in c) for c in sat_instance)
    print(f"   模型验证: {check}")
    print()
    print("实例 2: PHP(3,2)（3 鸽 2 笼——直觉 UNSAT）:")
    php = php_clauses(3, 2)
    print(f"   {len(php)} 条子句，变量 {len({x for c in php for x, _ in c})} 个")
    stats2 = {"decide": 0, "prop": 0, "conflict": 0}
    model2 = dpll_solve(php, stats2)
    print(f"   DPLL 判定: {'UNSAT' if model2 is None else f'SAT?! {model2}'}"
          f"   [决策 {stats2['decide']} / 传播 {stats2['prop']} / 冲突 {stats2['conflict']}]")
    print()
    print("实例 3: PHP(4,3) 的成本曲线（同款但更大一号）:")
    php3 = php_clauses(4, 3)
    stats3 = {"decide": 0, "prop": 0, "conflict": 0}
    model3 = dpll_solve(php3, stats3)
    print(f"   变量 {len({x for c in php3 for x, _ in c})} 个 → 决策 {stats3['decide']} / 冲突 {stats3['conflict']}")
    print("   ——每加一只鸽子，搜索成本跳一档：Haken 下界的实证影子（消解证明指数长）💡")


if __name__ == "__main__":
    partA_resolution_check()
    partB_dpll()
