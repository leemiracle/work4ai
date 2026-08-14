"""
Harvard Math 114 · 实验: Riemann vs Lebesgue 积分对比
依赖: numpy, matplotlib, scipy
运行: python3 riemann_vs_lebesgue.py

验证:
  1. Riemann vs Lebesgue: 同一个函数两种积分方法
  2. Dirichlet 函数: Riemann 失败, Lebesgue 成功
  3. DCT (控制收敛定理) 验证
  4. 4 种收敛模式的可视化 (a.s. / 依概率 / Lp / 依分布)
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
# 实验 1: Riemann vs Lebesgue 积分对比
# ============================================================
print("=" * 70)
print("实验 1: Riemann vs Lebesgue — f(x) = x^2 on [0,1]")
print("=" * 70)
true_val = 1.0 / 3.0

# --- Riemann: 按定义域分桶 (竖切) ---
riemann_vals = []
for n_bins in [10, 100, 1000, 10000, 100000]:
    x = np.linspace(0, 1, n_bins + 1)
    dx = 1.0 / n_bins
    riemann = np.sum(x[:-1]**2 * dx)
    riemann_vals.append(abs(riemann - true_val))

# --- Lebesgue: 按值域分桶 (横切) ---
lebesgue_vals = []
for n_bins in [10, 100, 1000, 10000, 100000]:
    y_bins = np.linspace(0, 1, n_bins + 1)
    y_mid = (y_bins[:-1] + y_bins[1:]) / 2
    measures = np.sqrt(y_bins[1:]) - np.sqrt(y_bins[:-1])
    lebesgue = np.sum(y_mid * measures)
    lebesgue_vals.append(abs(lebesgue - true_val))

n_bins_list = [10, 100, 1000, 10000, 100000]
print(f"{'bins':>8} | {'Riemann err':>14} | {'Lebesgue err':>14}")
print("-" * 44)
for i, nb in enumerate(n_bins_list):
    print(f"{nb:8d} | {riemann_vals[i]:14.2e} | {lebesgue_vals[i]:14.2e}")
print("→ Lebesgue 收敛更快 (O(1/n^2) vs Riemann O(1/n))")

# ============================================================
# 实验 2: Dirichlet 函数 — Riemann 失败, Lebesgue 成功
# ============================================================
print("\n" + "=" * 70)
print("实验 2: Dirichlet 函数 f = 1_Q on [0,1]")
print("=" * 70)
print("Riemann 积分:")
print("  任何分割的每个子区间都有有理数和无理数")
print("  上和 U(P,f) = sum M_i * dx_i = sum 1 * dx_i = 1")
print("  下和 L(P,f) = sum m_i * dx_i = sum 0 * dx_i = 0")
print("  inf U = 1 ≠ 0 = sup L → 不可积!")
print("\nLebesgue 积分:")
print("  ∫ 1_Q dm = 1 · m(Q ∩ [0,1]) + 0 · m(Q^c ∩ [0,1])")
print("  m(Q) = 0 (可数集测度为零)")
print("  ∫ 1_Q dm = 0 → 可积!")
print("\nML 关联: Lebesgue 积分能处理更广的函数类 → 概率论的严格基础")

# ============================================================
# 实验 3: DCT (控制收敛定理) 验证
# ============================================================
print("\n" + "=" * 70)
print("实验 3: 控制收敛定理 (DCT)")
print("=" * 70)
x = np.linspace(0, 1, 100000)
dx = 1.0 / 100000

print("\n反例: f_n(x) = n · 1_{[0,1/n]} (不被控制)")
print("  f_n → 0 a.e., 但 ∫f_n = 1 ↛ 0 (DCT 不适用)")
print("\n正例: g_n(x) = 1_{[0,1/n]} (被 g=1 控制)")
print("  g_n → 0 a.e., |g_n| ≤ 1 ∈ L^1, ∫g_n → 0 (DCT 适用)")

for n in [10, 100, 1000, 10000]:
    fn = n * (x < 1.0/n).astype(float)
    gn = (x < 1.0/n).astype(float)
    int_fn = np.sum(fn) * dx
    int_gn = np.sum(gn) * dx
    print(f"  n={n:5d}: ∫f_n={int_fn:.4f} (不→0), ∫g_n={int_gn:.8f} (→0)")

print("\nML 关联: SGD 中 mini-batch 梯度→全梯度 的合法性依赖 DCT")

# ============================================================
# 实验 4: 4 种收敛模式可视化
# ============================================================
print("\n" + "=" * 70)
print("实验 4: 四种收敛模式 (a.s. / 依概率 / Lp / 依分布)")
print("=" * 70)

N = 50000
true_dist = stats.norm(0, 1)
results = {"n": [], "prob": [], "L2": [], "dist": []}

for n in [1, 5, 10, 50, 100, 500, 1000, 5000]:
    sigma_n = 1.0 / np.sqrt(n)
    noise = np.random.normal(0, sigma_n, N)
    X = np.random.normal(0, 1, N)
    Xn = X + noise

    eps = 0.1
    results["n"].append(n)
    results["prob"].append(np.mean(np.abs(Xn - X) > eps))
    results["L2"].append(np.mean((Xn - X)**2))
    ks_stat, _ = stats.ks_2samp(Xn, X)
    results["dist"].append(ks_stat)

print(f"\n{'n':>6} | {'P(|Xn-X|>eps)':>14} | {'E[|Xn-X|^2]':>14} | {'KS dist':>10}")
print("-" * 55)
for i in range(len(results["n"])):
    print(f"{results['n'][i]:6d} | {results['prob'][i]:14.6f} | {results['L2'][i]:14.6f} | {results['dist'][i]:10.6f}")

print("\n蕴含关系: L^p ⟹ 依概率 ⟹ 依分布;  a.s. ⟹ 依概率")

# ============================================================
# 绘图
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 子图 1: Riemann vs Lebesgue 误差
axes[0,0].loglog(n_bins_list, riemann_vals, "ro-", linewidth=2, markersize=8, label="Riemann")
axes[0,0].loglog(n_bins_list, lebesgue_vals, "bs-", linewidth=2, markersize=8, label="Lebesgue")
axes[0,0].set_xlabel("bins")
axes[0,0].set_ylabel("|integral - true|")
axes[0,0].set_title("Riemann vs Lebesgue: error convergence")
axes[0,0].legend()
axes[0,0].grid(alpha=0.3)

# 子图 2: Riemann vs Lebesgue 分桶示意
x = np.linspace(0, 1, 500)
axes[0,1].plot(x, x**2, "k-", linewidth=2, label="f(x)=x^2")
# Riemann 竖条
for i in range(15):
    xb = i/15
    axes[0,1].fill_between([xb, xb+1/15], 0, xb**2, alpha=0.15, color="red")
# Lebesgue 横条
for i in range(15):
    yb = i/15
    xs = np.sqrt(yb)
    axes[0,1].fill_between([xs, 1], yb, yb+1/15, alpha=0.1, color="blue")
axes[0,1].set_xlabel("x (domain)")
axes[0,1].set_ylabel("y = f(x) (range)")
axes[0,1].set_title("Riemann (red=vertical) vs Lebesgue (blue=horizontal)")
axes[0,1].legend(fontsize=8)
axes[0,1].grid(alpha=0.3)

# 子图 3: 收敛模式
axes[1,0].semilogx(results["n"], results["prob"], "ro-", label="in probability", linewidth=2)
axes[1,0].semilogx(results["n"], [l*5 for l in results["L2"]], "bs-", label="L^2 (x5)", linewidth=2)
axes[1,0].semilogx(results["n"], results["dist"], "g^-", label="in distribution", linewidth=2)
axes[1,0].set_xlabel("n")
axes[1,0].set_ylabel("convergence metric")
axes[1,0].set_title("Four convergence modes")
axes[1,0].legend()
axes[1,0].grid(alpha=0.3)

# 子图 4: DCT 示意
x = np.linspace(0, 1, 1000)
for n, alpha in [(5, 0.6), (10, 0.4), (50, 0.2)]:
    fn = n * (x < 1.0/n).astype(float)
    axes[1,1].plot(x, fn, alpha=alpha, label=f"f_n, n={n}")
axes[1,1].axhline(y=0, color="k", linestyle="--", alpha=0.3)
axes[1,1].set_xlabel("x")
axes[1,1].set_ylabel("f_n(x)")
axes[1,1].set_title("DCT counterexample: f_n -> 0 a.e. but integral -> 1")
axes[1,1].legend()
axes[1,1].grid(alpha=0.3)

plt.suptitle("Harvard Math 114: Riemann vs Lebesgue + Convergence Modes", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
plt.close()

print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
print("\n=== 总结 ===")
print("1. Lebesgue 积分 = 按值域分桶 (比 Riemann 更强)")
print("2. Dirichlet 函数: Riemann 不可积, Lebesgue 可积 (=0)")
print("3. DCT: 极限与积分换序的合法性条件")
print("4. 四种收敛: Lp ⟹ 依概率 ⟹ 依分布; a.s. ⟹ 依概率")
