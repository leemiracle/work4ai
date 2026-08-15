import numpy as np
import math

# ===== Pure Pursuit 横向控制最小实现 =====
# 直觉：把车想象成"追"路径前方一个前瞻点，方向盘 = arctan(2*L*sin(alpha)/Ld)
def bicycle_kinematic(state, accel, delta, dt, L=2.5):
    x, y, yaw, v = state
    x += v * math.cos(yaw) * dt
    y += v * math.sin(yaw) * dt
    yaw += (v / L) * math.tan(delta) * dt   # 运动学自行车模型
    v += accel * dt
    return [x, y, yaw, v]

def pure_pursuit(state, path, Ld, L=2.5):
    x, y, yaw, v = state
    # 找前瞻点（路径上距离车 Ld 处）
    dists = np.hypot(path[:,0]-x, path[:,1]-y)
    idx = np.argmin(dists)
    # 向前找 Ld 距离的点（前瞻距离可随速度自适应 Ld = k*v）
    lookahead = Ld + 0.5 * v
    target_idx = idx
    cum = 0
    for i in range(idx, len(path)-1):
        cum += np.hypot(*(path[i+1]-path[i]))
        if cum >= lookahead:
            target_idx = i+1
            break
    tx, ty = path[target_idx]
    alpha = math.atan2(ty-y, tx-x) - yaw        # 目标方向与车头角之差
    delta = math.atan2(2 * L * math.sin(alpha), lookahead)  # 核心公式
    return delta

# 生成一条 S 弯参考路径
path = np.array([[i*0.5, 3*math.sin(i*0.3)] for i in range(100)])
state = [0, 0, 0.2, 5.0]  # x,y,yaw,v
traj = []
for _ in range(400):
    delta = pure_pursuit(state, path, Ld=3.0)
    state = bicycle_kinematic(state, accel=0, delta=delta, dt=0.1)
    traj.append(state[:2])
traj = np.array(traj)

# 评估跟踪误差
err = np.min(np.hypot(traj[:,0:1]-path[:,0:1].T, traj[:,1:2]-path[:,1:2].T), axis=1)
print(f"Pure Pursuit 跟踪完成: 平均横向误差 = {err.mean():.3f} m, 最大 = {err.max():.3f} m")
print(f"核心公式验证: 当 alpha=30°, Ld=5m, L=2.5m -> delta = {math.degrees(math.atan2(2*2.5*math.sin(math.radians(30)),5)):.2f}°")
