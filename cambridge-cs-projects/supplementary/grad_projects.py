"""
Cambridge CST — 研究生补充课程微项目集
覆盖 Part III / MPhil ACS 专题课程
"""
import math
import random
from collections import defaultdict


# ================================================================
# Part III Advanced Graphics
# ================================================================

def p3_advanced_graphics():
    """光线追踪基础"""
    print("\n📋 Part III Advanced Graphics: 光线-球求交")
    def intersect_sphere(ox, oy, oz, dx, dy, dz, cx, cy, cz, r):
        """Ray O+tD vs Sphere center C radius r"""
        fx, fy, fz = ox-cx, oy-cy, oz-cz
        a = dx*dx + dy*dy + dz*dz
        b = 2*(fx*dx + fy*dy + fz*dz)
        c = fx*fx + fy*fy + fz*fz - r*r
        disc = b*b - 4*a*c
        if disc < 0:
            return None
        t = (-b - math.sqrt(disc)) / (2*a)
        return t if t > 0 else None

    t = intersect_sphere(0, 0, 0, 0, 0, 1, 0, 0, 5, 1)
    print(f"   Ray (0,0,0)→(0,0,1), Sphere center=(0,0,5) r=1")
    print(f"   交点 t = {t:.2f} (z={t:.2f})")
    print("   → 光线在 z=4 处击中球面（5-1=4）")


# ================================================================
# Part III Bioinformatics
# ================================================================

def p3_bioinformatics():
    """Needleman-Wunsch 全局比对"""
    print("\n📋 Part III Bioinformatics: 序列比对 (Needleman-Wunsch)")
    def needleman_wunsch(s1, s2, match=1, mismatch=-1, gap=-2):
        n, m = len(s1), len(s2)
        dp = [[0]*(m+1) for _ in range(n+1)]
        for i in range(1, n+1): dp[i][0] = dp[i-1][0] + gap
        for j in range(1, m+1): dp[0][j] = dp[0][j-1] + gap
        for i in range(1, n+1):
            for j in range(1, m+1):
                s = match if s1[i-1] == s2[j-1] else mismatch
                dp[i][j] = max(dp[i-1][j-1]+s, dp[i-1][j]+gap, dp[i][j-1]+gap)
        return dp[n][m]

    score = needleman_wunsch("GATTACA", "GCATGCU")
    print(f"   GATTACA vs GCATGCU: 最优比对分数 = {score}")


# ================================================================
# Part III Hoare Logic & Model Checking
# ================================================================

def p3_hoare_logic():
    """Hoare 三元组验证"""
    print("\n📋 Part III Hoare Logic: {P} S {Q}")
    # {x=N} x := x+1 {x=N+1}
    N = 5
    x = N  # 前置条件 x=N
    x = x + 1  # 程序
    assert x == N + 1  # 后置条件
    print(f"   {{x = {N}}} x := x+1 {{x = {N+1}}}")
    print(f"   验证: x={x}, 后置条件成立? {x == N+1}")
    print("   Hoare 1969 CACM: {P}S{Q} = 若 P 成立且 S 终止, 则 Q 成立")


# ================================================================
# Part III Optimising Compilers
# ================================================================

def p3_optimising_compilers():
    """常量传播 + 死代码消除"""
    print("\n📋 Part III Optimising Compilers: 常量传播")
    code = [
        ("x", "=", "5"),
        ("y", "=", "x", "+", "3"),
        ("z", "=", "y", "*", "2"),
        ("w", "=", "z", "-", "10"),
    ]
    const_env = {}
    optimized = []
    for stmt in code:
        if len(stmt) == 3 and stmt[2].isdigit():
            const_env[stmt[0]] = int(stmt[2])
            optimized.append((stmt[0], int(stmt[2])))
        elif len(stmt) == 5:
            var, op, val = stmt[2], stmt[3], stmt[4]
            if var in const_env:
                if val in const_env:
                    val = const_env[val]
                if op == "+": result = const_env[var] + int(val)
                elif op == "-": result = const_env[var] - int(val)
                elif op == "*": result = const_env[var] * int(val)
                const_env[stmt[0]] = result
                optimized.append((stmt[0], result))
    print("   原始: x=5; y=x+3; z=y*2; w=z-10")
    print("   常量传播后:")
    for var, val in optimized:
        print(f"     {var} = {val}")
    print(f"   → 全部编译期计算, 运行时零计算!")


# ================================================================
# Part III Quantum Computing
# ================================================================

def p3_quantum_computing():
    """Grover 算法概念演示"""
    print("\n📋 Part III Quantum Computing: Grover 搜索")
    # 经典搜索 N 个无序项: O(N)
    # Grover 量子搜索: O(√N)
    for N in [100, 10000, 1000000]:
        classical = N
        quantum = math.sqrt(N)
        speedup = classical / quantum
        print(f"   N={N:>10,}: 经典={classical:>10,} 步, Grover={quantum:>8.0f} 步, "
              f"加速={speedup:.0f}x")
    print("   → 量子搜索提供平方根加速！")


# ================================================================
# Part III Concepts of Programming Languages
# ================================================================

def p3_concepts_pl():
    """Lambda calculus + Church 编码"""
    print("\n📋 Part III Concepts of PL: Lambda Calculus")
    # Church numerals (Python 模拟)
    church_zero = lambda f: lambda x: x
    church_succ = lambda n: lambda f: lambda x: f(n(f)(x))
    church_add = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
    church_mult = lambda m: lambda n: lambda f: m(n(f))

    def to_int(n): return n(lambda x: x+1)(0)

    three = church_succ(church_succ(church_succ(church_zero)))
    five = church_add(three)(church_succ(church_succ(church_zero)))
    fifteen = church_mult(three)(five)
    print(f"   Church 3 = {to_int(three)}")
    print(f"   3 + 2 = {to_int(five)}")
    print(f"   3 × 5 = {to_int(fifteen)}")
    print("   → 只用 lambda 就能表示所有自然数运算")


# ================================================================
# Part III Multicore Semantics
# ================================================================

def p3_multicore_semantics():
    """弱内存模型"""
    print("\n📋 Part III Multicore Semantics: 弱内存模型")
    # x86-TSO: Store Buffer 可重排
    # 线程1: x=1; r1=y  vs  线程2: y=1; r2=x
    # SC 下不可能 r1=0 且 r2=0，但 TSO 下可以！
    print("   Thread 1: x=1; r1=y")
    print("   Thread 2: y=1; r2=x")
    print("   SC (顺序一致): 不可能 r1=0 且 r2=0")
    print("   TSO (x86): Store Buffer → r1=0 且 r2=0 可能发生!")
    print("   → 多核编程不能假设 SC, 需要 memory barrier")


# ================================================================
# Part III Logics of Computation
# ================================================================

def p3_logics_of_computation():
    """线性逻辑"""
    print("\n📋 Part III Logics of Computation: 线性逻辑")
    # 线性逻辑: 每个假设恰好用一次
    # 普通 → 允许复制和丢弃
    # 线性 ⊸ 每个资源用恰好一次
    print("   直觉逻辑: A → A ∧ A (可以复制资源)")
    print("   线性逻辑: A ⊸ A (资源恰好用一次)")
    print("   Girard 1987: 资源敏感的逻辑")
    print("   应用: 并发、量子计算、会话类型")


# ================================================================
# Part III Computer Security
# ================================================================

def p3_computer_security():
    """侧信道攻击概念"""
    print("\n📋 Part III Computer Security: 侧信道")
    # 时序攻击: 密码比较耗时泄露信息
    def vulnerable_compare(stored, input_pwd):
        for i in range(min(len(stored), len(input_pwd))):
            if stored[i] != input_pwd[i]:
                return False
            # 每个字符匹配花费时间
        return len(stored) == len(input_pwd)

    def constant_time_compare(stored, input_pwd):
        result = len(stored) ^ len(input_pwd)
        for i in range(min(len(stored), len(input_pwd))):
            result |= stored[i] ^ input_pwd[i]
        return result == 0

    stored = b"secret123"
    print(f"   存储: {stored}")
    print("   普通比较: 逐字符 → 匹配越多耗时越长 → 泄露前缀!")
    print("   常数时间: XOR 累积 → 无论匹配多少耗时相同")


# ================================================================
# Part III Advanced Systems Research
# ================================================================

def p3_advanced_systems():
    """CAP 定理 + 分布式共识"""
    print("\n📋 Part III Advanced Systems: CAP 定理")
    print("   CAP: 一致性(C) + 可用性(A) + 分区容忍(P) 只能选 2")
    systems = {
        "CP": "Spanner, HBase, MongoDB (一致+分区容忍)",
        "AP": "Cassandra, DynamoDB, CouchDB (可用+分区容忍)",
        "CA": "单机 MySQL (无分区, 局域网)",
    }
    for cap, examples in systems.items():
        print(f"   {cap}: {examples}")
    print("   Brewer 2000 PODC: 分布式系统不可能三者兼顾")


# ================================================================
# 主入口
# ================================================================

def run_all_grad():
    print("=" * 64)
    print("🎓 Cambridge CST Part III / MPhil 研究生微项目")
    print("=" * 64)
    p3_advanced_graphics()
    p3_bioinformatics()
    p3_hoare_logic()
    p3_optimising_compilers()
    p3_quantum_computing()
    p3_concepts_pl()
    p3_multicore_semantics()
    p3_logics_of_computation()
    p3_computer_security()
    p3_advanced_systems()
    print("\n" + "=" * 64)
    print("✅ 全部研究生课程完成！")
    print("=" * 64)


if __name__ == "__main__":
    run_all_grad()
