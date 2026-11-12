# Layer 2 — Python SDK Provider 层(D 专题补丁)

> 对应 ONBOARDING.md §5 Layer 2 / 40 个文件 / `notes/02-py-sdk-providers/` 已覆盖 5 个 base + 概述
> 本篇性质:**补丁**——`notes/02/` 已有 8 篇 1700+ 行覆盖设计层,本篇补:
>   1. 文件路径锚点(让 ONBOARDING 提到的 35 个具体 `.py` 都能被 grep 匹配)
>   2. notes/02/ 没深读的大文件:`aws_bedrock.py`(713 行)/ `databricks.py`(881 行)/ `oracledb.py`(602 行)
>   3. 跨子类的设计模式补充(notes/02/ 是分类讲,本篇做跨类对比)
> 上游 HEAD:`4debc58a`

---

## 0. 重要:`notes/02-py-sdk-providers/` 已经讲过的(不重复)

| 笔记 | 行数 | 已覆盖 |
|---|---|---|
| `01-base-pattern.md` | 436 | 5 个 `base.py` 的统一抽象模式 |
| `02-llms.md` | 316 | **21 个 LLM 对比表 + OpenAI / Anthropic / Ollama 三深读** |
| `03-embeddings.md` | 288 | 15 个 embedding provider 概述 |
| `04-vector-stores.md` | 370 | **28 个 vector store 分类 + Qdrant / FAISS / Pinecone 三深读(含 SafeUnpickler、BM25、Hybrid)** |
| `05-graphs.md` | 305 | Neo4j / Memgraph / Kuzu / Apache AGE |
| `06-rerankers.md` | 296 | 5 个 reranker 对比 + Cohere 深读 |
| `07-factory.md` | 453 | `Factory` 工厂实例化 + Provider 注册 |
| `08-utils.md` | 354 | entity_extraction / scoring / lemmatization |

**因此本篇是补丁,不是完整 D 专题。读这篇前请先读上述 8 篇。**

---

## 1. 文件路径锚点(35 个具体 provider .py)

ONBOARDING §5 Layer 2 列了 35 个具体 provider 实现,以下是每个文件的一句话定位 + notes/02/ 的对应位置。

### 1.1 LLM 实现(`mem0/llms/<provider>.py`,9 个 ONBOARDING 提到)

| 文件 | 行数 | 类 | 默认 model | notes/02/02-llms.md 对应章节 |
|---|---|---|---|---|
| `mem0/llms/openai.py` | 150 | `OpenAILLM` | `gpt-5-mini` | §3(完整深读,含 OpenRouter / response_callback / store 参数) |
| `mem0/llms/anthropic.py` | 159 | `AnthropicLLM` | `claude-sonnet-4-6` | §4(完整深读,含 sampling 参数 family 启发式) |
| `mem0/llms/aws_bedrock.py` | **713** | `AWSBedrockLLM` | — | §1 表(本篇 §3 补深读) |
| `mem0/llms/gemini.py` | 228 | `GeminiLLM` | `gemini-1.5-flash-latest` | §1 表(用 google-genai SDK) |
| `mem0/llms/langchain.py` | — | `LangchainLLM` | — | §1 表(包装 LangChain LLM) |
| `mem0/llms/litellm.py` | — | `LiteLLM` | — | §1 表(LiteLLM 多 provider 路由) |
| `mem0/llms/ollama.py` | 144 | `OllamaLLM` | `llama3.1:70b` | §5(深读,本地 Ollama) |
| `mem0/llms/vllm.py` | — | `VllmLLM` | — | §1 表(vLLM server,OpenAI 兼容 API) |
| `mem0/llms/xai.py` | — | `XAILLM` | `grok-beta` | §1 表(xAI Grok,OpenAI 兼容 client) |

补充(ONBOARDING 未列但实际存在):`azure_openai.py` / `azure_openai_structured.py` / `openai_structured.py` / `deepseek.py` / `groq.py` / `together.py` / `lmstudio.py` / `minimax.py` / `sarvam.py`。

### 1.2 Embedding 实现(`mem0/embeddings/<provider>.py`,6 个 ONBOARDING 提到)

| 文件 | 行数 | 类 | 默认 model | notes/02/03-embeddings.md |
|---|---|---|---|---|
| `mem0/embeddings/openai.py` | 81 | `OpenAIEmbedding` | `text-embedding-3-small`(1536 维) | 概述 |
| `mem0/embeddings/huggingface.py` | 66 | `HuggingFaceEmbedding` | `BAAI/bge-m3`(1024 维) | 概述(sentence-transformers) |
| `mem0/embeddings/aws_bedrock.py` | — | `AWSBedrockEmbedding` | — | 概述(Cohere/Titan via Bedrock) |
| `mem0/embeddings/gemini.py` | — | `GeminiEmbedding` | `text-embedding-004`(768 维) | 概述 |
| `mem0/embeddings/ollama.py` | — | `OllamaEmbedding` | `nomic-embed-text`(768 维) | 概述(本地) |
| `mem0/embeddings/vertexai.py` | — | `VertexAIEmbedding` | `text-embedding-004`(768 维) | 概述(GCP) |

补充(ONBOARDING 未列):`azure_openai.py` / `together.py` / `fastembed.py` / `langchain.py`。

### 1.3 Vector Store 实现(`mem0/vector_stores/<provider>.py`,15 个 ONBOARDING 提到)

| 文件 | 行数 | 类 | BM25? | notes/02/04-vector-stores.md |
|---|---|---|---|---|
| `mem0/vector_stores/qdrant.py` | 606 | `Qdrant` | ✅(fastembed) | §2(完整深读,含 3 连接模式) |
| `mem0/vector_stores/faiss.py` | 648 | `FAISS` | ❌ | §3(完整深读,含 SafeUnpickler) |
| `mem0/vector_stores/pinecone.py` | 439 | `PineconeDB` | ✅(pinecone-text) | §4(完整深读) |
| `mem0/vector_stores/pgvector.py` | 559 | `PGVector` | ✅ | §1 表(PostgreSQL + pgvector) |
| `mem0/vector_stores/mongodb.py` | — | `MongoDB` | ✅ | §1 表(Atlas Vector Search) |
| `mem0/vector_stores/redis.py` | — | `RedisDB` | ✅ | §1 表(RediSearch) |
| `mem0/vector_stores/elasticsearch.py` | — | `ElasticsearchDB` | ✅ | §1 表(原生 BM25) |
| `mem0/vector_stores/milvus.py` | — | `MilvusDB` | ✅ | §1 表(Milvus / Zilliz) |
| `mem0/vector_stores/chroma.py` | — | `ChromaDB` | — | §1 表(嵌入式) |
| `mem0/vector_stores/weaviate.py` | — | `Weaviate` | ✅ | §1 表(内置 hybrid) |
| `mem0/vector_stores/supabase.py` | — | `Supabase` | ✅ | §1 表(pgvector 包装) |
| `mem0/vector_stores/cassandra.py` | **503** | `CassandraDB` | ✅ | §1 表(Cassandra 5+) |
| `mem0/vector_stores/azure_mysql.py` | **555** | `AzureMySQL` | — | §1 表 |
| `mem0/vector_stores/databricks.py` | **881** | `Databricks` | ✅ | §1 表(本篇 §4 补深读) |
| `mem0/vector_stores/oracledb.py` | **602** | `OracleAIVectorSearch` | ✅ | §1 表(本篇 §5 补深读) |
| `mem0/vector_stores/neptune_analytics.py` | **535** | `NeptuneAnalyticsVector` | — | §1 表(AWS Neptune + Gremlin) |

补充(ONBOARDING 未列):`opensearch.py` / `valkey.py` / `vertex_ai_vector_search.py` / `azure_ai_search.py` / `turbopuffer.py` / `s3_vectors.py` / `upstash_vector.py` / `baidu.py` / `langchain.py`。

### 1.4 Reranker 实现(`mem0/reranker/<provider>.py`,5 个 ONBOARDING 提到 全部)

| 文件 | 行数 | 类 | 实现方式 | notes/02/06-rerankers.md |
|---|---|---|---|---|
| `mem0/reranker/cohere_reranker.py` | 92 | `CohereReranker` | Cohere rerank API | §3(完整深读) |
| `mem0/reranker/huggingface_reranker.py` | — | `HuggingFaceReranker` | 本地 cross-encoder | §1 表 |
| `mem0/reranker/sentence_transformer_reranker.py` | — | `SentenceTransformerReranker` | sentence-transformers | §1 表 |
| `mem0/reranker/llm_reranker.py` | 172 | `LLMReranker` | 用 LLM 给每条打分 | §1 表(本篇 §6 补深读) |
| `mem0/reranker/zero_entropy_reranker.py` | 103 | `ZeroEntropyReranker` | ZeroEntropy API | §1 表(本篇 §6 补深读) |

---

## 2. 跨子类的设计模式补充(notes/02 是分类讲,本篇做跨类对比)

### 2.1 所有 provider 的"5 步骨架"

无论是 LLM / Embedding / VectorStore / Reranker,具体 provider 的 `__init__` 都遵循同一段:

```python
def __init__(self, config=None):
    # 1. Config 转换:dict → Config 子类;BaseConfig → Config 子类(字段映射)
    if config is None:
        config = XConfig()
    elif isinstance(config, dict):
        config = XConfig(**config)
    elif isinstance(config, BaseXConfig) and not isinstance(config, XConfig):
        config = XConfig(model=config.model, ...)
    
    super().__init__(config)
    
    # 2. 默认 model / collection_name 兜底
    if not self.config.model:
        self.config.model = "default-model"
    
    # 3. API key 解析(config 优先,fallback 到环境变量)
    api_key = self.config.api_key or os.getenv("X_API_KEY")
    if not api_key:
        raise ValueError("X API key required")
    
    # 4. 初始化 SDK client
    self.client = XSDK(api_key=api_key)
    
    # 5. 资源就绪检查(collection 存在?create_col)
    self.create_col(...)
```

这 5 步是 Mem0 的"provider 契约"。**任何新 provider 必须照此实现**。

### 2.2 Config 子类的 3 个等级

| 等级 | Config 类 | 何时用 |
|---|---|---|
| **基类** | `BaseLlmConfig` / `BaseVectorStoreConfig` | provider 不需要特殊字段时直接用(LiteLLM、Groq、Together) |
| **常规子类** | `OpenAIConfig` / `AnthropicConfig` / `QdrantConfig` 等 | provider 有 1-10 个特殊字段(openai_base_url、anthropic 的 family 推断等) |
| **复杂子类** | `AWSBedrockConfig`(bedrock 多 provider 路由) / `DatabricksConfig`(SQL + Delta Sync) | provider 接口本身复杂,需要大量配置 |

**这个等级决定 `__init__` 的复杂度**——基类 provider 几十行,复杂子类数百行(`aws_bedrock.py` 713 行 / `databricks.py` 881 行)。

### 2.3 错误处理的 3 种策略(跨类不一致)

| 策略 | 用法 | 例子 |
|---|---|---|
| **强失败**(默认) | ImportError 直接 raise | `aws_bedrock.py:9-10`:`raise ImportError("The 'boto3' library is required...")` |
| **降级 + warning** | 失败时返 fallback,记 warning | `reranker/zero_entropy_reranker.py:95-104`:rerank 失败时返原顺序 + `rerank_score=0.0` |
| **lazy 加载 + sentinel** | 第一次用才加载,失败标记 sentinel | `qdrant.py` BM25 encoder:`self._bm25_encoder = False`(sentinel),后续调用看 sentinel 跳过 |

**这 3 种策略各自适合的场景**:
- 强失败:provider 是核心,缺依赖没法跑
- 降级:辅助功能(BM25、reranker),失败也不阻塞主流程
- lazy:启动速度优先,可选依赖不要拖慢 init

### 2.4 行数分布的"长尾规律"

```
LLM        最长 aws_bedrock.py(713),其他多为 100-250 行,呈长尾
Embedding  最长 ~250 行,多为 50-100 行(embedding 接口简单)
VectorStore 最长 databricks.py(881),其次 faiss(648)/ qdrant(606)/ oracledb(602),
            但 cassandra/azure_mysql/neptune 也在 500+,呈双峰(简单 ~200,复杂 ~600)
Reranker   最长 llm_reranker(172),其他 90-110 行(rerank 接口最简单)
```

**结论**:**VectorStore 是这一层最复杂、最值得投入审计的子类**——因为不同 vector store 的接口差异最大(BM25 vs 无、server vs 嵌入式、SQL vs NoSQL),适配工作量天然大。

---

## 3. `aws_bedrock.py`(713 行,LLM 最大)深读补丁

notes/02/02-llms.md §1 只在表里给了一行,本节补深读。

### 3.1 文件作用

AWS Bedrock 是 **AWS 托管的多 LLM 路由服务**——一个 API 接口对接 Anthropic / Meta / Mistral / Cohere / AI21 / Stability / Amazon 等十余家 provider。`AWSBedrockLLM` 是 Mem0 对接 Bedrock 的适配器。

### 3.2 关键设计

#### 3.2.1 PROVIDERS 表 + `extract_provider()` 函数(L19-31)

```python
PROVIDERS = [
    "ai21", "amazon", "anthropic", "cohere", "meta", "mistral", "stability", "writer",
    "deepseek", "gpt-oss", "perplexity", "snowflake", "titan", "command", "j2", "llama",
    "minimax",
]

def extract_provider(model: str) -> str:
    for provider in PROVIDERS:
        if re.search(rf"\b{re.escape(provider)}\b", model):
            return provider
    raise ValueError(f"Unknown provider in model: {model}")
```

**为什么需要这函数**:Bedrock 的 `converse` API 不同 provider 的工具调用格式不同——必须先从 model ID(如 `anthropic.claude-3-5-sonnet-20241022-v2:0`)抽出 provider,再走对应分支。这是 Bedrock 多 provider 路由的核心复杂度。

#### 3.2.2 generate_response 的 provider 分支

后续 `generate_response()` 根据 `extract_provider(self.config.model)` 的结果,**为每个 provider 走不同的 tool 格式转换**——这是为什么文件能到 713 行。

#### 3.2.3 boto3 auth 复杂度

不像 OpenAI 一个 api_key 搞定,AWS 用 `boto3.Session().client("bedrock-runtime")`,需要:
- AWS access key ID
- AWS secret access key  
- AWS session token(可选,临时凭证)
- AWS region
- profile name(可选,从 `~/.aws/credentials` 读)

任何一项缺失或权限不够(IAM policy 要允许 `bedrock:InvokeModel` / `bedrock:InvokeModelWithResponseStream`)都会失败,所以这文件大量篇幅在做 auth fallback 和错误信息。

### 3.3 为什么是 LLM 中最大的(713 行 vs 第二 ~250 行)

- Bedrock 接 17 个 provider,每个 provider 的工具调用 schema 不一样
- AWS auth 多种方式(profile / env / 临时凭证)
- 流式响应处理(ResponseStream API)
- 错误处理的 `ClientError` 错误码爆炸

**结论**:**如果团队不用 Bedrock,这个文件可以略读**;要用 Bedrock,这文件是核心。

---

## 4. `databricks.py`(881 行,VectorStore 最大)深读补丁

notes/02/04-vector-stores.md §1 只在表里给了一行,本节补深读。

### 4.1 文件作用

Databricks Vector Search 是 **Databricks 平台内置的 vector search 服务**,Mem0 通过 `databricks.sdk.WorkspaceClient` 接入。两种索引:
- **Delta Sync Index**:自动从 Delta Table 同步(写入 Delta Table,索引自动更新)
- **Direct Access Index**:直接 API 写入,不走 Delta Table

### 4.2 关键设计

#### 4.2.1 SQL 标识符验证(L41-48)

```python
_VALID_SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def _validate_identifier(name: str, label: str = "identifier") -> str:
    if not isinstance(name, str) or not _VALID_SQL_IDENTIFIER.match(name):
        raise ValueError(f"Invalid {label}: {name!r}")
    return name
```

**为什么必须有这层验证**:Databricks 用 SQL 字符串拼接(不是参数化)构造 DDL/DML——如果 collection_name 含特殊字符或注入,可能执行任意 SQL。**这是该文件最重要的安全设计**。

#### 4.2.2 `MemoryResult` Pydantic 模型(L33-37)

```python
class MemoryResult(BaseModel):
    id: Optional[str] = None
    score: Optional[float] = None
    payload: Optional[dict] = None
```

所有 vector store 都有类似的输出模型(叫 `OutputData` / `MemoryResult` / `Document` 等),作用是把 provider 返回的 heterogeneous dict 统一成 Mem0 内部的 `{id, score, payload}` 三元组。

#### 4.2.3 `excluded_keys` 集合(L39)

```python
excluded_keys = {"user_id", "agent_id", "run_id", "hash", "data", "created_at", "updated_at"}
```

**为什么需要**:Databricks 把 metadata 当 column 存,但 Mem0 的 metadata 里既有"搜索用 scope 字段"(user_id 等)又有"实际元数据"。**写入 Databricks 时 scope 字段不进 metadata column**(它们已经存在 primary key constraint 里了),避免冗余存储。

#### 4.2.4 为什么是 VectorStore 中最大的(881 行 vs 第二 faiss 648 行)

- Databricks SDK 接口本身复杂(`WorkspaceClient` + 多个 service)
- 双索引类型(Delta Sync vs Direct Access)各自一套逻辑
- Delta Table DDL 操作(CREATE TABLE / ALTER / INSERT / MERGE)
- Auto-discovery:索引不存在时自动创建(等几分钟)
- Hybrid search(BM25 + semantic)用 Databricks 原生 function

**结论**:**如果团队不用 Databricks,这文件可以略读**;要用,要专门花时间消化 Delta Sync 索引的生命周期。

---

## 5. `oracledb.py`(602 行)深读补丁

### 5.1 文件作用

Oracle 23ai 引入 **AI Vector Search**——Oracle 数据库原生支持 vector 类型。`oracledb.py` 是 Mem0 对接 Oracle 的适配器。

### 5.2 关键设计

#### 5.2.1 距离度量 → score 转换(L47-50)

```python
_SCORE_FROM_DISTANCE = {
    "COSINE": lambda d: max(0.0, min(1.0, 1.0 - d)),
    "EUCLIDEAN": lambda d: 1.0 / (1.0 + max(0.0, d)),
    "EUCLIDEAN_SQUARED": lambda d: 1.0 / (1.0 + math.sqrt(max(0.0, d))),
    ...
}
```

**为什么需要**:Mem0 内部约定 `score ∈ [0, 1]`(越大越好),但 Oracle 返回的是 distance(越小越好,且范围不定)。不同距离度量需要不同转换公式:
- Cosine distance:`1 - d`(cosine distance ∈ [0, 2],转后 ∈ [-1, 1],再 clamp 到 [0, 1])
- Euclidean:`1 / (1 + d)`(把 [0, ∞] 压缩到 (0, 1])
- Euclidean squared:`1 / (1 + sqrt(d))`(先开方,变成普通 Euclidean)

**这是跨 vector store 的共通问题**——每个 store 都有自己的 score/distance 定义,Mem0 必须在 adapter 层统一。

#### 5.2.2 metadata key 验证(L38-44)

```python
METADATA_PATTERN = re.compile(r"[a-zA-Z0-9_\.\[\],\s\*]+")

def _validate_metadata_key(metadata_key: str) -> None:
    if not METADATA_PATTERN.fullmatch(metadata_key):
        raise ValueError(
            f"Invalid metadata key '{metadata_key}'. "
            "Only letters, numbers, underscores, nesting via '.', "
            "and array wildcards '[*]' are allowed."
        )
```

Oracle 的 JSON path 查询语法限制 metadata key 字符。这种"**adapter 层把 host 限制暴露给上层**"的模式,在所有 vector store 里都有,只是限制不同:
- Databricks:必须匹配 `^[A-Za-z_][A-Za-z0-9_]*$`(纯 SQL 标识符)
- Oracle:允许 `.` 嵌套和 `[*]` 数组(JSON path)
- Qdrant:几乎任意字符(payload 是 JSON)
- Pinecone:有限制但宽松

**这种异构是 VectorStore 适配器的核心复杂度来源**。

---

## 6. Reranker 跨类对比补丁(notes/02/06 只深读了 Cohere)

### 6.1 5 个 reranker 的关键差异

| Reranker | 依赖 | 离线? | 复杂度 | 失败行为 |
|---|---|---|---|---|
| `CohereReranker` | `cohere` SDK | ❌(API) | 92 行 | raise |
| `HuggingFaceReranker` | `sentence-transformers` + model 下载 | ✅(模型本地) | — | raise |
| `SentenceTransformerReranker` | `sentence-transformers` | ✅ | — | raise |
| `LLMReranker`(172 行) | 复用已配置的 LLM | 跟 LLM | 较复杂 | raise |
| `ZeroEntropyReranker`(103 行) | `zeroentropy` SDK | ❌(API) | 104 行 | **降级返原顺序 + rerank_score=0.0** |

### 6.2 `ZeroEntropyReranker` 的"降级"哲学

```python
# zero_entropy_reranker.py:95-104
except Exception as e:
    # Fallback to original order if reranking fails
    logger.warning("Zero Entropy reranking failed, falling back to original order: %s", e)
    fallback_docs = []
    for doc in documents:
        fallback_doc = doc.copy()
        fallback_doc['rerank_score'] = 0.0
        fallback_docs.append(fallback_doc)
    final_top_k = top_k or self.config.top_k
    return fallback_docs[:final_top_k] if final_top_k else fallback_docs
```

**降级而不是 raise**:rerank 是"锦上添花",失败时返回原始顺序比中断流程更好。**这是 reranker 应有的契约**——Cohere/HuggingFace/SentenceTransformer 都该改成这样,但目前不是(它们 raise)。

### 6.3 `LLMReranker` 的"零依赖"思路

LLMReranker **复用 Mem0 已配置的 LLM**(OpenAI/Anthropic/etc.),不需要额外装包。它把 rerank 转成 prompt:`"给定 query 和 documents,给每条打 0-100 分"`。**优点**:零新依赖;**缺点**:慢且贵(LLM 调用比 Cohere rerank 慢 10x)。适合**没有 Cohere/ZeroEntropy 账号、又不想下载 HuggingFace 模型**的场景。

---

## 7. 该层的"反模式 / 坑"

### 7.1 dimension 不匹配的静默错误

每个 embedding provider 的默认 model 维度不一样(OpenAI 1536 / HuggingFace 1024 / Gemini 768 / Ollama 768)。如果**先创建 collection 用 OpenAI(1536),后切换 embedder 到 Gemini(768),vector store 会拒绝写入**——但 Mem0 不主动检测,错误会从 vector store SDK 抛出,信息不直观。

**解决**:`MemoryConfig.vector_store.embedding_model_dims` 必须手工设,且要跟 embedder 实际维度对齐。`create_col()` 时 Mem0 用这值创建 collection。

### 7.2 SQL 注入面(Databricks / Oracle / PGVector)

凡是基于 SQL 的 vector store,**collection_name 和 metadata key 都是 SQL 注入面**。Mem0 的策略:
- Databricks:`_VALID_SQL_IDENTIFIER` regex
- Oracle:`METADATA_PATTERN` regex(允许 JSON path)
- PGVector:用参数化查询(`%s`)

但**用户仍可能在 metadata value 里注入**(虽然参数化能挡)。**审计建议**:如果团队基于 SQL vector store 二次开发,优先审 SQL 构造逻辑。

### 7.3 BM25 encoder 的版本依赖

Qdrant 的 BM25 用 `fastembed` 的 `Qdrant/bm25`,Pinecone 用 `pinecone-text` 的 `BM25Encoder`,这两个是**不同的 BM25 实现**(不同 tokenizer / 不同 IDF 计算),所以**跨 store 的 BM25 分数不可比**——这是 multi-signal fusion 时要注意的。

### 7.4 Reranker 的 top_k 语义混淆

`rerank(query, documents, top_k=None)`:
- `top_k=None`:返回全部 documents(只是 reranked 顺序)
- `top_k=10`:只返回前 10 条
- config.top_k:provider 默认值

调用方经常混淆——传 `top_k=None` 期望"返回所有",但某些 provider(如 Cohere)的 API `top_n=None` 默认返回全部,某些可能默认 10。**契约上应该统一**:"None 永远表示全部"。

---

## 8. 阅读完本补丁后应该理解

- ✅ notes/02/ 8 篇已经讲过的不再重复
- ✅ 35 个具体 provider `.py` 文件的路径锚点
- ✅ aws_bedrock.py / databricks.py / oracledb.py 三个大文件的关键设计
- ✅ 所有 provider 的"5 步骨架"和 Config 子类三级
- ✅ 错误处理的 3 种策略(强失败 / 降级 / lazy)
- ✅ SQL vector store 的注入面和防护
- ✅ 距离 → score 转换的数学(Cosine / Euclidean)
- ✅ ZeroEntropyReranker 的降级哲学
- ✅ dimension 不匹配的静默错误

---

📌 **下一步**:
- 已经把 L10 集成专题(D 深度)+ L2 Provider 补丁(浅)完成
- 接下来按 ROI 顺序:L11 Skill(D 专题,13 文件全空)→ L7 Dashboard(C 综述)→ L6 TS SDK(C 补丁)→ ...
