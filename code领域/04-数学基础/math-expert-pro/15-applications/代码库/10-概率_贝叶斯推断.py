"""
概率论：贝叶斯推断与 MCMC 采样
================================
数学概念：贝叶斯定理 / 先验-似然-后验 / MCMC / Metropolis-Hastings 算法
应用领域：统计推断 / 机器学习 / 贝叶斯深度学习 / A/B 测试
核心思想：贝叶斯定理 P(θ|D) ∝ P(D|θ)·P(θ)（后验 ∝ 似然×先验）。
         当后验无法解析求解时，用 MCMC（马尔可夫链蒙特卡洛）采样。
         Metropolis-Hastings：从提议分布 q(θ'|θ) 采样新值，
         以概率 α = min(1, P(θ'|D)q(θ|θ') / P(θ|D)q(θ'|θ)) 接受。
         经过 burn-in 后，样本服从后验分布（遍历定理保证）。
运行方式：python "10-概率_贝叶斯推断.py"
依赖：numpy, matplotlib, scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 贝叶斯基础 ============

def bayes_update(prior, likelihood, theta_grid):
    """贝叶斯更新：后验 ∝ 先验 × 似然。
    prior: 先验分布（在 theta_grid 上的概率密度）
    likelihood: 似然函数 P(D|θ)（在 theta_grid 上的值）
    返回：归一化的后验分布
    """
    posterior = prior * likelihood
    posterior /= np.trapz(posterior, theta_grid)  # 归一化（数值积分）
    return posterior


# ============ 2. Metropolis-Hastings MCMC ============

def metropolis_hastings(log_posterior, init_theta, n_samples, proposal_std=0.5, burn_in=1000):
    """Metropolis-Hastings MCMC 采样器。

    log_posterior: 对数后验函数 f(θ) → log P(θ|D)（可省略归一化常数）
    init_theta: 初始参数值
    n_samples: 采样数（不含 burn-in）
    proposal_std: 随机游走标准差（调参：太大拒绝率高，太小混合慢）
    burn_in: 丢弃的前 burn_in 个样本（未收敛）

    返回：samples（n_samples 个后验样本）, acceptance_rate
    """
    total = n_samples + burn_in
    samples = np.zeros(total)
    theta = init_theta
    log_p = log_posterior(theta)
    accepted = 0

    for i in range(total):
        # 提议：高斯随机游走
        theta_prop = theta + np.random.normal(0, proposal_std)
        log_p_prop = log_posterior(theta_prop)

        # 接受概率 α = min(1, exp(log_p_prop - log_p))
        # （对称提议分布 q(θ'|θ)=q(θ|θ')，所以 q 项抵消）
        log_alpha = log_p_prop - log_p

        if np.log(np.random.rand()) < log_alpha:
            theta = theta_prop
            log_p = log_p_prop
            accepted += 1

        samples[i] = theta

    acceptance_rate = accepted / total
    return samples[burn_in:], acceptance_rate


# ============ 3. 实验与可视化 ============

def main():
    np.random.seed(42)

    # ============================================================
    # 案例：推断硬币的偏置（经典的贝叶斯推断入门问题）
    # ============================================================
    # 问题：抛一枚硬币 n 次，出现 k 次正面。求正面概率 θ 的后验分布。
    # 模型：似然 P(D|θ) = θ^k (1-θ)^(n-k)（二项分布）
    # 先验：Beta(α,β)（共轭先验，α=β=1 = 均匀分布）

    print("=" * 60)
    print("案例：推断硬币偏置——贝叶斯推断入门")
    print("=" * 60)

    # ---- 生成观测数据 ----
    true_theta = 0.7  # 真实正面概率
    n_trials = 50
    data = np.random.binomial(1, true_theta, n_trials)
    k_heads = data.sum()
    print(f"真实 θ = {true_theta}")
    print(f"抛 {n_trials} 次，观测到 {k_heads} 次正面（频率 = {k_heads/n_trials:.2f}）")

    # ---- 实验 1：贝叶斯更新（先验 → 后验的演变）----
    print("\n" + "=" * 60)
    print("实验 1：贝叶斯更新（观测更多数据，后验如何变化？）")
    print("=" * 60)

    theta_grid = np.linspace(0.001, 0.999, 200)
    # 先验：Beta(1,1) = 均匀分布
    prior = stats.beta.pdf(theta_grid, 1, 1)

    # 逐步更新：看 1/5/10/25/50 次观测后后验怎么变
    update_points = [1, 5, 10, 25, 50]
    posteriors = {}
    current_prior = prior.copy()

    print(f"\n{'观测数':<8} {'后验均值':<12} {'后验众数':<12} {'95%置信区间'}")
    print("-" * 55)

    for n_obs in update_points:
        k = data[:n_obs].sum()
        # 似然：θ^k (1-θ)^(n-k)
        likelihood = theta_grid ** k * (1 - theta_grid) ** (n_obs - k)
        # 后验
        posterior = bayes_update(current_prior, likelihood, theta_grid)
        posteriors[n_obs] = posterior

        # 后验统计量
        post_mean = np.trapz(theta_grid * posterior, theta_grid)
        post_mode = theta_grid[np.argmax(posterior)]
        # 95% 置信区间
        cdf = np.cumsum(posterior) * (theta_grid[1] - theta_grid[0])
        cdf /= cdf[-1]
        ci_low = theta_grid[np.searchsorted(cdf, 0.025)]
        ci_high = theta_grid[np.searchsorted(cdf, 0.975)]

        print(f"{n_obs:<8} {post_mean:<12.4f} {post_mode:<12.4f} [{ci_low:.3f}, {ci_high:.3f}]")

        # 下一步用这个后验作为先验（顺序更新）
        current_prior = posterior

    print(f"\n[解读] 观测越多，后验越集中（不确定性降低）。")
    print(f"       50 次观测后，后验众数 ≈ {k_heads/n_trials:.2f}（接近真实 {true_theta}）。")

    # ---- 实验 2：MCMC 采样（Metropolis-Hastings）----
    print("\n" + "=" * 60)
    print("实验 2：Metropolis-Hastings MCMC 采样")
    print("=" * 60)

    # 定义对数后验（可省略归一化常数）
    # log P(θ|D) = k·log(θ) + (n-k)·log(1-θ) + log_prior(θ)
    k = k_heads
    n = n_trials

    def log_posterior(theta):
        if theta <= 0 or theta >= 1:
            return -np.inf
        return k * np.log(theta) + (n - k) * np.log(1 - theta)  # + 均匀先验(常数)

    # 运行 MCMC
    n_samples = 10000
    samples, acc_rate = metropolis_hastings(
        log_posterior, init_theta=0.5, n_samples=n_samples,
        proposal_std=0.1, burn_in=2000)

    print(f"采样数: {n_samples}（burn-in 2000）")
    print(f"接受率: {acc_rate:.2%}（理想 20-50%）")
    print(f"MCMC 后验均值: {samples.mean():.4f}")
    print(f"MCMC 后验标准差: {samples.std():.4f}")
    print(f"MCMC 95%置信区间: [{np.percentile(samples, 2.5):.4f}, {np.percentile(samples, 97.5):.4f}]")

    # 解析解（Beta共轭后验）：Beta(k+1, n-k+1)
    analytic_mean = (k + 1) / (n + 2)
    analytic_var = (k + 1) * (n - k + 1) / ((n + 2) ** 2 * (n + 3))
    print(f"\n解析后验均值: {analytic_mean:.4f}（Beta({k+1},{n-k+1})）")
    print(f"解析后验标准差: {np.sqrt(analytic_var):.4f}")
    print(f"\n[解读] MCMC 采样均值 {samples.mean():.4f} ≈ 解析解 {analytic_mean:.4f}（✓ 吻合）")
    print(f"       MCMC 的价值：当没有共轭先验（解析解不存在）时，仍能采样后验。")

    # ---- 实验 3：MCMC 的收敛诊断 ----
    print("\n" + "=" * 60)
    print("实验 3：MCMC 收敛诊断（trace plot + 自相关）")
    print("=" * 60)

    # 不同 proposal_std 的影响
    print("提议分布标准差的影响：")
    print(f"{'proposal_std':<15} {'接受率':<10} {'后验均值':<12} {'有效样本数(ESS)'}")
    print("-" * 55)
    for ps in [0.01, 0.05, 0.1, 0.3, 0.5]:
        s, ar = metropolis_hastings(log_posterior, 0.5, 5000, proposal_std=ps, burn_in=1000)
        # 粗略 ESS：1 + 2*Σρ_k（自相关）
        from numpy import correlate
        s_centered = s - s.mean()
        acf = correlate(s_centered, s_centered, 'full')[len(s)-1:]
        acf /= acf[0]
        ess = len(s) / (1 + 2 * np.sum(acf[1:50]))
        print(f"{ps:<15} {ar:<10.2%} {s.mean():<12.4f} {ess:.0f}")

    print("\n[解读] proposal_std 太小→接受率高但混合慢（ESS低）；")
    print("       太大→拒绝率高。最优约 0.1-0.3（接受率 20-50%）。")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：贝叶斯更新（后验演变）
    ax = axes[0, 0]
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(update_points)))
    for i, (n_obs, post) in enumerate(posteriors.items()):
        ax.plot(theta_grid, post, color=colors[i], lw=2,
                label=f'n={n_obs}次观测')
    ax.axvline(true_theta, color='red', ls='--', lw=2, label=f'真实θ={true_theta}')
    ax.set_xlabel('θ（正面概率）')
    ax.set_ylabel('后验密度')
    ax.set_title('贝叶斯更新：观测越多后验越集中')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 图 2：MCMC 采样直方图 vs 解析后验
    ax = axes[0, 1]
    ax.hist(samples, bins=50, density=True, alpha=0.6, color='steelblue',
            label='MCMC 采样')
    # 解析后验
    analytic_post = stats.beta.pdf(theta_grid, k + 1, n - k + 1)
    ax.plot(theta_grid, analytic_post, 'r-', lw=2, label=f'解析后验 Beta({k+1},{n-k+1})')
    ax.axvline(true_theta, color='green', ls='--', lw=2, label=f'真实θ={true_theta}')
    ax.set_xlabel('θ')
    ax.set_ylabel('密度')
    ax.set_title('MCMC 采样 vs 解析后验')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 3：MCMC trace plot（采样轨迹）
    ax = axes[1, 0]
    ax.plot(samples[:1000], 'b-', lw=0.5, alpha=0.7)
    ax.axhline(true_theta, color='red', ls='--', lw=1.5, label=f'真实θ={true_theta}')
    ax.axhline(samples.mean(), color='orange', ls=':', lw=1.5, label=f'采样均值={samples.mean():.3f}')
    ax.set_xlabel('迭代步')
    ax.set_ylabel('θ 采样值')
    ax.set_title('MCMC Trace Plot（前 1000 步）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：自相关函数
    ax = axes[1, 1]
    s_centered = samples - samples.mean()
    acf = np.correlate(s_centered, s_centered, 'full')[len(samples)-1:]
    acf /= acf[0]
    lag_max = 100
    ax.bar(range(lag_max), acf[:lag_max], color='coral', alpha=0.7)
    ax.axhline(0, color='black', lw=0.5)
    ax.set_xlabel('滞后 lag')
    ax.set_ylabel('自相关 ACF')
    ax.set_title('MCMC 采样自相关函数（衰减越快=混合越好）')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("10-贝叶斯MCMC_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 10-贝叶斯MCMC_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 贝叶斯定理：后验 ∝ 似然 × 先验（观测更新信念）")
    print("2. 共轭先验（Beta-二项）有解析解；一般情况用 MCMC")
    print("3. Metropolis-Hastings：接受-拒绝采样，遍历定理保证收敛")
    print("4. MCMC 调参：proposal_std 控制接受率（理想 20-50%）")
    print("5. 收敛诊断：trace plot 看混合，自相关看独立性")
    print("\n[解读] 贝叶斯推断 = '用数据更新信念'的数学框架。")
    print("       MCMC 让你能在任意复杂模型上做贝叶斯推断——")
    print("       这是现代统计学、贝叶斯深度学习、A/B 测试的核心引擎。")


if __name__ == "__main__":
    main()
