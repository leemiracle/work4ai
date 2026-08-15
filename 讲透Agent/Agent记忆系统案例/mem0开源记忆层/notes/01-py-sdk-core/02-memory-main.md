# 02 — `mem0/memory/main.py`（3851 行核心引擎顶层导航）

> 整个 Mem0 最复杂的文件。本篇是"地图",不深入每个方法（那是 06/07/08 的事）,只让你**看完知道每个方法在哪、做什么、怎么找**。

---

## 文件全景（按行号）

| 行号 | 内容 | 详细文档 |
|------|------|---------|
| L1-L82 | imports + 抑制 SWIG warning + logger 初始化 | — |
| L85-L137 | 常量定义（`_RUNTIME_FIELDS`/`_SENSITIVE_FIELDS_EXACT`/`ENTITY_PARAMS` 等） | §3 |
| L143-L251 | 辅助函数：identity 验证、search params 验证、sensitive field 检测 | §4 |
| L254-L298 | `_safe_deepcopy_config` / `_is_sensitive_field`（telemetry 用） | §4 |
| L301-L311 | `_normalize_iso_timestamp_to_utc` | §4 |
| L314-L404 | `_build_filters_and_metadata` ⭐ | §5 |
| L407-L446 | session_scope / entity_collection_name / expiration_date / payload_is_expired | §4 |
| L449-L450 | `setup_config()` 调用（模块级） | — |
| L456-L479 | `_OSSProject` / `_AsyncOSSProject`（占位：OSS 不支持 project.update） | — |
| **L482-L2119** | ⭐ **`class Memory(MemoryBase)`** —— 核心同步实现 | §6 |
| **L2161-L3851** | ⭐ **`class AsyncMemory(MemoryBase)`** —— 异步镜像 | §7 |

---

## 1. import 关系（顶层）

```python
# mem0/memory/main.py 顶部（精简）
from mem0.configs.base import MemoryConfig, MemoryItem
from mem0.configs.enums import MemoryType
from mem0.configs.prompts import (
    ADDITIVE_EXTRACTION_PROMPT,           # ⭐ v3 核心算法
    AGENT_CONTEXT_SUFFIX,
    PROCEDURAL_MEMORY_SYSTEM_PROMPT,
    generate_additive_extraction_prompt,
)
from mem0.exceptions import LLMError, Mem0ValidationError
from mem0.memory.base import MemoryBase
from mem0.memory.notices import (
    PERFORMANCE_SLOW_QUERY_THRESHOLD_SECONDS,
    detect_decay_usage_from_delete, detect_temporal_usage_from_metadata, ...
    display_first_run_notice, display_scale_threshold_notice, ...
    get_decay_feature_error_message, get_temporal_feature_error_message,
)
from mem0.memory.setup import mem0_dir, setup_config
from mem0.memory.storage import SQLiteManager
from mem0.memory.telemetry import MEM0_TELEMETRY, capture_event
from mem0.memory.utils import (
    extract_json, parse_messages, parse_vision_messages,
    process_telemetry_filters, remove_code_blocks,
)
from mem0.utils.entity_extraction import extract_entities, extract_entities_batch
from mem0.utils.factory import (
    EmbedderFactory, LlmFactory, RerankerFactory, VectorStoreFactory,
)
from mem0.utils.lemmatization import lemmatize_for_bm25
from mem0.utils.scoring import (
    ENTITY_BOOST_WEIGHT, get_bm25_params, normalize_bm25, score_and_rank,
)
from mem0.vector_stores.base import VectorStoreBase
```

> 注意：**没有 `from mem0.graphs import ...`** —— April 2026 重构已移除 graph 模块（详见 [`00-overview/02-architecture.md`](../00-overview/02-architecture.md) §2）。

---

## 2. 关键常量（L85-L140）

```python
# 运行时认证对象（不清红）
_RUNTIME_FIELDS = frozenset({"http_auth", "auth", "connection_class", "ssl_context"})

# 已知敏感字段（telemetry 时清空）
_SENSITIVE_FIELDS_EXACT = frozenset({
    "api_key", "secret_key", "private_key", "access_key", "password",
    "credentials", "credential", "secret", "token", "access_token",
    "refresh_token", "auth_token", "session_token", "client_secret",
    "auth_client_secret", "azure_client_secret", "service_account_json",
    "aws_session_token",
})

# 字段名后缀,暗示可能是密钥
_SENSITIVE_SUFFIXES = ("_password", "_secret", "_token", "_credential", "_credentials")

# Entity 参数（必须走 filters,不能顶层 kwarg）
ENTITY_PARAMS = frozenset({"user_id", "agent_id", "run_id"})

DELETE_ALL_BATCH_SIZE = 1000   # delete_all 每批最多删 1000 条

# Identity scope 字段（caller metadata 永远不能设）
_IDENTITY_KEYS = ENTITY_PARAMS | {"actor_id"}
```

---

## 3. 辅助函数（L143-L251）

| 函数 | 用途 |
|------|------|
| `_strip_identity_keys(metadata, existing_payload, *, context)` | 从 caller metadata 移除 identity 字段（防 scope 注入,issue #6655） |
| `_reject_top_level_entity_params(kwargs, method_name)` | search/get_all 拒绝顶层 user_id/agent_id/run_id（必须用 filters） |
| `_validate_and_trim_entity_id(value, name)` | coerce int→str、strip、拒绝空格/空 |
| `_validate_search_params(threshold, top_k)` | threshold ∈ [0,1]、top_k 非负整数 |
| `_validate_and_trim_search_query(query)` | query 非空字符串 |
| `_is_sensitive_field(field_name)` | telemetry 时判断字段是否敏感 |
| `_safe_deepcopy_config(config)` | 安全 deepcopy config（处理非可序列化对象） |

---

## 4. 时间/过期辅助

```python
def _normalize_iso_timestamp_to_utc(timestamp):
    """tz-aware ISO → UTC ISO；naive 透传不重写"""

def _normalize_expiration_date(value):
    """接受 str/date/datetime,统一返回 YYYY-MM-DD"""

def _payload_is_expired(payload):
    """检查 payload.expiration_date < today"""
```

---

## 5. ⭐ `_build_filters_and_metadata`（最关键 helper 之一）

L314-L404,被 `add()` 和 `update()` 共用。流程：

```python
def _build_filters_and_metadata(
    *, user_id, agent_id, run_id, actor_id,
    input_metadata, input_filters,
) -> tuple[Dict, Dict]:
    # 1. 从 input_metadata 里剥离 identity keys（防注入）
    base_metadata_template = _strip_identity_keys(deepcopy(input_metadata), {}, context="add()") if input_metadata else {}
    effective_query_filters = deepcopy(input_filters) if input_filters else {}

    # 2. 验证 + trim 三个 entity id
    user_id = _validate_and_trim_entity_id(user_id, "user_id")
    agent_id = _validate_and_trim_entity_id(agent_id, "agent_id")
    run_id = _validate_and_trim_entity_id(run_id, "run_id")

    # 3. 把 entity id 加进 metadata + filters
    if user_id:
        base_metadata_template["user_id"] = user_id
        effective_query_filters["user_id"] = user_id
        session_ids_provided.append("user_id")
    # ... agent_id, run_id 同

    # 4. 至少要有一个,否则 Mem0ValidationError
    if not session_ids_provided:
        raise Mem0ValidationError(...)

    # 5. 解析 actor_id（query-only,不进 metadata）
    resolved_actor_id = actor_id or effective_query_filters.get("actor_id")
    if resolved_actor_id:
        effective_query_filters["actor_id"] = resolved_actor_id

    return base_metadata_template, effective_query_filters
```

> 这个函数的细节决定了 Mem0 的**多租户隔离**——所有 memory 都 scoped 到 user/agent/run,不能跨 scope 查。

---

## 6. ⭐ `class Memory`（L482-L2119）公开 API 一览

| 方法 | 行号 | 详细文档 |
|------|------|---------|
| `__init__(config)` | L483-L548 | §6.1 |
| `from_config(cls, config_dict)` | L725-L732 | classmethod 入口 |
| `project` (property) | L549-L551 | 返回 `_OSSProject()`（受限） |
| `entity_store` (property) | L553-L575 | ⭐ 懒加载 entity 存储库 |
| ⭐ **`add(messages, ...)`** | L755-L872 | [`06-add-pipeline.md`](./06-add-pipeline.md) |
| ⭐ **`_add_to_vector_store(...)`** | L874-L1201 | 8 阶段 pipeline（add 的实际工作） |
| `get(memory_id)` | L1203-L1249 | [`08-update-delete.md`](./08-update-delete.md) |
| `get_all(*, filters, top_k, show_expired)` | L1250-L1320 | 同上 |
| `_get_all_from_vector_store(...)` | L1321-L1372 | 内部 |
| ⭐ **`search(query, *, top_k, filters, threshold, rerank, explain, ...)`** | L1374-L1518 | [`07-search-pipeline.md`](./07-search-pipeline.md) |
| `_process_metadata_filters(metadata_filters)` | L1519-L1594 | 高级 filter（AND/OR/NOT）处理 |
| `_has_advanced_operators(filters)` | L1596-L1621 | 检测高级 filter |
| `_search_vector_store(query, filters, limit, threshold, explain, show_expired)` | L1623-L1726 | 多信号融合检索 |
| `_compute_entity_boosts(query_entities, filters)` | L1728-L1808 | entity 加权计算 |
| `update(memory_id, text, metadata, expiration_date, data)` | L1810-L1862 | [`08-update-delete.md`](./08-update-delete.md) |
| `delete(memory_id)` | L1864-L1883 | 同上 |
| `delete_all(user_id, agent_id, run_id)` | L1885-L1939 | 同上 |
| `history(memory_id)` | L1941-L1954 | 同上 |
| `reset()` | L2119+ | 同上 |

### 私有 helpers（部分）

| 方法 | 行号 | 用途 |
|------|------|------|
| `_normalize_entity_text(value)` | L577-L579 | "  Foo  BAR " → "foo bar" |
| `_existing_entities_by_text(filters)` | L581-L598 | 查 entity store 返回 normalized_text → row 映射 |
| `_upsert_entity(entity_text, entity_type, memory_id, filters)` | L600-L645 | 单 entity upsert |
| `_remove_memory_from_entity_store(memory_id, filters)` | L647-L700 | 删 memory 时从 entity linked_memory_ids 移除 |
| `_link_entities_for_memory(memory_id, text, filters)` | L702-L723 | 单 memory 的 entity linking |
| `_should_use_agent_memory_extraction(messages, metadata)` | L734+ | 判断用 user 还是 agent extraction |
| `_create_memory(data, existing_embeddings, metadata)` | L1956-L1986 | 单条 memory 入库（被 add 和 procedural 用） |
| `_create_procedural_memory(messages, metadata, prompt)` | L1988-L2025 | procedural memory 创建 |
| `_update_memory(memory_id, data, existing_embeddings, metadata)` | L2027-L2087 | update 内部实现 |
| `_delete_memory(memory_id, existing_memory)` | L2089-L2117 | delete 内部实现 |

### 6.1 `__init__` 详解

```python
def __init__(self, config: MemoryConfig = MemoryConfig()):
    self.config = config

    # 4 个 Factory 创建组件
    self.embedding_model = EmbedderFactory.create(
        config.embedder.provider, config.embedder.config, config.vector_store.config
    )
    self.vector_store = VectorStoreFactory.create(
        config.vector_store.provider, config.vector_store.config
    )
    self.llm = LlmFactory.create(config.llm.provider, config.llm.config)
    self.db = SQLiteManager(config.history_db_path)

    self.collection_name = config.vector_store.config.collection_name
    self.api_version = config.version
    self.custom_instructions = config.custom_instructions

    # 可选 reranker
    self.reranker = None
    if config.reranker:
        self.reranker = RerankerFactory.create(config.reranker.provider, config.reranker.config)

    # entity_store 懒加载（property）
    self._entity_store = None

    # 遥测：如果启用,另建一个 telemetry_vector_store（collection=mem0migrations）
    if MEM0_TELEMETRY:
        telemetry_config_dict = config.vector_store.config.model_dump()
        telemetry_config_dict['collection_name'] = "mem0migrations"
        if config.vector_store.provider in ["faiss", "qdrant"]:
            telemetry_config_dict['path'] = os.path.join(mem0_dir, f"migrations_{config.vector_store.provider}")
            os.makedirs(telemetry_config_dict['path'], exist_ok=True)
        telemetry_config = config.vector_store.config.__class__(**telemetry_config_dict)
        self._telemetry_vector_store = VectorStoreFactory.create(
            config.vector_store.provider, telemetry_config
        )

    # 兼容性警告：vector store 不支持 keyword_search 时降级到 semantic-only
    if getattr(type(self.vector_store), "keyword_search", None) is VectorStoreBase.keyword_search:
        logger.warning(
            "The '%s' vector store does not support keyword search. "
            "Hybrid (BM25) scoring will be disabled and search will use "
            "semantic similarity only. ...",
            config.vector_store.provider,
        )

    capture_event("mem0.init", self, {"sync_type": "sync"})
```

### 6.2 `entity_store` property（懒加载）

```python
@property
def entity_store(self):
    if self._entity_store is None:
        # clone vector_store config,改 collection_name 为 xxx_entities
        entity_config = _safe_deepcopy_config(self.config.vector_store.config)
        entity_collection = _entity_collection_name(
            self.config.vector_store.provider, self.collection_name
        )
        # _entity_collection_name: provider=="s3_vectors" 用 "-",其他用 "_"
        # 例: "mem0" → "mem0_entities"；s3_vectors 时 → "mem0-entities"

        if hasattr(entity_config, 'collection_name'):
            entity_config.collection_name = entity_collection

        # Qdrant 特殊：共享 client 避免 RocksDB lock
        if self.config.vector_store.provider == "qdrant" and hasattr(self.vector_store, "client"):
            if hasattr(entity_config, "client"):
                entity_config.client = self.vector_store.client

        self._entity_store = VectorStoreFactory.create(
            self.config.vector_store.provider, entity_config
        )
    return self._entity_store
```

> **关键设计**：entity_store **复用** vector store provider（同一份数据库连接 / 同一个引擎）,但用独立 collection。Qdrant 内嵌模式下还要**共享 client** 避免 RocksDB 单进程 lock 冲突。

---

## 7. ⭐ `class AsyncMemory`（L2161-L3851）

AsyncMemory 是 Memory 的**异步镜像**,逻辑几乎一致,但有一些异步专用优化：

| Async 专用方法 | 行号 | 用途 |
|--------------|------|------|
| `_upsert_entity_async` | L2258 | async 版单 entity upsert |
| `_bulk_clear_entity_store` | L2308 | 批量清空 entity |
| `_remove_memory_from_entity_store` (async) | L2329 | async 版 cleanup |
| `_link_entities_for_memory` (async) | L2374 | async 版 linking |
| `add` (async) | L2423 | async 版 add |
| `_add_to_vector_store` (async) | L2522 | async 版 8 阶段 pipeline |
| `_search_vector_store` (async) | L3282 | async 版多信号检索 |
| `_compute_entity_boosts_async` | L3385 | async 版 entity boost（含并发 search） |
| ... 其他方法基本是 sync 版的 `async def` 镜像 |

> AsyncMemory 是单独的类（不继承 Memory）。代码重复度高,但为了真正的 async I/O 并发是必要的。详见 [`06-add-pipeline.md`](./06-add-pipeline.md) §10 async 部分。

---

## 8. `_OSSProject` vs Platform `Project`

L456-L479：

```python
_PROJECT_UPDATE_UNSUPPORTED_ERROR = "Project updates are not supported by the OSS Memory SDK."

class _OSSProject:
    def update(self, custom_instructions=None, custom_categories=None, multilingual=None, decay=None):
        if decay is True:
            raise ValueError(get_decay_feature_error_message("sync", "project.update", "decay"))
        raise ValueError(_PROJECT_UPDATE_UNSUPPORTED_ERROR)


class _AsyncOSSProject:
    async def update(self, ...):
        if decay is True:
            raise ValueError(await get_decay_feature_error_message_async("async", "project.update", "decay"))
        raise ValueError(_PROJECT_UPDATE_UNSUPPORTED_ERROR)
```

> Memory 的 `project` property 返回这个 `_OSSProject()`,任何 `m.project.update(...)` 都会报错。这是为了**API 同构**：OSS 和 Hosted 都有 `.project.update()`,但 OSS 永远抛友好错误（"仅 Platform 支持"）。

---

## 9. 阅读路径（建议）

第一次读 `main.py` 的人,按这个顺序：

1. **L482-L575** `Memory.__init__` + `entity_store` property（理解组件装配）
2. **L143-L251** 辅助函数（理解 validation 约束）
3. **L314-L404** `_build_filters_and_metadata`（理解 scope 隔离）
4. **L755-L872** `add()` 入口（理解调用流程）
5. **L874-L1201** `_add_to_vector_store`（8 阶段核心,跳过 Phase 7 子阶段先看大流程）
6. **L1374-L1518** `search()` 入口
7. **L1623-L1726** `_search_vector_store`（多信号融合）
8. **L1810-L2117** `update`/`delete`/`delete_all`/`history`
9. 最后回头看 Phase 7 子阶段（L1081-L1185 entity linking 细节）

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| add() 8 阶段逐阶段 | [`06-add-pipeline.md`](./06-add-pipeline.md) |
| search() 多信号融合 | [`07-search-pipeline.md`](./07-search-pipeline.md) |
| update/delete/delete_all/history/reset | [`08-update-delete.md`](./08-update-delete.md) |
| Factory 工厂模式 | [`02-py-sdk-providers/07-factory.md`](../02-py-sdk-providers/07-factory.md) |

---

📌 **下一步** → [`06-add-pipeline.md`](./06-add-pipeline.md) add() 全链路 8 阶段精读。
