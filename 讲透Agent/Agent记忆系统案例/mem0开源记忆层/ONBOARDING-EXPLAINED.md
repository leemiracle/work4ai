# Mem0 Onboarding 全文件深度解释（ONBOARDING-EXPLAINED）

> 本文档由 `/understand-explain` 基于 `docs/ONBOARDING.md`（612 行）+ `.understand-anything/knowledge-graph.json`（2071 nodes / 3600 edges / 15 layers）+ 真实源码（4 个 @fixer 子代理并行读取）生成。
> 生成时间：2026-08-11 · 基线 commit：`4debc58a`
> 阅读对象：想深度理解每个 ONBOARDING 提及文件的角色、内部结构、数据流的开发者。

---

## 0. 摘要

| 指标 | 数值 |
|------|------|
| ONBOARDING.md 提及文件 | **226 个唯一路径** |
| 在 knowledge-graph.json 中解析成功 | **209 个**（93%） |
| ONBOARDING 引用错误 | **2 个**（`api.md` 应为 `api-reference.md`；`mem0.ts.types.ts` 不存在） |
| 图谱节点类型分布 | file / document / config / pipeline / schema / service / example |
| ⭐🔥 双标记（最关键） | **11 个** |
| ⭐ 单标记（重要） | 11 个 |
| 🔥 单标记（复杂热点） | 46 个 |
| 普通 | 141 个 |

**核心洞察**：Mem0 是 **双 SDK 同构**（Python `Memory` ↔ TS `Memory`）的 polyglot monorepo，15 个架构层中第 1-6 层是引擎核心（**算法灵魂**），第 7-15 层是外围生态（封装、CLI、集成、文档）。所有上层（CLI / Server / Integrations）共用相同的 Memory 契约。

---

## 1. ⭐🔥 双标记 11 个文件（最关键，逐个深度解释）

### 1.1 `mem0/memory/main.py` (3851 行) — Python OSS 核心引擎

**图谱**: `file:mem0/memory/main.py` · layer: Python SDK 核心引擎 · complexity=complex · in_edges=? · out_edges=?

#### 角色定位
Mem0 **自托管模式的引擎室**。`Memory`（L482）与 `AsyncMemory`（L2161）两个类封装了从消息输入到向量存储、实体链接、混合检索、历史记录的完整闭环。与 `mem0/client/main.py`（Hosted 平台客户端）是**平行两套实现**——前者本地跑 LLM+embedding+vector_store，后者把请求转发到 `api.mem0.ai`。所有 provider 通过 `mem0.utils.factory` 注入，本文件只编排不实现。

#### 核心结构

**模块级 helper（L85–446，~20 个）**
- `_vector_store_list_rows` — 统一拆解 Chroma `[[...]]` / Qdrant `([...], n)` / PG `[...]` 三种 list 返回格式
- `_strip_identity_keys` / `_reject_top_level_entity_params` — 防 scope 注入（issue #4490/#6277/#6655）
- `_validate_and_trim_entity_id` — entity ID 强转 str + 拒空/拒内部空白
- `_is_sensitive_field` / `_safe_deepcopy_config` — telemetry 三层脱敏
- `_build_filters_and_metadata` — **核心**：产出 `(base_metadata_template, effective_query_filters)`，strip 身份键 + 校验至少一个 entity ID
- `_entity_collection_name` — s3_vectors 用 `-entities` 后缀，其余用 `_entities`

**`Memory` 类（继承 `MemoryBase`）**

| 方法 | 行号 | 用途 |
|------|------|------|
| `__init__(config)` | — | 4 个 Factory 创建 embedding/vector_store/llm/db，懒加载 `_entity_store=None`，可选 reranker + telemetry vector store |
| `from_config(config_dict)` (classmethod) | L726 | dict → MemoryConfig → 实例 |
| `add(messages, *, user_id, agent_id, run_id, metadata, timestamp, expiration_date, infer=True, memory_type, prompt)` | L755 | **主写入入口**；timestamp 在 OSS 报错，procedural 走 `_create_procedural_memory` |
| `_add_to_vector_store(...)` | L874 | **V3 phased batch pipeline**（见数据流） |
| `_create_memory(data, existing_embeddings, metadata)` | — | 单条写入：embed 缓存 + md5 去重 + text_lemmatized + history |
| `get(memory_id)` | L1203 | promoted keys 提升 + metadata 收拢 |
| `get_all(*, filters, top_k=20, show_expired=False)` | L1250 | fetch_limit = max(top_k*4, 60) |
| `search(query, *, top_k=20, filters, threshold=0.1, rerank=False, explain=False, reference_date, show_expired)` | L1374 | **主检索入口** |
| `_search_vector_store(query, filters, limit, threshold, explain, show_expired)` | L1623 | **9 步混合检索** |
| `_compute_entity_boosts(query_entities, filters)` | — | ThreadPoolExecutor(max_workers=4) 并行实体搜索 |
| `update(memory_id, text, metadata, expiration_date, data)` | L1810 | data 是 text 的 deprecated 别名 |
| `delete(memory_id)` / `delete_all(user_id, agent_id, run_id)` | L1864/L1885 | DELETE_ALL_BATCH_SIZE=1000，seen_batches 防重复 |
| `history(memory_id)` | L1941 | 从 SQLite 读 |
| `reset()` | L2119 | db.reset + vector_store reset + entity_store reset |
| `chat(query)` | L2157 | NotImplementedError |

**`AsyncMemory` 类（L2161–3851）**：1:1 镜像 Memory，所有 I/O 包 `asyncio.to_thread`；多 `_bulk_clear_entity_store`（防并发 read-modify-write race）。

#### 数据流

**`add()` 主链路（infer=True，V3 single-pass ADD-only）**
```
messages → 标准化 list[dict]
  → _build_filters_and_metadata (strip identity keys + 校验)
  → parse_vision_messages (可选)
  → _add_to_vector_store:
      Phase 0: session_scope + db.get_last_messages(10) + parse_messages
      Phase 1: embed(parsed) → vector_store.search(top_k=10) → UUID→整数映射 (防幻觉)
      Phase 2: LLM 单次调用 (ADDITIVE_EXTRACTION_PROMPT) → JSON {memory:[...]}
      Phase 3: embed_batch(mem_texts) → embed_map (失败逐条回退)
      Phase 4-5: per-memory md5 hash 去重 + lemmatize_for_bm25
      Phase 6: vector_store.insert(批量) + db.batch_add_history
      Phase 7: extract_entities_batch → 全局去重 → batch embed → search_batch → 分流 insert/update
      Phase 8: db.save_messages + return [{"id","memory","event":"ADD"}]
```

**`search()` 主链路（hybrid retrieval）**
```
query → lemmatize_for_bm25 + extract_entities(query)
  → embed(query)
  → vector_store.search(top_k=max(limit*4,60)) [语义 over-fetch]
  → vector_store.keyword_search [BM25, 若支持]
  → normalize_bm25(keyword_scores, midpoint, steepness)
  → _compute_entity_boosts: ThreadPoolExecutor(4) 并行 entity_store.search(top_k=500)
  → score_and_rank(semantic + bm25 + entity_boost, threshold, top_k, explain)
  → MemoryItem 格式化
  → 可选 reranker.rerank
```

#### 关键模式
1. **Single-pass ADD-only（April 2026）**：不再 UPDATE/DELETE/NOOP，LLM 只做抽取不做决策；旧记忆的"失效"靠搜索端 score+threshold+rerank
2. **UUID 整数化防幻觉**：Phase 1 把 top-10 现有记忆的 UUID 映射成 "0".."9" 再喂给 LLM
3. **md5 hash 双层去重**：`existing_hashes`(库内) ∪ `seen_hashes`(本批次)
4. **ThreadPoolExecutor 三路并行**：entity boost 并发查询
5. **三层 telemetry 脱敏**：runtime allowlist / exact denylist / suffix denylist
6. **graceful degradation**：batch 操作几乎都有"失败逐条回退"，entity 操作 try/except 吞掉（non-fatal）

#### 阅读建议
先读 `add()` (L755) → `_add_to_vector_store` (L874) 的 8 个 Phase 注释——这是整个系统的核心。然后读 `_search_vector_store` (L1623) 的 9 步注释。**警惕**：(1) AsyncMemory 与 Memory 是**复制粘贴**而非继承；(2) entity_store 是懒加载；(3) 大量 `asyncio.to_thread` 包装同步 I/O——async 路径不阻塞事件循环的关键。

---

### 1.2 `mem0/client/main.py` (1838 行) — Python Hosted Platform Client

**图谱**: `file:mem0/client/main.py` · layer: Python Hosted Platform Client · complexity=complex · in_edges=85 · out_edges=11

#### 角色定位
Mem0 **托管平台的薄客户端**。与 `mem0/memory/main.py`（本地跑全套 pipeline）完全不同——这里没有 LLM/embedding/entity linking，所有计算在服务端。每个方法就是：组装 payload → HTTP 请求 → `api_error_handler` 装饰器 → 返回 JSON。

#### 核心结构

**`MemoryClient` 类**：构造器 `__init__(api_key, host, client)` 调 `/v1/ping/` 获取 org_id/project_id/user_email，`httpx.Client(timeout=300)`。

| 分类 | 方法 | HTTP | 端点 |
|------|------|------|------|
| CRUD | `add` | POST | `/v3/memories/add/` |
| | `get(memory_id)` | GET | `/v1/memories/{id}/` |
| | `get_all(options, **kwargs)` | POST | `/v3/memories/`（分页） |
| | `search(query, options)` | POST | `/v3/memories/search/` |
| | `update(memory_id, options)` | PUT | `/v1/memories/{id}/` |
| | `delete(memory_id)` | DELETE | `/v1/memories/{id}/` |
| | `delete_all(options)` | DELETE | `/v1/memories/` |
| | `history(memory_id)` | GET | `/v1/memories/{id}/history/` |
| 实体 | `users()` / `delete_users(...)` | GET/DELETE | `/v1/entities/`、`/v2/entities/{type}/{name}/` |
| 批量 | `batch_update(memories)` / `batch_delete(memories)` | PUT/DELETE | `/v1/batch/` |
| 反馈 | `feedback(memory_id, feedback, feedback_reason)` | POST | `/v1/feedback/` |

**`AsyncMemoryClient` 类**：1:1 镜像，`httpx.AsyncClient`，`__aenter__/__aexit__`。

#### 关键模式
1. **Typed Options 模式**：`AddMemoryOptions`/`SearchMemoryOptions` 等 Pydantic 模型，`model_dump(exclude_unset=True)` 只传显式字段
2. **API 版本碎片**：v1（get/update/delete/history/entities）、v2（delete_users）、v3（add/search/get_all）共存
3. **`api_error_handler` 统一异常映射**：httpx HTTPStatusError/RequestError → mem0 自定义异常体系（RateLimitError 提取 `Retry-After`）
4. **路径段编码**：`_encode_path_segment` 防 memory_id/entity name 注入

#### 阅读建议
先读 `__init__` + `_validate_api_key`（理解 org/project 解析）→ 任一 CRUD 方法（看 `@api_error_handler` + `_prepare_params` 模式）→ `mem0/client/utils.py` 的 `api_error_handler`（异常映射）。

---

### 1.3 `tests/test_memory.py` — Memory 类主回归测试集

**图谱**: `file:tests/test_memory.py` · layer: Python SDK 测试套件 · complexity=complex

#### 角色定位
`Memory` / `AsyncMemory` 的**主回归测试集**（不测 `MemoryClient`）。测试策略：**全 mock**——`@patch` 替换 4 个 Factory + SQLiteManager，让 `Memory.__init__` 不碰真实 LLM/embedding/vector_store，然后调 public/private 方法验证行为。每个 bug fix 配一个回归测试，测试名就是 issue 编号。

#### 测试分类（~45 个 test 函数）

| 类别 | 代表测试 | 覆盖路径 |
|------|---------|---------|
| CRUD 烟测（fixture） | test_create_memory 等 6 个 | public API 可用性（mock） |
| reset | test_collection_name_preserved_after_reset | reset() 清表 + 保留 collection 名 |
| 搜索健壮性 | test_search_handles_incomplete_payloads | _search_vector_store 跳过无 data payload |
| get_all 格式兼容 | test_get_all_handles_nested_list_from_chroma | 3 种 vector store 返回格式（issue #3674） |
| metadata filter merge | TestProcessMetadataFiltersMerge (7 个) | 同 key 多算子 deep-merge |
| entity param 拒绝 | test_search_rejects_user_id_kwarg | 拒顶层 entity param |
| embedding 缓存 | test_add_infer_false_embeds_once | V3 pipeline 不重复 embed |
| 错误透传 | test_update_propagates_vector_store_failure | ConnectionError 不被伪装成 ValueError |
| entity race | TestAsyncDeleteAllEntityRace | bulk-clear entity store |

#### 关键模式
1. **全 mock 测试**：4 个 `@patch` 是每个测试的标配
2. **sync + async 成对**：关键测试都有 sync + `@pytest.mark.asyncio` async 版
3. **issue 编号驱动**：docstring 引用 issue #（#3674/#3723/#3849/#3952/#4850/#5710）
4. **`mock_vector_factory.side_effect = [store, telemetry_store]`**：必须 2 个返回值（主 store + telemetry store）

#### 阅读建议
先读 `MockVectorMemory` + `memory_client` fixture（理解 mock 策略）→ `test_search_handles_incomplete_payloads`（看真实测试怎么写）→ `TestProcessMetadataFiltersMerge`（看 filter merge 边界）。

---

### 1.4 `mem0-ts/src/oss/src/memory/index.ts` (2207 行) — TS OSS 核心引擎

**图谱**: `file:mem0-ts/src/oss/src/memory/index.ts` · layer: TypeScript SDK · complexity=complex

#### 角色定位
TS OSS `Memory` 是 Python `mem0.memory.main.Memory` 的 **同构移植**。两者 class 结构一一对应：构造器通过 5 个 Factory（Embedder/LLM/VectorStore/HistoryManager/Reranker）组装 provider，public API 表面完全一致（`add`/`search`/`get`/`getAll`/`update`/`delete`/`deleteAll`/`history`/`reset`）。TS 版独有 `_autoInitialize()` 的 **deferred pattern**（dimension probe + vector store init 放进 `_initPromise`，每个 public 方法 `await _ensureInitialized()`），Python 版在 `__init__` 同步完成。

#### 核心方法

| 方法 | 返回 | 对应 Python |
|------|------|------------|
| `constructor(config: Partial<MemoryConfig>)` | — | `__init__` |
| `static fromConfig(dict)` | Memory | `from_config` |
| `add(messages, config: AddMemoryOptions)` | SearchResult | `add` |
| `search(query, config: SearchMemoryOptions)` | SearchResult | `search` |
| `get(memoryId)` | MemoryItem \| null | `get` |
| `getAll(config)` | SearchResult | `get_all` |
| `update(memoryId, config)` | {message} | `update` |
| `delete(memoryId)` / `deleteAll(config)` / `history(memoryId)` / `reset()` | — | 同名 |
| `updateProject(options)` | never（OSS 抛错） | — |

#### 与 Python 的对齐差异
1. TS 用 `MemoryConfigSchema`（Zod `z.object`）在 `fromConfig` 做 parse，Python 用 Pydantic
2. TS 的 `addToVectorStore` 实现 **V3 phased batch pipeline**，Python 同逻辑结构相似但命名不同
3. TS 独有 **camelCase↔snake_case 双向转换层**（API 表面 camelCase，storage 用 snake_case）
4. TS 用 **deferred init + retry**：构造器不阻塞，首次 await；失败自动 retry

#### 关键模式
1. **Zod `.passthrough()` 容错**：允许 provider-specific 字段透传
2. **Entity store 双 VectorStore**：主 collection 存 memory，`{collection}_entities` 存 entity
3. **camelCase/snake_case 边界转换**

---

### 1.5 `mem0-ts/src/client/mem0.ts` (812 行) — TS Hosted MemoryClient

**图谱**: `file:mem0-ts/src/client/mem0.ts` · layer: TypeScript SDK · complexity=complex

#### 角色定位
Hosted Platform 的 HTTP 薄客户端，对应 Python `mem0.memory.client.MemoryClient`。OSS 在本地编排 LLM+embedder+vectorStore；本类只 POST 到 `api.mem0.ai`。两者 public API 一致，但 TS 版多了 platform-only 方法（`getProject`/`updateProject`/webhooks/`feedback`/`createMemoryExport`/`deleteUsers`）。

#### 方法清单（24 个 public async）
CRUD（add/search/get/getAll/update/delete/deleteAll/history）+ batch（batchUpdate/batchDelete）+ 实体（users/deleteUsers）+ Project + Webhook + feedback + export + ping。

#### 关键模式
1. **双引擎**：构造器内 `axios.create` 但实际走 `_fetchWithErrorHandling()`（原生 fetch），axios 是 dead code
2. **camelCase↔snake_case 边界转换**：请求 `camelToSnakeKeys`，响应 `snakeToCamelKeys`
3. **鉴权**：`Authorization: Token ${apiKey}`（注意是 `Token` 不是 `Bearer`）
4. **Identity cache 共享**：进程级 `Map<string, Promise<ClientIdentity>>` 同 apiKey 复用一次 ping 结果
5. **Telemetry aliasing**：把 OSS/CLI 匿名 ID 关联到 email

---

### 1.6 `server/main.py` (560 行) — FastAPI app 入口

**图谱**: `file:server/main.py` · layer: FastAPI 自托管 Server · complexity=complex

#### 角色定位
FastAPI app 入口与全部"扁平路由"（非 `/auth` 前缀）宿主。CORS 锁定 `DASHBOARD_URL`（默认 `localhost:3000`）；`Depends(verify_auth)` / `Depends(require_admin)` 做认证与权限分层；4 个 sub-router（auth / api_keys / entities / requests）经 `include_router` 挂载；模块顶层同步执行 `initialize_state(DEFAULT_CONFIG)` 构造全局 `Memory` 单例。

#### 端点表（14 个）

| HTTP | Path | 鉴权 |
|---|---|---|
| GET | `/` | 无（重定向 /docs） |
| GET/POST | `/configure` / `/configure/providers` | verify_auth / require_admin |
| POST | `/generate-instructions` | verify_auth |
| POST/GET/GET/PUT/GET/DELETE/DELETE | `/memories`、`/memories/{id}`、`/memories/{id}/history` | verify_auth（全量 DELETE 需 admin） |
| POST | `/search` | verify_auth |
| POST | `/reset` | **require_admin** |

#### 数据流（POST /memories）
1. `log_requests` middleware 生成 `X-Request-ID`、计时
2. `Depends(verify_auth)` 解析 token/api-key → `User`
3. 校验至少一个 identifier，调用 `get_memory_instance().add(...)`
4. 成功 → `telemetry.log_dashboard_nudge_once`；异常 → `_client_error`（4xx）或 `upstream_error`（500）
5. middleware `finally` 用 `run_in_executor` 异步落 `RequestLog`

#### 关键模式
- **无 lifespan**：`initialize_state` 在模块顶层同步执行（import 即初始化）
- **并发模型**：endpoint 多为 `def`（同步），FastAPI 跑线程池；middleware 是 `async`
- **config 脱敏**：`_redact_config` 递归把 SENSITIVE_CONFIG_KEYS 替换为 `"[redacted]"`
- **provider 白名单**：`BUNDLED_LLM_PROVIDERS`（openai/anthropic/gemini）限制 POST `/configure`

---

### 1.7 `server/auth.py` (220 行) — JWT + API key 双轨认证

**图谱**: `file:server/auth.py` · layer: FastAPI 自托管 Server · complexity=complex

#### 角色定位
**三轨认证真相源**：① `Authorization: Bearer <jwt>`；② `X-API-Key: <key>`（分"等于 `ADMIN_API_KEY` env"和"匹配库内 hash"两种）；③ `AUTH_DISABLED=true` 直接放行。

#### 核心结构
- **密码**：`CryptContext(schemes=["bcrypt"])`，`dummy_verify_password()` 防 email 枚举 timing attack
- **API key**：`generate_api_key()` 返回 `(full_key="m0sk_...", prefix, bcrypt_hash)`，prefix 预筛候选
- **JWT**：HS256，access 30 分钟 / refresh 30 天，refresh jti 落库
- **依赖链**：`verify_auth` → `require_auth` → `require_admin`

#### refresh 单次消费
`consume_refresh_jti` 用 `UPDATE ... WHERE used_at IS NULL AND expires_at > now` 的 `rowcount==0` 判定失败，关闭 read-check-write 重放竞态。

#### Bootstrap admin
空库 + `ADMIN_API_KEY`/`AUTH_DISABLED` 时，`require_admin` 返回内存常量 `_BOOTSTRAP_ADMIN`（`uuid(int=0)`）。

---

### 1.8 `skills/mem0/SKILL.md` (193 行) — AI agent 主 skill

**图谱**: `document:skills/mem0/SKILL.md` · layer: AI Agent Skill 体系 · complexity=complex

#### 角色定位
装上插件后**永远在 LLM context**。作用：① frontmatter `description` 是触发判别器；② 正文给出最小可用安装→初始化→CRUD 路径；③ 路由器，把深度内容延迟加载到 9 个子文件。

#### 结构
- **YAML frontmatter**：`name`、`description`（TRIGGER / DO-NOT-TRIGGER 正反例）、`version: 3.0.0`、compatibility（Python 3.10+/Node 18+）
- **Step 1–3**：安装认证 → 初始化 client → 核心 CRUD（Python+TS 并列）
- **Common integration pattern**：retrieve → generate → store 三段式 chat 函数模板
- **References 表**：9 个子文件（quickstart/sdk-guide/api-reference/architecture/features/integration-patterns/use-cases + python.md/node.md/differences.md）

#### 关键模式
- **always-on + lazy-load 双层**：主文件薄（~190 行）、深度下沉到子文件——context 预算管理标准做法
- **正负触发器**：`DO NOT TRIGGER when: ... CLI ... Vercel AI SDK ...` 划清 sibling skill 领地
- **双向互链**：3 个 skill（mem0 / mem0-cli / mem0-vercel-ai-sdk）显式声明依赖

---

### 1.9 `integrations/openclaw/index.ts` (1059 行) — OpenClaw 插件主入口

**图谱**: `file:integrations/openclaw/index.ts` · layer: Agent & Editor 集成 · complexity=complex · in_edges=2 · out_edges=18

#### 角色定位
通过 `definePluginEntry({ id: "openclaw-mem0", register(api) })` 注册 Mem0 记忆后端，装配 **8 个工具**（memory_search/add/get/list/update/delete + event_list/event_status），CLI 命令，以及两条互斥的生命周期 hook 链。

#### 核心结构
`register(api)` 有三层早退守卫：① cli-metadata 模式只注册元数据；② `needsSetup` 只暴露 `init` 命令；③ 正常路径：`createProvider` → 双模式分叉（`PlatformBackend` / `providerToBackend` adapter for OSS）→ 顺序注册 Public Artifacts → Tools → CLI → Hooks → Service。

**registerHooks（占 62%）** 包含两条分支：
- **Skills Mode**：`before_prompt_build` 返回 `{ prependSystemContext, prependContext }` 双通道——前者可缓存（无每轮成本），后者动态 recall。recall 三档 strategy：always / smart(默认) / manual。内嵌 **auto-dream**（记忆整理）
- **Legacy Mode**：`autoRecall` 在 prompt 前注入 `<relevant-memories>` 块（动态阈值丢弃低于 top score 50% 的结果），`autoCapture` 在 agent_end 异步提取

#### 关键模式
1. **Provider/Backend 双抽象**：统一 Platform/OSS 的 search/add/getAll 签名
2. **Per-agent isolation**：sessionKey 正则派生命名空间
3. **Trigger 过滤**：排除 cron/heartbeat
4. **Session-keyed dream lock**：只允许触发的 session 完成 dream

---

### 1.10 `integrations/vercel-ai-sdk/src/mem0-generic-language-model.ts` (170 行) — LanguageModelV3 实现

**图谱**: `file:integrations/vercel-ai-sdk/src/mem0-generic-language-model.ts` · layer: Agent & Editor 集成 · complexity=complex

#### 角色定位
实现 Vercel AI SDK 的 `LanguageModelV3` 接口（`specificationVersion = "v3"`），作为**透明代理**包裹真实 LLM。在每次 `doGenerate` / `doStream` 前自动执行记忆的写入 + 检索 + 注入，让上层 `generateText` / `streamText` 无感知地获得记忆能力。

#### 核心流程
**`processMemories`（private 方法）** 是唯一的核心逻辑：
1. `addMemories` — **先写**（await）
2. `getMemories` — 用 prompt 检索
3. 构造 system prompt（"These are the memories I have stored…"）
4. **浅拷贝** prompt 数组（防 retry 修改），`unshift` 注入记忆 system message

**doGenerate** → `processMemories` → 底层 LLM → 追加 `LanguageModelV3Source`（携带 `providerMetadata.mem0.memories`）。
**doStream** → 同流程但不注入 source（已知不对称）。

#### 关键模式
1. **先写后读**（与 OpenClaw 异步不同——这里同步阻塞）
2. **装饰器模式**：完全委托 `Mem0ClassSelector`（支持 openai/anthropic/cohere/groq/google/gemini）
3. **Source 透明度**：通过 `LanguageModelV3Source` 暴露使用了哪些记忆
4. **容错降级**：所有 Mem0 调用 try/catch，失败返回空记忆

---

### 1.11 `integrations/n8n-nodes-mem0/nodes/Mem0/Mem0.node.ts` (626 行) — n8n 节点

**图谱**: `file:integrations/n8n-nodes-mem0/nodes/Mem0/Mem0.node.ts` · layer: Agent & Editor 集成 · complexity=complex

#### 角色定位
n8n 工作流中的记忆操作节点。通过 `INodeType` 暴露 6 个 operation（Add/Search/Get Many/Get/Update/Delete），直接调 Mem0 REST API。`usableAsTool: true` 可被 n8n AI Agent 节点作为工具使用。

#### 核心结构
**`description`（59%）** 是声明式 UI：`properties` 数组用 `displayOptions.show` 控制 operation 条件可见。
**`execute`（命令式分发器）**：内部 `request` helper 封装 `httpRequestWithAuthentication`，自动注入 `qs: { source: 'N8N' }`。

| Operation | HTTP | 端点 |
|-----------|------|------|
| Add | POST | `/v3/memories/add/`（支持 `waitForCompletion` 轮询） |
| Search | POST | `/v3/memories/search/` |
| Get Many | POST | `/v3/memories/`（分页，returnAll 上限 10000 页） |
| Get/Update/Delete | GET/PUT/DELETE | `/v1/memories/{id}/`（注意：v1 端点） |

#### 关键模式
1. **声明式 UI + 命令式逻辑分离**
2. **异步轮询**：`pollEvent` GET `/v1/event/{id}/` 每 1500ms × 40 次（~60s）
3. **Entity filter 组合**：`buildEntityFilters` 自动生成 `OR` 子句
4. **continueOnFail**：失败 push error 而非抛异常

---

## 2. ⭐ 单标记 11 个文件（重要）

### `mem0/configs/base.py` [moderate]
**MemoryConfig** Pydantic 主模型（聚合 vector_store/llm/embedder/reranker/history_db_path/version）。所有配置入口，April 2026 重构后 graph 字段已移除。

### `mem0/utils/factory.py` [moderate]
**Factory 工厂模式中心**：`LlmFactory`/`EmbedderFactory`/`VectorStoreFactory`/`RerankerFactory` 按 config 字符串实例化对应 provider，支持任意组合。

### `integrations/pi-agent-plugin/src/entry.ts` [complex]
插件默认导出入口 `mem0Extension(pi)`：加载配置、创建 MemoryClient，注册 tool/commands/auto-capture，绑定 session lifecycle。

### `integrations/zapier-mem0/src/index.ts` [simple]
Zapier Platform CLI app 主入口（33 行）。组装 authentication、middleware、creates（add/delete memory）、triggers、searches。

### `skills/mem0-cli/SKILL.md` [complex]
mem0-cli skill 主入口：终端命令行使用指南（mem0 add/search/list/init/config 等），Node 与 Python 双实现共享同一规范。

### `skills/mem0-vercel-ai-sdk/SKILL.md` [complex]
`@mem0/vercel-ai-provider` 的 `createMem0` wrapped model 与 standalone 用法指南。

### `skills/mem0-test-integration/SKILL.md` [complex]
**Pipeline skill**：验证 `/mem0-integrate` 的产出，在同一分支运行原生测试套件（flag 关闭 → pre-existing failures baseline → flag 开启 → 新测试必须通过）。

### `docs/docs.json` [moderate]
Mintlify 站点配置：导航结构、主题色、footer、contextual 集成、redirects。整个文档站 247 mdx 的目录骨架。

### `docs/openapi.json` [complex]
Mem0 Platform REST API 的 OpenAPI 规范（paths/security/components），API 参考页数据源。

### `CLAUDE.md` [complex]
Claude Code 专用的项目导览文档（与 AGENTS.md 高度同步），为 Claude 提供 monorepo 的完整结构与工作流。

### `mem0/memory/main.py` ⭐（已在 §1.1 详述）

---

## 3. 🔥 单标记 46 个文件（复杂热点）

### Python SDK 核心引擎（2）

#### `mem0/memory/notices.py` (1582 行)
OSS 运行时 notice 系统。基于 PostHog feature flag 的 first_run/temporal/decay/scale_threshold/performance_slow_query 五类 notice，引导用户从 OSS 升级到 Platform。

#### `mem0/memory/utils.py`
memory 工具函数集：消息解析、JSON 抽取/修复、code block 剥离、配置安全深拷贝、遥测过滤。

### Python SDK Provider 抽象（7）

| 文件 | 行数 | 说明 |
|------|------|------|
| `mem0/llms/aws_bedrock.py` | 713 | 最大 LLM 适配器；extract_provider 支持 OpenAI/Anthropic/Meta/Cohere 多 provider bedrock 调用 |
| `mem0/llms/ollama.py` | 144 | 本地 Ollama 模型适配器 |
| `mem0/vector_stores/databricks.py` | 881 | 最大 vector store；Databricks Mosaic AI Vector Search |
| `mem0/vector_stores/oracledb.py` | 602 | Oracle AI Vector Search；复杂 JSON-path filter 翻译 |
| `mem0/vector_stores/neptune_analytics.py` | 535 | AWS Neptune；Cypher 查询 |
| `mem0/vector_stores/cassandra.py` | 503 | Apache Cassandra / Astra DB；SAI 向量索引 |
| `mem0/vector_stores/azure_mysql.py` | 555 | Azure MySQL；防 SQL 注入 |

### Python SDK 工具模块（1）

#### `mem0/utils/entity_extraction.py`
`_EntityCandidate` 数据结构 + `extract_entities`/`extract_entities_batch`，用 LLM 从文本抽取并去重/归一实体。

### Python Hosted Platform Client（1）

#### `mem0/client/project.py` (944 行)
Hosted Platform 项目管理：`ProjectConfig`、`BaseProject`/`Project`/`AsyncProject`。`update` 含 decay 配置。

### TypeScript SDK（5）

| 文件 | 行数 | 说明 |
|------|------|------|
| `mem0-ts/src/oss/src/utils/entity_extraction.ts` | 828 | 最大 utils；多策略文本实体提取（引号/大写/NLP/正则/metric-list） |
| `mem0-ts/src/oss/src/utils/notices.ts` | 1434 | notice 系统的 TS 移植 |
| `mem0-ts/src/oss/src/prompts/index.ts` | 1042 | Prompt 模板中心（FactRetrievalSchema/MemoryUpdateSchema Zod + ADDITIVE_EXTRACTION_PROMPT） |
| `mem0-ts/src/oss/src/vector_stores/databricks.ts` | **1627** | **全仓最大文件**；Databricks Vector Search + SQL Warehouse |
| `mem0-ts/src/oss/src/vector_stores/neptune_analytics.ts` | 1120 | Neptune；Gremlin 查询 |

### Server Dashboard（5）

| 文件 | 行数 | 说明 |
|------|------|------|
| `server/dashboard/src/app/setup/page.tsx` | 763 | /setup 多步配置向导 |
| `server/dashboard/src/lib/auth.tsx` | — | AuthProvider 认证上下文（refresh/clear session） |
| `server/dashboard/src/utils/api.ts` | — | axios 客户端（401 自动 refresh） |
| `server/dashboard/src/middleware.ts` | — | Next.js 路由守卫（access cookie 校验） |
| `server/dashboard/src/middleware.ts`（重复条目） | — | （ONBOARDING 中重复引用） |

### FastAPI Server（1）

#### `server/server_state.py`
进程内全局状态：线程安全持有 MemoryConfig + Memory 单例（`RLock` 保护），支持从 Settings 表加载覆盖、热更新后重建实例。

### 双 CLI（2）

| 文件 | 行数 | 说明 |
|------|------|------|
| `cli/python/src/mem0_cli/commands/memory.py` | 718 | 记忆命令层（cmd_add/cmd_search/cmd_get/cmd_list/cmd_update/cmd_delete/cmd_delete_all） |
| `cli/python/src/mem0_cli/commands/init_cmd.py` | 566 | init 交互式配置向导（最长命令文件）：API key + 校验 + 邮箱验证码 + 写配置 + agent_signal |

### Agent & Editor 集成（15）

#### mem0-plugin（8 个 lifecycle hooks）
| 脚本 | 触发点 | 行数 | 说明 |
|------|--------|------|------|
| `scripts/on_session_start.sh` | SessionStart | 199 | 解析身份、注入状态 banner、自动导入项目文件、后台配置 |
| `scripts/on_user_prompt.sh` | UserPromptSubmit | 228 | 检测错误/路径/恢复/记住意图，预取记忆；每 3 条消息触发后台 auto-capture |
| `scripts/enforce_metadata_defaults.sh` | PreToolUse | 218 | 拦截 MCP add_memory/search_memories，注入 user_id/app_id/session_id |
| `scripts/capture_session_summary.py` | Stop | — | 抽取最新 assistant 消息与已触及文件，run_id 去重存储 |
| `scripts/auto_import.py` | SessionStart | — | 导入 CLAUDE.md/AGENTS.md/.cursorrules/.windsurfrules/mem0.md |
| `scripts/import_competing_tools.py` | — | — | 从 cursorrules/copilot/cline/continue 导入 |
| `scripts/on_pre_compact.py` | PreCompact/Stop | — | 安全网：抽取结构化 session state |
| `.opencode-plugin/opencode-mem0.ts` | — | 1000 | OpenCode 插件主入口；9 个 MCP 工具 |

#### OpenClaw（4）
| 文件 | 行数 | 说明 |
|------|------|------|
| `cli/commands.ts` | 1872 | CLI 子命令注册（add/search/get/list/update/delete/import/init/status/config/...） |
| `providers.ts` | 641 | createProvider：PlatformBackend 或 OSS 后端 → Mem0Provider 包装 |
| `recall.ts` | — | token 预算化、分类排序召回引擎（identity 优先） |
| `skill-loader.ts` | 693 | skill 加载器：frontmatter 解析 + domain overlay 合并 |

#### Pi Agent（2）
- `src/commands.ts` — 注册 8 个斜杠命令（mem0-remember/forget/search/tour/dream/pin/scope/status）
- `src/memory/tools.ts` — 注册 mem0_memory 工具（search/add/get_all/update/delete/delete_all）

### 示例项目（5）

| 文件 | 说明 |
|------|------|
| `examples/mem0-demo/app/api/chat/route.ts` | Edge API：getMemories → streamText → addMemories 异步存储 |
| `examples/multimodal-demo/src/hooks/useChat.ts` | 聊天 hook：MemoryClient.add/getAll + OpenAI 流式，支持图片 |
| `examples/vercel-ai-sdk-chat-app/src/hooks/useChat.ts` | 同上，Vercel AI provider 版 |
| `examples/yt-assistant-chrome/src/content.js` (657 行) | YouTube 助手内容脚本：字幕 + 注入聊天面板 + MemoryClient |
| `examples/nemoclaw/setup-mem0-nemoclaw.sh` (864 行) | NemoClaw + OpenClaw 一键安装脚本 |

### CI/CD（2）

- `scripts/oss-to-platform-migrate.sh` — 迁移脚本：OSS 自托管导出 → 批量灌入 Platform API
- `scripts/llms-txt-ignore.txt` — llms.txt 覆盖率检查的忽略前缀清单

---

## 4. 普通文件 141 个（按层批量解释）

### Layer 1 — Python SDK 核心引擎（4）
- `mem0/memory/base.py` [simple] — `MemoryBase` ABC，声明 get/get_all/update/delete/history 五个抽象方法
- `mem0/memory/telemetry.py` [moderate] — `AnonymousTelemetry` PostHog 单例，可由环境变量禁用
- `mem0/memory/storage.py` [moderate] — `SQLiteManager` 持久化变更历史与运行状态，命名空间隔离 KV
- `mem0/memory/setup.py` [moderate] — 启动期配置：创建 `~/.mem0`，原子写 `config.json`

### Layer 2 — Python SDK Provider 抽象（33）

**5 个抽象基类**（不含 aws_bedrock.py 等 🔥 已列）：
- `mem0/llms/base.py` [moderate, 170 行] — `LLMBase`：统一 `generate_response`，reasoning/GPT-5 探测
- `mem0/embeddings/base.py` [simple] — `EmbeddingBase`：embed / embed_batch
- `mem0/vector_stores/base.py` [moderate, 100 行] — `VectorStoreBase`：create_col/insert/search/delete/update/get/list_cols/delete_col/reset
- `mem0/reranker/base.py` [simple] — `BaseReranker`：rerank

**LLM providers（11 个）**：
- `mem0/llms/openai.py` [simple] — gpt-5-mini 默认，支持 OpenRouter/自定义 base_url
- `mem0/llms/anthropic.py` [moderate] — Claude sonnet-4-6 默认，转 Mem0 messages ↔ Anthropic system blocks
- `mem0/llms/gemini.py` [moderate] — Gemini generate_content API + tool/function call
- `mem0/llms/vllm.py` [simple] — vLLM 自托管
- `mem0/llms/litellm.py` [simple, 90 行] — litellm.completion 统一 100+ 模型
- `mem0/llms/xai.py` [simple] — xAI Grok
- `mem0/llms/langchain.py` [simple, 97 行] — 包任意 LangChain ChatModel 成 LLMBase

**Embedder providers（6 个）**：
- `mem0/embeddings/openai.py` [moderate] — reference 实现，批量 + encoding_format
- `mem0/embeddings/huggingface.py` [moderate] — SentenceTransformer 或 inference API
- `mem0/embeddings/gemini.py` [moderate] — 批量 >100 自动分块
- `mem0/embeddings/aws_bedrock.py` [moderate] — Titan 系列 + L2 归一化
- `mem0/embeddings/vertexai.py` [moderate] — GCPAuthenticator + memory_action
- `mem0/embeddings/ollama.py` [moderate] — 自动归一化模型名 + 确保已拉取

**VectorStore providers（13 个）**：
- `mem0/vector_stores/qdrant.py` [complex] — 本地/远程、原生 sparse vector + keyword_search
- `mem0/vector_stores/pinecone.py` [moderate, 439 行] — serverless/pod、namespace、metadata filter
- `mem0/vector_stores/chroma.py` [moderate, 364 行] — 嵌入式，常用于原型
- `mem0/vector_stores/pgvector.py` [complex] — PostgreSQL + HNSW/IVFFlat、SQLAlchemy
- `mem0/vector_stores/faiss.py` [complex] — SafeUnpickler 安全反序列化、docstore
- `mem0/vector_stores/redis.py` [moderate, 367 行] — RediSearch HNSW + tag filter
- `mem0/vector_stores/elasticsearch.py` [moderate] — kNN + 全文混合
- `mem0/vector_stores/milvus.py` [moderate, 374 行] — IVF_FLAT/HNSW + partition
- `mem0/vector_stores/weaviate.py` [moderate] — Weaviate
- `mem0/vector_stores/mongodb.py` [moderate, 425 行] — Atlas $vectorSearch 聚合管道
- `mem0/vector_stores/supabase.py` [moderate] — Supabase pgvector 托管

**Reranker providers（5 个）**：
- `mem0/reranker/cohere_reranker.py` [moderate] — Cohere Rerank API，失败回退原序
- `mem0/reranker/huggingface_reranker.py` [moderate] — 本地 cross-encoder + sigmoid
- `mem0/reranker/llm_reranker.py` [moderate] — LLM 打分（0-1）
- `mem0/reranker/sentence_transformer_reranker.py` [moderate] — 本地 bi-encoder 相似度
- `mem0/reranker/zero_entropy_reranker.py` [moderate] — Zero Entropy API

### Layer 3 — Python SDK 配置系统（4）
- `mem0/configs/prompts.py` [moderate, 1062 行] — LLM prompt 常量库（FACT_RETRIEVAL_PROMPT、ADDITIVE_EXTRACTION_PROMPT、PROCEDURAL_MEMORY_SYSTEM_PROMPT 等）
- `mem0/configs/enums.py` [simple] — `MemoryType` 枚举（PROCEDURAL 显式处理）
- `mem0/configs/llms/azure.py` [simple] — Azure OpenAI 配置
- `mem0/exceptions.py` [moderate, 484 行] — 结构化异常体系（MemoryError 基类 + 13 个子类）

### Layer 4 — Python SDK 工具模块（5）
- `mem0/utils/scoring.py` [moderate] — **多信号融合**：BM25 参数、分数归一化、score_and_rank（vector + bm25 + entity 加权）
- `mem0/utils/lemmatization.py` [simple] — `lemmatize_for_bm25`：词形归一化提升召回
- `mem0/utils/http.py` [simple] — HTTP 客户端工厂，按 proxy 配置构造 httpx.Client
- `mem0/utils/gcp_auth.py` [moderate] — GCP ADC / Vertex AI / GenAI Client 三入口
- `mem0/utils/spacy_models.py` [moderate] — spaCy NLP 模型懒加载缓存

### Layer 5 — Python Hosted Platform Client（4）
- `mem0/__init__.py` [simple] — 包入口，importlib.metadata 读版本，导出 Memory/AsyncMemory + MemoryClient/AsyncMemoryClient
- `mem0/proxy/main.py` [moderate] — OpenAI 兼容 HTTP proxy（Mem0/Chat/Completions 命名空间）
- `mem0/client/types.py` [moderate] — Pydantic typed options（AddMemoryOptions/SearchMemoryOptions 等）
- `mem0/client/utils.py` [moderate] — `api_error_handler` 同步/异步双版本装饰器

### Layer 6 — TypeScript SDK（9）
- `mem0-ts/src/oss/src/utils/factory.ts` [complex, 297 行] — 4 个 Provider 工厂
- `mem0-ts/src/oss/src/types/index.ts` [moderate, 262 行] — Zod schema 类型系统（替代 Pydantic）
- `mem0-ts/src/oss/src/llms/aws_bedrock.ts` [complex, 294 行] — Converse API
- `mem0-ts/src/oss/src/embeddings/vertexai.ts` [complex, 251 行] — 服务账号/凭证 JSON
- `mem0-ts/src/oss/src/vector_stores/memory.ts` [complex, 491 行] — **默认 store**：内存+SQLite + cosine + BM25
- `mem0-ts/src/client/config.ts` [moderate] — 读写 `~/.mem0/config.json`，PostHog distinct_id
- `mem0-ts/src/common/exceptions.ts` [moderate] — 异常类镜像 Python

### Layer 7 — Server Dashboard（4）
- `server/dashboard/src/hooks/use-api-query.ts` [complex] — 通用数据拉取 hook，并发去重（useRef 防竞态）
- `server/dashboard/src/app/api/auth/refresh/route.ts` [complex] — Next.js Route Handler，POST/PUT/DELETE 代理 /auth/refresh
- `server/dashboard/src/components/ui/sidebar.tsx` [complex, 274 行] — shadcn/ui 侧边栏复合组件
- `server/dashboard/src/components/shared/data-table.tsx` [complex] — 通用数据表格，自定义列渲染

### Layer 8 — FastAPI Server（13）
- `server/db.py` [simple] — SQLAlchemy 引擎 + SessionLocal + declarative Base + get_db
- `server/models.py` [moderate] — 5 张 ORM 表（User/APIKey/RequestLog/RefreshTokenJti/Settings）
- `server/schemas.py` [simple] — MessageResponse 通用响应
- `server/rate_limit.py` [simple] — slowapi Limiter
- `server/routers/api_keys.py` [moderate] — admin CRUD API key（明文仅返一次）
- `server/routers/auth.py` [complex] — register/login/refresh/me/change-password/onboarding-complete
- `server/routers/entities.py` [moderate] — /entities 列出与删除
- `server/routers/requests.py` [simple] — /requests 分页审计日志
- `server/docker-compose.yaml` [service] — FastAPI + PostgreSQL/pgvector + mem0-dashboard 三服务
- `server/requirements.txt` [document] — Python 运行时依赖
- `server/init-db.sh` [config] — Postgres 初始化脚本

### Layer 9 — 双 CLI（11）

**Python CLI**：
- `cli/python/src/mem0_cli/app.py` [complex, 1416 行] — Typer app 主入口
- `cli/python/src/mem0_cli/backend/platform.py` [complex, 420 行] — PlatformBackend httpx 客户端
- `cli/python/src/mem0_cli/output.py` [complex, 394 行] — Rich 渲染层
- `cli/python/src/mem0_cli/backend/base.py` [moderate] — Backend ABC
- `cli/python/src/mem0_cli/state.py` [moderate, 45 行] — 进程内状态
- `cli/python/tests/test_commands.py` [complex, 1556 行] — 最大测试文件

**Node CLI**：
- `cli/node/src/index.ts` [complex, 932 行] — Commander program 主入口

**统一规范**：
- `cli/CLI_SPECIFICATION.md` [complex, 1613 行] — 双 CLI 共用规范（最长文档）
- `cli/cli-spec.json` [complex, 563 行] — 机器可读命令规范（option-parity 权威源）

### Layer 10 — Agent & Editor 集成（12）

**mem0-plugin**：
- `integrations/mem0-plugin/scripts/auto_capture.py` [moderate] — UserPromptSubmit 后台 hook（每 3 条）
- `integrations/mem0-plugin/plugin.json` [simple] — Antigravity 插件 manifest（v0.1.6）
- `integrations/mem0-plugin/mcp_config.json` [simple] — 通用 MCP server 配置（指向 mcp.mem0.ai）
- `integrations/mem0-plugin/hooks/hooks.json` [complex, 126 行] — Claude Code hooks manifest
- `integrations/mem0-plugin/hooks/codex-hooks.json` [complex, 104 行] — Codex hooks（MEM0_PLATFORM=codex）
- `integrations/mem0-plugin/.opencode-plugin/dream.ts` [complex, 225 行] — Dream 记忆巩固模块
- `integrations/mem0-plugin/skills/mem0/SKILL.md` [moderate] — 嵌套 mem0 skill
- `integrations/openclaw/openclaw.plugin.json` [complex, 319 行] — manifest（kind=memory，8 tools）
- `integrations/vercel-ai-sdk/src/index.ts` [simple] — 包入口 barrel
- `integrations/vercel-ai-sdk/src/mem0-utils.ts` [complex] — Mem0 REST API 封装 + 多模态转换
- `integrations/pi-agent-plugin/src/telemetry.ts` [complex] — PostHog 批量缓冲（5s 或 10 条 flush）
- `integrations/zapier-mem0/src/creates/add_memory.ts` [complex, 168 行] — Zapier "Create Memory" trigger

### Layer 11 — AI Agent Skill 体系（4）
- `skills/mem0/SKILL.md` ⭐🔥（已在 §1.8 详述）
- `skills/mem0-integrate/SKILL.md` [complex] — Pipeline skill：goal-driven TDD 流程将 Mem0 接入已有仓库（10 步管线）
- `skills/mem0-oss-to-platform/SKILL.md` [complex] — Pipeline skill：OSS self-hosted → Platform 迁移
- `skills/mem0/references/api-reference.md` [moderate] — Platform REST API 参考（**注**：ONBOARDING 误写为 `api.md`）

### Layer 12 — Mintlify 文档站（3）
- `docs/llms.txt` [simple] — 面向 LLM 的文档索引（按 Platform/OSS 分类）

### Layer 13 — 示例项目（10）
- `examples/mem0-demo/components/assistant-ui/thread.tsx` [complex, 561 行] — 对话线程组件
- `examples/multimodal-demo/src/contexts/GlobalContext.tsx` [complex] — 全局状态 Provider
- `examples/vercel-ai-sdk-chat-app/src/contexts/GlobalContext.tsx` [complex] — 全局状态 Provider（Vercel 版）
- `examples/yt-assistant-chrome/src/background.js` [complex] — Service Worker
- `examples/yt-assistant-chrome/src/options.js` [complex, 452 行] — 选项页
- `examples/nemoclaw/install-mem0-plugin.sh` [complex, 419 行] — Mem0 plugin 安装子脚本
- `examples/multiagents/llamaindex_learning_system.py` [class, complex] — TutorAgent + PracticeAgent 通过 Mem0Memory 共享学生记忆
- `examples/openai-inbuilt-tools/index.js` [function] — Mem0 对 OpenAI Responses API 的影响演示
- `examples/notebooks/mem0-autogen.ipynb` [complex, 1219 行] — Mem0 + AutoGen 多 Agent
- `examples/misc/diet_assistant_voice_cartesia.py` [example] — Mem0 + Cartesia 语音饮食助手

### Layer 14 — Python SDK 测试套件（15）
- `tests/test_main.py` [moderate] — 参数校验测试（entity_id、search limit/threshold）
- `tests/test_client.py` [complex] — MemoryClient 测试（typed options、filter operator、API key）
- `tests/test_server_auth.py` [complex] — JWT 认证 CRUD 流、边界、启动日志
- `tests/test_server_params.py` [complex] — FastAPI 21 类参数 schema 测试
- `tests/test_proxy.py` [moderate] — OpenAI 兼容 proxy 行为
- `tests/test_telemetry.py` [complex] — AnonymousTelemetry：禁用/启用、singleton、生命周期埋点
- `tests/test_telemetry_aliasing.py` [complex] — 匿名 ID 与 email 别名归并
- `tests/test_telemetry_sampling.py` [moderate] — 采样率（parse_sample_rate、before_send）
- `tests/test_oss_to_platform_migrate.py` [complex] — 迁移脚本完整测试套件（Mock HTTP server）
- `tests/memory/test_main.py` [complex] — ADD/UPDATE 错误处理、prompt 覆盖、async 路径
- `tests/memory/test_notices.py` [complex] — notice 系统全面测试（decay/temporal/performance）
- `tests/memory/test_safe_deepcopy_config.py` [complex] — 安全拷贝测试（deny-list、Pydantic/dataclass）
- `tests/utils/test_entity_extraction.py` [moderate] — extract_entities 单条 + batch
- `tests/utils/test_lemmatization.py` [simple] — lemmatize_for_bm25 词形归一化

### Layer 15 — CI/CD + 顶层项目配置（22）

**CI/CD workflows**：
- `.github/workflows/ci-gate.yml` [complex] — **CI 单一入口**：dorny/paths_filter 检测 + 路由 reusable workflows
- `.github/workflows/release.yml` [complex] — **Release Router**：按 tag 前缀路由（v*/ts-v*/cli-v*/...）
- `.github/workflows/ci.yml` [complex] — Python SDK CI（CHANGELOG 校验、ruff + pytest on 3.10/3.11/3.12）
- `.github/workflows/cd.yml` [moderate] — Python SDK 发布（Hatch build + OIDC）
- `.github/workflows/ts-sdk-ci.yml` [complex] — TS SDK CI（pnpm + prettier + tsup + jest）
- `.github/workflows/ts-sdk-cd.yml` [moderate] — TS SDK 发布（pnpm build + npm OIDC provenance）

**顶层项目配置**：
- `README.md` [moderate] — 项目主页：benchmark 成绩、核心特性、安装、两种模式
- `AGENTS.md` [complex] — AI coding assistant 项目导览（593 行/54 节）
- `LLM.md` [complex] — LLM 全景文档（1324 行，最详尽）
- `pyproject.toml` [moderate] — mem0ai v2.0.17 hatchling 配置
- `CONTRIBUTING.md` [moderate] — 贡献指南（issue/CLA/hatch/pnpm/Conventional Commits）
- `SECURITY.md` [simple] — 安全策略（GitHub private advisory / 72h 响应）
- `.pre-commit-config.yaml` [simple] — ruff check --fix + isort（black profile）
- `marketplace.json` × 5 — 编辑器插件市场注册表（root + .claude-plugin + .cursor-plugin + .codex-plugin + .agents/plugins）
- `scripts/check-llms-txt-coverage.py` [complex] — docs/llms.txt 一致性校验
- `.understand-anything/knowledge-graph.json` — 知识图谱本体（2071 nodes / 3600 edges）

---

## 5. ONBOARDING.md 引用错误清单

| # | 错误 | 修正 |
|---|------|------|
| 1 | `api.md` | 应为 `api-reference.md`（实际路径 `skills/mem0/references/api-reference.md`） |
| 2 | `mem0.ts.types.ts` | 不存在；可能想指 `mem0-ts/src/client/telemetry.types.ts` 或 `mem0.ts` 本身 |

---

## 6. 三档阅读优先级（给赶时间的人）

### 6.1 必读 5 个（理解整个系统）
1. `mem0/memory/main.py` ⭐🔥 — Memory 引擎（3851 行，看 add 的 8 phase + search 的 9 step）
2. `AGENTS.md` / `LLM.md` — 项目导览（看一遍代替看十遍 README）
3. `skills/mem0/SKILL.md` ⭐🔥 — always-on 知识入口
4. `mem0/utils/factory.py` ⭐ — Provider 插件模式的钥匙
5. `mem0/memory/utils.py` + `mem0/utils/scoring.py` — V3 pipeline 的辅助大脑

### 6.2 二次开发再加 4 个
6. `mem0-ts/src/oss/src/memory/index.ts` ⭐🔥 — Python↔TS 同构对照
7. `mem0/memory/main.py` 的 AsyncMemory 部分 — async 路径
8. `tests/test_memory.py` ⭐🔥 — 测试是活契约
9. `cli/cli-spec.json` — 命令规范的权威源

### 6.3 自托管再加 3 个
10. `server/main.py` ⭐🔥 + `server/auth.py` ⭐🔥 — FastAPI + 三轨认证
11. `server/docker-compose.yaml` ⭐ — 三服务编排
12. `.github/workflows/ci-gate.yml` ⭐ + `release.yml` ⭐ — 11 包治理

---

## 7. 元数据附录

### 7.1 15 个架构层完整列表

| # | Layer ID | Layer Name | ONBOARDING 提及文件数 |
|---|----------|-----------|---------------------|
| 1 | layer:py-sdk-core | Python SDK 核心引擎 | 7 |
| 2 | layer:py-sdk-providers | Python SDK Provider 抽象 | 40 |
| 3 | layer:py-sdk-config | Python SDK 配置系统 | 5 |
| 4 | layer:py-sdk-utils | Python SDK 工具模块 | 7 |
| 5 | layer:py-sdk-client | Python Hosted Platform Client | 6 |
| 6 | layer:ts-sdk | TypeScript SDK（平行实现） | 14 |
| 7 | layer:server-dashboard | Server Dashboard（Next.js 前端） | 9 |
| 8 | layer:server | FastAPI 自托管 Server | 14 |
| 9 | layer:cli | 双 CLI（Python Typer + Node commander） | 13 |
| 10 | layer:integrations | Agent & Editor 集成（6 个） | 32 |
| 11 | layer:skills | AI Agent Skill 体系（6 个） | 7 |
| 12 | layer:docs | Mintlify 文档站 | 3 |
| 13 | layer:examples | 示例项目（10 个 demo） | 15 |
| 14 | layer:tests | Python SDK 测试套件 | 15 |
| 15 | layer:ci-cd-top | CI/CD + 顶层项目配置 | 22 |

### 7.2 复杂度分布（按 ONBOARDING 提及的 209 个文件）

| Complexity | Count | 占比 |
|-----------|-------|------|
| complex | ~140 | 67% |
| moderate | ~55 | 26% |
| simple | ~14 | 7% |

### 7.3 节点类型分布

| Type | Count |
|------|-------|
| file | 170 |
| document | 19 |
| config | 12 |
| pipeline | 6 |
| example | 1 |
| schema | 1 |
| service | 1 |

---

*生成方法：基于 `docs/ONBOARDING.md`（226 引用）+ `.understand-anything/knowledge-graph.json`（2071 nodes）+ 4 个 @fixer 子代理源码精读。如需对单个文件做更深解释，运行 `/understand-explain <path>`。*
