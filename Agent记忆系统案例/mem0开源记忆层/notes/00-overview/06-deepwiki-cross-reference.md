# 06 — DeepWiki 交叉对照与补充

> 本篇基于 [DeepWiki `mem0ai/mem0`](https://deepwiki.com/mem0ai/mem0)（80+ 子页面,17 章）与本笔记系列的交叉对照。
> DeepWiki 是 Cognition Labs（Devin）做的"自动 wiki",**基于同 commit `4debc58a` 生成**(2026-08-11 index)。它的视角独特——按"概念主题"组织,而本笔记按"源码目录"组织。
> 本篇是**互补**:DeepWiki 强调概念和数据流,本笔记强调行号和实现细节。

---

## 1. DeepWiki 目录结构（17 章 80+ 页）

| 章节 | 子页 | 对应本笔记 |
|------|-----|----------|
| **1. Overview** | 1.1 System Architecture / 1.2 Install / 1.3 Deployment Models | [`00-overview/`](../00-overview/) |
| **2. Core Architecture** | 2.1 Factory Pattern / 2.2 Provider Ecosystem / 2.3 Configuration | [`02-py-sdk-providers/`](../02-py-sdk-providers/) |
| **3. Memory System** | 3.1 Memory Class / 3.2 MemoryClient / 3.3 Operations / 3.4 Scoping / 3.5 Async / 3.6 Proxy / 3.7 Intelligent Processing | [`01-py-sdk-core/`](../01-py-sdk-core/) + [`03-py-sdk-client/`](../03-py-sdk-client/) |
| **4. Graph Memory** ⚠️ | 4.1 Overview / 4.2 Store Providers / 4.3 Entity Extraction / 4.4 Search / 4.5 Thresholds | [`02-py-sdk-providers/05-graphs.md`](../02-py-sdk-providers/05-graphs.md) |
| **5. Storage Backends** | 5.1 Vector Stores / 5.2 Providers / 5.3 Config / 5.4 History Audit | [`02-py-sdk-providers/04-vector-stores.md`](../02-py-sdk-providers/04-vector-stores.md) + [`01-py-sdk-core/03-storage.md`](../01-py-sdk-core/03-storage.md) |
| **6. AI Model Integrations** | 6.1 LLMs / 6.2 LLM Config / 6.3 Embeddings / 6.4 Embed Config / 6.5 Reranking | [`02-py-sdk-providers/02-llms.md`](../02-py-sdk-providers/02-llms.md) 等 |
| **7. Platform and API** | 7.1 Hosted / 7.2 REST API / 7.3 Versioning / 7.4 Orgs / 7.5 Webhooks / 7.6 Export | [`03-py-sdk-client/`](../03-py-sdk-client/) |
| **8. Client SDKs** | 8.1 Python / 8.2 TS / 8.3 Vercel AI | [`04-ts-sdk/`](../04-ts-sdk/) |
| **9. Framework Integrations** | 9.1 Agent Frameworks / 9.2 OpenClaw / 9.3 Voice / 9.4 Dev Tools / 9.5 MCP / 9.6 Pi | [`08-integrations/`](../08-integrations/) |
| **10. Usage Patterns** | 10.1 Basic / 10.2 Advanced / 10.3 Domain | [`10-examples-eval/`](../10-examples-eval/) |
| **11. Advanced Features** | 11.1 Custom Prompts / 11.2 Telemetry / 11.3 Performance / 11.4 Filtering / 11.5 Batch | 散见各章 |
| **12. Self-Hosted Server** | 12.1 Setup / 12.2 Auth / 12.3 Dashboard | [`05-server/`](../05-server/) |
| **13. CLI** | 13.1 Commands / 13.2 Config | [`06-cli-python/`](../06-cli-python/) + [`07-cli-node/`](../07-cli-node/) |
| **14. Development** | 14.1 Setup / 14.2 Testing / 14.3 CI/CD / 14.4 Contrib / 14.5 Docs / 14.6 Eval / 14.7 Skills | [`00-overview/03-build-system.md`](./03-build-system.md) + [`00-overview/04-cicd.md`](./04-cicd.md) + [`09-skills/`](../09-skills/) |
| **15. OpenMemory (Deprecated)** | 15.1 Migration / 15.2 MCP | （旧版本,本笔记不覆盖） |
| **16. Legacy: Embedchain** | 16.1 / 16.2 / 16.3 | （更老的遗留,不覆盖） |
| **17. Glossary** | — | [`99-appendix/index.md`](../99-appendix/index.md) §A |

---

## 2. ⚠️ 行号差异（重要说明）

DeepWiki 引用的行号**与本笔记不一致**。例：

| 内容 | DeepWiki 行号 | 本笔记行号（实测） |
|------|-------------|----------------|
| `class Memory(MemoryBase)` | L216 | **L482** |
| `AsyncMemory` | L1140 | **L2161** |
| `add()` | L326-L429 / L431-L642 | **L755-L1202** |
| `search()` | L803-L912 | **L1374-L1818** |

**原因**：DeepWiki 索引的是 `4debc58a`,但**行号映射可能基于不同的代码状态**（如未含所有 PR / commit 顺序差异）。本笔记的行号基于**本地仓库** `grep -n` 实测,**更可靠**。

**建议**：
- 看本笔记优先用行号
- 看 DeepWiki 优先用**概念解释 + 源文件名 + 类名/函数名**（这些跨版本稳定）
- 行号引用一律以本笔记为准

---

## 3. ⭐ 重大澄清：Graph Memory 实际状态

DeepWiki 4.1 章澄清了我笔记之前没说清的状态：

### 实际三层状态

| 层 | Graph Memory 状态 |
|---|----------------|
| **Mem0 Platform（hosted）** | ✅ **Native built-in**（自动 entity 抽取 + 关系推理,**无需 Neo4j**） |
| **OSS `mem0/memory/main.py`** | ❌ 不 import 任何 `mem0.graphs.*` 模块（已移除独立调用） |
| **OSS 工具函数（保留）** | ✅ `mem0/memory/utils.py` 仍含 `format_entities` / `sanitize_relationship_for_cypher` / `remove_spaces_from_entities`（legacy 给外部 graph store 用） |
| **OSS graph store provider** | ⚠️ 不在 main pipeline（但 DeepWiki 提及历史代码可能仍在） |

### 修正之前的笔记

我笔记 [`02-py-sdk-providers/05-graphs.md`](../02-py-sdk-providers/05-graphs.md) 之前说"已移除"——更准确的说法是：

> **OSS main pipeline 不再使用独立 graph store**,改用基于 vector store 的 `entity_store`（复用同一 vector store provider,独立 collection）。但 Platform 仍内置完整 graph memory（自动抽取、boost 检索、multi-hop reasoning）。OSS 保留部分 legacy utility 函数供向后兼容。

详见 [`02-py-sdk-providers/05-graphs.md`](../02-py-sdk-providers/05-graphs.md)（已更新）。

---

## 4. ⭐ Session Scoping 完整说明（DeepWiki 3.4 补充）

我笔记 [`00-overview/02-architecture.md`](./02-architecture.md) 提到 scope,但 DeepWiki 给了更完整的语义。

### 4 个 scope 完整定义

| Identifier | Scope | 典型生命周期 | 用例 |
|---|---|---|---|
| `user_id` | 单个用户/账号 | 周-年 | 用户偏好、profile |
| `agent_id` | 特定 agent | 天-月 | agent 特定学习、操作模式 |
| `app_id` | 应用上下文 | 周-月 | 白标部署、服务隔离 |
| `run_id` | 单次对话/session | 分钟-小时 | 客服工单、临时聊天 |

> 注意：本笔记之前只强调 user_id/agent_id/run_id,**`app_id` 也是 scope 之一**（虽然 SDK 主路径常用前三个）。

### Identity 自动生成（telemetry 用）

```python
# mem0/client/main.py L125-L143
self.user_id = hashlib.md5(self.api_key.encode()).hexdigest()  # MD5(api_key)
# 通过 header 发送
"Mem0-User-ID": <md5_hash>
```

TS SDK 同样：

```typescript
// mem0-ts/src/client/mem0.ts L182-L184
const telemetryId = crypto.createHash('md5').update(apiKey).digest('hex');
```

### Project 级 agent 配置

```python
# mem0/client/project.py L180
# Project 可配 agent_custom_instructions（仅 agent-scoped memory 抽取时用）
project.update(agent_custom_instructions="Focus on coding preferences")
```

### Multi-agent 隔离

```python
# 同一 user_id 下多 agent
m.add("...", user_id="alice", agent_id="coder")      # coder agent 的 memory
m.add("...", user_id="alice", agent_id="researcher") # researcher agent 的 memory
m.search("...", filters={"user_id":"alice", "agent_id":"coder"})  # 不污染
```

---

## 5. ⭐ Advanced Filtering 完整 Operator 表（DeepWiki 11.4）

DeepWiki 给出了**带 PGVector SQL fragment** 的完整 operator 表（非常有价值）：

| Operator | 描述 | PGVector SQL Fragment |
|---|---|---|
| `eq` | Equals | `payload->>'%KEY%' = $%IDX%` |
| `ne` | Not Equals | `payload->>'%KEY%' != $%IDX%` |
| `gt` | Greater Than | `(payload->>'%KEY%')::numeric > $%IDX%` |
| `gte` | Greater Than or Equal | `(payload->>'%KEY%')::numeric >= $%IDX%` |
| `lt` | Less Than | `(payload->>'%KEY%')::numeric < $%IDX%` |
| `lte` | Less Than or Equal | `(payload->>'%KEY%')::numeric <= $%IDX%` |
| `in` | Value in list | `payload->>'%KEY%' = ANY($%IDX%::text[])` |
| `nin` | Value not in list | `NOT (payload->>'%KEY%' = ANY($%IDX%::text[]))` |
| `contains` | Case-sensitive substring | `payload->>'%KEY%' LIKE $%IDX% ESCAPE '\\'` |
| `icontains` | Case-insensitive substring | `payload->>'%KEY%' ILIKE $%IDX% ESCAPE '\\'` |
| `*` | Field exists (wildcard) | `payload ? %KEY%` |

### Logical Operators

```python
filters = {
    "user_id": "u1",                       # 必有 scope
    "AND": [{"category":"work"}, {"priority":"high"}],
    "OR": [{"tag":"vip"}, {"tag":"svip"}],
    "NOT": [{"archived": True}],
}
```

### 各 vector store 实现差异

| Provider | 实现方式 | 自动索引 session 字段 |
|---------|---------|------------------|
| **PGVector** | JSONB payload + `::numeric` cast + `LIKE/ILIKE` | ❌（要自己加） |
| **Qdrant** | `Filter` + `FieldCondition` + `MatchValue`（结构化对象） | ✅（remote client 自动建 payload index） |
| **Chroma** | `_generate_where_clause` 转 Chroma dict 格式,`$and` grouping | ❌ |
| **OpenSearch** | DSL `term` / `exists` clauses,`_SAFE_FILTER_KEY` regex 验证 | ✅（`keyword` 类型 mapping） |
| **Elasticsearch** | 类似 OpenSearch,`bool` must + `knn` filter | ✅（`keyword` mapping） |

### 类型处理

- **Boolean** → JSON string 比对（`'true'` / `'false'`）
- **List** → `ANY()` SQL（in 操作）
- **Validation**：OpenSearch 严格验证 value 是 scalar（防注入）

详见 [`01-py-sdk-core/07-search-pipeline.md`](../01-py-sdk-core/07-search-pipeline.md) §5（已更新）。

---

## 6. ⭐ Batch Operations（DeepWiki 11.5 补充）

### `batch_update(memories)` 和 `batch_delete(memories)`

```python
# Platform-only,Python SDK
m.batch_update([
    {"memory_id": "id1", "text": "new text 1"},
    {"memory_id": "id2", "metadata": {"updated": True}},
])
m.batch_delete([
    {"memory_id": "id1"},
    {"memory_id": "id2"},
])
```

### 关键特性

| 特性 | 说明 |
|------|------|
| **Platform Only** | OSS `Memory` 类没有这方法 |
| **单请求** | 把 list wrap 到 `memories` key 一次 POST |
| **TS camelCase 自动转换** | `memoryId` → `memory_id` |
| **不保证原子性** | 部分失败不回滚,要看 response 里每条的 status |
| **错误码** | 400 → ValidationError,401 → AuthenticationError,404 → MemoryNotFoundError |
| **遥测** | 成功后 fire `client.batch_update` 事件 |

### 何时用 batch

- bulk cleanup（删一批过期 memory）
- session migration（改一批 memory 的 metadata）
- 高延迟优化（RTT 大时,N 次 → 1 次）

详见 [`03-py-sdk-client/01-client.md`](../03-py-sdk-client/01-client.md) §7（已更新）。

---

## 7. ⭐ History & Audit（DeepWiki 5.4 补充）

### Schema 差异（Python vs TS）

| 列 | Python `history` 表 | TS `memory_history` 表 |
|---|---|---|
| 10 列 | 同 | 同 |

但**排序方向不同**：
- Python `get_history`: `ORDER BY created_at ASC, DATETIME(updated_at) ASC`（chronological）
- TS `getHistory`: `ORDER BY id DESC`（最近优先）

> 这是**API 不一致**——同样的 `history()` 调用,Python 和 TS 返回顺序不同。生产注意。

### `Memory.reset()` 行为（重要）

```python
def reset(self):
    self.db.reset()  # DROP history + messages 两张表
    self.db.close()
    self.vector_store = VectorStoreFactory.reset(self.vector_store)  # 重置 vector store
    self._entity_store = None  # 下次访问重建
```

**messages 表显式清空**——DeepWiki 5.4 强调这点（之前我没说清）：

> "The messages table is explicitly cleared during a `Memory.reset()` operation to ensure full data removal" — tests/test_memory.py L141-L143

详见 [`01-py-sdk-core/03-storage.md`](../01-py-sdk-core/03-storage.md) §5（已更新）和 [`01-py-sdk-core/08-update-delete.md`](../01-py-sdk-core/08-update-delete.md) §8。

---

## 8. ⭐ Async Operations（DeepWiki 3.5 补充）

### Python `AsyncMemory` vs `Memory`

| 维度 | Memory（sync） | AsyncMemory |
|---|---|---|
| LLM 调用 | 直接 sync | `await` |
| Entity boost 搜索 | `ThreadPoolExecutor(max_workers=4)` | `asyncio.gather` |
| 同步 helper 复用 | — | 用 `asyncio.to_thread` 包 sync helper |
| 测试覆盖 | 主测试 | `tests/memory/test_main.py` 镜像 |

### TS Memory 全 async

```typescript
class Memory {
  async add(messages, options?, filters?): Promise<...>
  async search(query, options?, filters?): Promise<...>
  // 所有方法都 async
}
```

> TS 没有单独的 `AsyncMemory` 类——所有方法默认 async。

### 并发模式

```python
# AsyncMemoryClient 并发
import asyncio
from mem0 import AsyncMemoryClient

async def main():
    async with AsyncMemoryClient(api_key="...") as m:
        results = await asyncio.gather(*[
            m.add(msg, filters={"user_id":"u1"}) for msg in messages
        ])
```

---

## 9. ⭐ `mem0/memory/utils.py` 关键 helper（DeepWiki 3.7 补充）

DeepWiki 揭示了几个我笔记没强调的 utility 函数（在 `mem0/memory/utils.py`）：

| 函数 | 行号（DeepWiki） | 用途 |
|------|--------------|------|
| `format_entities` | L79-L88 | 格式化 entity 给 graph store（legacy） |
| `sanitize_relationship_for_cypher` | L10-L11 | Cypher 关系字符串清理（legacy Neo4j） |
| `remove_spaces_from_entities` | — | entity 文本去空格 |
| `normalize_facts` | L90-L112 | 把 LLM 输出统一成 list of strings（小 LLM 可能返 obj 而非 str） |
| `remove_code_blocks` | L115-L128 | 去 markdown ` ``` ` 包裹 + 去 `<think>` 标签（DeepSeek 等 reasoning model） |
| `ensure_json_instruction` | L36-L58 | 如果用户 custom prompt 没说 "json",自动追加 JSON 强制指令 |
| `parse_messages` | L61 | 把 list[dict] 转 flat string 给 LLM |
| `extract_json` | L125 | robust 从 LLM 响应抽 JSON |

> `remove_code_blocks` 处理 `<think>` 标签很重要——DeepSeek R1 / o1 等 reasoning model 会输出 `<think>...</think>`,这个 helper 帮清理。

---

## 10. ⭐ V3 Additive Pipeline 关键概念（DeepWiki 3.7 补充）

### `linked_memory_ids` 不是 graph 关系,是 **supersede chain**

我笔记之前混淆了 `linked_memory_ids`（memory 上）和 `linked_memory_ids`（entity 上）。DeepWiki 3.7 澄清：

- **Entity 的 `linked_memory_ids`** = 哪些 memory 提到这个 entity（多对多映射）
- **Memory 的 `linked_memory_ids`**（LLM 输出） = 这条 memory "supersede/延续" 哪些已有 memory

> 当前 OSS 实际**只用 entity 的 linked_memory_ids**（用于 boost）,memory 上的 supersede linking LLM 输出**目前 OSS 未消费**（但 Platform 可能用）。

### `delete_linked=True`（Platform only）

```python
# Platform-only
m.delete(memory_id, delete_linked=True)
# 传递删除整个 supersede chain
```

> OSS 的 `delete()` 只接 `memory_id`,没有 `delete_linked` 参数。

### V3 简化的 action determination

| 旧 V1/V2 | V3 |
|---------|---|
| 多次 LLM 调用,LLM 决策 ADD/UPDATE/DELETE/NONE | **无 action determination**——所有抽取出来都 ADD |
| 复杂 merge logic | LLM 在 prompt 内做 dedup |
| 2-3 次 LLM 调用 | 1 次 LLM 调用（single-pass） |

---

## 11. ⭐ 几个 DeepWiki 揭示的额外细节

### `MemoryClient` 自动 user_id

```python
# 用户不传 user_id 时,client 自动生成（telemetry 用）
self.user_id = hashlib.md5(api_key.encode()).hexdigest()
```

但**业务 memory 仍需显式 user_id**——telemetry user_id 跟 memory scope user_id 是两个概念。

### `Memory` 类的 `enable_graph` 配置（legacy）

DeepWiki 提到旧版 `MemoryConfig(graph=GraphConfig(enable_graph=True))`——这在当前 OSS 已废弃（`MemoryConfig` 没 `graph` 字段）。

### Vercel AI SDK Provider

`@mem0/vercel-ai-provider` 让 Mem0 当 Vercel AI SDK 的 model 用：

```typescript
import { Mem0Provider } from '@mem0/vercel-ai-provider';
import { streamText } from 'ai';

const provider = new Mem0Provider({
  apiKey: process.env.MEM0_API_KEY,
  userId: 'alice',
});

const result = await streamText({
  model: provider,  // ⭐ 当 model 用
  messages: [...],
});
```

> 自动 add + search memory,开发者无感。

---

## 12. 本笔记没覆盖但 DeepWiki 有的（参考用）

| DeepWiki 章节 | 价值 | 建议 |
|------------|-----|-----|
| **7.3 API Versioning** | v1/v2/v3 endpoint 区别 | 看 DeepWiki |
| **7.4 Organizations and Projects** | 多组织结构 | 看 DeepWiki |
| **7.5 Webhooks and Events** | 事件订阅 | 看 DeepWiki |
| **7.6 Memory Export** | 数据导出 | 看 DeepWiki |
| **9.1 Agent Frameworks** | CrewAI/LangGraph/AutoGen 集成 | 看 DeepWiki |
| **9.3 Voice and Multimodal** | 语音/视觉 | 看 DeepWiki |
| **11.1 Custom Prompts** | 自定义 prompt 高级用法 | 看 DeepWiki |
| **11.2 Telemetry and Analytics** | dashboard 解读 | 看 DeepWiki |
| **11.3 Performance Optimization** | 性能调优 | 看 DeepWiki |
| **14.2 Testing** | 测试策略 | 看 DeepWiki |
| **14.5 Documentation System** | Mintlify 文档系统 | 看 DeepWiki |
| **14.6 Evaluation Framework** | benchmark 内部 | 看 DeepWiki |
| **15.x OpenMemory (Deprecated)** | 旧版本 | 跳过 |
| **16.x Embedchain (Legacy)** | 更老的 | 跳过 |

---

## 13. DeepWiki 局限性

| 局限 | 影响 |
|------|------|
| 行号可能不准 | 必须用类名/函数名定位 |
| Graph Memory 章节仍存在 | 容易误以为 OSS 有 graph（实际 main pipeline 不用） |
| 不区分 OSS / Platform 差异 | 比如 `delete_linked=True` 是 Platform only,DeepWiki 没明确标 |
| 自动生成,缺"为什么" | 没解释设计决策的权衡 |
| 不含性能数字 / benchmark | 只有概念 |
| 不会随上游自动同步 | 7 天才 refresh 一次 |

---

## 14. 推荐使用方式

| 场景 | 用 DeepWiki | 用本笔记 |
|------|----------|---------|
| 第一次理解 Mem0 | ✅ 概念清晰 | 略枯燥 |
| 找具体行号实现 | ❌ 不准 | ✅ 实测 |
| 看 architecture 图 | ✅ mermaid 多 | 各章都有 |
| 看 API 端点列表 | ✅ 全 | 仅 server 部分 |
| 选 vector store | 类似 | ✅ 有对比表 |
| 调试具体 bug | ❌ 缺细节 | ✅ 有坑点说明 |
| 设计决策权衡 | ❌ 缺 | ✅ 有 |

---

## 15. 接下来

| 想看 | 去哪 |
|------|------|
| 本笔记 README | [`../README.md`](../README.md) |
| Graph Memory 实际状态 | [`../02-py-sdk-providers/05-graphs.md`](../02-py-sdk-providers/05-graphs.md) |
| 完整 filter operator 表 | [`../01-py-sdk-core/07-search-pipeline.md`](../01-py-sdk-core/07-search-pipeline.md) |
| Batch operations | [`../03-py-sdk-client/01-client.md`](../03-py-sdk-client/01-client.md) |
| History 细节 | [`../01-py-sdk-core/03-storage.md`](../01-py-sdk-core/03-storage.md) |
| DeepWiki 原站 | https://deepwiki.com/mem0ai/mem0 |

---

📌 **下一步** → [`../README.md`](../README.md) 回总入口,或看上面 §15 的具体章节。
