# ETH 401-3651 · 习题集（精选 + 解题思路）

> **来源**：Higham (2001) SIAM Review 习题 + Kloeden & Platen 习题 + 自编

---

## 第 1 章 · 布朗运动与 Itô 积分

### Q1.1（基础）
计算 $\int_0^T W_t\,dW_t$（其中 $W_t$ 是标准布朗运动）。

<details><summary>解</summary>

用 Itô 公式于 $f(x) = x^2/2$：$df(W_t) = W_t\,dW_t + \frac12\cdot 1\cdot dt$（$f''=1$，$b=1$）。

$$\frac12 W_T^2 = \int_0^T W_t\,dW_t + \frac12 T$$

$$\boxed{\int_0^T W_t\,dW_t = \frac12 W_T^2 - \frac12 T}$$

> **关键**：确定性积分会给 $\frac12 W_T^2$，多出的 $-\frac12 T$ 是 Itô 校正项！
</details>

### Q1.2（基础）
证明 $\mathbb{E}\left[\int_0^T b(t)\,dW_t\right] = 0$（$b$ 确定性）。

<details><summary>解</summary>

Itô 积分定义为 $\sum b(t_i)(W_{t_{i+1}} - W_{t_i})$ 的极限。每项中 $b(t_i)$ 确定性，增量 $\Delta W \sim \mathcal{N}(0, \Delta t)$ 均值 0。故 $\mathbb{E}[\text{每项}] = 0$，取极限仍 0。

**Itô 等距**（Itô isometry）：$\mathbb{E}\left[\left(\int b\,dW\right)^2\right] = \int b^2\,dt$。
</details>

### Q1.3（中等）
对几何布朗运动 $dX = \mu X\,dt + \sigma X\,dW$，求 $X_t$ 的显式解。

<details><summary>解</summary>

用 Itô 公式于 $f(x) = \log x$：$f' = 1/x, f'' = -1/x^2$。
$$d(\log X) = \frac{1}{X}dX - \frac{1}{2X^2}(dX)^2 = \left(\mu - \frac{\sigma^2}{2}\right)dt + \sigma\,dW$$

积分：$\log X_t = \log X_0 + (\mu - \sigma^2/2)t + \sigma W_t$。
$$\boxed{X_t = X_0 \exp\left[\left(\mu - \frac{\sigma^2}{2}\right)t + \sigma W_t\right]}$$

**ML 关联**：Black-Scholes 模型；DDPM 的状态演化。
</details>

---

## 第 2 章 · Euler-Maruyama 与 Milstein

### Q2.1（基础）
对 SDE $dX = \lambda X\,dt + \mu X\,dW$（OU 过程的变体），写 Euler-Maruyama 格式。

<details><summary>解</summary>

$$X_{n+1} = X_n(1 + \lambda\Delta t) + \mu X_n \Delta W_n, \quad \Delta W_n = \sqrt{\Delta t}\,\xi_n, \xi_n \sim \mathcal{N}(0,1)$$

注意 $\Delta W \sim O(\sqrt{\Delta t})$，所以 $\mu X \Delta W \sim O(\sqrt{\Delta t})$ 主导截断误差。
</details>

### Q2.2（中等）
用 Milstein 格式解 Q2.1 的 SDE，并与 Euler-Maruyama 比较强收敛。

<details><summary>解</summary>

$b(x) = \mu x$，$b'(x) = \mu$。Milstein：
$$X_{n+1} = X_n + \lambda X_n\Delta t + \mu X_n\Delta W_n + \frac12\mu^2 X_n[(\Delta W_n)^2 - \Delta t]$$

额外项 $\frac12\mu^2 X_n[(\Delta W)^2 - \Delta t] \sim O(\Delta t)$（因 $(\Delta W)^2 \approx \Delta t$），提升了精度。

**强收敛阶**：Euler-Maruyama = 0.5，Milstein = 1.0。见 [experiments](experiments/euler_maruyama_sde.py) 验证。
</details>

### Q2.3（中等）
强收敛与弱收敛的区别是什么？为什么期权定价用弱收敛就够了？

<details><summary>解</summary>

- **强收敛**：$\mathbb{E}|X_T - X_N|$ 小——同一布朗运动驱动的数值解与精确解**逐条路径**逼近
- **弱收敛**：$|\mathbb{E}[g(X_T)] - \mathbb{E}[g(X_N)]|$ 小——只要求**分布**/期望逼近

期权定价只需 $\mathbb{E}[\text{payoff}(S_T)]$，**不需要逐条路径**，故弱收敛 $O(\Delta t)$ 的 Euler-Maruyama 足够。但若要研究单条价格的分位数/路径依赖期权，需要强收敛。

**ML 关联**：扩散模型采样只需弱收敛（生成的分布对即可），故 DDPM 用 Euler-Maruyama。
</details>

### Q2.4（开放）
多级蒙特卡洛 (MLMC) 如何加速 SDE 的期望估计？

<details><summary>提示</summary>

MLMC（Giles 2008）：在粗网格（$\Delta t$）和细网格（$\Delta t/2$）上配对模拟，用**差值** $X_\ell - X_{\ell-1}$ 的方差小（同一条粗路径驱动）。

总复杂度从 $O(\epsilon^{-3})$（标准 MC + Euler-Maruyama）降到 $O(\epsilon^{-2})$（MLMC）——达到理论最优。

**ML 关联**：扩散模型采样加速、不确定性量化的前沿。⚠️ 具体加速比对需查最新文献。
</details>

---

## 第 3 章 · 扩散模型与 Langevin

### Q3.1（基础）
OU 过程 $dX = -X\,dt + dW$ 的平稳分布是什么？

<details><summary>解</summary>

Fokker-Planck：$\partial_t p = \partial_x(xp) + \frac12\partial_{xx}p$。稳态 $\partial_t p = 0$：$\partial_x(xp) + \frac12\partial_{xx}p = 0$。

解：$p_\infty(x) = \frac{1}{\sqrt{\pi}}e^{-x^2}$（标准正态）。

**ML 关联**：OU 过程是 DDPM 前向扩散的连续版本——把数据"污染"成高斯。
</details>

### Q3.2（中等）
写出 DDPM 对应的连续正向 SDE 和反向 SDE（VP SDE）。

<details><summary>解</summary>

**VP (Variance Preserving) SDE**（对应 DDPM）：
- 正向：$dX = -\frac12\beta(t)X\,dt + \sqrt{\beta(t)}\,dW$
- 反向：$d\bar{X} = \left[-\frac12\beta(t)\bar{X} - \beta(t)\nabla_x\log p_t(\bar{X})\right]dt + \sqrt{\beta(t)}\,d\bar{W}$

$\nabla_x\log p_t$ = score function，用神经网络 $s_\theta(x,t)$ 估计。

**VE (Variance Exploding) SDE**（对应 NCSN/score-matching）：
- 正向：$dX = \sqrt{\frac{d[\sigma^2(t)]}{dt}}\,dW$
</details>

### Q3.3（开放）
为什么 score matching 训练 $s_\theta \approx \nabla\log p_t$ 比直接最大化 $\log p_t$ 容易？

<details><summary>提示</summary>

直接最大化 $\log p_0$（数据似然）需要积分掉所有隐变量（反向 SDE 的所有路径），intractable。

Score matching（Hyvärinen 2005, Vincent 2011）用去噪目标：
$$\mathcal{L} = \mathbb{E}_{x_0, \epsilon, t}\left[\|s_\theta(x_t, t) - \nabla_{x_t}\log p(x_t|x_0)\|^2\right]$$

其中 $\nabla_{x_t}\log p(x_t|x_0) = -(x_t - \sqrt{\bar\alpha_t}x_0)/\sqrt{1-\bar\alpha_t}$（高斯条件）。

这把 intractable 似然转成**可计算的回归**——DDPM 训练损失。详见 [2011.13456](https://arxiv.org/abs/2011.13456), [2006.11239](https://arxiv.org/abs/2006.11239) ✅。
</details>

### Q3.4（开放）
Langevin 采样 $\theta_{t+1} = \theta_t - \frac\eta2\nabla U(\theta_t) + \sqrt{\eta}\xi_t$ 收敛到什么分布？与 SGD 的关系？

<details><summary>提示</summary>

Langevin SDE $d\theta = -\frac12\nabla U d t + dW$ 的平稳分布 $\propto e^{-U}$。

SGLD（SGD 加噪声）= 离散 Langevin → 训练后期权重的**后验采样**而非点估计，用于贝叶斯神经网络、不确定性估计。Mangoubi & Vishnoi 等证明非凸 Langevin 的 mixing 时间与维数/条件数的关系（2019-2024 前沿）⚠️。
</details>

### Q3.5（开放 — 2024 前沿）
一致性模型（Consistency Models, [2303.01469](https://arxiv.org/abs/2303.01469)）如何绕过反向 SDE 的逐步求解？

<details><summary>提示</summary>

一致性模型 $f_\theta(x_t, t) \to x_0$（直接映射任意噪声到原图），训练目标：沿 ODE/SDE 轨迹的"一致性" $f(x_t, t) = f(x_{t'}, t')$。

优点：**一步生成**（vs DDPM 的 1000 步反向 SDE）。2024 的改进：Latent Consistency Model、sCM 等，把质量接近 GAN/Diffusion。⚠️ 具体细节需跟踪最新文献。
</details>
