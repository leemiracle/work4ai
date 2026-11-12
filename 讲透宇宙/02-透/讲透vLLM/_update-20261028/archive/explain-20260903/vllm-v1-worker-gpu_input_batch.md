# vLLM v1 深度解析：InputBatch（gpu_input_batch.py）

> 文件：`vllm/v1/worker/gpu_input_batch.py`（约 1150 行）
> 知识图谱 layer：`gpu-worker`；被 gpu_model_runner、lora_model_runner_mixin、mamba_utils 与 4 个 spec_decode proposer 依赖

## 角色定位

`InputBatch` 是 **persistent batch 的运行时状态容器**：decode 阶段活跃请求的全量快照——token 序列、块表引用、采样参数、LoRA 归属，以及它们的增删换压缩。它解决的问题是：vLLM v1 没有传统的 SequenceGroup 对象图，而是用"**行号即请求**"的扁平结构 + CPU 大矩阵，让 ModelRunner 每步能用纯 numpy 向量操作组装输入。

设计前提写在 `_update_states` 的注释里：**persistent batch 优化假设连续 step 的请求集合高度重叠**。所以数据一旦写入就尽量不动，只做增量修补；只有请求离开才触发 `condense` 压缩。它在生命周期中属于 ModelRunner 的私有财产：`execute_model` 的 `_update_states` 增删行，`_prepare_inputs` 从中 gather 输入张量。

## 内部结构

**`CachedRequestState`**（dataclass）：单请求快照——`req_id / prompt_token_ids / mm_features / sampling_params / generator / block_ids: tuple[list[int], ...]（按 kv_cache_group 分组的块 id）/ num_computed_tokens / output_token_ids`，外加 mrope/xdrope 位置、LoRA、pooling 状态、`in_progress_prompt_logprobs_cpu`（chunked prefill 跨步累积 prompt logprobs）。`get_token_id(idx)` 统一处理"prompt 段 + 输出段"的拼接寻址。

**`InputBatch`** 的存储分三类：

1. **CPU 大矩阵**：`token_ids_cpu: (max_num_reqs, max_model_len)` 的 int32 numpy 视图（背后是 torch tensor，可按行 gather）——这是整个 decode 状态的主存；`is_token_ids` 布尔矩阵标记混合输入（prompt_embeds 场景）；`num_tokens_no_spec / num_prompt_tokens / num_computed_tokens_cpu` 逐请求标量（pinned，可异步 H2D）。
2. **块表**：`MultiGroupBlockTable`（block_table.py），按组维护每请求 block id 表并派生 slot_mapping；`add_row / clear_row / swap_row / move_row` 四个生命周期操作与 InputBatch 严格同步。
3. **采样参数双缓冲**：`temperature/top_p/top_k/三大 penalty` 各有 GPU tensor + pinned CPU tensor + numpy 视图三份；配合 `greedy_reqs / random_reqs / top_p_reqs...` 等 **set 短路属性**（`all_greedy`、`no_penalties` 等），实现"没人用就不拷"的惰性 H2D。

另有 `batch_update_builder`（收集 added/removed/moved 供 logits processors 增量更新状态）、`spec_token_ids`（每请求本步的 draft token）、LoRA 映射（`request_lora_mapping` + `lora_id_to_request_ids`）、`prev_sampled_token_ids` + `async_copy_ready_event`（async scheduling 修补占位 token）。

## 数据流与方法群（约 28 个方法的骨架）

- **`add_request`**：`_register_add_request` 优先填 `batch_update_builder.pop_removed()` 的空洞（否则 append）；写 token 矩阵两段（prompt + 已有 output）、标量列、`block_table.add_row`；按 sampling_params 填 CPU 参数列并把 req_id 归入各 set；LoRA 映射登记。
- **`remove_request`**：docstring 警告**必须随后调 `condense()`**。置 `_req_ids[i] = None`、清块表行、从所有 set/dict 撤销，返回被删行号。
- **`swap_states(i1, i2)`**：全字段对调。关键优化：token 矩阵**只交换 active 前缀长度**（`num_tokens_no_spec + len(spec_token_ids)`），不搬整行 `max_model_len`——大上下文时这是数量级的节省；numpy 行无法直接 swap，需 tmp 副本。
- **`condense`**：双指针下沉——空洞队列（降序）+ 尾部非空指针，把尾部请求整行搬到最小空洞；每步记录 `moved` 供 logitsprocs 重建 penaltie 累积状态；最后裁剪列表长度。pooling 模型跳过采样态搬运。
- **`refresh_metadata`**：`batch_update_builder.get_and_reset()` 生成 BatchUpdate → 各 LogitsProcessor `update_state` → 若 batch 变化则 `_make_sampling_metadata()` 重建采样元数据（真正执行惰性 H2D：只有 `not no_penalties` 才拷 penalty 列，只有需要才物化 prompt_token_ids padded 矩阵）。
- **`update_req_spec_token_ids` / `update_async_output_token_ids` / `update_async_spec_token_ids`**：spec decode 与 async scheduling 的修补三部曲——把上一步真实采样 token 回填到占位 -1 的位置，处理"KV 加载失败丢弃 token"与"optimistic placeholder 超过实际接受数"两种长度错位。

## 关键设计决策

1. **numpy + pinned torch 双视图**：同一块内存既是 numpy（向量化 CPU 计算）又是 pinned tensor（异步 H2D），`CpuGpuBuffer` 模式的先驱。
2. **set 短路的惰性传输**：`no_top_p` 为真时连 top_p 列都不拷——decode 热路径上每步省下的 H2D 是微秒级收益的来源。
3. **空洞优先的 add + 惰性 condense**：请求进出尽量原地复用，只在必要时整批压缩，避免每步 O(n) 重排。
4. **spec token 占位符协议**：`token_ids_cpu` 中 draft 位置先写 placeholder（-1），采样完成后异步修补——这是 async spec decode 能 overlap 的信用基础。

## 新人提示

- 切入点：先读 `CachedRequestState` 字段表，再读 `add_request` → `remove_request` → `condense` 三连，最后读 `_make_sampling_metadata` 的惰性拷贝分支。
- 易混淆点①：`token_ids_cpu` 某行有效长度是 `num_tokens_no_spec[行] + len(spec_token_ids[行])`，**不是** `num_prompt_tokens + len(req_output_token_ids)`（后者含已固化 output，前者其实等于它——但 spec 占位段只在 spec decode 开启时存在）；读旧代码时注意行内可能残留已完成请求的脏数据，永远按有效长度切片。
- 易混淆点②：`block_ids` 在 CachedRequestState 里是"全量块表"，而 GPU 侧 `block_table` device tensor 是按 `commit_block_table(num_reqs)` 每步增量同步的——数据同源，时机不同。
- 易混淆点③：为什么 swap_states 不交换 `num_logprobs` 这类 dict？因为它们以 req_id 为键，与行号无关；只有数组化存储才需要随行交换。
