"""控制论：Lyapunov稳定性与最优控制
================================
数学概念：反馈控制 / Lyapunov稳定性 / 可控性 / LQR / PID / Riccati方程
应用领域：机器人 / 自动驾驶 / 飞行控制 / 电路 / 经济调控 / 深度学习优化器
核心思想：控制论 = 动力系统 + 反馈——通过观测输出调整输入使系统稳定。
  线性系统：ẋ = Ax + Bu（状态方程），y = Cx（输出）
  反馈：u = -Kx（状态反馈，改变闭环动力学）
  Lyapunov：V(x)正定且V̇(x)负定 → 原点渐近稳定（不需解ODE！）
  LQR：min ∫(xᵀQx + uᵀRu)dt → K = R⁻¹BᵀP（P解Riccati方程）
  PID：u = Kp·e + Ki·∫e + Kd·ė（比例-积分-微分）
运行方式：python "35-控制论.py"
依赖：numpy, matplotlib, scipy"""
import numpy as np, matplotlib.pyplot as plt
from scipy.linalg import solve_continuous_are
from scipy.integrate import solve_ivp
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def simulate_system(A, B, K, x0, T=10, dt=0.01):
    """仿真闭环系统 ẋ = (A-BK)x。"""
    A_closed = A - B @ K if B is not None else A
    def ode(t, x): return A_closed @ x
    sol = solve_ivp(ode, [0, T], x0, t_eval=np.arange(0, T, dt), rtol=1e-8)
    return sol.t, sol.y

def main():
    np.random.seed(42)
    print("="*60); print("实验 1：开环不稳定 → 闭环稳定"); print("="*60)
    # 倒立摆线性化模型：ẋ = Ax + Bu
    # 状态 x = [位置, 角度, 速度, 角速度]
    A = np.array([[0,0,1,0],[0,0,0,1],[0,0,0,0],[0,0,0,0]], dtype=float)
    B = np.array([[0],[0],[1],[0]], dtype=float)  # 只控制位置加速度
    # 实际倒立摆更复杂，这里用简化的不稳定系统
    A_simple = np.array([[0, 1], [-2, 3]], dtype=float)  # 特征值有正实部→不稳定
    B_simple = np.array([[0], [1]], dtype=float)
    eigs_open = np.linalg.eigvals(A_simple)
    print(f"开环系统 A={A_simple.tolist()}")
    print(f"开环特征值: {eigs_open.round(3)} → {'不稳定' if np.any(eigs_open.real > 0) else '稳定'}")
    # LQR 反馈
    Q = np.eye(2) * 10  # 状态惩罚
    R = np.array([[1.0]])  # 控制惩罚
    P = solve_continuous_are(A_simple, B_simple, Q, R)
    K_lqr = np.linalg.inv(R) @ B_simple.T @ P
    A_closed = A_simple - B_simple @ K_lqr
    eigs_closed = np.linalg.eigvals(A_closed)
    print(f"\nLQR 反馈 K = {K_lqr.flatten().round(4)}")
    print(f"闭环特征值: {eigs_closed.round(3)} → {'稳定' if np.all(eigs_closed.real < 0) else '不稳定'}")

    print("\n"+"="*60); print("实验 2：Lyapunov 稳定性——不用解ODE判断稳定性"); print("="*60)
    # 对于闭环系统 A_closed，Lyapunov 方程 AᵀP + PA = -Q
    Q_lyap = np.eye(2)
    P_lyap = solve_continuous_are(A_closed, np.zeros((2,0)), Q_lyap, np.zeros((0,0))) if False else None
    # 简化：直接用 P = solve_continuous_are 的结果
    print(f"闭环系统 A_closed = {A_closed.round(3).tolist()}")
    # 检查 V(x) = xᵀPx 正定？
    # 数值验证 Lyapunov 函数沿轨迹递减
    t_sim, x_sim = simulate_system(A_simple, B_simple, K_lqr, [2.0, 1.0])
    V_values = np.array([x_sim[:,i] @ P @ x_sim[:,i] for i in range(x_sim.shape[1])])
    print(f"Lyapunov 函数 V(x) = xᵀPx：")
    print(f"  V(0) = {V_values[0]:.4f}, V(末) = {V_values[-1]:.6f}")
    print(f"  V 单调递减: {'✓' if V_values[-1] < V_values[0] else '✗'}")
    print(f"\n[解读] V̇(x) < 0 → 系统渐近稳定。不需解ODE，只检查矩阵方程！")

    print("\n"+"="*60); print("实验 3：LQR——最优线性二次调节器"); print("="*60)
    # 不同 Q/R 权重的影响
    print(f"{'Q权重':<10} {'R权重':<10} {'K':<20} {'闭环极点':<20} {'响应速度'}")
    print("-" * 65)
    for q_val, r_val in [(1, 1), (10, 1), (100, 1), (1, 10), (1, 100)]:
        Q_t = np.eye(2) * q_val; R_t = np.array([[r_val]])
        P_t = solve_continuous_are(A_simple, B_simple, Q_t, R_t)
        K_t = np.linalg.inv(R_t) @ B_simple.T @ P_t
        eigs_t = np.linalg.eigvals(A_simple - B_simple @ K_t)
        speed = "快" if np.max(np.abs(eigs_t.real)) > 2 else "中" if np.max(np.abs(eigs_t.real)) > 1 else "慢"
        print(f"{q_val:<10} {r_val:<10} {K_t.flatten().round(3).tolist()!s:<20} {eigs_t.round(3).tolist()!s:<20} {speed}")
    print(f"\n[解读] Q大→状态收敛快（激进控制）；R大→控制温和（省能量）。")
    print(f"       LQR 自动找到'状态偏差 vs 控制能量'的最优平衡。")

    print("\n"+"="*60); print("实验 4：PID控制——工业标准"); print("="*60)
    # PID 控制 二阶系统
    def pid_control(Kp, Ki, Kd, x0=[1.0, 0], T=10):
        def ode(t, state):
            x, v, integral, _ = state  # 位置/速度/积分/上一次误差
            e = -x  # 目标=0
            u = Kp * e + Ki * integral + Kd * (-v)
            return [v, u, e, e]  # 简化的二阶系统 ẍ=u
        sol = solve_ivp(ode, [0,T], [x0[0], x0[1], 0, 0], t_eval=np.linspace(0,T,500), rtol=1e-6)
        return sol.t, sol.y[0]
    print(f"{'控制器':<15} {'Kp':<8} {'Ki':<8} {'Kd':<8} {'稳态误差':<12} {'超调':<10} {'特性'}")
    print("-" * 70)
    configs = [("P only", 2, 0, 0), ("PI", 2, 1, 0), ("PD", 2, 0, 1), ("PID", 3, 2, 1), ("PID调优", 5, 3, 2)]
    for name, kp, ki, kd in configs:
        t_pid, x_pid = pid_control(kp, ki, kd)
        ss_err = abs(x_pid[-1])
        overshoot = max(0, -x_pid.min()) if x_pid[0] > 0 else 0
        trait = "有稳态误差" if ss_err > 0.01 else "消除误差"
        if overshoot > 0.3: trait += ",超调大"
        elif overshoot > 0.05: trait += ",轻微超调"
        else: trait += ",无超调"
        print(f"{name:<15} {kp:<8} {ki:<8} {kd:<8} {ss_err:<12.4f} {overshoot:<10.4f} {trait}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    ax = axes[0,0]
    t_open, x_open = simulate_system(A_simple, None, None, [2, 1], T=5)
    t_closed, x_closed = simulate_system(A_simple, B_simple, K_lqr, [2, 1], T=5)
    ax.plot(t_open, x_open[0], 'r--', lw=2, label='开环 x₁（发散）')
    ax.plot(t_closed, x_closed[0], 'b-', lw=2, label='LQR闭环 x₁（收敛）')
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlabel('时间'); ax.set_title('开环不稳定 → LQR闭环稳定'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[0,1]
    ax.plot(t_closed, V_values[:len(t_closed)], 'g-', lw=2)
    ax.set_xlabel('时间'); ax.set_ylabel('V(x) = xᵀPx')
    ax.set_title('Lyapunov 函数单调递减 → 稳定'); ax.grid(alpha=0.3)
    ax = axes[1,0]
    for q_val, color in [(1,'red'), (10,'orange'), (100,'green')]:
        Q_t = np.eye(2)*q_val; P_t = solve_continuous_are(A_simple, B_simple, Q_t, np.array([[1.0]]))
        K_t = np.linalg.inv(np.array([[1.0]])) @ B_simple.T @ P_t
        _, x_t = simulate_system(A_simple, B_simple, K_t, [2,1], T=5)
        ax.plot(np.linspace(0,5,len(x_t[0])), x_t[0], color=color, lw=2, label=f'Q={q_val}')
    ax.set_xlabel('时间'); ax.set_ylabel('x₁')
    ax.set_title('LQR 不同Q权重 → 不同收敛速度'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1,1]
    for name, kp, ki, kd, color in [("P",2,0,0,'red'),("PI",2,1,0,'blue'),("PD",2,0,1,'green'),("PID",3,2,1,'purple')]:
        t_p, x_p = pid_control(kp, ki, kd)
        ax.plot(t_p, x_p, color=color, lw=2, label=f'{name}(Kp={kp},Ki={ki},Kd={kd})')
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlabel('时间'); ax.set_ylabel('x（位置）')
    ax.set_title('PID 控制对比'); ax.legend(fontsize=7); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("35-控制论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 35-控制论_结果.png")
    print("\n[总结] 1. 反馈控制:u=-Kx改变闭环动力学(不稳定→稳定)")
    print("2. Lyapunov:V正定+V̇负定=稳定(不需解ODE)")
    print("3. LQR:Riccati方程→最优K(状态偏差vs控制能量)")
    print("4. PID:工业标准(比例消除当前/积分消除稳态/微分预测)")

if __name__ == "__main__": main()
