# A-10 `EverMind-AI/EverOS`（12K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\EverMind-AI__EverOS
> Python ≥3.12 / src 约 36.8k 行 / Apache-2.0 ｜ 本地优先（local-first）+ Markdown 为唯一事实源的 Agent 记忆运行时，SQLite + LanceDB 仅作派生索引

## 1. 架构总览（目录地图，标出核心目录的职责）

```
src/everos/
├─ core/persistence/          # 存储基座：markdown（frontmatter/entries/原子写）、sqlite、lancedb 三套
├─ infra/persistence/         # 业务落地：markdown/mds/（7 种记忆 kind 的 frontmatter schema）、
│                             #   lancedb/tables+repos、sqlite/tables+repos（cluster/md_change_state 等）
├─ infra/ome/                 # 自进化事件引擎：Immediate/Cron/Idle 三种触发器 + 离线策略调度
├─ memory/
│   ├─ extract/               # 写入管线：ingest → boundary 切分 → user/agent 双管线
│   ├─ strategies/            # 7 个 OME 策略：抽取原子事实/画像/技能/foresight、聚类、反思
│   ├─ reflection/            # Select→Merge→Re-extract→Deprecate 反思编排器
│   ├─ cascade/               # md 文件监听 → 增量同步 LanceDB/SQLite（watcher/scanner/worker/reconciler）
│   ├─ search/                # 检索：KEYWORD/VECTOR/HYBRID/AGENTIC 四路 + heap-expand 层级融合
│   └─ get/                   # 按 id 直取（KV 路径）
├─ service/                   # 用例层：memorize / search / get / knowledge
└─ entrypoints/               # api（FastAPI）/ cli / tui
```

核心叙事：**md 是 canonical，数据库是投影**。用户可直接手改 `.md`，`cascade` watcher 把外部编辑同步回索引（README 定位 + `src/everos/memory/cascade/watcher.py:1-12`）。

## 2. 记忆机制深读（本笔记核心，每个论断钉 `相对路径:行号`）

### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）

- 入口 `POST /api/v2/memory/add` → `ingest.process` → `_boundary.prepare_cells()`（缓冲/合并/边界切分，产出 MemCell）→ `asyncio.gather(UserMemoryPipeline, AgentMemoryPipeline)`，见 `src/everos/service/memorize.py:1-12` 的管线图与 `src/everos/service/memorize.py:45-54` 的策略导入。
- User 管线：每个 cell 先发 `UserPipelineStarted` 事件让异步策略（atomic_fact/foresight/聚类）与 Episode 抽取**并行**（`src/everos/memory/extract/pipeline/user_memory.py:90-100`）；Episode 抽取是每 cell 一次 LLM 调用（`sender_id=None` 走整段 prompt，注释明确说明比 per-user fan-out 便宜），随后按 sender 复制成多份 md（`src/everos/memory/extract/pipeline/user_memory.py:112-117`）。
- 抽取 prompt 来自可覆盖的 prompt slots（YAML）：`src/everos/config/prompt_slots/episode_extract.yaml`、`boundary_detection.yaml`，由 `src/everos/memory/extract/pipeline/user_memory.py:102` 的 `prompt_loader.load("episode_extract")` 加载。
- 真正的 LLM 抽取算法在外部包 `everalgo`（`EpisodeExtractor`/`AtomicFactExtractor`/`EpisodeReflector`），EverOS 本体只做编排——算法不在本仓库内（`src/everos/memory/extract/pipeline/user_memory.py:20-22`、`src/everos/memory/strategies/extract_atomic_facts.py:12`）。
- 7 种记忆 kind（frontmatter schema 逐一定义）：episode、atomic_fact、user_profile、foresight、knowledge_topic/document、agent_case、agent_skill，见 `src/everos/infra/persistence/markdown/mds/` 目录；agent 轨迹也走同样管线（`src/everos/memory/extract/pipeline/agent_memory.py`）。

### 2.2 存储后端与数据模型（表/集合/文件布局，原文摘录 schema）

- 文件布局（原子事实为例）：`users/<scope_id>/.atomic_facts/atomic_fact-<YYYY-MM-DD>.md`，点前缀目录对用户隐藏（"framework-internal derived md"，`src/everos/infra/persistence/markdown/mds/atomic_fact.py:1-13`）。Episode 则是可见目录 `users/<scope>/episodes/episode-<date>.md`（`src/everos/infra/persistence/markdown/mds/episode.py:2-8`）。
- 文件级 schema（YAML frontmatter，pydantic 强类型）：`type/date/entry_count/created_at/last_appended_at/deprecated_entries`，继承链 `DailyLogPathMixin + UserScopedFrontmatter`，只读绝对字段 `id/type/schema_version` + 作用域 `user_id/agent_id/track`（`src/everos/infra/persistence/markdown/mds/episode.py:23-36`、`src/everos/core/persistence/markdown/frontmatter.py:18-28`）。
- 条目级格式：HTML 注释标记的 entry 块 + "audit-form" 正文（H2 头 + `**key**: value` 内联字段 + H3 小节），**故意全字符串、类型无关**，强类型模型放在 SQLite/LanceDB 索引层（`src/everos/core/persistence/markdown/entries.py:11-49`）。
- EntryId 结构 `<prefix>_<YYYYMMDD>_<NNNN>`，8 位零填充保证字典序==数字序（`src/everos/core/persistence/markdown/entries.py:62-71`）。
- 写入语义：同目录临时文件 + `fsync` + `os.replace` 原子替换（`src/everos/core/persistence/markdown/writer.py:136-163`）；进程内 per-path asyncio.Lock 防 read-modify-write 丢更新，进程间靠 `fcntl.flock` 的 `memory_root_lock`（`src/everos/core/persistence/markdown/writer.py:14-36`）；路径穿越防御 `resolve()` 后必须落在 memory root 内（`src/everos/core/persistence/markdown/writer.py:104-134`）。
- LanceDB 7 张表与 md 一一对应（`src/everos/infra/persistence/lancedb/tables/`：atomic_fact/episode/user_profile/foresight/knowledge_topic/agent_case/agent_skill）；SQLite 侧是 cluster、md_change_state、memcell、reflection_report、unprocessed_buffer（`src/everos/infra/persistence/sqlite/tables/`）。LanceDB 版本被钉死 `>=0.34.0,<0.35.0`，注释写明 0.32-0.34 有 compaction 回归、用 `with_position=False` FTS 绕过（`pyproject.toml` 依赖注释）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）

- 四种方法 KEYWORD / VECTOR / HYBRID / AGENTIC，按 owner_type 硬分区：user→episodes(+profiles)，agent→agent_cases+agent_skills（`src/everos/memory/search/manager.py:1-26`）。
- HYBRID 默认**无 LLM 重排**：sparse(BM25)+dense → `heap_expand`，即 RRF 排定扩展优先级 + LR 校准分数（sigmoid 到 [0,1]）做 episode 与其 atomic facts 的全局 top-N 竞争，参数 `rrf_k=60, facts_per_episode=3, max_convergence_rounds=10`（`src/everos/memory/search/manager.py:14-18`、`src/everos/memory/search/hierarchy.py:48-90`）。
- 显式常数：召回池 `top_k×2`、top_k 上限 100、无限模式 cosine 阈值 0.5（注释承认参照 enterprise 的 0.6，因 LanceDB/Milvus 分布漂移放宽）、atomic fact 池 `top_k×20` 封顶 2000（注释给出实测密度"1 memcell → 1 episode + ~28 facts"）（`src/everos/memory/search/manager.py:105-128`）。
- AGENTIC 自带 cross-encoder 迭代重排环；只有 HYBRID/AGENTIC 的 top score 被认为是"校准过的"，可进入 recall_hit 阈值统计，BM25/单路向量被排除以防仪表盘虚高（`src/everos/memory/search/manager.py:146-152`）。
- `SearchManager` 只读不写（`src/everos/memory/search/manager.py:25`）。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）

- **自进化 = OME 事件引擎 + 三类触发器**：`Immediate(on=[Event])` / `Cron(expr)` / `Idle(on, event_field, idle_seconds)`（Idle 要求事件按字段分桶静默 N 秒才触发，且 scan_interval ≤ idle_seconds/2，`src/everos/infra/ome/triggers.py:21-76`）。策略用装饰器注册：`@offline_strategy(name="extract_atomic_facts", trigger=Immediate(on=[EpisodeExtracted]), max_retries=2)`（`src/everos/memory/strategies/extract_atomic_facts.py:38-43`）。
- **反思（整合）**：`ReflectionOrchestrator` 执行 Select→Merge→Re-extract→Deprecate：按聚类选碎片 episode → LLM 合并为单条高质量 episode → 写回 md 并重发 `EpisodeExtracted` 重抽原子事实 → 原件在 md frontmatter `deprecated_entries` 与 LanceDB `deprecated_by` 字段**双侧软删除**（`src/everos/memory/reflection/orchestrator.py:1-8`、`:655-829`、`:1006-1029`）。注意：**不是物理删除**，md 里仍可 grep 到被弃条目。
- 反思由 cron 策略驱动，默认 `0 2 * * 1`（每周一凌晨）且 `enabled=False` 默认关闭（`src/everos/memory/strategies/reflect_episodes.py:50-56`）；单轮上限 `_MAX_CLUSTERS_PER_RUN = 10`（`src/everos/memory/reflection/orchestrator.py:40`）。
- **外部编辑自愈（cascade）**：watchdog 监听 memory root，事件按 kind 白名单入 SQLite 队列 `md_change_state`，worker 批量（batch 50、重试 3）把 md 增量投影到 LanceDB；orchestrator 还带 optimize/prune/rebuild 心跳与 12h 全量重建扫描（`src/everos/memory/cascade/watcher.py:1-12`、`src/everos/memory/cascade/orchestrator.py:89-97`、`:41-69` 健康判定）。watcher 对 macOS FSEvents 在 `os.replace` 上的假 delete 事件做了 stat 防御，避免误清 LanceDB（`src/everos/memory/cascade/watcher.py:88-99`）。
- 无 decay/TTL：时间衰减不存在，遗忘仅靠反思合并 + deprecated 软删。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）

- 检索结果经 `shaper.reshape_hybrid_output` 整形为 `SearchEpisodeItem`（episode + 其 atomic_facts 的父子混合列表，`src/everos/memory/search/manager.py:20-23`、`src/everos/memory/search/shaper.py`）。
- 未发现显式 token 预算/裁剪逻辑——预算控制靠 `top_k`、`_AGENT_TOP_K_CAP=10`（agent 记忆 payload 重，无限模式封顶 10 条防 rerank 上下文爆炸，`src/everos/memory/search/manager.py:108-111`）。注入拼装留给调用方（API 返回 DTO）。
- 侧通道：检索时顺带把未处理缓冲（unprocessed buffer）状态带回响应（`src/everos/memory/search/manager.py:53-56`、`:130-134`），供上层判断"还有消息没消化完"。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

**① 原子事实条目写入 md 的 entry 块格式**（`src/everos/core/persistence/markdown/writer.py:324-338`）：
```python
        # 3. Append all entry blocks in order.
        if entries:
            if body and not body.endswith("\n"):
                body += "\n"
            appended_blocks: list[str] = []
            for entry_body, entry_id in entries:
                eid_str = entry_id.format()
                appended_blocks.append(
                    f"<!-- entry:{eid_str} -->\n{entry_body}\n"
                    f"<!-- /entry:{eid_str} -->\n"
                )
            body = body + "".join(appended_blocks)
        # 4. Atomic write.
        return await self.write_markdown(target, frontmatter=meta, body=body)
```

**② Episode 抽取的事件并行扇出**（`src/everos/memory/extract/pipeline/user_memory.py:90-100`）：
```python
        # Emit upfront so OME-async strategies (atomic_fact / foresight /
        # cluster) start in parallel with the in-pipeline Episode work; they
        # consume the MemCell directly and do not depend on Episode output.
        for cell, memcell_id in zip(cells, memcell_ids, strict=True):
            await self._emit_pipeline_started(
                memcell_id=memcell_id,
                session_id=ingested.session_id,
                app_id=ingested.app_id,
                project_id=ingested.project_id,
                cell=cell,
            )
```

**③ 反思策略注册（cron + 默认关闭 + 能力门控）**（`src/everos/memory/strategies/reflect_episodes.py:50-78`）：
```python
@offline_strategy(
    name="reflect_episodes",
    trigger=Cron(expr="0 2 * * 1"),
    emits=[EpisodeExtracted],
    enabled=False,
    max_retries=1,
)
async def reflect_episodes(event: CronTick, ctx: StrategyContext) -> None:
    ...
    if not get_embedding_capability().available:
        logger.debug(
            "strategy_gated_off_embedding_unavailable",
            strategy_name="reflect_episodes",
        )
        return
```

**④ HYBRID 检索的 heap-expand 双融合**（`src/everos/memory/search/hierarchy.py:82-90`）：
```python
    # Phase 1 — dual fusion
    bm25_scores = {c.id: c.score for c in sparse}
    lr_results = lr(dense, sparse, coefs=lr_coefs)
    episode_scores = {c.id: c.score for c in lr_results}
    rrf_results = rrf(sparse, dense, k=rrf_k)

    if not rrf_results:
        return []
```

**⑤ cascade watcher 对原子替换假删除的防御**（`src/everos/memory/cascade/watcher.py:88-99`）：
```python
    def on_deleted(self, event: FileSystemEvent) -> None:
        # macOS FSEvents fires a synthetic deletion for the OLD inode
        # whenever ``os.replace`` overwrites an existing file ...
        # Propagating this false-positive 'deleted' drives the worker to
        # call ``delete_by_md_path`` and wipe LanceDB while md is fine.
        if Path(event.src_path).exists():
            return
        self._enqueue(event.src_path, "deleted")
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）

- README **无任何准确率/token 节省类数字声明**（通读 README 仅功能对比表，grep `%|benchmark|LOCOMO` 无命中）。[无声明——反虚荣加分项]
- 仓库有 `benchmarks/` 目录与 `scripts/e2e_memorize/` 端到端 fixture，但属内部性能/回归脚本，非公开 SOTA 口径。
- 工程性能口径散落在注释里（如 atomic fact 密度 ~28×，`src/everos/memory/search/manager.py:122-126`），属实测经验值 [自封-工程口径]。
- 测试面非常厚：unit/integration/e2e 三层齐备（`tests/` 目录树），cascade/reflection/search 均有对应用例，可复现性好。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）

1. **md-canonical + 数据库投影 + 双向同步**：把"用户可直接手改记忆文件"做成一等公民，用文件监听队列 + 幂等 worker 收敛两侧（`src/everos/memory/cascade/`）。这解决了 API-only 记忆库"用户不可审计/不可手修"的痛点。
2. **OME 三触发器模型**（Immediate/Cron/Idle）是记忆自进化的干净抽象：抽取类策略挂在 `EpisodeExtracted` 事件上并行扇出，整合类挂 cron，轻整理挂 idle——比 mem0 的"每次 add 后同步 update"更解耦（`src/everos/infra/ome/triggers.py:21-76`）。
3. **软删除双写**：md frontmatter `deprecated_entries` + LanceDB `deprecated_by` 同步打标而非删除，可追溯且可回滚（`src/everos/memory/reflection/orchestrator.py:1006-1029`）。
4. **父子层级检索**（episode↔atomic fact 的 max-pool 竞争）+ "只有校准过的分数才进 hit 率统计"的诚实度量观（`src/everos/memory/search/manager.py:146-152`）。
5. **可覆盖 prompt slots**（YAML per-pipeline），抽取 prompt 与代码解耦（`src/everos/config/prompt_slots/`）。

## 6. 局限与风险（失败模式、安全隐患、工程债）

- **核心算法在外部包 `everalgo`**：LLM 抽取/反思/rank 全部 import 自闭源或独立包，本仓库只是编排壳——单看本仓无法评估抽取质量（`src/everos/memory/extract/pipeline/user_memory.py:20-22`）。
- **反思默认关闭**（`enabled=False`），"self-evolving" 叙事在默认配置下只有抽取扇出，没有整合收敛（`src/everos/memory/strategies/reflect_episodes.py:54`）。
- LanceDB 版本被死锁在 0.34.x（上游 compaction 回归），升级路径存疑（`pyproject.toml` lancedb 依赖注释）。
- 反思的 SQL 过滤靠手工 `'` → `''` 转义（LanceDB 无参数化 API，`src/everos/memory/reflection/orchestrator.py:44-56`）——注入面已收敛但有债。
- watchdog→asyncio 的跨线程桥接、per-path 锁 + flock 两级锁：正确性论证很细（docstring 长文），但复杂度高，Windows 上 flock 不可用的分支需验证（`src/everos/core/persistence/markdown/writer.py:31-36`）。
- 无 decay/优先级遗忘；记忆量增长后全靠反思合并，长期库的检索成本无时间维度控制。

## 7. 一句话对比 mem0

mem0 是"API 进、API 出"的黑箱记忆服务（抽取+更新一体、库内闭环），EverOS 则把记忆变成**用户可读可改可 git 的 Markdown 仓库**，数据库只是缓存投影，自进化靠事件/定时/空闲三触发器的离线策略网格异步完成——透明性与可编辑性换来的是同步复杂度和对 `everalgo` 外部算法包的依赖。
