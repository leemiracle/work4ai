# 09 · 渲染层对话流：SSE 事件到 React 状态到像素

> 前篇（07 goosed SSE 后端 / 08 桌面主进程）讲到 goosed 的二代事件总线带着 512 条重放缓冲和单调 seq 跑在自签名 HTTPS 上。本篇顺着同一条河的下游走：事件离开 goosed 的 SSE 帧之后，如何在 Electron 渲染进程里被解析成 React 状态、再变成用户看到的消息气泡。这是整条链路中离用户最近、也最容易被低估复杂度的一段。

**先钉一处路径勘误**：任务书与部分旧资料写的 `ui/desktop/src/renderer/` 目录在本仓**不存在**。渲染进程应用层直接平铺在 `ui/desktop/src/` 下——入口 `renderer.tsx`、路由壳 `App.tsx`、业务 hooks 在 `src/hooks/`、组件在 `src/components/`，与主进程文件 `main.ts`、`preload.ts` 同级。知识图谱的层 8「桌面端渲染进程应用层」（116 节点）即对应这批文件，层 9「桌面端组件库」（305 节点）对应 `src/components/` 全量。

## 角色定位

在 16 层架构里，本文覆盖层 8 与层 9 的对话流主线：`useChatStream`/`useSessionEvents` 两个 hooks + `BaseChat`→`ProgressiveMessageList`→`GooseMessage` 渲染链。它的上游是层 7（主进程 Electron 壳）与层 6（goosed HTTP/SSE 服务），下游是像素。

渲染进程的边界由 Electron 三件套切开：

- **主进程 `main.ts`** 负责 spawn goosed、生成 `X-Secret-Key`（`main.ts:733` `crypto.randomBytes(32).toString('hex')`）、做证书钉扎（`main.ts:298` `app.on('certificate-error', ...)`）；
- **preload `preload.ts`** 只做窄桥：`contextBridge.exposeInMainWorld('electron', electronAPI)`（`preload.ts:361`），其中渲染层拿后端地址与密钥只靠两个 invoke——`getSecretKey: () => ipcRenderer.invoke('get-secret-key')` 与 `getGoosedHostPort: () => ipcRenderer.invoke('get-goosed-host-port')`（`preload.ts:272-273`），主进程侧对应 `ipcMain.handle` 注册在 `main.ts:1646` 与 `main.ts:1651`；
- **渲染层**本身不再有 Node 能力，一切对 goosed 的请求走浏览器 `fetch`（hey-api 生成的 openapi 客户端），HTTPS 自签名证书的放行由主进程 `certificate-error` 事件钉扎指纹解决（见「外部连接」）。

值得强调：渲染层与 goosed 之间**没有专职 IPC 代理**——主进程只为健康检查自建过一个走 `net.fetch` 的 client（`main.ts:922` `createClient(createConfig({ baseUrl, fetch: net.fetch, ... }))`，注释明言是为了让本地自签名 HTTPS 走 session 证书处理），而聊天流量全部由渲染进程直连 goosed。主进程在数据面上是旁观者。

## 内部结构

### 会话状态：useReducer 而非 zustand

任务书猜测「store/zustand 或 context」——实测**都不对**。`package.json` 无 zustand/redux/jotai/mobx（grep 零命中）；`src/store/` 目录只有一个 30 行的 `extensionOverrides.ts`（模块级 Map 存 hub 视图的扩展开关临时覆盖，与会话无关）。对话流的全部状态是 `useChatStream.ts:418` 的 `const [state, dispatch] = useReducer(streamReducer, initialState)`，状态形状 `StreamState`（`useChatStream.ts:63-70`）共六个字段：`messages`、`session`、`chatState`、`sessionLoadError`、`tokenState`、`notifications`；12 种 action（`useChatStream.ts:72-91`）里最关键的是终态三连 `START_STREAMING`/`STREAM_ERROR`/`STREAM_FINISH`——后两者都把 `chatState` 归位 `Idle`（`useChatStream.ts:167-172`）。`chatState` 是显式状态机，七值枚举定义在 `types/chatState.ts:1-9`：`Idle/Thinking/Streaming/WaitingForUserInput/Compacting/LoadingConversation/RestartingAgent`。它是整条 UI 的总开关——输入框可否提交、加载动画显示哪种图标、能否自动滚动，全部由它派生。

跨会话切换的"记忆"靠模块级缓存 `resultsCache`（`useChatStream.ts:33` `const resultsCache = new Map<string, { messages: Message[]; session: Session }>()`）：每次 state 变更都回写（`useChatStream.ts:449-453`），切回旧会话时若命中则直接 `SESSION_LOADED` 免网络往返（`useChatStream.ts:734-756`）。

### SSE 消费：长连接 + 按 request_id 路由

`useSessionEvents.ts` 是每个会话一条的**长生命周期 SSE 连接**。核心是一个 while 重连循环（`useSessionEvents.ts:55`），参数三件套：初始退避 500ms、上限 10s（`useSessionEvents.ts:29-30`）、连续失败 5 分钟后向所有 listener 广播合成的 `Error: 'Lost connection to server'`（`TERMINAL_ERROR_AFTER_MS`，`useSessionEvents.ts:31` 与 `useSessionEvents.ts:35-53`）。连接本身调 openapi 生成的 `sessionEvents`（URL `/sessions/{id}/events`，`api/sdk.gen.ts:534`），带 `Last-Event-ID` 请求头续传（`useSessionEvents.ts:60`），每个事件到达时记录其 `id` 供下次断线重放定位（`useSessionEvents.ts:62-66`）。注意 `sseMaxRetryAttempts: 1`（`useSessionEvents.ts:61`）——生成客户端（`api/core/serverSentEvents.gen.ts:82` `export const createSseClient`，AsyncGenerator 实现）自己的重试被关到最低，重连节奏完全由 hook 外层 while 循环接管。

事件分发按 `routingId = sessionEvent.chat_request_id ?? sessionEvent.request_id`（`useSessionEvents.ts:82`）查 listeners Map；`ActiveRequests` 事件是控制面特例，直接转给 `activeRequestsHandlerRef`（`useSessionEvents.ts:84-88`）；无 routingId 的 `Error` 广播给所有已注册 listener（`useSessionEvents.ts:90-95`）。`addListener(requestId, handler)` 返回退订闭包（`useSessionEvents.ts:139-154`）。

### 提交与重挂：POST+SSE 模式

发送一条消息走"新 POST+SSE 模式"，源码注释把协议讲得很清楚（`useChatStream.ts:650-656`）：①生成 `request_id`（`uuidv7`，`useChatStream.ts:664`）→ ②**先**注册 SSE listener **再** POST（防竞态）→ ③POST `/sessions/{id}/reply` → ④事件从长连接到达。POST body 携带 `{ request_id, user_message, override_conversation }`（`useChatStream.ts:696-705`）。

最精巧的是 **ActiveRequests 重挂**（`useChatStream.ts:611-648`）：聊天视图在回复仍在服务端跑时被重挂（切 tab 再切回），新 hook 实例通过 SSE 上的 `ActiveRequests` 事件发现 in-flight 请求并接管。冷挂载时序竞态（ActiveRequests 比 `resumeAgent` 先到、消息列表还是空）有专门处理：先注册**只缓冲不处理**的 listener（`useChatStream.ts:635-637` 把事件 push 进 `pendingReattachBufferRef`），等 `resumeAgent` 返回全量会话后再 `doReattach` 重放缓冲（`useChatStream.ts:785-808`）——注释明言"events are buffered in the meantime"（`useChatStream.ts:428-432`）。

### 渲染主线

组件链：`App.tsx` 路由把 `sessionId` 经 `viewOptions` 下发（`App.tsx:194`）→ `ChatSessionsContainer.tsx:50-52` 渲染 `<BaseChat sessionId={...}>`（多会话并存、按 `data-session-id` 隐藏非当前）→ `BaseChat.tsx:120` 调用 `useChatStream({ sessionId, onStreamFinish })` 拿到全部状态与动作 → `BaseChat.tsx:454` 把 `messages` 交给 `<ProgressiveMessageList>`。

`ProgressiveMessageList` 是性能组件：长会话分批上屏，默认 `batchSize = 20`、`batchDelay = 20`ms、超过 50 条才显示加载指示（`ProgressiveMessageList.tsx:77-79`）；用户按 Cmd/Ctrl+F 搜索时立即全量渲染（`ProgressiveMessageList.tsx:207-230`）。单条消息按角色分流（`ProgressiveMessageList.tsx:288-307`）：user 走 `UserMessage`（纯 toolResponse 的用户消息不渲染），assistant 走 `GooseMessage`，且 `isStreaming` 只赋予**最后一条** assistant 消息（`ProgressiveMessageList.tsx:299-304`）。`metadata.userVisible === false` 的消息整体跳过（`ProgressiveMessageList.tsx:240`）——elicitation 应答消息就是靠这个对用户隐身的（`types/message.ts:74` `metadata: { userVisible: false, agentVisible: true }`）。

`GooseMessage.tsx`（215 行）内部分四块：正文 `<MarkdownContent content={displayText} />`（`GooseMessage.tsx:133`）、图片预览、工具调用区 `toolRequests.map` → `ToolCallWithResponse`（`GooseMessage.tsx:163-194`）、以及两种人工确认卡 `ToolCallConfirmation` 与 `ElicitationRequest`（`GooseMessage.tsx:196-209`）。连续工具调用会被 `identifyConsecutiveToolCalls` 识别成链，链内消息隐藏时间戳收紧视觉密度（`ProgressiveMessageList.tsx:233`、`GooseMessage.tsx:71-74`）。

## 外部连接

**API 面（openapi 生成客户端）**：`src/api/` 是 `@hey-api/openapi-ts` 从 `openapi.json` 生成的全家桶，`api/index.ts` 一行导出上百个函数。对话流直接消费五个：`resumeAgent` → `POST /agent/resume`（`api/sdk.gen.ts:88-90`，挂载时加载会话+扩展）；`sessionReply` → `POST /sessions/{id}/reply`（`api/sdk.gen.ts:536-538`，二代提交端点）；`sessionEvents` → `GET /sessions/{id}/events`（`api/sdk.gen.ts:534`，SSE 长连）；`sessionCancel` → `POST /sessions/{id}/cancel`（`api/sdk.gen.ts:525-527`，停止按钮）；`getSession` → `GET /sessions/{session_id}`（`api/sdk.gen.ts:547`，全量会话重载）。**两代端点并存可证**：一代 `reply` → `sse.post '/reply'`（`api/sdk.gen.ts:458-460`）仍在生成的 SDK 里，但对话主线（grep `useChatStream.ts` 全文）已不引用——与 07 篇 goosed 侧两代并存的结论互为印证。

**启动装配**：`renderer.tsx:39` `await window.electron.getGoosedHostPort()` 拿到 `https://127.0.0.1:<port>`（launcher 视图 `#/launcher` 例外，`renderer.tsx:35-38`），然后 `client.setConfig({ baseUrl: gooseApiHost, headers: { 'X-Secret-Key': await window.electron.getSecretKey() } })`（`renderer.tsx:44-49`）。这是渲染层唯一的"启动装配"动作，之后所有 SDK 调用共享这份配置。

**证书钉扎**（承接 08 篇结论并落到行号）：渲染进程 fetch 的自签名证书在主进程 `main.ts:298` `app.on('certificate-error', ...)` 放行——`pinnedCertFingerprint` 已知则精确比对（`main.ts:304-309`），未知则 TOFU：首次握手指纹直接钉住并放行（`main.ts:310-314`）。本地 spawn 的 goosed 指纹来自其 stdout，外部后端走同一条 TOFU 逻辑（`main.ts:264-272` 注释钉版）。

**与主进程 IPC 的其余部分**：对话流还会碰 `window.electron.getSetting('enableNotifications')` / `isAnyWindowFocused()` / `showNotification()`（`useChatStream.ts:470-479`，任务完成且窗口失焦时发系统通知）、`window.electron.logInfo`（`useChatStream.ts:1095`）。渲染层内部通信用 `window.dispatchEvent` 自定义事件（`AppEvents` 常量体系）：`SESSION_STATUS_UPDATE` 把 chatState 翻译成 sidebar 可消费的 `streamState`（`BaseChat.tsx:152-173`）、`MESSAGE_STREAM_FINISHED` 判定新会话名 `^\d{8}_\d{6}$`（`useChatStream.ts:485-488`）、`SESSION_FORKED` 携带新会话 ID 触发跳转（`useChatStream.ts:1087-1094`）。

**组件库依赖**：渲染应用层（层 8，116 节点）重度依赖组件库（层 9，305 节点）。对话流直接消费的核心不过十几个：`ChatInput`（1436 行的表单巨件，`ChatInput.tsx:1436` `<form onSubmit={onFormSubmit}>`）、`ProgressiveMessageList`、`GooseMessage`/`UserMessage`、`MarkdownContent`、`ToolCallWithResponse`、`ToolCallConfirmation`、`ElicitationRequest`、`ToolApprovalButtons`、`LoadingGoose`、`SearchView`。

## 数据流

一条 assistant 消息从生成到上屏的完整路径：

1. **用户输入**：`ChatInput` 表单提交 → `BaseChat.tsx:190-195` `chatInputSubmit`（带 recipe 标记）→ `useChatStream.ts:863` `handleSubmit`。守卫检查（`useChatStream.ts:868-876`）：session 存在且 chatState 不在 `LoadingConversation/Streaming/Thinking/Compacting` 四态才放行。首条消息触发 `SESSION_CREATED` 事件并启动会话命名轮询（`useChatStream.ts:886-930`，最多 20 次、500ms 间隔，仅在流式进行中继续）。
2. **本地先行**：`createUserMessage`（`types/message.ts:30-52`）构造 `{role:'user', content:[{type:'text'},...], metadata:{userVisible:true, agentVisible:true}}`，乐观插入 messages 并 `START_STREAMING`（`useChatStream.ts:939-943`）。
3. **注册+提交**：`submitToSession`（`useChatStream.ts:657`）生成 `uuidv7` request_id，`createEventProcessor` + `addListener` 先行（`useChatStream.ts:671-693`），随后 `sessionReply` POST（`useChatStream.ts:696`）。若 POST 失败且错误含 `already has an active request`，仅静默回 `Idle`（`useChatStream.ts:719-722`）——服务端单请求约束的客户端镜像。
4. **服务端**：goosed 二代总线按单调 seq 广播（`crates/goose-server/src/session_event_bus.rs:31-40`，`seq: u64` 写成 SSE `id:` 帧而非 JSON 载荷）。
5. **事件解析**：`useSessionEvents` 的 AsyncGenerator 吐出事件 → 按 routingId 找到 handler（`useSessionEvents.ts:96-103`）→ `processEvent` 的 `Message` 分支（`useChatStream.ts:310-352`）。携带 `token_state` 一并更新。
6. **合并入列**：`pushMessage`（`useChatStream.ts:179-221`）是增量协议的关键：同 id 消息的尾部 text block 直接字符串拼接（`useChatStream.ts:198`）；thinking block 若带 `signature` 则整体替换（content_block_stop 的完整块），否则拼接 delta（`useChatStream.ts:208-213`）；其余 content block push 追加。inference 元数据（含 `resolvedModel`）经 `pendingInference` 暂存，等下一条 userVisible 的 assistant 消息再补挂（`useChatStream.ts:314-328`、`282-305`）——`ProgressiveMessageList.tsx:99-102` 正是读 `metadata.inference?.resolvedModel` 来渲染"模型已切换"提示的。
7. **状态分派**：事件含 `actionRequired` 且 `actionType === 'toolConfirmation'` 或 `'elicitation'` 时，`maybeUpdateUI(..., ChatState.WaitingForUserInput, forceImmediate=true)`（`useChatStream.ts:332-343`）——forceImmediate 绕过 reduced-motion 批处理立即上屏；含 compaction/thinking 通知则转 `Compacting`/`Thinking`（`useChatStream.ts:344-347`，判定函数见 `types/message.ts:232-243`）；否则维持 `Streaming`。
8. **渲染**：`dispatch SET_MESSAGES` → `ProgressiveMessageList` → `GooseMessage`：文本走 MarkdownContent，工具请求走 `ToolCallWithResponse`；流式期间最后一条 assistant 由 `LoadingGoose` 按 chatState 显示对应动画（`BaseChat.tsx:472-481`，图标映射 `LoadingGoose.tsx:43-51`，如 Streaming 态是 `FlyingBird` 150ms 摆翅）。
9. **确认回流**：用户点 Allow Once/Always Allow/Deny → `ToolApprovalButtons.tsx:81-93` 调 `confirmToolAction`（独立 REST 端点，**不走 sessionReply**），决策记入组件级 `globalApprovalState` Map 防重放（`ToolApprovalButtons.tsx:42-49`）。而 elicitation 的应答走的是另一条路：`submitElicitationResponse`（`useChatStream.ts:950-978`）构造 `actionType: 'elicitationResponse'` 的 user 消息再 `sessionReply`——注释钉版"unblocks an in-flight tool call on the original request's SSE stream"（`useChatStream.ts:958-959`），即不开新流、不翻 chatState。
10. **终态**：`Finish` 事件 → flush 全部暂存 → `onFinish()` → `STREAM_FINISH` 归位 Idle（`useChatStream.ts:369-375`、`455-523`）。

## 设计决策

**「先注册 listener 再 POST」**（`useChatStream.ts:670-693`，注释 `650-656`）：把"提交"与"事件流"解耦成两个正交通道——POST 只管触发，SSE 长连只管收。这带来三个红利：提交天然幂等可重试；重挂（reattach）无需重新 POST，监听既有 request_id 即可；停止（`stopStreaming`，`useChatStream.ts:1022-1052`）可以同时掐两头——`abort()` 掉在途 POST（若取消赢在 POST 完成前，reply 根本不会开始）+ `sessionCancel` 带 `{request_id}` 精确取消服务端任务，且**取消总是发到发起请求的那个 session**而非当前 session（`useChatStream.ts:1032-1041` 注释：用户可能已导航走）。

**512 重放缓冲的渲染层利用**：服务端 `REPLAY_BUFFER_CAPACITY = 512`（`session_event_bus.rs:8`，broadcast 通道另 256，`session_event_bus.rs:7`）。渲染层对它的利用有两个动作：①断线时 `Last-Event-ID` 头让服务端从缓冲补发（`useSessionEvents.ts:60`）；②补不回来时服务端回 `ClientTooFarBehind`（`session_event_bus.rs:23-26`），渲染层收到含 `too far behind` 的 Error 后**不当错误处理**——`onFinish()` 结束流但不设阻塞错误屏，然后 `reloadConversation` 全量拉取会话让 UI 对齐真实状态（`useChatStream.ts:358-364` 注释钉版，`reloadConversation` 实现在 `useChatStream.ts:527-541`）。这是"流式增量优先、全量快照兜底"的双层一致性策略。

**状态就近而非全局 store**（推断，源码无注释陈述动机）：不用 zustand 而用 hook 内 useReducer + 模块级 `resultsCache`，推断是刻意让会话状态的生存期与"当前聊天视图"绑定——多会话 tab 共存时（`ChatSessionsContainer.tsx:35-36`）各视图持有独立 reducer 实例天然隔离，而跨视图共享的信号（状态更新、改名、fork）全部走 `window.dispatchEvent` 事件总线显式声明。代价是任何视图卸载即丢内存态，靠 resultsCache 补偿。

**uuidv7 而非 uuidv4**（`useChatStream.ts:664`）：时间有序 ID，推断为服务端按到达序重放/排序时免额外戳。

**reduced-motion 通道**：`prefers-reduced-motion` 用户的消息更新合并成 1 秒一批（`REDUCED_MOTION_BATCH_INTERVAL = 1000`，`useChatStream.ts:227`；`maybeUpdateUI` 三分支 `useChatStream.ts:260-280`），但确认请求强制立即（forceImmediate）。把无障碍偏好做进流式路径是少见的产品级细节。

**305 个组件的规模**：层 9 有 305 节点（知识图谱实测），但对话流核心链只占约 15 个——大头在 settings/providers/onboarding/recipes/schedule/McpApps 等设置域。推断：goose 桌面端把"聊天"做薄（一条链贯穿）、把"配置"做厚（几百个 provider/模型/权限的设置界面），组件数反映的是配置面广度而非对话流复杂度。

## 新人提示

**加一种消息类型的步骤**（以新增一种 `systemNotification` 子类型为例）：①`crates/goose-server` 侧 openapi 模型加字段 → `just generate-openapi` 重新生成 `src/api/types.gen.ts`（**永不手编 openapi.json**，AGENTS.md 红线）；②`src/types/message.ts` 加判定函数（照抄 `getThinkingMessage` 的形状，`types/message.ts:232-243`）；③`useChatStream.ts` 的 `processEvent` Message 分支若需新 chatState，在 `types/chatState.ts` 加枚举值并在 `LoadingGoose.tsx:43-51` 的两个映射表补图标与文案；④渲染侧在 `ProgressiveMessageList.getSystemNotification`（`ProgressiveMessageList.tsx:130-132`）或 `GooseMessage` 里加分支。注意 `UpdateConversation` 全量替换路径（`useChatStream.ts:376-384`）会绕过 pushMessage，新 content 类型必须在两条路径下都可渲染。

**调试**：未打包时主进程自动装 React DevTools（`main.ts:908-917`），渲染层断点打在 `useChatStream.ts:308` `processEvent` 入口可看到每条 SSE 事件的原始形状；SSE 连接健康看 `useSessionEvents` 的 `connected` state（`useSessionEvents.ts:20`）；服务端侧直接看 goosed stdout（主进程已收集为 startup diagnostics，`main.ts:944-950`）。

**坑**：①`pushMessage` 只与**最后一条**消息合并（`useChatStream.ts:180`），若服务端交错推送两条同 id 消息中间夹了别的消息，会分裂成两条——这是按顺序流假设设计的；②listener 终态自清理带 `activeRequestIdRef.current === requestId` 守卫（`useChatStream.ts:683-691`），并发提交时旧请求的清理不会误删新请求的引用，改动这段时务必保留守卫；③两代 reply 并存：改协议时确认你改的是 `sessionReply`（`/sessions/{id}/reply`）而非遗留 `reply`（`/reply`，`api/sdk.gen.ts:458`）；④`handleSubmit` 的空消息+有历史分支（`useChatStream.ts:878-937`）语义是"重发最后一条"，不是 no-op——测试时容易误触；⑤elicitation 应答消息 `userVisible: false`，在 React DevTools 的 messages 数组里看得到但 UI 不渲染，别当成丢了。

---

**本篇全部行号锚已于写盘前经 sed/grep 逐条核实**（仓库快照：/usr-data/data2/repos/aaif-projects/repos/goose，ui/desktop 源码 303 个 .ts/.tsx 于 `src/components/`）。与前篇结论的两处交叉验证：两代 reply 端点并存（渲染层 SDK 侧 `api/sdk.gen.ts:534/536` vs `458`）、证书钉扎走 `certificate-error`（`main.ts:298`）均属实。
