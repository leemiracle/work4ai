# vllm/v1/worker/gpu_input_batch.py — InputBatch：persistent batch 的运行时状态容器

> 源码：`vllm/v1/worker/gpu_input_batch.py`（1144 行）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`InputBatch` 是 **persistent batch 的扁平化运行时状态**：decode 阶段活跃请求的全量快照——token 序列、块表引用、采样参数、LoRA 归属，以及它们的增删换压缩。vLLM v1 没有传统 SequenceGroup 对象图，本文件用"**行号即请求**"的扁平结构 + CPU 大矩阵，让 ModelRunner 每步用纯 numpy 向量操作组装输入（vllm/v1/worker/gpu_model_runner.py:1979 的 index_select gather 就是从这里的 token 大表取数）。设计前提写在 vllm/v1/worker/gpu_model_runner.py:1232 注释里：**persistent batch 优化假设连续 step 的请求集合高度重叠**——数据写入后尽量不动，只做增量修补，请求离开才触发 condense 压缩。它是 ModelRunner 的私有财产：`_update_states` 增删行，`_prepare_inputs` 从中 gather 输入。

## ② 内部结构

**`CachedRequestState`**（:34，dataclass）：单请求快照——req_id/prompt_token_ids/mm_features/sampling_params/generator/block_ids（按 kv_cache_group 分组）/num_computed_tokens/output_token_ids，外加 mrope 位置、prompt_embeds、LoRA、pooling 态、`in_progress_prompt_logprobs_cpu`（chunked prefill 跨步累积）、`prompt_is_token_ids`（混合输入逐位掩码）、`prev_num_draft_len`（async spec decode 专用 :59）。`get_token_id`（:77）统一"prompt 段+输出段"拼接寻址，越界返 -1。

**`InputBatch`**（:90）存储四类：①**CPU 矩阵**：`token_ids_cpu: (max_num_reqs, max_model_len)` int32 numpy 视图（:131，**刻意不 pin**，注释 :129 说明它不直接 H2D）；`is_token_ids` 布尔矩阵（:138，prompt_embeds 场景标真 token 位）；`req_prompt_embeds` 按请求 dict（:148，避免大 max_model_len 一次性预分配 OOM）；pinned 标量列 num_tokens_no_spec/num_prompt_tokens/num_computed_tokens_cpu（:149-169）；`replayssm_decode_base`（:174，Mamba2 ReplaySSM decode 环起点）。②**块表**：`MultiGroupBlockTable`（:183）按组维护块 id 并派生 slot_mapping。③**采样参数三重缓冲**：temperature/top_p/top_k/三大 penalty 各有 GPU+pinned CPU+numpy 三份（:195-247），配合 set 短路属性（all_greedy:1108、no_penalties:1124、no_thinking_budget:1132、no_allowed_token_ids:1143）。④**杂项**：num_accepted_tokens_cpu（:250，spec 默认 1）、LoRA 三件套（:256-258）、generators（:263）、num_logprobs+`logprob_token_ids`（:265-269，后者是"只算这几个 token"的省算路径）、batch_update_builder（:274）、惰性分配的 allowed_token_ids_mask（:443）、bad_words（:284）、`thinking_budget_state_holder`（:109，reasoning 模型 thinking budget 跟踪）、spec_token_ids（:296）、prev_sampled_token_ids+async_copy_ready_event（:306-312）。

## ③ 外部连接

- **依赖**：MultiGroupBlockTable/SlotMappingMode（:31）、BatchUpdateBuilder/LogitsProcessors（:21）、SamplingMetadata（:26）、thinking_budget_state 构造器（:27）、PoolingMetadata（:20）。
- **被依赖**：gpu_model_runner 是唯一写者；LoRA mixin 经 `make_lora_inputs`（:996）取映射做 prompt/token 级展开；spec decode proposer 家族直接读 num_tokens_no_spec+token_ids_cpu 起草——GPU n-gram 有专门增量同步（gpu_model_runner.py:1504 只搬新行）。

## ④ 数据流

- **`add_request`**（:345）：`_register_add_request`（:320）优先填 batch_update_builder.pop_removed() 空洞否则 append；写 token 矩阵两段（prompt :371+已有 output :382）与 is_token_ids 掩码；填标量列、block_table.add_row（:393）；按 sampling_params 填参数列并登记 set——greedy 的 temperature 写 0.0 防 apply_temperature 除零（:397）；ReplaySSM 时 replayssm_decode_base=num_tokens（:390，重入场以"prompt+已恢复 output"重新锚定环起点）；LoRA 登记（:482-492）。
- **`remove_request`**（:523）：docstring 警告**必须随后调 condense()**。置 _req_ids[i]=None、清块表行/embeds、从所有 set/dict 撤销。
- **`swap_states`**（:580）：全字段对调。关键优化：token 矩阵**只交换 active 前缀长度**（`_get_active_token_count`:693 = num_tokens_no_spec+len(spec_token_ids)，:585-587），不搬整行 max_model_len；numpy 行不能直接交换序，需 tmp 副本（:625）。
- **`condense`**（:698）：双指针下沉——removed 空洞队列（降序假设 :722）+尾部非空指针，整行搬最小空洞并记 moved 供 logitsprocs 重建 penalties 累积态；pooling 模式跳过采样态搬运（:783）；最后裁列表（:828-830）。
- **`refresh_metadata`**（:832）：get_and_reset 生成 BatchUpdate → thinking_budget 同步（:845）→ 各 LogitsProcessor update_state → `_make_sampling_metadata`（:851）执行惰性 H2D：not no_penalties 才拷 penalty 列（:864-878），需要才物化 prompt_token_ids padded 矩阵（:888，pad 值=vocab_size :993），output_token_ids 仅在 penalties/bad_words/自定义 logitsprocs/thinking-budget 需要时给（:903-913）。
- **spec/async 修补三部曲**：update_req_spec_token_ids（:496，占位写入并记 prev_num_draft_len）；update_async_output_token_ids（:1038，等事件后用真实采样 token 回填 -1 占位，处理"KV 加载失败丢弃"与"optimistic 占位超过实际接受数"两种错位 :1067-1082）；update_async_spec_token_ids（:1084，rejection sampler 用前修真实 draft）。

## ⑤ 设计决策

1. **numpy+pinned 双视图但不一刀切**：会异步 H2D 的标量列全 pinned，token_ids_cpu 明确不 pin（省锁页内存），传输走 runner 侧 gather+pin 通道。
2. **set 短路的惰性传输**：no_top_p 为真连 top_p 列都不拷——decode 热路径每步省下的 H2D 是微秒级收益来源；property 族是采样器的"谁在用谁付钱"协议。
3. **空洞优先 add + 惰性 condense**：请求进出原地复用，避免每步 O(n) 重排；代价是 remove 后必须 condense，协议靠 docstring 而非类型系统约束。
4. **spec 占位符协议**：token_ids_cpu 的 draft 位先写占位（async 下随后被 runner 在 GPU 侧 scatter 覆盖），采样完成后异步修补——async spec decode overlap 的信用基础。
5. **embedding 按请求 dict 存储**（:145-148）：不再预分配巨型 embeds 矩阵，大 max_model_len 更友好，代价是 gather 时逐请求拷贝（gpu_model_runner.py:1997 循环）。

## ⑥ 新人提示

- 切入点：CachedRequestState 字段表 → add/remove/condense 三连 → _make_sampling_metadata 惰性拷贝分支。
- 易混淆点①：行有效长度 = num_tokens_no_spec[行]+len(spec_token_ids[行])（_get_active_token_count），行尾可能残留脏数据，**永远按有效长度切片**。
- 易混淆点②：block_ids 是 CPU 侧全量块表，GPU 侧 device tensor 按 commit_block_table(num_reqs) 每步增量同步——同源不同时机。
- 易混淆点③：num_logprobs/logprob_token_ids 等 dict 以 req_id 为键，swap_states 不交换它们；只有数组化存储才随行交换。
- 加新采样参数三连位置：__init__ 三重缓冲 → add_request 写入+set 登记 → swap_states/condense 交换/搬运，漏一处就在 condense 后静默串行。
