# 05 — Graph Memory 三层状态澄清

> ⚠️ Graph memory 在 mem0ai/mem0 仓库有**复杂的三层状态**——很多人（包括旧版 AGENTS.md）混淆。本篇基于 [DeepWiki 4.1](https://deepwiki.com/mem0ai/mem0/4.1-graph-memory-overview) + 源码实测,精确说明。
>
> **TL;DR**：
> - **Mem0 Platform（hosted）**：Graph memory **native built-in**,无需 Neo4j
> - **OSS `mem0/memory/main.py`**：**不再 import** 任何 `mem0.graphs.*` 独立模块（main pipeline 移除）
> - **OSS utility 函数**：仍保留 `format_entities` / `sanitize_relationship_for_cypher` 等 legacy helper（向后兼容）
> - **OSS 替代方案**：基于 vector store 的 `entity_store`（复用同 provider,独立 collection）

---

## 1. 验证：graph 模块确实已删

```bash
$ ls mem0/graphs/
ls: 无法访问 'mem0/graphs/': 没有那个文件或目录

$ grep -rn "from mem0.graphs" mem0/
# (空)

$ grep -rn "neo4j\|memgraph\|kuzu" mem0/ --include='*.py'
mem0/exceptions.py:396:    details={"package": "kuzu", "feature": "graph_store"},
mem0/exceptions.py:397:    suggestion="Please install the required dependencies: pip install kuzu"
```

`mem0/exceptions.py` 还保留了 kuzu 的错误提示（可能 procedural 用）,但**没有 import graph 模块**。

`pyproject.toml` 也没有任何 graph 依赖。

---

## 2. 旧设计 vs 新设计

| 旧（v1.0） | 新（v1.1+ April 2026） |
|-----------|----------------------|
| `mem0/graphs/` 独立模块 | 不存在 |
| `MemoryConfig.graph = GraphConfig(...)` | `MemoryConfig.graph` 字段已删 |
| Neo4j/Memgraph/Kuzu/Apache AGE 4 provider | 无独立 graph provider |
| 复杂 Cypher 查询 | 简化 |
| Graph + Vector 双存储 | **复用 vector store**（用独立 collection） |

---

## 3. ⭐ 新设计：`entity_store`（基于 vector store）

`Memory` 类有个 property `entity_store`（详见 [`01-py-sdk-core/02-memory-main.md`](../01-py-sdk-core/02-memory-main.md) §6.2）:

```python
@property
def entity_store(self):
    """懒加载。复用 vector store provider,但用独立 collection。"""
    if self._entity_store is None:
        entity_config = _safe_deepcopy_config(self.config.vector_store.config)
        entity_collection = _entity_collection_name(
            self.config.vector_store.provider, self.collection_name
        )
        # _entity_collection_name:
        #   provider == "s3_vectors" → f"{collection_name}-entities"
        #   其他                     → f"{collection_name}_entities"
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

### 关键设计

| 设计 | 实现 |
|------|------|
| 复用 vector store | 同一 provider（如都是 qdrant） |
| 独立 collection | 命名后缀 `_entities`（s3_vectors 用 `-entities`） |
| 共享 client（Qdrant） | 避免 RocksDB 单进程 lock 冲突 |
| 懒加载 | 不用 entity 的用户零成本 |

### entity_store 的数据结构

每个 entity 是一个 vector 记录:

```python
{
    "id": "uuid",                           # entity ID
    "vector": [...],                        # entity 文本的 embedding
    "payload": {
        "data": "OpenAI",                   # entity 文本
        "entity_type": "ORG",               # spaCy NER 类型
        "linked_memory_ids": ["uuid1", "uuid2"],  # 关联的 memory 列表
        "user_id": "u1", "agent_id": "a1", "run_id": "r1",  # scope
    }
}
```

---

## 4. Entity 怎么被抽取（add pipeline Phase 7）

详见 [`01-py-sdk-core/06-add-pipeline.md`](../01-py-sdk-core/06-add-pipeline.md) §Phase 7。简化版：

```python
# 1. 用 spaCy NER 从 memory text 抽实体
entities = extract_entities_batch(memory_texts)
# 例: "Apple released new iPhone" → [("ORG", "Apple"), ("PRODUCT", "iPhone")]

# 2. 全局去重 + batch embed entity texts
entity_embeddings = self.embedding_model.embed_batch(entity_texts, "add")

# 3. batch search 已有 entity（top_k=1, score >= 0.95 阈值）
existing_matches = self.entity_store.search_batch(
    queries=valid_texts, vectors_list=valid_vectors, top_k=1, filters=search_filters,
)

# 4. 分流：existing（更新 linked_memory_ids）vs new（批量 insert）
for j, key in enumerate(valid_keys):
    exact_match = exact_matches.get(key)
    semantic_match = matches[0] if matches and matches[0].score >= 0.95 else None
    match = exact_match or semantic_match

    if match:
        # 更新现有 entity 的 linked_memory_ids
        payload = match.payload
        linked = set(payload.get("linked_memory_ids", []))
        linked |= memory_ids    # 合并
        payload["linked_memory_ids"] = sorted(linked)
        self.entity_store.update(vector_id=match.id, vector=None, payload=payload)
    else:
        # 新 entity 入待插入列表
        to_insert_payloads.append({
            "data": entity_text,
            "entity_type": entity_type,
            "linked_memory_ids": sorted(memory_ids),
            **search_filters,
        })

# 5. 单次批量 insert 新 entities
self.entity_store.insert(vectors=to_insert_vectors, ids=to_insert_ids, payloads=to_insert_payloads)
```

---

## 5. Entity 怎么被用（search pipeline Step 6）

详见 [`01-py-sdk-core/07-search-pipeline.md`](../01-py-sdk-core/07-search-pipeline.md) §3。简化版：

```python
# search 时
query_entities = extract_entities(query)   # 从 query 抽实体

# 对每个 entity,score >= 0.5 的匹配 entity 把 boost 加到它的 linked memories
for entity_text in query_entities:
    entity_embedding = self.embedding_model.embed(entity_text, "search")
    matches = self.entity_store.search(
        query=entity_text, vectors=entity_embedding,
        top_k=500,  # 抓所有相似 entity
        filters=search_filters,
    )
    for match in matches:
        similarity = match.score
        if similarity < 0.5:
            continue
        linked_memory_ids = match.payload.get("linked_memory_ids", [])
        num_linked = max(len(linked_memory_ids), 1)
        # memory_count_weight 衰减：链接越多 memory 的 entity,boost 越小
        memory_count_weight = 1.0 / (1.0 + 0.001 * ((num_linked - 1) ** 2))
        boost = similarity * ENTITY_BOOST_WEIGHT * memory_count_weight

        for memory_id in linked_memory_ids:
            memory_boosts[memory_id] = max(memory_boosts.get(memory_id, 0), boost)

# 然后 score_and_rank 把 boost 加到 final score
```

---

## 6. 为什么不用独立 graph DB 了？

| 维度 | 独立 graph DB（Neo4j 等） | entity_store（vector 复用） |
|------|-----------------------|-------------------------|
| 依赖 | 多一个数据库 | 0 新依赖 |
| 运维 | 多一个服务 | 0 新服务 |
| Cypher 查询能力 | 强 | 无（vector 相似度查） |
| 部署复杂度 | 高 | 低（自托管用户友好） |
| 关系表达 | 完整 graph（多跳） | 简单（entity ↔ memories 双向） |
| 性能 | graph traversal 快 | vector search + ID 跟随 |

### Mem0 的权衡选择

- **降复杂度**：自托管用户只需起 vector store（不需要 Neo4j）
- **够用**：benchmarks 显示 entity linking + multi-signal 已经把分数从 71.4 提到 92.5
- **API 简化**：`MemoryConfig.graph` 字段消失,用户少配一项

### 留下的损失

- 无法做复杂关系查询（"用户的所有同事的朋友"这种多跳）
- 关系结构是隐式的（在 linked_memory_ids 里）,不显式

---

## 7. 迁移：旧 graph user 怎么办

如果你之前用 `MemoryConfig(graph=GraphConfig(provider="neo4j", ...))`:

### 选项 A：留在 v1.0

```bash
pip install 'mem0ai<2.0'
```

继续用旧版（但不再维护）。

### 选项 B：升 v1.1+,接受新设计

```python
# 删 graph config
config = MemoryConfig(
    llm=...,
    vector_store=...,    # 没 graph 字段了
)
m = Memory(config=config)
# entity_store 自动启用（基于 vector store）
```

### 选项 C：自己加 graph 后端

继承 `MemoryBase` 写自己的 `GraphMemory` 类,在 `add`/`search` 里调 Neo4j。但这要写不少代码。

---

## 7.5 三层状态澄清（DeepWiki 4.1 关键发现）

| 层 | 状态 | 说明 |
|---|---|---|
| **Mem0 Platform** | ✅ **Native Graph Memory** | 自动 entity 抽取 + 关系推理 + multi-hop,**无需 Neo4j** |
| **OSS `mem0/memory/main.py`** | ❌ **不 import graph 模块** | main pipeline 不用独立 graph store |
| **OSS `mem0/memory/utils.py`** | ✅ **保留 legacy helper** | `format_entities` (L79-88) / `sanitize_relationship_for_cypher` (L10-11) / `remove_spaces_from_entities` |
| **OSS 替代** | ✅ **`entity_store`** | 复用 vector store,独立 collection,见上文 |

DeepWiki 4.1 原文：

> "In the Mem0 Platform, Graph Memory is **native and built-in**, replacing the need for external graph stores like Neo4j or Memgraph for most users"
> 
> "Mem0 has transitioned from requiring external graph databases to a native, built-in system on the Platform. However, the codebase still maintains utility functions for legacy sanitization... which are used when interfacing with external stores"

### Platform native vs OSS entity_store

| 维度 | Platform Native Graph | OSS entity_store |
|------|---------------------|------------------|
| 部署 | 内置 | 复用 vector store |
| 关系类型 | 推断（co-occurrence）+ 显式（LLM 抽） | 仅 co-occurrence |
| Multi-hop 推理 | ✅ | ❌ |
| 关系查询 API | ✅（`relations` 字段返回） | ❌ |
| 配置 | 0 配置 | 0 配置（自动启用） |
| 性能 | 高（专有索引） | 中（vector search + ID 跟随） |

---

## 8. 一个误解：entity_store ≠ graph

很多人以为 entity_store 是"轻量 graph",**不准确**。

| 真正的 graph | entity_store |
|------------|------------|
| 节点 + 边（多对多关系） | entity + linked_memory_ids（一对多映射） |
| 关系有类型/属性 | 只有 entity_type（spaCy 标的 ORG/PERSON/...） |
| 支持 Cypher 多跳查询 | 只能 vector 相似度查 + 拿 linked_memory_ids |
| 关系可独立查询 | 关系是 entity 的属性,不能反向查 |

> entity_store 是"**带实体索引的 vector store**",不是 graph。

---

## 9. 相关代码索引

| 代码 | 行号 | 用途 |
|------|------|------|
| `Memory.entity_store` property | main.py L553-L575 | 懒加载 |
| `_entity_collection_name` | main.py L417-L419 | 命名约定 |
| `_existing_entities_by_text` | main.py L581-L598 | exact text 查 |
| `_upsert_entity` | main.py L600-L645 | 单 entity upsert |
| `_remove_memory_from_entity_store` | main.py L647-L700 | delete 时清理 |
| `_link_entities_for_memory` | main.py L702-L723 | 单 memory linking（update 时用） |
| add() Phase 7 | main.py L1081-L1185 | batch linking（add 时用） |
| `_compute_entity_boosts` | main.py L1728-L1808 | search 时算 boost |

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| add() Phase 7（entity linking 5 子阶段） | [`01-py-sdk-core/06-add-pipeline.md`](../01-py-sdk-core/06-add-pipeline.md) §Phase 7 |
| search() Step 6（entity boost 公式） | [`01-py-sdk-core/07-search-pipeline.md`](../01-py-sdk-core/07-search-pipeline.md) §3 |
| entity 抽取（spaCy NER） | [`08-utils.md`](./08-utils.md) |
| Reranker（替代品,提升精准度） | [`06-rerankers.md`](./06-rerankers.md) |

---

📌 **下一步** → [`02-llms.md`](./02-llms.md) 21 个 LLM provider。
