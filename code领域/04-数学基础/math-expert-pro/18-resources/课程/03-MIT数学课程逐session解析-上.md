# CSdiy 数学篇 · 课程完全解析

> 本文档对 csdiy.wiki「CS 学习规划-课程地图-数学」部分的每门课程做**逐单元、逐 session** 的完全解析。
> 内容来源：MIT OCW / 课程官网真实抓取 + 学科知识。
> 颗粒度标准：每门课 → Unit → Part → **Session/Lecture（最细）**，每个 session 标注核心内容、关键概念、与 CS 的联系。

---

# 第一部分 · 数学基础

---

## 课程 #4 · 3Blue1Brown：Essence 系列（几何直觉催化剂）⭐ 模板样例

### 课程元数据

| 字段 | 内容 |
|------|------|
| 创作者 | **Grant Sanderson** |
| 频道主页 | https://www.youtube.com/c/3blue1brown |
| 动画引擎 | **manim**（Grant 自研，开源：https://www.manim.community ）|
| 定位 | 不是替代正课，而是**在形式化训练前建立几何直觉**，让后续 MIT 正课的符号推导"刻骨铭心" |
| csdiy 评价 | "用生动形象的动画阐释数学本质内核，兼具深度和广度，质量非常高" |
| 配套用法 | 3B1B 看一遍建立直觉 → MIT 正课过一遍形式化 → Mathlets 交互验证 |

3B1B 有两个直接对应 csdiy 数学基础的播放列表：**Essence of Linear Algebra**（配 18.06）和 **Essence of Calculus**（配 18.01）。

---

### 📘 播放列表 A：《Essence of Linear Algebra》（线性代数的本质）

🔗 https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab

**总览**：16 集，把 18.06 整门课的**几何直觉**浓缩呈现。Grant 的核心主张——"理解线性代数，不要从数字和矩阵运算开始，而要从**空间变换**开始"。

#### Chapter 1: Vectors, what even are they?（向量究竟是什么？）
- **核心问题**：打破"向量 = 一列数"的单一视角
- **三视角统一**：
  1. 物理视角：有方向有大小的箭头
  2. 计算机视角：有序的数字列表
  3. 数学家视角：任何满足加法与数乘的东西
- **关键动画**：二维平面上的箭头如何对应 `[x, y]` 数对
- **配 18.06**：对应 Unit I 的 "The Geometry of Linear Equations"

#### Chapter 2: Linear combinations, span, and basis vectors（线性组合、生成空间、基）
- **核心概念**：
  - **线性组合** = 向量加法 + 标量数乘
  - **Span（生成空间）** = 给定向量所有线性组合所能"到达"的点的集合
  - **基向量** = 张成空间所需的最少向量（如二维的 î, ĵ）
- **关键直觉**：二维平面上两个向量，如果共线，span 就塌缩为一条线（降维）
- **配 18.06**：对应 "Independence, Basis and Dimension"

#### Chapter 3: Matrices as linear transformations（矩阵 = 线性变换）⭐ 灵魂
- **核心主张**：**理解矩阵的唯一正确方式，是把它看作空间的变换**
- **线性变换的两条铁律**（必须同时满足）：
  1. 原点不动
  2. 网格线保持平行且等距
- **关键直觉**：矩阵的每一列 = 变换后基向量的落点；`[a c; b d]` 表示 î 落到 (a,b)，ĵ 落到 (c,d)
- **配 18.06**：对应 "Linear Transformations and their Matrices"

#### Chapter 4: Matrix multiplication as composition（矩阵乘法 = 变换复合）
- **核心直觉**：`M2 · M1` = 先做 M1 变换，再做 M2 变换
- **为什么矩阵乘法不满足交换律**：变换顺序不同，结果不同（旋转 + 剪切的顺序）
- **配 18.06**：对应 "Multiplication and Inverse Matrices"

#### Chapter 5: Three-dimensional linear transformations（三维线性变换）
- **延伸**：把第 3 集的直觉推广到三维，3×3 矩阵的每一列 = 变换后 î, ĵ, k̂ 的落点
- **配 18.06**：3D 几何基础

#### Chapter 6: The determinant（行列式的几何意义）⭐
- **核心直觉**：行列式 = 变换对空间的**缩放因子**
  - det > 0：保持定向（不翻转）
  - det < 0：翻转了空间
  - **det = 0：空间被压扁了**（降维，不可逆！）
- **关键洞见**：为什么 `det(AB) = det(A)·det(B)`——缩放因子相乘
- **配 18.06**：对应 "Properties of Determinants"

#### Chapter 7: Inverse matrices, column space, rank and null space（逆矩阵、列空间、秩、零空间）⭐⭐
- **逆矩阵直觉**：`A⁻¹` 是把 A 的变换"撤销"的变换
- **为什么 det=0 时没有逆**：你不能把被压扁的空间"还原"成高维
- **Rank（秩）**：变换后**实际留下的维数**（输出空间的维数）
- **Column space（列空间）**：所有可能输出的集合（变换能"到达"的地方）
- **Null space（零空间）**：被压扁到原点的输入集合
- **配 18.06**：对应 "Column Space and Nullspace" + "The Four Fundamental Subspaces"

#### Chapter 8: Nonsquare matrices as transformations between dimensions（非方阵 = 跨维度变换）
- **核心**：2×3 矩阵 = 把三维压扁到二维；3×2 = 把二维嵌入三维
- **配 18.06**：对应 "Left and Right Inverses; Pseudoinverse"

#### Chapter 9: Dot products and duality（点积与对偶性）⭐ 高阶直觉
- **核心直觉**：点积 = 把高维向量**投影**到一维数轴上
- **Duality（对偶性）**：每个多维到一维的线性变换，都对应一个向量（这就是行向量的本质）
- **配 18.06**：对应 "Orthogonal Vectors and Subspaces" + "Projections onto Subspaces"

#### Chapter 10: Cross products（叉积的几何）
- **核心直觉**：`v × w` 的向量 = 垂直于 v、w 所在平面，长度 = v,w 张成的平行四边形面积
- **方向由右手定则决定**
- **配 18.06**：行列式公式的几何来源

#### Chapter 11: Cross products in the light of linear transformations（从线性变换视角看叉积）
- **高阶视角**：叉积本质是一个"对偶性"——`(x,y,z) × (v,w)` 等价于一个以 (x,y,z) 为行的 3×3 行列式
- **配 18.06**：行列式的深层理解

#### Chapter 12: Cramer's rule, explained geometrically（克莱默法则的几何解释）
- **核心**：用行列式/体积比来求解线性方程组
- **配 18.06**：对应 "Cramer's Rule, Inverse Matrix and Volume"

#### Chapter 13: Change of basis（基变换）⭐
- **核心问题**：不同坐标系下同一个向量如何表示？
- **关键直觉**：基变换矩阵 = 把"我的语言"翻译成"你的语言"
- **配 18.06**：对应 "Change of Basis; Image Compression"

#### Chapter 14: Eigenvectors and eigenvalues（特征向量与特征值）⭐⭐
- **核心直觉**：**特征向量 = 变换中只被拉伸、方向不变的那些向量**；特征值 = 拉伸倍数
- **为什么特征向量重要**：在变换的混乱中，它们是"不动点"，给出最简洁的描述
- **配 18.06**：对应 "Eigenvalues and Eigenvectors" + "Diagonalization and Powers of A"

#### Chapter 15: Abstract vector spaces（抽象向量空间）
- **核心飞跃**：函数也构成向量空间！求导是一种线性变换！
- **配 18.06**：对应 "Matrix Spaces; Rank 1; Small World Graphs"——通向泛函分析

#### 补充: A quicker intuition for eigenvectors（特征向量快速直觉）
- 用更简短的方式重述 Ch14 的核心

---

### 📗 播放列表 B：《Essence of Calculus》（微积分的本质）

🔗 https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr

**总览**：约 17 集。Grant 的核心主张——"不要死记求导公式，每一个公式都可以从几何直觉推导出来"。

#### Chapter 1: The essence of calculus（微积分的本质）⭐
- **核心主张**：导数 = 求"瞬时变化率"，但"瞬时"在数学上有矛盾，需要用**极限**化解
- **关键动画**：用车位移-时间曲线，求某时刻速度 = 取 Δt→0 的平均速度
- **推导**：从几何定义推出 $f'(x) = \lim_{\Delta x \to 0} \frac{f(x+\Delta x) - f(x)}{\Delta x}$
- **配 18.01**：Session 1-3

#### Chapter 2: The paradox of the derivative（导数的悖论）
- **哲学层面**：0 时刻没有变化，但导数却是个确定的数。这个"悖论"的化解 = 极限思想
- **配 18.01**：Session 4-5

#### Chapter 3: Derivative formula geometrically（导数公式的几何推导）
- **用面积思想推导** $x^2$ 的导数 = $2x$，$x^3$ 的导数 = $3x^2$
- **通用规律**：$(x^n)' = n \cdot x^{n-1}$ 的几何来源
- **配 18.01**：Session 6

#### Chapter 4: Visualizing the chain rule and product rule（链式法则与乘积法则可视化）
- **链式法则**：复合变换的导数 = 各层导数相乘
- **乘积法则**：$(fg)' = f'g + fg'$ 的几何来源（面积变化）
- **配 18.01**：Session 9-11

#### Chapter 5: What's so special about Euler's number e?（欧拉数 e 为什么特别？）
- **核心**：在所有指数函数 $a^x$ 中，只有 $e^x$ 的导数等于自身
- **配 18.01**：Session 16-19

#### Chapter 6: Implicit differentiation, what's going on here?（隐式求导）
- **核心**：不必解出 y=f(x)，直接对等式两边求导
- **配 18.01**：Session 13-14

#### Chapter 7: Limits, L'Hôpital's rule, and epsilon-delta definitions（极限、洛必达法则、ε-δ 定义）
- **ε-δ 定义**：为什么数学家要这么"绕"地定义极限——为了严谨
- **洛必达法则**：0/0 型极限的求解工具
- **配 18.01**：Session 4-5 + Unit 5 Part A

#### Chapter 8: Integration and the fundamental theorem of calculus（积分与微积分基本定理）⭐⭐
- **核心**：积分 = 把无穷多个无穷小量加起来（求面积）
- **第一基本定理**：积分与求导互为逆运算（这是微积分的"奇迹"）
- **配 18.01**：Unit 3 Part A-B（核心！）

#### Chapter 9: What does area have to do with slope?（面积和斜率有什么关系？）
- **第二基本定理**的直觉：积分函数的导数 = 原函数
- **配 18.01**：Unit 3 Part B

#### Chapter 10: Higher order derivatives（高阶导数）
- 二阶导 = 导数的导数 = 加速度 vs 速度的关系
- **配 18.01**：Session 12

#### Chapter 11: Taylor series（泰勒级数）⭐⭐
- **核心直觉**：用某点的"值 + 各阶导数"信息，**逼近**该点附近的函数
- $f(x) \approx f(a) + f'(a)(x-a) + \frac{f''(a)}{2!}(x-a)^2 + ...$
- **为什么 CS 学生必学**：数值优化（梯度下降）、数值分析（18.330）、ML（损失函数局部近似）的全部根基
- **配 18.01**：Unit 5 Part B（重中之重！）

#### 后续章节：Taylor series 续、几何意义、related rates、integration by parts 等
- 进一步深化泰勒级数的收敛性、几何含义，以及积分技巧的直觉

---

### 3B1B 在 CS 学习中的应用映射

| 3B1B 章节 | CS/AI 中的直接应用 |
|-----------|------------------|
| Ch3-4 矩阵 = 变换 | 神经网络全连接层的本质 |
| Ch6 行列式 | 判断变换是否可逆（雅可比行列式） |
| Ch7 秩/列空间 | 理解线性方程组解的存在性、唯一性 |
| Ch9 点积/对偶 | 注意力机制 Attention 的本质 = 向量点积 |
| Ch14 特征值/特征向量 | PCA、谱聚类、PageRank |
| Ch15 抽象向量空间 | 函数空间 → 核方法、RKHS |
| Calculus Ch11 泰勒级数 | 牛顿法、二阶优化（牛顿法/BFGS） |

---

### 学习节奏建议（2 周通览）

| 周 | 内容 | 时长 |
|----|------|------|
| Week 1 周末 | 线性代数 Ch1-7（建空间直觉） | 3 小时 |
| Week 2 工作日 | 每天看 18.06 对应 lecture（形式化） | 每讲 1 小时 |
| Week 2 周末 | 线性代数 Ch8-15 + Calculus Ch1-8 | 5 小时 |
| Week 3 | Calculus Ch9-17 + 18.01 形式化 | 穿插 |

---

## 课程 #1 · MIT 18.01：Single Variable Calculus（单变量微积分）⭐ 模板样例

### 课程元数据

| 字段 | 内容 |
|------|------|
| 课程编号 | **18.01SC**（SC = Scholar 版，专为自学者设计，比一般 OCW 完整得多）|
| 主讲教授 | **Prof. David Jerison** |
| 开课学期 | Fall 2010 |
| 级别 | Undergraduate 本科入门 |
| 先修 | 高中数学（无大学先修） |
| 课程总规模 | **5 大 Unit + Final Exam，约 80+ 个 Session，8 个 Problem Set，4+1 次考试** |
| 资源类型 | 🎬 Lecture Videos / 🎬 Problem-solving Videos / 📝 Lecture Notes / ✏️ Problem Sets + Solutions / 📝 Exams + Solutions / 🧮 Interactive Java Mathlets |
| 课程主页 | https://ocw.mit.edu/courses/mathematics/18-01sc-single-variable-calculus-fall-2010/ |

**课程宣言**（官方）：覆盖一元函数的微分与积分，以无穷级数简论收尾。微积分是物理、工程、经济等众多学科的基石。本课为**独立自学**而设计，包含理解所有概念所需的全部材料。

---

### 📑 完整教学大纲（逐 Session 解析）

---

#### 🔵 Unit 1: Differentiation（微分）

> **本单元目标**：从"变化率"的直觉出发，建立导数的严格定义，掌握所有基本初等函数的求导规则。

##### Part A: Definition and Basic Rules（定义与基本规则）

> **官方简介**："This section explains what differentiation is and gives rules for differentiating familiar functions."（阐释微分是什么，并给出常见函数的求导规则）

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S1** | Introduction to Derivatives | 导数的物理动机——用车位移-时间曲线求瞬时速度；导数 = 切线斜率 = 瞬时变化率 |
| **S2** | Examples of Derivatives | 用定义 $f'(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}$ 计算 $x^2$、常数等基本函数的导数 |
| **S3** | Derivative as Rate of Change | 导数作为"变化率"的物理诠释：速度 = 位移导数，加速度 = 速度导数 |
| **S4** | Limits and Continuity | 极限的严格概念；连续性的定义；为什么导数要求函数连续 |
| **S5** | Discontinuity | 间断点类型：跳跃间断、可去间断、无穷间断；可微必连续但连续未必可微（如 \|x\|） |
| **S6** | Calculating Derivatives | 系统化求导：幂法则 $(x^n)'=nx^{n-1}$、常数法则、和法则 |
| **S7** | Derivatives of Sine and Cosine | $(\sin x)'=\cos x$，$(\cos x)'=-\sin x$ 的几何与极限推导 |
| **S8** | Limits of Sine and Cosine | $\lim_{x\to 0}\frac{\sin x}{x}=1$、$\lim_{x\to 0}\frac{1-\cos x}{x}=0$ 的夹逼证明 |
| **S9** | **Product Rule** | $(fg)'=f'g+fg'$——两函数乘积的导数（几何：面积变化）|
| **S10** | **Quotient Rule** | $(f/g)'=\frac{f'g-fg'}{g^2}$——商的求导法则 |
| **S11** | **Chain Rule** ⭐ | $(f(g(x)))'=f'(g(x))\cdot g'(x)$——复合函数求导，**最重要的求导法则** |
| **S12** | Higher Derivatives | 二阶导 $f''$、$n$ 阶导 $f^{(n)}$；物理意义（加速度 = 二阶导） |
| **PS1** | Problem Set 1 | 综合练习上述所有内容 |

##### Part B: Implicit Differentiation and Inverse Functions（隐式求导与反函数）

> **官方简介**："extends the methods of Part A to exponential and implicitly defined functions. By the end of Part B, we are able to differentiate most elementary functions."（扩展到指数函数与隐式定义函数，学完可对几乎所有初等函数求导）

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S13** | **Implicit Differentiation** ⭐ | 不必解出 y=f(x)，对等式两边直接对 x 求导（如圆 $x^2+y^2=1$）|
| **S14** | Examples of Implicit Differentiation | 隐式求导实例：求曲线切线、法线 |
| **S15** | Implicit Differentiation and Inverse Functions | 用隐式求导求反函数导数：$(f^{-1})'(y)=1/f'(x)$ |
| **S16** | The Derivative of $a^x$ | 指数函数求导：$(a^x)'=a^x \ln a$，引出自然底数 $e$ 的特殊地位 |
| **S17** | **The Exponential Function** | $(e^x)'=e^x$（唯一导数等于自身的函数！）；$\ln x$ 的导数 $=1/x$ |
| **S18** | Derivatives of other Exponential Functions | $a^x = e^{x\ln a}$ 的技巧，把任意底数化为 $e$ 底 |
| **S19** | An Interesting Limit Involving $e$ | $\lim_{n\to\infty}(1+1/n)^n=e$ 的推导与意义 |
| **S20** | Hyperbolic Trig Functions | $\sinh x=(e^x-e^{-x})/2$、$\cosh x=(e^x+e^{-x})/2$ 及其导数 |
| **PS2** | Problem Set 2 | 综合练习 |

📝 **Exam 1**（覆盖 Unit 1 全部内容）

---

#### 🟢 Unit 2: Applications of Differentiation（微分的应用）

> **本单元目标**：把求导能力转化为解决实际问题的工具——近似、优化、找零点、联系变化率。

##### Part A: Approximation and Curve Sketching（近似与曲线绘制）

> **官方简介**："describes how differentiation can be used to simplify complex calculations and graph functions."（如何用微分简化复杂计算并绘制函数图像）

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S23** | **Linear Approximation** ⭐ | $f(x)\approx f(a)+f'(a)(x-a)$——用切线近似函数（一阶泰勒），**ML 梯度下降的数学根基** |
| **S24** | Examples of Linear Approximation | 近似 $\sqrt{4.1}$、$\sin(0.1)$ 等实例 |
| **S25** | Introduction to Quadratic Approximation | $f(x)\approx f(a)+f'(a)(x-a)+\frac{f''(a)}{2}(x-a)^2$——二阶近似更精确 |
| **S26** | Using Quadratic Approximations | 二阶近似的应用；与牛顿法的联系 |
| **S27** | Sketching Graphs I | 多项式与有理函数画图：利用一阶导（增减）、二阶导（凹凸） |
| **S28** | Sketching Graphs II | 通用画图策略：找临界点、拐点、渐近线、端点行为 |
| **PS3** | Problem Set 3 | 综合练习 |

##### Part B: Optimization, Related Rates and Newton's Method（优化、相关变化率、牛顿法）

> **官方简介**：optimization = 研究函数的最大/最小输出（最高利润、最少材料、最近距离）。还涵盖用导数关联两个变化率，以及估计函数零点。

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S29** | **Optimization Problems** ⭐ | 求函数极值：$f'(x)=0$ 找临界点，二阶导判别极大/极小；**凸优化 EE364A 的雏形** |
| **S30** | Optimization Problems II | 约束优化实例：固定材料求最大体积等 |
| **S31** | **Related Rates** | 两个变量都随时间变化，用链式法则关联它们的导数（如气球充气时半径与体积的变化率）|
| **S32** | Ring on a String | 经典物理实例：环在绳上滑动，用相关变化率求解 |
| **S33** | **Newton's Method** ⭐ | $x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}$——迭代求方程零点，**数值分析 18.330 与优化 EE364A 的核心算法** |
| **PS4** | Problem Set 4 | 综合练习 |

##### Part C: Mean Value Theorem, Antiderivatives and Differential Equations（中值定理、反导数、微分方程）

> **官方简介**：MVT 是证明"导数忠实描述变化率"的关键；后半部分讨论求导的逆过程。

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S34** | **Introduction to MVT** ⭐ | 中值定理：连续可微函数在 [a,b] 上必存在 c 使 $f'(c)=\frac{f(b)-f(a)}{b-a}$ |
| **S35** | Using the Mean Value Theorem | MVT 的推论：$f'\equiv 0 \Rightarrow f$ 为常数；用于证明不等式 |
| **S36** | Differentials | 微分 $dy=f'(x)dx$ 的概念；线性近似的微分语言 |
| **S37** | **Antiderivatives** | 求导的逆运算：$\int x^n dx = \frac{x^{n+1}}{n+1}+C$；**积分概念的前奏** |
| **S38** | Integration by Substitution | 换元积分法：$\int f(g(x))g'(x)dx = \int f(u)du$，链式法则的逆 |
| **S39** | Introduction to Differential Equations | 什么是微分方程；$y'=ky$ 的解是指数函数 |
| **S40** | Separation of Variables | 可分离变量的一阶 ODE：$\frac{dy}{dx}=g(x)h(y) \Rightarrow \int\frac{dy}{h(y)}=\int g(x)dx$ |
| **PS5** | Problem Set 5 | 综合练习 |

📝 **Exam 2**（覆盖 Unit 2 全部内容）

---

#### 🟡 Unit 3: The Definite Integral and its Applications（定积分及其应用）

> **本单元目标**：建立积分的严格定义，证明微积分基本定理（积分与求导互逆），并应用于面积、体积、概率、数值计算。

##### Part A: Definition of the Definite Integral and First Fundamental Theorem（定积分定义 + 第一基本定理）

> **官方简介**：定积分描述函数图像与 x 轴之间的面积。第一基本定理确认可用导数知识快速计算该面积。

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S43** | Definite Integrals | 定积分 $\int_a^b f(x)dx$ 的概念：曲线下面积 |
| **S44** | Adding Areas of Rectangles | 用矩形近似面积：$\sum f(x_i)\Delta x$ |
| **S45** | Some Easy Integrals | 简单积分的几何计算（常数、线性函数）|
| **S46** | **Riemann Sums** ⭐ | 黎曼和：$\lim_{n\to\infty}\sum_{i=1}^n f(x_i^*)\Delta x_i$——积分的严格定义 |
| **S47** | Introduction of the FTC | 第一微积分基本定理的引入：积分与求导的奇迹联系 |
| **S48** | **The FTC (Fundamental Theorem)** ⭐⭐ | $\int_a^b f(x)dx = F(b)-F(a)$，其中 $F'=f$——**微积分的灵魂**，把面积问题化为反导数 |
| **S49** | Applications of FTC | 用 FTC 快速计算定积分 |
| **S50** | Combining FTC and MVT | FTC + MVT 的综合应用：积分中值定理 |
| **PS6** | Problem Set 6 | 综合练习 |

##### Part B: Second Fundamental Theorem, Areas, Volumes（第二基本定理、面积、体积）

> **官方简介**：第二基本定理描述积分是微分的反面；可以理解用定积分定义的函数；还涵盖用积分计算体积。

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S51** | **The Second FTC** ⭐⭐ | $\frac{d}{dx}\int_a^x f(t)dt = f(x)$——变上限积分的导数 = 被积函数；**定义新函数的有力工具** |
| **S52** | Proving the FTC | FTC1 与 FTC2 的严格证明 |
| **S53** | New Functions From Old | 用积分定义"新"函数：误差函数 erf、正弦积分 Si 等 |
| **S54** | The Second FTC and $\ln(x)$ | $\ln x = \int_1^x \frac{1}{t}dt$——自然对数定义为积分，导数为 $1/x$ |
| **S55** | Creating New Functions Using FTC2 | 用变上限积分构造解 |
| **S56** | Geometric Interpretation of Definite Integrals | $\int_a^b f(x)dx$ = 净有向面积（f 为负时面积取负）|
| **S57** | **How to Calculate Volumes** ⭐ | 旋转体体积：圆盘法 $V=\int \pi f(x)^2 dx$ |
| **S58** | Volume of a Sphere | 用圆盘法推导球体积 $V=\frac{4}{3}\pi r^3$ |
| **S59** | Volume of a Paraboloid | 绕 y 轴旋转抛物线求体积 |
| **PS7** | Problem Set 7 | 综合练习 |

##### Part C: Average Value, Probability and Numerical Integration（平均值、概率、数值积分）

> **官方简介**：计算平均值和概率是积分的重要应用。虽然几乎所有函数都可微，但很多函数无法直接积分——本部分介绍数值方法。

| Session | 标题 | 核心内容 |
|---------|------|---------|
| **S60** | Integrals and Averages | 连续函数平均值：$\bar{f}=\frac{1}{b-a}\int_a^b f(x)dx$ |
| **S61** | Integrals and Weighted Averages | 加权平均：$\int f(x)w(x)dx / \int w(x)dx$ |
| **S62** | **Integrals and Probability** ⭐ | 连续型概率：$P(a\le X\le b)=\int_a^b p(x)dx$，期望 $E[X]=\int x\cdot p(x)dx$——**CS70/CS126 概率论的前奏** |
| **S63** | **Numerical Integration** ⭐ | 梯形法则、辛普森法则——无法解析积分时的数值方法；**18.330 数值分析的前奏** |
| **S64** | Numerical Integration, Continued | 数值积分的误差分析 |
| **S65** | **Bell Curve, Conclusion** | 正态分布（钟形曲线）$\frac{1}{\sqrt{2\pi}}e^{-x^2/2}$ 与积分的联系 |
| **PS8** | Problem Set 8 | 综合练习 |

📝 **Exam 3**（覆盖 Unit 3 全部内容）

---

#### 🟣 Unit 4: Techniques of Integration（积分技巧）

> **本单元目标**：掌握系统化的积分技巧，能处理更复杂的被积函数。

##### Part A: Trigonometric Powers, Trigonometric Substitution and Completing the Square（三角幂、三角换元、配方）

| 核心内容 | 说明 |
|---------|------|
| **三角函数幂的积分** | $\int \sin^n x \cos^m x\,dx$ 的系统化处理（奇偶幂分类策略）|
| **三角换元** ⭐ | $\sqrt{a^2-x^2}\Rightarrow x=a\sin\theta$；$\sqrt{a^2+x^2}\Rightarrow x=a\tan\theta$；$\sqrt{x^2-a^2}\Rightarrow x=a\sec\theta$ |
| **配方** | 把 $\sqrt{ax^2+bx+c}$ 配方化为标准型再三角换元 |

📝 含 Problem Set + 部分练习

##### Part B: Partial Fractions, Integration by Parts, Arc Length, and Surface Area（部分分式、分部积分、弧长、表面积）

| 核心内容 | 说明 |
|---------|------|
| **分部积分** ⭐ | $\int u\,dv = uv - \int v\,du$——乘积求导法则的逆；LIATE 口诀选 $u$ |
| **部分分式分解** | 把 $\frac{P(x)}{Q(x)}$ 拆为简单分式再积分；处理有理函数的标准武器 |
| **弧长** | $L=\int_a^b \sqrt{1+(f'(x))^2}\,dx$——曲线长度的积分定义 |
| **旋转曲面面积** | $S=\int 2\pi f(x)\sqrt{1+(f'(x))^2}\,dx$ |

📝 含 Problem Set

##### Part C: Parametric Equations and Polar Coordinates（参数方程与极坐标）

| 核心内容 | 说明 |
|---------|------|
| **参数方程** | 曲线用 $(x(t),y(t))$ 表示；参数方程下的导数 $\frac{dy}{dx}=\frac{y'(t)}{x'(t)}$ |
| **极坐标** | $r,\theta$ 表示点；极坐标与直角坐标转换 $x=r\cos\theta, y=r\sin\theta$ |
| **极坐标下的面积** | $A=\int\frac{1}{2}r^2\,d\theta$——玫瑰线、心形线等区域的面积 |
| **极坐标曲线的弧长** | $L=\int\sqrt{r^2+(r')^2}\,d\theta$ |

📝 **Exam 4**（覆盖 Unit 4 全部内容）

---

#### 🔴 Unit 5: Exploring the Infinite（探索无穷）

> **本单元目标**：处理"无穷"相关的极限与级数，最终建立泰勒级数——用多项式逼近任意光滑函数。

##### Part A: L'Hôpital's Rule and Improper Integrals（洛必达法则与反常积分）

| 核心内容 | 说明 |
|---------|------|
| **L'Hôpital 法则** ⭐ | $\lim\frac{f(x)}{g(x)}$ 为 $0/0$ 或 $\infty/\infty$ 时 $=\lim\frac{f'(x)}{g'(x)}$——不定式极限的利器 |
| **反常积分** | $\int_a^\infty f(x)dx=\lim_{b\to\infty}\int_a^b f$；无界函数的积分 $\int_a^b$ 在瑕点取极限 |
| **收敛性判别** | 比较判别法：与已知收敛/发散的积分比较 |

##### Part B: Taylor Series（泰勒级数）⭐⭐ 重中之重

| 核心内容 | 说明 |
|---------|------|
| **泰勒多项式** | $f(x)\approx f(a)+f'(a)(x-a)+\frac{f''(a)}{2!}(x-a)^2+\cdots+\frac{f^{(n)}(a)}{n!}(x-a)^n$ |
| **泰勒级数** ⭐⭐ | 无穷展开 $f(x)=\sum_{n=0}^\infty \frac{f^{(n)}(a)}{n!}(x-a)^n$——**数值分析、ML 优化、物理建模的全部根基** |
| **收敛性与收敛半径** | 比值判别法确定级数在什么范围收敛 |
| **常见泰勒级数** ⭐ | $e^x=\sum\frac{x^n}{n!}$；$\sin x=\sum\frac{(-1)^n x^{2n+1}}{(2n+1)!}$；$\cos x$；$\ln(1+x)$；$\frac{1}{1-x}$ |
| **泰勒级数的应用** | 用泰勒级数求极限、近似、解微分方程、定义函数 |

📝 含 Problem Set

**🎯 Final Exam**（覆盖全部 5 个 Unit）

---

### 🎯 18.01 在 CS/AI 学习中的关键映射

| Session | 在 CS/AI 中的直接应用 |
|---------|---------------------|
| **S11 Chain Rule** | 反向传播 backpropagation 的数学本质 = 链式法则 |
| **S23 Linear Approx** | 梯度下降、一阶优化方法的根基 |
| **S25-26 Quadratic Approx** | 二阶优化（牛顿法）的前置 |
| **S29 Optimization** | 凸优化 EE364A 的雏形 |
| **S33 Newton's Method** | 18.330 数值分析 + EE364A 的核心算法 |
| **S48 FTC** | 概率论中用积分算概率的根基 |
| **S51 Second FTC** | 定义连续分布函数的工具 |
| **S62 Probability** | CS70/CS126 概率论的直接前奏 |
| **S63 Numerical Integration** | 18.330 数值分析的前奏 |
| **Unit 5 Taylor Series** | 数值优化、损失函数局部近似的全部根基 |

---

### 📅 学习节奏建议（一学期 13 周或精学 6 周）

**精学版（6 周，针对有基础者）**：
| 周 | 内容 | 重点 |
|----|------|------|
| W1 | Unit 1（S1-S20）+ 3B1B Calculus Ch1-6 | 建立导数 = 变化率的本质直觉 |
| W2 | Unit 2（S23-S40）| **重点：S23 线性近似、S29 优化、S33 牛顿法**（CS 核心） |
| W3 | Unit 3 Part A-B（S43-S59）+ 3B1B Ch8-9 | **重点：FTC 两大定理**（微积分灵魂） |
| W4 | Unit 3 Part C（S60-S65）| **重点：S62 概率、S63 数值积分**（通向后续课） |
| W5 | Unit 4（积分技巧）| 按需学，不死记所有技巧 |
| W6 | Unit 5（泰勒级数）⭐ | **CS 学生最重要的部分，务必吃透** |

---

## 课程 #3 · MIT 18.06：Linear Algebra（线性代数）⭐⭐ 核心中的核心

### 课程元数据

| 字段 | 内容 |
|------|------|
| 课程编号 | **18.06SC**（SC = Scholar 版） |
| 主讲教授 | **Prof. Gilbert Strang**（传奇——2023 年 88 岁上了最后一课，结束 MIT 61 年教学生涯） |
| 开课学期 | Fall 2011 |
| 级别 | Undergraduate |
| 教材 | *Introduction to Linear Algebra* — Gilbert Strang（https://math.mit.edu/~gs/linearalgebra/ ，清华采用） |
| 课程总规模 | **3 大 Unit，共 34 讲，3 次期中考试 + Final** |
| 资源类型 | 🎬 Strang 全套 Lecture Videos / 📝 Summary Notes / 🎬 每主题 Problem Solving Videos / ✏️ Problem Sets + Solutions / 🧮 Java Demonstrations / 📝 Exams + Solutions / 🎓 **Instructor Insights**（Strang 亲述教学法） |
| 特色页面 | **Meet the TAs** / **Final 18.06 Lecture 2023**（告别课录像）/ **Related Resources** |
| 课程主页 | https://ocw.mit.edu/courses/mathematics/18-06sc-linear-algebra-fall-2011/ |

**课程宣言**（官方）：覆盖矩阵理论与线性代数，强调对物理、经济、社科、自然科学、工程等其他学科有用的主题。与 Strang 教材 *Introduction to Linear Algebra* 配套。
