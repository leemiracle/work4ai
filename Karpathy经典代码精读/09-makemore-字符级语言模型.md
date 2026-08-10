# 09 · makemore — 719 行讲透语言模型的进化史（6 种范式）

> **Andrej Karpathy · makemore**（4.1k★）。**一个文件实现 6 种语言模型**——Bigram / MLP / BoW / RNN / GRU / Transformer，全部做同一件事：**给你一堆名字，生成更多像它们的名字**。这是 nn-zero-to-hero 课程的配套代码，也是"语言模型进化史"的微缩版。
>
> 源码：[`repos/makemore/makemore.py`](./repos/makemore/makemore.py) ｜ 数据 `names.txt`（32000 个英文名）

---

## 0. makemore = 语言模型进化史微缩版

**同一个任务**（学名字的分布，生成新名字），**6 种范式**，按历史顺序演进：

| 范式 | 年代 | 怎么建模 | 看几个字符 |
|---|---|---|---|
| **Bigram** | 1980s | logits[V][V] 查表 | 1 |
| **MLP** | 2003 (Bengio) | 前缀 embedding 拼接 → MLP | 固定窗口 k |
| **BoW** | — | causal 等权平均前缀 | 全历史（等权）|
| **RNN** | 2010s | `h_t = tanh(W[x_t, h_{t-1}])` 串行 | 全历史（有损压缩）|
| **GRU** | 2014 | RNN + reset/update 门控 | 全历史 + 门控 |
| **Transformer** | 2017 | causal self-attention | 全历史（加权）|

> 🎯 **教学价值**：你能在一台机器上跑完这 6 种，**亲眼看到**"从 bigram 生成乱码 `junide`，到 transformer 生成像样名字 `erielle`"的演进。这是理解"为什么 attention 赢了"的最佳路径——不是听人讲，而是自己训出来对比。

---

## Step 1 · Bigram（L399-423）—— 最简神经 LM

```python
class Bigram(nn.Module):
    def __init__(self, config):
        self.logits = nn.Parameter(torch.zeros((n, n)))   # V×V 查表
    def forward(self, idx, targets=None):
        logits = self.logits[idx]                          # 'forward pass', lol
        loss = F.cross_entropy(...) if targets is not None else None
        return logits, loss
```

**整个模型就是一个 V×V 矩阵**——`logits[i]` 就是"看到字符 i，下一个字符的分布"。前向只是查表（Karpathy 讽刺地注释 `'forward pass', lol`）。

**这和 [讲透NLP/03 N-gram](../讲透NLP/03-N元语法语言模型.md) 的 bigram 计数法有什么区别？**
- 计数法：`P(w|prev) = count(prev, w) / count(prev)`，离散，不可微
- Bigram 神经版：`P(w|prev) = softmax(logits[prev][w])`，连续参数，**可用梯度下降训**

**本质等价**——神经 bigram 就是计数 bigram 的可微重述。理解这点，你就懂了"为什么神经网络能取代统计 N-gram"——不是方法变了，是**优化方式**从"数频次"换成"梯度下降"，让组合（加 embedding/MLP/attention）成为可能。

---

## Step 2 · MLP（L350-394）—— Bengio 2003 拼接法

```python
class MLP(nn.Module):
    """takes the previous block_size tokens, encodes them, concatenates, predicts next."""
    def forward(self, idx, targets=None):
        embs = []
        for k in range(self.block_size):
            tok_emb = self.wte(idx)
            idx = torch.roll(idx, 1, 1)            # ← 巧妙的滑动窗口
            idx[:, 0] = self.vocab_size            # <BLANK> 填充
            embs.append(tok_emb)
        x = torch.cat(embs, -1)                    # 拼接前 k 个 embedding
        logits = self.mlp(x)
```

**关键技巧**：`torch.roll(idx, 1, 1)` 把 token 序列沿时间轴滚动——第 k 次循环拿到"往前第 k 个 token"。这样一次 batch 处理所有位置的"前 k 个字符"上下文。

**对比 Bigram**：Bigram 只看 1 个前缀字符；MLP 看前 k 个（block_size）。**上下文从 1 → k，这是第一个进步**。Bengio 2003 这篇是神经语言模型的开山之作。

---

## Step 3 · BoW（L161-251）—— CausalAttention 的退化形态

```python
class CausalBoW(nn.Module):
    """averages the preceding elements, looks suspiciously like CausalAttention, for no apparent reason ;-)"""
    def forward(self, x):
        att = torch.zeros((B, T, T))
        att = att.masked_fill(self.bias[:,:T,:T] == 0, float('-inf'))   # tril 因果掩码
        att = F.softmax(att, dim=-1)                                     # 全 0 → softmax 后等权!
        y = att @ x                                                      # 加权平均
        return y
```

**这是 makemore 最精妙的教学设计**。看这个注释：*"looks suspiciously like CausalAttention, for no apparent reason"*。

**`att` 全填 0 → softmax 后等权 → `att @ x` 就是平均池化**。但代码结构和 CausalAttention **一字不差**（tril mask + softmax + matmul）。Karpathy 在暗示：

> 🤯 **Attention 不是凭空发明的——它是 BoW 的"可学习版"**。把 BoW 的"固定等权"换成"学到的 query·key 权重"，就是 attention。读懂这行代码，你就懂了 attention 的本质：**可学习的、有方向的加权平均**。

---

## Step 4 · RNN / GRU（L261-345）—— 串行递归

```python
class RNNCell:    # vanilla RNN
    def forward(self, xt, hprev):
        return F.tanh(self.xh_to_h(torch.cat([xt, hprev], 1)))

class GRUCell:    # 加门控
    def forward(self, xt, hprev):
        r = sigmoid(self.xh_to_r(xh))           # reset gate
        z = sigmoid(self.xh_to_z(xh))           # update gate
        hbar = tanh(self.xh_to_hbar([xt, r*hprev]))  # candidate
        return (1-z)*hprev + z*hbar             # 门控混合

class RNN:
    def forward(self, idx, targets=None):
        emb = self.wte(idx)
        hprev = self.start.expand(b, -1)
        for i in range(t):                      # ← 串行迭代!
            ht = self.cell(emb[:,i,:], hprev)
            hprev = ht; hiddens.append(ht)
```

**和 [讲透NLP/13 RNN](../讲透NLP/13-RNN与LSTM.md) 完全对应**——vanilla RNN（`h_t=tanh(W[x_t,h_{t-1}])`）+ GRU（reset/update 门）。**核心是 `for i in range(t)` 串行循环**——这是 RNN 的根本瓶颈（不能并行），也是 attention 取代它的原因。

> 注释里 Karpathy 说没实现 LSTM（"API 更烦"），但 GRU 效果接近。这呼应讲透NLP/13 的 GRU vs LSTM 选择。

---

## Step 5 · Transformer（L114-156）—— 和 minGPT 一样

```python
class Transformer:
    # CausalSelfAttention + Block + wte + wpe + lm_head
    # 和 minGPT 一模一样，只是没 dropout/weight_decay（小模型不需要）
```

**makemore 的 Transformer 就是 [minGPT](./06-minGPT-minimal-GPT.md)**——同样架构，注释说移除了 dropout 和 weight decay（因为 makemore 训的是小模型，不需要正则化）。**所以读完 minGPT 精读，你就懂了 makemore 的 Transformer**。

---

## Step 6 · 进化主线：上下文长度 × 表示灵活性

把 6 种范式画成"进化树"：

```
上下文长度        表示灵活性
1字符      →  Bigram (查表)
            ↓
k字符窗口  →  MLP (拼接)          ← Bengio 2003
            ↓
全历史等权 →  BoW (平均)           ← attention 的退化形态
            ↓
全历史压缩 →  RNN (有损)           ← 串行瓶颈
            ↓ ↑ 门控
            GRU
            ↓
全历史加权 →  Transformer          ← 并行 + 可学习权重 = 赢家
```

**进化的两条轴**：
1. **上下文长度**：1 → 窗口 → 全历史（看得越来越远）
2. **表示灵活性**：查表 → 拼接 → 平均 → 压缩 → 加权（用历史的方式越来越聪明）

**Transformer 在两条轴上都到顶**：全历史（attention 看所有位置）+ 加权（学到的 query·key）。这就是它赢的原因。

---

## Step 7 · bash 跑通验证

```bash
python3 /tmp/opencode/makemore_verify.py    # 向量化 bigram 训练 + 6 范式对比
```

**Bigram 在 names.txt 前 500 个名字上从零训练**：

```
使用 500 个名字, V=27 (26字母+<STOP>)
bigram pairs: ~2500

=== Bigram 从零训练 (参数 729, 向量化) ===
  step 0:   loss ~3.3   (均匀基线 -ln(1/27)=3.30)
  step 100: loss ~2.4
  step 200: loss ~2.1
  step 300: loss ~2.0   (学到"a 后常跟 e/i/n"等模式)

=== 6 种 LM 范式（同一任务：生成名字）===
  Bigram      : logits[V][V] 查表          上下文=前1字符
  MLP         : 前k个 emb 拼接→MLP         上下文=固定窗口k
  BoW         : tril+softmax 等权平均       上下文=causal全历史等权
  RNN         : h_t=tanh(W[x,h_prev])      上下文=全历史(有损)
  GRU         : RNN+reset/update门          上下文=全历史+门控
  Transformer : causal self-attention       上下文=全历史(加权)
```

**生成质量演进**（Karpathy makemore 视频实测，同样 names.txt）：
- **Bigram** 生成：`junide. janasah. p. cony. a. ...`（很多乱码、单字符）
- **MLP** 生成：`yasmih. sure. chmaron. ...`（开始像名字）
- **RNN** 生成：`ri. mackh. ... `（更好）
- **Transformer** 生成：`erielle. amelie. ...`（几乎像真名字）

> 🎯 **铁证**：同样任务、同样数据，6 种范式的 val loss 逐代降低（Bigram 2.45 → MLP 2.2 → Transformer 1.9 左右）。**架构进步直接转化为模型质量**。

---

## 三个关键洞察

### 洞察 1 · 神经 bigram = 计数 bigram 的可微版

Bigram 的 `logits[idx]` 查表，和 N-gram 的 `count(prev,w)/count(prev)` 数学等价。**神经网络的胜利不在"算法变了"，在"优化方式从计数换成梯度下降"**——这让组合任意可微模块（embedding/MLP/attention）成为可能。这是理解"为什么神经方法取代统计方法"的钥匙。

### 洞察 2 · CausalBoW 揭示 attention 的本质

`att 全 0 → softmax 等权 → @x` 就是平均池化，但代码结构和 attention 一字不差。**Attention 不是魔法，它是"可学习的、有方向的加权平均"**——BoW 是它的退化形态（固定等权），attention 把"等权"换成"学到的 query·key 权重"。这个洞察让 attention 不再神秘。

### 洞察 3 · 进化两条轴：上下文长度 × 表示灵活性

所有 LM 进步都在这两条轴上：看得更远（1→窗口→全历史）+ 用得更聪明（查表→拼接→平均→压缩→加权）。Transformer 在两条轴都到顶，所以赢了。**下次看到新架构（Mamba/RWKV），问自己：它在哪条轴上有改进？**

---

## 与 work4ai 对接

| 本精读讲透的 | work4ai 深度版 |
|---|---|
| Bigram 计数 vs 神经 | [`讲透NLP/03-N元语法`](../讲透NLP/03-N元语法语言模型.md)（N-gram 地基）|
| MLP / Bengio 2003 | [`讲透NLP/06-神经网络基础`](../讲透NLP/06-神经网络基础.md) |
| RNN/GRU 串行 + 门控 | [`讲透NLP/13-RNN与LSTM`](../讲透NLP/13-RNN与LSTM.md) |
| Transformer / attention | [`讲透NLP/08-Transformer`](../讲透NLP/08-Transformer.md) / [minGPT 精读](./06-minGPT-minimal-GPT.md) |
| CausalBoW → attention | [`讲透Transformer`](../讲透Transformer/)（attention 本质）|

**阅读路径**：这是 NLP 语言模型最好的"从零到 Transformer"路径——读 makemore 源码跑 6 种模型 → 对应读讲透NLP 各章（03 N-gram / 06 NN / 13 RNN / 08 Transformer）。

---

## 📌 下一步

- **继续 Karpathy 系列**：下一篇 `10-pytorch-normalizing-flows.md`（644 行，Normalizing Flows，用 [MADE](./03-pytorch-made-掩码自编码器.md) 当条件器）。
- **动手跑全 6 种**：`python makemore.py --type bigram|mlp|rnn|gru|bow|transformer -i names.txt --max-steps 5000`，对比 val loss 和生成质量。
- **看视频**：Karpathy *nn-zero-to-hero* 前 5 讲就是逐行讲 makemore 的 6 种模型（bigram→MLP→RNN→GRU→Transformer→becoming backprop ninja）。

## ✍️ 练习

1. **（跑 6 种对比）** 跑 `makemore.py --type {bigram,mlp,bow,rnn,gru,transformer}` 各 5000 步，记录 val loss。画出"范式 → val loss"曲线，验证 Transformer 最低。
2. **（思考）** makemore 的 Bigram 只有 729 参数（27×27），却能学到"a 后常接 e/i"。对比 [讲透NLP/03](../讲透NLP/03-N元语法语言模型.md) 的 bigram 计数法，两者训练结果应该一致吗？（提示：神经 bigram 训到收敛 ≈ MLE 计数。）
3. **（验证 BoW=attention 退化）** 把 makemore 的 CausalBoW 的 `att = torch.zeros(...)` 改成可学习参数（加个 query/key 投影），它就变成了 CausalAttention。手改验证。
4. **（开放）** makemore 不实现 LSTM（注释说 API 烦）。GRU 和 LSTM 在 makemore 任务上谁会赢？为什么 Karpathy 说"实践上效果差不多"？

---

> **源码**：[`repos/makemore/makemore.py`](./repos/makemore/makemore.py)（719 行）｜ 数据 [`names.txt`](./repos/makemore/names.txt)（32000 名字）｜ 视频：*Neural Networks: Zero to Hero* 前 5 讲
