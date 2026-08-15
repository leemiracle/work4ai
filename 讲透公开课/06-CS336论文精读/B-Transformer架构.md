# B · Transformer 架构与组件（18 篇）

> 从 Attention 诞生到 2026 的 MLA/Mamba/字节级新架构。
> 对应讲座：**L3（architectures）、L4（attention alternatives + MoE）**

---

## B1. Vaswani et al. – Attention Is All You Need / Transformer (2017) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1706.03762](https://arxiv.org/pdf/1706.03762.pdf) · Google

**核心问题**：RNN 必须逐步计算（$h_t$ 依赖 $h_{t-1}$），无法并行；且长距离依赖靠隐藏状态传递，容易丢失。

**方法**：**完全抛弃循环，只用注意力**。

- **Scaled Dot-Product Attention**：
$$\text{Attn}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$
  - $Q=XW_Q, K=XW_K, V=XW_V$（self-attention 时 Q/K/V 都来自同一输入）
  - 除以 $\sqrt{d_k}$：防止点积过大导致 softmax 饱和（梯度消失）。直觉——点积方差正比 $d_k$，除以 $\sqrt{d_k}$ 让方差稳定在 1。

- **Multi-Head Attention**：把 $d$ 维拆成 $h$ 个 $\frac{d}{h}$ 维子空间，各自做 attention 再拼接。让模型在不同子空间关注不同关系（语法 vs 语义 vs 共指）。

- **残差连接 + LayerNorm**：每个子层 $x' = \text{LayerNorm}(x + \text{Sublayer}(x))$（post-norm 原版）。

- **Positional Encoding**：用正弦/余弦固定编码注入位置（因为 attention 本身是顺序无关的）。

**关键结果**：WMT 翻译 SOTA，且训练**完全并行**（比 LSTM 快一个数量级）。

**💡 工程经验**：
1. **CS336 A1 的核心就是手写 Transformer**——学生要实现 scaled dot product attention、multi-head attention、FFN、transformer block（共 14 个组件）。
2. **现代 LLM 和原版 Transformer 有 6 处关键差异**（理解这些是"从 2017 到 2026"的精华）：
   - encoder-decoder → **decoder-only**（GPT 路）
   - post-norm → **pre-norm**（训练更稳）
   - 正弦位置编码 → **RoPE**（B7）
   - LayerNorm → **RMSNorm**（B10，更快）
   - ReLU FFN → **SwiGLU**（B6）
   - MHA → **GQA**（B11，推理更快）
3. **注意力是 $O(n^2)$**——序列长度翻倍，计算量 4 倍。这是长序列的瓶颈，催生了整条 sparse/linear attention 路线（B3-B5, B14）。
4. **为什么除以 $\sqrt{d_k}$**：如果 $q,k$ 各分量是均值 0 方差 1 的独立分布，$q\cdot k$ 方差是 $d_k$。$d_k=64$ 时点积值域已达 ±24，softmax 会变成 near-one-hot，梯度几乎为 0。

**📍 CS336 角色**：L3 核心。整个课程围绕它展开。

---

## B2. Ba et al. – Layer Normalization (2016) ⭐⭐

- **链接**：[arxiv.org/abs/1607.06450](https://arxiv.org/pdf/1607.06450.pdf)

**核心问题**：BatchNorm 依赖 batch 维度，RNN/序列模型 batch=1 或变长时不好用；且训练/推理行为不一致。

**方法**：**对每个样本独立**，沿特征维归一化：$\bar x = \frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}$，$\mu,\sigma$ 是单个样本在特征维的统计。再学可仿射参数 $\gamma,\beta$。

**💡 工程经验**：
1. LayerNorm 是 Transformer 的标配——因为它不依赖 batch size，适合变长序列和单样本推理。
2. 但它比 RMSNorm 慢（多算均值）→ 现代模型（LLaMA 起）大多换 RMSNorm（B10）。
3. **LayerNorm 放哪**（pre-norm vs post-norm）影响巨大（见 B8）。

---

## B3. Child et al. – Generating Long Sequences with Sparse Transformer (2019) ⭐⭐

- **链接**：[arxiv.org/abs/1904.10509](https://arxiv.org/pdf/1904.10509.pdf) · OpenAI

**核心**：把 $O(n^2)$ 注意力改成**局部窗口 attention**——每个 token 只 attend 前面一个固定窗口 + 少量"跨步"（stride）全局点。复杂度降到 $O(n\sqrt{n})$ 或 $O(n)$。

**💡 工程经验**：
1. **长序列建模的最早系统方案**——让 Transformer 能处理图像/音频/长文本。
2. 局部 + 全局的**混合策略**成为后续所有长序列模型的设计模板（Longformer、BigBird、Longformer 都是变体）。
3. 局限：固定稀疏模式可能漏掉重要的长距离依赖。

**📍 CS336 角色**：L4 attention alternatives。

---

## B4. Beltagy et al. – Longformer (2020) ⭐⭐

- **链接**：[arxiv.org/abs/2004.05150](https://arxiv.org/pdf/2004.05150.pdf) · AllenAI

**核心**：**滑动窗口 attention**（每个 token 看左右 $w$ 个邻居，$O(n\cdot w)$）+ 少量**全局 attention**（在 [CLS]、标题等关键位置全 attend，捕捉任务信息）。

**💡 工程经验**：
1. 双层设计的精华：**局部处理细节，全局处理任务语义**——这个思路延续到今天的 long-context 设计。
2. Mistral 7B 用**滑动窗口 attention**（SWA）正是 Longformer 的简化版——证明在 8K-32K 上下文上又快又好。

---

## B5. Katharopoulos et al. – Linear Transformers (2020) ⭐

- **链接**：[arxiv.org/abs/2006.16236](https://arxiv.org/abs/2006.16236)

**核心**：用**核函数** $\phi(\cdot)$ 把 attention 改写成 $\sum_t \phi(K_t)\phi(K_t)^\top V_t$ 的形式，利用结合律**先聚合 $\phi(K)^\top V$ 再乘 $Q$**，复杂度从 $O(n^2 d)$ 降到 $O(n d^2)$。

**💡 工程经验**：
1. **理论很美，实践拉胯**——线性 attention 的表达力不如 softmax attention，质量普遍下降。说明 softmax 的非线性很关键。
2. 但思想被 **Performer、RWKV、Mamba** 继承：把 attention 改成"可递推的状态更新"，从而支持无限长上下文 + 恒定内存。

---

## B6. Shazeer – GLU Variants Improve Transformer (2020) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2002.05202](https://arxiv.org/pdf/2002.05202.pdf) · Google

**核心问题**：Transformer 的 FFN 用什么激活函数最好？

**方法**：实验 ReLU / GeLU / Swish，并引入 **GLU（Gated Linear Units）思想**——用一半隐藏单元"门控"另一半。

$$\text{FFN}_{\text{SwiGLU}}(x) = (\text{Swish}(xW_1) \odot xW_2) W_3$$

其中 Swish$(z) = z \cdot \sigma(\beta z)$。

**关键结果**：SwiGLU > GeGLU > ReGLU > 普通 FFN，质量提升且稳定。

**💡 工程经验**：
1. **SwiGLU 是现代 LLM 的 FFN 标配**——LLaMA、Mistral、Qwen、PaLM 全用。CS336 A1 明确要求实现 SwiGLU（`test_swiglu.npz`）。
2. **维度调整**：原 FFN 是 2 个矩阵（升维 $d \to 4d$，降维），SwiGLU 变 3 个矩阵。为保持参数量，把中间维从 $4d$ 降到 $\frac{2}{3} \cdot 4d = \frac{8}{3}d$，通常再取 64 或 128 的倍数。
3. 门控的直觉：让网络**动态决定哪些特征通过**——类似 LSTM 的门，但在 FFN 里。这增强了表达力。

**📍 CS336 角色**：A1 + L3。

---

## B7. Su et al. – Rotary Position Embedding / RoPE (2021) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2104.09864](https://arxiv.org/pdf/2104.09864.pdf)

**核心问题**：绝对位置编码（正弦/可学习）不擅长处理**相对位置**，且**外推到更长序列**时质量崩塌。

**方法**：对 query/key 做**旋转**——把 $d$ 维向量看成 $d/2$ 个二维平面，每个平面乘一个不同频率的旋转矩阵 $R_{\theta_i}$：

$$\tilde q = R_m W_q x, \quad R_m = \text{blockdiag}(R_{m\theta_1}, ..., R_{m\theta_{d/2}})$$

位置 $m$ 的 query 和位置 $n$ 的 key 做点积时，$R_m^\top R_n = R_{n-m}$——**只剩相对位置 $m-n$**！绝对编码，相对依赖，两全其美。

**💡 工程经验**：
1. **RoPE 是位置编码现代标配**——LLaMA/Mistral/Qwen/DeepSeek 全部采用。CS336 A1 要求实现（`test_rope.npz`）。
2. **频率设计**：$\theta_i = 10000^{-2i/d}$，低频分量对应大范围位置，高频对应精细位置——类似正弦编码但更优雅。
3. **长度外推**：RoPE 本身外推一般，但配合 **NTK-aware scaling** 或 **YaRN** 可外推到训练长度的 4-8 倍。LLaMA-2 从 4K 扩到 32K 就靠这个。
4. **实现技巧**：RoPE 可以用复数乘法或直接旋转矩阵实现，前者更简洁。CS336 测试用旋转矩阵版本。

**📍 CS336 角色**：A1 + L3。

---

## B8. Xiong et al. – On Layer Normalization in Transformer Architecture (2020) ⭐⭐

- **链接**：[arxiv.org/abs/2002.04745](https://arxiv.org/pdf/2002.04745.pdf)

**核心问题**：原版 Transformer 是 **post-norm**（先做子层再 LayerNorm：$\text{LN}(x + \text{sub}(x))$），但深层训练不稳。改成 **pre-norm**（先 LN 再子层：$x + \text{sub}(\text{LN}(x))$）会怎样？

**方法**：理论分析表明，post-norm 在初始时主路径梯度被 LayerNorm 阻断，导致**前几步训练发散**；pre-norm 让残差主路径畅通，梯度流好，训练更稳。

**💡 巙程经验**：
1. **所有现代 LLM 都用 pre-norm**——LLaMA、GPT-3、PaLM。post-norm 只在 BERT 这种浅层模型还行。
2. **pre-norm 的代价**：略微降低表达力（有论文指出 pre-norm 等价于"浅一些"的网络）。但稳定性收益远大于此。
3. 一个细节：pre-norm 时最后一层输出要**额外加一次 LayerNorm**（叫 FinalNorm），否则输出尺度不一致。

**📍 CS336 角色**：A1 + L3。学生实现的 transformer block 是 pre-norm 版。

---

## B9. Loshchilov & Hutter – Decoupled Weight Decay Regularization / AdamW (2017) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1711.05101](https://arxiv.org/pdf/1711.05101.pdf)

**核心问题**：原版 Adam 把权重衰减（L2 正则）加在梯度上：$g_t \leftarrow g_t + \lambda w$，再喂给 Adam 的自适应机制。但这导致**权重衰减被 $v_t$（梯度平方平均）缩放**，效果不对——频繁更新的参数，权重衰减被放大；不更新的参数，衰减几乎不起作用。

**方法**：**解耦**——权重衰减直接作用在参数上，不进 Adam 的 momentum/variance：

$$w_t = (1 - \eta\lambda) w_{t-1} - \eta \cdot \hat m_t / (\sqrt{\hat v_t} + \epsilon)$$

**💡 工程经验**：
1. **大模型训练必须用 AdamW**——SGD+momentum+decay 是等价的，但 Adam+decay（L2）不等价 AdamW。用错会导致泛化变差。
2. 权重衰减 $\lambda$ 通常设 $0.1$（LLaMA），但**作用其实更像正则化超参**，不是 L2 那么直接。
3. CS336 A1 第一个组件就是 AdamW（`test_adamw.npz`）。

**📍 CS336 角色**：A1 + L2。

---

## B10. Zhang & Sennrich – Root Mean Square Layer Normalization / RMSNorm (2019) ⭐⭐

- **链接**：[arxiv.org/abs/1910.07467](https://arxiv.org/abs/1910.07467)

**核心**：LayerNorm 要算均值 + 方差；RMSNorm **只算均方根**（不减均值）：

$$\bar x_i = \frac{x_i}{\sqrt{\frac{1}{d}\sum_j x_j^2 + \epsilon}} \cdot \gamma_i$$

**💡 工程经验**：
1. **省掉均值计算，速度快 7-64%**（论文数据）。大模型训练省 10% 时间就是巨量 GPU 小时。
2. 实验表明质量与 LayerNorm 持平甚至略好——因为减均值对 Transformer 的 attention 输入意义不大。
3. **LLaMA/Mistral/Qwen/DeepSeek 全用 RMSNorm**。CS336 A1 实现 RMSNorm（`test_rmsnorm.npz`）而非 LayerNorm。

**📍 CS336 角色**：A1 + L3。

---

## B11. Ainslie et al. – GQA / Grouped-Query Attention (2023) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2305.13245](https://arxiv.org/pdf/2305.13245.pdf) · Google

**核心问题**：MHA（multi-head）每个 query head 有一组独立的 K/V，**KV cache 太大**（推理瓶颈）。MQA（multi-query）所有 head 共享一组 K/V，快但质量降。

**方法**：**GQA 取中间值**——把 query head 分成 $G$ 组，每组共享一组 K/V。$G=1$ 退化为 MQA，$G=H$（head 数）退化为 MHA。

**💡 工程经验**：
1. **GQA 是推理优化的关键 trick**——LLaMA-2-70B 用 GQA（8 组 KV head for 64 query heads），LLaMA-3、Mistral、DeepSeek-V2 全用。
2. **KV cache 内存**正比 KV head 数：MHA→GQA(8)→MQA(1) 递减 8 倍。对长上下文（32K+），这是显存生死线。
3. 实验表明 $G=8$ 左右几乎无损质量，是性价比甜点。
4. CS336 L4 / L10（inference）讲 KV cache 时必提。

**📍 CS336 角色**：L4 + L10。

---

## B12. Henry et al. – QK-Norm (2023) ⭐

- **链接**：[arxiv.org/abs/2302.05442](https://arxiv.org/abs/2302.05442)

**核心**：在 Q、K 做 attention 之前各加一个 **LayerNorm/RMSNorm**，把它们的尺度拉回 1，防止 attention logit 爆炸。

**💡 工程经验**：训练超大模型（100B+）或超长序列时，QK 点积会数值不稳定——加 QK-Norm 提升稳定性。Cohere、Qwen、一些 2024 模型采用。小模型上收益不明显。

---

## B13. Tay et al. – ByeT5 / 字节级模型 (2021) ⭐

- **链接**：[arxiv.org/abs/2105.13626](https://arxiv.org/abs/2105.13626)

**核心**：直接在**字节**上建模（不经 tokenizer），消除 OOV/分词不一致问题。代价是序列长度爆炸（字节比 token 长 5-6 倍）。

**💡 工程经验**：字节级是"终极 tokenizer"的理想——无预处理、无语言偏见、对拼写/代码/多语言鲁棒。但计算成本高，催生了 Megabyte（分层）、BLT（动态分块）等折中方案。

---

## B14. Tay et al. – Megabyte (2023) ⭐⭐

- **链接**：[arxiv.org/abs/2305.07185](https://arxiv.org/pdf/2305.07185.pdf)

**核心**：分层字节建模——**全局模型**处理"块"（256 字节一组），**局部模型**处理块内字节。全局 $O(n^2)$ 中 $n$ 是块数（远小于字节数），局部并行无 attention。总复杂度 $O(n^{1.5})$ 级。

**💡 工程经验**：让字节级建模**计算可行**——是 BLT（Meta 2024）的直接前驱。

---

## B15. DeepSeek-V2 / MLA – Multi-head Latent Attention (2024) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2405.04434](https://arxiv.org/abs/2405.04434)

**核心问题**：GQA 已压缩 KV head，但长上下文（128K+）下 KV cache 仍然巨大。

**方法**：**MLA 把 KV 压缩成低秩潜在向量**。对每个 token，只缓存一个**小的压缩向量** $c_t$（维度远小于 $d \cdot n_{kv}$）；推理时从 $c_t$ **动态上采样**回完整 K/V。

$$c_t = W_c x_t, \quad K_t = W_K c_t, \quad V_t = W_V c_t$$

配合 RoPE 的特殊处理（解耦部分），MLA 能把 KV cache 压到 GQA 的 1/4 甚至更低，**质量不降反升**。

**💡 工程经验**：
1. **2024 年最重要的架构创新之一**——DeepSeek-V2/V3 用 MLA 支撑 128K 上下文且推理极快。
2. MLA + MoE = DeepSeek 的效率法宝，让它能用远少于 LLaMA 的推理算力达到同等质量。
3. 思想本质：**KV cache 是显存瓶颈 → 用低秩压缩减少存储 → 推理时解压**。类似 LoRA 压缩权重的思路，但用在 KV 上。

**📍 CS336 角色**：L4 attention alternatives 的前沿案例。

---

## B16. Dao & Gu – Mamba-2 / SSM (2024) ⭐⭐

- **链接**：[arxiv.org/abs/2405.21060](https://arxiv.org/abs/2405.21060)

**核心**：**状态空间模型（SSM）**——用线性时不变系统 $h_t = \bar A h_{t-1} + \bar B x_t$ 替代 attention。Mamba 引入**选择机制**（输入相关的 $A,B$），让 SSM 能像 attention 一样选择性记忆/遗忘。Mamba-2 与 attention 建立了数学联系（SSM ⊂ structured attention）。

**💡 工程经验**：
1. Mamba 的优势：**线性复杂度 + 恒定推理内存**（像 RNN 一样递推），适合超长序列。
2. 实践中纯 Mamba 在 LM 上略逊 Transformer，但 **Mamba-Transformer 混合**（如 Jamba、Nemotron-3）成为 2025 热门方向。
3. CS336 L19 邀请 **Dan Fu**（Mamba 作者）做 guest lecture。

**📍 CS336 角色**：L4 + L19（Dan Fu guest）。

---

## B17. Pernias et al. – BLT / Byte Latent Transformer (2024) ⭐⭐

- **链接**：[arxiv.org/abs/2412.09871](https://arxiv.org/abs/2412.09871) · Meta

**核心**：**动态字节分块**——不像 BPE 用固定词表，而是根据**熵**动态决定切分点（高熵处切分）。局部小模型处理块内字节，全局大模型处理块。

**💡 工程经验**：解决了 BPE 的"固定词表偏见"问题，且能自适应地分配计算（难的地方切更细）。Meta 2024 展示 BLT 在同等算力下可媲美 LLaMA-3。

---

## B18. T-Free / Aux-Free (2024) ⭐

- **链接**：T-Free [arxiv.org/abs/2406.19223](https://arxiv.org/abs/2406.19223) ｜ Aux-Free [arxiv.org/abs/2408.15664](https://arxiv.org/abs/2408.15664)

**T-Free**：不用 embedding 矩阵做 token 映射，而是用**稀疏特征**直接从隐藏状态映射回 token——大幅减小参数（embedding 占大模型 30%+ 参数）。

**Aux-Free**：解决训练时"词表头部 token 被过度学习"的不均衡问题（auxiliary loss 的替代）。

**💡 工程经验**：tokenizer/embedding 是 LLM 的"隐性税"——这两篇代表 2024 对它的反思。

---

## B 类总结：架构进化路线图

```
2017 Transformer (post-norm + MHA + 正弦PE + ReLU FFN)
   ↓ 6处改造
2024 现代 LLM (pre-norm + GQA/MLA + RoPE + SwiGLU + RMSNorm)

长序列分支:
  Sparse(2019) → Longformer(2020) → Linear(2020) → Mamba(2024)
                                                    ↓
                                         混合架构(2025-2026)

字节级分支:
  ByteT5(2021) → Megabyte(2023) → BLT(2024)
```

> **核心经验**：理解每个组件"为什么被换掉"，比记住最终配方更重要。因为 2027 的配方可能又变了，但设计逻辑（稳定、高效、表达力）不变。
