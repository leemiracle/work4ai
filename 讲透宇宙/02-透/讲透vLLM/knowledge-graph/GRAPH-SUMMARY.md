# vLLM 中文知识图谱 · 摘要

- **基线生成**: 2026-09-03 @ `7894394b0759`（11615 节点/33598 边）
- **本轮增量更新**: 2026-10-31 @ `06e172b5cf8845c80c40a6eaaecbcbde3e38e8df[:10]`（覆盖 2026-10-28 源码：3222 commits 增量，changed 1630/deleted 79/added 865，105 批重分析+图手术合并）
- **节点总数**: 14454（function 6290, class 4990, file 3113, config 25, service 13, document 10, step 6, pipeline 5, schema 2）
- **边总数**: 41124（imports 18562, contains 11248, exports 9116, inherits 1733, calls 310, depends_on 122, related 13, configures 6, triggers 5, documents 4, deploys 3, implements 2）
- **架构分层**: 16 层 | **学习导览**: 16 步 | **validator**: 0 issues / 0 warnings

## 架构分层（16 层）

| 层 | 名称 | 文件数 | 职责 |
|---|---|---|---|
| L01 | 全局基础与通用工具 | 82 | vLLM 根包的一等公民：环境变量表（envs）、日志、异常体系、采样/池化参数、请求与输出数据结构（sequence/outputs/logits_process），以及庞大的 vllm/utils 工具族、日志增强、tracing、usage 统计与静态资产，是所有上层的公共依赖。 |
| L02 | 平台适配与配置体系 | 62 | 硬件平台抽象（platforms 的 CUDA/ROCm/XPU/CPU/TPU 接口层）、插件机制（endpoint/IO/lora resolver）、设备分配器与 profiler，加上 vllm/config 中十余个模型/缓存/调度/并行配置段，构成『一份代码适配多种加速器』的配置中枢。 |
| L03 | V1 引擎核心与编译捕获 | 126 | V1 架构的大脑：EngineCore 主循环与前后端通信（core/core_client/async_llm）、输入预处理、增量去分词、admission control 与协调器；调度器与 KV Cache 管理器所在的 v1/core；配合 vllm/compilation 的 torch.compile 分段捕获与 CUDA Graph 体系共同决定执行效率。 |
| L04 | V1 Worker 与采样投机 | 178 | 真正执行 forward 的地方：GPU/CPU Worker 与 gpu_model_runner（批组装、权重加载、CUDA Graph 回放）、投机解码多协议实现、采样器与惩罚/水印后处理、结构化输出（xgrammar/guidance 对接），是性能调优的主战场。 |
| L05 | 注意力与 KV 缓存管理 | 165 | V1 注意力后端全家桶：FlashAttention/FlashInfer/Triton/MLA（含稀疏 indexer 与 prefill 选择器）/线性注意力/Mamba 等数十种 backend 与底层 attention ops，以及 KV cache 接口规范、kv_offload 卸载（CPU/NIXL/Mooncake 等）与 simple_kv_offload 轻量路径。 |
| L06 | 分布式并行与 KV 传输 | 196 | 多卡多机骨架 parallel_state 与各厂商 device_communicators（NCCL/PyNccl/Gloo/自定义 allreduce）、EPLB 与弹性 EP；以及 PD 分离核心 kv_transfer（LMCache/NIXL/Mooncake/SharedStorage 等连接器）、ec_transfer 编排与 weight_transfer 热更新、aux_output_connector。 |
| L07 | 核心算子与内核库 | 183 | 模型执行层的地基：model_executor 根胶水（custom_op/parameter）与 layers 根组件、kernels 目录的线性代数/attention/mhc 内核（含 81 个 linear 变体）、vllm/kernels 的 Triton+Helion 新内核（带 B200/H100 调优配置）、triton/cute/tilelang 工具，以及第三方 flash_linear_attention 线性注意力算子。 |
| L08 | 量化体系 | 126 | model_executor/layers/quantization 下的完整量化栈：FP8/INT8/AWQ/GPTQ/MXFPT4/DeepSeek weight-only 等格式的 linear/moe 方案、autotune 与在线校准，是与上游 kernel 库和模型实现三方对接的关键契约层。 |
| L09 | MoE 与 Transformer 组件 | 215 | 搭建 Transformer 的积木箱：117 个 fused_moe 文件（topk/permute/optimizer 与 CUDA/Triton 变体）、mamba/SSM 算子（含调优配置）、rotary_embedding 全家族、attention/pooler/fusion/hpc 组件，模型文件由它们拼装而成。 |
| L10 | 模型实现·厂商新架构 | 611 | vllm/models 下按厂商/模型族组织的新一代实现：kimi_k3、deepseek_v4/v41/v32、minimax_m3、qwen4_exp、glm5next、step5、inkling、muse_spark 等前沿模型，多带 nvidia/amd 平台特化子目录与专用 decode 路径，是本仓 2025-2026 的主增长区。 |
| L11 | 模型实现·经典注册表与加载 | 377 | model_executor/models 的经典扁平注册表（LLaMA/Qwen/Mistral 等 290+ 实现 + transformers 后端）与 registry 动态分发；model_loader 的 safetensors/GGUF/多格式加载、warmup 预热、offloader/determinism/hw_agnostic 支撑件。 |
| L12 | 多模态、LoRA 与 HF 兼容 | 183 | 模型生态外围：multimodal 的图像/音频/视频输入与编码预算、LoRA 请求管理与各并行层适配；transformers_utils 的 config/processor 兼容垫片（含 37 个 vendored configs）；v0 遗留 engine/arg_utils、inputs 抽象、ray 集成与 forward 微基准工具。 |
| L13 | 服务化入口 | 244 | 对外 API 层：OpenAI 兼容服务器（chat/completions/responses/embeddings/pooling/audio 等路由与 serving）、serve 框架（dev 工具/引擎协议/异常处理）、CLI 与 launchers、speech_to_text、scale_out 弹性、cohere/anthropic 兼容端点、MCP/RL 入口，以及离线 LLM 类。 |
| L14 | 流式解析与渲染引擎 | 167 | 把 token 流变成结构化输出的管线：vllm/parser 声明式流式解析引擎（新）、tool_parsers 51 种工具调用解析、reasoning 思考链分离器、renderers/chat_utils 提示渲染与 chat 模板、tokenizers 各厂商专用分词/detokenizer。 |
| L15 | Rust 前端 | 218 | rust/ 下的高性能前端族：server（gRPC 推理服务）、engine-core-client 直连 Python EngineCore、managed-engine 进程托管、chat/text 抽象、bench 压测、parser 与 metrics，通过 proto/control+inference 与 Python 后端互通。 |
| L16 | 构建与 CI | 35 | 多平台 Dockerfile（CPU/ROCm/EFA/Zen）、Buildkite 流水线与测试矩阵、requirements 锁定、cmake 外部工程与 setup.py 打包配置。 |

## 学习导览（16 步）

| 步 | 标题 | 要点 |
|---|---|---|
| 1 | 全仓印象：从安装到 import | 先建立坐标系：setup.py 定义包形态与编译扩展入口，vllm/__init__.py 暴露 LLM/AsyncLLM 等顶层 API，envs.py 集中 |
| 2 | 配置体系：一切从 EngineArgs 开始 | vLLM 的行为几乎全部由配置对象驱动 |
| 3 | V1 引擎主循环 | EngineCore 是 V1 的心脏：core.py 跑 engine_step 循环，core_client/output_processor 让前端进程通 |
| 4 | 调度器与 KV 预算 | 吞吐的灵魂在调度：scheduler 决定 prefill/decode 如何组批、抢占与 chunked prefill；kv_cache_manager 与 |
| 5 | GPU Worker：真正跑 forward 的地方 | gpu_worker 管生命周期（加载权重、warmup、内存 profile），gpu_model_runner 管一步执行（批组装、CUDAGraph 回放 |
| 6 | torch.compile 与 CUDA Graph 捕获 | vLLM 用分段编译换确定性：compilation 包做 piecewise cuda_graph 捕获与缓存，backends 定义编译后端，让 decod |
| 7 | 注意力后端全家桶 | 注意力是推理引擎的核心算子 |
| 8 | 采样与流式去分词 | logits 出来之后：sampler 落实 temperature/top-p/惩罚等采样参数，detokenizer 做增量去分词，sampling_par |
| 9 | 算子、量化与 MoE | 性能三大杠杆的交汇处：linear.py 是所有投影层的基座，quantization/fp8.py 展示量化方案如何替换 kernel，fused_moe/l |
| 10 | 模型实现的双轨制 | 本仓同时存在两代模型层：经典扁平注册表（llama.py 等 290+ 文件 + registry 动态分发）与新的厂商目录（vllm/models/deeps |
| 11 | 分布式与 PD 分离 | 从单卡到集群：parallel_state 管理 TP/EP 进程组与通信后端，device_communicators 封装各厂商集合通信；kv_transf |
| 12 | OpenAI 兼容服务与离线 LLM | 面向用户的门面：api_server 组装 FastAPI 路由，chat_completion/serving 实现最常用的对话端点（含流式），entrypo |
| 13 | 流式输出解析管线 | 现代模型的输出不只是文本：parser 是新的声明式流式解析引擎，tool_parsers 把工具调用从 token 流里抠出来，reasoning 分离思考链 |
| 14 | 多模态、LoRA 与 HF 兼容 | 生态扩展面：multimodal 定义图像/音频输入的预算与缓存，lora 在各并行线性层上做动态权重叠加，transformers_utils 的 confi |
| 15 | 平台适配层 | 回到底座：platforms/interface 定义能力接口（注意力后端候选、量化特性、指纹检测），cuda/rocm/xpu 等各自实现，上层所有『按平台选 |
| 16 | Rust 前端：另一种打开方式 | 收官看新前端：server 提供低开销 gRPC 推理服务，engine-core-client 直连 Python EngineCore 队列，managed |

## 相对 2026-09 基线的主要变化

- 节点 11615→14454（+24%），边 33598→41124（+22%）；v1 引擎/KV connector/厂商内核布局大改
- 新子系统入图：vllm/parser/（声明式流式解析引擎，py/rust 双栈）、vllm/snapshot/（CRIU 引擎快照）、kernels/mhc（hyper-connections 六后端）、DeepSeek v3.2/v4/Kimi K3/GLM-5-Next 等新模型与厂商专属内核目录
- Rust 前端层 99→218 文件；模型层拆为"厂商新架构/经典注册表"双轨（611+377）
- 修复 2026-09 基线 87 个覆盖洞文件（logger.py/lora/parser 子系统等整片漏收）+51 个二环文件兜底补录
