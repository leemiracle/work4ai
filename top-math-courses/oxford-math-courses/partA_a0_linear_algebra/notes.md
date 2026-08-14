# Oxford Part A A0 · 费曼三层笔记（线代深化）

> **教材**：Oxford 自编讲义 + Axler LADR（配）
> **特色**：**Year 2 核心**——把 Prelims M1 升级到**对偶空间、Jordan 标准型、双线性形式、对称矩阵谱理论**。与 Berkeley 110 / Princeton 217 同深度，Oxford 的几何/公理化味道更浓。
> **后续衔接**：Part C C7.1 随机矩阵理论（LLM 权重谱分析的直接数学基础）。

---

## 总览：A0 在 Oxford 体系的角色

| 主题 | A0 的深度 | 衔接 |
|---|---|---|
| 对偶空间 $V^*$ | 完整（零化子、对偶映射） | 核方法、表示论 |
| Jordan 标准型 | 广义特征向量 + 极小多项式 | Neural ODE/RNN |
| 双线性/二次型 | Sylvester 惯性 + 合同 | Hessian/SVM |
| 谱理论（对称） | 完整实谱定理 | PCA/协方差 |

---

## 第 1 层：直觉层（一句话比喻）

> **对偶空间** = "所有'用坐标测量向量'的尺子的集合——每个尺子给出一个坐标值。"
> **Jordan 标准型** = "不能对角化的矩阵，退而求其次的最简形状。"
> **合同（双线性形式换基）** = "换个坐标系看同一个二次曲面，形状不变——但相似（算子换基）会变形。"
> **Oxford A0 的哲学** = "Prelims 教了'怎么算'，A0 教'结构是什么'——对偶、Jordan、惯性都是结构层面的洞察。"

---

## 第 2 层：数学层（定义 + 定理 + LaTeX）

### 2.1 对偶空间 $V^*$ ★

**定义**：$V^*=\mathcal{L}(V,\mathbb{F})$，所有线性泛函 $f:V\to\mathbb{F}$。$\dim V^*=\dim V$。

**对偶基**：$e^i(e_j)=\delta^i_j$。若基矩阵 $B=[e_j]$，对偶基矩阵 $=B^{-T}$。

**零化子** $S^0=\{f\in V^*:f|_S=0\}$。$\dim S^0=\dim V-\dim S$。

**对偶映射** $T^*:W^*\to V^*$，$(T^*f)(v)=f(Tv)$。性质：$\ker T^*=(\text{im}\,T)^0$。

> **ML 关联**：Riesz 表示 → 核方法 $f(\mathbf{x})=\sum\alpha_iK(\mathbf{x}_i,\mathbf{x})$；梯度是对偶向量。

### 2.2 特征值、不变子空间、Jordan 标准型 ★★

**不变子空间** $W$：$T(W)\subseteq W$。

**广义特征向量**：$(T-\lambda I)^k v=0$。**广义特征空间** $G(\lambda)=\ker(T-\lambda I)^n$。

**Jordan 定理**（复）：$V=\bigoplus_\lambda G(\lambda)$，$T|_{G(\lambda)}$ 有 Jordan 形式 $\bigoplus J_{m_i}(\lambda)$。

**极小多项式** $m_T(x)$：$\lambda$ 的 Jordan 块最大尺寸 $=$ $m_T$ 中 $\lambda$ 的重数。

> **ML 关联**：$e^{Jt}$ 含 $t^{k-1}e^{\lambda t}$，Jordan 块尺寸 → 多项式增长 → RNN/Neural ODE 稳定性。

### 2.3 双线性形式与二次型 ★（A0 重点）

**双线性形式** $B:V\times V\to\mathbb{F}$。矩阵 $A$：$B(u,v)=u^TAv$。换基 → **合同** $A\mapsto P^TAP$（非相似）。

**对称双线性形式**（$B=B^T$）：可对角化（合同意义），对角元符号分类。

**Sylvester 惯性律**：合同下，对角化后 $+/0/-$ 个数 $(p,r,q)$ 不变。

**二次型** $q(v)=B(v,v)$。**配极化**恢复 $B$：$B(u,v)=\frac12[q(u+v)-q(u)-q(v)]$。

> **ML 关联**：
> - Hessian 惯性 $(p,q,0)$ → 临界点类型（全正=极小，有负=鞍点）。
> - SVM 对偶 = 半正定二次规划。
> - Mahalanobis 距离用正定 $\Sigma^{-1}$。

### 2.4 内积空间与谱定理 ★

**伴随** $T^*$：$\langle Tu,v\rangle=\langle u,T^*v\rangle$。

**实谱定理**：$T$ 自伴（$T=T^*$）⟺ 有标准正交特征基，特征值全实。

$$A=A^T\ \Longleftrightarrow\ A=Q\Lambda Q^T,\quad Q^TQ=I,\ \Lambda\text{ 对角实}$$

> **ML 关联**：协方差 $\Sigma=\frac1nX^TX$ 自伴半正定 → 谱定理 → PCA 主轴存在、正交、方差非负。**A0 让你确信 PCA 不是数值巧合而是定理保证。**

### 2.5 正定算子与平方根

$A$ 正定 ⟺ 特征值 $>0$ ⟺ $\exists S$ 使 $A=S^2$（$S$ 正定）。

**Cholesky** $\Sigma=LL^T$：正定矩阵的"平方根"。→ 生成相关高斯 $x=\mu+Lz$（$z$ 标准正态）。

---

## 第 3 层：代码层（numpy 验证对偶/Jordan/惯性）

```python
import numpy as np

# === 对偶基: B^{-T} ===
B = np.array([[1, 1], [0, 2.0]])  # 基向量列
Binv = np.linalg.inv(B)
dual = Binv.T  # 对偶基
print(f"对偶基 × 原基 = I? {np.allclose(dual.T @ B, np.eye(2))}")

# === Jordan: 不可对角化 ===
A = np.array([[4, 1], [0, 4.0]])  # J_2(4)
ew, ev = np.linalg.eig(A)
print(f"λ={ew}, 特征向量矩阵秩={np.linalg.matrix_rank(ev)} (<2 → 不可对角化, Jordan块)")

# === Sylvester 惯性: 合同保持惯性 ===
S = np.diag([3, -1, 2.0])  # 惯性 (2,1,0)
P = np.array([[1,1,0],[0,1,1],[1,0,1.0]])  # 可逆换基
cong = P.T @ S @ P
eb = np.linalg.eigvalsh(S); ec = np.linalg.eigvalsh(cong)
print(f"惯性: 前(+{np.sum(eb>0)},{np.sum(eb<0)}) 后(+{np.sum(ec>0)},{np.sum(ec<0)}) (Sylvester)")

# === 配极化: 二次型 → 双线性 ===
A = np.array([[2, 1], [1, 3.0]])
def q(x): return x @ A @ x
u, v = np.array([1, 0.0]), np.array([0, 1.0])
B_uv = 0.5*(q(u+v) - q(u) - q(v))
print(f"配极化 B(e1,e2)={B_uv} (应=A[0,1]=1)")

# === 实谱定理 + 正定平方根 ===
Sigma = np.random.randn(3,3); Sigma = Sigma @ Sigma.T  # 对称正定
L, Q = np.linalg.eigh(Sigma)  # eigh 返回 (特征值, 特征向量)!
print(f"对称? {np.allclose(Sigma, Sigma.T)}, 特征值>0? {np.all(L>0)}")
sqrt_Sigma = Q @ np.diag(np.sqrt(L)) @ Q.T
print(f"(√Σ)²=Σ? {np.allclose(sqrt_Sigma@sqrt_Sigma, Sigma)} (Cholesky 的本质)")
```

---

## 第 4 层：不足层

1. **Jordan 数值病态**：理论标准型，计算用 Schur（见数值分析课）。
2. **不覆盖随机矩阵**：LoRA 统计理论需 Part C C7.1（Marchenko-Pastur）。
3. **不覆盖 SVD 算法**：SVD 的数值实现需数值分析。
4. **有限维**：无限维泛函需研究生课。

---

## 第 5 层：应用层（ML 公式级对应）

| A0 概念 | ML 应用 | 公式 |
|---|---|---|
| 对偶空间 + Riesz | 核方法 | $f(\mathbf{x})=\sum\alpha_iK(\mathbf{x}_i,\mathbf{x})$ |
| Jordan 标准型 | RNN/Neural ODE 稳定性 | $e^{Jt}$ 多项式-指数项 |
| 二次型惯性 | Hessian 凸性 / SVM | $(p,q,r)$ 惯性 |
| 实谱定理 | PCA / 协方差 | $\Sigma=Q\Lambda Q^T$ |
| 正定 + 平方根 | 高斯采样 / Mahalanobis | $\Sigma=LL^T$, $x=\mu+Lz$ |
| 合同变换 | 坐标无关优化 | $P^TAP$ |

---

## 进阶：通向 LoRA 的数学（A0 → Part C C7.1）

A0 的谱理论 + 奇异值是 **LoRA/QLoRA 低秩微调**的直接数学根基：
- LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）：$W=W_0+BA$（低秩更新），根基 = Eckart-Young + 谱理论。
- QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）：4-bit 量化 + 低秩适配器。
- Part C C7.1 随机矩阵：Marchenko-Pastur 律区分权重的"信号/噪声"奇异值，为选秩 $r$ 提供理论。

---

## 与 work4ai 讲透系列的交叉

- **讲透优化器**：二次型惯性 → Hessian → 凸性 → 收敛速率。
- **讲透 PCA**：实谱定理 → 协方差对角化。
- **讲透 RNN**：Jordan 形式 → 梯度流的谱衰减。
- **讲透 LoRA/MRL**：A0 谱理论 + 奇异值 → 低秩近似的数学。
