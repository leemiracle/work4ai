# A-11 `MemTensor/MemOS`（10.7K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\MemTensor__MemOS
> Python / src 约 76.3k 行（另含大量 TS 插件）/ Apache-2.0 / v2.0.30 ｜ "记忆操作系统"：MemCube 容器 + 三态记忆（文本/激活 KV/参数 LoRA）+ 调度器，配套论文 arXiv:2507.03724

## 1. 架构总览（目录地图，标出核心目录的职责）

```
src/memos/
├─ mem_os/            # MOS/MOSCore：OS 叙事顶层，管多 MemCube、chat、CoT 分解
├─ mem_cube/          # MemCube：text/act/para/pref 四类记忆的装载-卸载容器
├─ memories/
│   ├─ textual/       # 旗舰 TreeTextMemory：Neo4j 图存储 + 树状组织
│   │   └─ tree_text_memory/organize（写入/重组）、retrieve（混合检索）
│   ├─ activation/    # KVCacheMemory：把 HF DynamicCache 当"激活记忆"存取
│   └─ parametric/    # LoRA 当"参数记忆"（占位级实现）
├─ mem_reader/        # 对话/文档/多模态 → 结构化记忆的抽取器（prompt 驱动）
├─ mem_scheduler/     # 记忆调度器：任务队列(Redis/RQ)+monitors+检索/过滤管线（OS 叙事主证据）
├─ vec_dbs/ graph_dbs/ reranker/ embedders/ llms/   # 组件工厂层（Milvus/Qdrant、Neo4j/PolarDB…）
├─ dream/             # "做梦"离线整理管线（diary/motive/reasoning/recall）
└─ api/               # FastAPI 服务 + MCP server
apps/                 # 5 个 TS 插件（OpenClaw/cloud/local-plugin 等，Star 数主要流量入口之一）
evaluation/scripts/   # LoCoMo/LongMemEval/LongBench-v2/PersonaMem/PrefEval 脚本
packages/memos-core/  # TS 版核心（capture/recall/ingest…），与 Python 版并行演进
```

OS 叙事的代码对应：`MOSCore` 自述"acts as an operating system layer for handling and orchestrating MemCube instances"（`src/memos/mem_os/core.py:38-43`）。

## 2. 记忆机制深读（本笔记核心，每个论断钉 `相对路径:行号`）

### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）

- 用户画像抽取 schema 是**硬编码键表**：objective_memory 16 键（nickname/gender/personality/birth/education/work/…），逐键带 confidence_score 与 timestamp（`src/memos/mem_reader/memory.py:65-100`）；记忆对象分 objective/subjective/scene（qa_pair+document）三仓（`src/memos/mem_reader/memory.py:24-50`）。
- 抽取 prompt（`SIMPLE_STRUCT_MEM_READER_PROMPT`）：要求 LLM 从对话输出 JSON `memory list`，每条 `{key, memory_type: "LongTermMemory"|"UserMemory", value}`，且"从用户视角抽取、assistant 只抽事实"（`src/memos/templates/mem_reader_prompts.py:1-40`）。
- TreeTextMemory 写入双路径：`_add_memories_batch`（批量 Cypher，batch=5）与 `_add_memories_parallel`（线程池 10 并发单点写）；`mode="sync"` 时写入后立即 `_cleanup_working_memory`（`src/memos/memories/textual/tree_text_memory/organize/manager.py:89-136`、`:138-139`）。
- 异步模式下 working↔long 绑定靠**正则内嵌 ID**：在 metadata.background 写 `[working_binding:<uuid>]`，事后正则回收临时 WorkingMemory 节点（`src/memos/memories/textual/tree_text_memory/organize/manager.py:23-51`）。
- 容量模型（OS 叙事核心）：WorkingMemory 20 / LongTermMemory 1500 / RawFileMemory 1500 / UserMemory 480，超限触发淘汰（`src/memos/memories/textual/tree_text_memory/organize/manager.py:68-80`；TreeTextMemory 构造处同款默认值 `src/memos/memories/textual/tree.py:81-87`）。

### 2.2 存储后端与数据模型（表/集合/文件布局，原文摘录 schema）

- MemCube = 四格容器：`text_mem / act_mem / para_mem / pref_mem`，每格可 `uninitialized`；`load/dump` 以目录为单位整体序列化，dump 要求空目录否则抛 `MemCubeError`（`src/memos/mem_cube/general.py:24-48`、`:50-118`）。
- TreeTextMemory 主存是 **Neo4j 图**（不是向量库）：节点带 `memory/memory_type/user_name/status/is_fast/evolve_to/version/history/…` 约 40 个字段（`src/memos/memories/textual/tree_text_memory/retrieve/recall.py:16-54` 的 `_LIGHTWEIGHT_VECTOR_RETURN_FIELDS` 即字段清单）。
- 记忆类型枚举（检索 scope 校验）：WorkingMemory/LongTermMemory/UserMemory/ToolSchemaMemory/ToolTrajectoryMemory/RawFileMemory/SkillMemory/PreferenceMemory（`src/memos/memories/textual/tree_text_memory/retrieve/recall.py:110-120`）。
- 激活记忆 = 真·KV cache：`KVCacheMemory.extract` 调 `llm.build_kv_cache(text)` 生成 HF `DynamicCache` 存 dict，`get_cache` 把多个 cache 拼接返回（`src/memos/memories/activation/kv.py:32-81`）——这是把 prefill 结果当记忆复用的实现基础（vLLM 版在 `vllmkv.py`）。
- 向量库（Milvus/Qdrant）只是组件层可选件，图库另有 PolarDB/Postgres 后端（`src/memos/vec_dbs/`、`src/memos/graph_dbs/` 工厂）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）

- 混合检索三路并发：`GraphMemoryRetriever.retrieve` 用 3 线程池同时跑 `_graph_recall`（结构化图查询）+ `_vector_recall`（向量）+ `_bm25_recall`（EnhancedBM25），再合并（`src/memos/memories/textual/tree_text_memory/retrieve/recall.py:94-160`）；`filter_weight = 0.6`（`recall.py:77`）。
- WorkingMemory 特例：不走相似度，直接 `get_all_memory_items(scope="WorkingMemory", status="activated")` 截 top_k（`recall.py:122-131`）——工作记忆=当前激活集。
- 检索前 LLM 任务解析：`TaskGoalParser` 把 query 解析成结构化 goal 再驱动图检索，可选 `cot/fast_graph/fulltext` 开关（`src/memos/memories/textual/tree_text_memory/retrieve/searcher.py:64-78`）。
- 深度检索（AdvancedSearcher）：3 个 thinking stage，每 stage LLM 判断 `can_answer` 并产出下一轮 `retrieval_phrases` 扩展检索，`stage_retrieve_top=3, max_retry_times=2`，prompt 在 `src/memos/templates/advanced_search_prompts.py` 的 `PROMPT_MAPPING`（`src/memos/memories/textual/tree_text_memory/retrieve/advanced_searcher.py:53-133`）。
- 重排：默认 `cosine_local` 分层权重 `{"topic":1.0,"concept":1.0,"fact":1.0}`（`src/memos/memories/textual/tree.py:63-75`），可换 http_bge 等；还有 `reranker/strategies/` 按场景（dialogue/singleturn/concat）选策略。
- 调度器侧还有一道 **LLM 记忆过滤**：`MemoryFilter.filter_unrelated_memories` 用 LLM 判哪些记忆与 query_history 无关，失败则保守全保留（`src/memos/mem_scheduler/memory_manage_modules/memory_filter.py:18-100`），管线封装在 `filter_pipeline.py:16-29`（unrelated/redundant 两道）。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）

- **后台重组线程**：`GraphStructureReorganizer` 起两条常驻线程——(1) PriorityQueue 消息消费循环（op=add/remove/merge/update/end，merge 优先级最高，`reorganizer.py:68`），(2) 周期性 structure optimizer（对 LongTermMemory/UserMemory 分别加 `_is_optimizing` 锁，`src/memos/memories/textual/tree_text_memory/organize/reorganizer.py:96-106`）；LLM 子聚类 prompt `LOCAL_SUBCLUSTER_PROMPT/REORGANIZE_PROMPT`（`reorganizer.py:24`）。
- 相似度合并阈值：`threshold=0.80, merged_threshold=0.92`（`manager.py:61-62`）——0.80 视为相关、0.92 以上合并。
- `dream/` 离线"做梦"管线：diary→motive→reasoning→recall 四段 pipeline + signal_store（`src/memos/dream/pipeline/`），挂接在调度器 `mem_dream_handler` 上（`src/memos/mem_scheduler/task_schedule_modules/handlers/mem_dream_handler.py`）。
- 调度演化 handler 网格：add/answer/query/feedback/mem_read/mem_reorganize/mem_dream/pref_add 八类任务 handler 注册进 dispatch map（`src/memos/mem_scheduler/general_scheduler.py:34-48`）。
- 遗忘 = 容量驱逐 + status 字段（`status="activated"` 过滤）+ merge 消化；无时间 decay。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）

- `MOSCore.chat`：搜各 cube 的 `text_mem.search`，把结果交给 `_build_system_prompt`（`src/memos/mem_os/core.py:292-305`）；默认模板"You have access to conversation memories…don't explicitly mention having memories"，自定义 `base_prompt` 用 `{memories}` 占位符替换（`core.py:356-384`）。
- PRO 模式 CoT 增强：`cot_decompose` 先判 `is_complex`，复杂 query 拆子问题逐个检索回答再合成（`src/memos/mem_os/main.py:131-198`），`cot_top_k=3`（`main.py:184`）。
- 无显式 token 预算；注入量靠 top_k 与调度器过滤管线控制（`filter_unrelated_and_redundant_memories`，`src/memos/mem_scheduler/memory_manage_modules/filter_pipeline.py:26-29`）。
- 激活记忆注入是另一条路：调度器 `update_activation_memory_periodically` / `replace_working_memory`（`general_scheduler.py:29-31`）直接换工作记忆集合，KV 路径则把 prefill cache 拼回模型（`kv.py:63-81`）。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

**① MemCube 四格容器**（`src/memos/mem_cube/general.py:28-48`）：
```python
        self._text_mem: BaseTextMemory | None = (
            MemoryFactory.from_config(config.text_mem)
            if config.text_mem.backend != "uninitialized"
            else None
        )
        ...
        self._act_mem: BaseActMemory | None = (...)
        self._para_mem: BaseParaMemory | None = (...)
        self._pref_mem: BaseTextMemory | None = (...)
```

**② 三路并发混合检索**（`src/memos/memories/textual/tree_text_memory/retrieve/recall.py:133-160`）：
```python
        with ContextThreadPoolExecutor(max_workers=3) as executor:
            # Structured graph-based retrieval
            future_graph = executor.submit(
                self._graph_recall, parsed_goal, memory_scope, user_name,
                use_fast_graph=use_fast_graph,
            )
            # Vector similarity search
            future_vector = executor.submit(
                self._vector_recall, query_embedding or [], memory_scope, top_k,
                search_filter=search_filter, search_priority=search_priority,
                user_name=user_name,
            )
            if self.use_bm25:
                future_bm25 = executor.submit(
                    self._bm25_recall, query, parsed_goal, memory_scope, ...
```

**③ OS 式容量与合并阈值**（`src/memos/memories/textual/tree_text_memory/organize/manager.py:61-87`）：
```python
        memory_size: dict | None = None,
        threshold: float | None = 0.80,
        merged_threshold: float | None = 0.92,
        is_reorganize: bool = False,
    ):
        ...
        self.current_memory_size = {
            "WorkingMemory": 0, "LongTermMemory": 0,
            "RawFileMemory": 0, "UserMemory": 0,
        }
        if not memory_size:
            self.memory_size = {
                "WorkingMemory": 20, "LongTermMemory": 1500,
                "RawFileMemory": 1500, "UserMemory": 480,
            }
```

**④ KV cache 当记忆存取**（`src/memos/memories/activation/kv.py:43-52`）：
```python
        # Build KV cache from the text using the LLM
        kv_cache = self.llm.build_kv_cache(text)

        # Create a KVCacheItem with the extracted cache
        cache_item = KVCacheItem(
            memory=kv_cache,
            metadata={"source_text": text, "extracted_at": datetime.now().isoformat()},
        )
        return cache_item
```

**⑤ 后台双线程重组器**（`src/memos/memories/textual/tree_text_memory/organize/reorganizer.py:96-106`）：
```python
        if self.is_reorganize:
            # ____ 1. For queue message driven thread ___________
            self.thread = ContextThread(target=self._run_message_consumer_loop)
            self.thread.start()
            # ____ 2. For periodic structure optimization _______
            self._stop_scheduler = False
            self._is_optimizing = {"LongTermMemory": False, "UserMemory": False}
            self.structure_optimizer_thread = ContextThread(
                target=self._run_structure_organizer_loop
            )
            self.structure_optimizer_thread.start()
```

## 4. 基准/评测声明（反虚荣视角：自封 or 第三方？可复现？数字与口径）

- **"35.24% token 节省"在仓库代码与文档中不存在**（全仓 grep `35.24/35%/节省` 无命中）。该数字出自团队论文 arXiv:2507.03724（README:275 引用），属 [自封-论文口径]，仓库内无对应复现脚本——**代码与论文可复现性脱节**。
- README 另称 OpenClaw 云插件"72% lower token usage"（README.md:59），无脚本佐证 [自封-营销口径]。
- 仓库内可复现的数字是 KV-cache TTFT 加速表：4090 上最高 77.4%（2k/0.5k），H800 上普遍 <20% 甚至为负（`docs/en/open_source/modules/memories/kv_cache_memory.md:118-149`）[自封-有数据表，硬件口径诚实（H800 负收益也照登）]。
- `evaluation/scripts/` 有 LoCoMo/LongMemEval/LongBench-v2/PersonaMem/PrefEval 五套完整 ingestion+eval 脚本（ingestion/metric/search 分文件），**框架可复现性好**，但仓库不携带跑分结果文件，与论文数字的对齐需自行验证。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）

1. **记忆三态统一容器**（textual/activation/parametric 同一 MemCube 接口 load/dump）：把 KV-cache prefill 和 LoRA 权重当"记忆"装卸，是比"文本记忆+向量库"更彻底的记忆抽象（`src/memos/mem_cube/general.py:50-118`、`src/memos/memories/activation/kv.py:16-31`）。
2. **图原生记忆 + 三路并发混合检索**（graph/vector/BM25 各占一线程，WorkingMemory 直读激活集不走相似度，`recall.py:122-160`）——图结构让"记忆演化"（merge/update 边操作）成为一等操作。
3. **OS 式容量分区**（Working 20/LongTerm 1500/User 480 的容量上限+驱逐）与**优先级队列消息驱动的后台重组**（merge 优先级最高，`reorganizer.py:68`）。
4. **调度器作为独立层**：消息标签→专用线程池→handler 注册表的 dispatch 架构（8 类任务 handler），加 Redis 队列与 monitors，是"记忆操作异步化/产品化"的完整参考（`general_scheduler.py:34-48`、`task_schedule_modules/dispatcher.py:38-49`）。
5. **检索后 LLM 二次过滤**（unrelated+redundant 两道，失败保守放行，`memory_filter.py:18-100`）——比单纯调 top_k 更精细的注入质量控制。

## 6. 局限与风险（失败模式、安全隐患、工程债）

- **论文-代码对应度打折**：旗舰数字 35.24% 不在仓库；`parametric`（LoRA）记忆基本是占位（`src/memos/memories/parametric/lora.py` 无训练闭环）；"OS"叙事的进程调度是线程池+队列，不是真资源管理。
- 双实现漂移：Python `src/memos` 与 TS `packages/memos-core`、`apps/*` 五个插件并行，行为一致性无保证（目录结构已可见分叉）。
- 工程粗糙处：类型注解 `(list, bool)` 元组写法（`memory_filter.py:22`）、working_binding 用正则从 metadata 字符串里抠 UUID（`manager.py:40`）、prompt 内嵌中文合规条款（"避免违反国家法律法规…"，`mem_reader_prompts.py:21`）。
- LLM 过滤/重排/CoT 解析全链路依赖 LLM 输出 JSON，虽有保守回退但延迟与成本叠加（检索一次至少 3 个 LLM 调用：goal parse + filter + rerank 判断）。
- Neo4j 强依赖（TreeTextMemory 构造即连图库，`tree.py:56`），单机轻量部署门槛高；相似度阈值 0.80/0.92 为硬编码默认，无自适应。

## 7. 一句话对比 mem0

mem0 把记忆收敛为"抽取-更新-向量检索"的轻量单库；MemOS 则试图按操作系统隐喻把记忆做成**分层资源系统**（多 MemCube 容器、三态记忆、容量分区、调度器与后台重组），概念雄心大、组件多，但论文旗舰数字与代码脱节、LoRA 记忆空壳、Python/TS 双栈漂移使其更接近"研究型全家电"而非生产单晶。
