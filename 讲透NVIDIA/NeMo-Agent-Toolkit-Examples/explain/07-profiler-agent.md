# 07 · profiler_agent：用 agent 分析 LLM 遥测的三节点图

## 角色定位

`profiler_agent` 是"agent 分析 agent"的元应用：从 Phoenix 可观测性 server 拉取 LLM trace，产出 token 用量、时序流程图与用户查询分析报告。它在示例仓中的定位是展示**不用 ToolNode 的另一种 LangGraph 编排**——LLM 不做 tool calling，而是输出结构化执行计划，由图节点顺序消费。包名 `nat_profiler_agent`，注册名 `profiler_agent`（`register.py:34`）。

## 内部结构

核心类 `ProfilerAgent`（`agent.py:52`）持 llm、工具 dict、response_composer 工具与 retry 参数（`agent.py:59-72`），内部常驻一个 `PydanticOutputParser(pydantic_object=ExecPlan)`（`agent.py:71`）。状态 `ProfilerAgentState`（`agent.py:40`）七字段：`exec_plan`/`messages`/`df_path`/`trace_infos`/`end_condition`/`retry_count`/`user_query`。

图构建在 `build_graph`（`agent.py:98-117`）：三节点 agent/executor/response_composer，agent 与 executor 之后各挂同一个 `conditional_edge`（`agent.py:105-112`）——`exec_plan.tools` 队列非空去 executor、空则去 response_composer（`agent.py:79-82`）；节点函数三件：`agent_node`（`agent.py:122-146`，LLM 输出经 parser 解析成 ExecPlan，失败则用 `RETRY_PROMPT`（`prompts.py:16`）带格式说明重试，`agent.py:138-142`）；`executor_node`（`agent.py:148-162`）从队列 popleft 执行，`px_query` 是特例——只有它接收完整 ExecPlan 参数（`agent.py:151-154`），其余工具只吃 `df_path`；`response_composer_node`（`agent.py:164-174`）在 `trace_infos` 为空时直接注入"无 trace"消息退出（`agent.py:166-167`）。

数据模型在 `data_models.py`：`ExecPlan`（`data_models.py:24`）核心是 `tools: deque[str]` 加时间窗/last_n/project_name；三工具输出分别填充 `TraceFlowInfo`（`data_models.py:52`）、`TokenUsageInfo`（`data_models.py:60`）、`PxQueryOutput`，最终聚合进 `TraceInfo`（`data_models.py:94`）。

工具四件（`tool/` 目录，各自独立注册）：`px_query`（`tool/px_query.py:35` 起，Phoenix Client 拉 spans dataframe；project 名为 "default" 时回落到配置的 `default_project_name`，`tool/px_query.py:124-125`，该字段还有非空校验 `tool/px_query.py:49-54`；last-n 模式按 trace 最早 start_time 倒序截取，`tool/px_query.py:133-147`；从 span 的 `attributes.input.value` 提取每个 trace 的用户原始 query，`tool/px_query.py:163-165`；结果落临时 CSV 传下游，`tool/px_query.py:160`）。`flow_chart`（`tool/flow_chart.py:59` 注册，按 `context.trace_id` 分组后逐 trace 画 matplotlib 时序图，`tool/flow_chart.py:91-95`）。`token_usage`（`tool/token_usage.py:57` 注册，同样分组统计，注意其 finally 块刻意**不清理**临时目录因为图片路径后续还要用，`tool/token_usage.py:109-111`）。`response_composer`（`tool/response_composer.py:45` 注册，读取 flow chart 与 token 图文件转 base64 内嵌进 HTML 回答，`tool/response_composer.py:62-64`、`tool/response_composer.py:70`）。

## 外部连接

向上：`register.py:59` 的 `@register_function` 挂进 NAT，`builder.get_tools`（`register.py:78`）按配置的 `tools` 名单取工具、`builder.get_tool("response_composer")`（`register.py:85`）单独取收尾工具。向外：Phoenix server（`configs/config.yml` 配 `phoenix_url`，默认 localhost:6006）；同一个 config.yml 还在 `general.telemetry.tracing` 节把 Phoenix 配为**本 agent 自身的 trace 上报后端**——profiler 分析的正是包含自己在内的 LLM 遥测。向下依赖 langchain/langgraph、phoenix client、matplotlib/pandas。

## 数据流

一次查询的完整路径：`_profiler_agent`（`register.py:91`）把 SYSTEM_PROMPT 模板（`prompts.py:29`，注入当前时间、工具清单与 JSON 格式说明）与用户问题拼成 SystemMessage → graph.ainvoke（`register.py:107`，`recursion_limit=(max_iterations+1)*2`）→ agent_node 产出 ExecPlan（约定 px_query 必须第一，`prompts.py:40`）→ executor 执行 px_query → `update_state`（`agent.py:176`）match-case 识别 `PxQueryOutput`（`agent.py:179`）把 `df_path` 写入 state、把"已拿到 DataFrame，别再调 px_query、请继续调全部分析工具"的护栏消息追加进 messages（`agent.py:183-188`）→ 后续 flow_chart/token_usage 依次消费同一 CSV，输出分别按 `agent.py:190`/`agent.py:197` 分支聚合进 `trace_infos` → 队列清空后 response_composer 把所有 TraceInfo 渲染成 HTML 返回，取 `state["messages"][-1].content` 作为函数输出（`register.py:108`）。

## 设计决策

1. **JSON 计划而非 tool calling**：LLM 一次产出全量执行序列，图按序消费——这是 ReWOO（Reasoning WithOut Observation）风格的省 token 编排，代价是失去按观察结果动态调整的能力，所以用护栏消息（`agent.py:183-188`）补偿。
2. **px_query 的特殊地位**：它产出全部分析工具的公共输入（CSV 路径），因此在 prompt（`prompts.py:40`）、参数传递（`agent.py:151-154`）与 state 更新（`agent.py:179-188`）三处都被特判。
3. **文件系统作总线**：工具间不传 DataFrame 而传 `df_path`，让 matplotlib 类工具直接复用 pandas 读 CSV 的成熟路径，也天然隔离了大对象不进 state。
4. **重试的边界处理**：parse 失败走 retry_prompt；`conditional_edge` 自身异常且 `retry_count` 到顶时直接结束并明说"无有效输出"（`agent.py:84-87`），不会死循环。
5. 值得批评的点：`token_usage` 不清理临时目录（`tool/token_usage.py:109-111`）与 `px_query` 在生成器 yield 后清理（`tool/px_query.py:179-181`）策略不一致，长跑进程会积累图片文件。

## 新人提示

跑通需要先有 Phoenix（`pip install phoenix` 后 `phoenix serve`）与被观测的 LLM 应用产生 trace；config.yml 的 `default_project_name` 配成被测应用 project（示例给 `simple_calculator`）。改提示词先看 `prompts.py:29-50`——格式说明由 `output_parser.get_format_instructions()` 动态注入（`register.py:99-103`），手改模板容易和 ExecPlan schema 脱节。测试基准是 `tests/test_profiler_agent.py` 与固定样本 `tests/test_spans.csv`，离线可跑。想加新分析工具：照 `token_usage` 模板写 Input(df_path)/Output(dict) 两模型 + `@register_function` 注册，然后在 config.yml 的 functions 与 workflow.tools 里同时挂上，`update_state` 需要为新输出类型补一个 match 分支（`agent.py:176-209`）。
