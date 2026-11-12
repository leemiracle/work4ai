# 04 · checkpointing 双体系与 FT launcher 容错运行时

## 角色定位

本篇覆盖 NVRx 两大运行时支柱：**checkpointing**（async_ckpt + local，重启后从哪恢复）与 **fault_tolerance/launcher.py**（4008 行，用户主入口——挂了怎么检测、要不要重启、何时触发归因）。两者合成"最小损失自愈循环"：launcher 抓故障 → 归因判 STOP → async/local 检查点恢复现场。文档锚：docs/source/checkpointing/、docs/source/fault_tolerance/usage_guide.rst。

## 内部结构

**FT 侧**：

- `launcher.py:351` class LocalElasticAgent(SimpleElasticAgent)——继承链来自 `torch.distributed.elastic.agent.server.api`（launcher.py:50-52 import），非 torchrun 同名类。
- 重启决策（launcher.py:694 注释起）：attribution STOP > 进展 > 重启预算；launcher.py:774-784 注释明确 "An attribution STOP preempts any restart decision" 且只有持 attribution client 的节点能锁存判定；终 cycle 归因触发在 launcher.py:2004-2005（`_request_terminal_attribution()`，定义 :1117）。
- 心跳：`rank_monitor_server.py:125`（RankMonitorServer；`_handle_unhealthy_node` :260、`_handle_timeout` :266、`_handle_init_msg` :379）+ `rank_monitor_state_machine.py:25`（RankMonitorState）/`:35`（RankMonitorStateMachine，非法迁移抛 :19 InvalidStateTransitionException）。
- 集合通信健康：`ft_rendezvous_barrier.py`（RendezvousTimeout :125、RendezvousSettings :200、GroupRankStatus :293）+ segment_health_check.py + c10d_monkey_patch.py + ipc_connector.py。
- timeout_dump 家族（989 行八件）：collector.py（256）调度、capture.py（288）执行、cuda_gdb.py:23（CudaGdb）、pyspy.py:37、gdb.py:54、ptrace.py:24、config.py（167）。
- 控制面：control_plane.py:69（ControlServices）、:129（_create_tcpStore）；配置 fault_tolerance/config.py（FaultToleranceConfig，心跳/段超时/信号）；数据模型 data.py（RankInfo、Authkey/Init/Heartbeat/Section IPC 消息）。

**ckpt 侧**：

- async_ckpt/：core.py（1117 行）——AsyncRequest/AsyncCaller（线程/进程/持久 worker 三形态）/AsyncCallsQueue 与 finalize 队列；filesystem_async.py:180（FileSystemWriterAsync 继承 PyTorch FileSystemWriter）、:86（ConsistentDataIdentifier）；state_dict_saver.py、torch_ckpt.py、cached_metadata_filesystem_reader.py。
- local/：base_state_dict.py + basic_state_dict.py（状态字典骨架）、ckpt_managers/（base_manager.py、local_manager.py）、replication/（group_utils.py 进程组、strategies.py 复制策略）。

## 外部连接

launcher 的归因钩子 import 自 attribution_manager（launcher.py:81-87）；cycle 元数据由 cycle_info_writer.py 写出、每 cycle 日志独立成目录（per_cycle_logs.py）；shared_utils 的 grpc_log_server.py（904 行）/grpc_log_leaf_server.py（624 行）按 log_aggregation.proto（54 行）聚合多节点日志，nvhcd.proto（33 行）定义心跳服务、nvrx_interface.proto（58 行）定义 cycle 信息；examples/fault_tolerance/ 提供 megatron_gpt_worker.py、train_ddp_heartbeats_api.py、train_ddp_sections_api.py、deployment/slurm 与 deployment/watch（nvrx_watch 看门狗）全链示例。

## 数据流

训练侧用户代码 begin_section/end_section → 心跳经 IPC（data.py 消息）到 RankMonitorServer（rank_monitor_server.py:125）→ 状态机（rank_monitor_state_machine.py:35）判定超时/不健康 → LocalElasticAgent（launcher.py:351）接管：先问归因（STOP 则终止并触发 launcher.py:2004 终局归因），否则重启 workers → 重启后从 async_ckpt 落盘的检查点恢复：AsyncCallsQueue 把保存任务交给 AsyncCaller worker，FileSystemWriterAsync（filesystem_async.py:180）流式写、ConsistentDataIdentifier（:86）保证一致性标识 → 下一 cycle 继续。超时现场同时被 timeout_dump 抓取（collector.py → cuda_gdb.py:23/pyspy.py:37）供归因消费。

## 设计决策

- **STOP 一票否决 + 单点锁存**：归因结论凌驾一切重启逻辑（launcher.py:774），且只有 attribution client 属主能置位——多节点竞态被结构性排除。
- **段模型而非全局看门狗**：section 级超时让 hang 检测贴近用户语义（collective、dataloader 各配各的超时）。
- **AsyncCaller 三形态**：core.py 让"线程/进程/持久 worker"可插拔——GPU 上序列化昂贵，持久 worker 摊平启动成本。
- **local 与 async 并存**：local 高频小快照 + async 低频大快照，RTO 与 IO 成本分层。
- **timeout_dump 独立成族**：抓现场（cuda-gdb/pyspy）与重启逻辑解耦，dump 失败不影响恢复路径。

## 新人提示

从 docs/source/fault_tolerance/examples 的 train_ddp_sections.rst 跑通最小例再读码；读 launcher.py 先跳过 4008 行里的 argparse 段直奔 :694 决策注释与 :351 类定义；测状态机用 tests/fault_tolerance/unit/test_rank_monitor.py；改 proto 三件后必须 `pip install .` 重生成 stub（CLAUDE.md Protobuf 节）；local/replication 的 strategies.py 决定复制拓扑，动它之前先跑 checkpointing 单测。
