# DeepWiki vLLM 全量知识库索引

> 来源: https://deepwiki.com/vllm-project/vllm 抓取日期: 2026-09-02
> 共 62 页（13 章），100% 覆盖，覆盖率检查见 [_coverage-check.md](_coverage-check.md)

| 编号-页面 | 标题 | 中文摘要 | 大小 |
|---|---|---|---|
| [1-overview](1-overview.md) | Overview | vLLM 全景：是什么、系统架构总览、核心组件与请求处理流程 | 22KB |
| [2-configuration-and-initialization](2-configuration-and-initialization.md) | Configuration and Initialization | 配置与初始化总章：EngineArgs 到 VllmConfig 的完整配置链路 | 21KB |
| [2.1-argument-parsing-and-engineargs](2.1-argument-parsing-and-engineargs.md) | Argument Parsing and EngineArgs | EngineArgs 参数解析：CLI 参数定义、类型推断与默认值体系 | 18KB |
| [2.2-vllmconfig-and-specialized-configuration-objects](2.2-vllmconfig-and-specialized-configuration-objects.md) | VllmConfig and Specialized Configuration Objects | VllmConfig 与各专用配置对象（CacheConfig/ParallelConfig 等）的组织方式 | 18KB |
| [2.3-environment-variables-system](2.3-environment-variables-system.md) | Environment Variables System | 环境变量系统：VLLM_* 变量的读取、优先级与运行时覆盖 | 14KB |
| [2.4-compilation-configuration-and-optimization-levels](2.4-compilation-configuration-and-optimization-levels.md) | Compilation Configuration and Optimization Levels | torch.compile 编译配置与优化等级（0-3 级别差异） | 20KB |
| [3-engine-architecture](3-engine-architecture.md) | Engine Architecture | 引擎架构总章：EngineCore、请求生命周期、调度与 KV cache 的协作 | 18KB |
| [3.1-enginecore-and-client-apis](3.1-enginecore-and-client-apis.md) | EngineCore and Client APIs | EngineCore 与客户端 API：异步引擎核心与 LLM/AsyncLLM 入口 | 12KB |
| [3.2-request-lifecycle-and-state-management](3.2-request-lifecycle-and-state-management.md) | Request Lifecycle and State Management | 请求生命周期：从提交到完成的完整状态机管理 | 17KB |
| [3.3-scheduler-and-resource-allocation](3.3-scheduler-and-resource-allocation.md) | Scheduler and Resource Allocation | v1 调度器：每步调度决策、队列管理与 GPU 内存分配算法 | 18KB |
| [3.4-kv-cache-management-and-prefix-caching](3.4-kv-cache-management-and-prefix-caching.md) | KV Cache Management and Prefix Caching | KV cache 管理与前缀缓存：块池、分配策略与缓存命中 | 21KB |
| [3.5-input-and-output-processing](3.5-input-and-output-processing.md) | Input and Output Processing | 输入输出处理：tokenization、detokenization 与增量输出 | 19KB |
| [3.6-metrics-and-observability](3.6-metrics-and-observability.md) | Metrics and Observability | 指标与可观测性：Prometheus 指标、日志与 stat 输出 | 16KB |
| [4-model-execution-on-gpu](4-model-execution-on-gpu.md) | Model Execution on GPU | GPU 模型执行总章：ModelRunner、worker 与采样流水线 | 17KB |
| [4.1-gpumodelrunner](4.1-gpumodelrunner.md) | GPUModelRunner | GPUModelRunner：模型加载、execute_model 与输入准备的核心循环 | 21KB |
| [4.2-worker-and-executor-architecture](4.2-worker-and-executor-architecture.md) | Worker and Executor Architecture | Worker 与 Executor 架构：多卡多机的进程组织 | 14KB |
| [4.3-inputbatch-and-request-state-management](4.3-inputbatch-and-request-state-management.md) | InputBatch and Request State Management | InputBatch：GPU 侧批内请求状态与张量管理 | 19KB |
| [4.4-sampling-and-token-generation](4.4-sampling-and-token-generation.md) | Sampling and Token Generation | 采样与 token 生成：采样参数、温度/top-p 与惩罚实现 | 21KB |
| [4.5-speculative-decoding](4.5-speculative-decoding.md) | Speculative Decoding | 投机解码：draft-target 协作、接受率与 ngram/eagle 方法 | 23KB |
| [5-model-support-and-registration](5-model-support-and-registration.md) | Model Support and Registration | 模型支持与注册总章：注册表、架构检测与多模态 | 18KB |
| [5.1-model-registry-and-architecture-detection](5.1-model-registry-and-architecture-detection.md) | Model Registry and Architecture Detection | 模型注册表：架构自动检测、多架构映射与注册装饰器 | 20KB |
| [5.2-configuration-loading-and-parsing](5.2-configuration-loading-and-parsing.md) | Configuration Loading and Parsing | 模型配置加载：HF config 解析与 vLLM 侧字段映射 | 18KB |
| [5.3-transformers-modeling-backend](5.3-transformers-modeling-backend.md) | Transformers Modeling Backend | Transformers modeling 后端：直接复用 HF 模型代码的执行路径 | 20KB |
| [5.4-multimodal-model-support](5.4-multimodal-model-support.md) | Multimodal Model Support | 多模态模型支持：VLM 架构、encoder 输入与投影层 | 32KB |
| [5.5-multimodal-data-processing](5.5-multimodal-data-processing.md) | Multimodal Data Processing | 多模态数据处理：图像/视频/音频预处理管线与预算控制 | 19KB |
| [6-serving-apis](6-serving-apis.md) | Serving APIs | 服务 API 总章：OpenAI 兼容服务器与扩展能力 | 13KB |
| [6.1-openai-compatible-api-server](6.1-openai-compatible-api-server.md) | OpenAI-Compatible API Server | OpenAI 兼容 API 服务器：路由、生命周期与请求分发 | 27KB |
| [6.2-chat-utilities-and-message-processing](6.2-chat-utilities-and-message-processing.md) | Chat Utilities and Message Processing | Chat 工具：消息模板、对话历史与 chat formatting | 22KB |
| [6.3-tool-calling-and-structured-output](6.3-tool-calling-and-structured-output.md) | Tool Calling and Structured Output | 工具调用与结构化输出：function calling、guided decoding 与语法约束 | 26KB |
| [6.4-lora-adapter-management](6.4-lora-adapter-management.md) | LoRA Adapter Management | LoRA 适配器管理：动态加载、热切换与权重服务 | 18KB |
| [6.5-rust-frontend-](6.5-rust-frontend-.md) | Rust Frontend (vllm-frontend-rs) | Rust 前端：HTTP 解析/响应的高性能 Rust 组件 | 21KB |
| [7-quantization-and-moe-optimizations](7-quantization-and-moe-optimizations.md) | Quantization and MoE Optimizations | 量化与 MoE 优化总章 | 21KB |
| [7.1-quantization-methods-overview](7.1-quantization-methods-overview.md) | Quantization Methods Overview | 量化方法总览：各类量化格式与注册机制 | 27KB |
| [7.2-fp8-and-low-precision-quantization](7.2-fp8-and-low-precision-quantization.md) | FP8 and Low-Precision Quantization | FP8 与低精度量化：缩放方案、校准与内核选择 | 26KB |
| [7.3-fusedmoe-layer-architecture](7.3-fusedmoe-layer-architecture.md) | FusedMoE Layer Architecture | FusedMoE 层架构：专家路由、分组 GEMM 与 kernel 融合 | 34KB |
| [7.4-moe-quantization-and-backend-selection](7.4-moe-quantization-and-backend-selection.md) | MoE Quantization and Backend Selection | MoE 量化与后端选择：专家权重量化与 Triton/CUDA 后端 | 26KB |
| [8-attention-backends](8-attention-backends.md) | Attention Backends | 注意力后端总章 | 19KB |
| [8.1-attention-backend-selection](8.1-attention-backend-selection.md) | Attention Backend Selection | 注意力后端选择机制：按平台/模型/特性自动挑选 | 13KB |
| [8.2-flashattention-and-flashinfer](8.2-flashattention-and-flashinfer.md) | FlashAttention and FlashInfer | FlashAttention 与 FlashInfer 后端实现对比 | 24KB |
| [8.3-mla-and-specialized-attention](8.3-mla-and-specialized-attention.md) | MLA and Specialized Attention | MLA 与专用注意力：DeepSeek MLA、滑窗、前缀无关注意力 | 26KB |
| [8.4-rocm-and-platform-specific-attention](8.4-rocm-and-platform-specific-attention.md) | ROCm and Platform-Specific Attention | ROCm 与平台专用注意力后端 | 21KB |
| [9-distributed-execution](9-distributed-execution.md) | Distributed Execution | 分布式执行总章 | 15KB |
| [9.1-parallelism-strategies](9.1-parallelism-strategies.md) | Parallelism Strategies | 并行策略：TP/PP/DP/EP 组合与并行配置 | 16KB |
| [9.2-communication-infrastructure](9.2-communication-infrastructure.md) | Communication Infrastructure | 通信基础设施：NCCL/自定义 allreduce、消息协调器 | 22KB |
| [9.3-multi-process-engine-management](9.3-multi-process-engine-management.md) | Multi-Process Engine Management | 多进程引擎管理：worker 进程启动、健康监控与故障恢复 | 15KB |
| [9.4-kv-cache-transfer-and-disaggregated-serving](9.4-kv-cache-transfer-and-disaggregated-serving.md) | KV Cache Transfer and Disaggregated Serving | KV cache 迁移与 PD 分离：KVConnector 与 prefill/decode 分离部署 | 46KB |
| [10-platform-support](10-platform-support.md) | Platform Support | 平台支持总章：硬件抽象层 | 15KB |
| [10.1-platform-abstraction-layer](10.1-platform-abstraction-layer.md) | Platform Abstraction Layer | 平台抽象层：Platform 接口与设备能力协商 | 16KB |
| [10.2-cuda-platform](10.2-cuda-platform.md) | CUDA Platform | CUDA 平台实现：NVIDIA 特有初始化与检测 | 14KB |
| [10.3-rocm-platform](10.3-rocm-platform.md) | ROCm Platform | ROCm 平台实现：AMD 支持路径 | 17KB |
| [10.4-xpu-cpu-and-tpu-platforms](10.4-xpu-cpu-and-tpu-platforms.md) | XPU, CPU, and TPU Platforms | XPU/CPU/TPU 平台实现 | 20KB |
| [11-build-system-and-deployment](11-build-system-and-deployment.md) | Build System and Deployment | 构建与部署总章 | 19KB |
| [11.1-docker-multi-stage-build](11.1-docker-multi-stage-build.md) | Docker Multi-Stage Build | Docker 多阶段构建：镜像分层与缓存策略 | 26KB |
| [11.2-dependency-management](11.2-dependency-management.md) | Dependency Management | 依赖管理：requirements 分层与版本锁定 | 17KB |
| [11.3-build-variants-and-configuration](11.3-build-variants-and-configuration.md) | Build Variants and Configuration | 构建变体与配置：CUDA 版本、架构矩阵与开关 | 19KB |
| [11.4-runtime-jit-compilation](11.4-runtime-jit-compilation.md) | Runtime JIT Compilation | 运行时 JIT 编译：torch.compile 与 CUDA graph 捕获 | 17KB |
| [12-testing-and-cicd](12-testing-and-cicd.md) | Testing and CI/CD | 测试与 CI/CD 总章 | 14KB |
| [12.1-test-organization-and-infrastructure](12.1-test-organization-and-infrastructure.md) | Test Organization and Infrastructure | 测试组织：目录结构、fixture 与分类体系 | 13KB |
| [12.2-buildkite-ci-pipelines](12.2-buildkite-ci-pipelines.md) | Buildkite CI Pipelines | Buildkite CI 流水线：阶段划分与硬件池调度 | 14KB |
| [12.3-hardware-specific-testing](12.3-hardware-specific-testing.md) | Hardware-Specific Testing | 硬件专项测试：多平台 nightly 与回归 | 20KB |
| [12.4-model-correctness-validation](12.4-model-correctness-validation.md) | Model Correctness Validation | 模型正确性验证：baseline 对比与 evals 体系 | 18KB |
| [13-glossary](13-glossary.md) | Glossary | 术语表：核心概念与缩略语定义 | 38KB |

## 相关子项目（overview 级摘要，见 related/）

vllm-omni、semantic-router、aibrix、llm-compressor、vllm-ascend、production-stack、vllm-metal、guidellm、recipes、speculators、router、vllm-skills；
全部 47 仓库清单见 [related/_repo-list.md](related/_repo-list.md)。
