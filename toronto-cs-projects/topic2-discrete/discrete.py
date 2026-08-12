"""
CSC 165 / CSC 236 Discrete Mathematics & Proofs (University of Toronto)
=======================================================================
覆盖主题：
- 谓词逻辑与量词（∀, ∃）
- 数学归纳法（弱归纳 + 强归纳）
- 渐近复杂度阶（O, Ω, Θ）
- 递推求解（Master Theorem）
- Gödel 不完备性 + Turing 机模拟

核心教材：
- "Mathematics for Computer Science" by Lehman, Leighton, Meyer (MIT)
- Cormen et al. "Introduction to Algorithms" Ch.3-4 (CLRS)

本文件实现：
- 谓词逻辑求值器
- 归纳法验证器（自动验证前 k 项）
- Master Theorem 求解器
- Gödel 编码/解码
- Turing 机模拟器

运行：
    python discrete.py
"""
from __future__ import annotations
import math


# ============ 1. 谓词逻辑 ============

def predicate_evaluator():
    """
    谓词逻辑求值器
    验证：∀x ∈ ℕ, ∃y ∈ ℕ, y > x（自然数无上界）
    """
    print("📋 1. 谓词逻辑")
    # ∀x ∈ {1..10}, ∃y ∈ {1..20}, y > x
    domain_x = list(range(1, 11))
    domain_y = list(range(1, 21))
    # P(x, y) = y > x
    all_hold = True
    for x in domain_x:
        exists = any(y > x for y in domain_y)
        if not exists:
            all_hold = False
            break
    print(f"   ∀x∈{{1..10}}, ∃y∈{{1..20}}, y>x: {all_hold}")

    # 德摩根律验证：¬(∀x P(x)) ≡ ∃x ¬P(x)
    P = lambda x: x % 2 == 0
    neg_forall = not all(P(x) for x in domain_x)
    exists_neg = any(not P(x) for x in domain_x)
    print(f"   ¬(∀x P(x)) = {neg_forall}, ∃x ¬P(x) = {exists_neg}, 等价: {neg_forall == exists_neg}")

    # 命题逻辑真值表
    print("\n   命题逻辑真值表：p→q ≡ ¬p∨q")
    print(f"   {'p':>5} {'q':>5} {'p→q':>5} {'¬p∨q':>5} {'等价':>5}")
    for p in [True, False]:
        for q in [True, False]:
            implies = (not p) or q
            equiv = (not p) or q
            print(f"   {str(p):>5} {str(q):>5} {str(implies):>5} {str(equiv):>5} {str(implies == equiv):>5}")


# ============ 2. 数学归纳法 ============

def induction_verifier():
    """
    归纳法自动验证器
    验证经典恒等式的前 N 项
    """
    print("\n📋 2. 数学归纳法验证")

    # 定理1：Σ i = n(n+1)/2
    N = 100
    ok1 = all(sum(range(1, n + 1)) == n * (n + 1) // 2 for n in range(1, N + 1))
    print(f"   Σ(i=1..n) = n(n+1)/2  [n=1..{N}]: {'✓' if ok1 else '✗'}")

    # 定理2：Σ i² = n(n+1)(2n+1)/6
    ok2 = all(sum(i ** 2 for i in range(1, n + 1)) == n * (n + 1) * (2 * n + 1) // 6 for n in range(1, N + 1))
    print(f"   Σ(i²) = n(n+1)(2n+1)/6 [n=1..{N}]: {'✓' if ok2 else '✗'}")

    # 定理3：Σ i³ = (n(n+1)/2)²
    ok3 = all(sum(i ** 3 for i in range(1, n + 1)) == (n * (n + 1) // 2) ** 2 for n in range(1, N + 1))
    print(f"   Σ(i³) = [n(n+1)/2]²    [n=1..{N}]: {'✓' if ok3 else '✗'}")

    # 定理4：2^n > n²  当 n ≥ 5
    ok4 = all(2 ** n > n ** 2 for n in range(5, N + 1))
    boundary = [n for n in range(1, 20) if 2 ** n > n ** 2]
    print(f"   2^n > n²  [n≥5]:         {ok4}, 临界点 n={boundary[0]}")


# ============ 3. 渐近复杂度 ============

def complexity_analysis():
    """
    渐近复杂度阶验证
    """
    print("\n📋 3. 渐近复杂度分析")

    def time_sort(algo, n):
        """返回操作次数"""
        if algo == "bubble":
            return n * (n - 1) // 2
        elif algo == "merge":
            return int(n * math.log2(n)) if n > 0 else 0
        elif algo == "radix":
            return 10 * n  # d=10 passes
        elif algo == "binary_search":
            return int(math.log2(n)) if n > 0 else 0

    algos = {
        "Bubble Sort O(n²)": "bubble",
        "Merge Sort O(n log n)": "merge",
        "Radix Sort O(dn)": "radix",
        "Binary Search O(log n)": "binary_search",
    }
    sizes = [10, 100, 1000, 10000, 100000]
    print(f"   {'Algorithm':<25}", end="")
    for s in sizes:
        print(f"{'n='+str(s):>10}", end="")
    print()
    for name, algo in algos.items():
        print(f"   {name:<25}", end="")
        for s in sizes:
            ops = time_sort(algo, s)
            print(f"{ops:>10,}", end="")
        print()

    # 反直觉发现
    print(f"\n   反直觉：n=100,000 时：")
    print(f"   Bubble 需要 {time_sort('bubble', 100000):,} 次比较")
    print(f"   Merge 需要 {time_sort('merge', 100000):,} 次比较")
    print(f"   → Bubble 是 Merge 的 {time_sort('bubble', 100000) / time_sort('merge', 100000):.0f}x！")


# ============ 4. Master Theorem ============

def master_theorem(a: int, b: int, f_n_exp: float, n: int = 1000) -> str:
    """
    Master Theorem: T(n) = aT(n/b) + O(n^d)
    - a: 子问题个数
    - b: 每次缩小因子
    - f_n_exp: f(n) = O(n^d) 中的 d
    """
    # critical exponent: log_b(a)
    log_ba = math.log(a) / math.log(b)

    if f_n_exp < log_ba - 0.001:
        return f"O(n^{log_ba:.2f})  [Case 1: f(n) = O(n^{f_n_exp}), {f_n_exp} < log_{b}({a})={log_ba:.2f}]"
    elif abs(f_n_exp - log_ba) < 0.001:
        return f"O(n^{log_ba:.2f} log n)  [Case 2: f(n) = Θ(n^{f_n_exp}) = Θ(n^{{log_b a}})]"
    else:
        return f"O(n^{f_n_exp:.1f})  [Case 3: f(n) = Ω(n^{f_n_exp}), {f_n_exp} > log_{b}({a})={log_ba:.2f}]"


def demo_master():
    print("\n📋 4. Master Theorem")
    examples = [
        ("Merge Sort", 2, 2, 1.0),    # T(n) = 2T(n/2) + O(n)
        ("Binary Search", 1, 2, 0.0),  # T(n) = T(n/2) + O(1)
        ("Karatsuba", 3, 2, 1.0),      # T(n) = 3T(n/2) + O(n)
        ("Strassen Matrix Mul", 7, 2, 2.0),  # T(n) = 7T(n/2) + O(n²)
        ("Naive Matrix Mul", 8, 2, 2.0),     # T(n) = 8T(n/2) + O(n²)
    ]
    for name, a, b, d in examples:
        result = master_theorem(a, b, d)
        print(f"   {name}: T(n) = {a}T(n/{b}) + O(n^{d:g})")
        print(f"     → {result}")


# ============ 5. Gödel 编码 ============

def godel_encoding():
    """
    Gödel 编码：将符号序列编码为唯一自然数
    使用素数幂积：编码(p1, p2, ...) = 2^p1 * 3^p2 * 5^p3 * ...
    """
    print("\n📋 5. Gödel 编码")

    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    def encode(sequence: list[int]) -> int:
        result = 1
        for i, val in enumerate(sequence):
            result *= primes[i] ** val
        return result

    def decode(n: int, length: int) -> list[int]:
        result = []
        for p in primes[:length]:
            exp = 0
            while n % p == 0:
                n //= p
                exp += 1
            result.append(exp)
        return result

    # 编码 "1+1=2" → [1, 1, 1, 2] (简单映射)
    seq = [1, 1, 1, 2]
    code = encode(seq)
    decoded = decode(code, len(seq))
    print(f"   序列 {seq} → Gödel数: {code}")
    print(f"   解码: {decoded}, 一致: {seq == decoded}")
    print(f"   → Gödel数有 {len(str(code))} 位，展示了算术可编码任意符号串")


# ============ 6. Turing 机 ============

class TuringMachine:
    """
    简化 Turing 机
    实现：二进制递增（接受一个二进制串，输出+1后的二进制串）
    """
    def __init__(self, tape_str: str, rules: dict, initial_state: str, accept_state: str):
        # tape: dict of position -> symbol
        self.tape = {}
        for i, s in enumerate(tape_str):
            self.tape[i] = s
        self.head = 0
        self.state = initial_state
        self.rules = rules
        self.accept = accept_state
        self.steps = 0

    def read(self) -> str:
        return self.tape.get(self.head, 'B')  # B = blank

    def step(self) -> bool:
        symbol = self.read()
        key = (self.state, symbol)
        if key not in self.rules:
            return False
        new_state, write_sym, direction = self.rules[key]
        self.tape[self.head] = write_sym
        self.state = new_state
        self.head += 1 if direction == 'R' else -1
        self.steps += 1
        return self.state != self.accept

    def run(self, max_steps=1000) -> str:
        while self.steps < max_steps:
            if not self.step():
                break
        min_pos = min(self.tape.keys())
        max_pos = max(self.tape.keys())
        return ''.join(self.tape.get(i, 'B') for i in range(min_pos, max_pos + 1))


def demo_turing():
    print("\n📋 6. Turing 机（二进制递增）")
    # 状态: q0=初始, q1=向左扫描, qH=接受
    # 输入: 1011 → 输出: 1100
    rules = {
        # 初始状态：移到最右端
        ('q0', '0'): ('q0', '0', 'R'),
        ('q0', '1'): ('q0', '1', 'R'),
        ('q0', 'B'): ('q1', 'B', 'L'),  # 到了右端，向左走
        # q1：加1逻辑
        ('q1', '0'): ('qH', '1', 'R'),  # 0→1，结束
        ('q1', '1'): ('q1', '0', 'L'),  # 1→0，进位，继续左移
        ('q1', 'B'): ('qH', '1', 'R'),  # 全是1，最高位进1
    }
    for test in ['0', '1', '10', '11', '1011', '111']:
        tm = TuringMachine(test, rules, 'q0', 'qH')
        result = tm.run()
        result = result.strip('B')
        expected = bin(int(test, 2) + 1)[2:]
        print(f"   {test} + 1 = {result} (期望 {expected}, {'✓' if result == expected else '✗'})")


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 165/236: Discrete Math & Proofs Demo")
    print("=" * 60)

    predicate_evaluator()
    induction_verifier()
    complexity_analysis()
    demo_master()
    godel_encoding()
    demo_turing()

    print("\n✅ CSC 165/236 完成！")
    print("💡 覆盖：谓词逻辑 + 归纳法 + 复杂度阶 + Master + Gödel + Turing机")


if __name__ == "__main__":
    demo()
