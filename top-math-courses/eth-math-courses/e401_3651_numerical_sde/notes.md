# ETH 401-3651 · 费曼三层讲透：随机微分方程的数值解

> **教材**：**Kloeden & Platen, *Numerical Solution of SDEs*** (Springer, 1992) ★
> **入门读物**：Higham, *An Algorithmic Introduction to Numerical Simulation of SDE* (SIAM Review, 2001) ✅
> **ML 关联**：扩散模型 (DDPM) = SDE 数值解；Score-based 生成 = 反向 SDE

---

# 费曼三层讲透：数值 SDE 到底在研究什么？

## 🧠 直觉层（1 句话比喻）

| 概念 | 比喻 |
|---|---|
| **布朗运动 $W_t$** | **"永远在抖动的随机游走"**——每瞬间都不可微，方差 $\propto t$ |
| **Itô SDE** | **"确定性漂移 + 随机抖动"**——$dX_t = \underbrace{a(X_t)dt}_{\text{趋势}} + \underbrace{b(X_t)dW_t}_{\text{噪声}}$ |
| **Itô 积分** | **"把抖动累加起来"**——$\int b\,dW$，但因为 $dW \sim \sqrt{dt}$，不能像普通积分算 |
| **Itô 公式** | **"随机版的链式法则，多一个修正项"**——$df = f'dX + \frac12 f'' b^2 dt$，多了 $\frac12$ 项！ |
| **Euler-Maruyama** | **"随机版的 Euler 方法"**——$X_{n+1} = X_n + a(X_n)\Delta t + b(X_n)\sqrt{\Delta t}\,\xi$ |
| **Milstein 格式** | **"Euler-Maruyama + Itô Taylor 二阶修正"**——更精确，强收敛 1.0 |
| **强收敛 vs 弱收敛** | **"路径对 vs 分布对"**——强收敛关心逐条路径，弱收敛只关心期望/分布 |
| **反向 SDE** | **"时间倒流的扩散"**——把噪声变数据，这是 score-based 生成的核心 |

> **一句话总结**：**数值 SDE = "在抖动的世界里做数值积分"**。关键区别：普通 ODE 的误差 $O(\Delta t)$，SDE 因 $dW \sim \sqrt{\Delta t}$ 误差降到 $O(\sqrt{\Delta t})$。**扩散模型 = 求反向 SDE 的数值解**。

---

## 🧮 数学层（核心定义 + 定理 + LaTeX）

### 1. 布朗运动（Brownian Motion / Wiener 过程）

$W_t$ 满足：
1. $W_0 = 0$
2. $W_t - W_s \sim \mathcal{N}(0, t-s)$（增量正态，独立于过去）
3. 轨道连续但**几乎处处不可微**

**关键增量**：$\Delta W = W_{t+\Delta t} - W_t \sim \sqrt{\Delta t}\,\mathcal{N}(0,1)$
$$\mathbb{E}[\Delta W] = 0, \quad \mathbb{E}[(\Delta W)^2] = \Delta t, \quad \Delta W \sim O(\sqrt{\Delta t})$$

> **这是 SDE 数值方法与 ODE 的根本区别**：ODE 截断误差 $O(\Delta t)$，SDE 因 $\Delta W$ 的随机性主导。

### 2. Itô SDE

$$dX_t = a(X_t, t)\,dt + b(X_t, t)\,dW_t$$

- $a$：**漂移系数**（确定性趋势）
- $b$：**扩散系数**（噪声强度）

### 3. Itô 积分

$$\int_0^T b(X_t, t)\,dW_t = \lim_{\|\pi\|\to 0}\sum_i b(X_{t_i}, t_i)(W_{t_{i+1}} - W_{t_i})$$

**关键**：被积函数取**左端点** $b(X_{t_i})$（不可预见性 / adapted）。这导致 Itô 积分不同于 Stratonovich（取中点）。

### 4. Itô 公式（随机链式法则）★★★

对 $Y_t = f(X_t)$（$X_t$ 满足 Itô SDE）：
$$df(X_t) = f'(X_t)\,dX_t + \frac{1}{2}f''(X_t)(dX_t)^2$$

展开 $(dX_t)^2 = (a\,dt + b\,dW)^2 = b^2(dW)^2 + \text{高阶项} = b^2\,dt$（用 $(dW)^2 = dt$）：
$$\boxed{df(X_t) = \left[f'a + \frac12 f'' b^2\right]dt + f'b\,dW_t}$$

> **对比确定性链式法则**：多了 $\frac12 f'' b^2 dt$ 项——**Itô 校正项**。这是 Black-Scholes、Fokker-Planck、反向 SDE 的核心。

### 5. Fokker-Planck 方程（SDE → PDE）

$X_t$ 的概率密度 $p(x, t)$ 满足：
$$\frac{\partial p}{\partial t} = -\frac{\partial}{\partial x}[a(x)p] + \frac12\frac{\partial^2}{\partial x^2}[b(x)^2 p]$$

> **ML 关联**：正向扩散 = Fokker-Planck 演化；反向 SDE = Fokker-Planck 时间倒流。

### 6. Euler-Maruyama 格式 ★

$$X_{n+1} = X_n + a(X_n)\Delta t + b(X_n)\Delta W_n, \quad \Delta W_n = \sqrt{\Delta t}\,\xi_n,\ \xi_n \sim \mathcal{N}(0,1)$$

**强收敛阶**：$O(\sqrt{\Delta t})$（路径误差）
**弱收敛阶**：$O(\Delta t)$（期望/分布误差）

### 7. Milstein 格式

$$X_{n+1} = X_n + a(X_n)\Delta t + b(X_n)\Delta W_n + \frac12 b(X_n)b'(X_n)\left[(\Delta W_n)^2 - \Delta t\right]$$

**强收敛阶**：$O(\Delta t)$（比 Euler-Maruyama 强一阶！）

> 额外项 $\frac12 b b'[(\Delta W)^2 - \Delta t]$ 来自 Itô-Taylor 展开的二阶项。

### 8. 强收敛 vs 弱收敛 ★

- **强收敛阶 $\gamma$**：$\mathbb{E}|X_T - X_N| \leq C(\Delta t)^\gamma$（**逐条路径**逼近）
- **弱收敛阶 $\beta$**：$|\mathbb{E}[g(X_T)] - \mathbb{E}[g(X_N)]| \leq C(\Delta t)^\beta$（**分布**逼近，$g$ 光滑）

| 格式 | 强收敛 | 弱收敛 |
|---|---|---|
| Euler-Maruyama | 0.5 | 1.0 |
| Milstein | 1.0 | 1.0 |
| 高阶 Runge-Kutta | 1.5+ | 2.0+ |

### 9. 反向 SDE（扩散模型核心）★★★

Anderson (1982) 证明：正向 SDE $dX_t = f(X_t,t)dt + g(t)dW_t$ 的**时间反向**也是 SDE：
$$d\bar{X}_t = \left[-f(\bar{X}_t, t) + g(t)^2 \nabla_x \log p_t(\bar{X}_t)\right]dt + g(t)\,d\bar{W}_t$$

其中 $\bar{W}_t$ 是反向布朗运动，$\nabla_x \log p_t$ 是 **score function**。

> **这是 Score-Based 生成模型 (Song et al. [2011.13456](https://arxiv.org/abs/2011.13456) ✅) 的数学核心**：训练一个神经网络 $s_\theta(x,t) \approx \nabla_x \log p_t(x)$ 估计 score，然后数值求解反向 SDE 生成样本。

### 10. Langevin 动力学（采样）

$$dX_t = -\nabla U(X_t)\,dt + \sqrt{2}\,dW_t$$

平稳分布 $\propto e^{-U(x)}$。**采样 = 让 SDE 跑到稳态**。

> **ML 关联**：能量模型采样、score matching、diffusion 的训练阶段。

---

## 💻 代码层（numpy 实现）

### Euler-Maruyama

```python
import numpy as np
import matplotlib.pyplot as plt

def euler_maruyama(a, b, x0, T, N, n_paths=1):
    """dX = a(X) dt + b(X) dW 的 Euler-Maruyama 数值解
       N: 时间步数, Δt = T/N
    """
    dt = T / N
    dW = np.sqrt(dt) * np.random.randn(n_paths, N)
    X = np.zeros((n_paths, N + 1))
    X[:, 0] = x0
    for i in range(N):
        X[:, i+1] = X[:, i] + a(X[:, i]) * dt + b(X[:, i]) * dW[:, i]
    return X

# 几何布朗运动 dX = μ X dt + σ X dW (Black-Scholes)
mu, sigma = 0.1, 0.3
X = euler_maruyama(lambda x: mu*x, lambda x: sigma*x, x0=1.0, T=1.0, N=1000, n_paths=50)
t = np.linspace(0, 1, 1001)
plt.plot(t, X.T, alpha=0.3)
plt.plot(t, np.exp(mu*t), 'r--', label=f'deterministic $e^{{\\mu t}}$')
plt.legend(); plt.savefig('gbm_paths.png', dpi=100)
```

### Milstein 格式

```python
def milstein(a, b, b_prime, x0, T, N, n_paths=1):
    """Milstein: 多一个 Itô 校正项 0.5 b b' ((dW)^2 - dt)"""
    dt = T / N
    dW = np.sqrt(dt) * np.random.randn(n_paths, N)
    X = np.zeros((n_paths, N + 1))
    X[:, 0] = x0
    for i in range(N):
        X[:, i+1] = (X[:, i] + a(X[:, i]) * dt + b(X[:, i]) * dW[:, i]
                     + 0.5 * b(X[:, i]) * b_prime(X[:, i]) * (dW[:, i]**2 - dt))
    return X
```

### Langevin 采样

```python
def langevin_sampling(score_fn, x0, n_steps=1000, step_size=0.01):
    """过阻尼 Langevin: dX = score(X) dt + √(2) dW (采样 ∝ exp(∫score))"""
    x = x0.copy()
    trajectory = [x.copy()]
    for _ in range(n_steps):
        x = x + step_size * score_fn(x) + np.sqrt(2 * step_size) * np.random.randn(*x.shape)
        trajectory.append(x.copy())
    return np.array(trajectory)
```

### 反向 SDE（扩散模型简化版）

```python
def reverse_sde(score_fn, shape, T=1.0, N=1000):
    """反向 SDE: 从纯噪声开始, 用 score 逐步去噪 (扩散模型核心)
       dX = [-f - g^2 score(X,t)] dt + g dW  (dt>0 表示反向时间参数化)
    """
    dt = T / N
    x = np.random.randn(*shape)  # 起始: 标准高斯 (T 时刻的分布)
    for i in range(N):
        t = T - i * dt  # 反向时间
        g = 1.0  # 扩散系数 (简化)
        f = 0.0  # 漂移 (简化: VP SDE)
        drift = -f - g**2 * score_fn(x, t)
        x = x + drift * dt + g * np.sqrt(dt) * np.random.randn(*x.shape)
    return x
```

---

## ⚠️ 不足层（局限）

| 局限 | 说明 |
|---|---|
| **Euler-Maruyama 强收敛仅 $O(\sqrt{\Delta t})$** | 比 ODE 的 $O(\Delta t)$ 慢一阶，需更细的网格 |
| **Milstein 需要 $b'(x)$** | 多维时 $b$ 是矩阵，$b'$ 难算（需要 Itô 张量）|
| **高阶格式极复杂** | 随机 Runge-Kutta / Itô-Taylor 展开项数爆炸 |
| **稀疏跳过程的 SDE 不同** | Lévy 驱动的 SDE 需要专门的数值格式 |
| **强收敛对路径敏感** | 多维时每步需要相关的高斯向量 |
| **多级蒙特卡洛 (MLMC)** | 用粗细网格差降低方差，但实现复杂 |
| **反向 SDE 依赖 score 精度** | score 估计误差 → 生成质量差，需大网络 + 长训练 |

---

## 🔬 应用层（ML 公式级对应）

### 1. 扩散模型 DDPM = Euler-Maruyama 求反向 SDE（[2006.11239](https://arxiv.org/abs/2006.11239) ✅）
$$x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{1-\alpha_t}{\sqrt{1-\bar\alpha_t}}\epsilon_\theta(x_t,t)\right) + \sigma_t z$$
$\epsilon_\theta$ 是噪声预测网络，本质是 Euler-Maruyama 解反向 SDE。

### 2. Score-Based 生成 = 反向 SDE（[2011.13456](https://arxiv.org/abs/2011.13456) ✅）
$$d\bar{X} = [-f(\bar{X},t) + g(t)^2 \nabla\log p_t(\bar{X})]dt + g(t)d\bar{W}$$
$s_\theta \approx \nabla\log p_t$，score matching 训练。

### 3. Langevin 采样 = 能量模型推断
$$dX = -\nabla U(X)dt + \sqrt{2}dW \;\Rightarrow\; p_\infty \propto e^{-U}$$

### 4. Black-Scholes 定价 = SDE 数值
$$dS = \mu S\,dt + \sigma S\,dW \;\Rightarrow\; \text{期权价格} = e^{-rT}\mathbb{E}[\max(S_T - K, 0)]$$

### 5. 神经网络训练 = Langevin / SGLD
SGD 加噪声 ≈ Langevin dynamics，$U = $ 损失函数。SGLD（[1511.03641](https://arxiv.org/abs/1511.03641) ⚠️）用此做贝叶斯神经网络。

---

## 📚 章节结构对照（Kloeden & Platen）

| 章 | 主题 | 重要性 |
|---|---|---|
| 1-2 | 概率/随机过程基础 | ★ |
| 3 | Itô / Stratonovich 积分 | ★★ |
| 4 | Itô 公式与随机 Taylor 展开 | ★★★ |
| 5-7 | **Euler-Maruyama / Milstein** | ★★★ |
| 8-9 | 强 / 弱收敛分析 | ★★ |
| 10-13 | 高阶格式（Itô-Taylor, Runge-Kutta）| ★ |
| 14-16 | **Monte Carlo, MLMC** | ★★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透扩散模型**：第 4-7 章（Itô 公式 + Euler-Maruyama + 反向 SDE）
- **讲透 Score-Based 生成**：第 4 章（反向 SDE 推导）
- **讲透 Langevin 采样**：第 1-2 章 + Fokker-Planck
- **讲透 SGLD/贝叶斯神经网络**：第 7 章 + Langevin
