# 04 · 查询与 Agentic 检索：ResolvedQueryPlan 与 nemo_agent 双模式

> 路径相对 `nemo_retriever/src/nemo_retriever/`。

## 角色定位

检索侧的双层结构：**经典查询**（`query/workflow.py`，380 行）把 QueryRequest 解析成可复用的检索计划，走"嵌入→向量库→（可选重排）"一步直出；**Agentic 检索**（`query/agentic.py` + 私有库 `_agentic/nemo_agent/`，图谱 30 节点）在经典检索之上加 LLM agent 循环——agent 反复检索、思考、再检索，最终产出文档选择（select 模式）或带引用的答案（answer 模式）。两层共用同一套向量库与嵌入配置，差异只在"检索一次"还是"检索到满意为止"。

## 内部结构

**经典层**：`query/workflow.py:94` `ResolvedQueryPlan` dataclass 一次性固化 top_k/candidate_k/lancedb_uri/table_name/retrieval_mode/embed_kwargs/rerank 配置；`resolve_query_plan`（`:139`）从 QueryRequest 抽取；`retriever_kwargs()`/`create_retriever()` 让服务进程反复建 Retriever 而不用重复解析（服务热路径的关键）。`query_documents`（`:181`）与 `query_documents_with_metadata`（`:164`）是查询双入口。

**Agentic 入口双算子**（`query/agentic.py`）：`AgenticQueryInputOperator`（`:110`）在 process 里把输入 DataFrame 归一成 `query_id`+`query_text` 两列——依次尝试 query_text/query/text 列名（`:122-128`），缺 query_id 就按行号补（`:129-130`）；`AgenticSelectionOutputOperator`（`:138`）反向：校验必需列 `{query_id, doc_id, rank}`（`:151-154`），按 query_id 分组、组内按 rank 排序组装 hit 列表，doc_id 回填 pdf_page（`:157-166`）。这一对是 agentic 查询图的入站/出站适配器，使 agent 管线与经典管线在 Retriever 接口上同构。

**配置与校验**：`AgenticRetrievalConfig`（`:174`）冻结 dataclass，三十余字段覆盖 vdb/embed/rerank/LLM 全栈；`__post_init__`（`:225-259+`）做互斥推演——后端合法值集 `{"openai_compatible","in_process"}`（`:60-61`），给了 `invoke_url` 就必须 openai_compatible、没给就必须 in_process（`:234-242`）；`llm_client` 与 `llm_backend` 是两个独立轴（WHERE 跑 vs WHICH 适配器，`:245-249` 注释）。top_k 驱动 ReAct 目标与每跳深度（`:218-221`）。

**Agent 本体**（`_agentic/nemo_agent/`）：`loop.py:178` `_BaseAgentLoop` 是通用循环引擎——`_RunState`（`loop.py:137`）承载每查询私有状态（一实例可并发服务多查询），工具执行异常有专门类型 `ToolExecutionError`（`loop.py:69-78`），异常分类进 `AgentError` 结果而非炸循环。`agent.py:72` `Agent` 在其上加双模式：构造期按 `config.mode` 选 end tool——select 模式用 `final_results` 工具+`06_select_lean_v1.j2` 提示词，answer 模式用 `log_answer`+`05_answer_lean_v1.j2`（`agent.py:112-124`）；`run_sync`（`agent.py:240`）同步入口。标准工具三件：retrieve（检索回调包装，过取/去重记账）、think_tool、end_tools。LLM 多后端在 `llm/`（litellm/callable/usage/errors），提示词模板 j2 八张在 `prompts/`。

**运行时**：`AgenticRetriever`（`query/agentic.py:387`）把 config 变成可跑的检索器（构造期组 embed_kwargs，`:404-411`）；管线适配器 `operators/graph_ops/react_agent_operator.py:80`（510 行）把 nemo_agent 包成 CPU 算子——`_retrieve_adapter`（`:243`）注入 `(query_text, top_k)→hits` 回调，`_run_single_query`（`:375`）跑单查询，输出按"每查询×每文档×每步"爆行（schema `:94-110`：step_idx=0 是种子检索，末尾合成 final 步），供 `RRFAggregatorOperator`（`operators/graph_ops/rrf_aggregator_operator.py:18`）融合多路结果；`pop_query_usage`（`:292`）把 LLM 用量冒泡给调用方。

## 外部连接

经典层向下连 `operators/vdb.py:274` RetrieveVdbOperator 与 05 篇的 LanceDB；rerank 连 `models/local/rerank_v2.py` 系或 NIM。agentic 层向下连 `models/local/agent_llm.py`（in_process vLLM）或 litellm 端点；查询编排上，`query/workflow.py:186` `build_agentic_config` / `:244` `build_agentic_retriever` 把 QueryRequest 翻成 agentic 配置。服务面：`service/routers/ingest.py:1725` `/v1/answer` 与 `:1886` `/v1/query` 是 HTTP 入口；`service/agentic_query.py` 与 vectordb 服务的专用线程池（`service/vectordb_app.py` 槽位 100）承接并发。`evidence/`（引用溯源）与 `shaping/`（结果整形）是查询结果的两个后处理包。

## 数据流

经典：QueryRequest → resolve_query_plan（一次）→ Retriever.query 循环复用 → hits（RetrievalHit 形态，见 05 篇）→ 可选 rerank → 返回。Agentic select：输入 DataFrame → AgenticQueryInputOperator 归一 → query 嵌入 → 种子检索 → ReAct 循环（LLM 决定再检索/思考/终止）→ final_results 工具收选择 → 输出爆行 → RRF 融合（种子+各跳+final）→ AgenticSelectionOutputOperator 组装 hits。Agentic answer 同循环但 end tool 换 log_answer，产出 answer+citations+citation_hits 三件（`query/agentic.py:96-104` AgenticAnswerResult 契约）。资源闭环：`query/workflow.py:271,286` 在 finally 里 `retriever.unload()`（`query/agentic.py:485` 实现，`:499-501` 反射调用 chat_fn 的 unload）确保本地 vLLM 引擎随请求释放。

## 设计决策

1. **一次解析反复使用**：ResolvedQueryPlan 把所有配置解析从每查询降为每服务/每批一次——检索延迟敏感路径上省掉重复校验。
2. **双模式共用一个循环引擎**：select/answer 只差 end tool+提示词模板（`agent.py:112-124` 的分支），检索循环、工具记账、错误分类完全复用——加第三种模式只需新 j2+新 end tool。
3. **私有库划界**：nemo_agent 放 `_agentic/` 下划线目录，意图是内部实现不对外承诺稳定性；对外稳定面是 ReActAgentOperator 与 AgenticRetriever 两个包装。
4. **用量追踪算子内建**：usage 不靠事后解析日志，而是 `pop_query_usage` 主动冒泡（`react_agent_operator.py:292`），服务层能按查询计费。
5. **爆行输出换融合自由**：agent 输出按步爆行而非只留 final，让 RRF 在种子/各跳/final 多路间加权融合——宁可输出宽一点，融合策略留给下游。

## 新人提示

- 判断自己该用哪层：只要"一次向量检索+重排"够用就别上 agentic——agent 循环的 LLM 成本与延迟是经典检索的数十倍。
- `AgenticQueryInputOperator` 只认三列名（query_text/query/text），自定义管线输出列名不同时要先加一列同名列（`:122-128`）。
- in_process 后端默认拉本地 vLLM 跑 nemotron-8b（`query/agentic.py:62-63`），显存不足改 `local_gpu_memory_utilization`（`:195`）或换 invoke_url 走远程。
- 查 agent 行为问题先读 `prompts/` 的 j2 模板——循环行为大部分是提示词决定的，不是代码。
- 泄漏排查：服务里 agentic 查询后显存不回落，检查调用方是否走的是带 finally unload 的入口（`query/workflow.py:271,286`），自建路径要手动调 `AgenticRetriever.unload()`。
