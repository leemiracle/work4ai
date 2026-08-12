"""
MIT 18.06 · 实验01: SVD 与 PCA 实战
依赖: numpy, matplotlib (纯标准库+科学计算, 零额外依赖)
运行: python3 01_svd_demo.py

验证:
  1. SVD 分解的正确性 (A ≈ U @ Σ @ Vt)
  2. Eckart-Young 定理: 低秩近似的最优性
  3. PCA 与 SVD 的等价性
  4. 图像压缩: 用 SVD 压缩一张合成图像
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 实验 1: SVD 分解与验证
# ============================================================
print("=" * 60)
print("实验 1: SVD 分解与验证")
print("=" * 60)

# 构造一个秩 3 的 5×4 矩阵
A = np.random.randn(5, 4)
U, S, Vt = np.linalg.svd(A, full_matrices=False)

print(f"A 的形状: {A.shape}")
print(f"U 的形状: {U.shape}")
print(f"S (奇异值): {np.round(S, 4)}")
print(f"Vt 的形状: {Vt.shape}")

# 验证 A = U Σ Vt
A_reconstructed = U @ np.diag(S) @ Vt
reconstruction_error = np.linalg.norm(A - A_reconstructed)
print(f"\n重建误差 ||A - UΣVt||: {reconstruction_error:.2e} (应≈0)")

# 验证 U 和 V 的正交性
print(f"U^T U ≈ I: {np.allclose(U.T @ U, np.eye(U.shape[1]))}")
print(f"V^T V ≈ I: {np.allclose(Vt @ Vt.T, np.eye(Vt.shape[0]))}")

# ============================================================
# 实验 2: Eckart-Young 定理 — 低秩近似的最优性
# ============================================================
print("\n" + "=" * 60)
print("实验 2: Eckart-Young 定理验证")
print("=" * 60)

# 构造一个有明确秩结构的矩阵 (秩 5)
n, m, true_rank = 20, 15, 5
U_true = np.random.randn(n, true_rank)
V_true = np.random.randn(true_rank, m)
A = U_true @ V_true + 0.01 * np.random.randn(n, m)  # 加小噪声

U, S, Vt = np.linalg.svd(A, full_matrices=False)

print(f"奇异值: {np.round(S, 2)}")
print(f"前 {true_rank} 个奇异值明显大于后续 (噪声)")

# 对 k=1,2,...,10 计算低秩近似的误差
for k in range(1, 11):
    A_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    error_svd = np.linalg.norm(A - A_k, "fro")
    # 对比: 随机投影的误差 (远大于 SVD)
    proj = np.random.randn(m, k)
    A_random = A @ proj @ np.linalg.pinv(proj)
    error_random = np.linalg.norm(A - A_random, "fro")
    print(f"  k={k:2d}: SVD 误差={error_svd:.4f}, 随机投影={error_random:.4f}, "
          f"比值={error_random/error_svd:.2f}x")

print("\n结论: SVD 低秩近似始终 ≤ 随机投影 (Eckart-Young 定理)")

# ============================================================
# 实验 3: PCA 与 SVD 等价性
# ============================================================
print("\n" + "=" * 60)
print("实验 3: PCA 与 SVD 等价性")
print("=" * 60)

# 生成 100 个 5 维样本, 前 2 维有强相关性
n_samples, n_features = 100, 5
X = np.random.randn(n_samples, n_features)
X[:, 1] = X[:, 0] * 2 + 0.1 * np.random.randn(n_samples)  # 列1=2*列0+噪声

# 方法 1: PCA via 协方差矩阵特征分解
X_centered = X - X.mean(axis=0)
C = X_centered.T @ X_centered / (n_samples - 1)  # 协方差矩阵
eigenvalues, eigenvectors = np.linalg.eigh(C)
# eigh 返回升序, 翻转为降序
eigenvalues = eigenvalues[::-1]
eigenvectors = eigenvectors[:, ::-1]

# 方法 2: PCA via SVD
U_svd, S_svd, Vt_svd = np.linalg.svd(X_centered, full_matrices=False)
# PCA 主成分 = Vt 的行 = SVD 的右奇异向量

print("方法 1 (协方差特征分解) 的前 2 个特征值:")
print(f"  {np.round(eigenvalues[:2], 4)}")
print("方法 2 (SVD) 的前 2 个奇异值²/(n-1):")
print(f"  {np.round(S_svd[:2]**2 / (n_samples - 1), 4)}")
print(f"两种方法等价: {np.allclose(eigenvalues[:2], S_svd[:2]**2/(n_samples-1), atol=1e-10)}")

# 解释方差比
total_var = eigenvalues.sum()
explained_ratio = eigenvalues / total_var
print(f"\n各主成分解释方差比: {np.round(explained_ratio, 4)}")
print(f"前 2 个主成分累计解释: {explained_ratio[:2].sum()*100:.1f}%")

# ============================================================
# 实验 4: 图像压缩 (SVD 低秩近似)
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 图像压缩")
print("=" * 60)

# 合成一个"棋盘+渐变"图像
img_size = 64
x = np.linspace(0, 2*np.pi, img_size)
y = np.linspace(0, 2*np.pi, img_size)
X_grid, Y_grid = np.meshgrid(x, y)
img = np.sin(X_grid) * np.cos(Y_grid) + 0.5 * np.sin(3*X_grid + Y_grid)
img += 0.1 * np.random.randn(img_size, img_size)

# SVD 压缩
U_img, S_img, Vt_img = np.linalg.svd(img, full_matrices=False)

fig, axes = plt.subplots(2, 3, figsize=(12, 8))
axes[0, 0].imshow(img, cmap="viridis")
axes[0, 0].set_title(f"原图 (rank={img_size})")
axes[0, 0].axis("off")

for idx, k in enumerate([1, 5, 10, 20, 50]):
    row, col = (idx + 1) // 3, (idx + 1) % 3
    img_k = U_img[:, :k] @ np.diag(S_img[:k]) @ Vt_img[:k, :]
    error = np.linalg.norm(img - img_k, "fro") / np.linalg.norm(img, "fro")
    storage_ratio = k * (img_size + img_size + 1) / (img_size * img_size)
    axes[row, col].imshow(img_k, cmap="viridis")
    axes[row, col].set_title(f"k={k}, 误差={error:.1%}, 存储={storage_ratio:.1%}")
    axes[row, col].axis("off")

plt.suptitle("SVD 图像压缩: 低秩近似效果", fontsize=14)
plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"图表已保存: {__file__.replace('.py', '.png')}")

# 数值总结
print("\n压缩效果总结:")
for k in [1, 5, 10, 20, 50, 64]:
    img_k = U_img[:, :k] @ np.diag(S_img[:k]) @ Vt_img[:k, :]
    error = np.linalg.norm(img - img_k, "fro") / np.linalg.norm(img, "fro")
    storage = k * (img_size + img_size + 1) / (img_size * img_size)
    print(f"  k={k:2d}: 相对误差={error:.2%}, 存储比={storage:.1%}")
