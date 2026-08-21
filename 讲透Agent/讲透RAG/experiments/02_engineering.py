"""
实验 02 — RAG 工程组件: chunk 切分 + 混合检索(TF-IDF+LSA) + rerank 概念
对应文档: 讲透RAG/02-工程组件.md
核心结论:
  1. chunk: 长文档必须切分(embedding有长度上限+检索精度), 固定长度+overlap 最常用
  2. 混合检索: 词面(TF-IDF) + 语义(LSA/神经) 分数融合, 取长补短
  3. rerank: 检索top-k后用交叉编码器精排, 大幅提升精度(但慢)
跑法: python3 -u 02_engineering.py
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

def P(*a): print(*a, flush=True)

# ============ Part 1: chunk 切分 ============
P("="*60); P("Part 1: chunk —— 长文档切分(固定长度+重叠)"); P("="*60)
long_doc = ("DeepSeek-V3是2024年12月发布的大模型。它有671B总参数采用MoE架构。"
            "每个token仅激活37B参数。支持128K上下文长度。训练用了14.8T高质量token。"
            "在多数基准上媲美GPT-4o但训练成本仅557万美元。")
size, overlap = 24, 6
chunks=[]; i=0
while i < len(long_doc):
    chunks.append(long_doc[i:i+size]); i += size - overlap
P("原文 %d 字, chunk_size=%d, overlap=%d → 切成 %d 块:" % (len(long_doc), size, overlap, len(chunks)))
for k,c in enumerate(chunks): P("  chunk%d: %s"%(k,c))
P("==> 切分是RAG必做: embedding有长度上限, 且短块检索更精准. overlap防止语义被截断.\n")

# ============ Part 2: 混合检索 (词面 TF-IDF + 语义 LSA) ============
P("="*60); P("Part 2: 混合检索 —— 词面 + 语义 分数融合"); P("="*60)
docs = ["DeepSeek-V3有671B参数MoE架构", "LoRA低秩微调省参数",
        "汽车发动机需要定期保养", "猫是常见的家庭宠物", "大模型参数量决定能力"]
tfidf = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,2))
X_sp = tfidf.fit_transform(docs)
# LSA: TF-IDF 降维成稠密语义向量(神经embedding的廉价替身)
lsa = TruncatedSVD(n_components=min(4, len(docs)-1), random_state=0)
X_dn = lsa.fit_transform(X_sp)
q = "模型有多少参数"
q_sp = tfidf.transform([q]); q_dn = lsa.transform(q_sp)
sim_sp = cosine_similarity(q_sp, X_sp).flatten()   # 词面
sim_dn = cosine_similarity(q_dn, X_dn).flatten()   # 语义(LSA)
hybrid = 0.4*sim_sp + 0.6*sim_dn                    # 混合
P("Q: '%s'  混合权重: 词面0.4 + 语义0.6" % q)
P("%-4s%10s%10s%10s"%("doc","词面","语义","混合"))
for i in range(len(docs)):
    P("[%-2d] %8.2f%10.2f%10.2f  %s"%(i, sim_sp[i], sim_dn[i], hybrid[i], docs[i][:18]))
P("==> 词面抓精确词('参数'), 语义抓概念('模型/参数量'), 混合取长补短.")
P("    实战: 向量(神经embedding) + BM25(词面) 用 RRF(Reciprocal Rank Fusion) 融合.\n")

# ============ Part 3: rerank ============
P("="*60); P("Part 3: rerank —— 检索后用交叉编码器精排"); P("="*60)
P("两阶段: ① 向量检索 top-20(快, 召回多但不够精) → ② reranker 对这20个逐个")
P("  用 cross-encoder(query,doc)打分精排, 取top-3(慢但精).")
P("区别: 检索用 bi-encoder(query/doc分别编码再比), rerank用 cross-encoder(联合编码,")
P("  交互更深, 更准但慢). 代表reranker: bge-reranker, Cohere Rerank.")
P("==> 工业RAG标配: 混合检索 → rerank top-3 → 注入prompt. 召回率+精度双高.")
