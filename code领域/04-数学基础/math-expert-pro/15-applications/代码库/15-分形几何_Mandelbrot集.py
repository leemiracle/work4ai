"""
分形几何：Mandelbrot 集与迭代函数系统
================================
数学概念：分形 / 自相似 / Hausdorff 维数 / Mandelbrot 集 / Julia 集 / 迭代函数系统
应用领域：图像压缩 / 自然形态建模 / 天线设计 / 艺术生成
核心思想：分形 = 自相似结构（局部看起来像整体）。
  Mandelbrot 集 M = {c ∈ ℂ : 迭代 z_{n+1} = z_n² + c, z_0=0 不发散}
  边界是数学中最复杂的对象之一（Hausdorff 维数 = 2）。
  迭代函数系统（IFS）：用压缩映射的随机迭代生成分形（如 Barnsley 蕨）。
  盒维数：N(ε) ~ ε^{-D}（用 ε 大小的盒子覆盖所需数量随 ε 的变化）
运行方式：python "15-分形几何_Mandelbrot集.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. Mandelbrot 集 ============

def mandelbrot(xmin=-2.5, xmax=1.0, ymin=-1.5, ymax=1.5,
               width=800, height=600, max_iter=100):
    """计算 Mandelbrot 集。
    z_{n+1} = z_n² + c, z_0 = 0
    若 |z_n| > 2 则发散（c 不在 M 中）
    返回：每个点的逃逸时间（用于着色）
    """
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y  # 复参数 c
    Z = np.zeros_like(C)
    escape_time = np.zeros_like(C, dtype=int)

    mask = np.ones_like(C, dtype=bool)
    for i in range(max_iter):
        Z[mask] = Z[mask]**2 + C[mask]
        diverged = np.abs(Z) > 2
        newly_escaped = diverged & mask
        escape_time[newly_escaped] = i
        mask = mask & ~diverged

    escape_time[mask] = max_iter  # 未发散的点
    return X, Y, escape_time


# ============ 2. Julia 集 ============

def julia_set(c, xmin=-1.5, xmax=1.5, ymin=-1.5, ymax=1.5,
              width=600, height=600, max_iter=100):
    """计算 Julia 集 J(c)。
    固定参数 c，变化初始点 z_0：z_{n+1} = z_n² + c
    与 Mandelbrot 的区别：Mandelbrot 变 c 定 z_0=0，Julia 变 z_0 定 c。
    """
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    escape_time = np.zeros_like(Z, dtype=int)
    mask = np.ones_like(Z, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask]**2 + c
        diverged = np.abs(Z) > 2
        newly_escaped = diverged & mask
        escape_time[newly_escaped] = i
        mask = mask & ~diverged

    escape_time[mask] = max_iter
    return X, Y, escape_time


# ============ 3. 迭代函数系统（IFS）：Barnsley 蕨 ============

def barnsley_fern(n_points=50000):
    """Barnsley 蕨（IFS 生成的最著名分形）。
    四个仿射变换以不同概率随机选择：
    f₁(x,y) = (0, 0.16y)                   p=0.01（茎）
    f₂(x,y) = (0.85x+0.04y, -0.04x+0.85y+1.6)  p=0.85（主体）
    f₃(x,y) = (0.2x-0.26y, 0.23x+0.22y+1.6)    p=0.07（左叶）
    f₄(x,y) = (-0.15x+0.28y, 0.26x+0.24y+0.44) p=0.07（右叶）
    """
    x, y = 0.0, 0.0
    points = np.zeros((n_points, 2))

    for i in range(n_points):
        r = np.random.random()
        if r < 0.01:
            x, y = 0, 0.16 * y
        elif r < 0.86:
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:
            x, y = 0.20 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else:
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        points[i] = [x, y]

    return points


# ============ 4. 盒维数计算 ============

def box_counting_dimension(points, min_box=2, max_box=50):
    """盒维数计算：N(ε) ~ ε^{-D}
    points: 点集 (N, 2)
    返回：盒维数估计
    """
    x_min, x_max = points[:, 0].min(), points[:, 0].max()
    y_min, y_max = points[:, 1].min(), points[:, 1].max()

    sizes = []
    counts = []

    for n_box in range(min_box, max_box + 1):
        eps_x = (x_max - x_min) / n_box
        eps_y = (y_max - y_min) / n_box

        # 计算每个点落在哪个盒子里
        bx = ((points[:, 0] - x_min) / eps_x).astype(int)
        by = ((points[:, 1] - y_min) / eps_y).astype(int)
        boxes = set(zip(bx, by))

        sizes.append(1.0 / n_box)
        counts.append(len(boxes))

    sizes = np.array(sizes)
    counts = np.array(counts)

    # log-log 拟合：log N = D log(1/ε) → 用 1/sizes（=n_box）拟合
    inv_sizes = 1.0 / sizes  # = n_box
    coeffs = np.polyfit(np.log(inv_sizes), np.log(counts), 1)
    dimension = coeffs[0]

    return sizes, counts, dimension


# ============ 5. 实验 ============

def main():
    np.random.seed(42)

    print("=" * 60)
    print("实验 1：Mandelbrot 集——数学中最复杂的对象")
    print("=" * 60)

    X, Y, M = mandelbrot(width=800, height=600, max_iter=100)
    in_set = np.sum(M == 100)
    total = M.size

    print(f"网格: 800×600 = {total} 点")
    print(f"迭代上限: 100 步")
    print(f"Mandelbrot 集内点数: {in_set} ({in_set/total:.1%})")
    print(f"逃逸点数: {total - in_set} ({(total-in_set)/total:.1%})")
    print(f"\n[解读] Mandelbrot 集的边界 Hausdorff 维数 = 2（充满平面）。")
    print(f"       它是数学中已知最复杂的几何对象——边界上每个尺度都有新结构。")

    print("\n" + "=" * 60)
    print("实验 2：Julia 集——不同参数 c 的变化")
    print("=" * 60)

    c_values = [
        (-0.7, 0.27015, "经典 Julia"),
        (0.285, 0.01, "近 Mandelbrot 边界"),
        (-0.8, 0.156, "螺旋型"),
        (-0.4, 0.6, "树突型"),
    ]

    for cx, cy, name in c_values:
        c = complex(cx, cy)
        _, _, J = julia_set(c, max_iter=80)
        connected = np.sum(J == 80) > 0
        print(f"  c={c:.4f} ({name}): {'连通' if connected else '断开'}")

    print(f"\n[解读] Mandelbrot 集是所有 Julia 集的'目录'——")
    print(f"       c 在 M 内 → J(c) 连通；c 在 M 外 → J(c) 断开（Fatou 尘埃）。")

    print("\n" + "=" * 60)
    print("实验 3：Barnsley 蕨——迭代函数系统（IFS）")
    print("=" * 60)

    fern = barnsley_fern(50000)
    print(f"生成 50000 个点的 Barnsley 蕨")
    print(f"四个仿射变换，概率 [0.01, 0.85, 0.07, 0.07]")

    # 计算盒维数
    sizes, counts, dim = box_counting_dimension(fern, 3, 40)
    print(f"盒维数估计: D ≈ {dim:.3f}")
    print(f"\n[解读] Barnsley 蕨的维数 ≈ 1.85（介于 1 和 2 之间——'分形'维数）。")
    print(f"       4 个简单的仿射变换就能生成逼真的蕨叶形状——")
    print(f"       这就是'压缩映射原理'的力量（Banach 不动点定理）。")

    print("\n" + "=" * 60)
    print("实验 4：分形的自相似性")
    print("=" * 60)

    # Koch 雪花的盒维数
    def koch_snowflake(iterations=5):
        """生成 Koch 雪花。"""
        # 初始三角形
        angles = [0, 2*np.pi/3, 4*np.pi/3]
        points = [(np.cos(a), np.sin(a)) for a in angles] + [(np.cos(0), np.sin(0))]

        for _ in range(iterations):
            new_points = []
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i+1]
                # 分成 4 段
                d = ((p2[0]-p1[0])/3, (p2[1]-p1[1])/3)
                pa = (p1[0]+d[0], p1[1]+d[1])
                pc = (p1[0]+2*d[0], p1[1]+2*d[1])
                # 尖端
                angle = np.arctan2(d[1], d[0]) - np.pi/3
                length = np.sqrt(d[0]**2 + d[1]**2)
                pb = (pa[0]+length*np.cos(angle), pa[1]+length*np.sin(angle))
                new_points.extend([p1, pa, pb, pc])
            new_points.append(points[-1])
            points = new_points
        return np.array(points)

    koch = koch_snowflake(iterations=5)
    sizes_k, counts_k, dim_k = box_counting_dimension(koch, 3, 40)

    print(f"Koch 雪花（5 次迭代）: {len(koch)} 个顶点")
    print(f"Koch 雪花盒维数: D ≈ {dim_k:.3f}（理论值 log(4)/log(3) ≈ {np.log(4)/np.log(3):.3f}）")
    print(f"Koch 雪花性质：面积有限，周长无限")
    print(f"\n[解读] 分形的'维度'不一定是整数——这是它与欧几里得图形的根本区别。")

    # ============ 6. 可视化 ============
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    # 图 1：Mandelbrot 集
    ax = axes[0, 0]
    im = ax.imshow(M, extent=[-2.5, 1.0, -1.5, 1.5], cmap='hot', origin='lower')
    ax.set_xlabel('Re(c)')
    ax.set_ylabel('Im(c)')
    ax.set_title('Mandelbrot 集（颜色=逃逸时间）')
    plt.colorbar(im, ax=ax, label='逃逸迭代数')

    # 图 2：Julia 集（经典）
    ax = axes[0, 1]
    c = complex(-0.7, 0.27015)
    _, _, J1 = julia_set(c, max_iter=80)
    im = ax.imshow(J1, extent=[-1.5, 1.5, -1.5, 1.5], cmap='magma', origin='lower')
    ax.set_xlabel('Re(z)')
    ax.set_ylabel('Im(z)')
    ax.set_title(f'Julia 集（c={c:.3f}）')
    plt.colorbar(im, ax=ax)

    # 图 3：Barnsley 蕨
    ax = axes[0, 2]
    ax.scatter(fern[::5, 0], fern[::5, 1], s=0.1, c='green', alpha=0.5)
    ax.set_title('Barnsley 蕨（IFS 生成分形）')
    ax.set_aspect('equal')
    ax.axis('off')

    # 图 4：Mandelbrot 放大（细节）
    ax = axes[1, 0]
    X2, Y2, M2 = mandelbrot(xmin=-0.8, xmax=-0.7, ymin=0.05, ymax=0.15,
                             width=600, height=600, max_iter=200)
    im = ax.imshow(M2, extent=[-0.8, -0.7, 0.05, 0.15], cmap='hot', origin='lower')
    ax.set_title('Mandelbrot 放大（无限自相似）')
    ax.set_xlabel('Re(c)')
    ax.set_ylabel('Im(c)')

    # 图 5：盒维数 log-log 图（蕨 + Koch）
    ax = axes[1, 1]
    ax.loglog(1/sizes, counts, 'go-', label=f'Barnsley 蕨 (D≈{dim:.2f})')
    ax.loglog(1/sizes_k, counts_k, 'bs-', label=f'Koch 雪花 (D≈{dim_k:.2f})')
    ax.set_xlabel('1/ε（盒子数的倒数）')
    ax.set_ylabel('N(ε)（盒子数）')
    ax.set_title('盒维数：log-log 图（斜率=维数）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 6：Koch 雪花
    ax = axes[1, 2]
    ax.fill(koch[:, 0], koch[:, 1], 'lightblue', edgecolor='blue')
    ax.set_title(f'Koch 雪花（D≈{dim_k:.2f}, 周长=∞）')
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("15-分形几何_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 15-分形几何_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. Mandelbrot 集：z_{n+1}=z_n²+c 的收敛点集，边界维数=2")
    print("2. Julia 集：固定 c 变 z_0，连通性取决于 c 是否在 M 内")
    print("3. IFS（迭代函数系统）：压缩映射随机迭代生成自然分形")
    print("4. 分形维数：非整数维度（盒维数 log-log 斜率）")
    print("\n[解读] 分形是'自然界的几何'——海岸线/云朵/血管/闪电都是分形。")
    print("       Mandelbrot 集 = 简单迭代 z²+c 产生无限复杂——")
    print("       这是'简单规则产生复杂性的最美例子'。")


if __name__ == "__main__":
    main()
