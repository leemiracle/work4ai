"""
Berkeley MATH 218 · 实验02: Brownian Motion 与 Diffusion Model 的 SDE 基础
依赖: numpy, matplotlib
运行: python3 02_brownian_sde_diffusion.py

验证 (随机过程 -> 扩散模型):
  1. Brownian motion 模拟: W_t-W_s ~ N(0,t-s), 独立增量, 路径连续
  2. 二次变差 <W>_t = t (形式上 (dW)^2 = dt) -> Itô 引理的根源
  3. 反射原理: P(max_{s<=t} W_s >= a) = 2 P(W_t >= a)
  4. DDPM 前向 SDE: x_t = sqrt(αbar_t) x_0 + sqrt(1-αbar_t) ε, 边际分布验证
  5. 扩散模型的逐步加噪 -> 终态近似纯噪声
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: Brownian motion 路径模拟 + 增量正态性
# ============================================================
print("=" * 60)
print("实验 1: Brownian motion 模拟 — 增量 W_t-W_s ~ N(0, t-s)")
print("=" * 60)

T = 1.0
N = 1000
dt = T / N
n_paths = 20000
# 模拟 Brownian 路径: W_{k+1} = W_k + sqrt(dt) * Z
dW = np.sqrt(dt) * np.random.standard_normal((n_paths, N))
W = np.zeros((n_paths, N + 1))
W[:, 1:] = np.cumsum(dW, axis=1)

# 验证 W_T ~ N(0, T)
emp_mean = W[:, -1].mean()
emp_var = W[:, -1].var()
print(f"  W_T 实测: 均值 = {emp_mean:.4f} (理论 0), 方差 = {emp_var:.4f} (理论 {T})")

# 验证增量 W_T - W_{T/2} ~ N(0, T/2), 且与 W_{T/2} 独立
inc = W[:, -1] - W[:, N // 2]
half = W[:, N // 2]
print(f"  增量 W_T-W_(T/2): 均值 = {inc.mean():.4f} (理论 0), 方差 = {inc.var():.4f} (理论 {T/2})")
print(f"  增量与 W_(T/2) 的相关系数 = {np.corrcoef(inc, half)[0,1]:.4f} (理论 0, 独立)")
print("  结论: Brownian motion 的独立增量 + 正态性 ✓")

# ============================================================
# 实验 2: 二次变差 <W>_t = t (Itô 引理的根源)
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 二次变差 <W>_t = t  →  (dW_t)^2 = dt (Itô 引理根源)")
print("=" * 60)

# 二次变差: sum (W_{k+1}-W_k)^2 -> T (当 dt->0)
for n_steps in [100, 1000, 10000]:
    dt2 = T / n_steps
    dW2 = np.sqrt(dt2) * np.random.standard_normal((5000, n_steps))
    qv = (dW2 ** 2).sum(axis=1)  # 每条路径的二次变差
    print(f"  划分 n={n_steps:5d} (dt={dt2:.4f}): 实测 <W>_T = {qv.mean():.4f} (理论 {T})")
print("  结论: dt->0 时 sum(dW^2) -> T  ✓  => 形式上 (dW_t)^2 = dt")
print("        这正是 Itô 引理 df = f'dW + (1/2)f''dt 多出二阶项的原因")

# Itô 积分验证: int_0^t W_s dW_s = (1/2)W_t^2 - (1/2)t
print("\n  Itô 积分: ∫₀ᵗ W_s dW_s 应 = (1/2)W_t² - (1/2)t")
ito_sum = np.sum(W[:, :-1] * dW, axis=1)  # 左端点 Itô 和
ito_exact = 0.5 * W[:, -1] ** 2 - 0.5 * T
print(f"  Itô 和  = {ito_sum.mean():.4f} (std={ito_sum.std():.4f})")
print(f"  解析值 (1/2)W_T²-(1/2)T 均值 = {ito_exact.mean():.4f}")
print(f"  逐路径误差均值 = {np.mean(ito_sum - ito_exact):.6f} (应 -> 0)")
print("  结论: Itô 积分比 Riemann 多出 -(1/2)t 修正项 ✓")

# ============================================================
# 实验 3: 反射原理 P(max_{s<=t} W_s >= a) = 2 P(W_t >= a)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 反射原理 — P(max W_s >= a) = 2 P(W_t >= a)")
print("=" * 60)

running_max = np.maximum.accumulate(W, axis=1)
a_values = [0.5, 1.0, 1.5, 2.0]
print(f"  {'a':>6} | {'实测 P(max>=a)':>16} | {'2P(W_T>=a)':>12} | {'相对误差':>10}")
for a in a_values:
    p_max = np.mean(running_max[:, -1] >= a)
    p_refl = 2 * np.mean(W[:, -1] >= a)
    err = abs(p_max - p_refl) / max(p_refl, 1e-10) * 100
    print(f"  {a:6.2f} | {p_max:16.4f} | {p_refl:12.4f} | {err:9.1f}%")
print("  结论: 反射原理 P(max>=a) ≈ 2P(W_T>=a) ✓ (用于障碍期权/首达时间)")

# ============================================================
# 实验 4: DDPM 前向 SDE — 扩散模型加噪过程
# ============================================================
print("\n" + "=" * 60)
print("实验 4: DDPM 前向 SDE — x_t = sqrt(ᾱ_t) x_0 + sqrt(1-ᾱ_t) ε")
print("        (Ho et al., arXiv:2006.11239)")
print("=" * 60)

# DDPM 调度: beta_t 线性, alpha_t = 1-beta_t, alphabar_t = prod alpha
T_ddpm = 1000
betas = np.linspace(1e-4, 0.02, T_ddpm)
alphas = 1 - betas
alphabar = np.cumprod(alphas)

# 原始数据 x_0 = 某固定点 (e.g. 一个像素值 / 1D 数据)
x0 = 2.0
n_samples_ddpm = 50000

# 选几个时间步验证边际分布
t_steps = [10, 100, 300, 500, 999]
print(f"  x_0 = {x0}, 验证 x_t | x_0 ~ N(sqrt(ᾱ_t) x_0, (1-ᾱ_t))")
print(f"  {'t':>6} | {'ᾱ_t':>10} | {'实测均值':>10} | {'理论均值':>10} | {'实测方差':>10} | {'理论方差':>10}")
for t in t_steps:
    ab = alphabar[t]
    eps = np.random.standard_normal(n_samples_ddpm)
    xt = np.sqrt(ab) * x0 + np.sqrt(1 - ab) * eps
    print(f"  {t:6d} | {ab:10.6f} | {xt.mean():10.4f} | {np.sqrt(ab)*x0:10.4f} | {xt.var():10.4f} | {1-ab:10.4f}")
print("  结论: 前向过程边际分布 x_t|x_0 ~ N(sqrt(ᾱ_t)x_0, 1-ᾱ_t) ✓")
print(f"        终态 t=999: ᾱ_t≈{alphabar[-1]:.2e}, x_t ≈ 纯噪声 (信息全毁)")

# ============================================================
# 实验 5: 反向去噪直觉 — score 方向
# ============================================================
print("\n" + "=" * 60)
print("实验 5: score function ∇log p_t(x) — 反向 SDE 的驱动力")
print("=" * 60)

# 对 x_t|x_0 ~ N(m, s^2), score = (x - m)/s^2 = -(eps * sqrt(1-ab))/(1-ab) = -eps/sqrt(1-ab)
# 即 score 与噪声方向相反 (去噪!)
print("  x_t|x_0 ~ N(sqrt(ᾱ)x_0, 1-ᾱ)")
print("  score ∇log p_t(x) = (x - sqrt(ᾱ)x_0)/(1-ᾱ) = -ε/sqrt(1-ᾱ)")
print("  → score 指向 '去噪' 方向 (降低噪声), 反向 SDE 沿 score 演化")
print("  → DDPM 训练神经网络 ε_θ(x_t,t) 预测噪声, 等价于学 score")

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# (1) Brownian 路径
t_grid = np.linspace(0, T, N + 1)
for i in range(20):
    axes[0][0].plot(t_grid, W[i], alpha=0.5, linewidth=0.7)
axes[0][0].axhline(y=0, color="k", linewidth=0.5)
axes[0][0].set_xlabel("时间 t")
axes[0][0].set_ylabel("W_t")
axes[0][0].set_title("Brownian motion 路径 (处处连续, 处处不可导)")
axes[0][0].grid(alpha=0.3)

# (2) W_T 的分布 vs N(0,T)
axes[0][1].hist(W[:, -1], bins=60, density=True, alpha=0.6, color="steelblue", label="实测 W_T")
xg = np.linspace(-4, 4, 200)
axes[0][1].plot(xg, np.exp(-xg**2 / (2*T)) / np.sqrt(2*np.pi*T), "r-", linewidth=2, label="N(0,1)")
axes[0][1].set_xlabel("W_T")
axes[0][1].set_ylabel("密度")
axes[0][0].set_title
axes[0][1].set_title("W_T ~ N(0, T) 验证")
axes[0][1].legend()
axes[0][1].grid(alpha=0.3)

# (3) 二次变差收敛
ns = [50, 100, 500, 1000, 5000]
qvs = []
for ns_ in ns:
    dt_ = T / ns_
    qv_ = (np.sqrt(dt_) * np.random.standard_normal((3000, ns_))**2).sum(axis=1)
    qvs.append(qv_.mean())
axes[0][2].plot(ns, qvs, "bo-", linewidth=2, markersize=8, label="实测 <W>_T")
axes[0][2].axhline(y=T, color="r", linestyle="--", linewidth=2, label="理论 = 1.0")
axes[0][2].set_xlabel("划分数 n")
axes[0][2].set_ylabel("二次变差 <W>_T")
axes[0][2].set_title("二次变差 → T (Itô: (dW)²=dt)")
axes[0][2].legend()
axes[0][2].grid(alpha=0.3)

# (4) 反射原理
a_range = np.linspace(0.1, 2.5, 30)
p_max_emp = [np.mean(running_max[:, -1] >= a) for a in a_range]
p_refl = [2 * np.mean(W[:, -1] >= a) for a in a_range]
axes[1][0].plot(a_range, p_max_emp, "b-", linewidth=2, label="实测 P(max W_s≥a)")
axes[1][0].plot(a_range, p_refl, "r--", linewidth=2, label="2P(W_T≥a)")
axes[1][0].set_xlabel("a")
axes[1][0].set_ylabel("概率")
axes[1][0].set_title("反射原理验证")
axes[1][0].legend()
axes[1][0].grid(alpha=0.3)

# (5) DDPM 调度: alphabar_t 衰减
axes[1][1].plot(alphabar, "b-", linewidth=2)
axes[1][1].set_xlabel("时间步 t")
axes[1][1].set_ylabel("ᾱ_t")
axes[1][1].set_title("DDPM 调度: ᾱ_t 单调衰减 → 0 (信息渐毁)")
axes[1][1].grid(alpha=0.3)
axes[1][1].axhline(y=0, color="k", linewidth=0.5)

# (6) 前向加噪的方差变化
var_t = 1 - alphabar
mean_t = np.sqrt(alphabar) * x0
axes[1][2].plot(t_grid_ddpm := np.arange(T_ddpm), mean_t, "b-", linewidth=2, label=f"均值 sqrt(ᾱ)·x₀ (x₀={x0})")
axes[1][2].plot(t_grid_ddpm, var_t, "r--", linewidth=2, label="方差 1-ᾱ")
axes[1][2].set_xlabel("时间步 t")
axes[1][2].set_ylabel("边际分布参数")
axes[1][2].set_title("DDPM 前向: 均值→0, 方差→1 (纯噪声)")
axes[1][2].legend()
axes[1][2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
