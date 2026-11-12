# 05 BaseToolkit 工具基座：camel/toolkits/base.py

## 1. 角色定位

camel/toolkits/base.py 只有 165 行，却是全仓 54 个 toolkit 的共同基座（图谱"工具系统基座"层的根节点）。`BaseToolkit`（camel/toolkits/base.py:61）定义工具包的三件套契约：统一 timeout 治理（构造参数+自动包裹）、get_tools 导出 FunctionTool、以及内嵌 FastMCP server 的 MCP 导出面。同文件的 `RegisteredAgentToolkit`（camel/toolkits/base.py:119）提供工具反向持有 agent 的 mixin，是 ScreenshotToolkit 等需要"工具内调 agent"场景的基础。工具层与 agent 层的边界就画在这个文件里：BaseToolkit 不知道 ChatAgent 的存在（仅 TYPE_CHECKING 引用），agent 却深度依赖它导出的工具 schema。

## 2. 内部结构

`BaseToolkit` 的特殊性在于**两套隐式改写通道同时生效**：

- **元类层（遥测）**：`class BaseToolkit(metaclass=AgentOpsMeta)`（camel/toolkits/base.py:61）。AgentOpsMeta 定义在 camel/utils/commons.py:617——若 `AGENTOPS_API_KEY` 环境变量存在且 agentops 可导入（commons.py:582 的 ToolEvent 门控），元类会给类体里每个 callable 挂 agentops_decorator（包装为 ToolEvent 记录上报），唯独跳过 `get_tools`（commons.py:630 的显式排除）。未配 key 时 ToolEvent=None，元类退化为普通 type，零开销。
- **`__init_subclass__` 层（超时）**（camel/toolkits/base.py:80）：每个子类定义时遍历类体公开 callable，逐一 `setattr(cls, attr_name, with_timeout(attr_value))`（camel/toolkits/base.py:95）。两个逃生门：方法签名自带 `timeout` 参数则跳过（camel/toolkits/base.py:90 的 inspect 检查）；或挂 `@manual_timeout`（camel/toolkits/base.py:30，只设 `_manual_timeout` 属性标记）声明自行管理。

`with_timeout`（commons.py:1007）的语义值得细读：未显式传 timeout 时从实例 `getattr(self, 'timeout', None)` 取（构造默认 Constants.TIMEOUT_THRESHOLD，camel/toolkits/base.py:73 校验必须为正）；同步版本在执行前检测 `asyncio.get_running_loop()`（commons.py:1066）——若当前线程已有运行中的事件循环，则放弃线程切换直接内联执行不强制超时，以保住 asyncio 上下文语义（如工具内 create_task 不被丢到别的线程）；异步版本用 `asyncio.wait_for`。

类体里还有一处罕见写法：`from mcp.server import FastMCP` 直接写在类体内（camel/toolkits/base.py:68）作类型注解用途，同时声明 `mcp: FastMCP` 与 `timeout` 两个类属性。方法面很薄：`get_tools` 抛 NotImplementedError（camel/toolkits/base.py:97）强制子类实现；`run_mcp_server`（camel/toolkits/base.py:107）以 stdio/sse/streamable-http 三模式拉起 `self.mcp`。

`RegisteredAgentToolkit`（camel/toolkits/base.py:119）：`_agent` 私有引用 + `agent` property（camel/toolkits/base.py:131，未注册时 logger.warning 并返回 None）+ `register_agent`（camel/toolkits/base.py:154）。ChatAgent 侧有配套钩子 `_is_called_from_registered_toolkit` 在 step 时检测调用来源，防止工具内再调 agent 造成递归。

## 3. 外部连接

- **@MCPServer 装饰器**（camel/utils/mcp.py:133）是 MCP 导出的真正工厂：其 `__call__` 包装类构造——`instance.mcp = FastMCP(server_name)`（mcp.py:230）；不指定 function_names 且是 BaseToolkit 子类时，从 `get_tools()` 推断工具清单（取 FunctionTool 的 `mcp_registration_func` 或 `.func`），并经 `_validate_function_types`（mcp.py:267）做 Pydantic 类型校验。仓内 54 个 toolkit 挂此装饰器。
- **MCP 三形态并存**（图谱钉版）：①继承 MCPToolkit（作为客户端连外部 MCP server，如 NotionMCP/Playwright）；②组合 MCPToolkit（如 MinimaxMCP 委托内层实例）；③独立 BaseToolkit+@MCPServer 自建 server。
- **FunctionTool** 是 get_tools 的返回契约，agent 侧 `_get_full_tool_schemas` 直接消费。
- **ChatAgent 反向注册**：agent 构造参数 `toolkits_to_register_agent` 触发 register_agent——注意 docstring 明示这**不会**把工具加给 agent，工具仍需走 tools 参数。

## 4. 数据流

工具定义期：子类定义 → AgentOpsMeta 先过一遍（可选遥测装饰）→ `__init_subclass__` 再过一遍（with_timeout 包裹）→ `@MCPServer` 包装 `__init__` 注入 FastMCP。运行期两条路：agent 路径——agent step 拿到 tool_calls 后 `_execute_tool` 查 tool_dict 调用（此时实际执行的是被 with_timeout 包过的函数，超时返回提示消息而非异常）；MCP 路径——外部 MCP client 请求 → FastMCP 按注册名分发 → 同一个被包裹的函数。两条路最终执行同一份实现，这是"一次定义、两面导出"的设计核心。

## 5. 设计决策

1. **双隐式通道 vs 显式装饰**：timeout 与遥测都是"定义即生效"，子类作者无感知也无从跳过（除非用逃生门）；好处是 54 个 toolkit 行为一致，坏处是读子类源码完全看不到这层行为，栈追踪里也多包装帧。
2. **事件循环感知的同步超时**（commons.py:1066）：宁可不强制超时也不破坏 asyncio 上下文——这个取舍在 async 宿主里跑同步工具时至关重要，但意味着"运行中 loop 内同步调用不受 timeout 保护"这一静默豁免。
3. **类体内 import FastMCP**（camel/toolkits/base.py:68）：把 MCP SDK 依赖推迟到类定义期而非模块导入期，配合 mcp.py 里构造函数内的延迟 import，重依赖隔离风格一致。
4. **`_manual_timeout` 用属性标记而非装饰器注册表**：最轻量的实现，但标记本身可被继承链上的覆写冲掉——覆写父类已标记方法时需重新标记。
5. **agent 反向引用走 mixin 而非构造参数**：避免 BaseToolkit→ChatAgent 的硬依赖，agent 可选注入，工具在无 agent 时警告但可用。

## 6. 新人提示

- **写新 toolkit 的三条铁律**：必调 `super().__init__(timeout=...)`（MinerUToolkit 漏调导致 BaseToolkit 初始化被跳过，是图谱钉版的反例）；长任务方法要么签名带 timeout 参数要么挂 @manual_timeout，否则被全局默认值掐死；get_tools 必须实现。
- **手动 requests 调用不受保护**：PubMedToolkit.get_abstract 等直接 requests 未传 timeout（图谱勘误），BaseToolkit.timeout 管不到方法内部的裸网络调用——超时治理只到函数边界。
- **@MCPServer 与 MCPToolkit 继承二选一别混用**：继承 MCPToolkit 是"当客户端"，@MCPServer 是"开服务端"，混挂会得到两个 server 实例。
- **未注册 agent 的工具调用静默失败**：RegisteredAgentToolkit.agent 返回 None 仅打 warning（camel/toolkits/base.py:131），后续 AttributeError 在调用点才爆，报错位置离根因很远。
- **MCP 类型校验严格**：mcp.py:267 的 `_validate_function_types` 拒绝非 Pydantic 可序列化类型，写工具签名时用 str/int/bool/bytes，复杂对象转 JSON 字符串。
