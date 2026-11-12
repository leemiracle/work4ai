# 讲透 NVSentinel（NVIDIA/NVSentinel）· 深讲知识库

> NVIDIA 开源 Kubernetes GPU 集群自主 SRE 平台（**agent-first 仓**：AGENTS.md 427 行是给 AI coding agent 的权威操作契约）：16+ 监控/治理组件（Go 1.27+Python 混编 monorepo）、健康事件管道→隔离→修复→排水→复位全闭环、单一 umbrella Helm chart 部署。
> 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/NVSentinel` · 产物基线 commit `fbe7ec29`

## 全链状态表

| 阶段 | 状态 | 产物与规格 |
|---|---|---|
| deepwiki | ✅ 完成（2026-10-26） | `deepwiki/` 63 页 TRUE_100（769,200 字符），MCP 通道；INDEX.md + _coverage-check.md |
| understand 图谱 v2 | ✅ 完成（2026-11-10） | 仓内 `.understand-anything/knowledge-graph.json`：**9783 节点 / 24229 边 / 16 层 / 16 步 tour / validate 0 issues（finalize 内置+独立双跑）** / fingerprints 2020 文件@fbe7ec29 |
| onboarding | ✅ 重写（2026-11-10，基于 v2 图谱） | `onboarding/ONBOARDING.md` 8 节，13077 非空白字符，71 个 file:line 锚（全部源码实测，验收抽验 5/5 命中+1 处行号笔误已修） |
| explain | ✅ 10 篇（6 旧篇保留+4 新篇） | `explain/` 六节结构合计 **35705 非空白字符 / 204 锚**（旧 6 篇 16212 字/106 锚基于同 commit 源码锚仍有效抽验 4/4；新 4 篇 19493 字/98 锚抽验 15/15 命中） |
| 勘误清单 | ✅ 本文 20 条 | 全部源码级实证（行号可复查） |

**explain 索引**（阅读顺序建议）：01 事件监控管道（gpu-health→analyzer）→ 03 故障治理修复链 → 02 janitor 控制器与 CRD → 04 preflight 与 node-drainer → 05 store-client 持久层与 proto 契约 → 07 commons Go 核心（healthpub 遥测底座）→ 08 NPD 健康状态机与 systemd 层监控（ADR-050）→ 06 Helm 部署栈与 E2E → 09 ADR 决策体系与 values overlay 群 → 10 API 契约链/CRD 生成物/UAT 验收。

**阅读总路线**：README（本文件）→ ONBOARDING.md 全景 → 按线读 explain → 源码对照。

## 图谱两代重建叙事（v1→v2，诚实记录）

- **v1（2026-11-10 01:12 夜间）**：10502n/20056e。缺陷：Go 跨 module import 大面积丢失——scanner 不认 monorepo 的 `go.mod replace` 引用（node-drainer→commons/data-models 等全漏），且把 import 目标目录展开时误含 `_test.go`（Go 不允许 import 测试文件）。
- **修复（2026-11-10 上午）**：批 1-51（816 文件）由 worker 重跑，import 全量手扫修正 5779 条边、逐条磁盘验证（0 坏）；批 52+ 为并行 worker 产物，零 ID 冲突。交接台账 `.understand-anything/tmp/BATCH-1-51-STATUS.md`。
- **v2（本版）**：9783n/24229e。节点 -719（v1 重复节点去重）、边 +4173（imports 修复净增）。finalize 内置 validate 与独立 `ua-inline-validate` 双跑均 0 issues。
- **遗留**：merge 后**函数级未解端点 134 条边被 drop**（端点函数节点在批产物中缺失，merge 保守丢弃而非造节点）——诚实记录，已在图谱边计数中扣除，不影响 file 级完整性（2244/2244 file 级节点全入层零重复）。
- **规范化**：341 条边缺 `type` 字段但带 `relation`（helm chart 相关边），finalize 前统一填充 `type=relation` 值，零语义变化。

## 甄别与勘误清单（18 条，全部源码级核实）

**图谱口径类**
1. **charts/ 多型重复节点**：`charts/` 域图谱 501 个 file 级节点 = **398 个唯一文件 + 103 个多型重复**——同一 yaml 被 `resource:` 与 `service:` 双类型节点覆盖（89 对，另有 4 个文件被 3-6 节点覆盖）。validator 只查 id 重复不查 (type,filePath)，合规但计数口径须注明：mongodb-store 磁盘 108 文件（图谱 147 节点）、postgresql 磁盘 65（图谱 95）；两者 `Chart.lock` 均未入谱。
2. **L12"存储子 chart 242 文件"是节点数**：唯一文件实为 173（108+65）。
3. **.github 文件数双口径**：`.github/` 全目录 88 文件（图谱 L16 含之），其中 workflows **23 个**（"66 个 workflow"是误传——66 为 workflows 目录含 composite action 子目录的总文件数）。
4. **platform-connectors 被 scanner 错标 infra**：`scan-result.json` byCategory 的 573 个 infra 文件含 14 个 platform-connectors 的 .go（含最核心的 `k8s_connector.go`/`process_node_events.go`）——实为事件接入分发中枢（图谱 L04）。

**ADR 类**
5. **ADR 双 055 撞号**：`docs/designs/055-nvcre-certification-monitor.md` 与 `055-pod-drain-policies.md` 并存，违反 `docs/designs/README.md:9` "Never reuse a number" 铁律；前者入索引（README.md:71）、后者未入却被 `063-pod-drain-policies-owner-kinds.md:7` 引用——引用 ADR-055 须消歧。
6. **ADR 索引漏收两篇**：designs/ 目录 61 篇编号 ADR vs 索引 59 行（`050-gpu-system-services-npd-checks.md` 与 `055-pod-drain-policies.md` 未入）。
7. **ADR 文件名与正文标题编号错位**：`030-grpc-tls-authentication.md` 正文题 "ADR-029"、`049-node-validation.md` 正文题 "ADR-045"——以文件名编号为准。
8. **ADR 数量口径**：目录 63 个 md = 61 篇编号 ADR + README + template；号段 001-063 缺 057/060/061 合法（README.md:12 "Gaps are expected"）。

**路径与命名类**
9. **MaintenanceRequest 类型路径勘误**：ADR-051 计划的 `api/v1alpha1/maintenance_request_types.go`（designs/051:60）从未落地——实际 `lifecycle-manager/api/v1alpha1/maintenancerequest_register.go`+`maintenancerequest_json.go`（无下划线、无 types 后缀）。
10. **k8s-datastore 目录名 ≠ chart 依赖名**：目录 `charts/k8s-datastore/`，Chart.yaml 依赖名 `k8sdatastore-crds`（values.yaml:358 开关键 `k8sdatastoreCrds` 随依赖名）。
11. **commons/pkg/lambda 不是 CEL**：`lambda/client.go:15` 是 Lambda Cloud API 客户端；CEL 求值在 commons/pkg/celevent 与 celfields。
12. **umbrella Chart.yaml 无 cert-manager 依赖与 kubeVersion 字段**：22 个依赖全是组件子 chart（实测 grep 两词皆无）。

**Helm 体系类**
13. **子 chart 计数**：`charts/` 22 个子目录 = Chart.yaml 22 个依赖（含 k8sdatastore-crds）；"21 个"口径过期。
14. **Helm 测试双口径**：umbrella 顶层 `tests/` 18 份 + 13 个子 chart 内嵌 `tests/` 38 份 = 全栈 56 份。
15. **values overlay 计数**：23 个 `values-*.yaml` overlay + `values.yaml` 主面板 = 24 个 values 系文件（"24 overlay"是含主文件的口径）。默认开启 4 个观测组件（gpuHealthMonitor/syslogHealthMonitor/labeler/metadataCollector，values.yaml:319-342），动作组件全关；但 labeler/metadata-collector **写节点标签与 Pod 注解**——"安全默认=零写操作"是过度简化。

**测试与杂项类**
16. **tests/uat 云环境实为三个**：aws（eks 脚本+nodegroup 模板）/gcp（cluster/project tf）/kind 有效，`azure/` 与 `oci/` 是**空占位目录**（find 无文件）。
17. **tests/helpers/kube.go 3756 行**：图谱单文件最高密度（120 节点/215 边）——测试工具库真密度，非分片缺陷；引用"批超限"结论时须带此语境。
18. **fern/ 是 API 文档发布链非 proto 契约**：fern.config.json+docs.yml+versions/v1.29.0.yml+convert_callouts.py（GitHub admonition 转换），配套 fern-docs-ci.yml；proto 契约在 data-models/protobufs 与 api/proto 两棵树。

**worker 终稿甄别补充**
19. **values-nvcre.yaml 不开 nvcre 组件**：`nvcreCertificationMonitor` 在该 overlay 零出现——它实开 `lifecycleManager`+`fault-quarantine.validation`（ADR-049 节点验证线）；"ADR-055 nvcre→values-nvcre.yaml"的映射不成立，nvcre-certification-monitor 开关需另行开启。tilt 族 overlay 实为 10 个非 9（多出 tls-disabled-percona，mongodb 变体构成 2×2 矩阵）。
20. **ADR-050 predicate 落地版更宽松**：ADR 文中策略样例带 reason 三元组匹配，`values-npd-gpu-services.yaml` 落地版仅匹配 type+status；另 postgresql 子 chart 的 condition 是全仓唯一非 `global.` 前缀例外（`charts/postgresql/Chart.yaml:30`）。

**其他钉版**：12 条自引用 imports 甄别（10 条合法 Go 外部测试包模式、1 条字符串字面量假阳性）最终图谱 self-loop=0；孤儿夹具 `tests/data/fr-multi-template-config.yaml` 全仓无消费方，勿参考；生成物（`*.pb.go`/`*_pb2.py`/`zz_generated.deepcopy.go`）遍布全仓勿手改。

## 附注

- ONBOARDING 与 explain 的字数口径 = 不计空白字符；explain 新 4 篇 4799-4966 字（09 达标 4800 内，07/08/10 微超 1-4%），内容密实锚实证，如实标注。
- 331 条批阶段甄别笔记收割于仓内 `.understand-anything/NOTES-DIGEST.md`。
- 姊妹产物：讲透NVIDIA/ 组内其余仓（DCGM/go-nvml/gpu-operator/NCCL 等 300+ 仓）见组级索引。
