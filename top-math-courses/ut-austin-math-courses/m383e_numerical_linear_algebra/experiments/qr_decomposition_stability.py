"""
UT Austin M 383E · 实验: QR 分解的数值稳定性
依赖: numpy, matplotlib (纯标准库+科学计算)
运行: python3 qr_decomposition_stability.py

验证 (Trefethen & Bau 核心思想):
  1. 三种 QR 实现: 经典 GS / 修正 GS / Householder
  2. 正交性损失: ||Q^T Q - I|| (CGS 最差, Householder 最好)
  3. Hilbert 矩阵: 经典病态矩阵的条件数爆炸
  4. 最小二乘: 正规方程 (κ²) vs QR (κ) vs SVD (κ)
  5. 向后稳定性: 扰动分析 ||A - Q_hat R_hat|| ≈ ε_machine ||A||
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

np.random.seed(42)

# ============================================================
# 三种 QR 实现
# ============================================================
def qr_classical_gs(A):
    """经典 Gram-Schmidt (数值不稳定, 教学用)"""
    m, n = A.shape
    Q = np.zeros((m, n)); R = np.zeros((n, n))
    for k in range(n):
        v = A[:, k].astype(float).copy()
        for j in range(k):
            R[j, k] = Q[:, j] @ A[:, k]   # CGS: 用原始 A[:,k]
            v -= R[j, k] * Q[:, j]
        R[k, k] = np.linalg.norm(v)
        if R[k, k] < 1e-15:
            Q[:, k] = 0
        else:
            Q[:, k] = v / R[k, k]
    return Q, R

def qr_modified_gs(A):
    """修正 Gram-Schmidt (向后稳定)"""
    m, n = A.shape
    Q = np.zeros((m, n)); R = np.zeros((n, n))
    V = A.astype(float).copy()
    for k in range(n):
        R[k, k] = np.linalg.norm(V[:, k])
        if R[k, k] < 1e-15:
            Q[:, k] = 0
        else:
            Q[:, k] = V[:, k] / R[k, k]
        for j in range(k + 1, n):
            R[k, j] = Q[:, k] @ V[:, j]   # MGS: 用更新后的 V
            V[:, j] -= R[k, j] * Q[:, k]
    return Q, R

def qr_householder(A):
    """Householder QR (最稳定, 工业标准)"""
    m, n = A.shape
    R = A.astype(float).copy()
    Q = np.eye(m)
    for k in range(min(m - 1, n)):
        x = R[k:, k]
        alpha = -np.sign(x[0] or 1.0) * np.linalg.norm(x)
        v = x.copy(); v[0] -= alpha
        vnorm = np.linalg.norm(v)
        if vnorm < 1e-15:
            continue
        v = v / vnorm
        # 应用 Householder 反射到 R 和 Q
        R[k:, :] -= 2 * np.outer(v, v @ R[k:, :])
        Q[:, k:] -= 2 * np.outer(Q[:, k:] @ v, v)
    return Q, R

def orthogonality_error(Q):
    """||Q^T Q - I||_F"""
    n = Q.shape[1]
    return np.linalg.norm(Q.T @ Q - np.eye(n), "fro")

# ============================================================
# 实验 1: 三种 QR 在良态矩阵上
# ============================================================
print("=" * 60)
print("实验 1: 三种 QR 在随机良态矩阵上")
print("=" * 60)

A = np.random.randn(20, 15)
eps = np.finfo(float).eps
print(f"机器精度 ε = {eps:.2e}")

Q_cgs, R_cgs = qr_classical_gs(A)
Q_mgs, R_mgs = qr_modified_gs(A)
Q_hh, R_hh = qr_householder(A)
Q_np, R_np = np.linalg.qr(A)  # numpy 参考 (Householder)

print(f"\n正交性损失 ||Q^T Q - I||:")
print(f"  经典 GS:      {orthogonality_error(Q_cgs):.2e}")
print(f"  修正 GS:      {orthogonality_error(Q_mgs):.2e}")
print(f"  Householder:  {orthogonality_error(Q_hh):.2e}")
print(f"  numpy (参考): {orthogonality_error(Q_np):.2e}")

print(f"\n分解误差 ||A - QR||:")
print(f"  经典 GS:      {np.linalg.norm(A - Q_cgs @ R_cgs):.2e}")
print(f"  修正 GS:      {np.linalg.norm(A - Q_mgs @ R_mgs):.2e}")
print(f"  Householder:  {np.linalg.norm(A - Q_hh @ R_hh):.2e}")

# ============================================================
# 实验 2: 病态矩阵上正交性崩溃
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 病态矩阵上 CGS 正交性崩溃")
print("=" * 60)

def ill_conditioned_matrix(m, n, kappa):
    """生成条件数 ~ kappa 的矩阵 (通过缩放奇异值)"""
    U, _ = np.linalg.qr(np.random.randn(m, n))
    V, _ = np.linalg.qr(np.random.randn(n, n))
    s = np.logspace(0, -np.log10(kappa), n)
    return U * s @ V.T

kappas = [1, 1e2, 1e4, 1e6, 1e8, 1e10]
err_cgs_list, err_mgs_list, err_hh_list = [], [], []
for kappa_target in kappas:
    A = ill_conditioned_matrix(30, 20, kappa_target)
    kappa_actual = np.linalg.cond(A)
    Q_cgs, _ = qr_classical_gs(A)
    Q_mgs, _ = qr_modified_gs(A)
    Q_hh, _ = qr_householder(A)
    err_cgs_list.append(orthogonality_error(Q_cgs))
    err_mgs_list.append(orthogonality_error(Q_mgs))
    err_hh_list.append(orthogonality_error(Q_hh))

fig, ax = plt.subplots(figsize=(9, 5))
ax.loglog(kappas, err_cgs_list, "ro-", label="经典 GS (崩溃)")
ax.loglog(kappas, err_mgs_list, "bs-", label="修正 GS")
ax.loglog(kappas, err_hh_list, "g^-", label="Householder (最稳)")
ax.loglog(kappas, [eps * k for k in kappas], "k--", alpha=0.3, label="ε·κ (理论界)")
ax.set_xlabel("条件数 κ(A)"); ax.set_ylabel("正交性损失 ||Q^T Q - I||")
ax.set_title("QR 数值稳定性: CGS 在病态矩阵上正交性丢失")
ax.legend(); ax.grid(True)
plt.tight_layout(); plt.savefig("qr_stability.png", dpi=100); plt.close()
print("图保存: qr_stability.png — CGS 在 κ>1e6 时正交性完全崩溃")

# ============================================================
# 实验 3: Hilbert 矩阵 — 经典病态矩阵
# ============================================================
print("\n" + "=" * 60)
print("实验 3: Hilbert 矩阵条件数爆炸")
print("=" * 60)

def hilbert(n):
    return 1.0 / (np.arange(1, n + 1)[:, None] + np.arange(1, n + 1)[None, :] - 1)

sizes = range(2, 16)
kappas_h = [np.linalg.cond(hilbert(n)) for n in sizes]
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(sizes, kappas_h, "mo-", linewidth=2)
ax.axhline(1 / eps, color="r", linestyle="--", label=f"1/ε_machine = {1/eps:.0e}")
ax.set_xlabel("矩阵尺寸 n"); ax.set_ylabel("条件数 κ(H_n)")
ax.set_title("Hilbert 矩阵: 条件数随 n 指数爆炸 (n≥12 不可解)")
ax.legend(); ax.grid(True)
plt.tight_layout(); plt.savefig("hilbert_condition.png", dpi=100); plt.close()

for n in [5, 8, 10, 12, 15]:
    print(f"  Hilbert {n:2d}×{n:2d}: κ = {np.linalg.cond(hilbert(n)):.2e}")

# ============================================================
# 实验 4: 最小二乘 — 正规方程 vs QR vs SVD
# ============================================================
print("\n" + "=" * 60)
print("实验 4: 最小二乘三种解法对比")
print("=" * 60)

def leastsq_normal(A, b):
    """正规方程: A^T A x = A^T b (条件数平方!)"""
    return np.linalg.solve(A.T @ A, A.T @ b)

def leastsq_qr(A, b):
    """QR: R x = Q^T b"""
    Q, R = np.linalg.qr(A)
    return np.linalg.solve(R[:A.shape[1]], (Q.T @ b)[:A.shape[1]])

def leastsq_svd(A, b):
    """SVD: x = V Σ^+ U^T b"""
    return np.linalg.pinv(A) @ b

# 构造病态最小二乘问题
m, n = 50, 10
A_well = np.random.randn(m, n)
A_ill = ill_conditioned_matrix(m, n, 1e8)
x_true = np.random.randn(n)
b_well = A_well @ x_true + 1e-3 * np.random.randn(m)
b_ill = A_ill @ x_true + 1e-3 * np.random.randn(m)

print(f"良态矩阵 κ(A) = {np.linalg.cond(A_well):.2e}:")
print(f"  正规方程误差: {np.linalg.norm(leastsq_normal(A_well, b_well) - x_true):.2e}")
print(f"  QR 误差:      {np.linalg.norm(leastsq_qr(A_well, b_well) - x_true):.2e}")
print(f"  SVD 误差:     {np.linalg.norm(leastsq_svd(A_well, b_well) - x_true):.2e}")

print(f"\n病态矩阵 κ(A) = {np.linalg.cond(A_ill):.2e}:")
print(f"  正规方程误差: {np.linalg.norm(leastsq_normal(A_ill, b_ill) - x_true):.2e} (崩溃!)")
print(f"  QR 误差:      {np.linalg.norm(leastsq_qr(A_ill, b_ill) - x_true):.2e}")
print(f"  SVD 误差:     {np.linalg.norm(leastsq_svd(A_ill, b_ill) - x_true):.2e} (最稳健)")

# ============================================================
# 实验 5: 向后稳定性验证
# ============================================================
print("\n" + "=" * 60)
print("实验 5: 向后稳定性 — ||A - Q̂R̂|| ≈ ε_machine ||A||")
print("=" * 60)

A = np.random.randn(40, 30)
Q_mgs, R_mgs = qr_modified_gs(A)
Q_hh, R_hh = qr_householder(A)
norm_A = np.linalg.norm(A)
backward_err_mgs = np.linalg.norm(A - Q_mgs @ R_mgs) / norm_A
backward_err_hh = np.linalg.norm(A - Q_hh @ R_hh) / norm_A

print(f"||A|| = {norm_A:.2e}")
print(f"MGS 向后误差:        {backward_err_mgs:.2e} (应 ≈ ε = {eps:.2e})")
print(f"Householder 向后误差: {backward_err_hh:.2e} (应 ≈ ε = {eps:.2e})")
print(f"两者均向后稳定: {backward_err_mgs < 100 * eps and backward_err_hh < 100 * eps}")

# ============================================================
# 实验 6: 验证 QR 分解 = Householder 反射的几何
# ============================================================
print("\n" + "=" * 60)
print("实验 6: Householder 反射几何可视化 (2D)")
print("=" * 60)

fig, ax = plt.subplots(figsize=(7, 7))
# 向量 x, 反射到 e1 方向
x = np.array([3.0, 1.0])
alpha = -np.sign(x[0]) * np.linalg.norm(x)
v = x - alpha * np.array([1, 0])
v = v / np.linalg.norm(v)
Hx = x - 2 * (v @ x) * v

ax.quiver(0, 0, x[0], x[1], angles="xy", scale_units="xy", scale=1, color="b", label="x")
ax.quiver(0, 0, Hx[0], Hx[1], angles="xy", scale_units="xy", scale=1, color="r", label="Hx (反射后)")
# 反射镜面 (垂直于 v)
t = np.linspace(-2, 4, 100)
normal = v
# 镜面: v^T (p - x/2) = 0 → 通过 x 和 Hx 的中点
mid = (x + Hx) / 2
# 镜面方向垂直于 (x - Hx)
mirror_dir = np.array([-v[1], v[0]])
ax.plot(mid[0] + t * mirror_dir[0], mid[1] + t * mirror_dir[1], "g--", alpha=0.5, label="反射镜面")
ax.set_xlim(-1, 5); ax.set_ylim(-3, 3); ax.set_aspect("equal")
ax.axhline(0, color="k", linewidth=0.5); ax.axvline(0, color="k", linewidth=0.5)
ax.legend(); ax.grid(True, alpha=0.3)
ax.set_title("Householder 反射: Hx = x - 2(v^T x)v, 把 x 映到 e_1 轴")
plt.tight_layout(); plt.savefig("householder_geometry.png", dpi=100); plt.close()
print(f"x = {x}, Hx = {np.round(Hx, 3)} (在 e_1 轴上, |Hx| = {np.linalg.norm(Hx):.3f} = |x| = {np.linalg.norm(x):.3f})")

print("\n" + "=" * 60)
print("全部完成. 输出: qr_stability.png, hilbert_condition.png,")
print("  householder_geometry.png")
print("=" * 60)
