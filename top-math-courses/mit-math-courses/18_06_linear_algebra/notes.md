# MIT 18.06 · 章节笔记

> **教材**：Strang, *Introduction to Linear Algebra* (6th ed, 2022)
> **目录核实**：math.mit.edu/~gs/linearalgebra/ila6/ila6outline.pdf
> **视频**：OCW 18.06 (Strang 34 讲) — ocw.mit.edu/courses/18-06-linear-algebra-spring-2010

---

## 五个矩阵分解（Strang 的核心框架）

Strang 6th edition 用**五个分解**贯穿全书：

| 分解 | 公式 | 含义 |
|---|---|---|
| **A = CR** | C=独立列, R=行简化 | 揭示列空间/行空间 |
| **A = LU** | L=下三角, U=上三角 | 高斯消元的矩阵形式 |
| **A = QR** | Q=正交, R=上三角 | Gram-Schmidt 正交化 |
| **S = QΛQ⁻¹** | Q=特征向量, Λ=特征值 | 谱分解（方阵对角化）|
| **A = UΣVᵀ** | U,V=正交, Σ=奇异值 | **SVD** ★ |

---

## 第 1 章：Vectors and Matrices

### 1.1 向量的线性组合

$\mathbf{u} = c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + \dots + c_n\mathbf{v}_n$

**关键概念**：所有 $c\mathbf{v}_1 + d\mathbf{v}_2$ 的集合构成一个**平面**（span）。

### 1.2 长度与角度（点积）

- **点积**：$\mathbf{v} \cdot \mathbf{w} = v_1 w_1 + \dots + v_n w_n$
- **长度**：$\|\mathbf{v}\| = \sqrt{\mathbf{v} \cdot \mathbf{v}}$
- **Cauchy-Schwarz**：$|\mathbf{v} \cdot \mathbf{w}| \leq \|\mathbf{v}\|\|\mathbf{w}\|$
- **角度**：$\cos\theta = \frac{\mathbf{v} \cdot \mathbf{w}}{\|\mathbf{v}\|\|\mathbf{w}\|}$

### 1.3 矩阵与列空间

- **矩阵-向量乘法 Ax** = 列向量的线性组合 $= x_1\mathbf{a}_1 + x_2\mathbf{a}_2 + \dots + x_n\mathbf{a}_n$
- **列空间** $C(A)$ = 所有 Ax 的集合 = 列向量的 span

### 1.4 矩阵乘法 AB 和 CR

- **AB**：$(AB)_{ij} = \sum_k A_{ik}B_{kj}$（行×列）
- **CR 分解** ★：$A = CR$，C 是独立列，R 是行简化矩阵
- **四种视角**：行×列、列×行、外积、分块

---

## 第 2 章：Solving Ax = b

### 2.1 消元法（Elimination）

- **高斯消元**：用行变换将矩阵化为上三角 U
- **主元（pivot）**：对角线上的非零元素
- **消元失败**：主元为 0 时需要行交换

### 2.2 A = LU 分解

$$A = LU, \quad L = \text{下三角（乘数）}, \quad U = \text{上三角（消元结果）}$$

- L 记录了消元过程的乘数
- **PA = LU**：带行交换的版本（P = 置换矩阵）

### 2.3 矩阵的逆

- $A^{-1}A = I$
- $(AB)^{-1} = B^{-1}A^{-1}$
- **可逆条件**：det A ≠ 0 / 列满秩 / Ax=0 只有零解

### 2.4 完整解 Ax = b

$Ax = b$ 的完整解 = **特解** + **零空间**：

$$\mathbf{x} = \mathbf{x}_p + c_1\mathbf{x}_n$$

---

## 第 3 章：Four Fundamental Subspaces ★

**这是 Strang 最深刻的贡献**——每个矩阵定义 4 个子空间：

| 子空间 | 符号 | 属于 | 维度 |
|---|---|---|---|
| **列空间** | $C(A)$ | $\mathbb{R}^m$ | $r$ |
| **零空间** | $N(A)$ | $\mathbb{R}^n$ | $n-r$ |
| **行空间** | $C(A^T)$ | $\mathbb{R}^n$ | $r$ |
| **左零空间** | $N(A^T)$ | $\mathbb{R}^m$ | $m-r$ |

**关键定理**（Fundamental Theorem of Linear Algebra）：

1. $r = \text{rank}(A)$
2. $C(A)$ 和 $N(A^T)$ 是 $\mathbb{R}^m$ 中的正交补
3. $C(A^T)$ 和 $N(A)$ 是 $\mathbb{R}^n$ 中的正交补

### 3.1 向量空间与子空间

- **向量空间**：对加法和数乘封闭的集合
- **子空间**：向量空间内的向量空间

### 3.2 零空间

$N(A) = \{\mathbf{x} : A\mathbf{x} = \mathbf{0}\}$

### 3.3 A = CR 与秩

$A = CR$ 中 C 的列数 = 秩 $r$

### 3.4 独立性与基

- **线性独立**：$c_1\mathbf{v}_1 + \dots + c_k\mathbf{v}_k = 0 \Rightarrow$ 所有 $c_i = 0$
- **基**：独立且张成的集合
- **维度**：基中向量的个数

---

## 第 4 章：Orthogonality

### 4.1 正交子空间

两个子空间 $V, W$ 正交：$\mathbf{v} \cdot \mathbf{w} = 0, \forall \mathbf{v} \in V, \mathbf{w} \in W$

### 4.2 投影

**向量到向量的投影**：

$$\mathbf{p} = \frac{\mathbf{a}^T\mathbf{b}}{\mathbf{a}^T\mathbf{a}}\mathbf{a}$$

**向量到子空间的投影**：

$$P = A(A^TA)^{-1}A^T$$

### 4.3 最小二乘法 ★

$Ax = b$ 无解时，求 $A\hat{x} \approx b$ 的最佳近似：

$$A^TA\hat{x} = A^Tb \quad \text{(Normal Equations)}$$

**ML 关联**：线性回归 = 最小二乘法。

### 4.4 Gram-Schmidt 与 QR ★

$$A = QR, \quad Q = \text{正交矩阵}, \quad R = \text{上三角}$$

Gram-Schmidt 过程：
1. $\mathbf{q}_1 = \mathbf{a}_1 / \|\mathbf{a}_1\|$
2. $\mathbf{q}_2 = (\mathbf{a}_2 - (\mathbf{q}_1^T\mathbf{a}_2)\mathbf{q}_1) / \|\dots\|$
3. ...

---

## 第 5 章：Determinants

### 5.1 行列式性质

1. $\det I = 1$
2. 行交换变号
3. 行线性
4. 两行相同 → det = 0
5. 行消元不变 det
6. $\det A = 0 \iff A$ 不可逆

### 5.2 行列式公式

- **代数余子式展开**：$\det A = \sum_j a_{ij}C_{ij}$
- **置换公式**：$\det A = \sum_{\sigma} \text{sign}(\sigma) \prod_i a_{i\sigma(i)}$

### 5.3 Cramer 法则

$x_i = \det A_i / \det A$（其中 $A_i$ 把 A 的第 i 列换成 b）

---

## 第 6 章：Eigenvalues and Eigenvectors ★

### 6.1 定义

$$A\mathbf{x} = \lambda\mathbf{x}, \quad \mathbf{x} \neq 0$$

$\lambda$ 是特征值，$\mathbf{x}$ 是特征向量。

### 6.2 对角化

$$S = Q\Lambda Q^{-1}$$

$Q$ 的列是特征向量，$\Lambda$ 是特征值对角矩阵。

### 6.3 差分方程与矩阵幂

$A^k = Q\Lambda^k Q^{-1}$

### 6.4 对称矩阵的谱定理 ★

$$A = Q\Lambda Q^T \quad (\text{当 } A = A^T)$$

- 特征值全实数
- 特征向量正交
- **ML 关联**：PCA、协方差矩阵

### 6.5 正定矩阵 ★

$A$ 正定 $\iff \mathbf{x}^TA\mathbf{x} > 0, \forall \mathbf{x} \neq 0$

- 所有特征值 > 0
- 所有主子式 > 0
- $A = R^TR$（R 列满秩）
- **ML 关联**：Hessian 正定 = 局部最小值

---

## 第 7 章：The Singular Value Decomposition (SVD) ★★★

**这是全书的高潮**。

### 7.1 SVD 定理

$$A = U\Sigma V^T$$

- $U$：$m \times m$ 正交矩阵（左奇异向量）
- $\Sigma$：$m \times n$ 对角矩阵（奇异值 $\sigma_1 \geq \sigma_2 \geq \dots \geq 0$）
- $V$：$n \times n$ 正交矩阵（右奇异向量）

### 7.2 几何意义

任何线性变换 = **旋转** ($V^T$) → **缩放** ($\Sigma$) → **旋转** ($U$)

### 7.3 SVD 与四个子空间

- $V$ 的前 $r$ 列 → 行空间的标准正交基
- $U$ 的前 $r$ 列 → 列空间的标准正交基
- $V$ 的后 $n-r$ 列 → 零空间的标准正交基
- $U$ 的后 $m-r$ 列 → 左零空间的标准正交基

### 7.4 低秩近似 ★

$$A_k = \sum_{i=1}^k \sigma_i \mathbf{u}_i\mathbf{v}_i^T$$

**Eckart-Young 定理**：$A_k$ 是秩 $\leq k$ 的矩阵中，最接近 $A$ 的（Frobenius 范数意义下）。

**ML 关联**：
- PCA = 对协方差矩阵做 SVD
- Transformer 低秩近似（如 LoRA）
- 推荐系统（Netflix Prize 的核心方法）
- 图像压缩

### 7.5 伪逆

$$A^+ = V\Sigma^+ U^T$$

- $A^+b$ = 最小范数最小二乘解
- **ML 关联**：正则化回归

### 7.6 PCA（主成分分析）

1. 中心化数据 $X$
2. 计算 $X^TX$（协方差矩阵）
3. 特征分解 $X^TX = V\Lambda V^T$
4. 投影到前 $k$ 个特征向量

等价于 SVD：$X = U\Sigma V^T$，取 $V$ 的前 $k$ 列。

---

## 第 8 章：Linear Transformations

### 8.1 线性变换定义

$T(\mathbf{x} + \mathbf{y}) = T(\mathbf{x}) + T(\mathbf{y})$
$T(c\mathbf{x}) = cT(\mathbf{x})$

### 8.2 矩阵表示

每个线性变换 $T: \mathbb{R}^n \to \mathbb{R}^m$ 对应一个 $m \times n$ 矩阵 $A$。

### 8.3 基变换

换基 = $A' = M^{-1}AM$

---

## 第 9 章：Linear Algebra in Engineering & Deep Learning

Strang 6th edition 新增（2022）。

### 9.1 图与邻接矩阵

- **图拉普拉斯** $L = D - A$（$D$ = 度矩阵，$A$ = 邻接矩阵）
- **ML 关联**：图神经网络（GNN）、谱聚类

### 9.2 傅里叶矩阵与 FFT

- **傅里叶矩阵** $F$：$F_{jk} = e^{-2\pi ijk/n}$
- **FFT**：$O(n \log n)$ 计算 $F\mathbf{x}$
- **ML 关联**：信号处理、卷积加速

### 9.3 马尔可夫矩阵

- 每列和为 1 的非负矩阵
- 最大特征值 = 1
- **ML 关联**：PageRank、MCMC

### 9.4 深度学习与低秩微调 ★★★

深度网络的每一个"层"本质就是**线性变换 + 非线性**：

$$\mathbf{h} = \sigma(W\mathbf{x} + \mathbf{b})$$

18.06 的全部工具都在这里派上用场。

#### (a) 反向传播 = Jacobian 链式法则

对复合函数 $L = L(\mathbf{h}_3),\ \mathbf{h}_3 = f_3(\mathbf{h}_2),\dots,\mathbf{h}_1 = f_1(\mathbf{x})$，梯度是 **Jacobian 矩阵的链式乘积**：

$$\frac{\partial L}{\partial \mathbf{x}} = J_1^T J_2^T J_3^T \frac{\partial L}{\partial \mathbf{h}_3}$$

- 每层 $f_i$ 的 Jacobian $J_i = \partial\mathbf{h}_{i}/\partial\mathbf{h}_{i-1}$。
- **梯度消失/爆炸**的本质：$\prod J_i^T$ 的乘积 → 特征值的乘积 $\prod\lambda_i$。当 $\lambda_i<1$ 连乘→消失；$\lambda_i>1$→爆炸。正交初始化让 $\|J_i\|\approx1$，是为了保持谱半径稳定。

#### (b) Attention = 矩阵乘法 + softmax

$$\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

- $QK^T$：$(n\times d)(d\times n)=n\times n$ 的**相似度矩阵**（列空间几何：query 投影到 key 方向）。
- $\sqrt{d_k}$ 缩放：点积的方差 $\sim d_k$，除以 $\sqrt{d_k}$ 控制 softmax 输入的尺度（数值稳定性）。
- **ML 关联**：18.06 第 1 章（矩阵乘法）+ 第 4 章（正交性 = 注意力的几何）。

#### (c) LoRA = 低秩参数更新（2024-2026 大热）★★★

**问题**：微调 175B 参数的 GPT 需要存全部 $\Delta W\in\mathbb{R}^{d\times k}$，显存爆炸。

**LoRA 假设**（已被实验验证）：预训练权重的**任务适配增量是低秩的**。

$$W = W_0 + \Delta W \approx W_0 + BA$$

- $W_0\in\mathbb{R}^{d\times k}$：冻结的预训练权重（不训练）。
- $B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k}$：可训练的低秩因子，秩 $r\ll\min(d,k)$。
- 参数量：$dk \to r(d+k)$。当 $d=k=4096,\ r=8$ 时，$16{,}777{,}216 \to 65{,}536$（缩减 256×）。

**为什么有效？** Eckart-Young 定理保证：若真实的 $\Delta W$ 近似秩 $r$，则 $BA$ 这个秩-$r$ 参数化能很好地重建它。实验显示语言模型的适配增量本征维度确实很低（Aghajanyan 等发现 $r\sim O(100)$ 即可）。

**QLoRA**（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）：在 LoRA 基础上把 $W_0$ 量化到 **4-bit NormalFloat**。NF4 的设计利用了权重近似正态分布 $W\sim\mathcal{N}(0,\sigma^2)$，量化格点按正态分位数 $\Phi^{-1}$ 排布，使量化误差信息论最优——这是**概率分布 + 矩阵量化**的交叉。

**统一视角**：LoRA / PCA / 推荐系统 / 图像压缩，都是**同一个 SVD 低秩近似**的不同应用：

| 应用 | 矩阵 | 低秩近似 |
|---|---|---|
| PCA | 中心化数据 $X$ | 主成分 = $V$ 前 $k$ 列 |
| 图像压缩 | 像素矩阵 | $A_k=\sum_{i=1}^k\sigma_i u_iv_i^T$ |
| 推荐系统 | 用户-物品评分 | 低秩潜在因子 |
| **LoRA** | 权重增量 $\Delta W$ | $\Delta W\approx BA$ |

#### (d) 正交性与 Transformer 稳定性

- 残差连接 $\mathbf{h}_{l+1}=\mathbf{h}_l+f(\mathbf{h}_l)$ 让信息"恒等"流动，本质是让变换接近**单位矩阵** $I$（谱 = 全 1）。
- LayerNorm 把每层激活归一化到 $\|\mathbf{h}\|\approx\text{const}$，等价于在每层约束**范数**，防止谱爆炸。

---

## 线性代数的统一图景（Strang 的"Big Picture"）

把全书串成一张图：

```
        ┌─────────────── 五个矩阵分解（贯穿全书）───────────────┐
        │  A=CR → A=LU → A=QR → S=QΛQ⁻¹ → A=UΣVᵀ              │
        │  (独立列) (消元) (正交化) (谱分解)   (SVD 万能)        │
        └──────────────────────────────────────────────────────┘
                              │
        ┌─────────────── 四个基本子空间（几何骨架）─────────────┐
        │  行空间 C(Aᵀ) ⟂ 零空间 N(A)        (在 ℝⁿ 中正交补)   │
        │  列空间 C(A)  ⟂ 左零空间 N(Aᵀ)     (在 ℝᵐ 中正交补)   │
        │  维度: r + (n-r) = n ;  r + (m-r) = m                 │
        └──────────────────────────────────────────────────────┘
                              │
        ┌─────────────── 应用出口 ──────────────────────────────┐
        │  最小二乘 → 回归    正定矩阵 → 优化     图拉普拉斯→GNN│
        │  谱定理 → PCA       SVD → 降维/LoRA    傅里叶→卷积    │
        │  马尔可夫 → PageRank/MCMC                              │
        └──────────────────────────────────────────────────────┘
```

**一句话总结**：所有线代应用都归结为"**找一个好的基**"——SVD/PCA 找统计最优基，傅里叶找频域基，特征向量找不变方向基，Gram-Schmidt 找正交基。

---

## 与 ML 的关联总表

| 线代概念 | ML 应用 |
|---|---|
| 矩阵乘法 | 神经网络 forward pass |
| 四个子空间 | 理解 over/under-determined 系统 |
| 最小二乘 | 线性回归 |
| 特征值/特征向量 | PCA、协方差矩阵 |
| 对称矩阵谱分解 | 样本协方差矩阵 |
| 正定矩阵 | Hessian（优化） |
| **SVD** ★ | PCA、推荐系统、低秩近似 |
| **伪逆** | 正则化回归 |
| 图拉普拉斯 | GNN、谱聚类 |
| 傅里叶矩阵 | CNN（卷积=频域乘法） |
| 马尔可夫矩阵 | PageRank、MCMC |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播**：梯度 = Jacobian，18.06 第 1-3 章
- **讲透 Transformer**：Attention = $QK^T$ 矩阵乘法 + softmax，18.06 第 1-7 章
- **讲透优化器**：正定矩阵 + 特征值，18.06 第 6 章
- **讲透 MRL**：SVD 低秩近似，18.06 第 7 章
