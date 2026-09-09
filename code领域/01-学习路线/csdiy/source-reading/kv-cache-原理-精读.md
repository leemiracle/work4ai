# KV Cache 原理精读：LLM 推理的核心优化

> 参照：vLLM (Kwon 2023) / llama.cpp / TGI
>
> csdiy 对应：tinyllm/infer.py + tinyinfer + vLLM 精读

---

## 一、问题：朴素推理的 O(N²) 计算

生成第 N 个 token 时，朴素方法重新计算所有 N 个 token 的 Attention：

```
生成 token 100：
  forward(token_0, token_1, ..., token_99)  → 100×d_model 的 Attention
  → Q[100] × K[100]^T = [100×100] 的 attention matrix

生成 token 101：
  forward(token_0, token_1, ..., token_100) → 101×d_model 的 Attention
  → Q[101] × K[101]^T = [101×101] 的 attention matrix
  → 前 100 个 token 的 K,V 被重复计算了！
```

**时间复杂度**：生成 N 个 token = O(N³)。

---

## 二、KV Cache：缓存历史 K,V

### 核心思想

```
生成 token N 时：
  只计算 Q[N]（新 token 的查询）
  K[0..N-1] 和 V[0..N-1] 从缓存读取（不重新计算）
  Attention(Q[N], K_cache, V_cache) → 只做 1×N 的 attention
```

**时间复杂度**：O(N²) → 每步 O(N)，总计 O(N²)。

### 两个阶段

```
Phase 1: Prefill（首次处理 prompt）
  forward(prompt_tokens)     → 一次处理整个 prompt
  缓存所有 K[i], V[i]        → 填充 KV Cache

Phase 2: Decode（逐 token 生成）
  forward(new_token)         → 只算 1 个 token 的 Q,K,V
  K_cache.append(K[new])     → 追加到缓存
  Attention(Q[new], K_cache, V_cache) → 1×N 的 attention
```

### 你的 tinyllm/infer.py

```python
class KVCache:
    def __init__(self):
        self.k = []; self.v = []  # 缓存历史 K, V
    def append(self, k_new, v_new):
        self.k.extend(k_new); self.v.extend(v_new)

# generate() 中的使用
# Phase 1: Prefill
logits = model.forward(prompt_ids)  # 处理整个 prompt

# Phase 2: Decode（只算新 token）
for _ in range(max_tokens):
    logits = model.forward([next_token])  # 只算 1 个 token
    next_token = sample(logits[-1])
```

---

## 三、KV Cache 的内存代价

```
每个 token 的 KV Cache = 2 (K+V) × n_layers × n_heads × d_head × dtype_size

例：LLaMA-7B, seq=4096
  = 2 × 32 × 32 × 128 × 2 bytes (FP16)
  = 0.5 MB/token
  × 4096 tokens = 2 GB KV Cache

例：LLaMA-70B, seq=8192
  = 2 × 80 × 64 × 128 × 2 = 2.5 MB/token
  × 8192 = 20 GB KV Cache（比模型权重还大！）
```

**KV Cache 是 LLM 推理的主要内存瓶颈。**

---

## 四、vLLM 的 PagedAttention

### 问题

传统 KV Cache 是**连续分配**的：
```
请求 A: [token0 token1 token2 ... ... ...]  ← 预留 max_seq 空间
请求 B: [token0 token1 ... ... ... ... ...]  ← 预留 max_seq 空间
```
→ 内部碎片严重（实际生成长度 < max_seq → 浪费）

### vLLM 的方案：PagedAttention（参照 OS 虚拟内存）

```
把 KV Cache 分成固定大小的 block（如 16 tokens/block）
类似操作系统的页式内存管理：

Block Pool: [b0][b1][b2][b3][b4][b5]...

请求 A: block_table = [b0, b3, b5]  → 逻辑连续，物理分散
请求 B: block_table = [b1, b2, b4]  → 按需分配
```

### 优势

1. **无内部碎片**：按需分配 block，最多浪费 1 个 block
2. **共享 KV**：不同请求可以共享相同 prompt 的 KV block（如 system prompt）
3. **动态批处理**：不同长度的请求可以灵活组合

---

## 五、KV Cache 优化技术

### Multi-Query Attention (MQA)

```
标准 MHA: n_heads 组独立的 K, V
MQA:     所有 head 共享 1 组 K, V
→ KV Cache 缩小 n_heads 倍！
```

代表：PaLM / Falcon / LLaMA-2

### Grouped-Query Attention (GQA)

```
MHA 和 MQA 的折中：n_heads → n_groups (如 8→2)
→ KV Cache 缩小 n_heads/n_groups 倍
→ 效果几乎不降
```

代表：LLaMA-2 70B / Mistral / Qwen-2

### KV Cache 压缩

| 方法 | 原理 | 效果 |
|------|------|------|
| Eviction | 删除 attention score 最低的 KV | ~50% 压缩 |
| Quantization | KV Cache 存 INT8 | 2x 压缩 |
| StreamingLLM | 只保留 sink tokens + recent tokens | 固定窗口 |
| H2O | 动态保留 top-K 重 attention 的 KV | ~50% 压缩 |

---

## 六、Prefill vs Decode 的延迟特征

```
Prefill (prompt=512 tokens):
  → 计算 dense attention [512×512]
  → GPU compute bound（算力瓶颈）
  → 延迟: ~50ms

Decode (1 token):
  → 计算 sparse attention [1×512]
  → GPU memory bandwidth bound（内存带宽瓶颈）
  → 延迟: ~5ms/token
```

**Decode 是 memory-bound** → GPU 利用率低 → vLLM 用 batching 弥补。

---

## 七、Continuous Batching（连续批处理）

传统 batching：等最长的请求生成完才切换 batch → 短请求等待。

Continuous Batching（vLLM 创新）：
```
时间 →
Req A: [prefill][decode][decode][done]
Req B:          [prefill][decode][decode][decode][done]
Req C:                   [prefill][decode][decode]
Req D:                            [prefill][decode]

→ 每步都可以加入新请求 / 移除完成请求
→ GPU 始终满载
```

---

## 八、一句话总结

> KV Cache = 缓存历史 K,V → 推理从 O(N³) 降到 O(N²)。
>
> PagedAttention (vLLM) = 操作系统页式管理 → 无碎片 + 共享 + 动态批处理。
>
> MQA/GQA = 共享 K,V → 缩小 KV Cache n_heads 倍。
>
> **LLM 推理 = Prefill (compute-bound) + Decode (memory-bound) → KV Cache 是连接两者的桥梁。**

---

*配套：[tinyllm/infer.py](../projects/tinyllm/infer.py) | [transformer-attention-deep](transformer-attention-deep-精读.md) | [softmax-temperature](softmax-temperature-精读.md)*
