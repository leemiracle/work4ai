# UT Austin M 383E · 费曼三层讲透：数值线性代数

> **教材**：**Trefethen & Bau, *Numerical Linear Algebra*** (SIAM, 1997) ★ — 361 页，ML 工程师最佳数值入门
> **一手核实**：Trefethen & Bau 已知经典教材 ✅；配套 Demmel *Applied Numerical Linear Algebra*
> **课程性质**：UT Austin Numerical Analysis Prelim（研究生资格考试）

---

# 费曼三层讲透：数值线性代数到底在研究什么？

## 🧠 直觉层（1 句话比喻）

| 概念 | 比喻 |
|---|---|
| **LU 分解** | **"高斯消元的矩阵记账法"**——把消元步骤存进 $L$，结果存进 $U$ |
| **QR 分解** | **"把矩阵的列正交化再回头算"**——Gram-Schmidt 的矩阵形式 |
| **SVD** | **"任何矩阵都能拆成旋转-拉伸-旋转"**——$A=U\Sigma V^T$，几何的终极分解 |
| **条件数** | **"输入小扰动→输出大波动的放大倍数"**——$\kappa = \sigma_{\max}/\sigma_{\min}$，越大越病态 |
| **向后稳定性** | **"算的不是原问题，但算的是附近某个问题的精确解"**——算法不放大误差的标志 |
| **Householder** | **"用镜面反射把向量拍成 $e_1$"**——比 Gram-Schmidt 更稳定的正交化 |
| **幂迭代** | **"反复乘 $A$，最大特征值的分量被指数放大"**——PageRank 的原理 |
| **Krylov 子空间** | **"用 $\{b, Ab, A^2b,\dots\}$ 张成的空间逼近解"**——CG/GMRES 的根基 |
| **预条件** | **"先换一个坐标系让矩阵接近单位阵再求解"**——把 $\kappa$ 降下来 |

> **一句话总结**：**数值线代 = "在有限精度浮点数世界里，如何不把误差放大"**。Trefethen & Bau 的核心是区分**问题的敏感性**（条件数）和**算法的质量**（稳定性）——两者正交。

---

## 🧮 数学层（核心定义 + 定理 + LaTeX）

### 1. 三大分解

#### LU 分解
$$PA = LU$$
- $L$：单位下三角（消元乘数），$U$：上三角（消元结果），$P$：置换（行交换）
- **用途**：解 $Ax = b$（分解一次 $O(n^3)$，回代 $O(n^2)$）
- **代价**：$2n^3/3$ flops

#### QR 分解 ★
$$A = QR$$
- $Q$：正交矩阵（$Q^TQ = I$），$R$：上三角
- **Gram-Schmidt 过程**：
  $$q_k = \frac{a_k - \sum_{j<k} r_{jk} q_j}{r_{kk}}, \quad r_{jk} = q_j^T a_k, \quad r_{kk} = \|\cdot\|$$
- **Householder 方法**（更稳定）★：用镜面反射 $H = I - 2vv^T/v^Tv$ 逐步把列清零
- **用途**：最小二乘（$A^TA\hat{x} = A^Tb$ → 解 $R\hat{x} = Q^Tb$，避免 $A^TA$ 的条件数平方）

#### SVD ★★★
$$A = U\Sigma V^T, \quad \sigma_1 \geq \sigma_2 \geq \dots \geq \sigma_r > 0$$
- 几何：$A$ 的作用 = 旋转($V^T$) → 缩放($\Sigma$) → 旋转($U$)
- **Eckart-Young**：$A_k = \sum_{i=1}^k \sigma_i u_i v_i^T$ 是秩 $\leq k$ 最佳近似
- **伪逆**：$A^+ = V\Sigma^+ U^T$（零奇异值取倒数变 0）

### 2. 条件数与稳定性 ★★（Trefethen 的核心洞见）

#### 问题的条件数
$$\kappa(A) = \|A\|\|A^{-1}\| = \frac{\sigma_{\max}}{\sigma_{\min}}$$

**相对误差放大**：若 $\hat{x} = (A+\delta A)^{-1}(b+\delta b)$，则
$$\frac{\|\delta x\|}{\|x\|} \leq \kappa(A)\left(\frac{\|\delta A\|}{\|A\|} + \frac{\|\delta b\|}{\|b\|}\right)$$

> **直觉**：$\kappa \sim 10^k$ 意味着损失约 $k$ 位有效数字。

#### 向后稳定性（算法的性质）★
算法 $\tilde{f}$ **向后稳定**：$\forall x$，$\exists \tilde{x}$ s.t. $\tilde{f}(x) = f(\tilde{x})$ 且 $\|\tilde{x} - x\|/\|x\| = O(\epsilon_{\text{machine}})$。

> **直觉**：算法给出的是**附近某个问题的精确解**，而非原问题的近似解。

**关键结论**：
- 回代（解三角系统）：向后稳定 ✓
- **标准 Gram-Schmidt：不向后稳定** ✗（正交性丢失）
- **修正 Gram-Schmidt（MGS）：向后稳定** ✓
- **Householder QR：向后稳定** ✓✓（首选）
- **Gaussian 消元 + 部分 pivoting：实践中稳定** ✓（理论上有反例）

#### 总误差 = 条件数 × 向后误差
$$\frac{\|\tilde{x} - x\|}{\|x\|} = O(\kappa(A) \cdot \epsilon_{\text{machine}})$$

> **核心教益**：问题病态（$\kappa$ 大）+ 算法稳定，误差仍大；问题良态 + 算法不稳定，误差也大。**两者都要管**。

### 3. 最小二乘的三种解法

| 方法 | 公式 | 条件数 | 推荐 |
|---|---|---|---|
| 正规方程 | $A^TA\hat{x} = A^Tb$ | $\kappa(A)^2$ | ✗ 病态 |
| QR | $R\hat{x} = Q^Tb$ | $\kappa(A)$ | ✓ |
| SVD | $\hat{x} = V\Sigma^+U^Tb$ | $\kappa(A)$ | ✓✓ 最稳健 |

> **ML 关联**：线性回归 `np.linalg.lstsq` 默认用 SVD/Pivot QR，不用正规方程。

### 4. 特征值计算

#### 幂迭代（Power Iteration）
$$v^{(k)} = \frac{A v^{(k-1)}}{\|A v^{(k-1)}\|} \to v_1 \quad (\text{对应 } \sigma_{\max})$$
收敛速率 $|\lambda_2/\lambda_1|^k$。**PageRank** = 幂迭代在 Google 矩阵上。

#### QR 算法 ★
$$A^{(k)} = Q^{(k)}R^{(k)}, \quad A^{(k+1)} = R^{(k)}Q^{(k)}$$
$A^{(k)} \to$ 上三角（特征值在对角线）。**实际**加 Hessenberg 化 + 位移加速。

### 5. 迭代法（Krylov 子空间）★★

对大稀疏矩阵 $A$，不想做 $O(n^3)$ 分解，而是迭代：

#### Krylov 子空间
$$\mathcal{K}_k(A, b) = \text{span}\{b, Ab, A^2b, \dots, A^{k-1}b\}$$

#### 共轭梯度（CG，对称正定）
$$x_k = \arg\min_{x \in \mathcal{K}_k} \|x - x^\star\|_A$$
- $k$ 步内（理论上）精确解；实际 $\lceil\sqrt{\kappa}\rceil$ 步达 $\epsilon$ 精度
- **ML 关联**：CG 用于神经网络的二阶优化（K-FAC, Hessian-free）

#### GMRES（非对称）
$$x_k = \arg\min_{x \in \mathcal{K}_k} \|b - Ax\|$$
- 每步最小化残差；代价 $O(k^2 n)$（需重启）

#### 预条件（Preconditioning）
$$M^{-1}Ax = M^{-1}b \quad (\kappa(M^{-1}A) \ll \kappa(A))$$
- 不完全 Cholesky（IC）、代数多网格（AMG）等

---

## 💻 代码层（numpy 实现）

### 手写 QR（三种方法对比）

```python
import numpy as np

def qr_gram_schmidt(A):
    """经典 Gram-Schmidt (不稳定, 教学用)"""
    m, n = A.shape
    Q = np.zeros((m, n)); R = np.zeros((n, n))
    for k in range(n):
        v = A[:, k].copy()
        for j in range(k):
            R[j, k] = Q[:, j] @ A[:, k]      # 经典 GS: 用 A[:,k]
            v -= R[j, k] * Q[:, j]
        R[k, k] = np.linalg.norm(v)
        Q[:, k] = v / R[k, k]
    return Q, R

def qr_modified_gram_schmidt(A):
    """修正 Gram-Schmidt (向后稳定)"""
    m, n = A.shape
    Q = np.zeros((m, n)); R = np.zeros((n, n))
    V = A.copy().astype(float)
    for k in range(n):
        R[k, k] = np.linalg.norm(V[:, k])
        Q[:, k] = V[:, k] / R[k, k]
        for j in range(k+1, n):
            R[k, j] = Q[:, k] @ V[:, j]       # 修正 GS: 用 V (已更新)
            V[:, j] -= R[k, j] * Q[:, k]
    return Q, R

def qr_householder(A):
    """Householder QR (最稳定, 工业标准)"""
    m, n = A.shape
    R = A.copy().astype(float)
    Q = np.eye(m)
    for k in range(min(m-1, n)):
        x = R[k:, k]
        alpha = -np.sign(x[0]) * np.linalg.norm(x)
        v = x.copy(); v[0] -= alpha
        if np.linalg.norm(v) < 1e-15: continue
        v = v / np.linalg.norm(v)
        R[k:, :] -= 2 * np.outer(v, v @ R[k:, :])   # Householder 反射
        Q[:, k:] -= 2 * np.outer(Q[:, k:] @ v, v)
    return Q, R
```

### 条件数与稳定性可视化

```python
# 生成 Hilbert 矩阵 (经典病态矩阵)
def hilbert(n):
    return 1.0 / (np.arange(1, n+1)[:, None] + np.arange(1, n+1)[None, :] - 1)

for n in [5, 10, 15]:
    H = hilbert(n)
    print(f"Hilbert {n}×{n}: κ = {np.linalg.cond(H):.2e}")
# Hilbert 10×10: κ ~ 1.6e13, 15×15: κ ~ 6e17 → 基本不可解
```

### SVD 与 PCA

```python
def pca_svd(X, k):
    """PCA 通过 SVD: 中心化 → SVD → 取前 k 个右奇异向量"""
    Xc = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    components = Vt[:k]          # 主成分方向
    projected = Xc @ components.T # 投影
    explained_var = (S**2) / (len(X) - 1)
    return components, projected, explained_var
```

### 共轭梯度法

```python
def conjugate_gradient(A, b, x0=None, max_iter=1000, tol=1e-8):
    """CG 解对称正定系统 Ax = b"""
    x = np.zeros_like(b) if x0 is None else x0.copy()
    r = b - A @ x
    p = r.copy()
    rsold = r @ r
    for i in range(max_iter):
        Ap = A @ p
        alpha = rsold / (p @ Ap)
        x += alpha * p
        r -= alpha * Ap
        if np.linalg.norm(r) < tol:
            break
        rsnew = r @ r
        p = r + (rsnew / rsold) * p   # 共轭方向更新
        rsold = rsnew
    return x, i + 1
```

---

## ⚠️ 不足层（局限）

| 局限 | 说明 |
|---|---|
| **LU 在病态矩阵上失败** | 即使向后稳定，$\kappa \sim 10^{16}$ 时结果全噪声（Hilbert 矩阵）|
| **QR 算法对非对称矩阵收敛慢** | 需 Hessenberg 化 + QR 位移，否则迭代次数爆炸 |
| **幂迭代只能求最大特征值** | 要全部特征值用 QR 算法；要中间特征值用 Lanczos |
| **CG 要求对称正定** | 非对称用 GMRES，但 GMRES 内存 $O(kn)$ 需重启 |
| **稀疏矩阵分解有 fill-in** | Cholesky 填充问题，需带宽/嵌套剖分排序 |
| **预条件是艺术** | 好的预条件子 $M$ 难找，问题依赖 |
| **SVD 代价 $O(\min(mn^2, m^2n))$** | 大矩阵用随机化 SVD（Halko-Martinsson-Tropp 2011）|

---

## 🔬 应用层（ML 公式级对应）

### 1. SVD → PCA / Transformer 低秩 / LoRA
$$X = U\Sigma V^T \quad \Rightarrow \quad X_k = U_k\Sigma_k V_k^T \quad \text{(Eckart-Young)}$$
- PCA：协方差矩阵 $X^TX$ 的特征向量 = $V$
- **LoRA**：$W \approx BA$（$B \in \mathbb{R}^{m \times r}, A \in \mathbb{R}^{r \times n}$），$r \ll \min(m,n)$
- 推荐：Netflix Prize 用截断 SVD

### 2. 数值稳定性 → PyTorch 算子设计
- **log-sum-exp trick**：$\log\sum e^{x_i} = c + \log\sum e^{x_i - c}$，$c = \max x_i$（避免上溢）
- **stable softmax**：`softmax(x) = softmax(x - max(x))`
- **GELU / LayerNorm** 用数值稳定公式

### 3. 幂迭代 → PageRank
$$r_{k+1} = \alpha M r_k + (1-\alpha)\frac{\mathbf{1}}{n}$$
$M$ = 列归一化邻接矩阵，$\alpha \approx 0.85$。幂迭代 $O(\text{nnz})$ 每步。

### 4. Krylov → Attention 加速
线性 attention 用核技巧把 $O(n^2)$ 变 $O(n)$，本质是在 Krylov 子空间里近似。

### 5. CG → 二阶神经网络优化
Hessian-free 优化（Martens 2010）用 CG 解 $H p = -\nabla f$ 而不求 $H^{-1}$。

### 6. 随机化 SDE → 随机化 SVD（[0909.4061](https://arxiv.org/abs/0909.4061) ✅）
用随机投影 $Q = \text{orth}(A \Omega)$ 把 $m \times n$ 矩阵降到 $m \times (k+p)$，再小 SVD。代价 $O(mnk)$ vs $O(mn\min(m,n))$。

---

## 📚 章节结构对照（Trefethen & Bau）

| 讲 | 主题 | 重要性 |
|---|---|---|
| 1-5 | 基础（矩阵-向量乘、正交、范数）| ★★ |
| 6-8 | **QR 分解**（GS, Householder, Givens）| ★★★ |
| 9-12 | **条件数与稳定性** | ★★★ |
| 13 | **LU 分解** | ★★ |
| 14-15 | **SVD** | ★★★ |
| 16-18 | 特征值计算（QR 算法）| ★★ |
| 20-22 | **迭代法**（CG, GMRES, Arnoldi）| ★★★ |
| 23-25 | 预条件与其他 | ★★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透反向传播的数值稳定性**：第 9-12 章（log-sum-exp / softmax）
- **讲透 Transformer 低秩**：第 14-15 章（SVD + Eckart-Young）
- **讲透 PCA**：第 15 章（SVD）
- **讲透 PageRank**：第 16 章（幂迭代）
