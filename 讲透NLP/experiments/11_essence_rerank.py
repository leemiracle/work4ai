#!/usr/bin/env python3
"""
实验 11 · 算法本质补充 —— 两阶段检索 (bi-encoder 召回 + cross-encoder rerank)
==============================================================================
对应文档:
  - 讲透NLP/11-信息检索与RAG.md (原笔记)
  - 讲透NLP/11-讲透笔记-算法经验版.md (算法经验萃取)

补充原实验 11_bm25_rag.py 的盲区 —— 演示 rerank 阶段的算法本质.
原实验只演示了"召回 (retrieval)", 但工业 RAG 标准是两阶段:
  Stage 1 (召回):  bi-encoder, 查询/文档独立编码, 算余弦, 快, 取 top-K (K~50)
  Stage 2 (rerank): cross-encoder, 查询+文档拼接后过模型, 慢但准, 取 top-k (k~5)

为什么需要两阶段? —— 速度精度的权衡.
  bi-encoder 可以预计算文档向量 (1M 文档 = 1M 次编码, 一次性)
  cross-encoder 必须每次查询都重新算 (1M 文档 = 1M 次前向, 每查询)
  所以 cross-encoder 直接用于全库不现实, 只能 rerank 召回的 top-K.

跑法:  python3 -u experiments/11_essence_rerank.py    (~1 秒)
依赖:  仅标准库
"""
import math
import random
from collections import Counter

random.seed(0)

# ============================================================
# 语料 (复用 11_bm25_rag.py 的设计, 简化版)
# ============================================================
DOCS = [
    ("D0", "cats are small carnivorous mammals that hunt mice and small birds"),
    ("D1", "domestic felines spend sixteen hours each day sleeping"),
    ("D2", "dogs are loyal canines descended from wild gray wolves"),
    ("D3", "the modern automobile was invented around eighteen eighty five"),
    ("D4", "electric cars can travel at very high speeds on the open highway"),
    ("D5", "a typical car reaches a top speed of two hundred kilometers per hour"),
    ("D6", "mice are small rodents that eat grain and seeds in fields"),
    ("D7", "cat food cat toys cat beds cat treats catnip products for cat owners"),
]

# 模拟"概念向量" —— 把词映射到 [animal, vehicle, action, speed, object] 5 维语义空间
CONCEPT = {
    "cat":    [0.95, 0.0,  0.1,  0.0,  0.0],
    "cats":   [0.95, 0.0,  0.1,  0.0,  0.0],
    "felines":[0.92, 0.0,  0.0,  0.0,  0.0],
    "mice":   [0.7,  0.0,  0.0,  0.0,  0.0],
    "dog":    [0.6,  0.0,  0.0,  0.0,  0.0],
    "dogs":   [0.6,  0.0,  0.0,  0.0,  0.0],
    "hunt":   [0.2,  0.0,  0.95, 0.0,  0.0],
    "car":    [0.0,  0.95, 0.0,  0.3,  0.0],
    "cars":   [0.0,  0.95, 0.0,  0.3,  0.0],
    "automobile":[0.0,0.95, 0.0,  0.0,  0.0],
    "vehicle":[0.0,  0.95, 0.0,  0.0,  0.0],
    "speed":  [0.0,  0.0,  0.0,  0.95, 0.0],
    "speeds": [0.0,  0.0,  0.0,  0.95, 0.0],
    "fast":   [0.0,  0.0,  0.0,  0.85, 0.0],
    "quickly":[0.0,  0.0,  0.0,  0.85, 0.0],
    "travel": [0.0,  0.0,  0.6,  0.0,  0.0],
    "move":   [0.0,  0.0,  0.6,  0.0,  0.0],
}


def toks(s):
    return [w.lower() for w in s.split()]


def doc_vec(doc_text):
    """bi-encoder 风格: 文档的"概念向量" = 所有词向量的平均"""
    ts = toks(doc_text)
    vecs = [CONCEPT[t] for t in ts if t in CONCEPT]
    if not vecs:
        return [0.0] * 5
    return [sum(v[i] for v in vecs) / len(vecs) for i in range(5)]


def cosine(a, b):
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0: return 0.0
    return sum(a[i]*b[i] for i in range(len(a))) / (na * nb)


# ============================================================
# Stage 1: bi-encoder 召回 (粗排, 快)
# ============================================================
def bi_encoder_retrieve(query, top_K=5):
    """查询/文档各自独立编码, 算余弦, 取 top-K"""
    qv = doc_vec(query)
    scored = [(cosine(qv, doc_vec(d[1])), d[0], d[1]) for d in DOCS]
    scored.sort(reverse=True)
    return scored[:top_K]


# ============================================================
# Stage 2: cross-encoder rerank (精排, 慢但准)
# ============================================================
def cross_encoder_score(query, doc_text):
    """
    cross-encoder 风格: 查询+文档拼接后, 直接算"逐词对位匹配"的总分.
    模拟 cross-encoder 的核心特性 —— 让 q 和 d 的每个词都"互相看到".

    实现: 对 q 的每个概念维度, 检查 d 中是否有"同维度且强度相近"的词.
    比简单的余弦更精细 —— 它能捕捉"q 中 speed 和 d 中 high speed 的细节匹配".
    """
    q_concepts = [(t, CONCEPT[t]) for t in toks(query) if t in CONCEPT]
    d_concepts = [(t, CONCEPT[t]) for t in toks(doc_text) if t in CONCEPT]
    score = 0.0
    # 1. 维度级精细匹配: 对每个概念维度单独打分
    for dim in range(5):
        q_dim = sum(c[dim] for _, c in q_concepts)
        d_dim = sum(c[dim] for _, c in d_concepts)
        # 不只是平均, 而是看"是否两边都强调这个维度"
        if q_dim > 0.3 and d_dim > 0.3:
            score += min(q_dim, d_dim) * 1.5    # 双边强调 → 加权
        elif q_dim > 0.3:
            score -= 0.1                          # 查询强调但文档没有 → 惩罚
    # 2. 直接词重叠奖励 (像 BM25 一样的精确匹配)
    q_toks = set(toks(query))
    d_toks = set(toks(doc_text))
    overlap = len(q_toks & d_toks)
    score += overlap * 0.3
    return score


def cross_encoder_rerank(query, candidates):
    """对召回的候选, 用 cross-encoder 重新打分"""
    scored = [(cross_encoder_score(query, text), did, text) for _, did, text in candidates]
    scored.sort(reverse=True)
    return scored


# ============================================================
# 演示: 两阶段检索 vs 单阶段 bi-encoder
# ============================================================
def section(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)


section("Stage 1: bi-encoder 召回 (粗排, 查询与文档独立编码, 算余弦, 快)")

queries = [
    ("Q1", "cats hunt", {"D0"}),                              # 关键词查询
    ("Q2", "how fast can a vehicle move", {"D4", "D5"}),      # 转述查询
    ("Q3", "top speed of a car", {"D5"}),                     # 精确查询
]

for qid, q, truth in queries:
    print(f"\n  {qid}: '{q}'   (正解 = {truth})")
    cands = bi_encoder_retrieve(q, top_K=5)
    print(f"  bi-encoder top-5 (召回):")
    for sc, did, _ in cands:
        mark = "✓" if did in truth else " "
        print(f"    {mark} {did}: cosine={sc:.3f}")

section("Stage 2: cross-encoder rerank (精排, 查询+文档拼接, 慢但准)")

for qid, q, truth in queries:
    print(f"\n  {qid}: '{q}'   (正解 = {truth})")
    cands = bi_encoder_retrieve(q, top_K=5)
    reranked = cross_encoder_rerank(q, cands)
    print(f"  rerank top-5 (cross-encoder 精排):")
    for sc, did, _ in reranked:
        mark = "✓" if did in truth else " "
        print(f"    {mark} {did}: rerank_score={sc:.3f}")

section("为什么必须两阶段? —— 速度精度的权衡")

print("""
  bi-encoder (Stage 1, 召回):
    - 查询和文档【各自独立】编码 → 文档向量可预计算
    - 1M 文档建一次索引, 之后每次查询只需 1 次查询编码 + 1M 次余弦
    - ANN 加速后, 单次查询 ~10ms
    - 精度: 中等 (查询-文档无深度交互)

  cross-encoder (Stage 2, rerank):
    - 查询+文档【拼接后一起】过模型 → 深度交互
    - 1M 文档 = 1M 次前向传播 (无法预计算, 因为查询要参与)
    - 直接用于全库: 单次查询 ~100s ❌ 不可接受
    - 只 rerank 召回的 top-50: 单次查询 ~5ms ✅ 可接受
    - 精度: 高 (能捕捉 "fast↔high speed" 这种细粒度语义对齐)
  
  → 两阶段 = 把 cross-encoder 的精度"挤"到召回的小集合上, 兼顾速度和精度.""")

# ============================================================
# 算法经验萃取
# ============================================================
section("算法经验萃取")

print("""
  从这份最小实验, 可以萃取的算法经验:

  经验 R1: bi-encoder 双塔是大规模检索的核心架构
           → 查询/文档独立编码, 可预计算, 可 ANN 加速
           → 迁移: 推荐系统双塔召回、广告 query-ad 双塔

  经验 R2: 两阶段 = 漏斗式精度-速度权衡
           → Stage 1 召回 (粗, 快): bi-encoder, 取 top-K (K=50)
           → Stage 2 精排 (细, 慢): cross-encoder, 取 top-k (k=5)
           → 迁移: 推荐召回+排序、广告投放、欺诈检测二阶段、CV 检测+识别

  经验 R3: cross-encoder 精度更高, 因为"查询-文档深度交互"
           → 不是简单算相似度, 而是让 q 和 d 的每个词互相 attend
           → 代价: 不能预计算, 必须每次查询都重算

  完整经验见: 11-讲透笔记-算法经验版.md §9 (R1-R10)
""")

print("=" * 76)
print("实验完成. 配套文档:")
print("  讲透NLP/11-信息检索与RAG.md (原笔记)")
print("  讲透NLP/11-讲透笔记-算法经验版.md (算法经验萃取)")
print("  讲透NLP/experiments/11_bm25_rag.py (原实验: BM25/dense/RRF)")
print("=" * 76)
