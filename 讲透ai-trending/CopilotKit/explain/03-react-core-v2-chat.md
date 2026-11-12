# 03 · react-core v2 聊天组件：输入、视图与 A2UI 表面

> 定位文件：`packages/react-core/src/v2/components/chat/`（22 文件 7316 行）+ `src/v2/a2ui/`（图谱「react-core v2 聊天组件」层，88 节点）

## 一、角色定位（16 层架构中位置）

第 9 层「react-core v2 聊天组件」的核心子域。chat/ 目录是 CopilotKit v2 的**整套无头+有头混合聊天 UI**：容器（CopilotChat.tsx 749 行）负责把 core 包（第 2 篇）的 agent 状态接进来，视图（CopilotChatView.tsx 900 行）负责布局与滚动，输入（CopilotChatInput.tsx 1424 行）负责 composer 全部交互；Popup/Sidebar 是 View 的三种宿主形态；a2ui/ 目录（严格说在 components 之外，但与聊天流共生）把 AG-UI activity 事件渲染成生成式 UI 表面。目录里还住着 Lightbox、normalize-auto-scroll、scroll-element-context 这类小而关键的配套件——**这个目录本身就是一个小型组件库**，react-ui v1（第 5 篇）反而建筑在其之上。

命名考古：这套文件源自已消亡的 `packages/v2/react/src`（v2/index.ts:11 注释 "Local V2 react code (absorbed into @copilotkit/react-core)"），迁移时 chat 组件从 kebab-case 改名 PascalCase（copilot-chat.tsx→CopilotChat.tsx；skills/copilotkit-develop/sources.md 的 43 条路径映射表，NOTES-DIGEST batch-46 钉版）——**旧文档里的 kebab 路径在磁盘上零存在**，看到 `copilot-chat-input.tsx` 一律映射成 `CopilotChatInput.tsx`。

## 二、内部结构（关键文件+行号锚拆解）

### 2.1 CopilotChatInput.tsx（1424 行）：composer 的全部交互

- **主组件**（CopilotChatInput.tsx:128 `export function CopilotChatInput`），三种输入模式 `CopilotChatInputMode = "input" | "transcribe" | "processing"`（CopilotChatInput.tsx:40）——这是**语音三态**：普通输入/录音转写中/处理中；transcribe 模式进入时自动 `recorder.start()`、离开时 stop（CopilotChatInput.tsx:321-331），非 input 模式强制紧凑布局并清空 slash 面板（CopilotChatInput.tsx:334-339）。
- **8 个 slot**（CopilotChatInputSlot 类型，:46-55）：textArea/sendButton/startTranscribeButton/cancelTranscribeButton/finishTranscribeButton/addMenuButton/audioRecorder/disclaimer。实现方式是**静态属性挂载**：子组件作为命名空间成员定义在文件底部（SendButton :1147、ToolbarButton :1164、StartTranscribeButton :1193、CancelTranscribeButton :1205、FinishTranscribeButton :1217、AddMenuButton :1229、TextArea :1349 forwardRef、AudioRecorder=CopilotChatAudioRecorder :1390、Disclaimer :1392），运行时经 `renderSlot(slotProp, Default, props)` 绑定（:498、:540）——用户传自定义组件替掉默认件，其余 props 原样注入。图谱钉版：这套"静态属性 + WithSlots 类型"就是 slot 系统的全部机制。
- **slash 命令面板**：`commandQuery` state（:174，null 表示面板关闭），输入以 `/` 开头即触发——`updateSlashState` 里 `value.startsWith("/")` 且只取**首行**做查询（:341-359，:349 是判定行）；过滤排序 startsWith 组优先于 contains 组（:240-266）；键盘导航 ArrowDown/ArrowUp 环形移动高亮（:410-436）、Enter 选中执行（:438-447）、Escape 关闭（:448-452）——全部只在 `commandQuery !== null && mode === "input"` 时生效（:406）。
- **IME 防误发**：handleKeyDown 第一行就拦 `e.nativeEvent.isComposing || e.keyCode === 229`（CopilotChatInput.tsx:404-407）——中日韩输入法组词期间的 Enter 不发送；配套 onCompositionStart/End 维护 isComposingRef（CopilotChatInput.tsx:504-509）。
- **Enter 语义**（CopilotChatInput.tsx:457-471 注释钉版设计）：composer 有可发送文本时 Enter **永远发送**，即使 run 在途——注释给出完整动机：非空 composer 是明确的发送意图；曾把该 Enter 路由到 onStop，导致用户选完 interrupt 选项后输入第二条消息时把 resume run 打断、下一个 interrupt 永远不出现。Enter→stop 仅在 composer 为空时保留（真正的停止手势）。按钮则相反：isProcessing 时按钮渲染为 Stop，点击无条件 stop（CopilotChatInput.tsx:523-528 注释对比两种控件差异）。
- **bottomAnchored 模式**（props 文档 :87-99）：flex 尾子元素定位时经 CSS 变量 `--copilotkit-license-banner-offset` 给固定定位的 license banner 预留底部空间，防重叠。

### 2.2 CopilotChat.tsx（749 行）：容器层与发送串行化

- **消息指纹 memo**（CopilotChat.tsx:609-630）：为避免 useMemo 依赖整数组引用，构造轻量 fingerprint（id:role:content 长度:toolCall 参数长度拼接）而非 JSON.stringify——注释点明动机是**别在每次 render 序列化巨大的 base64 附件**。
- **waitForActiveRunToSettle**（CopilotChat.tsx:317-333）：发送前若 `agent.isRunning` 且 agent 实现 RunCompletionAware（core 包第 2 篇的接口），await `activeRunCompletionPromise`；在途 run reject 也继续发送但留 console.error 可观测。
- **onSubmitInput**（CopilotChat.tsx:336-418）三段防御：① 上传中 fast-fail（CopilotChat.tsx:340-350，对着 ref 的活状态查，:196-201 注释解释闭包捕获的 state 跨 await 会过期）；② **乐观清空输入** `setInputValue("")`（CopilotChat.tsx:356 注释：先清让用户看到已受理，实际 dispatch 可能延迟到在途 run 之后）；③ await 之后**重查**上传守卫，若此刻被拦则**把文本恢复回 composer**（CopilotChat.tsx:364-378 注释："so it is never silently lost"）——这一恢复逻辑正是"慢网络/在途 run 下用户键入不丢"的防线。
- 建议点击路径镜像同一串行化（CopilotChat.tsx:421-427 注释点名 **#5195 修复**：选中建议不得抢占在途 run）。
- 线程恢复防闪屏：lastConnectedThreadId 让显式 threadId 的 welcome screen 抑制到 connect 完成（CopilotChat.tsx:222-231 注释）；非显式线程跳过 /connect——本地 UUID 后端没见过，connect 必 404（CopilotChat.tsx:238-245 注释）。
- 容器/视图分层：props 类型 = CopilotChatViewProps Omit 掉内部托管的 state 字段再扩展（图谱 file 节点钉版）。

### 2.3 CopilotChatView.tsx（900 行）：元素即状态与滚动

- **元素即状态（callback ref）**（:179-190 注释 + `useState<HTMLDivElement | null>` :191）：输入容器元素存成 state 而非 useRef。原因注释钉版：overlay wrapper 只在 chat-view 分支渲染（welcome 分支没有），普通 useRef+[] effect 在欢迎屏起步时会观察到 null 且**用户发第一条消息后永不重挂**——底部留白错、最后几条消息滚到绝对定位输入条下面。callback ref 让 ResizeObserver 随 overlay 挂载/卸载响应式附接/分离。
- 移动端键盘：useKeyboardHeight（:196）跟踪键盘开合。
- **滚动上下文传元素不传 ref**（scroll-element-context.ts:7-12 注释）：ScrollElementContext 携带元素本体，消费方（CopilotChatMessageView 喂 useVirtualizer 的 getScrollElement）在滚动容器首次挂载时**响应式重渲染**——ref 对象变化不触发渲染，元素值才会。
- autoScroll 三模式归一化 `pin-to-bottom | pin-to-send | none`（normalize-auto-scroll.ts:1-17），boolean 兼容映射（true→pin-to-bottom）。
- sendNonce 机制（CopilotChat.tsx:633-652）：lastUserMessageId 变化驱动 nonce 自增，让 pin-to-send 模式知道"这是新发送"而非恢复线程。

### 2.4 a2ui/：单活动生命周期（A2UIMessageRenderer.tsx，408 行）

`createA2UIMessageRenderer`（:79）注册 `activityType: "a2ui-surface"`（:88）的 activity 渲染器。设计核心（:66-71 注释钉版，OSS-162）：**整个生成式 UI 生命周期挂在一条稳定的 messageId 上**——pre-paint 状态（status: building/retrying/failed）先随 content 流入，paint 时 a2ui_operations 就位，状态原地互换、骨架被表面替换，零额外协调；schema 用 zod `.passthrough()`（:72-77）保未来字段。

- **按 surfaceId 分组**（:112-126）：operations 按 getOperationSurfaceId 分桶，缺省 DEFAULT_SURFACE_ID。
- **cross-over 交接**（:168-181 注释，图谱钉版）：loader 保持 in-flow，同时 surface **离屏挂载并绘制**，surface 首次 onReady 才瞬间互换——正确延迟取决于流速度/载荷大小/机器性能，固定 delay 不可能对；`requestAnimationFrame` 一帧后 setSurfaceReady（:180），8 秒 setTimeout 仅作 onReady 不来的兜底（图谱 A2UIMessageRenderer 节点钉版）。
- **pre-paint 记忆**（:157-166）：lastLoaderContentRef 记住最后一个真正的 pre-paint 快照，paint 快照不许覆盖它——防闪烁回退成通用骨架。
- recovery 参数（:59-62）：retrying 子标签 showAfterMs 默认 2000、showAfterAttempts 默认 2（:83-84），debugExposure 控制重试细节曝光度。

## 三、外部连接（imports 边上下游）

- **上游消费**：react-ui v1 的 Chat 组件、examples、Popup/Sidebar 宿主页面；skills/react-core 文档镜像（agent-access.md 引 use-agent 行号锚、client-side-tools.md 引 run-handler 锚，与本目录组件同层）。
- **下游依赖**：`@copilotkit/core`（CopilotKitCore/RunCompletionAware 判定）、`@copilotkit/a2ui-renderer`（A2UI 协议渲染器，第 11 层）、`@ag-ui/client`（Message/AbstractAgent 类型）、lucide-react 图标、tailwind-merge、radix 系 UI 原语（dropdown-menu/tooltip）、以及本包 v2/providers 的 CopilotChatConfigurationProvider（labels 国际化，CopilotChatInput.tsx:13-16）。
- **横向**：components/chat ↔ components/OpenGenerativeUIRenderer（第 1 篇 clarinet 中间件的前端对端，@jetbrains/websandbox iframe 沙箱）。

## 四、数据流（一条带附件消息的旅程）

1. 用户敲 `/` → updateSlashState 置 commandQuery（CopilotChatInput.tsx:349），面板浮出，ArrowDown 高亮第 2 项（:410）；
2. 用户删掉 `/` 直接打字，拖一张图进来 → useAttachments（CopilotChat.tsx:176-186）暂存为 uploading 状态；
3. Enter（非 IME 组词，:404 放行；commandQuery 已 null，:457 分支命中）→ send()（:473-491）：trim 非空才 onSubmitMessage，**非受控模式立即清空 + 受控模式 onChange("") 通知父级**（:482-486），焦点回 textarea；
4. 容器 onSubmitInput（CopilotChat.tsx:336）：上传守卫 fast-fail → 乐观清空输入 → waitForActiveRunToSettle 等 run → 重查上传（若仍在传，恢复文本回 composer :376）→ consumeAttachments 取就绪附件；
5. 有附件走多模态 contentParts 数组（text part + attachment source/metadata，:386-400），无附件纯文本 addMessage（:403-407）；
6. `copilotkit.runAgent({ agent })`（:409）进 core 包 RunHandler（第 2 篇 run-handler）→ AG-UI 事件流回放，agent.messages 增量更新；
7. View 层 messagesMemoKey 指纹变化触发新 messages 引用（:631-635），sendNonce++（:644-652），pin-to-send 把新 user message 滚进视口；若 agent 中途发 a2ui-surface activity，A2UIMessageRenderer 接管：building 骨架 → operations 到达 → 离屏 paint → onReady 互换（A2UIMessageRenderer.tsx:168-181）。

## 五、设计决策（为什么这么设计 + 替代方案）

- **Enter 永发 vs Enter 依 isProcessing 切换**：切换式（processing 时 Enter=stop）是多数聊天 UI 的直觉做法，但 CopilotKit 的 interrupt 选项流（选完 slot 后 run 仍在流式收尾）会把用户下一条消息误杀。钉版注释（CopilotChatInput.tsx:459-466）记录了这个从 bug 到语义的演化。代价是"空 composer Enter=stop"需要用户重新学习。
- **乐观清空+可恢复 vs 发送成功才清空**：等成功才清会在慢网络下让用户盯着不动了的文本怀疑没点上、连按 Enter；乐观清空立刻给反馈，但必须配套 post-await 守卫与恢复逻辑（CopilotChat.tsx:356-378），否则被拦的发送就是静默丢字。这是用复杂度换体感的典型交易。
- **元素即状态 vs useRef**：useRef 是 React 里装 DOM 节点的默认姿势，但 ref.current 变化不触发渲染、也不触发 effect 重跑——条件渲染的 overlay 场景直接翻车（CopilotChatView.tsx:179-190 注释全程钉版）。setState 存元素让 ResizeObserver 的生命周期跟着元素走。代价是每次挂载多一次渲染，可接受。
- **slot 静态属性 vs compound component context**：radix 式 compound（<Input.TextArea>）需要 provider 传配；静态属性挂默认组件 + renderSlot 直接替换更简单，类型上 WithSlots 直接 typeof 引用默认件（:46-55），零运行时开销。代价是默认件与命名空间耦合在同一文件（1424 行的体量来源之一）。
- **单 messageId 承载 a2ui 全生命周期 vs 多事件多组件**：拆成 building/painted 两个组件要跨组件协调交接时机；合在一个 activity 上，content schema 本身就是状态机（status 字段→operations 字段），cross-over 只是同一组件内的渲染分支切换（A2UIMessageRenderer.tsx:66-71）。

## 六、新人提示（坑+勘误+延伸阅读）

- **勘误（任务书对照）**：任务书称"Enter 键慢网络丢键击已知 bug"——源码中无此字样的 known-bug 注释；实际存在的是**三层防御**（IME 组词拦截 :404、Enter 永发语义 :457-471、乐观清空+被拦恢复 :356-378）与 **#5195 发送串行化修复**（:421-427 注释）。图谱 languageNotes 里"Enter 丢键击问题"指的正是这段历史（NOTES-DIGEST batch-56-part-2 引 b27），读代码时应把它理解为"已修复并防复发的设计"，而非 open bug。
- **勘误（路径）**：任何文档/记忆里的 `packages/v2/react/src/components/chat/copilot-*.tsx` 都是旧世界地址，机械映射 `packages/v2/react/src` → `packages/react-core/src/v2` 且 kebab→Pascal（NOTES-DIGEST batch-46 的 43 条映射表）；另有 5 条死引用（labels.ts/slot.ts/runtime.ts 等）已并入别的文件，别按图索骥。
- **IME 是第一公民**：任何新键盘交互都必须先过 isComposing/229 检查（:404-407），否则中日韩用户组词确认即误发——这是该组件族写死的规约。
- **别在 chat/ 里找消息渲染逻辑**：单条消息的气泡/工具调用/reasoning 展示在 CopilotChatMessageView.tsx（733 行）与 Assistant/UserMessage 子件，本篇从容器视角略过；读虚拟化要从 scroll-element-context.ts 的注释入手。
- **受控/非受控双模式**：value+onChange 传入即受控（send 后靠 onChange("") 通知父级重置，:482-486）；只传 defaultValue 则内部 state。混用会得到受控语义。
- 延伸阅读：第 2 篇（RunCompletionAware 与 activeRunCompletionPromise 的定义端）；第 5 篇（react-ui v1 如何包这层组件）；A2UIMessageRenderer 的姊妹件 A2UIRecoveryStates.tsx（419 行，重试 UX 全家桶）；skills/react-core/references/agent-access.md（带行号锚的 Common Mistakes 清单）。
