# 01 · agent 核心：protocol 消息模型与工具注册中枢

## 角色定位

`sandbox/protocol.py` + `sandbox/server/backends/{error_codes,response_builder}.py` + `sandbox/server/backends/tools/` 与 `sandbox/server/core/decorators.py` 共同构成 AgentFlow 的「agent 核心契约层」：它定义了 agent 与 sandbox 服务端之间说什么（消息模型）、怎么说（HTTP 端点常量）、说错了怎么报（错误码）、报成什么样（标准响应包），以及服务端如何发现并挂载工具（两套互补的注册机制）。这一层是纯定义、零业务——pydantic 模型不 import 任何重依赖，server 与 client 双方共享同一份契约（protocol.py 文件头 L6「fully independent of other modules」明示了这一设计意图）。

## 内部结构

**protocol.py 全文 13 个类**，恰好是一张自洽的消息分类学：

- `MessageType`（L23）与 `HTTPEndpoints`（L193）两个枚举/常量类——前者 10 个消息类型值（execute/execute:batch、session 四种、init 三种），后者 17 个端点常量（heartbeat/execute/session/init/tools/health/shutdown/warmup 两族，L195-225），消息类型与 URL 一一对应；
- `BaseMessage`（L41）——公共信封：`message_id`（uuid4 工厂 L43）、`timestamp`、`worker_id`、`session_id`，`Config.extra = "ignore"`（L49-51）容忍旧字段向后兼容；
- **10 个直接子类**构成请求族：执行线 `ExecuteRequest`（L68）/`ExecuteBatchRequest`（L102），会话线 `SessionCreate/Destroy/List/RefreshRequest`（L116/L129/L137/L143）与 `WorkerDisconnectRequest`（L150），初始化线 `InitResourceRequest`（L159）/`InitBatchRequest`（L171）/`InitFromConfigRequest`（L181）。

`ExecuteRequest` 是整个系统最热的一条消息，action 字段的「资源前缀」语法在此定义：`"vm:screenshot"`、`"rag:search"`、裸 `"TextSearch"` 三种形态（docstring L71-78），`get_resource_type()`（L88-93）与 `get_action_name()`（L95-99）负责切分。注意 L81-82 用 `# type: ignore` 把父类的 `Optional[str]` worker_id 覆写为必填 `str`——pydantic 允许这种收窄，mypy 报怨被显式压制。

**错误码层**（error_codes.py）：`ErrorCode(IntEnum)`（L14）以 0/4xxx/5xxx 三段划分语义——4xxx=调用方责任不可重试，5xxx=执行方责任按消息定夺（L20-27 注释明示策略）。有趣的是 L30-53 保留了一整批 legacy 细分码（4002 INVALID_REQUEST_FORMAT 到 5013 INTERNAL_ERROR），文件头又标注「otherwise can be removed」——两套并存，实际代码里 `build_error_response` 接受任意 int，细分码成了可选精度。`get_error_message()`（L56-92）是码→人话的映射表。

**响应包层**（response_builder.py）：`build_success_response`（L13-46）与 `build_error_response`（L49-86）输出统一的 `{code, message, data, meta}` 四件套，meta 里固定带 tool/execution_time_ms/resource_type/session_id/trace_id，`trace_id or str(uuid.uuid4())`（L44）保证未传时也能兜底生成——分布式追踪零成本接入。`ResponseTimer`（L89-107）上下文管理器统一计时。

**工具注册中枢**是本篇的重头戏，双轨制：

1. **有状态轨**：`@tool` 装饰器（core/decorators.py L116-191）只做「标记」不做注册——把 `ToolMetadata`（L66）挂到函数的 TOOL_MARKER 属性（L180），wrapper 上也复制一份（L187）；真正的注册发生在 `HTTPServiceServer.load_backend()` 反射扫描 `scan_tools`（L220）时。这是「声明与装配分离」。
2. **无状态轨**：`tools/__init__.py` 的模块级注册表 `_API_TOOLS: Dict[str, APIToolInfo]`（L56）+ `register_api_tool` 装饰器（L59-119）。装饰器会从 docstring 首行提取 description（L87-89），并向 BaseApiTool 实例自动注入 `tool_name`（L93-95）与 `resource_type`（L99-103，仅当实例还是默认值 "unknown" 时）。

注册表能工作的关键是 **`__init__.py` 尾部的四行副作用 import**（L221-225）：`from . import websearch, ds_tool, doc_tool, text2sql_tool`——每个工具模块在底部执行 `register_api_tool(...)(SomeTool())`（如 ds_tool.py L586-602）完成自注册，而 `__init__` 又反向 import 它们。这种「tools/__init__ ↔ 四工具集双向 import」形成一个自举回路：任何人 import `tools` 包，四个模块的注册副作用全部触发，注册表即满。`register_all_tools`（L156-214）随后把注册表批量挂到 server，并按 `config_key` 从配置注入实例配置（L186-194，跳过 `_` 前缀注释键 L189-190）。

**BaseApiTool 基类**（base_tool.py L22）是无状态轨的脚手架：`__call__`（L125-200）包办计时、日志、错误分类、响应构建全流程，子类只需实现 `execute()`（抽象方法 L66-81）。两条错误通道语义不同：抛 `ToolBusinessError`（L11-20，可携自定义 code 与 data）→ WARNING 级业务错误响应（L168-183）；抛任意 Exception → ERROR 级 5000 响应（L185-200）。`_sanitize_inputs`（L83-123）给日志与回显做脱敏：`config/api_key/serper_api_key/session_id` 等敏感键直接丢弃（L89-93），超 500 字符截断（L102-104），长 list/dict 折叠为长度摘要——防日志爆炸与凭据泄漏双保险。还有一处巧妙的响应合并（L155-157）：业务返回值若本身含 `result` 键则展平合并而非双层嵌套。

## 外部连接

上游：`HTTPServiceServer`（app.py L159 register_tool / L354 register_api_tool）消费双轨注册结果；`ToolExecutor.execute` 用 ExecuteRequest 驱动注册表里的函数。下游：四工具集（websearch/ds/doc/text2sql）与 MCP backend 都以 BaseApiTool 或 `@tool` 挂入；rollout 的 `AgentRunner` 通过 `convert_tool_schema_to_openai` 把 tool_schemas 翻译成 OpenAI function calling 格式喂给 LLM——协议层定义的 action 名与 tool_schemas 里的 schema 名必须严格一致，这是隐式耦合点。`sandbox/__init__.py` L55-65 顶层再导出 protocol 全家。

## 数据流

一次 `execute("vm:screenshot", {})` 的契约流：client 构造 `ExecuteRequest`（action="vm:screenshot"，worker_id 必填）→ POST `/api/v1/execute`（HTTPEndpoints.EXECUTE L199）→ ToolExecutor 解析前缀得 resource_type="vm" → 取/建会话 → 调注册表里的函数 → 无论成败都经 `build_success_response`/`build_error_response` 包成四件套回到 client。LLM 侧的闭环则是：tool_schemas 进 prompt → 模型吐 tool_call → runner 转 ExecuteRequest → 响应 data 再经 `format_tool_result` 压缩回消息。

## 设计决策（含批判）

- **共享契约单文件化**：server/client 共用 protocol.py，杜绝两端 schema 漂移；代价是文件成为合并冲突热点。
- **`extra = "ignore"` 的宽容信封**：平滑协议演进，但也意味着拼错字段名会被静默吞掉——调试时「发了没生效」类问题需先查拼写。
- **注册表自举的双刃**：副作用 import 让「import 即注册」极简，但注册顺序取决于 import 顺序，且模块级全局字典不可重置——单进程内多次测试可能累计脏注册。
- **错误码双体系残留**：legacy 细分码与新两段制并存且注释自认可删，属于「没做完的迁移」，新人容易困惑该用哪套；建议只用 0/4000/5000 三值+details 字符串。
- **一处死代码**：`sandbox/__init__.py` L77 `from .server.backends.base import StatelessBackend`——base.py 里根本没有这个类（实测 `sandbox.StatelessBackend` 为 MISSING），try/except ImportError 静默吞掉。靠 Python import 语义，同 try 块前一句绑定的 Backend/BackendConfig 仍可用，但这条死导入说明「文档里承诺的 StatelessBackend 从未落地或已被删」。

## 新人提示

1. 读代码顺序建议：protocol.py → error_codes/response_builder → base_tool.py → tools/__init__.py → decorators.py，两小时可通读，这一层不到 1500 行却是全仓咬合面。
2. 新增无状态工具三步：写类继承 BaseApiTool → 模块底部 `register_api_tool(name, config_key)(Instance())` → 若要进 LLM prompt 还需在 tool_schemas 对应域补 schema 并在 `__init__.py` L221-225 确认 import 链。
3. 调试时先看响应 meta.trace_id 与 execution_time_ms，配合 `_sanitize_inputs` 的 inputs 回显可完整还原一次调用现场，无需翻服务端日志。
4. action 名的冒号前缀是「路由键」，不是命名装饰——它直接决定 ToolExecutor 走哪个 backend 的会话；起名时想清楚资源归属再定前缀。
