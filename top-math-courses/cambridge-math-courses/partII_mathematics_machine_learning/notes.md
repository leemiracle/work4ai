# Cambridge Part II · 数学机器学习 精读笔记

> **课程**：Mathematics of Machine Learning (Part II / Part III level)
> **参考**：Shalev-Shwartz & Ben-David, *Understanding Machine Learning*；Mohri et al., *Foundations of Machine Learning*
> **Cambridge 特色**：从**数学**视角（概率不等式、凸分析、泛函分析）建立 ML 理论

---

## 〇、费曼直觉层：ML 理论在研究什么？

### 一句话直觉

> **ML 理论 = 回答"为什么机器学习有效？"——用数学证明泛化性。**

机器学习最大的谜团：你在训练集上拟合了 $10^9$ 个参数的神经网络，它竟然在**没见过的数据**上也有效。按经典统计直觉，参数这么多的模型应该严重过拟合。但它没有——**为什么？**

这就是 ML 理论的核心问题：**泛化性（Generalization）**。

### 三大支柱

| 支柱 | 直觉 | 核心问题 |
|---|---|---|
| **PAC 学习** | "概率近似正确" | 什么样的假设类可学习？ |
| **VC 维 / Rademacher 复杂度** | 假设类的"容量"度量 | 需要多少样本才能学？ |
| **凸优化** | 损失函数是碗 → 底部唯一 | 训练何时有保证？ |

### 经典泛化界的直觉

训练误差 $L_{\text{train}}$ 与真实误差 $L_{\text{true}}$ 的差距：
$$L_{\text{true}} \leq L_{\text{train}} + \underbrace{O\left(\sqrt{\frac{\text{复杂度}}{n}}\right)}_{\text{泛化 gap}}$$

经典理论说：参数越多 → 复杂度越大 → 泛化 gap 越大 → 过拟合。但深度学习违反了这个直觉！

---

## 一、数学层：核心定义与定理

### 1.1 PAC 学习框架 ★

**设定**：
- 输入空间 $\mathcal{X}$，输出空间 $\mathcal{Y} = \{0,1\}$（二分类）
- 数据分布 $\mathcal{D}$ over $\mathcal{X} \times \mathcal{Y}$
- 假设类 $\mathcal{H}$：候选函数集合
- 学习算法 $A$：接收训练集 $S = \{(x_i, y_i)\}_{i=1}^n$，输出 $h \in \mathcal{H}$

**定义（PAC 可学习）**：$\mathcal{H}$ 是 $(\epsilon, \delta)$-PAC 可学习的，如果存在算法 $A$ 和多项式 $p$，使得对任意分布 $\mathcal{D}$ 和目标函数，只要 $n \geq p(1/\epsilon, 1/\delta)$：
$$\Pr_{S \sim \mathcal{D}^n}\left[L_{\mathcal{D}}(A(S)) \leq \epsilon\right] \geq 1 - \delta$$

**直觉**：以高概率（$1-\delta$），学到的模型误差很小（$\leq \epsilon$）。

### 1.2 VC 维 ★

**定义（VC 维）**：假设类 $\mathcal{H}$ 的 VC 维 $\mathrm{VC}(\mathcal{H})$ = 能被 $\mathcal{H}$ "打散"（shatter）的最大点集大小。"打散" = 对点集的所有 $2^m$ 种标签组合，$\mathcal{H}$ 中都存在一个函数完美拟合。

**定理（VC 泛化界）**：对任意 $h \in \mathcal{H}$，以概率 $\geq 1-\delta$：
$$L_{\mathcal{D}}(h) \leq L_S(h) + \sqrt{\frac{2(\mathrm{VC}(\mathcal{H})\log(2en/\mathrm{VC}) + \log(2/\delta))}{n}}$$

**例子**：
- $\mathbb{R}^d$ 上的线性分类器：$\mathrm{VC} = d+1$
- 阈值函数 $h(x) = \mathbf{1}[x > \theta]$：$\mathrm{VC} = 1$
- 任意参数的神经网络：$\mathrm{VC}$ 可以很大

### 1.3 Rademacher 复杂度 ★

**动机**：VC 维只依赖假设类结构，不考虑数据分布。Rademacher 复杂度更细。

**定义**：样本集 $S = \{x_1, \ldots, x_n\}$，Rademacher 变量 $\sigma_i \in \{-1,+1\}$ i.i.d. 等概率。经验 Rademacher 复杂度：
$$\hat{\mathfrak{R}}_S(\mathcal{H}) = \mathbb{E}_\sigma\left[\sup_{h \in \mathcal{H}} \frac{1}{n}\sum_{i=1}^n \sigma_i h(x_i)\right]$$

**直觉**：$\sigma_i$ 是随机噪声标签。Rademacher 复杂度 = "假设类能拟合随机噪声的能力"。越高 → 容量越大 → 过拟合风险。

**定理（Rademacher 泛化界）**：以概率 $\geq 1-\delta$：
$$L_{\mathcal{D}}(h) \leq L_S(h) + 2\hat{\mathfrak{R}}_S(\mathcal{H}) + O\left(\sqrt{\frac{\log(1/\delta)}{n}}\right)$$

### 1.4 偏差-方差分解 ★

**平方损失下**：$\mathbb{E}[(y - \hat{f}(x))^2] = \underbrace{(\bar{f}(x) - f^*(x))^2}_{\text{偏差}^2} + \underbrace{\mathbb{E}[(\hat{f}(x) - \bar{f}(x))^2]}_{\text{方差}} + \sigma^2$

- **偏差**：模型平均预测与真实函数的差距（欠拟合）
- **方差**：不同训练集导致预测的变化（过拟合）
- **$\sigma^2$**：不可约噪声

**深度学习的异常**：参数极多 → 经典理论说方差应爆炸。但实际方差很小——这就是**"双下降"**现象的核心谜题。

### 1.5 正则化与稳定性 ★

**正则化**：$\min_w \frac{1}{n}\sum L(f_w(x_i), y_i) + \lambda\|w\|^2$

**稳定性（Stability）**：算法 $A$ 是 $\beta$-均匀稳定的，如果换一个训练样本，预测最多变化 $\beta$：
$$\sup_{S, S^{(i)}, z} |L(A(S), z) - L(A(S^{(i)}), z)| \leq \beta$$

**定理**：稳定算法泛化：$L_{\mathcal{D}}(A(S)) \leq L_S(A(S)) + 2\beta + O(1/\sqrt{n})$。

**SGD 的稳定性**：凸问题 + early stopping + 正则化 → SGD 稳定 → 泛化。

### 1.6 凸学习理论 ★

**凸性保证全局最优**：凸函数的局部最小 = 全局最小。

**强凸性 + 光滑性 → 快速收敛**：
- 强凸（$m$-强凸）：$f(y) \geq f(x) + \nabla f(x)^T(y-x) + \frac{m}{2}\|y-x\|^2$
- 光滑（$L$-光滑）：$\|\nabla f(x) - \nabla f(y)\| \leq L\|x-y\|$
- 条件数 $\kappa = L/m$ → 决定收敛速率

**梯度下降收敛**：$f(w_T) - f(w^*) \leq O(1/T)$（凸）或 $O(\kappa \log(1/\epsilon)/T)$（强凸）。

### 1.7 深度学习的泛化谜题 ★

**问题**：现代网络参数量 $p \gg$ 样本数 $n$，但不过拟合。

**经典理论的失败**：VC 维 / Rademacher 复杂度在 $p \gg n$ 时给出空的泛化界。

**新线索**（研究方向，⚠️ 尚无定论）：
1. **隐式正则化**：SGD 偏向"简单"解（平坦极小值、低范数）
2. **双下降**：过参数化区间的泛化曲线非单调，超过插值阈值后反而改善
3. **神经正切核（NTK）**：无限宽网络的梯度下降 ≈ 核岭回归 → 精确泛化界
4. **PAC-Bayes 界**：考虑后验分布而非单个假设 → 更紧的界

---

## 二、代码层：泛化界的数值验证

### 2.1 VC 维可视化

```python
import numpy as np
import matplotlib.pyplot as plt

# 2D 线性分类器的 VC 维 = 3
# 验证: 任意 3 个不共线的点, 2^3=8 种标签都能被一条直线分开
np.random.seed(42)
points = np.random.randn(3, 2)

fig, axes = plt.subplots(2, 4, figsize=(14, 7))
for idx, ax in enumerate(axes.flat):
    labels = [(idx >> i) & 1 for i in range(3)]
    labels = np.array(labels) * 2 - 1  # {-1, +1}
    # 找一个线性分类器
    # w·x + b = 0 分开两类
    if len(set(labels)) == 1:
        w, b = np.array([0, 1]), 5  # 全在一侧
    else:
        pos = points[labels == 1].mean(0)
        neg = points[labels == -1].mean(0)
        w = pos - neg
        b = -(w @ (pos + neg) / 2)
    for i in range(3):
        ax.scatter(*points[i], c='r' if labels[i] == 1 else 'b', s=100)
    xx = np.linspace(-2, 2, 100)
    if abs(w[1]) > 1e-6:
        yy = (-w[0]*xx - b) / w[1]
        ax.plot(xx, yy, 'k--', alpha=0.5)
    ax.set_title(f'标签={list(labels)}'); ax.set_xlim(-2,2); ax.set_ylim(-2,2)
plt.tight_layout(); plt.savefig('vc_dimension_demo.png', dpi=150); plt.show()
```

### 2.2 Rademacher 复杂度估计

```python
from sklearn.linear_model import LogisticRegression

def rademacher_complexity(X, hypothesis_class='linear'):
    """估计线性假设类的经验 Rademacher 复杂度"""
    n = len(X)
    sigma = np.random.choice([-1, 1], size=n)
    # sup_{w} (1/n) Σ σ_i (w·x_i) = (1/n) ||Σ σ_i x_i||
    # (线性函数无界, 需约束 ||w||≤1)
    return np.linalg.norm(X.T @ sigma) / n

X = np.random.randn(200, 10)
for d in [2, 5, 10, 50]:
    X = np.random.randn(200, d)
    rc = rademacher_complexity(X)
    print(f"d={d}: Rademacher 复杂度 ≈ {rc:.4f} (∝ √(d/n) = {np.sqrt(d/200):.4f})")
```

### 2.3 双下降现象模拟

```python
# 简化的双下降: 随参数量 p 变化的泛化误差
n = 100  # 样本数
p_range = np.arange(5, 500)
train_err = []
test_err = []
for p in p_range:
    # 过参数化 (p > n) 时训练误差 = 0 (插值), 但测试误差先升后降
    if p < n:
        te = 0.3 * (1 - p/n)  # 欠拟合区
        ts = 0.3 * (1 - p/n) + 0.1 * p/n
    else:
        te = 0.0  # 完美插值
        ts = 0.2 * np.exp(-(p-n)/100) + 0.05  # 双下降
    train_err.append(te); test_err.append(ts)

plt.plot(p_range, train_err, 'b-', label='训练误差')
plt.plot(p_range, test_err, 'r-', label='测试误差')
plt.axvline(n, color='gray', ls='--', label=f'n={n} (插值阈值)')
plt.xlabel('参数量 p'); plt.ylabel('误差'); plt.legend()
plt.title('双下降 (Double Descent)')
plt.savefig('double_descent.png', dpi=150); plt.show()
```

---

## 三、与深度学习的前沿联系 ★

### 3.1 神经正切核（NTK）

无限宽网络的梯度下降 ≈ 核岭回归，核函数为 NTK：
$$K_{\text{NTK}}(x, x') = \mathbb{E}_{\theta \sim \text{init}}\left[\left\langle\frac{\partial f_\theta(x)}{\partial\theta}, \frac{\partial f_\theta(x')}{\partial\theta}\right\rangle\right]$$

→ 精确泛化界（但只对无限宽 + lazy training 成立）。

### 3.2 PAC-Bayes 界

$$L_{\mathcal{D}}(h) \leq \mathbb{E}_{h \sim Q}[L_S(h)] + \sqrt{\frac{\mathrm{KL}(Q \| P) + \log(2\sqrt{n}/\delta)}{2n}}$$

$P$ = 先验，$Q$ = 后验（SGD 找到的解的分布）。这给出了目前最紧的非空泛化界之一。

### 3.3 隐式正则化

SGD 找的不是任意最小值，而是**低范数/平坦**最小值。理论分析：SGD 的连续极限 = 梯度流 = 在最小范数解的方向收敛。

---

## 四、不足层与边界

1. **经典理论 vs 深度学习**：VC 维、Rademacher 复杂度等经典工具对深度网络给出**空的**泛化界。这是本课的最大张力。
2. **无免费午餐定理**：不存在万能学习算法——任何算法在某些分布上失败。泛化必须依赖分布假设或归纳偏置。
3. **理论 vs 实践的 gap**：理论界通常比实际需要的样本数多几个数量级。理论只是给出"可学习性"的存在证明，不给出实用指导。

---

## 五、推荐路径

1. **Shalev-Shwartz & Ben-David** 前 6 章：PAC + VC 维 + Rademacher → **核心**
2. **Boyd 凸优化**（[Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)）配合：凸学习理论
3. **前沿**：Belkin 双下降论文 ([1812.11118](https://arxiv.org/abs/1812.11118) ✅) → NTK → PAC-Bayes
4. ⚠️ 深度学习泛化理论仍在快速发展中，没有标准教材

---

## 术语对照

| 英文 | 中文 |
|---|---|
| PAC learning | 概率近似正确学习 |
| VC dimension | VC 维（Vapnik-Chervonenkis）|
| Rademacher complexity | Rademacher 复杂度 |
| Generalization gap | 泛化差距 |
| Bias-variance tradeoff | 偏差-方差权衡 |
| Double descent | 双下降 |
| NTK (Neural Tangent Kernel) | 神经正切核 |
| PAC-Bayes | PAC-Bayes 界 |
| Implicit regularization | 隐式正则化 |
| Sample complexity | 样本复杂度 |
