# backend/go 桥接层 — llama（CGO 旧封装）与 whisper（purego 代表）：Go 后端如何包装 C/C++ 推理库

> 源文件：`backend/go/llm/llama/main.go`（23 行）+ `llama.go`（273 行）；`backend/go/whisper/main.go`（67 行）+ `gowhisper.go`（395 行）
> 知识图谱归属：Go 后端桥接层（backend/go）
> ⚠️ 路径勘误：任务原始路径 `backend/go/llama-cpp/main.go` 不存在。本版本 llama.cpp 的主力后端已是 C++ 单体 gRPC server（`backend/cpp/llama-cpp/grpc-server.cpp`，架构见 `.agents/llama-cpp-backend.md`）；`backend/go/llm/llama` 是保留的旧 CGO 封装，`backend/go/whisper` 是 purego 动态绑定模式的代表。本文按实际架构讲解 Go 桥接层的两种模式。

## 一、角色定位

`backend/go` 下每个子目录是一个**独立的可执行后端进程**：main.go 只做一件事——解析 `--addr` 后调 `grpc.StartServer(addr, &实现{})`。两个 main.go 开头同一句注释点明进程模型："this is started internally by LocalAI and a server is allocated for each model"——core 按需 spawn，每模型一个进程，崩溃隔离、卸载即退出。

两个文件代表把 C/C++ 推理库接进 gRPC 服务的两种绑定模式：

- **llama（CGO 静态绑定，legacy）**：`import github.com/go-skynet/go-llama.cpp`，编译期与 llama.cpp 绑死。它是旧封装——现在的 llama.cpp 支持全在 C++ 后端——但仍是"纯推理类 Go 后端"的最小完整模板：Load/Predict/PredictStream/Embeddings/TokenizeString 五件套。
- **whisper（purego 动态绑定，现役模式）**：`purego.Dlopen` 运行时加载 `libgowhisper`（默认 `./libgowhisper-fallback.{dylib|so}`，`WHISPER_LIBRARY` 可覆盖），12 个 C 函数用 `purego.RegisterLibFunc` 逐个注入 Go 函数变量。免 cgo 编译链，交叉编译与容器分发友好，库名运行时可换。

上游是 `pkg/grpc`（proto 协议 + `base.SingleThread` 并发模板），横向对标 `backend/cpp/llama-cpp`（C++ 直写 gRPC，无 Go 桥），下游分别是 go-llama.cpp（CGO）与 gowhisper C++ 封装层（`backend/cpp/whisper-cpp` 附近）+ whisper.cpp。

## 二、内部结构

**llama.go——选项搬运工模式**：`LLM{base.SingleThread; llama; draftModel}`（L14-19），draftModel 是投机解码的草稿模型。`Free()`（L23-33）依次释放两个模型再置 nil——VRAM 归还靠它，卸载路径必经。`Load(pb.ModelOptions)`（L34-122）是"默认值+非零覆盖"的参数映射：ropeFreqBase 默认 10000、scale 默认 1（L35-43）；NoMulMatQ/F16Memory/Embeddings/Reranking/NGPULayers/MMap/MainGPU/TensorSplit/NUMA/LowVRAM 逐项转 `llama.ModelOption`；Lora 路径与 DraftModel 路径都相对模型文件所在目录解析（L55、L107-110）；有 DraftModel 时开 `SetPerplexity(true)`（L98-101，镜像 llama.cpp speculative 示例的开关副作用）。`buildPredictOptions`（L124-215）把约 40 个推理参数（采样三件套、mirostat 三件套、penalties、grammar、stopwords、prompt cache、seed…）翻译成 PredictOption。`Predict`（L217-222）：有草稿模型走 `SpeculativeSampling`，否则普通 `Predict`。`PredictStream`（L224-247）：`SetTokenCallback` 把 token 推进 channel，goroutine 跑完 `close(results)`——gRPC 流式 = channel 语义。`Embeddings` 分文本级/token 级两路（L249-261）。细节瑕疵：L103 `llama.New` 的 err 到 L121 才返回，中途照常装草稿模型——legacy 代码的容错粗糙，也是读代码需批判的活例子。

**whisper/main.go——动态注册三步曲**：①定库名（darwin 与其他平台后缀分流）②`Dlopen(RTLD_NOW|RTLD_GLOBAL)` + 12 函数注册表（L38-51：load_model/load_model_vad/vad/transcribe/get_segment_{text,t0,t1}/n_tokens/get_token_id/get_segment_speaker_turn_next/set_abort/set_new_segment_callback）③`goNewSegmentCb = purego.NewCallback(onNewSegment)`（L60）——把 Go 函数固化成进程生命周期的 C 可调用指针，per-call 分发交给 user_data。

**gowhisper.go——回调桥与两条转写管线**：顶部 12 个 `Cpp*` 函数变量（L21-36）即 main.go 注册的目标。核心机制是**回调的三层桥**（L38-108）：`streamCallStates sync.Map`（callID→state）+ `streamCallSeq` 原子序号；`onNewSegment(idxFirst, nNew, userData)` 是 C trampoline 的 Go 侧，用 `nextIdx` 游标防御性遍历（防 whisper.cpp 合并多次 commit 到一次回调，L52-55），发 delta 前 `strings.ToValidUTF8(Clone(...))` 清洗（protobuf marshal 拒绝非法 UTF-8，L85）；**同步发送+channel 满即阻塞解码线程**——这是有意的背压路径，丢 delta 会破坏 `concat(deltas) == final.Text` 不变式（L73-76）；首个 delta 无前导空格、后续带单空格，拼出的文本就是空格连接的转写（L94-103）。

`Load`（L114-138）只认 `vad_only` 选项（只装 VAD 模型），其余打 stderr 警告。`VAD`（L140-174）：out 参数以 `0xdeadbeef` 哨兵初始化（栈追踪里见到它=C 侧没覆写）；`segsPtr==0` 对应空 vector；`unsafe.Slice` 把 C++ 内存读成成对 start/end 的 float32，/100 转秒。

`AudioTranscription`（离线，L176-278）六步：ctx 预检→临时目录+`utils.AudioToWav`（ffmpeg 转换）→wav 解码成 float32 PCM→**abort watcher**（goroutine 监听 ctx.Done→`CppSetAbort(1)`；defer 里 `close(done)+wg.Wait()` 同步 join，防迟到的 abort 腐蚀下一次调用，L213-231）→`CppTranscribe`（ret==2=取消）→逐段收集（时间戳×10000000 转 100ns、UTF-8 清洗、token id、diarize 加 `[SPEAKER_TURN]`）。`AudioTranscriptionStream`（L285-395）同骨架，再加：注册 per-call state+装 C 回调（defer 里 `SetNewSegmentCallback(0,0)`+`Delete`，panic 也能清干净陈旧指针，L320-333）；结束时 final 的 `Text` 直接复用 `state.assembled`（L389），e2e 契约 `concat(deltas)==final.Text` 由构造保证而非靠巧合。

## 三、外部连接

| 方向 | 对象 | 交互 |
|------|------|------|
| 上游 | pkg/grpc + pkg/grpc/base | StartServer 骨架、proto 消息（ModelOptions/PredictOptions/TranscriptRequest/VADRequest/TranscriptStreamResponse）、SingleThread 并发模板 |
| 上游 | core 模型加载器 | 按 backend 名 spawn 进程、传 --addr、gRPC Load/Predict/Free |
| 横向 | backend/cpp/llama-cpp | llama.cpp 现役主力（C++ 直写 gRPC，无 Go 层） |
| 横向 | backend/go/* 其他后端 | sherpa-onnx 等复用同 purego+回调注册表形状 |
| 下游 | go-skynet/go-llama.cpp | CGO 绑定（legacy） |
| 下游 | libgowhisper + whisper.cpp | purego 加载的 C++ 封装层 |
| 下游 | utils.AudioToWav / go-audio/wav | 音频格式归一化 |

## 四、数据流

**llama 路径**：core spawn 进程→gRPC `Load(ModelOptions)`（进程内 llama.New 载权重、可选草稿模型）→`Predict`/`PredictStream`（token 回调→channel→gRPC 流）/`Embeddings`/`TokenizeString`→`Free()` 释 VRAM→进程退出。

**whisper 流式路径**：音频文件→ffmpeg 转 wav→float32 PCM→`CppTranscribe`（whisper_full）→每段解码完成触发 new_segment_callback→C trampoline→`onNewSegment`（Go，按 callID 找 state）→results channel→gRPC 流→SSE；取消经 ctx→watcher→`CppSetAbort(1)`→whisper 内部检查点退出 ret=2。

## 五、设计决策

1. **每模型一进程**：注释明示 server-per-model——隔离崩溃、生命周期与模型对齐、Free 即进程退出兜底 VRAM 泄漏。
2. **main 极简+协议进框架**：23/67 行入口，所有后端共享 pkg/grpc 骨架；写新后端=实现一个 struct。
3. **SingleThread 并发模型**：whisper.cpp 的 ctx 是非线程安全单例，base 模板把并发调用串行化；`streamCallStates` 的 map 形状刻意镜像 sherpa-onnx 的 TTS 回调注册表——为将来去掉 SingleThread 不改契约预留（L38-42）。
4. **purego 优于 CGO（新代码）**：免 cgo 工具链、库运行时替换（WHISPER_LIBRARY）、跨平台分发只换 .so/.dylib；代价是手动签名注册与 unsafe 指针处理。
5. **回调指针生命周期分层**：NewCallback 指针进程级稳定，per-call 状态经 user_data 路由——稳定性和短生命周期解耦，C 回调永不指向已回收的 Go 栈。
6. **同步背压而非丢弃**：channel 满就阻塞解码线程——慢总比错好，不变式高于吞吐（L73-76）。
7. **abort 的同步 join**：watcher 必须 `wg.Wait()` 收尾，否则迟到的 `CppSetAbort(1)` 会杀掉下一次转写（L213-216 注释直书其害）。
8. **哨兵值做可观测防御**：`0xdeadbeef` 让"out 参数未被 C 覆写"在栈追踪里一眼可辨（L142-143）。
9. **边界处清洗数据**：非法 UTF-8 在逃出 cgo 前消毒，否则 protobuf 序列化时才炸，离事故现场十万八千里（L247-250）。

## 六、新人提示

- **写新 Go 后端**：从 `.agents/adding-backends.md` 清单开始，纯推理抄 llama 模板（Load+选项映射+Predict 三件套），带 C 回调的流式抄 whisper 模板（purego 注册表+三层回调桥+abort watcher）。
- **purego 后端的双边契约**：main.go 的函数注册表与 C 侧导出名单（gowhisper.cpp）必须同步增删，漏一个就是运行时 nil 调用。
- **改流式回调先读不变式**：`concat(deltas) == final.Text` 有 e2e 断言盯着，任何"优化掉空格/去重"的改动都会先挂测试。
- **调试 VAD/转写**：输出里见 0xdeadbeef 相关=出参没被覆写；转写静默失败先看 ret 码（2=取消，非 0=失败）。
- **别给 llama.go 加新功能**：它是 legacy 模板，llama.cpp 新能力（工具调用解析等）在 C++ 后端，见 `.agents/llama-cpp-backend.md`；读它的价值是学会"最小 Go 后端长什么样"。
- **SingleThread 假设**：任何并发化改造前记住 whisper ctx 单例约束；map 注册表已经为多并发铺路，但 C 侧还没有。
