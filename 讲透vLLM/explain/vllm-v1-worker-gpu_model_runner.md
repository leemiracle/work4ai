# vllm/v1/worker/gpu_model_runner.py — GPUModelRunner：GPU 执行总指挥（V1 大本营）

> 源码：`vllm/v1/worker/gpu_model_runner.py`（7192 行，全仓最大单文件）｜V2 新一代在 vllm/v1/worker/gpu/model_runner.py（2547 行，目录化重构中）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`GPUModelRunner` 是**单次 forward 的总指挥**：从 SchedulerOutput 出发，同步 persistent batch、组装输入、构建 attention 元数据、定 graph 路径、驱动 forward、采样、投机解码起草。Scheduler 决定"跑什么"，它决定"怎么跑"。三个 Mixin（vllm/v1/worker/gpu_model_runner.py:476）：LoRA/KVConnector/ECConnector。生命周期：构造（:478）→ load_model（:4967）→ initialize_kv_cache（:6990）→ capture_model（:6417）→ 稳态两段驱动。2026-09→10 形态级变化：**cascade attention 整体移除**（:541 只剩残迹）；graph 新增 Breakable 与 DBO；drafter 扩到 10+；async 修补链 GPU 化。V2 走 use_v2_model_runner 分叉（vllm/v1/worker/gpu_worker.py:577）。

## ② 内部结构

文件三段：异步输出包装（`AsyncGPUModelRunnerOutput`:269，旁路流 D2H sampled/logprobs/NaN/EP fault :313）、`ExecuteModelState`（:459，十字段交接）、主体（:475）。

`__init__` 重镇：drafter 十路分派（:598-668，ngram/GPU-ngram/suffix/eagle/dflash/gemma4-MTP/step3p5-MTP 等）+ RejectionSampler（:666）；InputBatch 占位 block_size 先建（:717，:692 注释引 PR #18298：须在 load_model 前）。**持久 buffer 群**（:774-857，graph 静态地址根基）：CpuGpuBuffer 系（input_ids/query_start_loc/req_indices…）+ is_padding（:781）/optimistic_seq_lens_cpu（:790）/**prev_positions**（:801，当前行→上一步行映射）/**discard_request_mask**（:818）；num_accepted_tokens 初始 fill(1)（:827，recurrent 内核取 accepted-1 作状态槽）；cudagraph_dispatcher（:876）。

注意力体系：kv_caches（:581）+ attn_groups[gid][i]（:583，按 (full_cls_name, kv_cache_spec, num_heads_q) 三元去重 :6631）；per-group builders（:6728，DBO 每 ubatch 一个）。

## ③ 外部连接

- **上游**：Worker 驱动（vllm/v1/worker/gpu_worker.py:1337/:1330）；输入 SchedulerOutput。
- **下游**：模型本体（`_model_forward`:3586 单点可覆写）；attention backends（:2363）；CudagraphDispatcher；drafter 与 mamba_utils（:1573）。
- **被继承**：cpu/xpu runner 复用骨架；V2 继承职责而非代码（:962/:1160 钩子为子类而留）。

## ④ 数据流：execute_model（:3906）六步 → sample_tokens（:4270）

1. **`_update_states`**（:1176）：清 finished（:1187）→ 新块 KV-zero（:1205）+CoW（:1207）→ unscheduled 移出 batch 但留 self.requests（:1231，"这步不跑"≠"不在世"）→ 新请求建 CachedRequestState（:1279）→ async spec decode 乐观 `extend([-1]*n)` 登记延迟校正（:1343）→ add+condense+reorder（:1105，MLA 类后端按算力/带宽拆批）+refresh_metadata（:1491）→ 返回校正闭包（:1514）。
2. **`_prepare_inputs`**（:1924）：**先 commit_block_table 启动 H2D**（:1944）与 CPU 重叠 → 批状 arange（:1948）→ index_select gather（:1971，比 np.take 快）→ prompt_embeds 填位（:1997）→ query_start_loc pad 非减（:2033）→ optimistic_seq_lens（:2045）→ async 时 GPU 校正 num_computed（:2107）→ positions/seq_lens（:2139）→ slot_mapping（:2148）→ `_prepare_input_ids`：async 用 prev_positions 在 GPU 侧 scatter 上步 token/draft（:1849）→ logits_indices：非 spec=`query_start_loc[1:]-1`（:2195，**每请求只留最后采样位**）。
3. **`_determine_batch_execution_and_padding`**（:3684）：`_is_uniform_decode`（:3620，最核心性能分岔）→ dispatcher 分派 → DP 对齐 padding（:3746）；DBO 时 `_allow_microbatching`（:3639）否决"读到自己 batch 内正在写的 prefix"的切分（:3662）。
4. **`_get_slot_mappings`**（:3822，padded 尾填 -1 :3870）+ **`_build_attention_metadata`**（:2253）：max_seq_len 取 optimistic 上界（:2290）→ block_table 空洞填 NULL_BLOCK_ID（:2309）→ CommonAttentionMetadata（:2363，带 mm_prefix:2334/R-SWA:2353/ReplaySSM:2357）→ **跨组缓存**：同 spec+builder 只 build 一次，其余 update_block_table 换表（:2409）→ drafter 表（:2512）+unpadded 视图（:2537）。
5. **`_preprocess`+forward**：spec 占位 clamp_(min=0) 防越界（:3277）；mm encoder+嵌入统一化（:3283，文本也走 embed）；三路分派（:3336）→ `set_forward_context`（:4154，metadata/batch_descriptor/slot_mappings/is_padding 挂全局上下文）→ `_model_forward`（mamba align 先 preprocess :4049）。
6. **收尾**：非 last PP rank 返回 IntermediateTensors（:4194）；last rank `hidden_states[logits_indices]` 只算采样位 logits（:4207）→ 存 ExecuteModelState（:4233）→ launch 后跑校正（:4249）→ 返回 None。

**`sample_tokens`**（:4270）：grammar bitmask 掩 logits（:4300）→ `_sample`（:3403）→ mamba 后处理（:1548）→ **drafter 时序三分**：GPU-token 系（EAGLE/DFlash/DraftModel 等）不等 CPU 吃采样结果（:4362）；CPU-token 系（ngram/suffix）bookkeeping 后起草（:4415）；超 drafter 长度**零起草**（:4420，脏 draft 腐蚀 Nemotron-H Mamba 态）→ `_bookkeeping_sync`（:4433）→ finalize_kv_connector（:4475）→ async 包 AsyncGPUModelRunnerOutput（:4505）并存 CPU 引用回 input_batch（:4520）。

## ⑤ 设计决策

1. **persistent buffer+静态形状**：graph 重放只改内容不改地址。**uniform decode 谓词是性能分岔**：只有"每请求恰好 1(+spec) token"的纯 decode 命中按 batch 维捕获的图，混合 chunked prefill 走 piecewise/eager。load_model（:4967）按模式包 BreakableCUDAGraphWrapper（:5139）/CUDAGraphWrapper（:5154，FULL）/UBatchWrapper（:5157，DBO），capture_model（:6417）大 shape 先捕小图复用池（:6435）、捕完 lock_workspace（:6510）。
2. **两段式+GPU 修补链**：execute 返回 None 存中间态，调度器在 GPU 忙时准备下一步；乐观占位-延迟校正（:1360/:1514/:2107）、prev_positions、scatter（:1849）构成"先假设、后回扣"信用系统——9 月以来复杂度增长最快地带。
3. **元数据跨组复用**：hybrid 组间同 spec+builder 只差 block table，update_block_table 免重复 build（:2409）。
4. **drafter 时序协议**：按"消费 GPU 还是 CPU token"归三类加零起草兜底；`_model_forward` 可整体替换。另有可观测内建：NaN 计数（:251）、EP fault（:313）、cudagraph_stats。

## ⑥ 新人提示

- 读法：:774-876 buffer 段 → :3906 按六步对照 → :1176 `_update_states` → :4270。
- 易混淆点①：**FULL vs PIECEWISE vs Breakable**——FULL 整步一张图（含 attention）；PIECEWISE 只录 attention 外编译段；Breakable 图内留断点。FA"eager 慎加 CPU 开销"警告（vllm/v1/attention/backends/flash_attn.py:1232）正因 piecewise。
- 易混淆点②：`cascade_attn_enabled=False`（:541）与 `use_cascade_attn` 形参（:3691）都是尸体——cascade 已随 #61126 移除。
- 易混淆点③：logits_indices 非全 token——prefill 每请求只留最后采样位（除非 spec/prompt logprobs）。
- 易混淆点④：num_computed_tokens 有 CPU 真值/GPU 校正/optimistic 三套时序，async spec decode 下逐步不同——追 bug 先分清在哪层。
- V2 线索：use_v2_model_runner 分流 gpu/ 新 runner；use_ubatching/use_replayssm 是 V1 内部演进，并行不悖。
