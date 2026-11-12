# 02 janitor 控制器与 CRD：修复动作引擎

> 锚基座：本地仓 @fbe7ec29，行号实测；图谱 L12 层，janitor/ 仓 577+1891 行两大文件。

## 角色定位

fault-remediation 决定"做什么"，janitor 决定"怎么把动作安全做掉"。它是四个维护 CR（RebootNode/TerminateNode/GPUReset/ExternalRemediationRequest）的统一控制器，外加 TTL 清理；动作执行期的节点锁、托管服务停启、Job 跟踪、多修复互斥全在这层。janitor-provider 是它的 CSP（云厂商）外挂代理。

## 内部结构

`janitor/main.go:102` 入口按序注册：RebootNode（main.go:216）→TerminateNode（main.go:227）→GPUReset（main.go:238）→ExternalRemediationRequest（main.go:249）四组 reconciler，再挂 TTL reconciler 组（main.go:261-263；`-enable-ttl` 默认开 main.go:361，默认 TTL 14 天 main.go:365，ADR-037）。

**GPUReset 控制器**是全仓最大控制器（`janitor/pkg/controller/gpureset_controller.go` 1891 行）：gpureset_controller.go:84 reconciler 结构体；:119 `Reconcile` 入口；:228 `startResetSessionIfNeeded` 开复位会话（节点锁+CSP 调用）；托管服务（device plugin/DRA operand）先停后启——:746 `managedApps` 列出、:539 `tearDownServices` 停、:1016 `restoreServices` 恢复；重置 Job :892 `createJob` 创建、:938 `checkJobStatus` 跟踪、:1448 `newGpuResetJob` 构造；:1241 `reconcileCompletion` 收尾。CRD 类型在 `janitor/api/v1alpha1/gpureset_types.go`（GPU 选择器/复位规格与状态/托管服务状态）。

**ExternalRemediationRequest 控制器**（`janitor/pkg/controller/externalremediationrequest_controller.go`，734 行）：外部系统 dispatch→应用/释放状态机，含释放失败转换。**维护争用仲裁**在 `maintenance_contention.go:36` `activeSameKindHolder`：只有"同 kind 且未完成"的持有者才算竞争；跨 kind 竞争与"完成到租约删除的小窗口"都按正常等待处理（maintenance_contention.go:28-30 两个 reason 常量）。

## 外部连接

CRD 随 janitor 子 chart 发布（`distros/kubernetes/nvsentinel/charts/janitor/crds/` 四份：external_remediation.crd.yaml、janitor.dgxc.nvidia.com_gpuresets/rebootnodes/terminatenodes.yaml——组名是 janitor.dgxc.nvidia.com，注意与其他组件的 nvsentinel.nvidia.com 组不同）。CSP 能力经 gRPC 到 janitor-provider：`janitor-provider/main.go:275` 注册 `CSPProviderServiceServer`（proto `api/proto/csp/v1alpha1/provider.proto`），三 RPC main.go:85 `SendRebootSignal`/main.go:124 `IsNodeReady`/main.go:161 `SendTerminateSignal`，main.go:70 `translateCSPError` 保留 provider 状态码。节点锁用 commons 的 distributedlock（`commons/pkg/distributedlock/`）。物理执行端是 gpu-reset Job（ADR-019/020，见 explain/03）。CRD 声明对照 `janitor/api/v1alpha1/rebootnode_types.go` 与 `terminatenode`/`external_remediation` 类型文件。

## 数据流

fault-remediation 渲染维护 CR→janitor Reconcile（gpureset_controller.go:119）拿节点锁（distributedlock）→争用仲裁（maintenance_contention.go:36）→GPUReset 线：停托管服务（gpureset_controller.go:539）→跑 gpu-reset Job（:892）→查 Job 状态（:938）→恢复服务（:1016）→写 CR status→TTL 到期自动删除。CSP 类动作（重启/终止）转 gRPC 给 janitor-provider 执行。

## 设计决策

"一个引擎四 CR"而非四组件：四类动作共享会话/锁/TTL 骨架，差异下沉到各自 reconciler。互斥判据选"同 kind 才算争用"（maintenance_contention.go:36 注释）是刻意宽松——避免 GPUReset 与外部维护互相误杀。TTL 清理做成 reconciler 而非 cron，是 K8s 声明式一致性的取向。CRD 组名 janitor.dgxc.nvidia.com 带历史沿革痕迹（dgxc=DGX Cloud），改名成本高于保留。

## 新人提示

读 gpureset_controller.go 先看 :119 Reconcile 的状态机分支图再下钻。webhook 校验与 metrics 证书在同 chart（certificate-metrics.yaml）。勘误提醒：`tests/data/fr-multi-template-config.yaml` 是无消费方的孤儿夹具，别拿它学修复模板——有效模板看 `fault-remediation/pkg/reconciler/templates/`（custom-action/gpureset/rebootnode 三件）。TTL 行为可用 `-default-ttl` 覆盖做快速实验。
