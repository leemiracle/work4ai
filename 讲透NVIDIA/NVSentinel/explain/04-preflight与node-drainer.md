# 04 preflight 准入门禁与 node-drainer 节点排水

> 锚基座：本地仓 @fbe7ec29，行号实测；图谱 L10/L11 层，ADR-026/034/015/041/063。

## 角色定位

这两个组件站在工作负载生命周期的两端：preflight 在 **pod 启动前**验 GPU 可用性（门禁），node-drainer 在 **维护前**把 pod 安全请走（排水）。前者防"带病上岗"，后者防"带载维修"——一进一出夹住 GPU 节点的服役窗口。

## 内部结构

**preflight**（Go 控制器，`preflight/main.go:63`）：三线并行。配置线：PreflightConfig CR 多实例冲突时 `preflight/pkg/controller/preflightconfig_controller.go:123` `applyOldestWithConflicts` 择最旧合法配置（preflightconfig_controller.go:97 `applyConfig` 应用、:165 `updateStatus` 回写）。gang 线：`preflight/pkg/controller/gang_controller.go:204` `RegisterPod` 注册 gang 成员、gang_controller.go:230 `ensureNCCLTopoConfigMap` 维护拓扑 ConfigMap；协调器 `preflight/pkg/gang/coordinator/coordinator.go:112` 名称清洗+coordinator.go:147 `ConfigMapName` 防超限、:206 `RegisterPeer`、:405 `GetRank` 分配 rank——ConfigMap 即注册表（coordinator.go:161 `EnsureConfigMap`）。执行线：`preflight-checks/` Python 三件（dcgm-diag 诊断/nccl-allreduce 全归约/nccl-loopback 回环；nccl-loopback 是 Go 检查器+PyTorch 运行时混合栈 Dockerfile）。

**node-drainer**（`node-drainer/main.go:49`）：决策核 `node-drainer/pkg/evaluator/evaluator.go:123` `EvaluateEventWithDatabase`——evaluator.go:80 `checkPreconditions` 前置条件→判断已隔离/已排水（evaluator.go:630 `isNodeAlreadyDrained`）→evaluator.go:177 `shouldUseCustomDrain` 选自定义排水（evaluator.go:442 `evaluateCustomDrain`，ADR-015）或原生驱逐→evaluator.go:679 `DrainScopeFor` 算排水范围（整节点或单 GPU 实体，部分排水）。Pod 策略在 `node-drainer/pkg/evaluator/pod_policies.go`（按策略列举各命名空间待驱逐 Pod）。洪泛防护：`node-drainer/pkg/queue/priority_queue.go:115` `classifyForEnqueue` 按代表性事件分级入队、priority_queue.go:152 `markNodeDraining` 给排水中节点降权（ADR-041）。coldstart 保证重启后恢复活跃排水状态。

## 外部连接

preflight 经 mutating admission webhook 注入 init container（`charts/preflight/templates/mutatingwebhook.yaml` + image-cache daemonset 预热镜像）；检查结果按 `preflight.publishTo` 发节点局部 socket 或 deployment 连接器（`docs/DATA_FLOW.md:27-31` 钉版"不走 change stream 管线"）。node-drainer 消费 store-client 事件流与 K8s informer 缓存；驱逐动作最终是 K8s API eviction。排水的"何时放行"对接 lifecycle-manager 的验证线（ADR-049）。

## 数据流

preflight：pod 调度→webhook 注 init container→（多节点时 gang 协调等齐）→dcgm-diag/nccl 检查跑硬件体检→结果即 HealthEvent 发连接器→失败则 pod 起不来。drainer：健康事件/维护请求→优先队列→evaluator 判定→pod_policies 列驱逐清单→按 DrainScope 整节点或单 GPU 实体排水→完成后标记，交 remediation/janitor 接棒。

## 设计决策

preflight 择旧（:123）而非择新：多 CR 冲突时最旧的配置最有可能是"曾经评审过的基线"，新 CR 可能是误提交。gang 用 ConfigMap 当注册表（coordinator.go:161）而非新 CRD：注册表生命周期跟 pod 走，K8s 原生对象够用。排水分级入队（priority_queue.go:115）解决的是"事件洪泛淹没代表性节点"——故障风暴时未排水节点必须排在已排水节点前。

## 新人提示

preflight 默认关（`values.yaml:355-356`），要按命名空间打标签才生效。`preflight/api/v1alpha1/zz_generated.deepcopy.go` 是 controller-gen 生成物。排水的 pod 策略配置看 `charts/node-drainer/templates/configmap.yaml` 与 ADR-063（owner kinds 扩展）。E2E 里排水相关测试用 `tests/node_drainer_test.go` 与 `node_drainer_pod_policies_test.go` 起步。
