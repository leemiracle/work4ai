# Oxford Part C C8.1 — Stochastic Differential Equations

> **学校**：Oxford | **学院**：Mathematical Institute
> **一手来源**：[courses.maths.ox.ac.uk](https://courses.maths.ox.ac.uk/)

## 课程信息
- **编号**：C8.1
- **学期**：Part C (研究生级)
- **教材**：Karatzas & Shreve, *Brownian Motion and Stochastic Calculus*；Øksendal, *Stochastic Differential Equations*
- **特色**：**Oxford SDE 金课**

## 教学大纲
1. **Brownian motion** 严格定义
2. Markov property
3. **Itô 积分** ★
4. **Itô 公式**（change of variables）
5. **Stochastic differential equations (SDEs)**
6. **Feynman-Kac 公式**
7. **Girsanov 定理**
8. **Applications to finance**（Black-Scholes）
9. **Backward SDE** 入门

## 与 ML 的关联（**扩散模型核心数学**）
- **Itô 积分**：DDPM / Score-Based Models 的数学基础
- **Feynman-Kac**：神经网络与 PDE 的联系
- **学完后**：能从 SDE 视角推导扩散模型

## 参考资源
- Karatzas & Shreve, *Brownian Motion and Stochastic Calculus* (Springer)
- Øksendal, *Stochastic Differential Equations* (Springer)
- UT Austin 对照：M 387D Stochastic Calculus（待写/未落盘）

---

## 📍 在数学全景中的位置

```
概率论 (随机过程)           ODE (确定性微分方程)
        │                          │
        └──────────┬───────────────┘
                   ▼
            本课: 随机微分方程 (SDE)
         ┌──────────┴──────────────────┐
         ▼                             ▼
   Itô 微积分                    Fokker-Planck 方程
   (随机积分/Itô 引理)          (密度的 PDE)
         │                             │
         ▼                             ▼
   反向 SDE ★                   Langevin 采样
   (扩散模型核心)                (MCMC / SGLD)
```

- **前置**：概率论 + [Princeton MAT 322 PDE](../../princeton-math-courses/mat322_pde/)
- **本课**：布朗运动 → Itô 积分 → Itô 引理 → SDE → Fokker-Planck → Girsanov → 反向 SDE
- **后续/交叉**：[ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（数值实现 + 扩散模型实验）

---

## 🔬 理论联系实际（ML/工程应用，公式级）

### 1. 扩散模型 = 反向 SDE ★
前向 $dx = f\,dt + g\,dW$；反向 $d\tilde{x} = [f - g^2\nabla\log p_t]\,dt + g\,d\tilde{W}$。详见 [notes.md](notes.md) §1.7。Song et al. [2011.13456](https://arxiv.org/abs/2011.13456) ✅。

### 2. Langevin MCMC = SDE 采样
$$dX = -\nabla U(X)\,dt + \sqrt{2}\,dW \implies \pi \propto e^{-U}$$
SGLD [Welling-Teh 2011, 1103.4140](https://arxiv.org/abs/1103.4140) ✅ 用随机梯度做大规模贝叶斯。

### 3. SGD = 带噪梯度流
$$d\theta = -\nabla L(\theta)\,dt + \sigma(\theta)\,dW$$
SDE 理论分析 SGD 收敛与泛化。

### 4. Itô 引理的"修正项" → Black-Scholes
$$df = \left(f_t + \mu f_x + \frac{\sigma^2}{2}f_{xx}\right)dt + \sigma f_x\,dW$$
多出的 $\frac{\sigma^2}{2}f_{xx}$ 是随机分析与确定性微积分的根本区别。

### 5. Girsanov 定理 → 变分推断
Radon-Nikodym 导数给出 ELBO 的精确表达式。

---

## 🆕 2024-2026 最新研究

| 子主题 | 最新进展 | 参考 |
|---|---|---|
| **Flow Matching** | 用确定性 ODE 替代 SDE 做生成，训练更稳定 | [Lipman ICLR 2023, 2210.02747](https://arxiv.org/abs/2210.02747) ✅ |
| **一致性模型** | 单步生成（无需反向 SDE 迭代） | [Song et al. 2023, 2303.01469](https://arxiv.org/abs/2303.01469) ✅ |
| **SDE 理论分析 SGD** | 用 SDE 分析 SGD 隐式正则化（偏向平坦极小值） | ⚠️ 2024 进展 |
| **随机微积分 + RL** | 受控 SDE = 连续 POMDP 的核心模型 | ⚠️ |
| **分数匹配收敛性** | 扩散模型分数匹配的收敛速率理论 | ⚠️ 2024 |

> ⚠️ 标记项建议核实最新版本。

---

📌 **下一步**：→ [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（数值实现）或 [Cambridge Part II ML](../../cambridge-math-courses/partII_mathematics_machine_learning/)
