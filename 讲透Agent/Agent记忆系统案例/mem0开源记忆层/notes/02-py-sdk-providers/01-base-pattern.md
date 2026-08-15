# 01 — Provider 抽象的统一设计模式（5 类 base.py 对比）

> Mem0 的"可插拔"靠 **5 类 base.py 抽象基类**。每类有相同的设计模式,但抽象的方法数差异巨大（reranker 1 个 vs vector store 12 个）。
> 本篇对比 5 类抽象的统一模式与差异,看完你能写自己的 provider。

---

## 1. 5 类 Provider 全清单

| 类别 | base 文件 | 抽象方法数 | 实例数 | 典型用途 |
|------|---------|---------|-------|---------|
| **LLM** | `mem0/llms/base.py` `LLMBase` | 1（+ 大量 helper） | 21 | 文本生成（extraction / summarization） |
| **Embedding** | `mem0/embeddings/base.py` `EmbeddingBase` | 1 | 15 | 向量化文本 |
| **Vector Store** | `mem0/vector_stores/base.py` `VectorStoreBase` | 12 | 28 | 存向量 + 检索 |
| **Reranker** | `mem0/reranker/base.py` `BaseReranker` | 1 | 5 | 重排检索结果 |
| ~~Graph~~ | ~~`mem0/graphs/`~~ | — | — | **已移除**（April 2026 重构） |

> Graph memory 在 v1.1+ 已被移除。Mem0 改用基于 vector store 的 **`entity_store`**（详见 [`05-graphs.md`](./05-graphs.md)）。

---

## 2. 统一设计模式

```python
# 所有 base 的骨架
class XBase(ABC):
    def __init__(self, config=None):
        # 1. 接 config（Pydantic model）
        if config is None:
            self.config = DefaultConfig()
        elif isinstance(config, dict):
            self.config = DefaultConfig(**config)   # 向后兼容
        else:
            self.config = config

    @abstractmethod
    def core_method(self, ...):
        """子类必须实现的核心方法"""
        pass

    def optional_helper(self, ...):
        """非抽象 helper,子类可 override 但有默认实现"""
        # 默认 fallback 逻辑
        ...
```

### 关键设计原则

| 原则 | 体现 |
|------|------|
| **ABC 强制契约** | 不实现 abstract method 无法实例化 |
| **非抽象方法给 fallback** | 子类不实现也能跑（性能差或功能受限） |
| **统一 config** | 接 `BaseXConfig` Pydantic 模型,工厂能从 dict 构造 |
| **Pydantic v2 全栈** | config / data model 一致 |
| **错误统一** | 抛 `mem0.exceptions` 里的具体异常（如 `LLMError`/`VectorStoreError`） |

---

## 3. ⭐ `LLMBase` 详解（最丰富的 helper）

`mem0/llms/base.py`：

```python
class LLMBase(ABC):
    def __init__(self, config=None):
        if config is None:
            self.config = BaseLlmConfig()
        elif isinstance(config, dict):
            self.config = BaseLlmConfig(**config)
        else:
            self.config = config
        self._validate_config()

    def _validate_config(self):
        """子类可 override 加 provider 特定验证"""
        if not hasattr(self.config, "model"):
            raise ValueError("Configuration must have a 'model' attribute")

    @abstractmethod
    def generate_response(self, messages, tools=None, tool_choice="auto", **kwargs):
        """核心:生成响应"""

    def _is_reasoning_model(self, model: str) -> bool:
        """⭐ 自动检测 reasoning model（o1/o3/gpt-5）"""
        # 1. config.is_reasoning_model 显式优先
        explicit = getattr(self.config, "is_reasoning_model", None)
        if explicit is not None:
            return explicit
        # 2. fallback 到名字启发式
        reasoning_models = {"o1", "o1-preview", "o3-mini", "o3", "gpt-5", "gpt-5o", ...}
        base_model = model.lower().rsplit("/", 1)[-1]
        if base_model in reasoning_models:
            return True
        if any(base_model.startswith(prefix) for prefix in ["o1-", "o1.", "o3-", "o3."]):
            return True
        return False

    def _uses_max_completion_tokens(self, model: str) -> bool:
        """⭐ GPT-5 family 用 max_completion_tokens 而非 max_tokens"""
        base_model = (model or "").lower().rsplit("/", 1)[-1]
        return base_model.startswith("gpt-5")

    def _get_supported_params(self, **kwargs) -> Dict:
        """⭐ reasoning model 自动过滤不支持参数"""
        model = getattr(self.config, 'model', '')
        if self._is_reasoning_model(model):
            supported_params = {}
            # 只保留 messages/response_format/tools/tool_choice/reasoning_effort
            for k in ["messages", "response_format", "tools", "tool_choice"]:
                if k in kwargs:
                    supported_params[k] = kwargs[k]
            reasoning_effort = getattr(self.config, 'reasoning_effort', None)
            if reasoning_effort:
                supported_params["reasoning_effort"] = reasoning_effort
            return supported_params
        else:
            return self._get_common_params(**kwargs)

    def _get_common_params(self, **kwargs) -> Dict:
        """普通 model 的标准参数"""
        params = {"temperature": self.config.temperature, "top_p": self.config.top_p}
        model = getattr(self.config, "model", "")
        if self._uses_max_completion_tokens(model):
            params["max_completion_tokens"] = self.config.max_tokens
        else:
            params["max_tokens"] = self.config.max_tokens
        params.update(kwargs)
        return params
```

### LLMBase 的智慧

| 特性 | 解决什么问题 |
|------|------------|
| `_is_reasoning_model` 启发式 | OpenAI o1/o3 不支持 `temperature`/`top_p`/`max_tokens`,自动过滤 |
| `_uses_max_completion_tokens` | GPT-5 拒绝 `max_tokens`,要 `max_completion_tokens` |
| `_get_supported_params` | 子类不用每个都写 "if reasoning: drop X" 逻辑 |
| `config.is_reasoning_model` 显式优先 | Azure 用奇怪名字（`gpt-5.4-nano-2026-03-17`）时,允许手动指定 |

> 这是 OpenAI API 不停变种的**适配层**——子类（如 `OpenAILLM`）只需关注 provider 特定调用,通用 logic 在 base。

### 子类要做什么

```python
class OpenAILLM(LLMBase):
    def __init__(self, config=None):
        super().__init__(config)
        self.client = openai.OpenAI(api_key=self.config.api_key)

    def generate_response(self, messages, tools=None, tool_choice="auto", **kwargs):
        params = self._get_supported_params(messages=messages, **kwargs)
        # 加 OpenAI 特定字段
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        response = self.client.chat.completions.create(
            model=self.config.model, **params
        )
        return response.choices[0].message.content
```

---

## 4. ⭐ `EmbeddingBase`（最简的抽象）

`mem0/embeddings/base.py`：

```python
class EmbeddingBase(ABC):
    def __init__(self, config=None):
        if config is None:
            self.config = BaseEmbedderConfig()
        else:
            self.config = config

    @abstractmethod
    def embed(self, text, memory_action: Optional[Literal["add", "search", "update"]]):
        """核心:嵌入单条文本"""

    def embed_batch(self, texts, memory_action="add"):
        """⭐ 非抽象,默认循环调 embed"""
        return [self.embed(text, memory_action) for text in texts]
```

### `embed_batch` 的设计

- **默认实现**：循环调 `embed()`（O(N) 次 API 调用）
- **子类可 override**：OpenAI / Cohere 等有原生 batch API 的 provider 可一次调用嵌入多条
- **子类不 override 也能跑**,只是慢

### `memory_action` 参数

3 个值：`"add"` / `"search"` / `"update"`。某些 embedding 模型（如 Voyage AI）对 add/search 用不同 model 或不同 prefix。多数 provider 忽略这个参数。

### 子类示例（OpenAIEmbedding）

```python
class OpenAIEmbedding(EmbeddingBase):
    def __init__(self, config=None):
        super().__init__(config)
        self.client = openai.OpenAI(api_key=self.config.api_key)

    def embed(self, text, memory_action=None):
        response = self.client.embeddings.create(
            input=text, model=self.config.model
        )
        return response.data[0].embedding

    def embed_batch(self, texts, memory_action=None):
        # ⭐ override 用原生 batch API
        response = self.client.embeddings.create(
            input=texts, model=self.config.model
        )
        return [d.embedding for d in response.data]
```

---

## 5. ⭐ `VectorStoreBase`（抽象方法最多）

`mem0/vector_stores/base.py`：12 个 abstract + 2 个 optional。

### 必须实现的 12 个

```python
class VectorStoreBase(ABC):
    @abstractmethod
    def create_col(self, name, vector_size, distance): ...

    @abstractmethod
    def insert(self, vectors, payloads=None, ids=None): ...

    @abstractmethod
    def search(self, query, vectors, top_k=5, filters=None): ...

    @abstractmethod
    def delete(self, vector_id): ...

    @abstractmethod
    def update(self, vector_id, vector=None, payload=None): ...

    @abstractmethod
    def get(self, vector_id): ...

    @abstractmethod
    def list_cols(self): ...

    @abstractmethod
    def delete_col(self): ...

    @abstractmethod
    def col_info(self): ...

    @abstractmethod
    def list(self, filters=None, top_k=None): ...

    @abstractmethod
    def reset(self): ...
```

### ⭐ 可选的 2 个（默认 fallback）

```python
def keyword_search(self, query: str, top_k: int = 5, filters: dict = None):
    """BM25 关键词搜索。默认返回 None（不支持）。
    
    子类 override 启用 hybrid search。
    """
    return None

def search_batch(self, queries: list, vectors_list: list, top_k: int = 1, filters: dict = None):
    """批量 search。默认循环调 search()。"""
    return [self.search(q, v, top_k=top_k, filters=filters) for q, v in zip(queries, vectors_list)]
```

### ⭐ 重要约定：`search()` 返回 score 必须 ∈ [0, 1]

> "All implementations must return similarity scores where higher values indicate greater similarity (range [0, 1] preferred). Implementations using distance metrics must convert to similarity before returning:
> - Cosine distance: `score = max(0.0, 1.0 - distance)`
> - L2 distance: `score = 1.0 / (1.0 + distance)`
> - Inner product: `score = value` (already higher = better)"

这是个**关键工程决策**——所有 provider 的 search 必须统一返回"越大越相似",让上层 fusion（`score_and_rank`）能直接相加。如果某个 provider 返回 distance（越小越相似）,必须在 provider 内部转换。

### 子类示例（Qdrant）

```python
class Qdrant(VectorStoreBase):
    def __init__(self, host=None, port=None, path=None, url=None, api_key=None,
                 collection_name="mem0", embedding_model_dims=1536, ...):
        # qdrant-client 初始化
        ...

    def create_col(self, name, vector_size, distance): ...
    def insert(self, vectors, payloads=None, ids=None): ...
    def search(self, query, vectors, top_k=5, filters=None):
        # qdrant 调用 + 把 distance 转 similarity
        ...
    def keyword_search(self, query, top_k=5, filters=None):
        # ⭐ Qdrant 支持 BM25,override 这个
        ...
```

---

## 6. ⭐ `BaseReranker`（最简）

```python
class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = None) -> List[Dict[str, Any]]:
        """重排 documents,返回带 'rerank_score' 字段的结果"""
        pass
```

只一个方法。子类实现：

```python
class CohereReranker(BaseReranker):
    def __init__(self, config):
        self.client = cohere.Client(api_key=config.api_key)

    def rerank(self, query, documents, top_k=None):
        docs = [d["memory"] for d in documents]
        result = self.client.rerank(
            model=self.config.model, query=query, documents=docs, top_n=top_k
        )
        return [
            {**documents[i.index], "rerank_score": i.relevance_score}
            for i in result.results
        ]
```

---

## 7. 5 类 base 的契约对比表

| 维度 | LLM | Embedding | VectorStore | Reranker |
|------|-----|-----------|-------------|---------|
| 核心方法 | `generate_response` | `embed` | 12 个 CRUD | `rerank` |
| Optional 方法 | — | `embed_batch`（默认循环） | `keyword_search`（默认 None）<br>`search_batch`（默认循环） | — |
| `__init__` | 接 config | 接 config | 接 **kwargs（**每个 provider 自定义**） | 接 config |
| Helper 数量 | 多（reasoning 检测等） | 0 | 0 | 0 |
| 子类代码量 | 中 | 小 | 大（最多） | 小 |

### VectorStore 的特殊处

注意 `VectorStoreBase.__init__` **不接 config** —— 各 provider 的 `__init__` 自定义 kwargs：

```python
class Qdrant(VectorStoreBase):
    def __init__(self, host=None, port=None, path=None, url=None, ...): ...

class PineconeDB(VectorStoreBase):
    def __init__(self, api_key=None, index_name=None, ...): ...
```

> 因为各 vector store 的连接参数差异巨大（Qdrant 用 host/port,Pinecone 用 api_key/region）。`VectorStoreFactory.create()` 用 `**config` 把 dict 透传给 `__init__`（详见 [`07-factory.md`](./07-factory.md)）。

---

## 8. 提供一致性的关键

### 数据结构约定

各 base 强制子类返回**一致的数据结构**:

| 方法 | 返回结构 |
|------|---------|
| `LLMBase.generate_response` | `str`（或 dict 含 tool_calls） |
| `EmbeddingBase.embed` | `List[float]`（向量） |
| `VectorStoreBase.search` | `List[OutputData]`（自定义类,id + score + payload） |
| `VectorStoreBase.get` | `OutputData` |
| `VectorStoreBase.list` | `List[OutputData]` |
| `BaseReranker.rerank` | `List[Dict]`（input documents 加 `rerank_score`） |

> `OutputData` 是各 vector store 内部的统一返回类（id/score/payload）。

### 错误类型约定

各 provider 抛对应的 mem0 异常（在 `mem0/exceptions.py`）：

- `LLMError` — LLM 调用失败
- `EmbeddingError` — embedding 失败
- `VectorStoreError` — vector store 失败
- `RerankerError` — reranker 失败

这样上层 try/except 能区分错误来源。

---

## 9. 添加新 Provider 的步骤

`AGENTS.md` 写的标准流程：

1. **创建主文件** `mem0/<category>/<provider_name>.py`
   - 继承对应的 `base.py`
   - 实现所有 abstract method
   - 用 `provider_to_class` 注册的类名

2. **配置类**（如果需要 provider 特定 config）
   - `mem0/configs/<category>/<provider_name>.py` 写 `<Provider>Config(BaseXConfig)`
   - 加 provider 特定字段

3. **注册到 factory**
   - `mem0/utils/factory.py` 的 `provider_to_class` dict 加一行
   - LLM: `("mem0.llms.<provider>.<Class>", <Config>)`
   - 其他: `"mem0.<category>.<provider>.<Class>"`

4. **加可选依赖**
   - `pyproject.toml` 的对应 optional group（`vector-stores` / `llms` / `extras`）加包
   - **绝不**加到 core `dependencies`

5. **测试**
   - `tests/<category>/<provider>/` 加测试

6. **文档**
   - `docs/integrations/<provider>.mdx` + 加 `docs/llms.txt`

详见 [`07-factory.md`](./07-factory.md)。

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| 4 个 Factory 类详解 | [`07-factory.md`](./07-factory.md) |
| 21 个 LLM provider 枚举 | [`02-llms.md`](./02-llms.md) |
| 28 个 Vector Store 对比 | [`04-vector-stores.md`](./04-vector-stores.md) |
| entity_store 替代 graph memory | [`05-graphs.md`](./05-graphs.md) |
| 8 个 utils（NER + BM25 + scoring） | [`08-utils.md`](./08-utils.md) |

---

📌 **下一步** → [`07-factory.md`](./07-factory.md) Factory 工厂模式。
