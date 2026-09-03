# vLLM v1 深度解析：GPUModelRunner（gpu_model_runner.py）

> 文件：`vllm/v1/worker/gpu_model_runner.py`（约 7700 行，v1 引擎最大单文件）
> 知识图谱 layer：`gpu-worker`（GPU 执行 Worker，124 节点），107 条 import 出边，被 cpu/xpu_model_runner 继承

## 角色定位

`GPUModelRunner` 是**单次模型 forward 的总指挥**：从 SchedulerOutput 出发，组装输入张量、构建 attention 元数据、决定 CUDA graph 路径、驱动模型 forward、采样、投机解码起草，最后把 token 送回调度器。如果说 Scheduler 是大脑（决定"跑什么"），ModelRunner 就是小脑（决定"怎么跑"）。它通过三个 Mixin 横向扩展能力：`LoRAModelRunnerMixin`（LoRA 装载）、`KVConnectorModelRunnerMixin`（KV 传输）、`ECConnectorModelRunnerMixin`（encoder 传输）。

在生命周期中：Worker 在 `init_device` 时构造它 → `load_model` 装载权重 → `initialize_kv_cache` 建显存池 → `capture_model` 捕获 CUDA graph → 稳态时每步被 `execute_model` + `sample_tokens` 驱动。

## 内部结构（关键成员）

- **请求状态**：`self.requests: dict[req_id, CachedRequestState]` + `self.input_batch: InputBatch`（persistent batch，见 gpu_input_batch 篇）。
- **持久 GPU buffer**（CUDA graph 的静态地址根基）：`input_ids / positions / query_start_loc / seq_lens / num_computed_tokens / req_indices / is_token_ids` 等，全部按 `max_num_tokens`、`max_num_reqs` 预分配，多数通过 `_make_buffer` 做成 CPU pinned + GPU 双份的 `CpuGpuBuffer`。
- **注意力体系**：`kv_caches: list[Tensor]`（物理显存）、`attn_groups[gid][i]`（group→backend 细分，支持滑窗/Mamba/全注意力混组）、per-layer metadata builders。
- **执行决策**：`cudagraph_dispatcher`（FULL/PIECEWISE 分派 + 捕获尺寸表 `cudagraph_batch_sizes`）。
- **投机解码**：`drafter`（EAGLE/Medusa/ngram/DFlash/Step3.5-MTP 等 10 种 proposer）+ `rejection_sampler`；`num_spec_tokens` 决定 `uniform_decode_query_len = 1 + num_spec_tokens`。
- **异步输出**：`AsyncGPUModelRunnerOutput` 在旁路 copy stream 上把 sampled_token_ids/logprobs D2H，事件同步后才 `get_output()`。
- **`ExecuteModelState`**（NamedTuple）：execute_model 与 sample_tokens 之间的两段式交接状态。

## 数据流：execute_model → sample_tokens

**`execute_model(scheduler_output)`** 返回 `None` 并把中间态存进 `self.execute_model_state`（配合 overlap scheduler 的拆步设计）。内部流水：

1. `_update_states()`：同步 persistent batch——移除 finished/unscheduled 请求、新增请求建 CachedRequestState、追加 running 请求的 new_block_ids、执行 KV-zero 清零与 CoW 块拷贝、返回延迟校正闭包（async scheduling 下推迟到 launch 后再等上一步校正）。
2. `_prepare_inputs()`：**先 `commit_block_table(num_reqs)` 启动 H2D**，让块表拷贝与后续 CPU 计算重叠；再用 `np.repeat` 算 req_indices、cumsum 算 query_start_loc，`torch.index_select` 从 token_ids_cpu 大表里按 `position + req_index × max_model_len` 稠密gather出本步 input_ids。
3. `_compute_cascade_attn_prefix_lens()`：若启用 cascade attention，结合 `num_common_prefix_blocks`（来自 KVCacheManager）算逐请求前缀长。
4. `_determine_batch_execution_and_padding()`：判定 uniform decode（`max_scheduled == 1+spec_tokens` 且 `num_tokens == max × num_reqs`）→ 选择 CUDAGraphMode（FULL 走捕获图 / PIECEWISE 走分段图 / NONE 走 eager）与 padding 目标形状；DBO microbatching 时 `_allow_microbatching` 会否决"读到自己 batch 内正在写的 prefix"的切分。
5. `_get_slot_mappings()` + `_build_attention_metadata()`：前者算 KV 写入槽位（可按 kernel_block_size 细分），后者组装 `CommonAttentionMetadata`（query_start_loc/seq_lens/block_table/slot_mapping）并分发给各组 builder（如 FlashAttentionMetadataBuilder.build）；FULL graph 模式下 block_table 空洞填 `NULL_BLOCK_ID`。
6. `_preprocess()` 产出 input_ids/positions/intermediate_tensors 后，进入 `set_forward_context(...)` 上下文（把 attn_metadata 挂进全局 forward context，供编译图内取用），调 `_model_forward()` → `self.model(...)`。
7. 非 last PP rank 返回 IntermediateTensors 给 Worker 发送；last rank `compute_logits(hidden_states[logits_indices])`——**只对每个请求最后一个采样位算 logits**。

**`sample_tokens(grammar_output)`**：取出 ExecuteModelState → 结构化输出 bitmask 掩 logits → `_sample()` 采样 → `_update_states_after_model_execute` 回写 token → （spec decode）按 drafter 类型决定 bookkeeping 前还是后起草：EAGLE/DraftModel 类直接吃 GPU 采样结果不等回 CPU，ngram 类等 CPU token → `_bookkeeping_sync()` 做 logprobs/prompt_logprobs 的 D2H 与解析 → 返回 `ModelRunnerOutput`；async scheduling 时包成 `AsyncGPUModelRunnerOutput`（旁路流拷贝），并把 CPU tensor 引用存回 input_batch 供下一步 penalties 修补占位 token。

## 关键设计决策

- **persistent buffer + 静态形状**：所有模型输入写入预分配 buffer，CUDA graph 重放时地址不变，只需改内容。这是"graph 捕获一次、无限重放"的前提。
- **uniform decode 判定**：只有"每请求恰好 1（+spec）个 token"的纯 decode 才能命中以 batch 维捕获的图；混合 chunked prefill 走 piecewise 或 eager。`_is_uniform_decode` 一行判断决定了 vLLM 最核心的性能分岔。
- **两段式 execute/sample**：让调度器在 forward 还在 GPU 上跑时就开始准备下一步（overlap），代价是状态交接复杂（`deferred_state_corrections_fn`、placeholder token -1 修补）。
- **capture_model 先捕大 shape**：`cudagraph_dispatcher.get_capture_descs()` 从大到小捕获，小图复用大图内存池；捕获前 warmup 若干次并 `torch.accelerator.synchronize()`，防止辅助流工作未完成污染捕获。

## 新人提示

- 切入点：先读 `__init__` 的 buffer 分配段（819-901 行）建立"静态形状"心智，再读 `execute_model`（4250 起）按上述七步对照，最后读 `_update_states`。
- 易混淆点①：**FULL vs PIECEWISE cuda graph**——FULL 把整步 forward 录进一张图（含 attention，要求 uniform batch + padding）；PIECEWISE 只录 attention 之外的编译段，attention 仍 eager（所以 FA forward 里的注释强调"此函数 eager 执行，慎加 CPU 开销"）。
- 易混淆点②：`_update_states` 里 unscheduled 请求被移出 persistent batch 但 `self.requests` 保留其状态——前者是"这步不跑"，后者是"还在世"（可能被抢占等待恢复）。
- 易混淆点③：logits_indices 不是全 token——prefill 时一个请求只留最后一个位置的 logits（除非要 prompt logprobs）。
- 文件里大量 `record_function_or_nullcontext` 是 profiler 埋点，跳读时可忽略。
