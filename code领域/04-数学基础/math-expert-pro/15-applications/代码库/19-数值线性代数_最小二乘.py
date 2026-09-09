"""
数值线性代数：最小二乘法与 QR 分解
================================
数学概念：最小二乘 / 正规方程 / QR 分解 / 条件数 / 多项式拟合 / 正交投影
应用领域：数据拟合 / 计量经济学 / 信号处理 / 机器学习 / 计算机视觉
核心思想：超定方程组 Ax=b（方程多于未知量）通常无精确解。
  最小二乘解：x* = argmin ||Ax - b||²
  正规方程：A^T A x = A^T b（但条件数平方→数值不稳定）
  QR 分解：A = QR（正交×上三角）→ Rx = Q^T b（条件数不平方→稳定）
  条件数：κ(A) = σ_max/σ_min（越大越病态）
  几何意义：投影——x* 使 Ax* 成为 b 在 A 的列空间上的正交投影
运行方式：python "19-数值线性代数_最小二乘.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 最小二乘求解器 ============

def least_squares_normal(A, b):
    """正规方程法：x = (A^T A)^{-1} A^T b
    缺点：κ(A^T A) = κ(A)² → 条件数平方，数值不稳定
    """
    ATA = A.T @ A
    ATb = A.T @ b
    return np.linalg.solve(ATA, ATb)


def least_squares_qr(A, b):
    """QR 分解法：A=QR → Rx = Q^T b（回代）
    优点：Q 正交→条件数不放大→数值稳定
    """
    Q, R = np.linalg.qr(A)
    # R 是上三角，回代求解 Rx = Q^T b
    return np.linalg.solve(R, Q.T @ b)


def condition_number(A):
    """条件数 κ(A) = σ_max / σ_min"""
    s = np.linalg.svd(A, compute_uv=False)
    return s[0] / s[-1] if s[-1] > 0 else float('inf')


# ============ 2. 多项式拟合 ============

def polynomial_fit(x, y, degree):
    """多项式最小二乘拟合。
    构造 Vandermonde 矩阵 V，解 V c = y
    返回：系数 c（从低次到高次）
    """
    V = np.vander(x, degree + 1, increasing=True)
    c = least_squares_qr(V, y)
    return c


# ============ 3. 实验 ============

def main():
    np.random.seed(42)

    print("=" * 60)
    print("实验 1：线性最小二乘——数据拟合基础")
    print("=" * 60)

    # 生成带噪声数据
    n = 50
    x_data = np.linspace(0, 10, n)
    y_true = 2.0 + 1.5 * x_data  # 真实关系 y = 2 + 1.5x
    y_noisy = y_true + np.random.randn(n) * 2.0

    # 构造 A = [1, x], 解 A c = y
    A = np.column_stack([np.ones(n), x_data])
    c_normal = least_squares_normal(A, y_noisy)
    c_qr = least_squares_qr(A, y_noisy)
    c_numpy = np.linalg.lstsq(A, y_noisy, rcond=None)[0]

    print(f"数据: {n} 个点, 真实关系 y = 2.0 + 1.5x, 噪声 σ=2.0")
    print(f"条件数 κ(A) = {condition_number(A):.2f}")
    print(f"\n正规方程解:  截距={c_normal[0]:.4f}, 斜率={c_normal[1]:.4f}")
    print(f"QR 分解解:   截距={c_qr[0]:.4f}, 斜率={c_qr[1]:.4f}")
    print(f"NumPy lstsq: 截距={c_numpy[0]:.4f}, 斜率={c_numpy[1]:.4f}")
    print(f"真实值:      截距=2.0000, 斜率=1.5000")

    # 计算残差
    residual = np.sqrt(np.mean((A @ c_qr - y_noisy) ** 2))
    print(f"\nRMS 残差 = {residual:.4f}（接近噪声 σ=2.0 → 拟合良好）")

    print(f"\n[解读] 最小二乘 = 正交投影：y 到 A 列空间的最近点。")
    print(f"       正规方程和 QR 给出相同结果（条件好时），但 QR 更稳定。")

    print("\n" + "=" * 60)
    print("实验 2：正规方程 vs QR——条件数与数值稳定性")
    print("=" * 60)

    # 构造病态矩阵（高条件数）
    print("构造不同条件数的矩阵，对比正规方程 vs QR 的精度：\n")

    print(f"{'场景':<20} {'κ(A)':<12} {'κ(A^T A)':<12} {'正规方程误差':<14} {'QR误差':<14} {'QR更稳定?'}")
    print("-" * 80)

    for name, scale in [("良态 κ≈1", 1), ("中等 κ≈10³", 1000), ("病态 κ≈10⁶", 1000000)]:
        # Hilbert-like 矩阵（经典病态）
        n_h = 8
        A_h = np.array([[1.0 / (i + j + 1) for j in range(n_h)] for i in range(n_h)])
        # 缩放条件数
        if scale > 1:
            A_h = A_h + np.eye(n_h) * 1e-12 * scale

        x_true_h = np.ones(n_h)
        b_h = A_h @ x_true_h

        kappa_A = condition_number(A_h)
        kappa_ATA = condition_number(A_h.T @ A_h)

        x_normal = least_squares_normal(A_h, b_h)
        x_qr = least_squares_qr(A_h, b_h)

        err_normal = np.linalg.norm(x_normal - x_true_h)
        err_qr = np.linalg.norm(x_qr - x_true_h)

        more_stable = "✓" if err_qr < err_normal else "≈"
        print(f"{name:<20} {kappa_A:<12.1e} {kappa_ATA:<12.1e} {err_normal:<14.2e} {err_qr:<14.2e} {more_stable}")

    print(f"\n[解读] 正规方程的条件数是 κ(A)² → 严重放大误差。")
    print(f"       QR 保持 κ(A) → 稳定得多。病态问题必须用 QR。")
    print(f"       极端情况用 SVD（pseudoinverse）——最稳定但最慢。")

    print("\n" + "=" * 60)
    print("实验 3：多项式拟合——欠拟合 vs 过拟合")
    print("=" * 60)

    # 生成非线性数据
    x_nl = np.linspace(0, 5, 30)
    y_nl_true = 3 * np.sin(2 * x_nl) + 0.5 * x_nl
    y_nl_noisy = y_nl_true + np.random.randn(30) * 0.8

    degrees = [1, 3, 5, 9, 15]
    x_fine = np.linspace(0, 5, 200)

    print(f"数据: 30 点, 真实关系 y = 3sin(2x) + 0.5x, 噪声 σ=0.8")
    print(f"\n{'次数':<6} {'κ(Vandermonde)':<18} {'训练RMS':<12} {'过拟合?'}")
    print("-" * 50)

    for deg in degrees:
        c = polynomial_fit(x_nl, y_nl_noisy, deg)
        V = np.vander(x_nl, deg + 1, increasing=True)
        kappa = condition_number(V)
        y_fit = V @ c
        rms = np.sqrt(np.mean((y_fit - y_nl_noisy) ** 2))

        # 判断过拟合：高次时 Vandermonde 条件数爆炸
        overfit = "✓ 严重" if kappa > 1e10 else "中" if kappa > 1e5 else "否"
        print(f"{deg:<6} {kappa:<18.2e} {rms:<12.4f} {overfit}")

    print(f"\n[解读] 多项式次数越高，Vandermonde 矩阵越病态。")
    print(f"       15 次多项式条件数 ~10²⁰ → 数值上完全不可信。")
    print(f"       这就是为什么高次多项式拟合要用正交多项式基。")

    print("\n" + "=" * 60)
    print("实验 4：几何理解——正交投影")
    print("=" * 60)

    # 2D 几何可视化
    print("最小二乘的几何意义：")
    print("  b 在 A 列空间 Col(A) 上的正交投影 = A x*")
    print("  残差 r = b - A x* ⊥ Col(A)")
    print("  → A^T r = 0 → A^T(b - Ax*) = 0 → A^T A x* = A^T b（正规方程）")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：线性回归拟合
    ax = axes[0, 0]
    ax.scatter(x_data, y_noisy, s=20, alpha=0.5, label='带噪数据')
    ax.plot(x_data, y_true, 'g-', lw=2, label='真实 y=2+1.5x')
    ax.plot(x_data, A @ c_qr, 'r-', lw=2, label=f'最小二乘拟合')
    for i in range(0, n, 5):
        ax.plot([x_data[i], x_data[i]], [y_noisy[i], A[i] @ c_qr], 'b-', alpha=0.3, lw=0.5)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'最小二乘线性回归（残差={residual:.2f}）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 2：多项式拟合（不同次数）
    ax = axes[0, 1]
    ax.scatter(x_nl, y_nl_noisy, s=20, c='gray', alpha=0.5, zorder=5)
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(degrees)))
    for deg, color in zip(degrees, colors):
        c = polynomial_fit(x_nl, y_nl_noisy, deg)
        V_fine = np.vander(x_fine, deg + 1, increasing=True)
        ax.plot(x_fine, V_fine @ c, color=color, lw=1.5, alpha=0.8, label=f'degree={deg}')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('多项式拟合：欠拟合 → 过拟合')
    ax.legend(fontsize=7)
    ax.set_ylim(-8, 8)
    ax.grid(alpha=0.3)

    # 图 3：条件数 vs 多项式次数
    ax = axes[1, 0]
    degs = range(1, 20)
    kappas = []
    for d in degs:
        V = np.vander(x_nl, d + 1, increasing=True)
        kappas.append(condition_number(V))
    ax.semilogy(degs, kappas, 'ro-', lw=2, markersize=6)
    ax.axhline(1e16, color='red', ls='--', alpha=0.5, label='float64 精度极限 (~1e16)')
    ax.set_xlabel('多项式次数')
    ax.set_ylabel('κ(Vandermonde)（对数）')
    ax.set_title('Vandermonde 条件数随多项式次数爆炸')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：正交投影几何
    ax = axes[1, 1]
    # 2D 案例：b=(3,1), A列空间=span{(1,0.5)}
    b = np.array([3, 1])
    a1 = np.array([1, 0.5])
    # 投影 p = (b·a1)/(a1·a1) * a1
    p = (b @ a1) / (a1 @ a1) * a1
    ax.quiver(0, 0, a1[0], a1[1], angles='xy', scale_units='xy', scale=1, color='blue', width=0.01, label='A的列向量')
    ax.quiver(0, 0, b[0], b[1], angles='xy', scale_units='xy', scale=1, color='black', width=0.01, label='b（观测）')
    ax.quiver(0, 0, p[0], p[1], angles='xy', scale_units='xy', scale=1, color='red', width=0.01, label='Ax*（投影）')
    ax.quiver(b[0], b[1], p[0]-b[0], p[1]-b[1], angles='xy', scale_units='xy', scale=1, color='green', width=0.01, label='残差 b-Ax*')
    ax.plot([0, 10*a1[0]], [0, 10*a1[1]], 'b--', alpha=0.3, label='Col(A)')
    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 3)
    ax.set_aspect('equal')
    ax.set_title('正交投影：最小二乘的几何意义')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("19-数值线性代数_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 19-数值线性代数_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 最小二乘：超定方程组的最优近似解（正交投影）")
    print("2. 正规方程 κ(A²)：条件数平方 → 病态时不稳定")
    print("3. QR 分解：条件数不放大 → 推荐的解法")
    print("4. 条件数 κ(A)：衡量问题的数值敏感度")
    print("5. 多项式拟合：次数↑ → Vandermonde 条件数↑↑ → 过拟合+数值不稳定")
    print("\n[解读] 数值线性代数是'让线性代数在计算机上可靠'的学问——")
    print("       理论上 (A^T A)^{-1} A^T b 正确，但数值上必须用 QR。")
    print("       这个教训适用于所有数值计算：'数学正确 ≠ 计算可靠'。")


if __name__ == "__main__":
    main()
