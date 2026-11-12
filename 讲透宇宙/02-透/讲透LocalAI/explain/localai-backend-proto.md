# localai-backend-proto — 52 个 RPC 的 Inference+Control 双协议统一契约

> 源码：`backend/backend.proto`（1473 行，注意：不在 pkg/grpc 下；生成代码 go_package 指向 `pkg/grpc/proto`）
> 契约核心：单一 `service Backend`，52 个 RPC 覆盖控制面与全部推理域

## 角色定位

这是 LocalAI 架构的"宪法层"。18 层架构里它单独成层：控制器（Go 主进程）与后端进程（llama.cpp C++ 绑定、Python、独立 Go 进程、分布式 worker）之间的**唯一**通信契约。任何语言实现这 52 个 RPC 的子集，即可成为 LocalAI 后端——AGENTS.md 的 adding-backends 流程本质就是"实现这个 service + 注册构建"。它存在的理由：推理引擎生态爆炸（llama.cpp/vLLM/SGLang/diffusers/whisper/…），LocalAI 用一份冻结的 proto 把"引擎多样性"封死在后端边界内，主进程代码不感知任何引擎细节。图谱中 .proto 不被 file-analyzer 分析（无节点），但它约束着 pkg/grpc 全部生成代码与 81 个 backend/go/* 进程。

## 内部结构

单一 `service Backend`（10-106 行），52 个 RPC 按域分组：

- **控制面（7）**：`Health`/`Free`/`Status`/`LoadModel`/`UnloadModel`（隐含于 Free）/`ModelMetadata`/`GetMetrics`。生命周期 = LoadModel 装载 → 推理 → Free 释放。
- **文本推理（10）**：`Predict`/`PredictStream`（服务端流）/`Embedding`/`TokenizeString`/`Detokenize`/`Rerank`/`Score`/`TokenClassify`/`StoresSet/Delete/Get/Find`（向量存储 CRUD，实际 4 个）。
- **视觉（8）**：`GenerateImage`/`UpscaleImage`/`GenerateVideo`/`Generate3D`/`Detect`/`Depth`/`FaceVerify`/`FaceAnalyze`。
- **音频（14）**：`AudioTranscription`（含 Stream/Live 三形态）、`TTS`/`TTSStream`、`SoundGeneration`/`SoundDetection`、`VAD`/`Diarize`、`AudioEncode`/`AudioDecode`、`AudioTransform`/`AudioTransformStream`、`AudioToAudioStream`（双向流）、`VoiceVerify/Analyze/Embed`。
- **作业（6）**：FineTune 三件套（Start/Progress 流/Stop）、Quantization 三件套、`ListCheckpoints`/`ExportModel`。
- **代理（1）**：`Forward` 双向流。

核心消息（1473 行中的骨架）：

- `PredictOptions`（287-373 行，54 字段）：llama.cpp 风格采样超参全集（Temperature/TopK/TopP/MinP/Mirostat×3/惩罚×4/TailFreeSamplingZ/TypicalP…）+ 多模态数组（Images/Videos/Audios）+ `Messages`（对话轮次）+ 工具调用（Tools/ToolChoice 为 JSON 字符串）+ `Metadata` map + **`ModelIdentity`（字段 54）**。
- `Reply`（392-401 行）：`bytes message`（正文/音频二进制复用）+ tokens 双计数 + 两段 timing + `bytes logprobs`（OpenAI 格式 JSON）+ `repeated ChatDelta chat_deltas`。
- `ChatDelta`（385-389）+`ToolCallDelta`（377-382）：C++ autoparser 的增量解析产物——content/reasoning_content/tool_calls 三通道，流式与最终结果共用。
- `ModelOptions`（407-533）：LoadModel 的装载参数镜像（ContextSize/F16Memory/GPU 层数等）。

## 外部连接

`option go_package = "github.com/go-skynet/LocalAI/pkg/grpc/proto"`：protoc 生成物落在 pkg/grpc/proto/，被 `pkg/grpc/client.go`（控制器侧客户端）、`pkg/grpc/server.go`（Go 后端服务端）、`backend/cpp/`（llama.cpp C++ 实现）与 81 个 `backend/go/*` 进程共同编译。`.agents/adding-backends.md` 的接入清单第一步就是对照本文件。改一个字段号 = 全生态重新编译；`reserved 24`（372 行）示范了防复用纪律。

## 数据流

以一次流式 chat 为例：控制器把模板渲染后的 prompt、采样参数、Tools JSON、ModelIdentity 打进 `PredictOptions` → `PredictStream` 返回 `stream Reply` → 后端每生成一段就 Send 一个 `Reply`：`message` 是增量文本，若 C++ 侧启用 autoparser 则 `chat_deltas` 携带解析好的 content/reasoning 分离与 tool_call 分片，Go 侧免做正则 → EOF 即结束。`Forward` 则是另一条路（105-106 行注释）：首帧 `ForwardRequest` 带 path/method/headers/首块 body，后续帧只带 `body_chunk`；响应侧首帧带状态码+headers，后续流式回传 SSE 帧；gRPC ctx 取消即断上游连接——大 body 无缓冲穿透。

## 设计决策

1. **Inference+Control 合一的单 service**：不拆"管理/推理"两个 service，后端进程只需实现一个接口即获得完整生态位；控制面 RPC（Health/Status）天然复用同一连接与鉴权。
2. **ModelIdentity 显式防错配**（341-369 行长注释）：分布式模式下 worker 可把停止后端的端口复用给另一个模型，纯活探针无法区分——`ModelIdentity` 与 LoadModel 时的 `Model` "由构造相等而非约定相等"，空值表示"跳过检查"保住老控制器兼容；同时明确禁止用 TTSRequest.model 冒充身份（它会被 FileStagingClient 改写成本地路径）。
3. **bytes 万能通道**：message/logprobs 用 bytes 而非 string，音频二进制与文本同字段复用，logprobs 以 OpenAI JSON 原样透传——内部 proto 不建模的细节就不翻译。
4. **Forward 的 wire-passthrough**：云代理翻译模式走 Predict，透传模式走 Forward 原样转发——"新 provider 字段当天可用"与"跨 provider 翻译"两种需求分开满足。
5. **每个 RPC 的语义注释都写在 proto 里**（如 TokenClassifyEntity 的 HF 聚合标签约定、ScoreRequest 的 KV 复用承诺）——契约即文档，多语言实现者无需读 Go 源码。

## 新人提示

- 切入点：先读 10-106 行的 service 定义（每个 RPC 一行），再精读 PredictOptions/Reply/ModelOptions 三个消息；其余 1400 行是各专域消息，按需查。
- 易混淆点一：`PredictStream`（单向服务端流）与 `AudioToAudioStream`（双向流）流形态不同，client.go 里对应两种生命周期封装。
- 易混淆点二：`Model` 字段在 PredictOptions 里不存在——模型身份由连接目标（LoadModel 过的进程）+ModelIdentity 表达；请求里另带模型路径是分布式 FileStaging 改写的产物。
- 加新 RPC 时 checklist：proto 定义 → 两端生成 → client.go 复制模板 → embed.go 适配 → AGENTS.md 的 backends 清单；漏 embed.go 会让进程内 Go 后端缺方法。
