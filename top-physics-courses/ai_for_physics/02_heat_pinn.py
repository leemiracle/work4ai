"""
PINN 解 2D 热传导方程 — 展示时间演化 + 多维输入
==================================================
方程:  u_t = u_xx   (扩散方程, x in [0,1], t in [0, 0.3])
初始:  u(x, 0) = sin(pi*x)
边界:  u(0, t) = u(1, t) = 0
解析解: u(x,t) = sin(pi*x) * exp(-pi^2 * t)

关键升级 (相比 pinn_poisson.py):
  - 2D 输入 (x, t) → 网络 [2] -> [H] -> [H] -> [1]
  - 同时含一阶导 (u_t) 和二阶导 (u_xx)
  - hard constraint: u = sin(pi*x) * NN(x,t)  → 边界自动满足
  - 初始条件: NN(x, 0) -> 1  (让 u(x,0) = sin(pi*x))

零依赖 (仅 NumPy), 目标: ~20s, 末端相对误差 < 10%
"""
import math
import time
import numpy as np

np.random.seed(42)

H = 10
N_W1, N_B1 = 2 * H, H
N_W2, N_B2 = H * H, H
N_W3, N_B3 = H * 1, 1
SLICES = [(0, N_W1),
          (N_W1, N_W1 + N_B1),
          (N_W1 + N_B1, N_W1 + N_B1 + N_W2),
          (N_W1 + N_B1 + N_W2, N_W1 + N_B1 + N_W2 + N_B2),
          (N_W1 + N_B1 + N_W2 + N_B2, N_W1 + N_B1 + N_W2 + N_B2 + N_W3),
          (N_W1 + N_B1 + N_W2 + N_B2 + N_W3,
           N_W1 + N_B1 + N_W2 + N_B2 + N_W3 + N_B3)]
N_PARAMS = sum(s[1] - s[0] for s in SLICES)


def unpack(theta):
    W1 = theta[SLICES[0][0]:SLICES[0][1]].reshape(2, H)
    b1 = theta[SLICES[1][0]:SLICES[1][1]]
    W2 = theta[SLICES[2][0]:SLICES[2][1]].reshape(H, H)
    b2 = theta[SLICES[3][0]:SLICES[3][1]]
    W3 = theta[SLICES[4][0]:SLICES[4][1]].reshape(H, 1)
    b3 = theta[SLICES[5][0]:SLICES[5][1]]
    return W1, b1, W2, b2, W3, b3


def nn(theta, xt):
    """xt: (N,2) [x, t] -> (N,1)"""
    W1, b1, W2, b2, W3, b3 = unpack(theta)
    z1 = np.tanh(xt @ W1 + b1)
    z2 = np.tanh(z1 @ W2 + b2)
    return z2 @ W3 + b3


def u(theta, xt):
    """hard constraint: u = sin(pi*x) * NN(x,t)  -> u(0,t)=u(1,t)=0 自动"""
    x = xt[:, 0:1]
    return np.sin(np.pi * x) * nn(theta, xt)


# collocation 点: 内部 (x,t) 网格 + 初始 t=0
_xs = np.linspace(0.1, 0.9, 5)
_ts = np.linspace(0.02, 0.3, 5)
XX, TT = np.meshgrid(_xs, _ts)
X_INT = np.column_stack([XX.ravel(), TT.ravel()])           # (25, 2)
X_IC = np.column_stack([np.linspace(0.1, 0.9, 8), np.zeros(8)])  # 初始点
H_FD = 1e-3


def loss(theta):
    # PDE 残差: u_t - u_xx = 0
    xt_tp = X_INT.copy(); xt_tp[:, 1] += H_FD
    xt_tm = X_INT.copy(); xt_tm[:, 1] -= H_FD
    u_t = (u(theta, xt_tp) - u(theta, xt_tm)) / (2 * H_FD)
    xp = X_INT.copy(); xp[:, 0] += H_FD
    xm = X_INT.copy(); xm[:, 0] -= H_FD
    u_xx = (u(theta, xp) - 2 * u(theta, X_INT) + u(theta, xm)) / (H_FD ** 2)
    pde = np.mean((u_t - u_xx) ** 2)
    # 初始: u(x,0)=sin(pi x) → NN(x,0)=1
    ic = np.mean((nn(theta, X_IC) - 1.0) ** 2)
    return pde + 3.0 * ic


def num_grad(theta, eps=1e-5):
    g = np.zeros_like(theta)
    for i in range(len(theta)):
        tp = theta.copy(); tp[i] += eps
        tm = theta.copy(); tm[i] -= eps
        g[i] = (loss(tp) - loss(tm)) / (2 * eps)
    return g


def clip_norm(g, mx=5.0):
    n = np.linalg.norm(g)
    return g * (mx / n) if n > mx else g


print("=" * 72)
print("  PINN 解 2D 热传导:  u_t = u_xx,  u(x,0)=sin(pi x),  u(0,t)=u(1,t)=0")
print("  解析解: u(x,t) = sin(pi*x) * exp(-pi^2 * t)")
print("=" * 72)

theta = np.random.randn(N_PARAMS) * 0.3
LR, EPOCHS = 0.01, 700
m_ad = np.zeros_like(theta); v_ad = np.zeros_like(theta)
B1, B2, EPS = 0.9, 0.999, 1e-8

print(f"\n网络: [2] -> [{H}] -> [{H}] -> [1],  参数 = {N_PARAMS}")
print(f"collocation: 内部 {len(X_INT)} + 初始 {len(X_IC)},  epoch = {EPOCHS},  Adam lr = {LR}\n")

t0 = time.time()
for ep in range(EPOCHS):
    g = clip_norm(num_grad(theta))
    m_ad = B1 * m_ad + (1 - B1) * g
    v_ad = B2 * v_ad + (1 - B2) * g * g
    theta -= LR * m_ad / (1 - B1 ** (ep + 1)) / (np.sqrt(v_ad / (1 - B2 ** (ep + 1))) + EPS)
    if ep % 100 == 0 or ep == EPOCHS - 1:
        print(f"  epoch {ep:4d}  loss = {loss(theta):.6e}")
print(f"\n训练耗时: {time.time()-t0:.1f}s")

# 验证: 在不同时刻对比解析解
print("\n" + "=" * 72)
print("  验证: 不同时刻的解 (取 x=0.5 处)")
print("=" * 72)
print(f"\n  {'t':>5} | {'解析解':>10} | {'PINN':>10} | {'相对误差':>10}")
print("  " + "-" * 48)
for t_val in [0.0, 0.05, 0.1, 0.2, 0.3]:
    x_arr = np.array([[0.5, t_val]])
    u_pred = u(theta, x_arr)[0, 0]
    u_exact = math.sin(math.pi * 0.5) * math.exp(-math.pi ** 2 * t_val)
    rel = abs(u_pred - u_exact) / max(abs(u_exact), 1e-10)
    print(f"  {t_val:5.2f} | {u_exact:10.6f} | {u_pred:10.6f} | {rel*100:9.2f}%")

# 空间剖面 (t=0.15)
print(f"\n  空间剖面 (t=0.15):")
t_check = 0.15
print(f"  {'x':>5} | {'解析解':>10} | {'PINN':>10}")
print("  " + "-" * 35)
for x_val in [0.1, 0.3, 0.5, 0.7, 0.9]:
    u_pred = u(theta, np.array([[x_val, t_check]]))[0, 0]
    u_exact = math.sin(math.pi * x_val) * math.exp(-math.pi ** 2 * t_check)
    print(f"  {x_val:5.2f} | {u_exact:10.6f} | {u_pred:10.6f}")

print("\n" + "=" * 72)
print("  ✦ 反直觉发现")
print("=" * 72)
print(f"""
  1. 这是 2D PINN: 网络吃 (x,t) 两个输入, 同时学空间结构和时间演化。
     pinn_poisson.py 是 1D 静态的; 这里是 1D 空间 + 时间 = 2D 输入。

  2. hard constraint  u = sin(pi*x)*NN(x,t)  让边界 u(0,t)=u(1,t)=0 自动满足,
     而且初始 u(x,0)=sin(pi*x)*NN(x,0) → 只需 NN(x,0)→1。
     NN 主要学"时间衰减" exp(-pi^2*t)。

  3. 解析解 exp(-pi^2*t) 在 t=0.3 时衰减到 e^(-2.96) ≈ 5.2%。
     PINN 看过 PDE 就能重现这个衰减 —— 它"发现"了扩散让波形变低变平。

  4. 把 u_t = u_xx 换成 Schrodinger i*hbar*psi_t = H*psi (加复数 + 量子算符),
     就是量子力学的 PINN。把 u 换成速度场, 加非线性项, 就是 Navier-Stokes。
     PINN 的统一性就在这: 损失函数改一下, 同一个网络架构解任何 PDE。
""")

# 末端误差
xt_end = np.column_stack([np.full(20, 0.5), np.full(20, 0.3)])
err = abs(u(theta, xt_end)[0,0] - math.sin(math.pi*0.5)*math.exp(-math.pi**2*0.3))
print(f"  末端 (x=0.5, t=0.3) 绝对误差: {err:.4f}")
