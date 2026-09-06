#!/usr/bin/env python3
"""lab03 · SMT 求解：手写 mini-CDCL 与 Z3/cvc5 对拍（03 章 §二/§三/§四）。
E1 UNSAT 公式 F=(x1∨x2)∧(¬x1∨x2)∧(¬x2∨x3)∧(¬x2∨¬x3)。
   手推锚点（03 章 §二）：决策 x1=T → 传播 x2=T（由 ¬x1∨x2）→ 传播 x3=T（由 ¬x2∨x3），
   与 (¬x2∨¬x3) 要求的 x3=F 相撞 → 学习单位子句 (¬x1) → 0 级断言后再传播出冲突 → UNSAT，
   学习子句恰为 [[-1]]。
   回跳语义（教学简化）：冲突时弹出一个决策 d、学习 [¬d]、assign 彻底清空（重启式回跳，
   回到 0 级），再对 clauses+learned 从头单位传播——学习子句此时起 0 级断言作用；
   0 级再冲突（决策栈为空）即 UNSAT。与真实 1UIP 的差异见 03 章 §二。
E2 SAT 公式 G=(x1∨x2)∧(¬x1∨x3)：决策+传播给出模型，逐子句代入验证——模型即 NP 证书。
E3 对拍：同一 F 喂 z3 与 cvc5 均应 unsat；LRA×EUF 组合（接口变量 u:=f(a) 的
   Nelson-Oppen 分工）应 sat——这是 SMT 在 SAT 之上多出来的"理论血肉"。
风格沿用系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from z3 import Bool, Solver, Not, Or, Real, Function, RealSort


def fmt_clause(c):
    """[1, -2] → (x1 ∨ ¬x2)：给人看的子句渲染。"""
    return "(" + "∨".join(f"x{l}" if l > 0 else f"¬x{-l}" for l in c) + ")"


def unit_propagate(assign, clauses, log=None):
    """单位传播到不动点（教科书语义：只对'未满足且恰剩一个未赋值文字'的子句点火）。
    assign: dict[var]->bool（原地修改）；返回 (assign, conflict_clause|None)；
    log 非 None 时逐条记录 (var, value, 子句)，供手推轨迹对照。"""
    changed = True
    while changed:
        changed = False
        for c in clauses:
            satisfied = False
            unassigned = []
            for lit in c:
                v = assign.get(abs(lit))
                if v is None:
                    unassigned.append(lit)
                elif v == (lit > 0):        # 该文字已为真 → 子句满足
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unassigned:              # 所有文字已赋值且为假 → 冲突
                return assign, c
            if len(unassigned) == 1:        # 恰剩一个文字 → 单位子句，强制其为真
                lit = unassigned[0]
                assign[abs(lit)] = lit > 0
                if log is not None:
                    log.append((abs(lit), lit > 0, c))
                changed = True
    return assign, None


def cdcl_solve(clauses, n_vars, trace=None):
    """mini-CDCL：单位传播 + 顺序决策 + 冲突学习（决策取反）+ 重启式回跳。
    clauses: list[list[int]]（正数 = xi，负数 = ¬xi）；
    返回 ("SAT", model:dict) 或 ("UNSAT", learned:list[list[int]])。
    冲突处理：决策栈空 → UNSAT；否则弹出最近决策 d，学习单位子句 [¬d]，assign 彻底
    清空回到 0 级（栈上更早的决策赋值已随之失效，一并弃掉），从 clauses+learned
    从头传播——[¬d] 以 0 级断言身份进场，此后永远钉住 xd=F。"""
    learned = []
    assign = {}
    trail = []                              # 决策栈（只记决策，不记传播）
    while True:
        log = [] if trace is not None else None
        assign, conflict = unit_propagate(assign, clauses + learned, log)
        if trace is not None and log:
            trace.append(("prop", list(log)))
        if conflict is not None:
            if trace is not None:
                trace.append(("conflict", conflict))
            if not trail:                   # 0 级冲突：无决策可撤 → UNSAT
                return "UNSAT", learned
            d = trail.pop()
            # 决策恒赋 True，此处直写取反
            clause = [-d]                       # 学习 (¬d)：决策取反（1UIP 的简化）
            learned.append(clause)
            if trace is not None:
                trace.append(("learn", clause))
            assign = {}                     # 重启式回跳：整体清空回 0 级
            trail = []
            continue                        # 从 clauses+learned 从头传播
        free = [v for v in range(1, n_vars + 1) if v not in assign]
        if not free:                        # 全部变量已赋值且无冲突 → SAT
            return "SAT", dict(assign)
        v = free[0]                         # 顺序决策：最小编号自由变量，先试 True
        trail.append(v)
        assign[v] = True
        if trace is not None:
            trace.append(("decide", v))


print("=" * 68)
print("E1 · mini-CDCL 手推：F → UNSAT")
print("=" * 68)
F = [[1, 2], [-1, 2], [-2, 3], [-2, -3]]
print("公式：F = (x1∨x2) ∧ (¬x1∨x2) ∧ (¬x2∨x3) ∧ (¬x2∨¬x3)")
trace = []
res, learned = cdcl_solve(F, 3, trace=trace)
print("决策/传播轨迹（与 03 章 §二手推逐步对照）：")
for ev in trace:
    if ev[0] == "decide":
        print(f"  决策  x{ev[1]} = T")
    elif ev[0] == "prop":
        for var, val, c in ev[1]:
            print(f"  传播  x{var} = {'T' if val else 'F'}（由子句 {fmt_clause(c)}：其余文字已全假）")
    elif ev[0] == "conflict":
        print(f"  冲突！子句 {fmt_clause(ev[1])} 所有文字为假")
    elif ev[0] == "learn":
        print(f"  回跳  撤销决策 x{abs(ev[1][0])}，学习单位子句 {fmt_clause(ev[1])}；assign 全清回 0 级（重启式回跳）")
print(f"结果：{res}，学习子句 = {learned}")
print("手推锚点：恰学 (¬x1)——全程唯一决策是 x1，冲突责任全在它，决策取反 = 完整理由")
assert res == "UNSAT" and learned == [[-1]], (res, learned)
print("→ E1 自检通过")

print("\n" + "=" * 68)
print("E2 · mini-CDCL：G → SAT（模型即证书）")
print("=" * 68)
G = [[1, 2], [-1, 3]]
print("公式：G = (x1∨x2) ∧ (¬x1∨x3)")
trace2 = []
res2, model = cdcl_solve(G, 3, trace=trace2)
for ev in trace2:
    if ev[0] == "decide":
        print(f"  决策  x{ev[1]} = T")
    elif ev[0] == "prop":
        for var, val, c in ev[1]:
            print(f"  传播  x{var} = {'T' if val else 'F'}（由子句 {fmt_clause(c)}：其余文字已全假）")
model_str = ", ".join(f"x{v}={'T' if b else 'F'}" for v, b in sorted(model.items()))
print(f"结果：{res2}，模型 = {{{model_str}}}")
ok = all(any(model[abs(l)] == (l > 0) for l in c) for c in G)
print(f"逐子句验证：{'  '.join(fmt_clause(c) + '=T ✓' for c in G)}  ← 模型可独立代入检查")
assert res2 == "SAT" and ok, (res2, model)
print("→ E2 自检通过：可独立检查的满足赋值，正是 NP 的'证书'")

print("\n" + "=" * 68)
print("E3 · 对拍与理论组合：z3/cvc5 与 LRA×EUF")
print("=" * 68)
x1, x2, x3 = Bool("x1"), Bool("x2"), Bool("x3")
s = Solver()
s.add(Or(x1, x2), Or(Not(x1), x2), Or(Not(x2), x3), Or(Not(x2), Not(x3)))
assert str(s.check()) == "unsat"
print("z3   对 F check → unsat（与 E1 手写 CDCL 一致）")
s2 = Solver()
s2.add(Or(x1, x2), Or(Not(x1), x3))
assert str(s2.check()) == "sat"
print(f"     对 G check → sat，z3 模型 {s2.model()}（模型不唯一——我的 CDCL 给全 T，同为一个证书）")
try:
    import cvc5.pythonic as cvc5p          # pythonic 接口刻意与 z3 同风格
    cs = cvc5p.Solver()
    c1, c2, c3 = cvc5p.Bool("x1"), cvc5p.Bool("x2"), cvc5p.Bool("x3")
    cs.add(cvc5p.Or(c1, c2), cvc5p.Or(cvc5p.Not(c1), c2),
           cvc5p.Or(cvc5p.Not(c2), c3), cvc5p.Or(cvc5p.Not(c2), cvc5p.Not(c3)))
    assert str(cs.check()) == "unsat"
    print("cvc5 对 F check → unsat（双引擎对拍一致；正文给 SMT-LIB 文本版）")
except ImportError:
    print("cvc5 pythonic 不可用，跳过（正文给 SMT-LIB 文本对拍）")
s3 = Solver()
f = Function("f", RealSort(), RealSort())  # 未解释函数：EUF 的地盘
a = Real("a")
s3.add(f(a) > 1.0, a < 2.0, f(a) + a < 3.0)
assert str(s3.check()) == "sat"
print(f"LRA×EUF 组合：f(a)>1 ∧ a<2 ∧ f(a)+a<3 → {s3.check()}，z3 模型 {s3.model()}")
print("  接口变量 u:=f(a) 后：EUF 管函数表，LRA 管 1<u ∧ a<2 ∧ u+a<3——Nelson-Oppen 分工（03 章 §三）")
print("\nlab03 全部自检通过")
