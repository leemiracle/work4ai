# NeMo-Agent-Toolkit-UI 上手指南（ONBOARDING）

> 图谱基线：281 节点 / 507 边 / 14 层 / 14 步 tour @ commit `41cb8cf8`。164 个 TS/JS 源文件，Next.js 15 + React 18。全部结论带源码行号锚。

## 1. 定位：NAT 的聊天前端

本仓是 **NeMo Agent Toolkit（NAT）的官方 chat 前端**——流式响应、人在环（HITL）、OAuth 登录、中间步骤可视化、RAG 数据流监控、MCP 工具浏览。它自己不含任何 LLM 推理逻辑，所有智能都在 `NAT_BACKEND_URL` 指向的后端，本仓只负责「聊天 UI + 协议转换网关」两层。

常量中心 `constants/index.js:5-7` 定义品牌（APPLICATION_NAME/'Scout Bot'）；`constants/index.js:20-22` 把 HTTP/WS 公共前缀（默认 `/api`、`/ws`）做成环境变量可覆写。会话身份靠 cookie：`constants/index.js:13` 的 `SESSION_COOKIE_NAME`，由 `middleware.ts:20-35` 首访种下（30 天、**httpOnly:false**——因为浏览器 WebSocket API 无法带自定义 cookie 头，前端要亲手读它拼进 WS URL）。**浏览器永远只访问 3000 端口**，3099 是内部口。

## 2. 双服务器网关架构：3000 网关 + 3099 内部 Next

全仓最特殊的架构决策：`proxy/server.js` 是 488 行纯 Node 网关（CommonJS 无框架），对外只开一个口（`proxy/server.js:70`，默认 3000），按路径分流：

- **`/api/*`** → 先过 SSRF 白名单（`proxy/server.js:201`），剥前缀后按端点路由：五个特殊端点（chat/chat-stream/generate/generate-stream/ca-rag）走「fetch 后端+响应加工」（`proxy/server.js:219-223,307-311`）；`EXTENDED_BACKEND_TARGETS` 标 NEXTJS 的端点（如 update-data-stream，`constants/index.js:56-61`）转回内部 Next；其余透明代理到后端（324-330）。
- **其余一切** → Next dev/standalone server（`proxy/server.js:333-337`），目标 `NEXT_INTERNAL_URL` 默认 3099（71-72）。
- **WS upgrade** → `/ws` 校验后**重写为后端 `/websocket`**（`proxy/server.js:384`），自定义头用 `_ws_headers` base64 查询参数 smuggling（362-378），在 `proxyReqWs` 钩子还原（142-160）。

开发/生产**同构**：`package.json` dev = `node proxy/server.js` + `next dev -p 3099`；`Dockerfile:60-66,81-83` = standalone Next @3099 + 同一 proxy/server.js @3000。（勘误钉版：图谱批阶段曾记「生产走 next.config rewrites 不走此网关」——`next.config.js` 实际没有 rewrites，Dockerfile CMD 才是权威。）`proxy/server.js:425-427` 把 keepAlive/requestTimeout 归零以容 SSE 长流；CA-RAG 带会话级 init 去重（`proxy/server.js:90,252-304`）。

请求方向由 `proxy/request-transformers.js` 完成 UI→后端转换：chat 系 payload 锁死四基字段+保留字段过滤（75-103），ca-rag 包成 `{state:{chat:{question}}}` 三层嵌套（151-159）。

## 3. Chat.tsx：1850 行中枢与 WS 协议

`components/Chat/Chat.tsx` 是全仓最大单文件（1850 行），身兼四职：

**WS 生命周期**：`connectWebSocket`（`Chat.tsx:391`）拼 URL 时注入 session cookie 作查询参数（406-410）、conversation_id 支持重连续传（413-417）、设置页自定义 query/headers（420-488，headers 经 btoa 编码成 `_ws_headers`，与网关解码端 `proxy/server.js:362` 成对）。onopen 第一件事发送 OAuth 模式偏好帧（`Chat.tsx:514`，构造器在 `utils/app/const.ts:30-36` 单一事实源）——必须连接即发，redirect 模式会立刻导航走丢掉排队帧。断线重连 3 次、间隔 1s（392-393,550-559）。

**入站分发**：`handleWebSocketMessage`（`Chat.tsx:819`）按五类分流——OAuth consent（820）、裸 user_auth_error（843）、结构校验（851，校验器 `types/websocket.ts:197-219` 抛含原始 JSON 的错误）、activeUserMessageId 过滤丢停止生成后的迟到消息（867-876）、interaction 开模态（893）。状态变换全部委托 `utils/chatTransform.ts` 纯函数（34-148），组件只做编排——172 行纯变换层因此可独立测试。

**HTTP 双链路**：WS 模式关掉时走 fetch（`Chat.tsx:1165-1174`），按端点选 builder（`Chat.tsx:1130-1159`），422 workflow 错误渲染进助手气泡而非 toast（1181-1220）。

**流式解析**：模块级三件套 `extractSsePayloads`/`splitNdjson`/`parsePossiblyConcatenatedJson`（`Chat.tsx:80-179`）处理 SSE 帧、NDJSON 行与半包重组。**ref 写穿**（`updateRefsAndDispatch`，`Chat.tsx:648-670`）先改 ref 再 dispatch，防止 WS 高频消息读到过期 React 闭包。

## 4. 流内标签私有协议：intermediatestep / observabilitytraceid

这是前后端约定的私有协议，**没有进任何标准**：网关把结构化元数据以 XML 风格标签内联进纯文本流，前端再剥出来。

**注入端**（server）：`proxy/response-processors.js:21-46` 把后端 `intermediate_data: {...}` 行重组成 `{type:'system_intermediate',...}` 消息，JSON.stringify 后包进 `<intermediatestep>` 写回响应流（38-42）；`processObservabilityTrace` 同法生成 `<observabilitytraceid>`（48-60）。两者经 `processCommonLineTypes`（68-82）挂进 chat 与 generate 两套流处理器。

**剥离端**（client）：`Chat.tsx:1339-1363` 正则抽走完整 observabilitytraceid 标签；`Chat.tsx:1366-1378` 处理**标签被 TCP 分块切开**——开标签索引大于闭标签时把残段存 `partialIntermediateStep` 等下个 chunk 拼回（1333-1336）；完整标签在 1381-1400 提取 JSON、1403-1408 从正文删净。步骤再经 `utils/app/helper.ts:148` 的 `processIntermediateMessage` 做**树合并**：按 id+name 替换（160-186）、按 parent_id 挂父节点（188-239），形成嵌套执行树。

HTTP 非流式路径另有头部通道：网关把后端 `observability-trace-id` 头转成 `Observability-Trace-Id`（`response-processors.js:178-186`），前端双通道兜底（`Chat.tsx:1240-1242`）。

## 5. Markdown 渲染引擎（components/Markdown 群）

单条消息气泡 `ChatMessage.tsx` 把渲染管线委托给 Markdown 目录：`352-372` 渲染中间步骤区、`376-395` 渲染正文区，插件栈 remarkGfm+remarkMath+rehypeRaw（321-322）支持 GFM 表格、公式与内嵌 HTML。

关键文件四件：`MemoizedReactMarkdown.tsx:10-17` 局部覆写 urlTransform 放行 data: URI（react-markdown v9 默认剥掉 base64 内联图）；`CustomComponents.tsx:12-16` 是**工厂函数**，按 messageIndex 闭包生成 14 种元素映射，每个组件独立 memo + isEqual 深比较（code 17-49、chart 51-62）——流式期间只有变化节点重渲染。`CodeBlock.tsx` 提供 Prism 高亮+复制+下载（38-117），json 先做单引号替换与 pretty-print（22-36）。`CustomDetails.tsx:52-71` 是折叠面板展开策略：sessionStorage 记忆手动切换（54、88-93）、流式时最后一步展开并显示进度条（127-133）。

`ChatMessage.tsx:115` 挡掉「无正文且无步骤」的空气泡；图表走 `Chart.tsx`（recharts 七类 + force-graph）。

## 6. HITL 交互链与 OAuth 双模式

**HITL**：WS 的 system_interaction_message 在 `Chat.tsx:893-895` 打开 InteractionModal（`ChatInteractionMessage.tsx:35`），支持 text/binary_choice/radio/notification 四种 input_type（184-260）；notification 不开模态走 toast.custom（138-164）。倒计时 20% 剩余转红（8、173-182），归零报错关闭（85-91）。**刻意没有 Cancel/背景关闭**——强制回应是 HITL 语义。回答经 `Chat.tsx:297-331` 以 user_interaction_message 帧回传，携带原 thread_id/parent_id。

**OAuth** 双模式由 `NEXT_PUBLIC_NAT_OAUTH_MODE` 决定（`const.ts:24-25`，redirect 默认）。popup 模式（`Chat.tsx:611-633`）：window.open 不带 noopener（否则拿不到句柄），信任边界用 `event.source !== popup` 判别（625-632）。redirect 模式（634-642）：跳转前持久化触发消息（594-603），返回后 resume effect 重发并精确删 1 或 2 条（1594-1657）。**取消守卫防循环**是精髓：半途返回时置 `oauth_redirect_cancelled`（350-368、1619），自动重连 effect 检查它避免「重连→预检→又跳登录页」死循环（370-377），只有显式发消息才清（964-967）。

## 7. 安全防线：SSRF / 原型污染 / 开放重定向

前后端双层四模块：

- **网关 SSRF**：`utils/security/url-validation.js:26-79` 用 URL 构造器归一化（37）后比对 ALLOWED_PATHS 白名单（66-69，来源 `constants/index.js:84-87`），再查一遍 `..` 双保险（58-63）；WS 路径限定唯一值（90-99）；服务端 fetch 仅 http(s)（110-131）。测试覆盖 `%2E/%252E` 双重编码穿越。
- **媒体 SSRF**：`utils/media/validation.ts:6` 封禁私有 IPv4/IPv6 段（65-77）、危险协议、userinfo（48）、控制字符（23-28），data: 仅放行 png/jpeg（10-14）。
- **开放重定向**：`utils/security/oauth-validation.ts:6-29` 校验后端推来的 OAuth URL（空白符拒绝/仅 http(s)/无凭据/8192 上限），失败时 `Chat.tsx:823-831` 拒绝打开。
- **原型污染**：`utils/security/import-validation.ts:42-62` 递归剔除 `__proto__/constructor/prototype` 并限 5MB（20-24）；网关侧 RESERVED_FIELDS 过滤（`request-transformers.js:77`）是第二道防线。

## 8. 测试体系与 i18n 陷阱

Jest 串行跑（`package.json` `--runInBand`）。三个坑新人必知：①**i18n 空词典**——`next-i18next.config.js:4-27` 声明 22 种语言，但磁盘只有 `public/locales/en/common.json` 且内容是 `{}`：缺键返回键名，文案全是硬编码英文；②**WS 双套平行类型**——`types/websocket.ts`（249 行协议中枢+运行时守卫）与 `types/chat.ts:29-72`（简化同名接口）并存，改协议必须两边同步，运行时校验用前者（`Chat.tsx:852`）；③**测试替身**——`__mocks__/websocket.ts:85` 导入时整体替换 global.WebSocket，`jest.config.js:21-22` 把 react-markdown 与 next-i18next 映射到 mock；proxy-integration 需先起 3000 口否则静默跳过。`.DS_Store` 被归档进 components/ 下——无害但别再提交。

数据流可视化是独立子系统（`DATA_STREAMING.md` 权威）：`pages/api/update-data-stream.ts:111-236` 是内存态中枢（POST 覆写/GET 取流/PATCH 标记入库，**重启即失**），DataStreamManager 2s 发现流（85-108）、DataStreamDisplay 100ms 拉增量（59-74）。

### 新人第一天路线

1. `npm run dev` 起双进程，浏览器开 **localhost:3000**（不是 3099）；
2. 读 `proxy/server.js:180-340` 理解分流，再读 `constants/index.js` 全文；
3. 跟一条消息走完 `Chat.tsx:962→1110/1165→819→chatTransform.ts` 全链；
4. 改文案看 `ChatMessage.tsx` 与空词典陷阱；加安全规则先写 `__tests__/security/` 用例。
