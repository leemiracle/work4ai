# 高级 RAG 精读：从朴素检索到智能检索

> 参照：LlamaIndex Advanced / LangChain Advanced / Self-RAG / Corrective RAG
>
> csdiy 对应：tinyrag + hnsw-algorithm + prompt-engineering + tinyvector

---

## 一、朴素 RAG vs 高级 RAG

```
朴素 RAG:
  查询 → 嵌入 → 检索 top-K → 拼接 → 生成

问题:
  ① 用户查询表述不清 → 检索不准
  ② 检索结果有噪音 → 干扰生成
  ③ 单次检索 → 不够全面
  ④ 无自我纠错 → 可能有幻觉

高级 RAG:
  查询重写 → 多路检索 → 重排序 → 压缩 → 生成 → 纠错
```

---

## 二、查询重写（Query Rewriting）

### 问题

```
用户: "那个东西怎么用？"
→ "那个东西" 指代不明 → 检索质量差
```

### 解法

```
① LLM 重写:
  原始: "那个东西怎么用？"
  重写: "tinyllm 的 KV Cache 怎么用？"

② HyDE (Hypothetical Document Embeddings):
  让 LLM 先生成一个假设的答案 → 用假设答案的嵌入去检索
  → 假设答案比模糊查询更接近目标文档

③ 多查询生成:
  一个查询 → 生成 3 个变体查询 → 分别检索 → 合并结果
```

---

## 三、多路召回（Hybrid Search）

### 向量检索 + 关键词检索

```
向量检索 (Dense):
  语义相似度 → 找"意思接近"的文档
  强项: 同义词/改写/跨语言
  弱项: 精确名称/编号/代码

关键词检索 (Sparse, BM25):
  词频匹配 → 找"包含关键词"的文档
  强项: 精确匹配/专有名词/代码
  弱项: 语义相似

混合检索 = Dense + Sparse → 取两者之长
```

### 实现

```python
# 参照 tinyrag 的 retriever
def hybrid_search(query, k=5):
    dense_results = vector_search(query, k=k*2)      # 向量检索
    sparse_results = bm25_search(query, k=k*2)        # BM25 检索
    merged = merge_and_rerank(dense_results, sparse_results, k=k)
    return merged
```

---

## 四、重排序（Reranking）

### 问题

```
向量检索速度快但精度有限 → top-10 中可能有噪音
→ 用更精确的模型重新排序 top-10
```

### Cross-Encoder Reranking

```
Bi-Encoder（向量检索用的）:
  embed(query) · embed(doc) → 相似度分数
  → 快但粗略（query 和 doc 独立编码）

Cross-Encoder（重排序用的）:
  [CLS] query [SEP] doc [SEP] → Transformer → 分数
  → query 和 doc 交互编码 → 精确但慢

→ 先用 Bi-Encoder 召回 top-100 → 再用 Cross-Encoder 精排 top-5
```

### LLM Reranking

```
让 LLM 判断检索结果的相关性:

Prompt: "Rate the relevance of this document to the query (1-10).
Query: {query}
Document: {doc}
Score: "
```

---

## 五、上下文压缩（Context Compression）

### 问题

```
检索到 10 个文档 × 500 字 = 5000 字 → 占满 context window
→ 大部分内容无关 → 浪费 token + 干扰生成
```

### 解法

```
① LLM 压缩: "提取以下文档中和查询相关的内容"
② 摘要: 把每个文档压缩成 1-2 句
③ 过滤: 去掉和查询无关的段落
```

---

## 六、Self-RAG（自检索 + 自纠错）

### 核心思想

让 LLM 自己决定：
1. 是否需要检索（不是每个问题都需要）
2. 检索结果是否有用
3. 生成是否基于检索内容

```
步骤:
① 判断: "这个问题需要检索吗？"
  → "天空为什么是蓝色的" → 不需要（常识）
  → "2024 年 GDP 数据" → 需要（时效性信息）

② 检索: 如果需要 → 检索 top-K

③ 评估: "检索到的文档有用吗？"
  → 有用 → 使用
  → 无用 → 重写查询 → 重新检索

④ 生成: "回答是否基于检索内容？"
  → 是 → 输出（标注引用来源）
  → 否 → 标注"可能不准确"
```

---

## 七、Corrective RAG (CRAG)

```
检索后自动评估质量 + 纠错:

① 检索 → 评估置信度
② 高置信 → 直接使用
③ 低置信 → 触发网页搜索（补充信息）
④ 重组 → 生成

→ 检索失败时有"Plan B"（不像朴素 RAG 只靠一次检索）
```

---

## 八、Graph RAG（知识图谱增强）

```
传统 RAG: 文档 → 嵌入 → 向量检索
Graph RAG: 文档 → 实体/关系提取 → 知识图谱 → 图查询

优势:
  ① 多跳推理（A 认识 B，B 认识 C → A 认识谁？）
  ② 全局信息（"总结所有文档的主要观点"）
  ③ 可解释性（推理路径可视化）
```

---

## 九、高级 RAG 架构对比

| 方法 | 核心创新 | 适用场景 | 复杂度 |
|------|---------|---------|--------|
| 朴素 RAG | 向量检索 | 简单 QA | ⭐ |
| + 查询重写 | HyDE/多查询 | 查询模糊 | ⭐⭐ |
| + 混合检索 | Dense+Sparse | 专有名词 | ⭐⭐ |
| + 重排序 | Cross-Encoder | 高精度需求 | ⭐⭐⭐ |
| + 压缩 | 摘要/过滤 | 长文档 | ⭐⭐⭐ |
| Self-RAG | 自检索+自评估 | 复杂推理 | ⭐⭐⭐⭐ |
| CRAG | 纠错+网页补充 | 高可靠性 | ⭐⭐⭐⭐ |
| Graph RAG | 知识图谱 | 多跳推理 | ⭐⭐⭐⭐⭐ |

---

## 十、一句话总结

> 高级 RAG = 查询重写 + 混合检索 + 重排序 + 压缩 + 自纠错。
>
> **Self-RAG 让模型自己决定"是否检索"→ 更智能。**
> **CRAG 让检索有"Plan B"→ 更可靠。**
>
> 朴素 RAG 是起点，高级 RAG 是生产级系统。

---

*配套：[tinyrag/pipeline.py](../projects/tinyrag/pipeline.py) | [hnsw-algorithm精读](hnsw-algorithm-精读.md) | [prompt-engineering-deep精读](prompt-engineering-deep-精读.md) | [bloom-filter精读](bloom-filter-精读.md)*
