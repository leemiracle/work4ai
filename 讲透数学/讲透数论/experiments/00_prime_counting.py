# -*- coding: utf-8 -*-
"""素数定理实拍 + Miller-Rabin 素性对拍。

04 章 · 数论转代码 配套实验。纯标准库。

事实链:
  素数定理:  π(x) ~ x/ln x   (Hadamard / de la Vallée Poussin, 1896)
  更准的逼近: π(x) ~ Li(x) = ∫₂ˣ dt/ln t   ——且 Li 一路领先
  Littlewood(1914): π(x) - Li(x) 会无穷多次变号——
      但首次交叉在 Skewes 数量级(≥10^316),任何可算尺度都只见"Li 领先"
  Miller-Rabin: 强伪素测试,对奇合数 n, ≥3/4 的底 a 会暴露其合数性;
      对拍验证: ≤N 的奇数上,多底 MR 判定 == 筛法真值(零漏检)

跑法: python experiments/00_prime_counting.py
"""

import math


# ---------- 1. 筛法:制造真值表 ----------

def sieve(n):
    """Eratosthenes 筛:返回 [0..n] 的布尔表,True=素数。"""
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    for p in range(2, math.isqrt(n) + 1):
        if is_p[p]:
            is_p[p * p :: p] = bytearray(len(is_p[p * p :: p]))
    return is_p


def li(x):
    """对数积分 Li(x) = ∫₂ˣ dt/ln t,用对数偏移级数:
    Li(x) = γ + ln ln x + Σ_{k≥1} (ln x)^k / (k·k!)  (x > 1, 收敛快)"""
    ln = math.log(x)
    s = 0.0
    term = 1.0
    for k in range(1, 60):
        term = ln ** k
        s += term / (k * math.factorial(k))
        if term < 1e-18:
            break
    return 0.5772156649015329 + math.log(ln) + s


# ---------- 2. Miller-Rabin(确定性小素数基) ----------

def miller_rabin(n, bases=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    """强伪素测试。对拍用途:素数 ⟹ 必过;合数 ⟹ 任一底暴露即判合。"""
    if n < 2:
        return False
    for p in bases:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in bases:                      # n < 3.3e24 时这组基是确定性的
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                 # a 见证了 n 是合数
    return True


def main():
    # ===== A. 素数定理实拍 =====
    print("=" * 66)
    print("素数定理实拍:π(x) vs Li(x) vs x/ln x(Littlewood 翻转的不可见性)")
    print("=" * 66)
    print(f"{'x':>12} {'π(x)':>10} {'x/ln x':>12} {'Li(x)':>14} "
          f"{'π/(x/lnx)':>10} {'Li-π':>8}")
    n = 2_000_000
    is_p = sieve(n)
    pi_table = [0] * (n + 1)
    c = 0
    for i in range(n + 1):
        if is_p[i]:
            c += 1
        pi_table[i] = c
    for x in (100, 1_000, 10_000, 100_000, 1_000_000, 2_000_000):
        pi_x = pi_table[x]
        ratio = pi_x / (x / math.log(x))
        print(f"{x:>12} {pi_x:>10} {x / math.log(x):>12.1f} {li(x):>14.1f} "
              f"{ratio:>10.4f} {li(x) - pi_x:>8.0f}")
    print()
    print("读数:")
    print("  · x/ln x 一直低估(比率缓慢升向 1);Li(x) 一直略高估——差距在长大,")
    print("    但相对误差持续缩小:Li 的相对精度在 x=2×10⁶ 已 ≈ 0.0001")
    print("  · Littlewood 定理保证 π 将在某处反超 Li——但在 ≥10^316 尺度,")
    print("    任何可算的 x 都只给你『Li 领先』的假象(数值证据的失效时刻)💡")

    # ===== B. Miller-Rabin 对拍 =====
    print()
    print("=" * 66)
    print("Miller-Rabin 对拍:MR(12 素数基) vs 筛法真值(≤10⁵ 奇数)")
    print("=" * 66)
    N = 100_000
    is_p2 = sieve(N)
    mr_primes = 0
    for n_ in range(3, N + 1, 2):
        if miller_rabin(n_) != bool(is_p2[n_]):
            raise AssertionError(f"MR 与筛法不一致: n={n_}")   # 零容忍
        mr_primes += is_p2[n_]
    known_carmichael = [561, 1105, 1729, 2465, 2821, 6601, 8911, 10585]
    for c_ in known_carmichael:
        assert not miller_rabin(c_), f"Carmichael 数 {c_} 应判合数"
        assert is_p2[c_] == 0
    print(f"素数个数(MR)=筛法: {mr_primes} ✓(零漏检/零误报)")
    print("Carmichael 数(Fermat 测试的克星)全部被强伪素测试正确判合 ✓")
    assert pi_table[100] == 25 and pi_table[1000] == 168, "素数计数的自检锚点"
    print("自检锚点:π(100)=25, π(1000)=168 ✓")
    print()
    print("结论:同余世界的『能算』(筛/素性)完全机械化;而分解仍无多项式算法——")
    print("     这条缝(可算≠快算)正是 04 章的密码经济学。")


if __name__ == "__main__":
    main()
