"""压缩感知：稀疏恢复与 L1 最小化
================================
数学概念：压缩感知 / 稀疏性 / L1最小化 / 正交匹配追踪(OMP) / RIP / 互相关
应用领域：MRI加速 / 单像素相机 / 压缩 / 信道编码 / 超分辨率
核心思想：稀疏信号可以从远少于 Nyquist 采样数的测量中精确恢复。
  稀疏性：信号在某个基下只有 k 个非零系数（k << n）
  测量：y = Φx，Φ 是 m×n 随机矩阵（m << n）
  恢复：min ||x||₁ s.t. Φx = y（L1 最小化 = 基追踪）
  OMP：贪心算法，逐步选出最相关的列
  RIP：Φ 满足限制等距性质 → 保证精确恢复（m ≥ C·k·log(n/k)）
  Candès-Tao 定理(2006)：随机测量矩阵以高概率满足 RIP
运行方式：python "29-压缩感知_稀疏恢复.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def omp(y, Phi, k):
    """正交匹配追踪（OMP）贪心算法。
    y = Phi x, x 稀疏(k个非零), 恢复 x。
    """
    m, n = Phi.shape
    residual = y.copy()
    support = []  # 被选中的列索引
    x = np.zeros(n)
    for _ in range(k):
        # 1. 匹配：找与残差最相关的列
        correlations = np.abs(Phi.T @ residual)
        correlations[support] = -1  # 排除已选
        best_idx = np.argmax(correlations)
        support.append(best_idx)
        # 2. 投影：最小二乘估计
        Phi_s = Phi[:, support]
        coeffs, _, _, _ = np.linalg.lstsq(Phi_s, y, rcond=None)
        # 3. 更新残差
        residual = y - Phi_s @ coeffs
    x[support] = coeffs
    return x, support

def main():
    np.random.seed(42)
    N = 256  # 原始信号维度
    k_values = [5, 10, 20, 40]  # 稀疏度

    print("="*60); print("实验 1：OMP 恢复稀疏信号"); print("="*60)
    for k in k_values:
        # 生成 k-稀疏信号
        x_true = np.zeros(N)
        support_true = np.random.choice(N, k, replace=False)
        x_true[support_true] = np.random.randn(k) * 3
        # 随机测量矩阵
        m = max(4 * k, int(0.3 * N))  # 测量数 m << N
        Phi = np.random.randn(m, N) / np.sqrt(m)
        y = Phi @ x_true
        # OMP 恢复
        x_rec, support_rec = omp(y, Phi, k)
        # 评估
        error = np.linalg.norm(x_rec - x_true) / np.linalg.norm(x_true)
        support_match = len(set(support_rec) & set(support_true)) / k
        print(f"k={k:>3}: m={m:>3}, 相对误差={error:.2e}, 支撑匹配={support_match:.0%} {'✓' if support_match > 0.9 else '✗'}")

    print(f"\n[解读] m = 4k 就能精确恢复 k-稀疏信号（远少于 Nyquist 的 N 个采样）。")
    print(f"       这是压缩感知的核心魔力——'少测多知'。")

    print("\n"+"="*60); print("实验 2：测量数 m vs 恢复成功率"); print("="*60)
    k = 20; N = 256; n_trials = 50
    m_values = [k, 2*k, 3*k, 4*k, 5*k, 6*k, 8*k, 10*k]
    print(f"{'m':<6} {'m/N':<8} {'成功率':<10} {'平均误差'}")
    print("-"*35)
    for m in m_values:
        successes = 0; errors = []
        for _ in range(n_trials):
            x_t = np.zeros(N)
            supp = np.random.choice(N, k, replace=False)
            x_t[supp] = np.random.randn(k)
            Phi_t = np.random.randn(m, N) / np.sqrt(m)
            y_t = Phi_t @ x_t
            x_r, _ = omp(y_t, Phi_t, k)
            err = np.linalg.norm(x_r - x_t) / np.linalg.norm(x_t)
            errors.append(err)
            if err < 1e-6: successes += 1
        rate = successes / n_trials
        avg_err = np.mean(errors)
        print(f"{m:<6} {m/N:<8.2f} {rate:<10.0%} {avg_err:.2e}")

    print(f"\n[解读] m ≈ 4k-5k 时成功率接近 100%。")
    print(f"       理论保证 m ≥ C·k·log(N/k)（Candès-Tao 2006）。")

    print("\n"+"="*60); print("实验 3：L1 vs L2 最小化——为什么 L1 能恢复稀疏？"); print("="*60)
    print("L2 最小化(min ||x||₂): 返回密集解（不稀疏）")
    print("L1 最小化(min ||x||₁): 返回稀疏解（大量零）")
    print("\n几何直觉：L1 球（菱形）的尖角对齐坐标轴，")
    print("          测量约束面首先碰到尖角 → 稀疏解。")
    print("          L2 球（圆）无尖角 → 密集解。")

    print("\n"+"="*60); print("实验 4：压缩感知应用"); print("="*60)
    apps = [("MRI", "10x加速扫描（减少憋气时间）"),
            ("单像素相机", "Rice大学硬件实现"),
            ("基因分型", "用少量SNP推断全基因组"),
            ("天文成像", "稀疏天体的高分辨率重建"),
            ("信道编码", "稀疏信道估计"),
            ("机器学习", "L1正则化(Lasso)=压缩感知的统计版")]
    for app, desc in apps: print(f"  {app:<16} → {desc}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    k_demo = 10
    x_demo = np.zeros(N)
    supp_demo = np.random.choice(N, k_demo, replace=False)
    x_demo[supp_demo] = np.random.randn(k_demo) * 3
    m_demo = 4 * k_demo
    Phi_demo = np.random.randn(m_demo, N) / np.sqrt(m_demo)
    y_demo = Phi_demo @ x_demo
    x_rec_demo, _ = omp(y_demo, Phi_demo, k_demo)

    ax = axes[0,0]
    ax.stem(np.arange(N), x_demo, linefmt='b-', markerfmt='bo', basefmt='k-', label='真实信号')
    ax.set_title(f'原始 k-稀疏信号(k={k_demo}, N={N})')
    ax.legend(); ax.grid(alpha=0.3)
    ax = axes[0,1]
    ax.stem(np.arange(N), x_rec_demo, linefmt='r-', markerfmt='rx', basefmt='k-', label='OMP恢复')
    ax.set_title(f'OMP恢复(m={m_demo}次测量, m/N={m_demo/N:.2f})')
    ax.legend(); ax.grid(alpha=0.3)
    # m vs 成功率曲线
    ax = axes[1,0]
    rates_plot = []
    m_plot = range(k, 10*k+1, k)
    for m_t in m_plot:
        s = 0
        for _ in range(30):
            x_t = np.zeros(N)
            sup_t = np.random.choice(N, k, replace=False)
            x_t[sup_t] = np.random.randn(k)
            Phi_t = np.random.randn(m_t, N) / np.sqrt(m_t)
            x_r, _ = omp(Phi_t @ x_t, Phi_t, k)
            if np.linalg.norm(x_r - x_t) / np.linalg.norm(x_t) < 1e-6: s += 1
        rates_plot.append(s/30)
    ax.plot(list(m_plot), rates_plot, 'bo-', lw=2, markersize=8)
    ax.axvline(4*k, color='red', ls='--', alpha=0.5, label=f'm=4k={4*k}')
    ax.axhline(0.9, color='green', ls=':', alpha=0.5)
    ax.set_xlabel('测量数 m'); ax.set_ylabel('恢复成功率')
    ax.set_title(f'压缩感知相变曲线(k={k})'); ax.legend(); ax.grid(alpha=0.3)
    # L1 vs L2 几何
    ax = axes[1,1]
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'b-', lw=2, label='L2球(圆)')
    diamond_x = [1,0,-1,0,1]; diamond_y = [0,1,0,-1,0]
    ax.plot(diamond_x, diamond_y, 'r-', lw=2, label='L1球(菱形)')
    ax.plot([0.3, 0.8], [0.8, 0.3], 'k--', lw=1.5, label='约束面')
    ax.plot(0, 1, 'ro', markersize=10, label='L1解(稀疏)')
    ax.plot(0.5, 0.5, 'bo', markersize=8, label='L2解(密集)')
    ax.set_title('L1 vs L2 几何：为什么 L1 恢复稀疏'); ax.legend(fontsize=7); ax.set_aspect('equal'); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("29-压缩感知_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 29-压缩感知_结果.png")
    print("\n[总结] 1. 压缩感知=稀疏信号从远少于Nyquist的测量中恢复")
    print("2. OMP贪心算法简单有效; L1最小化更鲁棒")
    print("3. m≥C·k·log(N/k)保证精确恢复(Candès-Tao)")
    print("4. 应用:MRI 10x加速/单像素相机/Lasso回归")

if __name__ == "__main__": main()
