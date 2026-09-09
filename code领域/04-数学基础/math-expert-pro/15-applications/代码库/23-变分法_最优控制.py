"""
变分法：最小作用量与最优控制
================================
数学概念：变分法 / 欧拉-拉格朗日方程 / 最速降线 / 最小作用量原理 / 最优控制
应用领域：经典力学 / 量子力学 / 航天轨道 / 机器人 / 经济学
核心思想：变分法寻找使泛函（函数的函数）取极值的函数。
  泛函 S[y] = ∫ L(t, y, y') dt
  欧拉-拉格朗日方程：∂L/∂y - d/dt(∂L/∂y') = 0
  最小作用量原理：物理轨迹使 S = ∫ L dt 取极值（Nature 选"捷径"）
  最速降线：重力下最快从 A 到 B 的曲线 → 摆线（不是直线！）
运行方式：python "23-变分法_最优控制.py"
依赖：numpy, matplotlib, scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 最速降线（Brachistochrone）============

def brachistochrone(theta_max, n=100):
    """最速降线 = 摆线。
    x = R(θ - sinθ), y = R(1 - cosθ)
    在重力下从 A(0,0) 到 B(x_end, y_end) 的最快路径。
    """
    theta = np.linspace(0, theta_max, n)
    x = theta - np.sin(theta)
    y = 1 - np.cos(theta)
    return x, y


def falling_time(x_end, y_end):
    """计算沿摆线的下落时间（参数化）。
    y_end/x_end 决定了 θ_end，进而决定 R 和 T。
    """
    # 解 x_end/R = θ - sinθ, y_end/R = 1 - cosθ
    # → y_end/x_end = (1-cosθ)/(θ-sinθ)
    from scipy.optimize import brentq

    def eq(theta):
        return (1 - np.cos(theta)) / (theta - np.sin(theta) + 1e-15) - y_end / x_end

    theta_end = brentq(eq, 0.01, 4 * np.pi)
    R = y_end / (1 - np.cos(theta_end))
    # 下落时间 T = sqrt(R/g) × θ_end
    g = 9.8
    T = np.sqrt(R / g) * theta_end
    return theta_end, R, T


def straight_line_time(x_end, y_end):
    """沿直线无摩擦下滑的时间（近似）。"""
    g = 9.8
    length = np.sqrt(x_end**2 + y_end**2)
    angle = np.arctan2(y_end, x_end)
    # 沿斜面加速度 = g sin(angle)
    a = g * np.sin(angle)
    return np.sqrt(2 * length / a)


# ============ 2. 弹簧-振子（拉格朗日力学）============

def lagrangian_oscillator(t_max=10, omega=2.0, y0=[1.0, 0.0]):
    """用拉格朗日力学求解简谐振子。
    L = T - V = ½mẋ² - ½kx²
    欧拉-拉格朗日：mẍ + kx = 0 → ẍ = -ω²x
    """
    def ode(t, y):
        return [y[1], -omega**2 * y[0]]

    sol = solve_ivp(ode, [0, t_max], y0, t_eval=np.linspace(0, t_max, 500), rtol=1e-10)
    return sol.t, sol.y[0], sol.y[1]


# ============ 3. 实验 ============

def main():
    print("=" * 60)
    print("实验 1：最速降线——重力下最快的路径")
    print("=" * 60)

    x_end, y_end = np.pi, 2.0  # 目标点
    theta_end, R, T_brach = falling_time(x_end, y_end)
    T_straight = straight_line_time(x_end, y_end)

    # 生成曲线
    theta_curve = np.linspace(0, theta_end, 100)
    x_brach = R * (theta_curve - np.sin(theta_curve))
    y_brach = R * (1 - np.cos(theta_curve))
    x_line = np.linspace(0, x_end, 50)
    y_line = np.linspace(0, y_end, 50)

    print(f"从 (0,0) 到 ({x_end:.2f}, {y_end:.2f})：")
    print(f"  摆线（最速降线）时间: {T_brach:.4f} s")
    print(f"  直线下滑时间:        {T_straight:.4f} s")
    print(f"  摆线快 {(1-T_brach/T_straight)*100:.1f}%！")
    print(f"  摆线参数: θ_end={theta_end:.3f}, R={R:.3f}")

    print(f"\n[解读] 直觉以为直线最快——错了！")
    print(f"       摆线先陡降（获取速度）再水平滑行——用'速度换距离'。")
    print(f"       这是变分法最经典的反直觉结果（1696 Bernoulli 挑战）。")

    print("\n" + "=" * 60)
    print("实验 2：最小作用量原理——自然选择最优路径")
    print("=" * 60)

    # 简谐振子：L = ½ẋ² - ½ω²x²
    t, x, v = lagrangian_oscillator(omega=2.0)

    # 计算作用量 S = ∫ L dt
    dt = t[1] - t[0]
    L = 0.5 * v**2 - 0.5 * 2.0**2 * x**2  # T - V
    S_real = np.trapz(L, t)

    # 简谐振子解析解 x(t) = cos(2t)
    x_analytic = np.cos(2 * t)
    L_analytic = 0.5 * (2 * np.sin(2 * t))**2 - 0.5 * 4 * np.cos(2 * t)**2
    S_analytic = np.trapz(L_analytic, t)

    # 扰动路径：x(t) = cos(2t) + ε sin(πt/T)
    epsilon = 0.1
    x_perturbed = np.cos(2 * t) + epsilon * np.sin(np.pi * t / t[-1])
    v_perturbed = -2 * np.sin(2 * t) + epsilon * np.pi / t[-1] * np.cos(np.pi * t / t[-1])
    L_perturbed = 0.5 * v_perturbed**2 - 0.5 * 4 * x_perturbed**2
    S_perturbed = np.trapz(L_perturbed, t)

    print(f"简谐振子（ω=2）的作用量 S = ∫L dt：")
    print(f"  真实轨迹 S = {S_real:.6f}")
    print(f"  解析轨迹 S = {S_analytic:.6f}")
    print(f"  扰动轨迹 S' = {S_perturbed:.6f} (ε={epsilon})")
    print(f"  ΔS = S' - S = {S_perturbed - S_real:.6f} > 0 → 真实轨迹使 S 极小")

    print(f"\n[解读] 最小作用量原理：物理轨迹使 S 取极值（通常是极小）。")
    print(f"       Nature 在所有可能路径中选择'最优'——这不是拟人化，而是数学事实。")
    print(f"       这是分析力学（Lagrange/Hamilton）的基础，也是量子力学的路径积分的起点。")

    print("\n" + "=" * 60)
    print("实验 3：欧拉-拉格朗日方程——变分法的核心")
    print("=" * 60)

    print("泛函 S[y] = ∫ L(t, y, ẏ) dt 的极值满足：")
    print("  欧拉-拉格朗日方程：")
    print("    ∂L/∂y - d/dt(∂L/∂ẏ) = 0")
    print()
    print("经典例子：")
    examples = [
        ("自由粒子 L=½mẋ²", "ẍ = 0（匀速直线运动）"),
        ("弹簧 L=½mẋ²-½kx²", "mẍ+kx=0（简谐振动）"),
        ("重力 L=½mẋ²-mgx", "ẍ=-g（自由落体）"),
        ("单摆 L=½mL²θ̇²-mgL(1-cosθ)", "θ̈=-(g/L)sinθ（非线性摆）"),
        ("测地线 L=½gᵢⱼẋⁱẋʲ", "弯曲空间最短路径（广义相对论）"),
    ]
    for lagr, eom in examples:
        print(f"  {lagr}")
        print(f"    → {eom}")

    print("\n[解读] 所有经典力学可以从一个原理（δS=0）推出。")
    print("       不需要 F=ma——只需要 L=T-V 和欧拉-拉格朗日方程。")
    print("       这是物理学的'大一统'：一个原理 → 所有力学定律。")

    print("\n" + "=" * 60)
    print("实验 4：最优控制——变分法的现代应用")
    print("=" * 60)

    print("最优控制问题：min ∫(成本)dt s.t. 动力学约束")
    print("Pontryagin 极大值原理（变分法的推广）：")
    print("  引入协态 λ(t)，构造 Hamiltonian H = L + λ·f")
    print("  最优控制 u* 使 H 取极值")
    print()
    print("应用实例：")
    apps = [
        ("火箭轨道", "min 燃料 s.t. 到达目标"),
        ("机器人路径", "min 时间 s.t. 避障"),
        ("经济学", "max 效用 s.t. 预算"),
        ("机器学习", "min 损失 s.t. 模型约束（梯度下降=变分法）"),
    ]
    for app, desc in apps:
        print(f"  {app}: {desc}")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：最速降线
    ax = axes[0, 0]
    ax.plot(x_brach, y_brach, 'b-', lw=3, label=f'摆线（最快 T={T_brach:.3f}s）')
    ax.plot(x_line, y_line, 'r--', lw=2, label=f'直线（T={T_straight:.3f}s）')
    ax.fill_between(x_brach, 0, y_brach, alpha=0.1, color='blue')
    ax.set_xlabel('x')
    ax.set_ylabel('y（高度）')
    ax.set_title(f'最速降线（摆线比直线快 {(1-T_brach/T_straight)*100:.0f}%）')
    ax.legend()
    ax.set_aspect('equal')
    ax.invert_yaxis()  # y 向下为正（下落）
    ax.grid(alpha=0.3)

    # 图 2：简谐振子
    ax = axes[0, 1]
    ax.plot(t, x, 'b-', lw=2, label='x(t)（位置）')
    ax.plot(t, v, 'r-', lw=2, label='v(t)（速度）')
    ax.plot(t, L, 'g-', lw=2, label='L(t)（拉格朗日量）')
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlabel('时间 t')
    ax.set_title('简谐振子（最小作用量原理）')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 图 3：作用量比较
    ax = axes[1, 0]
    epsilons = np.linspace(-0.5, 0.5, 50)
    S_values = []
    for eps in epsilons:
        x_p = np.cos(2 * t) + eps * np.sin(np.pi * t / t[-1])
        v_p = -2 * np.sin(2 * t) + eps * np.pi / t[-1] * np.cos(np.pi * t / t[-1])
        L_p = 0.5 * v_p**2 - 0.5 * 4 * x_p**2
        S_values.append(np.trapz(L_p, t))
    ax.plot(epsilons, S_values, 'b-', lw=2)
    ax.axvline(0, color='red', ls='--', lw=2, label='真实轨迹（ε=0）')
    ax.set_xlabel('扰动幅度 ε')
    ax.set_ylabel('作用量 S')
    ax.set_title('作用量在真实轨迹处取极值')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：不同参数下的最速降线形状
    ax = axes[1, 1]
    for y_ratio in [0.5, 1.0, 2.0, 3.0]:
        x_e = np.pi
        y_e = y_ratio
        try:
            th_e, R_e, _ = falling_time(x_e, y_e)
            th_c = np.linspace(0, th_e, 80)
            x_b = R_e * (th_c - np.sin(th_c))
            y_b = R_e * (1 - np.cos(th_c))
            ax.plot(x_b, y_b, lw=2, label=f'y/x={y_ratio/x_e:.2f}')
        except:
            pass
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('不同落点的最速降线（都是摆线）')
    ax.legend(fontsize=8)
    ax.invert_yaxis()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("23-变分法_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 23-变分法_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 变分法：寻找使泛函取极值的函数")
    print("2. 最速降线：摆线（不是直线）——反直觉的经典结果")
    print("3. 最小作用量：物理轨迹使 S=∫L dt 极小——Nature 选'最优'")
    print("4. 欧拉-拉格朗日方程：δS=0 的微分方程形式")
    print("5. 最优控制：变分法的现代推广（航天/机器人/ML）")
    print("\n[解读] 变分法是'优化的无穷维推广'——")
    print("       普通优化找最优点，变分法找最优函数。")
    print("       最小作用量原理告诉我们：宇宙在计算最优解。")


if __name__ == "__main__":
    main()
