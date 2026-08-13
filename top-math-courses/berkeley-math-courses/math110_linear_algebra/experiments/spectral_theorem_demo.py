"""
Berkeley MATH 110 · 实验01: 谱定理可视化 (Axler 风格)
依赖: numpy, matplotlib
运行: python3 spectral_theorem_demo.py

验证 Axler 第 7 章谱定理:
  1. 对称(自伴)矩阵: 特征值全实, 特征向量正交
  2. 正规矩阵 vs 非正规矩阵: 只有正规矩阵能正交对角化
  3. 正定算子的平方根: Σ = LLᵀ (协方差分解 / Cholesky)
  4. 奇异值的 Axler 定义: σᵢ = √(λᵢ(AᵀA))
  5. 二次型椭球: 对称矩阵的特征值 = 椭球半轴
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(11)

# ============================================================
# 实验 1: 实谱定理 —— 对称矩阵的特征值与特征向量
# ============================================================
print("=" * 60)
print("实验 1: 实谱定理 (Axler 7.29)")
print("=" * 60)

# 构造对称矩阵 S = (A + Aᵀ)/2
A = np.random.randn(4, 4)
S = (A + A.T) / 2  # 对称 = 自伴 (实情形)
print(f"S 对称? {np.allclose(S, S.T)}")

eigvals, eigvecs = np.linalg.eigh(S)  # 对称矩阵用 eigh
print(f"特征值: {np.round(eigvals, 4)}")
print(f"特征值全实? {np.allclose(eigvals.imag, 0)}")  # 谱定理保证
print(f"特征向量正交? {np.allclose(eigvecs @ eigvecs.T, np.eye(4))}")  # 谱定理保证
# 验证 S = Q Λ Qᵀ
recon = eigvecs @ np.diag(eigvals) @ eigvecs.T
print(f"S = QΛQᵀ 重建正确? {np.allclose(recon, S)}")

# ============================================================
# 实验 2: 正规 vs 非正规 —— 只有正规矩阵能正交对角化
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 正规 vs 非正规 (Axler 复谱定理 7.24)")
print("=" * 60)

# 正规矩阵: Hermite T = T*
T_normal = np.array([[2, 1j], [-1j, 3]])
is_normal = np.allclose(T_normal @ T_normal.conj().T, T_normal.conj().T @ T_normal)
print(f"T_normal 正规? {is_normal}")
ew, ev = np.linalg.eig(T_normal)
print(f"  特征向量酉正交? {np.allclose(ev @ ev.conj().T, np.eye(2))}")

# 非正规矩阵: 一般矩阵
T_nonormal = np.array([[1, 1], [0, 2]])  # 上三角, 非正规
is_normal2 = np.allclose(T_nonormal @ T_nonormal.T, T_nonormal.T @ T_nonormal)
print(f"T_nonormal 正规? {is_normal2}")
ew2, ev2 = np.linalg.eig(T_nonormal)
print(f"  特征向量正交? {np.allclose(ev2 @ ev2.T, np.eye(2))}")
print("  → 非正规矩阵特征向量不正交, 无法正交对角化 (谱定理不适用)")

# ============================================================
# 实验 3: 正定算子的平方根 (Axler 7.36)
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 正定算子的平方根 (协方差分解 Σ = LLᵀ)")
print("=" * 60)

# 构造正定矩阵 P
B = np.random.randn(3, 3)
P = B @ B.T + 0.1 * np.eye(3)  # 正定
eigvals_P = np.linalg.eigvalsh(P)
print(f"P 的特征值: {np.round(eigvals_P, 4)} (全 > 0 → 正定)")

# 平方根: P = Q Λ Qᵀ → √P = Q √Λ Qᵀ
L, Q = np.linalg.eigh(P)  # eigh 返回 (特征值, 特征向量)
sqrt_P = Q @ np.diag(np.sqrt(L)) @ Q.T
print(f"(√P)² = P? {np.allclose(sqrt_P @ sqrt_P, P)}")

# 对比 numpy 的 Cholesky (下三角)
L_chol = np.linalg.cholesky(P)
print(f"Cholesky: L Lᵀ = P? {np.allclose(L_chol @ L_chol.T, P)}")
print("→ 协方差矩阵 Σ = LLᵀ: 用 L 乘标准正态 z 即可生成相关样本 x = μ + Lz")

# ============================================================
# 实验 4: 奇异值的 Axler 定义 σᵢ = √(λᵢ(AᵀA))
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 奇异值 = √(λᵢ(AᵀA)) (Axler 定义, 7.52)")
print("=" * 60)

M = np.random.randn(5, 3)
# Axler: σᵢ = √(AᵀA 的特征值)
eig_AtA = np.linalg.eigvalsh(M.T @ M)  # AᵀA 半正定
axler_sv = np.sqrt(np.sort(eig_AtA)[::-1])
# numpy SVD
numpy_sv = np.linalg.svd(M, compute_uv=False)
print(f"Axler 定义奇异值: {np.round(axler_sv, 6)}")
print(f"numpy SVD 奇异值:  {np.round(numpy_sv, 6)}")
print(f"两者一致? {np.allclose(axler_sv, numpy_sv)}")

# ============================================================
# 实验 5: 二次型椭球 —— 特征值 = 椭球半轴
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 二次型 xᵀSx = const 的等高线是椭球")
print("=" * 60)

S2 = np.array([[2.0, 0.5], [0.5, 1.0]])  # 对称正定
ev2, Q2 = np.linalg.eigh(S2)
print(f"特征值 (椭球半轴²的倒数): {np.round(ev2, 4)}")
print(f"特征向量 (主轴方向):\n{np.round(Q2, 4)}")

# 画等高线 + 主轴
fig, ax = plt.subplots(figsize=(7, 7))
x = np.linspace(-2, 2, 300); y = np.linspace(-2, 2, 300)
X, Y = np.meshgrid(x, y)
Z = S2[0,0]*X**2 + 2*S2[0,1]*X*Y + S2[1,1]*Y**2  # xᵀSx
cs = ax.contour(X, Y, Z, levels=10, cmap="viridis")
ax.clabel(cs, inline=True, fontsize=7, fmt="%.1f")

# 主轴方向 = 特征向量, 长度 ∝ 1/√λ
for i in range(2):
    axis_dir = Q2[:, i] / np.sqrt(ev2[i])  # 半轴方向 × 长度
    ax.annotate("", xy=axis_dir, xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="crimson", lw=2.5))
    ax.annotate("", xy=-axis_dir, xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="crimson", lw=2.5))
    ax.text(axis_dir[0]*1.15, axis_dir[1]*1.15, f"λ={ev2[i]:.2f}",
            color="crimson", fontsize=12, fontweight="bold")

ax.set_aspect("equal"); ax.grid(True, alpha=0.3)
ax.axhline(0, color="gray", lw=0.5); ax.axvline(0, color="gray", lw=0.5)
ax.set_title("谱定理: xᵀSx=const 等高线 = 椭球\n红箭头 = 特征向量(主轴), 长度 ∝ 1/√λ")
ax.set_xlabel("x₀"); ax.set_ylabel("x₁")

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"图表已保存: {__file__.replace('.py', '.png')}")

print("\n" + "=" * 60)
print("核心结论 (Axler 谱定理的工程意义)")
print("=" * 60)
print("""
1. 对称/自伴矩阵: 谱定理保证特征值实 + 特征向量正交.
   → PCA 的主轴一定存在且正交, 这是定理不是巧合.

2. 正规矩阵: 复谱定理保证能酉对角化. 非正规矩阵不行.

3. 正定算子有平方根 √P: 协方差 Σ=LLᵀ 是其特例,
   用于生成相关高斯样本 x = μ + Lz.

4. 奇异值 σᵢ = √(λᵢ(AᵀA)): Axler 用算子结构定义,
   与 SVD 的几何定义 UΣVᵀ 数值一致.

5. 二次型 xᵀSx 的等高线是椭球, 主轴 = 特征向量,
   半轴 ∝ 1/√λ —— 谱定理的几何可视化.
""")
