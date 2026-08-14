# Cambridge Part IB Linear Algebra · 费曼三层笔记

> **教材**：Blyth & Robertson *Basic Linear Algebra*；Cameron *Linear Algebra*
> **特色**：**Cambridge Tripos 风格**——Michaelmas 学期 24 讲，从向量空间极速推到 Jordan 标准型、对偶空间、双线性/二次型。节奏全英最快，覆盖最深。
> **与 Princeton 217 的区别**：Part IB 节奏更快（一学期），但深度相当；Cambridge 用 Tripos 试题驱动，强调"考试级熟练"。

---

## 总览：Part IB 的 24 讲地图

| 讲次 | 主题 | Cambridge 侧重点 |
|---|---|---|
| 1-4 | 向量空间、基、维数 | 公理化 + 快速 |
| 5-8 | 线性映射、矩阵、秩 | 维数定理的多种证法 |
| 9-11 | 行列式 | 外形式/置换定义 |
| 12-16 | 特征值、对角化 | **三角化 + 可对角化判据** |
| 17-19 | **Jordan 标准型** ★ | 广义特征向量 + 极小多项式 |
| 20-22 | 双线性/二次型 | **Sylvester 惯性律 + 配极化** |
| 23-24 | 内积空间、对偶 | **Riesz 表示 + 伴随** |

---

## 第 1 层：直觉层（一句话比喻）

> **Jordan 标准型** = "不能对角化的矩阵，能化简到的最简单形状——对角线上有特征值，对角线上方可能有 1。"
> **极小多项式** = "让矩阵归零的最低次多项式——它告诉你 Jordan 块的最大尺寸。"
> **对偶空间** = "所有'用坐标测量向量'的方法的集合。"
> **二次型的惯性** = "换个坐标系，二次曲面的'凸/凹方向'个数不变。"
> **Cambridge 的哲学** = "24 讲讲完别人一年的内容——靠的是 Tripos 的考试压力和抽象的早入场。"

---

## 第 2 层：数学层（定义 + 定理 + 证明思路 + LaTeX）

### 2.1 向量空间与维数

标准公理化。**维数良定义**：所有基元素数相同（Steinitz 替换法证明）。

### 2.2 线性映射与矩阵

$T:V\to W$。**维数定理**：$\dim V=\dim\ker T+\dim\text{im}\,T$。

**秩** $r(T)=\dim\text{im}\,T$。矩阵的行秩 = 列秩 $=$ 秩。

### 2.3 行列式

Cambridge 两种定义并行：
- **公理化**（多重线性 + 交错 + $\det I=1$）；
- **置换公式** $\det A=\sum_\sigma\text{sgn}(\sigma)\prod_i a_{i\sigma(i)}$。

**乘积** $\det(AB)=\det A\det B$。

### 2.4 特征值与三角化 ★

**上三角化定理**（Cambridge 重点）：复矩阵 $A$ 必相似于上三角 $A=UTU^{-1}$（$T$ 上三角，对角元 = 特征值）。

**证明思路**：对维数归纳。$A$ 有特征向量 $\mathbf{v}_1$（复域必有），取 $U_1=\text{span}(\mathbf{v}_1)$，商空间 $V/U_1$ 上诱导算子上三角化（归纳），提升回 $V$。

**可对角化判据**：$A$ 可对角化 ⟺ 极小多项式无重根 ⟺ 几何重数 = 代数重数（每个特征值）。

### 2.5 Jordan 标准型 ★★★（Part IB 高潮）

**广义特征向量**：$(A-\lambda I)^k\mathbf{v}=0$。

**Jordan 块** $J_m(\lambda)$：$m\times m$，$\lambda$ 对角 + 上次对角 1。

**Jordan 定理**：复 $A$ 相似于 $J=\bigoplus J_{m_i}(\lambda_i)$。

**用极小多项式判定 Jordan 块尺寸**：$\lambda$ 的 Jordan 块最大尺寸 $=$ $\lambda$ 在极小多项式中的重数。

**例**：若极小多项式 $m(x)=(x-2)^2(x-3)$，则 $\lambda=2$ 的 Jordan 块最大 $2\times2$，$\lambda=3$ 的块都是 $1\times1$（可对角化部分）。

> **ML 关联**：RNN/Neural ODE 稳定性。$e^{Jt}$ 含 $t^{k-1}e^{\lambda t}$ 项，Jordan 块尺寸决定多项式增长程度。

### 2.6 双线性形式与二次型 ★（Part IB 特色）

**双线性形式** $B:V\times V\to\mathbb{F}$。矩阵 $A$：$B(\mathbf{u},\mathbf{v})=\mathbf{u}^TA\mathbf{v}$。

**合同** $A\mapsto P^TAP$（换基）。

**Sylvester 惯性律**：实对称双线性形式在合同下，对角化后 $+/-/0$ 个数不变，记 $(p,q,r)$。

**配极化**（polarization）：从二次型 $q(\mathbf{x})=B(\mathbf{x},\mathbf{x})$ 恢复双线性形式：
$$B(\mathbf{u},\mathbf{v})=\frac12[q(\mathbf{u}+\mathbf{v})-q(\mathbf{u})-q(\mathbf{v})]$$

> **ML 关联**：Hessian 惯性 $(p,q,r)$ → 临界点类型；SVM 半正定二次规划。

### 2.7 内积空间、伴随、谱定理

**伴随** $T^*$：$\langle T\mathbf{u},\mathbf{v}\rangle=\langle\mathbf{u},T^*\mathbf{v}\rangle$。

**实谱定理**：$A=A^T$ ⟺ $A=Q\Lambda Q^T$（$Q$ 正交）。

**Riesz 表示定理**：内积空间每个线性泛函 $f$ = $\langle\cdot,\mathbf{v}\rangle$（唯一 $\mathbf{v}$）。

> **ML 关联**：Riesz → 核方法 $f(\mathbf{x})=\sum\alpha_iK(\mathbf{x}_i,\mathbf{x})$。

### 2.8 对偶空间 $V^*$

$V^*=\{\text{线性泛函}\}$。$\dim V^*=\dim V$。对偶基 $e^i(e_j)=\delta^i_j$。

**零化子** $S^0=\{f\in V^*:f(\mathbf{s})=0,\forall\mathbf{s}\in S\}$。$\dim S^0=\dim V-\dim S$。

> 双对偶 $V^{**}\cong V$（自然同构，有限维）。

---

## 第 3 层：代码层（numpy 验证 Jordan / 惯性 / 伴随）

```python
import numpy as np

# === Jordan 形式: 不可对角化矩阵 ===
A = np.array([[3, 1, 0], [0, 3, 1], [0, 0, 3]])  # J_3(3) 本身
ew, ev = np.linalg.eig(A)
print(f"特征值: {ew} (三重 λ=3)")
print(f"特征向量矩阵秩: {np.linalg.matrix_rank(ev)} (< 3 => 不可对角化 => Jordan块)")

# === 极小多项式 vs 特征多项式 ===
# A=J_3(3): 特征多项式 (λ-3)^3, 极小多项式 (λ-3)^3 (最大块3×3)
# 若 A=diag(3, J_2(3)): 特征 (λ-3)^3, 极小 (λ-3)^2
B = np.array([[3, 0, 0], [0, 3, 1], [0, 0, 3]])  # diag(3, J_2(3))
# 验证 (B-3I)^2=0 但 (B-3I)≠0
print(f"(B-3I)^2=0? {np.allclose(np.linalg.matrix_power(B-3*np.eye(3),2), 0)}")  # True

# === Sylvester 惯性律 (合同保持惯性) ===
S = np.diag([2, -1, 3.0])  # 惯性 (2,1,0)
P = np.random.randn(3, 3)
cong = P.T @ S @ P  # 合同
eb = np.linalg.eigvalsh(S); ec = np.linalg.eigvalsh(cong)
print(f"合同前惯性: (+{np.sum(eb>0)}, {np.sum(eb<0)})")
print(f"合同后惯性: (+{np.sum(ec>0)}, {np.sum(ec<0)})  (应相同)")

# === 配极化: 从二次型恢复双线性形式 ===
def q(x):  # q(x) = x^T A x, A=[[2,1],[1,2]]
    return 2*x[0]**2 + 2*x[0]*x[1] + 2*x[1]**2
u, v = np.array([1.0, 0]), np.array([0.0, 1])
B_uv = 0.5*(q(u+v) - q(u) - q(v))  # 配极化
print(f"配极化 B(e1,e2)={B_uv} (应=1, 即 A_12)")
```

---

## 第 4 层：不足层

1. **Jordan 数值病态**：理论标准型，但微小扰动改变结构（实际用 Schur）。
2. **Tripos 考试导向**：偏"技巧性证明"，工程应用（PCA/SVD 实现）弱。
3. **不讲随机/统计**：LoRA 统计理论需 Oxford C7.1 / 概率课。

---

## 第 5 层：应用层（ML 公式级对应）

| Part IB 概念 | ML 应用 | 公式 |
|---|---|---|
| Jordan 标准型 | RNN/Neural ODE 稳定性 | $e^{Jt}$ 多项式-指数项 |
| 极小多项式 | 矩阵幂结构 | Jordan 块最大尺寸 |
| 谱定理 | PCA / 协方差 | $\Sigma=Q\Lambda Q^T$ |
| 二次型惯性 | Hessian / SVM 凸性 | $(p,q,r)$ |
| 对偶 + Riesz | 核方法 | $f(\mathbf{x})=\sum\alpha_iK(\mathbf{x}_i,\mathbf{x})$ |
| SVD（隐含） | LoRA 低秩 | $W_0+BA$ |

---

## 与 work4ai 讲透系列的交叉

- **讲透 RNN**：Jordan 形式 → 梯度 $\prod W^T$ 的谱衰减（BPTT）。
- **讲透 Neural ODE**：$e^{At}$ + 特征值实部 → 稳定性。
- **讲透 SVM**：二次型半正定 → 对偶凸规划。
- **讲透 LoRA/MRL**：对偶/不变子空间 → 低秩更新的数学框架。
