# 任务调度与工作流引擎

## 一、角色定位

本组文件构成 NVFlare 工作流引擎的三层：`ControllerSpec` 定义调度原语契约（`nvflare/apis/controller_spec.py:255`）；`Task`/`ClientTask` 是被调度的实体（`controller_spec.py:72`、`controller_spec.py:173`）；`WFCommServer` 是原语的服务端实现与任务队列（`nvflare/apis/impl/wf_comm_server.py:91`）；`ServerRunner.process_task_request` 把客户端拉取接到队列上（`nvflare/private/fed/server/server_runner.py:263`）。开箱工作流 SAG/Cyclic 与聚合器 family 在其上组装 FedAvg/CWT。两个甄别：①任务书所说 `workflows/base.py` **不存在**——SAG 直接继承 `Controller`，Cyclic 继承 `ModelController`；②`task_manager.py` 不是"任务表"而是**无状态策略对象**（约定 state 存 Task.props、键前缀 `__`，`nvflare/apis/impl/task_manager.py:31`），真任务表在 Task.client_tasks 与 WFCommServer._tasks。

## 二、内部结构

**ControllerSpec**（纯 ABC）定义三组原语及阻塞版：`broadcast`（一对多、min_responses 提前收兵，`controller_spec.py:319`/`:363`）、`send`（单目标、ANY/SEQUENTIAL，`controller_spec.py:411`）、`relay`（依次接力、dynamic_targets 收新客户端，`controller_spec.py:469`），外加 `cancel_task`（`controller_spec.py:517`）与 lifecycle 三方法。**Task** 携带四类回调钩子与运行态（targets、client_tasks、is_standing，`controller_spec.py:156`）；**ClientTask** 记录某客户端对某任务的进度（发送计数、结果时间戳）。**两套实现**：`Controller`（`nvflare/apis/impl/controller.py:25`）把原语委托给注入的 communicator——SAG 走这条；`TaskController`（`nvflare/apis/impl/task_controller.py:31`）自带直连实现——ccwf 客户端侧走这条（平行演化痕迹）。

**WFCommServer**：`process_task_request` 在 controller_lock 下扫 `_tasks` 队列（`wf_comm_server.py:190`）：已发送未收结果的客户端标记 resend 容错重发（`wf_comm_server.py:236`）；否则调 TaskManager 的 `check_task_send` 决定 SEND/BLOCK/NO_BLOCK（`wf_comm_server.py:248`；默认逻辑：做过不重发、命中目标列表或列表为空才发，`task_manager.py:44`）。锁定区间刻意只做决策、发送移出锁外，避免回调再入锁死锁。

**ScatterAndGather**（`nvflare/app_common/workflows/scatter_and_gather.py:36`）：start_controller 取 aggregator/persistor 并 load 初始模型；`control_flow` 的 round 循环（`scatter_and_gather.py:224`）每轮：learnable_to_shareable → 构造带 operator dict 的 Task → `broadcast_and_wait`（min_responses=min_clients，`scatter_and_gather.py:285`）→ `aggregate`（`scatter_and_gather.py:298`）→ shareable_to_learnable 回写 → 按 persist/snapshot 周期落盘。结果回调里逐份 `aggregator.accept`（`scatter_and_gather.py:447`）——accept 轮中即时、aggregate 轮末一次的两阶段设计。**Cyclic**（`nvflare/app_common/workflows/cyclic.py:21`）已迁移到 ModelController API：round 循环内 `sample_clients` 后逐客户端 `send_model_and_wait(targets=[client])`（`cyclic.py:71`）接力传模型——不再直接用 relay 原语。

**聚合器**：`InTimeAccumulateWeightedAggregator`（`nvflare/app_common/aggregators/intime_accumulate_model_aggregator.py:47`）accept 时经 WeightedAggregationHelper（`weighted_aggregation_helper.py:116`）边收边加权和、aggregate 出结果，expected_quantity 不足会等待；`DXOAggregator`（`nvflare/app_common/aggregators/dxo_aggregator.py:25`）面向任意 DXO、校验 data_kind 白名单；`accumulate_model_aggregator.py:22` 的 AccumulateWeightedAggregator 已是 `@deprecated` 别名。**ccwf**（cross-site validation）：`ServerSideController`（`nvflare/app_common/ccwf/server_ctl.py:58`）做进度跟踪与超时检测，`ClientSideController`（`client_ctl.py:45`）双继承 Executor+TaskController 在客户端本地编排 learn executor；`CyclicServerController`（`cyclic_server_ctl.py:20`）只声明 cyclic_order 即复用整套状态机。

## 三、外部连接

ServerRunner 是唯一入口：GET_TASK aux → `process_task_request`（`server_runner.py:263`）→ `current_wf.controller.communicator.process_task_request`（`server_runner.py:392`）；结果回流经 process_submission → result_received_cb。Controller 经 `set_communicator`（`controller.py:47`）绑定 communicator；聚合器由 job config 注入（aggregator_id 默认 "aggregator"）。事件系统（ROUND_STARTED/BEFORE_AGGREGATION 等）让 filter/widget 介入而不改 workflow。

## 四、数据流：一轮 FedAvg（pull 模型视角）

1. SAG 的 `control_flow` 构造 train Task 并 `broadcast_and_wait` → communicator 把 Task 放入 `_tasks` 成为 standing task，control_flow 线程阻塞等待。
2. 各客户端 CJ 主循环 `get_task_assignment` 发起 GET_TASK aux。
3. ServerRunner 校验 job_id 与重复领取（`server_runner.py:309`）后转交 communicator。
4. WFCommServer 扫队列：check_task_send 放行 → before_task_sent_cb（SAG 用它按客户端定制数据）→ 数据经 outbound filters 发回；客户端拿到的是"响应"而非推送。
5. 客户端执行 executor、submit_result 回传；process_submission 在 wf_lock 内交给 communicator，触发 result_received_cb → `aggregator.accept`。
6. 收满 min_responses（或超时）→ broadcast_and_wait 返回 → `aggregate` 产全局模型 → 下一轮；全部轮次后 control_flow 返回。

## 五、设计决策

**standing task**：任务站着等客户端来拉，服务器从不主动连接——只需单向连通（穿防火墙友好），代价是延迟受轮询间隔限制、服务器要维护重发/防重状态。**回调契约**：四 CB + TaskManager 钩子把控制流与数据加工分离，SAG 的 control_flow 因此只有百行。**两阶段聚合**（accept 即时 + aggregate 轮末）平衡内存峰值与等待。批判地看：①两套 controller 实现代码分叉，ccwf 被迫自建超时/状态上报；②`check_task_send` 的 BLOCK 态（不发且挡住后续）默认实现从不返回，认知负担大于收益；③Task.props 的 `__` 前缀约定靠文档而非类型系统保证，键冲突风险仍在；④SAG 一类兼管训练轮/persist/snapshot/内存清理，职责过载。

## 六、新人提示

**上手顺序**：`controller_spec.py` 只读 72-510（Task/ClientTask/原语签名）→ `task_manager.py`（96 行）→ `wf_comm_server.py` 的 `process_task_request` → SAG。**调试切入点**：任务不下发→在 `check_task_send` 打日志看 NO_BLOCK/BLOCK；轮次卡住→看 min_responses、`wait_time_after_min_received` 与 aggregator 的 expected_quantity 是否凑不齐；结果被丢→查 accept 返回与贡献日志（`scatter_and_gather.py:447`）。**常见坑**：①send 默认 SEQUENTIAL，要求 targets 为非空列表；targets 为 None 是"动态目标"语义而非列表省略；②relay 任务可能对同一客户端重发（resend 逻辑），executor 必须幂等；③aggregator 按配置注入，id 对不上时 SAG 直接 system_panic 而非降级；④Cyclic 每轮独立 `sample_clients`，参与者可能轮间不同，别假设稳定拓扑。
