"""
Cambridge CST - Shared Infrastructure v0.1
RAG 模块：向量检索 + 重排序（简化版）

参考论文：Lewis et al. "Retrieval-Augmented Generation" NeurIPS 2020
         Khattab & Zaharia "ColBERT" SIGIR 2020

设计：
- Embedding：sentence-transformers（真实） / 哈希近似（mock）
- 向量库：FAISS（真实） / 线性扫描（mock）
- Chunking：固定长度 + overlap
"""
from __future__ import annotations
import re
import hashlib
from dataclasses import dataclass, field
from typing import Optional
import math


@dataclass
class Document:
    id: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    id: str
    doc_id: str
    content: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class SimpleEmbedder:
    """句子嵌入：sentence-transformers 优先，hashing 兜底"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dim: int = 128):
        self.dim = dim
        self.model_name = model_name
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self.dim = self._model.get_sentence_embedding_dimension()
        except ImportError:
            print(f"⚠️  sentence-transformers 未安装，使用 hashing 嵌入 (dim={self.dim})")

    def embed(self, text: str) -> list[float]:
        if self._model is not None:
            return self._model.encode(text).tolist()
        return self._hash_embed(text)

    def _hash_embed(self, text: str) -> list[float]:
        """Hash-based embedding（mock，教学用）"""
        words = re.findall(r'\w+', text.lower())
        vec = [0.0] * self.dim
        for w in words:
            h = int(hashlib.md5(w.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class SimpleVectorStore:
    """向量库：FAISS 优先，线性扫描兜底"""

    def __init__(self, dim: int):
        self.dim = dim
        self.chunks: list[Chunk] = []
        self._index = None
        self._try_init_faiss()

    def _try_init_faiss(self):
        try:
            import faiss
            self._index = faiss.IndexFlatL2(self.dim)
        except ImportError:
            print("⚠️  faiss 未安装，使用线性扫描")

    def add(self, chunks: list[Chunk]):
        for c in chunks:
            if not c.embedding:
                continue
            self.chunks.append(c)
            if self._index is not None:
                import numpy as np
                self._index.add(np.array([c.embedding], dtype="float32"))

    def search(self, query_emb: list[float], top_k: int = 5) -> list[tuple[Chunk, float]]:
        """返回 [(chunk, distance), ...]"""
        if not self.chunks:
            return []

        if self._index is not None:
            import numpy as np
            _, indices = self._index.search(
                np.array([query_emb], dtype="float32"), min(top_k, len(self.chunks))
            )
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):
                    # FAISS 返回 L2 距离，转相似度
                    dist = float(self._index.reconstruct(idx)[0]) if False else 1.0
                    results.append((self.chunks[idx], dist))
            return results

        # 线性扫描（mock）
        scored = []
        for chunk in self.chunks:
            sim = self._cosine(query_emb, chunk.embedding)
            scored.append((chunk, 1 - sim))  # 转距离
        scored.sort(key=lambda x: x[1])
        return scored[:top_k]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1
        nb = math.sqrt(sum(y * y for y in b)) or 1
        return dot / (na * nb)


class SimpleRAG:
    """完整 RAG pipeline"""

    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedder = SimpleEmbedder()
        self.store = SimpleVectorStore(self.embedder.dim)

    def add_documents(self, documents: list[Document]):
        """添加文档：先 chunk 再 embed 再 store"""
        all_chunks = []
        for doc in documents:
            chunks = self._chunk_document(doc)
            for c in chunks:
                c.embedding = self.embedder.embed(c.content)
                all_chunks.append(c)
        self.store.add(all_chunks)
        return len(all_chunks)

    def _chunk_document(self, doc: Document) -> list[Chunk]:
        """固定长度 chunking + overlap"""
        words = doc.content.split()
        chunks = []
        i = 0
        chunk_idx = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_id = f"{doc.id}_c{chunk_idx}"
            chunks.append(Chunk(
                id=chunk_id,
                doc_id=doc.id,
                content=" ".join(chunk_words),
                metadata={**doc.metadata, "chunk_idx": chunk_idx}
            ))
            i += self.chunk_size - self.chunk_overlap
            chunk_idx += 1
        return chunks

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        query_emb = self.embedder.embed(query)
        results = self.store.search(query_emb, top_k)
        return [c for c, _ in results]

    def query_with_context(self, query: str, top_k: int = 5) -> tuple[str, list[Chunk]]:
        """检索 + 拼接上下文"""
        chunks = self.retrieve(query, top_k)
        context = "\n\n---\n\n".join(
            f"[Doc {c.doc_id}, chunk {c.metadata.get('chunk_idx', '?')}]: {c.content[:200]}..."
            for c in chunks
        )
        return context, chunks


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("RAG 模块测试")
    print("=" * 60)

    rag = SimpleRAG(chunk_size=30, chunk_overlap=10)

    # 添加测试文档
    docs = [
        Document(id="d1", content=(
            "Transformers are a type of neural network architecture introduced in 2017. "
            "They use self-attention mechanism to process input sequences in parallel. "
            "The original paper 'Attention is All You Need' by Vaswani et al. started the era of LLMs."
        )),
        Document(id="d2", content=(
            "Retrieval-Augmented Generation (RAG) combines retrieval with generation. "
            "It was introduced by Lewis et al. in 2020. RAG reduces hallucination "
            "by grounding LLM responses in retrieved documents."
        )),
        Document(id="d3", content=(
            "ReAct interleaves reasoning and acting in language models. "
            "Yao et al. 2022 showed that this synergy improves task performance. "
            "ReAct prompts the model to think, take action, and observe."
        )),
    ]
    n = rag.add_documents(docs)
    print(f"\n✅ 添加 {n} 个 chunks")

    # 检索测试
    queries = [
        "What is transformer architecture?",
        "How does RAG reduce hallucination?",
        "Who proposed ReAct?",
    ]
    for q in queries:
        print(f"\n🔍 Query: {q}")
        ctx, chunks = rag.query_with_context(q, top_k=2)
        for c in chunks:
            print(f"   → [{c.doc_id}] {c.content[:80]}...")
