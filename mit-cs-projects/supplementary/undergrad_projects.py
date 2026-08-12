"""
MIT EECS 补充课程微项目集 — 本科基础/进阶（undergrad_projects.py）
覆盖课程：
- 6.100B/6.0001 Intro Python (进阶)
- 6.01 SICP via Python
- 6.02 Intro to EECS II (Communications)
- 6.0002 Intro to Computational Thinking (stats)
- 6.009 Fundamentals of Programming (old)
- 6.031 Elements of Software Construction
- 18.06 Linear Algebra
- 18.600 Probability
- 6.042J Math for Computer Science
- 6.005 Software Construction (old)
"""
import math
import random
from collections import Counter


# ============ 6.100B / 6.0001 Intro Python (进阶) ============

def mit6_100b_recursion_backtracking():
    """递归回溯：N-Queens"""
    print("\n📋 6.100B: N-Queens 回溯")
    def solve_nqueens(n):
        cols = set(); diag1 = set(); diag2 = set()
        solutions = []
        def backtrack(row, placement):
            if row == n:
                solutions.append(placement[:])
                return
            for col in range(n):
                if col in cols or row-col in diag1 or row+col in diag2:
                    continue
                cols.add(col); diag1.add(row-col); diag2.add(row+col)
                placement.append(col)
                backtrack(row+1, placement)
                placement.pop(); cols.discard(col); diag1.discard(row-col); diag2.discard(row+col)
        backtrack(0, [])
        return solutions
    for n in [4, 5, 6, 8]:
        sols = solve_nqueens(n)
        print(f"  {n}-Queens: {len(sols)} 解, 一例: {sols[0] if sols else 'N/A'}")


# ============ 6.01 SICP via Python ============

def mit6_01_oop_and_state():
    """OOP + 状态：模拟银行账户"""
    print("\n📋 6.01: OOP 银行账户 + 状态")
    class Account:
        def __init__(self, owner, balance=0):
            self.owner = owner; self.balance = balance; self.history = []
        def deposit(self, amt):
            self.balance += amt
            self.history.append(('deposit', amt))
            return self.balance
        def withdraw(self, amt):
            if amt > self.balance:
                return "Insufficient funds"
            self.balance -= amt
            self.history.append(('withdraw', amt))
            return self.balance
    acc = Account("Alice", 100)
    acc.deposit(50); acc.withdraw(30); acc.deposit(200)
    print(f"  {acc.owner}: 余额=${acc.balance}, 操作 {len(acc.history)} 次")
    print(f"  历史: {acc.history}")


# ============ 6.02 Communications ============

def mit6_02_hamming_code():
    """Hamming(7,4) 纠错码"""
    print("\n📋 6.02: Hamming(7,4) 纠错码")
    # G: 生成矩阵 (4→7), H: 校验矩阵 (3×7)
    # 编码 4 bit data → 7 bit codeword
    def hamming_encode(data):
        d = data
        p1 = d[0] ^ d[1] ^ d[3]
        p2 = d[0] ^ d[2] ^ d[3]
        p3 = d[1] ^ d[2] ^ d[3]
        return [p1, p2, d[0], p3, d[1], d[2], d[3]]
    def hamming_syndrome(received):
        s1 = received[0] ^ received[2] ^ received[4] ^ received[6]
        s2 = received[1] ^ received[2] ^ received[5] ^ received[6]
        s3 = received[3] ^ received[4] ^ received[5] ^ received[6]
        return s1 + s2*2 + s3*4  # 错误位置 (0=无错)
    def hamming_correct(received):
        pos = hamming_syndrome(received)
        if pos == 0:
            return received
        corrected = received[:]
        corrected[pos-1] ^= 1  # 翻转错误位
        return corrected

    data = [1, 0, 1, 1]
    encoded = hamming_encode(data)
    print(f"  data={data} → encoded={encoded}")
    # 引入 1-bit 错误
    corrupted = encoded[:]
    corrupted[3] ^= 1
    print(f"  引入错误 bit3: {corrupted}")
    pos = hamming_syndrome(corrupted)
    print(f"  syndrome={pos} → 错误在位置 {pos}")
    corrected = hamming_correct(corrupted)
    print(f"  纠正后: {corrected} == 原始? {corrected == encoded}")


# ============ 6.0002 Stats ============

def mit6_0002_monte_carlo():
    """Monte Carlo 估算 π"""
    print("\n📋 6.0002: Monte Carlo π")
    random.seed(42)
    n = 100000
    inside = 0
    for _ in range(n):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1:
            inside += 1
    pi_est = 4 * inside / n
    print(f"  {n} 次采样: π ≈ {pi_est:.4f} (误差 {abs(pi_est - math.pi):.4f})")


# ============ 6.009 Fundamentals of Programming ============

def mit6_009_generators():
    """生成器：无限序列"""
    print("\n📋 6.009: 生成器与惰性求值")
    def fibonacci():
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    def take(gen, n):
        result = []
        for i, v in enumerate(gen):
            if i >= n: break
            result.append(v)
        return result
    fibs = take(fibonacci(), 15)
    print(f"  前 15 个 Fibonacci: {fibs}")
    # 无限素数生成器
    def primes():
        yield 2
        known = [2]
        candidate = 3
        while True:
            if all(candidate % p for p in known if p*p <= candidate):
                known.append(candidate)
                yield candidate
            candidate += 2
    print(f"  前 10 个素数: {take(primes(), 10)}")


# ============ 6.031/6.005 Software Construction ============

def mit6_031_testing():
    """软件测试：等价类划分 + 边界值"""
    print("\n📋 6.031: 测试设计 (等价类 + 边界值)")
    def is_leap_year(year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    # 等价类: 被4整除不被100 / 被400整除 / 不被4整除 / 被100不被400
    test_cases = [
        (2000, True),   # 被400整除
        (1900, False),  # 被100不被400
        (2024, True),   # 被4不被100
        (2023, False),  # 不被4
        (1600, True),   # 被400
        (1800, False),  # 被100不被400
    ]
    passed = 0
    for year, expected in test_cases:
        result = is_leap_year(year)
        ok = "✓" if result == expected else "✗"
        if result == expected: passed += 1
        print(f"  {year}: leap={result} (期望 {expected}) {ok}")
    print(f"  通过: {passed}/{len(test_cases)}")


# ============ 18.06 Linear Algebra ============

def mit18_06_gauss_elimination():
    """高斯消元解线性方程组"""
    print("\n📋 18.06: 高斯消元")
    def gauss_solve(A, b):
        n = len(A)
        # 增广矩阵
        M = [row[:] + [b[i]] for i, row in enumerate(A)]
        # 前向消元
        for col in range(n):
            # partial pivoting
            max_row = max(range(col, n), key=lambda r: abs(M[r][col]))
            M[col], M[max_row] = M[max_row], M[col]
            if abs(M[col][col]) < 1e-12:
                return None  # singular
            for row in range(col+1, n):
                factor = M[row][col] / M[col][col]
                for j in range(col, n+1):
                    M[row][j] -= factor * M[col][j]
        # 回代
        x = [0] * n
        for i in range(n-1, -1, -1):
            x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i+1, n))) / M[i][i]
        return x
    A = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
    b = [8, -11, -3]
    x = gauss_solve(A, b)
    print(f"  Ax=b, A={A}, b={b}")
    print(f"  解 x = {[round(v, 4) for v in x]}")
    # 验证
    check = [sum(A[i][j] * x[j] for j in range(3)) for i in range(3)]
    print(f"  验证 Ax = {[round(v, 4) for v in check]} == b? {all(abs(a-b) < 1e-8 for a, b in zip(check, b))}")


# ============ 18.600 Probability ============

def mit18_600_birthday_problem():
    """生日悖论"""
    print("\n📋 18.600: 生日悖论")
    def birthday_prob(n, trials=10000):
        collisions = 0
        for _ in range(trials):
            birthdays = [random.randint(1, 365) for _ in range(n)]
            if len(set(birthdays)) < n:
                collisions += 1
        return collisions / trials
    for n in [10, 23, 30, 50, 70]:
        prob = birthday_prob(n)
        # 理论值
        theory = 1
        for i in range(n):
            theory *= (365 - i) / 365
        theory = 1 - theory
        print(f"  n={n:>2}: 模拟碰撞率={prob:.1%}, 理论={theory:.1%}")


# ============ 6.042J Math for CS ============

def mit6_042_graph_theory():
    """图论：欧拉路径检测"""
    print("\n📋 6.042J: 欧拉路径")
    def has_euler_path(adj):
        # 欧拉路径存在条件：恰好 0 或 2 个奇度顶点
        odd = sum(1 for v in adj if len(adj[v]) % 2 == 1)
        return odd == 0 or odd == 2
    # 哥尼斯堡七桥 (欧拉说不行)
    konigsberg = {'A': ['B','B','C'], 'B': ['A','A','C'], 'C': ['A','B','D','D'], 'D': ['C','C']}
    # 正确的度数
    degrees = {v: len(adj) for v, adj in konigsberg.items()}
    print(f"  哥尼斯堡: 度数={degrees}")
    print(f"  有欧拉路径? {has_euler_path({v: list(range(d)) for v, d in degrees.items()})}")
    # 简单图 (有欧拉回路)
    simple = {'A': [0,1], 'B': [0,1], 'C': [0,1], 'D': [0,1]}
    print(f"  所有偶度图: 有欧拉路径? {has_euler_path(simple)}")


# ============ 主入口 ============

def run_undergrad():
    print("=" * 65)
    print("🎓 MIT EECS 本科补充课程微项目")
    print("=" * 65)
    mit6_100b_recursion_backtracking()
    mit6_01_oop_and_state()
    mit6_02_hamming_code()
    mit6_0002_monte_carlo()
    mit6_009_generators()
    mit6_031_testing()
    mit18_06_gauss_elimination()
    mit18_600_birthday_problem()
    mit6_042_graph_theory()
    print("\n" + "=" * 65)
    print("✅ 本科补充课程完成！")
    print("=" * 65)


if __name__ == "__main__":
    run_undergrad()
