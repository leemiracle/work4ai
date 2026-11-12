# 05 LangGraph 工作流：ReAct 图工厂与 GAIA 答案清洗链

## 角色定位

本篇串联三个文件：register.py 里的 **ReAct 工作流工厂**（agent_node/should_continue/StateGraph 组装，register.py:190-260）、utils/answer_cleaning.py 的 **LLM 答案清洗器**（answer_cleaning.py:66）、scripts/enrich_gaia_dataset.py 的 **GAIA 数据集预处理**。三者构成一条面向基准评测的完整链路：enrich 把数据集问题改造成 agent 可消化的形态 → ReAct 图跑完任务 → clean_answer_with_llm 把自由文本答案规整成可与 ground-truth 字符串比对的标准答案。这是 sandbox_agent 区别于"演示玩具"的部分——它从数据、执行到评分口径都为 GAIA-style evaluation 做了工程化。

## 内部结构

**状态与图**。`AgentState(TypedDict)`（register.py:107）三键：`messages` 带 `add_messages` reducer（register.py:110，LangGraph 惯例：新消息按 ID 合并追加而非整表覆盖）、`iteration_count`、`sandbox_id`。图是经典二节点 ReAct：`agent_node`（register.py:191）先查 `iteration >= config.max_iterations`，超限则不调 LLM、直接吐一条"已达最大步数"的 AIMessage 收尾（register.py:197-205）；否则把 SystemMessage 每轮前置到消息列表头部（register.py:208）再 `llm_with_tools.ainvoke`（register.py:211），返回时 `iteration_count + 1`（register.py:215）。`should_continue`（register.py:218）只看末消息有无 `tool_calls`：有则去 "tools"，无则 END（register.py:224-227）。装配：`ToolNode(tools)`（register.py:232）→ `StateGraph(AgentState)` 加两节点（register.py:235-239）→ `add_edge(START, "agent")` + `add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})`（register.py:242-249）+ `add_edge("tools", "agent")` 回边成环（register.py:250）→ compile（register.py:253）。`recursion_limit = max_iterations * 2 + 10`（register.py:258），注释算得清楚：每轮迭代耗 2 次递归（agent→tools→agent），外加 10 缓冲。

**响应函数** `_response_fn`（register.py:263）：组初始状态（HumanMessage+iteration 0+sandbox_id，register.py:274-278）→ `agent_graph.ainvoke(initial_state, config={"recursion_limit": …})`（register.py:282-285）→ 取 messages 末条 content（register.py:288-292）→ **`clean_answer_with_llm(llm, input_message, raw_response)`**（register.py:295）→ 异常兜底成错误字符串返回（register.py:301-303）。

**清洗器**。`_ANSWER_CLEANING_PROMPT`（answer_cleaning.py:25-63）三段规则：提取（剥 "The answer is…" 类前言、不改实质、公式不得截断，answer_cleaning.py:35-41）、格式（按题型定型：数字裸输出/列表用指定分隔符/Yes-No 首字母大写，answer_cleaning.py:44-50；**尺度匹配**——问 "多少千小时" 而答 "17000 hours" 要输出 "17"，answer_cleaning.py:51-53；大小写与标点规则，answer_cleaning.py:54-58）、输出（只出净答案，answer_cleaning.py:61-62）。函数体三层降级：空答案原样返回（answer_cleaning.py:87-89）；≤3 字符的纯数字直接短路不调 LLM（answer_cleaning.py:93）；LLM 调用后双护栏——空结果回退原文（answer_cleaning.py:106-108）、清洗结果比原文长 2 倍+50 判"可疑"也回退（answer_cleaning.py:109-111）；任何异常一律回退 raw（answer_cleaning.py:116-118）。

**enrich 脚本**。GAIA 原始 Question 列不含附件路径，而沙箱里附件是 UUID 命名的，agent 无从对号——脚本把 `[Attached file for this task: /workspace/input/{file_name}]` 前缀拼进有附件的问题（enrich_gaia_dataset.py:50、82），幂等可重跑（已 enrich 的跳过，enrich_gaia_dataset.py:78-79），输出 enriched parquet（enrich_gaia_dataset.py:90）。

## 外部连接

- **LangGraph**：StateGraph/START/END/ToolNode/add_messages 全部来自 langgraph 与 langchain-core（register.py:22-31）——本 example 是 NAT 框架内嵌裸 LangGraph 的样板（不经 NAT 自带 workflow 组件）。
- **与第 1、3、4 篇的接缝**：图里的 tools 即 `create_all_tools` 产物（register.py:173）；system_prompt 每轮前置（register.py:208）意味着工具清单变化只需改工厂层。
- **提示词-数据闭环**：system_prompt.py:84-85 的规则"If the question starts with `[Attached file for this task: /workspace/input/xxx.ext]`, use that exact path"与 enrich_gaia_dataset.py:50 的前缀模板**逐字对应**——数据格式与行为规范由两个文件共同锁定，改一处必须同步另一处。
- **评测配置**：config_gaia.yaml 用 GAIA_LEVEL/LLM_TYPE/LLLM_MODEL 环境变量参数化（头部注释），`nat eval` 命令消费 enriched 数据集。

## 数据流

一轮 ReAct 循环：HumanMessage 入 state → agent_node（SystemMessage+历史 → LLM → AIMessage+tool_calls）→ should_continue 路由到 tools → ToolNode 并发执行工具调用 → 结果以 ToolMessage 经 add_messages 合并 → 回边再到 agent_node，iteration+1。终止三出口：无 tool_calls（模型认为答完）、迭代上限（register.py:197）、recursion_limit 兜底。出口后统一过清洗器：question+raw answer 双输入（answer_cleaning.py:97-99）→ 规整答案字符串。评测侧独立流：metadata.parquet → enrich_dataset → enriched parquet → GAIA runner 对比 ground-truth。

## 设计决策

1. **SystemMessage 每轮动态前置**（register.py:208）而非一次注入 messages——state 保持纯对话流，提示词可随配置换装，也避免 add_messages reducer 对 system 消息的 ID 处理问题。
2. **两套刹车**：业务侧 max_iterations 给模型"优雅收尾"机会（还能说总结，register.py:199-205），框架侧 recursion_limit 防失控（register.py:258）——前者体验优先、后者安全兜底，*2+10 的换算公式使两闸同步。
3. **清洗器是"evaluator 对齐"而非"能力增强"**：它只修格式不改事实（answer_cleaning.py:38-39），三重回退护栏保证清洗失败永不劣于原文——评测链上的部件必须 fail-open。
4. **≤3 字符纯数字短路**（answer_cleaning.py:93）是省钱针：基准答案多是短数字，没必要为 "42" 调一次 LLM。
5. **enrich 前缀是 dataset 侧的"工具提示注入"**：把环境事实（哪个文件属于本题）编码进问题文本，比让 agent ls 猜测可靠得多；幂等设计（enrich_gaia_dataset.py:78-79）让它可安全重跑。

## 新人提示

- 改图结构（如加规划节点/记忆节点）只需在 register.py:235-250 区间动刀：add_node + 改 conditional_edges 映射表，AgentState 加键即可持久化新状态。
- ToolNode 默认**并行**执行一次 AIMessage 里的多个 tool_calls——沙箱是单实例，工具会并发打同一容器，写文件竞态要小心。
- 清洗器复用主 LLM（register.py:295 传入的 `llm`），不额外配模型；若主模型指令跟随差，清洗质量会直接拖累基准分数。
- recursion_limit 漏传会让长任务在 LangGraph 默认 25 步处暴毙——本仓在 ainvoke config 里显式传（register.py:284），复刻时别丢。
- 测试锚：test_register.py 锁配置默认值；GAIA 端到端无 CI 覆盖，跑 eval 前先用小 GAIA_LEVEL=1 子集验证。
