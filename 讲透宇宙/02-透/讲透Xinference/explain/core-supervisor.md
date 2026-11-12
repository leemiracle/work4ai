# core/supervisor.py — SupervisorActor 集群中枢精讲

> 仓库 `~/ai/inference`（包 `xinference/`），文件 7120 行。

## 一、角色定位

11 层架构中属 **layer:core 核心调度层**（tour 第 4 步）。主体是 6900+ 行的 `SupervisorActor(xo.StatelessActor)`（L223），`default_uid()` 返回 `"supervisor"`（L321）——集群寻址锚点：REST API 进程、本地模式、分布式 worker 一律 `xo.actor_ref(address, uid="supervisor")` 找到它。模型注册表、worker 表、副本路由、缓存下载、autostart、token router 管理面全在此，是控制面唯一大脑。

## 二、内部结构

- **注册表**：`register_model`（L2160）/`unregister_model`（L2274）。核心结构是 `__post_create__` 构建的 `_custom_register_type_to_cls`（L971-1008）：六种模型类型→`(spec_cls, register_fn, unregister_fn, generate_fn)` 四元组，复用 `model/` 各家族注册函数。
- **生命周期**：`launch_builtin_model`（L2839）、`_launch_builtin_sharded_model`（L3441，n_worker>1）、`terminate_model`（L4399）、`add_model_replica`（L4569）。
- **路由查询**：`get_model`（L5077）、`list_models`（L5161，带 debounce 缓存）。
- **worker 管理**：`add_worker`（L5406）、`report_worker_status`（L5514）、`_check_dead_nodes`（L4237）。
- **其余**：缓存下载（L2678）、autostart（L1042 起）、token router/tokenizer asset（L5781-7071 约 1300 行，后期膨胀主因）。

关键状态在 `__init__`（L224-319）：`_worker_address_to_worker`（注册表）、`_worker_status`（心跳+资源）、`_replica_model_uid_to_worker`（副本路由）、`_model_uid_to_replica_info`（含 `itertools.cycle` 轮询调度器，L334）、`_workers_launching`（L262，launch 期间豁免反向探活）。

## 三、外部连接

图谱 in-edges：`api/restful_api.py`、`deploy/local.py`、`deploy/supervisor.py` import 本文件，`RESTfulAPI` 持 supervisor ref 转发全部 REST 端点。`__post_create__`（L869-926）在同地址 `xo.create_actor` 出四个子 actor——`StatusGuardActor`/`CacheTrackerActor`/`ProgressTrackerActor`/`EventCollectorActor`；重活全下发 `WorkerActor`。同级依赖 `IdleFirstLaunchStrategy`（按 GPU 空闲率选 worker）。

## 四、数据流

**一次 launch_model 的 actor 交互**（POST `/v1/models`→restful_api.py L1151→`launch_builtin_model`）：

1. 校验（L2839）：`replica_config` 与 n_worker/worker_ip/gpu_idx 互斥（L2885）；n_worker>1 转 sharded 分支；local 部署忽略二者（L2880/L2935）；无 uid 则 `_gen_model_uid`（L2959）。
2. 写 CREATING（L3414+L3426）；`wait_ready=False` 时 `asyncio.create_task(_launch_model())` 挂入 `ASYNC_LAUNCH_TASKS`（L3431）。
3. `_launch_model`（L3151）：gather 并发拉 `get_model_count`（L3179）→三种放置：replica_config 钉死/`IdleFirstLaunchStrategy`（L3157）/load-first 排序（L3265）→gather 并发 `_launch_one_model`（L3340）。
4. `_launch_one_model`（L3020）：置 CREATING→**`worker_ref.launch_builtin_model(...)`**（L3104 跨 actor RPC）→`wait_for_load`（L3127，加载完才进路由表）→写路由（L3128）→READY。任一副本失败，外层统一 `terminate_model(suppress_exception=True)` 回滚（L3391）。
5. Worker 侧（core/worker.py L4129）：`locals()` 快照供自动恢复→`_spawn_subpool` 独立子进程池→`xo.create_actor(ModelActor, address=subpool_address, uid=model_uid)`（worker.py L4538）→`model_ref.load()`。推理时 `get_model`（L5077）轮询选副本；未就绪抛 `ModelNotReadyError`(503) 而非 404（L5093）。

**worker 生命周期**：`WorkerActor.__post_create__`（worker.py L1314）→`get_supervisor_ref(add_worker=True)`（L1422）→`add_worker`（L5406）：`_rebuild_worker_replica_state` 重建副本映射（supervisor 重启自愈）。此后周期 `report_worker_status` 刷心跳；`_check_dead_nodes`（L4237）在独立线程循环：心跳超时扣 `failure_remaining_count`，归零走 `_handle_dead_worker`；另有反向 `worker_ref.ping()`（L4302）探测 supervisor→worker 通道，`_workers_launching` 中的 worker 豁免（L4306，长下载饿死事件循环）。

## 五、设计决策

- **为什么 actor 模型**：模型表/worker 表/路由表是单写者共享状态，xoscar 单线程 actor 语义天然免锁（跨 await 的 scale 操作才补 `_get_model_replica_lock` L348）；按地址寻址使 `worker_ref` 在本进程还是远机透明——**单机与分布式共用同一代码路径**，`is_local_deployment()`（L5335）只影响少数校验分支。
- **一致性优先**：`register_model` 同步 worker 失败即全量回滚（L2239-2245）。
- **自愈三件套**：`WorkerNotRegisteredError`（L194）逼 worker 重走 add_worker；`add_worker` 重注册时 diff 出静默消失副本按意外终止处理（L5434）；`receive_heartbeat` 拒绝为未注册 worker 伪造状态（L5566 注释：否则死节点检测看到假活）。
- **代价**：7120 行上帝类，六类职责混居，token router 占尾段 1300 行，演进时最需拆分。

## 六、新人提示

- 切入点：`__init__`（L224-319）→`__post_create__`（L869）→`launch_builtin_model` 内嵌的 `_launch_one_model`/`_launch_model`。
- 易错点：①三层 uid：`model_uid`→replica uid（`-1` 后缀）→ModelActor uid，自定义 uid 不能以 `-rep<N>` 结尾（L3399）；②`get_model` 消耗轮询调度器，`describe_model` 用 `active_replica_ids[0]` 避免消耗（L5141 注释）；③死节点检测循环内不 await（L4267 注释）；④supervisor 内存态不持久，重启靠 worker 重报重建。
- 相关测试：`xinference/conftest.py`；冒烟：`xinference-local` 起集群后 `GET /v1/cluster/info`。
