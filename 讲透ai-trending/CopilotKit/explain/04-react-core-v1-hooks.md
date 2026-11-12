# 04 · react-core v1 hooks 生态与 v1↔v2 桥接

> 定位文件：`packages/react-core/src/hooks/`（v1 hooks，29 文件）+ `src/components/copilot-provider/` + `src/v2/providers/CopilotKitProvider.tsx`（图谱「react-core v1 基础层」74 节点与「react-core v2 聊天组件」层的交叠带）

## 一、角色定位（16 层架构中位置）

第 8 层「react-core v1 基础层」的主体，同时是 v1↔v2 两代世代的**接缝层**。今天 import 自 `@copilotkit/react-core` 的所有 v1 API（CopilotKit/useCopilotAction/useCoAgent/useCopilotChat）都活在这层，但它们的实现几乎全部已**穿透到 v2**：v1 的 CopilotKit 组件内部包着 v2 的 CopilotKitProvider，v1 的 useCoAgent 是 v2 useAgent 的薄包装，v1 的 useCopilotChatInternal 底层用 v2 useAgent 拿 agent。理解这层的正确姿势不是"学一套旧 API"，而是看**一个框架如何在重写期间保持公共 API 冻结**——包装、委托、反向导出三种手段的全谱系展示。

## 二、内部结构（关键文件+行号锚拆解）

### 2.1 CopilotKitProvider.tsx（v2，811 行）：稳定实例 + setter effects 跳首帧

v2 提供者是整棵组件树的根，两个机制撑起全部稳定性：

- **稳定实例（ref-init 惰性单例）**：`copilotkitRef` 为 null 时才 `new CopilotKitCoreReact({...})`（CopilotKitProvider.tsx:534-559）——provider 生命周期内实例只造一次，此后 props 变化**绝不重建**，一律走 setter。构造参数里 transport 三态（single/rest/auto 由 useSingleEndpoint 映射，CopilotKitProvider.tsx:538-543）；defaultThrottleMs 在构造块内同步设置（CopilotKitProvider.tsx:554-558 注释：让子 hooks **首次 render** 就读到正确值，等 useEffect 就晚了）。
- **setter effects 跳首帧（didMountRef 守卫）**：五个 setter effect（setTools/setRenderToolCalls/setRenderActivityMessages/setRenderCustomMessages 等）首行 `if (!didMountRef.current) return;`（CopilotKitProvider.tsx:687-705），didMountRef 在**声明于 setter effects 之后**的 effect 里置 true（CopilotKitProvider.tsx:707-711，注释明言"must be declared AFTER ... so it runs last"）。原因注释（CopilotKitProvider.tsx:678-684）是全文件最重要的段落：**React effects 自底向上触发**——子组件（useFrontendTool/useHumanInTheLoop）在自己的 effect 里 addTool() 注册工具，这些 effect 先于父 provider 的 effect 执行；若父 setter effect 挂载期也跑，会把孩子刚注册的工具用（可能空的）props 数组覆盖掉。
- 其余：frozen 空对象默认值防 effect 无谓重跑（CopilotKitProvider.tsx:60-64）；数组 props 经 useStableArrayProp 归一化并在开发态警告（CopilotKitProvider.tsx:228-239、:310/:417/:421，警告文案直接指路 useFrontendTool）；runtime 特性旗标订阅（CopilotKitProvider.tsx:563-576）；executingToolCallIds 提升到 provider 层——HITL 重连时 onToolExecutionStart 在子组件挂载前触发，provider 层才接得住（CopilotKitProvider.tsx:593-597）；onError 经 ref 转发避免重订阅（CopilotKitProvider.tsx:628-651）；generateSandboxedUi 的设计原则 prompt 是 shadcn 风格硬编码常量（DEFAULT_DESIGN_SKILL，CopilotKitProvider.tsx:66-75），工具描述连**参数生成顺序**都规定死（css→html→js，CopilotKitProvider.tsx:84-89）——与第 1 篇 clarinet 流式渲染的参数顺序一一对应。

### 2.2 v1 CopilotKit 组件：包 v2 provider 的洋葱

`CopilotKit`（copilotkit.tsx:77）的 JSX 结构是四层洋葱：ToastProvider → CopilotErrorBoundary → ThreadsProvider → **CopilotKitV2Provider**（copilotkit.tsx:86-99）。关键细节：`useSingleEndpoint={props.useSingleEndpoint ?? true}`（copilotkit.tsx:95）——**v1 默认走 single-route 信封模式**，v2 默认 auto；传给内层的还有 renderCustomMessages=[CoAgentStateRenderBridge]（copilotkit.tsx:84）把 v1 的 coagent 状态渲染桥进 v2 渲染器。CopilotKitErrorBridge（copilotkit.tsx:107 起）订阅 v2 core 错误转发给 v1 错误体系，注释强调"无论 Chat 组件渲染多少次只存在一个订阅"。v1 文件从 `"../../v2"` import Provider（copilotkit.tsx:28），而 v2/index.ts 尾部又反向 re-export v1 的 CopilotKit（"V1 backward-compat re-exports"）——**模块级环**就此闭合，靠 v2 导出顺序（自身组件先、v1 兼容层最后）避免初始化竞态。

### 2.3 useCopilotAction：三路分派 + Rules of Hooks 守卫

`useCopilotAction`（use-copilot-action.ts:135 起，函数签名带 const 泛型参数元组）按 action 配置三路分派：render→useRenderToolCall、hitl→useHumanInTheLoop、frontend→useFrontendTool。精妙处在配置切换守卫：初始配置存 useState（:138），每 render 重算当前配置，**类型变了直接 throw**（:147-150）——注释坦承这是在"条件调用 hook"与 React 调用栈规则之间两害相权：不换 hook 链就 throw，绝不静默错位。245 行里近 130 行是 JSDoc 教程（含 GIF 链接），这是 v1 hooks 的普遍文体。

### 2.4 useCoAgent：v2 useAgent 的兼容包装（380 行，大半是文档）

useCoAgent（use-coagent.ts:210）三行核心：`useAgent({ agentId: options.name })` + `useAgentNodeName`（use-coagent.ts:213-215），文件 use-coagent.ts:38-39 注释自认"thin compatibility wrapper over the v2 useAgent hook"。增值逻辑：setState 兼容两种形态——函数式 updater 与对象浅合并 `agent.setState({...agent.state, ...newState})`（use-coagent.ts:220-230）；config/configurable 经 `copilotkit.setProperties` 下发（use-coagent.ts:235-251）；外部状态管理模式（isExternalStateManagement）下把 options.state 序列化比对再同步（use-coagent.ts:253-265）。返回的 run 字段映射 v2 的 agent.runAgent()（use-coagent.ts:50-55 文档）。

### 2.5 useCopilotChatInternal（875 行）：最大的兼容层与真实的 API 缺口

- **connect 的一次性守卫**：lastConnectedAgentRef 记住已 connect 的 agent 实例，防无关 context 重渲染与 StrictMode 双调用触发重复 /connect（use-copilot-chat_internal.ts:344-346 注释）；cleanup 里 abort AbortController + detachActiveRun + **ref 置 null**（use-copilot-chat_internal.ts:398-405 注释：StrictMode 卸载重挂必须重新 connect）。connect 前手动塞 AbortController 的注释（use-copilot-chat_internal.ts:348-353）点名"镜像 V2 CopilotChat 模式"。
- **AGUIConnectNotImplementedError 静默吞**（use-copilot-chat_internal.ts:374-377）：agent 不实现 connect 就当无事发生。
- **interrupt 元素的响应式桥**：订阅 copilotkit.interruptElement（useLangGraphInterrupt 发布），让 v1 返回类型保持 reactive（use-copilot-chat_internal.ts:424-434）。
- **返回对象的真实缺口（任务书命题源码实证）**：`UseCopilotChatReturn` 接口声明了 visibleMessages（:157，已 @deprecated 标注"use messages instead"）、mcpServers/setMcpServers（:279-283）、runChatCompletion（:276）；但 `useCopilotChatInternal` 的 return 对象（:758 起）**不含 visibleMessages**，且 `// mcpServers,`、`// setMcpServers,` 两行被注释掉（:769-770）。上游公开包装 useCopilotChat 照样解构这些字段（use-copilot-chat.ts:107-112）再原样返回——**运行时拿到的是 undefined**。文件顶部还留着作者自疑注释 `// TODO: Do we need this? If so, does it work properly? test.`（use-copilot-chat.ts:105）。这是"接口承诺 vs 实现交付"落差的活标本：类型系统管不住注释掉的返回字段。
- 兜底件 use-copilot-chat-headless_c.ts 的 createNonFunctionalReturn（:183 起）给出非功能降级形态（mcpServers: [] 等），说明这族 API 曾有双实现。

### 2.6 其余 v1 hooks 一览（外部连接密度最高的一层）

use-copilot-readable/use-make-copilot-document-readable（文档上下文注入）、use-langgraph-interrupt（中断渲染）、use-copilot-authenticated-action、use-render-tool-call、use-frontend-tool、use-human-in-the-loop、use-coagent-state-render 三件套（render/render-bridge/render-registry，v1 共享状态渲染的注册表模式）、use-flat-category-store/use-tree（树形状态存储，被 copilot-messages 消费）、use-copilot-runtime-client（旧 GraphQL 客户端通道）。它们与 copilot-context/copilot-messages/threads-context 组成 v1 上下文系统，全部最终汇入 CopilotKitV2Provider 的 core 实例。

## 三、外部连接（imports 边上下游）

- **上游**：所有 v1 应用代码与 examples（`<CopilotKit>` + hooks 组合）；react-ui v1 组件库（第 5 篇）重度消费 useCopilotChat/useCopilotAction。
- **下游**：`../v2`（useAgent/useCopilotKit/CopilotKitProvider——v1 hooks 对 v2 的单向依赖是桥接主通道）；`@copilotkit/core`（CopilotKitCoreReact 包装的 CopilotKitCore，第 2 篇）；`@copilotkit/runtime-client-gql`（Agent/ExtensionsInput 等 v1 GraphQL 遗产类型）；`@copilotkit/shared`（错误族/COPILOT_CLOUD_CHAT_URL 常量）。
- **环**：v1 copilot-provider ↔ v2 index 互相 import（v1 用 v2 的 Provider，v2 re-export v1 的 CopilotKit）。图谱上表现为 react-core v1 层与 v2 层之间的双向边——本仓唯一的双代循环依赖。

## 四、数据流（v1 应用一次 useCopilotAction 注册的旅程）

1. 应用渲染 `<CopilotKit runtimeUrl instructions>`：Toast/ErrorBoundary/ThreadsProvider 逐层包裹，CopilotKitV2Provider 以初始 props 惰性构造唯一的 CopilotKitCoreReact（CopilotKitProvider.tsx:534-559）；
2. 子组件 `useCopilotAction({name, parameters, handler})` → 配置识别为 frontend → useFrontendTool 在自己的 effect 里 `copilotkit.addTool(...)`（子 effect 先跑）；
3. provider 的 setTools effect 本轮被 didMountRef 拦住（:688），不覆盖孩子的注册；挂载周期末尾 didMountRef 置 true（:709-711）；
4. 之后任何 render，若 props.frontendTools 数组引用变化，setTools 才用 props 里的全量列表同步一次（此时孩子 effect 也会重跑重注册，两者收敛）；
5. runtime /info 握手完成 → onRuntimeConnectionStatusChanged → provider setState 特性旗标（:567-571）→ v1 上下文层感知；
6. LLM 调用该工具 → core RunHandler（第 2 篇 run-handler.ts:617 followUp 门禁）执行 handler，结果回填消息流。

## 五、设计决策（为什么这么设计 + 替代方案）

- **稳定实例 + setter vs props 驱动重建**：重建 CopilotKitCoreReact 会重置 agent 注册表、线程订阅、特性旗标，用户改一个 header 就全断线；setter 粒度更新保住单例。代价是必须手工维护"构造初始值 + 后续 setter"两条路径的一致性，以及跳首帧守卫这种精致陷阱（自底向上 effect 顺序是 React 文档级知识但极反直觉）。
- **throw 而非条件 hook**：useCopilotAction 的配置切换守卫（use-copilot-action.ts:147-150）宁可运行时炸也不破坏 hook 调用栈——替代方案是把三种形态拆成三个 hook 让用户自己选，但那会破坏 v1 API 冻结承诺。
- **v1 默认 single-route（copilotkit.tsx:95）vs v2 默认 auto**：v1 世代部署的服务端多是老版本（只认信封模式），显式 single 最稳；v2 新部署让 /info 握手自动探测。一个 `?? true` 浓缩了两代默认值的分歧。
- **反向导出环 vs 严格分层**：理论上应让兼容层单向依赖新层，但 v2 是包的入口（index.ts 顶层就是 `export * from "./..."` v2 内容），v1 CopilotKit 必须从入口可见才能不破坏 `import { CopilotKit } from "@copilotkit/react-core"`——环是入口聚合的必然代价，用导出顺序控制初始化顺序。

## 六、新人提示（坑+勘误+延伸阅读）

- **坑（API 缺口）**：`useCopilotChat().visibleMessages/mcpServers/setMcpServers/runChatCompletion` 在运行时是 **undefined**（internal 返回对象缺 visibleMessages、注释掉 mcpServers 两行，use-copilot-chat_internal.ts:758-770）——TS 不报错因为接口还声明着（:157/:280）。用 `messages` 替代 visibleMessages；MCP 配置走 v2 途径。作者 TODO（use-copilot-chat.ts:105）表明此包装自身存废未决。
- **坑（StrictMode 双 connect）**：useCopilotChatInternal 的 connect effect 依赖 lastConnectedAgentRef + cleanup 置 null（:344-405），自写类似 effect 时照抄这个模式，否则开发模式 /connect 翻倍、生产正常——最难排查的一类"只在我机器上"问题。
- **别把 v1 hooks 当演进方向**：useCoAgent 380 行里大半是文档（NOTES-DIGEST batch-39 钉版），新代码直接用 v2 useAgent/useCopilotKit；v1 这层的价值是考古（API 为何长这样）与兼容（存量代码迁移面评估）。
- **effects 顺序是契约**：provider 内 didMountRef 的声明位置（:707-711）不是风格偏好而是正确性依赖——挪到文件前面就复现"孩子工具被清空"的 bug。改动 CopilotKitProvider 时先读 :678-684 注释。
- **数组 props 必须稳定**：renderToolCalls/frontendTools/humanInTheLoop 每 render 新字面量会在开发态收警告（:310/:417/:421），动态增删一律走 useFrontendTool/useHumanInTheLoop。
- 延伸阅读：第 2 篇（setter 们最终落在的 CopilotKitCore 与 AgentRegistry）；第 3 篇（useCopilotChatInternal 注释里点名的"V2 CopilotChat 模式"本体）；skills/react-core/references/client-side-tools.md（followUp 双轨与工具名唯一性）。
