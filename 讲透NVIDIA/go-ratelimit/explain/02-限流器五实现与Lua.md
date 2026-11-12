# 02 · 限流器五实现与 Lua 原子窗口（pkg/limiter）

## 角色定位

`pkg/limiter` 是判定核心：五种限流器实现同一个契约，数据面是 Redis ZSET 滑动窗口。**原子性全部押在一把 Lua 脚本上**——这是不用分布式锁实现精确滑动窗口的关键设计。

## 内部结构

- **契约**：`RateLimiter` 接口（pkg/limiter/limiter_interface.go:14）——`AllowRequest`（:16）/`RecordBytes`（:19）+配置读写+用量查询；中间件只依赖此接口。
- **redis.go（118 行）**：`RedisLimiter`（redis.go:25）持 `lua *redis.Script`（:32，NewRedisLimiter :38，键前缀 :47）；`Allow`（:50）一次 `lua.Run`（:53）原子完成窗口修剪+计数+判定；脚本 `slidingLua`（redis.go:75 起）以 Redis TIME 为时钟、ZSET 存请求时间戳；`GetLimit`（:67）查限值。
- **memory.go**：对照实现——`MemoryLimiter`（memory.go:28）`sync.RWMutex`（:35）+map 客户端表+周期清理（cleanupInterval :41/:75，cleanup :80，节流 :87-88）。
- **dual_limiter.go**：双维独立键空间——`requestKey` 前缀 `":req:"`、`byteKey` 前缀 `":byte:"`（dual_limiter.go:57-58），两键同传 Lua（:75/:92）；NewDualLimiter（:38）。
- **dynamic_limiter.go**：`DynamicLimiter`（dynamic_limiter.go:31）每判定先查客户端覆盖配置（GetClientConfig :153-154）再落窗口——热路径含 Redis 配置读取，有缓存优化空间。
- **resilient_limiter.go**：装饰器——`ResilientLimiter`（resilient_limiter.go:30）组合 memoryLimiter（:32/:62），`checkRedisAvailability`（:88-89）周期探测（:119），故障走内存回退（:128），恢复回切。
- **配置源**：`ConfigManager`（pkg/config/manager.go:36）客户端配置持久化 Redis，`ExtractClientID`（:150-152）提取键。

## 外部连接

上游：门面 Service 持 DynamicLimiter（pkg/ratelimit/ratelimit.go:70 一族）；中间件 `DualRateLimitMiddleware`（pkg/middleware/dual_ratelimit.go:26）消费 dual。mock 生态：生产包 `RedisMockClient`（mock_redis.go:31，SimulateFailure :307-308，MockLuaScript :314-315）被 redis_test.go 消费（redis_test.go:32/:112）；测试包 `MockRedisClient`（mock_test.go:32）三维故障注入 SetShouldFail/SetFailAfter/SetLatency（mock_test.go:49/:55/:61）被 dynamic_limiter_test.go:34 消费。

## 数据流

redis 判定：请求→键→`Allow` 组装 KEYS[1]=限流键、ARGV=[window_ms, limit]（redis.go:53）→Lua 内 ZREMRANGEBYSCORE 修剪过期、ZCARD 计数、ZADD 记录、判限→返回 [allowed, remaining, reset]。dual：请求与字节各进各的 ZSET（dual_limiter.go:57-58 两个键），互不挤占配额。resilient：探测失败→内存窗口接管（:128）→探测恢复→回切 Redis（期间内存窗口的计数不回灌，接受毛刺换可用性）。

## 设计决策

1. **Lua 原子窗口**：修剪+计数+判定三步若拆成多条命令，并发下会超发；单脚本原子执行免锁。
2. **Redis TIME 而非应用时钟**（redis.go:75）：多实例时钟漂移会把窗口算歪，用 Redis 单调时钟统一。
3. **memory 是一等公民不是玩具**：它同时是测试对照与 resilient 的回退目标（resilient_limiter.go:62）——语义必须与 redis 版一致。
4. **装饰器做弹性**：ResilientLimiter 不改 DynamicLimiter 一行代码（resilient_limiter.go:30 组合而非继承），降级逻辑可独立测试。

## 新人提示

加新限流维度先实现 RateLimiter 接口（limiter_interface.go:14）再配一个中间件包装。**热路径优化第一站是 dynamic_limiter.go:153 的 GetClientConfig**（每请求一次 Redis 读）。测试新实现直接 import 生产包 mock（mock_redis.go:46 NewRedisMockClient），别再手搓桩。观察 resilient 降级要看 checkRedisAvailability 的探测周期与回退窗口计数语义（内存接管期间数据不回灌）。
