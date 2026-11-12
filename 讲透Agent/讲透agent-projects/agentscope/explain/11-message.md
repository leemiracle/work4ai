# 11 message 消息类型：Msg 数据类与 ContentBlock 体系

> **勘误（以源码为准）**：任务来源所称的 "JsonModule 体系" 在本仓**不存在**（全仓 grep "JsonModule" 零命中）；真实形态是 `message/_message_base.py` 的 `Msg` 数据类 + `message/_message_block.py` 的 TypedDict 块体系，仅三个文件共约 400 行。（锚相对 `src/agentscope/`）

## 1. 角色定位

Msg 是全框架的**通用货币**：agent、pipeline、memory、formatter、rag、tool、realtime、tts 全以它（或它的 ContentBlock）为交换单元——仓内 42 个文件 import Msg。它同时承载三种语义：对话轮（name/role/content）、工具协议（tool_use/tool_result 块）、多模态容器（image/audio/video 块）。设计目标只有一个：让所有子系统说同一种话，供应商差异全部推给 formatter 层翻译。

## 2. 内部结构

**Msg**（`message/_message_base.py:21`）：六字段构造——name（发送者展示名）、content（`str | Sequence[ContentBlock]`，`message/_message_base.py:27`）、role（仅 user/assistant/system 三值，构造时 assert，`message/_message_base.py:61`）、metadata（结构化输出槽）、timestamp（毫秒精度截断）、invocation_id。id 由 shortuuid 生成（`message/_message_base.py:66`），是 memory 去重的依据。序列化是朴素的 `to_dict`/`from_dict` 对（`message/_message_base.py:75`）。

**访问器**：`get_text_content`（`message/_message_base.py:123`）有 str 快路径（`:136`），块路径只回收 `type=="text"` 的块（`:141`）；`get_content_blocks`（`message/_message_base.py:198`）把 str 内容自动包装成单 TextBlock（`:216`）后按 type 过滤（`:223`）——对外永远以块形态供给。

**块体系**（`message/_message_block.py`）：七种 TypedDict（total=False + Required 标注，`message/_message_block.py:9` 的 TextBlock 即范式）组成 `ContentBlock` 联合类型（`message/_message_block.py:110`）。ToolUseBlock 额外留 `raw_input` 保原文（`message/_message_block.py:90`）；ToolResultBlock 的 output 可以嵌套多模态块——工具直接回图。ThinkingBlock 为推理链路单独建模。

## 3. 外部连接

formatter 八家把 Msg 翻成各供应商方言（组 A 04 篇）；memory 按 `msg.id` 去重存储（`memory/_working_memory/_in_memory_memory.py:130`）；rag 的 DocMetadata.content 直接复用块类型；ReActAgent 把结构化输出写进 `msg.metadata`（`agent/_react_agent.py:473`）、查询改写结果也从 metadata 取（`agent/_react_agent.py:963`）；realtime 的 `send` 接受四种块（`realtime/_base.py:59`）；tts 的 `push` 以 Msg 为输入（`tts/_tts_base.py:96`）。

## 4. 数据流

用户 Msg（str content）→ agent → formatter 把块序列拆解为供应商 API 消息 → 模型响应 → TextBlock/ToolUseBlock 组装回 Msg → memory.add 落库 → 下轮 get_memory 取回 → 再进 formatter。str 本质是"语法糖"：任何跨子系统边界处都会被统一包装为块形态。metadata 则是旁路通道：模型的结构化输出、工具的成功标志都从这走，不污染 content。

## 5. 设计决策

①**TypedDict 而非 pydantic/dataclass**：运行时就是普通 dict，json 序列化零转换、子类零继承成本——代价是无校验，块内字段错误要到 formatter 层才爆。②**name 与 role 解耦**：role 管协议位（三家 API 通用），name 管展示位（多 agent 场景同名 role 靠 name 区分），这是多智能体对话可读性的关键。③**块化 content 对齐多模态 API**：Anthropic 风格的 content 数组成为内部规范，供应商特例被压到 formatter。④**str 双轨**：全文检索/日志等纯文本场景免构造块，读取时惰性升级。

## 6. 新人提示

- 勘误 1：`to_dict` 输出**不含 invocation_id**（`message/_message_base.py:75` 的返回字典只有六键），而 `from_dict` 会尝试读它（`message/_message_base.py:95`）——序列化往返会丢这个字段，依赖 invocation_id 做追踪的代码要自己补。
- 勘误 2：`has_content_blocks` 的类型注解 Literal 漏了 `"thinking"`（`message/_message_base.py:103` 起），而 `ContentBlockTypes` 是含 thinking 的（`message/_message_block.py:120`）——运行时传 thinking 正常工作，类型检查器却报错。
- 勘误 3：VideoBlock 的 docstring 写成 "The src of the **audio**"（`message/_message_block.py:76`）——复制粘贴错误，应为 video。
- 坑 4：`get_text_content` 只回收 text 块——thinking、tool_use 内容拿不到，调试"模型到底说了什么"时别拿它当全量视图。
- 坑 5：构造函数用 assert 校验 role/content（`message/_message_base.py:54`-`:61`），`python -O` 下 assert 全部失效，脏 role 会静默流到 formatter 才炸。
