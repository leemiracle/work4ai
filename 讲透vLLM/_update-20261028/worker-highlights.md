# Worker 架构亮点情报（layers/tour 重算素材，随批 accumulating）

## vllm/v1 引擎核心（batch 1-2）
- V1 引擎 IPC 协议全面 msgspec.Struct 化（array_like 位置序列化+字段追加兼容）
- elastic EP 扩缩容新线：EEPNotificationType / ReconfigureDistributedRequest / ElasticScalingCache
- fault tolerance sentinel（2026-10 新增）
- KV cache 双粒度：scheduler_block_size / hash_block_size 分离 + KVCacheConfigBuilder 平台可插拔接口
- HiSparse 三层 host-tier 管理器
- DeepSeek-V4.1 SWA replay_start（NewRequestData L55 实证）
- DiffusionScheduler（canvas 占位裁剪）= diffusion 请求新路径
- engine/__init__.py 是 359 行协议定义文件（14 个类全收，非空模板）

## 注意力后端（batch 7-8）
- backend.py 抽象层（AttentionBackend/MLAAttentionImpl 等 11 类）= 全批继承枢纽（89 条 inherits 汇聚）
- backends/registry.py qualname 字符串注册表 → 40 条 depends_on 指向后端实现文件
- 新子系统 mla/prefill/（base/registry/selector + 6 实现）
- triton_flash_attn.py → composite.py 工厂调用
- 新后端入图：HpcAttentionBackend、triton_flash_attn

## 投机解码 speculator 家族（batch 5，vllm/v1/worker/gpu/spec_decode）
- speculator 继承树全貌：BaseSpeculator→DraftModelSpeculator→（DFlash 系：DFlash/DFlash2/DSpark/XPress/LiLiCorr；TD-AR 系：Eagle/MTP/Gemma4；Standalone/AR、MultiModuleMTP、Ngram、ExtractHiddenStates）
- RejectionSampler + rejection_sampler_utils 全套 Triton kernel；XPress Jacobi kernels
- rejection_sampler.py MAX_CHUNK_BYTES 2GB→1GB（chunking 临时方案 TODO）
- eagle3 aux 层语义：dspark deepseek_v41 原样 layer id / v4 及其它 +1（capture-after）——eagle3_utils.py:125-132

## V1 worker 核心（batch 6）
- GPUModelRunner 7192 行 110 方法（仍在长）；Worker 65 方法
- DBO 微批三件套：ubatching/ubatch_utils/gpu_ubatch_wrapper
- Mamba 状态管理、workspace/lora/kv-connector mixin、XPU 适配层、容错 sentinel
- xpu_worker.py 外部 LB 下 DP rank→设备映射假设顺序分配（round-robin 会撞卡，注释自认）

## kv_offload 全新子系统（batch 11，vllm/v1/kv_offload）
- **基线后全新**（v1 原生 KV 卸载，非 kv_connector 路线）：三层抽象 OffloadingSpec（构建）/OffloadingManager（元数据+逐出）/OffloadingWorker（worker 进程传输）
- CPU tier：SharedOffloadRegion 单 mmap 全 worker 共享（O_EXCL leader 选举+ftruncate 协调）+ cudart hostRegister pin
- **Canonical（并行无关）KV 页布局**（RFC #42082）：num_blocks 恒为首要逻辑维，CopyRun/CanonicalPageMapping 相同字节 rank 轮流写——跨后端互操作关键设计
- 可插拔逐出：CachePolicy 内置 LRU（懒失效最小堆）与 ARC（T1/T2+B1/B2 幽灵链表），CachePolicyFactory 支持 out-of-tree 模块
- 二级 tiering：SecondaryTierManager 强制 GPU→CPU→secondary 级联 + EMA 背压 + ThrottledDrop + 异步 lookup 状态机；KVCR 适配器接外部 P2P 框架

## spec_decode proposer 统一家族（batch 12，vllm/v1/spec_decode）
- SpecDecodeBaseProposer（1800 行）统一 EAGLE/draft-model/并行起草（DFlash）
- DeepSeek V4 hc_mult 残差流扩展（L106）；BreakableCUDAGraph
- 新成员：DFlash（单次 forward 全 draft）、Gemma4 MTP（跨模型 KV 共享）、Step3.5 MTP（继承 EagleProposer 按层选步）、FLy 熵门控延迟验证、GPU 版 N-gram（全向量化 draft 驻留 GPU）
- VocabMapping 异构词表无损采样：BPE 'Ġ'/SentencePiece '▁' 归一化取交集约束 draft logits

## V1 worker 前端与采样链（batch 3-4）
- gpu/model_runner.py 新家 + gpu_model_runner.py 旧 shim 双路径并存（目录重构进行中）
- **V2 采样链 processor 模式**：penalties/logit_bias/bad_words/thinking_budget 全继承 LogitsProcessor，插件经 entry-points `vllm.logits_processors` 加载，前端进程共享 import-light 接口层
- penalties PENALTIES_BLOCK_SIZE 被 cpu/shm.py 覆写走 CPU；批分片采样 shard_owner/row 双侧镜像；watermark 用 Philox4x32-10 triton 内联
- AdaptiveVerificationManager（批 4，投机解码自适应验证新组件）
- ThinkingBudgetState 无基类（源码实证勘误）

## 水印子系统（batch 15，vllm/v1/watermarking，2026 增量全新）
- Gumbel-max 水印三层：prfs/（Philox4x32-10 counter-based PRF，GPU/NumPy 双路径）→ watermarker.py（ABC+RandomSampler）→ gumbel.py（Gumbel/DualKey 双水印器+检测器，Gamma survival 检验）
- 深度集成线①：GPUWatermarkSampler 挂进 v1 Sampler（逐请求开关走 UVA tensor）
- 深度集成线②：DraftWatermarker + watermarked_rejection_sample 延伸进投机解码拒绝采样（Philox 双密钥恢复）

## config 包全景（batch 16，vllm/config 28 子模块）
- 四大枢纽：ModelConfig 2176L 85 方法 / SpeculativeConfig 1766L（Qwen3-Omni DSpark 检查点契约 226L——DSpark 新模型线）/ ParallelConfig 1085L（TP/PP/DP/EP/CP/DCP+EPLB）/ CompilationConfig 1190L（CUDAGraphMode 13 组合）
- 增量新配置类（与执行层互证）：HiSparseConfig（稀疏 MLA KV 卸载）/ EngramConfig（n-gram 嵌入存储）/ AuxOutputConfig / IrOpPriorityConfig / EncoderCacheManagerConfig
- 可扩展注册：register_kv_cache_dtype 允许外部包注册自定义 KV dtype 处理器（Protocol 契约）
- vendored FA 接口：vllm_flash_attn FA2/3/4 统一入口 + vertical/slash 稀疏双入口

## entrypoints API 层大重构（batch 17-18，基线后）
- **目录彻底重组**：旧单文件 openai/serving.py 拆为 chat_completion/completion/responses/decisions/models 子包（protocol/serving/api_router/message_assembly/stream_processor 分层）；generate/ 成为总装配层（register_generate_api_routers 统一挂载 openai/anthropic/cohere/generative_scoring 路由，init_generate_state 集中构造 serving）
- **全新 Decisions API**（/v1/decisions + /v1/systemone）：label read 原语（单 token logprob 读取）+ ReadStrategy 六策略族（NextToken/DiffusionGemmaCanvas/Liquid/JointSchema/ClefFlash/D3）按模型家族分派；问题类型注册表（choice/noul/score）
- Responses API 完整化：ConversationContext 三实现 + 28 个 emit_* SSE 事件 + GPT-OSS Harmony 双向转换器（MCP 点分 recipient/browser 工具）
- /v1/chat/completions/batch 单请求 N 会话并发（merge_async_iterators）
- 协议口径统一：chat/completions/responses 共享 generate/base/protocol + GenerateBaseServing

## 多协议兼容层与 RL/scale_out（batch 21-22）
- **翻译器复用模式**：Anthropic/Cohere 兼容层不自建管线，继承 OpenAIServingChat 做纯协议翻译（AnthropicServingMessages 1064L 含流式 content block 状态机；CohereServingChatV2 1572L 对齐官方 SDK wire 类型）
- **RL entrypoints（训练×推理一体化，2026 重点线）**：在线 rl/online/api_router.py 暴露权重热更新全生命周期 pause→init_weight_transfer_engine→update_weights→finish→resume + draft 独立更新 + weight_checker + WeightOperationMetrics；离线 RLOfflineMixin 经 collective_rpc 下发 weight_transfer/
- **scale_out 三件套（全新子系统）**：render（chat 模板渲染）/derender（125 行流式状态机反渲染）/token_in_token_out（1010 行 token 直通协议）；factories.py 统一初始化；mm_features.py 多模态特征编码对称还原
- **Launcher 重构**：api_server/render 双入口 + NoSignalServer + serve_http（socket 预绑定/优雅关闭/watchdog）+ DPSupervisor（每 DP rank 一子 server 进程，python/rust 双形态）
- CLI 新子命令：preload（每 GPU 权重缓存 daemon）/snapshot（引擎状态快照）/download-kernels（FlashInfer 预编译内核）

## 杂项核心（batch 23-24）
- speech_to_text 独立 API 族：transcription/translation 双轨 + realtime WebSocket（RealtimeConnection 状态机）+ diarized 说话人归属
- envs.py 惰性注册表：模块级 __getattr__ + 两段式缓存冻结 + compile_factors 哈希进 torch.compile 缓存键；env_override.py=TorchInductor 版本化 backport 集中营
- 异常体系：VLLMError→Client(4xx)/Server(5xx)；GracefulHTTP 503 供 LB 重试=准入控制外化
- ir/ 内建算子注册表（新子系统）：IrOp registry+register_op（native/pysec/triton 多实现）
- device_communicators 军火库：CudaCommunicator=六路 allreduce（PyNccl/symm_mem/FlashInfer/CustomAR/QuickAR/AiterAR）×11 种 all2all 管理器（DeepEP HT/LL/V2、NIXL 弹性 EP、FlashInfer NVLink、Mori、MoonEP、AgRs）组合枢纽；batch-invariant 自动禁用无固定归约序后端；MNNVL 跨节点 multicast（Blackwell 门控）
- SHM 三件套：MessageQueue（环形+SpinCondition+ZMQ XPUB）→ShmTensorArena（零拷贝 slot arena）→SingleWriterShmObjectStorage（msgpack KV）

## HiSparse 与采样/结构化输出（batch 13-14，v1/core 线）
- **HiSparse 三层**：coordinator.py（调度侧，GPU 驻留页=主机层写回缓存，unpin_blocks/块表 append-only）/ runtime.py（数据面 pinned host 池 TP 共享 mmap，prefill staging 因 trtllm-gen 固定读前 ~250 行 pad 到 256）/ backend.py（平台注入抽象）——近期 Bugfix 热区（61659/62739）
- Qrita pivot 采样（topk_topp_triton.py 1734L，arXiv:2602.01518）：正态 CDF 查表初始化 pivot 迭代截断免全排序
- perf.py 解析器责任链：ParserChain 四组 ComponentMetrics 估 FLOPs/字节（MLA 单独建模潜压缩 KV）
- 结构化输出双 ABC：StructuredOutputBackend（引擎级 compile）/Grammar（请求级 accept+fill_bitmask）×四后端各带特性检测
- simple_kv_offload 磁盘后端：store/load 双线程不互阻、DMA/preadv 交错、O_DIRECT 4K 对齐
- **新钉版**：相对导入 `from .X import y` 命中具体模块时不发 __init__.py 包边（仅 fallback 发）

## pooling 与 serve 运维面（batch 19-20）
- pooling 三层正交：protocol mixin 库（字段组合）× IO processor 家族 × Serving 基类（__call__ 五段式在线管线）；五任务收进 PoolingServeContext 泛型
- scoring IO processor 五层继承树（BiEncoder→LateInteraction→Flash/Jina 双继承、CrossEncoder 旁支），三评分路径（双塔/交叉编码/ColBERT MaxSim 含 fused flash）
- 陷阱钉版：token_type_ids 截断/填充必须与 TokenizeParams._validate_tokens 同序，否则 query/doc 边界静默错位
- 多供应商：Cohere /v1/embed（task instruction+四编码）、Jina reranker/late-chunking、OpenAI /v1/embeddings（JSON/二进制流式双格式）
- serve 中间件化运维：弹性 EP ScalingMiddleware（503 挡流+ContextVar rank 退役）、sleep 分级显存卸载（L1 KV/L2 权重）、checkpoint 三端点、SageMaker 兼容层
- HTTP 工程：orjson numpy 原生序列化、with_cancellation 协作取消、鉴权 sha256 摘要比对防时序侧信道、ORCA 负载指标响应头

## KV/EC connector 全家谱（batch 25-26，v1/kv_connector）
- EC connector 双栈：CPU 栈（五层 connector→scheduler/worker 委托→session→ZMQ 控制面→NixlDataTransport+mmap 共享区+EmbeddingCache）vs Mooncake EC 栈（预约制：Producer 推送管理器+Consumer 幂等预约+双注册内存池）
- EncoderOutputWidth：DeepStack 多特征打包时编码器输出宽于 LM embedding 的 sizing
- KVConnectorBase_V1（625L 51 方法）+ SupportsHMA 双契约，七族实现：Mooncake 双路径（P2P connector 3138L vs DistributedStore 四件套，StoreLayout 四布局变体 RankLocal/TPSharded/LBHNC/LBNHC）、HF3FS（3FS 异步操作+gather/scatter Triton）、HiSparse（host/hot 双态+DMA，与注意力后端呼应）、LMCache 三形态、FlexKV、DecodeBench、example HMA 参考实现
- MooncakeConnector 传输区规划管线 expand→validate→align→coalesce
- 统一指标骨架：Stats/Logging/PromMetrics/Prom 四层基类全族继承

## KV connector 军团与 weight_transfer（batch 27-28，distributed 线）
- KV connector v1 军团：MoRIIO（4115L RDMA P2P WRITE 状态机+KDA/mamba 状态几何库 925L+心跳独立进程避 GIL）、NIXL（base_worker 4139L pull/push 双模式+兼容性哈希握手）、MooncakeStore（2480L 收发双线程+磁盘分层）、MultiConnector 扇出
- offloading_connector = kv_offload 的连接器门面（OffloadingSpecFactory 按 extra_config 选后端）——与批 11 图上闭环
- **weight_transfer 全新子系统（RL 权重同步五后端）**：WeightTransferEngine/Trainer ABC + WeightSource（plain/FSDP/DTensor）；CUDA IPC（免 rendezvous）/dense NCCL（packed broadcast）/稀疏 NCCL（坐标平坦索引补丁）/NCCL M2N（双 mesh 单 communicator 逐参数 reshard+digest 一致性）/sharded RDT（Ray+NIXL pull 型+BAKE 定型计划）
- 设计模式沉淀：must-agree 线参握手、fail-closed loader 校验、plan digest 全 rank 一致性（M2N/RDT 复用）、packed tensor 生产/消费对

## mono decode mega-kernel 与 DeepSeek-V4 家族（batch 33-34，vllm/models）
- **mono decode layer（本次增量最深的内核工程）**：DeepSeek-V4-Pro 在 MI355X（gfx950）把 decoder layer 全六环节（attention seam/attention/attn all-reduce/FFN seam/MoE/MoE all-reduce）压进两个持久 FlyDSL launch（K1/K2）；runner.py 61 层重跑 → layer.py K1/K2 装配 → stages/+attention/ → common/（tagged mailbox 跨 CTA/GPU handoff、peer_memory 对称内存 in-kernel TP all-reduce、plan JIT cache key 含 source digest）；moe.py 单文件 54 个 kernel-stage 全入图；ROCm/ATOM 参考设计 MIT 归因
- V4 平台三叉戟：deepseek_v4/__init__.py 硬件隔离入口（nvidia/amd 分发）；AMD 专用层 rocm.py 1970L（AITER 稀疏 MLA/SWA+MXFP4 压缩器，MonoDecodeLayer=DecoderLayer.forward drop-in）；common 层（DeepseekV4Attention 752L 平台无关+VL tower+六个融合 Triton 内核含 493L FlashInfer 混合稀疏索引）；CPU 全家（dspark/mtp deferred 占位如实标注）
- 跨批印证：rocm.py 继承链接批 7/8 attention backend 族（25 条 inherits），V4 模型层→v1 注意力抽象→Triton 内核三层贯通

## 弹性 EP 与 compilation（batch 29-30，distributed/compilation 线）
- **弹性 EP 四状态机**：elastic_state.py 四类 rank（existing/new/removing/remaining）各设阶段（COMMIT 阻塞前向）；elastic_execute.py 串联 standby 替换→专家权重传输→映射广播→reset_compile_wrapper（弃编译模型与 CUDA graph）→workspace 解锁-重建-再锁；仅 nixl_ep 可跨 rank 变化复用 MoE kernel
- EPLB 无竞争迁移：按 (src,dst) 聚合 flow 贪心装箱（每 rank 每批单 peer），6 实现通信器族；eplb_state.py 术语表钉版 logical/redundant/physical 三层专家概念
- UMBP connector"两半+协议运行时"：scheduler 半独占前缀匹配/worker 半翻译作业/3 Protocol+注册表工厂解耦（外部适配器免 import）；_LookupBlockPool 请求作用域驻留视图；TransferJobState 逐 key 隔离不连坐
- **compilation 双路线 CUDA graph**：传统 FX 预切分（split_graph 按注意力边界+sym_size.int 逐维分解）vs breakable cudagraph（sglang#19102 灵感：单捕获上下文+dispatcher 拦截注意力/KV op 断流转 eager，产物=零参 callable 序列）；InductorStandaloneAdaptor（torch 2.8+ 注释自述计划默认启用）+SHA256 内容寻址去重
- EngineArgs 3286 行类型驱动 argparse（Literal→choices 等）= 参数面单一事实源
- 自检钉版：resolve 子包 fallback（子包命中即止，勿回父包 __init__）+ UMBP 前缀转写笔误（lineRange 全量比对抓出）

## 融合 pass 与 Beam 模型（batch 31-32）
- torch.compile 融合 pass 四层抽象：InductorPass（UUID=源码 sha256 即编译缓存键）→VllmInductorPass（计时/dump）→VllmPatternMatcherPass（match_table 计数）→VllmFusionPatternMatcherPass（融合后 reshape 折叠/noop 清理）；VllmPatternReplacement ABC 统一 trace+guard+replace；PostGradPassManager 按平台装配三清单
- 融合覆盖=平台量化谱系：RMSNorm×FP8 全组合、allreduce+norm+量化（FlashInfer oneshot vs Aiter 双后端）、qk-norm+rope+KV 写入三合一（impl/fake 双实现）、MLA 双 norm；ROCm Aiter 单文件 20 Pattern 类
- Beam 模型（NVIDIA 平台极致 kernel 工程）：MNNVL 多播 Lamport 三缓冲 allreduce+CuteDSL 手写输出门控内嵌 PTX（ld.global.v4 带 cache hint、exp 交错 SIMD）+SM100 ll_bf16 低时延 GEMM（m=1/2/16 档）
- DFlash2 beam-search 分工钉版：draft 不进 torch.compile（speculator CUDA graph 外部捕获）；BeamModel 混入 EagleModelMixin（一模型两用：DFlash2 draft 与 EAGLE3 目标）
- 目标模型特征：NoPE+SSMax、混合滑窗、per-head QK RMSNorm、深度缩放残差、noaux_tc 分组 sigmoid 路由、TRTLLM NVFP4 fused MoE

## DSV4/V4.1 硬件后端矩阵（batch 35-36）
- vllm/models/ 新顶层布局：模型实现按硬件商分目录（nvidia/amd/xpu），deepseek_v41/__init__.py 硬件隔离入口
- DSV4 三后端 attention 矩阵：sparse_mla.py 公共基座（C128A topk 单 kernel metadata）；NVIDIA=FlashInfer TRTLLM-gen（SM100）/SM120+FlashMLA 双路；XPU=FP8 页即时反量化→BF16 sparse MLA
- MegaMoE 路线：NVIDIA DeepGemmMegaMoE（MXFP4+MegaGate+bf16_mega_gate）vs XPU 自研 Triton staging；quant_config 按 expert dtype 分派
- DSpark 半自回归投机解码三平台同构移植（draft 复用目标 attention、WKV 跨层投影）；V4 独有 e_proj/hc_head
- mono FlyDSL 数值细节：MXFP8 code=clamp(ceil(log2(amax/448))+127)、top-6 sqrtsoftplus 路由、rank 序精确 fp32 all-reduce、epoch 奇偶轮转免清零

## gfx942/Engram/specialized decode（batch 37-38）
- gfx942（MI300X/MI325X CDNA3）monokernel 补齐：weights942.py 权重重排（MXFP8 反量化→OCP 布局+负零清理——FlyDSL 无原生 MXFP8 的补偿）；topk.py 运行时 hipcc JIT 编 1517 行 .cu 做 top-512；fused_markov.py 单 launch Markov 采样
- **Engram（V4.1 独有，n-gram 记忆作为模型结构）**：common/engram.py 1814L 哈希查表门控进 hyper-connection 流（NgramHashState→ParallelEngramEmbedding 301L→DPSharedEngramStorage+4 Triton 内核+大页存储）；engram_peer.py 对称内存交换后端——**= DeepSeek Engram 论文 arXiv:2601.07372 的 vLLM 实现（用户已精读该论文）**
- specialized decode（GB300 延迟专用执行器）：AGENTS.md 收录完整约束契约（TP=4/DSpark/fp8 KV/MXFP4 sparse logits/FULL decode graph+跨 rank MIN all-reduce 保证一致启用）；mxfp8.py 低批投影 pinned tactics
- Lamport all-reduce × mHC 融合：cute_dsl/all_reduce_mhc.py 1343L 四级内核类+primitives.py 27 个 PTX 构建块；fused_wo_a 逆 RoPE+量化融合
- V4.1 独有 decoder replay 机制（model_state.py replay 批收集+decoder_replay_layers/cudagraph 三件套）

## DSV4.1 SM100 专用解码与 Flint（batch 39-40）
- SpecializedDecode 只接管 ≤FUSED_MHC_MAX_ROWS 纯 decode FULL graph 步（prefill/mixed/eager 走 stock 层）；TP 决策只读全 rank 共享 host 状态；side stream run 返回前 join
- Lamport mailbox 流水线：publishing_gemm.py 改编 FlashInfer BSD 低延迟 GEMM（仅改 epilog_warp）把输出直接写进融合 all-reduce+mHC 的 mailbox——GEMM 与通信真正重叠
- 1-8 行低批 MoE 重写：动机=并发 1 时 TRT-LLM-gen 每 MoE 层流式读 ~22 专家权重（HBM 时间+固定延迟）；CuTe DSL 三件套（route+持久 128x8 tcgen05 GEMM 对双缓冲累加器+融合 front）与被替换 kernel 位级一致
- sparse-MLA decode 微优化：共享 sparse-index 表+持久 multi-CTA KV 计数器（kernel 自清零）均不加集合通信
- Flint 全栈小批量 kernel 生态：GGUF NVFP4 读取重打包、调优表 GEMV 分发、split-KV paged decode（cluster DSMEM 归约+学习 sink）、融合 QKV 单 launch、低延迟 MoE 共享专家 aux stream fork/join

## Kimi K3 混合巨构（batch 45-46）
- K3=KDA（Kimi Delta Attention gated delta 线性注意力）+自包含 MLA（991L 不复用 DeepSeek 系）+MoE 三路混合；多模态顶层 426L 26 方法
- KDA 内核全套移植自 fla 生态（third_party/kda/ 四文件，prefill chunked+decode packed 递归双路径）
- **RecoverSSM（SSM×投机解码难题解法）**：SSM 状态无法部分回滚→verify+commit 两阶段（verify 并行算 n draft token 递归：Triton 版+SM10x CuTe 版 KdaTcVerify 368L/warp 特化版 570L；commit 内核折叠进持久状态）——与批 7 replayssm_decode_base_cpu、批 34 V4 decoder replay 形成跨批谱系
- K3 specialized decode（比 V4.1 更极致）：Lamport mailbox 16 字节 fragment 负零哨兵+88 PTX 原语库+五大功能区（gemm/kda cluster-split 递归/mla 426L FP8 KV+moe 1579L 持久 routed experts 按 B∈{1,2,4,8} 分流/attn_res 七 CTA cluster）

## K3 模型全落地补充（batch 43-44）
- KDA 层栈与 MLA 层栈交替（layer_kinds 划分）；latent MoE 带"复制的 routed up-projection"特殊语义（LatentTailTier 按 token 数分档）
- KDA 三级后端矩阵：AMD 融合 HIP（fused_kda_chunk 单 launch 全流程）→ vender FLA Triton（2200L）→ 回退；NVIDIA 融合/FlashInfer/vendored 三路+RecoverSSM 验证+cute_dsl gemm_rs_ar
- **第二个 FlyDSL mono 子系统**（K3 spec-verify 步，RFC #60904，MI355X TP8）：**fail-stop 协议独有设计**——每 rank health words（FAILED 粘滞）+每 16 步 TP CPU 组同步、全员同步步停机（单独停会让同侪悬死在集合通信）
- KIMI_K3_KV_BALANCED_MLA：vendored TokenSpeed FP8 MLA decode（4882L CuTe tcgen05.mma f8f6f4+TMEM+2-CTA M128）+设备端 split-KV work list 规划+双持久 tile scheduler
- 形状分派低延迟 GEMM：纯按 (N,K,M) 实测表分派 SM90/100/103/107；KDA 投影多流并发

## GLM-5-Next 与 HY V4（batch 41-42）
- **GLM-5-Next 双胞胎结构**（新模型目录组织范式，取代旧单文件平台 if-else）：common/ 平台无关层+amd//nvidia/ 两套 kernel（近乎逐行同构仅量化分叉）+sparse_indexer.py 纯平台 shim（current_platform 分派）
- **kpool（key-pooling）稀疏索引钉版**：indexer cache 按"池"存（每 pool_size 连续 token 一条）——compress_ratio==pool_size 让 kv_cache_spec 自动产出池粒度 slot_mapping/seq_lens/page_table；select pools→expand→append tail 全 triton 化；NVIDIA 独有 FWHT-128+FP8+deep_gemm MX scale
- KDA 线性注意力：GatedDeltaNetAttention 子类复用 GDN 状态缓存；显式 eager_break_during_capture；GLM-5-Next 混合层栈=MLA+KDA+MoE+MHC 超连接残差
- HY V4 iHC（independent Hyper-Connections）：hc_mult 条并行残差通道（Pre 收缩→子块→Post 散回→Head 合并），三级实现阶梯 HPC 单 kernel>in-tree Triton>eager
- HYV4MTP 内嵌采样器：draft 路径直接 import v1.sample.Sampler 在模型内采样；FP8 配置动态构造+exclusion 重映射（ignored_layers/exclude_modules 双属性名兼容）
- attention sink 透传：子类化平台后端只为传 per-head learnable attn_sink 进 kernel；amd 复用 nvidia/attention.py=跨平台共享注意力模块先例

## MuseSpark1x 与 Qwen4-Exp（batch 49-50）
- MuseSpark1x：门控 FP32 残差（NormPreservingResidualConnection）+压缩 MoE；AMD 五专家后端+bf16x3 router（三 bf16 平面矩阵核精确和出 FP32——数值精度工程）；Omni 线 NaViT vision+Waveform AutoEncoder（1920 样本≈80ms→1 latent）
- **Qwen4-Exp 三机制线**：①QSA（Query Sparse Attention 无权重索引器）分页 side-cache 挂进 AttentionBackend（QSAStateBackend/KeyStateCache）+AMD 1122L Triton 全套+397L 融合 prepare；②PLE（Position-Learning Enhancement）：n-gram id 哈希（offset[h]+xor_i(token*mult)）→查表嵌入（双后端×三量化 7 类）→gate/短卷积 659L Triton，PLELayer 挂 MambaBase——与 K3 Engram 同族的"记忆作为模型结构"第二例；③HyperConnection（门控残差）：NVIDIA mHC down+SiLU 融合 CuTe 双实现（FMA 315L/split-K MMA 487L）
- 统一约定：全部专家后端止于 GEMM2，post-expert finalize 单点收尾

## Step5/V3.2/dots3/inkling（batch 51-52）
- **Step5=CSA/DSA sparse attention 全自研栈**：CSA region summary（每八 token 压缩 256B FP8 在线 softmax，独立"summary KV cache 层"）；indexer 分数直算自分页 FP8 summary 键（SM90 packed MQA）；DSA decode 直读分页 KV 按 region；主 attention qkv 与 sparse-indexer q/k/z/g 单 GEMM 融合（FusedQKVIndexerLinear）；MegaMoE 共享对称存储
- Step5 prefill 三层复用：PrefillIndexerMetadata 一次分块（128MiB FP32 logits 界）全 DSA 层复用；CompactPagedPrefill 单计划跨层共享
- deepseek_v32 双平台重构：V3.2=DSA 架构（MLA+lightning indexer 选 token）；nvidia/amd 共享 attention.py+common/kernels.py 三融合 Triton；GLM52 低延迟 GEMM 选择器（SM103/107 实测表）复用进 MTP
- dots3_note：NOTE 变体三后端（FA3 varlen/TritonMQA/padded-sparse DSA——cache 行 pad 到 SWA latent 宽度直读 top-k）+Whisper 式 speech encoder
- inkling：muP 宽度乘子 logits 处理器+FA4 score-mod 相对偏置（NVIDIA）vs ROCm Triton+gluon gfx950 双路+多深度 MTP

## MiniMax M3（batch 47-48）
- M3 lightning indexer 公共层镜像 DeepSeek V4 设计：indexer 独立 key-only 侧缓存（自注册静态 forward context）；NVIDIA=MSA（fmha_sm100 build_k2q_csr+sparse_atten_func，decode 默认 Triton split-K 可选 CUTLASS）/AMD=MSA FP8 score（AITER page-16 rebase+Gluon decode）；双选择器集中决策
- **第三个 mono 实例（M3 AMD monokernel，MI355X TP4 专用卡 256 CU）**：每稀疏层=vLLM 输入 norm+注意力+一个持久 FlyDSL launch（TP all-reduce/Gemma norm/FP32 router top-4/共享+路由专家/MoE all-reduce 全在 kernel 内）；mono/sync.py 显式依赖 LLVM AMDGPU 内存模型（FlyDSL 0.3.4.1 所带 LLVM commit 钉死）
- fail-stop 完整语义：内核等 10s 上限→全 rank 粘性错误字；**每 forward 在 logits/采样前**用 torch._Assert_async 检查设备字——GPU 队列 trap→HSA abort worker→引擎停；保证失败步及之后零 token 返回+无逐步主机同步
- CUTLASS MSA 计划缓存：可变张量保持 cudagraph 稳定地址；NVFP4 KV 直读 vLLm 打包页（四视图+每头槽位）免解包
- 索引器 context-parallel：score 行按 world 轮转+AITER IPC all-gather（免 NCCL）→全局 top-k 合并；IndexerCPDecode 单例共享持久缓冲

## 量化内核矩阵与 model_executor 枢纽（batch 55-56）
- **"格式×后端"完整组合空间**：MXFP4/6/8/NVFP4 四格式各有抽象基类，下挂通用后端（emulation/pytorch/marlin/humming）+供应商后端（FlashInfer NVFP4 六变体：CuTeDSL W4A16/CuTeDSL/Cutlass/TRT-LLM/CUDNN/B12x）+硬件特化（RDNA3 gfx11 W4A8 int8 解码、gfx950 rocm_native dot_scaled+rocm_block32 737L 内核族、B12x W4A4/W4A16、DeepGEMM BMM）；31 条 inherits 锚定=图谱最规整的"实现矩阵"
- mla_attention.py 3402L=全仓 MLA 真正公共层（MLAAttention 1010L 被全部 MLA 后端共享+chunked context 规划）；sparse_mla SharedTopkIndicesBuffer+617L SparseMLACommonImpl
- attention.py unified_kv_cache_update+KV 量化初始化=密集后端公共入口；cross/encoder_only/static_sink 三变体走 underlying builder/impl 包装（与 composite 工厂同构）
- FusedMoE config.py 1585L 16 种量化格式工厂=MoE 量化配置单一事实源；专家族含 **CPU 全家 12 类**（×x86/ARM/Power/Zen 特化）；expert_substitution=MoNE 剪枝（arXiv:2507.00390）常量专家替换

## Mamba/SSD 与 CompressedTensors（batch 61-62）
- Mamba2 SSD 完整计算图六内核：chunk_state（cumsum）→bmm→chunk_scan（268L 主内核+_drop_racy_wgmma_configs 过滤 Hopper 竞态 wgmma 配置——罕见内核级 workaround）→state_passing→combined（varlen）→checkpoint（对接 GDN checkpoint 计划）
- ssu_dispatch.py 新后端分发层：MambaSSUBackend 抽象+Triton/FlashInfer/CPU 三实现；承载 ReplaySSM ring tracker 全套内核（update/commit/reset——与批 7 replayssm_decode_base_cpu 闭环）
- mhc.py 五 CustomOp（1020L）=Qwen4-Exp/K3 hyper-connection 公共层（TileLang/AITER 双后端）——与批 50 HyperConnection、批 38 all_reduce_mhc 三点连线
- CompressedTensors 双轴：MoE 轴 11 格式子类+scheme 轴 15 线性 scheme；W4A16 FlyDSL 三打包转换工具=GPTQ→FlyDSL 跨格式桥
- transform/ 子树增量新机制：HadamardTransform+线性变换分派+QUTLASS NVFP4——旋转等价变换（spinquant 类）路线

## MoE 子系统全貌（batch 57-58，本次更新最重单一子系统）
- 三步执行模型成文（modular_kernel.py 1841L）：[Quantize-Prepare]→[Permute-Experts-Unpermute]→[Finalize]；四 ABC 按 Modular（纯专家）/Monolithic（融合路由）两轴正交；FusedMoEKernel 总组装器+FusedMoEFactory 管线工厂
- **专家后端动物园 28 族 68 类**：CUTLASS×4/DeepGemm×2/FlashInfer×4（含 MoE-EP megakernel：路由+dispatch+计算+combine 单体）/Triton×2/Humming×3/OAI triton_kernels×3（非 2 幂 topk monkey-patch+bitmatrix 路由）/Marlin×2/AITER×5/TRT-LLM×8/XPU×6/CPU×2（zentorch）/RDNA3/MoonEP/HPC/仿真×2——全部经 LoRAExpertsMixin 可挂 LoRA
- oracle 决策层=量化格式→后端的编译器：九 oracle 统一 select→convert→make 三段式；mxfp4 oracle 2331L 最重（gpt-oss 专用优先级+DSV4 专用+600L 权重转换）
- prepare_finalize 八形态与 all2all 管理器一一对应（与批 24 的 11 管理器互补成完整 EP 拓扑）；DeepEP-v2 含 MXFP8 scale 打包+globalize-topk 融合
- 经典 fused_moe.py 仍活跃：调优配置三源（覆盖>调优文件>默认启发式）+custom op+fake 注册+UVA 感知

## MoE 路由器族与 layers（batch 59-60）
- 路由器族谱：FusedMoERouter(ABC)→BaseRouter（EPLB logical→physical 映射+padding 掩码）→8 具体路由器；create_fused_moe_router 工厂统一选择（含融合共享专家/零专家/**路由模拟器**——可配置分布随机路由用于测试）；V4 sqrt(softplus) 路由 CPU/dsv4_topk/fused_topk_bias 三处实现
- BF16x3 router GEMM 三平台：fp32 权重拆三 bf16 项和——ROCm Triton 三项归约/SM100 持久 kernel+split-K+调优表/SM90 MMA warpgroup(64 专家×token 块)+TMA warp；GateLinear 四级 GEMM 分发
- RoutedExperts（34 方法）=专家权重所有权+EPLB 映射+量化分发单一容器；capturer/sink 把单体 kernel 实际路由暴露给外部
- HPC 层（V4 超连接）：iHC 三块融合 kernel+HpcRopeNorm（RoPE+QK-Norm+KV 写入+FP8 Q）；**QkNormPolicy 枚举是 HPC kernel ABI 一部分**
- 线性注意力矩阵：GDN 家族（Qwen 2313L：prefill 五选一 SYCL/FlashInfer/AITER FlyDSL/Triton/CUDA+MTP 融合 decode；Kimi TP 复制分片；OLMo 融合门控）+LinearAttention（Bailing/MiniMax）+MambaMixer（replayssm ring 游标共享）；checkpoint 体系后端中立
- 融合量化协议：QuantizedActivation+expose/get input quant key 激活量化结果层间传递免重复量化

## 量化深水区（batch 63-64）
- **online/ 在线量化树（增量新机制）**：运行时量化完整体系——OnlineQuantizationConfig+OnlineRequantizationMixin+格式全家；lm_head.py 对已加载 bf16 头做在线 NVFP4 量化副本（quantize_copy→refresh→share→restore 生命周期，推测双头场景不同精度并行）
- ModelOpt FormatScheme 体系（modelopt.py 2790L）：量化键类型系统（Shapes 匹配+K 系列键+变换算子）+select/resolve/build 三步解析——全仓最"类型化"的量化配置系统
- Humming 集成层跨批闭环：quantization/humming.py 868L+utils/humming 五件套（schema 映射 437L 双向映射+回退、moe 组装 625L）；hadamard_block_size 钩子与批 62 HadamardTransform 呼应——SpinQuant 类旋转等价量化的 Humming 落地
- Marlin/FlashInfer 工具大全：marlin_utils 40 函数+fp4/fp8 变体；flashinfer_utils 13 布局工具（per-die 分片/MXFP8 shuffle/DeepSeek FP8 shuffle）；fp8_utils 31 函数含 silu×mul+FP8 融合
- turboquant/centroids.py=Lloyd-Max 最优标量量化器（旋转后高斯维度质心求解——TurboQuant 4-bit 数学根基）

## linear kernel 重组与 K3 第二执行器（batch 53-54）
- K3 specialized_decode="stock 主干外的第二执行器"：每步一次路由决策后单循环跑完全部预编译 provider；PrefetchController 步间隙预取下层层权重隐藏 HBM 延迟；oproj 生产者-消费者流水线（OprojProducer→mailbox→OprojConsumer reduce_scatter，OprojUmma=tcgen05 形态）
- kernels/linear/__init__.py 1452L=全家族稳定导入面+三级选择器（quant→backend→shape）；模块头钉版"即将按 provider 重组目录"；batch-invariance 过滤+register_linear_kernel 扩展点
- 双基类体系：MMLinearKernel（scaled_mm 系）+MPLinearKernel（W4A16/W4A8/WNA16，12 平台子类链式）+MxFp4LinearKernel 第三族；RDNA hybrid 886L 最重适配
- CuteDSL GEMM 三件套：低时延（ll_bf16 dotprod/splitK+VllmJitKernel JIT 缓存——基类在 jit_warmup.py 勘误）/skinny（m=1-16 动态特化，K3 专用解码底座）/gemm_rs_ar（GEMM 尾声直接 NVLink multimem 多播 RS/AR）
- DSA 稀疏注意力 kernel 下沉公共 kernels 层（candidate_blocks+sparse_mqa_logits）——DSA 家族正式从模型目录迁至公共层

## 量化词汇/RoPE/weight_cache（batch 65-66）
- 量化 utils 六件套成型：quant_utils（QuantKey/GroupShape/ScaleDesc 规范化量化词汇——MoE oracle 全面消费）+mxfp4/mxfp8/nvfp4/ocp_mx/nvfp4_emulation 各格式工具（swizzle 双平台+torch/Triton 双实现）
- RoPE 家族 PluggableLayer/CustomOp 化：ApplyRotaryEmb 统一入口+get_rope 320L 工厂+MRotaryEmbedding 基座三变体（Bailing/ERNIE-4.5-VL/交错）+VitMropeSetup 单融合 kernel+V4 缩放 RoPE+FoPE（Fourier）新成员
- DSA indexer 层双形态：SparseAttnIndexer CustomOp 520L（fused q-rope-quant+DCP topk 全局合并+TP 行分片交换）与 SparseMQAIndexer（两级选择候选消费级）+ROCm paged MXFP4 变体
- model_loader 大扩容：checkpoint_weight_patch（稠密/稀疏补丁供 sparse NCCL 引擎消费——跨批闭环）；EP 权重过滤省 I/O；reload/ 六件套（meta 设备三段重载）支撑 weight_update 热更新
- **weight_cache 子系统（全新，快速重启）**：每 GPU 一 daemon 进程显存持后量化/TP 分片权重 serve CUDA IPC 句柄；WeightCacheKey 三重指纹（safetensors 头+quant 配置+RoPE 参数）不匹配即拒绝；daemon 间 D2D seeding（认证 JSON 通道互传权重与 FlashInfer autotune 表）

## 模型注册表与新旧模型世代（batch 69-70）
- **interfaces.py=模型能力协议中枢（图谱级枢纽）**：2016L 集中全部 Supports* Protocol（MultiModal 351L 主协议/PP/LoRA/Quant/Eagle3/MambaPrefixCaching/IsHybrid 等）+30 余能力探测函数+EagleModelMixin——此前 22 批所有模型 inherits 的 Supports* 目标全汇聚于此
- 新模型世代密集区：Gemma4 全家五件（主模型自带 Triton 融合路由内核——模型内路由内核少见；mm 2361L 三模态+软 token）；**GLM 系八件（智谱生态完整落点：GLM-4 MoE/Lite/双 MTP/4.1V 2392L 自建 vision tower/4V/OCR/ASR 1135L）**；ERNIE 4.5 变分辨率 resampler；Gemma3n AltUp/Laurel 新构件；音频三件（SenseVoice SANM/FunAudioChat/FireRedASR2）+CacheOnly 注意力族（只写 cache 不算注意力）
- IBM Granite 生态六件（单厂商最完整变体矩阵：granite/moe/hybrid/shared/4_vision 三 downsampler/speech conformer）；gpt_oss 1448L OAI 注意力；EVA2-CLIP/InternS1/HyperCLOVAX 长尾

## 模型动物园 A-E 段（batch 67-68）
- **Bailing MoE 三代演进全景**：v1/v2（标准注意力）→v2.5（MLA+线性混合+独立 MTP）→v3（1573L：BailingMoeV3KimiDeltaAttention 520L 的 KDA 与 MLA 双路+v3 MTP+VL 视觉塔）——一个家族线性注意力/MLA/MoE/MTP/VL 五要素齐备
- Col* 多模态检索族统一模式：ColBERTMixin（晚期交互 5 方法）×四后端（ModernBert/JinaRoberta/Lfm2）；各 *Connector+ProcessingInfo+ForRetrieval 三件套——与 LateInteractionRunner/flash_maxsim 构成完整检索栈
- **deepseek_v2.py=DeepSeek 系单一实现枢纽**：V2/V3 共享（MLA+V3.2 lightning indexer+融合 QkvA+MoE）；DeepseekV3ForCausalLM/GlmMoeDsaForCausalLM 是两行别名类——GLM MoE DSA 直接复用 DeepSeek V2 实现
- Diffusion Gemma=vLLM 扩散式 LM 路径：自条件+请求级去噪状态+DiffusionSampler 1131-1690L 去噪循环全栈在模型层
- bert.py 一文件八种头（含 SPLADE 稀疏嵌入）；clef_joint_schema EvidenceRoutingLayer+JointSchemaHead 结构化抽取头

## 模型动物园 I-M 段（batch 71-72）
- **"继承复用"分层生态成主导范式**："新模型=复用 90%+特化 10%"——InternS1Pro 继承 Qwen3Moe/Qwen3VL 全套（自实现仅 MoE 块）；MTP/Eagle draft 几乎全挂 deepseek_mtp/qwen3_5_mtp 基类
- K2-Horizon：MoVA 体素混合注意力（fused_mova_impl）+加载期 RoPE 折叠进权重（消除运行期 rope）
- 多模态基座三连：InternVL（两级三件套+28 方法 ChatModel）/LLaVA（LlavaLikeConfig 鸭子接口+PixtralHF 分支）/MiniCPM-V（版本工厂五版本共存+EncoderCudaGraphMixin 视觉塔录 graph）
- LlavaOnevision2 2315L 自带 codec 视频管线（fps/帧抽取/标记展开在模型文件内）——"重逻辑下沉到模型"路线
- MiMoV2 加载期 FP8 重量化（per-tensor→分组 scale 在线转，免离线重导出）；音频双路线（MiMo 内嵌 RVQ codec vs KimiAudio 复用 Whisper）
- MiniCPMV4.7 canvas 布局引擎（多图拼贴网格分配减 padding）；Mamba2/LFM2=非注意力架构两端
- 方法论：worker2 对 56 高模板化文件用生成脚本（语义数据+AST 直读 imports 1:1）——提速且零笔误

## 注册表与 transformers 通用后端（batch 75-76）
- registry.py 运行时核心：_ModelRegistry 401L 三形态注册（立即/惰性 _LazyRegisteredModel 134L 首用才 import=启动加速关键/子进程探测）；与 interfaces.py 配对成"注册表+协议"双中枢——全部模型类最终汇聚点
- Qwen3 投机谱系：dflash（混合层基座逐层解析）→dflash2→dspark（全仓 DSpark 生态基准）→xpress（RefinerHead）→eagle3；Qwen3-VL 3255L
- **transformers/ 适配子系统（战略架构线）**：Base 749L 包装 HF PreTrainedModel+mixin 矩阵组合 9 预置类+vllm_attention_forward 注入+fusers 权重布局——"逐模型手写"→"通用 HF 后端"
- Step3 家族六件；whisper_causal 228L 工厂 block-pooling 包装；voxtral_realtime SupportsRealtime 双缓冲；utils.py 30+ 公共函数=全模型层共享基座

## Rust 前端深水区（batch 79-80）
- 本地多模态 spec 注册表=显式过渡机制（"借贷式架构"钉版）：SPECS 静态表本地优先/registry 兜底+别名重写
- Rust 逐位对齐 Python 预处理：MuseSpark 缩放语义复刻+分离 h/v 带复刻 PIL Lanczos3+带限 sinc 对齐 scipy；deepseek_v41 测试共享 fixtures 逐字节验证
- engine-core-client 三层：EngineCoreClient（53 方法门面）→ClientInner→RequestRegistry（**choose_engine_for_request 负载均衡决策点**）；协调器双模式（inproc DP 波次广播 vs external 发布订阅）
- 协议"惰性三态"：logprobs/采样掩码 direct/inline/数组惰性 resolve；msgpack+AllowTrailingFields 容忍演进
- MockEngineSockets 伪造双通道 socket——Rust 集成测试无需 Python 引擎
- Rust 方法论钉版：use 三路解析+**mod xxx; 声明以 depends_on 边补充**

## 模型动物园 m-q 段（batch 73-74）
- **Qwen3.5 家族四形态一基座**：Qwen3_5ForCausalLMBase（7 接口）派生 dense/MoE/VL/MoE-VL 四入口，全站 Qwen3Next 骨干+MTP 双 draft；Qwen2.5-VL 10 接口 30 方法=最重单类
- Qwen3-ASR 三件套：基础（7 接口）→ForcedAligner（token 分类化复用）→Realtime（音频环形缓冲+SupportsRealtime）
- NemotronH 混合矩阵：MLP/MoE/Mamba/Attention 四种解码层混排+ReplaySSM 接口+Nano VL v2
- 音频栈两大移植：phi4mm（NeMo Conformer 全家 2600L：GLU/ConvModule/CausalConv/T5 偏置/子采样）与 moss_audio（Whisper encoder+Qwen3 文本栈类继承复用）
- Pixtral 2D RoPE 双栈（原生 Mistral ViT meshgrid 预计算+HF 权重兼容栈）；MoonViT 可学习 2D 插值位置嵌入+Rope2D=Kimi 系前端标准件

## JIT warmup 与批不变（batch 77-78）
- JIT 预热框架三层统一（jit_warmup.py 1146L）：VllmJitKernel 抽象拥有 dispatch+warmup key+编译；三后端 helper（Triton 801L/CuTe DSL/TileLang）；TritonWarmupTensor 仅编译元数据张量+**全 warmup kernel 共享一个编译线程池**；_DispatchExprEvaluator 用 AST 受限子集追踪 dispatch 表达式（白名单强制）
- kernel_warmup.py=预热总线：单入口 fan-out 8 个专用 warmup 模块（attention/K3 KDA/Qwen GDN/Qwen VL/Mamba memcpy/replayssm/ROCm 分段注意力/水印 Philox）；FlashInfer autotune 缓存指纹+逐 rank 一致性检查
- ROCm RDNA 分段注意力 autotune 1336L：工作区预算内候选搜索+**交错测量抗时钟/热漂移**+胜者须稳定击败静态基线才采用+崩溃恢复分片重载
- **批不变模式**（batch_invariant.py 1444L）：mm/matmul/bmm/softmax/rms_norm/linear/all_reduce/reduce_scatter 全套 Triton 固定求和序实现（含持久 matmul 与 XPU tensor-descriptor 变体）+全局 monkey-patch 开关
- scaled_mm kernel 矩阵：9 文件 34 类三维展开（后端×量化类型×scale 粒度）；FlashInfer DeepGEMM 条件切换 kernel+Marlin"无 FP8 硬件借反量化"
- prefetch offloader：静态 GPU 缓冲池（每唯一形状槽位）+层分组异步 H2D+自定义 op 两级结构

## Rust parser/server 深水区（batch 81-82）
- rust parser unified 体系三层：output_grammar/（ArgumentSyntax trait 协议化参数渲染+strict 级别）→unified/hf/（**HfUnifiedParser 把 HF response_template 整体 Rust 化**：774L 状态机+regex DFA 流式步进+四值语法 text/JSON/XML-inline/KV-lines）→模型变体（beam 543L/kimi_k3 通道语法+XTML/muse 1166L recipient 路由+ATEM）；reasoning/tool 解析器按 trait 协议挂接
- rust server crate=**Python API server 的 Rust 平行实现**：lib.rs 491L main+gRPC 双服务（inference 流式 403L 含 EC 占位符保持——呼应 EC connector；control 541L 暂停/LoRA——呼应 RL 权重热更新）+convert.rs 1096L proto↔TextRequest+OpenAI 路由族（Python 侧的 Rust 镜像）；grpc/tests.rs 2767L MockEngine 66 测试函数
- 跨语言对拍基建：generate_differential.py 从 transformers 上游生成差分 fixtures；hf/tests.rs 覆盖五家模板——Rust/Python/transformers 行为一致性保障
- Rust use 三难点钉版：①crate 连字符↔下划线归一（读 Cargo.toml 建 14-crate 映射）②条目级 use 回退 mod.rs/目录同名父 .rs ③edition2018 uniform paths 按 crate 根解析

## LoRA 子系统全貌（batch 85-86）
- 层包装家族"两轴矩阵"：column_parallel_linear.py 一文件 4 型×2 轴（普通/S-LoRA 全分片）=8 类+VariableSlice 变体（checkpoint 子层分组≠标准切分时）；Step5 FusedQKVIndexer 四路 q/k/z/g 切片进 custom_layer
- FusedMoEWithLoRA 29 方法：MoE LoRA 完整生命周期，对接 MoELoRAContext+LoRAExpertsMixin（跨批闭环）
- ops 三后端：torch_ops（punica C++ BGMV/SGMV 六入口）+xpu_ops 移植+triton_ops（自研 Punica 等价，BF16/FP8 双套）
- 融合 MoE-LoRA 三级分派（fused_moe_lora_op 1706L）：one-shot 单 launch 快路径→small-batch 持久 GEMV（grid≈2×SM_count 占用优先）→标准三路；FP8 独立 895L（PDL 支持）；指针 profile_run 预收集（CUDA graph 安全）

## Rust server 完整前端与配置总装（batch 83-84）
- Rust server=完整 OpenAI 兼容前端：/v1/completions 全链（validate→convert→引擎→chunk 流→logprobs）+权重热更新七端点（含 **start_draft_weight_update**——draft 权重独立热更）+sleep/暂停/profiling/render 调试端点；AppState 共享路由状态（API key sha256 摘要存储）
- 显式兼容性校验哲学：validate_request_compat 119L 对不支持参数组合显式报错非静默忽略+ValidatedJson 校验提取二合一=Rust 前端防御性风格
- 9813L 集成测试基座：FakeChatBackend（10 方法）伪造完整 chat 后端——Rust 服务端测试不依赖 Python
- UtilityCallId 幂等 ID 设计：暂停/检查点等非生成调用一等公民化；惰性三态家族扩散（WireStructuredOutputsParams 加入）
- **VllmConfig 总装 3672L 62 方法**：全部子配置聚合+O0-O3 优化预设（enable_allreduce_rms_fusion 等按架构默认开关——呼应融合 pass 体系）+set_current_vllm_config 全局上下文
- 平台算子三巨头并列：_custom_ops.py（CUDA 4933L 100+ op）/_aiter_ops.py（ROCm 5262L ctypes 直连 .so）/_xpu_ops.py（1422L）——per-platform 算子注册表范式
- setup.py 构建三态：源码 CMake/precompiled_wheel_utils（747L 按平台×精度拼装）/Rust 组件预构建

## renderers 与 fla 内核库（batch 89-90）
- renderers=prompt 渲染统一抽象层：BaseRenderer 1422L **68 方法**（32 批以来方法最多单一抽象类：render/tokenize/apply_chat_template/embed 完整契约）+RendererRegistry 分发六家实现；HfRenderer 1511L 含 **jinja2 模板 AST 级变换**（十数个 AST 分析函数直接解析模板代码探测 content format）
- OnlineRenderer 718L/OnlineDerenderer 1073L=render/derender 在线引擎侧执行器（logprobs 双格式解析+MCP 允许工具提取）——与 ServingRender/ServingDerender 完整闭环
- Inkling renderer：Python 前端镜像 Rust 前端——跨语言行为对齐又一例
- flash_linear_attention ops=fla 内核 vendored 本体（KDA/GDN/SSD 依赖源）：gated delta rule 计算图内核件到齐（chunk_delta_h/solve_tril 三角逆合并三级内核=UT transform 核心/wy_fast WY 表示重算/fused_recurrent autograd）
- kda.py 1576L 聚合枢纽：kimi_k3 third_party/kda 四文件全部 import 此库（跨批边接上）

## tokenizer 协议与 tool_parsers 双代际（batch 91-94）
- vllm/tokenizers/ 新顶层包：TokenizerLike Protocol（25 方法）+registry 按配置分派七实现（HF cached/DeepSeek V32/V4/V4.1/Alpamayo2/Kimi-Audio/Mistral-tekken）全部面向协议编程；前导空格标记/恢复体系=detokenizer 公共底座
- DeepSeek 编码器双子（V4 648L/V4.1 608L）：自包含 chat+工具+thinking 编码管线（DSML 参数编码/developer→user 渲染/工具按调用序排序/thinking 丢弃）
- **tool_parsers 双代际并存（化石层）**：老代重量级实现（MiniCPM5XML 815L/Poolside 610L）vs 新代引擎适配薄壳（五个 parser 只是 registered_adapters 一行委托）——工具调用解析正整体迁移到 parser engine（与 Rust 本地 spec 注册表"过渡机制"同构）
- structural_tag_registry 1166L=结构化输出×工具调用桥接中枢（register 按模型登记触发器+resolve_tool_strictness 分档）；streaming.py 必需工具调用流式状态机
- 流式解析公共底座 utils.py 1289L：partial_tag_overlap 截断标签流式匹配+prefix/suffix/intermediate_diff 三件套=全部流式 parser 增量提取内核
- transformers_utils/configs=上游未合并模型配置收容所（28 配置近乎零耦合）；mistral.py 特例=326L 配置字典重映射适配器（应对 HF 上游格式漂移）；复合模型配置分片模式（MuseSpark/Qwen3ASR/BailingMoeV3 按组件分 dataclass 再组合）；draft 配置内嵌三形态

## parser 双轨与 reasoning 三层（batch 87-88）
- parser 包双轨（AGENTS.md 钉版）：Parser 统一接口为正朔+DelegatingParser（22 方法）桥接 legacy 对；**engine/=声明式引擎**（ParserEngineConfig=terminals+transitions+content events）——多数新模型直接继承 ParserEngine
- response_template=第三条路：模板校验 fail-fast→token 级推理终止检测→一份模板同出 reasoning/content/tool；response_template_grammar.py 1001L **从模板+JSON schema 反向推导 structural_tag**（含 closer 拼写歧义检查）
- reasoning 三层退化：ReasoningParser（legacy，AGENTS.md 明言"为兼容保留"）→BaseThinkingReasoningParser→24 具体解析器；双消费者：ParserManager+结构化输出管理器每 decode 步调 is_reasoning_end 决定 grammar bitmask 生效时机
- 模型特殊格式全景：MiniMax M2 无 think token（AppendThink 输出侧补）/K3 XTML 最新 marker 定位/HYV4 纯数据 Extractor 分层/Muse 多轮 turn/body 跟踪+增长尾部扣留/Poolside V1=deepseek_v3 drop-in
- 动态适配器对勘误：MinimaxM2ParserReasoningAdapter 非类定义，是 registered_adapters.py make_adapters() 动态生成

## 处理器注册面与兼容封装双塔（batch 95-96）
- 多模态处理器注册面 26 家：internvl.py 585L 最大族长（h2ovl/nemotron_vl/nvlm_d 四家直接继承）；音频三家（Filterbank 396L/KaldifeatFbank/WavFrontend+CMVN+LFR）；mimo_v2_omni 1234L SGLang 移植最重；kimi_k25_vision_fused="优化的 CPU 图像处理器"（NaViT resize 融合）
- **兼容封装双塔="vLLM 唯一导入点"模式**：deep_gemm.py 1147L 45 入口（GEMM 全家/MQA logits 含 sparse/MHC/UE8M0 打包布局）与 flashinfer.py 1365L 47 入口（**30+ has_flashinfer_* 版本探测函数**——各模型按特性探测后端的真正源头）；API 防腐层
- 运维工具：jit_monitor（warmup 后意外 JIT 编译监控三钩子）/gpu_sync_debug（热路径同步检测）/gc_utils（CUDA Graph 捕获期 GC 冻结）/FlexibleArgumentParser 518L/import_utils PlaceholderModule（registry 惰性加载底层机制）

## 多模态核心与平台层（batch 99-100）
- MM 缓存四级流水：ProcessorCache/ReceiverCache 双基类×shm（ShmObjectStoreSenderCache 12 方法跨进程）/LRU 双轴；4 工厂组装三级；MultiModalHasher 内容哈希+**GPU IPC 内存池**（按最大形状预留+lease 分配——多模态张量 GPU 间零拷贝）
- **MM 字段三态体系跨语言对应**：inputs.py 1029L Batched/Flat/Shared 三态与 rust protocol/multimodal.rs MmField 三态逐一对位——Python↔Rust 前端共享 MM 线格式
- PromptUpdate 状态机（processing/processor.py 1925L）：Insertion/Replacement 双态→队列编译→协议匹配→plan/apply 两阶段=多模态 token 注入核心；BaseProcessingInfo 21 方法契约面
- 视频后端 12 族分裂（video.py 1642L）：模型特定后端（帧采样/mrope 各异）+解码器三轴（OpenCV 软解/PyNvVideoCodec 硬解带池与显存预算/TorchCodec）mixin 组合；EVS/VidCom2 剪枝算法独立目录
- **Platform ABC 91 方法=硬件抽象层完整表面**；cuda.py 三层分裂；_get_backend_priorities 98L=全平台后端优先级矩阵中心；三级解析（显式插件>VLLM_PLATFORM>自动探测）
- WorkerProfiler 三 wrapper+create_worker_profiler；EndpointPlugin Protocol+entry_points 分组发现=第三方扩展统一入口

## 批 103-104（收官组·w:103-104，10-31 会话 c80bfac9）
- **KV cache 类型系统**：kv_cache_interface 19 类 KVCacheSpec 族（DeepSeek-V4 专属 MLA/SlidingWindowMLA alignment padding 与 bounded_replay、HiSparse 热/驻留双池、Mamba 状态池）+ KVQuantMode 15 态（fp8/nvfp4/turboquant/octave/ultraquant/CUSTOM）+ @register_kv_cache_spec 注册表=out-of-tree 平台免改核心接入；UniformTypeKVCacheSpecs 聚合包装专治裸 isinstance 漏 MLA 组
- **Executor 三层复用**：Executor ABC（get_class 按 backend 分发）→ MultiprocExecutor（MQ 广播控制面+FT 感知 KV 输出抢救+watchdog）→ RayExecutorV2 直接继承（两阶段初始化、不改 CUDA_VISIBLE_DEVICES 支持多实例共节点）
- **构建体系**：Dockerfile.rocm_72 独立 rust-input/rust-toolchain/rust-build 阶段（锁 cargo 缓存防 BuildKit 并发写坏）；Rust timed_trace.rs 黄金比例乘法混合确定性种子修复 PYTHONHASHSEED 随机性→prefix-cache 基准跨运行位可复现
- **实证勘误**：docker/Dockerfile.zen L62-63 COPY 的 requirements/test/zen.in 在 HEAD 磁盘不存在（cuda/rocm/xpu.in 之外）——构建依赖缺失或另有生成机制
- **验收修复（主会话）**：batch-104 有 29 个节点 complexity 字符串误填 lineRange——26 个按 sh/rust/py 三语法源码重扫修复+3 个 async fn 补修，complexity 按行幅重评；残余坏锚 0。step/pipeline/service/schema 类型曾撞手术白名单（险丢 17 节点），surgery_merge.py VALID 已扩（钉版：file-analyzer L127 step 为规范类型，工具 schema 契约须对齐——同 zoo 轮 onboard_prep KeyError 教训）

## 批 101-102（收官组·w:101-102，10-31 会话 c80bfac9）
- **vllm/snapshot/ 全新子系统**（CRIU+cuda-checkpoint 引擎快照）：事务式 create/restore（0700 目录+symlink/属主校验+fsync 原子 manifest）、canary oracle（"The capital of France is"，logprob 容差 1e-3）、sleep(2) 释放权重/KV→彩排比对→冻结→ready/release 握手后恢复服务
- **chat_utils prompt_embeds 新模态带安全闸**：占位符哨兵防纯文本注入拼接；Claude Code billing header 剥离保 prefix cache；Kimi 系专用 tool-call ID 格式
- **SamplingParams 迁移 msgspec.Struct**（PydanticMsgspecMixin）：structured-outputs 校验前置到请求期（JSON 嵌套≤64+16、NUL regex 早拒绝、xgrammar/guidance/outlines/lm-format-enforcer 四后端分支）
- **model_arch_config_convertor 30 类转换器**：is_deepseek_mla 枚举 2026 全 MLA 家族（deepseek_v2→v41、glm5_next、kimi_k2/linear、longcat_flash、pangu、bailing、hy_v4）；triton dispatcher sys.modules 全扫描重绑=非 CUDA 平台免改核心换内核
- **坑钉版**：仓根 `json`/`math`/`re`/`sys` 四个 0 字节垃圾文件会被 naive import 解析吸成假 imports 边——本轮已过滤，后续复扫规避（Task6 清理）

## 批 105（补录批·87 基线洞文件，10-31 会话 c80bfac9）
- **vllm/parser/ 声明式流式解析引擎**（补齐 12 文件）：ParserEngineConfig 把模型输出格式（Qwen3 XML/Mistral [TOOL_CALLS] 含 pre-v11 兼容/DeepSeek DSML/Nemotron）描述为**数据**（terminals/状态转移/arg converter）；1269 行 ParserEngine 58 方法单引擎同抽 reasoning+tool call；adapters.py 双适配器桥回旧注册表；rust vllm-parser crate（kimi_k3.rs 注释明言移植自 Python）=py/rust 双栈同构
- **mHC hyper-connections 多残差流内核六后端矩阵**：kernels/mhc barrel 暴露 cuda/aiter/cpu/tilelang/torch/triton 26 符号；tilelang split-k JIT+triton 补缺+torch 基准，与 DeepSeek V4 sparse attention 压缩器（2504 行 CuTeDSL，C4 融合/C128 split）同属 vllm/models/<model>/<vendor>/ops/ 按厂商专属内核新布局
- **rust bench crate 完整测量栈**：config（goodput SLO/ramp-up/长度分布）→datasets（random_mm rayon 并行多模态）→tokenizer（HF/tiktoken/服务端三态）→backends（五种 OpenAI 协议后端+UTF-8 安全流式裁剪）→metrics calculator= vllm bench serve 的 Rust 全链；Dockerfile.cpu 15 stage 双架构三出口
- **验收（主会话）**：459n/1063e，锚抽验 6/6（3 个"MISS"是验证器 rust pub struct 盲区，实命中）；pipeline-bin/understand/rust_use_rescan.py 两 bug 由 worker 修复（expand_body 空前缀双冒号+须在仓根运行）

## 手术合并终态（10-31 23:04 正式落盘）
- assembled-graph.json：**14454 节点 / 41124 边**（11615−10165+13004=守恒闭合；终检悬空 0）
- 残余丢弃诚实记账：符号级悬空 264（changed 文件未再产出的旧符号=重构阵亡）、跨批重复节点 49/重复边 25、白名单外 0
- 基线洞二环兜底：51 个磁盘存在但无节点的悬空 file: 端点（rust lib.rs barrel/cli 等）自动补最小节点救边（surgery_merge.py 通用兜底条款，summary 诚实标注"未深析"）
- 105 批救回悬空边 ~1060 实例（1399→339→兜底后 264 符号级）
