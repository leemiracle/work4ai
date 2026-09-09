"""
Ross 概率核心 2: 极限定理
============================
阶段1 / 模块04 / Ross 第2弹
衔接 #8 (Markov/Chebyshev) → 弱大数定律 → 强大数定律 → CLT → 蒙特卡洛
运行: python3 ross_02_limit_theorems.py  (4 张 PNG)

§1 弱大数定律 WLLN (Chebyshev 证明 + 掷骰收敛)
§2 强大数定律 SLLN (几乎必然收敛, 区别 WLLN)
§3 中心极限定理 CLT (标准化和 →d N(0,1))
§4 蒙特卡洛方法 (投点估 π, 误差 ~1/√n)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, kstest

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
rng = np.random.default_rng(42)


# §1 弱大数定律
def section_1_wlln():
    print("=" * 70)
    print("§1 弱大数定律 WLLN (用 #8 的 Chebyshev 证明)")
    print("=" * 70)
    print("""
    设 X₁..Xₙ iid, E[X_i]=μ, Var(X_i)=σ²。样本均值 X̄_n = (1/n)ΣX_i。
    WLLN: X̄_n → μ (依概率), 即 ∀ε>0: P(|X̄_n-μ|≥ε) → 0
    证明 (用 #8 的 Chebyshev):
      E[X̄_n] = μ  (期望线性性, #8 §2)
      Var(X̄_n) = σ²/n  (独立性)
      Chebyshev: P(|X̄_n-μ|≥ε) ≤ Var(X̄_n)/ε² = σ²/(nε²) → 0  ∎
    掷骰子: μ=3.5, σ²=35/12≈2.917, n→∞ 时 X̄_n→3.5
    """)
    mu = 3.5
    sigma2 = 35 / 12  # 掷骰方差
    n_traj = 5
    n_max = 1000000
    n_grid = np.unique(np.logspace(1, 6, 300).astype(int))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for t in range(n_traj):
        rolls = rng.integers(1, 7, size=n_max)
        cummean = np.cumsum(rolls).astype(float) / np.arange(1, n_max + 1)
        ax.plot(n_grid, cummean[n_grid - 1], lw=1.2, alpha=0.8, label=f'轨迹 {t + 1}')
    ax.axhline(mu, color='red', lw=2.5, ls='--', label=f'μ={mu} (理论)')
    ax.set_xscale('log')
    ax.set_xlabel('n (投掷次数, log)'); ax.set_ylabel('X̄_n (样本均值)')
    ax.set_title('弱大数定律 WLLN: X̄_n → μ=3.5 (依概率)\n5 条轨迹都收敛到 3.5')
    ax.legend(ncol=2); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_lt_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_lt_s1.png")
    # 断言: n=1e6 时 |X̄_n - 3.5| < 0.05
    big = rng.integers(1, 7, size=1000000)
    xbar = big.mean()
    bound = sigma2 / (1000000 * 0.05 ** 2)  # Chebyshev 上界 σ²/(nε²)
    print(f"  掷骰 n=1e6: X̄_n = {xbar:.5f}, |X̄_n - 3.5| = {abs(xbar - 3.5):.5f}")
    print(f"    理论 μ=3.5, Chebyshev 上界 σ²/(nε²) = {bound:.2e}")
    assert abs(xbar - 3.5) < 0.05, f"|X̄_n-3.5|={abs(xbar - 3.5)} 应<0.05"
    print("    ✓ 断言通过: |X̄_n - 3.5| < 0.05")


# §2 强大数定律
def section_2_slln():
    print("\n" + "=" * 70)
    print("§2 强大数定律 SLLN (几乎必然收敛)")
    print("=" * 70)
    print("""
    SLLN: P( lim_{n→∞} X̄_n = μ ) = 1   (几乎必然, almost surely / a.s.)
    意思: 一条轨迹上 X̄_n 最终「钉死」在 μ (不只是每个 n 大概率接近)。
    收敛强度关系:
      WLLN (依概率): 每个 ε, P(|X̄_n-μ|≥ε)→0  (允许轨迹偶尔抖动)
      SLLN (a.s.)  : 整条轨迹收敛            (抖动最终消失)
      a.s. ⟹ 依概率 (SLLN 比 WLLN 强!)
    严格证明 SLLN 需要测度论 (Borel-Cantelli / Kolmogorov 不等式), 阶段 2 再证。
    数值: 多条轨迹, 几乎所有都「钉」到 μ。
    """)
    mu = 3.5
    n_traj = 20
    n_max = 50000
    n_grid = np.unique(np.logspace(1, np.log10(n_max), 300).astype(int))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    final_devs = []
    for t in range(n_traj):
        rolls = rng.integers(1, 7, size=n_max)
        cummean = np.cumsum(rolls).astype(float) / np.arange(1, n_max + 1)
        ax.plot(n_grid, cummean[n_grid - 1], lw=0.8, alpha=0.6)
        final_devs.append(abs(cummean[-1] - mu))
    ax.axhline(mu, color='red', lw=2.5, ls='--', label=f'μ={mu}')
    ax.set_xscale('log')
    ax.set_xlabel('n (log)'); ax.set_ylabel('X̄_n')
    ax.set_title(f'强大数定律 SLLN: 20 条轨迹「几乎都」钉到 μ={mu}\n(a.s. 收敛: 抖动最终消失)')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_lt_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_lt_s2.png")
    final_devs = np.array(final_devs)
    print(f"  20 条轨迹 n={n_max} 末尾 |X̄_n-μ|:")
    print(f"    最大 = {final_devs.max():.4f}, 均值 = {final_devs.mean():.4f}")
    assert (final_devs < 0.1).all(), f"所有轨迹应收敛到 μ±0.1, 最大偏差 {final_devs.max()}"
    print(f"    ✓ 断言通过: 所有 20 条 |X̄_n-μ| < 0.1")


# §3 中心极限定理
def section_3_clt():
    print("\n" + "=" * 70)
    print("§3 中心极限定理 CLT ⭐")
    print("=" * 70)
    print("""
    CLT: X_i iid, E[X_i]=μ, Var(X_i)=σ²。标准化和
      Z_n = (ΣX_i - nμ) / (σ√n)  →d  N(0,1)  (n→∞)
    即「求和(无论原分布)标准化后趋向标准正态」。
    证明思路 (经典): 用特征函数, φ_{Z_n}(t) → e^(-t²/2) (N(0,1) 的 cf),
      由 MGF/特征函数唯一性 (#8 §3) → 收敛到 N(0,1)。阶段 2 测度论严格化。
    数值: U(0,1) 与 Poisson(1) 求和 n=30, 标准化, 直方图 vs N(0,1) PDF。
    """)
    mu, sigma = 0.5, np.sqrt(1 / 12)  # U(0,1)
    n_sum = 30
    m = 50000
    raw = rng.random((m, n_sum))  # U(0,1)
    Z = (raw.sum(axis=1) - n_sum * mu) / (sigma * np.sqrt(n_sum))
    ks_stat, ks_p = kstest(Z, 'norm')
    print(f"  U(0,1) 求和 n={n_sum}, m={m} 样本:")
    print(f"    标准化和: 均值={Z.mean():.4f} (理论 0), std={Z.std():.4f} (理论 1)")
    print(f"    KS 距离 vs N(0,1) = {ks_stat:.4f} (p={ks_p:.3f})")
    assert ks_stat < 0.05, f"KS={ks_stat} 应<0.05 (CLT 收敛)"
    print(f"    ✓ 断言通过: KS < 0.05 (n=30 已足够逼近正态)")
    # 泊松分布验证
    mu_p, sig_p = 1.0, 1.0  # Poisson(1): μ=σ²=1
    raw_p = rng.poisson(mu_p, size=(m, n_sum)).astype(float)
    Zp = (raw_p.sum(axis=1) - n_sum * mu_p) / (sig_p * np.sqrt(n_sum))
    ks_p_stat, _ = kstest(Zp, 'norm')
    print(f"  Poisson(1) 求和 n={n_sum}: KS = {ks_p_stat:.4f} (正态逼近)")
    print("  → 无论原分布(均匀/泊松), 求和标准化后都逼近 N(0,1) ✓")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    xs = np.linspace(-4, 4, 300)
    axes[0].hist(Z, bins=60, density=True, alpha=0.6, color='C0', label='标准化和 直方图')
    axes[0].plot(xs, norm.pdf(xs), 'r-', lw=2.5, label='N(0,1) PDF')
    axes[0].set_title(f'CLT: U(0,1) 求和 n={n_sum} 标准化 → N(0,1)\nKS={ks_stat:.4f}')
    axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.3)
    axes[1].hist(Zp, bins=60, density=True, alpha=0.6, color='C2', label='标准化和 直方图')
    axes[1].plot(xs, norm.pdf(xs), 'r-', lw=2.5, label='N(0,1) PDF')
    axes[1].set_title(f'CLT: Poisson(1) 求和 n={n_sum} 标准化 → N(0,1)\nKS={ks_p_stat:.4f}')
    axes[1].legend(); axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_lt_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_lt_s3.png")


# §4 蒙特卡洛
def section_4_montecarlo():
    print("\n" + "=" * 70)
    print("§4 蒙特卡洛方法 (CLT 的落地应用)")
    print("=" * 70)
    print("""
    投点法估 π: 在 [0,1]² 均匀投点, 落入 1/4 圆 x²+y²≤1 的比例 ≈ π/4。
      π_hat = 4 × (落入数 / 总数)
    误差来源 (CLT!): 单点指示 I~Bernoulli(π/4), π_hat = 4·Ī_n
      Var(π_hat) = 16·p(1-p)/n, std(π_hat) = O(1/√n)
    → 误差随 n 按 1/√n 衰减 (蒙特卡洛通用规律!)
    """)
    n_total = 200000
    pts = rng.random((n_total, 2))
    inside = (pts[:, 0] ** 2 + pts[:, 1] ** 2 <= 1).astype(float)
    cum_inside = np.cumsum(inside)
    n_vals = np.arange(1, n_total + 1)
    pi_hat = 4 * cum_inside / n_vals
    p = np.pi / 4
    std_envelope = 4 * np.sqrt(p * (1 - p)) / np.sqrt(n_vals)
    # 断言 n=2e5 相对误差 < 2%
    pi_final = pi_hat[-1]
    rel_err = abs(pi_final - np.pi) / np.pi
    print(f"  n={n_total}: π_hat = {pi_final:.5f}, 相对误差 = {rel_err * 100:.3f}%")
    print(f"    理论 π = {np.pi:.5f}")
    print(f"    CLT 预测 std(π_hat) = {4 * np.sqrt(p * (1 - p) / n_total):.5f} (~1/√n 衰减)")
    assert rel_err < 0.02, f"相对误差 {rel_err * 100:.2f}% 应<2%"
    print(f"    ✓ 断言通过: 相对误差 < 2%")
    # 误差 vs n 表
    check_ns = [1000, 10000, 100000, 200000]
    print(f"  {'n':>10} {'π_hat':>12} {'误差':>10} {'理论 std':>10}")
    for nv in check_ns:
        print(f"  {nv:>10} {pi_hat[nv - 1]:>12.4f} {abs(pi_hat[nv - 1] - np.pi):>10.4f} {std_envelope[nv - 1]:>10.4f}")
    print("  → 误差随 n 增大按 1/√n 衰减 (要精度×10, 样本要×100)")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    n_plot = np.logspace(2, np.log10(n_total), 400).astype(int)
    ax.plot(n_plot, pi_hat[n_plot - 1], 'C0', lw=1.2, label='π_hat(n)')
    ax.fill_between(n_plot, np.pi + std_envelope[n_plot - 1], np.pi - std_envelope[n_plot - 1],
                    alpha=0.25, color='C1', label='±1 std 包络 (~1/√n)')
    ax.axhline(np.pi, color='red', lw=2.5, ls='--', label=f'π={np.pi:.4f}')
    ax.set_xscale('log')
    ax.set_xlabel('n (投点数, log)'); ax.set_ylabel('π 估计值')
    ax.set_title(f'蒙特卡洛投点估 π: 误差 ~1/√n 衰减\nn={n_total}: π_hat={pi_final:.4f}')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ross_lt_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ross_lt_s4.png")
    print("\n  💡 极限定理串起来了:")
    print("     Chebyshev(#8) → WLLN(§1) → SLLN(§2) → CLT(§3) → 蒙特卡洛(§4)")
    print("     这是阶段 2「测度论概率」与「统计推断」的共同基石。")


if __name__ == "__main__":
    print("🎯 Ross 核心 2: 极限定理  |  阶段1 / 模块04\n")
    section_1_wlln()
    section_2_slln()
    section_3_clt()
    section_4_montecarlo()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 ross_02_limit_theorems.md, 做练习")
    print("=" * 70)
