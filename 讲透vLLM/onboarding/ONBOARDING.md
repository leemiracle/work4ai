# vLLM 新人上手指南（2026-10 重写版）

> 知识图谱基线：14454 节点 / 41124 边 / 16 层 / 16 步导览，源文件 7117，commit `06e172b5cf`（2026-10-31）。行号锚均经源码核实。

## 1. 项目总览

**vLLM** 是高吞吐、内存高效的 LLM 推理与服务引擎：把 HF checkpoint 变成生产服务，从 OpenAI 兼容 API 到 GPU kernel 全栈自研，Python 为主体，Rust 前端 14 个 crate，C++/CUDA/Triton/CuTeDSL/FlyDSL 算子。规模：经典模型目录 292 文件 + `vllm/models/` 厂商目录 15 个新架构族、attention backend 枚举 57、KV/EC/weight connector 30+。

为什么值得学：①PagedAttention+continuous batching 立身之本（第 3 节 5/6 条）；②双代执行引擎并存——V1（`vllm/v1/worker/gpu_model_runner.py:475`）与重写的 Model Runner V2（`docs/design/model_runner_v2.md:5`），单仓可见一代引擎的技术债清算；③推理前沿全覆盖：PD 分离、RL 训推一体、11 族投机解码、弹性专家并行、Gumbel 水印；④Rust 前端（`rust/src/server/src/lib.rs:197`）是 Python API server 的平行实现。

## 2. 架构分层（16 层）

| # | 层 | 文件数 | 职责 |
|---|---|---|---|
| 1 | 全局基础与通用工具 | 82 | envs/日志/异常/请求输出结构，公共依赖 |
| 2 | 平台适配与配置体系 | 62 | `vllm/config/` 28 子模块 + platforms 硬件抽象 |
| 3 | V1 引擎核心与编译捕获 | 126 | EngineCore 主循环、调度、KV 管理、torch.compile 捕获 |
| 4 | V1 Worker 与采样投机 | 178 | 双代 model runner、投机解码、采样、结构化输出 |
| 5 | 注意力与 KV 缓存管理 | 165 | 57 后端、MLA 家族、`v1/kv_offload/` 原生卸载 |
| 6 | 分布式并行与 KV 传输 | 196 | parallel_state、EPLB/弹性 EP、PD 分离、weight_transfer |
| 7 | 核心算子与内核库 | 183 | linear/embedding 基础层、kernels 内核族 |
| 8 | 量化体系 | 126 | FP8/AWQ/GPTQ/MXFPT4 方案、在线量化 |
| 9 | MoE 与 Transformer 组件 | 215 | 117 个 fused_moe 文件、mamba/SSM、rotary——积木箱 |
| 10 | 模型实现·厂商新架构 | 611 | `vllm/models/` 15 族（kimi_k3/deepseek_v4/glm5next/step5…） |
| 11 | 模型实现·经典注册表与加载 | 377 | 292 文件 + registry 分发 + model_loader |
| 12 | 多模态、LoRA 与 HF 兼容 | 183 | 输入预算缓存、LoRA 适配、40 个 vendored configs |
| 13 | 服务化入口 | 244 | OpenAI/Anthropic/Cohere API、serve 框架、CLI、RL 入口 |
| 14 | 流式解析与渲染引擎 | 167 | `vllm/parser/` 声明式解析（新）、55 个 tool_parsers、renderers |
| 15 | Rust 前端 | 218 | server/engine-core-client/managed-engine/parser/bench |
| 16 | 构建与 CI | 35 | Dockerfile、Buildkite、requirements |

与旧版最大不同：模型实现拆成 L10（厂商新架构，两个月长到 611 文件、全仓最大层）与 L11（经典）两层；Rust 前端 99→218。

## 3. 关键概念

1. **MRV2（Model Runner V2）**：从第一性原理重写的执行层——持久批与输入解耦（请求持有固定行、抢占即完成，`vllm/v1/worker/gpu/states.py:10`）、async-first。`vllm/config/vllm.py:731` 裁决启用（HiSparse/水印强制，开关 `vllm/envs.py:316`），选择点 `vllm/v1/worker/gpu_worker.py:577`，MRV2 实现入口 `vllm/v1/worker/gpu/model_runner.py:202`。V1 仍在服役，改代码先分辨代际。
2. **VllmConfig 聚合根（config 目录化）**：28 子模块聚合+交叉校验于 `vllm/config/vllm.py:349`（3672 行），CLI 单一事实源是 `vllm/engine/arg_utils.py:489` 的 EngineArgs（3285 行）。
3. **Platform 抽象**：`vllm/platforms/interface.py:137` 定义能力接口，`vllm/platforms/__init__.py:240` 三级解析（插件 > `VLLM_PLATFORM` > 自动探测）装配 current_platform。
4. **V1 引擎与 msgspec IPC**：AsyncLLM（`vllm/v1/engine/async_llm.py:93`）×独立进程 EngineCore（`vllm/v1/engine/core.py:123`），协议 msgspec 化（`vllm/v1/engine/__init__.py:137` 起 14 类）。
5. **Continuous batching 调度器**：`vllm/v1/core/sched/scheduler.py:86`（3726 行）每 step 重排批，waiting 凑预算 prefill、running 各出 1 token，配抢占与 chunked prefill。
6. **KVCacheSpec 类型系统**：`vllm/v1/kv_cache_interface.py:202` 起 19 个 spec + `:40` KVQuantMode 15 态；调度块与哈希块分离（`vllm/config/cache.py:354`），块池与前缀缓存 `vllm/v1/core/block_pool.py:137`。
7. **Attention backend 抽象**：契约 `vllm/v1/attention/backend.py:59`，注册表 `vllm/v1/attention/backends/registry.py:34`（57 成员）；MLA 公共层 `vllm/model_executor/layers/attention/mla_attention.py:426`（3402 行）。
8. **投机解码家族（两层）**：proposer 基类 `vllm/v1/spec_decode/llm_base_proposer.py:73`；speculator 树 `vllm/v1/worker/gpu/spec_decode/speculator.py:63`（dflash/dflash2/dspark/eagle/gemma4/mtp/ngram/xpress/lilicorr 各自成族）；方法谱系 `vllm/config/speculative.py:74`。
9. **kv_offload 原生卸载**：Spec/Manager/Worker 三层（`vllm/v1/kv_offload/base.py:717`）；CPU 共享 mmap `vllm/v1/kv_offload/cpu/shared_offload_region.py:87`，二级级联 `vllm/v1/kv_offload/tiering/base.py:135`。
10. **KV/EC/weight transfer 三族**：PD 分离契约 `vllm/distributed/kv_transfer/kv_connector/v1/base.py:181`（805 行 51 方法），工厂 `vllm/distributed/kv_transfer/kv_connector/factory.py:27`；RL 权重热更新 `vllm/distributed/weight_transfer/base.py:428`；EC transfer 传 encoder 特征。
11. **FusedMoE 三步执行**：`vllm/model_executor/layers/fused_moe/modular_kernel.py:58`——[Router]→[Quantize-Dispatch]→[Permute-Experts-Unpermute]→[Combine]；入口 `vllm/model_executor/layers/fused_moe/layer.py:92`，专家收口 `vllm/model_executor/layers/fused_moe/routed_experts.py:73`。
12. **量化格式×后端矩阵**：每格式（FP8 样例 `vllm/model_executor/layers/quantization/fp8.py:92`）下挂通用+供应商后端，MoE oracle 做"格式→后端"选择；online/ 支持运行时重量化。
13. **模型双轨制**：经典注册表 `vllm/model_executor/models/registry.py:1166`（基线 `vllm/model_executor/models/llama.py:464`）vs 厂商目录（硬件隔离入口范例 `vllm/models/deepseek_v4/__init__.py:12` 按 current_platform 分发）；能力协议集中 `vllm/model_executor/models/interfaces.py:178`。
14. **声明式 parser 与 renderers**：`vllm/parser/engine/parser_engine.py:111`（1268 行）按 terminals/状态转移一次同抽 reasoning+tool call，`vllm/parser/abstract_parser.py:344` 桥接旧注册表；入向 `vllm/renderers/base.py:106`（68 方法）。
15. **Rust 前端**：gRPC 服务 `rust/src/server/src/lib.rs:197`、引擎客户端 `rust/src/engine-core-client/src/client.rs:279`（负载均衡 `rust/src/engine-core-client/src/client/state.rs:201`）、托管 `rust/src/managed-engine/src/process.rs:88`、HF 模板 Rust 化 `rust/src/parser/src/unified/hf/parser.rs:49`。

## 4. 推荐学习路径（16 步）

### Step 1 全仓印象：从安装到 import
`setup.py`（1752 行）定义包形态与编译扩展，`vllm/__init__.py:21` 暴露顶层 API。先建坐标系再钻细节。
### Step 2 配置体系：一切从 EngineArgs 开始
EngineArgs 翻译 CLI（`vllm/engine/arg_utils.py:489`），VllmConfig 聚合校验；`vllm/config/model.py:152` 与 `vllm/config/cache.py:182` 最常读。理解启动的钥匙。
### Step 3 V1 引擎主循环
`vllm/v1/engine/core.py:123` 跑 engine_step，`vllm/v1/engine/core_client.py:376` 经消息队列取流式结果。看懂"请求如何被消费"。
### Step 4 调度器与 KV 预算
`vllm/v1/core/sched/scheduler.py:86` 决定组批/抢占/chunked prefill，`vllm/v1/core/kv_cache_manager.py:131` 计量 KV 规格。看懂"为什么这样分批"。
### Step 5 GPU Worker：真正跑 forward 的地方
`vllm/v1/worker/gpu_worker.py:197` 管生命周期（权重加载/warmup/显存 profile），双代 runner 选择见第 3 节 1 条。性能与显存问题第一现场。
### Step 6 torch.compile 与 CUDA Graph 捕获
`vllm/compilation/backends.py:828` 分段捕获，`vllm/compilation/decorators.py:86` 装饰器接入模型，`vllm/compilation/breakable_cudagraph.py:247` 新一代 breakable cudagraph。解释"低 batch 延迟为什么稳"。
### Step 7 注意力后端全家桶
registry 按平台分发：FlashAttention（`vllm/v1/attention/backends/flash_attn.py:286`）、FlashInfer、MLA（`vllm/v1/attention/backends/mla/flashattn_mla.py:40`）。精读 flash_attn+一个 MLA 建立全局感。
### Step 8 采样与流式去分词
`vllm/v1/sample/sampler.py:78` 落实采样参数（`vllm/sampling_params.py:271` 已迁 msgspec），`vllm/v1/engine/detokenizer.py:31` 增量去分词。引擎输出→用户文本。
### Step 9 算子、量化与 MoE
`vllm/model_executor/layers/linear.py:436` 投影层基座、`vllm/model_executor/layers/quantization/fp8.py:92` 量化样例、`vllm/model_executor/layers/fused_moe/layer.py:92` MoE 网关、`vllm/model_executor/layers/logits_processor.py:58` lm_head 收口。
### Step 10 模型实现的双轨制
经典注册表与厂商目录并存（第 3 节 13 条），`vllm/model_executor/model_loader/__init__.py:131` 把权重装进任一实现。对比两轨看演进方向。
### Step 11 分布式与 PD 分离
`vllm/distributed/parallel_state.py:1839` 初始化进程组，kv_transfer 把 prefill/decode 拆到不同节点（先读 `vllm/distributed/kv_transfer/README.md:1`），弹性 EP 四状态机 `vllm/distributed/elastic_ep/elastic_state.py:38`。扩吞吐主流架构。
### Step 12 OpenAI 兼容服务与离线 LLM
`vllm/entrypoints/openai/api_server.py:25` 起已是弃用垫片，真实入口 `vllm/entrypoints/launchers/api_server/entry.py:204`；对话端点 `vllm/entrypoints/openai/chat_completion/serving.py:123`、离线 `vllm/entrypoints/llm.py:62`、CLI `vllm/entrypoints/cli/serve.py:51`。
### Step 13 流式输出解析管线
`vllm/parser/engine/parser_engine.py:111` 声明式引擎，tool_parsers/reasoning 正向它迁移，`vllm/renderers/base.py:106` 管入向渲染。保证 API 语义正确。
### Step 14 多模态、LoRA 与 HF 兼容
`vllm/multimodal/__init__.py:7` 注册 processor，`vllm/multimodal/inputs.py` 的三态字段与 Rust 前端逐位对齐；`vllm/transformers_utils/processor.py:1` 是 HF 垫片。
### Step 15 平台适配层
`vllm/platforms/interface.py:137` 能力接口，`vllm/platforms/cuda.py:226` 与 `vllm/platforms/rocm.py:653` 各自实现。Step 7/9 的"按平台选路径"都汇聚于此。
### Step 16 Rust 前端：另一种打开方式
gRPC/客户端/托管/契约见第 3 节 15 条，与 Step 12 的 Python 入口对照，理解性能化演进方向。

## 5. 文件地图（按层速查）

- **V1 引擎（L3）**：`v1/engine/` 下 core（2962 行）/core_client（2205 行）/input_processor/output_processor/detokenizer/async_llm，协议集中在 `__init__.py`（359 行 14 类）
- **调度与 KV（L3/5）**：`v1/core/sched/scheduler.py`（3726 行）· `kv_cache_manager.py` · `block_pool.py` · `v1/kv_cache_interface.py`（1660 行）· `v1/kv_offload/`
- **执行与投机（L4）**：`v1/worker/gpu_model_runner.py`（V1，7192 行）· `v1/worker/gpu/model_runner.py`（MRV2，2547 行）· `gpu/cudagraph_utils.py` · `gpu/spec_decode/speculator.py` · `v1/spec_decode/llm_base_proposer.py` · `v1/worker/ubatching.py`（DBO 微批）· `v1/watermarking/gumbel.py`
- **注意力（L5）**：`v1/attention/backend.py`（1160 行）· `backends/registry.py` · `backends/flash_attn.py`（1879 行）· `layers/attention/mla_attention.py`（3402 行）
- **量化与 MoE（L8/9）**：`layers/quantization/__init__.py` · `fp8.py` · `fused_moe/modular_kernel.py`（1841 行）· `fused_moe/layer.py` · `layers/linear.py`（1833 行）
- **模型与加载（L10/11）**：`model_executor/models/registry.py`（1636 行）· `interfaces.py`（2016 行）· `models/llama.py` · `models/deepseek_v2.py`（2010 行）· `models/transformers/base.py` · `model_loader/weight_utils.py`（1936 行）· `warmup/jit_warmup.py`
- **分布式（L6）**：`distributed/parallel_state.py`（2780 行）· `kv_transfer/kv_connector/v1/base.py` · `weight_transfer/base.py` · `ec_transfer/` · `elastic_ep/` · `eplb/eplb_state.py`
- **入口与解析（L13/14/15）**：`entrypoints/launchers/` · `entrypoints/openai/chat_completion/serving.py` · `entrypoints/generate/api_router.py`（多协议统一挂载）· `entrypoints/rl/online/api_router.py`（RL 热更新）· `snapshot/controller.py`（CRIU 快照）· `parser/engine/parser_engine.py` · `renderers/base.py` · `rust/src/server/src/lib.rs`

## 6. 复杂度热点（新人绕行区）

行数 @ `06e172b5cf` 实测：

| 文件 | 行数 | 复杂点 |
|---|---|---|
| `v1/worker/gpu_model_runner.py` | 7192 | V1 总驱动，批组装/CUDA Graph/投机/多模态全耦合 |
| `v1/core/sched/scheduler.py` | 3726 | 调度+抢占+KV 预算+spec 元数据耦合 |
| `config/vllm.py` | 3672 | 聚合根，改一处牵全仓 |
| `layers/attention/mla_attention.py` | 3402 | 全仓 MLA 公共层 |
| `engine/arg_utils.py` | 3285 | 数百参数类型驱动组装 |
| `v1/engine/core.py` | 2962 | 独立进程+DP/MoE 弹性 Actor |
| `distributed/parallel_state.py` | 2780 | 全局单例，引用最广 |
| `config/speculative.py` | 2172 | 11 族 speculator 合法性矩阵 |
| `model_executor/models/interfaces.py` | 2016 | Supports* 协议中枢 |
| `model_executor/model_loader/weight_utils.py` | 1936 | 多迭代器与 loader 变体 |

改动前 `git log -- <file>` 看节奏；MRV2 迁移期先 `grep -rn use_v2_model_runner` 确认代际，别改错代。

## 7. 两个月演进增量与旧版勘误（2026-09 → 2026-10）

- **入口重构（旧版最大错误）**：`entrypoints/openai/api_server.py` 从主入口变 59 行弃用垫片，真实路径迁 `entrypoints/launchers/`；旧单文件 `openai/serving.py` 拆为 chat_completion/completion/responses/decisions/models 子包；Anthropic/Cohere 兼容层继承 OpenAIServingChat 做纯翻译；多协议路由统一挂 `vllm/entrypoints/generate/api_router.py:21`。
- **MRV2 出现**：旧版完全没有的概念；V1 巨型 runner 未删、仍在默认路径。
- **投机解码扩容**：EAGLE/MTP/ngram → 11 族 speculator（+dflash/dflash2/dspark/xpress/lilicorr/gemma4/multi_module_mtp/ngram_gpu/suffix/fly）。
- **全新子系统**：`v1/kv_offload/` 原生卸载 · `distributed/weight_transfer/`+`entrypoints/rl/` RL 训推一体 · `distributed/elastic_ep/` 弹性 EP · `entrypoints/scale_out/` · `vllm/snapshot/` CRIU 快照（`vllm/snapshot/controller.py:58` create/`:96` restore）· `v1/watermarking/`（`vllm/config/watermarking.py:27`）· Decisions API（`vllm/entrypoints/openai/decisions/strategies.py:145`）· `vllm/models/` 厂商目录 15 族。
- **口径修正**：模型 280+→292+15 族；tool parser 40+→55 且向 parser 引擎迁移；vendored configs 37→40；attention backend 55+→57；`entrypoints/chat_utils.py`→`vllm/renderers/chat_utils/`；config 成 28 子模块目录（VllmConfig 3036→3672 行）；量化扩成 MXFP4/6/8+NVFP4 格式族矩阵+在线量化；Rust 前端 99→218 文件。

## 8. 新人上手建议与下一步

**五分钟**：`pip install vllm` → `vllm serve <model>` → `curl :8000/v1/chat/completions`；离线 `LLM(model=...)`（`vllm/entrypoints/llm.py:62`）。

**第一周**：①Step 1-6 通读主线（约两天），Step 7-11 选两条深潜；②常开两个查询入口：`vllm/envs.py` 查开关、`vllm/config/vllm.py` 查配置关系；③改调度/KV 后用 `vllm bench serve` 或 Rust bench 量化收益；④报错栈 `gpu_model_runner.py`=V1、`gpu/model_runner.py`=MRV2，提 issue 写明代际与 `VLLM_USE_V2_MODEL_RUNNER` 取值。

**下一步**：配套 `../explain/` 精讲与 DeepWiki 页库；图谱本体在仓内 `.understand-anything/knowledge-graph.json`（可下钻任意子系统）。

---

*生成：2026-11-01 · 数据源：`.understand-anything/onboard-input.json`（2026-10-31，commit `06e172b5cf`）· 行号锚全部回源码核实*
