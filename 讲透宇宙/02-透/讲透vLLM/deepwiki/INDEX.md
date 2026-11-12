# DeepWiki vLLM 全量知识库索引

> 来源: https://deepwiki.com/vllm-project/vllm（MCP 通道 mcp.deepwiki.com 抓取）· 抓取日期: 2026-10-28
> 共 74 页（13 章），100% 覆盖（全层级对账 TRUE_100），覆盖率检查见 [_coverage-check.md](_coverage-check.md)
> 本次为 2026-09-02 版全量刷新：56 页内容全部更新、18 页新增（🆕）、6 页改名重组；对应源码基线 `06e172b5cf`（2026-10-28）

| 编号-页面 | 标题 | 中文摘要 | 大小 |
|---|---|---|---|
| [1-overview](1-overview.md) | Overview | vLLM 全景导向页：V1 引擎高层请求路径（EngineCore 统筹模型执行/KV cache/调度器装配）与工程师会遇到的仓库区域地图 | 14KB |
| [1.1-getting-started](1.1-getting-started-and-installation.md) 🆕 | Getting Started and Installation | 安装选项：平台专属 Python 依赖、源码构建配置、Docker 构建输入，及其对硬件要求/快速上手的确立与不确立边界 | 20KB |
| [1.2-examples](1.2-examples-and-usage-patterns.md) 🆕 | Examples and Usage Patterns | examples/ 全景技术导览：离线批推理/在线服务/PD 分离/pooling/RL 权重传输/语音/工具调用/可观测面板与代码实体映射 | 25KB |
| [1.3-model-recipes](1.3-model-recipes-and-deployment-guides.md) 🆕 | Model Recipes and Deployment Guides | 模型部署 recipes 与模型支持/测试注册表的区分：recipes/models 的支持-配置-测试注册侧关系 | 17KB |
| [2-configuration-and-initialization](2-configuration-and-initialization.md) | Configuration and Initialization | 配置系统总章（父页精简为地图）：输入→根 VllmConfig、专用配置分域、编译与环境变量位置 | 7KB |
| [2.1-argument-parsing](2.1-argument-parsing-and-engineargs.md) | Argument Parsing and EngineArgs | EngineArgs 数据class体系：CLI/Python API 输入的解析、校验、转换到统一 VllmConfig | 19KB |
| [2.2-vllmconfig](2.2-vllmconfig-and-specialized-configuration-objects.md) | VllmConfig and Specialized Config Objects | VllmConfig 根对象与专用子配置：ModelConfig/ParallelConfig/CacheConfig/SchedulerConfig 等结构与校验逻辑 | 19KB |
| [2.3-environment-variables](2.3-environment-variables-system.md) | Environment Variables System | vllm/envs.py 集中环境变量注册表：访问机制、辅助工具与 VLLM_* 变量技术参考（本轮大幅扩容+10KB） | 28KB |
| [2.4-compilation-config](2.4-compilation-configuration-and-optimization-levels.md) | Compilation Configuration | 编译控制：CompilationMode/CUDAGraphMode/PassConfig、编译器选择与缓存、Inductor 图 pass 与 vLLM IR 算子 | 21KB |
| [3-engine-architecture](3-engine-architecture.md) | Engine Architecture | V1 引擎核心总章：EngineCore 内层执行循环、客户端 API 分层、请求生命周期、调度、KV cache 与可观测 | 10KB |
| [3.1-enginecore](3.1-enginecore-and-client-apis.md) | EngineCore and Client APIs | EngineCore 中央执行引擎与 EngineCoreClient IPC 抽象（多进程策略），V1 引擎的地基（本轮+9KB） | 21KB |
| [3.2-request-lifecycle](3.2-request-lifecycle-and-state-management.md) | Request Lifecycle and State Management | 请求表示与路由：EngineCoreRequest 传输对象、InputProcessor 边界、客户端接口 | 18KB |
| [3.3-scheduler](3.3-scheduler-and-resource-allocation.md) | Scheduler and Resource Allocation | V1 调度器配置与资源分配边界：准入限制、每迭代 token 预算、KV cache 管理与 AsyncScheduler 变体 | 18KB |
| [3.4-kv-cache](3.4-kv-cache-management-and-prefix-caching.md) | KV Cache Management and Prefix Caching | KVCacheManager 连接调度器与 cache 协调：cache group、block 元数据、前缀哈希查找与事件发布 | 22KB |
| [3.5-input-output](3.5-input-and-output-processing.md) | Input and Output Processing | InputProcessor/renderer 配置/prompt 处理、逐请求输出状态、logprob 表示与流式响应异步收集 | 21KB |
| [3.6-metrics](3.6-metrics-and-observability.md) | Metrics and Observability | 可观测接口：引擎统计与 logger、tracing、profiling、Prometheus 生命周期钩子 | 18KB |
| [4-model-execution-on-gpu](4-model-execution-on-gpu.md) | Model Execution on GPU | GPU 模型执行总章：worker 侧执行连接调度批与模型计算（GPUModelRunner/Worker/执行阶段） | 14KB |
| [4.1-gpumodelrunner](4.1-gpumodelrunner.md) | GPUModelRunner | GPUModelRunner 统筹 GPU 侧执行：批准备/前向调用/注意力设施/KV 状态/采样与 pooling 路由/CUDA graph（+7KB） | 27KB |
| [4.2-worker-executor](4.2-worker-and-executor-architecture.md) | Worker and Executor Architecture | v1 executor 协调 worker 初始化与执行：UniProcExecutor、MultiprocExecutor 初始化路径、GPU Worker 设备装配与显存 profiling | 19KB |
| [4.3-inputbatch](4.3-inputbatch-and-request-state-management.md) | InputBatch and Request State Management | CachedRequestState 与 InputBatch：GPU worker 批数据结构、逐请求状态与 KV block 表/执行形状 | 24KB |
| [4.4-sampling](4.4-sampling-and-token-generation.md) | Sampling and Token Generation | V1 GPU 采样路径：Sampler 逐请求采样状态、logits processor、平台适配 top-k/top-p、结构化输出 grammar 约束 | 25KB |
| [4.5-speculative-decoding](4.5-speculative-decoding.md) | Speculative Decoding | 投机解码：proposer/verifier 角色、token 与概率数据、拒绝采样概念与接受信号（+6KB） | 28KB |
| [4.6-determinism](4.6-determinism-and-batch-invariance.md) 🆕 | Determinism and Batch Invariance | 批不变性模式（beta）：确定性执行措施、Triton 内核实现、调优 matmul 配置与 determinism 测试 | 17KB |
| [5-model-support](5-model-support-and-registration.md) | Model Support and Registration | 模型标识→HF 配置→模型实现/运行时配置/支持任务的连接总章 | 11KB |
| [5.1-model-registry](5.1-model-registry-and-architecture-detection.md) | Model Registry and Architecture Detection | HF 架构名与模型实现条目关联、配置/架构注册表、能力查询接口 | 19KB |
| [5.2-config-weight-loading](5.2-configuration-loading-and-weight-loading.md) | Configuration Loading and Weight Loading | 模型配置/checkpoint 选择→初始化→权重加载→后处理→layerwise 重载→IPC 权重缓存全路径（原"解析"页扩展改名） | 25KB |
| [5.3-transformers-backend](5.3-transformers-modeling-backend.md) | Transformers Modeling Backend | HF 模型包装后端：任务专属 mixin 组合（生成/MoE/多模态/embedding/分类）、层与注意力适配 | 26KB |
| [5.4-multimodal-support](5.4-multimodal-model-support.md) | Multimodal Model Support | SupportsMultiModal 接口、视觉语言/全模态实现选例、encoder CUDA Graph 支持 | 29KB |
| [5.5-multimodal-processing](5.5-multimodal-data-processing.md) | Multimodal Data Processing | 多模态数据流：MultiModalDataDict→解析→模型专属处理→媒体解码→encoder 执行（+8KB） | 27KB |
| [5.6-vendor-models](5.6-vendor-model-implementations-vllm-models.md) 🆕 | Vendor Model Implementations (vllm/models) | vllm/models 厂商/硬件特化模型实现：DeepSeek V3.2/V4/V4.1、Kimi K3、MiniMax M3（qwen4_exp/glm5next/step5 等点名未展开） | 29KB |
| [5.7-hybrid-attention](5.7-hybrid-and-linear-attention-models.md) 🆕 | Hybrid and Linear-Attention Models | 混合 SSM/线性注意力：Gated DeltaNet、Mamba/Mamba2、短卷积、递归状态 cache 与 metadata builder（Qwen3.5/Nemotron-H） | 25KB |
| [5.8-pooling-models](5.8-pooling-embedding-and-classification-models.md) 🆕 | Pooling, Embedding and Classification Models | pooling 模型支持：序列级/token 级任务、pooler 行为、score/rerank 输入与正确性测试 | 23KB |
| [6-serving-apis](6-serving-apis.md) | Serving APIs | 服务层总章：HTTP 接口入口、请求渲染路径；legacy api_server 弃用声明（launcher 入口为正身） | 13KB |
| [6.1-openai-api-server](6.1-openai-compatible-api-server.md) | OpenAI-Compatible API Server | Python HTTP 服务层：协议模型↔handler↔引擎/renderer 连接、endpoint 家族地图 | 28KB |
| [6.2-chat-utilities](6.2-chat-utilities-and-message-processing.md) | Chat Utilities and Message Processing | 聊天消息与 prompt 渲染路径：parse_chat_messages、chat template 配置、tokenizer 选择、BaseRenderer 体系 | 18KB |
| [6.3-tool-calling-parsers](6.3-tool-calling-reasoning-parsers-and-structured-output.md) | Tool Calling, Reasoning Parsers and Structured Output | 输出→内容/reasoning/tool call 解析、解析器注册组合、Responses 的 Harmony/MCP 工具流、grammar 约束编译（扩展改名） | 28KB |
| [6.4-lora](6.4-lora-adapter-management.md) | LoRA Adapter Management | LoRA 配置与运行时管理：加载卸载 API、WorkerLoRAManager、层选择、Punica/fused MoE LoRA | 20KB |
| [6.5-rust-frontend](6.5-rust-frontend-vllm-frontend-rs.md) | Rust Frontend (vllm-frontend-rs) | Rust 前端 HTTP/gRPC 服务层：crate 组成（serving/chat/text/llm/tokenizer/parser/engine-core transport/mock-engine/metrics）与 EngineCoreClient 连接 | 25KB |
| [6.6-scale-out-tito](6.6-scale-out-and-token-in-token-out-serving.md) 🆕 | Scale-Out and Token-in-Token-out Serving | 扩展服务路径：ServingTokens 的 token-in-token-out 生成、ServingDerender/OnlineDerenderer 反渲染回聊天/补全响应 | 22KB |
| [7-quantization-moe](7-quantization-and-moe-optimizations.md) | Quantization and MoE Optimizations | 量化配置→层方法/内核选择、FusedMoE 管线（路由+专家执行）总章 | 12KB |
| [7.1-quantization-overview](7.1-quantization-methods-overview.md) | Quantization Methods Overview | 量化概念与入口：方法注册表、FP8/INT8 描述子与内核、GPTQ/AWQ、compressed-tensors/Quark、在线量化、linear 内核导入层（+9KB） | 36KB |
| [7.2-fp8-low-precision](7.2-fp8-and-low-precision-quantization.md) | FP8 and Low-Precision Quantization | FP8/block/group scaling、MXFP4/NVFP4、DeepGEMM 集成与低精度 linear 内核选择 | 33KB |
| [7.3-fusedmoe](7.3-fusedmoe-layer-architecture.md) | FusedMoE Layer Architecture | 融合 MoE 执行架构：模块化内核接口、专家计算、backend 选择、experts/oracle/runner 组件分工 | 26KB |
| [7.4-moe-backend-selection](7.4-moe-quantization-and-backend-selection.md) | MoE Quantization and Backend Selection | MoE 量化与 routed-expert 执行：FP8/MXFP4 backend oracle、CUTLASS/DeepGemm/FlashInfer/TRTLLM/ROCm AITER 家族与 EP 交互 | 26KB |
| [7.5-custom-kernels](7.5-custom-kernels-and-c-cuda-extensions.md) 🆕 | Custom Kernels and C++/CUDA Extensions | 原生扩展边界：csrc/ 组织、PyTorch 算子注册与 stable ABI、CMake 入口、外部/JIT 内核库与内核 warmup | 22KB |
| [8-attention-backends](8-attention-backends.md) | Attention Backends | 注意力后端总章：AttentionBackendEnum 与注册表（标准/MLA/稀疏/平台专属） | 11KB |
| [8.1-backend-selection](8.1-attention-backend-selection.md) | Attention Backend Selection | 后端表示与选择机制：硬件/模型属性约束、Attention 层连接模型执行与后端实现（+11KB） | 24KB |
| [8.2-flashattention-flashinfer-flex](8.2-flashattention-flashinfer-and-flexattention.md) | FlashAttention, FlashInfer and FlexAttention | FA/FlashInfer/Triton Attention/FlexAttention 实现：backend 接口、metadata 与 KV cache、内核分发与编译（扩展改名收编 FlexAttention） | 25KB |
| [8.3-mla](8.3-mla-and-specialized-attention.md) | MLA and Specialized Attention | MLA 计算路径、稀疏 MLA 与 DeepSeek V3.2/V4 indexer 组件、混合模型注意力配置边界 | 26KB |
| [8.4-rocm-platform-attention](8.4-rocm-and-platform-specific-attention.md) | ROCm and Platform-Specific Attention | ROCm 后端与 AITER 集成、平台专属选择、CPU 注意力（Python metadata+C++ 内核）、XPU sparse MLA 注册 | 24KB |
| [9-distributed-execution](9-distributed-execution.md) | Distributed Execution | 分布式执行总章：并行进程组、设备通信与多进程服务/cache 移动/offload/权重更新邻接子系统 | 10KB |
| [9.1-parallelism](9.1-parallelism-strategies.md) | Parallelism Strategies | TP/PP/EP/DP/CP 进程组表示与使用，EPLB 与 Elastic EP 的专家重平衡 | 22KB |
| [9.2-communication](9.2-communication-infrastructure.md) | Communication Infrastructure | 分布式组状态、CUDA 设备通信、MoE all2all dispatch/combine、symmetric-memory、共享内存广播、all-reduce/RMSNorm 融合 | 23KB |
| [9.3-multiproc-engine](9.3-multi-process-engine-management.md) | Multi-Process Engine Management | 前端客户端↔engine-core 进程连接、本地 worker/Ray 基础设施、DP 客户端协调与负载均衡模式 | 19KB |
| [9.4-kv-transfer-disagg](9.4-kv-cache-transfer-and-disaggregated-serving.md) | KV Cache Transfer and Disaggregated Serving | V1 KV connector 接口与实现：MultiConnector、encoder-cache 传输、NIXL/LMCache/Mooncake/MoRIIO/hf3fs/flexkv 与 connector 指标 | 34KB |
| [9.5-kv-offloading](9.5-kv-offloading-and-tiering.md) 🆕 | KV Offloading and Tiering | KV offload 子系统：offload 调度器与管理器、CPU/多级存储配置、simple_kv_offload 独立路径与 cache 保留策略 | 30KB |
| [9.6-weight-transfer-rl](9.6-weight-transfer-and-rl-integration.md) 🆕 | Weight Transfer and RL Integration | 权重传输引擎：layerwise reload 机制、dense NCCL 引擎、异步 RL 示例（IPC/sparse NCCL 经测试套件识别） | 17KB |
| [10-platform-support](10-platform-support.md) | Platform Support | 平台层总章：共享 Platform 接口与硬件实现（身份/设备类型/分布式后端/量化支持表示） | 10KB |
| [10.1-platform-abstraction](10.1-platform-abstraction-layer.md) | Platform Abstraction Layer | Platform 抽象层：接口与能力类型、CUDA/ROCm/XPU/CPU 实现细节（+6KB） | 22KB |
| [10.2-cuda-platform](10.2-cuda-platform.md) | CUDA Platform | CUDA 实现：NVML 装配、无状态设备计数、compute-capability 注意力后端优先级、CuMemAllocator 标签内存池 | 18KB |
| [10.3-rocm-platform](10.3-rocm-platform.md) | ROCm Platform | ROCm 平台：设备可见性、AMD GPU 识别、GCN 架构查询、AITER 初始化与 ROCm Docker/CI 入口 | 17KB |
| [10.4-xpu-cpu-tpu](10.4-xpu-cpu-and-tpu-platforms.md) | XPU, CPU, and TPU Platforms | Intel XPU 执行、CPU 内核与 worker 基建、TPU 代码指针（+13KB 大扩容） | 32KB |
| [11-build-deployment](11-build-system-and-deployment.md) | Build System and Deployment | 构建/打包/安装/发布总章：Docker 构建、依赖与平台变体、安装路径与运行时内核准备 | 10KB |
| [11.1-docker-build](11.1-docker-multi-stage-build.md) | Docker Multi-Stage Build | Docker 构建结构：CUDA/CPU/XPU 三 Dockerfile 的命名 stage、产物交接、镜像变体与构建优化 | 21KB |
| [11.2-dependency-management](11.2-dependency-management.md) | Dependency Management | 运行时/测试依赖声明、原生构建的 PyTorch 兼容检查、预编译 Rust 扩展检测、Python 打包与 CMake 连接 | 20KB |
| [11.3-build-variants](11.3-build-variants-and-configuration.md) | Build Variants and Configuration | 构建变体：CUDA/ROCm/XPU/CPU、CPU nightly PyTorch、ARM64/s390x 目标与 Docker 构建选项 | 24KB |
| [11.4-runtime-jit](11.4-runtime-jit-compilation.md) | Runtime JIT Compilation | 运行时内核编译与 warmup：FlashInfer 可用性检查、DeepGEMM JIT、worker warmup 入口、CuteDSL NVFP4 MoE 准备 | 23KB |
| [12-testing-ci-cd](12-testing-and-ci-cd.md) | Testing and CI/CD | 测试总章：覆盖面、CI 组织、硬件感知执行与正确性验证（Buildkite test-area 体系） | 12KB |
| [12.1-test-org](12.1-test-organization-and-infrastructure.md) | Test Organization and Infrastructure | 测试组织：共享 pytest 基建、VllmRunner/HfRunner 模型对照、模型专属测试设置注册 | 19KB |
| [12.2-buildkite-ci](12.2-buildkite-ci-pipelines.md) | Buildkite CI Pipelines | Buildkite 测试配置：test-area 功能组、step 设置、源文件触发、分片、AMD 镜像（+11KB） | 25KB |
| [12.3-hardware-testing](12.3-hardware-specific-testing.md) | Hardware-Specific Testing | 硬件专属 CI：执行脚本、测试定义、命令处理与 AMD/ROCm、Intel XPU、CPU 平台覆盖 | 19KB |
| [12.4-correctness-benchmark](12.4-model-correctness-validation-and-benchmarking.md) | Model Correctness Validation and Benchmarking | 正确性检查与基准入口：LM Eval 作业、GSM8K 检查、模型/引擎正确性作业、serve.py 在线服务基准（扩展改名） | 20KB |
| [12.5-developer-tooling](12.5-developer-tooling-and-governance.md) 🆕 | Developer Tooling and Governance | 开发者工具与治理：pre-commit、mypy、GitHub Actions、Mergify、CODEOWNERS、agent skills（.agents/.claude）与贡献模型 | 13KB |
| [13-glossary](13-glossary.md) | Glossary | 术语表：代码库专属术语/黑话/缩写/领域概念，连接高层架构与具体代码实体 | 21KB |
