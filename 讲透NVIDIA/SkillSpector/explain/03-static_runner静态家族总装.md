# 03 · static_runner：静态模式家族的 2713 行总装

## 一、角色定位

`nodes/analyzers/static_runner.py`（2713 行）是 15 个 `static_patterns_*` 检测器的共享执行引擎：文件类型推断、多视图扫描、窗口切片、去重、许可证排除、资源预算、账本事件——全部集中在此，各检测器只声明"模式表 + analyze() + node()"三件套。它连同 `nodes/analyzers/__init__.py` 的 27 分析器注册表（ONBOARDING 称之为 SADD——Self-Auto-Discovered Directory，pkgutil 扫描自动发现，模块带 ANALYZER_ID+node 即注册，零接线成本）构成静态检测线的骨架。一个典型检测器薄到什么程度？`static_patterns_tool_misuse.node`（static_patterns_tool_misuse.py:3731-3735）只有一行实质调用：`static_runner.run_static_patterns_with_ledger(state, [sys.modules[__name__]])`——把自己整个模块当"模式模块列表"传进去。

## 二、内部结构

**常量与限额（static_runner.py:91-179）**：`FILE_TYPES` 19 种扩展名→类型映射（:91-110）；`MAX_FILE_CHARS` 复用 python_ast 的 1M 字符上限（:112）；`SECURITY_VIEW_WINDOW_CHARS = 256_000` 窗口 + `_WINDOW_OVERLAP_CHARS = 8192` 重叠（:113-115）；`MAX_FINDINGS_PER_ARTIFACT / MAX_FINDINGS_PER_ANALYZER` 各 10000（:153-154）；单制品静态分析时限默认 300s，可由 `SKILLSPECTOR_MAX_STATIC_ANALYSIS_SECONDS_PER_ARTIFACT` 覆盖（:155、158-179）。

**模块钩子协议（:645-689）**：模式模块可用四个显式开关与 runner 协作——`USES_PYTHON_AST`（opt-in 共享 AST）、`POSTPROCESS_USES_PYTHON_AST`、`POSTPROCESS_USES_RUNTIME_BUDGET`、`USES_RUNTIME_CHECK`，外加 `prepare_analysis/has_bounded_parse_exhaustion/postprocess_path_findings/cleanup_path_findings` 钩子。`_explicit_analysis_hook`（:650-655）用 `getattr_static` 校验"必须真声明"，防止动态查找造出假钩子。

**核心调用链**（自顶向下）：
- `run_static_patterns`（:2360-2452）：遍历 components，跳过 zip/docx 等容器路径与二进制（:2394-2402），预算检查后调 `_scan_all_views_detailed`（:2417-2426）；超时路径走 `_cleanup_expired_path_findings`（:2338-2357）——若模块带 postprocess 钩子但没有显式 cleanup，**丢弃部分前缀比泄漏中间态更安全**（:2354-2356 注释）。
- `run_static_patterns_with_ledger`（:2455 起）：同一扫描加"每个计划文件一条账本事件"——OPAQUE 内容记 PARTIAL/FAILED（:2491-2502）、被引用二进制记 PARTIAL、未引用记 OUT_OF_SCOPE（:2503-2512），完备性核算由此闭环。
- `_scan_all_views_detailed`（:1758-2273）是引擎心脏：先把模块分为 AST 组与词法组（:1771-1772）；声明式规避标记视图经 `_scan_declared_marker_views`（:1595 起，窗口常量 :137-152）；`prepare_analysis` 预构建（:1834-1841）；完备性哨兵 `has_bounded_parse_exhaustion` 在全制品上跑一次（:1898-1916，注释明说：窗口重叠无法证明"一条 shell 命令横跨多个窗口"的完备性）；AST 组走 `_scan_path`（:867）。
- **视图与窗口机器**：`_scan_view_windows`（:1080）、`_bounded_view_slices`（:1133）、`_AbsoluteSourceView`（:1155）；空白连续性投影 `_whitespace_continuity_views`（:1235）与 `_continuity_views`（:1371）——把跨窗口被切断的表达式用有界分隔符重拼辅助视图，"保留足够攻击者可控分隔符，使有界间隙表达式无法变成匹配"（:145-149 注释）；`_deduplicate_view_findings`（:1041）按视图作用域键 + finding 强度（`_view_finding_strength`，:988）裁决同一命中的多视图重复。
- **产物转换**：`analyzer_finding_to_finding`（:610-642）把分析器私有的 AnalyzerFinding 转成图态 Finding，explanation/remediation/category 缺省时从 pattern_defaults 补齐。

**配套文件**：`pattern_defaults.py` 的 `PatternCategory` 枚举（pattern_defaults.py:24）实测 18 个成员；`get_explanation/get_remediation/get_category/get_pattern_name`（pattern_defaults.py:450/457/465/470）是全部静态检测器的统一文案源。`common.py` 提供 markdown 围栏正则（common.py:31-32）、逻辑换行 `LOGICAL_LINE_BREAK`（:33，覆盖 \v\f\x1c-\x1e\x85   等 8 种换行字符）、`SourceLocationIndex`（:96）、AST 别名/类型解析工具族（:199-362）。以 `static_patterns_prompt_injection` 为样板：P1-P4 分级模式表（static_patterns_prompt_injection.py:65/89/102/130，P2 明确标注"仅 markdown 门控"）、`analyze()`（:324）、`node`（:527）。

## 三、外部连接

- `artifacts.security_text_views`（static_runner.py:36-42 import）——归一化/隐藏指令视图的生产者，runner 只消费；
- `security_reconstruction.build_declared_marker_views`（:65-69）——声明式规避标记的非执行重构；
- `python_ast.get_python_ast`（:60-64）——跨分析器共享 AST 缓存（键为 python_ast_cache_key）；
- `pattern_defaults` 文案、`inspection_ledger.ledger_event/analyzer_status_for_events`；
- state 的 `transitive_remaining_seconds`（:70、2407-2409）让静态扫描尊重全局传递闭包时钟。

## 四、数据流

state（components + local_file_cache 优先于 file_cache，:2372-2374）→ run_static_patterns_with_ledger → 逐路径：容器/二进制短路 → 时间与发现数预算 → （若模块 opt-in）共享 AST → `_scan_all_views_detailed`：原始窗口扫描 + 归一化视图 + 声明式标记视图 + 连续性投影，命中先按视图键去重 → postprocess 钩子全制品收口（:2298-2335）→ AnalyzerFinding→Finding → 每路径一条 COMPLETED/PARTIAL/OUT_OF_SCOPE 账本事件 → AnalyzerNodeResponse 返回。同一模式表在多视图上反复求值，靠 match_fingerprint 与视图键避免重复计数。

## 五、设计决策

1. **多视图扫描而非单文本扫描**：攻击面文本先经 artifacts 归一化（字距拉长/零宽/token 桥接），同一模式跑在原始窗口 + 安全视图 + 重构视图上——宁可多次匹配再去重，也不让混淆逃逸。
2. **256K 窗口 + 8K 重叠 + 连续性投影**三件套：把无界文本切成有界窗口的同时，用辅助投影兜住"跨界表达式"的完备性，这是对 ReDoS/超大制品的结构性防御。
3. **超时即弃私有前缀**：带 postprocess 的模块其中间态 finding 不是公共契约，宁可丢也不发半成品。
4. **许可证排除内置**（`_normalize_license_line` :430、`_is_license_basename` :503、`_is_license_boilerplate_line` :515）：Apache-2.0 头部的 "limitations" 等词不该触发模式。

## 六、新人提示（坑与勘误）

- **勘误钉版：手写 bash/shell 词法器不在 static_runner，在 static_patterns_tool_misuse.py**——`_ShellToken`（:390）、`_ShellCommandWord`（:400）、`_ShellDelimiterFrame`（:416，ONBOARDING 轮引用的 417 差一行）、`_bounded_static_substitution_end`（:2342）、`_bounded_shell_tokens`（:2352）。它是一套手写迭代式 shell 展开分帧器（引号状态机/ANSI-C 引号/花括号展开/case 子句计数），为的是在 3735 行的 tool_misuse 里对 rm -rf、root glob 等做词法级判定而非纯正则。
- 隐藏契约：钩子必须**显式声明**在模块上（getattr_static 校验，:650-655），动态 setattr 的属性会被无视。
- 静态线读 local_file_cache（含隐藏文件的全量本地视图），与 LLM 线读 llm_file_cache（脱敏投影）是两条数据道，改缓存逻辑时别合并。
- tour 描述"pattern_defaults 持有 19 类漏洞统一文案"，实测 PatternCategory 枚举 18 个成员（pattern_defaults.py:24-43）。
- 改任何 `static_patterns_*` 前先跑 tests/nodes/analyzers/test_static_patterns.py 及该模式专属回归；模式表新增条目要同步 pattern_defaults 文案，否则报告 explanation 为空。
