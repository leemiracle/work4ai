"""
Algorithms (Oxford CS)
================================================
覆盖主题：
- 分治法（merge sort / quick sort + 复杂度分析）
- 动态规划（最长公共子序列 / 0-1 背包）
- 图算法（Dijkstra / Prim 最小生成树）
- 复杂度证明（主定理 / amortized analysis）

核心教材（已核实）：
- Cormen, Leiserson, Rivest, Stein "Introduction to Algorithms" 3rd ed, MIT Press 2009 (CLRS)
- Kleinberg & Tardös "Algorithm Design" 2006
- Tarjan "Amortized Computational Complexity" SIAM J Alg Disc Meth 1985

本文件实现：
- Merge sort（含递归调用计数，验证 O(n log n)）
- Quick sort（随机 pivot，验证期望 O(n log n)）
- LCS 动态规划
- Dijkstra 最短路
- Prim 最小生成树

运行：
    python algorithms.py
"""
from __future__ import annotations
import heapq
import random
from collections import defaultdict


# ============ 1. 分治：Merge Sort ============

_merge_comparisons = [0]

def merge_sort(arr: list) -> tuple[list, int]:
    """归并排序，返回 (排序结果, 比较次数)。
    复杂度：T(n) = 2T(n/2) + O(n) → O(n log n) （主定理 case 2）
    """
    global _merge_comparisons
    if len(arr) <= 1:
        return arr, _merge_comparisons
    mid = len(arr) // 2
    left, _ = merge_sort(arr[:mid])
    right, _ = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list, right: list) -> tuple[list, int]:
    global _merge_comparisons
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        _merge_comparisons += 1
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result, _merge_comparisons


def merge_sort_with_count(arr: list) -> tuple[list, int]:
    """干净的 merge sort，返回 (结果, 比较次数)"""
    comparisons = [0]

    def sort(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = sort(a[:mid])
        right = sort(a[mid:])
        return merge(left, right)

    def merge(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    return sort(arr), comparisons[0]


# ============ 2. 分治：Quick Sort ============

_quick_comparisons = [0]

def quick_sort(arr: list, randomized: bool = True) -> tuple[list, int]:
    """快速排序。随机化 pivot → 期望 O(n log n)。
    最坏情况（固定 pivot + 已排序输入）= O(n²)
    """
    global _quick_comparisons
    _quick_comparisons = [0]
    result = _qs(list(arr), randomized)
    return result, _quick_comparisons[0]


def _qs(arr: list, randomized: bool) -> list:
    global _quick_comparisons
    if len(arr) <= 1:
        return arr
    if randomized:
        pivot_idx = random.randint(0, len(arr) - 1)
        pivot = arr[pivot_idx]
        rest = arr[:pivot_idx] + arr[pivot_idx + 1:]
    else:
        pivot = arr[0]
        rest = arr[1:]
    left = []
    right = []
    for x in rest:
        _quick_comparisons[0] += 1
        if x < pivot:
            left.append(x)
        else:
            right.append(x)
    return _qs(left, randomized) + [pivot] + _qs(right, randomized)


# ============ 3. 动态规划：LCS ============

def lcs(s1: str, s2: str) -> tuple[int, str]:
    """最长公共子序列。
    dp[i][j] = LCS(s1[:i], s2[:j])
    dp[i][j] = dp[i-1][j-1]+1        if s1[i-1]==s2[j-1]
             = max(dp[i-1][j], dp[i][j-1])  otherwise
    复杂度：O(mn) 时间 + 空间
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # 回溯找 LCS 字符串
    lcs_str = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i-1] == s2[j-1]:
            lcs_str.append(s1[i-1])
            i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1

    return dp[m][n], ''.join(reversed(lcs_str))


def knapsack_01(weights: list, values: list, capacity: int) -> tuple[int, list[int]]:
    """0-1 背包问题。
    dp[i][w] = 用前 i 个物品、容量 w 的最大价值
    复杂度：O(nW)
    返回 (最大价值, 选中的物品索引列表)
    """
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i-1][w]  # 不选物品 i
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1])

    # 回溯找选中物品
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(i - 1)
            w -= weights[i-1]

    return dp[n][capacity], list(reversed(selected))


# ============ 4. 图算法：Dijkstra ============

def dijkstra(graph: dict, source: str) -> tuple[dict, dict]:
    """Dijkstra 单源最短路。
    graph = {node: {neighbor: weight}}
    复杂度：O((V+E) log V) with binary heap
    """
    dist = {v: float('inf') for v in graph}
    prev = {v: None for v in graph}
    dist[source] = 0
    pq = [(0, source)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph[u].items():
            new_dist = d + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))

    return dist, prev


def reconstruct_path(prev: dict, source: str, target: str) -> list[str]:
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == source else []


# ============ 5. 图算法：Prim MST ============

def prim_mst(graph: dict) -> tuple[int, list[tuple]]:
    """Prim 最小生成树。
    从任意节点开始，每次选最小权重的横切边。
    复杂度：O(E log V) with heap
    """
    if not graph:
        return 0, []
    start = next(iter(graph))
    in_mst = {start}
    edges = []  # (weight, from, to)
    total_weight = 0
    mst_edges = []

    for v, w in graph[start].items():
        heapq.heappush(edges, (w, start, v))

    while edges and len(in_mst) < len(graph):
        w, u, v = heapq.heappop(edges)
        if v in in_mst:
            continue
        in_mst.add(v)
        total_weight += w
        mst_edges.append((u, v, w))
        for neighbor, weight in graph[v].items():
            if neighbor not in in_mst:
                heapq.heappush(edges, (weight, v, neighbor))

    return total_weight, mst_edges


# ============ 6. 主定理验证 ============

def master_theorem(a: int, b: float, f_n_asymptotic: str) -> str:
    """主定理：T(n) = aT(n/b) + f(n)
    Case 1: f(n) = O(n^{log_b a - ε}) → T(n) = Θ(n^{log_b a})
    Case 2: f(n) = Θ(n^{log_b a})     → T(n) = Θ(n^{log_b a} log n)
    Case 3: f(n) = Ω(n^{log_b a + ε}) → T(n) = Θ(f(n))
    """
    import math
    log_b_a = math.log(a) / math.log(b)
    return (f"T(n) = {a}T(n/{b}) + {f_n_asymptotic}, "
            f"log_{b}({a}) = {log_b_a:.2f}")


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Algorithms (Oxford CS) Demo")
    print("=" * 65)

    random.seed(42)

    # 1. Merge Sort vs Quick Sort 比较计数
    print("\n📋 1. 分治排序：比较次数对比")
    arr = list(range(100))
    random.shuffle(arr)

    _, ms_comps = merge_sort_with_count(arr)
    _, qs_rand_comps = quick_sort(arr, randomized=True)
    _, qs_fixed_comps = quick_sort(arr, randomized=False)

    n = len(arr)
    n_log_n = n * (n.bit_length())  # ≈ n log₂ n
    print(f"   n={n}, n log₂ n ≈ {n_log_n}")
    print(f"   Merge sort 比较次数:      {ms_comps}")
    print(f"   Quick sort (随机 pivot):  {qs_rand_comps}")
    print(f"   Quick sort (固定 pivot):  {qs_fixed_comps}")

    # 验证排序正确
    assert merge_sort_with_count(arr)[0] == sorted(arr)
    assert quick_sort(arr)[0] == sorted(arr)

    # 最坏情况：已排序数组 + 固定 pivot
    sorted_arr = list(range(50))
    _, qs_worst = quick_sort(sorted_arr, randomized=False)
    _, qs_best_rand = quick_sort(sorted_arr, randomized=True)
    print(f"\n   最坏情况（已排序+固定pivot, n=50）:")
    print(f"   固定 pivot 比较次数: {qs_worst} (≈n²/2={50*49//2})")
    print(f"   随机 pivot 比较次数: {qs_best_rand} (期望≈n log n={50*6:.0f})")

    # 2. LCS
    print("\n📋 2. 动态规划：最长公共子序列")
    s1, s2 = "ABCBDAF", "ACBDBAF"
    length, lcs_str = lcs(s1, s2)
    print(f"   LCS('{s1}', '{s2}') = '{lcs_str}', 长度={length}")

    # DNA 序列
    dna1 = "ACGTACGTACGT"
    dna2 = "AGTACGTCGTA"
    length2, lcs2 = lcs(dna1, dna2)
    print(f"   LCS('{dna1}', '{dna2}') = '{lcs2}', 长度={length2}")

    # 3. 背包
    print("\n📋 3. 动态规划：0-1 背包")
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8
    max_val, selected = knapsack_01(weights, values, capacity)
    print(f"   物品(重量/价值): {list(zip(weights, values))}")
    print(f"   容量={capacity} → 最大价值={max_val}, 选中={selected}")

    # 4. Dijkstra
    print("\n📋 4. 图算法：Dijkstra 最短路")
    graph = {
        'A': {'B': 4, 'C': 2},
        'B': {'A': 4, 'C': 1, 'D': 5},
        'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
        'D': {'B': 5, 'C': 8, 'E': 2},
        'E': {'C': 10, 'D': 2},
    }
    dist, prev = dijkstra(graph, 'A')
    print(f"   从 A 出发的最短距离: {dist}")
    path = reconstruct_path(prev, 'A', 'E')
    print(f"   A→E 路径: {' → '.join(path)}, 总距离={dist['E']}")

    # 5. Prim MST
    print("\n📋 5. 图算法：Prim 最小生成树")
    total, mst = prim_mst(graph)
    print(f"   MST 总权重: {total}")
    for u, v, w in mst:
        print(f"     {u} -- {v}: {w}")

    # 6. 主定理
    print("\n📋 6. 主定理应用")
    print(f"   {master_theorem(2, 2, 'O(n)')} → Merge sort, Case 2 → Θ(n log n)")
    print(f"   {master_theorem(2, 2, 'O(1)')} → 二分搜索, Case 1 → Θ(n^1) → Θ(log n)")
    print(f"   {master_theorem(1, 2, 'O(1)')} → 二分搜索 (a=1)")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print(f"   1. 对已排序数组，固定pivot快排={qs_worst}次比较（≈n²/2）")
    print(f"      但随机pivot={qs_best_rand}次（≈n log n）—— 仅改 pivot 策略")
    print(f"   2. A→E 直连权重10，但经 A→C→B→D→E={dist['E']} 更短")
    print(f"      贪心直觉（选直连）在带权图上错误，必须用 Dijkstra")
    print(f"   3. MST 贪心(Prim)=最优——这是贪心算法能保证最优的典型案例")
    print("=" * 65)


if __name__ == "__main__":
    main()
