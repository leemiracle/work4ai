# 客户端运行时与 FLARE Client API

## 一、角色定位

NVFlare 2.x 把一个 FL 站点的客户端拆成三层进程角色：CP（Client Parent，常驻父进程）、CJ（Client Job，每作业一个子进程）、真正跑训练的 trainer。本组文件覆盖三层核心：`ClientEngine` 在 CP 里管理通信与 aux/stream 通道（`nvflare/private/fed/client/client_engine.py:58`）；`JobExecutor` 负责 CJ 子进程拉起与生命周期（`nvflare/private/fed/client/client_executor.py:180`）；`ClientRunner` 在 CJ 内装配 ClientApp 并驱动"拉任务-执行-交结果"主循环（`nvflare/private/fed/client/client_runner.py:125`）。`nvflare/client/api.py` 的 `flare.init/receive/send` 是用户代码与运行时的门面。这是 2.x 的重构：作业崩溃只影响 CJ，CP 常驻；trainer 可与 CJ 解耦，用户代码甚至不必由 NVFlare 启动（attach 模式）。

## 二、内部结构

**ClientEngine（CP 层）** 继承 `ClientEngineInternalSpec, StreamableEngine`，构造时即创建 JobExecutor。`initialize_comm` 在 cell 建立后注册 AUX 通道通配回调，`_handle_aux_message` 按 topic 派发给 AuxRunner（`client_engine.py:147`）；shutdown 靠 touch `shutdown.fl` 文件。

**JobExecutor（CP→CJ 层）** 是 `ClientExecutor` 抽象类的唯一活跃实现。`start_app` 是核心：deep copy args 防污染；逐 key 校验 START_JOB 元数据与部署时落盘版本一致（`client_executor.py:241`）；组装 job_args，`EXE_MODULE` 固定指向 `nvflare.private.fed.app.client.worker_process`（`client_executor.py:278`），CJ 启动后靠 `PARENT_URL` 回连 CP。launcher 选择走 `fed_utils.get_job_launcher`（`client_executor.py:253`；`fed_utils.py:628` 广播 BEFORE_JOB_LAUNCH 让事件处理器竞标、要求恰好一个）。注意：类里的 `_get_job_launcher`（`client_executor.py:337`）全仓无调用方——死代码，任务书点名的它已被 fed_utils 版本取代。子进程退出由 `_wait_child_process_finish` 守候（`client_executor.py:623`）：解读 return code、释放资源并 fire JOB_COMPLETED（`client_executor.py:693`）。

**ClientRunner（CJ 层）** 继承 TBI：`TaskRouter` 维护 task_name→executor 表并支持 `*` 通配（`client_runner.py:49`）；主循环 `_try_run`（`client_runner.py:520`）内联心跳线程，循环体 `fetch_and_run_one_task` 拉任务（`client_runner.py:556`），三种特殊返回：无任务、`END_RUN`、`TRY_AGAIN`。拿到真任务后 `_do_task` 是全框架最长的编排函数（`client_runner.py:259`）：校验 peer context 与 job_id → 路由 executor → task data filters → `executor.execute`（`client_runner.py:386`）→ task result filters（`client_runner.py:457`），每步失败都返回带语义的 ReturnCode 并落审计事件。

**ClientAppRunner** 是 CJ 进程入口装配线（`nvflare/private/fed/client/client_app_runner.py:39`）：解析 fed_client.json、初始化 PrivacyService、创建 ClientRunManager 与 ClientRunner，connect_to_server 后进入 `client_runner.run`（`client_app_runner.py:80`）。

**Client API 门面** `api.py` 用 `(rank, config_file)` 缓存 context，`init` 经 `resolve_process_rank` 解析 Torch 进程组 rank（`api.py:70`）；`receive`/`send` 只转发到 `local_ctx.api`，实现按 `ClientAPIType` 分派（`api_context.py:99`）：IN_PROCESS_API 从进程内 DataBus 取，CELL_API 构造 CellClientAPI。`decorator.py` 只剩 `train`/`evaluate` 两个已 `@deprecated` 装饰器（`decorator.py:38`）——**仓库不存在 `@flare.filter` 装饰器**，任务书此点与源码不符（filter 是 Executor 配置）。

## 三、外部连接

- **与服务器**：ClientRunner 的 parent_target 默认 `FQCN.ROOT_SERVER`（`client_runner.py:709`），任务拉取、TASK_CHECK、结果提交都指向它；层级场景改指上游 aggregator。
- **与 CP**：CJ 的 `notify_job_status` 用 `FQCN.get_parent` 找 CP 并带重试上报（`client_app_runner.py:193`）；executor 侧用 `FQCN.join` 拼出 CJ 的 FQCN。
- **三种 backend**：`ClientAPIExecutor` 的 `execution_mode` 合法值是 in_process/external_process/attach（`nvflare/app_common/executors/client_api_executor.py:46`）——**没有任务书所说的 "sub_process"**。它在 START_RUN 事件里创建 backend（`client_api_executor.py:331`），execute 纯转发。InProcessBackend 把 trainer 跑在 CJ 内一条线程、经 DataBus 交互（`in_process_backend.py:76`）；ExternalProcessBackend 与 AttachBackend 共享 CellBackendBase 会话协议（`cell_backend.py:80`）。attach 的校验在 `nvflare/client/cell/attach.py`：trainer FQCN 由 CP FQCN 加前缀拼出（`attach.py:45`），非 TLS 网络必须显式声明 `connection_security='clear'`。
- **IPCAgent（旧线）**：`nvflare/client/ipc/ipc_agent.py:35` 是上一代 sub_process 时代的通信 agent——自建 Cell、注册 get_task/heartbeat/bye/abort 回调（`ipc_agent.py:104`）。新三 backend 已不走它，但仍作为公开 API 导出，由 `IPCExchanger`（`ipc_exchanger.py:52`）兼容线消费。

## 四、数据流：一次 in_process 训练任务

1. 服务器 START_JOB → CP 的 `start_app` 组装 job_args，launcher 启动 worker_process 子进程。
2. CJ 进程内 `ClientAppRunner.start_run`：解析配置、connect_to_server、上报 STARTED。
3. `ClientRunner.init_run` 先与父 runner 做 SYNC_RUNNER 握手（`client_runner.py:752`），成功后 fire START_RUN——该事件触发 ClientAPIExecutor 创建 backend 并起 trainer 线程。
4. 主循环拉到 train 任务（`client_runner.py:556`）→ filters → execute → backend 把 FLModel 经 DataBus 交给 trainer；用户代码 `flare.receive()` 训练后 `flare.send()` 交回。
5. 结果经 result filters（`client_runner.py:457`）→ 发送前先 TASK_CHECK 确认服务器还在等（为对抗不稳定网络）。
6. 服务器回 END_RUN → `run_abort_signal` 触发（`client_runner.py:561`）→ `end_run_events_sequence`（`client_runner.py:812`）→ CJ 退出 → CP 侧守候线程释放资源并 fire JOB_COMPLETED。

## 五、设计决策

**拉模型**：客户端主动轮询，服务器无需维护推送连接、天然穿防火墙；代价是空轮询流量与延迟下界。**CJ 子进程隔离**：作业崩溃不杀 CP，恢复以作业粒度进行；代价是每作业都要走 worker_process 启动加握手，小作业开销显著。**backend 可插拔**：同一 `flare.*` API 覆盖"同进程线程 / 框架启动的子进程 / 外部自启进程"三种 trainer 归属，attach 模式允许 trainer 先于作业存在——同类框架（Flower/PySyft）均要求 trainer 生命周期由框架掌管。批判地看：`_do_task` 单函数 260 行、十多种错误出口，可读性差；死代码与 IPCAgent 双线并存，说明向新 Client API 的迁移尚未收尾。

## 六、新人提示

**上手顺序**：先读 `api.py`（238 行门面），再跟 `client_runner.py` 的 `_try_run`→`fetch_and_run_one_task`→`_do_task` 调用链，最后碰 CP 侧两文件。**调试切入点**：任务没到 trainer，先看 CJ 日志 "got task assignment"（`client_runner.py:573`）——有则是 executor/backend 问题，无则是通信或路由问题。**常见坑**：① `flare.init()` 必须先于一切 API 调用（`api.py:50` 的报错即为此设计）；② executor 任务名写错不报配置错，而是运行时 ReturnCode.TASK_UNKNOWN（`client_runner.py:308`）；③ attach_id 是路由名不是秘密，别当 token 用（`client_api_executor.py:166`）；④ ClientStatus.STOPPED 指 runner 返回而非 OS 进程退出（`client_executor.py:514` 注释）。
