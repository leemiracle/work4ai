#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 11 章配套实验：BM25、稠密检索与最小 RAG
======================================================
对应文档: 11-信息检索与RAG.md

只用 Python 标准库（math / collections）。不用任何 NLP 库、不用 numpy、不用向量库。

跑这个脚本，你会看到三个「能跑出来」的结论：

  1.【★ 关键词堆砌骗过原始 TF，骗不过 BM25】
     查询 "cats hunt" 的正解是 D0（既讲猫又讲捕猎）。但语料里有一页"猫粮/猫玩具"
     把 cat 重复了 6 次的产品页 D7。原始词频检索（raw TF×IDF）把垃圾页排第 1
     （6 次 cat 得分 7.69 压过 D0 的"cat+hunt"3.07）；BM25 的 tf 饱和 + 罕见词高 IDF
     把 D0 排回第 1（3.18 vs 2.34）。
     铁证数字：tf 从 1 涨到 6，BM25 的饱和项只从 1.00 涨到 2.00——不是 6 倍。
     「重复堆砌关键词」在 BM25 里几乎买不到排名。

  2.【★ 词汇鸿沟让 BM25 直接归零】
     查询 "how quickly can a motor vehicle move"（汽车能跑多快）的正解是 D4/D5
     （讲 car / speed）。但查询词 {quickly, motor, vehicle, move} 和正解文档
     {car, speeds, reaches, ...} 没有任何表面词重叠——BM25 给【每一篇】文档都打 0 分
     （彻底失明）。一个手写的「概念向量」稠密检索器通过 car↔vehicle、quickly↔speed
     的语义桥接，把正解找回（余弦 ≈ 0.95）。这正是稠密检索（Sentence-BERT）存在的理由。

  3.【★ RAG 的天花板就是它的检索器】
     一个最小 extractive RAG（取 top-1 文档当答案来源）：
         Q1(关键词 "cats hunt")  : BM25 ✓  稠密 ✓
         Q2(转述   "vehicle..." ): BM25 ✗  稠密 ✓
     BM25 在 Q2 上被词汇鸿沟骗走、取回错文档 → 答案错；稠密检索取回正解 → 答案对。
     生成器（这里是抽取式）无法纠正检索错误——检索器是 RAG 的天花板。
     混合检索（RRF 融合两路信号）两种查询全对：每个通道的盲区被另一个覆盖。

自包含，几秒跑完：
    python3 -u experiments/11_bm25_rag.py
"""

import math
from collections import Counter, defaultdict

def P(*a, **kw):
    print(*a, **kw, flush=True)

SEP = "=" * 64

# ============================================================
# 0. 语料：8 篇短文档（英文，纯 ASCII）
#    设计要点：
#    - D7 是"猫"产品页，把 cat 重复 6 次（关键词堆砌 spam）；
#    - D4/D5 讲车速，但用 car/speed；D3 讲汽车发明，用 automobile；
#    - 让"查询词和正解词零表面重叠"的转述查询成为可能（发现 2）。
# ============================================================
DOCS = [
    "cats are small carnivorous mammals that hunt mice and small birds",        # D0
    "domestic felines spend sixteen hours each day sleeping on warm mats",      # D1
    "dogs are loyal canines descended from wild gray wolves",                   # D2
    "the modern automobile was invented around eighteen eighty five",           # D3
    "electric cars can travel at very high speeds on the open highway",         # D4
    "a typical car reaches a top speed of two hundred kilometers per hour",     # D5
    "mice are small rodents that eat grain and seeds in fields",                # D6
    "cat food cat toys cat beds cat treats cat collars catnip products for cat owners",  # D7
]
DID = [f"D{i}" for i in range(len(DOCS))]

STOP = set("the a an of are is was that and each for can at on to per in very how do".split())

def stem(w):
    # 极简后缀剥离：复数 -s → 单数。够这个玩具用（不追求语言学正确）。
    if len(w) > 3 and w.endswith("s"):
        return w[:-1]
    return w

def tokenize(text):
    toks = [w for w in text.lower().replace(".", "").split() if w not in STOP]
    return [stem(t) for t in toks]

DOC_TOKS = [tokenize(d) for d in DOCS]
N = len(DOCS)
AVGDL = sum(len(t) for t in DOC_TOKS) / N
DF = Counter()
for toks in DOC_TOKS:
    for t in set(toks):
        DF[t] += 1

def idf(term):
    df = DF.get(term, 0)
    return math.log(1 + (N - df + 0.5) / (df + 0.5))  # Lucene/标准形式，保证非负


# ============================================================
# 1. 原始 TF×IDF 检索器（不过滤关键词堆砌的"天真"基线）
#    score(d,q) = Σ_{t∈q} tf(t,d) · idf(t)     —— tf 线性，堆多少给多少分。
# ============================================================
def raw_tfidf_scores(query):
    q = tokenize(query)
    scores = [0.0] * N
    for i, toks in enumerate(DOC_TOKS):
        tf = Counter(toks)
        for t in q:
            if t in tf:
                scores[i] += tf[t] * idf(t)
    return scores


# ============================================================
# 2. BM25 检索器（tf 饱和 + 文档长度归一化）——工业词面检索的事实标准
#    score(d,q) = Σ_{t∈q} idf(t) · tf(t,d)·(k1+1) / ( tf(t,d) + k1·(1 − b + b·|d|/avgdl) )
#    k1 控制饱和速度（默认 1.5），b 控制长度归一化强度（默认 0.75）。
# ============================================================
def bm25_scores(query, k1=1.5, b=0.75):
    q = tokenize(query)
    scores = [0.0] * N
    for i, toks in enumerate(DOC_TOKS):
        tf = Counter(toks)
        dl = len(toks)
        norm = (1 - b + b * dl / AVGDL)
        s = 0.0
        for t in q:
            if t in tf:
                f = tf[t]
                s += idf(t) * (f * (k1 + 1)) / (f + k1 * norm)
        scores[i] = s
    return scores


# =================================================-----------
# 3. "稠密"检索器：手写概念向量（模拟 Sentence-BERT 学到的语义）
#    说明：真稠密检索器（bi-encoder）的向量是神经网络在海量语料上预训练出来的，
#    纯标准库无法复现。这里用一个【手写本体】模拟"语义知识"，
#    用来演示「词汇鸿沟」如何被语义桥接——这正是 dense retrieval 的核心价值。
#    OOV（本体里没有的词）返回空向量，模拟"语义向量空白"。
# ============================================================
CONCEPT_VEC = {
    # 动物
    "cat": {"feline": 1, "animal": 1}, "feline": {"feline": 1, "animal": 1},
    "dog": {"canine": 1, "animal": 1}, "canine": {"canine": 1, "animal": 1},
    "mouse": {"rodent": 1, "animal": 1}, "mice": {"rodent": 1, "animal": 1},
    "rodent": {"rodent": 1, "animal": 1},
    "bird": {"prey": 1, "animal": 1}, "wolf": {"canine": 1, "animal": 1},
    "wolve": {"canine": 1, "animal": 1}, "mammal": {"animal": 1},
    # 动作 / 属性
    "hunt": {"prey": 1, "motion": 1}, "eat": {"food": 1},
    "sleep": {"rest": 1}, "sleeping": {"rest": 1},
    "travel": {"motion": 1, "speed": 1}, "move": {"motion": 1, "speed": 1},
    "reach": {"motion": 1}, "reache": {"motion": 1},
    "quickly": {"speed": 1}, "fast": {"speed": 1},
    # 载具
    "car": {"vehicle": 1}, "automobile": {"vehicle": 1}, "vehicle": {"vehicle": 1},
    "motor": {"vehicle": 1}, "highway": {"vehicle": 1, "location": 1},
    "speed": {"speed": 1}, "velocity": {"speed": 1},
    # 场所 / 用品
    "mat": {"location": 1}, "rug": {"location": 1}, "field": {"location": 1},
    "bed": {"rest": 1, "location": 1}, "warm": {"rest": 1},
    # 食物
    "food": {"food": 1}, "treat": {"food": 1}, "catnip": {"food": 1},
    "grain": {"food": 1}, "seed": {"food": 1},
    # 发明
    "invented": {"invention": 1}, "modern": {"invention": 1},
}

def vec_from_tokens(tokens):
    v = defaultdict(float)
    for t in tokens:
        for c, w in CONCEPT_VEC.get(t, {}).items():
            v[c] += w
    return v

def cosine(v1, v2):
    if not v1 or not v2:
        return 0.0
    dot = sum(v1[c] * v2[c] for c in v1 if c in v2)
    n1 = math.sqrt(sum(x * x for x in v1.values()))
    n2 = math.sqrt(sum(x * x for x in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

def dense_scores(query):
    qv = vec_from_tokens(tokenize(query))
    return [cosine(qv, vec_from_tokens(toks)) for toks in DOC_TOKS]


# ============================================================
# 4. 排名 + RRF 混合融合
# ============================================================
def rank(scores):
    # 按 score 降序；同分按索引升序（确定性）
    return sorted(range(N), key=lambda i: (-scores[i], i))

def rrf_scores(query, k=60):
    """Reciprocal Rank Fusion：把多路检索器的【排名】融合。
    工程上最常用的无参数融合法。一个检索器若【完全无信号】（最高分<=0）则弃权，
    避免全零伪排名污染融合——这正是发现 2 里 BM25 在转述查询上的情形。"""
    cand = defaultdict(float)
    for scorer in (bm25_scores, dense_scores):
        s = scorer(query)
        if max(s) <= 0:
            continue  # 该通道失明 → 弃权
        for r, i in enumerate(rank(s)):
            cand[i] += 1.0 / (k + r)
    return [cand.get(i, 0.0) for i in range(N)]


# ============================================================
# 5. 最小 extractive RAG：检索 top-1 → 把它的原文当答案
#    （没有真生成器，但足以暴露"检索器=天花板"这一事实）
# ============================================================
def rag_answer(query, retriever):
    scores = retriever(query)
    top = rank(scores)[0]
    return top, DOCS[top]


# ============================================================
# 6. 打印工具
# ============================================================
def show_ranking(label, query, scorer, top_k=5):
    s = scorer(query)
    order = rank(s)
    P(f"\n  [{label}] 排名前 {top_k}:")
    for r, i in enumerate(order[:top_k]):
        P(f"     {r+1}. {DID[i]}  score={s[i]:.4f}  | {DOCS[i][:52]}")
    return order[0]


# ============================================================
# 主流程
# ============================================================
def main():
    P(SEP)
    P("讲透NLP · Ch11 实验：BM25、稠密检索与最小 RAG")
    P(SEP)
    P(f"语料：{N} 篇文档，平均长度 avgdl={AVGDL:.2f} tokens（去停用词+词干后）")
    for i, d in enumerate(DOCS):
        P(f"  {DID[i]}: {d}")

    # --------------------------------------------------------
    # 发现 1：关键词堆砌骗过原始 TF，骗不过 BM25
    # --------------------------------------------------------
    P("\n" + SEP)
    P("★ 发现 1：关键词堆砌骗过原始 TF，骗不过 BM25")
    P(SEP)
    q1 = "cats hunt"
    P(f'查询：「{q1}」  正解 = D0（既讲猫、又讲捕猎 mice/birds）')
    P(f'注意 D7 是把 cat 重复 {Counter(DOC_TOKS[7])["cat"]} 次的"猫用品"产品页（关键词堆砌）')

    P(f"\n  [原始 TF×IDF]  —— tf 线性，堆多少给多少分：")
    raw1 = raw_tfidf_scores(q1)
    for r, i in enumerate(rank(raw1)[:3]):
        P(f"     {r+1}. {DID[i]}  score={raw1[i]:.3f}")

    P(f"\n  [BM25]  —— tf 饱和 + 罕见词高 IDF：")
    bm1 = bm25_scores(q1)
    for r, i in enumerate(rank(bm1)[:3]):
        P(f"     {r+1}. {DID[i]}  score={bm1[i]:.3f}")

    raw_top = rank(raw1)[0]
    bm_top = rank(bm1)[0]
    P(f"\n  ➜ 原始 TF×IDF 选 top-1 = {DID[raw_top]}  {'✅ 正解' if raw_top==0 else '❌ 被堆砌骗走！'}")
    P(f"  ➜ BM25          选 top-1 = {DID[bm_top]}  {'✅ 正解' if bm_top==0 else '❌'}")

    P("\n  · 为什么 BM25 不被骗？看 tf 饱和（k1=1.5，文档长度=avgdl）：")
    P("       tf(词频)  raw(线性)   BM25饱和项 = tf·(k1+1)/(tf+k1)")
    for f in [1, 2, 4, 6, 8, 16]:
        sat = (f * 2.5) / (f + 1.5)
        P(f"       {f:>3}        {f:>5}        {sat:.3f}")
    P("     → tf 涨 16 倍（1→16），BM25 饱和项只涨 2.29 倍（1.00→2.29），渐近于 k1+1=2.5。")
    P("     → 加上 hunt 是罕见词（只出现在 D0）→ 高 IDF，D0 的两个词都得分，垃圾页 D7 只有 cat。")
    P("     结论：堆砌关键词在 BM25 里几乎买不到排名。")

    # --------------------------------------------------------
    # 发现 2：词汇鸿沟让 BM25 直接归零
    # --------------------------------------------------------
    P("\n" + SEP)
    P("★ 发现 2：词汇鸿沟让 BM25 直接归零")
    P(SEP)
    q2 = "how quickly can a motor vehicle move"
    P(f'查询：「{q2}」')
    P(f'  正解 = D4/D5（讲 car / speed）。去停用词+词干后查询词 = {tokenize(q2)}')
    P(f'  D4 tokens = {DOC_TOKS[4]}')
    P(f'  D5 tokens = {DOC_TOKS[5]}')
    P(f'  表面词重叠 = {{}} （car/vehicle、quickly/speed、move/travel 全是【同义不同形】）')

    bm2 = bm25_scores(q2)
    P(f"\n  [BM25] 每篇文档得分：{[round(x,3) for x in bm2]}")
    P(f"  ➜ BM25 对【全部 8 篇】都打 0 分 —— 彻底失明！top-1 只能靠索引顺序瞎选。")

    dn2 = dense_scores(q2)
    P(f"\n  [稠密/概念向量] 每篇文档余弦：{[round(x,3) for x in dn2]}")
    dn2_top = rank(dn2)[0]
    P(f"  ➜ 稠密检索选 top-1 = {DID[dn2_top]}  score={dn2[dn2_top]:.3f}  "
      f"{'✅ 正解' if dn2_top in (4,5) else '❌'}")
    P("     car↔vehicle（都是 vehicle 维）、quickly↔speed（都是 speed 维）—— 语义桥接跨过词汇鸿沟。")
    P("     这正是 Sentence-BERT / DPR 这类 bi-encoder 稠密检索器存在的全部理由：")
    P("     把「表面词形」换成「预训练学到的语义」，匹配同义/转述。")

    # --------------------------------------------------------
    # 发现 3：RAG 的天花板就是它的检索器
    # --------------------------------------------------------
    P("\n" + SEP)
    P("★ 发现 3：RAG 的天花板就是它的检索器")
    P(SEP)
    cases = [
        ("Q1 关键词", "cats hunt",                         {0}),
        ("Q2 转述  ", "how quickly can a motor vehicle move", {4, 5}),
    ]
    retrievers = [
        ("BM25 检索 ", bm25_scores),
        ("稠密检索 ", dense_scores),
        ("RRF 混合 ", rrf_scores),
    ]
    P("  最小 extractive RAG：取 top-1 文档原文当答案来源，检查 top-1 是否∈正解集\n")
    P("  " + " | ".join(f"{name:<10}" for name, _ in retrievers + [(" ", None)]))
    P("  " + "-" * 50)
    for cname, q, gold in cases:
        row = []
        for rname, rfn in retrievers:
            top, _ = rag_answer(q, rfn)
            ok = "✅" if top in gold else "❌"
            row.append(f"{ok} {DID[top]}")
        P(f"  {cname} | " + " | ".join(f"{c:<10}" for c in row))

    P("\n  ➜ BM25 在 Q2（转述）上被词汇鸿沟骗走 → 取回错文档 → 答案错。")
    P("  ➜ 稠密检索在 Q2 上靠语义桥接取回正解 → 答案对。")
    P("  ➜ RRF 混合（两路排名融合）两种查询全对——每个通道的盲区被另一个覆盖。")
    P("\n  关键洞察：extractive RAG 的答案完全来自 top-1 文档，【生成器无法纠正检索错误】。")
    P("  → 检索质量 = RAG 质量的天花板。这就是为什么工业界把大量精力花在")
    P("    chunking / 混合检索 / rerank 上（见姊妹项目 ../讲透RAG/02-工程组件.md）。")

    P("\n" + SEP)
    P("三个反直觉发现，全部跑通。")
    P(SEP)


if __name__ == "__main__":
    main()
