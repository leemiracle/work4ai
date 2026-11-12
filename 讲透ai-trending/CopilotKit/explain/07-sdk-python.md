# 07 · sdk-python：Python 侧的 agent 定义面与 AG-UI 事件方言

## 角色定位（16 层架构中位置）

sdk-python 在 16 层知识图谱中独占第 14 层「Python SDK」（184 个节点，其中 40 个 file/class 级节点直接挂层）。它是整个 CopilotKit monorepo 里唯一的非 TypeScript 代码群：JS 侧用 `packages/runtime` + `packages/sdk-js` 定义 agent 与端点，Python 侧则由 `sdk-python` 提供完全对称的定义面——把 Python 写的 LangGraph/CrewAI agent 暴露成 CopilotKit 前端可调用的远程端点。它与第 13 层「外围集成小包」中的 sdk-js 是镜像关系：两侧都消费 AG-UI 协议（sdk-python 经外部包 `ag-ui-langgraph`，见 `sdk-python/copilotkit/__init__.py:23`），都向第 4/6 层的 runtime（v1 GraphQL 与 v2 fetch-handler）提供 agent 发现与执行入口。

一句话：runtime 是"大脑"，前端 React 是"脸"，sdk-python 是"Python 世界的双手"。

## 内部结构（关键文件+行号锚拆解）

**包结构**（`sdk-python/copilotkit/`，21 个 Python 文件约 5700 行）：

- **`copilotkit/__init__.py`** — 57 行的公共导出面。`from .sdk import CopilotKitRemoteEndpoint`（`__init__.py:4`）确立主入口；`from ag_ui_langgraph.middlewares.state_streaming import StateStreamingMiddleware, StateItem`（`__init__.py:23-26`）把外部 AG-UI LangGraph 适配包的符号直接透出为一级 API。最著名的一行是 `__init__.py:49`：

  ```python
  "CrewAIAgent",  # pyright: ignore[reportUnsupportedDunderAll] pylint: disable=undefined-all-variable
  ```

  `__all__` 声明了 `CrewAIAgent`，但文件顶部**没有任何 import 引入它**——注释里的两条 linter 抑制就是这个"已知谎言"的自首。真身必须 `from copilotkit.crewai import CrewAIAgent` 显式导入（`copilotkit/crewai/__init__.py:5`），这样 crewai 重依赖（pyproject 中 optional，`pyproject.toml` 的 `[tool.poetry.extras] crewai`）才不会拖累所有用户。

- **`copilotkit/sdk.py`**（397 行）— 核心端点类。`CopilotKitRemoteEndpoint`（`sdk.py:66`）的 docstring 占了文件一半篇幅（四个完整用法示例，L84/108/124/138 的 `from copilotkit import ...` 全在 docstring 内非真实代码）。真正的运行逻辑只有五个方法：`__init__`（`sdk.py:215`，`actions`/`agents` 均接受 `List` 或工厂函数 `Callable[[CopilotKitContext], List[...]]`，懒加载模式）；`info`（`sdk.py:228`）返回 actions/agents 清单与 `sdkVersion`（`sdk.py:251`，取自 `metadata.version`，`sdk.py:22-25` 的 try/except 处理未安装元数据的情形）；`execute_action`（`sdk.py:269`）按名查 action 后执行 handler；`execute_agent`（`sdk.py:297`）；`get_agent_state`（`sdk.py:346`）。

  文件尾是兼容别名：`class CopilotKitSDK(CopilotKitRemoteEndpoint)`（`sdk.py:387`），构造器里 `warnings.warn("CopilotKitSDK is deprecated since version 0.1.31. Use CopilotKitRemoteEndpoint instead.")`（`sdk.py:392-393`）——注意任务书语境里"CopilotKitSDK=兼容别名"经源码核实是**继承式**别名而非赋值式（`CopilotKitSDKContext = CopilotKitContext` 那条才是赋值式，`sdk.py:63`）。

- **`copilotkit/protocol.py`**（305 行）— AG-UI 事件方言的 Python 表达。甄别修正：digest 笔记称之为"纯 dataclass"文件，源码实测全部是 **TypedDict 而非 dataclass**（`protocol.py:8` `from typing_extensions import TypedDict`）——共 15 个 TypedDict + 2 个 Enum，即任务书所说"17 类型"的实态。两个枚举：`RuntimeEventTypes`（`protocol.py:11-27`，14 个成员，PascalCase 字符串值即 AG-UI 事件名）；`RuntimeMetaEventName`（`protocol.py:30-35`，仅 3 个成员：LangGraphInterruptEvent/PredictState/Exit）。15 个 TypedDict 分两组：协议事件 9 个（TextMessageStart `protocol.py:38`、TextMessageContent `:46`、TextMessageEnd `:54`、ActionExecutionStart `:61`、ActionExecutionArgs `:70`、ActionExecutionEnd `:78`、ActionExecutionResult `:85`、AgentStateMessage `:94`、MetaEvent `:108`）由 `RuntimeProtocolEvent` 联合（`protocol.py:153-163`）聚合；生命周期事件 5 个（RunStarted `:116`、RunFinished `:123`、RunError `:130`、NodeStarted `:137`、NodeFinished `:145`）由 `RuntimeLifecycleEvent`（`:165`）聚合；二者再合成 `RuntimeEvent`（`:173`）。第 15 个 TypedDict 是 `PredictStateConfig`（`protocol.py:179`）。

  **11 个工厂函数**（`protocol.py:188-305`）：9 个事件构造器（text_message_start `:188`、text_message_content `:199`、text_message_end `:208`、action_execution_start `:213`、action_execution_args `:228`、action_execution_end `:239`、action_execution_result `:247`、agent_state_message `:259`、meta_event `:284`）+ 2 个序列化发射器（`emit_runtime_events` `:289`、`emit_runtime_event` `:303`）。工厂是纯 dict 构造（如 `text_message_start` 返回 `{"type": RuntimeEventTypes.TEXT_MESSAGE_START, ...}`，`protocol.py:192-196`）；`emit_runtime_events` 内的 `serialize_event`（`protocol.py:292-298`）把 Enum 值降级为字符串再 `json.dumps` 换行拼接。

- **`copilotkit/langgraph.py`**（495 行）— emit 系列。`copilotkit_customize_config`（`langgraph.py:167`）把 CopilotKit 自定义键写进 LangGraph config；`copilotkit_exit`（`:261`）、`copilotkit_emit_state`（`:298`）、`copilotkit_emit_message`（`:336`）、`copilotkit_emit_tool_call`（`:377`）、`copilotkit_interrupt`（`:456`）。emit 的底层是 LangGraph 的 `adispatch_custom_event`——`copilotkit_emit_message` 实体仅 3 行（`langgraph.py:366-373`）：dispatch `"copilotkit_manually_emit_message"` 事件 + `asyncio.shield(asyncio.sleep(0.02))` 让出事件循环 + 返回 True。这与 JS 侧 `packages/sdk-js/src/langgraph/utils.ts` 的 `dispatchCustomEvent` 事件名家族完全对称（copilotkit_exit / copilotkit_manually_emit_intermediate_state / ...），两侧是同一协议方言的两种发音。

- **`copilotkit/langchain.py`**（30 行）— deprecated 哨兵模块。导入即触发 `warnings.warn("copilotkit.langchain is deprecated. Use copilotkit.langgraph instead.", DeprecationWarning, stacklevel=2)`（`langchain.py:16-20`），然后从 langgraph 转发 7 个同名符号（`langchain.py:6-14`）。这是"编译期兼容+运行期报错引导"的最温和形态（runtime 侧 lib/index.ts 用的是构造即 throw 的硬哨兵，Python 侧选择了只警告不中断）。

- **`copilotkit/crewai/`** 子包（3 文件 1551 行）— `crewai_agent.py`（517 行，`CrewAIAgent` 类）；`crewai_sdk.py`（678 行，`copilotkit_flow_messages_to_copilotkit` 与逆函数 `copilotkit_messages_to_crewai_flow`，是 LangGraph 版同名函数的 CrewAI 对偶）；`copilotkit_integration.py`（356 行，`CopilotKitFlow` 继承外部 `crewai.flow.Flow` 并用 `Generic[S]` 保泛型，`tool_calls_log` 是模块级可变 list）。

- **`copilotkit/runloop.py`**（346 行）— 事件队列基建。`get_context_queue`（`runloop.py:59`）基于 contextvar 支持嵌套 run 上下文隔离；`queue_put(*events, priority=False)`（`runloop.py:106`）的 priority 参数让 exit 类事件插队。

- **`copilotkit/integrations/fastapi.py`**（332 行）— 双代 HTTP 入口。`add_fastapi_endpoint`（`fastapi.py:29`）注册一条 catch-all 路由 `f"{prefix}/{{path:path}}"` 接受全部五种 HTTP 方法（`fastapi.py:62-66`）；其 `use_thread_pool` 参数已弃用（`fastapi.py:38-43` 的 DeprecationWarning）。v0 `handler`（`fastapi.py:77`）按 `body.method` + `path` 字符串分发：`path == ""` 走 info（`fastapi.py:100-106`），`re.match(r"agent/([a-zA-Z0-9_-]+)", path)` 命中则执行 agent（`fastapi.py:109`）；v1 `handler_v1`（`fastapi.py:173`）改为显式路由（handle_info `:237` / handle_execute_action `:250` / handle_execute_agent `:274` / handle_get_agent_state `:312`）。入口处 `set_forwarded_headers(dict(request.headers))`（`fastapi.py:86`）把请求头存入 ContextVar 供出站 LLM 调用传播（header_propagation.py 的机制）。

## 外部连接（imports 边上下游）

- **上游外部依赖**：`langgraph >=0.3.25,<2` + `langchain >=0.3.0` 是必装硬依赖（`pyproject.toml [tool.poetry.dependencies]`）；`ag-ui-langgraph >=0.0.40 [fastapi]` 提供 AG-UI 协议适配；`crewai >=0.118.0` 是 optional extra 且限制 `python >=3.10,<3.14`。`pydantic-core >=2.35.0` 的钉版注释写明动机：cp314 wheel 首现于 2.35.0，旧版在 Python 3.14 强制 Rust 源码构建且撞 PyO3 0.24 上限。
- **下游消费者**：Node 侧 runtime 通过 HTTP 调用 `add_fastapi_endpoint` 挂出的端点（agent 发现走 `/info`，执行走 `/agent/{name}`）；图谱中 Python SDK 层与 runtime 层的连接是**网络边界**而非 imports 边——这正是 1892 节点图里 sdk-python 独占一层的原因（零 imports 边跨语言）。
- **仓内镜像**：`packages/sdk-js/src/langgraph/utils.ts` 的事件名家族（copilotkit_exit 等）与本包 langgraph.py 一一对应；`skills/copilotkit-integrations/references/integrations/langgraph.md` 的示例 `from copilotkit import CopilotKitState/LangGraphAGUIAgent` 直击本包导出面（digest b48 实证）。
- 测试线特殊设计：`tests/test_crewai_flow_messages_to_copilotkit.py` 用 `importlib.spec_from_file_location` 按文件路径直接加载 crewai_sdk.py，绕过 `crewai/__init__.py` 以免拉起 crewai_agent 重依赖；`tests/test_crewai_import_compat.py` 更极端——伪造 crewai 模块在测试内自我满足约束，对真实实现零覆盖（digest b62 甄别：不发 tested_by 边）。

## 数据流

一次典型的 agent 调用闭环：

1. **定义**：用户在 LangGraph 图节点里 `await copilotkit_emit_message(config, msg)`（`langgraph.py:336`）→ `adispatch_custom_event("copilotkit_manually_emit_message", {...})` 写入 LangGraph 事件流；
2. **端点暴露**：`CopilotKitRemoteEndpoint(agents=[...])` + `add_fastapi_endpoint(app, sdk, "/copilotkit")` 把图挂到 FastAPI；
3. **发现**：Node runtime 请求 `GET /copilotkit` → `handler` 判定 `path == ""` → `handle_info` → `sdk.info(context)`（`sdk.py:228`）返回 `{actions, agents, sdkVersion}`；
4. **执行**：runtime `POST /copilotkit/agent/{name}` → `handler` 正则命中（`fastapi.py:109`）→ `handle_execute_agent` → `sdk.execute_agent`（`sdk.py:297`）→ LangGraph astream 事件流中过滤 copilotkit_* 自定义事件；
5. **事件方言翻译**：自定义事件经 crewai_sdk 或 runloop 转成 protocol.py 的 TypedDict 形态（AG-UI PascalCase 字段名：messageId/parentMessageId/actionExecutionId），与 JS 侧 `@ag-ui/core` 的 Zod schema 同构；
6. **头传播**：入站请求头经 `set_forwarded_headers`（`fastapi.py:86`）进 ContextVar，`header_propagation.py` 的 `install_httpx_hook` 让出站 httpx 调用自动携带——审计/多租户链路不中断。

## 设计决策

- **TypedDict 而非 dataclass/pydantic**：protocol.py 选择最薄的 `typing_extensions.TypedDict`——事件就是 dict，工厂函数返回裸 dict，序列化零反射开销。这与 JS 侧 Zod schema 的"运行时校验"哲学相反：Python 侧信任生产者（自家 SDK），把校验成本留给边界（runtime 侧）。甄别注：任务书"17 dataclass"实为 15 TypedDict + 2 Enum。
- **`__all__` 里的幽灵导出**：`CrewAIAgent` 声明而不导入（`__init__.py:49`），是"让 IDE 补全知道它存在、让 import 路径保持显式"的折中——用户 `from copilotkit import CrewAIAgent` 会抛 ImportError，从而被迫走 `copilotkit.crewai` 子路径，重依赖隔离达成。两条 linter 抑制注释把这个技巧钉在了源码里。
- **兼容别名双形态**：类继承式（CopilotKitSDK extends CopilotKitRemoteEndpoint，可拦截构造器发警告，`sdk.py:387-393`）+ 类型赋值式（CopilotKitSDKContext = CopilotKitContext，`sdk.py:63`，零成本）。0.1.31 版本号写进警告文案，弃用有审计锚。
- **deprecate 阶梯**：langchain.py 警告不 throw（生态里 langchain 导入面太广，throw 会炸一片）；fastapi 的 use_thread_pool 警告但保留行为；CopilotKitSDK 警告但功能全同——三级都是"软着陆"，与 runtime 侧 lib/index.ts 构造即 throw 的硬哨兵形成跨语言的弃用策略光谱。
- **README 是营销页不是文档**：Quick Start 的 `from copilotkit import Copilot` / `copilot.add_tool()` / `copilot.run()`（`README.md:31-41`）全部是**不存在的 API**——`__init__.py` 导出面里没有 Copilot 类。阅读时以 `__init__.py:34-57` 的 `__all__` 为准（digest b42 同判）。这是典型的"README 先于/偏离实现"漂移，AI 辅助编码时代尤其危险。
- **langgraph.json 死引用**：`sdk-python/langgraph.json:6` 声明 `"autotale_ai": "./copilotkit/demos/autotale_ai/agent.py:graph"`，但 `copilotkit/demos/` 目录不存在（ls 实证）——LangGraph 平台部署配置指向已删除的 demo，`git log -S autotale` 仅命中引入该文件的提交本身。此文件当前对任何图都是空转。

## 新人提示

1. **别抄 README Quick Start**——先读 `copilotkit/__init__.py`（57 行）看真实导出面；`Copilot()` 不存在，正确的起手式是 `CopilotKitRemoteEndpoint(actions=[...], agents=[...])` + `add_fastapi_endpoint`。
2. **事件名双对照表**：写自定义事件时对照 `protocol.py:11-27`（14 个 RuntimeEventTypes）与 JS 侧 `@ag-ui/core` 的事件 schema——字段名是 camelCase（messageId 不是 message_id），工厂函数已帮你拼好，别手写 dict。
3. **emit ≠ 立即送达**：`copilotkit_emit_message` 末尾的 `await asyncio.shield(asyncio.sleep(0.02))`（`langgraph.py:372`）是刻意让出事件循环保证事件先于节点返回值被消费；删掉它可能导致消息乱序。
4. **crewai 子包是可选世界**：装 `pip install "copilotkit[crewai]"` 才有 `copilotkit.crewai`；CI 里没装时任何对它的顶层 import 都会炸——测试文件用 spec_from_file_location 绕行的原因就在这。
5. **调试入口**：`sdk.py:374` 的 `_log_request_info` + `logging.py` 的 `get_logger` 是 Python 侧唯一的观测面；配合 `COPILOTKIT_SDK_VERSION`（`sdk.py:29`）确认 Node↔Python 版本对齐。
6. **langgraph.json 别照抄**：其中的 autotale_ai 是死引用；你自己的 LangGraph Platform 部署应把 graphs 指向真实存在的图模块路径。
