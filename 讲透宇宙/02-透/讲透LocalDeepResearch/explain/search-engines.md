# 搜索引擎抽象：web_search_engines/（factory + base + 30 余引擎）

> `src/local_deep_research/web_search_engines/search_engine_factory.py`（812 行）、`search_engine_base.py`（1390 行）、`search_engines_config.py`、`engine_registry.py`。注意目录是 `web_search_engines/`，本仓无 `search/`。

## 1. 角色定位

16 层架构中的**搜索引擎抽象层**（layer:search-engines："引擎工厂、engine_registry 与 searxng/ddg/tavily 等 37 种引擎实现、rate_limiting 限流与相关性过滤"）。它是研究编排（`api/research_functions.py` → `langgraph_agent_strategy.py`）与异构检索源的唯一契约：上层只认 `BaseSearchEngine.run(query)`，不区分 SearXNG 自托管、DuckDuckGo 免费接口、Tavily 付费 API 或本地文档库（`engines/search_engine_library.py`）。

## 2. 内部结构

**factory** 三函数漏斗：
- `get_search()`（L662）：便捷入口，按引擎补默认参数（ddg/serpapi 等 5 引擎补 region/safe_search，L704）；
- `create_search_engine()`（L19）：装配线——解析 username（L48）→ 查 `retriever_registry`（L60，LangChain retriever 优先）→ snapshot 提引擎配置（L131 `search_config()`）→ 拒字面 `"none"`（L143）→ 未知引擎 fail-closed 抛 ValueError（L201，meta 引擎已删）→ **egress policy PEP**（L247 `evaluate_engine`）→ API key 解析（L298，缺 key 返 None）→ `get_safe_module_class` 白名单动态加载（L348）→ `inspect.signature` 过滤引擎不收的参数（L351）→ LLM 相关性过滤三级决策（L427：per-engine 设置 > `needs_llm_relevance_filter` 类属性 > 全局 skip）→ 按需包 `_create_full_search_wrapper`（L517）；
- `TIME_PERIOD_ENGINES = ("serpapi","tavily","wikinews")`（L16）：全局时间过滤只路由给支持的引擎。

**base** `BaseSearchEngine`（L115）是 `engines/` 下 32 个引擎类的抽象基类：
- 元数据类属性：`is_public/is_generic/is_scientific/is_local/is_news/is_code/is_books/is_lexical`（L142-184）供 UI 分组与策略选引擎；egress 双轴 `egress_sensitivity/egress_exposure`（L164）默认最保守象限（fail-closed）；
- 模板方法 `run()`（L631）两阶段检索：`_get_previews`（唯一抽象方法 L1347）→ preview filters → 科学引擎 DOI 预富集（L719）→ LLM 相关性过滤（L743）→ `_get_full_content`（L757）→ content filters；
- 共享设施：`AdaptiveWait`（L105）+ tenacity 重试（L682，3 次）；`_is_api_key_placeholder`（L85）+ `API_KEY_PLACEHOLDERS`（L45，防把环境变量名当 key 粘贴）；`_verify_egress_scope`（L515）运行时出口策略兜底（带 memo L560）。

**配置侧**：`search_engines_config.search_config()`（L99）从 snapshot/DB 读 `search.engine.web` 前缀，`_extract_per_engine_config`（L65）嵌套化，再从 `ENGINE_REGISTRY`（29 条硬编码 `EngineEntry`）注入 module/class，并动态追加 retriever 与 library 引擎——合计 30+ 可选。

## 3. 外部连接

图谱实证：base 被 34 文件 import（`search_system.py` + 全部引擎实现），全仓入度最高抽象之一；factory 出边指向 `security/egress/policy.py`、`module_whitelist.py`、`retriever_registry.py`、`engines/full_search.py`。调用方（grep）：`langgraph_agent_strategy.py` L1184/L1235、`api/research_functions.py` L124、`mcp/server.py`、`web/services/research_service.py`。下游：`rate_limiting/AdaptiveRateLimitTracker`（tracker.py L48，`get_wait_time` L233/`record_outcome` L324）、`relevance_filter.py`、`filters/base_filter.py`。

## 4. 数据流：一次搜索

API 研究请求 → `research_functions` L124 `get_search` → factory 读 snapshot 配置 + REGISTRY → egress 放行 → 反射实例化（如 `DuckDuckGoSearchEngine`）→ 策略层调 `run(query)` → `_get_previews` 返回归一化 `[{id,title,snippet,url}]`（schema 由 base 契约约定）→ 过滤/富集 → 限流时 `_raise_if_rate_limit`（L1097）抛 `RateLimitError` 触发自适应等待重试 → SearchTracker 记指标（L836，programmatic_mode 跳过）→ finally 清理临时属性与线程上下文（L846）。

## 5. 设计决策

- **统一两阶段 schema**：预览便宜全文贵，`_get_previews`/`_get_full_content` 分离使 LLM 过滤只作用于预览、全文抓取只给幸存者，成本随过滤收益递减。
- **统一 rate-limit**：各家限流表现不一（429/文案/配额），base 用 `rate_limit_patterns`（L210，子类可扩展）统一识别，共享 tracker 跨引擎学习等待时长。
- **配置与接线分离**：引擎参数存 DB（用户可改），module/class 硬编码于 `ENGINE_REGISTRY`，动态加载再过白名单——三层防注入，DB 值无法指定任意 Python 模块。
- **fail-closed**：未知引擎/策略拒绝均抛错不静默降级；ValueError 与 PolicyDeniedError 分开抛（L196 注释）便于区分配置错误与策略拒绝。

## 6. 新人提示

先读 `search_engine_ddg.py`（最短完整示例）再读 base 的 `run()`。**加新引擎四步**：① `engines/search_engine_<name>.py` 继承 base、实现 `_get_previews`、声明元数据类属性（别忘 egress 双轴，默认最保守）；② `ENGINE_REGISTRY` 加 `EngineEntry`；③ defaults JSON 加 `search.engine.web.<name>` 节；④ 需全文抓取则配 `full_search_module/class`。坑：`__init__` 务必把 `**kwargs` 转发 `super().__init__`（base L120 契约注释），否则 `settings_snapshot`/`programmatic_mode` 被静默吞掉——factory 兜底（L412）只救后者。
