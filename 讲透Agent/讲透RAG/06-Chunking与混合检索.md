# 06 — Chunking 与混合检索

> 「讲透 RAG」第七篇。05 讲了 embedding 选型。本篇讲**怎么切块（chunk）+ 怎么混合检索**——这是 RAG 工程的"手感"所在，决定检索质量。

---

## 1. 灵魂：切不好 = 检索不到

$$
\boxed{\text{chunk 质量} > \text{embedding 模型} > \text{rerank 模型}}
$$

再好的 embedding，如果把"一个完整论证"切成两半，检索时两半都不完整 → 答案残缺。

---

## 2. Chunking 策略

### 2.1 固定长度（最简）

按 token 数切（如 512 token），可重叠（overlap=50）。

- ✅ 简单
- ❌ 切断句子/段落

### 2.2 语义切分（推荐）

按自然边界切：段落/标题/句号。用 `langchain.TextSplitter` 或 `unstructured`。

### 2.3 递归切分（折中）

先按大结构（章节）切，太大再按段落，再按句子——**保证不切断语义单元**。

### 2.4 结构感知

Markdown/HTML 有结构（标题层级），按 heading 切最自然：
```
# 第一章 → 一个 chunk
## 1.1 节 → 如果太长，单独 chunk
```

### 2.5 chunk 大小的权衡

| 大小 | 优点 | 缺点 |
|---|---|---|
| 太小（128）| 检索精准 | 上下文不足 |
| 中等（512）| ★ 平衡 | — |
| 太大（2048）| 上下文全 | 检索稀释 + token 贵 |

**经验**：512-1024 token + 10% overlap 是多数场景的甜点。

---

## 3. 混合检索（BM25 + 向量）

### 3.1 为什么混合

- **向量检索**：懂语义（"苹果手机" ≈ "iPhone"），但关键词模糊
- **BM25（关键词）**：精确匹配关键词，但不懂同义词

**混合**：两者互补。

### 3.2 怎么混合

```
1. BM25 检索 top-50
2. 向量检索 top-50
3. 融合（RRF 或加权）
4. rerank 模型重排 top-10
```

**RRF（Reciprocal Rank Fusion）**：

$$
\text{score}(d) = \sum_{\text{检索器}} \frac{1}{k + \text{rank}(d)}
$$

$k$ 通常取 60。RRF 不需要分数归一化，简单有效。

### 3.3 Rerank（重排）

检索召回的 top-50 里，很多其实不相关。用 **cross-encoder**（如 BGE-reranker）对每个 (query, doc) 对打分，重排出 top-5。

- **Bi-encoder（embedding）**：query 和 doc 分别编码 → 快但粗
- **Cross-encoder（rerank）**：query 和 doc 拼接输入 → 慢但准

**典型配置**：bi-encoder 召回 50 → cross-encoder 重排出 5 → 塞进 LLM。

---

## 4. 工程坑

- **chunk 不要带噪声**：页眉/页脚/水印要清洗
- **元数据要保留**：来源/标题/日期存进 metadata，检索时可过滤
- **增量更新**：文档变了别全量重算（用文档 ID 映射）
- **评测！**：建 100 个 query 的标注集，对比不同 chunk 策略的 Recall@5

---

## 📌 下一步

[07-生产坑与多模态 RAG](07-生产坑与多模态.md)——把 RAG 推上生产的踩坑经验 + 图文表混排的多模态 RAG。

## ✍️ 练习

1. 同一文档，用 128/512/2048 三种 chunk 试，检索同一 query，看哪个 Recall 高。
2. BM25+向量混合时，如果一个文档在 BM25 排第 1、向量排第 100，RRF 分数大概是多少？它会被保留吗？
