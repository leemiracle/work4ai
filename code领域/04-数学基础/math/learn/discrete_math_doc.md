# 离散数学工具箱 - 完整使用文档

## 目录

1. [环境概览与安装](#1-环境概览与安装)
2. [数理逻辑 (Mathematical Logic)](#2-数理逻辑-mathematical-logic)
3. [集合论 (Set Theory)](#3-集合论-set-theory)
4. [组合数学 (Combinatorics)](#4-组合数学-combinatorics)
5. [图论 (Graph Theory)](#5-图论-graph-theory)
6. [代数结构 (Algebraic Structures)](#6-代数结构-algebraic-structures)
7. [数论 (Number Theory)](#7-数论-number-theory)
8. [离散优化 (Discrete Optimization)](#8-离散优化-discrete-optimization)
9. [递推关系与生成函数](#9-递推关系与生成函数)
10. [编码理论 (Coding Theory)](#10-编码理论-coding-theory)
11. [自动机与形式语言](#11-自动机与形式语言)
12. [离散概率 (Discrete Probability)](#12-离散概率-discrete-probability)
13. [进阶工具: Z3/automata-lib/pyformlang](#13-进阶工具-z3automata-libpyformlang)
14. [速查表 (Quick Reference)](#14-速查表-quick-reference)

---

## 1. 环境概览与安装

### 1.1 已安装工具一览

| 库 | 版本 | 用途 |
|---|---|---|
| **sympy** | 1.13.3 | 符号计算、逻辑、集合论、数论、组合数学、代数 |
| **networkx** | 3.4.1 | 图论（创建、分析、算法、可视化） |
| **python-igraph** | 1.0.0 | 高级图分析（社区检测、聚类系数） |
| **numpy** | 1.26.4 | 数值计算、矩阵运算 |
| **scipy** | 1.15.1 | 科学计算（组合数、指派问题、概率分布） |
| **matplotlib** | 3.5.1 | 可视化（图、树、Hasse图） |
| **pyeda** | 0.29.0 | 布尔代数、逻辑函数化简（Espresso算法） |
| **pulp** | 3.3.1 | 离散优化（0-1规划、整数规划） |
| **pydot** | 4.0.1 | Graphviz 图可视化 |
| **graphviz** (系统) | 2.43.0 | 图形渲染引擎 |
| **more-itertools** | 10.5.0 | 高级迭代工具 |
| **z3-solver** | 4.16.0 | SMT/SAT求解器 (数独、N皇后、约束求解) |
| **automata-lib** | 9.2.0 | 自动机理论 (DFA/NFA/PDA/TM) |
| **pyformlang** | 1.0.11 | 形式语言 (正则表达式↔DFA、CFG) |

### 1.2 安装命令

```bash
# 核心库（通常已预装）
pip install sympy networkx numpy scipy matplotlib

# 离散数学专用
pip install pyeda python-igraph pydot pulp more-itertools

# 进阶工具（强烈推荐）
pip install z3-solver automata-lib pyformlang

# 系统工具（可选，用于图渲染）
sudo apt install graphviz
```

### 1.3 运行示例

```bash
python3 discrete_math_examples.py
```

输出图片保存在 `output/` 目录下。

---

## 2. 数理逻辑 (Mathematical Logic)

### 2.1 工具选择

| 功能 | 推荐工具 |
|---|---|
| 命题逻辑运算 | `sympy.logic` |
| 真值表 | `sympy.logic.boolalg.truth_table` |
| SAT求解 | `sympy.logic.boolalg.satisfiable` |
| 范式转换 (CNF/DNF) | `sympy.logic.boolalg.to_cnf` / `to_dnf` |
| 主范式 (SOP/POS) | `sympy.logic.SOPform` / `POSform` |
| 布尔函数化简 | `pyeda` (Espresso算法) |

### 2.2 命题逻辑基本运算

```python
from sympy import symbols, And, Or, Not, Implies, Equivalent, Xor, Nand, Nor

p, q, r = symbols('p q r')

# 基本运算
expr_and = And(p, q)          # 合取: p & q
expr_or = Or(p, q)            # 析取: p | q
expr_not = Not(p)             # 否定: ~p
expr_implies = Implies(p, q)  # 蕴含: p → q
expr_equiv = Equivalent(p, q) # 等价: p ↔ q
expr_xor = Xor(p, q)          # 异或: p ⊕ q
expr_nand = Nand(p, q)        # 与非: ↑
expr_nor = Nor(p, q)          # 或非: ↓
```

### 2.3 真值表

```python
from sympy import symbols, Implies, And
from sympy.logic.boolalg import truth_table

p, q, r = symbols('p q r')
expr = Implies(And(p, q), r)  # (p ∧ q) → r

for inputs, result in truth_table(expr, [p, q, r]):
    print(f"{inputs} -> {result}")
```

**输出:**
```
[0, 0, 0] -> True
[0, 0, 1] -> True
[0, 1, 0] -> True
[0, 1, 1] -> True
[1, 0, 0] -> True
[1, 0, 1] -> True
[1, 1, 0] -> False   # 仅此行使公式为假
[1, 1, 1] -> True
```

### 2.4 可满足性检验 (SAT)

```python
from sympy import symbols, And, Or, Not, Implies, satisfiable

p, q, r = symbols('p q r')
formula = And(Implies(p, q), Or(Not(q), r), p)

result = satisfiable(formula)
# 输出: {p: True, q: True, r: True}
# 如果不可满足，返回 False
```

### 2.5 范式转换

```python
from sympy import symbols, Xor, to_cnf, to_dnf
from sympy.logic import SOPform, POSform

p, q = symbols('p q')
formula = Xor(p, q)

# 合取范式 (CNF)
cnf = to_cnf(formula)
# (p | q) & (~p | ~q)

# 析取范式 (DNF)
dnf = to_dnf(formula)
# (p & ~q) | (~p & q)

# 主析取范式 (SOP) — 指定最小项
sop = SOPform([p, q], [[0,1], [1,0]])  # m1 + m2

# 主合取范式 (POS) — 指定最大项
pos = POSform([p, q], [[0,1], [1,0]])  # M0 * M3
```

### 2.6 pyeda 布尔函数化简 (Espresso算法)

```python
from pyeda.inter import exprvar, expr2truthtable

a, b, c = map(exprvar, 'abc')

# 多数函数: 输出1当且仅当至少2个输入为1
f = a & b | a & c | b & c
simplified = f.simplify()

# 查看真值表
tt = expr2truthtable(f)
print(tt)
```

### 2.7 推理规则验证

```python
from sympy import symbols, And, Not, Implies, satisfiable

p, q = symbols('p q')

# 验证假言推理 (Modus Ponens): (p→q) ∧ p ⊢ q
premise1 = Implies(p, q)
premise2 = p
conclusion = q

# 如果前提 ∧ ¬结论 不可满足，则推理有效
combined = And(premise1, premise2)
is_valid = satisfiable(And(combined, Not(conclusion))) is False
# True: 推理有效
```

---

## 3. 集合论 (Set Theory)

### 3.1 工具选择

| 功能 | 推荐工具 |
|---|---|
| 有限集运算 | `sympy.sets.FiniteSet` |
| 区间运算 | `sympy.sets.Interval` |
| 幂集 | `FiniteSet.powerset()` |
| 笛卡尔积 | `ProductSet` / `*` 运算符 |
| 快速集合操作 | Python 内置 `set` / `frozenset` |
| 集合划分 | `sympy.utilities.iterables.multiset_partitions` |

### 3.2 集合基本运算

```python
from sympy import FiniteSet

A = FiniteSet(1, 2, 3, 4, 5)
B = FiniteSet(3, 4, 5, 6, 7)

A.union(B)                    # 并集: {1,2,3,4,5,6,7}
A.intersection(B)             # 交集: {3,4,5}
A - B                         # 差集: {1,2}
A.symmetric_difference(B)    # 对称差: {1,2,6,7}
```

### 3.3 子集与幂集

```python
from sympy import FiniteSet

S = FiniteSet(1, 2, 3)

# 子集检测
T = FiniteSet(1, 2)
T.is_subset(S)  # True

# 幂集 P(S)
P = S.powerset()
# FiniteSet(∅, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3})
# |P(S)| = 2^|S| = 8
```

### 3.4 笛卡尔积

```python
from sympy import FiniteSet

X = FiniteSet('a', 'b')
Y = FiniteSet(1, 2, 3)
product = X * Y  # 或 ProductSet(X, Y)
# |X × Y| = |X| × |Y| = 6
```

### 3.5 Python 原生集合操作

```python
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7}

A | B    # 并集
A & B    # 交集
A - B    # 差集
A ^ B    # 对称差
A <= B   # 子集检测
A < B    # 真子集

# frozenset: 不可变集合，可用作字典键
fs = frozenset([1, 2, 3])
```

### 3.6 集合划分

```python
from sympy.utilities.iterables import multiset_partitions

for part in multiset_partitions([1, 2, 3]):
    print(part)
# [[1, 2, 3]]
# [[1], [2, 3]]
# [[1, 2], [3]]
# [[1], [2], [3]]
```

---

## 4. 组合数学 (Combinatorics)

### 4.1 工具选择

| 功能 | 推荐工具 |
|---|---|
| 组合数 C(n,k) | `sympy.binomial` / `math.comb` |
| 排列数 P(n,k) | `math.perm` |
| 阶乘 n! | `sympy.factorial` / `math.factorial` |
| 排列枚举 | `itertools.permutations` |
| 组合枚举 | `itertools.combinations` |
| 可重复组合 | `itertools.combinations_with_replacement` |
| 可重复排列 | `itertools.product` |
| Catalan 数 | `sympy.catalan` |
| Fibonacci 数 | `sympy.fibonacci` |
| Stirling 数 | `sympy.functions.combinatorial.numbers.stirling` |
| 生成函数 | `sympy.series` |

### 4.2 排列与组合计数

```python
from sympy import binomial, factorial
from math import comb, perm

# 组合数 C(n,k) = n! / (k!(n-k)!)
C = binomial(10, 3)   # 120
C = comb(10, 3)       # 120 (math模块)

# 排列数 P(n,k) = n! / (n-k)!
P = perm(10, 3)       # 720

# 阶乘
f = factorial(10)     # 3628800
```

### 4.3 排列/组合枚举

```python
import itertools

# 全排列
list(itertools.permutations([1, 2, 3]))
# [(1,2,3), (1,3,2), (2,1,3), (2,3,1), (3,1,2), (3,2,1)]

# 组合 C(5,3)
list(itertools.combinations(range(1, 6), 3))

# 可重复组合 C(n+k-1, k)
list(itertools.combinations_with_replacement([1, 2, 3], 2))
# [(1,1), (1,2), (1,3), (2,2), (2,3), (3,3)]

# 可重复排列 n^k
list(itertools.product([0, 1], repeat=3))
# 8个二元组
```

### 4.4 特殊数列

```python
from sympy import catalan, fibonacci
from sympy.functions.combinatorial.numbers import stirling

# Catalan 数: C_n = C(2n,n)/(n+1)
for i in range(10):
    print(f"C_{i} = {catalan(i)}")
# 1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862

# Fibonacci 数
[fibonacci(i) for i in range(12)]
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# 第二类 Stirling 数 S(n,k): 将n个不同元素分为k个非空子集的方法数
stirling(5, 3, kind=2)  # 25

# 错排数 D(n)
def derangement(n):
    if n == 0: return 1
    if n == 1: return 0
    return (n - 1) * (derangement(n-1) + derangement(n-2))
```

### 4.5 生成函数

```python
from sympy import Symbol, binomial

x = Symbol('x')

# Fibonacci 生成函数: x / (1 - x - x^2)
gf = x / (1 - x - x**2)

# 提取第n项系数 = 第n个Fibonacci数
coeffs = [gf.series(x, 0, i+1).coeff(x, i) for i in range(10)]
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 4.6 容斥原理

```python
# |A∪B| = |A| + |B| - |A∩B|
# |A∪B∪C| = |A|+|B|+|C| - |A∩B|-|A∩C|-|B∩C| + |A∩B∩C|

def inclusion_exclusion(sets):
    """容斥原理计算并集大小"""
    from itertools import combinations
    n = len(sets)
    total = 0
    for k in range(1, n + 1):
        for combo in combinations(sets, k):
            intersection = set(combo[0])
            for s in combo[1:]:
                intersection &= s
            total += (-1)**(k+1) * len(intersection)
    return total
```

---

## 5. 图论 (Graph Theory)

### 5.1 工具选择

| 功能 | 推荐工具 |
|---|---|
| 图创建/基本操作 | `networkx` |
| 高级图分析/社区检测 | `igraph` |
| 图可视化 | `networkx` + `matplotlib` |
| 图渲染 (Graphviz) | `pydot` |
| 邻接矩阵 | `networkx` + `numpy` |

### 5.2 创建图

```python
import networkx as nx

# 无向图
G = nx.Graph()
G.add_edges_from([(1,2), (1,3), (2,3), (2,4), (3,5), (4,5)])

# 有向图
DG = nx.DiGraph([(1,2), (2,3), (3,1)])

# 带权图
WG = nx.Graph()
WG.add_weighted_edges_from([(1,2,3.5), (2,3,1.2)])

# 常见图
K5 = nx.complete_graph(5)          # 完全图 K5
C5 = nx.cycle_graph(5)             # 环图 C5
P5 = nx.path_graph(5)              # 路径图 P5
K33 = nx.complete_bipartite_graph(3,3)  # 完全二部图 K3,3
T = nx.balanced_tree(2, 3)         # 平衡2叉树(深度3)
```

### 5.3 图的基本属性

```python
G.number_of_nodes()    # 顶点数
G.number_of_edges()    # 边数
G.degree(node)         # 度数
list(G.neighbors(1))   # 邻居节点
nx.is_connected(G)     # 连通性
list(nx.connected_components(G))  # 连通分量
```

### 5.4 邻接矩阵

```python
import numpy as np
import networkx as nx

G = nx.Graph([(1,2), (1,3), (2,3)])
adj = nx.adjacency_matrix(G, nodelist=sorted(G.nodes())).todense()
print(np.array(adj))
```

### 5.5 最短路径

```python
# 单源最短路径
path = nx.shortest_path(G, source=1, target=5)
length = nx.shortest_path_length(G, source=1, target=5)

# 所有节点对最短路径
all_pairs = dict(nx.all_pairs_shortest_path_length(G))

# Dijkstra (带权图)
path = nx.dijkstra_path(WG, source=1, target=3)
```

### 5.6 欧拉与哈密顿

```python
# 欧拉路径/回路
nx.is_eulerian(G)           # 是否有欧拉回路
nx.has_eulerian_path(G)     # 是否有欧拉路径
list(nx.eulerian_circuit(G)) # 欧拉回路

# 哈密顿/旅行商 (近似)
from networkx.algorithms import approximation
path = approximation.traveling_salesman_problem(G)
```

### 5.7 最小生成树

```python
mst = nx.minimum_spanning_tree(G)
# Prim/Kruskal算法自动选择
```

### 5.8 二部图与图着色

```python
# 二部图检测
nx.is_bipartite(G)
coloring = nx.bipartite.color(G)  # 二分着色

# 图着色 (贪心)
coloring = nx.coloring.greedy_color(G, strategy='largest_first')
chromatic = max(coloring.values()) + 1  # 色数上界
```

### 5.9 图同构

```python
nx.is_isomorphic(G1, G2)  # 同构检测
```

### 5.10 igraph 高级分析

```python
import igraph as ig

# 创建随机图 (Erdos-Renyi)
g = ig.Graph.Erdos_Renyi(n=20, p=0.2)

g.diameter()                    # 直径
g.transitivity_undirected()     # 聚类系数
g.community_multilevel()        # Louvain社区检测
g.community_multilevel().modularity  # 模块度
```

### 5.11 图可视化

```python
import matplotlib.pyplot as plt
import networkx as nx

fig, ax = plt.subplots(figsize=(8, 6))
pos = nx.spring_layout(G, seed=42)  # 布局算法
nx.draw(G, pos, ax=ax, with_labels=True,
        node_color='lightblue', node_size=500,
        font_size=12, edge_color='gray')
plt.savefig("graph.png", dpi=150, bbox_inches='tight')
```

---

## 6. 代数结构 (Algebraic Structures)

### 6.1 置换与置换群

```python
from sympy.combinatorics import Permutation, PermutationGroup, Cycle
from sympy.combinatorics.named_groups import CyclicGroup, SymmetricGroup

# 创建置换
p = Permutation([1, 2, 0])   # 0→1, 1→2, 2→0 即 (0 1 2)

# 置换运算
q = Permutation([2, 0, 1])
r = p * q        # 复合
inv_p = ~p       # 逆
order = p.order() # 阶

# 置换群
S3 = SymmetricGroup(3)       # 对称群 S3
S3.order()                    # 6
list(S3.elements)             # 所有元素

C5 = CyclicGroup(5)          # 循环群 C5
```

### 6.2 矩阵运算

```python
from sympy import Matrix, det

A = Matrix([[1, 2], [3, 4]])

A + B           # 加法
A * B           # 乘法
det(A)          # 行列式: -2
A.inv()         # 逆矩阵
A.T             # 转置
A.rank()        # 秩
A.eigenvals()   # 特征值
```

### 6.3 二元关系

```python
from sympy import Matrix

# 关系矩阵
R = Matrix([[1,1,0],[1,1,0],[0,0,1]])

# 自反性: 对角线全为1
def is_reflexive(M):
    return all(M[i,i] == 1 for i in range(M.shape[0]))

# 对称性: M = M^T
def is_symmetric(M):
    arr = [list(row) for row in M.tolist()]
    return arr == [list(col) for col in zip(*arr)]

# 传递性: M^2 ⊆ M
def is_transitive(M):
    arr = __import__('numpy').array(M.tolist(), dtype=int)
    comp = (arr @ arr > 0).astype(int)
    return ((comp - arr) <= 0).all()

# 等价关系 = 自反 ∧ 对称 ∧ 传递
```

### 6.4 偏序集与 Hasse 图

```python
import networkx as nx
import matplotlib.pyplot as plt

elements = [1, 2, 3, 4, 6, 12]
H = nx.DiGraph()

# 构建覆盖关系 (去除传递边)
for a in elements:
    for b in elements:
        if a < b and b % a == 0:  # 整除关系
            if not any(a < c < b and c % a == 0 and b % c == 0
                       for c in elements):
                H.add_edge(a, b)

# 绘制 Hasse 图
pos = {n: (x_pos[n], level[n]) for n in H.nodes()}
nx.draw(H, pos, with_labels=True, arrows=False)
plt.savefig("hasse.png")
```

---

## 7. 数论 (Number Theory)

### 7.1 工具选择

| 功能 | 函数 |
|---|---|
| 素数检测 | `sympy.isprime(n)` |
| 素数范围 | `sympy.primerange(a, b)` |
| 素因子分解 | `sympy.factorint(n)` |
| GCD / LCM | `sympy.gcd(a,b)` / `sympy.lcm(a,b)` |
| 欧拉函数 | `sympy.totient(n)` |
| 模逆 | `sympy.mod_inverse(a, m)` |
| 中国剩余定理 | `sympy.ntheory.modular.crt()` |
| 离散对数 | `sympy.ntheory.discrete_log()` |

### 7.2 素数

```python
from sympy import isprime, primerange, factorint, nextprime

isprime(97)           # True
list(primerange(1, 30))  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
factorint(360)        # {2: 3, 3: 2, 5: 1}
nextprime(100)        # 101
```

### 7.3 GCD / LCM / 模运算

```python
from sympy import gcd, lcm, mod_inverse

gcd(12, 18)           # 6
lcm(12, 18)           # 36
mod_inverse(7, 11)    # 8 (因为 7*8 ≡ 1 mod 11)
```

### 7.4 欧拉函数

```python
from sympy import totient

totient(12)   # 4 (与12互素的数: 1,5,7,11)
totient(30)   # 8
```

### 7.5 中国剩余定理

```python
from sympy.ntheory.modular import crt

# 求 x 使得:
# x ≡ 2 (mod 3)
# x ≡ 3 (mod 5)
# x ≡ 2 (mod 7)
result, modulus = crt([3, 5, 7], [2, 3, 2])
# result=23, modulus=105
# 即 x ≡ 23 (mod 105)
```

### 7.6 RSA 加密示例

```python
from sympy import nextprime, mod_inverse

# 密钥生成
p, q = 61, 53
n = p * q                    # 3233
phi = (p-1) * (q-1)          # 3120
e = 17
d = mod_inverse(e, phi)      # 2753

# 加密: c = m^e mod n
msg = 42
cipher = pow(msg, e, n)      # 2557

# 解密: m = c^d mod n
plain = pow(cipher, d, n)    # 42
```

### 7.7 离散对数

```python
from sympy.ntheory import discrete_log

# 求 x 使 3^x ≡ 13 (mod 17)
x = discrete_log(17, 13, 3)  # 4
# 验证: 3^4 = 81 ≡ 13 (mod 17) ✓
```

---

## 8. 离散优化 (Discrete Optimization)

### 8.1 工具选择

| 功能 | 工具 |
|---|---|
| 0-1 整数规划 | `pulp` |
| 整数线性规划 | `pulp` |
| 指派问题 | `scipy.optimize.linear_sum_assignment` |
| TSP近似 | `networkx.algorithms.approximation` |

### 8.2 0-1 背包问题 (PuLP)

```python
from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, LpStatus, value

items = [('A', 2, 3), ('B', 3, 4), ('C', 4, 5), ('D', 5, 6)]
capacity = 8

prob = LpProblem("Knapsack", LpMaximize)
x = [LpVariable(f"x_{name}", cat=LpBinary) for name, _, _ in items]

# 目标: 最大化总价值
prob += lpSum(v * xi for (_, _, v), xi in zip(items, x))

# 约束: 总重量不超过容量
prob += lpSum(w * xi for (_, w, _), xi in zip(items, x)) <= capacity

prob.solve()
print(LpStatus[prob.status])  # "Optimal"
for (name, w, v), xi in zip(items, x):
    if value(xi) == 1:
        print(f"选择 {name}")
print(f"总价值: {value(prob.objective)}")
```

### 8.3 整数线性规划

```python
from pulp import LpProblem, LpMaximize, LpVariable, LpInteger, lpSum, value

prob = LpProblem("ILP", LpMaximize)
x1 = LpVariable("x1", lowBound=0, cat=LpInteger)
x2 = LpVariable("x2", lowBound=0, cat=LpInteger)

prob += 5*x1 + 4*x2             # max 5x1 + 4x2
prob += 6*x1 + 4*x2 <= 24       # s.t.
prob += x1 + 2*x2 <= 6

prob.solve()
print(f"x1={value(x1)}, x2={value(x2)}, z={value(prob.objective)}")
```

### 8.4 指派问题

```python
import numpy as np
from scipy.optimize import linear_sum_assignment

cost = np.array([
    [9, 2, 7, 8],
    [6, 4, 3, 7],
    [5, 8, 1, 8],
    [7, 6, 9, 4],
])

row_ind, col_ind = linear_sum_assignment(cost)
total = cost[row_ind, col_ind].sum()
# 最优指派: 0→1, 1→0, 2→2, 3→3, 总代价=13
```

---

## 9. 递推关系与生成函数

### 9.1 求解递推关系

```python
from sympy import symbols, Function, Eq, rsolve, simplify

n = symbols('n', integer=True)
y = Function('y')

# Fibonacci: y(n) = y(n-1) + y(n-2), y(0)=0, y(1)=1
eq = Eq(y(n), y(n-1) + y(n-2))
sol = rsolve(eq, y(n), {y(0): 0, y(1): 1})
# sol = √5*(1/2+√5/2)^n/5 - √5*(1/2-√5/2)^n/5

# 汉诺塔: T(n) = 2T(n-1) + 1, T(0)=0
eq2 = Eq(y(n), 2*y(n-1) + 1)
sol2 = rsolve(eq2, y(n), {y(0): 0})
# sol2 = 2^n - 1
```

### 9.2 生成函数提取系数

```python
from sympy import Symbol

x = Symbol('x')

# 1/(1-x)^k 的系数 = C(n+k-1, k-1)
gf = 1 / (1-x)**4
coeffs = [gf.series(x, 0, i+1).coeff(x, i) for i in range(8)]
# [1, 4, 10, 20, 35, 56, 84, 120]
```

---

## 10. 编码理论 (Coding Theory)

### 10.1 汉明距离

```python
def hamming_distance(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

codewords = ['0000', '0011', '1100', '1111']

# 最小汉明距离决定检错/纠错能力
min_dist = min(hamming_distance(codewords[i], codewords[j])
               for i in range(len(codewords))
               for j in range(i+1, len(codewords)))
# 检错: min_dist - 1 位
# 纠错: (min_dist - 1) // 2 位
```

### 10.2 汉明(7,4)码

```python
import numpy as np

# 生成矩阵 G (4×7)
G = np.array([
    [1,0,0,0,1,1,0],
    [0,1,0,0,1,0,1],
    [0,0,1,0,0,1,1],
    [0,0,0,1,1,1,1],
])

# 编码: c = d·G mod 2
data = np.array([1, 0, 1, 1])
codeword = data @ G % 2

# 校验矩阵 H (3×7)
H = np.array([
    [1,1,0,1,1,0,0],
    [1,0,1,1,0,1,0],
    [0,1,1,1,0,0,1],
])

# 伴随式: s = H·c^T mod 2 (全0表示无错)
syndrome = H @ codeword % 2
```

---

## 11. 自动机与形式语言

### 11.1 DFA 模拟

```python
def run_dfa(input_str, transitions, start, accept):
    current = start
    for ch in input_str:
        current = transitions.get((current, ch), current)
    return current in accept

# 识别包含 "01" 子串的二进制串
transitions = {
    ('q0', '0'): 'q1', ('q0', '1'): 'q0',
    ('q1', '0'): 'q1', ('q1', '1'): 'q2',
    ('q2', '0'): 'q2', ('q2', '1'): 'q2',
}

for s in ['010', '111', '0011', '10']:
    result = run_dfa(s, transitions, 'q0', {'q2'})
    print(f"'{s}' → {'接受' if result else '拒绝'}")
```

### 11.2 正则表达式

```python
import re

# 二进制串
re.match(r'^[01]+$', '10110')   # 匹配

# 偶数个1
re.match(r'^(0|1(01*0)*1)*$', '1100')  # 匹配

# 简单邮箱
re.match(r'^[a-z]+@[a-z]+\.[a-z]{2,3}$', 'test@com.cn')
```

---

## 12. 离散概率 (Discrete Probability)

### 12.1 古典概型与条件概率

```python
from math import comb

# 扑克牌: C(52,5) 种取法
total = comb(52, 5)

# 贝叶斯定理
p_disease = 0.001
p_pos_given_d = 0.99
p_pos_given_h = 0.05
p_pos = p_pos_given_d * p_disease + p_pos_given_h * (1 - p_disease)
p_d_given_pos = (p_pos_given_d * p_disease) / p_pos
```

### 12.2 常用分布

```python
from scipy.stats import binom

# 二项分布 B(n, p)
n, p = 10, 0.3

# P(X = k)
binom.pmf(3, n, p)

# P(X <= k)
binom.cdf(3, n, p)

# E[X] = np, Var[X] = np(1-p)
mean, var = binom.stats(n, p)
```

---

## 13. 进阶工具: Z3 / automata-lib / pyformlang

### 13.1 Z3 SMT Solver (强烈推荐)

**Z3** 是微软开发的 SMT 求解器，比 `sympy.satisfiable` **快几个数量级**，支持布尔逻辑、整数/实数算术、数组、位向量等。

| 功能 | sympy | Z3 |
|---|---|---|
| SAT求解 | `satisfiable()` | `Solver.check()` |
| 约束类型 | 仅布尔 | 布尔 + 整数 + 实数 + 位向量 + 数组 |
| 速度 | 慢 (教学级) | **极快** (工业级) |
| 应用 | 简单公式 | 数独、N皇后、程序验证 |

#### SAT求解

```python
from z3 import Bool, And, Or, Not, Implies, Solver, sat, Int

p, q, r = Bool('p'), Bool('q'), Bool('r')
s = Solver()
s.add(Implies(p, q))
s.add(Or(Not(q), r))
s.add(p)

if s.check() == sat:
    m = s.model()
    print(f"p={m[p]}, q={m[q]}, r={m[r]}")
```

#### 数独求解

```python
from z3 import Int, Solver, sat, Distinct

X = [[Int(f"x_{i}_{j}") for j in range(9)] for i in range(9)]
s = Solver()

# 每格1-9
for i in range(9):
    for j in range(9):
        s.add(X[i][j] >= 1, X[i][j] <= 9)

# 行/列/宫唯一
for i in range(9):
    s.add(Distinct([X[i][j] for j in range(9)]))  # 行
    s.add(Distinct([X[j][i] for j in range(9)]))  # 列
for i in range(0,9,3):
    for j in range(0,9,3):
        s.add(Distinct([X[i+di][j+dj] for di in range(3) for dj in range(3)]))

# 填入已知数字
grid = [[5,3,0,0,7,0,0,0,0], ...]  # 0=空
for i in range(9):
    for j in range(9):
        if grid[i][j] != 0:
            s.add(X[i][j] == grid[i][j])

if s.check() == sat:
    m = s.model()
    for i in range(9):
        print([m[X[i][j]] for j in range(9)])
```

#### N皇后问题

```python
N = 8
Q = [Int(f"Q{i}") for i in range(N)]
s = Solver()
for i in range(N):
    s.add(Q[i] >= 0, Q[i] < N)
s.add(Distinct(Q))
for i in range(N):
    for j in range(i+1, N):
        s.add(Q[i]-Q[j] != i-j)
        s.add(Q[i]-Q[j] != j-i)
```

#### 逻辑推理验证

```python
from z3 import unsat

def check_validity(premises, conclusion):
    """前提 ⊢ 结论 是否有效"""
    s = Solver()
    s.add(And(*premises))
    s.add(Not(conclusion))
    return s.check() == unsat  # 前提∧¬结论不可满足 → 有效
```

### 13.2 automata-lib (自动机理论)

完整的自动机理论库，支持 DFA/NFA/PDA/TM。

```python
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

# DFA: 识别包含"01"子串的二进制串
dfa = DFA(
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
dfa.accepts_input('010')   # True
dfa.accepts_input('111')   # False

# NFA → DFA (子集构造法)
dfa_from_nfa = DFA.from_nfa(some_nfa)

# DFA 最小化
min_dfa = dfa.minify()

# DFA 等价性
dfa1 == dfa2  # True/False
```

### 13.3 pyformlang (形式语言理论)

支持正则表达式 ↔ DFA 双向转换、上下文无关文法 (CFG)。

```python
from pyformlang.regular_expression import Regex
from pyformlang.cfg import CFG

# 正则表达式 → 最小DFA
regex = Regex("(0|1)*01")
dfa = regex.to_epsilon_nfa().to_deterministic().minimize()
dfa.accepts([Symbol('0'), Symbol('1')])  # True

# 上下文无关文法
cfg = CFG.from_text("S -> a S b | epsilon")
cfg.contains("aabb")  # True
cfg.contains("abc")    # False
```

### 13.4 进阶图论算法补充

```python
# 最大流
flow_val, flow_dict = nx.maximum_flow(G, 's', 't')

# 拓扑排序 (DAG)
order = list(nx.topological_sort(DAG))

# 强连通分量 (Tarjan)
sccs = list(nx.strongly_connected_components(DG))

# 中心性指标
nx.degree_centrality(G)        # 度中心性
nx.betweenness_centrality(G)   # 介数中心性
nx.eigenvector_centrality(G)   # 特征向量中心性

# 二分图最大匹配 (Hopcroft-Karp)
matching = nx.bipartite.maximum_matching(B)

# 网络连通性
nx.node_connectivity(G)        # 节点连通度
nx.edge_connectivity(G)        # 边连通度
sorted(nx.laplacian_spectrum(G))[1]  # 代数连通度 (Fiedler值)
```

### 13.5 高级组合数学补充

```python
# Burnside 引理 (旋转等价下的项链计数)
def necklace_count(n, k):
    from math import gcd
    return sum(k ** gcd(d, n) for d in range(n)) // n

# Pólya 计数 (旋转+翻转)
def necklace_count_dihedral(n, k):
    from math import gcd
    total = sum(k ** gcd(d, n) for d in range(n))
    if n % 2 == 0:
        total += (n//2) * k**(n//2) + (n//2) * k**(n//2+1)
    else:
        total += n * k**((n+1)//2)
    return total // (2*n)

# 整数分拆
from sympy import partition
partition(10)  # 42

# 矩阵快速幂求递推
import numpy as np
M = np.array([[1,1],[1,0]], dtype=object)
fib_n = np.linalg.matrix_power(M, n)[0][0]
```

---

## 14. 速查表 (Quick Reference)

### 14.1 常用公式

| 名称 | 公式 | Python |
|---|---|---|
| 组合数 | C(n,k) = n!/(k!(n-k)!) | `comb(n,k)` |
| 排列数 | P(n,k) = n!/(n-k)! | `perm(n,k)` |
| 可重复组合 | C(n+k-1,k) | `comb(n+k-1,k)` |
| 幂集大小 | \|P(S)\| = 2^|S| | `2**len(S)` |
| 鸽巢原理 | ceil(n/m) | `math.ceil(n/m)` |
| 容斥(2集) | \|A∪B\| = \|A\|+\|B\|-\|A∩B\| | - |
| 容斥(3集) | \|A\|+\|B\|+\|C\|-\|A∩B\|-\|A∩C\|-\|B∩C\|+\|A∩B∩C\| | - |
| Catalan | C_n = C(2n,n)/(n+1) | `catalan(n)` |
| Fibonacci | F_n = F_{n-1} + F_{n-2} | `fibonacci(n)` |
| Stirling II | S(n,k): n物分k非空组 | `stirling(n,k,kind=2)` |
| 错排 | D(n) = (n-1)(D(n-1)+D(n-2)) | 自定义递归 |
| 欧拉函数 | φ(n) | `totient(n)` |
| 费马小定理 | a^{p-1} ≡ 1 (mod p) | `pow(a,p-1,p)` |
| 汉明距离 | 不同位数 | `sum(c1!=c2 for ...)` |

### 14.2 图论算法速查

| 算法 | NetworkX 函数 |
|---|---|
| BFS/DFS | `nx.bfs_tree(G, source)` / `nx.dfs_tree(G, source)` |
| 最短路径 (无权) | `nx.shortest_path(G, s, t)` |
| 最短路径 (带权) | `nx.dijkstra_path(G, s, t)` |
| 最小生成树 | `nx.minimum_spanning_tree(G)` |
| 欧拉回路 | `nx.eulerian_circuit(G)` |
| 图着色 | `nx.coloring.greedy_color(G)` |
| 二部图检测 | `nx.is_bipartite(G)` |
| 同构检测 | `nx.is_isomorphic(G1, G2)` |
| TSP近似 | `nx.approximation.traveling_salesman_problem(G)` |
| 最大流 | `nx.maximum_flow(G, s, t)` |
| 连通分量 | `nx.connected_components(G)` |
| 拓扑排序 | `nx.topological_sort(DG)` |

### 14.3 导入速查

```python
# 逻辑
from sympy import symbols, And, Or, Not, Implies, Equivalent, Xor
from sympy.logic.boolalg import truth_table, satisfiable, to_cnf, to_dnf
from sympy.logic import SOPform, POSform

# 集合
from sympy import FiniteSet, Interval

# 组合
from sympy import binomial, factorial, fibonacci, catalan
import itertools

# 图论
import networkx as nx
import igraph as ig

# 代数
from sympy.combinatorics import Permutation, PermutationGroup
from sympy import Matrix, det

# 数论
from sympy import isprime, primerange, factorint, gcd, lcm, totient, mod_inverse
from sympy.ntheory.modular import crt
from sympy.ntheory import discrete_log

# 优化
from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, LpInteger, lpSum
from scipy.optimize import linear_sum_assignment

# 概率
from scipy.stats import binom

# 布尔化简
from pyeda.inter import exprvar, expr, expr2truthtable

# ====== 进阶工具 ======

# SMT/SAT求解 (工业级)
from z3 import Bool, Int, And, Or, Not, Implies, Solver, sat, unsat, Distinct

# 自动机 (DFA/NFA/PDA/TM)
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

# 形式语言 (正则表达式↔DFA, CFG)
from pyformlang.regular_expression import Regex
from pyformlang.cfg import CFG
```

---

## 附录: 文件结构

```
learn/
├── discrete_math_examples.py    # 基础示例 (11个主题, 70+示例)
├── advanced_discrete_math.py    # 进阶示例 (Z3/automata/pyformlang/高级图论/高级组合)
├── discrete_math_doc.md         # 本文档
├── output/
│   ├── graph_examples.png       # 图论可视化
│   └── hasse_diagram.png        # Hasse图 (偏序集)
└── 提示词.md
```
