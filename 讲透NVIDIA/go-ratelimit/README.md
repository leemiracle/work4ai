# 讲透 NVIDIA go-ratelimit（HTTP 限流库）

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/go-ratelimit` @ commit `ff47a8b2`（go 1.24，2026-11 快照）
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| DeepWiki 抓取 | ✅ 完成 | `deepwiki/`（INDEX + wiki 全页 + _coverage-check） |
| understand 图谱 | ✅ 完成 | 仓内 `knowledge-graph.json`：**243 节点 / 691 边 / 9 层 / 14 步导览**，validator 0 issues，fingerprints 基线 **56 文件 @ ff47a8b2** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节，7362 非空白字符，38 个 file:line 锚，全部源码核实） |
| explain 精讲 | ✅ 3/3 完成 | `explain/01..03-*.md`，六节结构、行号锚全源码核实（下表索引） |
| 勘误清单 | ✅ 7 条 | 见下文，全部经本仓源码一手核实 |

## explain 索引（3 篇）

| # | 篇目 | 主题 | 锚数（去重） |
|---|---|---|---|
| 01 | 门面与 utils 真实现 | Service 装配/re-export 陷阱/键清洗器管线 | 16 |
| 02 | 限流器五实现与 Lua | RateLimiter 契约/Lua 原子窗口/dual·dynamic·resilient | 20 |
| 03 | 中间件 Admin 与示例 | bytecounter 透传/PathMatcher 族/Admin API/接线链 | 22 |

字数口径：**不计空格字符**。三篇含锚 2187-2590，剔锚正文 1740-1969，均落 1500-2500 区间（双口径并记）。

## 14 步图谱导览速览

设计基线（README/DESIGN 51 标题）→ 门面 re-export → RateLimiter 契约 → Redis Lua 滑动窗口 → 内存对照 → 双维限流 → 动态热更新 → 弹性降级 → mock 基建 → 键提取清洗器 → 中间件装配族 → 选择性/请求感知 → Admin API → 服务接线与构建。

## 勘误清单（7 条，全部源码一手核实）

1. **门面 re-export 陷阱（读库第一坑）**：`pkg/ratelimit/ratelimit.go` 的 KeyFunc 族与 PathMatcher 族全是一行委托——`KeyByIP`（pkg/ratelimit/ratelimit.go:210-211）真身在 `pkg/utils/request.go:25`；`MatchPathPrefix`（pkg/ratelimit/ratelimit.go:154-155）真身在 `pkg/middleware/selective_ratelimit.go:48`。在门面文件里 grep 语义必然扑空。
2. **两套 mock 不是一套**：生产包 `mock_redis.go`（411 行，文件名不含 `_test` 故进生产构建）的 `RedisMockClient`（mock_redis.go:31，SimulateFailure :307-308、MockLuaScript :314-315）≠ 测试包 `mock_test.go` 的 `MockRedisClient`（mock_test.go:32，三维故障注入 SetShouldFail/SetFailAfter/SetLatency :49/:55/:61）。前者供下游与 redis_test.go（:32/:112）复用，后者专做 resilient 降级测试（dynamic_limiter_test.go:34 消费）——NOTES-DIGEST 的两条记录分属两套实现。
3. **cmd/server 接的是 DynamicLimiter 不是 ResilientLimiter**：图谱 examples 层称"cmd/server/main.go 是 Config→ResilientLimiter→中间件一条链"；实测 cmd/server/main.go:64 是 `limiter.NewDynamicLimiter`，全文件无 Resilient 引用。弹性完整接线在 `examples/dynamic_resilient/main.go:81`（`NewResilientLimiter`）。
4. **`h.config` 局部变量遮蔽**：`pkg/api/admin_handler.go:108-113` 的 `h.config.RedisAddress` 等是 handler **字段**访问（AdminConfig），真正的包级引用只有 `config.ClientConfig`（admin_handler.go:195）——`config` 同时是包名与字段名，grep `config\.` 需逐条分辨。
5. **Makefile 三个死 target（EXAMples 目录漂移）**：`Makefile:23` `EXAMPLES_DIR=cmd/examples` 与 `Makefile:28` `DYNAMIC_ONLY_DIR=examples/dynamic_only` 指向的目录**均不存在**（实际布局是 `examples/{dynamic_resilient,header_based_limiting,resilient_limiter,simple_logger}` + `cmd/server`）→ `build-basic`（Makefile:81）、`run-basic`（:108）、`run-dynamic`（:113）、`build-dynamic-only`（:105）、`run-dynamic-only`（:133）五个目标必失败，聚合目标 `examples`（:75）与 `all`（:137）连带失败；根 `main.go`:23 文案 "cmd/examples directory" 是同源漂移。可用目标仅 run-server/run-resilient/run-dynamic-resilient。
6. **`RateLimitMiddleware` 吃具体类型不吃接口**：`pkg/middleware/ratelimit.go:29` 签名是 `(rl *limiter.RedisLimiter)`——直连基础实现、不可替换；要换 dynamic/resilient 实现必须走 `DynamicRateLimitMiddleware(dl limiter.RateLimiter)`（dynamic_ratelimit.go:27）。两个入口不是简单的便捷/完整之分，是可替换性之分。
7. **bytecounter 的 Flush/Hijack 透传是生存线**：`pkg/middleware/bytecounter.go:52-54`（Flush）/`:59-61`（Hijack）若不透传，包装层会悄悄掐断 SSE 流与 WebSocket 升级——middleware_test.go:801-810/:824 的 mockFlusher/mockHijacker 专测此事。任何自定义 ResponseWriter 包装都应照抄此模式。

## 快速上手（新人 20 分钟版）

1. 读 `README.md`（499 行）五种限流器对比 + `DESIGN.md` 前两章；
2. `make run-server`（注意别用 run-basic，见勘误 5）起带 Admin API 的示例；
3. 精读 `onboarding/ONBOARDING.md` 第 3-4 节（契约与五种实现）；
4. 按场景选型：热更新→dynamic（+Admin API）；Redis 不稳→resilient；计费维度→dual+bytecounter；
5. 用 `cmd/server/main.go`（动态）或 `examples/dynamic_resilient/main.go:81`（弹性）当接线模板；
6. 下游集成测试直接 import 生产包 `NewRedisMockClient`（mock_redis.go:46）。
