# 05 model 模型层：ChatModelBase、流式解析与截断兜底

## 1. 角色定位

model 子系统是六家供应商（openai/dashscope/anthropic/gemini/deepseek/ollama，外加 trinity 训练后端）的统一出口。`src/agentscope/model/_model_base.py` 的 `ChatModelBase` 是刻意做小的协议层：只规定"可像函数一样调用、返回 `ChatResponse` 或其异步流"。它不碰 HTTP 细节、不做重试、不管方言——那是各家 `_xxx_model.py` 与 formatter 的分工。本文以最重的 `DashScopeChatModel` 为代表拆"构造注入/调用面/流式累积"三件事，并把题目里的"截断兜底"接回它的真实位置。

## 2. 内部结构

**ChatModelBase**：全部家当是两个类属性（model_name/stream）与三个方法。`__init__` 只收这两个参数（`src/agentscope/model/_model_base.py:22`）；唯一抽象方法是 `__call__`（`_model_base.py:39`），签名宽到 `*args/**kwargs`，返回类型双态：非流式给 `ChatResponse`，流式给 `AsyncGenerator[ChatResponse]`——这个双态约定是整个 agent 层判断 `if self.model.stream` 的依据。`_validate_tool_choice`（`_model_base.py:46`）是给子类共享的校验：三种模式（auto/none/required）之外，允许传具体函数名，但必须在 tools 清单里，否则报错并附全部可选项。

**ChatResponse**（`_model_response.py:20`）：dataclass，content 是四种块（text/tool_use/thinking/audio）的序列，usage 与 metadata 可空。注意流式场景下每个 chunk 的 content 都是**累积快照**而非增量——这是 agent 侧能直接覆盖 `msg.content` 的前提。

**DashScopeChatModel**（`src/agentscope/model/_dashscope_model.py:50`）构造期的机关：`enable_thinking=True` 而 `stream=False` 时强制改写为流式（`_dashscope_model.py:122`），因为 DashScope 思考模式只在流式下开放；`DASHSCOPE_API_HEADERS` 环境变量可注入自定义头。`__call__`（`_dashscope_model.py:162`）固定带 `"incremental_output": self.stream`（`_dashscope_model.py:220`）——增量输出与流式绑定，解析器才能把 chunk 当增量累积。工具三态处理：`required` 在 DashScope 不支持，降级为 `auto` 并发 DeprecationWarning（`_dashscope_model.py:230`）；`structured_model` 传入时 tools/tool_choice 全被覆盖成"只调这一个格式化工具"（`_dashscope_model.py:247`），结构化输出在 model 层就是受限工具调用。多模态分流：model_name 以 qvq 开头或含 `-vl` 时走 `AioMultiModalConversation`，否则 `AioGeneration`（`_dashscope_model.py:268`）。

**流式解析器** `_parse_dashscope_stream_response`（`_dashscope_model.py:300`）是本文件最长的函数，做三路累积：reasoning_content 进 thinking 前缀、content 进文本、tool_calls 按 index 增量拼接 id/name/arguments。`stream_tool_parsing=True` 时对未完成的 arguments JSON 做"修复式解析"（`_dashscope_model.py:415`），并保留上个 chunk 的解析结果防止回退（新解析更短就沿用旧的）；False 则中间 chunk 的 input 留空 dict，最后一个 chunk 统一解析补齐（`_dashscope_model.py:464`）。usage 只在带 usage 的 chunk 上更新。

**截断兜底的真实位置**：不在 model 层，而在 formatter 家族的 `TruncatedFormatterBase`（`src/agentscope/formatter/_truncated_formatter_base.py:48`）——"排版→计数→超限砍最早配对消息→重排"的 while 循环（`_truncated_formatter_base.py:71`）。model 只负责报错，formatter 负责不让请求超限发出。另一重兜底在 agent 层：`CompressionConfig` 的记忆压缩（详见 01 篇）。

## 3. 外部连接

上游消费方唯一：ReActAgent 的 `_reasoning`/`_summarizing`/查询重写/压缩四处 `await self.model(prompt, tools=..., tool_choice=...)`（`src/agentscope/agent/_react_agent.py:568`）。输入即 formatter 的输出（messages 列表），输出喂回 agent 组装 Msg。`ChatUsage` 在 `_model_usage.py` 单独成文件；`structured_model` 参数把 pydantic 转 JSON schema 的工具函数（`_create_tool_from_base_model`）复用自 tool 子系统。

## 4. 数据流

流式一次调用：agent 传来 formatter 排好的 messages+tools → `__call__` 组 kwargs（含 incremental_output）→ dashscope SDK 返回异步生成器 → `_parse_dashscope_stream_response` 逐 chunk：累积三路内容、每轮重建 content_blocks（thinking→text→tool_use 顺序）→ 有内容就 yield 一个累积快照 ChatResponse → agent 侧 `msg.content = chunk.content` 覆盖式更新并 `print(msg, False)` → 末 chunk 后若关了流式工具解析，补一次完整 JSON 修复并产出最终块。非流式则走 `_parse_dashscope_generation_response` 一次成型。

## 5. 设计决策

把 `__call__` 而非 `generate` 定为协议，让 model 实例天然可 await、可 Mock 成普通协程函数。双态返回（对象/异步生成器）是省内存与省接口数的折中，代价是消费方必须先看 stream 标志再迭代。tool_calls 按 index 累积而非按 id，是因为流式分片里 id 也可能被拆开。structured_model 复用 tools 通道（而非 response_format）保证六家行为一致，代价是"结构化输出时不能同时用其他工具"这一限制。截断放在 formatter 而非 model：只有排版后才知道真实 token 数，且砍消息必须懂 Msg 语义。

## 6. 新人提示

- 逻辑归属勘误：`ChatModelBase` 只有小半个协议（`_model_base.py:39`），"客户端注入或 api_key 惰性建连"等构造差异在各子类 `__init__` 里，找行为要去具体 `_xxx_model.py`。
- `required` 传给 DashScope 会被静默降级 `auto`（仅 DeprecationWarning，`_dashscope_model.py:230`）：依赖"必须调工具"的流程在 DashScope 上其实没有强制力。
- 流式 chunk 的 content 是累积快照：想存增量请自行 diff；反过来把快照当增量拼接会导致指数膨胀。
- thinking 块出现在每个累积快照开头：下游解析时别重复输出。
- `stream_tool_parsing` 的"防回退"逻辑（`_dashscope_model.py:415`）意味着中间 chunk 的 input 可能是猜出来的半成品 JSON：只有最后一个 chunk 的 input 可信。
- 与 ONBOARDING 4.2 节互补：那边讲 model-formatter 成对更换，本文给出双态返回、增量输出绑定与工具三态降级三个协议级细节。

自报：05-model.md｜约 3710 字符（不计空格）｜锚 17 个
