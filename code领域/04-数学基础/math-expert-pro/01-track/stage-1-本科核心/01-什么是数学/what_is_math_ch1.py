"""
《什么是数学》第1章: 自然数 — 用程序验证经典数论直觉
======================================================
阶段1 / 模块01 / 第1章
目标: 用 numpy/matplotlib 把柯朗的数论直觉可视化、可验证
运行: python3 what_is_math_ch1.py  (生成 4 张 PNG)

学习路径:
  §1 数学归纳法: 数学里的「for 循环」(程序员最熟悉的递归形式)
  §2 素数与厄拉多塞筛法 + 素数定理 π(n) ~ n/ln(n)
  §3 同余 / 费马小定理 / 模运算 (RSA 密码的数学根基)
  §4 数论奇观: 完美数 / 孪生素数 / 梅森素数 (引出未解之谜)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ═══════════════════════════════════════════════════════════════════
# §1  数学归纳法
# ═══════════════════════════════════════════════════════════════════
def section_1_induction():
    print("=" * 70)
    print("§1 数学归纳法: 数学里的「for 循环」")
    print("=" * 70)
    print("""
    数学归纳法 = 证明「对所有自然数 n 成立」的标准工具:
      基础: P(1) 成立
      归纳: P(n) 成立 ⟹ P(n+1) 成立
      结论: ∀n P(n) 成立

    直觉: 多米诺骨牌。推倒第 1 块 (基础), 且每块倒下会推倒下一块 (归纳),
          则所有骨牌都会倒 (结论)。
    程序员视角: 这就是递归! 基础 = base case, 归纳 = 递推关系。

    经典命题: 1+3+5+...+(2n-1) = n²  (前 n 个奇数和 = n 的平方)
    """)
    for n in [1, 2, 5, 10, 20]:
        s = sum(2*k - 1 for k in range(1, n + 1))
        print(f"    n={n:>2}: 奇数和={s:>4}, n²={n**2:>4}, 相等? {s == n**2}")

    print("""
    归纳证明:
      基础 n=1: 1 = 1² ✓
      归纳: 假设 1+3+...+(2n-1) = n²
            则 1+3+...+(2n-1)+(2n+1) = n² + (2n+1) = (n+1)² ✓
      所以对所有 n 成立。QED.
    几何直觉: 奇数和能拼成越来越大的正方形点阵 (L 形增量)。
    """)

    # 可视化: L 形拼正方形
    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    for ax, n in zip(axes, [1, 2, 3, 4]):
        for i in range(n):
            for j in range(n):
                layer = max(i, j)
                ax.plot(j + 1, n - i, 's',
                        color=plt.cm.viridis(layer / max(n - 1, 1)), ms=22)
        ax.set_xlim(0, n + 1); ax.set_ylim(0, n + 1)
        ax.set_aspect('equal')
        ax.set_title(f'n={n}: {n}×{n}={n**2} 点\n(每色 = 一个奇数)')
        ax.axis('off')
    plt.suptitle('数学归纳法的几何: 前 n 个奇数和 = n² (L 形拼正方形)')
    plt.tight_layout(); plt.savefig('wim_ch1_section1_induction.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch1_section1_induction.png")


# ═══════════════════════════════════════════════════════════════════
# §2  素数与筛法
# ═══════════════════════════════════════════════════════════════════
def section_2_primes():
    print("\n" + "=" * 70)
    print("§2 素数与厄拉多塞筛法")
    print("=" * 70)
    print("""
    素数: >1 的自然数, 只能被 1 和自己整除。数论的「原子」。
    算术基本定理: 任何 n>1 唯一分解为素数之积 (n 的「DNA」)。

    厄拉多塞筛法 (古希腊!): 找 ≤N 所有素数的高效算法
      1. 列 2..N
      2. 2 是素数, 划掉所有 2 的倍数
      3. 下一个未划掉的是 3 (素数), 划掉 3 的倍数
      4. 重复到 √N
    程序员视角: 经典算法, 复杂度 O(N log log N)。

    素数定理 (里程碑!): ≤N 的素数个数 π(N) ~ N/ln(N)
    """)

    def sieve(N):
        is_p = np.ones(N + 1, bool); is_p[:2] = False
        for i in range(2, int(N ** 0.5) + 1):
            if is_p[i]:
                is_p[i * i::i] = False
        return np.where(is_p)[0]

    N = 1000
    primes = sieve(N)
    print(f"  厄拉多塞筛法找 ≤{N} 的素数: 共 {len(primes)} 个")
    print(f"  前 20 个素数: {primes[:20].tolist()}")
    approx = N / np.log(N)
    print(f"  π({N}) = {len(primes)},  N/ln(N) = {approx:.1f},  "
          f"相对误差 {abs(len(primes) - approx) / len(primes) * 100:.1f}%")

    pi_N = np.array([np.sum(primes <= n) for n in range(2, N + 1)])
    xs = np.arange(2, N + 1)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(xs, pi_N, 'C0', lw=2, label='实际 π(n) (筛法)')
    axes[0].plot(xs, xs / np.log(xs), 'r--', lw=2, label='近似 n/ln(n)')
    axes[0].set_xlabel('n'); axes[0].set_ylabel('素数个数')
    axes[0].set_title(f'素数定理: π(n) ~ n/ln(n)\n({N} 内实际 {len(primes)} vs 近似 {approx:.0f})')
    axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.3)
    axes[1].vlines(primes[:200], 0, 1, colors='red', lw=0.8)
    for p in primes[:18]:
        axes[1].annotate(str(p), (p, 1.05), fontsize=7, rotation=90, ha='center', va='bottom')
    axes[1].set_xlabel('素数'); axes[1].set_yticks([]); axes[1].set_ylim(0, 1.5)
    axes[1].set_title('前 200 个素数: 分布越来越稀疏\n(但永不穷尽 — 欧几里得证明)')
    axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch1_section2_primes.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch1_section2_primes.png")


# ═══════════════════════════════════════════════════════════════════
# §3  同余与费马小定理
# ═══════════════════════════════════════════════════════════════════
def section_3_congruence():
    print("\n" + "=" * 70)
    print("§3 同余 / 费马小定理 / RSA 雏形")
    print("=" * 70)
    print("""
    同余: a ≡ b (mod n)  ⟺  a, b 除以 n 余数相同
    例: 17 ≡ 5 (mod 12)  (都是时钟 5 点)
    这是「时钟算术」 — 只关心余数。

    费马小定理 (数论明珠): 若 p 是素数, gcd(a,p)=1, 则
        a^(p-1) ≡ 1 (mod p)
    例: p=5, a=2: 2^4 = 16 = 3×5+1 ≡ 1 (mod 5) ✓

    为什么重要? 这是现代密码学 (RSA) 的数学根基:
      加密 = 用大素数 p 造锁, 用 a^(p-1)≡1 解锁
      破解 = 分解大整数 (极难) → 锁的安全
    """)
    print(f"  费马小定理验证 (a^(p-1) mod p 应恒=1):")
    for p in [5, 7, 11, 13]:
        results = [pow(a, p - 1, p) for a in range(1, p)]
        print(f"    p={p}: a=1..{p-1}, a^{p-1} mod p = {results}, 全=1? {all(r == 1 for r in results)} ✓")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    theta_clock = np.linspace(0, 2 * np.pi, 13)[:-1]
    for i, t in enumerate(theta_clock):
        axes[0].plot(np.cos(t), np.sin(t), 'o', color='steelblue', ms=22)
        axes[0].text(1.18 * np.cos(t), 1.18 * np.sin(t), str(i),
                     ha='center', va='center', fontsize=10)
    axes[0].set_aspect('equal'); axes[0].set_xlim(-1.5, 1.5); axes[0].set_ylim(-1.5, 1.5)
    axes[0].set_title('模 12 时钟: 17 ≡ 5 (mod 12)\n(同余 = 同一位置)')
    axes[0].axis('off')
    for p in [5, 7, 11, 13, 17, 19]:
        ys = [pow(a, p - 1, p) for a in range(1, p)]
        axes[1].scatter(range(1, p), ys, label=f'p={p}', s=22)
    axes[1].axhline(1, color='red', ls='--', label='恒=1 (费马小定理)')
    axes[1].set_xlabel('a'); axes[1].set_ylabel('a^(p-1) mod p')
    axes[1].set_title('费马小定理: 对素数 p, a^(p-1) mod p 恒为 1')
    axes[1].legend(fontsize=8); axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch1_section3_congruence.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch1_section3_congruence.png")


# ═══════════════════════════════════════════════════════════════════
# §4  数论奇观
# ═══════════════════════════════════════════════════════════════════
def section_4_wonders():
    print("\n" + "=" * 70)
    print("§4 数论奇观: 完美数 / 孪生素数 / 梅森素数")
    print("=" * 70)
    print("""
    数论之美: 简单定义 → 深邃未解之谜。

    完美数: n = 其真因子之和。例: 6=1+2+3, 28=1+2+4+7+14
      偶完美数 = 2^(p-1)·(2^p-1), 其中 2^p-1 是梅森素数 (欧几里得发现!)
      未解: 是否存在奇完美数? (至今无人找到, 也未证明不存在)

    孪生素数: (p, p+2) 都是素数。例 (3,5),(5,7),(11,13)
      未解: 是否无穷多? (2013 张益唐证明「间隔有界的素数对无穷」)

    梅森素数: 2^p-1 (p 素数)。已知最大素数几乎都是这种。
    """)
    def divisors_sum(n):
        return sum(d for d in range(1, n) if n % d == 0)
    perfects = [n for n in range(2, 10000) if divisors_sum(n) == n]
    print(f"  ≤10000 的完美数: {perfects}")
    for n in perfects:
        for p in range(2, 20):
            if n == 2 ** (p - 1) * (2 ** p - 1):
                print(f"    {n} = 2^{p-1} × (2^{p}-1) = 2^{p-1} × {2**p-1}, "
                      f"p={p} ({2**p-1} 是梅森素数)")
                break

    def sieve_set(N):
        is_p = np.ones(N + 1, bool); is_p[:2] = False
        for i in range(2, int(N ** 0.5) + 1):
            if is_p[i]:
                is_p[i * i::i] = False
        return set(np.where(is_p)[0])
    P = sieve_set(10000)
    twins = [(p, p + 2) for p in sorted(P) if p + 2 in P]
    print(f"\n  ≤10000 的孪生素数对数: {len(twins)}")
    print(f"  前 10 对: {twins[:10]}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].bar(range(len(perfects)), perfects, color='gold')
    for i, n in enumerate(perfects):
        axes[0].text(i, n, str(n), ha='center', va='bottom', fontsize=9)
    axes[0].set_xticks(range(len(perfects)))
    axes[0].set_xticklabels([f'第{i+1}个' for i in range(len(perfects))])
    axes[0].set_title('完美数 (前 4 个, 都遵循 2^(p-1)·(2^p-1))\n奇完美数是否存在? — 数学未解之谜')
    axes[0].set_yscale('log'); axes[0].grid(True, ls=':', alpha=0.3)
    cum = []
    cnt = 0
    for n in range(2, 10001):
        if n in P and (n + 2) in P:
            cnt += 1
        cum.append(cnt)
    axes[1].plot(range(2, 10001), cum, 'C1')
    axes[1].set_xlabel('n'); axes[1].set_ylabel('≤n 的孪生素数对数')
    axes[1].set_title(f'孪生素数累计 (≤10000 共 {len(twins)} 对)\n张益唐 2013: 间隔有界的素数对无穷')
    axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch1_section4_wonders.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch1_section4_wonders.png")
    print("\n  💡 这就是柯朗《什么是数学》的精神:")
    print("     简单定义 (素数/因子) → 程序验证 → 引出未解之谜 (完美数/孪生素数)")
    print("     数学的乐趣 = 在已知里发现未知。")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🔢 《什么是数学》第1章: 自然数  |  阶段1 / 模块01\n")
    section_1_induction()
    section_2_primes()
    section_3_congruence()
    section_4_wonders()
    print("\n" + "=" * 70)
    print("✅ 第1章跑通! 下一步: 读 ch01-自然数.md 笔记, 做 exercises.md")
    print("=" * 70)
