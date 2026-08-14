"""
PINN (Physics-Informed Neural Network) 解 1D Poisson 方程 — 纯 NumPy 最小实现
==========================================================================
解:  -u''(x) = sin(pi*x),   x in [0,1],   u(0)=u(1)=0
解析解: u(x) = sin(pi*x) / pi^2

关键技巧 (hard constraint):
    令  u(x) = x*(1-x) * NN(x)
    则 u(0)=u(1)=0 自动满足 → 损失只剩 PDE 残差, 训练更稳
    (这是 PINN 工程实践的标准技巧, 比软约束边界罚函数稳定得多)

方法: 数值二阶导 (有限差分) 算 PDE 残差; 数值梯度下降优化权重
稳定性: 小初始化 + 梯度裁剪 + 适中 lr

零依赖 (仅 NumPy + math), 目标: ~15 秒跑完, 相对误差 < 5%
"""
import math
import time
import numpy as np

np.random.seed(42)

# ============ 网络结构 [1] -> [H] -> [H] -> [1] ============
H = 12
N_W1, N_B1 = H, H
N_W2, N_B2 = H * H, H
N_W3, N_B3 = H, 1
SLICES = [(0, N_W1),
          (N_W1, N_W1 + N_B1),
          (N_W1 + N_B1, N_W1 + N_B1 + N_W2),
          (N_W1 + N_B1 + N_W2, N_W1 + N_B1 + N_W2 + N_B2),
          (N_W1 + N_B1 + N_W2 + N_B2, N_W1 + N_B1 + N_W2 + N_B2 + N_W3),
          (N_W1 + N_B1 + N_W2 + N_B2 + N_W3,
           N_W1 + N_B1 + N_W2 + N_B2 + N_W3 + N_B3)]
N_PARAMS = sum(s[1] - s[0] for s in SLICES)


def unpack(theta):
    W1 = theta[SLICES[0][0]:SLICES[0][1]].reshape(1, H)
    b1 = theta[SLICES[1][0]:SLICES[1][1]]
    W2 = theta[SLICES[2][0]:SLICES[2][1]].reshape(H, H)
    b2 = theta[SLICES[3][0]:SLICES[3][1]]
    W3 = theta[SLICES[4][0]:SLICES[4][1]].reshape(H, 1)
    b3 = theta[SLICES[5][0]:SLICES[5][1]]
    return W1, b1, W2, b2, W3, b3


def nn_forward(theta, x):
    """原始网络输出 NN(x), x: (N,1) -> (N,1)"""
    W1, b1, W2, b2, W3, b3 = unpack(theta)
    z1 = np.tanh(x @ W1 + b1)
    z2 = np.tanh(z1 @ W2 + b2)
    return z2 @ W3 + b3


def u_forward(theta, x):
    """hard-constraint 解: u(x) = x*(1-x) * NN(x), 自动满足 u(0)=u(1)=0"""
    return x * (1.0 - x) * nn_forward(theta, x)


# ============ collocation 点 ============
X_INT = np.linspace(0.05, 0.95, 25).reshape(-1, 1)
H_FD = 1e-3   # 二阶导步长 (大一点更稳)


def loss(theta):
    """PDE 残差: -u''(x) - sin(pi*x) = 0"""
    up = u_forward(theta, X_INT + H_FD)
    uc = u_forward(theta, X_INT)
    um = u_forward(theta, X_INT - H_FD)
    d2u = (up - 2 * uc + um) / (H_FD ** 2)
    res = -d2u - np.sin(np.pi * X_INT)
    return np.mean(res ** 2)


def num_grad(theta, eps=1e-5):
    g = np.zeros_like(theta)
    for i in range(len(theta)):
        tp = theta.copy(); tp[i] += eps
        tm = theta.copy(); tm[i] -= eps
        g[i] = (loss(tp) - loss(tm)) / (2 * eps)
    return g


def clip_grad_norm(g, max_norm=5.0):
    n = np.linalg.norm(g)
    if n > max_norm:
        g = g * (max_norm / n)
    return g


# ============ 训练 ============
print("=" * 70)
print("  PINN 解 1D Poisson:  -u''(x) = sin(pi*x),  u(0)=u(1)=0")
print("  解析解: u(x) = sin(pi*x) / pi^2")
print("  技巧: hard constraint  u(x) = x*(1-x)*NN(x)  → 边界自动满足")
print("=" * 70)

# GPT-2 风格小初始化 (std=0.02 太小, 用 0.3 平衡)
theta = np.random.randn(N_PARAMS) * 0.3
LR = 0.01
EPOCHS = 1000

# Adam 优化器状态 (手写, 自适应学习率, 比纯梯度下降快几倍收敛)
m_adam = np.zeros_like(theta)
v_adam = np.zeros_like(theta)
BETA1, BETA2, ADAM_EPS = 0.9, 0.999, 1e-8

print(f"\n网络: [1] -> [{H}] -> [{H}] -> [1],  参数数 = {N_PARAMS}")
print(f"collocation 点 = {len(X_INT)},  epoch = {EPOCHS},  lr = {LR}")
print(f"优化器: Adam (beta1={BETA1}, beta2={BETA2}) + 梯度裁剪 max_norm=5.0\n")

t0 = time.time()
for epoch in range(EPOCHS):
    g = num_grad(theta)
    g = clip_grad_norm(g, 5.0)
    # Adam 更新
    m_adam = BETA1 * m_adam + (1 - BETA1) * g
    v_adam = BETA2 * v_adam + (1 - BETA2) * (g * g)
    m_hat = m_adam / (1 - BETA1 ** (epoch + 1))
    v_hat = v_adam / (1 - BETA2 ** (epoch + 1))
    theta -= LR * m_hat / (np.sqrt(v_hat) + ADAM_EPS)
    if epoch % 100 == 0 or epoch == EPOCHS - 1:
        l = loss(theta)
        print(f"  epoch {epoch:4d}  PDE loss = {l:.6e}")
print(f"\n训练耗时: {time.time()-t0:.1f}s")

# ============ 验证 ============
X_TEST = np.linspace(0, 1, 50).reshape(-1, 1)
U_PRED = u_forward(theta, X_TEST).flatten()
U_EXACT = (np.sin(np.pi * X_TEST) / math.pi ** 2).flatten()

abs_err = np.abs(U_PRED - U_EXACT)
max_err = abs_err.max()
mean_err = abs_err.mean()
u_scale = np.abs(U_EXACT).max()
rel_err = max_err / u_scale

print("\n" + "=" * 70)
print("  验证结果")
print("=" * 70)
print(f"  解析解 u(0.5) = 1/pi^2 = {U_EXACT[25]:.6f}")
print(f"  PINN   u(0.5) =        {U_PRED[25]:.6f}")
print(f"  最大绝对误差 = {max_err:.6f}")
print(f"  平均绝对误差 = {mean_err:.6f}")
print(f"  相对误差     = {rel_err*100:.2f}%  (相对 u_max = {u_scale:.4f})")

print("\n  x    |  解析解   |  PINN 预测  |  绝对误差")
print("  -----+-----------+-------------+----------")
for i in range(0, 50, 7):
    print(f"  {X_TEST[i,0]:.2f} | {U_EXACT[i]:+.6f} |  {U_PRED[i]:+.6f}  | {abs_err[i]:.2e}")

print("\n" + "=" * 70)
print("  ✦ 反直觉发现")
print("=" * 70)
print(f"""
  1. 网络从未见过解析解 u = sin(pi*x)/pi^2, 它只见过 PDE (-u''=sin(pi*x))。
     训练后它"重新发明"了解析解 —— PINN 用物理定律本身当训练数据。

  2. hard constraint 技巧 (u=x*(1-x)*NN) 让边界 u(0)=u(1)=0 自动满足,
     损失只剩 PDE 残差 → 比软约束 (边界罚函数) 稳定几个数量级。
     这是 PINN 工程实战的关键 (软约束的边界权重难调, 易发散)。

  3. 相对误差 {rel_err*100:.2f}% 是用 {N_PARAMS} 参数 × 数值梯度达到的。
     真实科研用 PyTorch autograd (解析梯度) 快 100x, 且能用 Adam/L-BFGS。
     但原理就是这个 —— 物理定律 = 损失函数。

  4. 这个方法可推广到任何 PDE: 把 -u''=f 换成 Navier-Stokes / Schrödinger /
     Maxwell, 损失函数改一下, 网络架构不变。这就是 PINN 的统一性。
""")

if rel_err < 0.05:
    print(f"  ✓ 通过: 相对误差 {rel_err*100:.2f}% < 5%")
else:
    print(f"  ⚠ 相对误差 {rel_err*100:.2f}% 偏大, 可尝试: 增大 EPOCHS / 调 H / 用 Adam")
