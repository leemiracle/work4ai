"""
Oxford Part B B8.1 · 实验01: 条件期望=投影 + Doob 分解 + 似然比鞅
依赖: numpy, matplotlib
运行: python3 01_conditional_expectation_projection.py

验证 (Williams《Probability with Martingales》核心):
  1. 条件期望 = L² 正交投影 (E[Y|G] 是 Y 在 G-可测子空间的投影)
  2. 投影误差与 G 正交 (全期望公式 E[Y-E[Y|G]]=0)
  3. Doob 分解: X_n = M_n(鞅) + A_n(可料), 用对称游走验证
  4. 似然比是鞅: L_n = prod q(X_i)/p(X_i) 在 p 下是鞅 (变测度/ KL 散度连接)
  5. 鞅收敛定理: L¹-有界下鞅 a.s. 收敛 (Polya 罐模型)
  6. 回归 = 条件期望估计 (ML 关联)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: 条件期望 = L² 正交投影
# ============================================================
print("=" * 60)
print("实验 1: 条件期望 E[Y|G] = Y 在 G-可测子空间的正交投影")
print("=" * 60)

# 构造: X ~ N(0,1), G = sigma(X) 的有限逼近 (把 X 量化到 k 个 bin)
# Y = X^2 + 0.5*X + noise. E[Y|X] = X^2+0.5X (条件期望已知)
n = 100000
X = np.random.standard_normal(n)
Y = X**2 + 0.5 * X + 0.3 * np.random.standard_normal(n)

# G = sigma(X) 的逼近: 用 X 的分箱 (bin) 作为 sigma-代数的有限生成元
n_bins = 50
bins = np.quantile(X, np.linspace(0, 1, n_bins + 1))
bins[-1] += 1e-9
bin_idx = np.digitize(X, bins) - 1
bin_idx = np.clip(bin_idx, 0, n_bins - 1)

# E[Y|G] 的估计 = 每个 bin 内 Y 的均值 (这就是条件期望的离散逼近)
cond_exp = np.zeros(n)
for b in range(n_bins):
    mask = bin_idx == b
    if mask.sum() > 0:
        cond_exp[mask] = Y[mask].mean()

# 理论 E[Y|X] = X^2 + 0.5X (因为 noise 均值 0)
true_cond_exp = X**2 + 0.5 * X

print(f"  Y = X² + 0.5X + noise,  G = sigma(X) 的 {n_bins}-bin 逼近")
print(f"  E[Y|G] 估计(bin均值) 与理论 E[Y|X]=X²+0.5X 的相关系数:")
print(f"    corr(估计, 理论) = {np.corrcoef(cond_exp, true_cond_exp)[0,1]:.5f}")
residual = Y - cond_exp
print(f"  投影误差 (Y - E[Y|G]) 均值 = {residual.mean():.6f} (理论 0, 全期望公式)")
# 误差与 G-可测函数 (bin 指示) 正交: E[error * 1_A] ~ 0
ortho = np.array([residual[bin_idx == b].mean() for b in range(n_bins) if (bin_idx==b).sum()>50])
print(f"  误差在各 bin 内均值绝对值最大 = {np.abs(ortho).max():.6f} (应 ~0, 正交性)")
print("  结论: E[Y|G] 是 Y 在 G-可测函数上的 L² 投影, 误差与 G 正交 ✓")

# ============================================================
# 实验 2: Doob 分解 X_n = M_n + A_n
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Doob 分解 — X_n = M_n(鞅) + A_n(可料增序列)")
print("=" * 60)

# 取带漂移的随机游走 X_n = sum (X_i), X_i = +1 w.p. 0.6 else -1 (下鞅, 均值>0)
# Doob 分解: A_n = sum E[X_k - X_{k-1} | F_{k-1}] = sum (0.6-0.4)=0.2*k
p_drift = 0.6
n_steps = 500
n_sim = 30000
steps = np.where(np.random.random((n_sim, n_steps)) < p_drift, 1, -1)
X_path = np.zeros((n_sim, n_steps + 1))
X_path[:, 1:] = np.cumsum(steps, axis=1)

# 可料部分 A_n: E[ΔX_k|F_{k-1}] = 0.6*1+0.4*(-1) = 0.2, 累积
drift_per_step = (p_drift * 1 + (1 - p_drift) * (-1))  # = 0.2
A_path = np.arange(0, n_steps + 1) * drift_per_step
# 鞅部分 M_n = X_n - A_n
M_path = X_path - A_path[None, :]

# 验证 M_n 是鞅: E[M_{n+1}|F_n] = M_n => E[ΔM]=0
delta_M = M_path[:, 1:] - M_path[:, :-1]
print(f"  X_n = 带漂移游走 (p={p_drift}), 是下鞅 (E[X_n]递增)")
print(f"  可料增序列 A_n = {drift_per_step}*n (确定性)")
print(f"  M_n = X_n - A_n, 验证鞅性 E[ΔM_{{n+1}}|F_n]≈0:")
for k in [50, 200, 400]:
    print(f"    步 {k}: E[ΔM] 实测 = {delta_M[:, k].mean():+.5f} (理论 0)")
print(f"  M_n 整体均值 (各步): 范围 [{M_path.mean(axis=0).min():.3f}, {M_path.mean(axis=0).max():.3f}] (应 ~0)")
print("  结论: Doob 分解 X=M+A ✓, M 是零均值鞅, A 是确定性漂移")

# ============================================================
# 实验 3: 似然比是鞅 (变测度, KL 散度连接)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 似然比 L_n = Π q(X_i)/p(X_i) 在 p 下是鞅 (变测度)")
print("=" * 60)

# p = N(0,1), q = N(0.5, 1). 在 p 下采样, L_n = Π q(X_i)/p(X_i)
mu_q = 0.5
n_steps3 = 200
n_sim3 = 20000
X3 = np.random.standard_normal((n_sim3, n_steps3))
# 对数似然比增量: log(q/p) = log N(x;0.5,1) - log N(x;0,1) = 0.5*x - 0.125
log_ratio_inc = 0.5 * X3 - 0.125
log_L = np.cumsum(log_ratio_inc, axis=1)
L_path = np.exp(log_L)

# 鞅性验证: E[L_{n+1}|F_n] = L_n · E[q(X)/p(X)] = L_n · ∫q = L_n.
# 数值稳定的验证 = 单步增量 E_p[q(X)/p(X)] = ∫q = 1 (有限方差, 收敛快)
single_step_ratio = np.exp(0.5 * X3[:, 0] - 0.125)  # q(X)/p(X) 对单个样本
print(f"  p=N(0,1), q=N({mu_q},1), 在 p 下采样")
print(f"  单步增量 q(X)/p(X) 的均值 E_p[q/p] = {single_step_ratio.mean():.4f} (理论 1, ∫q=1)")
print(f"  → 鞅性 E[L_{{n+1}}|F_n] = L_n·E[q/p] = L_n ✓ (局部鞅增量期望=1)")

# 注意: 边际 E[L_n] = 1 理论成立, 但 L_n 是方差指数爆炸的对数正态,
# 朴素蒙特卡洛估计 E[L_n] 会系统性低估 (稀有巨大值采不到).
# E[L_n^2] = exp(n·μ²) → 相对误差 → ∞ (rare-event simulation 经典陷阱)
print(f"\n  ⚠️ 边际 E[L_n]=1 理论成立, 但 MC 估计退化 (对数正态方差爆炸):")
for k in [20, 100, 199]:
    print(f"    E[L_{k}] MC 估计 = {L_path[:, k].mean():.4f} (理论 1, 但 Var(L_n)~e^({0.25}n) 爆炸)")
print(f"    → 这正是 importance sampling / 罕见事件模拟的'相对误差爆炸'陷阱")

# KL(p||q) = E_p[log(p/q)] = -E_p[log(L_1)] (信息累积, 数值稳定)
kl_pq = 0.5**2 / 2  # KL(N(0,1)||N(0.5,1)) = mu^2/2 = 0.125
print(f"\n  KL(p||q) = μ²/2 = {kl_pq:.4f}")
print(f"  E_p[-log L_n] = n·KL(p||q) (信息累积, 数值稳定):")
print(f"    n=100: E[-log L_100] = {-log_L[:, 99].mean():.4f} vs 100·KL={100*kl_pq:.4f}")
print("  结论: 似然比鞅 + KL 散度 = 变测度/信息论/假设检验的统一工具 ✓")
print("        鞅性用'局部增量期望=1'验证(稳定); 边际期望的 MC 估计因方差爆炸不可靠 ⚠️")
print("        (ML: importance sampling / RLHF off-policy / 假设检验的数学基础)")

# ============================================================
# 实验 4: 鞅收敛定理 — Polya 罐
# ============================================================
print("\n" * 0)
print("=" * 60)
print("实验 4: 鞅收敛定理 — Polya 罐模型 a.s. 收敛")
print("=" * 60)

# Polya 罐: 初始 1 红 1 黑, 每次抽一个再放回并加一个同色. 
# 红球比例 X_n 是鞅 (Polya 罐经典结论), 且 X_n -> X_∞ ~ Uniform(0,1) (a.s.)
n_sim4 = 20
n_steps4 = 3000
final_proportions = []
sample_paths = []
for sim in range(n_sim4):
    red, black = 1, 1
    prop_path = [0.5]
    for _ in range(n_steps4):
        if np.random.random() < red / (red + black):
            red += 1
        else:
            black += 1
        prop_path.append(red / (red + black))
    sample_paths.append(prop_path)
    final_proportions.append(prop_path[-1])

final_proportions = np.array(final_proportions)
print(f"  Polya 罐: 红球比例 X_n 是鞅, a.s. 收敛到 X_∞ ~ Uniform(0,1)")
print(f"  模拟 {n_sim4} 条路径, 每条 {n_steps4} 步")
print(f"  最终比例: 均值={final_proportions.mean():.3f} (Uniform 期望 0.5)")
print(f"             方差={final_proportions.var():.4f} (Uniform(0,1) 方差 1/12={1/12:.4f})")
print("  结论: L¹-有界鞅 a.s. 收敛 ✓ — 极限分布是随机的(Uniform), 体现鞅收敛'停在哪里不确定'")

# ============================================================
# 实验 5: 回归 = 条件期望估计 (ML 关联)
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 回归 = 条件期望 E[Y|X] 的估计 (ML 核心关联)")
print("=" * 60)

# Y = sin(X) + noise, 回归拟合 E[Y|X] = sin(X)
Xr = np.random.uniform(-np.pi, np.pi, 2000)
Yr = np.sin(Xr) + 0.3 * np.random.standard_normal(2000)
# 用分箱估计条件期望
n_bins_r = 30
bins_r = np.linspace(-np.pi, np.pi, n_bins_r + 1)
bin_centers_r = 0.5 * (bins_r[:-1] + bins_r[1:])
idx_r = np.clip(np.digitize(Xr, bins_r) - 1, 0, n_bins_r - 1)
cond_est_r = np.array([Yr[idx_r == b].mean() if (idx_r==b).sum()>0 else 0 for b in range(n_bins_r)])
true_r = np.sin(bin_centers_r)
mse = np.mean((cond_est_r - true_r) ** 2)
print(f"  Y = sin(X) + noise, 分箱估计 E[Y|X]")
print(f"  估计 vs 真实 sin(X) 的 MSE = {mse:.5f} (随 bin 数/样本数增加 → 0)")
print("  结论: 回归/分箱 = 条件期望的逼近, 噪声被平均掉 ✓")
print("        (ML: 监督学习本质 = 估计条件期望 E[Y|X])")

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# (1) 条件期望投影
order = np.argsort(X)
axes[0][0].scatter(X[order[::50]], Y[order[::50]], s=3, alpha=0.3, color="gray", label="Y (带噪)")
axes[0][0].scatter(X[order[::50]], cond_exp[order[::50]], s=5, color="red", label="E[Y|G] (投影)")
xg = np.linspace(-3, 3, 200)
axes[0][0].plot(xg, xg**2 + 0.5*xg, "b-", linewidth=2, label="理论 E[Y|X]=X²+0.5X")
axes[0][0].set_xlabel("X")
axes[0][0].set_ylabel("Y")
axes[0][0].set_title("条件期望 = L² 投影")
axes[0][0].legend(fontsize=8)
axes[0][0].grid(alpha=0.3)

# (2) Doob 分解
t_grid = np.arange(n_steps + 1)
axes[0][1].plot(t_grid, X_path[:5].T, alpha=0.6, linewidth=0.8)
axes[0][1].plot(t_grid, A_path, "r--", linewidth=2.5, label=f"A_n = {drift_per_step}·n (可料)")
axes[0][1].set_xlabel("步数 n")
axes[0][1].set_ylabel("X_n")
axes[0][1].set_title("Doob 分解: X_n = M_n(鞅) + A_n(漂移)")
axes[0][1].legend()
axes[0][1].grid(alpha=0.3)

# (3) 似然比鞅 + KL
t3 = np.arange(1, n_steps3 + 1)
mean_logL = log_L.mean(axis=0)
axes[0][2].plot(t3, mean_logL, "b-", linewidth=2, label="E_p[log L_n] 实测")
axes[0][2].plot(t3, -kl_pq * t3, "r--", linewidth=2, label=f"-n·KL(p‖q) = -{kl_pq}n")
axes[0][2].set_xlabel("步数 n")
axes[0][2].set_ylabel("E[log L_n]")
axes[0][2].set_title("似然比鞅: E[log L_n] = -n·KL (信息累积)")
axes[0][2].legend()
axes[0][2].grid(alpha=0.3)

# (4) Polya 罐收敛
for sp in sample_paths[:10]:
    axes[1][0].plot(sp, alpha=0.6, linewidth=0.8)
axes[1][0].axhline(y=0.5, color="k", linestyle=":", alpha=0.5)
axes[1][0].set_xlabel("步数 n")
axes[1][0].set_ylabel("红球比例 X_n")
axes[1][0].set_title("Polya 罐: 鞅 a.s. 收敛 (极限随机)")
axes[1][0].grid(alpha=0.3)

# (5) Polya 罐极限分布
axes[1][1].hist(final_proportions, bins=15, density=True, alpha=0.6, color="green", label="模拟极限分布")
ug = np.linspace(0, 1, 100)
axes[1][1].plot(ug, np.ones_like(ug), "r-", linewidth=2, label="Uniform(0,1)")
axes[1][1].set_xlabel("X_∞")
axes[1][1].set_ylabel("密度")
axes[1][1].set_title("鞅极限 ~ Uniform(0,1)")
axes[1][1].legend()
axes[1][1].grid(alpha=0.3)

# (6) 回归 = 条件期望
axes[1][2].scatter(Xr[::5], Yr[::5], s=3, alpha=0.3, color="gray", label="数据")
axes[1][2].plot(bin_centers_r, cond_est_r, "r.-", linewidth=2, markersize=6, label="分箱估计 E[Y|X]")
axes[1][2].plot(bin_centers_r, true_r, "b--", linewidth=2, label="真实 sin(X)")
axes[1][2].set_xlabel("X")
axes[1][2].set_ylabel("Y")
axes[1][2].set_title("回归 = 条件期望估计 (ML)")
axes[1][2].legend(fontsize=8)
axes[1][2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
