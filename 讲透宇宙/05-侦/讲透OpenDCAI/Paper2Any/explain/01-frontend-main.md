# 01 · 前端主链：路由、认证、状态与 HTTP 生成层

## 角色定位

`frontend-workflow/` 是 Paper2Any 的 React 单页应用（Vite + TypeScript + Tailwind），承担整个平台的用户入口：20 个功能页（paper2ppt/paper2video/paper2poster/paper2citation/knowledge……）、认证计费门面、以及可视化编排画布。它不引入任何前端路由库与重型 HTTP 库——**路由是 App.tsx 里手写的 History API 双轨状态机，HTTP 是 backendClient 生成的双鉴权 fetch**（全仓无 axios 依赖，`package.json` grep 实证；任务书所述"axios 生成层"按源码勘误为"fetch 头生成层"）。这一定位决定了它的全部设计：小依赖、大自持、状态单仓。

## 内部结构

**路由层（App.tsx 332 行）**：`pageIds` 20 个页面 id（App.tsx:30-51）映射 `pagePaths` 路径表（App.tsx:57-78）；`getPageFromLocation`（App.tsx:112-124）先查 legacy hash（`getPageFromLegacyHash`，App.tsx:98-110，把 `#/paper2ppt` 这类旧 URL 归一化回 path），再查 pathname，未知路径回落 `DEFAULT_PAGE`。`useEffect`（App.tsx:138-160）注册 `popstate` 监听并在初次挂载时调 `syncPageFromLocation`——发现 hash 或路径不一致时用 `history.replaceState`（App.tsx:150）把 URL 规范化为干净 path；页面切换 `handlePageChange`（App.tsx:162-177）走 `pushState`（App.tsx:175）。页面渲染是最朴素的 `{activePage === 'xxx' && <XxxPage/>}` 条件挂载（App.tsx:239-259），FilesPage 与 AccountPage 以模态框形式复用（App.tsx:264-301）。

**挂载链（main.tsx:10-19）**：`StrictMode → AuthProvider → RuntimeConfigProvider → AuthGate → App`。AuthProvider（56 行）做会话生命周期：`getSession` 恢复 + `onAuthStateChange` 订阅，遇匿名会话直接 signOut（AuthProvider.tsx:29-33）。

**认证三态（authStore.ts 494 行 + AuthGate.tsx 95 行）**：AuthGate 按"未配置 Supabase → E2E 旁路 → loading → OTP 待验证 → 未登录 → 已登录"顺序分流。三处关键：①`isSupabaseConfigBypass`——Supabase 未配置时整棵应用免登录直通（AuthGate.tsx:44-46），配合 supabase.ts 的 null 单例（supabase.ts:22-30）构成"无云自部署"形态；②`isE2EAuthBypassed`（AuthGate.tsx:22-31）仅在 `import.meta.env.DEV` 下读 `localStorage.paper2any_e2e_bypass_auth === "1"` 放行，生产构建恒 false，另有 `window.__PAPER2ANY_E2E__` mock 钩子同样 DEV-only（authStore.ts:475-494）——测试后门被编译期钉死；③邮箱 OTP 流：`signUpWithEmail` 检测 `data.user && !data.session` 时置 `needsOtpVerification`（authStore.ts:170-177），AuthGate 据此切到 VerifyOtpPage（AuthGate.tsx:65-75）。

**OTP 页六格输入（VerifyOtpPage.tsx 203 行）**：`otpLength` 默认 6、粘贴 8 位码自动切 8 格（VerifyOtpPage.tsx:77-86，`setTimeout(..., 50)` 等格子重渲）；单数字自动跳格、末格集齐自动提交（VerifyOtpPage.tsx:60-62）、Backspace 空格回跳（VerifyOtpPage.tsx:67-69）、60 秒重发冷却（VerifyOtpPage.tsx:108）。

**邀请码补偿环（authStore.ts:369-393）**：`claimInviteCode` 失败时把码存 `localStorage.paper2any_invite_code`（authStore.ts:385），此后每次登录/注册/OTP/手机登录成功都尝试补兑并清除（authStore.ts:136-144、187-195、227-235、301-309）——注册页只负责先存码（RegisterPage.tsx:80-81），兑换统一 POST `/api/v1/account/invite/claim`（authStore.ts:65）。

**状态与 HTTP 层**：Zustand 仅此一家 `useAuthStore = create<AuthState>()`（authStore.ts:83）——"工厂"实为单 store 直建，用户态/配额/OTP 挂起位全在；配额刷新 `refreshQuota` 动态 import quotaService（authStore.ts:448）并静默失败。HTTP 侧 `getBackendHeaders`（backendClient.ts:6-23）先塞 `X-API-Key`，再异步取 Supabase access_token 塞 `Authorization: Bearer`，`backendFetch`（backendClient.ts:25-31）将其注入原生 fetch；config/api.ts 的 `apiFetch`（api.ts:46-59）是同一头的再包装。quotaService 自带 10s TTL + 60s stale 缓存与 inflight 去重（quotaService.ts:23-27）。

**ReactFlow 可视化编排（WorkflowCanvas.tsx 185 行）**：ReactFlow 画布 + `useNodesState/useEdgesState`（WorkflowCanvas.tsx:30-31）；拖放建图 `onDrop` 解析 `application/reactflow` 数据、`reactFlowInstance.project` 换算坐标、id 取 `${agentType.id}-${Date.now()}`（WorkflowCanvas.tsx:106-136）。两处架构补丁：①**setTimeout(0) 延迟同步**——`handleNodesChange/handleEdgesChange` 在 ReactFlow 内部 onChange 后用 `setTimeout(() => setNodes(nds => { onNodesChangeCallback(nds); return nds; }), 0)`（WorkflowCanvas.tsx:39-45、52-58）借 setNodes 函数式读取"已提交"的最新状态再回调父组件，绕开 onChange 时刻状态尚未落定的时序问题；②**window 全局逃生舱**——`(window as any).workflowCanvasAPI = { updateNode, deleteNode }`（WorkflowCanvas.tsx:80-83）把修改能力挂到全局，供无法传递 props 的兄弟组件（如 NodeConfigPanel）直接调用。

## 外部连接

- **后端 FastAPI**：全部请求经 backendFetch 双鉴权打到 `/api/v1/*`；配额走 quotaService → 后端 `/quota`；邀请码 → `/api/v1/account/invite/claim`。
- **Supabase**：lib/supabase.ts 单例（anon key + RLS），AuthProvider 订阅其会话事件；手机号经 `normalizePhoneE164China`（authStore.ts:57-62）补 `+86` 前缀走短信 OTP。
- **运行时配置**：RuntimeConfigProvider/runtimeConfigService 提供计费模式等后端下发配置，quotaService 读 `getRuntimeConfigSync().billing_mode`。
- **静态资产**：backendClient 的 `normalizeBackendAssetUrl`（backendClient.ts:57-86）把后端返回的 `/outputs/` 相对路径补全为当前 origin，并做 http→https 同主站协议升级。
- **下游组件**：App.tsx 只挂页面级组件；ReactFlow 四件（WorkflowCanvas/CustomNode/NodeConfigPanel/AgentNodePanel）与 AgentNodePanel 的拖拽源、NodeConfigPanel 的 `system_prompt/task_prompt` 双提示词编辑器（NodeConfigPanel.tsx:277-291）均在此层定义。

## 数据流

冷启动：main.tsx 挂载链 → AuthProvider `getSession` 恢复会话（无配置则 `setSession(null)` 直接放行）→ RuntimeConfigProvider 拉计费配置 → AuthGate 三态判定 → App 渲染。路由流：URL/hash → `getPageFromLocation` → setActivePage →（需要时）replaceState 规范化；反向：侧边栏点击 → handlePageChange → pushState + setActivePage。登录流：LoginPage → authStore.signInWithEmail → Supabase → setSession → refreshQuota（后端返回 mock 数据兜底未鉴权态，authStore.ts:98-99 注释）。每次鉴权成功都串行执行"邀请码补兑 → 配额刷新"两连。画布流：AgentNodePanel 拖出节点 → WorkflowCanvas onDrop 建节点 → 点击选中 → NodeConfigPanel 经 window.workflowCanvasAPI.updateNode 回写参数。

## 设计决策（含批判）

1. **手写路由而非 react-router**：20 页静态枚举 + 双轨兼容，零依赖零学习成本；代价是没有嵌套路由、没有路由参数、没有代码分割——20 个页面全部同步 import（App.tsx:2-28），首屏 bundle 全量加载。
2. **legacy hash 双轨是一次性迁移垫片**：hash 优先于 pathname（App.tsx:113-117）+ replaceState 抹平，意味着老书签永久有效但也意味着"hash 永远赢"——若未来某页面真需要 hash 锚点会被此逻辑劫持。
3. **认证后门 DEV-only 是正确姿势，但 localStorage 开关仍是弱点**：E2E 旁路依赖 `import.meta.env.DEV` 编译期剪枝（AuthGate.tsx:23），生产不可触发；不过开发服务器若暴露公网，设置一个 localStorage 键即可免登录，内网开发环境需自警。
4. **window.workflowCanvasAPI 全局逃生舱是 React 反模式的双刃剑**：它绕开 props 钻井解决兄弟通信，但也意味着**单画布假设**——两个 WorkflowCanvas 同屏会互相覆盖全局 API；且无 TypeScript 类型约束。
5. **最重的批判：ReactFlow 编排四件是"已建成、未接线"的孤岛资产**。全 src 精确 grep 实证：WorkflowCanvas 无任何外部 importer，AgentNodePanel、NodeConfigPanel 同样零消费者（CustomNode 仅被 WorkflowCanvas 引用），App.tsx 与 MindMapPage 均未挂载它们——即用户在当前产品里**看不到**这套可视化编排。setTimeout(0) 与全局 API 这两个"补丁"服务的正是一条尚未上线的功能线。读代码时不要把 WorkflowCanvas 当活跃链路。
6. **authStore 一仓通吃**：494 行里塞了邮箱/OTP/手机/OAuth/邀请码/配额六域，单 store 直建无切片；规模尚可，但每条登录路径都复制一遍"补兑邀请码"四行块（出现 4 次，authStore.ts:136-144 等），是该抽公共函数未抽的重复。
7. **HTTP 层双鉴权每请求现取 session**：getBackendHeaders 每次 `supabase.auth.getSession()`（backendClient.ts:12），无 token 缓存——正确性优先（永不过期 token）换少量开销，配合 quotaService 的 inflight 去重，性能账算得清。

## 新人提示

- 改页面清单只动两处：`pageIds`（App.tsx:30）与 `pagePaths`（App.tsx:57），再加 import 和一行条件渲染，路径映射与 hash 兼容是自动的（`pathToPage` 同时注册 path 与 page id 两种键，App.tsx:88-96）。
- 认证调试先看三个闸门变量：`isSupabaseConfigured()`（env 有没有配）、`loading`（AuthProvider 是否完成首查）、`needsOtpVerification`（是否卡在 OTP 态）；E2E 免登录用 `localStorage.setItem('paper2any_e2e_bypass_auth','1')`（仅 dev server）。
- 所有后端调用请走 `backendFetch`/`apiFetch`，别裸 fetch——否则丢 `X-API-Key` 会被 FastAPI 的 APIKeyMiddleware 拒掉。
- 想接 ReactFlow 画布时，记住 updateNode/deleteNode 在 `window.workflowCanvasAPI`（WorkflowCanvas.tsx:80），且节点变更回调晚一拍（setTimeout(0)）是刻意设计，别"修复"它。
- 手机号必须 11 位国内格式，`+86` 由 `normalizePhoneE164China` 自动补，不要自己拼国际前缀。
