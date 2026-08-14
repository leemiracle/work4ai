"""
算法三校整合 — Princeton COS 226 × MIT 6.006 × CMU 15-251
==========================================================
三视角看算法（一个算法，三种钻法，互为补全）：

  Princeton COS 226 + Sedgewick《Algorithms 4ed》— 把【可视化】做到极致
       每个算法配交互 demo、排序动画、图算法路径追踪
       教材：Sedgewick & Wayne《Algorithms》4ed + algs4.cs.princeton.edu
       学完 → 脑中有"图"，能直觉地选对算法

  MIT 6.006 / 6.046                              — 把【数学严谨】做到极致
       Master theorem 求解递推、amortized analysis、贪心正确性证明
       教材：CLRS《Introduction to Algorithms》+ Erik Demaine 讲义
       学完 → 能严格证明复杂度、能做 amortized 分析

  CMU 15-251 (Great Ideas in CS)                 — 把【思想史】做到极致
       停机问题、Cantor 对角线、P vs NP、归约、零知识证明
       教材：Spielman 课程讲义
       学完 → 理解"什么是可计算的"、"什么是难解的"

整合维度（每个主题三视角对比）：
  1. 排序：可视化过程(Princeton) | Master theorem(MIT) | 信息论下界(CMU)
  2. 查找：BST 可视化(Princeton) | 平摊分析(MIT) | 哈希与生日悖论(CMU)
  3. 图：  BFS/Dijkstra 可视化(Princeton) | 贪心正确性证明(MIT) | NP 完全归约(CMU)
  4. 计算：—— | 渐近分析(MIT) | 停机问题 + P vs NP(CMU)

思想史脉络：
  1900 Hilbert 第十问题 → 1931 Gödel 不完备 → 1936 Turing 停机问题
  → 1971 Cook-Levin (NP 完全) → 1973 Karp (21 个 NPC 问题)
  → 1977 RSA (P≠NP 的实用证据) → 现代：算法 = 文明基础设施

运行：
    python3 algo_integration.py
依赖：仅标准库
==========================================================
"""
from __future__ import annotations
import math
import random
from collections import deque, defaultdict

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 0 · 算法思想史（CMU 15-251 灵魂）                                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

ALGO_HISTORY = [
    (1900, "Hilbert 第十问题", "丢番图方程是否有整数解？——'可判定性'问题首次浮现"),
    (1931, "🔴 Gödel 不完备定理", "任何足够强的形式系统都有'真但不可证'的命题——数学有边界"),
    (1936, "🔴 Turing 停机问题", "不存在通用程序能判断任意程序是否停机——计算的绝对极限"),
    (1936, "Turing Machine", "Turing 定义'可计算'的数学模型——所有算法的祖先"),
    (1945, "排序算法诞生", "Von Neumann 归并排序——第一个 O(n log n) 算法"),
    (1959, "Dijkstra / Shell", "最短路 + 希尔排序——'算法设计'成为独立学科"),
    (1965, "Hartmanis Stearns", "提出'计算复杂性'——O(n) vs O(n²) 成为科学问题"),
    (1971, "🔴 Cook-Levin 定理", "SAT 是 NP 完全的——P vs NP 千禧难题诞生"),
    (1973, "Karp 21 问题", "证明 21 个问题都 NP 完全——NPC 无处不在"),
    (1977, "Knuth TAOCP Vol3", "《Sorting and Searching》——算法成为工程圣经"),
    (1990, "Sedgewick《Algorithms》", "用可视化教算法——'看见'比'证明'更直觉"),
    (2000, "千禧大奖难题", "P vs NP 悬赏 100 万美元——至今无人证明"),
]


def print_history() -> None:
    print("=" * 74)
    print("  Part 0 · 算法思想史 —— 从 Hilbert 到 P vs NP")
    print("=" * 74)
    for year, title, desc in ALGO_HISTORY:
        star = "🔴" if "🔴" in title else "  "
        t = title.replace("🔴 ", "")
        print(f"  {star}{year}  {t}")
        print(f"       {desc}")
    print()
    print("  💡 主线：人类先问'什么能算'(可计算性) → 再问'算多快'(复杂性) →")
    print("        最终撞上'难解 vs 易解'(P vs NP) 这堵墙。算法 = 在这堵墙内尽量聪明。")
    print()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 1 · 排序三视角                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  Princeton : 可视化——用字符柱状图打印每一步，"看见"算法
#  MIT       : Master theorem——严格推导 T(n)=2T(n/2)+O(n) = O(n log n)
#  CMU 15-251: 信息论下界——比较排序最少 Ω(n log n)，证明"不可能更快"

def part1_sorting() -> None:
    print("=" * 74)
    print("  Part 1 · 排序三视角 —— 看见、证明、封顶")
    print("=" * 74)
    print("  Princeton : 可视化每一步（字符柱状图）")
    print("  MIT       : Master theorem 严格推导复杂度")
    print("  CMU 15-251: 信息论下界 Ω(n log n)——比较排序的天花板")
    print()

    # ----- Princeton 视角：可视化 -----
    print("─" * 74)
    print("【Princeton 视角】快排可视化：看见 partition 怎么动")
    print("─" * 74)
    arr = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    print(f"  初始: {arr}")
    print("  快排每次选 pivot，把小元素挪到左边：")
    qsort_visual(arr, 0, len(arr) - 1, depth=0)
    print(f"  最终: {arr}")
    print("  → Princeton 的核心：每个算法都配 algs4 标准库的可视化 demo，")
    print("    你在屏幕上'看见'数据流动，比读公式更快建立直觉。")
    print()

    # ----- MIT 视角：Master theorem -----
    print("─" * 74)
    print("【MIT 视角】Master theorem：归并排序为什么是 O(n log n)？")
    print("─" * 74)
    print("  归并排序递推：T(n) = 2·T(n/2) + O(n)")
    print("  Master theorem 形式：T(n) = a·T(n/b) + O(nᵈ)")
    print("    a=2 (分 2 子问题)  b=2 (每个规模 n/2)  d=1 (合并代价 O(n))")
    print("    关键：a vs bᵈ   →   2  vs  2¹ = 2")
    cases = [(1, "a < bᵈ", "T(n) = O(nᵈ)", "分治合并占主导，如 BST 查找"),
             (2, "a = bᵈ", "T(n) = O(nᵈ log n)", "平衡，如归并排序"),
             (3, "a > bᵈ", "T(n) = O(n^log_b(a))", "子问题太多，如朴素 Strassen")]
    print(f"  {'Case':<6} {'条件':<12} {'结论':<22} {'例子'}")
    for c, cond, concl, ex in cases:
        print(f"  {c:<6} {cond:<12} {concl:<22} {ex}")
    print("  → 归并排序 a=bᵈ=2，命中 Case 2：T(n) = O(n¹ log n) = O(n log n) ✓")
    print("  → MIT 教你：不用展开递归树，套公式就能秒算任何分治的复杂度。")
    print()

    # ----- CMU 视角：信息论下界 -----
    print("─" * 74)
    print("【CMU 视角】信息论下界：比较排序永远不可能比 O(n log n) 快")
    print("─" * 74)
    print("  证明（决策树论证）：")
    print("    n 个元素有 n! 种排列。比较排序 = 一棵决策树，每个叶 = 一种排列。")
    print("    树至少 n! 个叶 → 高度 h ≥ log₂(n!)")
    print("    Stirling: log₂(n!) ≈ n·log₂(n) − n·log₂(e) = Ω(n log n)")
    print()
    print(f"  {'n':>8} {'n!':>20} {'log₂(n!)':>14} {'n·log₂(n)':>12}")
    for n in [10, 100, 1000, 1000000]:
        log_fact = sum(math.log2(i) for i in range(1, n + 1))
        nlogn = n * math.log2(n)
        print(f"  {n:>8} {'(巨大)':>20} {log_fact:>14.1f} {nlogn:>12.1f}")
    print("  → 这是'不可能'定理：无论多聪明，基于比较的排序达不到 O(n log n) 以下。")
    print("  → 想更快？必须跳出'比较'框架（计数排序/基数排序，但要求特殊条件）。")
    print()


def qsort_visual(arr, lo, hi, depth=0):
    """Princeton 风格：快排 partition 可视化，每层缩进打印。"""
    if lo >= hi:
        return
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    bar = "  " + "  " * depth
    sub = arr[lo:hi + 1]
    print(f"{bar}pivot={pivot} → {sub}")
    qsort_visual(arr, lo, i - 1, depth + 1)
    qsort_visual(arr, i + 1, hi, depth + 1)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 2 · 查找三视角                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  Princeton : BST 可视化——树形打印，红黑树平衡过程
#  MIT       : 平摊分析——动态数组 append 为什么是 O(1) 均摊
#  CMU 15-251: 哈希与生日悖论——碰撞概率反直觉

def part2_searching() -> None:
    print("=" * 74)
    print("  Part 2 · 查找三视角 —— 树、均摊、碰撞")
    print("=" * 74)
    print("  Princeton : BST 可视化（树形打印）")
    print("  MIT       : 平摊分析（动态数组的 O(1) 均摊秘密）")
    print("  CMU 15-251: 哈希 + 生日悖论（碰撞概率反直觉）")
    print()

    # ----- Princeton 视角：BST 可视化 -----
    print("─" * 74)
    print("【Princeton 视角】BST 可视化：插入序列怎么长歪")
    print("─" * 74)
    bst = BST()
    for k in [50, 30, 70, 20, 40, 60, 80, 10]:
        bst.insert(k)
    print("  插入顺序: 50,30,70,20,40,60,80,10 → 树形结构：")
    bst.print_tree()
    print(f"  查找 40: {'找到 ✓' if bst.search(40) else '未找到'}  比较次数={bst.last_cmp}")
    print("  → 顺序插入会退化成链表（最坏 O(n)）；红黑树靠'旋转'自动保持平衡 O(log n)。")
    print()

    # ----- MIT 视角：平摊分析 -----
    print("─" * 74)
    print("【MIT 视角】平摊分析：动态数组 append 凭什么是 O(1)？")
    print("─" * 74)
    print("  Python list / Java ArrayList 满了就倍增容量。单次倍增 = O(n) 拷贝！")
    print("  但 n 次 append 的【总】代价 = O(n) → 每次【均摊】O(1)。怎么证？")
    print()
    print("  势能法 (potential method)：")
    print("    Φ(状态) = 2·size − capacity   （存'富余能量'）")
    print("    扩容时刻：size=capacity，扩容后 capacity'=2·capacity")
    print("    实际代价 O(n) + ΔΦ = O(n) + (2n − 2n) − (2n − n) = O(n) − n = O(1)")
    da = DynArray()
    total_copies = 0
    for i in range(100):
        total_copies += da.append(i)
    print(f"\n  实验：append 100 次，触发 {da.resizes} 次扩容，总拷贝 {total_copies} 次")
    print(f"  均摊每次 = {total_copies/100:.2f} 次操作 → 确实 O(1) ✓")
    print("  → MIT 教你：不要看最坏的单次，要看'序列的总代价均摊到每次'。")
    print()

    # ----- CMU 视角：生日悖论 -----
    print("─" * 74)
    print("【CMU 视角】哈希碰撞：生日悖论反直觉")
    print("─" * 74)
    print("  问题：N 个人的房间里，两人同生日概率达 50% 需要 N=?")
    print("  直觉：约 365/2 ≈ 180 人？错！")
    print()
    print(f"  {'人数 N':>8} {'至少一对同生日概率':>22}")
    for n in [5, 10, 15, 23, 30, 50, 70]:
        # P(无碰撞) = ∏(1 - i/365)
        p_no = 1.0
        for i in range(n):
            p_no *= (365 - i) / 365
        print(f"  {n:>8} {1-p_no:>22.2%}")
    print("  → 只需 23 人就有 50% 概率碰撞！这是 O(√m) 而非 O(m)。")
    print("  → 哈希表同理：10⁶ 个桶，插 ~1250 个键就有 50% 碰撞概率。")
    print("  → 所以哈希必须处理碰撞（链地址/开放寻址），不能假装不会撞。")
    print()


class BSTNode:
    __slots__ = ("key", "left", "right")
    def __init__(self, key):
        self.key = key
        self.left = self.right = None

class BST:
    """Princeton 风格：BST + 树形可视化打印。"""
    def __init__(self):
        self.root = None
        self.last_cmp = 0

    def insert(self, key):
        self.root = self._ins(self.root, key)

    def _ins(self, node, key):
        if node is None:
            return BSTNode(key)
        if key < node.key:
            node.left = self._ins(node.left, key)
        elif key > node.key:
            node.right = self._ins(node.right, key)
        return node

    def search(self, key):
        self.last_cmp = 0
        node = self.root
        while node:
            self.last_cmp += 1
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def print_tree(self):
        """竖向树形打印（根在左，叶在右）。"""
        self._print(self.root, "")

    def _print(self, node, prefix):
        if node is None:
            return
        self._print(node.right, prefix + "      ")
        print(f"  {prefix}─[{node.key}]")
        self._print(node.left, prefix + "      ")


class DynArray:
    """MIT 视角：动态数组，记录扩容次数和拷贝代价。"""
    def __init__(self):
        self.data = [None] * 1
        self.size = 0
        self.resizes = 0

    def append(self, val):
        copies = 0
        if self.size == len(self.data):
            new_data = [None] * (len(self.data) * 2)
            new_data[:self.size] = self.data[:self.size]
            copies = self.size
            self.data = new_data
            self.resizes += 1
        self.data[self.size] = val
        self.size += 1
        return copies


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 3 · 图算法三视角                                                  ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  Princeton : Dijkstra 可视化——每步打印当前最短路树生长
#  MIT       : 贪心正确性证明——Dijkstra 的 exchange argument
#  CMU 15-251: NP 完全——图着色问题与归约

def part3_graphs() -> None:
    print("=" * 74)
    print("  Part 3 · 图算法三视角 —— 最短路、正确性、难解性")
    print("=" * 74)
    print("  Princeton : Dijkstra 可视化（最短路树逐步生长）")
    print("  MIT       : 贪心正确性证明（为什么 Dijkstra 不会错）")
    print("  CMU 15-251: NP 完全（图着色——漂亮但难解）")
    print()

    # 图：A--B--C--D--E 网络
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"A": 4, "C": 1, "D": 5},
        "C": {"A": 2, "B": 1, "D": 8, "E": 10},
        "D": {"B": 5, "C": 8, "E": 2},
        "E": {"C": 10, "D": 2},
    }

    # ----- Princeton 视角：Dijkstra 可视化 -----
    print("─" * 74)
    print("【Princeton 视角】Dijkstra 可视化：从 A 出发，最短路树怎么长")
    print("─" * 74)
    dist, order = dijkstra(graph, "A")
    for step, (node, d) in enumerate(order):
        bar = "█" * max(1, int(d / 2))
        print(f"  Step {step+1}: 锁定 {node}  dist={d:<3} {bar}")
    print(f"\n  最终最短距离: {dict(sorted(dist.items()))}")
    print("  → Princeton 风格：可视化让你'看见'优先队列怎么一个个弹出最近点。")
    print()

    # ----- MIT 视角：贪心正确性 -----
    print("─" * 74)
    print("【MIT 视角】Dijkstra 正确性：贪心为什么不会错？")
    print("─" * 74)
    print("  定理：Dijkstra 每次锁定一个点 u 时，dist[u] 就是真正的最短距离。")
    print("  反证法 (exchange argument)：")
    print("    假设锁定时 dist[u] 不是最优，存在更短路径 A → ... → x → u")
    print("    因为边权非负，路径上一定有个点 y 还没锁定（dist[y] < dist[u]）")
    print("    但 Dijkstra 总选 dist 最小的未锁定点——矛盾！应该先选 y 才对。")
    print("    ∴ 假设不成立，dist[u] 必是最优。■")
    print("  ⚠️ 关键前提：边权 ≥ 0。有负权时这个证明就崩了（需 Bellman-Ford）。")
    print("  → MIT 教你：每个贪心算法都要问'凭什么贪心是对的'，并用反证/交换论证。")
    print()

    # ----- CMU 视角：NP 完全 -----
    print("─" * 74)
    print("【CMU 视角】NP 完全：图着色——从 Dijkstra 到'算不动'")
    print("─" * 74)
    print("  3-着色问题：给图染色，相邻点不同色，能否只用 3 种颜色？")
    print("  复杂度：暴力 = 3ⁿ（n 个点每个 3 选择）——指数级，n=50 就算到宇宙尽头")
    print()
    print(f"  {'n (顶点)':>10} {'3ⁿ':>22}")
    for n in [10, 20, 30, 50, 100]:
        ops = 3 ** n
        print(f"  {n:>10} {ops:>22,}")
    print("  → 这是 NPC 问题：目前无多项式算法，P vs NP 的核心。")
    print("  → 实际工程用'近似算法'或'启发式'（贪心着色、模拟退火）求'够用'的解。")
    print("  → CMU 15-251 教你：识别 NPC，别浪费时间找精确解，转向近似/启发式。")
    print()


def dijkstra(graph, src):
    """Dijkstra：返回 (dist, 锁定顺序列表)。无 heapq 依赖，教学版线性选最小。"""
    dist = {v: math.inf for v in graph}
    dist[src] = 0
    visited = set()
    order = []
    while len(visited) < len(graph):
        u = min((v for v in graph if v not in visited),
                key=lambda v: dist[v])
        visited.add(u)
        order.append((u, dist[u]))
        for nb, w in graph[u].items():
            if nb not in visited:
                dist[nb] = min(dist[nb], dist[u] + w)
    return dist, order


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 4 · 计算理论（CMU 15-251 的灵魂）                                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part4_theory() -> None:
    print("=" * 74)
    print("  Part 4 · 计算理论 —— 算法的边界在哪里？")
    print("=" * 74)
    print()

    # 停机问题对角线
    print("─" * 74)
    print("【停机问题】不存在程序能判断任意程序是否停机（Turing 1936）")
    print("─" * 74)
    print("  对角线证明（反证法）：")
    print("    假设存在 Halt(P, x) 能判断程序 P 在输入 x 上是否停机。")
    print("    构造魔鬼程序 D(x):")
    print("        if Halt(x, x):   while True: pass   # 如果停机，就死循环")
    print("        else:            return              # 如果不停，就停")
    print("    问 D(D) 停不停？")
    print("      若停 → Halt(D,D)=True → D 死循环 → 矛盾")
    print("      若不停 → Halt(D,D)=False → D return → 矛盾")
    print("    ∴ Halt 不存在。这是计算的绝对边界。■")
    print("  → 意义：不是所有问题都能用算法解决。'能算'本身有数学边界。")
    print()

    # P vs NP
    print("─" * 74)
    print("【P vs NP】千禧难题：'验证答案'是否等于'找到答案'？")
    print("─" * 74)
    print("  P  = 多项式时间能【求解】的问题（排序、最短路、线性规划）")
    print("  NP = 多项式时间能【验证】答案的问题（数独、TSP、SAT）")
    print("  NPC = NP 里最难的（SAT、3-着色、TSP、子集和…），互相可归约")
    print()
    print("  核心疑问：P = NP 吗？（即：能快速验证 = 能快速求解？）")
    print("  业界共识：P ≠ NP（否则密码学崩塌、创造力可被自动化）")
    print("  但 60 年无人能证明——这就是 100 万美元悬赏的千禧难题。")
    print()
    print("  实用启示：遇到 NPC 问题，别找精确解，用：")
    print("    ① 近似算法（保证误差范围，如 TSP 的 1.5× 近似）")
    print("    ② 启发式（不保证质量，如模拟退火、遗传算法）")
    print("    ③ 参数化/固定参数可解（n 大但关键参数小时有戏）")
    print()

    # Cantor 对角线
    print("─" * 74)
    print("【Cantor 对角线】无穷也有大小——实数比自然数'更多'")
    print("─" * 74)
    print("  自然数 N = {0,1,2,...} 可数无穷 ℵ₀")
    print("  实数 R 不可数 —— 对角线证明：")
    print("    假设 (0,1) 区间实数能和自然数一一对应，列出：")
    print("      r₁ = 0.a₁₁ a₁₂ a₁₃ ...")
    print("      r₂ = 0.a₂₁ a₂₂ a₂₃ ...")
    print("      r₃ = 0.a₃₁ a₃₂ a₃₃ ...")
    print("    构造 d = 0.(1-a₁₁)(1-a₂₂)(1-a₃₃)...  ← 取对角线取反")
    print("    d 不等于任何一个 rᵢ（第 i 位不同）——矛盾！列表不全。■")
    print("  → 这套'对角线'技巧后来被 Turing/Gödel 反复用来证明'边界'。")
    print("  → 算法能处理的，永远是可数无穷（程序本身可编号）。连续世界靠数值近似。")
    print()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 5 · 三校能力地图 + 学习路径                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part5_capability() -> None:
    print("=" * 74)
    print("  Part 5 · 三校能力地图 —— 学完你能做什么？")
    print("=" * 74)
    rows = [
        ("Princeton COS 226", "可视化派", "脑中有图，直觉选对算法",
         "algs4 全套可视化 + 4 个 project", "★★★★☆"),
        ("MIT 6.006/6.046",   "严谨派",   "严格证明复杂度、做平摊分析",
         "CLRS 习题 + Erik Demaine 手写推导", "★★★★★"),
        ("CMU 15-251",        "思想派",   "识别 NPC、理解计算边界",
         "对角线证明 + 归约练习", "★★★★★"),
    ]
    print(f"  {'课程':<20} {'流派':<8} {'学完能力':<26} {'关键动作':<26} {'难度'}")
    print("  " + "─" * 72)
    for c, s, ab, act, d in rows:
        print(f"  {c:<20} {s:<8} {ab:<26} {act:<26} {d}")
    print()
    print("  🎯 整合学习路径（4 周速成）：")
    print("     Week 1: Princeton COS 226（看 algs4 可视化 + 实现排序/查找）")
    print("     Week 2: MIT 6.006（CLRS 递推分析 + 平摊分析 + 贪心证明）")
    print("     Week 3: 图算法（Dijkstra/MST + 正确性证明 + 可视化）")
    print("     Week 4: CMU 15-251（停机问题 + P vs NP + NPC 归约）")
    print()
    print("  📚 对应教材：")
    print("     • Sedgewick《Algorithms 4ed》— Princeton，可视化圣经")
    print("     • CLRS《Introduction to Algorithms》— MIT，严谨百科全书")
    print("     • Spielman 15-251 讲义 — CMU，思想史脉络")
    print()


def main() -> None:
    print()
    print("╔" + "═" * 72 + "╗")
    print("║" + " 算法三校整合 · Princeton COS 226 × MIT 6.006 × CMU 15-251 ".center(72) + "║")
    print("╚" + "═" * 72 + "╝")
    print()
    print_history()
    part1_sorting()
    part2_searching()
    part3_graphs()
    part4_theory()
    part5_capability()
    print("=" * 74)
    print("  ✅ 全部演示完成。下一步：")
    print("     1. 跑数据库整合对照：python3 database-systems/db_integration.py")
    print("     2. 按 Part 5 的 4 周路径，从 Princeton 可视化入门。")
    print("     3. 想深入某主题，告诉我（如'红黑树怎么旋转''NP 归约怎么做'）。")
    print("=" * 74)
    print()


if __name__ == "__main__":
    main()
