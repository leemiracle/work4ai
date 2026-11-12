# 服务端运行时 FedServer

## 一、角色定位

服务端与客户端镜像，也拆三层：SP（Server Parent 常驻父进程）、SJ（Server Job 每作业一个子进程）、SJ 内的 ServerRunner。`BaseServer`/`FederatedServer` 在 SP 承担部署与客户端注册握手（`nvflare/private/fed/server/fed_server.py:205`、`fed_server.py:357`）；`ServerEngine` 既在 SP 启动 SJ 子进程、也在 SJ 做任务分发引擎（`nvflare/private/fed/server/server_engine.py:91`）；`ServerRunner` 在 SJ 顺序执行 workflow 并响应拉任务（`nvflare/private/fed/server/server_runner.py:80`）；`JobRunner` 是 SP 的作业调度主循环（`nvflare/private/fed/server/job_runner.py:110`）。任务书说 ServerEngine 有 "main_loop 驱动"——**全仓 grep 不到 main_loop**：真正的驱动是 SP 侧 `JobRunner.run` 的 1 秒轮询（`job_runner.py:683`）与 SJ 侧 `ServerRunner._execute_run` 的 workflow 循环（`server_runner.py:130`）。

## 二、内部结构

**FederatedServer**：`BaseServer.deploy` 解析 target、组装 TLS credentials、以 `FQCN.ROOT_SERVER` 创建 Cell；子类 deploy 再切 HotState、注册回调与安全过滤器（`fed_server.py:1218`）。回调集在 `_register_cellnet_cbs`：SERVER_MAIN 通道上的 Challenge/Register/Quit/HeartBeat/ReportJobFailure（`fed_server.py:438`）。**注册握手**两步：`client_challenge` 建注册会话防伪造，对客户端 nonce 用站点证书私钥签名并回发服务器证书（`fed_server.py:731`）；`register_client` fire CLIENT_REGISTER_RECEIVED 让事件链可否决，再交 `ClientManager.authenticate` 发 token（`fed_server.py:794`），回复附 `sign_auth_token` 签名与 SSID（`fed_server.py:552`）。secure 模式下 `_validate_auth_headers` 作为全通道入站过滤器逐消息验签（`fed_server.py:522`），防客户端伪造"来自服务器"的消息。`process_job_failure` 是 CP 失败上报落点：只验 token（注释明言不带 PROJECT_NAME header），EXCEPTION 类直接 fail_run（`fed_server.py:909`）。

**ServerEngine**：核心 `_start_runner_process`（`server_engine.py:236`）——校验部署元数据、选 launcher、组装 job_args，SJ 的 EXE_MODULE 固定 `nvflare.private.fed.app.server.runner_process`（`server_engine.py:290`），认证上直接拿 job_id 当 token 并签名（`server_engine.py:284`），launch 后登记 run_processes 并起收尸线程（`server_engine.py:315`）。

**ServerRunner**：`run` 先 fire START_RUN、构建参与客户端森林（`server_runner.py:185`），再进 `_execute_run` 逐 workflow：initialize→control_flow（阻塞至结束）→finalize，wf_lock 保证 workflow 切换与消息处理互斥。`process_task_request` 是拉模型的服务端一半：status 为 init 回 TRY_AGAIN、为 done 回 END_RUN（`server_runner.py:285`）；`_processing_tasks` 表防同客户端重复领任务（`server_runner.py:309`）；任务取自 `current_wf.controller.communicator.process_task_request`（`server_runner.py:392`），经 outbound filters 附审计事件发出。`process_submission` 在 wf_lock 内准入后把结果交回当前 workflow（`server_runner.py:445`）。

**JobRunner**：SP 调度循环——取 `get_jobs_to_schedule` 的已批准作业交 scheduler 决策（`job_runner.py:706`），`_deploy_job` 把 app 推到各站点（`job_runner.py:167`），状态机 SUBMITTED→DISPATCHED→RUNNING（`job_runner.py:719`），异常则 FAILED_TO_RUN 并 fire JOB_ABORTED；`_job_complete_process` 后台线程收尾归档（`job_runner.py:488`）。

**配套件**：`ClientManager` 持 token→Client 表做登录/心跳，默认 min=2/max=10 个客户端（`client_manager.py:40`）；`RunManager` 是 SJ 内 EngineSpec 门面，按有无 job_id 区分 SJ/SP 上下文（`run_manager.py:33`）；`ServerState`/`HotState` 是极简状态机——基类所有动作返回 Not In Service，只有 HotState 全绿（`server_state.py:55`）；`job_meta_validator` 校验 job zip 的 meta/deploy_map/min_clients；`job_cmds` 是 ADMIN 命令模块（`job_cmds.py:149`）；GET_TASK 的 aux 入口 `GetTaskCommand` 调用 `process_task_request`（`server_commands.py:175`）。**SimulatorDeployer** 用临时端口 + tcp scheme 在单进程里造 SimulatorServer 与各模拟客户端 Cell（`simulator_deployer.py:35`），客户端引擎换成 SimulatorParentClientEngine——同一套协议，只是进程拓扑坍缩。

## 三、外部连接

与客户端：注册握手、心跳超时清理与 aux 任务通道。与 ADMIN：JobCommandModule 提供作业命令，作业先落 job store 再被调度。与 SJ：SP 传 PARENT_URL，SJ 用 job_id token 回连认证。与 snapshot/simulator：SJ 重启经 restore_snapshot 恢复；SimulatorServer 复用 FederatedServer 全部回调路径。

## 四、数据流：注册 + 一个作业的完整生命周期

1. 客户端 Cell 连上服务器发 Challenge：建 ClientRegSession、签名回 nonce+证书（`fed_server.py:731`）。
2. 客户端发 Register：事件链可拦截 → authenticate 发 token → 回 token+签名+SSID。此后所有请求带 token+签名，入站过滤器逐条验签。
3. ADMIN submit_job：job zip 经校验入 job store，状态 SUBMITTED。
4. SP 的 JobRunner 取到该作业，scheduler 判定后 `_deploy_job` 推 app 到各站点，状态 DISPATCHED（`job_runner.py:719`）。
5. `_start_run` → `_start_runner_process` 启动 SJ 子进程（`server_engine.py:236`）；SJ 内 RunManager/ServerRunner 就绪，status=started。
6. 各站点 CJ 回连注册到 SJ，SYNC_RUNNER 握手后进入拉任务循环；GET_TASK aux 请求经 GetTaskCommand 到 `process_task_request`（`server_commands.py:175`），workflow 的 controller 供任务。
7. workflow 结束：ServerRunner 在 finally 广播 END_RUN aux；SJ 退出上报 UPDATE_RUN_STATUS；SP 侧收尸线程判定成败并归档（`job_runner.py:488`）。

## 五、设计决策

**SP/SJ 镜像隔离**：服务器作业与客户端作业同级崩溃隔离；代价是调试链路跨三进程。**token 即身份**：客户端 token 由服务器签发、SJ 直接拿 job_id 当 token（`server_engine.py:284`）——授权完全押在 cell 边界验签上。**热/冷状态机**：冷态下一切动作返回 Not In Service，SJ 重启窗口的请求被干净拒绝。**拉模型的服务端代价**：每次 GET_TASK 都要拿 wf_lock 问当前 workflow，`_processing_tasks` 防重表（`server_runner.py:309`）是修补"同客户端并发拉取重复领任务"竞态的补丁——补丁式复杂度是拉模型的税。批判地看：fed_server.py 1255 行是 god class（部署/握手/鉴权/上报混居）；ServerEngine 同名承担 SP/SJ 双职责；`_listen_command` 对"心跳但作业已不在"直接 abort 是隐式状态迁移，优先排查它。

## 六、新人提示

**上手顺序**：先 `server_state.py`（69 行）→ `fed_server.py` 只读 438-964 回调区 → `job_runner.py:683` 调度循环 → `server_runner.py` 的 `_execute_run`。**调试切入点**：作业卡 SUBMITTED→看 JobRunner 日志有无 approved_jobs、scheduler 是否拒绝；客户端注册失败→查 challenge 是否报 "server is not in secure mode"（`fed_server.py:742`）；任务不下发→确认 ServerRunner status 是 started 而非 init（`server_runner.py:285`）。**常见坑**：① min_num_clients 默认 2（`client_manager.py:40`），单客户端实验须改配置；② site_config 超 64KB 被静默丢弃只留 warning；③ secure 模式验签覆盖所有通道，绕过 cell 的直连会被拒（`fed_server.py:522`）；④ 模拟器 scheme 是 tcp 非 grpc（`simulator_deployer.py:116`），报协议错先查。
