# 03 Workforce 编排：camel/societies/workforce/

## 1. 角色定位

Workforce 是 camel 的多智能体编排中枢：workforce.py 单文件 6239 行、约 121 个方法，加上同目录的 worker/task_channel/events/prompts 等 14 个文件构成完整子系统。它的职责是把 Task 队列经 LLM 协调分派给一组 Worker（单 agent、RolePlaying 对、甚至嵌套 Workforce），并自带任务分解、失败恢复、快照暂停、人工干预、管线编排（pipeline fork/join）等"运维级"能力。`class Workforce(BaseNode)`（workforce.py:175）自身继承节点基类——编排者也是节点，因此 `add_workforce`（workforce.py:3097）可以把一个 Workforce 整体挂进另一个 Workforce 形成层级组织。

## 2. 内部结构

状态与形态三件套：`WorkforceState`（workforce.py:132，IDLE/RUNNING/PAUSED/STOPPED 四态支撑人机干预）、`WorkforceMode`（workforce.py:141，AUTO_DECOMPOSE 自动分解 vs PIPELINE 预定义管线，`set_mode` 在 workforce.py:836）、`WorkforceSnapshot`（快照 pending/completed/依赖/指派的完整状态，`save_snapshot` 节流落盘）。

方法面按功能分组：

- **构建面**：`add_single_agent_worker`（workforce.py:2956）、`add_role_playing_worker`（workforce.py:3019）、`add_workforce`（workforce.py:3097）；管线族以 `pipeline_add`（workforce.py:889）为入口，配 add_parallel_pipeline_tasks/pipeline_fork/pipeline_join/pipeline_build 构成 DAG。
- **任务面**：`add_task`/`add_main_task`/`add_subtask` 维护队列；`_decompose_task`（workforce.py:1474）用协调 LLM 拆子任务；`_analyze_task`（workforce.py:1570）与 `_apply_recovery_strategy`（workforce.py:1753）构成失败分析与恢复。
- **调度面**：`_call_coordinator_for_assignment`（workforce.py:3693）让 LLM 给任务挑 worker，配 `_find_assignee` 兜底；`_create_worker_node_for_task`（workforce.py:4111）可在无合适现成节点时按角色描述动态创建新 agent。
- **循环面**：`_listen_to_channel`（workforce.py:5207）是主事件循环——处理暂停/停止/跳过请求、触发主任务分解（`_needs_decomposition` 标记）、节流快照、经 `_get_returned_task` 收割完成结果；`start`/`stop` 与 pause/resume/stop_gracefully/stop_immediately/skip_gracefully 组成完整生命周期控制。
- **同步门面**：`process_task`（workforce.py:2747）检测到已运行的事件循环时，开新线程跑独立 loop 执行 `process_task_async`（workforce.py:2594）——同步调用方在异步宿主（如 notebook）里也能用。

底层通信：`TaskChannel`（task_channel.py:85）是异步任务总线，Packet/PacketStatus 封装传输；events.py 以 13 个事件类构成封闭事件协议（WorkforceEventBase 起，覆盖 WorkerCreated/TaskAssigned/TaskCompleted/TaskFailed 等），供回调与日志树消费。

## 3. 外部连接

- Task（camel/tasks/task.py）是流通货币：content/id/state/dependencies/subtasks 的 Pydantic 模型。
- Worker 抽象在 `Worker(BaseNode, ABC)`（worker.py），两个实现：SingleAgentWorker（single_agent_worker.py，包一个 ChatAgent）与 RolePlayingWorker（role_playing_worker.py，包一对 RolePlaying）。
- 节点基建在 BaseNode（camel/societies/workforce/base.py）——注意 `__init__` 与 `reset()` 各自 new 一个占位 TaskChannel()（camel/societies/workforce/base.py:35），真实通道由 Workforce 统一 `set_channel` 下发覆盖。
- ChatAgent 深度耦合：暂停事件注入 agent（`_attach_pause_event_to_agent`）、共享上下文工具（`_get_or_create_shared_context_utility`）、工作流记忆（`save_workflow_memories`）。
- 对外导出：`to_mcp`（workforce.py 尾部）可把整个 workforce 变成 MCP 服务，与 ChatAgent.to_mcp 同款机制。

## 4. 数据流

主线：`add_task` 入 pending deque（主任务可带 `_needs_decomposition` 标记）→ `_post_ready_tasks` 检查依赖、经协调者 LLM 指派 → `_post_task` 把 Task 写入 TaskChannel（指定 assignee）→ worker 的 `_listen_to_channel` 经 `get_assigned_task_by_assignee` 领任务 → 执行后 `return_task` 回总线（成功 state=DONE / 失败 state=FAILED）→ Workforce 主循环 `_get_returned_task` 收割 → 成功走 `_handle_completed_task`（结果回填父任务、依赖计数递减）；失败走 `_handle_failed_task`（workforce.py:4567）——failure_count 递增、`_analyze_task` 诊断、`_apply_recovery_strategy` 选择重试/分解/换人，多次失败后 `_mark_task_permanently_failed`。PIPELINE 模式下则按 DAG 拓扑投递，`_all_pipeline_tasks_successful` 判定汇合。

## 5. 设计决策

1. **编排者即节点**（workforce.py:175 继承 BaseNode）：统一抽象让嵌套 workforce、快照、通道下发复用同一套协议，代价是"节点持有占位通道"的迷惑性（见坑②）。
2. **LLM 协调分派 + 确定性兜底**：指派先问协调 LLM，失败/无效再走 fallback 与动态建节点（workforce.py:3693/4111）——灵活性与可靠性分层。
3. **同步门面的双 loop 策略**（workforce.py:2747）：进程内已有 loop 时另起线程跑新 loop，避免 asyncio.run 二次嵌套崩溃，这是把异步内核卖给同步用户的标准姿势。
4. **快照+暂停+跳过构成人机协同面**：process_task 同步外壳下还有 `_process_task_with_snapshot` 与 `_process_task_with_intervention` 两条增强路径，配合 save_snapshot/restore_from_snapshot 支持断点续跑与任务改写。
5. **失败是一等公民**：专门的分析-恢复-永久失败三段式（workforce.py:1570/1753），比多数框架"失败即抛异常"更贴近生产。

## 6. 新人提示

- **坑① Task 默认 state=FAILED**：task.py:257 写死 `TaskState.FAILED` 且下一行自带 TODO "Add logic for OPEN in workforce.py"——新建 Task 若不显式 set_state 或被 workforce 流程覆盖，读到的状态是 FAILED，任何依赖 state 做判断的外层代码都会误判。
- **坑② BaseNode 的占位通道**：camel/societies/workforce/base.py:35 与 reset() 内各 new 一个 TaskChannel()，单看 BaseNode 会以为每个节点有独立总线；真实通道是 Workforce.set_channel 统一下发的同一个实例，未启动前对占位通道 post 任务等于扔进黑洞。
- **日志风格分裂**：worker.py 与 role_playing.py 用裸 logging.getLogger（后者还压到 WARNING），workforce.py 用 camel.logger.get_logger——排查时同名 logger 行为不一致属已知现状（图谱勘误钉版）。
- **嵌套 Workforce 的通道共享**：add_workforce 后子 workforce 收到的是外层通道，快照/恢复语义跨层传递时先读 `_graceful_shutdown` 理清失败传播。
- **协调者指派是 LLM 调用**：`_call_coordinator_for_assignment` 失败会走重试与 fallback，但意味着任务投递延迟不可预测，对延迟敏感的管线优先显式指定 assignee。
- **先读事件协议再读循环**：events.py 的 13 个事件类是理解 workforce 行为的最短路径，主循环里每个分支基本都对应一种事件。
