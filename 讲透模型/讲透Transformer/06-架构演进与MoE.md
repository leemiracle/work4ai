# 06 架构演进与 MoE：从原版 Transformer 到 DeepSeek-V3

> 2017-2025, Transformer 架构经历了"探索 → 收敛 → MoE 再分化"四个时代。
> 现代 dense 模型高度收敛到"LLaMA 配方"; MoE 成了前沿模型的标配。

---

## 四个时代 (jytan.net 框架)

| 时代 | 时期 | 主旋律 |
|------|------|--------|
| I. 奠基 | 2017-2019 | 原版确立, 立即涌现大量变体探索 |
| II. 缩放驱动 | 2020-2022 | 为 scale 优化: RMSNorm, RoPE, SwiGLU 涌现 |
| III. LLaMA 结晶 | 2023-2024 | LLaMA 把配方固化, 标准化加速 |
| IV. MoE 主导 | 2024-2025 | MoE 成新缩放轴, 多样性回归 |

---

## 一、LLaMA 配方 (2023, dense 模型的黄金标准)

LLaMA (2023.02) 把前几年的零散创新**结晶**成一个可复现配方, 之后几乎所有开源模型照搬:

| 组件 | 选择 | 来源 |
|------|------|------|
| 归一化 | Pre-Norm + **RMSNorm** | (05 篇) |
| 位置编码 | **RoPE** | (02 篇) |
| 激活/FFN | **SwiGLU** + 8/3 扩展 | (04 篇) |
| Attention | MHA (LLaMA-1) → **GQA** (LLaMA-2+) | (03 篇) |
| bias | **全部去掉** | kernel 友好 |
| 架构 | Decoder-Only | 自回归生成 |

> **为什么这个配方赢了**: 不是某个组件绝对最优, 而是**稳定性 + 吞吐 + 推理成本**的综合最优, 加上 FlashAttention/fused kernel 的生态网络效应——"kernel 支持什么, 大家就用什么"。

---

## 二、MoE (Mixture of Experts): 新缩放轴

### 核心思想: 稀疏激活

Dense 模型: 每个 token 激活所有参数。
MoE: 把 FFN 换成 **N 个专家 FFN**, 每次只路由到 **top-k 个**:
$$\text{FFN}_{\text{MoE}}(x) = \sum_{i \in \text{top-}k} g_i(x) \cdot \text{Expert}_i(x)$$
- 总参数大 (容量大), 但每 token 激活参数少 (计算省)。
- **路由器 (router/gate)** $g_i(x)$: 一个小线性层, 决定每个 token 去哪个专家。

### 演化

| 模型 | 时间 | 总参/激活 | 专家配置 |
|------|------|----------|---------|
| GShard | 2020 | - | 早期 MoE |
| **Mixtral 8×7B** | 2024.01 | 46.7B / 12.9B | 8 专家, 激活 2 |
| **DeepSeek-V3** | 2024.12 | 671B / 37B | 256+1 共享, 激活 8 |
| Llama 4 Maverick | 2025.04 | 400B / 17B | 128+1, 激活率 4.3% |
| Kimi K2 | 2025.07 | 1.04T / 32B | 384, 激活 8 |

### DeepSeek 的两大 MoE 创新

1. **细粒度专家 + 共享专家**: 把大专家拆成更多小专家 (更精细路由) + 隔离几个共享专家 (处理通用模式, 防冗余)。
2. **Auxiliary-loss-free 负载均衡**: 传统 MoE 加辅助损失强制专家负载均衡, 但会损害质量。DeepSeek 改用**偏置项 $b_i$** 只影响路由决策不影响专家加权——解决了 MoE 训练的老大难。

### Dense 前 3 层
DeepSeek-V3 前 3 层用 dense (不 MoE)。原因: 早期层要先提取基础语法语义特征, 此时路由器还做不好决策, 稀疏路由会不稳定。后来多个实验室跟进这个做法。

---

## 三、2025-2026 前沿: 三大方向

### 1. 稀疏注意力 (打破 O(n²))
- **DeepSeek Sparse Attention (DSA)**: token 级稀疏, 选最相关的 token, 复杂度 $O(L^2) \to O(L \cdot k)$
- FlashAttention 的各种变体

### 2. 残差进化: mHC (DeepSeek 2025.12)
把单条残差 $x + f(x)$ 推广成**多条并行残差流的混合** (Hyper-Connections)。问题是信号会爆炸 (>3000×)。mHC 用 **Birkhoff 多面体 + Sinkhorn 算法**约束混合矩阵为双随机, 把信号增益从 3000× 压到 1.6×。可能是 DeepSeek V4 的骨干。

### 3. 原生多模态 (early fusion)
Llama 4 / Gemini 3 把视觉 token 和文本 token **从第 1 层就拼在一起** (早期融合), 而非先用 vision encoder 再适配 (晚期融合)。cross-modal attention 从第 1 层就建立, 跨模态推理更强。

---

## 四、Decoder-Only 为何统一天下

现代大模型 (GPT/LLaMA/DeepSeek/Qwen) 几乎全是 **Decoder-Only**:
- 生成任务通用性最强 (chat/code/agent 都靠生成)
- Causal mask 让训练天然 scale (无双向依赖)
- 自回归 + KV Cache 推理高效

Encoder-Only (BERT) 退居"理解"任务 (分类/嵌入), Encoder-Decoder (T5) 在翻译/seq2seq 仍有用, 但都不是主流。

---

## 参考文献
- Touvron et al. 2023, *LLaMA* (配方结晶)
- Jiang et al. 2024, *Mixtral of Experts* (CS25 V4 讲过)
- DeepSeek-AI 2024, *DeepSeek-V2/V3* (MLA + MoE)
- jytan.net 2025, *The Crystallization of Transformer Architectures* (四时代框架)
- largo.dev 2026, *Frontier LLM Architectures 2026* (mHC/iRoPE/early fusion)
- DeepSeek 2025, *Manifold-Constrained Hyper-Connections* (mHC)
