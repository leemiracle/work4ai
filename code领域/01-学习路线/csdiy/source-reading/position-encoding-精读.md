# Position Encoding 精读：从 Sinusoidal 到 RoPE

> 参照：Vaswani 2017 / Su et al. 2021 (RoPE) / Press et al. 2021 (ALiBi)
>
> csdiy 对应：nanoGPT精读 + transformer-attention-deep + tinyllm/model.py

---

## 一、为什么需要位置编码

Attention 是**排列不变**的：

```
"猫吃鱼" 和 "鱼吃猫" → Attention 看到完全相同的 Q/K/V
```

模型不知道 token 的顺序 → 需要**额外注入位置信息**。

三种方案：

| 方案 | 思路 | 代表 |
|------|------|------|
| **Absolute PE** | 每个 position 一个固定向量 | 原始 Transformer / BERT |
| **Learned PE** | 每个 position 一个可学习向量 | GPT-2 / nanoGPT |
| **Relative PE** | 编码 position 之间的相对距离 | T5 / RoPE / ALiBi |

---

## 二、Sinusoidal（原始 Transformer 2017）

### 公式

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```

- `pos`：token 在序列中的位置（0, 1, 2, ...）
- `i`：维度索引（0 到 d/2-1）
- `d`：模型维度（如 512）

### 直觉

不同维度用**不同频率**的正弦波编码位置：

```
维度 0,1（低频）: sin(pos/1), cos(pos/1)       → 编码"精确位置"
维度 2,3:         sin(pos/100), cos(pos/100)   → 编码"局部位置"
维度 d-2,d-1（高频）: sin(pos/10000), cos(pos/10000) → 编码"全局位置"
```

### 为什么用正弦

1. **可外推**：训练时 max_seq=512，推理时可以到 1024（sin/cos 对任意 pos 有定义）
2. **相对位置可线性表示**：`PE(pos+k)` 可以表示为 `PE(pos)` 的线性变换 → 模型能学习相对注意力

### 使用方式

```python
# 原始 Transformer
x = token_embedding(token) + position_encoding(position)
```

### 缺点

- 绝对位置编码 → 模型需要从绝对位置"推断"相对关系
- 外推效果不好（训练 512 → 推理 2048 时性能下降）

---

## 三、Learned PE（GPT-2 / nanoGPT）

### 实现

```python
# nanoGPT 精读 §7.1
self.wte = nn.Embedding(vocab_size, d_model)   # 词嵌入
self.wpe = nn.Embedding(block_size, d_model)   # 位置嵌入（可学习）

# forward
tok_emb = self.wte(idx)           # [batch, seq, d]
pos_emb = self.wpe(positions)     # [batch, seq, d]
x = tok_emb + pos_emb             # 相加
```

### 特点

- 每个 position 一个**可学习**的向量
- 简单有效 → GPT-2/BERT/nanoGPT 全用这个
- **不能外推**：训练 max_seq=1024 → 推理不能超过 1024

### 你的 tinyllm/model.py

```python
self.tok_emb = [[random.gauss(0, 0.02) ...] for _ in range(vocab_size)]
self.pos_emb = [[random.gauss(0, 0.02) ...] for _ in range(max_seq)]

# forward
x = [[self.tok_emb[tid][j] + self.pos_emb[i][j] for j in range(d_model)]
     for i, tid in enumerate(token_ids)]
```

---

## 四、RoPE（Rotary Position Embedding，LLaMA）

### 核心思想

**不编码绝对位置，而是通过旋转矩阵让 Q·K 的点积自动包含相对位置。**

```
q_rotated = rotate(q, pos)
k_rotated = k, pos)

q_rotated · k_rotated = f(q, k, pos_q - pos_k)  ← 只依赖相对距离！
```

### 数学

对维度对 (2i, 2i+1) 做旋转：

```
[q'_{2i}  ]   [cos(mθ_i)  -sin(mθ_i)] [q_{2i}  ]
[q'_{2i+1}] = [sin(mθ_i)   cos(mθ_i)] [q_{2i+1}]

θ_i = 10000^(-2i/d)
```

旋转角度 `mθ_i` 与位置 `m` 成正比 → 不同维度不同旋转速度。

### 为什么有效

```
⟨rotate(q, m), rotate(k, n)⟩ = ⟨q, k⟩_rotated(m-n)

→ 点积自动是相对位置 (m-n) 的函数
→ 模型直接看到"这两个 token 相距多远"
```

### 外推能力

RoPE 天然支持长序列外推（配合 Position Interpolation 技术）：
- LLaMA 训练 max_seq=2048 → PI 后可扩展到 8192+
- 关键：RoPE 的旋转对任意 m 都有定义

### 使用

```python
# LLaMA / Qwen / DeepSeek 都用 RoPE
def apply_rotary_emb(q, k, cos, sin):
    q_rot = (q * cos) + (rotate_half(q) * sin)
    k_rot = (k * cos) + (rotate_half(k) * sin)
    return q_rot, k_rot
```

---

## 五、ALiBi（Attention with Linear Biases）

### 核心思想

不改 Q/K，而是在 attention score 上**直接加一个距离惩罚**。

```
score(i, j) = q_i · k_j / √d  - m · |i - j|
```

- `m`：每个 head 有不同的斜率（固定的几何序列）
- `|i - j|`：两个 token 的距离

### 特点

- **无需位置编码**：直接在 attention 上加偏置
- **天然外推**：训练 1024 → 推理 2048 无性能下降
- 简单高效
- 代表：BLOOM / MPT

---

## 六、对比总结

| 方案 | 外推 | 相对位置 | 复杂度 | 代表模型 |
|------|------|---------|--------|---------|
| Sinusoidal | ✅ | ⚠️（间接） | O(d) | 原始 Transformer |
| Learned | ❌ | ❌ | O(d) | GPT-2/BERT/nanoGPT |
| RoPE | ✅ | ✅ | O(d) | LLaMA/Qwen/DeepSeek |
| ALiBi | ✅ | ✅ | O(1) | BLOOM/MPT |

### 选择指南

```
你的模型需要长序列外推吗？
├── 是 → RoPE（当前最优）或 ALiBi（最简单）
└── 否 → Learned PE（最简单，效果不差）
```

---

## 七、和 tinyllm 的交叉

你的 `tinyllm/model.py` 用的是 **Learned PE**：

```python
# Position Embedding
self.pos_emb = [[random.gauss(0, 0.02) ...] for _ in range(max_seq)]

# forward
x = [[self.tok_emb[tid][j] + self.pos_emb[i][j] ...]
     for i, tid in enumerate(token_ids)]
```

如果要改成 RoPE：
```python
def apply_rope(q, pos, d_model):
    # 对每对维度做旋转
    for i in range(0, d_model, 2):
        theta = pos / (10000 ** (i / d_model))
        q[i], q[i+1] = q[i]*cos(theta) - q[i+1]*sin(theta), \
                        q[i]*sin(theta) + q[i+1]*cos(theta)
    return q
```

---

## 八、一句话总结

> 位置编码解决 Attention 的"排列不变"问题。Learned PE 最简单（GPT-2），RoPE 支持外推（LLaMA），ALiBi 最简单的外推方案。
>
> **当前趋势：RoPE + Position Interpolation = 无限长序列（如 Claude 的 200K context）。**

---

*配套：[transformer-attention-deep](transformer-attention-deep-精读.md) | [nanoGPT精读](nanoGPT-读懂最小GPT.md) | [tinyllm/model.py](../projects/tinyllm/model.py)*
