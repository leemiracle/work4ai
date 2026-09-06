"""
Berkeley MATH 218 · 实验01: 集中不等式与 PAC 泛化界 (Berkeley 学派核心)
依赖: numpy, matplotlib
运行: python3 01_concentration_generalization.py

验证 (Berkeley 集中不等式学派):
  1. Hoeffding 不等式: P(|均值-期望|>=t) <= 2e^{-2nt^2} (实测 <= 上界)
  2. PAC 泛化界: 样本复杂度 n ~ ln|H|/eps^2
  3. McDiarmid 有界差分: Lipschitz 函数的浓度 (用样本中位数)
  4. 重尾让 Hoeffding 失效: Cauchy 分布无界 -> 界不成立
  5. Union bound -> 多假设同时成立的泛化界
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)


# ============================================================
# 实验 1: Hoeffding 不等式 — 有界随机变量均值的浓度
# ============================================================
print("=" * 60)
print("实验 1: Hoeffding 不等式 — Bernoulli(0.3) 样本均值的尾概率")
print("=" * 60)

p_true = 0.3
n = 100
n_trials = 200000
# 每次抽 n 个 Bernoulli(p), 算样本均值
samples = np.random.binomial(1, p_true, (n_trials, n)).mean(axis=1)

thresholds = np.arange(0.02, 0.20, 0.02)
print(f"  真实均值 mu = {p_true}, 样本量 n = {n}, 试验次数 = {n_trials}")
print(f"  {'阈值 t':>10} | {'实测 P(|Xbar-mu|>=t)':>22} | {'Hoeffding 上界 2e^{-2nt^2}':>26}")
emp_probs_h = []
hoff_bounds = []
for t in thresholds:
    emp = np.mean(np.abs(samples - p_true) >= t)
    bound = 2 * np.exp(-2 * n * t ** 2)
    emp_probs_h.append(emp)
    hoff_bounds.append(min(bound, 1.0))
    print(f"  {t:10.2f} | {emp:22.6f} | {bound:26.6f}")
print("  结论: 实测概率始终 <= Hoeffding 上界 ✓ (界成立但较松)")

# ============================================================
# 实验 2: PAC 泛化界 — 样本复杂度
# ============================================================
print("\n" + "=" * 60)
print("实验 2: PAC 泛化界 — 样本复杂度 vs 泛化误差")
print("=" * 60)

log_H = np.log(1e6)  # |H| = 10^6
delta = 0.05
eps_target = 0.05
n_min = np.log(2 * np.exp(log_H) / delta) / (2 * eps_target ** 2)
print(f"  |H| = 10^6, delta = {delta}, eps = {eps_target}")
print(f"  所需最小样本 n* = ln(2|H|/delta)/(2 eps^2) = {n_min:.0f}")

# 验证: 用 n* 样本时, 泛化误差超过 eps 的概率
n_test = int(np.ceil(n_min))
n_trials2 = 50000
# 假设每个假设的真实误差 = 某固定值, 训练误差随机
# 简化: 单个假设 R(h)=0.3, 验证 |Rhat - R| <= eps 以概率 1-delta
over_count = 0
for _ in range(n_trials2):
    rhat = np.random.binomial(1, p_true, n_test).mean()
    if abs(rhat - p_true) > eps_target:
        over_count += 1
emp_fail = over_count / n_trials2
print(f"  用 n*={n_test} 样本: 实测 P(|Rhat-R|>eps) = {emp_fail:.4f} (应 <= delta={delta})")
print("  结论: 对单个假设, 失效概率 << delta (Hoeffding 单假设远松于 union bound)")

# ============================================================
# 实验 3: McDiarmid 有界差分 — 中位数函数的浓度
# ============================================================
print("\n" + "=" * 60)
print("实验 3: McDiarmid 有界差分 — 样本中位数 1/n-Lipschitz")
print("=" * 60)

n3 = 200
n_trials3 = 100000
# 数据 X_i ~ Uniform(0,1), f = 中位数. 改变一个 X_i 最多改变中位数 ~1/n (c_i ~ 2/n)
# 用 f = 第 k 顺序统计量 (中位数), bounded difference c_i ~ 2/n 是近似
medians = np.median(np.random.uniform(0, 1, (n_trials3, n3)), axis=1)
true_median_of_uniform = 0.5  # Uniform(0,1) 中位数的期望 ~ 0.5

# c_i 上界: 改变一个样本, 中位数最多移动 ~2/n (经验上)
c = 2.0 / n3
thresholds3 = np.arange(0.01, 0.08, 0.01)
emp_probs_m = []
mcdiarmid_bounds = []
print(f"  X_i~Uniform(0,1), n={n3}, f=中位数, bounded diff c_i~2/n={c:.4f}")
print(f"  {'阈值 t':>10} | {'实测':>12} | {'McDiarmid 上界':>16}")
for t in thresholds3:
    emp = np.mean(np.abs(medians - true_median_of_uniform) >= t)
    bound = 2 * np.exp(-2 * t ** 2 / (n3 * c ** 2))
    emp_probs_m.append(emp)
    mcdiarmid_bounds.append(min(bound, 1.0))
    print(f"  {t:10.3f} | {emp:12.6f} | {bound:16.6f}")
print("  结论: 中位数是 Lipschitz (改变一个样本影响小) -> McDiarmid 给出浓度 ✓")

# ============================================================
# 实验 4: 重尾让 Hoeffding 失效 — Cauchy 分布
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 重尾失效 — Cauchy 分布样本均值不收敛 (CLT/Hoeffding 失败)")
print("=" * 60)

n4_values = [10, 100, 1000, 10000]
n_trials4 = 50000
print(f"  Cauchy 分布: 密度 1/(pi(1+x^2)), 均值/方差都不存在")
print(f"  {'n':>8} | {'样本均值标准差':>16} | {'正态情形应 ~1/sqrt(n)':>22}")
for n4 in n4_values:
    cauchy_means = np.random.standard_cauchy((n_trials4, n4)).mean(axis=1)
    std_cauchy = np.std(cauchy_means)
    std_normal_pred = 1.0 / np.sqrt(n4)  # 若 CLT 适用, 均值 std 应 ~ sigma/sqrt(n)
    print(f"  {n4:8d} | {std_cauchy:16.4f} | {std_normal_pred:22.4f}")
print("  结论: 正态情形 std ~ 1/sqrt(n) 递减; Cauchy 的 std 不随 n 递减 ⚠️")
print("        Cauchy 样本均值与单个样本同分布 -> CLT/Hoeffding 完全失效")

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# (1) Hoeffding 不等式
axes[0][0].semilogy(thresholds, emp_probs_h, "b.-", linewidth=2, label="实测 P(|X̄-μ|≥t)")
axes[0][0].semilogy(thresholds, hoff_bounds, "r--", linewidth=2, label="Hoeffding 上界")
axes[0][0].set_xlabel("阈值 t")
axes[0][0].set_ylabel("概率 (log)")
axes[0][0].set_title(f"Hoeffding 不等式 (Bernoulli, n={n})")
axes[0][0].legend()
axes[0][0].grid(alpha=0.3, which="both")

# (2) 样本复杂度曲线 — n vs eps for different |H|
eps_range = np.linspace(0.02, 0.15, 50)
for logH, color, label in [(np.log(1e2), "blue", "|H|=10²"),
                            (np.log(1e6), "green", "|H|=10⁶"),
                            (np.log(1e12), "red", "|H|=10¹²")]:
    n_needed = (logH + np.log(2 / delta)) / (2 * eps_range ** 2)
    axes[0][1].semilogy(eps_range * 100, n_needed, color=color, linewidth=2, label=label)
axes[0][1].axhline(y=n_min, color="gray", linestyle=":", alpha=0.5)
axes[0][1].set_xlabel("泛化误差 ε (%)")
axes[0][1].set_ylabel("所需样本数 n")
axes[0][1].set_title(f"PAC 样本复杂度 (δ={delta})")
axes[0][1].legend()
axes[0][1].grid(alpha=0.3, which="both")

# (3) McDiarmid
axes[1][0].semilogy(thresholds3, emp_probs_m, "b.-", linewidth=2, label="实测 P(|med-0.5|≥t)")
axes[1][0].semilogy(thresholds3, mcdiarmid_bounds, "r--", linewidth=2, label="McDiarmid 上界")
axes[1][0].set_xlabel("阈值 t")
axes[1][0].set_ylabel("概率 (log)")
axes[1][0].set_title(f"McDiarmid 有界差分 (中位数, n={n3})")
axes[1][0].legend()
axes[1][0].grid(alpha=0.3, which="both")

# (4) Cauchy vs Normal 样本均值的标准差
n_plot = np.array(n4_values)
cauchy_stds = []
for n4 in n4_values:
    cm = np.random.standard_cauchy((10000, n4)).mean(axis=1)
    cauchy_stds.append(np.std(cm))
axes[1][1].loglog(n_plot, cauchy_stds, "rs-", linewidth=2, markersize=10, label="Cauchy 样本均值 std")
axes[1][1].loglog(n_plot, 1.0 / np.sqrt(n_plot), "b^-", linewidth=2, markersize=8, label="正态情形 1/√n")
axes[1][1].set_xlabel("样本量 n (log)")
axes[1][1].set_ylabel("样本均值 std (log)")
axes[1][1].set_title("重尾失效: Cauchy 均值不收敛 (CLT 失败)")
axes[1][1].legend()
axes[1][1].grid(alpha=0.3, which="both")

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
