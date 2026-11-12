# 深度解析：`python/sglang/srt/server_args.py`

> 源码: python/sglang/srt/server_args.py @ commit ec075d8bc

`server_args.py` 是 SGLang 全部启动配置的唯一权威定义处，实现了巨型 dataclass `ServerArgs`（约 300 个字段 + `__post_init__` 中 40 余个 `_handle_*` 归一化钩子）与 ZMQ 端口分配器 `PortArgs`。SGLang 是多进程 LLM 推理框架：TokenizerManager（主进程）、Scheduler（每 TP rank 一个子进程）、DetokenizerManager（子进程）经 ZMQ IPC 通信，而三方的拓扑结构（TP/PP/DP/EP/CP 怎么切、用哪些 kernel backend、开不开投机解码）全部由这份文件推导、校验并广播。它同时是 CLI 入口（`sglang.launch_server` → `prepare_server_args`）与 Python API 入口（`Engine(**kwargs)` 直接构造 `ServerArgs`）的交汇点，堪称"SGLang 能力面的总目录"——想知道 SGLang 支持什么，通读这一个文件的字段注释就够了。文件长 7879 行，其中约 2700 行是 `add_cli_args` 的 argparse 声明，与 dataclass 字段一一镜像。

---

## 一、文件总览与阅读地图

| 行区间 | 内容 |
|---|---|
| L1–88 | imports（environ、utils.common 中大量硬件探测函数、LoRARef 等） |
| L90–287 | 模块级常量：各 backend 的合法取值清单（`QUANTIZATION_CHOICES`、`ATTENTION_BACKEND_CHOICES`…） |
| L290–339 | `add_*_choices()` 系列插件扩展函数 |
| L342–861 | `ServerArgs` dataclass 字段定义（按功能分组注释） |
| L862–1014 | `__post_init__`：按严格顺序调度 40+ 个 `_handle_*` |
| L1016–4295 | 各 `_handle_*` 实现（内存启发式、模型特判、backend 兼容性、并行约束…） |
| L4296–7001 | `add_cli_args`：argparse 镜像（与字段分组一一对应） |
| L7002–7131 | `from_cli_args` 与只读属性（`url`/`use_mla_backend`…） |
| L7133–7678 | `check_server_args` / `check_lora_server_args` / 杂项校验与属性 |
| L7681–7697 | 全局单例机制 `_global_server_args` |
| L7700–7734 | `prepare_server_args`（CLI 总入口） |
| L7741–7841 | `PortArgs`（ZMQ IPC/TCP 端点分配） |
| L7844–7879 | `auto_choose_speculative_params`（投机解码默认超参） |

---

## 二、核心类与函数

### 2.1 模块级常量（L90–287）：能力面的"硬目录"

每个 `*_CHOICES` 列表都是一个可插拔维度的合法值域：

- `LOAD_FORMAT_CHOICES`（L103）：`auto/pt/safetensors/npcache/dummy/sharded_state/gguf/bitsandbytes/mistral/layered/flash_rl/remote/remote_instance/fastsafetensors/private/runai_streamer` —— 权重加载格式 17 种。
- `QUANTIZATION_CHOICES`（L122）：`awq/fp8/mxfp8/gptq/marlin/.../mlx_q4/mlx_q8/unquant` 近 30 种量化方案，覆盖 NVIDIA/AMD/NPU/Apple MLX。
- `ATTENTION_BACKEND_CHOICES`（L157）：通用（`triton/torch_native/flex_attention/dsa/dsv4`）+ NVIDIA（`fa3/fa4/flashinfer/flashmla/trtllm_mla/cutedsl_mla/tokenspeed_mla/trtllm_mha`...）+ AMD（`aiter/wave`）+ 其他平台（`intel_amx/ascend/intel_xpu`）。
- `MOE_RUNNER_BACKEND_CHOICES`（L208）与 `MOE_A2A_BACKEND_CHOICES`（L223）：MoE 计算 kernel 与 all-to-all 通信两维度正交（`deepep/mooncake/nixl/mori/ascend_fuseep/flashinfer/megamoe`）。
- `MIS_DELIMITER_TOKEN_ID = 9999`（L206）：Multi-Item Scoring 的占位 token。
- 别名处理：`nsa` 是 `dsa` 的弃用别名（L163）、`compressed` 是 `dsv4` 的弃用别名（L165）。

`add_load_format_choices()` 等 13 个函数（L290–339）允许外部插件（`sglang.srt.plugins.load_plugins` 加载的 OOT 包）向这些清单追加条目——这是"能力目录"的开放扩展点。

### 2.2 `ServerArgs` 字段：按参数分组解析（L342–861）

dataclass 的注释分组即 SGLang 的能力地图（注释同时要求字段顺序与 `add_cli_args` 严格一致，见 L347-350）。下面按十五个功能组逐一拆解。

#### ① 模型与 tokenizer（L353–370）

| 字段 | 默认 | 说明 |
|---|---|---|
| `model_path` | （必填） | 本地目录或 HF repo id，也接受 runai 对象存储 URI / remote URL |
| `tokenizer_path` | None→model_path | 独立 tokenizer 目录（ModelScope/镜像站场景） |
| `tokenizer_mode/backend` | auto / huggingface | `auto/slow/mistral`；backend 可选 `huggingface/rust` |
| `tokenizer_worker_num` / `detokenizer_worker_num` | 1 / 1 | 多 tokenizer 路由 / 多 detokenizer worker（见 engine.py ②） |
| `skip_tokenizer_init` | False | 纯 input_ids 服务（vLLM 兼容模式） |
| `load_format` | auto | 17 种权重格式（见 2.1） |
| `context_length` | None | 覆盖模型 config 的最大上下文 |
| `is_embedding` | False | embedding / rerank 服务器模式 |
| `prefill_only_disable_kv_cache` | False | embedding 场景彻底跳过 KV pool（fa_skip_kv_cache 路径） |
| `enable_multimodal` | None | VLM 开关（None 则按模型 config 自动判） |
| `model_impl` | auto | 可选 `mindspore`（NPU） |
| `model_config_parser` | auto | 模型 config 解析器选择 |

#### ② HTTP server 与安全（L372–388）

- `host="127.0.0.1"`、`port=30000`、`fastapi_root_path`（挂反代子路径）、`grpc_mode`（原生 gRPC 服务，端口默认 `port+10000`）。
- `skip_server_warmup` / `warmups`（自定义预热任务列表）。
- SSL 四件套 `ssl_keyfile/ssl_certfile/ssl_ca_certs/ssl_keyfile_password` + `enable_ssl_refresh`（证书热轮换）+ `enable_http2`（需 granian，且不支持多 tokenizer 与 ssl_refresh，L1086-1106）。

#### ③ 量化与数据类型（L390–401）

- `dtype="auto"`、`quantization=None`（近 30 种方案，见 2.1）、`quantization_param_path`（awq_scale 外置文件）。
- `kv_cache_dtype="auto"`：合法值 `auto/bfloat16/fp8_e5m2/fp8_e4m3/fp4_e2m1`（KV4）。
- `enable_fp32_lm_head`（小模型 logits 精度补偿）。
- ModelOpt 工作流：`modelopt_quant`（在线量化描述）→ `modelopt_checkpoint_save_path`（存量化 ckpt）→ `modelopt_checkpoint_restore_path`（还原）/ `modelopt_export_path`（导出）；`quantize_and_serve`（量化完直接服务）。
- `rl_quant_profile`：flash_rl 加载格式的量化 profile。

#### ④ 内存与调度（L403–430）

- 显存三闸门：`mem_fraction_static`（静态占比，None→按卡启发式）/ `max_running_requests` / `max_total_tokens`。
- chunked prefill：`chunked_prefill_size`（None→按显存分档）、`enable_dynamic_chunking`、`max_prefill_tokens=16384`、`prefill_max_requests`。
- 调度策略：`schedule_policy="fcfs"`（fcfs/lof/dlpl/random 等）、`schedule_conservativeness=1.0`（新请求准入激进度）、`enable_mixed_chunk`（prefill/decode 混批）。
- 优先级调度族：`enable_priority_scheduling`、`default_priority_value`、`disable_priority_preemption`、`priority_scheduling_preemption_threshold=10`、`schedule_low_priority_values_first`。
- 缓存形态：`page_size`（None→1，DSA 等场景自动改 64）、`radix_eviction_policy="lru"`（lru/lfu/slru/priority）、SWA 混合内存 `swa_full_tokens_ratio=0.8` / `disable_hybrid_swa_memory`。
- prefill delayer 族（L424-430，6 个参数）：按 token 使用率水位/前向次数桶自适应延迟 prefill，平滑 TTFT 波峰。

#### ⑤ 运行时与并行策略（L432–455、L522–532）

- 基础：`tp_size=1`、`pp_size=1`、`pp_max_micro_batch_size`、`pp_async_batch_depth=0`。
- 流式：`stream_interval=1`（每 N 个 decode 步回传一次）、`batch_notify_size=16`、`incremental_streaming_output`。
- GPU 映射：`base_gpu_id=0`、`gpu_id_step=1`（MIG/虚拟化交错编号时用）。
- 数据并行：`dp_size=1`、`load_balance_method="auto"`（非 PD 默认 round_robin；PD prefill 默认 follow_bootstrap_room，L1033-1042）。
- 细分并行：`attn_cp_size=1`（注意力上下文并行）、`moe_dp_size=1`（MoE 数据并行）——两者与 `tp/dp/ep` 的整除约束见 `_handle_context_parallelism`。
- 多节点：`dist_init_addr/nnodes/node_rank`；`use_ray`（Ray 后端，RayEngine 接管）。
- 其他：`watchdog_timeout=300`、`soft_watchdog_timeout`、`dist_timeout`、`sleep_on_idle`、`custom_sigquit_handler`（crash dump 定制）。

#### ⑥ 日志与可观测（L457–501）

- `log_level/log_level_http`、`log_requests`（含 level/format/target 三级过滤）、`decode_log_interval=40`、`crash_dump_folder`、`show_time_cost`。
- metrics：`enable_metrics`、`enable_mfu_metrics`、`enable_metrics_for_all_schedulers`、TTFT/ITL/E2E 直方图 buckets（`bucket_time_to_first_token` 等）、`prompt_tokens_buckets/generation_tokens_buckets`（tse/default/custom 三种规则，见 `validate_buckets_rule` L7451）。
- KV 事件：`kv_events_config`（ZMQ 发布订阅，供 KV-aware 路由器）。
- OTel：`enable_trace`、`otlp_traces_endpoint`。
- `stat_loggers`（L501）：类级 DI，把 scheduler/tokenizer/storage/radix_cache/expert_dispatch 五个 MetricsCollector 换成子类——嵌入式专用，无 CLI 面。

#### ⑦ API 层（L503–520）

- `api_key/admin_api_key`、`served_model_name`（禁含冒号——保留给 `model:adapter` LoRA 语法，L7171-7177）、`weight_version`。
- 模板与解析器：`chat_template/hf_chat_template_name/completion_template`、`reasoning_parser/tool_call_parser`（支持 `auto`，engine.py 启动时用 TemplateManager 探测结果回填）、`strip_thinking_cache`、`enable_strict_thinking`。
- `sampling_defaults="model"`（缺省采样参数来源：模型 config 或 OpenAI 风格）。
- ASR：`asr_max_buffer_seconds=60`、`asr_max_concurrent_sessions=32`。

#### ⑧ LoRA（L538–554）

| 字段 | 默认 | 说明 |
|---|---|---|
| `enable_lora` | None | 给了 `lora_paths` 则自动 True（L7324-7329） |
| `lora_paths` | None | dict / `name=path` 列表 / dict 列表 / LoRARef 列表四形态，启动时统一归一化为 `LoRARef`（L7356-7411） |
| `max_lora_rank` | None | 预分配的 A/B 矩阵秩上限 |
| `lora_target_modules` | None | 支持 `all` 哨兵（模型感知展开） |
| `max_loras_per_batch` | 8 | 单 batch 最多几个 adapter |
| `max_loaded_loras` | None | 常驻上限（LRU 淘汰），须 ≥ 前者 |
| `lora_backend` | csgmv | triton/csgmv/ascend/torch_native |
| `enable_lora_overlap_loading` | None | CPU 常驻 + 后台加载热替换（上限 2×max_loras_per_batch，L7339-7348） |
| `lora_use_virtual_experts` | False | MoE 虚拟专家 LoRA |
| `lora_drain_wait_threshold` | 0.0 | 换 adapter 前排空等待 |

约束：LoRA 目前**只兼容 NGRAM 投机解码**（L7351-7354）；`max_lora_chunk_size` 须为 16–128 的 2 的幂（L7438-7442）。

#### ⑨ Kernel backend（L556–577）

- `attention_backend` + `prefill_attention_backend` / `decode_attention_backend`：**prefill/decode 可分裂**（如 prefill=trtllm_mla + decode=cutedsl_mla），`get_attention_backends()`（L7070）是统一解析出口。
- `sampling_backend`（flashinfer/pytorch/ascend）、`grammar_backend`（默认 xgrammar，可选 outlines/llguidance/none）。
- `radix_cache_backend`：经 `register_radix_cache_backend` 注册的自定义 cache 工厂名。
- GEMM runner：`fp8_gemm_runner_backend` / `fp4_gemm_runner_backend`（8 种/6 种，见 2.1）。
- DSA 三件套：`dsa_prefill_backend/dsa_decode_backend/dsa_topk_backend`（DeepSeek V3.2 稀疏注意力，默认按硬件+KV dtype 自动定，L1715-1759）。
- `mamba_backend`（triton/flashinfer）、`mm_attention_backend`（多模态编码侧独立 backend）。

#### ⑩ 投机解码（L579–612）

- EAGLE 族：`speculative_algorithm`（EAGLE/EAGLE3/STANDALONE/DFLASH...）、`speculative_draft_model_path/revision/load_format`、`speculative_num_steps/eagle_topk/num_draft_tokens`（不填则 `auto_choose_speculative_params` L7844 按 arch 给默认三元组）、accept 阈值对 `speculative_accept_threshold_single/acc`（概率级提前接受）、`speculative_token_map`、`speculative_attention_mode`、`speculative_draft_window_size`。
- draft 侧可独立配置：`speculative_draft_attention_backend/speculative_moe_runner_backend/speculative_moe_a2a_backend/speculative_draft_model_quantization`（默认继承主模型量化，L1198-1201）。
- NGRAM 族（L599-608）：`speculative_ngram_min/max_bfs_breadth`、`match_type=BFS/PROB`、`max_trie_depth=18`、`capacity=10M`、外部队列 `speculative_ngram_external_corpus_path`（离线语料预填 trie）。
- `enable_multi_layer_eagle`（MiMoV2/Step3.x 自动开，L2206/2236）、自适应投机 `speculative_adaptive/speculative_adaptive_config`（按接受率动态调 steps，`max_speculative_num_draft_tokens` cached_property L7100 求上界）。

#### ⑪ 专家并行（L614–654）

- `ep_size=1`、`moe_a2a_backend="none"`（deepep/mooncake/nixl/mori/ascend_fuseep/flashinfer/megamoe，几乎全部强制 `ep_size=tp_size`，L3329-3463）、`moe_runner_backend="auto"`。
- DeepEP 细控：`deepep_mode`（auto/normal/low_latency，normal 关 CUDA graph L3357-3359）、`deepep_config`、`deepep_dispatcher_output_dtype`、`enable_deepep_waterfill`。
- 冗余专家与 EPLB：`ep_num_redundant_experts`、`enable_eplb`、`eplb_algorithm="auto"`、`eplb_rebalance_num_iterations=1000`、`eplb_rebalance_layers_per_chunk`、`ep_dispatch_algorithm`（static/dynamic）、`init_expert_location="trivial"`。
- 观测：`expert_distribution_recorder_mode`（stat/stat_approx/per_pass/per_token）、`expert_distribution_recorder_buffer_size`、`enable_expert_distribution_metrics`（EPLB 隐式要求 stat 模式，L3474-3478）。
- 弹性 EP：`elastic_ep_backend`（mooncake/nixl）、`enable_elastic_expert_backup`、`elastic_ep_rejoin`（节点摘除重入）；`moe_dense_tp_size`（MoE 模型中 dense 层独立 TP 度）。

#### ⑫ 记忆体扩展（L656–702）

- Mamba/线性注意力：`max_mamba_cache_size`、`mamba_ssm_dtype`（SM100 上 flashinfer GDN 要求 bfloat16，L3137-3149）、`mamba_full_memory_ratio=0.9`、`mamba_scheduler_strategy`（no_buffer/extra_buffer，L1190-1193 默认 no_buffer）、`mamba_track_interval=256`（须整除 page_size 且 ≥ draft tokens，L2623-2632）、`linear_attn_backend/decode_backend/prefill_backend`。
- HiCache 分层缓存：`enable_hierarchical_cache`、`hicache_ratio=2.0`、`hicache_size`、`hicache_write_policy="write_through"`、`hicache_io_backend="kernel"`、`hicache_mem_layout="layer_first"`、`hicache_storage_backend/prefetch_policy/extra_config`——layout×IO×storage 三维兼容性在 `_handle_hicache`（L3623-3650）四步归一化。
- `enable_hisparse` + `hisparse_config`（分层稀疏注意力）；`enable_lmcache/lmcache_config_file`（LMCache 集成）。
- Ktransformers：`kt_weight_path/kt_method/kt_cpuinfer/kt_threadpool_count/kt_num_gpu_experts/kt_max_deferred_experts_per_token`（CPU 大容量专家 + GPU 热专家）。
- Diffusion LLM：`dllm_algorithm/dllm_algorithm_config`（d1/td1 等，`_handle_dllm_inference` L4160 会连锁关闭 overlap/radix/PP/LoRA/分离/混合 chunk）。
- CPU offload：`cpu_offload_gb`、`offload_group_size/num_in_group/prefetch_step`、`offload_mode`。

#### ⑬ CUDA graph 与编译优化（L711–783，约 70 个开关）

- 整图 CUDA graph：`disable_cuda_graph`、`cuda_graph_max_bs/bs`、`disable_cuda_graph_padding`、`enable_breakable_cuda_graph`、`enable_profile_cuda_graph`、`enable_cudagraph_gc`、`debug_cuda_graph`。
- piecewise CUDA graph（torch.compile 切分整图）：`disable_piecewise_cuda_graph`（19 条自动关闭规则见 2.3）、`enforce_piecewise_cuda_graph`（测试用强制开）、`piecewise_cuda_graph_max_tokens/tokens/compiler`。
- `enable_torch_compile/torch_compile_max_bs=32/enable_torch_compile_debug_mode`。
- 调度：`disable_overlap_schedule`（overlap scheduler 是默认开启的性能支柱，多项特性会连锁关它）、`enable_dp_attention/enable_dp_lm_head`、`enable_two_batch_overlap/tbo_token_distribution_threshold=0.48`、`enable_single_batch_overlap`、`num_continuous_decode_steps`。
- 通信：`disable_custom_all_reduce`、`enable_mscclpp`、`enable_symm_mem/enable_nccl_nvls`、`enable_torch_symm_mem`、`enable_flashinfer_allreduce_fusion`（SM90/100 MoE 模型自动开，L2545-2572）。
- 确定性：`enable_deterministic_inference`、`rl_on_policy_target`（隐式开启确定性）。
- 其他：`enable_tokenizer_batch_encode`、`enable_dynamic_batch_tokenizer/batch_size=32/timeout=0.002`、`scheduler_recv_interval`、`numa_node`、`enable_return_hidden_states/routed_experts/indexer_topk`、`gc_threshold`、`triton_attention_*`、`enable_fused_qk_norm_rope`、`enable_attn_tp_input_scattered` 等。

#### ⑭ 分离式推理 PD disaggregation（L802–818）

- 核心：`disaggregation_mode`（null/prefill/decode）、`disaggregation_transfer_backend="mooncake"`（mooncake/nixl/ascend/fake/mori/mooncake_tcp）、`disaggregation_bootstrap_port=8998`、`disaggregation_ib_device`（IB 设备校验见 `_validate_ib_devices` L3886：读 `/sys/class/infiniband` 逐个核对、支持 per-GPU JSON 映射）。
- decode 侧：`disaggregation_decode_enable_radix_cache=False`、`disaggregation_decode_enable_offload_kvcache`（需 hicache_storage_backend）、`num_reserved_decode_tokens=512`、`disaggregation_decode_polling_interval=1`。
- 编码器分离（L813-818）：`encoder_only/language_only` 互斥且都要求 `disaggregation_mode=null`；`encoder_transfer_backend`（zmq_to_scheduler/zmq_to_tokenizer/mooncake）；`encoder_urls`；白名单校验 13 个 VLM arch（L3866-3884）。
- PD-Multiplexing：`enable_pdmux/pdmux_config_path/sm_group_num=8`（同一卡按 SM 组同时跑 P 和 D，check 阶段四条硬约束 L7197-7209）。

#### ⑮ 权重热更新与多实例加载（L820–860）

- `custom_weight_loader`（`module.Class` 列表）、`weight_loader_disable_mmap/prefetch_checkpoints/prefetch_num_threads/drop_cache_after_load`。
- 远程实例加载：`remote_instance_weight_loader_seed_instance_ip/service_port/send_weights_group_ports/backend`（transfer_engine/nccl/modelexpress）、`remote_instance_weight_loader_start_seed_via_transfer_engine`（配套 `engine_info_bootstrap_port=6789`，engine.py 会起 `EngineInfoBootstrapServer`）。
- 加密 checkpoint：`decrypted_config_file/decrypted_draft_config_file`；前向钩子：`forward_hooks`；通信压缩：`enable_quant_communications`（仅 NPU）；msProbe dump：`msprobe_dump_config`。

### 2.3 `__post_init__`（L862–1014）：一次编排 40+ 步的归一化流水线

这是全文件最关键的控制流。顺序敏感，注释里大量 "must run before/after"。完整调度表如下：

| 步骤 | 调用（行号） | 作用 |
|---|---|---|
| 1 | `_maybe_download_model_for_runai` (L867) | runai 对象存储 URI 先行下载 |
| 2 | `_handle_load_balance_method` (L870, L1027) | PD/非 PD 的 LB 默认值；校验 disaggregation_mode 合法 |
| 3 | `_handle_multimodal` (L873) | mm_process_config 结构校验（须早于 dummy 短路） |
| 4 | `_handle_ssl_validation` (L875) | SSL 文件存在性 + http2/granian 依赖 |
| 5 | `_handle_asr_validation` (L877) | ASR 参数正数校验 |
| 6 | `handle_pd_disaggregation` (L884) | arg_groups 钩子：PD flag 交叉校验 |
| 7 | `_validate_prefill_only_disable_kv_cache_args` (L888) | flag 前置条件（须 is_embedding 等） |
| — | **dummy 短路** (L890-892) | `model_path in [none, dummy]` 直接 return |
| 8 | `_handle_deprecated_args` (L895) | parser 别名映射 + gRPC env 读取 |
| 9 | `_handle_prefill_delayer_env_compat` (L898) | 旧 env 兼容 |
| 10 | unquant 解析 (L904-908) | `--quantization unquant` → None + 显式关闭标记 |
| 11 | `_handle_missing_default_values` (L911) | tokenizer_path/device/seed/ModelScope/draft 量化继承 |
| 12 | `_handle_hpu/cpu/npu/mps/xpu_backends` (L914-918) | 各硬件默认 backend |
| 13 | `current_platform.apply_server_args_defaults` (L923) | OOT 平台插件注入默认值 |
| 14 | `_handle_piecewise_cuda_graph` (L926) | 19 条自动关闭规则 |
| 15 | `get_device_memory_capacity` (L929) | 探测显存（后续多步公共依赖） |
| 16 | `_handle_gpu_memory_settings` (L932) | 见 2.4 |
| 17 | deterministic 预置 (L937-938) | 确定性推理强制关 allreduce fusion（须在模型特判前） |
| 18 | `_handle_model_specific_adjustments` (L941) | 见 2.5，821 行 arch 特判 |
| 19 | `_handle_sampling_backend` (L944) | flashinfer 可用性探测 |
| 20 | `_handle_deterministic_inference` (L947) | 须在 attention 自动选择**前**锁定确定性 backend |
| 21 | `_handle_attention_backend_compatibility` (L948) | 默认 backend 选择 + page_size 矫正 |
| 22 | `_handle_mamba_backend` / `_handle_linear_attn_backend` (L949-950) | flashinfer GDN 可用性与 dtype 约束 |
| 23 | `_handle_kv4_compatibility` (L951) | FP4 KV 的 2×2 backend 矩阵 |
| 24 | `_handle_page_size` (L952) | 默认 1（musa 为 64） |
| 25 | `_handle_amd_specifics` / `_handle_nccl_pre_warm` / `_handle_grammar_backend` (L953-955) | 平台杂项 |
| 26 | `_handle_multi_item_scoring` (L959) | MIS 连锁关 CUDA graph/radix/chunked prefill |
| 27 | `_handle_prefill_only_disable_kv_cache` (L966) | backend 已定型后二次校验（fa3/fa4） |
| 28 | `_handle_hicache` (L969) | layout/IO/storage 三维四步归一化 |
| 29 | `_handle_data_parallelism` (L972) | dp 联动（见 2.6） |
| 30 | `_handle_context_parallelism` (L975) | attn_cp/moe_dp 八条整除约束 |
| 31 | `_handle_moe_kernel_config` / `_handle_a2a_moe` (L978-979) | runner×量化兼容 / a2a 强制 ep=tp |
| 32 | `_handle_eplb_and_dispatch` / `_handle_expert_distribution_metrics` / `_handle_elastic_ep` (L980-982) | EPLB 与弹性 EP |
| 33 | `_handle_pipeline_parallelism` (L985) | PP>1 关 overlap |
| 34 | `handle_speculative_decoding` (L988-990) | arg_groups 钩子：EAGLE/NGRAM 参数推导 |
| 35 | `_handle_load_format` (L993) | gguf/mistral/remote 嗅探 |
| 36 | `_handle_encoder_disaggregation` (L996) | 编码器分离校验 |
| 37 | `_handle_tokenizer_batching` (L999) | 两种批处理互斥；skip_tokenizer_init 联动 |
| 38 | `_handle_environment_variables` (L1002) | CLI 字段回写 SGLANG_* env |
| 39 | `_handle_cache_compatibility` (L1005) | hicache×radix 互斥、offload 前置 |
| 40 | `_handle_dllm_inference` (L1008) | Diffusion LLM 连锁降级 |
| 41 | `_handle_debug_utils` (L1011) | CI 环境 soft watchdog |
| 42 | `_handle_other_validations` (L1014) | tensor dump/msProbe/JSON 参数解析 |

要点评注：

- **dummy 短路的位置**（L890–892）：`model_path.lower() in ["none", "dummy"]` 直接 return——测试/CI 不下模型就能把 Engine 拉起来；但 L869-888 的注释强调 1-7 步都是"必须在短路前"的校验（用户配错 SSL/PD flag 即使 dummy 也要报错）。
- **`_quantization_explicitly_unset`**（L904–908）：`--quantization unquant` 是"显式不量化"，与"没填"（None，可被自动检测覆盖）语义区分，防止 L1971-1993 的 sm100 自动量化检测误伤。
- **顺序即依赖**：例如 `_handle_deterministic_inference` 注释（L945-947）明说"必须先于 `_handle_attention_backend_compatibility`，否则自动检测会填进非确定性 backend"；`_handle_prefill_only_disable_kv_cache` 用 assert（L3610-3613）防调用点被重排。

### 2.4 `_handle_gpu_memory_settings`（L1411–1612）：三档联动的显存推导

核心注释在 L1411-1434：`GPU 显存 = 模型权重 + KV cache 池 + 激活 + CUDA graph buffer`，而 `mem_fraction_static = (权重+KV池)/总显存`。推导链：

1. **按显存分档**定 `chunked_prefill_size` 与 `cuda_graph_max_bs`：<20G（T4/4080）→ 2048/8；<35G（A10/4090）→ 2048/24（TP<4）或 80；<60G（A100-40G）→ 4096/32 或 160；<90G（H100）→ 8192/256 或 512；<160G（H20/H200）→ 同 H100；else（B200/MI300）→ 16384/512。L1449-1451 的长注释解释了低端卡 TP4/TP8 时 `cuda_graph_max_bs=80` 的来历（qwen2-72b 实测）。
2. `_generate_cuda_graph_batch_sizes`（L1614）：普通路径 `[1,2,4,8,12]+range(16,257,8)+...`；投机解码路径小 bs 更密（`range(1,9,1)+range(10,33,2)+...`）以降低 padding 浪费。
3. **`mem_fraction_static` 反推**（L1551–1598）：`reserved_mem = 512 + chunked_prefill*1.5 + cuda_graph_max_bs*2 + tp*pp/8*1024 (+DP attention 额外) (+piecewise graph) (+投机 4-6G)`，大卡下限 `max(reserved, 10G)`；MLA 后端 piecewise token 上限 2048 防性能回退（L1524-1531）。
4. VLM 再乘 `adjust_mem_fraction_for_vlm`（L7499）：以 ViT-L/14 为基线，按 `层数×hidden²` 复杂度比例 0.95×[0.8,1.05] 动态缩放。

### 2.5 `_handle_model_specific_adjustments`（L1761–2580）：按 arch 的一揽子特判

821 行的巨型 if-elif，是"SGLang 对各家模型做了什么优化"的索引：

- **DeepSeek V3/V3.2/Kimi K2.5/GLM-DSA**（L1796–2050）：DSA 模型设 `attention_backend=dsa`、`page_size=64`（ROCm 旧路径为 1）、按 SM 代数定 `kv_cache_dtype`（SM100→fp8_e4m3）与 dsa prefill/decode backend（`_set_default_dsa_backends` L1715：Blackwell→trtllm/flashmla_sparse，Hopper→flashmla_kv/fa3）；DSA prefill CP 自动联动（`enable_dp_attention+moe_dense_tp_size=1+moe_a2a=deepep+ep=tp`，L1831-1867）；**sm100 上检测 checkpoint 是否真含 FP8 权重**（`has_fp8_weights_in_checkpoint` L1980，避免 Moonlight 这类同架构 BF16 模型被误判）；`moe_runner_backend` 自动选 `flashinfer_trtllm`。
- **GPT-OSS**（L2058–2177）：按平台选 attention backend（sm100→trtllm_mha / sm90→fa3 / cpu→intel_amx / hip→aiter）；mxfp4 强制 bf16 计算；Blackwell+driver≥595 时 triton_kernels 会 SIGSEGV → 回退 triton（L2158-2167）。
- **MiMoV2 / Step3.x / Llama4 / Gemma2-4 / Qwen3 系 / GLM-4 MoE / KimiLinear / NemotronH / Lfm2**（L2179–2521）：各自的 attention backend 白名单、fused-qkv TP 约束（MiMoV2 L2180-2204）、multi-layer EAGLE 自动开启、mamba/hybrid 模型经 `_handle_mamba_radix_cache`（L2582：extra_buffer 策略下 radix cache 与 overlap/投机/页大小的相容性裁决）。
- **FlashInfer AllReduce Fusion 自动开启**（L2545–2572）：SM90/100 + TP>1 + 单机 + 非 DP attention + 无 a2a 的 MoE 模型全家（DeepSeek/GptOss/GLM/Qwen3...）自动 `enable_flashinfer_allreduce_fusion=True`；确定性推理则强制关（L2575）。

### 2.6 backend 自动选择与兼容性

- `_get_default_attn_backend`（L2677）：**MHA**：Hopper+spec-topk≤1→`fa3`（注释引 issue #17411：flashinfer 0.6.1 在 Hopper 有回退）；SM100→`trtllm_mha`；HIP→`aiter`；MPS→`torch_native`；否则 flashinfer（无 attention sink 时）或 triton。**MLA**：Hopper→fa3，Blackwell→flashinfer，HIP 按 KV head 数（16/128）选 aiter。
- `_handle_attention_backend_compatibility`（L2746–2995）：逐 backend 的 page_size 矫正——flashmla→64、cutlass_mla→128、trtllm_mla→32/64（且仅 Blackwell）、trtllm_mha→16/32/64、cutedsl_mla 仅 decode 且自动补 prefill=trtllm_mla；`torch_native/flex_attention` 强制关 CUDA graph；fa3+fp8_e5m2 → 降级 triton；aiter 长上下文 `mem_fraction_static×0.85`；`dual_chunk_flash_attn` 关 mixed chunk 与 radix。
- `_handle_kv4_compatibility`（L2997）：FP4 KV cache 与 prefill/decode backend 的 2×2 组合矩阵校验。
- `_handle_data_parallelism`（L3218）：`dp_size==1` 时硬关 DP attention；开 DP attention 则 `schedule_conservativeness×0.3`、`chunked_prefill_size//dp_size`（防 MoE kernel 越界）。
- `_handle_context_parallelism`（L3167）：`tp%attn_cp==0`、`tp%(dp*attn_cp)==0`、`ep*moe_dp≤tp`、`attn_cp≠moe_dp 时必须 moe_dp==1` 等 8 条整除断言。
- `_handle_a2a_moe`（L3329–3471）：所有 a2a backend 几乎都强制 `ep_size=tp_size`；`deepep_mode=normal` 关 CUDA graph；`flashinfer` a2a 要求 `dp==tp` 且 runner 限 cutlass/cutedsl，并校验 dispatch 容量覆盖 `max_prefill_tokens`（L3424-3454 精确到 env 名的报错信息）。
- `_handle_deterministic_inference`（L4057）：`rl_on_policy_target` 隐式开启；强制 `sampling_backend=pytorch`；TP>1 时 `NCCL_ALGO=allreduce:tree` + 禁 custom all-reduce（AMD 用天然确定性的 1-stage kernel）。
- `_handle_load_format`（L3727）：GGUF 文件嗅探、Mistral 原生格式探测（`_is_mistral_native_format` L3779：`consolidated*.safetensors` 且无 `model-*.safetensors`，或路径含 mistral-large-3/small-4/leanstral 且有 params.json）、runai/remote URL 自动切换。

### 2.7 CLI 层：`add_cli_args` / `from_cli_args`（L4296–7017）

`add_cli_args` 是 staticmethod，内部注释分组（L4299 `# Model and tokenizer`、L4436 `# HTTP server`、L4615 `# Memory and scheduling`、L5318 `# Data parallelism`、L5372 `# LoRA`、L5471 `# Kernel backend`、L5615 `# Speculative decoding`、L5824 `# Expert parallelism`、L6739 `# PD disaggregation`...共 44 组）与 dataclass 字段完全镜像。CLI 名与字段名的映射在 `from_cli_args`（L7003）：`--tensor-parallel-size→tp_size`、`--pipeline-parallel-size→pp_size`、`--attention-context-parallel-size→attn_cp_size`、`--moe-data-parallel-size→moe_dp_size`、`--data-parallel-size→dp_size`、`--expert-parallel-size→ep_size`；不在 Namespace 的字段（如 DI 专用 `stat_loggers`）跳过以保留默认（L7011-7017）。弃用别名经 `arg_groups/argparse_actions.py` 的 `DeprecatedStoreTrueAction/DeprecatedAliasStoreAction/LoRAPathAction` 处理。

### 2.8 只读属性与工具方法（L7019–7678）

- `url(port)`（L7019）：host 为 `0.0.0.0/::` 时内部请求回退 loopback。
- `ssl_verify`（L7035）：有 CA→返回路径；仅自签证书→`False` 并警告一次；无 SSL→`True`。
- `get_model_config`（L7061）：**惰性构建并缓存** `ModelConfig.from_server_args(self)`（避免循环 import）；后续 `use_mla_backend()`（L7083）、`is_attention_backend_not_set()`（L7089）都依赖它。
- `get_attention_backends`（L7070）：`(prefill or attention, decode or attention)` 的二元组解析——分裂 backend 的统一出口。
- `max_speculative_num_draft_tokens`（L7100，cached_property）：自适应投机时取候选 steps 最大值+1。
- `check_server_args`（L7133–7319）：跨字段终审——`tp*pp % nnodes==0`、PP 与 overlap/投机互斥（L7154）、**多节点必须开 DP attention**（L7159）、`served_model_name` 禁含冒号（保留给 `model:adapter` LoRA 语法，L7171-7177）、pdmux 四约束、优先级调度仅限 fcfs/lof、TBO 必须配 a2a、`enable_quant_communications` 仅 NPU+TP>1。
- `check_lora_server_args`（L7320–7449）：`lora_paths` 归一化为 `LoRARef` 列表（`name=path` 字符串/dict/纯路径三形态，deterministic_id）；**LoRA 目前只兼容 NGRAM 投机**（L7351）；`max_loaded_loras≥max_loras_per_batch`；`max_lora_chunk_size` 必须是 16–128 的 2 的幂。
- `describe_kv_events_publisher`（L7594）：把 `kv_events_config` 解析成 `/server_info` 上的结构化 wire contract（endpoint_port_base+dp_rank 的订阅规则），供 KV-aware 路由器零配置订阅；任何字段非法一律返回 None 保端点可用。

### 2.9 全局单例与入口（L7681–7734）

`_global_server_args`（L7682）+ `set_global_server_args_for_scheduler`（L7685，别名 `set_global_server_args_for_tokenizer` L7690）+ `get_global_server_args`（L7693）。因为 Scheduler/TokenizerManager 子进程只能拿到序列化副本，各进程入口（`model_runner.py:509`、`tokenizer_manager.py:246`、`encode_server.py:225`、`dflash_worker.py:157`、`expert_backup_manager.py:162`）把它重新钉回全局变量，深层代码（attention backend、MoE 层）用 `get_global_server_args()` 免传参读取。

`prepare_server_args(argv)`（L7700）：建 parser → 若有 `--config` 走 `ConfigArgumentMerger` 合并配置文件（L7715-7721）→ `logging.basicConfig` 先行（让 `__post_init__` 里的 warning 有格式化输出）→ `from_cli_args`。

### 2.10 `PortArgs`（L7741–7841）：ZMQ 拓扑的地址簿

7 个字段：`tokenizer_ipc_name`（detokenizer→tokenizer）、`scheduler_input_ipc_name`（tokenizer→scheduler rank0/DP controller）、`detokenizer_ipc_name`、`nccl_port`、`rpc_ipc_name`（Engine↔Scheduler RPC）、`metrics_ipc_name`、`tokenizer_worker_ipc_name`（多 tokenizer 时）。普通模式下 5 条 ZMQ 通道与进程拓扑的对应关系：

```
主进程                                     子进程
┌──────────────────┐   scheduler_input_ipc   ┌─────────────────┐
│ TokenizerManager ├──────────(PUSH)────────>│ Scheduler ×N     │
│   (Engine 同进程) │<─────────(PUSH)─────────┤ (tp/pp rank 各一)│
│                  │   tokenizer_ipc_name    └───┬─────────────┘
│                  │<──────(PUSH)────────────────┤ detokenizer_ipc
│                  │   （DetokenizerManager 回传）│
└──────┬───────────┘                           ┌─────────────────┐
       │ rpc_ipc_name (DEALER↔ROUTER)          │ DetokenizerMgr  │
       └──────────────────────────────────────>│ (1 或多 worker) │
                                               └─────────────────┘
  另有 metrics_ipc_name：Scheduler→TokenizerManager 的 Prometheus 指标流
  nccl_port：torch.distributed init rendezvous
```

`init_new`（L7762）两种模式：

- **普通模式**（非 DP attention，L7780–7790）：全部用 `ipc://{NamedTemporaryFile}` —— 单机 unix domain socket，零端口冲突；`nccl_port` 用 `get_free_port()` 或用户指定。
- **DP attention 模式**（L7791–7841）：必须 TCP（DP controller 需被多个 scheduler 进程组连接，且可能跨节点）。单机无 `dist_init_addr` 时以 `port+ZMQ_TCP_PORT_DELTA(233)` 为基址（L7794）；否则从 `dist_init_addr` 推导，`port_base=dist_port+1` 起依次 +1..+4 分配 tokenizer/detokenizer/rpc/metrics/scheduler_input（L7800-7809），并在 bind 前 `wait_port_available` 逐个探测、冲突即抛错（L7811-3827 的详细日志）。DP controller 再用 `DP_ATTENTION_HANDSHAKE_PORT_DELTA(13)`（L7738）给每个 DP rank 算 worker port。

### 2.11 `auto_choose_speculative_params`（L7844–7879）

按 arch 返回 `(num_steps, eagle_topk, num_draft_tokens)` 默认三元组：STANDALONE→(3,1,4)；Llama→(5,4,8)；DeepSeek/GptOss/GLM MoE/MiMoV2 等新架构→(3,1,4)；Grok→(5,4,8)。由 `arg_groups/speculative_hook.py:347` 在用户未显式指定时调用。

---

## 三、与其他模块的交互

**import 了谁**（依赖方向）：
- `sglang.srt.environ`（envs 统一环境变量面）、`sglang.srt.utils.common`（20+ 硬件探测：`is_cuda/is_hip/is_npu/is_sm90_supported/get_device_memory_capacity/has_fp8_weights_in_checkpoint`...）、`sglang.srt.utils.network`（`NetworkAddress/get_free_port/wait_port_available`）、`hf_transformers_utils.check_gguf`。
- 惰性 import 破环：`configs.model_config.ModelConfig`（L7062）、`platforms.current_platform`（L921/L2692）、`arg_groups.{pd_disaggregation,speculative,hisparse,deepseek_v4,nemotron_h}_hook`——把大块领域逻辑外置成钩子模块，本文件只保留编排。
- `lora.lora_registry.LoRARef`、`parser.reasoning_parser`、`function_call.function_call_parser`（choices 来自解析器注册表）。

**被谁调用**（grep 全仓 51 个文件直接 import）：
- 启动链：`sglang/launch_server.py:66` 与 `sglang/cli/serve.py:126` 调 `prepare_server_args`；`entrypoints/engine.py:218` 直接 `ServerArgs(**kwargs)`；`entrypoints/http_server.py` 依赖其字段逐项建 FastAPI 路由。
- 进程内广播：`managers/scheduler.py`、`managers/tokenizer_manager.py`、`model_executor/model_runner.py` 等经 `set_global_server_args_for_*` 钉全局单例后用 `get_global_server_args()` 读取。
- 派生配置：`configs/model_config.py` 的 `ModelConfig.from_server_args`、`managers/io_struct.py` 各请求结构体的默认值、`arg_utils`（benchmark 脚本复用 add_cli_args）。

---

## 四、关键设计决策

1. **"dataclass 字段 = 唯一事实源，argparse 是镜像"**：字段默认值写在 dataclass 上，`add_cli_args` 的 `default=ServerArgs.xxx` 引用同一常量，`from_cli_args` 只做改名与按字段过滤。这保证 CLI、Python API（`Engine(**kwargs)`）、配置文件三条入口语义一致，新增参数只改两处且顺序注释（L347-350）强制了可维护性。
2. **`__post_init__` 是"编译器"而非"校验器"**：大量 `_handle_*` 会**改写**用户参数（自动关 radix cache、强制 page_size、覆盖 moe_runner_backend），原则是"用户给意图，SGLang 定具体值"。警告日志记录每次改写，顺序依赖显式写在注释里——这是 300 个互相耦合的开关能共存的核心机制。
3. **硬件感知的默认值推导**（`_handle_gpu_memory_settings`、`_get_default_attn_backend`）：以 GPU 显存分档和 SM 代数为输入做启发式，目标让"裸跑 `sglang.launch_server --model x` 在任何卡上都接近最优"。代价是本文件必须持续吸收各模型/驱动的特判（如 Blackwell driver≥595 的 triton_kernels 崩溃），这也是它膨胀到 7900 行的主因。
4. **可插拔目录 + OOT 平台**：`add_*_choices` 开放扩展点 + `current_platform.apply_server_args_defaults` 钩子，让 NPU/XPU/MUSA 等 out-of-tree 后端无需改本文件即可注入默认值；`arg_groups/*_hook` 把 DeepSeek V4/NemotronH/HiSparse 等长特判外移，控制主文件熵增。
5. **配置的全进程可达性**：`ServerArgs` 随 `mp.Process` 序列化进每个子进程，再钉回 `_global_server_args` 单例；同时 `_handle_environment_variables` 把部分字段回写 `SGLANG_*` env——双通道（对象+env）覆盖"C 级扩展库只读 env"与"深层 Python 代码免传参"两类消费者。
6. **弃用参数的软着陆策略**：改名（`nsa→dsa`、`compressed→dsv4`、`qwen25→qwen`）一律保留旧名 + 运行时 warning + 自动改写（L1125-1146），配合 `argparse_actions.Deprecated*Action` 在 CLI 层拦截——在快速迭代的开源项目里，破坏用户启动脚本的成本远高于维护别名的成本。

---

## 五、环境变量速查（`_handle_environment_variables` 与 envs 交互）

本文件是"CLI 字段 → SGLANG_* env"的回写点之一（读 `sglang/srt/environ.py` 的 `envs` 注册表）：

| CLI/字段 | env | 行号 |
|---|---|---|
| `enable_torch_compile` | `SGLANG_ENABLE_TORCH_COMPILE` | L3995 |
| `mamba_ssm_dtype` | `SGLANG_MAMBA_SSM_DTYPE` | L3996-3997 |
| `disable_outlines_disk_cache` | `SGLANG_DISABLE_OUTLINES_DISK_CACHE` | L3998-4000 |
| `enable_deterministic_inference` | `SGLANG_ENABLE_DETERMINISTIC_INFERENCE` | L4001-4003 |
| 多节点强制关闭 | `SGLANG_OPT_USE_CUSTOM_ALL_REDUCE_V2=0` | L4006-4013 |
| `debug_cuda_graph` | `SGLANG_USE_BREAKABLE_CUDA_GRAPH=1` | L4014-4026 |
| sm<100 自动关闭 | `SGLANG_OPT_FP8_WO_A_GEMM` | L4027-4035 |

另有只在模型特判中设置的：DSA 阈值 `SGLANG_DSA_PREFILL_DENSE_ATTN_KV_LEN_THRESHOLD`（L1807/1820）、GLM5 on Blackwell 置 0、对称内存预分配 `SGLANG_SYMM_MEM_PREALLOC_GB_SIZE` 默认 4G（L1606-1612）等。方向感：**env 是 runtime 微调面，CLI 是部署拓扑面**；一个行为同时有 CLI 和 env 时以 CLI 为准（env 只在 CLI 未覆盖时生效，见 environ.py 语义）。

---

## 六、阅读建议

1. **先读字段分组注释**（L353–860），对照 `docs` 里的 CLI 文档建心智地图；不要一开始就读 `__post_init__`。
2. 再读 `__post_init__`（L862–1014）只看注释与调用顺序，把 40+ handler 当黑盒，理解"early validation → dummy 短路 → 默认值 → 设备 backend → 内存 → 模型特判 → kernel → 并行 → 兜底"的流水线骨架。
3. **按问题钻取**：调显存问题读 `_handle_gpu_memory_settings`（L1411）与其 docstring 里的公式；调 attention 报错读 `_handle_attention_backend_compatibility`（L2746）；跑 DeepSeek 读 L1796–2050；配 LoRA 读 `check_lora_server_args`（L7320）。
4. `add_cli_args`（L4296–7001）当字典查，勿通读；注意 CLI 名与字段名差异集中在 `from_cli_args`（L7003）的 6 个改名。
5. 修改参数时牢记三条铁律：①新字段顺序须与 `add_cli_args` 同步；②在 `__post_init__` 里加 handler 要注明与既有 handler 的先后依赖；③跨字段硬约束放 `check_server_args`（在 Engine 启动时由 `server_args.check_server_args()` 调用，见 engine.py L762），软改写放 `_handle_*`。
6. 注意本文件在提交 ec075d8bc 处的状态是"活跃膨胀期"（DSA/CP/elastic EP/piecewise graph 都是近期能力），读旧版博客/教程时以本文件 choices 清单为准。
