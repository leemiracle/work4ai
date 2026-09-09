# tinyrag — RAG 系统（参照 LangChain + LlamaIndex + Pinecone）

> 从零实现完整的 RAG（检索增强生成）技术栈。

## 模块清单

| 文件 | 参照 | 核心内容 |
|------|------|---------|
| `embedding.py` | sentence-transformers / BGE | Hash + TF-IDF 嵌入 + 余弦相似度 |
| `vectorstore.py` | Pinecone / FAISS / hnswlib | BruteForce KNN + HNSW ANN |
| `pipeline.py` | LangChain RAG / LlamaIndex | 文档切分 + 检索 + Prompt 增强 + 评估 |
| `server.py` | LangChain Serve / Dify | HTTP API（/ingest /query /search /stats） |
| `demo.py` | — | 端到端演示 |

## 端到端演示

```bash
python3 projects/tinyrag/demo.py
```

## HTTP API

```bash
python3 projects/tinyrag/server.py
# curl -X POST http://localhost:8001/ingest -d '{"doc_id":"test","text":"hello world"}'
# curl -X POST http://localhost:8001/query -d '{"query":"what is hello"}'
```

## csdiy 知识交叉

- [bloom-filter](../../source-reading/bloom-filter-精读.md) — 检索前的候选过滤
- [consistent-hashing](../../source-reading/consistent-hashing-精读.md) — 向量库分片
- [redis-data-structures](../../source-reading/redis-data-structures-精读.md) — 倒排索引基础
