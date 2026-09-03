# vLLM 新人上手指南

> 基于 understand-anything 知识图谱自动生成（11615 节点 / 33598 边 / 2226 个源文件 / commit `7894394b`）。技术术语保留英文。

## 1. 项目总览

| 项 | 内容 |
|---|---|
| 项目 | **vLLM** —— 高吞吐、内存高效的 LLM 推理与服务引擎 |
| 语言 | Python（主体）、Rust（新一代前端）、C++/CUDA/Triton（算子）、CMake |
| 框架 | PyTorch、FastAPI、Ray、CUDA、Triton、Docker |
| 规模 | 280+ 模型架构、55+ attention backend、70+ KV transfer connector，全仓 2200+ 源文件 |

**vLLM 是什么**：把 HuggingFace checkpoint 变成高性能生产服务的完整系统——从 OpenAI 兼容 API 到 GPU kernel 全栈自研。它是当前 LLM serving 事实上的开源标准之一，SGLang、TensorRT-LLM 等均与其对标。

**为什么值得学**：
- **PagedAttention**：把 OS 虚拟内存的分页思想引入 KV cache 管理，KV 显存浪费从 60%+ 降到近 4%，是 vLLM 的立身之本。
- **Continuous batching**：请求级迭代调度，新请求随时插入运行批次，无需等整批完成，吞吐数倍于静态 batching。
- **V1 架构**：前端（AsyncLLM）与引擎核心（EngineCore）进程分离、overlap scheduling、torch.compile piecewise 编译 + CUDA Graph，代表了 2025 年后推理引擎的工程范式。
- **生态广度**：投机解码（EAGLE/MTP/ngram）、结构化输出、多模态、PD 分离、MoE 专家并行、量化（FP8/FP4/GPTQ/AWQ）全部内置，是学习"推理系统全貌"的最佳单一仓库。

## 2. 架构分层（16 层）

图谱按职责把代码分为 16 层。自上而下大致是"用户入口 → 引擎 → 调度/显存 → 执行 → 算子/模型 → 平台"：

| # | 层 | 规模 | 职责与代表文件 |
|---|---|---|---|
| 1 | 服务入口 | 234 | OpenAI/Anthropic/Cohere 兼容 API、CLI、gRPC。`entrypoints/openai/api_server.py`、`entrypoints/llm.py`、`chat_utils.py` |
| 2 | 工具调用与推理解析 | 70 | 40+ 模型的 tool parser 与 `<think>` 推理链提取。`tool_parsers/abstract_tool_parser.py`、`reasoning/deepseek_r1_reasoning_parser.py` |
| 3 | Rust 前端 | 99 | Rust 重写的高性能 HTTP/gRPC server 与 EngineCore 客户端。`rust/src/server/src/lib.rs`、`rust/src/engine-core-client/src/client.rs` |
| 4 | 配置与环境 | 41 | 数百配置项的聚合与校验。`config/vllm.py`（VllmConfig 聚合根）、`engine/arg_utils.py`（EngineArgs）、`envs.py` |
| 5 | V1 引擎核心 | 80 | EngineCore/AsyncLLM 生命周期、输入输出处理、采样、投机解码、结构化输出。`v1/engine/core.py`、`async_llm.py` |
| 6 | 调度与 KV Cache 管理 | 49 | continuous batching 调度与 PagedAttention 块管理。`v1/core/sched/scheduler.py`、`kv_cache_manager.py`、`block_pool.py` |
| 7 | GPU 执行 Worker | 124 | ModelRunner 驱动 forward、CUDA Graph、executor 进程模型。`v1/worker/gpu_model_runner.py`、`gpu_worker.py` |
| 8 | 图编译与静态图 | 51 | torch.compile piecewise 编译与 CUDA Graph 捕获、融合 pass。`compilation/backends.py`、`v1/worker/gpu/cudagraph_utils.py` |
| 9 | 注意力后端 | 130 | FlashAttention/FlashInfer/TRT-LLM MLA/Triton 等 55+ 后端抽象与实现。`v1/attention/backend.py`、`backends/flash_attn.py` |
| 10 | 量化与 MoE | 214 | FP8/FP4/GPTQ/AWQ 等量化方案与 FusedMoE 执行。`layers/quantization/fp8.py`、`layers/fused_moe/fused_moe.py` |
| 11 | 模型实现 | 516 | 280+ Transformer 架构与权重加载。`models/llama.py`、`registry.py`、`model_loader/default_loader.py` |
| 12 | 计算层与算子内核 | 264 | Linear/Embedding/LoRA 等基础层与 Triton/Helion/CuTeDSL kernel。`layers/linear.py`、`_custom_ops.py` |
| 13 | 分布式执行 | 145 | TP/PP/DP/EP 进程组、custom all-reduce、KV transfer、EPLB。`distributed/parallel_state.py` |
| 14 | 多模态管线 | 66 | 图/视频/音频输入解析、processor 注册与缓存。`multimodal/registry.py`、`parse.py` |
| 15 | 平台适配与插件 | 20 | CUDA/ROCm/XPU/CPU/TPU 平台抽象与 OOT 插件。`platforms/interface.py` |
| 16 | 共享基础设施 | 142 | 通用工具、HF 适配、日志追踪、核心数据类型。`sampling_params.py`、`transformers_utils/config.py` |

## 3. 关键概念

1. **AsyncLLM / EngineCore 分离**：API 进程持有 AsyncLLM（异步前端，处理输入校验与流式输出），EngineCore 在独立进程运行调度+执行循环，两者经 ZMQ 以 msgspec 消息通信。好处：GIL 隔离，API 阻塞不影响引擎 step 节拍；EngineCore 崩溃可被哨兵（fault tolerance）拉起。
2. **PagedAttention / KV block**：KV cache 按固定大小 block（页）分配，逻辑块→物理块的映射由 BlockTable 维护，注意力 kernel 直接在分页布局上计算。显存按需分配，杜绝预留整条序列。
3. **BlockPool 与前缀缓存**：物理块以内容哈希（block hash，含 prefix token 序列+多模态/LoRA 附加键）索引，新请求 prompt 哈希命中即复用已算 KV（prefix caching），LRU 淘汰。这是多轮对话/Agent 场景 TTFT 陡降的关键。
4. **Continuous batching**：调度器每个 engine step 重新组批——waiting 队列的请求凑 token 预算做 prefill，running 请求各出 1 token 做 decode，完成的立刻移出、新来的立刻加入，GPU 永不空转。
5. **请求状态机与抢占**：Request 在 WAITING/RUNNING（被抢占时回退重算或换出）间流转；KV 不够时调度器按策略抢占低优先级请求、释放其块，保证高优请求不被饿死。
6. **Chunked prefill**：长 prompt 切成多个 token 块分多次迭代处理，避免一次巨型 prefill 阻塞 decode 造成尾延迟；与 prefill-decode 交错调度配合。
7. **Overlap scheduling（异步调度）**：CPU 侧第 N+1 步调度与 GPU 第 N 步计算重叠（async_scheduler + model runner 的异步输出回传），消除 CPU 发射间隙。
8. **torch.compile piecewise 编译 + CUDA Graph**：dynamo 捕获模型 FX 图，在 attention 等 splitting ops 处切开，可编译子图用 inductor 编译，不可编译部分用 CUDA Graph 捕获重放；配合融合 pass（RMSNorm+量化、QK norm+RoPE+KV 写入三合一等）压低 decode 步的 CPU 开销与 kernel 数。
9. **投机解码（speculative decoding）**：draft 模型（EAGLE/MTP 头/ngram 匹配/DFlash 并行草稿）一次猜 k 个 token，target 模型单步并行验证，rejection sampler 按概率接受——用少量冗余计算换 decode 步长倍增。
10. **结构化输出（structured output）**：请求带 json_schema/grammar 时，xgrammar（默认）等后端把文法编译成 token bitmask，采样前把非法 token 的 logits 置 -inf，保证输出可被程序解析。
11. **Attention backend 抽象**：AttentionBackend 基类做能力协商，AttentionMetadataBuilder 构造批元数据，各后端（FA/FlashInfer/TRT-LLM MLA/Triton/CPU…）注册进 registry，由平台 Platform + 配置在启动时选择——模型代码完全不感知后端差异。
12. **量化方法体系**：QuantizationConfig→QuantizeMethod 两层抽象，每种方案（FP8、GPTQ、AWQ、Marlin、compressed-tensors…）实现 create_weights/process_weights_after_loading/apply 三段式；权重加载后常做 repack（如 Marlin 格式）以适配专用 GEMM kernel。
13. **FusedMoE 与专家并行**：MoE 层拆为 router（topk 选路）+ FusedMoE（分组 GEMM + permute/unpermute）；专家可按 EP 切到多卡，token 经 all2all（DeepEP/FlashInfer）dispatch/combine，EPLB 后台按负载重排专家。
14. **多模态管线**：MULTIMODAL_REGISTRY 按模型注册 processor；用户输入（图/视频/音频）经 parse 归一为 data items，processor 替换 prompt 中的占位符并产出特征，PlaceholderRange 记录特征落在序列的区间；encoder 输出可缓存复用。
15. **KV transfer / PD 分离**：KVConnectorBase_V1 定义 scheduler/worker 双侧原语，70+ connector 把 prefill 实例算好的 KV 经网络/文件（NIXL/HF3FS/LMCache…）传给 decode 实例，实现 prefill-decode 分离部署。

## 4. 推荐学习路径（14 步）

### Step 1 项目总览：门面与骨架
**为什么**：先建全局地图再钻细节。**看**：`vllm/__init__.py`（延迟导入组装公共 API）、`vllm/entrypoints/__init__.py`（全部服务入口）、`setup.py`（CMake 构建 CUDA 算子）。**自检**：一个推理请求从哪扇门进来？C++ 扩展如何编译进 wheel？

### Step 2 配置体系：EngineArgs 与 VllmConfig
**为什么**：数百配置项，看懂聚合才能看懂启动。**看**：`vllm/engine/arg_utils.py`、`vllm/config/vllm.py`、`config/device.py`、`config/attention.py`。**自检**：一条 CLI 参数如何流入引擎各组件？配置哈希如何支撑编译缓存？

### Step 3 V1 引擎核心：AsyncLLM 与 EngineCore
**为什么**：整个系统的中枢。**看**：`v1/engine/async_llm.py`、`core.py`、`core_client.py`、`v1/engine/__init__.py`（msgspec 消息协议）。**自检**：API server 持有的引擎句柄到底连着什么？进程内与跨进程两种 client 差在哪？

### Step 4 请求的一生：输入校验到流式输出
**为什么**：vLLM 最核心的一条主线。**看**：`v1/engine/input_processor.py` → `v1/request.py` → `v1/core/sched/scheduler.py` → `v1/engine/output_processor.py` → `detokenizer.py`。**自检**：请求的数据形态在每个环节如何变化？stop string 在哪检测？

### Step 5 KV Cache：显存经济学
**为什么**：PagedAttention 是立身之本，直接决定吞吐上限。**看**：`v1/core/kv_cache_manager.py`、`kv_cache_utils.py`、`block_pool.py`。**自检**：一个 token 的 KV 如何写进块？前缀缓存为何能命中？抢占时块如何回收？

### Step 6 GPU 执行层：ModelRunner 驱动 forward
**为什么**：调度决策落地为 GPU 计算之处。**看**：`v1/worker/gpu_model_runner.py`（7700 行核心）、`worker_base.py`、`gpu/input_batch.py`、`gpu/cudagraph_utils.py`、`compilation/backends.py`。**自检**：SchedulerOutput 如何变成一次真实的 kernel 启动序列？CUDA Graph 为何要按 batch size 分段捕获？

### Step 7 模型动物园：新增一个模型怎么接
**为什么**：学习"vLLM 如何实现模型"的样本库。**看**：`models/llama.py`（基线五件套）、`qwen2.py`、`registry.py`、`interfaces.py`。**自检**：模型文件如何组合 layers 组件？如何被 config 中的架构名经 registry 找到？

### Step 8 计算层与算子：linear、量化、MoE 与注意力后端
**为什么**：性能真正藏身之处。**看**：`layers/linear.py`（TP 线性层族）、`vocab_parallel_embedding.py`、`quantization/fp8.py`、`fused_moe/fused_moe.py`、`v1/attention/backend.py`、`backends/flash_attn.py`。**自检**：模型层如何委托给这些组件？attention backend 如何按平台被选择？

### Step 9 分布式执行：TP/PP/DP/EP 进程组
**为什么**：大模型推理离不开多卡。**看**：`distributed/parallel_state.py`、`communication_op.py`、`device_communicators/custom_all_reduce.py`。**自检**：多卡 forward 中通信何时发生？TP 切分如何体现在 linear 层的 weight_loader？

### Step 10 多模态管线：图片音频如何变成 token
**为什么**：VLM 输入处理链路。**看**：`multimodal/parse.py`、`inputs.py`、`registry.py`、`cache.py`。**自检**：多模态输入从原始字节到 embedding、再到与文本 token 拼接的完整路径是什么？

### Step 11 服务入口：OpenAI 兼容 API 与离线 LLM 类
**为什么**：用户直接触达的一层，请求旅程的起点与终点。**看**：`entrypoints/llm.py`、`chat_utils.py`、`openai/api_server.py`、`chat_completion/protocol.py`、`grpc_server.py`。**自检**：HTTP 字段如何逐层翻译成 EngineCoreRequest？流式响应如何逐 token 返回？

### Step 12 工具调用与结构化输出
**为什么**：Agent 时代的输出治理层。**看**：`tool_parsers/abstract_tool_parser.py`、`tool_parsers/__init__.py`、`v1/structured_output/__init__.py`、`backend_xgrammar.py`。**自检**：logits bitmask 如何在采样前约束非法 token？工具调用如何从增量 token 流中被提取？

### Step 13 Rust 前端：高性能客户端与引擎共舞
**为什么**：新一代前端，为高密度进程管理而重写。**看**：`rust/src/engine-core-client/src/client.rs`、`transport.rs`、`protocol/sampling.rs`。**自检**：Rust 与 Python EngineCore 的 IPC 边界如何设计？对照 Step 3 的 core_client 体会同一协议的两种实现。

### Step 14 调优与基准：量化验证你的理解
**为什么**：学完架构后的实践工具箱。**看**：`cli/benchmark/serve.py`（TTFT/TPOT）、`throughput.py`、`startup.py`、`collect_env.py`。**自检**：改调度策略或 KV 配置后，如何用基准量化收益？——建议实际跑一轮 `vllm bench serve` 收尾。

## 5. 文件地图（按层速查）

### V1 引擎核心
| 文件 | 职责 |
|---|---|
| `vllm/v1/engine/async_llm.py` | 异步引擎前端，EngineClient 协议实现 |
| `vllm/v1/engine/core.py` | EngineCore 单步循环与独立进程变体 |
| `vllm/v1/engine/core_client.py` | Inproc/ZMQ/DP 客户端族 |
| `vllm/v1/engine/input_processor.py` | 输入校验与 EngineCoreRequest 构造 |
| `vllm/v1/engine/output_processor.py` | 引擎输出→RequestOutput 流式转换 |
| `vllm/v1/engine/detokenizer.py` | 增量反 tokenize 与 stop 检测 |
| `vllm/v1/request.py` | Request 状态机与 block 哈希 |
| `vllm/v1/sample/sampler.py` | 采样管线总入口 |
| `vllm/v1/structured_output/__init__.py` | 文法编译与 bitmask 管理 |

### 调度与 KV Cache
| 文件 | 职责 |
|---|---|
| `vllm/v1/core/sched/scheduler.py` | continuous batching 心脏（3123 行） |
| `vllm/v1/core/kv_cache_manager.py` | 调度器侧 KV 管理门面 |
| `vllm/v1/core/block_pool.py` | 物理块池+前缀缓存索引+LRU |
| `vllm/v1/core/kv_cache_utils.py` | 块哈希与分组策略（2486 行） |
| `vllm/v1/core/kv_cache_coordinator.py` | hybrid/无缓存等分组协调器 |
| `vllm/v1/kv_cache_interface.py` | KVCacheSpec 继承体系（Full/MLA/Sliding/Mamba） |

### GPU 执行 Worker
| 文件 | 职责 |
|---|---|
| `vllm/v1/worker/gpu_model_runner.py` | 7717 行执行总驱动 |
| `vllm/v1/worker/gpu_worker.py` | Worker 进程生命周期 |
| `vllm/v1/worker/gpu_input_batch.py` | InputBatch 批状态数据结构 |
| `vllm/v1/worker/gpu/cudagraph_utils.py` | CudaGraphManager 捕获/重放 |
| `vllm/v1/worker/worker_base.py` | Worker 抽象基类 |
| `vllm/v1/executor/uniproc_executor.py` | 单进程执行器（最简形态） |
| `vllm/v1/executor/multiproc_executor.py` | 多进程执行器 |
| `vllm/v1/worker/gpu/spec_decode/speculator.py` | 投机解码 speculator 基类 |

### 注意力后端
| 文件 | 职责 |
|---|---|
| `vllm/v1/attention/backend.py` | 后端抽象与 CommonAttentionMetadata |
| `vllm/v1/attention/backends/flash_attn.py` | 最常用 FlashAttention 后端 |
| `vllm/v1/attention/backends/flashinfer.py` | FlashInfer/TRT-LLM 集成 |
| `vllm/v1/attention/backends/triton_attn.py` | 纯 Triton 通用回退 |
| `vllm/v1/attention/backends/registry.py` | 后端注册表与懒加载 |
| `vllm/v1/attention/ops/triton_unified_attention.py` | 统一 prefill/decode Triton kernel |
| `vllm/v1/attention/backends/mla/flashattn_mla.py` | DeepSeek 式 MLA 代表实现 |

### 量化与 MoE
| 文件 | 职责 |
|---|---|
| `vllm/model_executor/layers/quantization/fp8.py` | FP8 核心（CUTLASS/DeepGemm） |
| `vllm/model_executor/layers/quantization/__init__.py` | 量化方法注册中心 |
| `vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors.py` | llm-compressor 入口 |
| `vllm/model_executor/layers/fused_moe/fused_moe.py` | Triton fused MoE kernel |
| `vllm/model_executor/layers/fused_moe/layer.py` | FusedMoE 工厂与专家映射 |
| `vllm/model_executor/layers/fused_moe/modular_kernel.py` | 通信+计算模块化 MoE 架构 |
| `vllm/model_executor/layers/fused_moe/routed_experts.py` | 路由专家容器与权重加载 |

### 模型实现与加载
| 文件 | 职责 |
|---|---|
| `vllm/model_executor/models/llama.py` | 最核心基线模型 |
| `vllm/model_executor/models/registry.py` | 架构名→实现懒加载映射 |
| `vllm/model_executor/models/interfaces.py` | 多模态/LoRA/PP 能力 Protocol |
| `vllm/model_executor/model_loader/default_loader.py` | safetensors 默认加载 |
| `vllm/model_executor/model_loader/weight_utils.py` | 权重迭代器与 loader 族（1585 行） |
| `vllm/model_executor/models/deepseek_v2.py` | MLA+MoE+DSA 代表（1983 行） |

### 分布式与编译
| 文件 | 职责 |
|---|---|
| `vllm/distributed/parallel_state.py` | TP/PP/DP/EP 进程组单例（2519 行） |
| `vllm/distributed/communication_op.py` | TP 通信原语公共 API |
| `vllm/distributed/device_communicators/custom_all_reduce.py` | IPC 自定义 allreduce |
| `vllm/distributed/kv_transfer/kv_connector/v1/base.py` | KV 连接器抽象基类 |
| `vllm/compilation/backends.py` | piecewise 编译后端 |
| `vllm/compilation/cuda_graph.py` | 编译场景 CUDA Graph 包装 |
| `vllm/compilation/decorators.py` | 模型接入 torch.compile 的装饰器 |

### 服务入口与共享设施
| 文件 | 职责 |
|---|---|
| `vllm/entrypoints/llm.py` | 离线推理顶级入口 |
| `vllm/entrypoints/chat_utils.py` | 对话消息解析（2223 行） |
| `vllm/entrypoints/openai/api_server.py` | OpenAI 兼容 server 主入口 |
| `vllm/entrypoints/cli/serve.py` | `vllm serve` 启动逻辑 |
| `vllm/sampling_params.py` | 全部采样选项定义 |
| `vllm/transformers_utils/config.py` | HF 配置加载中枢 |
| `vllm/platforms/interface.py` | Platform 抽象接口 |

## 6. 复杂度热点（新人绕行区）

图谱标记 complex 文件 1114 个。以下 15 个是"复杂度×重要性"最高的热点，**建议完成对应学习步骤后再碰**：

| 文件 | 行数 | 为什么复杂 | 何时才碰 |
|---|---|---|---|
| `v1/worker/gpu_model_runner.py` | 7717 | 115 个方法贯穿调度输出→kernel 启动→采样→异步回传全链路，横跨 CUDA Graph/投机解码/多模态 | 完成 Step 6 且要改执行行为时 |
| `v1/core/sched/scheduler.py` | 3123 | 调度策略+抢占+KV 预算+多模态 encoder+spec decode 元数据多重耦合 | 完成 Step 4/5 后 |
| `config/vllm.py` | 3036 | 2586 行聚合 dataclass，全部子配置的单一来源，改一处牵全仓 | 需要加配置项时（机械改法照抄现有子配置） |
| `engine/arg_utils.py` | 2935 | EngineArgs 聚合数百 CLI 参数，类型推导与组装逻辑繁重 | 加 CLI 参数时 |
| `v1/engine/core.py` | 2585 | EngineCore + 独立进程 + DP/MoE 弹性 Actor 变体，进程管理复杂 | 完成 Step 3 后 |
| `config/model.py` | 2525 | 82 个方法处理 dtype/max_len/HF config/多模态推导，兼容分支极多 | 模型配置报错排查时 |
| `distributed/parallel_state.py` | 2519 | 模块级全局单例状态机，全仓引用最广，误初始化即挂 | 完成 Step 9 后 |
| `v1/core/kv_cache_utils.py` | 2486 | 块哈希+分组策略（uniform/packed/hybrid）+内存估算，纯算法密度高 | 完成 Step 5 后 |
| `entrypoints/chat_utils.py` | 2223 | OpenAI 消息格式×多模态×工具调用×thinking 的全排列解析 | 改 chat 协议时 |
| `models/deepseek_v2.py` | 1983 | MLA+MoE+DSA 稀疏索引三合一，注册多个模型入口 | 学完 llama.py 再来 |
| `v1/engine/core_client.py` | 1887 | 进程内/ZMQ/DP/负载均衡多种客户端形态 | 完成 Step 3/13 后 |
| `layers/fused_moe/fused_moe.py` | 1859 | Triton MoE GEMM kernel 全量化格式支持+调优配置读取 | 做 MoE 性能工作时 |
| `v1/attention/backends/flash_attn.py` | 1834 | 级联注意力/DCP/encoder/RSWA 掩码等元数据构建分支极多 | 写新 attention 后端前 |
| `layers/linear.py` | 1779 | Column/Row/QKV 并行层族+weight_loader 体系，TP 语义核心 | 完成 Step 8 后 |
| `model_loader/weight_utils.py` | 1585 | 多种权重迭代器（mmap/多线程/流式）与 loader 变体 | 加载性能排查时 |

**通用建议**：这些文件改动前先跑 `git log -- <file>` 看近期变更节奏；用 debugger 在关键函数下断点跟一次真实请求，比通读源码高效得多。

---

*生成时间：2026-09-03 · 数据源：`.understand-anything/knowledge-graph.json`（analyzedAt 2026-09-03T16:28）*
