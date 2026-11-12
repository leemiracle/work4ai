<!-- source: knowledge-graph tour step | files: src/domain/javascript/javascriptApplicationGraph.ts, src/browser/CdpBrowserProvider.ts, src/application/javascript/JavaScriptApplicationService.ts, src/browser/CdpConnection.ts -->

# 10 · 浏览器观测与 JS 应用图：运行时取证与静态恢复在一张图上汇合

### 角色定位

REA 对网站/Electron 的逆向分两条线：运行时被动观察（CDP 旁听活浏览器）与静态结构恢复（混淆 bundle 重建）。本篇四文件是两条线的腰部：src/browser/CdpConnection.ts 与 src/browser/CdpBrowserProvider.ts（**layer:browser-js-observation**）是 CDP 传输内核与 `BrowserObservationPort` 九成员契约的实现（BrowserObservationPort.ts:39-64）；src/domain/javascript/javascriptApplicationGraph.ts（**layer:domain**）定义 JavaScript Application Graph（JAG）的节点/边/不变量；src/application/javascript/JavaScriptApplicationService.ts（**layer:application**）是静态分析编排入口。v6.5 加了第三条腿：**离线网络捕获**——mitmproxy 桥 bridge/mitmproxy/capture.py（384 行）解码已存 flows，配 WEB_SCRIPT/WEB_RUNTIME/WEB_NETWORK_CAPTURE 三契约族（toolContracts.ts:66-68）。运行时看到"实例"、静态恢复"结构"，JAG 让 `runtime-instance` 与 `content-digest` 等身份共存一图，靠 `observed_as` 桥接。

### 内部结构

**CdpConnection**：`#pending` Map 按消息 id 关联 Promise（:31），`#closed`（:40）与 `#protocolFailed`（:42）独立降级，`#transportFailure` 区分 disconnected/payload_limit（:43）。接收侧严格形状校验——sessionId 类型不符即判死（:307）；响应 sessionId 与 pending 不符判错防浏览器串话（:331-340）；`protocol_error` 只置协议失败不置 closed（:135-136）。`close()` 只关 REA 自己的 socket——注释明言 "never close the browser or selected page"（:206）。

**CdpBrowserProvider**：活连接方法共用骨架——端点发现（HTTP 拉 /json/list）→目标授权→origin 收缩→openCdpTargetSession→业务→finally closeCdpTargetSession（CdpBrowserProvider.ts:345-390）；`selectTargets` 把排除原因如实写进 limitations（:452）；`scopeToTargetOrigin` 未给白名单时收缩为目标单 origin——默认最小权限（:513）。

**JavaScriptApplicationService**：入口 safeParse（JavaScriptApplicationService.ts:38）；catch 四层：ArtifactReaderFailure→ArtifactOperationError、ZodError→AnalysisOutputError 带 JSON Pointer、文件系统错误码→io、兜底 ProviderAdapterError（:144-160）。

**javascriptApplicationGraph**：全部标识符是语义内容 SHA-256——node/observation/edge/graph 四级 ID 各自取摘要（javascriptApplicationGraph.ts:78/:95/:102/:532）。35 种节点 kind、12 种 relation 兼容静态与运行时实体（javascriptApplicationGraphSchemas.ts:15/:57）。`superRefine(checkGraphInvariants)`（:461）校验集合排序唯一、graph_id 重算一致、禁自环；核心是 `observationMatchesIdentity`（:209）：七种身份策略（content-digest/source-map-original/canonical-path/structural-fingerprint/artifact-local-key/runtime-instance/observation-fingerprint，javascriptApplicationEvidenceSchemas.ts:420 判别联合）各规定什么 observation 才支撑身份——`content-digest` 要求 sha256 逐字相等（:215）、`runtime-instance` 要求 runtime 类 authority（:236）、`structural-fingerprint` 只要 inferred 态（:253）；静态 authority 不得声称 runtime location。不可变化走工厂+WeakSet 认证（:554），裸 `Object.freeze` 无法伪造；序列化走 canonical JSON（src/domain/comparisonSemantics.ts:14，已上移一层）。

### 外部连接

CdpConnection 消费方很窄：`openCdpTargetSession` 决定 page-scope 直连还是经 `Target.attachToTarget` flatten:true 拿 session（CdpTargetSession.ts:139-140）；`closeCdpTargetSession` 逐域 disable→detach→close，abort 时并行撤离（:167-224）。JAG fan-in 覆盖版本对比、运行时对账、导出形状对比与 builder 群——后者经 JavaScriptArtifactGraphContext 边工厂（contains/ast-contains/static-inference）产出输入。三族新契约：WEB_SCRIPT（trace_web_source_location/trace_web_module_imports/export_web_scripts，webScriptToolContracts.ts:20/:44/:66）、WEB_RUNTIME（observe_web_execution/inspect_web_event_listeners，webRuntimeToolContracts.ts:16/:35）、WEB_NETWORK_CAPTURE（inspect_web_network_capture，webNetworkCaptureToolContracts.ts:16）。domain/javascript/ 子树 126→214 文件（单子域扩张冠军）：新增 electronStaticAnalysis* 八文件（主体/Ipc/Native/Browser/Types+3 测试）、electronActiveObservation、javascriptApplicationChangeGraph.ts（277 行）。汇合对账入口是 reconcile_javascript_runtime 命令（electronCommands.ts:153）与 JavaScriptRuntimeReconciliationEvidence。

### 数据流

运行时（observeSession）：`cdp_endpoint` 被 `browserEndpointSchema` 强制 loopback+显式端口+根路径（browserObservation.ts:81 起）；建连后 `observeCdpSession` 锚定主帧，`onEvent` 交 `TimelineCapture.ingest`（CdpObservationSession.ts:61-62）；窗口结束返回带三条固化 limitations 的 session——"时间线从 attach 开始""只留导航元数据""越权目的地不记 URL"（:125）。离线捕获：mitmproxy 桥用 mitmproxy 未改动的原生 tnetstring 解码器离线读 flows（capture.py:1），配套 http3-capture-lab 实验。静态：safeParse→`reconstructJavaScriptArtifact` 读包→builder 借边工厂产出节点/边→`createJavaScriptApplicationGraph` 派生 `jag_*` ID→步进冻结→Evidence 产出 sha256。汇合：运行时按 `runtime-instance` 身份、静态按内容/路径身份各自入图，reconcile 服务用 `observed_as` 把脚本实例钉到静态模块。JS 侧 v6.2 契约收紧：presence 三态 present/absent/unknown-coverage，`property_path` 是完整段数组或 null，导出形状对比保留双侧 presence——"未知值"与"属性缺失"必须区分（migration-6.2.md:127-137）。

### 设计决策

1. **内容寻址 ID**：同一语义内容无论谁产出 ID 必同，跨版本对比成原生能力；代价是构造侧必须严格规范化——"ID 即承诺"。
2. **身份策略显式建模**：七种 strategy 各带 stability 字面量（:423 起），消费方可静态知道 ID 跨版本是否作数。
3. **协议失败与传输失败分开**：payload_limit 报出字节预算（CdpConnection.ts:382-414）、命令拒绝不连坐——须能区分"浏览器拒绝命令"与"线坏了"。
4. **被动原则联动**：loopback-only+exact-origin 白名单+默认单 origin 收缩+越权导航"记录但抹 URL"是联动决策而非单点检查；离线捕获延续同一姿态——读已存 flows 不代理流量。
5. **presence 语义强制**：unknown-coverage 区分"没看到"与"确认没有"，导出对比保留双侧 presence——下游最痛但防幻觉最值的 v6.2 breaking。

### 新人提示

上手：javascriptApplicationGraphSchemas.ts（形状）→ javascriptApplicationGraph.ts 的 `observationMatchesIdentity`/`checkGraphInvariants`（:209/:442）→ CdpConnection.ts（传输）→ CdpTargetSession.ts（会话）→ CdpBrowserProvider.ts（编排）。易错点：①`jag_*` ID 不是随机值，语义字段一改 ID 必变，fixture 断言前先自算摘要；②page/browser-scope 的 sessionId 语义不同（undefined 即 page 直连）；③runtime location 只能由 runtime 类 authority 声称；④comparisonSemantics 已搬到 src/domain/ 根，老 import 路径失效；⑤写 JS 契约消费端禁止把 unknown presence 当 absent 处理（migration-6.2.md 明令）。测试入口：tests/boundary/browser/cdpConnection.test.ts 与 cdpBrowserProvider.*.test.ts 系列、javascriptApplicationGraph.test.ts、JavaScriptApplicationService.test.ts。
