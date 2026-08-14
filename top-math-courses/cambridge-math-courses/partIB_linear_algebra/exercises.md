# Cambridge Part IB Linear Algebra · 习题集（Tripos 风格）

> **来源**：Cambridge Past Tripos papers + Blyth & Robertson + 自编

---

## 第 1 章 · 特征值与三角化

### Q1.1（中等·三角化）
证明：任何复 $n\times n$ 矩阵相似于上三角矩阵。

<details><summary>解（归纳）</summary>

$n=1$ 平凡。$n>1$：复矩阵必有特征值 $\lambda_1$ 与特征向量 $\mathbf{v}_1$。以 $\mathbf{v}_1$ 为第 1 列构造可逆 $P_1$，则 $P_1^{-1}AP_1=\begin{pmatrix}\lambda_1&*\\0&B_1\end{pmatrix}$。$B_1$ 是 $(n-1)\times(n-1)$ 复矩阵，由归纳假设 $B_1=U_1T_1U_1^{-1}$（$T_1$ 上三角）。则 $P=P_1\begin{pmatrix}1&0\\0&U_1\end{pmatrix}$ 使 $P^{-1}AP$ 上三角。
</details>

---

## 第 2 章 · Jordan 标准型 ★★

### Q2.1（中等·求 Jordan 形式）
$A=\begin{pmatrix}2&1&0\\0&2&0\\0&0&2\end{pmatrix}$。求 Jordan 形式。

<details><summary>解</summary>

特征值 $\lambda=2$（三重）。$(A-2I)=\begin{pmatrix}0&1&0\\0&0&0\\0&0&0\end{pmatrix}$，秩 $1$ → $\ker(A-2I)$ 维 $=2$（几何重数 $2$）。
$(A-2I)^2=0$ → 广义特征空间 $=$ 全空间，最大 Jordan 块尺寸 $2$（因 $(A-2I)^2=0$ 但 $(A-2I)\neq0$）。
故 Jordan 形式 $=J_2(2)\oplus J_1(2)=\begin{pmatrix}2&1&0\\0&2&0\\0&0&2\end{pmatrix}$（已是对角分块）。

极小多项式 $m(x)=(x-2)^2$。
</details>

### Q2.2（开放·极小多项式与 Jordan）★
$A$ 的特征多项式 $=(x-1)^3(x-2)^2$，极小多项式 $=(x-1)^2(x-2)^2$。求 $A$ 的所有可能 Jordan 形式。

<details><summary>解</summary>

- $\lambda=1$：代数重数 3，极小多项式重数 2 → 最大块 $2\times2$。块分解：$J_2(1)\oplus J_1(1)$（唯一）。
- $\lambda=2$：代数重数 2，极小多项式重数 2 → 最大块 $2\times2$。块分解：$J_2(2)$（唯一）。

Jordan 形式 $=J_2(1)\oplus J_1(1)\oplus J_2(2)$（唯一确定）。

> **要点**：极小多项式 + 特征多项式 → 唯一确定 Jordan 形式（当块数少时）。
</details>

---

## 第 3 章 · 二次型与惯性

### Q3.1（中等·配方法）
用配方法（非特征值）将 $q=x^2+4xy+3y^2$ 化为标准形，求惯性。

<details><summary>解</summary>

$q=(x+2y)^2-4y^2+3y^2=(x+2y)^2-y^2$。
令 $u=x+2y,\ v=y$，则 $q=u^2-v^2$。惯性 $(p,q,r)=(1,1,0)$ → 不定（双曲型）。

验证：矩阵 $\begin{pmatrix}1&2\\2&3\end{pmatrix}$，特征值 $\frac{4\pm\sqrt{16+4}}2=2\pm\sqrt5$，一正一负 ✓。
</details>

### Q3.2（证明·Sylvester 惯性律）★
证明合同变换保持实对称矩阵的惯性。

<details><summary>解（思路）</summary>

设 $A$ 对称，$P$ 可逆，$\tilde A=P^TAP$。用 Courant-Fischer 极值：
$$\lambda_k^+(A)=\min_{\dim S=k}\max_{\mathbf{x}\in S}\frac{\mathbf{x}^TA\mathbf{x}}{\|\mathbf{x}\|^2}$$
合同 $A\mapsto P^TAP$ 等价于换变量 $\mathbf{y}=P^T\mathbf{x}$，子空间维数不变，正/负特征值个数不变。详见 Blyth & Robertson。
</details>

---

## 第 4 章 · 内积与谱定理

### Q4.1（中等·谱定理应用）
对称矩阵 $A=\begin{pmatrix}0&1\\1&0\end{pmatrix}$。用谱定理正交对角化，并解释几何。

<details><summary>解</summary>

特征值 $\lambda=\pm1$，特征向量 $(1,1)/\sqrt2,\ (1,-1)/\sqrt2$。$A=Q\Lambda Q^T$，$Q=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$。

几何：$A$ 是关于直线 $y=x$ 的**反射**（Hadamard 矩阵）。特征值 $+1$（反射轴上不变）和 $-1$（垂直翻转）。
</details>

---

## 第 5 章 · 对偶空间

### Q5.1（中等·零化子）
$V=\mathbb{R}^3$，$S=\text{span}\{(1,1,0),(0,1,1)\}$。求 $S^0$（零化子）的维数与一组基。

<details><summary>解</summary>

$\dim S=2$ → $\dim S^0=3-2=1$。
$f(\mathbf{x})=ax+by+cz\in S^0$ ⟺ $f(1,1,0)=a+b=0$ 且 $f(0,1,1)=b+c=0$ ⟺ $a=-b,\ c=-b$。取 $b=-1$：$f=-x+y-z$... 实际 $a=1,b=-1,c=1$：$f(x,y,z)=x-y+z$。
基：$\{x-y+z\}$（一个线性泛函）。

> **几何**：$S^0$ = "在 $S$ 上为零的泛函"，对应 $S$ 的法向量 $(1,-1,1)$。
</details>

---

## 综合大题

### Q-Final（Jordan + 谱定理综合·开放）★
$A=\begin{pmatrix}1&1&0\\-1&1&0\\0&0&2\end{pmatrix}$。
(a) 求特征值与 Jordan 形式。
(b) 判断 $e^{At}$ 的行为（衰减/振荡/爆炸）。
(c) 若 $A$ 是某动力系统的系数矩阵，原点稳定吗？

<details><summary>解</summary>

(a) 左上 $2\times2$ 块：$\det\begin{pmatrix}1-\lambda&1\\-1&1-\lambda\end{pmatrix}=(1-\lambda)^2+1=0$ → $\lambda=1\pm i$。右下 $\lambda=2$。
$\lambda=1\pm i$ 几何重数 1 = 代数重数 1（各一个）→ 可对角化部分。Jordan 形式 $=\text{diag}(J_1(1+i),J_1(1-i),J_1(2))$（全对角，无非对角1）。

(b) $e^{(1\pm i)t}=e^t(\cos t\pm i\sin t)$ → 振荡且 $e^t$ 增长。$e^{2t}$ 指数增长。

(c) $\text{Re}(\lambda)=1,2>0$ → **不稳定**（爆炸）。原点是排斥子。

> **ML 关联**：Neural ODE 若 Jacobian 有正实部特征值 → 训练发散。这正是 Part IB Jordan/谱理论的应用。
</details>
