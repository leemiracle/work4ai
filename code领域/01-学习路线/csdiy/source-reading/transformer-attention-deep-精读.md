# Attention 深度精读：从信息检索到 Transformer

> 参照：Attention Is All You Need (Vaswani 2017) + nanoGPT + tinyllm/model.py
>
> csdiy 对应：nanoGPT精读 + tinytransformer + tinytorch + tinyinfer

---

## 一、Attention 的本质：可微分的字典查找

### 直觉

字典查找：
```
query → 在 key-value 字典中找到最相似的 key → 返回对应的 value
```

Attention 就是**可微分版**的字典查找——不是找"最相似"的一个 key，而是给所有 key 算相似度 → 加权平均所有 value。

```
Attention(Q, K, V) = softmax(Q·Kᵀ / √d) · V
```

### 具体例子

```
Q = "猫吃什么？"（查询向量）
K = ["狗会跑", "猫吃鱼", "鸟会飞"]（每个 key 的向量）
V = [v_dog, v_cat, v_bird]（每个 key 对应的信息）

Q·K^T = [0.1, 0.9, 0.05]  → "猫吃鱼" 的相似度最高
softmax → [0.15, 0.80, 0.05]  → 加权分布
output = 0.15·v_dog + 0.80·v_cat + 0.05·v_bird  → 主要提取了 v_cat
```

**一句话**：Attention = "根据查询 Q，从所有 K-V 对中按相似度加权提取信息"。

---

## 二、QKV 的数学

### 线性投影

```
Q = X · W_Q    # 输入投影到查询空间
K = X · W_K    # 输入投影到键空间
V = X · W_V    # 输入投影到值空间
```

同一个输入 X 经过三个不同的线性变换 → 产生三种角色。

**为什么不直接用 X？** 因为"查询"、"键"、"值"需要不同的表示空间。

### 缩放点积

```
scores = Q · Kᵀ / √d_k
```

为什么要除以 √d_k？
- 如果 d_k 很大，Q·K^T 的值会很大 → softmax 进入饱和区 → 梯度消失
- 除以 √d_k 让方差回到 1 → 梯度健康

### Causal Mask（因果遮罩）

```
# 对上三角做 -∞ masking（参照 nanoGPT §4.3）
mask = [[ 0, -∞, -∞],
        [ 0,  0, -∞],
        [ 0,  0,  0]]

scores += mask  # 未来位置的 score 变 -∞
softmax(scores)  # 未来位置的 attention weight = 0
```

**为什么需要**：语言模型生成 token i 时不能看到 i+1 的信息（否则就是作弊）。

---

## 三、Multi-Head Attention

### 直觉

单个 Attention head 只能学一种"关注模式"。多个 head = 多种关注模式并行。

```
# 8 个 head 各自在 d/8 维空间里做 attention
head_0 = Attention(Q_0, K_0, V_0)  # 可能学到"语法依赖"
head_1 = Attention(Q_1, K_1, V_1)  # 可能学到"指代消解"
...
head_7 = Attention(Q_7, K_7, V_7)  # 可能学到"语义相似"

# 合并
MultiHead = Concat(head_0, ..., head_7) · W_O
```

### 工程实现（参照 nanoGPT §4.1）

```python
# QKV 合三为一（一次矩阵乘法 → 效率更高）
qkv = x @ self.qkv_weight  # [batch, seq, 3*d_model]

# 分头：把 d_model 拆成 (n_heads, d_head)
# 每个 head 在 d_head 维空间里做 attention
```

**关键洞察**：Multi-Head 的总计算量和 Single-Head 一样（d_model → n_heads × d_head），但表达能力更强。

---

## 四、Position Encoding

### 为什么需要位置信息

Attention 本身是**排列不变**的（permutation-invariant）——"猫吃鱼" 和 "鱼吃猫" 在 Attention 看来完全一样。需要额外注入位置信息。

### 两种方案

**Sinusoidal（原始 Transformer）**：
```
PE(pos, 2i) = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```

**Learned Embedding（GPT/BERT）**：
```
# 每个位置一个可学习的向量
pos_embedding = nn.Embedding(max_seq_len, d_model)
x = token_embedding(tokens) + pos_embedding(positions)
```

**RoPE（Rotary Position Embedding，LLaMA）**：
```
# 通过旋转矩阵注入相对位置
q_rotated = rotate(q, pos)
k_rotated = rotate(k, pos)
# q·k^T 自动包含相对位置信息
```

---

## 五、Pre-LN vs Post-LN

### Post-LN（原始 Transformer）

```
x = LayerNorm(x + Sublayer(x))
```

问题：深层训练不稳定（梯度爆炸/消失）。

### Pre-LN（GPT-2+，包括 nanoGPT）

```
x = x + Sublayer(LayerNorm(x))
```

优势：残差路径上没有 LayerNorm → 梯度能直接通过残差连接回传 → 深层训练更稳定 → 几乎不需要 warmup。

---

## 六、和 csdiy 的交叉

| 概念 | csdiy 对应 | 连接 |
|------|-----------|------|
| Attention QKV | 信息检索（IR） | tinysearch 的 BM25 是"硬"版 Attention |
| Softmax | tinytorch | softmax 在 tinytorch 的 loss.py 实现 |
| Multi-Head | Ensemble | 多头 = 多视角集成 |
| Position Encoding | 编码理论 | RoPE 借鉴 Fourier 变换 |
| KV Cache | 缓存理论 | bloom-filter精读：概率数据结构 |
| Weight Tying | 参数共享 | CNN 的卷积核也是参数共享 |

---

## 七、一句话总结

> Attention = softmax(Q·K^T/√d) · V —— 可微分的字典查找。
>
> Multi-Head = 多种关注模式并行。Pre-LN = 殱差路径不阻断梯度。KV Cache = 复用历史计算。
>
> **理解了 Attention，你就理解了 GPT/BERT/Llama/Qwen/DeepSeek 的心脏。**

---

*配套：[nanoGPT精读](nanoGPT-读懂最小GPT.md) | [tinyllm/model.py](../projects/tinyllm/model.py) | tinytransformer（`../projects/tinytransformer/`）*
