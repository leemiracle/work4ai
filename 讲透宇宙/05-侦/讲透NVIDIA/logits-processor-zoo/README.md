# 讲透 NVIDIA/logits-processor-zoo

NVIDIA logits 处理器动物园（v0.2.1）：7 个处理器 × 3 框架（transformers/TensorRT-LLM/vLLM）完整矩阵，"同一语义、三套协议"；含 vLLM 服务化 tokenizer 安全闸与 16 个示例 notebook。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | ✅ TRUE_100 | `deepwiki/` |
| understand 图谱 | ✅ 106n/197e/8 层/9 步 tour，0 issues，fingerprints 71 文件 @ 39b41a1f | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 7 节 / 57 行号锚（任务书 7 节 25 锚超额） | `onboarding/ONBOARDING.md` |
| explain | ✅ 3 篇（transformers 协议 / trtllm×vllm 协议对比 / tokenizer 安全闸） | `explain/01-…` `02-…` `03-…` |
| NOTES-DIGEST | ✅ 6 条 | 仓内 `.understand-anything/NOTES-DIGEST.md` |

## 源码级勘误清单（7 条，行号实证 @ 39b41a1f）

1. **vLLM 示例钉死 V0 引擎**：`lpz_examples/vllm/utils.py:6` `os.environ["VLLM_USE_V1"] = "0"`——全部 vLLM notebook 基于 V0 引擎 API；而 `pyproject.toml:14` 只约束 `vllm>=0.5.0.post1` 无上界，新版 vLLM（V0 已移除）下示例直接失效。任务书口径"15 ipynb"亦不准：实际 **16 个**（transformers 7 + vllm 7 + vllm_serve 170 行 + performance_profiling 1894 行）。
2. **测试函数命名复制粘贴错误**：`tests/transformers/test_multiple_choice.py:21` 函数名是 `test_cite_from_prompt_logits_processor`，测的却是 MultipleChoiceLogitsProcessor——pytest 照跑，但 `-k cite_from_prompt` 会误选中多选题测试、且 `tests/transformers/test_cite_prompt.py` 的同名真测试与之并存，语义混淆。
3. **enforce_tokens 是硬偏置非掩码**：`logits_processor_zoo/utils.py:46-52` 实现为候选整体抬 `max-min` gap、其余压到 `scores.min()`、候选间相对差保持——不是常见的 `-inf` 掩码；README:90"forces LLMs to use one of the choices"容易被读成均匀掩码，实际多选题输出仍按原始概率分布在选项间挑选。
4. **conftest 双模型口径并存**：`tests/conftest.py:55` session fixture 用 0B 单测专用模型 `MaxJeblick/llama2-0b-unit-test`（CI 无 GPU 跑真实前向），而同类 `LLMRunner` 的默认构造是 `google/gemma-1.1-2b-it`（`:24`）——gemma 系是 HF gated 模型，直接实例化 `LLMRunner()` 会先撞许可墙再谈下载。
5. **TRT-LLM 示例依赖私有路径**：`lpz_examples/trtllm/utils.py:10` `from tensorrt_llm._torch import LLM`（带 try-except 回退）——`_torch` 是 TRT-LLM PyTorch 后端的内部模块，版本间迁移频繁，示例的可用性强绑定特定 TRT-LLM 版本。
6. **trtllm 处理器状态跨请求不复位**：`_init_before_gen`（`trtllm/prevent_hallucination.py:57`、`trigger_phrase.py:58`）只在首调按 beam_width 惰性初始化，req_id 变化不触发重置——与 transformers 后端的自动新 prompt 检测（`base.py:37`）行为不同，长寿命服务里跨请求复用实例会带脏状态。
7. **图谱测试节点挂错文件**：图谱存在 `function:tests/transformers/test_multiple_choice.py:test_cite_from_prompt_logits_processor` 节点——它如实反映了勘误 #2 的命名错误（节点摘要按函数名描述成 cite_prompt 测试），读图谱时该节点的语义应按文件名 test_multiple_choice.py 纠正。

## 快速上手

pip 装（`pyproject.toml`：transformers 必装，trtllm/vllm extras 可选）→ 跑 `lpz_examples/transformers/cite_prompt_logits_processor.ipynb`（Qwen2.5-1.5B）→ 对比 trtllm/vllm 同名示例看协议差异。服务化：先设 `LOGITS_PROCESSOR_ZOO_VLLM_ALLOWED_TOKENIZERS` 再 `vllm serve … --logits-processor-pattern "logits_processor_zoo.vllm"`（README:69-73）。测试 `pytest tests/`——conftest 的 0B 模型让集成测试无 GPU 也能跑真生成。

## 深讲入口

- 三框架协议差异总表：`onboarding/ONBOARDING.md` 第 4-6 节
- transformers 基类状态机与两类范式：`explain/01`
- trtllm/vllm 适配对照（长度推断三态/ExternalStream/clone）：`explain/02`
- tokenizer 安全闸与服务化链路：`explain/03`
