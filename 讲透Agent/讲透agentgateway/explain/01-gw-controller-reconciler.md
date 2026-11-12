# 01 · gw_controller.go：reconcile 主循环——控制面的心脏

> 源码基线：`/usr-data/data2/repos/aaif-projects/repos/agentgateway/controller/pkg/controller/gw_controller.go`（619 行）。同链路支撑文件均在本文以行号锚实证。
>
> **勘误（任务书 vs 源码，按源码为准）**：①任务书称 `agentgateway_parameters.go` 为"同包支撑"——实际它在 `controller/pkg/deployer/` 包（`agentgateway_parameters.go:1` `package deployer`），由 gw_controller 经 `r.gwParams`（gw_controller.go:50）间接消费；②任务书提到"finalizer"——全 controller 模块 grep `Finalizer` **零命中**（含测试），本控制器的删除清理完全依赖 ownerReferences 垃圾回收（deployer.go:284、agentgateway_parameters.go:679）而非 finalizer 模式；③"SessionKeys 缓存"实为"缓存 miss 时让 API server 仲裁"的策略（agentgateway_parameters.go:637-639 注释），下文详述。

## 一、角色定位（16 层架构 L04；AgentGateway CR 到部署的完整生命周期归属）

在 understand 图谱的 16 层架构中，本文件属 **L04「控制面核心：reconciler 与 xDS 下发」**（462 节点，层摘要原文："controller/ 的 reconciler 装配与 GatewayClass 管理、setup/ 启动装配、deployer/ 通过 Helm 部署网关实例、syncer/ 将 krt…"）。图谱边实证其枢纽地位：`file:controller/pkg/setup/setup.go`、`file:controller/pkg/admin/server.go` 均 imports 指向本文件（4 条入边），出边 74 条——铺向 deployer 全家（deployer.go、agentgateway_parameters.go、gateway_parameters.go、charts.go、tls.go、values*.go）、apiclient、pluginsdk/collections 及 `api/v1alpha1/agentgateway` 的 12 个 CRD 类型文件。

一句话定位：**它是 Gateway CR 的全生命周期持有者**——从 watch 到翻译入队、从 helm 渲染到 SSA 落地、从 SessionKey 密钥仲裁到 status 地址回填，K8s 声明式世界（Gateway CR）与数据面世界（跑着 Rust 代理的 Pod）之间的一切状态收敛都由这 619 行驱动。它与 L03 翻译引擎（translator）的分界线很清晰：L03 把 Route/Policy 翻成 xDS IR 交给 syncer 推给代理，而本文件只负责"把网关实例本身部署出来并接上 xDS"——即 IR 集合 `GatewaysForDeployer` 的消费端之一（gw_controller.go:216）。

结构上它是一个非典型的 reconciler：不用 controller-runtime 的 `Reconciler` 接口，而是实现 istio `controllers.Queue` 驱动的裸循环（gw_controller.go:67、102），同时用 `var _ manager.LeaderElectionRunnable = (*gatewayReconciler)(nil)`（gw_controller.go:46）+ `NeedLeaderElection() bool` 返回 true（gw_controller.go:234-236）保证多副本下仅 leader 跑队列——这是 Istio 生态的惯用法，而非 upstream gateway-api 的 controller-runtime 标准件。

## 二、内部结构（reconcile 分段精讲）

### 2.1 事件入口：七类触发源汇入一条队列

`NewGatewayReconciler`（gw_controller.go:70-231）是全部接线的集散地：

1. **Gateway 自身**：handler 对 Update 事件做双层过滤——只有 `GetGeneration()` 变化（gw_controller.go:112，spec 变更）或 annotations 变化（gw_controller.go:118，`maps.Equal` 比较）才入队，纯 status 抖动被丢弃（gw_controller.go:123 "skip reconciling Gateway with no relevant changes"）。
2. **GatewayClass**：先按 `ControllerName` 过滤"是不是我们的类"（gw_controller.go:139），再全命名空间 List 出引用该类的 Gateway 逐个入队（gw_controller.go:142-148）。
3. **AgentgatewayParameters（AGWP）**：为避免 O(Gateway×AGWP) 全量扫描，建了两个 kclient 索引——`parametersRef`（gw_controller.go:152-158，取自 `gw.Spec.Infrastructure.ParametersRef`，提取函数 gw_controller.go:602-613）和 `gatewayClass`（gw_controller.go:159-162，提取函数 gw_controller.go:615-619）。AGWP 变更时走两级查找：先 `gatewaysByParamsRef.Lookup` 直连（gw_controller.go:170），再遍历 GatewayClass 找引用该 AGWP 的类、经 `gatewaysByClass.Lookup` 间连（gw_controller.go:178-196）。
4. **子对象回流**：`EnqueueForParentHandler(r.queue, gvk.KubernetesGateway)`（gw_controller.go:204）一次性挂到 Deployment/DaemonSet/ServiceAccount/Service/ConfigMap/Secret 六个 client（gw_controller.go:205-210）——手工改了生成的 Deployment 会被立即纠正回来。
5. **IR 变更**：`cfg.AgwCollections.GatewaysForDeployer.Register`（gw_controller.go:216-221），注释给出两个理由：不 Fetch 该集合所以要防陈旧引用；ListenerSet 加端口时要把新端口部署进 Service（gw_controller.go:212-215）。
6. **扩展点**：`controllerExtension.Register(r.queue, agwParamEventHandler)`（gw_controller.go:224）。
7. **xDS TLS 证书轮换**：`setupTLSCertificateWatch`（gw_controller.go:228，详见 2.5）。

队列本身：`controllers.NewQueue("GatewayController", WithReconciler(r.Reconcile), WithMaxAttempts(math.MaxInt), WithRateLimiter(rateLimiter))`（gw_controller.go:102）——**无限重试**配上 controller.go:18-22 的组合限流器（每项指数退避 500ms→10s + 全局令牌桶 10qps/100 burst），意味着 reconcile 里返回 err 永远安全，代价只是退避。

`Start`（gw_controller.go:239-282）先 `WaitForCacheSync` 九个 client 外加 `gwParams.GetCacheSyncHandlers()`（gw_controller.go:253-256，deployer 包的 agwParam/gwClass/secret/MeshConfig informer 同步，见 agentgateway_parameters.go:502-508），再 `r.queue.Run`（gw_controller.go:260），退出时 `ShutdownAll`（gw_controller.go:277）。

### 2.2 Reconcile 主体：一次调用的完整分段

`Reconcile(req types.NamespacedName)`（gw_controller.go:284-411）：

- **门卫段**（285-303）：缓存里取不到 Gateway 或带 DeletionTimestamp 直接返回 nil（gw_controller.go:286-290）；GatewayClass 不存在报错触发退避重试（gw_controller.go:293-296）；`ControllerName` 不是本控制器直接不管（gw_controller.go:299-303）。
- **指标段**（304-306）：`defer recordReconciliation("gateway", rErr)`（gw_controller.go:305）——无论走到哪层 return 都计入 `controller_reconciliations_total{controller,result}`（metrics.go:23-35）。
- **渲染段**（310-358）：`r.deployer.GetObjsToDeploy(ctx, gw)`（gw_controller.go:310）一次完成 values 生成→helm 渲染→overlays 后处理（deployer.go:199-231，PostProcessor 钩子在 deployer.go:222-228）。错误分三路：`ErrNoValidPorts`（gw_controller.go:312-315）**不写 status 直接返回 err**，注释明言"status is reported from translator"——端口无效是翻译层已报告过的配置问题；`ErrSessionKey`（gw_controller.go:316-329）写 `Programmed=False/DeploymentFailed`——注释强调"是部署问题而非网关配置无效"；其余一律 `Accepted=False/InvalidParameters`（gw_controller.go:333-343）。成功路径还有一段**状态自愈**：若此前因 InvalidParameters 置过 False，现在置回 `Accepted=True`（gw_controller.go:344-358）。
- **落地段**（359-379）：`SetNamespaceAndOwnerWithGVK` 打 ownerRef（gw_controller.go:359；deployer.go:268-295，`Controller: new(true)` 在 deployer.go:284）→ `DeployObjsWithSource` SSA 应用（gw_controller.go:360）→ 成功后 `PruneRemovedResources` 清理不再期望的 PDB/HPA/VPA/旧 workload（gw_controller.go:361-366；目标 GVK 表 deployer.go:406-412）。部署失败则 `Programmed=False/DeploymentFailed`（gw_controller.go:367-379）。
- **地址回填段**（380-408）：先做 Programmed 状态自愈（gw_controller.go:380-393），再从 objs 里捞出第一个 Service（gw_controller.go:398-403），调 `updateStatus`（gw_controller.go:405）。

### 2.3 status 上报：条件 + 地址两套独立机制

条件更新走 `updateGatewayStatusWithRetry`（gw_controller.go:545-555）→ 通用函数 `updateGatewayStatusWithRetryFunc`（gw_controller.go:491-518）：`utilretry.RetryOnConflict` 包住"取最新→改→`UpdateStatusNoResponse`"（gw_controller.go:496、507），冲突自动重试——这是对抗 status 子资源热竞争的标准姿势。

地址更新 `updateStatus`（gw_controller.go:413-440）有个容易忽略的细节：取到 Service 后还要验属主——`metav1.GetControllerOf(svc)` 为 nil（用户自带 Service，unmanaged 场景）或 `gw.UID != controller.UID`（gw_controller.go:427-434）都直接放弃，防止把别人的地址抄到自己 status 上。地址计算 `getDesiredAddresses`（gw_controller.go:442-486）：LoadBalancer 型 Service 优先取 Ingress（hostname 优先于 IP，gw_controller.go:446-457 与 584-600）；否则取 ClusterIP/ClusterIPs（gw_controller.go:460-472）；最后追加 `gw.Spec.Addresses` 里用户手写的地址并去重（gw_controller.go:475-483）。真正写回前用 `slices.EqualFunc` 判等免写（gw_controller.go:531-535）。

### 2.4 两级 AGWP 合并：GatewayClass 先、Gateway 后

参数解析的真正实现在 deployer 包 `agentgatewayParametersHelmValuesGenerator.resolveParameters`（agentgateway_parameters.go:442-487）：先看 GatewayClass 的 `spec.parametersRef`（agentgateway_parameters.go:446-466，非 AGWP 类型直接报错 463-465），再看 Gateway 的 `spec.infrastructure.parametersRef`（agentgateway_parameters.go:469-484，同样强校验类型）。两层结果装进 `resolvedParameters{gatewayClassAGWP, gatewayAGWP}`（agentgateway_parameters.go:351-356），`layers()` 固定返回 `[GatewayClass, Gateway]` 顺序（agentgateway_parameters.go:364-373）。

合并分两个通道，**顺序都严格 GWC 先、GW 后**：

- **values 通道**：`GetValues` 里先 `NewAgentgatewayParametersApplier(resolved.gatewayClassAGWP).ApplyToHelmValues(vals)` 再对 gatewayAGWP 来一遍（agentgateway_parameters.go:301-310，注释原文 "Apply AGWP Configs in order: GatewayClass first, then Gateway on top. This allows Gateway-level configs to override GatewayClass-level configs"）。`ApplyToHelmValues`（agentgateway_parameters.go:131-196）对 resources/Istio 做逐字段合并而非整体覆盖——注释举例"GWC 设 limits、GW 只设 requests"时两边都要保住（agentgateway_parameters.go:160-162、164-165）；env 合并 `mergeEnvVars` 同名后者胜（agentgateway_parameters.go:201-226）。`ModelCatalog` 只认 Gateway 级 AGWP（agentgateway_parameters.go:314-316，注释解释 ConfigMap 引用是部署相对路径，两级会有歧义）。
- **overlay 通道**：渲染后 `PostProcessObjects`（gateway_parameters.go:120-174）用 `strategicpatch.NewLayeredOverlayApplier(resolved.gatewayClassAGWP, resolved.gatewayAGWP)` 分层应用 strategic-merge-patch（gateway_parameters.go:161-164），紧跟 `sessionKeys.Apply`（gateway_parameters.go:168）。

两通道之间还有防线：`validateWorkloadOverlays`（agentgateway_parameters.go:394-422）按"最终生效的 workload kind"（由 `resolveWorkloadKind` 沿 layers 取**最后一个非空值**，agentgateway_parameters.go:375-392）校验任何一层的 overlay 不得与最终 kind 矛盾——比如最终是 DaemonSet 却有人配了 HPA overlay，直接报错（agentgateway_parameters.go:415-417）。

### 2.5 SessionKeys 冲突仲裁与证书 watch

**SessionKey**（代理加密 session ID 的对称密钥）的仲裁逻辑是全文件最精妙的一段。`applyManagedSessionKeyDefaults`（agentgateway_parameters.go:489-500）：若用户 env 里自带 `SESSION_KEY`（`usesManagedSessionKeyEnv`，agentgateway_parameters.go:237-239）则不托管；否则设 `SessionKeySecretName = SessionKeySecretName(gatewayName)`（agentgateway_parameters.go:498-499，命名规则 agentgateway_parameters.go:581-583，超 63 字符走 sha256 截断 585-593）。

`SessionKeys.Get`（agentgateway_parameters.go:640-667）的三段式：①缓存命中→校验属主后返回；②miss→`generateSessionKey` 生成 32 字节随机数 hex（agentgateway_parameters.go:595-601、603-613 校验）→ `secrets.Create`（agentgateway_parameters.go:655）；③撞上 `IsAlreadyExists`（agentgateway_parameters.go:659）→ 放弃自己的 key，**读回既有 Secret 用它**。注释把意图说透了："The Secret's key is created but never updated. The cache can miss a Secret created by an earlier reconcile, so on a miss the API server decides which key wins rather than this reconcile overwriting it"（agentgateway_parameters.go:637-639）——**key 一旦生成就永不轮换**，用 APIServer 的 create 原子性当分布式锁，避免两个 reconcile 各拿一把 key 导致新旧 Pod 会话互解不了。属主层面同理宽柔：Secret 存在但 controllerRef 的 UID 与当前 Gateway 不同（重建同名 Gateway 的场景）时，只要 Kind/Name 匹配就静默领养（agentgateway_parameters.go:697-725），只有连 Kind/Name 都不对才报"controlled by别人"（agentgateway_parameters.go:706-711）。最后 `AddSessionKeyChecksum` 把 key 的 sha256 写进 Pod template 注解 `checksum/session-key`（gateway_parameters.go:53、192-211），key 若真变了，Deployment 滚动重启跟上。

**证书 watch**：`setupTLSCertificateWatch`（gw_controller.go:560-582）向 `CertificateWatcher`（接口定义 start.go:52-54，仅一个 `RegisterCallback(func(tls.Certificate))`）注册回调——证书轮换时 List 全部 Gateway、按 ControllerName 过滤（gw_controller.go:576）后全量入队（gw_controller.go:578）。下游消费在 values 生成期：`XdsTLS` 开启时从 Secret 抽 CA 证书注入 helm values（agentgateway_parameters.go:326-342，`extractXdsCACertificate`/`injectXdsCACertificate` 在 tls.go:24、tls.go:10），让数据面代理能验证控制面 xDS 端点。

## 三、外部连接（上游 CRD watch/下游 deployer+syncer/证书 jwks 衔接）

- **上游（入边）**：图谱 4 条 imports 入边——`setup/setup.go` 是装配方（`watchGw` 在 controller.go:67-105 里 `NewGatewayParameters`→`NewGatewayDeployer`→`NewGatewayReconciler` 串成链，最后 `cfg.Mgr.Add` 注册进 manager，controller.go:88-104）；`admin/server.go`、`agentgateway/testutils/util.go`、`start_test.go` 是消费/测试方。watch 的 CRD 类型来自 L02 层：`api/v1alpha1/agentgateway` 12 个类型文件（图谱出边）。
- **下游（deployer 线）**：Reconcile 只调四个 deployer 方法——`GetObjsToDeploy`（渲染）、`SetNamespaceAndOwnerWithGVK`（属主）、`DeployObjsWithSource`（SSA 落地）、`PruneRemovedResources`（剪枝）。`DeployObjsWithSource`（deployer.go:301-386）逐对象做属主预检：已有对象的 controllerOf 不是本 Gateway 就拒绝（deployer.go:328-339，错误文案 "resource already exists and is not controlled by…" 在 deployer.go:336）；然后清掉 resourceVersion/generation/UID/managedFields/status 等 APIServer 管理字段后 `Semantic.DeepEqual` 判等，相等则跳过 patch（deployer.go:342-363）；真正落地走 `applyPatch`——`types.ApplyPatchType` + `Force: new(true)` + `FieldManager: agwControllerName`（deployer.go:113-117，由 deployer.go:381 调用）。
- **下游（syncer 线，间接）**：本文件不直接碰 syncer，但共享同一 `AgwCollections` krt 集合——`GatewaysForDeployer` 的 Register 回调（gw_controller.go:216）与 syncer 的 xDS 推送消费同源 IR；数据面代理拿到的 xDS 地址/端口/TLS 正是本文件部署时写进 values 的 `Xds.Host/Port/Tls`（agentgateway_parameters.go:547-553）。L04 层摘要把两者并列 ("deployer/ 通过 Helm 部署网关实例、syncer/ 将 krt…"）即为这层关系。
- **证书/jwks 衔接（按源码澄清）**：gw_controller 与证书的唯一交集是 xDS 控制面 CA（见 2.5）；**jwks 不在本文件链路上**——它由 start.go 装配进翻译插件（`JWKSLookup jwks.Lookup` start.go:78、`Plugins(...)` start.go:170-176），属 L03 翻译线。任务书"证书 jwks 衔接"应理解为两条平行的证书通道，不可混为一谈。

## 四、数据流（一次 CR 变更到 Gateway Pod 运行新配置的完整路径)

以"用户给 Gateway 加了一个 8443 listener"为例：

```
用户 kubectl edit Gateway（加 listener 8443）
  → APIServer bump generation
  → gwClient informer 收到 EventUpdate，GetGeneration 变化 → queue.AddObject      (gw_controller.go:112-115)
  → queue（指数退避限流 controller.go:18-22）弹出 → Reconcile                      (gw_controller.go:284)
  → 门卫三查：存在/未删/是我们的类                                              (gw_controller.go:286-303)
  → deployer.GetObjsToDeploy:
      resolveParameters 两级 AGWP（GWC 先 GW 后）                                  (agentgateway_parameters.go:442-487)
      getDefaultAgentgatewayHelmValues: 从 IR GatewaysForDeployer 取端口集合       (agentgateway_parameters.go:533-538, 516-532)
      ApplyToHelmValues ×2（逐字段合并）+ Istio/SPIFFE 决议 + SessionKey 默认       (agentgateway_parameters.go:301-324)
      RenderManifest: helm install --dry-run=client（内存 driver，零真实 IO）      (deployer.go:158-184)
      PostProcessObjects: 分层 strategic patch overlays + SessionKeys.Apply        (gateway_parameters.go:161-169)
  → SetNamespaceAndOwnerWithGVK: 全部对象挂 Gateway controller ownerRef            (deployer.go:268-295)
  → DeployObjsWithSource: 属主预检→DeepEqual 判等跳过→SSA apply(Force)             (deployer.go:328-381)
      Service 多了 8443 端口，Deployment template 未变则跳过 patch
  → PruneRemovedResources: 按 GatewayNameLabel + controller ownerRef 剪掉多余资源   (deployer.go:391-477)
  → updateStatus: 从 Service 回填 addresses（属主校验后）                           (gw_controller.go:405, 413-440)
  → Pod 层面：Service 变更即刻生效；template 若变（如端口注入容器）Deployment 滚动
  → 数据面新 Pod 起来后向 xDS server（部署时写死的 Xds.Host/Port）发起 ADS 订阅
  → syncer 从 krt IR（L03 翻译产物）推 xDS 配置 → 代理开始在新端口收流量
```

注意分工：**端口属于部署期**（helm values → Service/container ports，由本文件负责），**路由/后端/策略属于运行期**（xDS 推送，由 translator+syncer 负责）。改 listener 端口两边都会动，改 HTTPRoute 只有后者动、本文件只在 `GatewaysForDeployer` 变化时被动同步（gw_controller.go:216）。

## 五、设计决策（有注释用注释，无则标"推断"）

1. **两级合并为何存在**——注释直说：AgentgatewayParameters 既能挂在 GatewayClass（集群级基线）也能挂在 Gateway（实例级覆盖），`layers()` 顺序保证"GWC 先、GW 后"（agentgateway_parameters.go:301-302、369-372）；resources/Istio 逐字段合并的注释给出动机："preserve values from GatewayClass AGWP when Gateway AGWP only sets some fields (e.g., GWC sets limits, GW sets requests)"（agentgateway_parameters.go:160-161）。ModelCatalog 只认 Gateway 级是防歧义："they resolve from the Gateway's namespace… so the reference is always unambiguous"（agentgateway_parameters.go:311-313）。`ApplyToHelmValues` 开头的 DeepCopy 注释（agentgateway_parameters.go:136-139）记录了一个真实踩坑：不拷贝的话第一层 Apply 会把 GWC 缓存对象的 map 原地改掉。
2. **只借 helm 渲染、不用 helm 部署**——注释原文："We render a helm chart, but we do not use helm beyond that point."（agentgateway_parameters.go:129-130）。渲染用内存 driver + `DryRunStrategy = action.DryRunClient`（deployer.go:158、170），注释解释这是为了保证"no i/o … essentially guarantees that this function terminates quickly and doesn't block the rest of the controller"（deployer.go:167-169）——helm 只当模板引擎，状态管理全交给 SSA。release 名干脆用占位符 `"release-name-placeholder"`（gateway_parameters.go:236-240，注释 "A helm release is never installed, only a template is generated"）。
3. **SSA + Force 与属主预检的取舍**——`applyPatch` 用 `Force: new(true)` 抢字段所有权（deployer.go:114），配 `FieldManager=agwControllerName`；但 Force 之前先在 deployer.go:328-339 检查整对象归属，宁拒不抢。（推断：Force 只应作用于"本控制器生成的对象内字段冲突"，跨对象归属冲突必须硬失败，否则会把用户手动创建的同名资源字段洗掉。）DeepEqual 预检（deployer.go:357）则是省 APIServer 写放大。
4. **无 finalizer 的清理模型**——源码事实：零 finalizer，全部清理靠 ownerReferences（deployer.go:284 的 controller ownerRef + GC）加主动 prune（deployer.go:391）。SessionKey Secret 也走 ownerRef（agentgateway_parameters.go:679）。（推断：AGWP/ListenerSet 等无外部资源需要"删除前兜底"，纯 K8s 资源 GC 足够，finalizer 反而增加卡死风险。）
5. **SessionKey 永不更新的取舍**——agentgateway_parameters.go:637-639 注释（引文见 2.5）：可用性优先于密钥轮换——两把 key 并存比轮换中断更糟；key 泄露时用户可自带 `SESSION_KEY` env 接管（agentgateway_parameters.go:237-239）再删 Secret 重建，作为人工轮换通道（推断：这是逃生门而非自动机制）。
6. **队列无限重试 + 全局限流**——`WithMaxAttempts(math.MaxInt)`（gw_controller.go:102）（推断：配合分路 status 上报，err 重试对用户可见性无损；真正致命的错误都会在 status condition 里体现，不会无限打转）。`ErrNoValidPorts` 不写 status 是因为 translator 已报告（gw_controller.go:313 注释），避免双写打架。

## 六、新人提示（改 CR 字段的最小路径/调试 reconcile/坑）

**改一个 CR 字段的最小路径**（以"给 AGWP 加一个 values 字段"为例）：①`api/v1alpha1/agentgateway/agentgateway_parameters_types.go` 加类型 + zz_generate deepcopy；②`deployer/values.go` 的 `HelmConfig`/`AgentgatewayHelmGateway` 加镜像字段；③`agentgateway_parameters.go:144-195` 的 `ApplyToHelmValues` 加一行 `setIfNonNil`；④helm chart 模板（install/helm）加渲染。reconciler 本身几乎从不需要动——它的分发是通用的。**反过来**：想让某字段变化触发重部署，检查它是否影响 helm values——SSA 链路自动覆盖；若只影响 xDS，走 translator/syncer 线。

**调试 reconcile**：
- 日志 logger 名 `gateway-controller`（gw_controller.go:44），debug 级有完整决策痕迹——每条入队原因（"due to generation change" gw_controller.go:113、"due to AgentgatewayParameters change via GatewayClass" gw_controller.go:191）、跳过原因（gw_controller.go:123）、deployer 的 values dump（deployer.go:208-213）与"object unchanged, skipping apply"（deployer.go:358）。
- 本地验证渲染不必装集群：`GetGvksToWatch` 的思路（deployer.go:511-546 用占位 Gateway 渲染一遍看产物）可以直接抄成调试脚本。
- 状态排障先看两个 condition：`Accepted=False/InvalidParameters` → AGWP 解析/合并炸了（回看 gw_controller.go:333-343 链路）；`Programmed=False/DeploymentFailed` → SSA/session key/属主冲突（gw_controller.go:316-329、367-379）。

**坑**：
- **改 status 不会触发本控制器 reconcile**（generation 不变，gw_controller.go:112），但会触发 EnqueueForParent 的子对象事件——调 status 死循环不会发生，但别指望靠改 status 驱动逻辑。
- **同 namespace 重建同名 Gateway**：UID 变了，属主预检会拒绝部署（deployer.go:332-338 按 sourceGVK+Name 判 ownedBySource，Name 相同即放行——真正卡住的是 SessionKey 领养分支 agentgateway_parameters.go:706-711 只认 Kind/Name 不认 UID，会静默改 ownerRef）。旧对象 GC 完成前的新部署是灰色窗口。
- **手改生成的 Deployment 会被回滚**（gw_controller.go:204-210 父对象回流），自定义需求走 AGWP overlay（strategicpatch），别碰生成物。
- **AGWP 类型错误是硬失败**：parametersRef 指向非 AgentgatewayParameters 类型直接报错（agentgateway_parameters.go:463-465、482-483），没有 fallback。
- **helm 渲染是每次 reconcile 全量重跑的**（deployer.go:199-231），往 chart 里塞昂贵的模板函数（lookup 之类）前先想清楚——`DryRunClient` 挡不住模板本身的计算成本。
- 图谱 worker 曾把本文件归入"controller 包含 finalizer"的直觉印象——源码 grep 证伪；读这类 reconciler 时先确认清理模型（ownerRef GC vs finalizer）再动手，是避免加错 finalizer 的第一课。

---

*行号锚经 `sed -n '<N>p>'` 逐条核对于源码：写盘前批量自验 98/98 PASS，写盘后终验全文 224 个唯一 file:line 锚零越界。图谱引用自 `.understand-anything/knowledge-graph.json`（L04 层、file:function 节点与 imports 边）。*
