# 深度解析：`python/sglang/srt/model_executor/model_runner.py`

> 源码: python/sglang/srt/model_executor/model_runner.py @ commit ec075d8bc（3570 行）

## 目录

- [一、职责概述](#一职责概述)
- [二、数据流全景](#二数据流全景modelrunner-在主链路中的位置)
- [三、核心类与函数](#三核心类与函数)
  - [3.1 模块级常量与辅助](#31-模块级常量与辅助l246-335)
  - [3.2 `__init__` 初始化链](#32-__init__-初始化链l341-579)
  - [3.3 `initialize()` 总编排](#33-initialize加载内存池backendcuda-graph-的总编排l610-829)
  - [3.4 `load_model()`](#34-load_modell1236-1443)
  - [3.5 KV cache 管理 mixin](#35-kv-cache-管理modelrunnerkvcachemixin)
  - [3.6 attention backend 选择](#36-attention-backend-选择l2243-2317)
  - [3.7 CUDA Graph 协同](#37-cuda-graph-协同l2778-2962)
  - [3.8 forward 全模式执行](#38-forward-全模式执行l3008-3369)
  - [3.9 `sample()` 与 logits 后处理](#39-sample-与-logits-后处理l3371-3451)
  - [3.10 权重更新家族](#310-权重更新家族在线学习多实例协同)
  - [3.11 LoRA](#311-lora-l1998-2084)
  - [3.12 模型族适配属性族](#312-模型族适配属性族l2086-2186)
  - [3.13 `_dummy_run` 详解](#313-_dummy_run-详解l2457-2732)
  - [3.14 elastic EP 与专家并行运维](#314-elastic-ep-与专家并行运维)
- [四、与其他模块的交互](#四与其他模块的交互)
- [五、关键设计决策](#五关键设计决策)
- [六、阅读建议](#六阅读建议)
- [附录：方法级索引](#附录方法级索引)

## 一、职责概述

`ModelRunner` 是 SGLang scheduler 进程内的**推理执行器（inference executor）**：它向下封装"一块 GPU + 一个模型副本"的全部执行细节，向上对 `TpModelWorker` / scheduler 暴露四个动词——**加载模型、管理显存池、跑 forward、采样**。本文件是该类的主体实现（3570 行），与两个协作文件共同构成执行层：

- `model_runner_kv_cache_mixin.py`：`ModelRunnerKVCacheMixin`，KV cache 内存池的容量推导与创建（`ModelRunner` 通过继承获得）；
- `forward_batch_info.py`：`ForwardBatch`，单次 forward 的全部输入张量（见同系列另篇解析）；
- `cuda_graph_runner.py` / `piecewise_cuda_graph_runner.py`：CUDA Graph 捕获与重放（已有独立解析篇）。

一句话定位：**scheduler 决定"这一步跑哪些请求"，ModelRunner 决定"这一步在 GPU 上具体怎么跑"**。它完成五件事：

1. **模型加载**：分布式环境初始化（NCCL/TP/PP/EP/DP/CP 进程组）→ 权重加载（多种 load format）→ 量化/LoRA/torch TP 后处理；
2. **KV Cache 内存池创建**：加载后按 `mem_fraction_static` 推导 `req_to_token_pool` 与 `token_to_kv_pool_allocator` 的容量；
3. **attention backend 选择**：按设备/模型架构/用户参数从 `ATTENTION_BACKENDS` 注册表选出 prefill/decode（可不同）的 attention kernel 实现；
4. **forward 全模式执行**：`EXTEND`（含 prefill/chunked prefill/mixed）、`DECODE`、`IDLE`（DP attention 空转）、`SPLIT_PREFILL`、speculative 系列模式，并决定走 CUDA Graph replay 还是 eager forward；
5. **采样**：logits 预处理（grammar bias）→ `sampler` 采样 → logprob 计算。

此外它还承载一批"在线运维"能力：RLHF 权重热更新（`update_weights_from_distributed/tensor`）、远程实例权重分发、EPLB 专家重平衡、elastic EP 掉卡恢复、LoRA 动态加载。

## 二、数据流全景：ModelRunner 在主链路中的位置

```
TokenizerManager (前端进程)
        │  TokenizedGenerateReqInput
        ▼
Scheduler (managers/scheduler.py) ──调度──► ScheduleBatch（CPU 侧高层调度数据）
        │                                       │
        │                                       │ ForwardBatch.init_new(batch, model_runner)
        ▼                                       ▼
TpModelWorker ──► ModelRunner.forward(ForwardBatch)
                        │
                        ├── can_run_graph? ──► CudaGraphRunner.replay()          [整图]
                        ├── piecewise can_run? ─► PiecewiseCudaGraphRunner.replay [分段]
                        └── else ──► self.model.forward(...)                     [eager]
                        │
                        ▼
                ModelRunnerOutput(logits_output, can_run_graph, expert_metrics, ...)
                        │
                        ▼
        ModelRunner.sample(logits_output, forward_batch) ──► next_token_ids
                        │
                        ▼
        Scheduler 回填 → DetokenizerManager → 客户端
```

关键约定：`ScheduleBatch`（CPU 为主）→ `ForwardBatch`（GPU 张量为主）的转换发生在 `ForwardBatch.init_new`（forward_batch_info.py:451），转换时需要传入 `model_runner` 来访问 device、LoRA manager、ngram 配置等——这就是两个文件耦合的根源，也是本文反复出现 `model_runner` 参数的原因。

另一个理解入口是**进程视角**：每个 scheduler 进程里通常有 1 个 target `ModelRunner` + 0..N 个 draft `ModelRunner`（投机解码时），它们共享同一 GPU、同一分布式进程组、同一 KV 池配置，但各自持有独立的权重与（部分独立的）CUDA Graph。

## 三、核心类与函数

### 3.1 模块级常量与辅助（L246-335）

| 名称 | 行号 | 作用 |
|---|---|---|
| `MLA_ATTENTION_BACKENDS` | L246-261 | 支持 MLA（DeepSeek 系）架构的 backend 白名单（aiter/flashinfer/fa3/fa4/triton/flashmla/cutedsl_mla/cutlass_mla/trtllm_mla/tokenspeed_mla/ascend/dsa 等，"nsa" 是 "dsa" 的废弃别名） |
| `CHUNKED_PREFIX_CACHE_SUPPORTED_ATTENTION_BACKENDS` | L263-272 | 支持 chunked prefix cache 的 backend 白名单 |
| `TORCH_DTYPE_TO_KV_CACHE_STR` | L274-279 | KV cache dtype 枚举到字符串映射（fp8_e4m3/fp8_e5m2/bf16） |
| `add_mla_attention_backend` | L282-284 | 运行时向 MLA 白名单注册自定义 backend 的插件口 |
| `add_chunked_prefix_cache_attention_backend` | L288-291 | 同上，chunked prefix cache 白名单 |
| `UNBALANCED_MODEL_LOADING_TIMEOUT_S = 480` | L297 | 多 rank 权重加载掉队时 `monitored_barrier` 的超时（秒） |
| `resolve_language_model()` | L305-313 | 从 VLM/omni 包装模型剥出语言主干；`Qwen3OmniMoeForConditionalGeneration` 特判取 `thinker.model`（L307-308），否则依次试 `.model` → `.language_model` → `.model` |
| `RankZeroFilter` | L316-326 | logging Filter：INFO 只放行 rank0，WARNING/ERROR 全放行（错误不能被静音） |
| `ModelRunnerOutput` | L329-335 | forward 返回值 dataclass（见下） |
| `_UNSET` 哨兵 | L302 | 惰性缓存判空用（`None` 是合法业务值时不能拿 None 当"未算"） |
| `LocalSerializedTensor` | L3562-3570 | 只序列化指针不搬数据的跨 rank 张量容器（权重热更新用） |

`ModelRunnerOutput` 四字段（L329-335）：

```python
@dataclass
class ModelRunnerOutput:
    logits_output: Union[LogitsProcessorOutput, PPProxyTensors]  # 前向输出（PP 中间 rank 时为代理张量）
    can_run_graph: bool                                          # 本次是否走了 graph replay
    expert_distribution_metrics: Optional[ExpertDistributionMetrics]  # EPLB 统计
    routed_experts_output: Optional[TopkCaptureOutput]           # routed experts 捕获（调试/RL）
    indexer_topk_output: Optional[TopkCaptureOutput]             # NSA/DSA indexer topk 捕获
```

`can_run_graph` 之所以要透传：采样侧与上层要据此决定能否复用 graph 的静态 logits 缓冲、`next_token_logits` 的切片语义。

### 3.2 `__init__` 初始化链（L341-579）

构造函数接收 18 个参数（L341-362）：并行拓扑全套（`tp_rank/tp_size`、`moe_ep_rank/moe_ep_size`、`pp_rank/pp_size`、`dp_rank`、`attn_cp_rank`、`moe_dp_rank`）、`mem_fraction_static`、`gpu_id`、`nccl_port`、`server_args`、`is_draft_worker`，以及三个"注入型"参数——`req_to_token_pool`、`token_to_kv_pool_allocator`、`memory_pool_config`。**draft worker（投机解码草稿模型）直接复用 target worker 已解析好的内存池与池对象**，替代了旧的 `server_args._draft_pool_config` 突变 hack（L365-368 注释明确记录了这个迁移：*"replaces legacy `server_args._draft_pool_config` mutation hack"*）。

完整初始化链（引用行号）：

```
① 参数解析与派生标志                     L363-499
② model_specific_adjustment()           L506
③ set_global_server_args_for_scheduler  L509
④ pre_model_load_memory = init_torch_distributed()   L520
⑤ init_shared_mooncake_transfer_engine  L523
⑥ self.forward_stream = ...Stream()     L526
⑦ offloader / WeightChecker / slow_rank_detector / mindspore / deep_gemm   L529-541
⑧ self.initialize(pre_model_load_memory)            L549
⑨ check_quantized_moe_compatibility()               L550
⑩ elastic EP rejoin / 多模态校验 / support_pp 探测  L552-575
⑪ _model_update_group / _weights_send_group 字典    L578-579
```

①中的派生标志值得逐一记住（后续所有路径都在读它们）：

- `self.spec_algorithm`（L393-395）：从 `--speculative-algorithm` 解析，决定 eagle/dflash/ngram 分支；
- `self.use_mla_backend`（L403）：`attention_arch == MLA`，反向 hack 进全局 server_args（L512-513 注释自嘲 *"FIXME: hacky"*）；
- `self.model_is_mrope`（L405-410）：rope 配置含 `mrope_section` 即为真（Qwen2-VL 系三维 RoPE）；
- `self.is_hybrid_swa` / `is_hybrid_swa_compress`（L399-402）：混合滑动窗口注意力（双池）标志；
- **eagle3 草稿配置预读**（L430-453）：target worker 提前读 draft 模型的 `eagle_config`，确定 aux hidden state 捕获层 `eagle_aux_hidden_state_layer_ids`；
- **dflash 草稿配置预读**（L455-499）：读 `parse_dflash_draft_config`，`resolve_target_layer_ids` 在训练层数与运行时层数不一致时按运行时目标模型选层并告警（L483-492）。

④ `init_torch_distributed`（L1042-1189）要点：

- **只有 target worker 初始化分布式环境**（`if not self.is_draft_worker`，L1097）——draft 与 target 同进程同 GPU，共享进程组；
- CPU 设备的 AMX/ARM 特化：`sgl_kernel.init_cpu_threads_env` 绑核 + 共享内存 AllReduce（`LOCAL_SIZE` env，L1098-1114）；
- `init_distributed_environment`（L1117-1126）→ `initialize_model_parallel`（L1127-1137）**一次声明六种并行**：tensor / attention-data / pipeline / expert / attention-context / moe-data，外加 `duplicate_tp_group`（pdmux）与 symm mem 开关；
- `initialize_dp_attention`（L1138-1141）：DP attention 的独立通信域；
- backend 特例：elastic EP 用 mooncake 时切 `"mooncake"` backend 并配 IB 设备过滤（L1055-1073）；
- **NCCL 预热**（L1147-1162）：`--pre-warm-nccl`（AMD 默认开）时做一次小 all_reduce，消除首请求冷启动；
- **TP 显存均衡检查**（L1175-1183）：任一 rank 加载前可用显存 < 本地最低值×0.9 时告警（`SGLANG_ENABLE_TP_MEMORY_INBALANCE_CHECK` 下报错）——防止某卡被别的进程占着导致 KV 池推导失真；
- 返回 `pre_model_load_memory`（L1164-1169，分布式平均），这是后面内存池推导的第一个输入。

⑩ `support_pp` 探测（L568-570）用签名反射而非模型白名单：

```python
self.support_pp = (
    "pp_proxy_tensors" in inspect.signature(self.model.forward).parameters
)
```

模型声明了自己能收 `pp_proxy_tensors` 参数即视为支持流水线并行；`pp_size > 1` 时断言成立（L572-575）。

### 3.3 `initialize()`：加载→内存池→backend→CUDA Graph 的总编排（L610-829）

这是初始化链的"主干函数"，其调用顺序就是四大子系统的诞生顺序：

```
memory_saver_adapter                          L613   （torch memory saver 适配）
remote instance transfer engine               L617
expert location metadata + 分布记录器          L620-639   （EPLB 前置，draft worker 跳过）
EPLBManager / ExpertLocationUpdater           L642-647
self.sampler = create_sampler()               L652   （注意：sampler 先于模型创建）
self.load_model()                             L653   （见 3.4）
self._prepare_moe_topk()                      L654   （见 3.14）
remote instance 权重信息注册                   L666-680
层归属计算 start_layer/end_layer/num_effective_layers   L685-707
torchao 量化 / torch TP                        L718-729
init_lora_manager + LoRA CUDA graph MoE 缓冲  L731-740
enable_deterministic_inference → batch invariant 模式  L742-746
configure_kv_cache_dtype()                    L749
init_memory_pool(pre_model_load_memory)       L752   （mixin，见 3.5）
maybe_init_ngram_embedding()                  L755
init_routed_experts_capturer / init_indexer_capturer  L758-760
init_aux_hidden_state_capture()               L765   （必须先于 graph capture）
── 设备分支 L767-821 ──
forward_hooks 注册                            L823-824
init_piecewise_cuda_graphs()                  L827
prealloc_symmetric_memory_pool()              L829
```

设备分支原文（L767-821）值得细读，因为不同设备的初始化配方不同：

```python
if self.device == "cuda" or self.device == "musa":
    self.init_cublas()                    # 小 matmul 触发 cublas 初始化，防后续报错
    if self.enable_hisparse: ...          # HiSparseCoordinator（稀疏 KV 备份协调器）
    self.init_attention_backend()
    self.kernel_warmup()                  # FlashInfer autotune
    self._pre_initialize_flashinfer_allreduce_workspace()  # 必须先于 graph capture
    self.init_device_graphs()
elif self.device == "cpu":
    self.init_attention_backend(); self.init_device_graphs()
elif self.device == "npu":
    self.init_attention_backend()
    ... lazy_init_zbal_gva_mem ...        # zbal 显存惰性初始化（mix 模式 graph capture 前）
    self.init_device_graphs()
elif current_platform.is_out_of_tree():
    self.init_attention_backend()
    if current_platform.support_cuda_graph(): self.init_device_graphs()
    else: self.graph_runner = None; self.graph_mem_usage = 0
else:
    self.graph_runner = None; self.init_attention_backend()
```

两个"顺序敏感"注释（必须遵守，违反即 bug）：

- aux hidden 捕获配置必须在 CUDA Graph 捕获前生效（L762-765、L899-903），否则捕获出的 graph 缺少 eagle3/dflash 需要的隐藏态输出路径；
- LoRA MoE 缓冲必须在 `init_memory_pool` 前预分配（L735-740），否则内存 profiling 看不到这块开销、KV cache 会被算大。两阶段中 Phase 2（dense LoRA batch metadata）延迟到 `CudaGraphRunner.__init__` 里做，因为需要捕获期参数（max_bs、num_tokens_per_bs）。

### 3.4 `load_model()`（L1236-1443）

逐步走读：

1. **加载前采样**（L1238）：`get_available_gpu_memory` 记录基准；
2. **线程与算力适配**（L1244-1256）：`torch.set_num_threads(1)` 减少加载争抢；sm80 以下自动降级 float16（无 bf16 支持），sm75 以下直接 `RuntimeError`（L1254）；`set_cuda_arch()` 设置 JIT 编译目标架构；
3. **组装 LoadConfig**（L1259-1285）：包含 ModelOpt 量化配置与 remote instance 权重分发全套参数（seed instance IP、发送端口组、transfer engine 会话、ModelExpress URL 等）；
4. **remote instance NCCL 分发线程**（L1291-1307）：seed 实例的 tp_rank 0 起后台线程向目标实例发起发送组初始化；
5. **权重落 GPU**（L1311-1331）：`monkey_patch_vllm_parallel_state()`（L1311）临时打补丁兼容从 vllm 移植的量化代码；真正加载发生在 `memory_saver_adapter.region(GPU_MEMORY_TYPE_WEIGHTS, enable_cpu_backup=...)` 上下文中（L1316-1327）——配合 torch memory saver，权重区显存可被整体换出（CPU backup / PD 分离场景）；
6. **后处理**（L1332-1425）：NPU `empty_cache`；offloader `post_init`；NVTX 分层打点注册（L1342-1344）；fp8 KV cache scaling factor 加载（有 `load_kv_cache_scales` 方法的模型才支持，L1346-1367）；`sliding_window_size` 三来源推断（模型方法 > hybrid swa config > attention_chunk_size，L1370-1383）；tensor dump forward hook（L1401-1417）；`reserve_rope_cache_for_long_sequences`（L1419-1425，在 graph capture 前预扩 RoPE cache 防长序列越界）；
7. **加载完成同步**（L1427-1443）：`dist.monitored_barrier(timeout=480s, wait_all_ranks=True)`——任何 rank 加载失败/超时，其它 rank 都得到明确报错而不是无限挂起；mooncake backend 不支持 monitored_barrier，退化为普通 barrier（L1427-1429）。

### 3.5 KV cache 管理：`ModelRunnerKVCacheMixin`

实现在 `model_runner_kv_cache_mixin.py`（968 行），`ModelRunner(ModelRunnerKVCacheMixin)` 继承（L338）。主入口 `init_memory_pool`（mixin L953-968）：

```
init_memory_pool(pre_model_load_memory)
  ├─ draft worker：断言外部传入 memory_pool_config（复用 target 的解析结果）
  └─ target worker：_resolve_memory_pool_config (mixin L926-951)
       ├─ _profile_available_bytes (L62-76)
       │    rest = 加载后可用显存 − pre_model_load_memory × (1 − mem_fraction_static)
       │    mambaish 模型再走 handle_max_mamba_cache (L78+) 扣除 state cache
       ├─ create_memory_pool_configurator(...).calculate_pool_sizes(bytes, page_size)
       ├─ _apply_token_constraints：用户 --max-total-tokens 上限、page 对齐、PP 同步 (L832-859)
       └─ _resolve_max_num_reqs → max_running_requests (L861-893)
  └─ _apply_memory_pool_config (L895-924)
       写回 max_total_num_tokens / max_running_requests
       hybrid SWA 双池：full_max_total_num_tokens + swa_max_total_num_tokens (L899-901)
       DeepSeek-V4 压缩注意力四池：c4/c128 token 池 + state 池（draft 全部清零，L903-915）
       → _init_pools (L281+)：真正 new 出 ReqToTokenPool / token_to_kv_pool_allocator
```

容量推导的核心公式（mixin L62-76）：

```python
post_model_load_memory = get_available_gpu_memory(...)      # 权重加载后
rest_memory = post_model_load_memory - pre_model_load_memory * (1 - self.mem_fraction_static)
return int(rest_memory * (1 << 30))                          # KV 池可用字节数
```

即：`mem_fraction_static` 定义"加载前总显存中留给（权重+KV+运行时）的比例"，扣除权重与运行时保留后余量全给 KV。要点：

- **容量推导是"两次采样 profiling"**而非试运行——用加载前/后两个可用显存点反推，启动快且不依赖 dummy batch 形状；
- **draft worker 不重复推导**（`memory_pool_config` 由 target 在 `__init__` L360-368 传入）；
- hybrid SWA 与 DSV4 这类"一模型多池"的架构在 `MemoryPoolConfig`（pool_configurator.py）统一表达；`_validate_prefill_only_disable_kv_cache_pool_family`（mixin L243+）处理 prefill-only 服务的池族裁剪。

### 3.6 attention backend 选择（L2243-2317）

三级决策：

**第一级 `init_attention_backend`（L2243-2254）**按部署形态分叉：

```python
if self.server_args.enable_pdmux:                     # PD 复用同一 GPU
    self.attn_backend = self._get_attention_backend(init_new_workspace=True)
    self.decode_attn_backend_group = [
        self._get_attention_backend() for _ in range(self.server_args.sm_group_num)]
    self.decode_attn_backend = self.decode_attn_backend_group[0]
elif self.server_args.enable_two_batch_overlap and not self.is_draft_worker:
    self.attn_backend = TboAttnBackend.init_new(self._get_attention_backend)
else:
    self.attn_backend = self._get_attention_backend()
```

运行期 pdmux 用 `update_decode_attn_backend(stream_idx)`（L3005-3006）在 per-stream backend 组里切换。

**第二级 `_get_attention_backend`（L2256-2308）**：

- draft worker 可用 `--speculative-draft-attention-backend` 强制覆盖（L2258-2266）；
- `server_args.get_attention_backends()` 拆出 prefill/decode 两个名字，**若不同则构造 `HybridAttnBackend`**（prefill 用 fa3、decode 用 flashinfer 这类混搭，L2273-2297，日志明示 experimental）；
- 相同则单一 backend。选中后把拆分结果写回全局 server_args（L2304-2307）。

**第三级 `_get_attention_backend_from_str`（L2310-2317）**：查 `ATTENTION_BACKENDS` 注册表（attention_registry.py）实例化，再经 `attn_backend_wrapper(self, backend)` 包装——wrapper 统一注入 model_runner 引用，使各 backend 能读内存池、server_args。

选完后的预热三件套：

- `kernel_warmup`（L2319-2328）：目前只做 FlashInfer autotune；`_should_run_flashinfer_autotune`（L2351-2389）排除 cutedsl+deepep 组合（会触发 DeepEP dispatch 断言）与 sm90 以下；
- `_flashinfer_autotune`（L2391-2419）：在 forward_stream 上（避免 NCCL 2.29+ symm mem 的 default-stream 限制）跑 `_dummy_run`；缓存 key = sha256(模型路径|dtype|量化|moe backend|tp|pp|dp|ep|hf_config 类名)（L2421-2455），按 rank 落盘 `~/.cache/sglang/flashinfer/autotune/...`；
- `_pre_initialize_flashinfer_allreduce_workspace`（L2330-2349）：graph capture 前建好 allreduce fusion 工作区，避免 capture 中的集合通信与 `custom_all_reduce.register_graph_buffers` 死锁。

### 3.7 CUDA Graph 协同（L2778-2962）

两套 graph runner 并存，服务不同模式：

**① `init_device_graphs`（整图 graph，L2778-2828）**——捕获 decode（及 target_verify/idle）小 batch 全模型 forward：

- 跳过条件：非生成模型（embedding 模型没有 decode，L2783-285）、mindspore（L2787）、`disable_cuda_graph`（L2790）；CPU 设备仅 torch compile 时捕获（L2793-2794）；
- 平台分派（L2810-2821）：out-of-tree 平台用 `current_platform.get_graph_runner_cls()`；否则 defaultdict 映射 `cuda/musa→CudaGraphRunner`、`cpu→CPUGraphRunner`、`npu→NPUGraphRunner`；
- 前后显存采样得到 `graph_mem_usage`（L2823-2824），日志输出捕获耗时与占用。

**② `init_piecewise_cuda_graphs`（分段 graph，L2830-2962）**——把 prefill 按层分段捕获（attention eager、MoE/MLP 进 graph）：

- draft worker 默认跳过，由 eagle worker 在 `init_lm_head` 后显式回调（`force_for_draft_worker=True`，L2840-2844）——否则 graph 捕到的是未 final 的 embedding 权重；
- 关闭条件逐条检查（L2834-2858）：`--disable-piecewise-cuda-graph`、非语言模型（无 `.model`）、`piecewise_cuda_graph_tokens` 未设；
- **层清单采集**（L2860-2935）：先 `resolve_language_model` 剥主干（L2861），再遍历 `layer_model.layers`，按属性名兼容各种模型族：

```python
if hasattr(layer, "self_attn"):        # 标准 transformer / DeepSeek(attn_mqa)
    attn_layer = layer.self_attn.attn or layer.self_attn.attn_mqa
elif hasattr(layer, "attn"):           # hybrid 模型
elif hasattr(layer, "linear_attn"):    # GDN/线性注意力
elif hasattr(layer, "attention"):      # InternVL
elif hasattr(layer, "mixer"):          # NemotronH / Mamba(带 _forward_mamba 的存 layer 本身)
```

  产出四个平行列表 `attention_layers / moe_layers / moe_fusions / dsa_indexers`（mlp.experts / block_sparse_moe.experts / moe.experts / mixer.experts 四种 MoE 挂载点全兼容）；
- 层数不齐（非标准 GQA）则放弃（L2937-2943）；`enable_breakable_cuda_graph` 时用实验性 `BreakableCudaGraphRunner`（L2951-2955）。

运行期优先级：整图 graph 优先（decode 路径，`_forward_raw` L3301-3308），未命中再看 piecewise（extend 路径，`forward_extend` L3086-3101）。

### 3.8 forward 全模式执行（L3008-3369）

**入口 `forward`（L3183-3261）**——对外统一入口，负责"编排壳"：

- `forward_pass_id += 1`（L3191）——专家分布记录器的步编号；
- 可选 msprobe 精度调试器 start/stop（L3194-3198, 3254-3256）；
- profiler step span：`_build_step_span_name`（L3552-3559）生成形如 `step[EXTEND bs=8 toks=4096]` / `step[DECODE bs=32]` 的 trace 名；
- 全局专家分布记录器包裹本次 forward（L3206-3212），产出 `expert_distribution_metrics` 回填 `ModelRunnerOutput`（L3229）；
- 调 `_forward_raw`；elastic EP 场景若检测 rank 故障集合变化 → `_maybe_rebalance_after_rank_fault`（L3220-3228，实现 L3510-3537）：跑完 EPLB `rebalance()` 生成器后**重跑一次 `_forward_raw`**；
- routed experts / indexer topk 捕获器回调（L3232-3246，`no_copy_to_cpu` 由 overlap schedule 决定）；EPLB manager 收尾（L3248-3249）；dumper.step（L3251-3252）；`maybe_recover_ep_ranks`（L3258-3259）。

**核心 `_forward_raw`（L3263-3369）**——真正的执行决策：

```python
# ① forward_context 发布（L3274-3277）
if has_forward_context():                 # 外层已发布（spec worker 按步包了第 i 个子 backend）
    ctx_mgr = contextlib.nullcontext()
else:
    ctx_mgr = forward_context(ForwardContext(attn_backend=self.attn_backend))
with ctx_mgr:
    # ② can_run_graph 判定（L3279-3288）
    mode_check = (forward_batch.forward_mode.is_cpu_graph() if self.device == "cpu"
                  else forward_batch.forward_mode.is_cuda_graph())
    can_run_graph = bool(mode_check() and self.graph_runner
                         and self.graph_runner.can_run(forward_batch))
    ...
    # ⑤ 整图 graph 路径（L3301-3308）
    if can_run_graph:
        ret = self.graph_runner.replay(forward_batch, ...)
        return ModelRunnerOutput(logits_output=ret, can_run_graph=True)
    # ⑥ eager 路径前置同步
    if forward_batch.global_num_tokens_cpu is not None:
        forward_batch.prepare_mlp_sync_batch(self)       # DP attention 填充
    else:
        forward_batch.prepare_attn_tp_scatter_input(self)
    # CP 豁免的 num_token_non_padded 本地化（L3316-3331）
    ...
    # ⑦ 模式分发（L3337-3361）
    if   forward_batch.forward_mode.is_decode():            ret = self.forward_decode(...)
    elif forward_batch.forward_mode.is_split_prefill():     ret = self.forward_split_prefill(...)
    elif forward_batch.forward_mode.is_extend(v2 含):       ret, can = self.forward_extend(...)
    elif forward_batch.forward_mode.is_idle():              ret = self.forward_idle(...)
    else:                                                   raise ValueError
    # ⑧ PP 最后 rank 截断 padding logits（L3363-3367）
    if forward_batch.global_num_tokens_cpu is not None and self.pp_group.is_last_rank:
        forward_batch.post_forward_mlp_sync_batch(ret)
```

④⑤ 之间还有两处前置：hisparse decode 前的 `wait_for_pending_backup` + `num_real_reqs` 回填（L3291-3296）；hybrid SWA 的 `token_to_kv_pool.invalidate_loc_cache()`（L3298-3299，防止上一批的槽位缓存误用）。

**四个模式方法**逐一看：

| 方法 | 行号 | 要点 |
|---|---|---|
| `forward_decode` | L3008-3055 | `model.prepare_forward_batch` 钩子（Moss-VL 等模型的 cross-attn mask 预处理）；pdmux 时用 per-stream decode backend 并**在 ForwardContext 里覆盖发布**（L3021-3026, 3050-3054）；否则 `attn_backend.init_forward_metadata(forward_batch)`；`device_timer` 按 category=decode 计时 |
| `forward_extend` | L3057-3123 | 先组装 kwargs：`input_embeds`（转 bfloat16）、`replace_embeds/replace_positions`（token 级 embedding 覆写：先查 base embedding 再 scatter 替换，L3069-3081）、embedding 模型加 `get_embedding=True`；**先试 piecewise graph**（L3086-3101）；否则 init_forward_metadata + eager forward；返回 `(ret, can_run_graph)` |
| `forward_idle` | L3125-3154 | DP attention 下本 rank 无请求时的空转；`batch_size>0`（被 MLP sync pad 过）仍要 init_forward_metadata；`==0` 时**显式清空 `attn_backend.forward_metadata=None`**——防止上个 batch 的 req_pool 索引残留触发 SWA mapping use-after-free（L3128-3138 注释详述） |
| `forward_split_prefill` | L3156-3181 | PD 复用的分段 prefill：`split_index==0 或 reinit_attn_backend` 时重建元数据（L3162-3163）；每次只跑 `[split_index, min(+forward_count, num_hidden_layers))` 层区间（`model.forward_split_prefill` L3174-3179），推进 `forward_batch.split_index` |

`forward_decode/extend` 都有 `skip_attn_backend_init` 参数：CUDA Graph replay 路径或上层（如 TBO）已建好元数据时跳过重复构建。

### 3.9 `sample()` 与 logits 后处理（L3371-3451）

`_preprocess_logits`（L3371-3386）三步：

```python
sampling_info.update_regex_vocab_mask()                 # 生成 grammar 约束的词表掩码
sampling_info.apply_logits_bias(logits_output.next_token_logits)
sampling_info.vocab_mask = None    # 立刻释放！
```

L3381-3385 的注释解释了为什么第三步不可省：overlap 调度下 `delay_sample_func` 闭包与 `batch_record_buf` 会把 sampling_info（连同 vocab_mask）拖到下一轮迭代，结构性输出场景会造成**稳定的 VRAM 泄漏**。

`sample`（L3388-3419）核心调用：

```python
next_token_ids = self.sampler(
    logits_output,
    forward_batch.sampling_info,
    forward_batch.return_logprob,
    forward_batch.top_logprobs_nums,
    forward_batch.token_ids_logprobs,
    forward_batch.positions if forward_batch.forward_mode.is_decode()
                             else forward_batch.seq_lens - 1,   # prefill 只采末 token
)
self.maybe_update_ngram_token_table(next_token_ids, forward_batch)   # LongCat n-gram 表回填
```

注意采样位置的分支：decode 每请求一个 token，位置就是 `positions`；extend（prefill）只对每序列最后一个 token 采样，位置用 `seq_lens - 1`（L3411-3416）。

`compute_logprobs_only`（L3421-3451）：prefill-only 请求只要 `token_ids_logprobs` 不要生成时的省采样快路径，直接委托 `sampler.compute_logprobs_only`。

### 3.10 权重更新家族（在线学习/多实例协同）

| 方法 | 行号 | 场景 |
|---|---|---|
| `update_weights_from_disk` | L1598-1670 | 磁盘热更；`weight_name_filter` 支持只更部分权重；失败自动回滚重载（L1644-1652）；`recapture_cuda_graph` 时重建 graph（L1659-1667） |
| `init_weights_send_group_for_remote_instance` | L1672-1719 | 多实例权重分发：按 tp_rank 从端口列表选自己的端口建 custom process group |
| `send_weights_to_remote_instance` | L1721-1767 | 组内逐参数 broadcast 全部 named_parameters，发完销毁组 |
| `init_weights_update_group` / `destroy_weights_update_group` | L1769-1826 | RLHF：训练引擎（group rank0 = actor）与推理引擎建组；docstring（L1778-1787）讲清了角色分工 |
| `update_weights_from_distributed` | L1828-1885 | 按 (name, dtype, shape) 广播收权重 → `model.load_weights`；async_op 批量句柄并发收（L1862-1873） |
| `_update_bucketed_weights_from_distributed` | L1887-1916 | `flattened_bucket` 格式：一整条扁平张量 + 元数据重建（`FlattenedTensorBucket`） |
| `update_weights_from_tensor` | L1918-1947 | 直接吃张量列表；`load_format` 分 `direct`（`_model_load_weights_direct` L3540-3543）/ 自定义 loader（`dynamic_import`）/ 默认 `model.load_weights`；`LocalSerializedTensor` 按 rank 解包（L3546-3549） |
| `_update_weights_from_flattened_bucket` | L1949-1979 | 桶化张量的本地重建版本 |
| `get_weights_by_name` | L1981-1996 | 测试用按名取参（未优化性能，注释明示） |
| `update_expert_location` | L1496-1536 | EPLB 重平衡后同步专家位置；缺失逻辑专家按 `generate_weight_name_filter` 过滤**只补缺失权重**，否则全量重载 |
| `update_weights_from_ipc` / `save_remote_model` / `save_sharded_model` / `check_weights` | L3453-3487 | checkpoint engine IPC / `RemoteModelLoader.save_model` / `ShardedStateLoader.save_model` / `WeightChecker.handle` |

失败语义统一：权重族操作返回 `(bool, message)` 二元组，部分更新失败时提示"discard the whole weights"（L1878-1885）——宁可再生不可用半新半旧状态。

### 3.11 LoRA（L1998-2084）

- `init_lora_manager`（L1998-2012）：构造 `LoRAManager`（base 模型、max_loras_per_batch、lora_backend、target_modules 等全套配置）；
- `_init_lora_cuda_graph_moe_buffers`（L2014-2040）：两阶段初始化的 Phase 1——**所有 MoE LoRA 层共享一组缓冲**（顺序执行无需每层一份），在内存池推导前预分配；Phase 2 在 `CudaGraphRunner.__init__` 里调 `lora_manager.init_cuda_graph_batch_info()`（需捕获期参数）；
- `load_lora_adapter` / `load_lora_adapter_from_tensors` / `unload_lora_adapter`（L2042-2084）：动态加载/卸载，前后打印可用显存。

### 3.12 模型族适配属性族（L2086-2186）

一组 `@property` 用 `isinstance(hf_config, ...)` 判定模型族，供 backend 选择与内存池推导消费：

| 属性 | 行号 | 命中模型族 |
|---|---|---|
| `qwen3_next_config` | L2086-2091 | `Qwen3NextConfig` |
| `hybrid_lightning_config` | L2093-2098 | `BailingHybridConfig` |
| `hybrid_gdn_config` | L2100-2113 | Qwen3Next/Qwen3.5(±MoE)/InternS2Preview/JetNemotron/JetVLM |
| `mamba2_config` | L2115-2146 | NemotronH（MTP draft 无 Mamba 层时返回 None，L2118-2123）/FalconH1/Lfm2(±MoE/VL)/GraniteMoeHybrid（无 mamba 层返回 None） |
| `kimi_linear_config` | L2156-2161 | `KimiLinearConfig` |
| `linear_attn_model_spec` / `mambaish_config` | L2163-2186 | 兜底查 `linear_attn_model_registry`；`mambaish` = 四个具体 config 任一命中或注册表命中 |
| `max_token_pool_size` | L2148-2154 | hybrid SWA 时返回 `full_max_total_num_tokens`（全注意力池），否则 `max_total_num_tokens` |

`_linear_attn_registry_cache` 用 `_UNSET` 哨兵做惰性缓存（L2163-2168）——`None` 是合法查询结果，不能当"未查"。

### 3.13 `_dummy_run` 详解（L2457-2732）

"假跑一次 forward"是连接四个子系统的枢纽函数（autotune、warmup、graph 捕获的前身）。流程：

1. **选捕获形态**（L2459-2477）：生成模型用 `ForwardMode.DECODE`，embedding 模型用 `EXTEND`；spec 场景 target 用 `TARGET_VERIFY` 且 `num_tokens_per_bs = get_num_tokens_per_bs_for_target_verify(...)`（draft token 数相关）；`enable_return_hidden_states` 时 capture_hidden_mode 升到 FULL；
2. **MLP sync 对齐**（L2481-2486）：warmup 也要与调度期的 padding 规则对齐——`require_mlp_sync` 时 num_tokens 对齐 `attn_tp_size`；
3. **torch compile 预检**（L2490-2501）：模型声明 `_can_torch_compile=False`（如动态 rope scaling）则自动关闭 compile 并告警；
4. **构造静态输入**（L2510-2530）：`DecodeInputBuffers.create(...)` 一次性建齐 graph 级静态缓冲（input_ids/positions/seq_lens/out_cache_loc/req_pool_indices/next_token_logits_buffer/mrope/global_num_tokens 等，含 PP 代理张量与 encoder-decoder 填充值）；
5. **extend 形态补充**（L2534-2553）：非生成模型手工造 `extend_seq_lens=seq_len_fill_value`、`extend_prefix_lens=0`、`extend_start_loc=arange`；
6. **DP gather 场景的 global_num_tokens 填充**（L2560-2593）：mlp_tp_gather 填 `dp_size` 份、attn_tp_gather 填 1 份，并设 `global_dp_buffer_len`；
7. **spec_info 哑件**（L2595-2648）：按算法构造 `EagleVerifyInput` / `DFlashVerifyInput` / `NgramVerifyInput`（custom_mask 直接用 buffers 里的静态张量；capture_hidden_mode 按角色定）；
8. **手工组装 ForwardBatch**（L2661-2692）：不走 `init_new`，直接传 30 余个字段——这份字段清单等于"graph 捕获所需的最小 ForwardBatch 集"；LoRA 场景补 `lora_ids=[None]*bs` 并 `prepare_lora_batch`；
9. **执行**（L2697-2732）：`attn_backend.init_forward_metadata(forward_batch)` 后，`run_once()` 在 `forward_context` + `torch.inference_mode()` + 可选 `run_ctx`（autotune 上下文）下跑 `model.forward`；前后 `synchronize` + `tp_group.barrier()` 保证各 rank 对齐。

### 3.14 elastic EP 与专家并行运维

- `_prepare_moe_topk`（L1445-1494）：给启用 DeepEP waterfill 的 `TopK/HashTopK` 模块注入 `DeepEPWaterfillBalancer`；EPLB 冗余专家要计入每 rank 专家数（L1471-1476 注释解释 static EPLB 重映射与 waterfill 槽位重映射的交互）；
- `update_expert_location`（L1496-1536）+ `maybe_recover_ep_ranks`（L1538-1577）：掉线恢复后重置 `forward_pass_id`、重播 expert location metadata、广播随机种子（保证恢复后采样连续性）；L1539-1543 的 TODO 记录了 `active_ranks.all()` 会触发 host-device 同步的已知性能税；
- `_get_healthy_expert_location_src_rank`（L1579-1596）：all_gather rejoin 标志后挑第一个健康 rank 做广播源；注释强调不能用 `elastic_ep_rejoin` 参数判断（rejoin rank 之后可能转为健康角色）；
- `_maybe_rebalance_after_rank_fault`（L3510-3537）：`ElasticEPStateManager.is_active_equal_last()` 检测故障集合变化 → snapshot/sync → EPLB `rebalance()` → **重跑 `_forward_raw`**；
- `init_routed_experts_capturer` / `init_indexer_capturer`（L853-897）：按 `max_total_num_tokens + page_size` 与 `max_running_requests` 预分配捕获缓冲；indexer 捕获是 CUDA-only（其它平台只告警不建，L876-883）；
- `maybe_init_ngram_embedding`（L2734-2754）与 `maybe_update_ngram_token_table`（L2756-2776）：LongCat n-gram 表的初始化（尺寸镜像 req_to_token 池）与采样后回写（JIT kernel `update_token_table`）。

## 四、与其他模块的交互

| 模块 | 方向 | 内容 |
|---|---|---|
| `managers/schedule_batch.py` | 入 | `ScheduleBatch`/`ModelWorkerBatch` 经 `ForwardBatch.init_new` 变成执行输入；`sanity_check_mm_pad_shift_value`（L133，多模态 pad 值校验） |
| `forward_batch_info.py` | 出入 | forward 各模式消费 `ForwardBatch`；`_dummy_run` 手工构造它；`PPProxyTensors` 是 PP 中间激活载体 |
| `layers/attention/attention_registry.py` | 入 | `ATTENTION_BACKENDS` 注册表 + `attn_backend_wrapper`；每步由 ModelRunner 驱动 `init_forward_metadata` |
| `layers/attention/hybrid_attn_backend.py` / `tbo_backend.py` | 入 | prefill/decode 异构混搭与 TBO 父子拆分 |
| `model_executor/forward_context.py` | 出 | `forward_context(ForwardContext(attn_backend=...))` 向模型层（RadixAttention）发布当前 backend；pdmux/spec 场景支持外部覆盖（`has_forward_context` 检查） |
| `cuda_graph_runner.py` / `piecewise_cuda_graph_runner.py` / `cpu_graph_runner.py` / NPU graph runner | 出 | `init_device_graphs`/`init_piecewise_cuda_graphs` 构造；`_forward_raw`/`forward_extend` 判定并 replay；`DecodeInputBuffers` 即 graph 静态输入缓冲 |
| `mem_cache/`（memory_pool/allocator） | 入 | mixin 创建 `ReqToTokenPool`、`BaseTokenToKVPoolAllocator`；hybrid SWA 的 `invalidate_loc_cache` 在 forward 前调用 |
| `layers/sampler.py` + `sampling/sampling_batch_info.py` | 出 | `create_sampler()`；`sample()` 消费 `SamplingBatchInfo` 的 grammar/bias |
| `model_loader/loader.py` | 入 | `get_model_loader`/`DefaultModelLoader`，全部 load format 的入口；`set_default_torch_dtype` 上下文 |
| `distributed/parallel_state.py` + `dp_attention.py` | 入 | 六种并行初始化；`get_tp_group`/`get_pp_group`/`get_attention_tp_group` 缓存为成员（L1170-1172） |
| `eplb/`、`elastic_ep/` | 入 | 专家位置元数据、分布记录、重平衡、掉卡恢复、专家备份客户端 |
| `speculative/`（eagle/dflash/ngram） | 入 | `spec_algorithm` 决定 dummy run/捕获配置；draft worker 通过参数注入复用 target 池 |
| `lora/lora_manager.py` | 入 | 动态适配器；`ForwardBatch.init_new` 末尾触发 `fetch_new_loras`（非 overlap 加载模式） |
| `server_args.py` | 入 | 全局单例 `set_global_server_args_for_scheduler`（L509）；`use_mla_backend` 反向 hack 回全局（L512-513） |
| `platforms/`（current_platform） | 入 | out-of-tree 后端初始化、graph runner 类选择、cache/sync 抽象 |
| 调试设施 | 入 | msprobe / dumper / NVTX PytHooks / tensor_dump_forward_hook / WeightChecker |

## 五、关键设计决策

1. **"执行器+Mixin"而非上帝类拆分**：KV cache 容量推导整体移入 `ModelRunnerKVCacheMixin`（自注释型 `self: ModelRunner` 类型标注），`model_runner.py` 保留编排主链。内存策略（hybrid SWA、DSV4 四池、mamba state）可独立演进，主文件不被池类型组合爆炸污染。
2. **顺序即正确性**：初始化链中多处顺序约束被注释"钉死"——LoRA MoE 缓冲必须先于 `init_memory_pool`（否则 KV 池算大）、aux hidden 捕获必须先于 graph capture（否则 graph 缺输出路径）、flashinfer allreduce workspace 必须先于 graph capture（否则死锁）。理解 `initialize()`（L610-829）的最佳方式是把它当一张依赖拓扑图读。
3. **draft worker 是"寄生"执行器**：不建进程组（L1097）、不推导内存池（注入 `memory_pool_config`）、共享 req_to_token_pool——投机解码的 target/draft 两个 ModelRunner 在同进程内以最小组内通信协作，这是 SGLang 投机解码吞吐优势的工程基础之一。
4. **forward 双层结构（编排壳+分发核）**：`forward` 只做横切关注点（profiling、专家统计、elastic EP、捕获器），`_forward_raw` 只做执行决策（graph vs eager、模式分发、DP 同步）。elastic EP 的"重平衡后重跑 forward"因此能干净地复用 `_forward_raw`（L3530）而不重复横切逻辑。
5. **backend 选择的注册表+包装器模式**：`ATTENTION_BACKENDS` 注册表 + `attn_backend_wrapper` + `HybridAttnBackend`（prefill/decode 可异构）+ `TboAttnBackend`（overlap 拆分）+ pdmux per-stream backend 组，四种组合正交叠加；`forward_context` 运行期发布机制让模型层永远拿到"当前生效"的 backend，解耦多 backend 并存与模型代码。
6. **graph 优先级明确且两套并存**：decode 类走整图 `CudaGraphRunner`（`_forward_raw` 早期返回，L3301-3308），extend 走 `PiecewiseCudaGraphRunner`（在 `forward_extend` 内部判定，L3086-3101）；`ModelRunnerOutput.can_run_graph` 把"是否走了 graph"透传给上层（采样侧据此决定能否复用静态 logits 缓冲）。
7. **资源观测内建**：所有大内存操作（权重加载、内存池、graph 捕获、LoRA 加载）前后都采样 `get_available_gpu_memory` 并打印耗时——启动日志本身就是一份显存审计报告；TP rank 间失衡还有主动检查（L1175-1183）与掉队 barrier（L1431-1443）。

## 六、阅读建议

1. **第一次读**：只读三个函数就能建立骨架——`__init__`（L341）→ `initialize`（L610）→ `_forward_raw`（L3263），其余全是这根主干的支线。带着"权重→内存池→backend→graph"四幕剧的预期读 `initialize`，每一行都在给下一幕铺路。
2. **配对阅读**：本文件必须与 `forward_batch_info.py`（ForwardBatch 字段语义）和 `cuda_graph_runner.py`（已有另篇）三角互证；`_dummy_run`（L2457）是三者的交汇点——它手工构造 ForwardBatch，等于一份"ForwardBatch 最小可用字段清单"。
3. **调试视角**：排查 OOM 时看启动日志三联（"Load weight end" L1393 / "Memory pool end" mixin L965 / "Capture cuda graph end" L2825 的 avail mem）；排查首 token 慢看 NCCL warmup（L1147）与 `monitored_barrier`（L1431）；排查 DP attention 数值问题优先怀疑 `prepare_mlp_sync_batch` 的 padding 与 `post_forward_mlp_sync_batch` 的截断是否配对。
4. **改代码时**：在 `initialize()` 中插入新初始化步骤前，先确认它是否依赖 graph capture 之后的产物，或是否影响内存 profiling 的两个采样点——本文件历史 bug 多数源于顺序破坏（注释里三处 FIXME/TODO 都与此相关）。新增 forward 模式时记得同时改 `ForwardMode` 谓词（forward_batch_info.py）与 `_forward_raw` 的分发链（L3337-3361）。
5. **跳读索引**：权重热更新看 §3.10 表格行号直取；新模型接入（hybrid/线性注意力）看属性族 L2086-2186 与 piecewise 层采集 L2860-2935 的属性名兼容表；投机解码接入看 L393-499（eagle3/dflash 配置预读）+ `_dummy_run` 的 spec_info 分支；PD 分离看 `forward_split_prefill`（L3156）与 mooncake 引擎初始化（L1191-1234）。

## 附录：方法级索引

**初始化族**：`__init__` L341 · `init_msprobe` L581 · `init_mindspore_runner` L596 · `initialize` L610 · `adjust_hybrid_swa_layers_for_pp` L831 · `init_routed_experts_capturer` L853 · `init_indexer_capturer` L872 · `init_aux_hidden_state_capture` L899 · `remote_instance_init_transfer_engine` L917 · `_register_to_engine_info_bootstrap` L937 · `model_specific_adjustment` L983 · `check_quantized_moe_compatibility` L1004 · `init_torch_distributed` L1042 · `init_shared_mooncake_transfer_engine` L1191 · `load_model` L1236 · `configure_kv_cache_dtype` L2188 · `init_cublas` L2234 · `init_attention_backend` L2243 · `kernel_warmup` L2319 · `init_device_graphs` L2778 · `init_piecewise_cuda_graphs` L2830 · `init_threads_binding` L2964 · `apply_torch_tp` L2998 · `prealloc_symmetric_memory_pool` L3489

**forward/采样族**：`update_decode_attn_backend` L3005 · `forward_decode` L3008 · `forward_extend` L3057 · `forward_idle` L3125 · `forward_split_prefill` L3156 · `forward` L3183 · `_forward_raw` L3263 · `_preprocess_logits` L3371 · `sample` L3388 · `compute_logprobs_only` L3421 · `_dummy_run` L2457

**权重族**：`_prepare_moe_topk` L1445 · `update_expert_location` L1496 · `maybe_recover_ep_ranks` L1538 · `_get_healthy_expert_location_src_rank` L1579 · `update_weights_from_disk` L1598 · `init_weights_send_group_for_remote_instance` L1672 · `send_weights_to_remote_instance` L1721 · `init_weights_update_group` L1769 · `destroy_weights_update_group` L1815 · `update_weights_from_distributed` L1828 · `_update_bucketed_weights_from_distributed` L1887 · `update_weights_from_tensor` L1918 · `_update_weights_from_flattened_bucket` L1949 · `get_weights_by_name` L1981 · `save_remote_model` L3453 · `save_sharded_model` L3459 · `check_weights` L3469 · `update_weights_from_ipc` L3472 · `_maybe_rebalance_after_rank_fault` L3510

**LoRA 族**：`init_lora_manager` L1998 · `_init_lora_cuda_graph_moe_buffers` L2014 · `load_lora_adapter` L2042 · `load_lora_adapter_from_tensors` L2059 · `unload_lora_adapter` L2069

**ngram/hisparse**：`maybe_init_ngram_embedding` L2734 · `maybe_update_ngram_token_table` L2756

**属性族**：`qwen3_next_config` L2086 · `hybrid_lightning_config` L2093 · `hybrid_gdn_config` L2100 · `mamba2_config` L2115 · `max_token_pool_size` L2148 · `kimi_linear_config` L2156 · `_get_linear_attn_registry_result` L2163 · `linear_attn_model_spec` L2170 · `mambaish_config` L2175

**模块级函数**：`resolve_language_model` L305 · `_model_load_weights_direct` L3540 · `_unwrap_tensor` L3546 · `_build_step_span_name` L3552 · `LocalSerializedTensor` L3562

**mixin（model_runner_kv_cache_mixin.py）**：`_profile_available_bytes` L62 · `handle_max_mamba_cache` L78 · `calculate_mla_kv_cache_dim` L182 · `_calculate_mamba_ratio` L229 · `_validate_prefill_only_disable_kv_cache_pool_family` L243 · `_init_pools` L281 · `_apply_token_constraints` L832 · `_resolve_max_num_reqs` L861 · `_apply_memory_pool_config` L895 · `_resolve_memory_pool_config` L926 · `init_memory_pool` L953
