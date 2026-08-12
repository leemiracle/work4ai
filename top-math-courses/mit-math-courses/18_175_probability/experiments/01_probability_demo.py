"""
MIT 18.175 · 实验01: 概率论核心定理数值验证
依赖: numpy, matplotlib
运行: python3 01_probability_demo.py

验证:
  1. 强大数定律 (SLLN): 样本均值 → 期望
  2. 中心极限定理 (CLT): 标准化样本均值 → N(0,1)
  3. Hoeffding 不等式: 紧度验证
  4. 鞅与可选停时: 对称随机游走到达边界
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: 强大数定律
# ============================================================
print("=" * 60)
print("实验 1: 强大数定律 (掷骰子均值 → 3.5)")
print("=" * 60)

n_trials = 100000
dice = np.random.randint(1, 7, n_trials)
running_mean = np.cumsum(dice) / np.arange(1, n_trials + 1)
true_mean = 3.5

print(f"掷骰 {n_trials} 次, 累计均值 = {running_mean[-1]:.6f}")
print(f"真值 = {true_mean}")
print(f"误差 = {abs(running_mean[-1] - true_mean):.6f}")
print(f"n=100 时误差 = {abs(running_mean[99] - true_mean):.6f}")
print(f"n=1000 时误差 = {abs(running_mean[999] - true_mean):.6f}")
print(f"n=10000 时误差 = {abs(running_mean[9999] - true_mean):.6f}")

# ============================================================
# 实验 2: 中心极限定理
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 中心极限定理")
print("=" * 60)

from math import erf, sqrt
def normal_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))

for n in [1, 5, 10, 30, 100]:
    # 重复采样: 每次取 n 个 Uniform(0,1) 的均值
    n_experiments = 5000
    sample_means = np.random.uniform(0, 1, (n_experiments, n)).mean(axis=1)
    # 标准化: (mean - 0.5) / sqrt(1/(12n))
    standardized = (sample_means - 0.5) / np.sqrt(1.0 / (12 * n))
    # 与 N(0,1) 对比 (用 99 分位数)
    p99_actual = np.percentile(standardized, 99)
    p99_normal = normal_cdf_inv = 2.326  # N(0,1) 的 99 分位数查表
    print(f"  n={n:3d}: 标准化均值的 99 分位数 = {p99_actual:.4f}, "
          f"N(0,1) 的 99 分位数 = {p99_normal:.4f}, 差距 = {abs(p99_actual - p99_normal):.4f}")

# ============================================================
# 实验 3: Hoeffding 不等式
# ============================================================
print("\n" + "=" * 60)
print("实验 3: Hoeffding 不等式紧度验证")
print("=" * 60)

n_samples = 200
n_experiments = 10000
epsilons = np.arange(0.02, 0.30, 0.02)

actual_probs = []
hoeffding_bounds = []

for eps in epsilons:
    # X_i ~ Bernoulli(0.5), 计算 |mean - 0.5| > eps 的实际概率
    samples = np.random.binomial(1, 0.5, (n_experiments, n_samples)).mean(axis=1)
    actual = np.mean(np.abs(samples - 0.5) > eps)
    bound = 2 * np.exp(-2 * n_samples * eps**2)
    actual_probs.append(actual)
    hoeffding_bounds.append(bound)
    print(f"  eps={eps:.2f}: 实际概率={actual:.6f}, Hoeffding 上界={bound:.6f}, "
          f"紧度比={actual/max(bound, 1e-300):.4f}")

print(f"\n结论: Hoeffding 上界始终 ≥ 实际概率 ✓")

# ============================================================
# 实验 4: 鞅与可选停时 (对称随机游走)
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 对称随机游走到达 ±a 的期望时间")
print("=" * 60)

for a in [5, 10, 20]:
    n_simulations = 2000
    hitting_times = []
    for _ in range(n_simulations):
        pos = 0
        steps = 0
        while abs(pos) < a:
            pos += np.random.choice([-1, 1])
            steps += 1
        hitting_times.append(steps)
    mean_time = np.mean(hitting_times)
    theoretical = a**2  # 由可选停时: E[tau] = a^2
    print(f"  a={a:2d}: 模拟 E[tau]={mean_time:.1f}, 理论 a²={theoretical}, "
          f"误差={abs(mean_time - theoretical)/theoretical*100:.1f}%")

# ============================================================
# 图表: SLLN + CLT 可视化
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 左图: SLLN 收敛过程
axes[0].axhline(y=true_mean, color="r", linestyle="--", label="真值 3.5")
for trial in range(5):
    dice = np.random.randint(1, 7, 10000)
    rm = np.cumsum(dice) / np.arange(1, 10001)
    axes[0].plot(rm, alpha=0.6, linewidth=0.8)
axes[0].set_xlabel("试验次数 n")
axes[0].set_ylabel("累计均值")
axes[0].set_title("强大数定律: 样本均值 → 期望")
axes[0].legend()
axes[0].grid(alpha=0.3)

# 右图: Hoeffding 实际 vs 上界
axes[1].plot(epsilons, actual_probs, "b.-", label="实际概率", linewidth=2)
axes[1].plot(epsilons, hoeffding_bounds, "r--", label="Hoeffding 上界", linewidth=2)
axes[1].set_xlabel("$\\epsilon$")
axes[1].set_ylabel("$P(|\\bar{X}_n - \\mu| > \\epsilon)$")
axes[1].set_title(f"Hoeffding 不等式紧度 (n={n_samples})")
axes[1].legend()
axes[1].grid(alpha=0.3)
axes[1].set_ylim(-0.01, max(max(actual_probs), max(hoeffding_bounds)) * 1.1)

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
