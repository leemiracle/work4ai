# A-15 `plastic-labs/honcho`（6.6K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\plastic-labs__honcho
> Python（FastAPI + SQLAlchemy async + pgvector/turbopuffer/LanceDB）｜ MIT ｜ 一句话定位："AI 的心理理论（theory of mind）引擎"——按 observer→observed 有向对建模每个用户，用辩证法 Agent（dialectic）+ 梦境巩固（dreamer）把对话蒸馏成分层观察（observation）推理树。

## 1. 架构总览（目录地图，标出核心目录的职责）

```
src/
  models.py           SQLAlchemy ORM：Workspace/Peer/Session/Message/Collection/Document/Queue
  routers/            REST API（peers/sessions/messages/conclusions/workspaces/...）
  dialectic/          心理理论查询面：DialecticAgent（core.py）+ agentic_chat（chat.py）+ prompts
  deriver/            写入管线：消息→explicit 观察（队列消费者 + prompts）
  dreamer/            离线巩固：orchestrator + specialists + surprisal + trees(RP-tree/cover/lsh)
  crud/               数据访问：representation.py(查询)/peer_card.py/message.py(混合检索)/scope.py
  vector_store/       向量后端抽象：turbopuffer.py / lancedb.py
  llm/                统一 LLM 调用层（backend/caching/executor/streaming）
  utils/
    agent_tools.py    dialectic/dreamer 共用的 17+ 工具定义与执行器（2800 行）
    representation.py 四层观察 Pydantic 模型 + allowlist 安全级
  telemetry/          Prometheus/Langfuse/Sentry 全链路观测
mcp/  sdks/（python/ts） honcho-cli/  migrations/  docker/  database/
```

核心心智模型：记忆不是扁平列表，而是 **Collection(observer, observed) → Document(level=explicit|deductive|inductive|contradiction, source_ids[])** 的推理树——每条派生观察通过 `source_ids` 指回前提观察（GIN 索引支持反查，models.py:461-466）。

## 2. 记忆机制深读（本笔记核心：theory of mind 与记忆的耦合）

### 2.1 写入/抽取管线（deriver：消息→explicit 观察）

- 触发：消息经 `queue` 表入队（`models.py:477-529`），任务类型含 dream/reconciler/scope_backfill/summary/webhook（deriver/consumer.py:29-37 的 payload 类型）；partial unique index 对 pending 的 dream/reconciler 任务按 work_unit_key 去重（models.py:515-528）。
- 消费分发：`process_item`（`deriver/consumer.py:44-70`）按 task_type 分发，reconciler 不要求 workspace（:50-66）。
- 批处理：`process_representation_tasks_batch`（`deriver/deriver.py:39-62`）：
  - 一批消息（含 interleaving 上下文）格式化为带时间戳转写（deriver.py:107-110）。
  - 单次 LLM 调用输出结构化 `PromptRepresentation`（response_model + json_mode，:149-168），重试 3 次（:156-157），Sentry 事务包裹（:38）。
  - token 核算只计入队消息（:114-124），prompt 静态部分缓存估算（deriver/prompts.py:92-116）。
  - 配置解析链 workspace→session 逐级覆盖（deriver.py:75-91）；`reasoning.enabled=False` 可整体关停（:88-89）。
- 抽取 prompt（`deriver/prompts.py:56-89`）只做一件事：**explicit 原子事实**。规则要点（原文）：
  - "Facts about the target peer that can be derived directly from their messages"（:60）
  - "Each conclusion must be self-contained with enough context"（:62）
  - "Use absolute dates/times when possible (e.g. 'June 26, 2025' not 'yesterday')"（:63）
  - 归因规则：关于目标用 peer id，目标提及他人要说清（:69）
  - 示例 `"I just turned 25" → "alice is 25 years old"`；`"I took my dog for a walk in NYC" → "alice has a dog", "alice walked her dog in NYC"`（:74-77）
  - prompt 头部注释言明演化："NO peer card instructions, NO working representation - just extract observations"（prompts.py:4-5）——早期 working representation 已剥离。
  - 支持自定义指令注入（CUSTOM INSTRUCTIONS 段，:23-37）。
- 输出 schema：`PromptRepresentation.explicit: list[ExplicitObservationBase]`，field description 强调 "direct quotes or clear paraphrases only, no interpretation or inference"（`utils/representation.py:140-156`），validator 防御 LLM 返回 null（:150-156）。
- 一次写入多集合：observers 列表参数（deriver.py:43）表明同批观察按每个 observer→observed 对分别落库——**同一事实在不同观察者视角下各有一份**。

### 2.2 存储后端与数据模型（心理理论的物理化）

**关系层**（models.py）：
- 三级命名空间：Workspace（:96-126）→ Session（:166-202，M2M 关联 peers :41-93，peer 可带 per-session configuration :59-64）→ Message（:205-269，含 `seq_in_session` 稳定序号 :227、token_count :226、GIN 全文索引 `to_tsvector('english', content)` :264-268、content ≤65535 :241）。
- **方向性记忆容器**：`Collection` 唯一键 `(observer, observed, workspace_name)`（models.py:357-362）——"alice 对 bob 的认知"与"carol 对 bob 的认知"物理隔离，这是 ToM 的第一物理化。
- **Document 四层模型**（models.py:379-473）：
  - `level ∈ explicit|deductive|inductive|contradiction`（默认 "explicit"，:386-388）
  - `times_derived`（被引用次数，:389-391）
  - `source_ids JSONB`（前提文档 ID，:393-395）+ GIN 索引（:461-466）——推理树指针
  - `session_name` 可空（:405）、软删除 `deleted_at`（:406-408）
  - HNSW 余弦索引 m=16 ef_construction=64（:452-460）
  - 向量同步状态机 `sync_state(pending/...)` + `sync_attempts`（:410-419），reconciler 补偿（consumer.py:19）
- **peer card 不建表**：存在 observer 的 `internal_metadata` JSONB 里，键 `{observed}_peer_card`（`crud/peer_card.py:96-126`）——ToM 的第二物理化：**画像属于观察者，不属于被观察者**。Dreamer 可写 (scope, observed) 卡，但 scope 永不能当 observed（peer_card.py:84-89 拒绝："No peer card is ever formed about a scope"，且缺名的 reserved scope 也拒，:81-84 注释）。写后 read-through 缓存失效（:118-120）。

**向量层**（`vector_store/__init__.py:53-80`）：
- 抽象 `VectorStore`，namespace = `{prefix}.{doc|msg}.{sha256(workspace.observer.observed)[:43]}`（:16-30 哈希工具 + :62-64 格式注释）——**向量命名空间同样按有向对哈希隔离**。
- 实现有 turbopuffer 与 LanceDB 两个后端（vector_store/turbopuffer.py、lancedb.py）。

### 2.3 检索策略（dialectic：工具调用式心理理论查询）

**入口 agentic_chat**（`dialectic/chat.py:48-120`）：
- 预检（短 DB 会话）：解析 observer/observed peer 行 + **scope 双重拒绝**——`_reject_scope_observed`（:24-45）"A scope is a silent observer...No representation of a scope exists to query"；且用**已解析的行**而非名字检查，关掉"路由检查后新建 scope"的竞态窗口（:82-88 注释）。observer 侧允许 scope——"answering from a scope's perspective is the entire point"（:30-33）。
- peer card 按配置 `configuration.peer_card.use` 取（:103-110）：observer 自己的卡 + observed 的卡（方向性连卡片获取都区分）。
- DB 会话关闭后才跑 Agent："agent runs without holding a connection"（:111）。

**DialecticAgent**（`dialectic/core.py:53-111`）不是"检索器"而是"上下文合成 Agent"：
- 系统提示（`dialectic/prompts.py:82-237`）：
  - 定位："helpful and concise context synthesis agent that answers questions about users by gathering relevant information from a memory system"（:83）
  - 方向性视角注入："You are answering queries from the perspective of {observer}'s understanding of {observed}. This is a directional query"（:50-51）
  - peer card 声明为"constructed summaries...not a separate source of truth"（:76-80）——画像与观察同源，防双真相。
- **预取（防检索稀释）**：`_prefetch_relevant_observations`（core.py:178-260）：
  - query 嵌入只算一次（:203-211），分两路搜索：explicit 一路、deductive/inductive/contradiction 一路（:215-235，注释 "two separate searches to prevent retrieval dilution"）。
  - 数量按推理档位：minimal=10、其余=25（:199-200）。
  - 派生层带 id 返回以便走 reasoning chain（:253-254）。
- **工具集**（`utils/agent_tools.py:455-824`）：
  - 读观察：`search_memory`（语义）、`get_reasoning_chain`（遍历 source_ids 推理树，:768-799）
  - 读对话：`search_messages`/`grep_messages`/`get_messages_by_date_range`/`search_messages_temporal`/`get_observation_context`/`get_recent_history`
  - 写回：`create_observations_deductive/inductive`、`update_peer_card`、`extract_preferences`、`delete_observations`
  - minimal 档裁剪（core.py:116-132）；session allowlist 下 `get_reasoning_chain` 整个移除——"chains traverse provenance across sessions, so it can't be scoped"（core.py:118-124）。
- `search_memory` 本体（agent_tools.py:1099-1156）：
  - filters 支持 `level in` / `session_name in`；底层 `crud.query_documents` 走向量库。
  - **allowlist fail-closed**：空列表直接返回空 Representation（:1130-1131）；levels 钳到 `ALLOWLIST_SAFE_LEVELS=("explicit",)`（:1132-1136）。
  - `ALLOWLIST_SAFE_LEVELS` 的理由（`utils/representation.py:10-23`）：explicit 来自单 session 的 deriver，session 章权威；dreamer 跨 session 合成却只盖一个 session 章，按 session 过滤会泄漏；"until that exists this fails closed. Tracked in DEV-2201"。
- 查询侧分层访问（`crud/representation.py`）：`_query_documents_semantic`（:384-426，带 max_distance 与 level 过滤）、`_query_documents_recent`（:428-457，created_at 降序）、`_query_documents_most_derived`（:459-494，times_derived 降序 + id 保证确定性序）。
- 提示词中的检索方法论（prompts.py:102-171）：
  - 枚举/聚合题先 grep 后语义（"START WITH GREP"、"A single search is NEVER sufficient"，:118-129）
  - 强制去重表（item/特征/来源日期三列，:136-146）与验证步骤（:131-134）
  - 更新检测动词表（"changed/rescheduled/updated/now/moved"，:188-197），新值覆盖旧值
  - 矛盾处理协议：呈现双方并反问用户（:180-186）
  - **反幻觉戒律**（:204-232）："A confident 'I don't know' is ALWAYS correct; giving a fabricated answer is ALWAYS wrong"；"The test before stating a detail: Did I find this EXACT information...or am I inferring/inventing it?"
- 推理分档：`reasoning_level` minimal→各级独立 MODEL_CONFIG/MAX_OUTPUT_TOKENS/TOOL_CHOICE/MAX_TOOL_ITERATIONS（core.py:47-50、465-473），成本分级明确。

### 2.4 遗忘·整合·演化（dreamer：睡眠巩固）

- **梦境周期**（`dreamer/orchestrator.py:71-150`）：
  1. 可选 surprisal 采样：几何惊奇度挑"异常"观察当探索提示（:87-11 docstring、:138-150 实现）；specialists 自导探索，hints 只是建议。
  2. deduction 专家：自导探索产出 deductive 观察。
  3. induction 专家：产出归纳模式。
  4. CardRefreshSpecialist 刷 peer card（:29-33）。
  - 配置门控：全局 `DREAM.ENABLED`（:99）+ workspace/session 级 `configuration.dream.enabled`（:121-125）。
- 触发阈值（`dreamer/dream_scheduler.py:257-281`）：显式观察数达 `DREAM.DOCUMENT_THRESHOLD` 才排定时 dream；**dreamer 自己的产出不计入阈值**——"would inflate the threshold and create a feedback loop"（:281）。调度器记录 trigger_reason（"document_threshold" 等）与 documents_since_last_dream，供事后审计（:301-310）。
- 层级语义：
  - explicit：deriver，单 session 权威。
  - deductive：前提+结论（`utils/representation.py:92-102` source_ids+premises+conclusion）。
  - inductive：pattern_type ∈ preference/behavior/personality/tendency/correlation + confidence ∈ high/medium/low（:104-123）。
  - contradiction：存双方原文（:126-137）。
- 重要性替代 decay：软删除 + `times_derived` 排序（crud/representation.py:459-494）——"被引用最多的观察"即系统内部的重要性信号；无显式遗忘。
- 近邻几何：RP-tree（`dreamer/trees/rptree.py:14-123`，随机投影中位切分）服务于 surprisal；另有 covertree/lsh/graph/sklearn_wrapper 多树实现。

### 2.5 注入上下文的方式（chat 即查询）

- 面向应用的入口是 `chat`：DialecticAgent 回答"关于 observed 的自然语言问题"（README.md:106 示例 `alice.chat("What learning styles does the user respond to best?")`）。
- 上下文预算双闸：
  - session 历史注入：`SESSION_HISTORY_MAX_TOKENS`（core.py:140-176，按 token 限额取近消息，拼进 system prompt 的 `<session_history>` 块，时间戳格式化）。
  - 总输入：`MAX_INPUT_TOKENS`，超限由 `hit_input_token_cap` 标记（core.py:370、514）。
- 预取观察直接拼进首条 user 消息（core.py:301-315："Use these as primary context. You may still use tools..."），Agent 仍可自主补搜。
- 输出可结构化：response_model 强制 JSON（core.py:443-517）；流式 `answer_stream` 用 `stream_final_only=True`——工具轮次不流，只流最终合成段（core.py:519-570）。
- 观测埋点贯穿：DialecticCompletedEvent 携带 iterations/tool_calls/prefetched_conclusion_count/tokens（core.py:424-441）；Prometheus 按 reasoning_level 分维度记 token（:409-421）。

## 3. 关键代码摘录

**① 方向性 Collection：ToM 的物理化**（`src/models.py:357-362`）：
```python
__table_args__ = (
    UniqueConstraint(
        "observer",
        "observed",
        "workspace_name",
    ),
    ...
```

**② 四层观察 + 推理树指针**（`src/models.py:386-395`）：
```python
level: Mapped[DocumentLevel] = mapped_column(TEXT, nullable=False, server_default="explicit")
times_derived: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
embedding: MappedColumn[Any] = mapped_column(Vector(_VECTOR_DIM), nullable=True)
source_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True, server_default=text("NULL"))
```

**③ allowlist fail-closed：只信 explicit 的 session 章**（`src/utils/representation.py:10-37`）：
```python
# Explicit conclusions come from the deriver over a single session's message
# batch, so their stamp is authoritative. Deductive/inductive conclusions are
# produced by the dreamer, which reads across *all* sessions ... Serving those
# under a session allowlist would leak conclusions synthesized from sessions
# outside it.
ALLOWLIST_SAFE_LEVELS = ("explicit",)

def allowlist_safe_levels(levels: list[str] | None) -> list[str]:
    if levels is None:
        return list(ALLOWLIST_SAFE_LEVELS)
    return [level for level in levels if level in ALLOWLIST_SAFE_LEVELS]
```

**④ peer card 挂在观察者身上**（`src/crud/peer_card.py:96-109,123-126`）：
```python
stmt = (
    update(models.Peer)
    .where(models.Peer.workspace_name == workspace_name)
    .where(models.Peer.name == observer)          # 写在 observer 行上！
    .values(internal_metadata=models.Peer.internal_metadata.op("||")(
        {construct_peer_card_label(observer=observer, observed=observed): peer_card}))
)
...
def construct_peer_card_label(*, observer: str, observed: str) -> str:
    if observer == observed: return "peer_card"
    return f"{observed}_peer_card"
```

**⑤ 反幻觉戒律（dialectic 系统提示）**（`src/dialectic/prompts.py:219-232`）：
```
3. DO NOT say "I think...", "Probably...", or similar hedges when you lack evidence.
4. A confident "I don't know" is ALWAYS correct; giving a fabricated answer is ALWAYS wrong.
...
**The test before stating a detail:** Ask yourself, "Did I find this EXACT
information in my search results, or am I inferring/inventing it?" If you're
inventing it, OMIT IT.
```

## 4. 基准/评测声明（反虚荣视角）

- README.md:22 自称 "Honcho has defined the Pareto Frontier of Agent Memory" [自封]，指向自建 evals 页（honcho.dev/evals）与博客 Benchmarking-Honcho [自封][外部页面不可复现于本仓]。
- README.md:271-273："evals span LongMemEval, LoCoMo, and other long-conversation benchmarks...reproducible results"——**仓库内无 eval 代码/脚本/数据**，结果全部外链 [不可复现]。
- 仓库内可验证的只有 pytest 单测（tests/）与 telemetry 事件（DialecticCompletedEvent 等），不构成基准。
- 可复现性评注：
  - 每次 dialectic 运行都发 DialecticCompletedEvent（core.py:424-441），带 iterations/tool_calls/prefetched_conclusion_count/tokens——生产自观测齐全，但无公开数据。
  - evals 页与博客均在仓外，数字与口径（对比基线、数据集切分）无法在本仓核验。
  - LongMemEval/LoCoMo 均为公开数据集，理论上可自行搭建对比，但 honcho 侧的运行脚本未开源于此。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）

1. **记忆按有向对 (observer, observed) 隔离**（models.py:357-362 + vector_store/__init__.py:76-80 双层同构）：
   - 同一用户在不同 Agent/同伴眼中的画像是不同集合——多 Agent 系统里"谁的记忆"比"记了什么"更关键。
   - mem0 的 user/agent 维度没有这层方向性。
2. **推理树即记忆结构**：
   - source_ids 指针 + GIN 索引 + get_reasoning_chain 工具，任何派生结论可回溯到 explicit 前提（agent_tools.py:768-799、models.py:461-466）。
   - 比 mem0 的"更新日志"更能支撑答案可信度审查。
3. **写入与巩固分离的"睡眠"模型**：
   - 在线 deriver 只做廉价的 explicit 抽取（单次 LLM 调用/批）。
   - 离线 dreamer 才做演绎/归纳/矛盾检测；以文档阈值触发、自产出不计阈值防反馈循环（dream_scheduler.py:257-281）。
4. **surprisal 采样**（orchestrator.py:138-150、surprisal.py）：
   - 用几何惊奇度挑选"值得深想"的观察，给巩固阶段定向。
   - 比全量重跑便宜，是记忆巩固的主动选择机制。
5. **session allowlist 的"级别信任"失败关闭设计**（representation.py:24-37）：
   - 只有 session 章可信的层才能被范围过滤，宁可返回空也不泄漏跨 session 结论。
   - 范围控制做到数据模型层而非查询层。
6. **矛盾与更新作为一等记忆类型**：
   - contradiction 层存双方原文（representation.py:126-137）。
   - dialectic 提示词规定"呈现双方+反问用户"（prompts.py:180-186）、更新检测动词表（:188-197）——把记忆冲突从 bug 变成交互机会。
7. **反幻觉写入系统提示的结构化协议**（prompts.py:204-232）：
   - 检索型记忆 Agent 的答案质量下界由"何时必须弃答"决定。
8. **scope 竞态防御**（dialectic/chat.py:82-88）：
   - 用已解析 DB 行而非请求名做权限判断，关掉"校验与使用之间目标被改"的窗口。

## 6. 局限与风险

- 成本结构重：一条 query = 预取 2 路向量搜索 + N 轮工具调用（最多 MAX_TOOL_ITERATIONS）+ 最终合成，全部走 LLM；minimal 档是补丁不是解。
- dreamer 的 session 章不可信问题自认未解（representation.py:20-23 "ponytail: whole-level exclusion...fails closed. Tracked in DEV-2201"）——allowlist 场景下派生记忆全部不可见。
- Document/Message content 上限 65535 字符（models.py:241、425），长文档观察需外部切分。
- 双向量后端（turbopuffer 云 / LanceDB 本地）+ pgvector 内嵌列并存（models.py:392 vs vector_store/），同步靠 reconciler 状态机补偿（models.py:296-305），一致性面多、修复路径复杂。
- peer card 存 JSONB 无模式校验、无历史版本——画像被 update_peer_card 覆盖后不可回滚（peer_card.py:55-120 无审计）。
- 抽取质量依赖目标 peer 标注：prompt 要求 LLM 正确归因"关于目标 vs 目标提及他人"（prompts.py:69），多角色对话中误归因无后验校验。

## 7. 一句话对比 mem0

mem0 回答"这个用户说过什么值得记的"，honcho 回答"在某个观察者眼中这个用户是怎样的人"——同样的消息流，mem0 存扁平 facts+更新日志，honcho 存 explicit→deductive→inductive→contradiction 四层推理树并按有向对隔离，用 dreamer 离线巩固替代 mem0 的即时 LLM 更新决策，代价是查询必须经过一次多轮 LLM 辩证合成。

## 8. 附录：关键文件钉版地图

**数据模型（src/models.py）**
- `models.py:41-93`：session_peers M2M（peer 可带 per-session configuration）
- `models.py:96-126`：Workspace（h_metadata/internal_metadata/configuration 三类 JSONB）
- `models.py:129-163`：Peer（画像宿主）
- `models.py:205-269`：Message（seq_in_session、GIN 全文索引 :264-268）
- `models.py:276-331`：MessageEmbedding（HNSW + sync_state 状态机）
- `models.py:334-375`：Collection（observer×observed×workspace 唯一键）
- `models.py:378-473`：Document（四层 level、source_ids、times_derived、双 HNSW/GIN 索引）
- `models.py:477-529`：Queue（partial unique 去重 :515-528）

**dialectic（查询面）**
- `dialectic/chat.py:24-45`：scope 拒绝（observed 侧）
- `dialectic/chat.py:48-120`：agentic_chat 预检（行级 scope 检查、peer_card.use 配置）
- `dialectic/core.py:53-111`：DialecticAgent 构造（方向性 + 双 peer card）
- `dialectic/core.py:116-132`：工具集裁剪（minimal 档、allowlist 移 reasoning chain）
- `dialectic/core.py:134-176`：session 历史按 token 预算注入
- `dialectic/core.py:178-260`：双路预取（防稀释）
- `dialectic/core.py:443-517 / 519-570`：answer / answer_stream（stream_final_only）
- `dialectic/prompts.py:82-237`：系统提示全貌（视角/工作流/矛盾/更新/弃答）

**deriver（写入面）**
- `deriver/prompts.py:40-89`：minimal_deriver_prompt（explicit 抽取规则与示例）
- `deriver/deriver.py:39-131`：批处理（时间戳转写、token 核算）
- `deriver/deriver.py:149-168`：单次 LLM 调用（response_model + 3 次重试）
- `deriver/consumer.py:44-70`：任务分发（reconciler/dream/scope_backfill/...）

**dreamer（巩固面）**
- `dreamer/orchestrator.py:71-150`：梦境周期（surprisal→deduction→induction→card refresh）
- `dreamer/dream_scheduler.py:257-310`：文档阈值触发 + 反馈环注释
- `dreamer/surprisal.py:60,165`：阈值过滤 + top N
- `dreamer/trees/rptree.py:14-123`：随机投影树（近邻几何）
- `dreamer/specialists.py`：deduction/induction/CardRefresh 三专家

**crud / vector_store / 工具**
- `crud/representation.py:384-494`：三种查询（semantic/recent/most_derived）
- `crud/peer_card.py:55-126`：peer card JSONB 写 + scope 拒绝 + 缓存失效
- `crud/message.py:649-1080`：外部/内部语义搜索、grep、时间范围（混合检索全件）
- `vector_store/__init__.py:16-30,53-80`：namespace 哈希与抽象
- `utils/agent_tools.py:455-824`：17+ 工具定义（create/update/search/grep/reasoning_chain）
- `utils/agent_tools.py:1099-1156`：search_memory（allowlist fail-closed）
- `utils/agent_tools.py:2376-2497`：get_reasoning_chain 处理器
- `utils/representation.py:10-37`：ALLOWLIST_SAFE_LEVELS 及其理由
- `utils/representation.py:88-156`：四层观察 Pydantic 模型
