# 05 · gRPC 契约层——AceAgentGrpc 17 rpc 与 A2F 消息族

> 源：`ace_agent/4.1/webui/server/grpc/ace_agent.proto`（666 行）；`audio_2_face_microservice/1.2/proto/protobuf_files/nvidia_ace.controller.v1.proto`（118 行）与 `nvidia_ace.a2f.v1.proto`（156 行）

## 一、角色定位

两条并行契约线。**AceAgentGrpc**（`ace_agent.proto:24`）是对话后端统一门面：17 rpc 覆盖 pipeline 生命周期、语音双向流、转写流、上下文 CRUD 与文本对话，WebUI 服务端是头号消费者。**A2F 消息族**是 Audio2Face 数字人管线词汇表：两份 proto **全是 message、零 rpc**，服务定义在 services.* 系列（AnimationControllerService 4 rpc、A2FService 1 rpc）。分野即仓内架构界：对话智能 vs 面部动画。

## 二、内部结构

### 2.1 AceAgentGrpc：17 rpc 的功能分块（ace_agent.proto:24-108）

八块：Create/FreePipeline（28, 33）；SendAudio client-streaming（37）+ ReceiveAudio server-streaming（41）；StreamSpeechResults（48）；Start/StopRecognition（54, 58）；SetUserParameters/GetStatus/ReloadSpeechConfigs（62, 65, 69）；SynthesizeSpeech（79，注释 77-78：仅当 TTS 路由到 gRPC 客户端）；Get/Set/Update/DeleteUserContext（84-98）；Chat（104）/Event（107）。WebUI 只消费 5 个，其余给更全客户端。

### 2.2 语音三消息：首帧协议（110-160）

`SendAudioRequest`（115-136）oneof 合并配置帧与数据帧：注释 110-113 规定**首条必须是 StreamingRecognitionConfig**——篇 02 generator 首帧的协议依据。`StreamingRecognitionConfig`（139-160）五字段，注释 142 强调**仅单声道**。`ReceiveAudioRequest`（165-168）只有 stream_id。

### 2.3 StreamingSpeechResultsResponse：五路复用（290-309）

一条流 five-way `oneof metadata`（297-308）：asr_result/chat_engine_response/tts_result/pipeline_state/display_text——**五类载荷共用一条流**靠 case 区分（篇 02 的 switch 消费两路）。`ASRResult`（312-323）内嵌 Riva 的 `StreamingRecognitionResult`（327-339：alternatives 按置信度排序 + `is_final` 中间/终稿语义——前端气泡机制源头）。

### 2.4 Chat/ChatRequest：文本通道（531-616）

`ChatRequest`（548-583）十字段：query/bot_name（`{bot_name}_v{bot_version}`）/query_id/双语 language/`is_standalone`（574-576：true 不送 TTS）/user_context+metadata 双 map。`ChatResponse`（588-616）：text + `cleaned_text`（剥 markdown 版）+ is_final + json_response。

### 2.5 controller.v1：带结束标记的流词汇（18-116）

`AudioStream`（28-40）三分支：header → audio_with_emotion → **end_of_audio**（38）——显式哨兵标记结束。`AudioStreamHeader`（45-57）：audio_header+面部三参数组，注释 42-44 自我声明"**无 ID 版**"。`Event`（67-72）单一 `END_OF_A2F_AUDIO_PROCESSING`（59-65，"处理完"≠"收完数据"）+ Any metadata。`AnimationDataStream`（102-116）四分支，status 可夹中间可作末帧。`start_time_code_since_epoch`（95）注释是微型时间同步论文：Unix 纪元秒 + NTP 公网几十毫秒/局域网亚毫秒 + PTP 备选（86-94）。

### 2.6 a2f.v1：表情参数三件套（29-154）

`AudioStream`（29-37）**只两分支，无 end_of_audio**——注释 32 明说"关连接即结束"，与 controller 版哨兵形成同名异构对照。`AudioStreamHeader`（42-59）带 AnimationIds 即"带 ID 版"。参数三件：`FaceParameters`（64-74）map 泛型键值，注释 66-68 枚举 14 面部键；`BlendShapeParameters`（96-101）multipliers 缺省 1 + offsets 缺省 0，注释 89-95 给 clamp 算例；`EmotionPostProcessingParameters`（104-146）六参数全带默认值区间。`AudioWithEmotion`（148-154）= bytes 音频 + EmotionWithTimeCode 时间轴——**情绪是逐时刻曲线**。

## 三、外部连接

ace_agent.proto 经 buf.gen.yaml 生成 TS 到 `grpc/gen/`，被 GRPCClient（`GRPCClient.ts:21`）与三个 gRPC 任务 import。A2F 族被 services.* 两个服务 proto import；webui **不直接消费 A2F 族**（Unity/Unreal 集成侧契约）。两族共享 status.v1.Status。

## 四、数据流

语音全链：CreatePipeline → SendAudio（config→audio×N）→ ASR → StreamSpeechResults 回转写 → chat engine → TTS → ReceiveAudio 回音频 → FreePipeline。stream_id 是公共主键，对应篇 01 的 randomUUID。A2F 侧：PushAudioStream 推音频 → 推理 blendshape → PullAnimationDataStream 拉动画——一推一拉。

## 五、设计决策（从代码反推）

1. **首帧协议而非独立 rpc**：SendAudio 把 config 与数据合入一条流（115-136），省往返且保序——与 Google STT streaming API 同构，Riva 血统。
2. **五路 oneof 复用一条流**（290-309）：一次订阅看尽全程，代价是消费者按 case 自行分流。
3. **消息与服务分包**：controller/a2f 零 rpc，services.* 只写签名——消息族被三个服务复用而不重复定义。
4. **同名异构是刻意的两代共存**：controller.v1（无 ID+显式哨兵）与 a2f.v1（带 ID+关连接结束）注释互指（42-44 ↔ 39-41）——**import 选错包名不报编译错，只运行时字段缺失**，最需警惕。
5. **is_standalone 双开关**：ChatRequest:576 控 TTS 旁路、SpeechRecognitionControlRequest:221-227 控 ASR→DM-TTS 直通，语义相近作用层不同。
6. **注释即规范**：单声道（142）、首帧顺序（110-113）、clamp 算例（89-95）、NTP 精度（86-94）——隐式契约的唯一文档就是注释。

## 六、新人提示

- **加 rpc 先看 webui 是否消费**：GRPCClient 是 PromiseClient 泛型（`GRPCClient.ts:37-43`），新方法自动可用。
- **A2F 发音频别选错 AudioStream**：controller 版要发 EndOfAudio 哨兵、a2f 版靠 half-close——用错结束方式服务端挂等或提前截断。
- **改 sampling 相关字段记得三处对齐**（见篇 04 第六节）。
- **is_final 才是句边界**：中间帧整段重写，UI 只能原地更新（篇 03 mutate 路径为此设计）。
- **EmotionWithTimeCode 是曲线**：表达情绪要按时间轴铺点，单点只影响局部。

## 甄别记录

任务书称 "controller.v1.proto（17 rpc）"且路径指 `ace_agent/4.1/grpc/proto/`（不存在）；源码实证：**17 rpc 全在 `webui/server/grpc/ace_agent.proto` 的 AceAgentGrpc**，controller.v1.proto 位于 `audio_2_face_microservice/1.2/proto/protobuf_files/` 且**零 rpc 纯消息**。AudioStream 同名异构（EndOfAudio 有无、Header ID 有无两处主证）经注释 42-44/39-41 互指实证。
