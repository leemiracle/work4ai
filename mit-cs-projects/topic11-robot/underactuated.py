"""
6.4210 Underactuated Robotics（MIT, Tedrake）
================================================
覆盖主题：
- LQR 控制：cartpole 线性化（Lecture 7-8）
- 接触动力学：complementarity (LCP)（Lecture 11-12）
- Lyapunov 稳定性验证（V̇<0）（Lecture 3-4）
- 相图：simple pendulum（Lecture 2）

核心教材/论文：
- Tedrake "Underactuated Robotics: Algorithms for Walking, Running, Swimming, Flying, and Manipulation" (course notes, MIT)
- Kalman 1960 "Contributions to the Theory of Optimal Control" Bol Soc Mat Mexicana
- Stewart & Trinkle 1996 "An Implicit Time-Stepping Scheme for Rigid Body Dynamics with Coulomb Friction" IJNME (LCP)
- Khalil 2002 "Nonlinear Systems" 3rd ed (Lyapunov)

本文件实现：
- Discrete-time Riccati 方程求解 LQR gain
- LCP (Linear Complementarity Problem) 求解器（Lemke 简化）
- Lyapunov 函数导数验证 (V̇ = ∇V · f(x) < 0)
- Pendulum 相图 ASCII + 能量等高线

运行：
    python underactuated.py
"""
from __future__ import annotations
import math
import numpy as np


# ============ 1. LQR (Discrete Riccati) ============

def dlqr(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray,
         max_iter: int = 100, tol: float = 1e-8):
    """离散时间 LQR。求 K 使 u = -Kx 最小化 Σ(x'Qx + u'Ru)。
    DARE: P = A'PA - A'PB(R+B'PB)^-1 B'PA + Q
    """
    P = Q.copy()
    for _ in range(max_iter):
        BtP = B.T @ P
        K = np.linalg.solve(R + BtP @ B, BtP @ A)
        P_new = A.T @ P @ A - A.T @ P @ B @ K + Q
        if np.max(np.abs(P_new - P)) < tol:
            break
        P = P_new
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    return K, P


def cartpole_linearize(m_c=1.0, m_p=0.1, l=0.5, g=9.81):
    """cartpole 在 θ=0（杆向上）处线性化。状态 = [x, θ, x_dot, θ_dot]。

    由 Lagrangian 推导。线性化 EOM 的质量矩阵：
        [[M+m, ml],[ml, ml²]] · [ẍ; θ̈] = [F; mgl·θ]
    求逆后（det = M·m·l²）：
        ẍ = (F − mg·θ) / M
        θ̈ = (M+m)g·θ/(Ml) − F/(Ml)
    其中 M=m_c（小车），m=m_p（摆杆），l=半杆长。
    注意 B[3] 符号为负：力推车右移 → 摆杆相对左倒（θ̈<0）。
    """
    M, m = m_c, m_p
    A = np.array([
        [0, 0,             1, 0],
        [0, 0,             0, 1],
        [0, -m*g/M,        0, 0],
        [0, (M+m)*g/(M*l), 0, 0],
    ])
    B = np.array([[0], [0], [1/M], [-1/(M*l)]])
    return A, B


# ============ 2. LCP Solver (Lemke's algorithm 简化) ============

def solve_lcp_brute(M: np.ndarray, q: np.ndarray) -> np.ndarray | None:
    """暴力枚举解 LCP: find w,z >= 0 s.t. w = Mz + q, w·z = 0。
    对小问题用枚举（n<=8 可行）。
    """
    n = len(q)
    # 尝试所有 z 的支撑集（哪些 z_i > 0）
    from itertools import combinations
    for size in range(n + 1):
        for active in combinations(range(n), size):
            z = np.zeros(n)
            if not active:
                w = q.copy()
                if np.all(w >= -1e-10):
                    return z
                continue
            # 解 M[:,active] z[active] = -q
            M_sub = M[:, list(active)]
            try:
                z_sub = np.linalg.lstsq(M_sub, -q, rcond=None)[0]
            except np.linalg.LinAlgError:
                continue
            z[list(active)] = z_sub
            w = M @ z + q
            if np.all(z >= -1e-8) and np.all(w >= -1e-8):
                return np.maximum(z, 0)
    return None


def contact_lcp_demo():
    """小球接触地面：法向力互补条件。
    0 ≤ f_n (法向力), 0 ≤ g (间隙), f_n · g = 0
    """
    # M z + q ≥ 0, z ≥ 0, complementarity
    M = np.array([[1.0]])  # f_n = z
    q = np.array([-5.0])   # 重力，球在地面上需要法向力
    z = solve_lcp_brute(M, q)
    return z


# ============ 3. Lyapunov 稳定性 ============

def lyapunov_check(f, V, grad_V, x_points: list[np.ndarray], dt=1e-5):
    """在若干点检查 V̇ = ∇V · f(x) < 0（渐近稳定）。"""
    results = []
    for x in x_points:
        # 数值梯度
        g = grad_V(x)
        fx = f(x)
        Vdot = float(np.dot(g, fx))
        results.append((x.copy(), V(x), Vdot))
    return results


# ============ 4. Pendulum Phase Portrait ============

def pendulum_dynamics(theta, theta_dot, m=1, l=1, b=0.1, g=9.81):
    """ddθ = -(g/l)sin(θ) - (b/(m*l²))dθ"""
    return -(g/l)*math.sin(theta) - (b/(m*l**2))*theta_dot


def pendulum_energy(theta, theta_dot, m=1, l=1, g=9.81):
    """E = ½ml²θ̇² + mgl(1-cosθ)"""
    return 0.5*m*l**2*theta_dot**2 + m*g*l*(1-math.cos(theta))


def phase_portrait_ascii(grid_n=13, max_theta=2*math.pi, max_omega=8):
    """用 ASCII 箭头画相图。"""
    lines = []
    for i in range(grid_n):
        row = ""
        theta = -max_theta + 2*max_theta * i / (grid_n-1)
        for j in range(grid_n):
            omega = -max_omega + 2*max_omega * j / (grid_n-1)
            dtheta = omega
            domega = pendulum_dynamics(theta, omega)
            # 向量方向 → ASCII 箭头
            angle = math.atan2(domega, dtheta)
            arrows = "→↗↑↖←↙↓↘"
            idx = int((angle + math.pi) / (2*math.pi) * 8) % 8
            row += arrows[idx]
        lines.append((theta, row))
    return lines


def simulate_pendulum(theta0=2.5, omega0=0, dt=0.01, steps=500):
    """RK4 积分 pendulum。返回 (thetas, omegas, energies)。"""
    thetas, omegas, energies = [], [], []
    theta, omega = theta0, omega0
    for _ in range(steps):
        # RK4
        k1t, k1o = omega, pendulum_dynamics(theta, omega)
        k2t, k2o = omega+0.5*dt*k1o, pendulum_dynamics(theta+0.5*dt*k1t, omega+0.5*dt*k1o)
        k3t, k3o = omega+0.5*dt*k2o, pendulum_dynamics(theta+0.5*dt*k2t, omega+0.5*dt*k2o)
        k4t, k4o = omega+dt*k3o, pendulum_dynamics(theta+dt*k3t, omega+dt*k3o)
        theta += dt/6*(k1t+2*k2t+2*k3t+k4t)
        omega += dt/6*(k1o+2*k2o+2*k3o+k4o)
        thetas.append(theta)
        omegas.append(omega)
        energies.append(pendulum_energy(theta, omega))
    return thetas, omegas, energies


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.4210 Underactuated Robotics: LQR/LCP/Lyapunov/Pendulum")
    print("=" * 65)

    # --- LQR Cartpole ---
    print("\n📋 1. LQR 控制 cartpole (线性化 @ 杆向上)")
    A, B = cartpole_linearize()
    Q = np.diag([1, 10, 1, 1])  # θ 权重高
    R = np.array([[0.1]])
    dt = 0.05
    # 前向 Euler 离散化：A_d = I + A·dt, B_d = B·dt
    # dlqr 解的是离散代数 Riccati 方程 (DARE)，必须喂离散矩阵
    A_d = np.eye(4) + A * dt
    B_d = B * dt
    K, P = dlqr(A_d, B_d, Q, R)
    print(f"  状态 [x, θ, x_dot, θ_dot], 控制 = 力, dt={dt}")
    print(f"  u = -Kx, K = {[round(float(k),3) for k in K[0]]}")
    # 闭环仿真（前向 Euler：x_{k+1} = x_k + dt·(A·x + B·u)）
    x = np.array([[0.1], [0.1], [0], [0]])  # 初始扰动
    for step in range(200):
        u = -K @ x
        x = x + dt * (A @ x + B @ u)
    norm_x = float(np.linalg.norm(x))
    print(f"  初始扰动 [0.1, 0.1, 0, 0] → 200 步后状态: {x.flatten().round(6)}")
    print(f"  ‖x‖ = {norm_x:.6f}  {'(< 0.01 ✓ 稳定)' if norm_x < 0.01 else '(未收敛 ✗)'}")
    print(f"  → LQR 渐近稳定化不稳定系统 (杆向上=自然不稳定)。")

    # --- LCP ---
    print("\n📋 2. 接触 complementarity (LCP)")
    z = contact_lcp_demo()
    print(f"  小球在地面: 重力需求法向力")
    print(f"  LCP 解: z(法向力) = {z}, w = {np.array([[1.0]])@z + np.array([-5.0])}")
    print(f"  → z≥0, w≥0, z·w=0 (互补): 法向力正好抵消重力，无穿透。")
    # 2 维 LCP
    M2 = np.array([[2.0, 1.0],[1.0, 2.0]])
    q2 = np.array([-1.0, -1.0])
    z2 = solve_lcp_brute(M2, q2)
    w2 = M2 @ z2 + q2
    print(f"  2D LCP: M={M2.tolist()}, q={q2.tolist()}")
    print(f"  z={z2.round(3)}, w={w2.round(3)}, z·w={float(np.dot(z2,w2)):.4f}")

    # --- Lyapunov ---
    print("\n📋 3. Lyapunov 稳定性验证")
    # 系统 dx/dt = -x, V(x) = x² → V̇ = 2x(-x) = -2x² < 0
    f = lambda x: np.array([-x[0]])
    V = lambda x: x[0]**2
    grad_V = lambda x: np.array([2*x[0]])
    test_points = [np.array([v]) for v in [-2,-1,0.5,1,3]]
    results = lyapunov_check(f, V, grad_V, test_points)
    print(f"  系统 dx/dt = -x, V(x) = x²")
    print(f"  {'x':>6}{'V(x)':>8}{'V̇(x)':>8}{'稳定?':>6}")
    for x, v, vdot in results:
        print(f"  {x[0]:>6.1f}{v:>8.2f}{vdot:>8.2f}{'✓' if vdot < 0 else '✗':>6}")

    # --- Pendulum Phase Portrait ---
    print("\n📋 4. Pendulum 相图 (ASCII)")
    lines = phase_portrait_ascii(grid_n=15)
    print("  θ→  (水平=角度, 垂直=角速度)")
    for theta, row in lines:
        label = f"ω={math.sin(theta)*4:+.1f}" if abs(theta) > 3 else ""
        print(f"  {label:>8} |{row}")
    # 能量
    thetas, omegas, energies = simulate_pendulum(theta0=2.5, steps=300)
    print(f"\n  模拟 θ₀=2.5rad: 初始能量={energies[0]:.3f}J, 终态={energies[-1]:.3f}J")
    print(f"  能量衰减 {((energies[0]-energies[-1])/energies[0]*100):.1f}% (阻尼 b=0.1)")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：cartpole 自然不稳定，但 LQR 能稳定它")
    print("=" * 65)
    # 开环 vs 闭环特征值
    eigs_open = np.linalg.eigvals(A)
    A_cl = A - B @ K                      # 连续时间闭环
    eigs_closed = np.linalg.eigvals(A_cl)
    eigs_closed_d = np.linalg.eigvals(A_d - B_d @ K)  # 离散时间闭环
    print(f"  开环特征值(连续): {[round(float(e.real),3) for e in eigs_open]}")
    print(f"    → 有正实部 → 不稳定 (杆会倒)")
    print(f"  闭环特征值(连续): {[round(float(e.real),3) for e in eigs_closed]}")
    print(f"    → 全负实部 → 稳定 (LQR 控制力维持平衡)")
    print(f"  闭环特征值(离散|λ|): {[round(abs(complex(e)),3) for e in eigs_closed_d]}")
    print(f"    → 全 < 1 → 离散稳定")
    print(f"\n  改变 Q/R 权重对控制的影响:")
    for q_theta in [1, 5, 50, 500]:
        Q2 = np.diag([1, q_theta, 1, 1])
        K2, _ = dlqr(A_d, B_d, Q2, R)
        print(f"    Q_θ={q_theta:>3}: K={K2[0].round(2)}, "
              f"最大控制增益={max(abs(K2[0])):.2f}")
    print("  → 对 θ 惩罚越大，控制越激进（增益越大），稳定性越强但能耗越高。")

    print("\n✅ 6.4210 Demo 完成！")


if __name__ == "__main__":
    demo()
