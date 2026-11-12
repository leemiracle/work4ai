# 06 评测体系与 ATIF：把 agent 行为变成可断言的事实

覆盖 `nvidia_nat_atif`、`nvidia_nat_eval`、`nvidia_nat_data_flywheel` 三包与 `nvidia_nat_core` 的 atif_converter。勘误：ATIF 全称是 **Agent Trajectory Interchange Format**（trajectory.py:16 docstring 明写），任务书的"Agent Tool Interaction Format"与源码不符；ATOF 全称是 **Agentic Trajectory Observability Format**。ATIF 版权头同时署 Harbor Framework Contributors（2025），即自 Harbor 上游引入并做了明示 deviation。

## 一、角色定位

这是 NAT 的差异化主线："确定性评测 agent"。LLM-as-judge 又贵又不稳，NAT 把 agent 运行固化成强校验轨迹（ATIF），让工具调用、参数、观测之间的引用关系变成机器可判定的命题，评测器在其上做确定性打分。三包分工：ATIF 定义"轨迹长什么样"；eval 运行时管"跑数据集、收轨迹、分发评测器"；数据飞轮管"把线上 OTEL 观测回流成微调数据"。同一观测底座，评测、可观测、微调三用。

## 二、内部结构

**ATIF 轨迹层级**：`Trajectory`（trajectory.py:35，ATIF-v1.7 :32）→ `steps: list[Step]`（trajectory.py:80）→ 每 Step 携 `tool_calls`（step.py:72；ToolCall 在 tool_call.py:27）与 `observation`（step.py:76；Observation 在 observation.py:27，其 ObservationResult observation_result.py:30 经 `source_call_id` 反查所属 tool_call）。Step 带 `source: Literal["system","user","agent"]`（step.py:48）与多模态 message（step.py:63）。模型自带三组结构校验：step_id 从 1 连续（trajectory.py:119）、observation 引用必须命中本 step 的 tool_calls（trajectory.py:153）、model_name/tool_calls/metrics 等仅允许出现在 agent step（step.py:119）。子代理用 `subagent_trajectories` 内嵌数组（trajectory.py:100）+ `SubagentTrajectoryRef`（subagent_trajectory_ref.py:29，必须带 trajectory_id 或 trajectory_path 之一）表达。`Metrics`（metrics.py:27）逐 step 记 token/cost/logprobs 乃至 token_ids——为 RL 回流免重分词预留；`FinalMetrics`（final_metrics.py:27）做整轨迹聚合。对 Harbor 的 deviation 处处留注释：允许空 steps（trajectory.py:78）、message 默认空串（step.py:61）。

**ATOF 事件层**：运行时观测的 JSON Lines 线格式，两种事件——`ScopeEvent`（events.py:198，start/end 成对共享 uuid）与 `MarkEvent`（events.py:241，瞬时检查点）；`category` 闭集词表 11 个（category.py:47）；行为旗标 `Flags`（flags.py:29）。载荷 `data` 不透明，形状靠 `data_schema={name,version}` 声明。**extractors.py** 是"工具交互→确定性事实"的转换核心：三个 Protocol（LlmPayloadExtractor :89 等）+ 声明式 `SchemaMap` 引擎（:200），OpenAI/Anthropic/Gemini 三家注册（:389/:534/:673），register/resolve 按 data_schema 查表（:767/:805）——新厂商只需填一张映射表。

**eval 运行时**：`atif_evaluator.py` 定义双协议——`AtifEvaluator`（:45，`evaluate_atif_fn` :48 吃 AtifEvalSample :31）与 `LegacyEvaluator`（:54，`evaluate_fn`）。`AtifBaseEvaluator`（atif_base_evaluator.py:29）是基类：子类只实现 `evaluate_atif_item`（:42），基类管信号量限并发、异常降级 score=0.0、算平均分；legacy 侧对应 `BaseEvaluator`（base_evaluator.py:54，`evaluate_item` :72）。编排：`EvaluationRun`（evaluate.py:88）的 `run_workflow_local`（:199）逐条跑 workflow，经 `pull_intermediate`（:208）收中间步骤挂到 EvalInputItem.trajectory；`EvalAtifAdapter`（atif_adapter.py:35）用 `IntermediateStepToATIFConverter`（atif_converter.py:250）一次性转 ATIF 并缓存；`run_single_evaluator`（evaluate.py:561）按 isinstance 分派——ATIF 通道走 `EvaluationHarness`（eval_harness.py:44，注释明言只认 evaluate_atif_fn），legacy 走 :575。`DatasetHandler`（dataset_handler.py:34）管数据集读取、filter/reps/去重；`EvalCallbackManager`（eval_callbacks.py:162）挂落盘钩子。

**数据飞轮**：`SpanToDFWRecordProcessor`（dfw_record_processor.py:59）把 OTEL Span 交给 `get_trace_container`（span_to_dfw.py:45）——按 span 属性 `nat.framework`（:62）判源，Pydantic discriminated union 自动匹配已注册 schema；`TraceAdapterRegistry`（trace_adapter_registry.py:26，`register_adapter` :37 装饰器登记源→目标转换，`convert` :77）；`span_extractor.py` 顺带抽 token 用量（:25）。终点 `DFWElasticsearchTelemetryExporter`（register.py:30，注册名 :32，构建函数 :46）批量写 Elasticsearch 进 NVIDIA Data Flywheel。勘误：grep 证实 data_flywheel 全包零 ATIF 引用——飞轮走 OTEL Span→DFW 专属 schema 的独立线，与 ATIF 评测线只在观测源头共享，别在 DFW 转换器里找 ATIF。

## 三、外部连接

ATIF 被 core atif_converter、eval atif_adapter、FastAPI generate 路由（generate.py:254 提到返回 ATIF steps）消费；ATOF extractors 服务于 ATOF→ATIF 转换（规范 atof-to-atif-conversion-guide.md，I-10 条明确"给定排序事件流与稳定 extractor 注册表，转换是确定性的"）。eval 依赖 core 的 `Workflow.result_with_steps`（workflow.py:116）取轨迹；data_flywheel 挂在 core telemetry exporter 供给上。

## 四、数据流

一次 `nat eval`：DatasetHandler 加载数据集 → run_workflow_local 逐条跑 workflow 并收 IntermediateStep 轨迹 → EvalAtifAdapter 转一次 ATIF 缓存 → run_evaluators 双通道分派（ATIF→EvaluationHarness；legacy→evaluate_fn）→ EvalOutput 平均分+逐项 reasoning → callbacks 写结果。飞轮独立并行：serve 期 OTEL span → DFW 转换器 → ES exporter 批量上送。

## 五、设计决策

1. **契约先行**：轨迹是 pydantic 强校验数据而非日志文本——step_id 连续性、observation↔tool_call 引用闭合（trajectory.py:153）、agent-only 字段约束（step.py:119）都在模型层强制。评测器拿到的是结构化事实，可写纯确定性断言，比 judge 打分可复现且零 API 成本——确定性评测 agent 的机制根基。
2. **双协议过渡**：AtifEvaluator/LegacyEvaluator 并存（atif_evaluator.py:45/54，evaluate.py:561 分派），新评测器上 ATIF 线、旧的保留不破坏。
3. **观测/交换分层**：ATOF 管运行时事件流（低假设、载荷不透明），ATIF 管事后轨迹（强 schema、面向评测交换）；转换独立成 spec 且以确定性为目标。
4. **声明式抽取**：SchemaMap 让新厂商适配退化为填一张路径映射表（extractors.py 注册即可），扩展零代码。
5. **微调视角前置**：Metrics 收 token_ids/logprobs（metrics.py），飞轮收 token 用量（span_extractor.py:25）——评测与训练吃同一底座。
6. **上游 deviation 显式化**：对 Harbor 的每处偏离留源码注释，升级可对账。

## 六、新人提示

读序：trajectory.py → step.py → atif_evaluator.py → atif_adapter.py → evaluate.py，半天可通。实跑 examples/evaluation_and_profiling/simple_web_query_eval（atif-eval-readme.md 与 eval_config_atif.yml 现成）。坑：① 评测器继承 AtifBaseEvaluator 只实现 evaluate_atif_item，抛异常被包成 score=0.0 错误项而非中断，排查看 reasoning.error；② 全部模型 `extra="forbid"`，私货字段只能塞 Step.extra/ToolCall.extra 保留槽；③ v1.6→v1.7 变化：SubagentTrajectoryRef 的 session_id 不再是解析键，只带 session_id 的旧 ref 校验失败；④ 中间步骤→ATIF 字段对不上先查包内 intermediate-step-to-atif-mapping.md 再怀疑评测器。
