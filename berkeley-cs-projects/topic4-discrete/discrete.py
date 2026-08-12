"""
CS 70 Discrete Mathematics & Probability — UC Berkeley
================================================
覆盖主题：
- 数论 / 模算术 / 扩展欧几里得 / RSA（Lec 3-5）
- 图论 / Erdős（Lec 6-7）
- 马尔可夫链 + 平稳分布（Lec 17-20）
- 组合计数 / Stirling 估计（Lec 11-12）

核心教材/参考：
- Rivest, Shamir, Adleman "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems" CACM 1978
- Mitzenmacher & Upfal "Probability and Computing" 2nd ed (Cambridge 2017), Ch 7 Markov chains
- Erdős & Rényi "On Random Graphs I" Publ Math Debrecen 6 (1959)

本文件实现：
- 扩展欧几里得 + 模逆元
- Miller-Rabin 素数检测 + RSA 加解密
- Erdős–Rényi G(n,p) 随机图 + 连通性阈值
- Markov chain 平稳分布（power iteration）
- Stirling 近似 + 阶乘误差分析

运行：
    python discrete.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict


# ============================================================
# 1. 数论：扩展欧几里得 + 模逆元（CS 70 Lec 4）
# ============================================================

def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    扩展欧几里得：返回 (g, x, y) 使得 a*x + b*y = g = gcd(a,b)
    递归关系：gcd(a,b) = gcd(b, a mod b)
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def mod_inverse(a: int, m: int) -> int:
    """模逆元：a^{-1} mod m，要求 gcd(a,m)=1"""
    g, x, _ = ext_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"No inverse: gcd({a},{m})={g}")
    return x % m


def mod_pow(base: int, exp: int, mod: int) -> int:
    """快速模幂（square-and-multiply）"""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod
        exp >>= 1
        base = base * base % mod
    return result


# ============================================================
# 2. Miller-Rabin + RSA（CS 70 Lec 5）
# ============================================================

def is_prime_miller_rabin(n: int, k: int = 20) -> bool:
    """Miller-Rabin 素数检测（概率性，错误率 < 4^{-k}）"""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    # n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int = 16) -> int:
    """生成 bits 位的素数"""
    while True:
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime_miller_rabin(candidate):
            return candidate


class RSA:
    """
    RSA (Rivest-Shamir-Adleman 1978):
    - 选 p, q 大素数
    - n = p*q, φ(n) = (p-1)(q-1)
    - e 与 φ(n) 互素，d = e^{-1} mod φ(n)
    - 加密: c = m^e mod n;  解密: m = c^d mod n
    正确性：m^{ed} = m (mod n) by Fermat/Euler
    """
    def __init__(self, bits: int = 16):
        self.p = generate_prime(bits)
        self.q = generate_prime(bits)
        while self.q == self.p:
            self.q = generate_prime(bits)
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.e = 65537
        while ext_gcd(self.e, self.phi)[0] != 1:
            self.e += 2
        self.d = mod_inverse(self.e, self.phi)

    def encrypt(self, m: int) -> int:
        return mod_pow(m, self.e, self.n)

    def decrypt(self, c: int) -> int:
        return mod_pow(c, self.d, self.n)


# ============================================================
# 3. Erdős–Rényi 随机图 G(n,p)（CS 70 Lec 6-7）
# ============================================================

def erdos_renyi_graph(n: int, p: float) -> dict[int, set[int]]:
    """
    G(n,p)：n 个节点，每条边以概率 p 独立存在。
    反直觉：连通性阈值在 p = ln(n)/n 附近突变。
    """
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def is_connected(adj: dict[int, set[int]]) -> bool:
    """BFS 判断连通性"""
    nodes = list(adj.keys())
    if not nodes:
        return True
    visited = set()
    queue = [nodes[0]]
    visited.add(nodes[0])
    while queue:
        u = queue.pop(0)
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return len(visited) == len(nodes)


def connected_fraction(n: int, p: float, trials: int = 50) -> float:
    """估计 G(n,p) 连通的概率"""
    connected = 0
    for _ in range(trials):
        g = erdos_renyi_graph(n, p)
        if is_connected(g):
            connected += 1
    return connected / trials


# ============================================================
# 4. Markov Chain + 平稳分布（CS 70 Lec 17-20）
# ============================================================

def markov_stationary(transition: list[list[float]],
                       iterations: int = 10000,
                       tol: float = 1e-10) -> list[float]:
    """
    power iteration 求 π = π P (平稳分布)。
    收敛定理：不可约非周期马尔可夫链有唯一平稳分布。
    """
    n = len(transition)
    pi = [1.0 / n] * n  # uniform start
    for _ in range(iterations):
        new_pi = [0.0] * n
        for j in range(n):
            for i in range(n):
                new_pi[j] += pi[i] * transition[i][j]
        # 收敛检查
        diff = sum(abs(new_pi[i] - pi[i]) for i in range(n))
        pi = new_pi
        if diff < tol:
            break
    return pi


# ============================================================
# 5. Stirling 近似（CS 70 Lec 11）
# ============================================================

def stirling_approx(n: int) -> float:
    """
    Stirling: n! ≈ sqrt(2πn) * (n/e)^n
    用于估计大数阶乘和对数。
    """
    return math.sqrt(2 * math.pi * n) * (n / math.e) ** n


def log_factorial_exact(n: int) -> float:
    """精确 log(n!)"""
    return sum(math.log(k) for k in range(1, n + 1))


def log_stirling(n: int) -> float:
    """Stirling 对数版"""
    return 0.5 * math.log(2 * math.pi * n) + n * math.log(n / math.e)


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 70 Discrete Math Demo")
    print("=" * 60)
    random.seed(42)

    # 1. Ext GCD
    print("\n📋 1. 扩展欧几里得")
    for a, b in [(35, 15), (1071, 462), (240, 46)]:
        g, x, y = ext_gcd(a, b)
        print(f"   gcd({a},{b}) = {g} = {a}*{x} + {b}*{y}  ✓{a*x+b*y==g}")
    # 模逆
    inv = mod_inverse(3, 11)
    print(f"   3^(-1) mod 11 = {inv} (验证: 3*{inv} mod 11 = {3*inv%11})")

    # 2. RSA
    print("\n📋 2. RSA（小素数演示）")
    rsa = RSA(bits=16)
    print(f"   p = {rsa.p}, q = {rsa.q}, n = {rsa.n}")
    print(f"   e = {rsa.e}, d = {rsa.d}")
    message = 12345
    cipher = rsa.encrypt(message)
    decrypted = rsa.decrypt(cipher)
    print(f"   明文 = {message}")
    print(f"   密文 = {cipher}")
    print(f"   解密 = {decrypted} ✓" if decrypted == message else f"   FAIL")

    # 3. Erdős–Rényi 相变
    print("\n📋 3. Erdős–Rényi G(n,p) 连通性相变")
    n = 40
    threshold = math.log(n) / n
    print(f"   n = {n}, 理论阈值 p* = ln(n)/n = {threshold:.4f}")
    for factor in [0.3, 0.7, 1.0, 1.3, 2.0]:
        p = factor * threshold
        cf = connected_fraction(n, p, trials=30)
        print(f"   p = {factor:.1f}*p* = {p:.4f} → P(connected) = {cf:.0%}")

    # 4. Markov chain
    print("\n📋 4. Markov Chain 平稳分布")
    # PageRank-like: 3 状态
    P = [
        [0.0, 0.5, 0.5],   # A → B/C
        [0.3, 0.4, 0.3],   # B → A/B/C
        [0.6, 0.2, 0.2],   # C → A/B/C
    ]
    pi = markov_stationary(P)
    print(f"   转移矩阵:")
    for row in P:
        print(f"     {row}")
    print(f"   平稳分布 π = [{', '.join(f'{x:.4f}' for x in pi)}]")
    # 验证 π = πP
    piP = [sum(pi[i] * P[i][j] for i in range(3)) for j in range(3)]
    print(f"   验证 πP  = [{', '.join(f'{x:.4f}' for x in piP)}]")

    # 5. Stirling
    print("\n📋 5. Stirling 阶乘近似")
    for nn in [5, 10, 50, 100]:
        exact = log_factorial_exact(nn)
        approx = log_stirling(nn)
        err = abs(exact - approx)
        print(f"   {nn:>3}!  log_exact={exact:.4f}  log_stirling={approx:.4f}  误差={err:.4f}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print(f"   Erdős–Rényi 图 n={n} 的连通性不是随 p 线性变化，")
    print(f"   而是在 p* = ln({n})/{n} = {threshold:.4f} 附近发生尖锐相变：")
    print(f"   p = 0.7*p* 时几乎不连通，p = 1.3*p* 时几乎总连通。")
    print("   这是'阈值函数'现象：离散数学中的相变，类似水的冰点。")
    print("   小世界网络、社交图、神经网络连通性都遵循类似阈值律。")
    print()
    print("   Stirling 近似的相对误差随 n 增大而减小（n=100 误差<1%），")
    print("   这就是为什么密码学家用 Stirling 估计组合数。")


if __name__ == "__main__":
    demo()
