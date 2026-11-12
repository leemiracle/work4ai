<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/MiniRAG · page 6 LLM and Embedding Integration · fetched 2026-11-09 -->

# LLM and Embedding Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/llm/openai.py](minirag/llm/openai.py)

</details>



This document describes how MiniRAG integrates with Large Language Models (LLMs) and embedding models to power both the indexing and query phases of the RAG pipeline. It covers the abstraction interfaces, provider implementations, and integration points within the system architecture.

For detailed information about specific aspects of LLM integration:
- LLM interface implementations and provider-specific functions: see [LLM Interface](#6.1)
- Embedding function wrappers and generation: see [Embedding Functions](#6.2)  
- Supported model list and performance characteristics: see [Supported Models](#6.3)

## Purpose and Scope

MiniRAG's LLM and embedding integration layer provides:

1. **Unified async interfaces** for multiple LLM providers (OpenAI, HuggingFace, NVIDIA, OpenRouter)
2. **Embedding function abstraction** with dimension and token size metadata
3. **Retry and error handling** logic for robust API interactions
4. **Streaming and batch support** for different usage patterns

This layer decouples the core RAG logic from specific LLM implementations, enabling flexible model selection based on deployment constraints (cloud APIs, on-device models, or hybrid approaches).

---

## System Integration Architecture

The following diagram shows how LLM and embedding components integrate with the broader MiniRAG system:

**Diagram 1: LLM and Embedding Integration in MiniRAG Architecture**

```mermaid
graph TB
    subgraph "MiniRAG Core"
        MiniRAG["MiniRAG Class<br/>(minirag.py)"]
        Operate["RAG Operations<br/>(operate.py)"]
    end
    
    subgraph "LLM Integration Layer"
        LLMFunc["async LLM Functions"]
        
        subgraph "Provider Implementations"
            OpenAIComplete["openai_complete()"]
            GPT4o["gpt_4o_mini_complete()"]
            NvidiaComplete["nvidia_openai_complete()"]
            OpenRouterComplete["openrouter_openai_complete()"]
            HFComplete["hf_model_complete()"]
        end
        
        LLMFunc --> OpenAIComplete
        LLMFunc --> GPT4o
        LLMFunc --> NvidiaComplete
        LLMFunc --> OpenRouterComplete
        LLMFunc --> HFComplete
    end
    
    subgraph "Embedding Integration Layer"
        EmbedFunc["Embedding Functions"]
        
        subgraph "Embedding Implementations"
            OpenAIEmbed["openai_embed()<br/>text-embedding-3-small"]
            HFEmbed["HuggingFace Embeddings<br/>sentence-transformers"]
        end
        
        EmbedFunc --> OpenAIEmbed
        EmbedFunc --> HFEmbed
        
        Wrapper["@wrap_embedding_func_with_attrs<br/>embedding_dim, max_token_size"]
        Wrapper -.decorates.-> OpenAIEmbed
        Wrapper -.decorates.-> HFEmbed
    end
    
    subgraph "Storage Layer"
        VectorDB["Vector Storage<br/>entity_vdb, chunks_vdb"]
        GraphDB["Graph Storage<br/>entities, relationships"]
        KVDB["KV Storage<br/>text chunks"]
    end
    
    MiniRAG --> Operate
    Operate --> LLMFunc
    Operate --> EmbedFunc
    
    EmbedFunc --> VectorDB
    LLMFunc -.extracts entities.-> GraphDB
    LLMFunc -.generates text.-> KVDB
    
    style MiniRAG fill:#f9f9f9
    style LLMFunc fill:#f9f9f9
    style EmbedFunc fill:#f9f9f9
    style Wrapper fill:#e8e8e8
```

Sources: [minirag/llm/openai.py:1-267](), [README.md:36-42]()

---

## Two-Phase LLM Usage Pattern

MiniRAG uses LLMs and embeddings in distinct ways during the indexing and query phases:

**Diagram 2: LLM Calls in Indexing and Query Phases**

```mermaid
sequenceDiagram
    participant Docs as "Input Documents"
    participant MiniRAG as "MiniRAG.insert()"
    participant Operate as "operate.py"
    participant LLM as "LLM Functions"
    participant Embed as "Embedding Functions"
    participant Storage as "Storage Layer"
    
    rect rgb(245, 245, 245)
        Note over Docs,Storage: Phase 1: Indexing
        Docs->>MiniRAG: Raw text documents
        MiniRAG->>MiniRAG: Chunk into segments
        MiniRAG->>Operate: extract_entities(chunks)
        Operate->>LLM: Call with entity extraction prompt
        Note over LLM: openai_complete()<br/>gpt_4o_mini_complete()<br/>hf_model_complete()
        LLM-->>Operate: JSON with entities & relationships
        Operate->>Embed: Generate embeddings for entities
        Note over Embed: openai_embed()<br/>with text-embedding-3-small
        Embed-->>Operate: Embedding vectors
        Operate->>Embed: Generate embeddings for chunks
        Embed-->>Operate: Chunk embedding vectors
        Operate->>Storage: Store entities in graph_storage
        Operate->>Storage: Store embeddings in vector_storage
        Operate->>Storage: Store text in kv_storage
    end
    
    rect rgb(250, 250, 250)
        Note over Docs,Storage: Phase 2: Query
        Docs->>MiniRAG: User query string
        MiniRAG->>Operate: minirag_query(query)
        Operate->>LLM: Extract entities from query
        LLM-->>Operate: Query entities
        Operate->>Embed: Generate query embedding
        Embed-->>Operate: Query vector
        Operate->>Storage: Retrieve via graph + vector search
        Storage-->>Operate: Relevant chunks & entities
        Operate->>LLM: Generate answer with context
        Note over LLM: Stream or batch response
        LLM-->>Operate: Final answer text
        Operate-->>MiniRAG: Formatted response
    end
```

Sources: [minirag/llm/openai.py:93-169](), [README.md:36-42]()

---

## LLM Interface Design Pattern

All LLM integrations follow a consistent async interface pattern that provides:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| **Async Execution** | `async def` functions | Non-blocking I/O for API calls |
| **Retry Logic** | `@retry` decorator with exponential backoff | Handle rate limits and transient failures |
| **Streaming Support** | `AsyncIterator[str]` return type | Enable real-time response generation |
| **Message History** | `history_messages` parameter | Support conversational context |
| **System Prompts** | `system_prompt` parameter | Configure model behavior |
| **Provider Abstraction** | Unified function signature | Swap providers without code changes |

**Function Signature Pattern:**

```python
async def {provider}_complete(
    prompt: str,
    system_prompt: str = None,
    history_messages: List[Dict] = [],
    keyword_extraction: bool = False,
    **kwargs
) -> Union[str, AsyncIterator[str]]
```

Sources: [minirag/llm/openai.py:156-169](), [minirag/llm/openai.py:93-154]()

---

## LLM Provider Implementations

**Diagram 3: LLM Provider Architecture**

```mermaid
graph TB
    subgraph "Core Interface Pattern"
        BaseSignature["async complete()<br/>prompt, system_prompt, history_messages"]
    end
    
    subgraph "OpenAI-Compatible Providers"
        OpenAIImpl["openai_complete_if_cache()<br/>minirag/llm/openai.py:93-154"]
        
        OpenAIAPI["OpenAI API<br/>AsyncOpenAI client<br/>base_url: api.openai.com"]
        GPT4oMini["gpt_4o_mini_complete()<br/>model: gpt-4o-mini<br/>lines 187-199"]
        GPT4o["gpt_4o_complete()<br/>model: gpt-4o<br/>lines 172-184"]
        
        NvidiaAPI["NVIDIA API<br/>base_url: integrate.api.nvidia.com<br/>lines 202-216"]
        OpenRouterAPI["OpenRouter API<br/>base_url: openrouter.ai<br/>lines 218-241"]
        
        OpenAIImpl --> OpenAIAPI
        OpenAIImpl --> GPT4oMini
        OpenAIImpl --> GPT4o
        OpenAIImpl --> NvidiaAPI
        OpenAIImpl --> OpenRouterAPI
    end
    
    subgraph "HuggingFace Provider"
        HFImpl["hf_model_complete()<br/>Local or API models"]
        
        HFModels["Phi-3.5-mini-instruct<br/>GLM-Edge-1.5B-Chat<br/>Qwen2.5-3B-Instruct<br/>MiniCPM3-4B"]
        
        HFImpl --> HFModels
    end
    
    subgraph "Retry & Error Handling"
        RetryDec["@retry decorator<br/>tenacity library"]
        Exceptions["RateLimitError<br/>APIConnectionError<br/>APITimeoutError"]
        Backoff["Exponential backoff<br/>min=4s, max=60s<br/>max 3 attempts"]
        
        RetryDec --> Exceptions
        RetryDec --> Backoff
    end
    
    BaseSignature -.implements.-> OpenAIImpl
    BaseSignature -.implements.-> HFImpl
    
    RetryDec -.protects.-> OpenAIImpl
    RetryDec -.protects.-> HFImpl
    
    style BaseSignature fill:#f9f9f9
    style RetryDec fill:#f9f9f9
```

Sources: [minirag/llm/openai.py:81-241](), [README.md:74-89]()

---

## Embedding Function Architecture

The embedding integration uses a decorator pattern to attach metadata to embedding functions:

**Diagram 4: Embedding Function Wrapper Pattern**

```mermaid
graph LR
    subgraph "Decorator Pattern"
        WrapperFunc["@wrap_embedding_func_with_attrs<br/>minirag/utils.py"]
        
        Attrs["Function Attributes:<br/>embedding_dim=1536<br/>max_token_size=8192"]
        
        WrapperFunc --> Attrs
    end
    
    subgraph "Embedding Implementation"
        OpenAIEmbedFunc["openai_embed()<br/>minirag/llm/openai.py:243-267"]
        
        RetryLogic["@retry<br/>3 attempts<br/>4-60s backoff"]
        
        AsyncClient["AsyncOpenAI.embeddings.create()<br/>model: text-embedding-3-small"]
        
        NumpyArray["Returns: np.ndarray<br/>shape: (n_texts, 1536)"]
        
        RetryLogic --> OpenAIEmbedFunc
        OpenAIEmbedFunc --> AsyncClient
        AsyncClient --> NumpyArray
    end
    
    subgraph "Usage in MiniRAG"
        VectorStores["Vector Storage:<br/>entity_vdb<br/>entity_name_vdb<br/>relationships_vdb<br/>chunks_vdb"]
        
        Quantization["Optional Quantization:<br/>Reduce storage size"]
        
        NumpyArray --> VectorStores
        NumpyArray --> Quantization
    end
    
    WrapperFunc -.decorates.-> OpenAIEmbedFunc
    Attrs -.metadata for.-> VectorStores
    
    style WrapperFunc fill:#f9f9f9
    style OpenAIEmbedFunc fill:#f9f9f9
```

Sources: [minirag/llm/openai.py:243-267](), [minirag/llm/openai.py:69-74]()

---

## Configuration and API Keys

LLM and embedding functions access credentials through environment variables:

| Environment Variable | Purpose | Used By |
|---------------------|---------|---------|
| `OPENAI_API_KEY` | OpenAI authentication | `openai_complete()`, `openai_embed()` |
| `OPENAI_API_BASE` | Custom OpenAI endpoint | `openai_complete_if_cache()` |
| `OPENROUTER_API_KEY` | OpenRouter authentication | `openrouter_openai_complete()` |

**Configuration Flow:**

```mermaid
graph LR
    subgraph "Configuration Sources"
        EnvVars["Environment Variables"]
        FuncArgs["Function Arguments<br/>api_key, base_url"]
    end
    
    subgraph "Priority Logic"
        ArgCheck["Check function args"]
        EnvCheck["Check os.environ"]
        SetEnv["os.environ[KEY] = value"]
    end
    
    subgraph "Client Initialization"
        AsyncClient["AsyncOpenAI()<br/>or<br/>AsyncOpenAI(base_url=...)"]
    end
    
    FuncArgs --> ArgCheck
    ArgCheck -->|if provided| SetEnv
    ArgCheck -->|if not provided| EnvCheck
    EnvVars --> EnvCheck
    
    SetEnv --> AsyncClient
    EnvCheck --> AsyncClient
    
    style ArgCheck fill:#f9f9f9
```

Sources: [minirag/llm/openai.py:102-108](), [minirag/llm/openai.py:226-227](), [minirag/llm/openai.py:257-258]()

---

## Streaming Response Support

LLM functions can return either complete strings or async iterators for streaming:

**Return Type Handling:**

```python
# From minirag/llm/openai.py:131-153
if hasattr(response, "__aiter__"):
    # Streaming response
    async def inner():
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content is None:
                continue
            if r"\u" in content:
                content = safe_unicode_decode(content.encode("utf-8"))
            yield content
    return inner()  # Returns AsyncIterator[str]
else:
    # Complete response
    content = response.choices[0].message.content
    if r"\u" in content:
        content = safe_unicode_decode(content.encode("utf-8"))
    return content  # Returns str
```

This dual-mode support enables:
- **Batch processing** during indexing for efficiency
- **Real-time streaming** during query for user experience
- **Flexible integration** with different downstream consumers

Sources: [minirag/llm/openai.py:131-153]()

---

## Error Handling and Resilience

The LLM integration layer implements comprehensive error handling:

**Error Handling Strategy:**

| Error Type | Handling | Configuration |
|------------|----------|---------------|
| `RateLimitError` | Exponential backoff retry | Wait 4-60s, max 3 attempts |
| `APIConnectionError` | Automatic retry | Same backoff strategy |
| `APITimeoutError` | Automatic retry | Same backoff strategy |
| Empty response | Logged warning + empty string | No retry (data issue) |
| Unicode errors | `safe_unicode_decode()` | Automatic correction |

The retry decorator is applied at two levels:

1. **Function level**: [minirag/llm/openai.py:81-87]() for `openai_complete_if_cache()`
2. **Embedding level**: [minirag/llm/openai.py:244-250]() for `openai_embed()`

Sources: [minirag/llm/openai.py:81-87](), [minirag/llm/openai.py:144-150](), [minirag/llm/openai.py:244-250]()

---

## Keyword Extraction Mode

LLM functions support a special `keyword_extraction` mode for structured entity extraction:

**Extraction Flow:**

```mermaid
graph TB
    Query["User Query or Document Chunk"]
    
    ExtractFlag["keyword_extraction=True"]
    
    FormatSet["Set response_format"]
    
    subgraph "OpenAI API"
        JSONFormat["response_format='json'<br/>or<br/>GPTKeywordExtractionFormat"]
        
        StructuredOutput["beta.chat.completions.parse()"]
    end
    
    subgraph "Other Providers"
        FreeForm["Standard completion"]
        JSONParse["locate_json_string_body_from_string()"]
    end
    
    Result["Structured Entity Data"]
    
    Query --> ExtractFlag
    ExtractFlag -->|if True| FormatSet
    FormatSet --> JSONFormat
    FormatSet --> FreeForm
    
    JSONFormat --> StructuredOutput
    FreeForm --> JSONParse
    
    StructuredOutput --> Result
    JSONParse --> Result
    
    style ExtractFlag fill:#f9f9f9
    style Result fill:#f9f9f9
```

The `GPTKeywordExtractionFormat` schema:

```python
class GPTKeywordExtractionFormat(BaseModel):
    high_level_keywords: List[str]
    low_level_keywords: List[str]
```

Sources: [minirag/llm/openai.py:89-92](), [minirag/llm/openai.py:157-161](), [minirag/llm/openai.py:214-216]()

---

## Integration with MiniRAG Core

The LLM and embedding functions are accessed through the `QueryParam` configuration:

**Configuration Structure:**

| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `llm_model_func` | LLM function reference | `openai_complete`, `gpt_4o_mini_complete` |
| `llm_model_name` | Model identifier | `"gpt-4o-mini"`, `"Phi-3.5-mini-instruct"` |
| `embedding_func` | Embedding function | `openai_embed` with decorator attributes |
| `embedding_dim` | Inferred from function | `1536` (from decorator) |
| `max_token_size` | Inferred from function | `8192` (from decorator) |

The core MiniRAG class passes these through the `hashing_kv` global config:

```python
# Pattern used in minirag/llm/openai.py:162-163
model_name = kwargs["hashing_kv"].global_config["llm_model_name"]
return await openai_complete_if_cache(model_name, prompt, ...)
```

Sources: [minirag/llm/openai.py:162-169](), [minirag/llm/openai.py:243]()

---

## Performance Characteristics

Different LLM and embedding combinations affect MiniRAG performance:

**Model Performance on LiHua-World Dataset:**

| Model | Type | Parameters | Accuracy | Error Rate | Use Case |
|-------|------|-----------|----------|------------|----------|
| Phi-3.5-mini-instruct | SLM | ~3.8B | 53.29% | 23.35% | On-device |
| GLM-Edge-1.5B-Chat | SLM | 1.5B | 52.51% | 25.71% | Resource-constrained |
| Qwen2.5-3B-Instruct | SLM | 3B | 48.75% | 26.02% | Edge deployment |
| MiniCPM3-4B | SLM | 4B | 51.25% | 21.79% | Balanced |
| gpt-4o-mini | LLM | Unknown | 54.08% | 19.44% | Cloud API |

**Embedding Model:**
- Default: `text-embedding-3-small` with 1536 dimensions
- Storage optimization: 25% reduction vs. traditional RAG through quantization

Sources: [README.md:74-89](), [minirag/llm/openai.py:243]()

---

## Summary

The LLM and embedding integration layer in MiniRAG provides:

1. **Unified async interface** across multiple providers (OpenAI, HuggingFace, NVIDIA, OpenRouter)
2. **Robust error handling** with automatic retry and exponential backoff
3. **Flexible response modes** supporting both streaming and batch operations
4. **Metadata-enriched embeddings** via decorator pattern for storage optimization
5. **Structured extraction support** for entity and keyword identification
6. **Provider-agnostic design** enabling easy model swapping and A/B testing

This architecture enables MiniRAG to support both Small Language Models for on-device deployment and Large Language Models for cloud-based scenarios, with consistent interfaces throughout the codebase.

For implementation details:
- LLM function implementations: [LLM Interface](#6.1)
- Embedding generation and quantization: [Embedding Functions](#6.2)
- Complete model list and benchmarks: [Supported Models](#6.3)

Sources: [minirag/llm/openai.py:1-267](), [README.md:1-174]()

---

