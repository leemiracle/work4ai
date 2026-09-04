# 深度解析：`python/sglang/srt/entrypoints/engine.py`

> 源码: python/sglang/srt/entrypoints/engine.py @ commit ec075d8bc

`engine.py` 实现 SGLang 推理引擎的 Python API 入口类 `Engine`——它把"一条命令启动的推理服务"拆成主进程 + 子进程拓扑并管理其全生命周期。SGLang 是多进程 LLM 推理框架：本文件 docstring（L182-189）明确三组件分工——TokenizerManager 在主进程内 tokenize 请求并经 ZMQ 发给 Scheduler；Scheduler 子进程组负责调度 batch、前向推理，把输出 token 发给 DetokenizerManager；后者 detokenize 后再经 ZMQ 回传 TokenizerManager。`Engine` 自己不碰模型权重：它只负责拉起/看护/回收这些子进程，并把 generate/encode/LoRA/权重热更新等调用同步封装后转发给 `tokenizer_manager`。它与 `http_server.py` 是并列的两种宿主形态：离线脚本直接 `Engine(model_path=...)`，在线服务则由 `http_server.launch_server` 复用其 `_launch_subprocesses` 后在主进程跑 FastAPI。文件长 1405 行，一个类 + 五个模块级辅助函数。

---

## 一、文件总览

| 行区间 | 内容 |
|---|---|
| L20–116 | imports；L46 threading atexit 补丁；L114 uvloop 策略 |
| L119–127 | `SchedulerInitResult` dataclass |
| L130–175 | `init_tokenizer_manager()` 模块函数 |
| L178–1212 | `Engine` 类（入口 API + 子进程编排） |
| L1215–1300 | `_set_envs_and_config()`：全局环境与信号 |
| L1303–1307 | `_set_gc()` |
| L1310–1350 | `_scheduler_died_error` / `_wait_for_scheduler_ready` |
| L1353–1405 | `_calculate_rank_ranges` / `_compute_parallelism_ranks` |

`Engine` 拉起后的典型进程树（单机 TP2 为例）：

```
主进程 (python 脚本 / Engine)
├── TokenizerManager          （同进程对象，非子进程）
├── Scheduler tp_rank=0       （mp.Process, spawn；持有 GPU 0）
├── Scheduler tp_rank=1       （mp.Process, spawn；持有 GPU 1）
├── DetokenizerManager        （mp.Process；多 worker 时 + MultiDetokenizerRouter）
└── [可选] ExpertBackupManager（elastic EP）/ EngineInfoBootstrapServer（线程）

ZMQ 通道（PortArgs 分配，见 server_args.py 2.10）：
  TokenizerManager ──scheduler_input_ipc──> Scheduler(rank0 / DP controller)
  Scheduler ──detokenizer_ipc──> DetokenizerManager ──tokenizer_ipc──> TokenizerManager
  Engine ──rpc_ipc(DEALER)──> Scheduler(ROUTER)          # collective_rpc 通道
  Scheduler ──metrics_ipc──> TokenizerManager            # Prometheus 指标
```

DP 场景下多一层：主进程只启动 **DataParallelController**（L631-645），由它再 fork `dp_size × (tp/pp)` 个 Scheduler，孙进程 pid 经 pipe 回传汇入 `all_child_pids`（L654-657）。多节点场景下每个节点各有一棵同样的树，非零 rank 节点没有 TokenizerManager/DetokenizerManager（L807-833）。

启动时序（`_launch_subprocesses`，L734–880）：

| 序 | 动作 | 行号 |
|---|---|---|
| 1 | `configure_logger` + `_set_envs_and_config`（NCCL/CUDA env、SIGQUIT、spawn） | L755-756 |
| 2 | `load_plugins()`（防御性二次加载） | L760 |
| 3 | `server_args.check_server_args()`（跨字段终审） | L762 |
| 4 | `_set_gc`（gc_threshold） | L763 |
| 5 | `PortArgs.init_new`（ZMQ 端点分配） | L766-767 |
| 6 | 可选 `EngineInfoBootstrapServer`（远程权重 seed 服务） | L771-785 |
| 7 | `resolve_auto_parsers`（reasoning/tool-call auto 解析） | L787-791 |
| 8 | `_launch_scheduler_processes`（scheduler 或 DP controller 先行） | L794-796 |
| 9 | 可选 `run_expert_backup_manager`（elastic EP） | L801-805 |
| 10 | node_rank≥1：`wait_for_ready` → dummy health server → `wait_for_completion` 常驻 | L807-833 |
| 11 | `_launch_detokenizer_subprocesses`（1 worker 或 N+router） | L837-843 |
| 12 | tokenizer 侧：`init_tokenizer_manager` 或 `MultiTokenizerRouter` | L846-853 |
| 13 | `wait_for_ready`（全部 rank 模型加载完毕）+ 回传 `max_req_input_len` | L856-861 |
| 14 | `SubprocessWatchdog(processes, names).start()` | L863-872 |

顺序的依据：scheduler 加载权重最慢所以先起；tokenizer manager 建立时 bootstrap server 已就位（L845 注释）；`max_req_input_len` 在 ready 后才存在。

---

## 二、核心类与函数

### 2.1 模块级序幕（L45–116）

- `L46: setattr(threading, "_register_atexit", lambda *args, **kwargs: None)` —— 打掉 Python 标准库 threading 的 atexit 注册，否则 spawn 出的子进程在解释器退出路径上可能死锁（社区已知 bug 的 workaround，一行体现"多进程工程"属性）。
- `L114: asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())` —— 模块 import 即切换 uvloop，Engine 的同步 `generate`（内部 `loop.run_until_complete`）与后续 HTTP 服务共享高性能事件循环。

### 2.2 `SchedulerInitResult`（L119–127）

启动调度器的结果载体：`scheduler_infos`（各 rank 经 pipe 回传的 `max_req_input_len` 等元信息，最终暴露到 `/get_server_info`）、`all_child_pids`（供 `kill_process_tree` 收尸）、`wait_for_ready` / `wait_for_completion` 两个闭包（把"等模型加载完"与"join 进程退出"从启动路径解耦，多节点场景 node_rank>0 只调 wait）、`engine_info_bootstrap_server`（远程权重加载的种子信息服务）。**返回闭包而非句柄**，是为了让 RayEngine 等子类能替换等待语义。

### 2.3 `init_tokenizer_manager`（L130–175）

模块函数而非方法，目的是能被 `Engine.init_tokenizer_manager_func` 类字段替换（私有 fork 注入点）。流程：构造 `TokenizerManager(server_args, port_args)` → `TemplateManager().initialize_templates(...)`（chat/completion 模板）→ 处理 `reasoning_parser/tool_call_parser == "auto"`：用模板探测结果回填 server_args，探测失败则告警并置 None（L149-173）。这一步在主进程内完成，是"TokenizerManager 与 Engine 同进程"原则的具体落点。

### 2.4 `Engine` 类（L178–1212）

类声明 `class Engine(EngineScoreMixin, EngineBase)`：`EngineBase`（entrypoints/EngineBase.py）是抽象基类，统一 HTTP-engine 与离线 Engine 的 `generate/flush_cache/update_weights_from_tensor/load_lora_adapter/release_memory_occupation` 签名；`EngineScoreMixin` 提供 `score/async_score`（L1212 注释）。四个**类级可覆写字段**（L194–197）`server_args_class / init_tokenizer_manager_func / run_scheduler_process_func / run_detokenizer_process_func`——注释直言"允许私有 fork 替换以启动自己的进程"，RayEngine 即靠覆写 `_launch_scheduler_processes`（ray/engine.py L92）用 Ray actor 替代 `mp.Process`。

#### `__init__`（L199–272）

1. `L207: load_plugins()` —— **先于 ServerArgs 构造**加载插件，让挂在 `ServerArgs.__post_init__` 上的钩子（platforms 注入默认值、choices 扩展）能触发。
2. 参数双形态（L210–218）：kwargs 逐项构造 `server_args_class(**kwargs)`（离线用法默认压 `log_level="error"` 保持库安静）；或直接传 `server_args=` 整对象（服务端路径复用 CLI 解析结果）。
3. `L224: self.tokenizer_manager = None` 预置 + `L227: atexit.register(self.shutdown)` —— 防解释器退出时 handler 撞 AttributeError；即使脚本忘调 `shutdown()` 也能收掉子进程。
4. `L230–241`：调 `_launch_subprocesses`（见 2.5）拿五元组；watchdog 挂到 `tokenizer_manager._subprocess_watchdog`（L246，tokenizer 侧可停它）。
5. `L250–256`：主进程建 `zmq.Context(2)` 与 DEALER socket `send_to_rpc`（node_rank==0 才建；多节点非零 rank 的 Engine 不服务 RPC）——这是 `collective_rpc` 的通道。
6. `L259–266`：OTel tracing 初始化，thread label 按 `disaggregation_mode` 区分 Prefill/Decode Tokenizer。
7. `L268–272`：事件循环三态——已有 running loop 就复用（异步宿主内嵌场景），否则新建并 set。

#### 同步/异步双生的请求 API

`Engine` 的公开方法几乎都是"组请求对象 → 交 `tokenizer_manager` → （同步版）`loop.run_until_complete` 桥接"的薄封装，方法清单：

| 方法 | 行号 | 请求对象 | 备注 |
|---|---|---|---|
| `generate` | L309 | `GenerateReqInput` | 同步；stream 返回同步生成器 |
| `async_generate` | L401 | `GenerateReqInput` | 异步镜像 |
| `encode` / `async_encode` | L483 / L516 | `EmbeddingReqInput` | embedding |
| `rerank` | L550 | `EmbeddingReqInput(is_cross_encoder_request=True)` | 交叉编码器 |
| `score` / `async_score` | （mixin） | — | 由 `EngineScoreMixin` 提供（L1212） |
| `flush_cache` | L900 | — | 清空 radix cache |
| `open_session` / `close_session` | L903 / L933 | `OpenSessionReqInput` / `CloseSessionReqInput` | KV 共享多轮会话 |
| `start_profile` / `stop_profile` | L942 / L945 | — | torch profiler |
| `start/stop/dump_expert_distribution_record` | L948–961 | — | 专家负载统计 |
| `get_server_info` | L963 | — | `/get_server_info` 数据源 |
| `init_weights_update_group` | L974 | `InitWeightsUpdateGroupReqInput` | RL 权重广播组 |
| `destroy_weights_update_group` | L996 | — | 拆组 |
| `update_weights_from_distributed` | L1008 | `UpdateWeightsFromDistributedReqInput` | torch.distributed 广播 |
| `update_weights_from_tensor` | L1030 | `UpdateWeightsFromTensorReqInput` | 按 tp_size 序列化 N 份 |
| `update_weights_from_disk` | L1054 | `UpdateWeightFromDiskReqInput` | 免重启换模型 |
| `update_weights_from_ipc` | L1074 | `UpdateWeightsFromIPCReqInput` | checkpoint-engine 集成 |
| `get_weights_by_name` | L1088 | `GetWeightsByNameReqInput` | 读取权重 |
| `load_lora_adapter_from_tensors` | L1095 | `LoadLoRAAdapterFromTensorsReqInput` | 内存 tensor 直载 |
| `load_lora_adapter` / `unload_lora_adapter` | L1118 / L1131 | `Load/UnloadLoRAAdapterReqInput` | 运行时挂/摘 |
| `async_load_lora_adapter` / `async_unload_lora_adapter` | L1140 / L1157 | 同上 | 异步版 |
| `release_memory_occupation` / `resume_memory_occupation` | L1168 / L1174 | `Release/ResumeMemoryOccupationReqInput` | 显存让渡/恢复 |
| `freeze_gc` | L1180 | — | 冻结 GC 扫描范围 |
| `collective_rpc` | L1199 | `RpcReqInput` | 所有 scheduler 上执行任意方法 |
| `save_remote_model` / `save_sharded_model` | L1206 / L1209 | — | collective_rpc 薄封装 |

逐个说明关键细节：

- `generate`（L309–399）：参数与 `io_struct.GenerateReqInput` 一一对应（prompt/input_ids/sampling_params/多模态三通道 image/audio/video/logprob 族/`lora_path`/`custom_logit_processor`/`return_hidden_states/return_routed_experts`/`bootstrap_*`（PD 分离）/`rid`/`session_params`/`priority`）。先经 `_resolve_routed_dp_rank`（L278：`data_parallel_rank` 弃用警告→`routed_dp_rank`；dp_size≤1 时忽略 rank0 并告警；越界抛 ValueError），再组 `GenerateReqInput` 交给 `tokenizer_manager.generate_request`。**stream 模式的同步包装是亮点**（L386–396）：`generator_wrapper` 在同步生成器里逐个 `loop.run_until_complete(generator.__anext__())`，把异步流适配成 Python 迭代器给脚本用。
- `encode / async_encode`（L483–548）：embedding 请求，支持 `dimensions` 截断（Matryoshka）与 `embed_override_token_id/embed_overrides`（指定 token 的 embedding 覆写）。
- `update_weights_from_tensor`（L1030–1052）：非 `flattened_bucket` 格式时用 `MultiprocessingSerializer.serialize` **按 `tp_size` 份**序列化（每个 scheduler 进程独立反序列化一份，避免多进程共享 mmap 的写冲突）；`flattened_bucket` 直接透传（调用方已序列化好）。
- `open_session`（L903–931）：`capacity_of_str_len` 预留字符串容量、`streaming` 走 append-only 低开销路径、`timeout` 空闲自动回收——服务端 cache-aware 多轮对话的基础。
- `collective_rpc`（L1199–1204）：DEALER socket 发 `RpcReqInput`、**同步阻塞**收 `RpcReqOutput`，断言 success——这是把"任意方法名"打到所有 scheduler 的通用后门，测试与运维常用。

典型用法对照（对应上述方法族）：

```python
from sglang import Engine

with Engine(model_path="meta-llama/Llama-3.1-8B-Instruct",
            tp_size=2, log_level="error") as llm:
    # 1) 离线批量生成（非流式）
    out = llm.generate(["你好，介绍一下自己", "写一首五言绝句"],
                       sampling_params={"temperature": 0.7, "max_new_tokens": 256})
    print(out[0]["text"])

    # 2) 流式：返回同步生成器（L386 generator_wrapper 包装的异步流）
    for chunk in llm.generate("讲个长故事", sampling_params={"max_new_tokens": 512},
                              stream=True):
        print(chunk["text"], end="", flush=True)

    # 3) RL 场景：训练侧广播新权重（torch.distributed 通道）
    llm.init_weights_update_group(master_addr="127.0.0.1", master_port=29500,
                                  rank=1, world_size=2)
    llm.update_weights_from_distributed(names, dtensors)
    llm.destroy_weights_update_group()

    # 4) 运维后门：在所有 scheduler 上执行任意方法
    info = llm.collective_rpc("get_internal_state")
# with 块结束 → __exit__ → shutdown() → kill_process_tree（阻塞至 GPU 释放）
```

#### 生命周期与运维方法（L882–1210）

**shutdown 的三层语义**（L882–891）：

1. 停 `SubprocessWatchdog`（避免收尸过程中误报崩溃）；
2. `kill_process_tree(os.getpid(), include_parent=False, wait_timeout=60)`——按"杀本 pid 的整棵子树但保留自己"的语义实现，覆盖 scheduler/detokenizer/DP controller/孙进程全部；
3. docstring 强调**阻塞到 Scheduler 释放 GPU context**（wait_timeout=60），调用方可立即在同卡重启新实例——这对"训练/推理轮流用卡"的 RL 工作流至关重要。

配套机制：`__enter__/__exit__`（L893–898）支持 `with Engine(...) as llm:`；`__init__` 里的 `atexit.register(self.shutdown)`（L227）兜底脚本自然退出的场景；`L224` 预置 `self.tokenizer_manager = None` 防 handler 撞 AttributeError。

其余运维方法见 2.4 方法清单表。几个值得展开：

- `get_server_info`（L963–972）：返回 `{**asdict(server_args), **scheduler_infos[0], internal_states, version}`——CLI flag、运行时状态、版本三合一，是 `/get_server_info` 端点与诊断工具的数据源。
- `freeze_gc`（L1180–1193）：docstring 给出完整 rationale——服务预热后长命对象不再变化，冻结 GC 扫描范围可显著降低 decode 尾延迟（GC 停顿在百 GB 级对象图上是毫秒级杀手）。
- `release/resume_memory_occupation`（L1168–1178）：配合 `enable_memory_saver`（TorchMemorySaverAdapter，L581-583 在 scheduler 启动时注入）把权重换出 GPU，给训练进程腾卡，再 `resume` 回来继续服务，无需重新加载。

### 2.5 子进程启动三部曲（核心）

#### ① `_launch_scheduler_processes`（L564–675，classmethod）

- **dp_size==1 路径**（L579–630）：对每个 `(pp_rank, tp_rank)` 组合建 `mp.Pipe(duplex=False)`；GPU 编号公式（L598–602）`gpu_id = base_gpu_id + (pp_rank%pp_size_per_node)*tp_size_per_node + (tp_rank%tp_size_per_node)*gpu_id_step`——多机多卡时同一物理卡池的正确映射。`_compute_parallelism_ranks`（L1388–1405）把 tp_rank 换算成 `(attn_cp_rank, moe_dp_rank, moe_ep_rank)`，注释写明并行层级（外→内）：Attention 为 Global(TP)→DP→ATTN_CP→ATTN_TP，MoE 为 Global(TP)→MOE_DP→EP→MOE_TP。`proc.start()` 包在 `memory_saver_adapter.configure_subprocess()` 与 `numa_utils.configure_subprocess()` 双上下文里（L623–627）——TorchMemorySaver 让子进程可挂起显存，NUMA 绑定按 `numa_node` 参数设亲和。
- **dp_size>1 路径**（L631–645）：只启动**一个** `run_data_parallel_controller_process`，由它再 fork 全部 DP scheduler——DP 拓扑的递归启动权下放给 `managers/data_parallel_controller.py`。
- 返回的 `wait_for_ready` 闭包（L650–657）从 pipes 收集 infos，DP 模式下额外从 info 的 `SCHEDULER_PIDS_ARG` 吸收 controller 报告的孙进程 pid；`wait_for_completion`（L659–665）join 所有 proc 并在异常退出时打 error 日志。

#### ② `_launch_detokenizer_subprocesses`（L677–732）

`detokenizer_worker_num<=1`：单进程监听 `port_args.detokenizer_ipc_name`（经典形态）。`>1`：每个 worker 分配私有临时 ipc 名（L711），最后额外启动 `MultiDetokenizerRouter` 进程**霸占原 ipc 名**做扇出（L724–730）——对 Scheduler 侧完全透明，上游无感知扩容。`finally` 块（L721–722）保证 router 启动失败也恢复 `port_args.detokenizer_ipc_name` 原值。

#### ③ `_launch_subprocesses`（L734–880，总编排）

顺序即协议：
1. `configure_logger` + `_set_envs_and_config`（L755–756）→ 再 `load_plugins()`（防御性双保险，L760）→ `server_args.check_server_args()`（L762，server_args.py 终审校验的调用点）→ `_set_gc`（L763）。
2. `PortArgs.init_new(server_args)`（L767）分配 ZMQ 端点。
3. 可选 `EngineInfoBootstrapServer`（L771–785）：远程实例权重加载的 seed 节点信息服务，端口占用立即报错（多实例同机需显式分端口）。
4. `reasoning_parser/tool_call_parser=auto` 时先 `resolve_auto_parsers`（L787–791）。
5. 启动 schedulers（L794）；若开弹性 EP 再 `run_expert_backup_manager`（L801–805）。
6. **多节点分支**（L807–833）：`node_rank>=1` 的节点不跑 tokenizer/detokenizer——`wait_for_ready` 后，除非 env `SGLANG_BLOCK_NONZERO_RANK_CHILDREN=0`（Python API 内嵌场景提前返回 L812–820），否则起一个 **dummy health check server 占住 host:port**（L822，让 K8s/负载均衡探针有东西可探）然后 `wait_for_completion` 常驻等待。
7. 启动 detokenizer（L837–843，pid 并入 `all_child_pids`）。
8. `tokenizer_worker_num==1` → 主进程建 TokenizerManager/TemplateManager；`>1` → 建 `MultiTokenizerRouter`（L846–853，模板管理退位）。
9. `wait_for_ready`（L856）等全部 rank 模型加载完；**回传 `max_req_input_len`** 给 tokenizer_manager（L859–861）——TokenizerManager 由此能在入口端拒绝超长请求，而不是等 Scheduler 报错。
10. 组装 `SubprocessWatchdog(processes, names)`（L863–872）并 start：后台线程轮询子进程存活，崩了主动拉响整树退出（RayEngine 传 `scheduler_procs=None`，L864 注释）。

### 2.6 模块级辅助

- `_set_envs_and_config`（L1215–1300）：启动前的全局环境定型，逐项列出：

  | env/动作 | 值 | 行号 | 动机 |
  |---|---|---|---|
  | `NCCL_CUMEM_ENABLE` | `int(enable_symm_mem)` | L1217-1218 | 对称内存与 CuMem 显存池互斥 |
  | `NCCL_NVLS_ENABLE` | nvls 或 symm_mem | L1219-1226 | NVLink SHARP |
  | `CUDA_DEVICE_MAX_CONNECTIONS` | 8 | L1227 | flash attention 的经典坑（>1 会退化） |
  | `CUDA_MODULE_LOADING` | AUTO | L1228 | 按需 JIT 加载省内存 |
  | `TRTLLM_ENABLE_PDL` | 1 | L1230-1232 | flashinfer MoE/量化 kernel 的 PDL |
  | `CUTE_DSL_LOG_LEVEL/TO_CONSOLE` | 30 / 1 | L1234-1240 | CuteDSL 日志降噪 |
  | `SGLANG_RUN_ID` | 时间戳+随机数 | L1243-1245 | 一次启动的唯一标识（日志/追踪关联） |
  | prometheus multiproc dir / `set_ulimit` | — | L1248-1252 | 多进程指标与 fd 上限 |
  | flashinfer 0.6.11.post1 / sglang-kernel 0.4.3 版本断言 | — | L1255-1269 | kernel ABI 崩溃预防（`SGLANG_SKIP_SGL_KERNEL_VERSION_CHECK` 可跳） |
  | SIGQUIT launch-phase handler | `kill_process_tree` | L1272-1291 | 子进程失败→SIGQUIT 主进程→全树清理；gRPC 起来后被 tokenizer manager 的 running-phase handler 替换；`custom_sigquit_handler` 支持 crash dump |
  | `mp.set_start_method("spawn", force=True)` | — | L1300 | CUDA + fork 不安全；force 兼容外层已设 fork 的宿主 |

  注意只有主线程才注册信号（L1272 判断），非主线程启动 Engine 会 warning 并失去该保护（L1292-1297）。
- `_set_gc`（L1303）：按 `gc_threshold` 三元组调 `gc.set_threshold`（与 `freeze_gc` 方法配合）。
- `_scheduler_died_error`（L1310）：先 `join(10)` 拿 exitcode，报错文案直接提示"exit -9 多半是 OOM killer，跑 `dmesg -T | grep -i oom`"——把最常见的排障路径写进异常。
- `_wait_for_scheduler_ready`（L1321–1350）：关键在 `poll(timeout=5.0)` 而非阻塞 `recv()`（docstring L1325-1329）：每 5 秒醒一次扫所有进程 `is_alive()`，**子进程被 OOM SIGKILL 时立刻报错而不是永远挂死**；EOFError（pipe 关闭）→ died；`data["status"] != "ready"` → 初始化失败；两个分支分别转成带 rank 信息的 RuntimeError。
- `_calculate_rank_ranges`（L1353–1385）：给定 `(nnodes, pp_size, tp_size, node_rank)` 算本节点负责的 pp/tp rank 区间——`pp_size_per_node = pp//nnodes`、`nnodes_per_pp_rank = nnodes//pp`，支撑"PP 跨节点、TP 不跨节点"的默认切法。例：`nnodes=2, pp=2, tp=4` 时每节点 1 个 pp rank × 2 个 tp rank；`nnodes=2, pp=1, tp=8` 时两节点各持 tp rank 0-3 与 4-7（跨节点 TP）。
- `_compute_parallelism_ranks`（L1388–1405）：见 2.5①。手算示例加深理解——设 `tp_size=8, dp_size=2, attn_cp_size=2, moe_dp_size=1, ep_size=4`：
  - `attn_tp_size = tp // dp // attn_cp = 8//2//2 = 2`；
  - `attn_cp_rank = (tp_rank // 2) % 2`——tp_rank 0,1 的 attn_cp_rank=0（它们各持序列一半的 CP 分片），2,3 为 1，4,5 为 0，6,7 为 1；
  - `moe_dp_rank = tp_rank // (tp//moe_dp) = tp_rank // 8` 恒为 0（moe_dp=1 时无 MoE DP 切分）；
  - `moe_ep_rank = (tp_rank % 8) // (8//1//4) = tp_rank // 2`——0,1→expert 组 0；2,3→1；4,5→2；6,7→3。
  三个整除/取模公式是理解 SGLang"一卡多角色"（同一 tp_rank 同时处于 attention-CP 组与 MoE-EP 组）混合并行的钥匙。

---

## 三、与其他模块的交互

**import 了谁**（直接协作者）：

| 来源 | 符号 | 用途 |
|---|---|---|
| `managers/tokenizer_manager` | `TokenizerManager` | 主进程请求枢纽 |
| `managers/scheduler` | `run_scheduler_process` | scheduler 子进程入口（可注入） |
| `managers/detokenizer_manager` | `run_detokenizer_process` | detokenizer 子进程入口（可注入） |
| `managers/data_parallel_controller` | `run_data_parallel_controller_process`、`SCHEDULER_PIDS_ARG` | DP 拓扑递归启动 + 孙 pid 回传 |
| `managers/multi_tokenizer_mixin` | `MultiTokenizerRouter`、`run_multi_detokenizer_router_process` | 多 tokenizer / 多 detokenizer 扇出 |
| `managers/io_struct` | 20+ ReqInput/Output | Engine API 的类型化协议层 |
| `managers/template_manager` / `template_detection` | `TemplateManager`、`resolve_auto_parsers` | 模板与 auto parser 解析 |
| `entrypoints/EngineBase` / `engine_score_mixin` / `engine_info_bootstrap_server` | 基类 / score / seed 服务 | 接口契约与远程权重加载 |
| `server_args` | `ServerArgs`、`PortArgs` | 配置与 ZMQ 地址簿 |
| `utils`（含 network/watchdog/numa/torch_memory_saver_adapter） | `kill_process_tree`、`get_zmq_socket`、`SubprocessWatchdog` 等 | 进程与基础设施 |
| `elastic_ep.expert_backup_manager` | `run_expert_backup_manager` | 弹性 EP 权重备份 |
| `observability.trace`、`plugins`、`version` | tracing / 插件 / 版本号 | 杂项 |

**被谁调用**（grep 全仓查证）：

- `entrypoints/http_server.py:70` import，其 `launch_server`（http_server L2365）**直接调 `Engine._launch_subprocesses(...)` classmethod** 而不实例化 Engine——HTTP 服务复用启动编排，但主进程由 FastAPI/uvicorn（或 granian http2）接管。
- `srt/ray/engine.py:79` 的 `RayEngine(Engine)` 覆写 `_launch_scheduler_processes`（Ray actor，返回 `scheduler_procs=None`，watchdog 对其为空操作 L864-865）；`ray/http_server.py`、`ray/data_parallel_controller.py` 复用其启动函数与 rank 工具。
- 离线入口：`sglang/lang/api.py:44`（旧 API 兼容 lazy import）、`sglang/bench_offline_throughput.py:30`、`srt/weight_sync/utils.py:8`（RL 权重同步工具）实例化 `Engine`；`sglang/bench_one_batch.py:68` 单独 import `_set_envs_and_config` 做基准前环境对齐。

**与 `launch_server.py` 的完整关系链**：

```
python -m sglang.launch_server
  → prepare_server_args (server_args.py L7700, argparse + --config 合并)
  → http_server.launch_server(server_args)
      → Engine._launch_subprocesses(...)      # 借 classmethod，不建 Engine 实例
      → _setup_and_run_http_server(...)       # FastAPI 路由挂在 tokenizer_manager 上
```

即：**Engine 类 = 无 HTTP 宿主的纯净版服务**；`http_server` 与 `Engine` 是同一编排的两种宿主形态。改动 `_launch_subprocesses` 的行为时两条路径都会受影响，回归测试须两侧都跑。

---

## 四、关键设计决策

1. **"编排与宿主分离"**：`_launch_subprocesses` 做成 classmethod 并接受三个可注入函数（`init_tokenizer_manager_func/run_scheduler_process_func/run_detokenizer_process_func`），使同一套编排同时服务三种宿主——离线 `Engine`（实例化）、在线 `http_server`（只借启动函数）、分布式 `RayEngine`（覆写 scheduler 启动）。类字段注入点（L194–197）则照顾私有 fork，避免大改主干。
2. **同步 API 构建在异步核心上**：TokenizerManager 全异步，Engine 用 `loop.run_until_complete` + 生成器包装（L386–398）把它翻成同步/迭代器接口。一次实现、两种消费方式，且 uvloop 模块级安装保证同步路径性能不打折。
3. **故障即全树退出（fail-fast process tree）**：SIGQUIT 约定（子进程出错→通知主进程→`kill_process_tree`）+ atexit 双保险 + `SubprocessWatchdog` 存活巡检 + `poll(5s)` 防挂死的 ready 等待。多进程推理服务里"半死不活"比"崩溃重启"更危险，这套组合拳确保任何单点死亡都在秒级放大成可观测的整树退出。
4. **启动顺序编码了数据依赖**：scheduler 先起（加载权重最慢，先跑）、detokenizer 次之、tokenizer manager 最后建但仍要 `wait_for_ready` 等 scheduler 汇报——`max_req_input_len` 的回传（L859）让入口端具备拒绝非法请求的能力；非零 rank 节点用 dummy health server 占端口（L822）解决了"多节点下探针该打谁"的运维问题。
5. **Engine 是 façade 不是引擎**：generate/encode/LoRA/权重更新全部转发 `tokenizer_manager`，自身只多出三样东西——进程编排、RPC DEALER socket、事件循环桥接。这让 `EngineBase` 抽象能同时覆盖 HTTP 引擎与本类，weight_sync 等工具也能复用同一接口。

---

## 五、阅读建议

1. **先读 docstring 与 `__init__`（L178–272）**，对照三组件图（TokenizerManager→Scheduler→DetokenizerManager 的 ZMQ 环）建立全局观；再跳读 `_launch_subprocesses`（L734–880）理解启动时序。
2. 精读 `_launch_scheduler_processes`（L564–675）时手算一遍 `_compute_parallelism_ranks`（L1388）：取 `tp_size=8, dp_size=2, attn_cp_size=2, ep_size=4` 之类例子代入整除/取模公式，是理解 SGLang 混合并行最快的路径。
3. 读 `_set_envs_and_config`（L1215）留意两类副作用：NCCL/CUDA env 定型（影响所有子进程）与 SIGQUIT 注册（注意"launch 阶段 handler 会被替换"的注释，排查信号问题时不被迷惑）。
4. 调试启动挂死/OOM 时直接看 `_wait_for_scheduler_ready`（L1321）与 `_scheduler_died_error`（L1310）：报错文案自带 `dmesg` 排查指引；PID 全集在 `get_all_child_pids`（L274）。
5. 写离线脚本优先用 `with Engine(...) as llm:`（`__exit__` 保证 `shutdown`）；需要流式输出时理解 `generate(stream=True)` 返回的是同步生成器包装（L386），底层仍是异步流。
6. 与 http_server 的关系要分清：`launch_server` 借的是 `_launch_subprocesses` 这个 classmethod，**不会构造 Engine 实例**——两份"宿主"共享编排但各有各的生命周期管理；改动启动逻辑时务必两侧回归。
7. 延伸阅读顺序：`managers/tokenizer_manager.py`（请求如何进 ZMQ）→ `managers/scheduler.py`（batch 调度与 KV 管理）→ `managers/detokenizer_manager.py`（回程）→ `srt/ray/engine.py`（编排如何被 Ray 替换）。

---

## 六、常见误区与排障速查

| 症状 | 根因定位 | 关联行号 |
|---|---|---|
| `Engine(...)` 卡在启动不放 | scheduler 加载权重慢（正常）vs 子进程已死——看 `_wait_for_scheduler_ready` 的 5s 轮询是否已抛错 | L1321–1350 |
| 报 "Scheduler ... died, exit code -9" | OOM killer；按异常文案跑 `dmesg -T \| grep -i oom`，或降 `mem_fraction_static` | L1310–1319 |
| 子进程崩了但主进程还活着 | watchdog 未启动（RayEngine 传 None）或非主线程启动 Engine 丢了 SIGQUIT 保护 | L864, L1272, L1292–1297 |
| 同卡重启新实例报显存不足 | 旧实例 shutdown 未等 GPU context 释放；确认走的是 `shutdown()` 而非直接 kill（wait_timeout=60） | L882–891 |
| 多节点非零 rank 节点探针失败 | 该节点只有 dummy health server——探针应打 node_rank=0 | L822 |
| `generate(stream=True)` 在异步代码里用不了 | 它返回同步生成器，异步宿主请用 `async_generate` | L386–398 |
| 端口被占（bootstrap/rpc） | `EngineInfoBootstrapServer` 默认 6789，多实例需显式分端口 | L771–785 |
| DP 模式子进程没被杀干净 | 孙进程 pid 靠 `SCHEDULER_PIDS_ARG` 回传；确认 controller 正常上报 | L654–657 |

三个易错点提醒：

1. **别在 Engine 存活期间手动 kill 单个 scheduler**——watchdog 会把整树拉倒（这是设计行为，fail-fast）；
2. **`data_parallel_rank` 已弃用**——用 `routed_dp_rank`，且 `dp_size≤1` 时传 rank 会被忽略并告警（L278–307）；
3. **`log_level` 默认值差异**——离线 `Engine(**kwargs)` 默认压成 `error`，服务端路径原样透传 CLI 值；排查离线脚本问题记得显式传 `log_level="info"`。
