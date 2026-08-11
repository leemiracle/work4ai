# CS44N: Great Ideas in Graphics

> Stanford University, Autumn 2026
> 领域: 计算机图形学 / 通识入门
> Prerequisites: 微积分 + 基础编程
> Units: 3-4
> Difficulty: ⭐⭐⭐

---

## 📚 定位

面向非专业学生的图形学启蒙——聚焦"伟大思想"而非数学推导，理解如何用计算创造视觉世界。

---

## 🎯 学习目标

- 理解图形学核心思想的历史脉络
- 掌握光栅化与光线追踪的基本原理
- 能用数学描述 3D 物体的形状与运动
- 欣赏从早期 DEMO 到现代电影的视觉技术

---

## 📅 核心模块

### Module 1: 从线框到照片级
- 图形学简史（Sutherland → Pixar → RTX）
- 渲染管线概览
- 坐标变换（模型→世界→视图→投影）

### Module 2: 光栅化
- 三角形投影到屏幕
- 深度缓冲（Z-buffer）
- 着色模型（Flat / Gouraud / Phong）

### Module 3: 光线追踪
- 从眼睛出发追光（Whitted 1980）
- 反射、折射、阴影
- 蒙特卡洛路径追踪

### Module 4: 几何与建模
- 参数曲面 vs 网格
- 细分曲面（Subdivision Surfaces）
- Level of Detail（LOD）

### Module 5: 动画与物理
- 关键帧动画
- 逆向运动学（IK）
- 物理仿真与刚体动力学

---

## 💻 项目代码

📁 `supplementary/final_projects.py::cs44n_demo`

**实现内容**:
1. ✅ 8 大图形学核心思想概览
2. ✅ Ray Tracing / Rasterization / Radiosity 等概念梳理
3. ✅ BRDF / IK / LOD 等技术要点

**运行**:
```bash
cd supplementary
python3 final_projects.py
```

**输出示例**:
```
• Ray Tracing              : 从眼睛出发追光
• Rasterization            : 把三角形投影到屏幕
• Radiosity                : 全局光照 (漫反射间)
• Subdivision Surfaces     : Pixar 的有机造型
• Photon Mapping           : Caustics / 焦散
```

> 另见 `topic11-graphics/ray_tracer.py` — 光线追踪器实现

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **Ray Tracing** | 从眼睛逆向追光，逼真但慢 |
| **Rasterization** | 实时渲染主流，GPU 核心 |
| **BRDF** | 双向反射分布函数 |
| **Subdivision** | Pixar 的有机角色造型 |
| **Global Illumination** | 全局光照（间接光） |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **图形学入门** | CS44N → CS148 → CS248A |
| **游戏开发** | 理解渲染原理 |
| **视觉艺术** | 数学创造美 |
| **通识选修** | 无高深数学也能学 |

---

## 🚀 扩展方向

1. 学习 OpenGL / WebGL（`topic11-graphics/ray_tracer.py`）
2. 阅读 *Fundamentals of Computer Graphics* (Marschner)
3. 尝试 Blender（开源 3D 建模/渲染）
4. 探索 CS148（交互式图形学）

---

**对应代码**: `supplementary/final_projects.py::cs44n_demo` + `topic11-graphics/ray_tracer.py`
