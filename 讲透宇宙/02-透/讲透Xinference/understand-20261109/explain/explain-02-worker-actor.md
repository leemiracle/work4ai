# explain-02 · WorkerActor——单机执行者与进程编排（xinference/core/worker.py）

## 角色定位

WorkerActor（`xinference/core/worker.py:797`，`xo.StatelessActor`，6248 行约 130 方法）是**每台机器一个**的执行面 actor：接收 supervisor 的指令，在本机完成"下载 → 虚拟环境 → GPU 预留 → 子进程池孵化 → ModelActor 创建 → 权重加载"全链路，并把资源状态/心跳回传。与 `deploy/worker.py`（118 行入口壳，负责起 actor pool）分工类似 supervisor 的两层结构。它是唯一真正触碰宿主 OS 的组件——fork 子进程（sub-pool）、读 NVML/psutil、管 virtualenv、清孤儿 GPU 进程。

## 内部结构

`__init__`（`core/worker.py:798-912`）的内存态分三层：启动守卫 `_model_uid_launching_guard`（`:842`，防同 uid 并发启动）、活跃模型七张表 `_model_uid_to_model/_model_spec/_model_status/_addr/_launch_args/_pid/_subpool_pids`（`:854-871`）、GPU 归属表 `_gpu_to_model_uids` 与用户指定表（`:857-861`）。并发控制三件套：`_launch_semaphore`（`:850`，`XINFERENCE_MAX_CONCURRENT_LAUNCHES` 并发上限）、`_subpool_creation_lock`（`:910`，注释解释 xoscar `append_sub_pool` 无内部锁，并发 fork+GIL 会死锁）、`_download_artifact_cleanup_lock`（`:848`，序列化下载注册与仓库清理）。supervisor ref 缓存带代数号 `_supervisor_ref_generation`（`:814`）与显式注册标志 `_registered`（`:835`，注释明确 ref 非空不等于已注册——heartbeat 用 `add_worker=False` 会提前填缓存）。`__post_create__`（`:1314-1462`）：装配九类自定义模型注册表（`:1367-1416`，比 supervisor 多 video/world 两类）、清缓存目录（`:1418-1419`）、连 supervisor 并触发跨重启模型恢复 `_try_recover_models`（`:1428-1432`）、独立线程跑 `_periodical_report_status`（`:1434-1442`）、异步清上次 worker 暴死留下的 vLLM GPU 孤儿（`:1445-1452`，注释点出 vLLM EngineCore 无 `_check_ppid`，被 reparent 到 PID1 后仍占 VRAM）。

## 外部连接

上游 supervisor（`get_supervisor_ref` 缓存连接、`report_status`/`heartbeat` 回传）；下游通过 `_main_pool.recover_sub_pool = self.recover_sub_pool`（`:819`）把 xoscar 子池死亡回调接到自己身上——`recover_sub_pool`（`:914`）是自愈核心：子池进程挂掉时找到对应 model_uid，取持久化的 launch_args 重新 `launch_builtin_model`（即"模型级自动恢复"），恢复上限由 `_model_uid_to_recover_count` 控制（`:4643-4645`）。它还创建 `core/model.py` 的 ModelActor 并放进**独立子进程池**（`xo.create_actor(ModelActor, address=subpool_address, ...)`，`:4538-4552`）——这是"模型崩了不拖垮 worker"的隔离边界。xavier 场景额外提供 `launch_rank0_model`（`:6175`）与 `start_transfer_for_vllm`（`:6168`）两个专用通道。

## 数据流

`launch_builtin_model`（`:4129`）是一条精心排序的管线，顺序本身就是文档：①`launch_args = locals()` 快照（`:4159-4163`，注释强调必须放函数最前，否则自动恢复重放会缺参）→ ②audio/image/video/world 引擎名归一（`:4164-4201`）→ ③参数校验（gpu_idx 显式指定时忽略 n_gpu，`:4224-4232`；PEFT 禁用于 embedding/rerank，`:4247-4255`）→ ④登记 launching guard + 排队信号量（`:4274-4303`，满了记 `_launch_waiting` 日志）→ ⑤**先预留 GPU**（`_allocate_subpool_devices`，`:4376-4382`，注释说明并发启动能看到彼此的选择避免挤兑）→ ⑥分片模型(n_worker>1)提前孵子池拿地址（`:4406-4413`）→ ⑦下载权重 `_download_model_files`（`:4444-4460`，进度器分两阶段权重 0/0.8/1.0）→ ⑧装 virtualenv（`:4475-4517`，单 worker 模式**推迟子池孵化到 venv 装完**，`:4383-4397` 长注释解释：子进程 python 起在 venv 上，先孵化会把宿主库缓存进 sys.modules 造成版本混装）→ ⑨创建 ModelActor、必要时按 GPU 数追加 per-device rank 池（`:4538-4573`）→ ⑩`model_ref.load()` 并记录加载耗时指标（`:4582-4596`）→ ⑪登记七张表+持久化 launch_args（`:4613-4648`）→ ⑫StatusGuard 置 READY（`:4684-4695`）。失败路径同样完整：异常时释放设备、拆子池（`:4600-4612`），`wait_for_load` 失败走 `_clean_up_failed_launch`（`:4730-4738`/`:4707`，防陈旧注册表卡死同 uid 重启）。状态回传双频：`_periodical_report_status`（`:5575`）每次心跳+每 N 次全量 `report_status`（`:5452`），后者用 psutil 递归收集子进程 PID 做**确定性 GPU 显存归因**（`:5459-5503`，不读任何进程 environ）。

## 设计决策

三个鲜明的工程判断：①**launch_args 即恢复协议**——用 `locals()` 全量快照持久化，崩溃后 `recover_model`（`:6209`）原样重放；代价是要小心剥离非构造参数（`launch_ts`，`:6210-6223` 注释记录了 jina-reranker-v3 因多余 kwarg 崩溃的实战教训）；②**子进程隔离 + 双向死亡检测**：supervisor 反向 ping worker（supervisor 侧），worker 侧则靠 sub-pool monitor + `recover_sub_pool` 兜底进程级故障；`terminate_model` 里对 `xo.destroy_actor` 包 5 秒超时（`:5241-5249` 注释引用 xoscar PR#140：actor 调用超时后 CancelMessage 可能永远到不了已卡死的池）；③**排队可取消**：`cancel_launch_model`（`:4741`）三路取消（下载/venv 安装/子池），且等 launch 协程完全退场（guard 移除）才返回（`:4766-4780`），否则立刻重启会撞"<uid> is running"。

## 新人提示

读 launch 流程务必按上面 ①-⑫ 顺序对照源码注释，大量"为什么这么排"的答案都在注释里（如 venv 先于孵化、GPU 预留先于下载）。调试常见抓手：模型卡 loading 看 `get_model`（`:5427`）按 model_state 分类抛错——registering/loading 抛 `ModelNotReadyError`、error/stopping 抛 RuntimeError；GPU 显存账对不上先看 `_model_uid_to_subpool_pids` 归因表（`:4618-4630`）；worker 反复重连 supervisor 看 `_clear_supervisor_refs` 与 generation 机制（`:5526-5533`）。`terminate_model` 不允许终止 launching 中的模型（`:5161-5162`），必须先 cancel_launch。
