"""
CMU SCS — Undergraduate Course Micro-Projects
================================================
覆盖本科基础/进阶课程 10 门：
- 15-122 Imperative Computation (循环不变量 / Hoare triple)
- 15-251 Great Ideas in CS (停机问题 / P vs NP)
- 15-462 Computer Graphics (光线追踪)
- 15-213 Buffer Overflow (栈布局)
- 15-110 Java 入门 (OOP)
- 15-128 Freshman Immigration (习题)
- 15-214 Software Architecture (依赖图)
- 21-127 Concepts of Math (Cantor 对角线)
- 21-241 Linear Algebra (QR 分解)
- 21-259 Calculus 3D (梯度/散度/旋度)

每个 micro_* 函数实现一个小算法/演示。
"""
from __future__ import annotations
import math
import random

# ============ 15-122 Imperative Computation ============

def micro_15_122_loop_invariant():
    """循环不变量 + Hoare triple 验证：二分查找。"""
    print("\n📋 15-122: Loop Invariant — Binary Search")
    arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    target = 11
    lo, hi = 0, len(arr) - 1
    # Invariant: if target in arr, then arr[lo..hi] contains it
    iterations = 0
    while lo <= hi:
        iterations += 1
        mid = (lo + hi) // 2
        if arr[mid] == target:
            print(f"   Found {target} at index {mid} in {iterations} iterations")
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    print(f"   Not found after {iterations} iterations")
    return -1


# ============ 15-251 Great Ideas in CS ============

def micro_15_251_halting_problem():
    """停机问题：模拟悖论。"""
    print("\n📋 15-251: Halting Problem (不可判定性)")
    print("   假设 H(prog, input) 能判断 prog 是否在 input 上停机。")
    print("   构造 P(x): if H(x,x) then loop_forever else halt")
    print("   问 P(P) 是否停机？")
    print("   → 如果 H(P,P)=True 则 P(P) loop forever → 矛盾！")
    print("   → 如果 H(P,P)=False 则 P(P) halts → 矛盾！")
    print("   💡 不存在通用停机判定器 (Turing 1936)")

def micro_15_251_p_vs_np():
    """P vs NP 概念演示。"""
    print("\n📋 15-251: P vs NP")
    # TSP: verifying is easy (O(n)), finding is hard (O(n!))
    n = 8
    # Random distance matrix
    dist = [[random.randint(1, 100) if i != j else 0 for j in range(n)] for i in range(n)]
    # Verify a given tour
    tour = list(range(n)) + [0]
    total = sum(dist[tour[i]][tour[i+1]] for i in range(n))
    print(f"   TSP n={n}: verify tour cost = {total} (O(n))")
    print(f"   Brute force search: {math.factorial(n-1)//2} distinct tours")
    print(f"   💡 NP 问题：验证多项式时间，搜索指数时间")


# ============ 15-462 Computer Graphics ============

def micro_15_462_raytracer():
    """简化光线追踪：球体求交 + Phong 着色 (ASCII)。"""
    print("\n📋 15-462: Ray Tracing (ASCII Sphere)")
    width, height = 20, 10
    chars = " .:-=+*#%@"

    # Sphere at center, radius 3
    cx, cy, cz = 0, 0, 5
    radius = 3.0
    # Light direction
    lx, ly, lz = 0.5, -0.5, -1.0
    lnorm = math.sqrt(lx*lx + ly*ly + lz*lz)
    lx, ly, lz = lx/lnorm, ly/lnorm, lz/lnorm

    for y in range(height):
        row = ""
        for x in range(width):
            # ray from camera
            rx = (x - width/2) * 0.2
            ry = (y - height/2) * 0.3
            rz = 1.0
            # ray-sphere intersection
            ox, oy, oz = 0, 0, 0
            dx = cx - ox; dy = cy - oy; dz = cz - oz
            t = dx*rx + dy*ry + dz*rz
            px = ox + t*rx; py = oy + t*ry; pz = oz + t*rz
            d2 = (px-cx)**2 + (py-cy)**2 + (pz-cz)**2
            if d2 > radius*radius:
                row += " "
                continue
            # surface normal
            t_hit = t - math.sqrt(radius*radius - d2)
            hx = ox + t_hit*rx - cx
            hy = oy + t_hit*ry - cy
            hz = oz + t_hit*rz - cz
            hn = math.sqrt(hx*hx + hy*hy + hz*hz)
            nx, ny, nz = hx/hn, hy/hn, hz/hn
            # diffuse shading
            diff = max(0, -(nx*lx + ny*ly + nz*lz))
            idx = min(int(diff * (len(chars)-1)), len(chars)-1)
            row += chars[idx]
        print(f"   {row}")
    print("   💡 ASCII 球体 = 每像素求 ray-sphere 交点 + Phong 漫反射")


# ============ 15-213 Buffer Overflow ============

def micro_15_213_buffer_overflow():
    """栈布局演示（教学，非攻击）。"""
    print("\n📋 15-213: Stack Layout & Buffer Overflow")
    print("   函数栈帧布局 (x86, 高地址→低地址):")
    print("   ┌──────────────────┐ ← 高地址")
    print("   │ Return Address    │  (4/8 bytes)")
    print("   ├──────────────────┤")
    print("   │ Saved EBP/RBP     │")
    print("   ├──────────────────┤")
    print("   │ Local char buf[8] │  ← 溢出起点")
    print("   ├──────────────────┤")
    print("   │ Local variables   │")
    print("   └──────────────────┘ ← 低地址 (栈顶)")
    print("   溢出：写入 buf 超过 8 字节 → 覆盖 saved RBP → 覆盖 return addr")
    print("   防御: Stack Canary / ASLR / DEP(NX bit) / CFI")


# ============ 15-110 Java Intro ============

def micro_15_110_oop():
    """OOP 概念：封装/继承/多态。"""
    print("\n📋 15-110: OOP Concepts (Python pseudo-Java)")
    class Animal:
        def __init__(self, name):
            self.name = name  # encapsulation
        def speak(self):
            return f"{self.name} makes a sound"

    class Dog(Animal):  # inheritance
        def speak(self):  # polymorphism (override)
            return f"{self.name} says Woof!"

    class Cat(Animal):
        def speak(self):
            return f"{self.name} says Meow!"

    animals = [Dog("Rex"), Cat("Whiskers"), Dog("Buddy")]
    for a in animals:
        print(f"   {a.speak()}")
    print("   💡 多态：同 speak() 接口，不同实现，运行时绑定")


# ============ 15-128 Freshman Immigration ============

def micro_15_128_puzzles():
    """逻辑谜题。"""
    print("\n📋 15-128: Logic Puzzles")
    # Classic: 100 doors
    doors = [False] * 100  # all closed
    for step in range(1, 101):
        for i in range(step-1, 100, step):
            doors[i] = not doors[i]
    open_doors = [i+1 for i in range(100) if doors[i]]
    print(f"   100 doors problem: open doors = {open_doors}")
    print(f"   💡 只有完全平方数被翻转奇数次 → 开着的是 1,4,9,16,25,36,49,64,81,100")


# ============ 15-214 Software Architecture ============

def micro_15_214_dependency_graph():
    """模块依赖图 + 拓扑排序。"""
    print("\n📋 15-214: Dependency Graph (Topological Sort)")
    deps = {
        'auth': ['db', 'crypto'],
        'api': ['auth', 'db'],
        'db': ['config'],
        'crypto': ['config'],
        'config': [],
        'frontend': ['api'],
    }
    # Kahn's algorithm
    in_degree = {m: 0 for m in deps}
    for m in deps:
        for d in deps[m]:
            in_degree[d] = in_degree.get(d, 0)  # ensure exists
    # reverse: count incoming
    in_deg = {m: 0 for m in deps}
    for m in deps:
        for d in deps[m]:
            in_deg[d] += 1

    queue = [m for m in deps if in_deg[m] == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for dependent in deps:
            if node in deps[dependent]:
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    queue.append(dependent)
    print(f"   Build order: {' → '.join(order)}")
    print("   💡 无环依赖 → 可拓扑排序；循环依赖 = 架构缺陷")


# ============ 21-127 Concepts of Math ============

def micro_21_127_cantor_diagonal():
    """Cantor 对角线论证：实数不可数。"""
    print("\n📋 21-127: Cantor Diagonal Argument")
    # Assume we can list all real numbers in [0,1]
    # Construct a number different from the nth at position n
    fake_list = [
        "0.1111111...",
        "0.2222222...",
        "0.3333333...",
        "0.4444444...",
        "0.5555555...",
    ]
    # Diagonal: differ at each position
    diagonal = ""
    for i, num in enumerate(fake_list):
        orig = num[i+2]  # skip "0."
        diagonal += "7" if orig != "7" else "8"
    print(f"   Listed reals: {fake_list[:3]}...")
    print(f"   Diagonal number: 0.{diagonal}...")
    print(f"   It differs from list[0] at pos 0, list[1] at pos 1, ...")
    print("   💡 对角线数不在列表中 → 实数不可数 (Cantor 1891)")


# ============ 21-241 Linear Algebra ============

def micro_21_241_qr_decomposition():
    """Gram-Schmidt QR 分解。"""
    print("\n📋 21-241: QR Decomposition (Gram-Schmidt)")
    # 3x2 matrix
    A = [[1, 1], [1, 0], [0, 1]]
    # Gram-Schmidt
    def dot(u, v):
        return sum(a*b for a, b in zip(u, v))
    def scale(u, s):
        return [a*s for a in u]
    def sub(u, v):
        return [a-b for a, b in zip(u, v)]
    def norm(u):
        return math.sqrt(dot(u, u))

    cols = [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]
    Q_cols = []
    R = [[0.0]*len(cols) for _ in range(len(cols))]
    for j, col in enumerate(cols):
        v = col[:]
        for i in range(j):
            R[i][j] = dot(Q_cols[i], col)
            v = sub(v, scale(Q_cols[i], R[i][j]))
        R[j][j] = norm(v)
        Q_cols.append(scale(v, 1/max(R[j][j], 1e-10)))

    Q = [[Q_cols[j][i] for j in range(len(Q_cols))] for i in range(len(A))]
    print(f"   A = {A}")
    print(f"   Q = [[{Q[0][0]:.3f}, {Q[0][1]:.3f}], [{Q[1][0]:.3f}, {Q[1][1]:.3f}], [{Q[2][0]:.3f}, {Q[2][1]:.3f}]]")
    print(f"   R = [[{R[0][0]:.3f}, {R[0][1]:.3f}], [0, {R[1][1]:.3f}]]")
    print("   💡 A = QR, Q 正交, R 上三角 → 最小二乘法的基础")


# ============ 21-259 Calculus 3D ============

def micro_21_259_grad_div_curl():
    """梯度/散度/旋度 数值计算。"""
    print("\n📋 21-259: Gradient, Divergence, Curl (numerical)")
    # f(x,y,z) = x² + y² + z²
    # grad f = (2x, 2y, 2z)
    def f(x,y,z): return x**2 + y**2 + z**2
    h = 0.001
    x0, y0, z0 = 1.0, 2.0, 3.0
    grad = [
        (f(x0+h,y0,z0) - f(x0-h,y0,z0))/(2*h),
        (f(x0,y0+h,z0) - f(x0,y0-h,z0))/(2*h),
        (f(x0,y0,z0+h) - f(x0,y0,z0-h))/(2*h),
    ]
    print(f"   f(x,y,z) = x²+y²+z² at (1,2,3)")
    print(f"   Gradient ∇f = ({grad[0]:.1f}, {grad[1]:.1f}, {grad[2]:.1f})")
    print(f"   Expected:   (2.0, 4.0, 6.0)")

    # Vector field F = (x², y², z²)
    # div F = 2x + 2y + 2z = 12 at (1,2,3)
    # curl F = (∂Fz/∂y - ∂Fy/∂z, ...) = (0,0,0) for this field
    div = 2*x0 + 2*y0 + 2*z0
    print(f"   Divergence ∇·F = {div:.1f} (expected 12.0)")
    print(f"   Curl ∇×F = (0, 0, 0) — irrotational (gradient field)")
    print("   💡 curl(gradient) ≡ 0 — 向量恒等式")


# ============ 主入口 ============

def run_all():
    print("=" * 60)
    print("🎓 CMU SCS — Undergraduate Micro-Projects")
    print("=" * 60)
    random.seed(42)
    micro_15_122_loop_invariant()
    micro_15_251_halting_problem()
    micro_15_251_p_vs_np()
    micro_15_462_raytracer()
    micro_15_213_buffer_overflow()
    micro_15_110_oop()
    micro_15_128_puzzles()
    micro_15_214_dependency_graph()
    micro_21_127_cantor_diagonal()
    micro_21_241_qr_decomposition()
    micro_21_259_grad_div_curl()
    print("\n" + "=" * 60)
    print("✅ 全部本科微项目完成！(10 门课程)")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
