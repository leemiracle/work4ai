# 计算机图形学 + Web 开发 + 数据科学 深度展开（11 门）

> **来源**：csdiy.wiki + librarian delegate（calm-jade-tiger）实际 webfetch 验证
> **判定基准**：飞腾 D3000 NEON 算子优化项目

---

## 一、计算机图形学（6 门）

图形学与项目的交集：**光栅化、光线追踪、蒙特卡洛渲染、卷积、数值线性代数**都是密集浮点计算，是 SIMD/NEON 优化的典型场景。

### GAMES101 —— 现代计算机图形学入门 ｜ 中等
- **大学/讲师**：UCSB · **闫令琪**（Lingqi Yan，实时光线追踪推动者）
- **难度**：🌟🌟🌟 ｜ **学时**：80h
- **官网**：http://games-cn.org/intro-graphics/
- **视频**：https://www.bilibili.com/video/BV1X7411F744
- **GitHub**：https://github.com/ysj1173886760/Learning/tree/master/graphics/GAMES101
- **作业**：8 个 project（C++ 实现光栅化器 + 光线追踪器）
- **项目价值**：**光栅化与光线追踪正是 NEON SIMD 优化的典型算子目标**（矩阵乘、插值、像素填充）——理解这些 workload 的计算特征，有助于判断哪些算子值得向量化

### GAMES202 —— 高质量实时渲染 ｜ 弱
- **难度**：🌟🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://sites.cs.ucsb.edu/~lingqi/teaching/games202.html
- **视频**：https://www.bilibili.com/video/BV1YK4y1T7yY
- GAMES101 进阶：实时软阴影、环境光照、PBR、实时光线追踪、抗锯齿/超采样

### GAMES103 —— 基于物理的计算机动画 ｜ 弱
- **难度**：🌟🌟🌟🌟 ｜ **学时**：50h
- **官网**：http://games-cn.org/games103/
- **视频**：https://www.bilibili.com/video/BV12Q4y1S73g
- **GitHub**：https://github.com/indevn/GAMES103
- 物理动画模拟：刚体 / 布料 / 有限元弹性体 / 流体
- **价值**：物理模拟含大量数值求解，理论上是 NEON 加速对象

### Stanford CS148 ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：40h
- **官网**：https://web.stanford.edu/class/cs148/index.html
- 图形学入门（Python + Blender），三角形/法向量/纹理/BRDF/光线追踪

### ⭐ CMU 15-462 —— Computer Graphics ｜ 中等
- **难度**：🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：http://15462.courses.cs.cmu.edu/fall2022/
- **视频**：https://www.youtube.com/watch?v=W6yEALqsD7k
- 硬核图学金标准：采样/卷积/光栅化/光线追踪/**蒙特卡洛渲染 + 重要性采样**/数值微分/逆运动学/傅立叶方法
- **核心价值**：**蒙特卡洛渲染、卷积、数值线性代数**是密集浮点计算，正是 NEON 优化的高价值场景；数学深度高于 GAMES101

### USTC CG（刘利刚）｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：100h
- **官网**：http://staff.ustc.edu.cn/~lgliu/Courses/ComputerGraphics_2020_spring-summer/default.htm
- **视频**：https://www.bilibili.com/video/BV1iT4y1o7oM
- 比 GAMES101 更全面（含离散几何处理），数学化

---

## 二、Web 开发（4 门）｜ 整体相关度：弱

> 这四门均属应用层 Web 技术，与 NEON 算子优化/CXL 无任何交集。仅当项目需要配套测试工具链或可视化前端时才有间接价值。

### MIT Web (6.148/WebLab)
- **难度**：🌟🌟🌟 ｜ **学时**：4 周速成
- **官网**：https://weblab.mit.edu/schedule/
- 4 周速成前后端全栈，从零搭网站

### Stanford CS142
- **难度**：🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：https://web.stanford.edu/class/cs142/index.html
- **视频**：https://web.stanford.edu/class/cs142/lectures.html
- React/Node/Express/Web 安全，8 个 Project

### fullstackopen（University of Helsinki）
- **难度**：🌟🌟 ｜ 入门难度最低
- **官网**：https://fullstackopen.com/zh/
- React SPA + Node REST API + GraphQL + MongoDB

### CS571（UW-Madison）
- **难度**：🌟🌟🌟 ｜ **学时**：12 周 × (2h 讲座 + 4-10h 作业)
- **官网**：https://cs571.org/（邮箱免费申请 Badger ID）
- React + **React Native 移动端**最佳实践，含 DialogFlow/UX Design，每学期更新

---

## 三、数据科学（1 门）｜ 弱

### UCB Data100 —— Principles and Techniques of Data Science
- **难度**：🌟🌟🌟 ｜ **学时**：80h
- **官网**：https://ds100.org/
- **教材**：https://www.textbook.ds100.org/intro.html
- 数据清洗 / 特征工程 / 可视化 / ML 与推理基础（Python/Pandas/NumPy/Matplotlib）
- **价值**：上层分析，与底层算子优化无关

---

## 项目相关性总览

| 等级 | 课程 | 核心理由 |
|---|---|---|
| **🟡 中等** | GAMES101、CMU 15-462 | 光栅化/蒙特卡洛/卷积是 SIMD 优化高价值场景 |
| **🟢 弱** | GAMES202/103、CS148、USTC CG、4 门 Web、Data100 | 偏渲染算法或上层应用，可选作知识广度补充 |

**建议优先级**：若聚焦 NEON 算子优化，**GAMES101 + CMU 15-462** 是图形学里唯二相关的（理解光栅化/蒙特卡洛的计算特征）；其余课程与项目无直接工程价值，仅作通识。
