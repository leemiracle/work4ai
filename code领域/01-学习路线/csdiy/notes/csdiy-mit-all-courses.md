# MIT 课程完全详解（csdiy 收录全部 29 门）

> 按 MIT 系号组织：**18.xxx（数学系）** + **6.xxx（EECS 系）** + 其他。
> 每门课含：元数据 + 核心教学主题 + 在 CS/AI 中的应用 + 与其他 MIT 课的联系。
> MIT OCW 主页：https://ocw.mit.edu/

---

# 🔵 18.xxx 数学系课程（13 门）

> MIT 数学系课程编号规律：18.0x 微积分/线代 → 18.1x 高阶数学 → 18.3x 数值分析 → 18.7x 数论

---

## 18.01 — Single Variable Calculus（单变量微积分）⭐

| 字段 | 内容 |
|------|------|
| 教授 | **David Jerison** + Arthur Mattuck + Haynes Miller 团队 |
| 版本 | **18.01SC**（Scholar 版，专为自学者） |
| 先修 | 无 |
| 难度 | 🌟🌟 | 学时 | 因人 |
| 主页 | https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/ |

### 完整教学大纲（5 Unit, 80+ Session）
- **Unit 1 Differentiation**：导数定义/极限/连续/求导法则（积/商/链式）/sin·cos/指数对数
- **Unit 2 Applications**：线性近似⭐/二次近似/画图/**优化**⭐/**牛顿法**⭐/中值定理/反导数
- **Unit 3 Definite Integral**：黎曼和/**微积分基本定理 FTC**⭐⭐/面积体积/**概率**⭐/数值积分
- **Unit 4 Techniques**：三角积分/分部积分/部分分式/参数方程/极坐标
- **Unit 5 Infinite**：洛必达/反常积分/**泰勒级数**⭐⭐

### 在 CS/AI 中的应用
- 链式法则（Unit 1）→ **反向传播 backprop** 的数学根基
- 线性近似（Unit 2）→ **梯度下降** 的基础
- 牛顿法（Unit 2）→ **凸优化 EE364A** 的核心算法
- 概率（Unit 3）→ **CS70/CS126 概率论** 前奏
- 泰勒级数（Unit 5）→ **数值分析 18.330 + ML 损失函数局部近似** 的根基

🔗 深度解析见 `csdiy-math-complete.md`（80+ session 逐个）

---

## 18.02 — Multivariable Calculus（多变量微积分）

| 字段 | 内容 |
|------|------|
| 教授 | **Denis Auroux** |
| 先修 | 18.01 |
| 主页 | https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/ |

### 完整教学大纲（4 Unit）
- **Unit 1 Vectors & Matrices**：向量/点积/叉积/行列式/平面方程/参数曲线
- **Unit 2 Partial Derivatives** ⭐⭐：偏导/**梯度**⭐⭐⭐/方向导数/**拉格朗日乘数法**⭐⭐/Hessian
- **Unit 3 Double Integrals**：二重积分/线积分/**格林定理**
- **Unit 4 Triple Integrals**：三重积分/球坐标/**散度定理**⭐⭐/**斯托克斯定理**⭐⭐

### 在 CS/AI 中的应用（极高）
- **梯度** → **梯度下降法**的数学根基（ML 灵魂）
- **链式法则（多元）** → **反向传播 backprop**
- **拉格朗日乘数法** → **约束优化**（SVM/正则化/EE364A）
- **散度/斯托克斯** → 计算机图形学、物理仿真

🔗 深度解析见 `csdiy-math-complete.md`

---

## 18.06 — Linear Algebra（线性代数）⭐⭐ 核心

| 字段 | 内容 |
|------|------|
| 教授 | **Gilbert Strang**（传奇，88 岁告别课）|
| 教材 | *Introduction to Linear Algebra*（清华采用）|
| 主页 | https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/ |

### 完整教学大纲（3 Unit, 34 讲）
- **Unit I: Ax=b & Four Subspaces** ⭐⭐（14 讲）：线性方程几何/消元/ LU 分解/列空间/零空间/**四个基本子空间**⭐⭐⭐/图与网络
- **Unit II: Least Squares, Determinants, Eigenvalues** ⭐⭐（13 讲）：正交/**投影矩阵**⭐⭐/Gram-Schmidt/行列式/**特征值**⭐⭐⭐/对角化/马尔可夫矩阵
- **Unit III: Positive Definite & Applications** ⭐⭐⭐（10 讲）：对称矩阵/**FFT**⭐/正定矩阵/**SVD**⭐⭐⭐/线性变换/基变换/伪逆

### 在 CS/AI 中的应用（最高价值）
| 18.06 主题 | AI 应用 |
|-----------|---------|
| 最小二乘（L17）| 线性回归 OLS |
| 特征值（L22）| PCA/谱聚类/PageRank |
| SVD（L31）| 推荐系统/图像压缩/低秩近似 |
| 马尔可夫矩阵（L25）| MDP/强化学习 |
| 正定矩阵（L29）| 凸优化判别 |

🔗 深度解析见 `csdiy-math-complete.md`（34 讲逐讲）+ 教学模式 8 课已完成

---

## 18.03 — Differential Equations（常微分方程）

| 字段 | 内容 |
|------|------|
| 教授 | **Arthur Mattuck** + Haynes Miller |
| 先修 | 18.01/18.02（建议 18.06）|
| 主页 | https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/ |

### 完整教学大纲（4 Unit, 官网真实结构）
- **Unit I: First Order ODE**：可分离变量/几何方法/数值方法/积分因子/自治方程/线性 vs 非线性
- **Unit II: Second Order Linear ODE** ⭐：特征方程/**阻尼振荡器**⭐/共振/频率响应/LRC 电路
- **Unit III: Fourier Series & Laplace** ⭐⭐：傅里叶级数/δ 函数/冲激响应/**卷积**⭐⭐/拉普拉斯变换/传递函数
- **Unit IV: First-order Systems** ⭐：矩阵法/特征值/**相图**⭐/矩阵指数/线性化/混沌

### 在 CS/AI 中的应用
- **卷积**（Unit III）→ **CNN 卷积神经网络** 的数学根基
- **拉普拉斯变换** → 控制论/系统建模
- **特征值/相图** → 动力系统分析
- **混沌** → 复杂系统/预测极限

🔗 深度解析见 `csdiy-math-complete.md`

---

## 18.04 — Complex Variables（复变函数）

| 字段 | 内容 |
|------|------|
| 教授 | **Jeremy Orloff** |
| 先修 | 18.01/18.02 |
| 主页 | https://ocw.mit.edu/courses/18-04-complex-variables-with-applications-spring-2018/ |

### 核心教学主题
- 复数与欧拉公式 / **解析函数**⭐（复导数蕴含无穷可微）/ **柯西积分定理**⭐⭐ / 泰勒&洛朗级数 / **留数定理**⭐⭐（用留数算实积分）/ 调和函数

### 应用：信号处理逆变换 / 复变神经网络 / 图论随机游走

---

## 18.152 — Partial Differential Equations（偏微分方程）

| 字段 | 内容 |
|------|------|
| 先修 | 18.03 + 18.04 |
| 主页 | https://ocw.mit.edu/courses/18-152-introduction-to-partial-differential-equations-fall-2011/ |

### 核心教学主题
- **三大经典 PDE**：波动方程/热传导方程/拉普拉斯方程
- 特征线法 / 达朗贝尔公式 / 热核 / **分离变量法**（用傅里叶级数解 PDE）
- 格林函数 / 有限差分/有限元简介

### 应用：图上的扩散（GNN 热核）/ 图拉普拉斯（谱聚类）/ 物理仿真

---

## 18.330 — Introduction to Numerical Analysis（数值分析）⭐⭐

| 字段 | 内容 |
|------|------|
| 先修 | 微积分 + 线代 + 概率 |
| 语言 | **Julia** |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 主页 | https://github.com/mitmath/18330 |
| 教材 | https://fncbook.com |

### 核心教学主题（三步方法论）
① 建立估计 → ② 估计误差 → ③ 算法实现

- **浮点表示**⭐（IEEE 754/机器精度）/ Root Finding（牛顿法/二分法）
- **线性系统**（LU/条件数⭐/Jacobi-Gauss-Seidel）/ 插值与拟合 / 数值微积分
- **ODE 数值解**⭐（Euler/Runge-Kutta/刚性）

### 应用：深度学习数值稳定性 / 条件数→多重共线性 / Newton/BFGS 根基 / Neural ODE

---

## 18.335 — Numerical Methods（研究生数值分析）

| 字段 | 内容 |
|------|------|
| 先修 | 18.330 |
| 主页 | https://ocw.mit.edu/courses/18-335j-introduction-to-numerical-methods-spring-2019/ |

### 核心主题
- 矩阵计算高级算法（QR/SVD 数值实现）/ 稀疏矩阵与 Krylov 子空间（GMRES/CG）
- 特征值问题数值方法（QR 算法）/ **快速算法**（FFT/多极子）/ 并行数值计算

---

## 18.650 — Statistics for Applications（应用统计）

| 字段 | 内容 |
|------|------|
| 先修 | 概率论 |
| 主页 | https://ocw.mit.edu/courses/18-443-statistics-for-applications-spring-2015/ |

### 核心主题
- **MLE**⭐（几乎所有 ML 训练准则）/ 置信区间 / 假设检验（t/卡方/F）
- **线性回归**⭐ / ANOVA / 非参数统计 / **贝叶斯统计**

### 应用：MLE→ML 模型训练 / A/B 测试 / Bootstrap 不确定性

---

## 18.781 — Theory of Numbers（初等数论）

| 字段 | 内容 |
|------|------|
| 先修 | 数学成熟度 |
| 主页 | https://ocw.mit.edu/courses/18-781-theory-of-numbers-spring-2012/ |

### 核心主题
- 整除与素数 / **同余理论** / **欧拉定理**⭐（RSA 根基）/ 二次剩余与互反律
- **原根与离散对数**⭐（Diffie-Hellman 根基）/ 丢番图方程 / 连分数

### 应用：RSA 密码 / 离散对数→DH/ECC / 大数分解→Shor 量子算法

---

## 6.050J — Information and Entropy（信息与熵）⭐

| 字段 | 内容 |
|------|------|
| 教授 | **Paul Penfield** + **Seth Lloyd**（量子计算先驱）|
| 先修 | 无（大一定制）|
| 主页 | https://ocw.mit.edu/courses/6-050j-information-and-entropy-spring-2008/ |

### 13 个 Unit
- 比特与编码 / **压缩**⭐（霍夫曼/熵 $H=-\sum p\log p$）/ 噪声与纠错
- 概率 / **通信**⭐（信道容量 $C=B\log(1+S/N)$）/ 推断 / **最大熵**⭐
- 物理系统/能量/温度 / **量子信息**⭐

### 应用：**交叉熵损失**（DL 分类）/ KL 散度 / 最大熵 RL / 贝叶斯推断

---

## 6.042J — Mathematics for Computer Science

| 字段 | 内容 |
|------|------|
| 教授 | **Tom Leighton**（Akamai 创始人）|
| 先修 | Calculus + LA |
| 主页 | https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/ |

### 核心主题
数学推理与证明 / 数论与 RSA / 图论 / 可数性 / 离散概率 / 自动机

---

## 6.441 — Information Theory（信息论高阶）

| 字段 | 内容 |
|------|------|
| 级别 | 研究生 |
| 主页 | https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/ |

### 核心主题
熵与互信息 / 信源编码（AEP/率失真）/ **信道编码定理**⭐ / 微分熵 / 网络信息论

### 应用：互信息→表示学习 / 最大熵→EBM/SAC / 率失真→模型压缩

---

# 🟢 6.xxx EECS 系课程（14 门）

> MIT EECS 编号：6.0x 基础 → 6.1x 系统/安全 → 6.4-6.5x AI/ML → 6.8x 高级系统

---

## 6.007 — Signals and Systems（信号与系统）

| 字段 | 内容 |
|------|------|
| 教授 | **Alan V. Oppenheim**（信号处理泰斗）|
| 主页 | https://ocw.mit.edu/resources/res-6-007-signals-and-systems-spring-2011/ |

### 核心主题
LTI 系统 / **卷积** / **傅里叶变换**⭐⭐ / 拉普拉斯变换 / 采样定理 / 滤波器设计

### 应用：CNN 卷积 / 信号处理 / 通信系统

---

## Missing Semester（计算机教育缺失的学期）⭐ 必学

| 字段 | 内容 |
|------|------|
| 主页 | https://missing.csail.mit.edu/2020/ |

### 11 讲
Shell / Vim / 数据整理 / 命令行 / **Git**⭐⭐ / 调试与性能 / 构建工具 / 安全密码学 / 虚拟机容器

---

## 6.092 — Introduction to Programming in Java

| 字段 | 内容 |
|------|------|
| 学时 | <15h（7 节课，一天可完成）|
| 主页 | https://ocw.mit.edu/courses/6-092-introduction-to-programming-in-java-january-iap-2010/ |

7 节：Java 基础/控制流/**代码风格**/OOP/继承/Debug/异常

---

## 6.100L — Introduction to CS and Programming using Python

| 字段 | 内容 |
|------|------|
| 教授 | **Ana Bell** |
| 主页 | https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/ |

### 核心主题
Python 编程 / 算法与数据结构 / **测试与调试** / **算法复杂度 Big-O**

---

## 6.006 — Introduction to Algorithms ⭐

| 字段 | 内容 |
|------|------|
| 教授 | **Erik Demaine**（算法奇才）|
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 100h+ |
| 主页 | https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/ |
| 教材 | CLRS |

### 核心主题
AVL 树/跳表/哈希/B 树 / BFS/DFS/最短路/Dijkstra/MST/拓扑排序 / **动态规划**⭐ / 贪心 / 字符串匹配

---

## 6.046 — Design and Analysis of Algorithms

| 字段 | 内容 |
|------|------|
| 教授 | Erik Demaine + Srini Devadas + **Nancy Lynch** |
| 主页 | https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/ |

### 核心主题
分治深入 + 主定理 / **DP 深入+证明** / 贪心+交换论证 / **网络流**⭐ / 线性规划 / **NP 完全+近似**⭐ / 随机算法

---

## 6.031 — Software Construction ⭐

| 字段 | 内容 |
|------|------|
| 语言 | Java | 难度 | 🌟🌟🌟🌟 | 学时 | 100h |
| 主页 | https://web.mit.edu/6.031/ |

### 三大目标
**Safe from bugs** / **Easy to understand** / **Ready for change**

### 核心主题
代码规范（注释/Spec）⭐ / ADT（RI/AF）/ OOP（Liskov 替换）/ 设计模式 / 测试 / **并行编程**⭐ / 可变 vs 不可变

---

## 6.S081 — Operating System Engineering ⭐⭐

| 字段 | 内容 |
|------|------|
| 实验室 | MIT PDOS / 教授含 **Robert Morris**（Morris 蠕虫作者）|
| 语言 | C + RISC-V |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 主页 | https://pdos.csail.mit.edu/6.828/2021/schedule.html |

### 11 个 Lab（xv6 教学操作系统）
系统调用/页表/陷阱/COW/多线程/锁/网络/文件系统 + 后半程**经典论文精读**

---

## 6.824 — Distributed System ⭐⭐

| 字段 | 内容 |
|------|------|
| 实验室 | MIT PDOS / **Robert Morris** |
| 语言 | **Go** |
| 难度 | 🌟🌟🌟🌟🌟 | 学时 | 150h |
| 主页 | https://pdos.csail.mit.edu/6.824/ |

### 4 个 Project（基于 Raft 的分布式 KV-store）⭐⭐
MapReduce / **Raft 选举+日志** / **Raft 持久化+快照** / 分片 KV-store

### 核心主题
一致性/CAP / RPC / **Raft 共识**⭐⭐⭐ / 分布式事务 / 经典论文（MapReduce/GFS/Spanner）

---

## 6.1600 — Foundations of Computer Security

| 字段 | 内容 |
|------|------|
| 先修 | 离散数学 + 编程 + 系统基础 |
| 语言 | Python3 | 学时 | 50h |
| 主页 | https://61600.csail.mit.edu/2023/ |

### 五大模块
Authentication / Transport Security / Platform Security / Software Security / Human/End-user Security

---

## 6.858 — Computer System Security

| 字段 | 内容 |
|------|------|
| 语言 | C, Python | 学时 | 150h |
| 主页 | http://css.csail.mit.edu/6.858/2022/ |

### 4 Lab（基于 Zoobar Web App）+ Final Project（SecFS）
缓冲区溢出 / 权限分离 / **符号执行**⭐ / 浏览器攻击

---

## 6.7960 — Deep Learning

| 字段 | 内容 |
|------|------|
| 先修 | 线代 + 概率 + ML 基础 |
| 难度 | 🌟🌟🌟🌟 | 学时 | 90h |
| 主页 | https://ocw.mit.edu/courses/6-7960-deep-learning-fall-2024/ |

### 核心主题
覆盖**广**：LLM/NLP + CV 双主线。理论 + 模型设计 + 应用结合。

---

## 6.5940 — TinyML and Efficient Deep Learning Computing ⭐

| 字段 | 内容 |
|------|------|
| 教授 | **Song Han**（MIT，高效 ML 先驱）|
| 难度 | 🌟🌟🌟🌟 | 学时 | 50h |
| 主页 | https://hanlab.mit.edu/courses/2024-fall-65940 |

### 三大部分
1. **轻量化技术**：剪枝/量化/蒸馏/NAS
2. **前沿高效优化**：**LLM 推理**⭐/长上下文/后训练加速/多模态/GAN/扩散
3. **高效训练**：分布式并行/自动并行/梯度压缩/边缘训练

### 5 个实验：量化/剪枝/NAS/LLM 压缩/高效部署

---

## 6.S184 — Generative AI with SDEs（扩散模型）⭐

| 字段 | 内容 |
|------|------|
| 主讲 | Peter Holderrieth + Ezra Erives（MIT CSAIL IAP）|
| 语言 | Python/PyTorch | 学时 | 20h |
| 主页 | https://diffusion.csail.mit.edu/ |
| 教材 | [Flow Matching and Diffusion Models](https://arxiv.org/abs/2506.02070) |

### 核心主题
从**随机微分方程（SDE）**视角统一理解扩散模型 / Score-based models / DDPM / **流匹配 Flow Matching** / 分子设计/机器人应用

---

# 🟡 其他 MIT 课程

---

## ComputationalThinking（18.S191 — 计算思维）

| 字段 | 内容 |
|------|------|
| 教授 | **Alan Edelman** + David Sanders + **Charles Leiserson** |
| 语言 | **Julia** |
| 主页 | https://ocw.mit.edu/courses/18-s191-introduction-to-computational-thinking-fall-2022/ |

### 三大 Topic
图像处理（卷积/FFT）/ 社会科学与数据科学（统计/可视化/回归）/ 气候学建模（ODE 数值解）

---

## Web Development Crash Course（IAP）

| 字段 | 内容 |
|------|------|
| 主页 | https://weblab.mit.edu/schedule/ |
| 语言 | JS/HTML/CSS/NoSQL |

4 周 IAP 课程，从零掌握 Web 前后端技术栈。

---

# 📊 MIT 课程学习路径（按方向）

## 🎓 数学方向（csdiy 数学篇 = 全 MIT）
```
18.01 → 18.02 → 18.06 → 6.050J → 6.042J/18.03 → 18.330 → 18.04/18.152 → 18.650/18.781/6.441
```

## 💻 系统方向（MIT EECS 核心）
```
Missing Semester → 6.100L → 6.006 → 6.031 → 6.S081(OS) → 6.824(分布式) → 6.858(安全)
```

## 🤖 AI/ML 方向
```
18.06 + 18.02(梯度) → 6.042J(概率) → 6.7960(DL) → 6.5940(高效DL) → 6.S184(生成AI)
```

## ⚡ 高效部署方向（就业热门）
```
6.7960(DL基础) → 6.5940(TinyML)⭐ → 6.S184(扩散) 
```

---

## 📚 按编号索引（29 门）

| 编号 | 名称 | 系 | 难度 | 核心 |
|------|------|-----|------|------|
| 18.01 | 单变量微积分 | 数学 | 🌟🌟 | 泰勒级数/牛顿法 |
| 18.02 | 多变量微积分 | 数学 | 🌟🌟🌟 | 梯度/拉格朗日 |
| 18.06 | 线性代数 ⭐⭐ | 数学 | 🌟🌟🌟 | SVD/特征值/最小二乘 |
| 18.03 | 常微分方程 | 数学 | 🌟🌟🌟 | 卷积/CNN 根基 |
| 18.04 | 复变函数 | 数学 | 🌟🌟🌟🌟 | 留数定理 |
| 18.152 | 偏微分方程 | 数学 | 🌟🌟🌟🌟 | 三大经典 PDE |
| 18.330 | 数值分析 ⭐ | 数学 | 🌟🌟🌟🌟🌟 | Julia/浮点/条件数 |
| 18.335 | 数值方法(研) | 数学 | 🌟🌟🌟🌟🌟 | Krylov/FFT |
| 18.650 | 应用统计 | 数学 | 🌟🌟🌟🌟 | MLE/假设检验 |
| 18.781 | 初等数论 | 数学 | 🌟🌟🌟 | RSA 根基 |
| 6.050J | 信息与熵 ⭐ | EECS | 🌟🌟🌟 | 熵/信道容量 |
| 6.042J | CS 数学 | EECS | 🌟🌟🌟 | Tom Leighton |
| 6.441 | 信息论高阶 | EECS | 🌟🌟🌟🌟🌟 | 香农定理 |
| 6.007 | 信号与系统 | EECS | 🌟🌟 | Oppenheim |
| — | Missing Semester ⭐ | EECS | 🌟🌟 | Git/Shell/Vim |
| 6.092 | Java 入门 | EECS | 🌟🌟 | 7 节速成 |
| 6.100L | Python 入门 | EECS | 🌟🌟 | Big-O |
| 6.006 | 算法入门 ⭐ | EECS | 🌟🌟🌟🌟🌟 | Erik Demaine |
| 6.046 | 算法设计 | EECS | 🌟🌟🌟🌟🌟 | NP/网络流 |
| 6.031 | 软件构造 ⭐ | EECS | 🌟🌟🌟🌟 | 代码质量 |
| 6.S081 | 操作系统 ⭐⭐ | EECS | 🌟🌟🌟🌟🌟 | xv6/11 Lab |
| 6.824 | 分布式系统 ⭐⭐ | EECS | 🌟🌟🌟🌟🌟 | Raft/Go |
| 6.1600 | 安全基础 | EECS | 🌟🌟🌟 | 五模块 |
| 6.858 | 系统安全 | EECS | 🌟🌟🌟🌟🌟 | 符号执行 |
| 6.7960 | 深度学习 | EECS | 🌟🌟🌟🌟 | CV+NLP 双主线 |
| 6.5940 | TinyML ⭐ | EECS | 🌟🌟🌟🌟 | 量化/剪枝/LLM |
| 6.S184 | 生成AI | EECS | 🌟🌟🌟🌟 | 扩散/SDE |
| 18.S191 | 计算思维 | 数学 | 🌟🌟 | Julia |
| — | Web 开发(IAP) | EECS | 🌟🌟🌟 | 全栈速成 |

---

**文档版本**：v1.0（MIT 全 29 门课程详解）
**数据来源**：MIT OCW 官网 + csdiy.wiki + 学科知识
**最后更新**：2026-07-07
