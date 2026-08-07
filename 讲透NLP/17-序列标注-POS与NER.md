# 17 — 序列标注：词性标注 (POS) 与命名实体识别 (NER)

> 给输入序列里的**每一个词**打一个标签——这是 NLP 最基础的结构化任务。
> 从 1980 年代的 HMM 到 2018 年的 BERT，方法换了四代，但任务定义没变。
>
> 这一章你会看到：为什么 HMM 的"转移概率"在整体准确率上贡献不如发射概率，却在未知词（OOV）上是唯一的救命稻草；为什么 CRF 用"全局归一化"解决了 MEMM 的 label bias；以及为什么 BERT 把前面所有方法都收编了。

**配套实验**：`experiments/17_pos_hmm.py`（HMM POS tagger 从零实现 + Viterbi + 消融实验）

---

## 1. 直觉：给每个词打标签

### 1.1 什么是序列标注

**序列标注 (sequence labeling)**：输入一个词序列 $w_1, w_2, \ldots, w_n$，输出一个**等长**的标签序列 $y_1, y_2, \ldots, y_n$。

```
输入:  Janet  will   back   the    bill    .
标签:  NNP    MD     VB     DT     NN      .
```

每个词对应一个标签，输入输出长度相同。这与文本分类（整个文本一个标签）和序列到序列（输入输出长度不同）都不同。

两个最经典的序列标注任务：

| 任务 | 全称 | 标签是什么 | 例子 |
|------|------|-----------|------|
| **POS tagging** | Part-of-Speech Tagging（词性标注） | 名词 / 动词 / 形容词 / 介词 …… | "race" → VB 或 NN？ |
| **NER** | Named Entity Recognition（命名实体识别） | 人名 / 地名 / 机构名 / …… | "Beijing" → B-LOC |

### 1.2 POS Tagging：每个词的语法角色

词性标注就是给句子里的每个词标上**语法类别**。英语约 **45 类**（Penn Treebank 标签集）。

核心难点是**歧义 (ambiguity)**——同一个词在不同上下文有不同词性：

```
词 "back":
  "I will back the bill"        → VB  (动词：支持)
  "the back of the house"       → NN  (名词：背面)
  "go back home"                → RB  (副词：向后)
  "the back door"               → JJ  (形容词：后面的)
  "she backed the car"          → (backed = VBD)
```

实验脚本中的歧义句解码示例——HMM 通过**上下文**（转移概率）成功消歧：

```
句子 : she will back the bill .
金标 : PRP MD VB  DT  NN  .
预测 : PRP MD VB  DT  NN  .   ✓
```

"back" 在 "will" (MD) 之后，转移概率 $P(\text{VB} \mid \text{MD})$ 很高（情态动词后接动词），所以标对了 VB。

### 1.3 NER：找出文本里的"谁/哪里/什么机构"

命名实体识别是从文本中识别出**专有名词**并分类：

```
输入:  Apple   is   based   in   Cupertino  ,   California  .
标签:  B-ORG   O    O       O    B-LOC      O   B-LOC       .
```

常见实体类型（CoNLL 标准）：
- **PER**：人名（Barack Obama）
- **ORG**：机构名（Apple, United Nations）
- **LOC / GPE**：地名 / 地缘政治实体（Beijing, Pacific Ocean）
- **MISC**：其他（Olympics, German——派生词）

NER 比 POS 更难：实体是**开放集合**（新的人名、公司名每天都在产生），而 POS 标签集是**封闭的**（45 类不变）。

### 1.4 核心挑战：歧义 × 上下文

序列标注的本质是**利用上下文消歧**。一个词的标签不取决于它自身，而取决于它在句子中的位置：

```
"they can fish"
  → "can" = MD (情态动词), "fish" = VB (动词): "他们能捕鱼"
  → "can" = VB (动词),   "fish" = NN (名词): "他们装罐鱼" (不太常见)
```

单看 "can" 无法决定，必须看前后词的标签。这就是为什么需要**序列模型**（HMM/CRF/BiLSTM-CRF/BERT），而不是逐词独立分类。

---

## 2. 标注体系

### 2.1 Penn Treebank POS 标签集（45 类）

Penn Treebank 是 NLP 最广泛使用的英语 POS 标注规范，共 **45 个标签**。下表列出主要类别：

| 类别 | 标签 | 含义 | 例子 |
|------|------|------|------|
| **动词** | VB | 动词原形 | eat, run |
| | VBD | 过去式 | ate, ran |
| | VBG | 动名词/现在分词 | eating, running |
| | VBN | 过去分词 | eaten, run |
| | VBP | 非第三人称单数现在时 | I eat, they run |
| | VBZ | 第三人称单数现在时 | she eats, it runs |
| **名词** | NN | 单数名词 | dog, book |
| | NNS | 复数名词 | dogs, books |
| | NNP | 单数专有名词 | Mary, Beijing |
| | NNPS | 复数专有名词 | Americans |
| **形容词** | JJ | 形容词 | big, red |
| | JJR | 比较级 | bigger |
| | JJS | 最高级 | biggest |
| **副词** | RB | 副词 | quickly, very |
| | RBR | 比较级 | faster |
| | RBS | 最高级 | fastest |
| **功能词** | DT | 限定词 | the, a, this |
| | IN | 介词/从属连词 | in, of, because |
| | CC | 并列连词 | and, but, or |
| | MD | 情态动词 | will, can, must |
| | PRP | 人称代词 | he, she, it |
| | CD | 基数词 | one, 42 |
| | TO | to | to |
| **标点** | . | 句末标点 | . ! ? |
| | , | 逗号 | , |

> 其他标签还包括：EX（存在性 there）、FW（外来词）、LS（列表标记）、PDT（前限定词）、POS（所有格 's）、RP（小品词）、SYM（符号）、UH（感叹词）、WDT/WP/WP$/WRB（wh- 系列）、$（美元符）、``/''（引号）、( / )（括号）、:（冒号）、#（井号）。

**为什么是 45 个而不是更少？** Penn Treebank 在细粒度和实用性之间取了平衡。更粗的标签集（如 Universal Dependencies 的 17 类）更容易学，但丢失了时态（VBD vs VBP）、单复数（NN vs NNS）等有用信息。

### 2.2 BIO / BIOES：NER 的编码方案

NER 不能简单地说"这个词是地名"——需要标注**实体的边界**（一个实体可能跨越多个词）。两种主流编码：

**BIO（Begin-Inside-Outside）**：

```
Beijing     → B-LOC   (实体 Beijing 的开头)
and         → O       (非实体)
Shanghai    → B-LOC   (新实体 Shanghai 的开头)
```

多词实体的例子：

```
San    → B-LOC
Francisco → I-LOC   (San Francisco 的内部)
```

**BIOES（Begin-Inside-Outside-End-Single）**——更细，区分实体结尾：

```
San    → B-LOC      (开头)
Francisco → E-LOC   (结尾)
Beijing → S-LOC      (单字实体)
```

BIOES 比 BIO 略好（边界更明确），但差距不大。实际工程中 BIO 更常用。

**关键区别**：POS 的标签是**封闭集合**（45 类固定），NER 的标签是**开放集合**（B-PER, B-ORG, B-LOC, B-MISC, B-PRODUCT, B-EVENT, ... 可以无限扩展）。

---

## 3. 数学：四大方法

序列标注的四代方法，每一代解决上一代的瓶颈：

```
HMM (1980s)  →  CRF (2001)  →  BiLSTM-CRF (2015)  →  BERT (2018)
生成式          判别式          神经特征              预训练碾压
```

### 3.1 HMM：生成式序列标注

**Hidden Markov Model** 把词性标注建模为一个"隐藏状态序列生成观测序列"的过程：
- **隐藏状态** = 词性标签（你看不到）
- **观测** = 词（你看到的）

HMM 的核心公式——联合概率 $P(\text{tags}, \text{words})$ 的朴素分解：

$$
P(t_1^n, w_1^n) = \prod_{i=1}^{n} \underbrace{P(t_i \mid t_{i-1})}_{\text{转移概率 } A} \cdot \underbrace{P(w_i \mid t_i)}_{\text{发射概率 } B}
$$

其中 $t_0 = \text{START}$。这就是两个**独立性假设**：

1. **马尔可夫假设**：当前标签只依赖前一个标签——$P(t_i \mid t_1 \ldots t_{i-1}) = P(t_i \mid t_{i-1})$
2. **输出独立性**：当前词只依赖当前标签——$P(w_i \mid t_1 \ldots t_n, w_1 \ldots w_n) = P(w_i \mid t_i)$

> **为什么"朴素"（naive）？** 因为真实语言中，一个词的词性可能依赖更远的上下文（不只是前一个标签），一个词的出现也可能依赖前后多个词。但这两个假设让计算变得可行，而且在实践中效果出奇地好——和朴素贝叶斯分类器一样"朴素但好用"。

**训练 = 数数**：HMM 的参数通过最大似然估计（MLE），就是统计计数：

$$
\hat{P}(t_i \mid t_{i-1}) = \frac{C(t_{i-1}, t_i)}{C(t_{i-1})} \qquad \text{(转移概率)}
$$

$$
\hat{P}(w_i \mid t_i) = \frac{C(t_i, w_i)}{C(t_i)} \qquad \text{(发射概率)}
$$

加 $k$ 平滑处理零概率：

$$
\hat{P}(w_i \mid t_i) = \frac{C(t_i, w_i) + k}{C(t_i) + k \cdot V}
$$

### 3.2 Viterbi 解码

训练好 HMM 后，给定一个句子，怎么找到最优标签序列？穷举所有 $45^n$ 种可能是不行的（指数爆炸）。**Viterbi 算法**用动态规划把复杂度降到 $O(n \cdot N^2)$（$n$ = 句长，$N$ = 标签数）。

定义 $V_t(j)$ = 到位置 $t$、标签为 $j$ 的**最优路径**的对数概率：

$$
V_t(j) = \max_{i=1}^{N} V_{t-1}(i) \cdot \underbrace{a_{ij}}_{P(t_j \mid t_i)} \cdot \underbrace{b_j(o_t)}_{P(w_t \mid t_j)}
$$

初始化：

$$
V_1(j) = \pi_j \cdot b_j(o_1)
$$

实际代码中用**对数空间**避免下溢（连乘变连加）：

$$
\log V_t(j) = \max_{i} \big[\log V_{t-1}(i) + \log a_{ij}\big] + \log b_j(o_t)
$$

Viterbi = 最小编辑距离（Ch 2）的表亲——都是填一张网格 + 回溯。

> **Viterbi vs Forward 算法的唯一区别**：Forward 对前一步取 **$\sum$**（求和），Viterbi 取 **$\max$**（取最大）。求和得到"所有路径的总概率"，取最大得到"最优路径的概率"。Viterbi 还多了一个 backpointer 表用于回溯最优路径。

### 3.3 CRF：判别式 + 全局归一化

HMM 有两个瓶颈：**(1)** 难以加入任意特征（如大小写、后缀、词形）；**(2)** 生成模型 $P(X|Y) \cdot P(Y)$ 需要对 $P(X)$ 建模，但 $P(X)$（语言本身）很难学好。

**Conditional Random Field (CRF)** 直接建模 $P(Y \mid X)$——**判别式**模型：

$$
P(Y \mid X) = \frac{1}{Z(X)} \exp\left(\sum_{k=1}^{K} \lambda_k F_k(X, Y)\right)
$$

其中 $Z(X)$ 是**归一化常数（partition function）**：

$$
Z(X) = \sum_{Y' \in \mathcal{Y}} \exp\left(\sum_{k=1}^{K} \lambda_k F_k(X, Y')\right)
$$

全局特征分解为局部特征之和：

$$
F_k(X, Y) = \sum_{i=1}^{n} f_k(y_{i-1}, y_i, X, i)
$$

**特征函数 $f_k$ 的例子**（CRF 的核心优势——可以加任意特征）：

```python
f_1(y_{i-1}, y_i, X, i) = 1   if (y_{i-1}=DT and y_i=NN)     # 限定词后接名词
f_2(y_{i-1}, y_i, X, i) = 1   if word_i is capitalized        # 大写 → 可能 NNP
f_3(y_{i-1}, y_i, X, i) = 1   if word_i ends with "-ed"       # -ed → 可能 VBD
f_4(y_{i-1}, y_i, X, i) = 1   if (word_{i-1}="the" and y_i=VB) # the 后不太可能是动词
```

**CRF 解码仍然是 Viterbi**——因为线性链 CRF 也只依赖 $y_{i-1}$，动态规划格子结构不变。只需把 HMM 的 $\log a_{ij} + \log b_j$ 替换为 CRF 的 $\sum_k \lambda_k f_k$：

$$
V_t(j) = \max_{i} \left[V_{t-1}(i) + \sum_{k=1}^{K} \lambda_k f_k(y_{t-1}=i, y_t=j, X, t)\right]
$$

#### ★ 全局归一化 vs 局部归一化：为什么 CRF > MEMM

HMM 和 MEMM（Maximum Entropy Markov Model）都是**局部归一化**——每一步的概率单独归一化为 1。这导致 **label bias 问题**：

```
MEMM 在每一步：P(y_i | y_{i-1}, X) 是归一化的概率分布
  → 如果某个标签在某个位置"吃掉"了几乎所有概率质量，
     后续的证据（后面的词）就传不回来了。
```

CRF 用 $Z(X)$ 对**整个序列**做一次归一化——全局归一化。这让证据可以在整个序列上自由流动，不受局部瓶颈。

| 性质 | HMM | MEMM | CRF |
|------|-----|------|-----|
| 模型类型 | 生成式 $P(X,Y)$ | 判别式 $P(Y\|X)$ | 判别式 $P(Y\|X)$ |
| 归一化 | 局部 | 局部 | **全局** |
| Label bias | 无（生成式天然避免） | **有** | **无** |
| 任意特征 | 难 | 可以 | 可以 |
| 解码 | Viterbi | Viterbi | Viterbi |

### 3.4 BiLSTM-CRF：神经特征 + CRF 解码

CRF 的特征函数需要**人工设计**——大小写、后缀、前缀、词形……费时费力且不完整。

**BiLSTM-CRF**（Lample et al., 2016; Huang et al., 2015）用 BiLSTM 自动学习特征，CRF 做全局解码：

```
输入词序列
    ↓
[Embedding 层]    每个词 → 向量
    ↓
[BiLSTM 层]       前向 LSTM + 后向 LSTM → 拼接 → 上下文感知向量
    ↓
[Linear 层]       映射到标签分数
    ↓
[CRF 层]          全局归一化 + Viterbi 解码 → 最优标签序列
```

- **BiLSTM 的作用**：自动提取上下文特征（不需要手写 `f_k`）。前向 LSTM 看到左边上下文，后向看到右边，拼接后每个位置都有**双向上下文**。
- **CRF 的作用**：BiLSTM 输出的是每个位置独立的标签分数（局部），CRF 加上标签转移的全局约束，确保输出序列合法（如 `B-LOC` 后不能直接接 `I-PER`）。

BiLSTM-CRF 是 **2015-2018 年 NER 的 SOTA**，至今仍是低资源 NER 的强 baseline。

### 3.5 BERT 线性层：预训练碾压

2018 年后，BERT 几乎统治了序列标注。方法极其简单：

```
输入 token 序列
    ↓
[BERT 编码器]     12/24 层 Transformer，每个 token → 768/1024 维向量
    ↓
[Linear + Softmax] 每个 token → 标签概率分布
    ↓
取 argmax → 标签序列
```

**就这么简单**——BERT 的 contextual embedding 已经包含了所有需要的特征（词义、上下文、语法），只需要一个线性层把它们映射到标签空间。

| 方法 | CoNLL-03 NER F1 | 需要人工特征？ | 训练数据需求 |
|------|:---:|:---:|:---:|
| HMM | ~84% | 否（但能力有限） | 中 |
| CRF | ~89% | **是**（大量） | 中 |
| BiLSTM-CRF | ~90-91% | 否（字符嵌入等可选） | 中 |
| BERT | ~92-93% | **否** | 少（迁移学习） |
| BERT + CRF | ~93% | 否 | 少 |

> **BERT+CRF 的小增益**：在 BERT 上叠 CRF 层，在 NER 上通常提升 0.3-0.5 F1——因为 CRF 约束了实体边界（`B-` 后不能乱跳）。但对于 POS（标签集小、约束弱），BERT 纯线性头就够了，加 CRF 几乎无提升。

---

## 4. 方法演化时间线

```
1980s   HMM POS tagger        生成式、数数训练、Viterbi 解码
        ↑ Church 1988, DeRose 1988
        │
2001    CRF (Lafferty et al.) 判别式、全局归一化、解决 label bias
        ↑ 可加任意特征
        │
2015    BiLSTM-CRF            神经特征自动提取 + CRF 全局解码
        ↑ Lample 2016, Huang 2015
        │
2018    BERT (Devlin et al.)  预训练 contextual embedding + 线性头
        ↑ 一个线性层解决 POS/NER，CRF 只是锦上添花
        │
2020+   LLM (GPT/LLaMA)       prompt → 直接生成标签序列
        ↑ 连线性头都不需要，few-shot 工作
```

每一代解决上一代的瓶颈：
- **HMM → CRF**：从"只能用词本身"到"可以加任意特征"
- **CRF → BiLSTM-CRF**：从"人工设计特征"到"自动学习特征"
- **BiLSTM-CRF → BERT**：从"从头训练"到"预训练迁移"
- **BERT → LLM**：从"任务特定微调"到"通用 prompt"

---

## 5. 中文特殊：先分词再标注

中文 POS tagging 比英语多一步——**分词**。英语天然以空格分词，中文没有：

```
英语: "the dog runs" → ["the", "dog", "runs"]（空格分好了）
中文: "那只狗在跑" → ["那只", "狗", "在", "跑"]（需要先切词）
```

两种处理路线：

| 路线 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **词级** | 先分词，再对词标注 | 直觉自然，标签集与英语对齐 | 分词错误会传播给标注（error cascade） |
| **字符级** | 直接对单字标注，再合并 | 无分词错误传播；字符 embedding 更好学 | 标签集更大（需标注字在词中的位置） |

现代中文 NER 几乎都用**字符级 BiLSTM-CRF / BERT**——跳过分词，直接在字符上标注 BIO 标签。

中文特有的难点：
- **切分歧义**："南京市长江大桥" → "南京市/长江大桥" 还是 "南京/市长/江大桥"？
- **多音字**：多音字的读音影响词性（"行" xíng/háng）
- **外来词/网络新词**：没有固定词性，OOV 问题比英语更严重

---

## 6. 配套实验：HMM POS Tagger 消融实验

**文件**：`experiments/17_pos_hmm.py`（纯 NumPy，几秒跑完）

### 实验设计

在 125 句小型 Penn Treebank 风格语料上从零训练 HMM POS tagger，实现 Viterbi 解码，然后做**消融实验 (ablation)**——分别屏蔽转移概率和发射概率，看各自贡献多少。

### 关键结果

**结论 1：完整 HMM 基线**

| 指标 | 数值 |
|------|------|
| 测试集 token 准确率 | **89.9%** |
| 句子完全正确率 | **68.0%** |
| 歧义句 "back" 消歧 | ✓ 正确标为 VB |

**结论 2：消融实验——转移 vs 发射，谁贡献更多？**

| 模型 | token 准确率 | 相对完整模型 |
|------|:---:|:---:|
| 完整 HMM (A+B) | 89.9% | — |
| 屏蔽发射 B（只用转移） | 59.7% | −30.3pp |
| 屏蔽转移 A（只用发射） | 81.5% | −8.4pp |

> 整体 token 准确率上，**发射概率贡献更大**（屏蔽发射掉 30.3pp vs 屏蔽转移掉 8.4pp）。这符合直觉：大部分词是**无歧义**的——"dog" 几乎总是 NN，"barks" 几乎总是 VBZ——光看词本身就能标对。

**结论 3 ★：未知词（OOV）——转移概率是唯一救命稻草**

| 模型 | 已知词准确率 | 未知词准确率 |
|------|:---:|:---:|
| 完整 HMM (A+B) | 90.6% | **84.6%** |
| 屏蔽转移 A（只用发射） | 91.5% | **0.0%** |
| 屏蔽发射 B（只用转移） | 63.2% | 30.8% |

> ★ **反直觉发现**：去掉转移概率后，未知词准确率从 **84.6% 暴跌到 0.0%**。发射概率对未知词毫无信息（词没见过 → 均匀分布），唯一能帮你的是"标签序列的语法骨架"——前一个词性是什么，决定了当前词性最可能是什么。**转移概率不是锦上添花，而是 OOV 的全部。**

**结论 4：未知词靠上下文猜词性**

```
句子  : the blue elephant trumpets .   ("elephant" 训练集未出现)
金标  : DT  JJ  NN       VBZ      .
完整  : DT  JJ  NN       VBZ      .   ✓    ← "DT JJ ___ VBZ" → ___ 必是 NN
```

> 即使词从未见过，`DT JJ ___ VBZ` 这个转移模式也强烈暗示空格处 = NN。转移概率编码的是语言的**句法骨架**，与具体词汇无关。

### 反直觉发现的三层总结

| 层次 | 直觉 | 事实 |
|------|------|------|
| 整体准确率 | "转移和发射应该差不多重要" | 发射 > 转移（30.3pp vs 8.4pp） |
| 已知词 | "词本身就能决定词性" | 对，已知词靠发射就够（91.5%） |
| 未知词 | "没见过的词只能瞎猜" | 错！靠转移仍有 84.6%，没转移则归零（0%） |

**洞察**：转移概率的价值不在"锦上添花"，而在"OOV 保险"。你在已知词上看不到它的价值，但遇到从没见过的词时，它就是全部。这也是为什么 HMM / CRF 在低资源、高 OOV 场景至今有用——语法是通用的，不需要为每个新词重新训练。

---

## 7. 批判：LLM 时代，HMM / CRF 还有用吗？

### 被 BERT / LLM 替代的部分

- **英文 NER**：BERT 在 CoNLL-03 上 F1 ≈ 93%，HMM ≈ 84%，差距巨大。学术 benchmark 上，HMM/CRF 已被淘汰。
- **特征工程**：CRF 需要人工设计大量特征函数，BERT 自动学习。CRF 的"特征工程优势"在预训练时代变成了负担。
- **SOTA 竞赛**：所有 NER/POS leaderboard 的顶端都是大模型 + 微调/few-shot。

### HMM / CRF 仍然不可替代的场景

| 场景 | 为什么 HMM/CRF 仍有用 |
|------|----------------------|
| **低资源语言** | 没有预训练模型，没有标注数据。HMM 只需少量标注就能跑 |
| **高 OOV 领域** | 医疗、法律、化学——专业术语不断产生，BERT 词表覆盖不到。HMM 的转移概率对 OOV 天然鲁棒 |
| **可解释性** | HMM 的转移概率可以直接读成"DT 后面 95% 是 NN"。BERT 是黑箱 |
| **边缘部署** | HMM 模型小（几 MB）、推理快（CPU 毫秒级）。BERT 需要 GB 级内存 |
| **冷启动** | 从零开始标注，HMM 提供初始 baseline，比直接上 BERT 更稳 |

### LLM 的序列标注能力

现代 LLM (GPT-4 / Claude / LLaMA) 可以通过 prompt 直接做序列标注：

```
Prompt: "标注以下句子的词性（用 Penn Treebank 标签）：
         'The cat sits on the mat.'"
LLM:    "The/DT cat/NN sits/VBZ on/IN the/DT mat/NN ./."
```

- **优点**：zero-shot / few-shot，无需训练，无需标注数据
- **缺点**：推理慢（秒级 vs 毫秒级）、API 成本高、标签格式不稳定、长文本一致性差

### 方法选择的决策树

```
有大量标注数据 + GPU？
  → BERT 微调（SOTA）

有预训练模型但标注数据少？
  → BERT few-shot 或 LLM prompt

完全低资源（无预训练模型，少量标注）？
  → CRF（加人工特征）或 HMM

需要可解释性 / 边缘部署 / 极低延迟？
  → HMM（可解释 + 轻量）或 CRF（轻量 + 特征可控）

需要 OOV 鲁棒性？
  → HMM（转移概率天然处理 OOV）+ 词汇特征
```

---

## 📌 下一步

- **附录 A（HMM 深度版）**：HMM 的三个问题（评估/解码/学习）、前向-后向算法、Baum-Welch 无监督学习——比本章更深入
- **Ch 18（CFG 与成分句法分析）**：从"给词打标签"升级到"给短语建树"——PCFG、CKY 算法
- **Ch 19（依存句法分析）**：为什么中文更适合依存？transition-based vs graph-based
- **Ch 20（信息抽取）**：NER 是 IE 的第一步——关系抽取、事件抽取、时间表达式

---

## ✍️ 练习

**练习 17.1（HMM 训练）**：手算以下微型语料的转移概率矩阵 $A$ 和发射概率矩阵 $B$（不加平滑）：
```
the/DT dog/NN runs/VBZ ./.
the/DT cat/NN runs/VBZ ./.
```
计算 $P(\text{VBZ} \mid \text{NN})$ 和 $P(\text{runs} \mid \text{VBZ})$。

**练习 17.2（Viterbi 手算）**：用练习 17.1 的 HMM，手算 "the dog runs" 的 Viterbi 解码过程。画出 $3 \times 3$ 的 Viterbi 网格，标出每格的值和 backpointer。

**练习 17.3（OOV 消融）**：修改实验脚本，把训练集缩小到 20 句（高 OOV 场景），重新跑消融实验。观察：(a) 整体准确率怎么变？(b) 未知词准确率怎么变？(c) "转移 > 发射"的结论是否在高 OOV 下更明显？

**练习 17.4（CRF 特征设计）**：为英语 POS tagging 设计 5 个有用的 CRF 特征函数 $f_k(y_{i-1}, y_i, X, i)$，解释每个特征的直觉。提示：考虑大小写、后缀、前一个词、下一个词。

**练习 17.5（BIO 转换）**：将以下 BIO 标注转换为 BIOES 标注，并标注实体边界：
```
New/B-LOC York/I-LOC City/I-LOC is/O in/O the/O United/B-LOC States/I-LOC ./O
```

**练习 17.6（方法对比）**：对于以下场景，选择最合适的序列标注方法并说明理由：
1. 给 1000 句非洲小语种标注 POS（无预训练模型）
2. 给英文医疗文本做 NER（大量医学术语 OOV）
3. 在手机上实时做中文分词 + POS（< 10ms 延迟）
4. 给 100 万句英文做 NER（有 GPU，追 SOTA）

**练习 17.7（开放思考）**：LLM 可以直接用 prompt 做序列标注，为什么 BERT + 线性头在工业界仍是主流？从延迟、成本、一致性、可控性四个维度分析。

---

> 配套实验：`experiments/17_pos_hmm.py`。姊妹章节：`18-上下文无关文法与成分句法分析.md`（从词级标注升级到短语建树）、附录 `A-隐马尔可夫模型.md`（HMM 三问题的完整推导）。
