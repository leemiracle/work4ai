#!/usr/bin/env python3
"""
进阶离散数学工具 - 补充示例
================================
新增: z3-solver (SMT/SAT), automata-lib (自动机), pyformlang (形式语言)
"""

import os
import sys

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def separator(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ============================================================
# 1. Z3 SMT Solver - 比 sympy.satisfiable 强大得多
# ============================================================
def demo_z3():
    separator("1. Z3 SMT/SAT Solver")

    from z3 import Bool, And, Or, Not, Implies, If, Int, Solver, sat, unsat

    # --- 1.1 基本SAT求解 ---
    print("【1.1】SAT求解 (比sympy快几个数量级)")
    p, q, r = Bools('p q r')
    s = Solver()
    s.add(Implies(p, q))
    s.add(Or(Not(q), r))
    s.add(p)
    print(f"  约束: (p→q) ∧ (¬q∨r) ∧ p")
    result = s.check()
    if result == sat:
        m = s.model()
        print(f"  可满足! 解: p={m[p]}, q={m[q]}, r={m[r]}")

    # --- 1.2 数独求解 ---
    print("\n【1.2】数独求解 (Z3经典应用)")
    grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    X = [[Int(f"x_{i}_{j}") for j in range(9)] for i in range(9)]
    s = Solver()

    for i in range(9):
        for j in range(9):
            s.add(X[i][j] >= 1, X[i][j] <= 9)
            if grid[i][j] != 0:
                s.add(X[i][j] == grid[i][j])

    for i in range(9):
        s.add(Distinct([X[i][j] for j in range(9)]))
        s.add(Distinct([X[j][i] for j in range(9)]))

    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            s.add(Distinct([X[i+di][j+dj] for di in range(3) for dj in range(3)]))

    if s.check() == sat:
        m = s.model()
        print("  解:")
        for i in range(9):
            row = " ".join(str(m[X[i][j]]) for j in range(9))
            print(f"    {row}")

    # --- 1.3 整数约束求解 ---
    print("\n【1.3】整数约束求解")
    x, y = Ints('x y')
    s = Solver()
    s.add(x + y == 10)
    s.add(x - y == 4)
    s.add(x > 0, y > 0)
    if s.check() == sat:
        m = s.model()
        print(f"  x + y = 10, x - y = 4, x>0, y>0")
        print(f"  解: x={m[x]}, y={m[y]}")

    # --- 1.4 逻辑推理验证 ---
    print("\n【1.4】验证: 逻辑推理有效性")
    p, q, r = Bools('p q r')

    def check_validity(premises, conclusion):
        s = Solver()
        s.add(And(*premises))
        s.add(Not(conclusion))
        return s.check() == unsat

    # 假言三段论: (p→q) ∧ (q→r) ⊢ (p→r)
    valid = check_validity(
        [Implies(p, q), Implies(q, r)],
        Implies(p, r)
    )
    print(f"  假言三段论 (p→q)∧(q→r)⊢(p→r): {'有效' if valid else '无效'}")

    # 析取三段论: (p∨q) ∧ ¬p ⊢ q
    valid2 = check_validity(
        [Or(p, q), Not(p)],
        q
    )
    print(f"  析取三段论 (p∨q)∧¬p⊢q: {'有效' if valid2 else '无效'}")

    # --- 1.5 N皇后问题 ---
    print("\n【1.5】N皇后问题 (8皇后)")
    N = 8
    queens = [Int(f"Q_{i}") for i in range(N)]
    s = Solver()
    for i in range(N):
        s.add(queens[i] >= 0, queens[i] < N)
    s.add(Distinct(queens))
    for i in range(N):
        for j in range(i+1, N):
            s.add(queens[i] - queens[j] != i - j)
            s.add(queens[i] - queens[j] != j - i)
    if s.check() == sat:
        m = s.model()
        positions = [m[queens[i]].as_long() for i in range(N)]
        print(f"  解: 列位置 = {positions}")
        for i in range(N):
            row = " ".join("Q" if j == positions[i] else "." for j in range(N))
            print(f"    {row}")


def Bools(names):
    from z3 import Bool
    return [Bool(n.strip()) for n in names.split()]

def Ints(names):
    from z3 import Int
    return [Int(n.strip()) for n in names.split()]

def Distinct(vars):
    from z3 import Distinct as Z3Distinct
    return Z3Distinct(*vars)


# ============================================================
# 2. automata-lib - 完整的自动机库
# ============================================================
def demo_automata():
    separator("2. automata-lib: 自动机理论")

    from automata.fa.dfa import DFA
    from automata.fa.nfa import NFA
    from automata.fa.gnfa import GNFA
    from automata.pda.pda import PDA
    from automata.pda.npda import NPDA
    from automata.tm.dtm import DTM
    from automata.tm.ntm import NTM

    # --- 2.1 DFA: 识别以'01'结尾的二进制串 ---
    print("【2.1】DFA: 识别包含子串'01'的二进制串")
    dfa_contains_01 = DFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'0', '1'},
        transitions={
            'q0': {'0': 'q1', '1': 'q0'},
            'q1': {'0': 'q1', '1': 'q2'},
            'q2': {'0': 'q2', '1': 'q2'},
        },
        initial_state='q0',
        final_states={'q2'},
    )
    for s in ['010', '111', '0011', '10', '0', '0101']:
        result = dfa_contains_01.accepts_input(s)
        print(f"  '{s}' -> {'Accept' if result else 'Reject'}")

    # --- 2.2 DFA: 识别被3整除的二进制数 ---
    print("\n【2.2】DFA: 识别 mod 3 == 0 的二进制数")
    dfa_mod3 = DFA(
        states={'s0', 's1', 's2'},
        input_symbols={'0', '1'},
        transitions={
            's0': {'0': 's0', '1': 's1'},
            's1': {'0': 's2', '1': 's0'},
            's2': {'0': 's1', '1': 's2'},
        },
        initial_state='s0',
        final_states={'s0'},
    )
    for s in ['0', '11', '110', '1010', '111']:
        result = dfa_mod3.accepts_input(s)
        val = int(s, 2)
        print(f"  '{s}' (= {val}, mod3={val%3}) -> {'Accept' if result else 'Reject'}")

    # --- 2.3 NFA: 识别以'0'结尾 ---
    print("\n【2.3】NFA: 识别以'0'结尾的二进制串")
    nfa = NFA(
        states={'q0', 'q1'},
        input_symbols={'0', '1'},
        transitions={
            'q0': {'0': {'q0', 'q1'}, '1': {'q0'}},
            'q1': {},
        },
        initial_state='q0',
        final_states={'q1'},
    )
    for s in ['0', '10', '110', '1', '11', '010']:
        result = nfa.accepts_input(s)
        print(f"  '{s}' -> {'Accept' if result else 'Reject'}")

    # --- 2.4 NFA → DFA 转换 ---
    print("\n【2.4】NFA → DFA 子集构造法")
    dfa_from_nfa = DFA.from_nfa(nfa)
    print(f"  NFA状态数: {len(nfa.states)}")
    print(f"  等价DFA状态数: {len(dfa_from_nfa.states)}")
    print(f"  等价DFA状态: {dfa_from_nfa.states}")

    # --- 2.5 DFA 最小化 ---
    print("\n【2.5】DFA最小化")
    dfa_big = DFA(
        states={'A', 'B', 'C', 'D', 'E', 'F'},
        input_symbols={'0', '1'},
        transitions={
            'A': {'0': 'B', '1': 'C'},
            'B': {'0': 'A', '1': 'D'},
            'C': {'0': 'E', '1': 'F'},
            'D': {'0': 'E', '1': 'F'},
            'E': {'0': 'E', '1': 'F'},
            'F': {'0': 'E', '1': 'F'},
        },
        initial_state='A',
        final_states={'C', 'D', 'E', 'F'},
    )
    dfa_min = dfa_big.minify()
    print(f"  原始DFA: {len(dfa_big.states)} 个状态")
    print(f"  最小化后: {len(dfa_min.states)} 个状态")

    # --- 2.6 DFA 等价性检验 ---
    print("\n【2.6】DFA等价性检验")
    dfa1 = DFA(
        states={'A', 'B'},
        input_symbols={'0', '1'},
        transitions={'A': {'0': 'A', '1': 'B'}, 'B': {'0': 'A', '1': 'B'}},
        initial_state='A', final_states={'B'},
    )
    dfa2 = DFA(
        states={'X', 'Y', 'Z'},
        input_symbols={'0', '1'},
        transitions={'X': {'0': 'X', '1': 'Y'}, 'Y': {'0': 'Z', '1': 'Y'}, 'Z': {'0': 'Z', '1': 'Y'}},
        initial_state='X', final_states={'Y'},
    )
    print(f"  DFA1 ({len(dfa1.states)}状态) == DFA2 ({len(dfa2.states)}状态): {dfa1 == dfa2}")

    # --- 2.7 正则表达式 → NFA ---
    print("\n【2.7】正则表达式转NFA")
    print("  automata-lib 支持 NFA↔DFA 互转和 DFA 最小化")
    print("  pyformlang 支持 正则表达式 ↔ DFA 互转 (见第3节)")

    # --- 2.8 图灵机 ---
    print("\n【2.8】图灵机说明")
    print("  automata-lib 支持 DTM/NTM/多带图灵机")
    print("  可识别 a^n b^n c^n 等上下文有关语言")
    print("  需要定义完整的转移函数 (状态×带符号 → 状态×写入×方向)")


# ============================================================
# 3. pyformlang - 形式语言与自动机(高级)
# ============================================================
def demo_pyformlang():
    separator("3. pyformlang: 形式语言理论")

    from pyformlang.regular_expression import Regex
    from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

    # --- 3.1 正则表达式 → DFA ---
    print("【3.1】正则表达式 → 最小DFA")
    regex = Regex("(0|1)*01")
    dfa = regex.to_epsilon_nfa().to_deterministic().minimize()
    print(f"  正则表达式: (0|1)*01")
    print(f"  最小DFA状态数: {len(dfa.states)}")

    for s in ['01', '001', '1101', '0', '10', '111']:
        result = dfa.accepts([Symbol(c) for c in s])
        print(f"  '{s}' -> {'Accept' if result else 'Reject'}")

    # --- 3.2 DFA → 正则表达式 ---
    print("\n【3.2】DFA → 正则表达式 (状态消除法)")

    # --- 3.3 正则表达式操作 ---
    print("\n【3.3】正则表达式运算")
    r1 = Regex("0*1")
    r2 = Regex("1*0")
    print(f"  r1 = 0*1 (以1结尾)")
    print(f"  r2 = 1*0 (以0结尾)")
    print(f"  r1 union r2: 匹配以0或1结尾的串")

    # --- 3.4 上下文无关文法 (CFG) ---
    print("\n【3.4】上下文无关文法")
    from pyformlang.cfg import CFG, Terminal, Variable
    cfg = CFG.from_text("""
    S -> a S b | epsilon
    """)
    print(f"  文法: S -> aSb | ε")
    print(f"  变量: {cfg.variables}")
    print(f"  产生式数: {len(cfg.productions)}")

    for s in ['', 'ab', 'aabb', 'aaabbb', 'abc']:
        result = cfg.contains(s)
        print(f"  '{s}' ∈ L(G)? {result}")


# ============================================================
# 4. 补充: 高级图论算法
# ============================================================
def demo_advanced_graph():
    separator("4. 高级图论算法补充")

    import networkx as nx

    # --- 4.1 最大流 ---
    print("【4.1】最大流 (Ford-Fulkerson)")
    G = nx.DiGraph()
    G.add_edge('s', 'a', capacity=3)
    G.add_edge('s', 'b', capacity=2)
    G.add_edge('a', 'b', capacity=2)
    G.add_edge('a', 't', capacity=2)
    G.add_edge('b', 't', capacity=3)
    flow_val, flow_dict = nx.maximum_flow(G, 's', 't')
    print(f"  最大流值: {flow_val}")
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            if f > 0:
                cap = G[u][v]['capacity']
                print(f"    {u}->{v}: {f}/{cap}")

    # --- 4.2 拓扑排序 ---
    print("\n【4.2】拓扑排序 (DAG)")
    DAG = nx.DiGraph([('A','B'), ('A','C'), ('B','D'), ('C','D'), ('D','E')])
    topo = list(nx.topological_sort(DAG))
    print(f"  DAG: A→B→D→E, A→C→D→E")
    print(f"  拓扑排序: {topo}")

    # --- 4.3 强连通分量 ---
    print("\n【4.3】强连通分量 (Tarjan)")
    DG = nx.DiGraph([(1,2),(2,3),(3,1),(3,4),(4,5),(5,6),(6,4)])
    sccs = list(nx.strongly_connected_components(DG))
    print(f"  有向图: 1→2→3→1→4→5→6→4")
    print(f"  强连通分量: {sccs}")

    # --- 4.4 中心性指标 ---
    print("\n【4.4】中心性指标")
    G2 = nx.karate_club_graph()
    deg_cen = nx.degree_centrality(G2)
    bet_cen = nx.betweenness_centrality(G2)
    clo_cen = nx.closeness_centrality(G2)
    eig_cen = nx.eigenvector_centrality(G2, max_iter=200)
    top_deg = max(deg_cen, key=deg_cen.get)
    top_bet = max(bet_cen, key=bet_cen.get)
    top_eig = max(eig_cen, key=eig_cen.get)
    print(f"  Zachary空手道俱乐部网络 (34节点)")
    print(f"  度中心性最高: 节点{top_deg} ({deg_cen[top_deg]:.3f})")
    print(f"  介数中心性最高: 节点{top_bet} ({bet_cen[top_bet]:.3f})")
    print(f"  特征向量中心性最高: 节点{top_eig} ({eig_cen[top_eig]:.3f})")

    # --- 4.5 二分图匹配 ---
    print("\n【4.5】二分图最大匹配 (Hopcroft-Karp)")
    B = nx.complete_bipartite_graph(3, 4)
    matching = nx.bipartite.maximum_matching(B)
    print(f"  K(3,4) 最大匹配数: {len(matching)//2}")
    print(f"  匹配: {[(k,v) for k,v in matching.items() if k < v]}")

    # --- 4.6 网络鲁棒性 ---
    print("\n【4.6】网络连通性分析")
    print(f"  节点连通度 κ: {nx.node_connectivity(G2)}")
    print(f"  边连通度 λ: {nx.edge_connectivity(G2)}")
    print(f"  代数连通度 (Fiedler值): {sorted(nx.laplacian_spectrum(G2))[1]:.4f}")


# ============================================================
# 5. 补充: 高级组合数学
# ============================================================
def demo_advanced_combinatorics():
    separator("5. 高级组合数学补充")

    # --- 5.1 矩阵快速幂求递推 ---
    print("【5.1】矩阵快速幂求 Fibonacci")
    import numpy as np
    def fib_matrix(n):
        if n == 0: return 0
        M = np.array([[1,1],[1,0]], dtype=object)
        result = np.linalg.matrix_power(M, n-1)
        return result[0][0]
    fibs = [fib_matrix(i) for i in range(12)]
    print(f"  F(0..11) = {fibs}")

    # --- 5.2 Burnside 引理 ---
    print("\n【5.2】Burnside引理: 珠项链着色")
    from math import gcd as math_gcd
    def necklace_count(n, k):
        """n颗珠子，k种颜色，旋转等价下的不同项链数"""
        total = 0
        for d in range(n):
            total += k ** math_gcd(d, n)
        return total // n
    print(f"  6颗珠子，2种颜色: {necklace_count(6, 2)} 种不同项链")
    print(f"  6颗珠子，3种颜色: {necklace_count(6, 3)} 种不同项链")
    print(f"  4颗珠子，2种颜色: {necklace_count(4, 2)} 种不同项链")

    # --- 5.3 Pólya 计数定理 ---
    print("\n【5.3】Pólya计数: 考虑旋转和翻转")
    def necklace_count_dihedral(n, k):
        """考虑旋转和翻转"""
        total = 0
        for d in range(n):
            total += k ** math_gcd(d, n)
        if n % 2 == 0:
            total += (n // 2) * k ** (n // 2) + (n // 2) * k ** (n // 2 + 1)
        else:
            total += n * k ** ((n + 1) // 2)
        return total // (2 * n)
    print(f"  4珠2色 (二面体群D4): {necklace_count_dihedral(4, 2)} 种")
    print(f"  6珠2色 (二面体群D6): {necklace_count_dihedral(6, 2)} 种")

    # --- 5.4 整数分拆 ---
    print("\n【5.4】整数分拆 (Partition)")
    from sympy import partition
    for n in range(1, 11):
        print(f"  p({n}) = {partition(n)}")

    # --- 5.5 生成所有子集 ---
    print("\n【5.5】子集生成 (位运算)")
    S = ['a', 'b', 'c', 'd']
    n = len(S)
    print(f"  集合: {S}")
    for mask in range(1 << n):
        subset = [S[i] for i in range(n) if mask & (1 << i)]
        print(f"    {mask:04b} -> {subset}")


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("  进阶离散数学工具 - 补充示例")
    print("=" * 70)

    demo_z3()
    demo_automata()
    demo_pyformlang()
    demo_advanced_graph()
    demo_advanced_combinatorics()

    print("\n" + "=" * 70)
    print("  所有进阶示例执行完毕!")
    print("=" * 70)
