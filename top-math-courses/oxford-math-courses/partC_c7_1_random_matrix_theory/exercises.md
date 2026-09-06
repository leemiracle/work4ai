# Oxford Part C C7.1 · 随机矩阵理论 · 习题

> **教材**：Tao, *Topics in Random Matrix Theory*
> **难度**：⭐ 基础 → ⭐⭐⭐⭐ 挑战

---

## 一、半圆律与 Stieltjes 变换

### 题 1（⭐⭐）半圆律的 Stieltjes 变换

半圆分布 $\rho_{sc}(x) = \frac{1}{2\pi}\sqrt{4-x^2}$, $x \in [-2,2]$ 的 Stieltjes 变换定义为：
$$m(z) = \int_{-2}^{2} \frac{\rho_{sc}(x)}{x - z}\,dx, \quad z \in \mathbb{C}^+$$

(a) 证明 $m(z)$ 满足二次方程 $zm^2 + zm + 1 = 0$。

(b) 解出 $m(z)$，并验证 $\rho_{sc}(x) = \frac{1}{\pi}\lim_{\epsilon \to 0^+} \mathrm{Im}\, m(x + i\epsilon)$。

**提示**：用 $m'(z) = \int \frac{\rho_{sc}(x)}{(x-z)^2}dx$ 配合分部积分。

---

### 题 2（⭐⭐⭐）矩方法验证半圆律

Wigner 矩阵 $W = \frac{1}{\sqrt{N}}M$ 的 $k$ 阶矩 $m_k = \frac{1}{N}\mathrm{Tr}(W^k)$。

(a) 计算 $m_2 = \mathbb{E}[\frac{1}{N}\mathrm{Tr}(W^2)]$，验证它等于 1（半圆律的 $\int x^2 \rho_{sc}(x)dx = 1$）。

(b) 计算 $m_4 = \mathbb{E}[\frac{1}{N}\mathrm{Tr}(W^4)]$，验证它等于 2（Catalan 数 $C_2 = 2$）。

(c) 猜测一般规律 $m_{2k} = C_k$（第 $k$ 个 Catalan 数），并解释 Catalan 数为何出现。

**提示**：(c) 涉及非交叉配对（non-crossing pairing），这是自由概率的 combinatorial 核心。

---

## 二、Marchenko-Pastur 律

### 题 3（⭐⭐）MP 支撑与极限比

设 $X$ 是 $p \times n$ 随机矩阵，元素 i.i.d. $\mathcal{N}(0,1)$，样本协方差 $S = \frac{1}{n}XX^T$。

(a) 当 $\gamma = p/n = 0.25$ 时，计算 MP 支撑 $[b_-, b_+]$ 和零特征值的比例。

(b) 当 $\gamma \to 1^-$ 时，$b_- \to ?$ 解释这意味着什么。

(c) 当 $\gamma \to \infty$（$p \gg n$）时，谱会发生什么？与过参数化神经网络的关系？

---

### 题 4（⭐⭐⭐）PCA 中的信号检测

你有 $n = 1000$ 个样本，每个 $p = 500$ 维。数据生成模型为 $x_i = \theta v + \epsilon_i$，其中 $v \in \mathbb{R}^{500}$ 是未知信号方向，$\epsilon_i \sim \mathcal{N}(0, I)$。

(a) 样本协方差 $S$ 的噪声谱支撑是什么？（计算 $b_\pm$）

(b) 你做 PCA 得到最大特征值 $\lambda_1 = 3.5$。这个方向是信号还是噪声？给出判断依据。

(c) 如果 $\theta = 0.8$，信号能否被 PCA 检测到？（计算 BBP 阈值）

(d) 需要多大的 $\theta$ 才能让信号特征值冒出 $b_+$？

---

## 三、Tracy-Widom 与边缘统计

### 题 5（⭐⭐⭐）边缘涨落的标度

对 $N \times N$ GOE 矩阵（Gaussian Orthogonal Ensemble），最大特征值 $\lambda_{\max}$ 满足：
$$N^{2/3}(\lambda_{\max} - 2) \xrightarrow{d} \xi_1 \sim \text{TW}_1$$

(a) 解释为什么标度是 $N^{2/3}$ 而不是 $N^{1/2}$（与经典 CLT 对比）。

(b) TW$_1$ 的均值约为 $-1.21$，标准差约为 $0.90$。对 $N = 1000$，$\lambda_{\max}$ 在 $[1.97, 2.03]$ 内的概率大约是多少？

(c) 用代码模拟 $N = 500$ 的 GOE 矩阵 1000 次，画 $N^{2/3}(\lambda_{\max}-2)$ 的直方图，与 TW$_1$ 密度比较。

---

## 四、BBP 相变

### 题 6（⭐⭐⭐⭐）BBP 相变的严格证明思路

尖峰模型 $S = \frac{1}{n}XX^T + \theta vv^T$，$\gamma = p/n$。

(a) 用矩阵扰动论，写出加入 $\theta vv^T$ 后特征值的一阶修正。

(b) 证明当 $\theta > \sqrt{\gamma}$ 时，扰动后的最大特征值收敛到 $(1+\theta)(1+\gamma/\theta)$。

(c) 解释 $\theta = \sqrt{\gamma}$ 处相变的物理意义（信噪比的临界点）。

**提示**：(b) 用 resolvent $G(z) = (S - zI)^{-1}$ 和秩一更新公式。

---

## 五、ML 应用

### 题 7（⭐⭐⭐）权重初始化的谱分析

一个全连接层 $h = Wx$，$W \in \mathbb{R}^{m \times d}$，$x \in \mathbb{R}^d$，$m = 1024$, $d = 768$。

(a) 如果 $W_{ij} \sim \mathcal{N}(0, \sigma^2)$，前向传播方差 $\mathrm{Var}(h_i) = ?$（用 $d$ 和 $\sigma^2$ 表示）。

(b) 用 MP 律确定：$\sigma^2$ 取何值时，$\mathrm{Var}(h_i) = 1$？（即 Xavier 初始化的推导）

(c) 如果用 ReLU 激活函数 $\phi(h) = \max(0, h)$，为什么需要 He 初始化 $\sigma^2 = 2/d$？（用谱论证）

(d) 写代码验证：用 $\sigma^2 = 1/d$（不加 ReLU 的 Xavier）vs $\sigma^2 = 2/d$（He）的初始化，在 20 层网络上看方差随深度的变化。

---

### 题 8（⭐⭐⭐⭐）泛化的谱诊断（开放题）

Pennington-Martin-Mahoney 的框架认为：训练好的网络权重谱偏离 MP 律的程度可衡量泛化能力。

(a) 训练两个 MNIST 分类器：一个过拟合（训练 100 epoch），一个早停（10 epoch）。提取第一层权重矩阵 $W$。

(b) 计算 $WW^T$ 的谱，与 MP 律比较。哪个偏离更大？

(c) 计算"加权谱能量" $\sum_i (\hat{\lambda}_i - \lambda_i^{MP})^2$（$\hat\lambda_i$ 是实际特征值，$\lambda_i^{MP}$ 是 MP 预测），比较两个模型。

(d) ⚠️ 这种度量是启发式的，没有严格理论保证。讨论其局限性和可能的改进方向。

---

## 参考答案要点

<details>
<summary>题 3(a) 参考答案</summary>

$\gamma = 0.25$: $b_- = (1-\sqrt{0.25})^2 = 0.25$, $b_+ = (1+\sqrt{0.25})^2 = 2.25$。零特征值比例 = $1 - \gamma = 0.75$（因为 $p < n$，实际上 $p \times p$ 矩阵的秩 $\leq n > p$，没有零特征值——注意 $\gamma < 1$ 时 $S$ 满秩概率 1，但 MP 在 0 处有点质量代表"近零"积累。这里要注意 $p < n$ 和 $p > n$ 的区别）。

**更正**：当 $p/n = \gamma < 1$ 时，$S = \frac{1}{n}XX^T$ 是 $p \times p$ 矩阵，秩为 $\min(p,n) = p$（概率 1），所以没有精确的零特征值。MP 律在 $\gamma < 1$ 时在 0 处的点质量 $(1-\gamma)\delta_0$ 指的是**如果考虑 $n \times n$ 矩阵 $\frac{1}{n}X^TX$** 的情形。需要明确矩阵的维度约定。
</details>

<details>
<summary>题 4(c) 参考答案</summary>

$\gamma = 500/1000 = 0.5$，BBP 阈值 $\sqrt{\gamma} = \sqrt{0.5} \approx 0.707$。$\theta = 0.8 > 0.707$，所以**信号可以被检测到**。预测的信号特征值位置 = $(1+0.8)(1+0.5/0.8) = 1.8 \times 1.625 = 2.925$。而 $b_+ = (1+\sqrt{0.5})^2 \approx 2.914$。$2.925 > 2.914$，刚好冒出（但差距很小，实际中需要较多样本才能可靠区分）。
</details>
