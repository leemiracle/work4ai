# 09 — 能量模型与 Score-based：Diffusion 的理论源头

> 08 讲 Flow Matching（diffusion 的工程改进）。本篇挖到**理论源头**——能量模型（EBM）和 score matching。它们在 diffusion 之前就提出了"学数据分布的梯度"这个思想，是理解所有生成模型统一视角的钥匙。

---

## 1. 灵魂：学分布的"坡度"

$$
\boxed{\text{Score} = \nabla_x \log p(x) \quad \text{（数据分布的对数概率的梯度）}}
$$

- 能量模型：定义 $p(x) = \frac{e^{-E(x)}}{Z}$，学能量函数 $E(x)$
- **Score-based**：不学 $E$，直接学 $\nabla_x \log p(x) = -\nabla_x E(x)$——分布的"坡度"

> 🎯 **直觉**：想象数据分布是一座山，score 是山面的坡度。**沿坡度往上走 → 走到山顶（数据密集区）**。生成 = 从随机点出发，沿 score 爬到数据。

---

## 2. 为什么学 score 而非概率

学 $p(x)$ 要归一化（算 $Z$）——高维空间不可行。

学 score $\nabla_x \log p(x)$ **不需要 $Z$**（因为 $\log Z$ 的梯度是 0）：

$$
\nabla_x \log p(x) = \nabla_x \log e^{-E(x)} - \nabla_x \log Z = -\nabla_x E(x)
$$

这就是**避开了配分函数**的妙招。

---

## 3. Score Matching（怎么学 score）

### 3.1 经典 score matching（Hyvärinen 2005）

目标：$\min_\theta \mathbb{E}\left[\|s_\theta(x) - \nabla_x \log p(x)\|^2\right]$

问题：$\nabla_x \log p(x)$ 未知（正是我们要学的）。Hyvärinen 证明可以**用积分变换绕过**，只用数据样本——但需要二阶导（数值不稳）。

### 3.2 Denoising Score Matching（DSM）

加噪 $x_{\text{noisy}} = x + \sigma \epsilon$，学"去噪方向"：

$$
\min_\theta \mathbb{E}\left[\left\|s_\theta(x_{\text{noisy}}) + \frac{\epsilon}{\sigma}\right\|^2\right]
$$

**这和 DDPM 预测噪声是等价的**——DDPM 的 $\epsilon$-prediction 就是 score matching。

---

## 4. Langevin 采样（用 score 生成）

有了 score $s_\theta(x)$，用 **Langevin 动力学**生成：

$$
x_{t+1} = x_t + \frac{\eta}{2} s_\theta(x_t) + \sqrt{\eta} \cdot \epsilon
$$

- 沿 score 走（爬坡，趋向数据）
- 加噪声（避免卡在局部）
- 收敛到 $p(x)$

**这就是 diffusion 反向采样的连续版**——SDE 采样。

---

## 5. 统一：Diffusion = Score + 多尺度噪声

Song & Ermon 2019（Score-based generative）的关键洞察：

**单一尺度的 score 在低密度区域不准**（数据稀疏处学不好）。解法：**加多个尺度的噪声**，每个尺度学一个 score，采样时从粗到细。

$$
\{\sigma_1 > \sigma_2 > \cdots > \sigma_N\} \to \text{每个 } \sigma_i \text{ 训一个 score 网络}
$$

**这就是 diffusion 的本质**——多尺度噪声 + score matching + Langevin 采样。

---

## 6. EBM / Score / Diffusion / Flow 的统一

| 方法 | 学什么 | 采样 |
|---|---|---|
| EBM | 能量 $E(x)$ | MCMC（慢）|
| Score-based | $\nabla_x \log p$ | Langevin |
| **Diffusion** | 多尺度 score | 反向 SDE |
| Flow Matching | 速度场 $v$ | 反向 ODE |

**它们都是"学分布的某种梯度，然后沿梯度生成"**——只是梯度的定义和采样的路径不同。讲透生成模型 06 章的"统一视角"就是这层。

---

## 7. 批判性

- **EBM 理论美但工程难**：训练不稳定（MCMC 采样慢、模式坍缩）
- **Score matching 在高维仍有限**：低密度区域的 score 估计不准，导致生成多样性下降
- **被 diffusion "实用化"**：纯 score-based 不如 diffusion（多尺度噪声），但理论上是同一回事

> **诚实结论**：EBM 和 score 是生成模型的"深层理论"——理解它们，diffusion 就不再是黑箱。但工程上，diffusion（多尺度噪声 + 反向 SDE）才是落地赢家。

---

## 📌 下一步

[10-神经符号AI](10-神经符号AI.md)——离开"连续生成"路线，进入"非深度学习范式"：神经网络 + 符号逻辑的融合。

## ✍️ 练习

1. 为什么学 score $\nabla_x \log p$ 不需要算配分函数 $Z$？（提示：$\log Z$ 对 $x$ 的梯度是 0。）
2. Denoising Score Matching 和 DDPM 的 $\epsilon$-prediction 等价。这意味着 diffusion 本质是 score-based 吗？
3. 如果只在一个尺度学 score（不加多尺度噪声），生成会出什么问题？（提示：低密度区域 score 不准 → 模式覆盖差。）
