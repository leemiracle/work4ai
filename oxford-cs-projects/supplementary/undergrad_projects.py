"""
Oxford CS 本科课程微项目集
覆盖：
- Functional Programming
- Imperative Programming I/II
- Object-oriented Programming
- Discrete Mathematics
- Probability
- Linear Algebra
- Continuous Mathematics
- Computer Architecture
- Computer Networks
- Operating Systems
"""
import math
import random
from collections import defaultdict


# ============ Functional Programming ============

def micro_fp_folds():
    """Functional Programming: fold/reduce + 柯里化"""
    print("\n📋 Functional Programming: fold")
    def foldl(f, acc, lst):
        if not lst:
            return acc
        return foldl(f, f(acc, lst[0]), lst[1:])

    def foldr(f, acc, lst):
        if not lst:
            return acc
        return f(lst[0], foldr(f, acc, lst[1:]))

    nums = [1, 2, 3, 4, 5]
    print(f"   {nums}")
    print(f"   foldl(+, 0) = {foldl(lambda a,b: a+b, 0, nums)}")
    print(f"   foldr(+, 0) = {foldr(lambda a,b: a+b, 0, nums)}")
    # foldl vs foldr with subtraction
    print(f"   foldl(-, 0) = {foldl(lambda a,b: a-b, 0, nums)}  # ((((0-1)-2)-3)-4)-5")
    print(f"   foldr(-, 0) = {foldr(lambda a,b: a-b, 0, nums)}  # 1-(2-(3-(4-(5-0))))")

    # 柯里化
    def curry(f):
        def curried(x):
            return lambda y: f(x, y)
        return curried

    add = lambda x, y: x + y
    add_curried = curry(add)
    inc = add_curried(1)
    print(f"   curry(add)(1)(2) = {inc(2)}")
    print(f"   → 柯里化: (A,B)→C ≅ A→(B→C) [Curry-Howard 的实践]")


# ============ Imperative Programming ============

def micro_imp_pointers():
    """Imperative Programming: 指针模拟 + 内存模型"""
    print("\n📋 Imperative Programming: 引用语义 vs 值语义")
    # Python list 是引用
    a = [1, 2, 3]
    b = a  # 引用拷贝
    b[0] = 99
    print(f"   a = [1,2,3], b = a, b[0]=99")
    print(f"   a = {a}, b = {b}  ← a 也变了（引用语义）")

    # 值拷贝
    c = list(a)  # 值拷贝
    c[0] = 0
    print(f"   c = list(a), c[0]=0")
    print(f"   a = {a}, c = {c}  ← a 没变（值语义）")

    # 链表
    class Node:
        def __init__(self, val, next=None):
            self.val = val
            self.next = next

    # 反转链表
    def reverse(head):
        prev = None
        while head:
            nxt = head.next
            head.next = prev
            prev = head
            head = nxt
        return prev

    head = Node(1, Node(2, Node(3)))
    reversed_head = reverse(head)
    vals = []
    cur = reversed_head
    while cur:
        vals.append(cur.val)
        cur = cur.next
    print(f"   反转链表 1→2→3: {'→'.join(map(str, vals))}")


# ============ Object-oriented Programming ============

def micro_oop_inheritance():
    """OOP: 继承 + 多态"""
    print("\n📋 Object-oriented Programming: 继承与多态")

    class Shape:
        def area(self):
            return 0
        def describe(self):
            return f"{self.__class__.__name__}: area={self.area():.2f}"

    class Circle(Shape):
        def __init__(self, r):
            self.r = r
        def area(self):
            return math.pi * self.r ** 2

    class Rectangle(Shape):
        def __init__(self, w, h):
            self.w = w
            self.h = h
        def area(self):
            return self.w * self.h

    class Triangle(Shape):
        def __init__(self, b, h):
            self.b = b
            self.h = h
        def area(self):
            return 0.5 * self.b * self.h

    shapes = [Circle(3), Rectangle(4, 5), Triangle(6, 3)]
    for s in shapes:
        print(f"   {s.describe()}")
    total = sum(s.area() for s in shapes)
    print(f"   总面积: {total:.2f}")
    print(f"   → 多态: 同一接口(area)，不同实现")


# ============ Discrete Mathematics ============

def micro_discrete_graph_coloring():
    """Discrete Math: 图着色"""
    print("\n📋 Discrete Mathematics: 图着色（贪心）")
    # 图：地图 = 邻接表
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'C', 'D'],
        'C': ['A', 'B', 'D'],
        'D': ['B', 'C', 'E'],
        'E': ['D'],
    }

    def greedy_color(g):
        colors = {}
        color_names = ['红', '绿', '蓝', '黄', '紫']
        for node in sorted(g.keys()):
            used = {colors[nb] for nb in g[node] if nb in colors}
            for c in color_names:
                if c not in used:
                    colors[node] = c
                    break
        return colors

    coloring = greedy_color(graph)
    for node, color in sorted(coloring.items()):
        print(f"   {node}: {color}")

    # 验证
    valid = all(coloring[n1] != coloring[n2] for n1 in graph for n2 in graph[n1])
    print(f"   合法着色: {valid}")
    print(f"   用了 {len(set(coloring.values()))} 种颜色")


# ============ Probability ============

def micro_prob_monty_hall():
    """Probability: 蒙提霍尔问题"""
    print("\n📋 Probability: Monty Hall 三门问题")
    random.seed(42)
    n_trials = 100000

    stay_wins = 0
    switch_wins = 0
    for _ in range(n_trials):
        prize = random.randint(0, 2)
        choice = random.randint(0, 2)
        # 主持人打开一扇没奖的门
        reveal = [d for d in range(3) if d != choice and d != prize][0]
        # 换门
        switch_choice = [d for d in range(3) if d != choice and d != reveal][0]
        if choice == prize:
            stay_wins += 1
        if switch_choice == prize:
            switch_wins += 1

    print(f"   {n_trials} 次模拟:")
    print(f"   不换门赢率: {stay_wins/n_trials:.3f} (理论 1/3)")
    print(f"   换门赢率:   {switch_wins/n_trials:.3f} (理论 2/3)")
    print(f"   → 换门赢率 ≈ 2× 不换！反直觉但正确")


# ============ Linear Algebra ============

def micro_linalg_eigen():
    """Linear Algebra: 特征值/特征向量（幂迭代）"""
    print("\n📋 Linear Algebra: 幂迭代求最大特征值")

    def mat_vec(A, x):
        return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]

    def dot(x, y):
        return sum(a * b for a, b in zip(x, y))

    A = [[2, 1], [1, 3]]
    x = [1.0, 1.0]
    for _ in range(50):
        Ax = mat_vec(A, x)
        norm = math.sqrt(dot(Ax, Ax))
        x = [v / norm for v in Ax]

    # Rayleigh 商
    eigenvalue = dot(x, mat_vec(A, x)) / dot(x, x)
    print(f"   A = {A}")
    print(f"   幂迭代 → 最大特征值 ≈ {eigenvalue:.4f} (真值 ≈ 3.618)")
    print(f"   特征向量 ≈ [{x[0]:.3f}, {x[1]:.3f}]")


# ============ Continuous Mathematics ============

def micro_continuous_newton():
    """Continuous Math: 牛顿法求根"""
    print("\n📋 Continuous Mathematics: 牛顿法")
    # 求 x² - 2 = 0（√2）
    def f(x):
        return x * x - 2
    def fp(x):
        return 2 * x

    x = 1.0
    for i in range(10):
        x_new = x - f(x) / fp(x)
        if abs(x_new - x) < 1e-10:
            break
        x = x_new

    print(f"   牛顿法求 √2:")
    print(f"   收敛于 x = {x:.10f} (迭代 {i+1} 次)")
    print(f"   误差: {abs(x - math.sqrt(2)):.2e}")
    print(f"   → 二次收敛：每步误差平方减小")


# ============ Computer Architecture ============

def micro_arch_pipeline():
    """Computer Architecture: 流水线模拟"""
    print("\n📋 Computer Architecture: 5 级流水线")
    instructions = ["IF", "ID", "EX", "MEM", "WB"]
    n = 8  # 8 条指令

    # 无流水线：每条指令 5 周期
    no_pipeline = n * 5

    # 有流水线：5 + (n-1) 周期
    pipeline = 5 + (n - 1)

    # 打印流水线图
    print(f"   {n} 条指令, 5 级流水线:")
    print(f"   无流水线: {no_pipeline} 周期")
    print(f"   有流水线: {pipeline} 周期 (加速比 {no_pipeline/pipeline:.1f}×)")

    # ASCII 流水线图（前 5 条指令）
    print("   流水线图:")
    for inst in range(min(5, n)):
        row = f"   I{inst}: "
        for cycle in range(inst, inst + 5):
            if cycle < 12:
                row += f"{instructions[cycle-inst]:>4s} "
        print(row)


# ============ Computer Networks ============

def micro_networks_routing():
    """Computer Networks: 距离向量路由"""
    print("\n📋 Computer Networks: 距离向量路由 (Bellman-Ford)")
    # 网络: A-B (1), A-C (4), B-C (2), B-D (5), C-D (1)
    links = {
        ('A', 'B'): 1, ('A', 'C'): 4,
        ('B', 'C'): 2, ('B', 'D'): 5,
        ('C', 'D'): 1,
    }
    nodes = ['A', 'B', 'C', 'D']

    # 初始化距离
    dist = {n: {m: (0 if n == m else float('inf')) for m in nodes} for n in nodes}
    for (a, b), w in links.items():
        dist[a][b] = w
        dist[b][a] = w

    # Bellman-Ford 迭代
    for _ in range(len(nodes)):
        for a in nodes:
            for b in nodes:
                for c in nodes:
                    if dist[a][b] > dist[a][c] + dist[c][b]:
                        dist[a][b] = dist[a][c] + dist[c][b]

    print(f"   网络拓扑: A-B(1), A-C(4), B-C(2), B-D(5), C-D(1)")
    print(f"   从 A 的最短距离:")
    for n in nodes:
        print(f"     A → {n}: {dist['A'][n]}")


# ============ Operating Systems ============

def micro_os_page_replacement():
    """OS: 页面替换算法"""
    print("\n📋 Operating Systems: 页面替换算法")
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frame_size = 3

    def fifo(refs, size):
        frames = []
        queue = []
        faults = 0
        for p in refs:
            if p not in frames:
                faults += 1
                if len(frames) < size:
                    frames.append(p)
                    queue.append(p)
                else:
                    old = queue.pop(0)
                    frames[frames.index(old)] = p
                    queue.append(p)
        return faults

    def lru(refs, size):
        frames = []
        recent = []
        faults = 0
        for p in refs:
            if p in frames:
                recent.remove(p)
                recent.append(p)
            else:
                faults += 1
                if len(frames) < size:
                    frames.append(p)
                    recent.append(p)
                else:
                    old = recent.pop(0)
                    frames[frames.index(old)] = p
                    recent.append(p)
        return faults

    def optimal(refs, size):
        frames = []
        faults = 0
        for i, p in enumerate(refs):
            if p not in frames:
                faults += 1
                if len(frames) < size:
                    frames.append(p)
                else:
                    # 找未来最远使用的页
                    farthest = -1
                    victim = frames[0]
                    for f in frames:
                        try:
                            next_use = refs[i+1:].index(f)
                        except ValueError:
                            next_use = float('inf')
                        if next_use > farthest:
                            farthest = next_use
                            victim = f
                    frames[frames.index(victim)] = p
        return faults

    fifo_f = fifo(pages, frame_size)
    lru_f = lru(pages, frame_size)
    opt_f = optimal(pages, frame_size)

    print(f"   引用串: {pages}")
    print(f"   页框数: {frame_size}")
    print(f"   FIFO 缺页: {fifo_f}/{len(pages)}")
    print(f"   LRU 缺页:  {lru_f}/{len(pages)}")
    print(f"   OPT 缺页:  {opt_f}/{len(pages)} (理论最优)")
    print(f"   → OPT 总是最优；FIFO vs LRU 取决于引用串（此处 FIFO 略优 = Belady 现象）")


# ============ 主入口 ============

def run_all_undergrad():
    print("=" * 65)
    print("🎓 Oxford CS 本科课程微项目")
    print("=" * 65)

    micro_fp_folds()
    micro_imp_pointers()
    micro_oop_inheritance()
    micro_discrete_graph_coloring()
    micro_prob_monty_hall()
    micro_linalg_eigen()
    micro_continuous_newton()
    micro_arch_pipeline()
    micro_networks_routing()
    micro_os_page_replacement()

    print("\n" + "=" * 65)
    print("✅ 全部本科课程完成！")
    print("=" * 65)


if __name__ == "__main__":
    run_all_undergrad()
