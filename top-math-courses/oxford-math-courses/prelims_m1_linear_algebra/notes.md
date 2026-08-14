# Oxford Prelims M1 · 费曼三层笔记（入门线代，英式公理化）

> **教材**：Cameron, *Linear Algebra*
> **特色**：**Oxford Year 1 入门**——从向量空间公理（而非矩阵运算）起步，英式"结构先于计算"风格。为整个 Oxford 数学学位奠基。
> **定位**：比 MIT 18.06 更早抽象（公理化），但深度尚浅（Jordan/对偶留到 Part A A0）。

---

## 总览：Prelims M1 的内容地图

| 主题 | Oxford 特色 |
|---|---|
| 向量空间、子空间 | **公理出发**（不先教矩阵）|
| 线性方程组 | $A\mathbf{x}=\mathbf{b}$ 的几何（列空间）|
| 矩阵、行列式 | 行列式用公理化（非余子式先行）|
| 线性映射、秩 | 维数定理 |
| 特征值、对角化 | 矩阵幂 $A^k$ 与 ODE |
| 内积、正交 | Gram-Schmidt、最小二乘 |

---

## 第 1 层：直觉层（一句话比喻）

> **向量空间** = "能自由伸缩叠加的世界"——Oxford 从 8 条公理定义，而非"一列数"。
> **线性方程组** = "问 $\mathbf{b}$ 是否在列空间里"。
> **特征值** = "变换中方向不变只伸缩的轴"。
> **对角化** = "找到最好的坐标系，让矩阵变对角"。
> **Oxford 的哲学** = "先把骨架（公理/结构）搭好，再填计算肌肉——这样你理解的是'为什么'，不只是'怎么算'。"

---

## 第 2 层：数学层（定义 + 定理 + LaTeX）

### 2.1 向量空间（公理化）

**定义**：$V$ over $\mathbb{F}$，满足 8 条公理（加法交换/结合、零元、负元、标量乘分配/结合、$1v=v$）。

**例子**：$\mathbb{R}^n$，多项式 $\mathbb{F}[x]$，函数空间 $C(\mathbb{R})$。

**子空间**：对加法+数乘封闭的非空子集。

### 2.2 张成、线性无关、基、维数

- **张成** $\text{span}(S)$。
- **线性无关**：$\sum c_iv_i=0\Rightarrow c_i=0$。
- **基**：独立 + 张成。**维数** $\dim V$ = 基的大小（良定义，Steinitz 替换）。

### 2.3 线性方程组与矩阵

$A\mathbf{x}=\mathbf{b}$。**几何**：$\mathbf{b}\in C(A)$（列空间）？

**高斯消元** → 行阶梯形 → 解的结构：无解/唯一解/无穷多解。

**秩** $r$ = 独立列数 = 独立行数。

### 2.4 线性映射与维数定理

$T:V\to W$ 线性。$\ker T$（核），$\text{im}\,T$（像）。

**维数定理**（Rank-Nullity）：$\dim V=\dim\ker T+\dim\text{im}\,T$。

> **ML 关联**：理解 over/under-determined 回归（列数 > 行数 = 欠定）。

### 2.5 行列式

**公理化定义**：$\det$ 是唯一满足（1）多重线性（每行线性）、（2）交错（两行相同=0）、（3）$\det I=1$ 的函数。

**性质**：$\det(AB)=\det A\det B$；$\det A^T=\det A$；$\det A=0$ ⟺ $A$ 不可逆。

**几何**：$|\det A|$ = 线性变换的体积缩放比。

### 2.6 特征值与对角化

$A\mathbf{x}=\lambda\mathbf{x}$。特征多项式 $p(\lambda)=\det(\lambda I-A)$。

**对角化** $A=PDP^{-1}$ ⟺ 有 $n$ 个线性无关特征向量。

**矩阵幂**：$A^k=PD^kP^{-1}$。

> **ML 关联**：PageRank（转移矩阵最大特征值 1 的特征向量）；动力系统迭代。

### 2.7 内积与正交

**内积** $\langle\mathbf{u},\mathbf{v}\rangle$，范数 $\|\mathbf{v}\|=\sqrt{\langle\mathbf{v},\mathbf{v}\rangle}$，Cauchy-Schwarz。

**Gram-Schmidt**：任意基 → 标准正交基。

**正交投影**：$\mathbf{p}=\frac{\langle\mathbf{b},\mathbf{a}\rangle}{\langle\mathbf{a},\mathbf{a}\rangle}\mathbf{a}$。

**最小二乘**：$A^TA\hat{\mathbf{x}}=A^T\mathbf{b}$ → 线性回归。

> **ML 关联**：最小二乘 = 线性回归；Gram-Schmidt = QR 分解（数值稳定求解）。

---

## 第 3 层：代码层（numpy 验证基础概念）

```python
import numpy as np

# === 维数定理: rank + nullity = n ===
A = np.array([[1, 2, 3], [4, 5, 6.0]])  # 2×3
r = np.linalg.matrix_rank(A)
print(f"rank={r}, nullity={3-r}, sum={r+(3-r)} (维数定理: = n=3)")

# === 行列式 = 体积缩放 ===
A = np.array([[2, 0], [0, 3.0]])  # x方向放大2倍, y方向3倍
print(f"det={np.linalg.det(A)}, 单位正方形面积1 → 变换后={abs(np.linalg.det(A))}")

# === 对角化 + 矩阵幂 ===
A = np.array([[2, 1], [1, 2.0]])
ew, ev = np.linalg.eig(A)
print(f"特征值: {ew}")
A5 = ev @ np.diag(ew**5) @ np.linalg.inv(ev)  # A^5 = P D^5 P^-1
print(f"A^5 via 对角化 == 直接幂? {np.allclose(A5, np.linalg.matrix_power(A, 5))}")

# === 最小二乘 (线性回归) ===
A = np.array([[1, 0], [1, 1], [1, 2.0]])  # 拟合 y=a+bt
b = np.array([1.1, 2.0, 2.9])
x_hat = np.linalg.solve(A.T @ A, A.T @ b)  # normal equation
print(f"线性回归: y={x_hat[0]:.2f}+{x_hat[1]:.2f}t")
```

---

## 第 4 层：不足层

1. **不覆盖 Jordan/对偶**：留到 Part A A0。
2. **不覆盖 SVD**：Prelims 不讲，到 Part A/数值分析才出现。
3. **应用导向弱**：Oxford 重结构，PCA/LoRA 的直接应用需结合其他课。
4. **无随机/统计**：概率方向的线代应用需 Part B 概率。

---

## 第 5 层：应用层（ML 公式级对应）

| Prelims M1 概念 | ML 应用 | 公式 |
|---|---|---|
| 线性方程组 | 线性回归 | $A^TA\hat{x}=A^Tb$ |
| 维数定理 | 过/欠参数化理解 | $\dim=\text{rank}+\text{nullity}$ |
| 特征值/对角化 | PageRank / 矩阵幂 | $A^k=PD^kP^{-1}$ |
| 行列式 | 体积/可逆性 | $|\det A|$ = 缩放比 |
| Gram-Schmidt | 数值稳定求解 | $A=QR$ |
| 最小二乘 | 线性回归闭式解 | $\hat{x}=(A^TA)^{-1}A^Tb$ |

---

## 进阶路线

学完 Prelims M1 → **Part A A0**（对偶空间、Jordan 标准型、双线性形式、谱理论深化）→ **Part C C7.1 随机矩阵**（LLM 权重谱分析）。

LoRA/QLoRA 的低秩数学最终通向 Part C C7.1：用 Marchenko-Pastur 律区分权重矩阵的信号/噪声奇异值。

---

## 与 work4ai 讲透系列的交叉

- **讲透线性回归**：最小二乘 = 正交投影（Prelims M1 内积章）。
- **讲透 PageRank**：马尔可夫矩阵特征值（Prelims M1 对角化章）。
- **讲透 Transformer 入门**：矩阵乘法 = 列的线性组合（Prelims M1 矩阵章）。
