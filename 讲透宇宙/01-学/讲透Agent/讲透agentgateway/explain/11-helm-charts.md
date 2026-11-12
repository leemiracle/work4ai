# 11 · 三套 Helm chart：从 K8s 全托管到 standalone 数据面

> 源码基线：`/usr-data/data2/repos/aaif-projects/repos/agentgateway/controller/install/helm/`（三套发布 chart）与 `controller/pkg/helm/`（Go 内嵌数据面 chart）。图谱 L16「部署交付与 CI 基础设施」。
>
> **勘误（任务书 vs 源码，按源码为准）**：①任务书把「CRD 巨型模板 + 工作负载 Deployment/Daemonset 互斥 + configmap 三段合并」都归给主 chart——实际主 chart **不含任何 CRD 模板与 ConfigMap 模板**（`install/helm/agentgateway/templates/` 仅 10 个文件，无 crds、无 configmap），CRD 巨型模板在独立的 `agentgateway-crds` chart；Deployment/DaemonSet 互斥与 configmap 合并渲染都在**第四套** chart——Go 内嵌的 `pkg/helm/agentgateway/`（`templates/daemonset.yaml:2`、`templates/configmap.yaml:12-39`）；②任务书称「values 空壳默认值在 Go 侧 gateway_parameters.go loadChart 注入」——`loadChart`（charts.go:16-28）只装 chart 并注入**版本号**，真正的默认值注入在 `agentgateway_parameters.go:533-578` 的 `getDefaultAgentgatewayHelmValues`；③任务书「checksum 注解只哈希部分 configmap」是 **standalone chart** 的行为（`_helpers.tpl:176-181` startupConfig 剔除 modelCatalog），内嵌 chart 的 `checksum/config` 哈希的是**整个** configmap 模板（`_helpers.tpl:94`）；④主 chart `templates/deployment.yaml:120-121` 注释引用的 `pkg/deployer/wellknown.go` 的 `AgentgatewayDefaultTag` **在全仓 Go 代码中零命中**（grep 实证）——过期注释，kgateway 上游遗产，实际默认镜像机制是 `AGW_PROXY_IMAGE_*` env（deployment.yaml:103-111）→ `settings.go:236-241`。

这四套 chart 构成一条**部署形态光谱**：

| chart | 位置 | 部署什么 | 谁运行它 |
|---|---|---|---|
| agentgateway | install/helm/agentgateway | controller 控制面 | 用户 `helm install` |
| agentgateway-crds | install/helm/agentgateway-crds | 4 个 CRD | 用户 `helm install` |
| agentgateway-standalone | install/helm/agentgateway-standalone | 无控制面的数据面 | 用户 `helm install` |
| agentgateway（内部） | pkg/helm/agentgateway | 每个 Gateway 的数据面工作负载 | **controller 进程内**渲染 |

## 一、角色定位（L16；部署形态光谱：全托管 / 独立数据面 / CRD 独立分发）

在 understand 图谱 16 层架构中，这些文件全部归 **L16 部署交付与 CI 基础设施**（图谱节点 `config:controller/install/helm/...` 与 `file:controller/pkg/helm/embed.go` 均挂此层）。它们是仓库与最终用户之间的唯一交付界面：Makefile 的 `CHART_NAMES := agentgateway agentgateway-crds agentgateway-standalone`（Makefile:537）圈定三套对外发布物，`release-charts` 目标以 `--version $(HELM_CHART_VERSION_V) --app-version $(HELM_CHART_VERSION_V)` 双写版本后 `helm push` 到 OCI registry（Makefile:540-545）；第四套内嵌 chart 则永远不发布，编译进 controller 二进制（embed.go:8-9 `//go:embed all:agentgateway`）。

四者的分工哲学是**控制面与数据面的解耦度递减**：

- **agentgateway 主 chart**＝K8s 全托管形态。只装 controller（`templates/deployment.yaml:2` 固定 `kind: Deployment`），数据面 Pod 由 controller 按每个 Gateway CR 动态渲染内嵌 chart 生成（见数据流节）。
- **agentgateway-crds**＝CRD 独立分发。4 个 CRD 模板合计 35,726 行（wc 实证：agentgatewaybackends 17,216 / policies 11,567 / models 5,903 / parameters 1,040），全部由 controller-gen 生成——模板头部标注 `controller-gen.kubebuilder.io/version: v0.20.0`（agentgateway.dev_agentgatewayparameters.yaml:6），且 `make clean-gen` 会直接删除这批文件重新生成（Makefile:342 `rm -f install/helm/agentgateway-crds/templates/agentgateway.dev_*.yaml`），**勿手改**。独立成 chart 而非塞进主 chart 的 `crds/` 目录，推断依据是 Makefile 的独立部署目标用 `helm upgrade --install agentgateway-crds`（Makefile:571）——`crds/` 目录内的 CRD 在 `helm upgrade` 时永不更新，独立 chart 才能随版本演进升级 CRD（此为 Helm 生态通行约束，仓内无明文注释，标注为推断+工具行为）。
- **agentgateway-standalone**＝无 K8s API 依赖的数据面独立部署。装一个直接读本地 ConfigMap 文件的 agentgateway 代理（`templates/deployment.yaml:69-71` 容器 args `-f /config/config.yaml`），没有 xDS、没有 controller、没有 RBAC（templates/ 目录 10 个文件中**无 role.yaml**——与主 chart 的关键差异，批 49 发现属实；serviceaccount.yaml 仅 416 字节，不挂任何规则）。
- **内嵌 chart**＝controller 的渲染模板库。values.yaml 只有一行注释 `# Defaults are set in the Go code`（pkg/helm/agentgateway/values.yaml:1，全文件 0 行有效内容）——默认值全部在 Go 侧构造。

版本纪律上，三套发布 chart 的 `appVersion` 都写死占位符 `"0.0.0-dev"`，注释明言真实版本由 Makefile release-charts 在发布时注入（agentgateway/Chart.yaml:8-11、agentgateway-crds/Chart.yaml:8-11）；standalone chart 无此注释（Chart.yaml:7-8）且版本号落后主 chart 一个修订（0.0.1 vs 0.0.2）。内嵌 chart 则是另一条路：Chart.yaml 写 `version: 0.0.1-alpha1`/`appVersion: "2.0.0-alpha1"`（pkg/helm/agentgateway/Chart.yaml:5-6），运行时被 `loadChart` 覆写为编译版本号（charts.go:22-25 注释 "simulate what `helm package` in the Makefile does"）。

## 二、内部结构

### 2.1 主 chart：控制面的全部 K8s 资产

values.yaml 351 行、**29 个顶层键**（`grep -c '^[a-zA-Z]'` 实证，批 85/53 数据属实）。核心块是 `controller:`（values.yaml:67 起，占 67-207 行近四成篇幅）：`replicaCount: 1`（values.yaml:69）、`logLevel: info`（:75）、controller 镜像 `repository: controller`（:81）、Service 三端口 `agwGrpc: 9978 / health: 9093 / metrics: 9092`（:94-96）——9978 就是数据面回连 xDS 的 gRPC 端口。全局默认镜像 `registry: cr.agentgateway.dev`（:222）与 proxy 镜像 `repository: agentgateway`（:215）分置两处，模板里以 `controller.image.registry | default .Values.image.registry` 两级回退（deployment.yaml:66）。

`templates/deployment.yaml`（250 行）是主 chart 唯一工作负载，**没有 DaemonSet 分支**。值得逐段看的环境变量注入（92-203 行）几乎就是一份 settings.go 的字段对照表：

- **运行时自限**：`GOMEMLIMIT`/`GOMAXPROCS` 从 `resourceFieldRef` 取容器 limit（deployment.yaml:93-102）——Go 1.19+ 容器感知标配；
- **数据面镜像三件套**：`AGW_PROXY_IMAGE_REGISTRY/REPOSITORY/TAG`（:103-111）带 `{{- with }}` 空值跳过；
- **xDS 寻址**：`AGW_LOG_LEVEL`（:114）、`AGW_XDS_SERVICE_NAME` 取 `agentgateway.fullname`（:116-117）、`AGW_AGENTGATEWAY_XDS_SERVICE_PORT` 取 9978（:118-119）——这三者拼出数据面回连地址；
- **Istio mesh 五件套**：`AGW_ISTIO_AUTO_ENABLED/NAMESPACE/REVISION/CLUSTER_ID/NETWORK/CA_ADDRESS`（:125-150）；
- **feature gates**：`AGW_ENABLE_INFER_EXT`（:178-181）、`AGW_ENABLE_AGENTGATEWAY_MODELS`（:182-183）、`AGW_ENABLE_X_BACKEND`（:184-187）、`AGW_XDS_MODE`（:188-189）、`AGW_AGENTGATEWAY_CLASS_NAME`（:190-193）、`AGW_CONTROLLER_NAME`（:194-197）；
- **参数引用**：`AGW_GATEWAY_CLASS_PARAMETERS_REFS` 以 `toJson` 整体序列化（:198-199）；
- ** POD_NAMESPACE**：fieldRef 注入（:200-203）。

模板自带两处**渲染期硬校验**：`controller.extraEnv` 同时给 `value` 和 `valueFrom` 直接 `fail`（:159-171）；`gatewayClassParametersRefs` 每项缺 name/namespace 也 `fail`（:241-250）——错误在 `helm template` 阶段暴露，不留到运行时。

_helpers.tpl 97 行：`agentgateway.fullname`（:13-24）走标准 release-name 组合；`agentgateway.imageTag`（:87-96）给纯 semver 标签补 `v` 前缀（`1.2.3`→`v1.2.3`，`latest`/`dev` 不动）。有一处**死代码**：`agentgateway.validationLevel` helper（:72-79）引用 `.Values.validation.level`，但 values.yaml 29 个顶层键里没有 `validation`，grep 全 chart 也无任何调用方——上游遗产，改 chart 时别被它误导。

role.yaml 在 `rbac.create` 门后（role.yaml:1）渲染 **ClusterRole**，名字带命名空间后缀 `agentgateway-{{ .Release.Namespace }}`（role.yaml:4-6）——同集群多实例不抢名。monitoring.yaml 的开关链是 `monitoring.enabled` → `monitoring.proxy.podMonitor.enabled` 双层（monitoring.yaml:1-2），除 PodMonitor 外还渲染 Grafana dashboard ConfigMap，dashboard JSON 经 `.Files.Get "files/agentgateway-dashboard.json"` 内联（monitoring.yaml:114，40KB 仪表盘文件随 chart 分发）。

### 2.2 agentgateway-crds：35.7K 行生成物

Chart.yaml 与主 chart 同构（version 0.0.2 + appVersion 占位注释，agentgateway-crds/Chart.yaml:8-11）；values.yaml 是 **0 字节空文件**（wc -c 实证）——CRD chart 无任何可配置项。NOTES.txt 只教一件事：`kubectl get crds | grep agentgateway.dev`（templates/NOTES.txt）。四个 CRD 全部 `apiextensions.k8s.io/v1`，由 controller-gen 从 `api/v1alpha1/agentgateway` 类型生成；parameters CRD 里内嵌 CEL 校验（如 agentgateway.dev_agentgatewayparameters.yaml:1024-1030：`daemonSet overlays are only valid when workload.kind is DaemonSet`）——这份 CEL 规则正是内嵌 chart workload 互斥语义的 schema 侧镜像。

### 2.3 agentgateway-standalone：configmap 直读的一切机关

values.yaml 230 行、33 个顶层键。与主 chart 最重要的三个差异键：`namespaceOverride`（values.yaml:14，主 chart 没有）、`mode: readonly`（:23，仅 `readonly|database` 两值）、`config: {}`（:166）。:166 的注释是全 chart 语义密度最高的一行文档：config 顶层非 `config` 节的内容加 `config.modelCatalog` **热重载不重启 Pod**，嵌套 `config.*` 只在启动时读取所以变更要滚动重启，且 `config.storage`/`config.database` 由 chart 按 mode 代管、**禁止用户设置**。

渲染链三个 helper 层层递进（_helpers.tpl）：

1. **baseConfig**（:138-151）：用户 `.Values.config` 为空时给默认骨架——`gateways.default.port: 4000` + 空 `ui`/`llm.models`/`mcp.targets`；
2. **renderedConfig**（:153-170）：baseConfig 经 `fromYaml` 解析后按 mode 注入——`database` 模式写 `database.url` + `storage.mode: hybrid`（:162-164），否则 `storage.mode: file`（:166）；
3. **startupConfig**（:176-181）：renderedConfig 再 `deepCopy` 后 `unset "modelCatalog"`（:179）——只保留启动期配置。

configmap.yaml 只有 11 行（模板）：`config.yaml` 键的值就是 `renderedConfig`（configmap.yaml:10-11），文件第一行先跑 `agentgateway-standalone.validate`（configmap.yaml:1，validate.yaml:1 同样只有这一行 include）——mode 非法或 `mode=database` 缺 `postgres://` 前缀 URL 直接渲染失败（_helpers.tpl:183-196，regexMatch `^postgres(ql)?://`）。deployment.yaml:25 的 `checksum/config` 注解哈希的是 **startupConfig 而非 renderedConfig**（`include "agentgateway-standalone.startupConfig" . | sha256sum`），helper 顶部的注释把设计意图写得很清楚：「Hash only configuration that agentgateway reads at startup...plus config.modelCatalog, are reloaded without restarting the pod」（_helpers.tpl:172-175）——modelCatalog 改动不触发滚动重启，与 :166 注释互为印证。

工作负载同样是固定 `kind: Deployment`（standalone deployment.yaml:2），同样**无 DaemonSet**；但与主 chart 不同：副本数受 `autoscaling.enabled` 门控（:9-11）、挂 config volume 只读（:98-101，volume 来自 `<fullname>-config` ConfigMap，:112-115）、健康探针打 Envoy 风格的 `/healthz/ready:15021`（:56-68）。网关 Service 是独立模板 service-gateway.yaml（`gateway.service.enabled` 门控，:1），类型默认 LoadBalancer（values.yaml:93），大量 Service spec 字段通过 `agentgateway-standalone.serviceSpecFields` helper 复用（service-gateway.yaml:18）——这个 helper 在内嵌 chart 生态里同样存在，是三 chart 间少有的显式复制。另一处观察：standalone 也带了 `files/agentgateway-dashboard.json`，但其 templates/ 全目录 grep `Files.Get` **零命中**——死重文件。

### 2.4 内嵌 chart（pkg/helm/agentgateway）：每个 Gateway 一渲染

7 个模板共 531 行，却有全仓最关键的部署逻辑。模板前缀全是 `kgateway.*`（deployment.yaml:6、_helpers.tpl:19 等）——出身烙印，kgateway 项目直系移植。

- **workload 互斥**：deployment.yaml:2 `if eq (($gateway.workload).kind | default "Deployment") "Deployment"` 与 daemonset.yaml:2 的 `"DaemonSet"` 分支——两个模板渲染同一个 `kgateway.gateway.podTemplate`（:18），由 `.Values.agentgateway.workload.kind` 决定谁出资源。PruneRemovedResources 注释明言 workload-kind 切换后清旧资源（deployer.go:387-388 附近的函数文档）。
- **configmap 三段合并**（configmap.yaml:12-44）：`$baseConfig = rawConfig`（:13）为底；typed 段由三路汇成——`logging.format`（:16-18）、modelCatalog configMap sources 翻译成 `/etc/agentgateway/model-catalog/<name>/<name>.json` 文件路径（:19-27）、spiffe endpoint unix socket 地址（:31-37）；最终 `merge $typedConfig $baseConfig`（:39），注释点明优先级：「typed config takes precedence over rawConfig」（:38）。
- **podTemplate**（_helpers.tpl:84-358）：`checksum/config` 哈希整个 configmap 模板渲染结果（:94）+ 可选 `checksum/xds-ca`（:96）——配置一变即滚动；容器固定 `runAsUser: 10101` + drop ALL + readOnlyRootFilesystem（:122-129）；env 段先建 `userEnvNames` 集合再逐项 `hasKey` 判重（:156-160），模板级默认值含 `TERMINATION_GRACE_PERIOD_SECONDS`/`CONNECTION_MIN_TERMINATION_DEADLINE`（:162-169）、`XDS_ADDRESS` 按 xds.tls 开关切 http/https scheme（:203-208）、Istio 五项（:242-261）；volumes 段把 config volume（:302-304）、**projected serviceAccountToken（audience: agentgateway，43200s）**（:305-311）、modelCatalog 逐 ConfigMap 挂载（:334-343）、spiffe hostPath/CSI 二选一（:344-356）全部就位。

### 2.5 Go 侧装配：loadChart 只管装，默认值另有其人

`loadChart`（charts.go:16-28）做两件事：`loadFs` 遍历 embed FS（charts.go:36-38 断言根目录**恰好一个**条目）、按编译版本覆写 `Metadata.AppVersion/Version`（:22-25）。它不碰 values。真正的值注入管线在 `agentgatewayParametersHelmValuesGenerator.GetValues`（agentgateway_parameters.go:282-347）：`getDefaultAgentgatewayHelmValues` 从 Gateway CR 构造 `HelmConfig`（:533-578——name/gatewayClassName/ports/xds host+port+tls/resources，镜像三字段来自 `inputs.ImageDefaults`，:566-570）→ GatewayClass 级 AGWP overlay 先应用、Gateway 级后叠加（:303-311，注释 "GatewayClass first, then Gateway on top"）→ modelCatalog **只认 Gateway 级**（:312-317，注释解释 ConfigMap 引用按 Gateway 命名空间解析故不可两义）→ Istio/SPIFFE 解析（:320-323）→ 托管 sessionKey 默认（:325）→ xDS CA 注入（:327-341）→ `JsonConvert` 成 `map[string]any` 喂给 Helm。根键 `agentgateway` 由 `HelmConfig` 的 json tag 决定（values.go:8-11），与模板里 `.Values.agentgateway` 严丝合缝。渲染后的对象还有第二层 overlay：`PostProcessObjects` 用 `strategicpatch.NewLayeredOverlayApplier` 把 GatewayClass/Gateway 两级 AGWP 的 workload overlay 按同序叠加到已渲染对象上（gateway_parameters.go:117-119 注释 + 161-164）。

## 三、外部连接

- **deployer 渲染引擎**（explain-01 交叉）：`NewGatewayDeployer` 工厂第一行就 `LoadAgentgatewayChart()`（deployer_factory.go:10）；`RenderManifest` 用 `driver.NewMemory()` + `action.NewInstall` + `DryRunStrategy = action.DryRunClient` 做客户端 dry-run 渲染（deployer.go:158、170），注释强调无集群 I/O 保证函数快速终止（deployer.go:164-166）；渲染产物经 `applyPatch` 以 `types.ApplyPatchType`（SSA）+ FieldManager 落地（deployer.go:113），且先 `equality.Semantic.DeepEqual` 比对跳过无变化对象（deployer.go:357）；Patcher 抽象存在的原因写在 deployer.go:55——"SSA does not work with Dynamic fake client"。
- **AGW_* env → settings.go**（批 50 锚）：`BuildSettings` 一行 `envconfig.Process("AGW", settings)`（settings.go:287）把主 chart 注入的全部 AGW_ 前缀变量收进结构体；`XdsServiceName` 默认 `agentgateway`（:197-200）、`ProxyImageRegistry` 默认 `cr.agentgateway.dev`、`ProxyImageTag` 默认空（:236-241）——**这才是内嵌 chart 数据面镜像默认值的真源头**（回应勘误④：不存在 wellknown.go 的 AgentgatewayDefaultTag，镜像 registry/tag 由 env 驱动的 settings 供给 `inputs.ImageDefaults`）。
- **Makefile 打包矩阵**：`HELM_CHART_DIR_AGW/_CRD/_STANDALONE` 三目录变量（Makefile:511-513）、`package-agentgateway-charts` 聚合目标（:516-517）、双 semver 变量 `HELM_CHART_VERSION_NO_V/V`（:506-509）支持带 v/不带 v 两种标签推 OCI（:561-565）；开发态 `HELM_ADDITIONAL_VALUES ?= hack/helm/dev.yaml`（:514）——dev 值把日志调 debug、策略换 Recreate。
- **golden 快照测试**：`test/helm/chart_test.go` 以 `testdata/<chart>/<case>.golden` 对照渲染结果（chart_test.go:678-680），`REFRESH_GOLDEN=true` 环境变量重写金样（:685-688），Makefile 封装为 `make golden-helm`（Makefile:209-211）——chart 的回归防线。

## 四、数据流

**全托管形态（主 chart + CRD chart + 内嵌 chart）一次完整安装的渲染链**：

1. `helm install agentgateway-crds ...` → 4 个 CRD 落集群（Makefile:571）；
2. `helm install agentgateway ...` → values（29 键）与用户覆盖合并 → 渲染出 controller Deployment + ClusterRole + SA + Service(9978/9093/9092) + 可选监控资源——**注意：此刻集群里没有任何数据面**；
3. controller Pod 起来 → `envconfig.Process("AGW")`（settings.go:287）吃掉 deployment.yaml:92-203 注入的二十余个 env；
4. 用户创建 Gateway CR → reconciler 调 `GetValues`（agentgateway_parameters.go:282）构造 `HelmConfig{agentgateway: ...}`（values.go:8-11）→ `RenderManifest` 用内嵌 chart 在内存 dry-run 渲染（deployer.go:158-172）→ `PostProcessObjects` 两级 overlay（gateway_parameters.go:161-164）→ sessionKey checksum 注解（gateway_parameters.go:191-211，Deployment 与 DaemonSet 双分支 :199-202）→ SSA 落地（deployer.go:113）；
5. 数据面 Pod 读挂载的 ConfigMap（`-f /config/config.yaml`，内嵌 _helpers.tpl:152-154），回连 `XDS_ADDRESS`（:203-208）拿 xDS 配置——从此配置更新走 xDS 推送而非重新渲染，只有 configmap 内容变化（checksum/config，:94）才触发滚动。

**standalone 形态没有第 3-5 步**：`helm install` 渲染 configmap 时即完成 baseConfig→mode 注入→renderedConfig 的合并（_helpers.tpl:153-170），Pod 直接读文件，无 xDS 回连；后续 `helm upgrade` 改 `config.modelCatalog` 只更新 ConfigMap 不滚 Pod（checksum 用 startupConfig，deployment.yaml:25），改嵌套 `config.*` 则滚动重启——热重载语义完全由「数据面进程的文件 watcher + Helm checksum 注解选择性哈希」两个机制拼成。

## 五、设计决策

1. **「Defaults are set in the Go code」的取舍**（pkg/helm/agentgateway/values.yaml:1）：内嵌 chart 不走 Helm values 默认值机制，好处有三——默认值可依赖运行时信息（settings 的 env、Gateway CR 的 spec）、类型安全（`HelmConfig` 结构体 + `JsonConvert`，agentgateway_parameters.go:343-345）、chart 与 Go 同仓编译无版本漂移（loadChart 覆写版本号，charts.go:22-25 对齐 `helm package` 行为）。代价是**调试不对称**：`helm template` 裸跑内嵌 chart 得不到有意义输出，只能靠 golden 测试或 `--set agentgateway...` 手工构造。
2. **release 从不真正安装**：`GatewayReleaseNameAndNamespace` 返回硬编码 `"release-name-placeholder"`（gateway_parameters.go:236-240，注释 "A helm release is never installed, only a template is generated"）——Helm 在此被当纯模板引擎用，无 release 存储、无 helm rollback；生命周期全权交给 ownerReferences GC + SSA + PruneRemovedResources。这决定了运维语义：改数据面**只能改 Gateway CR/AGWP**，不存在 `helm upgrade` 数据面这回事。
3. **checksum 的选择性哈希**：standalone 把「启动期配置」与「热重载配置」切开后只哈希前者（_helpers.tpl:172-181），用 Pod 注解模拟出两级配置生效语义；内嵌 chart 则全量哈希 configmap（_helpers.tpl:94）+ sessionKey 单独注解（gateway_parameters.go:191-211）——因为 xDS 形态下 configmap 只剩引导配置，全量滚动是安全默认。
4. **namespaceOverride 的不一致**（推断，无注释）：standalone 有 `namespaceOverride` 键（values.yaml:14）且所有资源经 `agentgateway-standalone.namespace` helper（_helpers.tpl:13-15）；主 chart 既无此键也无 namespace helper，deployment.yaml:5 直接 `{{ .Release.Namespace }}`。上游 kgateway 主 chart 有同款 namespaceOverride（standalone 继承了该体系），本仓主 chart 未跟进——想在非 release 命名空间跑 controller 时两 chart 行为不同，属上游不一致，改主 chart 时注意别假设有该键。
5. **CRD 独立 chart**：见 2.2——35.7K 行生成物单列一 chart，配 `clean-gen` 全删重生成（Makefile:342）保证「生成物永不手改」的纪律可执行。
6. **kgateway 前缀与过期注释的清理债**：内嵌 chart 模板全套 `kgateway.*` 命名、主 chart deployment.yaml:120-121 注释引用不存在的 `wellknown.go/AgentgatewayDefaultTag`、主 chart 死 helper `validationLevel`（_helpers.tpl:72-79）、standalone 未被消费的 dashboard.json——移植痕迹四处可见且无害，但读码时必须以 Go 侧与 values 实证为准，不能信注释（本文勘误④即因此抓出）。

## 六、新人提示

**加一个 values 开关的完整链路**（以主 chart 加 `controller.foo` 为例）：①values.yaml `controller:` 块加键与注释（遵循现有 `# --` 注释格式，values.yaml:67-207 全是这个格式）；②deployment.yaml 相应位置消费（若属 env 注入，仿 :114-119 的 AGW_LOG_LEVEL 模式）；③若需要 Go 侧行为，settings.go 加字段 + `split_words:"true"` tag（:197-200 模式），env 名自动派生；④test/helm 加 values 用例并 `make golden-helm` 刷新金样（Makefile:209-211）；⑤若开关影响内嵌 chart 渲染，走 `HelmConfig`/`AgentgatewayHelmGateway` 结构体（values.go:8 起）而非模板默认值。

**本地调试**：`helm template install/helm/agentgateway --values hack/helm/dev.yaml` 看主 chart 全渲染；`helm template install/helm/agentgateway-standalone --set mode=database --set database.postgres.url=postgres://x` 可验证 validate helper 的失败路径（_helpers.tpl:190-192）；内嵌 chart 的调试入口不是 helm 而是 golden 测试——`go test ./test/helm/... -run Standalone` 或读 testdata/ 下的 .golden 文件直接看期望产物。

**三个坑**：①别在内嵌 chart 的 values.yaml 里加默认值——会被 Go 侧 `HelmConfig` 覆盖或根本不生效（values.yaml:1 的注释就是警告）；②改 crds chart 模板必被 controller-gen 重生成冲掉——改 `api/v1alpha1/agentgateway` 类型 + markers 再 `make generate`；③standalone 用户在 `.Values.config` 里手写 `storage`/`database` 会被 mode 注入覆盖（_helpers.tpl:162-168 直接 `set`，values.yaml:166 注释明令禁止）——报障时先查这两个键。

（完）
