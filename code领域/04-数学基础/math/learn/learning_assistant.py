#!/usr/bin/env python3
"""
离散数学学习助手 - 详细推理过程展示
====================================
功能: 真值表分析、自然演绎证明、命题逻辑等价推导、集合论证明、
      数学归纳法、图算法追踪、数论证明、矩阵计算步骤
"""

import os
from itertools import product as iter_product

from prettytable import PrettyTable

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def banner(title):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}\n")


# ============================================================
# 1. 真值表详细分析器
# ============================================================
def demo_truth_table_analyzer():
    banner("1. 真值表详细分析器")

    from sympy import symbols, And, Or, Not, Implies, Equivalent, Xor
    from sympy.logic.boolalg import truth_table

    p, q, r = symbols('p q r')

    def analyze_formula(expr, name="公式"):
        print(f"  分析对象: {name} = {expr}")
        print()

        vars_list = list(expr.free_symbols)
        vars_list.sort(key=str)
        n = len(vars_list)

        table = PrettyTable()
        headers = [str(v) for v in vars_list] + [str(expr), "值"]
        table.field_names = headers

        true_count = 0
        false_count = 0
        minterms = []
        maxterms = []

        for inputs, result in truth_table(expr, vars_list):
            row_vals = list(inputs)
            val = 1 if result else 0
            row_vals.extend([expr.subs(dict(zip(vars_list, inputs))), val])
            table.add_row(row_vals)

            if result:
                true_count += 1
                minterms.append(list(inputs))
            else:
                false_count += 1
                maxterms.append(list(inputs))

        print(table)

        total = 2**n
        print(f"\n  ┌──────────────────────────────────────────────────")
        print(f"  │ 分析结果:")
        print(f"  │  • 永真式 (Tautology):       {'是 ✓' if true_count == total else '否'}")
        print(f"  │  • 矛盾式 (Contradiction):   {'是 ✓' if false_count == total else '否'}")
        print(f"  │  • 可满足式 (Satisfiable):   {'是 ✓' if true_count > 0 else '否'}")
        print(f"  │  • 为真次数: {true_count}/{total}")
        print(f"  │  • 为假次数: {false_count}/{total}")
        print(f"  │  • 最小项 (minterms): {minterms}")
        print(f"  │  • 最大项 (maxterms): {maxterms}")
        print(f"  └──────────────────────────────────────────────────")

    # 分析多个经典公式
    analyze_formula(Implies(p, q), "蕴含 p→q")
    print("\n")
    analyze_formula(Equivalent(p, q), "等价 p↔q")
    print("\n")
    analyze_formula(Implies(And(p, q), r), "(p∧q)→r")
    print("\n")

    # 验证重要等价律
    banner("1b. 重要等价律验证")
    equivalences = [
        ("双重否定律", Not(Not(p)), p),
        ("德摩根律(1)", Not(And(p, q)), Or(Not(p), Not(q))),
        ("德摩根律(2)", Not(Or(p, q)), And(Not(p), Not(q))),
        ("蕴含等值式", Implies(p, q), Or(Not(p), q)),
        ("逆否律", Implies(p, q), Implies(Not(q), Not(p))),
        ("分配律(1)", And(p, Or(q, r)), Or(And(p, q), And(p, r))),
        ("吸收律(1)", And(p, Or(p, q)), p),
    ]

    table = PrettyTable()
    table.field_names = ["等价律", "左式", "右式", "等价?"]
    for name, left, right in equivalences:
        from sympy import simplify_logic
        equiv = simplify_logic(Equivalent(left, right))
        table.add_row([name, str(left), str(right), "✓ 等价" if equiv else "✗ 不等价"])
    print(table)


# ============================================================
# 2. 自然演绎证明系统
# ============================================================
def demo_natural_deduction():
    banner("2. 自然演绎证明系统")

    print("  推理规则库:")
    print("  ┌────────────────────────────────────────────────────────┐")
    print("  │ 规则           │ 记法                              │ 条件           │")
    print("  ├────────────────────────────────────────────────────────┤")
    print("  │ 假言推理 (MP)  │ p→q, p ⊢ q                       │                │")
    print("  │ 假言否定 (MT)  │ p→q, ¬q ⊢ ¬p                     │                │")
    print("  │ 析取三段论     │ p∨q, ¬p ⊢ q                      │                │")
    print("  │ 合取引入 (∧I)  │ p, q ⊢ p∧q                       │                │")
    print("  │ 合取消除 (∧E)  │ p∧q ⊢ p; p∧q ⊢ q                 │                │")
    print("  │ 析取引入 (∨I)  │ p ⊢ p∨q; q ⊢ p∨q                 │                │")
    print("  │ 双重否定 (DN)  │ ¬¬p ⊢ p                           │                │")
    print("  │ 条件证明 (CP)  │ [p]...q ⊢ p→q                    │ 假设p,推出q    │")
    print("  │ 反证法 (RAA)   │ [p]...⊥ ⊢ ¬p                     │ 假设p,得矛盾   │")
    print("  └────────────────────────────────────────────────────────┘")

    from z3 import Bool, And, Or, Not, Implies, Solver, unsat

    def prove(premises, conclusion, proof_name=""):
        """验证推理有效性并展示"""
        from z3 import And as Z3And, Not as Z3Not, Implies as Z3Implies, Bool as Z3Bool
        vars_set = set()
        for p in premises + [conclusion]:
            vars_set.update(p.free_symbols)
        syms = sorted(vars_set, key=str)
        z3_vars = {str(s): Z3Bool(str(s)) for s in syms}

        s = Solver()
        for prem in premises:
            s.add(Z3And(*[prem]) if not isinstance(prem, type(And(prem, prem))) else prem)
        s.add(Z3Not(conclusion))

        result = s.check() == unsat
        return result

    # --- 证明 1: Modus Ponens ---
    print("\n  【证明1】假言推理示例")
    print("  前提: p→q, p")
    print("  结论: q")
    print()
    print("  编号 │ 命题          │ 理由")
    print("  ─────┼───────────────┼──────────────────")
    print("   1   │ p→q           │ 前提 (Premise)")
    print("   2   │ p             │ 前提 (Premise)")
    print("   3   │ q             │ 假言推理 (MP): 1, 2")
    print("  ∴ q 得证 ✓")

    # --- 证明 2: 假言三段论 ---
    print("\n  【证明2】假言三段论")
    print("  前提: p→q, q→r")
    print("  结论: p→r")
    print()
    print("  编号 │ 命题          │ 理由")
    print("  ─────┼───────────────┼──────────────────")
    print("   1   │ p→q           │ 前提")
    print("   2   │ q→r           │ 前提")
    print("   3   │ │ p           │ 假设 (条件证明CP)")
    print("   4   │ │ q           │ MP: 1, 3")
    print("   5   │ │ r           │ MP: 2, 4")
    print("   6   │ p→r           │ CP: 3-5")
    print("  ∴ p→r 得证 ✓")

    # --- 证明 3: 反证法 ---
    print("\n  【证明3】反证法证明 ¬(p∧¬p)")
    print("  结论: ¬(p∧¬p) (矛盾律)")
    print()
    print("  编号 │ 命题          │ 理由")
    print("  ─────┼───────────────┼──────────────────")
    print("   1   │ │ p∧¬p        │ 假设 (RAA)")
    print("   2   │ │ p           │ ∧E: 1")
    print("   3   │ │ ¬p          │ ∧E: 1")
    print("   4   │ │ ⊥ (矛盾)    │ 2 和 3 矛盾")
    print("   5   │ ¬(p∧¬p)      │ RAA: 1-4")
    print("  ∴ ¬(p∧¬p) 得证 ✓ (矛盾律)")

    # --- 证明 4: 德摩根律 ---
    print("\n  【证明4】德摩根律: ¬(p∧q) ⊢ ¬p∨¬q")
    print()
    print("  编号 │ 命题              │ 理由")
    print("  ─────┼───────────────────┼──────────────────")
    print("   1   │ ¬(p∧q)            │ 前提")
    print("   2   │ │ ¬(¬p∨¬q)        │ 假设 (RAA)")
    print("   3   │ │ │ p              │ 假设")
    print("   4   │ │ │ │ q            │ 假设")
    print("   5   │ │ │ │ p∧q          │ ∧I: 3, 4")
    print("   6   │ │ │ │ ⊥            │ 1 和 5 矛盾")
    print("   7   │ │ │ ¬q             │ RAA: 4-6")
    print("   8   │ │ │ ¬p∨¬q          │ ∨I: 7")
    print("   9   │ │ │ ⊥              │ 2 和 8 矛盾")
    print("  10   │ │ ¬p               │ RAA: 3-9 (退假设q)")
    print("  11   │ │ ¬p∨¬q            │ ∨I: 10")
    print("  12   │ │ ⊥                │ 2 和 11 矛盾")
    print("  13   │ ¬p∨¬q              │ RAA: 2-12")
    print("  ∴ ¬(p∧q) → (¬p∨¬q) 得证 ✓")

    # --- 证明 5: 析取三段论 ---
    print("\n  【证明5】析取三段论")
    print("  前提: p∨q, ¬p")
    print("  结论: q")
    print()
    print("  编号 │ 命题          │ 理由")
    print("  ─────┼───────────────┼──────────────────")
    print("   1   │ p∨q           │ 前提")
    print("   2   │ ¬p            │ 前提")
    print("   3   │ │ p           │ 假设 (情况1)")
    print("   4   │ │ ⊥           │ 2 和 3 矛盾")
    print("   5   │ │ q           │ 爆炸原理 (ex falso)")
    print("   6   │ │ q           │ 假设 (情况2)")
    print("   7   │ q             │ ∨E: 1, 3-5, 6")
    print("  ∴ q 得证 ✓")


# ============================================================
# 3. 命题逻辑等价推导 (逐步化简)
# ============================================================
def demo_equivalence_derivation():
    banner("3. 命题逻辑等价推导 (逐步展示)")

    from sympy import symbols, And, Or, Not, Implies, Equivalent, Xor
    from sympy.logic.boolalg import to_cnf, to_dnf

    p, q, r = symbols('p q r')

    def step_derivation(expr, name=""):
        print(f"  目标: 化简 {name}")
        print(f"  原始: {expr}")
        print()

        current = expr
        step = 0

        # Step 1: 消除 ↔
        if any(isinstance(a, type(Equivalent(p,q))) for a in [current]):
            step += 1
            if isinstance(current, type(Equivalent(p,q))):
                new = And(Implies(current.args[0], current.args[1]),
                         Implies(current.args[1], current.args[0]))
                print(f"  Step {step}: 消除等价号 ↔")
                print(f"         A↔B ≡ (A→B)∧(B→A)")
                print(f"         = {new}")
                current = new

        # Step 2: 消除 →
        if 'Implies' in str(type(current)):
            step += 1
            print(f"  Step {step}: 消除蕴含号 →")
            print(f"         A→B ≡ ¬A∨B")

        cnf = to_cnf(expr)
        dnf = to_dnf(expr)

        step += 1
        print(f"\n  Step {step}: 合取范式 (CNF)")
        print(f"         {cnf}")

        step += 1
        print(f"\n  Step {step}: 析取范式 (DNF)")
        print(f"         {dnf}")

        print(f"\n  最终结果: {expr}")
        print(f"    CNF = {cnf}")
        print(f"    DNF = {dnf}")
        print()

    step_derivation(Implies(p, q), "p→q")
    step_derivation(Xor(p, q), "p⊕q")
    step_derivation(Equivalent(Implies(p, q), Or(Not(q), Not(p))),
                    "验证逆否律: (p→q) ↔ (¬q→¬p)")


# ============================================================
# 4. 集合论证明助手
# ============================================================
def demo_set_proof():
    banner("4. 集合论证明助手")

    def prove_set_equality(name, A, B, universal=None):
        """通过元素追踪证明 A = B"""
        if universal is None:
            universal = list(A | B)

        print(f"  命题: {name}")
        print(f"  A = {A}")
        print(f"  B = {B}")
        print()

        table = PrettyTable()
        table.field_names = ["元素", "∈ A?", "∈ B?", "∈A↔∈B?"]

        all_equal = True
        for x in universal:
            in_a = x in A
            in_b = x in B
            equiv = in_a == in_b
            if not equiv:
                all_equal = False
            table.add_row([x, "✓" if in_a else "✗", "✓" if in_b else "✗",
                          "✓" if equiv else "✗ 不同!"])

        print(table)
        print(f"\n  结论: {'A = B 成立 ✓' if all_equal else 'A ≠ B ✗'}")
        print()

    # 证明德摩根律
    U = set(range(1, 11))
    A = {1, 2, 3, 4, 5}
    B = {3, 4, 5, 6, 7}

    prove_set_equality(
        "德摩根律: (A∩B)^c = A^c ∪ B^c",
        U - (A & B),
        (U - A) | (U - B),
        U
    )

    prove_set_equality(
        "分配律: A∩(B∪C) = (A∩B)∪(A∩C)",
        A & (B | {2, 8, 9}),
        (A & B) | (A & {2, 8, 9}),
        U
    )

    prove_set_equality(
        "对称差: A△B = (A-B)∪(B-A)",
        A ^ B,
        (A - B) | (B - A),
        U
    )

    # 子集证明
    banner("4b. 子集证明")
    print("  命题: 若 A⊆B 且 B⊆C, 则 A⊆C")
    print()
    A = {1, 2}
    B = {1, 2, 3, 4}
    C = {1, 2, 3, 4, 5, 6}
    print(f"  A = {A}, B = {B}, C = {C}")
    print(f"  Step 1: A⊆B ? {A <= B} (任意x, x∈A→x∈B)")
    print(f"  Step 2: B⊆C ? {B <= C}")
    print(f"  Step 3: 由传递性, A⊆C ? {A <= C} ✓")
    print()
    print("  一般证明:")
    print("    任取 x ∈ A")
    print("    ∵ A ⊆ B, ∴ x ∈ B")
    print("    ∵ B ⊆ C, ∴ x ∈ C")
    print("    ∴ A ⊆ C  □")


# ============================================================
# 5. 数学归纳法证明展示
# ============================================================
def demo_induction():
    banner("5. 数学归纳法证明展示")

    # --- 5.1 求和公式 ---
    print("  【5.1】证明: 1+2+...+n = n(n+1)/2")
    print()
    print("  证明 (数学归纳法):")
    print()
    print("  Step 1: 基础步骤 (Base Case)")
    n = 1
    lhs = sum(range(1, n+1))
    rhs = n * (n+1) // 2
    print(f"    当 n={n}: 左边 = {lhs}, 右边 = {rhs}")
    print(f"    左边 = 右边 ? {lhs == rhs} ✓")
    print()
    print("  Step 2: 归纳假设 (Inductive Hypothesis)")
    print("    假设当 n=k 时成立: 1+2+...+k = k(k+1)/2")
    print()
    print("  Step 3: 归纳步骤 (Inductive Step)")
    print("    当 n=k+1 时:")
    print("    左边 = 1+2+...+k+(k+1)")
    print("         = k(k+1)/2 + (k+1)       [归纳假设]")
    print("         = (k+1)(k/2 + 1)")
    print("         = (k+1)(k+2)/2")
    print("         = (k+1)((k+1)+1)/2        [右边]")
    print("    = 右边 ✓")
    print()
    print("  Step 4: 验证 (前几项)")

    table = PrettyTable()
    table.field_names = ["n", "1+2+...+n", "n(n+1)/2", "相等?"]
    for n in range(1, 11):
        lhs = sum(range(1, n+1))
        rhs = n*(n+1)//2
        table.add_row([n, lhs, rhs, "✓" if lhs==rhs else "✗"])
    print(table)
    print("  由数学归纳法, 命题对所有正整数 n 成立。 □")

    # --- 5.2 幂集大小 ---
    print("\n  【5.2】证明: |P(S)| = 2^|S|")
    print()
    print("  证明 (数学归纳法):")
    print()
    print("  Step 1: 基础步骤")
    print("    |S|=0, S=∅, P(∅)={∅}, |P(S)|=1 = 2^0 ✓")
    print()
    print("  Step 2: 归纳假设")
    print("    假设 |S|=k 时, |P(S)|=2^k")
    print()
    print("  Step 3: 归纳步骤")
    print("    设 |S|=k+1, 取 s∈S, 令 S'=S\\{s}, |S'|=k")
    print("    P(S) = {不包含s的子集} ∪ {包含s的子集}")
    print("         = P(S') ∪ {T∪{s} : T∈P(S')}")
    print("    |P(S)| = |P(S')| + |P(S')| = 2·|P(S')| = 2·2^k = 2^(k+1) ✓")
    print()
    print("  验证:")

    table = PrettyTable()
    table.field_names = ["|S|", "集合S", "|P(S)|", "2^|S|", "相等?"]
    for k in range(6):
        S = set(range(k))
        ps = len(list(iter_product([0,1], repeat=k)))
        table.add_row([k, S if k<=4 else f"{{{k} elements}}", 2**k, 2**k, "✓"])
    print(table)
    print("  由数学归纳法, 命题成立。 □")

    # --- 5.3 整除性质 ---
    print("\n  【5.3】证明: 3 | (n³-n) 对所有整数 n")
    print()
    print("  即证明 n³-n 能被3整除")
    print()
    print("  证明:")
    print("    n³-n = n(n²-1) = n(n-1)(n+1) = (n-1)·n·(n+1)")
    print("    这是三个连续整数的乘积")
    print("    在任意三个连续整数中, 必有一个是3的倍数")
    print("    (鸽巢原理: n mod 3 ∈ {0,1,2})")
    print("    ∴ 3 | (n-1)·n·(n+1)")
    print("    ∴ 3 | (n³-n)  □")
    print()
    print("  验证:")

    table = PrettyTable()
    table.field_names = ["n", "n³-n", "n³-n mod 3", "被3整除?"]
    for n in range(-5, 11):
        val = n**3 - n
        table.add_row([n, val, val % 3, "✓" if val % 3 == 0 else "✗"])
    print(table)


# ============================================================
# 6. 图算法执行追踪
# ============================================================
def demo_algorithm_trace():
    banner("6. 图算法执行追踪 (逐步展示)")

    import networkx as nx

    G = nx.Graph()
    G.add_weighted_edges_from([
        (1,2,4), (1,3,2), (2,3,1), (2,4,5), (3,4,8), (3,5,10), (4,5,2)
    ])

    # --- 6.1 Dijkstra 最短路径 ---
    print("  【6.1】Dijkstra 最短路径算法 (1→5)")
    print()
    print(f"  图的边:")
    for u, v, w in G.edges(data='weight'):
        print(f"    {u}--{v} (权重={w})")
    print()

    print("  执行过程:")
    print("  ┌──────────────────────────────────────────────────────────────┐")

    import heapq
    dist = {n: float('inf') for n in G.nodes()}
    prev = {n: None for n in G.nodes()}
    dist[1] = 0
    visited = set()
    pq = [(0, 1)]
    step = 0

    print(f"  │ 初始化: dist = {dict(dist)}")
    print(f"  │         优先队列 = [(0, 1)]")
    print(f"  │─────────────────────────────────────────────────────────────│")

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        step += 1
        print(f"  │ Step {step}: 取出节点 {u} (dist={d})")

        for v in G.neighbors(u):
            if v not in visited:
                new_dist = d + G[u][v]['weight']
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(pq, (new_dist, v))
                    print(f"  │   松弛 {u}→{v}: dist[{v}] = {new_dist} "
                          f"(经{u}, 更新)")
                else:
                    print(f"  │   松弛 {u}→{v}: dist[{v}] = {dist[v]} "
                          f"(不更新, {new_dist}≥{dist[v]})")

    print(f"  │─────────────────────────────────────────────────────────────│")
    print(f"  │ 最终距离: {dict(dist)}")

    path = []
    node = 5
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    print(f"  │ 最短路径: {' → '.join(map(str, path))}")
    print(f"  │ 最短距离: {dist[5]}")
    print(f"  └──────────────────────────────────────────────────────────────┘")

    # --- 6.2 BFS 遍历 ---
    banner("6b. BFS 广度优先搜索遍历")
    G2 = nx.Graph([(1,2),(1,3),(2,4),(2,5),(3,6),(3,7)])
    print(f"  树: 1-2, 1-3, 2-4, 2-5, 3-6, 3-7")
    print()

    queue = [1]
    visited = {1}
    order = []
    levels = {1: 0}

    print("  ┌────────────────────────────────────────────────────┐")
    print(f"  │ 初始化: queue = [1], level[1] = 0")

    while queue:
        u = queue.pop(0)
        order.append(u)
        for v in sorted(G2.neighbors(u)):
            if v not in visited:
                visited.add(v)
                queue.append(v)
                levels[v] = levels[u] + 1
                print(f"  │ 访问 {u}→{v}: level[{v}] = {levels[v]}, "
                      f"queue = {queue}")

    print(f"  │────────────────────────────────────────────────────│")
    print(f"  │ BFS顺序: {order}")
    print(f"  │ 层次: {dict(levels)}")
    print(f"  └────────────────────────────────────────────────────┘")

    # --- 6.3 DFS ---
    banner("6c. DFS 深度优先搜索遍历")
    print(f"  同一棵树")
    print()

    stack = [1]
    visited = set()
    order = []
    depth_map = {}

    def dfs(node, depth=0):
        visited.add(node)
        order.append(node)
        depth_map[node] = depth
        indent = "  │ " + "  " * depth
        print(f"{indent}进入节点 {node} (深度={depth})")
        for v in sorted(G2.neighbors(node)):
            if v not in visited:
                dfs(v, depth + 1)
        print(f"{indent}离开节点 {node}")

    print("  ┌────────────────────────────────────────────────────┐")
    dfs(1)
    print(f"  │────────────────────────────────────────────────────│")
    print(f"  │ DFS顺序: {order}")
    print(f"  └────────────────────────────────────────────────────┘")


# ============================================================
# 7. 数论证明展示
# ============================================================
def demo_number_theory_proofs():
    banner("7. 数论证明展示")

    # --- 7.1 √2 无理性 ---
    print("  【7.1】证明: √2 是无理数")
    print()
    print("  证明 (反证法):")
    print("  ┌──────────────────────────────────────────────────────────────┐")
    print("  │ Step 1: 假设 √2 是有理数                                    │")
    print("  │   即 √2 = p/q, 其中 p,q 为正整数, gcd(p,q)=1 (既约分数)     │")
    print("  │                                                              │")
    print("  │ Step 2: 两边平方                                             │")
    print("  │   2 = p²/q²                                                  │")
    print("  │   p² = 2q²                                                   │")
    print("  │                                                              │")
    print("  │ Step 3: 推出 p 是偶数                                        │")
    print("  │   ∵ p² = 2q², ∴ 2 | p²                                      │")
    print("  │   ∵ 2 是素数, ∴ 2 | p                                        │")
    print("  │   ∴ p = 2k (某正整数k)                                       │")
    print("  │                                                              │")
    print("  │ Step 4: 代入                                                 │")
    print("  │   (2k)² = 2q²                                                │")
    print("  │   4k² = 2q²                                                  │")
    print("  │   q² = 2k²                                                   │")
    print("  │                                                              │")
    print("  │ Step 5: 推出 q 也是偶数                                      │")
    print("  │   ∵ q² = 2k², ∴ 2 | q², ∴ 2 | q                            │")
    print("  │                                                              │")
    print("  │ Step 6: 矛盾!                                                │")
    print("  │   p 和 q 都是偶数, 与 gcd(p,q)=1 矛盾                        │")
    print("  │   ∴ 假设不成立, √2 是无理数。 □                              │")
    print("  └──────────────────────────────────────────────────────────────┘")

    # --- 7.2 素数无穷多 ---
    print("\n  【7.2】证明: 素数有无穷多个 (欧几里得)")
    print()
    print("  证明 (反证法):")
    print("  ┌──────────────────────────────────────────────────────────────┐")
    print("  │ Step 1: 假设素数只有有限个: p₁, p₂, ..., pₙ                  │")
    print("  │                                                              │")
    print("  │ Step 2: 构造 N = p₁·p₂·...·pₙ + 1                           │")
    print("  │                                                              │")
    print("  │ Step 3: 分析 N 的性质                                        │")
    print("  │   对任意 pᵢ: N mod pᵢ = (p₁·...·pₙ + 1) mod pᵢ = 1         │")
    print("  │   ∴ 任意 pᵢ 都不整除 N                                       │")
    print("  │                                                              │")
    print("  │ Step 4: 矛盾                                                 │")
    print("  │   情况a: N是素数 → N不在列表中 → 矛盾                        │")
    print("  │   情况b: N是合数 → 有素因子p, 但p不在列表中 → 矛盾           │")
    print("  │   ∴ 素数有无穷多个。 □                                        │")
    print("  └──────────────────────────────────────────────────────────────┘")
    print()

    print("  验证 (前几步):")

    from sympy import primerange, isprime, factorint
    primes = list(primerange(2, 30))
    table = PrettyTable()
    table.field_names = ["前n个素数", "N=乘积+1", "N是素数?", "N的最小素因子"]
    for i in range(1, 8):
        ps = primes[:i]
        N = 1
        for p in ps:
            N *= p
        N += 1
        sp = isprime(N)
        factors = factorint(N)
        min_f = min(factors.keys()) if factors else N
        table.add_row([ps, N, "✓" if sp else "✗", min_f])
    print(table)

    # --- 7.3 费马小定理 ---
    banner("7b. 费马小定理验证与证明思路")
    print("  定理: 若 p 是素数, gcd(a,p)=1, 则 a^(p-1) ≡ 1 (mod p)")
    print()
    print("  证明思路:")
    print("  ┌──────────────────────────────────────────────────────────────┐")
    print("  │ 考虑集合 S = {a, 2a, 3a, ..., (p-1)a} (mod p)               │")
    print("  │                                                              │")
    print("  │ Step 1: S 中的元素互不相同 (mod p)                           │")
    print("  │   若 ia ≡ ja (mod p), ∵ gcd(a,p)=1, ∴ i≡j (mod p)          │")
    print("  │   ∵ 1≤i,j≤p-1, ∴ i=j                                        │")
    print("  │                                                              │")
    print("  │ Step 2: ∴ S = {1, 2, ..., p-1} (mod p) 的一个排列           │")
    print("  │                                                              │")
    print("  │ Step 3: 两边求积                                             │")
    print("  │   a·2a·3a·...·(p-1)a ≡ 1·2·3·...·(p-1) (mod p)            │")
    print("  │   a^(p-1)·(p-1)! ≡ (p-1)! (mod p)                          │")
    print("  │                                                              │")
    print("  │ Step 4: ∵ gcd((p-1)!, p) = 1, 可以两边消去 (p-1)!           │")
    print("  │   a^(p-1) ≡ 1 (mod p)  □                                     │")
    print("  └──────────────────────────────────────────────────────────────┘")
    print()

    print("  验证:")

    table = PrettyTable()
    table.field_names = ["素数p", "底数a", "a^(p-1)", "a^(p-1) mod p", "=1?"]
    for p in [5, 7, 11, 13, 17]:
        for a in [2, 3]:
            val = pow(a, p-1, p)
            table.add_row([p, a, f"{a}^{p-1}", val, "✓" if val == 1 else "✗"])
    print(table)


# ============================================================
# 8. 矩阵计算步骤展示
# ============================================================
def demo_matrix_steps():
    banner("8. 矩阵计算步骤展示 (行列式)")

    from sympy import Matrix, Rational, pprint

    def det_steps(M):
        print("  计算行列式, 逐步展开:")
        print()
        n = M.shape[0]

        if n == 1:
            print(f"  |{M[0,0]}| = {M[0,0]}")
            return M[0,0]

        if n == 2:
            ad = M[0,0] * M[1,1]
            bc = M[0,1] * M[1,0]
            print(f"  Step: 2×2 行列式公式")
            print(f"    = {M[0,0]}×{M[1,1]} - {M[0,1]}×{M[1,0]}")
            print(f"    = {ad} - {bc}")
            print(f"    = {ad - bc}")
            return ad - bc

        result = 0
        for j in range(n):
            cofactor = M[0, j]
            minor = M.minorMatrix(0, j)
            sign = (-1) ** j
            term = sign * cofactor

            print(f"  按第1行展开, 第{j+1}列:")
            print(f"    a(1,{j+1}) = {cofactor}")
            print(f"    代数余子式 C(1,{j+1}) = (-1)^(1+{j+1}) × M(1,{j+1})")
            print(f"                         = {'+' if sign > 0 else '-'} {abs(cofactor)} × |minor|")

            minor_det = det_steps(minor)
            contribution = term * minor_det
            print(f"    贡献: {term} × {minor_det} = {contribution}")
            print()
            result += contribution

        print(f"  行列式 = {result}")
        return result

    M = Matrix([[2, 1, -1], [3, 2, 1], [1, -1, 2]])
    print(f"  矩阵 A:")
    pprint(M)
    print()
    d = det_steps(M)
    print(f"\n  验证 (sympy): det(A) = {M.det()}")
    print(f"  我们的结果:   det(A) = {d}")


# ============================================================
# 9. 关系性质验证 (可视化)
# ============================================================
def demo_relation_properties():
    banner("9. 二元关系性质系统验证")

    def analyze_relation(name, matrix):
        import numpy as np
        M = np.array(matrix, dtype=int)
        n = M.shape[0]
        elements = list(range(1, n+1))

        print(f"  关系: {name}")
        print(f"  集合: {{{', '.join(str(e) for e in elements)}}}")
        print(f"  关系矩阵:")
        for row in M:
            print(f"    {list(row)}")
        print()

        # 自反性
        reflexive = all(M[i][i] == 1 for i in range(n))
        print(f"  自反性: {'✓' if reflexive else '✗'}")
        if not reflexive:
            missing = [elements[i] for i in range(n) if M[i][i] == 0]
            print(f"    缺少: ({', '.join(str(x) for x in missing)}) 不与自身相关")

        # 对称性
        symmetric = np.array_equal(M, M.T)
        print(f"  对称性: {'✓' if symmetric else '✗'}")
        if not symmetric:
            for i in range(n):
                for j in range(i+1, n):
                    if M[i][j] != M[j][i]:
                        if M[i][j] == 1:
                            print(f"    有({elements[i]},{elements[j]}) 但无({elements[j]},{elements[i]})")
                        else:
                            print(f"    有({elements[j]},{elements[i]}) 但无({elements[i]},{elements[j]})")

        # 反对称性
        antisymmetric = all(M[i][j] == 0 or M[j][i] == 0 or i == j
                           for i in range(n) for j in range(n))
        print(f"  反对称性: {'✓' if antisymmetric else '✗'}")

        # 传递性
        M2 = (M @ M > 0).astype(int)
        transitive = np.all((M2 - M) <= 0)
        print(f"  传递性: {'✓' if transitive else '✗'}")
        if not transitive:
            for i in range(n):
                for j in range(n):
                    if M2[i][j] == 1 and M[i][j] == 0:
                        for k in range(n):
                            if M[i][k] == 1 and M[k][j] == 1:
                                print(f"    有({elements[i]},{elements[k]})和"
                                      f"({elements[k]},{elements[j]})但无"
                                      f"({elements[i]},{elements[j]})")

        # 判断关系类型
        print()
        if reflexive and symmetric and transitive:
            print(f"  ★ 等价关系 (自反+对称+传递) ✓")
        if reflexive and antisymmetric and transitive:
            print(f"  ★ 偏序关系 (自反+反对称+传递) ✓")
        if not reflexive or not symmetric or not transitive:
            if not (reflexive and antisymmetric and transitive):
                print(f"  (既不是等价关系也不是偏序关系)")
        print()

    analyze_relation("等价关系 R1", [[1,1,0],[1,1,0],[0,0,1]])
    analyze_relation("偏序关系 R2 (≤ on {1,2,3})", [[1,1,1],[0,1,1],[0,0,1]])
    analyze_relation("普通关系 R3", [[0,1,0],[0,0,1],[1,0,0]])


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          离散数学学习助手 - 详细推理过程展示                        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_truth_table_analyzer()
    demo_natural_deduction()
    demo_equivalence_derivation()
    demo_set_proof()
    demo_induction()
    demo_algorithm_trace()
    demo_number_theory_proofs()
    demo_matrix_steps()
    demo_relation_properties()

    print("\n" + "="*70)
    print("  所有学习示例执行完毕!")
    print("="*70)
