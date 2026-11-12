# 07 · agent_ssas 事件流水线：从 Rail 钩子到 threat_log 的全链路

## 一、角色定位

agent_ssas 是本仓四件套的"态势感知"（SSAS = Security Situational Awareness System）子系统，与 agent_shield（事前拦截）、jiuwenbox（沙箱执行）不同，定位是**旁路观测与分析**：收进 Agent 运行时每个生命周期事件，过检测模块流水线，产出风险报告与 OCSF 威胁日志，默认不阻断业务。

整条流水线的物理形态是五个模块的接力：

```
AgentSSASSecurityRail (openjiuwen 宿主侧采集)
   → access_adapter (接入适配：进程内 AgentSSASBackend / HTTP AgentSSASRemoteBackend)
   → data_preprocessor (raw_event → UnifiedEvent 列表 + 聚合事件)
   → analysis_pipeline (订阅分发：建模→分析→存储→呈现)
   → presentation/threat_log (OCSF 报告落盘 JSON)
```

所有跨仓边界被压缩到一个 32 行的协议文件：`AgentSSASBackendProtocol`（`agent_ssas/src/agent_ssas/core/framework/access_adapter/protocol.py:16-32`），`typing.Protocol + runtime_checkable` 声明唯一方法 `report_event(raw_event: dict) -> RiskAssessment`。SecurityRail 侧只认这个协议、不 import 引擎内部——进程内模式直接持有 `AgentSSASBackend`（零网络延迟），HTTP 模式换成 `AgentSSASRemoteBackend`（POST 转发远端 FastAPI），Rail 代码一行不改。

一个易误判点：`AccessAdapter`（adapter.py:21-44）看似入口，实为 0.1 版"薄包装"——构造固定 new 一个 `AgentSSASBackend`（adapter.py:44），`report_event` 纯转发（adapter.py:66），给"未来多后端切换"留占位。

## 二、内部结构

### 采集端：SecurityRail 的六个管线事件

`AgentSSASSecurityRail` 挂在 openjiuwen 宿主的 Rail 体系里，`priority=80`（agent_ssas_security_rail.py:61），低于 PermissionInterruptRail(90) 和 SafetyPromptRail(85)——排序刻意：它后于其他安全 Rail 执行，因此能"观察"前序 Rail 的 deny 决策标志。0.1 版只实现 6 个走决策管线的事件（`_PIPELINE_EVENTS`，agent_ssas_security_rail.py:33-41）：BEFORE/AFTER_INVOKE、BEFORE/AFTER_MODEL_CALL、BEFORE/AFTER_TOOL_CALL；另 7 个直接覆写钩子的事件全是 TODO 注释（agent_ssas_security_rail.py:185-214）。

`run_security_check`（agent_ssas_security_rail.py:164-180）内部是四模块接力：EventBuilder 构建 raw_event → EventFilter 过滤 → EventReporter 上报并映射决策。EventFilter 的关键合成逻辑：当 BEFORE_TOOL_CALL 事件上发现 `ctx.extra["_skip_tool"]=True`（PermissionInterruptRail 已 deny），会把普通生命周期事件改写为安全检测事件 `permission_interrupt_tool`、event_class 置 `security`（event_filter.py:37-45），并按 RejectResult 前缀 `[PERMISSION_DENIED]` 区分"策略拒绝(medium)"与"用户 ask 模式拒绝(low)"（event_filter.py:88-93）。MODEL 事件上 `SecurityInterrupt` 静默降为 `SecurityReject`（agent_ssas_security_rail.py:113-118）——打断模型调用流没有意义。

### 引擎端：三层处理结构

`AgentSSASBackend.report_event`（agent_backend.py:139-219）是引擎的总入口，处理顺序固定：

1. `_ensure_initialized()` 防竞态守卫（agent_backend.py:164-171）：jiuwenswarm 集成层以 fire-and-forget 方式调 initialize()，首个事件到达时初始化可能未完成、订阅表为空会导致漏检测，所以入口先等待；
2. raw_event 持久化到 `raw_events` 表（agent_backend.py:174-177，失败仅记日志继续）；
3. `DataPreprocessor.parse` 展开为 UnifiedEvent 列表；
4. 逐事件 `pipeline.run`（agent_backend.py:185-203），每个 UnifiedEvent 还会补齐 event_id/event_type 等字段后写入 `events` 表；
5. `_merge_assessments` 聚合（agent_backend.py:298-345）：取最高风险等级为基座，合并 detected_threats/recommended_actions（去重保序），空 actions 兜底 `["log"]`。

### 预处理器：source 分发与聚合栈

`DataPreprocessor.parse`（preprocessor.py:82-117）按 `common.source` 字段查类级注册表 `_parsers`（preprocessor.py:56），未注册则落默认解析器 `AgentSSASPreprocessor`。解析产物可能是"派生事件 + 基础事件"列表——派生事件（如 session_start）直接透传，只有最后一个基础事件入聚合栈（preprocessor.py:109-115）。

`EventAggregator` 维护一个纯 list 聚合栈：`tool_output` 到达时倒序找同 `tool_call_seq` 的 `tool_input` 合并成 `one_toolcall_event`（event_aggregator.py:67-117）；`llm_output` 触发 `one_llmcall_event`（连同其间工具调用一起 `del self._stack[start_index:]`，event_aggregator.py:171）；`invoke_end` 触发最外层 `one_interaction_event`（event_aggregator.py:175-231）。三分支分发就一个 if 链（event_aggregator.py:59-65）。找不到配对起始事件不报错，用结束事件自身内容兜底构造（event_aggregator.py:99-102）——乱序容忍优先于精确性。

### 流水线：notify/auth 双模式分发

`ThreatAnalysisPipeline.run`（pipeline.py:107-158）拿到事件后先 `get_subscribers_with_mode(event_type)` 查订阅表，然后按模式分流：**notify 订阅者** `asyncio.create_task` 丢后台（pipeline.py:141-146），`report_event` 立即返回无风险结果；**auth 订阅者** `await` 同步等待（pipeline.py:149-155），结果聚合进返回值；全 notify 或无订阅直接返回无风险 `RiskAssessment()`（pipeline.py:130-132, 158）。

每个模块的流水线是四步（pipeline.py:360-465）：`modeler.build_model` 建模 → `analyzer.analyze` 分析 → 模块结果库 result.db 持久化 → threat_log 呈现。任何一步异常都只跳过该模块（pipeline.py:385-400），存储/呈现失败不影响报告返回（pipeline.py:447-463）。报告被流水线反向注入 `aux_ids`/`event_node`/`module_name`/`analytic_type_id`（pipeline.py:411-432）——timestamp 注入的动机写在注释里：缺失时回退 0.0 会让 result_store 的 TTL 清理把报告"立即误删"（pipeline.py:418-421）。

## 三、外部连接

- **上游**：openjiuwen agent-core 的 Rail 体系。Rail 基类提供 `_run_and_apply`/`apply_security_decision`；本 Rail 覆写 `_run_and_apply` 构建 `ExtendedSecurityCheckContext` 填十余个 ID 字段（agent_ssas_security_rail.py:78-120）。依赖方向：引擎包不依赖 openjiuwen，`backend_client/openjiuwen/` 这层才依赖。
- **jiuwenswarm**：仓内 `patches/jiuwenswarm_ssas_online.patch` 与 `_local.patch` 把流水线接入 swarm 宿主（online=HTTP 模式、local=进程内模式）。
- **HTTP 模式**：`AgentSSASRemoteBackend` 用 httpx POST `/api/v1/events`（agent_remote_backend.py:74-82），服务端同名端点懒初始化 backend 后调 `report_event`（http_server.py:118-133）。默认绑定 `0.0.0.0:8443`（settings.py:53-54）——无 token 配置时这是一张对全网裸奔的事件收集口。
- **存储**：主库 `ssas_core.db`（events/raw_events/alerts 三表）+ 每模块独立 `process.db`/`result.db` + `reports/threat_log/*.json`（threat_log.py:52-53）。
- **下游消费**：alerts 表（`_write_alerts`，pipeline.py:178-235，alert_id 格式 `{event_id}_{module_name}` 防多模块互覆）与 OCSF Detection Finding JSON（threat_log.py:79-96）。

## 四、数据流

以一次"工具被权限拒绝"的旅程为例：

1. 宿主触发 BEFORE_TOOL_CALL，PermissionInterruptRail（priority 90）先跑，写 `_skip_tool=True` 与 RejectResult 进 `ctx.extra`；
2. AgentSSASSecurityRail（priority 80）后跑，EventBuilder 构建三层结构 raw_event（common/payload/metadata）；
3. EventFilter 看到 `_skip_tool`，把 event_type 改写为 `permission_interrupt_tool`、event_class=`security`，payload 注入 risk_source/risk_type/risk_level/deny_reason（event_filter.py:41-45）；
4. EventReporter 经 protocol 调 backend（进程内直进引擎 / HTTP 序列化走网络）；
5. 引擎持久化 raw_event → 预处理解析出基础事件（+可能的聚合事件）→ 逐事件入流水线；
6. `security_rail_detection` 订阅了 `permission_interrupt_tool`（module.yaml:6，notify 模式），后台执行：BlankDataModeler 透传 → SecurityRailAnalyzer 按 deny_reason 定级（user_reject 降级、policy_deny 维持，security_rail_analyzer.py:109-117）→ 报告进 result.db + OCSF JSON 落盘；
7. 因为是 notify 模式，第 4 步的 `report_event` 早在检测开始前就返回了无风险 RiskAssessment；EventReporter 按 observe_only 策略映射为 SecurityAllow——业务零感知。

**聚合事件展开语义**（本流水线最精妙的一处）：检测模块在 module.yaml 里订阅的是聚合事件（如 `one_toolcall_event:auth`），manager（08 篇的 module_manager/manager.py）加载时按 `_AGGREGATE_EVENT_MAP`（:41-49）展开为 2~6 个基础事件子订阅，**auth 模式只落在结束事件上，起始事件一律 notify**（:309-319，注释见 :16-17 与 `_AGGREGATE_END_EVENT` :52-56）。原因直白：auth 意味着同步等待+可能阻断，"工具还没执行完"就去阻断没有意义——只有 tool_output 到达（事情已发生、上下文完整）时同步检测才有语义。这同时保证聚合事件订阅者在整条事件链上都有数据可吃（起始事件以 notify 身份喂给 modeler 积累状态），但只有结束事件会卡住调用方。

## 五、设计决策与权衡

1. **Protocol 而非 ABC**：跨仓契约用 `runtime_checkable` Protocol（protocol.py:16），引擎侧 `AgentSSASBackend` 隐式实现（agent_backend.py:30 类定义无基类）。好处是引擎包零依赖、宿主可鸭子类型注入任意 mock；代价是静态检查器只在显式 `isinstance` 时才校验。
2. **fail-open 三层嵌套**：EventReporter 异常返回 `SecurityAllow()`（event_reporter.py:44-51）；backend report_event 大 try 异常返回 `RiskAssessment()`（agent_backend.py:207-212）；HTTP 客户端网络异常同样合成无风险（agent_remote_backend.py:83-87）。观测系统挂了不能拖死主业务——与 shield/box 的 fail-closed 分区判据见 12 篇。
3. **auth 超时的策略化**：auth 订阅者超过 `auth_timeout`（默认 2.0 秒，settings.py:75）未返回时，按 module.yaml 的 `auth_timeout_policy` 合成默认报告（pipeline.py:279-298）：`allow` 合成无风险（pipeline.py:342-358），`reject` 合成 high 风险+block 建议（pipeline.py:325-341）。超时不抛异常，而是变成"可配置语义的报告"进入聚合通道——把故障处理统一进数据流。
4. **现状：auth 通道是预留的**。两个内置模块的 module.yaml 都没有 `:auth` 后缀，官方文档明言"当前内置模块全部是 notify 模式……auth 是为未来参与决策的检测模块预留的执行通道"（agent_ssas/docs/zh/explanation/detection-pipeline.md:106）。auth 分支被完整实现与测试，但生产路径零流量。
5. **告警落库从 backend 移入 pipeline**：注释留有考古证据——"告警写入已移至 ThreatAnalysisPipeline(统一覆盖 notify/auth 模式)"（agent_backend.py:201）。旧设计里 notify 后台任务无人 await、告警可能丢失；移到 pipeline 后两条路径的报告统一走 `_write_alerts`（pipeline.py:153-154, 173-176）。
6. **TTL 清理三入口**：启动一次（agent_backend.py:117）+ 每 100 次上报触发（`_TTL_CLEANUP_INTERVAL=100`，agent_backend.py:26-27, 213-219）+ 周期任务兜底（默认 24h，agent_backend.py:228-268）。

## 六、新人提示与坑

- **路径噪音**：`agent_ssas.core.framework.*`（引擎零件）、`agent_ssas.core.detection_modules.*`（可插拔检测器）、`backend_client/openjiuwen/`（宿主侧胶水）三个"core"极易迷路，先分层再读码。
- **agent_moss 幽灵模块**：agent_ssas/README.md:52 宣称有 3 个内置检测模块（含 agent_moss），但 `detection_modules/` 目录实际只有 security_rail_detection、test_detection（默认 disabled）和 common 组件目录。agent_moss 只存在于设计文档与测试报告里，发行包中没有——按文档排障会找不到文件。
- **0.0.0.0:8443 默认暴露**（settings.py:53-54）：HTTP 服务端默认监听全网卡；`http_token` 默认 None 意味着 TokenAuthMiddleware 压根不挂载（http_server.py:114-116）。若真要起 HTTP 模式，先配 token。
- **SQLite WAL 句柄**：Windows 上不显式 `close()` 会导致 `-wal/-shm` 文件锁住、目录删不掉（agent_backend.py:81-86 注释）。Rail 侧 `uninit` 钩子用 `asyncio.ensure_future` 调度异步 close，无事件循环时静默跳过、靠宿主显式调 `rail.close()` 兜底（agent_ssas_security_rail.py:141-158）。
- **聚合栈无容量上限**：EventAggregator._stack 是裸 list（event_aggregator.py:34），长会话+乱序流下持续增长；TTL 清理只管库和文件不管内存栈，`clear()` 存在但主流程无人调用。
- **事件表双写**：raw_events 与 events（解析后 UnifiedEvent）都落库，排查"解析丢字段"对照两表即可。
