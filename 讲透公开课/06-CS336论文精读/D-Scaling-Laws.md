# D · Scaling Laws 与训练理论（9 篇）

> **CS336 的理论核心**——回答"该花多少算力训多大的模型喂多少数据"。
> 对应讲座：**L9、L11（scaling laws）**｜ 作业：**A3（拟合 scaling law）**

---

## D1. Kaplan et al. – Scaling Laws for Neural Language Models (2020) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2001.08361](https://arxiv.org/pdf/2001.08361.pdf) · OpenAI

**核心问题**：模型大小 $N$（参数）、数据 $D$（tokens）、算力 $C$（FLOPs）和测试 loss 之间有什么定量关系？能否预测大模型的 loss？

**方法**：训练上百个不同规模的模型（从 1K 到 1.5B 参数），固定其他变量逐一扫描。发现 **loss 服从幂律**：

$$L(C) = \left(\frac{C_c}{C}\right)^{\alpha_C}, \quad L(N) = \left(\frac{N_c}{N}\right)^{\alpha_N}$$

经验值 $\alpha_C \approx 0.05$（极平缓！），$\alpha_N \approx 0.076$。

**关键结论（被后来推翻的部分）**：在固定算力 $C$ 下，最优分配是**主要增大模型，少喂数据**——大模型"省数据"。预测 GPT-3 (175B) 应只训 ~300B tokens（实际就是如此）。

**💡 工程经验**：
1. **幂律极其惊人**——跨越 6 个数量级仍是平滑的幂律，这在复杂系统里很少见，说明深度学习有某种深层结构。
2. Kaplan 的方法学教训：**没为每个模型大小调学习率**，导致小模型被低估、结论偏倚 → 直接被 Chinchilla 推翻。这是"实验设计不严谨会被打脸"的经典案例。
3. CS336 A3 让学生复现 scaling law 拟合——核心就是采集 $(N, D, L)$ 数据点，做对数-对数线性回归。
4. **loss 和下游任务不是线性关系**——loss 降 0.05 可能对应 MMLU 涨 10 分。后来 Overtrained Scaling Laws（D6）专门研究任务性能。

**📍 CS336 角色**：L9 核心。

---

## D2. McCandlish et al. – An Empirical Model of Large-Batch Training (2018) ⭐⭐

- **链接**：[arxiv.org/abs/1812.06162](https://arxiv.org/pdf/1812.06162.pdf) · OpenAI

**核心问题**：增大 batch size 能加速训练（更多并行），但到某个点后再增大就没用了。这个**临界点**在哪？

**方法**：提出 **critical batch size** $B_{\text{crit}}$——一个数据集/模型相关的阈值。batch < $B_{\text{crit}}$ 时，增大 batch 几乎线性加速且不损失质量；batch > $B_{\text{crit}}$ 时，**边际收益急剧递减**（简单梯度噪声估计饱和）。

**💡 工程经验**：
1. **大模型训练的 batch size 选择黄金法则**：先找 $B_{\text{crit}}$（用小规模扫描），然后训练用 $1\text{-}4 \times B_{\text{crit}}$。再大就是浪费显存。
2. $B_{\text{crit}}$ 与**梯度噪声尺度**（gradient noise scale）成正比——模型越大，临界 batch 越大（所以大模型可以用更大 batch）。
3. LLaMA-3 用 batch size 16M tokens，就是这个规律的工业实践。
4. 这也解释了**为什么小 batch 有时反而更好**（SGD 的正则化效果）——本质是噪声。

**📍 CS336 角色**：L9 / L2。

---

## D3. Bahdanau – The FLOPs Calculus of Language Model Training (2022) ⭐⭐⭐

- **链接**：[medium.com/@dzmitrybahdanau](https://medium.com/@dzmitrybahdanau/the-flops-calculus-of-language-model-training-3b19c1f025e4)

**核心**：一篇**博客**，但价值堪比论文——把训练 FLOPs 算得清清楚楚。

**关键公式**（decoder-only Transformer，前向）：
- 每个 token 的前向 FLOPs $\approx 6N$（$N$ = 非嵌入参数）。
- 反向约 2 倍前向，所以**训练一个 token 总计 $\approx 6N$ FLOPs**（前向 2N + 反向 4N 的简化记法，约定俗成）。
- 训练 $D$ 个 token 的总 FLOPs：$C \approx 6ND$。

**举例**：LLaMA-2 70B，$N=70\times10^9$，$D=2\times10^{12}$（2T tokens），$C = 6 \times 70\times10^9 \times 2\times10^{12} \approx 8.4 \times 10^{23}$ FLOPs。

**💡 工程经验**：
1. **这是 CS336 L2 的核心**——Percy 的"算力会计学"。每个工程决策都要算 FLOPs 预算。
2. **估算训练时间**：$T = C / (\text{GPU 数} \times \text{FLOPS/GPU} \times \text{MFU})$。H100 BF16 理论 989 TFLOPS，但 MFU 通常 40-55%，所以有效 ~400-540 TFLOPS。
3. **embedding 参数不计入 $N$**（计算时按词表频率摊薄）——这是常见陷阱。
4. $6N$ 的直觉：每个参数在前向参与 2 次乘加（一次 attention 一次 FFN），乘 2（forward+backward）。

**📍 CS336 角色**：**L2 的核心**，A2/A3 算力规划的基础。

---

## D4. Hoffmann et al. – Chinchilla (2022) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2203.15556](https://arxiv.org/pdf/2203.15556.pdf) · DeepMind

**核心问题**：Kaplan 说"大模型省数据"，但工业界发现训练不充分的 GPT-3 (175B) 被更小的、训得更充分的模型反超。到底该怎么分配？

**方法**：**三种独立估计交叉验证**（这是论文最严谨之处）：
1. **Approach 1（模型扫描）**：对每个模型大小，用 4 个学习率训练不同 token 数，取每个模型的**loss 下包络**。
2. **Approach 2（IsoFLOP）**：固定多个计算预算，在每个预算下找最优模型大小——直接读最佳 $(N, D)$。
3. **Approach 3（参数化拟合）**：拟合 $L(N,D) = E + A/N^\alpha + B/D^\beta$，得到 $\alpha \approx 0.34, \beta \approx 0.28$。

三种方法一致结论：**模型与数据应近似等比例增长**，最优 token 数 $D^* \approx 20 \times N$。

**关键结果**：Chinchilla 70B 用 1.4T tokens，**打平 Gopher 280B**——证明 GPT-3 严重训练不足。

**💡 工程经验**：
1. **"Chinchilla 最优"= 训练效率最优**，但**不等于部署最优**（见 D6）。这是初学者最常混淆的点。
2. $D^* \approx 20N$ 这个经验法则至今是预训练 token 数的起点（LLaMA-1 7B 训 1T，略多于 20×7B=140B 的最优，因为 Meta 权衡了推理成本）。
3. **Chinchilla 之后所有大模型都"训得更充分"**——LLaMA-2 (2T)、LLaMA-3 (15T)、Qwen (3T+) 远超 20N。这正是 Overtrained Scaling Laws（D6）的研究对象。
4. CS336 A3 让学生用 hosted API 重做这个实验——拟合自己的 $L(N,D)$。

**📍 CS336 角色**：**L9 + L11 的核心**，A3 的灵魂。

---

## D5. Yang et al. – Tensor Programs V / μP (2022) ⭐⭐

- **链接**：[arxiv.org/abs/2203.03466](https://arxiv.org/abs/2203.03466)

**核心问题**：大模型超参（学习率、初始化）怎么调？直接在大模型上 grid search 太贵。

**方法**：**μP（Maximal Update Parametrization）**——通过精心的参数化，让**小模型的最优超参可以直接迁移到大模型**。核心思想：保证各层**激活值的尺度**在宽度变化时不变。

**💡 工程经验**：
1. **调超参的范式转变**：以前是大模型上昂贵 grid search；μP 让你在小模型（比如 1B）上调，直接套用到 70B。
2. 实践中 μP 不完美（深度变化仍有问题），但思路被广泛采用。
3. 这也是 **scaling law 的理论根基**之一——为什么小模型实验能预测大模型？因为存在某种"参数化不变性"。

---

## D6. Besiroglu et al. – The Scaling Laws of Fine-Tuning / Overtrained (2024) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2403.08540](https://arxiv.org/pdf/2403.08540.pdf)

**核心问题**：Chinchilla 只优化**训练 loss**，忽略**推理成本**。但部署时小模型用得多——把 1.4B 模型训 900B tokens（远超 20×1.4B=28B 的 Chinchilla 最优），值得吗？

**方法**：固定训练 token/参数比（如 $D/N = 30, 60, 120, 240$），扫描，外推 300 倍计算。关注**下游任务性能**（不是预训练 loss）。

**关键结论**：**"过训练"小模型在部署上更划算**——一个训了 20 倍 Chinchilla 最优的 1.4B 模型，部署成本远低于同质量的大模型。这就是为什么 **LLaMA-3 8B 训 15T tokens**（$D/N \approx 1875$，是 Chinchilla 的 90 倍）。

**💡 工程经验**：
1. **训练-推理 trade-off**：如果模型要被亿级用户调用，推理成本主导，应该**过训练小模型**。如果是一次性研究，按 Chinchilla 最优。
2. 这篇把"scaling law 从 loss 导向转成部署成本导向"——是工业界训练决策的关键理论。
3. 解释了 LLaMA-3、Mistral、DeepSeek 为什么疯狂堆 tokens——**不是不懂 Chinchilla，是算过推理账**。

**📍 CS336 角色**：L11（scaling 续），现代训练决策的核心。

---

## D7. MiniCPM / WSD (2024) ⭐⭐

- **链接**：[arxiv.org/abs/2404.06395](https://arxiv.org/pdf/2404.06395.pdf) · 清华

**核心**：提出 **WSD（Warmup-Stable-Decay）学习率调度**：
- Warmup：学习率线性升
- **Stable**：保持恒定（不像 cosine 一直降）
- **Decay**：最后阶段快速降到 0

对比传统 **Cosine 调度**（D8）一直缓慢下降，WSD 的 stable 阶段训练效率更高，且 decay 阶段能"补救"质量。

**💡 工程经验**：
1. **Cosine 调度的痛点**：必须预知训练总步数。如果想中途加数据继续训，cosine 调度会失效（已降到底）。WSD 的 stable 阶段可以无限延长。
2. WSD 已被 MiniCPM、部分 OLMo 模型采用。2024-2025 的热门调度方案。

---

## D8. Loshchilov & Hutter – SGDR / Cosine Learning Rate (2017) ⭐

- **链接**：[arxiv.org/abs/1608.03983](https://arxiv.org/pdf/1608.03983.pdf)

**核心**：**余弦退火**——学习率按 $\eta_t = \eta_{min} + \frac{1}{2}(\eta_{max}-\eta_{min})(1+\cos(\pi t/T))$ 从最大降到最小。

**💡 工程经验**：
1. **大模型训练的事实标准调度**——LLaMA、GPT-3、PaLM 全用 cosine。
2. 配合 warmup（前 1-2% 步线性升温）。
3. 优点：平滑收敛；缺点：必须预定总步数（WSD 解决此问题）。

---

## D9. WRAP / Repetition Improves Training (2024) ⭐

- **链接**：[arxiv.org/abs/2401.16380](https://arxiv.org/abs/2401.16380)

**核心**：**数据重复（repeating tokens）可能有益**——传统认为"一遍数据最好"，但 WRAP 发现在某些数据稀缺场景，**重复训练 2-4 轮**反而提升（且不严重过拟合）。

**💡 工程经验**：挑战了"epoch=1 铁律"。但实践中**高质量数据重复** vs **低质量数据重复**差异巨大——重复前要确保数据质量。

---

## EleutherAI – Transformer Math 101 (2023, blog) ⭐⭐

- **链接**：[blog.eleuther.ai/transformer-math](https://blog.eleuther.ai/transformer-math/)

**核心**：把上述 FLOPs/参数/显存/算力的关系做成**工程师速查表**。包括：训练显存估算（$6N + \text{激活}$）、推理延迟估算、MFU 计算。**CS336 L2 的辅助读物**。

---

## D 类总结：Scaling Law 的三代演进

```
第1代 Kaplan (2020): "大模型省数据" → GPT-3 175B 只训 300B tokens
            ↓ 被推翻
第2代 Chinchilla (2022): "等比例，D≈20N" → 所有模型训得更充分
            ↓ 被修正
第3代 Overtrained (2024): "推理主导时过训练" → LLaMA-3 8B 训 15T

工程公式链:
  FLOPs ≈ 6ND (Bahdanau)
  → 选 (N,D) 用 Chinchilla (训练最优) 或 Overtrained (部署最优)
  → batch size 用 critical batch (D2)
  → LR 用 cosine 或 WSD
```

> **核心经验**：scaling law 不是"真理"，是**当前算力/数据/部署约束下的最优解**。约束变了（如推理算力降价、新架构出现），最优解也变。保持批判。
