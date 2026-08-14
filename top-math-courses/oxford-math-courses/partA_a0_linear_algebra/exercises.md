# Oxford Part A A0 · 习题集（线代深化，证明导向）

> **来源**：Oxford Part A 试题 + 自编（对偶/Jordan/二次型/谱定理）

---

## 第 1 章 · 对偶空间 ★

### Q1.1（中等·零化子）
$V=\mathbb{R}^3$，$U=\text{span}\{(1,0,1),(0,1,1)\}$。求 $U^0$ 的维数与基。

<details><summary>解</summary>

$\dim U=2$ → $\dim U^0=3-2=1$。$f(x,y,z)=ax+by+cz\in U^0$ ⟺ $f(1,0,1)=a+c=0$，$f(0,1,1)=b+c=0$ → $a=b=-c$。取 $c=-1$：$f=x+y-z$。基 $\{x+y-z\}$（对应法向量 $(1,1,-1)$）。
</details>

### Q1.2（中等·对偶映射）
$T:\mathbb{R}^2\to\mathbb{R}^2$，$T(x,y)=(x+y,x)$。标准基下 $T$ 的矩阵 $A$。求对偶映射 $T^*$ 的矩阵（标准对偶基下）。

<details><summary>解</summary>

$A=\begin{pmatrix}1&1\\1&0\end{pmatrix}$（列 = $Te_1=(1,1),Te_2=(1,0)$）。对偶映射 $T^*$ 在标准对偶基下的矩阵 $=A^T=\begin{pmatrix}1&1\\1&0\end{pmatrix}$（$A$ 对称，故相同）。

> **要点**：代数对偶映射的矩阵 = 原矩阵的转置。
</details>

---

## 第 2 章 · Jordan 标准型 ★★

### Q2.1（中等·Jordan 形式）
$A=\begin{pmatrix}5&1&0\\0&5&1\\0&0&5\end{pmatrix}$。求 Jordan 形式与极小多项式。

<details><summary>解</summary>

$\lambda=5$（三重）。$(A-5I)=\begin{pmatrix}0&1&0\\0&0&1\\0&0&0\end{pmatrix}$，秩 2 → 几何重数 1。$(A-5I)^2\neq0$，$(A-5I)^3=0$ → 最大块 $3\times3$。Jordan 形式 $=J_3(5)=A$ 本身。极小多项式 $m(x)=(x-5)^3$。
</details>

### Q2.2（开放·极小多项式判定）★
$A$ 特征多项式 $(x-2)^2(x-3)^2$，极小多项式 $(x-2)(x-3)^2$。求 Jordan 形式。

<details><summary>解</summary>

- $\lambda=2$：极小多项式重数 1 → 块全 $1\times1$ → $J_1(2)\oplus J_1(2)$（可对角化部分）。
- $\lambda=3$：极小多项式重数 2 → 最大块 $2\times2$，代数重数 2 → $J_2(3)$。

Jordan 形式 $=J_1(2)\oplus J_1(2)\oplus J_2(3)=\text{diag}(2,2,\begin{pmatrix}3&1\\0&3\end{pmatrix})$。
</details>

---

## 第 3 章 · 双线性形式与二次型 ★

### Q3.1（中等·配方法）
$q=2x^2+6xy+2y^2$。用配方法化标准形，求惯性。

<details><summary>解</summary>

$q=2(x^2+3xy+y^2)=2[(x+\frac32y)^2-\frac94y^2+y^2]=2(x+\frac32y)^2-\frac12y^2$。
令 $u=x+\frac32y,\ v=y$：$q=2u^2-\frac12v^2$。惯性 $(1,1,0)$ → 不定。
</details>

### Q3.2（中等·正定判定）
判断 $A=\begin{pmatrix}3&1\\1&3\end{pmatrix}$ 的正定性（用惯性 + 特征值两种方法）。

<details><summary>解</summary>

法 1（特征值）：$\lambda=2,4$ 全正 → 正定。
法 2（顺序主子式）：$\Delta_1=3>0$，$\Delta_2=9-1=8>0$ → 正定。
</details>

---

## 第 4 章 · 谱定理

### Q4.1（证明·自伴特征值实）★
证明自伴（实对称）算子的特征值全实。

<details><summary>解</summary>

$Tv=\lambda v$。$\lambda\langle v,v\rangle=\langle Tv,v\rangle=\langle v,Tv\rangle$（$T$ 自伴）$=\langle v,\lambda v\rangle=\bar\lambda\langle v,v\rangle$。故 $\lambda=\bar\lambda$（实）。

> **ML 关联**：协方差对称 → 特征值（方差）实正 → PCA 良定义。
</details>

### Q4.2（中等·谱分解应用）
对称矩阵 $A=\begin{pmatrix}1&2\\2&1\end{pmatrix}$。谱分解 $A=Q\Lambda Q^T$，并用它求 $A^{-1}$。

<details><summary>解</summary>

特征值 $\lambda=-1,3$，$Q=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$。$A=Q\text{diag}(-1,3)Q^T$。
$A^{-1}=Q\text{diag}(-1,\frac13)Q^T=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}\begin{pmatrix}-1&0\\0&1/3\end{pmatrix}\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}=\frac16\begin{pmatrix}-3+1&-3-1\\-3-1&-3+1\end{pmatrix}$... 计算：$=\begin{pmatrix}-1/3&2/3\\2/3&-1/3\end{pmatrix}$... 验证 $\det A=1-4=-3$，$A^{-1}=\frac1{-3}\begin{pmatrix}1&-2\\-2&1\end{pmatrix}=\begin{pmatrix}-1/3&2/3\\2/3&-1/3\end{pmatrix}$ ✓。

> **要点**：谱分解让求逆 = 特征值取倒数（对角化优势）。
</details>

---

## 综合大题

### Q-Final（谱定理 + 正定 + 高斯采样·开放）★
协方差矩阵 $\Sigma=\begin{pmatrix}4&2\\2&3\end{pmatrix}$。
(a) 谱分解 $\Sigma=Q\Lambda Q^T$。
(b) 求 Cholesky $\Sigma=LL^T$。
(c) 如何用 $L$ 生成服从 $\mathcal{N}(\mathbf{0},\Sigma)$ 的样本？

<details><summary>解</summary>

(a) 特征值 $\lambda=2\pm\sqrt5$... $\det=12-4=8$，$\text{tr}=7$，$\lambda=\frac{7\pm\sqrt{49-32}}2=\frac{7\pm\sqrt{17}}2\approx5.56,1.44$（全正 → 正定 ✓）。$Q$ 由特征向量组成。

(b) Cholesky：$L=\begin{pmatrix}2&0\\1&\sqrt2\end{pmatrix}$（$L_{11}=\sqrt4=2$，$L_{21}=2/2=1$，$L_{22}=\sqrt{3-1}=\sqrt2$）。验证 $LL^T=\begin{pmatrix}4&2\\2&3\end{pmatrix}$ ✓。

(c) 生成 $z\sim\mathcal{N}(0,I)$（标准正态），令 $x=Lz$。则 $\text{Cov}(x)=L\,\text{Cov}(z)L^T=LIL^T=\Sigma$。

```python
z = np.random.randn(2, 10000)
x = L @ z  # 10000 个 N(0,Σ) 样本
# 验证协方差 ≈ Σ
print(np.round(np.cov(x), 2))  # ≈ [[4,2],[2,3]]
```

> **ML 关联**：这是 A0 把"谱定理 + 正定算子平方根"接到"高斯过程/数据生成"的招牌应用。
</details>
