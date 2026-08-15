# 02 · minbpe — 329 行讲透整个 BPE 分词器

> **Andrej Karpathy · minbpe**（10k★）。Byte Pair Encoding（BPE）分词器的最小实现——`base.py` 165 行 + `basic.py` 74 行 + `regex.py` 164 行。GPT-2/4、Llama、tiktoken 用的分词算法，Karpathy 用几百行纯 Python 讲透了。
>
> 源码：``repos/minbpe/minbpe/`` ｜ 原仓库：https://github.com/karpathy/minbpe ｜ 视频：*Let's build the GPT Tokenizer*（2 小时逐行讲解）

---

## 0. 为什么 minbpe 是最优 BPE 教学项目

| 维度 | minbpe | tiktoken（OpenAI 生产级）|
|---|---|---|
| 语言 | **纯 Python** | Rust 内核 + Python 绑定 |
| 代码量 | **~330 行可读** | 几千行 + 预编译 merge 表 |
| 训练 | **支持**（从零训 BPE）| 只推理（merges 预烘焙）|
| 依赖 | 仅 `regex`（RegexTokenizer）/ 无（BasicTokenizer）| 重 |

**关键洞察**：BPE 算法本身极其简单——"反复合并最高频的相邻 pair"。生产级的复杂性全在**工程优化**（Rust 加速、正则切分、vocab 压缩），不在算法。读完 minbpe，GPT-4 的 tokenizer 再不是黑盒。

> 类比：minbpe 之于 tiktoken，相当于 [micrograd](./01-micrograd-自动微分引擎.md) 之于 PyTorch——把工业级实现剥到最小可训骨架。

---

## Step 1 · BPE 算法直觉：贪心合并最高频 pair

**问题**：LLM 要吃整数 token 序列，但文本是字符串。怎么把字符串切成 token？两种极端都不行：
- **字符级**（每字符一个 token）：序列太长，"hello" = 5 个 token，语义稀碎。
- **词级**（每词一个 token）：词表爆炸（英语几十万词），且遇生词就 OOV（out-of-vocabulary）。

**BPE 的折中**：从 256 个字节（byte-level，无 OOV）出发，**反复把出现最多的相邻 pair 合并成一个新 token**。合并到词表大小 V 为止。结果是"子词"（subword）——常见词整个是一个 token（如 `the`），罕见词切成几个子词 token（如 `tokenization` → `token` + `ization`）。

```
初始:  t h e   c a t   s a t   o n   t h e   m a t   (每字节一个 token)
合并1: th e   c a t   s a t   o n   th e   m a t      (t,h 高频→合并成 th)
合并2: the  c a t   s a t   o n   the  m a t          (th,e → the)
合并3: the  c a t  s a t  o n  the  m a t              ...直到词表满
```

> 🎯 **一句话**：BPE = "数据驱动的子词发现"——让语料自己决定哪些片段值得作为独立 token，而不是人工切词。

---

## Step 2 · 两个核心函数（`base.py` L13-41）

整个 BPE 的算法核心就这两个函数，加起来 30 行：

### 2.1 `get_stats` —— 数相邻 pair 频次

```python
def get_stats(ids, counts=None):
    """[1, 2, 3, 1, 2] -> {(1, 2): 2, (2, 3): 1, (3, 1): 1}"""
    counts = {} if counts is None else counts
    for pair in zip(ids, ids[1:]):        # 相邻两两配对
        counts[pair] = counts.get(pair, 0) + 1
    return counts
```

`zip(ids, ids[1:])` 是 Python 滑动窗口的惯用法——`[1,2,3]` 与 `[2,3]` zip 得 `[(1,2),(2,3)]`，即所有相邻 pair。

### 2.2 `merge` —— 把某 pair 替换成新 token

```python
def merge(ids, pair, idx):
    """ids=[1,2,3,1,2], pair=(1,2), idx=4 -> [4,3,4]"""
    newids = []
    i = 0
    while i < len(ids):
        if ids[i] == pair[0] and i < len(ids)-1 and ids[i+1] == pair[1]:
            newids.append(idx)            # 命中 pair → 用新 idx 替代
            i += 2                         # 跳过两个
        else:
            newids.append(ids[i]); i += 1
    return newids
```

线性扫描，命中 pair 就替换成新 token，跳两格；否则保留、进一格。

> 📌 **这两个函数就是 BPE 的全部算法**。剩下的是"迭代调用它们"的循环。

---

## Step 3 · `BasicTokenizer.train`（`basic.py` L20-49）—— 贪心合并循环

```python
def train(self, text, vocab_size, verbose=False):
    assert vocab_size >= 256
    num_merges = vocab_size - 256

    text_bytes = text.encode("utf-8")      # ① 文本 → bytes（0..255）
    ids = list(text_bytes)

    merges = {}                             # (int,int) -> int
    vocab = {idx: bytes([idx]) for idx in range(256)}
    for i in range(num_merges):
        stats = get_stats(ids)              # ② 数当前所有 pair 频次
        pair = max(stats, key=stats.get)    # ③ 选最高频 pair（贪心）
        idx = 256 + i                       # ④ 铸新 token：下一个可用 id
        ids = merge(ids, pair, idx)         # ⑤ 全部替换
        merges[pair] = idx                  # ⑥ 记录这次合并
        vocab[idx] = vocab[pair[0]] + vocab[pair[1]]   # vocab 派生
```

**6 步循环**，跑 `num_merges = V - 256` 次：
1. 文本 → utf-8 bytes（**byte-level，永远无 OOV**——任何 unicode 都能编码成 bytes）
2. 数相邻 pair 频次
3. **贪心**选最高频 pair
4. 铸新 token（id 从 256 递增）
5. 全部替换
6. 记录 merge + 派生 vocab（vocab[idx] = 两个子 token 的 bytes 拼接）

> 🤔 **为什么是贪心，不是动态规划？** 贪心不保证全局最优（合并了 `(e,s)` 后可能错过更好的 `(es,t)` 组合）——但 BPE 的妙处在于：**贪心的局部最优在前几步会自然引导出更好的组合**（合并 `es` 后，`est` 自然变高频，下一步就会被合并）。这是"简单规则涌现复杂结构"的典范。

---

## Step 4 · encode/decode 的关键不对称（最容易踩的坑）

这是 minbpe 最微妙、也是 BPE 最容易理解错的地方：

### 4.1 train 选**频次最高**的 pair；encode 选 **merge index 最低**的 pair

```python
# train（basic.py L35）: 选最高频
pair = max(stats, key=stats.get)

# encode（basic.py L64）: 选 merge index 最低（最早学到的）
pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
```

**为什么不一致？**

| 阶段 | 目标 | 选 pair 的依据 |
|---|---|---|
| `train` | 学词表 | **频次**（最高频的 pair 最值得合并）|
| `encode` | 把新文本切成 token | **merge index**（按学习的先后顺序应用合并）|

**关键**：encode 必须按 merge index 升序合并，才能**复现训练时的合并轨迹**，保证 `decode(encode(text)) == text`（可逆性）。

### 4.2 encode 的终止条件（basic.py L69）

```python
if pair not in self.merges:
    break      # 没有可合并的了
```

注释里 Karpathy 专门提醒一个 subtle bug：当所有 pair 都不在 merges 里时，`min` 会返回任意一个（因为 key 全是 `inf`），所以必须用 `if pair not in self.merges: break` 显式终止，否则会死循环或错误合并。

> 🎯 **铁律**：**train 是"建规则"，encode 是"按规则回放"**。两者的 pair 选择标准不同，但 encode 严格遵循 train 建立的 merge 顺序，所以可逆。

---

## Step 5 · byte-level + regex 预切分（RegexTokenizer）

`BasicTokenizer` 对整段文本的 bytes 直接做 BPE。但生产级 tokenizer（GPT-4）多了一层：**先用正则把文本切成"词块"，块内各自做 BPE**。

### 5.1 为什么要预切分

不切分的话，BPE 可能学出**跨词边界的荒谬 token**——比如 `" dog"`（空格+dog）和 `"cat"` 合并成 `" dogcat"`，这种 token 没用还污染词表。

GPT-4 的 split pattern（`regex.py` L19）：

```python
GPT4_SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
```

它把文本切成：单词（`'?(?:[sdmt]|ll|ve|re)` 缩写 / 字母串）、数字（最多 3 位一组）、标点、空白。**块内做 BPE，块间永不合**——这样 "tokenization" 能被切成 `token` + `ization`，但不会和前一个词粘在一起。

### 5.2 special tokens（`regex.py` L72, L123）

GPT 还有 `<|endoftext|>`、`<|im_start|>` 这类**特殊 token**——它们不是 BPE 学出来的，而是人工指定的固定 id，用于标记对话边界/结束符。`encode` 时先把它们从文本里 split 出来，分别处理。

---

## Step 6 · bash 跑通验证（铁证）

在真实 minbpe 上训练（`repos/minbpe/`），玩具语料跑 20 次合并：

```
=== BPE 训练: 20 次合并 (vocab 256→276) ===
merge 1/20: (101, 115) -> 256 (b'es')     had 9 occurrences
merge 2/20: (256, 116) -> 257 (b'est')    had 9 occurrences   ← es + t = est
merge 4/20: (108, 111) -> 259 (b'lo')     had 7 occurrences
merge 5/20: (259, 119) -> 260 (b'low')    had 7 occurrences   ← lo + w = low
merge 8/20: (262, 119) -> 263 (b'new')    had 6 occurrences
merge 9/20: (263, 258) -> 264 (b'newest ') had 6 occurrences  ← new + est = newest
merge 10/20: ... -> 265 (b'newest newest ')  ← 开始合并重复短语
...
merge 20/20: -> 275 (b'low low low low low lower')  ← 学到超长重复片段

=== 验证可逆性 ===
  'low'     → [260]              → 'low'     ✓
  'lowest'  → [260, 257]         → 'lowest'  ✓   ← low + est 子词组合
  'newest'  → [263, 257]         → 'newest'  ✓
  'lower'   → [260, 101, 114]    → 'lower'   ✓

=== 压缩率 ===
  原始 94 bytes → 编码后 9 tokens → 压缩率 9.6%
```

**复现命令**：
```bash
cd Karpathy经典代码精读
python3 /tmp/opencode/minbpe_verify.py    # 或见下方练习
```

**三个铁证**：
1. **子词涌现**：贪心合并自然学出 `es`→`est`→`low`→`newest` 这些语言学意义的子词，没人教它"est 是后缀"。
2. **子词组合性**：`lowest` = `[260(low), 257(est)]`——即使训练时没见过 `lowest` 整词，也能用 `low` + `est` 子词拼出，**这就是 BPE 解决 OOV 的原理**。
3. **可逆性**：encode→decode 完全还原（4/4 通过），证明 merge index 升序合并的正确性。

---

## 三个关键洞察

### 洞察 1 · 贪心涌现：简单规则长出复杂子词

BPE 只有一条规则"合并最高频 pair"，但跑 20 步就学出了 `est` 后缀、`low` 词根、甚至 `newest newest ` 重复短语。**这是"涌现"的微观典范**——局部的贪心选择，累积出有语言学结构的词表。无需任何语言学知识。

### 洞察 2 · train/encode 不对称保证可逆

train 按**频次**选 pair（建规则），encode 按 **merge index** 选 pair（回放规则）。这看似不一致，正是为了保证 `decode(encode(x)) == x`。**很多 BPE 教程讲错这点**（以为 encode 也按频次），导致实现不可逆。

### 洞察 3 · byte-level 是无 OOV 的根

从 256 个字节出发（不是从字符或词出发），任何 unicode 字符都能编码成 bytes。**BPE 永远不会遇到"未见字符"**——最坏情况退化到逐字节。这是 GPT 系列能处理任意语言、emoji、生僻字的根本原因。

---

## 与 work4ai 对接

| 本精读讲透的 | work4ai 深度版 |
|---|---|
| BPE 算法 + train/encode | `讲透NLP/02-词与token`（待写/未落盘）（token 化基础）|
| GPT-2/4 tokenizer 的内部 | [`讲透Transformer/13-Tokenizer`](../讲透Transformer/13-Tokenizer.md)（生产级 tokenizer）|
| byte-level / 子词 / OOV | [`讲透分词器/`](../notes/)（笔记，深化版）|
| 分词对 LLM 的影响（拼写/反转/计数）| [`讲透Prompt`](../讲透Prompt/)（"LLM 不会数 token"现象）|

**阅读路径**：读 [讲透NLP/02] 搞懂 token 化概念 → 读本精读看 330 行最小 BPE 实现 → 读 [讲透Transformer/13] 看 tiktoken 生产级差异。

---

## 📌 下一步

- **继续 Karpathy 系列**：下一篇 `03-pytorch-made-掩码自编码器.md`（144 行讲透 MADE，生成模型基础），对接讲透生成模型。
- **动手深读**：跑 minbpe 的 `gpt4.py`（用预训练 merges 编码真实 GPT-4 文本），对照 tiktoken 输出。
- **看视频**：Karpathy *Let's build the GPT Tokenizer*（2h 逐行讲 minbpe 全过程）。

## ✍️ 练习

1. **（手算）** 给文本 `"aaabdaaabac"`（SLP3 BPE 例），手算前 3 次 merge 会合并哪些 pair？对照 minbpe 跑出来验证。
2. **（验证可逆）** 对一段含 emoji + 中文 + 代码的混合文本（如 `"你好👋 print(x)"`），验证 `decode(encode(text)) == text`。byte-level 为什么能处理？
3. **（找不同）** `BasicTokenizer` vs `RegexTokenizer` 在同一文本上训练，词表差异在哪？用 `verbose=True` 对比前 10 个 merge。
4. **（思考）** 为什么 GPT-4 的 split pattern 把数字按"最多 3 位一组"切（`\p{N}{1,3}`）？这和 LLM"数不好大数"的现象有关吗？
5. **（开放）** BPE 是 1994 年的数据压缩算法，被 Sennrich 2015 引入 NMT。从"压缩"到"分词"，BPE 的本质目标变了吗？提示：都是"用最短的符号表示高频模式"。

---

> **源码**：``repos/minbpe/minbpe/base.py``（165 行）｜ ``basic.py``（74 行）｜ ``regex.py``（164 行）
