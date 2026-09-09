# 数据结构与算法 深度展开（5 门）

> **来源**：csdiy.wiki 数据结构与算法分类
> **判定基准**：飞腾 D3000 NEON 算子优化项目（DS&A 是 CS 基础，与项目间接相关）

---

## 1. UCB CS61B: Data Structures and Algorithms ｜ 中等
- **讲师**：Josh Hug
- **难度**：🌟🌟🌟 ｜ **学时**：60h
- **官网**：[sp24](https://sp24.datastructur.es/) / [fa23](https://fa23.datastructur.es/) / Gradescope **MB7ZPY**
- **GitHub**：[PKUFlyingPig/CS61B](https://github.com/PKUFlyingPig/CS61B)
- **作业**：14 Lab + 10 HW + 3 Project（上千行 Java）
- **价值**：数据结构中的**内存布局（数组 vs 链表的缓存友好性）**直接影响 NEON 向量化的数据加载效率

## 2. Coursera: Algorithms I & II（Sedgewick） ｜ 中等
- **讲师**：**Robert Sedgewick**（Princeton）
- **难度**：🌟🌟🌟 ｜ **学时**：60h
- **官网**：[Algo I](https://www.coursera.org/learn/algorithms-part1) / [Algo II](https://www.coursera.org/learn/algorithms-part2)
- **教材**：[algs4.cs.princeton.edu](https://algs4.cs.princeton.edu/home/)（开源 + [工业级代码](https://algs4.cs.princeton.edu/code/)）
- **GitHub**：[PKUFlyingPig/Princeton-Algorithm](https://github.com/PKUFlyingPig/Princeton-Algorithm)
- **作业**：10 个工业级 Project 带自动评分
- **价值**：算法效率分析有助于评估算子优化的理论上限；教材工业级代码风格对 NEON kernel 有参考

## 3. MIT 6.006: Introduction to Algorithms ｜ 中等
- **讲师**：**Erik Demaine**（算法奇才）+ Srini Devadas
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h+
- **官网**：[Fall 2011](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/)
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1b7411e7ZP)
- **教材**：*Introduction to Algorithms* (CLRS)
- **价值**：**分治思想（divide-and-conquer）是 GEMM tiling/递归矩阵乘的理论基础**；缓存 oblivious 算法设计原则对 NEON 数据搬运策略有指导

## 4. MIT 6.046: Design and Analysis of Algorithms ｜ 弱
- **讲师**：Erik Demaine + Srini Devadas + Nancy Lynch
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h+
- **官网**：[Spring 2015](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/)
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1A7411E737)
- 高级算法设计（NP/近似），与 NEON 底层优化关系不大

## 5. UCB CS170: Efficient Algorithms and Intractable Problems ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://cs170.org/
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1BU4y1b7RK)
- **GitHub**：[PKUFlyingPig/UCB-CS170](https://github.com/PKUFlyingPig/UCB-CS170)
- 覆盖分治/图论/动规/线性规划/网络流/NP/随机算法

---

## 项目相关性总览

| 课程 | 项目相关度 | 具体价值 |
|---|---|---|
| **MIT 6.006** | 中等 ⭐⭐ | 分治思想 = GEMM tiling 理论基础；cache-oblivious 算法 |
| **CS61B** | 中等 ⭐⭐ | 内存布局（数组 vs 链表）的 cache 友好性 |
| **Coursera Algo** | 中等 ⭐⭐ | 算法效率分析 + 工业级代码风格 |
| MIT 6.046 | 弱 ⭐ | 高级算法设计（NP/近似）|
| UCB CS170 | 弱 ⭐ | 理论复杂度分析 |

**建议优先级**：若聚焦 NEON 算子优化，**MIT 6.006（分治/cache-oblivious）+ CS61B（内存布局）** 是 DS&A 里唯二相关的。
