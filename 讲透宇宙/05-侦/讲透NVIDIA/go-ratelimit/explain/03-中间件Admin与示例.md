# 03 · 中间件装配、Admin API 与服务接线（pkg/middleware / pkg/api / cmd / examples）

## 角色定位

中间件层把限流器接入 net/http（判定→响应头/429/字节计数），Admin/Config API 提供运行时运维面，cmd/server 与 examples 示范完整接线。三层合起来是"**库怎么用才是对的**"的范本。

## 内部结构

- **中间件入口**：`RateLimitMiddleware`（pkg/middleware/ratelimit.go:29，吃具体类型 `*limiter.RedisLimiter`）；泛化入口 `DynamicRateLimitMiddleware(dl limiter.RateLimiter)`（dynamic_ratelimit.go:27）+Logger 变体（:32）。
- **响应语义**：判定错误 500（dynamic_ratelimit.go:43）、超限 429（:81）、正常写 `RateLimit-Request-Limit/Remaining/Reset` 与 `RateLimit-Bytes-Limit` 头（:58-74）；响应已发出后超限只能记日志（:111 注释）。
- **bytecounter**：`http.Flusher`（bytecounter.go:52-54）与 `http.Hijacker`（:59-61）透传——**不透传则 SSE/WebSocket 全坏**；middleware_test.go:801-810/:824 有 mockFlusher/mockHijacker 专门验证（全文件 1009 行）。
- **选择性限流**：`PathMatcher`（selective_ratelimit.go:27）+MatchPathPrefix/Exact/Regex/Any/None（:48/:55/:62/:70/:82），SelectiveRateLimitMiddleware（:30）。
- **请求感知**：`RequestSizeFunc`（request_aware_bytecounter.go:23）+`RequestAwareByteCounterWriter`（:26，Write :43）按请求体积预登记配额。
- **Admin API**：`AdminHandler`（pkg/api/admin_handler.go:49，构造 :55，473 行）状态查询/租户配置/批量操作/legacy 兼容+AdminKey 认证（:35/:80/:91）+Prometheus 指标；**局部遮蔽注意**：`h.config.RedisAddress`（:108-113）是字段访问，包级引用只有 `config.ClientConfig`（:195）。
- **Config 端点**：`ConfigHandler`（config_handler.go:33）查询/设置/重置，路由 `/admin/config/{clientID}`（:46-47，解析 :60-62）。

## 外部连接

上游消费：cmd/server/main.go 接线链 `NewDynamicLimiter`（cmd/server/main.go:64）→`NewConfigHandler`（:98）→`ratelimit.NewFromLimiter`（:122）→选择性限流重路径（MatchAny cmd/server/main.go:125-127）；**注意 cmd/server 接的是 DynamicLimiter 不是 ResilientLimiter**——弹性接线范本是 examples/dynamic_resilient/main.go:81。键函数与匹配器来自门面 re-export（pkg/ratelimit/ratelimit.go:154-155/210-211）。测试：api_test.go 790 行覆盖路由+认证；test-admin-api.sh 九条 curl 冒烟。

## 数据流

请求路径：中间件→键提取→AllowRequest→（放行）handler→bytecounter 包装写响应并累计字节→RecordBytes 登记→响应头带余量。（拒绝）直接 429+Retry 头。运维路径：PUT /admin/config/{clientID}→ConfigHandler→ConfigManager 写 Redis（manager.go:36）→下一次判定 DynamicLimiter 即读到新配置（dynamic_limiter.go:153）——**热更新闭环不重启**。

## 设计决策

1. **Flusher/Hijacker 透传是 bytecounter 的存在理由**：朴素包装 ResponseWriter 会悄悄破坏流式升级，接口探测透传（bytecounter.go:52-61）是标准解。
2. **两个中间件入口分工**：具体类型入口（pkg/middleware/ratelimit.go:29）简单场景零配置；接口入口（dynamic_ratelimit.go:27）可换 limiter 实现——选错入口会失去可替换性。
3. **AdminKey 可选认证**：内网部署零配置（admin_handler.go:80 开关），公网必须设钥（:91 比较）。
4. **示例即文档**：examples 四例按场景递进（header 五场景 examples/header_based_limiting/main.go:51/:188 多租户收官），Makefile run-* 六目标（Makefile:108-133）一键对应。

## 新人提示

接 SSE/WS 服务先用 middleware_test.go:801 的 mockFlusher 自测包装层；Admin API 上生产前设 AdminKey 并把 /admin 路径排除出限流范围（用 selective_ratelimit.go:82 的 MatchNone）。抄接线顺序：examples/dynamic_resilient/main.go:81（带弹性）优于 cmd/server（纯动态）。改响应头名要同步文档与监控面板（dynamic_ratelimit.go:58-74 是唯一写入点）。
