# 讲透 LLM · 思想史

> **一句话定位**：大语言模型不是 2017 年从石头里蹦出来的——它是一条从 Shannon 信息熵算起、跨越 78 年的思想长河，每一次"突破"都是旧思想等到了算力与数据的时机。
>
> **与 [`讲透AI历史`](../讲透AI历史/) 的关系**：本篇是 AI 通史的**LLM 专项纵深**——通史覆盖符号→连接→概率→深度→大模型五次范式转移（[`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md)），本篇在"大模型"这一段切进去，做到时间线×人物×思想×偶然性的博士级密度。
>
> **方法论前提**：本篇严格遵循 [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) 的五原则——思想史 > 年代史、路径依赖敏感、失败与成功同等重要、跨学科、批判性。**不写"年份+人物+事件"的维基百科。**

---

## 0. 方法论：用思想史看 LLM

在进入历史之前，先建立**怎么读**的能力。

**年代史陷阱**：如果只看"1948 Shannon → 2003 Bengio → 2013 word2vec → 2017 Transformer → 2018 BERT → 2020 GPT-3 → 2022 ChatGPT"，你会以为历史是线性进步的——每个节点都"必然"通向下一个。

**思想史纠正**：每一个节点背后都有一组**为什么此时此地**的问题：
- 为什么 Shannon 1948 提出的语言模型雏形，要等 55 年（2003 Bengio）才被神经网络重新激活？
- 为什么 BERT（2018）一度是 NLP 共识赢家，却最终被 GPT 路线（自回归生成）超越？
- 为什么 RLHF（Christiano 2017）早在 ChatGPT 前五年就提出了，却直到 2022 才"引爆"？
- 为什么 DeepSeek-R1 的纯 RL 训练能"涌现"推理，而同期大厂的路子完全不同？

**核心判断工具**：每次看到一个"突破"，问三问——① 这个思想的**前世**是什么？② **为什么此时此地**爆发（算力/数据/评测到位了吗）？③ 谁在**抵抗**它？为什么？

> 🎯 **博士级核心**：LLM 的历史不是"技术越来越好"的进步叙事，而是一部**统计派 vs 符号派 → 自回归 vs 双向 → 训练 scaling vs 推理 scaling**的路线斗争史。当前的"赢家叙事"掩盖了大量偶然性。

---

## 1. 前夜：n-gram 与 Chomsky 之争

### 1.1 Shannon 的信息熵实验（1948）

1948 年，Claude Shannon 在 *A Mathematical Theory of Communication* 中做了一件看似简单的事：**估算英语的熵**。

他的方法极其朴素——让人猜下一个字母。实验者对一段英文，从零上下文到逐渐给出前缀，统计猜对概率。结果：英语的熵约 **0.6–1.3 bits/字母**（视上下文长度而定），远低于随机字母的 $\log_2 26 \approx 4.7$ bits/字母。

这意味着什么？**英语文本高度可预测，上下文携带了大量信息**。Shannon 的估算方法本质上是：**用已知前缀预测下一个符号**——这就是语言模型的定义。

$$H(\text{English}) = \lim_{n \to \infty} -\frac{1}{n} \sum p(w_{1:n}) \log p(w_n | w_{<n})$$

Shannon 没有造"language model"这个词，但他**第一个把语言建模为概率序列预测问题**。这是 LLM 最远的思想源头——**"预测下一个 token"这个目标，1948 年就有了**。

### 1.2 Markov 的先驱实验（1913）

比 Shannon 还早 35 年，俄国数学家 Andrey Markov 在 1913 年手工分析了普希金《叶甫盖尼·奥涅金》的前两万字母，统计元音/辅音的转移概率，**发明了马尔可夫链**。

Markov 的贡献是概念性的：他证明语言不是独立的字母序列，而是一个**有记忆的随机过程**——当前符号的概率依赖于前几个符号。n-gram 模型（$P(w_n | w_{n-1}, ..., w_{n-N+1})$）就是马尔可夫链的直接应用。

### 1.3 n-gram 模型的统治（1950s–1990s）

n-gram 模型统治语言建模约 40 年。核心思想：**统计文本中 N 个词的共现频率，用最大似然估计转移概率**。

$$P(w_n | w_{<n}) \approx P(w_n | w_{n-N+1:n-1}) = \frac{\text{count}(w_{n-N+1:n})}{\text{count}(w_{n-N+1:n-1})}$$

**致命问题——维数灾难**：词表 $V$ 有数万词，bigram 需要 $V^2$ 个参数，trigram 需要 $V^3$。数据永远不够覆盖所有组合。所有平滑技术（Good-Turing、Kneser-Ney）都是在和这个根本问题搏斗。

### 1.4 Chomsky 的宣战（1956–1957）

1956 年，Noam Chomsky 发表 *Three Models for the Description of Language*，论证**有限状态自动机**（n-gram 模型的数学等价物）**不足以描述自然语言**。他的论据：英语有嵌套结构（"The man [who said [that ...]] is here"），需要递归，有限状态模型无法表达无限嵌套。

1957 年，*Syntactic Structures* 出版，Chomsky 提出生成语法（generative grammar），将语言定义为**一套生成规则**，而非**一个概率分布**。

**路线之争的本质**：
- **统计派**（Shannon 传统）：语言是概率分布，用统计方法建模。
- **规则派**（Chomsky 传统）：语言是规则系统，用形式语法生成。

**Chomsky 赢了——而且赢了 40 年。** 1957–1990，NLP 几乎被规则/符号方法垄断：句法分析器、语法规则、专家系统。统计方法被边缘化为"工程技巧"。

Chomsky 甚至有一句名言（后被反复引用）："**颜色的概率对我来说毫无意义**"（*The notion of probability of a sentence is an entirely useless one, under any known interpretation of this term.*）——直接否定了统计语言建模的根基。

### 1.5 统计派的地下抵抗（1990s）

Chomsky 的统治并非没有裂缝。1990s，三股力量在悄然复兴统计方法：

1. **IBM 统计机器翻译**（Brown et al. 1990-1993）：把翻译建模为概率模型，颠覆了基于规则的翻译系统。IBM 的 Candide 系统虽然没有最终胜出，但证明统计方法在语言任务上可行。
2. **Brown clustering**（Brown et al. 1992）：用聚类自动发现词类，是词向量的概念先驱。
3. **互联网数据爆炸**：万维网提供了海量文本数据，n-gram 的维数灾难开始被数据规模缓解。

> 🎯 **思想史洞察**：Chomsky 与 Shannon 之争，是 LLM 史上**第一次范式路线之争**。它不是"谁对谁错"——Chomsky 对嵌套结构的批评至今有效（LLM 仍然会在深层嵌套上出错），但**统计方法的工程胜利**（Google 翻译、搜索、语音）最终让 Chomsky 路线在 NLP 中边缘化。**这场争论的遗产**：今天 LLM 范式中"统计压倒规则"的格局，是 1990s 统计派的长期地下抵抗的成果，而非 Transformer 一朝之功。

---

## 2. 神经语言模型：Bengio 2003

### 2.1 维数灾难的新解法

2003 年，Yoshua Bengio 在 JMLR 发表 *A Neural Probabilistic Language Model*（NPLM），做了一个看似简单实则革命性的改动：

**把每个词表示为一个低维稠密向量（distributed representation），用神经网络计算 $P(w_n | w_{<n})$。**

$$P(w_n | w_{n-1}, ..., w_{n-m+1}) = \frac{e^{y_{w_n}}}{\sum_j e^{y_j}}, \quad y = b + Wx + U \tanh(d + Cx)$$

其中 $C$ 是词嵌入矩阵——每个词被映射到一个 ~50-100 维的向量。

**为什么这是范式突破？** n-gram 模型的参数量是 $O(V^N)$（指数增长），而神经网络 LM 的参数量是 $O(Vd + d^2)$（线性于词表，常数于 N）。**分布式表示打破了维数灾难**——语义相近的词共享表示空间，"猫"和"狗"的向量接近，所以即使"the cat sat on the"没见过，"the dog sat on the"也能帮助预测。

### 2.2 为什么没有立即引爆

Bengio 2003 是一个**超前于时代**的工作。接下来十年它没有引发革命，原因是经典的"**想法 vs 时机**"问题（[`讲透AI历史/00 §1.3`](../讲透AI历史/00-为什么学AI历史.md)）：

1. **算力不够**：2003 年的 CPU 跑神经 LM 比 n-gram 慢几个数量级，训不动大规模数据。
2. **数据不够**：2003 年还没有大规模干净文本数据集。
3. **学术氛围**：当时 NLP 主流还是 n-gram + 特征工程，神经方法被视为"理论有趣但不实用"。
4. **GPU 还没到位**：2006 年 NVIDIA CUDA 发布，2012 年 AlexNet 才证明 GPU 训练神经网络可行。

Bengio 自己后来回忆：他坚持这条路 20 年（2003–2018），期间被多次劝退。**这是"老一辈坚持成新范式"的罕见案例**（库恩定律说老一辈少转变，但 Bengio 是发起者，不是转变者——他始终在连接主义阵营）。

> 🎯 **博士级训练**：Bengio 2003 教会我们——**判断一个想法是否"成熟"，不只看想法本身，要看算力/数据/评测/学术氛围是否到位**。很多被埋没的好想法，只是在等时机。

---

## 3. 词向量革命：word2vec 2013

### 3.1 从副产品到主角

word2vec 的思想源头在 Bengio 2003——词嵌入是神经 LM 的副产品。但 Mikolov 2013（*Efficient Estimation of Word Representations in Vector Space*）做了两件改变游戏规则的事：

1. **效率**：去掉了隐藏层的非线性变换，只保留嵌入层 + 简单分类器。训练速度提升 10×，能在数十亿词上训。
2. **类比发现**：发现了嵌入空间的线性结构——$\vec{king} - \vec{man} + \vec{woman} \approx \vec{queen}$。

"king - man + woman = queen" 成为 2013-2015 年 NLP 最著名的"魔法"。它把一个抽象概念（语义类比）变成了**向量算术**——这极大激发了社区想象力。

### 3.2 GloVe：另一种哲学（Pennington 2014）

GloVe（*Global Vectors for Word Representation*）走不同路线：不训练神经网络，而是直接**分解全局词共现矩阵**。

$$J = \sum_{i,j} f(X_{ij}) (w_i^T \tilde{w}_j + b_i + \tilde{b}_j - \log X_{ij})^2$$

word2vec 是**局部上下文窗口**（在线学习），GloVe 是**全局统计**（矩阵分解）。两种哲学各有优势，最终在性能上接近。

### 3.3 概念革命：意义 = 向量空间中的位置

word2vec/GloVe 的真正贡献不是某个具体算法，而是**一个概念范式**：**词的意义可以被编码为高维空间中的一个点，语义关系是空间中的几何关系**。

这个范式影响深远——它直接通向后来的 contextual embeddings（ELMo/BERT）和 LLM 的表征空间。

### 3.4 但静态嵌入的天花板

word2vec 有一个根本缺陷：**每个词只有一个固定向量**。"bank"（河岸）和"bank"（银行）共享同一个表示。真实语言中，词义依赖上下文。

这个缺陷成为下一波革命的**驱动力**——2018 年 ELMo/BERT 的核心卖点就是"上下文相关的词向量"。

> 🎯 **思想史模式**：word2vec 是一个"**概念突破 + 工程红利**"的经典案例。概念（分布式表示）来自 Bengio 2003，工程（高效训练）来自 Mikolov 2013。**概念等了 10 年才被工程激活**——这和 Bengio 2003 等了 10 年才被算力激活是同一个模式。

---

## 4. 第一次范式转移：预训练（ELMo / GPT / BERT 2018）

### 4.1 三篇论文，一个范式

2018 年是 NLP 的"奇点年"——三个月内三篇论文共同确立了**预训练 + 微调**范式：

| 论文 | 时间 | 核心创新 | 架构 |
|------|------|---------|------|
| **ULMFiT**（Howard & Ruder） | 2018-01 | 证明 LM 预训练 + 微调在 NLP 有效 | AWD-LSTM |
| **ELMo**（Peters et al.） | 2018-02 | 上下文相关的词向量 | 双向 LSTM |
| **GPT-1**（Radford et al.） | 2018-06 | Transformer decoder + 生成式预训练 | Decoder-only |
| **BERT**（Devlin et al.） | 2018-10 | 双向 Transformer + Masked LM | Encoder-only |

**共同范式**：先在大规模无标注文本上预训练语言模型，再在小规模标注数据上微调。

**这为什么是范式转移（库恩意义上）？**

**旧范式**：每个 NLP 任务从零训练——为分类训分类器，为翻译训翻译模型，为 NER 训 NER 模型。任务特异性（task-specific）。

**新范式**：**一个预训练模型 + 轻量微调 → 适配所有任务**。通用性（universal）。

**不可通约性**：旧范式问"如何为任务 X 设计特征/架构"，新范式问"如何预训练一个好的语言表征"。问题变了。

### 4.2 ULMFiT：被低估的先驱

ULMFiT（Howard & Ruder, 2018-01）是三篇中最不被记住但**概念上最早**的。它用 LSTM（不是 Transformer）证明：在通用语料上预训练 LM，然后在目标任务上微调，能大幅提升小数据任务性能。

ULMFiT 的贡献是**概念性的**——它第一个系统证明了"预训练 → 微调"在 NLP 的迁移学习有效。GPT 和 BERT 都站在它的肩膀上。

### 4.3 BERT vs GPT：一场决定后续 5 年的路线分叉

2018 年底，BERT 和 GPT-1 几乎同时出现，但走的是**对立的架构路线**：

| 维度 | BERT | GPT-1 |
|------|------|-------|
| 架构 | **Encoder-only**（双向） | **Decoder-only**（自回归） |
| 预训练目标 | **Masked LM**（完形填空） | **Next-token**（预测下一个词） |
| 优势 | 理解任务（分类/NER） | 生成任务 |
| 2018-2019 地位 | **共识赢家**（刷爆 11 项 SOTA） | 被认为"只是另一种选择" |

**2018-2019 的共识**：BERT 更强。它在 GLUE、SQuAD 等 benchmark 上全面碾压 GPT-1。学术界普遍认为双向编码器优于自回归解码器。

**但 OpenAI 赌的是另一件事——Scaling。** GPT 路线的关键赌注是：**自回归生成模型在足够大的规模下，会涌现出 BERT 无法企及的能力（zero-shot/few-shot generation）**。

这个赌注在 2020 年 GPT-3 上被验证——但当时（2018-2019），几乎没有人认为 GPT 路线会赢。

> 🎯 **路径依赖与偶然性**：如果 2018 年 Google 全押 BERT 路线（事实上一度如此），而不是 OpenAI 坚持 GPT 路线，今天 LLM 的格局会完全不同。**GPT 路线的胜利不是因为它"更好"，而是因为它在 scaling 上的赌注恰好对了**——而 BERT 路线在生成能力上有架构性局限（Masked LM 天然不适合自回归生成）。这是 LLM 史上最大的路线偶然性，详见 §13。

---

## 5. Scaling Laws 与 GPT-3

### 5.1 Kaplan 2020：经验定律的发现

2020 年 1 月，OpenAI 的 Jared Kaplan 等人发表 *Scaling Laws for Neural Language Models*，发现了一个惊人的经验规律：

**LM 的 loss 与模型参数 $N$、数据量 $D$、计算量 $C$ 之间服从幂律关系。**

$$L(N) = \left(\frac{N_c}{N}\right)^{\alpha_N}, \quad L(D) = \left(\frac{D_c}{D}\right)^{\alpha_D}, \quad L(C) = \left(\frac{C_c}{C}\right)^{\alpha_C}$$

其中 $\alpha_N \approx 0.076$, $\alpha_D \approx 0.095$, $\alpha_C \approx 0.05$。

**意义**：这不是"更大更好"的常识——而是**loss 可预测地随规模下降**。给你 $10\times$ 算力，你能预测 loss 会降多少。这把"要不要 scale"从信仰问题变成了工程问题。

### 5.2 Chinchilla 的修正（2022）

Kaplan 的 scaling law 有一个被忽视的错误：它建议把大部分预算花在**增大模型**而非**增加数据**上。

2022 年，DeepMind 的 Hoffmann 等人（Chinchilla 论文）修正了这个偏差：

**计算最优配比**：模型参数 $N$ 和训练 token $D$ 应满足 **$D \approx 20N$**。

**Chinchilla 的证据**：用同样的算力，训一个 70B 模型喂 1.4T token（Chinchilla 配比），**超过了** GPT-3 的 175B 模型喂 300B token（Kaplan 配比）。GPT-3 **严重欠训练**。

这个发现影响巨大——它意味着几乎所有 2020-2021 的大模型（GPT-3、Jurassic、Gopher）都"参数太多、数据太少"。Llama 2/3 等后续模型都遵循 Chinchilla 配比。

### 5.3 GPT-3：范式炸弹

2020 年 6 月，GPT-3 发表，论文标题直截了当：*Language Models are Few-Shot Learners*。

**核心发现**：175B 参数的 GPT-3，**不需要任何微调**——只需在 prompt 里给几个例子（few-shot），就能做翻译、问答、写代码、做算术。

这推翻了 2018 年的"预训练 + 微调"范式：**微调不再是必需的——足够大的模型在 prompt 里就能学会新任务**（in-context learning）。

**为什么 GPT-3 是库恩范式转移？**
- **旧范式**：预训练 → 微调 → 部署（每个任务一个微调模型）
- **新范式**：预训练 → prompt → 直接用（一个模型适配所有任务）
- **新概念**："in-context learning" / "few-shot"——这些词在范式内**才被发明**
- **不可通约性**：微调范式的"任务适配"和 in-context learning 的"prompt 工程"是不同的语言

> 🎯 **博士级洞察**：GPT-3 证明了**GPT 路线（自回归 + scaling）的正确性**。2018-2019 的 BERT vs GPT 之争，在 2020 年由 GPT-3 判定——**自回归生成模型在足够规模下，涌现出双向模型无法企及的通用能力**。但要注意：这不是"自回归更好"的一般性结论——而是"**自回归 + 超大规模 = 涌现**"的特定结论。

---

## 6. RLHF 与 ChatGPT：对齐的引爆点（2022）

### 6.1 RLHF 的漫长孕育

ChatGPT 看似在 2022 年 11 月一夜爆发，但其核心技术 RLHF（Reinforcement Learning from Human Feedback）经历了 5 年的孕育：

| 时间 | 工作 | 贡献 |
|------|------|------|
| 2017 | **Christiano et al.** *Deep RL from Human Preferences* | 提出 RLHF 范式：人类偏好 → 奖励模型 → RL |
| 2020 | **Stiennon et al.** *Learning to Summarize from Human Feedback* | RLHF 用于文本摘要——证明 RLHF 在语言任务可行 |
| 2022-01 | **InstructGPT**（Ouyang et al.） | RLHF 用于指令遵循——**1.3B InstructGPT 被人类偏好超过 175B GPT-3** |

**InstructGPT 的关键数据点**：一个 1.3B 参数的模型，经过 RLHF 对齐后，**在人类偏好评估中超过了 175B 的 GPT-3**。这证明了一个深刻的结论：

> **对齐（alignment）比规模（scale）更重要。** 一个小的对齐模型比大的未对齐模型更有用。

### 6.2 ChatGPT：产品时刻

2022 年 11 月 30 日，ChatGPT 上线。5 天 100 万用户，2 个月 1 亿用户——成为历史上增长最快的消费级产品。

**ChatGPT 在技术上没有突破**——它是 InstructGPT（RLHF）+ GPT-3.5 的产品化。突破在于**产品形态**：免费、对话式、即时可用。

**思想史问**：为什么是 2022-11 而不是 2022-01（InstructGPT 发布时）？答案是：InstructGPT 是 API，面向开发者；ChatGPT 是免费产品，面向大众。**技术的引爆需要产品形态的匹配**——这与 2012 ImageNet 爆发（需要 AlexNet + GPU + ImageNet 数据三重到位）是同一模式。

### 6.3 DPO：RLHF 的简化

2023 年，DPO（Direct Preference Optimization）跳过了奖励模型，直接从偏好数据优化策略——**把 RLHF 变成了监督学习**。

**为什么 DPO 重要？** RLHF 的 PPO 训练极不稳定（同时训 4 个模型：policy、reference、reward、critic），DPO 只需 2 个（policy、reference）。这让中小团队也能做对齐。

**但 DPO 不是万能的**：它在 reasoning 强化上不如 GRPO（DeepSeek-R1 的方法），因为 GRPO 的群组相对优势对探索性任务更友好。详见 [`讲透RL/03`](../讲透RL/03-RLHF-DPO-GRPO.md)。

> 🎯 **博士级反思**：RLHF 的历史揭示了一个被忽视的真相——**ChatGPT 的成功不是算法突破，而是对齐工程的产品化**。Christiano 2017 提出 RLHF 时，没有人预见它会在 5 年后引爆消费级 AI。**技术突破到产品引爆之间的延迟，往往由"产品形态/市场/时机"决定，而非技术本身。**

---

## 7. 开源浪潮：LLaMA 2023

### 7.1 LLaMA 泄漏：民主化的意外起点

2023 年 2 月，Meta 发布 LLaMA（7B-65B），但**仅限研究申请**——不给商用。

几天后，模型权重在 4chan 泄漏。这成为开源 LLM 生态的**起爆点**——一旦权重公开，任何人都可以微调、量化、部署。

**连锁反应**：
- Stanford 用 $600 微调出 Alpaca（LLaMA 7B + GPT-3.5 蒸馏指令数据）
- Vicuna、WizardLM、Code LLaMA 等变体井喷
- llama.cpp 让 LLM 在 MacBook 上跑
- 量化技术（GGUF/AWQ/GPTQ）让 7B 模型在消费级 GPU 上部署

### 7.2 开源 vs 闭源的路线之争

LLaMA 泄漏后，LLM 领域形成**开源 vs 闭源**的两条路线：

| 维度 | 闭源（OpenAI/Anthropic/Google） | 开源（Meta/Mistral/DeepSeek/Qwen） |
|------|------|------|
| 模型权重 | 不公开 | 公开 |
| 商业模式 | API 收费 | 开源引流 + 企业服务 |
| 能力上限 | 通常领先 | 追赶中，差距缩小 |
| 生态控制 | 封闭 | 开放 |

**Meta 的战略反常**：Zuckerberg 决定开源 LLaMA 系列（Llama 2/3/4），这是大厂中最激进的开放策略。**为什么？** 因为 Meta 不靠模型卖 API——它靠用户在 Instagram/Facebook 的注意力变现。开源 LLM 让 AI 基础设施便宜化，有利于 Meta 的应用层。

### 7.3 DeepSeek：中国 AI 的范式叙事

2024-2025，DeepSeek 成为全球开源 LLM 最耀眼的明星——V3（MoE 架构，671B 总参数/37B 激活）在多项 benchmark 接近 GPT-4，而训练成本远低于同级别模型。R1 更是开源了 reasoning 能力。

**DeepSeek 的思想史意义**：它打破了"只有硅谷大厂能做顶级 LLM"的叙事，也打破了"开源必然落后闭源"的假设。详见 `讲透AI历史/advanced/06`（待写/未落盘）。

> 🎯 **博士级洞察**：LLaMA 泄漏是 LLM 史上最大的**偶然性事件**。Meta 的初衷是限制性发布（研究 only），但泄漏让权重大范围扩散。如果权重没有泄漏，开源 LLM 生态可能推迟 1-2 年——很多创业公司、研究项目的起点都会被推迟。**一个 4chan 帖子改变了 AI 产业的权力格局。**

---

## 8. 第二次范式转移：Reasoning Models（o1 / R1 2024-2025）

### 8.1 从训练 Scaling 到推理 Scaling

2024 年 9 月，OpenAI 发布 o1——第一个"reasoning model"。它的核心赌注是：

**不再靠增大模型参数提升能力，而是靠增加推理时的计算（test-time compute）让模型"想得更久"。**

这标志着 LLM 史上的**第二次范式转移**（第一次是 2018-2020 的预训练范式）：

| 维度 | 传统 Scaling（2020-2024） | Reasoning Scaling（2024+） |
|------|---|---|
| 增长维度 | 训练算力（更多参数 + 更多数据） | **推理算力**（更多思考步骤） |
| 代表 | GPT-3/4, Llama | o1/o3, DeepSeek-R1 |
| 技术手段 | 模型变大 | CoT + self-reflection + search |
| 边际成本 | 训练贵，推理便宜 | 推理贵（每 query 消耗更多 token） |

### 8.2 DeepSeek R1：纯 RL 的启示

2025 年 1 月，DeepSeek 发布 R1，其中 R1-Zero 版本**完全跳过 SFT，纯用 RL（GRPO + 可验证奖励）训练**，结果模型自发涌现了 chain-of-thought 推理能力。

训练日志中记录了一个戏剧性的"**aha moment**"——模型在 RL 训练中途突然开始自发产生 "Wait, let me reconsider..." 的自我反思行为，**这种行为没有被显式训练过，而是从 RL 中涌现的**。

**R1 的思想史意义**：
1. **证明了 RL 的力量**——当 reward 可验证（数学有答案/代码能跑），RL 极其有效。
2. **推理可以是涌现的**——不需要手把手教推理（SFT），模型在 reward 压力下自己学会思考。
3. **但 RLVR 有天花板**（[`讲透RL/05`](../讲透RL/05-RLVR的极限.md)）：pass@k 反转现象表明，**RLVR 是锐化器不是发现器**——它放大模型已有的能力，但不创造全新能力。

### 8.3 诚实的边界

Reasoning models 不是万能的：
- **推理贵**：o1 一个 query 可能消耗 10-100× 普通 LLM 的 token。
- **上限可能在预训练**：RLVR 的推理提升依赖预训练给的基础能力。
- **软推理 vs 硬推理**：chain-of-thought 是"软推理"（模式匹配 + 自洽性检查），不是形式逻辑证明。

> 🎯 **博士级判断**：Reasoning scaling 是否构成库恩意义上的"范式转移"仍有争议。支持方认为它改变了 scaling 的主战场（训练→推理）；反对方认为它只是 test-time compute 的工程优化，不是根本性的范式变化。我的判断：**它在工程层面是范式转移（改变了 scaling 的投入方向），但在科学层面仍是常规科学（没改变"LLM = 预测下一个 token"的基本假设）**。

---

## 9. 第三次范式转移的前夜：多模态 / Agent / 长上下文（2025-2026）

### 9.1 三条扩张线

2025-2026，LLM 正沿三条线同时扩张，每条都可能引发下一次范式转移：

**① 多模态融合**：从纯文本到图像/音频/视频。GPT-4o / Gemini / Claude 3.5 都已原生多模态。核心问题：**统一的 token 空间能否容纳所有模态？** LeCun 认为不能（文本和图像的信息密度不同），OpenAI 赌能（统一 token + 足够 scale）。

**② Agent：从 chatbot 到 actor**。LLM 从"回答问题"变成"执行任务"——调用工具、浏览网页、写代码、操作系统。核心问题：**LLM 能否成为可靠的序贯决策者？** RL（[`讲透RL/`](../讲透RL/)）是这条线的关键。

**③ 长上下文：1M+ tokens**。从 4K → 128K → 1M+，让 LLM 能"读完"整本书/整个代码库。核心问题：**长上下文真的等于"理解长文本"吗？** 实验表明，即使上下文有 1M tokens，模型对中间位置的信息仍会"遗忘"（lost in the middle 现象）。

### 9.2 World Model 之争

最根本的扩张是**世界模型**——LLM 理解物理世界的能力。

- **LeCun 路线（JEPA）**：预测抽象表征，不预测像素，理论可解释。
- **OpenAI 路线（Sora/Scaling）**：预测像素，赌涌现。
- **DeepMind 路线**：Genie/Dreamer 等基于 RL 的世界模型。

2026 仍未有定论。详见 [`05-2026前沿与开放问题 §3`](./05-2026前沿与开放问题.md)。

> 🎯 **思想史预测**：基于 §10 的模式分析，**第三次范式转移可能不是单一技术的突破，而是多模态 + Agent + world model 的融合**——当 LLM 不再只是"文本模式压缩器"，而是"多模态世界模拟器 + 行动者"时，范式的定义本身会改变。

---

## 10. 思想史反思：五个反常识

### 反常识 1：next-token prediction 是 NLP 最古老的思想

流行叙事：Transformer 2017 发明了 next-token prediction。

**真相**：next-token prediction 是 Shannon 1948 提出的——**LLM 的训练目标 78 年没变过**。变的是：用什么模型来拟合这个目标（n-gram → 神经网络 → Transformer），以及拟合的规模（百万词 → 万亿 token）。

**教训**：**底层思想的持久性 > 具体技术的时髦性**。

### 反常识 2：BERT 曾是共识赢家

流行叙事：GPT 路线从一开始就是对的。

**真相**：2018-2019，BERT 在学术界和工业界都被认为优于 GPT。它刷爆了 11 项 benchmark，而 GPT-1/2 被视为"另一种选择"。**GPT 路线的胜利是 2020 GPT-3 之后的事——而且是 OpenAI 一家公司的赌注，不是共识。**

**教训**：**共识可能是错的——尤其是当共识基于特定规模的实验时**。BERT 在小规模更好，但 GPT 在超大规模更好。**范式的胜负可能在 scale 轴上反转。**

### 反常识 3：对齐 > 规模（InstructGPT 的证据）

流行叙事：ChatGPT 成功是因为 GPT-3.5 更大。

**真相**：InstructGPT（1.3B，RLHF 对齐）在人类偏好上**超过** GPT-3（175B，未对齐）。**一个 100× 小但经过对齐的模型，比一个 100× 大但未对齐的模型更"有用"。**

**教训**：**能力的"有用性"不等于"规模"**——alignment 是一个独立的、与 scale 正交的能力维度。

### 反常识 4：Transformer 不是 LLM 的必要条件

流行叙事：没有 Transformer 就没有 LLM。

**真相**：Transformer（2017）极大地加速了 LLM 的发展，但**LLM 的核心思想（预训练 + next-token prediction）在 Transformer 之前就有了**（ULMFiT 用 LSTM 证明了预训练有效）。如果 Transformer 没有被发明，LLM 可能会晚几年，但 LSTM/attention 的组合最终也能走到类似的地方——只是更慢。

**教训**：**区分"加速器"和"必要条件"**——Transformer 是加速器，不是必要条件。

### 反常识 5：开源 LLM 的起点是一次泄漏

流行叙事：开源 LLM 是 Meta 的战略选择。

**真相**：Meta 发布 LLaMA 时是**限制性发布**（research only），不是开源。开源生态的起点是**权重泄漏**（4chan, 2023-03）。Meta 后来顺势把 Llama 2 开源——这是对既成事实的追认，不是初始计划。

**教训**：**重大历史转折可能由偶然事件触发**——不要把"事后合理化"当初始意图。

---

## 11. 关键人物与机构谱系

### 11.1 三条学术血脉

```
Bengio 谱系（加拿大/蒙特利尔）
├── 2003 NPLM（神经 LM 开山）
├── word embeddings 理论基础
├── 2014 sequence-to-sequence（与 Sutskever）
└── 2018 GPT-1（Radford，OpenAI，受 Bengio 影响）
    ↓
    影响：整个神经 LM 范式的思想源头

Google Brain 谱系
├── 2017 Transformer（Vaswani et al.）
├── 2018 BERT（Devlin et al.）
├── 2020 T5（Raffel et al.）
├── 2022 Chinchilla（Hoffmann et al.，DeepMind）
└── PaLM / Gemini 系列
    ↓
    影响：双向编码器 + scaling law

OpenAI 谱系
├── 2018 GPT-1（Radford）
├── 2019 GPT-2（staged release）
├── 2020 GPT-3（Brown et al.，few-shot learning）
├── 2020 Scaling Laws（Kaplan）
├── 2022 InstructGPT（Ouyang，RLHF）
├── 2022 ChatGPT
├── 2024 o1（reasoning）
└── 2025+ o3 / GPT-5
    ↓
    影响：自回归 + scaling + 对齐的完整路线
```

### 11.2 师承网络

- **Yoshua Bengio**：神经 LM 的祖父。他的学生和合作者遍布整个领域。
- **Ilya Sutskever**：Bengio 的博士生 → Google（AlexNet/Seq2Seq）→ OpenAI 联合创始人/首席科学家。**他是连接 Bengio 学术血统和 OpenAI 工业路线的关键人物**。GPT 路线的坚持很大程度上是他的赌注。
- **Sebastian Ruder**：ULMFiT 合作者，迁移学习在 NLP 的布道者。
- **Jason Weston**（Meta FAIR）：word2vec 之后的表征学习先驱。

### 11.3 机构的战略分歧

| 机构 | 核心赌注 | 代表 |
|------|---------|------|
| OpenAI | 自回归 + Scaling + RLHF | GPT/o 系列 |
| Google | 双向 + 多任务 + 多模态 | BERT/T5/Gemini |
| Meta (FAIR) | 开源 + 效率 | LLaMA |
| DeepMind | Scaling Law 精细化 + RL | Chinchilla/AlphaFold |
| Anthropic | Constitutional AI + 安全 | Claude |
| DeepSeek | MoE + RLVR + 极致效率 | V3/R1 |

> 🎯 **博士级洞察**：LLM 的路线之争很大程度上是**机构战略分歧**的体现。OpenAI 赌自回归，Google 最初赌双向，Meta 赌开源——这些赌注不是纯粹的科学判断，而是**商业/人才/数据的路径依赖**。

---

## 12. 失败方向与被淘汰的路线

### 12.1 静态词向量 → 上下文向量

word2vec/GloVe 曾是 NLP 标准工具（2013-2017）。但"一词一向量"的假设被 ELMo/BERT 彻底颠覆——**上下文相关的向量全面取代静态向量**。

**教训**：范式内的"标准工具"可能是下一个范式的淘汰对象。

### 12.2 Masked LM 用于生成

BERT 的 Masked LM 预训练目标适合理解任务（分类/NER），但**天然不适合生成任务**——因为 Masked LM 训练时看到的是"完形填空"（双向上下文），生成时需要自回归（只看前文）。

这个 mismatch 导致 BERT 路线在 ChatGPT 时代全面衰落。Google 的 T5 尝试用 text-to-text 统一（encoder-decoder），但最终还是被 decoder-only 路线压过。

### 12.3 从零训练多语言模型

早期尝试从零训练一个覆盖几十种语言的 LLM，但低资源语言性能差。后来发现**英语为主的 base + 多语言 SFT** 更有效——**路径依赖再次胜出**。

### 12.4 纯符号路线在 NLP 的残余抵抗

即使在 2024，仍有人尝试用符号方法（AMR、逻辑形式）增强 LLM。这些工作有价值（Neurosymbolic），但作为"替代 LLM"的路线已经失败——**统计/神经方法在 NLP 的统治已经不可逆**。

> 🎯 **博士级反思**：失败方向不是"愚蠢的错误"——它们在当时的条件下是合理的。BERT 用于生成在 2018 年看起来没问题，直到 GPT-3 证明自回归在 scale 下更好。**失败的教训**：**判断一个方向的成败，要放在 scale 轴上评估——小规模的最优可能在大规模时反转**。

---

## 13. 路径依赖与偶然性：GPT 路线 vs BERT 路线

### 13.1 最大的"如果"

LLM 史上最大的路径依赖问题是：**如果 2018 年 Google 全押 BERT 路线（实际上它一度如此），而不是 OpenAI 坚持 GPT 路线，今天会怎样？**

**反事实分析**：

如果 Google 赢得路线之争（BERT 成为主流），可能的结果：
- LLM 的核心能力会更偏向**理解**（分类/抽取/检索），而非**生成**（对话/代码/创作）。
- ChatGPT 可能不会出现——因为 BERT 路线天然不适合对话。
- Scaling Law 的发现可能推迟——因为 Google 的 BERT 路线不像 OpenAI 那样痴迷于"更大就更好"。
- 开源生态可能不同——因为 Google 倾向于发布论文但不发权重。

### 13.2 GPT 路线为什么赢了

不是因为它"更好"，而是因为三个**偶然因素**叠加：

1. **OpenAI 的赌注文化**：Altman/Sutskever 愿意花 $10M+ 训 GPT-3，这在当时是疯狂的决定。Google 内部有更多官僚阻力。
2. **In-context learning 的发现**：GPT-3 的 few-shot 能力是一个**意外的涌现**——没人预料到 175B 会突然学会"看几个例子就做新任务"。BERT 路线没有这个涌现，因为 Masked LM 不生成。
3. **RLHF 的补位**：GPT-3 的 base model 其实不好用（不受控/不安全/不对齐），是 RLHF 把它变成了 ChatGPT。RLHF + GPT 的组合是**事后发现的最佳搭配**，不是设计出来的。

### 13.3 偶然性清单

| 事件 | 如果没有发生 | 可能的替代 |
|------|-----------|-----------|
| LLaMA 权重泄漏（2023-03） | 开源 LLM 推迟 1-2 年 | 闭源 API 更长期垄断 |
| Ilya Sutskever 加入 OpenAI | GPT 路线可能没人坚持 | Google 的 BERT 路线主导 |
| Chinchilla 论文（2022） | 大量算力浪费在欠训练模型上 | Scaling 效率推迟 |
| DeepSeek R1 的 aha moment | 开源 reasoning 推迟 | o1 更长期垄断 reasoning |
| ChatGPT 免费（2022-11） | RLHF 的影响不会如此戏剧化 | 对齐技术被低估更久 |

> 🎯 **博士级核心**：**LLM 的当前格局有大量偶然性**。GPT 路线赢了，不意味着它是"必然最优"——它只是在特定历史条件下（OpenAI 的赌注 + in-context learning 的意外涌现 + RLHF 的补位）赢了。**学历史让你看到这些偶然，避免把当前格局当宿命。**

---

## 14. 开放问题

| 问题 | 为什么难 | 历史类比 |
|------|---------|---------|
| **Scaling Law 会撞墙吗** | 数据墙 + 能耗 + 边际递减 | n-gram 的维数灾难 |
| **自回归是唯一路线吗** | 目前最成功，但 MoE/SSM/世界模型在挑战 | BERT vs GPT 重演 |
| **LLM 能"真正推理"吗** | 模式匹配 vs 符号推理 | Chomsky vs Shannon 的延续 |
| **RLVR 的天花板在哪** | pass@k 反转 | 深度学习的过拟合 |
| **多模态能统一吗** | 文本/图像/视频信息密度不同 | n-gram 无法处理嵌套 |
| **Agent 能可靠吗** | 序贯决策 + 长程规划 + 误差累积 | 专家系统的维护爆炸 |
| **开源能追上闭源吗** | 算力/数据/人才的集中 | Linux vs Windows |
| **LLM 之后是什么** | 下一个范式不可预测 | 每次范式转移都被低估 |

---

## 15. 配套资源

### 15.1 核心论文（按时间线）

| 年份 | 论文 | 历史地位 |
|------|------|---------|
| 1948 | Shannon, *A Mathematical Theory of Communication* | 语言模型的思想源头 |
| 1913 | Markov, *Example of Statistical Investigation* | 马尔可夫链 |
| 1956 | Chomsky, *Three Models for the Description of Language* | 符号 vs 统计之争 |
| 2003 | Bengio et al., *NPLM* | 神经 LM 开山 |
| 2013 | Mikolov et al., *word2vec* | 词向量革命 |
| 2014 | Pennington et al., *GloVe* | 全局词向量 |
| 2018 | Peters et al., *ELMo* | 上下文向量 |
| 2018 | Howard & Ruder, *ULMFiT* | 预训练+微调 |
| 2018 | Devlin et al., *BERT* | 双向预训练 |
| 2018 | Radford et al., *GPT-1* | 自回归预训练 |
| 2019 | Radford et al., *GPT-2* | scaling 赌注 |
| 2020 | Kaplan et al., *Scaling Laws* | 幂律 |
| 2020 | Brown et al., *GPT-3* | few-shot learning |
| 2020 | Raffel et al., *T5* | text-to-text 统一 |
| 2022 | Hoffmann et al., *Chinchilla* | compute-optimal |
| 2022 | Ouyang et al., *InstructGPT* | RLHF 产品化 |
| 2025 | DeepSeek, *R1* | 开源 reasoning + RLVR |

### 15.2 本项目内导航

- **LLM 技术细节** → [00 LLM 是什么](./00-LLM是什么.md) → [01 完整生命周期](./01-完整生命周期.md) → [05 前沿](./05-2026前沿与开放问题.md)
- **Transformer 架构史** → [`讲透Transformer/`](../讲透Transformer/)
- **RLHF/DPO/GRPO** → [`讲透RL/03`](../讲透RL/03-RLHF-DPO-GRPO.md)
- **RLVR 边界** → [`讲透RL/05`](../讲透RL/05-RLVR的极限.md)
- **AI 通史（五次范式转移）** → [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md)
- **科学哲学（库恩/波普尔）** → [`讲透科学的现代性/03`](../讲透科学的现代性/03-AI时代的科学哲学.md)
- **中国 AI 史** → `讲透AI历史/advanced/06`（待写/未落盘）
- **从零训 LLM** → [`讲透公开课/06 CS336`](../讲透公开课/06-CS336语言建模从零造·全解.md)

---

## 16. 费曼回炉记录（L2 自检 · 已迭代）

- **F2 卡壳点**：长期把"LLM 历史"等同于"Transformer 之后的历史"——以为 2017 年之前的东西"不相关"。重读 Shannon 1948 后才意识到：**next-token prediction 这个目标 78 年没变，变的只是用什么模型去拟合它**。第二个卡壳在"BERT vs GPT 谁赢了"——习惯性认为"GPT 赢了所以 GPT 更好"，重读史料才发现 **2018-2019 BERT 是共识赢家，GPT 路线的胜利是 2020 GPT-3 之后的逆转，而且 OpenAI 是逆共识押注**。第三个坑：把 ChatGPT 当"RLHF 技术突破"，重读 InstructGPT 才明白 **RLHF 技术在 ChatGPT 前一年就有了（2022-01），ChatGPT 的突破是产品形态（免费对话式），不是算法**。
- **F3 术语翻译**：
  - "范式转移（paradigm shift）" → 不是"更好的方法取代旧的"，而是"**换了一个问题**"——预训练范式不是"更好的分类器"，而是把问题从"如何为每个任务设计模型"换成"如何预训练一个通用表征"。
  - "路径依赖" → 今天的 GPT 路线赢了不是因为它是"最优解"，而是因为 2018 年几个偶然事件（OpenAI 的赌注 + in-context learning 的涌现 + RLHF 补位）让它走到了前面——换一条路也可能走到类似的地方，只是 LLM 的具体长相会不同。
  - "涌现（emergence）" → 不是魔法，是 loss 曲线在某段规模上对某类任务突然变陡——像水烧到 100℃ 突然沸腾，但水温一直在涨，只是到那个点才发生相变。
- **F4 回炉**：v1 把历史写成"技术越来越好"的进步叙事（Shannon → Bengio → Transformer → GPT → ChatGPT），重心在"每个突破多厉害"。v2 改成**路线斗争史 + 偶然性分析**——加入"BERT 曾是共识赢家""LLaMA 泄漏是偶然""对齐 > 规模"等反常识，让读者看到**当前格局的非必然性**。diff 是从"进步叙事"升级为"思想史诊断"，训练读者对"赢家叙事"的免疫力。

---

## §一句话总结

> 🎯 **六句话**：
> 1. **LLM 的训练目标（next-token prediction）78 年没变**——从 Shannon 1948 到 GPT-4，变的是模型（n-gram → 神经网络 → Transformer）和规模（百万词 → 万亿 token）。
> 2. **LLM 经历了至少三次范式转移**：预训练范式（2018 ELMo/GPT/BERT）→ Scaling + In-context Learning（2020 GPT-3）→ Reasoning Scaling（2024 o1/R1）。每次都是"换问题"而非"更好的答案"。
> 3. **GPT 路线赢了 BERT 路线是最大的路径依赖**——2018-2019 BERT 是共识赢家，GPT 的逆转靠三个偶然因素（OpenAI 赌注 + 涌现 + RLHF）。
> 4. **对齐 > 规模**——InstructGPT（1.3B）超过 GPT-3（175B）证明 alignment 是与 scale 正交的能力维度。
> 5. **LLaMA 泄漏 + DeepSeek R1 = 开源 LLM 的两大偶然性事件**——一个 4chan 帖子和一个 aha moment 改变了产业格局。
> 6. **博士级核心**：**LLM 的当前格局有大量偶然性**——学历史让你看到这些偶然，避免把当前当宿命，训练对"赢家叙事"和"术语膨胀"的免疫力。

---

**完成日期**：2026-08-14 · **配套**：[讲透LLM README](./README.md) + [`讲透AI历史`](../讲透AI历史/) + [`讲透Transformer`](../讲透Transformer/) + [`讲透RL`](../讲透RL/) + [`讲透科学的现代性`](../讲透科学的现代性/)

---

## ✍️ 思考题

1. **反事实题**：如果 2018 年 OpenAI 没有坚持 GPT 路线，而是跟随 Google 做 BERT，ChatGPT 还会出现吗？给出你的推理。
2. **判断题**：Reasoning scaling（o1/R1）是库恩意义上的范式转移，还是 test-time compute 的工程优化？用 [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md) 的框架分析。
3. **批判题**：找一篇你读过的"LLM 突破"新闻，用本篇的反常识框架分析——哪些是真新思想，哪些是旧想法 + 更多算力？
4. **预测题**：基于 LLM 史的范式转移模式（每 2-4 年一次），预测下一次范式转移可能是什么、何时？给理由。
5. **延伸题**：Chomsky 1956 对有限状态模型的批评（嵌套结构），今天的 LLM 解决了吗？在什么任务上 LLM 仍然受限于这个批评？
