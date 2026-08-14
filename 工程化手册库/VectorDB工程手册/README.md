# Vector DB 工程手册

> **是什么**：专门存/检索向量的数据库。RAG 的存储层。
> **为什么重要**：Embedding 生成后要存 + 快速检索 → Vector DB 是必需品。

---

## 1. 是什么

**Vector DB** = 存海量向量 + 快速近似最近邻（ANN）搜索。

```
存：embedding → [(id, vector, metadata)]
查：query_vector → top-K nearest → [id1, id2, ...]
```

**核心指标**：
- **QPS**（Queries Per Second）
- **延迟**（p50 / p99）
- **召回率**（vs 暴力搜索）
- **数据量**（百万-十亿级向量）

## 2. 主流产品对比（2026-08）

| 产品 | 类型 | 特点 | 适用 | 规模 |
|------|------|------|------|------|
| **Pinecone** | 云 SaaS | 商业首选，易用 | 生产（不差钱）| 十亿级 |
| **Milvus** | 开源 | 大规模，CNCF | 自托管 | 十亿级 |
| **Qdrant** | 开源 | Rust 高性能 | 自托管 | 亿级 |
| **Weaviate** | 开源 | GraphQL + 混合检索 | 自托管 | 亿级 |
| **Chroma** | 开源 | 轻量易用 | 原型 | 百万级 |
| **pgvector** | PG 扩展 | 已有 PG | 小规模 | 百万级 |
| **Elasticsearch** | 搜索引擎 | + 全文搜索 | 混合检索 | 亿级 |

## 3. ANN 算法

| 算法 | 原理 | 精度 | 速度 |
|------|------|------|------|
| **HNSW** | 分层导航小世界图 | 高 | 极快 |
| **IVF** | 倒排文件 + 聚类 | 中 | 快 |
| **PQ**（Product Quantization）| 向量压缩 | 低 | 快 |
| **IVF + PQ** | 组合 | 中 | 极快 |
| **暴力搜索** | 精确 | 100% | 慢 |

**推荐**：**HNSW**（精度-速度平衡好，大多数 Vector DB 默认）

## 4. 多视角深层

### 📐 数学
- ANN = 近似最近邻搜索
- 在 R^d 空间找 top-K 最近点
- **维度灾难**：d > 1000 时，所有点距离趋同 → 需要降维或特殊算法

### 🌐 图论
- HNSW = 分层小世界图
- 类似社交网络：近邻连边 + 跨层快捷连接
- 搜索 = 从顶层（粗）到底层（精）

### 💰 经济学
- 云 Vector DB：$0.1/1M queries
- 自托管：GPU/CPU 成本 + 运维
- **选择**：小规模用云，大规模自托管

## 5. 实战：Chroma（最简）

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("docs")

# 存
collection.add(
    documents=["text1", "text2"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    metadatas=[{"source": "file1"}, {"source": "file2"}],
    ids=["1", "2"]
)

# 查
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=5
)
```

## 6. 选型决策树

```
你的需求？
├─ 原型 / 小规模（<100万）→ Chroma / pgvector
├─ 生产 + 不想运维 → Pinecone
├─ 生产 + 自托管 + 中规模 → Qdrant / Weaviate
├─ 超大规模（十亿+）→ Milvus
└─ 已有 Elasticsearch → ES + dense_vector
```

## 7. 反模式 10 条

1. **暴力搜索**（没有 ANN → 大规模慢死）
2. **不建索引**（HNSW 参数没调）
3. **维度不匹配**（embedding 1024 维，库配置 768）
4. **不更新**（数据变了不重新 embed）
5. **无 metadata 过滤**（全扫 → 慢）
6. **单机存太多**（OOM → 分布式）
7. **不监控召回率**（ANN 可能漏）
8. **混合检索权重不对**（dense + sparse 混合）
9. **忽略一致性**（多副本数据不一致）
10. **不做 benchmark**（不同库性能差 10x）

---

**核心理念**：**Vector DB 是 RAG 的地基。选对 = 省 10 倍运维。**
