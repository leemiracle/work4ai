"""
University of Toronto DCS - 本科补充课程微项目集
==================================================
覆盖课程（10 门）：
- CSC 104 How to Think Like a Computer Scientist
- CSC 108 Introduction to Computer Programming (加深)
- CSC 120 Computer Science for the Sciences
- CSC 290 Communication Skills for Computer Scientists
- CSC 301 Introduction to Software Engineering
- CSC 304 Algorithm Analysis
- CSC 320 Visual Computing
- CSC 336 Numerical Methods
- CSC 343 Introduction to Databases
- CSC 458 Computer Networks
"""
import math
import random
from collections import defaultdict


# ============ CSC 104: How to Think Like a Computer Scientist ============

def micro_csc104_abstraction():
    """抽象与计算思维：水仙花数 + 因数分解"""
    print("\n📋 CSC 104: 计算思维（水仙花数）")
    # 水仙花数: n 位数，各位数字的 n 次方之和等于自身
    narcissistic = []
    for n in range(100, 10000):
        digits = [int(d) for d in str(n)]
        power = len(digits)
        if sum(d ** power for d in digits) == n:
            narcissistic.append(n)
    print(f"   100-9999 内的水仙花数: {narcissistic}")
    print(f"   153 = 1³+5³+3³ = {1**3+5**3+3**3}")


# ============ CSC 108: 加深 - 字符串处理 ============

def micro_csc108_strings():
    """字符串处理：凯撒密码 + 回文检测"""
    print("\n📋 CSC 108: 字符串处理（凯撒密码）")

    def caesar_cipher(text, shift):
        result = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                result.append(ch)
        return ''.join(result)

    msg = "Hello World"
    encrypted = caesar_cipher(msg, 3)
    decrypted = caesar_cipher(encrypted, -3)
    print(f"   原文: {msg}")
    print(f"   加密(shift=3): {encrypted}")
    print(f"   解密: {decrypted}")

    # 回文检测
    def is_palindrome(s):
        s = ''.join(c.lower() for c in s if c.isalnum())
        return s == s[::-1]

    for test in ["racecar", "A man a plan a canal Panama", "hello"]:
        print(f"   回文检测 '{test}': {is_palindrome(test)}")


# ============ CSC 120: Computer Science for Sciences ============

def micro_csc120_scientific():
    """科学计算应用：人口增长模型"""
    print("\n📋 CSC 120: 科学计算（人口增长）")
    # Logistic 增长模型: P(t+1) = P(t) + r*P(t)*(1 - P(t)/K)
    K = 1000  # 环境容量
    r = 0.15  # 增长率
    P0 = 10   # 初始种群

    population = [P0]
    for _ in range(50):
        P = population[-1]
        population.append(P + r * P * (1 - P / K))

    print(f"   Logistic 模型: r={r}, K={K}, P0={P0}")
    print(f"   第10年: {population[10]:.1f}")
    print(f"   第25年: {population[25]:.1f}")
    print(f"   第50年: {population[50]:.1f} (接近 K)")
    print(f"   → 种群先指数增长，后趋于环境容量 K")


# ============ CSC 290: Communication Skills ============

def micro_csc290_communication():
    """技术沟通：API 文档生成 + UML"""
    print("\n📋 CSC 290: 技术沟通（API 文档模板）")
    doc_template = """   def calculate_bmi(weight: float, height: float) -> float:
       \"\"\"
       计算 BMI (Body Mass Index)

       Args:
           weight: 体重（千克）
           height: 身高（米）

       Returns:
           BMI 值 = weight / height²

       Raises:
           ValueError: 如果 weight 或 height ≤ 0

       Example:
           >>> calculate_bmi(70, 1.75)
           22.86
       \"\"\""""
    print(doc_template)
    bmi = 70 / 1.75 ** 2
    print(f"\n   BMI(70, 1.75) = {bmi:.2f}")


# ============ CSC 301: Software Engineering ============

def micro_csc301_agile():
    """敏捷开发流程模拟"""
    print("\n📋 CSC 301: 敏捷开发（Sprint 模拟）")
    backlog = [
        ("User login", 5, "High"),
        ("Search bar", 3, "Medium"),
        ("Profile page", 8, "High"),
        ("Dark mode", 2, "Low"),
        ("Settings menu", 5, "Medium"),
    ]
    velocity = 13  # 每 sprint 能完成的 story points

    print(f"   Product Backlog ({len(backlog)} stories):")
    for name, pts, prio in backlog:
        print(f"     {name:20s} {pts}pts [{prio}]")

    sprint = []
    remaining = velocity
    for name, pts, prio in sorted(backlog, key=lambda x: x[2] != "High"):
        if pts <= remaining:
            sprint.append((name, pts))
            remaining -= pts
    print(f"\n   Sprint (velocity={velocity}):")
    for name, pts in sprint:
        print(f"     ✓ {name} ({pts}pts)")
    print(f"   完成率: {sum(p for _, p in sprint)}/{velocity} points")


# ============ CSC 304: Algorithm Analysis ============

def micro_csc304_recurrence():
    """递推关系求解"""
    print("\n📋 CSC 304: 递推关系分析")
    # T(n) = 2T(n/2) + n → O(n log n)
    # T(n) = T(n-1) + 1 → O(n)
    # T(n) = 2T(n/2) + 1 → O(n)

    def t_merge_sort(n):
        if n <= 1:
            return 0
        return 2 * t_merge_sort(n // 2) + n

    def t_naive(n):
        return n  # T(n) = T(n-1) + 1

    sizes = [16, 64, 256, 1024]
    print(f"   {'n':>6} {'Merge T(n)':>12} {'n log n':>10}")
    for n in sizes:
        actual = t_merge_sort(n)
        theory = n * math.log2(n)
        print(f"   {n:6d} {actual:12d} {theory:10.0f}")


# ============ CSC 320: Visual Computing ============

def micro_csc320_dithering():
    """图像抖动（Floyd-Steinberg 简化版）"""
    print("\n📋 CSC 320: 图像抖动（半色调）")
    # 创建灰度渐变图像
    width = 20
    gray = [i / width for i in range(width)]  # 0 到 1 的渐变
    # 阈值抖动
    threshold_dither = ''.join('#' if g > 0.5 else '.' for g in gray)
    # Floyd-Steinberg 误差扩散
    fs_dither = []
    error = 0
    for g in gray:
        val = g + error
        if val > 0.5:
            fs_dither.append('#')
            error = val - 1.0
        else:
            fs_dither.append('.')
            error = val
    print(f"   原始灰度:   {''.join('░' if g > 0.33 else ' ' if g < 0.1 else '▒' for g in gray)}")
    print(f"   阈值抖动:   {''.join(threshold_dither)}")
    print(f"   Floyd-Steinberg: {''.join(fs_dither)}")
    print(f"   → 误差扩散产生更平滑的渐变效果")


# ============ CSC 336: Numerical Methods ============

def micro_csc336_newton_raphson():
    """Newton-Raphson 求根 + 数值积分"""
    print("\n📋 CSC 336: 数值方法（Newton-Raphson + Simpson）")

    # Newton-Raphson 求 √2
    def newton_sqrt(c, x0=1.0, tol=1e-10):
        x = x0
        iters = 0
        while abs(x ** 2 - c) > tol:
            x = 0.5 * (x + c / x)
            iters += 1
        return x, iters

    result, iters = newton_sqrt(2)
    print(f"   Newton √2 = {result:.12f} (iters={iters})")
    print(f"   math.sqrt(2) = {math.sqrt(2):.12f}")

    # Simpson 数值积分: ∫₀^π sin(x) dx = 2
    def simpson(f, a, b, n=100):
        h = (b - a) / n
        result = f(a) + f(b)
        for i in range(1, n):
            x = a + i * h
            result += 4 * f(x) if i % 2 == 1 else 2 * f(x)
        return result * h / 3

    integral = simpson(math.sin, 0, math.pi)
    print(f"   Simpson ∫₀^π sin(x) dx = {integral:.8f} (精确=2)")


# ============ CSC 343: Databases ============

def micro_csc343_sql_engine():
    """简化 SQL 查询引擎"""
    print("\n📋 CSC 343: 数据库（关系代数模拟）")
    # 模拟一张 students 表
    students = [
        {"id": 1, "name": "Alice", "dept": "CS", "gpa": 3.8},
        {"id": 2, "name": "Bob", "dept": "Math", "gpa": 3.5},
        {"id": 3, "name": "Carol", "dept": "CS", "gpa": 3.9},
        {"id": 4, "name": "Dave", "dept": "Physics", "gpa": 3.2},
        {"id": 5, "name": "Eve", "dept": "CS", "gpa": 3.6},
    ]

    # SELECT name, gpa FROM students WHERE dept = 'CS' ORDER BY gpa DESC
    cs_students = [s for s in students if s["dept"] == "CS"]
    cs_students.sort(key=lambda s: -s["gpa"])
    print("   SELECT name, gpa FROM students WHERE dept='CS' ORDER BY gpa DESC:")
    for s in cs_students:
        print(f"     {s['name']:10s} GPA={s['gpa']}")

    # 聚合: AVG(gpa) GROUP BY dept
    dept_gpas = defaultdict(list)
    for s in students:
        dept_gpas[s["dept"]].append(s["gpa"])
    print("\n   SELECT dept, AVG(gpa) FROM students GROUP BY dept:")
    for dept, gpas in sorted(dept_gpas.items()):
        print(f"     {dept:10s} AVG={sum(gpas)/len(gpas):.2f}")


# ============ CSC 458: Computer Networks ============

def micro_csc458_routing():
    """网络路由：Dijkstra 最短路径"""
    print("\n📋 CSC 458: 网络路由（Dijkstra）")
    # 网络拓扑图
    graph = {
        'A': {'B': 4, 'C': 2},
        'B': {'A': 4, 'C': 1, 'D': 5},
        'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
        'D': {'B': 5, 'C': 8, 'E': 2},
        'E': {'C': 10, 'D': 2},
    }

    import heapq
    def dijkstra(graph, start):
        dist = {v: float('inf') for v in graph}
        dist[start] = 0
        prev = {v: None for v in graph}
        pq = [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in graph[u].items():
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, prev

    dist, prev = dijkstra(graph, 'A')
    print(f"   从 A 出发的最短路径:")
    for node in sorted(graph):
        path = []
        cur = node
        while cur:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        print(f"     A→{node}: 距离={dist[node]:2d}, 路径={'→'.join(path)}")


# ============ 主入口 ============

def run_all_undergrad():
    print("=" * 60)
    print("🎓 Toronto DCS 本科补充课程微项目")
    print("=" * 60)

    micro_csc104_abstraction()
    micro_csc108_strings()
    micro_csc120_scientific()
    micro_csc290_communication()
    micro_csc301_agile()
    micro_csc304_recurrence()
    micro_csc320_dithering()
    micro_csc336_newton_raphson()
    micro_csc343_sql_engine()
    micro_csc458_routing()

    print("\n" + "=" * 60)
    print("✅ 全部本科补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_undergrad()
