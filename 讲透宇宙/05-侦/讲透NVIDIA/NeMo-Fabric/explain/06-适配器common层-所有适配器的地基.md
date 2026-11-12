# 06 · 适配器 common 层：Python common 与 TS common/ACP runner

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882 · adapters/python/common（2516 行）+ adapters/typescript/common（1156 行 npm 包 nemo-fabric-adapters-common v0.6.0）

## 一、角色定位

适配器把各家 harness（Claude/Codex/OpenCode/Cline…）翻译成统一契约，而 **common 层是全部适配器的地基**——把"宿主协议循环"这件事做一次，让 19 个适配器各自只写业务差异。图谱里 nemo_fabric_adapters.common 的 __init__.py:4 声明它是"Fabric 适配器实现的共享助手库（生命周期协议/指令校验/relay 工件就绪），被全部 Python 适配器与 langgraph 示例消费"。

消费方式一行见底（hermes/adapter.py:46）：`lifecycle.serve(HermesRuntime, config_loader=AgentConfig.from_mapping)`——适配器只提供 AdapterRuntime 实现，stdin/stdout 协议、校验、错误归一、健康传输全部由 common 接管。

TS 侧与 Python 镜像对称：lifecycle.ts 同样是"验证 NDJSON 生命周期请求、持有一个 adapter runtime、分发 start/invoke/stop、归一化响应"（lifecycle.ts:4-7 模块文档），外加 Python 侧没有的 **ACP 运行器**——@agentclientprotocol/sdk 的会话引擎，让 opencode/pi/strands 等 ACP 系 harness 一处复用。

## 二、内部结构（带行号）

### Python common（八模块）

- **lifecycle.py（888 行，最大）**：lifecycle.py:8 模块文档"Wire protocol for persistent local adapter hosts"。`AdapterRuntime` Protocol（lifecycle.py:43-62）定义三方法契约 start/invoke/stop（invoke 签名收发类型化 AgentRunRequest/AgentRunResult）；`serve()`（lifecycle.py:859-888）做两件关键事：**redirect_stdout(sys.stderr)**（:877-878 注释："整个宿主生命周期内把进程 stdout 留给协议，包括宿主空闲时的 SDK 后台任务"——适配器代码里任何 print 都不会污染协议流）与 asyncio.run(_serve)。`_serve`（lifecycle.py:790-857）主循环用 `asyncio.to_thread(input_stream.readline)` 读行（:804 注释：保持事件循环存活，"ClaudeSDKClient 等持久 SDK 客户端拥有绑定此 loop 的后台任务"）；invoke/invoke_openai_stream 失败标记 state.failed；EOF 后 finally 里 generation+=1、关 health、_stop_after_eof。
- 关键常量（lifecycle.py:64-70）：OpenAI 流式回连 127.0.0.1（:65）、协议 `fabric.openai_stream/v1alpha1`（:67）、profile `openai.chat_completions.chunk/v1`（:68）、单记录 1 MiB 界（:69）。`invocation_deadline`（lifecycle.py:32-40）把 deadline_millis 换算成 loop 单调钟，**一次调用只换算一次**。`_OpenAIStreamWriter`（:102）与 `_validated_openai_stream_payload`（:278）完成流式写出的校验链。
- **utils.py（792 行）**：payload 访问器族 30+ getter（fabric_config:140/runtime_context:166/settings_payload:188/models_payload:193/telemetry_payload:241/capability_plan:411/tools_config:415…）；HTTP 头校验与展开（validate_http_header:41/expand_http_headers:95）；Relay 关联元数据（relay_request_context:282/relay_correlation_metadata:307）；**ambient relay 插件拒绝链**（ambient_relay_plugin_config_paths:317/reject_ambient_relay_plugin_config:355/reject_inherited_relay_plugin_config:369）——发现环境里残留的外部 relay 插件配置即拒绝，防遥测被劫持。
- **health.py（177 行）**："Authenticated loopback transport for adapter health probes"（:8）——HMAC 认证的回环 Unix socket 健康探活，`unobserved_health`（:21-29）返回标准 unknown 结果（outcome/reason_code/activity/source/observed_at 五字段，对应契约 schema 的 required null 语义）。
- **instructions.py（40 行）**：`system_instruction`（:19-40）校验 harness 是否支持所配置的 instruction mode（replace/append），不支持即抛带 metadata 的 LifecycleError——错误里带上 field/mode/supported_modes 三元组。
- **relay_gateway.py（230）/relay_hooks.py（99）/relay_artifacts.py（109）/relay_version.py（14）**：NeMo Relay 遥测中继的网关、钩子、工件就绪与版本检查。
- **openai_chat.py（163）**：OpenAI chat 形态的统一处理。

### TS common（四模块+barrel）

- **lifecycle.ts（448 行）**：AdapterRuntime 接口（lifecycle.ts:34-40，与 Python Protocol 同构，多一个可选 check(level)）；HostState（:54-61）带 generation 计数；compileSchema(:116) 用 ajv 编译契约 schema 做**运行时校验**（validate:132）；dispatch(:261) 分发三操作；`serve()`(:379) 主循环。与 Python 版同构到错误码命名（callAdapter:218 包裹调用错误）。
- **acp-runner.ts（464 行）**：ACP（Agent Client Protocol）会话引擎。AcpSessionOptions(:43-58) 收 command/args/cwd/env/mcpServers/configOptions/permissionResolver/三级超时（startupTimeoutMs/promptTimeoutMs/shutdownTimeoutMs）；SpawnedAcpSession(:211) 实现 AcpSession(:66)；startAcpSession(:316) 是公共入口；terminateProcessTree(:120) 负责进程树清理；validateMcpCapabilities(:182) 与 validateConfigOption(:201) 在握手后校验 agent 声明的能力与配置项。**权限模型收窄为 "allow_once" | "deny"**（:27）——ACP 的授权由 permissionResolver(:29) 回调决定，适配器宿主永不自动放行。
- **model-endpoint.ts（65 行）**：`insecureHttpModelHosts`(:19) 用严格 HOSTNAME 正则（:9-10，53 字符上限、禁 scheme/port/path/通配符）白名单化"允许明文 HTTP 的模型主机"。
- **index.ts（31 行）**：barrel 注释钉版"exposes the lifecycle host, adapter-facing runtime interfaces, and normalized lifecycle errors **without exposing the host's internal protocol machinery**"——协议机器内部件不导出。

### 依赖对照

TS common 的 package.json 依赖四件：@agentclientprotocol/sdk 1.5.1、ajv 8.20（schema 校验）、zod 4.6.6、nemo-fabric-adapter-contract 0.6.0（契约包）+ engines node>=20.18.3。Python 侧 common 依赖 nemo-fabric-adapter-contract 的 dataclass，无 ajv 等价物（校验靠 codec + 类型系统）。

## 三、外部连接

- **上游契约**：两侧都 import nemo-fabric-adapter-contract（AgentRunRequest/AgentRunResult/AdapterCheckResult/RuntimeContext）——第 3 篇的双语言实现正是被本层消费。
- **宿主对端**：fabric-core 的 LocalAdapterHost（runtime.rs:868 起）spawn 适配器进程，在 stdin 上写 NDJSON 生命周期请求——serve 主循环读的就是它。
- **下游适配器**：Python 10 个（openclaw/codex/claude/deepagents/hermes/mini-swe-agent/nooa/openhands/remote-agent + common 自身）与 TS 9 个（opencode/cline/droid/kilo/kiro/pi/qwen/strands）全部以 common 为基座；ACP runner 被 strands 等复用（见第 11 步 tour）。
- **健康对端**：health.py 的 HMAC 回环传输对接 fabric-core check.rs 的 HMAC 健康码验证。

## 四、数据流

适配器进程启动 → lifecycle.serve 进入主循环 → 宿主发 start 载荷 → config_loader（AgentConfig.from_mapping）解码校验 → AdapterRuntime.start 初始化 → 宿主发 invoke → _typed_invocation（lifecycle.py:692）构造类型化请求 → runtime.invoke 执行 harness 交互（Python 适配器或经 AcpRunner spawn agent 进程）→ AgentRunResult → _encode_response（:758，sort_keys=True 稳定序列化）→ 单行 JSON 回宿主 → stop 后 EOF 退出。invoke 期间宿主可并发发健康探测——health.py 的回环 socket 独立于 stdin/stdout 协议。OpenAI 流式变体 invoke_openai_stream 经 _OpenAIStreamWriter 走 127.0.0.1 回连通道。

## 五、设计决策

1. **协议循环只写一次**：19 个适配器的最大公约数抽象成 serve+AdapterRuntime，新增 harness 适配器的全部协议成本归零——这是"适配器矩阵能长到 19 个"的结构性原因。
2. **stdout 是协议专线**：redirect_stdout（lifecycle.py:877）把整个 Python 进程的 stdout 重定向到 stderr，连 SDK 后台任务的输出都被兜住——否则一条意外 print 就毁掉 NDJSON 流。
3. **两侧错误码对齐**：LifecycleError/AdapterCallError、failure_response 的形态在 Python 与 TS 中同名同义——宿主侧无需关心适配器语言。
4. **ACP 权限只许 allow_once**：粒度设计（acp-runner.ts:27）让每次工具调用都重新决策，不产生"永久放行"状态——评测场景的可审计优先。
5. **明文 HTTP 白名单严格化**：model-endpoint.ts 的正则拒绝一切非纯 hostname 形态，宁可苛刻不可宽松——安全边界向紧。
6. **内部机器不导出**（index.ts:6-8）：适配器作者只能用公开接口，common 内部重构不破坏下游。

## 六、新人提示

- 写新 Python 适配器的最小骨架：实现 AdapterRuntime 三方法 + 一行 `lifecycle.serve(MyRuntime, config_loader=AgentConfig.from_mapping)`（照 hermes/adapter.py:46）。
- 调试时想 print，放心打——stdout 已被重定向到 stderr，宿主日志能看到；但别依赖顺序，stderr 与协议不同步。
- invoke 失败会置 state.failed（lifecycle.py:820-824），后续 invoke 直接被 _active_runtime 拒绝——失败后宿主必须 stop/start 重建，这是刻意的失败语义。
- TS 适配器接 ACP agent 先读 acp-runner.md（package.json files 字段把它打进 npm 包）；三种超时（startup/prompt/shutdown）默认值要按目标 harness 的启动速度调。
- utils.py 的 payload 访问器族是读取 start 载荷的唯一推荐途径——手写 payload["..."] 链会绕过默认值与类型收敛，踩坑率极高。
