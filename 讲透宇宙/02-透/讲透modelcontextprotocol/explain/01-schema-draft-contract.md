# 精讲：schema/draft/schema.ts —— MCP 协议契约真源（draft 终态）

## 角色定位

图谱 `file:` 节点，归 L09 契约层，批分析显示 32 条边指向它（全图入度最高）。它是**协议契约真源**：TS 声明（纯 interface/type，勘误钉版：**不用 zod**）经 typescript-json-schema 编译为 `schema/draft/schema.json`，再经 typedoc 生成 `docs/specification/draft/schema.mdx`；由 `scripts/generate-schemas.ts` 编译（L64/L95）。全文 3197 行，`LATEST_PROTOCOL_VERSION = "2026-07-28"`（L30）。

## 内部结构

五族分区：

- **JSON-RPC 地基**（L1-309）：`JSONValue`（L6）→ `JSONRPCMessage`（L26）→ `JSONRPCRequest`（L268）→ `JSONRPCResponse`（L309）。
- **错误码族**（L311-534）：五标准码 const（L312-316）；L407-425 注释钉死分区——`-32000~-32019` 归实现、`-32020~-32099` 归规范，历史码永不复用。
- **方法族**：21 个 `method:` 字面量（10 client 请求见 `ClientRequest` L3153-3163，3 个 server→client，8 通知见 `ServerNotification` L3174），3 个 deprecated 后**活跃面恰 18**——GA "26→18" 终态。
- **通知族**：cancelled（L648）、progress（L1040）、三个 list_changed、subscriptions/acknowledged（L1398）。
- **结构化类型族**：`InputRequest` 联合（L537）、`InputRequiredResult`（L584）、elicitation 受限 schema 六件套（L2876-3118）。

**stateless 重构五件套**（相对 2025-11-25 增量）：

1. **删 initialize/ping**：全文无此字符串——握手移除，零会话状态。
2. **per-request meta**：`RequestMetaObject`（L63）把原 initialize 协商搬进每请求 `_meta`——`protocolVersion`（L76）与 `clientCapabilities`（L98）必填，禁跨请求推断能力；结果侧 `serverInfo`（L157）。
3. **server/discover**（L665）：可选发现端点，`DiscoverResult`（L678）的 `supportedVersions` 替代版本协商。
4. **subscriptions/listen**（L1314）：客户端开长流，`SubscriptionFilter`（L1270）逐项 opt-in，server 先 acknowledged 再推流，通知带 `subscriptionId`（L133）——取代 HTTP GET SSE 与 `resources/subscribe`。
5. **结构化错误族**（L434-526）：三码带机器可读 `data`——`supported[]` 供选版重试（L483）、`requiredCapabilities` 告知缺失（L523）。

## 外部连接

- **上游**：`generate-schemas.ts`（148 行）遍历六版本，check 模式测过期（L120-127）。
- **下游**：`schema.json` 与 `examples/` 样例（`@includeCode` 内联，L324）。
- **图谱边**：六版本 related 演进链 2024-11-05 → 2025-03-26（elicitation）→ 2025-06-18（结构化 output）→ 2025-11-25（URL elicitation）→ 2026-07-28（stateless）→ draft；规范页 `document:` 节点持 depends_on 边。

## 数据流

一次 `tools/call`：`CallToolRequest`（L1882）params（L1863）继承 `InputResponseRequestParams`（L600）——重试可携 `inputResponses`（L605）与 `requestState`（L608，不透明 blob）。响应 `result: CallToolResult | InputRequiredResult`（L1848）由 `resultType`（L234）判别分发：`"complete"` 按 `CallToolResult`（L1809）：`content`（L1813）、`structuredContent`（L1821，符 `outputSchema` L2005）、`isError`（L1837——工具错误留在 result 而非 JSON-RPC error，LLM 可见可自纠）；`"input_required"` 按 L584 补输入后重发。`ResultType` 末位裸 `string`（L216）开放扩展，旧版缺此字段按 `"complete"`（L230-233）。列表类受 `CacheableResult`（L1081，`ttlMs`/`cacheScope`）约束。

## 设计决策

- **TS 而非 zod/手写 JSON**：类型即文档即机器契约，tsc 即校验；编译保证零漂移（CI check 强制），zod 增运行时依赖。
- **删 initialize 动机**：任一 HTTP 请求独立鉴权/路由（网关、serverless 友好），零会话内存；代价是字节膨胀，换来水平扩展。
- **日期版本制非 semver**（仓 CLAUDE.md 钉版）：`schema/[YYYY-MM-DD]/` 冻结 + `draft/` 工作版；废弃走 12 个月保留期（L110 logLevel，SEP-2577）。
- **错误码集中账本**：L407-425 注释即治理，规范码自 -32020 顺序分配。

## 新人提示

- **读法**：L1-534 地基错误族 → L3151-3197 汇总联合建全景 → 按需读方法族；`@category` 即规范章节名。
- **与 `schema/2026-07-28/schema.ts` 差异**：diff 实测仅 4 hunk（8 行），全是 JSDoc `@see` 链接路径差（L51/L60/L117/L140）——**类型层零差异**，draft 是 GA 冻结镜像非超前版。
- **常见误读**：① 无 initialize 握手——能力在每请求 `_meta`；② `isError: true` 仍在 result 内、非 JSON-RPC error；③ sampling/roots/logging 整族 `@deprecated`（L2104/L2718/L2031）；④ `_meta` 前缀第二段 `modelcontextprotocol`/`mcp` 全保留（L45）；⑤ elicitation `requestedSchema`（L2803）仅顶层 primitive 无嵌套；⑥ 枚选用 `oneOf+const+title`（L2959）弃非标准 `enumNames`（L3109）。
> 非空白字符 4781 / 锚 65
