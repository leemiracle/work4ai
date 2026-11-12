# 15 — Memory Networks 与 NTM：外部记忆的艺术

> 14 讲等变（物理启发）。本篇讲**记忆增强**——给神经网络一个**外部记忆库**，让它能"查表"而非"塞权重"。Memory Networks（2014）/ Neural Turing Machine（2014）是先驱，RAG 是它们的工程化。

---

## 1. 灵魂：权重 ≠ 记忆

$$
\boxed{\text{外部记忆} = \text{一个可读写的矩阵，独立于网络权重}}
$$

- 普通 NN：所有知识压缩进**权重**（慢更新、容量受限）
- **记忆增强 NN**：加一个外部矩阵 $M$，可"软寻址"读/写——快、大容量

> 🎯 **直觉**：权重是"长期记忆"（技能），外部记忆是"工作记忆"（当前任务的笔记）。

---

## 2. Memory Networks（2014，Weston）

最早的外部记忆网络：

$$
o = \sum_i \alpha_i M_i, \quad \alpha_i = \text{softmax}(\text{sim}(q, M_i))
$$

- $M$：$N \times d$ 记忆矩阵（存 $N$ 个向量）
- $q$：查询
- $\alpha$：软注意力权重（读哪些记忆）
- 输出 $o$：加权读出的记忆

**这和 attention 几乎一样**——Memory Networks 是 attention 之前就有的"软记忆检索"。

---

## 3. Neural Turing Machine（2014，Graves）

NTM 更进一步：**可读可写**。

### 3.1 读头 + 写头

- **读**：$\text{read} = \sum_i w_i^r M_i$（软寻址）
- **写**：$M_i \leftarrow M_i + w_i^w \cdot v$（软更新）

权重 $w$ 由 controller（LSTM/MLP）根据输入生成——**学习寻址**。

### 3.2 可微计算机

NTM 本质是**可微的图灵机**——controller 是 CPU，$M$ 是 RAM，attention 是"读磁头"。理论上能学习算法（排序/复制/关联记忆）。

### 3.3 DNC（Differentiable Neural Computer，2016）

NTM 的升级版——更稳定的记忆管理（动态分配/释放）。

---

## 4. 现代：Memorizing Transformer / RAG

### 4.1 Memorizing Transformer（Wu 2022）

给 Transformer 加一个**外部 K-V 库**（非滑动窗口的历史 key-value）。

- 近期 token：标准 attention
- 远期 token：查外部 K-V 库
- 效果：长上下文质量提升，无需无限扩大窗口

### 4.2 RAG = 工程化的 Memory Network

RAG 的检索-生成循环：

$$
\text{query} \to \underbrace{\text{检索外部 K-V}}_{\text{Memory Networks 的读}} \to \text{LLM 生成}$$

**RAG 本质是 Memory Networks 的工程实现**——外部记忆库（向量数据库）+ 软检索（embedding 相似度）。

---

## 5. 记忆增强 vs 纯权重

| 维度 | 纯权重（标准 NN）| 外部记忆（Memory/NTM/RAG）|
|---|---|---|
| 容量 | 受参数量限制 | 外部库可无限大 |
| 更新 | 训练（慢）| 实时读写（快）|
| 可解释 | 黑箱 | 可看"读了哪些记忆" |
| 复杂度 | 一次前向 | 加检索步骤 |

**洞察**：LLM 的"涌现"靠权重记忆；RAG/Agent 的"实时"靠外部记忆。两者互补。

---

## 6. 批判性

- **NTM 训练难**：可微计算机的梯度不稳，2016 后热度下降
- **RAG "退化"为工程**：学术界觉得 RAG 不如 NTM"优雅"，但工程上 RAG 赢了
- **长上下文 Transformer 弱化记忆需求**：128K 窗口的 Transformer 部分替代了外部记忆

> **诚实结论**：Memory Networks 是"超越权重"的思想先驱，但工程上 RAG（外部 K-V + 检索）才是赢家。NTM 的"可微计算机"是研究之美，落地困难。

---

## 📌 下一步

[16-未来展望](16-未来展望.md)——收尾篇：推理时计算 / 量子 ML / AGI 架构猜想。

## ✍️ 练习

1. RAG 是 Memory Networks 的工程化。它们最大的区别是什么？（提示：NTM 端到端训记忆，RAG 的检索器是预训练的向量模型。）
2. 如果 Transformer 的上下文能到无限长，还需要 RAG 吗？（提示：需要——成本/实时更新/可解释性。）
