# 10 · web-inspector 与遥测线：Lit 巨石、隐私契约与双汇流采样

## 角色定位（16 层架构中位置）

本篇横跨两处图谱层：`packages/web-inspector`（第 13 层「外围集成小包」的观察者组件）与遥测线（贯穿 shared 第 2 层 / runtime v2 第 6 层 / web-inspector 的横切关注点）。web-inspector 是宿主页面里挂载的**调试面板 Web Component**——开发者在自己的 app 里放一个 `<cpk-web-inspector>` 标签，即可查看 CopilotKit 的线程、agent 状态、消息流；它消费第 3 层 core 包的 ɵ 前缀内部 API（ɵselectThreads 等），是 core 内部契约的官方第二消费者（第一是 react-core）。遥测线则是全仓的"数据回流"侧写：v1 线走 shared/TelemetryClient（Segment+Lambda 双汇流），v2 runtime 有独立 TelemetryClient（5% 采样），inspector 有自己的三事件最小集——三套实现共享一个 Lambda 网关与隐私契约。

一句话：inspector 是"看 CopilotKit 在干什么"的窗口，遥测是"CopilotKit 看你在干什么"的管道——两者在这篇交汇因为 inspector 面板本身也上报三个匿名事件。

## 内部结构（关键文件+行号锚拆解）

### index.ts：7714 行 Lit 巨石

`packages/web-inspector/src/index.ts` 全文 7714 行，承载 3 个 LitElement 类与约 130-160 个方法（正则宽口径 163 个方法形声明）——本仓最大单文件，图谱把它标注为"反巨型文件警示样本"（digest b18）：

- `class CpkThreadList extends LitElement`（`index.ts:361`）——线程列表子组件，非导出（内部用），注册于 `customElements.define("cpk-thread-list", CpkThreadList)`（`index.ts:2334`）；
- `export class ɵCpkThreadDetails extends LitElement`（`index.ts:671`）——线程详情，ɵ 前缀（Angular 惯例的内部 API 标记），注册 `"cpk-thread-details"`（`index.ts:2337`）；
- `export class WebInspectorElement extends LitElement`（`index.ts:2340`）——主元素，标签常量 `WEB_INSPECTOR_TAG = "cpk-web-inspector"`（`index.ts:60`），文件末尾注册（`index.ts:7704`）。

关键属性：`autoAttachCore: { type: Boolean, attribute: "auto-attach-core" }`（`index.ts:2343`）Lit static properties 声明，默认 `private autoAttachCore = true`（`:2404`）——不传 core 时自动发现全局 CopilotKit 实例；对旧版 @copilotkit/core 赋值 `inspector.core` 做了容错（`:2689` 注释）。

lib/ 四件分担薄逻辑：`lib/persistence.ts`（206 行，零第三方依赖——UUID v4 用 `crypto.getRandomValues` 手写，所有 `is*` 校验器构成 localStorage 反序列化信任边界）；`lib/telemetry.ts`（179 行，下详）；`lib/context-helpers.ts`（166 行）；`lib/types.ts`（19 行）。构建侧 `styles/tailwind.css` 是 Tailwind v4 CSS-first 范式（`@import "tailwindcss"` + `@source`），与仓内 `packages/tailwind-config/tailwind.config.js` 的 v3 JS 配置遗存构成两代同仓（digest b61）。

### inspector 遥测：三事件最小集（lib/telemetry.ts）

文件头注释即**隐私契约**（`lib/telemetry.ts:1-29`）：不发送消息内容/agent 状态/prompt；`TELEMETRY_EVENTS` 三个事件全部 `oss.inspector.*` 命名空间（`banner_viewed`/`banner_clicked`/`threads_tab_clicked`，`:30-33`）——命名空间是刻意设计，让 Lambda 网关的事件 allowlist（oss-path-to-production）能服务端门控，新增事件不加 allowlist 条目会被拒（`:26-29` 注释）。端点 `TELEMETRY_INGEST_URL = "https://telemetry.copilotkit.ai/ingest"`（`:40` 附近）——注释钉版 OSS-96 工单："URL 刻意命名清晰以便用户在网络面板看到时明白这是什么"；文档 URL `TELEMETRY_DOCS_URL`（`:47` 附近）与 `packages/runtime/src/lib/telemetry-disclosure.ts` 镜像配对。fetch 3 秒超时（`FETCH_TIMEOUT_MS = 3000`，`:54` 附近）防慢网关拖挂宿主应用。`track()` 是 fire-and-forget（`:62` 注释）：同步返回、失败吞掉、opt-out 短路在**任何网络调用之前**（`:15` 注释），匿名 distinct_id 由 persistence 层 getOrCreateTelemetryDistinctId 提供。

### shared/TelemetryClient：双汇流与采样数学（v1 线）

`packages/shared/src/telemetry/telemetry-client.ts` 是 v1 服务端遥测核心：

- **硬编码 Segment writeKey**：构造函数里 `process.env.COPILOTKIT_SEGMENT_WRITE_KEY || "n7XAZtQCGS2v1vvBy3LgBCv2h3Y8whja"`（`telemetry-client.ts:72-74`）——默认值直接写死在源码，env 只能覆盖不能清空（想关掉走 telemetryDisabled 路径）；
- **单次掷骰双汇流**：`capture()` 里对未识别（无 telemetry_id）调用者先掷 `shouldSendEvent()`（`:96-99`），命中后**同一事件同时**发给 Lambda（`lambdaClient.send`，`:139-145`）与 Segment（`this.segment.track`，`:147+`）——一次决策两个去向，不会出现"Segment 有而 Lambda 无"的口径劈叉；
- **采样权重正确性**：`effectiveSampleRate = this.telemetryId ? 1 : this.sampleRate`（`:111`）——identified（付费客户）恒 100%、匿名按 sampleRate；每事件附 `sampleWeight: 1 / effectiveSampleRate`（`:112-115`）。注释 `:109-111` 讲透动机：若用单一全局权重，identified 客户计数会被放大约 1/sampleRate 倍——逐事件按人群算权重，下游外推（按 sampleWeight 加总）才对两类人群同时正确；
- **licenseToken 不外发**：JWT 本体刻意不进 globalProperties（digest b20 钉版），只有解出的 telemetry_id 经 lambda-client 请求头传输。

### lambda-client：claim-only 信任与 wire boundary

`packages/shared/src/telemetry/lambda-client.ts`：

- **不验签**：头部注释 `:12-14` 明言——license token 是 Ed25519 签名的 JWT，SDK 只 base64url 解码 payload 段提取 `telemetry_id`，"without verifying the Ed25519 signature, which is the license-verifier's job"（`:64-69` 重复钉版）。这是 **claim-only 信任模型**：遥测网关信认客户端声称的身份，防伪验证留给 license-verifier 包（根 package.json 钉 `@copilotkit/license-verifier ~0.4.2`）；
- **wire boundary 剥密**：`STRIPPED_KEYS = new Set(["cloud.public_api_key", "cloud.publicApiKey"])`（`lambda-client.ts:51`）——出站前把云 API key 从 properties 里剥掉，浏览器可见的 key 不进遥测管道；
- atob/Buffer 双路径兼容浏览器与 Node，fetch 配 AbortController 3 秒超时（digest b20）。

### v2 runtime 遥测与 Scarf 漂移

`packages/runtime/src/v2/runtime/telemetry/telemetry-client.ts` 是 v2 独立实现：默认 `private sampleRate: number = 0.05`（`:23`，5% 匿名采样）；同样 identified 豁免（`:61` 注释）；`setSampleRate` 带 NaN 防护（`:74`，`parseFloat('nonsense')` 不得静默丢掉全部匿名事件）。

**README 漂移实证**：`packages/runtime/README.md:60` 声称 "CopilotKit uses [Scarf](https://scarf.sh) for anonymous usage analytics"，package.json 也确有 `"@scarf/scarf": "^1.3.0"`（`runtime/package.json:98`）——但 `runtime/src` 全目录 grep "scarf" **零引用**（唯一残留是 `packages/shared/src/telemetry/scarf-client.ts`：URL 路径硬编码包版本、构造函数空占位）。实际运行时遥测全部走上述 v2 TelemetryClient → Segment analytics-node 链路。README 描述的是 Scarf 时代，实现已迁 Segment 两次（v1 shared 链 + v2 runtime 链），文案从未跟上。

## 外部连接（imports 边上下游）

- **web-inspector 上游**：`@copilotkit/core`（pnpm workspace 内部包，值导入 ɵselectThreads 等 + 两组 type-only 导入）、`lit`（组件基座）、marked（markdown 渲染）、lucide（图标）；`.svg` 资产走 Vite URL import；tsdown UMD globals 把 @copilotkit/core/lit/marked/lucide 全映射宿主全局（digest b61）——分发策略假定宿主页面已加载这些库。
- **web-inspector 下游**：`packages/react-core` 的 `CopilotKitInspector.tsx` 动态 import 本包 + mounted 标志防 SSR 水合错配（digest b5）——React 用户不直接接触 custom element，经包装组件接入。
- **遥测线上游**：`packages/shared/src/telemetry/events.ts` 的 `AnalyticsEvents` 类型映射（点分事件名 → payload 的 keyof 索引，`capture<K extends keyof AnalyticsEvents>` 获得逐事件类型检查）；`packages/react-core/src/setupTests.ts` 对 `@segment/analytics-node` 的 vi.mock 佐证 react v1 链的 node 端遥测依赖。
- **遥测线下游**：`telemetry.copilotkit.ai` Lambda 网关（fan-out 到 PostHog/Reo/Scarf 三后端，`lib/telemetry.ts:5` 注释）；Segment（writeKey 硬编码那个项目）。
- **消费点**：runtime v1 线（lib/telemetry-client.ts 从 `../../package.json` import 版本号是真实 import）+ runtime v2 线 + inspector 线三处实例化。

## 数据流

inspector 面板的一次数据访问与一次遥测上报：

1. **挂载**：宿主页面 `<cpk-web-inspector auto-attach-core>` → WebInspectorElement（`index.ts:2340`）connectedCallback → `autoAttachCore` 为 true 时（`:2794` 判定）扫描全局发现 CopilotKit 实例并订阅 core 的线程/状态流（ɵ API）；
2. **面板数据**：CpkThreadList（`:361`）渲染线程列表，选中项交给 ɵCpkThreadDetails（`:671`）——三个 Lit 类在同一个 shadow DOM 树内协作，数据全部来自内存中的 core 订阅，不发新请求；
3. **持久化**：面板展开状态、opt-out 标志经 `lib/persistence.ts` 的 is* 校验器读出 localStorage——被污染的存储在校验层被拦，不炸 UI；
4. **遥测上报**：用户点了 banner → `track("oss.inspector.banner_clicked", {...})` → opt-out 检查（短路在任何网络调用前）→ POST `telemetry.copilotkit.ai/ingest`（3 秒超时、fire-and-forget）→ Lambda allowlist 门控 → fan-out 三后端；
5. **服务端遥测**（对照）：runtime 进程里 v1 TelemetryClient.capture → identified? 直发 : 掷 5%/配置采样 → 单决策双发（lambdaClient.send + segment.track）→ 每事件带 sampleWeight 供下游正确外推 → lambda-client 出站前剥掉 STRIPPED_KEYS 里的 public_api_key。

## 设计决策

- **单文件巨石 vs 拆分**：7714 行不拆是有代价的选择——Lit 组件三件共享大量私有状态与模板，拆分收益（可读性）低于成本（跨文件传 refs）；图谱把它当"警示样本"而非"最佳实践"。新人读它建议从三个 class 声明行切入做三段式阅读。
- **隐私契约写在代码里**：lib/telemetry.ts 头部 29 行注释 + inspector 面板内 opt-out + docs 页镜像常量 + URL 刻意透明命名（OSS-96）——四层设计把"我们收集什么"变成可审计事实而非法务文档。对比很多产品把遥测藏在混淆代码里，这是开源产品的信任工程。
- **claim-only 是分层信任**：lambda-client 不验 Ed25519 不是偷懒——验签需要 license-verifier 拉进浏览器 bundle（Node crypto 依赖），而遥测被伪造的 worst case 只是"别人替你上报假事件"，商业风险归零；分层后 license-verifier 只在真正需要防伪的场合（premium 功能解锁）运行。
- **采样数学的讲究**：`sampleWeight: 1/effectiveSampleRate` 逐事件计算而非全局常量，防止"identified 客户被放大 20 倍计数"——这个 bug 的隐蔽之处在于小样本测试时看不出来，规模化后才爆。注释把推理链完整留在源码里。
- **Scarf 残留是迁移化石**：README 文案、package.json 依赖、scarf-client.ts 空壳三件都没清——遥测后端从 Scarf 迁 PostHog/Segment 的历史在三个文件里留下不一致地层，读文档者需要 grep 源码才能知道真相（本篇标题里"漂移"的由来）。
- **三套遥测实现并存**：shared/v1（Segment+Lambda 双汇流，服务端）、runtime/v2（独立 TelemetryClient，5% 采样）、inspector（三事件直发）——没有统一抽象，因为三者的运行环境（Node 进程/Edge/浏览器）、隐私边界、事件量级完全不同，强行抽象会造出最平庸的公共分母。

## 新人提示

1. **读 index.ts 别线性读**：先看 `:361/:671/:2340` 三个 class 头与 `:2334/:2337/:7704` 三个注册点，再按需跳方法；7714 行线性读会迷失。
2. **调试 inspector 用 DevTools 而非日志**：它是 shadow DOM Web Component，宿主 CSS 隔离；`document.querySelector("cpk-web-inspector").shadowRoot` 是你 friend。
3. **关遥测的三条路**：inspector 面板 opt-out（短路所有网络调用）/ env `COPILOTKIT_SEGMENT_WRITE_KEY` 覆盖（只改目的地）/ telemetryDisabled 构造参数（v1 线全关）——注意没有"只关 Segment 留 Lambda"的开关，双汇流是原子决策。
4. **新增遥测事件 checklist**：shared 线要在 `events.ts` 的 AnalyticsEvents 映射加类型（获得编译期检查）；inspector 线要同时去 Lambda allowlist 加条目，否则事件到网关即被拒（`:26-29` 注释）。
5. **别信 runtime README 的 Scarf 描述**：装 @scarf/scarf 不会让 runtime 上报 Scarf——它零引用；真遥测走 Segment，禁用路径见上条。
6. **sampleWeight 是外推关键**：做用户数据分析时务必按事件的 sampleWeight 加权（identified=1、匿名=1/sampleRate），直接 count 会系统性低估匿名流量。
