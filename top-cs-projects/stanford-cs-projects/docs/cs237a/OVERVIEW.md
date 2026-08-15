# CS237A: Principles of Robot Autonomy I

> Stanford University, Autumn 2025
> Instructors: **Sushant Veerendra Bansal** + **Marco Pavone** (NASA 自动驾驶顾问)
> Time: Tue/Thu 1:30-2:50 PM
> Prerequisites: 推荐线性代数 + 概率 + 编程
> Difficulty: ⭐⭐⭐⭐⭐

---

## 📚 课程定位

Stanford 机器人学**研究生旗舰课**。Pavone 是 NASA 自动驾驶顾问，研究方向涵盖：

- 运动规划（A*, RRT, RRT*）
- 反馈控制（PID, LQR, MPC）
- 状态估计（KF, EKF, Particle Filter）
- Learning-based 控制
- **LLM + Robotics**（最新方向）

---

## 📅 推测模块（基于 Pavone 经典教案）

### Part 1: 机器人数学基础
- SE(3) / SO(3) 群
- 李群 / 李代数
- 齐次变换矩阵
- 四元数

### Part 2: 运动规划
- **Graph search**: BFS / DFS / Dijkstra / A*
- **Sampling-based**: RRT / RRT* / PRM
- **Optimization-based**: CHOMP / TrajOpt
- **Learning-based**: Neural Motion Planning

### Part 3: 反馈控制
- **PID** — 经典
- **LQR** (Linear Quadratic Regulator)
- **MPC** (Model Predictive Control)
- **Lyapunov stability**

### Part 4: 状态估计
- **Bayes filter**
- **Kalman Filter** (KF)
- **Extended KF** (EKF)
- **Particle Filter** (Monte Carlo Localization)

### Part 5: 视觉感知（与 CS227A 重叠）
- SLAM
- Visual odometry
- Object detection for robots

### Part 6: Learning-based 控制
- Imitation Learning (Behavior Cloning)
- Reinforcement Learning (PPO, SAC)
- **Diffusion Policy** (2023) — Stanford 亮点

### Part 7: LLM + Robotics ⭐
- **RT-1, RT-2** (Google Robotics)
- **RT-X** (Open X-Embodiment)
- **VoxPoser** (Stanford)
- SayCan / PaLM-E

### Part 8: 自动驾驶专题
- Apollo / Waymo 架构
- Behavioral planning
- Safety guarantee

---

## 🧮 核心算法

### A* Path Planning
$$f(n) = g(n) + h(n)$$
- $g(n)$: start → n 的实际代价
- $h(n)$: n → goal 的启发式估计（admissible）

### RRT (Rapidly-exploring Random Tree)
```
T = {start}
for k iterations:
    x_rand = sample(random)
    x_nearest = nearest(T, x_rand)
    x_new = steer(x_nearest, x_rand, step)
    if collision_free(x_new):
        T.add(x_new, parent=x_nearest)
        if close(x_new, goal):
            return path(x_new)
```

### PID Controller
$$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

### Extended Kalman Filter
```
预测: x̂ = f(x, u); P = F P F^T + Q
更新: K = P H^T (H P H^T + R)^-1
      x̂ += K (z - h(x̂))
      P = (I - K H) P
```

---

## 💻 项目代码

📁 `topic5-robot/motion_planner.py`

**实现**（纯 numpy）：
1. ✅ A* 路径规划（8-connectivity）+ ASCII 可视化
2. ✅ RRT 简化版
3. ✅ PID 控制（含质量-摩擦系统仿真）
4. ✅ 差速驱动运动学

### 运行
```bash
cd topic5-robot
python3 motion_planner.py
```

**A* 输出示例**:
```
   Path found (15 steps):
     . . . . . . . . . .
     . . . . . . . . . .
     . . . . . . . . . .
     . . . █ █ █ . . . .
     . . . █ . . █ . . .
     S . . █ . . █ . . .
     · . . █ . . █ . . .
     · . . . . . █ . . .
     · · · · · . █ . . .
     · · · · · . █ . . G
```

---

## 📊 关键论文

### 🔴 P0
1. **LaValle 1998** "RRT" 
2. **Kavraki 1996** "PRM"
3. **Khatib 1986** "Potential Fields"
4. **Schulman 2014** "Motion Planning as Sequential Optimization"

### 🟡 P1
5. LaValle *Planning Algorithms* (教材，免费)
6. Thrun *Probabilistic Robotics* (教材)
7. **Brohan 2023** "RT-2"
8. **Chi 2023** "Diffusion Policy"

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **机器人研究** | CS237A → CS238 (POMDP) |
| **自动驾驶** | CS237A → CS238 + 实习 Waymo/Tesla |
| **LLM + Robotics** | CS237A → 读 RT-2/RT-X |
| **机器人工程** | CS137A (本科) → CS123 (Pupper) |

---

## 🚀 扩展

完成后推荐：
1. **CS227A** Robot Perception
2. **CS238** Decision Making under Uncertainty
3. **CS123** Building AI Robots (Pupper 实战)
4. 实习: Figure / Tesla / Boston Dynamics / 1X

---

**对应代码**: `topic5-robot/motion_planner.py`
