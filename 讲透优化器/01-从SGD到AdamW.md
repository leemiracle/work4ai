# 01 — 从 SGD 到 AdamW：动量与自适应学习率

> 「讲透优化器」核心章。00 讲了"为什么优化器决定训练成败"。本篇讲优化器的演化主线——**SGD → Momentum → RMSProp → Adam → AdamW**。每一步都解决了前一个的问题。

---

## 1. 灵魂：优化器 = 更新规则

$$
\boxed{\theta_{t+1} = \theta_t - \eta \cdot \underbrace{d_t}_{\text{更新方向}}}
$$

所有优化器的差别在 $d_t$ 怎么算——梯度直接用（SGD）、加动量、按参数自适应。

---

## 2. SGD（起点）

$$
d_t = g_t = \nabla_\theta \mathcal{L}(\theta_t)
$$

- 简单，但**震荡**（在 ravine 地形来回弹）
- 对学习率敏感（太大发散，太小慢）

---

## 3. Momentum（动量）

$$
v_t = \beta v_{t-1} + g_t, \quad d_t = v_t
$$

- 累积历史梯度 → **抑制震荡**（ravine 的横向来回抵消，纵向加速）
- $\beta \approx 0.9$：保留最近 ~10 步梯度的惯性

**直觉**：像重球滚下山——有惯性，不会被小坑拦住。

---

## 4. RMSProp（自适应学习率）

$$
s_t = \beta s_{t-1} + (1-\beta) g_t^2, \quad d_t = \frac{g_t}{\sqrt{s_t} + \epsilon}
$$

- 梯度大的参数 → 学习率自动**减小**（防爆）
- 梯度小的参数 → 学习率自动**增大**（加速）
- **每个参数有自己的有效学习率**

---

## 5. Adam = Momentum + RMSProp

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t \quad \text{(动量)}
$$
$$
v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \quad \text{(自适应)}
$$
$$
d_t = \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
$$

（$\hat{m}, \hat{v}$ 是偏差修正）

- **默认选择**：$\beta_1 = 0.9, \beta_2 = 0.999, \eta = 10^{-3}$
- 90% 的深度学习用 Adam

---

## 6. AdamW：修复 weight decay

### 6.1 Adam 的问题

L2 正则（weight decay）在 Adam 里和自适应耦合——**效果不对**。

### 6.2 AdamW 的解耦

把 weight decay **从梯度里拿出来**，直接作用在参数上：

$$
\theta_{t+1} = \theta_t - \eta \cdot d_t - \eta \cdot \lambda \theta_t
$$

- $\lambda \theta_t$：直接的权重衰减（不经过自适应）
- **这是大模型训练的标配**（GPT/Llama 都用 AdamW）

---

## 7. Lion 与未来

Lion（Google 2023，LLM 发现的优化器）：用 sign 函数替代自适应——更省内存（不存 $v_t$）。但仍是 Adam 系的变体。

**新趋势**：FP8 训练 + Sophia（二阶近似）+ Lion——但 AdamW 仍是主流。

---

## 8. 批判性

- **Adam 不是万能**：某些任务（CNN 图像）SGD+momentum 泛化更好（讲透泛化 02 章）
- **学习率仍是关键**：Adam 自动调"相对"学习率，但 $\eta$ 的绝对值仍要调（warmup/cosine schedule）
- **优化器研究的边际收益递减**：AdamW 够好，新优化器的提升常 < 5%

> **诚实结论**：AdamW 是当前最优工程选择。理解 SGD→Adam 的演化比追新优化器更重要——这培养了"优化器在做什么"的直觉。

---

## 📌 下一步

[02-学习率调度](02-学习率调度.md)（待补）——warmup + cosine 的原理。

## ✍️ 练习

1. Momentum 的 $\beta=0.9$ 意味着什么？（提示：保留 ~10 步梯度的指数加权。）
2. Adam 同时用动量和自适应。为什么不冲突？（提示：动量在分子，自适应在分母，正交。）
3. AdamW 把 weight decay 解耦。L2 正则（在 loss 里）和直接 weight decay 有什么区别？（提示：L2 经过自适应被缩放，直接 decay 不被缩放。）
