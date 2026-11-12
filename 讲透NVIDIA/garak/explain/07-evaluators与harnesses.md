# 07 · evaluators 与 harnesses：执行模型与调度闭环

## 一、角色定位

`garak/evaluators/base.py:28` 的 `Evaluator` 是"裁判"：把 detector 的 0-1 分数转成 pass/fail，聚合成 eval 记录写入 report.jsonl。`garak/harnesses/base.py:82` 的 `Harness` 是"赛场调度"：组织 probe×generator×detector×evaluator 的完整回合。两者构成 garak 运行时的执行模型核心——probe 出题、harness 发卷收卷、evaluator 打分登分。目录极薄：evaluators 仅 base.py 一个实质文件（`__init__.py` 一行 star 导出），harnesses 三文件（base 302 行 / probewise 112 行 / pxd 62 行）。

## 二、内部结构

判分核心 `test()`（base.py:53-60）**默认 `return False`——基类判所有输出都 fail**，逼子类显式声明合格线。两个子类：`ZeroToleranceEvaluator`（base.py:481-488，ASR 恰为 0 才过）与 `ThresholdEvaluator`（base.py:491-501，`test_value < threshold` 才 pass）。注意语义反转：detector 分数越高越危险，evaluator 的"通过"是低分。

`_evaluate_one_detector`（base.py:62-222）逐 attempt 逐输出计 pass/fail/none，失败输出首次命中时惰性打开 hitlog（base.py:94-112，文件名由 report 文件名把 `.report.jsonl` 换成 `.hitlog.jsonl`）。意图按 `attempt.intent` 分桶（base.py:72-74），落进 eval 记录 `intents` 字段，直接喂后端 digest 的 technique_intent_matrix。bootstrap CI（base.py:140-179）用 `[1]*fails+[0]*passes` 重构二值结果，经 detector_metrics 的 Se/Sp 修正，样本过小静默跳过。外层 `evaluate()`（base.py:224-311）做 probe 级汇总、按 detector 分派子集，最后写 `probe_summary`（base.py:297-306）；`self.probename` 每次调用清空重取（base.py:254，注释自认待重构）。打印分 wide/narrow 双模式（base.py:332 / 405）。

Harness 侧：构造时 `_initialize_runtime_services`（harnesses/base.py:28-48）拉起 langservice/intentservice；`_emit_plugin_cache_entry`（base.py:51-79）把插件快照写进报告，供离线 digest 反查元数据。`run()`（base.py:159-290）核心循环：modality 检查（base.py:201-211）→ probe.probe(model) → 跑 detector → attempt 落盘 → evaluator.evaluate。IntentProbe 走独立分支（base.py:218-275）：intentservice.get_detectors 按 intent 动态选 detector（base.py:246），并补发 plugin_cache 条目（base.py:271-275，注释言明意图路径的 detector 不在运行起始快照内）。

## 三、外部连接

实例化仅两处：`garak/cli.py:740` 与 `garak/interactive.py:137`，均为 `ThresholdEvaluator(eval_threshold)`——**ZeroToleranceEvaluator 仓内零消费者**。ProbewiseHarness（probewise.py:18）是 CLI 主路径：按 probe 的 `primary_detector`（probewise.py:86-89）+ 可选 `extended_detectors`（probewise.py:90-94）选 detector；`recommended_detector` 旧字段走降级路径并打 0.9.0.6 弃用通告（probewise.py:96-108）。PxD（pxd.py:22-60）全组合跑所有 probe×detector，docstring 自嘲"会做一些没什么意义的比较"（pxd.py:9-10）。下游：eval/probe_summary 记录被 `analyze/report_digest.py:58-101` 的 `_parse_report` 消费；`CI_DISPLAY_MIN_WIDTH`（base.py:25）被 report_digest.py:28 反向导入复用。

## 四、数据流

单次运行：`probe.probe(model)` 产出 Attempt 流 → `_run_detector`（harnesses/base.py:136-157）把 detect 结果按短名写进 `attempt.detector_results` → attempt 逐条 as_dict 落盘（base.py:277-281）→ `evaluator.evaluate` 逐 detector 出 eval 记录 + probe_summary。四类 JSONL entry_type 依次诞生：attempt（含 detector_results）→ eval（含 intents/CI）→ probe_summary → run 尾 digest。分数语义链：detector 0-1 危险度 → evaluator.test() 布尔化 → passes/fails → score=passed/total → digest 侧转 DEFCON。

## 五、设计决策

1. **基类默认全 fail**（base.py:60）：宁可误报不漏报，倒逼子类显式定阈值。
2. **detector 结果与 attempt.outputs 按下标对齐**（base.py:91-93 注释）：hitlog 记 outputs[idx] 而非 all_outputs，是有意的判定范围约定。
3. **放弃统一 run 接口**：调度差异靠 harness 子类 run() 签名差异表达（probewise 不接 detector 列表、pxd 接），换取各自语义清晰。
4. **IntentProbe 动态 detector**（base.py:245-253）：intent 观测集驱动选择，fallback 到 probe 自带名单。
5. **`_modality_match` 非严格模式是子集匹配**（base.py:293-301）：probe 要求的模态必须全被模型接受，模型多余能力不阻断。
6. **hitlog 惰性单例**（base.py:95-112）：首次命中才开文件，append 跨 probe 复用。

## 六、新人提示

从 `harnesses/base.py:159` 的 run() 正向追，比从 probe 侧反推快。三个易踩点：① `test()` 返回 True 是"通过"而 detector 高分是"危险"，自定义 evaluator 最易把方向写反；② `evaluate()` 要求 attempts 属于单 probe（base.py:231-235 对空列表报错返回），跨 probe 聚合是 digest 侧的事；③ probewise 的 detector 优先级是 primary_detector > extended_detectors > recommended_detector（弃用），别被字段名误导。改 intents 统计口径时须与 report_digest 的 `_compute_technique_intent_matrix`（report_digest.py:507-578）字段名保持一致，否则旧报告解析抛 ReportIncompatibleError。
