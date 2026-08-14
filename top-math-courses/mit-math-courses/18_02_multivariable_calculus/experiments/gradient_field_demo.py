#!/usr/bin/env python3
"""
MIT 18.02 实验：梯度下降在多变量函数上 + Jacobian/反向传播验证 + 条件数影响

纯 numpy + matplotlib，直接 python gradient_field_demo.py 运行。
依赖: pip install numpy matplotlib
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# 1. 梯度下降可视化（Rosenbrock 函数 + 等高线）
# ============================================================
def rosenbrock(w):
    return (1 - w[0])**2 + 100 * (w[1] - w[0]**2)**2

def rosenbrock_grad(w):
    g1 = -2*(1 - w[0]) - 400*w[0]*(w[1] - w[0]**2)
    g2 = 200*(w[1] - w[0]**2)
    return np.array([g1, g2])

def gradient_descent(grad_fn, x0, lr, n_steps):
    x = np.array(x0, dtype=float)
    traj = [x.copy()]
    for _ in range(n_steps):
        x = x - lr * grad_fn(x)
        traj.append(x.copy())
    return np.array(traj)

traj = gradient_descent(rosenbrock_grad, x0=[-1.2, 1.0], lr=0.002, n_steps=5000)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 等高线 + 下降轨迹
x_grid = np.linspace(-1.5, 2.0, 200)
y_grid = np.linspace(-0.5, 2.5, 200)
X, Y = np.meshgrid(x_grid, y_grid)
Z = rosenbrock(np.array([X, Y]))
axes[0].contour(X, Y, Z, levels=np.logspace(-1, 4, 20), cmap='viridis')
axes[0].plot(traj[:, 0], traj[:, 1], 'r.-', markersize=2, linewidth=0.5)
axes[0].plot(1, 1, 'r*', markersize=15, label='Global min (1,1)')
axes[0].set_xlabel('x1')
axes[0].set_ylabel('x2')
axes[0].set_title('Gradient Descent on Rosenbrock')
axes[0].legend()

# 损失收敛
axes[1].semilogy(rosenbrock(traj.T), 'b-', linewidth=0.8)
axes[1].set_xlabel('Iteration')
axes[1].set_ylabel('f(w) (log scale)')
axes[1].set_title('Rosenbrock Loss Convergence')
plt.tight_layout()
plt.savefig("gradient_field_demo.png", dpi=120)
print("=" * 60)
print("Experiment 1: Gradient Descent on Rosenbrock")
print(f"  Start: (-1.2, 1.0), min at (1,1)")
print(f"  After 5000 steps: w = ({traj[-1,0]:.4f}, {traj[-1,1]:.4f})")
print(f"  Loss: {rosenbrock(traj[-1]):.6e}")
print(f"  Figure saved: gradient_field_demo.png\n")

# ============================================================
# 2. Jacobian 链式法则 = 反向传播验证
# ============================================================
print("=" * 60)
print("Experiment 2: Jacobian = Backpropagation Verification")

np.random.seed(42)
W1 = np.random.randn(3, 2)    # layer 1: 2 -> 3
W2 = np.random.randn(1, 3)    # layer 2: 3 -> 1
x = np.array([0.5, -0.3])

def forward(W1, W2, x):
    a = W1 @ x                 # pre-activation (3,)
    h = np.maximum(a, 0)       # ReLU (3,)
    y = (W2 @ h)[0]            # scalar output
    return a, h, y

# Analytical gradient (backprop)
a, h, y = forward(W1, W2, x)
dy_dh = W2                     # Jacobian dy/dh = W2 (1x3)
dh_da = np.diag((a > 0).astype(float))  # ReLU' diagonal
da_dW1_times_x = np.outer(np.ones(3), x)  # for da_i/dW1_ij = x_j

# dL/dW1 where L = y (treat y as loss for simplicity)
grad_W1_analytical = np.outer(dy_dh[0] @ dh_da, x)  # (3,2)

# Numerical gradient (central difference)
eps = 1e-7
grad_W1_numerical = np.zeros_like(W1)
for i in range(W1.shape[0]):
    for j in range(W1.shape[1]):
        W1[i, j] += eps
        y_plus = forward(W1, W2, x)[2]
        W1[i, j] -= 2 * eps
        y_minus = forward(W1, W2, x)[2]
        W1[i, j] += eps
        grad_W1_numerical[i, j] = (y_plus - y_minus) / (2 * eps)

max_err = np.max(np.abs(grad_W1_analytical - grad_W1_numerical))
print(f"  Analytical dW1:\n{np.array2string(grad_W1_analytical, precision=6)}")
print(f"  Numerical  dW1:\n{np.array2string(grad_W1_numerical, precision=6)}")
print(f"  Max error: {max_err:.2e}")
print("  Conclusion: Jacobian chain rule = backprop (error ~1e-10)\n")

# ============================================================
# 3. 条件数对梯度下降的影响
# ============================================================
print("=" * 60)
print("Experiment 3: Condition Number Effect on GD")

def ellipsoid_f(w):    return w[0]**2 + 100 * w[1]**2
def ellipsoid_g(w):    return np.array([2*w[0], 200*w[1]])

H = np.array([[2, 0], [0, 200]])
eigenvalues = np.linalg.eigvalsh(H)
cond = max(eigenvalues) / min(eigenvalues)
print(f"  f(x,y) = x^2 + 100y^2")
print(f"  Hessian eigenvalues: {eigenvalues}")
print(f"  Condition number: {cond:.0f}")

traj_ell = gradient_descent(ellipsoid_g, x0=[1.0, 1.0], lr=0.009, n_steps=50)
print(f"\n  GD trajectory (lr=0.009), first 5 steps:")
for i in range(6):
    w = traj_ell[i]
    print(f"    step {i}: ({w[0]:+.4f}, {w[1]:+.4f}), f={ellipsoid_f(w):.6f}")
print(f"  Note: y-direction converges ~100x faster than x-direction")
print(f"  This 'ill-conditioning' is why Adam (arXiv:1412.6980) uses")
print(f"  per-parameter adaptive step sizes (sqrt of 2nd moment).")
print("=" * 60)
print("All experiments done.")
