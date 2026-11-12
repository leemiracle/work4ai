# 02 · WebSocketTask 与 gRPC 语音任务族——浏览器代理与音频管道

> 源：`webui/server/chat-session/tasks/WebSocketTask.ts`（592 行）、`GRPCSpeechTask.ts`（218 行）、`GRPCSpeechTranscriptionTask.ts`（108 行）

## 一、角色定位

三文件构成会话**数据面**（与 ChatSessionTask 控制面对称）。WebSocketTask 是浏览器在服务端的唯一代理：一端收 WS 帧一端收发 eventBus 事件，做协议翻译（`WebSocketTask.ts:38-42`）。GRPCSpeechTask 是**语音上行管道**：`userSentAudio` 经 client-streaming `SendAudio` 灌进 Agent，同时 `ReceiveAudio` 拉 bot 音频（`GRPCSpeechTask.ts:36-41`）。GRPCSpeechTranscriptionTask 是**字幕管道**：订阅 `StreamSpeechResults` 推转写给 UI（`GRPCSpeechTranscriptionTask.ts:31-38`），仅非 event 模式启用。

## 二、内部结构

### 2.1 WebSocketTask：listen/handle/send 三族（34 方法）

三族私有方法：**listen 12**（`WebSocketTask.ts:63-76` Promise.all 并联）、**handle 12**、**send 8**，链路机械：`listenX → once → handleX → sendXToUser → ws.send`。listen 两类：ws 本体三个——messages（91-96）/error（101-106）循环、close（111-114）**单发**；eventBus 九个全循环（120-241：botListUpdated/botStartedUtterance/ThinkingIdle/Gesture/botSentAudio/asrAvailable/userBargeIn/shutdown/serverConfigChange）。start 吞 `AbortError`、其余升级 `fatalError`（77-84）。

### 2.2 入站分发 handleWebSocketMessage（257-308）

一条 WS 两种帧：**ArrayBuffer 即用户音频**（258-261 直接 emit `userSentAudio`）；文本帧 JSON.parse 后按 `content.type` 三分支（277-307）：TYPING 按 isNewMessage 拆 `userStartedNewMessage`/`userUpdatedMessage`（278-291）；TEXT 发 `userFinishedMessage`（293-299）；TOGGLE_SPEECH 发 `userToggledSpeech`（301-306，模式切换入口）。解析失败仅 log（267-270）——坏帧丢弃不杀会话。

### 2.3 handle/send 族要点

`handleWebSocketClosed`（429-432）emit `userClosedSocket` 触发会话收尸；`handleWebSocketError`（438-440）只 log，ws error 不致命。`handleBotStartedGesture`（359-377）唯一 async handle：`emojiFinder.findEmoji(gesture)` 把手势译成 emoji，找不到 WARN 丢弃（367-373）。send 族 8 个序列化器：文本（461-477）/系统配置（484-490）/关机（496-505）/emoji（515-533）/typing（539-551）/**音频块（557-559，唯一二进制通道）**/ASR 字幕（567-577）/barge-in（583-591），共用 `shared/types.ts` 联合类型。

### 2.4 GRPCSpeechTask：队列+生成器+流

`interactionModes` 仅 SPEECH（`GRPCSpeechTask.ts:43-45`）——文本模式下被停，但 gRPC pipeline 不拆：`pipelineAcquired` 标志（59）保证**模式切换的 stop/start 不重复 `CreatePipeline`**（77-81），仅 cleanup 时 `FreePipeline`（68-72, 204-209；rpc 定义 `ace_agent.proto:28,33`）。start 并联三路（83-87）：①`listenBotAudio`（104-122）：while 内发起 server-streaming `ReceiveAudio({streamId})`，`for await` 逐块 emit `botSentAudio`（114-120）——流结束再开新一轮，天然重连；②`listenUserSentAudio`（127-136）收事件入队（143-146）；③`processUserAudioQueue`（153-188）：**async generator 首帧固定 `streamingConfig`**（158-168：单声道 LINEAR_PCM、采样率默认 16000，`config.ts:30-31`），此后 shift 队列产 `audioContent` 帧，队列空 `sleep(1)` 让权（169-181）；generator 交给 client-streaming `SendAudio`（185-187）。

### 2.5 GRPCSpeechTranscriptionTask：字幕与气泡

`currentMessageID`（`GRPCSpeechTranscriptionTask.ts:52`）承载 UI 语义：同一句 ASR 增量共用同一 messageID（气泡原地刷新），`isFinal` 后自增（101-103）开新气泡。`listenTextTranscription`（76-107）：while 循环 server-streaming `StreamSpeechResults`（83-85），`metadata.case` 二分支：`displayText`→`botStartedUtterance`（90-93）；`asrResult`→`asrAvailable`（94-103，取 `alternatives[0]` 最优候选）。

## 三、外部连接

上游：ChatSessionTask 注入 ws 与 emojiFinder（构造 49-55）；下游即兄弟任务——`userSentAudio` 由 `WebSocketTask.ts:260` 产生、`botSentAudio` 被 176-185 回传浏览器。三者共享 `GRPCClient` 单例（`GRPCSpeechTask.ts:47`）。测试 `WebSocketTask.test.ts`/`GRPCSpeechTask.test.ts` 覆盖事件往返。

## 四、数据流

语音全双工闭环：麦克风帧→WS→258→队列→`SendAudio`（config 帧先行）→Agent ASR；Agent TTS→`ReceiveAudio`→二进制 ws 帧→AudioPlayer（篇 04）；转写→`StreamSpeechResults`→JSON ws 帧→UI 气泡。barge-in 反向：Agent 检测→`userBargeIn`→`USER_BARGE_IN` 帧→UI 掐断本地音频缓冲（401-411）。

## 五、设计决策（从代码反推）

1. **协议翻译层零业务**：34 个方法全是收发翻译、无状态；换 ws 库或 schema 只动这一文件。
2. **音频走二进制旁路**（257-261, 557-559）：不 base64 不进 JSON——`index.ts:170` 的 `ws.binaryType="arraybuffer"` 是前提。
3. **队列+生成器解耦收发速率**（52, 157-182）：内存队列+`sleep(1)` 轮询是最朴素的背压，代价是空闲自旋。
4. **pipeline 生命周期独立于任务启停**（59, 68-72）：Create/FreePipeline 是重操作，标志位把它抬到会话级一次。
5. **流断自动重连**（106-121）：server-streaming 正常结束不算错误，下轮 while 重发，瞬时抖动消化在任务内部。
6. **AbortError 判法三处不一致**：`e.name === "AbortError"`（`WebSocketTask.ts:78`）/`e.code === "ABORT_ERR"`（`GRPCSpeechTask.ts:89`）/`e.code === 1`（`GRPCSpeechTranscriptionTask.ts:63`）——同一件事三种写法。

## 六、新人提示

- **加新消息类型只动两处**：`shared/types.ts` 加类型 + 本文件加一对 listen/handle。
- **别在 handle 里做重活**：handle 被 once 循环内联 await，查表（366）已是上限，重活会阻塞后续消息。
- **音频调试看两 log**：385 与 171 两行——两侧都有数而 UI 无声，问题在浏览器端（篇 04）。
- **`e.code === 1`**（63）是 gRPC CANCELLED 状态码。

## 甄别记录

任务书称 "35 方法"；源码清点 **34 个**（12 listen+12 handle+8 send+构造+start），按源码口径。其余图谱 summary 与源码一致。
