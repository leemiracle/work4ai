# CS42SI: 2D Game Development

> Stanford University, Autumn 2026
> 领域: 游戏开发 / 实践（Student Initiated）
> Prerequisites: CS106A 或同等编程基础
> Units: 2-3
> Difficulty: ⭐⭐

---

## 📚 定位

从零构建 2D 游戏——通过实战学习游戏循环、渲染、碰撞、状态管理，产出可玩的作品。

---

## 🎯 学习目标

- 理解并实现游戏循环（Game Loop）
- 掌握 2D 图形渲染与精灵动画
- 实现碰撞检测与物理响应
- 管理游戏状态与实体架构（ECS）

---

## 📅 核心模块

### Module 1: 游戏循环与架构
- 输入 → 更新 → 渲染
- 帧率控制（FPS）与 delta time
- 固定时间步 vs 可变时间步

### Module 2: 渲染与精灵
- 2D 图形 API（Canvas / SDL / Pygame）
- 精灵图集（Sprite Sheet）与动画帧
- 摄像机与视口滚动

### Module 3: 碰撞与物理
- AABB 碰撞检测
- 分离轴定理（SAT）
- 简单物理响应（反弹、摩擦）

### Module 4: 游戏架构
- Entity-Component-System（ECS）
- 状态机（菜单 / 游戏 / 暂停）
- 场景管理与对象池

### Module 5: 发布与迭代
- 音效与音乐集成
- 关卡设计工具
- 游戏测试与平衡

---

## 💻 项目代码

📁 `supplementary/all_micro_projects.py::cs42si_game_loop`

**实现内容**:
1. ✅ 经典游戏循环结构展示
2. ✅ 帧率控制概念（60 FPS = 16.7ms/帧）
3. ✅ Delta time 与帧率无关物理
4. ✅ ECS 架构概念说明

**运行**:
```bash
cd supplementary
python3 all_micro_projects.py
```

**核心概念输出**:
```
经典游戏循环:
while running:
    process_input()      # 输入
    update_state(dt)     # 物理更新
    render()             # 渲染
    dt = clock.tick(60)  # 控制帧率

关键概念:
- 帧率 (FPS): 60 fps = 16.7ms/帧
- delta time: 与帧率无关的物理
- ECS 架构: Entity / Component / System
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **Game Loop** | 游戏的心跳：输入→更新→渲染 |
| **ECS** | Entity-Component-System，数据导向架构 |
| **Delta Time** | 保证物理在不同帧率下一致 |
| **Sprite Sheet** | 精灵图集，高效渲染动画 |
| **AABB** | 轴对齐包围盒，快速碰撞检测 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **想入门游戏开发** | CS42SI → 独立游戏 |
| **CS106A 后实践** | 互动编程提升 |
| **Unity / Godot 学习者** | 底层原理补充 |
| **创意编程** | 游戏即交互艺术 |

---

## 🚀 扩展方向

1. 用 Pygame / LÖVE 完成一个完整小游戏
2. 学习 Godot 引擎（开源，GDScript）
3. 参与 Ludum Dare 游戏开发比赛
4. 进阶：CS377G（严肃游戏设计）

---

**对应代码**: `supplementary/all_micro_projects.py::cs42si_game_loop`
