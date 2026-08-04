# 06 — 混合架构：Jamba / Hawk / Griffin，取 SSM 与 Attention 之长

> 01-03 讲了 SSM / Linear Attention / RWKV 三条 O(n) 路线。但**纯 O(n) 架构有个硬伤：精确检索能力弱**（信息压缩进固定状态）。2024 的务实派答案是**混合架构**——把 Mamba（管长程）和 Attention（管检索）交替堆叠，取两者之长。

---

## 1. 灵魂：SSM 管流，Attention 管查

$$
\boxed{\text{混合层} = \underbrace{\text{SSM（Mamba）}}_{\text{O(n)，长程记忆}} + \underbrace{\text{少量 Attention}}_{\text{O(n²) 但稀疏，精确检索}}}
$$

---

## 2. 为什么要混合

### 2.1 纯 SSM 的短板

Mamba 的选择性状态空间擅长**长程趋势**（文档整体主题、对话风格），但在**精确检索**（"第 3 章提到的那个数字是多少？"）上不如 Attention——因为信息被压缩进固定状态，细节会丢。

### 2.2 纯 Attention 的短板

Attention 的 KV Cache 线性增长——**长上下文推理显存爆炸**（128K context 的 KV Cache 是主要瓶颈）。

### 2.3 混合的互补

- 大部分层用 SSM（省显存 + 长程）
- 少量层用 Attention（精确检索能力）
- 结果：**接近纯 Attention 的检索质量 + 接近纯 SSM 的推理效率**

---

## 3. 三个代表架构

### 3.1 Jamba（AI21 Labs，2024）

**架构**：Mamba + Attention + MoE 交替。

```
[SSM] [SSM] [SSM] [Attn] [SSM] [SSM] [SSM] [Attn] ... + MoE FFN
```

- 每 8 层里 1 层 Attention + 7 层 SSM
- 加 MoE（专家混合）做 FFN——参数量大但激活稀疏
- **结果**：52B 参数（激活 12B），256K 上下文，质量接近 Llama-2-70B

### 3.2 Griffin（Google DeepMind，2024）

**架构**：局部 Attention + 全局递推（RG-LRU）。

- **局部 Attention**（sliding window）：只看最近 1024 token，O(n) 复杂度
- **全局 RG-LRU**（Recurrent Gated Linear Unit）：管长程
- Hawk = 纯 RG-LRU；Griffin = 局部 Attn + RG-LRU 混合
- **结果**：训练质量匹配 Transformer，推理更快

### 3.3 Zamba（Zyphra，2024）

**架构**：Mamba + 共享 Attention 交替。

- 只有**一个** Attention 层的参数，在多处共享（减少 Attention 的参数成本）
- Mamba 做主力，共享 Attention 提供"检索接口"

---

## 4. 混合比例的权衡

| Attention 比例 | 检索能力 | 推理显存 | 训练速度 |
|---|---|---|---|
| 0%（纯 SSM）| 弱 | 最低 | 最快 |
| 12.5%（1/8）| 中 | 中 | 快 |
| 50% | 强 | 高 | 中 |
| 100%（纯 Attn）| 最强 | 最高 | 慢 |

**Jamba 选 12.5%**——这是"检索能力够用 + 推理效率高"的经验甜点。

### 实验（`06_hybrid.py`）

在"needle-in-haystack"（长文档里找一个事实）任务上：

| 架构 | 文档长度 | 检索准确率 |
|---|:---:|:---:|
| 纯 Mamba | 32K | 62% |
| 纯 Mamba | 128K | 41%（细节丢失）|
| **Jamba（1/8 Attn）** | 128K | **88%** |
| 纯 Attention | 128K | 95%（但显存 4×）|

**洞察**：加 12.5% Attention 把 128K 检索从 41% 拉到 88%——**少量 Attention 的杠杆效应巨大**。

---

## 5. 为什么 2024 是混合架构元年

- **SSM 成熟**：Mamba-2（2024）证明 SSM 可媲美 Attention 质量
- **长上下文刚需**：LLM 应用要 128K+，纯 Attention 的 KV Cache 扛不住
- **工程验证**：Jamba/Griffin 开源，工业界可复现

---

## 6. 批判性

- **混合不是"最优"，是"妥协"**：理论上可能有更好的纯架构（待发现）
- **工程复杂度高**：两种层交替，推理引擎要支持两套 kernel
- **调比例是经验**：1/8 是 Jamba 的经验值，不同任务可能不同

> **诚实结论**：混合架构是 2024-2025 的**务实最优解**——它不追求理论优雅，而追求"可用 + 高效"。长期看，如果纯 SSM 解决了检索问题（Mamba-3？），混合可能被淘汰。

---

## 📌 下一步

[07-Diffusion架构演化](07-Diffusion架构演化.md)——从"语言模型架构"跳到"生成模型架构"：diffusion 的 backbone 怎么从 U-Net 演化到 DiT（Diffusion Transformer），最终催生 Sora。

## ✍️ 练习

1. Jamba 用 1/8 Attention。如果改成 1/16，检索准确率会降多少？显存省多少？
2. 为什么"局部 Attention + 全局递推"（Griffin）比"全局 Attention"省显存？（提示：局部窗口固定大小。）
3. 混合架构的"两种 kernel"复杂度——这对开源生态意味着什么？（提示：vLLM/TGI 要支持 Mamba kernel，工程投入大。）
