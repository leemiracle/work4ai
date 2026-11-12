# 01 · restart_agent 运行时核心：归因代理的骨架与门面

## 角色定位

restart_agent 是 NVRx 的"故障法官"：训练作业挂掉后，它消费多源日志，产出结构化的归因结论（哪类故障、根因在哪、要不要重启）。它不是单脚本，而是一个带完整运行时、数据模型、身份系统与测试注入点的子框架，共 57 个 .py（`src/nvidia_resiliency_ext/attribution/restart_agent/`），上游对接 FT launcher 的归因钩子（launcher.py:81 import attribution_manager），下游经 L0-L4 五层流水线输出 Decision。

## 内部结构

包内布局（行数 wc 实证）：

- **入口与门面**：`cli.py:39`（main，argparse 入口）；`pipeline.py:38`（class RestartAgent）——注意 pipeline.py 全文仅 213 行，是薄门面而非编排主体。
- **真正的分发**：`single_run.py`（466 行，单次归因）与 `multi_route.py`（837 行，多路由/多作业场景，规模是 pipeline.py 的四倍）；`agent_runtime.py`（571 行）承载执行环境。
- **决策上下文**：`decision_pipeline.py`（826 行）+ `causality.py`（138 行，`build_result_cascades` causality.py:15 构造结果级联）构造因果链；`current_failure_facts.py`（160 行）提取本次故障事实；`preparation.py`（227 行）做前置准备。
- **跨次记忆**：`attempt_records.py`（378 行）记录历次尝试；`identity.py`（200 行）生成 fingerprint（`fingerprint_for` identity.py:90）、抽取 rank（`extract_rank` identity.py:155）——跨次尝试的稳定身份锚全靠它。
- **数据模型**：`models.py`（2031 行、69 个类）定义 Decision、失败域、L1 状态与归一化入口 `normalize_restart_agent_request`（models.py:1396）。
- **配置**：`config.py`（563 行）；**可测试性注入**在 `runtime.py`（Clock/Sleeper/ExecutorFactory 抽象，让测试能操纵时间与执行器）。
- **分层分析**在子包 l0/、l1/、l2/、l3/、l4/（见 02、03 篇）；工件与轨迹在 infrastructure/ 与 observability/。

## 外部连接

- 上游：FT launcher 经 `attribution_manager.py` 在重启决策点调用（launcher.py:694-784 的 attribution STOP 优先级）；attrsvc 经 `services/attrsvc/restart_agent_backend.py`（1556 行）把 HTTP 请求翻译成本包运行。
- 下游：结论流向 orchestration 的 http_api.py:70（post_log）与 postprocessing/slack.py:88（send_slack_notification）；MCP 面在 mcp_integration/mcp_server.py:44（NVRxMCPServer）。
- 姊妹栈：legacy_logsage/ 是它的前身（nvrx_logsage.py、combined_log_fr.py），故意不进 wheel。

## 数据流

一次典型单跑：cli.py:39 解析参数 → RestartAgent（pipeline.py:38）装配 → preparation.py 备料 → infrastructure/log_source.py 的 ChunkedLogReader 分块读日志 → identity.py 归一身份 → decision_pipeline.py 组决策上下文 → L0 组装（assembly.py:835 build_l0_bundle）→ L1-L4 分析 → execution.py 定义的 L0Artifacts/AnalysisRun（execution.py 数据类）落盘 observability/trace_builder.py 导出轨迹 → 结论经 multi_route.py 或 single_run.py 返回调用方。attempt_records.py 在每个 cycle 结束写入历史，供下次 L3 history.py:51（evaluate_history）消费。

## 设计决策

- **门面与编排分离**：pipeline.py 故意薄（213 行），重逻辑下沉 single_run/multi_route——避免"上帝文件"，也让单跑与多路由复用同一套 L0-L4。
- **确定性优先**：L0 完全不用 LLM（见 02 篇），LLM 只在 L1 出现且被 L2 grounding 锁死——把不可靠组件圈进最小边界。
- **身份系统先行**：identity.py 的 fingerprint 归一化保证了"同一个故障跨多次重启可关联"，这是 attempt_records 与 L3 历史评估成立的前提。
- **runtime.py 注入点**：Clock/Sleeper 抽象让 11091 行测试（test_restart_agent.py）可以不睡觉地测重试。

## 新人提示

先读 `docs/design/attribution/restart_agent/RUNTIME.md` 与 DESIGN.md 再看代码；从 models.py 的 Decision 类反向理解各字段谁生产谁消费；用 `grep -n "class RestartAgent" tests/attribution/unit/test_restart_agent.py`（:154）看测试如何继承门面类替换组件；引用 pipeline.py 时别按文件名猜测它是"总管线"——真正编排者在 single_run.py/multi_route.py。
