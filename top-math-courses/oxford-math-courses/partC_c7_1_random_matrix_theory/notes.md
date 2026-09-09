# Oxford Part C C7.1 · 随机矩阵理论 精读笔记

> **教材**：Tao, *Topics in Random Matrix Theory* (AMS GSM 132, 2012) — 免费在线
> **辅助**：Anderson-Guionnet-Zeitouni (AGZ), *An Introduction to Random Matrix Theory* (CUP, 2010)
> **参考**：Tao 的博客 terrytao.wordpress.com 有大量 RMT 系列帖

---

## 〇、费曼直觉层：随机矩阵到底在研究什么？

### 一句话直觉

> **把矩阵的每个元素当作随机数，研究特征值"集体行为"的普适定律。**

想象你往一个 $N \times N$ 矩阵的每个格子里扔一个随机数（比如标准正态分布），然后求它的特征值。你会以为特征值也乱七八糟吧？

**不。** 当 $N \to \infty$ 时，特征值的分布收敛到一个**确定的、普适的**形状——无论你用正态分布、均匀分布、还是掷硬币（±1）填矩阵，答案都一样。这就是 RMT 的魔力。

### 三个核心图像

| 图像 | 直觉 | ML 对应 |
|---|---|---|
| **半圆律**（Wigner） | 随机方阵的特征值排成一个半圆 | 权重矩阵 $\mathrm{diag}(W)$ 的谱 |
| **MP 律**（Marchenko-Pastur） | 样本协方差矩阵的特征值排成一个"鱼形" | $\frac{1}{n}XX^T$ 的谱 → PCA / 过拟合 |
| **Tracy-Widom** | 最大特征值的波动遵循一种特殊的分布 | "信号"何时能从噪声中冒出（spike 检测）|

### 类比：从"数论"到"统计物理"

- **确定性矩阵**（如 $A = I$）→ 特征值 = 固定点（像行星轨道）
- **随机矩阵** → 特征值集体行为 = 统计力学（像气体分子）
- RMT 就是**矩阵版的统计力学**：个别特征值不可预测，但集体分布有精确定律

---

## 一、数学层：核心定义与定理

### 1.1 Wigner 矩阵与半圆律 ★

**定义（Wigner 矩阵）**：$M_N$ 是 $N \times N$ 埃尔米特矩阵，上三角元素 $\{M_{ij}\}_{i \leq j}$ 独立同分布，满足：
- $\mathbb{E}[M_{ij}] = 0$
- $\mathrm{Var}(M_{ij}) = 1$（对角线 $\mathrm{Var}(M_{ii}) = 1$ 或 $2$，视约定）
- 有界矩条件：$\mathbb{E}[|M_{ij}|^k] \leq C_k$ 对所有 $k$

**归一化**：研究 $W_N = \frac{1}{\sqrt{N}} M_N$，特征值 $\lambda_1 \leq \cdots \leq \lambda_N$。

**经验谱分布（ESD）**：
$$\mu_N = \frac{1}{N}\sum_{i=1}^{N} \delta_{\lambda_i}$$

**定理（Wigner 半圆律，1955）**：当 $N \to \infty$ 时，$\mu_N$ 几乎处处弱收敛到**半圆分布**：
$$\rho_{sc}(x) = \frac{1}{2\pi}\sqrt{4 - x^2}, \quad x \in [-2, 2]$$

**直觉**：特征值集中在 $[-2, 2]$ 内，密度在中间最高（$x=0$ 时 $\rho = 1/\pi$），在边缘 $x = \pm 2$ 处趋于零（像 $\sqrt{4-x^2}$）。

**为什么是半圆？** Stieltjes 变换满足二次方程：
$$m(z) = \int \frac{\rho_{sc}(x)}{x - z}\,dx \quad \Longrightarrow \quad zm^2 + zm + 1 = 0$$
解出 $m(z) = \frac{-z + \sqrt{z^2 - 4}}{2z}$，虚部就是 $\rho_{sc}$。

### 1.2 Marchenko-Pastur 律（样本协方差矩阵）★

**设定**：$X$ 是 $p \times n$ 矩阵，元素 i.i.d. 均值为 0 方差为 1。样本协方差矩阵 $S = \frac{1}{n}XX^T$（$p \times p$）。

**关键参数**：$\gamma = p/n$（维数比）。当 $p, n \to \infty$ 且 $p/n \to \gamma$：

**定理（Marchenko-Pastur, 1967）**：$S$ 的 ESD 收敛到 **MP 分布**：
$$\rho_{MP}(x) = \frac{1}{2\pi \gamma x}\sqrt{(b_+ - x)(x - b_-)}, \quad x \in [b_-, b_+]$$
其中 $b_\pm = (1 \pm \sqrt{\gamma})^2$。

- 当 $\gamma < 1$ 时，在 $x=0$ 处有一个**点质量** $(1 - \gamma)\delta_0$（零特征值占比 $1 - \gamma$）。
- 当 $\gamma = 1$（方阵），$b_- = 0$，密度从原点发散。

**ML 意义**：如果数据是纯噪声（$X$ 的元素 i.i.d.），PCA 的特征值全部落在 $[b_-, b_+]$ 内。任何超出 $b_+$ 的特征值 = **真信号**！

### 1.3 Tracy-Widom 分布与边缘极限 ★

**问题**：最大特征值 $\lambda_{\max}$ 在哪？

**定理（边缘收敛）**：对 Wigner 矩阵，
$$N^{2/3}(\lambda_{\max} - 2) \xrightarrow{d} \xi_{\beta}$$
其中 $\xi_\beta$ 服从 **Tracy-Widom 分布**，$\beta \in \{1, 2, 4\}$（对应 GOE/GUE/GSE 对称类）。

- $\beta = 1$：实对称（GOE），最常见于 ML
- $\beta = 2$：复埃尔米特（GUE）
- Tracy-Widom 是 Airy 函数的 Fredholm 行列式：$F_2(s) = \det(I - K_s)$，$K_s$ 是 Airy 核。

**直觉**：$\lambda_{\max}$ 集中在 2 附近，涨落尺度 $N^{-2/3}$（比 $N^{-1/2}$ 更紧）。

### 1.4 尖峰模型与 BBP 相变 ★

**设定（Spike Model）**：$S = \frac{1}{n}XX^T + \theta vv^T$（信号 + 噪声），$v$ 是单位向量。

**定理（BBP 相变, Baik-Ben Arous-Péché 2005）**：信噪特征值 $\theta$ 只有在超过阈值 $\sqrt{\gamma}$ 时才能被检测到：
- $\theta > \sqrt{\gamma}$：$\lambda_{\max} \to (1+\theta)(1 + \gamma/\theta) > b_+$（冒出谱外！）
- $\theta \leq \sqrt{\gamma}$：$\lambda_{\max} \to b_+$（淹没在噪声中）

**ML 意义**：PCA 能否发现低秩信号？取决于信噪比 vs 维数比。这就是**高维统计的根本限制**。

### 1.5 自由概率（Free Probability）入门

**核心思想**：经典概率研究**可交换**随机变量的独立性和；自由概率研究**不可交换**（矩阵）的"独立性"。

**自由卷积**：如果 $A$, $B$ 是两个独立随机矩阵，$A+B$ 的谱分布不是经典卷积，而是**自由卷积** $\boxplus$。

- 半圆律 ⊗ 自由概率 = 中心极限定理：$A \boxplus B$（多个独立 Wigner 矩阵之和）→ 半圆。
- 这解释了为什么半圆律是普适的：它是矩阵版的 CLT。

### 1.6 普适性（Universality）★

**核心哲学**：局部特征值统计（间距分布、边缘极限）**不依赖**矩阵元素的分布——正态、均匀、±1 都给出相同极限。

**Tao-Vu（2010, Fields 级别）**：在极弱条件下证明了 Wigner 矩阵的 bulk 和 edge universality。

> **ML 启示**：不管你怎么初始化神经网络权重（高斯、均匀、截断正态），谱的宏观行为都一样。

---

## 二、代码层：从模拟到验证

### 2.1 手画半圆律（numpy）

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
N = 2000
# Wigner 矩阵: 实对称, 上三角 i.i.d. N(0,1)
A = np.random.randn(N, N)
W = (A + A.T) / np.sqrt(2 * N)   # 正确归一化: off-diag Var=1/N → 半圆律 [-2,2]
eigvals = np.linalg.eigvalsh(W)

x = np.linspace(-2, 2, 500)
semicircle = np.sqrt(4 - x**2) / (2 * np.pi)

plt.hist(eigvals, bins=80, density=True, alpha=0.6, label='经验谱')
plt.plot(x, semicircle, 'r-', lw=2, label='半圆律 $\\rho_{sc}$')
plt.xlabel('特征值'); plt.ylabel('密度'); plt.legend()
plt.title(f'Wigner 半圆律 (N={N})')
plt.savefig('semicircle_law.png', dpi=150)
plt.show()
print(f"lambda_max = {eigvals.max():.4f} (理论 → 2)")
```

### 2.2 Marchenko-Pastur 与 PCA 信号检测

```python
p, n = 500, 2000          # gamma = p/n = 0.25
gamma = p / n
X = np.random.randn(p, n) # 纯噪声
S = X @ X.T / n
eigvals_noise = np.linalg.eigvalsh(S)

# 加入一个 rank-1 信号
theta = 2.0  # > sqrt(gamma) ≈ 0.5, 应冒出
v = np.random.randn(p); v /= np.linalg.norm(v)
S_signal = S + theta * np.outer(v, v)
eigvals_signal = np.linalg.eigvalsh(S_signal)

b_plus = (1 + np.sqrt(gamma))**2
print(f"MP 上沿 b+ = {b_plus:.4f}")
print(f"噪声谱最大特征值 = {eigvals_noise.max():.4f}")
print(f"信号谱最大特征值 = {eigvals_signal.max():.4f}")
# 预测信号特征值位置: (1+theta)(1+gamma/theta)
pred = (1 + theta) * (1 + gamma / theta)
print(f"BBP 预测位置 = {pred:.4f}")
```

### 2.3 神经网络权重谱分析（→ 泛化理论）

```python
# 随机初始化的全连接层权重矩阵 W (fan_in x fan_out)
fan_in, fan_out = 784, 512
W = np.random.randn(fan_out, fan_in) / np.sqrt(fan_in)
S_W = W @ W.T                    # Gram 矩阵 → 样本协方差型
eigvals_W = np.linalg.eigvalsh(S_W)
# gamma = fan_out / fan_in ≈ 0.653
gamma = fan_out / fan_in
print(f"fan_out/fan_in = {gamma:.3f}, MP b+ = {(1+np.sqrt(gamma))**2:.4f}")
print(f"实际最大特征值 = {eigvals_W.max():.4f}")
# Xavier 初始化使谱恰好填满 MP 支撑 → 不爆炸/不消失的理论基础
```

完整实验代码见 [experiments/random_matrix_spectrum.py](experiments/random_matrix_spectrum.py)。

---

## 三、与深度学习理论的联系 ★（本课的核心价值）

### 3.1 Pennington 的谱分析框架

**Pennington-Schoenholz-Sohl-Dickstein (NeurIPS 2017, [1712.04747](https://arxiv.org/abs/1712.04747) ✅)**：用 MP 律分析随机网络中 Gram 矩阵的谱，解释"edge of chaos"。

- 前向传播 $h_{l+1} = \phi(W_l h_l)$，Gram 矩阵 $G_l = H_l H_l^T / n$。
- $G_l$ 的特征值分布可用自由概率递推。
- 如果谱"收缩"到 0 → 梯度消失；如果"爆炸" → 梯度爆炸。

### 3.2 随机矩阵与泛化

**Martin & Mahoney (2018-2021)**：训练好的网络的权重矩阵谱偏离 MP 律的程度 = **有效秩 / 信息容量**的度量。

$$\text{Weighted Energy} = \sum_i (\hat{\lambda}_i - \lambda_i^{MP})^2$$

偏离越大 → 学到了结构 → 泛化越好。（启发式，严格理论仍在发展中 ⚠️）

### 3.3 权重初始化 = 谱控制

- **Xavier/Glorot 初始化**（[Glorot & Bengio 2010](https://proceedings.mlr.press/v9/glorot10a.html)）：$W_{ij} \sim \mathcal{N}(0, 1/\mathrm{fan\_in})$ → 恰好让 $WW^T$ 的谱填满 MP 支撑，方差稳定。
- **He 初始化**：$\mathrm{Var}(W) = 2/\mathrm{fan\_in}$（补偿 ReLU 的半边截断）。
- 本质：初始化 = 控制 $\lambda_{\max}(WW^T)$，使前向/反向传播的谱半径 ≈ 1。

### 3.4 过参数化与双下降

当参数量 $p \gg$ 样本数 $n$（$\gamma = p/n \gg 1$），MP 律说大量特征值为零。这些零特征值方向 = **插值空间**。RMT 为"过拟合反而泛化"（double descent）提供了谱几何视角。

### 3.5 大语言模型的权重谱

⚠️ 近期工作（2024-2025）分析 LLM（如 LLaMA, GPT 级别）的权重矩阵谱，发现**重尾**偏离 MP 律——这可能解释了大模型的涌现能力。具体论文编号建议核实最新 ICLR/NeurIPS 录取列表。

---

## 四、不足层与边界

### 4.1 RMT 的局限

1. **独立性假设过强**：真实神经网络的权重不是独立的（经过梯度下降训练后有结构）。RMT 描述的是**随机初始化**或**噪声极限**，对训练后网络只能给启发式。
2. **非对称矩阵更难**：大部分漂亮定律（半圆律、TW）只对埃尔米特矩阵成立。非对称矩阵（如 ReLU 网络的 Jacobian）的谱是复平面上的圆环律（**Girko 圆律**），工具更复杂。
3. **有限尺寸效应**：$N \to \infty$ 的极限很美，但真实网络只有几千维。有限尺寸校正（$1/N$ 展开）是活跃研究方向。

### 4.2 理论 vs 实践的 gap

- Pennington 的谱分析只精确解决**线性**网络（无激活函数或线性化）。
- 非线性激活的谱传播需要自由概率的 **$R$-变换和 $S$-变换**递推，计算复杂。
- RMT 的泛化界通常比实际松（只给存在性证明，不够 tight）。

---

## 五、应用层：ML 工程师能用 RMT 做什么？

| 应用 | RMT 工具 | 实际效果 |
|---|---|---|
| **权重初始化设计** | MP 律 → Xavier/He | 所有框架默认使用 |
| **PCA 信号检测** | BBP 相变阈值 $\sqrt{\gamma}$ | 高维统计标准方法 |
| **协方差估计正则化** | Ledoit-Wolf 收缩 → MP 最优收缩 | sklearn `LedoitWolf` |
| **网络泛化诊断** | 权重谱偏离 MP 度 | 研究/调试工具 |
| **压缩与剪枝** | 低秩近似 + 谱分析 | LoRA 理论基础 |
| **对抗鲁棒性** | 权重矩阵条件数 → 扰动敏感度 | 研究中 |

### 关键公式速查卡

| 定律 | 密度函数 | 参数 |
|---|---|---|
| Wigner 半圆 | $\frac{\sqrt{4-x^2}}{2\pi}$, $x \in [-2,2]$ | 归一化 Wigner 矩阵 |
| Marchenko-Pastur | $\frac{\sqrt{(b_+-x)(x-b_-)}}{2\pi\gamma x}$ | $\gamma = p/n$, $b_\pm = (1\pm\sqrt\gamma)^2$ |
| Tracy-Widom $\beta=1$ | $F_1(s) = \exp\!\left(-\frac{1}{2}\int_s^\infty q(t)\,dt\right)\sqrt{F_2(s)}$ | $q$ = Painlevé II |
| BBP 相变 | $\theta_c = \sqrt{\gamma}$ | spike 检测阈值 |

---

## 六、推荐学习路径

1. **入门**：Tao 博客 "Topics in random matrix theory" 系列（最友好的直觉）
2. **核心**：Tao 的书前 3 章（半圆律 + MP + Stieltjes 变换法）
3. **ML 应用**：Pennington 2017 NeurIPS 论文 → Pennington & Worah 2019 ([1811.01968](https://arxiv.org/abs/1811.01968) ✅)
4. **前沿**：Martin-Mahoney "Traditional and Heavy-Tailed Self-Regularization" 系列

---

## 七、术语对照表

| 英文 | 中文 | 说明 |
|---|---|---|
| Empirical Spectral Distribution (ESD) | 经验谱分布 | 特征值的直方图 |
| Stieltjes transform | 斯蒂尔杰斯变换 | $\int \frac{d\mu(x)}{z-x}$，核心分析工具 |
| Free convolution | 自由卷积 | 矩阵版的卷积 |
| $R$-transform | $R$-变换 | 自由概率中的累积量 |
| Bulk universality | 体区普适性 | 内部特征值间距分布 |
| Edge universality | 边缘普适性 | 最大/最小特征值分布 |
| Spike model | 尖峰模型 | 低秩信号 + 噪声 |
| BBP transition | BBP 相变 | 信号检测阈值 |

> ⚠️ Tracy-Widom 分布没有简洁闭式表达（需要 Painlevé II 方程的解）。数值表见 bornemann 开源代码。
