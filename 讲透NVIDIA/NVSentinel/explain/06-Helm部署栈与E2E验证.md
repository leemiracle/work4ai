# 06 Helm 部署栈与 E2E 验证（深讲：umbrella chart 与测试体系）

> 锚基座：本地仓 @fbe7ec29，行号实测；图谱 L13/L14/L15 层。

## 角色定位

`distros/kubernetes/nvsentinel/` 是全平台的交付单元：一个 umbrella chart 聚合 22 个组件子 chart，values.yaml 是总装配面板；`tests/` 163 文件在 kind 集群上验证核心闭环。代码讲功能，这层讲"16 个组件如何被安全拧在一起发出去"。

## 内部结构

**umbrella**：`distros/kubernetes/nvsentinel/Chart.yaml` 声明 22 个子 chart 依赖（每个挂 `global.<组件>.enabled` 条件；实测无 cert-manager 外部依赖、无 kubeVersion 字段）。`values.yaml`（~690 行）values.yaml:318-362 组件开关默认值=**只开 4 个观测组件**（gpuHealthMonitor values.yaml:319/syslogHealthMonitor values.yaml:338/labeler values.yaml:340/metadataCollector values.yaml:342），analyzer/quarantine/drainer/remediation/janitor 等动作组件默认全关——"先观测后动刀"的安全默认。24 份场景 values（values-tilt.yaml/values-postgresql.yaml/values-remediation.yaml/values-aicr-*-uat.yaml…）覆盖部署形态矩阵。`templates/` 有平台连接器 8 件资源模板+`_platform-connector-config.tpl` partial、`job-external-mongodb-setup.yaml`（幂等索引模板 `nvsentinel.mongoIdempotencyIndexEval` 定义在 `templates/_external-mongo-init-eval.tpl:139`，还被 `charts/mongodb-store/templates/_init-eval.tpl:110` 跨 chart include）。准入策略 `policies/must-have-sbom.yaml`/`must-have-slsa.yaml` 强制供应链证明。

**数据存储独立发布**：mongodb-store chart 内嵌 mongodb/psmdb-operator/psmdb-db 三子 chart（`charts/mongodb-store/Chart.yaml`），mongodb 又嵌 kubectl/mongodb-exporter/nginx/os-shell 五子 chart（`charts/mongodb-store/charts/mongodb/Chart.yaml`）——**四层嵌套**是 Bitnami→Percona 迁移（ADR-013）产物；postgresql（v15.5.38）独立。CRD 随子 chart：janitor 4 份（组 janitor.dgxc.nvidia.com，如 `charts/janitor/crds/janitor.dgxc.nvidia.com_gpuresets.yaml`）、lifecycle-manager 2 份（`charts/lifecycle-manager/crds/maintenance_request.crd.yaml`+`nvsentinel.nvidia.com_validationrequests.yaml`）、k8s-datastore/preflight 各 1 份（`charts/k8s-datastore/crds/health_event.crd.yaml`、`charts/preflight/crds/preflight.nvsentinel.nvidia.com_preflightconfigs.yaml`）。

**E2E**（`tests/`）：`tests/cold_start_test.go:19-26` 注释钉版方法论——直接 mongosh 删 resume token 强制冷启动，"仅限 cold-start/stale-token 测试"；cold_start_test.go:61 `TestFaultRemediationColdStart` 验证重启后靠冷启动查询找回在途事件。夹具 `tests/data/basic-matching-configmap.yaml` 被 6 个测试文件消费（如 `tests/fault_quarantine_test.go:105`）。`tests/helpers/constants.go:19-20` 起定义镜像/超时常量。

## 外部连接

tilt 开发环境（`tilt/Tiltfile` 调 ko-tilt-build.sh）复用同一套 chart（values-tilt*.yaml 九种变体）；KWOK 假节点脚本+四 mock（csp-api-mock/dcgm-fake/event-exporter-mock/simple-health-client）撑起无硬件本地全栈。CI 的 e2e-test/publish/release 消费同一 Makefile 目标。

## 数据流

helm install → 依赖按 condition 装配 → 子 chart 渲染（各 `_helpers.tpl` 命名模板，如 `templates/_helpers.tpl` 定义 56 个辅助模板）→ CRD 随首装进集群（**helm upgrade 不装 CRD**，`docs/tutorials/requesting-node-maintenance.md:74,90` 明示需手动 apply `charts/lifecycle-manager/crds/`）→ 组件按 values 开关起 Pod → E2E 用 e2e-framework（`tests/go.mod` module 名就叫 `tests`）驱动验证。

## 设计决策

组件与数据面解耦发布（mongodb-store/postgresql 独立 chart）：数据库升级节奏与组件不同步。CRD 放子 chart crds/ 而非 umbrella：跟随组件版本。默认全关是安全工程：新装的 NVSentinel 不对集群做任何动作，直到运维显式开闸（values.yaml:318-362）。E2E 直改 Mongo（`tests/cold_start_test.go:19-26`）被明文限制使用范围——非常规手段防泛化。

## 新人提示

勘误三连：子 chart 实数 22（不是 21）；Helm 测试不止 umbrella `tests/` 的 18 份，另有 38 份内嵌在 13 个子 chart 的 tests/ 目录（gpu-health-monitor 6 份最多）；目录 `charts/k8s-datastore/` 的 chart 名是 `k8sdatastore-crds`（Chart.yaml name 字段），按目录名 grep 会扑空。改 CRD 记得手动 apply，upgrade 不会带上去。
