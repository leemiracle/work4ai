# 07 — Factory 工厂模式（4 个 Factory 类）

> Mem0 的"可插拔"靠 `mem0/utils/factory.py` 的 **4 个 Factory 类**。
> 它们用 `importlib.import_module` **懒加载** + `provider_to_class` dict **注册**,让用户不用的 provider 永远不被 import。

---

## 1. 文件全景（280 行）

```
mem0/utils/factory.py
├── load_class(class_type)              # L29-L32  动态加载 helper
├── class LlmFactory                    # L35-L149  ⭐ 21 providers
│   ├── provider_to_class               # 注册表
│   ├── create(provider_name, config)   # 主入口
│   ├── register_provider(name, ...)    # ⭐ 运行时扩展点
│   └── get_supported_providers()       # 列举
├── class EmbedderFactory               # L152-L177  15 providers
├── class VectorStoreFactory            # L180-L223  28 providers
└── class RerankerFactory               # L226-L280  5 providers
```

---

## 2. ⭐ `load_class(class_type)`（核心 helper）

```python
def load_class(class_type):
    """class_type = "mem0.llms.openai.OpenAILLM" → OpenAILLM 类"""
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
```

> 这就是**懒加载的核心**——只有真的要用 OpenAI 时才会 `import mem0.llms.openai`,而这个 import 又会触发 `import openai`。如果用户只用 Anthropic,openai 包永远不被加载。

---

## 3. ⭐ `LlmFactory`（21 个 provider）

### 3.1 注册表

```python
provider_to_class = {
    "ollama":              ("mem0.llms.ollama.OllamaLLM", OllamaConfig),
    "openai":              ("mem0.llms.openai.OpenAILLM", OpenAIConfig),
    "groq":                ("mem0.llms.groq.GroqLLM", BaseLlmConfig),
    "together":            ("mem0.llms.together.TogetherLLM", BaseLlmConfig),
    "aws_bedrock":         ("mem0.llms.aws_bedrock.AWSBedrockLLM", AWSBedrockConfig),
    "litellm":             ("mem0.llms.litellm.LiteLLM", BaseLlmConfig),
    "azure_openai":        ("mem0.llms.azure_openai.AzureOpenAILLM", AzureOpenAIConfig),
    "openai_structured":   ("mem0.llms.openai_structured.OpenAIStructuredLLM", OpenAIConfig),
    "anthropic":           ("mem0.llms.anthropic.AnthropicLLM", AnthropicConfig),
    "azure_openai_structured": ("mem0.llms.azure_openai_structured.AzureOpenAIStructuredLLM", AzureOpenAIConfig),
    "gemini":              ("mem0.llms.gemini.GeminiLLM", GeminiConfig),
    "deepseek":            ("mem0.llms.deepseek.DeepSeekLLM", DeepSeekConfig),
    "minimax":             ("mem0.llms.minimax.MiniMaxLLM", MinimaxConfig),
    "xai":                 ("mem0.llms.xai.XAILLM", XAIConfig),
    "sarvam":              ("mem0.llms.sarvam.SarvamLLM", BaseLlmConfig),
    "lmstudio":            ("mem0.llms.lmstudio.LMStudioLLM", LMStudioConfig),
    "vllm":                ("mem0.llms.vllm.VllmLLM", VllmConfig),
    "langchain":           ("mem0.llms.langchain.LangchainLLM", BaseLlmConfig),
}
```

> 注意：实际是 18 个 key,但部分 provider 多个 alias（如 `openai_structured`）。AGENTS.md 写 21 个,差异可能在子变体或新增。

### 3.2 `create()` 三种 config 输入处理

```python
@classmethod
def create(cls, provider_name, config=None, **kwargs):
    if provider_name not in cls.provider_to_class:
        raise ValueError(f"Unsupported Llm provider: {provider_name}")

    class_type, config_class = cls.provider_to_class[provider_name]
    llm_class = load_class(class_type)   # 动态加载

    if config is None:
        # case 1: 没传 config,用 kwargs 构造默认
        config = config_class(**kwargs)

    elif isinstance(config, dict):
        # case 2: dict,merge kwargs 后构造
        config = {**config, **kwargs}
        config = config_class(**config)

    elif isinstance(config, BaseLlmConfig):
        # case 3: BaseLlmConfig 实例 → 转 provider-specific config
        if config_class != BaseLlmConfig:
            config_dict = {
                "model": config.model,
                "temperature": config.temperature,
                "api_key": config.api_key,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "enable_vision": config.enable_vision,
                "vision_details": config.vision_details,
                "http_client_proxies": config.http_client_proxies,
            }
            # ⭐ 智能转发 reasoning 字段（只在 provider 接受时）
            params = inspect.signature(config_class).parameters
            accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in params.values())
            if accepts_kwargs or "reasoning_effort" in params:
                config_dict["reasoning_effort"] = config.reasoning_effort
            if accepts_kwargs or "is_reasoning_model" in params:
                config_dict["is_reasoning_model"] = config.is_reasoning_model
            config_dict.update(kwargs)
            config = config_class(**config_dict)
        else:
            # provider 用 base config,直接用
            pass
    else:
        # 假定已是正确的 config 类型
        pass

    return llm_class(config)
```

### 3.3 ⭐ `register_provider()` 运行时扩展

```python
@classmethod
def register_provider(cls, name, class_path, config_class=None):
    """让第三方包注册自定义 provider"""
    if config_class is None:
        config_class = BaseLlmConfig
    cls.provider_to_class[name] = (class_path, config_class)
```

### 使用示例

```python
# 第三方包 my_pkg 提供 CustomLLM
from mem0.utils.factory import LlmFactory
LlmFactory.register_provider(
    name="my_custom",
    class_path="my_pkg.llm.CustomLLM",
    config_class=BaseLlmConfig,
)

# 之后就能用
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import BaseLlmConfig

config = MemoryConfig(
    llm=BaseLlmConfig(provider="my_custom", model="custom-model"),
)
m = Memory(config=config)
```

> 这是 Mem0 SDK 的**核心扩展机制**。所有"添加新 provider"本质上都是改 `provider_to_class` 这个 dict。

---

## 4. `EmbedderFactory`（15 个）

```python
provider_to_class = {
    "openai": "mem0.embeddings.openai.OpenAIEmbedding",
    "ollama": "mem0.embeddings.ollama.OllamaEmbedding",
    "huggingface": "mem0.embeddings.huggingface.HuggingFaceEmbedding",
    "azure_openai": "mem0.embeddings.azure_openai.AzureOpenAIEmbedding",
    "gemini": "mem0.embeddings.gemini.GoogleGenAIEmbedding",
    "vertexai": "mem0.embeddings.vertexai.VertexAIEmbedding",
    "together": "mem0.embeddings.together.TogetherEmbedding",
    "lmstudio": "mem0.embeddings.lmstudio.LMStudioEmbedding",
    "langchain": "mem0.embeddings.langchain.LangchainEmbedding",
    "aws_bedrock": "mem0.embeddings.aws_bedrock.AWSBedrockEmbedding",
    "fastembed": "mem0.embeddings.fastembed.FastEmbedEmbedding",
}

@classmethod
def create(cls, provider_name, config, vector_config: Optional[dict]):
    # 特殊：upstash_vector 启用 enable_embeddings 时用 MockEmbeddings
    if provider_name == "upstash_vector" and vector_config and vector_config.enable_embeddings:
        return MockEmbeddings()

    class_type = cls.provider_to_class.get(provider_name)
    if class_type:
        embedder_instance = load_class(class_type)
        base_config = BaseEmbedderConfig(**config)
        return embedder_instance(base_config)
    else:
        raise ValueError(f"Unsupported Embedder provider: {provider_name}")
```

### 特殊：`MockEmbeddings`

```python
# mem0/embeddings/mock.py
class MockEmbeddings(EmbeddingBase):
    def embed(self, text, memory_action=None):
        return [0.0] * 1536   # 假向量,只测试用
```

某些 vector store 自带 embedding（如 Upstash）,SDK 用 MockEmbeddings 让上层接口一致。

### 注意：EmbedderFactory.create 接 `vector_config`

第 3 个参数 `vector_config` 是 LlmFactory 没有的。因为某些 vector store 自带 embedding（如 Upstash）,embedder 要知道 vector_store 配置才能判断要不要 mock。

---

## 5. `VectorStoreFactory`（28 个）

```python
provider_to_class = {
    "qdrant": "mem0.vector_stores.qdrant.Qdrant",
    "chroma": "mem0.vector_stores.chroma.ChromaDB",
    "pgvector": "mem0.vector_stores.pgvector.PGVector",
    "milvus": "mem0.vector_stores.milvus.MilvusDB",
    "upstash_vector": "mem0.vector_stores.upstash_vector.UpstashVector",
    "azure_ai_search": "mem0.vector_stores.azure_ai_search.AzureAISearch",
    "azure_mysql": "mem0.vector_stores.azure_mysql.AzureMySQL",
    "pinecone": "mem0.vector_stores.pinecone.PineconeDB",
    "mongodb": "mem0.vector_stores.mongodb.MongoDB",
    "redis": "mem0.vector_stores.redis.RedisDB",
    "valkey": "mem0.vector_stores.valkey.ValkeyDB",
    "databricks": "mem0.vector_stores.databricks.Databricks",
    "elasticsearch": "mem0.vector_stores.elasticsearch.ElasticsearchDB",
    "vertex_ai_vector_search": "mem0.vector_stores.vertex_ai_vector_search.GoogleMatchingEngine",
    "opensearch": "mem0.vector_stores.opensearch.OpenSearchDB",
    "supabase": "mem0.vector_stores.supabase.Supabase",
    "weaviate": "mem0.vector_stores.weaviate.Weaviate",
    "faiss": "mem0.vector_stores.faiss.FAISS",
    "langchain": "mem0.vector_stores.langchain.Langchain",
    "s3_vectors": "mem0.vector_stores.s3_vectors.S3Vectors",
    "baidu": "mem0.vector_stores.baidu.BaiduDB",
    "cassandra": "mem0.vector_stores.cassandra.CassandraDB",
    "neptune": "mem0.vector_stores.neptune_analytics.NeptuneAnalyticsVector",
    "turbopuffer": "mem0.vector_stores.turbopuffer.TurbopufferDB",
    "oracledb": "mem0.vector_stores.oracledb.OracleAIVectorSearch",
}

@classmethod
def create(cls, provider_name, config):
    class_type = cls.provider_to_class.get(provider_name)
    if class_type:
        if not isinstance(config, dict):
            config = config.model_dump()   # ⭐ Pydantic → dict
        vector_store_instance = load_class(class_type)
        return vector_store_instance(**config)   # ⭐ **kwargs 透传
    else:
        raise ValueError(f"Unsupported VectorStore provider: {provider_name}")

@classmethod
def reset(cls, instance):
    instance.reset()
    return instance
```

### 关键差异

`create()` 用 `**config` 透传给 provider 的 `__init__`,因为各 provider 的参数差异巨大（不像 LLM 有统一 config）。这就是为什么 `VectorStoreBase.__init__` 不接统一 config（详见 [`01-base-pattern.md`](./01-base-pattern.md) §7）。

---

## 6. `RerankerFactory`（5 个）

```python
provider_to_class = {
    "cohere": ("mem0.reranker.cohere_reranker.CohereReranker", CohereRerankerConfig),
    "sentence_transformer": ("mem0.reranker.sentence_transformer_reranker.SentenceTransformerReranker", SentenceTransformerRerankerConfig),
    "zero_entropy": ("mem0.reranker.zero_entropy_reranker.ZeroEntropyReranker", ZeroEntropyRerankerConfig),
    "llm_reranker": ("mem0.reranker.llm_reranker.LLMReranker", LLMRerankerConfig),
    "huggingface": ("mem0.reranker.huggingface_reranker.HuggingFaceReranker", HuggingFaceRerankerConfig),
}

@classmethod
def create(cls, provider_name, config=None, **kwargs):
    if provider_name not in cls.provider_to_class:
        raise ValueError(f"Unsupported reranker provider: {provider_name}")

    class_path, config_class = cls.provider_to_class[provider_name]

    if config is None:
        config = config_class(**kwargs)
    elif isinstance(config, dict):
        config = config_class(**config, **kwargs)
    elif not isinstance(config, BaseRerankerConfig):
        raise ValueError(f"Config must be a {config_class.__name__} instance or dict")

    try:
        reranker_class = load_class(class_path)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import reranker for provider '{provider_name}': {e}")

    return reranker_class(config)
```

---

## 7. 4 个 Factory 对比

| Factory | provider 数 | 注册结构 | `create()` 第 3 参 | `register_provider()` |
|---------|-----------|---------|------------------|-------------------|
| `LlmFactory` | 18-21 | `(class_path, config_class)` tuple | 无 | ✅ 公开 |
| `EmbedderFactory` | 11-15 | `class_path` str | `vector_config`（特殊） | ❌ 无（手动改 dict） |
| `VectorStoreFactory` | 25-28 | `class_path` str | 无 | ❌ 无 |
| `RerankerFactory` | 5 | `(class_path, config_class)` tuple | 无 | ❌ 无 |

### 为什么 LlmFactory 特殊

LLM 是 **API 变化最快**的领域（reasoning model、新参数等）,所以：
- 注册结构带 config_class（用 inspect.signature 动态判断字段）
- 唯一有 `register_provider()` 公开 API
- 唯一有 `get_supported_providers()` 列举 API

> 其他 Factory 简单加 key 到 dict 即可。

---

## 8. 一个完整的 provider 注册流程

假设要加一个新 LLM provider "FooLLM":

### 步骤 1: 写代码

```python
# mem0/llms/foo.py
from mem0.llms.base import LLMBase
from mem0.configs.llms.base import BaseLlmConfig

class FooLLM(LLMBase):
    def __init__(self, config=None):
        super().__init__(config)
        # 初始化 Foo API client
        self.client = foo_sdk.Client(api_key=self.config.api_key)

    def generate_response(self, messages, tools=None, tool_choice="auto", **kwargs):
        params = self._get_supported_params(messages=messages, **kwargs)
        response = self.client.chat(model=self.config.model, **params)
        return response.text
```

### 步骤 2: 加 config（可选）

如果 FooLLM 有特殊字段（如 `foo_region`）:

```python
# mem0/configs/llms/foo.py
from mem0.configs.llms.base import BaseLlmConfig

class FooConfig(BaseLlmConfig):
    foo_region: str = "us-east-1"
```

### 步骤 3: 注册到 Factory

```python
# mem0/utils/factory.py
from mem0.configs.llms.foo import FooConfig

class LlmFactory:
    provider_to_class = {
        ...
        "foo": ("mem0.llms.foo.FooLLM", FooConfig),
    }
```

### 步骤 4: 加可选依赖

```toml
# pyproject.toml
[project.optional-dependencies]
llms = [
    ...,
    "foo-sdk>=1.0.0",
]
```

### 步骤 5: 测试

```python
# tests/llms/test_foo.py
def test_foo_llm_basic():
    config = FooConfig(model="foo-1", api_key="test")
    llm = FooLLM(config)
    response = llm.generate_response([{"role": "user", "content": "hi"}])
    assert isinstance(response, str)
```

### 步骤 6: 文档

```bash
# docs/integrations/llms/foo.mdx
# + 加到 docs/llms.txt（scope: Both/OSS）
# + 加到 docs/docs.json 导航
```

---

## 9. 设计权衡

| 决策 | 替代方案 | Mem0 选这个的原因 |
|------|---------|----------------|
| 用 `importlib.import_module` 懒加载 | 全量 import | 启动快、依赖少 |
| `provider_to_class` dict 注册 | 装饰器自动注册 | 显式可读、易调试 |
| `register_provider()` 公开 API | 不开放 | 第三方包能扩展 |
| Factory 是 classmethod 不是函数 | 函数式 | 易扩展（继承） |
| `class_path` 是 str 不是 class | class 引用 | 避免不必要的 import |

---

## 10. 调试技巧

### 列举所有支持的 provider

```python
from mem0.utils.factory import LlmFactory
print(LlmFactory.get_supported_providers())
# ['ollama', 'openai', 'anthropic', ...]
```

### 测试某 provider 是否可加载

```python
from mem0.utils.factory import load_class
try:
    cls = load_class("mem0.llms.anthropic.AnthropicLLM")
    print("OK:", cls)
except ImportError as e:
    print("Not installed:", e)
```

### 运行时注册自定义 provider

```python
from mem0.utils.factory import LlmFactory
LlmFactory.register_provider(
    name="my_local",
    class_path="my_module.MyLocalLLM",
)
# 然后用 provider="my_local" 即可
```

---

## 11. 接下来

| 想看 | 去哪 |
|------|------|
| 21 个 LLM provider 对照 | [`02-llms.md`](./02-llms.md) |
| 28 个 vector store 对比 | [`04-vector-stores.md`](./04-vector-stores.md) |
| 5 类抽象模式 | [`01-base-pattern.md`](./01-base-pattern.md) |
| utils（NER + scoring + lemmatize） | [`08-utils.md`](./08-utils.md) |

---

📌 **下一步** → [`02-llms.md`](./02-llms.md) 21 个 LLM provider 实现对照。
