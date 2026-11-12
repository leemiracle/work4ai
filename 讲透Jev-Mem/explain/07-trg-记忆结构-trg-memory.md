> 标题：TRG 记忆结构——TemporalResonanceGraphMemory 精讲 · 源文件：memory/trg_memory.py（986 行）· 图谱标签：记忆存储与检索子系统 / 一级枢纽

## 角色定位

这个文件是 Jev-Mem 的心脏：`TemporalResonanceGraphMemory`（memory/trg_memory.py:67）把图数据库、向量数据库、编码器、LLM 粘成一个"会生长的记忆体"。文件头注释（trg_memory.py:4）写明它是 Jev-Mem 与 MAGMA baseline **共享**的图后端——同一套记忆结构既服务实验组也服务对照组，保证消融可比。

它存在的理由：纯向量检索只会"找相似"，回答不了"后来呢""为什么"。TRG 的答案是三件事：每条交互先抽取成结构化事件节点；入库时自动织出 TEMPORAL/SEMANTIC/CAUSAL/ENTITY 四类边；检索时先向量定位锚点再沿边遍历，把散落事实串成叙事。同时实现双通道记忆演化：快路径（trg_memory.py:486）不做 LLM 立即入库，慢路径（trg_memory.py:547）后台补推隐含关系。

## 内部结构

两个轻量 dataclass：`EventExtractionResult`（trg_memory.py:48）与 `QueryContext`（trg_memory.py:58）。主类方法：

- `__init__`（trg_memory.py:70）：`NetworkXGraphDB` 默认图库（trg_memory.py:93）、`KeywordEnricher`（trg_memory.py:96）、按参数选 OpenAI/MiniLM 编码器（trg_memory.py:98-104）、`create_vector_db`（trg_memory.py:105-109）、可选 `LLMController`（trg_memory.py:113-127）、stats 字典（trg_memory.py:134-139）、慢路径队列（trg_memory.py:145-147）
- `add_event`（trg_memory.py:152）完整入库主流程；`query`（trg_memory.py:234）：富化→编码→向量搜锚点→遍历→叙事合成
- `_extract_event`（trg_memory.py:309，json_schema 严格模式 329-351）/`_simple_extract_event`（trg_memory.py:368，>5 字符词当关键词 372、大写词当实体 376）
- `_create_temporal_links`（trg_memory.py:387）：全节点按时间排序后与前驱结 PRECEDES+SUCCEEDS 双向对（trg_memory.py:396-416）
- `_create_semantic_links`（trg_memory.py:421）：向量自检索 top3 建双向 RELATED_TO 边（trg_memory.py:428-460）
- `_async_causal_inference`（trg_memory.py:462）/`_infer_causality`（trg_memory.py:676，LLM 返回四种子类型，subtype_map 751-756）
- `fast_path_ingestion`（trg_memory.py:486）/`slow_path_consolidation`（trg_memory.py:547）/`_get_neighborhood`（trg_memory.py:585，BFS 2 跳）/`_infer_latent_edges`（trg_memory.py:610）/`_create_entity_edges`（trg_memory.py:643）
- `consolidate_narrative_nodes`（trg_memory.py:830，按小时窗聚合）/`_create_narrative_node`（trg_memory.py:860）；`save`/`load`（trg_memory.py:916、934）、`get_statistics`（trg_memory.py:958）、`wait_for_async_tasks`（trg_memory.py:982）

## 外部连接

import 三件套：graph_db 全套类型（trg_memory.py:20-30）、vector_db 接口与工厂（trg_memory.py:32-36）、`KeywordEnricher`（trg_memory.py:38）；`LLMController` 用 try/except 守卫导入（trg_memory.py:41-46，`LLM_AVAILABLE` 旗标），是唯一可选依赖。被引（grep 实证 9 文件）：`memory_builder.py`（构建期主消费者）、`query_engine.py`（直接用 trg.encoder/trg.graph_db）、`jev_mem_retrieval.py`、`jev_mem/demo.py`、`longmemeval.py` benchmark、三个测试、`scripts/evaluate_anchor_recall.py`。图谱一级枢纽，memory/ 子系统事实上的中心。

## 数据流

以 `add_event("I adopted a Labrador named Max", metadata={"speaker":"Mel"})` 为例：

1. `_extract_event`（trg_memory.py:167）请 LLM 返回 JSON：narrative/entities/keywords；失败则土法抽取（trg_memory.py:368）
2. 组装 `EventNode`（trg_memory.py:170-182），attributes 存 entities/keywords/raw_content
3. `KeywordEnricher.enrich_content`（trg_memory.py:185-193）把实体关键词拼进编码文本——向量拿"叙事+关键词"算，不是裸叙事
4. 编码（trg_memory.py:196-199）后双写：`graph_db.add_node`（trg_memory.py:202）+`vector_db.add_vector`（trg_memory.py:205-213）
5. 织边：时序边连最近旧节点（trg_memory.py:216）、语义边连 top3 邻居（trg_memory.py:219）；`enable_async` 时挂起因果推理（trg_memory.py:222-226）

查询侧 `query("What pet does Mel have?")`：富化→编码→向量库取锚（trg_memory.py:260-263，锚点数=max_results，257-258 注释解释多跳需更多锚）→默认 `TraversalConstraints(max_depth=3)`（trg_memory.py:274-280）→BFS 遍历→`_synthesize_narrative`（trg_memory.py:289、775）拼「Key Events / Event Sequences / Causal Relations」三段（trg_memory.py:781、792、813）装进 QueryContext。

快慢双路径：`fast_path_ingestion` 跳过 LLM 存原文节点（trg_memory.py:500-506）、只连时序边（trg_memory.py:522-528）、向量批量入库（trg_memory.py:537）、node_id 入队（trg_memory.py:540）；`slow_path_consolidation` 排空队列，每节点取 2 跳邻域（trg_memory.py:565），用 `_infer_latent_edges`+`_create_entity_edges` 补边并计数。

## 设计决策

**图+向量双写**是核心决策：图管结构（遍历/路径/叙事），向量管语义定位。两边同 node_id 关联，代价是存储翻倍、一致性自维护，但"向量粗定位+图精扩展"正是多跳正确率的来源。**双向边**（trg_memory.py:396-416、438-458 成对建）让邻居查询不辨方向、遍历代码极简，代价是边数×2。**LLM 全面降级**：抽取与因果都有无 LLM 回退，导入守卫保证裸环境可跑。

批判地看有三处硬伤：其一 `_infer_latent_edges`（trg_memory.py:610）里 prompt 拼好了却**从未发给 LLM**——trg_memory.py:627-629 注释自陈 simplified for minimal implementation，实际退化为"时间在前的邻居→confidence 0.5 的 LEADS_TO 边"（trg_memory.py:630-639），时序启发式冒充因果推理；其二 `_create_temporal_links` 每次入库全节点排序（trg_memory.py:389-390），O(N log N)/条，万级节点明显变慢；其三 `_create_entity_edges` 的 O(N) 全库扫（trg_memory.py:654）加每实体只连一条的 break（trg_memory.py:672）。这些是 shared backend 兼容 baseline 留下的债，真正的检索增强都在 query_engine.py 补。

## 新人提示

先读 `add_event`（trg_memory.py:152）与 `query`（trg_memory.py:234），各 80 行串起全部协作方，读懂即读懂骨架；再跳 `fast_path_ingestion`/`slow_path_consolidation`（trg_memory.py:486、547）看双通道。

三个常见误解：以为 CAUSAL 边都是 LLM 推的——慢路径实际是时间启发式（trg_memory.py:630-639），只有 `enable_async=True` 的 `_infer_causality`（trg_memory.py:676）才是真 LLM；以为向量拿原文算——实际是富化后文本（trg_memory.py:185-196），改 enrich 逻辑会连带改变全部语义边与检索行为；以为 `stats['links_created']` 等于图里总边数——它只是运行期计数器，load 后从 stats.json 恢复，与实际边数可能漂移，看真实分布用 `get_statistics`（trg_memory.py:958）的 link_types。另注意 `save`/`load`（trg_memory.py:916、934）不序列化 consolidation_queue，停机前应先跑完 `slow_path_consolidation`。
