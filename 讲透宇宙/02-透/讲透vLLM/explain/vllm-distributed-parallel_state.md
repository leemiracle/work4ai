# vllm/distributed/parallel_state.py — GroupCoordinator：全维度并行进程组的单一事实源

> 源码：`vllm/distributed/parallel_state.py`（2780 行）｜改编自 Megatron-LM parallel_state（:6）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

位于 **distributed（分布式执行层）**，是 vLLM 从 PyTorch 手里接管分布式环境的**进程组世界中枢**：把裸 rank 排布成有语义的组，再以 `GroupCoordinator`（vllm/distributed/parallel_state.py:427）统一暴露通信原语。docstring（:8-24）钉死工作流：`init_distributed_environment` → `initialize_model_parallel` → 业务代码 → `destroy_model_parallel` + `destroy_distributed_environment`。2026-09→10 的形态变化：组族从旧版 6 个扩到 **9 个全局单例**——新增 ETP（Engram 张量并行，:1599）、ENGRAM_DP（共享 Engram 嵌入表的 DP 组，:1608）、INNER_DP_WORLD（DP 内多节点 world，:1494）。它不 spawn 进程（那是 executor 的活），每个 GPU worker 进程各持一份本模块状态；模型层（fused_moe/mla_attention/mamba）与 EPLB、kv_transfer、elastic_ep 都以 `get_xx_group()` 断言访问器为唯一入口。

## ② 内部结构

`GroupCoordinator` 每组持双通道：`cpu_group`（gloo 控制面：对象广播/协调/barrier）+ `device_group`（nccl 等数据面）。rank 三兄弟看类注释表（vllm/distributed/parallel_state.py:440-446）：`rank` 全局、`local_rank` 节点内序号（决定用哪块 GPU）、`rank_in_group` 组内寻址号；`is_first_rank/next_rank/prev_rank` 属性族（:640-672）服务 PP 相邻 stage。集合通信 `all_reduce/all_gather/reduce_scatter`（:726/:754/:785）在 `use_custom_op_call`（:572，TPU 或平台声明 `use_custom_op_collectives()`）时走 `torch.ops.vllm.*`、以组名字符串寻址——torch.compile/Dynamo 兼容的关键；world_size==1 一律直通。MoE 通信门面 `dispatch/combine/dispatch_router_logits/combine_into_output`（:1436/:1458/:1416/:1479）整体委托 `device_communicator`（EP all-to-all 由平台通信器实现，:550）。`_groups` weakref 注册表（:160）支撑按名分发与批量 `_apply_to_device_comms`（:167）——`suspend/resume_device_comms`（:189）与 `checkpoint_prepare/restore_distributed_state`（:2455/:2462）两组生命周期钩子都靠它。

## ③ 外部连接

- **依赖**：`device_communicators/`（custom all-reduce 等平台通信器）、`shm_broadcast.MessageQueue`（共享内存对象广播，:562）、`utils.py`（StatelessProcessGroup/TCP store）、平台层（设备寻址 :530）、`torch.distributed._symmetric_memory`（symm-mem 补丁 op，:247/:420）。
- **被依赖**：`vllm/distributed/__init__.py` re-export 访问器给模型层与 `layers/linear.py`（TP all-reduce 的来源）；EPLB、elastic_ep、kv_transfer、`v1/worker` 均消费。
- **与 Ray 无关**：Ray 只是 executor backend 的一种；仅 `cleanup_dist_env_and_memory(shutdown_ray=True)`（:2551）顺手 `ray.shutdown()`。

## ④ 数据流（初始化 → 建组 → 运行期 PP 通道）

```
init_distributed_environment @:1839
  多节点/DP>1: rank 偏移 dp_rank*world_size @:1872
  world group TCPStore 端口经 coord_store 发布/领取 @:1884-1920
  split_group 路径: backend="cpu:gloo,cuda:nccl"+device_id
    急切绑定 @:1741；external_launcher 下校验父组 @:1778
  _WORLD @:2013；elastic EP 改走 StatelessGroupCoordinator
    @:1804（多节点 TP/PP 直接拒绝 :1994）

initialize_model_parallel @:2081
  布局序 ExternalDP×DP×PP×PCP×TP @:2151，5 维 rank 张量 @:2160
  每维: transpose 到末维 → reshape(-1,size) → unbind
  _TP @:2177（mq_broadcaster=True）
  _ETP @:2185（尺寸同 TP 则直接复用 _TP @:2192）
  _ENGRAM_DP @:2208（仅 DeepseekV41ForCausalLM @:2215）
  _DCP @:2250（transpose(-1,-2)，先跨 PCP 再跨 TP）
  _PCP @:2268 / _PP @:2287 / _DP @:2305
  _EP @:2326（dense 模型不建 :2328；use_all2all 可选）
  _EPLB @:2361（同 EP ranks 但独立 PG，隔离死锁）
```

运行期热路径是 PP 边界传 `IntermediateTensors`：`isend_tensor_dict`（vllm/distributed/parallel_state.py:1164）经 `_split_tensor_dict`（:116）拆 metadata+tensors，metadata 走 gloo、张量走 device backend；**2026-10 起主路径已异步化**——句柄连同源张量自保留进 `_pending_isends` FIFO（:589），`_reap_completed_isends`（:1127）在下一次发送前惰性回收（完成判据用 device backend 的 tensor handles，gloo 的 `is_completed()` 不可靠，注释 :1131-1140 写明）。`_RetainedHandle.wait()` 幂等（:85），因 worker 顶部 drain 与 reap 可能对同一 entry 二次 wait，而 gloo 点对点二次 wait 会永久阻塞（实测坑，:91-96）。

## ⑤ 设计决策

1. **组按"语义"而非"ranks"分裂**：EPLB 与 EP 同 ranks 却独立建组（:2361 注释），隔离 EPLB 重均衡通信与 MoE 前向 collective 的死锁；`make_sibling_device_group`（:591）同理为需并行的 op 流开"同成员、不同通信器"的兄弟组。
2. **MessageQueue 广播不再 TP 独享**：旧版只有 TP 组带 `mq_broadcaster`；现在 `_TP`（:2181）、`_DCP`（:2264）、`_INNER_DP_WORLD`（:2036）三组各建，并新增 `create_single_reader_mq_broadcasters`（:627）支持单读者拓扑——DCP 的 decode 调度元数据同步是新增消费者。
3. **Engram 专属组族**：ETP 让嵌入表 TP 尺寸独立于主干（:2187 从 engram_config 取），ENGRAM_DP 只在 DeepseekV41 且 GPU 表跨 DP 直读对端 HBM（NVLink 域，注释 :2222-2224）或按节点边界 gcd 对齐（`_engram_dp_shard_size`，:2058）时创建——维度爆炸换的是"每种通信模式一个精确组"。
4. **elastic EP 的世界替换是原子手术**：`_replace_active_groups`（:1567）先整体换出 DP→EP→WORLD→EPLB 四单例、旧组交调用方按序销毁；joining worker 在 ROCm 上经 `_elastic_join_warmup_ctx`（:2044）推迟通信器 warmup，等 commit 时新旧 ranks 一起暖机。
5. **split_group 从"实验"走向完整**：legacy 路径每组建组都发起全体 collective（组多时 O(N²) 慢）；split_group 路径（env `VLLM_DISTRIBUTED_USE_SPLIT_GROUP`，:489）父组一次 eager 绑定后按 `split_ranks` 切子组（:329），并配 `_validate_default_pg_for_split_group`（:1778）对 torchrun 等外部启动器给出"该给 init_process_group 传什么"的精确报错。
6. **CUDA graph 与通信器协同**：模块级 `graph_capture`（:1694）同时进 tp/pp/dp 三组各自的 capture 上下文（ca_comm/fi_pcie_ipc/aiter 各自注册 buffer），ROCm+aiter 时叠加 `non_expandable_allocations`（:1717）防捕获 buffer 被 realloc。

## ⑥ 新人提示

- 读法：:8 工作流 → :440 rank 表 → :2081 建组 reshape 代码，一条线即可；2780 行里大半是 docstring 与防御性 assert。
- 最易混淆仍是 `rank` vs `rank_in_group` vs `local_rank`；所有 `src/dst` 参数都是**组内局部 rank**（:831/:843 注释）。
- `barrier` 故意走 cpu_group（:1372 注释：NCCL barrier 内部是偷偷建 GPU tensor 的 broadcast，容易搞乱当前 device）。
- 集合通信别绕过 GroupCoordinator 直用 torch.distributed——custom all-reduce 分流、graph capture、custom op 分发全在这里；报 "expert parallel group is not initialized"（:1661）先查是不是 dense 模型误触 EP 路径。
- 排查建组慢/卡：先看 split_group 开关（:489），再看 elastic EP 是否误开（它把 world 换成 Stateless 协调，拓扑假设完全不同）。
