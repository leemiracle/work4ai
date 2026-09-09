# nanoGPT：读懂最小可运行 GPT

> 精读 `karpathy/nanoGPT`，源码来自 `/github-repos/references/nanoGPT/`。
> `model.py` 330 行就是一个完整可训练的 GPT（含 GPT-2 全部架构），`train.py` 336 行覆盖从数据加载到训练循环的全流程。
> 读完这两份文件，Transformer 就不再是黑盒——每个数学概念都能在代码里找到对应的那几行。

---

## 一、它到底干了什么

nanoGPT 的 `model.py` 实现了一个 **Decoder-only Transformer 语言模型**。给它一段 token 序列，它预测下一个 token。用同一套代码，既能从零训练一个 Shakespeare 文风生成器，也能加载 OpenAI 发布的 GPT-2 权重直接推理。

整个 GPT 由这几个零件拼成：

```
GPT
├── wte          词嵌入 (vocab → n_embd)
├── wpe          位置嵌入 (block_size → n_embd)
├── drop         Dropout
├── h[0..N]      N 个 Block（每层 = LayerNorm + Attention + LayerNorm + MLP）
│   └── Block
│       ├── ln_1 → attn(CausalSelfAttention)
│       └── ln_2 → mlp(MLP)
├── ln_f         最终 LayerNorm
└── lm_head      输出投影 (n_embd → vocab)
```

下面逐层拆开。所有代码片段都是**从仓库直接 Read 到的真实源码**，逐行注释。

---

## 二、GPTConfig：用 dataclass 当配置容器

```python
@dataclass
class GPTConfig:
    block_size: int = 1024       # 最大上下文长度
    vocab_size: int = 50304      # 词表大小，50257 向上取整到 64 的倍数
    n_layer: int = 12            # Transformer 层数
    n_head: int = 12             # 注意力头数
    n_embd: int = 768            # 嵌入维度
    dropout: float = 0.0         # dropout 概率
    bias: bool = True            # Linear/LayerNorm 是否带 bias
```

**为什么用 `@dataclass`**：Python 3.7+ 的数据类，自动生成 `__init__`、`__repr__`。比手写一堆 `self.x = x` 省事，又比传 dict 类型安全。

**`vocab_size = 50304` 的玄机**：GPT-2 真实词表是 50257，这里故意填到 50304。注释写着"padded up to nearest multiple of 64 for efficiency"。原因是 GPU 上矩阵运算对 64/128 的倍数维度更高效（向量化对齐）。这种"为硬件友好牺牲一点词表冗余"的工程取舍，是工业代码的典型细节。

---

## 三、LayerNorm：为什么不用 PyTorch 自带的

```python
class LayerNorm(nn.Module):
    """ LayerNorm but with an optional bias. PyTorch doesn't support simply bias=False """

    def __init__(self, ndim, bias):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(ndim))
        self.bias = nn.Parameter(torch.zeros(ndim)) if bias else None

    def forward(self, input):
        return F.layer_norm(input, self.weight.shape, self.weight, self.bias, 1e-5)
```

LayerNorm 的数学：对每个样本沿特征维归一化，再乘可学缩放 `weight`、加可学偏移 `bias`。

**为什么自己写一层**：注释说得很直白——PyTorch 的 `nn.LayerNorm` 不支持 `bias=False`。nanoGPT 后续实验发现"去掉 bias 更快更稳"（见 GPTConfig 的 `bias` 注释），所以要造一个能关 bias 的版本。

**第 7 行的小技巧**：`self.bias = ... if bias else None`。直接赋 None，`F.layer_norm` 收到 `bias=None` 就不加偏移。这种"参数可选"的处理避免了 if-else 分支。

**为什么不重新实现归一化数学**：`F.layer_norm` 内部是优化过的 CUDA kernel，手写 `(x - x.mean()) / x.std()` 会慢很多。这里复用底层函数，只在外面包一层参数管理。这是"站在巨人肩膀上做最小封装"的好范例。

---

## 四、CausalSelfAttention：Transformer 的心脏（逐行精读）

这是全文件最重要、也最难的一段。我们分构造函数和前向两部分看。

### 4.1 构造函数：QKV 投影合三为一

```python
def __init__(self, config):
    super().__init__()
    assert config.n_embd % config.n_head == 0
    # key, query, value projections for all heads, but in a batch
    self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd, bias=config.bias)
    # output projection
    self.c_proj = nn.Linear(config.n_embd, config.n_embd, bias=config.bias)
    # regularization
    self.attn_dropout = nn.Dropout(config.dropout)
    self.resid_dropout = nn.Dropout(config.dropout)
    self.n_head = config.n_head
    self.n_embd = config.n_embd
    self.dropout = config.dropout
    # flash attention make GPU go brrrrr but support is only in PyTorch >= 2.0
    self.flash = hasattr(torch.nn.functional, 'scaled_dot_product_attention')
    if not self.flash:
        print("WARNING: using slow attention. Flash Attention requires PyTorch >= 2.0")
        # causal mask to ensure that attention is only applied to the left in the input sequence
        self.register_buffer("bias", torch.tril(torch.ones(config.block_size, config.block_size))
                                    .view(1, 1, config.block_size, config.block_size))
```

**第 3 行的 assert**：`n_embd % n_head == 0`——嵌入维度必须能被头数整除，否则没法把维度均分给各头。这是个**前置不变量**，早 fail 比晚 fail 好。

**第 5 行是 GPT-2 的标志性优化**：`self.c_attn = nn.Linear(n_embd, 3 * n_embd)`。注意这里**用一个 Linear 同时算 Q、K、V**，而不是三个独立的 Linear。好处是单次大矩阵乘法比三次小矩阵乘法在 GPU 上快得多（kernel launch 开销低、内存访问连续）。前向时 `c_attn(x)` 输出 `(B, T, 3*n_embd)`，再 split 成三份。这是 GPT-2 原始实现的做法，注释里 `# ...for all heads, but in a batch` 点明了意图。

**第 7 行**：`c_proj` 是注意力输出后的线性映射，把多头拼接的结果投影回 `n_embd`。

**第 14-15 行的 Flash Attention 探测**：`self.flash = hasattr(torch.nn.functional, 'scaled_dot_product_attention')`。运行时检测 PyTorch 版本是否支持 Flash Attention。这是一种**优雅的向后兼容**：有就用快的内核，没有就退回手写慢版本。

**第 18-20 行的 causal mask 预计算**：`torch.tril(torch.ones(...))` 生成一个下三角矩阵（上三角为 0）。`.view(1, 1, block_size, block_size)` 前面补两个维度，方便后续广播。这个 mask 是"因果性"的保证——位置 i 只能看位置 ≤ i，看不到未来。用 `register_buffer` 注册，意味着它会跟着模型一起搬到 GPU、一起存 checkpoint，但不参与梯度更新。

### 4.2 前向：split → 分头 → 注意力 → 合头

```python
def forward(self, x):
    B, T, C = x.size() # batch size, sequence length, embedding dimensionality (n_embd)

    # calculate query, key, values for all heads in batch and move head forward to be the batch dim
    q, k, v  = self.c_attn(x).split(self.n_embd, dim=2)
    k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
    q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
    v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
```

**第 3 行**：`q, k, v = self.c_attn(x).split(self.n_embd, dim=2)`。一次大投影后，沿最后一维切成三段——这就是"QKV 合一投影"的拆包。

**第 4-6 行的 reshape 是全段最难的部分**，逐符号拆：

`k.view(B, T, n_head, C // n_head)` 把 `(B, T, n_embd)` 重塑成 `(B, T, n_head, head_dim)`，意思是"把嵌入维拆成 n_head 份，每份 head_dim 维"。

`.transpose(1, 2)` 交换第 1 和第 2 维，得到 `(B, n_head, T, head_dim)`。**这一步的目的是把"头"维度提到 batch 维旁边**，让每个头变成一个独立的"小 batch"。这样后续的 `q @ k^T` 会同时算所有头的注意力，无需 for 循环。

注释里 `(B, nh, T, hs)` 说明了最终形状：nh = n_head，hs = head_size。这种"用 einops 风格注释标出每维含义"的习惯，在读张量代码时极其有用。

### 4.3 注意力计算：两条路径

```python
    # causal self-attention; Self-attend: (B, nh, T, hs) x (B, nh, hs, T) -> (B, nh, T, T)
    if self.flash:
        # efficient attention using Flash Attention CUDA kernels
        y = torch.nn.functional.scaled_dot_product_attention(q, k, v, attn_mask=None, dropout_p=self.dropout if self.training else 0, is_causal=True)
    else:
        # manual implementation of attention
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)
        y = att @ v # (B, nh, T, T) x (B, nh, T, hs) -> (B, nh, T, hs)
```

**Flash 路径（第 3 行）**：一行搞定，`is_causal=True` 让内核自动处理因果 mask。这是 PyTorch 2.0+ 的 IO-aware 实现，比手写快几倍且省显存。

**手写路径（第 5-9 行）逐行讲，这是理解注意力数学的关键**：

**第 5 行**：`att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))`

- `k.transpose(-2, -1)` 把 K 的最后两维转置，`(B, nh, T, hs)` → `(B, nh, hs, T)`
- `q @ k^T` 得到 `(B, nh, T, T)`，这就是**未归一化的注意力分数矩阵**。每个元素 `[i,j]` 表示位置 i 对位置 j 的"关注度原始值"
- `* (1.0 / math.sqrt(k.size(-1)))` 是**缩放因子**，除以 head_dim 的平方根。为什么？因为点积的方差随维度增长，大维度会让 softmax 进入饱和区（梯度消失）。这个缩放把方差拉回 1 附近

**第 6 行**：`att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))`

把上三角（mask == 0 的位置）填成 `-inf`。这样 softmax 后这些位置的权重为 0——**位置 i 看不到位置 j > i**。`self.bias[:,:,:T,:T]` 是从预计算的下三角矩阵里切出当前序列长度 T 的子块。

**第 7 行**：`att = F.softmax(att, dim=-1)`。沿最后一维（key 维）做 softmax，把原始分数变成概率分布（每行和为 1）。

**第 8 行**：训练时对注意力权重做 dropout，随机丢弃一些注意力连接，防过拟合。

**第 9 行**：`y = att @ v`。用注意力权重对 V 加权求和，输出 `(B, nh, T, hs)`。每个位置的输出 = 所有位置 V 的加权平均，权重就是刚算的注意力。

**这段五行的本质**就是 Attention 论文里的公式 $\text{softmax}(\frac{QK^T}{\sqrt{d_k}})V$，只不过加了因果 mask 和 dropout。**如果你只能记住 Transformer 的一行代码，就是这一行 `att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))`。**

### 4.4 合头 + 输出投影

```python
    y = y.transpose(1, 2).contiguous().view(B, T, C) # re-assemble all head outputs side by side

    # output projection
    y = self.resid_dropout(self.c_proj(y))
    return y
```

**第 1 行**：`y.transpose(1, 2)` 把头维度移回去，`.contiguous()` 保证内存连续（view 要求），`.view(B, T, C)` 把多个头的输出拼接回 `n_embd` 维。注释"re-assemble all head outputs side by side"说得形象——各头结果像积木一样横向拼起来。

**第 3 行**：`c_proj` 把拼接结果做一次线性变换（让各头信息混合），再套残差 dropout。注意 dropout 作用在投影**之后**，这是 GPT-2 的惯例。

---

## 五、MLP：每个位置独立的两层全连接

```python
class MLP(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.c_fc    = nn.Linear(config.n_embd, 4 * config.n_embd, bias=config.bias)
        self.gelu    = nn.GELU()
        self.c_proj  = nn.Linear(4 * config.n_embd, config.n_embd, bias=config.bias)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        x = self.c_fc(x)
        x = self.gelu(x)
        x = self.c_proj(x)
        x = self.dropout(x)
        return x
```

结构极简：升维 4 倍 → GELU → 降维回去 → dropout。

**为什么先升 4 倍**：这是 Transformer 的标准设计。中间层扩大容量，让模型有更多"思考空间"做非线性变换，再压缩回原维度。4 倍是经验值，GPT-2、BERT 都用这个比例。

**为什么用 GELU 不用 ReLU**：GELU = `x * Φ(x)`（Φ 是标准正态的 CDF），比 ReLU 平滑，在 0 点可导。论文实践表明 GELU 在 NLP 任务上略优于 ReLU。`nn.GELU()` 直接调用 PyTorch 实现。

**重要观察**：MLP 对每个 token 位置独立作用，没有跨位置交互。跨位置的信息融合全靠前面的 Attention。这就是"Attention 做信息路由、MLP 做特征变换"的分工。

---

## 六、Block：Pre-LN 残差结构

```python
class Block(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.ln_1 = LayerNorm(config.n_embd, bias=config.bias)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = LayerNorm(config.n_embd, bias=config.bias)
        self.mlp = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x
```

整个 Block 的前向只有两行，但信息量极大。

**残差连接**：`x = x + f(x)`。`x` 直接跳过 `f`，保证梯度能沿捷径回传，深层网络才训得动。没有残差，12 层以上的 Transformer 几乎无法训练。

**Pre-LN 结构**：注意 LayerNorm 在子层**之前**（`self.attn(self.ln_1(x))`），不是之后。这叫 Pre-LN，对比原 Transformer 论文的 Post-LN。Pre-LN 训练更稳定，几乎不需要 warmup，是 GPT-2 之后的标配。

读这两行的方法：**先把 `self.ln_1(x)` 看成一个整体 `x'`，那么 `x = x + attn(x')` 就是标准的"残差注意力块"**。第二行同理。把归一化层"折叠"进子层，结构就清晰了。

---

## 七、GPT 主类：组装一切

### 7.1 构造：嵌入 + 层堆叠 + 权重共享

```python
def __init__(self, config):
    super().__init__()
    assert config.vocab_size is not None
    assert config.block_size is not None
    self.config = config

    self.transformer = nn.ModuleDict(dict(
        wte = nn.Embedding(config.vocab_size, config.n_embd),
        wpe = nn.Embedding(config.block_size, config.n_embd),
        drop = nn.Dropout(config.dropout),
        h = nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
        ln_f = LayerNorm(config.n_embd, bias=config.bias),
    ))
    self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
    # ... weight tying 警告注释 ...
    self.transformer.wte.weight = self.lm_head.weight # https://paperswithcode.com/method/weight-tying
```

**`nn.ModuleDict` vs 普通 dict**：用 `nn.ModuleDict` 而不是 `dict`，是为了让 PyTorch 自动注册子模块（参数收集、`.to(device)`、`state_dict` 都靠它）。普通 dict 里的模块会被忽略。

**`wte` 和 `wpe`**：词嵌入和位置嵌入都是 `nn.Embedding`，本质是可查表的大矩阵。位置嵌入用 `block_size` 行，每行是一个位置的向量。

**第 13 行的 Weight Tying**：`self.transformer.wte.weight = self.lm_head.weight`——**词嵌入矩阵和输出投影矩阵共享同一份权重**。直觉：输入端"token → 向量"的映射，和输出端"向量 → token 概率"的映射，语义上互为逆过程，共享参数既省内存（少一个 vocab×n_embd 的大矩阵）又有正则化效果。注释里给了 paperswithcode 链接，原始论文是 2016 年的"Using the Output Embedding to Improve Language Models"。

### 7.2 权重初始化：为什么 std=0.02

```python
    # init all weights
    self.apply(self._init_weights)
    # apply special scaled init to the residual projections, per GPT-2 paper
    for pn, p in self.named_parameters():
        if pn.endswith('c_proj.weight'):
            torch.nn.init.normal_(p, mean=0.0, std=0.02/math.sqrt(2 * config.n_layer))
```

**`self.apply(self._init_weights)`**：PyTorch 的 `apply` 会递归地对每个子模块调用 `_init_weights`，统一把 Linear 和 Embedding 初始化成 `normal(0, 0.02)`。

**为什么是 0.02**：GPT-2 论文的经验值。太大会让初始激活爆炸（深层累乘），太小会梯度消失。0.02 配合残差连接能在百层网络里保持激活稳定。

**第 4-5 行的特殊缩放**：对所有 `c_proj.weight`（残差路径的投影）额外除以 `sqrt(2 * n_layer)`。为什么？因为残差路径在每层累加，层数越多方差累积越大。除以 `sqrt(2*n_layer)` 把残差贡献的方差缩放到与层数无关——这是 GPT-2 论文附录里的 trick，让不同深度的模型训练动态更一致。

### 7.3 前向：嵌入 → 层 → 输出

```python
def forward(self, idx, targets=None):
    device = idx.device
    b, t = idx.size()
    assert t <= self.config.block_size, f"Cannot forward sequence of length {t}, block size is only {self.config.block_size}"
    pos = torch.arange(0, t, dtype=torch.long, device=device) # shape (t)

    # forward the GPT model itself
    tok_emb = self.transformer.wte(idx) # token embeddings of shape (b, t, n_embd)
    pos_emb = self.transformer.wpe(pos) # position embeddings of shape (t, n_embd)
    x = self.transformer.drop(tok_emb + pos_emb)
    for block in self.transformer.h:
        x = block(x)
    x = self.transformer.ln_f(x)

    if targets is not None:
        # if we are given some desired targets also calculate the loss
        logits = self.lm_head(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-1)
    else:
        # inference-time mini-optimization: only forward the lm_head on the very last position
        logits = self.lm_head(x[:, [-1], :]) # note: using list [-1] to preserve the time dim
        loss = None

    return logits, loss
```

**第 9 行**：`tok_emb + pos_emb`——词嵌入和位置嵌入**直接相加**（不是拼接）。因为两者同维，相加就是"把语义信息和位置信息混在同一向量里"。这是 Transformer 处理位置的标准方式。

**第 10-11 行**：N 个 Block 串行，每个 Block 处理一次。

**第 14-16 行的训练分支**：有 targets 时算完整 logits 和交叉熵损失。`logits.view(-1, V)` 把 `(b, t, V)` 摊平成 `(b*t, V)`，`targets.view(-1)` 摊平成 `(b*t,)`，这是 `cross_entropy` 要求的形状。`ignore_index=-1` 让 padding 位置不参与 loss。

**第 18-20 行的推理优化**：推理时（targets=None）**只对最后一个位置算 lm_head**。因为生成任务只关心"下一个 token"，前面位置的 logits 是浪费。`x[:, [-1], :]` 用列表索引 `[-1]` 而不是标量 `-1`，是为了**保留时间维**（形状 `(b, 1, n_embd)`），标量索引会丢掉这一维导致后面 reshape 出错。注释里特意提醒了这个细节。

### 7.4 configure_optimizers：为什么权重分两组

```python
def configure_optimizers(self, weight_decay, learning_rate, betas, device_type):
    param_dict = {pn: p for pn, p in self.named_parameters()}
    param_dict = {pn: p for pn, p in param_dict.items() if p.requires_grad}
    # 2D 及以上权重做 decay，1D（bias/layernorm）不 decay
    decay_params = [p for n, p in param_dict.items() if p.dim() >= 2]
    nodecay_params = [p for n, p in param_dict.items() if p.dim() < 2]
    optim_groups = [
        {'params': decay_params, 'weight_decay': weight_decay},
        {'params': nodecay_params, 'weight_decay': 0.0}
    ]
    ...
    optimizer = torch.optim.AdamW(optim_groups, lr=learning_rate, betas=betas, **extra_args)
```

**第 5-6 行的分组逻辑**：用 `p.dim() >= 2` 区分——矩阵参数（权重）做 weight decay，向量参数（bias、LayerNorm 的 weight/bias）不做。

**为什么这样分**：weight decay 是 L2 正则，惩罚大权重。但 bias 和 LayerNorm 参数本身就是"调节偏移"的，惩罚它们没意义，反而损害表达力。这是业界共识（GPT-2、ViT 都这么干）。

**第 12 行的 fused 探测**：`'fused' in inspect.signature(...)`——检测当前 PyTorch 是否支持 fused AdamW（C++ 融合实现，更快）。又是运行时优雅降级。

### 7.5 generate：自回归生成

```python
@torch.no_grad()
def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
    for _ in range(max_new_tokens):
        idx_cond = idx if idx.size(1) <= self.config.block_size else idx[:, -self.config.block_size:]
        logits, _ = self(idx_cond)
        logits = logits[:, -1, :] / temperature
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = -float('Inf')
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        idx = torch.cat((idx, idx_next), dim=1)
    return idx
```

**`@torch.no_grad()`**：生成时不需要梯度，装饰器关掉 autograd 省显存。

**第 3 行的裁剪**：序列超过 `block_size` 时只取最后 `block_size` 个 token，因为模型位置嵌入最多就这么多。

**第 5 行 temperature**：`logits / temperature`。temperature > 1 让分布更平坦（更随机），< 1 更尖锐（更确定）。除法是在 softmax 之前，等价于缩放 logits。

**第 6-8 行 top_k 采样**：只保留概率最高的 k 个候选，其余设 `-inf`。这避免采到长尾的烂 token，提升生成质量。`v[:, [-1]]` 取第 k 大的值作为阈值。

**第 10 行**：`torch.multinomial` 按概率分布采样一个 token。这就是"生成有随机性"的来源。

**第 11 行**：把新 token 拼到序列末尾，循环——这就是"自回归"：输出喂回输入，一步步往前生成。

---

## 八、`train.py` 关键片段

### 8.1 "穷人的 DataLoader"：裸 memmap

```python
def get_batch(split):
    if split == 'train':
        data = np.memmap(os.path.join(data_dir, 'train.bin'), dtype=np.uint16, mode='r')
    else:
        data = np.memmap(os.path.join(data_dir, 'val.bin'), dtype=np.uint16, mode='r')
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy((data[i+1:i+1+block_size]).astype(np.int64)) for i in ix])
    ...
    return x, y
```

**不用 DataLoader，直接 memmap**：数据预先编码成 `uint16` 的二进制文件（每个 token 两个字节），用 `np.memmap` 内存映射，按需读取，不全部载入内存。`x` 是 `data[i:i+block_size]`，`y` 是错位一格的 `data[i+1:i+1+block_size]`——**这就是"预测下一个 token"在数据层的样子：输入和标签错开一格**。

注释提到"每次重建 memmap 是为了规避内存泄漏"——这是 numpy memmap 的已知坑，作者特意贴了 StackOverflow 链接。读源码时遇到这种注释，说明作者踩过坑、留了记号。

### 8.2 梯度累积：用小显存模拟大 batch

```python
    for micro_step in range(gradient_accumulation_steps):
        if ddp:
            model.require_backward_grad_sync = (micro_step == gradient_accumulation_steps - 1)
        with ctx:
            logits, loss = model(X, Y)
            loss = loss / gradient_accumulation_steps # scale the loss to account for gradient accumulation
        X, Y = get_batch('train')
        scaler.scale(loss).backward()
```

**梯度累积的核心**：`loss = loss / gradient_accumulation_steps`，然后多次 forward+backward 累加梯度，最后只 step 一次。数学上等价于大 batch，但每次只占小 batch 的显存。

**为什么 `loss / N`**：因为 backward 的梯度会累加 N 次，除以 N 让累积后的总梯度等于"真实大 batch 的平均梯度"。

**DDP 的同步优化**：只在最后一个 micro_step 同步梯度（`require_backward_grad_sync = ...`），中间步骤各 GPU 各算各的，省通信开销。

### 8.3 学习率调度：warmup + cosine 衰减

```python
def get_lr(it):
    # 1) linear warmup for warmup_iters steps
    if it < warmup_iters:
        return learning_rate * (it + 1) / (warmup_iters + 1)
    # 2) if it > lr_decay_iters, return min learning rate
    if it > lr_decay_iters:
        return min_lr
    # 3) in between, use cosine decay down to min learning rate
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    assert 0 <= decay_ratio <= 1
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio)) # coeff ranges 0..1
    return min_lr + coeff * (learning_rate - min_lr)
```

**三段式调度**：
1. **Warmup**（线性升）：训练初期权重随机，大学习率会震荡。从 0 线性升到 `learning_rate`，给模型一个"适应期"。
2. **Cosine 衰减**：中段用余弦曲线从 `learning_rate` 缓慢降到 `min_lr`。余弦的好处是开始降得慢、中段快、末段又慢——符合训练后期需要精细调整的直觉。
3. **恒定 min_lr**：超过 `lr_decay_iters` 后固定在 `min_lr`，不再降。

**`coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))`**：decay_ratio 从 0 到 1 时，cos 从 1 到 -1，coeff 从 1 到 0。这是把 `[0, π]` 的余弦映射成 `[1, 0]` 的衰减系数，简洁优雅。

注释里提到"per Chinchilla"——指 DeepMind 的 Chinchilla 论文，建议 `lr_decay_iters ≈ max_iters`、`min_lr ≈ learning_rate/10`。这是经验法则。

### 8.4 梯度裁剪：防爆梯度

```python
    if grad_clip != 0.0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)
```

**`clip_grad_norm_`**：把所有梯度的全局范数缩放到不超过 `grad_clip`（默认 1.0）。训练中偶尔会出现 loss 突然飙升（坏 batch、数值不稳），梯度裁剪是"保险丝"，防止单步破坏权重。

**`scaler.unscale_` 在裁剪前**：fp16 训练时梯度被 GradScaler 放大了，裁剪前要先缩回真实尺度，否则阈值失真。

**`zero_grad(set_to_none=True)`**：PyTorch 推荐的清零方式，把 grad 设为 None 比 set 0 更省内存（省掉零张量的存储）。又一个细节优化。

---

## 九、一句话总结

> **GPT = 词嵌入 + 位置嵌入 → N 个 [Pre-LN + Causal Attention + Pre-LN + MLP] 残差块 → LayerNorm → 线性投影到词表。**

nanoGPT 的价值在于"零冗余"：每一行都对应论文里的一个概念，没有抽象层、没有配置地狱。读 `CausalSelfAttention.forward` 那 25 行，你能看到 `QK^T/√d → mask → softmax → @V` 的完整数学过程；读 `Block.forward` 两行，你看到残差和 Pre-LN 的工程取舍。

**下次你看到 HuggingFace 的 `GPT2LMHeadModel`，会知道它内部每个模块在做什么——因为它就是 nanoGPT 这套结构加了工程糖。**
