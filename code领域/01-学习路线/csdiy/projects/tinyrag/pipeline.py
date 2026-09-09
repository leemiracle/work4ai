#!/usr/bin/env python3
"""
tinyrag/pipeline.py — RAG 完整管道

参照：LangChain RAG / LlamaIndex / RAG from scratch
csdiy 对应：tinyrag(embedding+vectorstore) + tinyllm + tinysearch

完整流程：
  1. INGEST: 文档 → 切分 → 嵌入 → 存入向量库
  2. RETRIEVE: 查询 → 嵌入 → 相似度搜索 → Top-K 文档
  3. AUGMENT: 查询 + 检索文档 → 增强 Prompt
  4. GENERATE: LLM 基于 Prompt 生成回答
"""
import os, sys, re, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinyrag.embedding import HashEmbedding, TFIDFEmbedding, tokenize, cosine_similarity, batch_embed
from tinyrag.vectorstore import HNSWIndex, BruteForceIndex

def chunk_text(text, chunk_size=200, overlap=50):
    """文本切分（参照 LangChain RecursiveCharacterTextSplitter）"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk) > 20:
            chunks.append(chunk)
    return chunks

class RAGPipeline:
    """RAG 管道（参照 LangChain RetrievalQA）"""
    def __init__(self, embedding_model="hash", index_type="hnsw", dim=128, chunk_size=200, overlap=50):
        self.dim = dim; self.chunk_size = chunk_size; self.overlap = overlap
        # 选择嵌入模型
        if embedding_model == "tfidf":
            self.embedder = TFIDFEmbedding(dim); self._needs_fit = True
        else:
            self.embedder = HashEmbedding(dim); self._needs_fit = False
        # 选择索引
        if index_type == "hnsw":
            self.store = HNSWIndex(dim=dim)
        else:
            self.store = BruteForceIndex(dim=dim)
        self.corpus = []

    # ─── INGEST ───
    def ingest(self, doc_id, text, metadata=None):
        """文档入库：切分 → 嵌入 → 存储（参照 LlamaIndex ingestion）"""
        self.corpus.append(text)
        if self._needs_fit:
            self.embedder.fit(self.corpus)
        chunks = chunk_text(text, self.chunk_size, self.overlap)
        for i, chunk in enumerate(chunks):
            emb = self.embedder.embed(chunk)
            chunk_id = f"{doc_id}_chunk_{i}"
            meta = {"doc_id": doc_id, "chunk_idx": i, **(metadata or {})}
            self.store.upsert(chunk_id, chunk, emb, meta)
        return len(chunks)

    # ─── RETRIEVE ───
    def retrieve(self, query, top_k=5, filter=None):
        """检索（参照 LangChain retriever.invoke）"""
        query_emb = self.embedder.embed(query)
        results = self.store.search(query_emb, top_k=top_k, filter=filter)
        return results

    # ─── AUGMENT ───
    def augment(self, query, top_k=3):
        """构建增强 Prompt（参照 RAG context injection）"""
        results = self.retrieve(query, top_k=top_k)
        context_parts = [f"[Source {i+1}] ({r['metadata'].get('doc_id','?')})\n{r['content']}"
                         for i, r in enumerate(results)]
        context = "\n\n".join(context_parts)
        prompt = f"""Based on the following retrieved context, answer the question.
If the answer is not in the context, say "I don't know based on the provided context."

Context:
{context}

Question: {query}

Answer:"""
        return prompt, results

    # ─── EVALUATE ───
    def evaluate_retrieval(self, queries_with_expected, top_k=5):
        """评估检索质量（参照 RAGAS metrics）
        queries_with_expected: [(query, expected_doc_id), ...]"""
        total = len(queries_with_expected); hits = 0
        for query, expected_doc_id in queries_with_expected:
            results = self.retrieve(query, top_k=top_k)
            doc_ids = {r["metadata"].get("doc_id") for r in results}
            if expected_doc_id in doc_ids: hits += 1
        recall_at_k = hits / total if total > 0 else 0
        return {"recall@k": recall_at_k, "total_queries": total, "hits": hits, "k": top_k}

    def stats(self):
        return {"documents": self.store.count(), "dim": self.dim,
                "index_type": type(self.store).__name__,
                "embedder": type(self.embedder).__name__}
