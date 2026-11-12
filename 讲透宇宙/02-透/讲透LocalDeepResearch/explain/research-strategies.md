# strategies/ 研究策略家族 — 五种深度实现与 create_strategy 注册器

> 精讲：`search_system_factory.py`（403 行注册器）+ `advanced_search_system/strategies/`。勘误：UI 清单 `constants.py::AVAILABLE_STRATEGIES`。

## 1. 角色定位

知识图谱 16 层中属 **研究引擎与编程接口层**。`AdvancedSearchSystem`（search_system.py:69）是壳，`create_strategy`（factory L30）按名造策略，策略决定搜几轮、怎么提问、何时综合。图谱实证 `base_strategy.py` 入边 7 条——五个策略加 `enhanced_contextual_followup` 全部继承它。

## 2. 内部结构

- **BaseSearchStrategy**（base_strategy.py:27）：唯一抽象方法 `analyze_topic(query) -> dict`（L142）。公共基建：`check_termination`（L99，**复用 progress_callback 做取消检查**）、8 个 `CHECK_CONTEXT_*` 常量（L17-24）、`get_setting`（L87）。
- **create_strategy**（factory L30-402）：if-链分发+别名归一（L60）；分支 lazy import；kwargs>snapshot>默认。已删除的 `mcp`/`agentic` 为 `langgraph-agent` 弃用别名（L342）；未知名**警告后回落 source-based**（L385）。
- **策略文件**：`source_based`（source_based_strategy.py:28）、`focused_iteration`（:46）、`topic_organization`（:20）、`langgraph_agent`（:1888）、`news`（:298 内部）；`focused-iteration-standard` 是 focused 同类换 standard citation handler（factory L188）。

## 3. 外部连接

- **上游**：`AdvancedSearchSystem.__init__` 在 search_system.py:201 lazy import、L241 调用；`mcp/server.py:47` 亦复用。特殊名 `enhanced-contextual-followup` 不走工厂，先造 delegate 再包装（search_system.py:204）。
- **下游**（图谱实证）：source_based 引 `cross_engine_filter`/`parallel_search`/`citation_handler`；langgraph_agent 自带工具构造（L1166/L1677）。
- **UI 清单**：`AVAILABLE_STRATEGIES`（constants.py:124-149）被首页路由（fastapi_app.py:2498）、设置 UI、news 表单、MCP、metrics 共用——勿手抄第二份。

## 4. 数据流 — 各策略的循环差异

公共主干：`AdvancedSearchSystem.analyze_topic`（search_system.py:321）→ `_perform_search`（L414）→ `strategy.analyze_topic`（L476）。差异在循环体：

- **source-based（固定轮）**：`for iteration in range(1, iterations_to_run+1)`（L226），轮数读 `search.iterations` 默认 2（L217）；每轮=从累积结果生成问题→并行搜索→累积，首轮混入用户原句 verbatim；轮后统一过滤+单次综合。
- **focused-iteration（自适应迭代）**：默认 8 轮×5 问（L63，SIMPLEQA 调优）；循环首/搜索后/综合前三个取消检查点（L176/L249/L325）；实体覆盖追踪+验证搜索（L242/L258）；知识摘要四级截断（L71-76）省 token。
- **topic-organization（两阶段）**：采集（自研或委派 focused-iteration，L118）→ 聚类成主题 → 每主题 lead text → 可选精炼轮（默认关）。
- **langgraph-agent（无固定问题循环）**：`analyze_topic`（L2538）用 `create_agent` 起 agent，外层 50 步+子代理 8 步；`_build_tools` 按出网策略预过滤工具（L2600-2630）；LLM 自主决定搜什么、何时综合。
- 共享 `all_links_of_system` 按引用传入、引用号偏移续接（L180），多小节调用编号才连续。

## 5. 设计决策

- **if-链工厂而非插件/entry-points**：每分支 lazy import，选 source-based 不必装 langgraph 依赖树。
- **单一抽象方法+回调复用**：进度与取消同走 `progress_callback`（base_strategy.py:99）。
- **UI 清单与工厂名单分离**：工厂另认别名与内部策略（news_aggregation）。

## 6. 新人提示

- 新增策略三步：继承 `BaseSearchStrategy` 实现 `analyze_topic` → `create_strategy` 加分支 → `AVAILABLE_STRATEGIES` 加条目。
- 排查"策略没生效"：未知名只警告并回落 source-based（factory L386）；连字/下划线皆认，不分大小写。
- 三个"iterations"语义不同（2/8/50）；测试取消用 `CHECK_CONTEXT_*` 定位检查点。
