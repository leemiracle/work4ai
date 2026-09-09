# 长上下文精读：从 4K 到 10M

> 参照：RoPE Scaling / StreamingLLM / Ring Attention / YaRN
>
> csdiy 对应：position-encoding精读 + kv-cache精读 + flash-attention精读

---

## 一、长上下文的挑战

### 三个瓶颈

```
① 计算瓶颈:  Attention = O(N²) → N=100K 时计算量爆炸
② 内存瓶颈:  KV Cache = O(N) → N=100K 时 KV Cache > 模型权重
③ 外推瓶颈:  Position Encoding 训练 4K → 推理 100K 时性能崩溃
```

---

## 二、计算瓶颈的解法

### Flash Attention（参照 flash-attention精读）

```
标准: O(N²) HBM 读写
Flash: O(Nd) HBM 读写（分块计算）
→ N=128K 从 OOM 变为可行
```

### Sparse Attention

```
不是每个 token 都 attend 所有 token，而是只 attend 部分：

Sliding Window: 只 attend 最近 W 个 token → O(NW)
Dilated:       跳跃式 attend → 扩大感受野
Local + Global: 大部分 local + 少量 global token
```

代表：Longformer / BigBird / Mistral（sliding window attention）

### Linear Attention

```
把 softmax(QK^T)V 改写为 φ(Q) × (φ(K)^T V)
→ 不需要 N×N 矩阵 → O(Nd²)
```

代表：Linear Transformer / Performer / RWKV

---

## 三、内存瓶颈的解法

### KV Cache 压缩

```
Sliding Window KV Cache:
  只保留最近 W 个 token 的 KV → 固定内存
  丢弃旧的 KV → 无限生成

StreamingLLM (Xiao 2023):
  保留 attention sink（前几个 token）+ recent window
  → 稳定 + 无限长度
```

### KV Cache 量化

```
FP16 KV → INT8 KV → 2x 内存节省
FP16 KV → INT4 KV → 4x 内存节省
精度损失: <1% (INT8), ~3% (INT4)
```

---

## 四、外推瓶颈的解法

### 问题：训练 4K → 推理 100K

RoPE 的旋转角度 = position / 10000^(2i/d)：
```
position=4096: 旋转 = 4096/10000 = 0.41 弧度 → 训练见过的范围
position=100000: 旋转 = 10.0 弧度 → 从未见过的外推
→ 模型性能崩溃
```

### Position Interpolation (PI, Meta 2023)

```
把 position 压缩到训练范围内：
  原始: RoPE(pos)
  PI:   RoPE(pos × train_max / target_max)
  
例: 训练 4K, 掩码到 32K
  PI: RoPE(pos × 4096/32768) = RoPE(pos / 8)
→ 相当于"拉近"了 token 的位置间距
```

### NTK-Aware Scaling

```
不线性压缩，而是修改 RoPE 的 base frequency：
  原始: θ_i = 10000^(-2i/d)
  NTK:  θ_i = 10000^(-2i/d) × α  (α > 1)

→ 低维度（精确位置）保持不变
→ 高维度（粗略位置）被拉伸
→ 外推效果比 PI 好
```

### YaRN (Llama 3 用)

```
PI + NTK 的融合 + 分段缩放：
  不同维度用不同的缩放策略
→ 当前最优的位置外推方法
```

---

## 五、长上下文训练策略

### 直接长序列训练

```python
# 需要大量 GPU + Flash Attention
seq_len = 32768
batch_size = 1  # 长序列 batch 必须小
gradient_accumulation = 32  # 模拟大 batch
```

成本极高：训练 LLaMA-2 32K context 需要 ~1000 H100-days。

### 序列外推（Post-Training）

```
1. 用 4K context 训练基础模型
2. 用 32K context 做少量继续训练（~1% 原始数据量）
3. 配合 PI/YaRN 位置缩放
→ 成本只有直接训练的 1%
```

### Ring Attention（跨 GPU 长序列）

```
GPU 0: 处理 token 0-8191
GPU 1: 处理 token 8192-16383
...

环形传递 KV → 每个 GPU 都看到所有 token
→ N 张 GPU = N×8K 总 context
```

代表：Together AI 的 1M context Llama-2

---

## 六、长上下文的评估

### Needle in a Haystack（大海捞针）

```
在 100K 文档中放一个"针"（特定事实），问模型这个事实。
→ 测试模型是否真的"看到"了整个上下文。

结果：
  GPT-4 Turbo (128K):  73% 准确率
  Claude 2.1 (200K):   98% 准确率
  Gemini 1.5 (1M):     99% 准确率
```

### Lost in the Middle

```
模型倾向于记住 context 的开头和结尾，忘记中间：
  开头: ✅ 记住
  中间: ❌ 忘记
  结尾: ✅ 记住
→ "Lost in the Middle" 问题
```

---

## 七、各模型的长上下文方案

| 模型 | 最大 context | 方案 |
|------|-------------|------|
| GPT-4 Turbo | 128K | Flash Attention + PI |
| Claude 3 | 200K | Flash Attention + 工程优化 |
| Gemini 1.5 | 1M+ | Ring Attention + Sparse |
| LLaMA-3 | 128K | YaRN + GQA + Flash |
| Mistral | 32K-128K | Sliding Window + Flash |
| RWKV | ∞（理论上） | Linear Attention |

---

## 八、一句话总结

> 长上下文的三个瓶颈 = 计算（Flash Attention）/ 内存（KV Cache 压缩）/ 外推（YaRN 位置缩放）。
>
> 训练 4K → 推理 100K 的标准路径：YaRN + Flash Attention + KV Cache 量化 + 少量长序列继续训练。
>
> **Gemini 1.5 的 1M context = Ring Attention（跨 GPU）+ 极致工程优化。**

---

*配套：[position-encoding精读](position-encoding-精读.md) | [kv-cache-原理](kv-cache-原理-精读.md) | [flash-attention精读](flash-attention-精读.md)*
