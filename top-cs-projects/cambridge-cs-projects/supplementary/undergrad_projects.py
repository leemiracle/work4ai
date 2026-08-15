"""
Cambridge CST — 本科补充课程微项目集
覆盖 Part IA / Part IB 其余课程
"""
import math
import random
from collections import Counter


# ================================================================
# Part IA Object-Oriented Programming (Java → Python 模拟)
# ================================================================

def ia_oop_java_style():
    """OOP Java 风格：类继承、多态、接口"""
    print("\n📋 Part IA OOP: Java 风格 OOP")

    class Shape:
        def area(self): return 0
        def describe(self): return f"{type(self).__name__} area={self.area():.2f}"

    class Circle(Shape):
        def __init__(self, r): self.r = r
        def area(self): return math.pi * self.r**2

    class Rectangle(Shape):
        def __init__(self, w, h): self.w, self.h = w, h
        def area(self): return self.w * self.h

    shapes = [Circle(3), Rectangle(4, 5), Circle(1)]
    for s in shapes:
        print(f"   {s.describe()}")
    print("   → 多态: 同一个 describe() 调用不同子类的 area()")


# ================================================================
# Part IA Discrete Mathematics
# ================================================================

def ia_discrete_math():
    """离散数学：组合计数、鸽巢原理"""
    print("\n📋 Part IA Discrete Math: 鸽巢原理")
    # 鸽巢: 367 人中必有 2 人生日同天
    # 扩展: 任何 n+1 个正整数中必有两个差为 n 的倍数
    nums = [random.randint(1, 1000) for _ in range(11)]
    # 模 10 的余数只有 10 种 → 11 个数必有 2 个同余
    remainders = {}
    for n in nums:
        r = n % 10
        if r in remainders:
            print(f"   {nums[:11]}")
            print(f"   {n} ≡ {remainders[r]} (mod 10) → 差 = {n - remainders[r]} 是 10 的倍数")
            break
        remainders[r] = n
    # 组合数
    def C(n, k):
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
    print(f"   C(10,3) = {C(10,3)}, C(20,10) = {C(20,10)}")


# ================================================================
# Part IA Probability
# ================================================================

def ia_probability():
    """概率论：生日悖论模拟"""
    print("\n📋 Part IA Probability: 生日悖论")
    random.seed(42)
    for n in [10, 23, 50, 70]:
        hits = 0
        for _ in range(10000):
            birthdays = [random.randint(1, 365) for _ in range(n)]
            if len(set(birthdays)) < n:
                hits += 1
        theoretical = 1 - math.exp(-n*(n-1)/2/365)
        print(f"   {n:2d} 人: 重复生日概率={hits/10000:.3f}, 理论≈{theoretical:.3f}")
    print("   → 仅需 23 人就 >50% 概率有重复生日！")


# ================================================================
# Part IA Machine Learning
# ================================================================

def ia_ml_knn():
    """KNN 分类器"""
    print("\n📋 Part IA ML: K-Nearest Neighbors")
    # 2D 数据点
    points = [(1, 1, 'A'), (2, 1, 'A'), (1, 2, 'A'),
              (5, 5, 'B'), (6, 5, 'B'), (5, 6, 'B')]
    test = (3, 3)
    k = 3
    dists = sorted(points, key=lambda p: (p[0]-test[0])**2 + (p[1]-test[1])**2)
    neighbors = dists[:k]
    votes = Counter(n[2] for n in neighbors)
    label = votes.most_common(1)[0][0]
    print(f"   训练: A类=[(1,1),(2,1),(1,2)], B类=[(5,5),(6,5),(5,6)]")
    print(f"   测试点: {test}, K={k}")
    print(f"   最近邻: {[(n[0],n[1]) for n in neighbors]} → 分类: {label}")


# ================================================================
# Part IA Operating Systems & Networks
# ================================================================

def ia_os_net_pipes():
    """管道与 IPC"""
    print("\n📋 Part IA OS & Networks: 管道通信")
    # 模拟 producer-consumer
    buffer, max_size = [], 3
    log = []
    for item in range(6):
        while len(buffer) >= max_size:
            consumed = buffer.pop(0)
            log.append(f"     consume {consumed}")
        buffer.append(item)
        log.append(f"     produce {item} (buffer={len(buffer)})")
    while buffer:
        log.append(f"     consume {buffer.pop(0)}")
    for line in log[:6]:
        print(line)
    print(f"   ... (共 {len(log)} 步)")
    print("   → 有界缓冲区实现 producer-consumer 同步")


# ================================================================
# Part IB Databases
# ================================================================

def ib_databases():
    """关系代数 + SQL 查询模拟"""
    print("\n📋 Part IB Databases: 关系代数")
    students = [
        {"id": 1, "name": "Alice", "year": 2024, "dept": "CS"},
        {"id": 2, "name": "Bob", "year": 2023, "dept": "CS"},
        {"id": 3, "name": "Carol", "year": 2024, "dept": "Math"},
        {"id": 4, "name": "Dave", "year": 2023, "dept": "Physics"},
    ]
    grades = [
        {"sid": 1, "course": "Algorithms", "grade": 75},
        {"sid": 1, "course": "ML", "grade": 82},
        {"sid": 2, "course": "Algorithms", "grade": 90},
        {"sid": 3, "course": "Algorithms", "grade": 65},
    ]
    # σ_{dept='CS'} (students) ⋈ grades → π_{name, course, grade}
    cs_ids = {s["id"] for s in students if s["dept"] == "CS"}
    name_map = {s["id"]: s["name"] for s in students}
    result = [(name_map[g["sid"]], g["course"], g["grade"])
              for g in grades if g["sid"] in cs_ids]
    result.sort(key=lambda x: -x[2])
    print("   σ_{dept='CS'}(students) ⋈ grades:")
    for name, course, grade in result:
        print(f"     {name:6s} {course:12s} {grade}")


# ================================================================
# Part IB Computer Design
# ================================================================

def ib_computer_design():
    """数字逻辑：全加器"""
    print("\n📋 Part IB Computer Design: 全加器 → 4位加法器")
    def full_adder(a, b, cin):
        s = a ^ b ^ cin
        cout = (a & b) | (cin & (a ^ b))
        return s, cout

    def adder4(a_bits, b_bits):
        result = []
        carry = 0
        for i in range(3, -1, -1):
            s, carry = full_adder(a_bits[i], b_bits[i], carry)
            result.append(s)
        result.reverse()
        return result, carry

    a = [0, 0, 1, 1]  # 3
    b = [0, 1, 0, 1]  # 5
    sum_bits, carry = adder4(a, b)
    print(f"   {int(''.join(map(str,a)),2)} + {int(''.join(map(str,b)),2)} "
          f"= {int(''.join(map(str,sum_bits)),2)} (carry={carry})")


# ================================================================
# Part IB ECAD (Electronic CAD)
# ================================================================

def ib_ecad_fsm():
    """有限状态机（硬件描述风格）"""
    print("\n📋 Part IB ECAD: Moore FSM（交通灯）")
    states = {"RED": ("GREEN", 0), "GREEN": ("YELLOW", 1), "YELLOW": ("RED", 2)}
    current = "RED"
    print("   状态序列:")
    for i in range(6):
        output = states[current][1]
        print(f"     t={i}: {current:8s} output={output}")
        current = states[current][0]


# ================================================================
# Part IB Semantics of Programming Languages
# ================================================================

def ib_semantics():
    """操作语义：简单表达式求值"""
    print("\n📋 Part IB Semantics of PL: 操作语义")
    # Big-step: ⟨e, σ⟩ ⇓ v
    def eval_expr(e, env):
        if isinstance(e, int):
            return e
        if isinstance(e, str):
            return env[e]
        op, l, r = e
        lv, rv = eval_expr(l, env), eval_expr(r, env)
        if op == "+": return lv + rv
        if op == "*": return lv * rv

    env = {"x": 3, "y": 4}
    expr = ("+", ("*", "x", "y"), ("+", "x", "y"))  # x*y + (x+y)
    result = eval_expr(expr, env)
    print(f"   环境: {env}")
    print(f"   表达式: x*y + (x+y)")
    print(f"   求值: {result} (= 3*4 + 3+4 = 12+7)")


# ================================================================
# Part IB Complexity Theory
# ================================================================

def ib_complexity():
    """复杂度类演示"""
    print("\n📋 Part IB Complexity: P vs NP vs NPC")
    classes = {
        "P": ["排序 O(n log n)", "最短路 O(V²)", "矩阵乘法 O(n³)"],
        "NP": ["SAT", "图着色", "子集和"],
        "NPC": ["TSP (判定版)", "3-SAT", "Clique", "顶点覆盖"],
        "co-NP": ["UNSAT", "无哈密顿路径"],
    }
    for cls, problems in classes.items():
        print(f"   {cls}: {', '.join(problems[:3])}")
    print("   P ⊆ NP, NPC = NP ∩ NP-hard")
    print("   P = NP? （千禧年难题，百万美元悬赏）")


# ================================================================
# 主入口
# ================================================================

def run_all_undergrad():
    print("=" * 64)
    print("🎓 Cambridge CST 本科补充课程微项目")
    print("=" * 64)
    ia_oop_java_style()
    ia_discrete_math()
    ia_probability()
    ia_ml_knn()
    ia_os_net_pipes()
    ib_databases()
    ib_computer_design()
    ib_ecad_fsm()
    ib_semantics()
    ib_complexity()
    print("\n" + "=" * 64)
    print("✅ 全部本科补充课程完成！")
    print("=" * 64)


if __name__ == "__main__":
    run_all_undergrad()
