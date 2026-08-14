# 06 — Rerankers（5 个）

> Reranker 是**可选的二次重排**——在 multi-signal fusion 之后,用更强的模型重排 top-N。
> 5 个 reranker 都继承 `BaseReranker`,实现 `rerank(query, documents, top_k)`。

---

## 1. Provider 全清单

| Provider | 类 | 实现 | 用途 |
|---------|---|------|------|
| `cohere` | `CohereReranker` | Cohere rerank API | 商业 rerank,高质量 |
| `huggingface` | `HuggingFaceReranker` | 本地 cross-encoder | 免费,要 GPU |
| `sentence_transformer` | `SentenceTransformerReranker` | sentence-transformers | 同上 |
| `llm_reranker` | `LLMReranker` | ⭐ 用 LLM 给每条打分 | 复用已有 LLM,无新依赖 |
| `zero_entropy` | `ZeroEntropyReranker` | ZeroEntropy API | 商业 |

---

## 2. `BaseReranker` 抽象

```python
# mem0/reranker/base.py（完整）
class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = None) -> List[Dict[str, Any]]:
        """Rerank documents based on relevance to the query.

        Args:
            query: The search query
            documents: List of documents to rerank, each with 'memory' field
            top_k: Number of top documents to return (None = return all)

        Returns:
            List of reranked documents with added 'rerank_score' field
        """
        pass
```

只一个方法。子类实现。

---

## 3. ⭐ `CohereReranker`（最经典）

```python
class CohereReranker(BaseReranker):
    def __init__(self, config):
        if not COHERE_AVAILABLE:
            raise ImportError("cohere package is required. Install with: pip install cohere")

        self.config = config
        self.api_key = config.api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("Cohere API key is required.")
        self.model = config.model
        self.client = cohere.Client(self.api_key)

    def rerank(self, query, documents, top_k=None):
        if not documents:
            return documents

        # 提取文本（支持 memory/text/content 三个 key）
        doc_texts = []
        for doc in documents:
            if 'memory' in doc:
                doc_texts.append(doc['memory'])
            elif 'text' in doc:
                doc_texts.append(doc['text'])
            elif 'content' in doc:
                doc_texts.append(doc['content'])
            else:
                doc_texts.append(str(doc))

        try:
            response = self.client.rerank(
                model=self.model,
                query=query,
                documents=doc_texts,
                top_n=top_k or self.config.top_k or len(documents),
                return_documents=self.config.return_documents,
                max_chunks_per_doc=self.config.max_chunks_per_doc,
            )

            reranked_docs = []
            for result in response.results:
                original_doc = documents[result.index].copy()
                original_doc['rerank_score'] = result.relevance_score
                reranked_docs.append(original_doc)
            return reranked_docs

        except Exception as e:
            # ⭐ fallback 到原顺序
            logger.warning("Cohere reranking failed, falling back to original order: %s", e)
            fallback_docs = []
            for doc in documents:
                fallback_doc = doc.copy()
                fallback_doc['rerank_score'] = 0.0
                fallback_docs.append(fallback_doc)
            final_top_k = top_k or self.config.top_k
            return fallback_docs[:final_top_k] if final_top_k else fallback_docs
```

### Cohere 特色

- **API 调用**：`cohere.Client(api_key).rerank(...)`
- **`max_chunks_per_doc`**：长 doc 切 chunk
- **失败 fallback**：保留原顺序（避免 rerank 失败导致 search 失败）

---

## 4. ⭐ `LLMReranker`（用 LLM 重排,最灵活）

```python
class LLMReranker(BaseReranker):
    _SYSTEM_PROMPT = (
        "You are a relevance scoring assistant. "
        "Given a query and a document, score how relevant the document is to the query.\n\n"
        "Score the relevance on a scale from 0.0 to 1.0, where:\n"
        "- 1.0 = Perfectly relevant and directly answers the query\n"
        "- 0.8-0.9 = Highly relevant with good information\n"
        "- 0.6-0.7 = Moderately relevant with some useful information\n"
        "- 0.4-0.5 = Slightly relevant with limited useful information\n"
        "- 0.0-0.3 = Not relevant or no useful information\n\n"
        "Respond with only a single numerical score between 0.0 and 1.0. "
        "Do not include any explanation or additional text."
    )

    _MAX_INPUT_LEN = 4000   # 防 prompt flooding

    def __init__(self, config):
        # ...
        # ⭐ 复用 LlmFactory 创建底层 LLM
        self.llm = LlmFactory.create(llm_provider, llm_config)

    def rerank(self, query, documents, top_k=None):
        scored = []
        for doc in documents:
            score = self._score_one(query, doc)
            scored.append({**doc, "rerank_score": score})
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored[:top_k] if top_k else scored

    def _score_one(self, query, doc):
        """调 LLM 给单个 query-doc 对打分"""
        # truncate to _MAX_INPUT_LEN
        # ...
        prompt = f"Query: {query}\nDocument: {doc_text}\n\nScore:"
        response = self.llm.generate_response(messages=[
            {"role": "system", "content": self._SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        return self._extract_score(response)

    def _extract_score(self, response_text):
        """从 LLM 响应抽数字"""
        matches = re.findall(r'-?\d+\.\d+', response_text) or re.findall(r'-?\d+', response_text)
        if matches:
            score = float(matches[-1])   # 取最后一个数字
            return max(0.0, min(1.0, score))
        return 0.0
```

### LLMReranker 特色

- **零额外依赖**：复用已有 LLM（OpenAI / Anthropic / Ollama 都行）
- **per-doc 调用**：N 个 doc → N 次 LLM 调用（贵！）
- **truncate**：长 doc 截到 4000 字符（防 prompt flooding）
- **正则抽分**：从 LLM 响应抽最后一个数字

> ⚠️ 性能警告：N=20 个 doc → 20 次 LLM 调用,每次 ~500ms → 总 10 秒。仅用于精排少量 top candidates。

---

## 5. 5 个 Reranker 对比

| Reranker | 调用方式 | 1 doc 耗时 | N=20 总耗时 | 质量 |
|---------|---------|----------|-----------|------|
| Cohere | 1 次 batch API | — | ~500ms | ⭐⭐⭐⭐⭐ |
| HuggingFace | 本地 batch | — | ~200ms（GPU） | ⭐⭐⭐⭐ |
| SentenceTransformer | 本地 batch | — | ~200ms（GPU） | ⭐⭐⭐⭐ |
| LLMReranker | N 次串行 LLM 调用 | ~500ms | **~10 秒** | ⭐⭐⭐ |
| ZeroEntropy | 1 次 API | — | ~500ms | ⭐⭐⭐⭐ |

---

## 6. 配置示例

### Cohere

```python
from mem0.configs.rerankers.cohere import CohereRerankerConfig

config = MemoryConfig(
    reranker=CohereRerankerConfig(
        model="rerank-multilingual-v3.0",
        api_key="...",
    ),
)

m = Memory(config=config)
results = m.search("hello", filters={"user_id":"u1"}, rerank=True)   # ⚠️ 必须 rerank=True
```

### HuggingFace 本地

```python
from mem0.configs.rerankers.huggingface import HuggingFaceRerankerConfig

config = MemoryConfig(
    reranker=HuggingFaceRerankerConfig(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    ),
)
```

### LLMReranker（复用 OpenAI）

```python
from mem0.configs.rerankers.llm import LLMRerankerConfig

config = MemoryConfig(
    reranker=LLMRerankerConfig(
        provider="openai",
        model="gpt-4o-mini",
        api_key="...",
        temperature=0.0,
        max_tokens=10,
    ),
)
```

---

## 7. 关键点：reranker 默认不启用

```python
# Memory.search()
results = m.search("hello", filters={"user_id":"u1"})
# 不传 rerank=True,reranker 不调用

results = m.search("hello", filters={"user_id":"u1"}, rerank=True)
# 显式 rerank=True + MemoryConfig 配了 reranker,才调用
```

且看 `search()` 主流程：

```python
# mem0/memory/main.py L1494-L1500
if rerank and self.reranker and original_memories:
    try:
        reranked_memories = self.reranker.rerank(query, original_memories, limit)
        original_memories = reranked_memories
    except Exception as e:
        logger.warning(f"Reranking failed, using original results: {e}")
```

> 3 个条件全满足才 rerank：① `rerank=True` ② `self.reranker` 配了 ③ `original_memories` 非空。失败时 fallback 到原结果。

---

## 8. Reranker vs Fusion 检索

容易混淆：

| 阶段 | 方法 | 用什么 |
|------|------|-------|
| **Multi-signal fusion**（`_search_vector_store`） | 自动 | semantic + BM25 + entity boost（`score_and_rank`） |
| **Rerank**（可选） | 显式 `rerank=True` | Cohere / HF / LLM |

> fusion 是**多个 cheap signal** 融合;rerank 是**一个 expensive model** 精排。两者**叠加**用,效果最好。

---

## 9. 决策：要不要用 reranker

| 场景 | 推荐 |
|------|------|
| 一般应用 | 不用（fusion 够了） |
| 高质量要求（搜索产品） | Cohere |
| 本地 / 隐私 | SentenceTransformer / HuggingFace |
| 已有 LLM,想试 | LLMReranker（小 top_k） |

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| 抽象基类 | [`01-base-pattern.md`](./01-base-pattern.md) §6 |
| search() 主流程 | [`../01-py-sdk-core/07-search-pipeline.md`](../01-py-sdk-core/07-search-pipeline.md) §6 |
| Factory 注册 | [`07-factory.md`](./07-factory.md) §6 |

---

📌 **下一步** → [`08-utils.md`](./08-utils.md) entity 抽取 + BM25 scoring。
