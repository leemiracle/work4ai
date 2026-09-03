# vllm/distributed/parallel_state.py — 分布式并行态深解

## 角色定位

位于 **distributed（分布式执行层）**，改编自 **Megatron-LM 的 parallel_state**（文件头注明）。它是 vLLM 从 PyTorch 手里接管分布式环境的**进程组世界中枢**：TP/PP/DP/EP/EPLB/PCP/DCP 各维度的 `GroupCoordinator` 单例全部在此创建、暴露访问器、销毁。docstring 给出标准工作流：`init_distributed_environment` → `initialize_model_parallel`（或 `ensure_model_parallel_initialized`）→ 业务代码 → `destroy_model_parallel` + `destroy_distributed_environment`。它不 spawn 进程（那是 executor 的活），只管理"进程排布成组"后的通信语义——**每个 GPU worker 进程各持有一份本模块状态**。图谱 60+ 条入边印证其底座地位：device_communicators、EPLB、elastic_ep、kv_transfer、以及大量模型层（mla_attention/mamba/fused_moe...）。

## 内部结构

- **`GroupCoordinator`**（核心类，~1000 行）：包一个 PyTorch ProcessGroup 双通道——`cpu_group`（gloo，控制面：broadcast_object/协调）+ `device_group`（nccl 等，数据面）。rank 语义三兄弟看类注释的表格：`rank`=全局 rank；`local_rank`=**节点内**序号（决定用哪块 GPU）；`rank_in_group`=组内序号（PP/TP 通信寻址用）。属性族 `is_first_rank/is_last_rank/next_rank/prev_rank` 直接服务 PP 相邻 stage 通信。集合通信方法（all_reduce/all_gather/reduce_scatter/broadcast*）world_size==1 时直通返回；可经 `torch.ops.vllm.*` custom op 走（torch.compile/Dynamo 兼容，group 用名字字符串寻址）。P2P：`send/recv_tensor_dict`（`_split_tensor_dict` 把 dict 拆 metadata+tensors 两段传）是 **PP stage 间传 IntermediateTensors 的通道**；`_RetainedHandle` 保活已发送张量且 `wait()` 幂等（gloo 二次 wait 会永久阻塞，注释里写明是实测坑）。
- **模块级全局单例 + 访问器**：`_WORLD/_INNER_DP_WORLD/_TP/_DCP/_PP/_DP/_EP/_EPLB/_PCP` 配 `get_tp_group()` 等断言访问器——教科书式"全局变量构成单例状态机"。`_groups` 注册表用 weakref 支撑按名分发与批量 `_apply_to_device_comms`（suspend/resume/checkpoint 状态恢复）。
- **`graph_capture`** 上下文：切独立 CUDA stream 捕获，同时让 custom all-reduce/flashinfer IPC/aiter 通信器进入捕获模式——CUDA graph 与 NCCL 冲突的经典解法。

## 外部连接

出边：`device_communicators/base_device_communicator`（按平台解析具体通信器类，custom all-reduce 等）、`utils.py`（StatelessProcessGroup/TCP store）、`envs`、平台层。**与 Ray 的关系**：本模块不含 Ray；Ray 只是 `distributed_executor_backend` 的一种——RayDistributedExecutor 负责跨节点拉起 worker 进程，之后每个 worker 仍调用本模块的 init 函数建组。`cleanup_dist_env_and_memory(shutdown_ray=True)` 才顺手 `ray.shutdown()`。

## 数据流（初始化）

```
init_distributed_environment(world_size, rank, ...):
  多节点/DP>1 时 rank 偏移 dp_rank*world_size，改用 master_addr:port
  torch.distributed.init_process_group(nccl)   （或 split_group 新路径:
    backend="cpu:gloo,cuda:nccl" + device_id 急切绑定）
  _WORLD = init_world_group(全 ranks)   # elastic EP 走 StatelessGroupCoordinator
  _NODE_COUNT 探测（共享内存握手 in_the_same_node_as）

initialize_model_parallel(tp, pp, pcp, dcp):
  布局序 ExternalDP × DP × PP × PCP × TP 的 5 维 rank 张量
  每个维度: transpose 到末维 → reshape(-1, size) → unbind → group_ranks
  _TP/PP/DP/EP/... = init_model_parallel_group(group_ranks, ...)
  例: 8 卡 TP=2 PP=4 → TP 组 [g0,g1][g2,g3]...，PP 组 [g0,g2,g4,g6][g1,g3,g5,g7]
```

EP 组仅 MoE 模型创建（跨度=DP×PCP×TP，即 PP 各 stage 共享专家划分），EPLB 与 EP 同 ranks 但**独立 ProcessGroup**——注释言明是为隔离 EPLB 重均衡通信与 MoE 前向 collective 的死锁风险。decode/prefill context parallel（DCP/PCP）是序列维并行的两个新维度。

## 关键设计决策

1. **rank 布局即一切**：5 维 reshape+transpose 生成各组 ranks，保证相邻 rank 落同节点（DGX 内 NVLink 互通）是**调用方约定**——TP 走 NVLink、PP 走网卡的性能前提。
2. **CPU/设备双 PG + 消息队列广播**：TP 组独享 `MessageQueue`（共享内存）广播对象，比 gloo broadcast_object 快一个量级，供 TP rank 间广播调度元数据。
3. **弹性扩展路径**：elastic EP 用 `StatelessGroupCoordinator`（不依赖全局 init 的 TCP-store 协调）支持 DP worker 动态伸缩；`_replace_active_groups` 原子换组（先换后毁，顺序 DP→EP→WORLD→EPLB）。
4. **`ensure_model_parallel_initialized`**：幂等入口，已初始化则断言尺寸匹配——external_launcher（torchrun）下防止重复建组。
5. **split_group 实验路径**（`VLLM_DISTRIBUTED_USE_SPLIT_GROUP`）：用 PyTorch 新 split_group API 替代 N 次 new_group（legacy 路径每组建一次全体 collective，组多时初始化 O(N²) 慢）。

## 新人提示

- 阅读顺序：类 docstring 的工作流 → `GroupCoordinator` 注释的 rank 表 → `initialize_model_parallel` 的 reshape 代码。
- 最易混淆：`rank` vs `rank_in_group` vs `local_rank`；`broadcast/gather` 的 `src/dst` 参数是**组内局部 rank**。
- TP 下模型代码里 all-reduce 的来源：column parallel（QKV/gate_up，输出维切）后接 row parallel（o_proj/down_proj，尾部 reduce）——组就来自 `get_tp_group()`，详见 `layers/linear.py`。
- 集合通信不要绕过 GroupCoordinator 直用 torch.distributed——custom all-reduce/graph capture/custom op 的分流逻辑都在这里。
