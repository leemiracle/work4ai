# 10 — 掩码语言模型：BERT

> 这是「讲透NLP」的双向编码器篇。如果说 GPT 是"从左往右一个字一个字往下写"的**生成者**，BERT 就是"把句子中间挖个洞、看着两边猜"的**理解者**。本篇讲透：为什么"完形填空"（cloze）让 BERT 双向、它和 GPT 在架构与目标上的根本差异、为什么 LLM 时代 GPT 赢了但 BERT 至今没死。
>
> 配套实验：`experiments/10_mlm_bert.py`（从零实现 4 层 mini-BERT，跑出三个反直觉发现）。对应 SLP3 第 10 章 *Masked Language Models*（2026-01-06 release）。

---

## 1. 直觉层：从"预测下一个词"到"完形填空"

### 1.1 NTP 的天花板：只能往左看

回忆 GPT 类模型（见 `../讲透基础模型/`）的预训练目标——**next token prediction (NTP，预测下一个词)**：

```
"那只在阳光下睡觉的 ___"  →  预测 "猫"
```

模型在第 $t$ 位预测第 $t{+}1$ 位时，**只能看到** $1..t$（因果掩码 causal mask，下三角）。这有三个后果：

1. **它是生成模型**：天然适合"接着往下写"。
2. **它单向**：处理"猫"这个字时，看不到后面"在阳光下睡觉"——而理解任务（给"猫"打 POS 标签、判断"猫"是不是命名实体）恰恰需要**右边的信息**。
3. **每个 token 都有监督信号**：长度 $L$ 的序列提供 $L-1$ 个预测，信号密集。

### 1.2 MLM：挖个洞，看着两边猜

BERT（**B**idirectional **E**ncoder **R**epresentations from **T**ransformers，Devlin et al. 2019）换了一个完全不同的目标——**masked language modeling (MLM，掩码语言模型)**，本质是 1953 年就有的心理学"完形测试（cloze task）"：

```
"那只 [MASK] 在阳光下睡觉"  →  预测 [MASK] = "猫"
```

随机选 **15%** 的 token 挖掉，让模型根据**左右两边**的上下文猜回来。

> **一句话比喻**：NTP 是"蒙住右眼往前走"（只能看左边），MLM 是"把句子中间擦掉一个字，睁大双眼看全句填空"。正因为要填空，模型**被迫**同时用左右上下文——这就是"双向 (bidirectional)"的来源。

### 1.3 为什么这彻底改变了模型用途

| | NTP（GPT/Claude/Llama） | MLM（BERT/RoBERTa） |
|---|---|---|
| 看的方向 | 只往左（causal） | 左右都看（bidirectional） |
| 擅长 | **生成**（写文章、聊天） | **理解**（分类、标注、检索） |
| 输出 | 一个接一个往外"吐"字 | 给每个 token 算一个**上下文向量** |
| 能否生成文本 | ✅ 强 | ❌ 基本不行（它不学"接着写"） |

SLP3 一句话点破：**"Masked language models are not used for generation. They are generally instead used for interpretative tasks."**（掩码语言模型不用于生成，而用于"理解/解释"类任务。）

> ⚠️ **关键认知**：BERT **不是一个聊天机器人**。它甚至不能完整地"说一句话"。它是一台**"给每个词算上下文向量"的机器**，这些向量再拿去做分类、打标签、算相似度。这是初学者最常见的误解。

---

## 2. 架构层：双向 Transformer 编码器

### 2.1 唯一的区别：删掉因果掩码

BERT 的 Transformer 和 GPT 的 Transformer **几乎一模一样**（multi-head self-attention + FFN + LayerNorm + 残差）。唯一的架构差别是：**attention 矩阵不加上三角掩码**。

GPT（causal，见 `../讲透基础模型/01`）：

$$
\text{head} = \text{softmax}\!\left(\text{mask}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)\right)V \tag{10.1}
$$

BERT（bidirectional，**删掉 mask**）：

$$
\text{head} = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V \tag{10.2}
$$

直观地看 attention 矩阵 $QK^\top$（$\mathbb{R}^{n\times n}$）：

```
GPT (causal):              BERT (bidirectional):
q1·k1  -∞    -∞    -∞      q1·k1 q1·k2 q1·k3 q1·k4
q2·k1 q2·k2  -∞    -∞      q2·k1 q2·k2 q2·k3 q2·k4
q3·k1 q3·k2 q3·k3  -∞      q3·k1 q3·k2 q3·k3 q3·k4
q4·k1 q4·k2 q4·k3 q4·k4    q4·k1 q4·k2 q4·k3 q4·k4
（上三角 = -∞，softmax 后变 0）   （全满，所有词互相看见）
```

就这一个差别。但后果是深远的：BERT 里**每个 token 都能 attend 到所有 token**（包括右边未来的 token），所以输出的 $h_i$ 是"看完整个句子后"对该 token 的理解。

### 2.2 BERT 与 XLM-RoBERTa 的规模

| | BERT-base | XLM-RoBERTa |
|---|---|---|
| 词表 | 30k（WordPiece） | 250k（SentencePiece Unigram） |
| 上下文窗口 $N$ | 512 | 512 |
| 模型维度 $d$ | 768 | 1024 |
| 层数 $L$ | 12 | 24 |
| 每层头数 $A$ | 12 | 16 |
| 参数量 | ~110M | ~550M |

注意：**550M 在 LLM 里小得可怜**（Llama 3 有 405B，大三个数量级）。掩码语言模型通常比因果语言模型小得多——因为它不追求"无所不能地生成"，只追求"把表示算好"。

### 2.3 三大架构对照：Encoder vs Decoder vs Encoder-Decoder

这是 NLP 神经架构最核心的一张表，务必记住：

| 维度 | **Encoder-only**（BERT） | **Decoder-only**（GPT/Claude/Llama） | **Encoder-Decoder**（T5/BART） |
|---|---|---|---|
| 注意力 | 双向（无 mask） | 因果（下三角 mask） | encoder 双向 + decoder 因果 |
| 预训练目标 | MLM（完形填空） | NTP（预测下一词） | denoising（破坏→重建，seq2seq） |
| 每个位置的输出 | 看完全句的上下文向量 | 只看左边的上下文向量 | encoder 看全句；decoder 逐字生成 |
| 能生成文本？ | ❌ 基本不能 | ✅ 最强 | ✅ 可以 |
| 擅长任务 | 分类、NER、句向量、检索 | 对话、写作、通用 | 翻译、摘要 |
| LLM 时代地位 | 被收编为"特征提取器" | **统治者** | 逐渐被 decoder-only 挤压 |

> **历史脉络**：2018 年 BERT 一出来在 GLUE 上"屠杀"全场， Encoder-only 风光了两三年。但 2020 年后 GPT-3 证明 decoder-only + NTP + 足够大就能"通吃"，Encoder-Decoder（T5）和 Encoder-only 逐渐被边缘化。今天的格局是 **decoder-only 一统天下**——但 BERT 类模型在"快速、便宜、不需要生成"的场景里仍然活得好好的（见 §9.3）。

---

## 3. 数学层：MLM 训练目标

### 3.1 主损失：随机 mask 15%，预测被 mask 的词

给定输入序列 $x = (x_1, \dots, x_n)$，随机选一个被掩码位置集合 $M$（BERT 选 **15%** 的 token）。把 $M$ 里的 token 替换成"被破坏的版本" $x_{\text{mask}}$，送入 Transformer，对每个被 mask 的位置 $i \in M$ 算一个对词表的概率分布，用交叉熵逼它接近真实词 $x_i$：

$$
\mathcal{L}_{\text{MLM}} = -\frac{1}{|M|}\sum_{i \in M} \log P(x_i \mid x_{\text{mask}})
$$

具体地，第 $L$ 层（最后一层）输出向量 $h_i^L$ 经过语言模型头（unembedding 层 $E^\top$ + softmax）得到预测：

$$
u_i = h_i^L E^\top, \qquad y_i = \text{softmax}(u_i) \tag{10.3,\,10.4}
$$

然后 $-\log y_i[x_i]$ 就是位置 $i$ 的损失。**只有被 mask 的 15% 位置参与损失，其余 85% 不参与**——这是 MLM 效率问题的根源（见反直觉发现 3）。

### 3.2 mask 策略：80% [MASK] / 10% 随机 / 10% 不变

被选中的 15% 位置，并不是统一换成 `[MASK]`，而是：

| 概率 | 操作 | 例子（原词 delicious） |
|---|---|---|
| **80%** | 换成特殊符号 `[MASK]` | `lunch was [MASK]` |
| **10%** | 换成词表里随机一个词 | `lunch was gasp` |
| **10%** | 保持原词不变 | `lunch was delicious` |

**为什么要这么别扭的三选一？** 直觉上"全换成 `[MASK]`"最干净，但有个致命问题：

> **训练-推理不一致 (train-inference mismatch)**：预训练时 80% 的被预测位置都长着 `[MASK]`；但**微调/推理时输入里根本没有任何 `[MASK]`**（你不会给一句带 `[MASK]` 的话去做情感分类）。如果模型只在"看到 `[MASK]`"时才会预测，那它在真实任务上就废了。

三选一就是来缓解这个不一致的：
- **80% `[MASK]`**：让模型学会"看到洞就填"。
- **10% 随机词**：强迫模型即使位置上是个**错的词**也要预测对的——逼它不能只依赖这个位置本身的输入，而要靠**上下文**。
- **10% 不变**：让模型也处理"位置上就是对的词"的情形，保持对真实输入的校准。

> 配套实验的**反直觉发现 1** 会用数字证明：即便做了这三选一，模型在"看到 `[MASK]`"时预测仍然**显著更准**——`[MASK]` 上瘾是真实存在的。这是 MLM 与生俱来的"原罪"。

### 3.3 辅助损失：NSP（下一句预测）——后来被证伪

BERT 原版还有第二个目标 **Next Sentence Prediction (NSP)**：给模型看一对句子，让它判断 B 是不是真的跟在 A 后面（50% 是真相邻，50% 第二句随机抽）。用 `[CLS]` 位置的输出做二分类：

$$
y = \text{softmax}(h_{\text{CLS}}^L \, W_{\text{NSP}}), \qquad W_{\text{NSP}} \in \mathbb{R}^{d\times 2}
$$

为了 NSP，BERT 的输入要拼成 `[CLS] A [SEP] B [SEP]`，还要加**段嵌入 (segment embedding)**（标记哪些 token 属于 A、哪些属于 B）。

**但 RoBERTa (Liu et al. 2019) 做了严格的对照实验，结论是：NSP 没用，去掉反而更好。** 现代的 encoder-only 基本都不用 NSP 了。NSP 是 BERT 设计里最常被批评的一个决定。

### 3.4 训练规模

- BERT 原版：~33 亿词（Wikipedia + BooksCorpus），约 40 个 epoch。
- 现代（RoBERTa/XLM-R）：大得多，XLM-R 在 100 种语言、~3000 亿 token 的 Common Crawl 上训练。

多语言有个额外难题：**词表怎么选才公平？**（英语网页多，按频率抽会让词表偏向英语罕见词）。SLP3 给出经验公式——对语言 $i$ 用 $\alpha$-平滑重采样（$\alpha=0.3$ 效果好）来**抬升低资源语言**：

$$
q_i = \frac{p_i^\alpha}{\sum_{j=1}^{N} p_j^\alpha}, \qquad p_i = \frac{n_i}{\sum_k n_k} \tag{10.5}
$$

不过多语言模型也有"**多语言诅咒 (curse of multilinguality)**"：语言太多时，每种语言的表现都会下降；而且多语言模型"**带口音**"——英语的语法会渗入低资源语言的表示。

---

## 4. 上下文嵌入 vs 静态嵌入

### 4.1 从"一个词一个向量"到"一个词随上下文变多个向量"

这是 BERT 带来的最大概念跃迁，也是它和 word2vec/GloVe（见 `05-词嵌入`）的本质区别：

| | **静态嵌入**（word2vec/GloVe） | **上下文嵌入**（BERT） |
|---|---|---|
| 一个词有几个向量？ | **1 个**（词类型 type） | **每个语境一个**（词实例 token） |
| "bank"（银行/河岸） | 同一个向量（混在一起） | 在"河 bank"和"银行 bank"里**向量不同** |
| 体现什么 | 词的**类型意义** | 词在**具体句子里的实例意义** |

形式化：BERT 第 $L$ 层对 token $x_i$ 的输出 $h_i^L$ 就是它的**上下文嵌入**——它编码了"$x_i$ 在 $x_1..x_n$ 这句话里的意义"。常用做法：取最后一层 $h_i^L$，或**把最后 4 层平均**（$\frac14(h_i^L+h_i^{L-1}+h_i^{L-2}+h_i^{L-3})$）。

### 4.2 词义消歧（WSD）：上下文嵌入天然解决多义

`mouse` 在"a mouse controlling a computer"（鼠标）和"a quiet animal like a mouse"（老鼠）里，BERT 给出的向量会**自动分到不同簇**——SLP3 图 10.6 把英语/德语的 `die`（骰子 / 死亡动词 / 德语冠词）的 BERT 嵌射影到 2D，三个意义清晰分开。最佳 WSD 算法就是简单的 **1-最近邻**：用上下文嵌入去和已知词义的向量比余弦，最近的那个就是答案。

$$
\text{sense}(t) = \arg\max_{s \in \text{senses}(t)} \cos(t, v_s) \tag{10.7}
$$

### 4.3 反直觉：BERT 的向量"挤在一个方向"（各向异性 anisotropy）

这里有个**很反直觉的坑**，也是配套实验发现 2 的核心：

> 直接取 BERT 最后一层向量算**余弦相似度**，你会发现**任意两个词的余弦都接近 1**——所有向量都挤在一个窄窄的方向上。这叫**各向异性 (anisotropy)**（Ethayarajh 2019）。

各向同性的模型里，随机两个向量的余弦期望应为 0；但 BERT 末期几个维度的方差巨大（"rogue dimensions 流氓维度"，Timkey & van Schijndel 2021），把所有向量拽到同一方向。后果：**直接用原始 BERT 向量算相似度，效果极差**——这正是 Sentence-BERT（Reimers & Gurevych 2019）要被发明出来的原因。

补救：把向量**标准化（z-score）**——减均值、除标准差，让流氓维度被压下去：

$$
\mu = \frac{1}{|C|}\sum_{x\in C} x, \quad \sigma = \sqrt{\tfrac{1}{|C|}\sum(x-\mu)^2}, \quad z = \frac{x-\mu}{\sigma} \tag{10.8\text{–}10.10}
$$

---

## 5. 微调（fine-tuning）：预训练表示怎么变成具体能力

预训练好的 BERT 是个"通用理解器"，要干具体活还得**微调**：在顶部加一个轻量"头 (head)"，用少量标注数据训练。SLP3 总结了三类任务：

### 5.1 序列分类（sequence classification）
整句话打一个标签（情感分析、主题分类）。用 `[CLS]` 的输出 $h_{\text{CLS}}^L$ 过一个分类头：

$$
y = \text{softmax}(h_{\text{CLS}}^L W_C), \qquad W_C \in \mathbb{R}^{d\times k}
$$

### 5.2 句对分类（sentence-pair）
两个句子打一个关系标签（自然语言推理 NLI：蕴含/矛盾/中立）。输入拼成 `[CLS] A [SEP] B [SEP]`，同样用 `[CLS]` 输出分类。

### 5.3 序列标注（sequence labeling）——以 NER 为例
给**每个 token** 打一个标签（命名实体识别 NER、词性标注 POS）。每个位置的 $h_i^L$ 过分类头：

$$
y_i = \text{softmax}(h_i^L W_K), \qquad t_i = \arg\max_k y_i \tag{10.12,\,10.13}
$$

NER 用 **BIO 标注**（B=实体开头，I=实体内部，O=非实体）：`Jane/B-PER Villanueva/I-PER of/O United/B-ORG ...`，把"找实体边界"变成"逐 token 分类"。

> 微调的精妙之处：**预训练学的是通用语言知识，微调只动最后一两层 + 新加的头**。少量标注数据就能让一个 110M 参数的模型学会新任务——这是 2018–2022 年 NLP 的标准范式（pretrain → finetune）。直到 LLM 用 prompting/instruction tuning 把它也收编了。

---

## 6. BERT 家族变体

| 模型 | 核心改动 | 解决了什么 |
|---|---|---|
| **RoBERTa** (2019) | 去掉 NSP、更大 batch、更多数据、动态 mask | 证明 BERT 原版"没训够"；成为 encoder-only 新标杆 |
| **ALBERT** (2019) | 跨层**参数共享** + 因式分解嵌入 | 参数量暴降（同样效果用 1/10 参数） |
| **DistilBERT** (2019) | 知识蒸馏（teacher→student，6 层） | 体积/速度 -40%，保留 ~97% 能力——**部署利器** |
| **ELECTRA** (2020) | 用"判别器"代替"生成器"：判断每个 token 是否被换过（RTD 任务） | 解决 MLM"只用 15% token"的效率问题，**全部 token 都有监督** |
| **SpanBERT** (2020) | mask 连续**片段**而非单 token | 更好地建模短语/跨度 |
| **XLM-RoBERTa** (2020) | 多语言、100 种语言、250k 词表 | 一个模型走天下（但有"多语言诅咒"） |
| **Chinese-RoBERTa-wwm** | 中文**全词掩码 (whole word mask)**：要 mask 就把一个汉字词整体 mask | 字级 BERT 会把"机"+"器"分别 mask，泄露信息；全词 mask 更合理 |

> **中文 BERT 的特殊性**：英文用 WordPiece 子词，天然边界清晰；中文是**字级**，"机器学习"四个字如果逐字随机 mask，模型可能只看到"机[MASK]学[MASK]"就把答案猜出来（因为汉字间冗余大）。全词掩码强制 mask 掉整个词（"机器学习"全 mask），逼模型真正理解，效果更好。

---

## 7. 代码：从零实现 4 层 mini-BERT

完整可跑代码在 `experiments/10_mlm_bert.py`。这里讲三个最关键的片段。

**(1) 双向 attention——只是不加上三角 mask**（对比 GPT 的 causal 版本）：

```python
class TransformerBlock(nn.Module):
    def __init__(self, d, nhead, ffn, causal=False):
        ...
        self.causal = causal
    def forward(self, x):
        att = (Q @ K.transpose(-1,-2)) / math.sqrt(d_head)
        if self.causal:                       # ← GPT 走这里
            att = att.masked_fill(triu_mask, float('-inf'))
        att = F.softmax(att, dim=-1)          # BERT: causal=False, 跳过 if，全矩阵可见
        ...
```

**(2) 80/10/10 掩码**——配套实验会证明 `[MASK]` 上瘾：

```python
def make_mlm_batch(ids):
    labels = ids.clone()
    prob = torch.full(ids.shape, 0.15); prob[special] = 0.0
    m = torch.bernoulli(prob).bool(); labels[~m] = -100
    masked = ids.clone(); r = torch.rand(ids.shape)
    masked[m & (r < 0.8)] = MASK_ID
    masked[m & (r >= 0.8) & (r < 0.9)] = randint(...)
    # 剩下 10% 不变
    return masked, labels
```

**(3) MLM 损失**——`ignore_index=-100` 让 85% 的位置不参与：

```python
logits = model(masked)
loss = F.cross_entropy(logits.reshape(-1, V), labels.reshape(-1), ignore_index=-100)
```

---

## 8. 实验的三个反直觉发现

跑 `python3 experiments/10_mlm_bert.py`，会打印下面三个"反直觉"结论。

### 🔬 发现 1：BERT 对 `[MASK]` 上瘾（训练-推理不一致）

在"看左右猜挖掉的词"任务上，比较模型在**三种输入**下的预测准确率：

| 被预测位置输入的是 | 准确率（典型） | 含义 |
|---|---|---|
| `[MASK]`（哨兵） | **~80%** | 训练时 80% 见到的情况——**最准** |
| 真实词（keep） | ~85% | 位置上就是答案，当然准 |
| **随机错词** | **~40%** | 位置上是个误导词，掉很多 |

**反直觉点**：模型在"看到 `[MASK]`"时显著比"看到随机词"时准。但**微调/推理时输入里一个 `[MASK]` 都没有**——每个位置都是真实词。也就是说，模型预训练时最擅长的那种"看到洞就填"的情形，在真实任务里**永远不出现**。这就是 §3.2 说的 train-inference mismatch，也是 80/10/10 设计要缓解（但无法消除）的原罪。

### 🔬 发现 2：未微调的 BERT 句向量，做相似度竟然不如 word2vec

用"同主题=相关、跨主题=不相关"造句对，算余弦，用 AUC 衡量"能否把相关/不相关分开"：

| 句向量来源 | AUC | 平均两两余弦（各向异性指标） |
|---|---|---|
| **静态嵌入平均**（word2vec 式） | **~0.95** | ~0.5 |
| **BERT 原始 mean-pool**（未微调） | **~0.65**（差！） | **~0.90**（高度各向异性） |
| **BERT 微调后 mean-pool** | **~0.98** | ~0.6 |

**反直觉点**：更"先进"的上下文嵌入，在**不做任何微调**时，做语义相似度**反而不如**最朴素的静态词向量平均！原因就是 §4.3 的**各向异性**——原始 BERT 向量全挤在一个方向，余弦都接近 1，分不开。**微调之后**它才反超静态嵌入。这正是 Sentence-BERT / SimCSE 这类工作存在的全部理由。

### 🔬 发现 3：MLM 比 NTP 收敛慢——每步只学 15% 的 token

同样大小的模型、同样语料、同样预训练步数（250 步），冻结编码器、用线性探针测主题分类准确率：

| 预训练方式 | 250 步后探针准确率 |
|---|---|
| **NTP**（每个 token 都有监督，~100%） | **~95%** |
| **MLM**（只有 15% token 有监督） | **~75%** |
| MLM 训到 ~1500 步 | ~95%（追上 NTP） |

**反直觉点**：NTP 反而更快收敛！因为一条长度 $L$ 的句子里，NTP 拿到 $L-1$ 个监督信号，MLM 只拿到 $0.15L$ 个——**MLM 的监督密度只有 NTP 的约 1/7**。SLP3 原文直言："only 15% of the input samples... are actually used for training weights... BERT and its descendents are inefficient."（只有 15% 的输入真正参与训练，BERT 们是低效的。）MLM 要追上 NTP，得多花 ~7 倍步数——这正是 ELECTRA（让全部 token 都有监督）被发明出来的动机。

---

## 9. 局限与争议

### 9.1 MLM 的结构性缺陷

1. **训练-推理不一致**（发现 1）：`[MASK]` 是预训练的"拐杖"，推理时却没有。80/10/10 只是缓解。
2. **监督稀疏**（发现 3）：每步只用 15% 的 token，数据效率低。ELECTRA 用判别式任务（每个 token 都判一次"是否被替换"）部分解决，但没成主流。
3. **不能生成**：架构上就没有自回归生成能力，做不了摘要/对话/续写。
4. **各向异性**（发现 2）：原始句向量做相似度很差，必须额外微调或后处理。

### 9.2 为什么 GPT/NTP 最终赢了？

根本原因：**scaling 对 NTP 友好，对 MLM 不友好。**

- NTP 是**密度场**（density estimation）任务，模型越大、数据越多，下一个词就预测得越准，能力持续上升——而且**每个 token 都贡献梯度**，训练信号极其密集。
- MLM 只监督 15% 的 token，扩大规模时"信号浪费"也被放大；且 `[MASK]` 这套机制在大模型里收益递减。

2020 年 GPT-3 证明：**decoder-only + NTP + 足够大 = 通吃一切理解任务**（分类、NER、NLI 全能用 prompting 做，不需要 BERT 式微调）。从此 NLP 主线从 "pretrain→finetune" 转向 "pretrain→prompt/instruction"。BERT 类模型在"最前沿研究"里基本退场。

### 9.3 BERT 至今没死的场景

但"研究退场"≠"工程退场"。在以下场景，BERT 类模型**仍然是首选**：

| 场景 | 为什么还用 BERT |
|---|---|
| **句向量 / 语义检索** | Sentence-BERT、SimCSE 把 BERT 蒸成高质量向量库，比跑大模型便宜几个数量级（见 `../讲透RAG/`） |
| **文本分类** | 情感、意图识别——几十毫秒推理，准得够用 |
| **NER / 序列标注** | 抽实体、打标签——BERT 微调仍是工业标配 |
| **句法分析** | 依存/成分句法，双向信息很关键 |
| **端侧 / 低延迟** | DistilBERT 几十 MB，手机能跑；大模型做不到 |
| **批量特征提取** | 给百万文档算 embedding 建索引，BERT 比 LLM 便宜太多 |

> 一句话：**LLM 赢了"能力上限"，BERT 赢了"性价比下限"。** 当你不需要生成、只需要"理解+打标签"，且要快、要便宜、要可批量——BERT 类模型依然是最优解。

---

## 📌 下一步

- 想看 BERT 怎么被用来做检索/RAG → `11-信息检索与RAG.md`（导引到 `../讲透RAG/`）
- 想理解 GPT 那一侧（为什么 NTP 赢了）→ `../讲透基础模型/01-Transformer与注意力.md`、`../讲透基础模型/00-为什么预测下一个词能产生智能.md`
- 想看 attention 的深度版 → `../讲透Transformer/`
- 想看序列标注（NER/POS）的完整版 → `17-序列标注-POS与NER.md`
- 想动手调一个真 BERT → HuggingFace `transformers`：`AutoModel.from_pretrained('bert-base-chinese')`

---

## ✍️ 练习

**练习 10.1**（动手）把 `10_mlm_bert.py` 里的 mask 比例从 15% 改成 50%，再改成 5%。观察：mask 太多会发生什么（上下文被破坏太多）？太少又怎样（信号更稀疏）？哪个收敛最快？

**练习 10.2**（思考）ELECTRA 不预测被 mask 的词，而是判断"每个 token 是不是被偷偷换过"。为什么这个任务能让**全部** token 都参与训练？它和 MLM 的监督密度差多少倍？

**练习 10.3**（动手）在发现 2 里，对原始 BERT 句向量做 §4.3 的 z-score 标准化（减均值除标准差），再算 AUC。看看各向异性被压下去后，AUC 能涨多少。

**练习 10.4**（思考）有人主张"既然 NTP 通吃了，BERT 可以扔了"。请反驳：举出 3 个 LLM 在工程上不如 BERT 的场景，并说明为什么。

**练习 10.5**（挑战）用 HuggingFace 加载 `hfl/chinese-roberta-wwm-ext`，对一句中文做 MLM 预测（手动把某字换成 `[MASK]`），看 top-5 预测。再换成普通 `bert-base-chinese` 对比——全词掩码训练出的模型，预测"被挖掉一个字的词"时表现有何不同？

---

> 配套实验：`experiments/10_mlm_bert.py`。姊妹章节：`05-词嵌入-word2vec与GloVe.md`（静态嵌入）、`../讲透基础模型/01-Transformer与注意力.md`（attention 深度版）、`11-信息检索与RAG.md`（BERT 句向量的应用）。
