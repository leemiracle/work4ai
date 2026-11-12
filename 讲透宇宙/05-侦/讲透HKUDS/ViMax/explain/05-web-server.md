# 05 · web/server.mjs — 零依赖 HTTP 桥：SSE + 13 路由 + 子进程管理

> 源文件：`web/server.mjs`（321 行）。行号锚均从源码核实（commit fd4b72e7）。

## 1. 角色定位

server.mjs 是 Web 控制台的**桥接服务**：一个约 320 行的单文件 Node 服务器，同时扮演三个角色——①REST API（13 个 `/api/` 路由，:36-110，管会话/配置/历史/产物/上传/agent 启停/健康检查）；②SSE 事件总线（`/api/events`，:36，把 Python 引擎的 JSONL 事件流广播给所有浏览器标签页）；③**agent 进程管理器**（spawn/kill `main_agent.py`，:142-195/:232-243）。它是 ONBOARDING §5"TS→Python 跨语言桥"决策的 Web 侧落地：Web 前端不直接碰 Python，全靠这个桥 spawn 无头 CLI 并转发事件，进程边界即协议边界。

"零依赖"要精确理解：server.mjs 本体只 import `node:fs`/`node:http`/`node:path`/`node:child_process` 等**Node 内建模块**加两个本地 .mjs（:1-16）——后端桥无任何 npm 依赖；但 web 工作区的 package.json 仍有 react/vite 等 dependencies，那是给 Vite 前端（层 10）与 config-store.mjs 的 yaml 解析用的（config-store.mjs:3 `import {parse, stringify} from 'yaml'`）。服务桥本身零第三方包，这是它能随 `node server.mjs` 秒起、不碰 node_modules 的原因。

## 2. 内部结构

**启动配置（:18-29）**：webRoot/repoRoot 定位（:18-19，ESM 下用 `fileURLToPath` 取自身路径再 `..` 回仓根）；`--dev` 开关（:20）；默认绑定 `127.0.0.1:4173`（:21-22，**只听本机回环**，安全默认）；上传上限默认 100MB、可经 `VIMAX_WEB_UPLOAD_MAX_BYTES` 调（:23-26）；模块级状态三件：`subscribers`（SSE 连接集合，:27）、`agentProcess`（:28）、`activeSessionId`（:29）。

**请求处理主函数（:33-125）——密集 if 链，无框架路由表**。13 个 `/api/` 路由按"路径+方法"逐个 if 命中：

- 会话组：`GET /api/sessions`（:39，读 .vimax 会话状态）、`DELETE /api/sessions?session=`（:50-61，删除前先 404 校验存在性 :53-55，删的是活动会话则先杀 agent :56，删完广播 sessions_changed :59）；
- 配置组：`GET/PUT /api/config`（:42-49，读写 agent.local.yaml；PUT 成功后 `stopAgent('config')` :47——改配置必须重启 agent 才生效）；
- 内容组：`GET /api/history`（:62）、`GET /api/artifacts`（:65，产物树）、`GET /api/artifact`（:68，流式取单个产物，:296-304 用 `createReadStream().pipe()` 不整读内存）；
- 上传：`POST /api/uploads`（:71-85，先查 content-length 拒超限 :78-81，再流式读并边读边验 :82）；
- agent 组：`POST /api/agent/start`（:86-95，项目名 ≤64 字符校验 :90-92）、`POST /api/messages`（:96-103，**交互的唯一入口**——往 agent 进程 stdin 写一行文本 :101，agent 没跑则 409 :100）、`POST /api/agent/stop`（:104-107）、`GET /api/health`（:108-110）；
- 事件流：`GET /api/events`（:36，SSE，见下）。

命中不到 `/api/` 时：`/assets/vimax.png` 直接 pipe（:111-115）；dev 模式交给 Vite 中间件（:116-119）；生产模式走 `serveProductionApp`（:120,:306-315）——SPA fallback：任何路径先在 `dist/` 下找文件，找不到一律回 index.html；:310 的 `startsWith(distRoot + sep)` 检查是**路径穿越防线**（`/../` 类请求被兜回 index.html 而非读任意文件）。

**`startAgent`（:142-195）——spawn 全流程**：先互斥校验（newSession 与 sessionId 二选一，:143）；杀旧进程（:144）；经 `agentCommand()`（:245-256，**四级回退链**：`VIMAX_AGENT_COMMAND` 自定义命令 → `VIMAX_PYTHON_CMD` → `~/.local/bin/uv run python` → 仓内 `.venv/bin/python3` → 裸 `uv run python`）；spawn `main_agent.py --jsonl --stdin-repl` 加会话参数（:152）。**stdout 是手写行缓冲器**（:158-167）：chunk 累积、按行切、`lines.pop()` 把残行留回缓冲——TCP 分片劈开 JSON 行时不会解析坏；每个完整行交 `consumeAgentLine`。每个回调都带 `if (agentProcess !== child) return` 世代守卫（:162,:170,:176,:180,:189）——旧进程被替换后其残余事件不再广播。exit 时按 code/signal 区分 stopped/error（:179-187）；启动后 350ms 补一轮 sessions_changed + ready 广播（:188-194，等 Python 侧把会话文件写好）。

**`consumeAgentLine`（:197-209）——JSONL→SSE 的归约**：每行 `JSON.parse`，成功则 broadcast（遇 `session` 事件同步 activeSessionId :201 并触发会话列表刷新 :203-205）；**解析失败不丢弃**，降级为 `terminal` 事件广播（:206-208）——Python 侧裸 print 也能在 Web 上看到。

**`openEventStream`/`broadcast`（:211-230）——SSE 总线**：标准 `text/event-stream` 头 + `X-Accel-Buffering: no`（:212-217，防 nginx 缓冲）；连接即推一条初始 bridge_status（:218）；15s 心跳注释帧保活（:220）；`broadcast`（:227-230）把事件 JSON.stringify 后 `data: ...\n\n` 写给所有订阅者。

**`stopAgent`（:232-243）**：SIGTERM + 按 reason（switch/config/user）选人话文案广播。**`shutdown`（:317-321）**：SIGINT/SIGTERM（:139-140）→杀 agent→server.close→1s 兜底强退。

**请求体工具（:262-288）**：readJsonBody 限 1MB（:267）；readBinaryBody 边读边累计、超限即抛带 `statusCode=413` 的错误（:271-284）——与 :121-124 的统一错误处理（尊重 error.statusCode）配合，全文件唯一的错误出口。

## 3. 外部连接

**依赖上游**：Node 内建（fs/http/path/child_process/url，:1-6）；本地 `config-store.mjs`（:7，readAgentConfig/saveAgentConfig——API key 永不回传：读时 `result.api_key=''` + `result.has_api_key=Boolean(...)`，config-store.mjs:63-64）；本地 `server-lib.mjs`（:8-16，七个会话/产物纯函数：readSessionState/deleteSession/readSessionHistory/storeWorkspaceUpload/listSessionArtifacts/resolveArtifactPath/artifactContentType）。dev 模式动态 import vite（:128）。

**被依赖下游**：`web/src/App.tsx`（层 10）通过 fetch 打这 13 个路由 + EventSource 订阅 `/api/events`，事件归约在 `web/src/events.ts`（与 TUI 侧 lineMapping.ts 平行的纯函数层）；**spawn 的子进程**是 main_agent.py（`--jsonl --stdin-repl`，参数定义 main_agent.py:24,26）；`vimax` bash 分发器的 web 分支 exec `npm dev/start`（ONBOARDING §3 步骤 1）落到本文件的 dev/start script（web/package.json scripts）。测试侧：web/test/fake-agent.mjs 替身——设 `VIMAX_AGENT_COMMAND` 指向它即可让整个 Web 栈脱离 Python 独立开发（agentCommand 链第一级 :246-248 就是为此预留的注入口）。

## 4. 数据流：Web 上一次"发消息→看成片"的全程

1. 浏览器开页面 → `GET /api/events` 建立长连（:36→:211-225），收到初始 bridge_status(idle)。
2. 用户选项目点启动 → `POST /api/agent/start` → startAgent：杀旧进程、spawn `python main_agent.py --jsonl --stdin-repl --session <id>`（:152）→ 350ms 后 ready 广播。
3. 用户在聊天框输入"把这个 idea 做成视频"→ `POST /api/messages` → :101 写入子进程 stdin 一行。
4. Python 侧 main_agent.py 逐行读 stdin（main_agent.py:84-89），AgentLoop 开始转：每完成一个事件就 `print(json.dumps(event))` 到 stdout（main_agent.py:45）。
5. server.mjs 的行缓冲器收行 → consumeAgentLine 解析 → broadcast → SSE 帧写进所有订阅者 → App.tsx 的 events.ts 归约出聊天消息/进度条。渲染期间 tool_progress 事件（含 novel_render_load、novel_scene_render_start 等阶段）持续刷屏。
6. 用户点产物面板里的 mp4 → `GET /api/artifact?session=..&path=..` → resolveArtifactPath 校验路径在会话目录内（server-lib.mjs:201）→ createReadStream pipe（:303）→ 浏览器 `<video>` 播放。
7. 用户关页面或换项目：request close 清心跳退订（:221-224）；DELETE /api/sessions 若删的正是活动会话先 stopAgent（:56）。

## 5. 设计决策

- **手写 if 链而不用 Express/Fastify**：13 个路由的规模用框架是负资产——零依赖换来 `node server.mjs` 无构建直接跑、无 supply-chain 面积；代价是路由多了会失控（好在本桥职责单一， unlikely to grow）。
- **spawn+stdin+stdout(JSONL)+SSE 的三段式桥**：Python 引擎对"被谁调用"零感知（同一 main_agent.py 服务 TUI 与 Web），桥只做协议翻译。与 TUI 的差异仅在传输层：TUI 直接读子进程 stdout，Web 多一跳 SSE（多标签页共享同一 agent 由此免费获得）。
- **世代守卫（`agentProcess !== child`）遍布所有回调**：Node 子进程事件异步到达，切换会话时旧进程的 exit/stdout 事件若不设防会污染新会话的 UI——这是进程管理代码里最容易被漏掉的坑，本文件防得很整齐。
- **行缓冲器自己写**（:163-165）：`split(/\r?\n)` + `pop()` 回填是流式行协议的标准姿势，任何语言通用；不依赖 readline 是为了把"残行"逻辑显式留在眼前。
- **非 JSON 输出降级为 terminal 事件而非丢弃**：调试 Python 侧裸 print 时信息不丢失——桥的可观测性优先。
- **API key 单向阀门**（config-store.mjs:63-64）：前端能感知"已配置"（布尔）但永远拿不到明文——Web 控制台哪怕被 XSS 也不泄密钥。
- **127.0.0.1 默认绑定 + 会话目录内路径校验 + 上传双重点检**（content-length 预检 + 流式复核）：每一层都是"本地工具"定位下的克制安全，不追求公网部署。
- **--dev 挂 Vite 中间件而非代理**（:127-133,116-119）：middlewareMode 让 Vite HMR 与 API 同源同端口，前端零 CORS 配置。

## 6. 新人提示

- **加路由**：在 :36-110 的 if 链里加分支即可，但注意顺序敏感——`/api/config` 的 GET/PUT 靠方法区分，`/api/sessions` 的 GET/DELETE 同理；新路由放在 `/assets` 与 vite 分支**之前**，否则生产模式会掉进 SPA fallback。
- `activeSessionId` 有三个更新点（:151,:201,:191,:58）：start 时设定、session 事件跟随、350ms 定时器兜底、DELETE 后重取。改会话逻辑时四处都要过一遍，漏一处就会出现"UI 高亮与实际活动会话不一致"。
- 350ms 的 ready 延时（:188）是经验值：Python 写会话文件需要时间，太快 readSessionState 会读到旧态。若你把 main_agent.py 的启动输出改得更晚，这个数可能要调。
- `/api/messages` 是 202 Accepted（:102）——只代表"写进了 stdin"，不代表 agent 已处理；前端别把它当回执，真实状态看 SSE 里的 turn/done 事件。
- 改 SSE 事件格式时三处联动：本文件 consumeAgentLine（透传不解析内部结构）、web/src/events.ts（归约）、以及 ui/src/cli.tsx 的对应逻辑——事件 schema 是跨三端契约。
- `agentCommand()` 回退链（:245-256）与 TUI 侧 cli.tsx 的回退链**不完全相同**（TUI 多一层 .venv/uv 优先序差异，见 06 篇）：排障"Web 起不来但 TUI 能跑"时先对比两条链命中的是哪个解释器。
- 上传上限有**两个检查**（:78-81 预检 + :271-284 流式）但都防不了客户端谎报 content-length 之外的场景以外的问题——流式检查才是真防线，删预检可以、删流式检查不行。
- 本文件没有鉴权：绑 127.0.0.1（:21）是唯一屏障，别改成 0.0.0.0 裸奔——要暴露公网先加反代+鉴权层。
