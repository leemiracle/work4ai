# 03 · Embedding Providers：可选导入注册表与 build_embedding 工厂

## 角色定位

embedding 包（`datamind/capabilities/embedding/`）仅三文件却定义了全仓可扩展性范式：`factory.py:11` 的 `build_embedding` 是唯一入口，`providers/` 两实现装饰器自注册。所有可扩展轴共用 `core/registry.py:27` 的 `Registry` 泛型——`register(name)`（L36）、`create(name, **cfg)`（L55）、`known()`（L74），未知名报错附已注册清单。

## 内部结构

**可选导入注册表**是本包招牌（`embedding/providers/__init__.py`）：常驻项直 import（L10 `openai_compatible`，仅依赖 httpx）；可选项包 try/except——L15-18 `try: from . import huggingface / except Exception: pass`，注释明言 "so a base install still loads cleanly and the user gets a clear error only when they actually ask for this provider"。缺 sentence-transformers 不炸安装，只在选用时由 `HuggingFaceEmbedding.__init__` 二次延迟 import（`embedding/providers/huggingface.py:37-43`）抛 `ConfigError("...pip install datamind[huggingface]")`——错误延迟到决策点且带修复指引。**双名注册**：`embedding/providers/openai_compatible.py:41-42` 同类挂 `@register("openai_compatible")` + `@register("openai")`，配 `provider: openai` 命中同一实现。

## 外部连接

上游 `EmbeddingConfig`（`datamind/config.py:79-95`）：`provider` 是注册表键，`dimension=None` 留给首调探测（L86-87）。下游 KBService/SkillsService/memory/IngestService 全经 `build_embedding` 取实例。协议在 `core/protocols.py:227-228` 的 `@runtime_checkable EmbeddingProvider`（四件套，鸭子型免继承）。

## 数据流

`build_embedding`（`factory.py:11-47`）三步：①拼 kwargs——openai 系才带 timeout/retries/backoff（L24-31）；②**凭据回退**——`fallback_llm` 给出且 cfg 未配凭据时复用 LLM 网关（L33-39），支持"一钥一网关双端点"；③`registry.create`（L47）。运行时 openai_compatible：URL 归一化保证 `/v1` 恰好一次（`openai_compatible.py:68-71`）→ 批切分（L98-125 双上限）→ POST /v1/embeddings → 响应严校验：index 必须 JSON 整数且 bool 不算（L176-177）、按 index 重排（L179-181）、序号连续无重（L187-190）、维度批内一致（L191-195）、非有限值拒（L202-208）→ 首调探测 dimension（L209-215）→ usage 只采服务端报告（L218-226）。重试：5xx/408/409/429 可重试（L142-148），指数退避+抖动、尊重 Retry-After（L248-260）；`read_retry_budget_active()` 时立即上抛（L244-247）——外层已有预算，不让重试相乘。本地路径 `huggingface.py`：SentenceTransformer 同步编码丢 `asyncio.to_thread`（L59-65），dimension 以 `get_sentence_embedding_dimension()` 为权威（L49）。

## 设计决策（含批判）

可取：①"注册表+可选导入+决策点报错"三层漏斗让最小安装零负担；②凭据回退把网关型部署变一等公民；③对响应 index/dimension 的偏执校验把"截断响应看似完整批"变显式。**批判**：①`except Exception: pass`（`providers/__init__.py:17`）连语法错误都吞——huggingface.py 真有 bug 时症状是"provider 未注册"而非报错栈；②`_KNOWN_DIMS` 硬编码五模型（L32-38），新模型首调前 dimension=0 是脆弱哨兵（L78 占位、L210 覆盖）；③双名注册易被当两个实现。

## 新人提示

加新 provider 三步：类挂 `@embedding_registry.register("name")`、`providers/__init__.py` 加 try/except 导入、配 `DATAMIND__EMBEDDING__PROVIDER=name`——config.py 一字不改（`datamind/config.py:13-15`）。"unknown provider" 先看 `known()`；本地模型先 `pip install 'datamind[huggingface]'`。报 dimension mismatch（L197-201）查网关是否换底座模型。provider 必须 async embed_texts——协议在 `core/protocols.py:227`，runtime_checkable 只查签名。
