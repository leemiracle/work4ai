# CSdiy 核心 CS 课程完全解析（电子基础 + 数据结构与算法 + 软件工程）

> 本文档覆盖 csdiy 课程地图中 CS 专业核心的三大类，共 11 门课程。
> 数据来源：csdiy.wiki 课程详情 + 课程官网 + 学科知识。

---

# 第一大类 · 电子基础（3 门）

> **csdiy 观点**：了解电路基础，感受"从传感器收集数据 → 分析 → 算法预测"整条流水线，对计算思维培养有帮助。信号与系统则提供傅里叶变换这个"看世界的新视角"。

---

## 课程 #1 · UCB EE16A&B：Designing Information Devices and Systems I&II

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley（电子系大一入门）|
| 先修 | 无 |
| 语言 | Python |
| 难度 | 🌟🌟🌟 |
| 学时 | **150 小时**（重型）|
| EE16A 网站 | https://inst.eecs.berkeley.edu/~ee16a/su20/ |
| EE16B 网站 | https://eecs16b.org/ |
| 资源汇总 | https://github.com/PKUFlyingPig/EE16A |

**定位**：UCB EE 学生大一入门课。
- **EE16A**：通过电路从环境**收集和分析数据**
- **EE16B**：从收集到的数据**分析并做出预测行为**

所有 lab 有远程在线版，适合在家自学。

### 📑 核心教学主题
- **电路基础**：电阻/电容/电感；基尔霍夫定律；节点分析
- **线性电路**：运算放大器；滤波器
- **信号处理入门**：频域分析
- **系统建模**：微分方程描述电路
- **Python 数据分析**：用 Python 处理电路采集的数据

---

## 课程 #2 · UCB EE120：Signal and Systems ⭐ 实战最强

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61A, CS70, 微积分, 线性代数 |
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://inst.eecs.berkeley.edu/~ee120/fa19/ |
| 资源汇总 | https://github.com/PKUFlyingPig/UCB-EE120 |

**csdiy 评价**：傅里叶变换给人**全新的看世界的视角**，如同微分方程一样优雅。**6 个超有趣的编程作业**是本课精华。

### 📑 核心教学主题 + 6 大 Python Lab

| 主题/Lab | 核心内容 |
|---------|---------|
| **连续/离散信号** | 信号分类；线性时不变（LTI）系统 |
| **卷积** ⭐ | 卷积运算；卷积定理 |
| **傅里叶级数与变换** ⭐⭐ | 频域分析；频谱；**看世界的新视角** |
| **拉普拉斯变换** | 系统稳定性分析；传递函数 |
| **采样定理** ⭐ | 奈奎斯特采样；混叠；ADC/DAC |
| **Lab 3：FFT 实现** ⭐ | 用 Python 实现 FFT，与 NumPy 性能对比 |
| **Lab 4：心率推断** ⭐ | 分析手指影像数据推断心率 |
| **Lab 5：哈勃降噪** ⭐⭐ | 给哈勃望远镜照片降噪，恢复星空 |
| **Lab 6：倒立摆** ⭐ | 构造反馈系统，平衡小车上的细杆 |

---

## 课程 #3 · MIT 6.007：Signals and Systems（Oppenheim 经典版）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 主讲 | **Prof. Alan V. Oppenheim**（信号处理界泰斗）|
| 先修 | Calculus, Linear Algebra |
| 语言 | Matlab Preferred |
| 难度 | 🌟🌟 |
| 学时 | 50-70 小时 |
| OCW 网站 | https://ocw.mit.edu/resources/res-6-007-signals-and-systems-spring-2011/index.htm |
| B站视频 | https://www.bilibili.com/video/BV1CZ4y1j7hs |
| 教材 | *Signals and Systems*, 2nd Edition（Oppenheim 经典）|

**csdiy 评价**：*"看到老师名字：Alan V. Oppenheim。好的，上这门课的理由已经足够了。"*——泰斗级人物，理论经典的代名词。

### 📑 核心教学主题
- 信号与系统基础（连续/离散）
- LTI 系统与卷积
- 傅里叶级数与连续/离散傅里叶变换
- 拉普拉斯变换与 z 变换
- 采样与滤波

---

# 第二大类 · 数据结构与算法（5 门）⭐ CS 核心

> **csdiy 观点**：算法是 CS 的核心，几乎一切专业课的基础。如何将实际问题抽象为算法问题，并选用合适的数据结构在时间/内存限制下解决，是算法课的永恒主题。

---

## 课程 #4 · UCB CS61B：Data Structures and Algorithms ⭐ 强推

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61A |
| 语言 | **Java** |
| 难度 | 🌟🌟🌟 |
| 学时 | 60 小时 |
| 主讲 | **Josh Hug 教授**（autograder 开源）|
| 课程网站(sp24) | https://sp24.datastructur.es/ |
| Gradescope 代码 | **MB7ZPY**（免费加入测评）|
| 资源汇总 | https://github.com/PKUFlyingPig/CS61B |

**定位**：CS61 系列第二门。注重数据结构与算法设计，接触**上千行工程代码**，初步领会软件工程思想。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **Java 基础** | 保姆级教程；IDEA 配置；核心语法（无 Java 基础也可上）|
| **核心数据结构** ⭐ | 链表、栈、队列、二叉树、BST、哈希表、堆、图、并查集 |
| **算法** ⭐ | 排序（快排/归并）、搜索、BFS/DFS、最短路简介 |
| **复杂度分析** | Big-O / Big-Θ / Big-Ω；均摊分析 |
| **软件工程思想** | 抽象、接口、设计模式入门 |

### 作业体系（高质量，2018 春季版）
- **14 个 Lab**：自己实现绝大部分数据结构
- **10 个 Homework**：运用数据结构与算法解决实际问题
- **3 个 Project** ⭐：接触**上千行工程代码**（如实现简易 Google Maps、2D Minecraft）

---

## 课程 #5 · Coursera: Algorithms I & II（Princeton）⭐ Sedgewick 经典

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Princeton |
| 主讲 | **Robert Sedgewick 教授**（算法大师）|
| 先修 | CS61A |
| 语言 | **Java** |
| 难度 | 🌟🌟🌟 |
| 学时 | 60 小时 |
| Algo I | https://www.coursera.org/learn/algorithms-part1 |
| Algo II | https://www.coursera.org/learn/algorithms-part2 |
| 开源教材 | https://algs4.cs.princeton.edu/home/ |
| 工业级代码实现 | https://algs4.cs.princeton.edu/code/ |
| 资源汇总 | https://github.com/PKUFlyingPig/Princeton-Algorithm |

**csdiy 评价**：Coursera 上**评分最高的算法课**。Sedgewick 有魔力把复杂算法讲得生动浅显。*"困扰我多年的 KMP 和网络流算法都是在这门课上茅塞顿开的。"*——时隔两年还能写出推导与证明。

### 三步掌握法（csdiy 强调）
1. **为什么这么做？**（正确性推导/本质）→ 视频 + 开源教材
2. **如何实现？** → 工业级代码实现（从注释到命名极严谨）
3. **解决实际问题** → 10 个高质量 Project

### 📑 核心教学主题
- **Algo I**：并查集；排序（快排/归并/堆排序）；查找（BST/红黑树/哈希表）
- **Algo II**：图算法（无向图/有向图/最小生成树/最短路）；字符串（KMP ⭐/正则/数据压缩）

### 10 个 Project（全有实际问题背景 + 测试 + 自动评分，**代码风格也评分**）

---

## 课程 #6 · MIT 6.006：Introduction to Algorithms ⭐ Erik Demaine

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 主讲 | **Erik Demaine**（算法界奇才）|
| 先修 | 计算机导论（CS50/CS61A）|
| 语言 | Python |
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 100h+ |
| OCW(Fall 2011) | https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/ |
| B站视频 | https://www.bilibili.com/video/BV1b7411e7ZP |
| 教材 | *Introduction to Algorithms*（CLRS，算法圣经）|

**定位**：MIT-EECS 的瑰宝。比 CS106B 更侧重算法详解。**出名地难**。

### 📑 核心教学主题
- 数据结构：AVL 树、跳表、哈希表、B 树
- 图算法：BFS/DFS、最短路（Dijkstra/Bellman-Ford）、最小生成树、拓扑排序
- 动态规划 ⭐
- 贪心算法
- 高级排序（线性时间）
- 字符串匹配

---

## 课程 #7 · MIT 6.046：Design and Analysis of Algorithms

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 主讲 | Erik Demaine + Srini Devadas + **Nancy Lynch**（分布式算法大师）|
| 先修 | 6.006/CS61B/CS106B |
| 语言 | Python（但基本无编程作业）|
| 难度 | 🌟🌟🌟🌟🌟 |
| 学时 | 100h+ |
| OCW(Spring 2015) | https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/ |
| B站视频 | https://www.bilibili.com/video/BV1A7411E737 |
| 教材 | CLRS |

**定位**：6.006 后续。不同于"现学现用"的 6.006，6.046 侧重**举一反三设计算法 + 正确性证明**。绝大部分作业是**算法设计 + 证明**（不是编程）。学完覆盖 99% 考试/面试题。

### 📑 核心教学主题
- 分治算法深入 + 主定理
- 动态规划深入 + 证明
- 贪心算法 + 交换论证
- 网络流与匹配 ⭐
- 线性规划
- NP 完全性 + 近似算法 ⭐
- 随机算法

---

## 课程 #8 · UCB CS170：Efficient Algorithms and Intractable Problems

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | CS61B, CS70 |
| 语言 | **LaTeX**（纯书面作业）|
| 难度 | 🌟🌟🌟 |
| 学时 | 60 小时 |
| 课程网站 | https://cs170.org/ |
| B站视频 | https://www.bilibili.com/video/BV1AU4y1b7RK |
| 资源汇总 | https://github.com/PKUFlyingPig/UCB-CS170 |

**定位**：UCB 算法设计课，注重**理论基础与复杂度分析**。教材写得极好，证明浅显，适合做工具书。

### 📑 核心教学主题（13 次书面作业）
- 分治、图算法、最短路、生成树
- 贪心、动规、并查集
- 线性规划、网络流 ⭐
- **NP 问题** ⭐
- 随机算法、哈希算法

**学习建议**：只有书面作业（用 LaTeX），借此锻炼 LaTeX 技巧。

---

## 📊 数据结构与算法 · 选课指南

| 方向 | 推荐路径 |
|------|---------|
| **入门（Java）** | CS61B(#4) → Coursera Algo(#5) |
| **入门（Python）** | MIT 6.006(#6) |
| **进阶理论** | 6.006(#6) → 6.046(#7) 或 CS170(#8) |
| **面试/竞赛** | CS61B(#4) + Coursera Algo(#5) + 6.046(#7) |

**⚠️ CS61B vs 6.006 vs Coursera Algo 三选一/二**：
- CS61B：**最适合自学**（autograder 开源，Java，工程实践强）
- Coursera Algo：**讲解最生动**（Sedgewick，工业级代码）
- 6.006：**最硬核**（Erik Demaine，但难）

---

# 第三大类 · 软件工程（3 门）

> **csdiy 观点**：一份"能跑"的代码和一份**工业级高质量代码**有本质区别。

---

## 课程 #9 · MIT 6.031：Software Construction ⭐ 强推

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | 掌握至少一门编程语言 |
| 语言 | **Java** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://web.mit.edu/6.031/ |
| 资源汇总 | https://github.com/PKUFlyingPig/MIT6.031-software-construction |

**课程目标**（官方原话）——写出满足三个特性的高质量代码：

| 特性 | 含义 |
|------|------|
| **Safe from bugs** ⭐ | 正确性（当下行为对）+ 防御性（未来行为对）|
| **Easy to understand** ⭐ | 代码要能与人沟通（包括未来的自己）|
| **Ready for change** ⭐ | 软件总在变，好设计让变更容易 |

### 📑 核心教学主题（精细到如何写注释）

| 主题 | 核心内容 |
|------|---------|
| **代码规范** ⭐ | 如何写注释；**函数 Specification**；命名 |
| **抽象数据类型** | ADT 设计；表示不变量（RI）；抽象函数（AF）|
| **面向对象设计** | 继承、多态、Liskov 替换原则 |
| **设计模式** | 策略、观察者、工厂等 |
| **测试** ⭐ | 单元测试；等价类划分；测试覆盖 |
| **并行编程** ⭐ | 线程安全；锁；死锁 |
| **可变 vs 不可变** | 不可变设计的优势 |

### 4 个编程作业 + 1 个 Project（Java，精心设计）

---

## 课程 #10 · UCB CS169：software engineering

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | 无 |
| 语言 | **Ruby / JavaScript** |
| 难度 | 🌟🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | http://www.saasbook.info/courses |
| 教材 | *Software as a Service*（https://github.com/PKUFlyingPig/CS169-Software-Engineering/blob/master/saasbook.pdf）|
| Edx 课程 | 搜 *Agile SaaS Development* |
| 资源汇总 | https://github.com/PKUFlyingPig/CS169-Software-Engineering |

**定位**：不同于传统软工课的"plan and document"模式，本课专注**敏捷开发（Agile）+ 云平台 SaaS**。用 Ruby/Rails 框架阐释 SaaS，并在云平台免费部署。

### 📑 核心教学主题
- **敏捷开发（Agile）** ⭐：Scrum；用户故事；迭代开发
- **SaaS 架构**：MVC 模式；RESTful API
- **Ruby on Rails** ⭐：全栈 Web 框架
- **BDD/TDD**：行为驱动/测试驱动开发；Cucumber；RSpec
- **云部署**：Heroku/AWS 部署
- **版本协作**：Git 工作流

---

## 课程 #11 · CMU 17-803：Empirical Methods（研究型）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | CMU |
| 主讲 | **Bogdan Vasilescu**（实证研究 + 开源软件研究）|
| 先修 | 博士级课程（最好有 CS 基础）|
| 语言 | 不限 |
| 难度 | 🌟🌟🌟 |
| 学时 | 100 小时 |
| 课程网站 | https://bvasiles.github.io/empirical-methods/ |

**定位**：**软件工程实证研究**——博士生方向。csdiy 评价：传统 CS 重工程技术，但工具/技术的**设计、评估、社会价值**需要实证研究。

### 📑 核心教学主题
- 定性研究：访谈、定性编码
- 定量研究：调查设计、统计分析
- **数据挖掘**：GitHub / Stack Overflow 数据
- **统计建模**：回归、社交网络分析
- 研究方法论：实验设计、效度、伦理

---

# 📊 本文档三大类总结（11 门）

| 大类 | 课程数 | 核心课 |
|------|--------|--------|
| 电子基础 | 3 | EE120（信号系统，6 个精彩 Lab）|
| 数据结构与算法 | 5 | CS61B + Coursera Algo（自学最佳组合）|
| 软件工程 | 3 | MIT 6.031（代码质量圣经）|

## 选课套餐

### 算法方向（必修）
```
CS61B(#4) → Coursera Algo(#5) → 6.046(#7) 或 CS170(#8)
```

### 软件工程方向
```
MIT 6.031(#9) → CS169(#10)
```

### 硬件/信号方向
```
EE16(#1) → EE120(#2) 或 MIT 6.007(#3)
```

---

**文档版本**：v1.0
**最后更新**：2026-07-07
