# 08 · MCP 客户端：九种传输、JSON-RPC、延迟发现

> 证据：minified 源码偏移考古（传输层 chunk-qcefaeqg.js 全文级还原）[S]。
> 深报告（配置 schema 全表+SSRF 防护盘点+常量速查）：`rea-claude/reports/08-mcp.md`（42KB）。

## 1. 传输层：九种类型 [S]

| type | 实现 | 要点 |
|---|---|---|
| stdio | spawn 子进程 | NDJSON 帧；env **白名单继承**（仅 HOME/PATH/SHELL 等 6 个）；CLAUDE_PROJECT_DIR/CLAUDECODE=1 注入；stderr 缓冲 64MB 上限 |
| sse | GET SSE + POST 双通道 | **endpoint 事件同源强制**（SSRF 防线）；401→OAuth 重来 |
| http (streamable) | 单端点 POST | accept 双类型；mcp-session-id 会话头；断流带 last-event-id 重连+**消息级恢复**（replayMessageId）；403→升权重试 |
| ws | WebSocket | protocols:["mcp"] |
| sse-ide / ws-ide | IDE 变体 | 裸 fetch / IDE 授权头 |
| claudeai-proxy | 云代理 | 可**跳过 initialize 往返**（缓存投影）；capabilities 走 base64 头（≤6144B） |
| sdk | 进程内注册 | 不走网络（"SDK servers handled in print.ts"） |

协议版本 LATEST=**2025-11-25**，向后支持 5 版本。stdio 关闭序列：
stdin.end → 2s → SIGTERM → 2s → SIGKILL。

## 2. 连接编排 [S]

- 批量并发：本地 stdio 批 3（`MCP_SERVER_CONNECTION_BATCH_SIZE`）、远程批 20；
- **发现缓存**：命中 fresh/stale 不拨号，直接产 `type:"cached"` 客户端——
  **工具先上、首次调用才真连接**；stale 后台静默重拨（swr 语义）；
- 失败缓存 TTL 15min（插件 http/claudeai 4h）——死服务器不会拖慢启动；
- 超时：连接+list 30s（MCP_TIMEOUT）、握手 5s（MCP_CONNECT_TIMEOUT_MS）、
  工具空闲 stdio 30min/远程 5min。

## 3. 配置与作用域 [S]

- stdio：`{command, args, env, timeout, alwaysLoad, role:"comms"}`；
- http/sse：`{url, headers, headersHelper(命令名!), oauth{clientId,scopes...},
  tools:[{name, permission_policy: always_allow|ask|deny}], toolPermissions}`——
  **per-tool 权限策略在服务器配置里**；
- 作用域 8 个（local/project/user flag/policy…）；`.mcp.json` 上限 2MB；
- `role:"comms"`：协调者 comms 模式（工具从普通表剔除、成为唯一用户通道）。

## 4. 协议与工具发现 [S]

- JSON-RPC 2.0：initialize 握手 → capabilities 协商（tools/resources/prompts/
  roots/elicitation）→ notifications/initialized；
- list 系列分页 20 页封顶（退避 250/500/1000ms）；
- tools/call 结果含 `{content[], isError}` → 转 Claude 工具的 tool_result；
- **命名规则 `mcp__<server>__<tool>`**；prompts → 斜杠命令；
- **ToolSearch 延迟加载**：MCP 工具 schema 不进系统提示词，检索工具按需取回
  （token 预算 10%、放大 ×2.5；ENABLE_TOOL_SEARCH=0 全延迟/100 全加载）；
- MCP 资源三工具：ListMcpResources/ReadMcpResource/ReadMcpResourceDir。

## 5. 认证与防护 [S]

- 请求头认证三源互斥（headersHelper > headers > oauth）；
- OAuth 全流程（发现 metadata → PKCE → 回调端口 → 令牌刷新）；
- 防护盘点：SSE 同源强制、stdout 溢出断连（服务器往 stdout 打日志的守卫）、
  连接超时+失败缓存、env 白名单（防凭据泄漏进子进程）。
  **MCP URL 无通用内网拦截**（推测为产品决策：企业内网 MCP 合法）。

## 6. 手搓启示（→ rl-and-agents/）

1. **发现缓存+惰性连接**是 MCP 客户端最重要的 UX 决策：启动不等慢服务器，
  工具列表先上，调用时才拨号；
2. env 白名单继承——子进程默认"干净环境"，需要的变量显式传；
3. stdout 溢出守卫：一行代码防"服务器拿 stdout 当日志管道"拖死协议；
4. per-tool permission_policy 把权限粒度做到 MCP 服务器配置层——第三方工具
   的权限模型从"整服务器信任"进化到"逐工具三态"。
