# 02 · training_telemetry 与 TrainingRecorder 千行主线

## 角色定位

one_logger_training_telemetry 把通用 span 模型升级成**训练语义层**：标准 span 树（19 个 StandardTrainingJobSpanName）、标准事件族、生产力度量（productive work）核算，以及 1068 行的 TrainingRecorder 主实现。它是"训练效率审计"（吞吐/浪费算力/存档节奏）在遥测侧的落点。

## 内部结构

api/training_recorder.py:187 的 `TrainingRecorder(DefaultRecorder)` 承载三大状态机：`_TrainingState`（training_recorder.py:95-184）管迭代数/样本数/FLOPs/tokens/时间戳与五把 MultiWindowTimer（training_recorder.py:49-66 分别跟训练、验证、同步/异步存档、读档窗口，字段挂载 :115）；`_ProductivityState`（training_recorder.py:70-91）按迭代号记快照；`productivity_state: Dict[int, _ProductivityState]`（:179）配 `max_reported_productive_train_iterations`（:184）防异步 ckpt 乱序回填。20+ 个 `on_*` 钩子（training_recorder.py:360 on_app_start、:688 on_training_single_iteration_start、:938 on_save_checkpoint_start、:986 on_save_checkpoint_success）全部 @safely_execute 包裹（如 :442）——遥测故障绝不打断训练。`_get_rank()` 读 RANK 环境变量（training_recorder.py:45）。

## 外部连接

上游 TrainingTelemetryProvider（training_telemetry_provider.py:43，SingletonMeta 单例）是 OneLoggerProvider 的训练特化：builder 模式 with_base_config/with_config_override/with_exporter/configure_provider 增量拼装（:85-115）；默认黑名单八个高频短 span 不导出（:25-34 DEFAULT_SPANS_EXPORT_BLACKLIST：TRAINING_SINGLE_ITERATION/MODEL_FORWARD/MODEL_BACKWARD/OPTIMIZER_UPDATE 等——量太大）；_ReadOnlyConfig（:37-40）frozen 防篡改。下游消费 DefaultRecorder 的 exporter 分发与 ExportCustomizationMode 黑白名单机制（default_recorder.py:29-34）。标准名词表在 spans.py:5 与 events.py:9，是跨框架对齐的锚点词汇。

## 数据流

训练循环 → on_training_single_iteration_start/end 配对开合 MultiWindowTimer → 每 N 迭代 `_maybe_send_training_metrics_update`（training_recorder.py:752）把聚合指标打成 TRAINING_METRICS_UPDATE 事件（events.py:34，docstring :28-33 说明为何要聚合：循环太长、单步太碎）→ 存档时 on_save_checkpoint_start（training_recorder.py:938）记 _ProductivityState 快照，成功后（on_save_checkpoint_success :986）该迭代号之前的工作被确认为 productive → 导出时黑名单 span 被 DefaultRecorder 过滤。

## 设计决策

1. **聚合导出**：log_every_n_train_iterations 控制打点密度，事件时间戳反映"何时记录"而非"何时执行"（events.py:30-36 docstring）。
2. **生产力度量以 checkpoint 为准**：失败作业里最后一次成功存档之后的工作算浪费（training_recorder.py:172-178 注释）——异步存档下不能假设"存档成功时刻的状态就是快照内容"，所以按迭代号字典存。
3. **同步/异步存档分开建 span**：CHECKPOINT_SAVE_ASYNC 只含触发阻塞时间，真正写盘归 CHECKPOINT_SAVE_FINALIZATION（spans.py:44-52）。
4. **包根 training_recorder.py 是 0 字节空文件**：真身在 api/ 下，空壳是上游兼容遗留（甄别勘误见 README）。

## 新人提示

读 :95-184 的 _TrainingState 字段注释是理解全模块最快路径；对接新框架时照抄 spans/events 的标准名而不是自造词，后端报表依赖这套词汇；Lightning 用户直接用集成包（见 03 篇），别手写 on_* 调用。
