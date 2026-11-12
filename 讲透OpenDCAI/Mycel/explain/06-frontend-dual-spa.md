# 06 · 前端双 SPA：app 主工作台与 monitor 观测台

## 角色定位

`frontend/` 下是两个完全独立的 SPA 工程：**frontend/app** 是用户主工作台（React + react-router + zustand + Vite，约 213 个 ts/tsx 源文件的一半以上在此）——聊天、联系人、agent 雇佣、市场；**frontend/monitor** 是运维观测台（独立 package.json/vite.config.ts，对应后端 `/api/monitor` 路由，01 篇 FULL 形态才挂载）——沙箱列表、资源快照、操作审计。两者不共享构建与状态，只共享后端 API。前端与后端的解耦点是一个运行时注入的小机关：`__MYCEL_CONFIG__.apiBase` 让同一份静态产物可以指向任意后端地址。

## 内部结构

**app 主工作台**。入口 `main.tsx`（frontend/app/src/main.tsx:5-13）挂 RouterProvider + sonner Toaster；路由树（frontend/app/src/router.tsx:21-49）分五组：chat（含 hire/thread/:threadId、hire/new/:agentId、visit/:chatId 三类会话入口）、contacts（agents/:id、users/:userId 详情）、marketplace（列表+详情）、library/:type/:id（技能等库物件）。状态管理是 **4 个 zustand store**（frontend/app/src/store/）：`auth-store`（JWT+身份，persist 中间件落 localStorage，auth-store.ts:5 注释自述）、`app-store`、`conversation-store`（会话列表与消息）、`marketplace-store`（市场物件，API 前缀 `/api/marketplace`，marketplace-store.ts:4）——注意是四个不是三个，auth 也算一个独立 store。工具调用的可视化集中在 `components/tool-renderers/`：`ToolRenderer.tsx:12-39` 一个 switch 按 step.name 分派到 **9 路**渲染器（Edit/Write/Bash/Read/ListDir/Grep+Glob 共用 Search/WebFetch+WebSearch 共用 Web/Task 系五名共用 Task，兜底 DefaultRenderer）——渲染器按"语义类"而非"工具名"归组，新工具名只要落进已有语义类就零代码适配。市场组件里还有 `LineageTree.tsx`（物件血缘树）与一排 wording.test.tsx——**文案级测试**是这个前端的特色。chat-area 里 ToolDetailBox 按工具状态四色（calling/done/error/cancelled，ToolDetailBox.tsx:17-24）。

**monitor 观测台**。独立 vite 工程：`vite.config.ts:12` 用 `loadMonitorPorts()` 决定 dev 端口；`monitor-ports.ts:11-28` 的 `resolveMonitorPorts` 是**三级回退**解析器——环境变量（LEON_BACKEND_PORT/LEON_MONITOR_BACKEND_PORT/LEON_MONITOR_PORT/LEON_MONITOR_PREVIEW_PORT）→ git worktree 配置（worktree.ports.backend/monitor-backend/monitor-frontend/monitor-preview）→ 默认值（后端 8001、monitor dev 5174、preview 4174）。worktree 读取器在 dev-ports.ts:4-9，用 `execSync("git config --worktree --get <key>")`——**与后端 01 篇同一套 worktree.ports.* 约定**，一个 git worktree 一套端口，多实例并行开发不串台。

monitor 的灵魂是"更名史即测试史"。这仓经历过 sessions→sandboxes 的命名迁移，迁移不是删代码完事，而是**用测试把旧词钉死在棺材里**：
1. `monitor-nav.test.ts:11-14`——"treats sandboxes as the canonical runtime shell"：导航必须有 `/sandboxes`，且遗留路径 `/operations/op-1` 必须 resolve 到 `/sandboxes`（旧路永固重定向）。
2. `ResourcesPage.contract.test.js:16-43`——"does not describe internal resource rows as sessions"：**直接 readFileSync 源码文件**，断言 ResourcesPage.tsx 与 styles.css 里不再含 `runningSessionCount`、`sandbox-session-row`、`关联 session` 等十余个旧 token——合同测试防复活。
3. `SandboxesPage.test.ts:41-59`——"does not expose local runtime ids in visible row data"：本地运行时实例 id（leon-runtime- 前缀）不得出现在渲染行数据里，JSON.stringify 后断言不含前缀。

第 2、3 个测试还暴露一个反 grep 技巧：被禁的 token 在测试里用字符串拼接构造——`["lea", "se", "Id"].join("")`（ResourcesPage.contract.test.js:8）、`["leon", "runtime"].join("-") + "-"`（SandboxesPage.test.ts:6 与 SandboxesPage.tsx:40 同款）——**这样测试源码本身也不会被简单 grep "leon-runtime" 或 "leaseId" 搜到**，同时生产代码 SandboxesPage.tsx:44-45 把本地实例 id 显示为无链接的 "local runtime" 标签，内部 id 不外泄到 UI。

**apiBase 运行时注入链**（四处接力）：`frontend/app/Dockerfile:15-18` 把 docker-entrypoint.sh 拷进镜像作 CMD → 容器启动时 `docker-entrypoint.sh:3-6` 用 heredoc 现写 `/usr/share/nginx/html/config.js`：`window.__MYCEL_CONFIG__ = { apiBase: "${API_BASE:-}" }`，再起 nginx → `index.html:8` 无条件 `<script src="/config.js">`（构建产物里这个文件不存在，只有运行时才有）→ `auth-store.ts:11-19` 读取：`window.__MYCEL_CONFIG__?.apiBase ?? import.meta.env.VITE_API_BASE ?? ""`，空则用相对路径（同源部署）。**同一个镜像，改一个环境变量就换后端**——构建时配置被彻底推迟到启动时。

## 外部连接

- app → 后端全量 API：threads/messages/SSE（api/chat-events.ts、sse-processor.ts 消费 04 篇的事件流）、auth、contacts、marketplace、settings；monitor → `/api/monitor` 前缀（monitor_threads、global_router）与 03 篇的沙箱/孤儿数据。
- 两 SPA 互不 import；共享的只有 API 语义与 `frontend/monitor/src/resources` 一层薄契约（ResourcesPage.contract.test.js 同时盯 types.ts）。
- 部署形态：app 由 nginx 托管（entrypoint 写 config.js 到 html 根），monitor 有独立 dev/preview 端口约定，生产同样走后端静态托管或独立部署。

## 数据流

用户登录：auth-store 拿 token 持久化 → 所有 API 调用走 client.ts（API_BASE 已在 store 初始化时定死）→ 进入 chat 页发消息 → conversation-store 经 streaming.ts 建立 SSE → 每条事件里的工具步骤按 step.name 进 ToolRenderer 九路分派渲染 → 权限 ask 事件渲染成可点卡片，resolve 回调打回 04 篇的 permissions 端点。运维侧：monitor 打开 /sandboxes → 请求 `/api/monitor` 沙箱清单（含孤儿）→ buildSandboxWorkbenchShell 组装行数据（本地运行时在此被脱敏成 "local runtime"）→ 分诊卡（active_drift/detached_residue/orphan_cleanup/healthy_capacity 四类，SandboxesPage.test.ts:13-19 可见）。部署侧：CI 构建一次镜像 → 运维在任何环境起容器时给 API_BASE → entrypoint 写 config.js → 用户浏览器加载到的 config.js 即该环境后端地址。

## 设计决策（含批判）

1. **双 SPA 而非单 SPA 两路由**：用户台与运维台的发布节奏、权限模型、体积完全不同——monitor 不需要聊天组件，app 不需要分诊表。代价是两份构建配置、两套依赖升级，小修动两处。
2. **渲染器按语义类归组**（9 组件而非 N 工具）：TaskCreate/Update/List/Get 共用一个 TaskRenderer，新工具落语义类内零适配；只有真正新语义（如未来 MCP 专属展示）才加组件。这是"开放式封闭"在前端的低糖版本。
3. **命名迁移用测试钉棺材**：readFileSync 源码 + 断言 token 不存在，把"旧词复活"变成 CI 失败——比 code review 可靠。拼接构造 token（join("")）既防测试自身被 grep 误判，也是个善意的谜语：读懂它的同时你就理解了为什么它存在。
4. **apiBase 三级回退**（运行时 window → 构建时 env → 同源相对路径）：覆盖三种部署（容器任意后端/静态托管单环境/本地 dev），代价是排查"打到了错误后端"时要多想一层 window 配置从哪来——浏览器 console 看 `window.__MYCEL_CONFIG__` 是第一诊断动作。
5. **端口三级回退与后端同约定**：worktree.ports.* 是全仓多实例开发的地基，前后端各自解析但键名一致。批判：两处解析逻辑（01 篇 Python / 本篇 TS）没有共享测试互证，若键名改动只有人力保证同步。

## 新人提示

- 前端跑不起来先看两件事：monitor 的端口被谁占了（`git config --worktree --get worktree.ports.monitor-frontend` 查本 worktree 约定值）；app 请求 404 先在 console 看 `__MYCEL_CONFIG__` 是否被注入了错误 apiBase。
- 加新工具的可视化：先判断它属于哪个语义类（文件写/读/搜索/命令/web/task），九成情况只是 ToolRenderer.tsx:13-36 的 case 表加一个名字；只有新语义才建组件。
- 改 monitor 文案时若 CI 爆 ResourcesPage.contract.test，不是误报——你把被埋葬的旧词挖出来了；按新命名体系改写，而不是改测试。
- 别在前端源码里写 "leon-runtime" 或被禁 token 的完整字面量——测试用 join 拼接是有原因的，完整字面量会同时污染生产代码与测试的 grep 面。
- marketplace 的数据形状（MarketplaceItemSummary，marketplace-store.ts:6-22）与后端 marketplace 路由一一对应，改字段要前后端同步；wording.test.tsx 系列盯的是用户可见文案，改按钮文字先跑它们。
