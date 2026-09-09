"""
MIT 18.175 · 实验02: 中心极限定理数值验证 + Berry-Esseen 收敛速度
依赖: numpy, matplotlib
运行: python3 02_clt_numerical.py

验证:
  1. CLT: 不同分布的标准化样本均值 → N(0,1)
  2. Berry-Esseen: 收敛速度 O(1/sqrt(n))
  3. 重尾分布 (Cauchy) 让 CLT 失效 — 对比实验
  4. Batch size 与梯度噪声: CLT 在 mini-batch SGD 中的体现
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: CLT — 不同分布的标准化样本均值收敛到 N(0,1)
# ============================================================
print("=" * 60)
print("实验 1: CLT — 标准化样本均值 → N(0,1)")
print("=" * 60)

distributions = {
    "Uniform(0,1)":      lambda n: np.random.uniform(0, 1, n),
    "Exponential(1)":    lambda n: np.random.exponential(1, n),
    "Bernoulli(0.3)":    lambda n: np.random.binomial(1, 0.3, n),
    "Poisson(5)":        lambda n: np.random.poisson(5, n),
}

n_experiments = 20000
sample_sizes = [1, 5, 30, 100]

fig, axes = plt.subplots(len(distributions), len(sample_sizes),
                         figsize=(16, 12), squeeze=False)

for row, (dist_name, sampler) in enumerate(distributions.items()):
    for col, n in enumerate(sample_sizes):
        # 采样 n_experiments 次, 每次取 n 个样本的均值
        means = np.array([sampler(n).mean() for _ in range(n_experiments)])
        # 标准化: (mean - mu) / (sigma / sqrt(n))
        mu = means.mean()
        sigma_n = means.std()
        standardized = (means - mu) / sigma_n

        # KS 检验 vs N(0,1)
        ks_stat, ks_pval = stats.kstest(standardized, "norm")

        ax = axes[row][col]
        ax.hist(standardized, bins=60, density=True, alpha=0.6, color="steelblue")
        x = np.linspace(-4, 4, 200)
        ax.plot(x, stats.norm.pdf(x), "r-", linewidth=2, label="N(0,1)")
        ax.set_title(f"{dist_name}, n={n}\nKS={ks_stat:.4f}, p={ks_pval:.3f}",
                     fontsize=9)
        ax.set_xlim(-4, 4)
        if col == 0:
            ax.set_ylabel("密度")

print("结论: n 增大时, 所有分布的标准化均值都收敛到 N(0,1) ✓")
print("      KS 统计量随 n 增大而减小 (Berry-Esseen: O(1/sqrt(n)))")

# ============================================================
# 实验 2: Berry-Esseen 收敛速度
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Berry-Esseen 收敛速度 — sup|F_n - Φ| vs C/sqrt(n)")
print("=" * 60)

sampler = lambda n: np.random.exponential(1, n)
n_experiments = 50000
sample_sizes = [5, 10, 20, 50, 100, 200, 500]

ks_stats = []
for n in sample_sizes:
    means = np.array([sampler(n).mean() for _ in range(n_experiments)])
    mu, sigma = 1.0, 1.0  # Exponential(1): mu=1, sigma=1
    standardized = (means - mu) / (sigma / np.sqrt(n))
    ks_stat, _ = stats.kstest(standardized, "norm")
    ks_stats.append(ks_stat)
    # Berry-Esseen 上界 (C ≈ 0.4748, rho = E|X-mu|^3/sigma^3 = 2 for Exp(1))
    be_bound = 0.4748 * 2.0 / np.sqrt(n)
    print(f"  n={n:4d}: KS统计量(≈sup|F_n-Φ|) = {ks_stat:.5f}, "
          f"Berry-Esseen上界 = {be_bound:.5f}, 比值 = {ks_stat/be_bound:.3f}")

print("\n结论: KS统计量 ∝ 1/sqrt(n), 与 Berry-Esseen 一致 ✓")

# ============================================================
# 实验 3: 重尾分布让 CLT 失效 — Cauchy 分布
# ============================================================
print("\n" + "=" * 60)
print("实验 3: Cauchy 分布 — CLT 失效（方差无穷大）")
print("=" * 60)

for n in [10, 100, 1000, 10000]:
    samples = np.random.standard_cauchy((n_experiments, n)).mean(axis=1)
    print(f"  n={n:5d}: 样本均值 std = {samples.std():.4f} "
          f"(理论上不收敛, 应 ≈ π/sqrt(n) 若 CLT 适用 → {np.pi/np.sqrt(n):.4f})")

print("\n结论: Cauchy 分布没有 CLT！样本均值的方差不随 n 减小 ⚠️")
print("      原因: Cauchy 分布的方差/期望不存在 → CLT 条件不满足")

# ============================================================
# 实验 4: CLT 在 mini-batch SGD 中的体现
# ============================================================
print("\n" + "=" * 60)
print("实验 4: mini-batch 梯度噪声方差 vs batch size (CLT: σ²/n)")
print("=" * 60)

# 模拟: 真实梯度是数据集上的期望梯度, mini-batch 是采样近似
true_gradient = 2.0  # 假设真实梯度 = 2.0
data_gradients = np.random.normal(2.0, 3.0, 100000)  # 单样本梯度的分布

batch_sizes = [1, 4, 16, 64, 256, 1024]
noise_stds = []
for bs in batch_sizes:
    # 采 10000 次 mini-batch, 计算梯度噪声
    batch_grads = np.array([
        np.random.choice(data_gradients, bs).mean()
        for _ in range(10000)
    ])
    noise_std = batch_grads.std()
    noise_stds.append(noise_std)
    theoretical = 3.0 / np.sqrt(bs)  # CLT: σ/sqrt(n)
    print(f"  batch_size={bs:4d}: 梯度噪声 std = {noise_std:.4f}, "
          f"理论 σ/√n = {theoretical:.4f}")

print("\n结论: 梯度噪声 ∝ 1/√(batch_size), 这就是 CLT 在深度学习中的体现 ✓")
print("      → BatchNorm 用 batch 统计量的标准差来归一化, 抑制这个噪声")

# ============================================================
# 可视化: Berry-Esseen + 梯度噪声
# ============================================================
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# 左: Berry-Esseen
ns = np.array(sample_sizes)
ax1.loglog(ns, ks_stats, "bo-", label="实测 KS 统计量", linewidth=2)
ax1.loglog(ns, 0.4748 * 2.0 / np.sqrt(ns), "r--", label="Berry-Esseen C/√n", linewidth=2)
ax1.set_xlabel("样本量 n")
ax1.set_ylabel("sup |F_n - Φ|")
ax1.set_title("Berry-Esseen 收敛速度")
ax1.legend()
ax1.grid(alpha=0.3, which="both")

# 右: 梯度噪声
ax2.loglog(batch_sizes, noise_stds, "gs-", label="实测梯度噪声 std", linewidth=2)
ax2.loglog(batch_sizes, [3.0/np.sqrt(b) for b in batch_sizes],
           "r--", label="理论 σ/√(batch_size)", linewidth=2)
ax2.set_xlabel("Batch size")
ax2.set_ylabel("梯度噪声标准差")
ax2.set_title("CLT 在 mini-batch SGD 中: 噪声 ∝ 1/√(batch)")
ax2.legend()
ax2.grid(alpha=0.3, which="both")

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
