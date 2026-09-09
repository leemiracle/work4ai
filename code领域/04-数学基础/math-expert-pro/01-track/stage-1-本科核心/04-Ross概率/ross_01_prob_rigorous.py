"""
Ross 概率核心 1: 严格概率 + 不等式
====================================
阶段1 / 模块04 / Ross 第1弹
区别 math-expert W5-W6 (直觉/分布族): 这里强调严格定义 + 不等式 + 证明
运行: python3 ross_01_prob_rigorous.py  (4 张 PNG)

§1 随机变量 + CDF 的严格性质
§2 期望严格定义 + 线性性 + Jensen 不等式
§3 矩母函数 M(t)=E[e^(tX)]: 生成所有矩的工具
§4 Markov / Chebyshev 不等式 (大数定律的预备)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
rng = np.random.default_rng(42)


# §1 CDF 严格性质
def section_1_cdf():
    print("=" * 70)
    print("§1 随机变量 + 累积分布函数 CDF 的严格性质")
    print("=" * 70)
    print("""
    随机变量 X: 把随机试验结果映射成数字。
    CDF (累积分布函数): F(x) = P(X ≤ x)
    严格性质 (4 条):
      1. 非降: x₁<x₂ ⟹ F(x₁)≤F(x₂)
      2. 右连续: F(x+) = F(x)
      3. lim_{x→-∞} F(x) = 0
      4. lim_{x→+∞} F(x) = 1
    任何满足这 4 条的函数都是某个随机变量的 CDF (反过来也对)。
    """)
    # 对比离散 vs 连续 CDF
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    # 离散: 伯努利(0.3) CDF 阶梯
    p = 0.3
    xs = np.linspace(-1, 2, 500)
    cdf_disc = np.where(xs < 0, 0, np.where(xs < 1, 1-p, 1))
    axes[0].step(xs, cdf_disc, where='post', lw=2.5)
    axes[0].set_title('离散 CDF (Bernoulli 0.3): 阶梯\n右连续, 跳跃在取值点')
    axes[0].set_ylim(-0.05, 1.1); axes[0].grid(True, ls=':', alpha=0.3)
    axes[0].axhline(0, color='gray', lw=0.5); axes[0].axhline(1, color='gray', lw=0.5)
    # 连续: 标准正态 CDF
    from scipy.stats import norm
    axes[1].plot(xs * 2, norm.cdf(xs * 2), 'C1', lw=2.5)
    axes[1].set_title('连续 CDF (标准正态): 光滑\nPDF 的积分')
    axes[1].set_ylim(-0.05, 1.1); axes[1].grid(True, ls=':', alpha=0.3)
    axes[1].axhline(0, color='gray', lw=0.5); axes[1].axhline(1, color='gray', lw=0.5)
    plt.tight_layout(); plt.savefig('ross_pr_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_pr_s1.png")


# §2 期望严格 + Jensen
def section_2_expectation():
    print("\n" + "=" * 70)
    print("§2 期望严格定义 + 线性性 + Jensen")
    print("=" * 70)
    print("""
    E[X] = Σx·P(X=x)   (离散)
    E[X] = ∫x·f(x)dx   (连续)
    线性性 (最重要!): E[aX+bY] = aE[X]+bE[Y]  (无论 X,Y 是否独立)
    Jensen 不等式: 若 g 凸, E[g(X)] ≥ g(E[X])
      例 g(x)=x²: E[X²] ≥ (E[X])²  (方差非负的根源!)
    """)
    samples = rng.standard_normal(100000)
    EX = samples.mean()
    EX2 = (samples ** 2).mean()
    print(f"  标准正态样本 1e5 个:")
    print(f"    E[X] = {EX:.4f} (理论 0)")
    print(f"    E[X²] = {EX2:.4f} (理论 1)")
    print(f"    Var(X) = E[X²] - (E[X])² = {EX2 - EX**2:.4f} (理论 1)")
    print(f"    Jensen (凸 g=x²): E[X²]={EX2:.4f} ≥ (E[X])²={EX**2:.6f} ✓")
    # 验证线性性: E[2X+3] = 2E[X]+3
    Y = 2 * samples + 3
    print(f"    线性性 E[2X+3]={Y.mean():.4f} = 2·{EX:.4f}+3={2*EX+3:.4f} ✓")

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.linspace(-3, 3, 200)
    ax.plot(xs, xs ** 2, 'C0', lw=2.5, label='g(x)=x² (凸)')
    ax.plot(EX, EX ** 2, 'ro', ms=12, label=f'g(E[X])={(EX**2):.4f}')
    ax.axhline(EX2, color='green', ls='--', lw=2, label=f'E[g(X)]={EX2:.4f}')
    ax.annotate('Jensen: E[g(X)] ≥ g(E[X])\n(切线在下方 = 凸性)', xy=(0, 1), fontsize=12)
    ax.set_xlabel('x'); ax.set_ylabel('g(x)'); ax.legend()
    ax.set_title('Jensen 不等式: 凸函数下 E[g(X)] ≥ g(E[X])\n(方差 = 这个 gap)')
    ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_pr_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_pr_s2.png")


# §3 矩母函数
def section_3_mgf():
    print("\n" + "=" * 70)
    print("§3 矩母函数: 生成所有矩的工具")
    print("=" * 70)
    print("""
    矩母函数 M(t) = E[e^(tX)]
    性质 (神奇!): M^(n)(0) = E[X^n]  (n 阶导在 0 = n 阶矩)
      M'(0) = E[X]    (一阶矩 = 期望)
      M''(0) = E[X²]  (二阶矩)
    标准正态 N(0,1): M(t) = exp(t²/2)
      M'(t) = t·exp(t²/2), M'(0)=0=E[X] ✓
      M''(0)=1=E[X²] ✓
    MGF 唯一决定分布 (若两 RV 的 MGF 相同, 它们同分布)。
    这是阶段 2 概率严格化 (测度论) 的关键工具。
    """)
    samples = rng.standard_normal(100000)
    # 数值 MGF: M(t) = E[e^(tX)]
    ts = np.linspace(-1, 1, 50)
    M_num = np.array([np.mean(np.exp(t * samples)) for t in ts])
    M_ana = np.exp(ts ** 2 / 2)
    print(f"  数值 MGF vs 解析 exp(t²/2), 最大误差 = {np.max(np.abs(M_num - M_ana)):.4f}")
    # 数值验证 M'(0) = E[X], M''(0) = E[X²]
    h = 0.001
    M_prime_0 = (np.mean(np.exp(h*samples)) - np.mean(np.exp(-h*samples))) / (2*h)
    M_double_prime_0 = (np.mean(np.exp(h*samples)) - 2 + np.mean(np.exp(-h*samples))) / h**2
    print(f"  M'(0) 数值 = {M_prime_0:.4f} (应=E[X]≈0)")
    print(f"  M''(0) 数值 = {M_double_prime_0:.4f} (应=E[X²]≈1)")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ts, M_ana, 'C2', lw=2.5, label='解析 M(t)=exp(t²/2)')
    ax.plot(ts, M_num, 'r--', lw=1.5, label='数值 E[e^(tX)]')
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_xlabel('t'); ax.set_ylabel('M(t)'); ax.legend()
    ax.set_title('矩母函数: M(t)=E[e^(tX)]\nM^(n)(0)=E[X^n] (导数在 0 = 矩)')
    ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_pr_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_pr_s3.png")


# §4 Markov / Chebyshev 不等式
def section_4_inequalities():
    print("\n" + "=" * 70)
    print("§4 Markov / Chebyshev 不等式 (大数定律的预备)")
    print("=" * 70)
    print("""
    Markov (最简单): X≥0 时, P(X≥a) ≤ E[X]/a
    Chebyshev (核心): P(|X-μ|≥kσ) ≤ 1/k²
      例 k=2: P(|X-μ|≥2σ) ≤ 1/4 = 25%  (实际正态仅 4.6%, 不等式保守)
    意义: 不需要知道分布, 只用期望/方差就能给「尾巴概率」上界!
    这是大数定律证明的关键工具 (阶段 1 #9 会用)。
    """)
    samples = rng.standard_normal(100000)
    mu, sigma = 0, 1
    # Chebyshev vs 实际
    ks = np.array([1, 1.5, 2, 2.5, 3, 4])
    actual = np.array([np.mean(np.abs(samples - mu) >= k * sigma) for k in ks])
    chebyshev = 1 / ks ** 2
    print(f"  {'k':>4} {'实际 P(|X-μ|≥kσ)':>20} {'Chebyshev 上界':>18} {'紧度':>8}")
    for k, a, c in zip(ks, actual, chebyshev):
        print(f"  {k:>4} {a:>20.4f} {c:>18.4f} {a/c:>8.2f}")
    print("  → 不等式保守但通用 (任何分布都成立), 实际正态远低于上界")

    # Markov: X=|N(0,1)| (非负), E[X]=sqrt(2/π)≈0.8
    abs_samples = np.abs(samples)
    EX = abs_samples.mean()
    a_vals = np.array([1, 1.5, 2, 2.5, 3])
    actual_markov = np.array([np.mean(abs_samples >= a) for a in a_vals])
    markov_bound = EX / a_vals
    print(f"\n  Markov (X=|N(0,1)|, E[X]={EX:.4f}):")
    print(f"  {'a':>4} {'实际 P(X≥a)':>14} {'Markov 上界':>14}")
    for a, am, mb in zip(a_vals, actual_markov, markov_bound):
        print(f"  {a:>4} {am:>14.4f} {mb:>14.4f}")

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.semilogy(ks, actual, 'o-', lw=2, ms=8, label='实际 P(|X-μ|≥kσ) (正态)')
    ax.semilogy(ks, chebyshev, 's--', lw=2, ms=8, label='Chebyshev 上界 1/k²')
    ax.set_xlabel('k (σ 倍数)'); ax.set_ylabel('P (log)')
    ax.set_title('Chebyshev 不等式: 保守但通用的尾巴上界\n(任何分布都成立, 大数定律的证明工具)')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_pr_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_pr_s4.png")
    print("\n  💡 Markov/Chebyshev 是「不知道分布」时的最强工具。")
    print("     阶段 1 #9 (极限定理) 会用 Chebyshev 证明弱大数定律。")


if __name__ == "__main__":
    print("🎲 Ross 核心 1: 严格概率 + 不等式  |  阶段1 / 模块04\n")
    section_1_cdf()
    section_2_expectation()
    section_3_mgf()
    section_4_inequalities()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 ross_01_prob_rigorous.md, 做练习")
    print("=" * 70)
