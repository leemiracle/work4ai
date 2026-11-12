# 03 · useServerState——前端的 WebSocket 状态机

> 源：`webui/client/src/utils/useServerState.ts`（461 行）；消费方 `components/App/index.tsx`

## 一、角色定位

useServerState 是前端**通信中枢**：单个 React hook 承担三件事——建立并持有到 Node 服务端的 WS 连接（`createWebSocket` 244-361）、把入站帧翻译成 reducer action 驱动 UI 状态（272-333 + reducer 137-217）、暴露四个出站 send 函数（401-452）。它是篇 02 WebSocketTask 的浏览器侧镜像：同款"二进制=音频旁路、JSON=结构化消息"双帧型约定（273-275 对称篇 02 的 258-261）。App 根组件以四回调换取它（`App/index.tsx:48-53`）：音频→AudioPlayer、关机/错误→Toast、barge-in→`audioPlayer.interrupt()`（40-47）。

## 二、内部结构

### 2.1 状态与动作词汇表（38-135）

`ServerState`（38-45）六字段：`messages`（对话流）、`isBotTyping`、`latestBotEmoji`（BotFace 表情）、`serverConfig`（语音支持声明）、`botList`、`connectionState`。动作枚举 `ServerStateActionType` 11 种（47-59），其中连接四态 `ConnectionState`：INITIAL/READY/ERROR/CLOSED（61-66）。每个 action 配一个带 payload 的 interface（68-122），联合成 discriminated union `ServerStateAction`（124-135）——TypeScript 可辨识联合保证 reducer 每个 case 的 payload 类型自动收窄。

### 2.2 reducer：纯函数为主，一处例外（137-217）

连接四 action 只切 `connectionState`（139-146）；BOT_TEXT 追加消息并熄灭 typing（147-152）；EMOJI 追加+更新表情（153-159）；TYPING 置位（160-164）；SENT_USER_CHAT_MESSAGE 乐观入列（199-203）；CONFIG_CHANGE/BOT_LIST 各写各字段（204-213）；default 原样返回。

**例外在 `RECEIVED_ASR`（165-198）**：先按 messageID 在既有 USER TEXT 消息里 find（170-175）；命中则**直接原地改 `message.content.text` 后 `return state`**（177-181）——不是拷贝新对象而是 mutate + 返回同一 state 引用；未命中才新建消息气泡（184-198，此路径返回新对象会触发渲染）。机制后果见第五节。

### 2.3 createWebSocket：入站分发器（244-361）

URL：hostname + `getServerPort()` + 按 `https:` 选 `wss://`（251-255）。`getServerPort`（228-242）：DEV 读 `import.meta.env`；**PROD 静态构建无法携带 build-time 变量，改读运行时注入的 `window.process.env.VITE_SERVER_PORT`**（237-238），兜底 7007。

五个监听：`open`→READY（261-263）；`message` 分发（272-333）；`close` 按 `code === 1000` 二分 CLOSED/ERROR（342-354）；`error` **注册两次**——264-270 回调弹人话错误（含端口转发提示）、335-340 派 CONNECTION_ERROR，两路都触发；`beforeunload`→`socket.close()`（356-358）保证关标签页送出关闭帧。

message 优先级链（272-333）：①ArrayBuffer→`onReceiveBotAudio(new Int16Array(...))` 直交 AudioPlayer，**不进 React 状态**（273-275）；②SYSTEM 按 CONFIG_CHANGE/SHUTDOWN 分流（280-291）；③ASR/EMOJI/TYPING/BOT_LIST/BARGE_IN 显式 case（292-327），barge-in 走回调（324-327）；④**TEXT 无显式 case 落兜底**（329-332）——bot 正文靠排除法入列。

### 2.4 hook 本体与出站函数（363-461）

`useReducer` + `socketRef`（383-385）；`useEffect` 空依赖建连（387-399），卸载 `socket.close(1000)`（398）。四个 send：`sendChatMessage`（401-420，send 后**立即 dispatch 乐观入列**）；`sendUserTyping`（422-437，只发不入列）；`sendUserAudio`（439-441，ArrayBuffer 裸发）；`toggleSpeech`（443-452，服务端模式切换触发器）。

## 三、外部连接

上游唯一消费方 `App/index.tsx:48-53`；`ConnectionState` 另被 `UserTextInput/index.tsx:22` 引用。返回值落点：`botList`/`serverConfig` 喂 AppHeader（106-109），`messages`/`isBotTyping` 喂 ConversationHistory/BotFace（112-125），`connectionState` 喂 UserTextInput（134），`sendUserAudio` 作 `useMicrophone` 采集回调（54-58）。类型全部来自 `shared/types.ts`（21-36）——前后端 schema 单源。

## 四、数据流

出站三路：提交→`App/index.tsx:69`→JSON 帧→服务端 `userFinishedMessage`；逐键→`sendUserTyping`（App:82）→TYPING 帧；麦克风→`useMicrophone`→`sendUserAudio`→二进制帧。入站两路：结构化消息进 reducer 驱动渲染；音频块走回调直达 `audioPlayer.play`（App:40）绕开状态机——**16kHz/16bit 高频帧若进 reducer 会打爆渲染管线，旁路是刚需**。终止闭环：SHUTDOWN→致命 Toast（App:41-42）；连接异常→CONNECTION_ERROR→禁用输入。

## 五、设计决策（从代码反推）

1. **音频旁路两侧对称**：服务端 258-261 与此处 273-275 同款判断——双帧型协议靠 `shared/types.ts` 单源维持。
2. **乐观 UI**：`SENT_USER_CHAT_MESSAGE`（416-419）不等服务端确认即入列——聊天回显延迟感知优先，代价是服务端失败时消息已显示（靠 Toast 报错兜底）。
3. **ASR 高频帧的渲染取舍**：165-181 的 mutate+`return state` 让增量帧跳过 React 渲染调度，是刻意的性能捷径；但 useReducer 以 Object.is 比较返回值，**同引用返回不触发重渲染**——增量字幕要等下一次"返回新对象"的 action（新建气泡、bot 回复、typing 置位）才顺带上屏。React 严格模式下 reducer 应为纯函数，此处违反；改这段前先理解为什么（speech 模式 ASR 帧速率）。
4. **TEXT 走兜底而非显式 case**（329-332）：分支链按"特殊→一般"排序，正文是最常见消息故放最后省一次比较——但加新 content 类型时若插错位置会被兜底吞成 bot 文本，需警惕。
5. **双 error 监听**（264-270 + 335-340）：一个管用户感知（Toast）、一个管状态机（ERROR 态），职责分离但源码读起来像重复注册——是有意的两路。
6. **PROD 端口运行时注入**（228-242）：静态构建的 SPA 无法预知部署端口，`window.process.env` 注入是 Vite 生态少见的操作，改部署脚本时别弄丢这个注入。

## 六、新人提示

- **改消息协议三处联动**：`shared/types.ts`（schema）→服务端 WebSocketTask（listen/handle 对）→本文件 272-333 分发链 + reducer case；漏一处就是静默丢消息（兜底 case 会把未知类型误当正文）。
- **给 App 加状态别开第二条 WS**：所有通信都在这一个 hook 里；新需求优先加 action/回调，而非新连接。
- **调试连接**先看 Toast 文案（267 含端口转发提示）与 `connectionState`——CLOSED 是正常结束，ERROR 才是故障。
- **ASR 字幕"不刷新"先读第五节第 3 条**再动手：多数情况不是没收到帧（log 在服务端 397），而是渲染未被触发。

## 甄别记录

图谱 summary 称此文件为"WS 状态机"，与源码一致；RECEIVED_ASR 的 mutate 行为为本轮源码精读发现，图谱未记载，已按源码如实表述。
