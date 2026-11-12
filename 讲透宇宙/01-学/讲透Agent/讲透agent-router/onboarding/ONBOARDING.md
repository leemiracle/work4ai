# agent-router 新人 Onboarding（原 Envoy AI Gateway，AAIF 基金会治理的 Envoy 驱动 AI 流量控制面）

> 图谱基线：commit `7bcb4547`（2026-10-20），15 层 / 3083 节点 / 12740 边，分析于 2026-10-23。文中行号锚均经源码逐一核实；图谱概数与实测可能有零星漂移（本轮抽验大部分吻合，个别偏差见⑦节）。

## ① 这个项目是什么 / 为什么存在

**Agent Router 就是原 Envoy AI Gateway**。README.md:12 写明 "An Agentic AI Foundation project. Formerly *Envoy AI Gateway*"，README.md:29 起有整节更名公告：项目捐入 AAIF 基金会后仓库迁到 `theagentrouter/agent-router`、网站迁到 theagentrouter.ai，但**部署面一切照旧**——CRD 与 API group 不变、CLI 仍叫 `aigw`、namespace 仍是 `envoy-ai-gateway-system`、容器镜像与 Helm chart 名不变，且 **Go module 路径不变**：go.mod:1 至今仍是 `module github.com/envoyproxy/ai-gateway`。

先钉死最容易踩的身份坑（这也是本次图谱分析的最大勘误）：**本仓是 Go 项目，不是 Rust**——全仓 637 个 `.go` 文件、零 Cargo.toml；它也不是 "A2A 协议路由器"——A2A 目前只是 preview 能力（⑦节第 2 条），主线是 **LLM 协议翻译网关 + MCP 网关**两条产品线。AAIF 仓集合里真正的 Rust 实现是同批的 agentgateway，两者别混。

定位一句话（README.md:25）：给应用团队一个对一切模型与工具统一的 **OpenAI 兼容 API**——从托管厂商到自托管推理再到 MCP server；平台团队把凭证、路由、配额、failover、用量归因集中在一处，由 Envoy 与 Envoy Gateway 强制执行。"Agent Router controls, Envoy carries"——本仓只写控制面与数据面扩展，流量本身永远由 Envoy 扛。

为什么存在（GOALS.md:3-9）：降低应用接多家 GenAI 服务的集成复杂度，提供安全可规模化的 GenAI 流量路由。两类画像（GOALS.md:32-38）：**应用开发者**只要简单有效的 AI 流量接入；**基础设施管理员**要能安全、大规模地配置与监控。形态上是**两级网关模式**（README Usage 节）：Tier One Gateway 做认证、顶层路由、全局限流；Tier Two Gateway 对自托管模型集群做细粒度控制，含 endpoint picker（EPP/InferencePool）推理优化。

仓库产出三个进程入口：`cmd/controller`（K8s 控制面）、`cmd/extproc`（Envoy 外部处理数据面）、`cmd/aigw`（免 K8s 单机 CLI——README.md:43-49：`OPENAI_API_KEY=sk-... aigw run` 一条命令在笔记本起完整网关，监听 `localhost:1975/v1`）。规模感：637 个 Go 文件、15 层图谱 3083 节点，最大单文件 controller/gateway.go 1598 行；当前发布线 v0.6.0→v1.2.0（release-notes/ 五版，v1.0.0 是稳定里程碑），节奏跟随 Envoy Gateway 约两三个月一版。本文用法：②当地图、③当字典、④当主线剧情、⑦当避坑清单——四者合起来就是新人的前三天。

## ② 全景架构：15 层地图

- **L01 文档与设计提案层（25 文件）**：README/GOALS/CONTRIBUTING/SECURITY 等治理文档 + `docs/proposals/` 13 篇编号设计提案（001 立项、002 推理网关、003 EPP 集成、004 厂商专有字段、006 MCP 网关、009 配额感知路由、010/011/012 MCP 线）+ release-notes/ 五版发布说明。提案每篇都是"动机→schema 扩展→实现拆解"的完整设计文档，是理解"为什么长这样"的第一手史料。
- **L02 根配置与工程治理层（36 文件）**：go.mod（钉 go 1.27.2）、Makefile（全仓构建编排轴）、仓根单 Dockerfile（双阶段构建）、GitVersion.yaml、netlify.toml（文档站）与 .github/workflows/ 七个 CI 流水线。
- **L03 API CRD 类型层（27 文件）**：`api/v1beta1` 与 `api/v1alpha1` 双版本 CRD Go 类型。v1beta1 五大 CRD：AIGatewayRoute（api/v1beta1/ai_gateway_route.go:37，路由规则/后端引用/LLMRequestCosts 成本口径）、AIServiceBackend（后端+方言声明）、BackendSecurityPolicy（多云凭证聚合）、MCPRoute、GatewayConfig（extproc 容器与全局成本统计）；api/v1beta1/shared_types.go:19 的 `VersionedAPISchema` 是整个翻译体系的枢纽类型。API group 为 `aigateway.envoyproxy.io`（api/v1beta1/doc.go:10）。
- **L04 API 生成客户端层（78 文件）**：client-gen 机械产出的 clientset（typed+fake）/informers/listers，v1alpha1 41 文件 + v1beta1 37 文件。controller、e2e 与 aigw CLI 都经它读写 CR 对象——**全部为生成代码，改类型后须重跑 `make codegen`，永远不要手改**。
- **L05 协议翻译矩阵层（88 文件，全仓心脏）**：`internal/translator` 组成 model→model 翻译矩阵：openai_/anthropic_ 入口前缀 × openai/awsbedrock/awsanthropic/azureopenai/gcpvertexai/gcpanthropic/cohere/typesafe 等后端组合。awsbedrock 方向把 Chat Completions 映射为 Bedrock Converse API（含 thinking budget、cachePoint、ConverseStream 事件流回译），converse_helper/gemini_helper/anthropic_helper 是三个共享转换库。
- **L06 共享 API 契约层（33 文件）**：`internal/apischema`（19 Go 文件，OpenAI/Anthropic 的 wire schema 与多态 union 手写序列化、stream_fold 流式事件折叠——为绕开 encoding/json 的性能与多态短板）；`internal/internalapi`（三方共享的 `x-ai-eg-` 内部头前缀，internalapi.go:22；MCP 元数据头前缀 :70）；`internal/filterapi`（数据面声明式配置模型）。
- **L07 K8s 控制器调谐层（57 文件）**：`internal/controller`——controller.go:120 的 `StartControllers` 构造全部 reconciler 并按 backend→route→gateway 事件级联；gateway.go（1598 行）是 AIGatewayRoute/MCPRoute/QuotaPolicy/BSP/Secret 聚合到 HTTPRoute+extproc 配置的翻译总装线；`rotators/` 12 文件管 AWS/GCP/Azure 的 OIDC 凭证轮转（换临时凭据写回 Secret）。
- **L08 Envoy Gateway 扩展与配额 xDS 层（22 文件）**：`internal/extensionserver` 16 文件实现 Envoy Gateway 扩展 gRPC 服务（同时挂 gRPC 健康检查，extensionserver.go:101-111）：post_translate_modify.go:113 的 `PostTranslateModify`（1313 行编排集群名解析、ext_proc 过滤器插入、元数据注入）、post_route_modify.go:21、post_cluster_modify.go:32、mcproute.go:40（MCP 回环 listener 生成）、inferencepool.go:39-41（InferencePool 集群元数据键 `per_route_rule_inference_pool`）；`internal/ratelimit` 6 文件（runner+translator）做配额限流。
- **L09 Envoy 外部处理与 MCP 代理层（32 文件）**：`internal/extproc` 11 文件——server.go:71 `NewServer` 起 ExternalProcessor gRPC 双向流，models_processor.go:27 的 `/v1/models` 端点（含 Anthropic 兼容版 :96）；`internal/mcpproxy` 21 文件——MCP 会话代理运行时：CEL 授权 fail-closed、legacy/modern 双纪元协议、工具集变更 list_changed 通知（config.go:129）。
- **L10 后端认证与数据面工具库层（38 文件）**：`internal/backendauth` 16 文件覆盖 APIKey/Bearer、Anthropic x-api-key、AWS SigV4、Azure API-key/OIDC、GCP 等厂商认证 handler；另有 bodymutator/headermutator（请求体头变异）、redaction（脱敏）、llmcostcel（LLM 成本 CEL 表达式）、requestheaderattrs 等十余个微型支撑包。
- **L11 可观测性层（105 文件）**：`internal/tracing` 93 Go 文件——openinference/（48）与 otelgenai/（24）**双语义约定并存**的 span 词汇表，trace 上下文经 headers/_meta 双向传播；`internal/metrics` GenAI 指标与按 provider 的成本归因。
- **L12 CLI 入口与配置自举层（80 文件）**：cmd/aigw（16 Go 文件：main/run/config/translate/stdio2http/healthcheck/download_envoy）、cmd/controller、cmd/extproc（逻辑在 mainlib/main.go:217 的 `Main`，:93 `parseAndValidateFlags`）+ `internal/autoconfig`（10 文件，config.yaml.tmpl 供应商自动配置模板）。
- **L13 测试基建与假服务器层（162 文件）**：tests/internal 的 testopenai（可编程假 OpenAI 服务器：cassettes.go 全量盒带注册、handler.go JSON 语义匹配+SSE 切分、vcr.go 录制后脱敏）、testopeninference（假推理后端+trace 断言）、testmcp、testupstreamlib、e2elib，及 internal/testing（15 文件，testotel 断言器/收集器等）。
- **L14 集成与端到端测试层（192 文件）**：tests/crdcel（84 文件，CRD CEL 校验规则+用例）、tests/data-plane（24 Go 文件，extproc 数据面测试+VCR 录制回放）、tests/e2e（20 个 Go 测试：MCP 路由授权/OAuth/API-key 共 6 个 MCP 场景、配额限流、跨命名空间、provider fallback、流量切分、large_config）。
- **L15 部署清单与示例层（218 文件）**：`manifests/charts/` 双 Helm chart（ai-gateway-helm 主 chart 部署 controller+extproc，ai-gateway-crds-helm 由 controller-gen 生成 CRD 清单）+ `examples/`（basic/ 15 个 yaml 覆盖 openai/anthropic/aws（含 irsa/pod-identity/bedrock-anthropic 变体）/azure_openai/gcp_vertex/cohere/grokified/bitdeer 等供应商接入）。

数据流向一句话：**L03 CRD 被 L07 翻译、经 L08 下沉为 Envoy 配置；L09 在数据面按 L06 契约调用 L05 翻译器改写请求；L10/L11 提供认证与观测；L12-L15 是入口、验证与交付形态。**

怎么用这张地图：改 API 面去 L03/L04（记得 codegen）；改协议行为去 L05/L06；改控制逻辑去 L07/L08；改数据面行为去 L09；加观测去 L11——五条改动主线各自只跨两三层，这是分层设计给的直接红利。反过来排查线上问题也按此路由：请求没到后端查 L08 集群解析与 L09 选路，请求到了但格式错查 L05 翻译器，凭证错查 L10 backendauth 与 rotators，指标/trace 缺失查 L11 装配。

## ③ 核心抽象

**1. 泛型翻译器 Translator**。internal/translator/translator.go:48 定义 `Translator[ReqT, SpanT]` 四方法接口：RequestBody（含 forceBodyMutation/onRetry 语义的 flag 参数——同一个翻译器在首次发送与故障转移重发时行为可以不同）/ResponseHeaders/ResponseBody/ResponseError——任何"客户端方言→后端方言"组合都实现这四步。除 chat completions 主线外，矩阵还覆盖 completions/responses/embeddings/speech 与 token 计数（counttokens 族）等端点族，各自独立成文件。流式翻译的公共地基在 util.go：40 行 `cutSSEFieldPrefix`、50 行 `cutSSEDataPrefix`、56 行 `nextSSEEvent` 三件套负责 SSE 事件切分（剥字段前缀、兼容 LF/CRLF、保留半包）。命名约定：**文件名两段 = from_To**，`openai_awsanthropic.go` = OpenAI 方言入 → AWS Bedrock Anthropic 出，构造器 openai_awsanthropic.go:36 `NewChatCompletionOpenAIToAWSAnthropicTranslator` 可直接反读方向；反向例证 anthropic_openai.go:31 `NewAnthropicToChatCompletionOpenAITranslator`；最简直通族 openai_openai.go:30 之外 :36 还有 AWS OpenAI 变体。跨方向共享的 OpenAI↔Anthropic 双向转换库 anthropic_helper.go 有 **1541 行**，覆盖工具 schema、内容块、thinking 配置与结构化输出门控。

**2. 数据面 Processor 五方法契约**。internal/extproc/processor.go:25 的 `Processor` 接口：ProcessRequestHeaders/ProcessRequestBody/ProcessResponseHeaders/ProcessResponseBody + SetBackend（注释明言仅 upstream filter 调用）。processor_impl.go:236 的 `routerProcessor[ReqT,RespT,RespChunkT,EndpointSpecT]` 与 :486 的 `upstreamProcessor` 是两个泛型实现——router 级做请求解析、模型改写与选路，upstream 级做后端定向改写与响应回译。server.go:102-104 的 `processorForPath` 按 `:path` 实例化处理器（如 `/v1/models` 走 models_processor.go:27 的 modelsProcessor，Anthropic 兼容端点 :96 另有 anthropicModelsProcessor）。

**3. CRD→filterconfig 编译管道**。controller 把全部 CRD 聚合编译成 `internal/filterapi/filterconfig.go:25` 的 `Config` YAML，再分片写进 Secret 下发：internal/controller/filter_config_bundle.go:23-27 规定每片 `filterConfigBundlePartSizeBytes = 700*1024`、固定 8 个槽位（`maxFilterConfigBundleSlots = 8`，注释说明固定槽位数是为避免分片数变化导致重新挂载）；extproc 侧由 filterapi/watcher.go:38 的 `StartConfigBundleWatcher` 轮询挂载点，config_bundle.go:65 的 `ReassembleBundleConfig` 重组并校验完整性。这是控制面与数据面之间唯一的配置通道——读懂它就读懂了两个进程的边界与热更新路径：watcher 按固定 tick 轮询挂载目录（watcher.go:38 的 `tick` 参数），Secret 更新落盘后 extproc 无需重启即切换新配置。

**4. extensionserver xDS 钩子**。Envoy Gateway 允许扩展服务在 xDS 生成管线各阶段打补丁，本仓实现了 PostTranslateModify（post_translate_modify.go:113，1313 行）/PostRouteModify（post_route_modify.go:21）/PostClusterModify（post_cluster_modify.go:32）三族钩子：插入 ext_proc 过滤器、解析集群名、注入元数据；mcproute.go:40 `maybeGenerateResourcesForMCPGateway` 把 MCP 后端过滤器迁入新建的 127.0.0.1 回环 listener；inferencepool.go:39-41 用内部元数据键标记 InferencePool 集群，支撑 EPP 端点选择。这是"控制 Envoy 而不 fork Envoy"的关键机制。

**5. MCP 会话代理与双纪元**。mcpproxy 把 MCP 会话（JSON-RPC over Streamable HTTP）代理到多后端：LoadConfig 编译路由级配置，authorization.go:77 `compileAuthorization` 编译 CEL 授权表达式、:193 `authorizeRequest` 执行判定，CEL 编译失败按 fail-closed 处理（authorization.go:242）；config.go:129 起处理工具集变更的 `list_changed` 通知。era（纪元）机制见⑦节第 5 条——它是本仓为跟进 MCP 新规格（2026-07-28）演化出的独有抽象。

**6. 后端认证与成本归因**。backendauth 按 BackendSecurityPolicy 的声明装配 handler（APIKey 直发、AWS SigV4 签名、Azure/GCP 的 OIDC 交换）；控制面侧 rotators/ 定期轮转出临时凭据写回 Secret。用量侧，AIGatewayRoute 的 LLMRequestCosts 声明"从响应哪个字段取 token 数/成本"，由 llmcostcel 的 CEL 表达式求值，落进指标按 provider/model/路由归因——配额（QuotaPolicy）与限流都消费这份账本。

## ④ 一次请求的生命周期（按 tour 串）

以一条 Chat Completion 请求为主线，按 16 步导览顺序串起全仓：

**认知与语言阶段（step-01/02）**：从 README/GOALS 建立两级网关认知；Makefile 的 `build.%` 模式目标（Makefile:277-285 文档化 `build.controller`/`build.extproc`/`build.aigw`）编译三入口。用户提交 v1beta1 CRD：AIGatewayRoute 声明"哪些路由到哪些 AIServiceBackend"，后者的 `VersionedAPISchema`（api/v1beta1/shared_types.go:19）声明后端方言——**路由的本质是方言重写声明**。

**控制面翻译（step-09/10/12）**：StartControllers（controller.go:120）装配全部 reconciler 并按 backend→route→gateway 级联触发；gateway.go 把路由聚合成 Envoy Gateway 的 HTTPRoute + extproc 过滤器配置；backend_security_policy 与 rotators/ 持续轮转云凭证；extensionserver 的 `PostTranslateModify`（post_translate_modify.go:113）在 xDS 层插过滤器、改集群、迁 MCP listener。最终产物是 filterconfig Config，经 700KB×8 分片写进 Secret（step-04 讲清的就是这条暗线：internalapi 头族 + filterapi 模型 + config_bundle 重组）。

**数据面请求处理（step-03/05/06/07）**：客户端发 OpenAI 方言请求 → Envoy → cmd/extproc 进程（mainlib/main.go:217 `Main` 起服务）的 gRPC 双向流；router filter 按 `:path` 建 routerProcessor（server.go:102-104），ProcessRequestBody（processor_impl.go:236）解析 body、按路由选翻译器，把 OpenAI 请求重写为后端方言（Bedrock Converse / Vertex Gemini / GCP Anthropic / Cohere……），SetBackend 钉住后端并生成内部请求 ID；upstream filter 凭该 ID 接续（server.go:183-195 判别逻辑），做最终改写、加认证头，响应与 SSE 流沿 ResponseHeaders/ResponseBody 反向翻译回 OpenAI 方言，错误走 ResponseError 回译成用户可读的 JSON。`/v1/models` 端点由 extproc 本地合成，不打到后端。后端失败时路由可按声明 failover 到下一权重后端，此时翻译器带 onRetry 标志重跑 RequestBody——这正是 flag 参数存在的意义。

**观测与配额（step-08）**：tracing.go:145-152 按 `OTEL_SDK_DISABLED`/`OTEL_TRACES_EXPORTER` 决定 NoopTracing 或真实导出（:158 起三级判定 OTLP endpoint）；semconv.go:25 的 `AI_GATEWAY_TRACING_SEMCONV` 在 OpenInference 与 OTel GenAI 双语义约定间二选一，非法值直接拒绝启动而非静默回退。token 用量经 llmcostcel 记账，配额由 ratelimit 翻译成 Envoy 的全局限流调用。

**MCP 支线（step-11）**：MCPRoute 控制面编译出共享 mcpproxy Service + 回环 listener + 每后端 HTTPRoute，安全策略生成 OAuth2/JWT/APIKey 的 SecurityPolicy 并按 RFC 9728 注入 Protected Resource 元数据；数据面 MCP 会话经 CEL 授权、双纪元校验后代理到工具后端。

**单机形态（step-13）**：`aigw run` 内嵌 Envoy Gateway 配置模板（run.go:49 `go:embed envoy-gateway-config.yaml`），在 fake clientset（run.go:79-81）上跑与生产**完全相同**的 controller reconcile 链，写出 xDS 静态资源（run.go:280 `writeEnvoyResourcesAndRunExtProc`），由 func-e 拉起的 Envoy 消费（版本钉在 `.envoy-version` = 1.39.2）。配置读取优先级在 cmd/aigw/config.go:27 起定义：配置文件经 envsubst 展开 → 环境变量（config.go:45-50：OPENAI/AZURE_OPENAI key 优先于 ANTHROPIC）→ 自动生成。

**验证与史料（step-14/15/16）**：Helm 双 chart 部署；testopenai 盒带确定性重放真实厂商响应（免凭据、零成本、毫秒级）；最后 docs/proposals/ 13 篇提案收口设计演进史——002/003 讲 InferencePool 与 EPP 集成，004/005 讲厂商专有字段与 OriginalModel 归因，006→012 是 MCP 线的完整演进。

## ⑤ 目录导航

- `api/`：CRD 类型（v1beta1 稳定面 + v1alpha1）与生成客户端。改类型后必跑 `make codegen apigen`，否则 zz_generated 与 clientset 漂移。
- `cmd/`：三个 main——aigw（本地全栈运行器，子命令 version/run/healthcheck/download-envoy，见 main.go:36-42）、controller（K8s 控制面）、extproc（数据面，主体逻辑在 mainlib）。
- `internal/` 核心子包速查：translator（翻译矩阵）、extproc（数据面处理器）、controller（reconciler 总装+rotators）、extensionserver（xDS 钩子）、mcpproxy（MCP 代理）、backendauth（后端认证）、apischema（wire 契约）、internalapi（`x-ai-eg-` 头族）、filterapi（数据面配置）、tracing/metrics（观测）、ratelimit（配额限流）、autoconfig（CLI 自动配置）、redaction/bodymutator/headermutator（变异与脱敏）。
- `tests/`：internal（假服务器基建）、crdcel（CEL 校验）、data-plane（VCR 集成）、e2e（envtest 全链路，20 个场景文件）。
- `manifests/charts/`（Helm 双 chart）、`examples/basic/`（15 个供应商样例，最快上手语料）、`docs/proposals/`（设计史）、`site/`（文档站源码；A2A preview 文档在 site/docs/capabilities/a2a/）。仓根还有 `.env.ollama`（本地 Ollama 供应商 env 样例）与 pre-commit.sh。

按任务找文件的三条捷径：给新供应商加翻译，进 `internal/translator/` 按 from_To 命名新建文件并实现四方法，再去 apischema 补缺的 wire 类型；给新认证方式，进 `internal/backendauth/` 加 handler 并在 BackendSecurityPolicy 声明；调 MCP 行为，控制面在 `internal/controller/mcp_route*.go`、数据面在 `internal/mcpproxy/`。找不到符号时优先按旧名（ai-gateway/aigw/aigateway.envoyproxy.io）grep，而不是新名。

## ⑥ 构建·测试·质量体系

`make help` 列全部目标。本地开发第一件事是把 pre-commit.sh 挂上（`make precommit`），否则 CI 的 pr_style_check 会替你发现格式问题。代码质量线：`make lint format spellcheck editorconfig tidy`（CI 的 precommit_check.yaml 强制）。生成线：`make codegen`（controller-gen/client-gen 等）、`make apigen`（生成客户端与 CRD 清单入 crds-helm）、`make apidoc`（CRD 参考文档）——**api/ 目录任何改动后三者必跑**。构建线：`make build.aigw build.controller build.extproc`（Makefile:277-285 的 `build.%` 模式，支持 GOOS_LIST/GOARCH_LIST 交叉编译）。

测试是三层漏斗：单元（`make test`，含 test-coverage 覆盖率门）→ 数据面集成（`make test-data-plane`:211 无 K8s 跑 extproc+VCR 盒带回放；`make test-data-plane-mcp`:223 加 MCP 场景；`make test-crdcel` 跑 84 文件 CEL 用例；`make test-controller` 走 envtest 假 K8s）→ 端到端（`make test-e2e`:20 个场景、`make test-e2e-aigw`:268、`make test-e2e-upgrade` 升级路径、`make test-e2e-inference-extension`/`test-e2e-namespaced` 细分）。测试哲学是**确定性重放**：testopenai 用 go-vcr 格式 YAML 盒带按 `X-Cassette-Name` 头匹配重放真实厂商响应——免凭据、零成本、毫秒级；testopeninference 对偶缓存预录制 OpenInference span 做 trace 断言。Helm 侧有 helm-lint/package/test/push 四目标。CI 七个 workflow：build_and_test（主门）、codeql（安全扫描）、docker_build_job、precommit_check、pr_style_check、release、retest。发布物为 docker.io/envoyproxy/ai-gateway-* 镜像（名字未随更名变）。

## ⑦ 深水区预警（图谱勘误与坑）

以下 7 条均经 grep/Read 实证：

1. **身份三重陷阱（本次最大勘误）**：其一，本仓是 **Go 不是 Rust**——637 个 .go 文件、零 Cargo.toml（go.mod 直接是 Go module）；其二，仓库已更名 Agent Router，但 go.mod:1 仍是 `github.com/envoyproxy/ai-gateway`，import 路径、镜像名、namespace、API group 全是旧名；其三，GOALS.md:1 标题至今还是 "Envoy AI Gateway GOALS.md"——**在仓里搜 "ai-gateway"/"aigw"/"aigateway.envoyproxy.io" 才是正确姿势，搜 "agent-router" 会漏掉大半代码**。
2. **A2A 只是 preview，不是主线**：site/docs/capabilities/a2a/index.md:8 原文 "Agent Router does not yet have a dedicated A2A route type"——目前靠 Envoy 原生 `envoy.filters.http.a2a`（alpha）+ EnvoyPatchPolicy 硬配出 A2A 通道（capabilities/index.md:60 标注 preview），过滤器的协议校验只认 JSON-RPC 2.0 信封、超长 body 拒收，并把 method/task/context ID 落进动态元数据（`a2a.requests_rejected`/`a2a.invalid_json`/`a2a.body_too_large` 三个计数器）；一等公民 `A2ARoute` 还在 issue #2070 讨论中。带着"A2A 路由器"的预期入手会找错入口；AAIF 仓集合里承担 A2A 生态位的是 agentgateway 仓（Rust）。
3. **QuotaPolicy 版本不对等**：配额 CRD 只存在于 api/v1alpha1/quota_policy.go，v1beta1 没有对应物（v1alpha1/registry.go:21 注册 QuotaPolicy，v1beta1 registry 只注册五大 CRD）——配额仍是 alpha 特性；双版本 API 面并不对称，别假设 v1beta1 ⊇ v1alpha1。
4. **翻译器文件名方向语义**：文件名两段式 = from_To（openai_awsanthropic.go:36 构造器 `NewChatCompletionOpenAIToAWSAnthropicTranslator` 可反读）；`openai_openai.go` 并非"单文件纯透传"——:30 直通版外 :36 还有 AWS OpenAI 变体；anthropic_helper.go（1541 行）是跨方向共享库，改 OpenAI↔Anthropic 映射时两个入口方向都会被波及。
5. **MCP 双纪元陷阱**：mcpproxy/era.go:51 按 2026-07-28 规格（SEP-2575）把 MCP 协议劈成 legacy/modern 两纪元：era.go:56 `legacyOnlyMethods` 与 :70 `modernOnlyMethods` 混用即协议错误（client 在混纪元）；最阴的是 era.go:83-86——modern 纪元协议错误映射真实 HTTP 状态码，**legacy 纪元把同样的 JSON-RPC 错误装在 HTTP 200 的 body 里**，排障时两纪元状态码语义相反，先判纪元再读状态码。
6. **extproc 单流双 filter 的隐蔽协议**：同一条 gRPC 双向流同时服务 router 与 upstream 两级 filter，靠 stream attributes 有无判别（server.go:183-195），upstream 侧凭 router 生成的内部请求 ID 头接续（server.go:127-128 定义，注释言明这是为避免两级 filter 各自生成 ID 的竞态），ID 缺失直接 Internal 报错（server.go:190），请求结束后按 ID 清理映射（server.go:154-156）。读代码时别假设"一条流=一个请求"，也别假设两级 filter 看到同一个请求对象。
7. **图谱计数漂移与仓内小癖**：L13 fileCount=162 vs 实测 tests/internal 143 + internal/testing 15 = 158（差 4；层文件数为含 yaml/svg 的全类型口径）；L02 称"三级 Dockerfile"，实测仓根单 Dockerfile 双阶段（`FROM` 两条）。其余抽验高度吻合：translator 88、tracing 93（openinference 48/otelgenai 24）、controller 57（rotators 12）、crdcel 84、e2e 20、gateway.go 1598 行、anthropic_helper.go 1541 行、post_translate_modify.go 1313 行全对。另外 docs/proposals/ 有两个 012- 目录（012-mcp-new-spec-rc 与 012-mcp-tool-name-prefix-mode）——**编号撞号**，13 个目录只编到 012，引用提案时用目录全名别只报编号。

## ⑧ 上手路线：3 天计划

**Day 1（跑起来 + 语言层）**：上午 `OPENAI_API_KEY=... aigw run` 起单机网关，用 curl 或任意 OpenAI SDK 打 `localhost:1975/v1/v1/chat/completions`（README.md:43-49），再读 GOALS.md 与 examples/basic/openai.yaml、aws.yaml；下午精读 api/v1beta1 五大 CRD 与 shared_types.go:19 的 `VersionedAPISchema`，跑 `make codegen` 观察生成物变化。**过关标准**：能解释一条 AIGatewayRoute 如何声明 openai→aws-bedrock，并说出 v1alpha1/v1beta1 的差别（提示：QuotaPolicy）。
**Day 2（数据面心脏）**：上午精读 translator.go:48 四方法契约 + util.go SSE 三件套，挑 openai_awsbedrock.go（Converse 映射）啃透一个非平凡方向；下午跟 server.go 读双 filter 判别与 processor_impl.go:236/:486 两个泛型处理器，跑 `make build.extproc && make test-data-plane` 体会盒带重放，再开一个 VCR 测试对照盒带 YAML。**练习**：给某个翻译器加一个字段映射（比如一个工具调用参数），跑对应 data-plane 测试看盒带断言怎么报错，体会"改代码=改断言"的契约感。**过关标准**：能画出一条流式请求从 Envoy 进到响应回客户端经过的函数链。
**Day 3（控制面 + MCP + 全景收尾）**：上午读 controller.go:120 `StartControllers` 的级联拓扑、gateway.go 总装线、filter_config_bundle.go:23-27 的 700KB×8 分片与 extensionserver 三族钩子；下午走读 mcpproxy 的 era/authorization 双机制，把 docs/proposals/ 的 002/006/009 三篇当"为什么"收口，最后跑 `make test-e2e-aigw`。**练习**：在 kind 里按 site 文档起一个双后端路由，手动 kill 一个后端观察 failover 与重试日志；再用 EnvoyPatchPolicy 照 site/docs/capabilities/a2a/ 配一条 A2A preview 通道，验证⑦节第 2 条的边界。**过关标准**：能独立从"改一个 CRD 字段"说出它将依次触动哪几层（api→codegen→controller→extensionserver→Secret 分片→extproc watcher→translator），并知道排障时该去哪层加日志。

新人三诫：其一，别在 v1beta1 里找 QuotaPolicy，它在 v1alpha1（⑦-3）；其二，读 MCP 行为先判 legacy/modern 纪元再看状态码（⑦-5）；其三，全仓搜索一律用旧名 ai-gateway/aigw，新名 agent-router 在代码里几乎搜不到（⑦-1）。
