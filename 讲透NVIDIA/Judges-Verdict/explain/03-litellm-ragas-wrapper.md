# 03 · litellm_ragas_wrapper.py —— 绕开 LangChain 的 LiteLLM 直连适配器

## 角色定位

`llm_judge_benchmark/utils/litellm_ragas_wrapper.py`（200 行）是框架"26 家供应商"能力的关键：一个**鸭子类型**的 RAGAS LLM 适配器，用 litellm completion API 直接实现 RAGAS 期望的最小方法集，全程不 import langchain——docstring 开宗明义 "bypasses LangChain entirely"（litellm_ragas_wrapper.py:6）。

## 内部结构

**LiteLLMResult 数据类**（litellm_ragas_wrapper.py:20-25）只是 generations + llm_output 的壳，对应 LangChain LLMResult 的最小替代。

**RagasLiteLLMWrapper**（litellm_ragas_wrapper.py:28-173）五个方法：

- `__init__`（litellm_ragas_wrapper.py:34-67）：存参数外做两件全局事——litellm.drop_params=True（丢弃供应商不认识的参数）与 set_verbose=False；若传入 api_key 则**反写环境变量**（litellm_ragas_wrapper.py:61-67）：模型名含 nvidia→NVIDIA_NIM_API_KEY、含 gpt/o1/o3→OPENAI_API_KEY、含 claude→ANTHROPIC_API_KEY——与 judge_config_manager.py:69-104 的前缀表互为镜像。
- `generate`（litellm_ragas_wrapper.py:69-149）：同步主路径。先做 prompt 对象兼容（litellm_ragas_wrapper.py:74-79）；组 completion_kwargs（:84-91）；**o1/o3 模型跳过 temperature**（litellm_ragas_wrapper.py:94-95）；api_base 有值直用、否则 nvidia 模型读环境变量兜底（:98-104）；api_key=="EMPTY" 是本地服务器免鉴权特例（litellm_ragas_wrapper.py:107-112）。调用 completion（:117）后，**在函数体内定义两个内联类**适配响应：Generation（litellm_ragas_wrapper.py:125-136，__getitem__(0)→self）与 Result（:141-148）——对 LangChain 索引协议的手工仿真。
- `set_run_config`（litellm_ragas_wrapper.py:151-159）：RAGAS 初始化 metric 的回调钩子，存下 run_config 后 pass。
- `agenerate_text`（litellm_ragas_wrapper.py:161-164）：**异步路径直接调同步 generate**——并发全靠 RAGAS 线程池；`agenerate_prompt`（litellm_ragas_wrapper.py:166-173）逐 prompt 串行 await 后聚合。

**工厂 create_ragas_litellm_wrapper**（litellm_ragas_wrapper.py:176-199）：纯参数透传，评分引擎 llm_judge_scoring.py:147 的调用入口。

## 外部连接

唯一消费方是评分引擎的 LiteLLM 分支（llm_judge_scoring.py:145-158）；liteLLM 模型在 judge_config_manager.py:300-303 被显式拒绝，本文件就是 LiteLLM 路线的全部 LLM 面。向下依赖 litellm.completion（litellm_ragas_wrapper.py:17）。

## 数据流

请求向：RAGAS metric 调 generate(prompt_obj, n) → 取 prompt.text（litellm_ragas_wrapper.py:74-79）→ 单条 user message → kwargs 组装 → litellm.completion（litellm_ragas_wrapper.py:117）→ 任意供应商的 OpenAI 兼容端点。响应向：choices[].message.content（litellm_ragas_wrapper.py:121-122）→ 内联 Generation/Result → RAGAS 按索引协议读 generations[0][0].text → AnswerAccuracy 判分。

## 设计决策

- **环境变量反写是双刃剑**（litellm_ragas_wrapper.py:61-67）：好处是 litellm 内部路由自动拿 key；坏处是**进程级污染**——并行跑多供应商裁判时后构造的 wrapper 覆盖先者的环境变量。
- **鸭子类型而非继承**：只实现被实际调用的方法面，重试直接用 litellm 的 num_retries（litellm_ragas_wrapper.py:90）。

## 新人提示

新接供应商时按 litellm_ragas_wrapper.py:62-67 与 :100-104 的前缀链核对模型命名——名字含 "nvidia"/"gpt"/"claude" 触发特殊路由，不含已知前缀时 api_key 只能显式传。给新 RAGAS 版本适配时，先看它调 generate 还是 agenerate_text、读结果用 [0][0] 索引还是 .generations——这两个访问模式就是内联类的存在理由。

——锚核对于 2026-11-08，commit dfbcd5ee。
