"""
Formal Methods (Programmverifikation / PMM) — ETH Zürich
========================================================
覆盖主题：
- Kripke structure + CTL model checking
- SAT 求解（DPLL）
- SMT CDCL(T) 框架
- TLA+ 风格规约

核心教材/论文：
- Clarke, Grumberg, Peled "Model Checking" (MIT Press, 1999)
- Clarke, Emerson, Sistla "Automatic Verification of Finite-State Concurrent
  Systems Using Temporal Logic Specifications" ACM TOPLAS 8(2): 244-263 (1986) — CTL model checking 奠基
- Davis, Putnam, Logemann, Loveland "A Machine Program for Theorem-Proving"
  CACM 5(7): 394-397 (1962) — DPLL
- Marques-Silva, Sakallah "GRASP: A Search Algorithm for Propositional
  Satisfiability" IEEE TCAD 18(5): 508-518 (1999) — CDCL
- Lamport "Specifying Systems" (Addison-Wesley, 2002) — TLA+

本文件实现：
1. Kripke 结构 + CTL 符号化模型检测 (EG / EU / EX / EF)
2. DPLL SAT 求解器（含 unit propagation + pure literal）
3. 简易 SMT(T_LRA) 线性算术理论 + CDCL(T) 轮廓
4. TLA+ 风格 mutual exclusion 规约验证（完整 9 状态空间）

运行：
    python formal_methods.py
"""
from __future__ import annotations
import itertools


# ============ 1. Kripke 结构 + CTL 模型检测 ============

class Kripke:
    """
    Kripke结构 = (S, R, L)
    S: 状态集
    R: 迁移关系
    L: 标记函数（每个状态为真的原子命题）
    """

    def __init__(self, states: list[int], transitions: dict[int, list[int]],
                 labels: dict[int, set[str]]):
        self.states = states
        self.trans = transitions
        self.labels = labels

    def succ(self, s: int) -> list[int]:
        return self.trans.get(s, [])

    def pred(self, s: int) -> list[int]:
        return [p for p in self.states if s in self.succ(p)]


def ctl_EX(K: Kripke, sat_set: set[int]) -> set[int]:
    """EX phi: 存在一个后继满足 phi"""
    return {s for s in K.states if any(t in sat_set for t in K.succ(s))}


def ctl_AX(K: Kripke, sat_set: set[int]) -> set[int]:
    """AX phi: 所有后继满足 phi"""
    return {s for s in K.states if K.succ(s) and all(t in sat_set for t in K.succ(s))}


def ctl_EG(K: Kripke, sat_set: set[int]) -> set[int]:
    """
    EG phi: 存在一条路径，所有状态都满足 phi
    固定点迭代：Z = sat and {s | 存在 t in Z, s->t}
    """
    Z = set(sat_set)
    while True:
        new_Z = sat_set & {s for s in Z if any(t in Z for t in K.succ(s))}
        if new_Z == Z:
            return Z
        Z = new_Z


def ctl_EU(K: Kripke, sat_phi: set[int], sat_psi: set[int]) -> set[int]:
    """
    E[phi U psi]: 存在路径 phi 成立直到 psi 成立
    最小不动点：Z_0=空集; Z_{n+1} = sat_psi or (sat_phi and {s|存在 t in Z_n: s->t})
    """
    Z = set()
    while True:
        new_Z = sat_psi | (sat_phi & {s for s in K.states if any(t in Z for t in K.succ(s))})
        if new_Z == Z:
            return Z
        Z = new_Z


def ctl_EF(K: Kripke, sat_set: set[int]) -> set[int]:
    """EF phi = E[true U phi]: 存在路径最终到达 phi"""
    return ctl_EU(K, set(K.states), sat_set)


def ctl_AF(K: Kripke, sat_set: set[int]) -> set[int]:
    """AF phi = not EG(not phi)"""
    not_sat = set(K.states) - sat_set
    eg = ctl_EG(K, not_sat)
    return set(K.states) - eg


def eval_atom(K: Kripke, prop: str) -> set[int]:
    return {s for s in K.states if prop in K.labels.get(s, set())}


# ============ 2. DPLL SAT 求解器 ============

def parse_cnf(clauses: list[list[int]]) -> tuple[list[frozenset], set[int]]:
    vars_set = set()
    for cl in clauses:
        for lit in cl:
            vars_set.add(abs(lit))
    return [frozenset(cl) for cl in clauses], vars_set


def dpll(clauses: list[frozenset], assignment: dict[int, bool] | None = None,
         trace: list[str] | None = None) -> dict | None:
    """
    DPLL 算法（含 unit propagation + pure literal elimination）
    返回满足赋值 dict 或 None（UNSAT）

    trace: 可选，记录每步推导（用于展示 unit propagation 连锁）
    """
    if assignment is None:
        assignment = {}
    if trace is None:
        trace = []

    clauses = [c for c in clauses]  # copy

    # 应用当前赋值
    def simplify(clauses, var, val):
        new = []
        for cl in clauses:
            lit = var if val else -var
            if lit in cl:
                continue  # 子句满足
            new_cl = frozenset(l for l in cl if l != -lit)
            if not new_cl:
                return None  # 空子句 -> 冲突
            new.append(new_cl)
        return new

    # Unit propagation
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        for uc in unit_clauses:
            lit = next(iter(uc))
            var, val = abs(lit), (lit > 0)
            if var in assignment:
                if assignment[var] != val:
                    return None  # 矛盾
                continue
            assignment[var] = val
            trace.append(f"unit prop: var {var} = {val}")
            clauses = simplify(clauses, var, val)
            if clauses is None:
                return None
            changed = True

    if not clauses:
        return assignment  # 全部满足

    # Pure literal elimination
    all_lits = set()
    for c in clauses:
        all_lits |= c
    for lit in sorted(all_lits):
        if -lit not in all_lits:
            var = abs(lit)
            if var not in assignment:
                assignment[var] = lit > 0
                trace.append(f"pure literal: var {var} = {lit > 0}")
            clauses = [c for c in clauses if lit not in c]

    if not clauses:
        return assignment

    # 分支
    # 选变量
    first_var = abs(next(iter(next(iter(clauses)))))
    trace.append(f"branch: var {first_var}")
    for val in [True, False]:
        new_assign = dict(assignment)
        new_assign[first_var] = val
        new_clauses = simplify([frozenset(c) for c in clauses], first_var, val)
        if new_clauses is None:
            continue
        result = dpll(new_clauses, new_assign, trace)
        if result is not None:
            return result

    return None


# ============ 3. SMT (T_LRA) — CDCL(T) 轮廓 ============

class LinearConstraint:
    """线性约束: a1x1 + a2x2 + ... <= b"""
    def __init__(self, coeffs: dict[str, float], op: str, rhs: float):
        self.coeffs = coeffs
        self.op = op  # '<=', '>=', '<', '>', '=='
        self.rhs = rhs

    def evaluate(self, assignment: dict[str, float]) -> bool:
        val = sum(c * assignment.get(v, 0) for v, c in self.coeffs.items())
        if self.op == '<=':
            return val <= self.rhs
        elif self.op == '>=':
            return val >= self.rhs
        elif self.op == '==':
            return abs(val - self.rhs) < 1e-9
        elif self.op == '<':
            return val < self.rhs
        elif self.op == '>':
            return val > self.rhs
        return False

    def __repr__(self):
        terms = " + ".join(f"{c}{v}" for v, c in self.coeffs.items())
        return f"{terms} {self.op} {self.rhs}"


def smt_check(constraints: list[LinearConstraint], var_ranges: dict[str, list[float]]) -> dict | None:
    """
    简化 SMT 检查：枚举小值域（教学用）。
    真正 CDCL(T) 是 SAT 求解器 + 理论求解器交替。
    """
    var_names = list(var_ranges.keys())
    for combo in itertools.product(*[var_ranges[v] for v in var_names]):
        assignment = dict(zip(var_names, combo))
        if all(c.evaluate(assignment) for c in constraints):
            return assignment
    return None


# ============ 4. TLA+ 风格规约（完整 9 状态空间）============

def verify_mutex_spec():
    """
    TLA+ 风格互斥规约：
    变量 pc1, pc2 in {idle, wait, cs}
    不变式: not (pc1=cs and pc2=cs)

    完整 9 状态乘积空间 {idle,wait,cs}^2：
      state = pc1 * 3 + pc2  (0..8)
      state 8 = (cs, cs) 是需要排除的违例状态。

    协议规则（每个进程独立执行）：
      idle -> wait: 请求进入临界区
      wait -> cs:   仅当对方不在 cs 时才可进入
      cs -> idle:   离开临界区

    关键不变式：wait->cs 的迁移仅在对方 not in cs 时允许，
    使得 (cs,cs) 状态存在于状态空间中但永远不可达。
    """
    IDLE, WAIT, CS = 0, 1, 2
    state_names = ['idle', 'wait', 'cs']

    def sid(pc1, pc2):
        return pc1 * 3 + pc2

    def unpack(s):
        return s // 3, s % 3

    # 所有 9 个状态
    states = list(range(9))

    # 标记函数
    labels: dict[int, set[str]] = {}
    for s in range(9):
        pc1, pc2 = unpack(s)
        labels[s] = {f'p1_{state_names[pc1]}', f'p2_{state_names[pc2]}'}

    # 迁移关系
    transitions: dict[int, list[int]] = {}
    for s in range(9):
        pc1, pc2 = unpack(s)
        nxt = [s]  # self-loop（停留）

        # P1 迁移
        if pc1 == IDLE:
            nxt.append(sid(WAIT, pc2))
        elif pc1 == WAIT:
            if pc2 != CS:   # 仅当对方不在 CS 时才进入
                nxt.append(sid(CS, pc2))
        elif pc1 == CS:
            nxt.append(sid(IDLE, pc2))

        # P2 迁移
        if pc2 == IDLE:
            nxt.append(sid(pc1, WAIT))
        elif pc2 == WAIT:
            if pc1 != CS:   # 仅当对方不在 CS 时才进入
                nxt.append(sid(pc1, CS))
        elif pc2 == CS:
            nxt.append(sid(pc1, IDLE))

        transitions[s] = nxt

    K = Kripke(states, transitions, labels)

    # (cs,cs) = state 8
    both_cs = eval_atom(K, 'p1_cs') & eval_atom(K, 'p2_cs')
    assert sid(CS, CS) in both_cs, "state (cs,cs) must exist"

    # EF(both_cs): 哪些状态可达 (cs,cs)?
    ef_both = ctl_EF(K, both_cs)

    # 检查是否有其他状态的迁移指向 (cs,cs)
    incoming_to_cs_cs = [s for s in states
                         if sid(CS, CS) in transitions.get(s, []) and s != sid(CS, CS)]

    # 安全性：从初始状态 (idle,idle)=0 出发，(cs,cs) 不可达
    safe = 0 not in ef_both

    return K, safe, both_cs, ef_both, incoming_to_cs_cs


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Formal Methods: CTL + DPLL + SMT + TLA+")
    print("=" * 60)

    # 1. CTL Model Checking
    print("\n[1] Kripke 结构 + CTL 模型检测")
    # 交通灯状态机: 0=red, 1=green, 2=yellow
    states = [0, 1, 2]
    trans = {0: [1], 1: [2], 2: [0]}
    labels = {0: {'red'}, 1: {'green'}, 2: {'yellow'}}
    K = Kripke(states, trans, labels)

    green_states = eval_atom(K, 'green')
    af_green = ctl_AF(K, green_states)  # 从所有状态必然到达 green
    print(f"   状态: {states}, 迁移: {trans}")
    print(f"   AF(green) = {{所有状态必然到达 green}} = {sorted(af_green)}")
    print(f"   -> 从任何状态出发，必然经过 green: {'ok' if af_green == {0,1,2} else 'FAIL'}")

    eg_green = ctl_EG(K, green_states)
    print(f"   EG(green) = {sorted(eg_green)} (无法永远停留在 green)")

    # 2. DPLL
    print("\n[2] DPLL SAT 求解")
    # (p or q) and (not p or r) and (not q or r) and r -> SAT
    clauses = [[1, 2], [-1, 3], [-2, 3], [3]]  # p=1, q=2, r=3
    result = dpll([frozenset(c) for c in clauses])
    print(f"   (p or q) and (not p or r) and (not q or r) and r -> {'SAT' if result else 'UNSAT'}")
    print(f"   赋值: {result}")

    # UNSAT 例子: (p) and (not p)
    unsat = dpll([frozenset([1]), frozenset([-1])])
    print(f"   (p) and (not p) -> {'SAT' if unsat else 'UNSAT'}")

    # 3. SMT
    print("\n[3] SMT (线性算术)")
    constraints = [
        LinearConstraint({'x': 1}, '>=', 0),
        LinearConstraint({'y': 1}, '>=', 0),
        LinearConstraint({'x': 1, 'y': 1}, '<=', 10),
        LinearConstraint({'x': 2, 'y': 1}, '>=', 5),
    ]
    var_ranges = {'x': list(range(11)), 'y': list(range(11))}
    model = smt_check(constraints, var_ranges)
    print(f"   约束: x>=0, y>=0, x+y<=10, 2x+y>=5")
    print(f"   可满足模型: {model}")

    # 4. TLA+ 互斥（完整 9 状态）
    print("\n[4] TLA+ 风格互斥规约（完整 9 状态空间）")
    K2, safe, both_cs, ef_both, incoming = verify_mutex_spec()
    state_names = ['idle', 'wait', 'cs']
    print(f"   状态空间: {len(K2.states)} 个 (3x3 乘积: {{idle,wait,cs}}^2)")
    print(f"   (cs,cs) = state 8 存在于状态空间: {'ok' if 8 in both_cs else 'FAIL'}")
    print(f"   指向 (cs,cs) 的非自身迁移: {incoming} (应为空)")
    print(f"   EF(both_cs) = {sorted(ef_both)} (仅 state 8 自身)")
    init_reaches_violation = 0 in ef_both
    print(f"   从 (idle,idle) 可达 (cs,cs): {init_reaches_violation}")
    print(f"   不变式 not(p1_cs and p2_cs): {'ok 永远满足' if safe else 'FAIL 可违反'}")

    # 反直觉
    print("\n[*] 反直觉发现：DPLL 的 unit propagation 连锁")
    # 构造纯 unit propagation 链：(1), (-1,2), (-2,3), (-3,4), (-4,5)
    # [1] -> var1=True -> [-1,2] becomes [2] -> var2=True -> ...
    chain_clauses = [[1], [-1, 2], [-2, 3], [-3, 4], [-4, 5]]
    trace: list[str] = []
    r = dpll([frozenset(c) for c in chain_clauses], trace=trace)
    print(f"   5 个子句: [1], [-1,2], [-2,3], [-3,4], [-4,5]")
    print(f"   推导链: {' -> '.join(trace)}")
    n_assigned = len(r) if r else 0
    print(f"   结果: {r} ({n_assigned} 个变量)")
    pure_unit = all('branch' not in t for t in trace)
    print(f"   纯 unit propagation（无分支）: {pure_unit}")
    print(f"   -> {n_assigned} 个变量全部由 unit propagation 定出，零回溯！")

    print("\n[done] Formal Methods 完成!")


if __name__ == "__main__":
    demo()
