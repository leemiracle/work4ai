# Berkeley MATH 110 · 费曼三层笔记（Axler *Linear Algebra Done Right* 4th ed）

> **教材**：Axler, *Linear Algebra Done Right* (LADR), 4th ed, Springer, 2023（[免费 PDF](https://axler.net/LADR.html)）
> **风格**：**不用行列式**定义特征值——从向量空间 → 线性映射 → 算子 → 谱定理的纯结构路线
> **与 MIT 18.06 的关系**：18.06 教"算与直觉"，110 教"证明与结构"。两本互为镜像。

---

## 总览：Axler 的路线图 vs 传统路线

| 主题 | 传统路线（用行列式）| **Axler 路线（不用行列式）** |
|---|---|---|
| 特征值 | $\det(A-\lambda I)=0$ | $T$ 的不变子空间 → 多项式根 |
| 行列式 | 置换/余子式定义 | 用外形式 $\omega$ 定义：$\det T$ 是唯一使 $(Tv_1)\wedge\cdots\wedge(Tv_n)=c(v_1\wedge\cdots\wedge v_n)$ |
| 谱定理 | 特征多项式 + 内积 | **直接从自伴/正规算子构造** |
| 特征值存在性 | 代数基本定理（$\det$ 有复根）| 复空间：有限维算子必有特征值（用多项式）|

**为什么 Axler 不用行列式？** 因为行列式是一个"打包好的黑箱"——用它定义特征值绕过了结构。Axler 让你**看见**特征值是从哪里来的：不变子空间。

---

## 第 1 层：直觉层（一句话比喻）

> **向量空间** = 一个能用"线性组合"自由伸缩叠加的世界。
> **线性映射** = 保持网格线笔直、原点不动的变换。
> **特征值/不变子空间** = 变换中"方向不变只伸缩"的轴。
> **谱定理** = 对称/正规变换一定能找到一组互相垂直的"主轴"，变换在每根轴上只是单纯缩放。
> **Axler 的洞察** = "别用行列式这个大锤敲特征值这颗钉子——特征值的本质是'方向被保留'，不是'某个多项式等于零'。"

---

## 第 2 层：数学层（定义 + 定理 + 证明思路 + LaTeX）

### 2.1 向量空间与子空间（Ch 1-2）

**定义**（向量空间）：域 $\mathbb{F}$（$\mathbb{R}$ 或 $\mathbb{C}$）上的向量空间 $V$ 是带加法与标量乘法、满足 8 条公理的集合。

**定义**（张成与线性组合）：$\text{span}(v_1,\dots,v_n) = \{c_1v_1+\cdots+c_nv_n : c_i\in\mathbb{F}\}$。

**关键定理**（线性无关 ⟺ 唯一表示）：$v_1,\dots,v_n$ 线性无关 ⟺ 每个 $v\in\text{span}$ 的表示**唯一**。

**定理**（基的大小不变，即维度良定义）：$V$ 的任一组基都有相同元素个数，记 $\dim V$。

**证明思路**（Axler 2.35，Steinitz 替换）：若 $u_1,\dots,u_m$ 张成而 $w_1,\dots,w_n$ 独立，则 $m\geq n$。把独立向量逐个"插入"张成组并"挤出"一个老向量，独立性保持。→ 由此 $\dim$ 良定义。

### 2.2 线性映射、零空间、像（Ch 3）

**定义**：线性映射 $T:V\to W$ 满足 $T(u+v)=Tu+Tv$，$T(\lambda u)=\lambda Tu$。

**零空间** $\text{null}\,T = \{v:Tv=0\}$，**像** $\text{range}\,T = \{Tv:v\in V\}$。

#### ★ 维数定理（Rank-Nullity，Axler 3.22）

$$\dim V = \dim\text{null}\,T + \dim\text{range}\,T$$

**证明思路**：取 $\text{null}\,T$ 的基 $u_1,\dots,u_k$，扩充成 $V$ 的基 $u_1,\dots,u_k,v_1,\dots,v_r$。则 $Tv_1,\dots,Tv_r$ 是 $\text{range}\,T$ 的基（需证张成 + 独立）。故 $\dim V = k+r = \dim\text{null}+\dim\text{range}$。

> **ML 关联**：这就是 18.06 "四个子空间"维数关系的抽象版。$\dim\text{range}$ = rank，$\dim\text{null}$ = nullity。

### 2.3 多项式（Ch 4，为特征值做准备）

Axler 单列一章多项式，因为**有限维算子的特征值理论完全依赖多项式**。

**核心工具**：每个非常值复系数多项式有根（代数基本定理）。这保证复空间上算子必有特征值。

### 2.4 特征值、不变子空间（Ch 5）★★★ — Axler 的招牌

**定义**（不变子空间）：$W\subseteq V$ 是 $T$ 的不变子空间，若 $T(W)\subseteq W$。

**定义**（特征值）：$\lambda\in\mathbb{F}$ 是 $T$ 的特征值，若存在 $v\neq0$ 使 $Tv=\lambda v$。等价地：$\text{null}(T-\lambda I)\neq\{0\}$，即 $1$ 维不变子空间存在。

#### ★ Axler 的特征值存在性定理（5.21，复情形）

**在复向量空间上，每个算子都有特征值。**

**证明思路**（关键！不用行列式）：取 $v\neq0$，考虑 $v,Tv,T^2v,\dots,T^nv$（$n=\dim V$）。这 $n+1$ 个向量必线性相关 → 存在多项式 $p$ 使 $p(T)v=0$。由代数基本定理 $p(T)=(T-\lambda_1 I)\cdots(T-\lambda_m I)$，故某个 $(T-\lambda_j I)$ 不可逆 → $\lambda_j$ 是特征值。

> **对比**：传统教材写 $\det(A-\lambda I)=0$ 然后解多项式。Axler 直接从"$T$ 的幂必然相关"推出特征值——**纯结构，无行列式**。这是 LADR 全书最优雅的论证之一。

**定义**（特征多项式 vs 最小多项式）：Axler 优先用**最小多项式**（使 $p(T)=0$ 的最低次首一多项式）。

### 2.5 内积空间（Ch 6）

**定义**（内积）：$\langle u,v\rangle$ 满足线性性（第一参量）、共轭对称 $\langle u,v\rangle=\overline{\langle v,u\rangle}$、正定性。

**范数** $\|v\|=\sqrt{\langle v,v\rangle}$。**Cauchy-Schwarz** $|\langle u,v\rangle|\leq\|u\|\|v\|$。

**正交投影**（6.55）：对子空间 $U$，每个 $v=u+w$（$u\in U, w\in U^\perp$）唯一分解。投影算子 $P_Uv=u$。

#### ★ Gram-Schmidt（6.31）与 QR

把任意基变成标准正交基：$e_k = \frac{v_k - \sum_{j<k}\langle v_k,e_j\rangle e_j}{\|\cdot\|}$。矩阵形式即 $A=QR$。

### 2.6 内积空间上的算子（Ch 7）— 谱定理的前奏

**定义**（伴随，adjoint）：$T^*$ 是唯一满足 $\langle Tu,v\rangle=\langle u,T^*v\rangle$ 的算子。

- **自伴**（self-adjoint）：$T=T^*$（实空间即对称）。
- **正规**（normal）：$TT^*=T^*T$。

**关键引理**（7.21）：$T$ 正规 ⟹ $\|Tv\|=\|T^*v\|$ 对所有 $v$。→ 这是谱定理的基石。

### 2.7 谱定理（Ch 7）★★★

#### 复谱定理（Axler 7.24）

$V$ 是有限维**复**内积空间。以下等价：
1. $T$ 正规（$TT^*=T^*T$）。
2. $V$ 有 $T$ 的特征向量组成的**标准正交基**。
3. $T$ 有对角矩阵表示（关于某标准正交基）。

**证明思路**（关键一步）：用引理 7.21（$\|Tv\|=\|T^*v\|$）证明"正规算子的特征向量对应特征值的共轭"。然后对维数归纳：找一个特征向量 $e_1$，在 $e_1^\perp$ 上 $T$ 仍正规（不变），递归。

#### 实谱定理（Axler 7.29）

$V$ 是有限维**实**内积空间。$T$ 自伴 ⟺ $V$ 有 $T$ 的特征向量组成的**标准正交基**（且特征值全实）。

**证明思路**：实空间算子不一定有（实）特征值，但**自伴**算子必有——通过复化技巧：先证自伴算子的特征值是实数（$\lambda=\langle Tv,v\rangle/\langle v,v\rangle\in\mathbb{R}$），再用二次型 $\langle Tv,v\rangle$ 的极值找到第一个特征向量，归纳。

> **ML 关联**：协方差矩阵 $\Sigma$ 实对称 → 实谱定理 → PCA 主轴存在、正交、特征值（方差）全实。**Axler 让你确信 PCA 不是数值巧合，而是定理保证。**

### 2.8 正定算子与平方根（Ch 7）

**定义**：$T$ 正定 ⟺ $T$ 自伴且 $\langle Tv,v\rangle>0$（$\forall v\neq0$）。

**定理**：$T$ 正定 ⟺ 所有特征值 $>0$ ⟺ 存在正定算子 $S$ 使 $T=S^2$（平方根）。

> **ML 关联**：(1) 协方差矩阵半正定；(2) Cholesky $\Sigma=LL^*$ 是算子平方根；(3) Hessian 正定 ⟺ 局部极小。

### 2.9 奇异值（Ch 7，Axler 版）★★

Axler **不用 SVD 定理**而是用**奇异值**定义（优雅！）：

**定义**（奇异值）：$T$ 的奇异值 $=$ $\sqrt{T^*T}$ 的特征值（$T^*T$ 正定，有平方根）。

即 $\sigma_i = \sqrt{\lambda_i(T^*T)}$。这与 18.06 的 $A=U\Sigma V^T$ 一致：$T^*T=V\Sigma^2V^*$，奇异值 = $\Sigma$ 对角元。

> **统一**：18.06 从"几何分解 $A=U\Sigma V^T$"定义奇异值；Axler 从"算子结构 $\sqrt{T^*T}$"定义。殊途同归，但 Axler 的定义更"算子内在"。

### 2.10 Ch 8-9：复/实算子的结构定理 & Jordan 形式

- **复**：每个算子有上三角矩阵（关于某基）。若无重特征值则可对角化。
- **实**：分块上三角，$2\times2$ 块对应复特征值对。
- **广义特征向量**与**Jordan 形式**：当几何重数 $<$ 代数重数时，用广义特征向量补全。

> **ML 关联**：Jordan 形式 → 线性动态系统 $\dot{x}=Ax$ 的稳定性（特征值实部 $<0$ 稳定，$2\times2$ 块对应振荡）→ Neural ODE 分析。

### 2.11 行列式与迹（Ch 10，最后才讲！）

Axler 把行列式放到**最后一章**——因为它不是核心工具。

**迹** $=$ 特征值之和：$\text{tr}\,T=\sum\lambda_i$。
**行列式** $=$ 特征值之积：$\det T=\prod\lambda_i$。

Axler 用外形式定义行列式（唯一满足多重线性、交错、$\det I=1$ 的函数）。

---

## 第 3 层：代码层（numpy 验证 Axler 的关键定理）

```python
import numpy as np

# === 验证 1: 复谱定理 —— 正规算子有标准正交特征基 ===
# 构造一个正规矩阵 (Hermitian: T = T*)
T = np.array([[2, 1j], [-1j, 3]])  # Hermitian => 正规
print("T 正规?", np.allclose(T @ T.conj().T, T.conj().T @ T))  # True
eigvals, eigvecs = np.linalg.eigh(T)  # Hermitian 用 eigh
print("特征值全实?", np.allclose(eigvals.imag, 0))             # True (实谱定理)
print("特征向量标准正交?", np.allclose(eigvecs @ eigvecs.conj().T, np.eye(2)))  # True

# === 验证 2: 奇异值 = sqrt(T*T 的特征值) (Axler 定义) ===
A = np.random.randn(4, 3)
# Axler: 奇异值 = sqrt(A^* A) 的特征值
AtA_eigvals = np.linalg.eigvalsh(A.conj().T @ A)  # A^*A 半正定, 用 eigh
axler_sv = np.sqrt(np.sort(AtA_eigvals)[::-1])
numpy_sv = np.linalg.svd(A, compute_uv=False)
print("Axler 奇异值定义 == numpy SVD:", np.allclose(axler_sv, numpy_sv))

# === 验证 3: 正定算子有平方根 (谱定理推论) ===
S = np.random.randn(3, 3); S = S @ S.T  # 正定 (构造)
# 平方根: S = Q Λ Qᵀ -> sqrt(S) = Q sqrt(Λ) Qᵀ  (eigh 返回 特征值,特征向量)
L_eig, Q_eig = np.linalg.eigh(S)
sqrt_S = Q_eig @ np.diag(np.sqrt(L_eig)) @ Q_eig.T
print("sqrt(S)^2 == S?", np.allclose(sqrt_S @ sqrt_S, S))  # True
# 这就是 Cholesky / 协方差分解的数学本质

# === 验证 4: 维数定理 rank + nullity = dim ===
A = np.random.randn(5, 7)
rank = np.linalg.matrix_rank(A)
nullity = 7 - rank  # null(A) 维数
print(f"dim(domain)={7} = rank({rank}) + nullity({nullity})")  # 7 = 7
```

---

## 第 4 层：不足层（Axler 的局限）

1. **不覆盖数值方面**：Axler 证明存在性，但不讲"如何数值稳定地计算 SVD/特征值"（那是 Trefethen & Bau 的领域，见 [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)）。
2. **谱分解只对正规矩阵有效**：非正规矩阵（如一般的非对称矩阵）不能正交对角化，只能 Jordan 化。Axler 在 Ch 8-9 处理，但不如 Hoffman & Kunze 详尽。
3. **侧重有限维**：LADR 几乎不碰无限维（泛函分析），想要 Hilbert 空间理论需另学（MIT 18.102, Lax）。
4. **应用导向弱**：没有 PCA、最小二乘的工程实现（这些在 18.06 / CME 364A 里）。
5. **行列式放最后**：对需要早期用行列式的课程（如微分方程 $\det(\lambda I - A)$）不太方便。

---

## 第 5 层：应用层（ML 公式级对应）

| Axler 概念 | ML 应用 | 公式 |
|---|---|---|
| 维数定理 | 理解 over/under-determined 回归 | $\dim V = \dim\text{null}+\dim\text{range}$ |
| 正交投影 | 最小二乘 / 线性回归 | $P=A(A^TA)^{-1}A^T$ |
| 自伴算子谱定理 | PCA（协方差对角化） | $\Sigma=Q\Lambda Q^T$ |
| 正定算子 + 平方根 | 高斯采样 / Mahalanobis | $\Sigma=LL^T$, $x=\mu+Lz$ |
| 奇异值（$\sqrt{T^*T}$） | SVD → LoRA 低秩 | $\sigma_i=\sqrt{\lambda_i(A^TA)}$ |
| 不变子空间 | LoRA 低秩更新子空间 | $\Delta W\approx BA$, rank-$r$ 子空间 |
| Jordan 形式 | Neural ODE 稳定性 | 特征值实部 $<0$ |

---

## Axler vs Strang：核心差异总表

| 维度 | Strang (MIT 18.06) | **Axler (Berkeley 110)** |
|---|---|---|
| 特征值定义 | $\det(A-\lambda I)=0$ | 不变子空间 + 多项式 |
| 行列式 | 第 5 章（早） | 第 10 章（最后） |
| SVD | 第 7 章（几何 $A=U\Sigma V^T$） | 奇异值 = $\sqrt{T^*T}$ 特征值 |
| 四个子空间 | ★ 核心框架 | 隐含在维数定理中 |
| 风格 | 直觉、应用、图示 | 严格、结构、证明 |
| 适合 | 工程师、ML 实践者 | 数学专业、理论研究者 |
| 配套 | OCW 视频 | Axler 自录讲解 |

**最佳策略**：先用 18.06 建立直觉，再用 110 补证明。两本对照读是线代最稳的学法。

---

## 与 work4ai 讲透系列的交叉

- **讲透 Transformer**：attention $=QK^T$ 的几何 = Axler Ch 6 内积；softmax 不是线性 → 但 linear attention 是投影（Ch 7）。
- **讲透反向传播**：Jacobian 链式法则 = Ch 3 线性映射复合；梯度消失 = 谱半径（Ch 7）。
- **讲透优化器**：正定 Hessian = Ch 7 正定算子；条件数 = 奇异值比（Ch 7）。
- **讲透 LoRA/MRL**：低秩更新 = Ch 5 不变子空间 + Ch 7 奇异值。
