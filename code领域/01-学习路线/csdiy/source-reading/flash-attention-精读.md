# Flash Attention 精读：IO-Aware 的精确 Attention

> 参照：FlashAttention (Dao 2022) / FlashAttention-2 (Dao 2023)
>
> csdiy 对应：transformer-attention-deep + tinyllm + AI前沿

---

## 一、问题：标准 Attention 的 HBM 瓶颈

### 标准 Attention 的内存访问

```
S = Q @ K^T                    # [N×N] 写入 HBM
P = softmax(S)                 # [N×N] 读写 HBM
O = P @ V                      # [N×N] 读 HBM → [N×d] 写 HBM
```

- **HBM（高带宽内存）读写**：3 次 [N×N] 矩阵 = O(N²) 的 HBM 访问
- N=8192 时：N² = 67M 个 float → 268MB 的中间结果反复读写

### GPU 内存层次

```
SRAM (片上缓存): 20MB, 19TB/s  ← 极快但极小
HBM (显存): 40GB, 1.5TB/s     ← 大但慢 7x
```

**瓶颈**：O(N²) 的 HBM 读写，不是计算本身。

---

## 二、Flash Attention 的核心思想

### 分块计算 + 在线 Softmax

**不在 HBM 中存储 N×N 矩阵，而是在 SRAM 中分块计算。**

```
将 Q, K, V 分成块（block_size × d_model）
对每个 Q 块：
  在 SRAM 中遍历所有 K, V 块
  累积 softmax 的部分结果
  最终输出 O → 直接写入 HBM
```

### 在线 Softmax（关键技术）

标准 softmax 需要看到整行才能计算 → 不能分块。

Flash Attention 的**在线 softmax**：
```
# 处理 K 的第 j 个块时，累积更新 softmax 的分母
m_new = max(m_old, max(S_ij))           # 更新最大值
f_old = exp(m_old - m_new) × f_old      # 缩放旧指数和
f_new = f_old + Σ exp(S_ij - m_new)     # 加上新块
l_new = f_new                            # softmax 分母
```

→ 不需要存储完整的 N×N softmax 矩阵！

---

## 三、Flash Attention vs 标准 Attention

| 维度 | 标准 Attention | Flash Attention |
|------|---------------|-----------------|
| HBM 读写 | O(N²d + N²) | **O(Nd)** ← 减少 N 倍 |
| 计算 FLOPs | O(N²d) | O(N²d) ← 相同 |
| 中间矩阵 | N×N 存 HBM | **无**（全在 SRAM） |
| 结果 | 精确 | **精确**（不是近似！） |
| 长序列 | OOM | **N=128K 可行** |

### 关键洞察

Flash Attention **不减少计算量**（FLOPs 相同），而是**减少内存读写**。

GPU 计算速度 >> 内存带宽 → 减少 IO = 提速 2-4x。

---

## 四、FlashAttention-2 的改进

### 减少非矩阵运算 FLOPs

```
FA1: 很多 rescale 操作（softmax 分母更新）→ 非矩阵 FLOPs 占 25%
FA2: 重新编排循环 → 非矩阵 FLOPs 降到 5%
→ GPU 利用率从 25-40% 提升到 50-73%
```

### 更好的并行度

```
FA1: 只在 batch × n_heads 维度并行
FA2: 额外在 sequence 维度并行 → 更好地利用多 GPU
```

---

## 五、使用方式

### PyTorch 2.0+（自动启用）

```python
# PyTorch 2.0+ 自动使用 Flash Attention
with torch.autocast("cuda"):
    output = F.scaled_dot_product_attention(q, k, v)
# → 内部自动调用 Flash Attention（如果支持）
```

### 手动调用

```python
from flash_attn import flash_attn_func

output = flash_attn_func(q, k, v, causal=True)
# → 精确结果，但更快 + 更省显存
```

### 前提条件

- GPU: Ampere (A100) 或更新
- CUDA: 11.6+
- 数据类型: FP16 / BF16
- head_dim: ≤ 128（SRAM 容量限制）

---

## 六、对长序列的影响

```
序列长度:    2K      8K      32K     128K
标准 Attn:  4GB     64GB    OOM     OOM
Flash Attn: 0.3GB   1.2GB   4.8GB   19GB
速度比:      1x      3x      8x      15x+
```

**Flash Attention 让 128K 上下文成为可能**（Claude/GPT-4 Turbo 依赖它）。

---

## 七、Flash Attention 的衍生

| 变体 | 改进 | 用途 |
|------|------|------|
| FlashAttention-2 | 减少非 matmul FLOPs | 当前标配 |
| FlashAttention-3 | Hopper GPU 优化 | H100 |
| Ring Attention | 跨 GPU 分布式 | 多卡长序列 |
| Stream-LLM + Flash | 滑动窗口 + Flash | 流式推理 |

---

## 八、一句话总结

> Flash Attention = 分块计算 + 在线 Softmax → O(Nd) HBM 读写（vs O(N²)）。
>
> **精确的**（不是近似），但快 2-4x、省 N 倍显存。
>
> **没有 Flash Attention，就没有 GPT-4 Turbo 的 128K 上下文。**

---

*配套：[transformer-attention-deep](transformer-attention-deep-精读.md) | [kv-cache-原理](kv-cache-原理-精读.md) | [tinyllm/model.py](../projects/tinyllm/model.py)*
