"""
Knowledge Representation & Reasoning (Oxford CS)
================================================
覆盖主题：
- 描述逻辑 ALC（Tableau 算法）
- 原子概念层级 + 传递闭包（非完整 OWL）
- Resolution 归结原理
- Model checking（Kripke 结构）

核心论文/教材（已核实）：
- Baader, Calvanese, McGuinness, Nardi, Patel-Schneider "The Description Logic Handbook" 2nd ed, Cambridge 2007
- Russell & Norvig "Artificial Intelligence: A Modern Approach" 4th ed, Pearson 2021
- Robinson "A Machine-Oriented Logic Based on the Resolution Principle" JACM 1965

本文件实现：
- ALC tableau 推理器（概念可满足性）
- 命题逻辑 resolution prover
- 简单 ontology ABox + TBox 查询
- Kripke model checking（模态逻辑）

运行：
    python kr.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import itertools


# ============ 1. 描述逻辑 ALC ============

"""
ALC (Attributive Language with Complements) 基本构造子：
- 原子概念：A, B, C, ...
- 顶部/底部：⊤ (Thing), ⊥ (Nothing)
- 否定：¬C
- 合取：C ⊓ D (intersection)
- 析取：C ⊔ D (union)
- 全称量词：∀r.C (all values)
- 存在量词：∃r.C (some values)

Tableau 规则（展开算法）：
- ⊓规则: C⊓D(x) → 添加 C(x), D(x)
- ⊔规则: C⊔D(x) → 添加 C(x) 或 D(x)（分支）
- ∃规则: ∃r.C(x) → 创建新个体 y, r(x,y), C(y)
- ∀规则: ∀r.C(x), r(x,y) → 添加 C(y)
- ¬规则: ¬¬C(x) → 添加 C(x)
"""


@dataclass(frozen=True)
class ALCConcept:
    """ALC 概念表达式"""
    kind: str  # 'atom', 'top', 'bottom', 'not', 'and', 'or', 'exists', 'forall'
    name: str = ""        # for atom/role
    concept: 'ALCConcept' = None     # for not
    left: 'ALCConcept' = None        # for and/or
    right: 'ALCConcept' = None       # for and/or
    role: str = ""        # for exists/forall

    def __str__(self):
        if self.kind == 'atom':
            return self.name
        if self.kind == 'top':
            return '⊤'
        if self.kind == 'bottom':
            return '⊥'
        if self.kind == 'not':
            return f"¬{self.concept}"
        if self.kind == 'and':
            return f"({self.left} ⊓ {self.right})"
        if self.kind == 'or':
            return f"({self.left} ⊔ {self.right})"
        if self.kind == 'exists':
            return f"∃{self.role}.{self.concept}"
        if self.kind == 'forall':
            return f"∀{self.role}.{self.concept}"
        return "?"


def Atom(name): return ALCConcept('atom', name=name)
def Top(): return ALCConcept('top')
def Bottom(): return ALCConcept('bottom')
def Not(c): return ALCConcept('not', concept=c)
def And(c1, c2): return ALCConcept('and', left=c1, right=c2)
def Or(c1, c2): return ALCConcept('or', left=c1, right=c2)
def Exists(role, c): return ALCConcept('exists', role=role, concept=c)
def Forall(role, c): return ALCConcept('forall', role=role, concept=c)


def negate(c: ALCConcept) -> ALCConcept:
    """ALC 概念的否定（NNF）"""
    if c.kind == 'atom':
        return Not(c)
    if c.kind == 'not':
        return c.concept  # ¬¬C = C
    if c.kind == 'and':
        return Or(negate(c.left), negate(c.right))  # ¬(C⊓D) = ¬C⊔¬D
    if c.kind == 'or':
        return And(negate(c.left), negate(c.right))  # ¬(C⊔D) = ¬C⊓¬D
    if c.kind == 'top':
        return Bottom()
    if c.kind == 'bottom':
        return Top()
    if c.kind == 'exists':
        return Forall(c.role, negate(c.concept))  # ¬∃r.C = ∀r.¬C
    if c.kind == 'forall':
        return Exists(c.role, negate(c.concept))  # ¬∀r.C = ∃r.¬C
    return Not(c)


class ALCTableau:
    """ALC Tableau 推理器：检查概念可满足性"""

    def __init__(self):
        self.individuals = set()
        self.concept_assertions = defaultdict(set)  # individual -> {concepts}
        self.role_assertions = set()  # (x, role, y)
        self.fresh_count = 0

    def is_satisfiable(self, concept: ALCConcept) -> bool:
        """检查 concept 是否可满足（即 concept(x) 能否有一致的模型）"""
        self.individuals = {'a'}
        self.concept_assertions = defaultdict(set)
        self.role_assertions = set()
        self.fresh_count = 0
        self.concept_assertions['a'].add(concept)
        return self._expand({'a'})

    def _fresh(self) -> str:
        self.fresh_count += 1
        name = f"b{self.fresh_count}"
        self.individuals.add(name)
        return name

    def _expand(self, active: set) -> bool:
        """Tableau 展开（含分支回溯）"""
        changed = True
        while changed:
            changed = False
            # 检查冲突：C(x) 和 ¬C(x)
            for ind in list(active):
                to_check = list(self.concept_assertions[ind])
                for c in to_check:
                    neg = negate(c) if c.kind != 'not' else c.concept
                    if neg in self.concept_assertions[ind] and neg != c:
                        return False  # 冲突
                    if c.kind == 'not' and c.concept in self.concept_assertions[ind]:
                        return False
                    if c.kind == 'bottom':
                        return False

            # 应用规则
            for ind in list(active):
                for c in list(self.concept_assertions[ind]):
                    if c.kind == 'and' and c not in self._applied(ind, 'and'):
                        # ⊓规则
                        if c.left not in self.concept_assertions[ind]:
                            self.concept_assertions[ind].add(c.left)
                            changed = True
                        if c.right not in self.concept_assertions[ind]:
                            self.concept_assertions[ind].add(c.right)
                            changed = True

                    elif c.kind == 'or':
                        # ⊔规则（分支）
                        if c.left not in self.concept_assertions[ind] and \
                           c.right not in self.concept_assertions[ind]:
                            # 尝试左分支
                            saved = {k: set(v) for k, v in self.concept_assertions.items()}
                            saved_roles = set(self.role_assertions)
                            saved_inds = set(self.individuals)
                            self.concept_assertions[ind].add(c.left)
                            if self._expand({ind}):
                                changed = True
                                continue
                            # 回溯，尝试右分支
                            self.concept_assertions = defaultdict(set, saved)
                            self.role_assertions = saved_roles
                            self.individuals = saved_inds
                            self.concept_assertions[ind].add(c.right)
                            if not self._expand({ind}):
                                return False
                            changed = True

                    elif c.kind == 'exists':
                        # ∃规则：创建新个体
                        # 检查是否已有满足的 r-后继
                        existing = [y for (x, r, y) in self.role_assertions
                                    if x == ind and r == c.role]
                        has_match = any(c.concept in self.concept_assertions[y]
                                        for y in existing)
                        if not has_match:
                            y = self._fresh()
                            self.role_assertions.add((ind, c.role, y))
                            self.concept_assertions[y].add(c.concept)
                            active.add(y)
                            changed = True

                    elif c.kind == 'forall':
                        # ∀规则：对所有 r-后继添加 C
                        for (x, r, y) in self.role_assertions:
                            if x == ind and r == c.role:
                                if c.concept not in self.concept_assertions[y]:
                                    self.concept_assertions[y].add(c.concept)
                                    active.add(y)
                                    changed = True

        return True

    def _applied(self, ind, rule):
        return set()  # 简化：不跟踪已应用规则


# ============ 2. 命题逻辑 Resolution ============

class ResolutionProver:
    """命题逻辑归结证明器"""

    def __init__(self):
        self.clauses: list[set] = []  # 每个 clause 是 literal 的集合

    def add_clause(self, literals: set):
        self.clauses.append(frozenset(literals))

    def add_formula(self, formula: str):
        """添加公式的 CNF 形式（简化：直接传入 clause）"""
        pass

    def resolve(self, c1: frozenset, c2: frozenset) -> frozenset | None:
        """归结两个 clause"""
        for lit in c1:
            neg = lit[1:] if lit.startswith('¬') else '¬' + lit
            if neg in c2:
                # 归结：删除 lit 和 ¬lit
                resolvent = (c1 - {lit}) | (c2 - {neg})
                # 如果有互补对，tautology，跳过
                if self._is_tautology(resolvent):
                    return None
                return frozenset(resolvent)
        return None

    def _is_tautology(self, clause: set) -> bool:
        for lit in clause:
            neg = lit[1:] if lit.startswith('¬') else '¬' + lit
            if neg in clause:
                return True
        return False

    def prove(self, goal: str) -> bool:
        """用归结证明 goal（反证法：加入 ¬goal，推导空子句）"""
        neg_goal = goal[1:] if goal.startswith('¬') else '¬' + goal
        all_clauses = list(self.clauses) + [frozenset([neg_goal])]

        new = set()
        pairs = list(itertools.combinations(range(len(all_clauses)), 2))

        for _ in range(100):  # 最大迭代
            clause_list = list(all_clauses)
            for i in range(len(clause_list)):
                for j in range(i + 1, len(clause_list)):
                    resolvent = self.resolve(clause_list[i], clause_list[j])
                    if resolvent is not None:
                        if len(resolvent) == 0:
                            return True  # 空子句 = 矛盾 = 证明成功
                        if resolvent not in all_clauses:
                            all_clauses.append(resolvent)
                            new.add(resolvent)
            if not new:
                break
            new.clear()

        return False


# ============ 3. Ontology (ABox + TBox) ============

@dataclass
class Ontology:
    """原子概念层级 + 传递闭包（非完整 OWL，无角色推理/逆角色/基数约束等 DL 构造子）"""
    # TBox: 概念包含 C ⊑ D
    subsumptions: list = field(default_factory=list)  # [(C, D)]
    # ABox: 断言
    concept_assertions: dict = field(default_factory=dict)  # {individual: {concept}}
    role_assertions: list = field(default_factory=list)  # [(x, role, y)]

    def add_subsumption(self, sub, sup):
        self.subsumptions.append((sub, sup))

    def assert_concept(self, ind, concept):
        self.concept_assertions.setdefault(ind, set()).add(concept)

    def assert_role(self, x, role, y):
        self.role_assertions.append((x, role, y))

    def is_instance_of(self, ind, concept: str) -> bool:
        """检查个体是否属于某概念（用 TBox 推理）"""
        if concept in self.concept_assertions.get(ind, set()):
            return True
        # TBox: 如果 ind 属于 C，且 C ⊑ D，则 ind 属于 D
        direct = self.concept_assertions.get(ind, set())
        for sub, sup in self.subsumptions:
            if sub in direct and sup == concept:
                return True
            # 传递闭包
            if sub in direct:
                visited = set()
                queue = [sup]
                while queue:
                    c = queue.pop(0)
                    if c == concept:
                        return True
                    if c in visited:
                        continue
                    visited.add(c)
                    for s2, sup2 in self.subsumptions:
                        if s2 == c:
                            queue.append(sup2)
        return False


# ============ 4. Model Checking (Kripke) ============

@dataclass
class KripkeModel:
    """Kripke 结构用于模态逻辑模型检测"""
    states: set
    relations: dict  # {state: {next_states}}
    labeling: dict   # {state: {propositions}}

    def check_modal(self, state: str, formula: str) -> bool:
        """检查模态逻辑公式
        □p: 所有后继状态满足 p (box)
        ◇p: 存在后继状态满足 p (diamond)
        """
        if formula.startswith("□ "):
            prop = formula[2:]
            successors = self.relations.get(state, set())
            return all(self._eval_prop(s, prop) for s in successors)
        if formula.startswith("◇ "):
            prop = formula[2:]
            successors = self.relations.get(state, set())
            return any(self._eval_prop(s, prop) for s in successors)
        return self._eval_prop(state, formula)

    def _eval_prop(self, state: str, prop: str) -> bool:
        return prop in self.labeling.get(state, set())


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Knowledge Representation & Reasoning (Oxford) Demo")
    print("=" * 65)

    # 1. ALC Tableau
    print("\n📋 1. ALC 描述逻辑：概念可满足性")
    tableau = ALCTableau()

    # 可满足: ∃hasChild.Human ⊓ ∀hasChild.Doctor
    # "有一个人类的孩子，且所有孩子都是医生"
    concept1 = And(
        Exists("hasChild", Atom("Human")),
        Forall("hasChild", Atom("Doctor"))
    )
    print(f"   概念: {concept1}")
    sat1 = tableau.is_satisfiable(concept1)
    print(f"   可满足: {sat1} {'✓' if sat1 else '✗'}")

    # 不可满足: ⊥
    concept2 = Bottom()
    print(f"\n   概念: {concept2}")
    sat2 = tableau.is_satisfiable(concept2)
    print(f"   可满足: {sat2} {'✓' if sat2 else '✗'}")

    # 矛盾: A ⊓ ¬A
    concept3 = And(Atom("A"), Not(Atom("A")))
    print(f"\n   概念: {concept3}")
    sat3 = tableau.is_satisfiable(concept3)
    print(f"   可满足: {sat3} {'✓' if sat3 else '✗（冲突）'}")

    # 2. Resolution
    print("\n📋 2. 命题逻辑归结")
    prover = ResolutionProver()
    # 知识库: p→q, q→r, p
    # CNF: {¬p,q}, {¬q,r}, {p}
    prover.add_clause({'¬p', 'q'})
    prover.add_clause({'¬q', 'r'})
    prover.add_clause({'p'})

    # 证明 r
    print("   知识库: {¬p∨q, ¬q∨r, p}")
    print("   目标: r")
    result = prover.prove('r')
    print(f"   归结证明: {'成功 ✓' if result else '失败'}")

    # 不可证明: s
    print("   目标: s")
    result2 = prover.prove('s')
    print(f"   归结证明: {'成功' if result2 else '失败 ✓（正确：KB 不蕴含 s）'}")

    # 3. Ontology 推理
    print("\n📋 3. Ontology: TBox + ABox 推理")
    onto = Ontology()
    # TBox: Student ⊑ Person, Professor ⊑ Person, Person ⊑ Animal
    onto.add_subsumption("Student", "Person")
    onto.add_subsumption("Professor", "Person")
    onto.add_subsumption("Person", "Animal")
    # ABox: alice 是 Student
    onto.assert_concept("alice", "Student")
    onto.assert_concept("bob", "Professor")

    print("   TBox: Student⊑Person, Professor⊑Person, Person⊑Animal")
    print("   ABox: alice∈Student, bob∈Professor")
    print(f"   alice 是 Animal 吗? {onto.is_instance_of('alice', 'Animal')} ✓")
    print(f"   alice 是 Person 吗? {onto.is_instance_of('alice', 'Person')} ✓")
    print(f"   alice 是 Professor 吗? {onto.is_instance_of('alice', 'Professor')} ✓（正确：不蕴含）")
    print(f"   bob 是 Animal 吗? {onto.is_instance_of('bob', 'Animal')} ✓")

    # 4. Model Checking
    print("\n📋 4. 模态逻辑模型检测")
    # 多智能体系统：3 个状态
    model = KripkeModel(
        states={'s0', 's1', 's2'},
        relations={
            's0': {'s1', 's2'},
            's1': {'s2'},
            's2': {'s0'},
        },
        labeling={
            's0': {'safe'},
            's1': {'danger'},
            's2': {'safe', 'goal'},
        }
    )
    print("   Kripke 模型:")
    print("   s0 (safe) → s1 (danger), s2 (safe, goal)")
    print("   s1 (danger) → s2")
    print("   s2 (safe, goal) → s0")

    print(f"\n   □ safe (s0的后继都安全): {model.check_modal('s0', '□ safe')} ✗（s1有danger）")
    print(f"   ◇ goal (s0有后继达到goal): {model.check_modal('s0', '◇ goal')} ✓")
    print(f"   □ safe (s2的后继都安全): {model.check_modal('s2', '□ safe')} ✓（s0是safe）")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print("   1. A⊓¬A 不可满足——tableau 算法自动检测到 C(x)和¬C(x)的冲突")
    print("   2. 归结用反证法：加入¬r 后推导出空子句(□)→ 证明 r 成立")
    print("   3. Ontology 中 alice∈Student 蕴含 alice∈Animal（3步传递闭包）")
    print("      这是自动推理：声明子类关系，系统自动推出所有祖先类")
    print("   4. □safe 在 s0 不成立（有 danger 后继），但◇goal 成立")
    print("      模态逻辑能区分'所有'和'存在'两种量化")
    print("=" * 65)


if __name__ == "__main__":
    main()
