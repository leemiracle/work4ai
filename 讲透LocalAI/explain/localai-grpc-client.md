# localai-grpc-client — 1410 行 gRPC 客户端与 streamCleanup 流生命周期

> 源码：`pkg/grpc/client.go`（1410 行，37 个类型/方法）
> 定位：控制器侧访问"远程后端进程"的唯一通道，backend.proto 的 Go 客户端门面

## 角色定位

在 18 层架构中位于"后端通信层"，与 `embed.go`（进程内桥接）互为对偶：本文件管"跨进程"，embed 管"进程内"。模型加载器选中一个后端地址后，拿到的就是 `*Client`——上层（core/services 的推理调用方）完全不感知它是远程还是本地。它同时是 81 个 `backend/go/*` 后端进程的**库依赖**（图谱：importers 含全部 backend/go main.go），因为 Go 后端测试与工具同样需要客户端实现。存在理由：把 gRPC 的连接管理、并发语义（串行/并行后端）、看门狗记账、流生命周期统一封装，让 52 个 RPC 的调用点零重复代码。

## 内部结构

- `Client`（30-38 行）：`address`/`inFlight` 计数/`parallel` 开关/`token` + `sync.Mutex`（保护计数）+ `opMutex`（非并行模式的操作互斥）+ `wd WatchDog`。
- `bearerToken`（20-28）：`credentials.PerRPCCredentials` 实现，给每次调用注入 `Authorization: Bearer`，`RequireTransportSecurity()=false` 允许明文传输。
- `dial`（72-84）：`grpc.NewClient` + insecure + **50MB 双向消息上限**（音频/图像二进制的硬需求）。
- `setBusy`/`IsBusy`/`wdMark`（44-68）：busy 从布尔改成**计数**——注释明说：并行请求完成乱序，布尔会让第一个完成者把还在跑的同伴误报为 idle。
- **unary 方法群**（86-840，约 30 个）：Predict/Embeddings/LoadModel/GenerateImage/TTS/Transcription/Rerank/Stores×4/Detect/Depth/Face×2/Voice×3/…全部同构。
- **回调式流方法**（169-214、301-344 等）：PredictStream/TTSStream/AudioTranscriptionStream/FineTuneProgress/QuantizationProgress。
- **句柄式双向流**（841-1185）：ForwardClient、AudioTransformStreamClient（+`streamCleanup`/`LifecycleStream`）、AudioTranscriptionLiveClient、AudioToAudioStreamClient 四套。
- 尾部（1187-1410）：FineTune/Quantization 的 unary 与进度流、`Free`、`ModelMetadata`。

## 外部连接

上游：core/services 的推理管线、model loader、健康检查。下游：`pkg/grpc/proto` 生成代码 + google.golang.org/grpc。`Backend` 接口（本包定义，embed.go 以 `var _ Backend` 实现）让 Client 与 embedBackend 可互换——这是"进程内 vs 远程"对上层透明的机制核心。WatchDog 接口由 core 侧注入，用于 busy/idle 看门狗的请求级记账。

## 数据流

**unary 模板**（以 Predict 为例，134-150 行）：①`!parallel` 则 `opMutex.Lock`（串行后端逐调用互斥）→ ②`setBusy(true)`+defer false → ③`defer wdMark()()` 给看门狗记账 → ④`dial()` 新建连接 → ⑤`NewBackendClient(conn)` → ⑥RPC → ⑦defer `conn.Close()`。**每次调用独立建连/断连**——后端进程生命周期与连接解耦，进程崩溃重建后客户端零状态。

**回调式流**（PredictStream，169-214）：`for { select ctx.Done → return; stream.Recv() → EOF break / err → 判 ctx 取消则返回 ctx.Err() / f(reply) }`——先查 ctx 再 Recv，避免取消后阻塞在网络上。

**streamCleanup 生命周期**（933-986 行，本文件灵魂）：

- 语义：回调的存活期绑定**流的接收侧**。`CloseSend` 刻意不算终止——注释（933-935）解释：双工后端在客户端停止发送后仍会继续产出尾部响应。
- `newStreamCleanup`：登记初始回调并起 goroutine 监听 `ctx.Done` 触发 `finish`——客户端断连也能兜底释放连接。
- `add`：未终结则入队；已终结（`done=true`）则**立即同步执行**——晚到的清理者不丢责任。
- `finish`：置 done、清空 callbacks、`close(doneCh)`（唤醒监听 goroutine 防泄漏）、快照后逐个执行——**恰好一次**语义。

三个使用变体：`forwardClient.Recv` 出错时 `once.Do(closer)`（871-877）；`audioTransformStreamClient` 把 streamCleanup 暴露成公共 `AddCleanup` API（918-921 接口），Recv 终态触发 finish；`audioTranscriptionLiveClient`（1054-1080）用 closeOnce+release，其注释记录了真实 bug 教训：在 CloseSend 里关连接会让等待中的 Recv 死于 "connection is closing"，**每轮都丢最终转写结果**——修复即"连接释放只挂在 Recv 终态"。

`Forward`（879-914）：打开流后不能像 unary 那样 defer 清理——锁、busy 计数、看门狗的释放全部打包进 `cleanup` 闭包，由 closer 在 Recv 终态统一触发；dial 失败与开流失败两条路径各自显式 cleanup，保证 `setBusy(false)` 必然执行。

## 设计决策

1. **每调用一连接**：牺牲连接复用换取崩溃隔离与代码极简——后端进程随时可能被 LRU 驱逐杀掉，长连接反而是负担。
2. **并发语义内建**：`parallel` 一位开关切换"全局互斥"与"自由并发"，busy 用计数而非布尔，看门狗 hook 统一记账——正确的并发报告不依赖调用方自觉。
3. **三种流生命周期封装**（once.Do / streamCleanup+AddCleanup / closeOnce）应对不同所有权需求，共同不变式：**资源释放绑定 Recv 终态而非 CloseSend**。
4. **900 行同构样板是刻意的**：新增 RPC 照抄模板即可，审查时 diff 结构一致、风险低；抽象成反射/泛型反而增加心智负担。
5. 公共接口（ForwardClient 等）**不泄漏 pb 类型**（926-931 注释），让上层测试可 mock。

## 新人提示

- 切入点：30-84（结构+bearing+dial）→ 169-214（PredictStream 模板）→ 933-1042（streamCleanup 全节）；中间 600 行样板可跳。
- 易混淆点一：`opMutex` 只在 `!parallel` 时锁——串行后端（老 llama.cpp 单槽）与并行后端（vLLM 等）走同一段代码的不同分支。
- 易混淆点二：回调式流（`f func(reply)`）与句柄式流（返回接口）是两种 API 形态：前者简单但无法中途 Send，后者为实时音频/HTTP 转发保留双工。
- 排查"连接泄漏/计数不归零"问题时，盯住三件事：cleanup 是否所有错误路径都调用、Recv 是否必然读到终态、ctx 取消是否被 streamCleanup 的 goroutine 兜住。
