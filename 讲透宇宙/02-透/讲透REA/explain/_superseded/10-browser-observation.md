# 10 · 浏览器观测：CDP 被动观测、Playwright 场景与 JS 应用图

## 角色定位

`src/browser/`（57 文件）覆盖两条互补路线：被动观测——连接用户自有 CDP 端点只读观察已打开页面（`CdpBrowserProvider.ts:74`）；主动场景——用 Playwright 启动受控浏览器/Electron 执行动作脚本（`PlaywrightBrowserScenarioProvider.ts:312`）。传输地基是自写 CDP WebSocket JSON-RPC 的 `CdpConnection.ts:25`。静态侧 `JavaScriptApplicationService.ts:28` 把本地 JS/Electron 应用重建为 `javascriptApplicationGraph.ts` 的确定性应用图，与运行时观测在图内会师。

## 内部结构

`CdpConnection`：`#pending` Map 管理请求关联，`send` 支持 flat session 与 AbortSignal（`CdpConnection.ts:101`）；`#receive` 逐帧结构校验，id 帧应答、事件帧广播（`CdpConnection.ts:172`），形状不合法即 `#failPending("protocol_error")` 全连接熔断（`CdpConnection.ts:264`）；`close` 只关自己的 socket，绝不关浏览器或页面（`CdpConnection.ts:153`）。`CdpBrowserProvider` 六操作同构：discover→authorize→open session→执行→finally `closeCdpTargetSession`（`CdpBrowserProvider.ts:162`）；`analyzeBundle` 追加 source map 拉取（`CdpBrowserProvider.ts:139`）。

Playwright 双模式：connect 用 `chromium.connectOverCDP` 附着外部浏览器（`PlaywrightScenarioBrowser.ts:113`）；launch 用 `launchPersistentContext` 起 0700 临时 profile，并显式 `handleSIGHUP/SIGINT/SIGTERM: false` 防 REA 信号误杀（`PlaywrightScenarioBrowser.ts:133`）。`runScenario` 产出 steps+events+completeness，connect 模式自动补 events 缺失段（`PlaywrightBrowserScenarioProvider.ts:230`），limitations 逐条写明因果与保留边界（`PlaywrightBrowserScenarioProvider.ts:294`）。Electron 用 `_electron.launch` 注入 `-r hook` 预载（`PlaywrightElectronActiveProvider.ts:92`）并立即构造 `OwnedProcessGroup` 观察谱系（`PlaywrightElectronActiveProvider.ts:109`）。应用图核心是确定性 ID：节点 `jag_node_<sha256(semantic)>`，观测与边同策略（`javascriptApplicationGraph.ts:67`）；`observationMatchesIdentity` 按六种 identity strategy 交叉核对（`javascriptApplicationGraph.ts:152`）。

## 外部连接

依赖：`ws`（CdpConnection 唯一三方依赖，`CdpConnection.ts:1`）、playwright-core、domain 的 browserObservation/webBundle schema 群（`CdpBrowserProvider.ts:4`）。被 `BrowserScenarioCaptureService.ts:14` 包成 Evidence（provider 未配置返回 `AnalysisCapabilityUnavailableError`，`BrowserScenarioCaptureService.ts:19`），`server/createServer.ts` 注册全部 web 工具族。测试假浏览器 `tests/fixtures/fakeCdpBrowser.ts:16` 在真实 HTTP+WS 上复刻端点。

## 数据流

被动链：cdp_endpoint→`/json/version`+`/json/list` 发现→origin 白名单过滤（`CdpBrowserProvider.ts:365`）→flat session 执行命令→schema.parse 投影。主动链：scenario→factory.open→逐步执行动作（`PlaywrightBrowserScenarioProvider.ts:259`）→close 清理→captureSchema.parse。静态链：`analyzeJavaScriptApplicationValidated` 依序 reconstruct→steps 解析→协作式 Evidence 构造，每步间 `checkpointJavaScriptAnalysis` 让出响应取消（`JavaScriptApplicationService.ts:54`）；Zod 输出失败转 JSON Pointer 诊断（`JavaScriptApplicationService.ts:143`）。

## 设计决策

安全默认极强：被动观测绝不导航/点击；目标授权后 `scopeToTargetOrigin` 把后续网络请求自动限定在目标 origin（`CdpBrowserProvider.ts:424`）。消息预算显式化——maxPayload 超限归为独立 `payload_limit` 错误并报出字节数（`CdpConnection.ts:297`）。图不变量编码进 schema refinement：静态 authority 不得宣称 runtime location（`javascriptApplicationGraph.ts:144`），排序唯一性由 Unicode code point 全序保证，使图内容可复现哈希。Electron 取消时保留 partialObservation 快照而非丢弃（`PlaywrightElectronActiveProvider.ts:127`）。

## 新人提示

CdpConnection 是共享地基，`protocol_error` 熔断是不可恢复语义，别改成跳帧。场景 limitations 是产品承诺（agent 据此判断证据强度），新增捕获维度必须同步补 limitation。测试优先用 `startFakeCdpBrowser` 的故障注入（oversized/malformed/unsupportedMethods，`fakeCdpBrowser.ts:44`、`fakeCdpBrowser.ts:109`），未建模命令必须拒绝而非返回通用成功。
