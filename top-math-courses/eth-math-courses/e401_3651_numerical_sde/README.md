# ETH 401-3651 — Numerical Solution of Stochastic Differential Equations

> **学校**：ETH Zurich | **学院**：D-MATH
> **一手来源**：[vvz.ethz.ch](https://www.vvz.ethz.ch) + [math.ethz.ch](https://math.ethz.ch)

## 课程信息
- **编号**：401-3651-00L（研究生）
- **教材**：**Kloeden & Platen, *Numerical Solution of Stochastic Differential Equations*** ★
- **特色**：**ETH 数值 SDE 顶级课**——金融数学 / 扩散模型基础

## 教学大纲
1. Brownian motion review
2. Itô SDE 回顾
3. **Euler-Maruyama method** ★
4. **Milstein scheme**
5. **Strong vs weak convergence**
6. **Stochastic Taylor expansion**
7. **Runge-Kutta for SDE**
8. **Monte Carlo methods**
9. **Multilevel Monte Carlo**
10. **Applications**: financial derivatives, diffusion models

## 与 ML 的关联（**扩散模型核心数学**）
- **扩散模型 = SDE 数值解**：DDPM 用 Euler-Maruyama
- **Score-based models**：与 SDE 数值解紧密相关
- **学完后**：能从数值 SDE 视角实现 DDPM

## 参考资源
- Kloeden & Platen, *Numerical Solution of SDEs* (Springer, 1992)
- Higham, *An Algorithmic Introduction to Numerical Simulation of SDE* (SIAM Review, 2001) — 入门小册子
- 配合：[Oxford C8.1 SDE](../../oxford-math-courses/partC_c8_1_sde/)

📌 **下一步**：→ [401-3901 Linear & Combinatorial Optimization](../e401_3901_linear_combinatorial_optimization/)

---

## 📍 在数学全景中的位置

```
概率论 + 随机过程 (布朗运动, 鞅)
        │
        ▼
Itô 积分 / Itô 公式 (Oxford C8.1, UT Austin 387D)
        │
        ▼
本课: 数值 SDE ────► Euler-Maruyama / Milstein
        │              强/弱收敛分析
        │
        ├──► 扩散模型 (DDPM [2006.11239], Score SDE [2011.13456])
        ├──► Langevin 采样 / SGLD 贝叶斯神经网络
        └──► 金融数学 (Black-Scholes, Monte Carlo 定价)
```

- **前置**：[Oxford C8.1 SDE](../../oxford-math-courses/partC_c8_1_sde/)（Itô 微积分）
- **本课**：SDE 的数值离散化 + 收敛分析
- **后续**：扩散模型工程、MLMC 加速、反向 SDE

---

## 🔬 理论联系实际（ML/工程应用，公式级）

### 1. DDPM = Euler-Maruyama 解反向 SDE（[2006.11239](https://arxiv.org/abs/2006.11239) ✅）
$$x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{1-\alpha_t}{\sqrt{1-\bar\alpha_t}}\epsilon_\theta(x_t,t)\right) + \sigma_t z$$

### 2. Score-Based 生成 = 反向 SDE（[2011.13456](https://arxiv.org/abs/2011.13456) ✅）
$$d\bar{X} = \left[-f(\bar{X},t) + g(t)^2\nabla\log p_t(\bar{X})\right]dt + g(t)d\bar{W}$$

### 3. Langevin 采样 → 能量模型 / SGLD
$$dX = -\nabla U(X)dt + \sqrt{2}dW \;\Rightarrow\; p_\infty \propto e^{-U}$$

### 4. Black-Scholes 期权定价
$$dS = \mu S\,dt + \sigma S\,dW \;\Rightarrow\; \text{Price} = e^{-rT}\mathbb{E}[\max(S_T-K,0)]$$

### 5. 多级蒙特卡洛 (MLMC) 加速 — Giles 2008
复杂度 $O(\epsilon^{-3})$ → $O(\epsilon^{-2})$。

---

## 🆕 2024-2026 最新研究

| 子主题 | 最新进展 | 参考 |
|---|---|---|
| **一致性模型** | 一步生成绕过反向 SDE；LCM、sCM 等变体质量接近 Diffusion | [2303.01469](https://arxiv.org/abs/2303.01469) ✅ |
| **Flow Matching** | 用 ODE（非 SDE）做生成，训练更稳定 | [2210.02747](https://arxiv.org/abs/2210.02747) ✅ |
| **Rectified Flow** | 直线化扩散轨迹，少步采样 | 2023-2025 |
| **SDE 加速** | DPM-Solver（高阶 ODE 求解器）、一致性轨迹模型 | 2022-2024 |
| **Langevin 收敛理论** | 非凸 Langevin 的 mixing 时间与维度/条件数关系 | 2019-2024 ⚠️ |
| **MLMC for ML** | 扩散模型不确定性量化、变分推断加速 | 前沿 ⚠️ |

> ⚠️ 标记项的具体编号建议核实最新文献。
