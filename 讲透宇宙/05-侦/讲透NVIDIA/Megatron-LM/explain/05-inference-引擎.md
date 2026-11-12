# 05 · inference 引擎——DynamicInferenceContext、双引擎与 MTP 投机解码

> 主战场：`megatron/core/inference/`（全目录 46734 行 Python）。`contexts/dynamic_context.py` 以 **5326 行居全仓之冠**，`engines/dynamic_engine.py` 4798 行、`text_generation_controllers/text_generation_controller.py` 3863 行紧随——三大件构成 mcore 自带的推理引擎内核。

## ① 角色定位：这个子系统解决什么问题

mcore 不只想做训练框架，还要让**同一套并行切分的模型直接对外服务**。这要求它自己长成一个推理引擎：请求进、token 出的完整闭环——连续批（in-flight batching，任意时刻可增删请求）、页式 KV cache（显存切块动态分配）、prefix caching、投机解码（MTP）、多模态、断点 KV 交接（disaggregation），以及 asyncio 原生的高层 API 与 OpenAI 兼容服务。与 vLLM 的关系是**借鉴而非依赖**：`async_stream.py` 文件头直接标注 "adopted from vllm-project/vllm"，高层 API `MegatronAsyncLLM` 也对齐 vLLM 的调用形态（multimodal dict 按 "vLLM's modality-dictionary shape"，apis/_llm_base.py:452），但引擎本体是 mcore 原生实现，能吃到 TP/PP/EP 全套并行与 GTP 权重分片。

## ② 内部结构：关键类/函数与行号锚

**DynamicInferenceContext（`contexts/dynamic_context.py:343`）**：docstring 自述双职责——in-flight batching + 块级 KV cache（"similar to paged attention"）。94 个方法覆盖：prefix caching 全套计数器（:386-406，命中数/跳过的 prefill token 数，注释解释"高 skip 比例才能证明延迟增长是注意力而非重复 prefill"）、`_request_to_image_embeddings` 等多模态请求表（:409-411）、MLA latent cache 断言块大小必须 64（:414-419，"Flash MLA requires a block size of 64"）。头部 import 即依赖清单：`KVBlockAllocator`/`MambaSlotAllocator`（contexts/kv_block_allocator.py:17、mamba_slot_allocator.py:32）、`MambaMetadata`、`MTPContextMixin`、`RoutingMetadata`（MoE 推理路由）、`ContextGPUView`（gpu_view.py:6，在 :1540 挂载）。**MTPContextMixin（`contexts/mtp_context_mixin.py:25`）** 是投机解码的上下文侧：`should_enable_mtp_kv_cache`（:29）、lookahead token 的 `_decode_kv_lookahead_tokens`（:203）、`_mtp_trim_prefix_match`（:150）、`_mtp_begin_decode`（:336）等 19 个方法。

**双引擎（`engines/`）**：`StaticInferenceEngine`（static_engine.py:36）"does a simple forward pass"，固定 batch/seq——批处理/评测用；`DynamicInferenceEngine`（dynamic_engine.py:447，4798 行）才是服务主角，"requests of varying length to be dynamically added and removed in each inference step"。引擎状态机 `EngineState`（:262，RUNNING/PAUSED/SUSPENDED/RESUMED/STOPED 映射到 asyncio 事件）、`add_request`（:1964）、KV 交接版 `add_request_with_kv_handoff`（:660，配 disaggregation/inference_state_handoff.py 1230 行）、`step_modern`（:4097）与 `step_legacy`（:4101）两代步进并存。类属性 `_weight_epoch`（:475-480）的注释解释了为何用类级默认——测试经 `object.__new__` 造引擎时 init 不跑。

**调度与 API**：`Scheduler`（scheduler.py:17）维护 OrderedDict 请求表与 max_batch_size；`MegatronAsyncLLM`（apis/async_llm.py:20）是 asyncio 原生高层 API——`generate`（:77）、pause/unpause/suspend/resume/shutdown 生命周期（:126-168）、`serve` 起 OpenAI 兼容 HTTP（:185），强制 `use_coordinator=True`。流式输出走 `AsyncStream`（async_stream.py:17，vLLM 移植，`call_soon_threadsafe` 投递 + STOP_ITERATION 哨兵）。

**MTP 投机解码双实现（`text_generation_controllers/mtp_utils_{pytorch,triton}.py`）**：两文件 API 完全同构，各有四个顶层函数——`rewind_kv_cache`、`verify_speculative_tokens`、`prepare_next_forward_pass`、`mamba_state_selective_copy`。**职责分派**在 text_generation_controller.py:69-74：`rewind_kv_cache` 从 **pytorch 版**导入，其余三个从 **triton 版**导入。pytorch 版 rewind（mtp_utils_pytorch.py:6）docstring 写明回退三件事（kv_length_offsets/last_kv_block_offset/跨块边界时回收块），并有 `.tolist()` 批量取标量的优化注释（"Avoids N round-trips through the Python/C++ boundary"）；triton 版 rewind（mtp_utils_triton.py:105）的 kernel（:26）grid 按 CUDA-graph 兼容补零——"Programs with `pid >= num_active_requests` are padding and produce safe no-op outputs"。triton 版 `mamba_state_selective_copy`（:413）把 (L, M, S+1, *state_shape) 中被接受的中间状态拷回当前状态，grid=(N, num_layers, chunks)。

**philox 重放坑（`sampling/flashinfer_sampling.py:20-35`）**：`FlashInferSampling` docstring 明写为何永远 eager：**"FlashInfer bakes the philox state into a graph as a by-value constant at capture, so a captured sampler replays identical random numbers"**（附 LinkedIn 文章链接）——采集进 CUDA graph 的采样器每步重放同一批随机数，所以 kernel 选择数据依赖 + RNG 前进两个理由都要求采样留在 graph 外。每步按 batch 过滤器组合分派四条路径（logits/top-p/top-k/joint，:104-130）。

## ③ 外部连接：与哪些子系统互依

图谱里 parallel_state 的第二大消费方就是本目录（7 条入边）。向上：模型层经 `model_inference_wrappers/` 包成可调用对象，GPT/DeepSeek/hybrid 模型全走这条路；第 04 篇的 SSMDynamicInferenceMixin 直接 import 本目录的 `DynamicInferenceContext` 与 attention_context/triton tensor_ops，mamba_metadata/mamba_slot_allocator 是引擎替 SSM 层维护的状态。向下：`symmetric_memory.py`（184 行）被 parallel_state 反向 import（destroy 时终结）；MoE 推理路由用第 02 篇的 `token_dispatcher_inference`（NVLSAllGatherVDispatcher 等，dynamic_context.py:27-31）。横向：`moe/vllm_fused_moe.py`（887 行）+ `moe/permute.py`（783 行）是采自 vLLM 生态的 fused MoE 内核族；`disaggregation/` 连 prefill/decode 分离部署；`batch_dimensions_utils.py`（813 行）负责 packed batch 的维度簿记。MoELayer 头部反向 import 这里的 InferenceMode（moe_layer.py:35），训练/推理同层分岔。

## ④ 数据流：一次典型调用的路径

动态批一步（带 MTP 投机）：

1. 客户端 `await llm.generate(prompt)` → coordinator（`use_coordinator=True` 的 DP 协调器）把请求路由到某 rank → `Scheduler.add_request` → `DynamicInferenceContext.add_request`（:3395）登记请求、按 prefix caching 匹配块。
2. `DynamicInferenceEngine.step_modern`（:4097）：`prepare_requests`（:4204）组 batch——decode 请求与 prefill 请求混进 packed 序列，`ContextGPUView` 聚合 GPU 侧视图。
3. 模型 forward（含第 02/03/04 篇的 MoE、CSA、SSM 层），MTP 层产出 k 个 draft token，主模型一步验证。
4. 采样（FlashInferSampling eager 四路分派）；`verify_speculative_tokens`（triton）算每请求接受数。
5. `rewind_kv_cache`（pytorch）把 KV 簿记回退到接受位置；SSM 层 `mamba_state_selective_copy`（triton）回滚递归状态到快照；释放的多余块可留作 lookahead（keep_extra_blocks 语义，mtp_utils_pytorch.py docstring）。
6. token 经 AsyncStream 流回客户端；`DynamicInferenceEngineStepResult`（:436 TypedDict）回给引擎循环；KV 池/块计数器更新，prefix 命中率入日志。

## ⑤ 设计决策：为什么这么设计

**为什么 rewind 用 PyTorch 而验证/准备用 Triton？**（推断自 import 分派与两版注释）rewind 的循环体是"每请求几个标量更新"，pytorch 版用 `.tolist()` 一次拿全部标量后在 CPU 端循环反而便宜且可读；而 verify/prepare/mamba 回滚是逐 token/逐状态的张量级操作，Triton kernel 收益大。两版 API 同构保留了替换自由——triton rewind 也写好了（含 graph 兼容 padding），随时可切换。

**为什么采样器绝不进 CUDA graph？** philox 坑是硬约束：graph 捕获时 RNG 状态被按值固化，重放=每步同随机数，采样多样性被静默破坏。docstring 引用外部文章说明这是社区踩过的真实崩溃/漂移问题（"Pinned RNG drifting & crash from CUDA graph"）。mcore 的解法是承认"采样必须 eager"，并把它设计成 FlashInferSampling 的类契约（构造参数 `enable_cuda_graph` 接受但显式 `del`，:44-45）。

**为什么 5326 行堆在一个类？** DynamicInferenceContext 把 in-flight batching、块分配、prefix cache、MTP 元数据、多模态、MoE 路由全部收编——因为这些状态**必须对同一步的组装保持一致视图**，拆成多个对象会让每步组装陷入跨对象同步。用 Mixin（MTPContextMixin）切分关注点而不切分状态，是巨型上下文类的折中（推断：graph 甄别也把它标为全仓最大文件，属于"复杂度中心"而非坏味道）。

**为什么双引擎并存？** 静态引擎服务于离线批量生成与测试（无调度状态机、无 KV 页管理，行为可预测）；动态引擎服务在线。两者共享 controller 与 sampling，差异只在批组装——上层 API 按场景选引擎而不是删旧留新。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：`README.md` → `engines/static_engine.py`（最短闭环）→ `scheduler.py`（193 行）→ `dynamic_engine.py` 只读 :447-500 与 step_modern → `dynamic_context.py` 的 :343-460（双职责 docstring+init）→ `text_generation_controller.py` 的 MTP 段（:917 `_rewind_kv_cache`、:2197 调用点）→ mtp_utils 两文件对照读。
- **巨型文件策略**：dynamic_context.py 94 个方法别线性读，按"add_request → prepare_requests → step 消费"三条主线索 grep。
- **块大小 64 的硬约束**：cache_mla_latent 模式下 assert 拦截（:414-419），Flash MLA 用户必须显式设 `--inference-dynamic-batching-block-size 64`。
- **philox 坑是通用教训**：任何把 RNG 消费者捕进 CUDA graph 的尝试都会静默复现同一随机数；本仓用"eager + seeded generator + philox offset 前进"保可复现性。
- **mtp_utils 双实现是对照实验场**：改投机解码逻辑时两个文件都要改（API 同构是约定不是强制），漏改 pytorch 版会让 CPU 路径行为分叉。
- `step_modern`/`step_legacy` 两代并存（:4097/:4101），读调度逻辑先确认 config 选的是哪代；`EngineSuspendedError`（:277）与 pause/suspend 生命周期是服务运维路径，离线用户可跳过。
- 相关但独立：`disaggregation/`（KV 交接）与 `data_parallel_inference_coordinator/`（DP 请求路由）是部署形态差异，初读可先不管。
