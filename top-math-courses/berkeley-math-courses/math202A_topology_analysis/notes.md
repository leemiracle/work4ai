# Berkeley MATH 202A · 章节笔记（Lang / Knapp / Axler）

> **教材**：Lang *Real and Functional Analysis*；Knapp *Basic Real Analysis*；Axler *MIRA*
> **来源**：Prof. Rieffel 2024 Fall 讲义
> **特色**：**研究生数学入门票**——拓扑 + 实分析 + 泛函融合

---

# 费曼三层讲透：从度量空间到泛函分析

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **拓扑空间** | **"有近邻概念但可能没尺子"**：只知道"近"，不知道"多近" |
| **Banach 空间** | **"完备的赋范空间"**：有长度 + Cauchy 列收敛 |
| **Hilbert 空间** | **"有内积的完备空间"**：有长度 + 有角度 + Cauchy 收敛 |
| **RKHS** | **"能'点取值'的 Hilbert 空间"**：$f(x) = \langle f, k_x \rangle$ |
| **有界算子** | **"有限放大的变换"**：$\|Tx\| \leq M\|x\|$ |

---

## 🧮 数学层

### 拓扑空间

$(X, \tau)$：$\tau$ 是开集族（任意并 + 有限交封闭）。

**连续映射**：开集的原像是开集（比 ε-δ 更抽象）。

### 完备化定理

任何度量空间 $(X, d)$ 可以完备化为 $(\hat{X}, \hat{d})$，使 $X$ 在 $\hat{X}$ 中稠密。

**例子**：$\mathbb{Q}$ 的完备化 = $\mathbb{R}$。

### Banach 空间 ★

赋范空间 $(X, \|\cdot\|)$ 完备。

**压缩映射原理**：$T: X \to X$, $\|Tx-Ty\| \leq q\|x-y\|$, $q < 1$ → 唯一不动点。

**ML 应用**：梯度下降 $\theta_{k+1} = T(\theta_k) = \theta_k - \eta\nabla L(\theta_k)$ 的收敛分析。

### Hilbert 空间 ★

内积空间 $(\mathcal{H}, \langle \cdot, \cdot \rangle)$ 完备。

**正交投影**：$x = x_\parallel + x_\perp$（到闭子空间）

**Riesz 表示定理**：$f \in \mathcal{H}^* \implies \exists! y \in \mathcal{H}: f(x) = \langle x, y \rangle$

**ML 应用**：RKHS → 核方法。

### $L^p$ 空间 ★

$L^p(\mu) = \{f : \int |f|^p \, d\mu < \infty\}$，范数 $\|f\|_p = (\int |f|^p)^{1/p}$。

**对偶**：$(L^p)^* = L^q$（$1/p + 1/q = 1$, $1 < p < \infty$）。

### 4 种收敛模式 ★★★

$$\boxed{L^p \Rightarrow \text{依概率} \Rightarrow \text{依分布}; \quad \text{a.s.} \Rightarrow \text{依概率}}$$

| 模式 | 定义 | 蕴含 |
|---|---|---|
| **依分布** | $F_n \to F$ | 最弱 |
| **依概率** | $P(|X_n-X|>\epsilon) \to 0$ | ← $L^p$ / a.s. |
| **$L^p$** | $E[|X_n-X|^p] \to 0$ | → 依概率 |
| **a.s.** | $P(X_n \to X) = 1$ | → 依概率 |

### Lebesgue 积分（速成）

三大定理：
- **MCT**：$f_n \nearrow f \geq 0 \Rightarrow \int f_n \nearrow \int f$
- **Fatou**：$\int \liminf f_n \leq \liminf \int f_n$
- **DCT**：$|f_n| \leq g \in L^1, f_n \to f \Rightarrow \int f_n \to \int f$ ★

---

## 💻 代码层

```python
import numpy as np
# Hilbert 空间: 正交投影
# 将向量投影到子空间
v = np.array([3, 4])
e1 = np.array([1, 0])  # 子空间基底
proj = np.dot(v, e1) * e1  # 正交投影
perp = v - proj  # 正交分量
print(f"v = {v}, proj = {proj}, perp = {perp}")
print(f"验证正交: <proj, perp> = {np.dot(proj, perp)}")  # 应为 0

# RKHS: 核函数
def gaussian_kernel(x, y, sigma=1):
    return np.exp(-np.linalg.norm(x-y)**2 / (2*sigma**2))
# 再生性: f(x) = <f, k(x,·)>
print(f"k(0, 0.5) = {gaussian_kernel(np.array([0]), np.array([0.5])):.4f}")
```

---

## ⚠️ 不足层
- 不涉及算子谱理论的高级内容（需 Math 202B）
- 不做无界算子（量子力学需要）

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| Banach 空间 | 函数空间优化 |
| Hilbert 空间 | RKHS → SVM / Kernel PCA |
| Riesz 表示 | Gaussian Process |
| DCT | SGD 收敛 |
| $L^p$ 对偶 | Fenchel 对偶 / 变分推断 |
| 压缩映射 | 梯度下降收敛 |

---

## 章节概览（Rieffel 2024 版）

| 章 | 内容 | 关键 |
|---|---|---|
| 1-2 | 度量空间完备化 | 完备化定理 |
| 3-4 | 拓扑空间 | 紧致、连通、Hausdorff ★ |
| 5-6 | 测度论速成 | σ-代数、Lebesgue 积分 |
| 7-8 | $L^p$ 空间 | Hölder、完备性 ★ |
| 9 | Banach 空间 | 压缩映射、开映射定理 |
| 10 | Hilbert 空间 | 正交、Riesz 表示 ★ |
| 11 | 有界算子 | 伴随、谱定理简介 |
