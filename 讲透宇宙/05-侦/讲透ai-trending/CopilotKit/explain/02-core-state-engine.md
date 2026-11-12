# 02 · core 状态引擎：micro-redux、线程 store 与友邻接口

> 定位文件：`packages/core/`（图谱「core 状态引擎」层，21 节点）

## 一、角色定位（16 层架构中位置）

第 5 层「shared 共享横切库」之上、第 9 层「react-core v2 聊天组件」之下的**框架无关前端状态内核**。它不 import React（绑定全在 react-core），也不管网络协议（协议在 @ag-ui/client 与 runtime v2）。core 把"一个 agent 会话的全部客户端状态"（消息/工具/agent 注册表/线程列表/实时 socket）装进自制 Redux 风格状态机，vue/angular/react-native 绑定同源复用。

三条主线交织：**micro-redux**（状态机基建）→ **threads.ts**（用 micro-redux 搭的线程 store）→ **core.ts + delegate 子模块**（RunHandler/AgentRegistry/ContextStore/StateManager/SuggestionEngine 组合式拆分，互相靠 `CopilotKitCoreFriendsAccess` 友邻接口反向回调）。外加 IntelligenceAgent/ProxiedCopilotRuntimeAgent 两个 agent 类接到 SSE 或 Intelligence 平台。

## 二、内部结构（关键文件+行号锚拆解）

### 2.1 micro-redux（utils/micro-redux.ts，661 行）：不引 @ngrx/store 的 NgRx 复刻

文件通篇是 NgRx creator API 的手工复刻（NOTES-DIGEST batch-16 钉版："刻意不依赖 @ngrx/store，用约 660 行复刻其 API 形状"），动机是把依赖面压到只剩 rxjs：

- **ActionCreator**（micro-redux.ts:22-29）：工厂函数 + `type` 字面量 + `match()` 运行时类型守卫三合一。
- **createActionGroup**（micro-redux.ts:239-268）：批量生成命名空间化 creator，action type 硬编码为 `` `[${Source}] ${eventName}` ``（micro-redux.ts:237、:251）；props<T>()/empty()（micro-redux.ts:214-232）区分带参与无参。
- **createReducer**（micro-redux.ts:306-347）：on(...creators, reducer) 条目（micro-redux.ts:275-299）展开成 `Map<type, handlers[]>`，同 type 多 handler 顺序链式执行（micro-redux.ts:341-344），未知 action 原样返回（micro-redux.ts:337-339）。
- **createSelector**（micro-redux.ts:378-427）：单槽 memoization——只缓存上一次输入引用+结果（micro-redux.ts:393-400、:414-426）。
- **select/ofType 操作符**（micro-redux.ts:433-437、:445-462）：select=map+distinctUntilChanged；ofType 用 Set 过滤（micro-redux.ts:454）。
- **createEffect 双形态**（micro-redux.ts:467-515）：dispatch:true 的发射自动回流 dispatch（micro-redux.ts:593-607），dispatch:false 纯副作用（micro-redux.ts:610-616）。
- **createStore**（micro-redux.ts:541-661）：三条核心语义——① 构造时先用内部 boot action 预跑 reducer 得初态（micro-redux.ts:555-558）而非 lazy；② effect 订阅的 action 流经 observeOn(asapScheduler) 异步化（micro-redux.ts:588-590）防同步重入死循环；③ **fail-fast**：任何 effect 抛错，store 拒绝后续 dispatch 且 actions$/state$ 双双 error（micro-redux.ts:562-584）——错误显式烧穿而非吞掉（注释 micro-redux.ts:536-539 钉版为刻意 teardown）。
- 生命周期 action `@@micro-redux/init`/`stop`（micro-redux.ts:173-177）：init() 幂等（micro-redux.ts:636-649），stop() 先派发再退订全部 effect（micro-redux.ts:650-659）。

### 2.2 phoenix-observable（utils/phoenix-observable.ts，278 行）：Elixir Phoenix 的 Rx 化

Intelligence 平台实时层用 Phoenix Channels（Elixir 生态的 WebSocket 封装），本文件把它的回调 API 桥成 RxJS。设计上没有直接 import phoenix 的类型做继承，而是定义三个**最小结构契约**：`ɵPhoenixPushLike`/`ɵPhoenixChannelLike`/`ɵPhoenixSocketLike`（phoenix-observable.ts:16-41）——鸭子类型解耦，测试替身零成本。文件里 ɵ 前缀满天飞（Angular 内部 API 惯例，标记"包内可用、勿当公共 API"）。socket 生命周期信号 `ɵcreatePhoenixSocketSignals$`（phoenix-observable.ts:98-105）只做 open/error 的 Observable 适配，连接拆卸权留给上层。

### 2.3 threads.ts（1028 行）：八个 effect 织成的线程列表 store

`ɵcreateThreadStore`（threads.ts:557 的 `createThreadStore`，:1021 以 ɵ 名导出）是 micro-redux 的最大消费者。四组 action 分层（threads.ts:135-187）：**Adapter**（外部 API 动作）、**REST**（HTTP 生命周期）、**Socket**（实时事件）、**Domain**（纯状态语义 threadUpserted/threadDeleted）。

- **ThreadState**（threads.ts:111-121）：threads/isLoading/error/context/**sessionId**/nextCursor 等 11 字段；`sessionId` 是精髓——contextChanged 时自增（threads.ts:219），所有异步回包都带 sessionId 且 reducer 一律先做 `sessionId !== state.sessionId` 陈旧丢弃（threads.ts:239、:252、:267），**一代 context 一代会话**，竞态在 reducer 层免疫。
- **排序即业务**：sortThreadsByRecency（threads.ts:189-198）按 `lastRunAt ?? updatedAt ?? createdAt` 倒序，注释点明动机——archive/rename 这类 metadata 操作不应扰动顺序，只有真实 agent 活动才应置顶。
- 八个 effect 链（threads.ts:558-903 定义、:903-913 装配）：bootstrap（contextChanged→listRequested，:558）→ fetch（HTTP 列表，:573）→ metadataCredentials（listSucceeded 后需要 WS 则申请 join token，:604/:624）→ **socket**（:655，建 Phoenix 连接：ɵphoenixSocket$ + reconnectAfterMs/rejoinAfterMs 双指数退避 :674-677；订阅 topic `user_meta:${joinCode}` :678；连续失败 MAX_SOCKET_RETRIES=5 次后放弃并 warn，threads.ts:42/:689-695）→ **realtimeMapping**（:744，metadataReceived 译成 Domain action；**archived 在 includeArchived=false 时映射为删除而非 upsert** :758-766）→ fetchNextPage（:777）→ mutation（:845，rename/archive/delete 通用 REST 化）。
- **trackMutation**（threads.ts:916-953）：dispatch 转 Promise——merge 监听 mutationFinished（requestId 匹配）与 stopped（先停则拒绝）take(1) 收口；对外 renameThread/archiveThread/deleteThread 可 await（threads.ts:968-987）。
- 常量：`REQUEST_TIMEOUT_MS = 15_000`（threads.ts:43），用于 REST 流的 Rx timeout（:428、:484）。
- 文件尾部整批 ɵ 导出（threads.ts:1010-1028），含 `ɵMAX_SOCKET_RETRIES`——注释明说是为了让测试断言拆解阈值而不用各自硬编码。

### 2.4 core.ts 与友邻接口：组合式拆分的胶水

CopilotKitCore（core.ts:324）是门面，真活分散在 delegate 子模块。TS 私有性挡住了子模块调宿主的路，解法是**友邻接口** `CopilotKitCoreFriendsAccess`（core.ts:287-321）：声明 notifySubscribers/emitError/headers/credentials/debug/buildFrontendTools/getAgent 等"朋友可见"成员，子模块一律 `this.core as unknown as CopilotKitCoreFriendsAccess` 强转后调用（context-store.ts:46、agent-registry.ts:236/:386/:468-470，共 4 处，与图谱 imports 边一致——NOTES-DIGEST batch-16）。notifySubscribers 本体是 protected（core.ts:456-471），逐 subscriber try/catch 防一个坏订阅者炸全场。这是 C++ friend 的 TypeScript 民间实现：绕过编译期检查换组合自由，代价是接口与实现的手动同步义务。

**ContextStore**（context-store.ts:10-56）：context 注册表，add/remove 后经友邻接口广播 onContextChanged（context-store.ts:44-55）——context 变更对 agent 可见性的完整链路。

### 2.5 RunHandler（core/run-handler.ts，1064 行）：run 生命周期与 followUp 双轨

- **followUp 双轨**（skills 文档与源码逐字对齐，NOTES-DIGEST batch-52 抽验）：注册态 `FrontendTool.followUp?: boolean`（types.ts:39）声明"工具执行后要不要触发 LLM 跟进"；调用态 `CopilotKitCoreRunToolParams.followUp?: string | false`（run-handler.ts:47，三态文档在 :40-46——false 默认只记录、"generate" 直接再跑、任意其他字符串先注入一条 user message 再跑）。执行侧两处门禁：specific tool `tool?.followUp !== false`（run-handler.ts:617）、wildcard tool 同款（:757）；运行时处理在 :857-871——自定义文本先 push user message（:859-865），再 `await this._internal.waitForPendingFrameworkUpdates()` 让 React 的 useEffect 等延迟更新先落地（:866-869，注释明言镜像 processAgentResult 的同款 yield），最后递归 runAgent（:870）。
- **递归深度控制**：`_runDepth`（run-handler.ts:95-103）保证 AbortController 只在顶层 run 建立、follow-up 递归调用不重复建。
- **_lastConnectedThreadId**（run-handler.ts:105-125）：区分"新线程恢复"（要清空本地状态全量重放）与"同线程 churn 重连"（保留本地状态从 lastSeenEventId 续传）。注释里保留了案例名——"Tyler's bug"：曾把每次 connect 都当新恢复，导致 gateway 全量重放 ×churn 放大成 inspector 重复 `cpki_event_id` 行 + 间歇 "Message not found" toast。**源码注释里的 bug 考古是理解这段守卫存在的最短路径**。
- 工具结果插回消息流：找 parent message 的 index，splice 插到其后（run-handler.ts:599-613）；若 parent 已被切线程移除则**直接放弃插入且不触发 follow-up**（:601-607 注释）——防止把结果写进错误线程。

### 2.6 AgentRegistry（core/agent-registry.ts，617 行）与两个 agent 类

- **AgentRegistry**（agent-registry.ts:56）维护双注册表：localAgents（前端定义）+ remoteAgents（runtime 发现，:58-59），合并视图 _agents。initialize（:131-137）做 agentId 分配 + headers/credentials 下发。
- **transport 幂等守卫**（agent-registry.ts:69-73 注释）：_requestedTransport 存请求的模式（auto），_runtimeTransport 存 auto-detect 的**解析结果**（rest/single）；幂等比较对请求值做，否则 provider 每次 render 重放 "auto" 都重跑 /info 握手——React effect 重入在类型层免疫。
- **remote agent 发现**：fetchRuntimeInfo 后把 runtime 侧 agent 列表包成 ProxiedCopilotRuntimeAgent（agent-registry.ts:375-395）。
- **ProxiedCopilotRuntimeAgent extends HttpAgent**（agent.ts:100，@ag-ui/client 的 HTTP agent 基类）：构造时按 transport 定 run URL——single 直接用 runtimeUrl（信封带 method），rest 拼 `/agent/{routedId}/run`（agent.ts:116-130）。runtimeAgentId（agent.ts:96-101）允许注册键与路由键分离；字段 readonly 且注释解释为什么——super.url 构造时烘死，后改会 desync（agent.ts:105-109）。runtimeMode 经 /info 探测，失败回退 legacy（NOTES-DIGEST batch-134）。
- **IntelligenceAgent extends AbstractAgent implements RunCompletionAware**（intelligence-agent.ts:138-139）：Phoenix Socket+Channel 封装（:141-143），sharedState 跨 clone 共享 lastSeenEventIds（:144、:158-167）。两个协议级细节：REST 409 且 mode=run 抛 AgentThreadLockedError（:431-432，类 :77-83）——平台分布式线程锁的客户端投影；connectAgent 覆写**跳过 verifyEvents**（:170-176 注释）——AG-UI 校验器要求 RUN_STARTED 先于内容事件，connect 中途续流天然不满足，只能豁免。RunCompletionAware（:99）暴露 activeRunCompletionPromise，供 v2 CopilotChat 串行化等在途 run（NOTES-DIGEST batch-137）。

## 三、外部连接（imports 边上下游）

- **上游**：react-core v2 的 useAgentContext/useChat 系 hooks 直接消费 CopilotKitCore 与 ɵcreateThreadStore；vue/angular/react-native 绑定同源。
- **下游**：@ag-ui/client（AbstractAgent/HttpAgent/Message/ToolCall，本包最重外部依赖）；phoenix（Socket/Channel）；rxjs；@copilotkit/shared（randomUUID/logger/AGUI 类型别名）。
- **横向**：core 与 runtime v2 无直接 import，靠 HTTP/WS 协议耦合（/info 握手、AG-UI 事件流、Phoenix channels）——前后端解耦边界正画在 core 包右边缘。

## 四、数据流（一次线程重命名+实时同步的旅程）

1. UI 调 `threadStore.renameThread(id, "新名")`（threads.ts:968）→ trackMutation 生成 requestId、merge 监听 mutationFinished、dispatch `[Thread Adapter] renameRequested`（threads.ts:916-953）；
2. mutationEffect ofType 命中（threads.ts:845），组 REST 请求（friends 注入 headers），结果映射回 `[Thread REST] mutationFinished`（outcome 带 requestId）；
3. reducer 无需为 rename 写 handler——状态更新来自 socket：平台改名后向 `user_meta:{joinCode}` channel 推 metadataReceived（threads.ts:178-181）；
4. realtimeMappingEffect 译成 `[Thread Domain] threadUpserted`（threads.ts:770-775）；
5. upsertThread 替换记录并按 lastRunAt 重排（threads.ts:200-212、:189-198）；
6. UI 经 store.select(ɵselectThreads) 的 distinctUntilChanged 流收到新数组重渲染；
7. trackMutation 同拍收到 mutationFinished，Promise resolve。若 5 次重连失败，fatalSocketShutdown$ 放弃实时通道（threads.ts:689-695），此后靠 refresh() 手动拉——降级而非崩溃。

## 五、设计决策（为什么这么设计 + 替代方案）

- **自制 micro-redux vs 引 NgRx/Zustand**：CopilotKit 是被 embed 进宿主 App 的库，带大状态库进 bundle 会与宿主自己的 Redux/Zustand 撞版本；660 行复刻换来零新依赖+API 熟悉度（NgRx creator 形状）。代价是 fail-fast（micro-redux.ts:572-584）较烈——嵌入场景宁可烧穿也不静默错下去。
- **sessionId 代际守卫 vs 取消令牌**：RxJS cancel 要管理 subscription，sessionId 只在数据包打代际戳、reducer 丢旧代——零订阅管理成本，且天然覆盖"响应乱序"而非仅"已取消"。
- **友邻接口 vs protected vs 事件总线**：protected 无法跨包（dts 丢失）；事件总线让调用关系不可 grep。友邻接口把"谁能调什么"压进可读类型声明（core.ts:287-321），`as unknown as` 丑但集中可审计。
- **connectAgent 豁免 verifyEvents vs 改协议校验器**：校验器假设流从 RUN_STARTED 开始，connect 天然违反；改 @ag-ui/client 要动协议包发版节奏，局部豁免+注释钉版（intelligence-agent.ts:170-176）是务实短路。
- **trackMutation Promise 化 vs 纯回调**：外部 await 友好、内部纯 action 流——merge+take(1) 桥接两范式，stopped 兜底防永久 pending（threads.ts:930-940）。

## 六、新人提示（坑+勘误+延伸阅读）

- **ɵ 前缀到处都是**（threads.ts/phoenix-observable.ts 全线）：这是"包内部/测试专用"信号，不是拼写错误。公共 API 永远不该 re-export ɵ 符号。
- **followUp 两个类型别混**：types.ts:39 是 boolean（注册声明），run-handler.ts:47 是 string|false（调用控制）——同名不同义，skills 文档已抽验逐字对齐（NOTES-DIGEST batch-52）。
- **测试文件不在图谱**：packages/core/src/__tests__ 被 .understandignore 裁剪，找测试去磁盘直看（agent-registry-resync.test.ts 等）。
- **skills 文档路径漂移**：旧文档 packages/v2/core/... 目录已不存在，现路径 packages/core/（NOTES-DIGEST batch-45 钉版）；v1 错误类族现居 packages/shared/src/utils/errors.ts。
- **Phoenix 重连隐形地雷**：socket.disconnect() 置 closeWasClean=true 重置重连计时器，错误处理器里绝不能调（runtime 侧 runner/intelligence.ts 注释详尽，NOTES-DIGEST batch-102）。
- **fail-fast 传染**：effect 抛错后 store 永久报废（micro-redux.ts:562-584），新写 effect 必须 catchError 兜成 action（参考 threads.ts:541-553 的 catchError→mutationFinished(ok:false) 模式）。
- 延伸阅读：第 3/4 篇（react-core 消费面）；第 1 篇（runtime 侧线程双后端与 /info 握手另一端）；@ag-ui/client AbstractAgent 生命周期（skills/copilotkit-agui/references/client-sdk.md）。
