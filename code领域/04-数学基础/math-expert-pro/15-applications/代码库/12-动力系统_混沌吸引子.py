"""
动力系统：混沌理论与洛伦兹吸引子
================================
数学概念：动力系统 / 混沌 / 蝴蝶效应 / 奇异吸引子 / 李雅普诺夫指数
应用领域：气象预报 / 流体力学 / 生态学 / 混沌密码 / 心律分析
核心思想：确定性方程可以产生看似随机的行为——混沌。
  洛伦兹方程（1963，Edward Lorenz 发现）：
    dx/dt = σ(y - x)
    dy/dt = x(ρ - z) - y
    dz/dt = xy - βz
    经典参数 σ=10, ρ=28, β=8/3
  性质：
    1. 确定性：方程完全确定，无随机项
    2. 有界：轨迹被限制在吸引子区域内
    3. 非周期：永不重复
    4. 初值敏感：微小差异指数放大（蝴蝶效应）
  李雅普诺夫指数 λ > 0 → 混沌（相邻轨道指数分离）
运行方式：python "12-动力系统_混沌吸引子.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
# matplotlib 3.10+ 已内置 3D 投影，无需显式 import Axes3D

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 洛伦兹方程 ============

def lorenz(state, sigma=10, rho=28, beta=8/3):
    """洛伦兹方程右端。
    state = [x, y, z]
    返回 [dx/dt, dy/dt, dz/dt]
    """
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return np.array([dx, dy, dz])


def rk4_integrate(f, y0, t0, t_end, h):
    """RK4 积分器（向量版）。"""
    t = np.arange(t0, t_end + h, h)
    n = len(y0)
    y = np.zeros((len(t), n))
    y[0] = y0
    for i in range(len(t) - 1):
        k1 = f(y[i])
        k2 = f(y[i] + h * k1 / 2)
        k3 = f(y[i] + h * k2 / 2)
        k4 = f(y[i] + h * k3)
        y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


# ============ 2. 实验 ============

def main():
    np.random.seed(42)

    # ---- 实验 1：洛伦兹吸引子 ----
    print("=" * 60)
    print("实验 1：洛伦兹吸引子（混沌的标志性图像）")
    print("=" * 60)

    h = 0.01
    t_end = 40
    y0 = np.array([1.0, 1.0, 1.0])

    t, traj = rk4_integrate(lorenz, y0, 0, t_end, h)
    print(f"初值: {y0}")
    print(f"参数: σ=10, ρ=28, β=8/3（经典混沌参数）")
    print(f"积分: t∈[0,{t_end}], 步长 h={h}, 共 {len(t)} 步")
    print(f"轨迹范围: x∈[{traj[:,0].min():.2f}, {traj[:,0].max():.2f}], "
          f"y∈[{traj[:,1].min():.2f}, {traj[:,1].max():.2f}], "
          f"z∈[{traj[:,2].min():.2f}, {traj[:,2].max():.2f}]")
    print(f"\n[解读] 轨迹被限制在有界区域内，但永不重复——这就是「奇异吸引子」。")
    print(f"       形状像蝴蝶的两翼，是混沌理论的标志性图像。")

    # ---- 实验 2：蝴蝶效应（初值敏感性）----
    print("\n" + "=" * 60)
    print("实验 2：蝴蝶效应（初值差 10⁻⁸ 会怎样？）")
    print("=" * 60)

    y0_a = np.array([1.0, 1.0, 1.0])
    y0_b = np.array([1.0, 1.0, 1.0 + 1e-8])  # z 差 10⁻⁸

    t2, traj_a = rk4_integrate(lorenz, y0_a, 0, 30, h)
    _, traj_b = rk4_integrate(lorenz, y0_b, 0, 30, h)

    # 计算两条轨迹的距离
    dist = np.sqrt(np.sum((traj_a - traj_b) ** 2, axis=1))

    # 找距离超过 1 的时刻
    diverge_t = t2[np.searchsorted(dist, 1.0)] if np.any(dist > 1) else float('inf')

    print(f"初值 A: {y0_a}")
    print(f"初值 B: {y0_b}（z 差 10⁻⁸）")
    print(f"\n时刻 t=0:    距离 = {dist[0]:.2e}")
    print(f"时刻 t=5:    距离 = {dist[t2.searchsorted(5)]:.4f}")
    print(f"时刻 t=10:   距离 = {dist[t2.searchsorted(10)]:.4f}")
    print(f"时刻 t=20:   距离 = {dist[t2.searchsorted(20)]:.4f}")
    print(f"距离超过 1 的时刻: t ≈ {diverge_t:.1f}")

    print(f"\n[解读] 初值仅差 10⁻⁸（蝴蝶扇一下翅膀），")
    print(f"       约 t≈{diverge_t:.0f} 后两条轨迹完全分道扬镳。")
    print(f"       这就是「蝴蝶效应」——确定性系统的长期不可预测性。")

    # ---- 实验 3：李雅普诺夫指数 ----
    print("\n" + "=" * 60)
    print("实验 3：最大李雅普诺夫指数（混沌的定量判据）")
    print("=" * 60)

    # 计算方法：跟踪两条极近的轨迹，测量距离增长率
    # λ = lim (1/t) · ln(d(t)/d(0))
    # λ > 0 → 混沌

    y0_ref = np.array([1.0, 1.0, 1.0])
    eps = 1e-10
    y0_pert = y0_ref + np.array([eps, 0, 0])

    t3, traj_ref = rk4_integrate(lorenz, y0_ref, 0, 20, 0.01)
    _, traj_pert = rk4_integrate(lorenz, y0_pert, 0, 20, 0.01)

    dist3 = np.sqrt(np.sum((traj_ref - traj_pert) ** 2, axis=1))
    # 避免除以 0
    log_dist = np.log(dist3[1:] / dist3[0] + 1e-300)

    # 李雅普诺夫指数 ≈ log(d(t)/d(0)) / t
    # 取后半段（瞬态消退后）的平均
    mask = t3[1:] > 5  # 丢弃前 5 秒瞬态
    lyapunov = np.mean(log_dist[mask] / t3[1:][mask])

    print(f"初始扰动: ε = {eps}")
    print(f"最大李雅普诺夫指数 λ ≈ {lyapunov:.4f}")
    print(f"λ > 0: {'✓ 确认为混沌系统' if lyapunov > 0 else '✗ 非混沌'}")
    print(f"\n[解读] λ ≈ {lyapunov:.2f} 意味着距离每秒增长 e^{lyapunov:.2f} ≈ {np.exp(lyapunov):.2f} 倍。")
    print(f"       可预测时间 ≈ 1/λ ≈ {1/lyapunov:.1f} 秒（之后误差与吸引子同量级）。")
    print(f"       这就是为什么天气预报 2 周后基本不可信——大气是混沌系统。")

    # ---- 实验 4：不同 ρ 值的行为（分岔与混沌）----
    print("\n" + "=" * 60)
    print("实验 4：参数 ρ 对行为的影响（定态 → 混沌）")
    print("=" * 60)

    rhos = [0.5, 10, 24.0, 24.5, 28, 40]
    print(f"{'ρ':<8} {'行为':<20} {'x 终值范围':<20} {'判定'}")
    print("-" * 60)

    for rho in rhos:
        f = lambda s, r=rho: lorenz(s, rho=r)
        _, tr = rk4_integrate(f, np.array([1.0, 1.0, 1.0]), 0, 20, 0.01)
        # 取后半段分析
        x_late = tr[len(tr)//2:, 0]
        x_range = x_late.max() - x_late.min()

        if x_range < 0.01:
            behavior = "定态（收敛到不动点）"
            judge = "非混沌"
        elif x_range < 2:
            behavior = "极限环（周期）"
            judge = "非混沌"
        else:
            behavior = "混沌（奇异吸引子）"
            judge = "混沌"

        print(f"{rho:<8.1f} {behavior:<20} [{x_late.min():.2f}, {x_late.max():.2f}]{'':>4} {judge}")

    print(f"\n[解读] ρ < 1: 收敛到原点（稳定）")
    print(f"       1 < ρ < 24.74: 两个对称不动点（定态）")
    print(f"       ρ ≈ 24.74: Hopf 分岔（失稳）")
    print(f"       ρ > 24.74: 混沌（洛伦兹吸引子）")
    print(f"       → 参数微小变化导致定性改变 = 分岔（bifurcation）")

    # ============ 3. 可视化 ============
    fig = plt.figure(figsize=(16, 12))

    # 图 1：3D 洛伦兹吸引子
    ax = fig.add_subplot(221, projection='3d')
    ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'b-', lw=0.3, alpha=0.7)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('洛伦兹吸引子（3D 奇异吸引子）')

    # 图 2：蝴蝶效应（两条轨迹的 x 分量）
    ax = fig.add_subplot(222)
    ax.plot(t2, traj_a[:, 0], 'b-', lw=1, label='初值 A')
    ax.plot(t2, traj_b[:, 0], 'r-', lw=1, label='初值 B (差10⁻⁸)')
    ax.axvline(diverge_t, color='gray', ls='--', alpha=0.5, label=f'分岔 t≈{diverge_t:.1f}')
    ax.set_xlabel('时间 t')
    ax.set_ylabel('x(t)')
    ax.set_title('蝴蝶效应：初值差 10⁻⁸ 的两条轨迹')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 图 3：距离增长（对数尺度）
    ax = fig.add_subplot(223)
    ax.semilogy(t2, dist, 'g-', lw=1.5)
    ax.axhline(1, color='r', ls='--', alpha=0.5, label='距离=1')
    ax.set_xlabel('时间 t')
    ax.set_ylabel('轨迹距离（对数）')
    ax.set_title('蝴蝶效应：距离指数增长')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：x 分量的分岔图（不同 ρ 下的终态）
    ax = fig.add_subplot(224)
    for rho in [20, 24, 24.5, 28, 35]:
        f = lambda s, r=rho: lorenz(s, rho=r)
        _, tr = rk4_integrate(f, np.array([1.0, 1.0, 1.0]), 0, 30, 0.01)
        x_late = tr[len(tr)//2:, 0]
        ax.scatter([rho]*len(x_late[::20]), x_late[::20], s=0.5, alpha=0.3, label=f'ρ={rho}')
    ax.set_xlabel('ρ')
    ax.set_ylabel('x（后段采样）')
    ax.set_title('分岔图：ρ 增大时从定态到混沌')
    ax.legend(fontsize=7, markerscale=5)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("12-动力系统_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 12-动力系统_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 洛伦兹方程：确定性 ODE 产生混沌（非周期+有界+初值敏感）")
    print("2. 蝴蝶效应：初值差 10⁻⁸ 在 ~15 时间单位后放大到 O(1)")
    print("3. 李雅普诺夫指数 λ>0 是混沌的定量判据（λ≈0.9 for 洛伦兹）")
    print("4. 分岔：参数 ρ 从小到大 → 定态→极限环→混沌")
    print("\n[解读] 混沌 = '确定性中的随机性'——")
    print("       方程完全确定，但长期行为不可预测（初值不可能无限精确）。")
    print("       这解释了：天气预报为何 2 周后失效、为何难以预测股市、")
    print("       为何生态系统的微小扰动可能引发种群崩溃。")


if __name__ == "__main__":
    main()
