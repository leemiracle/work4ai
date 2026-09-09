# -*- coding: utf-8 -*-
"""倒立摆：开环不稳定 → LQR（Riccati 工厂）→ 单环 PD 结构极限 → 分离原理演示
对应章：00（大厦六层）/03（工厂与对偶）/04（代码走廊）。

纯 numpy 实现（Riccati 用 scipy.linalg.solve_continuous_are——标准数值配置）。
跑法：python cart_pole_lqr_pid.py   （5 组断言全过则退出码 0）
"""
import numpy as np
from scipy.linalg import solve_continuous_are

rng = np.random.default_rng(42)

# ── 1. 倒立摆线性化模型（cart-pole, pole up）────────────────────────
# 状态 x = [θ, θ̇, p, ṗ]；u = 小车推力。标准参数（cartpole 力学约定）。
M, m, l, g, b = 1.0, 0.1, 0.5, 9.81, 0.1
# 线性化（θ 向上，倒立平衡点）：
A = np.array([
    [0, 1, 0, 0],
    [(M+m)*g/(M*l), -b/(M*l), 0, 0],
    [0, 0, 0, 1],
    [-m*g/M, b/M, 0, 0],
], dtype=float)
B = np.array([[0], [-1/(M*l)], [0], [1/M]], dtype=float)

eig_open = np.linalg.eigvals(A)
print(f"[1] 开环极点: {np.sort_complex(eig_open).round(3)}")
assert (eig_open.real > 0).any(), "断言1失败：开环应不稳定"

# ── 2. LQR：Riccati 工厂一次生产 ───────────────────────────────────
Q = np.diag([10.0, 1.0, 1.0, 0.1])
R = np.array([[0.1]])
P = solve_continuous_are(A, B, Q, R)
K = np.linalg.solve(R, B.T @ P)
eig_lqr = np.linalg.eigvals(A - B @ K)
print(f"[2] LQR 增益 K = {K.round(3)}；闭环极点最大实部 = {eig_lqr.real.max():.3f}")
assert eig_lqr.real.max() < 0, "断言2失败：LQR 闭环应稳定"


def rk4(f, x, h):
    k1 = f(x); k2 = f(x + h/2*k1); k3 = f(x + h/2*k2); k4 = f(x + h*k3)
    return x + h/6*(k1 + 2*k2 + 2*k3 + k4)


def simulate(controller, x0, T=6.0, h=1e-3):
    """正向仿真；controller(x)->u。返回末状态与全程二次代价 J。"""
    x = x0.copy(); steps = int(T/h); J = 0.0
    for _ in range(steps):
        u = controller(x)
        J += h * float(x @ Q @ x + R[0, 0]*u*u)
        x = rk4(lambda s: A @ s + (B @ np.array([[u]])).ravel(), x, h)
    return x, J


# ── 3. LQR 闭环仿真 vs 开环（3 秒内开环发散, LQR 收敛）─────────────
x0 = np.array([0.2, 0.0, 0.0, 0.0])  # 摆偏 0.2 rad
x_open, _ = simulate(lambda s: 0.0, x0, T=3.0)
x_lqr, J_lqr = simulate(lambda s: float(-(K @ s)[0]), x0)
print(f"[3] 3s 末: 开环 |θ|={abs(x_open[0]):.2f}(发散) ; LQR |θ|={abs(x_lqr[0]):.4f}(收敛)")
assert abs(x_open[0]) > 10*abs(x0[0]), "断言3a失败：开环应显著发散"
assert abs(x_lqr[0]) < 1e-2 and abs(x_lqr[2]) < 5e-2, "断言3b失败：LQR 应回正"

# ── 4. 单环 PID 的结构极限：θ 单环对倒立摆原理上不可稳 ─────────────
# 反直觉发现：无论怎么整定 kp/kd（θ 单环 PD），闭环极点恒含正实部——
# 不是手艺问题，是结构问题（不稳定对象+状态耦合 → 单变量回路不够）。
# 这正是 1960 年状态空间革命（Kalman）的现场理由：需要满状态反馈。
print("[4] θ 单环 PD 闭环极点最大实部（应恒 > 0，即结构性不可稳）：")
for kp, kd in [(40, 10), (100, 20), (300, 60), (1000, 200)]:
    eig_pd = np.linalg.eigvals(A + B @ np.array([[-kp, -kd, 0, 0]]))
    print(f"    kp={kp:5}, kd={kd:4}: max Re = {eig_pd.real.max():+.3f}")
    assert eig_pd.real.max() > 0, "断言4失败：若某组增益能稳，改写本断言并更新 00 章"
print("    → 单环失效 ≠ 调参差；满状态 LQR（[2] 段）一把稳住——多变量必要性实证")

# ── 5. 分离原理：带噪观测(θ 与 p 两传感器) → Kalman 估计 → 同一 K 仍稳 ──
# 注：只测 θ 不可观（p 子空间从 θ 不可重构——摆角动力学不含小车位置），
#     滤波 ARE 无解；这正是"能观性=估计的前提"的活教具（00 章第六层）。
C = np.array([[1.0, 0, 0, 0],
              [0.0, 0, 1.0, 0]])               # 测 θ 与 p
W = np.eye(4)*1e-4; V = np.diag([1e-2, 1e-2])   # 过程/观测噪声
Pf = solve_continuous_are(A.T, C.T, W, V)        # 滤波 Riccati（对偶：A↔Aᵀ, B↔Cᵀ）
L = Pf @ C.T @ np.linalg.inv(V)                  # 稳态 Kalman 增益 (4×2)
x = x0.copy(); xhat = np.zeros(4)
h = 1e-3
for _ in range(int(6.0/h)):
    y = C @ x + rng.normal(0, np.sqrt(np.diag(V)))   # 带噪观测
    u = float(-(K @ xhat)[0])                         # 控制用估计值
    xhat = xhat + h*((A @ xhat) + (B @ np.array([u])).ravel() + L @ (y - C @ xhat))
    x = rk4(lambda s: A @ s + (B @ np.array([[u]])).ravel(), x, h)
print(f"[5] 分离原理: 噪声观测下 |θ|={abs(x[0]):.4f} (阈值<0.05)——估计+控制分而治之仍稳")
assert abs(x[0]) < 5e-2, "断言5失败：分离原理应使带噪估计闭环仍稳定"

print("\n[ALL 5 ASSERTS PASSED] 工厂(Riccati)/结构极限(单环)/对偶(两个ARE)/分离(滤波+LQR) 一个脚本。")
