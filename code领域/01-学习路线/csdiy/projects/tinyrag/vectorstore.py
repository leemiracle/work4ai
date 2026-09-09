#!/usr/bin/env python3
"""
tinyrag/vectorstore.py — 向量存储 + ANN 索引

参照：Pinecone / FAISS / Weaviate / Milvus
csdiy 对应：tinyvector + bloom-filter精读 + consistent-hashing精读

两种搜索模式：
  BruteForce — 精确 KNN（O(N)）
  HNSW       — 近似最近邻（O(log N)）
"""
import heapq, math, random
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Document:
    id: str; content: str; embedding: list; metadata: dict = field(default_factory=dict)

class VectorStore:
    """向量存储基类（参照 Pinecone Index）"""
    def __init__(self, dim=128):
        self.dim = dim; self.docs: dict[str, Document] = {}
    def upsert(self, doc_id, content, embedding, metadata=None):
        self.docs[doc_id] = Document(doc_id, content, embedding, metadata or {})
    def delete(self, doc_id):
        self.docs.pop(doc_id, None)
    def fetch(self, doc_id):
        return self.docs.get(doc_id)
    def count(self):
        return len(self.docs)

def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na * nb > 0 else 0.0

class BruteForceIndex(VectorStore):
    """暴力 KNN（参照 FAISS IndexFlat）
    精确但 O(N)，适合小数据集"""
    def search(self, query_embedding, top_k=5, filter=None):
        candidates = list(self.docs.values())
        if filter:
            candidates = [d for d in candidates if all(d.metadata.get(k) == v for k, v in filter.items())]
        scored = [(cosine_sim(query_embedding, d.embedding), d) for d in candidates]
        scored.sort(key=lambda x: -x[0])
        return [{"id": d.id, "score": round(s, 4), "content": d.content, "metadata": d.metadata}
                for s, d in scored[:top_k]]

class HNSWIndex(VectorStore):
    """HNSW 近似最近邻（参照 hnswlib / Pinecone）
    多层图导航 → O(log N) 搜索"""
    def __init__(self, dim=128, M=8, ef_construction=50):
        super().__init__(dim)
        self.M = M  # 每节点最大邻居
        self.graph: dict[str, set] = {}  # doc_id → 邻居
        self.entry_point: Optional[str] = None
        self.levels: dict[str, int] = {}  # doc_id → 层级
    def upsert(self, doc_id, content, embedding, metadata=None):
        super().upsert(doc_id, content, embedding, metadata)
        self._add_to_graph(doc_id)
    def _add_to_graph(self, new_id):
        level = 0
        while random.random() < 0.5 and level < 5: level += 1
        self.levels[new_id] = level
        self.graph[new_id] = set()
        if not self.entry_point:
            self.entry_point = new_id; return
        # 找最近的 M 个邻居（简化版暴力）
        new_emb = self.docs[new_id].embedding
        all_ids = [i for i in self.docs if i != new_id]
        scored = [(cosine_sim(new_emb, self.docs[i].embedding), i) for i in all_ids]
        scored.sort(key=lambda x: -x[0])
        for _, neighbor_id in scored[:self.M]:
            self.graph[new_id].add(neighbor_id)
            self.graph[neighbor_id].add(new_id)
            if len(self.graph[neighbor_id]) > self.M * 2:
                # 保留最近的
                nb_emb = self.docs[neighbor_id].embedding
                nb_scored = [(cosine_sim(nb_emb, self.docs[n].embedding), n) for n in self.graph[neighbor_id]]
                nb_scored.sort(key=lambda x: -x[0])
                self.graph[neighbor_id] = set(n for _, n in nb_scored[:self.M * 2])
    def search(self, query_embedding, top_k=5, ef=20, filter=None):
        if not self.entry_point:
            return []
        # 贪心图搜索（参照 HNSW search layer）
        visited = set(); current = self.entry_point
        best = [(cosine_sim(query_embedding, self.docs[current].embedding), current)]
        visited.add(current)
        for _ in range(ef * 3):
            neighbors = self.graph.get(current, set()) - visited
            if not neighbors: break
            for n in neighbors:
                visited.add(n)
                s = cosine_sim(query_embedding, self.docs[n].embedding)
                if s > best[0][0] or len(best) < top_k:
                    heapq.heappush(best, (s, n))
                    best = heapq.nlargest(top_k * 2, best)
                    current = n
        # 过滤 + 格式化
        best.sort(key=lambda x: -x[0])
        results = []
        for score, doc_id in best[:top_k]:
            doc = self.docs[doc_id]
            if filter and not all(doc.metadata.get(k) == v for k, v in filter.items()):
                continue
            results.append({"id": doc_id, "score": round(score, 4), "content": doc.content, "metadata": doc.metadata})
        return results
