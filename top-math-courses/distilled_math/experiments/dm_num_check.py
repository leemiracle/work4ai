# -*- coding: utf-8 -*-
"""
dm_num_check.py — 蒸馏卡 DM-NUM-01《数论》§4 机器验证
对应卡片: distilled_math/DM-NUM-01-数论.md
断言计数: 15（NUM-01 ~ NUM-15）
运行方式: python3 dm_num_check.py
依赖: sympy
置信含义: 全过 → 卡内对应断言可标 ★（= 有限实例机器抽查通过，非定理证明，见 METHODOLOGY §六）
浮点断言（NUM-15 PNT）带 10% 相对容差。
"""
from math import log, factorial
from sympy import isprime, factorint, primerange, legendre_symbol
from sympy.ntheory.modular import crt

PASS = []

def check(name, cond):
    assert cond, f"FAIL: {name}"
    PASS.append(name)
    print(f"  [PASS] {name}")

def mult_order(a, n):
    """a mod n 的乘法阶（要求 gcd(a,n)=1）"""
    cur, k = a % n, 1
    while cur != 1:
        cur = cur * a % n; k += 1
    return k

print("== NUM-01~04: Fermat 小定理 / 伪素数 / Carmichael ==")
primes = [3, 5, 7, 11, 13, 97]
check("NUM-01 Fermat 小定理实例: p ∈ {3,5,7,11,13,97} 均有 2^(p-1) ≡ 1 (mod p)",
      all(pow(2, p - 1, p) == 1 for p in primes))
check("NUM-02 伪素数 341: 341 = 11·31 是合数, 但 2^340 ≡ 1 (mod 341)",
      factorint(341) == {11: 1, 31: 1} and pow(2, 340, 341) == 1)
check("NUM-03 Fermat 测试换底即穿帮: 3^340 mod 341 = 56 ≠ 1（341 不是 base-3 伪素数）",
      pow(3, 340, 341) == 56)
check("NUM-04 Carmichael 数 561 = 3·11·17: 对互素底 a ∈ {2,5,7,13} 均有 a^560 ≡ 1 (mod 561)",
      factorint(561) == {3: 1, 11: 1, 17: 1}
      and all(pow(a, 560, 561) == 1 for a in (2, 5, 7, 13)))

print("== NUM-05~08: Fermat 数 / Euclid 素数无穷 ==")
F = [2 ** (2 ** n) + 1 for n in range(6)]
check("NUM-05 Fermat 数: F0..F4 = 3,5,17,257,65537 全素; F5 = 641·6700417 合（Euler）",
      F[:5] == [3, 5, 17, 257, 65537] and all(isprime(f) for f in F[:5])
      and factorint(F[5]) == {641: 1, 6700417: 1})
from math import gcd
check("NUM-06 恒等式 F0·F1·…·F_{n-1} = F_n − 2（n=1..5 逐个验证）",
      all(__import__('math').prod(F[:n]) == F[n] - 2 for n in range(1, 6)))
check("NUM-07 F0..F5 两两互素（15 对 gcd 全为 1）→ 素数无穷的 Fermat 路线",
      all(gcd(F[i], F[j]) == 1 for i in range(6) for j in range(i + 1, 6)))
P6 = [2, 3, 5, 7, 11, 13]
N6 = 2 * 3 * 5 * 7 * 11 * 13 + 1
fac6 = factorint(N6)
check("NUM-08 Euclid 构造实例: 2·3·5·7·11·13+1 = 30031 = 59·509, 新素因子不在原列表",
      N6 == 30031 and set(fac6) == {59, 509} and not (59 in P6 or 509 in P6))

print("== NUM-09: Wilson 定理 ==")
check("NUM-09 Wilson: 素数 p ∈ {5,7,11} 有 (p-1)! ≡ -1 (mod p); 合数 8 有 7! ≡ 0 (mod 8)",
      all(factorial(p - 1) % p == p - 1 for p in (5, 7, 11))
      and factorial(7) % 8 == 0)

print("== NUM-10/11: 二次互反律 / Euler 判据 ==")
odd_primes = list(primerange(3, 48))  # 3..47 共 14 个
pairs = [(p, q) for p in odd_primes for q in odd_primes if p < q]
ok_qr = all(legendre_symbol(p, q) * legendre_symbol(q, p)
            == (-1) ** ((p - 1) // 2 * (q - 1) // 2) for p, q in pairs)
check("NUM-10 二次互反律实例: p<q ≤ 47 共 91 对全部吻合 (p/q)(q/p) = (-1)^{…}",
      len(pairs) == 91 and ok_qr)
p13 = 13
ok_ec = all(pow(a, 6, p13) % p13 == legendre_symbol(a, p13) % p13
            for a in range(1, p13))
check("NUM-11 Euler 判据实例: p=13, a=1..12: a^6 ≡ (a/13) (mod 13)",
      ok_ec)

print("== NUM-12: 原根 ==")
def smallest_primitive_root(p):
    for g in range(2, p):
        if mult_order(g, p) == p - 1:
            return g
check("NUM-12 原根存在实例: (Z/p)* 循环, 最小原根 mod 7/11/13/17 分别为 3/2/2/3",
      [smallest_primitive_root(p) for p in (7, 11, 13, 17)] == [3, 2, 2, 3])

print("== NUM-13: 中国剩余定理（孙子定理） ==")
res = crt([3, 5, 7], [2, 3, 2])
check("NUM-13 CRT: x≡2 (mod 3), x≡3 (mod 5), x≡2 (mod 7) → x ≡ 23 (mod 105)",
      res == (23, 105))

print("== NUM-14/15: 素数计数与 PNT ==")
pi100 = len(list(primerange(2, 100)))
pi1k = len(list(primerange(2, 1000)))
check("NUM-14 π(100)=25, π(1000)=168", pi100 == 25 and pi1k == 168)
X = 10 ** 6
piX = len(list(primerange(2, X)))
approx = X / log(X)
rel_err = abs(piX - approx) / piX
check("NUM-15 PNT 数值: π(10^6)=78498, x/ln x=72382, 相对误差 7.8% < 10% 容差",
      piX == 78498 and rel_err < 0.10)
print(f"    π(10^6) = {piX}, x/ln x = {approx:.1f}, rel err = {rel_err:.3%}")

print(f"\n全部通过: {len(PASS)}/15 条断言")
print("（★ 含义 = 实例级机器抽查通过；定理级确证归 L3 Lean，见 METHODOLOGY §六）")
