# 10 · 音频引擎线：decoderWorker 预热、moshi-processor 抖动缓冲与可视化

## ① 角色定位

客户端实时性的全部难点集中在这条线。下行管线：WS 上的 Opus 页 → decoderWorker（Web Worker + WASM 解码）→ Float32 帧 → `moshi-processor`（AudioWorklet 抖动缓冲）→ 扬声器 + AnalyserNode 可视化。上行：麦克风 → opus-recorder（第二个 Worker，Opus 编码）→ WS。`decoderWorker.ts` 的核心使命是**预热**：用户还在首页点按钮时就把 WASM 拉下来初始化，把"连上才加载 WASM"的卡顿消灭在授权等待期。React 层只做编排，samples 永不经过组件状态。

## ② 内部结构

**decoderWorker.ts（预热管理器，159 行）**。`createWarmupBosPage`（L6-37）手工构造最小合法 Ogg BOS 页：OpusHead（L8-16，mono/48kHz/pre-skip 312）+ OggS 页头（L19-29，BOS flag L22、单 segment 19 字节 L27-28），CRC 全零——L26 注释明言"decoder doesn't check"，作用是触发解码器内部 init() 建缓冲。`createWorkerWithErrorTracking`（L40-52）用 `new Worker(new URL("/assets/decoderWorker.min.js", import.meta.url))`（L41-43）建 worker，onerror 记录 `lastWorkerError`。`sendInitCommand`（L55-73）发 init：`bufferLength = 960 * sampleRate / 24000`（L58）、解码侧 24kHz（L59）、重采样到 AudioContext 采样率（L60）、`resampleQuality: 0`（L61）；100ms 后补发 warmup BOS（L65-72）。预热单例（L76-78）；`prewarmDecoderWorker`（L81-109）：同采样率复用（L82-85）、否则 terminate 重建（L88-90），**用 1000ms setTimeout 当"就绪"**（L99-106）。`getPrewarmedWorker`（L113-138）：有错整只丢弃（L122-130），成功则**一次性取走并清空单例**（L132-136）。`createDecoderWorker`（L141-143）兜底；`initDecoder`（L146-159）对非预热 worker 同样处理。

**audio-processor.ts（AudioWorklet，185 行，首行 `// @ts-nocheck`）**。`MoshiProcessor` 构造器（L10-30）定缓冲参数：`frameSize = 80ms`（L17）、`initialBufferSamples = 1 帧`（L19，起播门槛）、`partialBufferSamples = 10ms`（L22）、`maxBufferSamples = 10ms`（L25，溢出阈值）、两个 5ms 增量（L27/L29）与 80ms 上限（L28/L30）。`port.onmessage`（L35-77）：reset 重建状态（L36-40）；攒够 initialBuffer 就 `start()`（L43-45）；超过 `totalMaxBufferSamples()`（L101-103 = 三者之和）就从最老帧丢到 `initial+partial`（L50-63）并把 maxBufferSamples 增 5ms 封顶 80ms（L65-67）；每包回传统计（L70-76，含 `delay: micDuration - timeInStream`）。`initState`（L80-99）**把两个缓冲参数打回 10ms**（L96-98），自适应成果不跨会话保留。`process`（L132-183）：`canPlay`（L128-130）要求已 start、有帧且 partial 耗尽；欠载时（L168-177）partialBuffer 增 5ms、`resetStart()` 回蓄水态、本块**淡出**（L175-177）；恢复首块**淡入**（L162-167）消爆音；统计累计量（L179-181）。L185 `registerProcessor("moshi-processor", ...)`。

**useServerAudio.ts（React 编排，205 行）**。`onDecode`（L47-53）把 Float32 直接 post 给 worklet port；`onWorkletMessage`（L55-62）收 worklet 回传统计同步进 `actualAudioPlayed.current`（L58）；`decodeAudio`（L86-108）把 Opus 页 post 给 worker，transfer 列表 `[data.buffer]`（L106）**零拷贝转移**，前 5 包打印 hasOggS 魔数校验（L93-99）；socket 效果（L123-139）：connected 且 decoderReady 才 reset worklet（L128）并 `startRecording()`（L130）；worker 生命周期效果（L148-196）：优先 `getPrewarmedWorker()`（L154），否则新建并 `initDecoder`（L177），卸载 terminate（L187-195）。

**上行采集**。`useUserAudio.ts`：`UserMediaStatuses` 七态枚举（L6-14）；`startRecordingUser`（L53-124）拿流后建 analyser（L57）、麦克风波形接 stereoMerger **右声道**（L61，供混录）；recorderOptions（L67-80）：`encoderFrameSize: 20`、`encoderSampleRate: 24000`、`encoderApplication: 2049`（L78，VOIP 模式）、`streamPages: true`；`ondataavailable`（L84-94）用 `encodedSamplePosition / 48000` 更新 `micDuration`（L86，Opus 恒按 48kHz 计位）。编码 worker 路径经 `?url` 导入（L3）。

**可视化**。`AudioVisualizer.tsx`：140 bin 频谱条 + 三色渐变（L29-37）。`ClientVisualizer.tsx`：11 档色带（L13-25，中间是 NVIDIA 绿 #76B900）；RMS 强度放大 1.4 倍 clamp（L67-75），双列 10 格音量条（L32-55）。`ServerVisualizer.tsx`：圆形脉冲半径随强度（L32），connected 时中心画 #76B900 内圆（L44-50），`smoothingTimeConstant = 0.95`（L88）平滑。

## ③ 外部连接

WASM 是**约定式 fetch 链**：`decoderWorker.ts:42` 引用 `/assets/decoderWorker.min.js`，在 `client/public/assets/` 里不经 Vite 打包；二进制 grep 实证 min.js 内部再 `fetch("decoderWorker.min.wasm")` 并 `WebAssembly.instantiate`——js/wasm 必须成对留在 public/assets，移动即断链。上游：Queue 的 `startProcessor`（`Queue.tsx:164-183`）建 AudioContext（L166）、prewarm（L169）、`addModule(moshiProcessorUrl)`（L179，`Queue.tsx:1` 以 `?worker&url` 导入）、connect(destination)（L182）；各节点经 MediaContext 注入（`MediaContext.ts:2-11` 七个 ref）。

## ④ 数据流

一条下行帧的旅程：WS arraybuffer → `useServerAudio.onSocketMessage`（L110-121）decode 出 audio → `decodeAudio` post（transfer buffer）→ WASM worker 解 Opus 得 Float32 → `onWorkerMessage`（L75-83）→ `onDecode` post 给 worklet port → MoshiProcessor 入队/缓冲/淡入淡出 → process 填 output → destination 出声；worklet 另接 analyser（`useServerAudio.ts:33`）供可视化。时序：首页 Connect → AudioContext + prewarm（WASM 与授权并行）→ 会话页 → getPrewarmedWorker → decoderReady → connected → reset + startRecording → 双向流启动。

## ⑤ 设计决策

- **双离渲染线程**：解码在 Web Worker、播放调度在 AudioWorklet、主线程只做 UI——20ms 帧率不丢音的前提。
- **预热单例一次性消费**（L132-136）：每次连接独占已初始化 worker，状态不串味。
- **双向自适应抖动缓冲**：欠载加 partial（L170-171）、溢出加 maxBuffer（L65-66），initState 打回 10ms（L96-98）每会话重新学习。
- **transferable 零拷贝**（L106）避免每帧 960 样本的 GC 压力。
- 上行直接产 Opus 页（24000Hz + streamPages），服务端免转码直喂 LM。

## ⑥ 新人提示（坑与勘误）

- **"就绪"是计时器不是事件**：预热 1000ms、init 1000ms、warmup 100ms 全是 setTimeout（L102/L65/L154-157），worker 从不回执。慢网下 WASM 未加载完就被标 ready，首包被 `decodeAudio` 丢弃（L87-90）或解码失败——排查"开局几秒没声"先看这里。
- **hasCriticalDelay 是半成品**：`useServerAudio.ts:37` 声明、L202-203 暴露 setter，但全仓**无人置 true**（只有 ServerAudio.tsx:22 的 Dismiss 置 false）——"连接异常已重连"横幅（ServerAudio.tsx:17-29）永不自现。
- `audio-processor.ts:1` 整文件 `@ts-nocheck`；L133 与 L69 的 `let delay` 声明后未用，类型检查全关从未报错。
- `useServerAudio.ts:33` 的 `worklet.current.connect(analyser.current)` 写在渲染体里每渲染执行——靠 connect 幂等才无害；L62 `port.onmessage` 同样每渲染覆盖。
- wasm/js 必须成对放 `public/assets/`（见③），最易被"清理静态资源"误伤。
- opus-recorder `bufferLength` 注释（useUserAudio.ts:63-66）自曝：对单声道无实际作用，影响分帧的是 frameSize/maxFramesPerPage。
