# Stanford MATH 113 · 费曼三层笔记（理论线代）

> **教材**：Axler *LADR* 4th ed（主）+ Strang *Introduction to Linear Algebra*（辅）
> **特色**：Stanford 的"理论 + 应用双轨"——既要严格证明，又要连上优化（CME 364A）与统计（STATS 200）。
> **与 Berkeley 110 的区别**：113 更强调 **Jordan 形式 / Cayley-Hamilton / 矩阵指数**在动力系统中的应用。

---

## 总览：Stanford 113 的双重视角

| 主题 | Axler 视角（结构）| Strang 视角（几何/计算）|
|---|---|---|
| 特征值 | 不变子空间 → 多项式 | $\det(A-\lambda I)=0$ + 图形直觉 |
| 谱定理 | 自伴算子有标准正交基 | 对称矩阵 = 椭球主轴 |
| Jordan 形式 | ★ 113 重点：广义特征向量 | 动力系统稳定性 |
| 矩阵指数 | $e^{At}=\sum A^kt^k/k!$ | ODE 解的谱分解 |

Stanford 的独特之处：把线代直接接到**硅谷的应用数学**——凸优化、统计、ML。

---

## 第 1 层：直觉层（一句话比喻）

> **Jordan 形式** = "特征值相同的矩阵，按'几乎不能对角化'的程度排队"——对角化是最简单情况，Jordan 块是"退而求其次"的最简形。
> **Cayley-Hamilton** = "矩阵满足自己的特征方程"——它自己的多项式把它归零。
> **矩阵指数** = "把 $e^x$ 的泰勒级数里的 $x$ 换成矩阵"——解线性 ODE 的万能钥匙。
> **Stanford 的哲学** = "理论要美，但必须能算、能用——证明谱定理是为了理解 PCA，证 Jordan 是为了分析 RNN。"

---

## 第 2 层：数学层（定义 + 定理 + 证明思路 + LaTeX）

### 2.1 向量空间与线性映射（复习 + 深化）

- **向量空间** $V$ over $\mathbb{F}$，**线性映射** $T:V\to W$。
- **维数定理**：$\dim V=\dim\text{null}\,T+\dim\text{range}\,T$。
- **矩阵表示**：固定基后，$T\leftrightarrow$ 矩阵 $A$。换基 $=$ 相似 $A'=P^{-1}AP$。

### 2.2 特征值与对角化

$A\mathbf{x}=\lambda\mathbf{x}$。对角化 $A=PDP^{-1}$（$D$ 对角）要求 $A$ 有 $n$ 个线性无关特征向量。

**可对角化条件**：几何重数 $=$ 代数重数（每个特征值）。

> 若不可对角化 → 需要 **Jordan 形式**（113 重点）。

### 2.3 谱定理（对称/Hermitian 矩阵）★★

**实谱定理**：$A=A^T$ ⟺ 存在正交 $Q$ 使 $A=Q\Lambda Q^T$（$\Lambda$ 对角，元素实）。

证明思路（自伴性 → 特征值实 → 归纳构造正交特征基）。详见 [Berkeley 110 notes](../../berkeley-math-courses/math110_linear_algebra/notes.md)。

**ML 关联**：协方差 $\Sigma=\frac1nX^TX$ 对称 → PCA 良定义。

### 2.4 Cayley-Hamilton 定理 ★（113 特色）

**定理**：每个方阵满足自己的特征方程。若 $p(\lambda)=\det(\lambda I-A)=\lambda^n+c_{n-1}\lambda^{n-1}+\cdots+c_0$，则
$$p(A)=A^n+c_{n-1}A^{n-1}+\cdots+c_0I=0$$

**证明思路**（用三角化 + 上三角矩阵的代数）：复数域上 $A$ 可上三角化 $A=UTU^*$，$p(A)=Up(T)U^*$。对上三角 $T$，$p(T)$ 的对角元 $p(t_{ii})=0$（$t_{ii}$ 是特征值），再用 $T-\lambda I$ 的结构证 $p(T)=0$。

**应用**：
- **矩阵求逆**：若 $A$ 可逆，$p(A)=0$ ⟹ $A^{-1}=-\frac1{c_0}(A^{n-1}+\cdots+c_1I)$。
- **矩阵幂降阶**：$A^k\ (k\geq n)$ 用特征方程降为 $<n$ 次多项式。
- **ML**：RNN 长程依赖 $\prod_{t}W^T$ 的分析，可用 Cayley-Hamilton 把高次幂约束在 $n$ 维。

### 2.5 Jordan 标准型 ★★★（113 核心）

**动机**：不是所有矩阵可对角化。Jordan 形式是"最接近对角化"的标准形。

**Jordan 块**：
$$J_m(\lambda)=\begin{pmatrix}\lambda&1&&\\&\lambda&\ddots&\\&&\ddots&1\\&&&\lambda\end{pmatrix}_{m\times m}$$

**Jordan 定理**：每个复矩阵 $A$ 相似于 Jordan 矩阵 $J=\bigoplus_i J_{m_i}(\lambda_i)$：
$$A=PJP^{-1},\quad J=J_{m_1}(\lambda_1)\oplus\cdots\oplus J_{m_k}(\lambda_k)$$

**广义特征向量**：$(A-\lambda I)^k\mathbf{v}=0$ 的向量。Jordan 链 $\mathbf{v}_1,\dots,\mathbf{v}_m$ 满足 $(A-\lambda I)\mathbf{v}_j=\mathbf{v}_{j-1}$。

**为什么重要**：Jordan 块的非对角 1 带来**多项式增长**：
$$J_m(\lambda)^k\ \text{含}\ \binom{k}{j}\lambda^{k-j}\text{项}$$

> **ML 关联（113 招牌）**：动力系统 $\dot{\mathbf{x}}=A\mathbf{x}$，解 $\mathbf{x}(t)=e^{At}\mathbf{x}_0$。
> - $e^{J_m(\lambda)t}=e^{\lambda t}\begin{pmatrix}1&t&\cdots&\frac{t^{m-1}}{(m-1)!}\\&1&\ddots&\\&&\ddots&t\\&&&1\end{pmatrix}$
> - $\text{Re}(\lambda)<0$ → 衰减稳定；Jordan 块 $>1$ 时多项式项 $t^k$ 短暂增长。
> - **Neural ODE** $\dot{\mathbf{h}}=f(\mathbf{h})$ 在平衡点线性化，稳定性 = Jacobian 的特征值实部。

### 2.6 矩阵指数与 ODE ★

$$e^{At}=\sum_{k=0}^{\infty}\frac{(At)^k}{k!}$$

性质：$e^{A(s+t)}=e^{As}e^{At}$；$\frac{d}{dt}e^{At}=Ae^{At}$。

用 Jordan 形式：$e^{At}=Pe^{Jt}P^{-1}$。

**ML 关联**：残差网络 $\mathbf{h}_{l+1}=\mathbf{h}_l+f(\mathbf{h}_l)$ 的连续极限 = Neural ODE。Euler 离散化 $=$ 残差连接。

### 2.7 正定矩阵与优化

$A$ 正定 ⟺ 特征值 $>0$ ⟺ $\mathbf{x}^TA\mathbf{x}>0$。

$f$ 凸 ⟺ Hessian $\nabla^2f\succeq0$。→ **Stanford CME 364A 的基石**。

### 2.8 SVD（连接 Strang 视角）

$A=U\Sigma V^T$。Eckart-Young 低秩近似 → PCA / LoRA。

---

## 第 3 层：代码层（numpy 验证 Jordan / Cayley-Hamilton / 矩阵指数）

```python
import numpy as np
from scipy.linalg import expm

# === Cayley-Hamilton: A 满足自己的特征方程 ===
A = np.array([[2, 1], [1, 2]])
# 特征多项式 λ²-4λ+3 (tr=4, det=3); 注意 np.polyval 是逐元素的, 矩阵多项式须用 @
pA = A @ A - 4 * A + 3 * np.eye(2)  # p(A) = A²-4A+3I
print("Cayley-Hamilton p(A)=0?", np.allclose(pA, np.zeros((2, 2))))  # True

# === Jordan 块的幂 (多项式增长) ===
J = np.array([[0.5, 1, 0], [0, 0.5, 1], [0, 0, 0.5]])  # 3×3 Jordan 块, λ=0.5
print("J^10 =", np.round(np.linalg.matrix_power(J, 10), 3))  # 含 k*λ^(k-1) 多项式项

# === 矩阵指数 e^(At) 与 ODE 稳定性 ===
A_unstable = np.array([[0.1, 0], [0, -0.5]])  # 特征值 0.1(不稳定), -0.5(稳定)
t = 5.0
eAt = expm(A_unstable * t)
print(f"e^(A·{t}) 的谱 = {np.round(np.linalg.eigvals(eAt), 4)}")
print("  特征值>1 的方向爆炸 (Neural ODE 不稳定)")

# === Jordan 形式: 不可对角化矩阵 ===
# A = [[2,1],[0,2]] 只有1个特征向量(几何重数1 < 代数2)
A_jordan = np.array([[2, 1], [0, 2]])
eigvals, eigvecs = np.linalg.eig(A_jordan)
print(f"特征值: {eigvals}, 特征向量矩阵秩: {np.linalg.matrix_rank(eigvecs)} (不可对角化)")
```

---

## 第 4 层：不足层

1. **Jordan 形式数值不稳定**：微小扰动可改变 Jordan 结构，实际计算用 Schur 分解（上三角）替代（见 [M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)）。
2. **实矩阵的 Jordan 可能含复数**：需实 Jordan 形式（$2\times2$ 块）处理复特征值对。
3. **不覆盖随机矩阵 / 张量**：LoRA 的统计理论、tensor decomposition 需额外课程。

---

## 第 5 层：应用层（ML 公式级对应）

| 113 概念 | ML 应用 | 公式 |
|---|---|---|
| 谱定理 | PCA / 协方差 | $\Sigma=Q\Lambda Q^T$ |
| Jordan 形式 | Neural ODE / RNN 稳定性 | $e^{Jt}$ 的多项式-指数项 |
| Cayley-Hamilton | 矩阵幂降阶 / RNN 分析 | $A^k$ 降为 $<n$ 次多项式 |
| 正定矩阵 | 凸优化 / Hessian | $\nabla^2f\succeq0$ ⟺ 凸 |
| 矩阵指数 | 残差网络连续化 | $\mathbf{x}(t)=e^{At}\mathbf{x}_0$ |
| SVD | LoRA 低秩 | $W_0+BA$ |

---

## 与 work4ai 讲透系列的交叉

- **讲透优化器**：正定 Hessian + 条件数 → 梯度下降收敛速率（113 + CME 364A）。
- **讲透 RNN**：Jordan 形式 → 长程依赖 $\prod W$ 的谱衰减。
- **讲透 Neural ODE**：矩阵指数 $e^{At}$ + 稳定性（特征值实部）。
