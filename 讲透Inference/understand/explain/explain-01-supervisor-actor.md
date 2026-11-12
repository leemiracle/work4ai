# explain-01 · SupervisorActor——集群的大脑与路由表（xinference/core/supervisor.py）

## 角色定位

SupervisorActor（`xinference/core/supervisor.py:223`，继承 `xo.StatelessActor`）是 Xinference 分布式集群的**控制面单点**：全集群唯一（uid 固定为 `"supervisor"`，`core/supervisor.py:322`），掌管 worker 注册表、模型路由表、副本状态机与死亡检测，所有 REST API 的写操作最终都汇到它这里。注意与 `deploy/supervisor.py` 区分——后者只是 103 行的进程入口壳（`deploy/supervisor.py:47-49` 创建 actor，`:96-99` 拉起 REST 服务），真正的 7120 行业务实体在 `core/supervisor.py`，约 190 个方法覆盖模型注册/启动/终止/扩缩副本/缓存下载/token router 管理/健康检查九大领域。"StatelessActor" 的含义是 actor 可在故障后被 xoscar 重建，因此其权威状态大量依赖 `StatusGuardActor`、`DownloadTaskStore`（`core/supervisor.py:269`，SQLite 持久化）等外部存储做恢复。

## 内部结构

`__init__`（`core/supervisor.py:224-319`）建立五组核心内存态：① worker 注册表 `_worker_address_to_worker` 与健康表 `_worker_status`（`:226-227`）；② 模型路由表 `_replica_model_uid_to_worker`（单 worker 或 tuple 多 shard，`:231-237`）与副本元信息 `_model_uid_to_replica_info`（`:238`，`ReplicaInfo` 定义在 `:213-221`，内含 round-robin `scheduler` 迭代器）；③ 下载任务仓 `_download_task_store`（`:269`，构造时把上次进程崩溃遗留的 active 下载标记为 interrupted，`:270-275`）；④ launch 历史、token router 配置、tokenizer 资产三个 SQLite/内存仓（`:293-313`）；⑤ list_models 三级缓存与 single-flight 锁（`:248-256`）。`__post_create__`（`:869-1040`）是真正的"开机序列"：起独立线程跑 `_check_dead_nodes` 死亡检测（`:880-888`）；在同地址创建 StatusGuard/CacheTracker/ProgressTracker/EventCollector 四个子 actor（`:898-926`）；装配六类自定义模型注册表 `_custom_register_type_to_cls`（`:971-1008`）；注册 SIGTERM 处理器（`:1023-1031`）；最后预建 xavier 的 BlockTracker/CollectiveManager 映射（`:1033-1039`）并调度 autostart（`:1040`）。

## 外部连接

上游是 `api/restful_api.py` 的各路由处理器（拿 `supervisor_ref` 直接 RPC）；下游通过 `_replica_model_uid_to_worker` 里的 actor ref 与 `core/worker.py` 的 WorkerActor 通信（launch/terminate/get_model 全走 ref 方法调用）；对客户端则以 `get_model`（`:5077`）返回 `core/model.py` 的 ModelActor ref，让推理流量**绕过 supervisor 直连模型 actor**。横向协作：`StatusGuardActor` 记录实例/副本状态机，`CacheTrackerActor` 记录模型版本与缓存（`:894-916`），`ProgressTrackerActor` 承载下载进度，vllm/xavier 的 `VLLMBlockTracker`+`CollectiveManager`（`:1033-1039`）支撑 KV 块迁移。worker 侧则通过 `add_worker`/`report_worker_status`/`receive_heartbeat`（`:5406/:5514/:5560`）三个入口反向注册。

## 数据流

以最核心的 `launch_builtin_model`（`:2839`）为主线：参数规整（local 模式强制 n_worker=1，`:2880-2883`；replica_config 与分片/遗留参数互斥校验，`:2885-2897`）→ n_worker>1 转 `_launch_builtin_sharded_model`（`:2899-2925`）→ xavier 预备（vLLM 专属、replica>1 才有意义，`:2982-3011`，world_size=replica+1）→ 内层闭包 `_launch_one_model`（`:3020`）写 CREATING 状态（`:3051`）、RPC `worker_ref.launch_builtin_model`（`:3104`）、**等引擎 load 完成才登记路由**（`wait_for_load`，`:3127`）再置 READY（`:3131`）；`_launch_model`（`:3151`）负责选点：并行拉取各 worker 模型数与 GPU 分配快照（`:3179-3187`），默认按 (count, address) 排序的 load-first（`:3265-3267`），`XINFERENCE_LAUNCH_STRATEGY=idle-first` 时换 `IdleFirstLaunchStrategy`（`:3157-3160`），replica_config 则完全钉死（`:3240-3247`）；多副本 `asyncio.gather` 并行发射（`:3340`），任一失败即回滚 `terminate_model(suppress_exception=True)`（`:3391-3397`）。查询侧 `get_model`（`:5077`）用 `next(replica_info.scheduler)` 做副本轮询（`:5089-5091`）；worker 死亡由 `_check_dead_nodes`（`:4237`）双通道发现——心跳超时计数（`:4241-4252`）与反向 ping（supervisor→worker 探测反向信道，`:4293-4375`，正在拉模型的 worker 豁免以免长下载饿死事件循环误判，`:4311-4321`），确认死亡后 `_handle_dead_worker` 做副本级清理并触发 autostart 重拉（`:4280-4291`）。

## 设计决策

几个值得咀嚼的取舍：①**路由表登记晚于引擎就绪**（`:3125-3127` 注释明言），杜绝请求被路由到半加载模型；②`WorkerNotRegisteredError` 特意继承 `Exception` 而非 `RuntimeError`（`:194-203` 长注释），因为 worker 的 report 循环把某些 RuntimeError 当致命错误会 break——用异常类型本身编码"这是可自愈的"；③worker 重注册时做**副本对账**（`add_worker` `:5434-5457`）：worker 复用旧地址重启不会触发死亡检测，于是 diff 监督侧映射与 worker 上报集合，把"悄悄消失"的副本按意外终止处理；④list_models 引入 debounce 结果缓存+single-flight 扫描（`:5161-5206`），针对 UI 每秒刷新打爆 xoscar 传输层的场景，且用时间戳而非 dict 作缓存哨兵——**空模型列表也是合法缓存值**；⑤规模操作用 `WeakValueDictionary` 存每模型锁（`:241-245`），防 stateless actor 上锁对象无限累积。

## 新人提示

读这个文件建议按"launch → query → health"三段跳跃式读，别顺序硬啃 7120 行。容易踩的坑：model_uid 不允许以 `-rep<number>` 结尾（`:3399-3404` 保留给副本后缀）；`wait_ready=False` 的异步启动期间 `get_model` 会抛 `ModelNotReadyError`（503）而非 404（`:5094-5102`），客户端应重试；xavier 模式下 rank0 是纯协调者不占副本 GPU（`:3037-3043`）。调试时 `_handle_dead_worker`（`:584`）、`_record_unexpected_down_replicas`（`:471`）与 `_rebuild_worker_status_guard_state`（`:733`）是状态恢复的关键三角，出"幽灵模型/worker 数不对"问题先看这三处。
