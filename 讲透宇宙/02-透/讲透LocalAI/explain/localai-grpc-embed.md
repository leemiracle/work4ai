# localai-grpc-embed — 进程内桥接与 12 个流适配类

> 源码：`pkg/grpc/embed.go`（876 行，17 个类型）
> 定位：把"进程内 Go 模型"伪装成 gRPC 后端，与远程 `Client` 完全同构

## 角色定位

18 层架构中的"进程内后端适配层"。LocalAI 的标准形态是"控制器进程 + 独立后端进程"（IPC 走 gRPC），但纯 Go 实现的模型（如 cloud-proxy 转发后端、测试 mock、内嵌轻量模型）没必要为一个进程间调用付序列化与进程管理成本——`embedBackend` 让它们**直接在控制器进程内**实现 `Backend` 接口。文件顶部 `var _ Backend = new(embedBackend)`（13 行）与成串的 `var _ pb.Backend_*Server`（14、341-346、637、675、713、787 行）断言了它的全部契约：既是 client.go 对偶的 Backend 门面，又把 gRPC 的 server-stream 接口在进程内"仿真"出来。上层模型加载器拿到 `embedBackend` 还是 `*Client`，调用方式完全一致——**传输形态的切换对业务层零感知**。

## 内部结构

三大块：

1. **`embedBackend` 门面**（16-339 行）：持有 `s *server`（进程内 AIModel 的宿主），53 个方法几乎全部一行转发 `return e.s.XXX(ctx, in)`。仅两处特殊：`HealthCheck` 恒真（24-26 行——进程内活着就是健康，无进程可探）；`IsBusy` 直查 `e.s.llm.Busy()`。
2. **单向下行流适配器**（751-785 等四处）：`embedBackendServerStream{ctx, fn}`、`embedBackendAudioTranscriptionStream`、`embedBackendFineTuneProgressStream`、`embedBackendQuantizationProgressStream`——结构完全一样，`Send(x)` 直接调回调 `fn(x)`，SetHeader/SendHeader/SetTrailer 全是 no-op。服务于"服务端流"RPC（PredictStream/TTSStream/两个 Progress/转写 Stream）：这类流客户端只收不发，回调即足够。
3. **双向流适配器**（184-286 + 348-635 + 787-876 行）：四对 server/client 镜像类，对应 `AudioTransformStream`/`AudioTranscriptionLive`/`AudioToAudioStream`/`Forward` 四个 bidi RPC——共 8 个类，加上 4 个单向适配器，即用户所称"12 个流适配类"。

## 外部连接

依赖 `pkg/grpc/proto`（消息类型与生成接口）与 `server`（同包进程内实现，持有 AIModel）。被 81 个 backend/go/* 进程引用——它们把 embed 的 server 部分当库用（后端进程本身就内嵌这套 server 逻辑）。对上，`embedBackend` 实现 client.go 定义的 `Backend` 接口与 `ForwardClient`/`AudioTransformStreamClient` 等公共流接口（341-346、787-788 行的接口断言），保证模型加载器可无缝替换。

## 数据流

**unary 路径**：调用方 → `embedBackend.Predict(ctx, in)` → `e.s.Predict(ctx, in)` → 进程内模型 → 同步返回 `*pb.Reply`。无网络、无序列化，`grpc.CallOption` 参数被静默忽略（签名保留只为接口对齐）。

**单向流路径**（40-46 行 PredictStream）：构造 `embedBackendServerStream{ctx, fn}` → `e.s.PredictStream(in, bs)`——server 实现每产出一帧调 `bs.Send(reply)` → 直接命中 `fn(reply)`。回调链路即"流"，零缓冲零拷贝。

**双向流路径**（以 AudioTransformStream 为例，184-212 行）——本文件的教科书段：

1. 建 `reqs`/`resps` 两个 buffered channel（cap 4；Forward/AudioToAudio 用 8）+ `srvDone chan error,1`；
2. 构造 server 侧 facade（实现 `pb.Backend_AudioTransformStreamServer`：Send 写 resps、Recv 读 reqs、reqs 关闭即 io.EOF）；
3. `go func() { err := e.s.AudioTransformStream(server); close(resps); srvDone <- err }()`——模型实现在独立 goroutine 里跑真实 server 逻辑；
4. 返回 client 侧镜像 facade：Send 写 reqs、Recv 读 resps、`CloseSend` 幂等（closeOnce 标志）后 `close(reqs)`——server 的 Recv 随即收到 io.EOF。

Recv 的收尾协议是精髓（415-435 行）：resps 关闭 → `cleanup.finish()`（复用 client.go 的 streamCleanup，ctx 取消有 goroutine 兜底）→ 从 srvDone 取 server 终态错误，有错返错、无错返 io.EOF。**顺序细节**：AudioTranscriptionLive 版（225-232 行）刻意**先写 srvDone 再 close(resps)**，注释解释——Recv 被 close 唤醒后必须能立刻读到错误，"ready-ack 契约"靠首个 Recv 把 Unimplemented 暴露给调用方；AudioToAudio 版（604-619 行）更进一步：Recv 在 resps 关闭后**阻塞等** srvDone（带 ctx 兜底），注释直言"不要竞速跑过真实错误"。三个版本对同一协议的微调，是并发正确性的活教材。

## 设计决策

1. **接口镜像而非通道直连**：不用"调用方直接拿 channel"的捷径，而是完整实现 gRPC 生成的 server/client 接口——代价是 12 个样板类，收益是进程内后端与远程后端的**行为完全同构**（含 CloseSend 半关闭、EOF 语义、终态错误传递），上层代码与测试一次编写两处可用。
2. **no-op 元数据方法**：SetHeader/SendHeader/SetTrailer/RecvMsg 全部空实现——proto 生成接口的庞杂面被"进程内用不到"一语裁掉，但保留签名以 satisfy interface。
3. **channel 容量刻意小**（4/8）：背压交给 Go channel 天然语义，避免快生产者堆积内存。
4. **复用 client.go 的 streamCleanup**：进程内流同样要处理 ctx 取消，两套传输共享一套生命周期组件——`newStreamCleanup(ctx, nil)`（210 行）只借它的"ctx Done 兜底 finish"能力。

## 新人提示

- 切入点：先读 13-46（门面+单向流），再读 184-212（AudioTransformStream 双向流最小样本），最后横向对比三个 Recv 收尾（415/513/604 行）体会协议微调。
- 易混淆点一：`embedBackendServerStream` 是**单向下行**（PredictStream 用），没有 Recv；`embedBackendAudioTransformStream` 是**双向**（有 Recv）——名字相近、接口面不同。
- 易混淆点二：本文件的 "embed" 是 in-process（进程内嵌）之意，与 Go embed 资源嵌入无关。
- 易混淆点三：`srvDone` 在 goroutine 里 `close(resps)` 与 `srvDone <- err` 的先后顺序在不同流里不同——这是刻意为之（见三处注释），改动前先读懂对应 bug 场景，别"统一重构"。
