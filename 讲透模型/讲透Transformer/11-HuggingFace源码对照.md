# 11 HuggingFace Transformers 源码对照

> 把原理变成可读的真实生产代码。本文对照 `huggingface/transformers` 的三个标志性实现:
> **LLaMA** (现代配方全集) · **Mixtral** (经典 MoE) · **DeepSeek-V3** (MLA 前沿)。
>
> 📌 Transformers 的 **modular 机制** (2024+): 每个模型有 `modular_*.py`, 只写"与 Llama 不同的部分"。读它能一眼看出"某模型在 LLaMA 基础上改了什么"——这是理解架构差异的最快路径。

---

## 一、LLaMA: 现代配方的完整源码 (对应 02-05 篇)

文件: `src/transformers/models/llama/modeling_llama.py`

### 1. RMSNorm (对应 05 篇)

```python
class LlamaRMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        self.weight = nn.Parameter(torch.ones(hidden_size))   # 只有 γ, 无 β (无平移)
        self.variance_epsilon = eps

    def forward(self, hidden_states):
        hidden_states = hidden_states.to(torch.float32)      # 上转 FP32 保精度
        variance = hidden_states.pow(2).mean(-1, keepdim=True)  # ← 不减均值! 只用 RMS
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)   # 乘可学习 γ
```
> 对照 05 篇公式: $\text{RMSNorm}(x) = \gamma \cdot \frac{x}{\sqrt{\frac{1}{d}\sum x_i^2 + \epsilon}}$。代码里 `pow(2).mean` + `rsqrt` 就是除 RMS。**注意没有减均值这一步**——这正是 RMSNorm 比 LayerNorm 快的原因。

### 2. RoPE 旋转位置编码 (对应 02 篇)

```python
class LlamaRotaryEmbedding(nn.Module):
    @staticmethod
    def compute_default_rope_parameters(config, device):
        base = config.rope_parameters["rope_theta"]           # θ, 通常 10000~500000
        dim = config.head_dim
        # 频率: inv_freq[i] = 1 / base^(2i/d), 不同维度用不同旋转频率
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2) / dim))
        return inv_freq, 1.0

    def forward(self, x, position_ids):
        # freqs[pos, i] = pos * inv_freq[i]  → 每个位置每个维度的旋转角度
        freqs = (inv_freq_expanded @ position_ids_expanded).transpose(1, 2)
        emb = torch.cat((freqs, freqs), dim=-1)               # cos/sin 的输入
        return emb.cos(), emb.sin()

def rotate_half(x):
    x1 = x[..., : x.shape[-1] // 2]                           # 前半
    x2 = x[..., x.shape[-1] // 2 :]                           # 后半
    return torch.cat((-x2, x1), dim=-1)                       # 构造旋转

def apply_rotary_pos_emb(q, k, cos, sin):
    q_embed = (q * cos) + (rotate_half(q) * sin)              # 复数旋转的实数实现
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed
```
> 对照 02 篇: RoPE 把每个 (q, k) 在二维子空间里旋转 $R_{m\theta}$。代码用 `rotate_half` 实现复数乘法的实数等价: $(a+bi)(\cos\theta+i\sin\theta)$ → `a*cos - b*sin, a*sin + b*cos`。

### 3. SwiGLU FFN (对应 04 篇)

```python
class LlamaMLP(nn.Module):
    def __init__(self, config):
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=config.mlp_bias)  # 门
        self.up_proj   = nn.Linear(hidden_size, intermediate_size, bias=config.mlp_bias)  # 上投影
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=config.mlp_bias)
        self.act_fn = ACT2FN[config.hidden_act]               # 通常是 "silu" (Swish)

    def forward(self, x):
        # SwiGLU: down( act(gate(x)) * up(x) )   ← 门控!
        return self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))
```
> 对照 04 篇公式: $\text{SwiGLU}(x) = \text{Swish}(xW_1) \odot (xW_2)$。代码一行 `act(gate(x)) * up(x)` 就是门控相乘。**三个 Linear** (gate/up/down), 为保持参数量中间维度用 $\frac{8}{3}d$。`mlp_bias` 通常 False (无 bias)。

### 4. GQA Attention (对应 03 篇)

```python
class LlamaAttention(nn.Module):
    def __init__(self, config, layer_idx):
        self.num_key_value_groups = config.num_attention_heads // config.num_key_value_heads
        # ↑ GQA 关键: query head 数 / kv head 数 = 每组共享几个 query
        self.scaling = self.head_dim ** -0.5                  # 1/√d_k
        self.q_proj = nn.Linear(hidden_size, num_attention_heads * head_dim, ...)
        self.k_proj = nn.Linear(hidden_size, num_key_value_heads * head_dim, ...)  # ← K 更小!
        self.v_proj = nn.Linear(hidden_size, num_key_value_heads * head_dim, ...)  # ← V 更小!

    def forward(self, hidden_states, position_embeddings, ...):
        q = self.q_proj(hidden_states).view(...).transpose(1, 2)
        k = self.k_proj(hidden_states).view(...).transpose(1, 2)
        v = self.v_proj(hidden_states).view(...).transpose(1, 2)
        q, k = apply_rotary_pos_emb(q, k, cos, sin)           # 只对 Q/K 加 RoPE, V 不加
        if past_key_values is not None:
            k, v = past_key_values.update(k, v, self.layer_idx)  # ← KV Cache!
        attn_output, _ = attention_interface(self, q, k, v, ...)  # 自动选 Flash/SDPA

def repeat_kv(hidden_states, n_rep):
    # GQA: 把少的 KV head 复制扩展, 和 query head 数对齐
    if n_rep == 1: return hidden_states                        # MHA 时无需复制
    return hidden_states[:, :, None, :, :].expand(batch, kv_heads, n_rep, slen, head_dim)...
```
> 对照 03 篇: `num_key_value_heads < num_attention_heads` 就是 GQA。`k_proj/v_proj` 的输出维度比 `q_proj` 小 `num_key_value_groups` 倍 → **KV Cache 直接缩小**。`repeat_kv` 在 eager attention 里把 KV head 复制对齐 query (Flash kernel 内部处理, 不需显式复制)。

### 5. Pre-LN + 残差组装 (对应 05 篇)

```python
class LlamaDecoderLayer(GradientCheckpointingLayer):
    def __init__(self, config, layer_idx):
        self.self_attn = LlamaAttention(config, layer_idx)
        self.mlp = LlamaMLP(config)
        self.input_layernorm = LlamaRMSNorm(...)              # attention 前的 norm
        self.post_attention_layernorm = LlamaRMSNorm(...)     # FFN 前的 norm

    def forward(self, hidden_states, ...):
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)   # ← Norm 在子层【前】= Pre-LN!
        hidden_states, _ = self.self_attn(hidden_states, ...)
        hidden_states = residual + hidden_states              # 残差: x + attn(norm(x))

        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states              # 残差: x + mlp(norm(x))
        return hidden_states
```
> 对照 05 篇: **残差主干道是干净的** (`residual = hidden_states` 在 norm 之前取), 这就是 Pre-LN 让深网络可训的根源。

### 6. 整体 + next-token CE (对应 07 篇)

```python
class LlamaModel(LlamaPreTrainedModel):
    def __init__(self, config):
        self.embed_tokens = nn.Embedding(vocab_size, hidden_size)  # token 嵌入
        self.layers = nn.ModuleList([LlamaDecoderLayer(...) for _ in range(num_layers)])
        self.norm = LlamaRMSNorm(...)                         # 最后的 final norm
        self.rotary_emb = LlamaRotaryEmbedding(config)        # RoPE (全模型共享一份)

class LlamaForCausalLM(LlamaPreTrainedModel):
    def __init__(self, config):
        self.model = LlamaModel(config)
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)  # logits 输出
    def forward(self, input_ids, labels=None, ...):
        outputs = self.model(input_ids, ...)
        logits = self.lm_head(outputs.last_hidden_state)
        if labels is not None:
            loss = self.loss_function(logits, labels, vocab_size)  # ← 交叉熵!
```
> 对照 07 篇: `lm_head` 把 hidden 投影到 vocab, `loss_function` 是 next-token 的 CrossEntropy。**注意 `_tied_weights_keys`**: `lm_head.weight` 和 `embed_tokens.weight` 绑定 (共享), 省一半嵌入参数。

---

## 二、Mixtral: 经典 MoE 源码 (对应 06 篇)

文件: `src/transformers/models/mixtral/modular_mixtral.py`
继承自 Mistral (Mistral 又基本是 LLaMA), 只把 FFN 换成 MoE。

### 1. Top-K 路由器 (Router/Gate)

```python
class MixtralTopKRouter(nn.Module):
    def __init__(self, config):
        self.top_k = config.num_experts_per_tok              # 每个 token 选几个专家 (通常 2)
        self.num_experts = config.num_local_experts          # 总专家数 (8)
        self.weight = nn.Parameter(torch.empty(num_experts, hidden_dim))

    def forward(self, hidden_states):
        router_logits = F.linear(hidden_states, self.weight) # 每个 token 对每个专家的分数
        router_probs = softmax(router_logits, dim=-1)
        router_top_value, router_indices = topk(router_probs, self.top_k)  # 选 top-k
        router_top_value /= router_top_value.sum(dim=-1, keepdim=True)     # 归一化!
        return router_logits, router_top_value, router_indices
```

### 2. 专家集合 + 稀疏计算

```python
class MixtralExperts(nn.Module):
    def forward(self, hidden_states, top_k_index, top_k_weights):
        for expert_idx in expert_hit:                        # 只算被选中的专家
            gate, up = linear(current_state, gate_up_proj[expert_idx]).chunk(2)
            current_hidden_states = act_fn(gate) * up        # 每个专家也是 SwiGLU!
            current_hidden_states = linear(current_hidden_states, down_proj[expert_idx])
            current_hidden_states *= top_k_weights[token_idx, top_k_pos]  # 乘路由权重
            final.index_add_(0, token_idx, current_hidden_states)
        return final
```

### 3. 负载均衡损失 (load balancing, 对应 06 篇传统 MoE)

```python
def load_balancing_loss_func(gate_logits, num_experts, top_k):
    # 鼓励 token 均匀分配到各专家, 防止"赢者通吃"(少数专家被疯狂使用)
    tokens_per_expert = mean(expert_mask)                    # 每个 expert 收到的 token 比例
    router_prob_per_expert = mean(routing_weights)           # 每个 expert 的平均路由概率
    return sum(tokens_per_expert * router_prob_per_expert) * num_experts
```
> 对照 06 篇: Mixtral 用**传统辅助损失**强制均衡。而 DeepSeek-V3 的 `e_score_correction_bias` 是 **auxiliary-loss-free** 方案——只影响路由决策不进 loss, 质量更好。看下面 DeepSeek 的对比。

---

## 三、DeepSeek-V3: MLA 前沿源码 (对应 03 篇 MLA)

文件: `src/transformers/models/deepseek_v3/modular_deepseek_v3.py`
继承自 Llama, 但 Attention 整个换成 **MLA**, FFN 换成 **DeepSeekMoE**。

### MLA 核心: 低秩 KV 联合压缩

```python
class DeepseekV3Attention(nn.Module):
    def __init__(self, config):
        # Q 也可低秩压缩 (大模型用): hidden → q_lora_rank → qk_head_dim
        self.q_a_proj = nn.Linear(hidden_size, q_lora_rank)        # 下投影
        self.q_a_layernorm = RMSNorm(q_lora_rank)
        self.q_b_proj = nn.Linear(q_lora_rank, num_heads * qk_head_dim)  # 上投影回来

        # ★ MLA 核心: KV 联合低秩压缩 ★
        self.kv_a_proj_with_mqa = nn.Linear(hidden_size, kv_lora_rank + qk_rope_head_dim)
        # ↑ 把 K 和 V 一起压到 kv_lora_rank 维 (+ 一点 RoPE 维)
        self.kv_a_layernorm = RMSNorm(kv_lora_rank)
        self.kv_b_proj = nn.Linear(kv_lora_rank, num_heads * (qk_nope_head_dim + v_head_dim))
        # ↑ 用时再上投影回完整 K, V

    def forward(self, hidden_states, position_embeddings, ...):
        # 1. Q 低秩压缩 (可选)
        q = self.q_b_proj(self.q_a_layernorm(self.q_a_proj(hidden_states)))
        q_pass, q_rot = split(q, [nope_dim, rope_dim])     # 拆"无位置"和"带RoPE"两部分

        # 2. ★ KV 压缩 (只缓存这个!) ★
        compressed_kv = self.kv_a_proj_with_mqa(hidden_states)   # 压到 kv_lora_rank
        k_pass, k_rot = split(compressed_kv, [kv_lora_rank, rope_dim])

        # 3. 上投影回完整 K, V (推理时用 "Absorb" 技巧省掉这步)
        k_pass = self.kv_b_proj(self.kv_a_layernorm(k_pass))
        k_pass, value = split(k_pass, [nope_dim, v_dim])

        # 4. Decoupled RoPE: 只对 k_rot/q_rot 加位置, k_pass 不加 (否则破坏低秩)
        q_rot, k_rot = apply_rotary_pos_emb(q_rot, k_rot, cos, sin)
        query = cat(q_pass, q_rot); key = cat(k_pass, k_rot)

        # 5. 缓存: 只存 compressed_kv 的小表示!
        if past_key_values is not None:
            key, value = past_key_values.update(key, value, layer_idx)
```

> **对照 03 篇 MLA**: 这就是"低秩 KV 联合压缩"的真实代码。关键点:
> 1. `kv_a_proj` 把 hidden 压到 `kv_lora_rank` (远小于 `num_heads * head_dim`) → **只缓存这个** → KV Cache 省 93%
> 2. **Decoupled RoPE** (`q_pass/q_rot` 拆分): RoPE 只加在小部分 `rope_dim` 上, 大部分 `nope_dim` 保持低秩可压缩。这是 MLA 能兼容 RoPE 的关键工程难点。
> 3. 推理时用 "Absorb" 操作把上投影吸收进 Q, 进一步省计算。

### DeepSeekMoE: 无辅助损失路由 (对比 Mixtral)

```python
class DeepseekV3TopkRouter(DeepseekV2TopkRouter):
    def __init__(self, config):
        # ★ 用 bias 代替 auxiliary loss ★
        self.register_buffer("e_score_correction_bias", torch.zeros(num_experts))

    def forward(self, hidden_states):
        scores = sigmoid(router_logits)
        scores_for_choice = scores + self.e_score_correction_bias   # bias 只影响【选谁】
        # ... group-based 选择 (先选组, 再组内选) ...
        topk_weights = scores.gather(1, topk_indices)               # 最终权重用原始 scores (不含 bias)
        return router_logits, topk_weights, topk_indices
```
> **对照 06 篇**: Mixtral 的 `load_balancing_loss_func` 把均衡写进 loss (损害质量)。DeepSeek 用 `e_score_correction_bias`——它只影响"选哪个专家", 但最终专家加权用原始 scores。**不进梯度, 不损害质量**, 这是 DeepSeek 的关键 MoE 创新。

### Dense 前 3 层 + MoE 后续

```python
class DeepseekV3DecoderLayer(LlamaDecoderLayer):
    def __init__(self, config, layer_idx):
        self.self_attn = DeepseekV3Attention(config, layer_idx)    # MLA
        if layer_idx >= config.first_k_dense_replace:              # 前 first_k 层用 dense
            self.mlp = DeepseekV3MoE(config)                       # 后续层用 MoE
        else:
            self.mlp = DeepseekV3MLP(config)                       # dense FFN
```
> **对照 06 篇**: 前 3 层 (`first_k_dense_replace`) 保持 dense FFN, 因为早期层要先提取基础特征, 此时路由器还做不好决策。

---

## 四、源码对照速查表

| 原理篇 | LLaMA 实现 | Mixtral 改动 | DeepSeek-V3 改动 |
|--------|-----------|-------------|-----------------|
| 02 位置编码 | `LlamaRotaryEmbedding` + `rotate_half` | 同 (继承 Mistral) | `apply_rotary_pos_emb_interleave` (Decoupled RoPE) |
| 03 注意力 | `LlamaAttention` (GQA) + `repeat_kv` | 同 (GQA) | **`DeepseekV3Attention` (MLA, 全部重写)** |
| 04 FFN/激活 | `LlamaMLP` (SwiGLU) | **`MixtralSparseMoeBlock` (换成 MoE)** | **`DeepseekV3MoE` (细粒度+共享专家)** |
| 05 归一化 | `LlamaRMSNorm` + Pre-LN 残差 | 同 | 同 |
| 06 MoE 路由 | 无 (dense) | `MixtralTopkRouter` + **辅助损失** | `DeepseekV3TopkRouter` + **bias (无辅助损失)** |
| 07 训练 | `lm_head` + `loss_function` (CE) | + `aux_loss` (负载均衡) | 同 LLaMA |

---

## 五、怎么继续读 transformers 源码

1. **入口**: 任选一个模型目录, 先读 `modular_*.py` (差异), 再读 `modeling_*.py` (完整)。
2. **对照**: LLaMA 是基准, 其他模型大多 `class XModel(LlamaModel): pass` 只改差异。
3. **关键文件**:
   - `src/transformers/modeling_rope_utils.py` — 所有 RoPE 变体 (default/dynamic/yarn/llama3)
   - `src/transformers/cache_utils.py` — KV Cache 实现 (DynamicCache 等)
   - `src/transformers/modeling_flash_attention_utils.py` — FlashAttention 集成
4. **值得读的模型**:
   - `llama4/` — iRoPE / NoPE 交错
   - `qwen3_moe/` — 另一种 MoE 设计
   - `gemma/` — GeGLU + RoPE 变体
   - `modernbert/` — 现代 Encoder 设计 (rotary + alternating)

> 💡 **学习法**: 读源码时, 每个类对照本项目的原理篇, 问自己"这行代码在实现哪个公式?"。能答出来, 就真懂了。

---

## 六、实验验证: 每处对照都用真实代码证实 ✓

配套脚本 `experiments/12_verify_real_llama.py` 用真实 `transformers` 库逐项验证本文对照, 实测结果 (2026-07):

| 验证项 | 真实 transformers vs 手写 | 最大差异 |
|--------|--------------------------|---------|
| §1 LlamaRMSNorm | `pow(2).mean` + `rsqrt` × γ | **0.00e+00** ✓ |
| §3 LlamaMLP (SwiGLU) | `down(silu(gate(x))*up(x))` | **0.00e+00** ✓ |
| §2 RoPE | 位置 0: cos=[1,1]; 位置 2: cos=[-0.42, 0.81] (角度增大) | 旋转证实 ✓ |
| §4 GQA | q_proj 64→64 (4头), k/v_proj 64→32 (2头) | KV Cache 缩 2× ✓ |
| §6 完整 CE loss | loss=4.19 ≈ ln(64)=4.16 (随机猜测) | next-token CE ✓ |

**训练对比** (真实 LLaMA vs 简化 mini-GPT, 同文本任务 60 步):
```
简化 mini-GPT:  104,982 参数 (可学习 pos_emb + GELU + MHA)   3.23 → 0.34
真实 LLaMA:      76,864 参数 (RoPE + SwiGLU + GQA + RMSNorm)  3.10 → 0.35
```
> **洞察**: 真实 LLaMA 用**更少 27% 参数**达到相当 loss——这正是"现代配方为 scale 设计"的实证。小规模差异不显, 但大规模长上下文下, RoPE 外推/GQA 省 KV/SwiGLU 表达力才拉开差距。

---

## 参考源码 (截至 2026)
- `huggingface/transformers` · `src/transformers/models/llama/modeling_llama.py`
- `huggingface/transformers` · `src/transformers/models/mixtral/modular_mixtral.py`
- `huggingface/transformers` · `src/transformers/models/deepseek_v3/modular_deepseek_v3.py`
- 完整仓库: https://github.com/huggingface/transformers
