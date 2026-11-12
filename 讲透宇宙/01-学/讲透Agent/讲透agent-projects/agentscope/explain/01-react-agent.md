# 01 ReActAgent 智能体内核：_react_agent.py 与元类钩子机关

## 1. 角色定位

`src/agentscope/agent/_react_agent.py` 是全仓唯一维护的智能体实现，把推理-行动循环、工具调用、双轨记忆、RAG、计划本、记忆压缩、结构化输出、实时中断收进一个类。心智模型分三层：`AgentBase`（`src/agentscope/agent/_agent_base.py:30`）提供调用/广播/中断/钩子容器；`ReActAgentBase`（`src/agentscope/agent/_react_agent_base.py:12`）追加 `_reasoning`/`_acting` 抽象接口与四档钩子位；`ReActAgent`（`src/agentscope/agent/_react_agent.py:98`）填实现。本文同时拆常被忽视的第四层：钩子机关本体在 `_agent_meta.py`，钩子能力是在类创建时刻零侵入挂上的。

## 2. 内部结构

**reply 主循环**：`reply`（`_react_agent.py:376`）先入账与检索，`for _ in range(self.max_iters)`（`_react_agent.py:432`）每轮先查记忆压缩，再 `_reasoning` 拿到带 tool_use 块的消息，为每个块起一个 `_acting` 协程，`parallel_tool_calls=True` 时 gather 并发否则逐个 await（`_react_agent.py:448`）。退出条件：无结构化要求且本轮没有 tool_use 块即返回（`_react_agent.py:513`）；`max_iters` 耗尽则 `_summarizing` 强制总结收尾。

**结构化输出状态机**：传 `structured_model` 时注册 `generate_response` 工具并强制 `tool_choice="required"`（`_react_agent.py:410`）；拿到合法输出后，若本轮已有文本则复用文本块返回，否则注入"现在生成文本回复"HINT 消息并把 tool_choice 改 `none`（`_react_agent.py:491`）；模型不调工具则注入"必须完成结构化输出"提醒并保持 required。`generate_response`（`_react_agent.py:825`）用 `model_validate` 校验参数，失败时把 ValidationError 文本装进 ToolResponse 让模型自纠（`_react_agent.py:845`），成功则经 `metadata.structured_output` 回传，`_acting` 在循环里拦截该 metadata 上抛（`_react_agent.py:701`）。

**记忆压缩**：每轮循环开头检查，`keep_recent` 保尾时按 tool_use/tool_result 的 id 配对整段保留，避免拆散调用与结果（`_react_agent.py:1028`）；token 超阈值才触发，用五字段 `SummarySchema` 生成结构化摘要写回，旧消息打上 `_MemoryMark.COMPRESSED` 标记（`_react_agent.py:1117`），此后所有取记忆处统一 `exclude_mark` 过滤。

**元类钩子机关**：`_AgentMeta.__new__`（`src/agentscope/agent/_agent_meta.py:147`）在类创建时对类体 attrs 里的 reply/print/observe 逐一套上 `_wrap_with_hooks`；`_ReActAgentMeta` 追加包装 `_reasoning`/`_acting`，对应十档钩子位。包装器（`_agent_meta.py:55`）先用 `inspect.signature.bind` 把任意位置/关键字参数归一成 kwargs，再跑实例级+类级 pre 钩子链——每个钩子拿 deepcopy 副本，返回 dict 即替换参数；注意 `args`/`kwargs` 两个键名被特判为可变参数展开后传给原函数（`_agent_meta.py:113`）；post 钩子链依序改写输出。钩子属性名=去下划线的函数名，所以 `_reasoning` 查的是 `_instance_pre_reasoning_hooks`。

## 3. 外部连接

model/formatter/toolkit/memory/long_term_memory/knowledge/plan_notebook/tts_model 全部构造注入，toolkit 缺省自建空箱、memory 缺省 `InMemoryMemory`。`reply` 被 `__call__` 调用：`__call__`（`_agent_base.py:448`）记录 `asyncio.current_task()` 供 `interrupt` 取消，finally 里 `_broadcast_to_subscribers`（`_agent_base.py:469`）把回复推给 MsgHub 订阅者——这是 pipeline 编排成立的物理基础。被打断时 CancelledError 转交 `handle_interrupt`，`_reasoning` 在 finally 里为未完成的 tool_use 补造假 tool_result 消息，保证记忆里调用与结果永远成对。产出侧：reasoning 消息流式经 `self.print` 出去，被 `stream_printing_messages` 消费。

## 4. 数据流

`await agent(msg)` → `__call__` 记 task → reply 入账+长期记忆/RAG 检索 → 循环{压缩检查 → `_reasoning`：PlanNotebook 提示入记忆 → `formatter.format` 组 prompt → 清 HINT → `self.model(prompt, tools=..., tool_choice=...)` → 流式则逐 chunk `print(msg, False)`、末次 `print(msg, True)` → reasoning 消息入记忆 → `_acting`：`toolkit.call_tool_function` → 逐 chunk 更新 tool_result 块、`is_interrupted` 时抛 CancelledError → finally 入记忆} → break → 返回 → `__call__` 广播。RAG 查询重写是隐藏支流：临时把 `model.stream` 置 False、用 `_QueryRewriteModel` 结构化输出改写检索词、finally 恢复流式开关。

## 5. 设计决策

钩子放元类而非装饰器，换来"子类覆写接口自动获得钩子"且无需记得加装饰器；代价是包装发生在类定义时，动态打补丁会静默失去钩子。钩子一律 deepcopy 入参，杜绝钩子间共享可变状态的脏数据，代价是大消息场景的拷贝开销。HINT 消息"用后即清"配合 `exclude_mark` 过滤，本质是在同一条记忆流里用标记位实现三个视图（全量/有效/临时），比维护多条列表更省、更易序列化。结构化输出复用工具调用通道而非各家私有 API mode，为的是六家供应商行为一致。

## 6. 新人提示

- `tool_choice` 是循环内变量：结构化流程会在 required/none 间切换，排查"模型突然不调工具"先看 `_react_agent.py:491` 附近的分支。
- 钩子包装断言实例级/类级四类钩子属性必须齐备：自定义 Agent 不调 `super().__init__()` 会直接断言失败，`clear_instance_hooks` 的报错文案也明确提示了这一点。
- pre 钩子返回 None=不改参数，返回非 dict 断言失败；想改 `_reasoning` 的入参必须返回完整 kwargs dict。
- 元类只包装类体 attrs 里定义的方法：继承未覆写的方法时用的是基类那份包装，Mixin 场景易踩。
- `handle_interrupt` 返回消息带 `metadata={"_is_interrupted": True}`，下游判中断认这个键，别比对文案。
- 与 ONBOARDING 4.1 节互补：那边讲钩子位与压缩配置入口，本文补齐参数归一、deepcopy 与 tool_choice 切换三个实现级语义。

自报：01-react-agent.md｜约 3530 字符（不计空格）｜锚 19 个
