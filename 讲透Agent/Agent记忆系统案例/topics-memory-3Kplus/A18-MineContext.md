# A-18 `volcengine/MineContext`（5.5K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\volcengine__MineContext
> Python（opencontext 包 ~120 个 .py，另有 PySide/Electron 式桌面前端）｜Apache-2.0 ｜ 一句话定位：火山引擎开源的本地"主动上下文引擎"——截图/文件/网页自动捕获 → VLM 抽取分类为**七类上下文** → 向量库按类型分集合存储 → LLM 驱动的迭代式按需检索注入（Context-Engineering 全家桶）
> 字节系工程风格：配置驱动的巨型 YAML prompt 库、双语 prompt（en/zh）、类型化 schema、监控表内建、默认 localhost + 显式鉴权开关。

## 1. 架构总览（目录地图，标出核心目录的职责）

核心包 `opencontext/` 四段流水线（与 config.yaml 四大段一一对应，`config/config.yaml:40-185`）：
- `context_capture/` — 采集（五源）：
  - screenshot（定时截屏）、folder_monitor（文件夹监控）、vault_document_monitor（应用内文档）、web_link_capture（网页链接）、base.py（公共基类）；
  - 默认全部 enabled:false，用户按需开启（`config/config.yaml:44,50,63,72`）。
- `context_processing/` — 加工：
  - processor/：screenshot_processor（25KB，VLM 批量抽取+批内合并）、document_processor（24KB，PDF/Office/VLM 双路）、entity_processor（实体抽取）；
  - chunker/：通用分块 + 结构化文档分块（xlsx/csv/jsonl/parquet 走专用 chunker，`models/enums.py:57-64`）；
  - **merger/**：context_merger（39KB 主流程）+ merge_strategies（49KB 六类型策略）+ cross_type_relationships（18KB 跨类型演化）——本仓最重的工程。
- `storage/` — 存储：UnifiedStorage 门面（32KB）+ 三后端（chromadb 默认 36KB / qdrant 23KB / sqlite 71KB），GlobalStorage 单例（`storage/global_storage.py:23-53`）。
- `context_consumption/` — 消费：
  - context_agent/：intent→context→executor→reflection 四节点工作流（reflection 已停用）；
  - completion/：编辑器 FIM 补全 + 补全缓存（completion_cache.py）；
  - generation/：日报生成、smart_tip、smart_todo、实时活动监控——记忆反向驱动 UI。
- `config/prompts_en.yaml|prompts_zh.yaml`（各 1850+ 行）— 全部 LLM 提示词集中管理（intent_analysis/query_classification/executor/context_collection/extraction/merging/generation/entity_processing/completion/document_processing 等组，见 `config/prompts_zh.yaml:6-1652` 目录），代码只按 key 取（`config/prompt_manager.py`）。
- `server/` FastAPI 路由（agent_chat/completions/conversation/monitoring 等 15 个）+ `web/` 前端 + `tools/` 检索工具集（每类上下文一个工具）。

## 2. 记忆机制深读

### 2.1 写入/抽取管线（主动捕获 + VLM 批量抽取）
- **触发者是被动的采集器**（非对话写入）：
  - 截图默认每 5 秒一张存本地目录（`config/config.yaml:44-46`），单张限 1920px/质量 85（`config.yaml:90-91`）；
  - 截图处理器有感知去重：dedup_cache_size=30、similarity_hash_threshold=7（`config.yaml:86-87`）；
  - 文件夹/Vault 文档每 30 秒扫描、忽略 node_modules/.git（`config.yaml:51-68`）；
  - 文档走"文本页 vs 扫描页"双路：每页字符 <50 判为扫描页送 VLM（`config.yaml:23-24`）。
- **截图批量抽取 prompt**（`config/prompts_en.yaml:410-527`）：VLM 一次看一批截图（batch_size=20，超时 10s，`config.yaml:88-89`），输出限定 JSON：
  ```json
  {"items": [{"decision": "NEW | MERGE", "history_id": "...", "screen_ids": [1,2,3],
    "analysis": {"context_type": "...", "title": "...", "summary": "...",
      "keywords": [...], "importance": 0-10, "confidence": 0-10,
      "event_time": "ISO8601 | null"}}]}
  ```
  （`prompts_en.yaml:430-449`）
- 抽取三原则（`prompts_en.yaml:452-493`）：
  - **"先识别活动、再分类类型"**：默认 activity_context，明确命中其他类型定义才换型（:454-455）；
  - **"一次活动多类型产出"**：看产品页同时记 activity+semantic、看任务板同时记 activity+state（:463-466）；
  - **"类型-风格匹配"**：activity 用 "current_user viewing..."、state 用 "Project progress shows..."、procedural 用 "Step 1:..."，并给出典型错误示例（:468-488）；
  - 多截图判定：同活动多图→MERGE 进一条（screen_ids 关联）；不同活动→多条独立（:490-493）。
- **七类上下文分类法**（`models/enums.py:84-100`）：entity（人物/项目画像）、activity（行为轨迹）、intent（未来计划）、semantic（概念知识）、procedural（操作流程）、state（状态进度）、knowledge（文件）；每类带 classification_priority 供冲突裁决（entity=9 > activity=8 > intent=7...，`models/enums.py:160,177`）与 key_indicators/examples 抽取判据（`models/enums.py:144-178`）。
- 抽取产物 `ProcessedContext`（`models/context.py:131-183`）：
  - properties：create/event_time、**call_count/merge_count/duration_count 生命周期计数器**（:93-95）、raw_properties 回指原始截图/文件（:85-87，上限 5 个，`config.yaml:93`）；
  - extracted_data：title/summary/keywords/entities/context_type/confidence/importance（:57-68）；
  - vectorize：text/image_path/vector（:109-128）。
- 实体独立管线：entity_extraction/entity_meta_merging/entity_matching 三组 prompt（`prompts_zh.yaml:1318-1461`），ProfileEntityTool 提供别名→canonical 归一化。

### 2.2 存储后端与数据模型
- **向量库按类型一集合**：`get_or_create_collection(name=f"{context_type}")`（chromadb_backend.py:166-168；qdrant 同构 `qdrant_backend.py:63-65`），另有独立 todo 集合（chromadb_backend.py:174）。检索天然带类型隔离；集合前缀 opencontext（`config.yaml:157`）。
- SQLite 文档库存业务表（`storage/backends/sqlite_backend.py:66-315`）：
  - vaults：报告/笔记，自引用 parent_id 树、软删 is_deleted（:73-88）；
  - todo（status/urgency/assignee/reason）、activity（含 resources/metadata JSON）、tips；
  - conversations/messages/message_thinking（对话与思维链持久化）；
  - **三张监控表**：monitoring_token_usage（time_bucket×model 唯一，:169-179）、monitoring_stage_timing（分阶段 min/max/avg 耗时+成败计数，:185-199）、monitoring_data_stats，保留 7 天（unified_storage.py:759 cleanup_old_monitoring_data(days=7)）——**LLM 成本可观测性内建到 schema**。
  - 带 PRAGMA table_info + ALTER TABLE 式轻量迁移（:107-152）。
- 嵌入维度默认 2048、输出 API 兼容 OpenAI（`config/config.yaml:32-37`）；ChromaDB 挂起写入有信号处理器 flush（chromadb_backend.py:57-98）。

### 2.3 检索策略：LLM 当检索规划员（agentic retrieval）
- 消费侧是四节点工作流（`context_consumption/context_agent/core/workflow.py:125-162`）：
  - INTENT_ANALYSIS：意图分析（查询分类 + 增强 + 实体识别，带最近 10 条历史，`nodes/intent.py:42,116-117`）；
  - CONTEXT_GATHERING：迭代收集（见下）；
  - EXECUTION：执行生成；
  - REFLECTION：自省回路**整体注释停用**（`workflow.py:150-158`）。
- ContextNode 迭代循环（最多 2 轮，`nodes/context.py:25,76-165`）：
  1. **先评估充分性再取数**：`evaluate_sufficiency` 让 LLM 回答 SUFFICIENT/PARTIAL/INSUFFICIENT（裸文本 `.upper()` 全等比较，`core/llm_context_strategy.py:166-173`；thinking 关闭省 token，:163）；
  2. 不足则 `analyze_and_plan_tools`：LLM 从工具清单（7 类上下文工具 + 实体画像工具 + web_search，`llm_context_strategy.py:38-41`）中自行挑选并构造参数（:43-97）；
  3. `asyncio.gather` 并发执行所有工具调用（:244-247），异常吞掉继续（:252-254）；
  4. **再用一次 LLM 校验过滤**：返回 relevant_result_ids 白名单；解析失败则全保留防丢数据（`llm_context_strategy.py:410-416`）；
  5. 达到轮次上限标 PARTIAL 继续执行（`nodes/context.py:154-155`）。
- 类型化检索工具：`BaseContextRetrievalTool` 子类各绑一个 CONTEXT_TYPE（`tools/retrieval_tools/` 下 semantic/activity/intent/procedural/state 各一个 3KB 小文件 + get_activities/get_daily_reports/get_tips/get_todos 专用工具），统一参数面（`base_context_retrieval_tool.py:179-220`）：
  - 语义 query（可空=纯过滤检索，:115-136）；
  - **实体过滤先经 ProfileEntityTool 归一化**（别名→canonical name，:78-93；"current_user" 特指本人，:189）；
  - **时间范围过滤**：create/update/event 三种时间轴可选（:202-207），要求模型预算好 Unix 整数时间戳；
  - top_k 默认 20、上限 100（:211-216）。
- 返回体自带类型描述帮助上层 LLM 理解（`base_context_retrieval_tool.py:148-151`）；ContextItem 附 relevance_score/relevance_reason（`models/schemas.py:80-96`）。

### 2.4 遗忘·整合·演化（本仓最重的工程）
- **类型感知合并策略**（`context_processing/merger/merge_strategies.py`）：每种 ContextType 一个 Strategy 类（Profile 109 / Activity 264 / State 442 / Intent 631 / Semantic 854 / Procedural 1062 行起），基类统一参数面（:30-37）：
  - 相似度阈值 entity 0.85 / activity 0.80 / intent 0.75 / semantic 0.72 / procedural 0.75 / **state 0.70**；
  - 保留天数 entity 365 / intent·semantic 180 / procedural 120 / activity 90 / **state 仅 7 天**；
  - 最大合并次数 3-10（state 最高 10）；activity 限 24h 时间窗、state 限 30 分钟窗（`config/config.yaml:112-143`）；
  - can_merge 判据各异：entity 要求实体重叠 Jaccard≥0.3（`merge_strategies.py:129-132`）；activity 额外要求时间接近；每类有专用 merge_contexts 实现（标题/摘要/关键词合并各有规则，如 activity `_merge_with_frequency` 按频率合并关键词 :366-374）。
- **遗忘曲线**（`merge_strategies.py:60-102`）：
  - `calculate_forgetting_probability` = `(1-e^(-t/τ)) × 重要性因子 × 访问因子`，τ=retention_days/3；
  - 重要性因子 (10-importance)/10，访问因子 1/(1+merge_count)——越被合并/使用越不忘；
  - 上限 0.95 封顶；`should_cleanup` 概率性删除（`random() < p`）+ 超期且 importance<5 直接删——**艾宾浩斯式遗忘的三因子模型：年龄×重要性×使用频率**。
- **跨类型演化**（`merger/cross_type_relationships.py:24-89`）：六条转移规则
  - intent→activity（意图完成变行为记录）、activity→profile（行为沉淀画像）、procedural→semantic（方法抽象为概念）、state→activity、activity→intent（行为模式识别新意图）、semantic→procedural（概念应用为操作）；
  - 每条带触发关键词、置信度加成（0.1-0.2）、重要性调整（-2~+2）、新保留期（30-365 天）与门槛（如 activity_to_profile 需 ≥3 条相关活动、activity_to_intent 需模式阈值 0.7）；
  - 转换置信度>0.8 才执行、每会话最多 10 次转换（:40-42）——**记忆条目在类型间"升级/降级"并继承不同生命周期**。
- 主流程 ContextMerger：全局相似度阈值 0.90、关联阈值 0.6、智能合并与记忆管理开关、清理检查间隔 24h（`merger/context_merger.py:43-44`、`config/config.yaml:99-105`）。
- **注意：merger 默认 `enabled: false`**（`config/config.yaml:97`）——演化/遗忘默认关闭，开箱只保留写入与检索。

### 2.5 注入上下文的方式
- 执行节点用 `state.contexts.prepare_context()` 四段格式化进 executor prompt（`nodes/executor.py:126-134`）：
  - chat_history（JSON 序列化）、collected_contexts（每项含 relevance_score/relevance_reason/原始数据，`models/schemas.py:144-163`）、current_document（vault 文档全文）、selected_content（编辑器选区）；
  - 上下文条目有面向 LLM 的统一序列化 `get_llm_context_string()`：id/title/summary/keywords/entities/type/metadata/create_time/event_time/duration_count 逐行拼接（`models/context.py:153-183`）。
- **"预热"形态的消费**（记忆不只服务问答，还反向驱动应用）：
  - completion_service：编辑器 FIM 补全，用 semantic_continuation prompt + 补全缓存（`prompts_zh.yaml:1461-1490`、`completion/completion_cache.py`）；
  - smart_tip/smart_todo 生成器：从记忆主动生成操作提示与待办（`prompts_zh.yaml:1081-1236`）；
  - realtime_activity_monitor：实时识别当前活动（`prompts_zh.yaml:1237-1317`）；
  - generation_report：日报/周报聚合（`prompts_zh.yaml:926`）。
- IntentNode 实体识别结果即时查询画像：`profile_tool.match_entity(entity_name)` 回填 metadata（`nodes/intent.py:208-217`）——实体记忆在意图阶段就被消费。

## 3. 关键代码摘录

**遗忘概率三因子**（`opencontext/context_processing/merger/merge_strategies.py:70-83`）：
```python
# Basic forgetting curve: P(t) = 1 - e^(-t/τ), where τ is the time constant
tau = self.retention_days / 3
base_forgetting = 1.0 - math.exp(-age_days / tau)
importance_factor = (10 - context.extracted_data.importance) / 10.0
access_factor = 1.0 / (1 + context.properties.merge_count)
forgetting_prob = base_forgetting * importance_factor * access_factor
return min(forgetting_prob, 0.95)  # Maximum forgetting probability capped at 95%
```

**充分性→规划→并发→过滤的迭代检索**（`opencontext/context_consumption/context_agent/nodes/context.py:88-143`）：
```python
# 1. Evaluate sufficiency first (including first iteration)
sufficiency = await self.strategy.evaluate_sufficiency(state.contexts, state.intent)
if sufficiency == ContextSufficiency.SUFFICIENT:
    break
# 2. Analyze information gap and plan tool calls
tool_calls, _ = await self.strategy.analyze_and_plan_tools(state.intent, state.contexts, ...)
# 3. Execute tool calls concurrently
new_context_items = await self.strategy.execute_tool_calls_parallel(tool_calls)
# 4. Validate and filter tool results
validated_items, _ = await self.strategy.validate_and_filter_tool_results(...)
```

**类型分集合存储**（`opencontext/storage/backends/chromadb_backend.py:166-168`）：
```python
for context_type in ...:
    collection_name = f"{context_type}"
    collection = self._client.get_or_create_collection(name=collection_name, ...)
```

**跨类型转换规则（记忆演化）**（`opencontext/context_processing/merger/cross_type_relationships.py:57-63`）：
```python
CrossTypeTransition.ACTIVITY_TO_PROFILE: {
    "trigger_keywords": ["skill", "ability", "expertise", "experience", "achievement"],
    "confidence_boost": 0.2,
    "importance_adjustment": 1,
    "retention_days": 365,
    "min_activity_count": 3,  # At least 3 related activities to convert
},
```

**实体别名归一化过滤**（`opencontext/tools/retrieval_tools/base_context_retrieval_tool.py:78-91`）：
```python
unify_result = self.profile_entity_tool.execute(
    entities=filters.entities, operation="match_entities", context_info="")
if unify_result.get("success"):
    unified_entities = [
        match.get("entity_canonical_name", match["input_entity"]) for match in matches]
    build_filter["entities"] = unified_entities
```

**充分性评估（裸文本判定）**（`opencontext/context_consumption/context_agent/core/llm_context_strategy.py:160-173`）：
```python
response = await generate_with_messages_async(
    messages=messages, enable_executor=False, thinking="disabled",
)
response_upper = response.upper()
if "SUFFICIENT" == response_upper:
    return ContextSufficiency.SUFFICIENT
elif "PARTIAL" == response_upper:
    return ContextSufficiency.PARTIAL
else:
    return ContextSufficiency.INSUFFICIENT
```

**类型分集合 + 类型化参数面**（`opencontext/tools/retrieval_tools/base_context_retrieval_tool.py:202-216`）：
```python
"time_type": {
    "type": "string",
    "enum": ["create_time_ts", "update_time_ts", "event_time_ts"],
    "default": "event_time_ts",
    ...
},
"top_k": {
    "type": "integer", "default": 20, "minimum": 1, "maximum": 100,
    ...
},
```

## 4. 基准/评测声明（反虚荣视角）
- 无检索质量/端到端基准，无测试目录中的评测套件（仓库只有构建/发布工作流）[不可复现]。
- README 中的能力描述（"smart context retrieval" 等）[自封]；有 monitoring 三表支撑运行时观测（token/耗时，`sqlite_backend.py:166-199`），属工程自监控而非学术评测。
- 值得肯定：prompt 双语对照、config 全量暴露阈值（可复现配置面），但无量化数字。

## 5. 可借鉴模式（字节系工程风格提炼）
1. **七类上下文分类法是记忆 schema 的"认知科学化"**：
   - entity/activity/intent/semantic/procedural/state/knowledge 分型（`models/enums.py:84-100`）；
   - 每型独立阈值（相似度/保留期/合并上限，`config/config.yaml:112-143`）+ 独立向量集合（chromadb_backend.py:166-168）+ 独立检索工具（tools/retrieval_tools/）；
   - **遗忘与合并策略按记忆类型参数化**（state 7 天即弃、entity 保一年），而非 mem0 的一套通用参数。
2. **"一次经历多类型产出"的抽取原则**：
   - 看产品页同时记 activity（行为）+ semantic（知识），配合分类优先级（entity>activity>...）解决归属冲突（`prompts_en.yaml:454-466`、`models/enums.py:160`）；
   - 类型-风格匹配约束（state 用"进度显示..."句式）+ 错误示例负样本教学（`prompts_en.yaml:468-488`）——抽取 prompt 的教学法值得抄。
3. **跨类型记忆演化状态机**：
   - intent→activity→profile 的"记忆升格链"，带最小样本数门槛（3 条活动才可沉淀画像）与保留期/重要性的自动调整（`cross_type_relationships.py:48-89`）；
   - 比 mem0 的 UPDATE/DELETE 操作语义更接近人类记忆巩固——意图完成后自动降级为历史、行为积累后自动升格为画像。
4. **检索即 Agent**：
   - LLM 先判"够不够"再决定"取什么"，取完再自我校验过滤，全链路 LLM 决策（`nodes/context.py:76-151`）；
   - 与固定 top-k 检索的根本差异：检索计划因查询而异、支持跨类型工具组合 + web_search 兜底；
   - 代价是每次问答 3+ 次额外 LLM 调用（由监控表显式计账）。
5. **遗忘三因子公式**：年龄×重要性×访问频率的乘积、95% 封顶、概率性删除避免雪崩（`merge_strategies.py:60-102`）——可直接移植的 decay 基线；且生命周期计数器（call_count/merge_count）从写入那天起就在为遗忘积累证据。
6. **Prompt 资产工程化**：
   - 全部提示词 YAML 化、en/zh 双份、随仓库版本化（`config/prompts_en.yaml`）；
   - 代码与 prompt 彻底解耦，prompt 可 diff 可 review——与把 prompt 散落代码字符串的做法（如 mimiclaw）形成两极。
7. **实体归一化作为检索前置**：所有实体过滤先经别名匹配转 canonical name（`base_context_retrieval_tool.py:78-93`），解决"小张/张三/张工"检索割裂；"current_user" 作为一等实体名统一主语（`prompts_en.yaml:417`）。
8. **LLM 成本观测内建到存储 schema**：token 分桶表 + 阶段耗时表保留 7 天自动清理（`sqlite_backend.py:166-199`）——重 LLM 系统的第一天就该有的账本。

## 6. 局限与风险
- **隐私与成本双高危**：设计上每 5 秒一张全屏截图送云端 VLM（`config/config.yaml:45`，默认关但为核心卖点）；本地明文存储；API 鉴权默认关闭（`config/config.yaml:194` "Enable authentication in production environment for security"）。
- **检索链路 LLM 调用密集**：充分性评估+规划+校验，每轮 3 次、最多 2 轮，问答前固定开销大；充分性判断用裸字符串 `response.upper()` 全等比较（`llm_context_strategy.py:166-173`），模型多说一个词就落入 INSUFFICIENT 分支，鲁棒性差。
- **最有记忆系统价值的部分默认关闭**：merger/遗忘/跨类型演化 `enabled: false`（`config/config.yaml:97`）——演化代码复杂度最大（merger 目录 107KB）而默认不跑，质量存疑；REFLECTION 节点整体注释停用（`workflow.py:150-158`），自省回路未达生产质量。
- 合并用余弦相似度+规则，跨类型转换依赖**英文关键词硬编码触发**（complete/skill/principle 等，`cross_type_relationships.py:52-88`），中文场景 prompt 有双语版但规则词表未双语化。
- 多轮 max_iterations=2 写死在代码（`nodes/context.py:25`），config 无对应项；工具结果过滤失败时"全保留"可能放大上下文（`llm_context_strategy.py:410-416`）。
- 遗忘的概率性删除用 `random()` 无种子、不可解释不可审计（`merge_strategies.py:98-102`）。

## 7. 一句话对比 mem0
mem0 解决"对话里抽取事实并检索回来"；MineContext 把记忆重构成**分层生命周期的上下文资产**——七类型 schema + 类型化遗忘/合并/演化 + LLM 自主检索规划 + 主动捕获（截屏/文件），是"记忆系统"向"个人上下文操作系统"的扩张。

具体差异点：
- 输入：mem0=对话 / MineContext=截屏+文件+网页+对话多源被动捕获；
- schema：mem0=平面事实 / MineContext=七类型 + 实体归一化 + 生命周期计数器；
- 演化：mem0=四操作 / MineContext=类型间升格链（intent→activity→profile）；
- 检索：mem0=固定混合检索 / MineContext=LLM 规划的迭代 agentic 检索；
- 代价：LLM 调用密集、重型工程、最核心演化模块默认关闭。
