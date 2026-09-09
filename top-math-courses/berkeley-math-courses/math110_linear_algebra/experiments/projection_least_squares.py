"""
Berkeley MATH 110 · 实验02: 正交投影与最小二乘 (Axler Ch 6-7)
依赖: numpy, matplotlib
运行: python3 projection_least_squares.py

验证 Axler 投影理论:
  1. 正交投影算子 P 满足 P² = P = P* (幂等 + 自伴)
  2. 最小二乘 = 投影到列空间: b̂ = P_C(A) b
  3. 正交直和分解 V = U ⊕ U⊥ (Axler 6.29)
  4. QR 分解 = Gram-Schmidt 的矩阵化 (Axler 6.31)
  5. 投影的几何可视化
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(23)

# ============================================================
# 实验 1: 正交投影算子的代数性质 P² = P = P*
# ============================================================
print("=" * 60)
print("实验 1: 正交投影算子的性质 (Axler 7.52b)")
print("=" * 60)

# 在 ℝ³ 中, 投影到由 u1, u2 张成的平面
u1 = np.array([1, 0, 1]) / np.sqrt(2)
u2 = np.array([0, 1, 0])
U = np.column_stack([u1, u2])  # 3×2, 列标准正交
P = U @ U.T  # 正交投影矩阵 (到 U 的列空间)
print(f"P² = P? {np.allclose(P @ P, P)}")        # 幂等
print(f"P = Pᵀ? {np.allclose(P, P.T)}")          # 自伴
print(f"P 的特征值 (应为 0 和 1): {np.round(np.linalg.eigvalsh(P), 4)}")
print("  → 投影的特征值只有 0(被压扁) 和 1(保留), 这就是 P²=P 的谱解释")

# ============================================================
# 实验 2: 最小二乘 = 投影到列空间
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 最小二乘法 = 正交投影 (Axler 6.55)")
print("=" * 60)

# 超定系统 Ax ≈ b (3 个点拟合直线)
A = np.array([[1, 0], [1, 1], [1, 2]], dtype=float)
b = np.array([1.1, 2.9, 5.2])

# 投影矩阵到 C(A): P = A(AᵀA)⁻¹Aᵀ
P_A = A @ np.linalg.inv(A.T @ A) @ A.T
b_hat = P_A @ b  # b 在列空间的投影 = 最佳拟合
residual = b - b_hat  # 残差 ⊥ C(A)

print(f"原始 b: {b}")
print(f"投影 b̂ = P_C(A) b: {np.round(b_hat, 4)}")
print(f"残差 b - b̂: {np.round(residual, 4)}")
# 验证残差 ⊥ 列空间 (Axler: b-b̂ ∈ N(Aᵀ) = C(A)⊥)
print(f"残差 ⊥ A 的列? {np.allclose(A.T @ residual, 0)}")

# 最小二乘解
x_hat = np.linalg.solve(A.T @ A, A.T @ b)
print(f"最小二乘解 x̂ = (AᵀA)⁻¹Aᵀb = {np.round(x_hat, 4)}  (直线 y = {x_hat[0]:.3f} + {x_hat[1]:.3f}t)")

# ============================================================
# 实验 3: 正交直和分解 V = U ⊕ U⊥
# ============================================================
print("\n" + "=" * 60)
print("实验 3: 正交直和分解 ℝⁿ = U ⊕ U⊥ (Axler 6.29)")
print("=" * 60)

# 任意向量 v 唯一分解 v = u + w, u ∈ U, w ∈ U⊥
v = np.array([3, 4, 5])
u_proj = P @ v         # U 分量
w_proj = v - u_proj    # U⊥ 分量
print(f"v = {v}")
print(f"u = P_U v = {np.round(u_proj, 4)}  (∈ U)")
print(f"w = v - u = {np.round(w_proj, 4)}  (∈ U⊥)")
print(f"u ⊥ w? {np.allclose(u_proj @ w_proj, 0)}")          # 正交
print(f"u + w = v? {np.allclose(u_proj + w_proj, v)}")       # 完整分解

# ============================================================
# 实验 4: QR = Gram-Schmidt 矩阵化
# ============================================================
print("\n" + "=" * 60)
print("实验 4: QR 分解 = Gram-Schmidt (Axler 6.31)")
print("=" * 60)

A4 = np.array([[1, 1, 1], [1, 0, 2], [0, 1, 3], [0, 0, 1]], dtype=float)
Q4, R4 = np.linalg.qr(A4)
print(f"A 的形状: {A4.shape}")
print(f"Q 正交? {np.allclose(Q4 @ Q4.T, np.eye(4))}")
print(f"R 上三角? {np.allclose(R4, np.triu(R4))}")
print(f"QR = A? {np.allclose(Q4 @ R4, A4)}")
# Axler: Q 的列 = Gram-Schmidt 得到的标准正交基

# ============================================================
# 实验 5: 可视化 —— 投影的几何
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 投影几何可视化")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

# 左: 2D 投影 (向量到直线)
ax = axes[0]
a = np.array([2, 1])
b2 = np.array([1, 3])
p = (a @ b2) / (a @ a) * a  # b 在 a 上的投影
ax.annotate("", xy=a, xytext=(0,0), arrowprops=dict(arrowstyle="->", color="steelblue", lw=2))
ax.annotate("", xy=b2, xytext=(0,0), arrowprops=dict(arrowstyle="->", color="gray", lw=2))
ax.annotate("", xy=p, xytext=(0,0), arrowprops=dict(arrowstyle="->", color="crimson", lw=2.5))
ax.plot([b2[0], p[0]], [b2[1], p[1]], "k--", label="残差 (⊥ a)")
ax.text(a[0]+0.1, a[1]+0.1, "a (子空间方向)", color="steelblue")
ax.text(b2[0]+0.1, b2[1]+0.1, "b (目标)", color="gray")
ax.text(p[0]+0.1, p[1]-0.3, f"P_a b (投影)", color="crimson")
ax.set_xlim(-0.5, 3); ax.set_ylim(-0.5, 4); ax.set_aspect("equal")
ax.axhline(0, color="gray", lw=0.5); ax.axvline(0, color="gray", lw=0.5)
ax.legend(); ax.grid(True, alpha=0.3)
ax.set_title("向量到子空间(直线)的投影\nP_a b = (a·b/a·a) a")

# 右: 最小二乘拟合
ax = axes[1]
t = np.array([0, 1, 2])
b_data = b
ax.scatter(t, b_data, s=80, color="crimson", zorder=5, label="观测点 b")
t_fit = np.linspace(-0.3, 2.3, 100)
y_fit = x_hat[0] + x_hat[1] * t_fit
ax.plot(t_fit, y_fit, "steelblue", lw=2, label=f"拟合 y={x_hat[0]:.2f}+{x_hat[1]:.2f}t")
b_fit = x_hat[0] + x_hat[1] * t
for i in range(3):
    ax.plot([t[i], t[i]], [b_data[i], b_fit[i]], "k--", alpha=0.6)
ax.scatter(t, b_fit, s=60, color="steelblue", marker="x", zorder=5, label="投影 b̂ ∈ C(A)")
ax.set_xlim(-0.3, 2.3); ax.legend(); ax.grid(True, alpha=0.3)
ax.set_title("最小二乘 = 投影到列空间\n虚线 = 残差 (⊥ C(A))")

plt.suptitle("Axler 投影理论: P²=P=P* → 最小二乘 → 线性回归", fontsize=13)
plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"图表已保存: {__file__.replace('.py', '.png')}")

print("\n核心结论:")
print("  Axler 的正交投影 P (P²=P=P*) 是最小二乘、线性回归、PCA 的统一数学骨架.")
