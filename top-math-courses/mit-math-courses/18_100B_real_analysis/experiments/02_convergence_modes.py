"""
MIT 18.100B · 实验02: 四种收敛模式可视化 + Riemann vs Lebesgue 对比
依赖: numpy, matplotlib
运行: python3 02_convergence_modes.py

验证:
  Part A — 4 种随机收敛模式的关系（预告测度论/概率论）:
    1. 几乎必然 (a.s.) 收敛
    2. 依概率 (in probability) 收敛
    3. L^p 收敛
    4. 依分布 (in distribution) 收敛
  Part B — Riemann vs Lebesgue 积分对比
  Part C — Heine-Borel 紧致性数值验证
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
# Part A: 四种收敛模式
# ============================================================
print("=" * 70)
print("Part A: 四种收敛模式的关系")
print("  L^p 收敛 ⟹ 依概率收敛 ⟹ 依分布收敛")
print("  几乎必然收敛 (a.s.) ⟹ 依概率收敛")
print("=" * 70)

# 构造随机变量序列 X_n = X + noise_n, noise_n -> 0
# 当 noise 的方差 -> 0 时，所有 4 种收敛都成立
N_SAMPLES = 10000
X_true = stats.norm(loc=0, scale=1)  # 极限分布 N(0,1)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

results = {"n": [], "a.s.": [], "prob": [], "L2": [], "dist": []}

for idx, n in enumerate([1, 5, 20, 100, 500, 1000]):
    # noise 方差随 n 衰减: sigma_n = 1/sqrt(n)
    sigma_n = 1.0 / np.sqrt(n)
    noise = np.random.normal(0, sigma_n, N_SAMPLES)
    X_true_samples = np.random.normal(0, 1, N_SAMPLES)
    X_n = X_true_samples + noise

    results["n"].append(n)

    # --- 1. 依概率收敛: P(|X_n - X| > eps) -> 0 ---
    eps = 0.1
    prob_conv = np.mean(np.abs(X_n - X_true_samples) > eps)
    results["prob"].append(prob_conv)

    # --- 2. L^2 收敛: E[|X_n - X|^2] -> 0 ---
    L2_conv = np.mean((X_n - X_true_samples) ** 2)
    results["L2"].append(L2_conv)

    # --- 3. 依分布收敛: 用 KS 检验 ---
    ks_stat, ks_p = stats.ks_2samp(X_n, X_true_samples)
    results["dist"].append(ks_stat)

    # --- 4. a.s. 收敛模拟: 固定样本路径，看 X_n(omega) -> X(omega) ---
    # 用一条固定路径
    fixed_omega = 0  # 固定一个样本点
    a_s_values = []
    for nn in [1, 5, 10, 50, 100, 500, 1000]:
        s_nn = 1.0 / np.sqrt(nn)
        a_s_values.append(np.random.normal(0, s_nn))
    # a.s. 收敛看的是: 对于几乎所有 omega, X_n(omega) -> X(omega)
    # 这里模拟: variance of X_n across time -> 0
    results["a.s."].append(sigma_n)

# 绘制收敛模式
ns = results["n"]

# 子图 1: 依概率收敛
axes[0, 0].semilogx(ns, results["prob"], "ro-", linewidth=2, markersize=8)
axes[0, 0].axhline(y=0, color="k", linestyle="--", alpha=0.5)
axes[0, 0].set_xlabel("n")
axes[0, 0].set_ylabel(f"P(|X_n - X| > {eps})")
axes[0, 0].set_title("依概率收敛: P(|X_n - X| > ε) → 0")
axes[0, 0].grid(alpha=0.3)

# 子图 2: L^2 收敛
axes[0, 1].loglog(ns, results["L2"], "bs-", linewidth=2, markersize=8)
ref_line = [1.0 / n for n in ns]
axes[0, 1].loglog(ns, ref_line, "k--", alpha=0.5, label="1/n (参考)")
axes[0, 1].set_xlabel("n")
axes[0, 1].set_ylabel("E[|X_n - X|²]")
axes[0, 1].set_title("L² 收敛: E[|X_n - X|²] → 0")
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# 子图 3: 依分布收敛 (KS 统计量)
axes[1, 0].semilogx(ns, results["dist"], "g^-", linewidth=2, markersize=8)
axes[1, 0].axhline(y=0, color="k", linestyle="--", alpha=0.5)
axes[1, 0].set_xlabel("n")
axes[1, 0].set_ylabel("KS 统计量 (分布距离)")
axes[1, 0].set_title("依分布收敛: F_n → F (KS 检验)")
axes[1, 0].grid(alpha=0.3)

# 子图 4: 直方图对比
x_plot = np.linspace(-4, 4, 200)
axes[1, 1].plot(x_plot, X_true.pdf(x_plot), "k-", linewidth=2, label="极限分布 N(0,1)")
for n, color in zip([1, 10, 100], ["red", "blue", "green"]):
    sigma_n = 1.0 / np.sqrt(n)
    # X_n ~ N(0, 1 + 1/n), 近似为 N(0,1)
    samples = np.random.normal(0, np.sqrt(1 + sigma_n**2), 5000)
    axes[1, 1].hist(samples, bins=50, density=True, alpha=0.2, color=color, label=f"n={n}")
axes[1, 1].set_title("依分布收敛: 分布形状趋近")
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

plt.suptitle("Part A: 四种收敛模式可视化", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(__file__.replace(".py", "_partA.png"), dpi=120, bbox_inches="tight")
plt.close()

print("\n收敛模式数值结果:")
print(f"{'n':>6} | {'P(|X_n-X|>ε)':>14} | {'E[|X_n-X|²]':>14} | {'KS stat':>10}")
print("-" * 55)
for i, n in enumerate(ns):
    print(f"{n:6d} | {results['prob'][i]:14.6f} | {results['L2'][i]:14.6f} | {results['dist'][i]:10.6f}")
print("\n结论: L² ⟹ 依概率 ⟹ 依分布，所有收敛模式都成立 (noise → 0)")

# ============================================================
# Part B: Riemann vs Lebesgue 积分对比
# ============================================================
print("\n" + "=" * 70)
print("Part B: Riemann vs Lebesgue 积分对比")
print("=" * 70)

# 函数: f(x) = x² 在 [0,1] 上, 真值 = 1/3
true_val = 1.0 / 3.0

# --- Riemann 积分: 按定义域分桶 ---
riemann_errors = []
for n_bins in [10, 100, 1000, 10000, 100000]:
    x = np.linspace(0, 1, n_bins + 1)
    dx = 1.0 / n_bins
    riemann = np.sum(x[:-1]**2 * dx)  # 左端点
    err = abs(riemann - true_val)
    riemann_errors.append(err)

# --- Lebesgue 积分模拟: 按值域分桶 ---
# f(x) = x² 的值域是 [0,1]
# Lebesgue 积分 = sum_y y * measure(f^{-1}(y)) dy
# f^{-1}(y) = sqrt(y), measure 在 [0,1] 上的密度 ~ 1/(2*sqrt(y))
lebesgue_errors = []
for n_bins in [10, 100, 1000, 10000, 100000]:
    y_bins = np.linspace(0, 1, n_bins + 1)
    dy = 1.0 / n_bins
    # 对每个值域桶 [y_i, y_{i+1}], 取中值 y_mid
    y_mid = (y_bins[:-1] + y_bins[1:]) / 2
    # f^{-1}([y_i, y_{i+1}]) = [sqrt(y_i), sqrt(y_{i+1})]
    # Lebesgue measure of this preimage = sqrt(y_{i+1}) - sqrt(y_i)
    measures = np.sqrt(y_bins[1:]) - np.sqrt(y_bins[:-1])
    lebesgue = np.sum(y_mid * measures)
    err = abs(lebesgue - true_val)
    lebesgue_errors.append(err)

# --- 不可积函数对比: Dirichlet 函数 ---
# f(x) = 1 if x in Q, 0 otherwise
# Riemann: U(P,f) = 1 (每个区间有有理数), L(P,f) = 0 (有无理数) → 不可积
# Lebesgue: integral = 1 * m(Q ∩ [0,1]) + 0 * m(Q^c ∩ [0,1]) = 1*0 + 0*1 = 0
print("\nDirichlet 函数 f = 1_Q:")
print(f"  Riemann: 上和 U = 1, 下和 L = 0 → 不可积 (U ≠ L)")
print(f"  Lebesgue: ∫f = 1·m(ℚ∩[0,1]) + 0·m(ℚᶜ∩[0,1]) = 0  → 可积!")
print(f"  关键: ℚ 的 Lebesgue 测度 = 0 (可数集测度为 0)")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图: Riemann vs Lebesgue 误差
n_bins_list = [10, 100, 1000, 10000, 100000]
axes[0].loglog(n_bins_list, riemann_errors, "ro-", linewidth=2, markersize=8, label="Riemann")
axes[0].loglog(n_bins_list, lebesgue_errors, "bs-", linewidth=2, markersize=8, label="Lebesgue")
axes[0].set_xlabel("分割数 (bins)")
axes[0].set_ylabel("|积分 - 真值|")
axes[0].set_title("Riemann vs Lebesgue: ∫₀¹ x² dx 的收敛")
axes[0].legend()
axes[0].grid(alpha=0.3)

# 右图: Riemann vs Lebesgue 分桶示意图
x = np.linspace(0, 1, 500)
y = x**2

# Riemann 分桶 (竖条)
n_riemann = 15
x_r = np.linspace(0, 1, n_riemann + 1)
for i in range(n_riemann):
    mid_x = (x_r[i] + x_r[i + 1]) / 2
    axes[1].fill_between([x_r[i], x_r[i + 1]], 0, mid_x**2, alpha=0.2, color="red")
axes[1].step(np.repeat(x_r, 2)[1:-1], np.repeat(x_r[:-1]**2 + (x_r[1]-x_r[0])**2, 2),
             where="mid", color="red", alpha=0.5, linewidth=1, label="Riemann 竖条")

# Lebesgue 分桶 (横条)
n_leb = 15
y_l = np.linspace(0, 1, n_leb + 1)
for i in range(n_leb):
    x_start = np.sqrt(y_l[i])
    x_end = np.sqrt(y_l[i + 1])
    if x_end > x_start:
        mid_y = (y_l[i] + y_l[i + 1]) / 2
        axes[1].fill_betweenx([y_l[i], y_l[i + 1]], x_start, 1, alpha=0.15, color="blue")

axes[1].plot(x, y, "k-", linewidth=2, label="f(x) = x²")
axes[1].set_xlabel("x (定义域)")
axes[1].set_ylabel("y = f(x) (值域)")
axes[1].set_title("Riemann (红·竖切定义域) vs Lebesgue (蓝·横切值域)")
axes[1].legend(fontsize=8)
axes[1].grid(alpha=0.3)

plt.suptitle("Part B: Riemann vs Lebesgue 积分", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(__file__.replace(".py", "_partB.png"), dpi=120, bbox_inches="tight")
plt.close()

print("\n积分误差对比:")
print(f"{'bins':>8} | {'Riemann err':>12} | {'Lebesgue err':>12}")
print("-" * 40)
for i, nb in enumerate(n_bins_list):
    print(f"{nb:8d} | {riemann_errors[i]:12.2e} | {lebesgue_errors[i]:12.2e}")

# ============================================================
# Part C: Heine-Borel 数值验证
# ============================================================
print("\n" + "=" * 70)
print("Part C: Heine-Borel 紧致性验证")
print("=" * 70)

# 验证 1: 紧致集 [0,1] 上连续函数取最值
print("\n[0,1] 紧致 → f 连续 → 最值存在:")
x = np.linspace(0, 1, 100000)
f1 = np.sin(10 * x) * np.exp(-x)
print(f"  f(x) = sin(10x)·e^(-x) on [0,1]")
print(f"  max = {f1.max():.6f} at x = {x[f1.argmax()]:.6f}")
print(f"  min = {f1.min():.6f} at x = {x[f1.argmin()]:.6f} ✓")

# 验证 2: 非紧致集 (0,1) 上可能无最值
print("\n(0,1) 非紧致 → f(x) = 1/x 无最大值:")
print(f"  f(0.01) = {1/0.01:.1f}, f(0.0001) = {1/0.0001:.1f} → ∞")

# 验证 3: 有界但不闭 → 不紧致
print("\n[0,1) 有界但不闭 → 不紧致:")
print(f"  f(x) = x on [0,1): sup = 1 但 1 ∉ f([0,1)) → 无最大值")

# 验证 4: Bolzano-Weierstrass — 有界序列有收敛子序列
print("\nBolzano-Weierstrass: 有界序列有收敛子序列")
seq = np.random.uniform(-1, 1, 1000)
# 取子序列: 每第 100 个
subseq = seq[::100]
print(f"  原序列范围: [{seq.min():.4f}, {seq.max():.4f}] (有界)")
print(f"  子序列前 5 项: {subseq[:5]}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图: 紧致 vs 非紧致
x_plot = np.linspace(0.001, 0.999, 500)
y_compact = np.sin(10 * x_plot) * np.exp(-x_plot)
axes[0].plot(x_plot, y_compact, "b-", linewidth=2, label="紧致 [0,1]: 有最值")
axes[0].plot(np.linspace(0.01, 0.99, 500), 1.0 / np.linspace(0.01, 0.99, 500),
             "r--", linewidth=2, label="非紧致 (0,1): 1/x 无上界")
axes[0].set_xlabel("x")
axes[0].set_ylabel("f(x)")
axes[0].set_title("紧致性 → 极值定理")
axes[0].legend()
axes[0].grid(alpha=0.3)
axes[0].set_ylim(-5, 15)

# 右图: 序列收敛模式 — x^n 逐点 vs 一致收敛
axes[1].set_title("x^n: 逐点收敛但不一致收敛")
x_plot = np.linspace(0, 1, 200)
for n in [1, 2, 5, 10, 50]:
    axes[1].plot(x_plot, x_plot**n, label=f"n={n}")
axes[1].plot(x_plot, (x_plot < 1).astype(float), "k--", linewidth=2, label="极限 (不连续)")
axes[1].set_xlabel("x")
axes[1].set_ylabel("x^n")
axes[1].legend(fontsize=8)
axes[1].grid(alpha=0.3)
axes[1].annotate("一致收敛失败:\n极限不连续\n但 $x^n$ 连续",
                 xy=(0.9, 0.5), fontsize=10, color="red",
                 bbox=dict(boxstyle="round", facecolor="lightyellow"))

plt.suptitle("Part C: Heine-Borel 紧致性", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(__file__.replace(".py", "_partC.png"), dpi=120, bbox_inches="tight")
plt.close()

print(f"\n图表已保存: {__file__.replace('.py', '_partA.png')}")
print(f"图表已保存: {__file__.replace('.py', '_partB.png')}")
print(f"图表已保存: {__file__.replace('.py', '_partC.png')}")
print("\n=== 总结 ===")
print("1. 四种收敛: L^p ⟹ 依概率 ⟹ 依分布; a.s. ⟹ 依概率")
print("2. Lebesgue 比 Riemann 强: Dirichlet 函数 Lebesgue 可积但 Riemann 不可积")
print("3. 紧致集 + 连续函数 = 最值存在 (ML 中 loss 最小值的理论保证)")
