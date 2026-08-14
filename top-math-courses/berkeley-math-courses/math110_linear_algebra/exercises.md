# Berkeley MATH 110 · 习题集（Axler 风格，证明导向）

> **来源**：Axler LADR 4th ed 习题 + 自编证明题
> **风格**：以**证明**为主（区别于 MIT 18.06 的计算题）。提示用 Axler 的"不变子空间 + 内积"路线，不用行列式。

---

## 第 1 章 · Vector Spaces

### Q1.1（基础·证明子空间）
设 $U=\{(x,2x,3x):x\in\mathbb{R}\}\subseteq\mathbb{R}^3$。证明 $U$ 是 $\mathbb{R}^3$ 的子空间，并求 $\dim U$。

<details><summary>解</summary>

需验证：(1) $\mathbf{0}\in U$（取 $x=0$）；(2) 对加法封闭：$(x,2x,3x)+(y,2y,3y)=(x+y,2(x+y),3(x+y))\in U$；(3) 对标量乘封闭：$c(x,2x,3x)=(cx,2cx,3cx)\in U$。

$\dim U=1$，基为 $\{(1,2,3)\}$。

> **Axler 风格**：用定义直接验证三条，而非算行列式。
</details>

### Q1.2（和 vs 直和）
设 $U=\{(x,0)\},\ W=\{(0,y)\},\ U'=\{(x,x)\}\subseteq\mathbb{R}^2$。
(a) $U+W=\mathbb{R}^2$ 吗？是直和吗？
(b) $U+U'=\mathbb{R}^2$ 吗？是直和吗？

<details><summary>解</summary>

(a) $U+W=\mathbb{R}^2$ ✓。且 $U\cap W=\{0\}$ → **直和**（Axler 1.40）。

(b) $U+U'=\mathbb{R}^2$ ✓（$(x,y)=(x-y,0)+(y,y)$）。但 $U\cap U'=\{(0,0)\}$ → 也是直和。

**Axler 直和判定**（1.40）：$U+W$ 是直和 ⟺ 每个 $v\in U+W$ 的分解唯一 ⟺ $U\cap W=\{0\}$。
</details>

---

## 第 3 章 · Linear Maps & 维数定理

### Q3.1（维数定理·中等）
设 $T:\mathbb{R}^5\to\mathbb{R}^3$ 是线性映射，$\dim\text{null}\,T=2$。求 $\dim\text{range}\,T$，并解释几何意义。

<details><summary>解</summary>

维数定理（Axler 3.22）：$\dim V=\dim\text{null}\,T+\dim\text{range}\,T$。
$5=2+\dim\text{range}\,T\Rightarrow\dim\text{range}\,T=3$。

几何：5 维输入经 $T$ 映射，2 维被"压扁"到零（零空间），3 维"存活"成像。

> **ML 关联**：autoencoder 的 encoder 就是这样的 $T$（降维）。
</details>

### Q3.2（投影是线性映射·中等）
设 $U\subseteq V$ 是子空间，$P_U$ 是正交投影。证明 $P_U$ 是线性映射且 $P_U^2=P_U$。

<details><summary>解</summary>

正交分解 $v=u+w$（$u\in U,w\in U^\perp$）唯一。$P_Uv=u$。
- 线性：$(v_1+v_2)=(u_1+u_2)+(w_1+w_2)$，且 $u_1+u_2\in U,\ w_1+w_2\in U^\perp$ → $P_U(v_1+v_2)=u_1+u_2=P_Uv_1+P_Uv_2$。
- $P_U^2=P_U$：$P_Uv=u\in U$，故 $P_Uu=u$（因 $u$ 已在 $U$ 中，分解为 $u+0$）→ $P_U^2v=P_Uu=u=P_Uv$。

> **ML 关联**：$P^2=P$（幂等）是投影的本质；最小二乘 $\hat{x}$ 满足 $A\hat{x}=P_{C(A)}b$。
</details>

---

## 第 5 章 · 不变子空间与特征值 ★

### Q5.1（特征值的 Axler 定义·中等）
设 $T:\mathbb{C}^2\to\mathbb{C}^2$，$T(x,y)=(3x+2y,\,-2x-y)$。不用行列式，求 $T$ 的特征值与特征向量。

<details><summary>解（Axler 路线）</summary>

取 $v=(1,0)$，考虑 $v,Tv,T^2v$：
$Tv=(3,-2)$，$T^2v=T(3,-2)=(3\cdot3+2\cdot(-2),\,-2\cdot3-1\cdot(-2))=(5,-4)$。

$\{v,Tv,T^2v\}$ 在 $\mathbb{C}^2$ 中必相关。找 $aI+bT+T^2=0$（最小多项式）：
计算 $T^2$：$T^2(x,y)=(5x+4y,-4x-3y)$。$T^2-(2I)$：$(5x+4y-2x,\,-4x-3y-2y)=(3x+4y,-4x-5y)$... 

更简洁：直接验证 $T^2-2T+I=0$？$T^2v-T(2v)+v$... 让我们用 $\text{tr}=3+(-1)=2$，$\det$（暂不用）...

**Axler 方法**：$Tv=\lambda v \Rightarrow (3-\lambda)x+2y=0,\ -2x+(-1-\lambda)y=0$ 有非零解。这是不变子空间 $W=\text{span}(v)$ 存在性。

解 $\lambda$：$(3-\lambda)(-1-\lambda)+4=0\Rightarrow\lambda^2-2\lambda+1=0\Rightarrow\lambda=1$（二重）。

$T-I$：$(2x+2y,-2x-2y)$，零空间 $x=-y$，特征向量 $(1,-1)$。几何重数 $=1<$ 代数 $2$ → 不可对角化（Jordan 块）。

> **要点**：Axler 不写"行列式 = 0"，而是问"哪个 1 维子空间不变"。
</details>

### Q5.2（不变子空间·开放）★
证明：若 $\dim V$ 是奇数，则 $\mathbb{R}$ 上每个算子 $T\in\mathcal{L}(V)$ 有 1 维或 2 维不变子空间。

<details><summary>解（思路）</summary>

取 $v\neq0$，$v,Tv,T^2v$ 张成 $W=\text{span}(v,Tv,T^2v,\dots)$。$\dim W\leq\dim V$。

若存在 $Tv=\lambda v$（1 维不变子空间）则完成。否则考虑最小多项式 $p$ 在 $\mathbb{R}$ 上分解为一次/二次因子（实系数多项式）。奇数维 → $T$ 的特征多项式（或最小多项式）必有奇次 → 必有实根 → 1 维不变子空间。

> **ML 关联**：高维算子"必有小不变子空间"——这正是 LoRA 假设"高维权重更新集中在低维子空间"的理论影子。
</details>

---

## 第 6-7 章 · 内积与谱定理 ★★

### Q7.1（自伴算子特征值实·证明）★★
证明：若 $T$ 自伴（$T=T^*$），则 $T$ 的特征值全是实数。（不用行列式！）

<details><summary>解</summary>

设 $Tv=\lambda v,\ v\neq0$。$\lambda\langle v,v\rangle=\langle Tv,v\rangle$。

因 $T$ 自伴：$\langle Tv,v\rangle=\langle v,Tv\rangle=\langle v,\lambda v\rangle=\bar\lambda\langle v,v\rangle$。

故 $\lambda\langle v,v\rangle=\bar\lambda\langle v,v\rangle$。因 $\langle v,v\rangle>0$，得 $\lambda=\bar\lambda$，即 $\lambda\in\mathbb{R}$。

> **ML 关联**：协方差矩阵 $\Sigma$ 对称（自伴）→ 特征值（方差）全实正 → PCA 良定义。Axler 这一步是 PCA 可行性的数学根基。
</details>

### Q7.2（正定 ⟺ 特征值 > 0·证明）★
设 $T$ 自伴。证明：$T$ 正定（$\langle Tv,v\rangle>0,\ \forall v\neq0$）⟺ 所有特征值 $>0$。

<details><summary>解</summary>

(⟸) 谱定理：有标准正交特征基 $e_i$，$Te_i=\lambda_ie_i$，$\lambda_i>0$。$v=\sum c_ie_i$，$\langle Tv,v\rangle=\sum\lambda_i|c_i|^2>0$（某 $c_i\neq0$）。

(⟹) 若 $Te_i=\lambda_ie_i$，取 $v=e_i$：$\langle Te_i,e_i\rangle=\lambda_i>0$。

> **ML 关联**：Hessian 正定 ⟺ 局部极小；协方差矩阵半正定（$\geq0$）。
</details>

### Q7.3（奇异值的 Axler 定义·计算）
$A=\begin{pmatrix}1&2\\0&1\\1&0\end{pmatrix}$。用 Axler 的定义（$\sigma_i=\sqrt{\lambda_i(A^TA)}$ 的特征值）求奇异值，并与 SVD 验证。

<details><summary>解</summary>

$A^TA=\begin{pmatrix}2&2\\2&5\end{pmatrix}$。特征值：$\det(A^TA-\lambda I)=(2-\lambda)(5-\lambda)-4=\lambda^2-7\lambda+6=0$，$\lambda=1,6$。

奇异值 $\sigma_1=\sqrt6\approx2.449,\ \sigma_2=1$。

验证（numpy `np.linalg.svd`）一致 ✓。
</details>

---

## 第 8 章 · 复算子结构

### Q8.1（上三角表示·中等）
证明（Axler 8.19）：复向量空间上每个算子有上三角矩阵表示。

<details><summary>解（思路）</summary>

对 $\dim V=n$ 归纳。$n=1$ 平凡。$n>1$：由 5.21，$T$ 有特征值 $\lambda$ 与特征向量 $v_1$。令 $U=\text{span}(v_1)$，则 $U$ 是 $T$ 的不变子空间。商空间 $V/U$ 维数 $n-1$，诱导算子 $\tilde T$ 有上三角表示（归纳假设）。提升回 $V$ 得上三角矩阵。

> **意义**：这是 Jordan 形式的基础。上三角矩阵的对角元 = 特征值。
</details>

---

## 综合大题

### Q-Final（谱定理应用：PCA 的存在性·开放）★
设 $\Sigma$ 是 $n\times n$ 实对称半正定矩阵（样本协方差）。
(a) 用**实谱定理**证明：存在标准正交矩阵 $Q$ 使 $\Sigma=Q\Lambda Q^T$，$\Lambda$ 对角且元素 $\geq0$。
(b) 解释为何这保证了 PCA 永远可行（主轴存在、正交、方差非负）。
(c) 写 Python 验证。

<details><summary>解</summary>

(a) $\Sigma$ 实对称 → 自伴 → 实谱定理（Axler 7.29）：有标准正交特征基 $e_1,\dots,e_n$，$Q=[e_i]$ 正交，$\Sigma=Q\Lambda Q^T$。$\Sigma$ 半正定 → 特征值 $\geq0$（Q7.2）。

(b) PCA 需要的三个性质——主轴正交（$Q$ 正交）、方差非负（$\Lambda\geq0$）、完全分解（$\Sigma=Q\Lambda Q^T$）——**全由谱定理一次性保证**。没有谱定理，PCA 可能"失败"（无实特征值/非正交）。Axler 让我们确信这不会发生。

(c)
```python
import numpy as np
np.random.seed(0)
X = np.random.randn(100, 5)
Sigma = np.cov(X, rowvar=False)          # 协方差, 对称半正定
L, Q = np.linalg.eigh(Sigma)             # eigh 返回 (特征值, 特征向量)!
print("Q 正交?", np.allclose(Q @ Q.T, np.eye(5)))     # True
print("特征值 >= 0?", np.all(L >= -1e-15))            # True
print("重建 Sigma = QΛQᵀ?", np.allclose(Q @ np.diag(L) @ Q.T, Sigma))  # True
```
</details>
