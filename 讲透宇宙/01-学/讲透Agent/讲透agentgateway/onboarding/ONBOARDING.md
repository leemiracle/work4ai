# agentgateway 新人 Onboarding（K8s 原生 AI agent 流量网关）

> 依据：understand-anything 图谱（commit `f51a7fb`，7792 节点/19479 边/16 层/16 步 tour）+ 原仓源码逐条核实。所有 `文件:行号` 锚均已在源码验证。

## ① 这个项目是什么 / 为什么存在

agentgateway 自我定位是 "The **first complete** connectivity solution for Agentic AI"（README.md:33）：一个构建在 AI 原生协议（MCP 与 A2A）之上的开源代理，为 agent-to-LLM、agent-to-tool、agent-to-agent 三类流量提供 drop-in 的安全、可观测与治理能力（README.md:36-40 的 Key Features 三段：LLM Gateway / MCP Gateway / A2A Gateway）。

它要补的缺口值得先想清楚：传统 API 网关（Envoy/APISIX/NGINX）不懂 MCP 会话语义、不懂 LLM 协议差异、更不懂 prompt 级策略；而 LangChain 之类框架自带的 LLM 网关又不管 K8s 生态、mTLS、凭据轮换这些基础设施层能力。agentgateway 的答案是把两边接起来——用基础设施圈成熟的 Gateway API/xDS/策略引擎语言，去治理 AI 圈的新协议流量。

治理归属：**Linux Foundation 项目**（README.md:130-131），法律形态是 LF Projects, LLC 旗下的 Series（CHARTER.md:1,5）。使命见 CHARTER.md §1a——为 AI agent 发现、连接外部工具与服务建立安全、可扩展的标准基座。注意：本仓与本地图谱所属的 aaif-projects 采集目录无任何组织关联，仓内零 AAIF 字样（全仓 grep 实证），归属以 README/CHARTER 为准。

技术形态是**双面架构**，这是理解全仓的第一把钥匙：

- **Go 控制面（`controller/`）**：K8s controller，实现 Gateway API 语义。它依赖 istio 框架的 krt 声明式集合（go.mod:55）与 envoy go-control-plane 的 xDS 类型（go.mod:16），负责把用户声明的 CRD 翻译成数据面配置并部署网关实例。
- **Rust 数据面（`crates/`）**：**自研代理，不是 Envoy**。它消费 xDS 协议、兼容 Envoy 生态的 ext_authz/ext_proc 外部集成协议（crates/agentgateway/src/http/envoy_proto_common.rs:12-15 直接引用 `protos::envoy::service::common::v3` 生成代码），但流量路径完全是 Rust 实现，底座 crate 带 ztunnel 血统（如 crates/core 的批量 nonblocking 日志）。MCP 支持基于官方 Rust SDK `rmcp 3.1.0`（crates/agentgateway/Cargo.toml:125）。

为什么"消费 xDS 但不用 Envoy"？因为数据面要在应用层做协议翻译（LLM 互译、MCP 中继），这需要完全掌控请求体与流式帧，Envoy 的 C++/WASM 扩展模型在这里性价比不高；而 xDS 作为控制协议足够标准化，可以复用 istio 圈成熟的下发基础设施。**协议兼容 Envoy、实现自立门户**是贯穿数据面的设计基调。

双运行形态（README.md:73-81）：**Standalone**——单二进制 + 平面 YAML 配置，`./target/release/agentgateway` 直接跑，浏览器开 `http://localhost:15000/ui` 进管理界面（DEVELOPMENT.md「Run the agentgateway binary」节），15000 这个端口来自 wellknown 常量（controller/pkg/wellknown/ports.go 钉死 ProxyAdminPort=15000，控制器自身 admin 端口则是 9095）；**Kubernetes**——内置 controller + Gateway API + Helm 全链路，默认 GatewayClass 名就叫 `agentgateway`（wellknown/controller.go:7）。两形态共享同一个 Rust 数据面与同一套策略语义，standalone 的 YAML 本质上是控制面翻译产物的手写版。

## ② 全景架构：16 层地图

| 层 | 是什么 | 关键文件锚 |
|---|---|---|
| L01 门面与工程配置 | 治理文档、Cargo workspace（16 成员）、Makefile、buf | Cargo.toml、Makefile:68、schema/config.json |
| L02 API 契约层 | 四种 CRD 类型 + CEL 校验 + ext_mcp protobuf 契约 | controller/api/v1alpha1/agentgateway/、api/ext_mcp.pb.go |
| L03 翻译与策略引擎 | K8s 语义→xDS IR 的翻译大脑 | plugins/traffic_plugin.go（2519 行）、translator/conversion.go（1927 行） |
| L04 控制面心脏 | reconciler 装配、Helm deployer、syncer→xDS 推送 | controller/pkg/controller/gw_controller.go、pkg/syncer/syncer.go |
| L05 支撑库与 agctl | wellknown 常量、凭据/状态汇报、agctl CLI | controller/pkg/wellknown/agw.go、pkg/cli/ |
| L06 e2e 测试体系 | kind 真集群 e2e + gomega 匹配器 + conformance | controller/test/e2e/、test/conformance/conformance_test.go |
| L07 Rust 数据面骨架 | 配置模型/热更新/代理生命周期/store/遥测 | crates/agentgateway/src/lib.rs:158（RawConfig）、:694（Config） |
| L08 HTTP 过滤器矩阵 | 31 个过滤器子模块：认证/授权/限流/重试/转换 | crates/agentgateway/src/http/mod.rs:1-34 |
| L09 MCP 网关与配置类型 | 招牌能力：MCP 会话中继、多上游聚合 | crates/agentgateway/src/mcp/、src/types/agent.rs |
| L10 CEL 表达式栈 | cel-fork 解释器 + celx 扩展函数 + 策略求值 | crates/cel-fork/cel/src/lib.rs:194、crates/celx/src/general.rs:20 |
| L11 LLM Provider 翻译引擎 | 七类 provider 协议全方向互译（含 SSE 逐帧） | crates/llm/src/lib.rs:11-23、conversion/bedrock.rs（4658 行） |
| L12 金样本夹具库 | 173 个 JSON 夹具驱动 insta 快照回归 | crates/llm/src/tests/、golden_tests.rs:54 |
| L13 数据面集成测试 | proxymock 全家桶：MemoryConnector 零网络组装拓扑 | crates/agentgateway/src/test_helpers/proxymock.rs:120 |
| L14 Rust 基础 crate | core/http/pool/hbone/xds/protos 公共底座 | crates/xds/src/client.rs、crates/core/src/strng.rs |
| L15 React 管理界面 | Models/Playground/McpServers/Logs 等页面 | ui/src/pages/Models.tsx:105、Logs.tsx（2951 行） |
| L16 交付与 CI | 三套 Helm chart、多阶段 Dockerfile、工具版本锚定 | controller/install/、Dockerfile:59、tools/exec-go-tool |

逐层展开几句关键的：L02 的 CRD 类型面是整个系统的"公共语言"——控制面翻译、UI 表单、CEL 校验、文档示例全部锚定在这组类型上，改一个字段会波及四处；L03 的 traffic_plugin.go 是策略引擎里最大的一块（2519 行），AgentgatewayPolicy 的 traffic 段几乎全由它消化；L07 的 lib.rs 同时是配置模型与模块清单的所在地，是数据面导航的起点；L08 与 L09 的关系是"通用 HTTP 能力"与"AI 协议能力"的分界——过滤器矩阵不关心协议语义，MCP/LLM 模块才做协议级翻译；L10 的 CEL 栈被两侧同时依赖，是最不该轻易动的底座；L11 的翻译引擎与 L12 的金样本是"实现与事实标准"的配对，改翻译必须过金样本这关。

阅读心法：**L02 契约 → L03 翻译 → L04 下发 → L07-L11 执行**是主链，按这个顺序读能始终知道"我在看的代码在整条链路的哪一环"。L05/L06/L12-L16 都是围绕主链的支撑与验证层。另一个隐性分界：Go 侧（L02-L06）与 Rust 侧（L07-L14）唯一的耦合面是 xDS protobuf（api/resource.pb.go ↔ crates/protos/proto/resource.proto 是同一契约的两端生成物），跨语言改动要两头同步；根目录的 buf.gen.yaml 是 proto→Go 侧的生成入口，Rust 侧由 crates/protos 的 build.rs 承担。

## ③ 核心抽象

**CRD 四类型**（全部在 controller/api/v1alpha1/agentgateway/，用户视角的四个名词）：

- **AgentgatewayBackend（短名 agbe）**：后端定义。Spec 以 `ExactlyOneOf=ai;static;dynamicForwardProxy;mcp;aws;a2a` 六选一（agentgateway_backend_types.go:55，struct 定义 :58）——这个"六选一"是全系统路由分派的根：ai 线进 LLM 翻译引擎，mcp 线进 MCP 网关，a2a 线进 A2A 代理。AI 线内嵌 LLMProvider 全家桶，provider 枚举 `openai;azureopenai;azure;anthropic;gemini;vertexai;bedrock;custom;copilot`（:215）；A2A 后端类型在 :136。
- **AgentgatewayModel（agmodel）**：模型路由层。以 `match.model` 匹配客户端请求里的模型名，spec 在具体 provider 与 virtualModel 二选一（agentgateway_model_types.go:58；VirtualModel :302 支持加权/故障转移/条件三种路由策略——这与 UI 的 Models.tsx:105 一一对应）。
- **AgentgatewayParameters（agpar）**：GatewayClass 级数据面供给参数——工作负载类型（Deployment/DaemonSet）、容器镜像、Istio/SPIFFE 集成等（agentgateway_parameters_types.go:53）。
- **AgentgatewayPolicy（agpol）**：巨型策略面，3682 行（wc -l 实证），struct :29、Spec :74 分 targetRefs/targetSelectors 加 traffic/frontend/backend 三段，覆盖认证/授权/限流/转换/遥测几乎全部策略 schema。AI 专属策略单列在 ai_policy.go：promptEnrichment（前后缀消息注入）:40、AIPromptGuard（内置正则/webhook/OpenAI Moderation/Bedrock Guardrails 的请求响应防护与脱敏）:415。

配套生成物勿手改：zz_generated.deepcopy.go 有 447 个 DeepCopy 函数（grep 实证）、zz_generated.register.go 注册四组 CRD 进 scheme。CEL 授权语义在 rbac.go——Allow/Require/Deny 三态，Deny 不推荐使用。overlay_types.go 定义 Strategic Merge Patch 覆盖生成的 K8s 资源，文档钉死 GatewayClass→Gateway 四步应用顺序。

**翻译层 IR**：translator/conversion.go（1927 行）把 HTTP/TCP/GRPC/TLS 路由规则转成 agw Route 并处理 parentRef 准入（:762 起，含端口与 Service parent 校验）。插件骨架不是 Go 惯见的 interface，而是 krt 集合构建器的 struct——`PolicyPlugin{Build, BuildReferences}`（controller/pkg/agentgateway/plugins/interfaces.go:47，入参 PolicyPluginInput :37）。数据面侧的内部 IR 在 crates/agentgateway/src/types/agent.rs：Bind :48、Listener :118、Route :802、ModelRoute :833、McpBackend :1914——控制面翻译的终点就是这组类型的序列化形态。

**xDS 下发**：syncer 把 krt 集合快照翻译为 xDS 地址集合，经 krtxds/xds.go 推送——文件头注释钉死派生关系（xds.go:1 "derived from istio/pilot delta.go"），以 delta gRPC 双向流下发。数据面消费端是 crates/xds/src/client.rs 的 Delta xDS 客户端：DeltaDiscoveryRequest 构造在 :421，ACK/NACK 信号处理 :468-469，指数退避 10ms 起步、15s 封顶（:474-475）。

**Rust 过滤器矩阵**：crates/agentgateway/src/http/mod.rs:1-34 声明 31 个子模块——filters/jwt/oidc/apikey/auth/authorization/ext_authz/ext_proc/localratelimit/remoteratelimit/budget/csrf/compression/outlierdetection/transformation_cel 等。授权引擎的核心三态在 authorization.rs:114-117（`Policy::Allow/Deny/Require(Arc<cel::Expression>)`，每条规则就是一个 CEL 表达式）；出站认证 BackendAuthKind 在 auth/mod.rs:72（AWS SigV4/Azure/GCP/OAuth 交换/cross-app 等变体分布在 :89-95）。

**三大子系统职责与衔接**：MCP 网关（src/mcp/）管 agent-to-tool 会话中继与工具联邦——它的价值在于把 N 个分散的 MCP server 聚合成一个端点，工具列表合并、资源名前缀改写、按用户类型动态路由都在这一层发生；LLM 翻译引擎（crates/llm + src/llm/）管协议互译与模型路由（ModelRouter 在 src/llm/model_router.rs:215）——客户端可以用任意一家协议说话、后端可以是任意另一家，互译矩阵以 Anthropic Messages 为枢纽格式中转（messages.rs:1223），流式场景逐帧翻译，这是全仓正确性要求最高的代码；CEL 栈（cel-fork/celx/src/cel）是公共表达式底座，被路由匹配、授权、guardrail、限流分桶、日志属性五处复用——cel/mod.rs:39 的 ContextBuilder 在配置期静态提取表达式引用了哪些变量、请求期按需注入对应快照，实现"用户只为用到的数据付费"（避免每个请求都构造全量上下文对象）。三者衔接点在 httpproxy.rs 的三层策略链：前端策略（监听器级）→网关策略→后端策略，MCP/LLM 各自在后端类型分派处接管；CEL 则像血管一样穿过滤滤器矩阵的每一站。

**standalone 模式的位置**：crates/agentgateway/src/config.rs 的 `parse_config`（:33 起）解析本地 YAML——先 shellexpand 展开环境变量、再注册 customFunctions（CEL 自定义函数配置化）——产出的 Config 与 xDS 下发产出的 Config 在 state_manager 层汇合。也就是说 standalone 不是"简化版"，而是把控制面的翻译产物交给用户手写，数据面执行逻辑完全同一套。

## ④ 一条请求的生命周期

先给全局视角：数据面是"配置驱动的状态机"——store/binds.rs（4787 行）持有 binds/backends/policies 双索引，xDS 资源的每次 upsert 都变成 BindEvent 流更新内存拓扑，请求处理路径上没有任何到控制面的同步调用，一切都读这份本地快照。所以理解一条请求，实际要理解"快照怎么来"（控制面回环）与"快照怎么用"（数据面路径）两半。

**数据面路径**（以 standalone 模式的 LLM 请求为例）：

1. **监听接入**：crates/agentgateway/src/proxy/gateway.rs:128 的 Gateway 按 bind 起监听，`proxy_bind`（:399）按协议分派——TLS bind 走 `maybe_terminate_tls`（:436-437）在边缘终结，另有 PROXY protocol 与 HBONE/waypoint 隧道分支（:268 引用 hbone h2 配置）。
2. **HTTP 处理主干**：交给全仓最大文件 proxy/httpproxy.rs（5712 行）走前端/网关/后端三层策略链；`select_backend`（:60）按路由选后端，`classify_request_protocol`（:82）判别请求协议决定后续管线。
3. **过滤器链**：http/mod.rs 矩阵逐个执行——JWT 验签（jwt.rs:72 的 `Jwt` 结构；:166 注释钉死 `iss` claim 必须匹配）、CEL 授权（authorization.rs:114）、本地令牌桶限流（localratelimit.rs:12 的 `RateLimit`）、ext_authz 外部仲裁（ext_authz.rs:59-60 复用 Envoy service.auth.v3 proto）。
4. **CEL 上下文按需注入**：cel/types.rs:43 的 `request: Option<RequestRef>` 按需挂载请求快照；敏感头脱敏由 `redact_sensitive`（:1938）与 config.rs:43 的 sensitive_headers 配置共同控制——日志与 CEL 求值看到的都是脱敏后视图。
5. **协议翻译与上游转发**：LLM 请求进 src/llm/，按目标 provider 把归一化消息模型翻成 wire 协议——crates/llm/src/types/messages.rs:14/126 的 Request/Response 是统一入口，:1223 的 MessagesResponse 是 Anthropic 枢纽格式（所有互译都以 Anthropic Messages 为中转），SSE 流式逐帧翻译含 thinking 预算钳制与 cache_control 映射。MCP 请求则进 src/mcp/：router.rs:37 `should_passthrough` 决定 well-known OAuth 端点直通，:70 `serve` 起服务；handler.rs:1140 `fanout_open_streams` 把 `*/list` 类方法扇出到多上游合并结果（:1246 记录 fanout 中单上游失败时的跳过降级）；会话由 session.rs:880 的 SessionManager 管理，:899 `ensure_idle_running` 起空闲收割任务防止会话泄漏。
6. **响应回环**：沿原链路返回，遥测/预算/日志类过滤器在响应侧再执行一轮（这正是 budget 成本核算与 token 统计的发生时机）。

**控制面如何改变数据面行为**（K8s 模式的完整回环）：

1. controller/pkg/setup/setup.go:191 `ctrl.NewManager` 装配 manager，串起集合、controller 与 syncer；
2. gw_controller.go:284 `Reconcile` 响应 Gateway/GatewayClass/AgentgatewayParameters 变更，调 deployer 用 helm v4 库内渲染产出数据面工作负载（deployer.go:12-16 的 helm imports）；
3. syncer.go:143 `buildResourceCollections` 把 krt 集合经 translator/plugins 翻译成 xDS 资源，krtxds 以 delta 流推送；
4. 数据面 state_manager.rs:16 的 StateManager 监听资源变更，:190 "resource changed, reloading" 触发热更新——配置原子替换、连接不断；
5. 状态回写：syncer.go:212 `buildFinalGatewayStatus` 等把翻译期条件按 Gateway/ListenerSet 分桶聚合回 K8s status，用户在 kubectl 里看到的 Ready 条件由此而来。

## ⑤ 目录导航

| 你想做什么 | 去哪里 | 要点 |
|---|---|---|
| 改 CRD schema/加策略字段 | controller/api/v1alpha1/agentgateway/ | 改完必须 `make gen` 重新生成 deepcopy/register |
| 加/改 HTTP 过滤器 | crates/agentgateway/src/http/ | mod.rs:1-34 注册子模块 + types/agent.rs 挂载进策略模型 |
| 加 LLM provider | crates/llm/src/（新 provider 模块 + conversion 实现） | lib.rs:11-23 是现有八家模块清单可照抄 |
| 加 provider 金样本 | crates/llm/src/tests/{requests,response}/ | golden_tests.rs:54 的 test_request 骨架自动拾取 |
| 改 MCP 网关行为 | crates/agentgateway/src/mcp/ | 阅读顺序 router.rs→handler.rs→session.rs |
| 加 CEL 自定义函数 | crates/celx/src/general.rs:20 `insert_all` | 函数注册集中在 :22-42（json/base64 族） |
| 改 UI 页面 | ui/src/pages/ | Models.tsx:105 三路由策略、McpServers.tsx:45 四类 target |
| 改安装/Helm | controller/install/、tools/get-agentgateway | 安装脚本 323 行，10 组平台矩阵 + GPG/SHA256 双验证 |
| 加 e2e 场景 | controller/test/e2e/ + testdata/ | 照 mcp_test.go:26 的 TestMCP + t.Run 结构写 |

一个容易踩的路径坑：找"网关主程序"时别去 crates/agentgateway/src/main.rs（不存在）——二进制入口在 agentgateway-app crate（见⑦第 1 条）；找 UI 的 API 客户端时别手写 fetch——ui/src/api/ 全部是生成代码（base.ts/configApi.ts/costsApi.ts 等按资源切分）。另外 Go 侧是三个 module：根 go.mod（module 名 github.com/agentgateway/agentgateway，controller/ 属于它）、api/go.mod（proto 生成代码独立成 module）、tools/go.mod（工具依赖隔离），改依赖时别改错文件。

## ⑥ 构建·测试·质量体系

**日常命令**（Makefile 目标行号实证）：`make build`（:68，cargo 构建）、`make lint`（:87，clippy）、`make test`（:106，`cargo test --tests --benches --examples`）、`make gen`（:131，generate-apis+generate-schema+format 三合一）、`make ui`（:63）、`make validate`（:157，examples 批量校验）。仓库没有 justfile，构建入口统一是 Makefile；CONTRIBUTION.md「Coding Standards」节钉死提交前检查：Rust 跑 `make lint`+`make test`，UI 跑 `pnpm check:fix`+`pnpm lint`+`pnpm test:e2e`，提交信息遵循 Conventional Commits。

**本地环境**（DEVELOPMENT.md）：Rust 1.86+、Node 24.17.0（ui/.nvmrc 锚定）、`corepack enable` 后 `pnpm install --frozen-lockfile`（锁文件严格模式，CI 与发布同款命令）；UI dev server 在 http://localhost:19000。K8s 联调走 Tilt（Tiltfile 支持 Live Update）。

**四层测试防线**，从快到慢：

1. **Rust 快照测试**：golden_tests.rs 以 insta 快照驱动 36 个测试函数（grep #[test] 实证），逐 provider 断言请求/响应/SSE 翻译输出——改翻译逻辑先跑这层，秒级反馈。
2. **Rust 集成测试**（crates/agentgateway/tests/）：integration.rs、fips.rs（FIPS 合规）、fips_jwt_init_order.rs（初始化顺序）、validate_examples.rs（校验 examples/ 全部 45 个场景配置）。测试基座是进程内网关——tests/common/gateway.rs 从 YAML 拉起真实网关进程（随机端口/优雅关闭），proxymock.rs:120 `basic_setup` 用 MemoryConnector 零网络开销组装 listener/route/backend/policy 拓扑，另有 extauthmock/extprocmock 等外部依赖 mock。
3. **Go e2e**（controller/test/e2e/，build tag `e2e`）：38 个 Test 函数、115 个 t.Run 子场景（实测统计），31 个 testdata 场景目录。跑法示例：`go test -tags=e2e -v ./controller/test/e2e -run '^TestRBAC$'`（README-e2e-framework.md:24）。框架是 istio test 风格 + gomega 断言（assertions.go 的 Eventually* 轮询），**不是 ginkgo**。
4. **conformance**（controller/test/conformance/conformance_test.go）：Gateway API 一致性验证，证明标准 API 实现没有走样。

**CI 卫生**：tools/exec-go-tool 按 go.mod+go.sum 校验和把 controller-gen/buf/helm 等工具缓存到 .bin 并版本锚定，保证本地与 CI 生成物一致；check_clean_repo.sh 在 CI 强制「make gen 后工作树必须干净」——这是生成物纪律的守门人，本地提交前自查 `make gen && git status`。

**质量体系的设计取向**值得新人体会：这个仓把"正确性事实标准"外化成了数据（金样本 JSON）而不是代码（手写断言），把"配置有效性"外化成了 examples/ 的 45 个可运行场景（validate_examples.rs 兜底），把"生成物一致性"外化成了干净树检查。三者共同点是用机器可判定的外部基准替代人肉 review，改动是否破坏行为几乎总能由某层防线自动回答——新人提交前照这个层次自下而上跑一遍，能省掉大量 review 来回。

## ⑦ 深水区预警（图谱台账勘误，全部源码实证）

1. **`agentgateway` 二进制不是 agentgateway crate 直接产出的**：`[[bin]] name = "agentgateway"` 在 crates/agentgateway-app/Cargo.toml:8-9；入口 crates/agentgateway-app/src/main.rs:2 只有一行 `fn main() -> anyhow::Result<()> { agentgateway_app::run() }`；UI 静态资源经 include_dir 打进二进制（crates/agentgateway-app/src/lib.rs:15，feature `ui_assets`）；Dockerfile:59 `CARGO_FEATURES=agentgateway-app/ui`。改数据面启动逻辑（线程池/drain/UI 装配）要看 app crate，别只盯 agentgateway crate 的 lib.rs。
2. **kgateway fork 遗产死路径**：控制面 fork 自 kgateway，残留多处死引用——`TLSSecretName = "kgateway-xds-cert"`（controller/api/settings/settings.go:151）、`LegacyMCPServiceHTTPPath = "kgateway.dev/mcp-path"`（controller/api/annotations/agentgateway.go:12）、`mcpProtocolLegacy = "kgateway.dev/mcp"` 系列（controller/pkg/syncer/backend/mcp.go:30-33）、apiclient 仍持有 kgateway clientset 字段（controller/pkg/apiclient/client.go:21）。读代码遇到 kgateway 字样先判断是不是兼容遗留，别当活跃功能路径追。
3. **`@/gateway-config` 是生成物**：ui/scripts/generate-schema.mjs:23 从 sanitized schema 生成 `ui/src/gateway-config.d.ts`，25 个文件 import 它（如 ui/src/pages/Models.tsx:52）。改类型要改 Rust 侧 LocalConfig 再重新生成，直接改 d.ts 会被下次生成覆盖。`@` 别名映射在 ui/vite.config.ts:20（→ ./src）。standalone 配置的权威 Schema 是 schema/config.json（title=LocalConfig，323 个 $defs，实测计数）。
4. **上游拼写笔误 `outlierdetction`**：crates/agentgateway/src/http/outlierdetection.rs:100 `#[path = "outlierdetction_tests.rs"]`——测试文件名本身拼错（少个 e），是上游遗留，图谱台账 PROGRESS.md:36 已钉版。grep 文件时两种拼写都要试，否则会误判"没有 outlier detection 测试"。
5. **UI provider 枚举实数 24 家**：ui/src/config.ts:48-73 的 `providerNames` 列表实数 24 项（openai…custom），其中核心 9 家在 `coreProviderNames`（config.ts:75 起）。图谱台账写 21 家，以源码为准；讨论"支持几家 provider"时先区分 UI 枚举（24）与 CRD ExactlyOneOf 枚举（9，见 agentgateway_backend_types.go:215）两个口径。
6. **e2e 框架语义**：不是 ginkgo——mcp_test.go:26 起是原生 `go test` 的 `TestMCP` + `t.Run` 子测试结构；gomega 只做断言层。台账里"ginkgo 语义"的说法指 base/test.go 的包装风格，别按 ginkgo 的 It/Describe 心智去找测试。
7. **行数口径**：图谱台账的行数偶有 ±1 漂移（traffic_plugin.go 实测 2519 行 vs 台账 2520；lib.rs 顶层模块实数 28 个 vs 台账 27），引用行号前用 `wc -l`/grep 复核。本文所有大文件行数（httpproxy.rs 5712 行、binds.rs 4787 行、bedrock.rs 4658 行、Logs.tsx 2951 行、policy_types.go 3682 行）均实测确认。
8. **凭据键名是跨语言契约**：controller/pkg/wellknown/constants.go:5-29 钉死 Secret 数据键名（accessKey/clientSecret/credentials.json/Authorization 等），控制面写、数据面读，改一处必须两头同步，否则凭据解引用静默失败。
9. **CEL fork 与上游的分叉**：CEL 解释器在 crates/cel-fork/cel/（不是 crates/cel-fork/src/），Program 在 lib.rs:194、compile 在 :205。目录结构是 cel + cel-derive 两个子 crate，别按常规 src/ 布局找。
10. **MCP SDK 双版本并存**：主版本 rmcp 3.1.0（crates/agentgateway/Cargo.toml:125，依赖别名为 legacy 的旧版另有 `legacy-rmcp = { package = "rmcp", version = "0.10.0" }` 在 :230，启用 SSE server transport）。生产代码里 sse.rs/mod.rs 用旧版处理 Legacy SSE 传输，新版走 Streamable HTTP——读 MCP 传输层时看到两个 rmcp 别名不要以为是冗余依赖。

## ⑧ 上手路线：3 天计划

**Day 1 —— 契约与控制面（tour 步 1-6）**：上午读 README + CHARTER 建立 Mission 感，过 Makefile:68/106 与 Cargo.toml workspace（16 成员）；精读四种 CRD 类型，重点吃透 agentgateway_backend_types.go:55 的 ExactlyOneOf 六选一——它是全系统路由分派的根。下午跟 translator/conversion.go 的路由翻译（:762 parentRef 准入）与 interfaces.go:47 的 PolicyPlugin 骨架，再看 gw_controller.go:284 → deployer → syncer.go:143 → krtxds/xds.go:1 的下发链。傍晚动手：跑通 `make build` 与 `make test`，浏览 controller/test/e2e/mcp_test.go 的场景组织。**检验标准**：能白板画出"一个 Gateway CR 变更如何变成数据面配置"的全链路。

**Day 2 —— 数据面与三大子系统（tour 步 7-13）**：上午从 lib.rs:158 的 RawConfig 与 app.rs:14 的 run 生命周期读起，过 gateway.rs:128 接入与 httpproxy.rs 三层策略链；选 2-3 个过滤器精读（建议 jwt.rs + authorization.rs:114 + localratelimit.rs）。下午主攻招牌能力：mcp/router.rs:37 → handler.rs:1140 fanout → session.rs:880 会话收割的 MCP 中继线，以及 crates/llm 的 messages.rs:14 枢纽格式 + conversion 互译 + golden_tests.rs:54 快照机制；顺带理解 cel/mod.rs:39 ContextBuilder 的按需注入设计。**检验标准**：能说清一条 LLM 请求从 TLS 终结到 SSE 帧翻译回环经过的关键函数。

**Day 3 —— 底座、UI 与动手闭环（tour 步 14-16）**：上午扫 crates/xds/src/client.rs 的 Delta 客户端与 ACK/NACK/退避（:468-475），了解 core/http/pool/hbone 如何被网关主体复用；看 ui/src/config.ts:48 的 24 家 provider 与 Models.tsx:105 的三种虚拟路由策略，理解 `@/gateway-config` 生成链（generate-schema.mjs:23）。下午动手闭环：挑一个 examples/ 场景（45 个任选）改配置跑 validate_examples.rs 验证，或在 crates/llm/src/tests/ 加一个小夹具跑金样本；最后读 tools/exec-go-tool 与 check_clean_repo.sh 理解 CI 卫生。**检验标准**：你的第一个 PR 一次过 `make gen` 的干净树检查。

**卡住时去哪查**：协议语义疑问先看 crates/protos/proto/ 的 proto 源文件（ext_mcp.proto/resource.proto 是契约原文）；策略字段行为疑问对照 CRD 类型注释（kubebuilder 注释就是文档）；运行行为疑问优先读 e2e 场景（controller/test/e2e/testdata/ 31 个目录是最全的行为样例库）；数据面行为疑问看进程内集成测试（crates/agentgateway/tests/tests/）怎么断言的。另外 controller/test/e2e/debugging.md 专门讲本地调试 e2e 的方法，README-e2e-framework.md 讲框架 API——两者是 e2e 层的地图。

——完——
