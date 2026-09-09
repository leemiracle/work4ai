"""
ETH 401-3651 · 实验: SDE 的 Euler-Maruyama 数值解
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 euler_maruyama_sde.py

验证 (Kloeden-Platen + Higham 2001 SIAM Review 风格):
  1. 布朗运动模拟: W_t 增量 ~ sqrt(dt) N(0,1)
  2. Euler-Maruyama vs Milstein 强收敛阶对比
  3. 几何布朗运动 (Black-Scholes): 数值解 vs 显式解
  4. OU 过程: 平稳分布验证
  5. 强收敛 vs 弱收敛的蒙特卡洛验证
  6. 多维 SDE: 扩散模型前向过程模拟
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 数值格式实现
# ============================================================
def euler_maruyama(a, b, x0, T, N, n_paths=1, seed=None):
    """dX = a(X) dt + b(X) dW, Euler-Maruyama, 返回 (n_paths, N+1) 轨迹"""
    rng = np.random.RandomState(seed)
    dt = T / N
    dW = np.sqrt(dt) * rng.randn(n_paths, N)
    X = np.zeros((n_paths, N + 1)); X[:, 0] = x0
    for i in range(N):
        X[:, i+1] = X[:, i] + a(X[:, i]) * dt + b(X[:, i]) * dW[:, i]
    return X, dW

def milstein(a, b, b_prime, x0, T, N, n_paths=1, seed=None):
    """Milstein: 加 Itô 校正 0.5 b b' ((dW)^2 - dt)"""
    rng = np.random.RandomState(seed)
    dt = T / N
    dW = np.sqrt(dt) * rng.randn(n_paths, N)
    X = np.zeros((n_paths, N + 1)); X[:, 0] = x0
    for i in range(N):
        bi = b(X[:, i]); bpi = b_prime(X[:, i])
        X[:, i+1] = (X[:, i] + a(X[:, i]) * dt + bi * dW[:, i]
                     + 0.5 * bi * bpi * (dW[:, i]**2 - dt))
    return X, dW

# ============================================================
# 实验 1: 布朗运动模拟
# ============================================================
print("=" * 60)
print("实验 1: 布朗运动 W_t 模拟")
print("=" * 60)

T, N = 1.0, 1000
dt = T / N
dW = np.sqrt(dt) * np.random.randn(50, N)
W = np.cumsum(dW, axis=1)
W = np.hstack([np.zeros((50, 1)), W])
t = np.linspace(0, T, N + 1)

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].plot(t, W[:20].T, alpha=0.5)
axes[0].plot(t, np.zeros_like(t), "k-", linewidth=0.5)
axes[0].set_title("布朗运动 20 条轨迹"); axes[0].set_xlabel("t"); axes[0].set_ylabel("$W_t$")
axes[0].grid(True, alpha=0.3)
# 验证: Var(W_T) ≈ T
axes[1].hist(W[:, -1], bins=30, density=True, alpha=0.7)
x_grid = np.linspace(-3, 3, 100)
axes[1].plot(x_grid, np.exp(-x_grid**2 / 2) / np.sqrt(2 * np.pi), "r-", lw=2, label="N(0,1)")
axes[1].set_title(f"$W_T$ 分布: 经验 vs N(0,T) (Var={np.var(W[:,-1]):.3f}, 应≈{T})")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("brownian_motion.png", dpi=100); plt.close()
print(f"Var(W_T) = {np.var(W[:,-1]):.4f} (理论 = {T})")

# ============================================================
# 实验 2: Euler-Maruyama vs Milstein 强收敛阶
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Euler-Maruyama vs Milstein 强收敛阶")
print("=" * 60)

# 测试 SDE: dX = 2X dt + 0.5 X dW (有显式解)
# 显式解: X_t = X_0 exp((2 - 0.5*0.5^2) t + 0.5 W_t) = X_0 exp(1.875 t + 0.5 W_t)
lam, mu = 2.0, 0.5
def exact_sol(X0, W_T, T):
    return X0 * np.exp((lam - 0.5 * mu**2) * T + mu * W_T)

X0, T = 1.0, 1.0
n_paths_mc = 500  # 蒙特卡洛路径数

Ns = [16, 32, 64, 128, 256, 512, 1024]
strong_err_em, strong_err_mil = [], []

for N in Ns:
    rng_seed = 123
    # 用同一布朗运动驱动两种格式
    X_em, dW_em = euler_maruyama(lambda x: lam*x, lambda x: mu*x, X0, T, N, n_paths_mc, seed=rng_seed)
    # Milstein 用同样的 dW
    dt = T / N
    X_mil = np.zeros_like(X_em); X_mil[:, 0] = X0
    for i in range(N):
        bi = mu * X_mil[:, i]
        X_mil[:, i+1] = (X_mil[:, i] + lam * X_mil[:, i] * dt + bi * dW_em[:, i]
                         + 0.5 * bi * mu * (dW_em[:, i]**2 - dt))
    # 显式解
    W_T = np.cumsum(dW_em, axis=1)[:, -1]
    X_exact = exact_sol(X0, W_T, T)
    # 强误差
    strong_err_em.append(np.mean(np.abs(X_em[:, -1] - X_exact)))
    strong_err_mil.append(np.mean(np.abs(X_mil[:, -1] - X_exact)))

fig, ax = plt.subplots(figsize=(8, 5))
dts = [T / N for N in Ns]
ax.loglog(dts, strong_err_em, "ro-", label="Euler-Maruyama")
ax.loglog(dts, strong_err_mil, "bs-", label="Milstein")
# 理论参考线
ref_em = strong_err_em[0] * (np.array(dts) / dts[0])**0.5
ref_mil = strong_err_mil[0] * (np.array(dts) / dts[0])**1.0
ax.loglog(dts, ref_em, "r--", alpha=0.5, label="$O(\\sqrt{\\Delta t})$ 参考线")
ax.loglog(dts, ref_mil, "g--", alpha=0.5, label="$O(\\Delta t)$ 参考线")
ax.set_xlabel("时间步 $\\Delta t$"); ax.set_ylabel("强误差 $\\mathbb{E}|X_N - X_T|$")
ax.set_title("强收敛阶: EM=0.5, Milstein=1.0 (理论验证)")
ax.legend(); ax.grid(True)
plt.tight_layout(); plt.savefig("sde_strong_convergence.png", dpi=100); plt.close()

# 估计收敛阶 (最小二乘斜率)
em_order = np.polyfit(np.log(dts), np.log(strong_err_em), 1)[0]
mil_order = np.polyfit(np.log(dts), np.log(strong_err_mil), 1)[0]
print(f"Euler-Maruyama 估计强收敛阶: {em_order:.3f} (理论 0.5)")
print(f"Milstein       估计强收敛阶: {mil_order:.3f} (理论 1.0)")

# ============================================================
# 实验 3: 几何布朗运动 (Black-Scholes)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 几何布朗运动 dX = μX dt + σX dW")
print("=" * 60)

mu_bs, sigma_bs = 0.10, 0.30
X_gbm, _ = euler_maruyama(lambda x: mu_bs*x, lambda x: sigma_bs*x, 100.0, 1.0, 500, 50, seed=7)

fig, ax = plt.subplots(figsize=(10, 5))
t = np.linspace(0, 1, 501)
ax.plot(t, X_gbm.T, alpha=0.3, color="steelblue")
ax.plot(t, 100 * np.exp(mu_bs * t), "r--", lw=2, label=f"$S_0 e^{{\\mu t}}$ (确定性趋势)")
ax.axhline(100, color="k", linewidth=0.5)
ax.set_title(f"几何布朗运动 (μ={mu_bs}, σ={sigma_bs}): 50 条股价路径")
ax.set_xlabel("t (年)"); ax.set_ylabel("S(t)"); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("geometric_brownian.png", dpi=100); plt.close()

# 蒙特卡洛期权定价: E[max(S_T - K, 0)] e^{-rT}
K, r = 105.0, 0.05
S_T = X_gbm[:, -1]
call_price = np.exp(-r * 1.0) * np.mean(np.maximum(S_T - K, 0))
# Black-Scholes 公式 (参考)
from math import log, sqrt, exp
from scipy.stats import norm
d1 = (log(100/K) + (r + 0.5*sigma_bs**2)*1.0) / (sigma_bs*sqrt(1.0))
d2 = d1 - sigma_bs*sqrt(1.0)
bs_price = 100*norm.cdf(d1) - K*exp(-r)*norm.cdf(d2)
print(f"蒙特卡洛期权价格: {call_price:.4f}")
print(f"Black-Scholes 公式: {bs_price:.4f}")
print(f"误差: {abs(call_price - bs_price):.4f}")

# ============================================================
# 实验 4: OU 过程平稳分布
# ============================================================
print("\n" + "=" * 60)
print("实验 4: Ornstein-Uhlenbeck 过程 dX = -θX dt + σ dW")
print("=" * 60)

theta, sigma_ou = 2.0, 1.0
X_ou, _ = euler_maruyama(lambda x: -theta*x, lambda x: sigma_ou, 5.0, 5.0, 2000, 1000, seed=11)

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
t_ou = np.linspace(0, 5, 2001)
axes[0].plot(t_ou, X_ou[:30].T, alpha=0.4)
axes[0].axhline(0, color="k", linewidth=0.5)
axes[0].set_title(f"OU 过程 (θ={theta}, σ={sigma_ou}): 回归到 0")
axes[0].set_xlabel("t"); axes[0].grid(True, alpha=0.3)
# 平稳分布: N(0, σ²/(2θ))
var_ss = sigma_ou**2 / (2 * theta)
axes[1].hist(X_ou[:, -1], bins=40, density=True, alpha=0.7, label="数值平稳分布")
x_grid = np.linspace(-3, 3, 100)
axes[1].plot(x_grid, np.exp(-x_grid**2/(2*var_ss))/np.sqrt(2*np.pi*var_ss), "r-", lw=2,
             label=f"$N(0, \\sigma^2/2\\theta)$ = N(0,{var_ss:.2f})")
axes[1].set_title("OU 平稳分布验证")
axes[1].legend(); axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("ornstein_uhlenbeck.png", dpi=100); plt.close()
print(f"数值平稳分布方差: {np.var(X_ou[:,-1]):.4f} (理论 {var_ss:.4f})")

# ============================================================
# 实验 5: 弱收敛验证 (分布/期望)
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 弱收敛验证 — E[X_T] 与 E[X_T^2]")
print("=" * 60)

# 同一 SDE: dX = 2X dt + 0.5X dW
# E[X_T] = X_0 exp(2T) = exp(2)
target_m1 = X0 * np.exp(lam * T)
target_m2 = X0**2 * np.exp((2*lam + mu**2)*T)  # E[X_T^2]

weak_err = []
for N in Ns:
    samples = []
    for s in range(20):
        X, _ = euler_maruyama(lambda x: lam*x, lambda x: mu*x, X0, T, N, 200, seed=1000+s)
        samples.append(X[:, -1])
    samples = np.concatenate(samples)
    m1 = np.mean(samples); m2 = np.mean(samples**2)
    weak_err.append(abs(m1 - target_m1) / target_m1)
    print(f"  N={N:5d}: E[X_T]={m1:.4f} (理论 {target_m1:.4f}), E[X_T²]={m2:.4f} (理论 {target_m2:.4f})")

print("弱收敛: 相对误差应随 N 增加而 O(1/N) 下降")

# ============================================================
# 实验 6: 扩散模型前向过程 (VP SDE 模拟)
# ============================================================
print("\n" + "=" * 60)
print("实验 6: 扩散模型前向过程 (VP SDE 离散化)")
print("=" * 60)

# DDPM 前向: x_t = sqrt(α_bar_t) x_0 + sqrt(1 - α_bar_t) ε
# 连续版 (VP SDE): dX = -0.5 β(t) X dt + sqrt(β(t)) dW
beta = 0.5  # 较大的 β 使前向在 T=1 内充分扩散到 N(0,I)

x0_data = np.array([3.0, 4.0])  # "数据点" (2D)
n_particles = 100
T_diff, N_diff = 1.0, 500
dt_diff = T_diff / N_diff

# 手写多维 Euler-Maruyama (x0 是向量, 多粒子)
rng = np.random.RandomState(22)
X_diff = np.tile(x0_data, (n_particles, 1)).astype(float)
X_diff_traj = [X_diff.copy()]
for i in range(N_diff):
    drift = -0.5 * beta * X_diff
    diff = np.sqrt(beta * dt_diff) * rng.randn(n_particles, 2)
    X_diff = X_diff + drift * dt_diff + diff
    if (i + 1) % 50 == 0:
        X_diff_traj.append(X_diff.copy())
X_diff_traj = np.array(X_diff_traj)  # (n_time, n_particles, 2)

fig, ax = plt.subplots(figsize=(8, 6))
for p in range(min(100, n_particles)):
    ax.plot(X_diff_traj[:, p, 0], X_diff_traj[:, p, 1], alpha=0.2, color="steelblue", linewidth=0.5)
ax.scatter(X_diff_traj[0, :, 0], X_diff_traj[0, :, 1], c="g", s=30, zorder=5, label=f"$t=0$ (数据, $x_0$)")
ax.scatter(X_diff_traj[-1, :, 0], X_diff_traj[-1, :, 1], c="r", s=10, alpha=0.5, zorder=5, label=f"$t=T$ (纯噪声)")
ax.set_title(f"扩散模型前向过程 (VP SDE, β={beta}): 数据 → 噪声")
ax.set_xlabel("$x_1$"); ax.set_ylabel("$x_2$"); ax.legend(); ax.grid(True, alpha=0.3)
ax.set_aspect("equal")
plt.tight_layout(); plt.savefig("diffusion_forward.png", dpi=100); plt.close()

# 验证 t=T 时分布接近 N(0, I)
final = X_diff_traj[-1]
print(f"t=T 时均值: {np.round(np.mean(final, axis=0), 3)} (应≈0)")
print(f"t=T 时方差: {np.round(np.var(final, axis=0), 3)} (VP 保持方差 ≈1)")
print("扩散模型 = 从数据分布到 N(0,I) 的 SDE 演化; 生成 = 反向 SDE")

print("\n" + "=" * 60)
print("全部完成. 输出: brownian_motion.png, sde_strong_convergence.png,")
print("  geometric_brownian.png, ornstein_uhlenbeck.png, diffusion_forward.png")
print("=" * 60)
