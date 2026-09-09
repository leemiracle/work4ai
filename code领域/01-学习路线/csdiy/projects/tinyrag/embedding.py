#!/usr/bin/env python3
"""
tinyrag/embedding.py — 文本嵌入模型

参照：sentence-transformers / OpenAI embeddings / BGE
csdiy 对应：tinysearch + tinyvector + AI核心

三种嵌入方式：
  HashEmbedding — 哈希到固定维度（无训练，快速但粗糙）
  TFIDFEmbedding — TF-IDF 加权（经典 IR 方法）
  BagOfWordsEmbedding — 词袋模型
"""
import hashlib, math, re
from collections import Counter

def tokenize(text):
    """简单分词（参照 tinysearch 的 tokenizer）"""
    text = text.lower()
    return re.findall(r"[\u4e00-\u9fa5]|[a-z0-9]+", text)

class HashEmbedding:
    """哈希嵌入（参照 hashing trick / Bloom filter 原理）
    优点：无需训练，固定维度，可处理任意文本
    缺点：无语义信息（只编码词频模式）"""
    def __init__(self, dim=128):
        self.dim = dim
    def embed(self, text):
        tokens = tokenize(text)
        vec = [0.0] * self.dim
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        # L2 归一化
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

class TFIDFEmbedding:
    """TF-IDF 嵌入（参照 Elasticsearch BM25 变体）
    需要 corpus 统计 IDF"""
    def __init__(self, dim=128):
        self.dim = dim
        self.idf = {}  # token → idf 值
        self.token_to_dim = {}  # token → 维度映射
    def fit(self, corpus):
        """从语料计算 IDF（参照 Elasticsearch 分析器）"""
        doc_freq = Counter()
        for doc in corpus:
            for token in set(tokenize(doc)):
                doc_freq[token] += 1
        N = len(corpus)
        for token, freq in doc_freq.items():
            self.idf[token] = math.log((N + 1) / (freq + 1)) + 1
        # 映射到固定维度
        for i, token in enumerate(sorted(self.idf.keys())):
            self.token_to_dim[token] = i % self.dim
    def embed(self, text):
        tokens = tokenize(text)
        tf = Counter(tokens)
        vec = [0.0] * self.dim
        for token, freq in tf.items():
            if token in self.idf:
                dim_idx = self.token_to_dim.get(token, 0)
                vec[dim_idx] += freq * self.idf[token]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

def cosine_similarity(a, b):
    """余弦相似度（参照 Pinecone 默认度量）"""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na * nb > 0 else 0.0

def batch_embed(texts, model="hash", dim=128, corpus=None):
    """批量嵌入"""
    if model == "tfidf" and corpus:
        emb = TFIDFEmbedding(dim)
        emb.fit(corpus)
    else:
        emb = HashEmbedding(dim)
    return [emb.embed(text) for text in texts]
