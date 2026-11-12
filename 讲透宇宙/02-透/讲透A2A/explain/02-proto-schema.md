# 02 · a2a.proto 精读：协议对象模型的 normative 源

> 目标文件：`/usr-data/data2/repos/aaif-projects/repos/A2A/specification/a2a.proto`（812 行，下文简写 proto）及其三份配套：`specification/buf.gen.yaml`（生成栈）、`specification/buf.yaml`（lint/breaking 栈）、`specification/.api-linter.yaml`（AIP 规则豁免栈）。specification.md §1.4 已声明 proto 是全部协议数据对象的唯一 normative 定义（详见 explain-01），本篇进入 proto 本体。文中行号锚均经 `grep -n` 对源文件逐条核实；git 考古结论标注提交号；无源可依处显式标（推断）。本仓知识图谱（批 12 产物，58 个 a2a.proto 相关节点）与本篇互为对照。

## 一、角色定位：812 行如何定义一个协议的全部对象

proto 开篇三行钉住技术底盘：`syntax = "proto3"`（proto:2，首行注释解释老编译器不认识 edition 语法）、`package lf.a2a.v1`（proto:3）、六个 import（proto:5-10）——google/api 三件套（annotations/client/field_behavior）换来 HTTP 注解与 REQUIRED 标注能力，protobuf 三件套（empty/struct/timestamp）换来通用类型。proto:12-16 的语言选项块是"一份定义、多语言分发"的声明：`csharp_namespace = "Lf.A2a.V1"`（proto:12）、`go_package = "google.golang.org/lf/a2a/v1"`（proto:13）、java 三选项（proto:14-16）。

全文件的量化身份：44 个 message、2 个 enum、11 个 RPC（`grep -c '^message\|^enum\|^  rpc'` 实测）。这 57 个声明分四族：①service A2AService（proto:19-140）11 个 RPC 构成协议操作面；②核心数据对象族（Task/Message/Part/Artifact 等）；③AgentCard 自描述族（含安全方案子族 10 个 message）；④请求/响应包装族（11 个 RPC 各配的 req/resp）。相比 v0.2 的 JSON Schema 手写定义，v1.0 把法源收拢到这 812 行——whats-new-v1.md:11 称之为从"gRPC 专用实现文件"升格为普适真源。

生成链的分工要澄清一处常见误读：**本仓 buf.gen.yaml 只配置了 4 门语言 7 个远端插件**——Python（buf.build/protocolbuffers/python:v29.3 + grpc/python，buf.gen.yaml:8-11）、Go（buf.gen.yaml:14-18）、Java（buf.gen.yaml:21-25）、TypeScript（community/stephenh-ts-proto:v1.165.0，buf.gen.yaml:28）；全用远端插件、零本地安装（buf.gen.yaml:3）。"五语言"的第五门是 C#：proto:12 的 csharp_namespace 只做了命名预留，本仓生成配置里没有 C# 插件（**推断**：.NET 类型生成在 a2a-dotnet SDK 仓内自行完成）；docs/sdk/index.md 的官方 SDK 表实际列了六门（Python/Go/Java/JS/C#/.NET/Rust），Rust 同样不在本仓 buf.gen.yaml 内。分发机制上，`.github/workflows/dispatch-a2a-update.yml` 监听 `specification/**` 路径（:7-8）变更即向 a2a-python 仓发 repository_dispatch（:16-21），触发下游重新拉取 proto 再生成——即"协议仓只管定义、SDK 仓各自消费"的松耦合。

## 二、内部结构：对象族谱与四个 oneof

**Task 族（proto:163-219）**：Task 是核心行动单元（proto:167），六字段——服务端生成的 id（proto:170，REQUIRED）、context_id 会话集合标识（proto:173）、必填 TaskStatus（proto:175）、artifacts 输出制品（proto:177）、history 多轮交互（proto:180，外包一对 protolint 注释 proto:178/181）、Struct metadata（proto:183）。TaskState 九值枚举（proto:187-208）：0 号位 TASK_STATE_UNSPECIFIED（proto:189）是 proto 惯例占位，JSON 线上合法值八个（explain-01 已钉此计数陷阱）；进行态 SUBMITTED/WORKING、终态四元 COMPLETED/FAILED/CANCELED/REJECTED（proto:194-205）、中断态 INPUT_REQUIRED=6（proto:201）与 AUTH_REQUIRED=8（proto:207）。TaskStatus 容器（proto:211）= state + message + ISO 8601 Timestamp（proto:218）。事件双胞胎：TaskStatusUpdateEvent（proto:296）与 TaskArtifactUpdateEvent（proto:308），后者带 append（proto:317，追加语义）与 last_chunk（proto:319，分块终结标记）两个流式专用 bool。

**Message/Part oneof 族（proto:221-293）**：Part 的载荷是全文件第一个 oneof——`oneof content { text=1 | raw=2 | url=3 | data=4 }`（proto:225-234），raw 在 JSON 序列化时转 base64（proto:228 注释），data 用 google.protobuf.Value 承载任意 JSON（proto:233）；公共属性 metadata/filename/media_type 挂在 oneof 之外（proto:236-241），media_type 注释明言"对所有 part 类型可用"（proto:240）。Role 枚举仅三值（proto:245-252）。Message（proto:260）是通信单元：message_id 创建方生成且 REQUIRED（proto:262）、role 与 parts 必填（proto:268/270）、extensions URI 列表（proto:274）与 reference_task_ids（proto:276）是 v1.0 新增的跨任务引用。Artifact（proto:280）与 Message 共享 Part 容器，artifact_id 任务内唯一（proto:282）。

**AgentCard 族（proto:334-467）**：AgentInterface（proto:336）四字段——url（HTTPS 或 hostname:port，proto:340）、protocol_binding 开放字符串（proto:344，官方核心支持 JSONRPC/GRPC/HTTP+JSON 三绑定）、tenant 路由标识（proto:351，设置后客户端 MUST 在所有请求回填）、protocol_version（proto:355）。AgentCard（proto:362）14 个字段，其中 supported_interfaces 有序列表（proto:371，首项即首选）、security_schemes 是 map<string, SecurityScheme>（proto:382）、signatures 是 JWS 签名数组（proto:396）、icon_url=14 是当前最大字段号（proto:398）。**"Next ID: 20" 注释（proto:361）是一个化石**：git 考古显示它诞生于 #1400 时代，当时 AgentCard 顶部有 `reserved 3, 9, 14, 15, 16;` 且 supported_interfaces=19/signatures=17/icon_url=18；#1494（1997c9d6，2026-02-17）删 reserved 并把字段号压实为 3/13/14，但 Next ID 标记忘改成 15——按该惯例的本义（防止删字段后误用旧号），当前有效值应为 15 而非 20。同族的 AgentCapabilities 四布尔/列表（proto:412-421）、AgentExtension（proto:424，URI+required 强制理解标记）、AgentSkill（proto:436，九字段含覆盖默认 IO 模式的 input_modes/output_modes proto:448-450）、AgentCardSignature（proto:457，RFC 7515 JWS 三件套 protected/signature/header）。

**transport 双通道 service（proto:19-140）**：11 个 RPC 按语义分三组。消息组：SendMessage（proto:21，POST /message:send）与 SendStreamingMessage（proto:33，POST /message:stream，**共用同一请求类型、返回 stream StreamResponse**）——这是"双通道"的实体：同一 message 入参，非流式返回 SendMessageResponse、流式返回事件流。任务组：GetTask（proto:45）/ListTasks（proto:55）/CancelTask（proto:64）/SubscribeToTask（proto:76，GET + stream 的罕见组合，对终态任务返回 UnsupportedOperationError proto:75）。推送配置 CRUD 组：Create/Get/List/Delete（proto:90/102/112/131）+ GetExtendedAgentCard（proto:122）。每个 RPC 的 google.api.http 注解都带 `additional_bindings` 双路径——裸路径与 `/{tenant}/...` 多租户路径成对（如 proto:25-28、:48-50）；CreateTaskPushNotificationConfig 直接拿资源型 TaskPushNotificationConfig 当请求（proto:90），上面挂着一段 api-linter 豁免注释（proto:85-88，"preserved for backwards compatibility"）。

## 三、外部连接：proto 在工具链与文档宇宙中的四个接口

**对 specification.md（宏消费）**：docs/specification.md 里 `proto_to_table` 宏调用 55 处（首处 :220 GetTaskRequest 表），外加 proto_enum_to_table 与 proto_service_to_table——§3/§4 的对象字段表全部是构建期从 proto 实时渲染，不存手工副本。三宏定义在 `.mkdocs/macros.py`：proto_to_table（macros.py:61）、proto_enum_to_table（:125）、proto_service_to_table（:147），默认 proto_file 参数即 'specification/a2a.proto'（:62）。宏的 `_extract_comments` 会过滤掉 protolint:/Next ID:/api-linter 前缀的注释行（macros.py:212-221）——所以 proto:361 的化石与 :85 的豁免注释不会泄漏进规范正文。字段表还能从 field_behavior 选项渲染出 Required 列（macros.py:304-308）， snake_case 自动转 camelCase 显示（macros.py:322）。与 explain-01 第三节的 16 组 message↔章节双锚表对照：本篇第二节给的就是同一批对象的 proto 侧行号。

**对 buf lint/breaking（buf.yaml）**：依赖仅 googleapis（buf.yaml:4）；lint 用 STANDARD+COMMENTS 双规则集（buf.yaml:9-10），豁免四条——PACKAGE_DIRECTORY_MATCH（lf.a2a.v1 与目录结构不匹配是有意的，buf.yaml:12）与三条 RPC 命名规则（buf.yaml:13-15，因请求名如 GetTaskPushNotificationConfigRequest 不符合 AIP 标准 *Request 命名）；breaking 检测用 FILE 级（buf.yaml:20）——**字段号变更、删字段、改类型都会被 CI 拦下**，这是字段号纪律的执法机构。

**对 api-linter（.api-linter.yaml）**：Google AIP 规则集的豁免清单，直接豁免 16 条（.api-linter.yaml:6-21，含 core::0140::abbreviations、core::0203::optional/required）+ 带 TODO 注释的技术性豁免 30 余条（:23-58，注释明言"Evaluate if the following should be enabled due to breaking changes"）——这份清单本身就是 A2A 偏离 Google API 设计规范的官方台账。CI 入口在 linter.yaml:31-63（buf-action v1.71.0 + api-linter v1.67.6，:42/:55）。protolint 是第四层：super-linter.env:14 开 VALIDATE_PROTOBUF、:22 指向 .github/linters/.protolint.yaml（仅移除 MAX_LINE_LENGTH 规则，.protolint.yaml:4），proto 里的 disable/enable 行内注释（proto:178/181/487/493）即为其而设。

**对 JSON Schema 工件**：scripts/proto_to_json_schema.sh 用 bufbuild/protoschema-plugins 的 protoc-gen-jsonschema（脚本内版本校验块）把 proto 转 JSON Schema 2020-12 bundle，生成前先 grep 剥离 protolint 注释行（脚本 Step 0），产出 a2a.json 被 specification/json/README.md:3 钉死为"non-normative build artifact，禁止手改"。

## 四、数据流：从 812 行定义到线上 JSON 的三条派生路径

**路径 A（SDK 类型）**：开发者跑 `buf generate`（specification/ 目录内），buf.gen.yaml 的 7 个远端插件把 a2a.proto 编译为四语言的 protobuf 消息类与 gRPC stub，落入 src/python、src/go、src/java、src/typescript 四个 out 目录（buf.gen.yaml:9/15/22/29）。协议主仓的变更经 dispatch-a2a-update.yml 推给 SDK 仓重生成（Python 通道已自动化，其余语言**推断**为各自 CI 定时或手动同步）。SDK 文档站再从这些类型生成参考页（docs/sdk/ 目录）。

**路径 B（线上 JSON，ADR-001）**：`adrs/adr-001-protojson-serialization.md`（2025-11-18，TSC 决议）选定 ProtoJSON 规范作为 JSON 序列化 normative 方案，理由是"标准方法+成熟多语言库+跨实现一致"；决议同时留下可逆条款——若发现重大问题可在规范内复制 ProtoJSON 约定。落到 proto 的三处可见后果：①字段 JSON 名全 camelCase（macros.py:322 的显示转换即预演）；②枚举线上值 = proto 定义的 SCREAMING_SNAKE_CASE 字符串（whats-new-v1.md:20）；③bytes 型 raw 序列化为 base64 字符串（proto:228 注释直接预告了这一行为）。

**路径 C（JSON Schema bundle）**：docs 构建（docs.yml:82-100，protoc 28.3 + protoc-gen-jsonschema + clone googleapis）跑 proto_to_json_schema.sh → clean_schema_names.py 剥 `.jsonschema.json` 后缀与 `lf.a2a.v1.` 包前缀（clean_schema_names.py:7-12）→ 捆绑为 docs/spec/a2a.json 发布。注意 protoc 版本双轨：buf.gen.yaml 的 python 插件钉 v29.3（buf.gen.yaml:8），docs 线用 protoc 28.3（docs.yml:86）——两代编译器并行是历史现状，非配置错误。

三路径的规范地位排序：proto（normative）> SDK 类型（生成物）> a2a.json（non-normative 工件）——specification/json/README.md:3 与 explain-01 引用的 §1.4 声明完全一致。

## 五、设计决策：三组从 git 考古读出的取舍

**1. field number 稳定性纪律与其化石。** proto 的字段号一旦发布即不可复用——buf.yaml:20 的 FILE 级 breaking 检测是执法者，git 史里有两段实证。正向示范：#1400 时代 AgentCard 删除五个字段后用 `reserved 3, 9, 14, 15, 16` 防误用（配合 Next ID: 20 提示下一个安全号）； SendMessageConfiguration 的 `blocking = 4` 改名 `return_immediately = 4`（#1507，601c408a，2026-03-10）**保号改名**、极性反转留给 JSON 语义层。反向化石：ListTaskPushNotificationConfigsRequest 里 tenant 声明在首位却拿字段号 4（proto:761），task_id=1/page_size=2/page_token=3（proto:763/766/769）——溯源是 2026-02-17 同日双提交竞态：#1486（cf735cb8，12 时段合入）先把消息改名复数形，#1494（1997c9d6，14 时段合入）统一把 8 个消息的 tenant 压到 1 号位，却漏了这个刚改名的第 9 个消息（其 diff 中该消息零命中）。此后 v1.0 冻结破坏性变更，错位成为永久兼容化石（知识图谱批 12 已捕获：ListTaskPushNotificationConfigsRequest 节点 summary 原文"tenant 字段号 4……系历史兼容"）。"漏掉是疏忽而非设计"为（推断）——两个提交的 diff 证据只能证明遗漏事实。

**2. oneof vs optional 的分工。** 全文件四个 oneof 各司其职：Part.content（proto:225）做内容多态判别（v1.0 删 kind 字段后成员名即判别符，specification.md:3491）；SecurityScheme.scheme（proto:505）复刻 OpenAPI 3.2 Security Scheme Object 的 discriminated union（proto:502-503 注释自认）；OAuthFlows.flow（proto:569）五选一并把 implicit=3/password=4 标 `[deprecated = true]`（proto:575/577，注释指路 Authorization Code + PKCE 或 Device Code）；SendMessageResponse.payload 与 StreamResponse.payload（proto:782/793）做返回多态——后者四成员 task/message/status_update/artifact_update 是流式与 push 通道共享的事件全集。而 proto3 的 `optional` 只用在标量存在性敏感处：history_length（proto:154/672）、page_size（proto:688）等分页/截断参数——注释强调"未设=不限、设 0=一条都不要"三态（proto:151-153），裸 int32 无 presence 区分不了前两态，这是 optional 存在的全部理由。

**3. enum SCREAMING_SNAKE_CASE 迁移。** whats-new-v1.md:20 记录 v1.0 Breaking 变更"枚举值从 kebab-case 改 SCREAMING_SNAKE_CASE 以合规 ProtoJSON"；:212 与 :249 分别钉 TaskState（TASK_STATE_ 前缀）与 Role（ROLE_ 前缀）两个迁移点。proto 侧的呼应是 proto:189-207/247-251 的命名本身与 0 号位 UNSPECIFIED 占位——proto3 枚举必须从 0 起且首个值惯例为 *_UNSPECIFIED，这直接催生了"九值枚举、线上八值"的计数口径（explain-01 已钉）。迁移动因（对齐 ProtoJSON、避免小写枚举在多语言 SDK 里命名冲突）在 whats-new 有明文；更细的"为何不是 PascalCase"层（推断） proto/whats-new 均无论述。

## 六、新人提示

**加一个字段的合规流程（五步）**：①在 proto 里选字段号——先查该 message 现有最大号与是否残留 Next ID 注释（AgentCard 的 Next ID: 20 已过时，实际安全号是 15，proto:361 化石勿信），绝不复用已删号，AgentCard 族曾有 reserved 3,9,14,15,16 的先例；②注释写清语义并区分 MUST/SHOULD（字段注释会被 macros.py 直接渲染进规范正文）；③过三道 lint——buf lint（STANDARD+COMMENTS，buf.yaml:9-10）、api-linter（新字段可能撞豁免清单外的 AIP 规则）、protolint（复数命名规则 REPEATED_FIELD_NAMES_PLURALIZED，history 那对注释 proto:178/181 是绕行示范）；④`buf generate` 同步四语言产物；⑤检查 a2a.json 是否需重建（非 normative 但 SDK 生态消费它）。字段号一经发布不可改——tenant=4 化石就是改不动的前车之鉴。

**buf 工具链命令速查**：生成 `cd specification && buf generate`（依赖 buf.yaml:4 的 googleapis，先 `buf dep update`）；本地 lint `buf lint`；破坏性检查 `buf breaking --against '.git#branch=main'`；api-linter 单跑参照 linter.yaml:63 的完整命令行（需先 `buf export buf.build/googleapis/googleapis --output=.googleapis`）。

**三个坑**：①**别手改 a2a.json**——它是构建产物（specification/json/README.md:3 "Do NOT edit"），改 proto 后由 build_docs.sh:33-39 再生；②**读 AgentCard 字段号别信 Next ID**——20 是 #1494 压号前的旧值，当前最大 14（proto:398），下一个安全号 15（此条按 Next ID 惯例本义（推断））；③**CreateTaskPushNotificationConfig 的请求即资源**（proto:90）——它不像其他 RPC 用独立 Request 消息，且带着 api-linter 豁免注释（proto:85-88），照抄这个模式给新 RPC 会被 AIP 规则打回。另有一个无害化石别误删：proto:385 的 `protolint:enable` 在 AgentCard 内没有配对 disable（#1400 时代即如此），protolint 对多余 enable 静默忽略，但若有人"顺手补对称"删掉它，得确认不影响 proto:487-493 的 StringList 区块。

---

*本篇为 explain 系列第 2 篇（对象模型与生成栈）；第 1 篇 specification.md 叙事主线见 01-specification-deepread.md，两篇行号锚可互相换算（§4 章节锚 ↔ 本篇 proto 声明锚）。*
