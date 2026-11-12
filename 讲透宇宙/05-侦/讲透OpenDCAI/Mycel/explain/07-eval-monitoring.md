# 07 · eval 评测与 monitor 监控中间件

## 角色定位

eval/ 与 monitor 是 Mycel 的"仪表盘双引擎"：eval 负责**让 agent 跑可复现的场景并算账**（token/成本/时延），monitor 负责**在运行时旁路记账**（每次模型调用的输入输出、上下文水位、状态机迁移）。二者一静一动：eval 是拉取式批处理（对真实后端发消息、收轨迹、算指标），monitor 是推送式中间件（挂在 agent runtime 的 `awrap_model_call` 钩子上）。monitor 后端域（backend/monitor）再把两者缝合产品化，向前端 32 个 ts/tsx 文件的 monitor SPA 暴露 22 个只读为主的 API。

## 内部结构

**eval 层**（8 文件 1338 行）三段式：
- `harness/scenario.py:26-35` — YAML 场景定义：id/name/category/timeout_seconds（默认 120）/sandbox（默认 "local"）/messages（支持 delay_seconds 模拟用户节奏）。
- `harness/runner.py:33-92` — `EvalRunner.run_scenario` 完整生命周期：create_thread → 逐消息 `run_message(enable_trajectory=True)`（asyncio.wait_for 超时兜底）→ 终态为 error/cancelled 立即抛 RuntimeError（runner.py:49-52）→ get_runtime 拿快照 → `_build_trajectory` 合并 captures → collector 算指标 → store 落盘。finally 里 delete_thread 清理失败时用 `primary_error.add_note`（runner.py:88-92，Python 3.11+ 异常注记，不吞主错误）。`run_all` 用 Semaphore(max_concurrent=3) 控并发（runner.py:100）。
- `collector.py:28-141` — 两层指标：Tier1 SystemMetrics（token 五分类合计、cache_hit_rate=cache_read/(input+cache_read+cache_write)，collector.py:41-42）；Tier2 ObjectiveMetrics（每工具 avg/max/p95、慢操作阈值 read_file 60s 其他 30s，collector.py:92；tokens_per_second、tool_calls_per_llm_call 效率比）。

**monitor 中间件**（core/runtime/middleware/monitor/，7 文件）：
- `base.py:5-16` — `BaseMonitor` ABC：on_request/on_response 抽象，get_metrics/reset 默认空实现。
- `middleware.py:37-41` — 三件套注册顺序 TokenMonitor/ContextMonitor/StateMonitor；`update_model`（middleware.py:52-56）支持 `based_on` 别名换算重绑 CostCalculator 与 context_limit。
- `token_monitor.py:51-55` — usage_metadata 路径把 input_tokens 扣掉 cache_read+cache_write（净输入），output 扣掉 reasoning，五桶分账；response_metadata 是 OpenAI 风格兜底（token_monitor.py:59-71）。
- `context_monitor.py:39` — 无真实 usage 时按 `总字符数//2` 估 token；拿到真实 input_tokens 后覆盖（context_monitor.py:29-35）；`is_near_limit` 0.8 阈值（:54）。
- `state_monitor.py:14-43` — 8 态枚举 + VALID_TRANSITIONS 白名单状态机（INITIALIZING→READY→ACTIVE⇄IDLE，ERROR→RECOVERING→READY）。
- `cost.py` — 定价双源：OpenRouter API（urllib 同步 5s 超时，cost.py:129-133）→ 失败回退随仓发布的 `models.json`（467,562 字节、346 模型快照）。per-token 字符串价 ×1M 转 Decimal；免费模型 costs=None 但 context_length/provider 照收（cost.py:50-51）；缓存价缺省按 provider 推断（anthropic 0.1/1.25、openai 0.5/1.0，cost.py:88-104）；`_normalize_model_name` 剥日期后缀并把 `claude-sonnet-4-5-20250929` 归一为 `claude-sonnet-4.5`（cost.py:240-251）。
- `usage_patches.py:5-52` — **langchain-anthropic ≥1.0 流式 usage 回归的猴补丁**：上游假设 message_delta 带全量 usage，实际 Anthropic 把 input_tokens 放 message_start，补丁恢复 v0.2.4 行为（注释明言"上游修复后移除"）。

## 外部连接

- `EvaluationJobSpec` 是 frozen dataclass（evaluation_scheduler.py:9-15），`EvaluationJobScheduler` 是单方法 Protocol（:18-19）——纯接口无实现依赖；生产实现 `BackgroundTaskEvaluationScheduler`（background_task_scheduler.py:8-21）只包装一个 schedule_task 可调用，把执行细节全部留给 FastAPI 后台任务。
- `gateway.py` 22 个 API 函数（gateway.py:13-156）：沙箱投影/详情/清理、孤儿 runtime、operation 审计、资源浏览、eval workbench/batch/scenario/run 详情；`get_dashboard`（:56-84）聚合成 infra/workload/latest_evaluation 三段首页快照。
- backend/monitor 四层目录：application/use_cases（11 模块 1368 行）→ infrastructure（read_models 5 服务 + evaluation 4 模块 + io/persistence/providers）→ mutations（清理副作用）→ app（独立 FastAPI 入口）。
- cost.py 的 `_context_limits` 与 `_model_providers` 是模块级可变全局，被 context_limit 自动探测复用。

## 数据流

场景批评测主链：前端 create_evaluation_batch（gateway.py:95-109）→ use_cases 校验 scenario_ids（`select_monitor_eval_scenarios` 对缺失 id 抛 KeyError，evaluation_execution_service.py:20-25，`model_copy(update={"sandbox": ...})` 覆写沙箱）→ EvaluationBatchService 建 batch + 逐 scenario 建 batch_run（batch_service.py:22-59，batch_id 格式 `eval-batch-{uuid4().hex[:12]}`）→ scheduler.submit → 后台 `run_monitor_evaluation_batch` 起 EvalClient 跑批 → 状态回写 pending→running→completed/failed，`refresh_batch_summary` 把 failed+cancelled 合计为 failed_runs（batch_service.py:96）→ TrajectoryStore 落 Supabase/SQLite。模型调用侧：每次 LLM 请求经 MonitorMiddleware.awrap_model_call 先 on_request 后 on_response 分发（middleware.py:71-94），response.prepared_request 非空时短路跳过记账（:86-87），异常时 mark_error 进状态机。

## 设计决策（含批判）

- **frozen spec + Protocol scheduler**：backend 域不 import 具体执行器，测试可塞任意假 scheduler（tests/Unit/monitor/test_monitor_evaluation_scheduler_boundary.py 钉的就是这条边界）。干净，但 submit 无返回值无确认，批丢失只能靠轮询 batch 状态发现。
- **346 模型快照随仓发布**：离线可算价，代价是快照陈旧（新模型无价则 `_resolve_costs` 前缀匹配兜底或干脆不计费）。Decimal 全程避免浮点累加误差，工程上讲究。
- **is_error 启发式脆弱**：runner.py:147 用 `"error" in content.lower()` 判工具失败——工具输出正文含 "error" 一词即误报，成功率指标会系统性偏低。
- **批内串行**：EvaluationBatchExecutor 逐 scenario 顺序跑（batch_executor.py:15-23），EvalRunner.run_all 的并发信号量在批评测路径实际未被利用——批内一个慢场景拖全批。
- **默认场景目录不存在**：runner.py:224 回退 `eval/scenarios/`，该目录全仓没有；CLI 裸跑必打 "No scenarios found"。

## 新人提示

1. 读 monitor 从 `middleware.py` 入手 30 行看懂分发模型，再看三个子 monitor，最后才碰 cost.py 的定价归一化。
2. 改 eval 指标先改 collector，它只依赖 RunTrajectory 纯数据模型，可离线单测。
3. models.json 是 OpenRouter /models 原始响应的整包快照，不要手工编辑；上游字段变更时重新拉取覆盖。
4. usage_patches 的补丁有幂等护栏 `_anthropic_patched`，但升级 langchain-anthropic 后务必回归流式 token 统计——补丁可能悄悄失效或双重注入。
