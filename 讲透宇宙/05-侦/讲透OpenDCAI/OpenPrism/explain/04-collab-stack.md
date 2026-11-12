# 04 Yjs 协同全栈：手写 y-protocols 二进制 WS 协议

## 角色定位

OpenPrism 的多人实时协同是**跨前后端五节点**自研栈：前端 `collab/provider.ts`（179 行 WS 客户端）+ `EditorPage.tsx` 协同 effect（L1493-1542）；后端 `routes/collab.js`（HTTP+WS 双协议）+ `services/collab/docStore.js`（文档注册与广播中枢）+ `tokenService.js`（令牌签发）。核心特征：**没有用 y-websocket 库**，直接用 lib0 encoding/decoding + y-protocols/sync 手写二进制帧协议，两端对等实现 MESSAGE_SYNC=0 / MESSAGE_AWARENESS=1（provider.ts:8-9 / docStore.js:12-13）。

## 内部结构

`provider.ts`：`connect` L52 挂 doc/awareness 双监听；doc 更新处理器 L76-83 把本地 update 包成 SYNC 帧发走（origin 过滤防回环）；awareness 处理器 L84-98 编码客户端集。`openWebSocket` L111-160：URL 拼 `/api/collab?projectId&file&token`（L119-124），onopen 即发 `writeSyncStep1` 状态向量交换（L128-133）；断线指数退避重连 `min(10000,800×2^attempts)`（L154）。`handleMessage` L162-178 分帧：SYNC 走 `readSyncMessage`（回包>1 字节才发送），AWARENESS 走 `applyAwarenessUpdate`。

`docStore.js`：模块级 `docs Map`（L15）以 `projectId:filePath` 为 key。`getOrCreateDoc` L94-124 首建时读磁盘灌进 `ydoc.getText('content')`（L101-108）；`registerDocHandlers` L73-92 把 update 广播给同文档其他连接。落盘是 **800ms debounce**：`scheduleFlush` L61-71 → `flushDoc` L46-59 写文件并更新 project.json 的 updatedAt；间隔 `COLLAB_FLUSH_DEBOUNCE_MS=800`（constants.js:17）钉死。`setupConnection` L126-186：新连接先收 SYNC step1 + 全量 awareness；close 后无人则设 60s 清理计时器（L176-180）删 docs 条目。

`tokenService.js`：手搓 JWT 风格——`op1.<base64url(payload)>.<HMAC-SHA256>`（issueToken L21-27，签名 L17-19）；verifyToken L29-49 用 `crypto.timingSafeEqual` 防时序攻击（L39），校验版本/pid/role/exp（L42-44）。

## 外部连接

`routes/collab.js` 五端点：invite 签发 admin token（L11-16）、resolve 换项目名（L18-35）、flush 强制落盘（L37-45）、status 查连接数（L47-55）、WS 主通道（L57-105）。鉴权门 L62-69：非本机 IP 且无有效 token 直接 `close(1008)`；token 与 query 的 projectId 不一致也拒（L75-78）；非文本文件拒 1003（L90-93）；路径经 `safeJoin` 防穿越（L96）。前端 EditorPage：`collabCompartment`（L1366）热插拔 `yCollab(ytext, awareness)`（L1512）。

## 数据流

编辑传播：击键 → Y.Doc update → provider 发 SYNC 帧 → docStore 广播 + scheduleFlush → 800ms 后写盘。加入流程：项目页 `createCollabInvite` 生成分享链接 → 协作者打开 `/collab` → resolve 验 token → 跳编辑器 → WS 发 SyncStep1 → 服务端回差量 → yCollab 渲染远端光标（awareness 带 name/color，七色池 EditorPage.tsx:125）。

## 设计决策（含批判）

手写协议的收益是砍掉 y-websocket 依赖、重连策略自主可控；800ms debounce 平衡了写放大与丢失窗口。**安全观察（必录）**：`constants.js:11` 的 `COLLAB_TOKEN_SECRET` 存在硬编码开发默认值 `'openprism-collab-dev'`——环境变量未设时任何人可离线伪造 `op1.` 令牌直连 WS（L66 只拦"非本机且无 token"，有伪 token 即通过）。公网部署（tunnel 模式下必然）必须设 `OPENPRISM_COLLAB_TOKEN_SECRET`。其余批判：其一，**后端重启丢两样东西**：docStore 未 flush 的最后 800ms 编辑 + transfer.js:13 的 jobs Map（转换任务态同病，跨篇印证）；其二，单文件单 Y.Doc 粒度无跨文件事务；其三，60s 清理计时器会被重连 clearTimeout 保活（L129-132），设计对但 docs 无上限的内存风险未度量。

## 新人提示

调协同问题分三段：WS 建连（status 端点 L47-55 看 conns 数）、同步（SyncStep1/2 二进制帧，Network 面板看 ArrayBuffer）、落盘（flush 端点强制写）。改协议必须两端同改（provider.ts 与 docStore.js 分帧逻辑互为镜像）。公网部署先换 secret。
