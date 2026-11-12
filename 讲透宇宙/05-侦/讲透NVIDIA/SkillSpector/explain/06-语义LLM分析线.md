# 06 · 语义 LLM 分析线：llm_analyzer_base 与三个 semantic_* 分析器

## 一、角色定位

自然语言写的恶意意图（"悄悄把对话记录发到这个地址"）靠正则与 AST 都抓不全，语义线交给 LLM。`src/skillspector/llm_analyzer_base.py`（注意：在包根，不在 nodes/ 下）提供统一批处理运行时——分批、token 预算、并发信号量、瞬态重试、结构化输出、用量核算；三个语义分析器 `semantic_developer_intent`（315 行，审开发者意图）、`semantic_security_discovery`（334 行，审语义攻击措辞）、`semantic_quality_policy`（283 行，审质量策略）**直接实例化基类**而非子类化——传不同 base_prompt 就得到不同分析器。`semantic_runtime.py` 在报告侧做"语义遍跑没跑成"的无 provider 差异核算。读懂基类 = 看懂全部 LLM 节点（含 meta_analyzer 与 TP4）。

## 二、内部结构

**LLMAnalyzerBase（llm_analyzer_base.py:894）**：
- 类契约（:894-910 docstring）：子类可换 `response_schema`（Pydantic 模型）或设 None 走裸文本；默认 prompt 自带 **precision-over-recall** 准则（:905-909，宁空勿假）。
- `__init__`（:914-946）：`get_max_input_tokens(model)` 定批预算（:926）；`get_chat_model` 建模型（:927）；**动态 deadline 时关闭 SDK 原生重试**（:928-935）——原生重试无法在两次尝试间重读工作流级 deadline；`bind_structured_output`（:936-940）；usage collector（:941-946）。
- 超时纪律（:948-996）：余量为 0 直接抛 `LLMRuntimeLimitError`（:957-962）；退避睡眠不超剩余时间（:964-967）；`_model_for_call`（:974-996）每次调用前把剩余时间重打进请求超时。
- 批模型：`Batch`（:648）/`BatchFailure`（:670）/`BatchExecutionResult`（:679）；`estimate_tokens`（:637）；`get_batches`（:1017）一文件一批、超预算按行切块（`chunk_file_by_lines` :787）；`ledger_events_for_batches`（:725）把批结果映射账本（含未覆盖区间 :693）；`number_lines`（:839）给 prompt 加 L 行号。
- 执行：`run_batches_detailed`（:1292-1337）串行版，结构化校验失败→`LLM_STRUCTURED_RESPONSE_INVALID` 批级失败；`arun_batches`（:1339-1387）并发版：信号量限并发（`SKILLSPECTOR_MAX_LLM_CONCURRENCY`，`resolve_max_concurrency` :537）；瞬态故障三连重试——传输/服务错退避 500ms/1s/2s、限流 5s/15s/30s，Retry-After 更长从之；单批最多 7 次外层调用（:1346-1381）。`arun_batches_detailed`（:1389）里 `_GlobalLLMLimiter`（:453）**按进程共享**——预算语义是"全进程并行请求数"而非"每分析器"（:1397-1400）。`collect_findings`（:1465）汇总成功批。重试判定基础设施在 :127-390（可重试状态码 408/409/425/429、`_provider_retry_after_seconds` :326）。

**三个语义分析器**（结构同构，以 semantic_developer_intent 为准）：
- `ANALYZER_ID` + `requires_api_key = True`（semantic_developer_intent.py:44-45，三者同）；
- `ANALYZER_PROMPT` 内嵌完整规则书：SDI 线四规则（:64-161）——SDI-1 描述-行为失配、SDI-2 场景不当能力、SDI-3 权限范围蔓延、SDI-4 注释与代码矛盾，每规则带正反例与"勿报"边界；`_format_manifest`（:164）把 manifest 压成四行注入 prompt（:249）。SSD 线四规则（semantic_security_discovery.py:73-90，语义提示注入/新攻击措辞/自然语言外传/叙事性诱导），prompt 定位"抓正则抓不到的残余缺口"（:100-103）。SQP 线三规则（semantic_quality_policy.py:80-147，模糊触发词/缺用户警示/策略违规，SQP-1 仅限 markdown/文本）。
- `node`（developer_intent :186-315）：`use_llm=False` → disabled/DISABLED_BY_CONFIGURATION（:188-199）；读 **llm_file_cache**（脱敏投影，:201-204）；模型槽位四级回退 `model_config[ANALYZER_ID] → default → MODEL_CONFIG → _SKILLSPECTOR_DEFAULT_MODEL`（:219-225，SSD/SQP 同构 :182/:194）；共享时钟耗尽 → 全部目标记 RUNTIME_LIMIT 批失败（:230-244）；**直接实例化** `LLMAnalyzerBase(base_prompt=..., model=..., node=ANALYZER_ID, timeout=动态余量)`（:250-255）→ get_batches → `run_async(arun_batches)`（:256-257）→ collect_findings → 账本/状态/遥测四件套返回；异常分支区分 LLMRuntimeLimitError（部分覆盖账本，:276-289）与 provider 故障（unavailable，:295-308）。**llm_call_log 的 ok 判据是"全部批成功"而非"部分成功"**（:266-272 注释：一批 429 一批成功仍是丢覆盖）。

**semantic_runtime.py（核算侧）**：`semantic_runtime_accounting`（:107-197）是"语义遍完成"判定器——每个必需语义分析器须按 (source_scope, analyzer_id) 精确报一条 completed（恰一次成功调用）或 not_applicable（零调用）；状态不能跨 source 借用（:186-189）；有有效发现还须有成功的 meta_analyzer 记录（:191-195）。`required_semantic_analyzer_ids`（:36）动态取必需集，`semantic_runtime_limitation`（:200）转限制文案。

## 三、外部连接

providers 层的 `get_chat_model` 与 `bind_structured_output` 是唯一模型入口（尊重 SKILLSPECTOR_PROVIDER 体系）；constants.py `_MODEL_SLOTS`（:65-74）为三个 semantic 各设槽位；`LLMMetaAnalyzer`（nodes/meta_analyzer.py:300）与 `_TP4Analyzer`（mcp_tool_poisoning.py:900）是基类另外两个消费者；cli.py:65-69 在报告与退出码层消费核算结论。

## 四、数据流

llm_file_cache → get_batches（按文件/行块切批，带 L 行号文本）→ arun_batches（全局信号量 + 三连退避 + 结构化输出绑定）→ LLMAnalysisResult（LLMFinding 列表，:631/:575，Pydantic 校验）→ collect_findings 转 Finding → AnalyzerNodeResponse{findings, 逐批 ledger, status_events, llm_call_log, inference_usage}。meta 阶段后 semantic_runtime_accounting 复核 llm_call_log × analyzer_status_events 的 (scope, analyzer) 二维一致性，决定报告"LLM 分析"标签能否写"已使用且完备"。

## 五、设计决策

1. **组合优于继承**：语义三分析器直接实例化基类、只换 prompt——prompt 即配置。真正子类化的是两个需定制 parse 的节点：_TP4Analyzer（返回自定义类型，mcp_tool_poisoning.py:916-924）与 LLMMetaAnalyzer（过滤/富化模式）。
2. **动态 deadline 贯穿到 SDK 层**：禁原生重试、调用前重打请求超时、退避睡眠封顶，三层都感知共享时钟，子扫描不会把全局预算烧在重试上。
3. **失败永远可见**：批失败 → BatchExecutionResult → 账本 PARTIAL → llm_call_log ok=False → semantic_runtime 判"不完备"，任何一环丢覆盖都浮到报告面。
4. **precision-over-recall 默认**：宁可不报也不误报，配合 meta_analyzer 二次过滤成双闸。

## 六、新人提示（坑与勘误）

- **路径勘误**：DEVELOPMENT.md:134/355 把 llm_analyzer_base.py 链到 `nodes/` 下，实际在 `src/skillspector/llm_analyzer_base.py`（docs/LLM_ANALYZER_BASE_GUIDE.md:7 路径正确）；"唯一继承者 _TP4Analyzer"需限定——仅在 nodes/analyzers 包内成立，全局还有 meta_analyzer.py:300 的 LLMMetaAnalyzer，共两个子类。
- 语义线读 llm_file_cache（脱敏投影），本地敏感文件不会发往外部 provider——测试注入用 file_cache 会被判"无适用文件"。
- `--no-llm` 下三个语义分析器返回 disabled 而非消失，完备性账本仍能看到它们（graph.py:39-41 注释的设计意图）。
- 并发上限**进程级**共享（_GlobalLLMLimiter :453-535）：多个语义分析器并行扇出共同挤一个 SKILLSPECTOR_MAX_LLM_CONCURRENCY 池，单独调大某分析器并发无意义。
- estimate_tokens（:637）与 provider 真实计费有偏差；inference_usage 才是账面真值（provider 上报，docs/INFERENCE_USAGE.md）。
- 改基类重试策略先跑 tests/nodes/test_llm_analyzer_base.py，改 prompt 规则书先跑 tests/nodes/test_semantic_quality_policy.py。
