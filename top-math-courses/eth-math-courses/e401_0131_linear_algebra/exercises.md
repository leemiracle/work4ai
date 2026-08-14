# ETH 401-0131 · 习题集（工学院线代，应用导向）

> **来源**：Strang 习题 + ETH 试题 + 自编（条件数/QR/SVD 方向）

---

## 第 1 章 · 范数与条件数 ★

### Q1.1（中等·条件数）
$A=\begin{pmatrix}1&1\\1&1.001\end{pmatrix}$。
(a) 估 $\kappa(A)$ 量级。
(b) 解 $A\mathbf{x}=(2,2)^T$ 与 $A\mathbf{x}'=(2,2.001)^T$，观察扰动放大。

<details><summary>解</summary>

(a) 近似奇异，$\sigma_{\min}\approx0.0007$，$\sigma_{\max}\approx2$，$\kappa\approx3000$。

(b) $\mathbf{x}=(2,0)^T$（精确）。$\mathbf{x}'$：由 $x_1+x_2=2,\ x_1+1.001x_2=2.001$ → $0.001x_2=0.001$ → $x_2=1,\ x_1=1$。$\mathbf{x}'=(1,1)^T$。$\mathbf{b}$ 变 $5\times10^{-4}$，$\mathbf{x}$ 变 $O(1)$，放大 $\sim\kappa$。

> **ML 关联**：$\kappa$ 大 → 梯度下降需小学习率。
</details>

---

## 第 2 章 · QR 与最小二乘 ★

### Q2.1（中等·QR 求最小二乘）
$A=\begin{pmatrix}1&1\\1&0\\0&1\end{pmatrix}$，$\mathbf{b}=(2,1,1)^T$。用 QR 求最小二乘解。

<details><summary>解</summary>

$Q=\begin{pmatrix}1/\sqrt2&1/\sqrt6\\1/\sqrt2&-1/\sqrt6\\0&2/\sqrt6\end{pmatrix}$，$R=\begin{pmatrix}\sqrt2&1/\sqrt2\\0&\sqrt{3/2}\end{pmatrix}$（Gram-Schmidt）。
$Q^T\mathbf{b}=(3/\sqrt2,1/\sqrt6)^T$。解 $R\hat{\mathbf{x}}=Q^T\mathbf{b}$：$\sqrt{3/2}x_2=1/\sqrt6$ → $x_2=1/3$；$\sqrt2x_1+\frac1{\sqrt2}\cdot\frac13=\frac3{\sqrt2}$ → $x_1=4/3$。$\hat{\mathbf{x}}=(4/3,1/3)^T$。

> **要点**：QR 避免了 $\kappa(A^TA)=\kappa(A)^2$ 的条件数平方问题。
</details>

---

## 第 3 章 · 特征值与振动

### Q3.1（中等·广义特征值）
弹簧-质量系统 $K=\begin{pmatrix}2&-1\\-1&2\end{pmatrix}$，$M=I$。求固有频率 $\omega_i$。

<details><summary>解</summary>

$K\mathbf{x}=\omega^2\mathbf{x}$，即 $K$ 的特征值 $=\omega^2$。$\lambda=1,3$ → $\omega_1=1,\ \omega_2=\sqrt3$。振型：$(1,1)/\sqrt2$（同相），$(1,-1)/\sqrt2$（反相）。

> **ETH 工程传统**：特征值 = 振动频率，共振 = 外力频率匹配。
</details>

---

## 第 4 章 · SVD 与低秩 ★

### Q4.1（中等·SVD 计算）
$A=\begin{pmatrix}3&0\\0&2\\0&0\end{pmatrix}$。求 SVD。

<details><summary>解</summary>

$A^TA=\text{diag}(9,4)$ → $\sigma_1=3,\sigma_2=2$，$V=I$。$u_1=Av_1/\sigma_1=(1,0,0)^T$，$u_2=(0,1,0)^T$，$u_3=(0,0,1)^T$（补全）。
$A=\begin{pmatrix}1&0&0\\0&1&0\\0&0&1\end{pmatrix}\begin{pmatrix}3&0\\0&2\\0&0\end{pmatrix}\begin{pmatrix}1&0\\0&1\end{pmatrix}$。
</details>

### Q4.2（开放·LoRA 压缩）★
权重矩阵 $W\in\mathbb{R}^{d\times d}$，$d=4096$。奇异值谱 $\sigma_1\geq\cdots$ 且 $\sigma_{17}$ 后骤降。
(a) 用 LoRA 秩 $r=16$，参数压缩比？
(b) Eckart-Young 保证的近似误差？

<details><summary>解</summary>

(a) 全量 $d^2=16{,}777{,}216$。LoRA $r(d+d)=16\times8192=131{,}072$。压缩 $128\times$。

(b) Eckart-Young：$\|W-W_{16}\|_F=\sqrt{\sigma_{17}^2+\cdots+\sigma_d^2}\approx\sigma_{17}$（因后续骤降）。

> **ML 关联**：这正是 LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）的数学根基。
</details>

---

## 第 5 章 · 谱定理

### Q5.1（中等）
$A=\begin{pmatrix}4&1\\1&4\end{pmatrix}$。谱分解，求 $A^{1/2}$（矩阵平方根）。

<details><summary>解</summary>

$\lambda=3,5$，$Q=\frac1{\sqrt2}\begin{pmatrix}1&1\\-1&1\end{pmatrix}$。$A=Q\text{diag}(3,5)Q^T$。
$A^{1/2}=Q\text{diag}(\sqrt3,\sqrt5)Q^T$。验证 $(A^{1/2})^2=A$。

> **ML 关联**：协方差 $\Sigma^{1/2}$ 用于生成相关样本 $x=\Sigma^{1/2}z$。
</details>

---

## 综合大题

### Q-Final（SVD 图像压缩·开放）★
一张 $64\times64$ 灰度图 $I$。
(a) 用 SVD 秩-$k$ 近似 $I_k=\sum_{i=1}^k\sigma_iu_iv_i^T$，存储从 $64^2$ 降到 $k(64+64+1)$。
(b) $k=8$ 时压缩比？若 $\sigma_9/\sigma_1=0.05$，相对误差约多少？

<details><summary>解</summary>

(a) 原存储 $4096$。$k=8$：$8\times129=1032$。压缩 $4096/1032\approx4\times$。

(b) 相对误差 $\approx\sqrt{\sigma_9^2+\cdots+\sigma_{64}^2}/\|I\|_F\leq\sigma_9/\sigma_1\approx0.05$... 若后续奇异值接近 $\sigma_9$，误差约 $5\%$；实际因骤降，更低。

> **ETH 应用**：SVD 图像/信号压缩是 ETH 工程线代的招牌应用，直接通向 LoRA 的权重压缩。
</details>
