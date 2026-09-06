# Harvard Math 114 — Measure, Integration and Banach Spaces

> **学校**：Harvard
> **一手来源**：Harvard Undergraduate Brochure 2025-2026

## 课程信息
- **编号**：Math 114
- **先修**：Math 112 或 Math 23b
- **教材**：Folland, *Real Analysis*；Rudin, *Real and Complex Analysis*
- **特色**：测度论 + 泛函分析入门

## 教学大纲
1. **Lebesgue measure & integral** ★
2. **Convergence theorems**（MCT, DCT, Fatou）
3. **$L^p$ spaces** ★
4. **Banach spaces 入门**
5. **Hilbert spaces 入门**
6. **Fourier 分析**（如时间允许）

## 与 ML 的关联（**ML 理论核心**）
- **$L^p$ 空间**：神经网络函数空间
- **DCT**：极限换序（ML 训练收敛证明）
- **学完本课后**：能从泛函视角理解 RKHS（kernel methods）

## 参考资源
- Folland, *Real Analysis* (2nd ed, Wiley)
- Rudin, *Real and Complex Analysis*
- MIT 对照：[MIT 18.125 Measure and Integration](../../mit-math-courses/)

## 📍 在数学全景中的位置

```
前置知识                        本课                        后续课程
─────────────────────────────────────────────────────────────────────
Harvard Math 112 实分析   →   Harvard Math 114          →   Harvard Math 131 拓扑
(Rudin: 度量空间+Riemann)       (Lebesgue + Banach/Hilbert)    Harvard Math 122 代数
MIT 18.100B 或同等                                           泛函分析深化
                                                             偏微分方程
```

**难度阶梯**（测度论方向）

| 阶梯 | 课程 | 教材 | 角色 |
|---|---|---|---|
| 基础 | Rudin *Principles* Ch 11 | Rudin | Lebesgue 一页纸速览 |
| **核心 ★** | **Harvard Math 114** | **Folland** | **Lebesgue + Lp + Banach** |
| 研究生 | MIT 18.125 | Rudin *R&C* | 测度论深化 |
| 应用 | MIT 18.175 | Durrett | 测度论概率 → ML 理论 |
| 高阶 | UT Austin M 381C | Folland | PhD 资格考级别 |

> 本课是**从 Riemann 积分到现代分析**的飞跃。Lebesgue 积分是概率论、泛函分析、偏微分方程的**共同基础**。

## 🔬 理论联系实际

### 应用 1：Lebesgue 积分 vs Riemann → 概率测度 → 大数定律的严格证明

**Riemann**：按定义域分桶（竖切）→ Dirichlet 函数 $\mathbf{1}_\mathbb{Q}$ 不可积

**Lebesgue**：按值域分桶（横切）→ $\int \mathbf{1}_\mathbb{Q} \, d\mu = 1 \cdot \mu(\mathbb{Q} \cap [0,1]) = 1 \cdot 0 = 0$ ✓

概率论中，**期望就是 Lebesgue 积分**：
$E[X] = \int_\Omega X \, dP = \int_{-\infty}^{\infty} x \, dF(x)$

**强大数定律**（用 DCT 证明）：$\frac{1}{n}\sum_{i=1}^n X_i \xrightarrow{a.s.} E[X]$——其证明**必须用 Lebesgue 积分**（Riemann 积分处理不了可列无穷个随机变量的极限换序）。

### 应用 2：$L^p$ 空间完备性 → 神经网络函数空间

$L^p(\Omega, \mathcal{F}, \mu) = \{f : \int |f|^p \, d\mu < \infty\}$ 是**Banach 空间**（完备赋范空间）。

- $p = 2$：$L^2$ 是 **Hilbert 空间**（有内积）→ 正交分解 → Fourier 分析
- 神经网络研究的函数空间通常是 $L^p$ 空间的子集
- **ML 对应**：RKHS（再生核 Hilbert 空间）= kernel methods 的严格基础

### 应用 3：控制收敛定理 (DCT) → 极限与积分换序

$|f_n| \leq g, \; g \text{ 可积}, \; f_n \to f \; a.e. \implies \int f_n \to \int f$

**ML 对应**：SGD 收敛证明中，mini-batch 梯度 $\frac{1}{|B|}\sum_{i \in B} \nabla \ell(\theta; x_i)$ 对 batch size $\to \infty$ 的收敛，需要 DCT 保证极限与期望换序合法。

### 应用 4：Hilbert 空间 → RKHS → 核方法

$\text{RKHS}: \quad \exists k(\cdot, \cdot): \quad f(x) = \langle f, k(x, \cdot) \rangle_{\mathcal{H}}$

- $k(x,y) = \exp(-\|x-y\|^2/2\sigma^2)$（高斯核）定义一个 RKHS
- SVM、Kernel PCA、Gaussian Process 都建立在 RKHS 上
- **本质**：RKHS 的完备性来自 Hilbert 空间理论（Math 114 后半）

### 应用 5：Banach 不动点 → 优化收敛的泛函分析视角

在 Banach 空间 $X$ 中，压缩映射 $T: X \to X$ 有唯一不动点。梯度下降在**函数空间**（而非参数空间）中的收敛分析需要 Banach 空间框架。

## 🆕 2024-2026 最新研究

### 1. RKHS 与神经网络的等价（NTK 理论）

2024-2026 的核心进展：在无限宽极限下，神经网络等价于一个 RKHS 中的核回归：
$f_{\text{NTK}}(x) = \sum_i \alpha_i k_{\text{NTK}}(x, x_i)$
- $k_{\text{NTK}}$ 是一个正定核 → 由 Mercer 定理定义 RKHS
- 连接：Math 114 的 **Hilbert 空间 + 正交投影**正是 NTK 收敛性证明的工具
- Yang et al. (2024) 推广到 Transformer 的 NTK ⚠️

### 2. 最优传输 (Optimal Transport) 的测度论基础

最优传输理论（将一个概率测度 $\mu$ 连续映射到另一个 $\nu$）在 2024-2026 ML 中爆发式应用：
- Wasserstein GAN：$W_1(\mu, \nu) = \inf_\gamma \int \|x-y\| \, d\gamma$
- 计算依赖测度论：测度之间的距离用**概率测度空间**的几何定义
- 连接：Math 114 的 **测度论 + 弱收敛**是 OT 的数学语言

### 3. Score-Based Diffusion 的测度论视角

Song et al. 的 score-based diffusion model（2021 起）在 2024-2026 获得了严格的测度论分析：
- diffusion 过程 = 测度的连续形变 $\mu_0 \to \mu_T$
- score function $\nabla \log p_t(x)$ 在测度论中是 **Radon-Nikodym 导数**的应用 ⚠️
- 连接：Math 114 的 **Radon-Nikodym 定理 + 测度绝对连续性**是理论基础

> ⚠️ 标记的具体论文年份/引用待一手核实 arXiv。核心数学工具（DCT, Radon-Nikodym, Hilbert 空间）来自 Math 114 是确定的。

---

📌 **下一步**：→ [Harvard Math 122 Algebra I](../math122_algebra_I/)
