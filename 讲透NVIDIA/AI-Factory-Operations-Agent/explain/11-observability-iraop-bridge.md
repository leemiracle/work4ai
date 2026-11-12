# 11 · observability 插件 + iraop 桥 + nemoclaw.json：观测工具面与自实现 MCP 客户端

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`files/openclaw-seed/extensions/observability/{index,loki,grafana}.ts`（266/165/516 行）、`extensions/iraop/index.ts`（469 行）、`files/openclaw-seed/nemoclaw.json`（373 行）
> 协同文件：`extensions/observability/openclaw.plugin.json`、`extensions/iraop/SKILL.md`、`templates/openclaw.yaml:213`（装配点）

## 一、角色定位

observability 与 iraop 是 agent 的两条"外部证据通道"：前者让 agent 自己查 Prometheus/VictoriaMetrics 指标与 Loki 日志、自己建 Grafana 仪表盘并推到用户眼前；后者把 NVIDIA 基础设施文档检索（iraop/Sequoia 服务）作为 MCP 工具接进来。两者的实现取向截然不同——observability 直接手写 HTTP 调各系统的 REST API，iraop 则手写了一个 **176 行的 MCP-over-SSE 客户端**去对接远端 MCP 服务器。nemoclaw.json 是两者的共同宿主配置：它把插件开关、端点 URL、凭据环境变量引用全部编译成 OpenClaw 的 `openclaw.json`。

命名陷阱先钉死：`nemoclaw.json` **不是合法 JSON**——它是 Helm 模板（文件头 33 行全是 `{{- range }}` 指令，`nemoclaw.json:1-33`），渲染后才成为 JSON，经 seed ConfigMap 的 `tpl` 调用（`openclaw-seed-configmap.yaml:28`）落地为 `openclaw.json`（`openclaw.yaml:213` 拷贝）。"nemoclaw"是早期代号残留，仓库内文件名与渲染产物名不一致是既成事实。

## 二、内部结构

### observability 三件：指标、日志、仪表盘

**index.ts（266 行）是插件入口与指标工具**。`definePluginEntry`（`index.ts:169`）先挂 Loki 工具再注册自家三件：`observability_metric_names`（`:185`）、`observability_query`（`:215`，PromQL 即时查询）、`observability_range_query`（`:242`，区间查询）。内建防灌爆：`compactResult()`（`:102`）限制返回的序列数与每序列点数（`maxSeries=50` 默认，`query()` 的参数），`parsePromValue`（`:78`）把 Prometheus 文本值安全转数。`prometheusFetch`（`:83`）是三条工具共用的取数通道。

**loki.ts（165 行）是日志工具**，防御密度全仓罕见：`lokiUrl` 校验拒绝任何 userinfo/query/fragment（`loki.ts:41-43`，与 proxy/校验层的 HTTPS-only 哲学一致）；时间窗硬上限 24 小时（`:30`）；**响应体流式计数 2MiB 即断**（`:60-63`）——不等下载完才发现爆炸；标签值全量 encodeURIComponent 且拒绝 `.`/`..`（`:93,101`）；`observability_log_labels`（`:81-120`）做有界 fan-out：最多 20 个标签名 × 各取 50 值 + series 查询（`:106-115`），并刻意同时返回 `streamLabels`（"哪些标签属于同一来源"，`:84` 的工具描述写明用途）——让模型选对标签组合而不是瞎猜。`observability_logs`（`:122-164`）支持 range/instant 两模式（instant 禁带 start/step，`:142`），streams 结果按剩余配额逐流截断（`:156-162`）。

**grafana.ts（516 行）是仪表盘工具**，心脏是 `validatePanels()`（`grafana.ts:169-271`，恰 103 行）。它对每块待建面板做**三通道预检**：

1. 数据源存在性：拉 `/api/datasources` 清单核 UID+type 双匹配（`:182,185-187`），日志面板必须 Loki 数据源（`:189-191`）；
2. Prometheus 直查：`/api/v1/query` 试跑（`:193-206`），`requireData=true` 时空序列即 error；
3. **Grafana 真渲染 + UI 代理双复核**：`POST /api/ds/query`（`:209-214`）确认有数据帧，再经 Mosaic UI 的 `/api/grafana/proxy/api/ds/query`（`:232-236`，带 `Origin: uiUrl`）确认**用户浏览器里那扇 iframe 也能拿到同样数据**——三通道全绿才 `ok: true`（`:266`）。

这套"先验证再创建"的逻辑挂在 `dashboard_create`（`:399-479`）：验证失败返回 `created:false` + 完整 issues + `availableDatasources`（`:428-434`），模型拿到可用数据源清单即可自纠重试；成功则 `buildDashboard()`（`:340-356`，schemaVersion 42、15s 刷新）POST 到 `/api/dashboards/db`（`:437-441`），随后经 `/api/ui/actions` 发 `open_grafana` 动作把 iframe 推到用户 UI（`:450-462`）。`dashboard_list`（`:377-397`）与 `dashboard_open`（`:481-516`）补齐发现与复开。认证双轨：Grafana API 走 token/basic（`authHeaders:148-159`），UI 通道走 `MOSAIC_UI_MACHINE_TOKEN`（`uiAuthHeaders:161-167`）。

### iraop/index.ts：176 行手写 MCP-over-SSE 客户端

`callMcpTool()`（`iraop/index.ts:107-282`）是全仓唯一的 MCP 客户端实现，注释自陈动机（`:102-106`）："每调用开新流、跑 initialize 握手、调一个工具、关闭。无状态+简单。约 200ms 连接开销对 iraop 30-120 秒的研究往返是噪声"。结构五段：

1. **SSE 解析泵**（`:152-211`）：手写增量解析——先把 `\r\n?` 归一为 `\n`（`:163`，SSE 规范允许三种换行）、按空行切事件、`event:`/`data:` 行归类、注释行跳过（`:171`）、data 前缀**恰好一个**可选空格（`:176-177`，注释强调用 trim 会啃掉 JSON 内部缩进）。`endpoint` 事件解析出会话 URL（`:180-185`），`message` 事件按 id 匹配 pending map 解决/拒绝（`:186-201`）。
2. **RPC 层**（`:213-251`）：`rpc()` 递增 id、pending 注册、POST 失败即抛；`notify()` 无 id。401 错误有专属文案（`:225-230`）——注释点明"SSE 开流和每个 POST 是独立 HTTP 请求，各自鉴权"（`:222-224`），开流成功不代表调用腿成功。
3. **握手**（`:253-268`）：`initialize`（protocolVersion 2024-11-05）→ `notifications/initialized` → `tools/call`，标准三步。
4. **超时与清理**（`:115-116,273-281`）：AbortController 整体超时（默认 240 秒，`:9`），finally 里 cancel reader 并 await 泵退出。

外围四个工具注册在 `definePluginEntry`（`:329-469`）：`iraop_query`（`:336-413`，depth 缺省 **quick**——`:367-372` 注释给出理由：iraop 服务端默认 deep 是"多代理迭代研究，数分钟级"，且与 OpenClaw 共享同一个 vllm-nemotron 端点会争推理容量）、`iraop_list_collections`（`:415-425`）、`iraop_list_documents`（`:427-446`）、`iraop_get_document`（`:448-467`）。配置读取有个精致细节：`${VAR}` 残留检测（`:48-53`）——OpenClaw 对未设置的环境变量会保留字面 `${VAR}`，当 bearer 发出去会被 iraop 记成"被拒的调用方"而非"未配置"，故显式清空。`toOpenClawResult()`（`:287-304`）处理 MCP `isError` 语义：把错误文本拼出抛异常而不是吞掉。查询结果固定 unshift 一段"Evidence scope: documentation research..."免责声明（`:402`）——文档研究≠现场取证，边界写进每次回答。

### nemoclaw.json：配置编译器

373 行里前 33 行是**纯 Helm 逻辑**：遍历 managed MCP servers（`:2-21`）与 external servers（`:22-33`），把 secretHeaders 编译成 `${MOSAIC_MCP_...}` 环境变量引用（`:8-9,26-27`）、拼 in-cluster URL `http://mcp-{name}:{port}{path}`（`:17`）——与 openclaw.yaml:530-550 的 env 注入严丝合缝。JSON 体从 `:34` 开始：gateway 18789 token 鉴权（`:35-40`）、agent 主模型 `llm/{llmModel}`（`:65`）、skills 白名单六项（`:67-74`）、edit/HITL 状态（`:235-237`）、各插件配置块（kubernetes `:273-282`、openshell `:288-293`、iraop `:302-308`、bcm `:312-324`、remote-ssh `:328-337`、grafana/observability `:341-362`）。观察 `:341-362`：grafana 与 observability 两插件的配置块几乎同构（同一组 URL/数据源/凭据引用），再次印证第 07 篇的判断——独立 grafana 插件与 observability 内嵌 grafana.ts 是功能重叠的两代实现，nemoclaw.json 两块配置都留着。

## 三、外部连接

- **数据面**：Prometheus/VictoriaMetrics（observability 三工具）、Loki（`observability.loki.url` + 可选 `X-Scope-OrgID` 租户头，`loki.ts:47-48`）、Grafana（三 dashboard 工具）、Mosaic UI（`/api/ui/actions` 推 iframe、`/api/subagents/events` 推进度）。
- **iraop 服务**：`http://iraop:8000/mcp/sse`（`iraop/index.ts:8`），由独立的 iraop stack（Sequoia 文档检索）提供，凭据 `IRAOP_API_KEY`（`openclaw.yaml:634-640` 注入，Secret 生成见 `secrets.yaml:47-65`）。
- **nemoclaw.json 的消费链**：values → tpl 渲染 → seed ConfigMap → init-config cp → OpenClaw 启动加载。改插件配置的第一入口是 values.yaml 与 nemoclaw.json 模板，不是落盘后的 openclaw.json（会被下次滚动覆盖）。
- **progress 上报**：iraop 的 `postSubagentEvent`（`:72-100`，fire-and-forget，失败静默）让用户在 UI 看到 "Opening IRA MCP/SSE connection" 等阶段事件——长工具的体验补偿。

## 四、数据流

仪表盘创建流：agent 调 `dashboard_create{title,panels}` → validatePanels 三通道预检（数据源→PromQL 试跑→Grafana ds/query→UI 代理）→ 全绿则 POST dashboards/db → `/api/ui/actions` open_grafana → 用户 UI 切到 Grafana 标签页看到 iframe。任何一通道 fail，返回带 availableDatasources 的自纠载荷。iraop 查询流：agent 调 `iraop_query{question,depth:"quick"}` → 开 SSE 流（Bearer）→ endpoint 事件给会话 URL → initialize 三步 → tools/call `query` → 30-120 秒后结果回流 → 免责声明 unshift → content 返回；期间 delta 事件推 UI。

## 五、设计决策

- **三通道验证而非一查了之**（`grafana.ts:169-271`）：数据源存在、查询合法、Grafana 能渲染、**用户浏览器代理也能渲染**——最后一条是 AFOA 特有的诚实：仪表盘建出来用户打不开等于没建。UI 代理通道还带 `Origin: uiUrl`（`:234`），复刻浏览器的真实请求形态。
- **手写 MCP 客户端 vs 引 SDK**：iraop 的理由（`:102-106`）是典型的"一次性调用 + 高延迟容忍"场景，连接复用无收益；对照第 10 篇 mosaic-mcp 的 stdio 手写——AFOA 两次选择都说明 MCP 协议面足够小，依赖不值得。
- **Loki 的发现工具返回"证据"而非"模式名"**（`loki.ts:105-118`）：labels 工具同时返回值样本与 series 归属，模型第一次调用就能定位正确标签组合——把"先 schema 后数据"的两步并一步。
- **quick 为缺省档**（`iraop/index.ts:367-372`）：推理容量是共享资源，默认档位的选择就是容量策略。

## 六、新人提示

- 改 grafana/loki 端点时改 values 的 `observability.*` 与 nemoclaw.json `:341-362` 两块配置，**不要**只改一处；`MOSAIC_LOKI_AUTHORIZATION`、`MOSAIC_GRAFANA_BASIC_*` 都是 openclaw.yaml 注入的环境变量（`:590-612`），ConfigMap 里只有 `${...}` 引用。
- iraop 报 401 时看 `iraop/index.ts:225-230` 的专属文案——开流 401 与 POST 401 是两个不同的失败点，日志前缀 `[iraop-plugin]`（`:128`）可直接 grep。
- validatePanels 的 requireData 默认 true（`grafana.ts:425`）——建"空但合法"的仪表盘要显式传 false，别改默认值。
- ⚠️ 甄别记录：任务简报"iraop 176 行自实现 MCP 客户端"实测吻合（`callMcpTool`，`iraop/index.ts:107-282`，282−107+1=176）；"validatePanels 103 行"吻合（`grafana.ts:169-271`）。**图谱 file 节点 summary 称 iraop"经 MCP streamable HTTP 调用"与源码不符**——源码实现是 MCP-over-SSE 传输（`DEFAULT_SSE_URL` 以 `/mcp/sse` 结尾，`:8`；注释通篇 MCP-over-SSE，`:102,222`），以源码为准。nemoclaw.json=Helm 模板化 JSON 的判断与 `openclaw-seed-configmap.yaml:28` 的 `tpl` 调用互证。

（行号锚基于当前工作树源码逐条核实。）
