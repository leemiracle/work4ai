# nvidia-resiliency-ext 新人上手指南（ONBOARDING）

> 知识底座：understand 图谱 2875 节点 / 3677 边 / 14 层 / 16 步 tour，fingerprints 608 文件基线 @ commit `af2a108b`（2026-10-27，Merge PR #464 timeout-dump-tools）。
> 本文所有行号锚均经源码 grep 实证；口径说明见各节。

## 1. 项目定位与数字底座

**NVIDIA Resiliency Extension（NVRx）是 PyTorch 分布式训练的"弹性容错层"**：在 SLURM 作业不重新分配节点的前提下完成进程内重启（Fault Tolerance）、用异步/本地双体系检查点把故障损失压到最小（Checkpointing）、用 CUPTI 扩展识别慢 rank（Straggler Detection），并用一套 LLM 归因代理（restart_agent）在每次故障后自动回答"为什么挂、要不要重启"。README.md 开篇定位是 "maximizes goodput ... quickly detecting faults at runtime and resuming training automatically"——四大能力（README.md Core Components 节）+ 归因一条暗线，构成全仓骨架。

数字底座（全部 wc 实证）：

| 事实 | 数值 | 锚 |
|---|---|---|
| 全仓最大单体 | `l0/assembly.py` 5595 行 | `src/nvidia_resiliency_ext/attribution/restart_agent/l0/assembly.py` |
| 用户主入口 | `fault_tolerance/launcher.py` 4008 行 | `src/nvidia_resiliency_ext/fault_tolerance/launcher.py` |
| 归因主测试 | `tests/attribution/unit/test_restart_agent.py` 11091 行、8 个顶层测试类 | `tests/attribution/unit/test_restart_agent.py:154` |
| 数据模型总集 | `restart_agent/models.py` 2031 行、69 个类 | `models.py:1396`（normalize_restart_agent_request） |
| 设计文档 | `docs/design/attribution/restart_agent/` 恰 21 篇 | DESIGN.md / L0A.md / L1.md / L2.md / L3.md / L4.md / TOOLS.md / TAXONOMY.md 等 |
| proto 契约 | 三件共 145 行 | `shared_utils/proto/nvhcd.proto:1`、`log_aggregation.proto:1`、`nvrx_interface.proto:1` |

CLAUDE.md 是官方给 AI 协作者的架构导览（本仓自身就用 agent 协作开发，见 CLAUDE.md "Project Overview" 节），新人第一读应是它 + README.md，第二读才是本文。

## 2. 构建体系与技术栈

- **构建入口** `build.py`：`_compile_protos`（build.py:98）把三个 proto 在一次 protoc 调用里编译成 `*_pb2.py`/`*_pb2_grpc.py`（生成物 gitignore，装包时再生成）；`_skip_ext_build`（build.py:45）对应环境变量 `STRAGGLER_DET_SKIP_CUPTI_EXT_BUILD=1`，无 CUDA/CUPTI 环境可跳过 C++ 扩展编译。
- **CUPTI 扩展**是 pybind11 工程：绑定模块入口 `cupti_src/cupti_module_py.cpp:33`（`PYBIND11_MODULE(nvrx_cupti_module, m)`），C++ 侧主体 `CuptiProfiler.cpp:96`（initializeProfiling）到 `:158`（bufferRequested 回调），配 `BufferPool.cpp` 与 `CircularBuffer.h`。
- **CI 五条**（`.github/workflows/`）：build_docs.yml / cherry_pick_release.yml / claude_review.yml / lint_code.yml / unit_test.yml——文档构建、发版 cherry-pick、AI 评审、black+isort+ruff、单测各有独立管线。
- **质量工具链**：`black==24.10.0 / isort==5.13.2 / ruff==0.6.9`，行宽 100（pyproject.toml）。
- **平台**：Python 3.12/3.14、PyTorch>=2.8.0、CUDA>=12.8、NVML>=535（GPU 健康检查要 570，README.md Platform Support 表）。
- **文档**：Sphinx 工程 `docs/source/`（fault_tolerance 23 篇、checkpointing、straggler_det、attribution 子树，md/rst 共 85 件），`sphinx-build -b html docs/source public/` 要求零警告。

## 3. 架构分层地图（图谱 14 层收敛为五大域）

图谱 14 层（L01-L14）按耦合度可收敛成五大域，建议按此记忆：

1. **归因域（L02-L08，图谱最大块）**：restart_agent 运行时核心（L02）→ L0 证据组装（L03）→ L1-L4 分层分析（L04）→ 基础设施与可观测（L05）→ orchestration 编排与后处理（L06）→ MCP 集成与 legacy_logsage（L07）→ nvrx-attr skills（L08）。`src/nvidia_resiliency_ext/attribution/` 下 restart_agent 子包就有 57 个 .py。
2. **容错域（L10）**：launcher/rank_monitor/rendezvous/timeout_dump/control_plane。
3. **检查点域（L11）**：async_ckpt 五件 + local 体系（base/basic state_dict、ckpt_managers/、replication/）。
4. **横切域（L09、L12）**：straggler CUPTI 扩展与 trace_analyzer；shared_utils（日志三件、health_check、telemetry、proto）。
5. **服务与外围（L01、L13、L14）**：工程治理与文档；attrsvc/smonsvc 常驻服务；示例与 238 件测试基座。

跨域的关键"接缝"只有两条：**launcher.py 的归因钩子**（见第 4 节）与 **attrsvc 的 restart_agent_backend 桥**（见第 6 节）。理解这两条缝，五域就拼成了整图。

## 4. 核心链路一：FT 容错运行时（挂了怎么办）

`ft_launcher` CLI 的实现全在 `fault_tolerance/launcher.py`（4008 行）：

- **LocalElasticAgent**（launcher.py:351）继承 torch 的 `SimpleElasticAgent`（launcher.py:50-52 import 自 `torch.distributed.elastic.agent.server.api`）——它包装训练函数为多周期 FT 循环，每个 cycle 失败后决定重启或终止。
- **重启决策三优先级**（launcher.py:694 注释块起）：attribution STOP 判定 > 进展判定 > 重启预算。launcher.py:774-784 明确注释 "An attribution STOP preempts any restart decision"——归因结论可以一票否决重启；且只有持有 attribution client 的节点能锁存判定（防多节点竞争）。终止 cycle 触发最终归因在 launcher.py:2004-2005（`agent._request_terminal_attribution()`，方法定义 launcher.py:1117）。
- **心跳状态机**：`rank_monitor_server.py:125`（RankMonitorServer，asyncio gRPC/TCP 服务）+ `rank_monitor_state_machine.py:25`（RankMonitorState 枚举）与 `:35`（RankMonitorStateMachine，非法迁移抛 `InvalidStateTransitionException` rank_monitor_state_machine.py:19）。服务端按消息类型分发：`_handle_unhealthy_node` rank_monitor_server.py:260、`_handle_timeout` :266、`_handle_init_msg` :379。
- **段超时模型**：用户代码 `begin_section(name)/end_section(name)` 圈出带独立超时的命名区间，段外用默认超时——这是 NVRx 检测 hang 的核心语义（examples/fault_tolerance/train_ddp_sections_api.py 是最小可跑示例）。
- **集合通信健康**：`ft_rendezvous_barrier.py:125`（RendezvousTimeout）、`:200`（RendezvousSettings）、`:293`（GroupRankStatus 枚举）维护自定义 rendezvous 屏障；`segment_health_check.py` 与 `c10d_monkey_patch.py` 补 c10d 侧健康探测。
- **timeout_dump 家族**（989 行八件，PR #464 新入）：超时现场抓取器——`cuda_gdb.py:23`（CudaGdb，ToolCapture 子类）、`pyspy.py:37`、`gdb.py:54`、`ptrace.py:24`，调度在 `collector.py`（256 行）与 `capture.py`（288 行），配置 `config.py`（167 行）。设计文档 `docs/source/fault_tolerance/timeout_dump.rst`。
- **控制面**：`control_plane.py:69`（ControlServices）与 `:129`（_create_tcpStore）——独立进程承载 rank monitor 等服务，launcher 主进程通过 TCPStore 握手。

## 5. 核心链路二：restart_agent 归因代理（L0-L4 五层流水线）

restart_agent 是全仓智力密度最高的部分，21 篇设计文档（`docs/design/attribution/restart_agent/`）与 11091 行测试都为它服务。五层流水线：

- **L0 证据组装（确定性，无 LLM）**：`l0/assembly.py`（5595 行）把多源日志组装成决策上下文——`L0ObservationAccumulator`（assembly.py:550，Sequence[LogLine]）累积观察，`build_l0_bundle`（:835）产出 L0Bundle；证据检测 `_detect_evidence`（:880）识别 RDMA 端口生命周期、分布式超时波等模式，上下文化 `_contextualize_evidence`（:965），最终装配 `_assemble_bundle`（:1170）。模式知识在 `l0/registry.py`（SignatureRegistryRow :17、NcclRdmaPortLifecycleMatch :24，设计文档 PATTERN_REGISTRY.md）。`l0/decision.py:39`（build_decision_evidence）与 `:318`（canonical_identity_anchor_line——跨次尝试的稳定身份锚）把 bundle 投影为决策证据；projection.py（1321 行）与 narrative.py（511 行）做投影与叙事。
- **L1 LLM 工具调用分析**：`l1/openai_compatible.py`（2185 行，L1 最大件）——`LlmConfig`（:63）、`ToolLoopSession`（:271）、`ToolRoundExecutor`（:374）实现多轮工具循环；错误分型 `LlmCallError`（:223）/`ModelEvidenceParseError`（:240）/`ModelEvidenceContractError`（:244）。工具面定义在 `l1/tools.py`（1012 行）与 tool_contracts.py；故障类别表 `l1/categories.py:102`（CATEGORIES）从 `categories.json` 装载并校验 schema_version（categories.py:23，`restart_agent.categories.v1`）；响应合法性由 response_contract.py（L1ResponseContract）与 validation.py 把守。
- **L2 落地与防幻觉**：`l2/grounding.py:15`（model_visible_line_numbers）/`:39`（model_visible_line_texts）把"模型看到的行号"固化为可核对事实——LLM 引用的每行证据都必须真实存在于工具回传数据；audit.py 与 failure_facts.py 把输出落为可追溯事实链。
- **L3 历史评估**：`l3/history.py:51`（evaluate_history）、`:233`（evaluate_cycle_history）、`:286`（_evaluate_job_progress）——跨 cycle 累积"这次故障和上次是不是同一个"的上下文。
- **L4 策略决策**：`l4/policy.py` 依据 L0-L3 证据输出重启/升级/停止建议（对应 launcher 的 attribution STOP 语义）。

运行时编排：入口 `cli.py:39`（main）→ `pipeline.py:38`（RestartAgent 门面类，仅 213 行）→ 实际分发在 `single_run.py`（466 行）与 `multi_route.py`（837 行，多路由场景比 pipeline.py 大四倍）；`decision_pipeline.py`（826 行）与 `causality.py`（138 行）构造因果链；`attempt_records.py`（378 行）跨次尝试记录；`identity.py`（200 行）做 fingerprint/rank/GPU/node 身份归一。可测试性注入点在 `runtime.py`（Clock/Sleeper/ExecutorFactory 抽象）与 `agent_runtime.py`（571 行）。

**服务化**：`orchestration/http_api.py:70`（post_log）/`:93`（get_log_response）把归因做成 HTTP 服务；`postprocessing/slack.py:88`（send_slack_notification）与 `:148`（should_notify_slack）推结果进频道；`coalescing/`（coalescer.py + coalesced_cache.py，共 1117 行级）把重复触发合并去抖。**MCP 工具面**：`mcp_integration/mcp_server.py:44`（NVRxMCPServer，319 行）+ `registry.py`（AttributionModuleRegistry，322 行）+ `mcp_client.py`（553 行）+ `server_launcher.py`（182 行）——restart_agent 与 fr_analyzer 都被注册为 MCP 模块供 LLM/外部 agent 调用。**旧栈**：`legacy_logsage/`（nvrx_logsage.py、combined_log_fr.py、combined_log_fr_mcp.py、llm_merge.py、slurm_parser.py、splitlog.py、tracked_jobs.py）是 restart_agent 前身，故意不进 wheel（CLAUDE.md "legacy LogSage" 节），测试需 `PYTHONPATH=src`。

## 6. 核心链路三：检查点、掉队者与常驻服务

- **async_ckpt**：`async_ckpt/core.py`（1117 行）定义 AsyncRequest/AsyncCaller（线程/进程/持久 worker 三形态）/AsyncCallsQueue 调度与 finalize 队列；`filesystem_async.py:180`（FileSystemWriterAsync，继承 PyTorch FileSystemWriter）与 `:86`（ConsistentDataIdentifier）是落盘主体。用法示例 examples/checkpointing/async_ckpt.py。
- **local 检查点**：`checkpointing/local/`——base_state_dict.py / basic_state_dict.py + `ckpt_managers/`（base_manager.py、local_manager.py）+ `replication/`（group_utils.py、strategies.py：进程组工具与复制策略），为频繁快照优化。
- **straggler**：主 API 在 `straggler/straggler.py`（407 行）——`CallableId`（:35）、`CustomSection`（:66）、`Detector`（:86，检测器主类，straggler.py:86）；`interval_tracker.py:24`（ReportIntervalTracker）控上报节奏，`reporting.py:154`（ReportGenerator）+ `:32`（StragglerId）做统计评分与跨 rank all-gather；`statistics.py` 仅 35 行（Statistic 枚举 :19）。Python 绑定 `cupti.py` 只有 95 行——真正扩展在 cupti_src（见第 2 节）。
- **trace_analyzer**：`trace_analyzer.py:17`（TraceAnalyzer）分析 PyTorch Profiler/Flight Recorder 轨迹；`fr_attribution.py` 做 FR 首次故障归因，`fr_support.py` 提供 dump 路径发现与 MCP 响应转换。
- **attrsvc**（服务化归因）：`services/attrsvc/`——FastAPI 应用 `src/nvidia_resiliency_ext/services/attrsvc/app.py:131`（create_app，:18 import FastAPI）；桥接层 restart_agent_backend.py（1556 行，把 HTTP 请求转成 restart_agent 运行）；通知 slack.py（875 行，注意与 postprocessing/slack.py 174 行是两个不同文件）；规格书 ATTRSVC_SPEC.md；部署三态 deploy/{Dockerfile, kubernetes.yaml, nvrx-attrsvc.service} 外加 slurm.sbatch/supervise/snapshot 脚本。
- **smonsvc**（SLURM 作业监视）：`services/smonsvc/`——`monitor.py:24`（SlurmJobMonitor）轮询作业状态，经 attrsvc_client 触发归因。
- **skills**：`src/nvidia_resiliency_ext/skills/nvrx-attr/`（注意在顶层 skills/ 不在 attribution/ 下）——主 SKILL.md + fr-analysis、log-analysis、fault-injection-loop 三个子技能（各带 SKILL.md），脚本 score_attribution.py 评分与 fr-analysis/scripts/fr_attribution.py。
- **shared_utils 横切件**：`health_check.py`（2267 行）——GPUHealthCheck（:267）、NicHealthCheck（:463）、NicLinkStateHealthCheck（:736），NVML 经 `with_pynvml_lock`（:105）串行化；日志聚合三件 grpc_log_server.py（904 行）/grpc_log_leaf_server.py（624 行）/log_aggregator.py（183 行）配 log_aggregation.proto；inject_fault.py（363 行）是故障注入测试底座。

## 7. 测试体系与质量基座

- **归因单测 126 件**的龙头是 `tests/attribution/unit/test_restart_agent.py`：11091 行、8 个顶层测试类（:154 RestartAgent 子类起）、343 个 def（含方法；常被引用的"259 函数"是旧提取口径）。测试用大量替身控制 LLM 行为：_FakeEvidenceExtractor（:541）、_BlockingEvidenceExtractor（:592）、_RetryOnceEvidenceExtractor（:611）、_ContractRepairEvidenceExtractor（:684）、_OutputLimitEvidenceExtractor（:816）——覆盖重试、契约修复、输出截断等故障注入路径。
- **FR 回归基线**：`tests/attribution/unit/fr_traces/` 四套真实 trace（gpu_error_1st / gpu_error_2nd / lock_gil_1st / lock_gil_2nd，每套 _dump_N 目录序列）+ `reference_outputs/` 四份钉死输出的参考文件——FR 归因的 golden test。工具 fr_attribution_test_utils.py 与 REFERENCE_VALIDATION_SUMMARY.md 记录验证结论。
- **fault_tolerance 单测 35 件**（如 test_rank_monitor.py）、checkpointing/straggler 各自 unit 目录；功能测试 func/ 需多 GPU/SLURM 不进 CI。
- CPU-only 快捷键：`pytest tests/straggler/unit/ -k "test_all_gather_object_calls_num or test_fail_if_not_initialized"`（CLAUDE.md "Running Tests" 节）。
- 服务侧测试在 services/tests/，示例（megatron_gpt_worker.py、train_ddp_heartbeats_api.py、basic_ft_example.py、deployment/watch 看门狗与 deployment/slurm 部署链）本身也是可执行的文档。

## 8. 新人上手路径

按依赖序而非目录序读，五天路径：

1. **Day 1 定位**：README.md → CLAUDE.md → docs/source/fault_tolerance/usage_guide.rst；跑 examples/fault_tolerance/basic_ft_example.py 感受 section API。
2. **Day 2 FT 主线**：launcher.py:351（LocalElasticAgent）→ rank_monitor_state_machine.py:25（状态机枚举，最小完整语义单元）→ rank_monitor_server.py:125 → ft_rendezvous_barrier.py。只追"心跳→超时→决策→重启"一条线。
3. **Day 3 归因主线**：docs/design/attribution/restart_agent/DESIGN.md → L0A.md → 逐层 L1.md/L2.md/L3.md/L4.md；对照代码 assembly.py:835（build_l0_bundle）与 decision.py:39。设计文档是按层写的，与代码目录一一对应。
4. **Day 4 检查点+掉队者**：async_ckpt/core.py（AsyncCaller 三形态）→ filesystem_async.py:180；straggler.py:86（Detector）→ cupti_src/cupti_module_py.cpp:33。
5. **Day 5 服务与生态**：attrsvc app.py:131 → restart_agent_backend.py → mcp_integration/mcp_server.py:44；跑一个 fr_traces 回归测试看 golden 基线怎么工作。

练习：(a) 在 test_restart_agent.py 里找到 _ContractRepairEvidenceExtractor 的用例，解释"契约修复"救的是什么故障；(b) 从 launcher.py:774 注释出发，画出 attribution STOP 在多节点上的锁存时序；(c) 用 sub-dat 思路把 fr_traces/gpu_error_1st 缩小成最小复现并跑通 reference 比对。

> 勘误与口径警示：引用"slack.py""pipeline.py""statistics.py"等重名/小文件时必须带包路径；详见同目录上级 README.md 勘误清单（8 条）。
