# core/http/endpoints/openai/realtime.go — OpenAI Realtime API 会话引擎：从一帧声音到一个回应

> 源文件：`core/http/endpoints/openai/realtime.go`（2931 行）
> 知识图谱归属：api-openai 层
> ⚠️ 路径勘误：任务原始路径 `core/http/endpoints/localai/realtime.go` 不存在，实际位于 `core/http/endpoints/openai/`。同目录还有约 20 个 `realtime_*.go` 协作文件（transport_ws/webrtc、conncoord/turncoord/respcoord/compactcoord 四个协调器、tts_pipeline、semantic_vad、sound_detection、voicegate、compaction、chunker、stream 等），本文件是主引擎。

## 一、角色定位

这是 LocalAI 对 OpenAI Realtime API 的实现：一条 WebSocket 或 WebRTC 连接上的全双工语音对话——客户端持续推音频，服务端做话轮检测（VAD）→转写→LLM 推理→TTS 合成→推回音频事件流。文件开头一句话给出架构分野（L100-101）：模型可以是**组合管线**（VAD+STT+LLM+TTS 四个独立后端拼成，"emulated"），也可以是 **any-to-any 单模型**（如 liquid-audio 一个引擎包办全程，走专用路径）。`prepareRealtimeConfig`（L437-467）负责识别：带 `FLAG_REALTIME_AUDIO` usecase 的模型自动把自身名字填进四个空管线槽（L447-459），用户仍可逐槽覆盖；两者都不是则拒绝。

三种会话形态共用一个循环：完整 realtime、transcription-only（`updateTransSession` L1113 切换）、sound-detection-only（`soundOnly` L537：有 sound_detection 无 STT/LLM→关 VAD 关转写，靠声音事件激活）。对上游它是 echo handler（`Realtime` L349：WS upgrade→读 query 参数→进主循环；`RealtimeSessions`/`RealtimeTranscriptionSession` 是 501 占位）；对下游它只依赖 `Model` 接口（L269-315：VAD/Transcribe/Predict/TTS/TTSStream/TranscribeStream/SoundDetection/TranscribeLive/ClassifyTurn/FillToolArguments/Warmup 等 14 个方法）——管线与 any-to-any 在此统一。

## 二、内部结构

**Session（L104-199）是会话状态大全**：TurnDetection（server_vad/semantic_vad/none）、InputAudioTranscription、双锁音频缓冲（InputAudioBuffer+AudioBufferLock / OpusFrames+OpusFramesLock）、Conversations、Tools、Classifier（prefill 打分选项选择，替代生成）、Compaction 四参数+懒加载 summarizerFactory、AssistantExecutor/AssistantTools（进程内 MCP 工具面）、voiceGate+voiceVerified（声纹门）、respSink（M3 响应协调器）。常量层（L47-61）：本机采样率 16000（全部 ASR/VAD 后端约定）、远端默认 24000、音频缓冲上限 100MB、WS 单消息上限 10MB、`defaultInstructions`（教模型"输出会被念出来"的语音体提示词）。

**runRealtimeSession（L471-1058）十步搭台**：加载模型配置→assistant 工具发现（admin 门禁 L494）→soundOnly 判定→建 Session+默认 Conversation+`newResponseSink()`（单写者、至多一个活跃响应，L589-592 注释直书它替换的 legacy dual-writer）→newModel 构建 ModelInterface→voiceGate 构建→**Warmup**（L670-688：并发预热全部子后端+声纹模型，阻塞到全部完成——加载失败在会话建立时报，而不是首回合调用到一半炸；`disable_warmup` 退回懒加载）→WebRTC 专属（InputSampleRate 直接设 16000 防双重重采样，L710-712）→connSink（M1 连接协调器：VAD/opus 解码/声音窗口三个 goroutine 的启停与一次性 teardown）→进入读循环。读循环（L760-1051）分发 11 类客户端事件：session.update 双分支（模型/voice/STT 变更会重建 ModelInterface 并**异步** Warmup——updateSession 持全局 sessionLock，阻塞多秒会卡死所有会话，L1221-1235 注释）；append（base64+100MB 闸）；commit（手动路径，经 respSink 串行）；item 增删截查；response.create/cancel（都走 respSink）；`test_tone` 诊断事件（440Hz 正弦波全链路自检，仅 WebRTC，L1089-1111）。

**入站音频两条汇合路**：WS 走 base64→直接 append；WebRTC 走 `decodeOpusLoop`（L1312-1361）——300ms ticker 把 Opus 帧攒批、单次 gRPC AudioDecode、48k→16k 重采样后 append，约 3 次调用/秒而非每 RTP 包一次。

**话轮检测 handleVAD→vadTick（L1412-1644，引擎核心）**：300ms 一 tick。每 tick：①重读语义模式配置（session.update 可中途切换；semantic→server 切换时丢弃孤儿 live 流但**不打断说话中的 turn**，L1479-1486）；②90s 缓冲上限整秒裁剪+游标 rebase（`maxTurnBufferSec`，L1378-1385 注释解释永不暂停的 turn 会怎样）；③**扫描窗口裁剪**（L1523-1536）：silero 只有几百 ms 循环记忆，窗口=max(提交阈值,语义 eagerness)+1s 余量，只扫尾部——把每 tick 成本从"全缓冲二次方"降为常数，段坐标再 rebase 回全缓冲坐标；④runVAD gRPC；⑤零段≠无语音的三态处理（L1560-1596）：裁剪生效时窗口全静音但 turn 在说话→用 `lastSpeechEndSec` 直接提交（真语音不能当噪声丢）；真无语音→`dropInspectedPrefix` 保留 0.5s holdback（`noSpeechHoldbackSec`：词首可能已开始而 silero 未过阈，L1363-1368）+turncoord Abort(no_speech)；⑥有段→`turncoord.Onset`（Idle→Speaking 原子转移：开 live ASR 流+喂缓冲前缀+**BargeIn 非阻塞取消在途响应**+发 speech_started——"turn 开"与"speech started"永不失同步，L1427-1431 注释）；⑦尾静音超阈值→`vadCommit`（L1651-1713）：语义模式先过 **retranscribe 门**（EOU 触发的提交用离线批解码复核流式 EOU，假阳性就消费掉 EOU 继续听，L1664-1689），然后 `dropInspectedPrefix(inspectedBytes, 0)`（tick 期间新到的音频属于下一 turn）+turncoord Silence（speech_stopped→committed→终结 live 流→发起响应）。

**提交→响应 commitUtteranceWithTranscript（L1747-1929）**：写临时 WAV；声纹门 `Resolve` 与转写**并发**起跑（纯延迟优化，L1774-1809 注释：硬 join 在 LLM 之前，未授权的声音永远到不了 LLM/tools/TTS）；转写四分支（gated 批解码权威 / live 流文本直接复用 itemID / 文件路径 emitTranscription / sound-only 无转写）；声纹 join 处 **fail-closed**（裁决不了=不放行，L1880-1887）+when:first 会话级短路 + 个性化注入；最后 `generateResponse`→`triggerResponse`。

**响应生成 triggerResponse（L2194-2247）+triggerResponseAtTurn（L2249-2585）**：核心不变式是 **liveResponse 单 terminal**——一个 response.create 从头到尾恰好一个 response.created/done，跨整个服务端 agentic 工具递归共享同一 id、累积 output、求和 usage（L2155-2171 注释；metadata 回显让客户端能把带外响应与自己的请求配对）。每回合：组装会话历史（instructions+compaction Memory+`trimRealtimeItems` 尾部裁剪且保住 function_call/output 配对，L415-430）→声纹个性化→classifier 分支（prefill 打分，toolTurn==0 才生效）→流式 LLM 分支（管线开 streaming 且工具走 tokenizer template 才可流，防语法函数调用的 JSON 泄进语音，L2425-2431）→buffered 路径：Predict→**ChatDeltas 优先**（C++ autoparser 解析好的 content/tool_calls 直接用；#9985：无 reasoning 时防御性再抽 think 标签）→reasoning 抽取→ParseFunctionCall→NoAction "answer"函数取 message 字段当语音→`emitAssistantMessage`（output_item.added→content_part.added→transcript delta/done→TTS 音频→双 done；每个阶段有 barge-in 检查点，取消时把半成品 item 从会话里摘除，L2647-2653）→`emitToolCallItems`（L2775-2902）双路径：Assistant 工具进程内执行（call+output 都入会话，客户端只见可观测事件）并递归 `triggerResponseAtTurn`（上限 `maxAssistantToolTurns=10`）；普通工具走 OpenAI 标准回环（arguments.done 等客户端送回输出）。收尾 `maybeCompact` 把老化 turn 折叠成滚动 Memory。ID 全部 crypto/rand 16 字节 hex，注释写明无碰撞是会话记账的硬前提（L2923-2930）。

## 三、外部连接

| 方向 | 对象 | 交互 |
|------|------|------|
| 上游 | echo 路由 /v1/realtime | Realtime 入口；Sessions/TranscriptionSession 端点 501 占位 |
| 协作 | 同目录 20 个 realtime_*.go | 四协调器（conncoord/turncoord/respcoord/compactcoord=M1-M4）、transport 双实现、tts_pipeline、semantic_vad、voicegate、compaction |
| 下游 | Model 接口实现（realtime_model.go） | 管线组装或 any-to-any 直连 |
| 依赖 | application | 模型配置/加载器、模板求值器、LocalAIAssistant holder、VoiceRegistry |
| 依赖 | pkg/{sound,laudio,functions,reasoning} | 重采样/WAV 头/函数调用解析/think 标签抽取 |
| 依赖 | backend 包 | TokenUsage、PreloadStages（warmup）、LiveTranscription 会话 |

## 四、数据流

入站一帧声音的完整旅程：客户端 append（WS：base64 PCM16；WebRTC：Opus RTP→decodeOpusLoop 批解码重采样）→InputAudioBuffer→handleVAD 每 300ms tick→silero 段+（语义模式）live ASR 流的 delta/EOU→vadCommit→临时 WAV→（声纹 Resolve 并行）→transcribe→user item（带 transcript+speaker）→triggerResponse→历史组装→Predict→ChatDeltas/文本+工具解析→emitAssistantMessage→TTS（流式则逐 PCM 块发 audio delta）→transport.SendAudio。横向贯穿的是取消语义：BargeIn 在 Onset 时取消在途响应，之后在"LLM 后/TTS 前/TTS 中"三处检查点收尾，取消的半成品从会话历史摘除。连接拆除由 conn.close() 按依赖序完成，恰好一次。

## 五、设计决策

1. **四个显式状态机替换布尔标志群**：M1 连接/M2 话轮/M3 响应/M4 压缩，注释多处标注"替换 legacy 失败模式 N"（如 speechStarted 与 live 流失同步、dual-writer 响应、compacting atomic.Bool）——并发正确性靠结构而非纪律。
2. **单 terminal 不变式**：liveResponse 跨递归累积，agentic 多回合对外是一个 response——协议形状由构造保证。
3. **裁剪窗口建立在模型特性上**：silero"只有几百 ms 记忆"是被注释论证的事实，性能优化因此安全；窗口地板防配窄（长静音不可测=turn 不可提交）。
4. **音频保守主义**：0.5s holdback、裁剪后全静音仍按 lastSpeechEnd 提交、"零段≠无语音"——宁可多听半秒，不切词首。
5. **fail-closed 声纹门**：Resolve 出错=拒绝；并发仅是延迟优化，硬 join 在一切副作用之前（注释把"被拒 turn 只浪费无副作用的转写算力"的安全论证写全了）。
6. **warmup 双策略**：会话建立时阻塞（早暴露错误），session.update 时异步（全局锁下阻塞会卡所有会话）——同一操作两种策略，依据是持锁范围。
7. **三层资源上限**：单 WS 消息 10MB/音频缓冲 100MB/单 turn 90s，各自注释论证攻击面或增长路径。
8. **buffer 全复制纪律**：dropInspectedPrefix 有裁剪时返回 fresh copy，防后续 append 涂写与旧 backing array 共享的内存（L1387-1392）。
9. **传输无关**：Transport 接口隔离 WS/WebRTC 差异，test_tone 顺带成为 Opus 编码→RTP→浏览器解码全链路的探针。

## 六、新人提示

- **阅读顺序**：本文件 → 四个协调器包（conncoord/turncoord/respcoord/compactcoord，注释里的"Part 2 failure mode N / invariant N"即指它们的设计文档）→ realtime_model.go（Model 接口实现）。
- **改话轮检测先跑测试**：vadTick/classifySoundWindow 被刻意提取成同步函数，就是为了不用 ticker 驱动；三个常量（holdback/warmupMargin/maxTurnBufferSec）的注释是裁剪正确性的论证，动它们先动注释。
- **事件协议以 types 包为唯一权威**：诊断事件（test_tone）不在 OpenAI 协议内，别混进正常分支。
- **加新音频处理逻辑记住采样率约定**：缓冲是 InputSampleRate（默认 24k），VAD/STT 固定 16k，重采样只该发生在一处。
- **调"为什么没反应/为什么被打断"**：看 respSink（响应串行化）与 BargeIn 检查点；看 turncoord 状态（Idle/Speaking）而非猜布尔标志。
- **协议兼容细节有据可查**：`modalities` beta 别名（L76-87）、language-only 更新保 STT backend（L1200-1213）、AssistantTools 在客户端 tools 刷新后存活（L1258-1281）——每条注释都是一个真实翻车故事的墓碑。
