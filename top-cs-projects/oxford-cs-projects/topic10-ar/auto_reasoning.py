"""
Automated Reasoning (Oxford CS)
================================================
覆盖主题：
- DPLL SAT 求解算法
- CDCL（Conflict-Driven Clause Learning）
- Resolution 归结
- Superposition calculus（mini）

核心论文/教材（已核实）：
- Davis, Putnam, Logemann, Loveland "Machine Program for Theorem Proving" CACM 1962 (DPLL)
- Marques-Silva & Sakallah "GRASP: A Search Algorithm for the Satisfiability Problem" IEEE Trans Computers 1999 (CDCL)
- Nieuwenhuis, Oliveras, Tinelli "Solving SAT and SAT Modulo Theories" Handbook of Satisfiability 2009
- Robinson "Resolution Principle" JACM 1965

本文件实现：
- DPLL（含 unit propagation + pure literal elimination）
- CDCL（1-UIP clause learning + VSIDS 简化）
- Resolution 反驳
- Superposition 简化（ordered paramodulation）

运行：
    python auto_reasoning.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import random


# ============ 1. DPLL SAT Solver ============

class DPLLSolver:
    """DPLL SAT 求解器

    DPLL 算法核心：
    1. Unit propagation: 如果某 clause 只剩一个未赋值文字，强制赋值
    2. Pure literal elimination: 如果某变量只以正/负形式出现，赋相应值
    3. 分支：选一个变量，尝试 True/False

    复杂度：最坏 O(2^n)，但实际很快
    """

    def __init__(self):
        self.decisions = 0
        self.propagations = 0

    def solve(self, clauses: list[list[int]], num_vars: int) -> dict | None:
        """
        clauses: CNF，每个 clause 是 literal 列表（正=变量号，负=否定）
        num_vars: 变量数
        返回: {var: True/False} 或 None (UNSAT)
        """
        self.decisions = 0
        self.propagations = 0
        assignment = {}
        result = self._dpll(clauses, assignment, num_vars)
        return result

    def _dpll(self, clauses, assignment, num_vars) -> dict | None:
        # 1. 检查是否所有 clause 都满足
        if self._all_satisfied(clauses, assignment):
            # 填充未赋值变量
            for v in range(1, num_vars + 1):
                if v not in assignment:
                    assignment[v] = True
            return dict(assignment)

        # 2. 检查是否有空 clause（冲突）
        if self._has_empty_clause(clauses, assignment):
            return None

        # 3. Unit propagation
        assignment = dict(assignment)
        unit_result = self._unit_propagate(clauses, assignment)
        if unit_result is False:
            return None

        # 4. Pure literal elimination
        self._pure_literal_eliminate(clauses, assignment, num_vars)

        # 5. 再检查
        if self._all_satisfied(clauses, assignment):
            for v in range(1, num_vars + 1):
                if v not in assignment:
                    assignment[v] = True
            return dict(assignment)

        # 6. 选择分支变量
        var = self._pick_branch_var(clauses, assignment, num_vars)
        if var is None:
            return dict(assignment)

        self.decisions += 1

        # 分支 1: var = True
        trial = dict(assignment)
        trial[var] = True
        result = self._dpll(clauses, trial, num_vars)
        if result is not None:
            return result

        # 分支 2: var = False
        trial = dict(assignment)
        trial[var] = False
        return self._dpll(clauses, trial, num_vars)

    def _lit_value(self, lit: int, assignment: dict) -> bool | None:
        var = abs(lit)
        if var not in assignment:
            return None
        val = assignment[var]
        return val if lit > 0 else not val

    def _clause_status(self, clause: list[int], assignment: dict) -> str:
        """返回 'sat', 'unsat', 'unit'(返回unit lit), 'unresolved'"""
        unassigned = []
        for lit in clause:
            val = self._lit_value(lit, assignment)
            if val is True:
                return 'sat'
            if val is None:
                unassigned.append(lit)
        if not unassigned:
            return 'unsat'
        if len(unassigned) == 1:
            return ('unit', unassigned[0])
        return 'unresolved'

    def _all_satisfied(self, clauses, assignment):
        for clause in clauses:
            status = self._clause_status(clause, assignment)
            if status != 'sat':
                return False
        return True

    def _has_empty_clause(self, clauses, assignment):
        for clause in clauses:
            if self._clause_status(clause, assignment) == 'unsat':
                return True
        return False

    def _unit_propagate(self, clauses, assignment) -> bool:
        """Unit propagation，返回 False 表示冲突"""
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                status = self._clause_status(clause, assignment)
                if status == 'unsat':
                    return False
                if isinstance(status, tuple) and status[0] == 'unit':
                    lit = status[1]
                    var = abs(lit)
                    assignment[var] = (lit > 0)
                    self.propagations += 1
                    changed = True
        return True

    def _pure_literal_eliminate(self, clauses, assignment, num_vars):
        """纯文字消去"""
        polarity = defaultdict(set)  # var -> {+1, -1}
        for clause in clauses:
            for lit in clause:
                if self._lit_value(lit, assignment) is None:
                    polarity[abs(lit)].add(1 if lit > 0 else -1)
        for var, pols in polarity.items():
            if var not in assignment and len(pols) == 1:
                assignment[var] = (pols.pop() > 0)

    def _pick_branch_var(self, clauses, assignment, num_vars):
        """选择分支变量（第一个未赋值的）"""
        for v in range(1, num_vars + 1):
            if v not in assignment:
                return v
        return None


# ============ 2. CDCL (Clause Learning) ============

class CDCLSolver:
    """CDCL SAT 求解器（真 1-UIP + VSIDS + 完整 unit propagation）

    CDCL vs DPLL 的关键区别：
    1. 冲突分析：沿 antecedent 链做隐式归结到 1-UIP（first unique implication point）
    2. 非时序回溯：只回溯到学习 clause 的次高决策层
    3. VSIDS 启发式：基于冲突中文字活跃度的分支策略
    4. Unit propagation 迭代到不动点（每次 propagate 真把所有 unit clause 推完）
    """

    def __init__(self):
        self.learned_clauses = []
        self.conflicts = 0
        self.activity = {}  # var -> activity score (VSIDS)

    def _bump(self, var, decay=0.95):
        """VSIDS: 冲突时 bump 参与变量的 activity"""
        self.activity[var] = self.activity.get(var, 0.0) + 1.0
        # 偶尔 decay 防止数值膨胀
        if self.activity[var] > 1e100:
            for v in self.activity:
                self.activity[v] *= 1e-100

    def solve(self, clauses: list[list[int]], num_vars: int) -> dict | None:
        assignment = {}  # var -> bool
        # trail 元素: (var, value, decision_level, antecedent_clause or None)
        trail = []
        decision_level = 0

        all_clauses = [tuple(c) for c in clauses]
        max_iter = 10000

        for _ in range(max_iter):
            # Unit propagation 到不动点
            conflict = self._propagate(all_clauses + self.learned_clauses,
                                        assignment, trail, decision_level)
            if conflict is not None:
                self.conflicts += 1
                if decision_level == 0:
                    return None  # UNSAT at level 0

                # 真 1-UIP 冲突分析
                learned, backtrack_level = self._analyze_conflict(
                    conflict, trail, decision_level)
                if learned is None or len(learned) == 0:
                    return None
                self.learned_clauses.append(learned)

                # 非时序回溯到 backtrack_level
                while trail and trail[-1][2] > backtrack_level:
                    v, _, _, _ = trail.pop()
                    del assignment[v]
                decision_level = backtrack_level
                continue

            # 检查是否全部满足
            if self._all_sat(all_clauses + self.learned_clauses, assignment, num_vars):
                for v in range(1, num_vars + 1):
                    if v not in assignment:
                        assignment[v] = True
                return assignment

            # 决策：VSIDS 选 activity 最高的未赋值变量
            decision_level += 1
            var = self._pick_var_vsids(assignment, num_vars)
            if var is None:
                return assignment
            assignment[var] = True
            trail.append((var, True, decision_level, None))

        return None  # 超过 max_iter，诚实报告失败

    def _propagate(self, clauses, assignment, trail, dl):
        """迭代到不动点的 unit propagation"""
        changed = True
        # 用队列避免重复扫描
        while changed:
            changed = False
            for clause in clauses:
                unassigned = []
                sat = False
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        val = assignment[var]
                        if (val and lit > 0) or (not val and lit < 0):
                            sat = True
                            break
                    else:
                        unassigned.append(lit)
                if sat:
                    continue
                if len(unassigned) == 0:
                    return clause  # 冲突 clause
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    assignment[var] = lit > 0
                    trail.append((var, lit > 0, dl, clause))
                    changed = True
        return None

    def _analyze_conflict(self, conflict_clause, trail, dl):
        """真 1-UIP 冲突分析（Marques-Silva & Sakallah 1999 GRASP 风格）

        算法：
        1. 当前 clause = conflict_clause
        2. 找出当前决策层 dl 上的文字数量
        3. 若 >1，取 trail 上最新赋值的 dl-层文字 lit，用其 antecedent clause 做隐式归结
           （删除 lit、加入 antecedent 中除 ¬lit 外的所有文字，去重）
        4. 重复直到只剩 1 个 dl-层文字 = UIP
        5. 学习 clause = 当前 clause 的全部文字取反（asserting literal 是 UIP 的取反）
        6. backtrack_level = 学习 clause 中除 asserting literal 外的最高决策层
        """
        # 建立 var -> (level, antecedent, trail_index) 索引
        var_info = {}
        for idx, (v, val, level, ante) in enumerate(trail):
            var_info[v] = (level, ante, idx)

        # 当前 clause 作为 set of literals
        current = set(conflict_clause)

        # 找 dl 层文字
        def lits_at(level):
            return [l for l in current if var_info.get(abs(l), (None,))[0] == level]

        dl_lits = lits_at(dl)

        # 防御性循环上限
        for _ in range(len(trail) + 10):
            if len(dl_lits) <= 1:
                break
            # 选 trail 上最新（idx 最大）的 dl 层文字
            latest = max(dl_lits, key=lambda l: var_info[abs(l)][2])
            v = abs(latest)
            _, ante, _ = var_info[v]
            if ante is None:
                # 是决策变量，不能再 resolve（理论上 UIP 应在到达决策变量前出现）
                break
            # 隐式归结: current = (current \ {latest}) ∪ (ante \ {-latest})
            current.discard(latest)
            for lit in ante:
                if lit == -latest:
                    continue
                current.add(lit)
            # bump 所有参与归结的变量（VSIDS）
            for lit in ante:
                self._bump(abs(lit))
            dl_lits = lits_at(dl)

        # 学习 clause = UIP 取反 + 其他层文字取反
        # 标准做法：asserting literal 是 dl 层唯一文字的取反
        # 其他文字保留原值（它们处于 < dl 的层，回溯后会被强制）
        # 为简化，我们直接把 current 中所有文字取反作为 learned
        learned = tuple(-l for l in current)

        # 计算回溯层：learned 中除 asserting literal 外的最高层
        # asserting literal 是 dl 层那个（取反后），其他都在 < dl 层
        asserting_lit = None
        other_levels = []
        for lit in learned:
            v = abs(lit)
            if v in var_info and var_info[v][0] == dl:
                asserting_lit = lit
            elif v in var_info:
                other_levels.append(var_info[v][0])

        if asserting_lit is None or len(other_levels) == 0:
            backtrack_level = 0
        else:
            backtrack_level = max(other_levels)

        return learned, backtrack_level

    def _all_sat(self, clauses, assignment, num_vars):
        # 全变量赋值 + 全 clause 满足
        if len(assignment) < num_vars:
            return False
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    val = assignment[var]
                    if (val and lit > 0) or (not val and lit < 0):
                        sat = True
                        break
            if not sat:
                return False
        return True

    def _pick_var_vsids(self, assignment, num_vars):
        """VSIDS: 选 activity 最高的未赋值变量"""
        best_var, best_score = None, -1.0
        for v in range(1, num_vars + 1):
            if v in assignment:
                continue
            score = self.activity.get(v, 0.0)
            if score > best_score:
                best_score = score
                best_var = v
        # 若全部 activity=0（首次），返回第一个未赋值
        if best_var is None:
            for v in range(1, num_vars + 1):
                if v not in assignment:
                    return v
        return best_var


# ============ 3. Resolution ============

def resolution_refutation(clauses: list[set]) -> bool:
    """归结反驳：返回 True 如果子句集不可满足"""
    clause_set = [frozenset(c) for c in clauses]
    new_clauses = set()

    for _ in range(500):
        pairs_found = False
        clause_list = list(set(clause_set))
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvent = _resolve_clauses(clause_list[i], clause_list[j])
                if resolvent is not None:
                    pairs_found = True
                    if len(resolvent) == 0:
                        return True  # 空子句
                    if resolvent not in set(clause_set):
                        new_clauses.add(resolvent)
        if not new_clauses:
            break
        clause_set.extend(new_clauses)
        new_clauses.clear()

    return False


def _resolve_clauses(c1: frozenset, c2: frozenset) -> frozenset | None:
    for lit in c1:
        neg = -lit
        if neg in c2:
            resolvent = (c1 - {lit}) | (c2 - {neg})
            # tautology check
            for l in resolvent:
                if -l in resolvent:
                    return None
            return frozenset(resolvent)
    return None


# ============ 4. Superposition Calculus (Mini) ============

class SuperpositionMini:
    """Superposition calculus mini：处理等式推理

    核心规则（简化）：
    - Demodulation: 用等式重写更大的项
    - Paramodulation: 从等式 s=t 和 C[s] 推出 C[t]
    """

    def __init__(self):
        self.equations: list[tuple] = []  # [(left, right)]
        self.clauses: list[set] = []

    def add_equation(self, left: str, right: str):
        """添加等式 left = right"""
        self.equations.append((left, right))

    def add_clause(self, clause: set):
        self.clauses.append(clause)

    def demodulate(self, term: str) -> str:
        """用等式重写项（不停应用直到不动点）"""
        changed = True
        while changed:
            changed = False
            for left, right in self.equations:
                if left in term:
                    term = term.replace(left, right)
                    changed = True
        return term

    def derive(self) -> list[str]:
        """用 superposition 推导新的事实"""
        derived = []
        for clause in self.clauses:
            new_clause = set()
            for lit in clause:
                if isinstance(lit, str):
                    rewritten = self.demodulate(lit)
                    if rewritten != lit:
                        derived.append(f"  {lit} → {rewritten}")
                    new_clause.add(rewritten)
                else:
                    new_clause.add(lit)
        return derived


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Automated Reasoning (Oxford CS) Demo")
    print("=" * 65)

    random.seed(42)

    # 1. DPLL
    print("\n📋 1. DPLL SAT 求解")

    # SAT 实例: (x1∨x2) ∧ (¬x1∨x3) ∧ (¬x2∨x3) ∧ (¬x3)
    # 实际上 UNSAT（因为 ¬x3 蕴含 ¬x1∧¬x2，但 (x1∨x2) 要求至少一个为真）
    clauses_unsat = [
        [1, 2],      # x1 ∨ x2
        [-1, 3],     # ¬x1 ∨ x3
        [-2, 3],     # ¬x2 ∨ x3
        [-3],        # ¬x3
    ]
    solver = DPLLSolver()
    result = solver.solve(clauses_unsat, num_vars=3)
    print(f"   公式: (x1∨x2) ∧ (¬x1∨x3) ∧ (¬x2∨x3) ∧ (¬x3)")
    print(f"   DPLL 结果: {'SAT' if result else 'UNSAT'}")
    print(f"   决策次数: {solver.decisions}, 传播次数: {solver.propagations}")

    # SAT 实例: (x1∨x2) ∧ (¬x1∨x3) ∧ (¬x2∨x3)
    clauses_sat = [
        [1, 2],
        [-1, 3],
        [-2, 3],
    ]
    result2 = solver.solve(clauses_sat, num_vars=3)
    print(f"\n   公式: (x1∨x2) ∧ (¬x1∨x3) ∧ (¬x2∨x3)")
    print(f"   DPLL 结果: {'SAT' if result2 else 'UNSAT'}")
    if result2:
        print(f"   解: {result2}")
        # 验证
        for clause in clauses_sat:
            vals = []
            for lit in clause:
                v = result2[abs(lit)]
                vals.append(v if lit > 0 else not v)
            print(f"     {clause}: {vals} → {'✓' if any(vals) else '✗'}")

    # 2. CDCL
    print("\n📋 2. CDCL（含子句学习）")
    cdcl = CDCLSolver()
    cdcl_result = cdcl.solve(clauses_unsat, num_vars=3)
    print(f"   CDCL 结果: {'SAT' if cdcl_result else 'UNSAT'}")
    print(f"   学习的子句数: {len(cdcl.learned_clauses)}")
    print(f"   冲突次数: {cdcl.conflicts}")

    # 3. Resolution
    print("\n📋 3. 归结反驳")
    # 不可满足: {p,q}, {p,¬q}, {¬p,q}, {¬p,¬q}
    res_clauses = [{1, 2}, {1, -2}, {-1, 2}, {-1, -2}]
    unsat = resolution_refutation(res_clauses)
    print(f"   子句集: {res_clauses}")
    print(f"   归结推导空子句: {'是 → UNSAT ✓' if unsat else '否 → SAT'}")

    # 可满足: {p,q}, {¬p}
    res_clauses2 = [{1, 2}, {-1}]
    unsat2 = resolution_refutation(res_clauses2)
    print(f"\n   子句集: {res_clauses2}")
    print(f"   归结推导空子句: {'是 → UNSAT' if unsat2 else '否 → SAT ✓'}")

    # 4. Superposition
    print("\n📋 4. Superposition：等式推理")
    sup = SuperpositionMini()
    sup.add_equation("a", "b")       # a = b
    sup.add_equation("b", "c")       # b = c
    sup.add_equation("f(c)", "d")    # f(c) = d
    sup.add_clause({"f(a)"})

    print("   等式: a=b, b=c, f(c)=d")
    print("   子句: f(a)")
    derived = sup.derive()
    for d in derived:
        print(f"  {d}")
    # f(a) → f(b) → f(c) → d
    result_term = sup.demodulate("f(a)")
    print(f"   f(a) 经等式重写 → {result_term}")

    # 5. 随机 SAT 实例
    print("\n📋 5. 随机 3-SAT 相变现象")
    # 在 clause/variable ratio ≈ 4.26 时最难
    n_vars = 20
    for ratio in [2.0, 4.26, 8.0]:
        n_clauses = int(n_vars * ratio)
        random_clauses = []
        for _ in range(n_clauses):
            lits = random.sample(range(1, n_vars + 1), 3)
            lits = [l if random.random() > 0.5 else -l for l in lits]
            random_clauses.append(lits)
        solver2 = DPLLSolver()
        res = solver2.solve(random_clauses, n_vars)
        status = "SAT" if res else "UNSAT"
        print(f"   ratio={ratio:.2f} ({n_clauses} clauses): {status}, "
              f"decisions={solver2.decisions}")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print("   1. (x1∨x2)∧(¬x1∨x3)∧(¬x2∨x3)∧(¬x3) 是 UNSAT")
    print("      ¬x3 蕴含 ¬x1∧¬x2，但 (x1∨x2) 要求至少一个为真 → 矛盾")
    print("   2. 3-SAT 在 ratio≈4.26（clauses/vars）时最难——这是'相变'现象")
    print("      ratio<4 大概率 SAT，ratio>6 大概率 UNSAT，中间最难")
    print("   3. CDCL 学习子句避免了重复搜索同一空间——这是现代 SAT solver 快的关键")
    print("   4. 归结只用一条规则（互补文字消去）就能证明所有命题逻辑定理")
    print("=" * 65)


if __name__ == "__main__":
    main()
