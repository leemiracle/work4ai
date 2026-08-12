"""
Part IA / IB Algorithms (Cambridge CST)
=======================================
覆盖主题：
- 分治（mergesort, 快速排序分析）
- 快速选择（quickselect, 期望 O(n)）
- 动态规划（LIS, coin change）
- Master theorem 验证
- NP 完全归约（SAT → 3SAT → Clique）

核心教材：
- Cormen, Leiserson, Rivest & Stein 2009 "Introduction to Algorithms" 3rd ed, MIT Press (CLRS)
- Kleinberg & Tardös 2006 "Algorithm Design", Pearson
- Karp 1972 "Reducibility Among Combinatorial Problems" Complexity of Computer Computations

本文件实现：
- mergesort + 逆序对计数
- quickselect（中位数，期望 O(n)）
- DP: LIS / coin change
- Master theorem 自动判定
- SAT → 3SAT → Clique 归约链

运行：
    python algorithms.py
"""
from __future__ import annotations
import random
import math


# ================================================================
# 1. 分治：mergesort + 逆序对
# ================================================================

def mergesort(arr):
    """返回 (sorted_arr, inversion_count)"""
    if len(arr) <= 1:
        return arr[:], 0
    mid = len(arr) // 2
    left, inv_l = mergesort(arr[:mid])
    right, inv_r = mergesort(arr[mid:])
    merged = []
    i = j = inv_split = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            inv_split += len(left) - i  # left[i:] 都比 right[j] 大
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, inv_l + inv_r + inv_split


# ================================================================
# 2. 快速选择（找第 k 小，期望 O(n)）
# ================================================================

def quickselect(arr, k):
    """返回 arr 中第 k 小元素（0-indexed）"""
    arr = list(arr)
    while True:
        pivot = random.choice(arr)
        lows = [x for x in arr if x < pivot]
        highs = [x for x in arr if x > pivot]
        pivots = [x for x in arr if x == pivot]
        if k < len(lows):
            arr = lows
        elif k < len(lows) + len(pivots):
            return pivot
        else:
            k -= len(lows) + len(pivots)
            arr = highs


# ================================================================
# 3. 动态规划
# ================================================================

def longest_increasing_subsequence(arr):
    """LIS: O(n log n) 用 patience sorting"""
    import bisect
    piles = []
    parent = {}
    indices = []
    for i, x in enumerate(arr):
        pos = bisect.bisect_left(piles, x)
        if pos == len(piles):
            piles.append(x)
            indices.append(i)
        else:
            piles[pos] = x
            indices[pos] = i
        parent[i] = indices[pos - 1] if pos > 0 else -1
    # 重建序列
    seq = []
    k = indices[len(piles) - 1]
    while k != -1:
        seq.append(arr[k])
        k = parent[k]
    return len(piles), seq[::-1]


def coin_change(coins, amount):
    """最少硬币数 DP"""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i and dp[i - c] + 1 < dp[i]:
                dp[i] = dp[i - c] + 1
    return dp[amount] if dp[amount] != float('inf') else -1


# ================================================================
# 4. Master Theorem 判定
# ================================================================

def master_theorem(a, b, f_is_theta_nc, extra_constant=0):
    """
    T(n) = aT(n/b) + f(n)
    a: 子问题数, b: 缩小因子
    f_is_theta_nc: f(n) = Θ(n^c) 的指数 c

    返回 T(n) 的渐近界。
    关键比较: c vs log_b(a)
    """
    crit = math.log(a) / math.log(b)
    c = f_is_theta_nc
    if c < crit - 1e-9:
        return f"Θ(n^{crit:.2f})  [Case 1: c={c} < log_b(a)={crit:.2f}]"
    elif abs(c - crit) < 1e-9:
        return f"Θ(n^{crit:.2f} log n)  [Case 2: c = log_b(a) = {crit:.2f}]"
    else:
        return f"Θ(n^{c})  [Case 3: c={c} > log_b(a)={crit:.2f}]"


# ================================================================
# 5. NP 完全归约
# ================================================================

def sat_to_3sat(clauses):
    """
    SAT → 3SAT 归约（CLRS 标准等价归约 / equi-satisfiable）。
    输入: clause list (每个 clause 是 literal list, ! 前缀表示否定)
    将每个子句转换为恰好 3 个文字的子句集合（引入新变量），
    保持等价可满足性：原 SAT 可满足 ⟺ 归约后 3SAT 可满足。

    归约规则（对子句 C = (l_1 ∨ ... ∨ l_k)）：
      k=1: 4 子句 + 2 新变量 y_1,y_2, 强制 l_1=True
      k=2: 2 子句 + 1 新变量 z
      k=3: 原样保留
      k≥4: 链式拆分, k-3 新变量, k-2 子句
    """
    result = []
    fresh = [0]

    def new_var():
        fresh[0] += 1
        return f"z{fresh[0]}"

    def neg(lit):
        """返回文字的否定（! 前缀表示否定）"""
        return lit[1:] if lit.startswith("!") else f"!{lit}"

    for clause in clauses:
        k = len(clause)
        if k == 1:
            # (l_1) → 4 子句 + 2 新变量 y_1, y_2
            # (l_1∨y_1∨y_2) ∧ (l_1∨y_1∨¬y_2) ∧ (l_1∨¬y_1∨y_2) ∧ (l_1∨¬y_1∨¬y_2)
            # 后 3 子句的 y 部分穷尽 y_1,y_2 全部 4 种取值, 必有一项为假 → l_1 必须为真
            y1, y2 = new_var(), new_var()
            l = clause[0]
            result.append([l, y1, y2])
            result.append([l, y1, neg(y2)])
            result.append([l, neg(y1), y2])
            result.append([l, neg(y1), neg(y2)])
        elif k == 2:
            # (l_1 ∨ l_2) → 2 子句 + 1 新变量 z
            # (l_1∨l_2∨z) ∧ (l_1∨l_2∨¬z) — z 任取值都不影响, 等价于 (l_1∨l_2)
            z = new_var()
            result.append([clause[0], clause[1], z])
            result.append([clause[0], clause[1], neg(z)])
        elif k == 3:
            result.append(list(clause))
        else:
            # k ≥ 4: 链式拆分, k-3 个新变量 y_1..y_{k-3}, 共 k-2 子句
            # (l_1∨l_2∨y_1) ∧ (¬y_1∨l_3∨y_2) ∧ ... ∧ (¬y_{k-3}∨l_{k-1}∨l_k)
            ys = [new_var() for _ in range(k - 3)]
            result.append([clause[0], clause[1], ys[0]])               # 首子句
            for j in range(1, k - 3):                                  # 中间子句
                result.append([neg(ys[j - 1]), clause[j + 1], ys[j]])
            result.append([neg(ys[k - 4]), clause[k - 2], clause[k - 1]])  # 末子句
    return result


# ----------------------------------------------------------------
# 等价可满足性穷举验证工具
# ----------------------------------------------------------------

def _eval_clause(clause, assignment):
    """评估单个子句在给定赋值下是否为真"""
    for lit in clause:
        negated = lit.startswith("!")
        var = lit[1:] if negated else lit
        lit_true = (not assignment.get(var, False)) if negated else assignment.get(var, False)
        if lit_true:
            return True
    return False


def _brute_force_sat(clauses):
    """穷举所有赋值, 返回公式是否可满足（仅用于小规模验证）"""
    from itertools import product
    varnames = set()
    for clause in clauses:
        for lit in clause:
            varnames.add(lit.lstrip("!"))
    varnames = sorted(varnames)
    for vals in product([False, True], repeat=len(varnames)):
        assignment = dict(zip(varnames, vals))
        if all(_eval_clause(c, assignment) for c in clauses):
            return True
    return False


def clique_from_3sat(clauses_3, n_vars):
    """
    3SAT → Clique 归约。
    每个 3SAT 子句的每个文字 = 图中一个顶点。
    两个顶点连边 ⟺ 不同子句 ∧ 文字不矛盾。
    有大小 = 子句数的 clique ⟺ 3SAT 可满足。
    """
    vertices = []  # (clause_idx, literal)
    for ci, clause in enumerate(clauses_3):
        for li, lit in enumerate(clause):
            vertices.append((ci, lit))

    edges = set()
    for i, (c1, l1) in enumerate(vertices):
        for j, (c2, l2) in enumerate(vertices):
            if i < j and c1 != c2:
                # 不矛盾: l1 和 l2 不是 x 和 !x
                if not (l1.lstrip('!') == l2.lstrip('!') and
                        ('!' in l1) != ('!' in l2)):
                    edges.add((i, j))

    return vertices, edges


def greedy_clique(vertices, edges):
    """贪心近似求 clique"""
    adj = {i: set() for i in range(len(vertices))}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    # 贪心: 从度最大的点开始
    best = []
    for start in range(len(vertices)):
        clique = {start}
        candidates = adj[start]
        while candidates:
            v = max(candidates, key=lambda x: len(adj[x] & clique))
            if adj[v] >= clique:
                clique.add(v)
                candidates = adj[v] - clique
            else:
                candidates.discard(v)
        if len(clique) > len(best):
            best = sorted(clique)
    return [vertices[i] for i in best]


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IA/IB Algorithms — Demo")
    print("=" * 64)
    random.seed(42)

    # 1. Mergesort + 逆序对
    print("\n📋 1. Mergesort + 逆序对计数")
    arr = [5, 2, 8, 1, 9, 3, 7, 4, 6, 0]
    sorted_arr, inv = mergesort(arr)
    print(f"   原: {arr}")
    print(f"   排序: {sorted_arr}")
    print(f"   逆序对数: {inv}")
    # 验证：逆序最大为 n(n-1)/2
    n = len(arr)
    print(f"   理论最大逆序: {n*(n-1)//2}, 实际: {inv}")

    # 2. Quickselect
    print("\n📋 2. Quickselect（期望 O(n) 求中位数）")
    big = [random.randint(0, 10000) for _ in range(10001)]
    med = quickselect(big, 5000)
    print(f"   10001 个随机数的中位数: {med}")
    print(f"   排序验证: {sorted(big)[5000]}")

    # 3. LIS
    print("\n📋 3. 最长递增子序列 LIS")
    seq = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9]
    length, lis = longest_increasing_subsequence(seq)
    print(f"   序列: {seq}")
    print(f"   LIS 长度: {length}, 序列: {lis}")

    # 4. Coin change
    print("\n📋 4. Coin Change DP")
    for amt in [11, 27, 100]:
        result = coin_change([1, 5, 10, 25], amt)
        print(f"   coins=[1,5,10,25], amount={amt}: 最少 {result} 枚")

    # 5. Master theorem
    print("\n📋 5. Master Theorem 判定")
    cases = [
        ("Mergesort", 2, 2, 1),       # T = 2T(n/2) + O(n)
        ("Binary search", 1, 2, 0),   # T = T(n/2) + O(1)
        ("Strassen", 7, 2, 2),        # T = 7T(n/2) + O(n^2)
        ("Naive matmul", 8, 2, 2),    # T = 8T(n/2) + O(n^2)
    ]
    for name, a, b, c in cases:
        result = master_theorem(a, b, c)
        print(f"   {name}: T(n)={a}T(n/{b})+O(n^{c}) → {result}")

    # 6. NP 归约链
    print("\n📋 6. NP 完全归约: SAT → 3SAT → Clique")
    sat_input = [["x1", "x2", "x3", "x4"], ["!x1", "x2"], ["x3"]]
    print(f"   SAT 输入: {sat_input}")
    clauses_3 = sat_to_3sat(sat_input)
    print(f"   3SAT 子句数: {len(clauses_3)}")
    for c in clauses_3:
        print(f"      {c}")
    vertices, edges = clique_from_3sat(clauses_3, 4)
    print(f"   Clique 图: {len(vertices)} 顶点, {len(edges)} 边")
    clique = greedy_clique(vertices, edges)
    print(f"   贪心 clique: {len(clique)} 个顶点")
    print(f"   → 若 |clique| = 子句数, 则 3SAT 可满足")

    # 6b. 等价可满足性穷举验证
    print("\n   📐 等价可满足性穷举验证（equi-satisfiability）:")
    test_cases = [
        ("可满足: (x1∨x2∨x3∨x4) ∧ (!x1∨x2) ∧ (x3)",
         [["x1", "x2", "x3", "x4"], ["!x1", "x2"], ["x3"]]),
        ("不可满足: (x1) ∧ (!x1)  — 单元子句矛盾",
         [["x1"], ["!x1"]]),
        ("不可满足: 2-SAT 四子句穷尽 (x1,x2) 全部赋值",
         [["x1", "x2"], ["!x1", "x2"], ["x1", "!x2"], ["!x1", "!x2"]]),
    ]
    all_ok = True
    for desc, formula in test_cases:
        sat_orig = _brute_force_sat(formula)
        reduced = sat_to_3sat(formula)
        sat_red = _brute_force_sat(reduced)
        ok = sat_orig == sat_red
        all_ok = all_ok and ok
        mark = "✅等价" if ok else "❌不等价(BUG!)"
        print(f"   {desc}")
        print(f"      原始SAT={sat_orig}  归约3SAT={sat_red}  {mark}")
    print(f"   {'✅ 全部通过：归约保持等价可满足性' if all_ok else '❌ 存在不等价！'}")

    print("\n✅ Algorithms 完成！")
    print("\n💡 反直觉发现：")
    print("   - mergesort 顺带数逆序对（O(n log n) 而非 O(n²)）")
    print("   - quickselect 找中位数只需 O(n)，比先排序 O(n log n) 更快")
    print("   - Strassen(7子问题) vs 朴素(8子问题): 同为 Case 1（c < log_b(a)），但 Strassen 的指数 log₂7≈2.81 vs 朴素 log₂8=3")
    print("   - SAT→3SAT→Clique: 看似无关的问题通过归约证明同等难度")


if __name__ == "__main__":
    demo()
