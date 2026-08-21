# 07 预训练与 Scaling Laws

> 预训练 = 用海量无标注文本做 next-token prediction。Scaling Laws 告诉我们"怎么分配算力最划算"。
> 这是大模型时代的"物理定律"。

---

## 一、预训练目标: Next-Token Prediction

给定文本 $x_1, x_2, ..., x_T$, 最大化:
$$\mathcal{L} = -\frac{1}{T}\sum_{t=1}^{T} \log P(x_t \mid x_{1:t-1}; \theta)$$

就是**交叉熵** (你学过的损失函数!)。模型学会预测下一个 token, 就顺便学会了语法、知识、推理。

> 💡 **CS25 连接**: Jason Wei (OpenAI, CS25 V4) 讲 "Intuitions on Language Models"——把 next-token prediction 理解为"海量多任务学习", 每个 token 是一个训练样本, 不同 token 隐含不同任务。这个视角解释了 scaling 和涌现。

---

## 二、Chinchilla Scaling Law (2022) — 最重要的定律

DeepMind 2022 发现: 给定固定算力预算 $C$, 模型参数 $N$ 和数据 token 数 $D$ 应该按特定比例分配, 才能最小化 loss:

$$\mathcal{L}(N, D) = E + \frac{A}{N^\alpha} + \frac{B}{D^\beta}$$

**核心结论**: **算力最优 = 每个参数训练约 20 个 token** ($D \approx 20N$)。

| 模型 | 参数 N | 最优数据 D=20N | 实际教训 |
|------|--------|---------------|---------|
| GPT-3 | 175B | 3.5T | 只训了 0.3T, **严重欠训练** |
| Chinchilla | 70B | 1.4T | 用 1.4T, 以 175B 1/2 的算力超越 GPT-3 |
| LLaMA | 65B | 1.3T | 训了 1.4T, 接近最优 |

> **教训**: GPT-3 之后大家发现, 与其堆参数, 不如堆数据。LLaMA/Qwen/DeepSeek 都按 Chinchilla 比例训练。

---

## 三、三个关键发现

### 1. 涌现能力 (Emergent Abilities)
Jason Wei et al. 2022: 某些能力 (链式推理、多步数学) 在小模型上**几乎为 0**, 到某个规模**突然出现**。这是"量大出奇迹"的实证。

### 2. 数据质量 > 数据数量
"Garbage in, garbage out"。DeepSeek/Math 用大量**高质量推理数据** (含 CoT) 预训练, 即使后训练也补不回来 (CS25 V6 Prabhumoye: "front-loading reasoning-rich data during pretraining yields persistent gains")。

### 3. 后 Chinchilla: 数据墙
2024+ 最优模型已训练 **15-50 倍 Chinchilla 比例**的数据 (LLaMA-3 用 15T token 训 70B), 因为推理质量收益大于过拟合代价。但**高质量文本即将耗尽**, 合成数据成新方向。

---

## 四、训练技术栈

| 组件 | 现代选择 |
|------|---------|
| 优化器 | **AdamW** (lr=1e-4~3e-4) + weight decay 0.1 |
| 学习率 | **Warmup + Cosine decay** (先升后降) |
| batch size | 渐进增大 (从 0.5M 到 4M+ token/step) |
| 并行 | 数据并行 + 张量并行 + 流水线并行 + **专家并行** (MoE) |
| 精度 | BF16 训练, **FP8** (DeepSeek-V3) 进一步省显存 |

---

## 参考文献
- Kaplan et al. 2020, *Scaling Laws for Neural Language Models* (原始 scaling law)
- Hoffmann et al. 2022, *Training Compute-Optimal LLMs* (Chinchilla)
- Wei et al. 2022, *Emergent Abilities of Large Language Models*
- CS25 V4: Jason Wei "Intuitions on Language Models"
- CS25 V6: Prabhumoye "From Next-Token Prediction to Next-Generation Intelligence"
