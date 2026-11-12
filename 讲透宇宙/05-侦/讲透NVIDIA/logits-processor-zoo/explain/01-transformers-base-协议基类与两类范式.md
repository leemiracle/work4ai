# 精讲 01：transformers/base.py——协议基类与七处理器的两类范式

## 角色定位

`logits_processor_zoo/transformers/base.py`（51 行）定义了 transformers 后端的处理器协议：批维 `__call__(input_ids, scores)` 之下，用一个自动"新生成检测"状态机替子类管理生命周期，子类只写 `_process`。七个 transformers 处理器全部落在这层协议上，且全部归入两类范式：**静态偏置**类与**状态监控+短语注入**类。

## 内部结构

状态机核心 `_check_new_generation`（`base.py:29-43`）：首次调用记 prompt 并 `_reset`（`:30-33`）；此后每次用 `torch.equal(input_ids[:, :-1], self.prev_token_ids)`（`:37`）判断——把当前输入砍掉最后一列（刚 decode 的 token）后与上次输入比对，相等即同一条生成的推进，不等即新 prompt 触发 `_reset()`（`:39-41`）并更新记录（`:43`）。`_reset`（`:26`）默认空实现，有状态的子类覆写它。这套机制的前提是 transformers 逐 token 传完整 input_ids（批形状 `[B, L]`），也因此成为三框架中唯一能"从输入推断生命周期"的后端。

两类范式各举代表。**静态偏置**：`CiteFromPromptLogitsProcessor`（`cite_prompt.py:23`）——`boost_factor` 直接加成 prompt token 集（可选 EOS，`boost_eos` `:42`），`conditional_boost_factor` 按上一 token 是 prompt 内 token 的后继做条件加成；`MultipleChoiceLogitsProcessor`（`multiple_choice.py:25`）构造期把选项文本转 token（`:45`），`_process` 里 `enforce_tokens` 硬约束到选项集，`boost_first_words` 非零时按选项首词原 logits 比例加权（`:78-79`）。**状态监控+注入**：`PreventHallucinationLogitsProcessor`（`prevent_hallucination.py:24`）——`_reset` 重建批维低置信计数器（`:58-60`），`_process` 逐行判 `softmax().amax() < minp`（`:65`）累计 `minp_count`，超 `tolerate` 后开始逐 token 注入回退短语（`:68`）；`ForceLastPhrase`/`TriggerPhrase`/`MaxTime`/`GenLength` 同属注入/收尾家族，其中 `max_time.py:25` 与 `generation_length.py:24` 混入 `SentenceChecker` 实现句子边界等待。

## 外部连接

向上：`transformers/__init__.py` re-export 全部 7 个处理器，用户经 `LogitsProcessorList` 挂进 `model.generate`（示例骨架 `lpz_examples/transformers/utils.py:42-45`）。向下：全部复用 `utils.py` 四原语——`text_to_token:23`、`get_new_line_tokens:39`、`enforce_tokens:46-52`、`SentenceChecker:55`。测试面 `tests/transformers/` 每处理器一个文件，`test_cite_prompt.py` 是分支覆盖样板。

## 数据流

每 decode 步：HF generate 以 `[B, L]` input_ids + `[B, V]` scores 调 `__call__`（`base.py:48`）→ 状态机判定延续/重置 → `_process(input_ids, scores)` 返回改写后的 scores → 采样器照常 softmax 采样。静态偏置类只看 prompt 前缀（不依赖 input_ids 历史），监控类靠 input_ids 拿到批内每行的生成位置，注入类用 `_reset` 清掉的迭代器在短语 token 序列上推进。

## 设计决策

- **前缀比对而非显式 session id**：transformers 协议没有请求标识，前缀相等是唯一可靠的延续信号；代价是 O(L) 比对每步执行（对 KV-cache 场景可接受）。
- **enforce_tokens 保相对差**（`utils.py:47-51`）：抬 gap 压 min 而非 -inf 掩码，多选题仍能按概率在 a/b/c/d 里挑——"强制"不等于"均匀"。
- **批维状态全量重建**：`_reset` 按 batch_size 零初始化（`prevent_hallucination.py:60`），换 prompt 时旧状态绝不残留。

## 新人提示

写新处理器先决定范式：只需偏置就无状态（继承基类只写 `_process`）；要注入短语就要在 `_reset` 里重建迭代器并接受"换 prompt 即断句"的语义。批内多行不同 prompt 长度时 `input_ids[:, :-1]` 比对仍成立（padding 在左侧，`lpz_examples/transformers/utils.py` 的 padding_side 处理可参考）。排错第一现场：`torch.equal` 对 dtype/形状敏感，混合精度下 input_ids 恒为 long 无碍，但自定义 generate 循环若传错维度会静默把每次都判成"新 prompt"（表现：注入类处理器永远只注入第一个 token）。
