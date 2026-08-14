# Oxford Prelims M1 · 习题集（入门线代）

> **来源**：Oxford Prelims 试题 + Cameron 习题 + 自编

---

## 第 1 章 · 向量空间与线性方程组

### Q1.1（基础）
判断 $\{(x,y,z):x=y+z\}$ 是否为 $\mathbb{R}^3$ 的子空间。

<details><summary>解</summary>

含 $\mathbf{0}$（$0=0+0$）。加法：$(x_1,y_1,z_1)+(x_2,y_2,z_2)$，$x_1=y_1+z_1,x_2=y_2+z_2$，则 $x_1+x_2=(y_1+y_2)+(z_1+z_2)$ ✓。数乘类似 ✓。→ **是子空间**。
</details>

### Q1.2（基础·线性方程组几何）
$A=\begin{pmatrix}1&2\\3&6\end{pmatrix}$，$\mathbf{b}=(1,3)^T$ 与 $\mathbf{b}'=(1,4)^T$。哪个 $\mathbf{b}$ 在 $C(A)$ 中？

<details><summary>解</summary>

$C(A)=\text{span}\{(1,3)^T\}$（列 2 = 2×列 1）。
$\mathbf{b}=(1,3)^T=(1,3)^T$ ∈ $C(A)$ ✓（$x=(1,0)^T$）。
$\mathbf{b}'=(1,4)^T$：需 $c(1,3)^T=(1,4)^T$ ⟹ $c=1$ 但 $3c=3\neq4$ → 不在 $C(A)$。
</details>

---

## 第 2 章 · 维数定理

### Q2.1（中等）
$T:\mathbb{R}^4\to\mathbb{R}^3$，$\dim\ker T=2$。求 $\dim\text{im}\,T$。

<details><summary>解</summary>

维数定理：$4=\dim\ker T+\dim\text{im}\,T=2+\dim\text{im}\,T$ → $\dim\text{im}\,T=2$。
</details>

---

## 第 3 章 · 行列式

### Q3.1（基础）
$A=\begin{pmatrix}1&2&3\\0&1&4\\5&6&0\end{pmatrix}$。求 $\det A$。

<details><summary>解</summary>

按第一行展开：$1\cdot(1\cdot0-4\cdot6)-2\cdot(0\cdot0-4\cdot5)+3\cdot(0\cdot6-1\cdot5)=1(-24)-2(-20)+3(-5)=-24+40-15=1$。

> **几何**：$|\det|=1$ = 变换保体积。
</details>

---

## 第 4 章 · 特征值与对角化

### Q4.1（中等）
$A=\begin{pmatrix}3&1\\1&3\end{pmatrix}$。求特征值、特征向量，对角化，并算 $A^{10}$。

<details><summary>解</summary>

特征值 $\lambda=2,4$。特征向量 $(1,-1)/\sqrt2,\ (1,1)/\sqrt2$。$A=P\text{diag}(2,4)P^{-1}$。
$A^{10}=P\text{diag}(2^{10},4^{10})P^{-1}$。$2^{10}=1024$，$4^{10}=1048576$。

> **ML 关联**：对角化让矩阵幂从 $O(n^3\cdot k)$ 变 $O(n^3)$——RNN 长程依赖分析的基础。
</details>

### Q4.2（中等·PageRank）
$M=\begin{pmatrix}0.8&0.3\\0.2&0.7\end{pmatrix}$（列随机）。求稳态分布。

<details><summary>解</summary>

列和 1 → $\lambda_1=1$ 是特征值。$M\mathbf{x}=\mathbf{x}$：$0.8x_1+0.3x_2=x_1$ → $0.3x_2=0.2x_1$ → $x_1=1.5x_2$。归一化 $x_1+x_2=1$：$x_1=0.6,x_2=0.4$。稳态 $(0.6,0.4)^T$。
</details>

---

## 第 5 章 · 内积与最小二乘

### Q5.1（中等·最小二乘）★
点 $(0,1),(1,3),(2,5)$。用最小二乘拟合 $y=a+bt$。

<details><summary>解</summary>

$A=\begin{pmatrix}1&0\\1&1\\1&2\end{pmatrix}$，$\mathbf{b}=(1,3,5)^T$。$A^TA=\begin{pmatrix}3&3\\3&5\end{pmatrix}$，$A^T\mathbf{b}=(9,13)^T$。
$\hat{\mathbf{x}}=(A^TA)^{-1}A^T\mathbf{b}$：$\det(A^TA)=15-9=6$，逆 $=\frac16\begin{pmatrix}5&-3\\-3&3\end{pmatrix}$。$\hat{\mathbf{x}}=\frac16\begin{pmatrix}5&-3\\-3&3\end{pmatrix}\begin{pmatrix}9\\13\end{pmatrix}=\frac16\begin{pmatrix}45-39\\-27+39\end{pmatrix}=\begin{pmatrix}1\\2\end{pmatrix}$。
$y=1+2t$。

> **ML 关联**：这就是线性回归的闭式解。
</details>

### Q5.2（基础·Gram-Schmidt）
对 $\mathbf{a}_1=(1,1,0),\mathbf{a}_2=(1,0,1)$ 执行 Gram-Schmidt。

<details><summary>解</summary>

$\mathbf{q}_1=(1,1,0)/\sqrt2$。$\mathbf{v}_2=\mathbf{a}_2-\langle\mathbf{a}_2,\mathbf{q}_1\rangle\mathbf{q}_1=(1,0,1)-\frac1{\sqrt2}\cdot\frac1{\sqrt2}(1,1,0)=(1/2,-1/2,1)$。$\|\mathbf{v}_2\|=\sqrt{1/4+1/4+1}=\sqrt{3/2}$。$\mathbf{q}_2=(1/2,-1/2,1)/\sqrt{3/2}$。
</details>

---

## 综合大题

### Q-Final（对角化 + 矩阵幂·开放）★
斐波那契数列 $F_{n+1}=F_n+F_{n-1}$。用对角化求 $F_n$ 的闭式（Binet 公式）。

<details><summary>解</summary>

$\begin{pmatrix}F_{n+1}\\F_n\end{pmatrix}=\begin{pmatrix}1&1\\1&0\end{pmatrix}\begin{pmatrix}F_n\\F_{n-1}\end{pmatrix}$，故 $\begin{pmatrix}F_{n+1}\\F_n\end{pmatrix}=A^n\begin{pmatrix}F_1\\F_0\end{pmatrix}=A^n\begin{pmatrix}1\\0\end{pmatrix}$，$A=\begin{pmatrix}1&1\\1&0\end{pmatrix}$。

$A$ 特征值：$\lambda^2-\lambda-1=0$，$\lambda=\frac{1\pm\sqrt5}{2}=\varphi,\psi$（黄金比）。对角化 $A=P\text{diag}(\varphi,\psi)P^{-1}$，$A^n=P\text{diag}(\varphi^n,\psi^n)P^{-1}$。

$F_n=\frac{\varphi^n-\psi^n}{\sqrt5}$（Binet 公式）。

> **要点**：这是 Prelims M1"对角化 → 矩阵幂 → 递推闭式"的招牌应用。
</details>
