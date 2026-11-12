# 01 · extproc server 主循环：一条 gRPC 双向流里的两级 filter

## 一、角色定位

`internal/extproc` 是 Agent Router（原 Envoy AI Gateway，Go 实现）的数据面心脏：Envoy 不改一行代码，靠 ext_proc 协议把每个请求的头/体/响应送到本包做解析、方言翻译与凭证注入。`cmd/extproc/main.go:20` 只管信号与优雅退出（SIGTERM 后睡 15 秒再退，main.go:39）；装配在 `cmd/extproc/mainlib/main.go:217` 的 `Main`：建 Server、逐端点 `Register`（:329）、起配置 watcher（:364）。

## 二、内部结构

**Server（server.go:59）**：`processorFactories` 按 path 登记工厂，`routerProcessorsPerReqID` 供 upstream 侧认领。`LoadConfig`（server.go:85）把 CRD 编译产物变成运行时配置，:90 注释直言 `This is racey, but we don't care.`——整指针替换，容忍新旧瞬时并存。`processorForPath``processorForPath`（:104）按 `:path` 精确匹配；upstream 侧改读 `originalPathHeader`（:125）——重试时 `:path` 已是后端路径。

**Process 主循环（server.go:132）**：每条流先落兜底 `passThroughProcessor`（processor.go:43 空转发，覆盖"更早 filter 已直接应答、无 RequestHeaders 阶段"的流）。收到 RequestHeaders（每请求一次，:180）时：`:184` 用 `req.GetAttributes() != nil` 判定 **isUpstreamFilter——有无 stream attributes 是判别两级 filter 的唯一信号**；upstream 侧从 `internalReqIDHeader`（:129）取 ID，缺失直接 Internal（:190）；router 侧生成 `x-request-id + UUID`（:197）防撞。upstream 侧当场 `setBackend`（:380）：从 attributes 解析 backendName（:411）/routeName（:434）并认领 router 处理器（:399）；router 侧登记进 map（:233），defer 清理（:152）。`processMsg`（:252）四路分派到 Processor 四方法，并在 router 侧响应里追加内部请求 ID 头（:271）——upstream 侧 ID 的下发通道。

**Processor 契约（processor.go:25）**：请求头/体、响应头/体四阶段 + `SetBackend`（processor.go:34，仅 upstream filter 调用）。`NewFactory`（processor_impl.go:59）按 isUpstreamFilter 产出两角色。`/v1/models` 不打后端：`NewModelsProcessor`（models_processor.go:41）本地合成清单直接回 200；Anthropic 兼容版在 :96。debug 日志对 authorization 等四头一律 `[REDACTED]`，`isSensitiveHeader`（server.go:487）另拦 `x-aigw-` 前缀与 SigV4 后缀（:482）。

## 三、外部连接

- **filterapi**：LoadConfig 消费 Config，`StartConfigBundleWatcher`（filterapi/watcher.go:38）轮询 Secret 分片驱动热更新。
- **backendauth**：SetBackend 后持有 `backend.Handler`（processor_impl.go:759），请求头阶段 `h.Do` 注入凭证（:430）。
- **translator**：SetBackend 里 `GetTranslator` 按后端方言取翻译器（processor_impl.go:768）；端点不支持属用户可见错误，存下回 422 而非炸流（:770）。
- **tracing**：router 侧开 span（:321），upstream 侧记 provider 与 TTFT/ITL（:812）。

## 四、数据流

流式请求全路径：router filter 阶段收 RequestHeaders（无 attributes）→ 建 routerProcessor → `ProcessRequestBody`（processor_impl.go:236）：解析模型名与 stream、写 `x-ai-eg-model` 头（:289）、存原始 body 供重放、回 ClearRouteCache（模型头会改选路）。Envoy 选出集群进入 upstream filter（新流，带 attributes）→ setBackend 认领 → `ProcessRequestHeaders`（:351）：`translator.RequestBody` 产出新头新体（:375），`onRetry()`（:341）时带原始体重放；`CONTINUE_AND_REPLACE`（:477）一次交回 Envoy，故 upstream 的 ProcessRequestBody 直接 panic "BUG"（:487）。响应沿 ProcessResponseHeaders（:491，流式且 200 才切 STREAMED）→ ProcessResponseBody 逐块回译（:542，gzip 解压 :713）；本地应答被 `localReplyEmitted` 短路（:546）。

## 五、设计决策

1. **一条流两种角色**：router 与 upstream 共用同一 gRPC 服务，判别靠 attributes（server.go:184），接续靠内部请求 ID（:129：避免两级 filter 各自生成 ID 的竞态）。切忌假设"一条流=一个请求"。
2. **响应挂在 router 名下**：upstreamProcessor 只管请求侧，响应委托父处理器（processor_impl.go:173，注释自嘲 "hack and dirty workaround"）——省去响应侧重建翻译状态。
3. **失败按 ID 兜底**：ID 缺失、认领失败一律 Internal（server.go:190、:401）。
4. **防伪造**：upstream-host 头先删再从可信 xDS 元数据回填（server.go:444），防伪造值驱动 SigV4 签名。

## 六、新人提示

加端点从 `Register` 表入手（mainlib/main.go:329）；改行为进 processor_impl.go 两个泛型实现。测试：`internal/extproc/server_test.go`、`processor_impl_test.go`、`tests/data-plane`。两个必踩坑：upstream 侧断点打在 ProcessRequestHeaders 而非 ProcessRequestBody（后者是 panic 路径）；"请求没到后端"先查 server.go:411 的 backendName 解析。
