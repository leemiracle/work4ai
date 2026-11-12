# 06 · topics 概念群精读：协议的十一个切面

> 覆盖对象：`/usr-data/data2/repos/aaif-projects/repos/A2A/docs/topics/` 11 篇概念文档（what-is-a2a / a2a-and-mcp / key-concepts / life-of-a-task / agent-discovery / enterprise-ready / streaming-and-async / multi-tenancy / extensions / custom-protocol-bindings / extension-and-binding-governance）+ `docs/definitions.md` 术语表页。全部行号锚经 grep 从源文件核实。

## 一、角色定位

**8 层架构中的 L02：概念与主题文档层。** 仓库知识图谱把 `docs/topics/` 11 篇加 `definitions.md` 归为 L02（12 节点），位于 L01 规范正文（`specification.md`）之下、教程与 SDK 文档之上。它们不是规范：`what-is-a2a.md:244` 明说 "The [A2A specification](../specification.md) is the source of truth for every capability, method, and data structure"——topics 是**规范正文的横向切面**，按关注点而非章节序重组协议知识：安全切面（enterprise-ready）、时间性切面（streaming-and-async）、身份发现切面（agent-discovery）、生命周期切面（life-of-a-task）、生态位切面（a2a-and-mcp）、部署横向扩展切面（multi-tenancy）、可扩展性三切面（extensions + custom-protocol-bindings + governance）。

导航结构佐证这种"切面"定性：`mkdocs.yml:24-31` 把前 8 篇排在 "Introduction" 组，`mkdocs.yml:32-35` 把扩展三篇单独拎出 "Extensions" 组——站点信息架构本身就是"入门切面"与"进阶切面"两档。另有两枚历史化石藏在 `mkdocs.yml:179-181` 的重定向表：`documentation.md → topics/key-concepts.md`、`topics/push-notifications.md → topics/streaming-and-async.md`——push notification 曾是独立主题页，后被合并进 streaming-and-async，这解释了该文为何长达 111 行且前半 SSE / 后半 webhook 结构分明。

与规范分工的典型样本是 enterprise-ready：规范正文两处（`specification.md:1875`、`specification.md:3100`）在安全章节把读者"外包"给本页——`specification.md:3100` 原文 "This section consolidates security guidance... For additional enterprise security considerations, see [Enterprise-Ready Features]"。规范给 MUST/SHOULD，topics 给落地清单。

## 二、内部结构

**主题地图是一张"枢纽 + 三角 + 叶子"网络**（md 间互链共 12 条边，全部核实）：

- **枢纽 key-concepts**：5 条出边辐射全群——`key-concepts.md:52`（→streaming-and-async）、`:95`（→life-of-a-task）、`:101`（→enterprise-ready）、`:102`（→agent-discovery）、`:103`（→extensions），每条都长在对应概念的段落尾部，即"概念提到哪、链接跟到哪"。它还有 1 条入边（`what-is-a2a.md:243`）。本体是 5 要素总表：`key-concepts.md:27-33` 的表格把 Agent Card / Task / Message / Part / Artifact 五要素的描述与 Key Purpose 一并铺开，是全协议概念的最小闭包；`key-concepts.md:69-74` 给出 Part 的 `oneof` 四选一（text/raw/url/data）。
- **扩展三角**：extensions ↔ governance 双向（`extensions.md:73` 出、`extension-and-binding-governance.md:4` 回）、custom-protocol-bindings ↔ governance 双向（`custom-protocol-bindings.md:143` 出、`extension-and-binding-governance.md:4` 回）、cpb → extensions 单向（`custom-protocol-bindings.md:9`）。三页构成协议"可扩展性"子系统的闭环。
- **两条独立单向边**：`what-is-a2a.md:161`（→a2a-and-mcp，深读比较的入口）、`multi-tenancy.md:121`（→agent-discovery，多 agent 各自发卡的依据）。
- **五个纯叶子**：enterprise-ready、life-of-a-task、streaming-and-async、agent-discovery、a2a-and-mcp 在 topics 内部零出边（enterprise-ready 甚至全篇零链接——见第五节）。它们是读者路径的终点站。

**definitions.md 是"术语表"名不副实的机制页**：它不含任何术语定义条目，而是 mkdocs 的 snippet include 容器——`definitions.md:14-16` 用 `--8<-- "docs/spec/a2a.proto"` 语法把 proto 真源直接内嵌渲染，`definitions.md:30` 同样内嵌 `a2a.json`。两处自述真相源关系：`definitions.md:5-6` 声明 proto3 是 "the source of truth for the A2A protocol specification"，`definitions.md:21` 声明 JSON Schema "automatically generated from the protocol buffer definitions"——即 JSON 视图是 proto 的派生物（与 explain-02 的 proto 精读结论一致）。

## 三、外部连接

**topics → specification.md 的锚链共 19 条**，密度分布极不均匀：

- streaming-and-async 独占 10 锚：`streaming-and-async.md:19-21`（Task / TaskStatusUpdateEvent / TaskArtifactUpdateEvent 三个数据结构）、`:40-41`（SendStreamingMessage / SubscribeToTask 两个方法）、`:50`、`:55`（双锚：StreamResponse 与 Push Notification Payload）、`:70-71`——本页几乎是"规范的流式章节导读版"。
- agent-discovery 4 锚：`:3`（§8 Agent Card 规范定义）、`:84`（§3.11.1 GetExtendedAgentCard）、`:106`（§13.3 扩展卡访问控制）、`:108`（§8.6 缓存）。
- custom-protocol-bindings 3 锚：`:20`（§5.8 绑定标识）、`:42`（§5 绑定要求与互操作）、`:88`（§5.4 错误码映射）。
- multi-tenancy 1 锚：`:102`（§8.3.2 客户端协议选择——tenant 回显的规范出处）。

**specification.md → topics 反向 6 处**：`specification.md:41`（→what-is-a2a）、`:133`（→key-concepts）、`:1875` 与 `:3100`（两次→enterprise-ready）、`:1982`（→agent-discovery）、`:3637`（→a2a-and-mcp 附录 B）。双向引用网络让"读规范卡住→跳概念页→再回规范锚点"成为可行路径。

**对外部世界的连接**：a2a-and-mcp 两个生态坐标——`a2a-and-mcp.md:6` 链 modelcontextprotocol.io，`a2a-and-mcp.md:12` / `:17` 给出全站最著名的两句定位 "**MCP is vertical.**" 与 "**A2A is horizontal.**"，`:29` 收束为 "MCP gives each agent depth, and A2A gives your system reach"。life-of-a-task 唯一外链是 `life-of-a-task.md:66` 的 Google 论坛帖 "Demystifying Tasks vs Messages"；what-is-a2a 有 `:159` 的 "Why Agents Are Not Tools" 帖与 `:242` 的 Python 教程入口。extensions 的外链最重：`:49-52` 四个官方示例仓（secure-passport / timestamp / traceability / AGP）、`:276` 直接用 `--8<--` 远程内嵌 a2a-samples 的 Python 源码、`:299` 收尾链 Google 官方博客。

**enterprise-ready 的"终态"定位**：如前述，规范两次把安全综合指引的出口指向它；同时它自己零出边、零互链（全篇 grep 无任何 md 链接），只被 key-concepts.md:101 引用一次。它是网络中的汇点（sink）。

## 四、数据流

**读者的主数据流是"what-is-a2a 三岔口"**：`what-is-a2a.md:240-244` 的 "What's Next" 给出三条分流——`:242` "Prefer a hands-on approach?" 进 Python 教程；`:243` "Want the foundations?" 读 key-concepts；`:244` "Want to deep dive?" 直捣 specification。这决定了 topics↔规范↔教程三层的跳转拓扑：概念页负责"何时用/为什么"，规范锚点负责"精确语义"，教程负责"手上跑通"。

**运行时的三股数据流也在本层讲透**：

1. **发现流**（agent-discovery）：客户端按 `agent-discovery.md:25` 的标准路径 `GET https://{domain}/.well-known/agent-card.json`（RFC 8615）拉卡，`:100` 的服务端指引要求 `ETag` 从卡片 `version` 字段或内容哈希派生以支持条件请求；拿到卡后进入 what-is-a2a.md:195-208 的认证序列图（解析 securitySchemes → Auth Server 换 JWT），最后 POST 消息。
2. **扩展协商流**（extensions）：`extensions.md:90-91` Agent Card 内 `AgentCapabilities.extensions` 声明能力 → `extensions.md:177-185` 客户端在 HTTP 头 `A2A-Extensions` 携带逗号分隔的扩展 URI 列表请求激活 → 服务端忽略不支持的、激活支持的 → 响应回显同名头（`extensions.md:217-235` 的完整请求/响应对）。扩展 payload 走 metadata 命名空间：请求示例 `extensions.md:211` 把参数放在 `"https://example.com/ext/konami-code/v1/code": "motherlode"` 这样的 URI 键下。
3. **租户回显流**（multi-tenancy）：`multi-tenancy.md:74-77` 定义 `tenant` 为服务端完全自定的 **opaque string**；`:98-101` 的硬规则是客户端 MUST 原样回显所选 `AgentInterface` 的 tenant 值、未设置则 MUST 省略——`:105-107` 进一步说该字段可承载 agent 标识 / workspace slug / 组织 ID 等任意判别键。

**推送通知流**是数据流最复杂的一条（streaming-and-async 后半）：`streaming-and-async.md:45` 点明适用场景是"minutes, hours, or even days"级长任务；`:50-53` 客户端交 `TaskPushNotificationConfig`（webhook URL + 可选 token + 可选 authentication）；`:55` 通知 payload 复用 `StreamResponse` 结构；`:96-108` 给出完整的 JWT+JWKS 非对称密钥流（服务端签发含 iss/aud/iat/exp/jti/taskId 的 JWT → webhook 按 kid 取公钥验签）。配套安全边界在 `:83-85`：服务端不得盲信客户端给的任意 URL，否则沦为 SSRF 攻击源或 DDoS 放大器。

## 五、设计决策

**概念页 vs 规范章节的信息分工**：概念页独占两类内容——"选型指导"与"叙事场景"。样本一：streaming-and-async 的两个 "When to Use" 小节（`:27-34` 流式适用清单、`:58-64` 推送适用清单）在规范里没有对应物，规范只定义结构。样本二：life-of-a-task 的三型 agent 分类（`life-of-a-task.md:45-64`：message-only / task-generating / hybrid）是文档层的归纳性指导，"hybrid 一旦建 Task 便只回 Task"（`:62-64`）这类行为约定以叙事而非 MUST 句式给出。规范则反向只在需要精确定义处出现——概念页用锚链把裁量权还给规范。

**零外链叶子页的存在价值**：enterprise-ready 全篇 139 行无一条链接，内容是 TLS/认证/授权/隐私/可观测/API 治理六节清单式最佳实践（如 `enterprise-ready.md:51-55` 的 401 配 `WWW-Authenticate`、403 语义）。推断：这种"自足闭合"写法服务于点查与审计场景——安全审查者可整页打印核对，不被链接牵走；它的流量入口全部来自外部（规范两处 + key-concepts 一处），不需要也不应该自我导流。

**扩展机制的双命名空间设计**：`extensions.md:58-60` 规定官方扩展用 `https://a2a-protocol.org/extensions/` URI 前缀 + `ext-` 仓前缀（实验态 `experimental-ext-`）；`custom-protocol-bindings.md:127-129` 对偶地规定 `bindings/` URI 前缀 + `cpb-` 仓前缀。关键句是 `extension-and-binding-governance.md:34`："These URIs are identifiers, HTTP access is not expected"——URI 只做全局唯一标识符、不承诺可访问，把"身份"与"托管位置"解耦（`extensions.md:257-259` 还建议用 w3id.org 永久标识服务防断链）。治理页 `:14-21` 用一张双列表格统一两种工件的层级命名，`:44-48` 给出官方态四要件（RFC 2119 措辞 / Apache 2.0 / 至少一个参考实现 / 网站文档），`:121-125` 规定毕业须 TSC 半数出席、多数通过。这套设计的动机在 `extensions.md:15-16` 自述："customizing A2A without fragmenting the core standard"——扩展层吸收变化，核心协议保持稳定。

**扩展安全默认值**：`extensions.md:173-175` 规定扩展默认不激活（为不支持扩展的客户端保底），`extensions.md:140-146` 规定 `required: true` 的强约束语义与违约拒绝；配套的 `extensions.md:285-297` 安全条款要求扩展新方法必须过与核心方法相同的认证授权检查、MUST NOT 绕过主安全控制。

**任务不可变 + 客户端管版本链**：`life-of-a-task.md:79-81` 规定终态任务不能重启、精修必须开新 Task（同 contextId）；`:121` 明确 artifact 版本链追踪"not part of the A2A protocol specification"、由客户端负责，服务端只需 `:123` 承诺复用一致 `artifact-name`。这是把编排智能放客户端、执行智能放服务端的职责切割。

## 六、新人提示

**推荐阅读顺序**：what-is-a2a（全景 + `:110-129` 五设计原则，尤其 `:126-129` 的 Opaque Execution）→ key-concepts（五要素总表 `:27-33`）→ life-of-a-task（Task/Message 裁量，`:5-12` 的二分法是全协议最重要的判断题）→ 按需切面：做集成读 agent-discovery + streaming-and-async，做平台读 multi-tenancy + enterprise-ready，做协议开发读扩展三篇。

**可跳过**：multi-tenancy（只有多 agent 同域部署才需要）；custom-protocol-bindings（只有要发明 WebSocket/MQTT 等新传输才需要，且 `:45-53` 的三条硬要求——全操作覆盖/数据模型保真/行为一致——先掂量）；extension-and-binding-governance 的法务细节（`:190-193` 的 Linux Foundation 许可授予只在提交贡献时相关）。

**四个坑**：

1. **definitions.md 不是术语表**——想查术语解释会扑空，它只是 proto/JSON 的渲染壳（`definitions.md:14-16`）；概念解释在 key-concepts。
2. **enterprise-ready 是死胡同页**——读完想跳规范对应章节？没有链接，得自己回 specification 搜（安全相关在 §13 附近，规范 `specification.md:3100` 有入口）。
3. **老资料里的 push-notifications 页已不存在**——内容并入 streaming-and-async（`mkdocs.yml:181` 重定向为证），SSE 与 webhook 的能力开关是两个独立字段（`streaming-and-async.md:11` 的 `capabilities.streaming: true` 与 `:49` 的 `capabilities.pushNotifications: true`）。
4. **extensions 示例是虚构的**——konami-code/Magic 8-ball 只是教学示例（`extensions.md:99-135`），真实可用的扩展看 `:47-52` 表格里的四个官方仓。另注意 `extensions.md:249-253`：扩展破坏性变更必须换新 URI，版本不匹配时服务端 MUST NOT 回退到其他版本——对接时按 URI 精确匹配，别做模糊兼容。

**本篇与系列的关系**：规范正文的逐节精读见 explain-01，proto schema 的字段级拆解见 explain-02，教程线见 explain-03；本篇补上 L02 概念层的地图，explain 系列至此覆盖 A2A 文档四层（规范/概念/教程/SDK）。

---

explain-06: 汉字 2149 / 锚 54 / 六节 PASS
