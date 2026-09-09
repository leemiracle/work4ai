"""
拓扑数据分析：持续同调与数据形状
================================
数学概念：拓扑数据分析 TDA / 持续同调 / Betti 数 / barcode / Vietnamorish 复形
应用领域：材料发现 / 药物设计 / 生物信息 / 时间序列 / 机器学习（表示几何）
核心思想：TDA 从点云数据中提取"形状"信息——连通分量、洞、空腔。
  Vietnamorish 复形：对每个半径 ε，连接距离 ≤ 2ε 的点 → 形成拓扑空间
  Betti 数：β₀=连通分量数，β₁=一维洞数，β₂=二维空腔数
  持久性：随 ε 变化时拓扑特征的"寿命"——长寿特征=真信号，短寿=噪声
  Barcode：每个拓扑特征一条线段（出生→死亡），长寿线段=数据真实结构
运行方式：python "20-TDA_拓扑数据分析.py"
依赖：numpy, matplotlib, scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import connected_components

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. Vietnamorish 复形与持续同调 ============

def betti_numbers(points, epsilon):
    """计算给定半径 ε 时的 Betti 数（简化版：只算 β₀ 和 β₁）。
    构造 Vietnamorish 复形，用图论方法计算。
    """
    n = len(points)
    dist = squareform(pdist(points))

    # 邻接矩阵：距离 ≤ 2ε 的点相连
    adj = (dist <= 2 * epsilon).astype(float)
    np.fill_diagonal(adj, 0)

    # β₀ = 连通分量数（图论）
    n_components, _ = connected_components(adj, directed=False)

    # β₁（简化估计）：对每个连通分量，β₁ ≈ 边数 - 顶点数 + 1
    # 这是一个粗略估计（完整的同调计算需要边界算子）
    edges = np.sum(adj) / 2  # 无向图边数
    beta1_approx = max(0, int(edges) - n + n_components)

    return n_components, beta1_approx


def persistence_barcode(points, epsilon_range):
    """计算持续同调 barcode（β₀ 和 β₁ 随 ε 变化）。"""
    bettas0 = []
    bettas1 = []

    for eps in epsilon_range:
        b0, b1 = betti_numbers(points, eps)
        bettas0.append(b0)
        bettas1.append(b1)

    return np.array(bettas0), np.array(bettas1)


# ============ 2. 数据生成 ============

def generate_circle(n=100, r=1.0, noise=0.1, seed=42):
    """生成圆环上的点云（有一个洞）。"""
    rng = np.random.RandomState(seed)
    theta = rng.uniform(0, 2 * np.pi, n)
    x = r * np.cos(theta) + rng.randn(n) * noise
    y = r * np.sin(theta) + rng.randn(n) * noise
    return np.column_stack([x, y])


def generate_two_clusters(n=100, seed=42):
    """生成两个分离的簇（β₀=2）。"""
    rng = np.random.RandomState(seed)
    c1 = rng.randn(n // 2, 2) + [3, 3]
    c2 = rng.randn(n // 2, 2) + [-3, -3]
    return np.vstack([c1, c2])


def generate_torus_cross_section(n=150, R=2, r=0.7, noise=0.05, seed=42):
    """生成类似环面的 2D 投影（有两个洞的截面）。"""
    rng = np.random.RandomState(seed)
    theta = rng.uniform(0, 2 * np.pi, n)
    phi = rng.uniform(0, 2 * np.pi, n)
    # 环面参数化，取一个截面
    x = (R + r * np.cos(phi)) * np.cos(theta)
    y = (R + r * np.cos(phi)) * np.sin(theta)
    x += rng.randn(n) * noise
    y += rng.randn(n) * noise
    return np.column_stack([x, y])


# ============ 3. 实验 ============

def main():
    np.random.seed(42)

    print("=" * 60)
    print("实验 1：圆环——检测一维洞（β₁=1）")
    print("=" * 60)

    circle = generate_circle(100, r=2.0, noise=0.15)
    epsilon_range = np.linspace(0.05, 2.0, 50)
    b0_circle, b1_circle = persistence_barcode(circle, epsilon_range)

    print(f"数据: 100 个点采样自半径=2 的圆环（加噪声）")
    print(f"Vietnamorish 复形参数 ε ∈ [0.05, 2.0]")

    # 找到 β₁=1 的稳定区间
    stable_b1 = np.where(b1_circle == 1)[0]
    if len(stable_b1) > 0:
        eps_range_b1 = epsilon_range[stable_b1]
        print(f"\nβ₁=1 的稳定区间: ε ∈ [{eps_range_b1.min():.3f}, {eps_range_b1.max():.3f}]")
        print(f"→ 检测到一个持续的一维洞（圆环结构）")

    print(f"\n[解读] 当 ε 太小→全是孤立点（β₀=100）；")
    print(f"       当 ε 适中→形成环（β₁=1，检测到洞）；")
    print(f"       当 ε 太大→所有点连成一个实心盘（β₁=0，洞被填满）。")

    print("\n" + "=" * 60)
    print("实验 2：两个簇——检测连通分量（β₀=2）")
    print("=" * 60)

    clusters = generate_two_clusters(100)
    b0_clusters, b1_clusters = persistence_barcode(clusters, epsilon_range)

    stable_b0_2 = np.where(b0_clusters == 2)[0]
    if len(stable_b0_2) > 0:
        eps_range_2 = epsilon_range[stable_b0_2]
        print(f"β₀=2 的稳定区间: ε ∈ [{eps_range_2.min():.3f}, {eps_range_2.max():.3f}]")
        print(f"→ 检测到两个连通分量")

    print(f"\n[解读] 小 ε: β₀=100（孤立点）；中 ε: β₀=2（两个簇）；大 ε: β₀=1（合并）。")
    print(f"       β₀=2 的区间长度 = 簇间分离程度的度量。")

    print("\n" + "=" * 60)
    print("实验 3：噪声 vs 信号——持久性的价值")
    print("=" * 60)

    # 生成有噪声的圆环
    circle_noisy = generate_circle(100, r=2.0, noise=0.4)  # 大噪声
    b0_noisy, b1_noisy = persistence_barcode(circle_noisy, epsilon_range)

    # 比较 Betti 数变化模式
    print(f"{'ε':<8} {'β₀(低噪)':<10} {'β₁(低噪)':<10} {'β₀(高噪)':<10} {'β₁(高噪)':<10}")
    print("-" * 50)
    for i in range(0, len(epsilon_range), 5):
        eps = epsilon_range[i]
        print(f"{eps:<8.2f} {b0_circle[i]:<10} {b1_circle[i]:<10} {b0_noisy[i]:<10} {b1_noisy[i]:<10}")

    print(f"\n[解读] 低噪声时 β₁=1 的区间很长（信号）；")
    print(f"       高噪声时 β₁ 波动很大（噪声混入）。")
    print(f"       持续同调的力量：区分'长寿特征'（信号）和'短寿特征'（噪声）。")

    print("\n" + "=" * 60)
    print("实验 4：TDA 的应用——为什么数学家关心数据形状？")
    print("=" * 60)

    print("TDA 应用场景：")
    print("  1. 材料科学：多孔材料的孔径分布（β₁, β₂）")
    print("  2. 神经科学：大脑神经网络的拓扑结构")
    print("  3. 机器学习：表示空间的几何（mechanistic interpretability）")
    print("  4. 时间序列：信号周期性检测（Takens 嵌入 + TDA）")
    print("  5. 生物信息：蛋白质结构的形状分析")
    print("  6. 异常检测：'形状变化' = 异常事件")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    # 图 1：圆环点云 + 不同 ε 的复形
    ax = axes[0, 0]
    ax.scatter(circle[:, 0], circle[:, 1], s=20, c='steelblue')
    # 画 ε=0.5 时的边
    dist_c = squareform(pdist(circle))
    eps_show = 0.5
    for i in range(len(circle)):
        for j in range(i + 1, len(circle)):
            if dist_c[i, j] <= 2 * eps_show:
                ax.plot([circle[i, 0], circle[j, 0]],
                        [circle[i, 1], circle[j, 1]], 'b-', alpha=0.1, lw=0.5)
    ax.set_title(f'Vietnamorish 复形（圆环, ε={eps_show}）')
    ax.set_aspect('equal')
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)

    # 图 2：Betti 数变化（圆环）
    ax = axes[0, 1]
    ax.plot(epsilon_range, b0_circle, 'b-', lw=2, label='β₀（连通分量）')
    ax.plot(epsilon_range, b1_circle, 'r-', lw=2, label='β₁（一维洞）')
    ax.set_xlabel('ε（Vietnamorish 半径）')
    ax.set_ylabel('Betti 数')
    ax.set_title('圆环的持续 Betti 数')
    ax.legend()
    ax.set_ylim(-0.5, 15)
    ax.grid(alpha=0.3)

    # 图 3：Betti 数变化（两个簇）
    ax = axes[0, 2]
    ax.scatter(clusters[:, 0], clusters[:, 1], s=20, c=['red'] * 50 + ['blue'] * 50)
    ax.set_title('两个簇点云（β₀ 应为 2）')
    ax.set_aspect('equal')

    # 图 4：两个簇的 Betti 数
    ax = axes[1, 0]
    ax.plot(epsilon_range, b0_clusters, 'b-', lw=2, label='β₀')
    ax.plot(epsilon_range, b1_clusters, 'r-', lw=2, label='β₁')
    ax.axhline(2, color='green', ls='--', alpha=0.5, label='β₀=2（两簇）')
    ax.set_xlabel('ε')
    ax.set_ylabel('Betti 数')
    ax.set_title('两个簇的持续 Betti 数')
    ax.legend()
    ax.set_ylim(-0.5, 15)
    ax.grid(alpha=0.3)

    # 图 5：高噪声圆环
    ax = axes[1, 1]
    ax.scatter(circle_noisy[:, 0], circle_noisy[:, 1], s=20, c='orange', alpha=0.7)
    ax.set_title('高噪声圆环（σ=0.4）')
    ax.set_aspect('equal')

    # 图 6：持续 barcode（简化版：β₁ 的"生存区间"）
    ax = axes[1, 2]
    # 画 β₁ 的变化作为"barcode"
    ax.fill_between(epsilon_range, 0, b1_circle, alpha=0.5, color='red', label='β₁ 圆环(低噪)')
    ax.fill_between(epsilon_range, 0, b1_noisy, alpha=0.3, color='orange', label='β₁ 圆环(高噪)')
    ax.set_xlabel('ε')
    ax.set_ylabel('β₁')
    ax.set_title('持续 barcode（β₁ 的生存区间）')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("20-TDA_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 20-TDA_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. TDA = 从点云数据提取'形状'（连通分量/洞/空腔）")
    print("2. Betti 数：β₀=分量数, β₁=洞数, β₂=空腔数")
    print("3. 持续同调：随 ε 变化的拓扑特征寿命——长寿=信号")
    print("4. Vietnamorish 复形：距离 ≤ 2ε 的点相连")
    print("\n[解读] TDA 是'数据中的拓扑学'——")
    print("       传统的统计看'数值'，TDA 看'形状'。")
    print("       当数据有拓扑结构（环/分支/空腔）时，TDA 能捕获统计方法漏掉的信息。")
    print("       这是 2024-2026 最热门的交叉方向之一（[热点方向追踪/](../热点方向追踪/) #4）。")


if __name__ == "__main__":
    main()
