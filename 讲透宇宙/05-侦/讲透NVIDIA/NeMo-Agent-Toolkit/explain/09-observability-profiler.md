# 09 · 可观测性与性能剖析：observability 管线 + profiler 计费预测

## 一、角色定位

NAT 把「看得见」当成一等能力而不是外挂：core 的 `observability/` 是一条自研的 OTEL 风格事件管线（导出器+处理器），负责把 workflow 执行中的 intermediate step、span、token 用量变成可导出的遥测；`nvidia_nat_opentelemetry` 包把这条管线对接到标准 OTEL 生态；`nvidia_nat_profiler` 包则站在管线上游做性能经济学——LLM token 计费、GPU 容量估算、并发吞吐预测。三者合起来回答 agent 生产环境的三个终极问题：刚才发生了什么（追踪）、花了多少钱（计费）、要多少卡（容量）。

这一层与 ATIF 评测体系（见 06 篇）共享同一份数据底座——intermediate step 流。区别在出口：评测出指标，可观测出遥测，profiler 出账单与采购建议。

## 二、内部结构

**core observability 管线**（`packages/nvidia_nat_core/src/nat/observability/`，37 文件）的三段式：

1. **导出器基座**：`base_exporter.py:40` 的 `IsolatedAttribute` 描述符是精妙设计——导出器实例可被「隔离复制」，per-session 数据不会串写；`base_exporter.py:103` `class BaseExporter(Exporter)` 是抽象基类。具体导出器四类：file/raw/span/processing（`exporter/file_exporter.py` 等同目录）。
2. **导出器管理器**：`exporter_manager.py:26` `class ExporterManager` 是管线的总开关——`add_exporter`（exporter_manager.py:79）/`remove_exporter`（exporter_manager.py:94）/`get_all_exporters`（exporter_manager.py:127）管理生命周期，`create_isolated_exporters`（exporter_manager.py:136）按 context state 派生隔离副本，`shutdown_timeout` 默认 120 秒（exporter_manager.py:46）保证优雅关停。Workflow 基类把它直接挂为属性（`builder/workflow.py:96` `exporter_manager` property）。
3. **处理器族**：`processor/processor.py:27` `class Processor(Generic[InputT, OutputT], ABC)` 定义 `process()` 单方法契约（processor.py:65）——纯函数式流处理。已实现处理器：`IntermediateStepSerializer`（processor/intermediate_step_serializer.py:22，把中间步骤序列化，输入类型直引 `data_models/intermediate_step.py` 的 IntermediateStep）、`BatchingProcessor`（processor/batching_processor.py:33，攒批回调）、`CallbackProcessor` 派生系（callback_processor.py）、FalsyBatchFilter、SpanTagging，以及脱敏子族。

**脱敏子族**是这层的隐藏宝石：`processor/redaction/redaction_processor.py:38` `RedactionProcessor` 抽象 + :81 `RedactionContextState` + :92 `RedactionManager` + :145 `RedactionContext` 四件套，配套 contextual_redaction_processor.py / span_header_redaction_processor.py 等实现，在遥测出门前清洗敏感字段——NAT 对「可观测 vs 泄密」的张力给出了管线内答案，而不是让用户自己擦日志。

**mixin 配置体系**（`observability/mixin/`，8 文件）：file_mode.py、serialize_mixin.py、tagging_config_mixin.py、redaction_config_mixin.py 等把可配置面拆成可组合混入，供 data_models 与导出器共享——这是 NAT「config 一切」哲学在遥测域的延续。

**OTEL 对接**（`packages/nvidia_nat_opentelemetry/src/nat/plugins/opentelemetry/`，19 文件）：otel_span_exporter.py、otlp_span_adapter_exporter.py、otlp_span_redaction_adapter_exporter.py、span_converter.py——把 NAT 内部 span 翻成 OTEL 语义再出站，且 adapter 版自带脱敏（文件名即架构）。

**profiler 域包**（`packages/nvidia_nat_profiler/src/nat/plugins/profiler/`，48 文件）：

- `callbacks/base_callback_class.py` + `token_usage_base_model.py`：token 用量采集的挂点模型；
- `calc/calculations.py:27` `compute_slope`、:93 `_remove_outliers`、:183 `calc_gpu_estimate_based_on_slope`、:232 `calc_gpu_estimate_for_single_concurrency`——从实测延迟/吞吐点拟合斜率并外推 GPU 数量；`calc_runner.py:46` `LinearFitAnalyzer`、:110 `CalcRunner` 组装计算；
- `cli/sizing.py:114` `calc_command` 与 :279 `sizing_command` 暴露 `nat profiler` 子命令；
- `decorators/latency.py:16` 起 `@latency_sensitive` 装饰器——给函数标延迟敏感级别，供 LLM 路由把高敏感请求导向低延迟后端（decorators/latency.py:23），以及 `function_tracking.py`/`framework_wrapper.py`；
- `register.py:18-21` 把 avg_llm_latency/avg_num_llm_calls/avg_tokens_per_llm_end/avg_workflow_runtime 四个 runtime_evaluator 注册为**评测器**——profiler 的产出直接变成 `nat eval` 可用的指标，两体系在此合流；
- `forecasting/model_trainer.py` 与 `config.py`：吞吐预测模型训练。

## 三、外部连接

上游：`builder/intermediate_step_manager.py` 产生的执行事件是管线主食；`data_models/intermediate_step.py` 定义其类型。下游：OTEL collector/Arize Phoenix（另有 `nvidia_nat_phoenix` 包）/W&B（`nvidia_nat_weave`）接收出站遥测；`nvidia_nat_data_flywheel` 的 trace_conversion 复用同一 span 流做微调数据回流（见 06 篇）；profiler 的 runtime evaluator 被 eval 体系消费。横向：`nvidia_nat_security` 的输出验证器与 redaction 处理器在「清洗敏感内容」上语义呼应；MCP server 侧甚至有 `memory_profiler.py`（`nvidia_nat_mcp/src/nat/plugins/mcp/server/memory_profiler.py:25`）用 tracemalloc 监控导出器与 intermediate_step_manager 的实例泄漏——可观测体系自己也被观测。

## 四、数据流

一次 `workflow.run()` 的遥测之旅：中间步骤事件由 IntermediateStepManager 发出 → IntermediateStepSerializer 序列化 → BatchingProcessor 攒批 → RedactionProcessor 按配置清洗 → ExporterManager 路由到已注册导出器（file 落盘 / OTLP 出站 / processing 再加工）→ session 结束时隔离副本（create_isolated_exporters）各自 flush，关停窗口 120s。profiler 路径独立成环：profiling 运行（examples/evaluation_and_profiling/ 提供 0-7 并发梯度脚本）产出 token 用量与延迟记录 → calc_command 读入 → compute_slope 拟合（含 _remove_outliers 去离群点）→ calc_gpu_estimate_based_on_slope 输出「目标延迟下需 N GPU」→ sizing_command 汇总成采购/部署建议。

## 五、设计决策

1. **自研管线而非直接用 OTEL SDK**：NAT 需要对 intermediate step 做细粒度控制（隔离复制、session 级 flush、脱敏），OTEL 的 exporter 语义不够，于是 core 只定义自己的 Processor/Exporter 抽象，OTEL 降级为一种出站适配（opentelemetry 包的 adapter 命名明示了这层关系）。
2. **脱敏内置在管线**：RedactionProcessor 是 Processor 的一等实现而非后处理脚本——遥测在产生点就能脱敏，避免「先落盘再清洗」的竞态窗口。
3. **空壳包的演进痕迹**：core `profiler/callbacks/__init__.py` 与 `profiler/forecasting/__init__.py` 是空文件——实现整体迁去了 nvidia_nat_profiler 包，core 只留目录骨架。读 core 时别在这里找代码（勘误：如果期望 core profiler 有实质实现，实际为空壳，真身在域包）。
4. **profiler=evaluator 的合流**：register.py 直接注册 runtime evaluator，容量数据天生是评测指标——避免了「性能工具」与「评测工具」两套数据格式。
5. **IsolatedAttribute 描述符**：用 `__set_name__`/`__get__` 协议实现导出器字段的 per-copy 隔离（base_exporter.py:73-94），比 deepcopy 轻量且类型安全。

## 六、新人提示

上手顺序：先跑 `examples/evaluation_and_profiling/` 的 profiling 示例看 JSON 轨迹长什么样 → 读 exporter_manager.py:26 一个类看懂生命周期 → 读 processor.py:27 的 30 行契约 → 再看 redaction 子族与 OTLP adapter。坑：①config 里 observability 配置错了往往静默无输出——先开 file exporter 验证事件流存在，再切 OTLP；②profiler 的 GPU 估算质量取决于并发梯度数据点数，3 个点拟合斜率误差极大，examples 的 0-7 并发脚本是最低配置；③`shutdown_timeout` 120s 内强杀进程会丢尾部批次；④core/profiler 空壳勿浪费时间；⑤latency_sensitive 装饰器只打标，不改变路由行为——路由决策要靠支持敏感度的 LLM 配置消费它。
