# top-math-courses：顶级数学院校课程全景

> **一句话定位**：仿照 [`top-cs-projects/`](../top-cs-projects/) 的方法论，把全球 9 所顶级数学名校的本科+研究生课程**一手核实、系统化整理**，专门服务你"**应用数学研究型工程师**"的最终目标（方向候选：ML 理论 / 概率随机过程 / 数值分析 / 优化 / 信息论）。
>
> **与 `top-cs-projects/` 的关系**：CS 版教"怎么造轮子"，数学版教"轮子背后的几何/代数/分析/概率原理"。两者**正交互补**——ML 工程师的"完整教育" = top-cs-projects（工程）+ top-math-courses（理论）。

---

## 为什么需要这个系列

你的最终目标是 **数学专家**（每周 10-20h，6-8 年达研究入门级）。当前数学自评 **0**（线代/概率/微积分/优化全 0），但**逻辑思维强**。

直接读论文 / 顶会博士班的教材（如 Vershynin *High-Dimensional Probability*、Boyd *Convex Optimization*）会卡在最基础的实分析/测度论/线性代数（高维）上。

**唯一可行的路径**：从顶级数学本科项目的基础课切入，**系统地**补 4 年本科 + 2 年研究生的数学基础。

而顶级数学项目的课程设置本身经历了**几代数学家的反复打磨**——MIT 18.100 实分析、Cambridge Part IB Linear Algebra、Princeton MAT215 单变量分析——这些课程的教学质量**远超**任何自学教材。

## 选校逻辑（与 top-cs-projects 对齐 9 校）

| # | 学校 | 中文 | 数学强项 | 与你方向的相关性 |
|---|---|---|---|---|
| 1 | **MIT** | 麻省理工 | 应用数学、概率、数值分析、信息论 | ★★★★★（核心） |
| 2 | **Princeton** | 普林斯顿 | 纯数学、几何、拓扑、解析数论 | ★★★（基础）|
| 3 | **Harvard** | 哈佛 | 纯数学、数论、几何 | ★★★（基础）|
| 4 | **Stanford** | 斯坦福 | 应用数学、金融数学、优化 | ★★★★★（核心） |
| 5 | **Berkeley** | 伯克利 | 概率、应用数学、调和分析 | ★★★★（核心） |
| 6 | **Cambridge** | 剑桥 | Part III（研究生黄金标准）| ★★★★★（核心）|
| 7 | **Oxford** | 牛津 | 几何、随机分析、随机矩阵 | ★★★★ |
| 8 | **ETH Zurich** | 苏黎世理工 | 应用数学、概率、数值分析 | ★★★★★（核心）|
| 9 | **UT Austin** | 库朗研究所 | 应用数学、数值分析、概率 | ★★★★★（核心）|

> 选校不仅看综合排名，更看**与你方向（ML 理论/概率/数值/优化/信息论）的匹配度**——所以 UT Austin（Shanghai 数学 #5，应用数学顶级）、ETH（数值+概率强）、MIT（信息论发源地）权重高于纯数学最强的 Princeton/Harvard。

## 课程覆盖范围

9 校 × 平均每校 15-25 门核心课 = **150-200 门数学课**。按 5 大方向分类：

| 方向 | 代表课程 | 你的目标关联 |
|---|---|---|
| **分析（Analysis）** | MIT 18.100/100B, Princeton MAT215, Cambridge Analysis I/II, Harvard Math 112 | ML 理论的基石（测度、收敛、积分） |
| **代数（Algebra）** | MIT 18.701/702, Princeton MAT345/346, Harvard Math 122/123 | 表示论 + 张量（深度学习几何） |
| **几何与拓扑** | MIT 18.901, Princeton MAT419, Harvard Math 131/132, Cambridge Differential Geometry | 流形学习、信息几何 |
| **概率与随机过程** | MIT 18.175, Berkeley Math 218, Stanford Math 230, Cambridge Probability & Measure | **ML 理论核心** |
| **数值分析与优化** | MIT 18.085/086, UT Austin M 383E/2043, ETH 401-3651, Stanford Math 171/176 | **工程落地核心** |

## 目录结构

```
top-math-courses/
├── README.md                          ← 本文件
├── SCHOOL_SELECTION.md                ← 9 校选校理由 + 数学排名分析
├── UNIFIED_ROADMAP.md                 ← 30 课最优路径（融合 9 校）
├── FAST_TRACK.md                      ← 应用数学工程师 2-3 年快速通道
├── CROSS_SCHOOL_INSIGHTS.md           ← 9 校教学风格对比
├── AUDIT_PLAN.md                      ← 质量审计方法论
├── CROSS_INDEX_WITH_WORK4AI.md        ← 与讲透X系列的交叉索引
│
├── mit-math-courses/                  ← MIT Math 18.x
│   ├── SCHOOL.md                      ← 学校强项 + 课程目录
│   ├── 18_06_linear_algebra/          ← 单门课目录
│   │   ├── README.md                  ← 课程信息
│   │   ├── notes/                     ← 讲透宪法三层
│   │   └── exercises/
│   ├── 18_100_real_analysis/
│   ├── 18_175_probability/
│   └── ...
│
├── princeton-math-courses/            ← Princeton MAT xxx
├── harvard-math-courses/              ← Harvard Math xxx
├── stanford-math-courses/             ← Stanford MATH xxx
├── berkeley-math-courses/             ← Berkeley Math xxx
├── cambridge-math-courses/            ← Cambridge Mathematical Tripos
├── oxford-math-courses/               ← Oxford Math
├── eth-math-courses/                  ← ETH Zurich 401-xxx
└── ut-austin-math-courses/              ← UT Austin M XXX/XXXC
```

## 三层讲透宪法（与 work4ai 一致）

每门课的笔记按三层：

1. **直觉层**——一句话比喻 + 为什么需要它
2. **数学层**——关键定义、定理、证明思路
3. **代码层**——可运行的最小 Python/NumPy 实验（数值验证、可视化）

附加：
- **不足层**——方法的局限、与其他方法关系
- **应用层**——与 ML/工程的具体关联

## 与 top-cs-projects 的差异

| 维度 | top-cs-projects | top-math-courses |
|---|---|---|
| 核心产物 | **可运行 Python 项目** | **可读证明 + 可跑数值实验** |
| 评估方式 | 代码 pass 测试 | 习题证明 + 数值验证 |
| 工程量 | 每主题 200-500 行 Python | 每主题 5-15 页笔记 + 100 行 numpy |
| 学习节奏 | 主题制（按应用） | 序列制（按依赖） |
| 跨校对比 | 同主题不同实现 | 同概念不同讲法 |

## 实施路线图

### 阶段 1：课程清单（**本阶段**）
- 9 校 × SCHOOL.md（每校 15-25 门核心课的目录）
- 一手核实课程编号、教材、教学大纲链接
- 输出：`{school}-math-courses/SCHOOL.md` × 9

### 阶段 2：融合（顶层文档）
- UNIFIED_ROADMAP：从 0 基础到研究入门的 30 课最优路径
- FAST_TRACK：针对应用数学工程师的 2-3 年快速通道
- CROSS_SCHOOL_INSIGHTS：同概念不同讲法对比
- CROSS_INDEX_WITH_WORK4AI：与讲透X系列的映射

### 阶段 3：样板课讲透
- 选 3-5 门最核心课（如 MIT 18.06/18.100/18.175、Cambridge Part IB Linear Algebra）做完整讲透
- 每门课产出 notes/ + exercises/ + experiments/

### 阶段 4：质量审计
- 仿 top-cs-projects v1.3 流程：3 轮深审
- 一手核实所有课程链接、教材 ISBN、arXiv 引用

## 铁律（沿用 work4ai + top-cs-projects）

1. **课程编号一手核实**（学校官网/academic guide，不凭记忆）
2. **教材信息精确**（作者、版次、ISBN）
3. **arXiv 论文 ID 必核实**（与 work4ai 一致）
4. **跨校对比要客观**（不偏向任一校）
5. **与 ML 实战紧密关联**（不要纯抽象数学）
6. **代码可跑通**（bash 验证，与 work4ai 铁律一致）
7. **不写空壳**（要么不写，要么写扎实）

## 立即开始

按用户要求"先遍历所有顶尖学校的课程，最后再融合"：

1. 先逐校调研（一手 webfetch 学校官网）→ 写 `SCHOOL.md` × 9
2. 全部 9 校完成后，写顶层 `UNIFIED_ROADMAP.md` / `FAST_TRACK.md` / `CROSS_SCHOOL_INSIGHTS.md`
3. 选样板课做完整讲透

---

📌 **当前进度**：
- ✅ 顶层架构设计（本文件）
- 🚧 9 校 SCHOOL.md 调研中（已完成 MIT、Princeton、Cambridge、Harvard、Stanford、Berkeley；已完成全部 9 校（含 UT Austin））
- ⏳ 阶段 2 融合（待 9 校完成后启动）

详见各校目录下的 `SCHOOL.md`。
