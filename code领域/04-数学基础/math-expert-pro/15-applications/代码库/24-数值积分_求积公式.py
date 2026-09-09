"""
数值积分：求积公式与误差分析
================================
数学概念：数值积分 / 梯形法则 / Simpson 法则 / Gauss 求积 / 蒙特卡洛积分 / 收敛阶
应用领域：科学计算 / 统计物理 / 金融工程 / 计算机图形学
核心思想：解析积分常不可求，用数值方法近似。
  梯形法则：∫f ≈ h[½f₀ + f₁ + ... + ½fₙ]（误差 O(h²)）
  Simpson 法则：∫f ≈ (h/3)[f₀ + 4f₁ + 2f₂ + ... + fₙ]（误差 O(h⁴)）
  Gauss 求积：最优节点+权重（n 点精确到 2n-1 次多项式）
  蒙特卡洛：高维积分的唯一选择（误差 O(1/√N)，与维数无关）
运行方式：python "24-数值积分_求积公式.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 求积公式实现 ============

def trapezoid(f, a, b, n=100):
    """梯形法则。误差 O(h²)。"""
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    return h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1])

def simpson(f, a, b, n=100):
    """Simpson 1/3 法则。误差 O(h⁴)。n 必须为偶数。"""
    if n % 2 == 1:
        n += 1
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    return (h / 3) * (y[0] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-1:2]) + y[-1])

def gauss_legendre(f, a, b, n=5):
    """Gauss-Legendre 求积。n 点精确到 2n-1 次多项式。"""
    # Gauss-Legendre 节点和权重（通过 numpy 获取）
    nodes, weights = np.polynomial.legendre.leggauss(n)
    # 变换到 [a, b]
    t = 0.5 * (b - a) * nodes + 0.5 * (a + b)
    return 0.5 * (b - a) * np.sum(weights * f(t))

def monte_carlo_integrate(f, a, b, N=10000, dims=1):
    """蒙特卡洛积分（高维优势）。误差 O(1/√N)。"""
    samples = np.random.uniform(a, b, (N, dims))
    vals = f(samples) if dims > 1 else f(samples)
    volume = (b - a) ** dims
    return volume * np.mean(vals)


# ============ 2. 实验 ============

def main():
    np.random.seed(42)

    print("=" * 60)
    print("实验 1：一维积分——四种方法对比")
    print("=" * 60)

    # 测试函数 ∫₀^π sin(x)dx = 2
    f = np.sin
    a, b = 0, np.pi
    exact = 2.0

    print(f"∫₀^π sin(x)dx = {exact}")
    print(f"\n{'方法':<18} {'n=10':<14} {'n=100':<14} {'n=1000':<14}")
    print("-" * 60)

    for name, method in [("梯形 O(h²)", trapezoid),
                          ("Simpson O(h⁴)", simpson),
                          ("Gauss-5点", lambda f, a, b, n: gauss_legendre(f, a, b, 5))]:
        results = []
        for n in [10, 100, 1000]:
            val = method(f, a, b, n)
            err = abs(val - exact)
            results.append(f"{err:.2e}")
        print(f"{name:<18} {results[0]:<14} {results[1]:<14} {results[2]:<14}")

    # 蒙特卡洛
    mc_results = []
    for N in [100, 1000, 10000]:
        val = monte_carlo_integrate(f, a, b, N)
        mc_results.append(f"{abs(val-exact):.2e}")
    print(f"{'蒙特卡洛 O(1/√N)':<18} {mc_results[0]:<14} {mc_results[1]:<14} {mc_results[2]:<14}")

    print(f"\n[解读] Gauss 5 点精度远超梯形/Simpson（用 5 个点精确积分 9 次多项式）。")
    print(f"       蒙特卡洛误差 ~1/√N 与维数无关——高维积分的唯一选择。")

    print("\n" + "=" * 60)
    print("实验 2：收敛阶验证")
    print("=" * 60)

    ns = [4, 8, 16, 32, 64, 128, 256]
    errors_trap = []
    errors_simp = []
    errors_gauss = []

    for n in ns:
        errors_trap.append(abs(trapezoid(f, a, b, n) - exact))
        errors_simp.append(abs(simpson(f, a, b, n) - exact))
        errors_gauss.append(abs(gauss_legendre(f, a, b, min(n, 10)) - exact))

    print(f"{'n':<6} {'梯形误差':<14} {'Simpson误差':<14} {'Gauss误差':<14} {'Simpson/梯形'}")
    print("-" * 62)
    for i, n in enumerate(ns):
        ratio = errors_simp[i] / errors_trap[i] if errors_trap[i] > 0 else 0
        print(f"{n:<6} {errors_trap[i]:<14.2e} {errors_simp[i]:<14.2e} {errors_gauss[i]:<14.2e} {ratio:<10.2e}")

    # 收敛阶
    p_trap = np.polyfit(np.log(ns[2:]), np.log(errors_trap[2:]), 1)[0]
    p_simp = np.polyfit(np.log(ns[2:]), np.log(errors_simp[2:]), 1)[0]
    print(f"\n收敛阶：梯形 p≈{-p_trap:.1f}（理论2），Simpson p≈{-p_simp:.1f}（理论4）")

    print("\n" + "=" * 60)
    print("实验 3：高维积分——蒙特卡洛的优势")
    print("=" * 60)

    # ∫[0,1]^d e^(-|x|²) dx（高维高斯积分近似）
    def f_nd(x):
        return np.exp(-np.sum(x**2, axis=1))

    print(f"∫[0,1]^d exp(-|x|²) dx 的高维积分：\n")
    print(f"{'维数 d':<8} {'梯形(100^d点)':<20} {'蒙特卡洛(10000点)':<20} {'MC可行性'}")
    print("-" * 65)

    for d in [1, 2, 3, 5, 10, 20]:
        n_per_dim = 100
        total_grid = n_per_dim ** d

        if total_grid <= 10**7:  # 网格法可行
            grid = np.linspace(0, 1, n_per_dim)
            meshes = np.meshgrid(*[grid] * d)
            points = np.column_stack([m.ravel() for m in meshes])
            val_grid = np.mean(f_nd(points))
            grid_str = f"{val_grid:.6f}"
        else:
            grid_str = f"不可行({total_grid:.0e}点)"

        val_mc = monte_carlo_integrate(f_nd, 0, 1, 10000, dims=d)
        feasible = "✓" if d >= 5 else "网格更快"
        print(f"{d:<8} {grid_str:<20} {val_mc:.6f}{'':>6} {feasible}")

    print(f"\n[解读] 梯形法则的代价 = n^d（指数爆炸）；")
    print(f"       蒙特卡洛的代价 = N（与维数无关）。")
    print(f"       d > 5 时网格法不可行 → 蒙特卡洛是唯一选择。")
    print(f"       这就是为什么统计物理/金融/ML 用蒙特卡洛。")

    # ============ 3. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：梯形 vs Simpson 可视化
    ax = axes[0, 0]
    x_dense = np.linspace(0, np.pi, 200)
    ax.plot(x_dense, np.sin(x_dense), 'b-', lw=2, label='sin(x)')
    # 梯形（n=8）
    x_trap = np.linspace(0, np.pi, 9)
    ax.fill_between(x_trap, np.sin(x_trap), alpha=0.2, color='red')
    ax.plot(x_trap, np.sin(x_trap), 'ro-', lw=1.5, label=f'梯形(n=8)')
    # Simpson（n=8）抛物线段
    for i in range(0, 8, 2):
        x_seg = np.linspace(x_trap[i], x_trap[i+2], 30)
        # 抛物线拟合 3 点
        coeffs = np.polyfit(x_trap[i:i+3], np.sin(x_trap[i:i+3]), 2)
        ax.plot(x_seg, np.polyval(coeffs, x_seg), 'g--', lw=1.5, alpha=0.7)
    ax.plot([], [], 'g--', lw=1.5, label='Simpson(n=8)')
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title('梯形（直线段）vs Simpson（抛物线段）')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 图 2：收敛阶 log-log
    ax = axes[0, 1]
    ax.loglog(ns, errors_trap, 'rs-', lw=2, markersize=6, label=f'梯形(p≈{-p_trap:.1f})')
    ax.loglog(ns, errors_simp, 'b^-', lw=2, markersize=6, label=f'Simpson(p≈{-p_simp:.1f})')
    ax.loglog(ns, errors_gauss, 'go-', lw=2, markersize=6, label='Gauss(5点)')
    ax.set_xlabel('n（子区间数）')
    ax.set_ylabel('绝对误差')
    ax.set_title('收敛阶对比（log-log，斜率=阶数）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 3：蒙特卡洛误差 vs N
    ax = axes[1, 0]
    Ns = [100, 500, 1000, 5000, 10000, 50000, 100000]
    mc_errors = []
    for N in Ns:
        val = monte_carlo_integrate(f, a, b, N)
        mc_errors.append(abs(val - exact))
    ax.loglog(Ns, mc_errors, 'mo-', lw=2, markersize=6)
    # 理论 1/√N 线
    ax.loglog(Ns, [1.0 / np.sqrt(N) for N in Ns], 'k--', lw=1.5, label='O(1/√N)理论')
    ax.set_xlabel('采样数 N')
    ax.set_ylabel('误差')
    ax.set_title('蒙特卡洛积分误差 ~ 1/√N')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：高维积分代价对比
    ax = axes[1, 1]
    dims = range(1, 16)
    grid_cost = [100**d for d in dims]
    mc_cost = [10000] * len(dims)  # MC 代价固定
    ax.semilogy(dims, grid_cost, 'r^-', lw=2, markersize=6, label='网格法(100^d 点)')
    ax.semilogy(dims, mc_cost, 'bs-', lw=2, markersize=6, label='蒙特卡洛(10000 点)')
    ax.axhline(1e15, color='gray', ls='--', alpha=0.5, label='float64 精度极限')
    ax.set_xlabel('维数 d')
    ax.set_ylabel('计算代价（函数求值次数）')
    ax.set_title('维数灾难：网格 vs 蒙特卡洛')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("24-数值积分_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 24-数值积分_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 梯形 O(h²)：简单但低精度")
    print("2. Simpson O(h⁴)：抛物线拟合，实用主力")
    print("3. Gauss 求积：最优节点，n 点精确到 2n-1 次")
    print("4. 蒙特卡洛：误差 1/√N，与维数无关——高维唯一选择")
    print("5. 维数灾难：网格法代价 n^d，d>5 不可行")
    print("\n[解读] 数值积分是'连续数学的离散化'——")
    print("       低维用 Gauss（最高效），高维用蒙特卡洛（唯一可行）。")
    print("       这个选择贯穿统计物理、金融工程、贝叶斯推断。")


if __name__ == "__main__":
    main()
