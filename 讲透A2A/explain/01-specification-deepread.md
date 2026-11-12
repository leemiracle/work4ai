# 01 · specification.md 精读：A2A v1.0 协议的叙事主线

> 目标文件：`/usr-data/data2/repos/aaif-projects/repos/A2A/docs/specification.md`（3639 行，14 章 + 2 附录）；辅助：`docs/whats-new-v1.md`（975 行迁移指南，下文简写 whats-new）与 `specification/a2a.proto`（812 行，简写 proto）。文中全部行号锚均经 `sed -n` 逐条对源文件核实。与仓内其余文档的关系可对照 `onboarding/ONBOARDING.md`（本仓知识图谱的人读入口）。

## 一、角色定位：proto 是法，本文是法典释义

这份文档的开篇第 3 行就钉住版本身份——"Latest Released Version 1.0.0"（specification.md:3），向下兼容追溯 0.3.0 / 0.2.6 / 0.1.0 三个旧版链接。但真正定义它"是什么"的，是 §1.4 Normative Content 一句宪法级声明：`spec/a2a.proto` 是所有协议数据对象与请求/响应消息的**唯一权威 normative 定义**，构建期生成的 JSON 工件（`a2a.json`）是非规范产物，SDK 语言绑定与任何派生形式 **MUST** 从 proto 重新生成而非手改（specification.md:107）。规范甚至给出了这么做的理由：以 proto 为 normative 源确保协议中立性（protocol neutrality）、减少规范漂移（specification drift）、给生态一条确定性演进路径（specification.md:123）。所以 specification.md 的角色不是"另一份规范"，而是 proto 的**人读展开**——这一机械证据就写在文档体内：§3 与 §4 的对象定义大量使用 `{{ proto_to_table("Task") }}` 这类宏占位符（如 Task 在 specification.md:776、AgentCard 在 specification.md:897），文档站构建时由宏直接解析 a2a.proto 渲染字段表（宏机制见 ONBOARDING.md ⑥ 节，`.mkdocs/macros.py` 三宏）。

v1.0 相对 0.x 的收敛，whats-new 概括为四大主题：协议成熟与标准化（proto 从"gRPC 专用实现文件"升格为普适 normative 真源，whats-new:11）、类型安全（枚举从 kebab-case 改 SCREAMING_SNAKE_CASE，whats-new:20）、开发者体验（复合 ID `tasks/{id}` 简化为纯 UUID，whats-new:31；原生多租户，whats-new:33）、企业就绪（Agent Card 签名、三大绑定等价性保证）。规范化程度的跃升还有一个外部标志：§14 整章是 IANA 注册模板（specification.md:3249），把 `application/a2a+json` 媒体类型（specification.md:3255）、`A2A-Version` 头（specification.md:3313）与 `.well-known/agent-card.json`（specification.md:3357）当作正式互联网资产来注册。当一份"迁移指南"里出现 RFC 8785（JCS 规范化）、RFC 7515（JWS）、google.rpc.Status、ISO 8601 毫秒级时间戳（whats-new:546-582）这一串正式依赖清单时，它已经从项目文档变成了准标准文本。

一个读者必须先建立的分层心智来自 §1.3：整个规范分为三层——L1 规范数据模型（Protocol Buffer 消息）、L2 抽象操作（绑定无关的能力）、L3 协议绑定（JSON-RPC / gRPC / HTTP+REST 的具体映射）（specification.md:45、:92、:94、:96）。规范自述这个分层保证"核心语义在所有绑定间保持一致、新增绑定不必动数据模型、开发者可以独立于绑定思考操作"（specification.md:98-103）。读懂这条分层线，后面所有章节的位置就都有了坐标。

## 二、内部结构：14 章的组织逻辑

规范的章节顺序是：术语（§2，specification.md:125）→ 操作（§3，:147）→ 数据模型（§4，:766）→ 绑定要求与互操作（§5，:1143）→ 示例（§6，:1304）→ 认证授权（§7，:1871）→ 发现（§8，:1974）→ 三个绑定分章（§9 JSON-RPC :2260、§10 gRPC :2536、§11 HTTP+JSON/REST :2772）→ 自定义绑定指南（§12，:3004）→ 安全（§13，:3098）→ IANA（§14，:3249），加附录 A 迁移兼容（:3384）与附录 B 与 MCP 的关系（:3627）。

这个顺序对应 §1.3 的三层从内向外交错展开：§3 先讲 L2 的十一个抽象操作（Send Message :159、Send Streaming Message :182、Get Task :214、List Tasks :232、Cancel Task :264、Subscribe to Task :285、四个 Push Notification Config CRUD :313-:383、Get Extended Agent Card :404），§4 再讲 L1 数据模型，然后 §9-§11 才是 L3 的逐绑定落地——操作在前、对象在后，正文里满篇 `#411-task` 这类反向锚把操作签名链接到对象定义。值得注意的是术语节先给 RFC 2119 级别的需求语言定义（MUST/SHOULD/MAY，specification.md:129），这提示全文的粗体关键词都是规范性用语而非修辞。

**（推断）** 规范没有解释自己的章节顺序，以下是从结构读出的叙事判断：发现（§8）与认证（§7）被排在操作（§3）之后，说明文档的默认读者是"实现者"而非"使用者"——先定义协议的对象与行为，再补齐企业化横向关切（认证、发现、签名、缓存），最后用三个绑定分章收口到可部署形态；而"发现→认证→任务→流式→扩展"这条主线其实是运行时的调用链顺序，它体现在 §6 示例的编排里（见第四节），不在章节排序里。安全（§13）作为收尾的横向章节与 §7 纵向分工：§7 管交互流程中的认证授权语义，§13 管实现者必须承担的横向安全责任（授权作用域 :3104、push 安全 :3132、扩展卡访问控制 :3165）。

附录 A 值得单独点名：它是一张改名台账（如 `MessageSendParams`→`SendMessageRequest` 等，specification.md:3388-3395）加一组隐藏 HTML 锚（specification.md:3403-3446），钉死了 v1.0 最大的破坏性变更——kind 判别符移除（§A.2.1，:3461）。附录 B 则用一段"汽车分层"式的分工说明结束全文：MCP 管工具/资源接入，A2A 管 agent 间对等协作，Server agent 可在履行 A2A 任务时用 MCP 调底层工具（specification.md:3631、:3635）。

## 三、外部连接：specification.md 在文档宇宙里的位置

**与 proto 的逐 message 对应**（本章 ↔ 哪个 message，行号双锚）：§4.1.1 Task（:774）↔ `Task`（proto:167）；TaskState（:786）↔ 枚举 `TaskState`（proto:187，九值 TASK_STATE_UNSPECIFIED..TASK_STATE_AUTH_REQUIRED 分布在 proto:189-207）；Message（:792）↔ proto:260；Part（:804）↔ proto:224，其 `oneof content` 四成员 text/raw/url/data 在 proto:225-231；Artifact（:810）↔ proto:280；流事件 TaskStatusUpdateEvent/TaskArtifactUpdateEvent（:818/:824）↔ proto:296/:308；推送配置（:832）↔ proto:470；AgentCard（:895）↔ proto:362，其 AgentInterface 子对象 ↔ proto:336，AgentCapabilities ↔ proto:412；SendMessageRequest（:434）↔ proto:649；SendMessageResponse（proto:780）与 StreamResponse（:456）各自的 `oneof payload` ↔ proto:782/:793。§3.1 的十一个操作整体 ↔ `service A2AService`（proto:19），而 §5.3 的方法映射表（specification.md:1162-1174）把每个操作同时映射到 JSON-RPC 方法名、gRPC 方法名与 REST 端点，是三绑定互查的枢纽表。

**与主题文档（docs/topics/）的双向引用**：规范正文向外链接 what-is-a2a（:41）、key-concepts（:133）、enterprise-ready（:1875）、agent-discovery（:1982）、a2a-and-mcp（:3637）；ONBOARDING.md ② 节把这 12 页主题文档定性为"规范正文的分层复读"，建议先读它们再啃 3639 行正文。**与教程**：ONBOARDING.md ③-④ 指出 Python 教程线（docs/tutorials/python/）演示的正是规范的 §6 示例序列与 Task 状态机。**与 ADR**：§5.5 在解释枚举序列化时显式援引 ADR-001 ProtoJSON 序列化决议（specification.md:1222）。**与 llms 三件套**：docs/llms.txt 将 proto 标注为 normative、JSON Schema 标注为 non-normative（ONBOARDING.md ⑥），与 §1.4 的声明同源。**与 SDK 文档**：SDK 绑定是 proto 的下游产物（specification.md:107），因此 SDK 文档永远追随本文，冲突时以 proto 为准。

## 四、数据流：一次完整交互按规范章节走一遍

以 §6 的示例串起全链路（全部为规范原文示例，行号可复查）：

1. **发现 agent-card.json**：客户端 GET `/.well-known/agent-card.json`（specification.md:1826 示例；:1988 定义三种发现途径——well-known、注册表目录、直接配置）。Agent Card 是 A2A Server **MUST** 发布的元数据（specification.md:1980），缓存走 HTTP 标准（:2246）。
2. **协商**：从卡片的 `supportedInterfaces` 有序列表选第一个自己支持的传输（首项即首选，specification.md:1998；客户端选择规则四条在 :2006-2010，含 tenant 回填义务）；capabilities 里的 streaming（:666）、pushNotifications（:573）、extendedAgentCard（:406）决定后续可用操作，未声明而调用将收到规范错误（能力校验 :571-576）。版本协商：客户端每个请求**MUST**带 `A2A-Version` 头（specification.md:712，也可作为查询参数 :729），服务端按 Major.Minor 匹配语义（:708），不支持则返回 VersionNotSupportedError（:737）。
3. **认证**：三步流程——经卡片 `securitySchemes` 发现要求、带外取凭证、逐请求携带（specification.md:1887-1889）；生产部署 MUST 加密传输（:1879）。原则句：身份信息在协议层处理，不进 A2A 语义（:1873）。
4. **sendMessage**：`POST /message:send`（示例 specification.md:1315），带 role/parts/messageId。返回值二选一：Task（跟踪处理）或直接 Message（简单交互）（:169-170）；默认阻塞直到终态或中断态（:446），`return_immediately: true` 则建任务即返（:448）。taskId 由服务端生成（:610），客户端提供 taskId 建新任务不被支持（:615）；contextId 逻辑分组多任务多消息（:586），只给 taskId 时 agent 必须反推 contextId、两者不匹配必须拒收（:627-628）。
5. **Task 状态机**：JSON 线上八个状态值全列于验证错误示例（specification.md:1614）：SUBMITTED/WORKING → 终态 COMPLETED/FAILED/CANCELED/REJECTED（终态集合见 :175、:210），中断态 INPUT_REQUIRED（多轮续问示例 :1383-1439，状态 :1414）与 AUTH_REQUIRED（agent 把授权责任委托给客户端，:1919；客户端可再向上委托形成 AUTH_REQUIRED 任务链，:1945）。注意 AUTH_REQUIRED 的授权范围规范刻意不定义（:1966-1972）——状态转移本身不等于授权。
6. **artifact / 事件流**：流式场景 `POST /message:stream`，SSE 响应依次下发 task → artifactUpdate → statusUpdate（示例 specification.md:1370-1381）。流的两种合法形态：message-only（恰好一个 Message 即关流，:208）与 task lifecycle（Task 开头，终态关流，:210）。事件全局有序 MUST 保证（:683）；同一任务可并发多流、事件广播且互不影响（:687-694）；SubscribeToTask 重订时首事件必须是当前 Task 快照，专门堵住"GetTask 之后、订阅之前"的信息丢失缝隙（:311）。结果永远走 Artifact 而非 Message（:758），Message 不承诺可靠投递（:762）。
7. **push**：长任务场景先注册 webhook（REST 端点组 :1170-1173），任务变更时 agent 向 webhook POST 一个 StreamResponse 载荷（specification.md:844；四选一结构 :862-869；端到端示例 :1620-1690）。客户端 MUST 回 2xx（:877）且应幂等消费（:878）；服务端 at-least-once 投递（:884）；删除配置幂等（:402）；URL 须校验私网段防 SSRF（:3143）。

## 五、设计决策：从规范原文论证四个取舍

**1. Part 用 oneof 多态而非类型继承。** v1.0 把 v0.3 的 TextPart/FilePart/DataPart 三类型合并为单一 `Part`，载荷是 proto `oneof content { text | raw | url | data }`（proto:224-231；whats-new:277、:339）。规范在附录 A.2.1 给出了官方理由清单：与 Protocol Buffers 的 oneof 语义对齐、消除"字段名+kind 值"的冗余、让 JSON-RPC 与 gRPC 表示更贴近、简化 schema 代码生成、**消除在 schema 语言里表达继承结构的需要**、强化强类型语言中的类型安全（specification.md:3550-3556）。运行时判别从 `part.kind === "text"` 变成成员名本身——"member name acts as the discriminator"（:3491），流事件同理（`statusUpdate`/`artifactUpdate` 包裹对象，:3524-3530）。连带的横切约定：JSON 全部 camelCase（:1204），枚举值按 ProtoJSON 用 proto 定义里的 SCREAMING_SNAKE_CASE 字符串（:1215）。这是 whats-new 标记的唯一 CRITICAL 级破坏性变更（whats-new:608-642）。

**2. Task 状态集的取舍。** 规范没有一篇"状态机设计说明"，但从行为条款可以拼出取舍逻辑（**推断**）：四个终态被反复用于"不可再收消息/必须关流/不可取消"的判定（:175、:210、:305），把 CANCELED 与 REJECTED、FAILED 分开，让"客户端主动取消""服务端拒绝""执行失败"三种结局在审计与重试策略上可区分；INPUT_REQUIRED 与 AUTH_REQUIRED 两个中断态是异步-first 原则的落点——规范明言 blocking 模式要等到"terminal **or interrupted** state"（:446），中断态是任务停摆等待对端动作的正规通道，且 AUTH_REQUIRED 支持沿 agent 链向上委托（:1945）。

**3. push notification 为什么独立通道。** 规范 §3.5 开篇定性：三种更新机制是**互补**的（specification.md:648），并各自给出适用场景——轮询"简单、全绑定可用、适合防火墙后的客户端"（:652-657），流式"低延迟、需常连接"（:659-666），推送"server-to-server、长任务、事件驱动架构、客户端无需维持连接"（:668-673）。关键的一句机制设计："无论 agent 使用哪种协议绑定，WebHook 调用一律用 plain HTTP 与 HTTP 绑定定义的 JSON 载荷"（:677）——推送通道与主绑定解耦，客户端甚至可以只用 gRPC 而让回调走 HTTP。载荷复用 StreamResponse 格式（:844）让推送与流式共享同一套事件类型；（**推断**）这避免了为离线场景再发明一套事件格式的成本，但"复用即省成本"的动机是本文推断，规范只陈述了复用事实。

**4. 错误模型的统一。** 所有绑定的错误**MUST**传达三元组：机器可读 code、人类可读 message、可选 details 数组（每项带 ProtoJSON `Any` 的 `@type`，推荐 google.rpc 类型，specification.md:540-547）。§5.4 给出九个 A2A 专属错误到 JSON-RPC 码（-32001~-32009）、gRPC status、HTTP status 的全映射表（:1180-1190）；因多个 A2A 错误可能映射同一 HTTP 400，实现 MUST 附带 ErrorInfo（reason 大写蛇形、domain 固定 "a2a-protocol.org"）消歧（:2939-2943）。防信息泄露条款也在这条线上：服务端 SHOULD NOT 区分"不存在"与"无权访问"（:527）。

## 六、新人提示

**读规范的正确顺序**（结合 ONBOARDING.md ⑧ 的 Day 1 路线）：先读 §1.3 三层图（:45-90）与 §1.4 normative 边界（:107）建立"proto 是法"的心智；再顺 §3（操作语义：幂等 :492-496、错误分类 :498-563、异步模型 :567、多轮 :580-645、更新机制 :646-705）与 §4（数据模型）走主干；§5 是绑定无关的横切约定速查区（方法映射 :1162、错误映射 :1180、命名 :1204、时间戳 ISO 8601 毫秒 UTC :1230-1237、字段存在性 :1257-1275）；用 §6 的九个示例验证理解；三个绑定章节按需查阅；§13 安全是上线前必读而非可选项。新人在 §3.4（contextId/taskId 语义 :584-645）与 §8.4（Agent Card 签名的 JCS 规范化 :2012-2165）最容易迷路，建议对照 topics 的 life-of-a-task 与 agent-discovery 两页（ONBOARDING.md ②）。

**v1.0 迁移三大坑**（whats-new 提炼，均有正文对照）：
1. **判别符换轨**：Part 与流事件的 `kind` 字段已删除，改为成员名判别（specification.md:3461-3556；whats-new:608-642）。解析器从 `part.kind === "text"` 改为 `"text" in part`，且服务端不得再输出 kind（:3544）。
2. **枚举值改写 + 时间戳精度**：`"completed"`→`"TASK_STATE_COMPLETED"`、`"user"`→`"ROLE_USER"`（whats-new:212-214、:736-747），timestamp 升为毫秒精度（whats-new:215）。字符串比较逻辑全部要改。
3. **AgentCard 结构重组**：`url`/`preferredTransport`/`protocolVersion` 顶层字段并入 `supportedInterfaces[]`（whats-new:378-418），`supportsExtendedAgentCard` 移入 `capabilities.extendedAgentCard`（specification.md:3558-3587）。取端点的代码从 `agentCard.url` 改为 `agentCard.supportedInterfaces[0].url`。
次级坑：HTTP 错误体从 RFC 9457 problem+json 换成 google.rpc.Status JSON（Content-Type 也从 `application/problem+json` 变 `application/json`，whats-new:754-762）；HTTP+JSON 路径删掉 `/v1` 前缀（whats-new:199）；OAuth 删 Implicit/Password 两流、增 Device Code（RFC 8628）与 PKCE 声明（whats-new:505-517）。

**与 SDK 文档的关系**：SDK 是 proto 的生成物（specification.md:107 明令 MUST 从 proto 重新生成），SDK 文档描述的是各语言对本文的封装——查"协议是什么"以本文与 proto 为准，查"怎么用"看 SDK；`json/a2a.json` 与 JSON Schema 是 non-normative 构建产物，手改无效（specification.md:119）。最后一个计数陷阱（**推断**+proto 事实）：人们常说"Task 九态"，proto 枚举确实有九个值（proto:187-207），但 TASK_STATE_UNSPECIFIED=0 是 proto 惯例占位，JSON 线上合法值是八个（specification.md:1614 的校验示例即为八值全集）——读文档时别数错。

---

*本篇为 explain 系列第 1 篇；第 2 篇起转向 proto 本体、主题文档群与教程线的逐文件精讲。*
