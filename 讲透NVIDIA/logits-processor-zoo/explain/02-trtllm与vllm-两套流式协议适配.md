# 精讲 02：trtllm 与 vllm 后端——两套流式协议的适配差异

## 角色定位

`logits_processor_zoo/trtllm/` 与 `vllm/` 各 7 个处理器，与 transformers 版语义一一对应，但两家的调用协议完全不同：TRT-LLM 是"req_id + CUDA 流指针 + beam 级状态"的流式引擎协议，vLLM 是"单序列无批维 + clone 复制"的引擎协议。对比读这三份同名实现，是理解"推理引擎 logits 钩子设计空间"的最佳教材。

## 内部结构

**TRT-LLM 协议**以 `trtllm/generation_length.py` 为样板：`__call__(req_id, logits, token_ids, stream_ptr, ...)`（`:53-54`）——引擎不给 input_ids 增量，**长度自管**：`self.token_count`（`:51` 零初始化，`:70` 每步自增）替代 `len(input_ids)`；CUDA 流以裸指针传入，`torch.cuda.ExternalStream(stream_ptr)`（`:59`）包一层保证 logits 张量操作入队到正确流。批次维度用 `_init_before_gen(beam_width)`（`trigger_phrase.py:58`、`prevent_hallucination.py:57`）惰性建——首次 `__call__`（`:66-67` 调用点）按 beam 数初始化迭代器/计数表，prompt 预处理（multiple_choice 的选项首词预扫）也在此。基类是 `tensorrt_llm.sampling_params.LogitsProcessor`（`generation_length.py:21`）。长度偏置公式 `boost_factor * token_count**p / 10**p`（`:57`）与 transformers 版同构。

**vLLM 协议**以 `vllm/cite_prompt.py` 为样板：`__call__(prompt_tokens_ids, past_token_ids, scores)`（`:46`）——**单序列、无批维**：引擎对每条采样序列独立调用处理器，`len(past_token_ids)` 即已生长度（`generation_length.py:57`）。状态跨调用保留（`_reset` 显式提供，`last_phrase.py:47`），并行采样 n>1 时引擎靠 `clone()`（`last_phrase.py:44`、`trigger_phrase.py:64`、`prevent_hallucination.py:55`、`max_time.py:60`）给每个样本复制独立实例。条件加成逻辑在此协议下最易读：上一 token `past_token_ids[-1]`（`cite_prompt.py:56`），扫 prompt 相邻对取后继加进集合（`:57-59`）。

## 外部连接

trtllm 包被 `lpz_examples/trtllm/utils.py` 的 `TRTLLMTester` 消费：`from tensorrt_llm._torch import LLM`（`:10`，带回退）+ 贪心 `SamplingParams`（`:32`）。vllm 包多一个 `tokenizer.py` 安全模块，且是服务化入口——`vllm serve --logits-processor-pattern "logits_processor_zoo.vllm"`（README:73）按模块名动态加载，kwargs 来自 HTTP 请求体。

## 数据流

TRT-LLM：引擎每步携 req_id 与 logits 调处理器 → 首调 `_init_before_gen` 建 beam 状态 → `ExternalStream` 包流 → 按 token_count 施加策略 → 自增计数。vLLM：每条序列每步调用，`past_token_ids` 单调增长；需要批语义的逻辑（如防幻觉的批计数）在 vllm 版退化为单序列标量状态（对照 `prevent_hallucination.py` 两版的 `_reset` 形状差异）。

## 设计决策

- **长度推断三态**：transformers 靠 input_ids 形状、trtllm 靠自累加计数、vllm 靠 past 长度——三家分别选了"最可信的免费信号"。
- **流正确性显式化**（TRT-LLM）：流式引擎里 logits 所在 CUDA 流与默认流不同步会让加成"晚到"，ExternalStream 是必须而非装饰。
- **clone 而非锁**（vLLM）：并行采样无共享状态=无锁无竞争，代价是要求处理器可深拷贝（持有 tokenizer 引用即可浅共享）。

## 新人提示

迁移自定义处理器到某框架前先回答三问：调用单位是批还是序列？长度从哪来？状态何时重置？——这三问答案就分别是三后端差异的全部。TRT-LLM 侧注意 `_init_before_gen` 只在首调触发，同一处理器实例跨请求复用时 req_id 变化不会自动重置状态（与 transformers 的自动检测相反，需要自己比对）。vLLM 侧记住 V0 引擎前提：`lpz_examples/vllm/utils.py:6` 钉死 `VLLM_USE_V1="0"`，新版 vLLM 移除 V0 后示例需改写（README 勘误 #1）。
