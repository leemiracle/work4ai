# TensorRT-LLM ONBOARDING

> 图谱基线：7262 节点 / 17517 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 2855 文件 @ commit `b75bcd14`
> 源仓：`/usr-data/data2/repos/agent-repos/NVIDIA/TensorRT-LLM`（4835 文件裁后 2855 进入图谱）
> 全文行号锚均从源码核实（2026-11-07）。

---

## 1. 项目定位：NVIDIA 旗舰推理引擎的三体仓库

TensorRT-LLM 的自我定位写在 README 第一屏（`README.md:5`）：**"optimizes inference for LLMs and Visual Gen models with specialized kernels for common operations, an efficient runtime, and a pythonic framework"**——注意它已不是纯 LLM 推理库，而是 **LLM 推理 + Visual Gen（图像/视频生成）双战场**；技术栈徽章钉住代际（`README.md:9-11`）：Python 3.10/3.12、CUDA 13.4.1、PyTorch 2.14.0。

本仓是罕见的"三体"结构：

| 域 | 内容 | 体量 |
|---|---|---|
| Python 域 `tensorrt_llm/` | llmapi 服务面 + `_torch` PyTorch 原生后端（模型/注意力/MoE/投机解码/pyexecutor）| 图谱 L01-L10 主轴 |
| C++ 域 `cpp/` | runtime/executor/batch_manager 引擎核 + fmha_v2/xqa/thop/cutlass_extensions kernel 库 | L11-L14 |
| agent 生态 `.claude/`/`.codex/` | NVIDIA 用 Claude Code/Codex 协作开发本仓的 skills+agents 活证据 | L15，199 文件 |

执行后端的官方口径见 `AGENTS.md:63`：**PyTorch 后端是 Default**（`TorchLlmArgs` → `_torch/pyexecutor/` → `PyExecutor` → PyTorch Engine），旧 TRT builder 引擎已退居遗产线。三个 CLI 入口钉在 `setup.py:705-708`：`trtllm-serve`（OpenAI/Anthropic/gRPC 服务）、`trtllm-bench`（基准）、`trtllm-eval`（评测）。工程卫生细节如 `warn_on_build_skew`（`setup.py:250`）检测本地构建与预编译产物版本错位，是 pip 安装与源码混用时的第一道防线。

一句话定位：**从 OpenAI 协议 JSON 到 SM 指令流的全栈推理引擎，且同时是 NVIDIA 用 agent 开发 agent 基础设施的双层实验场。**

## 2. 架构总览：16 层 = 用户面 → 模型 → kernel → 生态 四段

图谱 16 层按"请求旅程"分四段读：

```text
用户面    L01 llmapi/serve/grpc ── L16 bench/evaluate/triton_backend
模型层    L02 模型库百家谱 ── L03 VisualGen ── L04 注意力后端 ── L05 MoE ── L06 投机解码
引擎kernel L09 Python 核心库 ── L11 C++ 引擎 ── L12 KV V1/V2 ── L07 disagg 跨节点
          L10 CuTe DSL/Triton ── L13 fmha_v2/xqa ── L14 thop/cutlass_extensions
生态      L08 scaffolding/agent-flow ── L15 .claude skills
```

**请求一条链**：请求从 L01 协议适配进入 → L02 `DecoderModelForCausalLM` 前向 → L04/L05 注意力与专家 → L06 投机解码 draft/verify → pyexecutor 调度（可断 CUDA Graph）→ L12 KV 三层存储 → L07 PD 分离跨节点 KV 搬运 → L10/L13/L14 kernel 落到 GPU。

三个承重锚值得先记：

- `tensorrt_llm/__init__.py:112` 的 `__getattr__` 惰性导出（`LLM`/`AsyncLLM`/`VisualGen` 等映射表在 91-108 行）——包导入零开销的官方姿势；
- `tensorrt_llm/_torch/pyexecutor/py_executor.py:391` `class PyExecutor`——PyTorch 后端调度循环本体；
- `cpp/include/tensorrt_llm/executor/executor.h:62` `SamplingConfig`（单类 45 方法）——C++/Python 双侧共享的采样参数权威定义点。

双域汇流靠 nanobind 绑定（`cpp/tensorrt_llm/nanobind/`）：KV Cache V2 整套 C++ 能力（58 文件）经绑定回到 Python 门面 `tensorrt_llm/runtime/kv_cache_manager_v2/__init__.py`。架构上最反直觉的一点：**TRT-LLM 的主执行路径已经 Python 化**（PyTorch 原生 + torch.compile），C++ 域的重心移到 kernel 与 KV 存储/传输这类"Python 写不动"的深水区。

## 3. llmapi 服务入口：`llm.py` + `llm_args.py` 配置总线

**入口层**（`tensorrt_llm/llmapi/llm.py`，2073 行）：`BaseLLM`（`llm.py:350`）定义 `generate`（`llm.py:659`）/`generate_async`（`llm.py:764`）同步异步双接口；`_TorchLLM`（`llm.py:1804`）实现 PyTorch 后端；用户面的 `LLM`（`llm.py:2047`）继承自 `_TorchLLM`——**类继承链本身就是后端选择史**（旧 TRT 引擎层的删除痕迹留在基类拆分里）。

**配置总线**（`tensorrt_llm/llmapi/llm_args.py`，7182 行，全仓最大 Python 文件）：`BaseLlmArgs`（`llm_args.py:4879`）→ `TorchLlmArgs`（`llm_args.py:5611`）的 Pydantic 树是数百项配置的唯一真源（AGENTS.md 钦定 "Complete configuration schema"）。其中**稀疏注意力配置族是各家旗舰模型的必争之地**，七个类按谱系排布：

| 配置类 | 行号 | 服务对象 |
|---|---|---|
| `BaseSparseAttentionConfig` | `llm_args.py:692` | 抽象基类 |
| `SeqLenAwareSparseAttentionConfig` | `llm_args.py:719` | 序列长度感知中间层 |
| `QSASparseAttentionConfig` | `llm_args.py:736` | QSA（Qwen 系稀疏） |
| `MiniMaxM3SparseAttentionConfig` | `llm_args.py:858` | MiniMax M3 |
| `RocketSparseAttentionConfig` | `llm_args.py:1035` | Rocket（百川系） |
| `DeepSeekSparseAttentionConfig` | `llm_args.py:1093` | DSA（V3.2 Indexer/TopK） |
| `DeepSeekV4SparseAttentionConfig` | `llm_args.py:1341` | V4 混合压缩（继承 DSA 扩展） |

另有 `SkipSoftmaxAttentionConfig`（`llm_args.py:1479`）作旁支。改任何 LlmArgs 字段的 PR 必须重跑 `scripts/generate_llm_args_golden_manifest.py` 并提交 golden manifest（AGENTS.md 硬规矩）。

**服务面**：`tensorrt_llm/commands/serve.py`（2814 行）是 `trtllm-serve` 入口，`serve()`（`serve.py:1331`）主路径 + `serve_encoder`（`serve.py:1756`）/`serve_embedding`（`serve.py:1891`）专用变体。协议侧三通道：OpenAI 兼容（`serve/openai_protocol.py` 64 个 Pydantic 模型一字排开）、**Anthropic 兼容**（`serve/anthropic_adapter.py:694` `AnthropicStreamReframer` 把 TRT-LLM 流重帧成 Anthropic SSE）、gRPC（`grpc/openengine/proto/openengine/v1/` 八个 proto——`openengine.proto:38` `service Inference` 与 `:43` `service Control`；**包内 proto 是 canonical 单一事实源**，`_generated/` 勿手改）。

## 4. 模型库百家谱：76 个 modeling 文件与四大家族

`tensorrt_llm/_torch/models/` 下 **76 个 `modeling_*.py`**（实点数：deepseekv3/v4、glm5_next、kimi_k3_vl/kimi_linear/kimi_k25、qwen3_5/qwen4_exp/qwen3_next、gemma4 全家、nemotron/nemotron_h、minimaxm2/m3(+vl)、hunyuan、step3p7、hyperclovax、gpt_oss、mixtral、cohere2、seedoss……），由 `_arch_index.py`（约 204 键的静态表）驱动懒加载。

**DeepSeek V4 线**（`modeling_deepseekv4.py`，2714 行）是当前世代的复杂度天花板：`modeling_deepseekv4.py:73` 直接 import `mHC` 超连接组件（对应 C++ `thop/mhcOp.cpp`，见 §7）；`DeepseekV4Attention(MLA)`（`:1371`）挂稀疏后端；`DeepseekV4MoE`（`:1512`）；`DeepseekV4MTPHead`（`:1223`）+ `DeepseekV4ForCausalLM`（`:2551`，继承 `SpecDecOneEngineForCausalLM`）原生接投机解码。V3.2 老线在 `modeling_deepseekv3.py:1933` `DeepseekV3ForCausalLM`。

**GLM-5.3**（`modeling_glm5_next.py`，2081 行）展示了谱系复用：`Glm5NextLinearAttention`（`:764`）**直接继承 Kimi 的 `KimiKDALinearAttention`**（KDA 线性注意力血统共享），配 `Glm5NextIndexer`（`:887`，token 选择索引器）与 `Glm5NextSparseAttention`（`:977`）构成"线性+稀疏"混合层。

**Kimi K3/K2.5/Linear**：`modeling_kimi_linear.py` 3126 行，`KimiLinearForCausalLM`（`:2090`）；K3 的出厂投机配置单独成文件 `tensorrt_llm/_torch/configs/k3_dspark.py:23` `K3DsparkConfig`。

**Qwen3.5/3.8**：`modeling_qwen3_5.py:704` `Qwen3_5ForCausalLM`（Moe 变体 `:671`）。**勘误口径**：仓内没有 "qwen3_8" 命名——Qwen3.8 是 `qwen4_exp` 线：`configs/qwen4_exp.py:3` docstring 明言 "In-tree configurations for **Qwen3.8-Flash-Next** checkpoints"（transformers 不带 Qwen4Exp 配置类，故进树），`Qwen4ExpConfig`（`configs/qwen4_exp.py:160`）。

`_torch/configs/` 共 **11 家 in-tree HF 兼容配置**（cosmos3/deepseek_v3/deepseekv4/gemma4/glm5_next/k3_dspark/kimi_k3/kimi_linear/laguna/minicpmv4_6/qwen4_exp），全部继承 `PretrainedConfig`——HF checkpoint 无官方 config 类时的兜底模式。权重侧 `checkpoints/` 43 份 mapper/loader；跨模型组件在 `modules/`：mhc 超连接（`modules/mhc/hyper_connection.py:72` `class mHC`，`HCHead` 在 `:253`）、dwdp 权重并行、linear.py 的 17 种量化 LinearMethod。

## 5. VisualGen 视觉生成线：与 LLM 平行的第二引擎

VisualGen 是独立 vertical（AGENTS.md 明言 "not an LLM backend"）：有自己的 engine/args/params/outputs，只在注意力、量化、并行上复用 PyTorch 后端资产。公共 API 面在 `tensorrt_llm/visual_gen/`：`VisualGenArgs`（`visual_gen/args.py:686`，860 行，含 `TeaCacheConfig:400` 免训练步跳过、`CpuOffloadConfig:543`）；内部实现在 `_torch/visual_gen/`。

骨架三件：`pipeline_registry.py:102` `register_pipeline` 注册各家族 + `:151` `AutoPipeline` 从 checkpoint 单 safetensors 探测管线类型；`pipeline.py:104` `BasePipeline`（1474 行）统一 run_inference 去噪主循环、CUDA Graph 装配与分相计时。

模型家族（`_torch/visual_gen/models/` 九目录，超出任务书列举的两家值得点名）：

- **Cosmos3** 世界模型：`cosmos3/transfer.py:210` `resolve_transfer_config` 负责权重迁移（`Cosmos3TransferConfig:156`），`action.py`（机器人动作宽度按 domain 键控）+ `sound_tokenizer.py` 佐证其"全模态"野心；
- **FLUX.1 + FLUX.2**：`flux/attention.py:315` `Flux2ParallelSelfAttention`、`transformer_flux2.py:440` `Flux2Transformer2DModel`（FLUX.1 的 `transformer_flux.py` 同目录并存）；
- **LTX-2**：目录内 `LTX_2_CHECKPOINT_FORMAT.md` 是罕见的**权重格式契约文档**（格式变更须过此文档）；
- **WAN**：`wan/dup_up3d.py:21` `_supports_triton_indexing` 是 Triton int32 偏移 2^31 硬边界的防御式探测——不过关走逐 chunk 回退，教科书级的 kernel 边界工程；
- 另有 **MiniMax-H3**（`minimax_h3/`）、`glm_image/`、`hunyuan_video1_5/`、`qwen_image(+_layered)/`。

kernel 侧共用 `cute_dsl_kernels/blackwell/sol_attn_backend.py`：`_load_sol_attn`（`:78`，`functools.lru_cache(maxsize=1)`）延迟导入整个 CuTe DSL（导入昂贵且未必被选），`SUPPORTED_ARCHS = frozenset({100, 103})`（`:94`）与 interface 的 `_CUTE_BACKENDS` 靠人工同步——改架构支持时的已知坑点。

## 6. 推理核心三件：投机解码 × MoE 契约 × KV Cache V1/V2

### 6.1 投机解码全家族（`_torch/speculative/`）

接口层 `speculative/interface.py`（3081 行）：`SpeculativeDecodingMode`（`interface.py:308`）是模式位标志——**`:313` 注释明言 2/4/8 三个位已退役**（两模型 MTP_EAGLE、EAGLE3、DRAFT_TARGET 让位给 one-model 统一 worker：`MTP_EAGLE_ONE_MODEL=3`、`EAGLE3_ONE_MODEL=5`）；请求级元数据 `SpecMetadata`（`:478`）。

四代草头各成文件：**DFlash**（`dflash.py` 2112 行，`DFlashWorker:634`，DeepSeek 系 KV 注入路线）→ **DSpark**（`dspark.py`：`DSv4DSparkWorker:221` 是 V4 专用、`DSparkWorker(DFlashWorker):831` 继承复用——**DSpark 是 DFlash 的子类化演进**这一谱系在类定义行一目了然）→ **EAGLE3**（`eagle3.py:436` `Eagle3OneModelWorker`，`:1302` `MTPEagleWorker` 再继承出 MTP-Eagle 混合；`eagle3_dynamic_tree.py` 带动态树变体）→ **MTP**（`mtp.py:247` `MTPWorker`，`mtp_dynamic_tree.py` 同款动态树）。

工程亮点是 `accept_stats.py` 的**零开销设计**：未启用时 recorder 为 None 全链路不调进（`accept_stats.py:117` `DFlashAcceptStatsRecorder`）；置信度调度走 `dspark_confidence` 延迟导入（`:90`），把 DSpark 论文的 Θ=τ·SPS 置信度阈值做成可选 provider。

### 6.2 MoE 契约谈判语言（`_torch/moe/fused_moe/`）

TRT-LLM 把"选哪个 MoE 后端"做成了**显式契约谈判**：`impl_contract.py`（657 行）用一组 frozen dataclass 定义谈判词汇——`MoEProblem:98`（问题陈述）× `MoEEnvironment:232`（环境探测：flashinfer/deepgemm-megamoe/cutedsl-rubin 依赖冻结）× `MoEDeployment:267`（部署意图）→ `MoEEligibility:341`（各实现资格判定）→ `MoEResolutionReport:452`（裁决报告，含 `MoERejectReason:301` 降级链描述与 "MoE resolution: {winner} (via {selected_by})" 的人类可读输出）。后端工厂 `create_moe.py:43` `create_moe_backend` 按 12 个后端实现（cute_dsl/cutlass/deepgemm/densegemm/marlin/triton/trtllm_gen/vanilla…）分派；`routing.py`（1778 行）收录 15+ 家模型路由（DeepSeekV3/V4、MiniMaxM2/M3、Llama4、SparseMixer、SigmoidRenorm…）。这是"配置即协商"的罕见架构——比 if-else 树可测、可比错、可审计。

### 6.3 KV Cache V1/V2 双体系三层存储

**V1**（C++ 单体时代）：`cpp/include/tensorrt_llm/batch_manager/kvCacheManager.h`（2754 行 20 类）——`KVCacheBlock:387`、`GenerationRequest:595`、`KVCacheBlockPool:784`、滑窗专用 `WindowBlockManager:866`、`BlockManager:1502`、总管 `KVCacheManager:2292`，线性注意力状态 `LinearAttentionMetadata`（`:146`）专为 Mamba 系留位；实现 `kvCacheManager.cpp` 4647 行 167 函数。

**V2**（重写，`kv_cache_manager_v2/` 58 文件）是**GPU/Host/Disk 三层存储**：`config.h:37/53/69` `GpuCacheTierConfig`/`HostCacheTierConfig`/`DiskCacheTierConfig` 三层配置，`:83` `CacheTierConfig = std::variant<...>` 变体聚合；`storageManager.h:125` `StorageManager`（55 方法）做分层调度，迁移核心 `submitMigrationBatch`（声明 `:382`，实现 `storageManager.cpp:579`）；块级前缀共享 `blockRadixTree.h:355` `BlockRadixTree`（token 级共享，比 V1 的 radixBlockTree 更细）；`coldPageCodec.cpp` 冷页压缩（Python 侧 `_torch/kv_cache_compression/` 的 NVFP4 冷页量化与其跨语言呼应）；`copyEngine/cudaVirtMem` 走 CUDA VMM 虚拟内存做异步拷贝。Python 驾驶舱 `pyexecutor/kv_cache/kv_cache_manager_v2.py:1107` `KVCacheManagerV2`（150 方法的资源管理器巨类，兼容量估算纯函数库与 host tier 自动配额）。

配套两件值得点名：`pyexecutor/breakable_cuda_graph_runner.py:26` `BreakableCUDAGraphRunner`（**改编自 SGLang** 的可断 CUDA 图——投机分支处拆段重放）；KV 外存连接器 `connectors/mooncake_store/`（与 vLLM 共用 MOONCAKE_CONFIG_PATH，一套部署喂两个引擎）：`config.py:87` `StoreRole`、`master.py:362` `LaunchedMaster`，`donor.py:29` 注释钉版设计决策——**"donation 刻意不是 StoreRole"**（角色描述引擎流量，没有一个角色表示"只贡献内存"，容量与流量两轴正交）。

## 7. kernel 深水区：fmha_v2 / xqa / CuTe DSL / thop 四座矿

### fmha_v2（`cpp/kernels/fmha_v2/`，145 文件）——SM70→SM120 全世代 tile 体系

`cpp/kernels/fmha_v2/setup.py`（6990 行）是**代码生成式 kernel 仓**：`get_kernel_code`（`setup.py:2235`）/`get_api_code`（`:2473`）/`get_cubin_header`（`:3346`）三段生成管线驱动 4000+ 行枚举器按代际批量产出绑定。架构覆盖表钉在 `setup.py:22-33` `sm2name`：Volta 70/72、Turing 75、**Ampere 80/86/87、Ada 89、Hopper 90、Blackwell 120**（`kSM_120=120` 常量在 `:3847`，`ENABLE_SM120` 环境开关在 `:6798`）——横跨四代 GPU 的 tile 抽象。分代测试脚本 `test_sm70/75/80/90_*.sh` 与 Makefile `TORCH_CUDA_ARCH_LIST` 锁 8.0/9.0 双架构互相印证。tile 体系三层：`src/fmha/traits.h`（22 类 Volta→Blackwell traits）、`kernel_traits.h:151` `Kernel_traits_` 主装配模板、Hopper 专用 `hopper/arrive_wait.h:115` `Arrive_wait`（mbarrier 全家封装）与 `hopper/compute_tile.h`；warpspec 双 warp 组流水在 `warpspec/`（`dma.h`/`compute.h`/`circular_buffer.h`——`circular_buffer.h:499` `ComputeGroupBarrierAccessor`）。

### xqa（`cpp/kernels/xqa/`，36 文件）——多 query 头聚束解码注意力

`mha.cu`（3008 行）：`kernel_mha`（`mha.cu:2795`，`__launch_bounds__(256, nbCtaPerSM)`）→ `launchMHA`（`:2870`）→ `cudaLaunchKernelEx`（`:2953`，PDL 可编程依赖发射）。最有考古价值的是 `mha_stdheaders.cuh`（1298 行）：**kernel 内禁标准库，`:227-232` 手写 `is_same` type_traits 特化**——device 侧 C++ 元编程的自足实现，与 `gmma.cuh`（Hopper MMA 封装）、`gen_cubins.py`（预编译 cubin 分发）合成一套独立王国。

### CuTe DSL（`_torch/cute_dsl_kernels/`，139 文件）——Python 写 kernel，Blackwell/Rubin 双代并行

`cutedsl_megamoe/kernel_src/` 下 `blackwell/` 与 `rubin/` 双代并行维护同族 kernel。**Rubin sm107 是下一代主战场**：rubin 世代合计 16692 行，local_mega 五件（mainloop 1313 + local_routing 1712 + kernel 1084 + epilogue 460 + tma_gather 101），另含 `mega/` 的 gen_specialized 变体（mainloop_gen_specialized 1798 行）。锚点：`block_scaled_swap_ab_fc12_mainloop.py:14` `import cutlass.utils.rubin_helpers as sm107_utils`（**Rubin helper 已进 CUTLASS 上游**）、`:102` `self.architecture = "sm_107"`、`:380` `make_blockscaled_trivial_tiled_mma`。单 kernel 融合极限在 `blackwell/kimi_k3_kda/fused_k1234.py`（2278 行文件）：`fused_k1234_kernel`（`:539`）一个 kernel 1500+ 行融合 KDA 线性注意力全前向。dspark 投机注意力 kernel（`blackwell/dspark/attention_kernel.py`）与 conv 的 tcgen05 UMMA 2-CTA+cluster 联合校验同场。

### thop（`cpp/tensorrt_llm/thop/`，124 文件）——C++ 自定义算子总库 + vendored 三件套

`allreduceOp.cpp`（2446 行）覆盖 NVLS/MNNVL 多路径集合通信：`:1142` `checkMNNVLSupport` 探测，`:489` 注释论证 multimem 的 O(const.) 扩展性收益（性能随 rank 数增长）；`mhcOp.cpp` 是 **DeepSeek-V4 混合压缩注意力宿主**：`mhcBigFuseOp:28`/`mhcGemmSqrsumFmaOp:44`/`mhcHcHeadApplyOp:54` 三算子对应 Python `modules/mhc/hyper_connection.py`（§4）；`compressorOp.cpp:30` `compressorPagedKvCompressOp` 实现 V4 在线 Compressor。vendored 生态在此汇流：`include/tensorrt_llm/deep_gemm/`（`scheduler.cuh` 761 行 14 类调度器，含 SwapAB 变体；`nvrtc_cutlass.cuh` 在 JIT 编译单元内**自包含定义 TMA 原语**避免运行时链接 CUTLASS）、deep_ep（nvshmem 源载荷 txz）。

## 8. agentic 生态：NVIDIA 用 agent 开发 agent 基础设施

### scaffolding + contrib（`tensorrt_llm/scaffolding/`，L08）

scaffolding 是"用 TRT-LLM 跑 agent/研究负载"的框架层：`controller.py` 的 Controller ABC + task.py 五角色消息体系。`contrib/` 收录七个研究脚手架：**SWE-bench Coder**（`contrib/Coder/coder.py:114` `Coder`、`:135` `SWEBenchCoder`、`:290` `create_swebench_coder_scaffolding_llm` 工厂）、**DeepConf** 置信度控制（`deep_conf_controller.py:12/43/79/125` 四个 Offline/Online × 普通/多数票控制器一字排开）、**Dynasor**（`dynasor_controller.py:11` `DynasorGenerationController`，推理时 MCTS 搜索）、TreeInference、open_deep_research、iter_research、mcp。

### agent-flow（仓根独立 Python 包）

仿 PyTorch 的 agent 编排框架：`agent_flow/module.py:33` `Module(ABC)` 树形生命周期（`:108` `Sequential`）、`layers.py:118` `AgentLayer`（forward/aforward 同步异步双态）、`runtime.py:13` `PortalRunner`（线程+队列 portal 模式让同步代码安全驱动 async SDK）。后端归一化：`backends/claude_code.py:223` `ClaudeCodeClient` / `:448` `ClaudeCodeBackend`（SDK 消息→共享事件的大量归一化），codex 双后端同构。工作流层 perf_analyze/perf_optimize（1692 行共享命令知识库——trtllm-serve/nsys/ncu 的规范 flag 参考）与 agent_team（1543 行状态机，**只读 YAML decision 字段驱动、杜绝正则解析散文**）是"提示词工程纪律化"的范本。

### .claude 三族 agents + 28 个 skills（L15）

`.claude/README.md` 开宗明义这是 version-controlled 的领域知识组件。`agents/` 11 个子代理分三族：**exec 族**（exec-compile-specialist/exec-local-slurm/exec-remote-slurm——本地/远程/Slurm 编译执行）、**kernel 族**（cuda/cute/tileir/triton 四专家，kernel-cute-specialist 155 行最厚）、**perf 族**（profiling 383 行/test-sync 597 行/torch-cuda-graph）。`skills/` 28 个目录中最重的是 **perf-optimization-casebook**：41 个案例文档分三族（communication 5 / kernel-and-fusion 17 / runtime-execution 19），每案 frontmatter+决策先例八要素（适用性/机制/应用/预期收益/精度风险/验证/回滚）；`data/aliases.yaml` 是查询期归一化词表（如 `sm100: [blackwell, b200, gb200]`，**同义词禁与 canonical 碰撞**），patterns.yaml 要求 pattern 与 case 双向回指——声明式注册表契约。`agent-tests/perf-test-sync` 用 promptfoo 做提示词回归；`.codex/` 是 Codex 侧镜像。**这层生态与主仓同仓同进化：NVIDIA 把 agent 协作开发本身做成了可测试的工程资产。**

---

### 新人上手三步

1. **跑通服务**：`trtllm-serve <hf_model> --port 8000`，对照 §3 读 `llm_args.py` 的 TorchLlmArgs 字段树；
2. **改一个模型**：从 `modeling_qwen3_5.py`（最薄）入手，沿 `_arch_index.py` 注册 → `configs/` in-tree config → `checkpoints/` mapper 三件套走一遍（docs/source/torch/adding_new_model.md 是官方路径）;
3. **下深水区**：按 §6→§7 顺序读 `impl_contract.py`（谈判词汇）→ `fmha_v2/setup.py`（生成管线）→ `cutedsl_megamoe/kernel_src/rubin/`（下一代），配 `.claude/skills/` 里对应的 kernel/perf skills 当导读。

**已知勘误与坑**（本图谱批阶段甄别钉版）：Qwen3.8 = `qwen4_exp` 线非独立命名；sol_attn 的 `SUPPORTED_ARCHS` 与 interface 人工同步易漂移；`xqa/mha_sm90_transpose.xlsx` 是设计记录非代码；KV V2 文件数 58（图谱摘要写 55，以盘上为准）；casebook 案例数为 41（5+17+19，任务书口述 44 与盘上不符）。

