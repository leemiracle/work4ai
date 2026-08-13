# Princeton MAT 217 · 习题集（证明导向，荣誉级）

> **来源**：Hoffman & Kunze + Axler + 自编（quotient/dual/Cayley-Hamilton 方向）

---

## 第 1 章 · 商空间与对偶 ★

### Q1.1（中等·商空间）
$V=\mathbb{R}^3$，$U=\{(x,y,z):x+y+z=0\}$。
(a) 求 $\dim(V/U)$。
(b) 描述 $V/U$ 的几何意义。

<details><summary>解</summary>

(a) $U$ 是平面，$\dim U=2$，$\dim(V/U)=3-2=1$。

(b) $V/U$ 的元素是"平行于 $U$ 的平面"（陪集）。两个向量在同一陪集 ⟺ 它们的差 $\in U$（即差的分量和为 0）。可取代表 $\mathbf{v}+U \mapsto x+y+z$（投影到 $(1,1,1)$ 方向）。$V/U\cong\mathbb{R}$。

> **ML 关联**：商空间 = "忽略 $U$ 方向后的信息"。
</details>

### Q1.2（中等·对偶基）
$V$ 的基 $e_1=(1,0),\ e_2=(1,2)$。求对偶基 $e^1,e^2\in V^*$。

<details><summary>解</summary>

$e^i(e_j)=\delta^i_j$。设 $e^1(\mathbf{x})=ax_1+bx_2$，$e^1(e_1)=a=1$，$e^1(e_2)=a+2b=0\Rightarrow b=-1/2$。故 $e^1=(1,-1/2)$。
$e^2(e_1)=c=0$，$e^2(e_2)=c+2d=1\Rightarrow d=1/2$。故 $e^2=(0,1/2)$。

验证：$\begin{pmatrix}1&0\\-1/2&1/2\end{pmatrix}\begin{pmatrix}1&1\\0&2\end{pmatrix}=I$ ✓。
</details>

---

## 第 2 章 · Cayley-Hamilton ★★

### Q2.1（证明·完整 Cayley-Hamilton）★
用伴随矩阵法证明 Cayley-Hamilton 定理（Hoffman & Kunze 风格）。

<details><summary>解（思路）</summary>

设 $p(\lambda)=\det(\lambda I-A)=\lambda^n+c_{n-1}\lambda^{n-1}+\cdots+c_0$。

由伴随矩阵性质：$\text{adj}(\lambda I-A)\cdot(\lambda I-A)=p(\lambda)I$。

$\text{adj}(\lambda I-A)$ 的每个元素是 $\lambda$ 的多项式（次数 $\leq n-1$），故可写 $B(\lambda)=B_0+\lambda B_1+\cdots+\lambda^{n-1}B_{n-1}$（矩阵系数）。

展开 $B(\lambda)(\lambda I-A)=p(\lambda)I$，比较 $\lambda^k$ 的系数，得一组递推关系。代入累加（$\sum$ 消去中间项）即得 $p(A)=A^n+c_{n-1}A^{n-1}+\cdots+c_0I=0$。

> **要点**：这是"纯代数"证明，不需三角化或复化，适用于任意域。
</details>

---

## 第 3 章 · 谱定理与正规算子

### Q3.1（中等·正规但不自伴）
$T=\begin{pmatrix}2&i\\-i&2\end{pmatrix}$（Hermite，正规）。验证复谱定理：特征值实、特征向量酉正交。

<details><summary>解</summary>

正规：$TT^*=\begin{pmatrix}2&i\\-i&2\end{pmatrix}\begin{pmatrix}2&i\\-i&2\end{pmatrix}^*...$ 验证 $TT^*=T^*T$ ✓（Hermite 必正规）。
特征值：$\det(T-\lambda I)=(2-\lambda)^2-1=0$，$\lambda=1,3$（全实，因 Hermite）。
特征向量 $(i,-1)/\sqrt2$ 与 $(i,1)/\sqrt2$，内积 $=i\cdot(-i)/2+(-1)(1)/2=0$ ✓ 酉正交。

> **要点**：复谱定理比实谱定理更一般（正规 ⊋ 自伴）。
</details>

---

## 第 4 章 · 双线性形式与二次型 ★

### Q4.1（中等·Sylvester 惯性）
$q(x,y)=x^2-4xy+y^2$。求惯性 $(p,q,r)$ 并判定类型。

<details><summary>解</summary>

矩阵 $A=\begin{pmatrix}1&-2\\-2&1\end{pmatrix}$。特征值：$(1-\lambda)^2-4=0$，$\lambda=-1,3$。
惯性 $(p,q,r)=(1,1,0)$ → **不定**（鞍点型）。

> **ML 关联**：这是鞍点处 Hessian 的典型惯性（优化中鞍点比局部极小更常见）。
</details>

### Q4.2（开放·合同变换）★
证明：合同变换 $A\mapsto P^TAP$（$P$ 可逆）保持对称矩阵的惯性（Sylvester 惯性律）。

<details><summary>解（思路）</summary>

关键：合同保持"正定性"和"符号"。用 Seymour 定理（惯性律）：任何合同对角化 $\text{diag}(+,\dots,+,-,\dots,-,0,\dots,0)$ 中 $+/−/0$ 个数不变。

反证法：若 $P^TAP$ 有更多正特征值，用插值（Courant-Fischer 极值）导出矛盾。详见 Hoffman & Kunze。

> **ML 关联**：换坐标系不改变 Hessian 的凸性/凹性 → 优化性质是坐标无关的。
</details>

---

## 第 5 章 · 典型群

### Q5.1（中等·正交群）
证明：$T\in\mathrm{O}(V)$（正交算子）⟺ $\|T\mathbf{v}\|=\|\mathbf{v}\|$（等距）。

<details><summary>解</summary>

(⟹) $T^*T=I$ ⟹ $\|T\mathbf{v}\|^2=\langle T\mathbf{v},T\mathbf{v}\rangle=\langle\mathbf{v},T^*T\mathbf{v}\rangle=\langle\mathbf{v},\mathbf{v}\rangle=\|\mathbf{v}\|^2$。

(⟸) 极化恒等式：$\langle T\mathbf{u},T\mathbf{v}\rangle$ 可由 $\|T(\mathbf{u}+\mathbf{v})\|^2,\|T\mathbf{u}\|^2,\|T\mathbf{v}\|^2$ 恢复 = $\langle\mathbf{u},\mathbf{v}\rangle$ → $T^*T=I$。

> **ML 关联**：正交权重 = 等距 → 不改变激活范数 → 防梯度爆炸/消失。
</details>

---

## 综合大题

### Q-Final（谱定理 + 二次型 + 优化·开放）★
设 Hessian $H=\begin{pmatrix}2&1&0\\1&2&1\\0&1&2\end{pmatrix}$（三对角，常见于链式结构）。
(a) 用谱定理求特征值。
(b) 求惯性，判定临界点类型。
(c) 若这是某损失函数的 Hessian，梯度下降会收敛到什么？

<details><summary>解</summary>

(a) 对称 → 实谱定理。特征值 $\lambda_k=2+2\cos\frac{k\pi}{4}$，$k=1,2,3$ → $\lambda=2-\sqrt2\approx0.586,\ 2,\ 2+\sqrt2\approx3.414$。

(b) 全正 → 惯性 $(3,0,0)$ → **正定** → 局部极小。

(c) 正定 Hessian → 凸（局部）→ 梯度下降收敛到该临界点（局部极小）。条件数 $\kappa=\frac{2+\sqrt2}{2-\sqrt2}\approx5.83$，收敛不太慢。

> 这是 MAT 217 把"谱定理 + 二次型"接到"优化"的招牌综合。
</details>
