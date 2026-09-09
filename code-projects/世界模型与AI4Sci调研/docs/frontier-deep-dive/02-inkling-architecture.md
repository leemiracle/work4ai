# Inkling 架构深挖：Thinking Machines Lab 的反主流选择

> 2026-07-15 Thinking Machines Lab（Mira Murati）发布 · 975B MoE / 41B 激活
> 首个从零训练 · Apache 2.0 开源 · 定位为"微调基底"

## TL;DR

Inkling 的价值不在"它是最强的"——作者明确说它不是。它的价值在于**验证了 5 个反主流架构选择在 975B 规模上可行**：相对位置偏置（不用 RoPE）、短卷积前置、5:1 SWA:Global 交替、训练嵌入 MTP、为微调而非 leaderboard 设计。这些选择单独看都有先例，但在千亿规模上组合验证是第一次。

---

## 1. 5 个反主流选择

### 1.1 相对位置偏置（不用 RoPE）

| 主流 | Inkling |
|---|---|
| RoPE（Llama/Qwen/DeepSeek/Mistral 全家）| 学习式相对位置偏置（learned relative position bias）|

**为什么反主流**：RoPE 在 2021 年后被几乎所有 LLM 采用，因为它"数学优雅"（旋转矩阵保证内积只依赖相对距离）+ "外推性好"（配合 NTK/YaRN）。

**Inkling 为什么选择不用 RoPE**：
- RoPE 的高频维度在长上下文下会"振荡不稳定"（见模块 11 §03 §NTK-aware scaling 实验）
- 相对位置偏置更"直接"——在 attention score 上加一个学习的偏置项 $b_{i-j}$，不需要旋转 Q/K
- **代价**：偏置表的大小是 $O(L)$（$L$ 是最大距离），1M 上下文需要 1M 个偏置参数

**历史回响**：这是 T5（2020）和 ALiBi（2021）思想的复兴——它们也用相对偏置。Inkling 在 975B 上验证了这个"古老"选择依然可行。

### 1.2 短卷积前置（每 block 加短卷积）

每个 Transformer block 的 K/V 投影之后，加一个**短卷积**（kernel size 通常 3-7）。

**作用**：在 attention 之前做一次"局部平滑"——提取 token 的局部模式（n-gram、短语边界），让 attention 聚焦在全局关系上。

**历史回响**：这是 Hyena / 极早期 convolution+attention 混合（如 ConvBERT）思想的回归。短卷积 + 全 attention 是"局部+全局"的天然分工。

### 1.3 5:1 SWA:Global attention 交替

Inkling 的 66 层中，每 6 层里 5 层是 sliding window attention（窗口大小 512），1 层是全局 attention。

| 配置 | SWA 层 | Global 层 | 比例 |
|---|---|---|---|
| Mistral 7B | 全部 SWA | 无 | 100:0 |
| Gemma 2 | 交错 | 交错 | 1:1 |
| **Inkling** | 5 层 | 1 层 | **5:1** |

**为什么 5:1**：SWA 省显存+计算（只看 512 token），Global 保长程检索（看到全部）。5:1 是 Inkling 在 1M 上下文下找到的"效率-质量"最优比。

**与模块 11 §07 的连接**：这是 sliding window attention 的最新工程化参数。模块 11 §07 §2.2 已讨论 SWA，Inkling 的 5:1 是新数据点。

### 1.4 训练嵌入 MTP（Multi-Token Prediction）

DeepSeek V3 把 MTP 作为训练目标，Inkling 把 MTP 的 drafter 层**训练时一起学**，推理时直接用作 speculative decoding 的 draft model——不需要外挂小模型。

**工程优势**：MTP drafter 和主模型共享表示（只是多了几个预测头），训练成本几乎不增，推理时 spec decoding 加速 2-3×。

### 1.5 为微调而非 leaderboard 设计

Inkling 作者明确说：**"这不是最好的模型"**。它的 token 效率、多模态广度、安全 refusal 行为、可微调性优先于 benchmark 分数。

**反共识**：2026 年的主流是"越大越强、leaderboard 越高越好"。Inkling 走了"做好基底，让下游微调发挥"的路——类似"Linux 内核"哲学而非"Windows 一体化"。

---

## 2. 关键数字

| 维度 | Inkling | Inkling-Small |
|---|---|---|
| 总参数 | 975B | 276B |
| 激活参数 | 41B | 12B |
| 激活率 | 4.2% | 4.3% |
| 层数 | 66 | 未公开 |
| 专家数 | 256 + 2 共享 | 未公开 |
| 每层激活专家 | 6 + 2 共享 | 未公开 |
| 上下文 | 1M | 1M |
| 模态 | 文本+图像+音频 | 同 |
| 权重格式 | BF16 / NVFP4 | BF16 |
| VRAM（BF16）| 2 TB | ~550 GB |
| VRAM（NVFP4）| 600 GB | ~165 GB |
| License | Apache 2.0 | Apache 2.0 |

---

## 3. 反直觉发现：Inkling-Small 在某些 benchmark 上**超过** Inkling

Inkling-Small（276B）在以下 benchmark 上**超越** Inkling（975B）：
- HLE with tools: 46.6% vs 46.0%
- GPQA Diamond: 88.3% vs 87.2%
- IFBench: 83.4% vs 79.8%
- CharXiv RQ: 83.4% vs 82.0%

**但在以下 benchmark 上明显落后**：
- SimpleQA Verified: 20.9% vs 43.9%（**事实记忆差 2×**）
- Tau 3 Banking: 13.6% vs 23.7%（**长程 agent 差 1.7×**）
- Terminal-Bench 2.1: 52.7% vs 63.8%

**洞察**：这组数据**清晰地分离了"推理"和"记忆"**。小模型推理能力不差（甚至更好——可能因为更少干扰），但事实记忆和长程 agent 能力需要更多参数。**这为"什么时候该用大模型"提供了量化依据**：需要事实/长程 → 大模型；需要纯推理 → 小模型可能够用。

---

## 4. 对 LLM 设计空间的 5 个启示

1. **RoPE 不是唯一答案**：相对位置偏置在 975B 上可行，值得重新评估
2. **短卷积 + attention 是自然的"局部+全局"分工**：纯 attention 不一定是最高效的
3. **5:1 SWA:Global 是 1M 上下文的工程最优比**（待更多模型验证）
4. **训练嵌入 MTP 是 spec decoding 的零成本路径**
5. **"推理 vs 记忆"的分离**：Inkling-Small 的数据提供了"何时该用大模型"的量化依据

---

## 5. 与项目的连接

- 模块 11 §03 位置编码：相对位置偏置 vs RoPE 的对比（更新"RoPE 一统天下"的叙事）
- 模块 11 §07 §2.2 SWA：5:1 比例是新工程数据点
- 模块 12 §05 §12.1 推测解码：训练嵌入 MTP 是新路径
- 模块 13 §13 形式化 Agent：Inkling 的"为微调设计"哲学与 Certigrad4 的"verified ML"有共鸣——基底稳定 + 上层适配

---

## 6. 来源

- [HF Blog: thinkingmachines-inkling](https://huggingface.co/blog/thinkingmachines-inkling)（官方发布 + 架构图）
- [IoT Digital Twin PLM 架构分析](https://iotdigitaltwinplm.com/inkling-thinking-machines-architecture-benchmarks-2026/)（第三方深挖，含 layer-by-layer 分析）
- Inkling 在 HuggingFace：`thinkingmachines/Inkling`（BF16）/ `thinkingmachines/Inkling-NVFP4`
- transformers v5.14.0+ 原生支持
