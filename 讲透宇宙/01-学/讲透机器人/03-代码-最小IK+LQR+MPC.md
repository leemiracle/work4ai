---
card_id: ROB-03
title: "第 3 幕 · 代码：最小 IK + LQR + MPC + EKF"
universe: 讲透机器人
arc_position: 第 3 幕
status: draft
next_card: ROB-04
refs:
  - "Lynch & Park, Modern Robotics（在线免费英文 + B 站中文讲解）"
  - "Brunton《数据驱动的科学与工程》中文版（控制部分）"
  - "高翔《视觉 SLAM 十四讲》（EKF/图优化）"
  - "古月居 guyuehome.com（ROS 中文实例）"
---

# 💻 第 3 幕 · 代码：IK + LQR + MPC + EKF

## 1. 2 连杆平面臂逆运动学（解析解）

```python
import numpy as np

def forward_kinematics(theta1, theta2, l1=1.0, l2=1.0):
    x = l1*np.cos(theta1) + l2*np.cos(theta1+theta2)
    y = l1*np.sin(theta1) + l2*np.sin(theta1+theta2)
    return np.array([x, y])

def inverse_kinematics(x, y, l1=1.0, l2=1.0):
    """解析 IK: 余弦定理."""
    r2 = x**2 + y**2
    cos_t2 = (r2 - l1**2 - l2**2) / (2*l1*l2)
    if abs(cos_t2) > 1: return None  # 超出工作空间
    t2 = np.arccos(cos_t2)
    t1 = np.arctan2(y, x) - np.arctan2(l2*np.sin(t2), l1 + l2*np.cos(t2))
    return t1, t2

if __name__ == "__main__":
    # 正运动学
    t1, t2 = 0.5, 0.3
    x, y = forward_kinematics(t1, t2)
    print(f"FK: theta=({t1:.2f},{t2:.2f}) -> ({x:.3f},{y:.3f})")
    # 逆运动学
    sol = inverse_kinematics(x, y)
    print(f"IK: ({x:.3f},{y:.3f}) -> theta={sol}")
    # 验证
    print(f"回验 FK: {forward_kinematics(*sol)}")
    # 超出工作空间
    print(f"超出 (3,3): {inverse_kinematics(3, 3)}")
```

## 2. 倒立摆 LQR 控制

```python
import numpy as np

def cartpole_dynamics(x, u, m=1.0, M=5.0, L=2.0, g=9.81):
    """简化倒立摆线性化模型: x=[位置, 速度, 角度, 角速度]."""
    # 在 (角度=0, 角速度=0) 线性化
    A = np.array([
        [0, 1, 0, 0],
        [0, 0, m*g/M, 0],
        [0, 0, 0, 1],
        [0, 0, (M+m)*g/(M*L), 0],
    ])
    B = np.array([[0],[1/M],[0],[1/(M*L)]])
    return A @ x + B.flatten() * u

def dlqr(A, B, Q, R):
    """离散 LQR: 解 Riccati."""
    P = Q.copy()
    K = np.zeros((B.shape[1], A.shape[0]))
    for _ in range(1000):
        K = -np.linalg.inv(R + B.T @ P @ B) @ (B.T @ P @ A)
        P = Q + A.T @ P @ A + A.T @ P @ B @ K
        if np.max(np.abs(K)) > 1e6: break
    return -K  # 反号(公式约定)

if __name__ == "__main__":
    dt = 0.05
    A = np.array([[1, dt, 0, 0],[0,1,0.2*dt,0],[0,0,1,dt],[0,0,2.2*dt,1]])
    B = np.array([[0],[0.2*dt],[0],[0.4*dt]])
    Q = np.diag([1, 0.1, 10, 0.1])  # 角度权重最大
    R = np.array([[0.1]])
    K = dlqr(A, B, Q, R)
    print(f"LQR 增益 K = {K}")
    # 仿真
    x = np.array([0, 0, 0.2, 0])  # 初始偏 0.2 弧度
    for t in range(100):
        u = K @ x
        x = A @ x + B.flatten() * u
        if t % 20 == 0:
            print(f"  t={t*dt:.1f}s 角度={x[2]:.4f} 位置={x[0]:.4f}")
    print(f"LQR 把摆杆从偏角 0.2 拉回平衡.")
```

## 3. MPC 简化版（倒立摆，QP）

```python
import numpy as np

def mpc_cartpole(x0, N=10, dt=0.1, steps=50):
    """简化 MPC: 每步求解有限时域最优控制(暴力枚举 demo)."""
    A = np.array([[1, dt, 0, 0],[0,1,0.2*dt,0],[0,0,1,dt],[0,0,2.2*dt,1]])
    B = np.array([[0],[0.2*dt],[0],[0.4*dt]])
    Q = np.diag([1, 0.1, 10, 0.1])
    R = np.array([[0.1]])
    x = x0.copy()
    for t in range(steps):
        # 枚举若干控制候选, 选最优
        best_u, best_cost = 0, 1e18
        for u_try in np.linspace(-3, 3, 21):
            xp = x.copy(); cost = 0
            for k in range(N):
                cost += xp @ Q @ xp + R[0,0]*u_try**2
                xp = A @ xp + B.flatten()*u_try
            if cost < best_cost:
                best_cost, best_u = cost, u_try
        x = A @ x + B.flatten()*best_u
        if t % 10 == 0:
            print(f"  t={t*dt:.1f}s 角度={x[2]:.4f} u={best_u:.2f}")
    return x

if __name__ == "__main__":
    x0 = np.array([0, 0, 0.3, 0])
    print(f"MPC 控制倒立摆(初始偏角 0.3):")
    mpc_cartpole(x0)
    print(f"\n洞察: 真实 MPC 用 cvxpy/osqp 解 QP, 这里暴力枚举仅 demo 原理.")
```

## 4. EKF SLAM 简化（1D 跟踪）

```python
import numpy as np

def ekf_1d_step(x, P, z, u, Q=0.1, R=0.5):
    """1D EKF: 预测(运动) + 更新(观测)."""
    # 预测
    x_pred = x + u
    P_pred = P + Q
    # 更新(观测=位置直接观测)
    K = P_pred / (P_pred + R)
    x_new = x_pred + K * (z - x_pred)
    P_new = (1 - K) * P_pred
    return x_new, P_new

if __name__ == "__main__":
    x, P = 0.0, 1.0  # 初始位置估计 + 不确定度
    true_traj = [0.5*i for i in range(20)]  # 真实轨迹
    print("EKF 跟踪 1D 轨迹:")
    for t in range(20):
        u = 0.5  # 控制(预期前进 0.5)
        z = true_traj[t] + np.random.randn()*0.5  # 带噪声的观测
        x, P = ekf_1d_step(x, P, z, u)
        if t % 5 == 0:
            print(f"  t={t} 真实={true_traj[t]:.2f} 观测={z:.2f} 估计={x:.2f}±{P:.2f}")
    print(f"\nEKF 融合了预测(运动)和观测(传感器), 比单独用任一更准.")
```

## 这段代码教什么

1. **解析 IK**：余弦定理 + atan2，2 连杆有闭式解
2. **LQR**：解 Riccati 得最优增益，倒立摆能拉回平衡
3. **MPC**：每步解有限时域最优，能处理约束（真实用 cvxpy/osqp）
4. **EKF**：预测+更新两步，融合运动预测和传感器观测

**生产化**：用 Pinocchio（动力学库）/ CasADi（最优控制）/ GTSAM（因子图）/ ORB-SLAM3（视觉 SLAM）。

📌 **下一张卡** → `04-不足-Sim2Real与接触.md`
