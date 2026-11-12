# 08 · controller 装配中枢与 Gateway 总装线：从事件级联到 700KB×8 分片

## 一、角色定位

`internal/controller` 是 K8s 控制面：controller.go:120 的 `StartControllers` 是装配中枢，构造全部 reconciler 并建立"后端变更逐级向上触发"的事件拓扑；gateway.go（1598 行）是总装线——一个 Gateway 引用的全部 AIGatewayRoute/MCPRoute/BSP/GatewayConfig 在此聚合编译成 filterconfig Config，经 Secret 分片下发，再滚动 Envoy 网关 Pod 生效。它不直接碰 xDS：产物是 Envoy Gateway 认识的 HTTPRoute/注解/Secret，xDS 层留给 extensionserver（11 篇）。

## 二、内部结构

**装配中枢（controller.go:120）**：先建 11 个字段索引（controller.go:123 与 :301）；再按序装配：Gateway 控制器挂 gatewayEventChan（controller.go:133）；AIGatewayRoute 控制器 `Owns` HTTPRoute/HTTPRouteFilter 并收 route 事件（controller.go:155）；backend/BSP 逐级上抛（controller.go:169/:182）；InferencePool 先探测 CRD 存在再建（controller.go:193，缺 CRD 只 Info）；Secret 控制器**故意不用**共用 builder——controller.go:224 注释说明 Secret 内容变化不改 generation，GenerationChangedPredicate（controller.go:298）会吞事件；QuotaPolicy 仅当 RateLimitRunner 非空（controller.go:253）；mutating webhook `/mutate`（controller.go:275）与 gateway reconciler 共享同一个 extProcBuilder（controller.go:134 注释：两边必须算出同一模板 hash，构造器 extproc_builder.go:39）。泛型 handleFinalizer（controller.go:634）管 finalizer 与删除传播。

**总装线 Reconcile（gateway.go:94）**：列路由/MCPRoute（gateway.go:103/:108，MCPRoute 按创建时间排序保确定性 gateway.go:114）；getObjectsForGateway 按 EG 的 owning-gateway 标签在两个候选 namespace 找 pods/deployments/ds（gateway.go:1444），Pod 未就绪 requeue 5s（gateway.go:129）；fetchGatewayConfig 经注解取 GatewayConfig（gateway.go:1577，键在 ai_gateway_route.go:65）；stampGatewayConfigHash（gateway.go:1544）把 GatewayConfig spec 的 sha256 前 8 字节写进 Gateway 注解——gateway.go:146 注释道破动机：**EG 不 watch GatewayConfig，改配置必须借 Gateway 这个 EG 认识的资源触发重翻译**；序列化特意用 stdjson 保 byte 稳定哈希（gateway.go:13 注释）。

**reconcileFilterConfigSecret（gateway.go:396）**：每条路由两遍扫描——先收模型清单（命中 `x-ai-eg-model` 精确匹配 header，gateway.go:453），再收后端：跨命名空间先过 ReferenceGrant，拒绝即剔该后端（gateway.go:494）；InferencePool 假定 OpenAI schema（gateway.go:511）；Header/BodyMutation 路由级覆盖后端级（mergeHeaderMutations gateway.go:337、mergeBodyMutations gateway.go:290）；多 BSP 挂同一后端直接报错（gateway.go:1200，安全考虑）；凭证经 bspToFilterAPIBackendAuth（gateway.go:908）六分支翻译，AWS 走默认链时不读 Secret（gateway.go:942，IRSA 场景注释 gateway.go:965）；credentialOverride 输入头追加进 remove 列表防凭证上 wire（gateway.go:816）；MCPConfig 编译（mcpConfig gateway.go:634：VerifiedJWT 只在 OAuth 配了才为真 gateway.go:693、BackendSelector 复用授权引擎 gateway.go:761、两类身份头去重合并 gateway.go:777）；最后 yaml.Marshal→writeFilterConfigBundle（gateway.go:623）。

**分片与滚动**：filter_config_bundle.go 每片 700KB（filter_config_bundle.go:25）、固定 8 槽（filter_config_bundle.go:28，注释：槽位固定才不引起重新挂载）、超槽报错（filter_config_bundle.go:49）、多余片删除（filter_config_bundle.go:63）、索引 Secret 带 checksum/UUID（filter_config_bundle.go:52）。annotateGatewayPods（gateway.go:1334）：rollout 进行中先 requeue（isRolloutInProgress gateway.go:1301）；Pod 混侧车状态强制自愈（gateway.go:1366）；逐 Pod patch UUID 注解（gateway.go:1380，注释 gateway.go:1333 引用外部文章——K8s 挂载 Secret 刷新延迟的已知加速 hack）；hash 写进 pod template 注解（gateway.go:1398）让 Kubernetes 掌管滚动节奏。

## 三、外部连接

- **aigw run**：同一条翻译链在 fake client 上复刻（run.go:304 translateCustomResourceObjects、run.go:183 起 extensionserver），单机与生产共用 reconciler。
- **extproc**：分片 Secret 经卷挂载被 filterapi watcher 轮询重组（01 篇）。
- **rotators**：BSP 翻译读的 Secret 由 09 篇轮换器保鲜。
- **Envoy Gateway**：产物交给 EG；quota hash 注解（ai_gateway_route.go:58）与 GatewayConfig hash 同为"让 EG 重翻译"的触发器。

## 四、数据流

一次配置变更旅程：apply BSP/AIServiceBackend/AIGatewayRoute → 事件沿 backend→route→gateway 通道级联（如 backend_security_policy.go:385 向下游发 GenericEvent）→ GatewayController.Reconcile 总装：聚合（拒者剔除、mutation 合并、凭证内联）→ 分片写 Secret → stamp hash → annotate Pods → K8s 滚动 Envoy Pod → 新 Secret 被 extproc watcher 拾取。删除经 handleFinalizer 反向传播。

## 五、设计决策

1. **双通道触发翻译**：EG 只认 Gateway/HTTPRoute，"我们 CRD 的变更"被换算成"EG 资源的变更"——GatewayConfig hash 写 Gateway（gateway.go:1544）、QuotaPolicy hash 写 HTTPRoute（ai_gateway_route.go:51 注释讲透 no-op update 陷阱）。读懂这两个注解就读懂控制面与 EG 的耦合面。
2. **失败跳过而非全盘失败**：单后端解析失败只丢弃继续装（gateway.go:504/:536），但 isCtxErr（gateway.go:391 注释）区分"context 取消要返回"与"对象坏了要跳过"——读挂了还继续会发布缺后端的配置。
3. **固定 8 槽**：把"配置内容变更"与"挂载结构变更"解耦。
4. **UUID 注解 hack 有代价**：加速 Secret 刷新换来每次 reconcile 都碰 Pod。
5. **standalone 内建**：standAlone 模式跳过 Pod 检查、Secret 落空 namespace（gateway.go:127 注释）。

## 六、新人提示

改总装逻辑九成场景落在 reconcileFilterConfigSecret 与 mcpConfig 两函数；测试 gateway_test.go 与 tests/controller（envtest）。排障三步：看 CR 的 NotAccepted condition（newConditions controller.go:607 只有两态）→ 看 filterconfig Secret 各分片内容是否含目标后端 → 看 Envoy Pod 模板注解 hash 是否更新。坑：别给 Secret 控制器套 GenerationChangedPredicate（controller.go:224）；GatewayConfig 查不到只降级默认不报错（gateway.go:1586），"改配置没生效"先核对注解名与 namespace。
