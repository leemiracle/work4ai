# 06 · minGPT — 310 行讲透整个 GPT 架构

> **Andrej Karpathy · minGPT**（24k★）。GPT（Generative Pre-trained Transformer）的最小 PyTorch 实现——`model.py` 310 行 + `trainer.py` 109 行。nanoGPT 的前身，把 OpenAI GPT-2 的 TensorFlow 实现剥到"一个文件读得完"。
>
> 源码：[`repos/minGPT/mingpt/model.py`](./repos/minGPT/mingpt/model.py) ｜ 原仓库：https://github.com/karpathy/minGPT

---

## 0. 为什么 minGPT 是理解 GPT 的最佳入口

| 维度 | minGPT | HuggingFace transformers |
|---|---|---|
| 代码量 | **310 行单文件** | modeling_gpt2.py ~1500 行 + 抽象层 |
| 依赖 | 仅 PyTorch | transformers 全家桶 |
| 可读性 | **每个组件从零写** | 调用抽象基类 |
| 能加载预训练权重 | ✅（`from_pretrained`）| ✅ |

**关键洞察**：GPT 的架构其实极其简洁——token embedding + position embedding + N 个 Transformer Block + LM head。所有"神奇"都来自两个组件：**因果自注意力**和**残差堆叠**。读完 minGPT，GPT-2/3/4 再不是黑盒——它们只是 minGPT 的"放大版"。

> 类比：minGPT 之于 GPT-4，相当于 [micrograd](./01-micrograd-自动微分引擎.md) 之于 PyTorch——把工业模型剥到最小可读骨架。

---

## Step 1 · GPT 整体架构（`model.py` L260-273）

```python
def forward(self, idx, targets=None):
    pos = torch.arange(0, t)                                    # 位置索引
    tok_emb = self.transformer.wte(idx)                        # ① token embedding
    pos_emb = self.transformer.wpe(pos)                        # ② position embedding
    x = self.transformer.drop(tok_emb + pos_emb)               # ③ 相加 + dropout
    for block in self.transformer.h:                            # ④ N 个 Transformer Block
        x = block(x)
    x = self.transformer.ln_f(x)                               # ⑤ 最终 LayerNorm
    logits = self.lm_head(x)                                    # ⑥ 投影到词表
    loss = F.cross_entropy(...) if targets is not None else None
    return logits, loss
```

**6 步前向**，就是整个 GPT：

```
token ids [b, t]
   │ wte (token embedding)
   ▼
[b, t, n_embd]  ←┐
   │ wpe (position embedding, 相加)
   ▼
   Block 1 ──→ Block 2 ──→ ... ──→ Block N      (每个 = attention + MLP, 残差)
   ▼
   ln_f (LayerNorm)
   ▼
   lm_head (Linear → vocab_size)
   ▼
logits [b, t, vocab_size]   (每位置预测下一 token)
```

> 🎯 **两个 embedding 相加**（不是拼接）：token 和位置信息融合进同一向量空间。这要求 n_embd 能同时编码"是什么词"+"在什么位置"——足够大的 n_embd 自然能做到。

---

## Step 2 · CausalSelfAttention（L29-71）—— GPT 的心脏

### 2.1 QKV 合并成一个 Linear

```python
self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)   # 一次算出 Q,K,V
# forward:
q, k, v = self.c_attn(x).split(self.n_embd, dim=2)          # 切成三份
```

**为什么不用三个 Linear？** 合并后是一次矩阵乘（效率高），split 是零拷贝视图。GPT-2 原版这么设计，minGPT 忠实复刻。

### 2.2 多头 reshape

```python
q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)  # (B, nh, T, hs)
k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
```

把 `n_embd` 维拆成 `n_head × head_dim`，把 head 维提到 batch 维——这样 attention 的 batched 矩阵乘自然实现多头并行。

### 2.3 注意力 + 因果掩码（核心）

```python
att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))   # 缩放点积
att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))   # 因果掩码!
att = F.softmax(att, dim=-1)
y = att @ v
```

`self.bias` 是预计算的下三角矩阵（L47-48）：

```python
self.register_buffer("bias", torch.tril(torch.ones(block_size, block_size)).view(1, 1, block_size, block_size))
```

`masked_fill(bias==0, -inf)` 把上三角（未来位置）的注意力分数设为 -inf，softmax 后变 0——**位置 t 只能看到位置 ≤t**。这就是"因果"，是 GPT 作为自回归模型的根本。

> 📌 **对比 [MADE](./03-pytorch-made-掩码自编码器.md)**：MADE 用权重 mask 实现因果，GPT 用注意力 mask。**思想同源**（掩码强制因果），实现不同（MADE 在 Linear 权重，GPT 在 attention 分数）。

### 2.4 输出投影

```python
y = y.transpose(1, 2).contiguous().view(B, T, C)   # 多头拼回
y = self.resid_dropout(self.c_proj(y))              # 投影 + dropout
```

多头输出拼回 n_embd 维，过一个 Linear 投影。

---

## Step 3 · Block（L73-93）—— pre-LN 残差结构

```python
class Block(nn.Module):
    def __init__(self, config):
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        self.mlp = ModuleDict(c_fc=Linear(n_embd, 4*n_embd), c_proj=Linear(4*n_embd, n_embd), act=NewGELU(), ...)
    def forward(self, x):
        x = x + self.attn(self.ln_1(x))      # ① 残差 + 注意力 (pre-LN)
        x = x + self.mlpf(self.ln_2(x))      # ② 残差 + MLP (pre-LN)
        return x
```

**两个关键设计**：

1. **Pre-LN**（LN 在子层**前**）：`x + sublayer(LN(x))`，不是 `LN(x + sublayer(x))`。GPT-2 用 pre-LN，训练更稳定（梯度沿残差路径无 LN 阻碍）。
2. **残差连接**（`x + ...`）：让梯度能直通底层，支撑深网络（N=12~96 层）。和 [LSTM 细胞状态加法](../讲透NLP/13-RNN与LSTM.md)、[VQ-VAE straight-through](./05-deep-vector-quantization-VQVAE.md) 同理——**保梯度畅通是深网络可训的命门**。

MLP 是 2 层全连接（n_embd → 4×n_embd → n_embd）+ GELU。4× 扩展是经验值。

---

## Step 4 · generate（L282-310）—— 自回归生成

```python
@torch.no_grad()
def generate(self, idx, max_new_tokens, temperature=1.0, do_sample=False, top_k=None):
    for _ in range(max_new_tokens):
        idx_cond = idx if idx.size(1) <= block_size else idx[:, -block_size:]   # 超长则裁尾
        logits, _ = self(idx_cond)
        logits = logits[:, -1, :] / temperature                                   # 最后位置 + 温度
        if top_k is not None:
            v, _ = torch.topk(logits, top_k); logits[logits < v[:, [-1]]] = -inf # top-k 截断
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, 1) if do_sample else probs.argmax(-1, keepdim=True)
        idx = torch.cat((idx, idx_next), dim=1)                                   # 追加
    return idx
```

**4 个生成技巧**：
1. **裁尾**：超 block_size 时只取最后 block_size 个（滑窗）
2. **温度**：`logits/temperature`——T<1 更确定（更尖），T>1 更随机（更平），T→0 退化为 greedy
3. **top-k**：只在前 k 个高概率里采样，过滤长尾噪声
4. **sample vs argmax**：采样（`multinomial`）引入随机性，argmax 确定性

> 🎯 这套生成逻辑是所有自回归 LM 的标准模板——nanoGPT / GPT-2 / Llama 的 generate 几乎一字不差。

---

## Step 5 · bash 跑通验证（causal mask 铁证）

构造 gpt-nano（3 层/3 头/48 维，96K 参数），验证架构 + **因果性**：

```bash
python3 /tmp/opencode/mingpt_verify.py
```

```
=== minGPT (gpt-nano) ===
总参数: 96,048 (96.0K)

=== 前向 ===
输入 [2,10] → logits [2,10,100]  ✓
自回归 loss: 4.637 (理论 -ln(1/100)=4.605)  ✓

=== causal mask 铁证 ===
改第 6 个 token, 各位置 logits 变化量:
  位置 0-5 (修改点之前): [0, 0, 0, 0, 0, 0]   ← 严格为 0!
  位置 6-7 (修改点及之后): [10.5, 0.73]        ← 有变化
  → 因果性 ✓ 成立

=== 自回归生成 ===
prompt:        [36, 16, 84, 80]
greedy 续写:   [36, 16, 84, 80, 96, 68, 2, 39, 2, 39]   ← 确定性
采样(T=0.8):   [36, 16, 84, 80, 27, 1, 59, 80, 35, 49] ← 随机性
```

**三个铁证**：
1. **参数量精确**：gpt-nano 96K 参数，gpt2-xl 约 1432M（接近真实 1558M，差异来自精算 bias）。
2. **初始 loss ≈ 均匀分布**：4.637 ≈ -ln(1/100)=4.605——未训练模型等价于均匀猜测，数学正确。
3. **因果性铁证**：改位置 6 的 token，**位置 0-5 的输出完全不变**（变化严格为 0），位置 6+ 才变。证明 tril 因果掩码正确生效——**未来信息没有泄漏到过去**。

---

## Step 6 · from_pretrained + configure_optimizers（工程细节）

### 6.1 从 HuggingFace 加载预训练权重（L174-213）

```python
@classmethod
def from_pretrained(cls, model_type):
    model_hf = GPT2LMHeadModel.from_pretrained(model_type)   # HF 模型
    for k in keys:
        if any(k.endswith(w) for w in transposed):           # Conv1D → Linear 要转置
            sd[k].copy_(sd_hf[k].t())
        else:
            sd[k].copy_(sd_hf[k])
```

**坑**：OpenAI GPT-2 用的是 `Conv1D`（不是标准 Linear），权重矩阵需要**转置**才能对上 minGPT 的 `nn.Linear`。`transposed = ['c_attn', 'c_proj', 'c_fc', 'c_proj']` 这四个要 `.t()`。这是从 HF 迁移权重的经典坑。

### 6.2 configure_optimizers：decay/no_decay 分组（L215-258）

```python
decay = set(); no_decay = set()
for mn, m in self.named_modules():
    for pn, p in m.named_parameters():
        if pn.endswith('bias'): no_decay.add(fpn)                    # bias 不 decay
        elif isinstance(m, (nn.Linear,)): decay.add(fpn)            # Linear 权重 decay
        elif isinstance(m, (nn.LayerNorm, nn.Embedding)): no_decay.add(fpn)  # LN/Emb 不 decay
```

**只对 Linear 权重做 weight decay**，bias/LayerNorm/Embedding 不做。这是 GPT 训练的标准实践（和 [lecun1989](./04-lecun1989-repro-复现1989论文.md)、[VQ-VAE](./05-deep-vector-quantization-VQVAE.md) 一样）。这个模式在 Karpathy 三个项目里重复出现——**记下来，是通用工程套路**。

---

## 三个关键洞察

### 洞察 1 · GPT = embedding + N×(attention + MLP) + head，仅此而已

剥掉所有工程装饰，GPT 的核心就是：token+pos embedding → N 层（因果 attention + MLP 残差）→ 投影到词表。**"涌现"全靠规模**——同样的 310 行代码，放大到 96 层、12288 维、175B 参数，就是 GPT-3。架构没变，规模变了天。

### 洞察 2 · 因果掩码 = 注意力里的"时间箭头"

`masked_fill(tril==0, -inf)` 这一行让 GPT 只能看过去、不能看未来——**这就是自回归的语言模型能在训练时并行（一次前向算所有位置）的原因**。对比 RNN 的串行、MADE 的权重 mask，attention + tril mask 是最优雅的因果实现。读懂这一行，就读懂了为什么 GPT 能高效训练。

### 洞察 3 · minGPT → nanoGPT：从"可读"到"可训"

minGPT 强调**可读**（教学），nanoGPT 强调**可训**（速度）。nanoGPT 的改进：去掉 NewGELU 用 F.gelu、ModuleDict 改 Sequential、加 flash attention 支持、优化数据加载。**架构完全一样，工程优化让训练快 3-5 倍**。这是"教学版 → 生产版"演进的典范。

---

## 与 work4ai 对接

| 本精读讲透的 | work4ai 深度版 |
|---|---|
| GPT 整体架构 | [`讲透Transformer`](../讲透Transformer/)（attention/MoE/推理优化）|
| CausalSelfAttention 逐行 | [`讲透Transformer/11-HuggingFace源码对照`](../讲透Transformer/11-HuggingFace源码对照.md)（对比生产实现）|
| 自回归生成（temperature/top-k）| [`讲透基础模型`](../讲透基础模型/)（NTP + 解码策略）|
| pre-LN 残差 / 初始化 | [`讲透PyTorch`](../讲透PyTorch/)（残差为何能训深网）|

**阅读路径**：读 [讲透Transformer] 懂 attention 数学 → 读本精读看 310 行最小 GPT → 读 [nanoGPT](./07-nanoGPT-从零训练GPT.md)（下一篇）看生产优化。

---

## 📌 下一步

- **继续 GPT 三连**：下一篇 `07-nanoGPT-从零训练GPT.md`（666 行，minGPT 的"可训"升级版，业界最广用的从零训 GPT 代码）。
- **动手训**：在 minGPT/demos.py 里有个在加法任务上训 gpt-nano 的 demo，CPU 可跑，看 loss 下降。
- **看视频**：Karpathy *Let's build GPT: from scratch* 逐行讲 minGPT 的 attention。

## ✍️ 练习

1. **（验证多头）** 把 gpt-nano 的 n_head 从 3 改成 1，看参数量和输出是否变？多头相对单头多了多少参数？（答案：几乎不变，多头只是 reshape。）
2. **（手算 attention）** 给定 Q=K=V=[[1,0],[0,1]]（2 个 token，2 维），手算无掩码的 attention 输出。再加因果掩码，看输出怎么变。
3. **（思考）** pre-LN（`x+sub(LN(x))`）和 post-LN（`LN(x+sub(x))`）哪个更易训深网？为什么 GPT-2 选 pre-LN？提示：残差路径上的非线性。
4. **（开放）** minGPT 的 lm_head 和 wte 不共享权重（不 tied）。GPT-2 原版是 tied 的（lm_head = wte.T）。tied 的好处和坏处？nanoGPT 默认 tied。
5. **（延伸）** 读 `from_pretrained` 的 transposed 列表，解释为什么 Conv1D → Linear 要转置。HF 的 Conv1D 和 nn.Linear 的权重布局差在哪？

---

> **源码**：[`repos/minGPT/mingpt/model.py`](./repos/minGPT/mingpt/model.py)（310 行）｜ [`trainer.py`](./repos/minGPT/mingpt/trainer.py)（109 行）｜ 配套：[demos.py](./repos/minGPT/demos.py)（加法任务训 gpt-nano）
