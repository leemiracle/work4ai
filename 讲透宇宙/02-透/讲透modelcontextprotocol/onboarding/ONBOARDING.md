# Model Context Protocol（MCP）规范仓 Onboarding

本仓是 MCP（Model Context Protocol）的**规范官方仓**（github.com/modelcontextprotocol）：协议规范正文、TypeScript 权威 schema、Mintlify 文档站、SEP 提案树、官方博客与治理文件全部同仓演进，由 Agentic AI Foundation（AAIF，LF Projects 系列）托管。本图谱基于 commit `80041ab0a139a8f4fb3adbc99f7ae9113ea59671`（2026-10-20），共 **633 节点 / 1800 边 / 14 层 / 15 步 tour**，覆盖 573 个可分析文件（docs 365 个 mdx 规范与指南、seps 45、schema 16、blog 64、tools 31）。一句话定位：**一个协议、六代快照、一套生成链**——读任何文件之前，先问它属于哪一代、是源还是产物。

## ① 这个项目是什么 / 为什么存在

MCP 是给 AI 应用连接外部系统的开放标准，官方指南的比喻是"AI 应用的 USB-C"（docs/docs/2025-11-25/getting-started/intro.mdx:10）。2024 年之前，每个 AI 应用接每个数据源都要定制集成，N 个应用 × M 个系统就是 N×M 的组合爆炸；MCP 把"应用 ↔ 上下文/工具"的接口标准化，让服务器一次实现、处处可用。协议 2024-11-05 由 Anthropic 发布，2025-12 加入 Agentic AI Foundation（blog/content/posts/2025-12-09-mcp-joins-agentic-ai-foundation.md），治理框架依 GOVERNANCE.md:3 归 LF Projects, LLC，代码与规范贡献走 Apache-2.0（GOVERNANCE.md:7），文档（除规范外）走 CC-BY-4.0（GOVERNANCE.md:11）。两位 Lead Maintainer David Soria Parra 与 Den Delimarsky 署名维护（blog/content/posts/2026-07-28-spec-ga/index.md:7 起 author 节），名录详见 MAINTAINERS.md:7。

这个仓不是某个 SDK 的实现仓——TypeScript/Python 等 SDK 各有独立仓库，本仓只负责**规范本身的单一事实源**：README.md:11 明言 schema 先以 TypeScript 定义、再编译为 JSON Schema 供更广生态消费；仓库同时托管规范正文（docs/specification/ 六代全量快照）、开发者文档站（docs/docs/，Mintlify，配置 docs/docs.json:33 起按版本分列导航，共 1453 行）、SEP 提案（seps/ 45 个 .md）与官方博客（blog/，Hugo，26 篇正文）。

理解本仓的第一透镜是**版本代际**：规范六版本（2024-11-05 → 2025-03-26 → 2025-06-18 → 2025-11-25 → 2026-07-28 → draft）每版都完整保留全量目录快照，"改规范"实际是在新目录里长出新的一代，旧版永不覆写——AGENTS.md:45-46 把 released 与 in-progress（schema/draft 与 docs/specification/draft）分列就是这条原则的书面化。第二透镜是**源与产物的严格二分**：schema.ts 是源、schema.json 与 schema.mdx 是产物；seps/*.md 是源、docs/seps/*.mdx 是产物——CI 会机械地保证两边零漂移。抓住这两点，全仓 573 个文件就不再是一盘散沙。

## ② 全景架构：14 层地图

| 层 | 名 | 文件数 | 职责 |
|---|---|---|---|
| L01 | 规范主线·奠基期双版本 | 37 | 2024-11-05 首版（三角色+三原语）与 2025-03-26（OAuth 2.1+Streamable HTTP），一切 diff 的对照基线 |
| L02 | 规范主线·安全与表达力扩展期 | 43 | 2025-06-18（elicitation+schema 立真源）与 2025-11-25（tasks），会话式有状态协议的终态 |
| L03 | 规范主线·GA 无状态转向 | 62 | 2026-07-28 首个 GA 版 + draft 镜像，全仓最大范式转折层 |
| L04 | 用户指南镜像·四代稳定版 | 64 | docs/docs/ 下四版同构教程（getting-started/learn/develop/tools/tutorials） |
| L05 | 用户指南镜像·GA 与草案 | 52 | 2026-07-28/draft 两版指南，inspector 十页手册爆发 |
| L06 | 扩展体系与官方 Registry | 20 | extensions/ 九页（Apps/Skills/Tasks/auth+兼容矩阵）+ registry/ 十一篇 |
| L07 | SEP 提案·根目录源树 | 46 | seps/*.md 决策原始记录（SEP-414 至 2667 全编号） |
| L08 | SEP 提案·站点渲染树 | 44 | docs/seps/*.mdx 渲染产物，与 L07 构成源→产物双树 |
| L09 | JSON Schema 六版本契约 | 16 | schema/&lt;v&gt;/ 六目录，schema.ts 真源 + schema.json 产物 |
| L10 | SEP 生命周期自动化机器人 | 31 | tools/sep-automation GitHub App（TS+Octokit，含 8 测试文件） |
| L11 | 官方博客（Hugo 站） | 64 | blog/ 26 篇正文+PaperMod 主题定制，发布第一手叙事 |
| L12 | 社区治理与工作组生态 | 44 | 根目录治理纲领 + docs/community（14 个 WG + 8 个 IG） |
| L13 | CI/CD 与工程基建 | 30 | .github 13 条 workflow + 工具链配置 + 代理指令 |
| L14 | 构建生成链与文档站点装配 | 20 | scripts 五脚本 + typedoc 配置 + 站点资产 + plugins 技能插件 |

骨架逻辑一句话：**L01-L03 是纵向时间轴（规范正文六代），L09 是它的 schema 投影，L04-L05 是它的指南投影，L07-L08+L10 是它的决策记录与自动化，L06 是核心之外的生长点，L11-L13 是组织与机械土壤，L14 把一切黏成可发布整体**。

三个重点层展开。**L01 奠基层**是所有版本 diff 的原点：2024-11-05 版确立 JSON-RPC 2.0 骨架与 Host/Client/Server 三角色，单独成页的 messages.mdx 为该版独有（次版并入 basic/index）；2025-03-26 首开 changelog.mdx 版本账本并引入授权与 Streamable HTTP。**L03 GA 层**是本仓最大叙事发生地：62 个文件里包含范式转折的全部现场——协议面重构（basic/）、目录大重排（utilities 并入 patterns、authorization 拆四页、transports 分目录）、deprecated.mdx 废弃注册表，以及与 GA 版逐字镜像的 draft 目录。**L09 schema 层**是唯一"文件少而杠杆最大"的层：16 个文件定义六版协议契约，interface 数从 66 一路涨到 128，方言从 draft-07 切到 2020-12——规范语义的最硬表达全在这里。

## ③ 核心抽象

**JSON-RPC 2.0 消息骨架**。全协议建立在 JSON-RPC 2.0 之上（docs/specification/2024-11-05/basic/messages.mdx:8），Request/Response/Notification 三形态，请求 id 不得为 null、也不得与在途请求重复（同文件 :27）。GA 版把"结果"升级为多态：result MUST 携带 `resultType` 字段（docs/specification/2026-07-28/basic/index.mdx:73），取值 `complete`（终态成功）与 `input_required`（还需输入，:81-82），客户端不认识的取值 MUST 视为无效（:84），缺席则按 `complete` 兼容旧版（:85）。错误码 -32000~-32099 分区管理：-32000~-32019 是 legacy 禁新增（:114/:117），规范保留段含 -32020 HeaderMismatch、-32022 UnsupportedProtocolVersion（:133/:135）——读 GA 版任何报错先查这张分区表。

**三原语与三层控制**。服务端三大特性按"谁控制"分层：Prompts 用户控制（斜杠命令/菜单）、Resources 应用控制（附加上下文数据）、Tools 模型控制（让 LLM 采取行动）（docs/specification/2024-11-05/server/index.mdx:19-21），配 Host/Client/Server 三角色（docs/specification/2024-11-05/architecture/index.mdx:46/:57——Host 是入口应用、Client 为每个 Server 造连接）。这组概念分工从首版延续至今未变，是读所有六版的通用词汇表；GA 版的变化只在传输与协商层，原语语义基本稳定。

**版本代际：stateful → stateless**。2025-11-25 及以前是"会话式有状态"：initialize 握手 → 运行 → 关闭三段式生命周期（docs/specification/2025-11-25/basic/lifecycle.mdx:21-23 时序图），握手交换 protocolVersion+capabilities+clientInfo（:47 起），HTTP 传输用 Mcp-Session-Id 会话头维持连接。2026-07-28 GA 整体推翻：删 initialize 握手（docs/specification/2026-07-28/changelog.mdx:14）、删协议级会话与 Mcp-Session-Id（同文件 :12）、删 ping 与 logging/setLevel（:20），能力协商改为**逐请求** `_meta` 携带 io.modelcontextprotocol/protocolVersion 与 clientCapabilities（docs/specification/2026-07-28/basic/versioning.mdx:44；HTTP 上走 MCP-Protocol-Version header :46），版本不符回 -32022 驱动客户端选版重试。服务器发起请求（elicitation/sampling/roots）被 **MRTR**（Multi Round-Trip Requests，SEP-2322）取代：服务器不再"反向呼叫"客户端，而是对 tools/call 等请求直接回 `InputRequiredResult`（docs/specification/2026-07-28/basic/patterns/mrtr.mdx:124），携带服务端不透明 requestState（:130，客户端 MUST NOT 解析其内容），客户端收集 inputResponses 后**用新 id 重试原请求**（:184-186 列出可用的三类请求）——服务端全程零状态，这是无状态化的最后一块拼图。配套新增必选 `server/discover`（docs/specification/2026-07-28/server/discover.mdx:7-8，服务器 MUST 实现以广播版本/能力/身份）。

**SEP 提案机制**。重大变更必须走 SEP（Specification Enhancement Proposal，docs/community/sep-guidelines.mdx:8）——它是征集社区意见与记录设计决策的首要机制（:10），以 markdown 形式维护在 seps/ 目录（:14）。状态机 proposal→draft→in-review→accepted→final/dormant 六态（tools/sep-automation/src/types.ts:6），新提案从 seps/TEMPLATE.md:1 的模板起步（Abstract/Motivation/Specification/Rationale 等八节，:12 起），升 Final 前必须有完整参考实现与一致性测试（:77）。GA 转向的每条 breaking change 都能溯源：无状态化=SEP-2575（seps/2575-stateless-mcp.md:3 Status Final，Abstract 开宗明义"真正无状态、每请求自包含"，:11 起）、MRTR=SEP-2322（seps/2322-MRTR.md:3）。

**扩展体系**。核心协议刻意收窄，能力生长走扩展：标识符格式 `{vendor-prefix}/{extension-name}`，官方用 io.modelcontextprotocol/ 前缀、第三方须用自有反向域名防冲突（docs/extensions/overview.mdx:10）；客户端在每请求 `_meta` 的 io.modelcontextprotocol/clientCapabilities 里声明支持哪些扩展（:137）。扩展分 modular/specialized/experimental 三类，实验扩展经 SEP Extensions Track（SEP-2133）毕业为官方（docs/extensions/overview.mdx:91/:95-97）。三大官方扩展各有重料：**Apps**（对话内交互 HTML，为什么不用独立 web app——上下文保留+双向数据流+沙箱安全，docs/extensions/apps/overview.mdx:24/:37，机制四步走 _meta.ui.resourceUri 预加载+:71 的 sandboxed iframe 渲染）；**Skills over MCP**（skill:// URI 指向 SKILL.md 与配套文件，:112，完整文件清单挂 Resources 原语，docs/extensions/skills/overview.mdx:143）；**Tasks**（长时操作的异步任务句柄，2026-07-28 从核心移入扩展 io.modelcontextprotocol/tasks，docs/specification/2026-07-28/changelog.mdx:22）。

## ④ 一次规范演进的旅程（15 步 tour）

按图谱 tour 顺序串讲，60 分钟走完协议两年：

**T01 门面**：README → docs/docs.json 导航树 → AGENTS.md，建立"三件套同仓"的地图感。**T02 奠基 2024-11-05**：architecture 页三角色、server/index 三层控制、lifecycle 的 initialize 握手（docs/specification/2024-11-05/basic/lifecycle.mdx:47 客户端 MUST 发 initialize）、messages.mdx 的 JSON-RPC 骨架；对照 schema/2024-11-05/schema.ts（:5 定义 LATEST_PROTOCOL_VERSION="2024-11-05"，66 个 interface）建立 diff 基线。**T03 2025-03-26**：OAuth 2.1 整体纳入——基于 OAuth 2.1 IETF Draft+RFC8414 授权服务器元数据+RFC7591 动态客户端注册的三标准精选子集（docs/specification/2025-03-26/basic/authorization.mdx:29-33），实现 MUST 支持 OAuth 2.1（:39）；HTTP+SSE 换轨 Streamable HTTP（docs/specification/2025-03-26/changelog.mdx:13），另加 JSON-RPC batching（同文件 :16）——"换轨不弃旧"的向后兼容叙事从这版开始成为传统。**T04 中期终态**：2025-06-18 新增 elicitation（服务器经客户端向用户征集结构化输入，elicitation/create 请求，docs/specification/2025-06-18/client/elicitation.mdx:59），schema 刻意限平铺基元以降低客户端实现成本（:199）；2025-11-25 的 Tasks 是最重实验原语——两阶段响应（接受即回 CreateTaskResult，结果稍后经 tasks/result 取，docs/specification/2025-11-25/basic/utilities/tasks.mdx:123-126）+ 请求方轮询直到终态（:195），页首明确标注 experimental（:9）。到此为止的 initialize 握手、会话头、服务器发起请求，都将在下一步被整体推翻——记住这张终态快照。

**T05-T06 GA 无状态转向（全仓最大叙事）**：2026-07-28 把 MCP 从双向有状态协议改为请求/响应无状态协议（blog/content/posts/2026-07-28-spec-ga/index.md:22，同文 :6 的 description 一句话列尽全部新特性）。changelog（docs/specification/2026-07-28/changelog.mdx）九条 major 逐条记账：删会话（:12）、删握手（:14）、新增 server/discover（:16）、删 ping/setLevel（:20）、tasks 移出核心（:22）、MRTR 引入（:24）。Streamable HTTP 传输页 Info 块明示四项 breaking（docs/specification/2026-07-28/basic/transports/streamable-http.mdx:19-20：移除 GET 流端点与协议级会话；:685 对带 Mcp-Session-Id 头的请求直接忽略不回显）；subscriptions/listen 长活通知流取代旧订阅 RPC（docs/specification/2026-07-28/basic/patterns/subscriptions.mdx:7）；deprecated.mdx 登记废弃特性——Roots/Sampling/Logging/Dynamic Client Registration 四项自 2026-07-28 起废弃，最早移除窗口均为 2027-07-28 后首个修订版（docs/specification/2026-07-28/deprecated.mdx:26-29），至少 12 个月的废弃缓冲是生态友好的硬承诺。draft/ 目录与 GA 版文件集完全一致、仅真源链接指向 schema/draft，是下一版的滚动工作副本。**T07 schema 六版本**：interface 数 66→68→76→120→128（2025-11-25 史上最大扩容 +44），2026-07-28 与 draft 完全一致（128+27 type）；方言代际与规范代际精确同步（见⑥）。**T08-T09 指南镜像**：规范讲 MUST/SHOULD，指南讲如何上手——四代同构 learning funnel（intro 的 USB-C 定位 → architecture 概念地图 → build-server 双语言实战，其中 STDIO 服务器禁写 stdout 的铁律在 docs/docs/2025-11-25/develop/build-server.mdx:48 与 :369 两处 Python/Node 双语重申 → debugging/inspector 工具 → sdk 分层）。GA 版指南爆发 inspector 十页：protocol-eras 讲 legacy/modern 协议纪元（docs/docs/2026-07-28/tools/inspector/protocol-eras.mdx:6，:14-15 明确 legacy 是默认、auto 才探测 server/discover——调试工具为何不默认 auto 的答案在这里）；mcpdo 是 ssh-agent 式常驻连接客户端（docs/docs/2026-07-28/tools/inspector/mcpdo.mdx:6，daemon 名叫 mcpdod、按需启动 :14）——协议换轨直接催生了调试工具链重写。

**T10-T11 扩展与 Registry**：client-matrix 是 14 客户端×四扩展的支持矩阵（docs/extensions/client-matrix.mdx:35 起的表），生态现实的诚实快照——MCP Apps 覆盖最广、Skills 多为 Partial。Registry 定位关键：只存元数据不存代码（docs/registry/quickstart.mdx:15），server.json 把 server 名映射到 npm/PyPI/Docker 包（docs/registry/about.mdx:19/:38），既是创作者的发布处（:14）也是客户端与聚合器的 REST 发现接口（:16），主要消费者是下游市场类聚合器（:50）；发布走 mcp-publisher CLI，mcpName 必须以 io.github.用户名/ 反向 DNS 前缀开头（docs/registry/quickstart.mdx:63）——命名空间即信任模型。**T12-T13 SEP 双树与机器人**：根 seps/ 是源、docs/seps/ 是产物，规范正文是结果、SEP 树是过程；sep-automation（tools/sep-automation/package.json:2）的 rules.ts 是生命周期单一事实源——proposal 无 sponsor 90 天 ping、180 天休眠（tools/sep-automation/src/rules.ts:78/:83-84），processor.ts 编排自动迁移/失活分析/维护者问责三段流水线（tools/sep-automation/src/processor.ts:50 SEPProcessor 类），types.ts 定义贯穿全流程的数据载体 SEPItem（:15）与七种 ActionType（:42）。**T14-T15 机械层与收尾**：生成链与 CI 见⑥；镜头拉远看组织土壤——WG 与 IG 双轨（IG 讨论问题、WG 交付方案，决策走 lazy consensus→投票→升级，docs/community/working-interest-groups.mdx:6/:17），transports/registry/sdk 等 14 个工作组正是各规范特性的孵化器；roadmap 给出未来 6-12 个月方向：Agentic Messaging 原语（docs/development/roadmap.mdx:26，把 Tasks/subscriptions/progress 统一进共享生命周期，:30）、HTTP-Native 传输统一与加固（:39，含 HTTP over stdio 的 HTTP/2 方案 :47）、Agent Identity 与企业安全（:52，DPoP/Workload Identity Federation/ID-JAG :60-61）——这些正是 draft 镜像的未来内容。

## ⑤ 目录导航

- **docs/specification/&lt;v&gt;/**：规范正文六代全量快照。读当前版从 2026-07-28/index.mdx 入；看演进读各版 changelog.mdx；每版内 basic（消息/生命周期/传输/授权/版本）/ server（tools/resources/prompts/discover）/ client / basic/patterns（GA 版起）分节。
- **docs/docs/&lt;v&gt;/**：同六代的开发者指南镜像（Mintlify 站正文），getting-started/learn/develop/tools/tutorials/sdk 六段式，面向上手而非规范语言；两个版本树文件名与规范树同名仅目录不同，搜索时注意区分。
- **seps/**：SEP 提案**源树**（45 个 .md，含 TEMPLATE.md 模板与 README 外链指针）。**改提案只动这里**；历史源树由 migrate_seps.js:3-5 从 GitHub issues 一次性迁移而来。
- **docs/seps/**：SEP 站点渲染**产物**（44 个 .mdx），由 render-seps.ts 生成并自动提交，勿手改。
- **schema/&lt;v&gt;/**：schema.ts（真源，唯一可手改）+ schema.json（编译产物）+ schema.mdx（typedoc 页面模板，见⑦坑）+ examples/（JSON 夹具；AGENTS.md:60-64 约定目录名=类型名、文件经 @includeCode 引用回 schema.ts）。
- **scripts/**：五脚本——generate-schemas.ts（编译六版 schema）、render-seps.ts（渲染 SEP 并回写 docs.json 导航，scripts/render-seps.ts:314 起构建分组导航）、validate-examples.ts（校验夹具）、check-mdx-comments.ts（校验 mdx 内 JS 注释）、pull-registry-docs.sh（同步 Registry 文档）。
- **tools/sep-automation/**：SEP 生命周期 GitHub App，src 下 actions/（transition/ping 等）、sep/（analyzer/detector 解析 front-matter）、hooks/（discord 通知）、github/、maintainers/、rules.ts 规则引擎分包清晰，test/ 含 8 个测试文件。
- **blog/**：Hugo 站，content/posts/ 26 篇（2025-07 治理公告至 2026-08 路线图），layouts 为 PaperMod 主题定制，hugo.toml 开启 JSON 输出供客户端搜索。
- **plugins/mcp-spec/**：Claude Code 技能插件（plugins/mcp-spec/.claude-plugin/plugin.json:2），含 search-mcp-github（检索历史决策）与 draft-sep（起草提案）两技能。
- **根目录**：AGENTS.md（仓库结构+贡献命令+AI 协作规则，CLAUDE.md 是其符号链接）、AI_POLICY.md:13（用 AI 辅助贡献必须披露）、GOVERNANCE/MAINTAINERS/CONTRIBUTING/SECURITY 等治理纲领、package.json（generate/check/prep 命令入口）。

## ⑥ 构建·生成·质量体系

全仓核心纪律：**schema.ts 是唯一真源，一切产物必须可再生成且零漂移**（AGENTS.md:50-56——改 schema/[version]/schema.ts 后跑 npm run generate:schema 同时刷新 schema.json 与 Schema Reference 文档，"Always regenerate after editing schema files" 是明文铁律）。

- **generate 链**（package.json:24-27）：`generate` = generate:schema + generate:seps。schema 又分两路并行：generate:schema:json 调 scripts/generate-schemas.ts 把六版 schema.ts 编译为 schema.json；generate:schema:md 对每版以 schema/&lt;v&gt;/schema.mdx 为**页面模板**、同名 schema.ts 为入口跑 typedoc，产物落到 docs/specification/&lt;v&gt;/schema.mdx（package.json:27 的重定向语法可证模板与产物的方向）。generate:seps 调 scripts/render-seps.ts，读 seps/*.md 生成 docs/seps/*.mdx 并**回写 docs.json 的 SEPs 导航标签**（scripts/render-seps.ts:10/:25）。
- **check 链**（package.json:32-35）：四层 schema 检查——check:schema:ts（tsc --noEmit+eslint+prettier）→ check:schema:json（generate-schemas --check 重算比对）→ check:schema:examples（validate-examples.ts，scripts/validate-examples.ts:50 起遍历 examples 目录逐夹具验证）→ check:schema:md（typedoc 重渲染后 cmp 逐字节比对产物）；另有 check:docs（格式/JS 注释/死链三查）与 check:seps（SEP 渲染是否最新）。
- **prep**（package.json:45）：提交前一条命令全量跑"检查真源 → 生成 → 再检查文档与 SEP → 格式化"；AGENTS.md:78-94 给贡献者的命令速查就是这套。
- **方言代际**：scripts/generate-schemas.ts:11-12 定义 LEGACY_SCHEMAS（前三版保持 JSON Schema draft-07），:14-15 定义 MODERN_SCHEMAS（2025-11-25/2026-07-28/draft 用 2020-12），:30-31 对现代版做 dialect 字符串正则变换——SEP-1613/2106"立 2020-12 为默认方言"的决策直接落在编译器里，产物头部 $schema 行即可验证两代方言。
- **13 条 workflow**：main.yml 是主门禁（.github/workflows/main.yml:24-31 依次跑 schema ts/json/md 三查，防真源与产物漂移）；render-seps.yml 在 PR 上 verify、push main 时重渲染并自动提交（.github/workflows/render-seps.yml:37-43）；sep-lifecycle.yml 每周一 09:00 UTC 定时驱动 SEP 机器人（.github/workflows/sep-lifecycle.yml:12）；另有 cut-release/publish-release 双发布流、deploy-blog/stage-blog/blog-preview 三博客流、markdown-format、labeler、sep-reminder、sep-lifecycle-manual、slash-commands。
- **站点辅助**：docs/version-warning.js 在旧版与 draft 页面挂"非最新版"横幅（:12 定义 DRAFT_VERSION），依赖站内 /specification/latest 重定向，发新版无需改脚本。

## ⑦ 深水区预警（图谱勘误与坑）

1. **schema.ts 不用 zod**。六版 schema.ts 全部是纯 TypeScript interface/type（2026-07-28 版 128 interface+27 type，全文零 import 零运行时代码），编译走 typescript-json-schema 体系。按"TS schema 惯例必 zod"的直觉猜是错的。
2. **schema/&lt;v&gt;/schema.mdx 是模板不是产物**。它只含标题骨架与 {/* @category */} 注释，作为 typedoc 的 --schemaPageTemplate 输入；真正的 Schema Reference 产物在 docs/specification/&lt;v&gt;/schema.mdx。两处同名异义，读文档读错目录会以为内容缺失。
3. **SEP 双树勿混淆**：seps/*.md 是源（45 个），docs/seps/*.mdx 是产物（44 个）——数量本就不等，评审与 diff 以源树为准；产物由 CI 自动维护，手改会被下次渲染覆盖。
4. **labeler.yml 双文件两角色**：.github/labeler.yml 是 actions/labeler 的**配置**（:5 起按 blog/**、docs/docs/** 等路径打标签），.github/workflows/labeler.yml 是触发 PR 自动打标的 **workflow**——同名字不同物，搜索时两处都会命中。
5. **draft 与 GA 完全镜像**：schema/draft/schema.ts 与 2026-07-28 版接口集逐字一致，且 LATEST_PROTOCOL_VERSION 仍指 "2026-07-28"（schema/draft/schema.ts:30）——draft 不代表"更超前"，只是下一版工作副本；规范正文 draft 目录同理，diff 通常只剩站内链接路径。
6. **examples/ 夹具是校验资产**：schema/&lt;v&gt;/examples/ 下 258 个 JSON 全部被 validate-examples.ts 消费，改类型定义必须同步夹具，否则 check:schema:examples 红。
7. **图谱工程坑**（来自本图谱批分析台账 PROGRESS.md）：scanner 对 mdx 间相对链接大多为空，本图谱的 imports 边由子代理逐文件重扫补齐；258 个 examples 夹具在图谱分析前已 ignore（均 12.5 行/个，无图谱语义）——图谱里 schema 层只有 16 个真文件节点。
8. **AI 贡献有披露红线**：AGENTS.md 对非 MAINTAINERS 名单维护者（或合并 PR<3 者）用 AI 代开 issue 设限，AI_POLICY.md:13 要求在 PR/issue 中声明 AI 辅助及程度——拿本仓练手 agentic 流程前先读这两份，别踩社区政策。
9. **messages.mdx 只存在于首版**：找 JSON-RPC 消息骨架的现行版本应读 basic/index.mdx（2025-03-26 起并入），按旧教程路径找会 404。
10. **两个 docs 树同名易混**：docs/specification/&lt;v&gt;/（规范语言）与 docs/docs/&lt;v&gt;/（开发者指南）版本号同名、部分文件名也同名（如各有 architecture/lifecycle 页），搜索定位时必须先确认自己在哪棵树——一条经验法则：讲 MUST/SHOULD 的是规范树，讲 how-to 与代码示例的是指南树。

## ⑧ 上手路线：3 天计划

**Day 1 读规范主线（建立时间轴直觉）**：上午从 docs/specification/2026-07-28/index.mdx 读 GA 版全部五节，重点精读 basic/index.mdx 的 resultType 多态与错误码分区、basic/versioning.mdx 的无握手协商、server/discover.mdx；下午回读 2024-11-05 版三页（architecture/server index/messages）建立词汇表，再浏览 2025-11-25/basic/lifecycle.mdx 看被推翻前的会话式终态，最后把 2026-07-28/changelog.mdx 的九条 major 与 deprecated.mdx 对照通读——形成"stateful→stateless"的完整对照。练习：不看资料写出 initialize 握手被什么机制取代。

**Day 2 摸 schema 与生成链（吃透真源纪律）**：上午通读 schema/2026-07-28/schema.ts 全文（128 interface 半天可完成，注意 io.modelcontextprotocol/ 前缀的 _meta 键族），对照产物 docs/specification/2026-07-28/schema.mdx 理解 @category 分组；下午读 scripts/generate-schemas.ts 弄清 LEGACY/MODERN 方言分代，本地跑 `npm run generate` 观察三路产物刷新，再跑 `npm run check` 看门禁如何逐层比对；最后读 AGENTS.md 全文记住"改 ts 必再生成"铁律与 examples/ 约定。练习：给某个 interface 加一个字段，验证哪些检查会拦住不同步的产物。

**Day 3 走治理与生态（接入贡献流程）**：上午从 seps/TEMPLATE.md 与 docs/community/sep-guidelines.mdx 学提案格式与八步工作流，精读 SEP-2575 与 SEP-2322 两个 Final 范本（正好对应 Day 1 的两大范式变更），浏览 tools/sep-automation/src/rules.ts 理解六态迁移与失活阈值如何自动化；下午读 docs/extensions/overview.mdx 与 client-matrix.mdx 理解扩展治理，docs/registry/about.mdx 理解元数据注册中心，收尾读 blog GA 公告（2026-07-28-spec-ga/index.md）与 docs/development/roadmap.mdx 对齐未来 6-12 个月方向。至此规范、schema、指南、SEP、机器人五条线全部闭合，你对本仓的理解将从"六百多个文件"收敛为"一个协议的六代快照加一套生成链"；之后可到 issue 区认领第一个 good first issue，或按 TEMPLATE 起草第一个提案——记得先读 AI 披露政策。

---

> 锚 68 处 / 汉字 4108（统计口径：正则 `[一-鿿]` 计汉字；`路径.扩展名:行号` 计锚，全部经仓内源文件逐个核实，文件存在性与行号界内自动校验通过）
