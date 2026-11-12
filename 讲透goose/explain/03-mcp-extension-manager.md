# 03 · extension_manager.rs + mcp_client.rs：MCP 扩展机制——goose 的工具供给系统

> 源码基线：`/usr-data/data2/repos/aaif-projects/repos/goose`（crates/goose/src/agents/，extension_manager.rs 共 2932 行，mcp_client.rs 共 1156 行）。所有行号锚均经 grep/sed 从源码逐一核实。

## 一、角色定位

goose 是一个 AI agent 框架，而 agent 的"手"全部来自 MCP（Model Context Protocol）扩展：shell 命令、文件编辑、代码分析、技能发现……这些工具不是硬编码在 agent 里的，而是由**扩展子系统**统一供给。这个子系统的中枢就是 `ExtensionManager`。

在架构上，`Agent`（crates/goose/src/agents/agent.rs:231）持有唯一一个 `extension_manager: Arc<ExtensionManager>` 字段。模型推理产生的工具调用请求，最终都会流经 agent.rs:916 的 `Agent::dispatch_tool_call` 总入口，再在 agent.rs:1031-1038 转发给 `extension_manager.dispatch_tool_call`。也就是说，extension_manager 是 agent 与"所有工具"之间唯一的桥——图谱（.understand-anything/knowledge-graph.json）中 `file:crates/goose/src/agents/agent.rs --imports--> file:crates/goose/src/agents/extension_manager.rs` 这条边，正是这个唯一持有关系的体现；图谱还记录了 acp/server.rs、goose-cli/src/commands/configure.rs、goose-server/src/routes/agent.rs 等九个文件的 imports 入边，说明 CLI、桌面后端、ACP 三种宿主形态都汇聚到这一个管理器。

extension_manager.rs:139-147 定义了管理器本体：`extensions: Mutex<HashMap<String, Extension>>` 是扩展注册表（名字 → 运行态扩展），`tools_cache` + `tools_cache_version`（AtomicU64）构成工具列表缓存，`context: PlatformExtensionContext` 为进程内平台扩展提供会话管理器等直连能力。图谱对它的摘要是"扩展管理器：客户端注册表 + 平台扩展上下文 + 工具缓存"，与源码三件套完全对应。

mcp_client.rs 则提供抽象面与具体实现：`McpClientTrait`（mcp_client.rs:69）定义"一个扩展客户端能做什么"（列工具/调工具/读资源/取提示词/订阅通知），`McpClient`（mcp_client.rs:434）是基于 rmcp 库的真 MCP 协议客户端，`GooseClient`（mcp_client.rs:144）是实现 MCP client 侧回调（sampling/elicitation/roots）的宿主处理器。两者合起来构成"**编排**（谁提供哪个工具）+ **传输**（怎么跟 server 说话）"的分层。

值得注意的是路由的对称性：向上一侧 agent.rs:916 的入口先处理特权工具（schedule 管理工具 agent.rs:978、final_output 工具 agent.rs:998、前端工具特判 agent.rs:1024），剩下的"普通工具"才落到 extension_manager；向下一侧 extension_manager 再按工具名前缀路由到具体扩展。两级 dispatch 各管一层特例，这正是本机制的骨架。

## 二、内部结构

### 2.1 注册表与扩展运行态

`Extension` 结构（extension_manager.rs:71-82）是单个扩展的运行态：持有原始 `config`、`resolved_config`（密钥解析后的快照）、`client: McpClientBox`（即 `Arc<dyn McpClientTrait>`，见 :55 类型别名）、`server_info`（握手获得的 server 能力）以及 `_temp_dir`（inline_python 扩展的临时目录保活句柄）。resolved_config 的用途有源码注释明证（:73-77）：在客户端创建时捕获密钥替换后的配置快照，用于检测**密钥轮换**而无需每次重读 keyring，且"只在内存持有——从不序列化到磁盘"。

`add_extension`（extension_manager.rs:807）是装载入口，核心是一个覆盖全部扩展形态的巨型 match（:839-1045）：

- **Sse**：直接拒绝，报"SSE is unsupported, migrate to streamable_http"（:841-844）——SSE 形态仅为旧配置文件兼容保留（extension.rs:154-155 注释）。
- **StreamableHttp**（:845-876）：先 `merge_environments` 合并明文 envs 与 keyring 密钥（:856），再对 URI/headers/socket 做 `$VAR` 与 `${VAR}` 变量替换（:857-862，替换函数在 :479-503，特意在原始输入上扫描以避免递归展开，见 :490-491 注释），然后进 `create_streamable_http_client`（:558）。该函数有一个精心设计的 OAuth 路径：若凭据库已有 token，先**主动刷新**直连（:625-647，注释明言"避免每次新会话都走 401 → 浏览器重认证的循环"）；否则裸连，仅当命中 `should_attempt_oauth_fallback`（:390，识别 AuthRequired 与裸 HTTP 401）才发起 `oauth_flow` 浏览器认证（:659-675）。Unix domain socket 变体在 :683-741（`socket` 字段语义见 extension.rs:238-243 注释：HTTP over UDS，`uri` 仅作 Host 头）。
- **Builtin / Platform**（:877-952）：按 `name_to_key` 归一化名字后先查 `PLATFORM_EXTENSIONS` 静态表（:886）。命中则走**进程内工厂**：`(def.client_factory)(context)`（:897），context 里注入了指向管理器自身的 Weak 引用与当前会话（:888-896）。未命中则按内置 MCP server 处理：`get_builtin_extension` 查不到就报 Unknown extension（:900-904）；有 Docker 容器时改为 `docker exec -i <id> goose mcp <name>`（:913-933）；否则走**进程内双工管道**：两对 `tokio::io::duplex(65536)`（:935-936），一端交给 `extension_fn(server_read, server_write)` 起 server，另一端交给 `McpClient::connect`（:940-948）。
- **Stdio**（:953-1006）：外部子进程形态。合并环境变量后额外注入 `AGENT_SESSION_ID`（:965-967）；先过恶意包检查 `deny_if_malicious_cmd_args`（:970，OSV 漏洞库扫描 uvx/npx 包）；有容器时包装成 `docker exec`（:972-987），否则用 `resolve_command` 在含 npm 全局路径的搜索路径中解析命令（:989 与 :182-190）。最终都进 `child_process_client`（:328-387）：`TokioChildProcess` 派生进程并 piped stderr（:353-355），单独 spawn 任务收全量 stderr（:360-364）——若初始化失败，stderr 内容会随 `ProcessExit` 错误一起返回（:380-385），这是诊断"扩展起不来"的第一手材料。
- **InlinePython**（:1007-1039）：把 `code` 写入临时目录（:1014-1017），用 `uvx --with mcp [--with dep...] python <file>` 拉起（:1019-1025）——即"一段 Python 代码就是一个扩展"，依赖由 uvx 按需安装。
- **Frontend**（:1040-1044）：此处直接报错"Frontend extensions cannot be added as server extensions"——前端扩展根本不进这个管理器（见第五节）。

连接成功后写入注册表并使工具缓存失效（:1049-1061）；若同名扩展已存在且未解析/已解析配置双双相等则直接跳过（:822-830），配置有变则按新配置重启——这套比较正是为了上面说的密钥轮换检测。

### 2.2 工具聚合与前缀

`fetch_all_tools`（:1264-1359）并发对所有扩展调 `list_tools`（`future::join_all`，:1338），每个工具做三件事：过 `is_tool_available` 白名单（:1294）；确定公开名——普通扩展加 `扩展名__工具名` 前缀（`format!("{}__{}", name, tool.name)`，:1298），一等平台扩展不加前缀（:1290，`is_unprefixed_extension` 判定在 :293-302）；把归属写进工具 meta（`TOOL_EXTENSION_META_KEY = "goose_extension"`，:221 与 :1306-1309）。最后按公开名去重，重名工具直接跳过并告警（:1340-1354）。聚合结果经 `get_all_tools_cached`（:1195-1215）缓存——带版本号的双重检查模式：填充缓存前比对 `tools_cache_version`，期间若有扩展增删（版本号在 :1259-1262 递增并清缓存）则放弃写入，避免缓存到陈旧列表。

### 2.3 调用路由：resolve_tool 与 dispatch_tool_call

`resolve_tool`（:1566-1645）是路由核心，三级策略：先在缓存工具表里精确匹配名字，归属优先读 meta（:1580-1585），无 meta 再按 `__` 前缀切（:1582-1584）；拿到归属后 `strip_prefix("{owner}__")` 还原真实工具名（:1594-1597）。若精确匹配失败，退而按 `__` 切前缀直接找扩展客户端（:1617-1629）——这条回退路径意味着即便工具列表还没聚合，只要命名合规也能路由。仍找不到则报 RESOURCE_NOT_FOUND 并附上全部可用工具名（:1631-1644），错误信息本身就能引导模型自我纠正。

`dispatch_tool_call`（:1647-1727）在路由后先做 available_tools 二次校验（:1656-1671），然后**不直接执行**而是返回 `ToolCallResult { result: Box::new(fut.boxed()), notification_stream }`（:1723-1726）：result 是装箱的 future（真正的 `client.call_tool` 在 :1695-1703 异步执行），notification_stream 来自 `client.subscribe()`（:1676）用于流式转发 server 的进度/日志通知。拆成"future + 通知流"两件套，让 agent 侧能边等结果边消费通知。

### 2.4 McpClientTrait 抽象面

mcp_client.rs:69-142 的 trait 定义了 11 个方法，其中 6 个有默认实现且默认全部返回 `TransportClosed` 错误（:94-141）——即"不实现就等于不支持"，资源/提示词能力全靠 server_info 声明（`supports_resources` 查 server capabilities，extension_manager.rs:101-106）。最精妙的是 `get_instructions`（mcp_client.rs:87-92）：默认从握手的 `get_info()` 读静态 instructions，注释明言"平台扩展可覆写以提供**动态计算的指令**（例如刚发现的 skills）"。trait 对象有两类实现：`McpClient`（协议实现，mcp_client.rs:572-736）和各平台扩展的 Client（如 DeveloperClient）。`McpClient::call_tool`（:646-672）→ `send_request_with_context`（:515-535，注释 :523-525 说明内层 mutex 只在发送期持有、等待响应在锁外，使并发调用可重叠）→ `await_response`（:537-558）：`tokio::select!` 三路竞争——响应到达 / 超时（发 CancelledNotification 并报 `ServiceError::Timeout`，:549-552）/ 取消令牌触发（同样发取消通知，:553-556）。每个请求还会把 session_id 与 working_dir 注入请求 `_meta`（`inject_session_context_into_extensions`，:740-773），让 server 侧（包括 goose 自己 `goose mcp` 起的 server）能感知会话上下文。

## 三、外部连接

**被谁调用**：① agent.rs 是主消费者——初始化时 `add_extension_inner`（agent.rs:1271）对 Frontend 形态特判走 `insert_frontend_extension`（agent.rs:1290-1292），其余全部进 `extension_manager.add_extension`（agent.rs:1296-1300）；每轮推理后 `handle_approved_and_denied_tools`（agent.rs:704）对权限审批通过的请求逐个调 dispatch（agent.rs:715），被拒的则直接回 `DECLINED_RESPONSE`（agent.rs:748-760）。② 图谱 imports 边显示 acp/server.rs、goose-cli/commands/configure.rs、goose-server/routes/agent.rs 也直接使用本模块（如 CLI 的扩展开关、桌面端的动态增删）。③ moim.rs 的 `inject_moim` 调 `collect_moim`（extension_manager.rs:1902）收集平台扩展的"模型导向信息"注入对话，且上下文窗口小于 32_000 token 的模型直接跳过（:1908-1915）以防挤占有限上下文。

**依赖谁**：① `super::extension` 模块提供 `ExtensionConfig` 七形态枚举（extension.rs:153-286）与安全防线 `Envs`——31 个禁止覆盖的环境变量黑名单（extension.rs:71-108，PATH/LD_PRELOAD/NODE_OPTIONS 等劫持向量全覆盖）。② `crate::builtin_extension`（builtin_extension.rs:5 的 `SpawnServerFn` 类型、:11-13 注册、:22-24 查询）是内置 MCP server 的全局注册表，由 **goose-cli/cli.rs:2074 与 goose-server/state.rs:39** 在启动时调 `register_builtin_extensions(goose_mcp::BUILTIN_EXTENSIONS)` 填充——这个注册表模式解耦了 goose 核心仓与 goose-mcp 仓的编译依赖。③ goose-mcp 仓的 `BUILTIN_EXTENSIONS`（goose-mcp/src/lib.rs:57-63）目前只有四个内置扩展：autovisualiser（MCP Apps UI 资源可视化）、computercontroller（桌面控制）、memory、tutorial，由 `builtin!` 宏（lib.rs:48-55）包装成"spawn 双工流即 serve"的函数。④ 权限层：PreToolUse hook 可策略性拒绝（agent.rs:934-965），PermissionManager 的审批结果决定请求进 approved 还是 denied 队列——权限系统站在 dispatch 之前。⑤ skills 机制完全寄生在扩展系统上：`crate::skills` 本身注册为平台扩展（platform_extensions/mod.rs:192-203），其 `SkillsClient::get_instructions`（skills/client.rs:224-236）每次动态扫描 `~/.agents/skills` 与项目 `.agents/skills` 目录发现技能——这正是 mcp_client.rs:87-92 注释所述"动态指令"的真实用例。⑥ 图谱 contains 边把 ExtensionManager/add_extension/dispatch_tool_call/fetch_all_tools/collect_moim 五个符号挂在文件节点下，与本文结构一一对应。

## 四、数据流：一次工具调用的完整旅程

以模型输出 `computercontroller__screenshot` 这类带前缀调用为例（无前缀的 `shell` 同理，靠 meta 归属）：

1. **审批**：权限层分类请求 → approved 队列（agent.rs:712）→ `Agent::dispatch_tool_call`（agent.rs:916）。
2. **前置钩子**：PreToolUse hook 策略检查，命中 Deny 则直接返回策略错误且错误文案明言"Do not retry"（agent.rs:948-964）。
3. **特权特判**：schedule 工具（agent.rs:978）、final_output（agent.rs:998）、前端工具（agent.rs:1024，返回"Frontend tool execution required"交宿主执行）依次短路。
4. **管理器路由**：`ExtensionManager::dispatch_tool_call`（extension_manager.rs:1647）→ `resolve_tool`（:1654 → :1566）：meta 优先、前缀回退，解析出 `extension_name="computercontroller"`、`actual_tool_name="screenshot"` 与客户端句柄。
5. **二次校验**：available_tools 白名单复查（:1656-1671），不在名单报 RESOURCE_NOT_FOUND。
6. **协议执行**：`McpClient::call_tool`（mcp_client.rs:646）构造 CallToolRequest，注入 session/working_dir meta（:740），`await_response` 三路 select（:537-558）。**超时路径**：超时秒数三级取值——扩展配置 timeout > 全局 `GOOSE_DEFAULT_EXTENSION_TIMEOUT` > `DEFAULT_EXTENSION_TIMEOUT = 300`（extension_manager.rs:63-69 与 config/extensions.rs:11），到点后向 server 发 CancelledNotification（mcp_client.rs:560-569）并返回 `ServiceError::Timeout`。**进程崩溃路径**：stdio 子进程死掉则通道关闭，`await_response` 收到错误映射为 TransportClosed（mcp_client.rs:547）。**server 端错误**：`ServiceError::McpError` 透传 ErrorData，其余包装为 INTERNAL_ERROR（extension_manager.rs:1698-1703）。
7. **安全清洗与增强**：`remove_untrusted_mcp_app_meta`（:1705，函数体 :245-269）剥掉 server 伪造的 `__goose_tool_update_meta`/`goose.mcpApp` meta；若宿主支持 MCP Apps 再由 goose 侧自主读取 UI 资源、以**受信 meta** 回插（:1707-1718 与 :271-291）——先剥后插，防伪造设计一进一出非常完整。
8. **回环**：`ToolCallResult`（result future + notification_stream，:1723-1726）回到 agent 的 `tool_stream`（agent.rs:716-723），流式通知（进度/日志）与最终结果分别汇入对话，再进入下一轮推理。

反向数据流同样存在：server 也能调用 client——`GooseClient::create_message`（mcp_client.rs:286-369）把 MCP sampling 请求转发给 goose 自己的 provider 补全（系统提示默认"You are a general-purpose AI agent called goose"，:322-325）；`create_elicitation`（:371-409）把 server 的表单征询交给全局 ActionRequiredManager 等 UI 回答，超时 300 秒（:397）；`list_roots`（:245-251）把当前工作目录作为 root 报给 server。goose 在 MCP 里同时是 client 与"被调用方"，这是它比一般 MCP 宿主多出的一层。

## 五、设计决策

**内置扩展为何进程内**。两条路径都算"内置"，但分两档。平台扩展（developer/analyze/skills/summon 等）走 `client_factory` 直造客户端对象（extension_manager.rs:897），extension.rs:204 的字段注释给出官方理由："Platform extensions that have direct access to the agent etc and run in the agent process"——它们需要会话管理器、agent 句柄这类进程内能力（PlatformExtensionContext，platform_extensions/mod.rs:210-216）。内置 MCP server（computercontroller 等）虽在同一二进制家族里，却仍走 MCP 协议：进程内 duplex 管道（:935-937）取代 socket。**推断**（无直接注释）：这样保留了协议一致性（同一套 McpClientTrait 消费方式）与"随时可外置"的自由度——developer 的历史佐证了这一点：`DEFAULT_EXTENSION: &str = "developer"`（config/extensions.rs:10）说明 developer 曾是内置 MCP 扩展的默认项，如今它已迁出 goose-mcp、成为进程内平台扩展（platform_extensions/mod.rs:151-162），而 goose-mcp 的 BUILTIN_EXTENSIONS（lib.rs:59-62）里已无 developer。

**外部扩展为何子进程隔离**。三个安全机制全部压在 stdio/inline_python 路径上：装载前 OSV 恶意包扫描（extension_manager.rs:970，且对不认识的生态系统"fail open"跳过，extension_malware_check.rs:54 注释）；31 项环境变量黑名单阻断 PATH/LD_PRELOAD 类劫持（extension.rs:71-108）；stderr 全量捕获确保崩溃可诊断（:360-385）。子进程形态还天然获得故障隔离与多语言自由（uvx 起 Python，npm 路径解析起 Node）。

**前端扩展的特殊性——勘误**。任务书提到的"FrontendChat"在本仓 **grep 零命中，不存在此符号**；按源码，前端扩展的真实机制是：`ExtensionConfig::Frontend`（extension.rs:250-266）携带前端自报的 `tools: Vec<Tool>` 与 instructions；add_extension 明确拒收（extension_manager.rs:1040-1044）；agent.rs:1290-1292 把它转存进独立的 `frontend_extensions`/`frontend_tools` 注册表（agent.rs:233-234），由 `rebuild_frontend_derived_state` 重建（agent.rs:855-858）；执行时 agent 故意返回"Frontend tool execution required"错误（agent.rs:1024-1029），把执行权让给桌面 UI 宿主。本质是"工具元数据进模型上下文、执行体留在前端"的反转控制。

**其余可圈可点的取舍**：工具前缀 `扩展__工具` 防全局重名，但 analyze/developer/summon/skills/code_execution 五个一等扩展 `unprefixed_tools: true`（platform_extensions/mod.rs:40、109、137、158、199）——高频核心工具免前缀降低模型出错率，归属信息藏进 meta（:1306-1309）而非名字。缓存版本号 + 双重检查（:1195-1215）用 AtomicU64 避免了"聚合途中扩展被增删导致缓存脏数据"。超时统一在 `await_response` 单点实施（mcp_client.rs:537-558）且**先发协议级取消再报错**，把清理责任交给 server。

## 六、新人提示

**新增内置 MCP 扩展最小三步**：① 在 crates/goose-mcp/src/ 写新模块，实现 rmcp 的 `ServerHandler`（照抄 autovisualiser/computercontroller 的结构）；② 在 goose-mcp/src/lib.rs:59-62 的 `BUILTIN_EXTENSIONS` 里加一行 `builtin!(myext, MyServer)`；③ 用户配置 `type: builtin, name: myext`（默认配置形态见 extension.rs:288-298 的 `Default`，其 timeout 默认走 300 秒）。

**新增平台扩展**：在 crates/goose/src/agents/platform_extensions/ 新建模块，实现 `McpClientTrait`（至少 list_tools/call_tool，参考 developer/mod.rs:176-230 的直调式实现——shell/write/edit 直接调本地工具对象），定义 `EXTENSION_NAME`，再到 mod.rs:28 的 `PLATFORM_EXTENSIONS` 表 `map.insert`（顺带决定 `unprefixed_tools`/`hidden`/`default_enabled` 三个开关，字段语义见 mod.rs:257-260 注释）。

**接入外部 MCP server**：在 `~/.config/goose/config.yaml` 的 `extensions:` 段写 `type: stdio`（cmd+args+envs+env_keys）或 `type: streamable_http`（uri+headers，密钥用 `env_keys` 引用 keyring 并在 header 里写 `$KEY` 占位，替换逻辑见 extension.rs:434-498 的 `resolve`）。注意 SSE 类型会直接报错（extension_manager.rs:841）。

**调试入口**：① 扩展起不来先看 `ProcessExit` 错误里的 stderr（extension_manager.rs:382）；② `RUST_LOG=debug` 可见 dispatch 明细（:1689-1694 的 debug 日志含工具名/会话/工作目录）与"Failed to list tools"告警（:1285）；③ 工具莫名不可见时查三处：available_tools 白名单（extension.rs:406-432：空表=全放行）、重名去重日志（:1346-1350）、工具缓存版本（改配置后管理器自动失效，:1259-1262）。

**坑**：① 工具名以 `__` 为命名空间分隔符，自定义 server 的工具名里**不要**再含 `__`，否则前缀回退路由（:1617-1629）可能解析错归属；② unprefixed 一等扩展的工具没有前缀，路由完全依赖 meta（:1580），自己拼工具名测试时容易踩空；③ timeout 字段单位是**秒**（`Duration::from_secs`，:368/:606）；④ 平台扩展拿到的 `PlatformExtensionContext.extension_manager` 是 Weak 引手（mod.rs:211-212），用前需 upgrade，防循环引用；⑤ 前端扩展永远进不了 ExtensionManager，调试"前端工具不执行"要去 agent.rs:1024 的特判与宿主 UI 侧找，而不是扩展管理器。

---

### 附：与任务书的差异声明

1. 任务书称扩展配置在 `agents/extension/` 目录——实际是单文件 `agents/extension.rs`（932 行），PLATFORM_EXTENSIONS 等定义在 `agents/platform_extensions/mod.rs`。
2. 任务书称 goose-mcp 内置扩展有"developer 桌面控制"——实际 developer 已迁移为**进程内平台扩展**（platform_extensions/developer/），goose-mcp 当前的内置四件套是 autovisualiser/computercontroller/memory/tutorial（goose-mcp/src/lib.rs:59-62）；"桌面控制"对应的是 computercontroller。
3. 任务书提到"spawn_anderve"——本仓无此符号，进程内 spawn 的实际函数是 `spawn_and_serve`（goose-mcp/src/lib.rs:31）与 `(def.client_factory)(context)`（extension_manager.rs:897），按源码为准。
4. "FrontendChat"不存在，前端扩展机制见第五节勘误段。
