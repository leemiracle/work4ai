# 03 · architecture/index.mdx：一页规范看六代演进（2024-11-05 → draft）

## 一、角色定位

`docs/specification/draft/architecture/index.mdx`（174 行）是图谱 L03 document 层节点、规范树**总纲页**：定义三角色模型，server/*、client/* 挂其下。六代同名页经**版本链 related 边**串成主轴：`2024-11-05→2025-03-26→2025-06-18→2025-11-25→2026-07-28→draft`，stateful→stateless 范式转折落满这 174 行。

## 二、内部结构（draft 版章节地图）

1. **开篇（L7-13）**：关键句 L8-9——"MCP is a **stateless** protocol: every request is self-contained"并自携带版本与能力。2025-11-25 前此处是 "stateful session protocol"，一词之差隔两代范式。
2. **Core Components（L15-82）**：mermaid 架构图（L17-48）；Host（L54-59）；Clients（L63-69，核心 L66 每请求自带版本与能力，无会话内存）；Servers（L76-82，L80：server 经 `InputRequiredResult` 反向索要 sampling/elicitation/roots）。
3. **Design Principles（L84-114）**：极易构建（L89）、可组合（L95）、**不得读全对话/不得窥他 server**（L101-102）、渐进叠加（L109）。
4. **Capability Negotiation（L116-174）**：能力**每请求携带**——client 能力放 `_meta` 的 clientCapabilities 键（L120），server 能力经可选 `server/discover` 发现（L121-123）；时序图（L131-162）三段：Discovery（L137-140）、反向取输入（L144-150）、Subscriptions 订阅流（L155-161）。

## 三、外部连接

draft 四条出链恰覆盖 stateless 三支柱：`server/discover`（L122）、`/server`（L166）、subscriptions（L169）、tools（L171）。拓扑即证据：2024-11-05 出链 `client/sampling`（旧 L180），2026-07-28 起被 subscriptions/tools 取代——sampling 降格为反向取输入的用例。`server/discover.mdx` 仅后两代存在（server/ 目录 4→5）；elicitation、tasks 页均未反哺本页。图谱三层（transports→本页+basic/index→server/*、client/*）以此页为中间层根。

## 四、数据流：六代演进表（重点）

**2024-11-05（184 行）奠基**：stateful session protocol（该版 L7-9）；三原语+stdio；独有 **"## Message Types" 章节（L112-123）**——Requests/Responses/Notifications 三消息类型按 JSON-RPC 2.0 逐条定义；时序图以 Initialize 握手开头、Terminate 收尾。

**2025-03-26（172 行，-12）换轨代**：本页唯一实质改动是**整段删 Message Types**（12 行收编进 basic/index）。真正革命在兄弟页：transports 以 **Streamable HTTP** 替换 HTTP+SSE、authorization 引入 **OAuth 2.1**——本页零感知，未动系统形状。

**2025-06-18（174 行，+2）**：纯增量：加 section-numbers div（L5）。elicitation 落 client/elicitation 页，本页无一字提及。

**2025-11-25（174 行，0）**：本页零改动（仅链接）。tasks（长时任务+终态）落 server 侧；L115 仍写能力 "during initialization"。

**2026-07-28（174 行不变，内容大换血）stateless 转折**：①开篇改写（新 L8-9）；②Clients 删 stateful 会话职责（旧 L63）改 per-request（新 L66）；③Servers 改 InputRequiredResult 三合一（旧 L78→新 L80）；④协商重写：握手→per-request `_meta`+可选 discover（L120-123）；⑤时序图重画：删 Initialize/Terminate，新增三块（L137-161）。guides 联动：debugging 367→389 行（OTel 转向）、inspector 158→209 行（CLI 重写）——协议与生态同步换代。

**draft（174 行）**：仅四处链接改 `/specification/draft/*`（L122/166/169/171）；前沿增量未触总纲，风向标在支柱页（inspector 209→201）。

## 五、设计决策

**为何 stateful→stateless**：会话握手要求 server 维护每连接状态，serverless/边缘/网关下代价随规模陡增，且 initialize 协商的能力无法升降级。2026-07-28 把会话拆成正交两件——**每请求自描述**（L66/L120）+**显式订阅流**（L155-161），状态下沉到实现层；代价是请求冗余与鉴权上移，收益是水平扩展与版本共存。**日期版本制**：每版不可变快照，draft 与 GA 同构。**总纲滞后**：新能力先落角色页一至两版才被收编，须分清"本代新增/本代回填"。

## 六、新人提示

**细读三代跳过两代**：细读 **2024-11-05**（奠基+独有 Message Types）、**2025-11-25**（stateful 终态）、**2026-07-28**（与 2025-11-25 的 diff 是全史含金量最高对照）；**2025-03-26/2025-06-18 的本页可跳**（合计删 12 行加 1 行），看点在 transports/elicitation。**draft 风向标**：别盯总纲，盯三信号——discover 演化、subscriptions 模型、时序图（L131-162）opt/alt 块增删，每次重画都是范式级前兆。

---
*锚基于 draft 版（2026-10-27 快照），历史版锚已标版本，diff 结论经实证。*

**尾注**：非空白 4796；锚 43。
