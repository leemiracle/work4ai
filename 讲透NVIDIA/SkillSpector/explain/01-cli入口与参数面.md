# 01 · cli.py：入口与参数面——"薄包装"哲学与 3245 行的现实

## 一、角色定位

`src/skillspector/cli.py` 是 SkillSpector 对人的唯一主接口。模块 docstring（cli.py:16-20）自我声明为"thin wrapper over the LangGraph workflow：把 CLI 参数映射为初始 state、调用 graph、把结果映射为输出与退出码，No business logic; workflow lives in the graph"。这句宣言与 3245 行的实体形成有趣张力——前 760 行确实是薄包装，但传递闭包扫描引擎（`_scan_transitive`，cli.py:1819 起）、多 skill 递归编排（`_scan_multi_skill`，cli.py:2667）这些"编排级业务"全部长在 CLI 层而非 graph 层。理解这个分层现实是读懂本文件的第一步：graph 只负责单次扫描的最小闭环，跨目标编排归 CLI。

三个 Typer 命令构成完整入口面：`scan`（cli.py:413-764）、`mcp`（cli.py:3114-3155，启动 MCP server）、`baseline`（cli.py:3158-3241，生成抑制基线）。

## 二、内部结构

**入口装配**：`_ensure_utf8_streams`（cli.py:83-100）在 import 期就把 stdout/stderr 重配为 UTF-8+errors=replace，防 Windows cp1252 编不出终端报告的 box-drawing 字符而崩溃。Typer app 定义在 cli.py:102-107，`no_args_is_help=True`。

**输出与传输枚举**：`FormatChoice`（cli.py:127-133）四格式 terminal/json/markdown/sarif；`_MACHINE_READABLE_FORMATS = {json, sarif}`（cli.py:137）是关键分界——机器可解析格式的全部状态文本走 stderr，保证 stdout 只有报告本体。`TransportChoice`（cli.py:140-144）服务 `mcp` 命令的 stdio/http 二选一。

**传递闭包预算体系**（cli.py:112-277）是本文件最重的一块：
- 模块级上限常量：`_TRANSITIVE_MAX_TARGETS = 32`、`_TRANSITIVE_MAX_BYTES = 10MB`、artifacts/findings/components/status_events/references 各 10000（cli.py:114-121），多 skill 上限 32 个（cli.py:122）；
- `_TransitiveBudget`（cli.py:147-157）打包成 dataclass；
- `_CachedTransitiveResult`（cli.py:160-180）缓存一次子扫描的全部 17 类产物；
- `_TransitiveTraversalState`（cli.py:183-277）是核心：`can_scan_more()`（cli.py:221-237）四预算联合判停（目标数/字节/制品/秒），`pause_deadline()/resume_deadline()`（cli.py:269-277）在等待网络下载时冻结时钟——时间预算只计扫描耗时、不计等待耗时；`_note_incomplete` 超过 256 条截断原因后以哨兵句"additional transitive limitations omitted"收敛（cli.py:205-212）。

**scan 命令主流程**（cli.py:413-764）按序分派：① `--mcp-registry` 独占分支（cli.py:590-619），与 recursive/baseline/yara 互斥且只支持 json 格式，直接走 `scan_registry` 不进 graph；② 本地路径预校验 `validate_local_input_path`（cli.py:624-630），URL/git@ 开头跳过；③ recursive 目录探测 `detect_skills`（cli.py:643-679），发现多 skill 则转 `_scan_multi_skill`，发现不完整也带账本事件继续有界扫描而非失败；④ 作者随包基线的 opt-in 机制（cli.py:694-717）：`.skillspector-baseline.yaml` 默认只提示不应用，须显式 `--use-shipped-baseline`——防止 skill 作者的基线替你压掉发现；⑤ 单 skill 主路径 `_scan_skill`（cli.py:2335-2417）。

**graph 调用与流式进度**：`_run_graph_scan`（cli.py:1374-1475）非流式直接 `graph.invoke`；流式用 `graph.stream(stream_mode=["updates","values"])`（cli.py:1425-1429），按节点更新推进 Rich 进度条并打印文件树与"Rule completed"行，全部写 stderr。`_wired_analyzer_node_ids`（cli.py:1366-1371）从编译后的 graph.nodes 反查真实接入的分析器集合，进度条总数 = 5 固定节点 + N 分析器。

**baseline 命令**（cli.py:3158-3241）：跑一次扫描（格式固定 json，因为"we consume findings, not report_body"，cli.py:3210-3211），把当前全部发现固化为指纹基线，供后续 `scan --baseline` 抑制旧发现、只报新增。

## 三、外部连接

- `from skillspector.graph import graph`（cli.py:47）——导入即触发模块级 `create_graph()`；
- `transitive` 子模块提供 `normalize_prefixes/canonicalize_source_identity`（cli.py:632-637、2396-2402）；
- `suppression` 五件套（Baseline/load/dump/effective_findings/discover，cli.py:71-78）；
- `multi_skill.detect_skills` 与 `mcp_registry.scan_registry`（cli.py:59-61）；
- `cleanup.cleanup_result` 在 finally 中兜底删除临时目录（cli.py:762-764）；
- LangSmith 追踪 `_build_trace_config`（cli.py:767-782），tags 携带 environment 与 version。

## 四、数据流

参数 → `_scan_state`（cli.py:309-333）构造 dict 初始 state（input_path/output_format/use_llm/llm_requested/source_local_only，baseline 加载失败在 scan 层映射为退出码 2）→ graph.invoke/stream → result dict → `_write_result`（cli.py:343-360，sarif_report 缺 report_body 时兜底 json.dumps）→ 退出码判定（cli.py:737-750）：`execution_successful=False`→2；`--fail-on-incomplete` 且不完备→1；`--fail-on-findings` 且有效发现非空→1；risk_score>RISK_THRESHOLD(50)→1；否则 0。子扫描结果经 `_cache_transitive_result`（cli.py:1151）与 `_source_aware_*` 系列函数（cli.py:879-1077）做来源隔离合并——子扫描的 finding_id 用 `_scoped_finding_id`（cli.py:865-867）按 source_identity 重散列，避免跨目标 ID 碰撞。

## 五、设计决策

1. **退出码契约三分**：2=输入/用法/执行错误，1=有发现或超阈或显式不完备（CI 门禁语义），0=干净。`--fail-on-findings` 与默认的 risk_score>50 是两个独立的 1 触发器，CI 里想"只要有发现就红"必须显式加前者。
2. **时钟暂停**：`pause/resume_deadline` 把 wall-clock 从预算中切出去，传递闭包扫多个 URL 时不会被下载等待时间吃光 600s 全局预算。
3. **结果缓存的键是 (target, source_local_only) 元组**（`_TransitiveTraversalState.cache`，cli.py:185），同一目标在 local-only 与完整模式下算两次——宁可重扫也不让"本地视图"污染"完整视图"。
4. **机器可读输出纪律**：所有进度/警告走 err_console，json/sarif 管道场景 stdout 永远干净。

## 六、新人提示（坑与勘误）

- scan docstring（cli.py:558-588）列出的 provider 清单含 nv_inference，但 providers 包在盘上只有 13 个子包，antigravity_cli 在 `providers/__init__.py:159` 注册却未出现在该帮助文本——帮助文本与注册表已漂移。
- `--mcp-registry` 分支在参数组合校验失败时退出码是 2 而非 1（cli.py:596、601）。
- recursive 多 skill 扫描不支持 `--baseline`（cli.py:652-657 直接退出 2），要按子 skill 分别建基线。
- `_result_body`（cli.py:336-340）暗示 terminal/json/markdown 三格式都由 report 节点产 report_body，sarif 可能只有结构化 `sarif_report` 字段——写消费脚本时要同时兜两者。
- 随包基线默认不生效是安全设计而非 bug：作者可以在基线里压掉自己的恶意发现，opt-in 权必须留在扫描者手里（cli.py:477-487 的 help 文本明说）。
- 传递闭包的截断原因列表上限 256 且去重（cli.py:205-212），看到"additional transitive limitations omitted"哨兵句说明真实截断数被收敛过。
