# 05 — 词嵌入：word2vec 与 GloVe

> 这是「讲透NLP」的**词表示核心篇**，对应 SLP3 **Ch 5 (Word Embeddings)**。
>
> 一句话定位：**把「词的意思」从一张查不到的离散符号表，搬进一个可做加法、可算余弦的几何空间**——从此 `king - man + woman ≈ queen` 不再是比喻，而是坐标运算。配套实验：`experiments/05_word2vec.py`

---

## 0. 为什么需要词嵌入

回顾第 3、4 章，我们一直用一个**非常笨**的办法表示文本：

> 把整篇文档表示成一个**稀疏的词袋向量**（bag-of-words）：第 $i$ 维 = 词 $w_i$ 在文档里出现的次数。每个词本身则用 **one-hot** 表示——一个长度等于词表 $V$、只在自己的位置上是 1、其余全是 0 的向量。

这套表示法有三个致命问题，而本章就是要彻底解决它们：

1. **维度灾难（curse of dimensionality）**：词表 $V$ 动辄几万到几十万，one-hot 向量稀疏到几乎全是 0，却占满整条内存。
2. **语义真空**：one-hot 下任意两个不同词的内积都是 0，**猫、狗、虎三者的 one-hot 两两正交，距离完全一样**。`cat` 和 `dog` 离得并不比 `cat` 和 `democracy` 近。
3. **无法泛化**：一个词在训练集没见过（OOV），或它的搭配没出现过，模型对它就一无所知——这正是第 4 章里 `min_df=2` 要扔掉罕见词的根因。

> 🎯 本章的核心信息只有一句：**与其让每个词占一条独立的、互不相关的轴，不如让每个词变成一条短的、稠密的、由它「常和谁一起出现」决定的向量——意思就藏在那些方向里。**

这就是**词嵌入（word embedding）**：把词从离散的 one-hot 空间，「压缩」进一个低维（50–300 维）的稠密实向量空间，使得**语义相近的词在几何上靠近**。

---

## 一、直觉层：意思 = 上下文的指纹

### 1.1 one-hot 到底有多糟

把 `cat`、`dog`、`tiger`、`democracy`、`algorithm` 都画成 one-hot，会得到一组两两正交的坐标轴。在这个空间里算余弦相似度：

$$
\cos(\text{cat}, \text{dog}) = \cos(\text{cat}, \text{democracy}) = 0
$$

**所有不同词都「一样远」**。模型根本不知道猫和狗是近亲。更要命的是：one-hot 不能做任何有意义的向量运算，`cat` 加 `dog` 在数学上毫无定义。

### 1.2 分布假设：「一个词的意思，由它的邻居决定」

本章的灵魂是一句 1957 年的格言：

> **"You shall know a word by the company it keeps."**
> —— J.R. Firth, 1957

还有更早的 Harris (1954) **分布假设（distributional hypothesis）**：**上下文相似的词，意义相似。** 这条朴素到近乎平凡的原则，撑起了整个现代词表示：

- `king` 常和 `crown, throne, rule, queen, royal` 一起出现；
- `queen` 也常和 `crown, throne, rule, king, royal` 一起出现；
- 于是它们的上下文分布很像 → 它们的意思很像 → 它们的向量应该靠近。

### 1.3 从「数共现」到「学向量」：两条路线

实现「上下文 → 向量」有两条路：

| | **计数法（count-based）** | **预测法（predictive）** |
|---|---|---|
| 做法 | 建共现矩阵 → PPMI 加权 → SVD 降维 | 直接训练神经网络去预测上下文 |
| 代表 | LSA、PPMI+SVD（**附录 J 详讲**） | **word2vec、GloVe（本章主线）** |
| 优点 | 全局统计、稳定 | 训练快、可增量、可扩展到海量语料 |
| 关系 | Levy & Goldberg (2014) 证明：**SGNS ≈ 在 PMI 矩阵上做隐式 SVD** |

> ⚠️ 一条贯穿全章的认知：**word2vec 的「魔力」不在神经网络，而在「分布假设 + 低秩结构」**。附录 J 的实验会证明——**没有任何梯度下降、纯线性代数（PPMI+SVD）也能复现 `king-man+woman≈queen`**。word2vec 只是把这个过程做成了可大规模训练的形式。

### 1.4 稠密向量的两个魔法

一旦词变成稠密向量 $v_w \in \mathbb{R}^d$，两件 one-hot 永远做不到的事成为可能：

1. **可算相似度**：余弦相似度（见 §2.8）直接给出「两个词有多近」。
2. **可做线性算术**：`king - man + woman ≈ queen` 成立——意味着语义维度（如「性别」「王室性」「时态」「首都」）被**近似线性地编码**进了向量轴。

这正是 BERT、GPT 内部第一层 `nn.Embedding` 的源头。

---

## 二、数学层

### 2.1 符号约定：每个词有两套向量

设词表大小 $V$，嵌入维度 $d$。word2vec 给**每个词 $w$ 配两套向量**：

- $v_w \in \mathbb{R}^d$：**中心词向量（center / input）**，当 $w$ 作中心词时用；
- $u_w \in \mathbb{R}^d$：**上下文向量（context / output）**，当 $w$ 作被预测的上下文时用。

**为什么要两套？** 数学上对称、推导干净（让「打分」和「被打分」的角色分离），训练更稳定。**训练结束后，丢弃 $u$，只保留 $v$（或取 $\tfrac{v+u}{2}$）作为该词的最终向量。** 这是 word2vec 的一个惯例，初学者常困惑「为什么一个词有两个向量」——记住：两套只为训练，落盘只用一套。

### 2.2 Skip-gram：给定中心词，预测上下文

**Skip-gram** 的思路：扫过语料的每个位置 $t$，用中心词 $w_t$ 去预测它窗口内的每个上下文词 $w_{t+j}$（$j\neq 0$）。目标函数（最大化对数似然）：

$$
\boxed{\;\mathcal{L}(\theta) \;=\; \sum_{t=1}^{T}\;\sum_{\substack{-c\le j\le c\\ j\neq 0}} \log P(w_{t+j}\mid w_t)\;}
$$

其中 $c$ 是窗口半径（如 $c=4$）。直觉：**让真正出现过的上下文，在「给定中心词」下的概率尽量大**——这自然把和中心词语义相关的词拉到附近。

> word2vec 还用一个细节叫**动态窗口**：每个中心词的实际窗口大小从 $\{1,\dots,c\}$ 均匀采样，相当于给近邻词更大的权重。本实验会实现它。

### 2.3 softmax 概率：完美但算不动

用两套向量的点积定义概率（softmax over 全词表）：

$$
\boxed{\;P(o\mid c) \;=\; \frac{\exp(u_o^{\top} v_c)}{\sum_{w=1}^{V}\exp(u_w^{\top} v_c)}\;}
$$

它语义完美，但**分母要遍历整个词表 $V$**（几万到几十万）。每一步训练都要算 $V$ 次指数和梯度——语料稍大就完全不可行。于是有了下一节的近似。

### 2.4 负采样（Negative Sampling）：把多分类拆成 $K+1$ 个二分类

**核心思想**：与其做 $V$ 类 softmax，不如把这个正样本对（中心、上下文）配 $K$ 个「负样本」（随机噪声词），然后做 $K+1$ 个**独立的二分类**——「这一对（中心，候选）是不是真的在语料里同时出现过？」

目标（最大化，等价于最小化下面的损失）：

$$
\boxed{\;\mathcal{L}_{\text{SGNS}} \;=\; -\log\sigma(u_o^{\top} v_c) \;-\; \sum_{k=1}^{K}\log\sigma(-\,u_{n_k}^{\top} v_c)\;}
$$

其中 $\sigma(x)=1/(1+e^{-x})$ 是 sigmoid，$o$ 是正上下文，$n_k$ 是采样的负词。

**逐项读懂**：
- $\log\sigma(u_o^{\top}v_c)$：把**正样本对的点积拉大**（让它们尽量同时出现）；
- $\log\sigma(-u_{n_k}^{\top}v_c)$：把**负样本对的点积压小**（让中心词和随机噪声词尽量不同时出现）。

**负样本怎么采？** 不是均匀采样，而是按 **$P(w)\propto \text{count}(w)^{0.75}$** 采样（Mikolov 2013）。0.75 这个幂**降低高频词（`the`/`of`）的被采概率、抬高低频词**——否则负样本几乎全是停用词，学不到东西。

> 本实验的**反直觉发现 2** 正是关于 $K$：$K$ 不是越大越好。在信号干净的 toy 语料上，小到中等的 $K$（甚至 $K=1$）已足以让 4 个类比全中——模型对 $K$ 颇为鲁棒；但 $K$ 过大（如 20、30）会频繁撞上**假负样本**（其实和中心词真共现、本不该被推开的词），把它们也当噪声推开，质量反降。

### 2.5 CBOW：skip-gram 的对偶

**CBOW（Continuous Bag-of-Words）** 把 skip-gram 反过来：**给定上下文（窗口内所有词），预测中心词**。把上下文向量做平均 $\hat v = \tfrac{1}{2c}\sum_{j\neq 0}u_{w_{t+j}}$，然后预测 $w_t$：

$$
P(w_t\mid \text{context}) = \frac{\exp(v_{w_t}^{\top}\hat v)}{\sum_w \exp(v_w^{\top}\hat v)}
$$

损失结构与 skip-gram 完全对偶。**经验法则**：skip-gram 在小语料/罕见词上更好（每个上下文词都贡献一次更新），CBOW 在大数据上更稳更快。

### 2.6 GloVe：把全局共现矩阵「压缩」进向量

**GloVe（Global Vectors, Pennington et al. 2014）** 不靠预测，而是直接拟合**全局共现矩阵** $X_{ij}$（词 $j$ 在词 $i$ 上下文中出现的次数）。它的目标：让两个词向量的内积 $\approx$ 它们共现次数的对数：

$$
\boxed{\;J \;=\; \sum_{i,j=1}^{V} f(X_{ij})\,\big(v_i^{\top}\tilde v_j + b_i + \tilde b_j - \log X_{ij}\big)^2\;}
$$

- $v_i$ 是词 $i$ 的中心向量，$\tilde v_j$ 是词 $j$ 的上下文向量（同样两套）；
- $b_i, \tilde b_j$ 是偏置，吸收词频的整体偏移；
- $f(X_{ij})$ 是**加权函数**，压制 `the` 这种高频词的统治性影响：

$$
f(x) = \begin{cases}(x/x_{\max})^{\alpha} & x < x_{\max}\\ 1 & x \geq x_{\max}\end{cases},\qquad \alpha=0.75,\ x_{\max}=100
$$

**直觉**：GloVe 是「计数法（共现矩阵）」与「预测法（向量化目标）」的融合——它同时利用了全局统计（像 LSA）和向量的几何性质（像 word2vec）。所以 GloVe 在类比任务上常略胜 word2vec。

### 2.7 PPMI 预告：word2vec 的「底牌」（附录 J 详）

理解 word2vec 必须理解 **PMI / PPMI**。两词的点互信息：

$$
\text{PMI}(w,c) = \log\frac{P(w,c)}{P(w)\,P(c)} = \log\frac{\#\text{共现}(w,c)\cdot N}{\#(w)\cdot\#(c)}
$$

- PMI > 0：两词共现**比独立出现更频繁**（真的相关）；
- PMI < 0：共现**比随机还少**（互相回避）。

取 $\max(0,\cdot)$ 得 **PPMI**（Positive PMI，扔掉负值）。**关键定理（Levy & Goldberg 2014）**：

> **Skip-gram with negative sampling 隐式地在做「shifted PPMI 矩阵的 SVD」。**

也就是说——**word2vec 学到的向量，本质是 PPMI 共现矩阵的低秩近似**。附录 J 会用纯 NumPy（无神经网络）的 PPMI+SVD 复现 `king-man+woman≈queen`，余弦 $>0.9$，给这条定理一个铁证。

### 2.8 余弦相似度与类比推理

**余弦相似度**（忽略向量长度，只看方向）：

$$
\boxed{\;\cos(\vec a,\vec b) = \frac{\vec a\cdot \vec b}{\lVert\vec a\rVert\,\lVert\vec b\rVert}\in[-1,1]\;}
$$

**类比推理（analogy）**：`king - man + woman ≈ queen` 的几何含义是**平行四边形**——「王室性」方向 $\vec{king}-\vec{man}$ 应与 $\vec{queen}-\vec{woman}$ 平行。形式化的**3CosAdd** 解法（Mikolov 2013）：

$$
d^{*} = \arg\max_{d\notin\{a,b,c\}}\;\cos\big(\vec d,\ \vec b - \vec a + \vec c\big)
\qquad\text{(问 } a:b = c:d\text{，如 man:king = woman:? )}
$$

> 本实验的**反直觉发现 1**：直接问「`king` 的最近词是谁」未必得到 `queen`；但 `king - man + woman` 这步**向量算术**会精确落到 `queen` 上——因为减法删掉了「男性」成分、加法补上了「女性」成分，这步操作是在**语义空间里导航**，不是在词表里检索。

---

## 三、代码层：从零实现 Skip-gram + Negative Sampling

完整可跑脚本见 `experiments/05_word2vec.py`（PyTorch 从零、CPU、几十秒）。核心三段：

**① 负采样损失**（与 §2.4 公式一一对应）：

```python
# centers: (B,) 正样本中心词   positives: (B,) 正样本上下文   negs: (B,K) 负样本
vc = v[centers]            # (B,d)  中心向量
up = u[positives]          # (B,d)  正上下文向量
un = u[negs]               # (B,K,d) 负样本上下文向量
logit_p = (vc * up).sum(1)            # 正样本点积 σ(u_o·v_c)
logit_n = torch.bmm(un, vc.unsqueeze(2)).squeeze(2)   # 负样本点积
loss = -(F.logsigmoid(logit_p).mean() + F.logsigmoid(-logit_n).mean())
```

**② 类比评测**（与 §2.8 公式对应）：

```python
target = v[base] - v[minus] + v[plus]      # king - man + woman
sim  = cosine(target, all_vectors)         # 与全词表的余弦
sim[[base, minus, plus]] = -np.inf         # 排除输入词本身
top1 = argmax(sim)                          # 期望 = queen
```

**③ 语料设计的「三维正交因子化」**：实验把每个词的上下文由**三个互相正交的维度**各自独立承载——**阶层**（royal/common，由 `crown`/`throne` 或 `field`/`house` 等名词）、**代际**（ruler/heir，由 `rules`/`governs` 或 `plays`/`learns` 等动词）、**性别**（m/f，由代词 `he`/`she` 与家庭名词）。于是 $\vec{king}\approx\text{royal}\oplus\text{ruler}\oplus\text{male}$，做算术时三维各自抵消：

$$
\vec{king}-\vec{man}+\vec{woman}
= \text{royal}\oplus\text{ruler}\oplus\text{female}
= \vec{queen}
$$

精确成立，而 `princess`（heir 动词）因代际不同被区分开——这是让 `queen` 而非 `princess` 胜出的关键。这是**教学简化**：真实语料里这种因子化藏在噪声之下，是统计趋势而非人为构造。配套地，本 toy 语料只有 68 词，向量维度 $d$ 也有甜区（实验发现 $d\approx20$ 最佳，$d\ge50$ 就开始把噪声词的伪共现也背进去，$d=300$ 时类比全崩）。

---

## 四、局限与争议

### 4.1 静态嵌入三大病

word2vec/GloVe 给每个词**一个固定的向量**，由此产生三个根本缺陷：

| 病症 | 例子 | 根因 |
|---|---|---|
| **一词多义（polysemy）** | `bank`（河岸 / 银行）只有一个向量 | 静态向量是所有用法的平均 |
| **上下文无关（context-blind）** | `apple`（水果 / 公司）同向量 | 不看句子 |
| **OOV（词表外）** | 训练没见过的词没有向量 | 词表固定，新词无表示 |

### 4.2 偏见：词嵌入是社会的一面镜子

词嵌入忠实地**继承了训练语料里的社会偏见**。经典案例（Bolukbasi et al. 2016, *Man is to Computer Programmer as Woman is to Homemaker*）：

$$
\vec{man} - \vec{woman} + \vec{homemaker} \approx \vec{programmer}\;?
$$

性别、种族、年龄的刻板印象都会被几何化进向量。SLP3 专辟一节讨论，至今是「负责任 AI」的核心议题。

### 4.3 类比评测本身有争议

- `king-man+woman=queen` 部分是**低维向量代数的巧合**，并不代表模型真「懂」王后；换几个类比（如道德、因果）就常常失效。
- 同一数据集上，换种子、换维度，rank-1 命中率波动很大——**类比准确率不是稳健的评测**。

### 4.4 BERT 上下文嵌入如何「治本」（预告 Ch10）

BERT（第 10 章）让**每个词在每个语境里有一个独立的向量**：

| | 静态嵌入（word2vec/GloVe） | 上下文嵌入（BERT） |
|---|---|---|
| 一词一向量？ | ✅ 固定 | ❌ 随语境变 |
| 一词多义 | ❌ 无法区分 | ✅ `bank`在金融句/河流句向量不同 |
| OOV | ❌ 无向量 | ✅ 子词（BPE）能拼出未见词 |
| 代价 | 极便宜、可离线 | 要跑整个 Transformer，贵 |

**但代价是**：BERT 向量不再是「一个词一个坐标」，几何类比（`king-man+woman`）也不再直接适用——你拿到的是「这句话里这个词」的向量，而非「这个词本身」的向量。

### 4.5 静态嵌入今天的位置

在 LLM 时代，静态嵌入并没有死，反而**仍是基线和基础设施**：

- **检索 / RAG 的 embedding retrieval**（句向量、文档向量，如 SBERT、BGE）。
- **资源受限场景**：端侧、嵌入式——几十 MB 的词向量库，微秒级查表。
- **可解释工具**：分析词表、聚类、词典构建。
- **LLM 内部第一层**：GPT/BERT 的 `nn.Embedding` 本质就是一张（随机初始化后学出来的）静态词向量表——只是它随后被 Transformer 的注意力层层「上下文化」。

---

## 五、中文 NLP 的特殊性

### 5.1 字级 vs 词级：中文 word2vec 的两难

中文没有空格，**分词（word segmentation）本身就是一道带歧义的工序**（第 17 章详），这直接影响 word2vec 的基本单元：

- **词级**：`今天/天气/真/好` → 语义完整，但**分词错误会污染向量**，且新词（OOV）多。
- **字级**：`今/天/天/气/真/好` → 无需分词、OOV 极少、模型小，但**单字语义不完整**。
- **实践折中**：字向量 + 词向量联合，或用字向量相加近似词向量；预训练 BERT-wwm（全词掩码）实质是字级输入 + 词级监督。

### 5.2 fastText：子词（subword）的妙招

fastText（Bojanowski et al. 2017）把每个词拆成**字符 n-gram 子词**，词向量 = 它所有子词向量之和：

$$
\vec w = \sum_{g\in \mathcal{G}(w)} \vec z_g
$$

- 解决**形态丰富语言**（土耳其语、芬兰语）的词形变化；
- 解决 **OOV**：`running` = `run` + `ing` 的子词，没见过的词也能拼出向量；
- 对中文：相当于在「字」与「词」之间架了一座桥。

### 5.3 中文预训练谱系

word2vec/SENNA → **Tencent AI Lab 800 维 / 800 万词**静态向量库（中文界经典资源）→ **BERT-wwm / RoBERTa-wwm**（哈工大讯飞实验室，全词掩码）→ 当下的中文 LLM。

---

## 六、与其他章的桥梁

| 联结 | 关系 |
|---|---|
| **Ch03/Ch04（BoW/TF-IDF）** | 那里的「特征是稀疏离散词频」→ 本章换成「学出来的稠密向量」，**这是从符号 NLP 走向神经 NLP 的第一步** |
| **附录 J（PPMI+SVD）** | 计数法 vs 本章预测法，**Levy & Goldberg 把两者统一**——强烈建议对照读 |
| **Ch06（神经网络基础）** | 神经网络的**第一层就是 embedding 矩阵 $E$**，one-hot 乘 $E$ = 查表，本章把这张表的来历讲透 |
| **Ch07（LLM）** | LLM 词表 → embedding lookup → Transformer；本章的 $v_w$ 就是那张表的雏形 |
| **Ch10（BERT）** | 静态嵌入的「上下文无关」病 → BERT 上下文嵌入的解药 |

---

## 📌 下一步

- **想看「计数法」如何用纯线性代数复现 word2vec 的魔力** → 附录 `J-PPMI与SVD.md`（无神经网络的 `king-man+woman≈queen`）
- **想看嵌入如何被神经网络使用** → `06-神经网络基础.md`（embedding 矩阵 = 查表）
- **想看上下文嵌入如何治掉静态嵌入的三大病** → `10-掩码语言模型-BERT.md`
- **想看嵌入在 LLM 里如何变成词表第一层** → `07-大语言模型.md`

---

## ✍️ 练习

1. **（手算 softmax）** 3 个词 $V=\{a,b,c\}$，向量 $v_c=[1,0]$，$u_a=[2,0], u_b=[0,1], u_c=[1,1]$。算 $P(a\mid c),P(b\mid c),P(c\mid c)$。若要把 $P(a\mid c)$ 拉大，$u_a$ 该朝哪个方向移动？
2. **（理解两套向量）** 为什么 word2vec 要给每个词配 $v$ 和 $u$ 两套向量？如果只用一套（$v=u$）会发生什么？（提示：对称性、正负样本的角色、训练稳定性。）
3. **（推导负采样梯度）** 对 §2.4 的 SGNS 损失，求 $\partial \mathcal{L}/\partial v_c$。你会发现梯度里出现 $(\sigma(u_o^\top v_c)-1)\,u_o + \sum_k \sigma(u_{n_k}^\top v_c)\,u_{n_k}$——直觉上这就是「把 $u_o$ 拉近、把 $u_{n_k}$ 推远」。
4. **（复现反直觉发现 2）** 把实验的 $K$ 扫成 $\{1,2,3,5,10,15,20,30\}$，画出类比命中数随 $K$ 的曲线。解释为什么 $K$ 太大会让「真正相关的词也被推开」。
5. **（复现反直觉发现 3）** 把 `dim` 扫成 $\{10,30,50,100,200,300,500\}$，观察类比命中数与参数量 $2V\cdot d$ 的关系。在什么条件下「维度越大越差」最明显？（提示：语料越小、噪声越多，过拟合越早。）
6. **（工程）** 本实验负采样用 $P(w)\propto\text{count}(w)^{0.75}$。如果把指数改成 0（均匀采样）或 1（按原频采样），对罕见词/停用词的负样本分布各有什么影响？哪种最糟？
7. **（思考）** GloVe 损失里为什么是对 $\log X_{ij}$ 而不是 $X_{ij}$ 做回归？（提示：共现次数跨好几个数量级，log 压缩 + 与 PPMI 的联系。）
8. **（对比）** 用同一份 toy 语料，分别跑本章的 SGNS 和附录 J 的 PPMI+SVD，比较两者在类比任务上的命中数。这如何佐证「Levy & Goldberg 的统一」？

---

> 配套实验：`experiments/05_word2vec.py`（PyTorch 从零、CPU、几十秒跑完）。
> 姊妹章节：附录 `J-PPMI与SVD.md`（计数法对照）、`06-神经网络基础.md`（embedding 矩阵）、`10-掩码语言模型-BERT.md`（上下文嵌入治本）。
