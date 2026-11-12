# 11 · 会话页组件树：Conversation 编排、ServerInfo/TextDisplay 面板与 useModelParams

## ① 角色定位

`Conversation.tsx`（296 行）是全链路编排者：把温度/top-k/种子/提示词拼进 WS URL、实例化 useSocket、装配 SocketContext/MediaContext 双 Provider、组合五个功能面板（ServerAudio 播放、UserAudio 采集、TextDisplay 流式文本、ServerAudioStats 统计、ServerInfo 服务端配置），并额外维护一条**旁路 MediaRecorder** 把整场对话混录成可下载文件。改 UI 从这棵树入手；改参数语义从 `useModelParams.ts` 入手。

## ② 内部结构

**Conversation.tsx**。Props（L17-29）：`workerAddr`/`workerAuthId`/`email`/`theme`、由 Queue 注入的 `audioContext`/`worklet` 两个 ref（L24-25）、可选 `onConversationEnd`/`isBypass`/`startConnection`，以及 `...Partial<ModelParamsValues>`（L29，Queue 用 `{...modelParams}` 全量展开注入）。

- **buildURL**（L32-76）：`workerAddr` 为 "same" 或空时归一成当前 host:port（L48-53）；协议随页面 https→wss（L55）；路径 `/api/chat`（L56）；可选 `worker_auth_id`/`email`（L57-62）+ 12 个采样参数逐个 append（L63-73：text_temperature、text_topk、audio_temperature、audio_topk、pad_mult、text_seed、audio_seed、repetition_penalty_context、repetition_penalty、text_prompt、voice_prompt）。`textSeed`/`audioSeed` 用 `useMemo` 每会话随机一次（L113-114，上限 1e6）。
- **参数态**：`useModelParams(params)`（L109）接收 Queue 传值作初值。
- **socket 接线**：`onDisconnect` 回调（L125-129，setIsOver + stopRecording）；`useSocket({uri: WSURL, onDisconnect})`（L131-135）；挂载即 `start()`（L155-160）。
- **旁路录音**：`audioStreamDestination`（L104）+ 2 通道 `stereoMerger`（L105）+ MediaRecorder 128kbps（L106）；`startRecording`（L162-183）做立体声路由——先把旧连接断干净（L170-174 try/catch），worklet 接 merger **左声道**（L176，AI 声音）、merger 接 destination（L178），再启动 MediaRecorder（L181）；右声道由 useUserAudio 接麦克风（10 篇）。`stopRecording`（L185-199）反向拆链。onstop 里 webm 容器走 `fixWebmDuration` 修时长（L143-147），产出下载链接（L148、L275）。
- **交互**：`onPressConnect`（L201-212）——会话已结束则整页 reload（L202-204），否则 connected 时 stop、未连时 start；状态灯三色（L214-222，绿 #76b900）；按钮文案机（L224-233）。
- **Provider 树**（L236-289）：SocketContext.Provider（L236-242）→ 主网格 → `audioContext.current && worklet.current` 时挂 MediaContext.Provider（L254-265，七个 ref/函数）→ ServerAudio（L267-272，注入 setGetAudioStats 回调注册器）+ UserAudio（L273）+ 下载链接（L274-276）+ TextDisplay（L278-280，容器 ref 传入）+ ServerAudioStats（L281-283）→ 树外底部 ServerInfo（L286）。

**子组件**。`ServerInfo.tsx`：拿 useServerInfo，无数据即 null（L5-7），有则展示十项服务端配置（L10-19，含 lm_model_file/instance_name——部署排障第一现场）。`TextDisplay.tsx`：useServerText 的文本数组逐段渲染（L27-34），当前最后一段加粗（L30）；text 变化即平滑滚到底（L15-23）。`ModelParams.tsx`（85 行）：**注意它是死代码**（见⑥），结构上用 modal 本地暂存 voice/text prompt（L25-26）、18 音色下拉（L41-58）、Reset/Validate 双按钮（L65-81）。`Controls.tsx`（28 行）：BOS/EOS 按钮，直接 send testMessages 常量（L11-17）——同样死代码。

**useModelParams.ts（154 行）**。默认值常量（L4-13）：text 0.7/25、audio 0.8/250、padMult 0、repetition context 64/penalty 1.0、教师人格默认提示词（L11）、默认音色 NATF0.pt（L12）。`ModelParamsValues` 十字段（L15-26）。useState 初始化用 `params?.x || DEFAULT`（L32-40），仅 `randomSeed` 走 `useLocalStorage`（L41，跨会话记忆）。`resetParams`（L43-59）只还原 7 个数值参数；`setParams`（L61-83）全量覆盖（Queue 表单的提交入口）。包装 setter（L85-128）带"范围校验"。

## ③ 外部连接

上游 Queue：`{...modelParams}` 展开 + audioContext/worklet refs 注入（`Queue.tsx:196-203`）。下游：MediaContext 被 useUserAudio/useServerAudio 消费；SocketContext 被 ServerAudio/UserAudio/TextDisplay 及可视化消费；ServerAudioStats 通过 `getAudioStats` ref 回调（L93-100 初始兜底值 + L268-270 注册）拉 worklet 统计。getMimeType/getExtension（`getMimeType.ts:55-70`）决定录音容器与扩展名。

## ④ 数据流

参数流：Queue 首页表单 → modelParams state → Conversation props → buildURL → **WS URL 查询串** → 服务端握手时读取定型——此后客户端改任何参数都不生效（UI 用 `disabled={isConnected}` 防呆，ModelParams L34/L40）。音频流经 MediaContext 的 refs 直通 worklet（10 篇）；文本/元数据流经 SocketContext（09 篇）；统计流：worklet → useServerAudio.getAudioStats → ServerAudioStats 每 141ms 轮询（`ServerAudioStats.tsx:38-46`）+ 0.85 系数滑动平均（L21、L41-44）。

## ⑤ 设计决策

- **参数即 URL**：采样配置在握手一刻固化，免协议消息、免运行时同步，服务端实现也最简单。
- **音频基建跨页存活**：AudioContext/worklet 由 Queue 创建、经 props 注入——会话组件重挂不影响音频图，是"refs 而非 context/state"的典型取舍。
- **旁路混录左 AI 右人声**：stereoMerger 双声道设计让下载的录音天然分轨，后期可单独消音。
- **getAudioStats 注册器模式**：子组件把取值函数注册进父级 ref，父级定时轮询——避免统计数字高频 setState 打爆渲染。

## ⑥ 新人提示（坑与勘误）

- **useModelParams 校验恒真（钉版勘误）**：七个数值 setter 的条件全是 `value <= MAX || value >= MIN`（L86、L91、L96、L101、L106、L111、L116）——任何值都至少满足一侧，`||` 应为 `&&`。例如 `value <= 1.2 || value >= 0.2`（L86）对 99.9 也成立。**范围校验完全失效**，ModelParams 的"Validate"按钮名存实亡（好在参数真正消费方是服务端 URL，坏值会被服务端拒）。
- **buildURL 内嵌 useMemo 违反 hooks 规则**：`Conversation.tsx:47` 在普通函数 buildURL 里调 `useMemo`。当前恰好每渲染调用一次（L116）所以能跑，但任何人把它挪进事件回调（如 onPressConnect）就会在渲染外调 hook 而崩溃——重构前先拆出来。
- **ModelParams.tsx 与 Controls.tsx 是死组件**：grep 实证全仓零 import；18 音色清单因此在死组件（L41-58）与 Queue 的 VOICE_OPTIONS（`Queue.tsx:11-16`）**双份维护**，加音色要改两处（实际只需改 Queue 那份）。
- **startConnection prop 声明未用**：L28 定义、L87 解构，函数体零引用——Queue 传它只是历史遗留。
- `resetParams`（L43-59）不清 textPrompt/voicePrompt/randomSeed，且 L49-50 调的是带（失效）校验的包装 setter 而 deps 列的是 Base setter——命名错位但行为等价。
- 挂载即连（L155-160）与 onPressConnect 的重连逻辑并存：会话结束后唯一出路是 `window.location.reload()`（L203），整页刷新重置一切 refs——简单粗暴但意味着无状态保留的会话循环。
