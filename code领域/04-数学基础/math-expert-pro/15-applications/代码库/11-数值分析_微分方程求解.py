"""
数值分析：常微分方程的数值解法
================================
数学概念：常微分方程 ODE / 欧拉法 / Runge-Kutta 法 / 收敛阶 / 稳定性
应用领域：物理仿真 / 工程计算 / 流体力学 / 控制系统 / 电路分析
核心思想：ODE y'=f(t,y) 的解析解常常不存在，用数值方法离散化求解。
  欧拉法（1阶）：y_{n+1} = y_n + h·f(t_n, y_n)  局部截断误差 O(h²)
  RK4（4阶龙格-库塔）：
    k1 = f(t_n, y_n)
    k2 = f(t_n + h/2, y_n + h·k1/2)
    k3 = f(t_n + h/2, y_n + h·k2/2)
    k4 = f(t_n + h, y_n + h·k3)
    y_{n+1} = y_n + (h/6)(k1 + 2k2 + 2k3 + k4)  局部截断误差 O(h⁵)
  收敛阶：误差 ~ C·h^p（p=1欧拉, p=4 RK4）
运行方式：python "11-数值分析_微分方程求解.py"
依赖：numpy, matplotlib, scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 数值方法实现 ============

def euler_method(f, t0, y0, t_end, h):
    """前向欧拉法（1阶）。y_{n+1} = y_n + h*f(t_n, y_n)
    最简单但精度低，仅用于教学对比。
    """
    t = np.arange(t0, t_end + h, h)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        y[i + 1] = y[i] + h * f(t[i], y[i])
    return t, y


def rk4_method(f, t0, y0, t_end, h):
    """4阶 Runge-Kutta 法（RK4）。标准数值 ODE 求解器。
    用 4 个斜率的加权平均，精度 O(h^4)。
    """
    t = np.arange(t0, t_end + h, h)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        k1 = f(t[i], y[i])
        k2 = f(t[i] + h / 2, y[i] + h * k1 / 2)
        k3 = f(t[i] + h / 2, y[i] + h * k2 / 2)
        k4 = f(t[i] + h, y[i] + h * k3)
        y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


def rk2_method(f, t0, y0, t_end, h):
    """2阶 Runge-Kutta（中点法）。精度 O(h^2)，介于欧拉和 RK4 之间。"""
    t = np.arange(t0, t_end + h, h)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        k1 = f(t[i], y[i])
        k2 = f(t[i] + h / 2, y[i] + h * k1 / 2)
        y[i + 1] = y[i] + h * k2
    return t, y


# ============ 2. 实验与可视化 ============

def main():
    # ============================================================
    # 案例 1：指数增长 y' = y, y(0)=1（解析解 y=e^t）
    # 案例 2：钟摆 y'' + sin(y) = 0（非线性，无解析解）
    # ============================================================

    # ---- 案例 1：线性 ODE（有解析解，验证精度）----
    print("=" * 60)
    print("案例 1：y' = y, y(0)=1（解析解 y = e^t，验证数值精度）")
    print("=" * 60)

    f1 = lambda t, y: y  # y' = y
    t0, y0, t_end = 0, 1, 3
    t_exact = np.linspace(t0, t_end, 300)
    y_exact = np.exp(t_exact)

    # 不同步长对比
    print(f"\n{'步长 h':<10} {'欧拉误差':<14} {'RK2误差':<14} {'RK4误差':<14} {'RK4/欧拉':<10}")
    print("-" * 62)

    hs = [0.5, 0.1, 0.05, 0.01]
    errors = {'euler': [], 'rk2': [], 'rk4': []}

    for h in hs:
        t_e, y_e = euler_method(f1, t0, y0, t_end, h)
        t_rk2, y_rk2 = rk2_method(f1, t0, y0, t_end, h)
        t_rk4, y_rk4 = rk4_method(f1, t0, y0, t_end, h)

        # 误差 vs 解析解
        err_e = abs(y_e[-1] - np.exp(t_end))
        err_rk2 = abs(y_rk2[-1] - np.exp(t_end))
        err_rk4 = abs(y_rk4[-1] - np.exp(t_end))

        errors['euler'].append(err_e)
        errors['rk2'].append(err_rk2)
        errors['rk4'].append(err_rk4)

        ratio = err_rk4 / err_e if err_e > 0 else 0
        print(f"{h:<10.3f} {err_e:<14.6e} {err_rk2:<14.6e} {err_rk4:<14.6e} {ratio:<10.6f}")

    # 验证收敛阶
    print("\n收敛阶验证（误差 ~ C·h^p）：")
    for method, name in [('euler', '欧拉'), ('rk2', 'RK2'), ('rk4', 'RK4')]:
        errs = errors[method]
        # log(误差比) / log(步长比) ≈ 收敛阶
        p = np.log(errs[-2] / errs[-1]) / np.log(hs[-2] / hs[-1])
        print(f"  {name}: 收敛阶 p ≈ {p:.2f}（理论值: {1 if method=='euler' else 2 if method=='rk2' else 4}）")

    print("\n[解读] 欧拉法 1 阶（误差 ~h¹），RK2 2 阶（~h²），RK4 4 阶（~h⁴）。")
    print("       步长减半时：欧拉误差减半，RK4 误差减 16 倍。RK4 用同样步长精度高得多。")

    # ---- 案例 2：非线性钟摆（无解析解）----
    print("\n" + "=" * 60)
    print("案例 2：非线性钟摆 θ'' + sin(θ) = 0（无解析解）")
    print("=" * 60)

    # 转为一阶方程组：y=[θ, ω], y'=[ω, -sin(θ)]
    def pendulum(t, y):
        theta, omega = y
        return np.array([omega, -np.sin(theta)])

    y0_pend = np.array([np.pi / 3, 0])  # 初始角度 60°，初速 0
    t_end_pend = 10
    h_pend = 0.01

    # 用 RK4 求解（向量版）
    t_p = np.arange(0, t_end_pend + h_pend, h_pend)
    y_p = np.zeros((len(t_p), 2))
    y_p[0] = y0_pend
    for i in range(len(t_p) - 1):
        k1 = pendulum(t_p[i], y_p[i])
        k2 = pendulum(t_p[i] + h_pend / 2, y_p[i] + h_pend * k1 / 2)
        k3 = pendulum(t_p[i] + h_pend / 2, y_p[i] + h_pend * k2 / 2)
        k4 = pendulum(t_p[i] + h_pend, y_p[i] + h_pend * k3)
        y_p[i + 1] = y_p[i] + (h_pend / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    # 用 scipy solve_ivp（高精度参考解）
    sol = solve_ivp(pendulum, [0, t_end_pend], y0_pend, method='DOP853',
                    t_eval=t_p, rtol=1e-12, atol=1e-12)

    # 小角度近似（θ≈sin θ → 简谐运动）
    omega_small = np.sqrt(1)  # g/L=1
    theta_small = y0_pend[0] * np.cos(omega_small * t_p)

    err_vs_scipy = np.max(np.abs(y_p[:, 0] - sol.y[0]))
    err_vs_small = np.max(np.abs(y_p[:, 0] - theta_small))

    print(f"初始角度: {y0_pend[0]:.4f} rad = {np.degrees(y0_pend[0]):.1f}°")
    print(f"步长: {h_pend}")
    print(f"RK4 vs scipy(DOP853) 最大误差: {err_vs_scipy:.2e}")
    print(f"非线性解 vs 小角度近似 最大偏差: {err_vs_small:.4f} rad = {np.degrees(err_vs_small):.2f}°")
    print(f"\n[解读] 初始 60° 时，小角度近似（简谐运动）偏差显著。")
    print(f"       非线性效应使周期变长（大振幅摆得更慢）。")
    print(f"       这就是为什么钟摆设计要控制振幅——大角度非线性效应影响计时精度。")

    # ---- 案例 3：稳定性——刚性问题 ----
    print("\n" + "=" * 60)
    print("案例 3：数值稳定性（刚性方程 y' = -1000y + 999e^{-t}）")
    print("=" * 60)

    f_stiff = lambda t, y: -1000 * y + 999 * np.exp(-t)
    y0_stiff = 0
    # 解析解：y = e^{-t} - e^{-1000t}（快瞬态 + 慢衰减）

    print(f"解析解: y(t) = e^(-t) - e^(-1000t)")
    print(f"  快分量 e^(-1000t) 在 t<0.005 后消失")
    print(f"  慢分量 e^(-t) 主导长期行为\n")

    # 显式方法需要 h < 2/1000 = 0.002 才稳定
    print(f"{'步长 h':<10} {'欧拉稳定?':<12} {'RK4稳定?':<12} {'终值误差'}")
    print("-" * 50)
    for h in [0.001, 0.0015, 0.002, 0.005, 0.01]:
        t_s, y_euler = euler_method(f_stiff, 0, y0_stiff, 0.1, h)
        _, y_rk4 = rk4_method(f_stiff, 0, y0_stiff, 0.1, h)
        y_true = np.exp(-0.1) - np.exp(-100)
        stable_e = "✓" if abs(y_euler[-1]) < 10 else "✗ 爆炸"
        stable_r = "✓" if abs(y_rk4[-1]) < 10 else "✗ 爆炸"
        err = abs(y_rk4[-1] - y_true) if stable_r == "✓" else float('nan')
        print(f"{h:<10.4f} {stable_e:<12} {stable_r:<12} {err:.2e}")

    print(f"\n[解读] 刚性方程的显式方法步长受快分量限制（h<2/λ_max）。")
    print(f"       超过临界步长→数值解爆炸（不稳定）。")
    print(f"       这就是为什么刚性方程要用隐式方法（BDF/隐式RK）。")

    # ============ 3. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：y'=y 的三种方法对比
    ax = axes[0, 0]
    h_demo = 0.5
    t_e, y_e = euler_method(f1, t0, y0, t_end, h_demo)
    t_rk2, y_rk2 = rk2_method(f1, t0, y0, t_end, h_demo)
    t_rk4, y_rk4 = rk4_method(f1, t0, y0, t_end, h_demo)
    ax.plot(t_exact, y_exact, 'k-', lw=2, label='解析解 e^t')
    ax.plot(t_e, y_e, 'rs--', lw=1.5, markersize=8, label=f'欧拉 (h={h_demo})')
    ax.plot(t_rk2, y_rk2, 'g^--', lw=1.5, markersize=8, label=f'RK2 (h={h_demo})')
    ax.plot(t_rk4, y_rk4, 'bo--', lw=1.5, markersize=8, label=f'RK4 (h={h_demo})')
    ax.set_xlabel('t')
    ax.set_ylabel('y')
    ax.set_title("y'=y 的数值解对比（大步长看精度差异）")
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 2：收敛阶（log-log 图）
    ax = axes[0, 1]
    ax.loglog(hs, errors['euler'], 'rs-', lw=2, markersize=8, label='欧拉 (p≈1)')
    ax.loglog(hs, errors['rk2'], 'g^-', lw=2, markersize=8, label='RK2 (p≈2)')
    ax.loglog(hs, errors['rk4'], 'bo-', lw=2, markersize=8, label='RK4 (p≈4)')
    # 参考线
    ax.loglog(hs, [hs[0]**1 * errors['euler'][0]/hs[0]] * len(hs), 'r:', alpha=0.3)
    ax.loglog(hs, [h**4 * errors['rk4'][0]/hs[0]**4 for h in hs], 'b:', alpha=0.3)
    ax.set_xlabel('步长 h')
    ax.set_ylabel('终值误差')
    ax.set_title('收敛阶：log-log 图（斜率=收敛阶 p）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 3：非线性钟摆
    ax = axes[1, 0]
    ax.plot(t_p, np.degrees(y_p[:, 0]), 'b-', lw=2, label='非线性解 (RK4)')
    ax.plot(t_p, np.degrees(theta_small), 'r--', lw=2, label='小角度近似（简谐）')
    ax.set_xlabel('时间 t')
    ax.set_ylabel('角度 θ (度)')
    ax.set_title('非线性钟摆 vs 小角度近似（初始60°）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：相空间（θ vs ω）
    ax = axes[1, 1]
    ax.plot(y_p[:, 0], y_p[:, 1], 'b-', lw=1.5)
    ax.plot(y_p[0, 0], y_p[0, 1], 'go', markersize=10, label='起点')
    ax.set_xlabel('角度 θ (rad)')
    ax.set_ylabel('角速度 ω (rad/s)')
    ax.set_title('钟摆相空间轨迹（闭合曲线=周期运动）')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig("11-数值分析_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 11-数值分析_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 欧拉法 1 阶（O(h)），RK2 2 阶（O(h²)），RK4 4 阶（O(h⁴)）")
    print("2. 收敛阶用 log-log 图验证：斜率 = 阶数 p")
    print("3. 非线性方程（钟摆）无解析解，数值方法是唯一手段")
    print("4. 刚性方程需隐式方法（显式方法步长受限）")
    print("5. 相空间可视化揭示动力学结构（周期/混沌/吸引子）")
    print("\n[解读] 数值分析是'连续数学'到'离散计算'的桥梁——")
    print("       微分方程、积分、优化都靠它落地到计算机。")
    print("       RK4 是科学与工程仿真的事实标准（物理引擎/电路仿真/CFD）。")


if __name__ == "__main__":
    main()
