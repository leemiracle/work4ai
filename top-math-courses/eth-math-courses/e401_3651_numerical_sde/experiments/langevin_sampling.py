"""
ETH 401-3651 · 实验: Langevin 动力学采样与 Score-Based 生成
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 langevin_sampling.py

验证:
  1. Langevin SDE 采样到目标分布 e^{-U}
  2. Score matching 的去噪目标 (DDPM 训练损失)
  3. 反向 SDE 数值解 = 扩散模型采样 (玩具示例)
  4. Score 函数的可视化
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: Langevin 采样 — 从能量函数采样
# ============================================================
print("=" * 60)
print("实验 1: Langevin 采样 dX = -∇U(X) dt + √2 dW")
print("=" * 60)

def langevin_sample(grad_U, x0, n_steps=5000, step_size=0.005, n_particles=2000):
    """过阻尼 Langevin, 平稳分布 ∝ e^{-U}"""
    x = np.tile(x0, (n_particles, 1)).astype(float)
    trajectory = [x.copy()]
    for i in range(n_steps):
        g = grad_U(x)
        noise = np.sqrt(2 * step_size) * np.random.randn(*x.shape)
        x = x - step_size * g + noise
        if (i + 1) % 500 == 0:
            trajectory.append(x.copy())
    return np.array(trajectory)

# 双峰分布: U(x) = -log(0.5 N(x; -3, 1) + 0.5 N(x; 3, 1))
# ∇U(x) = -( -(x+3)φ(-3) - (x-3)φ(3) ) / (φ(-3)+φ(3))
def grad_U_bimodal(x):
    # ∇U = (x+3) exp(-(x+3)^2/2) + (x-3) exp(-(x-3)^2/2) 归一化
    p1 = np.exp(-0.5 * (x + 3)**2)
    p2 = np.exp(-0.5 * (x - 3)**2)
    g1 = -(x + 3) * p1
    g2 = -(x - 3) * p2
    return -(g1 + g2) / (p1 + p2)  # -∇log p

x0 = np.array([0.0])
traj = langevin_sample(grad_U_bimodal, x0, n_steps=8000, step_size=0.01, n_particles=5000)
final = traj[-1].ravel()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(final, bins=50, density=True, alpha=0.7, label="Langevin 采样")
x_grid = np.linspace(-8, 8, 200)
target = 0.5 * np.exp(-0.5*(x_grid+3)**2)/np.sqrt(2*np.pi) + 0.5 * np.exp(-0.5*(x_grid-3)**2)/np.sqrt(2*np.pi)
axes[0].plot(x_grid, target, "r-", lw=2, label="目标分布 (双峰高斯)")
axes[0].set_title("Langevin 采样收敛到目标分布")
axes[0].legend(); axes[0].grid(True, alpha=0.3)
# 轨迹展示
for p in range(30):
    axes[1].plot(traj[:, p, 0], alpha=0.3, linewidth=0.5)
axes[1].set_title("Langevin 粒子轨迹 (粒子从 0 出发扩散到双峰)")
axes[1].set_xlabel("步数"); axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("langevin_sampling.png", dpi=100); plt.close()
print(f"采样均值: {np.mean(final):.3f} (理论 0, 双峰对称)")
print(f"采样方差: {np.var(final):.3f} (理论 ≈ 1 + 9 = 10)")

# ============================================================
# 实验 2: Score function 可视化
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Score function ∇log p(x) 可视化")
print("=" * 60)

def mixture_pdf(x):
    return 0.5 * np.exp(-0.5*(x+3)**2)/np.sqrt(2*np.pi) + 0.5 * np.exp(-0.5*(x-3)**2)/np.sqrt(2*np.pi)

def mixture_score(x):
    eps = 1e-12
    return grad_U_bimodal(x.reshape(-1, 1)).ravel()

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
axes[0].plot(x_grid, mixture_pdf(x_grid), "b-", lw=2)
axes[0].set_ylabel("$p(x)$"); axes[0].set_title("混合高斯密度")
axes[0].grid(True, alpha=0.3)
score = mixture_score(x_grid)
axes[1].plot(x_grid, score, "r-", lw=2)
axes[1].quiver(x_grid[::10], np.zeros_like(x_grid[::10]), score[::10], np.zeros_like(score[::10]),
               angles="xy", scale_units="xy", scale=5, width=0.003, color="r", alpha=0.5)
axes[1].axhline(0, color="k", linewidth=0.5)
axes[1].set_ylabel("$\\nabla_x \\log p(x)$"); axes[1].set_xlabel("x")
axes[1].set_title("Score function: 指向高密度方向 (生成模型的核心)")
axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("score_function.png", dpi=100); plt.close()
print("Score 始终指向密度增加的方向 — Langevin/reverse SDE 沿 score '爬升'")

# ============================================================
# 实验 3: DDPM 训练损失 (score matching / denoising)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: DDPM 去噪 score matching 损失")
print("=" * 60)

# 目标: L = E_{x_0, ε, t} || s_θ(x_t, t) - s(x_t, t) ||²
# 其中 x_t = sqrt(α_bar_t) x_0 + sqrt(1-α_bar_t) ε, ε ~ N(0,I)
# s(x_t, t) = -ε / sqrt(1-α_bar_t) (高斯条件的 score)
# 等价: L_simple = E || ε_θ(x_t, t) - ε ||²  (DDPM 简化)

def forward_diffuse(x0, t, alpha_bar):
    """x_t = sqrt(α_bar_t) x_0 + sqrt(1-α_bar_t) ε"""
    eps = np.random.randn(*x0.shape)
    return np.sqrt(alpha_bar) * x0 + np.sqrt(1 - alpha_bar) * eps, eps

# β schedule: linear from β_1=1e-4 to β_T=0.02, T=1000
T = 1000
betas = np.linspace(1e-4, 0.02, T)
alphas = 1 - betas
alpha_bar = np.cumprod(alphas)

# 生成 "数据" (双峰)
data = np.random.choice([-3, 3], size=5000).astype(float) + 0.5 * np.random.randn(5000)

# 可视化不同 t 的前向扩散
fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))
times = [0, 50, 200, 999]
for ax, t_step in zip(axes, times):
    if t_step == 0:
        samples_t = data
    else:
        samples_t, _ = forward_diffuse(data, t_step, alpha_bar[t_step])
    ax.hist(samples_t, bins=50, density=True, range=(-6, 6), color="steelblue", alpha=0.7)
    ax.set_title(f"t={t_step}, $\\bar\\alpha$={alpha_bar[t_step]:.3f}")
    ax.set_xlim(-6, 6); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("ddpm_forward_diffusion.png", dpi=100); plt.close()
print(f"α_bar 演化: t=0 → 1.0, t=50 → {alpha_bar[50]:.3f}, t=200 → {alpha_bar[200]:.3f}, t=999 → {alpha_bar[999]:.4f}")
print("t=T 时数据 → N(0,I), 反向过程 (DDPM 采样) 从噪声恢复数据")

# 模拟 score matching 损失 (玩具: 线性 score 模型 s(x,t) = -a(t) x)
def score_matching_loss(a_param, data, alpha_bar, n_samples=10000):
    """简化损失: s_θ(x,t) = -a x 近似 score = -x/(1-α_bar) * ... """
    t = np.random.randint(1, T, n_samples)
    ab = alpha_bar[t]
    x0 = np.random.choice(data, n_samples)
    eps = np.random.randn(n_samples)
    xt = np.sqrt(ab) * x0 + np.sqrt(1 - ab) * eps
    target_score = -eps / np.sqrt(1 - ab)  # 条件 score
    pred_score = -a_param * xt  # 参数化
    return np.mean((pred_score - target_score)**2)

# 网格搜索最优 a (玩具优化)
a_grid = np.linspace(0.1, 3.0, 30)
losses = [score_matching_loss(a, data, alpha_bar) for a in a_grid]
best_a = a_grid[np.argmin(losses)]
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(a_grid, losses, "b-")
ax.axvline(best_a, color="r", linestyle="--", label=f"最优 a = {best_a:.2f}")
ax.set_xlabel("参数 a"); ax.set_ylabel("Score matching 损失")
ax.set_title("DDPM 训练损失最小化 (玩具: s_θ(x,t) = -a x)")
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("score_matching_loss.png", dpi=100); plt.close()
print(f"最优 a = {best_a:.2f}")

# ============================================================
# 实验 4: 反向 SDE 采样 (玩具扩散模型)
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 反向 SDE 数值解 (玩具扩散模型采样)")
print("=" * 60)

# 实验 4: DDPM 反向采样 (离散 DDPM kernel, 数值稳定)
# 目标分布: N(μ, σ²) with μ=2, σ²=0.25
# DDPM 离散前向: x_t = sqrt(ᾱ_t) x_0 + sqrt(1-ᾱ_t) ε
# DDPM 离散反向: x_{t-1} = (1/sqrt(α_t))[x_t - (1-α_t)/sqrt(1-ᾱ_t) · ε_θ(x_t,t)] + σ_t z
# 解析 score: ε = -sqrt(1-ᾱ_t) · score(x_t,t)
tgt_mu, tgt_var = 2.0, 0.25

# DDPM schedule
T_ddpm = 200
betas_d = np.linspace(1e-4, 0.04, T_ddpm)
alphas_d = 1 - betas_d
abar_d = np.cumprod(alphas_d)

def ddpm_reverse_sample(shape, n_particles=3000):
    x = np.random.randn(*shape)  # x_T ~ N(0, I)
    trajectory = [x.copy()]
    for t in range(T_ddpm - 1, 0, -1):
        ab = abar_d[t]
        a = alphas_d[t]
        # 解析 score: 对 N(μ_t, σ_t²), score = -(x-μ_t)/σ_t²
        mu_t = tgt_mu * np.sqrt(ab)
        var_t = tgt_var * ab + (1 - ab)
        score = -(x - mu_t) / var_t
        # ε = -sqrt(1-ᾱ_t) score
        eps = -np.sqrt(1 - ab) * score
        # DDPM reverse mean
        mean = (1 / np.sqrt(a)) * (x - (1 - a) / np.sqrt(1 - ab) * eps)
        # 噪声 (t>1), t=0 无噪声
        sigma = np.sqrt(betas_d[t]) if t > 1 else 0.0
        x = mean + sigma * np.random.randn(*x.shape)
        if t % 40 == 0:
            trajectory.append(x.copy())
    trajectory.append(x.copy())
    return np.array(trajectory)

samples_reverse = ddpm_reverse_sample((3000,))
final_reverse = samples_reverse[-1]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(samples_reverse[0], bins=50, density=True, alpha=0.5, color="r", label="t=T (N(0,1) 噪声)")
axes[0].hist(final_reverse, bins=50, density=True, alpha=0.7, color="g", label="t=0 (反向采样)")
x_grid = np.linspace(-3, 6, 200)
target_pdf = np.exp(-0.5*(x_grid - tgt_mu)**2 / tgt_var) / np.sqrt(2*np.pi*tgt_var)
axes[0].plot(x_grid, target_pdf, "k-", lw=2, label=f"目标 N({tgt_mu}, {tgt_var})")
axes[0].set_title("反向 SDE (解析时间相关 score): 噪声 → 目标")
axes[0].legend(); axes[0].grid(True, alpha=0.3)

mean_traj = [np.mean(s) for s in samples_reverse]
var_traj = [np.var(s) for s in samples_reverse]
steps = np.arange(len(samples_reverse)) * 40
axes[1].plot(steps, mean_traj, "b-o", label=f"均值 (目标 {tgt_mu})")
axes[1].plot(steps, var_traj, "r-s", label=f"方差 (目标 {tgt_var})")
axes[1].axhline(tgt_mu, color="b", linestyle="--", alpha=0.3)
axes[1].axhline(tgt_var, color="r", linestyle="--", alpha=0.3)
axes[1].set_xlabel("反向 SDE 步数"); axes[1].set_ylabel("统计量")
axes[1].set_title("反向 SDE 逐步恢复目标分布")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("reverse_sde_sampling.png", dpi=100); plt.close()

print(f"生成样本均值: {np.mean(final_reverse):.3f} (目标 {tgt_mu})")
print(f"生成样本方差: {np.var(final_reverse):.3f} (目标 {tgt_var})")
print(f"DDPM 反向采样成功恢复目标分布 (用解析 score / ε)")
print(f"注: 真实扩散模型用神经网络学 ε_θ(x_t,t); 多峰需更复杂模型")

print("\n" + "=" * 60)
print("全部完成. 输出: langevin_sampling.png, score_function.png,")
print("  ddpm_forward_diffusion.png, score_matching_loss.png, reverse_sde_sampling.png")
print("=" * 60)
