# 04 · 前端音频双子星——useAudioPlayer 与 useMicrophone

> 源：`webui/client/src/utils/useAudioPlayer.ts`（135 行）、`useMicrophone.ts`（193 行）、`linear-pcm-processor.worklet.js`（73 行）、`audio-contexts.ts`（25 行）

## 一、角色定位

这对 hook 是浏览器侧音频编队：**useMicrophone 管"听"**——getUserMedia 采麦克风经 AudioWorklet 转线性 PCM，80ms 一块送 WS 上行（篇 03 旁路）；**AudioPlayer 管"说"**——收服务端 bot TTS Int16 块，归一化进预分配 60 秒 AudioBuffer 边写边播，barge-in 整块丢弃。共享 `audio-contexts.ts` 两个 AudioContext：BOT 用默认率、USER 钉 16k（19-25）——**采集与播放刻意不同率**，免一侧重采样。接线：`App/index.tsx:38` 建播放器、40 行 play、47 行 interrupt、54-58 建麦克风。

## 二、内部结构

### 2.1 AudioPlayer：生长式播放器（useAudioPlayer.ts:26-130）

常量：44100Hz、60s、Int16 极值（21-24）。核心状态：`offset` 写指针、`currentAudioSequenceDuration/StartedAt` 序列计时、`timerID` 复位定时器（27-35）。构造即预建 60s 单声道 AudioBuffer 并 connect destination（37-43）。

`play(buffer: Int16Array)`（51-97）三步：①Int16→Float32 归一化——正值除 32767、负值除 32768（60-66），避免负半周削 1 LSB；②**`offset === 0` 时 `source.start()` 并记 `startedAt`**（71-74）——Web Audio 没有 append/暂停 API，这里的技巧是"先启动播放头，后续块往缓冲区更后方写"，播放头追赶写指针，实现流式播放；③重算复位定时器（83-96）——序列总时长不可预知（bot 还在合成），每来一块 `clearTimeout` 重设"剩余时长 = 累计时长 − 已播时长"（86-92），到点 `reset()`。

`reset()`（107-117）：offset 清零、disconnect、**整体重建 buffer+source**——AudioBufferSourceNode 是一次性的（start 过不能重用），所以"清空"的代价是两个对象重建。`interrupt()`（124-129）= clearTimeout + reset，即 barge-in 的本地动作：立即掐断并丢弃缓冲。`getSource()`（119-121）暴露 source 节点给 BotFace 画波形（`App/index.tsx:123`）。

### 2.2 useMicrophone：授权状态机 + 采集管线（useMicrophone.ts:109-193）

双状态机合一：`MicAccessState`（INITIAL/LOADING/GRANTED/ERROR，36-41）+ `isRecording`（22-26），五 action reducer（70-101）。

`requestAccess`（122-167）：getUserMedia 默认设备（127-129）→ enumerateDevices 反查 label（130-134）→ **蓝牙/无线麦克风预警**（136-144）：蓝牙 HFP 档劣化采集拖垮 ASR，是前端唯一能提前 sniff 的信号。管线（146-156）：MediaStreamSource → worklet → **connect(destination)**（153）——worklet 不写输出，连 destination 非放音而是挂进渲染图：**不在图上的节点不会被音频线程拉取**。

`startRecording`（169-178）：未授权先 requestAccess，再 **`audioCtx.resume()`**（174）——浏览器 autoplay policy 下 AudioContext 出生即 suspended，需用户手势救活；`stopRecording`（180-185）用 **`suspend()` 而非断开管线**——恢复采集时无需重建 worklet。

### 2.3 linear-pcm-processor.worklet.js：Float→PCM16 折叠器

`BUFFER_SIZE_MS = 80`（24，块大延迟高但 I/O 少）。构造按 worklet 全局 `sampleRate` 算缓冲（16k 时 1280 采样）建 Int16Array（32-36）。`process`（44-61）：取第一输入第一声道（45-47）；Float32 [-1,1] clamp 后**负乘 0x8000、正乘 0x7FFF**（49-53）压 Int16；满则 `flush`——postMessage 结构化克隆给主线程（67-70），buffer 复用安全。

## 三、外部连接

useAudioPlayer 消费方：App:38/40/47/89/92/123（构造、play、interrupt、模式切换 enable、波形源）。useMicrophone 消费方：App:54-58（采集回调=`server.sendUserAudio`）、UserSpeechInput 用 `microphoneState`/`source`（App:137-142，source 喂 useRealTimeVolume 画音量）。worklet 经 Vite `?url` 导入（`useMicrophone.ts:20`）。类型小瑕：worklet 传出 Int16Array 而回调签名声明 ArrayBuffer（110，`useServerState.ts:439-441` 同）——`ws.send` 兼容 ArrayBufferView 故无恙。

## 四、数据流

上行：麦克风 Float32@16k → worklet 折叠 Int16@80ms → postMessage → `sendUserAudio` → WS 二进制帧 → 服务端 → `SendAudio` gRPC（篇 02）。下行：`botSentAudio` → WS 二进制帧 → `onReceiveBotAudio`（`useServerState.ts:273-275`）→ play 归一化写入 44.1k 缓冲（**下发若非 44.1k 此处无重采样**，契约由 TTS 侧保证）。barge-in 全链：Agent 检测 → `USER_BARGE_IN` 帧 → App:47 → interrupt()——**静音动作在浏览器本地完成**，零往返延迟。

## 五、设计决策（从代码反推）

1. **生长式播放而非 MediaSource**：MediaSource Extensions 不支持 AudioContext 图内使用；预分配大 buffer + 追写是 Web Audio 流式播放的标准解，60s 上限即 bot 单次连续发言上限——超出部分的写入越界静默丢弃（Float32Array 越界赋值 no-op）。
2. **非环形**：一次性线性缓冲，序列结束/打断即整体重建（107-117）——实现简单，重建频率低。
3. **双 AudioContext 不同采样率**（audio-contexts.ts:22-25）：采集钉 16k 与服务端 `USER_SPEECH_SAMPLE_RATE`（`config.ts:30-31`）对齐；播放走设备原生率——两侧解耦，谁也不迁就谁。
4. **suspend/resume 而非拆管线**（174, 181）：状态切换 O(1)，管线常驻——代价是 stop 后 worklet 仍在图上（挂起态不耗 CPU）。
5. **蓝牙预警放前端**（136-144）：授权时一次性提示，比事后排查"识别率差"省一个工单。
6. **注释与代码的一处不符**：57-59 注释称收到的是 "unsigned 16-bit words"，实际 `Int16Array` 是有符号（60-66 的正负分支也证明如此）——注释笔误，代码正确。

## 六、新人提示

- **改采样率先查三处对齐**：worklet 用 `sampleRate` 全局（32）跟随 USER_AUDIO_CONTEXT；服务端 config `USER_SPEECH_SAMPLE_RATE` 默认 16000；`StreamingRecognitionConfig` 首帧声明（`GRPCSpeechTask.ts:158-168`）——三处必须一致，否则 ASR 变速变调。
- **bot 音量无声先查 enable**：`play` 头部 52-54 直接丢未 enable 的块——模式切换（App:89/92）之外的场景调用 play 会静默失效。
- **barge-in 不掐服务端**：interrupt 只清本地；服务端照常推后续块，UI 靠 enabled/模式门控兜住。
- **音频块大小调优**只动 `BUFFER_SIZE_MS`（24）：80ms 是延迟/吞吐折中，减半则消息数翻倍。

## 甄别记录

任务书称 "60 秒环形 AudioBuffer"；源码实证为**一次性线性 60s 缓冲**（offset 单调递增、reset 整体重建，`useAudioPlayer.ts:99-117`），无环形写入逻辑，本文按源码。注释 "unsigned 16-bit"（57-59）与 Int16Array 实情不符，一并勘误。
