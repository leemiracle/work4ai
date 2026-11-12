# 02 · graph.py 流程编排：88 行接线、27 分析器与 57 字段状态机

## 一、角色定位

`src/skillspector/graph.py` 只有 88 行，却是全仓心脏。它把 LangGraph 的 StateGraph 装配成一条固定拓扑：`resolve_input → build_context → 并行分析器扇出 → meta_analyzer（扇入）→ finalize_inspection_ledger → report → END`。所有检测能力都不写在这里——27 个分析器经 `nodes/analyzers/__init__.py` 的动态发现机制汇入。配合 `state.py` 的 57+ 字段共享状态与三个自定义 reducer，这份文件定义了"分析器插件"的接入契约。仓根 `langgraph.json` 把它暴露给 LangGraph Studio 做可视化调试。

## 二、内部结构

**create_graph（graph.py:44-85）** 分四步：

1. **五个固定节点**（graph.py:48-52）：resolve_input（输入物化）、build_context（上下文构建）、meta_analyzer（LLM 汇聚过滤）、finalize_inspection_ledger（完备性账本定稿）、report（报告产出）。
2. **分析器接线循环**（graph.py:59-70）：遍历 `ANALYZER_NODE_IDS`，先做可用性门控——模块若定义了 `is_available()` 且返回 False 则跳过并告警（graph.py:62-65）；否则 `workflow.add_node(analyzer_id, guard_analyzer_node(analyzer_id, ANALYZER_NODES[analyzer_id]))`，每个分析器都被 `guard_analyzer_node`（inspection_ledger.py:1076-1123）包裹——任何未捕获异常被转成每个 component 一条 `ANALYZER_RUNTIME_ERROR` 的 FAILED 账本事件加终态 failed 状态事件，绝不让单个分析器崩掉整个图。
3. **零分析器防线**（graph.py:72-73）：没有任何分析器接入时打警告"Scan will produce no findings"。
4. **边装配**（graph.py:75-84）：START→resolve_input→build_context；每个分析器 build_context→analyzer→meta_analyzer（扇出/扇入全连通）；meta_analyzer→finalize→report→END。没有条件边。

模块级 `graph = create_graph()`（graph.py:88）意味着 import 即编译，CLI 与 MCP server 共享同一实例。

**注册表（nodes/analyzers/__init__.py）**：`_discover_analyzers`（__init__.py:34-64）用 `pkgutil.iter_modules(__path__)` 按文件系统顺序遍历包内模块，import 成功后取两个属性：`ANALYZER_ID`（字符串）与 `node`（可调用）——两者齐备才注册进三个全局表 ANALYZER_NODE_IDS/ANALYZER_NODES/ANALYZER_MODULES（__init__.py:55-61）；import 失败进 `ANALYZER_LOAD_ERRORS`（__init__.py:44-53）。实测 27 个模块定义 `ANALYZER_ID`：15 个 `static_patterns_*` + static_yara（静态 16）+ behavioral_ast/behavioral_taint_tracking/artifact_integrity/bundled_execution_surface（行为 4）+ mcp 三分析器（3）+ semantic 三分析器（3）+ structured_skill_roles（1）。注意 osv_client.py 虽在包内且定义了 `is_available()`（osv_client.py:826），但无 ANALYZER_ID，只是被 static_yara 复用的工具模块，不注册为节点。

**状态机（state.py）**：`SkillspectorState(TypedDict, total=False)`（state.py:233）全部字段可选。三类带 reducer 的字段决定了并行扇出的合并语义（state.py:273-297）：
- `findings: Annotated[list[Finding], merge_findings_by_id]`——按 finding_id 合并、**同 ID 后写覆盖先写**（state.py:175-186），这让 meta_analyzer 的 enriched 版本能原位替换静态原始版；
- `inspection_ledger: Annotated[..., merge_inspection_ledger]`（state.py:189-230）——拼接且封顶 `MAX_INSPECTION_LEDGER_EVENTS`，超限时保留前 N-1 条并追加一条 `ledger_output` PARTIAL 哨兵事件（记录真实 observed_records 总数），账本永远不会无限膨胀也永远不说谎；
- `analyzer_status_events / llm_call_log / inference_usage / structured_summaries` 用 `operator.add` 纯拼接。

**资源预算**：模块级常量 `MAX_WORKFLOW_SECONDS`（默认 600s，可由 `SKILLSPECTOR_MAX_WORKFLOW_SECONDS` 覆盖，state.py:46-73）、`MAX_WORKFLOW_BYTES = 64MB`、`MAX_WORKFLOW_ARTIFACTS = 10000`、`MAX_WORKFLOW_LIMITATION_RECORDS = 256`（state.py:75-77）。`workflow_resource_budget` 作为不透明对象放进 state（state.py:355-358），`_has_resource_budget_contract`（state.py:167-172）用鸭子类型识别"有 remaining_seconds/remaining_bytes/remaining_artifacts 三方法"的任意预算对象——CLI 的 `_TransitiveTraversalState` 就这样被塞进 graph 而不需要 graph 认识它的类型。四个 `transitive_remaining_*` 访问器（state.py:385-437）供各分析器读取共享余量。

**节点响应契约**：`AnalyzerNodeResponse`（state.py:447）规定分析器返回 `findings`（必填）+ inspection_ledger/analyzer_status_events/structured_summaries/llm_call_log/inference_usage（NotRequired）；`MetaAnalyzerResponse`（state.py:460）另加 `effective_finding_ids`。

## 三、外部连接

- langgraph 的 `StateGraph/START/END`（graph.py:24）——唯一框架依赖；
- `inspection_ledger.guard_analyzer_node` 提供崩溃防护；`llm_utils.is_llm_available` 作为兼容再导出（graph.py:27、39-41），图构造刻意与凭据解耦：没有 API key 时分析器以显式状态（disabled/unavailable）出现在结果里，而不是从图里消失；
- build_context 写入的 components/file_cache/manifest/model_config 等是全部分析器的输入面；meta_analyzer 消费 findings 全集，产出 effective_finding_ids 给 report 做选择；
- langgraph.json 指向本模块供 Studio 渲染。

## 四、数据流

单次扫描：CLI 构造初始 state dict → graph.invoke → resolve_input 物化输入（URL/git/zip/单文件→本地目录，记 temp_dir_for_cleanup）→ build_context 解析制品清单、文件缓存、AST 缓存键、manifest、模型槽位 → 27 个分析器并行执行，各自返回增量（findings/账本/状态事件），reducer 自动合并 → meta_analyzer 对 canonical findings 做 LLM 过滤/增补（fail-closed：LLM 失败时全量保留）→ finalize_inspection_ledger 定稿完备性账本 → report 应用基线抑制、计算 risk_score、渲染 report_body/sarif_report。并行扇出意味着分析器执行顺序无关，只有 meta 之后的串行链有序。

## 五、设计决策

1. **文件系统序发现而非策划清单**（graph.py:56-58 注释明说）：加分析器=丢一个带 ANALYZER_ID+node 的模块进包，零接线改动；代价是文档表格顺序≠注册顺序（并行执行所以无害）。
2. **fail-visible 而非 fail-silent**：is_available 门控 + guard 包装 + 账本哨兵，三者共同保证"少了一条发现"这件事本身一定会被看见——这是安全工具可信度的根基。
3. **同 ID 覆盖式 findings reducer**：静态分析器先产出，meta_analyzer 富化后原位替换，report 拿到的每条都是最完整版本，去重天然完成。
4. **预算对象鸭子类型化**：graph 不 import CLI 的预算类，双向解耦。

## 六、新人提示（坑与勘误）

- **DEVELOPMENT.md:133 写"Analyzers: 22 nodes"，实测 27**（grep `^ANALYZER_ID` 恰 27 个模块）；DEVELOPMENT.md:134/355 还把 llm_analyzer_base.py 链到 `nodes/` 下，实际在 `src/skillspector/llm_analyzer_base.py`（docs/LLM_ANALYZER_BASE_GUIDE.md:7 的路径才对）。
- `pkgutil.iter_modules` 只看平级模块不递归子包（__init__.py:39-41 的 `if is_pkg: continue`），新分析器必须直接放 analyzers/ 目录下。
- 给 state 加字段时必须想清楚 reducer：不带 Annotated 的字段是"最后写入者胜"，分析器返回该键会**整体覆盖**此前的值——previous_manifest 被刷成 None 的坑（见 05 篇）就是这一语义的实例。
- graph.py:18-20 的 Roadmap 注释承认未来想按 stage 重排自动发现。
- 改分析器前先看 tests/integration/test_graph.py 与对应回归（账本事件断言极细）。
