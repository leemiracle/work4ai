# 05 Front 与 Worker 进程模型（tour S07）

## 一、角色定位

AgentServer 内部是 Front/Runtime 两层进程模型：Front（主进程）持有对 Gateway 的 WebSocket 端口与控制面；真正的 OpenJiuwen Agent Runtime 跑在**常驻 Worker 子进程**里，两者经本地 IPC（unix domain socket / Windows named pipe）通信。四个文件各司其职：`supervisor/runtime_supervisor.py`（1239 行）是 Front 侧的 Worker 监督者——docstring 一句话钉死边界（runtime_supervisor.py:3）："Manage Runtime Workers. **This process does not execute Agent turns**"；`supervisor/affinity.py`（33 行）是会话粘性路由表；`worker/dispatcher.py`（765 行）是 Worker 内把 IPC 帧转为 Runtime 调用的执行分发核心；`worker/gateway_bridge.py`（218 行）是顶替旧 WebSocket 位置的虚拟网关套接字。

这个模型的核心承诺：**Worker 常驻、Front 可换**。app_agentserver.py:183 的 "Detach only" 注释在 Worker 侧得到完整呼应（worker/service.py:101 日志 "supervisor disconnected; runtime stays resident"）——模型加载一次，Front 崩溃重启零重载成本。

## 二、内部结构

### runtime_supervisor.py：Front 侧监督者

常量区（runtime_supervisor.py:58-72）定下全部时间预算：心跳间隔 10s、心跳超时 30s、HELLO 超时 10s、watchdog 巡检 5s、转发队列 256/转发超时 10s。最关键的两条（runtime_supervisor.py:68-72 注释）：`_WORKER_STALL_WARN = 30.0`、`_WORKER_STALL_RESTART = 180.0`——**区分"传输活着但业务循环停摆"**的场景，warn 一次超过一个心跳窗，sustained 180 秒才换 Worker。

监督主循环 `_supervise`（runtime_supervisor.py:451）编排 `_bring_up`（runtime_supervisor.py:518，spawn Worker、等 HELLO/IPC 就绪）、`_pump`（runtime_supervisor.py:624，读写 IPC 流）、`_watchdog`（runtime_supervisor.py:1077）、`_watch_process`（runtime_supervisor.py:1164）。看门狗的防误杀设计值得细读：

- **自 loop 停摆免疫**（runtime_supervisor.py:1086-1100）：Front 自己的事件循环卡顿时，pending pong 可能就躺在已完成的 future 里。此时**不因自己的卡顿处决 Worker**——记录峰值 lag、推迟判定、下轮用新证据复查。
- **transport 超时三重确认**（runtime_supervisor.py:1101-1109）：pong 在本次唤醒早些时候被接受但 pump 还没消费，先 `await asyncio.sleep(0)` 让证据落地再判死。
- `_classify_worker_stall`（runtime_supervisor.py:1128-1162）：beat_age ≤ 30s 视健康；> 180s 关连接换代（runtime_supervisor.py:1138-1151）；其间每两个巡检周期告警一次（runtime_supervisor.py:1152-1161）。

故障路径：`recover_from_failed`（runtime_supervisor.py:249）与 `_schedule_restart`（runtime_supervisor.py:967）驱动换代重生；`_apply_readiness`（runtime_supervisor.py:935）把 Worker 的 IPC readiness 流翻译到 04 篇的 Readiness 状态机；`_handle`（runtime_supervisor.py:776）处理 Worker 回帧（REQUEST_DONE/DELIVERY_ACK/SNAPSHOT 等）；`dispatch_parsed_request`（runtime_supervisor.py:333）是 Front→Worker 的请求入口。

### affinity.py：粘性路由（33 行）

docstring（affinity.py:3-7）：**桌面 AgentServer 只跑 primary Worker，备用槽留给 phase 2 的 warm standby**。SessionAffinity.worker_for（affinity.py:23-27）用 `setdefault` 把 session 钉到 primary——目前一切会话都路由到同一个 Worker，这个类的存在是为多 Worker 预留的接口。forget/clear（affinity.py:29/affinity.py:32）做会话回收。

### worker/dispatcher.py：Worker 执行分发

`_MAX_QUEUED_REQUESTS = 32`（dispatcher.py:56）是就绪前排队上限。`handle`（dispatcher.py:151-232）按 IPC 帧类型分发，几个值得注意的分支：

- **KIND_HEARTBEAT 的 off-loop 兜底**（worker/dispatcher.py:164-168 注释）：named-pipe 快路径已在读线程上应答过 ping，这个分支只服务流式传输——两条路径都回 `heartbeat_reply(beat_age)`，pong 里带业务循环的停滞年龄（与 worker/service.py:145-158 的 fast path 呼应：心跳不中断，停滞不遮蔽）。
- KIND_SHUTDOWN 置 shutdown_requested 返回 False 关会话（worker/dispatcher.py:172-173）；KIND_GATEWAY_ATTACH/DETACH 管理 Gateway 附着（worker/dispatcher.py:174-180）。
- KIND_REQUEST（worker/dispatcher.py:190-214）：先 `_reconcile_execution_state` 对账执行状态（区分输出段与终态），再 `events.register` 登记 dispatch_id，未就绪时 CHAT_CANCEL 走排队取消（worker/dispatcher.py:208-211），读者必须保持可用以接收 delivery ACK。

`mark_ready`（worker/dispatcher.py:95-131）是启动优先级的巧妙设计：在放行排队请求**之前**，对 CHAT_SEND/RESUME/ANSWER 三类请求领取 `preparation.pause_background()` 令牌（worker/dispatcher.py:102-111）——让首批对话请求不被后台准备任务拖慢；请求完成经 `_release_startup_priority`（worker/dispatcher.py:133-139）归还。注释（worker/dispatcher.py:96-98）点明时序：在 set_available 可能挂起之前就要领优先级，等进了 Runtime dispatch 再暂停就太晚。

### worker/gateway_bridge.py：虚拟网关套接字

docstring（gateway_bridge.py:3）："Virtual Gateway socket. **Worker writes land on IPC, never on the Front port**"。WorkerGatewayBridge（worker/gateway_bridge.py:57，类 docstring："Object passed to Agent Runtime wherever it used to hold a WebSocket"）——Runtime 代码以为自己握着 WebSocket，实际 send 落到 KIND_WIRE IPC 帧。`send`（worker/gateway_bridge.py:79 起）的关键语义（worker/gateway_bridge.py:87-93 注释）：流式帧属于执行而非开始的那条连接；**单发（unary）非推送响应才算 critical**，critical 帧拿 wire_id + Future 走送达 ACK，`_DELIVERY_TIMEOUT = 15.0`（worker/gateway_bridge.py:28-30 注释：Front 给 Gateway 转发留 10s，再留余量给失败回执）。流式帧入 WorkerEventStore 事件日志支持重放（worker/gateway_bridge.py:63）。ContextVar 三元组 delivered/generation/dispatch_id（worker/gateway_bridge.py:25-27）界定请求上下文；publication_lock 按 scope 弱引用缓存（worker/gateway_bridge.py:71-77）只序化同 scope 的恢复帧与实时帧。

### worker/service.py：Worker 服务循环与三级超时

`serve_worker`（worker/service.py:42）的 accept 循环（worker/service.py:72-109）：每个 Front 连接一个 session，generation 递增（ConnHolder，gateway_bridge.py:33-51，"Rebind does not reload the Runtime"）；连接断开走 `_retire_session` 并继续等下一个 Front——**runtime stays resident**（worker/service.py:101）。code_identity（worker/service.py:64-71）在循环外算一次：这是本进程已加载代码的身份，升级磁盘代码后新 Front 必须拒绝旧 Worker。

**三级关闭超时**（worker/service.py:32-35）：`_RUNTIME_LOAD_SHUTDOWN_TIMEOUT = 10.0`（等 runtime 加载 drain）、`_DISPATCH_SHUTDOWN_TIMEOUT = 10.0`（等 dispatch drain）、`_RUNTIME_SHUTDOWN_TIMEOUT = 30.0`（等 runtime 优雅关闭），外加共享总 deadline `SHUTDOWN_TIMEOUT = 30.0`（worker/service.py:239 的 `remaining()` 取 stage 限额与总剩余的 min）。

**WorkerForceExit（os._exit 硬退路径）**：异常类（worker/service.py:38-39）语义是"dispatch 无视取消，Runtime 关闭不得执行"。四个触发点：runtime 加载超 deadline（worker/service.py:203）、dispatch 仍运行（worker/service.py:244-248，docstring worker/service.py:233-238 讲透理由——还在跑的 dispatch 持有 Runtime 引用，跳过优雅关闭强制退进程，绝不从它脚下抽走 Runtime）、runtime 关闭超时（worker/service.py:267）、runtime 关闭失败（worker/service.py:274，持久化/资源清理不完整）。捕获协议（worker/service.py:59-62、worker/service.py:97-99、worker/service.py:126-127、worker/service.py:135-136）：fatal 单独存变量，防止 finally 的优雅 `_close_worker` 被替换成 IPC teardown 的 CancelledError，最终 `raise fatal` 由 main 层记录主日志后 `os._exit` 硬退。

### worker_process.py：IPC 端点与 RWX 串台修复

`_runtime_instance_token`（worker_process.py:23-31）的注释是一份生产事故档案：**企业版 AgentServer Pods 共享一块 RWX PVC 存 workspace**，没有 Pod 本地 token 时所有 Pod 推导出相同的 `runtime-<scope>.sock` 路径——第二个 Pod 会重附着到第一个 Pod 的常驻 Worker，HELLO 超时、不绑 8766 端口、永远 1/2 Ready。修复：取 K8s 注入的 `HOSTNAME`（即 Pod 名）sha256 前 8 hex 做 socket 名后缀，`JIUWENSWARM_RUNTIME_INSTANCE` 可覆盖。`default_socket_path`（worker_process.py:33 起）还处理 unix 路径 100 字节限制（worker_process.py:45-49 回退 tempfile 目录并校验属主与 0700 权限）。

## 三、外部连接

- 上游：app_agentserver.py:53-78 的 `_start_supervisor` 构造 RuntimeSupervisor、attach 进 Front、`run_until_ipc_ready`（runtime_supervisor.py:229）。
- Front 侧 trio 协作：RuntimeSupervisor 实现 front/admission.py 的 RuntimeBackend 协议；EventForwarder/RequestRegistry 承接请求登记与事件转发（runtime_supervisor.py:16-17 导入）。
- Worker 侧：supervisor/worker_process.py 的 WorkerProcess 负责 spawn（`_bring_up` :518 消费）；worker/main.py 是子进程入口（:87 导入 serve_worker）。
- Readiness 桥：`_apply_readiness`（runtime_supervisor.py:935）把 IPC readiness 帧映射到 lifecycle.py 的 mark_* 家族，Front 的 admission 据此放行/排队。
- GatewayBridge 与 06 篇的 adapter：`bind_runtime` → `bind_gateway_transport(self._bridge, self._lock)`（dispatcher.py:86-93）——Runtime（interface_deep 的 JiuWenSwarm）拿到的"WebSocket"就是 bridge。

## 四、数据流

一次 chat 请求的完整路径：

1. Gateway → Front WS → admission 放行（AGENT_READY 前排队）→ `dispatch_parsed_request`（runtime_supervisor.py:333）编码为 KIND_REQUEST 帧。
2. `_pump`/`_forward_wire`（runtime_supervisor.py:624/:863）写 IPC；Worker dispatcher.handle（dispatcher.py:151）收到，`_reconcile_execution_state` 对账 → `events.register` → `_spawn(_run_request)`（:379）。
3. `_run_request` 调 Runtime；Runtime 的所有"WebSocket 写"经 gateway_bridge.send（gateway_bridge.py:79）：流式帧→事件日志+KIND_WIRE；critical 单发→wire_id+Future 等 Front 的 DELIVERY_ACK（15s 超时）。
4. Front `_handle`（runtime_supervisor.py:776）收 WIRE 帧转给 Gateway 连接，回 DELIVERY_ACK；REQUEST_DONE 到达后 `_finish_request`（runtime_supervisor.py:925）完成请求登记。
5. 健康面：Front 每 10s 发 HELLO/HEARTBEAT（runtime_supervisor.py:1066-1075），Worker 在读线程 off-loop 应答并携带 beat_age；watchdog（runtime_supervisor.py:1077）30s 无 pong 判 transport 死，业务 beat 停滞 30s 告警/180s 换代（runtime_supervisor.py:1128）。
6. 关闭面：KIND_SHUTDOWN → dispatcher.drain（10s）→ runtime load drain（10s）→ runtime 优雅关闭（30s），任一环节卡死 raise WorkerForceExit → main 记日志 → os._exit。

## 五、设计决策

1. **Front 薄、Worker 胖、IPC 单通道**：控制面响应性与模型加载成本解耦；代价是所有执行流量过 IPC（critical 帧需要 ACK 协议补偿可靠性，gateway_bridge.py:87-93）。
2. **心跳双信号（transport pong + business beat）**：传输健康与业务循环健康分开测量，pong 在读线程 off-loop 应答保证阻塞循环里心跳不断流、同时如实上报停滞年龄（worker/service.py:145-158）——这是"活着"与"在干活"的区分，比单一心跳诚实。
3. **看门狗的反误杀偏置**（runtime_supervisor.py:1086-1109）：自己的 loop 卡顿不处决 Worker、pong 迟到先让证据落地。监督者的第一美德是别制造事故。
4. **硬退优于半关闭**（worker/service.py:233-238）：dispatch 拒绝取消时宁可 os._exit 也不在运行中的执行脚下关闭 Runtime——数据完整性优先于优雅性。
5. **实例 token 解决共享卷串台**（worker_process.py:23-31）：分布式部署里"同路径 socket"是隐形单点，Pod 名后缀把碰撞概率压到零；这是从 1/2 Ready 事故反推出的修复。
6. **启动优先级令牌**（dispatcher.py:95-131）：首批对话请求显式暂停后台准备，"用户等着的第一句话"优先于完备性——用小机制买到体感收益。

## 六、新人提示

- 排查"请求没响应"先分清三段：Front 日志有没有收到（WS 层）→ supervisor 有没有 forward（IPC 层，看 `_forward_wire`/DELIVERY_ACK 日志）→ Worker 有没有执行（dispatcher `_run_request`）。三段日志前缀分别是 [AgentServer]/[Supervisor]/[Worker]。
- Worker 日志里 "runtime stays resident" 不是错误——是设计行为；但若 Front 频繁重连，要查的是 Front 为何退出而不是 Worker。
- 改任何 `_WORKER_STALL_*` 常量前想清楚语义：WARN 是"告警但不动作"、RESTART 是"换代即丢掉常驻 Runtime 的全部热状态"，180s 不是随便选的。
- K8s 部署见 1/2 Ready：先查 Pod 间是否共享 workspace 卷、socket 名是否带 instance token（worker_process.py:41 的 `runtime-{scope}-{instance}.sock`）；`JIUWENSWARM_RUNTIME_INSTANCE` 是手动覆盖口。
- dispatcher 的排队上限 32（dispatcher.py:56）只在就绪前生效；满了的行为是拒绝而非丢弃——压测启动期 429 时别把这个当瓶颈。
- gateway_bridge 的 critical 判定（单发非推送）是投递语义的分界线：把 streaming 帧误标 critical 会把吞吐拖进 ACK 往返；反之 unary 回执丢失会造成会话事务悬挂。
