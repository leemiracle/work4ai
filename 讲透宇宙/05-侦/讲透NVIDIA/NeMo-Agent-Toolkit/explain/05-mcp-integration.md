# 05 MCP 集成：NAT 与 Model Context Protocol 的双向桥

## 一、角色定位

`nvidia_nat_mcp` 包接入 MCP 生态的两个方向：**server 方向**——把 NAT workflow/functions 发布为 MCP server，供任意 MCP 客户端当工具调用；**client 方向**——把外部 MCP server 的工具作为 function_group 注册进 builder，供 NAT 的 LLM agent 调用。前者与 fastapi/console 同属 front_end 家族，后者属 function_groups 家族。

入口在 entry points（`pyproject.toml:78-86`）四组；包级 `register.py:20` 汇入两侧注册。

勘误（重要）："client 方向经 tool_converter 转成 NAT function"与源码不符——tool_converter 只服务 server 方向（`tool_converter.py:373`，NAT function 包装为 MCP tool）；client 方向转换在 `client_impl.py:487`（mcp_session_tool_function，FunctionInfo.create 落成 NAT function）。

## 二、内部结构

**server 方向：front_end 形态。** `MCPFrontEndConfig(FrontEndBaseConfig, name="mcp")`（`server/front_end_config.py:29`）：port 9901、transport 默认 streamable-http、tool_names 控发布面、base_path 挂载、server_auth 认证；校验器（`:83`）对公网无认证与 sse+auth 告警。`MCPFrontEndPlugin`（`server/front_end_plugin.py:30`）的 `run()`（`:61`）：建 builder → worker.create_mcp_server() → worker.add_routes() → 默认 `run_streamable_http_async()`（`:103`）；配 base_path 则把 `mcp.streamable_http_app()` mount 进 FastAPI 包装 app（`:141`）。注册走 `@register_front_end`（`server/register_frontend.py:23`），即 `nat mcp serve` 落点（`cli/commands.py:43`）。

**server worker：发布管线。** Worker 双层（Base `server/front_end_plugin_worker.py:43`，默认实现 `:357`，`create_mcp_server` `:377` 可挂 AuthSettings+TokenVerifier）。`_default_add_routes`（`:123`）：health 端点 → `builder.build()`（`:147`）→ 收齐全部 functions 与 workflow 本体 → tool_names 过滤（`:153`）→ 每 function 建 SessionManager（Workflow 直接用、普通 function 包成 mini-workflow，`:170`）→ `register_function_with_mcp`（`:187`）→ 零函数 RuntimeError。调试面 /debug/tools/list（`:258`）与 /debug/memory/stats（`MemoryProfiler` `memory_profiler.py:25`）。

**tool_converter：NAT function 到 MCP tool。** `register_function_with_mcp`（`tool_converter.py:373`）取 input_schema 与描述，`create_function_wrapper`（`:167`）做脏活：ChatRequest 输入折叠成单 query 参数（`:191`）；参数名清洗与碰撞映射（`:66`）；default_factory 哨兵防 FastMCP 提前物化默认值；动态 `__signature__`（`:323`）对 MCP 隐藏 ctx，wrapper 内剥 ctx、重验证后经 `session_manager.run(payload)`（`:290`）执行保 observability，最后 `mcp.tool(...)` 注册（`:406`）。

**认证。** server 侧 `IntrospectionTokenVerifier`（`server/introspection_token_verifier.py:27`）适配 mcp SDK TokenVerifier 并委托核心包 BearerTokenValidator——支持 jwks/introspection/discovery 多模式，类名以偏概全。client 侧两类 provider：`mcp_oauth2` 交互式（`auth/auth_provider_config.py:26`）与 `mcp_service_account` 服务账号（`auth/service_account/provider_config.py:86`）；OAuth 回调复用 console 的 redirect server（`auth/auth_flow_handler.py:209`）。

**client 方向：function_group 形态。** `MCPServerConfig`（`client/client_config.py:36`）定义 transport stdio/sse/streamable-http 与字段互斥校验（`:65`——stdio 禁 url/auth、sse 禁 auth）；`MCPClientConfig(name="mcp_client")`（`:140`）带 session_aware_tools 默认 True、max_sessions 100、idle 1 小时；per-user 变体配置 `:154`。三传输实现共享 MCPBaseClient（`client/client_base.py:139`，带重连与 OAuth 注入）。核心 `MCPFunctionGroup`（`client/client_impl.py:150`）是 RWLock 会话池：session_id 从 Context cookie 解析（`:232`）、双检建会话、ref_count 防清理竞态（锁协议 23 行注释 `:155`）。注册入口（`:555`）：建客户端 → get_tools → tool_overrides 改名 → 逐工具 add_function（`:664`）；per-user 变体（`:690`）每用户独立 client。HTTP 工具清单路由 `/mcp/client/tool/list`（`client/fastapi_routes.py:222`）由核心 fastapi worker 可选拼装；CLI 另有 tool call/ping（`cli/commands.py:1067`）。

## 三、外部连接

依赖核心包的 FrontEndBase/WorkflowBuilder/SessionManager/BearerTokenValidator；跨包复用 console 的 `_FastApiFrontEndController` 起 OAuth redirect server。协议面：MCP 三 transport、OAuth2、httpx。examples/MCP/：simple_calculator_mcp 同时用 stdio 与 streamable-http 两类 server 并示范 tool_overrides；per-user 版换 `_type: per_user_mcp_client`；simple_auth_mcp 示范 mcp_oauth2。

## 四、数据流

**server 向**（外部客户端调 NAT 工具）：POST {host}:9901/mcp 发 initialize/tools/call → FastMCP 路由到 wrapper（`tool_converter.py:247`）→ 剥 ctx 与哨兵默认值 → ChatRequest 走 from_string、否则 schema 重验证 → `session_manager.run(payload)`（`:290`）产出事件流 → 结果字符串/JSON 返回。

**client 向**（NAT agent 调外部工具）：YAML `function_groups._type: mcp_client` → 装配期 get_tools（`client_impl.py:642`）枚举远端工具 → 逐工具注册进 group（`:664`）→ LLM 调用时 `_response_fn`（`:516`）从 context 解析 session_id → 会话池取/建该会话 client → 剥掉框架填的 None（`:64`，注释点名 Kaggle 类 server 拒绝多余 null）→ `mcp_tool.acall` → 字符串结果回 LLM（per-user 配置下每用户独立 client/token）。

## 五、设计决策

1. 复用 front_end 家族：与 fastapi 同基类、同 `@register_front_end`、同 runner_class 钩子——一套注册/启动/CLI 机制两用，观测同源（两向都过 SessionManager/Runner）。
2. 两向转换难度不对称：server 向要伪造 python 签名骗过 FastMCP；client 向因 MCP SDK 的 input_schema 本就是 Pydantic 模型而近乎直通。
3. session_aware_tools 默认开：每会话独立 MCP client 是 per-user token 隔离的前提，代价是会话上限与 idle 清理整套并发机制。
4. 并发正确性当一等公民：RWLock 快读慢写、ref_count 防 TOCTOU、lifetime task 约束 cancel scope——锁协议写成注释契约。
5. SSE 只读兼容：保留 sse 但明示不支持 auth/base_path（`server/front_end_config.py:97`）。
6. 容错哲学：工具调用失败返回错误字符串而非 raise，让 LLM 看到错误并决定重试。

## 六、新人提示

- 起 server 最快路径：examples/MCP/simple_calculator_mcp + `nat mcp serve`；验证用 `GET /debug/tools/list` 与 `nat mcp client ping`。
- 端口心智：fastapi 前端 8000、MCP server 9901。
- 生产三开关：host 非 localhost 必配 server_auth；只有 streamable-http 支持 auth；网关后用 base_path。
- client 排查顺序：transport 互斥校验报错（`client_config.py:65`）→ 连接/重连日志 → null 剥离 → 会话上限（默认 100）。
- 两套过滤别混淆：server 侧 tool_names 控发布面；client 侧 include/exclude 是 FunctionGroup 基类能力（core `data_models/function.py:50`）。
- 参数名清洗使 MCP 工具参数名可能与 NAT 字段名不同，联调盯 alias 映射（`tool_converter.py:210`）。
