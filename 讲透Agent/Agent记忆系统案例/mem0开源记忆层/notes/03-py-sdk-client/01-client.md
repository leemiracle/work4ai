# 01 — `MemoryClient` / `AsyncMemoryClient`（Hosted Platform Client）

> Hosted 模式的入口。所有方法都是 HTTP wrapper,把请求发到 `https://api.mem0.ai`。
> 跟 `Memory` API 表面同构,但实际不跑算法,只调 REST API。

---

## 1. 文件结构

```
mem0/client/
├── main.py        # ⭐ MemoryClient + AsyncMemoryClient (1838 行)
├── project.py     # BaseProject + Project + AsyncProject（项目管理）
├── types.py       # Options Pydantic 模型（AddMemoryOptions 等）
└── utils.py       # api_error_handler 装饰器
```

---

## 2. `MemoryClient` 方法清单

| 方法 | 用途 | OSS Memory 对应 |
|------|------|---------------|
| `add(messages, options, **kwargs)` | 添加 memory | `Memory.add()` |
| `get(memory_id)` | 取单条 | `Memory.get()` |
| `get_all(options, **kwargs)` | 列出 | `Memory.get_all()` |
| `search(query, options, **kwargs)` | 搜索 | `Memory.search()` |
| `update(memory_id, text, ...)` | 更新 | `Memory.update()` |
| `delete(memory_id, delete_linked=False)` | 删单条 | `Memory.delete()` |
| `delete_all(options, **kwargs)` | 批量删 | `Memory.delete_all()` |
| `history(memory_id)` | 变更历史 | `Memory.history()` |
| `reset()` | 清空 | `Memory.reset()` |
| **`users()`** ⭐ | 列用户 | ❌（OSS 无） |
| **`delete_users(...)`** ⭐ | 删用户 | ❌ |
| **`batch_update(memories)`** ⭐ | 批量改 | ❌ |
| **`batch_delete(memories)`** ⭐ | 批量删 | ❌ |
| **`create_memory_export(schema, ...)`** ⭐ | 创建导出任务 | ❌ |
| **`get_memory_export(...)`** ⭐ | 拿导出 | ❌ |
| **`get_summary(filters)`** ⭐ | 摘要 | ❌ |
| **`get_project(fields)`** ⭐ | 拿项目信息 | `Memory.project`（OSS 受限） |
| **`update_project(...)`** ⭐ | 改项目（含 decay/temporal） | ❌ |
| **`chat()`** ⭐ | OpenAI 兼容 chat | ❌ |
| **`get_webhooks/create_webhook/...`** ⭐ | webhook 管理 | ❌ |
| **`feedback(...)`** ⭐ | 反馈 | ❌ |

> **⭐** 是 Platform 独有（OSS 没对应）。这是双模式"功能差异"的真相。

---

## 3. `__init__`

```python
class MemoryClient:
    def __init__(self, api_key=None, host=None, client=None):
        self.api_key = api_key or os.getenv("MEM0_API_KEY")
        self.host = host or "https://api.mem0.ai"
        self.org_id = None
        self.project_id = None
        self.user_id = get_user_id()    # 本地 anon ID（telemetry 用）

        if not self.api_key:
            raise ValueError("Mem0 API key is required")

        # httpx client,enable cookies + retry
        self.client = client or httpx.Client(
            base_url=self.host,
            headers={"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"},
            timeout=60.0,
        )

        # 验证 + 拿 org_id/project_id
        self._validate_api_key()

        # 把 anon ID 合并到 email（如果用户登录了）
        _maybe_alias_anon_to_email(...)
```

### 关键点

- 默认 host `https://api.mem0.ai`,可改 `host=` 接自托管 server
- 默认 60 秒 timeout
- `client=` 可传自定义 httpx.Client（高级用法,如代理）
- API key 用 `Token <key>` header（不是 `Bearer`）

---

## 4. ⭐ `add()` 示例

```python
@api_error_handler
def add(self, messages, options: Optional[AddMemoryOptions] = None, **kwargs) -> Dict[str, Any]:
    """Add memories.

    Identity fields (user_id, agent_id, app_id, run_id) must be passed inside
    the ``filters`` dict — the v3 API does not accept them at the top level.
    """
    payload = self._prepare_payload(messages, kwargs)
    if options:
        # Options 是 Pydantic model,只取非 None 字段
        options_dict = options.model_dump(exclude_none=True, exclude_unset=True)
        payload.update(options_dict)

    # ⭐ 不在顶层传 user_id/agent_id/run_id/app_id,API 会拒
    return self.client.post("/memories/", json=payload).json()
```

### 用法

```python
from mem0 import MemoryClient
from mem0.client.types import AddMemoryOptions

m = MemoryClient(api_key="...")
result = m.add(
    "I prefer dark mode",
    options=AddMemoryOptions(
        filters={"user_id": "alice"},   # ⭐ 必须在 filters 里
        metadata={"source": "chat"},
        expires_in_days=30,
    ),
)
```

> **重要变化**：v3 API 要求 `user_id`/`agent_id`/`app_id`/`run_id` 在 `filters` 里,不接受顶层。`Memory` OSS 仍接受顶层,但 `MemoryClient` 强制 filters。

---

## 5. `Options` 类型（types.py）

```python
class AddMemoryOptions(BaseModel):
    filters: Optional[Dict[str, Any]]          # 必须含 user_id 等
    metadata: Optional[Dict[str, Any]]
    infer: Optional[bool]
    custom_categories: Optional[List[Dict]]
    custom_instructions: Optional[str]
    agent_custom_instructions: Optional[str]
    timestamp: Optional[int]                   # Unix timestamp
    expiration_date: Optional[str]             # YYYY-MM-DD
    structured_data_schema: Optional[Dict]     # 结构化抽取


class SearchMemoryOptions(BaseModel):
    filters: Optional[Dict]
    metadata: Optional[Dict]
    top_k: Optional[int]
    rerank: Optional[bool]
    threshold: Optional[float]
    fields: Optional[List[str]]                # 字段投影
    categories: Optional[List[str]]            # 分类过滤
    show_expired: Optional[bool]
    reference_date: Optional[Union[str, int]]  # ⭐ Platform-only
    latest_only: Optional[bool]
    keyword_search: Optional[bool]
```

> Options 类提供 IDE 自动补全 + runtime 验证。也支持直接 `**kwargs`（向后兼容）。

---

## 6. `api_error_handler` 装饰器

`client/utils.py`：

```python
def api_error_handler(func):
    """Supports both sync and async functions."""
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                _handle_http_error(e)
                raise
            except httpx.RequestError as e:
                _handle_request_error(e)
                raise
        return async_wrapper
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                _handle_http_error(e)
                raise
            except httpx.RequestError as e:
                _handle_request_error(e)
                raise
        return wrapper
```

### 错误转换

| httpx 错误 | 转 mem0 异常 |
|----------|----------|
| `HTTPStatusError` 429 | `RateLimitError`（带 `Retry-After`） |
| `HTTPStatusError` 4xx | `ClientError` / `ValidationError` / `AuthenticationError` |
| `HTTPStatusError` 5xx | `ServerError` |
| `TimeoutException` | `NetworkError(NET_TIMEOUT)` |
| `ConnectError` | `NetworkError(NET_CONNECT)` |
| 其他 `RequestError` | `NetworkError(NET_GENERIC)` |

---

## 7. Platform 独有功能（OSS 没有的）

| 功能 | 怎么用 | 业务价值 |
|------|-------|---------|
| **多用户管理** | `users()` / `delete_users(ids)` | SaaS 应用 |
| **批量操作** | `batch_update(memories)` / `batch_delete(memories)` ⭐ | 数据迁移、维护 |
| **导出** | `create_memory_export(schema)` → `get_memory_export` | 数据导出/备份 |
| **摘要** | `get_summary(filters)` | dashboard |
| **项目管理** | `get_project` / `update_project` | 多项目组织 |
| **Decay** | `update_project(decay=True)` | 旧 memory 自动衰减 |
| **Temporal** | `add(timestamp=...)` `search(reference_date=...)` | 时间感知检索 |
| **Webhooks** | `create_webhook(event_types=["memory.added"])` | 事件订阅 |
| **Feedback** | `feedback(memory_id, score)` | RLHF / 数据改进 |
| **Chat** | `m.chat.create(model="gpt-5-mini", messages=...)` | OpenAI 兼容 |

### 7.1 ⭐ Batch Operations 详解（DeepWiki 11.5）

`batch_update` 和 `batch_delete` 是 Platform 独有的批量操作,把 N 次单请求压成 1 次。

#### API 签名

```python
# Python（sync + async 都有）
m.batch_update(memories: List[Dict]) -> Dict
m.batch_delete(memories: List[Dict]) -> Dict

# TS
m.batchUpdate(memories: MemoryUpdateBody[]) => Promise<...>
m.batchDelete(memories: ...) => Promise<...>
```

#### Memory 对象结构（batch_update）

```python
[
    {"memory_id": "id1", "text": "new text 1"},        # 改 text
    {"memory_id": "id2", "metadata": {"updated": True}},  # 改 metadata
    {"memory_id": "id3", "text": "...", "metadata": {...}},  # 都改
]
```

#### 关键特性

| 特性 | 说明 |
|------|------|
| **Platform Only** | OSS `Memory` 类没有这方法 |
| **单请求** | 把 list wrap 到 `memories` key 一次 POST `{"memories": [...]}` |
| **TS camelCase 自动转换** | `memoryId` → `memory_id`（[mem0-ts/src/client/utils.ts L36](https://github.com/mem0ai/mem0/blob/main/mem0-ts/src/client/utils.ts)） |
| **不保证原子性** | 部分失败不回滚,要看 response 里每条的 status |
| **错误码** | 400 → `ValidationError` / 401 → `AuthenticationError` / 404 → `MemoryNotFoundError` |
| **遥测** | 成功后 fire `client.batch_update` 事件 |

#### 何时用 batch

| 场景 | 推荐 |
|------|------|
| Bulk cleanup（删一批过期 memory） | ✅ batch_delete |
| Session migration（改一批 metadata） | ✅ batch_update |
| 高延迟环境（RTT > 200ms） | ✅ 任何 batch |
| 需要原子性（全成功或全失败） | ❌ 不要用 batch（不保证） |
| 单条操作 | ❌ 用普通 update/delete |

#### 性能对比

| 方式 | 100 条 memory 操作 | 网络请求 |
|------|----------------|--------|
| 循环单条 | 100 次 RTT | 100 |
| Batch | 1 次 RTT | **1** |
| Async 单条并发（asyncio.gather） | max(100 个 RTT) | 100 |

> Batch 在弱网环境收益最大（N×RTT → 1×RTT）。低延迟内网下,async 并发可能更快（不阻塞）。

---

## 8. `AsyncMemoryClient`

```python
class AsyncMemoryClient:
    """异步版,所有方法 async def,用 httpx.AsyncClient"""

    def __init__(self, api_key=None, host=None, client=None):
        # ...
        self.client = client or httpx.AsyncClient(
            base_url=self.host,
            headers={"Authorization": f"Token {self.api_key}"},
            timeout=60.0,
        )

    async def add(self, messages, options=None, **kwargs):
        # 完全镜像 sync 版,只是 await
        ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
```

> AsyncMemoryClient 支持 `async with`（自动 close connection）。

---

## 9. 用法对比 OSS

```python
# === OSS ===
from mem0 import Memory
m = Memory()
m.add("hello", user_id="u1")                          # ⭐ 顶层 user_id OK
results = m.search("hello", filters={"user_id": "u1"})  # 必须 filters

# === Hosted ===
from mem0 import MemoryClient
m = MemoryClient(api_key="...")
m.add("hello", filters={"user_id": "u1"})             # ⭐ 必须 filters
results = m.search("hello", filters={"user_id": "u1"})

# === Async Hosted ===
from mem0 import AsyncMemoryClient
async with AsyncMemoryClient(api_key="...") as m:
    await m.add("hello", filters={"user_id": "u1"})
    results = await m.search("hello", filters={"user_id": "u1"})
```

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| 双模式对比 | [`../00-overview/05-two-modes.md`](../00-overview/05-two-modes.md) |
| Chat 兼容 OpenAI 接口 | [`02-proxy.md`](./02-proxy.md) |
| Telemetry 隐私 | [`03-telemetry.md`](./03-telemetry.md) |

---

📌 **下一步** → [`02-proxy.md`](./02-proxy.md) HTTP 代理 + OpenAI 兼容 chat。
