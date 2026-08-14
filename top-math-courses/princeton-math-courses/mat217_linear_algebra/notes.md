# Princeton MAT 217 · 费曼三层笔记（荣誉线代）

> **教材**：Hoffman & Kunze *Linear Algebra* / Axler LADR / Halmos *Finite-Dimensional Vector Spaces*
> **特色**：全美最严格的本科线代之一——接续 MAT 215 的证明训练，做到**最一般的抽象**：商空间、对偶空间、Cayley-Hamilton、Jordan、正规算子谱定理、二次型。
> **与 Berkeley 110 的区别**：217 更抽象、更完整（多 quotient space、Cayley-Hamilton 证明、典型群）、节奏更慢更深。

---

## 总览：MAT 217 的抽象阶梯

| 层次 | 概念 | Princeton 独有的深度 |
|---|---|---|
| 1. 空间 | 向量空间、子空间 | + **商空间** $V/U$ |
| 2. 映射 | 线性映射、维数定理 | + **对偶空间** $V^*$、对偶映射 $T^*$ |
| 3. 结构 | 特征值、对角化 | + **Cayley-Hamilton 完整证明** |
| 4. 标准型 | Jordan、有理标准型 | + **不变因子、初等因子** |
| 5. 几何 | 内积、谱定理 | + **正规算子、典型群 O/U/SO(n)** |
| 6. 形式 | 双线性、二次型 | + **Sylvester 惯性律、合同** |

---

## 第 1 层：直觉层（一句话比喻）

> **商空间** $V/U$ = "把 $U$ 里的所有向量'看成同一个点'后得到的新空间"——像把三维空间按层切片成二维。
> **对偶空间** $V^*$ = "所有'测量'向量的尺子的集合"——每个尺子是一个线性泛函。
> **Cayley-Hamilton** = "矩阵是自己的特征方程的根"。
> **二次型的合同** = "换个坐标系看同一个二次曲面，形状不变"。
> **Princeton 的哲学** = "每个概念都做到最一般——先抽象，再具体；这样你看到的是结构，不是特例。"

---

## 第 2 层：数学层（定义 + 定理 + 证明思路 + LaTeX）

### 2.1 商空间（Quotient Space）★（Princeton 特色）

**动机**：模掉一个子空间，"忽略"那个方向。

**定义**：$U\subseteq V$ 子空间。陪集 $\mathbf{v}+U=\{\mathbf{v}+\mathbf{u}:\mathbf{u}\in U\}$。商空间 $V/U=\{\mathbf{v}+U:\mathbf{v}\in V\}$。

**维数**：$\dim(V/U)=\dim V-\dim U$。

**商映射** $\pi:V\to V/U$，$\pi(\mathbf{v})=\mathbf{v}+U$。线性，$\ker\pi=U$。

**应用**：商空间让"模掉等价关系"严格化。

> **ML 关联**：持续学习把权重空间"商掉旧知识子空间"→ 新学习不干扰旧知识。quotient space 是描述这的语言。

### 2.2 对偶空间 $V^*$ ★

**定义**：$V^*=\mathcal{L}(V,\mathbb{F})$ = 所有线性泛函 $f:V\to\mathbb{F}$。$\dim V^*=\dim V$。

**对偶基**：若 $e_1,\dots,e_n$ 是 $V$ 的基，对偶基 $e^1,\dots,e^n\in V^*$ 满足 $e^i(e_j)=\delta^i_j$。

**对偶映射**：$T:V\to W$ 诱导 $T^*:W^*\to V^*$，$(T^*f)(\mathbf{v})=f(T\mathbf{v})$。（注意：这是代数对偶，不同于内积空间的伴随。）

**定理**：$\text{range}(T^*)=(\text{null}\,T)^0$（零化子），$\text{null}(T^*)=(\text{range}\,T)^0$。四子空间的对偶版本。

> **ML 关联**：Riesz 表示定理（内积空间）：每个泛函 $f$ = 与某固定向量的内积 → 核方法 $f(\mathbf{x})=\langle\phi(\mathbf{x}),\mathbf{w}\rangle$。反向传播的梯度是"对偶向量"。

### 2.3 特征值与 Cayley-Hamilton ★★（完整证明）

**特征值**：$T\mathbf{v}=\lambda\mathbf{v}$。

**Cayley-Hamilton 定理**（完整证明，Hoffman & Kunze 传统）：

$A$ 满足 $p_A(A)=0$，$p_A(\lambda)=\det(\lambda I-A)$。

**证明思路**（用伴随矩阵）：$\text{adj}(\lambda I-A)\cdot(\lambda I-A)=p_A(\lambda)I$。$\text{adj}(\lambda I-A)$ 是 $\lambda$ 的矩阵多项式 $B_0+\lambda B_1+\cdots+\lambda^{n-1}B_{n-1}$。展开比较 $\lambda$ 幂 → 得 $p_A(A)=0$。

> 这是 Princeton 要求的"不靠三角化、直接代数"的证明。

### 2.4 不变子空间与 Jordan 标准型

**不变子空间** $W$：$T(W)\subseteq W$。

**广义特征空间**：$G(\lambda,T)=\text{null}(T-\lambda I)^{\dim V}$。

**Jordan 定理**（复）：$V=\bigoplus_\lambda G(\lambda,T)$，每个 $G(\lambda,T)$ 上 $T$ 有 Jordan 形式 $J_{m_1}(\lambda)\oplus\cdots$。

**有理标准型**（Princeton 加深）：不依赖特征值（任意域），用不变因子构造友矩阵（companion matrix）。

### 2.5 内积空间与谱定理

**伴随** $T^*$：$\langle T\mathbf{u},\mathbf{v}\rangle=\langle\mathbf{u},T^*\mathbf{v}\rangle$。

**正规算子谱定理**（最一般版本）★：
- 复：$T$ 正规（$TT^*=T^*T$）⟺ 有标准正交特征基。
- 实：$T$ 自伴（$T=T^*$）⟺ 有标准正交特征基（特征值实）。

> **ML 关联**：协方差对称 → 谱定理 → PCA。MAT 217 让你看到 PCA 是"正规算子"理论的最简单特例。

### 2.6 双线性形式与二次型 ★（Princeton 完整）

**双线性形式** $B:V\times V\to\mathbb{F}$：双线性。

**矩阵表示**：固定基，$B(\mathbf{u},\mathbf{v})=\mathbf{u}^T A\mathbf{v}$。换基 → **合同** $A\mapsto P^TAP$（不是相似！）。

**Sylvester 惯性律**：对称双线性形式在合同下，正/负/零特征值个数不变（惯性 $(p,q,r)$）。

**分类**：正定（$p=n$）、负定、不定、退化。

> **ML 关联**：Hessian 的惯性 $(p,q,0)$ 判定临界点类型（$p=n$ 极小，$q=n$ 极大，不定则鞍点）。SVM 对偶是半正定二次型。Mahalanobis 距离用正定 $\Sigma^{-1}$。

### 2.7 典型群（接抽象代数）

- $\mathrm{GL}(V)$：一般线性群（所有可逆算子）。
- $\mathrm{O}(V)$：正交群（保内积 $T^*T=I$）。
- $\mathrm{U}(V)$：酉群（复正交）。
- $\mathrm{SO}(n)$：特殊正交（行列式 1，旋转）。

> **ML 关联**：正交初始化（$\mathrm{O}(n)$ 元素）；等变神经网络用 $\mathrm{SO}(3)$（AlphaFold）。

---

## 第 3 层：代码层（numpy 验证 quotient/dual/Cayley-Hamilton）

```python
import numpy as np

# === Cayley-Hamilton (矩阵多项式, 用 @ 不是逐元素) ===
A = np.array([[1.0, 2], [3, 4]])
tr, det = np.trace(A), np.linalg.det(A)
pA = A @ A - tr * A + det * np.eye(2)  # λ²-(tr)λ+(det), 矩阵版
print("Cayley-Hamilton p(A)=0?", np.allclose(pA, 0))

# === 对偶空间: 对偶基 ===
V = np.array([[1, 0], [1, 2]])  # V 的基向量作为列
Vinv = np.linalg.inv(V)
# 对偶基的坐标: e^i 满足 e^i(e_j)=δ^i_j => 对偶基矩阵 = V^{-T} 的列
dual_basis = Vinv.T  # 每列是一个对偶基向量
print("对偶基 × 原基 = I?", np.allclose(dual_basis.T @ V, np.eye(2)))

# === 合同 vs 相似: 二次型的坐标变换 ===
S = np.array([[2.0, 0], [0, 3]])  # 对角二次型
P = np.array([[1.0, 1], [0, 1]])  # 换基矩阵
congruent = P.T @ S @ P   # 合同 (二次型换基)
similar = np.linalg.inv(P) @ S @ P  # 相似 (算子换基)
print("合同矩阵:\n", congruent, "\n不同于相似:\n", np.round(similar, 3))

# === Sylvester 惯性律: 合同保持惯性 ===
eig_before = np.linalg.eigvalsh(S)
eig_after = np.linalg.eigvalsh(congruent)
print(f"惯性 (正特征值数): 合同前 {np.sum(eig_before>0)}, 合同后 {np.sum(eig_after>0)}")
```

---

## 第 4 层：不足层

1. **纯数学导向**：无 PCA/SVD 的工程实现（见 [MIT 18.06](../../mit-math-courses/18_06_linear_algebra/) / [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)）。
2. **Jordan 数值不稳定**：理论完美但计算上几乎不可用（用 Schur 替代）。
3. **有限维为主**：泛函（无限维）需另学。
4. **不覆盖随机/张量**：LoRA 统计理论、tensor 分解需额外课程。

---

## 第 5 层：应用层（ML 公式级对应）

| MAT 217 概念 | ML 应用 | 公式 |
|---|---|---|
| 商空间 $V/U$ | 持续学习（商掉旧知识） | 权重空间分解 |
| 对偶空间 $V^*$ | 核方法 / 反向传播梯度 | Riesz: $f(\mathbf{x})=\langle\mathbf{x},\mathbf{v}\rangle$ |
| Cayley-Hamilton | 矩阵幂降阶 | $A^k$ 约束在 $n$ 维 |
| 谱定理（正规算子） | PCA（最一般条件） | $\Sigma=Q\Lambda Q^T$ |
| 二次型 + Sylvester 惯性 | Hessian 凸性 / SVM | $(p,q,r)$ 惯性 |
| 典型群 O(n)/SO(n) | 正交初始化 / 等变网络 | $T^*T=I$ |

---

## 与 work4ai 讲透系列的交叉

- **讲透优化器**：二次型惯性 → Hessian → 凸性 → 收敛性。
- **讲透 Transformer**：对偶空间 → 注意力的核视角；典型群 → 正交初始化。
- **讲透 LoRA/MRL**：商空间 + 不变子空间 → 低秩更新的子空间解释。
