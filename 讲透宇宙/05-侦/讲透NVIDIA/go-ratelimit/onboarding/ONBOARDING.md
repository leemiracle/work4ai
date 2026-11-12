# go-ratelimit 新人上手指南（NVIDIA HTTP 限流库）

> 基于知识图谱（243 节点 / 691 边 / 9 层 / 14 步导览，指纹 56 文件 @ commit `ff47a8b2`）与源码逐条核实编写。
> 所有 `文件:行号` 锚点均从仓库源码验证（仓库根 `/usr-data/data2/repos/agent-repos/NVIDIA/go-ratelimit`，go.mod:1 `module github.com/NVIDIA/go-ratelimit`，go.mod:3 `go 1.24`，依赖 go-redis/logrus/testify）。

---

## 1. 项目定位与架构总览

go-ratelimit 是 NVIDIA 出品的 **HTTP 限流库**：以 Redis 为数据面的滑动窗口限流，支持按请求次数与响应字节双维度、客户端级配置热更新、Redis 故障弹性降级，并附送 Admin/Config 运维 API。设计基线看两份文档：`DESIGN.md`（292 行、51 个标题节点，覆盖滑动窗口选型/Redis 数据面/配置分层/弹性降级依据，11 章）与 `README.md`（499 行，五种限流器对比与快速上手）。

五种限流器实现（全部实现统一契约，见第 3 节）：**redis**（基础滑动窗口）/ **memory**（无 Redis 对照实现）/ **dual**（请求+字节双维）/ **dynamic**（客户端级覆盖配置）/ **resilient**（Redis 故障自动回退内存）。图谱 9 层自底向上：门面 → 键工具 → 中间件 → 限流器核心 → 配置日志 → Admin API → 示例 → 文档 → 构建。

一句话心智模型：**限流维度由键决定（pkg/utils），判定逻辑在限流器（pkg/limiter），接入 HTTP 靠中间件（pkg/middleware），公共入口只有一个门面（pkg/ratelimit），运维面在 pkg/api**。

## 2. 公共门面与"一行委托"re-export 陷阱

`pkg/ratelimit/ratelimit.go`（279 行）是库的**唯一公共入口**：`Service`（pkg/ratelimit/ratelimit.go:70）聚合 DynamicLimiter 与中间件装配——`Middleware()`（pkg/ratelimit/ratelimit.go:140）、`MiddlewareWithRequestSize()`（:145-146）、`SelectiveMiddleware(matcher)`（:150-151）、`RegisterConfigAPI(mux)`（:180）、`SetClientConfig/ResetClientConfig`（:190/:200）配置热更新直达。

**最大阅读陷阱：KeyFunc 族与 PathMatcher 族全是 re-export**。`KeyByIP` 在门面只有一行委托（pkg/ratelimit/ratelimit.go:210-211 `return utils.KeyByIP(r)`），`MatchPathPrefix` 等同理（pkg/ratelimit/ratelimit.go:154-155 起）——真实实现分别在 `pkg/utils/request.go:25` 与 `pkg/middleware/selective_ratelimit.go:48`。**在门面看到任何函数都要跳到实现包去读语义**。`DefaultOptions`（pkg/ratelimit/ratelimit.go:58）兜底 `KeyFunc: utils.KeyByIP`（:65），未传 logger 时回退 NoOpLogger（:108）。

根 `main.go` 是 28 行占位（打印使用说明后 os.Exit，:22-24）——它提示的 "cmd/examples" 目录实际叫 `examples/`（文档漂移，见 README 勘误）；真实接线示例在 `cmd/server/` 与 `examples/` 四例。

## 3. 统一契约、Lua 原子窗口与内存对照

**契约**：`pkg/limiter/limiter_interface.go:14` 的 `RateLimiter` 接口是全库第一张图——`AllowRequest`（limiter_interface.go:16）判定请求、`RecordBytes`（:19）登记字节，外加配置读写与用量查询；五种实现与全部中间件只依赖它。

**Redis 滑动窗口（redis.go，118 行）**：数据面基石。`RedisLimiter`（redis.go:25）持有 `lua *redis.Script`（:32，构造于 NewRedisLimiter :38，键加前缀 :47）；`Allow`（:50）执行 `slidingLua` 脚本（:75 起，注释明言用 Redis TIME 做时钟、ZSET 存时间戳），**窗口修剪+计数+判定三步在一个 Lua 脚本内原子完成**（lua.Run :53）——这是不用分布式锁的关键。`GetLimit`（:67）提供窗口限值查询。

**内存对照（memory.go）**：无 Redis 环境与测试的兜底实现——`MemoryLimiter`（memory.go:28）用 `sync.RWMutex`（:35）保护 map 客户端表，后台周期清理 goroutine（cleanupInterval 默认 1 分钟，:41/:75，清理函数 :80，节流 :87-88），同样支持请求+字节双计数与客户端配置覆盖。它同时是 resilient 限流器故障回退的目标实现（见第 4 节）。

## 4. 双维·动态·弹性：三种高阶限流器与配置热更新

- **双维（dual_limiter.go）**：请求次数与响应字节**两个独立滑动窗口**——键空间分离：`requestKey` 加 `":req:"` 前缀、`byteKey` 加 `":byte:"`（dual_limiter.go:57-58），`AllowRequest` 与 `RecordBytes` 各走各的键（:75/:92 两处把两个键同时传给 Lua）。构造入口 NewDualLimiter（:38），中间件侧 DualRateLimitMiddleware（pkg/middleware/dual_ratelimit.go:26）。
- **动态（dynamic_limiter.go）**：核心判定管线——`DynamicLimiter`（dynamic_limiter.go:31）每次判定先查客户端覆盖配置（`GetClientConfig` :153-154）再落 Redis 窗口；默认配置来自全局 Config。**注意配置读取在热路径上，有缓存优化空间**（NOTES batch-3 钉版）。
- **弹性（resilient_limiter.go）**：装饰器模式包装 DynamicLimiter——`ResilientLimiter`（resilient_limiter.go:30）组合 `memoryLimiter`（:32，构造 :62）；`checkRedisAvailability`（:88-89）周期探测（调用点 :119），失败自动回退内存限流（:128 走 memoryLimiter.AllowRequest）、恢复后回切，配置管理透传。配套专题文档 `docs/RESILIENT_RATE_LIMITING.md` 讲清回退机制与监控要点。
- **配置持久化（pkg/config）**：`ConfigManager`（pkg/config/manager.go:36）把客户端级限流配置写入 Redis（Get/Set/Delete/SetDefault），`ExtractClientID`（manager.go:150-152）提取配置键——是 dynamic/resilient 热更新的数据源；`LoadConfig`（pkg/config/config.go:37）从环境变量构造全局 Config。日志面：`pkg/logger/logger.go` 的 logrus 封装与 CustomLogger 适配（:94），中间件侧另有自己的 Logger 接口（pkg/middleware/logger.go:19）+NoOpLogger（:25）解耦日志库。

## 5. HTTP 中间件装配族与 SSE 保通

`pkg/middleware` 把限流器接入 net/http：

- **包装器**：`RateLimitMiddleware`（pkg/middleware/ratelimit.go:29）把**具体类型** `*limiter.RedisLimiter` 包为中间件（注意不是接口，见 README 勘误 6）；泛化入口是 `DynamicRateLimitMiddleware(dl limiter.RateLimiter)`（dynamic_ratelimit.go:27）与带 Logger 变体（:32）。
- **判定与响应**：中间件装配"键提取→判定→限流响应"链：判定错误回 500（dynamic_ratelimit.go:43），超限回 429（:81），正常路径写 `RateLimit-Request-Limit/Remaining/Reset`、`RateLimit-Bytes-Limit` 响应头（:58-74）；响应已发出后才知超限时只能记日志不能再改状态码（:111 注释）。
- **bytecounter（本层最精妙处）**：包装 ResponseWriter 统计响应字节——**必须透传 `http.Flusher`（bytecounter.go:52-54）与 `http.Hijacker`（:59-61）**，否则 SSE 流式推送和 WebSocket 升级会被包装层破坏。middleware_test.go 1009 行专门有 mockFlusher/mockHijacker 验证（:801-810/:824）。
- **选择性限流**：`PathMatcher func(path string) bool`（selective_ratelimit.go:27）+五件套 `MatchPathPrefix/Exact/Regex/Any/None`（:48/:55/:62/:70/:82），`SelectiveRateLimitMiddleware`（:30）决定哪些路径参与。
- **请求感知变体**：`RequestSizeFunc`（request_aware_bytecounter.go:23）按请求体积预登记配额，`RequestAwareByteCounterWriter`（:26，Write :43）+dynamic_ratelimit_request_aware.go 组成"按请求大小计费"的通道。

## 6. 键提取与防注入清洗器

限流维度=键的构造层（pkg/utils）：

- **request.go**：`KeyByIP`（request.go:25）优先取 `X-Forwarded-For`（:66-67，注释警告只信自家代理设置的值），退回 `RemoteAddr`（:71-73 net.SplitHostPort）；KeyByClientID/KeyByClientIDAndRoute 提供租户/路由分桶维度。
- **header_keys.go（防注入设计）**：`KeyByHeader`（header_keys.go:63）/`KeyByHeaderWithOptions`（:70，sanitizer 应用点 :85）/`KeyByHeaderWithFallback`（:157 回退链）构成键函数族；三个清洗器组成 sanitizer 管线——**AlphanumericSanitizer**（:179 去非字母数字）、**UUIDSanitizer**（:190-191 校验归一 UUID）、**MaxLengthSanitizer**（:209-213 截断）——**防 HTTP 头值直接进 Redis 键**（分隔符注入会伪造他人键空间、超长值会打爆内存）。391 行专题文档 `docs/HEADER_BASED_RATE_LIMITING.md`（37 节）覆盖回退链与多租户实践。

## 7. 测试基建：生产包 mock 与三维故障注入

本库最有意思的工程决策在 `pkg/limiter`：

- **mock_redis.go（411 行）编译进生产包**：文件名不含 `_test` 故进生产构建——`RedisMockClient`（mock_redis.go:31）带完整命令桩（String/ZSet/Expire/Time，zsets map :34，zsetEntry 结构 :40 维护有序集合语义，构造器 :46），**下游测试可直接 import**；支持 Lua 脚本桩 `MockLuaScript`（:314-315，NewMockLuaScript :324 按 allowCount 放行）与 `SimulateFailure`（:307-308）故障注入。redis_test.go 正是拿它离线验证 Lua 判定路径（redis_test.go:32/:112）。
- **mock_test.go（717 行）是第二套 mock**：`MockRedisClient`（mock_test.go:32）专供测试编译，提供**三维故障注入模型**——`SetShouldFail`（:49 恒失败）/`SetFailAfter`（:55 N 次后失败）/`SetLatency`（:61 注入延迟），支撑 resilient 限流器的降级测试；dynamic_limiter_test.go 消费它（:34）。**两套 mock 不是重复建设：一套进生产包给下游复用，一套留在测试包做行为注入**。
- 对照测试：limiter_test.go 的 TestHelpers 支撑跨实现的并发/竞态/基准对照；api_test.go 790 行覆盖 Admin 路由集成与认证；test-admin-api.sh 九条 curl 冒烟（健康检查/认证/配置读写/批量/错误路径）可直接跑。

## 8. Admin/Config 运维 API、服务接线与构建

- **Admin API（pkg/api）**：`AdminHandler`（admin_handler.go:49，构造 :55，473 行）提供限流状态查询/租户与客户端配置管理/批量操作/legacy 兼容端点，带可选 AdminKey 认证（配置 :35，开关判定 :80，密钥比较 :91）与 Prometheus 指标导出。**阅读注意局部遮蔽**：`h.config.RedisAddress` 等（:108-113）是 handler 字段访问，真正的包级引用只有 `config.ClientConfig`（:195）——`config` 既是包名又是字段名。
- **Config 端点**：`ConfigHandler`（config_handler.go:33）是运行时配置的查询/设置/重置 API，`RegisterRoutes` 挂 `/admin/config/{clientID}`（:46-47，URL 解析 :60-62），AdminKey 管理复用 SetAdminKey（:41）。
- **服务接线教材（cmd/server/main.go，147 行）**：`NewDynamicLimiter`（cmd/server/main.go:64）→`NewConfigHandler`（:98）→`ratelimit.NewFromLimiter`（:122）→中间件挂载（含 MatchAny 选择性限流重路径 :125-127）一条链。**注意它接的是 DynamicLimiter 而非 ResilientLimiter**（图谱描述有误，见 README 勘误 3）；完整弹性接线看 `examples/dynamic_resilient/main.go:81`。
- **示例四例**：dynamic_resilient（动态+弹性装配与热更新）/header_based_limiting（五场景递进：简单/带选项/多 Header/回退链/多租户，examples/header_based_limiting/main.go:51/:188）/resilient_limiter（降级行为）/simple_logger（自定义 Logger）。`SETUP_GUIDE.md` 讲 Redis 准备与环境变量。
- **构建（Makefile，164 行 22 target）**：build（:31）/test（:37）/test-cover（:41）/lint（:52）/verify 聚合（:67）标准目标；examples 构建族 build-basic/server/resilient/dynamic-resilient/dynamic-only（:78-102）；**run-* 六个一键目标中三个因目录漂移已失效**（Makefile:23 的 EXAMPLES_DIR 指向不存在的 cmd/examples，可用仅 run-server/run-resilient/run-dynamic-resilient，详见 README 勘误 5）。

**新人上手路径**：读 README+DESIGN.md 前两章 → `make run-server` 感受限流响应头与 Admin API → 精读 limiter_interface.go:14-25（契约）与 redis.go（Lua 窗口）→ 按场景选型（要热更新→dynamic；Redis 不稳→resilient；要计费→dual+bytecounter）→ 用 cmd/server/main.go 当接线模板 → 生产前用 mock_redis.go 写自己的集成测试。

---

## 附：图谱元信息

| 项 | 值 |
|---|---|
| 节点/边 | 243 / 691 |
| 分层 | 9 层（门面→键工具→中间件→限流器核心→配置日志→Admin API→示例→文档→构建） |
| 导览 | 14 步（step-01 设计基线 → step-14 服务接线·示例·构建） |
| 指纹基线 | 56 文件 @ ff47a8b2 |
| 分析时间 | 2026-11-08 14:04 |
