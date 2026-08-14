# RAG 工程手册

> **建立**：2026-08-13
> **是什么**：RAG = Retrieval-Augmented Generation，检索增强生成。先检索再生成，让 LLM 锚定真实知识。
> **为什么重要**：LLM 知识截止训练时，幻觉是头号问题。RAG 是企业 LLM 应用层最热方向（2023+ 必备）。

---

## 1. 是什么 + 为什么

**RAG 的本质**：不把知识塞进模型权重，**放到外部知识库**。每次回答前先检索相关文档，把文档塞进 prompt，再生成答案。

**vs Fine-tuning**：
- 微调学**风格 / 行为**
- RAG 学**知识 / 事实**
- 不要用微调学知识（这是反模式，见反模式 #1）

**2026 现状**：Long Context（Gemini 2M / Claude 1M）没杀死 RAG——RAG 仍是企业必需（成本可控 + 可溯源 + 实时更新）。

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析一个 RAG 系统（chunk 策略 / 检索质量 / reranking）|
| **说** | 用 RAG 圈行话（embedding / vector DB / top-K / recall@K / NIAH）|
| **读** | 读 RAG 论文（Lewis 2020 / RAG-Fusion / Self-RAG / GraphRAG）|
| **写** | 搭建一个生产级 RAG 系统 |

---

## 3. CRRMO 解析框架

任何 RAG 系统可拆为 5 要素：

```
C - Chunking（切片）：文档怎么切
R - Retrieval（检索）：怎么找相关 chunk
R - Reranking（重排）：怎么精排 top-K
M - Merging（合并）：怎么把 chunk 塞进 prompt
O - Output（输出）：怎么让 LLM 基于文档生成
```

### C · Chunking（切片）
| 策略 | 何时用 |
|------|--------|
| 固定大小（如 512 token）| 简单文档 |
| 按段落 / 标题 | Markdown / HTML |
| 语义切片（SemanticChunker）| 长文档 |
| 递归切片（RecursiveCharacterSplitter）| 通用 |
| Parent-Document（小块检索 + 大块返回）| 精度 + 上下文 |

**关键参数**：chunk_size（200-1000 token）+ overlap（10-20%）

### R · Retrieval（检索）
| 方法 | 何时用 |
|------|--------|
| 向量检索（dense）| 语义相似 |
| BM25（sparse）| 关键词精确 |
| Hybrid（dense + sparse）| 生产推荐 |
| Multi-query（生成多个 query）| 复杂问题 |
| HyDE（生成假设答案再检索）| 长尾问题 |

### R · Reranking（重排）
- 检索 top-50 → reranker 精排 top-5
- 工具：**Cohere Rerank** / **BGE-Reranker** / **Voyage Rerank**
- 改进检索质量 10-30%

### M · Merging（合并）
- 简单拼接
- Lost-in-the-middle 优化（重要在前）
- 结构化（XML tag 包裹）

### O · Output
- "基于以下文档回答..."
- 引用 source（可溯源）
- "如果文档没有，说不知道"（降幻觉）

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 准确性** | 答案正确率（黄金集对比）|
| **2. 稳健性** | 同样问题多次跑方差 |
| **3. 可迁移性** | 跨语言 / 跨领域 |
| **4. 效率** | 检索延迟 + token 消耗 |
| **5. 可控性** | 引用准确 / 可溯源 |
| **6. 安全性** | 检索到敏感文档 / prompt injection |

### 评估工具
- **RAGAS**：4 维度（faithfulness / answer relevancy / context precision / context recall）
- **TruLens**：RAG 三件件（context relevance / groundedness / answer relevance）
- **DeepEval**：单元测试框架

---

## 5. 工具栈（2026-08）

### 框架
| 工具 | 特点 |
|------|------|
| **LangChain** | 全栈，最流行 |
| **LlamaIndex** | RAG 专门优化 |
| **Haystack** | 企业级 |
| **DSPy** | RAG + 自动优化 |

### Embedding 模型
| 模型 | 特点 |
|------|------|
| **OpenAI text-embedding-3-large** | 3072 维，商业最强 |
| **Voyage AI** | 质量 SOTA |
| **BGE-M3**（智源）| 开源，多语言 |
| **Cohere Embed v3** | 商业 |

### 向量数据库
| 工具 | 类型 | 特点 |
|------|------|------|
| **Pinecone** | 云 | 商业首选 |
| **Weaviate** | 开源 | GraphQL |
| **Milvus** | 开源 | 大规模 |
| **Chroma** | 轻量 | 入门 |
| **Qdrant** | 开源 | Rust 高性能 |
| **pgvector** | PostgreSQL 扩展 | 已有 PG 用 |

### Reranker
- **Cohere Rerank** / **BGE-Reranker** / **Voyage Rerank**

---

## 6. 跨平台差异

| 维度 | 开源（LlamaIndex + Chroma）| 商业（Pinecone + OpenAI）|
|------|---|---|
| 成本 | 免费（自托管）| 按量付费 |
| 维护 | 自己 | 平台 |
| 精度 | 中-高 | 高 |
| 中文 | BGE-M3 好 | OpenAI 一般 |
| 隐私 | 完全私有 | 数据上传 |

---

## 7. 实战案例

### 案例：企业文档问答 RAG

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# Step 1: 加载文档
documents = SimpleDirectoryReader("./docs").load_data()

# Step 2: 切片 + Embedding
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")

# Step 3: 索引
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
    chunk_size=512,
    chunk_overlap=50,
)

# Step 4: 查询
query_engine = index.as_query_engine(
    similarity_top_k=10,  # 检索 top-10
    # reranker 可加
)
response = query_engine.query("公司的报销流程是什么？")
print(response)
print(response.source_nodes)  # 可溯源
```

### 高级：Hybrid 检索 + Reranking

```python
from llama_index.core.retrievers import QueryFusionRetriever

# dense + sparse 混合
dense_retriever = index.as_retriever(similarity_top_k=50)
sparse_retriever = bm25_retriever  # BM25

hybrid = QueryFusionRetriever(
    [dense_retriever, sparse_retriever],
    similarity_top_k=5,  # 最终 top-5
    num_queries=3,  # 多 query
)
```

---

## 8. 反模式 10 条

1. **微调学知识**（应该用 RAG）
2. **chunk 太大**（2000+ token → 检索精度差）
3. **chunk 太小**（100- token → 丢上下文）
4. **无 overlap**（chunk 边界丢信息）
5. **只用 dense 检索**（关键词精确场景用 Hybrid）
6. **无 reranking**（top-50 直接塞 → 噪声多）
7. **不评估**（没跑 RAGAS 就上线）
8. **Lost in middle**（重要 chunk 放中段）
9. **无引用**（不能溯源 → 用户不信）
10. **跨语言直接复制**（中文文档用英文 embedding → 效果差）

---

## 9. 下一步

- 读 Lewis et al. 2020 "RAG" 原论文
- 读 Gao et al. 2024 "RAG Survey"（arXiv 2401.15872）
- 用 LlamaIndex 搭最简 RAG
- 用 RAGAS 评估
- 加 BGE-Reranker 看精度提升

---

**版本**：v1.0（2026-08-13）
**核心理念**：**RAG = 检索 + 生成 + 溯源。让 LLM 锚定真实世界。**
