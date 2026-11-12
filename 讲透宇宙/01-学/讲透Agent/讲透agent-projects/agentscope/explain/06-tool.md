# 06 tool 工具系统：Toolkit 分发中枢与 MCP 桥

## 1. 角色定位

tool 子系统管"智能体能做什么"。中枢是 `src/agentscope/tool/_toolkit.py` 的 `Toolkit`（`_toolkit.py:117`）：一个继承 StateModule 的工具箱，负责注册/移除/分组/激活、JSON schema 导出、统一调用分发与中间件增强。目录形态勘误：不存在 `_tool_base.py`——"工具"不是类，而是"任意返回 `ToolResponse`（`_response.py:12`）的函数"，schema 从 docstring/type hints 自动解析。MCP 桥在顶层 `mcp/` 子包：`MCPToolFunction`（`src/agentscope/mcp/_mcp_function.py:15`）把远端 MCP 工具包装成本地可调用对象，再经 `register_mcp_client` 灌进 Toolkit，与普通函数同池管理。

## 2. 内部结构

**注册面** `register_tool_function`（`_toolkit.py:269`）按函数形态三路分派：`MCPToolFunction` 直接取其现成 schema；`partial` 对象把绑定参数并入 preset_kwargs；普通函数走 `_parse_tool_function` 从 docstring+签名生成 schema。同名冲突由 `namesake_strategy` 四态处置（raise/override/skip/rename）。工具组机制让工具可整组启停：basic 组永远在 schema 里，其余组仅激活时可见。

**schema 出口** `get_json_schemas`（`_toolkit.py:545`）只导出"basic 或所在组激活"的工具；若注册了元工具 `reset_equipped_tools`，会即时用 `create_model` 动态拼一个以组名为字段的 pydantic 模型挂上去——这就是 ReActAgent 的 `enable_meta_tool`：模型自己决定装备哪些组。Toolkit 还内置 agent skills 字典，`get_agent_skill_prompt` 被 ReActAgent 的 `sys_prompt` property 拼接进系统提示。

**分发面** `call_tool_function`（`_toolkit.py:674`）是 ReActAgent `_acting` 的直接下游，设计要点是**永不抛异常**：函数名不存在返回带 "FunctionNotFoundError" 文案的 ToolResponse（`_toolkit.py:700`）；所在组未激活同样返回提示文本（`_toolkit.py:721`）；工具执行抛 `McpError` 或任意 Exception 一律转成错误文本 ToolResponse（`_toolkit.py:778`、`_toolkit.py:788`）；协程内被取消则产出 `is_interrupted=True` 的特殊响应（`_toolkit.py:757`）。返回值按 AsyncGenerator/Generator/ToolResponse 三态分别包成统一的异步生成器（`_toolkit.py:801`），postprocess_func 可选挂在出口。中间件 `_apply_middlewares`（`_toolkit.py:57`）在运行时读实例的 `_middlewares` 列表，逆序套娃成洋葱链——同一装饰器工厂，中间件可动态增删。

**MCP 桥**：`register_mcp_client`（`_toolkit.py:817`）先检查有状态客户端已连接，list_tools 后按 enable/disable 白黑名单过滤，逐个 `get_callable_function(wrap_tool_result=True)` 转成 MCPToolFunction 再走普通注册。`MCPToolFunction.__call__`（`_mcp_function.py:82`）双通道：无状态通道每次调用都重新 `client_gen()` 建流、`ClientSession.initialize()`、call_tool、随上下文退出销毁（`_mcp_function.py:89`）；有状态通道复用长连 session 直呼。`wrap_tool_result=True` 时把 MCP 内容块转成 AgentScope 块并包成 ToolResponse。

## 3. 外部连接

上游：ReActAgent 构造时注入（缺省自建空箱），`_reasoning` 每轮取 `get_json_schemas` 喂模型，`_acting` 调 `call_tool_function`（消费点 `src/agentscope/agent/_react_agent.py:683`）。横向：长短期记忆在 agent_control 模式下把 `retrieve_from_memory` 等两个方法注册为工具；PlanNotebook 的计划工具以 `plan_related` 组挂入；`generate_response` 结构化输出工具也走同一注册面。状态侧：Toolkit 的 state_dict 只存激活组名，session 恢复时只回放激活状态（见 03 篇）。MCP 客户端四实现（stdio/http stateful/http stateless/http_stateless）都在 `mcp/` 包。

## 4. 数据流

模型产出一个 tool_use 块 → `_acting` 传入 `call_tool_function` → 查名/查组激活 → 合并 preset_kwargs 与模型给参 → 原函数执行（async/async-gen/sync-gen 三态）→ 异常全部就地转文本响应 → 包装成统一异步生成器（过中间件洋葱）→ 逐 chunk 吐累积 ToolResponse → agent 写成 ToolResultBlock 入记忆。MCP 路线在"原函数执行"一步换成 MCPToolFunction：本地或远端 session call_tool → MCP 内容块转 AgentScope 块 → 包 ToolResponse 返回，对上层完全透明。

## 5. 设计决策

"工具=函数而非类"把接入成本降到最低（写函数+docstring 即得 schema），代价是复杂工具态必须外置。错误不抛而返回文本，是让模型看得见失败、可自我重试——把异常处理变成推理循环的一部分。组激活把上百工具的 schema 噪声压到按需供给，配合元工具形成"模型自管装备"的闭环。MCP 双通道设计（每调用新建会话 vs 长连复用）把无状态工具的部署简单性与有状态工具（如浏览器）的会话连续性分开定价。中间件用"运行时读实例列表"而非注册时固化，支持热插拔，代价是每次调用多一层间接。

## 6. 新人提示

- 目录勘误：没有 `_tool_base.py`/`Tool` 基类；工具契约就是"返回 ToolResponse 或其生成器"（其五个字段里 `is_last`/`is_interrupted` 是流式与中断语义的关键）。
- 错误静默化是双刃剑：工具执行失败 agent 不会崩，但你也别指望异常栈进日志——错误文本直接进了模型上下文（`_toolkit.py:788`）。
- 有状态 MCP 客户端必须 LIFO 关闭（`src/agentscope/mcp/_http_stateful_client.py:24` 的 note 与上游 python-sdk issue 577），多客户端后开先关，否则报错。
- `reset_equipped_tools` 的 schema 是每次 `get_json_schemas` 动态重建的：改组描述后无需手工刷新，但别在调用间隙缓存旧 schema。
- preset_kwargs 不进 schema、对模型不可见（`_toolkit.py:545` 的 note）：适合塞凭据类参数，也意味着模型永远改不了这些参数。
- 与 ONBOARDING 4.2/坑 10 互补：那边点到 LIFO 与工具注册入口，本文拆开错误转文本、三态返回包装与 MCP 双通道三个分发级机制。

自报：06-tool.md｜约 3410 字符（不计空格）｜锚 18 个
