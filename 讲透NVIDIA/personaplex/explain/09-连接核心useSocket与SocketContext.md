# 09 · 连接核心：useSocket 状态机、SocketContext 与服务端数据 hooks

## ① 角色定位

`useSocket.ts`（125 行）是会话页的心脏：它管理 WebSocket 从建立到断开的完整生命周期——三态状态机、10 秒无消息看门狗、陈旧连接防御——并把 `sendMessage` 与连接状态暴露出去。`SocketContext.ts` 把这三样下发整棵组件树；`useServerText`/`useServerInfo` 则示范了下游如何绕过 React 状态、直接在 socket 原生事件上自订阅消费。理解这篇是理解"为什么音频不卡"的前提：所有实时数据都不经过 React 渲染循环。

## ② 内部结构

**useSocket.ts**。签名（L5-13）接收 `{onMessage, uri, onDisconnect: onDisconnectProp}`。内部状态三件套：`lastMessageTime` ref（L14）、`socketRef` ref（L15，注释明言用 ref 保持 socket 引用稳定）、`socketStatus` useState（L16，初始 disconnected）。

- `sendMessage`（L18-27）：`socketStatus !== "connected"` 时打印日志静默丢弃（L20-23），否则 `encodeMessage` 后发送——协议层（08 篇）的唯一上行入口。
- `onConnect`（L29-32）：open 事件只把状态置 **connecting**，注释"connected, now waiting for handshake"——TCP 通了但还没拿到服务端握手帧。
- `onMessageEvent`（L52-67）：刷新 `lastMessageTime`（L54），decode 后若 `type == "handshake"` 才置 connected（L57-60，日志"let's rocknroll"），再转交可选的 `onMessage` 回调。
- `onDisconnect`（L34-50）：见勘误节，含陈旧连接防御（L41-49）。
- `start`（L69-84）：若已有 socket 先 close 旧的（L71-74）；新建 `WebSocket(uri)` 并设 `binaryType = "arraybuffer"`（L76，二进制协议的前提）；挂 open/close/message 三个监听（L77-79）后写入 `socketRef`。
- `stop`（L86-97）：close + 置 null + 状态归 disconnected；L92-94 被注释掉的 `onDisconnectProp()` 说明手动停止**刻意不触发**断开回调。
- 看门狗 `useEffect`（L99-115）：仅在 connected 时启动，每 500ms 轮询（L109），`Date.now() - lastMessageTime > 10000` 即 close（L104-106）——靠"最近消息时间"而非心跳包判活。

返回值（L117-124）：`socketStatus`、`socket: socketRef.current`（渲染期快照）、`sendMessage`、`start`、`stop`、`setSocketStatus`。

**SocketContext.ts**。`SocketContextType`（L4-8）只暴露 status/socket/sendMessage 三项；`createContext` 默认值（L10-14）是 disconnected + null + no-op，保证 Provider 之外误用不炸；`useSocketContext`（L16-18）标准封装。

**消费 hooks**。`useServerText.ts`：自建 message 监听（L10-17），`type === "text"` 时追加进数组并计数；`useEffect`（L19-29）在 socket 引用变化时**先清空文本再重订阅**——重连即新会话。`useServerInfo.ts`：zod schema `ServersInfoSchema`（L6-28）校验 metadata 里的 8 个采样参数 + `instance_name` + 11 字段 `build_info`（git/rustc/cargo 全量构建信息）；`parseInfo`（L30-37）safeParse 失败返回 null 只打 console；监听逻辑同款（L67-89）。

## ③ 外部连接

上游：`Conversation.tsx:131-135` 实例化 useSocket（uri 是 buildURL 拼出的 WS 地址，onDisconnect 是 L125-129 的回调）；`Conversation.tsx:236-242` 用 SocketContext.Provider 下发。下游五处消费 context：useServerAudio（10 篇）、useServerText、useServerInfo、UserAudio（发音频）、ServerVisualizer（connected 才画内圆，`ServerVisualizer.tsx:44`）。协议层 encoder/types 是它的直接依赖。

## ④ 数据流

状态机全貌：`disconnected --start()--> [open事件] connecting --handshake帧--> connected --close/stop/看门狗--> disconnected`。UI 侧对应三色灯（`Conversation.tsx:214-222`：绿 #76b900 / 橙 / 红）。消息数据流不进 React：一个 arraybuffer 到达后被 useSocket（握手判定）、useServerAudio（音频）、useServerText（文本）、useServerInfo（元数据）各自监听并各自 `decodeMessage` 一次——**每帧最多解码四次**，换取的是各消费方完全独立、无需中央分发器、也避免了高频音频帧触发 re-render。

## ⑤ 设计决策

- **connecting 中间态**：open≠可用，必须等服务端握手（带上最终采样配置）才算就绪，避免客户端在服务端未就绪时灌音频。
- **ref 持 socket**：socket 不是 React 状态，重连不依赖组件重渲染；context 里的 socket 快照随 status 变化引发的渲染自然刷新。
- **陈旧连接防御**（L41-49）：重连竞态下旧 socket 的 close 事件迟到，只有 `socketRef.current === closedSocket` 时才清理并回调，否则按 stale 忽略——start() 先关旧（L71-74）再建新的模式配合这层判断构成完整的重入安全。
- **看门狗不依赖 ping**：直接用 lastMessageTime，实现零协议依赖（代价见 08 篇勘误）。
- **上下文最小面**：context 只给三项，start/stop 留在 Conversation 层，避免子组件随意拉扯连接。

## ⑥ 新人提示（坑与勘误）

- **onDisconnectProp 双调用（钉版勘误）**：`onDisconnect` 里 L38-40 **无条件**调一次 `onDisconnectProp()`；随后 L42-46 的 current-socket 分支里 L46 又调一次 `onDisconnectProp?.()`。自然断开与看门狗路径（socketRef 未被清空，`socketRef.current === closedSocket` 成立）会触发**两次**回调——Conversation 的回调（L125-129）里 `setIsOver(true)` 天然幂等、`stopRecording` 有 `isRecording` 守卫（`Conversation.tsx:188-190`），侥幸无害；但任何未来接入的非幂等回调（打点、弹窗）都会重复执行。手动 `stop()` 路径因 socketRef 已置 null 只触发 L38-40 那一次。同理 L37 与 L45 对 `setSocketStatus("disconnected")` 也重复调用。
- **sendMessage 的竞态窗口**：依赖 `socketStatus` 状态快照（L20），握手刚完成的极小窗口内旧闭包仍会拒发——音频首帧偶发丢失可先查这里。
- 看门狗 effect 的依赖数组含 `onDisconnect`（L115）但效果体内并未使用它（只在 L107 注释里），属于误导性依赖。
- `useServerInfo` 的 zod schema（L6-28）与手写 `ServerInfo` 类型（L39-61）双份维护，未用 `z.infer`——服务端加字段要改两处。
- 下游 hook 的监听器依赖 `socket` 快照，若某次重连没有引起渲染（理论上 status 未变），旧 socket 上的监听不会迁移——当前时序下 status 必变所以不触发，但这是隐式耦合。
