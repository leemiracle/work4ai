# 数学（基础 3 + 进阶 6 = 9 门）深度展开

> **来源**：csdiy.wiki + librarian delegate（brisk-golden-falcon）实际 webfetch 验证

---

## 数学基础（3 门）

### 1. MIT 18.01 / 18.02: Calculus ｜ 弱（背景知识）
- **讲师**：MIT
- **难度**：🌟🌟 ｜ **学时**：因人而异
- **官网**：[18.01 OCW](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/) / [18.02 OCW](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/)
- **辅助**：[3Blue1Brown 微积分的本质](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr)
- **价值**：18.06/18.330 前置；理解梯度/导数有助于激活函数数值行为

### 2. ⭐ MIT 18.06: Linear Algebra（Gilbert Strang）｜ 核心
- **讲师**：**Gilbert Strang**（88 岁告别课，执教 MIT 61 年）
- **难度**：🌟🌟🌟 ｜ **学时**：因人而异
- **官网**：[OCW Fall 2011](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/)
- **教材**：*Introduction to Linear Algebra*, Strang — [官网](https://math.mit.edu/~gs/linearalgebra/)（清华采用为官方教材）
- **辅助**：[3Blue1Brown 线性代数的本质](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab)
- **核心价值**：**NEON 算子优化核心是矩阵乘法 GEMM + 向量点积的 SIMD 加速**。深刻理解矩阵分解（LU/QR）、向量空间、线性变换是编写高效 NEON GEMM kernel（tiling/blocking/packing）的理论基石

### 3. MIT 6.050J: Information Theory and Entropy ｜ 弱
- **讲师**：Penfield
- **难度**：🌟🌟🌟 ｜ **学时**：100h
- **官网**：[OCW Spring 2008](https://ocw.mit.edu/courses/6-050j-information-and-entropy-spring-2008/)
- **教材**：[Information and Entropy 免费 PDF](https://ocw.mit.edu/courses/6-050j-information-and-entropy-spring-2008/resources/mit6_050js08_textbook/)
- **价值**：若涉及量化（INT8/INT4 压缩）的精度评估可略参考

---

## 数学进阶（6 门）

### 4. UCB CS70: Discrete Math and Probability ｜ 弱
- **难度**：🌟🌟🌟 ｜ **学时**：60h
- **官网**：http://www.eecs70.org/
- **GitHub**：[PKUFlyingPig/UCB-CS70](https://github.com/PKUFlyingPig/UCB-CS70)
- 每模块（逻辑/图论/数论/概率）对应实际算法（RSA、纠错码、哈希表）

### 5. UCB CS126: Probability Theory ｜ 弱
- **讲师**：Jean Walrand
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：[fa20](https://inst.eecs.berkeley.edu/~ee126/fa20/content.html)
- **教材**：*Probability in EE and CS* — [PDF](https://link.springer.com/content/pdf/10.1007%2F978-3-030-49995-2.pdf)
- **GitHub**：[PKUFlyingPig/EECS126](https://github.com/PKUFlyingPig/EECS126)

### 6. MIT 6.042J: Mathematics for CS ｜ 弱
- **讲师**：**Tom Leighton**（Akamai 联合创始人）
- **难度**：🌟🌟🌟 ｜ **学时**：50-70h
- **官网**：[Spring 2015](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1n64y1i777/)

### 7. ⭐⭐ MIT 18.330: Introduction to Numerical Analysis ｜ 核心（lens 04/08）
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：[github.com/mitmath/18330](https://github.com/mitmath/18330)
- **教材**：[fncbook.com](https://fncbook.com)（开源，含丰富 Julia 实例）
- **GitHub**：[PKUFlyingPig/MIT18.330](https://github.com/PKUFlyingPig/MIT18.330)
- **核心价值**：**最直接相关的数学课**。浮点表示（FP32/FP16/BF16 精度）、舍入误差分析、数值稳定性——正是算子优化必须处理的精度与正确性问题。**直接对应 lens-precision.c 的 FP16 累加 bug 理论依据**

### 8. ⭐⭐ Stanford EE364A: Convex Optimization（Boyd）｜ 中等
- **讲师**：**Stephen Boyd**（凸优化大牛）
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：http://stanford.edu/class/ee364a/index.html
- **教材**：*Convex Optimization* — [stanford.edu/~boyd/cvxbook](https://stanford.edu/~boyd/cvxbook/)
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1aD4y1Q7aW)
- **GitHub**：[PKUFlyingPig/Standford_CVX101](https://github.com/PKUFlyingPig/Standford_CVX101)
- **价值**：模型量化/稀疏化的优化建模（最优量化粒度搜索）涉及凸优化

### 9. Information Theory, PR&NN（MacKay）｜ 弱
- **讲师**：**Sir David MacKay**（已故，Cambridge）
- **难度**：🌟🌟🌟 ｜ **学时**：30-50h
- **官网**：http://www.inference.org.uk/mackay/itila/
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1rs411T71e)
- 信息论与神经网络交叉视角，里程碑著作

---

## 项目相关性总览

| 课程 | 相关度 | 具体价值 |
|---|---|---|
| **MIT 18.06** | ⭐⭐⭐ 核心 | GEMM 数学基础，矩阵分解 = NEON tiling 理论 |
| **MIT 18.330** | ⭐⭐⭐ 核心 | 浮点误差 = lens-precision + FP16 累加 bug 理论依据 |
| **Stanford EE364A** | ⭐⭐ 中等 | 凸优化 = 量化粒度搜索 |
| 其余 6 门 | ⭐ 弱 | 数学背景知识 |
