# 讲透 nvidia-resiliency-ext（NVIDIA Resiliency Extension / NVRx）

NVIDIA 官方 PyTorch 训练弹性容错库：进程内重启（Fault Tolerance）+ 异步/本地双检查点（Checkpointing）+ CUPTI 掉队者检测（Straggler）+ LLM 故障归因代理（restart_agent）。仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-resiliency-ext`。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | 完成（34 页 TRUE_100） | `deepwiki/`（INDEX.md + _coverage-check.md + wiki_full.md） |
| understand 图谱 | 完成：2875 节点 / 3677 边 / 14 层 / 16 步 tour，validate 0 issues | 仓内 `.understand-anything/knowledge-graph.json` |
| fingerprints 基线 | 608 文件 @ `af2a108b`（2026-10-27，PR #464 timeout-dump-tools） | 仓内 `.understand-anything/fingerprints.json` |
| ONBOARDING | 完成（8 节，行号锚 60+，全部 grep 实证） | `onboarding/ONBOARDING.md` |
| explain 系列 | 完成 5 篇（六节结构，行号锚 12+/篇） | `explain/01..05` |
| 本 README | 状态表 + 勘误 8 条 | 本文 |

explain 索引：01-restart-agent-core（门面与运行时）/ 02-l0-assembly（5595 行确定性证据组装）/ 03-l1-l4-attribution-mcp（LLM 分层分析与工具生态）/ 04-ckpt-ft-launcher（检查点双体系与 4008 行启动器）/ 05-tests-straggler-cupti（11091 行测试基座与 CUPTI 扩展）。

## 阅读顺序建议

新人：README（仓根）→ CLAUDE.md → onboarding/ONBOARDING.md → docs/source/fault_tolerance/usage_guide.rst；深潜：docs/design/attribution/restart_agent/ 21 篇设计文档对照 explain 01-03；运维线：explain 04 + services/attrsvc/ATTRSVC_SPEC.md。

## 勘误清单（源码实证，引用前必读）

1. **skills 包路径不在 attribution 下**：nvrx-attr skill 实际在 `src/nvidia_resiliency_ext/skills/nvrx-attr/`（含 fr-analysis/log-analysis/fault-injection-loop 三个子技能 SKILL.md），与 attribution/ 平级；`src/nvidia_resiliency_ext/attribution/skills/` 目录不存在（find 实证）。按"归因技能在归因包里"的直觉找会扑空。
2. **"pipeline.py 编排全流程"是误导**：pipeline.py 仅 213 行、只有 RestartAgent 门面类（pipeline.py:38）；真实编排主体是 single_run.py（466 行）与 multi_route.py（837 行），decision_pipeline.py（826 行）也远大于它。图谱 L02 描述把 pipeline.py 放首位属于"入口≠重心"的错位。
3. **"test_restart_agent.py 259 函数"口径过期**：grep 实测 343 个 def（含类方法）、8 个顶层测试类；11091 行属实。259 应为旧一代 tree-sitter 提取口径，引用时建议改用"8 类 343 def"。
4. **两个 slack.py 职责不同**：`attribution/postprocessing/slack.py`（174 行，send_slack_notification :88 / should_notify_slack :148，归因结果推送判定）与 `src/nvidia_resiliency_ext/services/attrsvc/slack.py`（875 行，attrsvc 服务侧通知全家桶）。裸写 "slack.py" 必须带包前缀。
5. **L1 的大头是 provider 适配不是工具定义**：openai_compatible.py 2185 行 > tools.py 1012 行（ToolRoundExecutor openai_compatible.py:374 是工具循环核心）。DeepWiki 5.x 章按"detector/scoring"叙事容易让人低估 provider 层体量。
6. **CUPTI 绑定主体在 C++**：straggler/cupti.py 仅 95 行；pybind11 模块在 cupti_src/cupti_module_py.cpp:33（nvrx_cupti_module），缓冲三件（CuptiProfiler.cpp/BufferPool/CircularBuffer.h）才是数据面。"cupti.py 是 CUPTI 扩展"的说法只对了一成。
7. **straggler 主检测类在 straggler.py 不在 statistics.py**：Detector（straggler.py:86）与 CallableId/CustomSection 都在 407 行的 straggler.py；statistics.py 仅 35 行（Statistic 枚举 :19）。早期 grep 混排输出曾把两者行号互串，引用前需双查。
8. **LocalElasticAgent 是"同名不同源"**：本仓 LocalElasticAgent（launcher.py:351）继承 `SimpleElasticAgent`（launcher.py:50-52，torch.distributed.elastic.agent.server.api），不是 torchrun 用的 LocalElasticAgent；按 PyTorch 文档查这个类名会查到另一个实现。

## 口径备注

- 行数一律 `wc -l` 实证；类/函数计数 grep 顶级定义（含缩进方法），与 tree-sitter 提取存在口径差。
- docs/design/attribution/restart_agent/ "21 篇设计文档"为精确数（ls 实证：DESIGN/REQUIREMENTS/L0A/L0B/L1/l1_category_selection/L2/L3/L4/TOOLS/SCHEMA/TAXONOMY/PATTERN_REGISTRY/PROGRESSIVE/RUNTIME/DECISIONS/EVALUATION/CONFIGURATION/STATUS/ATTRSVC_INTEGRATION/README）。
- docs/source/ 的 md+rst 共 85 件（含 fault_tolerance 23 篇），"21 篇"仅指 design 设计文档子集，勿混用。
