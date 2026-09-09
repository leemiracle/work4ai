"""
微分几何：曲线、曲率与测地线
================================
数学概念：参数曲线 / Frenet 标架 / 曲率 / 挠率 / 测地线 / 高斯曲率 / Gauss 绝妙定理
应用领域：广义相对论 / 计算机图形学 / 机器人路径规划 / 弹性力学 / 地图投影
核心思想：微分几何用微积分研究弯曲空间。
  参数曲线 γ(t)：切向量 T = γ'/|γ'|，曲率 κ = |T'|/|γ'|
  Frenet 标架：{T, N, B}（切/法/副法），满足 Frenet-Serret 方程
  高斯曲率：K = κ₁ × κ₂（两主曲率乘积，内蕴量）
  Gauss 绝妙定理：K 可由第一基本形式（度量）完全决定 → 弯曲是内蕴的
  测地线：曲面上"最短路径"（局部距离极小）
运行方式：python "21-微分几何_曲线与曲面.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 曲线微分几何 ============

def frenet_frame(gamma, t):
    """计算 Frenet 标架 {T, N, B} 和曲率/挠率。
    gamma(t): 3D 参数曲线
    返回：T, N, B, curvature, torsion 数组
    """
    # 数值微分
    dt = t[1] - t[0]
    d1 = np.gradient(gamma, dt, axis=0)   # γ'(t)
    d2 = np.gradient(d1, dt, axis=0)      # γ''(t)
    d3 = np.gradient(d2, dt, axis=0)      # γ'''(t)

    speed = np.linalg.norm(d1, axis=1)
    T = d1 / speed[:, np.newaxis]          # 单位切向量

    curvature = np.zeros(len(t))
    torsion = np.zeros(len(t))
    N = np.zeros_like(T)
    B = np.zeros_like(T)

    for i in range(len(t)):
        if speed[i] < 1e-10:
            continue
        # 曲率 κ = |γ' × γ''| / |γ'|³
        cross = np.cross(d1[i], d2[i])
        curvature[i] = np.linalg.norm(cross) / speed[i]**3

        if curvature[i] > 1e-10:
            # 法向量 N = (T' / |T'|)
            T_prime = np.gradient(T, dt, axis=0)[i]
            N[i] = T_prime / np.linalg.norm(T_prime) if np.linalg.norm(T_prime) > 1e-10 else T[i]
            # 副法向量 B = T × N
            B[i] = np.cross(T[i], N[i])

            # 挠率 τ = (γ' × γ'') · γ''' / |γ' × γ''|²
            cross_norm_sq = np.linalg.norm(cross)**2
            if cross_norm_sq > 1e-10:
                torsion[i] = np.dot(cross, d3[i]) / cross_norm_sq

    return T, N, B, curvature, torsion


# ============ 2. 曲面几何 ============

def surface_curvature(func, u_range, v_range, nu=50, nv=50):
    """计算参数曲面 S(u,v) 的高斯曲率和平均曲率。
    func(u,v): 返回 (x,y,z) 的参数化函数
    返回：高斯曲率 K, 平均曲率 H 的网格
    """
    u = np.linspace(*u_range, nu)
    v = np.linspace(*v_range, nv)
    U, V = np.meshgrid(u, v)

    X, Y, Z = func(U, V)

    # 数值偏导
    du = u[1] - u[0]
    dv = v[1] - v[0]

    Xu, Yu, Zu = [np.gradient(arr, du, axis=1) for arr in [X, Y, Z]]
    Xv, Yv, Zv = [np.gradient(arr, dv, axis=0) for arr in [X, Y, Z]]
    Xuu, Yuu, Zuu = [np.gradient(arr, du, axis=1) for arr in [Xu, Yu, Zu]]
    Xuv, Yuv, Zuv = [np.gradient(arr, dv, axis=0) for arr in [Xu, Yu, Zu]]
    Xvv, Yvv, Zvv = [np.gradient(arr, dv, axis=0) for arr in [Xv, Yv, Zv]]

    # 第一基本形式 E, F, G
    E = Xu**2 + Yu**2 + Zu**2
    F = Xu*Xv + Yu*Yv + Zu*Zv
    G = Xv**2 + Yv**2 + Zv**2

    # 法向量
    cross_x = Yu*Zv - Zu*Yv
    cross_y = Zu*Xv - Xu*Zv
    cross_z = Xu*Yv - Yu*Xv
    cross_norm = np.sqrt(cross_x**2 + cross_y**2 + cross_z**2)

    # 第二基本形式 L, M, N
    L = (Xuu*cross_x + Yuu*cross_y + Zuu*cross_z) / cross_norm
    M_coeff = (Xuv*cross_x + Yuv*cross_y + Zuv*cross_z) / cross_norm
    N_coeff = (Xvv*cross_x + Yvv*cross_y + Zvv*cross_z) / cross_norm

    # 高斯曲率 K = (LN - M²) / (EG - F²)
    denom = E * G - F**2
    denom = np.where(np.abs(denom) < 1e-10, 1e-10, denom)
    K = (L * N_coeff - M_coeff**2) / denom

    # 平均曲率 H = (EN + GL - 2FM) / (2(EG - F²))
    H = (E * N_coeff + G * L - 2 * F * M_coeff) / (2 * denom)

    return U, V, K, H


# ============ 3. 经典曲线/曲面 ============

def helix(t):
    """螺旋线 γ(t) = (cos t, sin t, 0.3t)"""
    return np.column_stack([np.cos(t), np.sin(t), 0.3 * t])

def torus(u, v, R=2, r=0.7):
    """环面参数化"""
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return x, y, z

def sphere(u, v):
    """球面参数化"""
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    return x, y, z

def saddle(u, v):
    """马鞍面 z = x² - y²"""
    return u, v, u**2 - v**2


# ============ 4. 实验 ============

def main():
    print("=" * 60)
    print("实验 1：螺旋线——Frenet 标架与曲率")
    print("=" * 60)

    t = np.linspace(0, 6 * np.pi, 500)
    gamma = helix(t)
    T, N, B, kappa, tau = frenet_frame(gamma, t)

    # 理论值
    r_helix, a_helix = 1.0, 0.3
    kappa_theory = r_helix / (r_helix**2 + a_helix**2)
    tau_theory = a_helix / (r_helix**2 + a_helix**2)

    kappa_empirical = np.mean(kappa[10:-10])
    tau_empirical = np.mean(tau[10:-10])

    print(f"螺旋线: γ(t) = (cos t, sin t, {a_helix}t)")
    print(f"理论曲率 κ = r/(r²+a²) = {kappa_theory:.4f}")
    print(f"数值曲率 κ ≈ {kappa_empirical:.4f}")
    print(f"理论挠率 τ = a/(r²+a²) = {tau_theory:.4f}")
    print(f"数值挠率 τ ≈ {tau_empirical:.4f}")
    print(f"\n[解读] 曲率 = 偏离直线的程度（直线 κ=0）；")
    print(f"       挠率 = 偏离平面的程度（平面曲线 τ=0）。")
    print(f"       螺旋线的 κ 和 τ 都是常数——最均匀的 3D 曲线。")

    print("\n" + "=" * 60)
    print("实验 2：高斯曲率——曲面的内蕴几何")
    print("=" * 60)

    surfaces = {
        '球面（K>0 椭圆点）': (sphere, (0, 2*np.pi), (0.01, np.pi-0.01), 1.0),
        '环面（K 可正可负）': (torus, (0, 2*np.pi), (0, 2*np.pi), None),
        '马鞍面（K<0 双曲点）': (saddle, (-1.5, 1.5), (-1.5, 1.5), -4.0),
    }

    for name, (func, ur, vr, K_expected) in surfaces.items():
        U, V, K, H = surface_curvature(func, ur, vr)
        K_mean = np.nanmean(K)
        K_range = (np.nanmin(K), np.nanmax(K))
        print(f"\n{name}:")
        print(f"  K 范围: [{K_range[0]:.3f}, {K_range[1]:.3f}]")
        print(f"  K 均值: {K_mean:.3f}")
        if K_expected is not None:
            print(f"  理论 K = {K_expected:.1f}")

    print(f"\n[解读] 高斯曲率 K = κ₁ × κ₂（两个主曲率乘积）：")
    print(f"  K > 0：椭圆点（球面/碗形）——两个主曲率同号")
    print(f"  K = 0：抛物点（柱面/平面）——至少一个主曲率为零")
    print(f"  K < 0：双曲点（马鞍/薯片）——两个主曲率异号")

    print("\n" + "=" * 60)
    print("实验 3：Gauss 绝妙定理——弯曲是内蕴的")
    print("=" * 60)

    print("Gauss 绝妙定理（Theorema Egregium, 1827）：")
    print("  高斯曲率 K 完全由第一基本形式（度量）决定。")
    print("  → K 是内蕴量：曲面上的'居民'不离开曲面就能测量 K。")
    print()
    print("推论：")
    print("  • 球面（K=1/R²>0）无法等距映射到平面（K=0）")
    print("    → 这就是为什么地图投影必然扭曲！")
    print("  • 圆柱面（K=0）可以展开成平面（卷纸展开）")
    print("  • 披萨定理：折叠披萨让它不弯曲（利用 K=0 方向）")
    print()
    print("爱因斯坦的推广：")
    print("  广义相对论：引力 = 时空的高斯曲率")
    print("  质量弯曲时空 → 光沿测地线传播 → 我们感知为'引力'")

    print("\n" + "=" * 60)
    print("实验 4：测地线——曲面上的'直线'")
    print("=" * 60)

    print("测地线：曲面上局部最短的曲线。")
    print("  球面上的测地线 = 大圆（赤道/经线）")
    print("  平面上的测地线 = 直线")
    print("  圆柱面上的测地线 = 螺旋线（展开后是直线）")
    print()
    print("测地线方程（用 Christoffel 符号 Γ）：")
    print("  d²x^k/dt² + Γ^k_ij (dx^i/dt)(dx^j/dt) = 0")
    print()
    print("[解读] 测地线是弯曲空间中'惯性运动'的推广。")
    print("       飞机跨洋航线走大圆（不是直线！）——因为地球是球面。")

    # ============ 5. 可视化 ============
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    # 图 1：螺旋线 3D + Frenet 标架
    ax = axes[0, 0]
    ax.plot(gamma[:, 0], gamma[:, 1], 'b-', lw=2)
    # 画标架（2D 投影）
    for idx in range(0, len(t), 50):
        pos = gamma[idx, :2]
        ax.quiver(pos[0], pos[1], T[idx, 0], T[idx, 1], color='red', scale=15, width=0.003)
        ax.quiver(pos[0], pos[1], N[idx, 0], N[idx, 1], color='green', scale=20, width=0.003)
    ax.set_title('螺旋线（俯视）+ T(红)/N(绿) 标架')
    ax.set_aspect('equal')
    ax.grid(alpha=0.3)

    # 图 2：曲率/挠率沿弧长
    ax = axes[0, 1]
    arc = np.cumsum(np.linalg.norm(np.diff(gamma, axis=0), axis=1))
    arc = np.insert(arc, 0, 0)
    ax.plot(arc, kappa, 'b-', lw=2, label=f'κ（理论={kappa_theory:.3f}）')
    ax.plot(arc, tau, 'r-', lw=2, label=f'τ（理论={tau_theory:.3f}）')
    ax.axhline(kappa_theory, color='blue', ls='--', alpha=0.3)
    ax.axhline(tau_theory, color='red', ls='--', alpha=0.3)
    ax.set_xlabel('弧长 s')
    ax.set_ylabel('κ / τ')
    ax.set_title('螺旋线的曲率与挠率（常数）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 3-5：三个曲面的高斯曲率
    for idx, (name, (func, ur, vr, _)) in enumerate(surfaces.items()):
        ax = axes[0 if idx < 2 else 1, 2 if idx < 2 else idx - 2]
        if idx == 2:
            ax = axes[1, 0]
        U, V, K, H = surface_curvature(func, ur, vr, nu=40, nv=40)
        im = ax.pcolormesh(U, V, K, cmap='RdBu_r', shading='auto',
                           vmin=-np.nanmax(np.abs(K)), vmax=np.nanmax(np.abs(K)))
        ax.set_title(f'{name}：高斯曲率 K')
        ax.set_xlabel('u')
        ax.set_ylabel('v')
        plt.colorbar(im, ax=ax)

    # 图 6：曲率分类图
    ax = axes[1, 2]
    ax.text(0.5, 0.85, '高斯曲率分类', ha='center', fontsize=14, fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.5, 0.70, 'K > 0 椭圆点\n（球面/碗）\n两个主曲率同号',
            ha='center', fontsize=10, color='blue', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    ax.text(0.5, 0.43, 'K = 0 抛物点\n（柱面/平面）\n至少一个主曲率为零',
            ha='center', fontsize=10, color='gray', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    ax.text(0.5, 0.15, 'K < 0 双曲点\n（马鞍/薯片）\n两个主曲率异号',
            ha='center', fontsize=10, color='red', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("21-微分几何_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 21-微分几何_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. Frenet 标架 {T,N,B}：完全描述 3D 曲线的几何")
    print("2. 曲率 κ：偏离直线的程度；挠率 τ：偏离平面的程度")
    print("3. 高斯曲率 K=κ₁κ₂：正（碗）/零（柱）/负（马鞍）")
    print("4. Gauss 绝妙定理：K 是内蕴的（不需嵌入即可测量）")
    print("5. 测地线：弯曲空间的'直线'，广义相对论的轨道")
    print("\n[解读] 微分几何是'弯曲空间的微积分'——")
    print("       从地图投影到广义相对论到机器人路径规划，")
    print("       Gauss 的洞见（弯曲是内蕴的）改变了物理学。")


if __name__ == "__main__":
    main()
