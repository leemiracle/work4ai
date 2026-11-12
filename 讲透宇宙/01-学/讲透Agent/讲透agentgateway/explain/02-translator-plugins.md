# 02 · translator 与 plugins：把 K8s 资源翻译成网关 IR 的引擎层

> 源码基线：`/usr-data/data2/repos/aaif-projects/repos/agentgateway/controller/pkg/agentgateway/`（translator/ 23 个 Go 文件 + plugins/ 26 个非测试文件）。双巨头：`plugins/backend_policies.go`（1970 行）与 `plugins/traffic_plugin.go`（2519 行）。同链路支撑：`controller/api/v1alpha1/agentgateway/`（CRD 类型）、`controller/pkg/agentgateway/jwks/`（凭据衔接）、`controller/pkg/syncer/`（下游消费）、`controller/pkg/pluginsdk/`。全文行号锚均经 sed/grep 逐条核实。
>
> **勘误（任务书 vs 源码，按源码为准）**：①任务书称 backend_policies 为"九类 LLM 策略"——实际 `translateBackendPolicyToAgw` 是 **14 个 appendPolicy 分支**（backend_policies.go:164-220：HTTP/Tunnel/TLS/TCP/Health/SessionAffinity/Transformation/Authorization + MCP 三子项 Authorization/Authentication/Guardrails + AI + Auth + ExtAuth）；"九"更接近 `translateBackendAuth` 内部的 **9 种后端凭证来源**（backend_policies.go:989 起：InlineKey/SecretRef/AWS/Azure/GCP/OAuthTokenExchange/CrossAppAccess/JwtSign/Passthrough）。②任务书把 pluginsdk 当"插件契约"重点——实际 `controller/pkg/pluginsdk/types.go` 全文仅 31 行（一个 `GatewayControllerExtension` 接口，pluginsdk/types.go:20），真正的插件契约（`PolicyPlugin`/`BackendPlugin`/`AgwPlugin`）在 `plugins/interfaces.go` 与 `plugins/registry.go`；pluginsdk 其余是 collections/krtutil/reporter 工具库。③traffic_plugin 实测 2519 行（非 2520）。

## 一、角色定位（16 层架构 L03；上游 reconcile 下游 xDS 下发的枢纽）

在 understand 图谱的 16 层架构中，translator+plugins 构成 **L03「控制面翻译与策略引擎」**，987 个节点、16 层中节点数第三大（仅次于 L08 HTTP 过滤器矩阵 1069 与 L02 API 契约 283 的两倍多），层摘要原文："K8s API 语义到 xDS IR 的翻译大脑：translator 与 plugins（traffic_plugin 为最大引擎）将 Gateway/HTT…"。它的上下游分工极其清晰：

- **上游（L02 API 契约层）**：`AgwCollections`（plugins/collection.go:30）把 Gateway/HTTPRoute/AgentgatewayPolicy/AgentgatewayBackend/AgentgatewayModel 等 CRD 全部包装成 istio **krt Collection**（响应式集合，informer 事件自动触发下游重算）——AgentgatewayPolicies 在 collection.go:221、Backends 在 :222、Models 在 :223（默认 `NewDisabledCollection`，需 `settings.EnableAgentgatewayModels` 才开，collection.go:231-233，这是一个按需减负的开关）。
- **下游（L04 控制面核心）**：翻译产物是 `ir.AgwResource`（ir/ir.go:41-44，`= *api.Resource + Gateway 归属`），由 `syncer.BuildPolicies`（syncer/policy_collections.go:34）Join 成 `resources/Policies` 集合后推向 xDS 下发（见 01 篇 gw_controller 链路）。

一句话定位：**这是控制面的"编译器前端"**——K8s 声明式资源是源语言，protobuf 定义的路由/策略 IR（`api.Route`/`api.Policy`/`api.Backend`）是目标语言，L04 的 syncer 是链接器。所有 K8s 语义的规整化（路径前缀补 `/`、百分比换算、CEL 校验、ReferenceGrant 鉴权）都发生在这一层，数据面（Rust）拿到的 IR 已经是干净的。

## 二、内部结构（四层：契约 → 集合 → 路由/模型翻译 → 策略翻译）

### 2.1 插件契约层：struct 而非 interface 的注册表

- `AgwPlugin`（plugins/registry.go:12-16）是插件贡献的三元组：`AddResourceExtension`（附加资源集合）、`ContributesPolicies`（按 GroupKind 注册策略翻译插件）、`ContributesBackends`（按 GroupKind 注册后端翻译插件）。
- `PolicyPlugin`（plugins/interfaces.go:47-52）两个钩子：`Build` 产出策略集合+status 集合；`BuildReferences` 只产引用附件——注释（interfaces.go:49-51）言明后者"用基础 ReferenceIndex 调用（在 PolicyAttachments 之前）以避免自引用图构建"，这是整个翻译管线的破环关键（详见第五节）。`BackendPlugin`（interfaces.go:42-45）同构。
- `AgwPolicy`（plugins/interfaces.go:55-59）= `Gateway 归属 + *api.Policy`；其 `ResourceName()`（interfaces.go:65-72）刻意与 AgwResource 投影同名，注释说明是为了"MapCollection 免持双集合"。
- `MergePlugins`（registry.go:21）合并多个插件；冲突检测 `contestedResourceExtensionFields`（registry.go:56-59 调用，:65 定义）用反射找出被多个插件同时填充的 AddResourcesPlugin 字段并**打日志丢弃后到者**——不 panic、静默降级，代价是冲突时行为难以察觉（无注释说明动机，此为推断）。
- 生产注册点在 `controller/pkg/controller/start.go:170-176`：`Plugins()` 返回 5 个内置插件（NewAgentPlugin/NewInferencePlugin/NewA2APlugin/NewBackendTLSPlugin/NewBackendPlugin），:190 `MergePlugins` 合一；`cfg.ExtraAgwPlugins`（start.go:186-188）留出外部扩展口——所以 pluginsdk 的 `GatewayControllerExtension`（pluginsdk/types.go:20-31，Register/Start/Stop 三方法）面向的是"Gateway 级事件扩展"，与策略插件是两条正交扩展轴。

### 2.2 集合装配层与路由翻译主线

`AgwRouteCollection`（translator/route_collections.go:449-457）一次接收 HTTP/GRPC/TCP/TLS 四类路由集合，产出 `AgwResource 集合 + RouteAttachment 集合 + AncestorBackend 集合`三元组。内部用泛型 `createRouteCollectionGeneric`（route_collections.go:898）统一四种路由的 status+翻译装配，各自只提供"一条规则→一个 api.Route"的转换闭包。以 HTTPRoute 为例（route_collections.go:466-511）：

1. `buildHTTPRouteGroupBindings`（route_collections.go:460）先建委托（delegation）绑定，注释说明要在 status collection 之前建好，才能给被委托子路由设 parent status；
2. 每条 rule 先过 `modelServingRuleRouterKey`（route_collections.go:470）判定是否"模型服务规则"——若是，注释点破设计（route_collections.go:484）："**AgentgatewayModel is a selector, not a conventional backend**"，于是清空 BackendRefs 走特殊翻译，回填单 backend 指向内部 router（route_collections.go:496-505）；
3. 常规路径进 `ConvertHTTPRouteToAgw`（conversion.go:41-98）：Key 用 `InternalRouteRuleKey`（namespace/name/rule 序号唯一，conversion.go:46）→ `processRouteMatches`（conversion.go:101-131）把 path/header/method/query 四类 match 逐一转换 → `BuildAgwTrafficPolicyFilters`（conversion.go:364）翻译 rule 级 filter → `ApplyTimeouts`/`ApplyRetries`（builtin_helpers.go:17/61，Gateway API 内建字段转 TrafficPolicySpec，零值跳过、attempts 截断 255，builtin_helpers.go:84-85）→ `buildAgwHTTPDestination`（conversion.go:81）解析后端引用；
4. `modelRouters`（route_collections.go:520-539）把带 `/llm:router:httproute:` 前缀的 router key 的路由**额外投影成一个 ModelRouter Backend 资源**——同一条数据两种 IR 形态。

match 层的规整化值得注意：`CreateAgwPathMatch`（agw.go:62）对非 regex 路径强制补前导 `/`（agw.go:70-76 注释）、前缀匹配吃掉尾斜杠但根 `/` 除外（agw.go:84-90，引 Gateway API spec 原文）、EXACT 则逐字节不归一（agw.go:97-98）；GRPC 侧的 header 匹配复用同一套 HeaderMatch proto（agw.go:372）。`CreateAgwMirrorFilter`（agw.go:206）把 Fraction/Percent 两种镜像比例统一换算成百分数（agw.go:223-234）。这些微语义是 e2e 行为差异的常发地。

### 2.3 模型翻译主线：AgwModelCollection

`AgwModelCollection`（model_collections.go:33-61）是一个 `krt.NewStatusManyCollection`：每个 AgentgatewayModel CR 进来，先 `extractModelParentReferenceInfo`（:45）解 parent gateway，再 `translateModelForParents`（:46）产资源、`reports.ReportMap`（:41-48）产 status。核心翻译函数链：`convertAgentgatewayModel`（:440）→ 虚模型 `translateVirtualModel`（:507）/具体后端 `modelConcreteBackend`（:582）/故障转移 `modelFailoverBackend`（:598）/provider 翻译 `translateModelLLMProvider`（:678）；内联策略经 `translateInlineModelBackendPolicy`（:835）复用 plugins 的 `TranslateInlineBackendPolicy`（backend_policies.go:123）——**模型翻译是策略翻译的客户**。

`extractModelAncestorBackends`（model_collections.go:66-133）专门维护祖先后端闭包：收集 custom backendRef、内联策略后端（:99-103 经 `BackendReferencesFromBackendPolicy`）、虚拟模型 callout 后端（:107-109）、failover 传递闭包（:111-121，注释说明非法目标从族谱和生成的 failover backend 中同时剔除），最后产出**排序后的 gateway × backend 笛卡尔积**（:127-131 注释原文 "Generate sorted cartesian product"）——排序是确定性输出的关键（krt 增量计算依赖 Equals 稳定）。

### 2.4 策略翻译双巨头：一个 CR，三段 47 类

`TranslatePolicyToAgw`（traffic_plugin.go:433-464）是策略总入口，严格三段式：`translateFrontendPolicyToAgw`（frontend_policies.go:26，frontend 只能 target Gateway，HTTP/ProxyProtocol 等少数分支）→ `translateTrafficPolicyToAgw`（traffic_plugin.go:480）→ `translateBackendPolicyToAgw`（backend_policies.go:139）。三段错误各自聚合，最后 `errors.Join`（traffic_plugin.go:463），且每条产物盖上 `CreationTimestamp = max(unix, 0)`（traffic_plugin.go:459）。

**traffic 段 17 类**（traffic_plugin.go:528-631 顺序即代码顺序）：ExtAuth、ExtProc、Authorization、RateLimit、Transformation、Csrf、Cors、HeaderModifiers、HostnameRewrite、Timeouts、Retry、Delay、DirectResponse、Buffer、JWTAuthentication、APIKeyAuthentication、BasicAuthentication。其中四类（ExtAuth/ExtProc/Transformation/DirectResponse）走 `processConditional`（traffic_plugin.go:1239-1273）：CRD 侧是 `ConditionalPolicy[T]`（concrete 或带 CEL 条件的列表），concrete 直出单 policy，conditional 则逐条翻译并以 `api.Policy_Conditional` 包成条件策略集（:1285-1310），CEL 条件在此即时校验（:1299 `isCEL`），全局 CEL env + 1024 容量 LRU 缓存在 `init()`（traffic_plugin.go:77-89）。

**backend 段 14 分支**（backend_policies.go:164-220）。AI 分支 `translateBackendAI`（backend_policies.go:861-987）是 LLM 网关的浓缩：PromptEnrichment（:866-868）、Defaults/Overrides 逐字段 toJSONValue（:870-894）、Transformations/FinalTransformations 为 CEL 表达式——**校验失败仍写入值**（:904-905 注释 "Still set it so it wipes out the value on error, mirroring the header value"）、PromptGuard（:920-944，请求/响应/webhook 守卫转 ai_policies.go 的 processRequestGuard/processResponseGuard）、ModelAliases（:946-948）、PromptCaching（:950-960，MinTokens 默认 1024）、Routes 的 path→RouteType 映射（:962-968）。MCP 三子项里 `translateMCPAuthenticationSpec`（backend_policies.go:737-797）展示 jwks 衔接：owner 缺省时用 `PolicyBackendMCPAuthenticationLookupOwner`（:750-753），Strict/Permissive/Optional 三态（:741-747），ClientSecretRef 经 `ResolveCredentialKeyRef` 解析且空值报错（:776-782）。Auth 分支 `translateBackendAuth`（:989 起）内部 9 选 1：InlineKey/SecretRef（Authorization 头特判在 :1019 附近）/AWS（:1668）/Azure（:1751，含 :1821 ClientSecret）/GCP（:1870）/OAuthTokenExchange（:1260，grant type/actor token/token cache 全套）/CrossAppAccess（:1157）/JwtSign（:1909）/Passthrough。

## 三、外部连接（CRD → 翻译 → IR → xDS 的四面体）

- **CRD 面（L02）**：`AgentgatewayPolicySpec`（agentgateway_policy_types.go:74）= TargetRefs（:84，CEL 校验限定 7 种可引用 Kind 且单 policy 只能一种 Kind，:81-82）+ TargetSelectors（:92）+ Strategy（:100，inheritance 仅 traffic 段有效）+ Frontend（:112）/Traffic/Backend 三大段——与翻译三段一一对应；合并语义直接写在 K8s 注释里（字段级合并非深合并，优先级 Gateway < Listener < Route < Route Rule < Backend）。
- **下游 IR 面（L04）**：`ToResourceForGateway`（gateway_collection.go:60）把 AgwPolicy 包成 AgwResource；syncer 侧**两阶段构建**：先 `CollectPolicyReferences`（syncer/policy_collections.go:20）跑所有插件的 BuildReferences 填满引用索引（注释 :22-27 说明动机："让 ext_proc backendRefs 等产生的 PolicyAttachments 先入索引，BackendTLSPolicy 这类后跑的策略才能查到 gateway"），再 `BuildPolicies`（:34）真正产策略——与 interfaces.go:49-51 的破环注释互为印证。
- **jwks 面**：`jwks.Lookup` 接口（jwks/lookup.go:10）只有一个方法 `InlineForOwner`——把远端 owner（`RemoteJwksOwner`，jwks/owner.go:32）解析成内联 JWKS JSON 字符串；PolicyCtx 携带 `JWKSOwner`（traffic_plugin.go:139）供内联 backend policy 复用 backend 的 owner。
- **解析器面**：`PolicyCtx`（traffic_plugin.go:130-149）聚合六个外部依赖：remotehttp.Resolver（SSRF 防护的 HTTP 解析）、jwks.Lookup、CredentialResolver（OSS 内建 Secret 解析或注入链，:141-144 注释）、References/Grants（引用索引与 ReferenceGrant 鉴权接口 ReferenceGrantChecker，interfaces.go:24-35）。

## 四、数据流：一条 AgentgatewayPolicy CR 变更走完翻译产出 IR

以"用户 apply 了一条 targetRefs 指向 HTTPRoute、带 traffic.jwtAuthentication 与 backend.ai 的 AgentgatewayPolicy"为例：

1. **informer 触发**：collection.go:221 的 AgentgatewayPolicies krt 集合收到事件；因 NewAgentPlugin 的 Build 已把 `TranslateAgentgatewayPolicy` 注册为该集合的变换函数（traffic_plugin.go:112-117 `krt.NewStatusManyCollection`），翻译在 krt 依赖图中自动重算——没有显式 reconcile 循环，**声明式响应式管线**。
2. **目标解析**：`TranslateAgentgatewayPolicy`（traffic_plugin.go:188）先跑一遍 `TranslatePolicyToAgw`（:214）得到与目标无关的基础策略集；再对每个 TargetRef（:300-303）/TargetSelector（:304-313，选择器无命中记 attachment error）解出 `api.PolicyTarget`，`targetKey` 结构体去重（:273-295）防同一目标被重复处理。
3. **挂接与幻影防护**：对每个 policyTarget 调 `references.LookupGatewaysForPolicyTarget`（reference_indexes.go:525）查归属 Gateway；:236-241 注释解释 backend 类目标解析失败时跳过 gateway 解析——防"另一条 backend 链恰好引用同名对象"推出幻影配置（phantom target）。
4. **克隆定靶**：`ClonePoliciesForTarget`（traffic_plugin.go:466-478）对基础策略浅克隆，Key 追加 `attachmentName(policyTarget)`（:2205 生成的挂接后缀），Target 字段指向具体目标——一份翻译、多目标复用，O(目标数) 克隆而非 O(目标数×策略字段) 重译。
5. **产出与回写**：AgwPolicy 列表（Gateway+Policy）交给 syncer 的 `BuildPolicies` Join → `ToResourceForGateway`（gateway_collection.go:60）→ `resources/Policies` 集合 → xDS 推送；同时 status 侧按 Gateway 去重后 `MergeAncestors`（traffic_plugin.go:329，plugins/status.go:39）合并已有 ancestors——:323-327 注释强调**只排序新增项**，因为 status syncer 按序写回，全量重排会让期望与实际 status 恒不等（无谓写放大）。
6. **验证闭环**：golden_test.go 的 `TestRouteCollection`（golden_test.go:50）等五个目录驱动测试，用 `testutils.RunForDirectory` 喂 testdata/ 下的 YAML 清单，断言产出的 `ir.AgwResource` 排序快照——testdata/references-policy-refgrants/ 下甚至有 denied-route-backend.yaml 这类负例。

## 五、设计决策（有注释用注释，无则标"推断"）

- **struct 注册表而非 interface**：AgwPlugin/PolicyPlugin 都是带函数字段的结构体（registry.go:12、interfaces.go:42-52），只填关心的槽位；配合 MergePlugins 的反射冲突检测（registry.go:65-86）。（推断）动机是可选钩子用 interface 需空实现或类型断言，struct 字段 nil 即未贡献，更贴合"每个内置插件只贡献一两种能力"的现状。
- **BuildReferences 与 Build 两阶段**：源码注释（interfaces.go:49-51、policy_collections.go:22-27）明确为破自引用环——策略可以引用 backend，backend 的 PolicyAttachment 又影响别的策略的目标解析，必须先收集引用再产策略。
- **巨文件的代价**：traffic_plugin.go 2519 行、backend_policies.go 1970 行，两者实际是"一个 CRD Kind 的全部字段翻译器"，与 `AgentgatewayPolicySpec.Traffic/Backend` 的字段一一对应（types.go:112/126/147 三段）。代价一：单文件合并冲突高发区（推断）；代价二：测试也巨量化——oauth_auth_test.go 941 行、jwks_translation_test.go 295 行均直接测这两个文件的函数；收益：**新增一个 policy 字段的 diff 集中在一处**，review 面小。（推断）这是"按 CRD 分文件"压倒"按机制分文件"的自觉取舍。
- **错误策略三态**：appendPolicy 闭包（backend_policies.go:151-162、traffic_plugin.go:497-525）统一"翻译出错→log+聚合 error 但不中断其余分支"；`PolicyConditionMap`（traffic_plugin.go:335-341）区分"部分翻译成功"（partial validity）与全败——**尽力翻译**而非 fail-fast，与 K8s status 条件模型对齐。
- **CEL 校验失败仍写值**（backend_policies.go:904-905 注释）：让数据面拿到显式坏值而"擦掉原值"，与 header 语义对齐——宁可运行期拒绝也不静默丢弃整个策略。
- **krt 全响应式**：整个 L03 无一个显式 reconcile 函数（对比 01 篇 gw_controller 的裸队列循环），正确性依赖各集合的 `Equals` 实现正确（如 AgwPolicy.Equals 用 protoconv.Equals，interfaces.go:61-63；ParentInfo 逐字段 Equals，interfaces.go:115-132）。（推断）这是押注 istio krt 框架的生态选择，换来的是增量重算与天然去重。

## 六、新人提示

**加一种 policy 类型的最短路径**（以 traffic 段为例）：① types.go 给 `Traffic` struct 加字段+kubebuilder 校验（agentgateway_policy_types.go）；② traffic_plugin.go 顶部加 Key 后缀常量（模式见 :60-68 的 `jwtPolicySuffix = ":jwt"`）；③ 写 `processXxxPolicy(ctx PolicyCtx, x *agentgateway.Xxx, phase, basePolicyName, policy)` 返回 `*api.Policy`（可参考 processCSRFPolicy，traffic_plugin.go:2067 最简）；④ 在 `translateTrafficPolicyToAgw` 加一个 `if traffic.Xxx != nil` 分支（:528-631 段内）；⑤ 若需条件化，包一层 `processConditional`（:1239）；⑥ api proto 已有对应 TrafficPolicySpec Kind（`api/` 下 proto 生成代码）；⑦ testdata/ 加 YAML 快照跑 golden test。backend 段同理但走 backend_policies.go:164-220 的分支表。

**调试翻译输出**：改 `testdata/<目录>/` 下 YAML + 期望 JSON，跑 `go test ./controller/pkg/agentgateway/translator/ -run TestRouteCollection`（golden_test.go:50）；要看全量 IR 用 `testutils.Syncer(t, ctx, ...)` 后 `ri.Outputs.Resources.List()`（golden_test.go:36-38 的模式）。syncer_bench_test.go（437 行）提供性能基线。策略翻译单测直接进 plugins 包（oauth_auth_test.go:1 起 941 行是范本）。

**坑**：①policy 的最终 Key = `ns/name` + 类型后缀 + attachmentName（ClonePoliciesForTarget，traffic_plugin.go:473），排查 IR 重复/丢失先看这三段拼接；②AgentgatewayModel 在 HTTPRoute 里是"选择器不是后端"（route_collections.go:484 注释），模型服务规则的 BackendRefs 会被清空重写，对着 CR 猜 IR 会猜错；③CEL 表达式在控制面校验（isCEL，traffic_plugin.go:2201）失败不阻止写入（backend_policies.go:904），别指望控制面拦住所有坏表达式——数据面还有一层 cel 求值栈（L10）；④`Models` 集合默认 disabled（collection.go:223），本地起测试忘了 `EnableAgentgatewayModels`（golden_test.go:67 TestModels 里有置位）会看到模型翻译"完全不跑"；⑤MCP 认证的 JWKS 是异步拉取的，`InlineForOwner` 在 keyset 未就绪时返回错误（jwks/lookup.go:31-34），翻译期报错不代表配置错——等 fetch 完成会自愈。
