# NVSentinel 新人导览（ONBOARDING）

> 基于知识图谱 v2（9783 节点 / 24229 边 / 16 层 / 16 步 tour，commit `fbe7ec29`）+ 源码实测重写。`file:line` 锚均逐条验证；文件计数以 `find -type f` 实测为准，与图谱口径差异见第 8 节。

## 1. 项目定位与全景

NVSentinel 是 NVIDIA 开源的 **Kubernetes GPU 集群自主 SRE 平台**，使命在 `README.md:7`：**detects and remediates GPU faults on Kubernetes nodes**。一块坏 GPU 能悄悄污染一整次训练或让节点空载数小时；NVSentinel 把处置自动化为 **检测→保护→修复** 闭环：经 DCGM/syslog/云维护事件实时发现故障，先 cordon/drain 隔离故障节点，再 GPU 复位或整机重启修复、带回服役，无需人工 page。GPU 覆盖 Volta 到 Blackwell（`README.md:270`）。

**形态**：Go 1.27 + Python 3.10 混编；16+ 个组件独立部署——每个 Go 模块独立 `go.mod`、Go workspace 串接（跨模块 import 后跑 `make dependencies-sync`）；硬件传感器是 Python。全部组件由单一 umbrella Helm chart 经 OCI 发布。**采用哲学**（`README.md:88`）：默认只开监控、任何集群可安全跑；治理能力逐级显式开旗。

### agent-first：AGENTS.md 是给 AI coding agent 的协作契约

本仓最独特之处：根目录 **AGENTS.md（427 行）是为 Claude Code/Codex/Cursor 预写的权威操作手册**，`.github/copilot-instructions.md` 只是指回它的指针（`AGENTS.md:3`）。人类新人也应先读，核心规矩：

- **角色定调**（`AGENTS.md:11`）：以生产 K8s Principal Engineer 标准行事——系统会在真实集群重启机器，正确性与运维安全永远优先。
- **十条不可协商规则**（`AGENTS.md:83-94`）：写前必读；`make lint-test-all` 是 PR 硬门禁；绝不削弱测试换绿灯；先读兄弟模块；三振出局；一切 I/O 带 `context.Context`；**治理是破坏性操作——cordon/drain/reboot/reset 代码必须附"健康时不触发"的测试**；改行为先读 ADR；一切向后兼容。
- **agent 越界清单**（`AGENTS.md:96-107`）：不得 push/merge/关 PR；不得动分支保护与发布 workflow；不得顺手 bump chart 版本；只对自建 `kind-nvsentinel` 集群跑 dev-env/e2e/kubectl；**不得给 commit 加 agent 署名**。
- **向后兼容是硬约束**（`AGENTS.md:134`）：滚动升级期间新旧版本互跑、还要读上一版数据；兼容面按易碎度排序——protobuf（只加字段永不重编号）、存储 schema、Helm values、CRD、节点标签/conditions（公共 API）、指标名、CLI 旗标；**CI 不查**，要自查。
- **ADR 纪律**（`AGENTS.md:110-130`）：50+ 篇决策记录在 `docs/designs/`，实现前写、编号永不复用（`AGENTS.md:124`）、废弃走 supersede；agent 可起草、维护者拍板。
- **编码约定**：`retry.RetryOnConflict` 循环内裸错误、循环外再 wrap（`AGENTS.md:220`，wrap 会杀死重试）；K8s 测试用 envtest 真 API server（`AGENTS.md:319`）；禁 `time.Sleep`、用 `require.Eventually/Never`（`AGENTS.md:340`）；优先级（`AGENTS.md:405`）：安全>可测试>一致性>可读>简洁。

配套：`DEVELOPMENT.md`（1475 行，`:103` 起架构节）、`.versions.yaml` 工具版本单一事实源。

## 2. 架构总览与核心数据流

管线是 **Detect → Ingest → Act** 三段（`AGENTS.md:17` 图）：

**Detect——监控器全员对等**：GPU（DCGM）、Syslog、CSP、NIC、KOM、Health Events Analyzer 六类信号源全是同构 health monitor——analyzer 只是不读设备而做跨事件模式检测，**无特殊地位**，与其余监控器走同一条 gRPC 发布路径（`AGENTS.md:38`）。

**Ingest——platform-connectors 双角色**：node-local 角色是每节点 DaemonSet，在 **UDS 上服务 PlatformConnector gRPC**（`platform-connectors/pkg/nodelocal/role.go:18` 包注释）；socket 刻意 group/world 可访问（`role.go:100` listen、`role.go:113` chmod 0o666）——发布者以杂散非 root UID 运行，"谁能报哪个节点"由 node-binding 拦截器鉴权而非文件权限。batch 被接受即 ACK 入 ring buffer，connector 自行消费重试。服务端 `platform-connectors/pkg/server/platform_connector_server.go:84` 把未指定策略的事件归一化为 `EXECUTE_REMEDIATION`。

**Act——存储分发 + K8s API 双总线**：模块间**零直调**，协调只经共享事件存储（MongoDB change streams / PostgreSQL）与 K8s API（`AGENTS.md:42`；`docs/DATA_FLOW.md:17-20` 的"发布-订阅"是存储层视角，节点内传输是 UDS gRPC，叠加才是完整数据面）。动作链：fault-quarantine cordon → node-drainer 驱逐 → fault-remediation 建维护 CR → janitor 消费 CR 执行 reset/reboot（janitor 是唯一由 K8s API 而非存储驱动的执行器）。

**数据契约**在 `data-models/protobufs/health_event.proto`：`service PlatformConnector` 唯一 RPC `HealthEventOccurredV1(HealthEvents)`（`:54-55`）。`HealthEvent`（`:94`）字段即平台词汇表（agent/componentClass/checkName/isFatal/recommendedAction/errorCode/nodeName、quarantine/drainOverrides、processingStrategy）。三档策略（`:68`）：`EXECUTE_REMEDIATION` 可改集群、`STORE_ONLY` 只持久化（观测/演练）、`STORE_AND_ANALYSE` 持久化+分析不动作。`RecommendedAction`（`:75`）编号不连续（REPLACE_VM=25、CUSTOM=27……），是 proto 永不复用编号规矩的活样本。同一 proto 经 protoc-gen-crd 生成 `HealthEventResource` CRD（`:125`）——proto 是 CRD 单一来源。

**发布客户端** commons/pkg/healthpub 双模式：默认 **socket 模式**（`HEALTH_PUBLISH_TARGET` 未设，发到本节点 UDS，`commons/pkg/healthpub/publisher.go:18`）；**direct 模式**（该变量已设则 TLS+token 直连 deployment 连接器，`commons/pkg/healthpub/dial.go:86` 的 DialFromEnvOr 定夺；此时 `AcknowledgesStorage()`（`publisher.go:204`）才为真，即确认真正落库）。持久层统一经 `store-client/pkg/datastore/interfaces.go:22` DataStore 接口。

对外进出门户：**入口** MaintenanceRequest（ADR-051）让外部系统预告维护、NVSentinel 准备节点；**出口** ExternalRemediation（ADR-040）把自修不了的节点移交外部——`data-models/protobufs/external_remediation.proto:28` 的 Condition 消息是两个方向的 CR 状态词汇。

## 3. 代码地图：16 层分层导览

| 层 | 文件 | 导读与关键路径 |
|---|---|---|
| L01 工程基座与构建入口 | 29 | AGENTS/README/DEVELOPMENT、根 `Makefile`（1006 行，`:293` lint-test-all 总门禁）、`make/common.mk`（fanIn=25 全仓最高） |
| L02 API 契约与数据模型 | 61 | `data-models/protobufs/` 三棵 proto + `api/proto/`（device/csp v1alpha1）+ 三组 K8s CRD。**先读契约再读实现** |
| L03 commons 共享库 | 87 | 26 个 Go 包：healthpub、celevent/celfields（共享 CEL 词汇，`commons/pkg/celevent/celevent.go:15`）等；`commons/pkg/lambda/client.go:15` 是 Lambda Cloud 客户端而非 CEL（勘误④） |
| L04 platform-connectors 接入分发 | 91 | `main.go:114`；connectors/transformers/auth/nodelocal/ringbuffer |
| L05 健康监控器家族 | 261 | 七监控器+event-exporter：gpu-health-monitor（Python/DCGM，`gpu_health_monitor/dcgm_watcher/dcgm.py:230`）、syslog（xid/sxid/gpufallen/nicdriver 族）、nic/csp/KOM/nvcre/slurm-drain |
| L06 health-events-analyzer | 37 | `main.go:54`；reconciler（对账+恢复线）、config（when 门控 `pkg/config/rules.go:55`）。事件汇聚判定处 |
| L07 资产采集与标注 | 58 | labeler（`pkg/devicecounts/resource_slices.go:33` 以 DRA ResourceSlice 打标签）、metadata-collector（`pkg/mapper/mapper.go`）、log-collector |
| L08 store-client 持久层 | 104 | 纯库无 main：datastore（双后端仓储）+ client。换库只动这层 |
| L09 preflight 预检门禁 | 99 | gang 调度发现（`pkg/gang/discoverer/kubernetes.go:15`）、webhook 准入 + 三探针（dcgm-diag/nccl-allreduce/nccl-loopback） |
| L10 故障治理动作链 | 222 | fault-quarantine（断路器 `pkg/breaker/breaker.go:44`）、fault-remediation（`main.go:76`）、gpu-reset（**242 行 shell** `gpu_reset.sh:16`）、node-drainer（`pkg/evaluator/evaluator.go:52`）、janitor（`pkg/controller/rebootnode_controller.go:90`）、lifecycle-manager（`internal/controller/maintenancerequest_controller.go:77`） |
| L11 umbrella Helm 模板 | 101 | Chart.yaml（`:21` 起 22 子 chart）、values.yaml 主面板、templates/ 51、tests/ 18、23 overlay（第 5 节） |
| L12 存储子 chart | 173（实测） | mongodb-store（108 文件；图谱因 resource:/service: 双型建模记 147 节点）+ postgresql（65，图谱 95 同因） |
| L13 组件子 chart 群 | 259 | 其余 20 个组件 chart（preflight 38/lifecycle-manager 22/janitor 19…）；`charts/k8s-datastore` 目录名≠依赖名 `k8sdatastore-crds`（勘误③） |
| L14 测试体系 | 177 | tests/uat（aws 15/gcp 14/kind 7 + azure/oci 占位）、scale-tests 压测、helpers/data |
| L15 文档与 ADR | 164 | designs 61 篇编号 ADR（001-063）、configuration 25、runbooks 19、tutorials 15。设计意图首要入口 |
| L16 CI·开发环境·演示与插件 | 252 | `.github/`（实测 workflows 23 个）、tilt/（dcgm-fake/csp-api-mock/kwok mock 族）、demos/、plugins/（slinky-drainer 等） |

## 4. 核心子系统深潜：事件管道与 NPD 健康状态机

### 4.1 事件管道全链

**(1) 传感**——以 gpu-health-monitor 为标本（其余同构）：`dcgm.py:230` DCGMWatcher 经 pydcgm 直连 DCGM（所以 GPU Operator 要开 `dcgm.enabled=true` standalone，`README.md:27-35`）；`dcgm.py:137` ProbeWatchdog 在 DCGM 挂死时触发临界事件逃生；发布在 `platform_connector/platform_connector.py:38`（MAX_RETRIES=10 批量重试）与 `direct_publisher.py:73` 的 direct 模块。syslog 按 xid/sxid/gpufallen/nicdriver 分检测器包。

**(2) 接入**——除 §2 已述的鉴权/归一化/入队 ACK 外：transformers 做字段覆盖/转换（ADR-021/023）后落库并更新 K8s node conditions。

**(3) 决策**——health-events-analyzer：`rules.go:55` 每规则可带 `when` CEL 门控，关键语义在 `rules.go:64-77`——**when 求值失败回退为"适用"**：when 只是省查询的预筛，失败必须保守放行。命中后输出仍是 HealthEvent、走同一管道——"analyzer 只是又一个监控器"的机制实现。`values.yaml:635` 样例：`when: 'event.agent == "syslog-health-monitor" && "109" in event.errorCode'`。恢复线 `pkg/reconciler/node_recovery*.go`（ADR-059）。

**(4) 执行**——breaker.go:44 断路器（1 秒粒度 ring buffer 跟踪唯一 cordon 节点，5 分钟窗口达 50% 熔断全部事件处理——小集群要显式关）；node-drainer `evaluator.go:123` 评估排水、`:177` 决定是否走自定义排水插件（ADR-015；plugins/slinky-drainer 就是一个）；fault-remediation 建维护 CR；janitor `rebootnode_controller.go:90` reconcile CR 执行重启/GPU 复位；lifecycle-manager `maintenancerequest_controller.go:170` claimAndEmit 编排"隔离→排水→外部维护→验证放行"（ADR-051）。

### 4.2 NPD 健康状态机专节

NVSentinel 对 node-problem-detector 的集成是"**借别人的探测器、走自己的管道**"，两篇 ADR 分两步：

**缺口**（ADR-050，`docs/designs/050-gpu-system-services-npd-checks.md`）：DCGM 的 fabric probe state 是**闩锁式注册结果**而非进程存活——Fabric Manager 注册后死掉 DCGM 仍报旧值（issue #883：FM 死了 2.5 周无人知）；syslog 监控不看 systemd 单元状态。**没有现有监控器能回答"nvidia-fabricmanager 是否在运行"**。

**消费模型**（ADR-053，`docs/designs/053-npd-checks-integration.md`）：NPD 三类监视器（被动日志/主动脚本/统计采集）把问题发布为**永久 Node Conditions**；NVSentinel 侧姿势：**KOM watch core/v1 Node、per-condition CEL 策略匹配、命中生成 HealthEvent 走既有管道**——不新增组件。ADR-050 另用 NPD CustomPluginMonitor 配自定义检查（custom-plugin-fm-*.json 与 check_fm_*.sh）覆盖 GPU 系统服务层。

**关键边界**：`values-npd-remediation.yaml:18` 明文 **"NVSentinel does not install or configure NPD"**——本仓不装 NPD 只消费其 conditions；策略须与集群 NPD 实际发布的 condition type 对上。

**两个 overlay 的策略语义**：`values-npd-gpu-services.yaml`（ADR-050 配套）开 KOM（`:37`）注入 `NPDFabricManagerDown`（`:66`，CEL 谓词 `resource.status.conditions.exists(c, c.type == "FabricManagerDown" && c.status != "False")`，isFatal+REPLACE_VM）与 `NPDFabricManagerNotInstalled`（`:112`，仅 FM 必装的 NVSwitch 机群启用）；`values-npd-remediation.yaml`（ADR-053 配套）是 NPD 默认条件的修复策略，**只开 KOM 不开治理组件**——要真执行须与 `values-remediation.yaml` 叠加（`:27-31`），验证用 `processingStrategy: STORE_ONLY` 无损演练（`:33`）。**Helm 列表替换陷阱**：KOM `policies` 是 list、Helm 整体替换不合并——两 overlay 头部都警告会替换用户已有 policy 列表，默认策略被刻意重复保底。

KOM 本体：`health-monitors/kubernetes-object-monitor/pkg/policy/evaluator.go:35` Evaluator（`:69` EvaluatePredicate 判命中、`:92` EvaluateNodeAssociation 判归属节点）；`pkg/controller/reconciler.go:136` Reconcile 驱动状态转换，`:289` handleHealthy/UnhealthyTransition 成对（恢复转换同样产事件）、`:200-205` 对已删 Node 只清内部状态不发布。

## 5. Helm 部署体系

部署面全部在 `distros/kubernetes/nvsentinel/`，是**用户唯一面对的配置表面**（Helm values 被列为最易碎兼容面：永不改名/删除用户已设键，新键默认值保现状）。

**Chart.yaml**（`:21` 起）声明 **22 个子 chart**，与 `charts/` 22 子目录一一对应：postgresql 是 vendored 上游（15.5.38），其余 21 个 0.1.0 随伞发布；**Chart.lock 却只锁 16 个**（勘误⑤）。CRD 不在独立 config/crd 树而**住在各组件 chart 里**（envtest 直接指 chart 的 crds 目录，`AGENTS.md:326`）。

**values.yaml 主面板**：`global:` 块是全组件开关（`values.yaml:319-360`）——gpuHealthMonitor/syslogHealthMonitor/labeler/metadataCollector 默认 true，faultQuarantine（`:322`）、nodeDrainer（`:324`）、faultRemediation（`:326`）、mongodbStore（`:347`）、kubernetesObjectMonitor（`:349`）、preflight（`:355`）等默认 false，与 Adoption 哲学对应；`:287`/`:294` tracing/audit 全局开关。

**23 个 values overlay**（实测 `values-*.yaml`）四族：能力开关族（remediation/nvcre/npd-gpu-services/npd-remediation/preflight-kube/postgresql/full）；Tilt 本地开发族（10 个变体对应 tilt/ mock 矩阵）；云验收族（aicr-uat 及 aws/gcp 变体、atlas-gcp、aws-docdb、cosmosdb-test）；叠加即语义（NPD 修复演示=remediation+npd-remediation 两层）。

**存储双雄**：mongodb-store（108 文件，arbiter/hidden+TLS+Percona 变体，ADR-013）与 postgresql（65 文件，pgbackrest）。README 快速开始的 mongodb root password Secret 警告（`README.md:57-60`）——已有数据卷无此 Secret 时新密码会把 NVSentinel 锁在旧数据外。

**组件 chart 群**（其余 20 个）：各带 `_helpers.tpl`、镜像/RBAC/configmap 与 crds/；umbrella 层 templates/ 51 + tests/ 18 个冒烟钩子。

## 6. 构建与测试体系

**Makefile**（1006 行）：总门禁 `lint-test-all`（`Makefile:293`）= protos/license-headers/gomod/renovate/dead-code + 全模块 lint+test + helm lint——CI 同款，模块子集不算数。每模块经 `make/go.mk` 统一接口（`make -C labeler lint-test`）。代码生成 `protos-generate`（`:303`，一次驱动两棵 proto 树的 Go+Python 绑定）。镜像双轨：Go 走 `ko`（`:697`）；Python/shell/CUDA 走 `docker-all`（`:682`）。本地集群 `dev-env`（`:942`，ctlptl 管 Kind、Tilt 内循环）、`e2e-test`（`:961`）。

**测试金字塔**：单元/集成在组件内（envtest 真 API server、`-race` 全开；治理路径 >80% 覆盖）；E2E 对本地 Kind，CI 跑全矩阵（AMD64/ARM64 × MongoDB/Percona/PostgreSQL——**PostgreSQL 不是二等公民**）；**UAT 云上验收**（`tests/uat/README.md:3`）：在 CSP 建生产级集群跑端到端，aws/gcp/kind 主力+azure/oci 占位；**压测** tests/scale-tests/（event-generator 注入，ADR-054）；chart 冒烟（umbrella tests/ 18 钩子）；**mock 族** tilt/（dcgm-fake/csp-api-mock/kwok）——无 GPU 全管线可跑，`demos/local-fault-injection-demo` 一条 `demo.sh` 演完"排水→修复→回迁"闭环。

## 7. 新人上手路线（按 16 步 tour）

**第一程·契约与底座（tour 1-3）**：① AGENTS.md→README→DEVELOPMENT.md 架构节；② `health_event.proto` 逐字段精读，再扫另两棵 proto 与三组 v1alpha1；③ commons：healthpub 双模式→celevent CEL→server 骨架。

**第二程·传感与管道（tour 4-9）**：④ platform-connectors（nodelocal→server→transformers）；⑤ gpu-health-monitor 标本：DCGMWatcher→发布路径，理解"加监控器"的形状；⑥ 其余监控器速过（重点 KOM CEL policy，§4.2）；⑦ analyzer when 门控+reconciler；⑧ 资产三件套；⑨ store-client DataStore 抽象。

**第三程·治理动作链（tour 10-14）**：⑩ fault-quarantine（breaker→evaluator→reconciler）；⑪ fault-remediation+gpu-reset；⑫ node-drainer 决策树+自定义排水+janitor CR 消费；⑬ lifecycle-manager MR 状态机+ValidationRequest；⑭ preflight gang+webhook+三探针。

**第四程·部署与质量（tour 15-16）**：⑮ Chart.yaml→values.yaml 开关面板→23 overlay 四族→存储双雄；⑯ tests/uat+scale-tests+tilt mock，**亲手跑** `demos/local-fault-injection-demo/demo.sh`——从故障注入到自动恢复是理解本仓价值的最短路径。

配套：`docs/designs/README.md` 索引按子系统 grep；运维读 runbooks/、配置读 configuration/。出师自检：能回答"一条 HealthEvent 从 DCGM 异常到节点重启经过哪几跳、每跳在哪个文件"。

## 8. 陷阱与勘误

以下均经源码逐项验证：

1. **生成物绝不手改**：`.pb.go`/deepcopy 改 `.proto` 后跑 `make protos-generate`，CI diff 漂移即红；Go 模块**没有 Dockerfile 不是遗漏**——ko 构建（`AGENTS.md:81`）。
2. **ADR 缺号合法、撞号不合法**：61 个 ADR 占 001-063，缺 057/060/061 合法（`docs/designs/README.md:12` "Numbers are allocated, not contiguous"）。但 **055 用了两次**：nvcre-certification-monitor 进索引（`docs/designs/README.md:71`）、pod-drain-policies 未进索引却被 `063-pod-drain-policies-owner-kinds.md:7` 引用——违反 `AGENTS.md:124` "永不复用编号"，引用 ADR-055 须消歧。
3. **k8s-datastore 目录名 ≠ 依赖名 k8sdatastore-crds**；values 键随依赖名（`values.yaml:357` 的 `k8sdatastoreCrds`）。
4. **commons/pkg/lambda 不是 CEL**：是 **Lambda Cloud REST API 客户端**（`commons/pkg/lambda/client.go:15` 原文）；CEL 在 `celevent`/`celfields`。旧图谱曾标"CEL 表达式求值"。
5. **Chart.lock 落后 Chart.yaml**：依赖 22 个、lock 只锁 16 个（缺 nvcre/event-exporter/k8sdatastore-crds/slurm-drain/nic/janitor-provider）——`helm dependency build` 走 lock 会少装。
6. **文件数双口径**：磁盘实测 mongodb-store 108/postgresql 65；图谱记 147/95 节点——同一 yaml 被 resource:/service: 双型建模产生重复（mongodb-store=106 唯一路径+41 多型重复）。workflows 实测 23 个；values overlay 实测 23 个（"24"把主 values.yaml 也计入）。
7. **gpu-reset 是 shell 不是 Go**：`gpu-reset/gpu_reset.sh` 242 行 Bash，Dockerfile 包装成节点特权 Job。
8. **janitor 的 CRD 家族没有"Janitor"这个 Kind**：`janitor/api/v1alpha1/` 实际是 ExternalRemediation、GPUReset、RebootNode、TerminateNode 四组；MaintenanceRequest 是 lifecycle-manager 的另一条线。
9. **Helm 列表整体替换**：KOM policies 是 list，应用 NPD overlay 会整体替换用户已有列表而非合并（两 overlay 头部显式警告）；默认策略被刻意重复保底。
10. **NPD 是外部依赖**：本仓不装不配 NPD（`values-npd-remediation.yaml:18` 原文），前提是集群自装 NPD 且 condition types 匹配；验证用 STORE_ONLY。
11. **UDS 0o666 是特性**：发布者以杂散非 root UID 运行，收紧权限会打断全部发布者；鉴权在 node-binding 拦截器（`role.go:127`）。
12. **UAT azure/oci 各只 1 个文件**（占位），云验收主力 aws/gcp/kind。`e2e-test`/`kubectl` 只对自建 `kind-nvsentinel` 集群（`AGENTS.md:103`）。

**任务书前提勘误**："mongodb-store 147 文件/postgresql 95""24 个 overlay"与磁盘实测不符，已按实测改写并在第 6 条说明双口径成因；"22 个子 chart 依赖"经 Chart.yaml:21 清点属实。