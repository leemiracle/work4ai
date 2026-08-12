"""
COS 226 Algorithms（Princeton）— Graph Algorithms
====================================================
覆盖主题（Sedgewick & Wayne, Algorithms 4th ed, Ch 4）：
- DFS / BFS（连通分量、最短路径）
- Kruskal MST（union-find + 贪心）
- Dijkstra 最短路（优先队列）
- Ford-Fulkerson 最大流（增广路径）
- Burrows-Wheeler Transform（BWT，用于 bzip2 压缩）

核心教材/论文：
- Sedgewick & Wayne "Algorithms" 4th ed, Section 4.1-4.4
- Dijkstra 1959 "A Note on Two Problems in Connexion with Graphs" Numerische Mathematik
- Ford & Fulkerson 1956 "Maximal Flow through a Network" Canadian J Math
- Kruskal 1956 "On the Shortest Spanning Subtree of a Graph" Proc AMS
- Burrows & Wheeler 1994 "A Block-Sorting Lossless Data Compression Algorithm" DEC SRC

本文件实现：
1. DFS (recursive) + BFS (queue-based) on adjacency list
2. Kruskal MST via Union-Find
3. Dijkstra shortest path via min-heap
4. Ford-Fulkerson max-flow (BFS-based Edmonds-Karp)
5. Burrows-Wheeler Transform (encode + decode)

运行：
    python graphs.py
"""
from __future__ import annotations
import heapq
from collections import deque


# ================================================================
# 1. Graph + DFS + BFS
# ================================================================

class Graph:
    """Undirected graph with adjacency list."""

    def __init__(self, n: int):
        self.n = n
        self.adj: list[list[int]] = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int):
        self.adj[u].append(v)
        self.adj[v].append(u)

    def add_directed(self, u: int, v: int, w: float = 1.0):
        self.adj[u].append((v, w))


def dfs(graph: Graph, start: int) -> list[int]:
    """Depth-first search — returns visited order."""
    visited = set()
    order = []

    def go(u):
        visited.add(u)
        order.append(u)
        for v in graph.adj[u]:
            if isinstance(v, tuple):
                v = v[0]
            if v not in visited:
                go(v)

    go(start)
    return order


def bfs(graph: Graph, start: int) -> tuple[list[int], list[int]]:
    """Breadth-first search — returns (order, distances)."""
    visited = {start}
    queue = deque([start])
    order = [start]
    dist = [-1] * graph.n
    dist[start] = 0
    while queue:
        u = queue.popleft()
        for v in graph.adj[u]:
            if isinstance(v, tuple):
                v = v[0]
            if v not in visited:
                visited.add(v)
                order.append(v)
                dist[v] = dist[u] + 1
                queue.append(v)
    return order, dist


# ================================================================
# 2. Union-Find (for Kruskal MST)
# ================================================================

class UnionFind:
    """Union-Find with path compression + union by rank."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of components

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1
        return True


def kruskal_mst(n: int, edges: list[tuple[float, int, int]]) -> list[tuple[float, int, int]]:
    """
    Kruskal MST: sort edges by weight, greedily add if no cycle.
    edges: list of (weight, u, v). Returns MST edges.
    """
    edges_sorted = sorted(edges)
    uf = UnionFind(n)
    mst = []
    total = 0.0
    for w, u, v in edges_sorted:
        if uf.union(u, v):
            mst.append((w, u, v))
            total += w
            if len(mst) == n - 1:
                break
    return mst


# ================================================================
# 3. Dijkstra Shortest Path
# ================================================================

def dijkstra(n: int, adj: dict[int, list[tuple[int, float]]], src: int) -> list[float]:
    """Dijkstra: single-source shortest path with min-heap."""
    dist = [float('inf')] * n
    dist[src] = 0.0
    pq = [(0.0, src)]
    visited = [False] * n
    while pq:
        d, u = heapq.heappop(pq)
        if visited[u]:
            continue
        visited[u] = True
        for v, w in adj.get(u, []):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist


# ================================================================
# 4. Ford-Fulkerson Max Flow (Edmonds-Karp: BFS augmenting paths)
# ================================================================

class FlowNetwork:
    """Max-flow via Edmonds-Karp (BFS-based Ford-Fulkerson)."""

    def __init__(self, n: int):
        self.n = n
        # capacity[u][v] = remaining capacity
        self.cap = [[0.0] * n for _ in range(n)]

    def add_edge(self, u, v, cap):
        self.cap[u][v] += cap

    def _bfs_find_path(self, s, t, parent):
        """BFS to find augmenting path. Returns True if path found."""
        visited = [False] * self.n
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            for v in range(self.n):
                if not visited[v] and self.cap[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    if v == t:
                        return True
                    queue.append(v)
        return False

    def max_flow(self, s, t) -> float:
        parent = [-1] * self.n
        total_flow = 0.0
        while self._bfs_find_path(s, t, parent):
            # Find min capacity along the path
            path_flow = float('inf')
            v = t
            while v != s:
                u = parent[v]
                path_flow = min(path_flow, self.cap[u][v])
                v = u
            # Update residual capacities
            v = t
            while v != s:
                u = parent[v]
                self.cap[u][v] -= path_flow
                self.cap[v][u] += path_flow
                v = u
            total_flow += path_flow
        return total_flow


# ================================================================
# 5. Burrows-Wheeler Transform
# ================================================================

def bwt_encode(s: str) -> str:
    """Burrows-Wheeler Transform.
    Append sentinel '$', sort all rotations, return last column.
    """
    s = s + '$'
    n = len(s)
    # Generate all rotation indices
    rotations = sorted(range(n), key=lambda i: s[i:] + s[:i])
    # Last column = char before each sorted rotation's first char
    last_col = ''.join(s[(i - 1) % n] for i in rotations)
    return last_col


def bwt_decode(encoded: str) -> str:
    """Inverse BWT using LF-mapping."""
    if not encoded:
        return ""
    n = len(encoded)
    # Build first column (sorted chars)
    first_col = sorted(encoded)
    # LF-mapping: for each char, rank in last col → position in first col
    # Count occurrences
    from collections import defaultdict
    rank = defaultdict(int)
    lf = [0] * n
    # next[] array: index in first col for each index in last col
    counts = {}
    for c in encoded:
        counts[c] = counts.get(c, 0) + 1
    # Compute cumulative starts
    starts = {}
    cumsum = 0
    for c in sorted(counts):
        starts[c] = cumsum
        cumsum += counts[c]
    # Build LF mapping
    char_count = defaultdict(int)
    for i in range(n):
        c = encoded[i]
        lf[i] = starts[c] + char_count[c]
        char_count[c] += 1
    # Walk from '$' (which is first in sorted)
    # Find '$' in encoded
    dollar_idx = encoded.index('$')
    result = []
    idx = dollar_idx
    for _ in range(n):
        idx = lf[idx]
        result.append(first_col[idx])
    return ''.join(reversed(result))


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 226: Graph Algorithms Demo")
    print("=" * 60)

    # --- 1. DFS / BFS ---
    print("\n📋 1. DFS & BFS")
    g = Graph(8)
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (4, 7), (5, 7)]
    for u, v in edges:
        g.add_edge(u, v)
    dfs_order = dfs(g, 0)
    bfs_order, dist = bfs(g, 0)
    print(f"   图: {edges}")
    print(f"   DFS from 0: {dfs_order}")
    print(f"   BFS from 0: {bfs_order}")
    print(f"   BFS 距离:   {dist}")

    # --- 2. Kruskal MST ---
    print("\n📋 2. Kruskal MST")
    n_nodes = 6
    mst_edges = [(7, 0, 1), (5, 0, 2), (8, 1, 2), (9, 1, 3),
                 (7, 2, 3), (5, 2, 4), (15, 3, 4), (6, 3, 5), (8, 4, 5),
                 (9, 0, 3)]
    mst = kruskal_mst(n_nodes, mst_edges)
    total = sum(w for w, _, _ in mst)
    print(f"   MST edges: {[(u, v, w) for w, u, v in mst]}")
    print(f"   MST 总权重: {total}")
    # Verify: all nodes connected
    uf = UnionFind(n_nodes)
    for w, u, v in mst:
        uf.union(u, v)
    print(f"   连通分量数: {uf.count} (应为 1)")

    # --- 3. Dijkstra ---
    print("\n📋 3. Dijkstra 最短路")
    adj = {
        0: [(1, 4), (2, 2)],
        1: [(2, 1), (3, 5)],
        2: [(1, 1), (3, 8), (4, 10)],
        3: [(4, 2)],
        4: [],
    }
    dists = dijkstra(5, adj, 0)
    print(f"   从节点 0 到各节点最短距离: {dists}")
    print(f"   最短路径 0→4: {dists[4]}")

    # --- 4. Ford-Fulkerson Max Flow ---
    print("\n📋 4. Ford-Fulkerson 最大流")
    fn = FlowNetwork(6)
    flow_edges = [(0, 1, 16), (0, 2, 13), (1, 2, 10), (2, 1, 4),
                  (1, 3, 12), (2, 4, 14), (3, 2, 9), (4, 3, 7),
                  (3, 5, 20), (4, 5, 4)]
    for u, v, c in flow_edges:
        fn.add_edge(u, v, c)
    max_flow = fn.max_flow(0, 5)
    print(f"   流网络边: {flow_edges}")
    print(f"   最大流 (0→5): {max_flow}")

    # --- 5. BWT ---
    print("\n📋 5. Burrows-Wheeler Transform")
    text = "banana"
    encoded = bwt_encode(text)
    decoded = bwt_decode(encoded)
    print(f"   原文:   '{text}'")
    print(f"   BWT编码: '{encoded}'")
    print(f"   BWT解码: '{decoded}'")
    print(f"   往返一致: {decoded == text + '$'}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    # BWT clustering effect
    text2 = "mississippi"
    enc2 = bwt_encode(text2)
    # Count consecutive runs
    runs = 1
    for i in range(1, len(enc2)):
        if enc2[i] != enc2[i - 1]:
            runs += 1
    print(f"   BWT('mississippi') = '{enc2}'")
    print(f"   编码后 run 数: {runs} (原文 {len(text2)} 字符)")
    print(f"   → BWT 把相同字符聚集，使后续 RLE + entropy coding 极高效")
    print(f"   → 这是 bzip2 比 gzip 压缩率高 20-40% 的核心原因")

    print("\n✅ COS 226 Algorithms Demo 完成！")


if __name__ == "__main__":
    demo()
