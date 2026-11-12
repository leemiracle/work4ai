# 08 · ui/desktop 主进程：Electron 壳与 goosed 子进程的边界

> 源码基线：本地仓 `/usr-data/data2/repos/aaif-projects/repos/goose`。主进程文件群：`ui/desktop/src/main.ts`（2819 行）、`goosed.ts`（451 行）、`preload.ts`（371 行）、`startupDiagnostics.ts`、`mesh.ts`。全部行号锚已从源码逐一核实。
>
> **两处与任务书不符的勘误（按源码为准）**：① 任务书所说的 `main/` 目录不存在——主进程代码是 `src/` 下的扁平文件集（main.ts + goosed.ts + preload.ts + 若干工具模块），没有子目录；② 任务书背景称"密钥每次启动随机"——对认证密钥 `X-Secret-Key` 仍然成立（`main.ts:733` 的 `crypto.randomBytes(32)` 每次 Electron 启动随机），但 **TLS 自签证书已改为磁盘缓存复用**：`crates/goose-server/src/tls.rs:178-180` 的 `load_cached_tls()` 快路径会优先读 `Paths::config_dir()/tls/server.pem`（`tls.rs:109-111`），只有无缓存时才走 `generate_self_signed_cert()` 现生成。钉扎机制不受影响——两条路径都会向 stdout 打印 `GOOSED_CERT_FINGERPRINT=`（`tls.rs:82/180/187`）。

## 一、角色定位：16 层架构中的"进程编排层"

在 goose 的 16 层知识图谱中，桌面端主进程与构建打包是**第 8 层**（48 个节点），其上是第 9 层渲染进程应用层、第 10 层组件库，其下直连第 7 层 goose-server。它是整条链上唯一的 Node.js/Electron 代码——Rust 世界（crates/）与 React 世界（renderer）之间的一切都从这层经过。

它是一个**刻意做薄的壳**。判断依据是职责清单而非体积：main.ts 2819 行里没有一个业务概念（没有 session、没有 agent loop、没有 tool 调用），全部是四类"操作系统代理"工作：

1. **进程编排**——拉起/看护/回收 goosed 子进程（`goosed.ts` 整个文件）；
2. **窗口与系统资源**——BrowserWindow、托盘、全局快捷键、系统通知、电源锁；
3. **安全策略执行**——TLS 证书钉扎（`main.ts:268/298/335` 三处）、CSP 动态注入（`main.ts:2139`）、危险协议黑名单（`main.ts:1075`）、设置键白名单（`main.ts:1611`）；
4. **IPC 桥**——约 45 个 `ipcMain.handle/on` 通道，把 Node 能力（文件对话框、spawn、Notification）以受控面暴露给渲染进程。

所有对话智能都在 Rust 的 goosed 里。主进程对"消息如何生成"一无所知，它只保证：goosed 活着、TLS 连接是真的、渲染进程拿到了 baseUrl 和 secret。这个边界划分是全仓最清晰的一条线。

## 二、内部结构

### 2.1 app 启动链（模块加载 → appMain）

main.ts 的顶层代码在 `app.ready` 之前就干了四件事：

- **Squirrel 装卸守卫**：`if (started) app.quit()`（`main.ts:261`），Windows 安装器事件直接退出；
- **goose:// 协议注册**：dev 模式强制抢占注册并在 macOS 上 spawn `open --reset-protocol-handler` 抢回默认句柄（`main.ts:360-375`），生产模式常规注册（`main.ts:378`）；
- **单实例锁**：非 macOS 平台 `app.requestSingleInstanceLock()`（`main.ts:385`），第二实例通过 `second-instance` 事件接收命令行里的 `goose://` 深链并分派（`main.ts:390-445`）；macOS 则走 `open-url` 事件（`main.ts:544`）。深链有五种 hostname：`bot/recipe`（新建聊天窗口+配方注入）、`new-session`、`resume`、`extension`、`sessions`，前三种直接开新窗，后两种经 `pendingDeepLinks` Map（`main.ts:457`）排队等渲染进程就绪；
- **双通道证书钉扎器注册**（见 2.3）。

真正的初始化在 `app.whenReady().then(appMain)`（`main.ts:2752`）。`appMain()`（`main.ts:2112`）顺序执行：代理配置 `configureProxy`（`main.ts:2113`，读 HTTPS_PROXY/HTTP_PROXY 灌给 `session.setProxy`）→ Windows shim 准备 → 更新 IPC 注册 → 麦克风权限放行（`main.ts:2121-2130`）→ **CSP 注入**（`main.ts:2134-2142`，每个响应头动态重算 `buildCSP(externalGoosed)`，注释明言这是为了"改外部后端设置不用重启就生效"）→ 键盘快捷键迁移 → 全局快捷键注册（`main.ts:2154`）→ **Origin 重写**（`main.ts:2156-2159`，把所有请求 Origin 硬写成 `http://localhost:5173`，让 goosed 的 CORS 校验在打包模式下同样通过——dev 服务器端口被固化进了生产逻辑）→ 托盘创建（`main.ts:2161-2163`）→ 首窗创建（`main.ts:2172`）→ 延迟 2 秒启动自动更新器（`main.ts:2178-2187`）→ 原生菜单手术（往 File/Edit/View/Help 菜单插 New Chat、Find、About Goose 等项，`main.ts:2201-2467`）→ 最后 `translateMenuLabels` 做简体中文菜单翻译（`main.ts:2465`，手写字典在 `main.ts:72-130`，因为主进程用不了渲染层的 react-intl）。

### 2.2 goosed 子进程生命周期（createChat 是核心函数）

`createChat`（`main.ts:792`）每开一个聊天窗口就完整跑一遍"起后端→建窗口"流程，**一个窗口对应一个 goosed 进程、一个端口**：

1. **取密钥**：`getServerSecret`（`main.ts:735-749`）三级来源——外部后端 settings 里配置的 secret → `GOOSE_EXTERNAL_BACKEND` 模式下强制要求 `GOOSE_SERVER__SECRET_KEY` 环境变量（缺失直接 throw，`main.ts:740-744`）→ 本地模式用模块加载时生成的 `GENERATED_SECRET`（`main.ts:733`，`crypto.randomBytes(32)`，每次 Electron 启动随机、进程内所有窗口共享）。
2. **起进程**：`startGoosed`（`main.ts:826` → `goosed.ts:202`）内部：
   - 外部后端短路：settings 启用 externalGoosed 时直接返回远端 URL、`process:null`、cleanup 是空操作（`goosed.ts:218-240`）；`GOOSE_EXTERNAL_BACKEND` 环境变量是第二条外部短路（`goosed.ts:242-265`）；
   - 本地路径：`findAvailablePort`（`goosed.ts:25-36`）先 bind 端口 0 探测空闲端口再关闭，`findGoosedBinaryPath`（`goosed.ts:43-83`）四级查找——`GOOSED_BINARY` 环境变量 → 打包后 `resources/bin/goosed`（`goosed.ts:59`）→ dev 模式 `src/bin/`、`target/release/`、`target/debug/`（`goosed.ts:65-67`）；
   - `spawn(goosedPath, ['agent'], ...)`（`goosed.ts:290-315`），`stdio: ['ignore','pipe','pipe']`（`goosed.ts:300`），cwd 设为聊天工作目录，env 注入 `GOOSE_PORT` 和 `GOOSE_SERVER__SECRET_KEY`（`goosed.ts:133-134`，命名遵循 config crate 的 `__` 嵌套约定）。日志打印前对含 secret/key 的环境变量名做 `[REDACTED]` 脱敏（`goosed.ts:303-312`）；
   - **指纹提取**：监听子进程 stdout，逐行找 `GOOSED_CERT_FINGERPRINT=` 前缀（`goosed.ts:323-340`），拿到即 resolve `fingerprintReady` Promise；`startGoosed` 在返回前 `await fingerprintReady`（`goosed.ts:435`），所以 createChat 拿到的 `goosedResult.certFingerprint` 必定已就绪（或进程已退出为 null）。
3. **钉扎**：`if (goosedResult.certFingerprint) pinnedCertFingerprint = goosedResult.certFingerprint`（`main.ts:842-844`）。
4. **回收**：`app.on('will-quit', () => goosedResult.cleanup())`（`main.ts:846-849`）。cleanup 先 SIGTERM，5 秒没死且非 Windows 补 SIGKILL（`goosed.ts:424-429`）；Windows 用 `taskkill /pid <pid> /f /t` 连根杀进程树（`goosed.ts:416`）。应用级 `will-quit` 还有 mesh 子进程清理和电源锁/快捷键注销（`main.ts:2791-2811`）。

健康检查在窗口侧：`checkServerStatus`（`main.ts:934` → `goosed.ts:89-116`）以 100ms 间隔轮询 `/status` 端点、30 秒总超时（`goosed.ts:94-95`），同时盯 stderr 的致命模式（`/panicked at/、/RUST_BACKTRACE/、/fatal error/i`，`goosed.ts:118-121`）。失败时弹原生错误框，正文拼出子进程退出码、是否见过 TLS 指纹、是否见过健康检查成功、诊断文件路径、stderr 尾巴（`main.ts:941-954`）——这套取证来自 `startupDiagnostics.ts`：每次启动写一份 JSON 到 `userData/logs/startup/`，stderr 尾巴保留 80 行、历史文件留 20 份（`startupDiagnostics.ts:36-37`）。外部后端连不上还有一条活路："Disable External Backend & Retry" 按钮关掉设置后递归重试 createChat（`main.ts:967-975`）。

### 2.3 证书钉扎：一个指纹，两条通道

模块级状态就一个变量：`let pinnedCertFingerprint: string | null = null`（`main.ts:268`）。策略注释写在定义上方（`main.ts:263-267`）：本地拉起的 goosed 用 stdout 指纹钉扎；外部后端用 TOFU（Trust-On-First-Use，首次握手即钉扎，进程生命周期内有效）。

同一个指纹作用在两条互不相干的验证通道上：

- **渲染进程的 fetch**（含 SSE）走 `app.on('certificate-error')`（`main.ts:298-315`）：非信任主机直接拒绝；有指纹则比对 `certificate.fingerprint`（大小写归一 `normalizeFingerprint`，`main.ts:283-293`），匹配才放行；无指纹（健康检查引导窗口期）则 TOFU——接受任意 localhost 证书并把首个指纹钉住（`main.ts:310-313`）；
- **主进程自己的 `net.fetch`**（健康检查、mesh 探测用）走 `session.defaultSession.setCertificateVerifyProc`（`main.ts:334-350`），同样的信任主机判断+指纹比对+TOFU，回调值 0/-2/-3 是 Chromium 证书验证错误码。

信任主机判定 `isTrustedHost`（`main.ts:278-281`）= localhost 或 `trustedExternalHostname`（每次 createChat 从 settings 的外部 URL 重算缓存，`main.ts:806-816`）。若用户为外部后端显式配置了 `certFingerprint`，则直接钉死该值跳过 TOFU（`main.ts:820-824`）。

goosed 侧的配合在 `tls.rs`：`self_signed_config()` 先查缓存（`tls.rs:179`），miss 才 `generate_self_signed_cert()`（`tls.rs:30-43`，SAN 只含 127.0.0.1 和 localhost）并持久化到配置目录，两条路径都 `println!("GOOSED_CERT_FINGERPRINT={fingerprint}")`——`tls.rs:187` 这行的文档注释明说"printed to stdout so the parent process (e.g. Electron) can pin it and reject connections from any other certificate"。stdout 成了父子进程间的可信带外信道：本机任意进程都可能连上这个端口，但只有持有指纹和 secret 的 Electron 才能通过验证。

### 2.4 IPC 通道清单与窗口管理

主进程维护三张注册表：`windowMap`（windowId→BrowserWindow）、`goosedClients`（windowId→goosed HTTP Client，`main.ts:773-774`）、`appWindows`（standalone app 窗口名→窗口）。**goosedClients 按 windowId 索引是关键设计**：每个聊天窗口的请求路由到自己那个 goosed，`get-goosed-host-port` / `get-acp-url` 两个 handler 都用 `BrowserWindow.fromWebContents(event.sender)?.id` 反查（`main.ts:1651-1661/1663-1674`）——窗口间工作目录隔离、进程隔离，但 standalone app 窗口可以继承发起窗口的 client（`main.ts:2685`）。

ipcMain 通道约 45 个，代表性的几类：

| 类别 | 通道（行号） | 说明 |
|---|---|---|
| 后端契约 | `get-secret-key`(1646) `get-goosed-host-port`(1651) `get-acp-url`(1663) | 渲染进程构建 API 客户端的三要素 |
| 生命周期 | `react-ready`(1541) `create-chat-window`(2475) `close-window`(2513) `restart-app`(2638) | react-ready 触发 pendingInitialMessages 释放(1549-1553) |
| 设置 | `get-setting`(1605) `set-setting`(1628) | set-setting 带 14 键白名单防原型污染(1611-1638) |
| 文件/系统 | `read-file`(1973) `write-file`(2013) `select-file-or-directory`(1851) `show-save-dialog`(2059) | 渲染进程无 Node，全靠这些 |
| 子进程 | `check-mesh/start-mesh/stop-mesh`(1914-1916) `check-ollama`(1918) | mesh=Apple Silicon 本地 LLM 进程(mesh.ts:1-7) |

窗口本体用 `electron-window-state` 记忆位置尺寸（默认 940×800，`main.ts:861-864`），恢复时刻意不用 `useContentSize`——注释解释了 #9363 bug：外框尺寸被当内容尺寸重放，每次启动窗口长高一截（`main.ts:871-875`）。另有两种特殊窗口：Spotlight 式快速启动器（600×80 无框、失焦即毁、Esc 即毁，`main.ts:1216-1278`）和独立 app 窗口（`main.ts:2670-2683`，尺寸由 GooseApp 声明）。窗口关闭时清理三张表、停电源锁（`main.ts:1189-1210`）。

## 三、外部连接

**下游 goosed（HTTPS+SSE）**：baseUrl 形如 `https://127.0.0.1:{port}`（`goosed.ts:272`）。主进程自己的客户端用 `net.fetch` 而非全局 fetch——注释明说原因是"让发往本地自签 HTTPS 服务器的请求走 session 的证书处理"（`main.ts:920-931`），即 `setCertificateVerifyProc` 那条钉扎通道；请求头带 `X-Secret-Key`（`main.ts:928`）。渲染进程的 HTTP 客户端是 openapi 生成的 `@hey-api/openapi-ts` 产物（`src/api/client/index.ts:1` 自动生成声明），在 `renderer.tsx:44-48` 用 `window.electron.getGoosedHostPort()` + `getSecretKey()` 完成 setConfig——主进程因此**从不见业务流量**，它只递钥匙。

**ACP WebSocket**：`buildAcpWebSocketUrl`（`main.ts:751-757`）把 baseUrl 改写成 `{base}/acp?token=...`、协议 https→wss；渲染进程经 `get-acp-url` 拿到后由 `acpConnection.ts:39` 建流。这是第 4 层 ACP 协议在桌面端的入口。

**上游系统能力**：托盘（5 个候选图标路径探测，找不到就降级禁用并写回设置，`main.ts:1299-1331`）；自动更新（`UPDATES_ENABLED=true` 硬编码于 `src/updates.ts:1`，`setupAutoUpdater` 延迟 2 秒在首窗后启动，`main.ts:2178-2187`）；全局快捷键（聚焦窗口+快速启动器两项，`main.ts:2085-2110`）；系统通知（渲染进程 `notify` 通道转发，title/body 限长 1000、剥 HTML 标签、点击回调聚焦原窗，`main.ts:2520-2565`）；powerSaveBlocker 防休眠（按窗口追踪，`main.ts:1195-1209`）。

**preload 暴露面**：`contextBridge.exposeInMainWorld('electron', electronAPI)` 和 `('appConfig', appConfigAPI)` 双注入（`preload.ts:361-362`）。`ElectronAPI` 类型共 60+ 成员（`preload.ts:102-195`），但真正的特权通道只有三个直通 ipcRenderer 的泛型方法 `on/off/emit`（`preload.ts:291-305`）——渲染进程事件总线靠它转发主进程推送（`set-initial-message`、`mouse-back-button-clicked`、`mesh-not-running` 等）。窗口配置不走 IPC：主进程把 appConfig JSON 塞进 `additionalArguments`（`main.ts:889-906`，含 baseUrl、工作目录、recipe 深链、security 开关），preload 用 `process.argv.find(arg => arg.startsWith('{'))` 解出来（`preload.ts:85`），同步可读、零往返。安全基线在 BrowserWindow 一处声明：`nodeIntegration:false, contextIsolation:true, webSecurity:true`（`main.ts:885-888`）+ `persist:goose` partition 共享会话（`main.ts:907`）。

## 四、数据流：冷启动到第一条消息上屏

1. `app.whenReady()` → `appMain()`（`main.ts:2752/2112`）：代理、CSP、快捷键、托盘就绪；
2. `createChat`（`main.ts:792`）→ `getServerSecret`（735）：本地模式取 `GENERATED_SECRET`（733，本次会话随机）；
3. `startGoosed`：端口探测（`goosed.ts:269`）→ 二进制定位（267）→ `spawn goosed agent`（291/315），env 注入端口+secret（133-134）；
4. goosed 侧 `self_signed_config()`：命中缓存复用旧证书（`tls.rs:179-180`）或现生成（`tls.rs:30-43`），stdout 打指纹行；
5. 主进程 stdout 解析器捕获指纹（`goosed.ts:323-340`），`await fingerprintReady`（435）后写入 `pinnedCertFingerprint`（`main.ts:842-844`）——此刻起两条 TLS 通道都只认这张证书；
6. `net.fetch` 客户端建好（`main.ts:922-931`），`checkServerStatus` 以 100ms 步进轮询健康端点（`main.ts:934`），成功后停掉 stderr 收集防内存增长（`main.ts:990-991`）；
7. `new BrowserWindow`（866）带 preload（885）与 argv 配置（889-906），`loadURL`（1141）加载 HashRouter 路由的渲染页（hash 拼装在 `main.ts:1137-1138`）；
8. 渲染进程入口 `renderer.tsx`：非 launcher 视图先 `getGoosedHostPort()`，null 则 alert 后放弃（`renderer.tsx:39-42`）；拿到后给 openapi 客户端 setConfig baseUrl + `X-Secret-Key`（`renderer.tsx:44-48`）；React 挂载完发 `react-ready`（`preload.ts:205`）；
9. 主进程 `react-ready` handler（`main.ts:1541`）：释放排队中的初始消息（1549-1553）和深链（1556-1570）——深链消息可能早于 React 就绪到达，靠这两张 pending Map 兜住时序；
10. 用户发第一条消息：渲染进程走 POST+SSE 模式（`useChatStream.ts:650-655` 注释自述：先注册 SSE 监听再 POST `/sessions/{id}/reply`，request_id 用 uuidv7），事件流从 goosed 的 SSE 端点经渲染进程 fetch——即 `certificate-error` 钉扎通道（`main.ts:298`）——回流上屏。ACP 侧会话管理则并行走 WebSocket（`acpConnection.ts:39`）。主进程在这条链里只出过一次场：第 6 步递钥匙。

## 五、设计决策

**Electron 壳 + Rust 后端，而非 Tauri 或 Node 内嵌**（仓内无架构决策文档，以下除注明外为推断+源码旁证）：
- *子进程而非嵌入式绑定*：goosed 与 CLI 共用同一个二进制（dev 查找路径直接指向 `target/release/goosed`，`goosed.ts:65-67`），桌面端免费获得 CLI 的全部能力与独立升级节奏；Rust panic 只杀子进程，stderr 致命模式检测（`goosed.ts:118-121`）和退出码诊断（`main.ts:941-954`）把故障域隔离在 Electron 之外。推断的另一半理由是避免 Node↔Rust FFI 的内存边界复杂度。
- *Electron 而非 Tauri*：纯推断，但依赖面提供旁证——vibrancy/trafficLightPosition（`main.ts:867-869`）、powerSaveBlocker、electron-squirrel-startup（`main.ts:23/261`）、electron-window-state、electron-devtools-installer（`main.ts:53/912`）都是深绑 Electron 生态的成熟件。

**证书钉扎的安全取舍**（有注释，`main.ts:263-267`）：本地 goosed 监听 127.0.0.1 随机端口，但本机其他进程同样能连。防线有两道——stdout 指纹确保"连到的服务器是真的 goosed"（防本机 DNS/端口抢跑劫持），`X-Secret-Key` 随机密钥确保"客户端是真的 Electron"（防未授权调用）。外部后端买不起带外信道，退化为 TOFU+可选显式指纹（`main.ts:820-824`）——这是明确的降级取舍。**推断**：认证 secret 每次启动随机（`main.ts:733`）而 TLS 证书改为磁盘缓存（`tls.rs:178-180`），组合效果是重启换钥匙不换锁——secret 挡住的重放面在重启后即失效，而证书缓存避免了每次启动都触发 TOFU 重建。

**stdout 信道的代价与治理**：指纹之后的 goosed stdout 仍是长寿命管道。`goosed.ts:355-366` 有一段罕见的"血泪注释"：留着 data 监听器会让每块 stdout 都经 V8 `String::NewFromTwoByte` 转字符串，数小时级会话曾直接触发 V8 断言**崩掉主进程**；修法是拿完指纹立即 `removeAllListeners('data')` + `resume()` 让管道裸排。这是子进程架构边界上最贵的一课：带外信道用完必须拆。

**每窗口一个 goosed 实例**（`goosedClients` 按 windowId 索引，`main.ts:774`）：推断动机是工作目录级隔离——每个聊天窗口绑定一个目录一个 agent 进程，session 数据天然分片；代价是多窗口多进程多端口，清理责任落在 will-quit（`main.ts:846-849`）。

**渲染进程零特权**：contextIsolation+无 Node（`main.ts:887-888`），所有系统访问白名单化（设置键 14 个白名单 `main.ts:1611`、协议黑名单 `main.ts:1075`、CSP 每响应重算 `main.ts:2139`）；但 `on/off/emit` 泛型透传（`preload.ts:291-305`）是一个务实的口子——通道名不设白名单，推断为接受"渲染进程被攻破时 IPC 面全开"的残余风险换取事件总线灵活性。

## 六、新人提示

- **调试主进程**：`pnpm start-gui-debug` 带 `--inspect=9229`（package.json:16）；渲染进程 devtools 用 `Alt/Cmd+Opt+I`（`main.ts:1155-1156`）；E2E 调试设 `ENABLE_PLAYWRIGHT=1` 开 9222 远程调试端口（`main.ts:352-356`）；dev 模式自动装 React DevTools（`main.ts:911-918`）。
- **dev 环境第一个坑**：goosed 二进制四级查找要求先 `cargo build`（`goosed.ts:65-67` 找 `target/release|debug`），否则 `findGoosedBinaryPath` 直接 throw "not found in any of the possible paths"。可用 `GOOSED_BINARY` 指定自定义路径（`goosed.ts:44`）。
- **打包流水线入口**：electron-forge 体系，`package.json` 的 `"main": ".vite/build/main.js"`（第 10 行）+ `pnpm make`（第 20 行）；打包产物里 goosed 落在 `resources/bin/`（`goosed.ts:59`）。API 客户端是生成物：改 server 后先 `just generate-openapi` 再 `pnpm generate-api`（openapi-ts），**手工编辑 openapi.json / *.gen.ts 是仓规明令禁止**。
- **启动失败排查**：先看错误对话框里的诊断路径，再去 `userData/logs/startup/` 读 JSON（含 spawn/指纹/健康检查事件时间线与 stderr 尾 80 行，`startupDiagnostics.ts:36-37`）；"TLS fingerprint observed: no" 基本等于 goosed 没起来或 stdout 协议变了。
- **改 IPC 时的隐性契约**：`get-goosed-host-port`/`get-acp-url` 依赖 `goosedClients` 里注册表项（`main.ts:1651-1674`）——standalone app 窗口能工作是因为 `launch-app` 显式继承 client（`main.ts:2685`）；新窗口类型若忘了这一步，渲染进程会在 `renderer.tsx:41` 静默 alert。
- **两代 reply 并存**（前篇 07 已详述，主进程视角只需知道）：渲染层一代端点事件流绑死 POST 响应，二代是"先订阅长连 SSE 再 POST"（`useChatStream.ts:650-655`）；两者都走渲染进程 fetch，即 `certificate-error` 钉扎通道，主进程无感知。
- **长会话稳定性**：任何要监听 goosed stdout 的新代码，读完必须移除监听器（教训见 `goosed.ts:355-366` 的 V8 崩溃注释）；stderr 收集也有对称的 `stopErrorLogCollection()`（`main.ts:990`），别把无界数组带进数小时会话。
