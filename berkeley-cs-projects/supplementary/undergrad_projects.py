"""
UC Berkeley EECS — 本科进阶课程微项目集
覆盖：CS 61A 进阶 / CS 70 进阶 / EE16A / CS 170 / CS 161 / CS 164 / CS 169 / CS 174 / CS C100 / EE120
"""
import math
import random
from collections import defaultdict, deque


# ============ CS 61A 进阶：面向对象 + 多重分派 ============

def cs61a_multiple_dispatch():
    """CS61A Lec 13: 数据导向程序设计 / 多重分派"""
    print("\n📋 CS61A 进阶: 多重分派（复数运算）")
    # 直角坐标 vs 极坐标
    ops = {}

    def register(type1, type2, op_name):
        def decorator(fn):
            ops[(type1, type2, op_name)] = fn
            return fn
        return decorator

    @register("rect", "rect", "add")
    def add_rr(a, b):
        return ("rect", a[1] + b[1], a[2] + b[2])

    @register("polar", "polar", "add")
    def add_pp(a, b):
        # 转直角加再转回极坐标（简化）
        x1, y1 = a[1] * math.cos(a[2]), a[1] * math.sin(a[2])
        x2, y2 = b[1] * math.cos(b[2]), b[1] * math.sin(b[2])
        x, y = x1 + x2, y1 + y2
        return ("polar", math.sqrt(x*x+y*y), math.atan2(y, x))

    def apply_op(a, b, op_name):
        key = (a[0], b[0], op_name)
        if key not in ops:
            return None
        return ops[key](a, b)

    r1 = ("rect", 1, 2)
    r2 = ("rect", 3, 4)
    result = apply_op(r1, r2, "add")
    print(f"   (1+2i) + (3+4i) = {result}  (期望 rect 4+6i)")


# ============ CS 70 进阶：容斥原理 ============

def cs70_inclusion_exclusion():
    """CS70: 容斥原理——欧拉函数"""
    print("\n📋 CS70 进阶: 容斥原理（欧拉函数）")
    def euler_phi(n):
        """φ(n) = n × Π(1 - 1/p)，p 是 n 的素因子"""
        result = n
        temp = n
        p = 2
        while p * p <= temp:
            if temp % p == 0:
                while temp % p == 0:
                    temp //= p
                result -= result // p
            p += 1
        if temp > 1:
            result -= result // temp
        return result

    for n in [10, 12, 36, 100]:
        phi = euler_phi(n)
        print(f"   φ({n}) = {phi}  (≤{n} 中与 {n} 互素的正整数个数)")


# ============ EE 16A/B：线性电路 ============

def ee16a_linear_circuit():
    """EE16A: 基尔霍夫定律解电路"""
    print("\n📋 EE16A: 基尔霍夫定律（节点电压法）")
    # 简单电路: 3 节点，解线性方程组
    # G·V = I (G 是电导矩阵)
    # [2 -1  0]   [V1]   [1]
    # [-1 3 -1] · [V2] = [0]
    # [0 -1  2]   [V3]   [0]
    G = [[2, -1, 0], [-1, 3, -1], [0, -1, 2]]
    I = [1, 0, 0]
    # Gauss 消元
    n = 3
    aug = [G[i] + [I[i]] for i in range(n)]
    for col in range(n):
        for r in range(col + 1, n):
            factor = aug[r][col] / aug[col][col]
            aug[r] = [aug[r][j] - factor * aug[col][j] for j in range(n + 1)]
    V = [0] * n
    for i in range(n - 1, -1, -1):
        V[i] = aug[i][n]
        for j in range(i + 1, n):
            V[i] -= aug[i][j] * V[j]
        V[i] /= aug[i][i]
    print(f"   节点电压: V1={V[0]:.3f}, V2={V[1]:.3f}, V3={V[2]:.3f} V")


# ============ CS 170 高效算法：Dijkstra ============

def cs170_dijkstra():
    """CS170: Dijkstra 最短路"""
    print("\n📋 CS170: Dijkstra 最短路（加权图）")
    import heapq
    graph = {
        "A": [("B", 4), ("C", 2)],
        "B": [("C", 1), ("D", 5)],
        "C": [("B", 1), ("D", 8), ("E", 10)],
        "D": [("E", 2)],
        "E": [],
    }
    dist = {n: math.inf for n in graph}
    dist["A"] = 0
    heap = [(0, "A")]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    print(f"   从 A 到各节点最短距离: {dict((k, v) for k, v in dist.items())}")


# ============ CS 161 安全：缓冲区溢出示意 ============

def cs161_buffer_overflow():
    """CS161: 缓冲区溢出原理"""
    print("\n📋 CS161: 缓冲区溢出（栈布局）")
    print("""
   栈布局（高→低地址）:
   ┌──────────────┐
   │ return addr  │  ← 攻击目标（覆盖为 shellcode 地址）
   ├──────────────┤
   │ saved ebp    │
   ├──────────────┤
   │ buffer[64]   │  ← strcpy(buf, attacker_input) 越界写
   ├──────────────┤
   防御:
   - 栈 canary（栈金丝雀检测覆盖）
   - ASLR（地址随机化）
   - NX bit（栈不可执行）
   - Stack cookies (gcc -fstack-protector)
   """)


# ============ CS 164 编译器：正则 + DFA ============

def cs164_regex_to_dfa():
    """CS164: 正则 → NFA → DFA（Thompson 构造简化）"""
    print("\n📋 CS164: 正则匹配（简化 DFA）")
    # 识别 'ab*c' 的 DFA
    # 状态 0 --a--> 1 --b--> 1 --c--> 2(accept)
    transitions = {
        0: {"a": 1},
        1: {"b": 1, "c": 2},
        2: {},
    }
    accept = {2}
    tests = ["ac", "abc", "abbbc", "abbc", "bac"]
    for s in tests:
        state = 0
        for ch in s:
            state = transitions.get(state, {}).get(ch, -1)
            if state == -1:
                break
        result = "✓" if state in accept else "✗"
        print(f"   'ab*c' 匹配 '{s}': {result}")


# ============ CS 169 SaaS：REST API 设计 ============

def cs169_rest_api():
    """CS169: RESTful API 设计"""
    print("\n📋 CS169: REST API（CRUD 映射）")
    endpoints = [
        ("GET", "/movies", "列出所有电影"),
        ("GET", "/movies/42", "获取 #42 电影详情"),
        ("POST", "/movies", "创建新电影"),
        ("PUT", "/movies/42", "更新 #42"),
        ("DELETE", "/movies/42", "删除 #42"),
    ]
    for method, path, desc in endpoints:
        print(f"   {method:6s} {path:20s} → {desc}")
    print("   HTTP 状态码: 200 OK / 201 Created / 400 Bad / 404 Not Found / 500 Error")


# ============ CS 174 概率：生日悖论 ============

def cs174_birthday_paradox():
    """CS174: 生日悖论"""
    print("\n📋 CS174: 生日悖论")
    def birthday_prob(n, k=365, trials=10000):
        collisions = 0
        for _ in range(trials):
            days = [random.randint(1, k) for _ in range(n)]
            if len(set(days)) < n:
                collisions += 1
        return collisions / trials

    for n in [10, 23, 50, 70]:
        p = birthday_prob(n)
        print(f"   {n} 人中至少 2 人生日相同: {p:.1%}")


# ============ CS C100 Data：A/B 测试 ============

def csc100_ab_test():
    """CS C100: A/B 测试统计显著性"""
    print("\n📋 CS C100: A/B 测试（z-test）")
    # A 组: 1000 访客, 120 转化 (12%)
    # B 组: 1000 访客, 145 转化 (14.5%)
    n_A, conv_A = 1000, 120
    n_B, conv_B = 1000, 145
    p_A, p_B = conv_A / n_A, conv_B / n_B
    p_pool = (conv_A + conv_B) / (n_A + n_B)
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n_A + 1/n_B))
    z = (p_B - p_A) / se
    print(f"   A 组转化率: {p_A:.2%}, B 组: {p_B:.2%}")
    print(f"   z-score = {z:.3f}")
    print(f"   显著性 (z>1.96 = 95%): {'显著 ✓' if z > 1.96 else '不显著 ✗'}")


# ============ EE 120 信号：FFT ============

def ee120_dft():
    """EE120: 离散傅里叶变换（DFT 简化）"""
    print("\n📋 EE120: DFT（手工计算低频分量）")
    import cmath
    # 信号: 2Hz 正弦 + 直流
    N = 8
    signal = [1 + math.sin(2 * math.pi * 2 * t / N) for t in range(N)]
    # DFT: X[k] = Σ x[n] e^(-i 2πkn/N)
    X = []
    for k in range(N):
        s = 0
        for n in range(N):
            s += signal[n] * cmath.exp(-2j * math.pi * k * n / N)
        X.append(s)
    print(f"   信号: 1 + sin(2π·2t/N), N={N}")
    print(f"   X[0] (DC) = {X[0].real:.3f}  (期望 8)")
    print(f"   |X[2]| = {abs(X[2]):.3f}  (期望 4, 2Hz 分量)")
    print(f"   |X[6]| = {abs(X[6]):.3f}  (期望 4, 对称分量)")


# ============ 主入口 ============

def run_all_undergrad():
    print("=" * 60)
    print("🎓 UC Berkeley EECS 本科进阶课程微项目")
    print("=" * 60)
    cs61a_multiple_dispatch()
    cs70_inclusion_exclusion()
    ee16a_linear_circuit()
    cs170_dijkstra()
    cs161_buffer_overflow()
    cs164_regex_to_dfa()
    cs169_rest_api()
    cs174_birthday_paradox()
    csc100_ab_test()
    ee120_dft()
    print("\n" + "=" * 60)
    print("✅ 全部本科进阶微项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_undergrad()
