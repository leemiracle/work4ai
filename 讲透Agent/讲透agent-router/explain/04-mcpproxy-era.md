# 04 · MCP 会话代理与双纪元：mcpproxy 把多工具后端拼成一个端点

## 一、角色定位

`internal/mcpproxy`（21 文件）是第二条产品线（MCP 网关）的数据面：代理 MCP 会话（JSON-RPC over Streamable HTTP）到多后端——客户端开一个会话，网关对每个后端各开一个，工具列表合并、调用按名路由。控制面把 MCPRoute 编译成共享 Service + 回环 listener（07-12 篇）。另一主角是 **era.go 的双纪元**：2026-07-28 新规格（SEP-2575）把协议劈成 legacy（有握手与会话）与 modern（无状态，元数据进 `_meta` 与镜像头）。**先判纪元再读状态码**是排障前置。

## 二、内部结构

**era.go（331 行）**：`legacyOnlyMethods`（era.go:56）列新规格删除的方法（initialize/ping 等 8 个）；`modernOnlyMethods`（:70）为 modern 独有。`detectClientEra`（:198）只看 `Mcp-Protocol-Version` 头是否等于 `2026-07-28`（:206）。`validateLegacyRequest`（:219）很松，只拒 modern 方法（:222）。`validateModernRequest`（:238）五连检：不许发 JSON-RPC response（:245）；`Mcp-Method` 头必填且须与 body 一致（:257，SEP-2243）；legacy 方法 404（:271）；`Mcp-Session-Id` 出现即 400（:279）；`_meta` protocolVersion 必填且与头一致（:299），call 须带 clientCapabilities（:318）。`protocolError` 带 HTTPStatus（:87）——**modern 映射真实状态码，legacy 装进 HTTP 200 body**。

**入口（mcpproxy.go）**：`NewMCPProxy`（mcpproxy.go:68）注册 `"/"` 万能 handler（:86：路由选择在 Envoy 层完成），按方法分派 GET/POST/DELETE（:93）。POST body 上限 4MiB，env 可覆盖（:52、:58）。

**POST 主路径（handlers.go:65）**：读 body、解码 JSON-RPC（:95）后分派——**handlers.go:107 是 `// TODO: Detect era`，主分派器仍无条件走 `serveLegacyPOST`（:109）**；modern 的 `serveModernPOST`（modern.go:48，自注 Phase 1）已实现有测试但未接线——这是双纪元落地的真实状态。legacy 路径（legacy.go:189）按方法分派：initialize 建复合会话（:484）、tools/call 走 :643。

**复合会话（mcpproxy.go:194）**：initialize 并行 fan-out 到全部授权后端（`wg.Go` :232），单个失败不拖垮（:240），全失败才报错（:270）。会话 ID 是加密复合体，含 subject 与每后端会话表（:275）；恢复时校验 subject 防劫持（:320）。`mergedProtocolVersion`（:391）公式 `max(floor, min(client, min(perBackendMax)))`——诚实地板：只承诺最弱后端版本。GET 长连接由 streamNotifications + 心跳维持（session.go:195、:277）。

**授权（authorization.go）**：`compileAuthorization`（:77）预编译 CEL（cost limit 10000，:99）；`authorizeRequestWith`（:207）按 source（JWT/headers）→ target（backend/tool）→ CEL 三层匹配；**CEL 运行时错误 fail-closed 拒绝整个请求**（:248：当"条件不成立"处理会绕过 Deny）。会话创建时 `selectAuthorizedBackends`（mcpproxy.go:166）预筛后端，被拒者拿不到转发凭证（:205）。工具集变化经 `toolChangeSignaler.Signal()`（config.go:351）唤醒会话发 `list_changed`。

## 三、外部连接

- **filterapi**：LoadConfig 消费 MCPConfig，与 extproc 共用 watcher 通道。
- **internalapi**：route 名经 `MCPRouteHeader` 传入；original path 双头透传（:124）。
- **go-sdk jsonrpc/mcp**：消息与类型用官方 SDK；era.go:26 镜像其未导出的现代头常量。

## 四、数据流

legacy `tools/call`：POST → 解码 → 按头恢复会话（解密、subject 校验）→ CEL 授权 → `handleToolCallRequest`（legacy.go:643）从 `__` 前缀解出目标后端（handlers.go:178）→ 用该后端复合会话转发 → 响应原路返回，资源 URI 改写回前缀形态（handlers.go:211）。initialize 则 fan-out 建会话、合并工具列表（handlers.go:426）；modern 路径（接线后）无状态，`server/discover` 聚合后端能力（modern.go:299）。

## 五、设计决策

1. **纪元判定最小化**：只信 Protocol-Version 头（era.go:206），检测与校验分离。
2. **状态码按纪元翻转**：protocolError 携 HTTPStatus（era.go:87），两纪元语义相反。
3. **fail-closed CEL**：求值错误拒整个请求而非跳规则（authorization.go:248），防绕过 Deny。
4. **会话即加密凭据**：复合 ID 内嵌 subject+后端表，无服务端会话存储、天然水平扩展（mcpproxy.go:320）。
5. **分派器保持薄**：servePOST 只解码一次就交棒（handlers.go:58：legacy 退役时可一步删掉其分支）。

## 六、新人提示

改授权读 authorization_test.go（1098 行）；改纪元读 era_test.go。工具名前缀 `__`（handlers.go:178）。坑三处：handlers.go:107 的 TODO 说明 modern 未接线，别盲测现代客户端；legacy 错误在 200 body 里；`server/discover` 仅 modern 合法，legacy 见它会被 era.go:222 拒。
