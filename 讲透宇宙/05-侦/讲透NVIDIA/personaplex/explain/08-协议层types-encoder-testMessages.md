# 08 · 协议层：client/src/protocol/ 的二进制 WS 消息契约

## ① 角色定位

`protocol/` 三文件（types.ts / encoder.ts / testMessages.ts）定义了浏览器与 moshi 服务端之间 WebSocket 上的**二进制消息契约**：每条消息是"1 字节类型标签 + 变长 payload"，编解码全部在这 89 行 encoder 里手工完成，没有 protobuf/JSON 框架。前后端所有交互——握手、音频帧、流式文本、控制动作、元数据、错误、保活——都走这一套。它是客户端里少数与服务端逐字节耦合的模块，改一个标签值就是破坏性变更。

## ② 内部结构

**types.ts：类型契约**。核心是 `WSMessage` 判别联合（`types.ts:20-48`），共 7 个分支：handshake（L21-25，携带 version/model）、audio（L26-29，`data: Uint8Array`）、text（L30-33）、control（L34-37，携带 action）、metadata（L38-41，`data: unknown`）、error（L42-45）、ping（L46-48，无载荷）。辅助契约：`VERSIONS_MAP`/`MODELS_MAP`（`types.ts:8-14`）目前都只有 `0: 0b00000000` 一个键，是协议版本演化的预留位；`SocketStatus` 三态（`types.ts:51`：connected/disconnected/connecting）；`CONTROL_MESSAGES_MAP`（`types.ts:53-58`）定义 4 个控制动作：`start=0b000`、`endTurn=0b001`、`pause=0b010`、`restart=0b011`。`types.ts:1-6` 另有 `MessageType` 字符串字面量联合（5 种）。

**encoder.ts：编解码**。`encodeMessage`（`encoder.ts:9-33`）按类型打标签：handshake 编成 3 字节 `[0x00, version, model]`（L12-16）；audio 是 `[0x01, ...data]` 直接拼接 Opus 页（L18）；text/control 分别为 0x02（TextEncoder，L20）与 0x03 两字节（L22）；metadata 先 `JSON.stringify` 再 UTF-8 编码（L24-27）；error 用 0x05（L29）；ping 是单字节 0x06（L31）。`decodeMessage`（`encoder.ts:35-89`）取 `data[0]` 分流（L36-37）：handshake 分支**不读 payload**，version/model 硬编码返回 0（L39-45）；control 分支反查 `CONTROL_MESSAGES_MAP` 找到值等于 `payload[0]` 的键（L56-59），查不到直接 throw（L61-64，且留着一行 `//TODO: log this and don't throw`）；metadata 分支 `JSON.parse`（L73）；未知标签落到 default 分支 throw（L84-87）。

**testMessages.ts：预置常量**。六个导出（`testMessages.ts:3-32`）：`handshakeMessage`、`audioMessage`（10 字节零填充，L9-12）、`textMessage`、`controlBOSMessage`（action: start，L19-22）、`controlEOSMessage`（action: endTurn，L24-27）、`metadataMessage`。

## ③ 外部连接

编码侧唯一入口是 `useSocket.sendMessage`（`useSocket.ts:18-27`，见 09 篇）：UserAudio 的麦克风 chunk、Controls 的控制消息都经它编码后 `socket.send`。解码侧是**扇出式**消费：`useSocket.onMessageEvent`（`useSocket.ts:52-67`）解一次用于握手判定，`useServerAudio.ts:110-121`、`useServerText.ts:10-17`、`useServerInfo.ts:67-77` 三个 hook 又各自在原生 message 事件上解一次——同一帧最多被 `decodeMessage` 四次。服务端对端是 `moshi/moshi/server.py:460` 注册的 `/api/chat` WebSocket 路由（aiohttp），两侧共用同一套首字节标签约定（服务端侧详见组 1 文章）。

## ④ 数据流

上行：`UserAudio.onRecordingChunk`（`UserAudio.tsx:22-33`）产出 Opus 页 → `sendMessage({type:"audio"})` → `encodeMessage` 拼出 `[0x01, ...opus帧]` → WS 发送。下行：arraybuffer 到达 → `new Uint8Array(eventData.data)` → `decodeMessage` 按 `data[0]` 还原成 WSMessage → 各消费方按 `message.type` 分发（audio 进解码 worker、text 进流式文本、metadata 进 zod 校验）。握手方向值得注意：客户端 open 后**不主动发握手**，而是等服务端推来 handshake 帧才把状态置为 connected（`useSocket.ts:57-60`）——握手是服务端发起的"可以开始说话了"信号。

## ⑤ 设计决策

- **单字节标签 + 零 header 直拼**：音频路径每帧只多 1 字节，对 20ms 一帧的实时流几乎免费。
- **判别联合 + 穷尽 switch**：`encodeMessage` 的 switch（L10-32）没有 default 分支——TS 编译器保证 7 种类型全覆盖，将来加第 8 种消息时漏写 case 会直接编译报错。
- **metadata 走 JSON-in-binary**：低频通道（服务端配置下发）用自描述格式，高频通道（audio）用裸字节，按频率分配序列化成本。
- 控制动作用查表反解而非 switch，新增动作只改 map 一处（L57-59）。

## ⑥ 新人提示（坑与勘误）

- **MessageType 落后 WSMessage 两个版本**：`types.ts:1-6` 的 `MessageType` 只有 5 种（handshake/audio/text/control/metadata），缺 error 与 ping；且 grep 实证它**全仓零消费**——只有定义没有 import，纯死导出。真实契约以 WSMessage 7 分支为准。
- **testMessages 名不副实**：它不是测试夹具，`controlBOSMessage`/`controlEOSMessage` 被生产组件 Controls.tsx 引用（`Controls.tsx:1-4`）当常量用；反倒是 `audioMessage`/`textMessage`/`metadataMessage` 三个无人消费。当然 Controls 本身也是死代码（11 篇）。
- **handshake 解码是假解码**：L42-43 把 version/model 写死 0，payload 里的真实字节被丢弃——服务端将来真发非零版本号时客户端无感知。
- **control 坏帧会炸监听器**：`encoder.ts:63` 的 throw 发生在 message 事件回调里，而所有订阅方（useSocket L52-67、三个 hook）都没有 try/catch 包裹 decodeMessage——一个非法控制帧会让本轮及后续处理中断。
- ping（0x06）只有 encode 没有 UI/心跳消费者；结合 useSocket 的 10 秒看门狗（09 篇）看，保活策略实际依赖"服务端持续有消息"而非 ping/pong 机制。
