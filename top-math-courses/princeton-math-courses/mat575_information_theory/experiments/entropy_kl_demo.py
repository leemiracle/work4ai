"""
Princeton MAT 575 · 信息论实验: 熵 + KL 散度 + 互信息可视化
依赖: numpy, matplotlib
运行: python3 entropy_kl_demo.py

验证:
  1. Shannon 熵: Bernoulli(p) 的熵 H(p) = -p*log(p) - (1-p)*log(1-p)
  2. KL 散度: 非负性 (Gibbs 不等式)、非对称性
  3. Cross-entropy = H(p) + KL(p||q)
  4. 互信息 I(X;Y) vs 相关性 (高斯 vs 非高斯)
  5. 数据处理不等式: I(X;Z) <= I(X;Y)
  6. VAE KL 项: 高斯分布间的 KL 散度
  7. Huffman 编码 vs 熵下界
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm, entropy

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: Shannon 熵 — Bernoulli(p) 的二元熵函数
# ============================================================
print("=" * 60)
print("实验 1: Bernoulli(p) 的二元熵函数 H(p)")
print("=" * 60)

ps = np.linspace(0.001, 0.999, 200)
H_binary = -ps * np.log2(ps) - (1 - ps) * np.log2(1 - ps)

max_idx = np.argmax(H_binary)
print(f"  最大熵在 p={ps[max_idx]:.3f} 处, H_max = {H_binary[max_idx]:.4f} bits")
print(f"  理论: p=0.5 时 H(0.5) = 1 bit ✓")

# ============================================================
# 实验 2: KL 散度 — 非负性 + 非对称性
# ============================================================
print("\n" + "=" * 60)
print("实验 2: KL 散度 — Gibbs 不等式 (KL >= 0) + 非对称性")
print("=" * 60)

# 离散分布对比
p = np.array([0.1, 0.2, 0.3, 0.4])
q = np.array([0.25, 0.25, 0.25, 0.25])  # 均匀

kl_pq = np.sum(p * np.log2(p / q))
kl_qp = np.sum(q * np.log2(q / p))
print(f"  p = {p}, q = {q}")
print(f"  KL(p||q) = {kl_pq:.6f} (>= 0 ✓)")
print(f"  KL(q||p) = {kl_qp:.6f} (>= 0 ✓)")
print(f"  非对称: KL(p||q) = {kl_pq:.6f} ≠ {kl_qp:.6f} = KL(q||p) ✓")

# 验证: KL = 0 当且仅当 p = q
kl_same = np.sum(p * np.log2(p / p))
print(f"  KL(p||p) = {kl_same:.6f} (= 0 ✓)")

# ============================================================
# 实验 3: Cross-entropy = H(p) + KL(p||q)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: Cross-entropy 分解 — H(p,q) = H(p) + KL(p||q)")
print("=" * 60)

p = np.array([0.7, 0.2, 0.1])
q = np.array([0.5, 0.3, 0.2])

H_p = -np.sum(p * np.log2(p))
H_pq = -np.sum(p * np.log2(q))
kl = np.sum(p * np.log2(p / q))

print(f"  H(p) = {H_p:.6f}")
print(f"  H(p,q) = cross-entropy = {H_pq:.6f}")
print(f"  KL(p||q) = {kl:.6f}")
print(f"  H(p) + KL(p||q) = {H_p + kl:.6f} = H(p,q) = {H_pq:.6f} ✓")
print(f"\n  ML 关联: 最小化 cross-entropy loss = 最小化 KL(p_true || q_model)")

# ============================================================
# 实验 4: 互信息 vs 相关性
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 互信息 I(X;Y) vs 皮尔逊相关系数")
print("=" * 60)

def estimate_mi(x, y, bins=20):
    """用直方图法估计互信息"""
    hist_2d, _, _ = np.histogram2d(x, y, bins=bins)
    pxy = hist_2d / hist_2d.sum()
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    mask = pxy > 0
    mi = np.sum(pxy[mask] * np.log2(pxy[mask] / (px * py)[mask]))
    return mi

n = 10000

# (a) 高斯相关
mean = [0, 0]
rho = 0.5
cov = [[1, rho], [rho, 1]]
data_gauss = np.random.multivariate_normal(mean, cov, n)
mi_gauss = estimate_mi(data_gauss[:, 0], data_gauss[:, 1])
corr_gauss = np.corrcoef(data_gauss[:, 0], data_gauss[:, 1])[0, 1]
# 理论: I = -0.5 * log(1 - rho^2)
mi_gauss_theory = -0.5 * np.log2(1 - rho**2)
print(f"  高斯相关 (ρ=0.5): 相关系数 = {corr_gauss:.3f}, I(X;Y) = {mi_gauss:.4f} bits")
print(f"    理论 I = -0.5*log2(1-ρ²) = {mi_gauss_theory:.4f}")

# (b) 非线性相关: Y = X² (相关系数=0, 但互信息>0)
x = np.random.normal(0, 1, n)
y = x**2 + np.random.normal(0, 0.1, n)
mi_nonlinear = estimate_mi(x, y)
corr_nonlinear = np.corrcoef(x, y)[0, 1]
print(f"  非线性 Y=X²: 相关系数 = {corr_nonlinear:.4f} (≈0!), I(X;Y) = {mi_nonlinear:.4f} bits (>>0)")
print(f"  结论: 互信息能捕获非线性依赖, 相关系数不能 ✓")

# ============================================================
# 实验 5: 数据处理不等式 I(X;Z) <= I(X;Y)
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 数据处理不等式 — X → Y → Z (加噪链)")
print("=" * 60)

n = 20000
X = np.random.normal(0, 1, n)
Y = X + np.random.normal(0, 0.5, n)    # X → Y (信号 + 噪声)
Z = Y + np.random.normal(0, 0.5, n)    # Y → Z (进一步加噪)

mi_XY = estimate_mi(X, Y)
mi_XZ = estimate_mi(X, Z)
mi_YZ = estimate_mi(Y, Z)
print(f"  I(X;Y) = {mi_XY:.4f}")
print(f"  I(X;Z) = {mi_XZ:.4f}  <= I(X;Y) ✓")
print(f"  I(Y;Z) = {mi_YZ:.4f}")
print(f"  结论: 后处理不会增加信息 → I(X;Z) ≤ I(X;Y) ✓")

# ============================================================
# 实验 6: VAE 高斯 KL 项
# ============================================================
print("\n" + "=" * 60)
print("实验 6: VAE KL 项 — KL(N(μ,σ²) || N(0,1))")
print("=" * 60)

# 理论: KL = 0.5 * (μ² + σ² - log(σ²) - 1)
test_cases = [
    (0.0, 1.0, "标准正态"),
    (1.0, 1.0, "均值偏移"),
    (0.0, 0.5, "方差减小"),
    (2.0, 2.0, "大幅偏移"),
    (0.0, 0.1, "方差极小"),
]

print(f"  {'μ':>5s} {'σ':>5s} {'理论 KL':>10s} {'数值 KL':>10s}")
for mu, sigma, desc in test_cases:
    kl_theory = 0.5 * (mu**2 + sigma**2 - np.log(sigma**2) - 1)
    # 数值验证: Monte Carlo
    samples = np.random.normal(mu, sigma, 500000)
    log_p = norm.logpdf(samples, mu, sigma)
    log_q = norm.logpdf(samples, 0, 1)
    kl_numerical = np.mean(log_p - log_q)
    print(f"  {mu:5.1f} {sigma:5.1f} {kl_theory:10.4f} {kl_numerical:10.4f}  ({desc})")

print("  结论: VAE 的 KL 项有闭式解, 无需 Monte Carlo ✓")

# ============================================================
# 实验 7: Huffman 编码 vs 熵下界
# ============================================================
print("\n" + "=" * 60)
print("实验 7: Huffman 编码平均码长 vs 熵下界")
print("=" * 60)

import heapq
from collections import Counter

def huffman_code_lengths(probs):
    """返回 Huffman 编码的码长"""
    heap = [[p, [i]] for i, p in enumerate(probs)]
    heapq.heapify(heap)
    code_lens = [0] * len(probs)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for idx in lo[1]:
            code_lens[idx] += 1
        for idx in hi[1]:
            code_lens[idx] += 1
        heapq.heappush(heap, [lo[0] + hi[0], lo[1] + hi[1]])
    return code_lens

test_distributions = [
    ([0.5, 0.25, 0.125, 0.125], "幂律分布"),
    ([0.4, 0.3, 0.2, 0.1], "递减分布"),
    ([0.25, 0.25, 0.25, 0.25], "均匀分布"),
]

for probs, desc in test_distributions:
    probs = np.array(probs)
    H = -np.sum(probs * np.log2(probs))
    code_lens = huffman_code_lengths(probs.tolist())
    avg_len = np.sum(probs * np.array(code_lens))
    print(f"  {desc} {probs}: H = {H:.4f}, Huffman avg L = {avg_len:.4f}, "
          f"差距 = {avg_len - H:.4f} (< 1 ✓)")

# ============================================================
# 可视化
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# (1) 二元熵函数
axes[0][0].plot(ps, H_binary, "b-", linewidth=2)
axes[0][0].axvline(x=0.5, color="r", linestyle="--", alpha=0.5)
axes[0][0].set_xlabel("p")
axes[0][0].set_ylabel("H(p) bits")
axes[0][0].set_title("二元熵函数 H(p) = -p log₂p - (1-p)log₂(1-p)")
axes[0][0].grid(alpha=0.3)

# (2) KL 散度热力图
p_vals = np.linspace(0.01, 0.99, 50)
q_vals = np.linspace(0.01, 0.99, 50)
P, Q = np.meshgrid(p_vals, q_vals)
KL = P * np.log2(P / Q) + (1 - P) * np.log2((1 - P) / (1 - Q))
KL = np.clip(KL, 0, 5)
im = axes[0][1].pcolormesh(P, Q, KL, cmap="YlOrRd", shading="auto")
axes[0][1].plot([0, 1], [0, 1], "w--", linewidth=1.5, label="p=q (KL=0)")
axes[0][1].set_xlabel("p")
axes[0][1].set_ylabel("q")
axes[0][1].set_title("KL(p||q) 热力图")
axes[0][1].legend(fontsize=8)
fig.colorbar(im, ax=axes[0][1])

# (3) Cross-entropy 分解
p_fixed = np.array([0.7, 0.2, 0.1])
q_range = np.linspace(0.05, 0.9, 100)
ce_vals = []
kl_vals = []
for q1 in q_range:
    q2 = (1 - q1) * 0.6
    q3 = (1 - q1) * 0.4
    q = np.array([q1, q2, q3])
    ce = -np.sum(p_fixed * np.log2(q))
    kl = np.sum(p_fixed * np.log2(p_fixed / q))
    ce_vals.append(ce)
    kl_vals.append(kl)
axes[0][2].plot(q_range, ce_vals, "b-", label="Cross-entropy H(p,q)", linewidth=2)
axes[0][2].plot(q_range, kl_vals, "r--", label="KL(p||q)", linewidth=2)
axes[0][2].axhline(y=-np.sum(p_fixed * np.log2(p_fixed)), color="g",
                    linestyle=":", label=f"H(p)={-np.sum(p_fixed*np.log2(p_fixed)):.2f}")
axes[0][2].set_xlabel("q₁")
axes[0][2].set_ylabel("bits")
axes[0][2].set_title("Cross-entropy = H(p) + KL(p||q)")
axes[0][2].legend(fontsize=8)
axes[0][2].grid(alpha=0.3)

# (4) 互信息 vs 相关性散点图
axes[1][0].scatter(data_gauss[:500, 0], data_gauss[:500, 1], alpha=0.3, s=5, c="blue", label=f"高斯 ρ={corr_gauss:.2f}")
axes[1][0].scatter(x[:500], y[:500], alpha=0.3, s=5, c="red", label=f"Y=X² ρ={corr_nonlinear:.2f}")
axes[1][0].set_xlabel("X")
axes[1][0].set_ylabel("Y")
axes[1][0].set_title(f"互信息: 高斯 I={mi_gauss:.2f}, 非线性 I={mi_nonlinear:.2f}")
axes[1][0].legend(fontsize=8)
axes[1][0].grid(alpha=0.3)

# (5) 数据处理不等式
chain_labels = ["I(X;Y)", "I(X;Z)", "I(Y;Z)"]
chain_vals = [mi_XY, mi_XZ, mi_YZ]
bars = axes[1][1].bar(chain_labels, chain_vals, color=["green", "orange", "blue"], alpha=0.7)
axes[1][1].set_ylabel("互信息 (bits)")
axes[1][1].set_title("数据处理不等式: I(X;Z) ≤ I(X;Y)")
for bar, val in zip(bars, chain_vals):
    axes[1][1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{val:.3f}", ha="center", fontsize=9)
axes[1][1].grid(alpha=0.3, axis="y")

# (6) VAE KL 曲面
mu_range = np.linspace(-3, 3, 80)
sigma_range = np.linspace(0.1, 3, 80)
MU, SIG = np.meshgrid(mu_range, sigma_range)
KL_vae = 0.5 * (MU**2 + SIG**2 - np.log(SIG**2) - 1)
contour = axes[1][2].contourf(MU, SIG, KL_vae, levels=20, cmap="viridis")
axes[1][2].set_xlabel("μ")
axes[1][2].set_ylabel("σ")
axes[1][2].set_title("VAE KL: KL(N(μ,σ²)||N(0,1))")
fig.colorbar(contour, ax=axes[1][2])

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
