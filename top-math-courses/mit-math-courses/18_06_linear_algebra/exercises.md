# MIT 18.06 · 习题集（精选 + 解题思路）

> **来源**：MIT OCW 18.06 Problem Sets（公开免费）+ Strang 6th ed 习题 + 自编
> **参考**：[ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/assignments](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/assignments/)

---

## 第 1 章 · Vectors and Matrices

### Q1.1（基础）
$\mathbf{v}_1 = (1,1,0)$, $\mathbf{v}_2 = (0,1,1)$, $\mathbf{v}_3 = (1,0,1)$。这三个向量是否线性独立？

<details><summary>解</summary>

构造矩阵 $A = \begin{pmatrix} 1 & 0 & 1 \\ 1 & 1 & 0 \\ 0 & 1 & 1 \end{pmatrix}$，$\det A = 2 \neq 0$，所以独立。

**ML 关联**：特征向量的独立性 → PCA 中主成分的选择。
</details>

### Q1.2（点积）
证明 Cauchy-Schwarz 不等式：$|\mathbf{v} \cdot \mathbf{w}| \leq \|\mathbf{v}\|\|\mathbf{w}\|$。

<details><summary>解</summary>

对任意 $t$，$\|\mathbf{v} + t\mathbf{w}\|^2 \geq 0$。展开：
$$\|\mathbf{v}\|^2 + 2t(\mathbf{v}\cdot\mathbf{w}) + t^2\|\mathbf{w}\|^2 \geq 0$$

这是关于 $t$ 的二次式恒非负 → 判别式 $\leq 0$：
$$4(\mathbf{v}\cdot\mathbf{w})^2 \leq 4\|\mathbf{v}\|^2\|\mathbf{w}\|^2$$

**ML 关联**：Hölder 不等式的最简形式。
</details>

---

## 第 2 章 · Solving Ax = b

### Q2.1（LU 分解）
求 $A = \begin{pmatrix} 2 & 1 \\ 6 & 8 \end{pmatrix}$ 的 LU 分解。

<details><summary>解</summary>

消元：第 2 行减 3 倍第 1 行：
$$U = \begin{pmatrix} 2 & 1 \\ 0 & 5 \end{pmatrix}, \quad l_{21} = 3$$

$$L = \begin{pmatrix} 1 & 0 \\ 3 & 1 \end{pmatrix}, \quad A = LU = \begin{pmatrix} 1 & 0 \\ 3 & 1 \end{pmatrix}\begin{pmatrix} 2 & 1 \\ 0 & 5 \end{pmatrix}$$

验证：$LU = \begin{pmatrix} 2 & 1 \\ 6 & 8 \end{pmatrix}$ ✓
</details>

### Q2.2（零空间）
求 $A = \begin{pmatrix} 1 & 2 & 3 \\ 2 & 4 & 6 \end{pmatrix}$ 的零空间。

<details><summary>解</summary>

$A$ 的秩 = 1（行 2 = 2×行 1）。$Ax = 0 \Rightarrow x_1 + 2x_2 + 3x_3 = 0$。

令 $x_2 = s, x_3 = t$，则 $x_1 = -2s - 3t$。

$$N(A) = s\begin{pmatrix} -2 \\ 1 \\ 0 \end{pmatrix} + t\begin{pmatrix} -3 \\ 0 \\ 1 \end{pmatrix}$$

零空间维度 = $n - r = 3 - 1 = 2$。
</details>

---

## 第 3 章 · Four Fundamental Subspaces

### Q3.1（四个子空间）
$A = \begin{pmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{pmatrix}$。找出 $C(A), N(A), C(A^T), N(A^T)$ 的基和维度。

<details><summary>解</summary>

$r = \text{rank}(A) = 2$（行向量独立）。

- $C(A) \subseteq \mathbb{R}^2$：基 = $A$ 的两列（独立），dim = 2
- $N(A) \subseteq \mathbb{R}^3$：dim = $3 - 2 = 1$。解 $Ax = 0$：$x = (1,-2,1)^T$
- $C(A^T) \subseteq \mathbb{R}^3$：基 = $A$ 的两行，dim = 2
- $N(A^T) \subseteq \mathbb{R}^2$：dim = $2 - 2 = 0$（只有零向量）
</details>

---

## 第 4 章 · Orthogonality

### Q4.1（最小二乘）★
给定点 $(0,1), (1,3), (2,5)$，用最小二乘法拟合直线 $y = a + bt$。

<details><summary>解</summary>

设计矩阵 $A = \begin{pmatrix} 1 & 0 \\ 1 & 1 \\ 1 & 2 \end{pmatrix}$, $\mathbf{b} = (1,3,5)^T$。

Normal equations: $A^TA\hat{\mathbf{x}} = A^T\mathbf{b}$

$$A^TA = \begin{pmatrix} 3 & 3 \\ 3 & 5 \end{pmatrix}, \quad A^T\mathbf{b} = \begin{pmatrix} 9 \\ 13 \end{pmatrix}$$

解：$\hat{\mathbf{x}} = (A^TA)^{-1}A^T\mathbf{b} = \begin{pmatrix} 1 \\ 2 \end{pmatrix}$

拟合直线：$y = 1 + 2t$。

**ML 关联**：这就是线性回归的闭式解。
</details>

### Q4.2（Gram-Schmidt）
对 $\mathbf{a}_1 = (1,1,0), \mathbf{a}_2 = (1,0,1)$ 执行 Gram-Schmidt 正交化。

<details><summary>解</summary>

$\mathbf{q}_1 = \frac{1}{\sqrt{2}}(1,1,0)$

$\mathbf{v}_2 = \mathbf{a}_2 - (\mathbf{q}_1 \cdot \mathbf{a}_2)\mathbf{q}_1 = (1,0,1) - \frac{1}{\sqrt{2}} \cdot \frac{1}{\sqrt{2}}(1,1,0) = (1/2, -1/2, 1)$

$\mathbf{q}_2 = \frac{\mathbf{v}_2}{\|\mathbf{v}_2\|} = \frac{(1/2, -1/2, 1)}{\sqrt{1/4+1/4+1}} = \frac{1}{\sqrt{3/2}}(1/2, -1/2, 1)$
</details>

---

## 第 5 章 · Determinants

### Q5.1（行列式公式）
证明 $\det A = 0 \iff A$ 不可逆。

<details><summary>解</summary>

$\det A = 0$ $\Rightarrow$ 消元后某行全零 $\Rightarrow$ $A$ 的列线性相关 $\Rightarrow$ $Ax = 0$ 有非零解 $\Rightarrow$ $A^{-1}$ 不存在。

反方向类似。

**ML 关联**：矩阵可逆性影响梯度的存在性。
</details>

---

## 第 6 章 · Eigenvalues

### Q6.1（对角化）
$A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$，求特征值和特征向量，并对角化。

<details><summary>解</summary>

特征方程：$\det(A - \lambda I) = (2-\lambda)^2 - 1 = 0 \Rightarrow \lambda = 1, 3$

$\lambda = 1$：$(A-I)\mathbf{x} = 0 \Rightarrow \mathbf{x} = (1,-1)^T$
$\lambda = 3$：$(A-3I)\mathbf{x} = 0 \Rightarrow \mathbf{x} = (1,1)^T$

$$A = Q\Lambda Q^{-1} = \frac{1}{2}\begin{pmatrix} 1 & 1 \\ -1 & 1 \end{pmatrix}\begin{pmatrix} 1 & 0 \\ 0 & 3 \end{pmatrix}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

（注：$Q$ 的列是特征向量，但需要归一化）

**ML 关联**：对称矩阵的谱分解 → PCA。
</details>

### Q6.2（正定矩阵）★
证明 $A$ 正定 $\iff$ 所有特征值 > 0。

<details><summary>解</summary>

$A$ 正定 $\iff \mathbf{x}^T A \mathbf{x} > 0, \forall \mathbf{x} \neq 0$。

对称矩阵可对角化 $A = Q\Lambda Q^T$。

$\mathbf{x}^T A \mathbf{x} = \mathbf{x}^T Q\Lambda Q^T \mathbf{x} = \mathbf{y}^T \Lambda \mathbf{y} = \sum \lambda_i y_i^2$

其中 $\mathbf{y} = Q^T \mathbf{x}$。$\sum \lambda_i y_i^2 > 0, \forall \mathbf{y} \neq 0 \iff \lambda_i > 0$。

**ML 关联**：Hessian 正定 → 局部最小值。
</details>

---

## 第 7 章 · SVD ★

### Q7.1（SVD 计算）
求 $A = \begin{pmatrix} 3 & 0 \\ 0 & -2 \end{pmatrix}$ 的 SVD。

<details><summary>解</summary>

$A^TA = \begin{pmatrix} 9 & 0 \\ 0 & 4 \end{pmatrix}$，特征值 $9, 4$。$\sigma_1 = 3, \sigma_2 = 2$。

$V = I$（$A^TA$ 的特征向量）

$U$：$A\mathbf{v}_1 = 3\mathbf{e}_1 \Rightarrow \mathbf{u}_1 = \mathbf{e}_1$
$A\mathbf{v}_2 = -2\mathbf{e}_2 \Rightarrow \mathbf{u}_2 = -\mathbf{e}_2$

$$A = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}\begin{pmatrix} 3 & 0 \\ 0 & 2 \end{pmatrix}\begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}$$
</details>

### Q7.2（Eckart-Young 定理）★
证明 SVD 给出最佳低秩近似：$\|A - A_k\|_F = \sigma_{k+1}$。

<details><summary>解（思路）</summary>

关键思路：对任意秩 $\leq k$ 的矩阵 $B$，利用 Weyl 不等式 $\sigma_{k+1}(A) \leq \sigma_{k+1}(B) + \|A-B\|_2$，由于 $\sigma_{k+1}(B) = 0$（$B$ 秩 $\leq k$），所以 $\|A-B\|_2 \geq \sigma_{k+1}$。

而 $A_k$ 恰好达到这个下界，所以是最优的。

**ML 关联**：PCA / 降维的理论基础。LoRA 的低秩近似。
</details>

---

## 第 8 章 · Linear Transformations

### Q8.1（基变换）
$T(\mathbf{x}) = A\mathbf{x}$，$A = \begin{pmatrix} 3 & 1 \\ 1 & 3 \end{pmatrix}$。用特征向量作为新基，表示 $T$。

<details><summary>解</summary>

特征向量 $\mathbf{q}_1 = (1,1)/\sqrt{2}, \mathbf{q}_2 = (1,-1)/\sqrt{2}$，特征值 $\lambda_1 = 4, \lambda_2 = 2$。

在新基下，$T$ 变成对角矩阵 $\begin{pmatrix} 4 & 0 \\ 0 & 2 \end{pmatrix}$。
</details>

---

## 第 9 章 · Graphs / Fourier / Markov

### Q9.1（马尔可夫矩阵）
$M = \begin{pmatrix} 0.9 & 0.2 \\ 0.1 & 0.8 \end{pmatrix}$。求稳态分布。

<details><summary>解</summary>

$M$ 每列和为 1 → 最大特征值 $\lambda_1 = 1$。

$M\mathbf{x} = \mathbf{x}$ → $\begin{pmatrix} 0.9 & 0.2 \\ 0.1 & 0.8 \end{pmatrix}\begin{pmatrix} x_1 \\ x_2 \end{pmatrix} = \begin{pmatrix} x_1 \\ x_2 \end{pmatrix}$

$0.1 x_1 = 0.2 x_2 \Rightarrow x_1 = 2 x_2$

稳态：$(2/3, 1/3)^T$。

**ML 关联**：PageRank 的核心。
</details>

---

## 综合大题

### Q-Final ★（PCA 实现）
给定矩阵 $X$（$n \times d$，$n$ 个样本，$d$ 维），写 Python 代码实现 PCA：
1. 中心化 $X$
2. 计算 SVD
3. 取前 $k$ 个主成分
4. 投影

<details><summary>解</summary>

```python
import numpy as np

def pca(X, k):
    # 1. 中心化
    X_centered = X - X.mean(axis=0)
    # 2. SVD
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    # 3. 前 k 个主成分
    V_k = Vt[:k].T       # (d, k)
    # 4. 投影
    X_pca = X_centered @ V_k  # (n, k)
    return X_pca, V_k

# 测试
np.random.seed(0)
X = np.random.randn(100, 5)  # 100 样本 × 5 维
X_pca, V = pca(X, k=2)
print(f"原始维度: {X.shape} → PCA 后: {X_pca.shape}")
print(f"解释方差比: {np.var(X_pca, axis=0) / np.var(X, axis=0).sum()}")
```
</details>
