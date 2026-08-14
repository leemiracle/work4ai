# Oxford Part C C8.1 · 随机微分方程 精读笔记

> **教材**：Oksendal, *Stochastic Differential Equations* (6th ed, Springer)
> **辅助**：Karatzas & Shreve, *Brownian Motion and Stochastic Calculus*；Gardiner, *Stochastic Methods*
> **参考**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

---

## 〇、费曼直觉层：SDE 到底在研究什么？

### 一句话直觉

> **SDE = ODE + 噪声——当微分方程里塞进了随机扰动。**

普通 ODE：$\frac{dx}{dt} = f(x)$ → 轨迹完全确定。
SDE：$dx = f(x)\,dt + g(x)\,dW_t$ → 轨迹是随机的。

其中 $W_t$ 是**布朗运动**（Wiener 过程）——连续但处处不可导的随机过程。

### 三个核心直觉

| 概念 | 直觉 | ML 对应 |
|---|---|---|
| **布朗运动 $W_t$** | 花粉在水中的随机游走 | 扩散模型中的噪声注入 |
| **Itô 积分** | "噪声驱动的面积累积" | 随机优化的理论基础 |
| **Langevin 方程** | 带摩擦的布朗运动 → 收敛到玻尔兹曼分布 | **MCMC 采样** ★ |

### 为什么 ODE 不够用？

热传导方程 $u_t = \Delta u$ 描述了**平均行为**（浓度的期望）。但如果你问"一个具体粒子在哪？"——答案是随机的，需要 SDE：
$$dX_t = \sqrt{2D}\,dW_t$$
单个粒子的轨迹是随机游走，但大量粒子的分布满足热方程。**PDE 描述群体，SDE 描述个体。**

---

## 一、数学层：核心定义与定理

### 1.1 布朗运动（Wiener 过程）

**定义**：$W_t$ ($t \geq 0$) 是标准布朗运动，如果：
1. $W_0 = 0$
2. 增量独立：$W_{t+s} - W_t$ 独立于 $\{W_u : u \leq t\}$
3. 增量正态：$W_{t+s} - W_t \sim \mathcal{N}(0, s)$
4. 轨迹连续

**关键性质**：
- 处处连续但**几乎处处不可导**（"病态"轨迹）
- $\mathbb{E}[W_t] = 0$, $\mathrm{Var}(W_t) = t$
- 协方差：$\mathrm{Cov}(W_s, W_t) = \min(s, t)$
- 二次变差：$\langle W \rangle_t = t$（有限变差变差为无穷！）

### 1.2 Itô 积分 ★

**问题**：如何定义 $\int_0^T f(t, \omega)\,dW_t$？$W_t$ 不可导，所以不能用普通积分。

**Itô 的构造**：
1. 分割 $[0,T] = \{t_0, \ldots, t_n\}$
2. 对**简单过程** $f = \sum c_i \mathbf{1}_{[t_i, t_{i+1})}$，定义 $\int f\,dW = \sum c_i (W_{t_{i+1}} - W_{t_i})$
3. 对一般过程取 $L^2$ 极限

**关键特征**：被积函数取**左端点**值 $f(t_i)$，不用区间中点。这导致 Itô 积分有"修正项"（见 Itô 引理）。

**Itô 等距（Itô Isometry）** ★：
$$\mathbb{E}\left[\left(\int_0^T f\,dW\right)^2\right] = \mathbb{E}\left[\int_0^T f^2\,dt\right]$$

### 1.3 Itô 引理 ★（随机微积分的链式法则）

**定理（Itô 引理）**：若 $X_t$ 满足 $dX = \mu\,dt + \sigma\,dW$，且 $f(t,x)$ 二阶连续可导，则：
$$df(t, X_t) = \left(\frac{\partial f}{\partial t} + \mu\frac{\partial f}{\partial x} + \frac{\sigma^2}{2}\frac{\partial^2 f}{\partial x^2}\right)dt + \sigma\frac{\partial f}{\partial x}\,dW$$

**与普通链式法则的区别**：多了一个 $\frac{\sigma^2}{2}\frac{\partial^2 f}{\partial x^2}dt$ 项——这是因为 $(dW)^2 = dt$（二次变差），所以 $dX^2 = \sigma^2 dW^2 = \sigma^2 dt$ 不能忽略。

**直觉**：Itô 积分取左端点 → Taylor 展开到二阶 → 额外的"凸性修正"。

### 1.4 SDE 的解

**SDE 一般形式**：
$$dX_t = \mu(t, X_t)\,dt + \sigma(t, X_t)\,dW_t$$

**强解**：给定 $W_t$ 的一条轨迹，$X_t$ 是 $W_t$ 的函数。

**弱解**：只需存在某个概率空间上的 $(X, W)$ 满足方程。

**存在唯一性**（Lipschitz 条件）：若 $\mu, \sigma$ 关于 $x$ Lipschitz 连续，则强解存在唯一。

### 1.5 Fokker-Planck 方程 ★

SDE 的解 $X_t$ 是一个随机过程，其**概率密度** $p(x,t)$ 演化满足：
$$\frac{\partial p}{\partial t} = -\frac{\partial}{\partial x}[\mu(x)p] + \frac{1}{2}\frac{\partial^2}{\partial x^2}[\sigma^2(x)p]$$

**直觉**：密度函数的"守恒律"——概率的漂移 + 扩散。

**ML 意义**：扩散模型中，前向过程 $p(x,t)$ 的演化由 Fokker-Planck 方程描述。反向过程需要逆向 Fokker-Planck。

### 1.6 Langevin 方程与不变分布 ★

**Langevin SDE**：
$$dX_t = -\nabla U(X_t)\,dt + \sqrt{2}\,dW_t$$

其中 $U(x)$ 是势函数。

**定理**：不变分布（平稳分布）为 $\pi(x) \propto e^{-U(x)}$（玻尔兹曼分布）。

**证明思路**：代入 Fokker-Planck 方程，验证 $p = e^{-U}$ 使 $\partial p/\partial t = 0$。

**ML 应用**：Langevin 采样 = MCMC。想从 $\pi(x) \propto e^{-U(x)}$ 采样？解 Langevin SDE 即可。

### 1.7 反向 SDE ★（扩散模型核心）

如果前向 SDE 为 $dX = f(X,t)\,dt + g(t)\,dW$，则**反向 SDE**（Anderson 1982）：
$$d\tilde{X} = \left[f(\tilde{X},t) - g(t)^2 \nabla_{\tilde{X}} \log p_t(\tilde{X})\right]dt + g(t)\,d\tilde{W}$$

关键：反向过程需要**分数函数** $\nabla_x \log p_t(x)$。

**扩散模型的核心思想**（Song et al. 2021, [2011.13456](https://arxiv.org/abs/2011.13456) ✅）：
1. 前向：数据 → 噪声（已知 SDE）
2. 学习分数函数 $\nabla_x \log p_t(x)$（神经网络）
3. 反向：噪声 → 数据（逆向 SDE 数值解）

### 1.8 Girsanov 定理

**定理**：通过改变漂移项（加一个适应性过程），可以改变测度。

$$\text{在测度 } \mathbb{Q} \text{ 下}: dW^\mathbb{Q} = dW^\mathbb{P} + \theta\,dt$$

Radon-Nikodym 导数：
$$\frac{d\mathbb{Q}}{d\mathbb{P}} = \exp\left(-\int_0^T \theta\,dW - \frac{1}{2}\int_0^T \theta^2\,dt\right)$$

**应用**：金融中定价衍生品（风险中性测度）；ML 中变分推断（改变测度优化 ELBO）。

---

## 二、代码层：SDE 数值模拟

### 2.1 Euler-Maruyama 方法

```python
import numpy as np
import matplotlib.pyplot as plt

def euler_maruyama(mu, sigma, x0, T, N, n_paths=1):
    """dX = mu(X)dt + sigma(X)dW 的 Euler-Maruyama 数值解"""
    dt = T / N
    dW = np.sqrt(dt) * np.random.randn(n_paths, N)
    X = np.zeros((n_paths, N + 1))
    X[:, 0] = x0
    for i in range(N):
        X[:, i+1] = X[:, i] + mu(X[:, i]) * dt + sigma(X[:, i]) * dW[:, i]
    return X

# Ornstein-Uhlenbeck 过程: dX = -θX dt + σ dW (均值回归)
theta, sigma = 2.0, 0.5
X = euler_maruyama(lambda x: -theta * x, lambda x: sigma, x0=3.0, T=5, N=1000, n_paths=50)
t = np.linspace(0, 5, 1001)
for path in X[:10]:
    plt.plot(t, path, alpha=0.3)
plt.axhline(0, color='r', ls='--', label='平稳均值=0')
plt.xlabel('t'); plt.ylabel('X_t'); plt.title('OU 过程: 均值回归')
plt.savefig('ou_process.png', dpi=150); plt.show()
```

### 2.2 Langevin 采样验证玻尔兹曼分布

```python
# 目标分布: π(x) ∝ exp(-U(x)), U(x) = x^4/4 - x^2/2 (双井势)
# Langevin SDE: dX = -∇U(X) dt + √2 dW
U = lambda x: x**4 / 4 - x**2 / 2
grad_U = lambda x: x**3 - x  # ∇U

samples = euler_maruyama(lambda x: -grad_U(x), lambda x: np.sqrt(2),
                          x0=0, T=100, N=10000, n_paths=1)
samples = samples[0, 5000:]  # 丢弃 burn-in

x_grid = np.linspace(-2, 2, 200)
target = np.exp(-U(x_grid))
target /= target.sum() * (x_grid[1] - x_grid[0])

plt.hist(samples, bins=50, density=True, alpha=0.5, label='Langevin 采样')
plt.plot(x_grid, target, 'r-', lw=2, label='$e^{-U}$ (目标)')
plt.legend(); plt.title('Langevin 采样 → 玻尔兹曼分布')
plt.savefig('langevin_sampling.png', dpi=150); plt.show()
```

### 2.3 扩散模型前向过程（加噪）

```python
# DDPM 前向: x_t = sqrt(α̅_t) x_0 + sqrt(1-α̅_t) ε, ε~N(0,I)
def forward_diffusion(x0, T=100):
    betas = np.linspace(0.001, 0.02, T)
    alphas = 1 - betas
    alpha_bar = np.cumprod(alphas)
    noise = np.random.randn(*x0.shape)
    x_t = np.sqrt(alpha_bar[-1]) * x0 + np.sqrt(1 - alpha_bar[-1]) * noise
    return x_t, noise

# 这就是热方程的离散化: 数据 → 噪声
```

完整实验见 [ETH 401-3651 SDE experiments](../../eth-math-courses/e401_3651_numerical_sde/experiments/)（本课与其互补，ETH 更偏数值，Oxford 更偏理论）。

---

## 三、与 ML 的联系 ★

### 3.1 扩散模型 = 反向 SDE ★

DDPM（Ho et al. 2020）和 Score-based 模型（Song et al. 2021）的理论基础是**反向 SDE**。详见 §1.7。

### 3.2 Langevin MCMC = SDE 采样

Langevin SDE $dX = -\nabla U dt + \sqrt{2}\,dW$ 是最简单的 MCMC 方法之一。

**SGLD**（Stochastic Gradient Langevin Dynamics, Welling & Teh 2011, [1103.4140](https://arxiv.org/abs/1103.4140) ✅）：用随机梯度近似 $\nabla U$ → 大规模贝叶斯推断。

### 3.3 随机优化 = SDE 的漂移近似

SGD 的连续化：$d\theta = -\nabla L(\theta)\,dt + \sigma(\theta)\,dW$。噪声来自 mini-batch 采样。SDE 理论可分析 SGD 的收敛和泛化。

### 3.4 强化学习 = SDE 控制

连续控制的 POMDP 经常用 SDE 建模环境动态：$dX = f(X, u)\,dt + \sigma\,dW$。

### 3.5 变分推断与 ELBO

VAE 和扩散模型的 ELBO 可以从 SDE 视角推导——Girsanov 定理给出精确的 Radon-Nikodym 导数。

---

## 四、不足层与边界

1. **Itô vs Stratonovich**：本课主要用 Itô 积分（金融/ML 标准）。Stratonovich 积分在物理中更常见（链式法则保持普通形式）。两者的选择影响 SDE 的物理诠释。
2. **高维 SDE 很难**：理论优美，但 $n > 100$ 维时数值求解非常昂贵。扩散模型在几百到几千维中运作，需要特殊技巧（score matching + amortized inference）。
3. **分数不匹配**：反向 SDE 需要分数函数 $\nabla \log p_t$，但真实数据的 $p_t$ 未知。必须用神经网络近似——这是工程难点，不是数学难点。

---

## 五、应用层速查

| 应用 | SDE 工具 | 效果 |
|---|---|---|
| **扩散模型** | 反向 SDE | DDPM/Score-based 生成 |
| **Langevin MCMC** | 不变分布 | 贝叶斯采样 |
| **SGLD** | 随机梯度 + Langevin | 大规模贝叶斯 |
| **金融定价** | Girsanov + Feynman-Kac | Black-Scholes |
| **随机优化** | SGD = 带噪梯度流 | 分析泛化 |
| **强化学习** | 受控 SDE | 连续控制 |

---

## 六、推荐路径

1. **Oksendal 第 2-5 章**：布朗运动 + Itô 积分 + Itô 引理 + SDE → **核心**
2. **Oksendal 第 8 章**：Fokker-Planck / Kolmogorov 方程 → **理解扩散模型的关键**
3. **跳过**：最优停时、滤波理论（除非做量化金融）
4. **交叉**：[ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（数值实现）+ [Princeton MAT 322 PDE](../../princeton-math-courses/mat322_pde/)（确定性 PDE 对照）

---

## 术语对照

| 英文 | 中文 |
|---|---|
| Brownian motion / Wiener process | 布朗运动 / Wiener 过程 |
| Itô integral | Itô 积分 |
| Itô's lemma | Itô 引理（链式法则）|
| Quadratic variation | 二次变差 |
| Fokker-Planck equation | Fokker-Planck 方程（前向 Kolmogorov）|
| Backward Kolmogorov | 后向 Kolmogorov 方程 |
| Langevin equation | 朗之万方程 |
| Score function | 分数函数 $\nabla \log p$ |
| Reverse SDE | 反向 SDE |
| Girsanov theorem | Girsanov 测度变换 |
| Feynman-Kac | 费曼-卡茨公式 |
| Euler-Maruyama | EM 数值方法 |
