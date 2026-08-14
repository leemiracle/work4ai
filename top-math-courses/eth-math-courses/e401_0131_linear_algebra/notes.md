# ETH 401-0131 · 费曼三层笔记（线代，工学院版）

> **教材**：Strang *Introduction to Linear Algebra* 6th ed（主）+ Fischer *Lineare Algebra*（德，辅）
> **特色**：**ETH D-MATH 工学院线代**——与 MIT 18.06 同用 Strang 教材，但 ETH 欧洲风格多一份严谨：**复数与范数早期引入**、强调**数值稳定性**（QR vs normal equation）、工程传统（特征值 = 振动模态）。
> **后续**：ETH 数值方法（401-2611）/ 凸优化（401-3904）/ SDE 数值（401-3651）全建立在此之上。

---

## 总览：ETH 线代的工程视角

| 主题 | Strang 直觉 | ETH 加深的严谨 |
|---|---|---|
| 复数 | 简略 | ★ 早期引入（欧拉传统）|
| 范数/条件数 | 提及 | ★ 数值稳定性核心 |
| LU/QR | 计算 | ★ QR 比 normal eq 更稳 |
| 特征值 | PCA | ★ 振动模态（结构工程）|
| SVD | 低秩 | ★ 数据压缩工程实现 |

---

## 第 1 层：直觉层（一句话比喻）

> **范数** = "衡量向量'大小'的尺子"——不同范数看不同侧面（$\ell^1$=出租车距离，$\ell^2$=直线，$\ell^\infty$=最大坐标）。
> **条件数** = "线性系统的'敏感度'——输入抖一抖，输出抖几倍。"
> **QR 比 normal equation 稳** = "正交变换不放大误差，但 $A^TA$ 把条件数平方（放大误差）。"
> **特征值 = 振动频率** = "桥梁/建筑的固有频率——共振 = 特征值匹配外力频率。"
> **ETH 的哲学** = "Strang 教你看见矩阵，ETH 教你算得稳——工程师既要直觉，也要数值可靠。"

---

## 第 2 层：数学层（定义 + 定理 + LaTeX）

### 2.1 复数（ETH 早期引入）

$z=a+bi=re^{i\theta}$，欧拉公式 $e^{i\theta}=\cos\theta+i\sin\theta$。

复矩阵的 Hermitian 转置 $A^*=\bar A^T$。酉矩阵 $U^*U=I$。

> **ML 关联**：复特征值 = 振荡模式（RNN/Neural ODE）；傅里叶变换 = 复矩阵。

### 2.2 范数与条件数 ★（ETH 核心）

**向量范数**：$\|\mathbf{v}\|_p=(\sum|v_i|^p)^{1/p}$。$\ell^1,\ell^2,\ell^\infty$。

**矩阵范数**：$\|A\|_2=\sigma_{\max}(A)$（谱范数）。

**条件数**：$\kappa(A)=\frac{\sigma_{\max}}{\sigma_{\min}}$。

**扰动界**：$\frac{\|\Delta\mathbf{x}\|}{\|\mathbf{x}\|}\leq\kappa(A)\frac{\|\Delta\mathbf{b}\|}{\|\mathbf{b}\|}$。

> **ML 关联**：$\kappa$ 大 → 梯度下降慢（需小学习率）；BatchNorm/LayerNorm 降低激活矩阵条件数。

### 2.3 LU 分解

$A=LU$（$L$ 下三角，$U$ 上三角）。带置换 $PA=LU$。

**复杂度**：$O(n^3)$ 但常数小。

### 2.4 QR 与最小二乘 ★（ETH 数值重点）

$A=QR$（Gram-Schmidt 或 Householder）。

**最小二乘**：$A\hat{\mathbf{x}}\approx\mathbf{b}$。
- **Normal equation** $A^TA\hat{\mathbf{x}}=A^T\mathbf{b}$：简单但 $\kappa(A^TA)=\kappa(A)^2$（条件数平方，数值不稳）。
- **QR 方法** $R\hat{\mathbf{x}}=Q^T\mathbf{b}$：$\kappa$ 不平方，**数值稳定**。✓ ETH 推荐。

> **ML 关联**：岭回归 $\hat{x}=(A^TA+\lambda I)^{-1}A^Tb$ 加 $\lambda I$ 改善条件数（正则化）。

### 2.5 特征值与振动模态 ★（ETH 工程传统）

弹性结构 $K\mathbf{x}=\omega^2M\mathbf{x}$（广义特征值问题）。特征值 $\omega^2$ = 固有频率²，特征向量 = 振型。

**共振**：外力频率 $\approx\omega_i$ → 振幅爆炸。

> **ML 关联**：训练动态的"共振"（学习率匹配损失景观曲率 = 特征值）。

### 2.6 SVD 与低秩近似 ★

$A=U\Sigma V^T$。Eckart-Young：$A_k=\sum_{i=1}^k\sigma_iu_iv_i^T$ 最优秩-$k$ 近似。

> **ML 关联**：PCA = 数据 SVD；**LoRA** $W_0+BA$ = 权重增量的低秩近似（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）；**QLoRA**（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）4-bit 量化 + 低秩。

### 2.7 谱定理（对称矩阵）

$A=A^T$ ⟹ $A=Q\Lambda Q^T$，特征值实，特征向量正交。

---

## 第 3 层：代码层（numpy 验证条件数/QR/SVD）

```python
import numpy as np

# === 条件数: 病态系统 ===
A = np.array([[1, 1], [1, 1.0001]])  # 近似奇异
kappa = np.linalg.cond(A)
print(f"条件数 κ(A)={kappa:.0f} (病态: 输入抖1e-4 → 输出抖~κ倍)")
b = np.array([2, 2]); b2 = np.array([2, 2.0001])
x1 = np.linalg.solve(A, b); x2 = np.linalg.solve(A, b2)
print(f"b 微扰 → x 从 {np.round(x1,3)} 变到 {np.round(x2,3)} (放大~κ倍)")

# === QR vs Normal Equation 数值稳定性 ===
np.random.seed(0)
A = np.random.randn(5, 3) + 1e-6*np.random.randn(5,3)  # 列近似相关
b = np.random.randn(5)
# Normal equation
x_normal = np.linalg.solve(A.T@A, A.T@b)
# QR
Q, R = np.linalg.qr(A)
x_qr = np.linalg.solve(R, Q.T@b)
print(f"Normal vs QR 差: {np.linalg.norm(x_normal-x_qr):.2e} (QR 更稳)")

# === SVD 低秩近似 (LoRA 数学) ===
W = np.random.randn(100, 80)
U, S, Vt = np.linalg.svd(W, full_matrices=False)
r = 5  # LoRA 秩
W_lowrank = U[:,:r] @ np.diag(S[:r]) @ Vt[:r,:]  # Eckart-Young 最优
err = np.linalg.norm(W - W_lowrank, 'fro') / np.linalg.norm(W, 'fro')
print(f"秩-{r} 近似相对误差: {err:.2%}")
print(f"参数压缩: {100*80} → {r*(100+80)} ({100*80/(r*(100+80)):.0f}x)")

# === 对称矩阵谱定理 ===
S = np.random.randn(4,4); S = (S+S.T)/2
L, Q = np.linalg.eigh(S)  # eigh 返回 (特征值, 特征向量)!
print(f"对称谱定理: QΛQᵀ=S? {np.allclose(Q@np.diag(L)@Q.T, S)}, 特征值实? {np.allclose(L.imag,0)}")
```

---

## 第 4 层：不足层

1. **理论证明弱于 Oxford/Cambridge**：ETH 重计算/应用，纯数学严格性不如 Axler 路线。
2. **不覆盖随机矩阵**：LoRA 统计理论需 Oxford C7.1。
3. **Jordan 形式简略**：Strang 不深讲 Jordan（偏应用）。
4. **不深究抽象代数**：对偶/张量/商空间不在工学院线代范围。

---

## 第 5 层：应用层（ML/工程公式级对应）

| ETH 概念 | 应用 | 公式 |
|---|---|---|
| 条件数 $\kappa$ | 训练稳定性 / 正则化 | $\kappa=\sigma_{\max}/\sigma_{\min}$ |
| QR（稳定最小二乘） | 稳健回归 | $R\hat{x}=Q^Tb$ |
| 特征值（振动） | 结构共振 / 训练动态 | $Kx=\omega^2Mx$ |
| SVD + Eckart-Young | PCA / LoRA 低秩 | $W_0+BA$ |
| 谱定理 | 协方差 / PCA | $\Sigma=Q\Lambda Q^T$ |
| 复特征值 | 振荡/Neural ODE | $\lambda=a\pm bi$ |

---

## ETH 工程体系全景

```
401-0131 线代 (本课) ──┬──▶ 401-2611 数值方法 CSE (Quarteroni)
                       ├──▶ 401-3904 凸优化 (Boyd/Bubeck)
                       ├──▶ 401-3651 SDE 数值 (Kloeden&Platen)
                       └──▶ ETH 数据科学 / 金融数学
```

ETH 的招牌是**应用数学欧洲顶级**——线代是其基石，后续数值/优化/SDE 全建立在线代的 LU/QR/SVD 之上。

---

## 与 work4ai 讲透系列的交叉

- **讲透优化器**：条件数 → 收敛速率；正定 Hessian → 凸性。
- **讲透 PyTorch**：矩阵算子 = LU/QR/SVD 的数值实现。
- **讲透 LoRA/MRL**：SVD 低秩近似 = LoRA 的全部数学。
- **讲透数值稳定**：QR vs normal equation → BatchNorm/LayerNorm 的动机。
