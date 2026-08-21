# 13 — Predictive Coding：大脑的"预测-误差"与 AI 的回响

> 12 讲 SNN（脉冲）。本篇讲 **Predictive Coding**——大脑处理信息的理论模型：大脑不"被动接收"，而是**主动预测 + 只处理预测误差**。这和自回归 LLM / diffusion / RLHF 都有惊人同构。

---

## 1. 灵魂：大脑只看"意外"

$$
\boxed{\text{Predictive Coding} : \text{高层预测低层输入，只传 } \underbrace{\text{误差}}_{\text{预测 - 实际}} \text{ 给高层}}
$$

- 传统信息处理：每层都传全部信息
- **Predictive Coding**：每层只传**预测误差**（新信息）——大部分被"预测对了"的信息丢弃

> 🎯 **直觉**：你不会注意每秒眨眼（大脑预测对了，不传）；但你会注意突然的声响（预测错了，传误差）。

---

## 2. 数学：Rao & Ballard 1999

经典 predictive coding 模型：

$$
\text{误差} = x - \hat{x}, \quad \hat{x} = f(\text{高层表征})
$$

- $x$：低层输入（如像素）
- $\hat{x}$：高层对低层的预测
- 只传误差 $x - \hat{x}$ 上行

**训练目标**：最小化总误差 + 表征稀疏性。

---

## 3. 和 AI 的三重同构

### 3.1 自回归 LLM = 预测下一个词

LLM 的训练目标 $P(x_t | x_{<t})$ 就是**预测**。生成时，"惊讶"（低概率）的 token 是信息量大的——这和 predictive coding 的"只传误差"对应。

**注意力机制**某种程度就是"动态预测误差"：高 attention 权重 = 预测需要更新的地方。

### 3.2 Diffusion = 预测并消除噪声

Diffusion 训练 $\epsilon_\theta(x_t)$ 预测噪声——**预测"哪里偏离了数据"**，然后消除。

**这就是 predictive coding**：模型预测"输入里哪里是噪声（误差）"，然后去掉。

### 3.3 RLHF = 预测人类偏好

RLHF 的 reward model 预测"人类会给多少分"——预测错了（高分但人类不喜欢）就是**误差**，PPO 据此修正。

---

## 4. 为什么这个视角有用

### 4.1 解释 LayerNorm 的作用

Predictive Coding 理论里，每层要做**除法归一化**（误差/方差）——这和 LayerNorm 的操作一致。这解释了为什么 Transformer 需要 LayerNorm（不只是数值稳定，是 predictive coding 的一部分）。

### 4.2 指导稀疏激活

"只传误差"意味着大部分神经元应该静默——这和 MoE（专家稀疏激活）/ ReLU（负数归零）的**稀疏性**对应。

### 4.3 连续学习（Continual Learning）

大脑能持续学新东西不忘旧——因为只传"新误差"，旧预测不动。这启发了** continual learning 的"冻结+扩展"**策略（讲透复用权重 06 章）。

---

## 5. 批判性

- **Predictive Coding 是"理论框架"，不是"算法"**：它解释了很多现象，但不能直接训模型
- **大脑是否真的"只传误差"仍有争议**：神经科学证据部分支持部分反对
- **AI 的"相似"可能是表面类比**：LLM 的预测 next token 和大脑的预测机制不一定同构

> **诚实结论**：Predictive Coding 是**有用的元理论**——它给 AI 提供了"为什么这样设计"的生物学解释（LayerNorm/稀疏/自回归）。但它不能直接产生新算法，价值在启发思考。

---

## 📌 下一步

[14-Equivariant与GNN](14-Equivariant与GNN.md)——物理/科学启发的架构：等变神经网络（旋转/平移不变）。

## ✍️ 练习

1. LLM 预测 next token，大脑预测下一层输入。两者都是"预测"——但 LLM 的预测用于生成，大脑的预测用于什么？（提示：压缩信息/只传新东西。）
2. Diffusion 预测噪声 = predictive coding 预测误差。如果 diffusion 训得好（误差小），生成质量会怎样？（提示：误差小→预测准→生成接近数据。）
3. 如果 Transformer 把"只传误差"做到极致（高置信度 token 不传），会变成什么？（提示：稀疏 attention 的理论依据之一。）
