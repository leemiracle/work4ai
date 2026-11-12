> 标题：记忆构建写路径——MemoryBuilder 精讲 · 源文件：memory/memory_builder.py（1388 行）· 图谱标签：记忆存储与检索子系统 / 一级枢纽（class:memory/memory_builder.py:MemoryBuilder）

## 角色定位

`MemoryBuilder`（`memory/memory_builder.py:26`）是 Jev-Mem 写路径的中枢，也是全仓最大的类：一个文件装着**两套完整构建器**。`build()`（119-187）是论文的 Jev-Mem System-One 写路径——用 admission 概率批量评估替代逐条 LLM 抽取；`build_memory()`/`extract_event()`（1143-1290、326-499）是 MAGMA System-Two 基线——逐 turn LLM 抽取再批量建链。两者共享同一 TRG 存储层，消融实验因此可比；文件头 docstring（1-9）列的四件事主要描述基线路径。Jev 路径的宣言在 `build` docstring（120-123）："**No System-Two extraction is used for successful System-One writes.**"——写入成功时零 LLM 抽取调用，这是论文"记忆构建 6.6× 加速"的机制根源。

## 内部结构

按职责分组（26 个方法挑主干）：

**组装**（33-117）：`__init__` 提供五个注入点（jev_config/jev_client/trg_memory/llm_enabled/use_episodes）。61-66 行组装 Jev 三件套（config/client/`WritePolicy`）；69-70 行：`use_episodes` 与 `write_enabled` 互斥（"one canonical node per observation"）；78-82 行血泪注释——别把 persist_dir 传给 TRG 构造（会只加载 vectors、污染 --rebuild）；84-99 行 OPENAI_API_KEY 缺失则降级；101-117 行装配 parser/formatter/segmenter 与六个运行态容器。

**Jev 写路径**：`build`（119-187）五步见数据流；`_store_jev_node`（189-218）事务化入库——先验候选存在（192-195）、插向量失败即止（196-198）、try 里插节点+关系边+时序链，except 时删节点删向量再 raise（212-215）；`_build_magma`（220-226）降级出口（audit `write_fallback`，节点标 `controller=magma_fallback`）；`consolidate`（228-291）周期巩固。

**System-Two 抽取（基线）**：`extract_event`（326-499）——351-372 行 JSON 抽取 prompt（七键），384-390 行剥 ```json 围栏，374-446 行三次重试含 429 降级，468-476 行按 `turn_number` 逐小时推进时间戳。

**节点工厂与索引**：`create_episode_node`（501-549）、`create_session_nodes`（551-599，session 摘要 → SESSION 节点）、`create_event_from_episode`（601-670）；`_index_text_basic`（672-695，词+bigram）、`index_event`（697-728，原文与四类语义抽取进倒排索引）。

**MAGMA 建链八连**（730-1102）：temporal（PRECEDES/SUCCEEDS，`latest_only` 只补尾）、context（窗口 3）、semantic（SIMILAR_TO）、causal（换说话人 RESPONSE_TO）、entity（SAME_ENTITY，防重 932-940 遍历全部 links）、temporal_proximity（24h）、qa（问句→ANSWERED_BY）、episode/session 归属；`batch_create_links`（1104-1141）统一调度。

**顶层编排与持久化**：`build_memory`（1143-1290）；`save`（1292-1326，五件：graph/vectors/keyword_index/jev_mem_config/episodes）；`load`（1328-1360，`validate_cached_backend` + stats 重建 1355-1357）；`add_sessions_to_existing_memory`（1362-1388，注释："~1 minute vs ~20 minutes"）。

## 外部连接

顶部 import 四件（19-22）：`TemporalResonanceGraphMemory/Link/LinkType`、`SessionNode/NodeType/LinkSubType`、`EpisodeSegmenter/Episode`、`TemporalParser`。延迟 import：`LLMController`/`AnswerFormatter`（53-54）、Jev 三件套（61-63）、`EventNode`/`find_candidates`（128-129）、`node_state`（140、234）、`consolidation_questions`/`choice_fixture`（243）、`validate_cached_backend`（1333）。被 import 八个源文件：`jev_mem/system.py:5`、`jev_mem/__init__.py:10`、demo、两个 benchmark、`memory/__init__.py`、`memory/longmemeval_jev.py`、`memory/test_harness.py`，加 7 个测试。图谱归 layer:memory-storage。

## 数据流

**Jev 路径**（`build`，119-187）：入参 `(interaction, timestamp, metadata)` → 131-132 非空校验 → 134 判 `write_enabled`（关则直落 MAGMA）→ 137-152 admission：138 行全图扫 `raw_content` 判 exact_duplicate，141-143 行取最近 `candidate_top_k` 个 EVENT 作 recent_memories，144 行 `assess_observation`，None 则降级（145-146），score<0.60 则 audit `memory_rejected` 返 None（150-152）→ 154-156 typing → 157-159 entities（metadata 或 regex 兜底）→ 161-166 组 `EventNode`，塞 `jev_mem` 块（164-166）→ 167-170 时间解析+enrich+encode → 171 `find_candidates` → 172-174 `relations`（None 则降级）→ 175 `_store_jev_node` → 176 索引 → 178-183 audit `memory_constructed` → 184-186 周期巩固触发 → 187 返回 node。

例子：`build("[Alice]: I moved to Berlin", ts, {"speaker": "Alice"})` 通过 admission 后与既有 "Alice lives in Paris" 候选建边，并在 204-211 行增量补 MAGMA 时序边（203 行注释：这些邻居独立于 Jev 候选集）——Jev 判语义边、MAGMA 判时序边。

**MAGMA 路径**（`build_memory`，1143-1290）：write_enabled 分支（1153-1168）逐 turn 调 `build`；基线分支先建 SESSION 节点（1175），1187-1190 行**猴子补丁**废掉 TRG 内建建链（1259-1260 恢复），逐 turn `extract_event`→`add_event`→`index_event`（1205-1249），最后 `batch_create_links`（1263）集中建八类边。

**巩固**（228-291）：对候选发 consolidation 问题，257-267 行按阈值建 CONTRADICTS/REDUNDANT_WITH/RELATED_TO 边（sha256 幂等 link_id）；268-286 行 representation 为 merge/promote 且无矛盾时，用注入的 System-Two summarizer 生成摘要，置 `_consolidating=True`（278）递归走 `build` 入库——原始证据永不删除（229 行 docstring："raw evidence always survives"），`consolidation_key` 防重复摘要（271-272）。

## 设计决策

**双控制器同居一文件**：Jev 路径约 200 行、MAGMA 基线约 800 行，同居保证存储/索引/持久化严格对齐，对照实验无隐藏差异。**事务化入库**（189-218）：向量先插、节点后插、异常双向回滚，"半插入"状态挡在图外；204-211 的增量时序链让 Jev 写入无需 batch 阶段也获得 MAGMA 序列结构。**成本可审计**：每写 emits `memory_constructed`（180-183），降级 emits `write_fallback`（223），System-Two 只在巩固摘要出现（286，`llm_calls=1`）——三事件即论文成本曲线的数据源。

批判地看：1388 行巨石（MAGMA 八连与 Jev 路径几乎无共享，可拆 `magma_baseline.py`）；138 行 duplicate 检测全图 O(N) 扫 `raw_content`；`create_entity_links` 防重（932-940）每条新边遍历全部 links，大图 O(N×E) 热点；`_simple_entity_extraction`（301）只认大写英文人名；1187-1190 猴子补丁若中途抛异常，恢复代码（1259）不会执行。

## 新人提示

上手：先读 `build` 119-187（Jev 主线）→ `_store_jev_node` 189-218（事务）→ 对照 `tests/test_jev_mem.py`。四个高频误解：① `build` 返回 None 不等于出错——可能是 admission 拒绝（audit `memory_rejected`，什么都没写）或降级（audit `write_fallback`，实际写了 MAGMA 节点），先查审计再下结论；② `use_episodes` 与 `write_enabled` 同开在 69-70 行直接 ValueError；③ 326 行往后的 `extract_event` 一大段**不是死代码**，是基线与 episode 模式主干；④ `jev_mem_config.json` 只在 write/read 任一开启时落盘（1312-1314）；`load` 先 `validate_cached_backend`（1333-1334）拒跨后端缓存。调写入问题：audit 三事件 → 节点 `jev_mem` 块（164-166）。
