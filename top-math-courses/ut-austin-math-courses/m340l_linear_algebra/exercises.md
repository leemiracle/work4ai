# UT Austin M340L · 习题集（应用线代，计算导向）

> **来源**：Lay 习题 + UT Austin 试题 + 自编（应用/数据科学方向）

---

## 第 1 章 · 线性方程组与矩阵

### Q1.1（基础·RREF）
将 $\begin{pmatrix}1&2&3|6\\2&5&3|14\\1&3&2|8\end{pmatrix}$ 化为 RREF 并求解。

<details><summary>解</summary>

$R_2-2R_1,\ R_3-R_1$：$\begin{pmatrix}1&2&3|6\\0&1&-3|2\\0&1&-1|2\end{pmatrix}$。$R_3-R_2$：$\begin{pmatrix}1&2&3|6\\0&1&-3|2\\0&0&2|0\end{pmatrix}$。$R_3/2$：$z=0$。回代 $y-3(0)=2$ → $y=2$。$x+2(2)+0=6$ → $x=2$。解 $(2,2,0)$。

> **ML 关联**：唯一解 = $\mathbf{b}\in C(A)$ 且 $N(A)=\{\mathbf{0}\}$。
</details>

### Q1.2（基础·列空间几何）★
$A=\begin{pmatrix}1&2\\2&4\\3&6\end{pmatrix}$。$C(A)$ 是什么？$\mathbf{b}=(1,2,4)^T$ 在 $C(A)$ 中吗？

<details><summary>解</summary>

列 2 = 2×列 1 → $C(A)=\text{span}\{(1,2,3)^T\}$（一条直线）。
$\mathbf{b}=(1,2,4)^T$：需 $c(1,2,3)^T=(1,2,4)^T$ → $c=1$ 但 $3c=3\neq4$ → **不在** $C(A)$。

> **直觉**：$A\mathbf{x}=\mathbf{b}$ 无解（Lay：b 不在列空间里）。
</details>

---

## 第 2 章 · 行列式

### Q2.1（基础）
$\det\begin{pmatrix}2&1&0\\1&3&1\\0&1&2\end{pmatrix}$？

<details><summary>解</summary>

$=2(6-1)-1(2-0)+0=10-2=8$。$\neq0$ → 可逆。

> **几何**：$|\det|=8$ = 变换体积缩放比。
</details>

---

## 第 3 章 · 向量空间与秩

### Q3.1（中等·四子空间）★
$A=\begin{pmatrix}1&2&0\\2&4&1\end{pmatrix}$（$2\times3$，秩 $r=2$）。
指出 $C(A), C(A^T), N(A), N(A^T)$ 各在 $\mathbb{R}^?$ 中，维数多少。

<details><summary>解</summary>

$A$ 是 $m=2,n=3$ 矩阵。列独立（列 2=2×列1，但列 3 引入新信息）→ $r=2$。
- $C(A)\subseteq\mathbb{R}^2$，$\dim=2$（满列秩）→ $C(A)=\mathbb{R}^2$。
- $N(A^T)\subseteq\mathbb{R}^2$，$\dim=m-r=0$（只有零向量）。
- $C(A^T)\subseteq\mathbb{R}^3$，$\dim=r=2$。
- $N(A)\subseteq\mathbb{R}^3$，$\dim=n-r=1$。$A\mathbf{x}=0$：$x_1+2x_2=0,\ 2x_1+4x_2+x_3=0$ → $x_3=0$... 令 $x_2=t$：$x_1=-2t$ → $N(A)=\text{span}\{(-2,1,0)^T\}$。

> **Lay 核心**：四子空间 + 秩定理 = 线代结构的全景图。
</details>

---

## 第 4 章 · 特征值与马尔可夫链

### Q4.1（中等·马尔可夫稳态）★
$M=\begin{pmatrix}0.7&0.4\\0.3&0.6\end{pmatrix}$（列随机）。求稳态分布。

<details><summary>解</summary>

列和 1 → $\lambda=1$ 是特征值。$M\mathbf{x}=\mathbf{x}$：$0.7x_1+0.4x_2=x_1$ → $0.4x_2=0.3x_1$ → $x_1=\frac43x_2$。归一化 $x_1+x_2=1$：$\frac43x_2+x_2=1$ → $x_2=\frac37,\ x_1=\frac47$。稳态 $(4/7,3/7)^T\approx(0.571,0.429)$。

> **ML 关联**：PageRank = 加阻尼的马尔可夫链。
</details>

### Q4.2（基础·对角化求幂）
$A=\begin{pmatrix}2&1\\0&3\end{pmatrix}$。求 $A^{10}$。

<details><summary>解</summary>

上三角 → 特征值 $2,3$。$A=PDP^{-1}$，$D=\text{diag}(2,3)$。
$A^{10}=PD^{10}P^{-1}$。$2^{10}=1024,\ 3^{10}=59049$。
$P=\begin{pmatrix}1&1\\0&1\end{pmatrix}$（特征向量 $(1,0)^T,(1,1)^T$）。
$A^{10}=\begin{pmatrix}1&1\\0&1\end{pmatrix}\begin{pmatrix}1024&0\\0&59049\end{pmatrix}\begin{pmatrix}1&-1\\0&1\end{pmatrix}=\begin{pmatrix}1024&59049-1024\\0&59049\end{pmatrix}=\begin{pmatrix}1024&58025\\0&59049\end{pmatrix}$。
</details>

---

## 第 5 章 · 正交与最小二乘 ★

### Q5.1（中等·最小二乘回归）★
数据点 $(1,2),(2,3),(3,5),(4,7)$。用最小二乘拟合 $y=\beta_0+\beta_1 t$。

<details><summary>解</summary>

$A=\begin{pmatrix}1&1\\1&2\\1&3\\1&4\end{pmatrix}$，$\mathbf{y}=(2,3,5,7)^T$。
$A^TA=\begin{pmatrix}4&10\\10&30\end{pmatrix}$，$A^T\mathbf{y}=(17,50)^T$。
$\det(A^TA)=120-100=20$。$\hat{\boldsymbol\beta}=\frac1{20}\begin{pmatrix}30&-10\\-10&4\end{pmatrix}\begin{pmatrix}17\\50\end{pmatrix}=\frac1{20}\begin{pmatrix}510-500\\-170+200\end{pmatrix}=\begin{pmatrix}0.5\\1.5\end{pmatrix}$。
$y=0.5+1.5t$。

> **ML 关联**：这就是 OLS 线性回归的闭式解——M340L 的招牌应用。
</details>

### Q5.2（基础·Gram-Schmidt）
对 $\mathbf{a}_1=(1,0,0),\mathbf{a}_2=(1,1,0)$ 执行 Gram-Schmidt 得正交基。

<details><summary>解</summary>

$\mathbf{q}_1=(1,0,0)$（已单位）。$\mathbf{v}_2=\mathbf{a}_2-\langle\mathbf{a}_2,\mathbf{q}_1\rangle\mathbf{q}_1=(1,1,0)-(1)(1,0,0)=(0,1,0)$。$\mathbf{q}_2=(0,1,0)$。

> **ML 关联**：QR 分解的基础 → 数值稳定的回归求解。
</details>

---

## 第 6 章 · 对称矩阵、SVD、PCA ★

### Q6.1（中等·正定判定）
判断 $A=\begin{pmatrix}2&-1\\-1&2\end{pmatrix}$ 是否正定（顺序主子式 + 特征值）。

<details><summary>解</summary>

法 1（顺序主子式）：$\Delta_1=2>0$，$\Delta_2=4-1=3>0$ → **正定**。
法 2（特征值）：$\lambda^2-4\lambda+3=0$ → $\lambda=1,3$ 全正 → **正定**。

> **ML 关联**：正定 = Hessian 凸 = 协方差合法。
</details>

### Q6.2（中等·SVD 基础）
$A=\begin{pmatrix}1&0\\0&3\\0&0\end{pmatrix}$。奇异值是什么？

<details><summary>解</summary>

$A^TA=\text{diag}(1,9)$ → 奇异值 $\sigma_1=3,\sigma_2=1$。$\|A\|_2=\sigma_{\max}=3$。

> **ML 关联**：最大奇异值 = 谱范数；LoRA 选截断秩 $r$ 时看奇异值"拐点"。
</details>

---

## 综合大题

### Q-Final（最小二乘 + SVD/PCA · 开放）★
数据矩阵 $X=\begin{pmatrix}1&1\\1&2\\1&3\end{pmatrix}$，标签 $\mathbf{y}=(2,4,5)^T$。
(a) 求最小二乘回归 $\hat{\boldsymbol\beta}$。
(b) 中心化后做 PCA，第一个主成分方向是什么？

<details><summary>解</summary>

(a) $A^TA=\begin{pmatrix}3&6\\6&14\end{pmatrix}$，$A^T\mathbf{y}=(11,25)^T$。$\det=42-36=6$。$\hat{\boldsymbol\beta}=\frac16\begin{pmatrix}14&-6\\-6&3\end{pmatrix}\begin{pmatrix}11\\25\end{pmatrix}=\frac16\begin{pmatrix}154-150\\-66+75\end{pmatrix}=\begin{pmatrix}2/3\\3/2\end{pmatrix}$。$y=\frac23+\frac32t$。

(b) 中心化：$\bar{t}=2$，列 $(−1,0,1)^T$。PCA 只一个方向 → 主成分沿 $(−1,0,1)^T/\sqrt2$（方差最大的方向）。

> **M340L 招牌**：把最小二乘（Ch6）和 PCA（Ch7）串起来——这是数据科学线代的两块基石。
</details>
