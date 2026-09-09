# Stanford MATH 113 · 习题集（理论 + 应用导向）

> **来源**：Axler LADR + Strang 习题 + 自编（Jordan/Cayley-Hamilton/ODE 方向）

---

## 第 1 章 · 对角化与特征值

### Q1.1（基础）
$A=\begin{pmatrix}4&1\\2&3\end{pmatrix}$。求特征值、特征向量，判断是否可对角化。

<details><summary>解</summary>

$\det(A-\lambda I)=(4-\lambda)(3-\lambda)-2=\lambda^2-7\lambda+10=0$，$\lambda=2,5$。
两个不同特征值 → 可对角化。$\lambda=2:(2,−2)^T/\sqrt2$；$\lambda=5:(1,1)^T/\sqrt2$。
$A=PDP^{-1}$，$D=\text{diag}(2,5)$。
</details>

---

## 第 2 章 · Cayley-Hamilton ★

### Q2.1（中等·证明 Cayley-Hamilton 用途）
设 $A=\begin{pmatrix}1&2\\3&4\end{pmatrix}$。
(a) 求 $A$ 的特征多项式 $p(\lambda)$。
(b) 验证 $p(A)=0$。
(c) 用 Cayley-Hamilton 求 $A^{-1}$（不用直接求逆）。

<details><summary>解</summary>

(a) $p(\lambda)=\lambda^2-5\lambda-2$（$\text{tr}=5$，$\det=-2$）。

(b) $A^2=\begin{pmatrix}7&10\\15&22\end{pmatrix}$，$p(A)=A^2-5A-2I=\begin{pmatrix}7-5-2&10-10\\15-15&22-20-2\end{pmatrix}=0$ ✓

(c) $p(A)=0\Rightarrow A^2-5A-2I=0\Rightarrow A(A-5I)=2I\Rightarrow A^{-1}=\frac12(A-5I)=\frac12\begin{pmatrix}-4&2\\3&-1\end{pmatrix}=\begin{pmatrix}-2&1\\1.5&-0.5\end{pmatrix}$。

> **要点**：Cayley-Hamilton 把求逆变成"矩阵的低次多项式"。
</details>

---

## 第 3 章 · Jordan 标准型 ★★

### Q3.1（中等·求 Jordan 形式）
$A=\begin{pmatrix}2&1&0\\0&2&1\\0&0&2\end{pmatrix}$。
(a) $A$ 的特征值与几何重数？
(b) $A$ 的 Jordan 形式是什么？能否对角化？

<details><summary>解</summary>

(a) 特征值 $\lambda=2$（三重）。$(A-2I)$ 的秩 $=2$ → 零空间维数（几何重数）$=3-2=1<$ 代数重数 $3$。

(b) 几何重数 $1$ → 只有 1 个 Jordan 块 → $J=J_3(2)=A$ 本身（已是 Jordan 形式）。**不可对角化**。
</details>

### Q3.2（开放·Jordan 块的幂）★
对 $m\times m$ Jordan 块 $J_m(\lambda)$，证明 $J_m(\lambda)^k$ 的 $(i,j)$ 元含 $\binom{k}{j-i}\lambda^{k-(j-i)}$（$j\geq i$）。

<details><summary>解（思路）</summary>

$J_m(\lambda)=\lambda I+N$，$N$ 是上移位幂零矩阵（$N^m=0$）。二项展开：
$$J^k=(\lambda I+N)^k=\sum_{j=0}^{m-1}\binom{k}{j}\lambda^{k-j}N^j$$
$N^j$ 的 $(i,i+j)$ 元 $=1$，其余 $0$。故 $(i,i+r)$ 元 $=\binom{k}{r}\lambda^{k-r}$。

> **ML 关联**：这解释了 RNN 中 $W^k$ 为何随 $k$ 呈多项式-指数混合衰减/增长。
</details>

---

## 第 4 章 · 谱定理与正定

### Q4.1（中等·正定判定）
判断 $A=\begin{pmatrix}2&-1\\-1&2\end{pmatrix}$ 是否正定。用两种方法。

<details><summary>解</summary>

法 1（特征值）：$\lambda=1,3$ 全 $>0$ → 正定。
法 2（顺序主子式）：$\Delta_1=2>0$，$\Delta_2=\det A=3>0$ → 正定。

> **ML 关联**：$A$ 是常见的高斯过程核（RBF 变体），正定保证良定义。
</details>

---

## 第 5 章 · 矩阵指数与 ODE ★

### Q5.1（中等·用 Jordan 求 $e^{At}$）
$A=\begin{pmatrix}0&1\\-1&0\end{pmatrix}$（旋转矩阵）。求 $e^{At}$ 并解释几何意义。

<details><summary>解</summary>

特征值 $\lambda=\pm i$。$A$ 可对角化 $A=P\text{diag}(i,-i)P^{-1}$。
$e^{At}=P\text{diag}(e^{it},e^{-it})P^{-1}=\begin{pmatrix}\cos t&\sin t\\-\sin t&\cos t\end{pmatrix}$。

**几何**：$e^{At}$ 是旋转矩阵 → 解 $\mathbf{x}(t)=e^{At}\mathbf{x}_0$ 是匀速圆周运动（特征值纯虚 = 振荡，不衰减不爆炸）。

> **ML 关联**：Neural ODE 中纯虚特征值 = 振荡模式（周期性动力学）。
</details>

### Q5.2（开放·稳定性）★
动力系统 $\dot{\mathbf{x}}=A\mathbf{x}$，$A=\begin{pmatrix}-1&0&0\\0&0.5&1\\0&0&0.5\end{pmatrix}$。判断原点稳定性。

<details><summary>解</summary>

特征值：$-1$（来自左上块），$0.5$（二重，来自 $2\times2$ Jordan 块 $J_2(0.5)$）。
$\text{Re}(\lambda)=0.5>0$ → 原点**不稳定**（爆炸）。即使有 $-1$ 方向衰减，正特征值方向指数增长主导。

Jordan 块 $J_2(0.5)$ 还带来 $te^{0.5t}$ 的多项式增长项，加剧不稳定。
</details>

---

## 综合大题

### Q-Final（Jordan 形式 + Neural ODE·开放）★
某 Neural ODE 在平衡点线性化为 $\dot{\mathbf{h}}=J\mathbf{h}$，$J=\begin{pmatrix}-0.3&0.1\\-0.1&-0.3\end{pmatrix}$。
(a) 求 $J$ 的特征值，判断平衡点稳定性。
(b) 写 $e^{Jt}$ 的表达式。
(c) 解释这对训练（梯度反向传播）意味着什么。

<details><summary>解</summary>

(a) $\text{tr}=-0.6$，$\det=0.09+0.01=0.10$。$\lambda=\frac{-0.6\pm\sqrt{0.36-0.40}}2=-0.3\pm0.1i$。$\text{Re}(\lambda)=-0.3<0$ → **渐近稳定**（衰减振荡）。

(b) $J=-0.3I+0.1\begin{pmatrix}0&1\\-1&0\end{pmatrix}$。$e^{Jt}=e^{-0.3t}\begin{pmatrix}\cos(0.1t)&\sin(0.1t)\\-\sin(0.1t)&\cos(0.1t)\end{pmatrix}$。

(c) 衰减振荡 → 梯度反向传播时信号以 $e^{-0.3t}$ 衰减（稳定，不会爆炸），但会振荡。这意味着该 ODE block 训练稳定，适合深层堆叠。条件数小 → 收敛快。

> 这是 Stanford 113 把"线代"接到"深度学习动力学"的招牌应用。
</details>
