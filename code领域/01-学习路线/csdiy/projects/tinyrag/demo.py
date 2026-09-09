#!/usr/bin/env python3
"""tinyrag/demo.py — RAG 系统端到端演示"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinyrag.pipeline import RAGPipeline

def main():
    print("=" * 60)
    print("  tinyrag — RAG 检索增强生成 端到端演示")
    print("  参照 LangChain + LlamaIndex + Pinecone")
    print("=" * 60)

    rag = RAGPipeline(embedding_model="hash", index_type="hnsw", dim=64, chunk_size=80, overlap=20)

    # ─── INGEST ───
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 1: 文档入库 (INGEST)     │")
    print("└─────────────────────────────────┘\n")
    docs = {
        "llm_guide": """
        Large Language Models like GPT-4 use transformer architecture with multi-head attention.
        Training requires massive text corpora and GPU clusters. The model learns to predict
        the next token in a sequence. Fine-tuning with LoRA allows adapting the model to
        specific tasks with minimal parameters. Quantization to INT8 or INT4 reduces memory
        usage significantly, enabling deployment on consumer hardware.
        """,
        "rag_paper": """
        Retrieval-Augmented Generation combines a retriever with a generator.
        The retriever finds relevant documents from a knowledge base using vector similarity.
        The generator (LLM) produces answers conditioned on retrieved context.
        RAG outperforms pure generation on factual QA because it grounds answers in real data.
        Key components: document chunking, embedding model, vector database, and LLM.
        """,
        "vector_db": """
        Vector databases store high-dimensional embeddings for similarity search.
        Popular options include Pinecone, Weaviate, Milvus, and FAISS.
        ANN algorithms like HNSW provide O(log N) approximate nearest neighbor search.
        Bloom filters can pre-filter candidates to reduce disk IO.
        Consistent hashing enables horizontal scaling across nodes.
        """,
    }
    for doc_id, text in docs.items():
        text = " ".join(text.split())  # 去多余空白
        n = rag.ingest(doc_id, text)
        print(f"  {doc_id}: {n} chunks")

    print(f"\n  索引: {rag.stats()}")

    # ─── RETRIEVE ───
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 2: 向量检索 (RETRIEVE)   │")
    print("└─────────────────────────────────┘\n")
    queries = ["What is LoRA fine-tuning?", "How does RAG work?", "What are ANN algorithms?"]
    for q in queries:
        results = rag.retrieve(q, top_k=2)
        print(f"  Q: {q}")
        for r in results:
            print(f"    [{r['id']:30s}] score={r['score']:.3f} → {r['content'][:60]}...")
        print()

    # ─── AUGMENT ───
    print("┌─────────────────────────────────┐")
    print("│  Phase 3: Prompt 增强 (AUGMENT) │")
    print("└─────────────────────────────────┘\n")
    query = "How does vector search work?"
    prompt, sources = rag.augment(query, top_k=2)
    print(f"  Query: {query}")
    print(f"  Sources: {[s['metadata']['doc_id'] for s in sources]}")
    print(f"\n  Augmented Prompt:\n  {'─'*50}")
    for line in prompt.split("\n")[:8]:
        print(f"  {line}")
    print(f"  {'─'*50}")

    # ─── EVALUATE ───
    print("\n┌─────────────────────────────────┐")
    print("│  Phase 4: 检索质量评估          │")
    print("└─────────────────────────────────┘\n")
    eval_set = [
        ("transformer architecture", "llm_guide"),
        ("retrieval augmented", "rag_paper"),
        ("HNSW nearest neighbor", "vector_db"),
        ("quantization INT8", "llm_guide"),
        ("Pinecone Weaviate", "vector_db"),
    ]
    metrics = rag.evaluate_retrieval(eval_set, top_k=3)
    print(f"  Recall@3 = {metrics['recall@k']:.0%} ({metrics['hits']}/{metrics['total_queries']} queries hit)")

    print(f"\n{'='*60}")
    print(f"  tinyrag = embedding.py + vectorstore.py + pipeline.py + server.py")
    print(f"  完整 RAG 栈: 嵌入 → ANN 索引 → 检索 → 增强 → 评估 → API")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
