# Princeton MAT 322 — Introduction to Partial Differential Equations

> **学校**：Princeton | **学期**：Spring | **学分**：QCR
> **一手来源**：[math.princeton.edu/undergraduate](https://www.math.princeton.edu/undergraduate)

## 课程信息
- **编号**：MAT 322 / 335（不同变体）
- **先修**：MAT 201 (multivariable calculus) 或 MAT 215/216
- **教材**：Strauss, *Partial Differential Equations: An Introduction*；Evans (深入)
- **特色**：PDE 入门

## 教学大纲
1. **Three canonical PDE**：Heat / Wave / Laplace
2. **Boundary value problems**
3. **Fourier series**
4. **Separation of variables**
5. **Sturm-Liouville theory**
6. **Green's functions**
7. **Method of characteristics**（一阶 PDE）
8. **Maximum principle**

## 与 ML 的关联
- **Heat equation**：扩散模型的理论原型
- **Wave equation**：神经波（少见但用于物理 AI）
- **Laplace / Poisson**：图半监督学习
- **学完本课后**：能从 PDE 视角理解 score-based generative models

## 参考资源
- **教材**：Strauss, *Partial Differential Equations* (Wiley)
- **进阶教材**：Evans, *Partial Differential Equations* (Springer, 2010)
- **UT Austin 对照**：[MATH-GA 2451 PDE](../../ut-austin-math-courses/)（应用版）

## 学习建议
- **节奏**：每周 4-5 小时，12 周

📌 **下一步**：→ [MAT 345 Algebra I](../mat345_algebra_I/)

---

## 📍 在数学全景中的位置

```
多元微积分 (偏导, 梯度, 散度)      ODE (常微分方程)
        │                                │
        └──────────┬─────────────────────┘
                   ▼
            本课: 偏微分方程 (PDE)
     ┌─────────────┼──────────────┐
     ▼             ▼              ▼
  热方程          波方程        Laplace 方程
  (扩散)         (传播)         (平衡态)
     │             │              │
     ▼             ▼              ▼
 扩散模型 ★    物理 AI       图半监督学习
 (DDPM)       (Neural ODE)   (标签传播)
     │
     ▼
 随机 PDE / SDE → Langevin 采样
```

- **前置**：多元微积分 + [MIT 18.03 ODE](../../mit-math-courses/18_03_differential_equations/)
- **本课**：热/波/Laplace 三大 PDE + 分离变量 + Fourier 级数 + 最大值原理
- **后续/交叉**：[ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（随机 PDE → 扩散模型）

---

## 🔬 理论联系实际（ML/工程应用，公式级）

### 1. 扩散模型 = 随机热方程 ★
DDPM 前向过程 $dx = -\frac{\beta(t)}{2}x\,dt + \sqrt{\beta(t)}\,dW$ 是热方程的随机版本。反向过程 = 逆向热流。详见 [notes.md](notes.md) §3.1。

### 2. 分数匹配 = Fokker-Planck 漂移
$$\nabla_x \log p_t(x) = \text{Fokker-Planck 方程的核心量}$$
Score-based 生成模型 = 学热方程的"逆向温度梯度"。

### 3. 图拉普拉斯 → 半监督学习
图上 $L = D - A$ 是连续 $\Delta$ 的离散化。标签传播 $\frac{dF}{dt} = -LF$。

### 4. 热核 = 高斯卷积
$$u(x,t) = (G_t * u_0)(x), \quad G_t = \frac{e^{-|x|^2/4t}}{(4\pi t)^{n/2}}$$
热方程的解 = 高斯模糊。时间越大越模糊（方差 $\propto t$）。

### 5. PINN（物理约束神经网络）
$$\mathcal{L} = \|u_\theta - u_{\text{data}}\|^2 + \lambda\|u_t - \Delta u_\theta\|^2$$

---

## 🆕 2024-2026 最新研究

| 子主题 | 最新进展 | 参考 |
|---|---|---|
| **Flow Matching** | 用 ODE（而非 SDE）做生成，更高效 | [Lipman et al. ICLR 2023, 2210.02747](https://arxiv.org/abs/2210.02747) ✅ |
| **分数扩散模型** | 统一 DDPM/Score Matching 理论 | Song et al. [2011.13456](https://arxiv.org/abs/2011.13456) ✅ |
| **PINN 收敛性** | 理论分析 PINN 对高维 PDE 的收敛速率 | ⚠️ 2024 进展 |
| **神经算子** | Fourier Neural Operator = 频域学 PDE 解算子 | [Li et al. 2021, 2010.08895](https://arxiv.org/abs/2010.08895) ✅ |
| **高维扩散** | 扩散模型在 >1000 维中的 PDE 分析 | ⚠️ 理论仍在发展 |

> ⚠️ 标记项建议核实最新 arXiv 版本。

---

📌 **下一步**：→ [MAT 345 Algebra I](../mat345_algebra_I/) 或 [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)
