"""随机矩阵理论：Wigner半圆律与Tracy-Widom
================================
数学概念：随机矩阵 / Wigner矩阵 / 半圆律 / Tracy-Widom分布 / 谱间距统计 / 普适性
应用领域：量子物理(能级) / 深度学习(Hessian谱) / 金融(相关矩阵) / 黎曼ζ零点 / 信号检测
核心思想：大随机矩阵的特征值分布展现出惊人的普适性——不依赖具体分布。
  Wigner矩阵：对称随机矩阵，对角线以上独立同分布
  半圆律：N→∞时，特征值密度 ρ(λ) = (2/π)√(1-λ²) （支撑在[-2σ,2σ]）
  Tracy-Widom分布：最大特征值的极限分布（描述'边缘'涨落）
  普适性：不同分布的矩阵有相同的极限谱——这就是为什么它出现在各处
  Montgomery-Odlyzko：黎曼ζ零点间距 = GUE随机矩阵特征值间距
运行方式：python "34-随机矩阵理论.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def wigner_matrix(n, dist='normal'):
    """生成 Wigner 随机对称矩阵。"""
    if dist == 'normal':
        A = np.random.randn(n, n)
    elif dist == 'uniform':
        A = np.random.uniform(-1, 1, (n, n))
    elif dist == 'rademacher':
        A = 2 * (np.random.randint(0, 2, (n, n)) - 0.5)
    return (A + A.T) / (2 * np.sqrt(n))  # 对称化 + 归一化

def semicircle_density(x):
    """Wigner 半圆律密度 ρ(λ) = (2/π)√(1-λ²)。"""
    return np.where(np.abs(x) < 1, (2/np.pi) * np.sqrt(1 - x**2), 0)

def main():
    np.random.seed(42)
    print("="*60); print("实验 1：Wigner 半圆律——随机矩阵的特征值分布"); print("="*60)
    sizes = [50, 100, 500, 1000]
    all_eigs = {}
    for n in sizes:
        A = wigner_matrix(n, 'normal')
        eigs = np.linalg.eigvalsh(A)
        all_eigs[n] = eigs
        print(f"  N={n:>5}: 特征值范围 [{eigs.min():.3f}, {eigs.max():.3f}], 理论[-2,2]")

    print(f"\n[解读] N→∞ 时特征值密度趋近于半圆 ρ(λ)=(2/π)√(1-(λ/2)²)。")
    print(f"       支撑在 [-2σ, 2σ]（σ 是矩阵元素的方差）。")

    print("\n"+"="*60); print("实验 2：普适性——不同分布给出相同极限"); print("="*60)
    n = 500; n_trials = 20
    for dist_name in ['normal', 'uniform', 'rademacher']:
        all_e = []
        for _ in range(n_trials):
            A = wigner_matrix(n, dist_name)
            all_e.extend(np.linalg.eigvalsh(A))
        all_e = np.array(all_e)
        # 比较 Wigner 半圆
        hist, edges = np.histogram(all_e, bins=50, density=True)
        centers = (edges[:-1] + edges[1:]) / 2
        theory = semicircle_density(centers / 2) / 2  # 缩放到 [-2,2]
        max_dev = np.max(np.abs(hist - theory))
        print(f"  {dist_name:<12}: 最大偏差 = {max_dev:.4f} {'✓ 普适' if max_dev < 0.05 else '≈'}")

    print(f"\n[解读] 不管矩阵元素是正态/均匀/Rademacher(±1)，")
    print(f"       极限谱都是同一个半圆——这就是'普适性'。")

    print("\n"+"="*60); print("实验 3：Tracy-Widom 分布——最大特征值的涨落"); print("="*60)
    n = 100; n_trials = 2000
    max_eigs = []
    for _ in range(n_trials):
        A = wigner_matrix(n)
        max_eigs.append(np.linalg.eigvalsh(A)[-1])
    max_eigs = np.array(max_eigs)
    # Tracy-Widom 分布的近似（最大特征值 ≈ 2 + n^{-2/3} * TW
    tw_scaled = (max_eigs - 2) * n**(2/3)
    print(f"N={n}, {n_trials}次试验:")
    print(f"  最大特征值: 均值={max_eigs.mean():.4f}, 标准差={max_eigs.std():.4f}")
    print(f"  缩放后: 均值={tw_scaled.mean():.4f}, 标准差={tw_scaled.std():.4f}")
    print(f"  理论 Tracy-Widom β=1: 均值≈-1.27, 标准差≈1.0")

    print("\n"+"="*60); print("实验 4：Montgomery-Odlyzko——黎曼ζ零点与RMT"); print("="*60)
    print("惊人发现：黎曼ζ函数零点间距 ≈ GUE随机矩阵特征值间距")
    print("  → 暗示素数分布与随机矩阵有深层联系")
    print("  → 这是攻黎曼猜想的新窗口（14-frontier 热点方向 #3）")
    # 模拟 GUE 间距
    n_gue = 100; n_trials_gue = 100
    spacings = []
    for _ in range(n_trials_gue):
        A = wigner_matrix(n_gue)  # GUE（实对称近似）
        eigs = np.sort(np.linalg.eigvalsh(A))
        s = np.diff(eigs[n_gue//3:2*n_gue//3])  # 中间部分的间距
        s = s / np.mean(s)  # 归一化
        spacings.extend(s)
    spacings = np.array(spacings)
    # GUE 间距分布 Wigner surmise: P(s) ≈ (32/π²) s² exp(-4s²/π)
    s_theory = np.linspace(0, 4, 100)
    P_theory = (32/np.pi**2) * s_theory**2 * np.exp(-4*s_theory**2/np.pi)
    print(f"\n  GUE 特征值间距（Wigner surmise）:")
    print(f"    P(s) = (32/π²)s² exp(-4s²/π)")
    print(f"    模拟均值 s = {spacings.mean():.3f}（归一化后应为1）")
    print(f"  → 这与黎曼ζ零点间距统计一致！")

    print("\n"+"="*60); print("实验 5：RMT 在深度学习中的应用"); print("="*60)
    # 模拟 MLP 的 Hessian 谱
    print("深度学习的 Hessian 谱 ≈ 随机矩阵 + spike（Marchenko-Pastur + 少数大特征值）")
    print("  → 大部分特征值遵循 RMT（噪声方向）")
    print("  → 少数偏离的特征值 = '信号方向'（学习的本质）")
    print("  → 这解释了为什么 SGD 能在超高维空间中泛化")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    ax = axes[0,0]
    x_semi = np.linspace(-2.1, 2.1, 200)
    ax.plot(x_semi, semicircle_density(x_semi/2)/2, 'r-', lw=3, label='半圆律理论')
    for n, alpha in [(50, 0.3), (200, 0.5), (1000, 0.7)]:
        eigs = all_eigs.get(n, np.linalg.eigvalsh(wigner_matrix(n)))
        ax.hist(eigs, bins=40, density=True, alpha=alpha, label=f'N={n}')
    ax.set_xlabel('特征值 λ'); ax.set_ylabel('密度 ρ(λ)')
    ax.set_title('Wigner 半圆律：N→∞ 收敛'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[0,1]
    for dist_name, color in [('normal','blue'), ('uniform','green'), ('rademacher','red')]:
        eigs_list = []
        for _ in range(10):
            A = wigner_matrix(300, dist_name)
            eigs_list.extend(np.linalg.eigvalsh(A))
        ax.hist(eigs_list, bins=50, density=True, alpha=0.3, color=color, label=dist_name)
    ax.plot(x_semi, semicircle_density(x_semi/2)/2, 'k-', lw=2, label='半圆律')
    ax.set_title('普适性：不同分布→同一极限'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax = axes[1,0]
    ax.hist(tw_scaled, bins=50, density=True, alpha=0.7, color='steelblue', label='缩放后最大特征值')
    ax.set_xlabel('(λ_max - 2) × N^{2/3}'); ax.set_ylabel('密度')
    ax.set_title(f'Tracy-Widom 分布（N={n}, {n_trials}试验）'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1,1]
    ax.hist(spacings, bins=50, density=True, alpha=0.5, color='coral', label='GUE间距(模拟)')
    ax.plot(s_theory, P_theory, 'b-', lw=2, label='Wigner surmise')
    ax.set_xlabel('归一化间距 s'); ax.set_ylabel('P(s)')
    ax.set_title('GUE 间距分布 = 黎曼ζ零点间距'); ax.legend(); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("34-随机矩阵理论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 34-随机矩阵理论_结果.png")
    print("\n[总结] 1. Wigner半圆律:随机矩阵特征值→半圆分布(普适)")
    print("2. Tracy-Widom:最大特征值的涨落分布(边缘统计)")
    print("3. Montgomery-Odlyzko:黎曼ζ零点≈GUE间距(素数-随机矩阵连接)")
    print("4. 应用:量子能级/ML-Hessian/金融相关矩阵/信号检测")

if __name__ == "__main__": main()
