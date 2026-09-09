"""矩阵谱理论：特征值分解与数值算法
================================
数学概念：谱定理 / 特征值分解 / Schur分解 / 幂法 / QR算法 / Jordan标准型
应用领域：振动分析 / 量子力学 / PageRank / 主成分分析 / 稳定性分析
核心思想：矩阵的"谱"（特征值集合）揭示其本质行为。
  谱定理：对称矩阵 A = QΛQ^T（正交对角化）
  幂法：反复乘 A，收敛到最大|λ|的特征向量
  QR算法：A=QR → A'=RQ，反复迭代收敛到上三角（特征值在对角线）
  谱半径 ρ(A) = max|λᵢ|（决定矩阵幂的收敛/发散）
  条件数 κ = σ_max/σ_min（决定数值稳定性）
运行方式：python "31-矩阵谱理论.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def power_iteration(A, n_iter=100):
    """幂法：求最大|λ|的特征对。"""
    n = A.shape[0]
    v = np.random.randn(n); v /= np.linalg.norm(v)
    eigenvalues = []
    for _ in range(n_iter):
        w = A @ v
        lam = v @ w  # Rayleigh 商
        v = w / np.linalg.norm(w)
        eigenvalues.append(lam)
    return lam, v, eigenvalues

def qr_algorithm(A, n_iter=100):
    """QR算法：求所有特征值。A=QR → A'=RQ → 重复收敛到上三角。"""
    Ak = A.copy()
    for _ in range(n_iter):
        Q, R = np.linalg.qr(Ak)
        Ak = R @ Q
    return np.diag(Ak)

def main():
    np.random.seed(42)
    n = 6
    print("="*60); print("实验 1：谱定理——对称矩阵的正交对角化"); print("="*60)
    # 构造对称矩阵 A = QΛQ^T
    Lambda_true = np.diag([5, 3, 1, -1, -3, -5])
    Q_orth = np.linalg.qr(np.random.randn(n, n))[0]
    A_sym = Q_orth @ Lambda_true @ Q_orth.T
    eigvals_sym = np.linalg.eigvalsh(A_sym)
    print(f"真实特征值: {np.sort(np.diag(Lambda_true))[::-1]}")
    print(f"计算特征值: {np.sort(eigvals_sym)[::-1]}")
    print(f"对称性检查: ||A-A^T|| = {np.linalg.norm(A_sym - A_sym.T):.2e}")
    print(f"\n[解读] 对称矩阵的特征值全是实数，特征向量正交。")
    print(f"       A = QΛQ^T → A^k = QΛ^kQ^T（幂的简单计算）。")

    print("\n"+"="*60); print("实验 2：幂法——求最大特征值"); print("="*60)
    lam_power, v_power, convergence = power_iteration(A_sym, 100)
    print(f"幂法收敛值: {lam_power:.6f}（真实最大=5.0）")
    print(f"迭代过程: {[f'{c:.3f}' for c in convergence[:5]]}... → {convergence[-1]:.6f}")
    conv_rate = abs(convergence[-1] - 5.0) / abs(convergence[0] - 5.0) if abs(convergence[0] - 5.0) > 0 else 0
    print(f"收敛速度取决于 |λ₂/λ₁| = |3/5| = 0.6（线性收敛）")

    print("\n"+"="*60); print("实验 3：QR算法——求所有特征值"); print("="*60)
    eigvals_qr = qr_algorithm(A_sym, 200)
    print(f"QR算法特征值: {np.sort(eigvals_qr)[::-1].round(4)}")
    print(f"真实特征值:   {np.sort(np.diag(Lambda_true))[::-1]}")
    print(f"匹配 {'✓' if np.allclose(np.sort(eigvals_qr), np.sort(np.diag(Lambda_true)), atol=1e-6) else '✗'}")

    print("\n"+"="*60); print("实验 4：谱半径与稳定性"); print("="*60)
    print("动力系统 x_{n+1} = Ax_n 的稳定性取决于谱半径 ρ(A):")
    for name, matrix in [
        ("稳定 ρ<1", np.array([[0.5, 0.1],[0, 0.3]])),
        ("临界 ρ=1", np.array([[1.0, 0],[0, 0.5]])),
        ("不稳定 ρ>1", np.array([[1.2, 0.1],[0, 1.1]]))]:
        eigs = np.linalg.eigvals(matrix)
        rho = np.max(np.abs(eigs))
        x = np.array([1.0, 1.0])
        trajectory = [np.linalg.norm(x)]
        for _ in range(20): x = matrix @ x; trajectory.append(np.linalg.norm(x))
        print(f"  {name}: ρ={rho:.2f}, 20步后||x||={trajectory[-1]:.2e} {'(→∞)' if trajectory[-1]>1e3 else '(→0)' if trajectory[-1]<1e-3 else '(有界)'}")

    print("\n"+"="*60); print("实验 5：条件数——矩阵的数值敏感度"); print("="*60)
    print(f"{'矩阵类型':<18} {'κ(A)':<12} {'||Δx||/||x||':<15} {'解读'}")
    print("-" * 60)
    for name, M in [("正交矩阵", Q_orth),
                     ("对称良态", A_sym),
                     ("Hilbert(病态)", np.array([[1/(i+j+1) for j in range(6)] for i in range(6)]))]:
        kappa = np.linalg.cond(M)
        b = M @ np.ones(n)
        b_perturbed = b + 1e-8 * np.random.randn(n)
        x_exact = np.linalg.solve(M, b)
        x_perturbed = np.linalg.solve(M, b_perturbed)
        rel_err = np.linalg.norm(x_perturbed - x_exact) / np.linalg.norm(x_exact)
        print(f"  {name:<16} {kappa:<12.1e} {rel_err:<15.2e} {'稳定' if kappa<100 else '中等' if kappa<1e6 else '病态!'}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    ax = axes[0,0]
    ax.plot(range(len(convergence)), convergence, 'b.-', lw=1.5)
    ax.axhline(5.0, color='red', ls='--', label='真实 λ₁=5')
    ax.set_xlabel('迭代步'); ax.set_ylabel('Rayleigh商')
    ax.set_title('幂法收敛到最大特征值'); ax.legend(); ax.grid(alpha=0.3)
    # 特征值在复平面
    ax = axes[0,1]
    for name, M in [("对称(实数)", A_sym), ("非对称(可能复数)", Q_orth @ np.array([[2,-1],[0,0.5,0,0,0],[0,0,1,0,0,0],[0,0,0,-1,0,0],[0,0,0,0,3,0],[0,0,0,0,0,-2]]) @ Q_orth.T if False else np.random.randn(n,n))]:
        eigs = np.linalg.eigvals(M)
        ax.scatter(eigs.real, eigs.imag, s=80, label=name)
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.set_xlabel('Re(λ)'); ax.set_ylabel('Im(λ)')
    ax.set_title('复平面上的特征值分布'); ax.legend(); ax.grid(alpha=0.3); ax.set_aspect('equal')
    # 谱半径稳定性
    ax = axes[1,0]
    for rho_target, color in [(0.5,'green'), (1.0,'orange'), (1.5,'red')]:
        M = np.array([[rho_target, 0.1],[0, rho_target*0.8]])
        x = np.array([1.0, 0.5]); traj = [np.linalg.norm(x)]
        for _ in range(30): x = M @ x; traj.append(np.linalg.norm(x))
        ax.semilogy(traj, color=color, lw=2, label=f'ρ={rho_target}')
    ax.axhline(1, color='gray', ls='--', alpha=0.5)
    ax.set_xlabel('迭代步'); ax.set_ylabel('||x||（对数）')
    ax.set_title('谱半径决定稳定性'); ax.legend(); ax.grid(alpha=0.3)
    # 条件数
    ax = axes[1,1]
    sizes = range(3, 12)
    kappa_hilbert = [np.linalg.cond(np.array([[1/(i+j+1) for j in range(s)] for i in range(s)])) for s in sizes]
    kappa_random = [np.linalg.cond(np.random.randn(s, s)) for s in sizes]
    ax.semilogy(sizes, kappa_hilbert, 'rs-', lw=2, markersize=6, label='Hilbert矩阵(病态)')
    ax.semilogy(sizes, kappa_random, 'bo-', lw=2, markersize=6, label='随机矩阵(良态)')
    ax.axhline(1e16, color='red', ls='--', alpha=0.5, label='float64极限')
    ax.set_xlabel('矩阵大小 n'); ax.set_ylabel('条件数 κ（对数）')
    ax.set_title('条件数 vs 矩阵大小'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("31-矩阵谱理论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 31-矩阵谱理论_结果.png")
    print("\n[总结] 1. 谱定理:对称矩阵=QΛQ^T(正交对角化)")
    print("2. 幂法:O(n²/iter)求最大特征值(PageRank的基础)")
    print("3. QR算法:O(n³/iter)求所有特征值(标准方法)")
    print("4. 谱半径ρ(A)<1=稳定; Hilbert矩阵=病态经典例")

if __name__ == "__main__": main()
