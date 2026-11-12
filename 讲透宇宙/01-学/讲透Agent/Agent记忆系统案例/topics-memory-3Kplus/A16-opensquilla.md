# A-16 `opensquilla/opensquilla`（6.6K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\opensquilla__opensquilla
> Python（约 1011 个 .py，src/opensquilla 下 40+ 子包）｜自述定位：self-hosted AI 助手网关，"同样预算更高智能密度"（token 效率为其主打卖点）
> 形态：单机网关 + 多 agent + 本地 SQLite 记忆索引 + Markdown 记忆文件（MEMORY.md / memory/*.md）

## 1. 架构总览（目录地图，标出核心目录的职责）

- `src/opensquilla/memory/` — 记忆核心包（23 个文件）：
  - `store.py`（1369 行）：SQLite+FTS5+sqlite-vec 索引层；
  - `retrieval.py`：混合检索+时间衰减+MMR 后处理；
  - `sync_manager.py`（440 行）：文件→索引的六触发同步 + TTL 清扫；
  - `turn_capture.py`：回合捕获（原始审计层，不进索引）；
  - `flush.py` + `session_flush.py`（3562 行）：压缩前语义落盘（子代理蒸馏）；
  - `dream/`（11 个文件）：cron 定时证据门控记忆固化（晋升进 MEMORY.md）；
  - `profile_import/`：外部画像文件导入融合（fusion prompt 版本 profile-fusion-v3，`memory/profile_import/models.py:15`）。
- `src/opensquilla/engine/` — 回合引擎（40+ 模块）：context_budget（预算协调）、compaction_control（压缩后 continuation 决策）、prompt_cache_keepalive（前缀缓存保活）、tokenjuice_adapter（工具结果投影）、routing/（模型路由校准）等。
- `src/opensquilla/plugins/tokenjuice/` — 规则驱动的工具输出压缩器：
  - 130+ 条按 CLI 工具族分类的 JSON 规则（git/docker/kubectl/npm/tests/...，见 `plugins/tokenjuice/rules/` 目录清单）；
  - 衍生自上游 vincentkoc/tokenjuice（MIT，`plugins/tokenjuice/PROVENANCE.md:8`），Python reducer 自研维护（`PROVENANCE.md:14-16`）。
- `src/opensquilla/tools/builtin/memory_tools.py`（863 行）— 模型可调用的 memory_save/memory_search 工具（含注入扫描）。
- `src/opensquilla/gateway/` — boot 装配（`gateway/boot.py:3077-3103` 调 create_memory_tools）、RPC 面（rpc_memory.py：MEMORY.md 与 memory/*.md 的读写校验在 `rpc_memory.py:437`）。
- `migrations/` — yoyo 式 schema 迁移（`store.py:50-52` 提到 V004 back-fill）。
- 其他相关：`agents/`（多 agent 域与记忆目录解析，`manager.py:449-455` 引 scope 解析器）、`session/`（会话存储，可挂 SessionSourceIndexer 把会话派生内容索引进记忆库，`manager.py:552-560`）、`scheduler/`（cron，Dream 的触发方）、`observability/`、`provider/`（provider 抽象与预算证明）。

### 2.0 补充深读：session_flush 与 profile_import
- `session_flush.py`（3562 行）是 flush 计划的执行体：由 sessions.reset 与 compaction 路径调用，fire-and-forget（回执可丢弃，`session_flush.py:3-6`）；通过 `MemoryToolHandler` 协议复用 memory_save 工具落盘（`session_flush.py:37`），并解析 "Saved to <path> (N chunks indexed; integrity=...)" 回执行校验写入完整性（`session_flush.py:52-56`）；失败时写 raw fallback 档案（`.raw_fallbacks/`，`flush.py:12-13`）。
- `profile_import/`（9 文件，~220KB）是记忆的另一入口：导入外部画像文件 → LLM 融合（FUSION_SYSTEM_PROMPT，版本 profile-fusion-v3，`profile_import/prompts.py:11`）→ 事务化写入（transaction.py 28KB，支持 undo，UNDO_SYSTEM_PROMPT `prompts.py:55`）；prompt 字节配额 1MB、超限迭代裁剪（`profile_import/models.py:240,904-899`）。

## 2. 记忆机制深读

### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）
- **四条写入路径**：
  1. 模型主动调用 `memory_save`：写入 MEMORY.md 或 memory/**/*.md，路径白名单校验（`src/opensquilla/tools/builtin/memory_tools.py:125-133`），写入后同事务内联 TTL 清扫（`memory_tools.py:81-105`）；
  2. 回合自动捕获 `TurnCaptureService.capture_turn`：默认只存 user 侧、单条截断 2000 字符（`src/opensquilla/memory/turn_capture.py:62-76`），落到私有 state `turns/<session-slug>/<date>.md`（含分卷滚动：单文件超 50K 字符开 part002，`turn_capture.py:78-95,156-191`）；
  3. session 重置/压缩前语义 flush：子代理用 prompt 从 transcript 蒸馏"值得留"的事实写入 memory/ 目录（`memory/flush.py:1` "pre-compaction save via sub-agent"；系统提示 `flush.py:18-25`，用户提示 `flush.py:27-49`）；
  4. Dream 定时固化（见 2.4）。
- **turn capture 刻意不进检索索引**："Raw turns are audit/debug state, not curated memory"（`turn_capture.py:33-37`）；旧版误放在 memory/archive/ 的 turn 文件有一次性迁移逻辑移到 state/turns（`memory/manager.py:182-236`）。
- flush prompt 保真规则（`flush.py:31-43`）：
  - 保留原子事实，足够回答后续追问；
  - 人史对话保留具体人名事件/关系/偏好/目标，禁止只留"宽泛类别摘要"；
  - 相对日期（yesterday 等）须借 `[opensquilla-message: date=...]` 源日期解析为绝对日期；
  - 每条事实附源注释 `<!-- opensquilla-source: date=YYYY-MM-DD message=N anchor=ANCHOR -->`——**事实级溯源锚点**；
  - 无话可说回 `[SILENT_REPLY_TOKEN]`（`flush.py:11`），避免无意义写入。
- flush 预算：软阈值 4000 token、强制压缩转写本 2MB、保留 token 下限 1000（`flush.py:58-60`）；raw 回退档案上限 800KB（`flush.py:12`）。
- 写入前注入扫描：`_MEMORY_THREAT_PATTERNS` 八类正则（ignore previous instructions / you are now a / system prompt override / 凭证外传 curl|wget / cat .env|credentials / authorized_keys / `<system>`）+ 不可见 Unicode（U+200B-200D/FEFF/202A-202E）阻断（`memory_tools.py:54-78`）。
- memory_search 证据注入预算：默认结果数常量、上限 20 条、证据 900 字符/条（`memory_tools.py:130-133`），查询停用词表过滤（`memory_tools.py:134-161`）。

### 2.2 存储后端与数据模型
- SQLite 单库，四张表 + 两个虚表（`src/opensquilla/memory/store.py:55-120`）：
  - `files(path PK, source, hash, mtime, size, schema_version)` — 文件级指纹（`store.py:55-64`）；
  - `chunks(id PK, path, source, start_line, end_line, hash, model, text, embedding, updated_at, schema_version)` — 行号级分块，**保留 chunk 在原 Markdown 中的行区间**（`store.py:66-80`）；
  - `embedding_cache(provider, model, provider_key, hash, embedding, dims, updated_at, UNIQUE(provider,model,provider_key,hash))` — 跨会话嵌入缓存（`store.py:82-94`）；查询侧缓存开关 `cost.query_embedding_cache`（`manager.py:508-510`）；
  - `meta(key, value)` — schema 版本等（`store.py:96-102`）；
  - `chunks_fts` FTS5 虚表，unicode61 分词，正文外字段 UNINDEXED（`store.py:104-115`）；
  - `chunks_vec` vec0 虚表（sqlite-vec 扩展，`store.py:515`）；
  - 索引 `idx_chunks_path`/`idx_chunks_source`（`store.py:117-120`）。
- **真相层是 Markdown 文件，SQLite 只是可重建的派生索引**——index_file 按 hash 跳过未变文件，重启零重嵌入开销（`sync_manager.py:108-110`）；MEMORY_SCHEMA_VERSION=1 + yoyo 迁移留位（`store.py:50-53`）。
- 记忆目录来源可选 `state`（默认）或 `workspace`（MEMORY.md 放工作区，`gateway/config.py:992`、`manager.py:515-524`）。

### 2.3 检索策略
- store.search 混合检索（`store.py:905-939`）：
  - 向量侧：sqlite-vec KNN，查询向量 L2 归一化后 blob 匹配，`WHERE v.embedding MATCH ? AND k = ?` 且模型名对齐（`store.py:941-973`）；
  - 词法侧：BM25 FTS5，rank→[0,1] 用 `1/(1+rank)`（负 rank 取反，`store.py:1364-1369`），先取 k*3 再过滤（`store.py:1001`）；无结果时降级放行 relaxed 结果并打元数据标记（`store.py:1025-1030`）；
  - 向量异常自动回落 FTS-only（`store.py:935-938`）；无嵌入 API key 时初始化即强制 FTS-only 并把权重改 0/1（`manager.py:572-575`）。
- MemoryRetriever 三层后处理（`src/opensquilla/memory/retrieval.py:184-264`）：
  1. **时间衰减**：仅对文件名带日期的 daily note 指数衰减（半衰期默认 30 天），MEMORY.md 与非日期文件视为 evergreen 不衰减（`retrieval.py:42-69`）；
  2. **来源加权**：sessions 来源 ×0.92（`retrieval.py:180`）；
  3. **可选 MMR 去冗余**：λ=0.7，token 级 Jaccard 相似度（ASCII 词 + CJK 一元+二元组，`retrieval.py:72-122`）。
- 低分但有词法保证匹配的结果不会被 min_score 误杀（relaxed/lexical guaranteed 双通道，`retrieval.py:235-245`）。
- 检索前触发"搜索时同步"：search(reason="search:{intent}") 先跑 sync_manager（`retrieval.py:191-192`）；SearchIntent 区分 TOOL/其他注入意图并写进结果元数据（`retrieval.py:262-263`）。

### 2.4 遗忘·整合·演化
- **同步触发模型**：MemorySyncManager 统一 sync() 入口，六种触发点——session-start（新 session key 首见）、search（检索前若脏）、watch（轮询 2s+防抖 1.5s）、timer（默认关）、session-delta（累计 100KB 或 50 条消息）、post-compaction（压缩后）（`sync_manager.py:46-59,66-67`、`sync_manager.py:20-36`）。
- **TTL 遗忘**：`entry_ttl_days` + `ttl_sweep_interval_minutes` 独立后台循环（与索引同步分离，`sync_manager.py:56-58`）；启动时**先清扫再索引**（"don't waste an embed pass on files we are about to delete"，`sync_manager.py:104-120`）。
- **Dream（记忆固化）**：cron 触发的"证据门控晋升"管线（`dream/runner.py:1` "evidence-gated memory consolidation"）：
  1. `.dream_cursor` 时间戳游标扫描 mtime 更新的文件（`dream/runner.py:118-144`）；
  2. 累积证据存储（出现次数 seen_count / 负向复发计数 negative_recurrence）；
  3. 确定性打分排序：阈值 0.55、负向复发≥2 淘汰、最小出现 1 次、批上限 20（`dream/runner.py:294-302`）；
  4. LLM 只做最后一步：把候选合并进 MEMORY.md，**输出限定为 upsert/merge/skip 三种 JSON 操作的 patch**（`dream/prompts.py:31-45`），patch 可带 `expected_old_text_sha256` 乐观锁与 `replaces_memory_ids` 多换一语义（`dream/prompts.py:85-98`）；
  5. 每次运行写 JSONL 回执 + MEMORY.md 备份到 `.dream_backups/`（`dream/runner.py:190-238`），dry_run/preview_mode 支持灰度（`dream/runner.py:264-267`）。
- **压缩后 continuation 状态机**：`decide_compaction_continuation` 纯函数，按 receipt_safe/prompt_changed/semantic_flush_ok/retry 六态裁决 continue/retry/degraded/blocked/failed/partial（`engine/compaction_control.py:28-89`）；语义 flush 失败但原始会话已落盘时允许降级继续（`compaction_control.py:74-79`）。
- **历史数据自愈**：legacy raw-dump 回退文件迁入 `.raw_fallbacks/` 点前缀目录防再污染检索（`manager.py:72-79,87-156`）；legacy turn 捕获档案迁出记忆区并同步删索引行（`manager.py:182-236,542-550`）。

### 2.5 注入上下文的方式与 token 效率（"同样预算更高智能密度"的真实机制）
1. **工具结果规则压缩（tokenjuice）**：
   - 130+ 条 JSON 规则按 CLI 工具族（git/docker/kubectl/npm/test/lint/cloud...）静态压缩工具输出：strip ANSI、dedupeAdjacent、跳过提示行、head/tail 截断、**正则计数器把 N 行明细折叠成 "modified file ×12" 计数**（示例 `plugins/tokenjuice/rules/git/status.json:11-53`）；
   - 零 LLM 调用、确定性；失败时 preserveOnFailure 原样保留（`engine/tokenjuice_adapter.py:42-46` "tool output must never fail an agent turn"）；
   - 适配器只在"确实变短"时接受结果（逐行相同或变长都返回 None，`tokenjuice_adapter.py:66-69`）；
   - 规则排序：generic/fallback 永远垫底、priority 降序（`plugins/tokenjuice/rules.py:64-73`）。
2. **提示缓存保活**：捕获已成功请求的 provider 可见前缀为不可变快照 `PromptCacheKeepaliveCandidate`（session_key/provider/model/messages/tools/config 五元组），供网关日后重放作辅助请求维持缓存热度；候选对象本身不改历史、无持久化（`engine/prompt_cache_keepalive.py:1-7,17-30`）——**直接省钱而非省 token**。
3. **预算证明即压缩决策**：`coordinate_provider_context_budget` 把"预算校验"与"必要压缩"合为单一决策点，产出 send/send_compacted/budget_limited/invalid_request 四态（`engine/context_budget.py:35-79`），支持保护当前用户消息与指定工具结果下标（`context_budget.py:43-44`）。
4. **辅助调用预算隔离**：Dream/flush 等辅助 LLM 调用走 `resolve_auxiliary_request_budget`/`ensure_auxiliary_text_fits` 独立预算（`dream/runner.py:59-67`），辅助用量经 `account_provider_stream` 记账、与主对话分离（`dream/runner.py:83-97`）。
5. **与记忆的连接**：
   - memory_search 证据 snippet 限 900 字符、结果上限 20 条（`memory_tools.py:131-132`）；
   - 嵌入查询缓存复用（`store.py:82-94`）；
   - **压缩前 flush 是"记忆替代上下文"**——压缩丢掉的细节先蒸馏进 memory/，之后可被检索召回，这就是 token 预算与记忆系统的真实耦合点（`flush.py:1` "pre-compaction save via sub-agent"）；
   - session-delta 同步阈值（100KB/50 条）同时控制嵌入成本（`sync_manager.py:23-24`）。

### 2.6 补充深读：retention / checkpoint / embedding
- `retention.py`（8KB）：TTL 清扫实现 `prune_expired_memory_files`——memory_save 内联调用 + MemorySyncManager 后台 sweep 双覆盖（`memory_tools.py:88-96` 注释说明两者分工：内联覆盖 plan 路径，后台覆盖其余）。
- `checkpoint.py`（11KB）：durable checkpoint sidecar（`memory/.checkpoints/**.jsonl`），路径合法性校验要求 ≥4 段且前两段必须是 memory/.checkpoints（`memory_tools.py:113-122`）——压缩/重置过程的中断恢复凭据。
- `embedding.py`（20KB）/`embedding_resolver.py`（9KB）：provider 解析链——无 API key 时回落 NullEmbeddingProvider 并强制 FTS-only（`manager.py:470-479`）；查询嵌入结果按 (provider, model, provider_key, hash) 缓存去重（`store.py:82-94`），成本项 `cost.query_embedding_cache` 默认 on（`manager.py:508-510`）。
- `embedding.py` 中 OpenAI 兼容 /api/embeddings 单 prompt 限制的历史注释（`embedding.py:216`）显示对多 provider 兼容性的细致处理。

### 2.7 数据类型与默认参数速查（`src/opensquilla/memory/types.py`）
- 默认检索参数：`DEFAULT_MEMORY_SEARCH_RESULTS = 6`、`DEFAULT_MEMORY_SEARCH_MIN_SCORE = 0.35`（`types.py:9-10`）——低门槛高召回取向。
- 双来源枚举 `MemorySource`：memory（策展记忆文件）/ sessions（会话派生索引，检索时权重 ×0.92）（`types.py:42-44`、`retrieval.py:180`）；来源过滤支持 all/memory/sessions（`types.py:47-61`）。
- 双档检索模式 `SearchMode`：hybrid / fts-only（`types.py:64-66`）。
- 检索意图 `SearchIntent`：tool（模型工具调用）/ admin（CLI 管理查询），写进结果 metadata 供归因（`types.py:69-74`、`retrieval.py:262-263`）。
- 弱匹配元数据通道：`relaxed_keyword_match` / `lexical_guarantee` 两个标记位让低于 min_score 的词法命中绕过阈值（`types.py:11-14,102-110`）——**宁可多给模型看，不让召回空手**。
- min_score 归一化钳到 [0,1]，非法输入回默认值（strict 模式才抛错，`types.py:17-39`）。

### 2.8 检索结果如何回到模型（证据预算化）
- memory_search 工具返回的不是原文全文，而是**证据预算化后的片段**：
  - `_bounded_memory_search_evidence`：先清洗，超 900 字符时做"查询居中"截取——优先保留命中词上下文，块首尾标注 "... (earlier/later lines omitted)"（`memory_tools.py:260-277`）；
  - 每条结果附分解分数 `score / vector_score / text_score`（`memory_tools.py:280-286`），模型可见检索依据。
- **容量治理 `_enforce_size_limits`**：memory/ 目录文件数超 `max_files` 上限时按 mtime FIFO 删最旧 .md（跳过策展的 MEMORY.md 与点前缀文件，`memory_tools.py:289-318`）——文件级遗忘的第三通道（TTL/衰减之外）。
- 多 agent 工具路由：store/retriever 按 agent_id 字典注册，调用时从 ToolContext contextvar 取当前 agent 选择对应实例，缺省回落 main（`memory_tools.py:321-359`）。

## 3. 关键代码摘录

**检索三层后处理管线**（`src/opensquilla/memory/retrieval.py:205-246`）：
```python
if self._temporal_decay_enabled:
    ...  # 指数衰减后重排序
filtered = [
    r for r in raw_results
    if is_searchable_source_path(r.source, str(r.path))
    and (source_filter is None or r.source == source_filter)
    and (r.score >= opts.min_score
         or is_relaxed_keyword_match(r)
         or is_lexical_guaranteed_match(r))
]
filtered.sort(key=lambda r: _rank_score(r, self._source_weights), reverse=True)
```

**Evergreen 判定 + 指数衰减**（`src/opensquilla/memory/retrieval.py:52-69`）：
```python
def _temporal_decay(score, path, mtime, half_life_days=30.0):
    if _is_evergreen(path):   # MEMORY.md 与非日期文件不衰减
        return score
    ...
    lam = math.log(2) / half_life_days
    return score * math.exp(-lam * age_days)
```

**Dream 晋升 prompt（约束为 3 种 JSON 操作）**（`src/opensquilla/memory/dream/prompts.py:32-40`）：
```python
"You are updating OpenSquilla MEMORY.md as curated long-term memory.\n"
"Return JSON only with an operations array. ...\n"
'- {"op":"upsert","candidate_ids":["..."],"section":"User Preferences",'
'"memory_id":"mem_short_stable_id","text":"- durable memory"}\n'
'- {"op":"merge",...}\n'
'- {"op":"skip","candidate_ids":["..."],"reason":"not durable"}\n'
```

**tokenjuice 计数器折叠**（`src/opensquilla/plugins/tokenjuice/rules/git/status.json:36-53`）：
```json
"counters": [
  {"name": "modified file",  "pattern": "^(?:M:|\\s*modified:|[ MTRU][MTRU]\\s+)"},
  {"name": "new file",       "pattern": "^(?:A:|\\s*new file:|A.\\s+)"},
  {"name": "untracked file", "pattern": "^(?:\\?\\?:|\\?\\?\\s+)"}]
```

**六触发统一同步入口**（`src/opensquilla/memory/sync_manager.py:46-59`）：
```python
class MemorySyncManager:
    """Manages all memory sync triggers through a unified sync() entry point.
    Trigger points:
      1. session-start  — first time a session key is seen
      2. search         — before search, if dirty
      3. watch          — file changes detected by polling
      4. timer          — periodic interval (optional, default off)
      5. session-delta  — accumulated byte/message threshold
      6. post-compaction — after context compaction
    Background TTL sweep runs as an independent loop ..."""

**压缩前 flush 系统提示（追加式、静默令牌）**（`src/opensquilla/memory/flush.py:18-25`）：
```python
FLUSH_SYSTEM_PROMPT_TEMPLATE = """\
Pre-compaction memory flush.
Store durable memories only in {relative_path} (create the memory/ directory if needed).
If {relative_path} already exists, APPEND new content only — do not overwrite existing entries.
...
If there is nothing worth storing, reply with {silent_token}.
"""
```

## 4. 基准/评测声明（反虚荣视角）
- 仓库内未见针对记忆检索质量或 token 节省率的公开基准数字/复现脚本 [不可复现]。
- tokenjuice 压缩有 fixtures 单测与打包检查（`plugins/tokenjuice/PROVENANCE.md:30-32` "Run the tokenjuice projection tests and packaging checks before release"），但无跨工具压缩率报告 [自封未给数字]。
- "同样预算更高智能密度"是产品叙述；其机制本体（规则压缩/缓存保活/预算门控）代码真实存在且工程化完整，但"更高智能"无第三方验证。
- 有 `eval/` 目录与大量 tests（memory/session flush 行为由测试钉死，`session_flush.py:4-6`），属工程自测，非学术评测。
- Dream 产出有可观测性（JSONL 回执含 provider_calls/evidence_ms/前后 sha，`dream/runner.py:197-218`），但没有公开的固化准确率/误删率统计 [自封未给数字]。
- 官方 README 多语言（de/es/fr/ja/zh-Hans）与 RELEASES/CHANGELOG 表明活跃运营，但星数与记忆能力无因果 [自封]。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **Markdown 为真相、SQLite 为可丢弃索引**：
   - 索引坏了删库重建即可，记忆本体人类可读可编辑（`store.py:55-120` 的 files/chunks 表只是派生指纹）；
   - 比 mem0 的"DB 为真相"更适合个人助手场景，也天然支持用户手工策展。
2. **chunk 带行号区间 + 事实级源注释**：
   - chunks 表存 start_line/end_line，检索结果可给 `path#L12-L30` 式引用（`store.py:1020`）；
   - flush 要求每条蒸馏事实附 `<!-- opensquilla-source: date=... message=N -->`（`flush.py:41-43`）——记忆可审计、可回溯到原对话。
3. **Dream 的"LLM 只产 patch 不产文本"**：
   - 固化决策是确定性评分（证据累积+负向复发淘汰，`dream/runner.py:294-302`）；
   - LLM 输出限定 upsert/merge/skip JSON + `expected_old_text_sha256` 乐观锁 + `replaces_memory_ids` 归并语义（`dream/prompts.py:69-98`）——把不可靠的生成约束成可校验的结构化操作。
4. **记忆与上下文预算的闭环**：
   - 压缩前必 flush（丢上下文前先蒸馏，`flush.py:1`）；压缩后 continuation 状态机裁决是否降级继续（`engine/compaction_control.py:28-89`）；
   - 检索证据限 900 字符注入（`memory_tools.py:132`）——记忆系统同时是 token 效率系统的一环。
5. **工具输出确定性压缩**（tokenjuice）：
   - 130+ 规则 + 正则计数器折叠，零 LLM 成本的上下文瘦身；
   - "确实变短才接受"的保守接受准则（`tokenjuice_adapter.py:66-69`）；
   - 可独立移植到任何 Agent 的工具层。
6. **evergreen/dated 双轨遗忘**：
   - 只对日期命名的日常笔记衰减，稳定记忆永不衰减（`retrieval.py:42-49`）；
   - 避免 mem0 式统一 decay 把"用户偏好"这类持久事实冲淡。
7. **提示缓存保活候选**（`engine/prompt_cache_keepalive.py`）：把"维持 provider 前缀缓存热度"抽象成不可变快照对象，是省钱（非省 token）维度的独特机制。

## 6. 局限与风险
- 工程债：`session_flush.py` 单文件 3562 行、`store.py` 1369 行、memory_tools.py 863 行、profile_import/service.py 68KB；flush 行为由测试钉死（"Current behavior is pinned by the memory flush tests"，`session_flush.py:4-6`），重构成本高。
- 注入扫描是正则黑名单（`memory_tools.py:54-63`），改写即可绕过；不可见字符检测只覆盖 U+200B-200D/FEFF/202A-202E 少数字符段（`memory_tools.py:65`）。
- 检索召回上限 min(200, k*10) 与 MMR 是进程内同步计算，Jaccard MMR 在大候选集上 O(n·k)（`retrieval.py:108-122`）。
- tokenjuice 规则只覆盖固定 CLI 工具族，任意长输出靠 generic/fallback 的 head/tail 截断，语义损失无度量；规则与上游 MIT 同步是长期维护负担（`PROVENANCE.md:23-32`）。
- Dream 依赖外部 LLM provider，辅助调用虽走独立预算但仍花真钱；无 provider 时固化管线静默失效。
- Windows 长路径需 `\\?\` 前缀包装（`manager.py:44-55`），跨平台 IO 细节易碎；manager 构建失败路径的逆序清理逻辑复杂（`manager.py:627-660`）。
- FIFO 容量治理只看 mtime 不看内容重要性（`memory_tools.py:289-318`），高频更新的低价值文件反而安全、冷而重要的旧文件先被删。
- relaxed/lexical 弱匹配通道（`types.py:102-110`）可能放行大量低分结果，注入预算 900 字符/条 × 20 条上限的最坏情形仍可观。

## 7. 一句话对比 mem0
mem0 把记忆当"抽取-存储-检索"的数据库问题；opensquilla 把记忆当"文件优先、索引可弃、压缩前蒸馏、规则压缩工具输出"的**个人知识工作流 + token 经济学问题**。

具体差异点：
- 存储真相：mem0=数据库 / opensquilla=Markdown 文件+可弃索引；
- 抽取：mem0=对话即时 LLM 抽取 / opensquilla=四路写入（工具直写+回合捕获+压缩前蒸馏+定时 Dream）；
- 演化：mem0=ADD/UPDATE/DELETE/NOOP 四操作 / opensquilla=Dream patch（upsert/merge/skip + sha256 乐观锁）+ TTL + 双轨衰减；
- 检索：两者混合检索相当（向量+BM25），opensquilla 多 evergreen 豁免与来源加权；
- 独有：tokenjuice 规则压缩、提示缓存保活、预算证明门控——**记忆与 token 效率一体设计**是 mem0 完全没有的维度。
