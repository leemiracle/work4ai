"""
CS329Z HW1 Part A 进阶 - Hybrid Search (BM25 + Dense)

为什么需要 Hybrid Search？
- 纯 dense（向量）：捕获语义，但错过关键词（如人名/产品名）
- 纯 sparse (BM25)：精确匹配关键词，但不懂同义/上下文
- Hybrid：两者加权融合 = 生产 RAG 系统标配

参考：
- BM25: Robertson & Zaragoza 2009 "The Probabilistic Relevance Framework: BM25 and Beyond"
- Hybrid: Gao et al. 2024 "Modular RAG" arXiv 2407.21059
"""
from __future__ import annotations
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class BM25Doc:
    id: str
    tokens: list[str]


class SimpleBM25:
    """简化版 BM25（无外部依赖）"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: list[BM25Doc] = []
        self.doc_freq: dict[str, int] = defaultdict(int)  # term -> # docs containing
        self.avg_len: float = 0.0
        self.N: int = 0

    def fit(self, documents: list[tuple[str, str]]):
        """documents: [(id, content), ...]"""
        self.docs = []
        total_len = 0
        for doc_id, content in documents:
            tokens = self._tokenize(content)
            self.docs.append(BM25Doc(id=doc_id, tokens=tokens))
            total_len += len(tokens)
            for term in set(tokens):
                self.doc_freq[term] += 1

        self.N = len(self.docs)
        self.avg_len = total_len / self.N if self.N else 0

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+', text.lower())

    def score(self, query: str) -> dict[str, float]:
        """返回 {doc_id: bm25_score}"""
        query_terms = self._tokenize(query)
        scores: dict[str, float] = defaultdict(float)

        for doc in self.docs:
            tf = Counter(doc.tokens)
            doc_len = len(doc.tokens)
            for term in query_terms:
                if term not in tf:
                    continue
                # IDF
                df = self.doc_freq.get(term, 0)
                idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
                # TF normalization
                tf_val = tf[term]
                norm = tf_val * (self.k1 + 1) / (
                    tf_val + self.k1 * (1 - self.b + self.b * doc_len / self.avg_len)
                )
                scores[doc.id] += idf * norm

        return dict(scores)


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    """Min-max normalize scores to [0, 1]"""
    if not scores:
        return {}
    lo, hi = min(scores.values()), max(scores.values())
    if hi == lo:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


class HybridSearcher:
    """Hybrid: α * BM25 + (1-α) * Dense"""

    def __init__(self, bm25: SimpleBM25, dense_searcher, alpha: float = 0.5):
        """
        bm25: SimpleBM25 instance (fit 后)
        dense_searcher: callable(query, top_k) -> [(chunk_id, score), ...]
        alpha: BM25 权重（0 = 纯 dense, 1 = 纯 sparse）
        """
        self.bm25 = bm25
        self.dense_search = dense_searcher
        self.alpha = alpha

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """返回 [(chunk_id, hybrid_score), ...]"""
        # Sparse
        bm25_scores = self.bm25.score(query)
        bm25_norm = normalize_scores(bm25_scores)

        # Dense
        dense_results = self.dense_search(query, top_k=top_k * 2)
        dense_scores = {cid: s for cid, s in dense_results}
        dense_norm = normalize_scores(dense_scores)

        # Fusion
        all_ids = set(bm25_norm) | set(dense_norm)
        hybrid = {}
        for cid in all_ids:
            s_bm25 = bm25_norm.get(cid, 0)
            s_dense = dense_norm.get(cid, 0)
            hybrid[cid] = self.alpha * s_bm25 + (1 - self.alpha) * s_dense

        return sorted(hybrid.items(), key=lambda x: -x[1])[:top_k]


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("Hybrid Search 测试")
    print("=" * 60)

    docs = [
        ("d1", "The Transformer architecture uses self-attention."),
        ("d2", "BERT is bidirectional encoder for language understanding."),
        ("d3", "GPU acceleration speeds up neural network training."),
        ("d4", "CUDA is the programming model for NVIDIA GPUs."),
        ("d5", "RLHF trains language models with human feedback."),
    ]

    bm25 = SimpleBM25()
    bm25.fit(docs)

    # Mock dense searcher (假设它工作得很好)
    def mock_dense(query: str, top_k: int = 5):
        # 模拟 dense embedding 把 "GPU" 和 "CUDA" 视为相关
        if "GPU" in query or "graphics" in query:
            return [("d3", 0.9), ("d4", 0.85), ("d1", 0.3)]
        if "transformer" in query.lower():
            return [("d1", 0.95), ("d2", 0.4)]
        return [("d1", 0.5)]

    hybrid = HybridSearcher(bm25, mock_dense, alpha=0.5)

    queries = [
        "GPU",
        "Transformer architecture",
        "CUDA programming",  # 关键词，BM25 应该强
        "attention mechanism",  # 语义，dense 应该强
    ]

    for q in queries:
        print(f"\n🔍 Query: '{q}'")
        print("   BM25 only:")
        for cid, score in sorted(bm25.score(q).items(), key=lambda x: -x[1])[:3]:
            print(f"     {cid}: {score:.3f}")
        print("   Hybrid:")
        for cid, score in hybrid.search(q, top_k=3):
            print(f"     {cid}: {score:.3f}")
