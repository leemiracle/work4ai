# 附录 I — 词义与 WordNet：同义词集、词义关系与消歧

> 对应 SLP3 附录 I。词有歧义——*bank* 可以是“银行”也可以是“河岸”。本章介绍**词义**（word sense）的形式化表示、**WordNet** 词典数据库及其词义关系网络（同义、上下位、部分整体），以及**词义消歧**（WSD）算法。

---

## 1. 直觉：一个词 = 多个离散的意义

*mouse* 至少有两个义：(1) 鼠标，(2) 老鼠。*bank*：(1) 银行，(2) 河岸。我们用上标标注：$bank^1, bank^2$。

**词义消歧**（WSD）就是根据上下文确定一个词用的是哪个义：

- *"a bank can hold the investments"* → $bank^1$（银行）
- *"the east bank of the river"* → $bank^2$（河岸）

> 🧩 **反直觉**：在 word2vec 中，*up* 和 *down* 的 embedding 极其接近——反义词语义空间中几乎重叠！因为它们出现在几乎相同的上下文中。这正是为什么需要显式词义资源的理由。

---

## 2. WordNet：词义关系数据库

### 2.1 Synset（同义词集）

WordNet 的核心单元是 **synset**——一组近义词构成的集合，代表一个概念：

$$\{\text{chump}^1, \text{fool}^2, \text{gull}^1, \text{mark}^9, \text{patsy}^1, \text{sucker}^1, \ldots\}$$

gloss: *a person who is gullible and easy to take advantage of.*

每个 synset 有 gloss（词典释义）和示例。WordNet 3.0 含 117,798 名词 / 11,529 动词 / 22,479 形容词 / 4,481 副词。

### 2.2 词义关系

| 关系 | 方向 | 定义 | 例子 |
|------|------|------|------|
| **同义** (synonymy) | ↔ | 意义相同/相近 | couch / sofa |
| **反义** (antonymy) | ↔ | 意义对立 | long / short |
| **上位** (hypernymy) | ↑ | 更一般的概念 | car → vehicle |
| **下位** (hyponymy) | ↓ | 更具体的子类 | vehicle → car |
| **部分** (meronymy) | ⊂ | 整体-部分 | wheel is part of car |
| **整体** (holonymy) | ⊃ | 部分-整体 | car has-part wheel |

上下位链构成 **IS-A 层级**（本体论 / ontology），可用于推理：*leukemia IS-A cancer* → 知道 leukemia 就知道它是 cancer 的子类。

> 名词有 26 个 **supersense**（粗粒度语义类别：ANIMAL, ARTIFACT, FOOD, PERSON...），动词有 15 个。当细粒度义不够用时可回退到 supersense。

### 2.3 结构化多义 (Structured Polysemy)

一个词的多个义之间可以有系统关系：*bank*（机构）↔ *bank*（机构的建筑）。这种规律性的多义叫 **metonymy**（转喻）：

$$\text{BUILDING} \leftrightarrows \text{ORGANIZATION} \qquad \text{AUTHOR} \leftrightarrows \text{WORKS}$$

---

## 3. 词义消歧（WSD）算法

### 3.1 上下文 embedding 最近邻（当前最优）

对 SemCor 标注语料中每个义的每个出现位置算 BERT 上下文 embedding，取均值得到**义 embedding** $v_s$。测试时：

$$\text{sense}(t) = \arg\max_{s \in \text{senses}(t)} \cos(v_t, v_s)$$

> 简单的 1-NN + BERT，就是当前 WSD 的最强基线（Peters et al. 2018）。

### 3.2 Lesk 算法（知识驱动，零训练）

选 gloss（释义）与上下文**词汇重叠最多**的义：

$$\text{score}(s) = |\text{gloss}(s) \cap \text{context}|$$

*bank* 上下文含 "deposits, mortgage" → $bank^1$ 的 gloss 有 "deposits" → 重叠=2 → 选 $bank^1$。

### 3.3 最频繁义基线

最简单的基线——选 WordNet 中排序第一个义。在 SemCor 上出人意料地难超越。

---

## 4. 中文词义资源

| 资源 | 特点 | 规模 |
|------|------|------|
| **HowNet（知网）** | 董振东创建，基于**义原**（sememe）的概念表示，词分解为义原组合 | ~100K 词 / ~2K 义原 |
| **同义词词林（扩展版）** | 哈工大，按义类分层树状分组，5 层编码 | ~77K 词 / 大类→中类→小类 |
| **中文 WordNet (CWN)** | 台大中研院，遵循 Princeton WordNet 框架的中文版 | 持续扩充 |
| **中文 Wikipedia 链接** | 类似英文 Wikipedia 锚链接做义标注 | 大规模但噪声多 |

> HowNet 的独特之处：每个词标注其**义原**（如“打”=`Hit|击打`），义原本身有层次结构。这使得 HowNet 能做比 synset 更细粒度的语义分解。

---

## 5. 批判性视角

- **离散义 vs 连续 embedding**：WordNet 把意义切成离散块，但语言的实际使用是连续的——一个义在不同语境中滑动。BERT 等 contextual embedding 模糊了边界，使 WSD 的离散假设越来越站不住脚。
- **WSD 的实用性存疑**：在端到端 NLP 任务（翻译、问答）中，显式 WSD 步骤往往**不提升**甚至**降低**性能——因为下游模型已隐式处理了词义。WSD 更多作为**评估工具**和**可解释性分析**手段而存在。
- **中文资源的碎片化**：英文有统一的 Princeton WordNet，中文多个并行资源（HowNet/词林/CWN），标准不统一，覆盖率不一，整合是长期难题。

---

## ✍️ 练习

1. ⭐ *bass* 在 WordNet 中有 8 个义。给出至少 3 个不同上下文句子，判断各自属于哪个义。
2. 简化 Lesk 算法对 *"I sat on the river bank"* 会选哪个义？gloss 重叠分析。
3. ★ 为什么 word2vec 中反义词 embedding 很近？这对 WSD 意味着什么？（提示：分布假设——反义词出现在相同句法槽。）

→ [J-PPMI点互信息.md](J-PPMI点互信息.md)：词的共现统计如何变成有意义的向量——WordNet 的词义关系有定性的表达，PPMI+SVD 给出定量的向量。
