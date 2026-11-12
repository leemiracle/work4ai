"""
实验 00 — 为什么需要 RAG: LLM 的知识三问题 + 最小检索演示
对应文档: 讲透RAG/00-为什么需要RAG.md
核心结论:
  1. LLM 知识三问题: 幻觉(编造)、时效(过时)、私有(不知道) —— 都因知识在参数里
  2. RAG = 检索相关文档 → 注入 prompt → LLM 基于文档生成 (给 LLM 接"外部记忆")
  3. 检索用 TF-IDF/向量相似度, 找"相关的少数", 而非塞全部(成本+噪声)
  4. 三选一: 改行为用微调, 注知识用 RAG, 临时用 prompt
跑法: python3 -u 00_why_rag.py
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def P(*a): print(*a, flush=True)

P("="*60); P("Part 1: LLM 的知识三问题"); P("="*60)
P("  ① 幻觉: 'DeepSeek-V3 有多少参数?' LLM 可能编一个看似合理的数(如175B)")
P("  ② 时效: '今天股市如何?' 训练截止后的事, LLM 不知道(会瞎编或拒答)")
P("  ③ 私有: '我们公司2025年Q3营收?' 内部数据, LLM 从没见过")
P("根因: LLM 的知识是【参数化】的(训练时固化在权重里), 无法事后更新/核实.")
P("解法: RAG 给它接【非参数化】知识 —— 实时检索外部文档, 基于文档回答.\n")

# ============ Part 2: 最小 RAG (TF-IDF 检索) ============
P("="*60); P("Part 2: 最小 RAG —— TF-IDF 检索相关文档"); P("="*60)
# 一个迷你知识库 (模拟"外部记忆")
docs = [
    "DeepSeek-V3 于2024年12月发布, 671B参数, 采用MoE混合专家架构, 每token激活37B.",
    "LoRA 是2021年Hu等人提出的参数高效微调, 用低秩分解ΔW=BA, 只训1%参数.",
    "Transformer 由 Google 2017年在 Attention Is All You Need 中提出, 基于自注意力.",
    "公司2025年Q3营收 8.2亿元, 同比增长45%, 主要由Agent产品线贡献.",
    "QLoRA 把基座量化到4bit再加LoRA, 让70B模型单卡可训.",
    "Retrieval-Augmented Generation (RAG) 由 Lewis 等2020年提出, 检索+生成.",
]
P("知识库 %d 篇文档 (LLM 的'外部记忆'):" % len(docs))
for i,d in enumerate(docs): P("  [%d] %s"%(i,d))

vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,3))
X = vec.fit_transform(docs)   # 文档向量化

queries = [
    "DeepSeek V3 的参数量是多少?",
    "公司Q3营收多少?",
    "怎么用很少的参数微调大模型?",
]
P("\n检索 top-2 (TF-IDF 余弦相似度):")
for q in queries:
    qv = vec.transform([q])
    sims = cosine_similarity(qv, X).flatten()
    top2 = sims.argsort()[::-1][:2]
    P("\n  Q: %s" % q)
    for i in top2:
        P("    [%.2f] %s" % (sims[i], docs[i][:40]+"..."))

P("\n==> 检索精准定位到相关文档. 把这些文档注入 prompt:")
P('    "基于以下资料回答: {检索到的文档} 问题: {query}"')
P("    LLM 就能基于事实回答(而非幻觉). 这就是 RAG 的核心.")
P("    注: 本机无本地LLM, 检索用TF-IDF; 真实RAG用神经网络embedding(下篇)+LLM生成.\n")

# ============ Part 3: 为什么不塞全部文档进 prompt? ============
P("="*60); P("Part 3: 为什么检索, 而不塞全部进 prompt?"); P("="*60)
P("  ① 上下文长度限制(虽长但有上限, 且超长注意力变差)")
P("  ② 成本: input token 按量计费, 塞1万篇文档=烧钱")
P("  ③ 噪声: 无关文档干扰, LLM 可能被误导(lost in the middle)")
P("  ④ 时效: 文档库可实时更新, 检索即时反映最新; 塞prompt要重传")
P("==> 检索是'用相关性筛选', 把'海量文档'压成'少数相关的', 兼顾质量与成本.\n")

# ============ Part 4: 三选一 ============
P("="*60); P("Part 4: 知识注入三选一"); P("="*60)
P("  改【行为/风格/格式】 → 微调(LoRA)")
P("  注【知识/事实/最新】 → RAG")
P("  临时【适应/可溯源】 → Prompt")
P("  常组合: LoRA调行为 + RAG注知识")
