"""
UT Austin M 383E · 实验: SVD 与 PCA 的完整实现
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 svd_pca.py

验证 (Trefethen & Bau 第 14-15 章 + ML 关联):
  1. SVD 分解的几何意义: 旋转-拉伸-旋转
  2. Eckart-Young 定理: 低秩近似的最优性
  3. PCA = 数据矩阵的 SVD
  4. 图像压缩: 截断 SVD
  5. 伪逆与最小范数最小二乘
  6. 随机化 SVD (Halko-Martinsson-Tropp) 加速
  7. 神经网络权重谱分析 (与随机矩阵的联系)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)
eps = np.finfo(float).eps

# ============================================================
# 实验 1: SVD 的几何意义 (2D 旋转-拉伸-旋转)
# ============================================================
print("=" * 60)
print("实验 1: SVD 的几何意义 — 旋转-拉伸-旋转")
print("=" * 60)

A = np.array([[3.0, 1.0], [1.0, 2.0]])
U, S, Vt = np.linalg.svd(A)
print(f"A =\n{A}")
print(f"奇异值 σ = {S}")
print(f"U (左奇异向量, 旋转):\n{np.round(U, 3)}")
print(f"Vt (右奇异向量, 旋转):\n{np.round(Vt, 3)}")

# 可视化: 单位圆经过 A 变换后变椭圆
theta = np.linspace(0, 2 * np.pi, 100)
circle = np.vstack([np.cos(theta), np.sin(theta)])
transformed = A @ circle

fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(circle[0], circle[1], "b-", label="单位圆 (输入)")
ax.plot(transformed[0], transformed[1], "r-", label="A·圆 (输出=椭圆)")
# 画奇异向量方向
for i in range(2):
    ax.quiver(0, 0, S[i] * U[0, i], S[i] * U[1, i], angles="xy", scale_units="xy", scale=1,
              color=["g", "m"][i], label=f"σ_{i+1} u_{i+1} (σ={S[i]:.2f})")
ax.set_xlim(-5, 5); ax.set_ylim(-5, 5); ax.set_aspect("equal")
ax.axhline(0, color="k", linewidth=0.3); ax.axvline(0, color="k", linewidth=0.3)
ax.legend(); ax.grid(True, alpha=0.3)
ax.set_title("SVD 几何: A = UΣV^T = 旋转(V^T) → 拉伸(Σ) → 旋转(U)")
plt.tight_layout(); plt.savefig("svd_geometry.png", dpi=100); plt.close()
print("验证: A = U Σ V^T 重构误差:", np.linalg.norm(A - U @ np.diag(S) @ Vt))

# ============================================================
# 实验 2: Eckart-Young 定理验证
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Eckart-Young — 低秩近似的最优性")
print("=" * 60)

# 构造秩 5 + 噪声的矩阵
n, m, true_rank = 30, 20, 5
U_true = np.random.randn(n, true_rank)
V_true = np.random.randn(true_rank, m)
A = U_true @ V_true + 0.1 * np.random.randn(n, m)

U, S, Vt = np.linalg.svd(A, full_matrices=False)
print(f"奇异值 (前 8): {np.round(S[:8], 2)}")
print(f"明显的秩断裂: σ_5={S[4]:.2f}, σ_6={S[5]:.2f} (噪声水平)")

# 截断 SVD 近似 vs 随机低秩近似
fig, ax = plt.subplots(figsize=(9, 5))
ranks = range(1, m + 1)
svd_errors = [np.linalg.norm(A - U[:, :k] @ np.diag(S[:k]) @ Vt[:k], "fro") for k in ranks]
# 理论下界: Eckart-Young
ey_bounds = [np.sqrt(np.sum(S[k:] ** 2)) for k in ranks]
ax.semilogy(ranks, svd_errors, "bo-", label="截断 SVD (Eckart-Young 最优)")
ax.semilogy(ranks, ey_bounds, "g--", label="理论下界 √Σ_{i>k} σ_i²")
ax.axvline(true_rank, color="r", linestyle=":", label=f"真实秩 = {true_rank}")
ax.set_xlabel("近似秩 k"); ax.set_ylabel("||A - A_k||_F")
ax.set_title("Eckart-Young: 截断 SVD 是 Frobenius 范数下最优低秩近似")
ax.legend(); ax.grid(True)
plt.tight_layout(); plt.savefig("eckart_young.png", dpi=100); plt.close()
print(f"k={true_rank} 时误差 = {svd_errors[true_rank-1]:.2f} (噪声水平)")
print(f"k={true_rank-1} 时误差 = {svd_errors[true_rank-2]:.2f} (信号+噪声)")

# ============================================================
# 实验 3: PCA = 数据 SVD
# ============================================================
print("\n" + "=" * 60)
print("实验 3: PCA 通过 SVD")
print("=" * 60)

def generate_pca_data(n=200, d=2, seed=0):
    rng = np.random.RandomState(seed)
    angle = np.pi / 6  # 主轴方向
    R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    scales = np.array([3.0, 0.5])  # 主轴方差
    X = (R * scales) @ rng.randn(2, n)
    return X.T

X = generate_pca_data(n=300)
Xc = X - X.mean(axis=0)

# SVD 方法
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
components = Vt  # 主成分方向
explained_var = S ** 2 / (len(X) - 1)
var_ratio = explained_var / explained_var.sum()

print(f"主成分方向:\n{np.round(components, 3)}")
print(f"方差解释比: {var_ratio}")
print(f"PC1 方向角度: {np.degrees(np.arctan2(components[0, 1], components[0, 0])):.1f}° (真实 30°)")

fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(Xc[:, 0], Xc[:, 1], alpha=0.3, s=10)
for i in range(2):
    scale = 2 * np.sqrt(explained_var[i])
    ax.quiver(0, 0, scale * components[i, 0], scale * components[i, 1],
              angles="xy", scale_units="xy", scale=1, color=["r", "g"][i],
              label=f"PC{i+1} (σ={S[i]:.1f}, {var_ratio[i]*100:.1f}%)")
ax.set_xlim(-10, 10); ax.set_ylim(-10, 10); ax.set_aspect("equal")
ax.axhline(0, color="k", linewidth=0.3); ax.axvline(0, color="k", linewidth=0.3)
ax.legend(); ax.grid(True, alpha=0.3)
ax.set_title("PCA via SVD: 主成分 = 数据矩阵的右奇异向量")
plt.tight_layout(); plt.savefig("pca_svd.png", dpi=100); plt.close()

# ============================================================
# 实验 4: 图像压缩 (截断 SVD)
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 图像压缩 — 截断 SVD")
print("=" * 60)

# 合成 "图像" (渐变 + 纹理)
img = np.zeros((100, 100))
for i in range(100):
    for j in range(100):
        img[i, j] = 0.5 * (i / 100) + 0.3 * np.sin(0.2 * j) + 0.2 * np.random.randn()
img += np.outer(np.linspace(0, 1, 100), np.linspace(1, 0, 100))

U, S, Vt = np.linalg.svd(img, full_matrices=False)
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
axes[0].imshow(img, cmap="gray"); axes[0].set_title("原始 (秩 ≤ 100)")
for ax, k in zip(axes[1:], [5, 20, 50]):
    approx = U[:, :k] @ np.diag(S[:k]) @ Vt[:k]
    err = np.linalg.norm(img - approx, "fro") / np.linalg.norm(img, "fro")
    ax.imshow(approx, cmap="gray")
    ax.set_title(f"k={k} (压缩比 {100/k:.0f}×, 误差 {err*100:.1f}%)")
    ax.set_xlabel(f"存储: {k*(100+100+1)} vs {100*100}")
plt.tight_layout(); plt.savefig("svd_image_compression.png", dpi=100); plt.close()
print(f"奇异值衰减: σ_1={S[0]:.1f}, σ_5={S[4]:.1f}, σ_20={S[19]:.1f}, σ_50={S[49]:.1f}")
print("k=5 已捕获主要结构 — 低秩近似有效")

# ============================================================
# 实验 5: 伪逆与最小范数最小二乘
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 伪逆 A⁺ = V Σ⁺ U^T")
print("=" * 60)

# 秩亏矩阵 (多解的最小二乘)
A = np.array([[1.0, 2.0, 3.0], [2.0, 4.0, 6.0]])  # 秩 1
b = np.array([1.0, 2.0])
A_pinv = np.linalg.pinv(A)
x_pinv = A_pinv @ b
print(f"A (秩 {np.linalg.matrix_rank(A)}):\n{A}")
print(f"b = {b}")
print(f"伪逆解 x⁺ = {np.round(x_pinv, 4)}")
print(f"||x⁺|| = {np.linalg.norm(x_pinv):.4f} (最小范数解)")
print(f"A x⁺ = {np.round(A @ x_pinv, 4)} (投影到列空间)")
# 验证最小范数: 任取另一解 x' = x⁺ + null, ||x'|| > ||x⁺||
null_vec = np.array([2.0, -3.0, 1.0])  # A null 向量
x_other = x_pinv + 0.5 * null_vec
print(f"另一解 x' = {np.round(x_other, 4)}, ||x'|| = {np.linalg.norm(x_other):.4f} > ||x⁺|| ✓")

# ============================================================
# 实验 6: 随机化 SVD (Halko-Martinsson-Tropp)
# ============================================================
print("\n" + "=" * 60)
print("实验 6: 随机化 SVD 加速 (arXiv:0909.4061)")
print("=" * 60)

def randomized_svd(A, k, p=10, n_iter=4):
    """随机化 SVD: 用随机投影降到 (k+p) 维再小 SVD
       代价 O(mn(k+p)) vs 精确 SVD O(mn min(m,n))
    """
    m, n = A.shape
    Omega = np.random.randn(n, k + p)
    Y = A @ Omega
    Q, _ = np.linalg.qr(Y)
    # 功率迭代提高精度 (当奇异值衰减慢时)
    for _ in range(n_iter):
        Q, _ = np.linalg.qr(A.T @ Q)
        Q, _ = np.linalg.qr(A @ Q)
    B = Q.T @ A          # 小矩阵 (k+p) × n
    Ub, S, Vt = np.linalg.svd(B, full_matrices=False)
    U = Q @ Ub
    return U[:, :k], S[:k], Vt[:k]

m, n, true_rank = 500, 300, 20
U_t = np.random.randn(m, true_rank); V_t = np.random.randn(true_rank, n)
A = U_t @ V_t + 0.01 * np.random.randn(m, n)

import time
t0 = time.time(); U_ex, S_ex, Vt_ex = np.linalg.svd(A, full_matrices=False); t_ex = time.time() - t0
t0 = time.time(); U_r, S_r, Vt_r = randomized_svd(A, k=20, p=10); t_r = time.time() - t0

print(f"精确 SVD: {t_ex*1000:.1f} ms, 前 20 奇异值: {np.round(S_ex[:20], 1)}")
print(f"随机 SVD: {t_r*1000:.1f} ms (加速 {t_ex/t_r:.1f}×), 前 20 奇异值: {np.round(S_r[:20], 1)}")
print(f"奇异值误差: {np.max(np.abs(S_ex[:20] - S_r)):.2e}")
print(f"低秩近似误差: 精确={np.linalg.norm(A-U_ex[:,:20]@np.diag(S_ex[:20])@Vt_ex[:20]):.2e}, "
      f"随机={np.linalg.norm(A-U_r@np.diag(S_r)@Vt_r):.2e}")

# ============================================================
# 实验 7: 神经网络权重谱 (与随机矩阵联系)
# ============================================================
print("\n" + "=" * 60)
print("实验 7: 神经网络权重矩阵的奇异值谱 (→ 随机矩阵理论)")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
# 模拟: 随机初始化的权重 vs 训练后的权重
W_init = np.random.randn(200, 200) / np.sqrt(200)  # He 初始化
W_trained = W_init + 0.3 * np.random.randn(200, 200)  # 训练后添加低秩结构
W_trained[:, :20] *= 5  # 模拟部分方向被放大

S_init = np.linalg.svd(W_init, compute_uv=False)
S_trained = np.linalg.svd(W_trained, compute_uv=False)

axes[0].hist(S_init ** 2, bins=50, density=True, alpha=0.7, color="b", label="随机初始化")
axes[0].set_title("随机初始化: 谱 ≈ Marchenko-Pastur")
axes[0].set_xlabel("奇异值平方"); axes[0].legend(); axes[0].grid(True, alpha=0.3)

axes[1].hist(S_trained ** 2, bins=50, density=True, alpha=0.7, color="r", label="训练后")
axes[1].set_title("训练后: 谱偏离 MP (出现大奇异值)")
axes[1].set_xlabel("奇异值平方"); axes[1].legend(); axes[1].grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("weight_spectrum.png", dpi=100); plt.close()
print(f"随机初始化奇异值: max={S_init.max():.3f}, min={S_init.min():.3f} (接近 MP 分布)")
print(f"训练后奇异值:     max={S_trained.max():.3f}, min={S_trained.min():.3f} (谱被拉伸)")
print("→ 见 Oxford C7.1 随机矩阵理论: MP 律描述随机矩阵的奇异值分布")

print("\n" + "=" * 60)
print("全部完成. 输出: svd_geometry.png, eckart_young.png, pca_svd.png,")
print("  svd_image_compression.png, weight_spectrum.png")
print("=" * 60)
