
---

### 📑 完整教学大纲（逐 Lecture 解析）

---

#### 🔵 Unit I: Ax = b and the Four Subspaces（线性方程组与四个基本子空间）

> **本单元灵魂**：从解线性方程组出发，建立矩阵的几何理解，最终达到线性代数最重要的概念——**四个基本子空间**（列空间、零空间、行空间、左零空间）。

| Lecture | 标题 | 核心内容 |
|---------|------|---------|
| **L1** | **The Geometry of Linear Equations** ⭐ | 线性方程组的**三种视角**：行图像（线交点）、列图像（列向量线性组合）、矩阵形式 $Ax=b$。开篇即建立"矩阵 = 列向量组合"的直觉 |
| **L2** | An Overview of **Key Ideas** | 全课总览：行独立、列独立、秩、基——提前鸟瞰整个 Unit I 的核心概念 |
| **L3** | **Elimination with Matrices** | 高斯消元法：初等行变换把矩阵化为上三角；行交换处理主元为 0 |
| **L4** | Multiplication and Inverse Matrices | 矩阵乘法的**四种方式**（行×列、列、行、块）；逆矩阵 $A^{-1}$ 的存在条件与求解（$[A\|I]\to[I\|A^{-1}]$） |
| **L5** | **Factorization into A = LU** ⭐ | 矩阵的 LU 分解：$A=LU$（下三角×上三角）；高斯消元的矩阵语言；为什么 LU 分解是数值线性代数的基石 |
| **L6** | Transposes, Permutations, **Vector Spaces** | 转置 $A^T$；置换矩阵 $P$（行交换）；**向量空间**概念：对加法和数乘封闭的集合；$\mathbb{R}^2, \mathbb{R}^3$ 与子空间 |
| **L7** | **Column Space and Nullspace** ⭐⭐ | **$C(A)$**（列空间）= A 的列的所有线性组合；**$N(A)$**（零空间）= 满足 $Ax=0$ 的所有 x；两个核心子空间的定义与几何 |
| **L8** | **Solving Ax = 0** ⭐ | 求零空间：行化简 $A\to R$（简化行阶梯形）；主元变量与自由变量；**特殊解**（每个自由变量对应一个） |
| **L9** | **Solving Ax = b** ⭐ | 求完整解 $x=x_p+x_n$（特解 + 零空间）；$Ax=b$ 解的存在性（$b\in C(A)$?）、唯一性（$N(A)=\{0\}$?）的判别 |
| **L10** | **Independence, Basis and Dimension** ⭐ | 线性无关；**基**（生成 + 无关）；**维数** = 基中向量个数；$rank(A)$ = 主元数 = 列空间维数 |
| **L11** | ⭐⭐⭐ **The Four Fundamental Subspaces** | **本课灵魂**：列空间 $C(A)$（$\mathbb{R}^m$ 中，维数 $r$）、零空间 $N(A)$（$\mathbb{R}^n$ 中，维数 $n-r$）、行空间 $C(A^T)$（$\mathbb{R}^n$ 中，维数 $r$）、左零空间 $N(A^T)$（$\mathbb{R}^m$ 中，维数 $m-r$）；四个子空间的正交关系（**大图 Big Picture**）|
| **L12** | Matrix Spaces; Rank 1; Small World Graphs | 推广：矩阵本身也构成向量空间；秩 1 矩阵的特殊性（所有矩阵 = 秩 1 矩阵之和）；小世界图与图论 |
| **L13** | **Graphs, Networks, Incidence Matrices** | 图的关联矩阵 $A$；$A x = b$ = 电路方程（基尔霍夫电流/电压定律）；应用：网络流、电路分析 |
| **L14** | Exam 1 Review | Unit I 复习 |

📝 **Exam 1**（覆盖 Unit I 全部 13 讲核心内容）

---

#### 🟢 Unit II: Least Squares, Determinants and Eigenvalues（最小二乘、行列式、特征值）

> **本单元灵魂**：引入正交性（投影 → 最小二乘）、行列式（体积与可逆性）、特征值（矩阵的"本征方向"）——这三者是数据分析与机器学习的数学根基。

| Lecture | 标题 | 核心内容 |
|---------|------|---------|
| **L15** | **Orthogonal Vectors and Subspaces** | 正交：$x^T y=0$；行空间 ⊥ 零空间（Unit I 大图的深化）；正交补 |
| **L16** | **Projections onto Subspaces** ⭐⭐ | 投影矩阵 $P=A(A^TA)^{-1}A^T$；把向量投影到列空间；**为什么 $A^TA$ 反复出现在数据科学中** |
| **L17** | **Projection Matrices and Least Squares** ⭐⭐ | **最小二乘法** $A^TA\hat{x}=A^Tb$——线性回归的数学解！当 $Ax=b$ 无解时，求最优近似 $\hat{x}$；**ML/AI 最核心公式之一** |
| **L18** | **Orthogonal Matrices and Gram-Schmidt** ⭐ | 正交矩阵 $Q$（$Q^TQ=I$）；**Gram-Schmidt 正交化**：把任意基化为正交基；$A=QR$ 分解（最小二乘的优雅形式） |
| **L19** | **Properties of Determinants** | 行列式三大性质：单位阵 det=1、行交换变号、线性性；由性质推导 det(AB)=det(A)det(B)、det(A⁻¹)=1/det(A) |
| **L20** | Determinant Formulas and Cofactors | 行列式的显式公式：按行/列展开，余子式与代数余子式 |
| **L21** | **Cramer's Rule, Inverse Matrix and Volume** | Cramer 法则解 $Ax=b$；$A^{-1}$ 用余子式表示；**行列式 = 体积**（线性变换对空间的缩放因子，呼应 3B1B Ch6） |
| **L22** | ⭐⭐⭐ **Eigenvalues and Eigenvectors** | $Ax=\lambda x$——特征向量（方向不变）与特征值（拉伸倍数）；特征方程 $\det(A-\lambda I)=0$；**PCA、谱聚类、PageRank 的根基** |
| **L23** | **Diagonalization and Powers of A** ⭐ | $A=S\Lambda S^{-1}$——对角化；$A^n=S\Lambda^n S^{-1}$——矩阵幂的快速计算；对角化条件（n 个无关特征向量） |
| **L24** | **Differential Equations and exp(At)** ⭐ | $\frac{du}{dt}=Au$ 的解 $u(t)=e^{At}u(0)$；矩阵指数；**把线代与微分方程联系**，为动力系统/控制论铺路 |
| **L25** | **Markov Matrices; Fourier Series** ⭐ | 马尔可夫矩阵（列和为 1，最大特征值 = 1）→ **马尔可夫链的稳态 = 特征向量**；傅里叶级数 = 无穷维的正交基展开（SVD/FFT 的前奏） |
| **L26** | Exam 2 Review | Unit II 复习 |

📝 **Exam 2**（覆盖 Unit II 全部 11 讲核心内容）

---

#### 🟡 Unit III: Positive Definite Matrices and Applications（正定矩阵与应用）

> **本单元灵魂**：对称矩阵的优美性质（特征值为实数、特征向量正交）、正定矩阵（通向优化的桥梁）、SVD（线性代数的巅峰成就）。

| Lecture | 标题 | 核心内容 |
|---------|------|---------|
| **L27** | **Symmetric Matrices and Positive Definiteness** ⭐ | 对称矩阵 $A=A^T$：特征值必为实数、特征向量必正交（$A=Q\Lambda Q^T$ 谱定理）；正定矩阵的定义（$x^TAx>0$）与判别（特征值全正）|
| **L28** | **Complex Matrices; Fast Fourier Transform (FFT)** ⭐ | 厄米矩阵（复数版对称）；酉矩阵（复数版正交）；**FFT**——把 DFT 从 $O(n^2)$ 降到 $O(n\log n)$，信号处理/卷积网络的数学根基 |
| **L29** | **Positive Definite Matrices and Minima** ⭐⭐ | 正定矩阵 = 判别函数极小值（Hessian 矩阵正定 → 局部最小值）；**凸优化 EE364A 的判别核心**；$A=LDL^T$ 分解 |
| **L30** | Similar Matrices and **Jordan Form** | 相似矩阵 $B=M^{-1}AM$；Jordan 标准形（不可对角化矩阵的最简形式） |
| **L31** | ⭐⭐⭐ **Singular Value Decomposition (SVD)** | $A=U\Sigma V^T$——**任何矩阵都能分解**；奇异值 = $A^TA$ 特征值的平方根；**推荐系统、图像压缩、PCA、低秩近似、LSA 的数学根基**；线性代数巅峰 |
| **L32** | **Linear Transformations and their Matrices** | 线性变换（保加法+保数乘）；每个线性变换对应一个矩阵（依赖基的选择）；呼应 3B1B Ch3 |
| **L33** | **Change of Basis; Image Compression** ⭐ | 基变换矩阵；JPEG 压缩的原理——换到 DCT 基后丢掉小系数；**变换 = 换基，压缩 = 截断** |
| **L34** | **Left and Right Inverses; Pseudoinverse** | $A^+$ 伪逆——对非方阵/不满秩矩阵也能定义"广义逆"；最小二乘解 $\hat{x}=A^+b$；**SVD 的优雅应用** |
| **L35** | Exam 3 Review | Unit III 复习 |

📝 **Exam 3**（覆盖 Unit III 全部 8 讲核心内容）

**🎯 Final Course Review + Final Exam**

🎓 **Final 18.06 Lecture 2023**（Strang 教授的告别课——88 岁最后一课，2023 年 5 月 15 日，具有纪念意义。链接：https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/final-1806-lecture-2023/ ）

---

### 🎓 Instructor Insights（Strang 教学法，稀有元资源）

OCW 特设页面，Strang 亲述他如何教这门课：
- **直觉优先**：先讲几何图像（如四个子空间的大图），再讲形式化推导
- **重复关键概念**：核心思想（如 $C(A), N(A)$）在多个 lecture 反复强化
- **联系应用**：每个抽象概念都配上应用（图论、电路、最小二乘）

---

### 🎯 18.06 在 CS/AI 学习中的关键映射（极高价值）

| Lecture | 在 CS/AI 中的直接应用 |
|---------|---------------------|
| **L7-11 四个子空间** | 理解数据矩阵 $X$ 的结构，PCA 的几何根基 |
| **L16-17 投影/最小二乘** ⭐⭐ | **线性回归 OLS 解 $w=(X^TX)^{-1}X^Ty$ = 最小二乘**；ML 最基础公式 |
| **L18 Gram-Schmidt / QR** | 数值稳定的回归求解；GPT 正交化 |
| **L22 特征值/特征向量** ⭐⭐ | **PCA 降维、谱聚类、PageRank、振动模态** |
| **L23 对角化** | 矩阵幂的快速计算；马尔可夫链稳态 |
| **L24 exp(At) 微分方程** | GNN 中的连续扩散、动力系统建模 |
| **L25 马尔可夫矩阵** ⭐ | **MDP/强化学习、PageRank、随机游走** |
| **L27 对称矩阵/谱定理** | 核方法、协方差矩阵的特征分解 |
| **L28 FFT** ⭐ | **信号处理、CNN 的频域分析、多项式乘法** |
| **L29 正定矩阵** ⭐⭐ | **凸优化的判别核心**；高斯过程的协方差矩阵；ML 损失函数的 Hessian |
| **L31 SVD** ⭐⭐⭐ | **推荐系统、图像压缩、PCA、LSA、低秩近似、数据压缩的巅峰工具** |
| **L33 基变换/图像压缩** | JPEG 原理、小波变换、特征脸 |
| **L34 伪逆** | 欠定/超定系统的最小范数解；ML 中的广义逆 |

---

### 📅 学习节奏建议（一学期 13 周或精学 6 周）

**精学版（6 周，配合 3B1B 直觉）**：
| 周 | 内容 | 重点 | 3B1B 配合 |
|----|------|------|----------|
| W1 | L1-L6（方程组、消元、LU、向量空间） | 建立矩阵 = 变换的直觉 | Ch1-4 |
| W2 | L7-L13（列空间、零空间、四个子空间）⭐⭐ | **本课灵魂，务必吃透** | Ch5-8 |
| W3 | L15-L18（正交、投影、最小二乘、QR）⭐⭐ | **ML 线性回归的根基** | Ch9 |
| W4 | L19-L25（行列式、特征值、对角化、马尔可夫） | **PCA/PageRank 的根基** | Ch12-14 |
| W5 | L27-L31（对称矩阵、FFT、正定、SVD）⭐⭐⭐ | **SVD 是巅峰，务必精读** | Ch14-15 |
| W6 | L32-L34（线性变换、基变换、伪逆）+ 复习 | 综合应用 | - |

**⚠️ 关键提醒**：
- **L11（四个子空间）、L17（最小二乘）、L22（特征值）、L31（SVD）** 是整门课的四大支柱，每一个都直接对应 AI/ML 的核心技术
- 看 lecture 前**先看对应 3B1B 章节**建立几何直觉，再听 Strang 形式化讲解，效果最佳

---

## 课程 #2 · MIT 18.02：Multivariable Calculus（多变量微积分）

### 课程元数据

| 字段 | 内容 |
|------|------|
| 课程编号 | **18.02SC**（SC = Scholar 版） |
| 主讲教授 | **Prof. Denis Auroux** |
| 开课学期 | Fall 2010 |
| 级别 | Undergraduate |
| 先修 | 18.01（单变量微积分） |
| 课程总规模 | **4 大 Unit + Final Exam** |
| 资源类型 | 🎬 Lecture Videos / 🎬 Recitation Videos / 📝 Worked Examples / ✏️ Problem Sets + Solutions / 📝 Exams + Solutions / 🧮 Interactive Java Mathlets |
| 应用领域（官方声明） | **物理科学、工程、经济学、计算机图形学** |
| 课程主页 | https://ocw.mit.edu/courses/mathematics/18-02sc-multivariable-calculus-fall-2010/ |

**课程宣言**（官方）。覆盖多元函数的微分、积分与向量微积分。这些工具广泛用于物理科学、工程、经济学和**计算机图形学**。专为独立自学而设计。

---

### 📑 完整教学大纲（逐 Part 解析）

---

#### 🔵 Unit 1: Vectors and Matrices（向量与矩阵）

> **本单元目标**：建立多维空间的几何工具——向量、点积、叉积、矩阵，为多变量函数奠基。

##### Part A: Vectors, Determinants and Planes（向量、行列式与平面）

| 核心主题 | 说明 |
|---------|------|
| **向量基础** | 三维向量 $(x,y,z)$；向量加法、数乘；模长 $\|\vec{v}\|$；单位向量 |
| **点积（Dot Product）** ⭐ | $\vec{a}\cdot\vec{b}=\|\vec{a}\|\|\vec{b}\|\cos\theta$；**投影**；正交性判别（点积=0）；功的计算 |
| **叉积（Cross Product）** | $\vec{a}\times\vec{b}$：垂直于两者所在平面，模长 = 平行四边形面积；右手定则；用于求法向量 |
| **行列式** | $3\times3$ 行列式 = 平行六面体的有向体积；行列式=0 → 三向量共面 |
| **平面方程** | 过点 $P_0$、法向量 $\vec{n}$ 的平面：$\vec{n}\cdot(\vec{r}-\vec{r_0})=0$；点到平面距离 |

📝 Problem Set + Exam 1 准备

##### Part B: Matrices and Systems of Equations（矩阵与方程组）

| 核心主题 | 说明 |
|---------|------|
| **线性方程组** | 用矩阵求解多维几何问题 |
| **矩阵与线性变换** | 矩阵作用于向量 = 旋转/缩放/剪切（呼应 18.06） |
| **逆矩阵求解** | $A\vec{x}=\vec{b}\Rightarrow\vec{x}=A^{-1}\vec{b}$ |

##### Part C: Parametric Equations for Curves（曲线的参数方程）

| 核心主题 | 说明 |
|---------|------|
| **参数曲线** | $\vec{r}(t)=(x(t),y(t),z(t))$ 描述运动轨迹 |
| **速度与加速度** | $\vec{v}=\vec{r}'(t)$（速度向量）；$\vec{a}=\vec{r}''(t)$（加速度） |
| **弧长** | $L=\int\|\vec{r}'(t)\|dt$ |
| **切线、法平面** | 曲线在某点的切向量与法平面 |

📝 **Exam 1**（覆盖 Unit 1 全部内容）

---

#### 🟢 Unit 2: Partial Derivatives（偏导数）

> **本单元目标**：把单变量微积分推广到多变量——偏导数、梯度、方向导数、约束优化。**这是 ML/AI 最相关的单元。**

##### Part A: Functions of Two Variables, Tangent Approximation and Optimization（二元函数、切线近似、优化）

| 核心主题 | 说明 |
|---------|------|
| **多元函数** | $z=f(x,y)$ 的图像是三维曲面；等高线（contour plot）|
| **偏导数** ⭐ | $f_x=\frac{\partial f}{\partial x}$（固定 y 对 x 求导）；几何意义：沿坐标轴方向的斜率 |
| **二阶偏导** | $f_{xx}, f_{xy}, f_{yy}$；Clairaut 定理（混合偏导与顺序无关）|
| **切平面近似** ⭐ | $f(x,y)\approx f(a,b)+f_x(a,b)(x-a)+f_y(a,b)(y-b)$——**18.01 线性近似的多元版** |
| **无约束极值** | 临界点 $\nabla f=0$；**二阶导判别** $D=f_{xx}f_{yy}-f_{xy}^2$（Hessian 行列式）；极大/极小/鞍点 |
| **鞍点** | $D<0$：一个方向上凸、另一方向下凹（ML 中优化器逃离的关键点）|

📝 Problem Set

##### Part B: Chain Rule, Gradient and Directional Derivatives（链式法则、梯度、方向导数）⭐⭐ ML 核心

| 核心主题 | 说明 |
|---------|------|
| **链式法则（多元）** ⭐ | $\frac{df}{dt}=\frac{\partial f}{\partial x}\frac{dx}{dt}+\frac{\partial f}{\partial y}\frac{dy}{dt}$；**反向传播的多元版** |
| **梯度 $\nabla f$** ⭐⭐⭐ | $\nabla f=(f_x,f_y)$——**ML 梯度下降的灵魂**；梯度 = 最速上升方向 |
| **方向导数** ⭐ | $D_{\vec{u}}f=\nabla f\cdot\vec{u}$——任意方向的变化率；最大方向导数 = 梯度方向 |
| **梯度几何** | 梯度 ⊥ 等高线；负梯度 = 最速下降方向（**梯度下降法的数学根基**）|
| **梯度应用** | 优化、图像分割、物理场（电场=电势梯度）|

📝 Problem Set

##### Part C: Lagrange Multipliers and Constrained Differentials（拉格朗日乘数法与约束微分）⭐

| 核心主题 | 说明 |
|---------|------|
| **拉格朗日乘数法** ⭐⭐ | 在约束 $g(x,y)=0$ 下求 $f$ 极值：$\nabla f=\lambda\nabla g$；**凸优化 EE364A 的雏形** |
| **几何直觉** | 极值点处 $f$ 与 $g$ 的等高线相切（梯度平行）|
| **多约束推广** | 多个约束 $g_1=0,g_2=0,...$ 的拉格朗日法 |
| **约束微分** | 约束下的微分关系（如沿曲线运动的变化率）|

📝 **Exam 2**（覆盖 Unit 2 全部内容——**AI/ML 学生最重要的考试**）

---

#### 🟡 Unit 3: Double Integrals and Line Integrals in the Plane（二重积分与平面线积分）

> **本单元目标**：把积分推广到二维区域和向量场——通向物理学的力、功、通量。

##### Part A: Double Integrals（二重积分）

| 核心主题 | 说明 |
|---------|------|
| **二重积分定义** | $\iint_R f(x,y)\,dA$——曲顶柱体体积；矩形→一般区域的推广 |
| **累次积分** | $\int\int f\,dy\,dx$——化为两次单变量积分；Fubini 定理（可交换顺序）|
| **极坐标下的二重积分** | $dA=r\,dr\,d\theta$；圆形区域用极坐标简化 |
| **变量替换** | 雅可比行列式 $J$：$dA=\|J\|\,du\,dv$；**18.06 行列式的几何应用** |

##### Part B: Vector Fields and Line Integrals（向量场与线积分）

| 核心主题 | 说明 |
|---------|------|
| **向量场** | $\vec{F}(x,y)=(P,Q)$——每点一个向量（如力场、流速场）|
| **线积分（功）** ⭐ | $\int_C \vec{F}\cdot d\vec{r}=\int_C P\,dx+Q\,dy$——力沿路径做的功 |
| **保守场与势函数** | 保守场 $\vec{F}=\nabla f$：线积分只依赖起点终点，与路径无关 |
| **判别保守场** | $\frac{\partial P}{\partial y}=\frac{\partial Q}{\partial x}$（旋度为零）|

##### Part C: Green's Theorem（格林定理）⭐

| 核心主题 | 说明 |
|---------|------|
| **格林定理** ⭐⭐ | $\oint_C P\,dx+Q\,dy=\iint_D\left(\frac{\partial Q}{\partial x}-\frac{\partial P}{\partial y}\right)dA$——**线积分 = 面积分**，斯托克斯定理的二维版 |
| **几何意义** | 沿边界的环量 = 区域内旋度的总和 |
| **面积公式** | $A=\frac{1}{2}\oint_C x\,dy-y\,dx$——用线积分求面积 |

📝 **Exam 3**（覆盖 Unit 3 全部内容）

---

#### 🟣 Unit 4: Triple Integrals and Surface Integrals in 3-Space（三重积分与三维曲面积分）

> **本单元目标**：推广到三维——三重积分、通量、三大定理（散度定理、斯托克斯定理）统一向量微积分。

##### Part A: Triple Integrals（三重积分）

| 核心主题 | 说明 |
|---------|------|
| **三重积分** | $\iiint_V f\,dV$——四维"超柱体"体积；质量、质心、转动惯量 |
| **柱坐标** | $(r,\theta,z)$：$dV=r\,dr\,d\theta\,dz$；柱对称区域简化 |
| **球坐标** ⭐ | $(\rho,\theta,\phi)$：$dV=\rho^2\sin\phi\,d\rho\,d\theta\,d\phi$；球对称区域简化（物理/图形学常用） |

##### Part B: Flux and the Divergence Theorem（通量与散度定理）⭐⭐

| 核心主题 | 说明 |
|---------|------|
| **通量（Flux）** ⭐ | $\iint_S \vec{F}\cdot\hat{n}\,dS$——向量场穿过曲面的"流量"；正/负通量 |
| **散度（Divergence）** | $\nabla\cdot\vec{F}=\frac{\partial P}{\partial x}+\frac{\partial Q}{\partial y}+\frac{\partial R}{\partial z}$——每点的"源/汇"强度 |
| **散度定理（高斯定理）** ⭐⭐ | $\iint_{\partial V}\vec{F}\cdot\hat{n}\,dS=\iiint_V\nabla\cdot\vec{F}\,dV$——**曲面积分 = 体积积分**；物理/电磁学/流体力学的核心 |
| **应用** | 电场高斯定律、流体不可压缩条件（散度=0）|

##### Part C: Line Integrals and Stokes' Theorem（线积分与斯托克斯定理）⭐⭐

| 核心主题 | 说明 |
|---------|------|
| **旋度（Curl）** ⭐ | $\nabla\times\vec{F}$——向量场的旋转程度；旋度=0 → 保守场 |
| **斯托克斯定理** ⭐⭐ | $\oint_{\partial S}\vec{F}\cdot d\vec{r}=\iint_S(\nabla\times\vec{F})\cdot\hat{n}\,dS$——**线积分 = 曲面积分**；格林定理的三维版 |
| **三大定理统一** ⭐⭐⭐ | FTC（一维）→ 格林定理（二维）→ 斯托克斯定理（三维）= **微积分最高成就**，统一了"边界积分 = 内部积分" |

🔧 **Physics Applications**（物理应用专题：电磁学、流体力学中的实际应用）

📝 **Exam 4**（覆盖 Unit 4 全部内容）

**🎯 Final Exam**（含 Practice Final + Review + Final）

---

### 🎯 18.02 在 CS/AI 学习中的关键映射

| Part | 在 CS/AI 中的直接应用 |
|------|---------------------|
| **Unit 1 向量/叉积** | 计算机图形学（法向量、碰撞检测）、3D 游戏开发 |
| **Unit 2 Part A 偏导** | 神经网络中损失函数对每个权重的偏导 |
| **Unit 2 Part B 梯度/方向导数** ⭐⭐⭐ | **梯度下降法的数学根基**——ML 优化的灵魂 |
| **Unit 2 Part B 链式法则** ⭐⭐⭐ | **反向传播 backprop = 多元链式法则** |
| **Unit 2 Part C 拉格朗日乘数法** ⭐⭐ | **约束优化**（SVM、正则化）的根基；EE364A 凸优化 |
| **Unit 2 Part C Hessian 判别** | 优化中判断驻点性质（鞍点逃离）|
| **Unit 3-4 雅可比行列式** | 生成模型中的变量替换（Normalizing Flow）|
| **Unit 4 Part B 散度** ⭐ | GAN、连续正则化（Wasserstein）、流模型 |
| **Unit 4 Part B/C 高斯/斯托克斯定理** | 计算机图形学、物理仿真、电磁学 |

---

### 📅 学习节奏建议（精学 4 周，聚焦 AI 相关）

| 周 | 内容 | 重点 |
|----|------|------|
| W1 | Unit 1（向量、点积、叉积、矩阵） | 建立多维几何直觉 |
| W2 | Unit 2 Part A-B（偏导、梯度、方向导数）⭐⭐⭐ | **AI/ML 最核心内容**——梯度下降的根基 |
| W3 | Unit 2 Part C（拉格朗日乘数法）+ Unit 3（二重积分） | 约束优化 + 积分基础 |
| W4 | Unit 4（三重积分、散度、斯托克斯） | 物理仿真/图形学方向重点 |

**⚠️ 关键提醒**：
- **Unit 2 是 AI/ML 学生的核心**——梯度、链式法则、约束优化直接对应深度学习训练
- 走 AI 方向可略读 Unit 3-4（偏物理/图形学），但**雅可比行列式**（Unit 3 Part A）对生成模型很重要

---

## 课程 #5 · MIT 6.050J：Information and Entropy（信息与熵）⭐ CS 友好的零基础信息论

### 课程元数据

| 字段 | 内容 |
|------|------|
| 课程编号 | **6.050J**（联合开设：EECS + 机械工程）|
| 主讲教授 | **Prof. Paul Penfield** + **Prof. Seth Lloyd**（量子计算先驱）|
| 开课学期 | Spring 2008 |
| 级别 | Undergraduate（**专为大一新生定制，零先修**） |
| 教材 | *Information and Entropy*（Penfield 亲撰，[开源 PDF](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-050j-information-and-entropy-spring-2008/syllabus/MIT6_050JS08_textbook.pdf)）|
| 课程总规模 | **13 Unit + 开源教材 + 编程作业** |
| 资源类型 | 📖 Open Textbook（开源教材，OCW 罕见配套书）/ ✏️ Problem Sets + Solutions / 💻 Programming Assignments（Matlab）|
| 课程主页 | https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-050j-information-and-entropy-spring-2008/index.htm |

**课程宣言**（官方）。"探索**通信与计算的终极极限**，强调信息的**物理本质**。"熵的概念应用于**信道容量**与**热力学第二定律**——这种"信息论 = 物理学"的统一视角是本课最大特色。csdiy 评价：**全球极罕见的"大一零基础信息论"课**。

---

### 📑 完整教学大纲（13 Unit 逐个解析）

| Unit | 标题 | 核心内容 | 关键概念 |
|------|------|---------|---------|
| **1 & 2** | **Bits and Codes**（比特与编码） | 信息的基本单位；比特；二进制编码；ASCII；**生物信息表示**（DNA = 4 进制） | 比特、字节、信息量度量、编码效率 |
| **3** | **Compression**（压缩）⭐ | 无损压缩；**霍夫曼编码**；前缀码；信息熵 $H=-\sum p_i\log_2 p_i$ 作为压缩下限（香农信源编码定理） | 香农熵、最优编码、数据压缩 |
| **4** | **Noise and Errors**（噪声与错误） | 有噪信道；**纠错码**（奇偶校验、汉明码）；检错 vs 纠错 | 信道噪声、汉明距离、纠错能力 |
| **5** | **Probability**（概率） | 概率基础；贝叶斯定理；随机变量；期望与方差 | 概率分布、贝叶斯、独立性 |
| **6** | **Communications**（通信）⭐ | 香农信道编码定理；信道容量 $C=B\log_2(1+S/N)$；**带宽与信噪比的权衡** | 信道容量、香农极限、带宽 |
| **7** | Processes（过程） | 随机过程入门；马尔可夫过程；稳态分布 | 马尔可夫链、转移概率 |
| **8** | **Inference**（推断）⭐ | 统计推断；贝叶斯推断；最大似然估计；从数据中学习 | MLE、MAP、贝叶斯推断 |
| **9** | **Maximum Entropy**（最大熵）⭐ | **最大熵原理**；在约束下选熵最大的分布（最无偏的推断）；**Jaynes 原理** | 最大熵分布、无偏推断 |
| **10** | Physical Systems（物理系统） | 信息的物理观；麦克斯韦妖；兰道尔原理（擦除 1 比特耗散 $kT\ln2$ 能量） | 信息物理观、兰道尔极限 |
| **11** | **Energy**（能量） | 信息与能量的关系；可逆计算（不耗能）；不可逆计算的能量代价 | 可逆计算、能量-信息等价 |
| **12** | **Temperature**（温度） | 信息与热力学；熵的统计力学定义 $S=k\ln W$；温度的统计定义 | 统计力学熵、玻尔兹曼分布 |
| **13** | ⭐ **Quantum Information**（量子信息） | 量子比特（qubit）；量子叠加；量子纠缠；量子计算入门（Seth Lloyd 专长） | qubit、量子门、Shor 算法 |

### 📝 资源索引（Resource Index）

课程提供完整 Resource Index 页面，索引所有 readings/problems/assignments。

---

### 🎯 6.050J 在 CS/AI 学习中的关键映射

| Unit | 在 CS/AI 中的直接应用 |
|------|---------------------|
| **Unit 1-2 比特/编码** | 数据压缩、无损编码的根基 |
| **Unit 3 压缩/熵** ⭐⭐ | **交叉熵损失函数、KL 散度的数学根源**；深度学习分类的损失函数本质 |
| **Unit 4 纠错码** | 通信协议、存储系统的可靠性 |
| **Unit 5 概率** | 通向 CS70/CS126 概率论的桥梁 |
| **Unit 6 信道容量** ⭐ | 无线通信、5G/6G 的理论极限 |
| **Unit 8 推断** ⭐ | **贝叶斯网络、贝叶斯深度学习、不确定性估计** |
| **Unit 9 最大熵** ⭐ | **最大熵 RL（Soft Actor-Critic）、能量模型（EBM）** |
| **Unit 10-12 物理信息** | 物理信息神经网络（PINN）、可逆神经网络（Normalizing Flow）|
| **Unit 13 量子信息** | 量子机器学习（QML）的前沿 |

---

### 📅 学习节奏建议（100 小时，一学期 13 周）

| 周次 | Unit | 重点程度 |
|------|------|---------|
| W1-2 | Unit 1-3（比特、编码、压缩）⭐ | **CS 核心必学** |
| W3 | Unit 4（噪声与纠错） | 重要 |
| W4 | Unit 5（概率） | 通向 CS70 的桥梁 |
| W5-6 | Unit 6-7（通信、过程）⭐ | **CS 核心必学** |
| W7-8 | Unit 8-9（推断、最大熵）⭐⭐ | **AI/ML 核心** |
| W9-11 | Unit 10-12（物理系统） | CS 学生可略读 |
| W12-13 | Unit 13（量子信息） | 按兴趣选学 |

**⚠️ 关键提醒**：
- **Unit 3（熵）、Unit 8（推断）、Unit 9（最大熵）** 是 AI/ML 学生最重要的三个 Unit
- 熵的概念 $H=-\sum p\log p$ 在 ML 中无处不在（交叉熵损失、KL 散度、互信息、决策树信息增益）
- 本课是 6.441（高阶信息论）的零基础前奏

---

## 📊 数学基础部分（5 门）全部完成 ✅

| 课程 | 状态 | 颗粒度 |
|------|------|--------|
| #4 3Blue1Brown | ✅ | 33 集逐集 |
| #1 MIT 18.01 | ✅ | 80+ session 逐个 |
| #3 MIT 18.06 | ✅ | 34 讲逐讲 |
| #2 MIT 18.02 | ✅ | 4 Unit × 12 Part |
| #5 MIT 6.050J | ✅ | 13 Unit 逐个 |

---

# 第二部分 · 数学进阶

> **定位**：大二/大三课程，需先修数学基础。csdiy 评价：这类课容易"学了就背，考了就忘"，好课的标准是**理论 + 算法实战结合**。

---

## 课程 #6 · UCB CS70：Discrete Math and Probability Theory ⭐ CS 友好

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley |
| 先修 | **无**（最适合 CS 学生入门的离散数学课）|
| 语言 | 无（纯理论 + 证明）|
| 难度 | 🌟🌟🌟 |
| 学时 | 60 小时 |
| 课程网站 | http://www.eecs70.org/ |
| 资源汇总 | https://github.com/PKUFlyingPig/UCB-CS70 |

**csdiy 评价**：不是纯理论堆砌，而是**每个理论模块都配一个算法实战**——让 CS 学生在夯实理论的同时感受理论的实际力量。

### 📑 核心教学主题（理论 ↔ 算法映射表）⭐ 本课灵魂

| 理论模块 | 实际算法运用 | 核心概念 |
|---------|-------------|---------|
| **逻辑证明** | **稳定匹配算法**（Gale-Shapley）| 命题逻辑、量词、证明方法（归纳/反证/构造）|
| **图论** | 网络拓扑设计 | 图、树、连通性、欧拉/哈密顿路径、二分图 |
| **基础数论** | **RSA 算法** ⭐ | 模运算、欧拉定理、费马小定理、中国剩余定理 |
| **多项式环** | **纠错码设计**（Reed-Solomon/BCH）| 有限域、多项式运算、Berlekamp-Welch 译码 |
| **概率论** | **哈希表设计、负载均衡** | 组合计数、条件概率、贝叶斯、期望、方差、马尔可夫/切比雪夫不等式 |

### 🎯 在 CS/AI 中的应用
- **RSA** → 密码学基础（通向 CS255）
- **纠错码** → 通信/存储可靠性（通向 6.050J Unit 4）
- **概率论** → ML 理论基础（通向 CS126）
- **稳定匹配** → 算法设计（通向 CS170）

**学习建议**：CS 学生**最该优先学**的进阶数学课，直接喂给后续算法/密码学/网络课的养料。notes 写得深入浅出，公式推导与实例并重。

---

## 课程 #7 · UCB CS126：Probability Theory（概率论进阶）⭐⭐

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | UC Berkeley（EE126）|
| 先修 | **CS70 + 微积分 + 线性代数**（先修最严的之一）|
| 语言 | **Python** |
| 难度 | 🌟🌟🌟🌟🌟（满星）|
| 学时 | 100 小时 |
| 课程网站 | https://inst.eecs.berkeley.edu/~ee126/fa20/content.html |
| 教材（开源 PDF） | https://link.springer.com/content/pdf/10.1007%2F978-3-030-49995-2.pdf |
| 教材（Epub） | https://link.springer.com/download/epub/10.1007%2F978-3-030-49995-2.epub |
| Jupyter Notebook 实战 | https://jeanwalrand.github.io/PeecsJB/intro.html |
| 资源汇总 | https://github.com/PKUFlyingPig/EECS126 |

**csdiy 评价**：作者自述"上的时候很吃力，但坚持下来收获巨大"。涉及统计学、**随机过程**等深入内容。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **概率论复习与深化** | σ-代数、概率公理、条件概率、独立性、贝叶斯定理 |
| **随机变量** | 离散/连续型；PMF/PDF/CDF；重要分布（伯努利/二项/泊松/均匀/指数/正态）|
| **期望与方差** | 期望的线性性（**最重要的技巧**）；方差分解；矩生成函数 |
| **多维随机变量** | 联合分布；协方差矩阵；相关系数；条件分布 |
| **极限定理** ⭐ | 大数定律（LLN）；**中心极限定理（CLT）**——统计推断的根基 |
| **随机过程** ⭐⭐ | **马尔可夫链**（转移矩阵、稳态分布、首达时间）；泊松过程；**布朗运动** |
| **统计推断** | 最大似然估计（MLE）；置信区间；假设检验 |
| **贝叶斯推断** | 先验/后验；MAP 估计；贝叶斯滤波 |

### 三大特色
1. **教材全开源** *Probability in EE and CS*，每章以真实算法举例（**PageRank、路径规划、语音识别**）
2. **全书 Python Jupyter Notebook** 实现，可在线修改运行
3. **14 个书面作业 + 9 个编程作业**，理论实战双管齐下

### 🎯 在 CS/AI 中的应用
- **马尔可夫链** → **MDP/强化学习、PageRank、随机游走**
- **CLT** → 统计假设检验、A/B 测试
- **贝叶斯推断** → **贝叶斯深度学习、不确定性估计**
- **随机过程** → 排队论、网络分析

**⚠️ 学习建议**：难度满星，先修严格。建议 CS70 + 18.06 都学扎实后再上。

---

## 课程 #8 · MIT 6.042J：Mathematics for Computer Science（备选）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | Calculus, Linear Algebra |
| 语言 | Python preferred |
| 难度 | 🌟🌟🌟 |
| 学时 | 50-70 小时 |
| 主讲 | **Tom Leighton**（Akamai 联合创始人）|
| 课程网站 | https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/ |
| B站视频(spring2015) | https://www.bilibili.com/video/BV1n64y1i777/ |

**定位**：CS70 的 MIT 对应版本，**二选一即可**（内容重叠 80%+）。

### 📑 核心教学主题
- 数学推理与证明（归纳、不变量）
- 数论与密码学（RSA）
- 图论
- 可数性/不可数性（康托尔对角线）
- 概率论（离散）
- 自动机与图灵机简介

**选择建议**：偏好工程实践选 CS70，偏好理论深度选 6.042J。

---

## 课程 #9 · ComputationalThinking（MIT 计算思维入门 · Julia 体验课）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | 无 |
| 语言 | **Julia** |
| 课程网站（全开源） | https://computationalthinking.mit.edu/Spring21/ |

**定位**：18.330 之前的**轻量体验课**。csdiy 感悟：科学的魅力不是故弄玄虚，而是让每个普通人都能理解。

### 📑 三个 Topic

| Topic | 核心内容 |
|-------|---------|
| **图像处理** | 用 Julia 实现图像滤波、边缘检测、压缩；理解卷积、傅里叶变换 |
| **社会科学与数据科学** | 数据清洗、统计分析、可视化、回归；理解数据驱动决策 |
| **气候学建模** | 微分方程数值求解；全球气候模型的简化版；理解建模-模拟-验证流程 |

**学习建议**：难度不大，先过这门感受 Julia + 计算思维，再决定是否投入 18.330。

---

## 课程 #10 · MIT 18.330：Introduction to Numerical Analysis ⭐⭐

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | **微积分 + 线性代数 + 概率论** |
| 语言 | **Julia** |
| 难度 | 🌟🌟🌟🌟🌟（满星）|
| 学时 | **150 小时**（重型）|
| 课程网站 | https://github.com/mitmath/18330 |
| 开源教材 | https://fncbook.com （*Fundamentals of Numerical Computation*）|
| 资源汇总 | https://github.com/PKUFlyingPig/MIT18.330 |

**核心主题**：用**离散的计算机表示**估计和逼近数学上**连续的概念**。

### 📑 核心教学主题

| 主题 | 核心内容 | 关键概念 |
|------|---------|---------|
| **浮点表示** ⭐ | IEEE 754 标准；机器精度；**舍入误差** | 浮点数、相对/绝对误差 |
| **Root Finding** | 二分法、牛顿法、割线法；收敛阶 | 不动点迭代、收敛性分析 |
| **线性系统** | LU 分解；条件数；迭代法（Jacobi/Gauss-Seidel） | 条件数 κ(A)、数值稳定性 |
| **插值与拟合** | 多项式插值；样条；最小二乘拟合 | 龙格现象、切比雪夫节点 |
| **数值微分与积分** | 前向/中心差分；梯形/辛普森法则；高斯积分 | 误差阶 O(h^n) |
| **微分方程数值解** ⭐ | Euler 法；Runge-Kutta；稳定性区域 | 刚性问题、隐式方法 |

### 三步方法论（csdiy 强调）
① 如何建立估计 → ② 如何估计误差 → ③ 如何用算法实现估计

### 🎯 在 CS/AI 中的应用
- **浮点误差** → 深度学习中的数值稳定性（梯度爆炸/消失）
- **条件数** → 矩阵求逆的可靠性（ML 中的多重共线性）
- **优化算法** → 牛顿法/拟牛顿法（BFGS）的根基
- **ODE 数值解** → 神经 ODE（Neural ODE）、物理信息网络（PINN）

**学习建议**：难度满星 + 150 小时，**强烈建议先过 ComputationalThinking** 感受 Julia，再投入。

---

## 课程 #11 · MIT 18.335：Introduction to Numerical Methods（研究生数值分析）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT（研究生级）|
| 先修 | 18.330 或同等 |
| 课程网站 | https://ocw.mit.edu/courses/mathematics/18-335j-introduction-to-numerical-methods-spring-2019/index.htm |

**定位**：18.330 之后的研究生深造，**意犹未尽者参考**。方向：科学计算/HPC/数值优化才需要。

### 📑 核心主题（深化版）
- 矩阵计算的高级算法（QR、SVD 的数值实现）
- 稀疏矩阵与迭代法（Krylov 子空间、GMRES、CG）
- 特征值问题的数值方法（QR 算法、分治法）
- 快速算法（FFT、多极子、快速多重球）
- 并行数值计算

---

## 课程 #12 · MIT 18.04：Complex Variables with Applications（复变函数 · 先修补齐）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 主讲 | **Dr. Jeremy Orloff** |
| 开课学期 | Spring 2018 |
| 级别 | Undergraduate |
| 先修 | 18.01/18.02 |
| 课程网站 | https://ocw.mit.edu/courses/mathematics/18-04-complex-variables-with-applications-spring-2018/ |
| 资源 | Lecture Notes / Recitations / Problem Sets / Exams / MATLAB Tutorials |

**定位**：作为微分方程的**先修知识补齐**。课程宣言：复分析是解决物理问题的基本工具，围绕**解析函数**（有复导数的函数）——复导数的存在性本身就有极强的函数性质蕴含。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **复数与复平面** | 复数运算；欧拉公式 $e^{i\theta}=\cos\theta+i\sin\theta$；复几何 |
| **解析函数** ⭐ | 复导数；柯西-黎曼方程；**解析性 = 无穷可微**（复分析的奇迹）|
| **初等函数** | 复指数、复对数、复幂、复三角函数 |
| **复积分** ⭐⭐ | **柯西积分定理**（闭合路径积分为 0）；柯西积分公式 |
| **级数展开** ⭐ | **泰勒级数**与**洛朗级数**（Laurent）；收敛圆/环 |
| **留数定理** ⭐⭐ | 用留数计算**实积分**（看似难算的实积分变简单）|
| **应用** | 调和函数；二维流体；Laplace/Fourier 变换 |

### 🎯 在 CS/AI 中的应用
- **留数定理** → 信号处理中的逆变换
- **解析函数** → 复变神经网络、可控生成模型
- **调和函数** → 图论中的随机游走、电势理论

---

## 课程 #13 · MIT 18.03：Differential Equations（常微分方程）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 课程编号 | **18.03SC**（SC = Scholar 版）|
| 主讲 | **Prof. Arthur Mattuck** + **Prof. Haynes Miller** + Dr. Jeremy Orloff + Dr. John Lewis |
| 开课学期 | Fall 2011 |
| 级别 | Undergraduate |
| 先修 | 18.01/18.02（建议 18.06）|
| 课程主页 | https://ocw.mit.edu/courses/mathematics/18-03sc-differential-equations-fall-2011/ |
| 资源 | 🎬 Mattuck 全套讲座 / 📝 Course Notes / 🎬 Problem Solving Videos / ✏️ Problem Sets / 🧮 Mathlets / 📝 Exams |

**课程宣言**（官方）。**自然法则用微分方程表达**。科学家和工程师必须知道如何建模、求解、解释。聚焦科学工程中最有用的方程与技术。

### 📑 完整教学大纲（4 Unit，官网抓取）

#### 🔵 Unit I: First Order Differential Equations（一阶 ODE）- 12 主题
| 主题 | 核心内容 |
|------|---------|
| Basic DE's | 基本概念；可分离变量方程 |
| Geometric Methods | 方向场；积分曲线；定性分析 |
| Numerical Methods | 欧拉法；数值求解 |
| Linear ODE's | 一阶线性 ODE 标准形 |
| **Integrating Factors** ⭐ | 积分因子法求解线性 ODE |
| Complex Arithmetic | 复数运算（为振荡解准备）|
| Sinusoidal Functions | 正弦/余弦函数；相位 |
| Constant Coefficients | 常系数线性 ODE |
| Exponential Input | 指数输入；增益与相位滞后 |
| Autonomous Equations | 自治方程；平衡点；稳定性 |
| Linear vs Nonlinear | 线性（叠加原理）vs 非线性（无叠加）|

📝 Exam 1

#### 🟢 Unit II: Second Order Constant Coefficient Linear Equations（二阶常系数线性 ODE）- 9 主题
| 主题 | 核心内容 |
|------|---------|
| **Characteristic Equation** ⭐ | 特征方程 $ar^2+br+c=0$；通解 |
| **Damped Oscillators** ⭐ | 阻尼振荡器：欠阻尼/临界阻尼/过阻尼 |
| Exponential Response | 指数响应函数（ERF）|
| Gain and Phase Lag | 增益与相位滞后 |
| Undetermined Coefficients | 待定系数法求特解 |
| Linear Operators | 线性算子；**线性时不变性（LTI）** |
| Pure Resonance | 共振现象 |
| Frequency Response | 频率响应；实用共振 |
| Applications | LRC 电路；阻尼比 |

📝 Exam 2

#### 🟡 Unit III: Fourier Series and Laplace Transform（傅里叶级数与拉普拉斯变换）- 11 主题
| 主题 | 核心内容 |
|------|---------|
| **Fourier Series** ⭐ | 周期函数的三角级数展开 |
| Operations on FS | 微分/积分/平移对 Fourier 级数的作用 |
| Periodic Input | 周期输入下的 ODE；共振 |
| Step and Delta | 阶跃函数；**δ 函数（冲激）**；广义导数 |
| **Impulse Response** ⭐ | 单位冲激响应——系统特征描述 |
| **Convolution** ⭐⭐ | 卷积运算；卷积定理——**CNN 的数学根基** |
| **Laplace Transform** ⭐ | 拉普拉斯变换；初值问题求解工具 |
| Partial Fractions | 部分分式求逆变换 |
| Solving IVP's | 用拉普拉斯变换解初值问题 |
| Transfer Functions | 传递函数；权函数；格林公式 |
| Poles | 极点；幅频响应；与 ERF 的联系 |

📝 Exam 3

#### 🟣 Unit IV: First-order Systems（一阶方程组）- 7 主题
| 主题 | 核心内容 |
|------|---------|
| Linear Systems | 一阶线性方程组引入 |
| **Matrix Methods** ⭐ | 矩阵法；**特征值与简正模**（联系 18.06）|
| **Phase Portraits** ⭐ | 相图；定性行为（鞍点/螺旋/中心）|
| **Matrix Exponentials** ⭐ | 矩阵指数 $e^{At}$（联系 18.06 L24）|
| Nonlinear Systems | 非线性方程组 |
| **Linearization** ⭐ | 在临界点附近线性化——动力系统分析核心 |
| Limit Cycles and Chaos | 极限环；混沌——线性的局限 |

**🎯 Final Exam**

### 🎯 在 CS/AI 中的应用
- **Unit III 卷积** ⭐⭐ → **CNN 卷积神经网络**、信号处理
- **Unit III 拉普拉斯变换** → 控制论、系统建模
- **Unit IV 特征值/相图** → 动力系统、动力系统神经网络
- **Unit IV 线性化** → 优化、系统稳定性分析
- **混沌** → 复杂系统、预测极限

---

## 课程 #14 · MIT 18.152：Partial Differential Equations（偏微分方程）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 先修 | 18.03（ODE）+ 18.04（复变，建议）|
| 课程网站 | https://ocw.mit.edu/courses/mathematics/18-152-introduction-to-partial-differential-equations-fall-2011/index.htm |

**定位**：18.03 之后深入 PDE 的建模与求解。

### 📑 核心教学主题
| 主题 | 核心内容 |
|------|---------|
| **三大经典 PDE** | **波动方程**（双曲）、**热传导方程**（抛物）、**拉普拉斯方程**（椭圆）|
| **一阶 PDE** | 特征线法；运输方程 |
| **波动方程** | 行波解；达朗贝尔公式；能量守恒 |
| **热传导方程** ⭐ | 热核；平滑效应；最大值原理 |
| **拉普拉斯方程** ⭐ | 调和函数；最大值原理；边界值问题 |
| **分离变量法** | 用傅里叶级数解 PDE（联系 18.03 Unit III）|
| **格林函数** | 用源函数表示解 |
| **数值方法简介** | 有限差分；有限元（联系 18.330）|

### 🎯 在 CS/AI 中的应用
- **热传导方程** → 图上的扩散（GNN 的热核）
- **拉普拉斯算子** → 图拉普拉斯（谱聚类、谱图理论）
- **PDE 数值解** → 物理仿真、计算机图形学

---

## 课程 #15 · Cambridge：Information Theory, Pattern Recognition, and Neural Networks（MacKay）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Cambridge |
| 主讲 | **Sir David MacKay**（信息论与神经网络双修大师，R.I.P.）|
| 先修 | Calculus + Linear Algebra + Prob & Stats |
| 难度 | 🌟🌟🌟 |
| 学时 | 30-50 小时 |
| 课程网站 | http://www.inference.org.uk/mackay/itila/ |
| B站视频 | https://www.bilibili.com/video/BV1rs411T71e |
| 教材 | *Information Theory, Inference, and Learning Algorithms*（官网免费电子版）|

**定位**：信息论与机器学习的**统一视角**，MacKay 是该领域传奇。教材是该领域里程碑式著作。

### 📑 核心教学主题
| 主题 | 核心内容 |
|------|---------|
| **信息论基础** | 熵、互信息、相对熵（KL 散度）；香农编码定理 |
| **数据压缩** | 霍夫曼编码；算术编码；Lempel-Ziv |
| **信道编码** | 信道容量；香农极限；Turbo 码/LDPC 码 |
| **统计推断** | 贝叶斯推断；最大似然；**模型比较** |
| **神经网络** | 从信息论视角看神经网络；Hopfield 网络 |
| **概率图模型** | 贝叶斯网络；马尔可夫随机场 |
| **蒙特卡洛方法** | 重要抽样；MCMC；Metropolis-Hastings |

### 🎯 在 CS/AI 中的应用
- **KL 散度** → **VAE、知识蒸馏、变分推断**的核心
- **贝叶斯推断** → **贝叶斯深度学习**
- **MCMC** → 概率编程、贝叶斯采样
- **信息论统一视角** → 理解 ML 的深层结构

**学习建议**：跨信息论/概率论/神经网络的经典，R.I.P. Prof. MacKay。

---

## 📊 数学进阶部分（10 门）全部完成 ✅

| 课程 | 子类 | 核心亮点 |
|------|------|---------|
| #6 CS70 | 离散概率 | 理论↔算法映射表（RSA/纠错码/哈希）|
| #7 CS126 | 离散概率 | 随机过程 + Python Jupyter + PageRank |
| #8 6.042J | 离散概率 | Tom Leighton，CS70 备选 |
| #9 ComputationalThinking | 数值分析 | Julia 体验课（图像/数据/气候）|
| #10 18.330 | 数值分析 | Julia 数值分析，三步方法论 |
| #11 18.335 | 数值分析 | 研究生数值方法（Krylov/FFT）|
| #12 18.04 | 微分方程 | 复变函数，留数定理 |
| #13 18.03 | 微分方程 | ODE 4 Unit，卷积/CNN 根基 |
| #14 18.152 | 微分方程 | PDE 三大经典方程 |
| #15 MacKay | 综合 | 信息论+ML 统一视角 |

---

# 第三部分 · 数学高阶

> **定位**：面向高年级甚至研究生。csdiy 评价：按兴趣自取所需——"凡事硬要争有用无用倒也无趣"。

---

## 课程 #16 · Stanford EE364A：Convex Optimization（凸优化）⭐⭐⭐ ML 核心

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **Stephen Boyd**（凸优化领域大牛）|
| 先修 | **Python + 微积分 + 线代 + 概率论 + 数值分析**（先修最严的之一）|
| 语言 | **Python**（CVX 框架，支持 Python/Julia）|
| 难度 | 🌟🌟🌟🌟🌟（满星）|
| 学时 | **150 小时**（重型）|
| 课程网站 | http://stanford.edu/class/ee364a/index.html |
| B站视频 | https://www.bilibili.com/video/BV1aD4y1Q7aW |
| 教材 *Convex Optimization* | https://stanford.edu/~boyd/cvxbook/ |
| 资源汇总 | https://github.com/PKUFlyingPig/Standford_CVX101 |

**核心洞见**（csdiy 精华）：对同一问题，**建模时一个细小改变，求解难度天壤之别**——如何让你建模的方程是"凸"的，是一门**艺术**。

### 📑 核心教学主题

| 主题 | 核心内容 |
|------|---------|
| **凸集** ⭐ | 仿射集、凸集、凸包、超平面/半空间、多面体；保持凸性的运算 |
| **凸函数** ⭐ | 凸函数定义与判别；一阶/二阶条件（$\nabla^2 f\succeq 0$）；保持凸性的运算（复合、逐点最大）|
| **凸优化问题** ⭐⭐ | 标准形；线性规划（LP）、二次规划（QP）、QCQP、SOCP、SDP |
| **对偶理论** ⭐⭐ | 拉格朗日对偶；KKT 条件——**最优性的充要条件**；强/弱对偶 |
| **内点法** | 求解凸问题的核心算法（障碍法、原始-对偶内点法）|
| **无约束优化** | 梯度下降；牛顿法；拟牛顿法（BFGS）|
| **应用案例** | 逼近与拟合；统计估计；几何问题（最小体积椭球）；数值线性代数 |

### 🎯 在 CS/AI 中的应用（极高价值）
| 主题 | AI 应用 |
|------|---------|
| **梯度下降** ⭐⭐⭐ | **深度学习训练的核心算法** |
| **牛顿法/BFGS** | 二阶优化方法；逻辑回归的求解 |
| **凸性判别** | 判断损失函数是否凸（为什么用交叉熵不用 MSE）|
| **KKT 条件** | SVM 的推导；正则化的理论 |
| **LP/QP** | SVM、资源分配、排程 |
| **SDP** ⭐ | 半正定规划：组合优化的松弛、核学习、相位恢复 |

**⚠️ 学习建议**：先修最严（5 项），但**这是 ML 方向的必杀技**。csdiy 原文：EE364A 是"建模凸性"的艺术，掌握后你的 ML 建模能力会质变。

---

## 课程 #17 · MIT 6.441：Information Theory（信息论高阶）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 级别 | 研究生 |
| 先修 | 6.050J 或概率论扎实 |
| 课程网站 | https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-441-information-theory-spring-2016/syllabus/ |

**定位**：6.050J 的高阶版本，面向高年级/研究生。

### 📑 核心教学主题
| 主题 | 核心内容 |
|------|---------|
| **熵与互信息** ⭐ | 微分熵；互信息 $I(X;Y)$；数据处理不等式 |
| **信源编码** | 渐近等分性（AEP）；信源编码定理；率失真理论 |
| **信道容量** ⭐ | 离散无记忆信道；信道编码定理；高斯信道容量 $C=\frac{1}{2}\log(1+SNR)$ |
| **微分熵** | 连续随机变量的熵；最大熵分布 |
| **率失真理论** | 有损压缩的理论极限 |
| **网络信息论** | 多用户信道；广播信道；中继信道 |
| **信息论与统计** | 大偏差理论；假设检验的信息论下界 |

### 🎯 在 CS/AI 中的应用
- **互信息** ⭐ → 互信息神经估计（MINE）、表示学习
- **最大熵** → 能量模型、Soft Actor-Critic
- **率失真** → 模型压缩的理论基础

---

## 课程 #18 · MIT 18.650：Statistics for Applications（应用统计学）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 级别 | Undergraduate |
| 先修 | 概率论 |
| 课程网站 | https://ocw.mit.edu/courses/mathematics/18-443-statistics-for-applications-spring-2015/index.htm |

**定位**：应用导向的统计学，数据分析必备。

### 📑 核心教学主题
| 主题 | 核心内容 |
|------|---------|
| **参数估计** | 矩估计；**最大似然估计（MLE）**；克拉美-拉奥下界 |
| **置信区间** | 构造方法；正态/非正态情形；Bootstrap |
| **假设检验** | 显著性水平；p 值；t 检验、卡方检验、F 检验 |
| **线性回归** ⭐ | 最小二乘；模型诊断；残差分析 |
| **方差分析（ANOVA）** | 单因素/多因素方差分析 |
| **非参数统计** | 秩检验；置换检验 |
| **贝叶斯统计** | 先验/后验；共轭分布；贝叶斯回归 |

### 🎯 在 CS/AI 中的应用
- **MLE** → 几乎所有 ML 模型的训练准则
- **假设检验** → A/B 测试、模型评估
- **线性回归** → ML 的入门模型
- **Bootstrap** → 模型不确定性的估计

---

## 课程 #19 · MIT 18.781：Theory of Numbers（初等数论）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | MIT |
| 级别 | Undergraduate |
| 先修 | 无（数学成熟度）|
| 课程网站 | https://ocw.mit.edu/courses/mathematics/18-781-theory-of-numbers-spring-2012/index.htm |

**定位**：密码学/理论 CS 的数学基础。

### 📑 核心教学主题
| 主题 | 核心内容 |
|------|---------|
| **整除与素数** | 素数定理；算术基本定理；欧几里得算法（GCD）|
| **同余理论** | 模运算；中国剩余定理；费马小定理 |
| **欧拉定理** ⭐ | 欧拉 φ 函数；欧拉定理——**RSA 的数学根基** |
| **二次剩余** | 勒让德符号；二次互反律 |
| **原根与离散对数** | 原根的存在性；**离散对数问题——Diffie-Hellman 的根基** |
| **丢番图方程** | 线性丢番图方程；佩尔方程 |
| **连分数** | 连分数展开；无理数逼近 |

### 🎯 在 CS/AI 中的应用
- **RSA** → 公钥密码学（通向 CS255）
- **离散对数** → Diffie-Hellman 密钥交换、椭圆曲线密码
- **大数分解** → RSA 安全性、量子计算（Shor 算法）

---

## 课程 #20 · Stanford CS255：Cryptography（密码学）

### 课程元数据
| 字段 | 内容 |
|------|------|
| 开课 | Stanford |
| 主讲 | **Dan Boneh**（密码学顶级学者）|
| 先修 | 数论基础（18.781 或同等）|
| 课程网站 | http://crypto.stanford.edu/~dabo/cs255/ |

**定位**：数论的应用方向，网络安全/密码学方向必修。

### 📑 核心教学主题
| 主题 | 核心内容 |
|------|---------|
| **密码学原语** | 流密码；分组密码（AES）；哈希函数；MAC |
| **对称加密** ⭐ | AES；工作模式（CBC/GCM）；认证加密 |
| **公钥密码** ⭐ | **RSA**（数论应用）；**ElGamal**（离散对数）；椭圆曲线密码（ECC）|
| **数字签名** | RSA 签名；DSA；Schnorr 签名 |
| **密钥交换** | **Diffie-Hellman**；TLS 握手原理 |
| **零知识证明** ⭐ | ZKP 范式；Schnorr 协议；zk-SNARK 简介 |
| **密码协议** | 承诺方案；秘密共享；安全多方计算 |
| **后量子密码** | 格密码；编码密码——**抗量子计算**的新方向 |

### 🎯 在 CS/AI 中的应用
- **TLS/HTTPS** → 网络安全基础设施
- **数字签名** → 区块链、身份认证
- **零知识证明** ⭐ → 隐私计算、ZK-Rollup（区块链扩容）
- **同态加密** → 隐私机器学习（联邦学习、安全聚合）
- **后量子** ⭐ → 量子计算时代的安全

---

## 📊 数学高阶部分（5 门）全部完成 ✅

| 课程 | 子类 | 核心亮点 |
|------|------|---------|
| #16 EE364A | 凸优化 | Boyd；KKT；梯度下降/牛顿法（ML 核心）|
| #17 6.441 | 信息论 | 香农定理；网络信息论 |
| #18 18.650 | 统计 | MLE；假设检验；Bootstrap |
| #19 18.781 | 数论 | RSA 根基；离散对数 |
| #20 CS255 | 密码学 | Dan Boneh；公钥密码；零知识证明 |

---

# 🎯 全文档总结：20 门课程按方向的学习路径

## 按目标方向的选课套餐（复用）

### 🎓 套餐 A：通用 CS 基础（所有方向必学）
```
3Blue1Brown(4) → 18.01(1) + 18.06(3) → 18.02(2) → CS70(6) → 6.050J(5)
```
**学时约**：~300 小时。csdiy 作者反复强调的"刻骨铭心"基础。

### 🤖 套餐 B：机器学习 / AI 方向（csdiy 没明说但隐性贯穿）
```
套餐A → CS126(7)（随机过程，ML 理论基石）
      → EE364A(16) 凸优化（ML 的数学引擎，必学！）
      → 18.330(10) 数值分析（数值稳定性）
      → MacKay(15)（信息论+ML 统一视角）
```
**学时约**：+500 小时。**EE364A 是 ML 方向的必杀技**。

### 🔬 套餐 C：理论 CS / 密码学方向
```
套餐A → CS70(6) 数论部分 → 18.781(19) 初等数论 → CS255(20) 密码学
                                → 6.441(17) 信息论高阶
```

### 🌡️ 套餐 D：科学计算 / 建模方向
```
套餐A → ComputationalThinking(9, Julia体验) → 18.330(10) → 18.335(11)
                                        → 18.04(12) → 18.03(13) → 18.152(14)
```

### 📡 套餐 E：信号处理 / 通信方向
```
套餐A → 6.050J(5) → 6.441(17) 信息论 → MacKay(15)
```

### 📊 套餐 F：数据科学方向
```
套餐A → CS70(6) → CS126(7) → 18.650(18) 应用统计
```

---

## ⚠️ 关键提醒（避坑指南）

1. **先修严格性**：CS126(#7) 和 EE364A(#16) 是先修要求最多的两门（5 项先修），**不要跳级**。
2. **CS70 vs 6.042J**：二选一，内容重叠 80%+。CS70 更重算法实战（推荐）。
3. **数值分析先学体验课**：18.330(#10) 难度满星 + 150 小时，**先过 ComputationalThinking(#9)**。
4. **微分方程是可选项**：CS 培养方案普遍不要求；走图形学/物理仿真才必修。
5. **3Blue1Brown 是催化剂不是替代品**：先看 3B1B 建立直觉 + 再看 MIT 正课形式化。

---

## 📚 按课程编号索引

| # | 课程 | 难度 | 学时 | 先修 |
|---|------|------|------|------|
| 1 | MIT 18.01 单变量微积分 | 🌟🌟 | 因人 | 无 |
| 2 | MIT 18.02 多变量微积分 | 🌟🌟🌟 | 因人 | 18.01 |
| 3 | MIT 18.06 线性代数 | 🌟🌟🌟 | 因人 | 无 |
| 4 | 3Blue1Brown Essence 系列 | 🌟 | 数小时 | 无 |
| 5 | MIT 6.050J 信息与熵 | 🌟🌟🌟 | 100h | 无 |
| 6 | UCB CS70 离散数学+概率 | 🌟🌟🌟 | 60h | 无 |
| 7 | UCB CS126 概率论进阶 | 🌟🌟🌟🌟🌟 | 100h | CS70+微积分+线代 |
| 8 | MIT 6.042J CS 数学 | 🌟🌟🌟 | 50-70h | Calculus+LA |
| 9 | ComputationalThinking | 🌟🌟 | 短 | 无 |
| 10 | MIT 18.330 数值分析 | 🌟🌟🌟🌟🌟 | 150h | 微积分+线代+概率 |
| 11 | MIT 18.335 数值方法(研) | 🌟🌟🌟🌟🌟 | - | 18.330 |
| 12 | MIT 18.04 复变函数 | 🌟🌟🌟🌟 | - | 18.01/02 |
| 13 | MIT 18.03 常微分方程 | 🌟🌟🌟 | - | 18.01/02 |
| 14 | MIT 18.152 偏微分方程 | 🌟🌟🌟🌟 | - | 18.03+18.04 |
| 15 | Cambridge MacKay 信息论+ML | 🌟🌟🌟 | 30-50h | Calculus+LA+Prob |
| 16 | Stanford EE364A 凸优化 | 🌟🌟🌟🌟🌟 | 150h | Python+微积分+线代+概率+数值 |
| 17 | MIT 6.441 信息论高阶 | 🌟🌟🌟🌟🌟 | - | 6.050J 或概率扎实 |
| 18 | MIT 18.650 应用统计 | 🌟🌟🌟🌟 | - | 概率论 |
| 19 | MIT 18.781 初等数论 | 🌟🌟🌟 | - | 数学成熟度 |
| 20 | Stanford CS255 密码学 | 🌟🌟🌟🌟 | - | 数论 |

---

**文档版本**：v1.0 完整版
**数据来源**：MIT OCW 官网真实抓取 + csdiy.wiki 课程详情 + 学科知识
**最后更新**：2026-07-07
