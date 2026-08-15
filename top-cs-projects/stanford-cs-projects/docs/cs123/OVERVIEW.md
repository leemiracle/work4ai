# CS123: Building AI-Enabled Robots

> Stanford University | 本科 / 研究生 | 软硬件一体化机器人实战
> Instructors: **Karen Liu**（机器人仿真 / 物理动画）+ **Jie Tan**（Google DeepMind，机器人学习）
> 先修: 编程基础 + 基础线性代数
> 难度: ⭐⭐⭐⭐（硬件 + 软件 + AI 三位一体）
> 定位: 学生亲手造一只 **Pupper 机器狗**，8 个 Lab 全栈实战

---

## 📚 课程定位

CS123 是 Stanford **最独特的机器人实战课**——每位学生从零组装一只开源四足机器狗 **Pupper**，并通过 8 个递进式 Lab 让它学会站立、行走、遥控和（用 AI）自主行动。课程融合**机械组装、嵌入式固件、控制算法与机器学习**，是真正的"软硬结合"。

### Karen Liu 教授
- Stanford CS 教授，研究方向：物理仿真、机器人学习、布料/毛发动画
- 代表作：DiffSim、可微仿真用于机器人策略学习

### Jie Tan（Google DeepMind）
- DeepMind 机器人团队负责人，研究方向：机器人运动学习、Sim-to-Real
- 代表作：四足机器人 RL 运动、Sim-to-Real 迁移

### Pupper 机器狗
- Stanford 学生机器人社团（Stanford Student Robotics）设计的**开源四足机器人**
- 成本约 $300-$600，3D 打印件 + 舵机 + 树莓派/ESP32
- 社区：pupper（GitHub），让每个学生都能拥有自己的"小 Spot"

---

## 🎯 学习目标

1. **组装**一只完整的四足机器狗（机械 + 电路 + 固件）
2. 实现**逆运动学**，控制 12 个舵机完成步态
3. 用经典控制让 Pupper **站立、平衡、行走**
4. 用**强化学习**（Sim-to-Real）训练运动策略
5. 用手机/手柄**遥控**，并接入摄像头做感知

---

## 📅 核心模块（8 个 Lab）

| Lab | 主题 | 内容 |
|-----|------|------|
| **Lab 1** | 组装 | 3D 打印件装配 + 舵机标定 + 接线 |
| **Lab 2** | 固件 | 树莓派/ESP32 环境 + 舵机驱动 |
| **Lab 3** | 逆运动学 | 足端坐标 → 关节角度（3-DOF 腿） |
| **Lab 4** | 站立与平衡 | 重心控制 + 稳定姿态 |
| **Lab 5** | 步态生成 | Trot / Crawl 步态时序 |
| **Lab 6** | 遥控交互 | 手柄/手机 App + 速度指令 |
| **Lab 7** | 感知 | 摄像头 + 简单视觉（跟随/避障） |
| **Lab 8** | AI 运动 | RL 训练（Sim-to-Real）策略部署 |

---

## 💻 项目代码

📁 `topic5-robot/motion_planner.py`（Pupper 控制相关模块）

Pupper 的运动控制依赖本课程的核心算法，共享代码中实现：
1. ✅ **运动学**：差速驱动模型（足端/关节映射的简化版）
2. ✅ **PID 控制**：舵机角度闭环（Pupper 平衡的核心）
3. ✅ **轨迹规划**：步态路径生成（A* / RRT 用于导航）

### 运行
```bash
cd topic5-robot
python3 motion_planner.py
```

> Pupper 的逆运动学核心：给定足端目标位置 $(x, y, z)$，求三关节角度 $(\theta_1, \theta_2, \theta_3)$。PID 控制器维持机身姿态稳定。

---

## 📊 关键概念/论文

### 🔴 必读 P0
1. **Stanford Pupper 文档**（GitHub: stanfordstudentrobotics/pupper）
2. **Tan et al. (Google)** "Sim-to-Real: Robot Learning from Simulated Perception"
3. **Hwangbo 2019** "Learning agile and dynamic motor skills for legged robots"（ANYmal RL）

### 🟡 P1
4. Karen Liu — 可微仿真（DiffSim）系列论文
5. **Hutter et al.** ANYmal 四足机器人系列
6. Boston Dynamics Spot 公开技术资料

### 核心概念
- **逆运动学（IK）**：足端 → 关节角
- **Sim-to-Real**：仿真训练策略 → 真实机器人部署
- **Trot 步态**：对角腿同步，动态平衡
- **模型预测控制（MPC）**：足端力优化

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **机器人全栈** | CS123 是软硬结合的最佳起点 |
| **强化学习实战** | 想把 RL 部署到真机的学生 |
| **硬件创客** | 喜欢动手组装 + 写固件的极客 |
| **Sim-to-Real 研究** | CS123 → 读 DeepMind / ETH 论文 |

---

## 🚀 扩展

完成后推荐：
1. **CS137A / CS237A** — 运动规划与控制理论深化
2. **CS238** — Decision Making under Uncertainty（POMDP）
3. **CS227A** — Robot Perception（视觉 / SLAM）
4. 开源社区：Pupper v2 / Stanford Quadruped / MIT Mini Cheetah
5. 实习：Boston Dynamics / Figure / Tesla Optimus / Unitree / Google DeepMind

---

**对应代码**: `topic5-robot/motion_planner.py`
