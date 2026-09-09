# Attention 变体精读：从 Dense 到 Sparse 到 Linear

> 参照：Longformer / Linformer / MQA / GQA / Sliding Window
>
> csdiy 对应：transformer-attention-deep + kv-cache-原理 + long-context精读

---

## 一、标准 Attention 的代价

```
Attention(Q, K, V) = softmax(QK^T / √d) × V

计算: O(N² × d)     ← N 是序列长度
内存: O(N²)         ← N×N 的 attention matrix
KV Cache: O(N × d)  ← 每层每头的 KV

N=8192: N²=67M → 256MB 中间矩阵（每层每头）
```

**问题**：长序列时 N² 爆炸。

---

## 二、KV 共享优化（减少 KV Cache）

### MHA（标准 Multi-Head）

```
n_heads = 32, d_head = 128
KV Cache = 2 × n_layers × n_heads × N × d_head

LLaMA-7B: 2 × 32 × 32 × N × 128 = 0.26 MB/token
N=4096 → 1GB KV Cache
```

### MQA（Multi-Query Attention，Shazeer 2019）

```
所有 head 共享 1 组 K, V（只有 Q 是 multi-head）

KV Cache = 2 × n_layers × 1 × N × d_head
→ 缩小 n_heads 倍（32x）！

LLaMA-7B: 0.008 MB/token → N=4096 只需 33MB
缺点: 质量轻微下降
```

### GQA（Grouped-Query Attention，Ainslie 2023）

```
MHA 和 MQA 的折中：
  n_heads 个 Q → 分成 n_groups 组
  每组共享 1 组 K, V

例: 32 heads → 4 groups → 每组 8 个 head 共享 KV
→ KV Cache 缩小 8 倍
→ 质量几乎不降
```

### 对比

| 方案 | Q heads | KV heads | KV Cache | 质量 | 代表 |
|------|---------|----------|---------|------|------|
| MHA | 32 | 32 | 1× | 最好 | 原始 Transformer |
| MQA | 32 | 1 | 1/32 | 略降 | PaLM/Falcon |
| GQA | 32 | 4-8 | 1/4-1/8 | ≈MHA | **LLaMA-2/Mistral** |

---

## 三、稀疏 Attention（减少 N² 计算）

### Sliding Window Attention

```
每个 token 只 attend 最近 W 个 token（而非全部 N 个）

attention_matrix:
  [1 1 0 0 0 0 0]   ← token 0 attend [0,1]
  [1 1 1 0 0 0 0]   ← token 1 attend [0,1,2]
  [0 1 1 1 0 0 0]   ← token 2 attend [1,2,3]
  [0 0 1 1 1 0 0]   ← ...

W=3 时: 计算量 O(NW) vs O(N²)

代表: Mistral（W=4096）/ Longformer
```

**效果**：W=4096 时 → 等效 4096 context 但不受序列长度限制（可以无限生成）。

### Global + Local（Longformer）

```
少数 token 有 global attention（attend 所有）
其他 token 只有 local attention（sliding window）

代表: Longformer
效果: 兼顾全局信息 + 局部计算效率
```

### Dilated Sliding Window

```
跳跃式 attend（如 [1, _, 1, _, 1]）
→ 感受野更大但计算量不变
类似 Dilated CNN
```

---

## 四、Linear Attention

### 数学变换

```
标准: O = softmax(QK^T) × V   ← 需要计算 N×N 矩阵

Linear: O = φ(Q) × (φ(K)^T × V)  ← 先算 K^T V（d×d），再乘 Q

φ = 核函数（替代 softmax）
→ 不需要 N×N 矩阵！
→ 计算: O(N × d²) 而非 O(N² × d)
```

### 代表方法

| 方法 | φ(x) | 特点 | 代表 |
|------|------|------|------|
| Linear Transformer | elu(x)+1 | 最简单 | Katharopoulos 2020 |
| Performer | 正随机特征 | 近似 softmax | Choromanski 2020 |
| RWKV | 线性化 RNN | 推理 O(1) | RWKV |
| Mamba | SSM 选择性 | 当前最强线性 | Gu 2023 |

### Mamba（State Space Model）

```
不是 Attention，而是选择性状态空间模型：
  h_t = A × h_{t-1} + B × x_t    ← 线性递推
  y_t = C × h_t                   ← 线性读出

→ 推理时 O(1) per token（不需要 KV Cache）
→ 训练时可以并行（类似 Linear Attention）
→ 效果接近 Transformer（某些任务更好）
```

---

## 五、完整对比表

| 方法 | 计算 | 内存 | KV Cache | 质量 | 长序列 | 代表 |
|------|------|------|---------|------|--------|------|
| MHA | O(N²d) | O(N²) | O(Nd) | 最好 | ❌ | 原始 |
| MQA | O(N²d) | O(N²) | O(Nd/h) | 略降 | ❌ | PaLM |
| GQA | O(N²d) | O(N²) | O(Nd/g) | ≈MHA | ❌ | LLaMA-2 |
| Sliding | O(NWd) | O(NW) | O(Nd) | 局部好 | ✅ | Mistral |
| Sparse | O(Nkd) | O(Nk) | O(Nd) | 中等 | ✅ | Longformer |
| Linear | O(Nd²) | O(Nd) | O(d²) | 降 | ✅✅ | Performer |
| Mamba | O(Nd) | O(d) | O(d) | ≈Attn | ✅✅ | Mamba |

---

## 六、选择指南

```
序列长度 < 8K → MHA 或 GQA（质量最好）
序列长度 8K-32K → GQA + Flash Attention（平衡）
序列长度 32K-128K → GQA + Sliding Window + Flash
序列长度 > 128K → Linear Attention（Mamba/RWKV）
推理延迟敏感 → GQA（最小 KV Cache）
```

---

## 七、一句话总结

> GQA = 当前的甜点选择（LLaMA/Mistral/Qwen 全用）。
>
> Sliding Window = 让 Mistral 无限生成长文本。
>
> Mamba = Attention 的有力竞争者（线性推理 + 选择性记忆）。
>
> **趋势：从 Dense → GQA → Sliding → Linear/Mamba，用更少的计算做更长的序列。**

---

*配套：[transformer-attention-deep](transformer-attention-deep-精读.md) | [kv-cache-原理](kv-cache-原理-精读.md) | [long-context精读](long-context-精读.md) | [flash-attention精读](flash-attention-精读.md)*
