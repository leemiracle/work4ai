"""
6.1210/6.006 Introduction to Algorithms（MIT）
================================================
覆盖主题：
- 最短路：Dijkstra、Bellman-Ford（Lecture 9-10, 13）
- 动态规划：LIS、Edit Distance（Lecture 15-16, 19）
- 最小生成树：Kruskal、Prim（Lecture 18）

核心教材/论文（经典，无 arXiv ID）：
- Cormen, Leiserson, Rivest, Stein (CLRS) "Introduction to Algorithms" 4th ed, Ch 22-25
- Dijkstra 1959 "A Note on Two Problems in Connexion with Graphs" Numerische Mathematik
- Bellman 1958 "On a Routing Problem" Quarterly of Applied Mathematics
- Kruskal 1956 "On the Shortest Spanning Subtree of a Graph" Proc AMS

本文件实现：
- Dijkstra（优先队列）
- Bellman-Ford（负权检测）
- DP: LIS (最长递增子序列) + Edit Distance
- MST: Kruskal（union-find）+ Prim

运行：
    python algorithms.py
"""
from __future__ import annotations
import heapq
from dataclasses import dataclass


# ============ 1. 图数据结构 ============

@dataclass
class Graph:
    """有向带权图（邻接表）"""
    nodes: set
    edges: dict  # node -> [(neighbor, weight), ...]

    @classmethod
    def from_edges(cls, edge_list: list[tuple]) -> 'Graph':
        nodes = set()
        adj = {}
        for u, v, w in edge_list:
            nodes.add(u); nodes.add(v)
            adj.setdefault(u, []).append((v, w))
            adj.setdefault(v, [])
        return cls(nodes=nodes, edges=adj)


# ============ 2. 最短路算法 ============

def dijkstra(g: Graph, src) -> tuple[dict, dict]:
    """Dijkstra 单源最短路（非负权）。O((V+E) log V) with binary heap."""
    dist = {n: float('inf') for n in g.nodes}
    dist[src] = 0
    prev = {n: None for n in g.nodes}
    pq = [(0, src)]
    visited = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in g.edges.get(u, []):
            if w < 0:
                raise ValueError("Dijkstra 不支持负权！")
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def bellman_ford(g: Graph, src) -> tuple[dict, bool]:
    """Bellman-Ford：支持负权，检测负环。O(VE)"""
    dist = {n: float('inf') for n in g.nodes}
    dist[src] = 0
    n = len(g.nodes)
    for _ in range(n - 1):
        updated = False
        for u in g.nodes:
            if dist[u] == float('inf'):
                continue
            for v, w in g.edges.get(u, []):
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    updated = True
        if not updated:
            break
    # 检测负环
    has_neg_cycle = False
    for u in g.nodes:
        if dist[u] == float('inf'):
            continue
        for v, w in g.edges.get(u, []):
            if dist[u] + w < dist[v]:
                has_neg_cycle = True
                break
    return dist, has_neg_cycle


def reconstruct_path(prev: dict, src, dst) -> list:
    path = []
    cur = dst
    while cur is not None:
        path.append(cur)
        if cur == src:
            break
        cur = prev[cur]
    return path[::-1] if path and path[-1] == src else []


# ============ 3. 动态规划 ============

def lis(arr: list[int]) -> tuple[int, list[int]]:
    """最长递增子序列。O(n^2) DP。"""
    n = len(arr)
    if n == 0:
        return 0, []
    dp = [1] * n
    prev = [-1] * n
    for i in range(n):
        for j in range(i):
            if arr[j] < arr[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                prev[i] = j
    best = max(range(n), key=lambda i: dp[i])
    # 回溯
    seq = []
    k = best
    while k != -1:
        seq.append(arr[k])
        k = prev[k]
    return dp[best], seq[::-1]


def edit_distance(s1: str, s2: str) -> tuple[int, list[list[int]]]:
    """Levenshtein 编辑距离。O(nm) DP。dp[i][j] = s1[:i] → s2[:j] 最小操作数。"""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i  # 删除
    for j in range(m + 1):
        dp[0][j] = j  # 插入
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # 删除
                    dp[i][j-1],    # 插入
                    dp[i-1][j-1],  # 替换
                )
    return dp[n][m], dp


# ============ 4. 最小生成树 ============

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def kruskal(nodes: list, edges: list[tuple]) -> list[tuple]:
    """Kruskal MST。edges = [(w, u, v), ...]。O(E log E)。"""
    idx = {n: i for i, n in enumerate(nodes)}
    uf = UnionFind(len(nodes))
    edges_sorted = sorted(edges)
    mst = []
    for w, u, v in edges_sorted:
        if uf.union(idx[u], idx[v]):
            mst.append((u, v, w))
    return mst


def prim(nodes: list, adj: dict, start) -> list[tuple]:
    """Prim MST。adj = {node: [(neighbor, weight), ...]}。O(E log V)。"""
    in_mst = set()
    mst_edges = []
    pq = [(0, start, None)]
    while pq and len(in_mst) < len(nodes):
        w, u, parent = heapq.heappop(pq)
        if u in in_mst:
            continue
        in_mst.add(u)
        if parent is not None:
            mst_edges.append((parent, u, w))
        for v, ew in adj.get(u, []):
            if v not in in_mst:
                heapq.heappush(pq, (ew, v, u))
    return mst_edges


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.006 Algorithms: Dijkstra / Bellman-Ford / DP / MST")
    print("=" * 65)

    # --- Dijkstra ---
    print("\n📋 1. Dijkstra 最短路")
    edges = [('S','A',10),('S','B',5),('A','B',2),('A','C',1),
             ('B','A',3),('B','C',9),('B','D',2),('C','D',4)]
    g = Graph.from_edges(edges)
    dist, prev = dijkstra(g, 'S')
    for n in sorted(dist):
        print(f"  S→{n}: dist={dist[n]}", end="")
        if dist[n] < float('inf'):
            print(f"  path={' → '.join(reconstruct_path(prev,'S',n))}")
        else:
            print()
    print("  参考：CLRS Fig 24.6 经典示例")

    # --- Bellman-Ford with negative edges ---
    print("\n📋 2. Bellman-Ford（含负权）")
    neg_edges = [('S','A',4),('S','B',5),('A','B',-3),('B','A',2),('A','C',1)]
    g2 = Graph.from_edges(neg_edges)
    dist2, neg = bellman_ford(g2, 'S')
    print(f"  含负权边 A→B(-3): {dict(sorted(dist2.items()))}")
    print(f"  负环? {neg}")
    print("  → Dijkstra 无法处理负权；Bellman-Ford 可以，还能检测负环。")

    # --- LIS ---
    print("\n📋 3. 最长递增子序列 (LIS)")
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    length, seq = lis(arr)
    print(f"  数组: {arr}")
    print(f"  LIS 长度: {length}, 子序列: {seq}")

    # --- Edit Distance ---
    print("\n📋 4. 编辑距离 (Levenshtein)")
    s1, s2 = "kitten", "sitting"
    ed, table = edit_distance(s1, s2)
    print(f"  '{s1}' → '{s2}': 编辑距离 = {ed}")
    # 打印 DP 表
    print(f"  DP 表:")
    print("     " + " ".join(f"{c:>3}" for c in "  " + s2))
    for i, row in enumerate(table):
        ch = " " if i == 0 else s1[i-1]
        print(f"  {ch:>2} " + " ".join(f"{v:>3}" for v in row))

    # --- MST Kruskal vs Prim ---
    print("\n📋 5. 最小生成树 (Kruskal vs Prim)")
    nodes = list('ABCDEF')
    wedges = [(7,'A','B'),(5,'A','D'),(8,'B','C'),(9,'B','D'),
              (7,'B','E'),(5,'C','E'),(15,'D','E'),(6,'D','F'),(8,'E','F'),(11,'B','F')]
    mst_k = kruskal(nodes, wedges)
    total_k = sum(w for _, _, w in mst_k)
    adj_mst = {n: [] for n in nodes}
    for w, u, v in wedges:
        adj_mst[u].append((v, w)); adj_mst[v].append((u, w))
    mst_p = prim(nodes, adj_mst, 'A')
    total_p = sum(w for _, _, w in mst_p)
    print(f"  Kruskal MST: {mst_k}  total={total_k}")
    print(f"  Prim    MST: {mst_p}  total={total_p}")
    assert total_k == total_p, "两算法 MST 总权重应相同"
    print(f"  ✓ 两种算法得到相同总权重 {total_k}（边集合可能不同但权重一致）")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print('💡 反直觉发现：负权边让"贪心"失效')
    print("=" * 65)
    print("Dijkstra 是贪心算法——一旦确定某节点最短路就不再更新。")
    print("但负权边会打破这个假设：")
    edges3 = [('A','B',4),('A','C',2),('C','B',-3)]
    g3 = Graph.from_edges(edges3)
    try:
        d_dij, _ = dijkstra(g3, 'A')
        d_bf, _ = bellman_ford(g3, 'A')
        print(f"  Dijkstra    A→B = {d_dij['B']}  (错误！贪心先锁定 B=4)")
        print(f"  Bellman-Ford A→B = {d_bf['B']}  (正确：A→C→B = 2+(-3) = -1)")
        print(f"  差异 = {d_dij['B'] - d_bf['B']}")
    except ValueError as e:
        print(f"  {e}")

    print("\n✅ 6.006 Demo 完成！")


if __name__ == "__main__":
    demo()
