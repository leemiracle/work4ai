# 01 Self-Attention 深度：KV Cache 与 FlashAttention

> 上一篇 (00 全景) 讲了 Self-Attention 的基本公式。本篇深入两个让它"能用起来"的工程突破:
> **KV Cache** (让推理快) 和 **FlashAttention** (让训练能放下长序列)。

---

## 一、KV Cache: 自回归推理的加速器

### 问题: 生成时重复计算

GPT 生成是**自回归**的: 逐个 token 生成。第 $t$ 步, 用 $[x_1...x_t]$ 预测 $x_{t+1}$。第 $t{+}1$ 步, 用 $[x_1...x_{t+1}]$ 预测 $x_{t+2}$。

注意: 前面 $t$ 个 token 的 K、V 每步都重算! 这是巨大的浪费。

### 解法: 缓存历史 K/V

观察到 **K、V 只依赖输入 token, 与新生成的 Q 无关**。所以:
- 每生成一个新 token, 只算**它自己的** K、V, 追加到缓存
- 下一步直接复用缓存里所有历史 K、V

```
Step t:   Q_t 与  [K_1..K_t, V_1..V_t]  算 attention  (缓存已存前 t-1, 只新算第 t)
Step t+1: Q_{t+1} 与 [K_1..K_{t+1}, V_1..V_{t+1}]  (复用前 t 个, 只新算第 t+1)
```

**复杂度**: 从每步 $O(t^2)$ (重算) 降到每步 $O(t)$ (只算新 token)。

### KV Cache 的代价: 显存

$$\text{KV Cache} = 2 \times n_{layer} \times n_{kv\_head} \times d_h \times \text{seq\_len} \times \text{batch} \times \text{dtype\_bytes}$$

例: LLaMA-2 70B, 32K 上下文, batch=1, FP16 → **~40 GB** 仅 KV Cache!
这正是 03 篇讲的 MQA/GQA/MLA 要解决的。

> 💡 **CS25 连接**: Charles Frye (Modal, CS25 V6) 讲 "Serving Transformers: Lessons from the Trenches"——KV Cache 管理是生产推理系统的头号难题。

---

## 二、FlashAttention: 让 O(n²) 不再爆炸

### 问题: 标准 attention 的内存墙

$$\text{Attention} = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) V$$

标准实现要先把 $n \times n$ 的 $QK^T$ 矩阵**写到 HBM (显存)**, 再 softmax, 再乘 V。对长序列 (n=128K), 这个中间矩阵极大, 反复读写 HBM → 慢。

### Dao 的洞察: 算法没变, 改的是"读写顺序"

GPU 有两层存储:
- **SRAM** (片上, ~20MB, 极快)
- **HBM** (显存, ~80GB, 慢)

标准 attention 的瓶颈是 **HBM 读写次数**, 不是计算量。FlashAttention 的核心:
1. 把 Q, K, V 分块 (tiling)
2. 在 **SRAM 里**算分块的 attention (用 online softmax 技巧, 不需要完整 $QK^T$)
3. 只把最终结果写回 HBM

**结果** (Dao et al. 2022):
- 同样的数学结果 (exact, 非近似!)
- HBM 读写从 $O(n^2)$ 降到 $O(n^2 d / M)$ ($M$ = SRAM 大小)
- **快 2-4 倍, 显存省 5-20 倍**, 支持更长序列

### FlashAttention 2 & 3
- **v2** (2023): 更好的并行化 (沿序列和 head 维度), 快 ~2 倍。
- **v3** (2024): 针对 H100, 利用异步 copy + FP8, 达到 740 TFLOPS (H100 峰值的 75%)。

### FlashMLA (DeepSeek 2025)
DeepSeek 为 MLA 定制的 kernel, 在 H800 上达 **660 TFLOPS** + **3000 GB/s** 显存带宽。这是 MLA 能落地的工程基础 (没有它 MLA 慢于 GQA)。

---

## 三、为什么你写的 attention 要用 SDPA

PyTorch 2.0+ 的 `F.scaled_dot_product_attention` 自动调用 FlashAttention 后端。你实验里 mini-GPT 就用它:
```python
a = F.scaled_dot_product_attention(q, k, v, is_causal=True)
```
- 自动选最快的 kernel (Flash / memory-efficient / 数学后端)
- 自动处理 causal mask
- **永远不要手写 softmax(QK^T)V 再搬到显存**——那是最慢的写法

---

## 速查

| 技术 | 解决什么 | 收益 |
|------|---------|------|
| **KV Cache** | 推理重复计算 | 每步 O(t²)→O(t), 代价是显存 |
| **MQA/GQA/MLA** | KV Cache 显存 | 砍 K/V head 数或低秩压缩 (03 篇) |
| **FlashAttention** | 训练/推理的 HBM 瓶颈 | 快 2-4×, 省显存, exact |
| **FlashMLA** | MLA 的 kernel | 让 MLA 真正可用 |

---

## 参考文献
- Dao et al. 2022, *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*
- Dao 2023, *FlashAttention-2*
- Shah et al. 2024, *FlashAttention-3*
- DeepSeek 2025, FlashMLA (GitHub: deepseek-ai/FlashMLA)
