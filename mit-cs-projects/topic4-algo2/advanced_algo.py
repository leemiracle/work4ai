"""
6.1220/6.046 Design and Analysis of Algorithms（MIT）
================================================
覆盖主题：
- 最大流：Ford-Fulkerson + Edmonds-Karp BFS（Lecture 6-7）
- FFT：Cooley-Tukey 蝶形算法（Lecture 11）
- 随机化：Quickselect 期望线性选择（Lecture 9）
- 近似/并查集应用（Lecture 4）

核心教材/论文（经典，无 arXiv ID）：
- Cormen et al. (CLRS) 4th ed, Ch 26 Max Flow, Ch 30 FFT
- Ford & Fulkerson 1956 "Maximal Flow through a Network" Canadian J Math
- Cooley & Tukey 1965 "An Algorithm for the Machine Calculation of Complex Fourier Series" Math Comp
- Hoare 1961 "Algorithm 65: Find" Comm ACM (quickselect)
- Edmonds & Karp 1972 "Theoretical Improvements in Algorithmic Efficiency for Network Flow Problems" JACM

本文件实现：
- Ford-Fulkerson (BFS = Edmonds-Karp) 最大流
- Cooley-Tukey FFT + 多项式乘法
- Randomized Quickselect
- Union-Find 进阶（离线连通性查询）

运行：
    python advanced_algo.py
"""
from __future__ import annotations
import cmath
import math
import random


# ============ 1. 最大流 Ford-Fulkerson (Edmonds-Karp) ============

def build_residual(edges: list[tuple]) -> dict:
    """构建残量图。edges = [(u, v, cap), ...]"""
    cap = {}
    adj = {}
    nodes = set()
    for u, v, c in edges:
        cap[(u, v)] = cap.get((u, v), 0) + c
        cap[(v, u)] = cap.get((v, u), 0)  # 反向边初始 0
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
        nodes.add(u); nodes.add(v)
    return cap, adj, nodes


def bfs_augmenting(cap, adj, src, sink):
    """BFS 找增广路（Edmonds-Karp）。返回 (path, bottleneck)。"""
    visited = {src}
    queue = [(src, [src], float('inf'))]
    while queue:
        u, path, flow = queue.pop(0)
        for v in adj.get(u, []):
            if v not in visited and cap.get((u, v), 0) > 0:
                new_flow = min(flow, cap[(u, v)])
                new_path = path + [v]
                if v == sink:
                    return new_path, new_flow
                visited.add(v)
                queue.append((v, new_path, new_flow))
    return None, 0


def max_flow(edges, src, sink) -> tuple[int, list]:
    """Ford-Fulkerson (Edmonds-Karp BFS)。返回 (最大流, 每轮记录)。"""
    cap, adj, nodes = build_residual(edges)
    total = 0
    history = []
    while True:
        path, bottleneck = bfs_augmenting(cap, adj, src, sink)
        if not path:
            break
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            cap[(u, v)] -= bottleneck
            cap[(v, u)] += bottleneck
        total += bottleneck
        history.append((path[:], bottleneck))
    return total, history


# ============ 2. FFT Cooley-Tukey ============

def fft(a: list[complex], invert: bool = False) -> list[complex]:
    """递归 Cooley-Tukey FFT。len(a) 必须是 2 的幂。O(n log n)。"""
    n = len(a)
    if n == 1:
        return a[:]
    # 分奇偶
    even = fft(a[0::2], invert)
    odd = fft(a[1::2], invert)
    angle = (2 * math.pi / n) * (1 if invert else -1)
    w_n = cmath.exp(1j * angle)
    w = 1
    result = [0] * n
    half = n // 2
    for k in range(half):
        t = w * odd[k]
        result[k] = even[k] + t
        result[k + half] = even[k] - t
        if invert:
            result[k] /= 2
            result[k + half] /= 2
        w *= w_n
    return result


def fft_multiply(poly1: list[float], poly2: list[float]) -> list[int]:
    """FFT 多项式乘法。返回系数（整数截断）。O(n log n)。"""
    n = 1
    while n < len(poly1) + len(poly2) - 1:
        n <<= 1
    a = [complex(x, 0) for x in poly1] + [0] * (n - len(poly1))
    b = [complex(x, 0) for x in poly2] + [0] * (n - len(poly2))
    fa = fft(a)
    fb = fft(b)
    fc = [fa[i] * fb[i] for i in range(n)]
    res = fft(fc, invert=True)
    return [int(round(res[i].real)) for i in range(len(poly1) + len(poly2) - 1)]


# ============ 3. Randomized Quickselect ============

def quickselect(arr: list, k: int) -> any:
    """期望 O(n) 选择第 k 小元素（k 从 0 开始）。"""
    arr = arr[:]
    return _qs(arr, k)


def _qs(arr, k):
    if len(arr) == 1:
        return arr[0]
    pivot = random.choice(arr)
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]
    if k < len(lows):
        return _qs(lows, k)
    elif k < len(lows) + len(pivots):
        return pivot
    else:
        return _qs(highs, k - len(lows) - len(pivots))


# ============ 4. Union-Find 进阶 ============

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.comps = n  # 连通分量数

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.comps -= 1
        return True

    def connected(self, a, b) -> bool:
        return self.find(a) == self.find(b)


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.046 Advanced Algorithms: Max-Flow / FFT / Quickselect / UF")
    print("=" * 65)
    random.seed(42)

    # --- Max Flow ---
    print("\n📋 1. 最大流 (Ford-Fulkerson / Edmonds-Karp)")
    # CLRS Fig 26.1 经典例
    edges = [('s','1',16),('s','2',13),('1','2',10),('2','1',4),
             ('1','3',12),('3','2',9),('2','4',14),('4','3',7),
             ('3','t',20),('4','t',4)]
    flow, hist = max_flow(edges, 's', 't')
    print(f"  网络 (CLRS 26.6 示例):")
    for p, b in hist:
        print(f"    增广路 {' → '.join(p)}  flow={b}")
    print(f"  最大流 = {flow} (CLRS 答案=23)")

    # --- FFT polynomial multiply ---
    print("\n📋 2. FFT 多项式乘法 (Cooley-Tukey)")
    p1 = [1, 2, 3]   # 1 + 2x + 3x^2
    p2 = [4, 5]       # 4 + 5x
    result = fft_multiply(p1, p2)
    naive = [0] * (len(p1) + len(p2) - 1)
    for i, a in enumerate(p1):
        for j, b in enumerate(p2):
            naive[i+j] += a * b
    print(f"  ({p1}) * ({p2})")
    print(f"  FFT:    {result}")
    print(f"  Naive:  {naive}")
    assert result == naive, "FFT 与朴素乘法结果应一致"
    # 大数乘法
    num1, num2 = 123, 4567
    prod = fft_multiply([int(d) for d in str(num1)[::-1]],
                        [int(d) for d in str(num2)[::-1]])
    carry = 0
    for i in range(len(prod)):
        carry, prod[i] = divmod(prod[i] + carry, 10)
    while carry:
        prod.append(carry % 10); carry //= 10
    big_result = int(''.join(map(str, prod[::-1])))
    print(f"  大数乘法 {num1} x {num2} = {big_result} (验证 {num1*num2})")

    # --- Quickselect ---
    print("\n📋 3. Randomized Quickselect")
    arr = [random.randint(1, 1000) for _ in range(50)]
    median = quickselect(arr, 25)
    sorted_arr = sorted(arr)
    print(f"  数组(前10): {arr[:10]}...")
    print(f"  Quickselect 第25小 = {median}")
    print(f"  排序验证第25个     = {sorted_arr[25]}")
    # 性能对比
    import time
    big = [random.randint(0, 10**6) for _ in range(10000)]
    t1 = time.perf_counter()
    m1 = quickselect(big, len(big)//2)
    t1 = time.perf_counter() - t1
    t2 = time.perf_counter()
    m2 = sorted(big)[len(big)//2]
    t2 = time.perf_counter() - t2
    print(f"  n=10000: quickselect {t1*1e6:.0f}μs vs sort {t2*1e6:.0f}μs (加速 {t2/t1:.1f}x)")

    # --- Union-Find ---
    print("\n📋 4. Union-Find 离线连通性")
    uf = UnionFind(10)
    unions = [(0,1),(2,3),(1,3),(4,5),(3,4)]
    queries = [(0,3),(0,5),(2,5),(6,7)]
    for a, b in unions:
        uf.union(a, b)
    print(f"  unions: {unions}")
    for a, b in queries:
        print(f"    connected({a},{b}) = {uf.connected(a,b)}")
    print(f"  连通分量数 = {uf.comps}")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：FFT 把 O(n^2) 多项式乘法降到 O(n log n)")
    print("=" * 65)
    sizes = [64, 128, 256, 512, 1024]
    for n in sizes:
        p1 = [random.randint(0, 9) for _ in range(n)]
        p2 = [random.randint(0, 9) for _ in range(n)]
        t1 = time.perf_counter()
        fft_multiply(p1, p2)
        t1 = time.perf_counter() - t1
        t2 = time.perf_counter()
        naive = [0]*(2*n-1)
        for i in range(n):
            for j in range(n):
                naive[i+j] += p1[i]*p2[j]
        t2 = time.perf_counter() - t2
        print(f"  n={n:>4}: FFT {t1*1e3:>7.2f}ms | naive {t2*1e3:>9.2f}ms | 加速 {t2/t1:>5.1f}x")
    print("  → n 越大优势越明显，FFT 的分治蝶形结构在大规模信号处理/")
    print("    大整数乘法(Schönhage–Strassen) 中是基石。")

    print("\n✅ 6.046 Demo 完成！")


if __name__ == "__main__":
    demo()
