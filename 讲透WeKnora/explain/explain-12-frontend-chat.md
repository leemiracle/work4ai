# explain-12 · frontend/src/views/chat/index.vue — 聊天主界面编排器

```
文件路径: frontend/src/views/chat/index.vue
行数:     2004 行（template L1-186 / script setup L187-1600 / style L1601-2004）
所属层:   前端应用层（layer:frontend）
一句话:   RAG 问答与 Agent 模式的用户侧统一入口——SSE 流式渲染、会话切换、消息插话（steer）、追问建议、引用抽屉与沙箱面板全在此编排。
```

## 一、角色定位

用户与 WeKnora 对话的一切都发生在这个视图：路由 `/platform/chat/:chatid` 的宿主、新建会话的落点，并以 `embeddedMode` 复用于公开智能体嵌入页（props 注入 agent/KB，绕过全局 store，L243-248、L298-300）。它决定一次提问如何组装检索范围与端点（快问快答 `/api/v1/knowledge-chat` vs Agent `/api/v1/agent-chat`，L1381）、SSE 块如何落进消息列表、切换/刷新时如何恢复未完成的生成。属 L9 前端应用层核心视图，是 5.x 聊天系统与 7.x 前端两簇节点的交汇处。

## 二、内部结构

**1. Template（L1-186）**：根 div 按嵌入/引用抽屉/沙箱面板三状态切 class 并注入 CSS 变量（L2-6）；顶栏 ChatHeader + 沙箱开关（L7-24）；骨架屏与新会话推荐问题卡（L30-92）；消息循环 `:key="session.id"` 上方有一段血泪注释（L93-100）——用索引作 key 会让历史加载时整个列表销毁重建、白屏蔓延；用户/助手气泡由 `usermsg`/`botmsg` 渲染（L107-140）；`InputField` 暴露 send/steer/stop 三组事件（L154-164）；悬浮层含浏览器任务预览与问题 minimap（L169-173）；四个全局抽屉/面板（L176-185）。

**2. 流态机委托（L778-878）**：核心流处理已抽到 `useChatStreamHandler`，本文件拿回 `processStreamChunk`/`handleMsgList` 等 7 个函数并用 9 个回调定制——`onAfterMsgList`（L799-848）在历史加载后发现未完成的助手消息时自动 continue-stream 续流（IM 渠道改为静默轮询恢复，L833-847）；`onTurnComplete`（L874）触发追问建议与排队消息冲刷。

**3. 发送主流程 `sendMsg`（L1229-1412）**：图片先传临时附件、失败降级 base64 内联（L1248-1274）→ 本地附件补传换 documentId（L1279-1302）→ 推入用户气泡 → 汇聚三来源知识范围（侧栏 + @提及 + 追问建议携带的 KB，L1360-1376）→ `startStream` POST。

**4. steer 插话子系统（L956-1227）**：生成中可发 inject（立即注入当前轮）或 after（排队下轮）消息；`handleSteerMsg` 处理服务端 new_run/already_injected 状态与 SSE 先于 HTTP 到达的竞态（L989-995）；`attachSteerFollowUp`（L1141）轮询最多 40 次把新 run 接回流。

**5. 其余编排**：会话切换 `watch(route.params)`（L657-691，状态全清 + `restoreDefaultsIfSnapshotted` 防旧请求态泄漏）；上滚分页（L717-749，只有真实向上滚动才脱离自动跟随）；推荐问题防抖 300ms 并 watch 六种上下文（L624-635）；fork 分叉经 sessionStorage 携带草稿（L327-415）。

## 三、外部连接

**依赖**：composables `useStream`（SSE 底座，L267）、`useChatStreamHandler`、三个 `provideChatXxx` 依赖注入（L238-241）；stores——menu（firstQuery 首问直达、标题更新 L1488）、settings（agent/模型/KB 全局态 + `hydrateSessionInputState` 恢复输入栏 L311）、sessionActivity（侧栏"生成中"标记，L439-442）；API 层 chat/steer/message-suggestion/temporary-attachments/agent 十余个函数。**被依赖**：路由表与创建会话页（firstQuery 跳转至此）、嵌入宿主页。**后端契约**：两条 chat 端点、`GET /api/v1/sessions/continue-stream`、steer 五个 REST 端点、SSE 的 `session_title` 等块类型（L1481-1496）。

## 四、数据流：一次提问的 SSE 渲染

回车 → InputField emit send-msg → `sendMsg`：`stopStream` + `prepareForNewOutgoingMessage` 清上一轮流态 → 附件上传 → 用户气泡 push 进 messagesList（L1346）并滚底 → 读 settings 判断 agentEnabled 选端点（L1381）→ `startStream` POST 收 SSE → 每 chunk 进 `onChunk`（L1480）：`session_title` 类型更新会话菜单，其余交 `processStreamChunk` 写尾部助手消息（引用/思考/工具时间线在此展开）→ botmsg 响应式渲染 markdown → 轮次完成回调加载追问建议（轮询 generating 最多 120 秒，L577-582）并冲刷 after 队列 → isReplying 复位、侧栏活动标记清除（L822-824）。

## 五、设计决策

- **编排而非实现**：2000 行里没有一行 SSE 解析或 markdown 渲染——那在 useStream/useChatStreamHandler/botmsg 里；本文件保留业务编排（范围组装、渠道差异、竞态策略），是组合式 API 的正确用法。
- **防御性注释密度极高**：`:key` 注释（L93-100）、向上滚动判定（L736-745）、IM 轮询恢复（L1414-1418）、steer 竞态（L989-992）——每条都是修过的真实 bug 的钉版，改前必读。
- **渠道语义分支**：同一界面服务 web/公开嵌入/IM 三来源，`channel === 'im'` 分支把"IM 回复不经过本服务器"这一后端事实显式化。
- 批判点：约 25 个 ref 状态在本作用域，steer 子系统横跨 270 行相互咬合，仍是前端复杂度热点；`watch(route.params)` 与 `onBeforeRouteUpdate` 双通道切换的时序依赖较隐晦。

## 六、新人提示

- 改"消息怎么渲染"去 botmsg.vue，改"流态怎么转"去 useChatStreamHandler.ts，本文件只改"何时发、发到哪、带什么范围"。
- 排查"刷新后回答不见了"：看 onAfterMsgList 的 continue-stream 恢复（L825-848）。
- 发送范围是三处合并（侧栏/@提及/追问建议），调试请求体时 `knowledge_base_ids` 可能大于侧栏所见。
- 停止生成分三步：stop-generation（本地立即停）→ stop-confirmed（服务端确认，清 steer 队列）→ stop-failed（回滚 loading 态），别只接第一个。
- 延伸：DeepWiki `7.3-chat-interface-and-agent-display.md`、`5.1-chat-interface-and-user-experience.md`、`7.5-state-management-and-api-integration.md`。
