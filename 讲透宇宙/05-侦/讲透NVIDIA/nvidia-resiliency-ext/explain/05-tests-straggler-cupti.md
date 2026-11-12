# 05 · 测试体系、straggler CUPTI 扩展与 trace_analyzer

## 角色定位

本篇覆盖三块"质量与观测"基础设施：(1) **归因测试基座**——11091 行的 test_restart_agent.py 与 fr_traces 金样回归；(2) **straggler 掉队者检测**——Python API + C++ CUPTI 扩展两层；(3) **trace_analyzer**——PyTorch/Flight Recorder 轨迹分析线。三者共同保证"归因结论可信、性能异常可见"。

## 内部结构

**测试侧**（tests/attribution/unit/，126 件）：

- `test_restart_agent.py`：11091 行、8 个顶层测试类、343 个 def（含方法）。:154 是测试版 RestartAgent 子类；替身家族控制 LLM 故障路径——_FakeEvidenceExtractor（:541）、_BlockingEvidenceExtractor（:592）、_RetryOnceEvidenceExtractor（:611）、_ContractRepairEvidenceExtractor（:684）、_RetryThenContractRepairExtractor（:738）、_OutputLimitEvidenceExtractor（:816）、_SingleResponseEvidenceExtractor（:857）。
- **fr_traces 金样**：tests/attribution/unit/fr_traces/ 四套真实 trace（gpu_error_1st / gpu_error_2nd / lock_gil_1st / lock_gil_2nd，每套 _dump_0..N 目录）+ reference_outputs/ 四份参考输出 + fr_attribution_test_utils.py + REFERENCE_VALIDATION_SUMMARY.md——FR 归因的 golden 回归，输出逐字比对。
- MCP/orchestration/restart_agent 各有独立 test_fr*.py / test_mcp_server_cache.py；fault_tolerance 单测 35 件（test_rank_monitor.py 等）；CPU-only 子集用 `-k` 过滤（CLAUDE.md）。

**straggler 侧**（src/nvidia_resiliency_ext/attribution/straggler/）：

- 主 API straggler.py（407 行）：`CallableId`（:35）、`CustomSection`（:66）、`Detector`（:86 检测器主类）；statistic 枚举在 statistics.py:19（该文件仅 35 行）。
- 节奏与上报：interval_tracker.py:24（ReportIntervalTracker）、reporting.py（StragglerId :32、Report :42、ReportGenerator :154，统计评分+跨 rank all-gather）；name_mapper.py 归一 kernel/算子名；dist_utils.py 分布式工具。
- **C++ 扩展 cupti_src/**：cupti_module_py.cpp:33（`PYBIND11_MODULE(nvrx_cupti_module, m)`）；CuptiProfiler.cpp:96（initializeProfiling）/:106（shutdown）/:116（start）/:126（stop）/:148（reset）/:158（bufferRequested 回调）；BufferPool.h:24（class BufferPool）内存池；CircularBuffer.h:23（class CircularBuffer）环形缓冲。Python 侧绑定 cupti.py 仅 95 行——薄壳。

**trace_analyzer 侧**：trace_analyzer.py:17（class TraceAnalyzer）入口；capture.py:16（capture_logs）/:30（capture_stdout）与 trace_collector.py:22（TraceCollector 基类）/:39（TorchFRTraceCollector）采集；fr_attribution.py 做 FR 首次故障归因（`CollectiveAnalyzer` fr_attribution.py:97 继承 NVRxAttribution，CLI 入口 main fr_attribution.py:1036）；fr_support.py（dump 路径发现/checkpoints 推断/MCP 响应转换/markdown 附录）。

## 外部连接

straggler 的 CUPTI 数据经 CuptiProfiler 订阅 kernel/内存活动，喂给 Detector（straggler.py:86）评分；ReportGenerator（reporting.py:154）的跨 rank 结果可接 dist_utils 广播；trace_analyzer 的 FR 线消费 timeout_dump（04 篇）与 Flight Recorder dump，结论经 fr_support.py 进 MCP 工具面（03 篇 mcp_server.py:44）；fr_traces 金样由 test_fr.py 家族消费，也是 skills/nvrx-attr/fr-analysis/scripts/fr_attribution.py 的实跑数据源。

## 数据流

训练进程内：用户 wrap 训练 step → Detector（straggler.py:86）注册 CustomSection（:66）→ CUPTI 回调（CuptiProfiler.cpp:158 bufferRequested）经 CircularBuffer/BufferPool 批量吐记录 → cupti.py 桥回 Python → ReportIntervalTracker（interval_tracker.py:24）到点触发 → ReportGenerator（reporting.py:154）统计评分 → all-gather 全 rank 报表识别慢者。FR 线：故障 dump 落盘 → trace_collector/capture 收集 → TraceAnalyzer（trace_analyzer.py:17）分析 → fr_attribution.py 归因 → fr_traces 同构数据在 CI 里逐字回归（reference_outputs 比对）。

## 设计决策

- **替身即契约测试**：七个 EvidenceExtractor 替身（test_restart_agent.py:541-857）把 LLM 的失败模式（阻塞/限流/截断/违约）变成确定性用例——LLM 系统的回归测试靠"模拟故障注入"而非真实调用。
- **金样钉死输出**：fr_traces 四套覆盖 GPU 错误与 GIL 死锁 × 首次/二次故障四个象限，reference_outputs 逐字比对防归因漂移。
- **重活在 C++、语义在 Python**：CUPTI 热路径（缓冲/回调）在 cupti_src，95 行的 cupti.py 只做绑定——GIL 不进数据面。
- **构建可降级**：无 CUDA 环境用 `STRAGGLER_DET_SKIP_CUPTI_EXT_BUILD=1`（build.py:45 _skip_ext_build）跳过扩展，CPU 测试仍可跑。

## 新人提示

跑 `pytest tests/straggler/unit/ -k "test_all_gather_object_calls_num or test_fail_if_not_initialized"` 先建立信心；读 CUPTI 线从 cupti_module_py.cpp:33 的模块定义看导出面；改 reporting.py 前先跑 fr_traces 回归确认没动金样；新增替身请沿用 :541 起的命名惯例（行为名入类名）；REFERENCE_VALIDATION_SUMMARY.md 记录了金样的生成与验证方法，动 reference_outputs 前必读。
