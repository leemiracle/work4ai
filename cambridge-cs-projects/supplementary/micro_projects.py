"""
Cambridge CST — 杂项微项目集
覆盖实验课、seminar、special topics
"""
import math
import random
from collections import Counter


# ================================================================
# Interaction Design (Part II)
# ================================================================

def micro_interaction_design():
    """Nielsen 启发式评估 + Fitts 定律"""
    print("\n📋 Interaction Design: Fitts 定律")
    # Fitts: MT = a + b·log₂(2D/W)  D=距离, W=目标宽度
    def fitts_MT(D, W, a=0.1, b=0.2):
        return a + b * math.log2(2 * D / W)
    targets = [("小按钮(10px远)", 10, 20), ("大按钮(100px远)", 100, 80),
               ("菜单栏(500px远)", 500, 200)]
    for name, D, W in targets:
        mt = fitts_MT(D, W)
        print(f"   {name}: D={D}px, W={W}px → MT={mt:.3f}s")
    print("   → 目标越大越近, 移动越快 (Fitts 1954)")


# ================================================================
# Statistics (Part IB)
# ================================================================

def micro_statistics():
    """中心极限定理模拟"""
    print("\n📋 Statistics: 中心极限定理")
    random.seed(42)
    for n in [1, 5, 30, 100]:
        means = []
        for _ in range(1000):
            samples = [random.uniform(0, 1) for _ in range(n)]
            means.append(sum(samples) / n)
        m = sum(means) / len(means)
        var = sum((x - m)**2 for x in means) / len(means)
        print(f"   n={n:3d}: 样本均值≈{m:.3f}, 方差≈{var:.5f} (理论=1/{12*n})")
    print("   → 无论原始分布, 样本均值趋近正态分布")


# ================================================================
# Graphics (Part IB)
# ================================================================

def micro_graphics():
    """Bresenham 直线算法"""
    print("\n📋 Graphics: Bresenham 直线")
    def bresenham(x0, y0, x1, y1):
        points = []
        dx, dy = abs(x1-x0), abs(y1-y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy: err -= dy; x0 += sx
            if e2 < dx: err += dx; y0 += sy
        return points

    pts = bresenham(0, 0, 7, 3)
    # ASCII 网格
    grid = [['.' for _ in range(8)] for _ in range(4)]
    for x, y in pts:
        grid[y][x] = '#'
    for row in grid:
        print("   " + " ".join(row))
    print(f"   {len(pts)} 个像素, 全整数运算无浮点")


# ================================================================
# Group Project 风格
# ================================================================

def micro_group_project():
    """敏捷开发 + 版本控制模拟"""
    print("\n📋 Group Project: 敏捷迭代")
    backlog = ["登录", "搜索", "购物车", "支付", "评价", "推荐"]
    velocity = 2  # 每轮做2个
    sprint = 0
    while backlog:
        sprint += 1
        done = backlog[:velocity]
        backlog = backlog[velocity:]
        print(f"   Sprint {sprint}: 完成 {done} (剩余 {len(backlog)})")
    print(f"   → {sprint} 轮迭代, Git 分支: main → feature → PR → merge")


# ================================================================
# Concurrent Systems 加深
# ================================================================

def micro_concurrent_dining():
    """哲学家就餐问题"""
    print("\n📋 Concurrent Systems: 哲学家就餐")
    n = 5
    print(f"   {n} 个哲学家, {n} 把叉子")
    print("   死锁方案: 所有人先拿左叉 → 死锁")
    print("   解决 1: 限制最多 n-1 人同时拿叉")
    print("   解决 2: 奇数先拿左, 偶数先拿右")
    print("   解决 3: Dijkstra 层级 (先拿小编号叉)")
    print("   → Dijkstra 1965: 经典死锁避免")


# ================================================================
# Algorithms II
# ================================================================

def micro_algorithms_ii():
    """图算法: Dijkstra"""
    print("\n📋 Algorithms II: Dijkstra 最短路")
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"D": 3},
        "C": {"B": 1, "D": 5},
        "D": {},
    }
    # Dijkstra
    dist = {n: float('inf') for n in graph}
    dist["A"] = 0
    visited = set()
    while len(visited) < len(graph):
        u = min((n for n in graph if n not in visited), key=lambda x: dist[x])
        visited.add(u)
        for v, w in graph[u].items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for n in sorted(dist):
        print(f"   A → {n}: {dist[n]}")
    print("   → A→C→B→D = 2+1+3 = 6 (比 A→B→D = 4+3 = 7 更短!)")


# ================================================================
# Type Theory
# ================================================================

def micro_type_theory():
    """简单类型 lambda 演算"""
    print("\n📋 Type Theory: 简单类型 λ 演算")
    # 类型推断: λx.x : α → α
    # λx.λy.x : α → β → α
    print("   λx.x       : α → α        (恒等)")
    print("   λx.λy.x    : α → β → α    (常函数)")
    print("   λf.λx.f x  : (α→β) → α → β (应用)")
    print("   Curry-Howard: 类型 = 命题, 程序 = 证明")
    print("   α→α 对应 'P → P' 的证明")


# ================================================================
# Geometric Modelling
# ================================================================

def micro_geometric_modelling():
    """Bézier 曲线"""
    print("\n📋 Geometric Modelling: Bézier 曲线")
    def bezier(t, points):
        n = len(points) - 1
        x, y = 0, 0
        for i, (px, py) in enumerate(points):
            # Bernstein polynomial
            coeff = math.comb(n, i) * (1-t)**(n-i) * t**i
            x += coeff * px
            y += coeff * py
        return x, y

    control = [(0, 0), (2, 4), (4, 0)]
    print(f"   控制点: {control}")
    for t in [0, 0.25, 0.5, 0.75, 1.0]:
        x, y = bezier(t, control)
        print(f"   t={t:.2f}: ({x:.2f}, {y:.2f})")
    print("   → 曲线必过首末控制点, 中间点「吸引」曲线")


# ================================================================
# Databases 加深
# ================================================================

def micro_databases_btree():
    """B-tree 插入"""
    print("\n📋 Databases: B-tree (2-3树)")
    # 简化 2-3 树插入
    class Node:
        def __init__(self, keys=None, children=None):
            self.keys = list(keys) if keys else []
            self.children = list(children) if children else []

    # 模拟顺序插入 1..7 到 2-3 树
    print("   插入 1,2,3,4,5,6,7:")
    print("   2-3树: 每个节点 1-2 个 key, 2-3 个子节点")
    print("   插入3: [1|2|3] → split → [2] with [1],[3]")
    print("   最终根: [4]")
    print("        /          \\")
    print("     [2]           [6]")
    print("    /   \\         /   \\")
    print("  [1]  [3]      [5]  [7]")
    print("   → B-tree 保持平衡, 查找 O(log n)")


# ================================================================
# Quantum Information
# ================================================================

def micro_quantum_info():
    """量子纠缠 + Bell 态"""
    print("\n📋 Quantum Information: Bell 态")
    # |Φ+⟩ = (|00⟩ + |11⟩) / √2
    # 测量 A → B 必然相同
    random.seed(42)
    print("   Bell 态 |Φ+⟩ = (|00⟩ + |11⟩) / √2")
    print("   模拟 10 次测量:")
    results = []
    for _ in range(10):
        a = random.choice([0, 1])
        b = a  # 完美相关
        results.append((a, b))
    for a, b in results[:5]:
        print(f"     Alice={a}, Bob={b} {'✓ 相同' if a==b else '✗'}")
    agree = sum(1 for a, b in results if a == b)
    print(f"   ... 一致率: {agree}/10 (理论=100%)")
    print("   → 纠缠粒子「超距相关」(EPR 悖论)")


# ================================================================
# 主入口
# ================================================================

def run_all_micro():
    print("=" * 64)
    print("🎓 Cambridge CST 杂项微项目集")
    print("=" * 64)
    micro_interaction_design()
    micro_statistics()
    micro_graphics()
    micro_group_project()
    micro_concurrent_dining()
    micro_algorithms_ii()
    micro_type_theory()
    micro_geometric_modelling()
    micro_databases_btree()
    micro_quantum_info()
    print("\n" + "=" * 64)
    print("✅ 全部杂项微项目完成！")
    print("=" * 64)


if __name__ == "__main__":
    run_all_micro()
