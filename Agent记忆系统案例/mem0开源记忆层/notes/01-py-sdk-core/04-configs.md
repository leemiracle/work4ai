# 04 — 配置系统（`mem0/configs/`）

> 整个 Mem0 的配置层。Pydantic v2 模型,层级清晰,所有可调参数都在这里。

---

## 1. `configs/` 目录结构

```
mem0/configs/
├── base.py              # ⭐ 顶层 MemoryConfig + MemoryItem + AzureConfig
├── enums.py             # MemoryType (SEMANTIC/EPISODIC/PROCEDURAL)
├── prompts.py           # ⭐ 1062 行 prompt 模板（详见 05-prompts.md）
├── embeddings/
│   ├── base.py          # BaseEmbedderConfig
│   └── configs.py       # EmbedderConfig（统一入口）
├── llms/
│   ├── base.py          # BaseLlmConfig + 子配置（Anthropic/OpenAI/...）
│   ├── configs.py       # LlmConfig
│   ├── openai.py
│   ├── anthropic.py
│   └── ...
├── vector_stores/
│   ├── base.py          # BaseVectorStoreConfig
│   ├── configs.py       # VectorStoreConfig
│   └── ...
└── rerankers/
    ├── base.py
    ├── config.py        # RerankerConfig
    └── ...
```

---

## 2. ⭐ `MemoryConfig`（顶层配置容器）

`mem0/configs/base.py` L29-L57：

```python
class MemoryConfig(BaseModel):
    vector_store: VectorStoreConfig = Field(
        description="Configuration for the vector store",
        default_factory=VectorStoreConfig,
    )
    llm: LlmConfig = Field(
        description="Configuration for the language model",
        default_factory=LlmConfig,
    )
    embedder: EmbedderConfig = Field(
        description="Configuration for the embedding model",
        default_factory=EmbedderConfig,
    )
    history_db_path: str = Field(
        description="Path to the history database",
        default=os.path.join(mem0_dir, "history.db"),
    )
    reranker: Optional[RerankerConfig] = Field(
        description="Configuration for the reranker",
        default=None,
    )
    version: str = Field(
        description="The version of the API",
        default="v1.1",   # ⭐ 算法版本,非 endpoint 版本
    )
    custom_instructions: Optional[str] = Field(
        description="Custom instructions for fact extraction",
        default=None,
    )
```

### 7 个字段

| 字段 | 类型 | 默认 | 用途 |
|------|------|------|------|
| `vector_store` | `VectorStoreConfig` | qdrant local | 向量存储 |
| `llm` | `LlmConfig` | openai gpt-5-mini | LLM provider |
| `embedder` | `EmbedderConfig` | openai text-embedding-3-small | 嵌入模型 |
| `history_db_path` | `str` | `~/.mem0/history.db` | SQLite 路径 |
| `reranker` | `Optional[RerankerConfig]` | None | 可选重排器 |
| `version` | `str` | `"v1.1"` | 算法版本（影响返回格式） |
| `custom_instructions` | `Optional[str]` | None | fact extraction 自定义指令 |

### 使用示例

```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import AnthropicConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig

config = MemoryConfig(
    llm=AnthropicConfig(model="claude-3-5-sonnet", api_key="..."),
    embedder=EmbedderConfig(model="text-embedding-3-large"),
    vector_store=VectorStoreConfig(provider="qdrant", host="localhost", port=6333),
    version="v1.1",
    custom_instructions="Focus on extracting only dietary preferences",
)
m = Memory(config=config)
```

---

## 3. ⭐ `MemoryItem`（Pydantic 数据模型）

`mem0/configs/base.py` L16-L26：

```python
class MemoryItem(BaseModel):
    id: str = Field(..., description="The unique identifier for the text data")
    memory: str = Field(..., description="The memory deduced from the text data")
    hash: Optional[str] = Field(None, description="The hash of the memory")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the text data")
    score: Optional[float] = Field(None, description="The score associated with the text data")
    created_at: Optional[str] = Field(None, description="The timestamp when the memory was created")
    updated_at: Optional[str] = Field(None, description="The timestamp when the memory was updated")
```

7 个字段——**这是 API 返回给用户的 memory 标准格式**。`get()`/`get_all()`/`search()` 返回的字段都按这个 schema。

> 注意：实际 vector store 里 payload 含的字段更多（`data`/`hash`/`text_lemmatized`/`attributed_to`/`expiration_date`/`user_id` 等）,但**对外暴露时按 `MemoryItem` + selected promoted_keys**（见 `Memory.get()` L1219-L1248 的字段映射逻辑）。

---

## 4. `MemoryType` 枚举

`mem0/configs/enums.py`（完整 7 行）：

```python
from enum import Enum

class MemoryType(Enum):
    SEMANTIC = "semantic_memory"      # 事实性记忆（"User is 25 years old"）
    EPISODIC = "episodic_memory"      # 事件性记忆（"User went to Paris last week"）
    PROCEDURAL = "procedural_memory"  # 过程性记忆（"Agent should always ask for budget first"）
```

> 认知科学三分类。但当前 `Memory.add()` **只显式处理 `PROCEDURAL`**（`memory_type=MemoryType.PROCEDURAL.value`）——其他两类靠 LLM 自然抽取。

---

## 5. `AzureConfig`（遗留）

`mem0/configs/base.py` L60-L81：

```python
class AzureConfig(BaseModel):
    api_key: str = Field(default=None)
    azure_deployment: str = Field(default=None)
    azure_endpoint: str = Field(default=None)
    api_version: str = Field(default=None)
    default_headers: Optional[Dict[str, str]] = Field(default=None)
```

> 单独存在的 Azure 配置（**不在 `MemoryConfig` 里**）。可能为兼容老代码保留,新代码用 `mem0/configs/llms/azure.py` 里的 `AzureOpenAIConfig`。

---

## 6. Provider 配置层级（以 LLM 为例）

```
mem0/configs/llms/
├── base.py            # BaseLlmConfig（基类,所有 provider 共享字段）
├── configs.py         # LlmConfig = BaseLlmConfig 的别名（保持兼容）
├── openai.py          # OpenAIConfig
├── anthropic.py       # AnthropicConfig
├── azure.py           # AzureOpenAIConfig
└── ...
```

### `BaseLlmConfig`（推断的字段）

虽然没直接读,但通过 `factory.py` L97-L106 能推出共享字段：

```python
{
    "model": str,
    "temperature": float,
    "api_key": str,
    "max_tokens": int,
    "top_p": float,
    "top_k": int,
    "enable_vision": bool,
    "vision_details": Any,
    "http_client_proxies": Any,
    "reasoning_effort": Optional[str],   # 仅某些 provider（OpenAI o1/o3）
    "is_reasoning_model": Optional[bool],
}
```

provider-specific config 类（如 `AnthropicConfig`）在 `BaseLlmConfig` 上加自有字段。

---

## 7. `LlmFactory` 的配置转换逻辑

`mem0/utils/factory.py` L93-L123 处理三种 config 输入：

```python
if config is None:
    config = config_class(**kwargs)
elif isinstance(config, dict):
    config = config_class(**{**config, **kwargs})
elif isinstance(config, BaseLlmConfig):
    if config_class != BaseLlmConfig:
        # 把 base config 转 provider-specific
        config_dict = {
            "model": config.model,
            "temperature": config.temperature,
            # ... 8 个标准字段
        }
        # 只在 provider config 接受 reasoning 字段时才转发
        params = inspect.signature(config_class).parameters
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in params.values())
        if accepts_kwargs or "reasoning_effort" in params:
            config_dict["reasoning_effort"] = config.reasoning_effort
        # ...
        config = config_class(**config_dict)
```

> **关键设计**：用 `inspect.signature` 动态检查 provider config 是否接受 `reasoning_effort`/`is_reasoning_model`,只对接收的 provider 转发——避免 OpenAI o1 字段污染 Anthropic 等不支持 reasoning 的 provider。

---

## 8. 全局路径变量

`mem0/configs/base.py` L11-L13：

```python
home_dir = os.path.expanduser("~")
mem0_dir = os.environ.get("MEM0_DIR") or os.path.join(home_dir, ".mem0")
```

`mem0_dir` 在模块顶部定义,**全 SDK 共享**：

| 用途 | 路径 |
|------|------|
| `history.db` | `{mem0_dir}/history.db` |
| `config.json` | `{mem0_dir}/config.json` |
| telemetry migrations | `{mem0_dir}/migrations_qdrant/` |

可通过 `MEM0_DIR=/path env` 覆盖。

---

## 9. Pydantic v2 用法（快速回顾）

Mem0 全面用 Pydantic v2 语法：

| Pydantic v1 | Pydantic v2（Mem0 用） |
|------------|---------------------|
| `class Cfg(BaseModel): x: int = 5` | 同 |
| `class Config: ...` | `model_config = ConfigDict(...)` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `validator(...)` | `field_validator(...)` |
| `Field(...)` | 同 |

> 如果你看 `.dict()` / `.json()` 出现在代码里,说明是 Pydantic v1 残留（可能 bug）。Mem0 已全面 v2 化。

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| Prompt 系统详解 | [`05-prompts.md`](./05-prompts.md) |
| LLM provider 配置类 | [`02-py-sdk-providers/02-llms.md`](../02-py-sdk-providers/02-llms.md) |
| Memory 类怎么用 config | [`02-memory-main.md`](./02-memory-main.md) |

---

📌 **下一步** → [`05-prompts.md`](./05-prompts.md) 1062 行 prompt 模板系统。
