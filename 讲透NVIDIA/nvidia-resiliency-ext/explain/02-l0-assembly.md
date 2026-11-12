# 02 · L0 证据组装层：5595 行确定性引擎

## 角色定位

`l0/assembly.py`（5595 行，全仓最大单体）是 restart_agent 的"证据警察"：在 LLM 介入之前，把原始日志、模式匹配结果与集群上下文组装成一份可追溯的 L0 决策上下文（L0Bundle）。它完全确定性——同样的日志永远得到同样的 bundle，这层的选择直接决定 L1 模型能看到什么、L2 能核验什么。设计文档 docs/design/attribution/restart_agent/L0A.md 与 L0B.md 是权威出处。

## 内部结构

assembly.py 的关键构件（行号 grep 实证）：

- 观察累积：`L0ObservationAccumulator`（assembly.py:550，Sequence[LogLine] 子类）；
- 入口函数：`build_l0_bundle`（:835）与 `build_l0_bundle_from_observations`（:857）；
- 证据检测：`_detect_evidence`（:880）——识别 `_RdmaPortLifecycleEvent`（:361）、`_DistributedTimeoutWave`（:414）、`_TimedOperationEvent`（:402）等模式事件；
- 上下文化：`_contextualize_evidence`（:965）产出 `_ContextualEvidence`（:511）与 `_ContextWindowSelection`（:527）；
- 实体挂接：`_attach_operation_artifact_entity`（:1081）、`_attach_failed_path_entity`（:1134）把证据绑到失败路径实体；
- 装配与自检：`_assemble_bundle`（:1170）、`_selection_summary`（:1227）、`_validate_l0a_selection_accounting`（:1297）——L0A 选择记账有专门校验。

兄弟件：`registry.py`（581 行）维护模式签名注册表——`SignatureRegistryRow`（registry.py:17）、`NcclRdmaPortLifecycleMatch`（:24），配套设计文档 PATTERN_REGISTRY.md；`decision.py:39`（build_decision_evidence）把 bundle 投影成决策证据、`canonical_identity_anchor_line`（decision.py:318）选身份锚行；projection.py（1321 行）、narrative.py（511 行）做投影与叙事（`build_failure_narrative` narrative.py:16、`build_decision_evidence_view` narrative.py:230、`narrative_references_resolve` narrative.py:293 校验叙事引用可回解）；codec.py（306 行）编解码（`write_l0_bundle` codec.py:40 / `read_l0_bundle` codec.py:55）；streaming.py（486 行）支撑流式消费；retry_lifecycle.py（69 行）管重试生命周期。

## 外部连接

上游吃 infrastructure/log_source.py 的 ChunkedLogReader（内存/索引文件两模式，快照与回放两种读法）；下游把 L0Bundle 交给 l1（工具面 l1/tools.py 1012 行把它喂给 LLM）、l2/grounding.py:15（model_visible_line_numbers）用它的行号做防幻觉核验、l4/policy.py 据其证据强度做决策。observability/trace_builder.py 会导出 L0 过程轨迹。

## 数据流

日志行 → `L0ObservationAccumulator`（:550）累积 → `_detect_evidence`（:880）跑模式注册表（registry.py）→ 命中的模式事件 + `_RegistryObservation`（:448）→ `_contextualize_evidence`（:965）选上下文窗口 → `_attach_*_entity`（:1081/:1134）挂实体 → `_assemble_bundle`（:1170）产出 L0Bundle → `build_decision_evidence`（decision.py:39）/ `_select_decision_context`（decision.py:231）投影 → `canonical_identity_anchor_line`（decision.py:318）定锚 → narrative/projection 生成人可读叙事。`_validate_l0a_selection_accounting`（:1297）保证"选了多少、为什么选"账目平。

## 设计决策

- **先登记后匹配**：模式知识集中在 registry.py 的签名表而非散落在 if-else 里——新增一种故障模式只需加行注册（PATTERN_REGISTRY.md 定义流程）。
- **L0A/L0B 分册设计**：L0A（证据选择与记账）与 L0B（叙事投影）拆成两份文档两个阶段，记账校验（:1297）插在中间当关卡。
- **数值安全**：`_fast_numeric_rank`（:818）等 helper 对 rank 解析做了快速路径，避免 5595 行里 O(n²) 字符串操作。
- **身份锚是一等公民**：canonical_identity_anchor_line（decision.py:318）确保每份证据都能钉回一行真实日志，供 L2 grounding 反查。

## 新人提示

不要通读 5595 行：从 build_l0_bundle（:835）出发只追主链 8 个函数；先读 L0A.md 的图再看代码；用 `_detect_evidence`（:880）里的模式列表反查 registry.py 签名；测试侧在 test_restart_agent.py 里搜 "l0" 相关用例与 fixtures/数据目录；改 registry.py 前先读 PATTERN_REGISTRY.md 的准入标准。
