# A2A 协议仓新人 Onboarding（Agent2Agent Protocol）

> 基于知识图谱（183 节点 / 352 边 / 8 层 / 8 步 tour，commit `98279d6`）与原仓源码逐行核实编写；文中所有 `路径:行号` 锚均已程序化对源码验证。仓址 a2aproject/A2A，本地 `/usr-data/data2/repos/aaif-projects/repos/A2A`。

## ① 这个项目是什么 / 为什么存在

A2A（Agent2Agent）是让异构 AI agent 互相发现能力、协商交互方式并协作完成任务的开放协议。它解决的核心痛点（`docs/topics/what-is-a2a.md` 以国际旅行规划场景演绎）：agent 能力无法被外部发现、每个组合都要定制集成、框架间互操作缺失、长任务缺乏异步协作机制、企业安全与治理诉求没有统一抓手等六大类。五项设计原则贯穿全协议：简单（对象模型尽量少）、企业就绪（认证授权与可观测开箱即用）、异步优先（长任务不必挂连接）、模态无关（不预设文本/音频/视频）、**不透明执行**——协作方只交换任务与制品，不暴露内部状态、记忆与推理过程。在 agent 技术栈的四层定位里，A2A 与底层模型、中间的 agent 开发框架、面向工具接入的 MCP 都不抢位置，它专管最上面一层：跨框架、跨组织的 agent 之间横向连线。

治理沿革一句话讲清：项目由 Google 发起，现已捐赠给 Linux Foundation。`docs/llms.txt:3` 自述 "originated by Google and donated to the Linux Foundation"；官方博客 `docs/blog/posts/a2a-joins-aaif.md`（2026-08-27）记录其被 Agentic AI Foundation（AAIF）接纳为 Growth Stage 项目，与 MCP、goose、AGENTS.md 并列为兄弟项目，中性治理避免了单厂商锁定；`mkdocs.yml:6` 的 site_author 已是 The Linux Foundation。与 MCP 的关系是**互补而非竞争**：MCP 垂直深耕单 agent 的工具接入，A2A 水平连接跨组织边界的 agent（`docs/topics/a2a-and-mcp.md`，规范附录 B `docs/specification.md:3627`）。

**新人第一认知：本仓是协议的"规范本体仓"，只定协议、不做实现。** `docs/specification.md:107`（§1.4 Normative Content）白纸黑字：`spec/a2a.proto` 是所有协议数据对象与请求/响应消息的**唯一权威 normative 定义**；构建期生成的 JSON 工件是非规范产物；六语言官方 SDK（Python/Go/Java/JS/.NET/Rust）全部住在独立外部仓（清单见 `docs/sdk/index.md`）。实现类问题别来这个仓找代码——这里除了文档站工程脚本，几乎没有可运行的产品代码。

治理与版本：九席技术指导委员会（Google/Microsoft/Cisco/AWS/Salesforce/ServiceNow/SAP/IBM/Bloomberg 各一席，`GOVERNANCE.md:3`）负责协议、SDK 与文档的全部技术监督；TSC 决策过半数出席为法定人数、多数决（`GOVERNANCE.md:71`），投票成员六周未到会按 LFX 考勤除名（`GOVERNANCE.md:73`）。版本线：v1.0.0 于 2026-03-12 发布（`CHANGELOG.md:12`，公告 `docs/blog/posts/announcing-1.0.md`——企业级能力、Web 对齐架构、与 MCP 互补定位），当前 1.0.1（2026-05-26，`CHANGELOG.md:3`）；v0.3→v1.0 的全部破坏性变更（如核心操作改名、Part 类型统一被列为 CRITICAL 级）沉淀在 `docs/whats-new-v1.md`（975 行迁移指南）。

## ② 全景架构：8 层地图

| 层 | 名字 | 内容 | 文件数 |
|---|---|---|---|
| L01 | 协议规范本体 | `specification/a2a.proto` + `docs/specification.md`（3639 行 14 章）+ whats-new-v1 + buf/buf.gen/api-linter 配置 + JSON Schema 产物管线 | 64 |
| L02 | 概念与主题文档 | `docs/topics/` 12 页：what-is-a2a、key-concepts、life-of-a-task、a2a-and-mcp、agent-discovery、streaming-and-async、enterprise-ready、multi-tenancy、extensions 三篇 + `docs/definitions.md` 术语表 | 12 |
| L03 | Python 教程线 | `docs/tutorials/python/` 8 步 Quickstart（导言→环境→Skill/Card→Executor→启动→客户端→流式多轮→后续路径） | 9 |
| L04 | SDK 文档与官方公告 | SDK 总览 + Python SDK Sphinx 文档（`docs/sdk/python/conf.py`）+ 博客三篇（1.0 发布 / 加入 AAIF / A2A CLI） | 8 |
| L05 | 文档站构建与站点资产 | `mkdocs.yml` + `.mkdocs/`（macros 宏与主题覆盖模板）+ `scripts/` 六个构建脚本 + 主页 / 404 / robots / sitemap / llms 三件套 | 38 |
| L06 | 治理与社区 | GOVERNANCE / MAINTAINERS / CONTRIBUTING / CODE_OF_CONDUCT / SECURITY + `.gitvote.yml` + `adrs/` + community / partners（约 180 家）/ roadmap | 18 |
| L07 | CI 与 lint 体系 | 11 条 GitHub Actions workflow + 6 份 linter 配置 + 本地等价 format.sh / lint.sh / sort_spelling.sh | 28 |
| L08 | 开发环境与杂项 | devcontainer 三件套 + `.gemini/config.yaml` + `.gitattributes` / `.git-blame-ignore-revs` | 6 |

依赖方向一眼看穿：**L01 是唯一源头**——概念文档（L02）解释它，教程（L03）演示它，JSON Schema 与站点规范页（L05）从它派生，外部 SDK 实现它；L05 与 L07 是把 L01-L04 发布成 a2a-protocol.org 站点的工程设施；L06 定规矩；L08 是锦上添花。新人改动的九成落在 L01-L03，但读懂 L05/L07 才不会在 CI 门禁上撞墙。各层的"门面文件"值得先认脸：L01 是 `specification/a2a.proto`，L05 是 `mkdocs.yml`（nav 树在 `mkdocs.yml:21` 起），L07 是 `.github/workflows/docs.yml`，L06 是 `GOVERNANCE.md`。

L02 的 12 页主题文档是"规范正文的分层复读"：入门走 what-is-a2a 与 key-concepts；进阶三篇 life-of-a-task（状态机）、streaming-and-async（双通道）、agent-discovery（三种发现途径）；企业落地看 enterprise-ready（传输安全/认证/授权/合规/可观测/网关六大支柱）与 multi-tenancy（子路径/认证头/请求体 tenant 字段三种路由）；扩展生态看 extensions 三篇（机制、自定义绑定、统一治理）。读完 L02 再啃 3639 行规范正文，效率高一个量级。

## ③ 核心抽象：a2a.proto 的协议对象主线

812 行 proto（package `lf.a2a.v1` 于 `specification/a2a.proto:3`）定义 `A2AService`（`specification/a2a.proto:19`）的 **11 个 RPC、44 个 message、2 个 enum**（数量已逐一清点核实）。五条主线：

1. **AgentCard——发现机制核心**（`specification/a2a.proto:362`）：name/description/supported_interfaces/version/capabilities/skills 必填，注释保留 Next ID: 20 的字段号管理约定。其中 `AgentInterface`（`specification/a2a.proto:336`）声明接入端点四要素：url（HTTP 传输生产环境必须是绝对 HTTPS，gRPC 则为 hostname:port）、protocol_binding 开放字符串（官方核心值 JSONRPC/GRPC/HTTP+JSON）、tenant 多租户路由字段（设置后客户端必须在所有请求回填）、protocol_version；同一 agent 可按有序列表暴露多个绑定，首项为首选。`AgentSkill`（`specification/a2a.proto:436`）是能力描述单元，input/output_modes 可覆盖 agent 级默认值。卡片签名走 RFC 8785 JCS 规范化 + RFC 7515 JWS（规范 §8.4，`docs/specification.md:2012`）。
2. **Task——有状态行动单元**（`specification/a2a.proto:167`）：服务端生成的 id、context_id（会话分组标识，同一上下文可跨多个任务复用）、必填 TaskStatus（`specification/a2a.proto:211` = TaskState + 关联 Message + ISO 8601 时间戳）、artifacts 输出制品集、history 多轮历史、metadata 自定义键值。九态生命周期枚举 TaskState（`specification/a2a.proto:187`）：进行态 SUBMITTED/WORKING、终态 COMPLETED/FAILED/CANCELED/REJECTED、中断态 INPUT_REQUIRED/AUTH_REQUIRED（等待用户输入或认证）——"进行/终/中断"三分法是理解所有 SDK 行为的钥匙。任务查询（GetTask `specification/a2a.proto:45`）、列表（ListTasks）、取消（CancelTask `specification/a2a.proto:64`）均围绕它展开。
3. **Message 与 Part 多态**（`specification/a2a.proto:260` / `specification/a2a.proto:224`）：Message 必填 role（`Role` 枚举在 `specification/a2a.proto:245`：ROLE_USER 客户端→服务端、ROLE_AGENT 反向）与至少一个 Part；context_id/task_id 可选但同给时必须匹配。Part 用 oneof 承载 text / raw（JSON 序列化为 base64）/ url / data（google.protobuf.Value 任意 JSON）四种载荷，metadata/filename/media_type 三公共字段对全部 Part 类型可用——这一个类型撑起了模态无关原则。
4. **流式 update 事件**：TaskStatusUpdateEvent（`specification/a2a.proto:296`）= task_id + context_id + 新 TaskStatus；TaskArtifactUpdateEvent（`specification/a2a.proto:308`）携带 Artifact 且 append=true 追加同 ID 旧制品、last_chunk=true 标记末块，支撑大制品分块流式下发；StreamResponse（`specification/a2a.proto:791`）oneof 四载荷：task / message / status_update / artifact_update。
5. **transport 双通道**：每个 RPC 均带 google.api.http 注解——SendMessage 于 `specification/a2a.proto:23` 映射 `post: "/message:send"`，`specification/a2a.proto:25` 的 additional_bindings 加 `/{tenant}/message:send` 多租户路径。这是三大标准绑定（JSON-RPC §9 `docs/specification.md:2260`、gRPC §10 `docs/specification.md:2536`、HTTP+JSON/REST §11 `docs/specification.md:2772`）、绑定等价性要求（§5 `docs/specification.md:1143`）与自定义绑定指南（§12 `docs/specification.md:3004`）的 proto 侧地基。

## ④ 一条消息的生命周期

按 specification.md 章节顺序，走一遍客户端 sendMessage 的完整旅程：

1. **发现**：客户端从 `/.well-known/agent-card.json`（RFC 8615 标准路径）拉取 AgentCard；三种发现途径（well-known 标准路径 / 策展注册表目录 / 直接配置私有发现）与敏感信息保护（认证扩展卡、mTLS、注册表选择性披露）见 `docs/topics/agent-discovery.md`；HTTP 缓存走 Cache-Control + ETag 条件请求（§8.6，`docs/specification.md:2244`）。卡片里的 capabilities（`specification/a2a.proto:412`）决定后续走法：streaming 与 push_notifications 是两个开关，extended_agent_card 提示还有认证后的扩展卡（GetExtendedAgentCard，`specification/a2a.proto:122`）。
2. **认证与发请求**：身份认证走 HTTP 头、不进协议载荷（§7 `docs/specification.md:1871`）；随后调 SendMessage（同步，`specification/a2a.proto:21`）或 SendStreamingMessage（流式，`specification/a2a.proto:33`）。请求配置对象在 §3.2（`docs/specification.md:430`）——accepted_output_modes 声明客户端可接受的响应媒体类型、history_length 历史条数上限、return_immediately=true 时建任务即返回不等终态。
3. **两条返回路径**（`docs/topics/key-concepts.md:90` "Agent Response: Task or Message"）：无状态 agent 直接回 Message（message-only 形态）；有状态 agent 建 Task 进入状态机（task-generating / hybrid 形态辨析见 `docs/topics/life-of-a-task.md:32`）。
4. **状态机流转**：SUBMITTED→WORKING→终态；多轮交互（§3.4，`docs/specification.md:580`）携带 taskId/contextId 续任务；INPUT_REQUIRED 中断等待用户输入（LangGraph 实例见教程 `docs/tutorials/python/7-streaming-and-multiturn.md`）；任务终态不可变、不可重启（`docs/topics/life-of-a-task.md:77` Task Immutability）。
5. **事件流**：流式场景（§6.2，`docs/specification.md:1349`）经 SSE 订阅，StreamResponse 四类流事件（§4.2 `docs/specification.md:814`）按序下发，大制品靠 append/last_chunk 分块重组；断线后经 SubscribeToTask（`specification/a2a.proto:76`）重订。
6. **push notification**：长任务或弱客户端（移动端/serverless）场景——§3.5（`docs/specification.md:646`）定义轮询/流式/推送三种更新机制。客户端先用推送配置 CRUD 五个 RPC（`specification/a2a.proto:90` 起，`TaskPushNotificationConfig` 消息在 `specification/a2a.proto:470`）注册 webhook；服务端在显著状态变更（终态 / input-required / auth-required）时向 webhook POST 一个 StreamResponse 载荷（`docs/topics/streaming-and-async.md:55`）；客户端验证后再 GetTask（`specification/a2a.proto:45`）拉全量任务（§6.6 全流程示例 `docs/specification.md:1620`）。

## ⑤ 目录导航

| 你想做的事 | 去处 | 提交类型（`CONTRIBUTING.md:82`-`84`） |
|---|---|---|
| 改协议（字段/枚举/RPC/注释） | `specification/a2a.proto` | `feat:` / `fix:`（禁 spec scope） |
| 改人读规范正文 | `docs/specification.md` | `docs(spec):` |
| 改概念/主题页 | `docs/topics/*.md` | `docs:` |
| 写教程 | `docs/tutorials/python/`（8 步线） | `docs:` |
| 改文档站构建 | `mkdocs.yml` + `.mkdocs/` + `scripts/` | `chore:` / `ci:` |
| 改 CI/lint | `.github/workflows/` + `.github/linters/` | `ci:` |
| 记录架构决策 | `adrs/`（按 `adrs/adr-template.md` 起草） | — |
| SDK 使用问题 | 外部仓 a2a-python 等（本仓只有跳转页） | — |

两个易错点：其一，规范正文与 proto 常需联动——`CONTRIBUTING.md:85` 的 TIP 明说文档改动若影响协议语义，连 proto 注释一起改，以触发新协议版本发布；其二，`adrs/` 在 docs/ 之外，由构建脚本末尾拷进 `site/adrs`（`scripts/build_docs.sh:87`），不要试图挪进 docs/。想先看协议全貌的机器可读版：`docs/definitions.md` 用 content tabs 提供 Protobuf / JSON 双视图，`docs/llms-reference.txt` 是非规范性速查。

## ⑥ 构建·文档·lint 体系

**构建链**（统一入口 `scripts/build_docs.sh`，98 行）：
- `regen_needed()`（`scripts/build_docs.sh:16`）对比 a2a.proto 与 json/a2a.json 的 mtime，过期才调 `scripts/proto_to_json_schema.sh` 重生成；后者校验 protoc / bufbuild 版 protoc-gen-jsonschema / jq 三依赖并甄别插件实现版本串（`scripts/proto_to_json_schema.sh:26`），多级回退定位 googleapis 注解路径（GOOGLEAPIS_DIR 环境变量，`scripts/proto_to_json_schema.sh:48`）。
- schema 与 proto 拷进 `docs/spec/` 供 MkDocs 引用（`scripts/build_docs.sh:46`），级联 `scripts/build_sdk_docs.sh`（uv 建 .doc-venv → 从 PyPI 装 a2a-sdk → sphinx-apidoc 自动生成 API 参考的 html 与 text 双版本），最后按 deploy 参数分派 `mike deploy` 或 `mkdocs build`（`scripts/build_docs.sh:76`）。
- 文档站配置 `mkdocs.yml`：Material 主题 + mike 版本化（`mkdocs.yml:128`，canonical_version latest 在 `mkdocs.yml:204`）+ macros 插件挂载 `.mkdocs/macros.py`（`mkdocs.yml:170`）——`proto_to_table` / `proto_enum_to_table` / `proto_service_to_table` 三宏（`.mkdocs/macros.py:61` / `:125` / `:147`）用 proto_schema_parser 直接解析 a2a.proto 渲染 GitHub 风格字段表进文档，**改 proto 后文档表格自动跟上**。
- llms 三件套：`docs/llms.txt`（curated 索引，`:10` 标注 normative proto、`:11` 标注 non-normative JSON Schema）与 `docs/llms-reference.txt` **手工维护**；llms-full.txt 由 `scripts/build_llms_full.sh` 生成**勿手编**（以 llms.txt 为 curated index，`scripts/build_llms_full.sh:37`；末尾并入 a2a.proto 全文，`scripts/build_llms_full.sh:121`）。

**CI**：`.github/workflows/docs.yml` 是唯一部署 pipeline——装 Python 3.13 / uv / Buf 1.71.0 / Go 1.25 工具链后跑 build_docs.sh（`.github/workflows/docs.yml:103`）与 build_llms_full.sh（`:106`）；PR 只 `mkdocs build` 校验（`:110`），push main 部署 dev+latest 双别名并设默认版本（`:115` 附近），release 按标签版本化部署。`.github/workflows/linter.yaml` 双 job：super-linter slim@v8 全仓检查（`:27`，22 条环境变量经 `:24` 注入 GITHUB_ENV）+ api-linter v1.67.6 按 AIP 规则查 proto（`:55`，A2A 用 `.api-linter.yaml` 禁用了 50 余条规则给自有 REST 风格绑定让路）。lint 配置三件事记住就行：markdownlint 显式关 MD013 行长/MD033 内联 HTML 等（`.github/linters/.markdownlint.json:3` 起）、protolint 仅豁免 MAX_LINE_LENGTH（`.github/linters/.protolint.yaml:4`，正为 proto 里的长 URL 行而设）、lychee 链接检查 6 并发 30 秒超时（`lychee.toml:5`/`:8`）。拼写检查由 check-spelling 拉取 30+ 部 cspell 远程字典，白名单 `.github/actions/spelling/allow.txt` 收录 420 词，顺序由脚本自动维护。本地等价入口：`scripts/lint.sh`（docker 跑与 CI 同款镜像）、`scripts/format.sh`（markdownlint --fix + 拼写白名单排序）——PR 前必跑这两条，可免九成 CI 打回。

**环境一键化选项**：不想手装 protoc/Go/Buf 工具链，可用 devcontainer（`.devcontainer/devcontainer.json` 基于 ubuntu 基镜像 features 装 Python 3.12/Go/Node，postCreateCommand 调 `.devcontainer/setup.sh` 装 protoc v28.3 与 protoc-gen-jsonschema 并克隆 googleapis 到 third_party/），VS Code 与 GitHub Codespaces 两种打开方式均支持；依赖清单另见 `requirements-docs.txt`（mkdocs-material/redirects/macros/mike + sphinx/furo/myst-parser + a2a-sdk 与 proto-schema-parser/tabulate）。

**跨仓联动**：main 上 `specification/**` 有 push 时，`.github/workflows/dispatch-a2a-update.yml`（paths 过滤 `:8`）向 a2a-python 发 a2a_json_update 事件（`:21`）驱动下游 SDK 同步 JSON 规范——**改 proto 的影响从来不止本仓**。

## ⑦ 深水区预警

1. **`docs/spec/` 在仓里不存在**（ls 可实证）：它是 `scripts/build_docs.sh:46` mkdir+cp 的本地构建产物。clone 后跳过 build_docs.sh 直接 mkdocs build，可能因缺 a2a.json 而失败——标准路径是先跑 `./scripts/build_docs.sh`（`CONTRIBUTING.md:47`）再 `mkdocs serve`（`CONTRIBUTING.md:54`）。
2. **json/a2a.json 是 non-normative 构建产物且不入库**：`specification/json/README.md:3` 与 `docs/specification.md:107` 双重钉版，`specification/json/README.md:18` 明令 "Do NOT edit manually. Update the proto instead"——任何"改 JSON Schema"的念头都应改成改 proto。
3. **知识图谱口径：绝对 URL 不入图**：本图谱只建仓内相对链接边。`docs/tutorials/index.md:7` 的 Python Quickstart 是该页唯一相对链接入口，其余 13 条教程全是 a2a-samples / a2a-dotnet 外部 GitHub 链接、在图中零出边——"教程页没有出边"不是内容缺失，是图谱口径。
4. **legacy redirect 五分页合并史**：`mkdocs.yml:174`-`178` 记录旧 `specification/` 下 overview.md / agent-card.md / agent-to-agent-communication.md / sample-messages.md / details.md 五页全部 redirect 进 specification.md 对应锚点——早期规范曾是五篇分页，v1 收敛为单页长文。全仓共 30 条 redirect_maps（`mkdocs.yml:172`）+ `docs/root-redirects/` 静态重定向目录 + `docs/404.html` 客户端兜底三层机制，动任何 URL 前先查这三处。
5. **提交规范是 CI 门禁不是建议**：conventional-commits 工作流按 paths-filter 区分三类改动分别校验 PR 标题——只改 specification.md 必须 `docs(spec):`，改 a2a.proto 用 `feat:/fix:` 且禁 spec scope（与 `CONTRIBUTING.md:82`-`84` 对应），release-please 据此自动发版，错标题直接被拦。
6. **MD041 抑制指令别顺手清理**：`README.md:40` 与 `docs/index.md:7` 各有一条 `<!-- markdownlint-disable MD041 -->`（首行非顶级的豁免），删了 CI 立红。
7. **站点版本号来自环境变量**：`mkdocs.yml:15` 的 a2a_version 由 MIKE_VERSION 注入、本地预览恒为 "dev"——不是 bug。
8. **扩展与绑定是两个正交概念**：Extensions 改行为不改传输（A2A-Extensions 头三步协商激活，`docs/topics/extensions.md:171`，示例值 `:198`）；Custom Bindings 换传输不改行为（WebSockets/MQTT 等）。新人最易混，两者还各有独立治理流程（`docs/topics/extension-and-binding-governance.md`）。

## ⑧ 上手路线：2 天计划

**Day 1 协议本体（tour step 1-4）**
- 上午：读 `docs/topics/what-is-a2a.md`（六大痛点 / 五项原则 / 四层技术栈定位）+ `docs/topics/key-concepts.md`（三类角色 `:9`、五大通信元素 `:23`）；对照通读 a2a.proto 的 11 个 RPC 与 ③ 的五条对象主线；skim `docs/specification.md` §1-§4（`:13` / `:147` / `:766`），重点 §1.4 normative 边界（`:105`）。
- 下午：跑 Python 教程 1-7——重点 `docs/tutorials/python/4-agent-executor.md`（五步事件流：建任务→WORKING→业务逻辑→artifact_update→COMPLETED）与 `docs/tutorials/python/6-interact-with-server.md`（含期望的流式四块事件输出）；再读 `docs/topics/life-of-a-task.md` 与 `docs/topics/streaming-and-async.md` 补齐状态机与双通道；有余力看 `docs/topics/a2a-and-mcp.md`（汽车修理厂场景讲透垂直 vs 水平分工）。
- Day 1 自测：能白板画出"发现→认证→sendMessage→Task 九态→事件流→push notification"全链图。

**Day 2 工程设施（tour step 5-8）**
- 上午：按 `CONTRIBUTING.md:11`（Python 3.10+ / uv / Node / Docker）装环境，`./scripts/build_docs.sh` 起构建、`mkdocs serve` 预览；读 `mkdocs.yml` 的 nav 树与 redirect_maps、`.mkdocs/macros.py` 三宏；跑一遍 `scripts/lint.sh` 与 `scripts/format.sh` 亲身感受门禁。
- 下午：读 `.github/workflows/docs.yml` 与 `.github/workflows/linter.yaml` 两条工作流 + dispatch 跨仓联动；读 `GOVERNANCE.md` 与 `adrs/adr-001-protojson-serialization.md`（ProtoJSON 选型 `:32`、枚举值改 SCREAMING_SNAKE_CASE 的破坏性影响 `:52`——理解 A2A 的 JSON 序列化为何长这样）；最后扫 devcontainer 三件套（`.devcontainer/devcontainer.json:15` postCreateCommand、`:30` 转发 8000 端口）与 `.gitattributes:2`（docs/ 与 .mkdocs/ 标记 linguist-documentation 不计语言统计）。
- 出师三问：a2a.json 能手改吗（不能，`specification/json/README.md:18`）；`docs/spec/` 为什么不存在（构建产物，`scripts/build_docs.sh:46`）；`feat:` 与 `docs(spec):` 各留给谁（a2a.proto / specification.md，`CONTRIBUTING.md:82`-`84`）。全答对，即可去 `docs/roadmap.md` 挑一个近期倡议（v1.1 协议增强、双向流、A2A CLI 集成、Elicitation 多轮）领任务。想参与协议演进，先读 `docs/topics/extension-and-binding-governance.md` 了解扩展与绑定从提案到毕业的五阶段流程，再从修文档小错起步攒信用——本仓的 PR 一律需要评审，TSC 成员也不例外。
