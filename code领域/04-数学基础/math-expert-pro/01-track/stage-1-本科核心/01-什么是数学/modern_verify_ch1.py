# -*- coding: utf-8 -*-
"""《什么是数学》第1章 现代验证（柯朗 ch01）
用 Python 验证：欧几里得算法 / 同余 / 费马小定理 / RSA
风格延续 math-expert：section_N() / bash 跑通 / 断言 / 纯 Python 无依赖"""

# ---------- 纯 Python 工具（无外部依赖） ----------
def is_prime(n):
    """试除法判素（到 √n）"""
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True

def mod_inverse(e, phi):
    """扩展欧几里得求 e^(-1) mod phi"""
    def ext(a, b):
        if b == 0: return a, 1, 0
        g, x1, y1 = ext(b, a % b)
        return g, y1, x1 - (a // b) * y1
    g, x, _ = ext(e, phi)
    assert g == 1, f"{e} 与 {phi} 不互素，无逆元"
    return x % phi


# ---------- §1 欧几里得算法 ----------
def section_1_euclid():
    print("\n" + "="*60)
    print("【§1 欧几里得算法：辗转相除求 gcd + 扩展欧几里得】")
    print("="*60)

    # 迭代版 gcd
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    # 递归版（展示归纳结构 —— 和 ch01 归纳法呼应）
    def gcd_rec(a, b):
        return a if b == 0 else gcd_rec(b, a % b)

    # 扩展欧几里得：找 x,y 使 ax + by = gcd(a,b)（Bezout 恒等式）
    def ext_gcd(a, b):
        if b == 0:
            return a, 1, 0
        g, x1, y1 = ext_gcd(b, a % b)
        return g, y1, x1 - (a // b) * y1

    # 验证
    assert gcd(252, 105) == 21
    assert gcd_rec(252, 105) == 21
    g, x, y = ext_gcd(252, 105)
    assert g == 21 and 252 * x + 105 * y == 21

    print(f"gcd(252, 105) = {g}（迭代与递归一致）")
    print(f"递推步骤链：")
    a, b = 252, 105
    while b:
        print(f"  gcd({a}, {b}) → gcd({b}, {a % b})")
        a, b = b, a % b
    print(f"Bezout 恒等式：252×({x}) + 105×({y}) = {252*x + 105*y} = gcd ✓")
    print("\n→ 欧几里得算法 = 数学归纳法（递归）的典范")
    print("→ 扩展版给出 Bezout 系数，是求模逆元的工具（RSA 私钥就靠它）")


# ---------- §2 同余 ----------
def section_2_congruence():
    print("\n" + "="*60)
    print("【§2 同余：定义、性质、快速模幂】")
    print("="*60)

    a, b, n = 17, 23, 7
    # 同余保持加法与乘法
    assert (a + b) % n == ((a % n) + (b % n)) % n
    assert (a * b) % n == ((a % n) * (b % n)) % n
    print(f"17 + 23 = 40 ≡ {40 % 7} (mod 7)，而 17≡{17%7}、23≡{23%7}，{17%7}+{23%7}={17%7+23%7}≡{(17%7+23%7)%7}")
    print(f"17 × 23 = 391 ≡ {391 % 7} (mod 7)，而 {17%7}×{23%7}={17%7*23%7}≡{(17%7*23%7)%7}")

    # 快速模幂（Python 内置 pow(a,k,n) 是 O(log k) 的平方求幂）
    print(f"\n快速模幂 3^100 mod 7 = {pow(3, 100, 7)}（pow(a,k,n) 内置，O(log k)）")
    print(f"对照朴素算：3^100 是 {len(str(3**100))} 位数，朴素先算再 mod 极慢；快速幂每步取 mod，数永远 < n")

    # 威尔逊定理预告（p 素数 ⟺ (p-1)! ≡ -1 (mod p)）
    for p in [5, 7, 11, 13]:
        assert (math_factorial(p-1) % p) == (p - 1)
    print(f"\n威尔逊定理：(p-1)! ≡ -1 (mod p)：(4!,6!,10!,12!) mod (5,7,11,13) = "
          f"{math_factorial(4)%5}, {math_factorial(6)%7}, {math_factorial(10)%11}, {math_factorial(12)%13}（都是 p-1）")

    print("\n→ 同余把'无限大数'的运算压进 mod n 的有限范围 —— 这是数论计算的工程基础")


# ---------- §3 费马小定理 + 欧拉定理 ----------
def section_3_fermat():
    print("\n" + "="*60)
    print("【§3 费马小定理 + 欧拉定理】")
    print("="*60)

    # 费马小定理：p 素数、gcd(a,p)=1 ⟹ a^(p-1) ≡ 1 (mod p)
    print("费马小定理：若 p 素数且 gcd(a,p)=1，则 a^(p-1) ≡ 1 (mod p)")
    print("验证 2^(p-1) mod p：")
    for p in [5, 7, 11, 13, 97, 101, 7919, 104729]:
        if is_prime(p):
            r = pow(2, p-1, p)
            print(f"  2^{p-1} mod {p} = {r} {'✓ 等于 1' if r == 1 else '✗'}")
            assert r == 1

    # 费马素性测试（及其弱点：Carmichael 数）
    print("\n费马素性测试：若 a^(n-1) ≢ 1 (mod n)，则 n 必是合数")
    composite = 561  # 最小 Carmichael 数（合数但 a^(n-1)≡1 对所有互素 a 成立）
    print(f"  Carmichael 数 {composite}（合数但'伪装'成素数）：")
    print(f"    2^{composite-1} mod {composite} = {pow(2, composite-1, composite)}（=1，误判为素数！）")
    print(f"    但 {composite} = 3 × 11 × 17 = {3*11*17}（实际是合数）")
    print("  → 费马测试不可靠，需 Miller-Rabin 等更强测试")

    # 欧拉定理：gcd(a,n)=1 ⟹ a^φ(n) ≡ 1 (mod n)，φ 是欧拉函数
    print("\n欧拉定理（费马小定理的推广）：a^φ(n) ≡ 1 (mod n)，φ(n)=1..n 中与 n 互素的数的个数")
    def euler_phi(n):
        result = n
        p = 2
        tmp = n
        while p * p <= tmp:
            if tmp % p == 0:
                while tmp % p == 0:
                    tmp //= p
                result -= result // p
            p += 1
        if tmp > 1:
            result -= result // tmp
        return result
    for n in [9, 10, 12]:
        phi = euler_phi(n)
        a = next(a for a in range(2, n) if gcd_verify(a, n) == 1)
        assert pow(a, phi, n) == 1
        print(f"  φ({n}) = {phi}；取 a={a}（与 {n} 互素），{a}^φ({n}) mod {n} = {a}^{phi} mod {n} = {pow(a, phi, n)} ✓")
    print("→ 费马小定理是欧拉定理 n=素数 的特例（φ(p)=p-1）")


# ---------- §4 RSA ----------
def section_4_rsa():
    print("\n" + "="*60)
    print("【§4 RSA：用小素数演示公钥加密全流程】")
    print("="*60)

    # 1. 选两个素数
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    print(f"① 选素数 p={p}, q={q}")
    print(f"② n = pq = {n}（公开）；φ(n) = (p-1)(q-1) = {phi}（保密）")

    # 2. 公钥 e（与 φ 互素）
    e = 17
    assert gcd_verify(e, phi) == 1
    print(f"③ 公钥 e={e}（与 φ 互素）")

    # 3. 私钥 d = e^(-1) mod φ（扩展欧几里得）
    d = mod_inverse(e, phi)
    assert (e * d) % phi == 1
    print(f"④ 私钥 d = e^(-1) mod φ = {e}^(-1) mod {phi} = {d}")
    print(f"   验证：e×d mod φ = {e}×{d} mod {phi} = {(e*d) % phi} ✓")

    # 4. 加密 m → c = m^e mod n
    m = 42
    c = pow(m, e, n)
    print(f"⑤ 加密：明文 m={m} → 密文 c = m^e mod n = {m}^{e} mod {n} = {c}")

    # 5. 解密 c → m = c^d mod n
    m2 = pow(c, d, n)
    assert m == m2
    print(f"⑥ 解密：密文 c={c} → 明文 = c^d mod n = {c}^{d} mod {n} = {m2}")
    print(f"   还原：{m} == {m2} ✓")

    print(f"\nRSA 的全部数学：素数 + 欧拉函数 + 模逆元（扩展欧几里得）+ 快速模幂")
    print(f"安全性：攻击者知道 (e={e}, n={n})，要算 d 必须知道 φ(n)={phi}")
    print(f"       要算 φ(n)=(p-1)(q-1) 必须分解 n={n}={p}×{q}——大数分解极难")
    print(f"       （现实中 n 是 2048+ 位，分解需经典计算机数十亿年）")


# ---------- 辅助 ----------
def math_factorial(n):
    r = 1
    for i in range(2, n+1): r *= i
    return r

def gcd_verify(a, b):
    while b: a, b = b, a % b
    return a


if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  《什么是数学》第 1 章 · 现代验证（柯朗 ch01）           ║")
    print("║  Python 验证：欧几里得 / 同余 / 费马·欧拉 / RSA          ║")
    print("╚" + "═"*58 + "╝")
    section_1_euclid()
    section_2_congruence()
    section_3_fermat()
    section_4_rsa()
    print("\n" + "═"*60)
    print("✅ 全部 4 节验证通过。第 1 章数学全部用 Python 跑通。")
    print("═"*60)
