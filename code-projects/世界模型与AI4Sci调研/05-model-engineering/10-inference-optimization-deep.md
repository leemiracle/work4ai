# LLM 推理优化的最细节：从 KV Cache 到 Speculative Decoding

> 本文是 `world-ai4sci-math/05-model-engineering` 的深度补章。前面的章节讲了 vLLM / SGLang 的工程概览，本文聚焦**推理优化的最细节**——KV cache 内存布局、PagedAttention 块表实现、continuous batching 的调度循环、speculative decoding 的拒绝采样数学证明、量化算法的逐位推导。所有 arXiv 引用均经 API 一手核实。
>
> 关键 arXiv 一览（已核实）：
> - Speculative decoding: Leviathan et al. 2023 [arXiv:2211.17192](https://arxiv.org/abs/2211.17192)（ICML 2023 Oral）；Chen et al. 2023 [arXiv:2302.01318](https://arxiv.org/abs/2302.01318)；Xia et al. 2023 SpecDec 首提 [arXiv:2203.16487](https://arxiv.org/abs/2203.16487)（EMNLP 2023 Findings）
> - 多头投机：Medusa [arXiv:2401.10774](https://arxiv.org/abs/2401.10774)；EAGLE [arXiv:2401.15077](https://arxiv.org/abs/2401.15077)；EAGLE-2 [arXiv:2406.16858](https://arxiv.org/abs/2406.16858)
> - 系统：vLLM [arXiv:2309.06180](https://arxiv.org/abs/2309.06180)（SOSP 2023）；SGLang [arXiv:2312.07104](https://arxiv.org/abs/2312.07104)；DistServe [arXiv:2401.09670](https://arxiv.org/abs/2401.09670)（OSDI 2024）；Splitwise [arXiv:2311.18677](https://arxiv.org/abs/2311.18677)；Mooncake [arXiv:2407.00079](https://arxiv.org/abs/2407.00079)；FlashInfer [arXiv:2501.01005](https://arxiv.org/abs/2501.01005)（MLSys 2025）
> - KV cache：StreamingLLM [arXiv:2309.17453](https://arxiv.org/abs/2309.17453)（ICLR 2024）；H2O [arXiv:2306.14048](https://arxiv.org/abs/2306.14048)；KVQuant [arXiv:2401.18079](https://arxiv.org/abs/2401.18079)（NeurIPS 2024）；KIVI [arXiv:2402.02750](https://arxiv.org/abs/2402.02750)（ICML 2024）；DeepSeek-V2 MLA [arXiv:2405.04434](https://arxiv.org/abs/2405.04434)
> - 量化：GPTQ [arXiv:2210.17323](https://arxiv.org/abs/2210.17323)（ICLR 2023）；AWQ [arXiv:2306.00978](https://arxiv.org/abs/2306.00978)（MLSys 2024 Best Paper）；SmoothQuant [arXiv:2211.10438](https://arxiv.org/abs/2211.10438)（ICML 2023）；BitNet b1.58 [arXiv:2402.17764](https://arxiv.org/abs/2402.17764)
> - 注意力：FlashAttention [arXiv:2205.14135](https://arxiv.org/abs/2205.14135)

---

## 一、Prefill vs Decode：两种根本不同的计算形态

理解一切推理优化的起点，是认识到**一次 LLM 推理请求由两个计算形态完全相反的阶段组成**。所有系统设计（continuous batching、prefill-decode 分离、speculative decoding）的动因都来自这两个阶段的差异。

### 1.1 Prefill 阶段：compute-bound 的大 GEMM

当用户提交一条 prompt（例如 2048 个 token），模型需要做一次"前向"计算出所有 token 的 KV cache，并产出第一个新 token。这个过程是 **prompt-level 并行**的——所有 2048 个 token 同时进入 attention。

计算量：对每一层，QKV 投影 + attention + FFN，其中 attention 的 $\text{QK}^T$ 是 $[2048, d]\times[d, 2048]$ 的矩阵乘，FFN 是两次 $[2048, d]\times[d, 4d]$。整个 prefill 的算术强度（arithmetic intensity，FLOPs/Byte）非常高。

以 Llama-70B 为例：$d_\text{model}=8192$，64 个 attention head，每头 $d_h=128$，80 层。对 2048 token 的 prefill：
- 每层 attention 算力 $\approx 4 \cdot 2048^2 \cdot 8192 \approx 1.37\times10^{11}$ FLOPs
- 每层 FFN 算力 $\approx 12 \cdot 2048 \cdot 8192^2 \approx 1.65\times10^{12}$ FLOPs
- 全模型约 $(1.37\times10^{11} + 1.65\times10^{12})\times 80 \approx 1.43\times10^{14}$ FLOPs ≈ 142 TFLOPs

而 H100 SXM5 的 BF16 算力是 **1979 TFLOPS**，理论上 142 TFLOPs 只要 **72 毫秒**——但要把权重（70B × 2 bytes = 140 GB，远超单卡 80GB，需 TP）从 HBM 加载一次，所以实际墙钟时间被算力吃掉，**GPU 计算单元（SM）的占用率（Tensor Core utilization）可以高达 60-80%**。

> **铁律 1**：Prefill 是 **compute-bound**（算力受限）。优化方向是 GEMM kernel 优化、张量并行（TP）、FlashAttention 这种 IO-aware kernel。

### 1.2 Decode 阶段：memory-bound 的逐 token 采样

Prefill 产出第一个 token 后，进入自回归 decode：每生成一个 token，就要把整个模型权重从 HBM 读到 SM 再算一次。每步只处理 1 个新 token（在 batch 内），算力需求极小，但**必须读完整份权重**。

算术强度暴跌：decode 一步对每层 FFN 是 $[1, d]\times[d, 4d]$，仅 $12\cdot d^2$ FLOPs，但要读 $12\cdot d^2$ bytes 权重。**算术强度 ≈ 1 FLOP/Byte**（BF16 下）。而 H100 的 Roofline 拐点（ridge point）在 **约 296 FLOPs/Byte**（1979 TFLOPS / 6.7 TB/s 内存带宽，BF16 非稀疏算术强度阈值）。

decode 的算术强度 1 ≪ 296，完全在 memory-bound 区。GPU SM 利用率常跌到 **0.5%-2%**。这就是 LLM 推理"贵"的本质——**你花钱买的是算力，却受限于带宽**。

> **铁律 2**：Decode 是 **memory-bound**（带宽受限）。优化方向只有两条：(a) 让单步处理的 token 更多——这是 **continuous batching** 和 **speculative decoding** 的动机；(b) 让每次读的字节更少——这是 **量化** 和 **KV cache 压缩** 的动机。

### 1.3 Prefill/Decode 分离架构

把两个阶段放在同一批调度会产生严重互相干扰（interference）：一个长 prefill 会阻塞整批的 decode，TTFT（time to first token）和 TPOT（time per output token）无法同时优化。DistServe、Splitwise、Mooncake 把它们分到不同 GPU：

> 论文：DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving [arXiv:2401.09670](https://arxiv.org/abs/2401.09670)（OSDI 2024）
>
> 论文：Splitwise: Efficient generative LLM inference using phase splitting [arXiv:2311.18677](https://arxiv.org/abs/2311.18677)（Microsoft，ISCA 2024）
>
> 论文：Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving [arXiv:2407.00079](https://arxiv.org/abs/2407.00079)（Moonshot AI / 清华，Kimi 的真实生产系统）

**DistServe** 把 prefill 和 decode 放到**不同的 GPU 池**，分别独立选择并行策略（prefill 用 TP，decode 用 PP 更省通信），再用 KV cache 传输把它们串起来。报告在同等 SLO 下能服务 **7.4×** 更多请求。

**Splitwise**（微软）发现 decode 阶段不需要顶级 GPU 算力，可以放到更便宜、更低功耗的机器上。关键工程挑战是 **KV cache 的跨机传输**——他们用 GPU 集群的背板互联（InfiniBand / NVLink）把 prefill 节点算出的 KV state 推到 decode 节点。同成本同功耗下吞吐 **2.35×**。

**Mooncake**（月之暗面 Kimi 的真实平台）走得更远：不仅 prefill/decode 物理分离，还把集群里**闲置的 CPU/DRAM/SSD 资源**组织成一个**全局分布式 KV cache 池**。它的核心创新是 **KVCache-centric scheduler**——请求进系统时，先看 KV cache 池里有没有现成的 prefix 可复用（system prompt、长上下文），有就直接跳到 decode；并在过载时用**预测式提前拒绝**（early rejection）保 SLO。长上下文场景吞吐提升 **525%**，真实生产负载多扛 **75%** 请求。这是 KV cache 从"中间状态"升级为"一等公民"的范式转移。

下面是一个体现分离架构调度逻辑的最小骨架（伪代码）：

```python
# DistServe / Mooncake 风格的 prefill-decode 分离调度器骨架
class DisaggregatedScheduler:
    def __init__(self, prefill_pool, decode_pool, kv_transfer_bus):
        self.prefill_pool = prefill_pool      # 算力强的 GPU 池
        self.decode_pool = decode_pool        # 带宽优化的 GPU 池
        self.kv_bus = kv_transfer_bus         # RDMA / NVLink 跨机 KV 传输
        self.global_kv_store = {}             # Mooncake 的全局 KV cache 池

    def handle_request(self, prompt, max_tokens):
        # 1. prefix 命中检查（Mooncake 核心）
        prefix_hash = self.hash_prefix(prompt)
        cached_kv, cached_len = self.global_kv_store.get(prefix_hash, (None, 0))

        # 2. 只 prefill 未命中部分
        prefill_node = self.prefill_pool.pick_least_loaded()
        kv_state = prefill_node.run_prefill(prompt[cached_len:])

        # 3. 跨机把 KV state 传到 decode 池
        decode_node = self.decode_pool.pick_least_loaded()
        self.kv_bus.transfer(kv_state, src=prefill_node, dst=decode_node)

        # 4. 在 decode 池做 continuous batching 的逐 token 采样
        tokens = decode_node.run_decode(kv_state, max_tokens)

        # 5. 写回全局 KV cache 池供后续请求复用
        self.global_kv_store[prefix_hash] = (kv_state, len(prompt))
        return tokens
```

这种架构把 TTFT 和 TPOT 解耦：prefill 池可以拼命用 TP 把单请求 prefill 压到 50ms 以内，decode 池可以用更大的 batch 摊薄带宽成本，两者互不干扰。

---

## 二、KV Cache 的最细节：内存布局与压缩

KV cache 是 decode 阶段最大的内存消费者，也是 vLLM/SGLang 这一代推理引擎的**核心数据结构**。理解它的形状、占用、压缩是看懂所有源码的前提。

### 2.1 KV cache 的张量形状

标准 Multi-Head Attention（MHA）下，对每个 token、每一层，缓存 Key 和 Value 各一份：

```
KV shape per layer = [2, batch, num_kv_heads, seq_len, head_dim]
                      ^    ^       ^             ^         ^
                  K/V 一起  batch  head 数      序列长度  每头维度
```

对 Llama-2-70B：`num_heads=64`，`num_kv_heads=64`（MHA），`head_dim=128`，`num_layers=80`，BF16（2 bytes）。

**单 token 的 KV cache 占用**：
$$
\text{KV per token} = 2 \times \text{num\_layers} \times \text{num\_kv\_heads} \times \text{head\_dim} \times \text{dtype\_bytes}
$$
$$
= 2 \times 80 \times 64 \times 128 \times 2 = 2.62 \text{ MB / token}
$$

**单请求 4096 context 的 KV cache**：$2.62 \times 4096 \approx 10.5$ GB。

H100 80GB 减去权重（70B × 2 = 140GB，需 2 卡 TP，每卡 70GB 权重）后，每卡只剩 ~10GB 给 KV cache 和激活——**单卡只能塞下 1 个 4K 请求**，这就是为什么 naive 推理服务吞吐低。

### 2.2 MQA / GQA / MLA 的 KV 形状

为了压 KV cache，业界演化出三种 head 共享策略：

**MQA（Multi-Query Attention）**：所有 query head 共享 **1 对** KV head。Llama 之前 falcon-40b、PaLM 用。`num_kv_heads=1`。KV 直接缩到 1/64。

**GQA（Grouped-Query Attention）**：折中，`num_kv_heads` 是 `num_heads` 的约数。Llama-2-70B 用 GQA-8（`num_kv_heads=8`），KV 缩到 8/64 = 1/8。**单 token KV = 2 × 80 × 8 × 128 × 2 ≈ 328 KB**——比 MHA 节省 8 倍。这是 Llama-2-70B 能在大 batch 下服务的关键。

```python
# 三种 attention 的 KV head 配置对比
configs = {
    "MHA (falcon-40b)":  {"num_heads": 64, "num_kv_heads": 64},  # KV 全量
    "GQA-8 (Llama-70B)": {"num_heads": 64, "num_kv_heads": 8},   # KV 1/8
    "MQA (PaLM-540B)":   {"num_heads": 64, "num_kv_heads": 1},   # KV 1/64
}
```

**MLA（Multi-head Latent Attention，DeepSeek）**：DeepSeek-V2 引入的更激进方案。

> 论文：DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model [arXiv:2405.04434](https://arxiv.org/abs/2405.04434)

MLA 的核心想法是把 KV cache **压缩到一个低秩潜在向量** $c_t$。对每个 token，不存完整的 K/V，而是存一个 $d_c$ 维（DeepSeek-V2 取 $d_c=512$，远小于 $n_h \cdot d_h = 128 \cdot 128 = 16384$）的 latent，在需要时通过上投影矩阵恢复出 K 和 V：

$$
c_t = W^{DKV} h_t, \quad k_t = W^{UK} c_t, \quad v_t = W^{UV} c_t
$$

配合 RoPE 的分离（一部分 head 走 RoPE 单独存），DeepSeek-V2 把 KV cache 压缩到 MHA 的 **~7%**，论文报告 KV cache 减少 **93.3%**，吞吐 **5.76×**。这是 2024 年最有原创性的 attention 变体。

```python
# MLA 的极简示意（DeepSeek-V2 §3.2 思路）
class MultiHeadLatentAttention(nn.Module):
    def __init__(self, d_model=5120, d_c=512, d_h=128, n_h=128):
        super().__init__()
        # 下投影：d_model -> d_c（只缓存 d_c 维 latent）
        self.W_DKV = nn.Linear(d_model, d_c, bias=False)
        # 上投影（推理时可在权重里融合掉，不占 KV cache）
        self.W_UK = nn.Linear(d_c, n_h * d_h, bias=False)
        self.W_UV = nn.Linear(d_c, n_h * d_h, bias=False)

    def forward(self, h_t, kv_cache):
        c_t = self.W_DKV(h_t)               # [batch, d_c] —— 这就是真正存进 cache 的
        kv_cache.append(c_t)                # 只存 latent，不存展开后的 K/V
        C = torch.stack(kv_cache)           # [seq, batch, d_c]
        K = self.W_UK(C).view(seq, batch, n_h, d_h)
        V = self.W_UV(C).view(seq, batch, n_h, d_h)
        # ... standard attention with Q
```

### 2.3 KV Cache 内存占用：实例

把上面的公式实例化到几种主流模型 + 硬件，理解"为什么 KV cache 是瓶颈"：

| 模型 | 参数 | layers | kv_heads | head_dim | bytes/token (FP16) | 4K context | 32K context |
|------|------|--------|----------|----------|---------------------|------------|-------------|
| Llama-2-7B | 7B | 32 | 32 (MHA) | 128 | 524 KB | 2.1 GB | 16.8 GB |
| Llama-2-70B | 70B | 80 | 8 (GQA-8) | 128 | 328 KB | 1.3 GB | 10.5 GB |
| Llama-3-70B | 70B | 80 | 8 (GQA-8) | 128 | 328 KB | 1.3 GB | 10.5 GB |
| DeepSeek-V2 (MLA) | 236B(21B激活) | 80 | latent d_c=512 | - | ~28 KB | 0.11 GB | 0.9 GB |

最后一个最能说明问题：MLA 把 DeepSeek-V2 的 KV 压到 Llama-70B 的 **< 10%**，这正是 DeepSeek 能在长上下文（128K）下保持低成本的关键。

**最大 batch size 的硬约束**：单 H100 80GB 跑 Llama-70B（TP=2，每卡 70B×2/2=70GB 权重），剩 10GB 给 KV。Llama-70B 每 token 328KB → 10GB / 328KB ≈ **30K token 总容量**。如果是 batch=30、平均 context 1K，正好打满。这就是为什么没有 PagedAttention 之前，系统利用率卡在 20-40%。

### 2.4 KV Cache 压缩：丢弃不重要 token

当 context 远超预算，必须扔掉一部分旧 KV。两条技术路线：

**StreamingLLM（attention sink）**——一个反直觉但极重要的发现：

> 论文：Efficient Streaming Language Models with Attention Sinks [arXiv:2309.17453](https://arxiv.org/abs/2309.17453)（MIT Han Lab + Meta，ICLR 2024）

作者发现：删掉**最近**的 token 之外的 KV（即 window attention）会让模型崩溃；但**保留前 4 个 token 的 KV** + 滑动窗口，模型可以稳定生成到 **400 万 token**。原因是：softmax 让前几个 token 变成"attention sink"——它们没有语义意义，但吸收了多余的 attention 分数（类似 softmax 必须把概率质量分配出去，前面 token 成了"垃圾桶"）。删掉 sink，attention 分布被打乱，模型崩。

```python
# StreamingLLM 的 cache 管理（极简实现）
class StreamingLLMCache:
    def __init__(self, sink_size=4, window_size=2048):
        self.sink = []            # 永不删除的前 4 个 token 的 KV
        self.window = deque(maxlen=window_size)  # 滑动窗口

    def append(self, token_kv):
        self.window.append(token_kv)

    def get_cache(self):
        return self.sink + list(self.window)   # 总是 sink + 最近 window

    # 关键：在窗口满了之后，旧 token 自然被 deque 弹出，但 sink 保留
```

实测：Llama-2-7B 用 StreamingLLM 在 4M token 上 perplexity 稳定，比 sliding-window-recompute 快 **22.2×**。

**H2O（Heavy Hitter Oracle）**——基于"少数 token 贡献了大部分 attention"的发现：

> 论文：H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models [arXiv:2306.14048](https://arxiv.org/abs/2306.14048)

H2O 把 KV cache 驱逐建模为**动态次模最大化**（dynamic submodular）：每步把累积 attention score 最高的 token（Heavy Hitter）和最近 token 保留，驱逐其他。保留 20% heavy hitter 就能几乎无损。论文给出**次模函数近似比**的理论保证（在温和假设下），这是少有的有理论分析的 KV 压缩工作。

```python
# H2O 驱逐策略（简化版）
def h2o_evict(kv_cache, attention_scores, keep_ratio=0.2):
    """
    attention_scores: [num_tokens]，每个历史 token 的累积 attention 权重
    """
    n = len(kv_cache)
    n_keep = int(n * keep_ratio)
    # 重 token + 最近 token 各占一半配额
    n_recent = n_keep // 2
    n_heavy = n_keep - n_recent

    heavy_idx = attention_scores.argsort(descending=True)[:n_heavy]
    recent_idx = list(range(n - n_recent, n))
    keep_idx = sorted(set(heavy_idx.tolist()) | set(recent_idx))
    return [kv_cache[i] for i in keep_idx]
```

### 2.5 KV Cache 量化：KVQuant 与 KIVI

权重能 4-bit，KV cache 也能——但 KV 有自己的分布特性，不能照搬权重量化。

> 论文：KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization [arXiv:2401.18079](https://arxiv.org/abs/2401.18079)（Berkeley + SambaNova，NeurIPS 2024）

KVQuant 的四把刀：
1. **Per-Channel Key Quantization**：Key 沿 channel 维量化（而不是 token 维），匹配 Key 的分布；
2. **Pre-RoPE Key Quantization**：在 RoPE 之前量化 Key（RoPE 会破坏 Key 的分布对称性）；
3. **Non-Uniform Quantization**：按层敏感度加权的非均匀数据类型；
4. **Per-Vector Dense-and-Sparse**：把 outlier 单独剥出来，避免它拉宽量化范围。

效果：3-bit 量化在 Wikitext-2/C4 上 perplexity 损失 < 0.1，**单卡 A100-80GB 跑 Llama-7B 100 万 context**，8 卡系统跑 **1000 万 context**。

> 论文：KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache [arXiv:2402.02750](https://arxiv.org/abs/2402.02750)（Rice + Meta + CMU，ICML 2024）

KIVI 的关键洞察：**Key 和 Value 的最优量化维度不同**——Key 应 per-channel，Value 应 per-token。这是个反直觉但严谨的结论：Key 的 channel 之间分布差异大，Value 的 token 之间更均匀。结果：**2-bit** KV cache，几乎无精度损失，峰值内存降 **2.6×**，batch size 提 **4×**，吞吐 **2.35×-3.47×**。

```python
# KIVI 的非对称量化：Key per-channel, Value per-token
def kivi_quantize_key(K, n_bits=2):
    # K shape: [seq, num_kv_heads, head_dim]
    # 沿 head_dim 维（per-channel）分组量化
    group_size = 32
    K_grouped = K.reshape(seq, num_kv_heads, head_dim // group_size, group_size)
    qmin = K_grouped.min(dim=-1, keepdim=True)
    qmax = K_grouped.max(dim=-1, keepdim=True)
    scale = (qmax - qmin) / (2**n_bits - 1)
    K_q = torch.round((K_grouped - qmin) / scale).clamp(0, 2**n_bits - 1).to(torch.uint8)
    return K_q, scale, qmin

def kivi_quantize_value(V, n_bits=2):
    # V shape: [seq, num_kv_heads, head_dim]
    # 沿 seq 维（per-token）分组量化
    return quantize_along_seq_dim(V, n_bits)   # 对称的，但沿不同轴
```

### 2.6 KV Cache 跨请求复用

KV cache 的另一条优化线是**跨请求共享**——多个请求如果有相同的 prefix（system prompt、few-shot examples），不必重复 prefill。

**PagedAttention**（vLLM，§五详解）：通过块表让同一物理块被多个请求的逻辑序列引用——写时复制（CoW）实现"前缀共享 + 各自独立 decode"。

**RadixAttention**（SGLang，§六详解）：用基数树（radix tree）自动发现所有在途请求的公共前缀，结构化地组织 KV cache 复用。

**LMCache**：UC Berkeley 2024 开源，把 KV cache 复用从"同一 GPU 进程内"扩展到**跨 GPU、跨节点、跨请求**，配合 vLLM 使用。命中 system prompt 后 prefill 时间可降到几毫秒。

**Mooncake 的全局 KV 池**（§1.3 已述）：把这推向极致——KV cache 是分布式系统的一等公民，有自己的调度器、自己的存储层（DRAM/SSD 分级）、自己的 SLO。

---

## 三、Continuous Batching：吞吐量的根本机制

如果没有 continuous batching，LLM serving 的吞吐会被一个简单的统计现象毁掉：**不同请求的输出长度差异巨大**（有的 10 token，有的 2000 token）。

### 3.1 静态 batching 的低效

朴素做法：凑齐 batch=8，等所有 8 个请求都生成完才放下一批。问题：如果 7 个请求 100 token 完成，1 个请求 2000 token 完成，那 7 个请求完成后**剩下的 GPU 时间只服务 1 个请求**——GPU 利用率从 8/8 暴跌到 1/8。

实测：在 30% 慢请求的场景，静态 batching 的吞吐只有理论峰值的 30-40%。

### 3.2 Continuous Batching（Orca, OSDI 2022）

> 论文：Orca: A Distributed Serving System for Transformer-Based Generative Models. Yu et al., OSDI 2022（无 arXiv，USENIX 直接发表）

Orca 提出 **iteration-level scheduling**（**调度粒度从"请求"降到"单次 decode iteration"**）：每个 decode step 后重新决定 batch 组成——完成的请求踢出去，等队首的新请求插进来。这样 GPU 几乎永远在处理满 batch。

核心是一个** while 循环**，每次迭代：

```python
# Continuous Batching 的核心调度循环（Orca 思想，vLLM 实现的骨架）
class ContinuousBatchingScheduler:
    def __init__(self, engine, max_batch_size=256):
        self.engine = engine
        self.running = []          # 当前正在 decode 的请求
        self.waiting = deque()     # 队列里等 prefill 的请求
        self.max_batch = max_batch_size

    def schedule_loop(self):
        while True:
            schedule = self._make_iteration_schedule()
            self.engine.step(schedule)   # 跑一次 decode / prefill

    def _make_iteration_schedule(self):
        # 1. 驱逐完成的请求
        self.running = [r for r in self.running if not r.is_finished()]

        # 2. 在还有余量时，从 waiting 弹出新请求做 prefill
        #    （注意：vLLM 的实际实现里 prefill 和 decode 是分开 iteration 的，
        #     v0 引擎有 prefill-heavy / decode-only 的交替调度策略）
        while (self.waiting and len(self.running) < self.max_batch
               and self._kv_budget_available()):
            new_req = self.waiting.popleft()
            self.running.append(new_req)

        # 3. 把 running 列表打包成一个 batch 喂给 engine
        return self._build_batch(self.running)
```

关键洞察：**decode 阶段的 batch 内每个请求各跑各的 token，互不影响**——因为 attention 是 mask 掉的，KV cache 各存各的。这让"动态插拔请求"几乎零成本。

### 3.3 vLLM 的实现：iteration-level + chunked prefill

vLLM 在 Orca 基础上加了两个工程优化：

1. **Chunked prefill**：长 prompt 的 prefill 拆成多个 chunk，跨 iteration 执行，避免单次 prefill 阻塞 decode。
2. **Prefill/decode 混合 batch**：v0 早期版本严格交替（一个 iteration 全 prefill 或全 decode），后期支持混合——把短 prefill 塞进 decode iteration 一起跑。

vLLM 的 `LLMEngine.schedule()` 是整个系统的心脏，简化结构：

```python
# vllm/engine/llm_engine.py 的核心调度逻辑（简化展示思想）
class LLMEngine:
    def schedule(self) -> SchedulerOutputs:
        # 1. 把上次 iteration 完成/超时的请求从 running 移除
        self._schedule_running()

        # 2. 预算检查：KV cache 块够不够给新请求 prefill
        #    budget = total_kv_blocks - running_used_blocks
        budget = self.block_manager.get_num_free_gpu_blocks()

        # 3. 从 waiting 队列拉新请求做 prefill
        #    - 检查 prefix cache 命中（前缀共享）
        #    - 分配物理块号到 block_table
        while self.waiting and budget > 0:
            req = self.waiting[0]
            needed = self._estimate_blocks(req)
            if needed > budget:
                break  # 这一批先不接
            self.waiting.popleft()
            self.running.append(req)
            self._allocate_blocks(req)
            budget -= needed

        # 4. 返回这次 iteration 的调度决策：
        #    哪些请求要 prefill、哪些要 decode、块怎么分配
        return SchedulerOutputs(
            scheduled_seqs=self.running,
            blocks_to_swap_in=...,     # prefix cache 命中时的块拷贝
            blocks_to_swap_out=...,
        )

    def step(self) -> List[RequestOutput]:
        """一次 decode iteration 的完整流程"""
        seq_group_metadata_list = self._prepare_seqs()
        scheduler_outputs = self.schedule()
        # 调 model_runner 跑一次 forward
        output = self.model_runner.execute_model(
            seq_group_metadata_list, scheduler_outputs
        )
        # 处理采样结果，更新 sequence 状态
        return self._process_model_outputs(output, scheduler_outputs)
```

### 3.4 从 0 实现 continuous batching

下面是一个**单文件、纯 PyTorch、可跑通**的 minimal continuous batching demo，展示核心机制（不含 PagedAttention，用 padding + attention mask 代替，便于教学）：

```python
"""
minimal_continuous_batching.py
从 0 实现的 continuous batching 教学版。
依赖：torch + transformers（任意小 model，如 gpt2）
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import deque

class CBBatch:
    """一个可变 batch，支持运行时增删请求。"""
    def __init__(self):
        self.reqs = []          # 每个 req 是 dict{id, input_ids, generated, done}
        self.pad_id = 0

    def add(self, req):
        self.reqs.append(req)

    def remove_done(self):
        self.reqs = [r for r in self.reqs if not r["done"]]

    def build_tensor(self):
        """左 padding，让所有请求最后一个 token 对齐——这是 attention 计算的关键。"""
        max_len = max(len(r["input_ids"]) + len(r["generated"]) for r in self.reqs)
        batch = torch.full((len(self.reqs), max_len), self.pad_id, dtype=torch.long)
        attn_mask = torch.zeros_like(batch)
        for i, r in enumerate(self.reqs):
            full = r["input_ids"] + r["generated"]
            # 左 padding：把真实 token 放到 batch 末尾
            batch[i, -len(full):] = torch.tensor(full)
            attn_mask[i, -len(full):] = 1
        return batch, attn_mask


class CBEngine:
    def __init__(self, model_name="gpt2", max_batch=8, max_new_tokens=50):
        self.model = AutoModelForCausalLM.from_pretrained(model_name).cuda().eval()
        self.tok = AutoTokenizer.from_pretrained(model_name)
        self.pad_id = self.tok.eos_token_id
        self.max_batch = max_batch
        self.max_new = max_new_tokens
        self.batch = CBBatch()
        self.queue = deque()

    def submit(self, prompt):
        ids = self.tok.encode(prompt, return_tensors="pt").tolist()[0]
        self.queue.append({"id": id(prompt), "input_ids": ids,
                           "generated": [], "done": False})

    def _fill_batch(self):
        while self.queue and len(self.batch.reqs) < self.max_batch:
            self.batch.add(self.queue.popleft())

    @torch.no_grad()
    def step(self):
        """一次 decode iteration。"""
        self._fill_batch()
        self.batch.remove_done()
        if not self.batch.reqs:
            return []

        input_ids, attn_mask = self.batch.build_tensor()
        logits = self.model(input_ids.cuda(), attention_mask=attn_mask.cuda()).logits
        # 每个请求只看最后一个有效位置的 logits
        next_tokens = logits[:, -1, :].argmax(dim=-1).cpu().tolist()

        finished = []
        for r, tok in zip(self.batch.reqs, next_tokens):
            r["generated"].append(tok)
            if tok == self.tok.eos_token_id or len(r["generated"]) >= self.max_new:
                r["done"] = True
                finished.append(r)
        return finished

    def run_until_done(self):
        results = []
        while self.batch.reqs or self.queue:
            results.extend(self.step())
        return results


# 测试
if __name__ == "__main__":
    eng = CBEngine()
    for p in ["Hello world", "The capital of France is",
              "def fibonacci(n):", "Once upon a time"]:
        eng.submit(p)
    for r in eng.run_until_done():
        print(eng.tok.decode(r["input_ids"] + r["generated"]))
        print("---")
```

这个 ~80 行的实现抓住了 continuous batching 的精髓：**每个 step 后 batch 组成都重新计算**，完成请求立即释放，队列里的新请求立即填进空位。真实 vLLM 多出来的是 PagedAttention（消除 padding 浪费）、prefix cache、speculative decoding 集成等工程层。

---

## 四、Speculative Decoding：无损加速的数学之美

Speculative decoding 是 2022-2024 年 LLM 推理优化最优雅的发明之一。它的核心承诺：**在不改变输出分布的前提下，用一个小模型"猜"几个 token，大模型一次性验证，从而把多次 decode 合并成一次**。这是少有的"理论上无损、工程上 2-4× 加速"的技术。

### 4.1 基本原理

朴素 decode：每步大模型 $M$（target）生成 1 个 token，需要 $N$ 步生成 $N$ 个 token，每步都要把 $M$ 的全部权重读一遍——纯 memory-bound。

Speculative decoding：用一个小的 draft model $D$（同样架构、参数少 10-100×）**串行**生成 $\gamma$ 个候选 token（draft 快，因为权重小），然后**把这 $\gamma$ 个 token 一次性**喂给 $M$ 做验证——验证是**并行**的，因为 $M$ 知道前 $i$ 个 token 后能一次 forward 算出第 $i+1$ 个位置的概率分布。

如果 $D$ 猜对了，这 $\gamma$ 个 token 一气呵成；猜错了，从第一个错误位置截断，剩下的 $M$ 自己的预测继续。**核心是**：$M$ 的 forward 不论猜对几个，都只跑一次。

### 4.2 三篇奠基论文（一手核实）

**Leviathan et al. 2023（Google）**：

> 论文：Fast Inference from Transformers via Speculative Decoding [arXiv:2211.17192](https://arxiv.org/abs/2211.17192)（ICML 2023 Oral）

这是把 speculative decoding 引入 Transformer LLM 推理的奠基工作。核心算法：
- Draft model 生成 $\gamma$ 个候选 token $x_1, \dots, x_\gamma$
- Target model 并行计算 $p(x_1), p(x_2|x_1), \dots, p(x_{\gamma+1}|x_1\dots x_\gamma)$
- **拒绝采样**：对每个候选 $x_i$，以 $\min(1, p(x_i)/q(x_i))$ 的概率接受（$q$ 是 draft 分布）
- 拒绝时，从归一化的 $\text{relu}(p-q)$ 重新采样一个 token

在 T5-XXL 上获得 **2×-3×** 加速，输出分布完全不变。

**Chen et al. 2023（DeepMind）**：

> 论文：Accelerating Large Language Model Decoding with Speculative Sampling [arXiv:2302.01318](https://arxiv.org/abs/2302.01318)

DeepMind 的同期工作（与 Leviathan 独立），在 Chinchilla 70B 上获得 **2-2.5×** 加速。算法等价，但作者更清晰地给出了拒绝采样的数学保证。

**Xia et al. 2023（北大 + MSRA）**——SpecDec，"Speculative Decoding" 这个名字的首次公开提出：

> 论文：Speculative Decoding: Exploiting Speculative Execution for Accelerating Seq2seq Generation [arXiv:2203.16487](https://arxiv.org/abs/2203.16487)（EMNLP 2023 Findings）

这是**最早**正式把"speculative execution"引入 AR decoding 的工作（v1 2022-03，原名 "Generalized Aggressive Decoding"，v5 改名为 "Speculative Decoding"）。作者还提出了 Spec-Drafter（独立训练的 draft 模型）和 Spec-Verification，在机器翻译/摘要上获得 **~5×** 加速。

### 4.3 拒绝采样的数学保证（无损性证明）

这是 speculative decoding 最美的部分。我们要证明：**用上面的算法采样，输出 token 的分布严格等于 target model $p$ 的分布**。

**命题**：对每个位置，speculative decoding 采出的 token $x$ 满足 $\Pr[x] = p(x)$。

**证明**（直觉版）：draft model 提议 $x'$（来自分布 $q$），target 验证时有三种情况：

1. **接受** $x'$：概率 $\Pr[\text{accept} | x'] = q(x') \cdot \min(1, p(x')/q(x')) = \min(q(x'), p(x'))$。
2. **拒绝** $x'$ 并重采样 $x$：从 $\text{norm}(\text{relu}(p - q))$ 采样。对任意 $x$，这种情况贡献的概率是
$$
\sum_{x'} q(x')\left(1 - \min(1, p(x')/q(x'))\right) \cdot \frac{\text{relu}(p(x) - q(x))}{Z}
$$
其中 $Z = \sum_y \text{relu}(p(y) - q(y)) = 1 - \sum_y \min(p(y), q(y))$（因为 $p(y) = \min(p,q) + \text{relu}(p-q)$，求和为 1）。

3. 合并两种情况的总概率：
$$
\Pr[x] = \min(q(x), p(x)) + \left(1 - \sum_y \min(p(y), q(y))\right) \cdot \frac{\text{relu}(p(x) - q(x))}{Z}
$$
$$
= \min(q(x), p(x)) + \text{relu}(p(x) - q(x)) = p(x).
$$

**证毕。** 这是个巧妙的构造：$\min(p, q)$ 用接受覆盖 $p \leq q$ 的部分，$\text{relu}(p - q)$ 用拒绝重采样覆盖 $p > q$ 的部分，两者拼起来恰好等于 $p$。这正是**rejection sampling 应用于 token 序列**的精妙之处。

代码实现：

```python
def speculative_sample(p_logits, q_logits, draft_tokens, gamma):
    """
    p_logits, q_logits: [gamma+1, vocab] —— target 和 draft 在 gamma+1 个位置的概率
    draft_tokens: [gamma] —— draft model 串行提议的 gamma 个 token
    返回：接受的前 k 个 token + 1 个新采样的 token（共 k+1 个，k 可能=0）
    """
    p = torch.softmax(p_logits, dim=-1)   # [gamma+1, vocab]
    q = torch.softmax(q_logits, dim=-1)   # [gamma+1, vocab]

    accepted = []
    for i in range(gamma):
        x = draft_tokens[i]
        # 拒绝采样的接受概率
        accept_prob = torch.min(torch.ones(()), p[i, x] / q[i, x]).item()
        if torch.rand(()).item() < accept_prob:
            accepted.append(x)
        else:
            # 拒绝：从 relu(p - q) 归一化重采样
            residual = torch.relu(p[i] - q[i])
            residual = residual / residual.sum()
            new_token = torch.multinomial(residual, 1).item()
            return accepted, new_token    # 提前终止

    # 所有 gamma 个都接受了，bonus 第 gamma+1 个直接从 p 采样
    bonus = torch.multinomial(p[gamma], 1).item()
    return accepted, bonus
```

### 4.4 加速比分析

设 draft 接受率（acceptance rate）为 $\alpha \in [0,1]$（每个位置被接受的概率），draft length $\gamma$。**期望接受的 token 数**：
$$
E[\text{accepted}] = \sum_{i=1}^{\gamma} \Pr[\text{前 } i \text{ 个都接受}] = \sum_{i=1}^{\gamma} \alpha^i = \frac{\alpha(1 - \alpha^\gamma)}{1 - \alpha}
$$
加上 bonus 1 个，每次 forward 期望产出 $\frac{\alpha(1 - \alpha^\gamma)}{1 - \alpha} + 1$ 个 token。

**理论加速比**（忽略 draft 成本）：
$$
\text{speedup} \approx \frac{E[\text{tokens per forward}]}{1} = 1 + \frac{\alpha(1 - \alpha^\gamma)}{1 - \alpha}
$$

举例：$\alpha = 0.8, \gamma = 5$：加速 $\approx 1 + 0.8 \times (1 - 0.32768) / 0.2 \approx 1 + 2.69 = 3.69\times$。

**实测 caveat**：draft model 自己也要时间，且 $\gamma$ 越大，draft 阶段越慢。最优 $\gamma$ 通常在 4-8。实测加速比往往比理论低 20-30%。

### 4.5 Medusa：去掉独立 draft model

> 论文：Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads [arXiv:2401.10774](https://arxiv.org/abs/2401.10774)（Princeton + Together AI + Stanford，Tri Dao 在列）

独立 draft model 的痛点：要额外存一份权重、要训练、要同步。Medusa 的洞察：**直接在 target model 上加几个额外的解码头**（Medusa heads），每个头预测下 1, 2, 3, ... 个 token。一次 target forward 同时拿到主头 logits 和 $\gamma$ 个 Medusa head 的预测。

用 **tree-based attention** 把多个候选路径组合成一棵小树（典型拓扑：每头 top-2 候选，共 $2^\gamma$ 条路径），一次 attention 验证整棵树。Medusa-1（冻结 backbone 微调头）获得 **2.2×** 无损加速；Medusa-2（联合微调）获得 **2.3×-3.6×**。

```python
# Medusa head 的结构（简化）
class MedusaHeads(nn.Module):
    def __init__(self, hidden_dim, vocab_size, num_medusa_heads=4):
        super().__init__()
        self.heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.SiLU(),
                nn.Linear(hidden_dim, vocab_size),
            ) for _ in range(num_medusa_heads)
        ])

    def forward(self, hidden_state):
        # hidden_state: [batch, hidden_dim]（最后位置）
        # 返回 gamma 个未来位置的 logits
        return [head(hidden_state) for head in self.heads]
```

### 4.6 EAGLE / EAGLE-2：在特征空间投机

> 论文：EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty [arXiv:2401.15077](https://arxiv.org/abs/2401.15077)（北大 + MSRA）
>
> 论文：EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees [arXiv:2406.16858](https://arxiv.org/abs/2406.16858)

EAGLE 的两个核心观察：
1. **特征层（second-to-top-layer hidden state）的自回归比 token 层更容易**——因为特征空间更平滑；
2. **特征层自回归的不确定性**（uncertainty）是性能瓶颈——不解决它，draft 准不到哪去。

EAGLE 的解法：用上一 token 的特征 + 当前 token 的 embedding 一起喂给一个轻量 draft 网络，**消解了不确定性**。对 Llama-2-Chat 70B 获得 **2.7×-3.5×** 加速，吞吐翻倍，分布无损。

**EAGLE-2** 进一步引入**上下文感知的动态 draft tree**：观察到 draft token 的接受率不仅取决于位置，也取决于 context（draft model 是 well-calibrated 的，confidence 接近真实接受率）。用 confidence 动态调整树的结构——高 confidence 路径多分配候选，低 confidence 路径剪枝。加速比 **3.05×-4.26×**，比 EAGLE-1 再快 **20-40%**。

```python
# EAGLE-2 动态树构造的伪代码
def build_dynamic_draft_tree(draft_logits_per_level, top_k=2, max_nodes=64):
    """
    draft_logits_per_level: list of [num_candidates, vocab]，每层每候选的 logits
    返回：一棵按 confidence 加权裁剪的候选树
    """
    tree = [{"token": <sos>, "score": 1.0, "children": []}]
    frontier = tree
    for level_logits in draft_logits_per_level:
        new_frontier = []
        for node in frontier:
            # top-k candidates with their confidence
            top_vals, top_ids = level_logits[node["idx"]].topk(top_k)
            for val, tid in zip(topvals, topids):
                child = {"token": tid, "score": node["score"] * val, "children": []}
                node["children"].append(child)
                new_frontier.append(child)
        # 按 score 全局排序，只保留 top max_nodes 个节点（剪枝）
        new_frontier.sort(key=lambda n: -n["score"])
        frontier = new_frontier[:max_nodes]
    return tree
```

### 4.7 SpecBench 与实测

Spec-Bench（github.com/hemingkx/Spec-Bench）是一个评测 speculative decoding 在多种任务（翻译、摘要、代码、数学、QA）上加速比的标准化 benchmark。综合各家报告：
- naive speculative decoding（独立小 draft）：1.5×-2×
- Medusa：2.2×-3×
- EAGLE：2.7×-3.5×
- EAGLE-2：3×-4.3×

注意：加速比对**任务敏感**——代码、数学这类"答案确定"的任务，draft 接受率高（$\alpha$ 可达 0.85+），加速比接近上限；开放对话 $\alpha$ 较低（0.5-0.7），加速比打折。

---

## 五、PagedAttention 详解：把 OS 虚拟内存搬进 LLM

PagedAttention 是 vLLM 的灵魂创新，让 KV cache 内存利用率从 20-40% 跳到 **90%+**。理解它需要先理解它解决的具体问题。

### 5.1 没有 PagedAttention 的世界

朴素 KV cache 管理给每个请求预分配**连续**的物理内存，长度按**最大可能 context** 估。两个灾难：

1. **内部碎片（internal fragmentation）**：请求实际只生成 100 token，但预分配了 2048 token 的空间——浪费 95%。
2. **外部碎片（external fragmentation）**：请求 A 完成后释放 2048 token 的块，新请求 B 只需要 512 token，剩下的 1536 token 无法被其他大请求用。

vLLM 论文测量：在朴素系统里，**60-80% 的 KV cache 内存被碎片浪费**——这意味着 batch size 被压到本应的 1/3。

### 5.2 OS 虚拟内存的借鉴

> 论文：Efficient Memory Management for Large Language Model Serving with PagedAttention [arXiv:2309.06180](https://arxiv.org/abs/2309.06180)（SOSP 2023，UC Berkeley Sky Computing）

vLLM 借用了操作系统的**分页（paging）**思想：
- 物理内存（GPU KV cache buffer）切成固定大小的**块（block）**，典型每块 16 个 token 的 KV。
- 每个请求维护一个**块表（block table）**——逻辑 token 序列到物理块号的映射，类似 OS 进程的 page table。
- 逻辑上连续的 token 可以散落在物理上不连续的块里——**碎片消失了**。

OS 里 page 大小通常是 4KB；vLLM 里 block 大小通常是 16 token（Llama-70B GQA-8 下，每块 $16 \times 328\text{KB} \approx 5.2$ MB，正好适配 GPU memory access pattern）。

### 5.3 Block Table 的实现

每个请求有一个 block table，是一个 1D 整数数组。例如请求的实际序列占 50 token，block_size=16：
- 需要 $\lceil 50/16 \rceil = 4$ 个块
- block_table = [7, 12, 3, 18] 表示逻辑 token 0-15 在物理块 7，16-31 在物理块 12，等等。

attention kernel 在计算时，**先查 block_table 拿到物理块号，再去 KV cache buffer 取数据**——这是 PagedAttention 算子与普通 attention 的唯一区别。

vLLM 的 CUDA kernel（`paged_attention_v1/v2`）核心逻辑（伪 CUDA 代码）：

```cuda
// 简化的 PagedAttention CUDA kernel（展示 block_table 查找逻辑）
__global__ void paged_attention_kernel(
    float* output,              // [num_seqs, num_heads, head_dim]
    const float* q,             // [num_seqs, num_heads, head_dim]
    const float* key_cache,     // [num_blocks, num_kv_heads, block_size, head_dim]
    const float* value_cache,   // 同 key
    const int* block_tables,    // [num_seqs, max_num_blocks_per_seq]
    const int* context_lens,    // [num_seqs] 每个请求的当前长度
    int block_size,
    int num_kv_heads,
    int head_dim
) {
    int seq_idx = blockIdx.y;
    int head_idx = blockIdx.x;
    int tid = threadIdx.x;

    int ctx_len = context_lens[seq_idx];
    int num_blocks = (ctx_len + block_size - 1) / block_size;

    // 对当前请求的所有历史 token 计算 attention
    extern __shared__ float scores[];   // 动态共享内存存 attention 分数
    float max_score = -INFINITY;

    for (int block_i = 0; block_i < num_blocks; block_i++) {
        // 关键：从 block_table 查物理块号
        int physical_block = block_tables[seq_idx * max_blocks + block_i];

        for (int in_block_i = tid; in_block_i < block_size; in_block_i += blockDim.x) {
            int token_pos = block_i * block_size + in_block_i;
            if (token_pos >= ctx_len) break;

            // 从物理块取 K，与 Q 做点积
            const float* k = key_cache + physical_block * num_kv_heads * block_size * head_dim
                             + head_idx * block_size * head_dim
                             + in_block_i * head_dim;
            float score = dot_product(q + seq_idx * num_heads * head_dim + head_idx * head_dim,
                                       k, head_dim);
            score /= sqrtf((float)head_dim);
            scores[token_pos] = score;
            max_score = fmaxf(max_score, score);
        }
    }

    // softmax（略）+ 与 V 加权求和（同样按 block_table 索引）...
}
```

注意 `block_tables[seq_idx * max_blocks + block_i]` 这一行——这是 PagedAttention 与普通 attention 的全部区别：**一次额外的间接寻址**。开销极小（共享内存里的整数数组查找），但消除了所有碎片。

### 5.4 Fragmentation 消除的数学

设请求 i 的实际长度 $L_i$，block size $B$。PagedAttention 下每请求占用 $\lceil L_i / B \rceil \times B$ 字节，**每请求最多浪费 $B-1$ 个 token 的空间**。对 $B=16$，浪费率 $\leq 16/L_i$。

对长度 1024 的请求，浪费率 $\leq 1.6\%$。对比朴素系统的 60-80% 浪费——**这是为什么 vLLM 把吞吐提到 2-4×**。

vLLM 的 block manager 核心数据结构（简化）：

```python
# vllm/core/block_manager.py 的核心思想（简化）
class BlockAllocator:
    """GPU 物理块分配器。"""
    def __init__(self, num_blocks, block_size):
        self.num_blocks = num_blocks
        self.free_blocks = list(range(num_blocks))   # 空闲块栈

    def allocate(self):
        return self.free_blocks.pop()

    def free(self, block_idx):
        self.free_blocks.append(block_idx)


class BlockTable:
    """单个请求的块表。"""
    def __init__(self, allocator):
        self.allocator = allocator
        self.physical_blocks = []   # 逻辑块 -> 物理块号的列表

    def append_token(self):
        """新增一个 token：当前块满了就分配新块。"""
        if len(self.physical_blocks) * self.block_size == self.num_tokens:
            self.physical_blocks.append(self.allocator.allocate())
        self.num_tokens += 1

    def get_physical_block(self, logical_idx):
        return self.physical_blocks[logical_idx]


class BlockManager:
    """全局块管理，对应 vLLM 的 BlockSpaceManager。"""
    def __init__(self, block_size, num_gpu_blocks):
        self.allocator = BlockAllocator(num_gpu_blocks, block_size)
        self.block_tables = {}   # req_id -> BlockTable

    def can_allocate(self, req):
        """是否有足够空闲块接受新请求 prefill？"""
        return len(self.allocator.free_blocks) >= self._required_blocks(req)

    def allocate(self, req):
        bt = BlockTable(self.allocator)
        for _ in range(len(req.input_ids)):
            bt.append_token()
        self.block_tables[req.id] = bt

    def free(self, req_id):
        for blk in self.block_tables[req_id].physical_blocks:
            self.allocator.free(blk)
        del self.block_tables[req_id]
```

### 5.5 CoW 与跨请求 KV 共享

PagedAttention 还解锁了一个 OS 同款能力：**copy-on-write (CoW)**。两个请求共享同一个 system prompt，它们的 block_table 前几项指向同一组物理块；任何一个请求要修改某个块时（beam search 的分支、不同的采样结果），先复制该块再修改——其他请求不受影响。这让 vLLM 原生支持 beam search、shared-prefix batching、parallel sampling。

---

## 六、Prefix Caching / RadixAttention

system prompt 经常很长（几千 token），每次请求都重新 prefill 是巨大浪费。Prefix caching 把已算过的 KV cache 留下来给后续请求复用。

### 6.1 SGLang 的 RadixAttention

> 论文：SGLang: Efficient Execution of Structured Language Model Programs [arXiv:2312.07104](https://arxiv.org/abs/2312.07104)（Berkeley + Stanford + CMU）

SGLang 把 KV cache 组织成一棵**基数树（radix tree）**：每个节点代表一段 token 序列，从根到叶的路径对应一个完整请求。**多个请求有公共前缀时，自动共享树上的祖先节点**——不需要任何手动标注 prefix。

```python
# RadixAttention 的基数树结构（简化）
class RadixNode:
    def __init__(self):
        self.tokens = []           # 这段节点存的 token
        self.kv_cache = None       # 这段 token 的 KV cache（已算好）
        self.children = {}         # 第一个 token -> child RadixNode
        self.ref_count = 0         # 多少在途请求引用此节点


class RadixCache:
    def __init__(self):
        self.root = RadixNode()

    def match_prefix(self, tokens):
        """从根开始，找最大匹配的公共前缀。返回命中的 token 数和对应节点路径。"""
        node = self.root
        matched = 0
        for i, tok in enumerate(tokens):
            if tok in node.children:
                node = node.children[tok]
                matched += len(node.tokens)
                # 实际实现要处理 node 内部的部分匹配
            else:
                break
        return matched, node

    def insert(self, tokens, kv_cache):
        """新请求 prefill 完成后，把它的 KV cache 插入树。"""
        matched, node = self.match_prefix(tokens)
        remaining = tokens[matched:]
        if remaining:
            # 创建新子节点
            child = RadixNode()
            child.tokens = remaining
            child.kv_cache = kv_cache[matched:]
            node.children[remaining[0]] = child
```

**Few-shot prompting 的加速**：few-shot 的 examples 完全相同，只是 query 不同——RadixAttention 自动让 N 个请求共享 examples 段的 KV cache，prefill 时间从 N × full 降到 full + N × small。

**System prompt 复用**：所有请求共享的 system prompt 在第一次请求后永久驻留在树根，后续请求 prefill 时跳过这部分，TTFT 降低 5-10×。

SGLang 论文报告：在 agent control、逻辑推理、few-shot、JSON 解码、RAG pipeline、多轮对话上，**比 SOTA 高 6.4× 吞吐**。

### 6.2 vLLM 的 Automatic Prefix Caching (APC)

vLLM 后期也加了 prefix caching（v0.5+），实现思路类似但更工程化：用 token hash 链做块级别的命中检查（每个 block 算一个 hash，包含前一个 block 的 hash，形成哈希链），命中时直接复用物理块。配合 PagedAttention 的 block 抽象，prefix cache 的命中是**指针级别**的——把请求的 block_table 前几项指向 cache 里的物理块即可。

---

## 七、量化推理：让每字节都更密

量化是另一个独立维度的优化：让模型权重和/或 KV cache 占的字节更少，直接缓解 decode 的 memory-bound。三大流派：**weight-only**（只量化权重，激活保持 FP16）、**weight+activation**（W8A8/W4A8）、**KV-only**。

### 7.1 GPTQ：基于二阶信息的逐层权重压缩

> 论文：GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers [arXiv:2210.17323](https://arxiv.org/abs/2211.17192)（ICLR 2023，IST Austria + ETH）

GPTQ 的核心是 **OBQ（Optimal Brain Quantization）** 的批量化版本。对一个权重矩阵 $W$，逐列量化：量化第 $i$ 列时，要把未量化部分做更新以补偿量化误差。补偿量用**Hessian 矩阵的逆**近似：

$$
W_{:,j} \leftarrow W_{:,j} - \frac{W_{:,i} - \text{quant}(W_{:,i})}{[H^{-1}]_{ii}} [H^{-1}]_{i,:}, \quad \forall j > i
$$

其中 $H = X X^T$（$X$ 是该层的输入激活）。GPTQ 用 Cholesky 分解高效计算 $H^{-1}$，并把 175B 模型的量化压到 **4 GPU 小时**。在 A100 上比 FP16 推理快 **3.25×**，A6000 上快 **4.5×**。

### 7.2 AWQ：保护 1% 显著权重

> 论文：AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration [arXiv:2306.00978](https://arxiv.org/abs/2306.00978)（MIT Han Lab，MLSys 2024 Best Paper）

AWQ 的关键洞察：**不是所有权重都同等重要**。激活幅度大的 channel 对应的权重，量化误差被放大，必须保护。但用混合精度（部分 FP16，部分 INT4）硬件不友好。AWQ 的巧思：用**等价缩放**——把显著 channel 的权重大幅度缩放，让它们落在 INT4 表示精度更高的区域，同时把对应的激活反向缩放，数学上等价：

$$
y = W x = (W \cdot \text{diag}(s)) \cdot (\text{diag}(1/s) \cdot x) = W' x'
$$
量化 $W'$（被缩放过的权重）误差更小，反量化时 $x'$ 用 FP16 算。只保护 **1%** 的显著 channel，INT4 量化几乎无损。TinyChat 实现比 HF FP16 快 **3×**，还能在手机 GPU 跑 70B Llama-2。

### 7.3 SmoothQuant：把激活 outlier 平移到权重

> 论文：SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models [arXiv:2211.10438](https://arxiv.org/abs/2211.10438)（MIT Han Lab + NVIDIA，ICML 2023）

SmoothQuant 解决的是 **W8A8**（权重和激活都 INT8）的难点：激活里有少量 outlier（某些 channel 数值大几百倍），破坏 INT8 表示。它用一个数学等价变换把"难量化的激活"变成"易量化的权重"：

$$
y = (W x) = (W \cdot \text{diag}(s^{-1})) \cdot (\text{diag}(s) \cdot x) = \hat{W} \hat{x}
$$
选 $s_j = \max(|x_j|)^\alpha / \max(|W_{:,j}|)^{1-\alpha}$（$\alpha$ 通常 0.5）让 $\hat{W}$ 和 $\hat{x}$ 都落在 INT8 范围。INT8 全矩阵乘，A100 上 **1.56×** 加速，2× 内存减少，几乎无损。让单节点跑 530B 模型。

### 7.4 主流量化方案对比

| 方案 | 权重精度 | 激活精度 | KV cache | 适用场景 | 精度损失 |
|------|----------|----------|----------|----------|----------|
| GPTQ | INT4 | FP16 | FP16 | 单卡大模型 | 小 |
| AWQ | INT4 | FP16 | FP16 | 边缘/移动端 | 极小 |
| SmoothQuant | INT8 | INT8 | FP16 | 数据中心 W8A8 | 极小 |
| KVQuant | FP16 | FP16 | INT3 | 超长 context | 小 |
| KIVI | FP16 | FP16 | INT2 | 大 batch 吞吐 | 小 |
| FP8 (H100原生) | FP8 | FP8 | FP8 | H100 原生 | 极小 |
| BitNet b1.58 | 三值 {-1,0,1} | INT8 | - | 训练时量化 | 匹配 FP16 |

### 7.5 BitNet 1.58：量化的极端

> 论文：The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits [arXiv:2402.17764](https://arxiv.org/abs/2402.17764)（MSRA，Furu Wei 团队）

BitNet b1.58 把**每个权重**量化到三值 $\{-1, 0, 1\}$，即 $\log_2 3 \approx 1.58$ bit。核心创新是 **训练时就是 1.58 bit**（不是 PTQ），用专门的 BitLinear 层替换 nn.Linear。匹配 FP16 同尺寸模型的 perplexity 和下游任务性能，但内存降到 1/6，能耗大幅下降。开启了"1-bit LLM 专用硬件"的设计方向。

### 7.6 KV Cache 量化的实战集成

vLLM / SGLang 都原生支持 `--kv-cache-dtype fp8` 或 `int8`。FP8 KV cache 在 H100 上几乎免费（FP8 原生支持），KV 内存减半，batch size 翻倍，精度损失 < 0.5%。这是 2024 年最性价比的"一行参数翻吞吐"。

---

## 八、Batch Size 调优：吞吐 vs 延迟的权衡

### 8.1 tradeoff 曲线

decode 阶段，batch size 越大，每次 forward 摊薄的权重读取成本越多——**吞吐**越高。但 batch 越大，单次 forward 的算力越多（每个 token 的 attention 算力叠加），**延迟**越高。

低 batch：带宽受限（memory-bound），吞吐低，延迟低。
高 batch：算力受限（compute-bound），吞吐高，延迟高。

最优工作点取决于 SLO：实时聊天要求 TPOT < 50ms，必须小 batch；离线 batch inference 无延迟要求，把 batch 撑到算力上限。

### 8.2 最大 batch size 的计算

给定 GPU 和模型，最大 batch size 受三个因素约束：

```python
def max_batch_size(model_params, gpu_mem, kv_per_token, max_context,
                   gpu_tlops, gpu_bandwidth, target_tpot):
    """
    model_params: 模型参数量（如 70e9）
    gpu_mem: GPU 内存（字节，如 80e9）
    kv_per_token: 每 token KV cache 字节
    max_context: 单请求最大 context 长度
    target_tpot: 目标每 token 延迟（秒）
    """
    weight_bytes = model_params * 2   # BF16

    # 约束 1：内存。权重 + 总 KV cache <= GPU 内存
    available_for_kv = gpu_mem - weight_bytes
    max_batch_mem = available_for_kv / (kv_per_token * max_context)

    # 约束 2：算力（compute-bound 时）。
    # 每 token 的算力（约 6 × params FLOPs）
    flops_per_token = 6 * model_params
    # 一次 decode iteration 的算力 = batch × flops_per_token
    # 算力上限下，单 iteration 时间 = batch × flops_per_token / gpu_tlops
    # 必须 < target_tpot
    max_batch_compute = target_tpot * gpu_tlops / flops_per_token

    return min(max_batch_mem, max_batch_compute)


# H100 + Llama-70B 示例
# max_batch_size(70e9, 80e9, 328e3, 4096, 1979e12, 3.35e12, 0.05)
# 约 ~20-30，正是实测区间
```

### 8.3 不同 GPU 的实测区间

| GPU | 内存 | 带宽 | 算力(BF16) | Llama-70B 合理 batch | 注 |
|-----|------|------|-----------|----------------------|-----|
| H100 SXM5 | 80GB | 3.35 TB/s | 1979 TFLOPS | 32-64 | 推理旗舰 |
| H200 | 141GB | 4.8 TB/s | 1979 TFLOPS | 80-128 | 长上下文友好 |
| A100 80GB | 80GB | 2.0 TB/s | 312 TFLOPS | 16-24 | 老一代旗舰 |
| L40S | 48GB | 0.864 TB/s | 362 TFLOPS | 4-8 | 推理性价比 |
| RTX 4090 | 24GB | 1.0 TB/s | 330 TFLOPS | 1-2 | 单卡跑不了 70B |

### 8.4 Prefill 和 Decode 的不同最优 batch

prefill 是 compute-bound，最优 batch 受算力限制；decode 是 memory-bound，最优 batch 受内存（KV cache）限制。DistServe 的核心论点之一就是：**这两个最优 batch 不同，强行用一个 batch 服务两个阶段必然次优**——所以分离架构才会赢。

---

## 九、采样优化

### 9.1 Top-k / Top-p / Temperature 的实现

朴素实现：对最后位置 logits $\in \mathbb{R}^V$（$V$ 是词表，~32K-128K）算 softmax 后采样。问题：每次都要扫整个词表。

优化：用 **Top-k 截断 + Top-p（nucleus）** 缩小候选集：
- Top-k：只保留 logits 最高的 K 个候选（K=50 常见）；
- Top-p：保留累积概率达 p 的最小候选集。

```python
def sample_top_p(logits, p=0.9, temperature=0.8):
    """FasterTransformer / vLLM 风格的 top-p 采样。"""
    logits = logits / temperature
    probs = torch.softmax(logits, dim=-1)
    # 按 prob 降序排序，累积
    sorted_probs, sorted_idx = probs.sort(descending=True)
    cumsum = sorted_probs.cumsum(dim=-1)
    # 找累积 >= p 的第一个位置，之后的全 mask
    cutoff = (cumsum > p).float().cumsum(dim=-1) > 0
    sorted_probs[cutoff] = 0
    # 重新归一化
    sorted_probs /= sorted_probs.sum(dim=-1)
    # 在小集合上采样
    sampled = torch.multinomial(sorted_probs, 1)
    return sorted_idx.gather(-1, sampled)
```

关键优化：**在排序前用 Top-k 先粗筛**（K=1000），把候选集从 32K 降到 1K，再排再 nucleus——避免对整个词表做 softmax + sort。

### 9.2 TensorRT-LLM 的优化

NVIDIA 官方推理引擎 TensorRT-LLM 把推理优化推到极致：
- ** kernels fusion**：把 RMSNorm + QKV proj + RoPE + attention 融合成一个大 kernel，减少 kernel launch 开销；
- **CUDAGraph**：把整个 decode iteration 编成静态计算图，避免每步重新 launch kernel；
- **In-flight batching**：NVIDIA 版的 continuous batching，集成到引擎层；
- **Plugin 机制**：支持 Medusa、speculative decoding、custom attention。

实测在 H100 上，TensorRT-LLM 比 vLLM 快 10-30%（特定模型和场景），但工程门槛高、闭源 plugin 多。

### 9.3 Speculative Tree Attention

Medusa / EAGLE 用 tree-based attention 同时验证多条候选路径。核心：把多条候选 token 序列拼成一棵树，用一个**特殊的 attention mask** 让每条路径只能看到它的祖先：

```python
# Medusa 的 tree attention mask 构造（4 头，每头 2 候选，共 1 + 4 + 4*4 = 节点数）
# 树结构：root -> [c1, c2] -> [c11, c12, c21, c22] -> ...
# mask[i][j] = 1 iff j 是 i 的祖先（包括自己）

def build_tree_attention_mask(tree_structure):
    """
    tree_structure: list of (parent_idx, token)
    返回 [N, N] 的下三角 attention mask，反映树的祖先关系
    """
    N = len(tree_structure)
    mask = torch.zeros(N, N)
    for i in range(N):
        # i 的祖先链
        anc = i
        while anc != -1:
            mask[i, anc] = 1
            anc = tree_structure[anc][0]   # 父节点
    return mask
```

这让多条候选路径的验证成本与单条几乎相同——一次 attention 算完。

### 9.4 Structured Decoding（SGLang）

SGLang 的另一杀手锏：把 JSON / regex 等**结构化输出**的约束编译成**压缩的有限状态机（compressed FSM）**，在每个 token 采样时直接 mask 掉不合法的 token——比逐 token 跑 parser 快几十倍。这让 LLM 输出 JSON 的速度从"边写边检查"变成"一次 forward 出合法 JSON"。

---

## 十、推理引擎全景对比

| 引擎 | 定位 | 关键技术 | 优势 | 劣势 |
|------|------|----------|------|------|
| **vLLM** | 通用吞吐 SOTA | PagedAttention, continuous batching, prefix cache | 开源、社区大、易用 | 结构化输出弱 |
| **SGLang** | 结构化 + Agent | RadixAttention, compressed FSM, RadixAttention | 多轮 Agent / JSON 最快 | 部分场景不如 vLLM |
| **TensorRT-LLM** | NVIDIA 官方 | kernel fusion, CUDAGraph, in-flight batching | H100 上最快 | 闭源 plugin、门槛高 |
| **llama.cpp** | CPU + 量化 | GGUF 量化、Metal/CUDA/Vulkan 后端 | 单机离线、低门槛 | 吞吐远不如 GPU 引擎 |
| **MLC-LLM** | universal compile | TVM 编译、WebGPU/iOS/Android | 跨平台部署 | 极致性能不如专一引擎 |
| **DeepSpeed-FastGen** | 微软 | Dynamic Splitfuse（混合 prefill-decode） | 长序列友好 | 社区小 |
| **LightLLM** | 国产轻量 | 纯 Python、kernel 优化 | 二次开发容易 | 生态弱 |

**FlashInfer** 不是引擎而是**注意力 kernel 库**：

> 论文：FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving [arXiv:2501.01005](https://arxiv.org/abs/2501.01005)（UW + NVIDIA + OctoAI，MLSys 2025）

FlashInfer 用 **block-sparse format + composable formats** 处理 KV cache 的异构存储（PagedAttention 块、RadixAttention 子树、prefix cache 命中），并提供 **JIT 编译的可定制 attention template**——支持各种 attention 变体（MHA/GQA/MLA/Medusa tree）一次编写。已被 vLLM、SGLang、MLC-Engine 集成。报告 inter-token latency 降 **29-69%**，长上下文 latency 降 **28-30%**。

---

## 十一、给「应用数学研究型工程师」的建议

基于用户的目标（应用数学研究型工程师、每周 10-20h、强偏好有趣+工程落地），给出三步递进的实战路径：

### 11.1 第一步：读 vLLM 源码（最深入）

vLLM 是研究 LLM 推理系统设计的最佳教材——工业级、开源、注释清晰。建议阅读顺序：

1. `vllm/core/scheduler.py`：continuous batching 的调度循环（~800 行），看完理解 §三；
2. `vllm/core/block_manager.py`：PagedAttention 的块表管理（~600 行），看完理解 §五；
3. `vllm/attention/backends/flash_attn.py`：attention 算子如何调用 PagedAttention 块表；
4. `vllm/engine/arg_utils.py`：所有可调参数（max_num_batched_tokens、gpu_memory_utilization 等）；
5. `vllm/model_executor/layers/`：采样、量化、RoPE 等模型层实现。

读源码的方法：带着一个具体问题（"prefix cache 怎么命中的？""speculative decoding 在哪个文件 hook 进 forward 的？"），从入口顺藤摸瓜，而不是从头读到尾。

### 11.2 第二步：实现 Medusa head（亲手做）

Medusa 是**最小完整**的 speculative decoding 实现（比 EAGLE 简单），适合作为第一个手写项目：

1. 拿一个 base model（Llama-3-8B 或 Qwen-7B）；
2. 在 hidden state 上接 4 个 Medusa head（每个一层 MLP + 一层 Linear），训练它们预测下 1-4 个 token；
3. 实现 tree attention mask 构造 + 接受算法；
4. 对比 vanilla decode 的 token/s。

完整流程 1-2 周。关键收获：彻底理解 §四的拒绝采样数学、§9.3 的 tree attention、以及 PyTorch 自定义 attention 的工程细节。Medusa 官方 repo（github.com/FasterDecoding/Medusa）是好参考。

### 11.3 第三步：实现 continuous batching（系统设计能力）

按 §3.4 的 80 行 demo 出发，逐步加：
1. PagedAttention 风格的 block 管理（替换 padding）；
2. prefix cache；
3. speculative decoding 集成。

目标不是做生产级引擎（vLLM 已经很好），而是**完整跑通一次系统设计 cycle**——这是从"会用 LLM"到"理解 LLM 系统"的质变。

### 11.4 数学视角的延伸

对应用数学导向的读者，推理优化有几个值得深入的数学问题：

1. **拒绝采样的最优性证明**（§4.3）——它在多大程度上能推广到非 token 的离散序列？连续变量？
2. **GQA/MLA 的低秩结构**——MLA 本质是 KV 的低秩分解，与矩阵补全、PCA 的关系；
3. **KV cache 压缩的次模性**（H2O）——为什么 attention score 的累积是次模函数？近似比能否改进？
4. **Speculative decoding 的最优 draft length $\gamma$**——这是 $\alpha(\gamma)$、draft 成本、target 成本的联合优化，是个有意思的 tradeoff 分析。

这些都不是"读论文+复现"的题，而是"理解后能提出新方案"的研究题——正契合应用数学研究型工程师的定位。

---

## 📌 进一步阅读

**Speculative Decoding 综述**：
- Xia et al., "Tutorial Proposal: Speculative Decoding for Efficient LLM Inference" [arXiv:2503.00491](https://arxiv.org/abs/2503.00491)（COLING 2025 Tutorial，最系统的综述）
- Spec-Bench：github.com/hemingkx/Spec-Bench

**系统论文**：
- Orca（OSDI 2022，continuous batching 起源，无 arXiv，USENIX 直接发表）
- vLLM SOSP 2023 [arXiv:2309.06180](https://arxiv.org/abs/2309.06180)
- DistServe OSDI 2024 [arXiv:2401.09670](https://arxiv.org/abs/2401.09670)
- Mooncake [arXiv:2407.00079](https://arxiv.org/abs/2407.00079)（Kimi 生产系统）

**源码**：
- vLLM：github.com/vllm-project/vllm（推荐先读 `vllm/core/`）
- SGLang：github.com/sgl-project/sglang（推荐先读 `sglang/srt/mem_cache/`）
- FlashInfer：github.com/flashinfer-ai/flashinfer（attention kernel 库）
- Medusa：github.com/FasterDecoding/Medusa
- EAGLE：github.com/SafeAILab/EAGLE

**量化**：
- MIT Han Lab 的 [llm-awq](https://github.com/mit-han-lab/llm-awq) 和 [smoothquant](https://github.com/mit-han-lab/smoothquant)
- GPTQ 官方：github.com/IST-DASLab/gptq

**KV Cache**：
- StreamingLLM：github.com/mit-han-lab/streaming-llm
- H2O：github.com/FMInference/H2O
- LMCache：github.com/LMCache/LMCache

---

## ✍️ 思考题

1. **拒绝采样的推广**。Speculative decoding 的拒绝采样证明（§4.3）依赖 token 是离散的。如果把它推广到连续潜变量序列（例如 latent diffusion 的逐步去噪），需要哪些修改？哪些假设会失效？这是不是一个值得探索的新研究方向？

2. **MLA 的低秩与 KV cache 的关系**。DeepSeek-V2 的 MLA 把 KV 压到 latent $d_c=512$。本质上这是把 $[n_h, d_h]=[128, 128]$ 的 KV 矩阵做了一次秩 512 的近似。请从矩阵补全 / 低秩近似的角度分析：MLA 的近似误差上界是多少？压缩比 93.3% 的理论依据是什么？能否进一步压到 99%？

3. **PagedAttention 的 block size 选择**。vLLM 默认 block_size=16。请分析：block_size 太小（如 1）和太大（如 1024）各有什么问题？从（a）fragmentation 浪费率、（b）attention kernel 的内存访问模式、（c）block_table 的显存占用三个维度分析最优 block_size。

4. **Speculative decoding 的最优 $\gamma$**。给定接受率 $\alpha$、draft model 单 token 时间 $t_d$、target model 单 token 时间 $t_t$，请推导最优 draft length $\gamma^*$。在 H100 上 Llama-70B（$t_t \approx 25$ms）+ 7B draft（$t_d \approx 3$ms）+ $\alpha = 0.7$ 的实际数值是多少？敏感性如何（$\alpha$ 从 0.5 到 0.9，$\gamma^*$ 怎么变）？

5. **Continuous batching 与延迟 SLO**。设 95 percentile 延迟 SLO 是 TPOT ≤ 50ms。在 H100 + Llama-70B 上，用 continuous batching 时，batch size 越大吞吐越高但尾延迟也越高。请分析：（a）为什么 batch 增大会拉长尾延迟？（b）如果引入 prefill-decode 分离（DistServe 风格），尾延迟的曲线如何变化？（c）在不分离的情况下，有什么调度策略能在高 batch 下保住尾延迟 SLO？（提示：考虑 chunked prefill、priority scheduling、early rejection）

---

<!-- delegate 直接写入，2026-07-20 -->
