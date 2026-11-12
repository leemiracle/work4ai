# 01 · LangGraph 三层架构：core 抽象 → agents → nodes → graph

## 角色定位

One-Eval 用 LangGraph 把「自然语言评测需求 → 基准 → 下载 → 推理 → 指标 → 报告」组织成可中断、可恢复的有状态图。地基是 `one_eval/core/` 四件套：`state.py`（状态）、`agent.py`（Agent 抽象）、`node.py`（节点抽象）、`graph.py`（图构建器），外加 `serving/custom_llm_caller.py`（LLM 调用抽象）。分层：serving 打 OpenAI 兼容 API；agents 封装「角色+提示词+解析」；nodes 是节点外壳；graph 目录用 `GraphBuilder` 拼图。

## 内部结构

- **BaseAgent**（core/agent.py:17）：三个抽象属性 `role_name`/`system_prompt_template_name`/`task_prompt_template_name`（agent.py:73-89）；`parse_result` 剥 \`\`\`json 围栏再解析，失败降级 `{"raw": content}`（agent.py:91-106）。子类基座 `CustomAgent`（agent.py:113）的 `create_llm`（agent.py:150）按 `DF_MODEL_NAME > OE_MODEL_NAME > self.model_name` 解析模型，皆空抛 ValueError（agent.py:153-162）；`run`（agent.py:179-192）组装双消息后 `await llm.ainvoke`。`api_url` 默认硬编码公网端点 `http://123.129.219.111:3000/v1`（agent.py:128-131）。
- **BaseLLMCaller / CustomLLMCaller**（serving/custom_llm_caller.py:16/38）：双通道——无工具时 `_call_raw_api` 用 httpx 直打 `/chat/completions`，429/502/503/504 重试 3 次（custom_llm_caller.py:148-168）；要工具才落回 `ChatOpenAI.bind_tools`（224-229）。超时兜底 60s（66-70）。
- **BaseNode**（core/node.py:7）：仅 26 行，`run` 抽象 + `__call__` 直通（node.py:17-19）。nodes/ 有两道人工闸门：`InterruptNode`（nodes/interrupt_node.py:17，validator 拦截闸门）与 `PreEvalReviewNode`（nodes/pre_eval_review_node.py:11，评测前一次性确认闸门），均靠 `interrupt()`+`Command(goto=...)` 暂停与跳转。
- **GraphBuilder**（core/graph.py:57）：`add_node/add_edge/add_conditional_edge` 流式收集；`build`（graph.py:178-201）统一用 `_wrap_node_with_tools` 包装节点——透传 `RunnableConfig`、注册角色级工具（graph.py:135-176）。

## 外部连接

core 向上被 9 个业务 Agent（agents/）与 15 个节点文件消费；向下依赖 `utils/prompts.py` 的 `prompt_registry` 与 `toolkits/tool_manager.py` 单例 `get_tool_manager()`（tool_manager.py:57-62，pre/post 工具按角色分组）。LangGraph 侧只消费 `StateGraph`/`interrupt`/`Command`/`BaseCheckpointSaver` 四个原语。

## 数据流

`NodeState`（core/state.py:79，含 user_query/benches/metric_plan 等 20 余字段）进入 `node.run(state)` → 节点实例化 Agent → 渲染双模板 → `create_llm` 产 Caller → httpx 调 API 回 `AIMessage` → `parse_result` 得 dict → 写 `state.result[role_name]` → 返回 state 或 `Command`。状态深拷贝做 checkpoint（state.py:134-137），字段拼错被 `update()` 的 hasattr 断言拦下（state.py:127-131）。

## 设计决策（含批判）

1. **Agent/Node 双层分离**：Node 不懂 LLM、Agent 不懂图，职责干净；代价是每节点都「实例化 → run → 丢弃」，无复用。
2. **`__init_subclass__` 试实例化**（agent.py:20-27）：子类定义即实例化取 role_name，注释明言「移除AgentRegistry注册」——只做空跑校验，历史包袱。
3. **TypeError 降级猜测**（graph.py:159-168）：包装器先按 `(state, config)` 调，捕获含 "argument" 的 TypeError 再退回只传 state；自认难区分参数不匹配与内部报错，误吞内部 TypeError 风险真实存在。
4. **默认端点硬编码**：私有化部署必须显式设 `OE_API_BASE`/`OE_API_KEY`，否则流量打到公网 IP。

## 新人提示

阅读顺序：`core/state.py` → `core/node.py` → `core/agent.py` → `serving/custom_llm_caller.py` → 任一 node（query_understand_node.py:15，28-42 行即全部逻辑）。写新 Agent 只需继承 CustomAgent、实现三个模板名属性、在 prompts 注册模板；写新节点继承 BaseNode 再 `add_node`。调试先看 `parse_result` 是否返回 `{"raw": ...}`——那是模型没吐合法 JSON 的信号。
