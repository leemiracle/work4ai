# 08 — `update()` / `delete()` / `delete_all()` / `history()` / `reset()` / `_create_memory()`

> add() 和 search() 是核心,本篇覆盖**剩余的所有写/读方法**。每个方法都不复杂,但有一些容易踩的坑（如 delete_all 的循环保护、update 的 entity cleanup）。

---

## 1. 方法清单

| 方法 | 行号 | 用途 |
|------|------|------|
| `update(memory_id, text, metadata, expiration_date, data)` | L1810-L1862 | 改一条 memory 的内容/元数据 |
| `delete(memory_id)` | L1864-L1883 | 删一条 memory |
| `delete_all(user_id, agent_id, run_id)` | L1885-L1939 | 批量删（按 scope） |
| `history(memory_id)` | L1941-L1954 | 取变更历史 |
| `reset()` | L2119-L... | 全清（含 vector store + SQLite） |
| `_create_memory(data, existing_embeddings, metadata)` | L1956-L1986 | 内部:单条入库（add 内部用） |
| `_create_procedural_memory(messages, metadata, prompt)` | L1988-L2025 | 内部:procedural memory 创建 |
| `_update_memory(memory_id, data, existing_embeddings, metadata)` | L2027-L2087 | 内部:update 实现 |
| `_delete_memory(memory_id, existing_memory)` | L2089-L2117 | 内部:delete 实现 |

---

## 2. `update(memory_id, text, metadata, expiration_date, data)`

```python
def update(
    self,
    memory_id,
    text: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    expiration_date: Any = _UNSET,
    data: Optional[str] = None,
):
    capture_event("mem0.update", ...)

    # data 是 text 的废弃别名（向后兼容）
    if data is not None:
        logger.warning("`data` is deprecated, use `text` instead")
        if text is None:
            text = data

    # 至少要传一个
    if text is None and metadata is None and expiration_date is _UNSET:
        raise ValueError("At least one of text, metadata, or expiration_date must be provided.")

    # 合并 metadata + expiration_date
    update_metadata = deepcopy(metadata) if metadata is not None else None
    if expiration_date is not _UNSET:
        update_metadata = update_metadata or {}
        update_metadata["expiration_date"] = _normalize_expiration_date(expiration_date)
        # 注意:expiration_date=None 表示"清除"（_UNSET 才是"不变"）

    # 如果有新 text,先 embed
    existing_embeddings = {}
    if text is not None:
        existing_embeddings[text] = self.embedding_model.embed(text, "update")

    self._update_memory(memory_id, text, existing_embeddings, update_metadata)
    display_first_run_notice(self, "sync", "update")
    return {"message": "Memory updated successfully!"}
```

### 关键点

| 点 | 说明 |
|----|------|
| `_UNSET` sentinel | 区分"没传"和"传了 None"。`expiration_date=None` = 清除；`_UNSET` = 不变 |
| `data` 废弃别名 | 早期 API 用 `data`,新代码用 `text`。下个 major 会删 |
| `text` 改了才 re-embed | 没传 text 时不调 embed（省 API 调用） |
| 返回固定字符串 | 不返回 memory 对象,只返回 `{"message": "Memory updated successfully!"}` |

---

## 3. `_update_memory()`（内部实现）

```python
def _update_memory(self, memory_id, data, existing_embeddings, metadata=None):
    existing_memory = self.vector_store.get(vector_id=memory_id)
    if existing_memory is None:
        raise ValueError(f"Memory with id {memory_id} not found")

    prev_value = existing_memory.payload.get("data")
    if data is None:
        data = prev_value     # 没 text 更新,沿用旧 text
    if not isinstance(data, str):
        raise ValueError(f"Memory with id {memory_id} does not have text content to update")

    text_changed = (data != prev_value)

    # 合并 metadata:existing + new（剥离 identity keys）
    new_metadata = deepcopy(existing_memory.payload)
    if metadata is not None:
        new_metadata.update(_strip_identity_keys(metadata, existing_memory.payload))

    new_metadata["data"] = data
    new_metadata["hash"] = hashlib.md5(data.encode()).hexdigest()    # ⭐ 重算 hash
    new_metadata["text_lemmatized"] = lemmatize_for_bm25(data)        # ⭐ 重算 lemmatize
    new_metadata["created_at"] = existing_memory.payload.get("created_at")  # 保留创建时间
    new_metadata["updated_at"] = datetime.now(timezone.utc).isoformat()     # 更新更新时间

    # embed（用 cache 或重算）
    if data in existing_embeddings:
        embeddings = existing_embeddings[data]
    else:
        embeddings = self.embedding_model.embed(data, "update")

    self.vector_store.update(vector_id=memory_id, vector=embeddings, payload=new_metadata)

    # 写历史
    self.db.add_history(
        memory_id, prev_value, data, "UPDATE",
        created_at=new_metadata["created_at"],
        updated_at=new_metadata["updated_at"],
        actor_id=new_metadata.get("actor_id"),
        role=new_metadata.get("role"),
    )

    # ⭐ Entity cleanup（仅 text_changed 时）
    session_filters = {k: new_metadata[k] for k in ("user_id", "agent_id", "run_id") if new_metadata.get(k)}
    if text_changed:
        self._remove_memory_from_entity_store(memory_id, session_filters)
        self._link_entities_for_memory(memory_id, data, session_filters)

    return memory_id
```

### Entity cleanup 流程

text 变了 → 1. 先从老 text 关联的 entity 记录里移除该 memory_id（`_remove_memory_from_entity_store`）；2. 再对新 text 抽 entity 并 link（`_link_entities_for_memory`）。

> 如果 text 没变（只改 metadata 或 expiration_date）,跳过 entity cleanup——省 NER + embed 成本。

---

## 4. `delete(memory_id)`

```python
def delete(self, memory_id):
    capture_event("mem0.delete", ...)
    existing_memory = self.vector_store.get(vector_id=memory_id)
    if existing_memory is None:
        raise ValueError(f"Memory with id {memory_id} not found")

    self._delete_memory(memory_id, existing_memory)

    # 检测 decay usage（提示用户升级到 Platform）
    decay_usage_notice = detect_decay_usage_from_delete()
    if decay_usage_notice:
        display_decay_usage_notice(self, "sync", "delete", *decay_usage_notice)
    else:
        display_first_run_notice(self, "sync", "delete")

    return {"message": "Memory deleted successfully!"}
```

极简——预取 existing_memory（用于 _delete_memory 写历史）→ 删 → 显示 notice。

---

## 5. `_delete_memory()`（内部）

```python
def _delete_memory(self, memory_id, existing_memory=None):
    if existing_memory is None:
        existing_memory = self.vector_store.get(vector_id=memory_id)
        if existing_memory is None:
            raise ValueError(f"Memory with id {memory_id} not found")

    prev_value = existing_memory.payload.get("data", "")
    created_at = _normalize_iso_timestamp_to_utc(existing_memory.payload.get("created_at"))
    updated_at = datetime.now(timezone.utc).isoformat()
    payload = existing_memory.payload or {}

    # 提取 session scope filters（用于 entity cleanup）
    session_filters = {k: payload[k] for k in ("user_id", "agent_id", "run_id") if payload.get(k)}

    self.vector_store.delete(vector_id=memory_id)

    # 写历史（event="DELETE", is_deleted=1）
    self.db.add_history(
        memory_id, prev_value, None, "DELETE",
        created_at=created_at,
        updated_at=updated_at,
        actor_id=existing_memory.payload.get("actor_id"),
        role=existing_memory.payload.get("role"),
        is_deleted=1,
    )

    # Entity cleanup
    self._remove_memory_from_entity_store(memory_id, session_filters)

    return memory_id
```

> 跟 update 类似的 entity cleanup——保证 entity store 不留死链。

---

## 6. ⭐ `delete_all()`（含死循环保护）

```python
def delete_all(self, user_id=None, agent_id=None, run_id=None):
    # 验证 + trim
    user_id = _validate_and_trim_entity_id(user_id, "user_id")
    agent_id = _validate_and_trim_entity_id(agent_id, "agent_id")
    run_id = _validate_and_trim_entity_id(run_id, "run_id")

    filters = {}
    if user_id: filters["user_id"] = user_id
    if agent_id: filters["agent_id"] = agent_id
    if run_id: filters["run_id"] = run_id

    if not filters:
        raise ValueError(
            "At least one filter is required to delete all memories. "
            "If you want to delete all memories, use the `reset()` method."
        )

    capture_event("mem0.delete_all", ...)

    deleted_count = 0
    seen_batches = set()       # ⭐ 死循环保护

    while True:
        memories = self.vector_store.list(
            filters=filters, top_k=DELETE_ALL_BATCH_SIZE   # 1000
        )[0]
        if not memories:
            break

        # 防止 list 不前进（vector store bug 或 filters 失效）
        batch_ids = tuple(sorted(str(memory.id) for memory in memories))
        if batch_ids in seen_batches:
            logger.warning("Stopping delete_all after a repeated memory batch")
            break
        seen_batches.add(batch_ids)

        for memory in memories:
            self._delete_memory(memory.id)
        deleted_count += len(memories)

    logger.info(f"Deleted {deleted_count} memories")

    # notice
    decay_usage_notice = detect_decay_usage_from_delete_all(deleted_count)
    ...
    return {"message": "Memories deleted successfully!"}
```

### 关键设计

| 点 | 为什么 |
|----|------|
| `DELETE_ALL_BATCH_SIZE = 1000` | 大部分 vector store `list()` 默认 100 条,会**静默截断**——加大 batch |
| `seen_batches` set | 防死循环：如果某次 list 返回的 ID 集跟之前一样（说明 delete 没生效）,立即退出 |
| 必须 ≥1 filter | 防止误删全库（要用 `reset()` 才能真清空） |
| 逐条 _delete_memory | 因为要写 history + entity cleanup（不能 bulk delete） |

### 性能代价

`delete_all` 是 **O(N)** 的逐条删除（每条 vector delete + SQLite history + entity cleanup）。1 万条 memory 删一次可能 10+ 秒。这是为了**保证 history 和 entity store 一致**——粗放的 bulk delete 会留下 orphan entity link。

---

## 7. `history(memory_id)`

```python
def history(self, memory_id):
    capture_event("mem0.history", ...)
    history = self.db.get_history(memory_id)
    display_first_run_notice(self, "sync", "history")
    return history
```

直接转 SQLiteManager。SQLiteManager.get_history 返回：

```python
[
    {
        "id": "...",
        "memory_id": "...",
        "old_memory": "...",
        "new_memory": "...",
        "event": "ADD" | "UPDATE" | "DELETE",
        "created_at": "...",
        "updated_at": "...",
        "is_deleted": bool,
        "actor_id": "...",
        "role": "user" | "assistant" | "system",
    },
    ...
]
```

按 created_at ASC, updated_at ASC 排序。

---

## 8. `reset()`

```python
def reset(self):
    """
    Reset the memory store by:
        Deletes the vector store collection
        Resets the database
        Recreates the vector store with a new client
    """
    logger.warning("Resetting all memories")

    self.db.reset()       # DROP history + messages 两张表
    self.db.close()

    # 重置 vector store（具体怎么 reset 看 provider 实现）
    self.vector_store = VectorStoreFactory.reset(self.vector_store)

    # 重置 entity_store（下次访问会重新创建）
    self._entity_store = None
    ...
```

> ⚠️ `reset()` 会**清空所有数据**——history、messages、vector、entity。仅在调试时用。生产**绝对不要**。

---

## 9. `_create_memory()`（内部入库 helper）

```python
def _create_memory(self, data, existing_embeddings, metadata=None):
    """被 _add_to_vector_store (Phase 6) 和 _create_procedural_memory 共用"""
    logger.debug(f"Creating memory with {data=}")

    # 用 cache 或现 embed
    if data in existing_embeddings:
        embeddings = existing_embeddings[data]
    else:
        embeddings = self.embedding_model.embed(data, memory_action="add")

    memory_id = str(uuid.uuid4())
    new_metadata = deepcopy(metadata) if metadata is not None else {}
    new_metadata["data"] = data
    new_metadata["hash"] = hashlib.md5(data.encode()).hexdigest()
    if "created_at" not in new_metadata:
        new_metadata["created_at"] = datetime.now(timezone.utc).isoformat()
    new_metadata["updated_at"] = new_metadata["created_at"]
    new_metadata["text_lemmatized"] = lemmatize_for_bm25(data)

    self.vector_store.insert(
        vectors=[embeddings],
        ids=[memory_id],
        payloads=[new_metadata],
    )

    self.db.add_history(
        memory_id, None, data, "ADD",
        created_at=new_metadata.get("created_at"),
        updated_at=new_metadata.get("updated_at"),
        actor_id=new_metadata.get("actor_id"),
        role=new_metadata.get("role"),
    )

    return memory_id
```

> 注意：这个 helper **不做 entity linking**——只入库 + 写历史。entity linking 是 add() 主 pipeline 的 Phase 7。`_create_memory` 用在 procedural memory 和 raw mode（`infer=False`）。

---

## 10. `_create_procedural_memory()`

```python
def _create_procedural_memory(self, messages, metadata=None, prompt=None):
    """procedural memory = agent 的元知识总结"""
    logger.info("Creating procedural memory")

    # 用 PROCEDURAL_MEMORY_SYSTEM_PROMPT（详见 05-prompts.md §6）
    parsed_messages = [
        {"role": "system", "content": prompt or PROCEDURAL_MEMORY_SYSTEM_PROMPT},
        *messages,
        {"role": "user", "content": "Create procedural memory of the above conversation."},
    ]

    try:
        procedural_memory = self.llm.generate_response(messages=parsed_messages)
        procedural_memory = remove_code_blocks(procedural_memory)
    except Exception as e:
        logger.error(f"Error generating procedural memory summary: {e}")
        raise

    if metadata is None:
        raise ValueError("Metadata cannot be done for procedural memory.")

    metadata = {**metadata, "memory_type": MemoryType.PROCEDURAL.value}
    embeddings = self.embedding_model.embed(procedural_memory, memory_action="add")
    memory_id = self._create_memory(
        procedural_memory,
        {procedural_memory: embeddings},
        metadata=metadata,
    )

    capture_event("mem0._create_procedural_memory", ...)
    return {"results": [{"id": memory_id, "memory": procedural_memory, "event": "ADD"}]}
```

### 触发条件

`Memory.add(memory_type="procedural_memory", agent_id="...")` → 走这个分支（不走向量抽取 pipeline）。

### 用例

- browser agent 跑了 N 步操作 → 总结成 procedural memory 供下次复用
- agent 学会了某个工具的调用模式 → 存为 procedural

---

## 11. 各方法对应的 history event

| 方法 | event | old_memory | new_memory | is_deleted |
|------|-------|-----------|-----------|-----------|
| `add` (regular) | `ADD` | None | text | 0 |
| `add` (infer=False) | `ADD` | None | msg_content | 0 |
| `add` (procedural) | `ADD` | None | summary | 0 |
| `update` (text changed) | `UPDATE` | prev | new | 0 |
| `update` (metadata only) | `UPDATE` | prev=text | new=same | 0 |
| `delete` | `DELETE` | prev | None | 1 |

---

## 12. async 版（AsyncMemory）

行号参考 [`02-memory-main.md`](./02-memory-main.md) §7。所有方法基本是 sync 版的 `async def` 镜像。差异：

- `_upsert_entity_async` / `_bulk_clear_entity_store_async` 等 async 专用 helper
- 用 `concurrent.futures.ThreadPoolExecutor` 包 sync LLM/embed 调用（在 async 里阻塞调用）
- AsyncMemory **不继承 Memory**,是独立类（避免 sync 方法被误用）

---

## 13. 错误处理一致性

所有公开方法遵循类似错误模式：

```python
try:
    # 业务逻辑
except ValidationError:
    raise   # 直接抛
except SomeInternalError as e:
    logger.error(...)
    raise
finally:
    display_*_notice(...)  # 即使失败也显示 notice（有些）
```

> 错误类型在 `mem0/exceptions.py`（484 行）定义。详见 [`03-py-sdk-client/03-telemetry.md`](../03-py-sdk-client/03-telemetry.md)（暂未写,先看源码）。

---

## 14. 接下来

| 想看 | 去哪 |
|------|------|
| add() 8 阶段（核心） | [`06-add-pipeline.md`](./06-add-pipeline.md) |
| search() 多信号融合 | [`07-search-pipeline.md`](./07-search-pipeline.md) |
| _strip_identity_keys 等安全 helper | [`02-memory-main.md`](./02-memory-main.md) §3-4 |
| 异常体系 | [`03-py-sdk-client/03-telemetry.md`](../03-py-sdk-client/03-telemetry.md) |

---

📌 **下一步** → [`06-add-pipeline.md`](./06-add-pipeline.md) add() 8 阶段深度剖析。
