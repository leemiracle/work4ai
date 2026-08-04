# 01 · Scaling Law 严格证明——从 Kaplan 到 Chinchilla 到 Besiroglu

> **博士级目标**：基础层 [02-ScalingLaw](../02-ScalingLaw.md) 给你"loss ~ 参数量幂律"的现象 + Chinchilla 最优配比。本篇**严格化**：
> - 推导 Kaplan 2020 与 Hoffmann 2022 的损失函数假设
> - 证明 Chinchilla 最优配比 $D^* \approx 20N$ 的数学来源
> - 复盘 Besiroglu 2024 的复现争议——为什么这是一个**科学诚信**的故事
>
> 预备：基础层 [02 ScalingLaw](../02-ScalingLaw.md) + 信息论地基（KL/Jensen）+ 微积分（拉格朗日乘子）。

---

## 一、问题的精确陈述

### 1.1 Scaling Law 想预测什么

**给定**：
- 算力预算 $C$（FLOPs）
- 参数量 $N$
- 数据量 $D$（tokens）

**问**：测试 loss $L(N, D, C)$ 怎么随它们变化？特别地——

**核心问题**：固定 $C$，怎么分配 $N$ 和 $D$ 让 $L$ 最小？

$$\min_{N, D} L(N, D) \quad \text{s.t.} \quad C(N, D) = \text{const}$$

### 1.2 FLOPs 怎么算

对 decoder-only Transformer，前向 + 反向的 FLOPs（Kaplan 2020 附录推导）：

$$C \approx 6 N D$$

**直觉**：
- 每个参数参与前向一次（$2ND$）+ 反向一次（$4ND$，梯度比前向多）
- 总 $6ND$

**所以约束**：$C = 6ND$，即 $D = C / (6N)$。

> 🎯 **关键**：固定算力 $C$，参数 $N$ 大 → 数据 $D$ 小；反之。**这是 Chinchilla 优化的核心 trade-off**。

---

## 二、Kaplan 2020 的 Scaling Law

### 2.1 损失函数假设

Kaplan et al. (2020) 提出（基于实证拟合）：

$$L(N, D, C) = \min\left(\frac{A}{N^\alpha} + \frac{B}{D^\beta} + L_\infty, \, L_\infty\right)$$

其中：
- $A, B$ 是常数
- $\alpha, \beta$ 是幂律指数
- $L_\infty$ 是不可约损失（自然语言的 entropy 下界）

**直觉**：
- $A/N^\alpha$：参数不足导致的 loss（"模型容量"项）
- $B/D^\beta$：数据不足导致的 loss（"数据"项）
- $L_\infty$：理想 loss 下界

### 2.2 Kaplan 的拟合结果

Kaplan 在大量模型（小到 1k 参数，大到 1.5B）上拟合得到：

$$\alpha = 0.076, \quad \beta = 0.095 \quad (\text{近似相等})$$

**含义**：参数和数据的"边际收益"几乎相同。

### 2.3 Kaplan 的最优配比（关键结论）

把 $D = C/(6N)$ 代入 $L$，对 $N$ 求导令其为 0，得到最优 $N^*$。

**Kaplan 的推导给出**（关键结论）：

$$N^* \propto C^{0.73}, \quad D^* \propto C^{0.27}$$

**含义**：算力增长时，**应该主要堆参数，少堆数据**。

**实践影响**：GPT-3（175B 参数，300B tokens）按这个法则设计——**参数远多于数据**。

> ⚠️ **这个结论后来被 Chinchilla 推翻**。但 Kaplan 论文的**形式**是对的——错的是拟合的数据范围（详见第三节）。

---

## 三、Chinchilla 2022 的修正

### 3.1 Hoffmann et al. 的关键洞察

Chinchilla 团队（DeepMind）发现 Kaplan 的拟合有两个问题：

1. **学习率 schedule 不对**：Kaplan 用"固定学习率"，但真实训练用 cosine decay。**这导致小模型 loss 偏高**——让数据看起来比实际重要。
2. **数据范围窄**：Kaplan 主要在 < 10B tokens 拟合，外推到 100B+ 不可靠。

**Chinchilla 的修正**：
- 重新设计实验：固定 $C$，扫描 $N$ 和 $D$ 的组合
- 用更合理的 LR schedule
- 在 4 个算力档（$10^{18}$ 到 $10^{21}$ FLOPs）拟合

### 3.2 Chinchilla 的损失函数假设

Hoffmann 2022 用**与 Kaplan 相同的函数形式**：

$$L(N, D) = E + \frac{A}{N^\alpha} + \frac{B}{D^\beta}$$

（$E$ 即 $L_\infty$）

但拟合参数**不同**：

$$\alpha = 0.34, \quad \beta = 0.28$$

（注：Hoffmann 的实际参数见论文 Table 3，简化后接近这值）

### 3.3 推导最优配比

**目标**：固定 $C = 6ND$，最小化 $L$。

**用拉格朗日乘子法**（博士级数学工具）：

$$\mathcal{L} = E + \frac{A}{N^\alpha} + \frac{B}{D^\beta} + \lambda(6ND - C)$$

对 $N$ 求偏导令其为 0：

$$\frac{\partial \mathcal{L}}{\partial N} = -\frac{\alpha A}{N^{\alpha+1}} + 6\lambda D = 0$$

对 $D$ 求偏导令其为 0：

$$\frac{\partial \mathcal{L}}{\partial D} = -\frac{\beta B}{D^{\beta+1}} + 6\lambda N = 0$$

两式相除消去 $\lambda$：

$$\frac{\alpha A / N^{\alpha+1}}{\beta B / D^{\beta+1}} = \frac{D}{N}$$

整理：

$$\frac{D}{N} = \frac{\alpha A \cdot D^{\beta+1}}{\beta B \cdot N^{\alpha+1}}$$

进一步化简（用 $D = C/(6N)$ 代入），得到关系：

$$\frac{D^*}{N^*} \approx \text{const}$$

**具体数值**（代入 $\alpha \approx \beta$）：

$$D^* \approx 20 N^*$$

> 🎯 **Chinchilla 法则**：**每个参数应该被 ~20 个 token 训练**。这是博士级推导的终点。

### 3.4 与 Kaplan 的对比

| | Kaplan 2020 | **Chinchilla 2022** |
|---|---|---|
| $N^* \propto C^x$ | $C^{0.73}$ | $C^{0.50}$ |
| $D^* \propto C^x$ | $C^{0.27}$ | $C^{0.50}$ |
| **核心差异** | 参数多，数据少 | **参数-数据同步** |

**实证验证**：Chinchilla 70B（训 1.4T tokens）**超过** GPT-3 175B（训 300B tokens）。**GPT-3 严重欠训**。

---

## 四、Besiroglu 2024 的复现争议

### 4.1 Besiroglu 团队的发现

Besiroglu, Erdil, Barnett, You (2024) 试图**复现 Hoffmann 2022 的第三种估计方法**（Hoffmann 用了三种，第三种最关键）。

**他们的发现**（arXiv:2404.10102）：
1. Hoffmann 报告的**置信区间异常窄**——窄到要求 ~600,000 次实验才能得到
2. 但 Hoffmann 实际只跑了 < 500 次实验
3. 用 Hoffmann 自己的方法重新拟合，得到的**结果与他们的窄置信区间不一致**
4. 但**与 Hoffmann 的第一、二种估计方法一致**

**核心矛盾**：Hoffmann 的第三种方法（最被引用的）的统计严谨性有问题。

### 4.2 这意味着什么

**好消息**：核心结论 $D^* \approx 20N$ **依然成立**——其他两种方法支持它。

**坏消息**：我们对"Chinchilla 法则的精确数值"的**置信度**应该更低。可能 $D^*/N^*$ 的真实最优在 10-30 之间，而非精确 20。

### 4.3 为什么这是博士级典范

这个案例展示了 ML 研究的**科学诚信**：

1. **复现是科学的核心**——但 ML 圈长期不重视
2. **重要论文也可能有错**——哪怕来自 DeepMind
3. **修正不会推翻结论，但调整我们对结论的信心**
4. **作者团队（Besiroglu）就是圈内人**——自我纠错是健康的

> 🎯 **博士级训练**：读 Besiroglu 论文时，**注意他们怎么措辞**——他们不说"Hoffmann 错了"，说"我们重新推导得到与第一二种方法一致的结果"。**学术礼貌 + 严谨**是必修课。

---

## 五、当前前沿（2024-2026）

### 5.1 Scaling Law 的扩展方向

| 方向 | 关键问题 | 代表论文 |
|---|---|---|
| **推理时 scaling** | 推理 compute 也有 scaling law？ | OpenAI o1 / DeepSeek R1 |
| **MoE scaling** | MoE 的 effective parameters 怎么算？ | DeepSeek-V3, Mixtral |
| **多模态 scaling** | 不同模态的最优配比不同？ | Chameleon, Gemini |
| **数据质量 scaling** | 不是 token 数，是信息量？ | Phi 系列, DataComp |
| **Repeat data** | 数据重复多次的边际收益？ | Mueller et al. 2024 |

### 5.2 一个开放问题（博士级）

**问题**：为什么 $\alpha \approx \beta \approx 0.3$？这背后有更深的理论吗？

**当前假说**：
- **统计学习理论**视角：和 sample complexity 相关（但深度网络违反经典理论）
- **信息论**视角：loss 和数据信息熵的关系
- **临界现象**视角：类似统计物理的临界点（争议大）

> ⚠️ 这是 ML 理论的**真正开放问题**——没有任何论文给出令人信服的解释。博士论文级方向。

---

## 六、博士级练习题

### 6.1 推导题

**Q1**：从 Kaplan 形式 $L = E + A/N^\alpha + B/D^\beta$，用拉格朗日乘子推导 $D^*/N^*$ 的一般表达式。当 $\alpha = \beta$ 时简化为多少？

**Q2**：如果引入"数据质量"因子 $q$（即 $D \to qD$），最优配比怎么变？

### 6.2 实验题

**Q3**：写一段 Python 代码，给定 $\alpha, \beta$，扫描 $C \in [10^{18}, 10^{22}]$，画出 $N^*(C)$ 和 $D^*(C)$ 的曲线。Kaplan 和 Chinchilla 的曲线长什么样？

**Q4**：复现 Besiroglu 的核心发现——给定一个 (loss, N, D) 数据集，用最小二乘拟合 $\alpha, \beta$，看置信区间怎么随样本数变化。

### 6.3 批判题

**Q5**：Kaplan 2020 被引用几千次，为什么 2 年才被 Chinchilla 修正？这反映 ML 研究的什么问题？

**Q6**：Chinchilla 法则 $D^* \approx 20N$ 在 MoE 模型上成立吗？（提示：MoE 的"有效参数"怎么定义？）

**Q7**：如果出现新模态（视频、3D），scaling law 还成立吗？参数和数据的最优配比会变吗？

### 6.4 思考题（开放）

**Q8**：为什么 $\alpha \approx \beta \approx 0.3$？背后的物理/统计机制是什么？

**Q9**：如果数据墙先到（互联网公开数据用完），scaling law 会怎么"破"？

**Q10**：递归自我改进（[`07-AI for AI`](../../讲透AI应用全景/07-AI%20for%20AI.md)）下，scaling law 怎么重新定义？

---

## 七、关键引用（BibTeX）

```bibtex
@article{kaplan2020scaling,
  title={Scaling Laws for Neural Language Models},
  author={Kaplan, Jared and others},
  journal={arXiv:2001.08361},
  year={2020}
}

@article{hoffmann2022training,
  title={Training Compute-Optimal Large Language Models},
  author={Hoffmann, Jordan and others},
  journal={arXiv:2203.15556 (Chinchilla)},
  year={2022}
}

@article{besiroglu2024chinchilla,
  title={Chinchilla Scaling: A replication attempt},
  author={Besiroglu, Tamay and Erdil, Ege and Barnett, Matthew and You, Josh},
  journal={arXiv:2404.10102},
  year={2024}
}
```

---

## 八、一句话总结

> 🎯 **博士级五句话**：
> 1. Scaling Law 形式 $L = E + A/N^\alpha + B/D^\beta$，参数-数据-算力的损失分解。
> 2. Kaplan 2020 拟合给出 $N^* \propto C^{0.73}$——参数主导，但**学习率 schedule 不当 + 数据范围窄**。
> 3. Chinchilla 2022 修正为 $N^* \propto C^{0.50}$、$D^*/N^* \approx 20$——**参数-数据同步**（拉格朗日乘子推导）。
> 4. Besiroglu 2024 复现发现 Hoffmann 第三方法的置信区间不可信——但**核心结论 $D^* \approx 20N$ 仍成立**。
> 5. **博士级核心**：scaling law 是 ML 最接近"硬科学"的理论，但 $\alpha \approx \beta \approx 0.3$ **至今没有解释**——这是开放前沿。

---

📌 **下一步**

1. **做练习 Q1-Q4**：拉格朗日推导 + 拟合实验（建议本机跑，CPU 即可）。
2. **深读三篇原文**：Kaplan / Chinchilla / Besiroglu，按 [00 论文清单](./00-论文阅读清单.md) 的 L3 标准。
3. **进入 [02 涌现的争论](./02-涌现的争论.md)**：scaling 的另一面——能力是渐变还是突变。
4. **思考 Q8-Q10**：每个都是博士论文级方向。
