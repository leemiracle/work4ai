"""
偏微分方程：热传导与波动方程
================================
数学概念：偏微分方程 PDE / 热方程 / 波动方程 / 有限差分法 / 稳定性条件
应用领域：传热学 / 电磁波 / 量子力学 / 流体力学 / 金融数学
核心思想：PDE 描述多变量函数的变化规律。
  热方程：∂u/∂t = α ∇²u（扩散，时间不可逆，平滑化）
  波动方程：∂²u/∂t² = c² ∇²u（传播，时间可逆，保能量）
  有限差分法（FDM）：用差分替代微分
    ∂u/∂t ≈ (u(t+Δt) - u(t)) / Δt
    ∇²u ≈ (u(x+Δx) + u(x-Δx) - 2u(x)) / Δx²
  CFL 稳定性条件：α Δt / Δx² ≤ 0.5（显式热方程）
运行方式：python "14-偏微分方程_热传导与波动.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 有限差分法求解 PDE ============

def solve_heat_1d(nx=100, nt=500, alpha=0.4, dx=0.1, dt=0.01, init_type='pulse'):
    """一维热方程 ∂u/∂t = α ∂²u/∂x²（有限差分）。
    
    显式格式：u^{n+1}_i = u^n_i + r(u^n_{i+1} - 2u^n_i + u^n_{i-1})
    其中 r = α Δt / Δx²（CFL 数）
    稳定性要求 r ≤ 0.5
    """
    r = alpha * dt / dx**2  # CFL 数
    x = np.linspace(0, (nx-1)*dx, nx)
    u = np.zeros(nx)
    
    # 初始条件
    if init_type == 'pulse':
        u[nx//2 - 5:nx//2 + 5] = 1.0  # 中心脉冲
    elif init_type == 'step':
        u[:nx//2] = 1.0  # 阶跃
    
    # 边界条件：u(0)=u(L)=0（Dirichlet）
    history = [u.copy()]
    
    for n in range(nt):
        u_new = u.copy()
        u_new[1:-1] = u[1:-1] + r * (u[2:] - 2*u[1:-1] + u[:-2])
        u_new[0] = u_new[-1] = 0  # 边界
        u = u_new
        if n % 10 == 0:
            history.append(u.copy())
    
    return x, np.array(history), r


def solve_wave_1d(nx=100, nt=500, c=1.0, dx=0.1, dt=0.05, init_type='plucked'):
    """一维波动方程 ∂²u/∂t² = c² ∂²u/∂x²（有限差分）。
    
    显式格式：
    u^{n+1}_i = 2u^n_i - u^{n-1}_i + r²(u^n_{i+1} - 2u^n_i + u^n_{i-1})
    其中 r = c Δt / Δx（CFL 数）
    稳定性要求 r ≤ 1
    """
    r = c * dt / dx  # CFL 数
    x = np.linspace(0, (nx-1)*dx, nx)
    u = np.zeros(nx)
    u_prev = np.zeros(nx)
    
    # 初始条件
    if init_type == 'plucked':
        center = nx // 2
        u[:center] = np.linspace(0, 1, center)
        u[center:] = np.linspace(1, 0, nx - center)
        # 初始速度 = 0 → u_prev = u（用空间导数近似第一步）
        u_prev = u.copy()
    elif init_type == 'pulse':
        u[nx//2 - 5:nx//2 + 5] = 1.0
        u_prev = u.copy()
    
    history = [u.copy()]
    
    for n in range(nt):
        u_new = np.zeros(nx)
        u_new[1:-1] = (2 * u[1:-1] - u_prev[1:-1] +
                       r**2 * (u[2:] - 2*u[1:-1] + u[:-2]))
        u_new[0] = u_new[-1] = 0  # 固定边界
        u_prev = u.copy()
        u = u_new
        if n % 10 == 0:
            history.append(u.copy())
    
    return x, np.array(history), r


def solve_heat_2d(nx=50, ny=50, nt=300, alpha=0.2, dx=0.1, dt=0.01):
    """二维热方程 ∂u/∂t = α(∂²u/∂x² + ∂²u/∂y²)。"""
    r = alpha * dt / dx**2
    x = np.linspace(0, (nx-1)*dx, nx)
    y = np.linspace(0, (ny-1)*dx, ny)
    u = np.zeros((ny, nx))
    
    # 初始条件：中心热源
    u[ny//2 - 3:ny//2 + 3, nx//2 - 3:nx//2 + 3] = 1.0
    
    history = [u.copy()]
    
    for n in range(nt):
        u_new = u.copy()
        u_new[1:-1, 1:-1] = u[1:-1, 1:-1] + r * (
            u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[:-2, 1:-1] +  # x 方向
            u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, :-2]     # y 方向
        )
        u = u_new
        if n % 20 == 0:
            history.append(u.copy())
    
    return x, y, np.array(history), r


# ============ 2. 实验 ============

def main():
    print("=" * 60)
    print("实验 1：一维热传导方程 ∂u/∂t = α ∂²u/∂x²")
    print("=" * 60)

    x, heat_history, r_heat = solve_heat_1d(nx=100, nt=500, alpha=0.4,
                                              dx=0.1, dt=0.01, init_type='pulse')

    print(f"网格: 100 点, 500 时间步")
    print(f"CFL 数 r = αΔt/Δx² = {r_heat:.3f}（稳定要求 ≤ 0.5）{'✓' if r_heat <= 0.5 else '✗'}")
    print(f"初始条件: 中心脉冲（u[45:55]=1, 其余=0）")
    print(f"边界条件: u(0)=u(L)=0（Dirichlet，两端固定零度）")

    # 峰值衰减
    peak_0 = heat_history[0].max()
    peak_end = heat_history[-1].max()
    print(f"\n峰值衰减: {peak_0:.2f} → {peak_end[0] if isinstance(peak_end, np.ndarray) else peak_end:.4f}")
    print(f"[解读] 热方程是'扩散'——初始尖锐信号随时间平滑化。")
    print(f"       熵不减（不可逆）。这就是为什么热量不会自发聚集。")

    print("\n" + "=" * 60)
    print("实验 2：一维波动方程 ∂²u/∂t² = c² ∂²u/∂x²")
    print("=" * 60)

    x_w, wave_history, r_wave = solve_wave_1d(nx=100, nt=500, c=1.0,
                                                dx=0.1, dt=0.05, init_type='plucked')

    print(f"网格: 100 点, 500 时间步")
    print(f"CFL 数 r = cΔt/Δx = {r_wave:.3f}（稳定要求 ≤ 1）{'✓' if r_wave <= 1 else '✗'}")
    print(f"初始条件: 拨弦（三角形位移, 初始速度=0）")
    print(f"边界条件: u(0)=u(L)=0（固定端，类似吉他弦）")

    # 能量守恒检查
    energy_0 = np.sum(wave_history[0]**2)
    energy_end = np.sum(wave_history[-1]**2)
    print(f"\n能量守恒检查: E₀={energy_0:.4f}, E_end={energy_end:.4f}（比值={energy_end/energy_0:.4f}）")
    print(f"[解读] 波动方程是'传播'——初始扰动沿弦传播，在端点反射。")
    print(f"       能量守恒（时间可逆）——与热方程的根本区别。")

    print("\n" + "=" * 60)
    print("实验 3：热方程 vs 波动方程（扩散 vs 传播的对比）")
    print("=" * 60)

    print(f"{'性质':<15} {'热方程':<20} {'波动方程'}")
    print("-" * 55)
    print(f"{'阶数':<15} {'一阶时间导':<20} {'二阶时间导'}")
    print(f"{'时间可逆性':<15} {'不可逆（扩散）':<20} {'可逆（传播）'}")
    print(f"{'能量':<15} {'衰减（耗散）':<20} {'守恒'}")
    print(f"{'稳态':<15} {'u→常数（平衡）':<20} {'持续振荡'}")
    print(f"{'平滑性':<15} {'瞬时平滑化':<20} {'保持正则性'}")
    print(f"{'CFL 条件':<15} {'r≤0.5':<20} {'r≤1'}")

    print(f"\n[解读] 热方程和波动方程是 PDE 的两大原型。")
    print(f"       前者描述'耗散'（热传导/扩散/布朗运动），")
    print(f"       后者描述'传播'（波/电磁场/引力）.")

    print("\n" + "=" * 60)
    print("实验 4：二维热传导（中心热源扩散）")
    print("=" * 60)

    x2, y2, heat2d_history, r2d = solve_heat_2d(nx=50, ny=50, nt=300)

    print(f"网格: 50×50, 300 时间步")
    print(f"CFL 数 r = {r2d:.3f}")
    print(f"初始: 中心 6×6 热源 = 1.0, 其余 = 0")
    print(f"最终温度范围: [{heat2d_history[-1].min():.4f}, {heat2d_history[-1].max():.4f}]")
    print(f"[解读] 二维热扩散展示各向同性——热量均匀向四周扩散。")

    # ============ 3. 可视化 ============
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    # 图 1：热方程时间演化（多时刻快照）
    ax = axes[0, 0]
    snapshots = [0, 5, 20, 50, 100, -1]
    labels = ['t=0', f't={5*10*0.01:.1f}', f't={20*10*0.01:.1f}',
              f't={50*10*0.01:.1f}', f't={100*10*0.01:.1f}', '最终']
    colors = plt.cm.hot(np.linspace(0.2, 0.9, len(snapshots)))
    for i, (snap, label, color) in enumerate(zip(snapshots, labels, colors)):
        ax.plot(x, heat_history[snap], color=color, lw=1.5, label=label)
    ax.set_xlabel('位置 x')
    ax.set_ylabel('温度 u')
    ax.set_title('热方程：脉冲扩散（时间演化）')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # 图 2：波动方程时间演化
    ax = axes[0, 1]
    for i, (snap, label, color) in enumerate(zip(snapshots, labels, colors)):
        ax.plot(x_w, wave_history[snap], color=color, lw=1.5, label=label)
    ax.set_xlabel('位置 x')
    ax.set_ylabel('位移 u')
    ax.set_title('波动方程：弦的振动（时间演化）')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # 图 3：热方程时空图（瀑布图）
    ax = axes[0, 2]
    im = ax.imshow(heat_history[::2], aspect='auto', origin='lower',
                   extent=[0, x[-1], 0, 500*0.01], cmap='hot')
    ax.set_xlabel('位置 x')
    ax.set_ylabel('时间 t')
    ax.set_title('热方程时空图（颜色=温度）')
    plt.colorbar(im, ax=ax, label='温度')

    # 图 4-6：二维热扩散快照
    for idx, t_idx in enumerate([0, len(heat2d_history)//3, -1]):
        ax = axes[1, idx]
        im = ax.imshow(heat2d_history[t_idx], origin='lower', cmap='hot',
                       extent=[0, x2[-1], 0, y2[-1]], vmin=0, vmax=1)
        t_label = '初始' if t_idx == 0 else '中间' if idx == 1 else '最终'
        ax.set_title(f'二维热扩散（{t_label}）')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        plt.colorbar(im, ax=ax, label='温度')

    plt.tight_layout()
    plt.savefig("14-PDE热传导与波动_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 14-PDE热传导与波动_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 热方程（抛物型）：扩散、耗散、不可逆、平滑化")
    print("2. 波动方程（双曲型）：传播、守恒、可逆、振荡")
    print("3. 有限差分法：用差分替代微分，显式格式简单但有 CFL 限制")
    print("4. CFL 条件：显式格式的时间步长受空间步长限制")
    print("\n[解读] PDE 是'连续物理'的数学语言——")
    print("       从热量扩散到电磁波到引力波，都用 PDE 描述。")
    print("       理解热方程=理解扩散；理解波动=理解传播。")
    print("       这两个方程是所有 PDE 的原型（Laplace/Poisson/Schrodinger 都是变体）。")


if __name__ == "__main__":
    main()
