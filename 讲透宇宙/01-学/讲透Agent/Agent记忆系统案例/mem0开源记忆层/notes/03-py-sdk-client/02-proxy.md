# 02 — HTTP 代理与 OpenAI 兼容 chat 接口

> `mem0/proxy/main.py` 提供一个**高级封装**：让 Mem0 像OpenAI 一样用——同一份代码,既能跑 OSS Memory,也能跑 Hosted Client,且对外暴露 `chat.completions.create()` 接口。

---

## 1. 文件全景

```python
# mem0/proxy/main.py（精简）
import mem0
import litellm   # ⭐ 自动装
from mem0 import Memory, MemoryClient
from mem0.configs.prompts import MEMORY_ANSWER_PROMPT


class Mem0:
    """统一入口：根据参数自动选 Memory 或 MemoryClient"""
    def __init__(self, config=None, api_key=None, host=None):
        if api_key:
            self.mem0_client = MemoryClient(api_key, host)        # Hosted
        else:
            self.mem0_client = Memory.from_config(config) if config else Memory()  # OSS
        self.chat = Chat(self.mem0_client)


class Chat:
    def __init__(self, mem0_client):
        self.completions = Completions(mem0_client)


class Completions:
    def __init__(self, mem0_client):
        self.mem0_client = mem0_client

    def create(
        self, model, messages,
        # Mem0 参数
        user_id=None, agent_id=None, run_id=None, metadata=None,
        filters=None, top_k=10,
        # LLM 参数（litellm 全套）
        temperature=None, max_tokens=None, tools=None, ...
    ):
        ...
```

> 设计模仿 OpenAI SDK 的 `client.chat.completions.create()`,但加了 memory 参数。

---

## 2. ⭐ `Mem0` 类：自动选 OSS vs Hosted

```python
class Mem0:
    def __init__(self, config=None, api_key=None, host=None):
        if api_key:
            self.mem0_client = MemoryClient(api_key, host)
        else:
            self.mem0_client = Memory.from_config(config) if config else Memory()

        self.chat = Chat(self.mem0_client)
```

| 参数 | 选谁 |
|------|------|
| `api_key="..."` | Hosted `MemoryClient` |
| `config=MemoryConfig(...)` | OSS `Memory(config)` |
| 都不传 | OSS `Memory()` 用默认 |

> 同一份应用代码,改 init 参数就切换 OSS/Hosted,完全透明。

---

## 3. ⭐ `Completions.create` 流程

```python
def create(self, model, messages, user_id=None, agent_id=None, run_id=None,
           metadata=None, filters=None, top_k=10, ...LLM 参数):
    if not any([user_id, agent_id, run_id]):
        raise ValueError("One of user_id, agent_id, run_id must be provided")

    # ⭐ litellm 检测 model 是否支持 function calling
    if not litellm.supports_function_calling(model):
        raise ValueError(f"Model '{model}' does not support function calling.")

    # Step 1: 准备 messages（注入 system prompt）
    prepared_messages = self._prepare_messages(messages)

    # Step 2: 如果最后一条是 user message
    if prepared_messages[-1]["role"] == "user":
        # 2a: 异步加 memory（不阻塞响应）
        self._async_add_to_memory(messages, user_id, agent_id, run_id, metadata, filters)

        # 2b: 同步搜相关 memory
        relevant_memories = self._fetch_relevant_memories(
            messages, user_id, agent_id, run_id, filters, top_k
        )
        # 2c: 把 memory 注入最后一条 user message
        prepared_messages[-1]["content"] = self._format_query_with_memories(
            messages, relevant_memories
        )

    # Step 3: 调 litellm.completion（支持所有 OpenAI 兼容 model）
    response = litellm.completion(
        model=model, messages=prepared_messages,
        temperature=temperature, max_tokens=max_tokens,
        tools=tools, ...
    )

    capture_event("mem0.chat.create", self.mem0_client)
    return response
```

### 关键设计

| 设计 | 为什么 |
|------|------|
| 异步 add（threading.Thread） | 不阻塞 chat 响应,memory 慢慢存 |
| 同步 search | 必须,因为要把结果注入 query |
| litellm 中间层 | 100+ LLM provider 一个 API |
| 注入最后一条 user message | 不污染 system / 历史 |

---

## 4. `_fetch_relevant_memories`（取最近 6 条）

```python
def _fetch_relevant_memories(self, messages, user_id, agent_id, run_id, filters, top_k):
    # ⭐ 只取最后 6 条作为 search query（防爆 token）
    message_input = [f"{message['role']}: {message['content']}" for message in messages][-6:]
    return self.mem0_client.search(
        query="\n".join(message_input),
        user_id=user_id, agent_id=agent_id, run_id=run_id,
        filters=filters, top_k=top_k,
    )
```

> 只取最后 6 条——避免长 conversation 把 search query 撑爆。

---

## 5. `_format_query_with_memories`（注入 memory）

```python
def _format_query_with_memories(self, messages, relevant_memories):
    entities = []
    if isinstance(self.mem0_client, mem0.memory.main.Memory):
        # OSS 返回 {"results": [...], "relations": [...]}
        memories_text = "\n".join(memory["memory"] for memory in relevant_memories["results"])
        if relevant_memories.get("relations"):
            entities = [entity for entity in relevant_memories["relations"]]
    elif isinstance(self.mem0_client, mem0.client.main.MemoryClient):
        # Hosted 返回 [...]
        memories_text = "\n".join(memory["memory"] for memory in relevant_memories)

    return (
        f"- Relevant Memories/Facts: {memories_text}\n\n"
        f"- Entities: {entities}\n\n"
        f"- User Question: {messages[-1]['content']}"
    )
```

### 注入格式

```
- Relevant Memories/Facts: User likes dark mode. User is a software engineer.

- Entities: ['OpenAI', 'Python']

- User Question: What IDE should I use?
```

LLM 看到这个,会基于 memory 给出"基于偏好的回答"。

---

## 6. `_async_add_to_memory`（异步存 memory）

```python
def _async_add_to_memory(self, messages, user_id, agent_id, run_id, metadata, filters):
    def add_task():
        logger.debug("Adding to memory asynchronously")
        self.mem0_client.add(
            messages=messages,
            user_id=user_id, agent_id=agent_id, run_id=run_id,
            metadata=metadata, filters=filters,
        )

    threading.Thread(target=add_task, daemon=True).start()
```

> 用 threading.Thread（不是 asyncio）是因为 `Memory.add()` 是 sync。daemon=True 让进程退出时不用等。

---

## 7. litellm 自动安装

```python
# mem0/proxy/main.py
try:
    import litellm
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "litellm"])
        import litellm
    except subprocess.CalledProcessError:
        print("Failed to install 'litellm'. Please install it manually using 'pip install litellm'.")
        sys.exit(1)
```

> 第一次 import 失败时自动 `pip install litellm`——无缝用户体验。这是少数 Mem0 自动装依赖的地方（其他都要手动 `pip install mem0ai[extras]`）。

---

## 8. 用法示例

### 简单 chat（OSS）

```python
from mem0.proxy import Mem0

m = Mem0()  # 默认 OSS Memory
response = m.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Hi, I'm Alice"}],
    user_id="alice",
)
print(response.choices[0].message.content)
# "Hi Alice! ..."
```

### Chat（Hosted）

```python
from mem0.proxy import Mem0

m = Mem0(api_key="...")
response = m.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Hi, I'm Alice"}],
    user_id="alice",
    top_k=5,
)
```

### 带 tools

```python
tools = [
    {"type": "function", "function": {"name": "get_weather", "parameters": {...}}}
]
response = m.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    user_id="alice",
    tools=tools,
)
```

---

## 9. Proxy vs 直接用 Memory + LLM

| 维度 | 直接用 Memory + OpenAI | 用 Mem0 proxy |
|------|---------------------|--------------|
| 控制力 | 完全自定义 prompt | 注入格式固定 |
| 多 provider | 自己写 | litellm 100+ provider |
| 自动 add | 自己实现 | 内置 |
| Tools | 自己实现 | litellm 内置 |
| 学习曲线 | 中 | 低 |
| 性能 | 灵活 | 固定模式 |

> Proxy 适合**快速原型 / 简单 chat 应用**。生产复杂场景建议直接用 Memory + 自己控 prompt。

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| MemoryClient HTTP | [`01-client.md`](./01-client.md) |
| Telemetry 隐私 | [`03-telemetry.md`](./03-telemetry.md) |
| OpenAI 兼容怎么实现 | litellm 文档 https://docs.litellm.ai |

---

📌 **下一步** → [`03-telemetry.md`](./03-telemetry.md) 遥测与隐私。
