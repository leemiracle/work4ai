"""
Part IA Foundations of Computer Science (Cambridge CST)
========================================================
覆盖主题：
- 集合、关系、函数（injective / surjective / bijective）
- 偏序集与格（Hasse 图、上确界 / 下确界）
- 基数与 Cantor 对角线论证（可数 vs 不可数）
- 停机问题归约（不可判定性证明）

核心教材：
- Velleman 2006 "How to Prove It" Cambridge University Press
- Huth & Ryan 2004 "Logic in Computer Science" 2nd ed, Cambridge University Press
- Devlin 2003 "Sets, Functions and Logic" 3rd ed, Chapman & Hall
- Turing 1936 "On Computable Numbers" Proc London Math Soc

本文件实现：
- Relation 操作（复合、逆、传递闭包）
- 偏序集 / 格验证（Warshall 算法求传递闭包）
- Cantor 对角线论证（实数不可数）
- 停机问题归约（矛盾证明）
- Schröder–Bernstein 基数比较

运行：
    python foundations.py
"""
from __future__ import annotations
from itertools import product


# ================================================================
# 1. 集合与关系
# ================================================================

class Relation:
    """二元关系 R ⊆ A × A，用 frozenset of (x, y) pairs 表示"""

    def __init__(self, pairs, universe=None):
        self.pairs = frozenset(pairs)
        self.universe = set(universe) if universe else {x for p in pairs for x in p}

    def contains(self, x, y):
        return (x, y) in self.pairs

    def compose(self, other: "Relation") -> "Relation":
        """(R ∘ S): x R∘S z ⟺ ∃y. (x,y)∈S ∧ (y,z)∈R"""
        new = set()
        for (x, y1) in other.pairs:
            for (y2, z) in self.pairs:
                if y1 == y2:
                    new.add((x, z))
        return Relation(new, self.universe | other.universe)

    def inverse(self) -> "Relation":
        return Relation({(y, x) for (x, y) in self.pairs}, self.universe)

    def is_reflexive(self) -> bool:
        return all((x, x) in self.pairs for x in self.universe)

    def is_symmetric(self) -> bool:
        return all((y, x) in self.pairs for (x, y) in self.pairs)

    def is_antisymmetric(self) -> bool:
        return all(not ((y, x) in self.pairs and x != y)
                   for (x, y) in self.pairs)

    def is_transitive(self) -> bool:
        for (x, y) in self.pairs:
            for (y2, z) in self.pairs:
                if y == y2 and (x, z) not in self.pairs:
                    return False
        return True

    def transitive_closure(self) -> "Relation":
        """Warshall / Floyd 算法求传递闭包"""
        elems = sorted(self.universe)
        idx = {e: i for i, e in enumerate(elems)}
        n = len(elems)
        M = [[False] * n for _ in range(n)]
        for (x, y) in self.pairs:
            M[idx[x]][idx[y]] = True
        # Floyd–Warshall
        for k in range(n):
            for i in range(n):
                if M[i][k]:
                    for j in range(n):
                        if M[k][j]:
                            M[i][j] = True
        new = {(elems[i], elems[j]) for i in range(n) for j in range(n) if M[i][j]}
        return Relation(new, self.universe)

    def __repr__(self):
        return f"Relation({sorted(self.pairs)})"


# ================================================================
# 2. 函数类型检查
# ================================================================

def classify_function(func_pairs, domain, codomain):
    """
    给定 graph 集合判定 injective / surjective / bijective。
    func_pairs: list of (x, y)
    """
    dom_vals = {}
    for x, y in func_pairs:
        if x in dom_vals and dom_vals[x] != y:
            return "not a function (multi-valued)"
        dom_vals[x] = y
    is_func = set(dom_vals) == set(domain)
    if not is_func:
        return "partial / not total on domain"
    rng = set(dom_vals.values())
    injective = len(rng) == len(dom_vals)  # 值域大小=定义域大小
    surjective = rng == set(codomain)
    if injective and surjective:
        return "bijective"
    if injective:
        return "injective (not surjective)"
    if surjective:
        return "surjective (not injective)"
    return "neither"


# ================================================================
# 3. 偏序集与格
# ================================================================

class Poset:
    """偏序集 (P, ≤)"""

    def __init__(self, leq_pairs):
        self.leq = Relation(leq_pairs)
        # 加入自反性闭包
        all_e = self.leq.universe
        reflexive = {(x, x) for x in all_e} | self.leq.pairs
        self.leq = Relation(reflexive, all_e)

    def upper_bounds(self, subset):
        """上界：对所有 s∈S, s ≤ u"""
        return {u for u in self.leq.universe
                if all((s, u) in self.leq.pairs for s in subset)}

    def lower_bounds(self, subset):
        return {l for l in self.leq.universe
                if all((l, s) in self.leq.pairs for s in subset)}

    def least_upper_bound(self, subset):
        ubs = self.upper_bounds(subset)
        if not ubs:
            return None
        for u in ubs:
            if all((u, other) in self.leq.pairs for other in ubs):
                return u
        return None  # 多个极小上界，无上确界

    def greatest_lower_bound(self, subset):
        lbs = self.lower_bounds(subset)
        if not lbs:
            return None
        for l in lbs:
            if all((other, l) in self.leq.pairs for other in lbs):
                return l
        return None

    def is_lattice(self) -> bool:
        """所有两元素子集都有上确界和下确界"""
        elems = sorted(self.leq.universe, key=str)
        for a in elems:
            for b in elems:
                if self.least_upper_bound({a, b}) is None:
                    return False
                if self.greatest_lower_bound({a, b}) is None:
                    return False
        return True


# ================================================================
# 4. Cantor 对角线论证（不可数性）
# ================================================================

def cantor_diagonal(n):
    """
    构造对角线实数：给定一个假设的实数列表，构造一个不在列表中的实数。
    用二进制小数演示。
    """
    import random
    random.seed(n)
    # 假设有人声称能列出 [0,1] 的所有实数（二进制小数）
    # 这里只列前 n 个
    listing = [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]
    # 对角线：第 i 个实数的第 i 位翻转
    diagonal = [1 - listing[i][i] for i in range(n)]
    # 验证 diagonal 不等于任何一个列出的实数
    matches = sum(1 for row in listing if row == diagonal)
    return diagonal, matches


# ================================================================
# 5. Schröder–Bernstein 定理演示
# ================================================================

def schroeder_bernstein_demo():
    """
    若 |A| ≤ |B| 且 |B| ≤ |A|，则 |A| = |B|。
    演示：自然数 ↔ 偶数（双向单射）。
    """
    A = set(range(10))
    B = set(range(0, 20, 2))
    f = {x: 2 * x for x in A}      # A → B 单射
    g = {y: y // 2 for y in B}     # B → A 单射
    assert set(f.values()) <= B
    assert set(g.values()) <= A
    return True


# ================================================================
# 6. 停机问题归约
# ================================================================

class HaltingProblem:
    """
    归约证明：假设存在 halts(prog, input)，则构造悖论。
    """

    @staticmethod
    def paradox(halts_func):
        """
        def D(x):
            if halts_func(x, x):
                loop_forever()      # 故意不停
            else:
                return              # 停

        问 halts(D, D)?
        - 若 halts(D, D)=True → D 不停（矛盾）
        - 若 halts(D, D)=False → D 停（矛盾）
        """
        def D(x):
            if halts_func(x, x):
                while True:     # 故意死循环
                    pass
            # else: 停止

        result = halts_func("D", "D")
        if result:
            actual = "diverge"  # D(D) 会死循环
        else:
            actual = "halt"
        # 矛盾：halts 说 halt 但实际 diverge，或反之
        contradiction = (result and actual == "diverge") or \
                        (not result and actual == "halt")
        return result, actual, contradiction


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IA Foundations of CS — Demo")
    print("=" * 64)

    # 1. 关系
    print("\n📋 1. 二元关系：复合与传递闭包")
    R = Relation({(1, 2), (2, 3), (3, 4)}, universe={1, 2, 3, 4})
    print(f"   R = {sorted(R.pairs)}")
    print(f"   R 传递? {R.is_transitive()}")
    tc = R.transitive_closure()
    print(f"   R⁺ 传递闭包 = {sorted(tc.pairs)}")
    print(f"   R⁺ 传递? {tc.is_transitive()}")

    # 2. 函数类型
    print("\n📋 2. 函数类型检查")
    f1 = [(1, 'a'), (2, 'b'), (3, 'c')]     # 双射
    f2 = [(1, 'a'), (2, 'a'), (3, 'b')]     # 非单射
    print(f"   f1 {f1}: {classify_function(f1, {1,2,3}, {'a','b','c'})}")
    print(f"   f2 {f2}: {classify_function(f2, {1,2,3}, {'a','b','c'})}")

    # 3. 偏序集与格
    print("\n📋 3. 偏序集与格（除数格）")
    # 6 的正除数按整除偏序
    divs = {1, 2, 3, 6}
    leq = {(a, b) for a in divs for b in divs if b % a == 0}
    poset = Poset(leq)
    print(f"   偏序: {sorted(poset.leq.pairs)}")
    print(f"   是格? {poset.is_lattice()}")
    lub = poset.least_upper_bound({2, 3})
    glb = poset.greatest_lower_bound({2, 3})
    print(f"   lub(2,3) = {lub}  （最小公倍数！）")
    print(f"   glb(2,3) = {glb}  （最大公约数！）")

    # 4. Cantor 对角线
    print("\n📋 4. Cantor 对角线论证")
    diag, matches = cantor_diagonal(20)
    print(f"   假设列出 20 个实数，对角线数 = {''.join(map(str, diag))}")
    print(f"   对角线数在列表中出现次数: {matches}")
    print(f"   → 无论列表多长，总存在不在列表中的实数（不可数！）")

    # 5. Schröder–Bernstein
    print("\n📋 5. Schröder–Bernstein 定理")
    ok = schroeder_bernstein_demo()
    print(f"   |N| = |偶数| 证明: {'✓' if ok else '✗'}")
    print(f"   f: n↦2n (单射 N→偶数), g: y↦y/2 (单射 偶数→N)")
    print(f"   ⟹ |N| = |偶数|（看似「偶数更少」，实则等势）")

    # 6. 停机问题
    print("\n📋 6. 停机问题归约（不可判定性）")
    # 模拟一个「假设的」halts 判定器
    def fake_halts(prog, inp):
        return True  # 假设它总能判定
    result, actual, contra = HaltingProblem.paradox(fake_halts)
    print(f"   假设 halts(D, D) = {result}")
    print(f"   但 D(D) 实际会 {actual}")
    print(f"   矛盾? {contra}")
    print(f"   ⟹ halts 函数不可能存在（停机问题不可判定）")

    print("\n✅ Foundations of CS 完成！")
    print("\n💡 反直觉发现：")
    print("   - 对角线论证：不管你怎么列实数，翻转对角线总能造出不在列表中的数")
    print("   - 停机问题：假设能判定停机 → 构造自我指涉的程序 → 矛盾")
    print("   - Schröder-Bernstein：自然数和偶数「一样多」——无限的反直觉")


if __name__ == "__main__":
    demo()
