# UT Austin M340L · 费曼三层笔记（应用线代，最友好版）

> **教材**：Lay, Lay & McDonald, *Linear Algebra and Its Applications* 6th ed
> **特色**：**UT Austin 应用线代**——10 校中最友好的一门。**不先教公理**，直接从矩阵运算和线性方程组入手，逐步引向特征值/SVD。**数据科学导向**：每章都有真实数据应用（PCA、网络、Leontief 投入产出、马尔可夫链）。
> **后续**：UT **M 383E 数值线代**（NumPy/PyTorch 底层）；UT 数据科学证书全栈。

---

## 总览：M340L 的应用驱动结构

| Lay 章节 | 应用钩子 | ML 对应 |
|---|---|---|
| Ch1 线性方程组 | 投入产出、网络流 | 线性回归闭式解 |
| Ch2 矩阵代数 | 图像变换 | 注意力 $QK^T$ |
| Ch3 行列式 | 体积、可逆判定 | 雅可比 |
| Ch4 向量空间 | 子空间、四子空间 | 特征空间 |
| Ch5 特征值 | 马尔可夫链、PageRank | 谱聚类 |
| Ch6 正交/最小二乘 | 最小二乘回归、GPS | 普通最小二乘 (OLS)、岭回归 |
| Ch7 对称矩阵/SVD | PCA、图像压缩 | LoRA、PCA |

---

## 第 1 层：直觉层（一句话比喻）

> **矩阵乘向量** = "矩阵列的线性组合"——$A\mathbf{x}=x_1\mathbf{a}_1+\cdots+x_n\mathbf{a}_n$。Lay 第一章就让你**看见**这个。
> **秩** = "矩阵里真正独立的信息量"——其余都是冗余。
> **特征值** = "变换中只伸缩不旋转的方向"。
> **SVD** = "任何矩阵都能拆成'旋转→伸缩→旋转'三步"。
> **Lay 的哲学** = "先建立矩阵直觉（看得见、摸得着），再慢慢加抽象——这样应用型人才不会在公理墙前却步。"

---

## 第 2 层：数学层（定义 + 关键公式）

### 2.1 线性方程组与矩阵

$A\mathbf{x}=\mathbf{b}$ 的三种可能：无解 / 唯一解 / 无穷多解。

**高斯消元** → RREF（简化行阶梯形）→ 读解。

**列空间** $C(A)$：$A$ 列的所有线性组合。$\mathbf{b}\in C(A)$ ⟺ $A\mathbf{x}=\mathbf{b}$ 有解。

> **Lay 特色**：Ch1 就引入列空间几何，让"无解"变成"b 不在列空间里"——直观。

### 2.2 矩阵代数

$(AB)\mathbf{x}=A(B\mathbf{x})$。**注意**：$AB\neq BA$（一般）。

**分块矩阵**：大矩阵当"小矩阵的矩阵"乘。

> **ML 关联**：Transformer 的 $QK^T V$ 是分块/批量矩阵乘；PyTorch `einsum` 的本质。

### 2.3 行列式

$\det A$ = 体积缩放比。$\det A=0$ ⟺ 奇异（不可逆）。

余子式展开 + 性质（$\det(AB)=\det A\det B$）。

### 2.4 向量空间与四子空间 ★

- **列空间** $C(A)\subseteq\mathbb{R}^m$
- **零空间** $N(A)\subseteq\mathbb{R}^n$
- **行空间** $C(A^T)\subseteq\mathbb{R}^n$
- **左零空间** $N(A^T)\subseteq\mathbb{R}^m$

**秩** $r=\dim C(A)=\dim C(A^T)$。

> **Lay 的招牌**：四子空间图——把矩阵的"结构"可视化。这是后续 Strang/MIT 18.06 的核心。

### 2.5 特征值与对角化

$A\mathbf{x}=\lambda\mathbf{x}$。特征多项式 $\det(\lambda I-A)$。

**对角化** $A=PDP^{-1}$ → $A^k=PD^kP^{-1}$。

**马尔可夫链**：转移矩阵 $M$（列随机），稳态 = $\lambda=1$ 的特征向量。

**PageRank**：带阻尼的马尔可夫链 $\mathbf{p}_{t+1}=dM\mathbf{p}_t+\frac{1-d}{n}\mathbf{1}$。

### 2.6 正交与最小二乘 ★（M340L 招牌应用）

**正交投影** $\text{proj}_{\mathbf{a}}\mathbf{b}=\frac{\mathbf{a}^T\mathbf{b}}{\mathbf{a}^T\mathbf{a}}\mathbf{a}$。

**Gram-Schmidt** → QR 分解。

**最小二乘**（过定系统 $A\mathbf{x}\approx\mathbf{b}$）：
$$\hat{\mathbf{x}}=(A^TA)^{-1}A^T\mathbf{b}$$

> **ML 关联**：**这就是线性回归的闭式解**——M340L 让你看见最小二乘 = 正交投影。

### 2.7 对称矩阵、二次型、SVD ★

**对称矩阵谱定理**：$A=A^T$ → 特征值实、特征向量正交。

**正定** $A$：$\mathbf{x}^TA\mathbf{x}>0\ \forall\mathbf{x}\neq0$ ⟺ 特征值全正 ⟺ 顺序主子式全正。

**SVD** $A=U\Sigma V^T$：任何矩阵都有，$\sigma_i$ = 奇异值。

**Eckart-Young**：$A_k$（截断 SVD）是最优秩-$k$ 近似。

> **ML 关联**：PCA = 中心化数据 SVD；LoRA = 权重增量的低秩近似。

---

## 第 3 层：代码层（numpy 验证四子空间/最小二乘/SVD）

```python
import numpy as np

# === 四子空间: C(A) 和 N(A) 的正交关系 ===
A = np.array([[1, 2, 3],
              [4, 5, 6.0]])
# N(A): Ax=0 的解
# RREF → x1 = x3, x2 = -2*x3 → 基 (1,-2,1)
n_basis = np.array([1, -2, 1.0])
print(f"A @ 零空间基 = 0? {np.allclose(A @ n_basis, 0)} (零空间 ⊥ 行空间)")

# === 最小二乘 = 线性回归闭式解 ===
t = np.array([0, 1, 2, 3, 4.0])
y = np.array([1.1, 2.9, 5.1, 6.8, 9.2])  # 近似 y=2t+1
A = np.column_stack([np.ones_like(t), t])  # 设计矩阵
x_hat = np.linalg.solve(A.T @ A, A.T @ y)  # normal equation
print(f"线性回归: y = {x_hat[0]:.2f} + {x_hat[1]:.2f}*t  (真值 ~1, 2)")

# === SVD 低秩近似 (PCA / 图像压缩) ===
np.random.seed(42)
data = np.random.randn(20, 10)  # 20 个 10 维样本
data_centered = data - data.mean(axis=0)
U, S, Vt = np.linalg.svd(data_centered, full_matrices=False)
# PCA: 主成分 = V 的行（右奇异向量）
explained = S**2 / (S**2).sum()
print(f"前 2 个主成分解释方差: {explained[:2].sum():.1%}")

# === 马尔可夫链稳态 (PageRank 雏形) ===
M = np.array([[0.9, 0.3],
              [0.1, 0.7]])  # 列随机
ew, ev = np.linalg.eig(M)
idx = np.argmin(np.abs(ew - 1.0))  # λ=1 的特征向量
steady = ev[:, idx].real
steady /= steady.sum()
print(f"稳态分布: {np.round(steady, 3)}  (λ=1 特征向量)")

# === 对称矩阵谱定理 + 正定 ===
S = np.array([[2, 1], [1, 3.0]])
vals, vecs = np.linalg.eigh(S)
print(f"对称矩阵特征值 {np.round(vals,3)} (全正→正定); QΛQᵀ=S? {np.allclose(vecs@np.diag(vals)@vecs.T, S)}")
```

---

## 第 4 层：不足层

1. **理论证明最少**：Lay 重应用轻证明——抽象派（Oxford/Cambridge）会觉得不够"数学"。
2. **不覆盖对偶/Jordan**：高级结构留到研究生课。
3. **不覆盖随机矩阵**：LoRA 的统计理论需更深课程。
4. **数值方法浅**：只教原理，不教 Householder/Givens 等稳定算法（那是 M 383E）。
5. **复数矩阵简略**：Hermitian/酉只在附录。

---

## 第 5 层：应用层（ML/数据科学公式级对应）

| M340L 章节 | 应用 | 公式 / 代码 |
|---|---|---|
| Ch1 方程组 | 投入产出、网络流 | $A\mathbf{x}=\mathbf{b}$ |
| Ch2 矩阵 | 图像变换、注意力 | $QK^TV$ |
| Ch4 子空间 | 特征工程 | 四子空间 |
| Ch5 特征值 | PageRank/马尔可夫 | $M\mathbf{p}=\mathbf{p}$ |
| Ch6 最小二乘 | **线性回归** | $\hat{x}=(A^TA)^{-1}A^Tb$ |
| Ch6 QR | 稳健回归 | $R\hat{x}=Q^Tb$ |
| Ch7 正定 | 协方差/岭回归 | $x^TAx>0$ |
| Ch7 SVD | **PCA / LoRA** | $A_k=\sum_{i=1}^k\sigma_iu_iv_i^T$ |

---

## UT Austin 后续路线

```
M340L 应用线代 (本课) ──┬──▶ M 383E 数值线代 (LU/QR/Householder 稳定算法)
                        ├──▶ M 378K 统计 → 数据科学证书
                        └──▶ CS 机器学习 / NLP → LoRA/Transformer
```

**UT Austin 的优势**：应用线代 + 数值线代 + 数据科学证书的完整链条——从 M340L 到生产级 ML 的路径最短。

---

## 与 work4ai 讲透系列的交叉

- **讲透线性回归**：M340L Ch6 最小二乘 = OLS 闭式解。
- **讲透 PCA**：M340L Ch7 SVD + 协方差谱定理。
- **讲透 PageRank**：M340L Ch5 马尔可夫链特征值。
- **讲透 Transformer 入门**：M340L Ch2 矩阵乘 = 列线性组合。
- **讲透 LoRA/MRL**：M340L Ch7 Eckart-Young → 低秩微调。

---

## 学习建议（给初学者）

1. **Lay 先读，Strang 后补**：Lay 建立直觉，Strang 加深四子空间。
2. **每章做 2 个应用题**：投入产出、最小二乘、PageRank——这些是 Lay 的精华。
3. **用 numpy 验证每一步**：见上方代码，跑一遍比读十遍强。
4. **做完后挑战 MIT 18.06**：M340L 是跳板，18.06 是招牌。
