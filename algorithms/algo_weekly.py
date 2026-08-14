"""
算法 4 周实战练习册 —— 把 algo_integration.py 的理论变成可跑的练习
====================================================================
配合 algorithms/algo_integration.py 食用。

  Week 1 · Princeton COS 226 —— 可视化练手（排序对决 + BST 树高）
  Week 2 · MIT 6.006         —— CLRS 证明（Master 定理 + 平摊分析 + 贪心）
  Week 3 · 图算法            —— Dijkstra 路径还原 + Kruskal MST + 拓扑排序
  Week 4 · CMU 15-251        —— 计算理论（归约 + 近似算法 + 停机悖论）

每周末有 ✍️ 自测题，跑通代码 + 答对自测 = 过关。

运行：
    python3 algo_weekly.py
依赖：仅标准库
====================================================================
"""
from __future__ import annotations
import math
import random
from collections import defaultdict, deque

def banner(title):
    print("\n" + "█" * 74)
    print(f"  {title}")
    print("█" * 74)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 1 · Princeton —— 可视化练手                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week1_visual() -> None:
    banner("Week 1 · Princeton COS 226 —— 可视化练手：排序对决 + BST 树高")

    print("""
  目标：用"看见"建立直觉。Princeton 的核心信条——可视化 > 公式。
""")

    # ── 练习 1：排序对决 ──
    print("─" * 74)
    print("【练习 1】排序算法对决：比较次数 & 交换次数实测")
    print("─" * 74)
    random.seed(42)
    data = [random.randint(1, 999) for _ in range(20)]
    print(f"  输入（20 个随机数）: {data}\n")

    candidates = [
        ("冒泡排序 bubble", bubble_sort, "O(n²)"),
        ("插入排序 insertion", insertion_sort, "O(n²)"),
        ("归并排序 merge", merge_sort, "O(n log n)"),
        ("快速排序 quick", quick_sort_count, "O(n log n)"),
    ]
    print(f"  {'算法':<20} {'比较次数':>10} {'交换/移动':>12} {'理论复杂度'}")
    print("  " + "─" * 60)
    for name, fn, complexity in candidates:
        comps, moves = fn(list(data))
        print(f"  {name:<20} {comps:>10} {moves:>12}  {complexity}")
    print("""
  → n=20 时冒泡 190 次 vs 归并 65 次；n=1000 时差距会到 ~500000 vs ~10000。
  → 渐近优势在小数据看不出，数据越大 O(n²) 和 O(n log n) 的鸿沟越明显。
  → Princeton algs4 库有 StdDraw 实时画柱状图动画，这里用计数代替。
""")

    # ── 练习 2：BST 树高对决 ──
    print("─" * 74)
    print("【练习 2】BST 树高：随机插入 vs 顺序插入，差多少？")
    print("─" * 74)
    keys_random = list(range(1, 32))
    random.shuffle(keys_random)
    keys_sorted = list(range(1, 32))

    h_rand = bst_height(keys_random)
    h_sort = bst_height(keys_sorted)
    ideal = math.floor(math.log2(32))   # 完美平衡高度
    print(f"  31 个节点（1..31）：")
    print(f"    随机顺序插入 → 树高 = {h_rand}  （接近理想 {ideal}）")
    print(f"    已排序插入   → 树高 = {h_sort}  （退化为链表！）")
    print(f"    完美平衡高度 → {ideal}")
    print(f"""
  → 顺序插入让 BST 退化成链表，查找从 O(log n) 恶化到 O(n)！
  → 这就是为什么需要【平衡树】（红黑树/AVL）：插入后自动旋转，保证 h=O(log n)。
  → 红黑树性质：任意路径不超过最短路径 2 倍 → h ≤ 2·log₂(n+1)。
""")

    print("─" * 74)
    print("  ✍️ W1 自测题：")
    print("     Q1: 快排在【已排序】数据上表现如何？为什么 algs4 要 shuffle？")
    print("         (提示：每次 pivot 都是最小值，退化为 O(n²))")
    print("     Q2: 红黑树的 5 条性质里，哪一条直接保证 h=O(log n)？")
    print("─" * 74)


# ── 排序算法（带计数）─────────────────────────────────────────────────────
def bubble_sort(a):
    comps = moves = 0
    a = list(a)
    for i in range(len(a)):
        for j in range(len(a) - 1 - i):
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                moves += 1
    return comps, moves

def insertion_sort(a):
    comps = moves = 0
    a = list(a)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comps += 1
            if a[j] > key:
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return comps, moves

def merge_sort(a):
    comps = moves = 0
    a = list(a)
    def ms(arr):
        nonlocal comps, moves
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left, right = ms(arr[:mid]), ms(arr[mid:])
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            comps += 1
            if left[i] <= right[j]:
                merged.append(left[i]); i += 1
            else:
                merged.append(right[j]); j += 1
            moves += 1
        merged.extend(left[i:]); merged.extend(right[j:])
        moves += len(left) - i + len(right) - j
        return merged
    ms(a)
    return comps, moves

def quick_sort_count(a):
    comps = moves = 0
    def qs(arr):
        nonlocal comps, moves
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        less, equal, greater = [], [], []
        for x in arr:
            comps += 1
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            else:
                greater.append(x)
        moves += len(arr)
        return qs(less) + equal + qs(greater)
    qs(list(a))
    return comps, moves


# ── BST 树高 ─────────────────────────────────────────────────────────────
def bst_height(keys):
    class N:
        __slots__ = ("k", "l", "r")
        def __init__(self, k): self.k, self.l, self.r = k, None, None
    root = None
    for k in keys:
        if root is None:
            root = N(k); continue
        node = root
        while True:
            if k < node.k:
                if node.l is None: node.l = N(k); break
                node = node.l
            elif k > node.k:
                if node.r is None: node.r = N(k); break
                node = node.r
            else: break
    def height(n):
        if n is None: return 0
        return 1 + max(height(n.l), height(n.r))
    return height(root)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 2 · MIT 6.006 —— CLRS 证明练习                                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week2_proofs() -> None:
    banner("Week 2 · MIT 6.006 —— CLRS 证明：Master 定理 + 平摊 + 贪心")

    print("""
  目标：把"我猜是 O(n log n)"变成"我证明是 O(n log n)"。
""")

    # ── 练习 1：Master 定理求解器 ──
    print("─" * 74)
    print("【练习 1】Master 定理求解器：套公式秒算分治复杂度")
    print("─" * 74)
    cases = [
        ("归并排序", 2, 2, 1, "a=bᵈ=2", "O(n log n)"),
        ("二分查找", 1, 2, 0, "a=bᵈ=1", "O(log n)"),
        ("Strassen 矩阵乘", 7, 2, 2, "a=7 > bᵈ=4", "O(n^log₂7)≈O(n^2.81)"),
        ("朴素矩阵乘", 8, 2, 2, "a=bᵈ=8", "O(n^3)"),
        ("Karatsuba 乘法", 3, 2, 1, "a=3 > bᵈ=2", "O(n^log₂3)≈O(n^1.58)"),
    ]
    print("  T(n) = a·T(n/b) + O(nᵈ)，比较 a 与 bᵈ:")
    print(f"  {'算法':<18} {'a':>3} {'b':>3} {'d':>3}  {'判定':<14} {'结论'}")
    print("  " + "─" * 56)
    for name, a, b, d, judge, concl in cases:
        print(f"  {name:<18} {a:>3} {b:>3} {d:>3}  {judge:<14} {concl}")
    print("""
  → 规则：a < bᵈ → O(nᵈ)；a = bᵈ → O(nᵈ log n)；a > bᵈ → O(n^log_b a)
  → MIT Erik Demaine 强调：递归树画出来，看'每层总工作量'的变化趋势即可。
""")

    # ── 练习 2：平摊分析实验 ──
    print("─" * 74)
    print("【练习 2】平摊分析实验：MULTIPOP 的 O(1) 均摊")
    print("─" * 74)
    print("  栈操作：PUSH=O(1), POP=O(1), MULTIPOP(k)=O(min(k,s)) 单次最坏 O(n)")
    print("  但 n 次任意操作【总】代价 = O(n) → 均摊 O(1)。怎么证？")
    stack = []
    total_ops = 0
    random.seed(7)
    for _ in range(1000):
        op = random.choice(["push", "push", "push", "pop", "multipop"])
        if op == "push":
            stack.append(random.randint(0, 99)); total_ops += 1
        elif op == "pop":
            if stack: stack.pop()
            total_ops += 1
        else:  # multipop
            k = random.randint(1, 5)
            popped = min(k, len(stack))
            for _ in range(popped): stack.pop()
            total_ops += popped   # multipop 实际代价 = 弹出元素数
    print(f"  1000 次混合操作，实际总代价 = {total_ops}")
    print(f"  均摊每次 = {total_ops/1000:.2f} → 远小于最坏估计，确为 O(1) ✓")
    print("""  势能法证明：Φ = 栈中元素数
    PUSH: 实际 1 + ΔΦ(+1) = 2  → 均摊 O(1)
    POP:  实际 1 + ΔΦ(-1) = 0  → 均摊 O(1)
    MULTIPOP(k): 实际 min(k,s) + ΔΦ(-min(k,s)) = 0 → 均摊 O(1)
  → 每个操作均摊 O(1)，n 次总计 O(n)。单次最坏的恐慌被势能消化。
""")

    # ── 练习 3：贪心正确性 ──
    print("─" * 74)
    print("【练习 3】活动选择：贪心为什么对？")
    print("─" * 74)
    activities = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
                  (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
    chosen = activity_selection(activities)
    print(f"  11 个活动（start, end）: {activities}")
    print(f"  贪心选（按 end 排序，每次选最早结束）: {chosen}")
    print(f"  共选 {len(chosen)} 个互不冲突活动")
    print("""  正确性证明（交换论证）：
    设最优解 OPT 选了活动 o₁,o₂,...，贪心选 g₁,g₂,...
    关键：g₁.end ≤ o₁.end（贪心选最早结束的）
    ∴ 用 g₁ 替换 o₁ 不冲突，OPT 剩下的问题仍是原问题子集
    归纳：贪心每步都能"对齐"最优 → 贪心 = 最优 ■
""")

    print("─" * 74)
    print("  ✍️ W2 自测题：")
    print("     Q1: T(n) = 4T(n/2) + O(n² log n)，套 Master 定理得什么？")
    print("         (提示：a=4, bᵈ=2²=4，a=bᵈ → Case 2 变体)")
    print("     Q2: 为什么'平摊分析'不能用于最坏情况保证？什么场景才适用？")
    print("─" * 74)


def activity_selection(acts):
    """贪心活动选择：按结束时间排序，每次选最早结束且不冲突的。"""
    acts = sorted(acts, key=lambda x: x[1])
    chosen, last_end = [], -math.inf
    for s, e in acts:
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 3 · 图算法实战                                                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week3_graphs() -> None:
    banner("Week 3 · 图算法实战：Dijkstra 路径还原 + Kruskal MST + 拓扑排序")

    print("""
  目标：不只是求出答案，还要【还原路径】【证明正确】。
""")
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"A": 4, "C": 1, "D": 5},
        "C": {"A": 2, "B": 1, "D": 8, "E": 10},
        "D": {"B": 5, "C": 8, "E": 2},
        "E": {"C": 10, "D": 2},
    }

    # ── 练习 1：Dijkstra + 路径还原 ──
    print("─" * 74)
    print("【练习 1】Dijkstra + 路径还原：不只给距离，还原怎么走")
    print("─" * 74)
    dist, prev, order = dijkstra_with_path(graph, "A")
    print("  从 A 出发的最短路：")
    for node in sorted(dist, key=lambda v: dist[v]):
        path = reconstruct(prev, "A", node)
        path_str = " → ".join(path) if path else "(无路径)"
        print(f"    A → {node}: dist={dist[node]:<3}  路径: {path_str}")
    print("""
  → 关键：维护 prev[] 数组记录"从哪来"，终点回溯即得路径。
  → 这就是导航软件（Google Maps）的核心算法（+ A* 启发式优化）。
""")

    # ── 练习 2：Kruskal MST ──
    print("─" * 74)
    print("【练习 2】Kruskal 最小生成树：并查集防止成环")
    print("─" * 74)
    edges = [
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 1),
        ("B", "D", 5), ("C", "D", 8), ("C", "E", 10), ("D", "E", 2),
    ]
    mst, total = kruskal(edges)
    print(f"  所有边（按权排序）: {sorted(edges, key=lambda e: e[2])}")
    print(f"  MST 选边: {mst}")
    print(f"  总权重 = {total}")
    print("""
  → Kruskal：边按权排序，逐条加入，若两端已连通（并查集 Find）则跳过（会成环）。
  → 正确性（cut 性质）：每条被选的边都是某割的最小横跨边 → 必在某 MST 中。
""")

    # ── 练习 3：拓扑排序 ──
    print("─" * 74)
    print("【练习 3】拓扑排序：课程依赖怎么排课")
    print("─" * 74)
    deps = {
        "数据结构": [], "算法": ["数据结构"],
        "数据库": ["数据结构"], "OS": ["数据结构"],
        "分布式": ["OS", "数据库"], "ML": ["算法", "线性代数"],
        "线性代数": [], "深度学习": ["ML"],
    }
    order = topo_sort(deps)
    print(f"  课程依赖图: {deps}")
    print(f"  拓扑序（合法修课顺序）: {' → '.join(order)}")
    print("""
  → Kahn 算法：反复找入度=0 的点输出，删除其出边，重复。
  → 若输出节点数 < 总节点数 → 图有环，存在循环依赖（无法排课）。
  → 实战：make/build 系统、npm 依赖解析、任务调度都是拓扑排序。
""")

    print("─" * 74)
    print("  ✍️ W3 自测题：")
    print("     Q1: 有负权边时 Dijkstra 会出错，错在哪一步？该用哪个算法？")
    print("         (提示：负权破坏'锁定即最优'的贪心前提 → Bellman-Ford)")
    print("     Q2: Prim 和 Kruskal 求 MST，哪个更适合稠密图？为什么？")
    print("─" * 74)


def dijkstra_with_path(graph, src):
    dist = {v: math.inf for v in graph}
    dist[src] = 0
    prev = {v: None for v in graph}
    visited = set()
    order = []
    while len(visited) < len(graph):
        u = min((v for v in graph if v not in visited), key=lambda v: dist[v])
        visited.add(u)
        order.append(u)
        for nb, w in graph[u].items():
            if nb not in visited and dist[u] + w < dist[nb]:
                dist[nb] = dist[u] + w
                prev[nb] = u
    return dist, prev, order

def reconstruct(prev, src, dst):
    path = []
    cur = dst
    while cur is not None:
        path.append(cur)
        if cur == src:
            break
        cur = prev[cur]
    return list(reversed(path)) if path and path[-1] == src else []

def kruskal(edges):
    """Kruskal MST：边排序 + 并查集。"""
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(a, b):
        parent[find(a)] = find(b)

    edges_sorted = sorted(edges, key=lambda e: e[2])
    mst, total = [], 0
    for u, v, w in edges_sorted:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, w))
            total += w
    return mst, total

def topo_sort(graph):
    """Kahn 拓扑排序：入度法。"""
    in_deg = {n: 0 for n in graph}
    for n, deps in graph.items():
        for d in deps:
            in_deg[n] = in_deg.get(n, 0)
    for n, deps in graph.items():
        for d in deps:
            in_deg[n] += 1
    queue = deque([n for n in graph if in_deg[n] == 0])
    order = []
    while queue:
        n = queue.popleft()
        order.append(n)
        for m, deps in graph.items():
            if n in deps:
                in_deg[m] -= 1
                if in_deg[m] == 0:
                    queue.append(m)
    return order


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 4 · CMU 15-251 —— 计算理论                                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week4_theory() -> None:
    banner("Week 4 · CMU 15-251 —— 计算理论：归约 + 近似 + 停机悖论")

    print("""
  目标：理解"什么是难解的"，学会归约与近似，直面计算的边界。
""")

    # ── 练习 1：NPC 归约 ──
    print("─" * 74)
    print("【练习 1】归约演示：独立集 ↔ 顶点覆盖（互补关系）")
    print("─" * 74)
    # 图：A-B, B-C, C-D, A-C
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("A", "C")]
    print(f"  图 G: 节点 {nodes}, 边 {edges}")
    print("  定理：S 是独立集 ⟺ V\\S 是顶点覆盖")
    print("     独立集：任意两点无边相连")
    print("     顶点覆盖：每条边至少一端在集合中")
    print()
    # 验证：S={B,D} 是独立集？
    from itertools import combinations
    for size in [2]:
        for S in combinations(nodes, size):
            S_set = set(S)
            cover = set(nodes) - S_set
            is_indep = all(not (u in S_set and v in S_set) for u, v in edges)
            is_cover = all(u in cover or v in cover for u, v in edges)
            if is_indep:
                print(f"    S={S} 是独立集 ⟺ V\\S={sorted(cover)} 是顶点覆盖? {is_cover} ✓")
    print("""
  → 归约意义：如果独立集难解，顶点覆盖也难解（反之亦然）。
  → NPC 证明套路：拿一个已知 NPC 问题，多项式归约到你的问题。
""")

    # ── 练习 2：近似算法 ──
    print("─" * 74)
    print("【练习 2】Vertex Cover 近似：2-近似算法（贪心取边）")
    print("─" * 74)
    cover = vc_approx(edges)
    print(f"  图边 {edges}")
    print(f"  贪心近似顶点覆盖 = {sorted(cover)}（大小 {len(cover)}）")
    print("""
  算法：每次任取一条未覆盖边，把【两端都】加入覆盖，删所有关联边。
  近似比证明：每取一条边，最优解中至少一个端点在该边上 → 取两端顶多 2 倍最优。
  → 这里取了 4 个点，但最优可能只要 2 个（如 {B,C}）——正是 2-近似"可能多取"的体现。
  → 面对 NPC，不追求精确，追求'保证误差范围'的近似。这是工程智慧。
""")

    # ── 练习 3：停机悖论 ──
    print("─" * 74)
    print("【练习 3】停机悖论：如果 Halt 函数存在，世界会矛盾")
    print("─" * 74)
    print("""  假设能写出一个函数：
    def halts(program, input):
        return True if program(input) 会停 else False

  那就能构造魔鬼程序：
    def devil(x):
        if halts(x, x):       # 如果 x(x) 会停
            while True: pass   # 就死循环
        else:
            return             # 否则就停

  问：devil(devil) 停不停？
    若停 → halts(devil,devil)=True → devil 死循环 → 矛盾
    若不停 → halts(devil,devil)=False → devil 返回 → 矛盾

  结论：halts 函数【不可能存在】。这是计算的绝对边界。
  → 这不是工程问题，是数学定理。无论计算机多强大，都跨不过这道坎。
""")
    # 实际"运行"devil 的演示（会无限循环，这里只打印说明）
    print("  （devil(devil) 无法真正运行——这就是悖论的力量）")
    print()

    print("─" * 74)
    print("  ✍️ W4 自测题：")
    print("     Q1: 把 3-SAT 归约到独立集，核心思路是什么？")
    print("         (提示：每个变量赋值造两点，冲突 clause 用边连接)")
    print("     Q2: P=NP 被证明为真，会对 RSA 密码造成什么影响？")
    print("─" * 74)


def vc_approx(edges):
    """Vertex Cover 2-近似：贪心取边两端。"""
    cover = set()
    remaining = list(edges)
    while remaining:
        u, v = remaining[0]
        cover.add(u); cover.add(v)
        remaining = [(a, b) for a, b in remaining
                     if a not in cover and b not in cover]
    return cover


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  主入口                                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

def main() -> None:
    print()
    print("╔" + "═" * 72 + "╗")
    print("║" + " 算法 4 周实战练习册 · 把理论变成手感 ".center(72) + "║")
    print("╚" + "═" * 72 + "╝")
    week1_visual()
    week2_proofs()
    week3_graphs()
    week4_theory()
    print("\n" + "=" * 74)
    print("  🎓 4 周通关检查表：")
    print("     □ W1: 实测过排序比较次数，理解 BST 退化为链表的危害")
    print("     □ W2: 会套 Master 定理，能解释平摊分析为什么 O(1)")
    print("     □ W3: 手写过 Dijkstra 路径还原 + Kruskal MST + 拓扑排序")
    print("     □ W4: 懂 NPC 归约套路，能给 NPC 问题写近似算法")
    print("=" * 74)
    print()


if __name__ == "__main__":
    main()
