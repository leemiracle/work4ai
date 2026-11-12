# 04 formatter 多供应商格式化：FormatterBase 与 OpenAI/DashScope 方言

## 1. 角色定位

formatter 子系统是 AgentScope 的"方言隔离层"：统一内部消息格式 `Msg`（七种内容块）与各家 chat API 请求体之间的全部翻译都压在这里，model 层因此可以只管收发。目录形态勘误：不存在 `_pipeline_base` 式的单根——七族 formatter（openai/dashscope/anthropic/gemini/deepseek/ollama/a2a）每族两个类（Chat 单智能体 + MultiAgent 多智能体），真正的公共基座是两层：`FormatterBase`（`src/agentscope/formatter/_formatter_base.py:11`）定协议与工具，`TruncatedFormatterBase`（`src/agentscope/formatter/_truncated_formatter_base.py:19`）加截断兜底与消息分组模板。本文以默认方言 OpenAI 与最重方言 DashScope 为代表。

## 2. 内部结构

**FormatterBase**：抽象面只有一个 `format`，真正被七族复用的是两个 staticmethod：`assert_list_of_msgs` 入参校验（`_formatter_base.py:20`）；`convert_tool_result_to_string`（`_formatter_base.py:37`）解决"API 工具结果不支持多模态"的通病——文本块直取、图片/音频/视频块降级为"文件在 xxx 路径"的说明文字，base64 数据还会先落盘成文件（`_formatter_base.py:100`），返回 (文本, [(路径, 块)]) 二元组供上层决定是否"提升"回消息流。多条文本时自动拼成 bullet 列表。

**TruncatedFormatterBase——模板方法+重试环**：`format`（`_truncated_formatter_base.py:48`）是核心机关：deepcopy 入参后进入 while 循环，`_format` 排版 → `_count` 计 token → 不超限即返回，超限则 `_truncate` 砍头再来（`_truncated_formatter_base.py:71`）。`_truncate` 的砍法讲配对纪律：从尾往前找"tool_use/tool_result 的 id 队列清空"的边界，保证砍掉的调用与结果成对（`_truncated_formatter_base.py:193`）；系统提示单独超限直接 raise；孤儿调用（有 use 无 result）也 raise。`_format` 模板方法把消息流切成 system + 交替的 `tool_sequence`/`agent_message` 组（内部是个逐消息分组的状态机），分派给子类两个钩子 `_format_tool_sequence`/`_format_agent_message`——这是多智能体场景兼容 tools API 的通用解法。

**OpenAIChatFormatter**（`src/agentscope/formatter/_openai_formatter.py:156`）：单智能体场景直接逐消息翻译：tool_use 块聚成 `tool_calls` 数组、input 序列化成 JSON 字符串；tool_result 变 `role:"tool"` 消息；本地图片文件自动读出转 base64 data URI（`_openai_formatter.py:83`）；assistant 消息里的音频块被刻意丢弃防后续调用报错；content 与 tool_calls 双空的消息整条跳过。`promote_tool_result_images=True` 时把工具结果里的图片提取成新 user 消息插回原位（`_openai_formatter.py:307`）。**OpenAIMultiAgentFormatter**（`_openai_formatter.py:362`）则走基类分组路线：agent_message 组压缩成一条 user 消息，历史文本包进 `<history>` 标签、逐条带 `名字: 内容` 前缀（`_openai_formatter.py:484`）；tool_sequence 组直接委托 Chat 版实例格式化——组合而非继承。

**DashScope 方言**（`src/agentscope/formatter/_dashscope_formatter.py:147`）：类 docstring 明列三条已知 API 坑（qwen-vl-max 缺 content 报 KeyError、content=None 报 TypeError、qwen3-max 空文本触发重复调工具），对策是给无有效内容的消息兜底空列表。媒体块本地路径转 `file://` 绝对路径（`_dashscope_formatter.py:48`）；出口处 `_reformat_messages` 把纯文本多块 content 合并成单字符串——专为 HuggingFaceTokenCounter 的计数兼容。多智能体版（`_dashscope_formatter.py:413`）同样走 `<history>` 路线，但要求 tool 消息位于输入末尾。

## 3. 外部连接

上游只有 `Msg` 与内容块类型；下游唯一消费者是 ReActAgent 的 `_reasoning`（`src/agentscope/agent/_react_agent.py:554` 处 `formatter.format(msgs=[system, *memory...])`）与查询重写、压缩等支线——凡是把记忆变 prompt 的地方都过 formatter。`token_counter`/`max_tokens` 构造参数接 `TokenCounterBase`，不传则截断环退化为直通。tracing 的 `@trace_format` 装饰器挂在 format 上做全供应商统一的格式化观测。

## 4. 数据流

一次推理前的翻译：memory 取出的 Msg 流 → `format` deepcopy → `_format` → 单智能体直译成 chat.completions 消息数组；多智能体先分组：开场若干轮对话被压成带 `<history>` 的首条 user 消息，紧随其后的工具调用/result 段保持原生 tool 消息序列 → `_count` 计 token → 超限则 `_truncate` 从最早的可配对边界整段丢弃 → 重新排版直到达标 → 交给 model 层发请求。工具结果里若有图片：默认降级成路径文字；开 promote 后以 user 消息形式回流给模型。

## 5. 设计决策

方言差异全部上收到 formatter、model 保持哑管道，新增供应商=写一个 formatter+一个 model 而不动 agent。截断做成"排版-计数-砍-重排"重试环而非一次精确切分，是因为 token 数只有排版成 API 格式后才可数，循环是最诚实的实现；代价是极端超限时会多排几次版。多智能体历史压缩成 `<history>` 文本是有损但通用的方案——多数 API 的 name 字段不参与多实体区分，塞进文本是最大公约数。DashScope 用运行时兜底（空列表）而非报错，是对上游 API 行为不稳定的事后防御。

## 6. 新人提示

- 目录里没有 `_formatter_base` 之外更深的基类：`support_tools_api`/`support_multiagent`/`supported_blocks` 是各 formatter 类上的声明式属性，换供应商前先看这三行，别靠猜。
- `_truncate` 砍的是"最早完整对"而非固定条数：依赖消息顺序时注意恢复/重放场景的 id 配对必须完整，否则直接 ValueError（`_truncated_formatter_base.py:211`）。
- 多智能体格式器要求 tool 消息在输入末尾（DashScope 版 note 明示）：若你在 MsgHub 中途插入工具调用轮，分组器会把它切走，历史里看不到。
- 本地图片走 base64 内联（`_openai_formatter.py:83`）：大图的 token 成本会翻倍，生产环境优先用 URL source。
- `convert_tool_result_to_string` 会把 base64 媒体写到本地磁盘（`_formatter_base.py:100`）：长跑服务注意磁盘堆积。
- 与 ONBOARDING 4.2 节互补：那边一句"截断兜底在 TruncatedFormatterBase"，本文拆开重试环、分组状态机与配对砍头三件事。

自报：04-formatter.md｜约 3650 字符（不计空格）｜锚 18 个
