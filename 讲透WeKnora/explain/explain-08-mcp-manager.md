# explain-08 · mcp/manager.go — MCP 服务管理器（工具生态核心）

> **文件**：`internal/mcp/manager.go`（327 行）
> **所属层**：外部集成层 · internal/mcp 包（导览第 9 步）
> **一句话定位**：MCP 客户端连接的进程级缓存与生命周期管理器——连接去重（singleflight）、按服务配置版本失效、OAuth 按用户身份分键、定期清扫死连接。

## 1. 角色定位

MCP 让 Agent 能调用任意外部工具服务。每次调用新建连接要付握手+初始化往返；无脑长连则配置更新后仍用旧连接。`MCPManager` 解决这层"连接经济学"：**同一服务全进程共享一条连接，配置变了自动重连，OAuth 每用户一条连接，挂了定期回收**，是 mcp_tool 与 mcp_service 共同的连接底座。

## 2. 内部结构

- **结构体**（L16-33）：三张"账"——`clients`（键→连接）、`connecting`（pending）、`oauthRepo`，加 RWMutex 与管理器 ctx；L25：**无关服务器的连接不得持锁做 I/O**。
- **包装与构造**（L35-70）：`managedMCPClient` 的 Disconnect 先 cancel 生命 ctx（L41）；`NewMCPManager` 起后台 ctx 与清扫 goroutine。
- **缓存键**（L75-80）：非 OAuth=服务 ID；OAuth=`服务ID+"\x00"+用户身份`——**每身份一条自己的连接**。
- **核心 GetOrCreateClient**（L88-148）：L89-100 三道门（ctx 取消/服务未启用/**stdio 因安全被禁用**）；L102 OAuth 须从 ctx 解析出合法 principal；L114 持锁段——命中且存活且版本匹配（比对 UpdatedAt）直接返回，过期断开删除；同 key 进行中的复用 pending；否则登记并异步建连，ctx 派生自**管理器**而非请求（L135，SSE 长连不随请求而死）；解锁后等 done。
- **connectClient 与握手**（L150-209）：建连→Initialize（默认 30s、封顶 60s）；L162 竞态——被 CloseClient 作废则成功也视为取消，失败断连。
- **关闭与运维**（L212-327）：`CloseClient`（L223）匹配裸 ID 与 `ID+"\x00"` 前缀——一次关掉 OAuth **所有**用户连接；清扫每 5 分钟剔死连接；ListActiveServices 供观测。

## 3. 外部连接

import 仅 logger、types、interfaces。管理同包 client.go:25 的 MCPClient 接口（Initialize/ListTools/CallTool/IsConnected；传输分发在 client.go:192）。调用方：mcp_tool.go:711（执行工具）、mcp_oauth.go:99、mcp_service.go:469（同步目录）。container.go:192 注册为**进程级单例**；oauth_manager.go 管授权、security.go 管 SSRF。

## 4. 数据流

租户配了 OAuth 的 GitHub MCP，两用户先后让 Agent"查 issue"：A 首次触发 → cacheKey `svc\x00userA` 未命中，登记 pending 异步建连 → initialize → CallTool 返回。B 键不同，建**自己的**连接（token 隔离）。管理员改 URL → UpdatedAt 变 → 下次调用断旧连重连。清扫把僵尸连接移出缓存，下次调用自然重建。

## 5. 设计决策

① pending 表（L128）防并发各自建连——Agent 并行工具调用下是常态；② 连接挂管理器 ctx 而非请求 ctx（L135）：连接主人是管理器，等待方可放弃，长连不随请求死；③ 用 UpdatedAt 当版本号零成本，代价是同秒两次配置变更漏失效；④ 锁内只操作 map、建连在锁外，慢服务器不拖全进程。批评点：`GetClient`（L212）按裸 ID 查表，OAuth 服务永远查不到，属遗留接口，判断连接状态应用 ListActiveServices。

## 6. 新人提示

① stdio 被硬禁用（L98）是刻意安全决策——容器内起子进程风险大，扩传输先过安全评审；② 排查"调不到"按链路：Enabled→principal→握手超时→IsConnected；③ `CloseClient` 波及**所有用户**连接，注意影响面；④ 测试看 manager_startup_test.go；⑤ 搭配 DeepWiki《11.4 MCP Server Integration》Part 1 与《5.5 MCP Tool Integration》。
