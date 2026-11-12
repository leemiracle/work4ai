# 09 MCP 工具生态

> 对应导览 S11。代表文件：`jiuwenswarm/server/runtime/mcp/registry.py`（1644 行）、`state_store.py`、`call_timeout_patch.py`、`jiuwenswarm/server/runtime/opencode_zen.py`。

## 一、角色定位

mcp/ 子系统是工具接入的统一协议面：把 marketplace 打包的 MCP server（remote/stdio/cli 三形态）、用户自定义 MCP、凭据管理、连接生命周期全部收进 `mcp.*` RPC（jiuwenswarm/server/dispatch.py:179-189 登记 MCP_LIST/SHOW/INSTALL/CONNECT/WAIT_AUTH/CANCEL_CONNECT/DISCONNECT/REGISTER_CUSTOM/SAVE_CREDENTIALS 等十余个方法）。registry.py 是核心注册表——读内置包清单与 Hub 包、合并 state.json 与 config.yaml；marketplace.py 走 SkillHub 目录与安装生命周期。同层的 opencode_zen.py 则解决"零配置免费模型"：启动时实拉 Opencode Zen 的 free 模型目录驻内存，与 MCP 工具生态共同构成开箱即用能力面。

## 二、内部结构

**registry.py** 按包目录驱动：`_package_roots` 返回内置与 Hub 两个包根（mcp/registry.py:146-148），`resolve_package` 读 `McpPackageManifest`（mcp/registry.py:150-156），`_detect_integration_type` 从包目录推断 remote-mcp/stdio-mcp/cli 三形态（mcp/registry.py:203）。`list_marketplace_mcps(mcp_filter="builtin")` 汇总市场清单（mcp/registry.py:457），`_build_summary/_build_detail` 组装展示字段并做 `_mask_mcp_spec` 脱敏（mcp/registry.py:298,327,374）。连接状态机：`connect_mcp` 按 integration_type 分派——A/B 形态 upsert state.json，C 形态跑 CliDriver 安装+版本+auth 步骤链，authUrlDomain 步骤返回 `auth_required` 哨兵让 handler 展示 URL 后经 `complete_cli_auth` 续跑（mcp/registry.py:789-806）；`cancel_connect/was_connect_cancelled/clear_connect_cancel` 管取消标记，新连接清除旧标记支持"取消后重试"（mcp/registry.py:746-784，mcp/registry.py:814-816）。自定义 MCP 走 `register_custom_mcp`：无包落盘、直接写 state.json、拒绝与内置目录同名（connect_mcp 按目录存在性分派，内置会遮蔽自定义，mcp/registry.py:1466-1485），"http" 被归一化为 streamable-http 防 "Unsupported MCP client type"（mcp/registry.py:1491-1497）。

**state_store.py** 管 `<workspace>/mcp/state.json`：connect/disconnect 改文件，`get_mcp_servers` 与 config.yaml 手写的 `mcp.servers` 合并成上层唯一清单（state_store.py:4-7）。凭据安全是硬规则：**token 永不落此文件，只存 `${VAR}` 占位符**，真值在 `mcp/credentials/<name>.json`、构 config 时经 CredentialStore 解析（state_store.py:35-38）。credential.py 把复杂度归因为**凭据获取策略而非传输**：none（免费直连）/token（静态 token 注入 env/headers/url 占位）/cli_oauth（CLI 二进制自管 OAuth）三类（credential.py:3-10）。apps.py 支持 MCP Apps——工具经 `_meta.ui.resourceUri` 声明 `ui://` 交互 UI，前端沙箱 iframe 渲染、postMessage 回传（apps.py:2-6）。

## 三、外部连接

上游：`mcp.*` RPC 由 dispatch.py 查表进 handler；`mcp_references.py` 提供 Runtime MCP 引用的只读传输中立校验——名字正则 `[A-Za-z0-9][A-Za-z0-9_.-]*` 锚定（mcp_references.py:8），`McpReferenceStatus` 三态 READY/NOT_READY/MISSING（mcp_references.py:12-18）。marketplace 侧 `asset_mcp_publish_converter.py` 把授权自定义配置转成**可移植无凭据源**：不连接、不启进程、不查凭据、不拷本地文件，只复制显式 runtime 白名单、丢弃连接/账号状态（asset_mcp_publish_converter.py:3-7）——资产以 MCP 形式发布到 Hub 的前置转换。超时补丁的注入点在 `interface_deep.py:1855`（`apply_mcp_call_timeout_patch()`，import 于 623 行）。opencode_zen.py 的消费方全在 AgentServer 进程：ConfigAdapter 把免费模型追加进 `models.list`、`_build_model_cache` 逐条建 Model、cron 工具与 Gateway 读同一缓存（opencode_zen.py:18-25）。

## 四、数据流

安装一个市场 MCP：`mcp.install {name}` → resolve_package 校验 → connect_mcp 分派 → remote/stdio 直接 upsert state.json（state 字段先写 "connecting" 而非 "connected"——handler 才翻终态，前端显示"连接中"、崩溃重启不静默丢连接，mcp/registry.py:817-827）→ cli 形态跑 CliDriver 安装，需要授权时返回 auth_required，用户完成 OAuth 后 complete_cli_auth 收尾并安装捆绑 skills（mcp/registry.py:807-812）。会话加载：chat.send 的 `mcp` 字段决定本次会话载哪些 server；TUI 的全局默认集另由 `list_tui_enabled_mcps` 提供——**enabled 字段跨渠道分裂**：state.json 的 `enabled` 是"TUI/全局默认开关"，web 渠道完全忽略它（按 chat.send 的 mcp 字段加载），所以 enabled=False 的 web 连接 MCP 照常可用（state_store.py:8-9,27,203-209）。免费模型流：AgentServer 启动 → 拉 Zen 目录（`-free` 后缀+常免 big-pickle）→ 内存缓存 → chat 选模型时按 `ZEN_CLIENT_HEADERS` 发请求。

## 五、设计决策

①**anyio/asyncio 取消语义冲突（补丁钉版）**：`MCPTool.invoke` 调 `call_tool` 无 timeout，MCP SDK 的 SSE 读默认 `sse_read_timeout` 300s——远端进程被杀后调用悬挂数分钟，表现为 TUI 永久转圈+agent 反复重试（call_timeout_patch.py:3-14）。修法必须用 `anyio.fail_after`（cancel scope）而非 `asyncio.wait_for`：**wait_for 把协程跑在另一个 asyncio Task 里，与 anyio task group 的 cancel-scope/Task 不变量冲突会腐化会话**，健康调用随后集体报 "Not connected"；fail_after 在当前 Task 内取消，兼容 SDK 的 scope（call_timeout_patch.py:21-28）。补丁幂等：模块级 `_PATCHED` 哨兵防重复（call_timeout_patch.py:33-34,43）。②**UA 伪装绕限流**：Zen 免费层按 UA 门槛放行——Python openai SDK 的 "openai-python/..." UA 直接 429 FreeUsageLimitError，即使带 referer 头也一样；把 UA 覆写成 "opencode"、镜像 opencode provider.ts 的 HTTP-Referer/X-Title/X-Source 三件套，SDK 请求就与第一方 opencode 客户端不可区分（opencode_zen.py:57-77，注释明确标注"verified against live Zen"）。免费判定用 models.dev 目录的 `cost.input == 0`（opencode_zen.py:79-83），config.yaml 零写入、`api_key="public"` 匿名访问（opencode_zen.py:50-51）。③**凭据与状态分居**：state.json 只存占位符+连接状态，凭据独立文件，发布转换器再抹一层。④**安装失败可回滚**：`rollback_failed_connect` 与 `_classify_install_failure` 把 CLI 安装失败归类成带 install_cmd 提示的 CliConnectError（mcp/registry.py:1018,1085）。

## 六、新人提示

- 排查 "MCP 调用永久挂起" 先读 call_timeout_patch.py 头注释——它是全仓对 anyio/asyncio 冲突最完整的一手记录；给单个 server 配超时用 `--timeout_s N`，补丁会把它 stamp 成 `_jws_call_timeout`。
- **不要用 enabled 字段判断 web 会话会不会加载某个 MCP**——那是 TUI 专属开关，跨渠道语义分裂是刻意设计。
- 自定义 MCP 起名先查内置包目录，同名会被 McpRegistryError 拒绝；transport 填 "http" 能被容忍，但归一化后是 streamable-http。
- 改 Zen 免费模型逻辑记得三条铁律：不写 config.yaml、不改 agent-core、目录拉不到就缓存为空（免费模型只在 Zen 可用时存在，opencode_zen.py:26-28,47-52）。
- registry 的 show/list 输出都要过 `_mask_mcp_spec`，新增字段忘了加掩码会把手写 headers 里的 token 泄给前端。
