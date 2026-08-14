# CS137A: Principles of Robot Autonomy I (本科)

> Stanford University | 本科课程 | CS237A 的本科版本
> Instructor: **Marco Pavone**（NASA 自动驾驶顾问，机器人规划与控制权威）
> 先修: 线性代数 + 概率 + 编程基础
> 难度: ⭐⭐⭐⭐
> 定位: 本科生版机器人自主性，运动规划 + 控制 + 状态估计

---

## 📚 课程定位

CS137A 是研究生旗舰课 **CS237A（Principles of Robot Autonomy I）的本科版本**，由同一讲师 **Marco Pavone** 教授。Pavone 是 NASA 自动驾驶顾问，研究方向涵盖运动规划、反馈控制、状态估计与 LLM + Robotics。本科版在数学深度上略作简化，更强调工程实现与直觉建立。

> 与 CS237A 共享 `topic5-robot/motion_planner.py` 代码。

---

## 🎯 学习目标

1. 掌握经典**运动规划**算法（A* / RRT / RRT*）
2. 理解并实现**反馈控制**（PID / LQR 基础）
3. 学习**状态估计**（Kalman Filter / Particle Filter 直觉）
4. 了解 **Learning-based 控制**与 **LLM + Robotics** 前沿
5. 用纯 numpy 从零实现机器人核心算法

---

## 📅 核心模块

### Part 1: 机器人数学基础
- 坐标变换 / 齐次变换矩阵
- 2D / 3D 运动学（差速驱动 / 阿克曼）

### Part 2: 运动规划
- **图搜索**: BFS / DFS / Dijkstra / **A***
- **采样规划**: **RRT** / RRT* / PRM
- 势场法（Potential Fields）

### Part 3: 反馈控制
- **PID** 控制（经典）
- LQR（Linear Quadratic Regulator）基础
- 轨迹跟踪

### Part 4: 状态估计
- Bayes Filter 直觉
- **Kalman Filter**（KF）
- Extended KF / Particle Filter（蒙特卡洛定位）

### Part 5: 前沿专题
- Imitation Learning / RL（PPO, SAC）
- **Diffusion Policy**（2023, Stanford）
- LLM + Robotics（RT-1 / RT-2 / SayCan）

---

## 💻 项目代码

📁 `topic5-robot/motion_planner.py`（与 CS237A 共享）

**实现内容**（纯 numpy / stdlib）：
1. ✅ **A\* 路径规划**（8-connectivity）+ ASCII 网格可视化
2. ✅ **RRT 简化版**（随机采样 + 碰撞检测 + 目标偏置）
3. ✅ **PID 控制**（含质量-摩擦系统仿真，观测上升时间）
4. ✅ **差速驱动运动学**（走方形轨迹验证）

### 运行
```bash
cd topic5-robot
python3 motion_planner.py
```

**A\* 输出示例**：15 步路径 + ASCII 网格图（S 起点、G 目标、█ 障碍、· 路径点）。

---

## 📊 关键概念/论文

### 🔴 必读 P0
1. **LaValle 1998** "Rapidly-exploring Random Trees"（RRT）
2. **Kavraki 1996** "Probabilistic Roadmaps"（PRM）
3. **Khatib 1986** "Real-Time Obstacle Avoidance"（势场法）

### 🟡 P1
4. LaValle *Planning Algorithms*（免费教材）
5. Thrun *Probabilistic Robotics*（KF / PF 教材）
6. **Chi 2023** "Diffusion Policy"（Stanford 亮点）
7. **Brohan 2023** "RT-2"（Google Robotics）

### 核心公式
- A\*: $f(n) = g(n) + h(n)$（实际代价 + 启发式估计）
- PID: $u(t) = K_p e + K_i \int e\,dt + K_d \frac{de}{dt}$

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **本科机器人入门** | CS137A 是最佳起点（比 CS237A 更友好） |
| **自动驾驶** | CS137A → CS238（POMDP）+ 实习 |
| **LLM + Robotics** | 读 RT-2 / RT-X |
| **硬件实战** | CS137A → CS123（Pupper 机器狗） |

---

## 🚀 扩展

完成后推荐：
1. **CS237A** — 研究生版，数学更深（李群 / MPC / EKF 严格推导）
2. **CS238** — Decision Making under Uncertainty（POMDP）
3. **CS123** — Building AI-Enabled Robots（亲手造 Pupper）
4. **CS227A** — Robot Perception（SLAM / 视觉）

---

**对应代码**: `topic5-robot/motion_planner.py`
