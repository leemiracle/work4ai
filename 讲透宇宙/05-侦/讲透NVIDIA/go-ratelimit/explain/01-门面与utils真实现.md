# 01 · 门面与 utils 真实现（pkg/ratelimit / pkg/utils / 根 main.go）

## 角色定位

`pkg/ratelimit` 是库的**唯一公共门面**——下游只 import 这一个包；`pkg/utils` 是被门面 re-export 的键构造真实现。理解这对关系是读库的第一课：**门面看到的函数大多不是实现**。

## 内部结构

- **Service 装配体**：`Service`（pkg/ratelimit/ratelimit.go:70）聚合 DynamicLimiter 与中间件装配——`Middleware()`（pkg/ratelimit/ratelimit.go:140）、`MiddlewareWithRequestSize()`（:145-146）、`SelectiveMiddleware(matcher)`（:150-151）、`RegisterConfigAPI(mux)`（:180）、`GetLimiter()`（:185）、`SetClientConfig/ResetClientConfig`（:190/:200）。
- **re-export 族**：`KeyByIP`（pkg/ratelimit/ratelimit.go:210-211）一行委托 `utils.KeyByIP`；`MatchPathPrefix` 等（pkg/ratelimit/ratelimit.go:154-155 起）委托 middleware 包——**真身在 pkg/utils/request.go:25 与 pkg/middleware/selective_ratelimit.go:48**。
- **默认值**：`DefaultOptions`（pkg/ratelimit/ratelimit.go:58）兜底 `KeyFunc: utils.KeyByIP`（:65）；options 未填 KeyFunc 时再兜一次（:85）；logger 缺省 NoOpLogger（:108）。
- **utils 键函数**：`KeyByIP`（pkg/utils/request.go:25）优先 `X-Forwarded-For`（:66-67，注释警告只信自家代理），退回 `RemoteAddr`（:71-73）；`KeyByHeader`（header_keys.go:63）/`KeyByHeaderWithOptions`（:70，sanitizer 应用 :85）/`KeyByHeaderWithFallback`（:157 回退链）。
- **清洗器管线**：AlphanumericSanitizer（header_keys.go:179）/UUIDSanitizer（:190-191）/MaxLengthSanitizer（:209-213）。
- **根 main.go**：28 行占位（根 main.go:22-24 打印指引后退出）。

## 外部连接

门面向上服务 cmd/server（cmd/server/main.go:122 `ratelimit.NewFromLimiter`）与全部 examples；向下把实现细节永久隔离在 utils/middleware/limiter 三包。日志解耦：中间件自有 Logger 接口（pkg/middleware/logger.go:19）+NoOpLogger（:25），库不强制日志实现。

## 数据流

一次中间件调用：请求进来→门面传入的 KeyFunc（默认 utils.KeyByIP，pkg/ratelimit/ratelimit.go:65）提取键→限流器判定→结果写响应头/429。Header 键路径：`KeyByHeader("X-Client-ID")` 取值→sanitizer 清洗（防分隔符/长度注入）→拼 Redis 键→窗口判定。多租户：KeyByClientID 或 Header 回退链（header_keys.go:157）落到不同键空间。

## 设计决策

1. **门面+re-export 而非直接暴露实现包**：公共 API 面最小化、下游 import 单点；代价是读代码必须跨包跳转——语义全在实现包。
2. **sanitizer 管线**：HTTP 头是攻击者可控输入，直接进 Redis 键会注入键空间（分隔符伪造他人配额）——清洗是安全边界而非锦上添花。
3. **DefaultOptions 兜底链**（pkg/ratelimit/ratelimit.go:58/:65/:85）：三处兜底保证零配置可用，代价是排查"为什么按 IP 限流"要看三行。
4. **根 main.go 保留占位**：go install 语义下库仓带 main 包易误导，占位打印指引是折中（其文案 "cmd/examples" 实为 examples/，文档漂移）。

## 新人提示

**在 ratelimit.go 看到的函数一律跳实现包读语义**；改键逻辑改 utils，改路径匹配改 middleware，门面只加委托。选清洗器：租户 ID 是 UUID 就用 UUIDSanitizer（header_keys.go:190），自由字符串用 Alphanumeric+MaxLength 组合。X-Forwarded-For 只在自有代理后可信（request.go:66 注释），裸暴露场景直接用 RemoteAddr 维度。
