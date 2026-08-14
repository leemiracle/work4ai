# 05 · KV Cache 量化：精度压缩的代价与收益

> [00 §3.2](./00-为什么KV Cache是推理的生命线.md) 算过：Llama-3-70B batch=32 要 86GB KV。量化到 INT4 → ~22GB——**装得下了**。但 KV Cache 量化比权重量化**风险更高**：权重的误差分布在所有 token 上被平均，而 KV 的误差会在**每一步 attention 的 softmax 里放大**——一个异常 KV 直接扰乱整个分布。本章把"为什么能压""压到什么程度会崩""怎么压才不崩"讲透。
>
> 配套：[00 §3.2](./00-为什么KV Cache是推理的生命线.md)（成本账）+ [vLLM 量化文档](https://docs.vllm.ai/en/latest/quantization/)

---

**2024 年夏。** 一位推理服务工程师照搬权重量化的经验，把 KV Cache 直接 INT4 量化——损失"应该 1-2% 吧"。上线后用户反馈：**模型在长上下文时开始"幻觉 + 跑题"**。他困惑地 grep loss 曲线：整体 perplexity 只涨了 1.5%，**但长序列（>8K token）的 task 涨了 12%**。重读论文才发现：KV 误差通过 softmax 指数放大，**长上下文是误差累积的重灾区**。他加了一招"重要 token 保 FP8、其余 INT4"的混合精度，损失压回 0.3%。**这件事教育了整个社区：KV 量化不是权重量化的复刻**。

---

## 一、为什么 KV 量化比权重难

### 1.1 误差传播路径不同

- **权重量化**：$W$ 量化误差 → 直接进激活，被 LayerNorm 部分吸收
- **KV 量化**：$K$ 误差进 softmax 分母，$V$ 误差进加权和——**两个地方都被指数函数放大**

### 1.2 异常值 (outlier) 集中

LLM 的 K/V 在少数通道有 **outlier**（数值大几十倍）。朴素 per-tensor 量化把整体 scale 拉到 outlier 大小 → 大部分通道的有效精度只有 2-3 bit。

## 二、三档量化方案

### 2.1 FP8（保守派）

- vLLM 原生支持，per-head 或 per-tensor
- **几乎零质量损失**（<0.5% perplexity）
- 显存减半——**最安全的"免费午餐"**

### 2.2 INT8 / INT4（中庸）

- 需要 **per-token 量化**（每个 token 独立 scale）或 **per-channel 量化**（每个 KV 通道独立 scale）
- INT4 + per-channel：质量损失 1-3%，显存 1/4
- INT4 + per-tensor：**直接崩**——长上下文涨 10%+

### 2.3 1.58-bit（极端派，2025 学术热点）

- **ternary**：{-1, 0, +1}
- 代表工作：**BitNet**（权重 1.58-bit）+ 后续 KV 1.58-bit 探索
- 极致压缩，但**需要训练时量化感知（QAT）**——纯 PTQ 做不到
- 2026 仍在前沿研究阶段

## 三、反模式与陷阱

### 3.1 L4 陷阱 1：照搬权重量化的 per-tensor

这是最常见的崩盘原因。**KV 必须用 per-token 或 per-channel scale**——vLLM 的 `fp8` 模式默认 per-token。

### 3.2 L4 陷阱 2：忽视长上下文累积误差

报告里 perplexity 平均涨 1% 不代表没事——**8K+ 长度可能涨 10%**。必须单独跑长上下文 benchmark（如 RULER、LongBench）验证。

### 3.3 L4 陷阱 3：和 MLA 的叠加要小心

MLA（[04](./04-MLA深挖.md)）只存 latent，**latent 量化和朴素 KV 量化路径不同**——直接对 latent 做 INT4 可能比朴素 KV INT4 更差。DeepSeek-V3 的部署用 **latent FP8**，不是 INT4。

### 3.4 L4 陷阱 4：忽视 K 和 V 的不对称

**K 对量化更敏感**（K 进 softmax 分母，指数放大）；V 更鲁棒（线性加权和）。生产实践：**K 用 FP8 / V 用 INT4** 是常见不对称组合。

## 四、和 PagedAttention / MLA 的关系

- **PagedAttention**（[02](./02-PagedAttention深挖.md)）：治碎片——与量化正交，可叠加
- **MLA**（[04](./04-MLA深挖.md)）：治表示效率——叠加时对 latent 而非 KV 量化
- **分层存储**（[06](./06-分层KVCache.md)）：治容量——量化是"压"，分层是"卸"，**两者互补**

## 五、选型决策树

```
你的瓶颈是显存吗？
├─ 否 → 不要量化（成本不该付）
└─ 是 → 上下文长度？
   ├─ < 8K → FP8（零风险，减半）
   ├─ 8K-32K → INT8 per-token（损失 <1%）
   ├─ 32K-128K → INT4 per-channel + K 保 FP8
   └─ > 128K → 必须配合分层存储或 MLA
```

## 六、费曼回炉（L2 自检）

- **F2 卡壳点**：我曾以为"FP8 / INT8 / INT4"是平滑渐进。实测后发现**存在断崖**：FP8 → INT8 平滑，INT8 → INT4 不做 per-channel 直接崩——这是**量化噪声 vs outlier 比值**的相变。
- **F3 术语翻译**：
  - "per-token scale" → 每个新 token 单独算一把"刻度尺"
  - "outlier channel" → 少数"嗓门特别大"的通道，会绑架整组
- **F4 回炉**：v1 我写"INT4 损失 1-2%"——平均看是对的；v2 强调"**长上下文是真正考验**，benchmark 必须覆盖长序列"。

---

> 🎯 **一句话**：KV 量化比权重量化风险高（softmax 放大 + outlier 集中）——**FP8 是免费午餐，INT4 必须 per-channel + 长上下文单独验证**，和 PagedAttention / MLA 正交可叠加。

📌 **下一步**：[06 分层 KV Cache](./06-分层KVCache.md)（GPU/CPU/SSD 三级），或回 [README](./README.md)。
