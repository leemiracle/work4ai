# 08 Text-to-SQL：11-agent LangGraph 组图（表格数据问答）

## 角色定位

`nemo_retriever/src/nemo_retriever/tabular_data/` 是 Retriever 从"文档 RAG"扩展到"表格数据问答"的支线：把自然语言问题转成 SQL、在注入的数据库连接上执行、格式化返回。核心是 `retrieval/text_to_sql/` 的 11-agent LangGraph 组图——不做单次 prompt 生成，而是"抽取实体→语义检索候选→双重校验→降级重建→执行"流水线，带完整重试阶梯与放弃路径。

## 内部结构

组图骨架在 `text_to_sql_graph.py:175` 的 `create_graph()`：11 个节点（`text_to_sql_graph.py:224-234`）——entities_extraction、retrieve_candidates、prepare_candidates、construct_sql_from_candidates、construct_sql_not_from_snippets、reconstruct_sql、validate_sql_query、validate_intent、execute_sql_query、format_and_respond、unconstructable_sql_response。主链是固定三连边（`text_to_sql_graph.py:237-239`）：实体抽取 → 候选检索 → 候选准备 → 从候选构造 SQL；随后 `route_decision`（`text_to_sql_graph.py:114`）按 state 的 `decision` 分流，别名 `constructable→validate_sql_query`（`text_to_sql_graph.py:128-130`）。

重试阶梯是图的灵魂，`route_sql_validation`（`text_to_sql_graph.py:29`）：SQL 无效时 `sql_attempts` 计数，第 4 次尝试降级为 fallback——放弃候选片段改从 relevant tables 整表构造（`text_to_sql_graph.py:50-52`）；第 8 次彻底放弃走 unconstructable（`text_to_sql_graph.py:55-57`）；SQL 有效但 `reconstruction_count>5` 时跳过意图校验直奔执行，防无限循环（`text_to_sql_graph.py:62-64`）。execute_sql_query 节点复用同一个 `route_sql_validation` 做出口路由（`text_to_sql_graph.py:274-284`）——执行报错同样计入阶梯。意图校验 `route_intent_validation`（`text_to_sql_graph.py:68`）失败折返 reconstruct_sql，后者与 validate_sql_query 是线性边（`text_to_sql_graph.py:294`）；两条终止边通 END（`text_to_sql_graph.py:296-297`）。注意 `route_translation`（`text_to_sql_graph.py:94-111`）已定义但未挂任何边——当前版本是死代码。

节点工厂 `_make_node`（`text_to_sql_graph.py:140`）给每个节点包访问计数日志，写 `path_state["node_visit_counts"]`（`text_to_sql_graph.py:154-160`）——可观测"哪些 agent 被走了几遍"。

agent 基类在 `base.py:28`：`BaseAgent` ABC 强制 `execute(state)→dict` 契约（`base.py:55-76`），可选 `validate_input`（返回 False 则跳过执行，`base.py:78-91`）与 `handle_error`（异常写进 `path_state["error"]`，`base.py:93-122`）。`agent_wrapper`（`base.py:153`）把 agent 适配成 LangGraph 节点：输入校验→执行→非 dict 结果防护（`base.py:191-193`）→异常兜底。

关键 agent 择要：EntitiesExtractionAgent 用 pydantic `EntitiesExtractionModel`（`entities_extraction.py:28-39`）抽概念实体，空返回回退 `[question]` 整句（`entities_extraction.py:81-82`）；CandidateRetrievalAgent 做语义检索（`candidates_retrieval.py:31`），Neo4j 图扩展在 `data_access/candidates.py:212` 完成并去重（`candidates.py:191`）；CandidatePreparationAgent 有两个 LLM 相关性过滤器（`candidates_preparation.py:190`、`:256`）；SQLFromCandidatesAgent 产出 `constructable/unconstructable` 决策（`sql_from_semantic.py:139`），方言由 `resolve_connector_from_tables`（`connector_routing.py:23`）按 `database_name` 匹配 connector、无匹配回退 `connectors[0]`（`connector_routing.py:44-46`）；SQLValidationAgent 调 sqlglot 系 `parse_query_single`（`sql_parse_validation.py:126`，实现在 `ingestion/services/queries.py:171`），方言列表取自 connector `dialect`（`sql_parse_validation.py:88-89`）；SQLExecutionAgent 执行后 DataFrame 转 JSON（`sql_execution.py:43`），报错回阶梯重试（`sql_execution.py:89`）。

## 外部连接

状态类型直接持有重对象：`state.py:34` 的 `AgentState` 含 `llm: ChatNVIDIA`、`connectors: list[SQLDatabase]`、`retriever: Retriever`——三者在图状态里传递而非全局单例。`SQLDatabase` 是 ABC（`sql_database.py:36`），`dialect` 属性约定为 sqlglot 兼容名（duckdb/snowflake，`sql_database.py:137-141`）。LLM 构造在 `llm_invoke.py:23-28`：`ChatNVIDIA` 读 env `BASE_URL`/`NVIDIA_API_KEY`/`MODEL_NAME`（默认 nemotron-3-nano-30b-a3b）。结构化输出走 `safe_invoke_with_structured_output`（`llm_invoke.py:31`）——ValidationError 追加为 SystemMessage 让模型自我修正，最多 3 轮（`llm_invoke.py:41-58`）。入口 `main.py:26-27` 模块级编译图；`stream_agent_response`（`main.py:89`）产出 step/result/error 事件，`recursion_limit=45`（`main.py:101`）。上游消费方：`graph/retriever.py:675-679` 的 `Retriever.generate_sql` 桥到旧单发路径，dev 工具 `dev_tools/debug_ingest.py:134` 直接调 `get_agent_response`。ingestion 侧负责把库 schema+示例查询写进 Neo4j 图与向量索引供检索用。

## 数据流

一次问答：`AgentPayload`（`state.py:23-31`）→ `_build_state` 校验 connectors/retriever 非空（`main.py:34-45`）、拼主系统提示（带当日日期，`main.py:52-55`）、domain_rules 来自 custom_analyses+acronyms（`main.py:48`）→ 图执行：entities 抽取写 `path_state["entities"]` → 语义检索+图扩展得候选 → LLM 过滤 → 候选(表 schema+相似查询片段)进 SQL 构造 prompt → sqlglot 按方言校验 → 意图校验（问题 vs SQL 是否答非所问）→ 执行 → ResponseAgent 写 `path_state["final_response"]`（`response.py:90`）→ `_extract_answer`（`main.py:73-86`）兜底取最后一条 message。

## 设计决策

1. **阶梯降级而非一次生成**：候选片段失败 4 次降级到整表构造、8 次放弃——把"构造不出来"当成一等出口（unconstructable agent 专职体面认输）。
2. **双重校验分工**：validate_sql_query 是语法层（sqlglot 静态解析），validate_intent 是语义层（LLM 判断是否答非所问）——两层失败都回流 reconstruct，但意图层有跳过开关（>5 次重建后放弃意图校验保交付）。
3. **决策字符串协议**：agent 间通信靠 `decision` 字符串+edge map，LangGraph 对非法值直接抛错（`text_to_sql_graph.py:119-121` 注释明言这是免费护栏）。
4. **结构化输出自愈**：ValidationError 反馈给模型重试而非立即失败（`llm_invoke.py:41`），配合 function_calling method。
5. **重对象入 state**：LLM/连接器/检索器随 state 流转，agent 可单测（mock state dict）也免了全局单例。

## 新人提示

- `state.py:51-55` 有文档/代码错位：docstring 说用 `normalized_question`，代码读的是 `path_state["initial_question"]`——排查"问题没被归一化"时先看这里。
- `route_translation` 未接线（见上），加多语言支持时别假设它已在跑。
- `recursion_limit=45` 与 8 次尝试上限、5 次重建上限是三道独立的保险丝，改动任一都要重算最坏路径长度（fallback 分支会重复经过 validate 链）。
- 新增 connector 必须实现 `dialect` 与 `database_name`（`sql_database.py:47-49`），否则方言校验与连接路由双双失灵。
- `node_visit_counts`（`text_to_sql_graph.py:156`）是现成的调试入口：一次 run 结束看它就知道循环卡在哪个 agent。
