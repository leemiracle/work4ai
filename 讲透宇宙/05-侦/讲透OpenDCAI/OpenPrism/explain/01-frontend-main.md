# 01 前端主链：main.tsx / App 路由 / client.ts / vite 代理

## 角色定位

这一层是 OpenPrism 前端的"脊柱"：`main.tsx`（18 行）完成 React 挂载与三重 Provider 包裹，`App.tsx`（17 行）定义全部 4 条路由 + 1 条兜底，`api/client.ts`（558 行）把后端全部 HTTP 面（44 个导出函数 + 内部 `request` 封装，合计 45 个函数）收进单文件，`vite.config.ts`（23 行）用两条代理规则把开发期请求转发到 Fastify 后端与 SwiftLaTeX 云端。理解这四个文件，就掌握了前端到后端的全部通道。

## 内部结构

`main.tsx:10-18`：`createRoot` 挂载，`React.StrictMode` → `I18nextProvider`（i18n 实例在 `src/i18n/index.ts` 初始化，zh-CN 默认）→ `BrowserRouter` → `App`。无全局状态库，跨页共享全靠 localStorage。

`App.tsx:10-14` 五条路由：`/`→LandingPage（营销页，打字机动画）、`/projects`→ProjectPage（995 行，项目列表/导入/设置）、`/editor/:projectId`→EditorPage（5560 行巨兽，见第 2 篇）、`/collab`→CollabJoinPage（45 行，邀请 token 落地页）、`*`→重定向 `/projects`。

`client.ts` 分四段：L1-51 九个接口类型（ProjectMeta/TemplateMeta/ArxivPaper 等）；L53-56 `API_BASE=''` 与三个存储键（`openprism-lang`/`openprism-collab-token`/`openprism-collab-server`）；L97-115 核心函数 `request<T>`——合并 `x-lang` 语言头（L100）、`Authorization: Bearer` 协作 token（L91-95），有 body 自动补 Content-Type，非 2xx 直接 `throw new Error(await res.text())`；L117-558 按域分组的 44 个导出函数：项目 CRUD 13 个、文件操作 8 个、协作 4 个、agent/编译/模板/arXiv/plot/LLM 各 1-2 个、transfer 4 个、MinerU transfer 2 个。

## 外部连接

`vite.config.ts:8-20` 两条代理：`/api`→`http://localhost:8787`（`ws:true`+`xfwd:true`，WebSocket 与真实 IP 透传，协作通道复用它）；`/texlive`→`https://texlive.swiftlatex.com`（L18 rewrite 剥掉前缀）。后端端口由 `apps/backend/src/config/constants.js:10` 的 `PORT=8787` 钉死，与代理目标闭环。生产模式无 Vite：后端 `index.js:60-78` 直接 serve `frontend/dist` 并做 SPA fallback，同源相对路径两态通用。

## 数据流

一次典型调用：页面调 `runAgent()`（client.ts:279-296）→ `request` 拼头 → Vite 代理 → 后端 preHandler（index.js:34-44）校验协作 token → Fastify 路由。语言流：localStorage `openprism-lang` → `getLangHeader()`（L58-62）→ `x-lang` 头 → 后端 i18n 错误文案本地化。特殊流两条：`importArxivSSE`（L401-434）用原生 `EventSource` 收 progress/done/error 三事件做导入进度；四个 FormData 上传（`uploadFiles` L232、`importZip` L381、`visionToLatex` L436、`mineruTransferUploadPdf` L542）绕开 `request` 手写 fetch，因为 body 不能预设 JSON Content-Type。

## 设计决策（含批判）

`API_BASE=''` 相对路径是聪明的一手——开发代理与生产静态托管零配置切换。SSE 选 EventSource 而非 fetch-stream 是取其自动重连，但代价是 EventSource 不能带自定义头，token 只能塞 query 参数（L409），与 header 方式并存形成两种鉴权姿势。批判三点：其一，45 个函数单文件无模块切分，项目域/协作域/transfer 域完全可以拆目录；其二，四个 FormData 函数重复同一段错误处理模板，`request` 缺一个 `form()` 变体；其三，错误抛 `Error(res.text())`——后端返回的 JSON 错误串被当 message 用，上层 `err.message` 展示给用户时会露出原始 JSON。

## 新人提示

加新接口的固定动作：在 client.ts 按域追加函数 → 确认后端路由前缀是 `/api`（否则代理不通）→ 需要鉴权时走 `request`，上传走手写 fetch 模板。改路由路径记得 App.tsx 与后端 SPA fallback（index.js:71-77）两处都对 `/api` 前缀敏感。调试 401 先看 sessionStorage 里有没有 collab token、请求是否来自非本机 IP（后端 `requireAuthIfRemote` 只对远程强制）。`/texlive` 代理目前前端源码零消费者（详见第 6 篇勘误），别被它误导去连 SwiftLaTeX。
