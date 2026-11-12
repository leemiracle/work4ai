# 02 · Chat.tsx：1850 行中枢——WS 生命周期、流式渲染、标签剥离

## 角色定位

`components/Chat/Chat.tsx`（1850 行）是全仓最大单文件，聊天界面的一切运行时行为都从这里出发：WebSocket 连接管理、HTTP 双发送链路、五类入站消息分发、SSE/NDJSON 流式解析、私有标签剥离、OAuth/交互模态调度、滚动跟随。它身兼「协议客户端」与「UI 编排器」双职——但状态变换刻意全部外委托给纯函数层，自己只做 wiring。

## 内部结构

**模块级流式解析器**（组件外，可单测）：`normalizeNewlines` 折叠 CRLF/CR（`Chat.tsx:75-78`）；`extractSsePayloads` 按空行切 SSE 事件块、只留 `data:` 行、忽略 [DONE] 哨兵（`Chat.tsx:80-112`）；`splitNdjson` 按行切 NDJSON（`Chat.tsx:114-121`）；`tryParseJson` 静默解析（`Chat.tsx:123-129`）；`parsePossiblyConcatenatedJson` 用花括号深度计数拆分被拼接的顶层 JSON 对象（`Chat.tsx:154-179`）；`getWebSocketCustomPayload` 从 sessionStorage 读自定义 WS 参数（`Chat.tsx:181-200`）。

**连接生命周期**：`connectWebSocket`（`Chat.tsx:391`）先 `getCookie` 取 session（`Chat.tsx:397-401`），拼 URL 时注入 `?session=`（`Chat.tsx:406-410`）与 `conversation_id` 重连续传（`Chat.tsx:413-417`）；自定义 query 直接拼、自定义 headers 经 btoa 编成 `_ws_headers`（`Chat.tsx:479-482`，网关解码端成对）。onopen 即发 OAuth 偏好帧（`Chat.tsx:514`）并从 sessionStorage 恢复 activeUserMessageId（`Chat.tsx:516-525`）；onclose 递归重连最多 3 次、间隔 1s（`Chat.tsx:392-393`、`Chat.tsx:550-559`），耗尽后关 loading 态并 toast（`Chat.tsx:563-575`）。`handleStopConversation` 双模式分治：WS 清 activeUserMessageId、HTTP abort controller（`Chat.tsx:261-290`）。

**入站分发**：`handleWebSocketMessage`（`Chat.tsx:819`）顺序——OAuth consent 校验 URL 后开流程（`Chat.tsx:820-840`）→ 裸 `user_auth_error` 静默停流（`Chat.tsx:843-850`）→ 结构+conversation_id 校验（`Chat.tsx:851-865`）→ activeUserMessageId/conversationId 双过滤丢迟到消息（`Chat.tsx:867-876`）→ complete 状态延迟 200ms 收尾（`Chat.tsx:880-890`）→ interaction 开模态（`Chat.tsx:893-895`）→ 四个 process* 纯函数串行变换 messages（`Chat.tsx:935-941`）→ `applyMessageUpdate` 更新标题（`Chat.tsx:944-947`）→ `updateRefsAndDispatch` 落盘（`Chat.tsx:955-959`）。

**HTTP 链路与标签剥离**：`handleSend`（`Chat.tsx:962`）WS 优先（`Chat.tsx:1013-1124`，帧构造 `Chat.tsx:1096-1107`），否则按端点选 builder（`Chat.tsx:1130-1159`）fetch（`Chat.tsx:1165-1174`）。流式 reader 循环里：generate 端点走 SSE→NDJSON→纯文本三级探测（`Chat.tsx:1283-1321`）；**标签剥离三段式**——完整 `<observabilitytraceid>` 正则抽取并删除（`Chat.tsx:1339-1363`）、残缺 `<intermediatestep>` 半标签存 `partialIntermediateStep` 等下个 chunk 拼回（`Chat.tsx:1333-1336` 与 `Chat.tsx:1366-1378`）、完整标签解析成步骤对象并从正文删净（`Chat.tsx:1381-1408`）；workflow 错误 JSON 转加粗错误文案（`Chat.tsx:1410-1416`）；首 chunk 建助手消息、后续 chunk 更新末条（`Chat.tsx:1419-1498`）。422 错误渲染进气泡而非 toast（`Chat.tsx:1181-1220`）。

## 外部连接

上游消费 HomeContext 十一个状态字段（`Chat.tsx:203-220`）；下游把渲染交给 MemoizedChatMessage（`Chat.tsx:1804-1810`，空气泡由 `chatTransform.ts:154-164` 的守卫挡掉）、输入交给 ChatInput（`Chat.tsx:1818-1839`）、HITL 交给 InteractionModal（`Chat.tsx:1840-1845`）。协议层 import types/websocket 的守卫族（`Chat.tsx:38-50`）与 const.ts 的消息类型表（`Chat.tsx:13-17`）。

## 数据流

WS 模式：用户消息 → `handleSend` 组 user_message 帧 → onmessage → 分发器 → 纯函数变换 → ref 写穿+dispatch+sessionStorage 双写（`Chat.tsx:648-670`）。HTTP 模式：fetch 流 → 字节级标签剥离 → 步骤树合并（`Chat.tsx:1424-1433`）→ 助手消息增量更新。停止生成：activeUserMessageId 置 null 后，所有后续入站消息在 `Chat.tsx:871-876` 被静默丢弃。

## 设计决策

①**ref 写穿**（`updateRefsAndDispatch`，`Chat.tsx:648-670`）先改 ref 再 dispatch——WS 高频消息在 React 批处理延迟期内也能读到最新 conversations，绕开闭包陷阱；②**变换全外置**：chatTransform.ts 172 行纯函数使最复杂的状态逻辑可独立测试，组件只剩编排；③**半标签缓冲**而非整流缓冲：内存只存一个残段，长流式不膨胀；④**OAuth 偏好帧连接即发**（`Chat.tsx:510-514` 注释）：redirect 模式导航走会丢排队帧，open 时刻是唯一安全窗。

## 新人提示

改消息处理先看 `chatTransform.ts` 是否已有对应纯函数，**不要**在 handleWebSocketMessage 里内联写变换；流式相关 bug 先读 `__tests__/components/Chat.streaming-edge-cases.test.tsx`（本地复刻了半包重组逻辑验证残缺标签）；`Chat.tsx:1244` 有一处 `if (!false)` 死代码——非流式分支（`Chat.tsx:1523-1556`）实际不可达，读代码时跳过；新增 state 记得同时进 `Chat.tsx:1569-1581` 的 useCallback 依赖数组，漏了就是过期闭包 bug。
