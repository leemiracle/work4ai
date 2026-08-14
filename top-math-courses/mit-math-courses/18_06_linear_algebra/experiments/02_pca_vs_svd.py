"""
MIT 18.06 · 实验02: PCA 与 SVD 的等价性 + 四个子空间可视化
依赖: numpy, matplotlib
运行: python3 02_pca_vs_svd.py

验证:
  1. PCA via 协方差特征分解 ≡ PCA via SVD (数值等价)
  2. SVD 的 U/Σ/Vᵀ 分别张成四个基本子空间
  3. 解释方差比与奇异值的平方关系
  4. 二维数据上主成分方向的几何可视化
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(7)

# ============================================================
# 实验 1: PCA 两种实现路径的等价性
# ============================================================
print("=" * 60)
print("实验 1: PCA 两种实现路径的数值等价性")
print("=" * 60)

# 构造相关数据: 2D 椭圆 + 噪声
n = 200
angle = np.array([[1.0, 0.6],   # 协方差结构: x0 与 x1 强相关
                  [0.6, 0.4]])
X = np.random.randn(n, 2) @ np.linalg.cholesky(angle) * 3
X += np.array([5, -2])  # 平移 (非中心化)

# --- 路径 A: 协方差矩阵特征分解 ---
Xc = X - X.mean(axis=0)                       # 中心化
Cov = (Xc.T @ Xc) / (n - 1)                    # 样本协方差
eigvals_A, eigvecs_A = np.linalg.eigh(Cov)     # eigh 返回升序
eigvals_A, eigvecs_A = eigvals_A[::-1], eigvecs_A[:, ::-1]  # 降序

# --- 路径 B: SVD ---
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
eigvals_B = S ** 2 / (n - 1)
# Vt 的行 = 右奇异向量 = PCA 主方向 (注意符号可能翻转)
eigvecs_B = Vt.T

print("协方差特征分解得到的特征值:", np.round(eigvals_A, 6))
print("SVD 奇异值²/(n-1)        :", np.round(eigvals_B, 6))
print("两者数值相等:", np.allclose(eigvals_A, eigvals_B))

# 主方向: 可能差一个符号 (特征向量/奇异向量的符号不唯一)
# 比较时取绝对值
directions_match = np.allclose(np.abs(eigvecs_A), np.abs(eigvecs_B), atol=1e-10)
print("主方向一致 (符号无关):", directions_match)

# 解释方差比
explained_ratio = eigvals_A / eigvals_A.sum()
print(f"各主成分解释方差比: PC1={explained_ratio[0]:.1%}, PC2={explained_ratio[1]:.1%}")

# ============================================================
# 实验 2: SVD 揭示四个基本子空间
# ============================================================
print("\n" + "=" * 60)
print("实验 2: SVD 与四个基本子空间")
print("=" * 60)

# 构造一个秩 2 的 4×3 矩阵
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9],
              [2, 4, 6]], dtype=float)  # 第 4 行 = 2×第 1 行 -> 秩较低
U, S, Vt = np.linalg.svd(A, full_matrices=True)
r = np.sum(S > 1e-10)
print(f"A 的形状: {A.shape},  数值秩 r = {r}")
print(f"奇异值: {np.round(S, 6)}")

print("\n四个基本子空间 (由 SVD 的列给出标准正交基):")
print(f"  列空间  C(A)  ⊂ ℝ^{A.shape[0]}: U 的前 {r} 列  -> dim = {r}")
print(f"  左零空间 N(Aᵀ) ⊂ ℝ^{A.shape[0]}: U 的后 {A.shape[0]-r} 列 -> dim = {A.shape[0]-r}")
print(f"  行空间  C(Aᵀ) ⊂ ℝ-{A.shape[1]}: Vᵀ的前 {r} 行 (V 的前 {r} 列) -> dim = {r}")
print(f"  零空间  N(A)  ⊂ ℝ-{A.shape[1]}: Vᵀ的后 {A.shape[1]-r} 行 -> dim = {A.shape[1]-r}")

# 验证: A 的列应该在 U 的前 r 列张成的空间中
proj_col = U[:, :r] @ (U[:, :r].T @ A)
print(f"\nA 在其列空间中的投影误差: {np.linalg.norm(A - proj_col):.2e} (应≈0)")
# 验证: N(A) 中的向量 A x = 0
null_vec = Vt[r:].T[:, 0] if (A.shape[1] - r) > 0 else None
if null_vec is not None:
    print(f"零空间向量 x = {np.round(null_vec, 4)}")
    print(f"  A @ x = {np.round(A @ null_vec, 8)} (应≈0)")

# ============================================================
# 实验 3: 二维 PCA 几何可视化
# ============================================================
print("\n" + "=" * 60)
print("实验 3: PCA 主成分方向几何可视化")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 左图: 数据 + 主成分方向
ax = axes[0]
ax.scatter(Xc[:, 0], Xc[:, 1], s=8, alpha=0.4, color="steelblue", label="中心化数据")
scale = 3 * np.sqrt(eigvals_A)  # 用特征值的平方根缩放箭头长度
for i, color in enumerate(["crimson", "darkgreen"]):
    vec = eigvecs_A[:, i] * scale[i]
    ax.annotate("", xy=(vec[0], vec[1]), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color=color, lw=2.5))
    ax.text(vec[0]*1.1, vec[1]*1.1, f"PC{i+1}\n{explained_ratio[i]:.1%}",
            color=color, fontsize=11, fontweight="bold")
ax.axhline(0, color="gray", lw=0.5); ax.axvline(0, color="gray", lw=0.5)
ax.set_aspect("equal"); ax.legend(); ax.set_title("PCA: 主成分方向 = 协方差矩阵特征向量")
ax.set_xlabel("x0 (中心化)"); ax.set_ylabel("x1 (中心化)")

# 右图: 投影到 PC1 vs 原始 — 维度压缩
ax = axes[1]
# 投影到第 1 主成分 (1D)
proj_pc1 = Xc @ eigvecs_A[:, 0]
reconstructed = np.outer(proj_pc1, eigvecs_A[:, 0])  # 仅用 PC1 重建
ax.scatter(Xc[:, 0], Xc[:, 1], s=8, alpha=0.3, color="steelblue", label="原始数据")
ax.scatter(reconstructed[:, 0], reconstructed[:, 1], s=10, color="crimson",
           label=f"仅 PC1 重建 (保留 {explained_ratio[0]:.0%} 方差)")
# 连线
for i in range(0, n, 6):
    ax.plot([Xc[i, 0], reconstructed[i, 0]], [Xc[i, 1], reconstructed[i, 1]],
            "k-", alpha=0.2, lw=0.5)
ax.axhline(0, color="gray", lw=0.5); ax.axvline(0, color="gray", lw=0.5)
ax.set_aspect("equal"); ax.legend(); ax.set_title("降维: 投影到第 1 主成分 (垂线=损失)")
ax.set_xlabel("x0"); ax.set_ylabel("x1")

plt.suptitle("PCA = SVD: 主成分分析 = 对数据矩阵做 SVD", fontsize=13)
plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"图表已保存: {__file__.replace('.py', '.png')}")

# ============================================================
# 关键结论
# ============================================================
print("\n" + "=" * 60)
print("核心结论")
print("=" * 60)
print("""
1. PCA ≡ SVD:  对中心化数据 Xc 做奇异值分解 Xc = U Σ Vᵀ,
   则 V 的列 (= 右奇异向量) 就是 PCA 的主成分方向,
   且 特征值 λᵢ = σᵢ²/(n-1).

2. SVD 同时给出四个基本子空间的标准正交基:
   - C(A)  = span(U 的前 r 列)
   - N(Aᵀ) = span(U 的后 m-r 列)
   - C(Aᵀ) = span(V 的前 r 列)
   - N(A)  = span(V 的后 n-r 列)

3. 降维的损失 = 被丢弃的奇异值:  ‖X - X_k‖_F = √(σ²_{k+1} + ... + σ²_n)
   这就是 Eckart-Young 定理 —— SVD 给出最优低秩近似.
""")
