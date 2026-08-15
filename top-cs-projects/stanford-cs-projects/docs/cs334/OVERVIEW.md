# CS334: Robots and Arts

> Stanford University, Autumn 2026
> 领域: 机器人 + 创意艺术
> Prerequisites: 编程基础；艺术兴趣
> Units: 3-4
> Difficulty: ⭐⭐⭐

---

## 📚 定位

探索机器人作为艺术媒介——从生成式运动到人机共演，技术驱动的新型艺术表达。

---

## 🎯 学习目标

- 理解机器人运动学基础（前向/逆向）
- 掌握生成式艺术算法（L-system、元胞自动机）
- 能设计机器人行为编排（编舞）
- 探索人机交互的美学维度

---

## 📅 核心模块

### Module 1: 机器人作为艺术工具
- 机械臂的历史（工业 → 艺术装置）
- 绘画机器人（e-David、Paul-IX）
- 装置艺术中的机器人

### Module 2: 运动学基础
- 前向运动学（关节角 → 末端位置）
- 逆向运动学（目标 → 关节角）
- 轨迹规划与平滑插值

### Module 3: 生成式运动
- L-system 与分形运动轨迹
- 元胞自动机（Conway 生命游戏）
- Boids 群体行为
- 反应扩散系统

### Module 4: 人机协作表演
- 机器人舞蹈编排
- 实时交互（传感器 → 动作）
- 延迟、安全与即兴

### Module 5: 美学与哲学
- 创造力能否被编程？
- 作者权：人 / 机器人 / 算法？
- 机器美学（包豪斯 → 数控美学）

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs334_demo`

**实现内容**:
1. ✅ L-system 字符串重写系统（3 次迭代）
2. ✅ 分形动作序列生成（F+F-F-F+F）
3. ✅ 机器人路径模拟（2D 坐标 + 角度）
4. ✅ 轨迹路径点统计

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
L-system 动作序列 (长度 76): F+F-F-F+F+F+F-F-F+F+F+F-F-F+F...
路径点数: 77, 最终位置: (12.0, 0.0)
关键: L-system / 生成艺术 / 物理交互
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **L-system** | Lindenmayer 系统，分形生成 |
| **运动学** | 关节空间 ↔ 笛卡尔空间 |
| **Boids** | Reynolds 群体行为模型 |
| **元胞自动机** | 离散空间的规则演化 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **艺术 + 技术** | CS334 = 媒体艺术的机器人入口 |
| **机器人方向** | 不同于工业应用的新视角 |
| **生成艺术** | L-system / CA 的物理实现 |
| **新媒体艺术** | 装置设计 |

---

## 🚀 扩展方向

1. 学习 Processing / openFrameworks 创意编程
2. 探索 Universal Robots 艺术项目案例
3. 研究 Bot & Dolly（电影级机器人摄影）
4. 阅读 *The Art of Artificial Evolution* (Richter)

---

**对应代码**: `supplementary/undergrad_projects.py::cs334_demo`
