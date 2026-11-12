# logits-processor-zoo 讲透导航（Onboarding）

> 基于图谱 106 节点/197 边/8 层/9 步 tour @ commit 39b41a1f，行号锚经源码核实（2026-11）。配套：`../deepwiki/`、`../explain/` 3 篇、`../README.md`（勘误 7 条）。

## 1. 这个仓库是什么

NVIDIA 的 **logits 处理器动物园**（v0.2.1，`pyproject.toml:3`）：把"超越语法约束的生成控制"——答案长短、多选题限选、引用 prompt、超时收尾、防幻觉回退、触发短语、强制尾句——做成 **7 个处理器 × 3 个推理框架** 的完整矩阵。`logits_processor_zoo/` 下三个后端包（`transformers/`、`trtllm/`、`vllm/`）各 7 个处理器（各自 `__init__.py` 均 re-export 7 项），语义相同、协议各异——"同一语义、三套协议"是全仓的组织原则，也是读代码的主线。核心洞察：logits processor 是所有推理引擎都留的钩子，但每家传参形状/状态管理/生命周期都不同，本仓把差异吸收进适配层，让上层只关心控制策略本身。

## 2. 共享底座：utils.py 四原语

`logits_processor_zoo/utils.py` 是三框架全部处理器复用的原语层，理解它们等于理解半个动物园：

- **`text_to_token`**（`utils.py:23`）：文本转单 token，容忍 BOS/前缀空格引入的多 token，超限抛异常（`:34`）——处理器参数（短语/触发词）到 token id 的标准入口。
- **`get_new_line_tokens`**（`:39`）：收集词表中解码以换行结尾的全部 token id，供"等句子结束再收尾"类逻辑用。
- **`enforce_tokens`**（`:46-52`）：**硬约束而非掩码**——`choice_scores = scores[tokens].clone()`，整体加 `gap = max-min`（`:47-49`）把候选抬到全体之上，其余 `fill_(scores.min())`（`:50`）压底；候选之间的相对差保持不变（多选题仍可按概率选 a/b/c/d）。这与常见的 set -inf 掩码语义不同，是全仓最易被误读的函数。
- **`SentenceChecker`**（`:55`）：句子结束检测 mixin（最后 token 是否句号/换行），`MaxTimeLogitsProcessor` 与 `GenLengthLogitsProcessor` 都混入它（`transformers/max_time.py:25`、`generation_length.py:24`）。

## 3. tokenizer 安全闸：vllm/tokenizer.py

服务化场景下处理器 kwargs 来自 HTTP 请求体（README:63），tokenizer 若按字符串加载就是任意文件/网络加载漏洞。`vllm/tokenizer.py` 是显式设计的服务端安全边界：`get_vllm_tokenizer`（`:27-32`）只接受两类输入——对象直接放行（`:28-29`），字符串必须过 `_validate_tokenizer_name`（`:35`）且 `AutoTokenizer.from_pretrained(..., local_files_only=True)`（`:32`）禁止网络拉取。校验四连：allowlist 未配置直接拒绝（`:42-46`，环境变量 `LOGITS_PROCESSOR_ZOO_VLLM_ALLOWED_TOKENIZERS`，`:24`）；空名/首尾空白拒绝（`:48-49`）；URL（含 `://`）拒绝（`:51-52`）；未列名拒绝（`:54-58`）。默认拒绝、显式信任、只读本地——三层防御与 README:61-76 的 `vllm serve --logits-processor-pattern "logits_processor_zoo.vllm"` 用法闭环（README:69-73 给出完整命令）。

## 4. transformers 协议：基类自动状态机

`transformers/base.py` 是三框架中最简洁的协议范本，全部 51 行：`BaseLogitsProcessor`（`:21`）只暴露 `__call__(input_ids, scores)`（`:48-51`），内部先走 `_check_new_generation`（`:29-43`）——**用 `torch.equal(input_ids[:, :-1], self.prev_token_ids)`（`:37`）判断"本次输入是否上次的延续"**：去掉最后一列（刚生成的 token）与上次输入相等即同一生成的下一步，否则视为换 prompt 调 `_reset()`（`:26`，子类重置自己的计数器/迭代器）并记新 prompt（`:41`）。子类因此**只需实现 `_process`**（`:45`，如 `last_phrase.py:45`、`max_time.py:58`、`generation_length.py:51`），批维状态（如 `prevent_hallucination.py:60` 的 `minp_count` 按 batch_size 零初始化）由 reset 机制兜底。这是"框架状态管理差异"吸收层的第一个样本。

## 5. trtllm 协议：req_id + ExternalStream + beam 级迭代器

TRT-LLM 的流式推理引擎不传 `input_ids`，处理器自己管长度与批次状态：`__call__(req_id, logits, token_ids, stream_ptr, ...)`（`trtllm/generation_length.py:53-54`）——**token_count 自行累加**（`:51` 初始化，`:70` 每次 +1）替代 input_ids 长度推断；`stream_ptr` 经 `torch.cuda.ExternalStream`（`:59`）包成 CUDA 流保证 logits 操作在正确流上。批次/beam 状态用 `_init_before_gen(beam_width)`（`trigger_phrase.py:58`、`prevent_hallucination.py:57`）惰性初始化——首次调用按 beam 数建迭代器/计数表（`:66-67` 的调用点），prompt 相关预处理（如 `multiple_choice` 的选项首词预扫）也挂在这里。基类直接继承 `tensorrt_llm.sampling_params.LogitsProcessor`（`generation_length.py:21`）。长度偏置公式在 `:57`：`boost_val = boost_factor * token_count**p / 10**p`，多项式压短/拉长答案。

## 6. vllm 协议：单序列无批维 + clone()

vLLM 的处理器按**单条序列**调用：`__call__(prompt_tokens_ids, past_token_ids, scores)`（`vllm/cite_prompt.py:46`、`generation_length.py:53`）——没有批维、没有 input_ids 拼接，`len(past_token_ids)` 即已生长度（`:57`）。cite_prompt 的条件加成逻辑清晰可读：prompt 集合 `set(prompt_tokens_ids)`（`:47`）直接加成；`conditional_boost_factor` 非零时取上一 token（`:56`），扫 prompt 相邻对把后继 token 加进加成集（`:57-59`）。并行采样（n>1）时每个样本需要独立状态，所以 4 个有状态处理器实现 `clone()`（`last_phrase.py:44`、`trigger_phrase.py:64`、`prevent_hallucination.py:55`、`max_time.py:60`）——引擎为每条采样序列复制一份。

## 7. 示例、测试与服务化

- **16 个 notebook**（`lpz_examples/`：transformers 7 + vllm 7 处理器示例 + `vllm_serve.ipynb` 170 行 + `performance_profiling.ipynb` **1894 行**——后者是 logits 处理器开销的基准测量方法论，输出延迟/吞吐对比）。三份示例运行器是公共骨架：transformers `LLMRunner`（`lpz_examples/transformers/utils.py:6`，默认 Qwen2.5-1.5B-Instruct + chat 模板 `:28`）、trtllm `TRTLLMTester`（`lpz_examples/trtllm/utils.py:6-14`，`tensorrt_llm._torch.LLM` 优先带回退）、vllm `vLLMRunner`（`lpz_examples/vllm/utils.py:9-10`，注意 `:6` 的 `VLLM_USE_V1="0"` 钉死 V0 引擎）。
- **测试哲学=轻依赖+真生成**：`tests/conftest.py:53-55` 的 session fixture 用 **0B 单测专用模型** `MaxJeblick/llama2-0b-unit-test`——CI 无 GPU 也能跑真实前向做断言；`LLMRunner` 类本体（`:23-50`）默认 gemma-1.1-2b-it 供本地全量跑。`test_utils.py` 覆盖三原语，`tests/vllm/test_tokenizer.py` 覆盖安全层全部拒绝分支。
- **新人路线**：README 处理器清单（`:81-111` 七条）→ transformers 版任一处理器（协议最简）→ `explain/01`（base 状态机）→ 换读 trtllm/vllm 同名处理器对比协议（`explain/02`）→ 安全层与 serve 化（`explain/03`）→ `performance_profiling.ipynb` 看开销。
