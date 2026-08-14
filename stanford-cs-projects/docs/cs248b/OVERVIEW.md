# CS248B: Animation and Simulation

> Stanford University, Autumn 2026
> 领域: 物理仿真 / 计算机动画
> Prerequisites: 线性代数 + 微积分 + 编程基础
> Units: 3-4
> Difficulty: ⭐⭐⭐⭐

---

## 📚 定位

用数值方法模拟物理世界——从弹球到流体，理解电影特效与游戏引擎背后的数学引擎。

---

## 🎯 学习目标

- 掌握常微分方程（ODE）的数值积分方法
- 理解刚体、柔体、流体不同仿真模型
- 能实现基础物理引擎（碰撞、约束、力）
- 理解稳定性与数值误差的工程权衡

---

## 📅 核心模块

### Module 1: 运动学与数值积分
- 欧拉法（显式 / 隐式）
- Verlet 积分
- Runge-Kutta 方法
- 时间步长与稳定性

### Module 2: 质点-弹簧系统
- 胡克定律与阻尼
- 布料仿真
- 约束求解（位置投影）

### Module 3: 刚体动力学
- 质心、转动惯量
- 碰撞检测（AABB、GJK）
- 碰撞响应（冲量法）

### Module 4: 流体仿真
- Navier-Stokes 方程
- 欧拉方法（网格）
- SPH（光滑粒子流体动力学）
- 浅水方程

### Module 5: 高级主题
- 有限元方法（FEM）
- 有限元变形体
- 群体动画（Boids）
- 可微仿真与机器学习

---

## 💻 项目代码

📁 `supplementary/final_projects.py::cs248b_demo`

**实现内容**:
1. ✅ 简化重力弹球仿真（150 步）
2. ✅ 欧拉积分（速度 → 位置更新）
3. ✅ 碰撞反弹（弹性系数 0.8）
4. ✅ ASCII 轨迹可视化

**运行**:
```bash
cd supplementary
python3 final_projects.py
```

**输出示例**:
```
弹球轨迹（前 10 步）:
  t=  0:   ●  (h=10.00m)
  t=  1:  ●  (h=9.99m)
  ...
  t=  8:          ●  (h=0.00m) ← 触地反弹
关键: Verlet integration / 刚体 / 流体（SPH, Navier-Stokes）
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **Verlet 积分** | 能量守恒优于欧拉法 |
| **SPH** | 光滑粒子流体动力学 |
| **Navier-Stokes** | 流体运动基本方程 |
| **碰撞检测** | AABB / GJK / SAT |
| **可微仿真** | ∂物理/∂参数 → 梯度优化 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **想做游戏引擎** | CS248B → 物理 SDK 开发 |
| **电影特效** | 流体 / 破碎仿真 |
| **机器人仿真** | MuJoCo / Isaac Sim 基础 |
| **AI for Science** | 可微仿真 = 梯度来源 |

---

## 🚀 扩展方向

1. 使用 Box2D / Bullet 物理引擎
2. 探索 Houdini（影视级仿真工具）
3. 学习 Position Based Dynamics（PBD）
4. 阅读 *Fluid Simulation for Computer Graphics* (Bridson)

---

**对应代码**: `supplementary/final_projects.py::cs248b_demo`
