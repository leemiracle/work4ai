# 11 — 信息检索与 RAG（导引版）

> 这是「讲透NLP」的检索篇。一句话定位：**LLM 的知识来自训练数据（参数化记忆），它不知道你的私人文档、最新新闻、公司内部 wiki——要让它"看着"这些资料回答，就得先**检索**出相关片段，再喂给模型。这套"检索 → 生成"就叫 **RAG（Retrieval-Augmented Generation，检索增强生成）**。本篇讲透检索的两种范式（词面检索 BM25 vs 语义检索 dense）、它们各自的"盲区"，以及为什么 RAG 的天花板永远是它的检索器。**
>
> 配套实验：`experiments/11_bm25_rag.py`（从零实现 TF-IDF / BM25 / 概念向量稠密检索 / RRF 混合 / 最小 RAG，跑出三个反直觉发现）。对应 SLP3 第 11 章 *Information Retrieval with BERT*（2026-01-06 release）。本章是导引版——工程深度版见姊妹项目 `../讲透RAG/`（5 篇全完成）。

---

## 1. 直觉层：为什么 LLM 需要 RAG

### 1.1 参数化知识的三个硬伤

回忆 Ch07：GPT 类模型把知识"压"进权重里——训练时见过的东西，推理时靠参数"回忆"。这种**参数化知识 (parametric knowledge)** 有三个无法绕开的问题：

1. **截止日期 (staleness)**：模型训练到某一天就停了，之后发生的事它不知道（"今天的股价"、"刚发布的论文"）。
2. **幻觉 (hallucination)**：当被问到训练时没见过的细节，模型会"一本正经地编"——因为它只会"像那样接着写"，不会说"我不知道"。
3. **私有数据 (private data)**：你的合同、病历、公司内部文档，模型训练时根本没见过，不可能从权重里调出来。

> **一句话比喻**：LLM 像一个"只凭脑子"参加考试的学生——会的不一定能记准（幻觉），不会的只能瞎编，而且看不到开卷资料。RAG 就是给这个学生**临时塞一张"开卷小抄"**：先把问题和资料库里相关的那页找出来，让他"看着抄"。

### 1.2 RAG = 检索 + 生成

RAG 的流水线极其朴素，只有两步：

```
   用户问题  ──→  [① 检索器]  ──→  top-k 相关文档  ──→  [② LLM]  ──→  回答
                     ↑                                    ↑
                从知识库找资料                  "根据这些资料，答案是..."
```

1. **检索 (retrieve)**：在知识库（一堆切好的文本片段 chunk）里，找出和问题最相关的 top-k 个。
2. **生成 (generate)**：把这 top-k 个片段拼进 prompt（"根据以下资料回答：... 资料：[片段] 问题：...")，让 LLM 基于它们作答。

> ⚠️ **关键认知（配套实验发现 3 的核心）**：RAG 的回答**完全建立在检索器找回来的片段上**。如果检索器找错了（漏掉正解、取回无关片段），生成器再强也"巧妇难为无米之炊"——它会看着错的资料答错的题，甚至基于错资料一本正经地编。**检索器就是 RAG 的天花板。** 这是本篇最重要的一个判断。

### 1.3 检索的两种范式：词面 vs 语义

检索这一步怎么算"相关"？历史上两套思路，各有所长：

| | **词面检索 (lexical / sparse)** | **语义检索 (dense / neural)** |
|---|---|---|
| 核心思想 | 文档和查询**共享多少词**、词有多稀有 | 文档和查询的**意思**有多接近 |
| 代表算法 | **TF-IDF、BM25** | **Sentence-BERT、DPR、E5、BGE** |
| 向量 | 稀疏（词表维度，大部分为 0） | 稠密（几百维实数） |
| 擅长 | 精确关键词、专有名词、代码、ID | 同义转述、跨语言、模糊语义 |
| 盲区 | **词汇鸿沟**：同义不同形就抓不到 | 罕见词/精确串反而可能漏 |

SLP3 第 11 章的标题就是 *Information Retrieval with BERT*——讲的就是 BERT 这类**双向编码器**（见 Ch10）怎么被改造成"句向量机器"（Sentence-BERT），从而做语义检索。下面数学层把两条线都讲透。

---

## 2. 数学层：从词频到语义相似度

### 2.1 词项-文档矩阵：IR 的起点

信息检索（IR）的最基本数据结构是**词项-文档矩阵 (term-document matrix)**：行是词，列是文档，格子里是这个词在这篇文档里出现的次数（**词频 tf，term frequency**）。

```
              D0(cats)  D1(felines)  D4(cars)  D7(cat产品页) ...
cat/feline       1          1            0          6            ...
hunt             1          0            0          0            ...
car              0          0            1          0            ...
speed            0          0            1          0            ...
```

查询 "cats hunt" 就是一个"伪文档"，和每列算相似度——最朴素的就是共享词的 tf 之和。这就是 **TF-IDF** 的雏形。

### 2.2 TF-IDF：词频 × 逆文档频率

光数共享词不够：高频虚词（the、is）到处都是，匹配了也没信息量；罕见实词（mitochondria）匹配上信息量极大。所以给每个词乘一个**逆文档频率 (IDF)**——出现在越少文档里的词越值钱：

$$
\text{idf}(t) = \log\frac{N}{\text{df}(t)}, \qquad \text{tf-idf}(t,d) = \text{tf}(t,d)\cdot \text{idf}(t)
$$

其中 $N$ 是文档总数，$\text{df}(t)$ 是包含词 $t$ 的文档数。文档 $d$ 对查询 $q$ 的得分就是所有查询词的 tf-idf 之和：

$$
\text{score}_{\text{tfidf}}(d, q) = \sum_{t \in q} \text{tf}(t,d)\cdot \text{idf}(t) \tag{11.1}
$$

### 2.3 TF-IDF 的致命缺陷：词频线性，可被"堆砌"骗

TF-IDF 的 tf 是**线性**的：一个词出现 6 次，得分就是出现 1 次的 6 倍。这给了**关键词堆砌 (keyword stuffing)** 可乘之机——早期 SEO 把 "cat" 在页面里重复一百遍，TF-IDF 就给它打天文高分。

> 配套实验的**反直觉发现 1** 会用数字证明：查询 "cats hunt"，正解是 D0（讲猫又讲捕猎），但语料里有一页把 cat 重复 6 次的产品页 D7。**原始 TF-IDF 把垃圾页 D7 排到第 1**（6 次 cat 得 7.69 分，压过 D0 的 cat+hunt 共 3.07 分）。这就是线性 tf 的危害。

### 2.4 BM25：词面检索的事实标准

BM25（Okapi BM25，Robertson et al. 1990s）用两个修正治好了 TF-IDF 的病，至今是工业词面检索的王者（Elasticsearch / Lucene 的默认打分）：

$$
\text{score}_{\text{BM25}}(d, q) = \sum_{t \in q} \text{idf}(t)\cdot \frac{\text{tf}(t,d)\cdot(k_1+1)}{\text{tf}(t,d) + k_1\!\left(1 - b + b\cdot\frac{|d|}{\text{avgdl}}\right)} \tag{11.2}
$$

两个修正：

**(a) tf 饱和 (saturation)** —— 分子分母里都含 $\text{tf}$，使得 tf 增大时得分**趋于一个上限** $k_1+1$，而不是线性增长：

$$
\text{sat}(\text{tf}) = \frac{\text{tf}\cdot(k_1+1)}{\text{tf}+k_1} \;\xrightarrow{\text{tf}\to\infty}\; k_1+1 \tag{11.3}
$$

直观地：一个词出现 1 次说明"相关"；出现 6 次**并不意味着"6 倍相关"**——多出来的重复几乎不增加信息。默认 $k_1=1.5$，饱和上限是 2.5。

**(b) 文档长度归一化** —— $\frac{|d|}{\text{avgdl}}$ 把文档长度（$|d|$）相对平均长度（avgdl）考虑进去：长文档天然更容易"碰巧"包含查询词，所以要打折。$b$（默认 0.75）控制打折强度。

> 配套实验**发现 1** 给出铁证：tf 从 1 涨到 16，BM25 的饱和项只从 1.00 涨到 2.29（渐近 2.5），而原始 tf 涨了 16 倍。**堆砌关键词在 BM25 里几乎买不到排名**——同样的查询 "cats hunt"，BM25 把正解 D0 排回第 1（3.18 vs D7 的 2.34）。

### 2.5 词汇鸿沟：词面检索的天花板

BM25 把词面检索做到了极致，但它有一个**结构性盲区**：只认"表面词形"，不认"意思"。

> **词汇鸿沟 (vocabulary mismatch)**：用户问 "how fast can a vehicle go"，正解文档写的是 "a car reaches a top speed of..."。人和稠密检索器都知道 vehicle≈car、fast≈speed，但 **BM25 看到的是 {fast, vehicle, go} 和 {car, speed, reaches}——零个词相同，得分 = 0**。

SLP3 把这个问题叫 *vocabulary mismatch problem*：用户用的词和文档作者用的词经常不一样（同义词、转述、不同语言）。词面检索对此**无能为力**——这正是语义检索被发明出来的动机。

### 2.6 语义检索（稠密检索）：用向量表示"意思"

语义检索的思路：用一个**编码器 (encoder)** 把查询和文档都映射成稠密向量，然后算**余弦相似度**：

$$
\text{sim}(q, d) = \cos(\mathbf{v}_q, \mathbf{v}_d) = \frac{\mathbf{v}_q\cdot \mathbf{v}_d}{\lVert\mathbf{v}_q\rVert\,\lVert\mathbf{v}_d\rVert} \tag{11.4}
$$

只要编码器学得好，"vehicle" 和 "car" 的向量就会很近（因为它们在训练语料里出现在相似的上下文里——分布假设，见 `05-词嵌入`）。于是 {fast, vehicle, go} 的向量和 {car, speed, reaches} 的向量余弦会很高，跨过词汇鸿沟。

**关键架构：双编码器 (bi-encoder)**。检索要算一个查询对**几百万文档**的相似度，不可能让查询和每个文档"交互计算"（太慢）。Sentence-BERT（Reimers & Gurevych 2019）的解法：

- 查询和文档**各自独立**过一个 BERT，各自 mean-pool 出一个向量 $\mathbf{v}_q$、$\mathbf{v}_d$。
- 文档向量**预先算好**存进向量库（建索引，见 §3.3）。
- 检索时只算 $\mathbf{v}_q$ 和库里每个 $\mathbf{v}_d$ 的余弦——可用近似最近邻（ANN，approximate nearest neighbor）在毫秒内搜完上亿条。

$$
\mathbf{v}_q = \text{meanpool}(\text{BERT}(q)), \quad \mathbf{v}_d = \text{meanpool}(\text{BERT}(d)), \quad \text{score} = \cos(\mathbf{v}_q, \mathbf{v}_d) \tag{11.5}
$$

> 注意这和 Ch10 的坑（发现 2：未微调 BERT 句向量各向异性、做相似度反而不如 word2vec）直接相关——所以语义检索的编码器都是**专门微调过**的（Sentence-BERT 用 NLI 数据、DPR 用问题-正解段落对训练），不是裸 BERT。

### 2.7 混合检索：两路信号融合（RRF）

BM25 和 dense 各有盲区（词面怕转述、语义怕罕见精确串），工业 RAG 几乎都用**混合检索 (hybrid retrieval)**：两路各排一次名，再融合。最常用的无参数融合法是 **RRF（Reciprocal Rank Fusion，倒数排名融合）**：

$$
\text{score}_{\text{RRF}}(d) = \sum_{\text{检索器 } r}\frac{1}{k + \text{rank}_r(d)} \tag{11.6}
$$

其中 $\text{rank}_r(d)$ 是文档 $d$ 在检索器 $r$ 的排名（第 1 名 rank=0），$k$ 常取 60。直觉：**排名越靠前贡献越大，两路都靠前的文档得分最高**。配套实验发现 3 会演示：单 BM25 在转述查询上失明，单 dense 偶尔漏精确串，**RRF 融合后两种查询全对**。

---

## 3. 从检索到 RAG：完整流水线

### 3.1 文档处理：chunking + 建索引

知识库通常是大 PDF / 网页 / 代码，不能整篇塞给 LLM（上下文窗口有限、且噪声多）。标准流程：

1. **切分 (chunking)**：把长文档切成几百 token 的片段（chunk），可带 overlap（避免切断句子）。
2. **建索引**：
   - 词面索引：倒排索引（inverted index），词 → 出现在哪些 chunk。BM25 在它上面跑（毫秒级）。
   - 语义索引：每个 chunk 过 encoder 存向量，用 ANN（FAISS / HNSW）加速余弦搜索。

> 工程细节（chunk 大小怎么选、overlap 多少、混合检索怎么配权重、rerank 怎么做）是 `../讲透RAG/02-工程组件.md` 的主题，本章不展开。

### 3.2 生成：把片段拼进 prompt

检索出 top-k 片段后，拼成 prompt 喂给 LLM：

```
根据以下资料回答问题。如果资料里没有答案，请说"资料不足"。

【资料1】{chunk_1}
【资料2】{chunk_2}
...
【问题】{user_query}
```

LLM 基于这些资料作答。**诚实性 (faithfulness)** 是 RAG 评估的核心：模型是否真的"依据资料"而不是夹带私货（幻觉）。`../讲透RAG/04-评估.md` 讲怎么用 RAGAS 量化和惩罚这种"不忠"。

### 3.3 向量索引加速：ANN

语义检索要算一个查询向量对上亿文档向量的余弦，暴力 $O(N)$ 太慢。**近似最近邻 (ANN)** 用图结构（HNSW）或乘积量化（PQ）把搜索降到 $O(\log N)$，代价是"可能漏掉极少数真正最近邻"（近似）。这是稠密检索能上规模的工程前提。数学细节见 `../讲透RAG/01-检索数学.md`。

---

## 4. 代码：从零实现 BM25 + 稠密检索 + 最小 RAG

完整可跑代码在 `experiments/11_bm25_rag.py`（纯标准库，几秒跑完）。这里讲三个最关键的片段。

**(1) BM25 的 tf 饱和**——分子分母都含 tf，使其渐近于 $k_1+1$：

```python
def bm25_scores(query, k1=1.5, b=0.75):
    q = tokenize(query); scores = [0.0]*N
    for i, toks in enumerate(DOC_TOKS):
        tf = Counter(toks); dl = len(toks)
        norm = (1 - b + b*dl/AVGDL)          # 文档长度归一化
        for t in q:
            if t in tf:
                f = tf[t]
                scores[i] += idf(t) * (f*(k1+1)) / (f + k1*norm)   # ← 饱和项
    return scores
```

**(2) 稠密检索的余弦相似度**——查询和文档各自变成概念向量再算角度：

```python
def dense_scores(query):
    qv = vec_from_tokens(tokenize(query))    # 查询向量
    return [cosine(qv, vec_from_tokens(toks))    # 每篇文档的余弦
            for toks in DOC_TOKS]
```

> 实验里用**手写本体**（cat→{feline,animal}、car→{vehicle}）模拟 Sentence-BERT 的语义向量，因为纯标准库无法跑真 BERT。原理一致：把"词形"换成"语义维度"，同义词落到同一维，跨过词汇鸿沟。

**(3) RRF 混合 + 最小 RAG**：

```python
def rrf_scores(query, k=60):
    cand = defaultdict(float)
    for scorer in (bm25_scores, dense_scores):
        s = scorer(query)
        if max(s) <= 0:        # 该通道失明（如 BM25 遇转述）→ 弃权，不污染融合
            continue
        for rank, i in enumerate(rank(s)):
            cand[i] += 1.0/(k+rank)
    return [cand.get(i,0.0) for i in range(N)]

def rag_answer(query, retriever):
    top = rank(retriever(query))[0]     # 检索 top-1
    return top, DOCS[top]               # 把它的原文当答案来源
```

---

## 5. 实验的三个反直觉发现

跑 `python3 -u experiments/11_bm25_rag.py`，会打印下面三个"反直觉"结论。

### 🔬 发现 1：关键词堆砌骗过原始 TF，骗不过 BM25

查询 "cats hunt"，正解是 D0（讲猫又讲捕猎）。语料里有一页把 cat 重复 6 次的产品页 D7。

| 检索器 | top-1 | 得分 | 判定 |
|---|---|---|---|
| 原始 TF×IDF | **D7（垃圾页）** | 7.69 vs D0 的 3.07 | ❌ 被堆砌骗走 |
| **BM25** | **D0（正解）** | 3.18 vs D7 的 2.34 | ✅ |

**反直觉点 + 铁证数字**：tf 从 1 涨到 6，BM25 的饱和项只从 1.00 涨到 **2.00**（不是 6 倍！）；即便 tf 涨到 16，饱和项也只到 2.29，渐近于 $k_1+1=2.5$。**"多重复几次关键词"在 BM25 里几乎买不到排名**——这就是 §2.4 的饱和函数在保护排序。加上 "hunt" 是罕见词（只出现在 D0）→ 高 IDF，D0 两个查询词都得分，垃圾页 D7 只有 cat 一根独苗。这是 IR 教科书"为什么用 BM25 不用 TF-IDF"最直白的演示。

### 🔬 发现 2：词汇鸿沟让 BM25 直接归零

查询 "how quickly can a motor vehicle move"（汽车能跑多快），正解是 D4/D5（讲 car / speed）。但查询词 {quickly, motor, vehicle, move} 和正解文档 {car, speed, reaches, travel} **零个表面词相同**。

| 检索器 | 每篇文档得分 | top-1 | 判定 |
|---|---|---|---|
| **BM25** | **全部 8 篇都是 0.0** | 瞎选（靠索引顺序） | ❌ 彻底失明 |
| **稠密（概念向量）** | D5=0.962, D4=0.949 | D5 | ✅ 正解 |

**反直觉点**：一个完全合理的问句，BM25 给**所有**文档都打 0 分——最强的词面检索器在此刻和"随机瞎选"没区别。稠密检索器靠 car↔vehicle（同是 vehicle 维）、quickly↔speed（同是 speed 维）的语义桥接，把正解找回（余弦 0.96）。**这就是 Sentence-BERT / DPR 这类稠密检索器存在的全部理由：把"表面词形"换成"预训练学到的语义"，匹配同义转述。**

### 🔬 发现 3：RAG 的天花板就是它的检索器

最小 extractive RAG（取 top-1 文档原文当答案来源）：

|  | Q1 关键词 "cats hunt" | Q2 转述 "vehicle move" |
|---|---|---|
| **BM25 检索** | ✅ D0 | ❌ 取回 D0（错） |
| **稠密检索** | ✅ D0 | ✅ D5 |
| **RRF 混合** | ✅ D0 | ✅ D5 |

**反直觉点**：同一个 RAG、同一个（抽取式）"生成器"，BM25 在 Q2 上取回错文档 → 答案就错；换稠密检索 → 答案就对。**生成器无法纠正检索错误**——它只能看着喂进来的资料作答。检索质量 = RAG 质量的天花板。RRF 混合把两路排名融合，每个通道的盲区被另一个覆盖，两种查询全对——这正是工业 RAG 几乎都用混合检索的原因。

---

## 6. 局限与争议

### 6.1 词面检索（BM25）的边界
1. **词汇鸿沟（发现 2）**：只认词形不认意思，同义转述/跨语言直接失明。这是结构性的，加多少 IDF 都治不好。
2. **仍是强基线**：在"精确关键词、专有名词、代码标识符、产品 ID"类查询上，BM25 经常**打败**时髦的稠密模型（BEIR 基准反复证实）。"BM25 is a strong baseline" 不是客套——很多团队上了 dense 后发现召回率反而降了，又退回 BM25。

### 6.2 稠密检索的边界
1. **罕见词 / 精确串**：稠密向量把词"模糊化"，遇到稀有专有名词、数字、错误码反而可能漏（这些正是 BM25 的强项）。
2. **领域漂移**：编码器在通用语料上训练，换到医疗/法律/代码领域，向量质量下降——常需领域微调。
3. **可解释性差**：BM25 为什么排这篇？因为有这几个关键词，一目了然。稠密为什么排这篇？"向量距离近"——说不清。
4. **成本**：建索引要跑一遍 encoder（贵），查询要算向量（虽 ANN 加速，仍比倒排索引重）。

### 6.3 RAG 本身的争议
1. **检索器是天花板（发现 3）**：再强的 LLM，喂错资料就答错。工业上大量精力花在 chunking / 混合检索 / rerank 上，就是在抬这个天花板。
2. **上下文污染**：塞进 top-k 个片段，若其中混入无关片段，LLM 可能被带偏（"lost in the middle"）。
3. **RAG ≠ 万能**：对需要**多跳推理**（"A 的作者的导师是谁"）、**全局综合**（"总结这本 500 页报告"）的问题，朴素 top-k 检索不够，要用 GraphRAG / Agentic RAG / 多步检索（见 `../讲透RAG/03-高级架构.md`）。
4. **被 LLM 长上下文挑战**：当上下文窗口涨到百万 token（Gemini），有人质疑"直接塞全文还要 RAG 干吗"。但成本、精度、可更新性仍让 RAG 在工程上不可替代——长上下文和 RAG 是互补而非替代。

---

## 📌 下一步

- **RAG 的工程深度版**（chunking / 混合检索 / rerank / GraphRAG / 评估）→ `../讲透RAG/`（00 原理 + 01 数学 + 02 工程 + 03 高级 + 04 评估，5 篇全完成）
- **BERT 怎么被改造成句向量机器** → `10-掩码语言模型-BERT.md`（发现 2 的各向异性正是 Sentence-BERT 要微调的原因）
- **词嵌入与分布假设**（vehicle 为什么和 car 向量接近）→ `05-词嵌入-word2vec与GloVe.md`
- **数学：余弦、TF-IDF、ANN 的推导** → `../讲透RAG/01-检索数学.md`
- **上手真稠密检索器** → HuggingFace `sentence-transformers`：`SentenceTransformer('BAAI/bge-base-zh')`

---

## ✍️ 练习

**练习 11.1**（动手）把 `11_bm25_rag.py` 里的 BM25 参数 $k_1$ 从 1.5 改成 0.5（饱和更快）和 5.0（饱和更慢），重跑发现 1。观察：$k_1$ 越小，垃圾页 D7 的分数被压得越狠吗？直觉上 $k_1$ 控制了什么？

**练习 11.2**（思考）发现 2 里 BM25 对所有文档都打 0 分。有人说"那就把 0 分的也算相关，反正没更差的"。请反驳：当所有分数都是 0 时，BM25 实际上把"排序"退化成了什么？为什么这等于"瞎选"？

**练习 11.3**（动手）在发现 2 的查询里加一个"桥梁词"——把查询改成 "how quickly can a **car** move"（加了和 D4/D5 共享的 car）。现在 BM25 还会全零吗？为什么"加一个共享词"就能救活词面检索？这暗示了 query rewriting（查询改写）这类技术的价值。

**练习 11.4**（思考）发现 3 说"检索器是 RAG 的天花板"。请设想：如果用一个非常强的 LLM 当生成器，它能不能"识别出检索回来的资料是错的，然后拒绝回答"？这需要什么能力？现在的 LLM 做得到吗（提示：faithfulness / self-RAG）？

**练习 11.5**（挑战）用 HuggingFace `sentence-transformers` 加载一个真稠密检索器（如 `BAAI/bge-small-en`），把本实验的 8 篇文档编码成向量，重跑发现 2。真神经检索器的余弦和我们的"手写概念向量"打分分布有何不同？哪个更像真 BM25 的"语义补集"？

---

> 配套实验：`experiments/11_bm25_rag.py`。姊妹章节：`10-掩码语言模型-BERT.md`（BERT 句向量）、`05-词嵌入-word2vec与GloVe.md`（分布假设）、`../讲透RAG/`（RAG 工程深度版）。
