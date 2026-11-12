# llm/ — 多供应商 LLM 抽象：注册表、自动发现与统一工厂

> 精讲对象：`src/local_deep_research/llm/llm_registry.py`（261 行）+ `llm/providers/`（base.py / auto_discovery.py / openai_base.py + implementations/ 16 个实现）+ 入口 `config/llm_config.py::get_llm`（560 行）。LDR 的 LLM 层是"注册表 + 自动发现 + 统一包装"三件套，不是简单的 if-else 路由。

## 1. 角色定位

知识图谱 **layer:llm-providers（LLM 供应商抽象层）**，图谱层描述明确其职责："ollama/llamacpp/openai 兼容等 21 个 provider 实现、llm_registry 注册表与 providers/base 基类抽象，向上层屏蔽本地与云端差异"。它处在研究引擎（layer:research-engine）之下、配置层（layer:config）之侧：策略/引用处理/问题生成只拿 `BaseChatModel` 用，完全不感知供应商。目录拓扑：`llm/__init__.py` 导出注册表 API；`llm/providers/__init__.py` 末行一句 `discover_providers()`（L16）——**import 即扫描注册**，这是全层最关键的副作用。

## 2. 内部结构

**注册表（llm_registry.py）**：`LLMRegistry`（L26）线程安全、按用户分命名空间——`{namespace: {小写名: llm}}`（L33），`_SHARED_NAMESPACE = None`（L21）作共享命名空间哨兵。核心方法：`register`（L46，拒绝 None 值防静默穿透）、`get`（L97，**先查用户命名空间再回落共享**——用户注册永不影响他人）、`list_registered`（L136，确定性排序：own 优先 + shared 去重）、`clear`（L167，无参全清含 built-ins，是 64+ 测试的隔离夹具）。模块级单例 `_llm_registry`（L189）+ 6 个公开包装函数（`register_llm` L193 等）。

**基类契约（providers/base.py）**：`BaseLLMProvider`（L21）定义类属性契约——`api_key_setting` / `api_key_optional` / `provider_name`（默认 "unknown"，不改会被自动发现跳过）/ `egress_exposure`（L78，默认 `Exposure.EXPOSING`，ADR-0007 出网声明）。辅助方法族：`resolve_api_key`（L120，必填缺失抛 ValueError、可选返回 None）、`resolve_api_key_or_placeholder`（L147，统一占位符 `"not-required"` L9）、`has_api_key`（L173，fail-closed）。**最重要的一条契约在 docstring L55-58：`create_llm()` 必须返回裸 `BaseChatModel`，禁止在内部包装**——限速/token 计数/think 标签剥离统一由 `get_llm()` 事后追加。

**OpenAI 兼容腰层（openai_base.py）**：`OpenAICompatibleProvider`（L17）给一切 OpenAI 协议服务（llamacpp/lmstudio/openrouter/deepseek/xai/ionos/requesty/orcarouter/custom_openai_endpoint）提供公共 `create_llm`（L39）与模型列表（`list_models_for_api` L286，含 SSRF 校验 L343）。

**自动发现（auto_discovery.py）**：`ProviderDiscovery` 单例（L59-70）。`discover_providers`（L72）glob 扫描 `implementations/*.py`（L98）→ `importlib.import_module`（L107）→ `inspect.getmembers` 找类（L116），过滤条件五连（L123-137）：名以 Provider 结尾、`provider_name` 非 unknown、`issubclass(BaseLLMProvider)`、非基类自身、**`obj.__module__ == module.__name__`**（防止 import 进来的基类被重复注册）。命中即 `register_llm(normalize_provider(provider_key), obj.create_llm)`（L146-149）——**注册的是类方法本身**，即工厂函数。implementations/ 现有 16 个文件：ollama、llamacpp、lmstudio、openai、anthropic、google、deepseek、openrouter、xai、ionos、atlascloud、requesty、orcarouter、custom_{openai,anthropic}_endpoint。

## 3. 外部连接

图谱边：`llm_registry` 入边仅两条（`llm/__init__.py`、`auto_discovery.py`）——注册表被藏在整个包 API 之后；真正的枢纽是 `config/llm_config.py`，其入边多达 10 条（research_functions、research_service、report_generator、search_config、graders、evaluator、news_analyzer……）——**所有需要模型的模块都经 `get_llm`**。反向依赖：`llm_config.py` 顶部 `from ..llm.providers import discover_providers  # noqa: F401`（L15）——注释言明这是故意触发注册、失败必须炸响而非静默空注册表。安全侧连接：`security/egress/policy.py`（出网策略 PEP）、`security/ssrf_validator.assert_base_url_safe`（ollama.py:74）、`security/log_sanitizer.scrub_error`（凭据脱敏）；计量侧 `metrics.TokenCounter`（llm_config.py:537-551）；限速侧 `web_search_engines/rate_limiting/llm`（L509-518）。

## 4. 数据流 — 一次 LLM 调用的供应商选择链

研究循环里任何 `self.model.invoke(...)` 之前，模型都经历了这条链（`get_llm`，llm_config.py:54）：

1. **身份解析**：显式 `username` 参数 > snapshot 的 `_username`（L88-91，复用 `username_from_snapshot`）。
2. **参数解析**：model_name/temperature/provider 逐个 `get_setting_from_snapshot` 兜底（L94-105，provider 默认 "ollama"——本地优先的产品姿态）；清洗引号空白后 `normalize_provider` 归一小写（L108-116）。
3. **端点覆写**：`openai_endpoint` + 显式 URL 时浅拷贝 snapshot 叠加 `llm.openai_endpoint.url`（L123-132），不污染调用方。
4. **出网策略 PEP（fail-closed）**（L145-247）：无 snapshot 时只放行 `_LOCAL_DEFAULT_LLM_PROVIDERS` 白名单与用户注册的进程内 LLM（L185-196），其余一律 `PolicyDeniedError`；有 snapshot 时按 `resolve_run_primary_engine` 推导运行主引擎并构建 `EgressContext`，`require_local_llm=True` 则过 `evaluate_llm_endpoint`（L234-247）——注释记录了旧版 searxng 回退是 fail-OPEN 漏洞（L199-207）已被封死。
5. **注册表命中**：`is_llm_registered(provider, username)`（L252）→ 命中则取注册对象：callable 且非 `BaseChatModel` 视为工厂，以 `model_name/temperature/settings_snapshot` 调用（L260-264，TypeError 重抛签名提示）；是实例则直用（L279-281）。**自动发现的 built-in 供应商都走这条**——它们的 `create_llm` 类方法就是工厂。
6. **合法性校验**：有效供应商集合从 `get_discovered_provider_options()` 动态派生 ∪ {"none"}（L308-313）——历史上硬编码 `VALID_PROVIDERS` 与发现列表漂移（xai/ionos/deepseek 遗漏），现以发现为唯一真源；模型名必填（L325-332，不给默认模型防静默替换）。
7. **上下文窗口**：`_get_context_window_for_provider`（L28，转发 `_helpers`）写入 `research_context["context_limit"]` 供溢出检测（L341-353）。
8. **统一包装** `wrap_llm_without_think_tags`（L499）：可选限速包装（L509-518）→ 有 research_id 则挂 `TokenCounter` 回调（L534-551）→ 终饰 `ProcessingLLMWrapper`（L382）。

`ProcessingLLMWrapper` 是全链最精巧的一环：`_normalize_response`（L386）是**全仓唯一授权剥离 `<think>` 标签的位置**（docstring L388-399 明令禁止下游对新鲜 invoke 结果再做 `remove_think_tags`）——Qwen3/deepseek-r1 等本地推理模型会把思考链以纯文本吐出；`invoke`/`ainvoke` 都过它（L425/L433），`__getattr__` 透传其余属性（L444），`bind_tools` 覆写返回再包装的 bound model（L459-496）——否则 agent 循环拿到的裸模型会绕过 stripper，正是 issue #4804 `<think>` 污染 Anthropic 严格解析器的根因。

## 5. 设计决策

- **为什么注册表+工厂而非 if-else**：新供应商 = 在 implementations/ 丢一个文件，命名规范即被扫描、注册、进 UI 下拉（`get_provider_options` L181）——OCP 开闭原则的落地；注册类方法作工厂意味着**惰性构造**：`get_llm` 才带本次的 model/temperature/snapshot 实例化，同一供应商可为不同研究用不同参数。
- **为什么"裸模型 + 集中包装"**：若各 provider 自包装，限速/计数/think 剥离会出现 16 份漂移副本。集中到 `get_llm` 出口保证**每个 LLM 恰好包一次**，下游拿到即用。
- **为什么按用户命名空间**：多租户 web 服务下，一个用户注册的 "my-llm" 不能遮蔽他人 built-in，也不能泄进别人的列表（llm_registry docstring L5-11）。
- **为什么本地优先 + 出网 PEP**：LDR 的产品身份是 local-first（provider 默认 ollama、`OllamaProvider.egress_exposure = Exposure.CONTAINED`、`is_cloud=False`），云端是可选增强；PEP fail-closed 保证后台脚手架代码无法在无策略快照时悄悄实例化云端模型。
- **为什么 normalize_provider 小写归一**：设置存储、UI value、注册键三处大小写历史上不一致，`normalize_provider`（base.py:12）是唯一的归一收口。

## 6. 新人提示

- **切入点**：加供应商照抄 `implementations/llamacpp.py`（15-95 行，OpenAICompatibleProvider 最小 subclass）；本地非 OpenAI 协议参考 `ollama.py`（直连 `ChatOllama` + 自理模型列表）。
- **易错点 1**："Provider not registered by auto-discovery" 报错（llm_config.py:366）几乎总是 import 期炸了——去日志找 "Error loading provider from <module>"；`clear_llm_registry()` 无参连 built-in 一起清，恢复要 `discover_providers(force_refresh=True)`。
- **易错点 2**：测试里 patch 上下文窗口必须 patch `...config.thread_settings.get_setting_from_snapshot` 而非 llm_config 里的名字（L36-42 NOTE 明示函数内局部 import 导致的绑定差异）。
- **易错点 3**：`create_llm` 里别包 wrapper（契约 L55-58）；也别在业务代码里对 invoke 结果再剥 think 标签——重复且掩盖 bug。
- **易错点 4**：`resolve_api_key` 对必填供应商抛异常但 `has_api_key` 吞掉（base.py:181-183），`is_available` 默认 False 是 fail-closed——新 provider 不覆写它就不会出现在可用列表。
