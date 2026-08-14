"""
Oxford Part C C7.1 · 实验: 随机矩阵谱分析 (Wigner / MP / Tracy-Widom / 神经网络权重)
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 random_matrix_spectrum.py

验证:
  1. Wigner 半圆律: 随机对称矩阵特征值 → 半圆密度
  2. Marchenko-Pastur 律: 样本协方差矩阵特征值 → MP 密度
  3. BBP 相变: spike 信号何时冒出噪声谱
  4. Tracy-Widom: 最大特征值的 N^{-2/3} 涨落
  5. 神经网络权重谱: Xavier 初始化 vs MP 律
  6. 泛化诊断: 随机权重 vs 结构化权重的谱偏离
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 辅助: 半圆律与 MP 律密度函数
# ============================================================
def semicircle_pdf(x):
    return np.sqrt(np.maximum(4 - x**2, 0)) / (2 * np.pi)

def mp_pdf(x, gamma):
    b_plus = (1 + np.sqrt(gamma))**2
    b_minus = (1 - np.sqrt(gamma))**2
    val = np.sqrt(np.maximum((b_plus - x) * (x - b_minus), 0))
    with np.errstate(divide='ignore', invalid='ignore'):
        density = val / (2 * np.pi * gamma * x)
    density[x <= 0] = 0
    return density

# ============================================================
# 实验 1: Wigner 半圆律
# ============================================================
print("=" * 60)
print("实验 1: Wigner 半圆律")
print("=" * 60)

N = 3000
A = np.random.randn(N, N)
W = (A + A.T) / np.sqrt(2 * N)   # 正确归一化: off-diag Var=1/N → 半圆律 [-2,2]
eigvals_wigner = np.linalg.eigvalsh(W)

x_grid = np.linspace(-2.5, 2.5, 1000)
print(f"  N = {N}")
print(f"  lambda_min = {eigvals_wigner.min():.4f} (理论 → -2)")
print(f"  lambda_max = {eigvals_wigner.max():.4f} (理论 → 2)")
print(f"  均值 = {eigvals_wigner.mean():.6f} (理论 = 0)")

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(eigvals_wigner, bins=100, density=True, alpha=0.5, label='经验谱')
ax.plot(x_grid, semicircle_pdf(x_grid), 'r-', lw=2.5, label=r'半圆律 $\rho_{sc}$')
ax.set_xlabel('特征值'); ax.set_ylabel('密度')
ax.set_title(f'Wigner 半圆律 (N={N})'); ax.legend(fontsize=12)
fig.tight_layout(); fig.savefig('wigner_semicircle.png', dpi=150)
print("  → 已保存 wigner_semicircle.png")

# ============================================================
# 实验 2: Marchenko-Pastur 律
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Marchenko-Pastur 律")
print("=" * 60)

for gamma_label, p, n in [("γ=0.25", 500, 2000), ("γ=1.0", 1000, 1000), ("γ=2.0", 2000, 1000)]:
    X = np.random.randn(p, n)
    S = X @ X.T / n
    eigvals_mp = np.linalg.eigvalsh(S)
    gamma = p / n
    b_plus = (1 + np.sqrt(gamma))**2
    b_minus = (1 - np.sqrt(gamma))**2
    print(f"  {gamma_label}: p={p}, n={n}")
    print(f"    MP 支撑 [{b_minus:.4f}, {b_plus:.4f}]")
    nonzero = eigvals_mp[eigvals_mp > 0.001]
    print(f"    实际 min={nonzero.min():.4f}, max={eigvals_mp.max():.4f}")
    print(f"    零特征值占比 = {(eigvals_mp < 0.001).mean():.4f} (理论 1-γ={max(1-gamma,0):.4f})")

# 画 gamma=0.25 的图
p, n = 500, 2000
X = np.random.randn(p, n)
S = X @ X.T / n
eigvals_mp = np.linalg.eigvalsh(S)
gamma = p / n
b_plus = (1 + np.sqrt(gamma))**2

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(eigvals_mp[eigvals_mp > 0.01], bins=80, density=True, alpha=0.5, label='经验谱')
x_mp = np.linspace(0.01, b_plus * 1.1, 1000)
ax.plot(x_mp, mp_pdf(x_mp, gamma), 'r-', lw=2.5, label=f'MP 律 (γ={gamma})')
ax.set_xlabel('特征值'); ax.set_ylabel('密度')
ax.set_title(f'Marchenko-Pastur 律 (p={p}, n={n})'); ax.legend(fontsize=12)
fig.tight_layout(); fig.savefig('marchenko_pastur.png', dpi=150)
print("  → 已保存 marchenko_pastur.png")

# ============================================================
# 实验 3: BBP 相变 — 信号检测
# ============================================================
print("\n" + "=" * 60)
print("实验 3: BBP 相变 (spike 信号何时冒出)")
print("=" * 60)

p, n = 500, 1000
gamma = p / n
theta_critical = np.sqrt(gamma)
b_plus = (1 + np.sqrt(gamma))**2
print(f"  γ = {gamma:.2f}, BBP 阈值 √γ = {theta_critical:.4f}")
print(f"  MP 上沿 b+ = {b_plus:.4f}")

thetas = np.linspace(0.3, 2.5, 15)
lambda_max_list = []
for theta in thetas:
    X = np.random.randn(p, n)
    S = X @ X.T / n
    v = np.random.randn(p); v /= np.linalg.norm(v)
    S_spiked = S + theta * np.outer(v, v)
    eigvals = np.linalg.eigvalsh(S_spiked)
    lambda_max_list.append(eigvals[-1])

lambda_max_arr = np.array(lambda_max_list)
# BBP 预测: theta > sqrt(gamma) 时, lambda_max = (1+theta)(1+gamma/theta)
bbp_prediction = np.where(
    thetas > theta_critical,
    (1 + thetas) * (1 + gamma / thetas),
    b_plus
)

print(f"  {'θ':>6s} {'λ_max(实际)':>12s} {'λ_max(BBP预测)':>14s}")
for i in range(len(thetas)):
    print(f"  {thetas[i]:6.3f} {lambda_max_arr[i]:12.4f} {bbp_prediction[i]:14.4f}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(thetas, lambda_max_arr, 'bo-', ms=5, label='实际 $\\lambda_{\\max}$')
ax.plot(thetas, bbp_prediction, 'r--', lw=2, label='BBP 预测')
ax.axvline(theta_critical, color='gray', ls=':', label=f'BBP 阈值 $\\sqrt{{\\gamma}}={theta_critical:.3f}$')
ax.axhline(b_plus, color='green', ls='-.', alpha=0.7, label=f'$b_+={b_plus:.3f}$')
ax.set_xlabel('信号强度 θ'); ax.set_ylabel('最大特征值')
ax.set_title('BBP 相变: 信号检测'); ax.legend(fontsize=10)
fig.tight_layout(); fig.savefig('bbp_transition.png', dpi=150)
print("  → 已保存 bbp_transition.png")

# ============================================================
# 实验 4: Tracy-Widom 涨落 (最大特征值的 N^{-2/3} 标度)
# ============================================================
print("\n" + "=" * 60)
print("实验 4: Tracy-Widom 涨落 — 最大特征值的 N^{-2/3} 标度")
print("=" * 60)

sizes = [200, 500, 1000, 2000]
n_trials = 100
for N in sizes:
    max_eigs = []
    for _ in range(n_trials):
        A = np.random.randn(N, N)
        W = (A + A.T) / np.sqrt(2 * N)
        max_eigs.append(np.linalg.eigvalsh(W)[-1])
    max_eigs = np.array(max_eigs)
    centered = N**(2/3) * (max_eigs - 2)
    print(f"  N={N:5d}: λ_max={max_eigs.mean():.6f} (→2), "
          f"N^{{2/3}}(λ_max-2) 均值={centered.mean():.4f}, std={centered.std():.4f}")
print("  (Tracy-Widom β=1: 均值≈-1.21, std≈0.9029)")
print("  ⚠️ 有限 N 时有偏差，但 N^{-2/3} 标度可验证")

# ============================================================
# 实验 5: 神经网络权重谱 — Xavier 初始化 vs MP 律
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 神经网络权重谱分析")
print("=" * 60)

fan_in, fan_out = 784, 512
# Xavier 初始化: Var = 1/fan_in
W_xavier = np.random.randn(fan_out, fan_in) / np.sqrt(fan_in)
# 不正确的初始化: Var = 1 (太大)
W_bad = np.random.randn(fan_out, fan_in)

for name, W in [("Xavier (1/√fan_in)", W_xavier), ("无缩放 (Var=1)", W_bad)]:
    S = W @ W.T
    eigvals = np.linalg.eigvalsh(S)
    gamma_w = fan_out / fan_in
    b_plus_scaled = (1 + np.sqrt(gamma_w))**2
    # Xavier 的 Gram 矩阵 ≈ (1/fan_in) * MP 支撑
    print(f"  {name}:")
    print(f"    γ = {gamma_w:.4f}, MP b+ = {b_plus_scaled:.4f}")
    print(f"    λ_max(WW^T) = {eigvals.max():.4f}")
    print(f"    λ_min(WW^T > 0) = {eigvals[eigvals>1e-6].min():.4f}")

# 画 Xavier 的谱 vs MP
S_xavier = W_xavier @ W_xavier.T
eigvals_xavier = np.linalg.eigvalsh(S_xavier)
gamma_w = fan_out / fan_in

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, W, title in [(axes[0], W_xavier, "Xavier 初始化"),
                      (axes[1], W_bad, "无缩放 (Var=1)")]:
    S = W @ W.T
    eigvals = np.linalg.eigvalsh(S)
    ax.hist(eigvals[eigvals > 1e-6], bins=60, density=True, alpha=0.5)
    # 理论 MP (需要缩放: 实际 Var(W_ij) 决定支撑)
    var_scale = np.var(W.ravel()) * fan_in  # effective variance factor
    b_p = var_scale * (1 + np.sqrt(gamma_w))**2
    b_m = var_scale * (1 - np.sqrt(gamma_w))**2
    x_th = np.linspace(max(b_m * 0.5, 1e-4), b_p * 1.1, 500)
    mp_th = mp_pdf(x_th / var_scale, gamma_w) / var_scale
    ax.plot(x_th, mp_th, 'r-', lw=2, label=f'MP (缩放×{var_scale:.1f})')
    ax.set_title(f'{title}: WW^T 谱'); ax.legend(fontsize=10)
    ax.set_xlabel('特征值')
fig.tight_layout(); fig.savefig('nn_weight_spectrum.png', dpi=150)
print("  → 已保存 nn_weight_spectrum.png")

# ============================================================
# 实验 6: 泛化诊断 — 随机 vs 结构化权重谱偏离
# ============================================================
print("\n" + "=" * 60)
print("实验 6: 谱偏离度量 (随机 vs 低秩结构)")
print("=" * 60)

d = 500
# 纯随机
W_random = np.random.randn(d, d) / np.sqrt(d)
eigvals_random = np.linalg.eigvalsh((W_random + W_random.T) / 2)

# 低秩 + 噪声 (模拟训练后的权重: 有少量大特征值)
rank = 10
U = np.random.randn(d, rank)
W_structured = U @ U.T / rank + 0.3 * np.random.randn(d, d) / np.sqrt(d)
W_structured = (W_structured + W_structured.T) / 2
eigvals_structured = np.linalg.eigvalsh(W_structured)

# 谱偏离: Kolmogorov-Smirnov 统计量
from numpy import histogram
hist_r, _ = np.histogram(eigvals_random, bins=50, range=(-3, 3), density=True)
hist_s, _ = np.histogram(eigvals_structured, bins=50, range=(-3, 3), density=True)
ks_distance = np.abs(np.cumsum(hist_r) - np.cumsum(hist_s)).max()
print(f"  随机权重 λ_max = {eigvals_random.max():.4f}")
print(f"  结构化权重 λ_max = {eigvals_structured.max():.4f} (低秩信号 → 大特征值冒出)")
print(f"  谱偏离 KS 距离 = {ks_distance:.4f}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(eigvals_random, bins=50, range=(-3, 6), density=True, alpha=0.4, label='随机权重')
ax.hist(eigvals_structured, bins=50, range=(-3, 6), density=True, alpha=0.4, label='结构化权重')
ax.axvline(2, color='r', ls='--', label='半圆律上沿 (=2)')
ax.set_xlabel('特征值'); ax.set_ylabel('密度')
ax.set_title('谱偏离: 随机 vs 结构化 (泛化诊断)'); ax.legend(fontsize=11)
fig.tight_layout(); fig.savefig('spectral_deviation.png', dpi=150)
print("  → 已保存 spectral_deviation.png")

print("\n" + "=" * 60)
print("全部实验完成! ✓")
print("=" * 60)
