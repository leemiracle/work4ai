# browser_use/llm/openai/chat.py + base.py 精讲——LLM 统一入口

## 一、角色定位

先做路径勘误：常被引用的 `browser_use/llm/chat.py` **不存在**。LLM 统一入口实际是一对文件——`llm/base.py`（75 行）定义 `BaseChatModel` Protocol 与共享工具；`llm/openai/chat.py`（324 行）的 `ChatOpenAI` 是参考实现与事实基类。`llm/` 目录是 20 余个 provider（openai/anthropic/google/groq/deepseek/mistral/ollama/litellm/azure/cerebras/openrouter/aws/vercel/oci_raw/browser_use 网关…）的平行实现，每目录一对 `chat.py + serializer.py`，全部结构性满足 `BaseChatModel` Protocol（如 anthropic/chat.py L38、deepseek/chat.py L31——是 Protocol 实现而非继承 ChatOpenAI，Azure 是少数例外）。README 直言设计哲学：从 LangChain 迁到 `openai.types.chat.chat_completion_message_param` 格式（base.py 文件头 L1-5），**OpenAI 消息格式是全仓通用语**。Agent 侧只认 `BaseChatModel`（agent/service.py L27、L140）——依赖倒置：高层不 import 任何具体 provider。

## 二、内部结构

**base.py 两个部件**：

1. `is_reasoning_model(model, reasoning_models)`（L18-29）：子串匹配判断推理模型，空表直接 False。
2. `BaseChatModel`（L32-74）：`@runtime_checkable` Protocol。核心契约一个方法：`async ainvoke(messages, output_format=None, **kwargs) -> ChatInvokeCompletion[T]`（L57-59，两个 @overload 区分 str 与 Pydantic 泛型返回），加 `model` 属性与 `provider`/`name`/`model_name`。最巧一手是 `__get_pydantic_core_schema__`（L61-74）：让 Protocol 能直接当 Pydantic 字段类型用——AgentSettings 才能类型安全持有任意 LLM 实例。

**ChatOpenAI（dataclass，L24-77）**：字段三组。模型参数默认值有讲究——`temperature=0.2`、`frequency_penalty=0.3`（L38 注释：防 4.1-mini 无限生成 `\t`）、`max_completion_tokens=4096`（L64）、`reasoning_effort='low'`（L39）；三个兼容开关：`add_schema_to_system_prompt`（L43，schema 塞系统提示而非 response_format）、`dont_force_structured_output`（L44，完全不强制）、`remove_min_items_from_schema`/`remove_defaults_from_schema`（L45-50，给挑刺 provider 删 schema 键）。客户端参数透传 AsyncOpenAI，`max_retries=5`（L59 注释：自动化可靠性）。`reasoning_models` 默认表列 o 系与 gpt-5 全家（L65-77）。

**ainvoke 主流程（L152-323）**四步：

1. **序列化**：`OpenAIMessageSerializer.serialize_messages`（L166）把仓内 BaseMessage 转 OpenAI 格式——每 provider 一个 serializer 是本层唯一真差异点。
2. **参数装配**（L169-192）：非 None 才进 model_params；推理模型特判（L189-192）——匹配 `reasoning_models` 时加 `reasoning_effort` 并**删掉 temperature 与 frequency_penalty**（o 系拒绝采样参数，不删会 400）
3. **两分支**：无 output_format 纯文本（L194-222）；有则构造 `response_format=ResponseFormatJSONSchema`，schema 由 `SchemaOptimizer.create_optimized_json_schema` 从 Pydantic 模型生成（L225-233，strict: True），再按 remove 开关瘦身；`add_schema_to_system_prompt` 时把 schema 追加进系统消息（L236-243，兼容两种 content 形态）。
4. **响应解析与异常翻译**（见下）。

## 三、外部连接

- **被 Agent 消费**：`llm.ainvoke(input_messages, output_format=self.AgentOutput, session_id=...)`（agent/service.py L1950-1953）——结构化输出在 LLM 层完成 Pydantic 校验，拿到即合法 AgentOutput。
- **消息体系**：`llm/messages.py` 的 BaseMessage/UserMessage/SystemMessage（带 cache 标志）由 prompts.py 生产
- **schema 体系**：`llm/schema.py` 的 SchemaOptimizer 把 Pydantic schema 优化成 provider 可用的 JSON Schema
- **异常体系**：`llm/exceptions.py` 三异常 ModelRateLimitError/ModelProviderError/ModelOutputTruncatedError——Agent 的 fallback 切换（agent/service.py L1973-1979、可重试码 {401,402,429,500,502,503,504}）靠这三个类型驱动
- **返回值体系**：`llm/views.py` 的 `ChatInvokeCompletion[T]`（L41，completion/usage/stop_reason/thinking）与 `ChatInvokeUsage`（L8，cached/cache_creation 按可空统一）。

## 四、数据流

一次 Agent 步内调用：消息列表 → serializer 转 OpenAI 格式（cache 标记进系统消息）→ chat.completions.create（带 json_schema）→ 三道防线：

1. **空 choices 防线**（L202-215、L260-273）：choices 空抛 ModelProviderError(status_code=502)，错误消息教育代理用户"确保 base_url 代理实现 /v1/chat/completions 返回非空 choices"——把常见配置错误变成可读诊断。
2. **截断防线**（L277-290）：`finish_reason == 'length'` 抛 ModelOutputTruncatedError，注释点明痛点（L275-276）：**推理模型可能把 token 预算全烧在隐藏思考上，留下 content=None + finish_reason='length'**——检查必须在 content-None 之前，否则真因被吞。
3. **解析防线**（L292-301）：content 为 None 抛 ProviderError；`model_validate_json(content)`（L301）做最终校验。

底层 SDK 异常出口统一翻译（L309-323）：RateLimitError→ModelRateLimitError（触发 Agent 的 fallback）、APIConnectionError/APIStatusError/其他→ModelProviderError（保留 status_code）。**所有 provider 出口都是这套异常方言**，Agent 才能统一重试/降级。

usage 统计有跨 provider 语义注释（L125-127）：OpenAI 的 reasoning_tokens 是 completion_tokens 子集；对比 Google 单列 thinking_tokens、Anthropic 的 total 要自己加回缓存 token（anthropic/chat.py L215）——字段统一但语义校准散在各实现。

## 五、设计决策与取舍

1. **Protocol 而非抽象基类**：`runtime_checkable` + `__get_pydantic_core_schema__`，新 provider 零负担即插即用；代价是没有强制力，漏实现 ainvoke 运行时才炸。
2. **OpenAI 格式做通用语**：迁离 LangChain 换来自主性（消息结构、缓存标记、usage 语义自定），代价是每接一个非 OpenAI 方言 provider 都要写 serializer——每目录 serializer.py 的存在原因。
3. **结构化输出三档可调**：强 json_schema（默认）→ schema 进系统提示（给半兼容网关）→ 完全不强制（靠模型自觉+解析兜底），兼容阶梯覆盖长尾代理。
4. **每次调用新建 client**：`get_client()`（L109-117）在每次 ainvoke 构造——配置变更即时生效且无共享状态，连接复用交 SDK 池。
5. **默认参数偏保守自动化**：temperature 0.2、retries 5、max_completion_tokens 4096、reasoning_effort low——全朝"长跑任务稳定省钱"调。

## 六、新人提示（坑/勘误）

- **找 `llm/chat.py` 会扑空**：入口是 base.py（协议）+ openai/chat.py（参考实现）。加新 provider：复制任一子目录的 chat.py+serializer.py 改两文件。
- **推理模型参数自动剥离**：模型名撞上 reasoning_models 表时 temperature/frequency_penalty 被静默删（L191-192）——"温度怎么没生效"的答案在这。
- **`max_completion_tokens=4096` 默认可能不够**：推理模型隐藏思考占预算，撞上限收到 ModelOutputTruncatedError（L283），长任务显式调大。
- **别在 provider 层重试业务错误**：这层只翻译异常，重试/降级全在 Agent（`_try_switch_to_fallback_llm`）；在此层加重试会与 SDK 的 max_retries=5 叠乘放大。
- **`chat.py` 在十余个目录重复**：引用行号必须带目录前缀，否则锚点歧义。
- **usage 语义跨 provider 不对齐**：`prompt_tokens` 是否含缓存、total 是否手动加缓存（Anthropic）口径不同——views.py L14 与各实现注释是唯一权威。
