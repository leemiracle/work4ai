#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离散数学工具箱 - 典型示例集合
==============================
涵盖：数理逻辑、集合论、组合数学、图论、代数结构、数论、离散优化
依赖：sympy, networkx, igraph, numpy, scipy, matplotlib, pyeda, pulp, pydot
"""

import os
import math
import itertools
from fractions import Fraction
from collections import Counter

import numpy as np
from scipy.special import comb as scipy_comb, perm as scipy_perm
from scipy.linalg import expm

import sympy as sp
from sympy import (
    symbols, Symbol, sympify, simplify, expand, factor,
    And, Or, Not, Xor, Implies, Equivalent, Nand, Nor,
    satisfiable, to_cnf, to_dnf,
    FiniteSet, Union, Intersection, Complement, EmptySet, UniversalSet,
    Interval, ProductSet, PowerSet,
    Matrix, eye, zeros, det, trace,
    gcd, lcm, isprime, primerange, factorint, totient, mod_inverse,
    binomial, factorial, fibonacci, catalan,
    solve, Eq, Rational,
)
from sympy.combinatorics import Permutation, PermutationGroup, Cycle
from sympy.logic import SOPform, POSform
from sympy.logic.boolalg import BooleanTrue, BooleanFalse, truth_table

import networkx as nx
import igraph as ig

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

_chinese_fonts = [f.name for f in fm.fontManager.ttflist
                  if any(k in f.name for k in ['Microsoft YaHei', 'SimHei', 'SimSun', 'Noto Sans SC'])]
if _chinese_fonts:
    plt.rcParams['font.sans-serif'] = _chinese_fonts + plt.rcParams['font.sans-serif']
plt.rcParams['axes.unicode_minus'] = False

from pyeda.inter import exprvar, expr, espresso_exprs, truthtable as pyeda_tt, expr2truthtable

from pulp import (
    LpProblem, LpMaximize, LpMinimize, LpVariable,
    LpBinary, LpInteger, lpSum, LpStatus, value
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def separator(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ============================================================
# 1. 数理逻辑 (Mathematical Logic)
# ============================================================
def demo_logic():
    separator("1. 数理逻辑 (Mathematical Logic)")

    # --- 1.1 命题与逻辑运算 ---
    print("【1.1】命题逻辑基本运算")
    p, q, r = symbols('p q r')

    expr_and = And(p, q)
    expr_or = Or(p, q)
    expr_not = Not(p)
    expr_implies = Implies(p, q)
    expr_equiv = Equivalent(p, q)
    expr_xor = Xor(p, q)
    expr_nand = Nand(p, q)
    expr_nor = Nor(p, q)

    formulas = {
        "合取 (AND)": expr_and,
        "析取 (OR)": expr_or,
        "否定 (NOT)": expr_not,
        "蕴含 (IMPLIES)": expr_implies,
        "等价 (EQUIV)": expr_equiv,
        "异或 (XOR)": expr_xor,
        "与非 (NAND)": expr_nand,
        "或非 (NOR)": expr_nor,
    }
    for name, f in formulas.items():
        print(f"  {name}: {f}")

    # --- 1.2 真值表 ---
    print("\n【1.2】真值表")
    expr_complex = Implies(And(p, q), r)
    print(f"  表达式: {expr_complex}")
    print("  真值表:")
    tt = truth_table(expr_complex, [p, q, r])
    for row in tt:
        print(f"    {row}")

    # --- 1.3 可满足性 ---
    print("\n【1.3】可满足性检验 (SAT)")
    formula = And(Implies(p, q), Or(Not(q), r), p)
    print(f"  公式: {formula}")
    result = satisfiable(formula)
    print(f"  可满足: {result}")

    # --- 1.4 CNF / DNF 转换 ---
    print("\n【1.4】CNF (合取范式) 与 DNF (析取范式)")
    formula = Xor(p, q)
    print(f"  原始: {formula}")
    print(f"  CNF:  {to_cnf(formula)}")
    print(f"  DNF:  {to_dnf(formula)}")

    # --- 1.5 主析取/合取范式 ---
    print("\n【1.5】主析取范式 (SOP) 与主合取范式 (POS)")
    sop = SOPform([p, q], [[1,1]])
    pos = POSform([p, q], [[1,1]])
    print(f"  p AND q 的 SOP: {sop}")
    print(f"  p AND q 的 POS: {pos}")

    # --- 1.6 pyeda: 布尔函数化简 (Espresso算法) ---
    print("\n【1.6】pyeda 布尔函数化简 (Espresso算法)")
    a, b, c = map(exprvar, 'abc')
    f1 = a & b | a & c | b & c
    print(f"  原始: {f1}")
    f1_simplified = f1.simplify()
    print(f"  化简: {f1_simplified}")

    # pyeda truth table
    print("\n  pyeda 真值表:")
    tt_obj = expr2truthtable(a & b | a & c)
    print(f"  {tt_obj}")

    # --- 1.7 推理规则验证 ---
    print("\n【1.7】推理规则验证 (假言推理 Modus Ponens)")
    premise1 = Implies(p, q)
    premise2 = p
    conclusion = q
    combined = And(premise1, premise2)
    is_valid = satisfiable(And(combined, Not(conclusion))) is False
    print(f"  前提1: {premise1}")
    print(f"  前提2: {premise2}")
    print(f"  结论:  {conclusion}")
    print(f"  推理有效: {is_valid}")


# ============================================================
# 2. 集合论 (Set Theory)
# ============================================================
def demo_set_theory():
    separator("2. 集合论 (Set Theory)")

    # --- 2.1 集合基本运算 ---
    print("【2.1】集合基本运算")
    A = FiniteSet(1, 2, 3, 4, 5)
    B = FiniteSet(3, 4, 5, 6, 7)
    C = FiniteSet(1, 2, 8)

    print(f"  A = {A}")
    print(f"  B = {B}")
    print(f"  A ∪ B = {A.union(B)}")
    print(f"  A ∩ B = {A.intersection(B)}")
    print(f"  A - B = {A - B}")
    print(f"  A △ B (对称差) = {A.symmetric_difference(B)}")

    # --- 2.2 子集与超集 ---
    print("\n【2.2】子集关系")
    S = FiniteSet(1, 2)
    print(f"  S = {S}")
    print(f"  S ⊆ A ? {S.is_subset(A)}")
    print(f"  B ⊆ A ? {B.is_subset(A)}")

    # --- 2.3 幂集 ---
    print("\n【2.3】幂集 P(S)")
    S = FiniteSet(1, 2, 3)
    P = S.powerset()
    print(f"  S = {S}")
    print(f"  |P(S)| = {len(P)}")
    print(f"  P(S) = {P}")

    # --- 2.4 笛卡尔积 ---
    print("\n【2.4】笛卡尔积")
    X = FiniteSet('a', 'b')
    Y = FiniteSet(1, 2, 3)
    product = X * Y
    print(f"  X = {X}, Y = {Y}")
    print(f"  X × Y = {product}")
    print(f"  |X × Y| = {len(product)}")

    # --- 2.5 区间运算 ---
    print("\n【2.5】区间运算")
    I1 = Interval(0, 5)
    I2 = Interval(3, 8)
    print(f"  I1 = {I1}")
    print(f"  I2 = {I2}")
    print(f"  I1 ∩ I2 = {I1.intersect(I2)}")
    print(f"  I1 ∪ I2 = {I1.union(I2)}")

    # --- 2.6 Python 集合高级操作 ---
    print("\n【2.6】Python原生集合操作")
    A_py = {1, 2, 3, 4, 5}
    B_py = {4, 5, 6, 7}
    C_py = {1, 2}
    print(f"  A | B  = {A_py | B_py}   (并集)")
    print(f"  A & B  = {A_py & B_py}   (交集)")
    print(f"  A - B  = {A_py - B_py}   (差集)")
    print(f"  A ^ B  = {A_py ^ B_py}   (对称差)")
    print(f"  C <= A = {C_py <= A_py}  (子集)")
    print(f"  frozenset可用于做字典键: {frozenset([1,2,3])}")

    # --- 2.7 集合划分 ---
    print("\n【2.7】集合划分 (Set Partitions)")
    from sympy.utilities.iterables import partitions
    elems = [1, 2, 3, 4]
    from sympy.utilities.iterables import multiset_partitions
    print(f"  {elems} 的所有划分:")
    for i, part in enumerate(multiset_partitions(elems)):
        print(f"    划分{i+1}: {part}")


# ============================================================
# 3. 组合数学 (Combinatorics)
# ============================================================
def demo_combinatorics():
    separator("3. 组合数学 (Combinatorics)")

    n, k = 10, 3

    # --- 3.1 排列与组合 ---
    print("【3.1】排列与组合")
    print(f"  C({n},{k}) = C(n,k) = {binomial(n, k)}")
    print(f"  P({n},{k}) = n!/(n-k)! = {factorial(n)//factorial(n-k)}")
    print(f"  {n}! = {factorial(n)}")

    from math import comb, perm
    print(f"  math.comb({n},{k}) = {comb(n, k)}")
    print(f"  math.perm({n},{k}) = {perm(n, k)}")

    # --- 3.2 可重复组合 ---
    print("\n【3.2】可重复组合 (Multiset Coefficient)")
    n_val, k_val = 5, 3
    result = binomial(n_val + k_val - 1, k_val)
    print(f"  从{n_val}种元素中取{k_val}个 (可重复)")
    print(f"  C(n+k-1, k) = C({n_val+k_val-1}, {k_val}) = {result}")

    # --- 3.3 排列枚举 ---
    print("\n【3.3】排列枚举")
    items = [1, 2, 3]
    perms = list(itertools.permutations(items))
    print(f"  {items} 的全排列 ({len(perms)}个):")
    for p in perms:
        print(f"    {p}")

    # --- 3.4 组合枚举 ---
    print("\n【3.4】组合枚举")
    combs = list(itertools.combinations(range(1, 6), 3))
    print(f"  C(5,3) = {len(combs)}个:")
    for c in combs:
        print(f"    {c}")

    # --- 3.5 可重复排列/组合 ---
    print("\n【3.5】可重复排列与组合")
    rep_combs = list(itertools.combinations_with_replacement([1, 2, 3], 2))
    print(f"  从[1,2,3]取2个 (可重复组合): {rep_combs}")
    rep_perms = list(itertools.product([1, 2], repeat=3))
    print(f"  [1,2]的3位可重复排列: {rep_perms}")

    # --- 3.6 鸽巢原理验证 ---
    print("\n【3.6】鸽巢原理验证")
    pigeons = 13
    holes = 12
    print(f"  {pigeons}只鸽子放入{holes}个笼子")
    print(f"  至少有一个笼子有 >= {math.ceil(pigeons/holes)} 只鸽子")

    # --- 3.7 容斥原理 ---
    print("\n【3.7】容斥原理 (Inclusion-Exclusion)")
    total = 100
    like_math = 40
    like_physics = 30
    like_both = 15
    like_either = like_math + like_physics - like_both
    like_neither = total - like_either
    print(f"  总人数: {total}")
    print(f"  喜欢数学: {like_math}, 喜欢物理: {like_physics}, 都喜欢: {like_both}")
    print(f"  至少喜欢一门: {like_either} (容斥原理)")
    print(f"  都不喜欢: {like_neither}")

    # --- 3.8 生成函数 ---
    print("\n【3.8】生成函数 (Generating Functions)")
    x = Symbol('x')
    gf = 1 / (1 - x)**4
    coeffs = [gf.series(x, 0, n+1).coeff(x, n) for n in range(8)]
    print(f"  1/(1-x)^4 的系数 (可重复组合): {coeffs}")
    print(f"  验证: C(n+3,3) = {[binomial(i+3,3) for i in range(8)]}")

    # --- 3.9 Catalan 数 ---
    print("\n【3.9】Catalan 数")
    for i in range(10):
        print(f"  C_{i} = {catalan(i)}")

    # --- 3.10 Fibonacci 数 ---
    print("\n【3.10】Fibonacci 数列")
    fibs = [fibonacci(i) for i in range(12)]
    print(f"  F(0..11) = {fibs}")

    # --- 3.11 第二类 Stirling 数 ---
    print("\n【3.11】第二类 Stirling 数 S(n,k)")
    from sympy.functions.combinatorial.numbers import stirling
    n_s, k_s = 5, 3
    print(f"  S({n_s},{k_s}) = {stirling(n_s, k_s, kind=2)}")
    print(f"  含义: 将{n_s}个不同元素分为{k_s}个非空子集的方法数")

    # --- 3.12 错排数 ---
    print("\n【3.12】错排数 (Derangement)")
    def derangement_num(n):
        if n == 0: return 1
        if n == 1: return 0
        return (n - 1) * (derangement_num(n-1) + derangement_num(n-2))
    for i in range(1, 8):
        print(f"  D({i}) = {derangement_num(i)}")


# ============================================================
# 4. 图论 (Graph Theory)
# ============================================================
def demo_graph_theory():
    separator("4. 图论 (Graph Theory)")

    # --- 4.1 创建图 ---
    print("【4.1】创建图 (NetworkX)")
    G = nx.Graph()
    G.add_edges_from([(1,2), (1,3), (2,3), (2,4), (3,5), (4,5)])
    print(f"  顶点数: {G.number_of_nodes()}")
    print(f"  边数: {G.number_of_edges()}")
    print(f"  顶点: {list(G.nodes())}")
    print(f"  边: {list(G.edges())}")

    # --- 4.2 度数 ---
    print("\n【4.2】度数 (Degree)")
    for node in sorted(G.nodes()):
        print(f"  deg({node}) = {G.degree(node)}")

    # --- 4.3 邻接矩阵 ---
    print("\n【4.3】邻接矩阵")
    adj = nx.adjacency_matrix(G, nodelist=sorted(G.nodes())).todense()
    print(f"  A = \n{np.array(adj)}")

    # --- 4.4 最短路径 ---
    print("\n【4.4】最短路径")
    path = nx.shortest_path(G, source=1, target=5)
    length = nx.shortest_path_length(G, source=1, target=5)
    print(f"  1→5 最短路径: {path}, 长度: {length}")

    all_pairs = dict(nx.all_pairs_shortest_path_length(G))
    print(f"  所有最短路径长度:")
    for src in sorted(all_pairs):
        for dst in sorted(all_pairs[src]):
            if src < dst:
                print(f"    {src}→{dst}: {all_pairs[src][dst]}")

    # --- 4.5 连通性 ---
    print("\n【4.5】连通性")
    print(f"  图是否连通: {nx.is_connected(G)}")
    components = list(nx.connected_components(G))
    print(f"  连通分量数: {len(components)}")

    # --- 4.6 欧拉路径/回路 ---
    print("\n【4.6】欧拉路径与回路")
    print(f"  有欧拉路径: {nx.has_eulerian_path(G)}")
    print(f"  有欧拉回路: {nx.is_eulerian(G)}")

    euler_G = nx.Graph([(1,2), (2,3), (3,1), (3,4), (4,5), (5,3)])
    print(f"  三角+回路图 欧拉回路: {nx.is_eulerian(euler_G)}")
    if nx.has_eulerian_path(euler_G):
        ep = list(nx.eulerian_path(euler_G))
        print(f"  欧拉路径: {ep}")

    # --- 4.7 哈密顿路径 (旅行商近似) ---
    print("\n【4.7】哈密顿路径近似 (TSP)")
    tsp_G = nx.complete_graph(5)
    import random
    random.seed(42)
    for u, v in tsp_G.edges():
        tsp_G[u][v]['weight'] = random.randint(1, 20)
    tsp_path = nx.approximation.traveling_salesman_problem(tsp_G, cycle=True)
    tsp_cost = sum(tsp_G[tsp_path[i]][tsp_path[i+1]]['weight'] for i in range(len(tsp_path)-1))
    print(f"  TSP近似解: {tsp_path}")
    print(f"  总代价: {tsp_cost}")

    # --- 4.8 最小生成树 ---
    print("\n【4.8】最小生成树")
    mst = nx.minimum_spanning_tree(G)
    print(f"  MST边: {list(mst.edges())}")
    print(f"  MST顶点数: {mst.number_of_nodes()}, 边数: {mst.number_of_edges()}")

    # --- 4.9 树的性质 ---
    print("\n【4.9】树")
    T = nx.balanced_tree(2, 3)
    print(f"  2叉平衡树(深度3): {T.number_of_nodes()}个节点")
    print(f"  是否为树: {nx.is_tree(T)}")
    print(f"  叶节点: {[n for n in T.nodes() if T.degree(n)==1]}")

    # --- 4.10 二部图 ---
    print("\n【4.10】二部图")
    B = nx.complete_bipartite_graph(3, 4)
    print(f"  K_3,4: 是否二部图 {nx.is_bipartite(B)}")
    coloring = nx.bipartite.color(B)
    sets = {0: [], 1: []}
    for node, color in coloring.items():
        sets[color].append(node)
    print(f"  左部: {sorted(sets[0])}")
    print(f"  右部: {sorted(sets[1])}")

    # --- 4.11 图的着色 ---
    print("\n【4.11】图着色")
    coloring = nx.coloring.greedy_color(G, strategy='largest_first')
    chromatic = max(coloring.values()) + 1 if coloring else 0
    print(f"  贪心着色: {coloring}")
    print(f"  色数 (上界): {chromatic}")

    # --- 4.12 同构检测 ---
    print("\n【4.12】图同构检测")
    G1 = nx.cycle_graph(5)
    G2 = nx.cycle_graph(5)
    G3 = nx.path_graph(5)
    print(f"  C5 同构 C5: {nx.is_isomorphic(G1, G2)}")
    print(f"  C5 同构 P5: {nx.is_isomorphic(G1, G3)}")

    # --- 4.13 igraph 高级分析 ---
    print("\n【4.13】igraph 高级图分析")
    ig_g = ig.Graph.Erdos_Renyi(n=20, p=0.2, directed=False)
    print(f"  随机图 G(20, 0.2): {ig_g.vcount()}顶点, {ig_g.ecount()}边")
    print(f"  平均度数: {np.mean(ig_g.degree()):.2f}")
    print(f"  直径: {ig_g.diameter()}")
    print(f"  聚类系数: {ig_g.transitivity_undirected():.4f}")
    communities = ig_g.community_multilevel()
    print(f"  社区数(Louvain): {len(communities)}")
    print(f"  模块度: {communities.modularity:.4f}")

    # --- 4.14 可视化 ---
    print("\n【4.14】图可视化")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    pos1 = nx.spring_layout(G, seed=42)
    nx.draw(G, pos1, ax=axes[0], with_labels=True, node_color='lightblue',
            node_size=500, font_size=12, font_weight='bold', edge_color='gray')
    axes[0].set_title("Undirected Graph G", fontsize=13)

    DG = nx.DiGraph([(1,2), (2,3), (3,1), (1,4), (4,5), (5,2)])
    pos2 = nx.spring_layout(DG, seed=42)
    nx.draw(DG, pos2, ax=axes[1], with_labels=True, node_color='lightgreen',
            node_size=500, font_size=12, font_weight='bold',
            edge_color='gray', arrows=True, arrowstyle='->', arrowsize=15)
    axes[1].set_title("Directed Graph", fontsize=13)

    pos3 = nx.spring_layout(B, seed=42)
    bipartite_coloring = nx.bipartite.color(B)
    colors = ['lightcoral' if bipartite_coloring[n]==0 else 'lightskyblue' for n in B.nodes()]
    nx.draw(B, pos3, ax=axes[2], with_labels=True, node_color=colors,
            node_size=500, font_size=12, font_weight='bold', edge_color='gray')
    axes[2].set_title("Complete Bipartite K(3,4)", fontsize=13)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "graph_examples.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("  图已保存至 output/graph_examples.png")


# ============================================================
# 5. 代数结构 (Algebraic Structures)
# ============================================================
def demo_algebra():
    separator("5. 代数结构 (Algebraic Structures)")

    # --- 5.1 群论：置换群 ---
    print("【5.1】置换与置换群")
    p1 = Permutation([1, 2, 0])
    p2 = Permutation([2, 0, 1])
    print(f"  σ = {p1} (1→2, 2→3, 0→1 即循环 (0 1 2))")
    print(f"  τ = {p2} (循环 (0 2 1))")
    print(f"  σ∘τ = {p1 * p2}")
    print(f"  σ的逆 = {~p1}")
    print(f"  σ的阶 = {p1.order()}")

    print("\n  对称群 S3:")
    S3 = PermutationGroup(Permutation(0,1,2), Permutation(0,1))
    print(f"  阶: {S3.order()}")
    print(f"  所有元素:")
    for elem in S3.elements:
        print(f"    {elem}")

    # --- 5.2 循环群 ---
    print("\n【5.2】循环群")
    from sympy.combinatorics.named_groups import CyclicGroup
    C5 = CyclicGroup(5)
    print(f"  C5 (5阶循环群):")
    print(f"  阶: {C5.order()}")
    print(f"  生成元: {C5.generators}")

    # --- 5.3 矩阵运算与线性代数 ---
    print("\n【5.3】矩阵运算")
    A = Matrix([[1, 2], [3, 4]])
    B_mat = Matrix([[5, 6], [7, 8]])
    print(f"  A = {A.tolist()}")
    print(f"  B = {B_mat.tolist()}")
    print(f"  A+B = {(A + B_mat).tolist()}")
    print(f"  A*B = {(A * B_mat).tolist()}")
    print(f"  det(A) = {det(A)}")
    print(f"  A^(-1) = {(A.inv()).tolist()}")
    print(f"  A^T = {(A.T).tolist()}")

    # --- 5.4 关系矩阵与复合 ---
    print("\n【5.4】二元关系矩阵")
    R1 = Matrix([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    R2 = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    R_comp = (R1 * R2).applyfunc(lambda x: 1 if x > 0 else 0)
    print(f"  R1 (置换关系):\n{np.array(R1.tolist())}")
    print(f"  R2 (恒等关系):\n{np.array(R2.tolist())}")
    print(f"  R1∘R2 (复合):\n{np.array(R_comp.tolist())}")

    # --- 5.5 等价关系验证 ---
    print("\n【5.5】等价关系验证")
    def is_reflexive(M):
        n = M.shape[0]
        return all(M[i, i] == 1 for i in range(n))

    def is_symmetric(M):
        arr = np.array(M.tolist())
        return np.array_equal(arr, arr.T)

    def is_transitive(M):
        arr = np.array(M.tolist(), dtype=int)
        comp = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                for k in range(arr.shape[0]):
                    comp[i][j] |= arr[i][k] & arr[k][j]
        return np.array_equal((arr | comp), arr)

    eq_rel = Matrix([[1,1,0],[1,1,0],[0,0,1]])
    print(f"  关系矩阵:\n{np.array(eq_rel.tolist())}")
    print(f"  自反: {is_reflexive(eq_rel)}")
    print(f"  对称: {is_symmetric(eq_rel)}")
    print(f"  传递: {is_transitive(eq_rel)}")
    print(f"  是等价关系: {is_reflexive(eq_rel) and is_symmetric(eq_rel) and is_transitive(eq_rel)}")

    # --- 5.6 偏序集 (Hasse图) ---
    print("\n【5.6】偏序集与Hasse图")
    divides = lambda a, b: b % a == 0
    elements = [1, 2, 3, 4, 6, 12]
    H = nx.DiGraph()
    for a in elements:
        for b in elements:
            if a < b and divides(a, b):
                if not any(a < c < b and divides(a,c) and divides(c,b) for c in elements):
                    H.add_edge(a, b)
    print(f"  整除偏序集 ({elements}) 的覆盖关系:")
    for edge in H.edges():
        print(f"    {edge[0]} | {edge[1]}")

    fig, ax = plt.subplots(figsize=(6, 5))
    pos = {n: (0, 0) for n in H.nodes()}
    levels = {1:0, 2:1, 3:1, 4:2, 6:2, 12:3}
    x_pos = {1:1.5, 2:0.5, 3:2.5, 4:0, 6:3, 12:1.5}
    for n in H.nodes():
        pos[n] = (x_pos[n], levels[n])
    nx.draw(H, pos, ax=ax, with_labels=True, node_color='lightyellow',
            node_size=600, font_size=14, font_weight='bold',
            arrows=False, edge_color='gray')
    ax.set_title("Hasse Diagram: Divisibility Poset (D12)", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "hasse_diagram.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Hasse图已保存至 output/hasse_diagram.png")


# ============================================================
# 6. 数论 (Number Theory)
# ============================================================
def demo_number_theory():
    separator("6. 数论 (Number Theory)")

    # --- 6.1 素数 ---
    print("【6.1】素数检测与生成")
    test_nums = [2, 7, 15, 17, 23, 97, 100]
    for n in test_nums:
        print(f"  {n}: {'素数' if isprime(n) else '合数'}")
    primes_100 = list(primerange(1, 101))
    print(f"  100以内素数: {primes_100}")
    print(f"  100以内素数个数: {len(primes_100)}")

    # --- 6.2 素因子分解 ---
    print("\n【6.2】素因子分解")
    numbers = [60, 84, 360, 1001, 7920]
    for n in numbers:
        print(f"  {n} = {factorint(n)}")

    # --- 6.3 GCD / LCM ---
    print("\n【6.3】最大公约数与最小公倍数")
    pairs = [(12, 18), (35, 49), (100, 75), (17, 23)]
    for a, b in pairs:
        print(f"  gcd({a},{b}) = {gcd(a,b)}, lcm({a},{b}) = {lcm(a,b)}")

    # --- 6.4 欧拉函数 ---
    print("\n【6.4】欧拉函数 φ(n)")
    for n in [1, 2, 6, 10, 12, 15, 20, 30]:
        print(f"  φ({n}) = {totient(n)}")

    # --- 6.5 模运算与模逆 ---
    print("\n【6.5】模运算")
    a_val = 7
    m_val = 11
    print(f"  {a_val} mod {m_val} = {a_val % m_val}")
    inv = mod_inverse(a_val, m_val)
    print(f"  {a_val}^(-1) mod {m_val} = {inv}")
    print(f"  验证: {a_val} * {inv} mod {m_val} = {(a_val * inv) % m_val}")

    # --- 6.6 中国剩余定理 ---
    print("\n【6.6】中国剩余定理")
    from sympy.ntheory.modular import solve_congruence, crt
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    result = crt(moduli, remainders)
    print(f"  x ≡ {remainders[0]} (mod {moduli[0]})")
    print(f"  x ≡ {remainders[1]} (mod {moduli[1]})")
    print(f"  x ≡ {remainders[2]} (mod {moduli[2]})")
    print(f"  解: x ≡ {result[0]} (mod {result[1]})")

    # --- 6.7 同余方程 ---
    print("\n【6.7】同余方程求解")
    x = Symbol('x')
    from sympy.ntheory.modular import solve_congruence as solve_cong
    sol = solve_cong((2, 3), (3, 5), (2, 7))
    print(f"  x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)")
    print(f"  解: {sol}")

    # --- 6.8 费马小定理验证 ---
    print("\n【6.8】费马小定理验证")
    for p in [5, 7, 11, 13]:
        a = 2
        print(f"  {a}^({p-1}) mod {p} = {pow(a, p-1, p)} (应为1)")

    # --- 6.9 RSA示例 ---
    print("\n【6.9】RSA加密示例 (教学用途)")
    p_rsa, q_rsa = 61, 53
    n_rsa = p_rsa * q_rsa
    phi_rsa = (p_rsa - 1) * (q_rsa - 1)
    e_rsa = 17
    d_rsa = mod_inverse(e_rsa, phi_rsa)
    print(f"  p={p_rsa}, q={q_rsa}, n={n_rsa}, φ(n)={phi_rsa}")
    print(f"  公钥: (e={e_rsa}, n={n_rsa})")
    print(f"  私钥: (d={d_rsa}, n={n_rsa})")
    msg = 42
    encrypted = pow(msg, e_rsa, n_rsa)
    decrypted = pow(encrypted, d_rsa, n_rsa)
    print(f"  明文: {msg}")
    print(f"  密文: {encrypted}")
    print(f"  解密: {decrypted}")

    # --- 6.10 离散对数 ---
    print("\n【6.10】离散对数")
    from sympy.ntheory import discrete_log
    base, target, modulus = 3, 13, 17
    dlog = discrete_log(modulus, target, base)
    print(f"  求 x 使得 {base}^x ≡ {target} (mod {modulus})")
    print(f"  x = {dlog}")
    print(f"  验证: {base}^{dlog} mod {modulus} = {pow(base, dlog, modulus)}")


# ============================================================
# 7. 离散优化 (Discrete Optimization)
# ============================================================
def demo_optimization():
    separator("7. 离散优化 (Discrete Optimization)")

    # --- 7.1 0-1背包问题 ---
    print("【7.1】0-1背包问题 (PuLP)")
    items = [('A', 2, 3), ('B', 3, 4), ('C', 4, 5), ('D', 5, 6)]
    capacity = 8
    print(f"  物品: (名称, 重量, 价值)")
    for name, w, v in items:
        print(f"    {name}: 重量={w}, 价值={v}")
    print(f"  背包容量: {capacity}")

    prob = LpProblem("Knapsack", LpMaximize)
    x_vars = [LpVariable(f"x_{name}", cat=LpBinary) for name, _, _ in items]
    prob += lpSum(v * x for (_, _, v), x in zip(items, x_vars))
    prob += lpSum(w * x for (_, w, _), x in zip(items, x_vars)) <= capacity
    prob.solve()

    print(f"  状态: {LpStatus[prob.status]}")
    print(f"  最优解:")
    total_w = 0
    for (name, w, v), x in zip(items, x_vars):
        if value(x) == 1:
            print(f"    选择 {name} (重量={w}, 价值={v})")
            total_w += w
    print(f"  总价值: {value(prob.objective)}, 总重量: {total_w}")

    # --- 7.2 整数线性规划 ---
    print("\n【7.2】整数线性规划")
    prob2 = LpProblem("ILP_Example", LpMaximize)
    x1 = LpVariable("x1", lowBound=0, cat=LpInteger)
    x2 = LpVariable("x2", lowBound=0, cat=LpInteger)
    prob2 += 5*x1 + 4*x2
    prob2 += 6*x1 + 4*x2 <= 24
    prob2 += x1 + 2*x2 <= 6
    prob2.solve()
    print(f"  max 5x1 + 4x2")
    print(f"  s.t. 6x1+4x2≤24, x1+2x2≤6, x1,x2≥0 (整数)")
    print(f"  最优: x1={value(x1)}, x2={value(x2)}, 目标={value(prob2.objective)}")

    # --- 7.3 指派问题 ---
    print("\n【7.3】指派问题")
    cost_matrix = np.array([
        [9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4],
    ])
    from scipy.optimize import linear_sum_assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    print(f"  代价矩阵:\n{cost_matrix}")
    print(f"  最优指派:")
    total_cost = 0
    for r, c in zip(row_ind, col_ind):
        print(f"    工人{r} → 任务{c} (代价={cost_matrix[r,c]})")
        total_cost += cost_matrix[r, c]
    print(f"  最小总代价: {total_cost}")


# ============================================================
# 8. 递推关系与生成函数
# ============================================================
def demo_recurrence():
    separator("8. 递推关系与生成函数")

    # --- 8.1 求解递推关系 ---
    print("【8.1】求解线性递推关系 (sympy rsolve)")
    from sympy import Function, Eq, rsolve
    n = Symbol('n', integer=True)
    y = Function('y')

    fibo_eq = Eq(y(n), y(n-1) + y(n-2))
    fibo_sol = rsolve(fibo_eq, y(n), {y(0): 0, y(1): 1})
    print(f"  Fibonacci递推: y(n) = y(n-1) + y(n-2)")
    print(f"  通项公式: y(n) = {fibo_sol}")
    print(f"  验证:", [simplify(fibo_sol.subs(n, i)) for i in range(8)])

    # --- 8.2 汉诺塔递推 ---
    print("\n【8.2】汉诺塔递推")
    hanoi_eq = Eq(y(n), 2*y(n-1) + 1)
    hanoi_sol = rsolve(hanoi_eq, y(n), {y(0): 0})
    print(f"  T(n) = 2T(n-1) + 1")
    print(f"  通项: T(n) = {hanoi_sol}")
    print(f"  化简: T(n) = {simplify(hanoi_sol)}")
    print(f"  验证: {[simplify(hanoi_sol.subs(n, i)) for i in range(6)]}")

    # --- 8.3 生成函数 ---
    print("\n【8.3】生成函数应用")
    x = Symbol('x')
    gf_fib = x / (1 - x - x**2)
    print(f"  Fibonacci生成函数: {gf_fib}")
    fib_coeffs = [gf_fib.series(x, 0, i+1).coeff(x, i) for i in range(10)]
    print(f"  系数 (Fibonacci数): {fib_coeffs}")

    # --- 8.4 递推求解一般形式 ---
    print("\n【8.4】一般线性递推")
    gen_eq = Eq(y(n), 3*y(n-1) - 2*y(n-2))
    gen_sol = rsolve(gen_eq, y(n), {y(0): 1, y(1): 3})
    print(f"  y(n) = 3y(n-1) - 2y(n-2), y(0)=1, y(1)=3")
    print(f"  通项: {gen_sol}")
    print(f"  化简: {simplify(gen_sol)}")
    print(f"  验证: {[simplify(gen_sol.subs(n, i)) for i in range(6)]}")


# ============================================================
# 9. 编码理论
# ============================================================
def demo_coding():
    separator("9. 编码理论 (Coding Theory)")

    # --- 9.1 汉明码 ---
    print("【9.1】汉明距离")
    def hamming_distance(s1, s2):
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))

    codewords = ['0000', '0011', '1100', '1111']
    print(f"  码字: {codewords}")
    print(f"  汉明距离矩阵:")
    print(f"  {'':>8}", end='')
    for cw in codewords:
        print(f"  {cw:>6}", end='')
    print()
    for i, c1 in enumerate(codewords):
        print(f"  {c1:>8}", end='')
        for j, c2 in enumerate(codewords):
            print(f"  {hamming_distance(c1, c2):>6}", end='')
        print()
    min_dist = min(hamming_distance(codewords[i], codewords[j])
                   for i in range(len(codewords))
                   for j in range(i+1, len(codewords)))
    print(f"  最小汉明距离: {min_dist}")
    print(f"  检错能力: {min_dist - 1}位")
    print(f"  纠错能力: {(min_dist - 1) // 2}位")

    # --- 9.2 奇偶校验 ---
    print("\n【9.2】奇偶校验码")
    data = '10110'
    parity = str(data.count('1') % 2)
    codeword = data + parity
    print(f"  数据: {data}")
    print(f"  偶校验位: {parity}")
    print(f"  编码后: {codeword}")

    # --- 9.3 汉明码 (7,4) ---
    print("\n【9.3】汉明(7,4)码编码")
    G_matrix = np.array([
        [1,0,0,0,1,1,0],
        [0,1,0,0,1,0,1],
        [0,0,1,0,0,1,1],
        [0,0,0,1,1,1,1],
    ])
    data_vec = np.array([1, 0, 1, 1])
    encoded = data_vec @ G_matrix % 2
    print(f"  数据: {data_vec}")
    print(f"  生成矩阵 G:\n{G_matrix}")
    print(f"  编码: {encoded}")

    H_matrix = np.array([
        [1,1,0,1,1,0,0],
        [1,0,1,1,0,1,0],
        [0,1,1,1,0,0,1],
    ])
    syndrome = H_matrix @ encoded % 2
    print(f"  校验矩阵 H:\n{H_matrix}")
    print(f"  伴随式: {syndrome} (全0表示无错)")


# ============================================================
# 10. 自动机与形式语言
# ============================================================
def demo_automata():
    separator("10. 自动机与形式语言 (基础)")

    # --- 10.1 正则表达式 ---
    print("【10.1】正则表达式匹配")
    import re
    patterns = {
        r'^[01]+$': '二进制串',
        r'^[a-z]+@[a-z]+\.[a-z]{2,3}$': '简单邮箱',
        r'^\d{3}-\d{4}$': '电话格式 xxx-xxxx',
        r'^(0|1(01*0)*1)*$': '偶数个1的二进制串',
    }
    test_cases = [
        ('10110', r'^[01]+$'),
        ('10210', r'^[01]+$'),
        ('test@com.cn', r'^[a-z]+@[a-z]+\.[a-z]{2,3}$'),
        ('123-4567', r'^\d{3}-\d{4}$'),
    ]
    for text, pat in test_cases:
        match = bool(re.match(pat, text))
        print(f"  '{text}' 匹配 '{pat}': {match}")

    # --- 10.2 DFA模拟 ---
    print("\n【10.2】DFA模拟: 识别包含'01'子串的二进制串")
    states = {'q0', 'q1', 'q2'}
    alphabet = {'0', '1'}
    transitions = {
        ('q0', '0'): 'q1',
        ('q0', '1'): 'q0',
        ('q1', '0'): 'q1',
        ('q1', '1'): 'q2',
        ('q2', '0'): 'q2',
        ('q2', '1'): 'q2',
    }
    start = 'q0'
    accept = {'q2'}

    def run_dfa(input_str):
        current = start
        for ch in input_str:
            current = transitions.get((current, ch), current)
        return current in accept

    test_strs = ['010', '111', '0011', '10', '0', '0101']
    for s in test_strs:
        result = run_dfa(s)
        print(f"  '{s}' → {'接受' if result else '拒绝'}")

    # --- 10.3 上下文无关文法 ---
    print("\n【10.3】上下文无关文法 (CFG) 示例")
    print("  S → aSb | ε")
    print("  生成语言: {a^n b^n | n ≥ 0}")
    def generate_anbn(n):
        return 'a' * n + 'b' * n
    for i in range(5):
        print(f"    n={i}: '{generate_anbn(i)}'")

    # --- 10.4 文法推导 ---
    print("\n【10.4】简单表达式文法推导")
    print("  E → E + T | T")
    print("  T → T * F | F")
    print("  F → (E) | id")
    print("  推导 'id + id * id':")
    print("    E → E + T → T + T → F + T → id + T")
    print("    → id + T * F → id + F * F → id + id * F → id + id * id")


# ============================================================
# 11. 概率与离散概率
# ============================================================
def demo_probability():
    separator("11. 离散概率 (Discrete Probability)")

    from math import comb

    # --- 11.1 古典概型 ---
    print("【11.1】古典概型")
    total = comb(52, 5)
    royal_flush = 4
    print(f"  5张牌组合数: {total}")
    print(f"  同花顺: {royal_flush}/{total} = {royal_flush/total:.2e}")
    four_kind = 13 * 48
    print(f"  四条: {four_kind}/{total} = {four_kind/total:.2e}")

    # --- 11.2 条件概率 ---
    print("\n【11.2】条件概率 (贝叶斯定理)")
    p_disease = 0.001
    p_pos_given_disease = 0.99
    p_pos_given_healthy = 0.05
    p_pos = p_pos_given_disease * p_disease + p_pos_given_healthy * (1 - p_disease)
    p_disease_given_pos = (p_pos_given_disease * p_disease) / p_pos
    print(f"  P(病)=0.001, P(+|病)=0.99, P(+|健康)=0.05")
    print(f"  P(病|+) = {p_disease_given_pos:.4f} ({p_disease_given_pos*100:.2f}%)")

    # --- 11.3 二项分布 ---
    print("\n【11.3】二项分布")
    from scipy.stats import binom
    n_trials, p_success = 10, 0.3
    print(f"  B({n_trials}, {p_success}):")
    for k in range(n_trials + 1):
        prob = binom.pmf(k, n_trials, p_success)
        bar = '█' * int(prob * 80)
        print(f"    P(X={k:2d}) = {prob:.4f} {bar}")

    # --- 11.4 期望与方差 ---
    print("\n【11.4】随机变量期望与方差")
    outcomes = {1: 0.2, 2: 0.3, 3: 0.1, 4: 0.15, 5: 0.25}
    expected = sum(x * p for x, p in outcomes.items())
    variance = sum((x - expected)**2 * p for x, p in outcomes.items())
    print(f"  分布: {outcomes}")
    print(f"  E[X] = {expected:.2f}")
    print(f"  Var[X] = {variance:.4f}")
    print(f"  σ = {variance**0.5:.4f}")


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          离散数学工具箱 - 典型示例集合                              ║")
    print("║          Discrete Mathematics Toolkit - Examples                    ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_logic()
    demo_set_theory()
    demo_combinatorics()
    demo_graph_theory()
    demo_algebra()
    demo_number_theory()
    demo_optimization()
    demo_recurrence()
    demo_coding()
    demo_automata()
    demo_probability()

    print("\n" + "="*70)
    print("  所有示例执行完毕！")
    print("  输出图片保存在 output/ 目录下")
    print("="*70)
