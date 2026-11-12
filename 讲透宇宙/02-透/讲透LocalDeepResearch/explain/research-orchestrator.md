# research_functions.py — 研究编排心脏：迭代"搜索→阅读→综合"的完整链路

> 精讲对象：`src/local_deep_research/api/research_functions.py`（781 行，API 门面）
> 配套深读：`search_system.py`（AdvancedSearchSystem）与 `advanced_search_system/strategies/source_based_strategy.py`（真正的迭代循环体）——研究编排在 LDR 中是"三层接力"而非单文件。

## 1. 角色定位

知识图谱 16 层架构中，这三个文件同属 **layer:research-engine（研究引擎与编程接口层）**，是整个系统的中轴。`research_functions.py` 是**程序化 API 的总入口**：对外暴露 `quick_summary` / `generate_report` / `detailed_research` / `analyze_documents` 四个公开函数（图谱 contains/export 边各 4 条），对内把一切配置收敛成一个 `AdvancedSearchSystem` 实例然后退场。注意它与 web 路径的关系：Web UI 走的是 `web/services/research_service.py` 的 `run_research_process`（L914），后者**绕过本文件、直接构造 `AdvancedSearchSystem`**（research_service.py:1549）——所以本文件是"SDK/编程接口"的心脏，而 `AdvancedSearchSystem` 才是两条路径共享的真心脏。图谱入边证实消费方为 `api_v1.py`、`server.py`、`benchmark_service.py`、`benchmarks/runners.py`（后者 `from ..api import quick_summary`）。

## 2. 内部结构

文件内 6 个函数分三组：

- **装配组**：`_init_search_system`（L33-163）——研究系统的唯一组装点。注册 retrievers（L81-87）与自定义 LLMs（L89-95）→ `get_llm()` 取模型（L102）→ `get_search()` 取搜索引擎（L124）→ 构造 `AdvancedSearchSystem`（L138）→ 覆写 `system.max_iterations` / `questions_per_iteration`（L156-157）→ 挂 `progress_callback`（L160）。异常时 `safe_close(llm)` 防泄漏（L149-153）。`_close_system`（L22-30）是镜像的拆卸点。
- **四个公开函数**：`quick_summary`（L167，快速摘要）、`detailed_research`（L512，结构化数据返回）、`generate_report`（L345，额外接 `IntegratedReportGenerator` 产出 markdown 报告，L483-489）、`analyze_documents`（L621，本地文档集合检索，不进迭代循环）。
- **公共骨架**：三者共享同一套仪式——settings snapshot 缺失时 `create_settings_snapshot()` 兜底并告警（L228-263）、生成 `research_id`（L266-270）、注册自定义组件、`set_search_context(search_context)` 写线程上下文（L304）、`finally` 中 `_close_system` + `clear_search_context()`（L338-341）。

真正的状态机在下游两级：

- `AdvancedSearchSystem`（search_system.py:69）：持有 `model`/`search`/`citation_handler`/`question_generator`/`findings_repository`，经 `search_system_factory.create_strategy`（L201-268）实例化策略——docstring L96-116 列出 20 种策略名（source-based/iterdrag/recursive/browsecomp/evidence/constrained 系列等），本文件默认 `search_strategy="source_based"`（L40）。
- `SourceBasedSearchStrategy.analyze_topic`（source_based_strategy.py:165）：**迭代循环本体**。

## 3. 外部连接

出边（imports）：`config/llm_config.get_llm`、`config/search_config.get_search`、`search_system.AdvancedSearchSystem`、`report_generator.IntegratedReportGenerator`、`settings_utils`、`utilities.db_utils.no_db_settings`（装饰器，L166/L344/L511/L620——programmatic 模式关闭 DB）、`utilities.thread_context`、`security.file_write_verifier.write_file_verified`（L493，落盘受 `api.allow_file_output` 门控）。

入边：如上四个消费方。`search_system.py` 的入边更广——`research_functions.py`、`report_generator.py`、`research_service.py`、`evaluator.py`、`topic_based.py`，坐实"所有路径汇聚于 AdvancedSearchSystem"。策略家族经 `BaseSearchStrategy`（base_strategy.py:27）抽象：`analyze_topic` 是唯一抽象方法（L142），`check_termination`（L99）复用 progress_callback 实现取消检查——8 个 `CHECK_CONTEXT_*` 常量（L17-24）标记循环内 8 个取消检查点。

## 4. 数据流 — 一次 quick_summary 的完整迭代流转

以 `quick_summary("量子计算最新进展?")` 为例：

1. **快照与上下文**：`create_settings_snapshot()` 冻结配置（线程安全快照传播到后台搜索线程，L300-303 注释）；`set_search_context` 携带 research_id/query/mode/phase。
2. **装配**：`_init_search_system` → `get_llm` → `get_search` → `AdvancedSearchSystem` → 工厂造出 `SourceBasedSearchStrategy`。注意 `all_links_of_system` 列表**按引用**传入策略（search_system.py:198 ↔ source_based_strategy.py:94-95 docstring），是跨层共享的引用单一真源。
3. **进入状态机** `analyze_topic`（search_system.py:321）→ `_arm_egress_backstop`（L367，CLI/API 路径兜底武装 PEP-578 出网审计钩子）→ `_perform_search`（L414）→ `strategy.analyze_topic`（L476）。
4. **迭代循环**（source_based_strategy.py:226 `for iteration in range(1, iterations_to_run+1)`，默认 `search.iterations=2`）：
   - *提问*：第 1 轮把**用户原句 verbatim** 与 LLM 生成问题并搜（L283-287，防 LLM 误读歧义查询；超 300 字符自动降级只搜 LLM 问题，L252-265）；第 2+ 轮用累积结果的最近 `[-30:]` 条（`search.question_context_limit`，L318-324）作上下文生成后续问题——**这就是"阅读"环节：上一轮搜索结果是下一轮提问的教材**。
   - *并行搜索*：每个问题一个线程，`@preserve_research_context` 装饰的 `search_question`（L366-380）→ `run_parallel_searches`（L386）；结果 extend 进 `accumulated_search_results_across_all_iterations`（局部变量，L178/L410）。
   - *取消检查*：循环首（L227）、搜索后（L396，注释明言这是单次迭代最大停顿 10-30s）、综合前（L471）。
5. **终过滤**：`cross_engine_filter.filter_results`（L435-445），`start_index=len(self.all_links_of_system)` 保证新引用号续接。
6. **综合**：`citation_handler.analyze_followup`（L498）产出带 [1][2] 引用号的正文；失败时降级保留来源不写 Error 进正文（L496-531，区分"综合失败"与"无结果"两种文案）。
7. **回传**：`findings_repository.format_findings_to_text`（L571）→ 返回 dict（L609）→ `_perform_search` 附上 `search_system` 自引用与全量 links（L494-495）→ `quick_summary` 取 `current_knowledge` 作 summary（L321-322）→ finally 拆系统清上下文。

`generate_report` 的差异：初次 `analyze_topic` 后，`IntegratedReportGenerator` 对**每个章节小节再次调用 `analyze_topic`**（docstring L58-60），`all_links_of_system` 跨调用持续 extend、引用号靠 `total_citation_count_before_this_search`（L184）续接——第一轮 [1]-[15]、第二轮 [16]-[28]。

## 5. 设计决策

- **为什么迭代循环而非一次性**：单轮搜索受制于查询措辞与搜索引擎首屏；循环让 LLM 读到上轮 snippet 后**生成更精准的后续问题**（iterative deepening），`[-N:]` 截断控制上下文膨胀。同时用 `search_original_query=True` 保底——LLM 可能把 "local deep research" 歪解成 Austin 热岛（L247-249 注释实例），verbatim 原句保证至少一次搜索命中正题。
- **为什么策略模式**：20 种策略共享 `BaseSearchStrategy` 接口与进度/取消/引用基建，工厂按名字惰性导入（`create_strategy` 内 import），使 browsecomp/constrained 等重策略零成本共存。`AdvancedSearchSystem` 只做编排不做研究——单一职责让它同时服务 web/SDK/benchmark。
- **进度回调即取消通道**：不另设 termination callable，复用已铺到 15 处的 `set_progress_callback` 管线（base_strategy.py:103-108 注释），research_service 识别 `"termination_check"` phase 即查标志返回。
- **安全内建**：异常经 `sanitize_error_for_client`（L592，max_length=500）防 CWE-209 凭据泄漏；"Error:" 前缀保留供 research_service 路由 ErrorReportGenerator（L583-584 注释）。

## 6. 新人提示

- **切入点**：先读 `SourceBasedSearchStrategy.analyze_topic` 的类 docstring（L30-63）——作者自己写了最准确的高层流程图；再对照 search_system_factory.py:30 的 if-链看策略如何被选中。
- **易错点 1**：`accumulated_search_results_across_all_iterations`（局部）与 `self.all_links_of_system`（共享）是两个列表，L171-177 注释反复强调；混用会导致 detailed report 引用重复（issue #301 修复即 `id()` 判重，search_system.py:488-491）。
- **易错点 2**：改迭代行为时别只改 `system.max_iterations`——策略内 `iterations_to_run` 在 `analyze_topic` 里重新从 snapshot 读 `search.iterations`（L208），构造参数只是初值。
- **易错点 3**：`quick_summary` 无 snapshot 时会退到默认+环境变量并打 warning（L244-248）；调试"为什么没用我的配置"先查这条日志。
- **易错点 4**：搜索线程里 `get_search_context()` 依赖 `@preserve_research_context`（L366）传递，删装饰器会导致 metrics/research_id 静默丢失。
