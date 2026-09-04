# DeepWiki sgl-project/sglang 全量索引（110/110 页）

> 抓取日期：2026-09-03 | DeepWiki 索引基线：commit `94183a8d`（2026-08-27）| 本地代码基线：`ec075d8bc`
> 来源：https://deepwiki.com/sgl-project/sglang | 覆盖率验证见 [_coverage-check.md](_coverage-check.md)
> 用法：每页 = DeepWiki 对应页面的完整中文可用抓取（含源码行号引用），点文件名阅读。

## 目录

| 章 | 主题 | 页数 |
|----|------|------|
| 1 | [概览](#1-概览) | 3 |
| 2 | [安装与部署](#2-安装与部署) | 5 |
| 3 | [核心服务器架构](#3-核心服务器架构) | 4 |
| 4 | [请求处理流水线](#4-请求处理流水线) | 5 |
| 5 | [内存管理与 KV Cache](#5-内存管理与-kv-cache) | 5 |
| 6 | [分布式执行策略](#6-分布式执行策略) | 5 |
| 7 | [模型配置与加载](#7-模型配置与加载) | 4 |
| 8 | [MoE 与 DeepSeek 模型](#8-moe-与-deepseek-模型) | 5 |
| 9 | [量化系统](#9-量化系统) | 5 |
| 10 | [模型执行层](#10-模型执行层) | 7 |
| 11 | [sgl-kernel 内核库](#11-sgl-kernel-内核库) | 7 |
| 12 | [投机解码](#12-投机解码) | 4 |
| 13 | [API 接口](#13-api-接口) | 5 |
| 14 | [环境与配置](#14-环境与配置) | 3 |
| 15 | [测试与开发](#15-测试与开发) | 5 |
| 16 | [发布与部署自动化](#16-发布与部署自动化) | 4 |
| 17 | [输出生成与采样](#17-输出生成与采样) | 5 |
| 18 | [多模态与视觉语言模型](#18-多模态与视觉语言模型) | 4 |
| 19 | [高级特性](#19-高级特性) | 8 |
| 20 | [SGLang Router](#20-sglang-router-sgl-router) | 3 |
| 21 | [SGLang Model Gateway](#21-sglang-model-gateway-sgl-model-gateway) | 4 |
| 22 | [扩散与多模态生成](#22-扩散与多模态生成-multimodal_gen) | 4 |
| 23 | [SGLang 前端语言](#23-sglang-前端语言) | 3 |
| 24 | [术语表](#24-术语表) | 3 |

---

## 1. 概览

- [1-overview.md](1-overview.md) — Overview：SGLang 定位/多进程架构/请求生命周期/核心组件
- [1.1-repository-layout-major-packages-and-entry-points.md](1.1-repository-layout-major-packages-and-entry-points.md) — 仓库布局、主要包与入口点
- [1.2-core-concepts-and-dataflow-(tokenizer-scheduler-modelrunner-detokenizer).md](1.2-core-concepts-and-dataflow-(tokenizer-scheduler-modelrunner-detokenizer).md) — 核心概念与数据流（Tokenizer → Scheduler → ModelRunner → Detokenizer）

## 2. 安装与部署

- [2-installation-and-deployment.md](2-installation-and-deployment.md) — 章节总览
- [2.1-installation-methods.md](2.1-installation-methods.md) — 安装方式（pip/docker/源码；各硬件平台 wheel 矩阵）
- [2.2-hardware-platform-configuration.md](2.2-hardware-platform-configuration.md) — 硬件平台配置（CUDA/ROCm/XPU/CPU/NPU）
- [2.3-docker-deployment.md](2.3-docker-deployment.md) — Docker 部署
- [2.4-multi-node-and-distributed-deployment.md](2.4-multi-node-and-distributed-deployment.md) — 多节点与分布式部署（Ray 集群）

## 3. 核心服务器架构

- [3-core-server-architecture.md](3-core-server-architecture.md) — 章节总览
- [3.1-multi-process-architecture-and-ipc.md](3.1-multi-process-architecture-and-ipc.md) — 多进程架构与 IPC（ZMQ 拓扑）
- [3.2-server-configuration-(serverargs).md](3.2-server-configuration-(serverargs).md) — 服务器配置（ServerArgs 全参数）
- [3.3-tokenizermanager-and-detokenizermanager.md](3.3-tokenizermanager-and-detokenizermanager.md) — TokenizerManager 与 DetokenizerManager

## 4. 请求处理流水线

- [4-request-processing-pipeline.md](4-request-processing-pipeline.md) — 章节总览
- [4.1-request-lifecycle-and-data-structures.md](4.1-request-lifecycle-and-data-structures.md) — 请求生命周期与数据结构（Req/ScheduleBatch/ForwardBatch）
- [4.2-scheduler-and-batch-formation.md](4.2-scheduler-and-batch-formation.md) — Scheduler 与组批
- [4.3-model-execution-and-forward-pass.md](4.3-model-execution-and-forward-pass.md) — 模型执行与前向
- [4.4-cuda-graphs-and-performance-optimizations.md](4.4-cuda-graphs-and-performance-optimizations.md) — CUDA Graphs 与性能优化

## 5. 内存管理与 KV Cache

- [5-memory-management-and-kv-cache.md](5-memory-management-and-kv-cache.md) — 章节总览
- [5.1-memory-pools-and-token-to-kv-mapping.md](5.1-memory-pools-and-token-to-kv-mapping.md) — 内存池与 token→KV 映射（ReqToTokenPool/TokenToKVPoolAllocator）
- [5.2-radixcache-and-prefix-sharing.md](5.2-radixcache-and-prefix-sharing.md) — RadixCache 与前缀共享
- [5.3-hicache-multi-tier-storage.md](5.3-hicache-multi-tier-storage.md) — HiCache 多级存储（GPU→CPU→SSD）
- [5.4-storage-backends-and-transfer-optimization.md](5.4-storage-backends-and-transfer-optimization.md) — 存储后端与传输优化

## 6. 分布式执行策略

- [6-distributed-execution-strategies.md](6-distributed-execution-strategies.md) — 章节总览
- [6.1-tensor-and-pipeline-parallelism.md](6.1-tensor-and-pipeline-parallelism.md) — 张量并行与流水线并行
- [6.2-expert-parallelism-for-moe-models.md](6.2-expert-parallelism-for-moe-models.md) — MoE 专家并行
- [6.3-data-parallelism-and-dp-attention.md](6.3-data-parallelism-and-dp-attention.md) — 数据并行与 DP Attention
- [6.4-prefill-decode-disaggregation.md](6.4-prefill-decode-disaggregation.md) — Prefill-Decode 分离

## 7. 模型配置与加载

- [7-model-configuration-and-loading.md](7-model-configuration-and-loading.md) — 章节总览
- [7.1-modelconfig-system.md](7.1-modelconfig-system.md) — ModelConfig 系统
- [7.2-model-loading-pipeline.md](7.2-model-loading-pipeline.md) — 模型加载流水线
- [7.3-supported-model-architectures.md](7.3-supported-model-architectures.md) — 支持的模型架构（200+ 家族）

## 8. MoE 与 DeepSeek 模型

- [8-moe-and-deepseek-models.md](8-moe-and-deepseek-models.md) — 章节总览
- [8.1-moe-layer-architecture.md](8.1-moe-layer-architecture.md) — MoE 层架构（TopK 路由/FusedMoE）
- [8.2-deepseek-architecture-and-mla.md](8.2-deepseek-architecture-and-mla.md) — DeepSeek 架构与 MLA
- [8.3-expert-routing-and-token-dispatch.md](8.3-expert-routing-and-token-dispatch.md) — 专家路由与 token 分发（DeepEP）
- [8.4-moe-quantization-and-optimization.md](8.4-moe-quantization-and-optimization.md) — MoE 量化与优化

## 9. 量化系统

- [9-quantization-system.md](9-quantization-system.md) — 章节总览
- [9.1-quantization-configuration-and-registry.md](9.1-quantization-configuration-and-registry.md) — 量化配置与注册表
- [9.2-fp8-and-modelopt-quantization.md](9.2-fp8-and-modelopt-quantization.md) — FP8 与 ModelOpt 量化
- [9.3-fp4-and-mxfp4-quantization.md](9.3-fp4-and-mxfp4-quantization.md) — FP4 与 MXFP4 量化
- [9.4-int8-and-other-quantization-methods.md](9.4-int8-and-other-quantization-methods.md) — INT8 与其他量化（AWQ/GPTQ/Marlin）

## 10. 模型执行层

- [10-model-execution-layers.md](10-model-execution-layers.md) — 章节总览
- [10.1-multi-platform-layer-abstraction.md](10.1-multi-platform-layer-abstraction.md) — 多平台层抽象
- [10.2-attention-mechanisms-and-backends.md](10.2-attention-mechanisms-and-backends.md) — 注意力机制与后端（RadixAttention/FlashAttention/FlashInfer/MLA）
- [10.3-positional-embeddings.md](10.3-positional-embeddings.md) — 位置编码（RoPE 等）
- [10.4-normalization-and-activation-layers.md](10.4-normalization-and-activation-layers.md) — 归一化与激活层
- [10.5-linear-layers-and-distributed-communication.md](10.5-linear-layers-and-distributed-communication.md) — 线性层与分布式通信
- [10.6-hybrid-and-linear-attention-models.md](10.6-hybrid-and-linear-attention-models.md) — 混合与线性注意力模型（Mamba/线性 attention）

## 11. sgl-kernel 内核库

- [11-sgl-kernel-library.md](11-sgl-kernel-library.md) — 章节总览
- [11.1-build-system-and-multi-architecture-support.md](11.1-build-system-and-multi-architecture-support.md) — 构建系统与多架构支持
- [11.2-kernel-categories-and-implementations.md](11.2-kernel-categories-and-implementations.md) — 内核类别与实现
- [11.3-quantization-kernels.md](11.3-quantization-kernels.md) — 量化内核
- [11.4-moe-fused-kernels.md](11.4-moe-fused-kernels.md) — MoE 融合内核
- [11.5-third-party-library-integration.md](11.5-third-party-library-integration.md) — 第三方库集成（FlashInfer/CUTLASS）
- [11.6-cpu-and-jit-kernel-support.md](11.6-cpu-and-jit-kernel-support.md) — CPU 与 JIT 内核支持

## 12. 投机解码

- [12-speculative-decoding.md](12-speculative-decoding.md) — 章节总览
- [12.1-eagle-algorithm-and-architecture.md](12.1-eagle-algorithm-and-architecture.md) — EAGLE 算法与架构
- [12.2-draft-and-verification-flow.md](12.2-draft-and-verification-flow.md) — Draft 与验证流程
- [12.3-integration-with-scheduling.md](12.3-integration-with-scheduling.md) — 与调度的集成

## 13. API 接口

- [13-api-interfaces.md](13-api-interfaces.md) — 章节总览
- [13.1-python-engine-api.md](13.1-python-engine-api.md) — Python Engine API（离线批量推理）
- [13.2-http-server-and-openai-compatible-api.md](13.2-http-server-and-openai-compatible-api.md) — HTTP 服务器与 OpenAI 兼容 API
- [13.3-chat-templates-and-conversation-formatting.md](13.3-chat-templates-and-conversation-formatting.md) — Chat 模板与会话格式化
- [13.4-grpc-server-interface.md](13.4-grpc-server-interface.md) — gRPC 服务器接口

## 14. 环境与配置

- [14-environment-and-configuration.md](14-environment-and-configuration.md) — 章节总览
- [14.1-environment-variables-system.md](14.1-environment-variables-system.md) — 环境变量系统（environ.py 集中登记）
- [14.2-hardware-detection-and-platform-configuration.md](14.2-hardware-detection-and-platform-configuration.md) — 硬件检测与平台配置

## 15. 测试与开发

- [15-testing-and-development.md](15-testing-and-development.md) — 章节总览
- [15.1-test-infrastructure-and-cicd.md](15.1-test-infrastructure-and-cicd.md) — 测试基础设施与 CI/CD
- [15.2-benchmarking-and-performance-measurement.md](15.2-benchmarking-and-performance-measurement.md) — 基准测试与性能测量
- [15.3-test-runners-and-model-comparison.md](15.3-test-runners-and-model-comparison.md) — 测试运行器与模型对比
- [15.4-development-tools-and-debugging.md](15.4-development-tools-and-debugging.md) — 开发工具与调试

## 16. 发布与部署自动化

- [16-release-and-deployment-automation.md](16-release-and-deployment-automation.md) — 章节总览
- [16.1-wheel-build-and-release-pipeline.md](16.1-wheel-build-and-release-pipeline.md) — Wheel 构建与发布流水线
- [16.2-docker-build-and-release-pipeline.md](16.2-docker-build-and-release-pipeline.md) — Docker 构建与发布流水线
- [16.3-version-management.md](16.3-version-management.md) — 版本管理

## 17. 输出生成与采样

- [17-output-generation-and-sampling.md](17-output-generation-and-sampling.md) — 章节总览
- [17.1-sampling-parameters-and-configuration.md](17.1-sampling-parameters-and-configuration.md) — 采样参数与配置
- [17.2-logits-processing-pipeline.md](17.2-logits-processing-pipeline.md) — Logits 处理流水线
- [17.3-sampling-algorithms.md](17.3-sampling-algorithms.md) — 采样算法（top-k/top-p/temperature/min-p）
- [17.4-penalties-and-constraints.md](17.4-penalties-and-constraints.md) — 惩罚与约束（repetition/frequency/presence penalty）

## 18. 多模态与视觉语言模型

- [18-multimodal-and-vision-language-models.md](18-multimodal-and-vision-language-models.md) — 章节总览
- [18.1-vision-language-model-architecture.md](18.1-vision-language-model-architecture.md) — 视觉语言模型架构
- [18.2-multimodal-input-processing.md](18.2-multimodal-input-processing.md) — 多模态输入处理（图像/视频/音频）
- [18.3-supported-vision-language-models.md](18.3-supported-vision-language-models.md) — 支持的 VLM 列表

## 19. 高级特性

- [19-advanced-features.md](19-advanced-features.md) — 章节总览
- [19.1-lora-adapter-support.md](19.1-lora-adapter-support.md) — LoRA 适配器
- [19.2-constrained-and-structured-output.md](19.2-constrained-and-structured-output.md) — 约束与结构化输出（xgrammar/outlines/llguidance）
- [19.3-observability-and-monitoring.md](19.3-observability-and-monitoring.md) — 可观测性与监控
- [19.4-session-management.md](19.4-session-management.md) — 会话管理
- [19.5-function-calling-and-tool-use.md](19.5-function-calling-and-tool-use.md) — 函数调用与工具使用
- [19.6-diffusion-llm-(dllm)-support.md](19.6-diffusion-llm-(dllm)-support.md) — 扩散 LLM（DLLM）支持
- [19.7-rl-integration-and-advanced-engine-features.md](19.7-rl-integration-and-advanced-engine-features.md) — RL 集成与高级引擎特性

## 20. SGLang Router (sgl-router)

- [20-sglang-router-(sgl-router).md](20-sglang-router-(sgl-router).md) — 章节总览
- [20.1-experimental-sgl-router:-slim-kv-aware-router.md](20.1-experimental-sgl-router:-slim-kv-aware-router.md) — 实验性 slim KV-aware router
- [20.2-router-grpc-pipeline-and-tool-parsing.md](20.2-router-grpc-pipeline-and-tool-parsing.md) — Router gRPC 流水线与 tool 解析

## 21. SGLang Model Gateway (sgl-model-gateway)

- [21-sglang-model-gateway-(sgl-model-gateway).md](21-sglang-model-gateway-(sgl-model-gateway).md) — 章节总览
- [21.1-gateway-architecture-and-worker-management.md](21.1-gateway-architecture-and-worker-management.md) — 网关架构与 worker 管理
- [21.2-routing-policies-and-load-balancing.md](21.2-routing-policies-and-load-balancing.md) — 路由策略与负载均衡
- [21.3-workflow-engine-and-wasm-middleware.md](21.3-workflow-engine-and-wasm-middleware.md) — 工作流引擎与 WASM 中间件

## 22. 扩散与多模态生成 (multimodal_gen)

- [22-diffusion-and-multimodal-generation-(multimodal_gen).md](22-diffusion-and-multimodal-generation-(multimodal_gen).md) — 章节总览
- [22.1-diffusion-runtime-architecture.md](22.1-diffusion-runtime-architecture.md) — 扩散 runtime 架构
- [22.2-supported-diffusion-models-and-dit-architectures.md](22.2-supported-diffusion-models-and-dit-architectures.md) — 支持的扩散模型与 DiT 架构
- [22.3-diffusion-api-and-lora-support.md](22.3-diffusion-api-and-lora-support.md) — 扩散 API 与 LoRA

## 23. SGLang 前端语言

- [23-sglang-frontend-language.md](23-sglang-frontend-language.md) — 章节总览（结构化编程 DSL：fork/join/future）
- [23.1-language-ir-and-interpreter.md](23.1-language-ir-and-interpreter.md) — 语言 IR 与解释器
- [23.2-backend-integrations-for-frontend-language.md](23.2-backend-integrations-for-frontend-language.md) — 前端语言的后端集成

## 24. 术语表

- [24-glossary.md](24-glossary.md) — 章节总览
- [24.1-glossary:-runtime-scheduling-and-memory-terms.md](24.1-glossary:-runtime-scheduling-and-memory-terms.md) — 运行时/调度/内存术语
- [24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms.md](24.2-glossary:-distributed-quantization-multimodal-and-gateway-terms.md) — 分布式/量化/多模态/网关术语

---

## 相关生态仓（related/）

见 [related/_repo-list.md](related/_repo-list.md)。
