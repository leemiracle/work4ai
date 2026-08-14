#!/usr/bin/env python3
"""
MIT 18.03 实验：ODE 数值解法对比 (Euler vs RK4) + 线性系统稳定性 + Neural ODE 示意

纯 numpy + matplotlib，直接 python ode_solver_demo.py 运行。
依赖: pip install numpy matplotlib
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# 1. Euler vs RK4 精度对比
# ============================================================
def euler(f, x0, t_array):
    n = len(x0)
    x = np.zeros((len(t_array), n))
    x[0] = x0
    for i in range(len(t_array) - 1):
        h = t_array[i+1] - t_array[i]
        x[i+1] = x[i] + h * np.atleast_1d(f(x[i], t_array[i]))
    return x

def rk4(f, x0, t_array):
    n = len(x0)
    x = np.zeros((len(t_array), n))
    x[0] = x0
    for i in range(len(t_array) - 1):
        h = t_array[i+1] - t_array[i]
        k1 = np.atleast_1d(f(x[i], t_array[i]))
        k2 = np.atleast_1d(f(x[i] + h/2 * k1, t_array[i] + h/2))
        k3 = np.atleast_1d(f(x[i] + h/2 * k2, t_array[i] + h/2))
        k4 = np.atleast_1d(f(x[i] + h * k3, t_array[i] + h))
        x[i+1] = x[i] + h/6 * (k1 + 2*k2 + 2*k3 + k4)
    return x

print("=" * 60)
print("Experiment 1: Euler vs RK4 (dx/dt = -x, exact = e^{-t})")
print(f"{'step h':>10} {'Euler err':>14} {'RK4 err':>14} {'ratio':>10}")
f_decay = lambda x, t: -x
x0 = np.array([1.0])
for h in [0.5, 0.2, 0.1, 0.05, 0.01]:
    t = np.arange(0, 2.0 + h/2, h)
    euler_sol = euler(f_decay, x0, t)[-1, 0]
    rk4_sol = rk4(f_decay, x0, t)[-1, 0]
    exact = np.exp(-2)
    e_err = abs(euler_sol - exact)
    r_err = abs(rk4_sol - exact)
    print(f"{h:10.2f} {e_err:14.6e} {r_err:14.6e} {e_err/max(r_err,1e-30):10.1f}")
print("Conclusion: RK4 error << Euler error; RK4 ~ O(h^4), Euler ~ O(h)\n")

# ============================================================
# 2. 阻尼振荡: ddx/dt2 + p*dx/dt + q*x = 0 (化为系统)
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

# 欠阻尼 (p=0.6, q=1): x'' + 0.6x' + x = 0 -> [x'; x''] = [x'; -0.6x'-x]
damped = lambda x, t: np.array([x[1], -0.6*x[0] - x[1]])
t_fine = np.linspace(0, 20, 1000)
sol = rk4(damped, np.array([1.0, 0.0]), t_fine)
axes[0].plot(t_fine, sol[:, 0], 'b-', linewidth=1.2)
axes[0].set_title("Underdamped Oscillation\nx''+0.6x'+x=0")
axes[0].set_xlabel("t"); axes[0].set_ylabel("x(t)")
axes[0].axhline(0, color='k', linewidth=0.3)

# 相平面: 螺旋
axes[1].plot(sol[:, 0], sol[:, 1], 'r-', linewidth=0.8)
axes[1].plot(sol[0, 0], sol[0, 1], 'go', markersize=6)
axes[1].set_title("Phase Portrait (Spiral Sink)")
axes[1].set_xlabel("x"); axes[1].set_ylabel("x'")
axes[1].axhline(0, color='k', linewidth=0.3)
axes[1].axvline(0, color='k', linewidth=0.3)

# Neural ODE = continuous ResNet (simple: h' = -tanh(h^2)*h)
neural_ode = lambda h, t: -np.tanh(h**2) * h
h0 = np.array([2.0])
t_ode = np.linspace(0, 5, 200)
sol_ode = rk4(neural_ode, h0, t_ode)
# Overlay Euler with large step (= "discrete ResNet layers")
t_euler = np.linspace(0, 5, 6)  # 5 "layers"
sol_euler = euler(neural_ode, h0, t_euler)
axes[2].plot(t_ode, sol_ode[:, 0], 'b-', linewidth=1.5, label="Neural ODE (RK4 fine)")
axes[2].plot(t_euler, sol_euler[:, 0], 'rs--', markersize=7, label="ResNet (Euler, dt=1)")
axes[2].set_title("Neural ODE vs ResNet\n(RK4 = continuous, Euler dt=1 = discrete)")
axes[2].set_xlabel("t (depth)"); axes[2].set_ylabel("h(t)")
axes[2].legend(fontsize=8)

plt.tight_layout()
plt.savefig("ode_solver_demo.png", dpi=120)
print("Figure saved: ode_solver_demo.png\n")

# ============================================================
# 3. 线性系统稳定性 (eigenvalues)
# ============================================================
print("=" * 60)
print("Experiment 3: Linear System Stability via Eigenvalues")
systems = {
    "Stable sink":    np.array([[-2, 0], [0, -1]]),
    "Saddle (unstable)": np.array([[1, 0], [0, -2]]),
    "Center (oscillate)": np.array([[0, 1], [-4, 0]]),
    "Spiral source":  np.array([[0.5, -1], [1, 0.5]]),
}
for name, A in systems.items():
    eigvals = np.linalg.eigvals(A)
    max_real = max(eigvals.real)
    status = "STABLE" if max_real < 0 else ("MARGINAL" if max_real == 0 else "UNSTABLE")
    print(f"  {name:22s}: eigenvalues={np.round(eigvals, 2)}, {status}")

print("\nMamba SSM connection:")
print("  h'(t) = A*h + B*x, A must have Re(eigenvalue) < 0 for stable memory")
A_mamba = np.diag([-1.0, -2.0, -3.0])  # HiPPO-like diagonal
print(f"  Example A (diagonal, HiPPO-like): eigenvalues = {np.linalg.eigvalsh(A_mamba)}")
print("  All negative -> continuous system stable -> good long-range memory")
print("=" * 60)
print("All experiments done.")
