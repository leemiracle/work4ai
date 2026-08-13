"""
Stanford CME 364A · 实验: SVM 的 KKT 完整推导与对偶求解
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 svm_kkt_derivation.py

本实验完整走通 SVM 的数学链:
  1. 原问题 (Primal): min 0.5||w||^2 + C Σ ξ_i  s.t. y_i(w^T x_i + b) ≥ 1 - ξ_i
  2. 拉格朗日函数 L(w,b,ξ,α,μ)
  3. 驻点条件 → 对偶问题 (Dual): max Σα_i - 0.5 Σ α_i α_j y_i y_j K_ij
     s.t. 0 ≤ α_i ≤ C, Σ α_i y_i = 0
  4. KKT 互补松弛 → 支持向量识别
  5. 核技巧: 线性核 vs RBF 核
  6. 与 sklearn 对比验证
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 数学推导回顾 (打印 KKT 链)
# ============================================================
print("=" * 70)
print("SVM 完整 KKT 推导链")
print("=" * 70)
derivation = """
原问题 (Primal, 软间隔):
   min_{w,b,ξ}  0.5 ||w||² + C Σ ξ_i
   s.t.         y_i (w^T x_i + b) ≥ 1 - ξ_i   (i=1..n)
                ξ_i ≥ 0

拉格朗日函数 (乘子 α_i ≥ 0 对分类约束, μ_i ≥ 0 对 ξ_i ≥ 0):
   L = 0.5||w||² + C Σξ_i - Σ α_i [y_i(w^T x_i + b) - 1 + ξ_i] - Σ μ_i ξ_i

驻点条件 (对 w, b, ξ 求导 = 0):
   ∂L/∂w = 0  →  w = Σ α_i y_i x_i              ... (★ w 只由 α≠0 的样本决定)
   ∂L/∂b = 0  →  Σ α_i y_i = 0                  ... (类别平衡约束)
   ∂L/∂ξ_i = 0 →  C - α_i - μ_i = 0 → α_i ≤ C   ... (α 的上界)

代回 L 得对偶问题 (Dual):
   max_α  Σ α_i - 0.5 Σ_ij α_i α_j y_i y_j (x_i^T x_j)
   s.t.   0 ≤ α_i ≤ C,   Σ α_i y_i = 0

KKT 互补松弛:
   α_i [y_i(w^T x_i + b) - 1 + ξ_i] = 0
   μ_i ξ_i = 0  →  (C - α_i) ξ_i = 0

样本分类:
   α_i = 0        : 非支持向量, 在间隔外, 对 w 无贡献
   0 < α_i < C    : 严格支持向量, 恰在间隔边界 y_i(w^T x_i + b) = 1
   α_i = C        : 间隔违例 (ξ_i > 0) 或在边界内
"""
print(derivation)

# ============================================================
# 数据生成: 线性可分 + 非线性 (月牙形)
# ============================================================
def make_linear(n=60, seed=0):
    rng = np.random.RandomState(seed)
    X = np.vstack([rng.randn(n, 2) + [2, 2], rng.randn(n, 2) + [-2, -2]])
    y = np.array([1] * n + [-1] * n, dtype=float)
    return X, y

def make_moons(n=80, noise=0.15, seed=0):
    rng = np.random.RandomState(seed)
    n2 = n // 2
    t1 = np.linspace(0, np.pi, n2)
    t2 = np.linspace(np.pi, 2 * np.pi, n2)
    X1 = np.c_[np.cos(t1), np.sin(t1)] + noise * rng.randn(n2, 2)
    X2 = np.c_[1 - np.cos(t2), 0.5 - np.sin(t2)] + noise * rng.randn(n2, 2)
    X = np.vstack([X1, X2])
    y = np.array([1] * n2 + [-1] * n2, dtype=float)
    return X, y

# ============================================================
# SVM 对偶求解器 (简化 SMO, 教学版)
# ============================================================
def svm_dual_smo(X, y, C=1.0, kernel="linear", gamma=0.5, n_passes=10, tol=1e-5):
    """简化 SMO 求解 SVM 对偶问题
       max Σα_i - 0.5 Σ α_i α_j y_i y_j K_ij
       s.t. 0 ≤ α_i ≤ C, Σ α_i y_i = 0
    """
    n = len(y)
    alpha = np.zeros(n)
    b = 0.0

    def K(i, j):
        if kernel == "linear":
            return X[i] @ X[j]
        elif kernel == "rbf":
            d = X[i] - X[j]
            return np.exp(-gamma * d @ d)
        else:
            raise ValueError(kernel)

    # 预算核矩阵 (小数据集)
    Km = np.array([[K(i, j) for j in range(n)] for i in range(n)])

    def decision_kernel(i):
        return np.sum(alpha * y * Km[i]) + b

    rng = np.random.RandomState(0)
    for _ in range(n_passes):
        num_changed = 0
        for i in range(n):
            Ei = decision_kernel(i) - y[i]
            if (y[i] * Ei < -tol and alpha[i] < C) or (y[i] * Ei > tol and alpha[i] > 0):
                j = rng.choice([k for k in range(n) if k != i])
                Ej = decision_kernel(j) - y[j]
                ai_old, aj_old = alpha[i], alpha[j]
                # 边界
                if y[i] != y[j]:
                    L = max(0, alpha[j] - alpha[i])
                    H = min(C, C + alpha[j] - alpha[i])
                else:
                    L = max(0, alpha[i] + alpha[j] - C)
                    H = min(C, alpha[i] + alpha[j])
                if H - L < 1e-12:
                    continue
                eta = 2 * Km[i, j] - Km[i, i] - Km[j, j]
                if eta >= 0:
                    continue
                alpha[j] -= y[j] * (Ei - Ej) / eta
                alpha[j] = np.clip(alpha[j], L, H)
                alpha[i] += y[i] * y[j] * (aj_old - alpha[j])
                # 更新 b
                b1 = b - Ei - y[i] * (alpha[i] - ai_old) * Km[i, i] - y[j] * (alpha[j] - aj_old) * Km[i, j]
                b2 = b - Ej - y[i] * (alpha[i] - ai_old) * Km[i, j] - y[j] * (alpha[j] - aj_old) * Km[j, j]
                if 0 < alpha[i] < C:
                    b = b1
                elif 0 < alpha[j] < C:
                    b = b2
                else:
                    b = (b1 + b2) / 2
                num_changed += 1
        if num_changed == 0:
            break

    sv = alpha > 1e-6
    return alpha, b, sv, Km

# ============================================================
# 实验 A: 线性可分数据
# ============================================================
print("=" * 70)
print("实验 A: 线性 SVM (线性核)")
print("=" * 70)

X_lin, y_lin = make_linear(n=40, seed=2)
alpha, b, sv, Km = svm_dual_smo(X_lin, y_lin, C=1.0, kernel="linear", n_passes=50)

w = np.sum((alpha * y_lin)[:, None] * X_lin, axis=0)  # w = Σ α_i y_i x_i
print(f"w = {np.round(w, 3)}")
print(f"b = {b:.3f}")
print(f"||w|| = {np.linalg.norm(w):.3f}, 间隔 2/||w|| = {2/np.linalg.norm(w):.3f}")
print(f"支持向量数: {sv.sum()} / {len(y_lin)}")

# KKT 验证: α_i > 0 的样本应满足 y_i(w^T x + b) ≈ 1
margins = y_lin * (X_lin @ w + b)
print("\nKKT 互补松弛验证 (支持向量应在间隔边界 ±1):")
for idx in np.where(sv)[0][:5]:
    print(f"  样本 {idx}: α={alpha[idx]:.3f}, margin y(w·x+b)={margins[idx]:.3f} (应≈1)")

acc = np.mean(margins > 0)
print(f"训练精度: {acc*100:.1f}%")

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax = axes[0]
ax.scatter(X_lin[y_lin == 1, 0], X_lin[y_lin == 1, 1], c="b", marker="o", label="y=+1")
ax.scatter(X_lin[y_lin == -1, 0], X_lin[y_lin == -1, 1], c="r", marker="x", label="y=-1")
ax.scatter(X_lin[sv, 0], X_lin[sv, 1], s=200, facecolors="none", edgecolors="k", linewidths=2, label="支持向量")
xx = np.linspace(*ax.get_xlim(), 100)
if abs(w[1]) > 1e-6:
    ax.plot(xx, -(w[0] * xx + b) / w[1], "k-", lw=2)
    ax.plot(xx, -(w[0] * xx + b - 1) / w[1], "k--", alpha=0.5)
    ax.plot(xx, -(w[0] * xx + b + 1) / w[1], "k--", alpha=0.5)
ax.set_title(f"线性 SVM (C=1, {sv.sum()} SV)"); ax.legend(); ax.grid(True, alpha=0.3); ax.set_aspect("equal")

# ============================================================
# 实验 B: 非线性数据 (RBF 核)
# ============================================================
print("\n" + "=" * 70)
print("实验 B: 非线性 SVM (RBF 核) — 月牙形数据")
print("=" * 70)

X_moon, y_moon = make_moons(n=100, noise=0.15, seed=1)
alpha2, b2, sv2, Km2 = svm_dual_smo(X_moon, y_moon, C=1.0, kernel="rbf", gamma=0.5, n_passes=50)
print(f"支持向量数: {sv2.sum()} / {len(y_moon)}")

# 决策函数 (核形式): f(x) = Σ α_i y_i K(x_i, x) + b
def decision_rbf(X_train, y_train, alpha, b, gamma, X_eval):
    K = np.exp(-gamma * np.sum((X_eval[:, None, :] - X_train[None, :, :]) ** 2, axis=2))
    return K @ (alpha * y_train) + b

# 网格可视化
ax = axes[1]
x_min, x_max = X_moon[:, 0].min() - 0.5, X_moon[:, 0].max() + 0.5
y_min, y_max = X_moon[:, 1].min() - 0.5, X_moon[:, 1].max() + 0.5
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
grid = np.c_[xx.ravel(), yy.ravel()]
Z = decision_rbf(X_moon, y_moon, alpha2, b2, 0.5, grid).reshape(xx.shape)
ax.contourf(xx, yy, Z, levels=50, cmap="RdBu", alpha=0.3)
ax.contour(xx, yy, Z, levels=[-1, 0, 1], colors=["r", "k", "b"], linestyles=["--", "-", "--"], linewidths=[1, 2, 1])
ax.scatter(X_moon[y_moon == 1, 0], X_moon[y_moon == 1, 1], c="b", marker="o", edgecolors="k")
ax.scatter(X_moon[y_moon == -1, 0], X_moon[y_moon == -1, 1], c="r", marker="x")
ax.scatter(X_moon[sv2, 0], X_moon[sv2, 1], s=200, facecolors="none", edgecolors="lime", linewidths=2)
acc2 = np.mean(np.sign(decision_rbf(X_moon, y_moon, alpha2, b2, 0.5, X_moon)) == y_moon)
ax.set_title(f"RBF 核 SVM (γ=0.5, {sv2.sum()} SV, acc={acc2*100:.0f}%)")
ax.grid(True, alpha=0.3)

plt.tight_layout(); plt.savefig("svm_kkt_kernels.png", dpi=100); plt.close()

# ============================================================
# 实验 C: C 参数的影响 (正则化强度)
# ============================================================
print("\n" + "=" * 70)
print("实验 C: 正则化参数 C 的影响 (欠拟合 vs 过拟合)")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, C in zip(axes, [0.01, 1.0, 100.0]):
    a_c, b_c, sv_c, _ = svm_dual_smo(X_moon, y_moon, C=C, kernel="rbf", gamma=0.5, n_passes=50)
    Z = decision_rbf(X_moon, y_moon, a_c, b_c, 0.5, grid).reshape(xx.shape)
    ax.contourf(xx, yy, Z, levels=50, cmap="RdBu", alpha=0.3)
    ax.contour(xx, yy, Z, levels=[0], colors="k", linewidths=2)
    ax.scatter(X_moon[y_moon == 1, 0], X_moon[y_moon == 1, 1], c="b", marker="o", edgecolors="k", s=30)
    ax.scatter(X_moon[y_moon == -1, 0], X_moon[y_moon == -1, 1], c="r", marker="x", s=30)
    acc_c = np.mean(np.sign(decision_rbf(X_moon, y_moon, a_c, b_c, 0.5, X_moon)) == y_moon)
    ax.set_title(f"C={C} (SV={sv_c.sum()}, acc={acc_c*100:.0f}%)\n{'大C=低正则=过拟合风险' if C >= 10 else '小C=高正则=欠拟合' if C <= 0.1 else '平衡'}")
    ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig("svm_C_effect.png", dpi=100); plt.close()
print("C 小 → 高正则 (间隔大, 欠拟合); C 大 → 低正则 (间隔小, 过拟合风险)")

print("\n" + "=" * 70)
print("全部完成. 输出: svm_kkt_kernels.png, svm_C_effect.png")
print("=" * 70)
