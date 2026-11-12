# 01 · proxy/ 双服务器网关：流内标签的注入端

## 角色定位

`proxy/` 目录三件套（server.js 488 行、response-processors.js 335 行、request-transformers.js 168 行）是全仓唯一的服务端 Node 进程——一个**无框架、纯 CommonJS 的反向代理网关**。它存在的理由只有一个：浏览器只见 3000 一个口，后端 NAT server 与内部 Next（3099）之间的所有协议适配（路径重写、格式转换、流内标签注入、CORS、WS 升级）都发生在这一层。

## 内部结构

**入口与配置**：`NAT_BACKEND_URL` 必填、缺失即退出（`server.js:40-44`），并强制 http(s) 校验（`server.js:49-62`）；从中派生 HTTP/WS 双上游 origin（`server.js:64-67`）。网关口 `PORT` 默认 3000（`server.js:70`），Next 内部目标默认 3099（`server.js:71-72`）。

**两个 http-proxy 实例**：nextProxy 专管 Next（`server.js:96-102`，ws:true 支持 HMR）、backendProxy 管后端（`server.js:105-110`）；各有 502 错误处理（`server.js:113-133`），`proxyRes` 钩子统一加 CORS 头（`server.js:136-139`）。

**HTTP 分流主逻辑**（`server.js:180-338`）：`/api/*` 命中后——OPTIONS 预检直接 204（`server.js:191-198`）→ SSRF 白名单失败 403（`server.js:201-210`）→ 剥 `/api` 前缀（`server.js:213`）→ 五特殊端点判定（`server.js:219-223`）→ `doFetchAndProcess` 原生 fetch 转发+端点专属 processor（`server.js:226-249`）→ 非特殊端点查 `EXTENDED_BACKEND_TARGETS`，标 NEXTJS 者转回内部 Next（`server.js:314-321`），其余透明代理（`server.js:324-330`）；一切非 `/api` 流量无条件进 Next（`server.js:333-337`）。

**CA-RAG 特例**：`doCaRagWithInit`（`server.js:252-304`）用模块级 Set（`server.js:90`）记住 ragUuid-conversationId，首次 `/call` 前先 POST `/init`（`server.js:263-267`），失败透传状态码（`server.js:269-284`）。

**WS 升级**（`server.js:341-422`）：路径必须 `/ws`（`server.js:349-352`）且过校验（`server.js:354-359`，403 销毁 socket）；`_ws_headers` base64 解码挂到 `req._wsCustomHeaders`（`server.js:362-378`），路径**重写为后端 `/websocket`**（`server.js:384`）交 backendProxy.ws（`server.js:386-403`）；`proxyReqWs` 钩子还原 Origin/Protocol/Cookie/自定义头（`server.js:142-160`）。

**标签注入**（response-processors.js）：`processIntermediateData` 把后端 `intermediate_data:` 行重组成 `type:'system_intermediate'` 消息再包 `<intermediatestep>` 写回流（`response-processors.js:21-46`，写回在 `response-processors.js:38-42`）；`processObservabilityTrace` 生成 `<observabilitytraceid>`（`response-processors.js:48-60`）；`processCommonLineTypes` 公共分派（`response-processors.js:68-82`）；流结束残留缓冲兜底（`response-processors.js:90-95`）。五个 processor：chat-stream 按 SSE `data:` 行抽 choices 内容写纯文本（`response-processors.js:102-163`），chat 非流式四级回退 choices/message/answer/value（`response-processors.js:168-202`），generate 系保留原始 data 帧（`response-processors.js:207-292`），ca-rag 三级回退（`response-processors.js:299-326`）。

## 外部连接

上游依赖 constants（路由白名单唯一来源，`server.js:12-22` import）与 url-validation（`server.js:25-28`）；下游是浏览器 fetch 与 Chat.tsx 的 WebSocket。request-transformers 被 `Chat.tsx:62-67` import 用于 HTTP 发送——同一转换逻辑被前端 TS 与网关 JS 共享。Dockerfile 把 proxy/constants/utils 三目录 COPY 进 runner 层（`Dockerfile:65-66`），CMD 与 dev 同构双进程（`Dockerfile:81-83`）。

## 数据流

请求向：UI `POST /api/chat/stream` → SSRF 校验 → 剥前缀 → body 原样透传（`server.js:226-238`）→ 后端。响应向：字节流按 `\n` 切行、残行回 buffer（`response-processors.js:127-131`），`data:` 行提取内容（`response-processors.js:134-150`），`intermediate_data:`/`observability_trace:` 行转标签（`response-processors.js:68-82`），前端最终收到「纯文本+内联标签」混合流。

## 设计决策

①**双服务器而非 Next API routes 承载代理**：WS 升级、流式 pipe、跨域 cookie 转发在 Next route handlers 里都别扭，原生 http + http-proxy 最直接；②**fetch 后再加工而非 pipe 直通**：只有读完再重组才能注入 UI 私有标签，代价是一跳延迟；③**`_ws_headers` 查询参数 smuggling**：浏览器 WebSocket API 不能设自定义头，借 URL 通道过代理再还原，是已知模式的干净实现；④超时归零（`server.js:425-427`）专为 SSE 长流拆 Node 默认超时墙。

## 新人提示

改路由先改 `constants/index.js` 的 CORE_ROUTES/EXTENDED_ROUTES（`constants/index.js:84-87` 白名单自动跟上），别在 server.js 硬编码；新增特殊端点要在 `server.js:219-223` 加判定、response-processors 加 processor、`server.js:307-311` 加路由**三处同步**；`__tests__/proxy/proxy-integration.test.js` 需真起 3000 口否则静默跳过；`proxy/` 是 CommonJS，`server.js:9-13` 的 ESLint disable 注释别「顺手修掉」。
