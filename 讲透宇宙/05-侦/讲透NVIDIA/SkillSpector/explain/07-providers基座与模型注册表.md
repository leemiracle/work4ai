# 07 · providers 基座：协议四件套、工厂延迟 import 与 model_registry.yaml

## 一、角色定位

`src/skillspector/providers/` 是全部 LLM 流量的"变电站"：上游（llm_utils、llm_analyzer_base、constants、MCP server）只认这里的门面函数，下游 13 个子包各管一类后端（8 家 HTTP + 5 家本地 CLI）。包根四件套：`base.py` 用 `typing.Protocol` 定义能力契约（不强制继承）；`__init__.py` 是按名分派的工厂 + 回退链；`registry.py` 是 YAML token 预算查询器（带全局覆盖）；`chat_models.py` 存共享构造器与采样参数校验。"上下文多大、输出上限多少、没 key 怎么退"全收口在这层——语义线（06 篇）的批预算依赖它。

## 二、内部结构

**base.py——纯 Protocol，零实现**：
- `ModelMetadataProvider`（:37）：三个 ClassVar/方法契约——`DEFAULT_MODEL`、`SLOT_DEFAULTS`（:51-52）、`get_context_length`/`get_max_output_tokens` 返回 `None` 表示"不知道，请走默认"（:54-56）、`resolve_model(slot)` 三级瀑布 `SKILLSPECTOR_MODEL` env → 槽位默认 → 通用默认（:43-45, :58）。
- `CredentialsProvider`（:61）唯一方法 `resolve_credentials() -> (api_key, base_url|None) | None`（:69）；`ChatModelProvider`（:72）`create_chat_model(model, max_tokens, timeout=120)`（:75-81）。
- `AgentCLICapable`（:84）：CLI 提供方的**可选扩展协议**——`is_available() -> (bool, reason)`（:104）+ `complete(prompt, model, max_output_tokens)`（:106-112），HTTP 提供方不实现。
- `LLMProvider`（:115）= 前三者多继承的完整面；`has_cli_capability`（:119-127）用 `callable(getattr(...))` 鸭子判定而非 isinstance——外部注入的 provider 无需继承任何类也能被识别（Python 结构子类型运行期不强制）。

**__init__.py——工厂与回退链**：
- `_INJECTED_PROVIDER` 是 `ContextVar`（:75-78）：`use_provider()/reset_provider()`（:90-97）支持测试与 batch_scan 注入实例，优先级高于环境变量。
- `_select_active_provider`（:105-178）读 `SKILLSPECTOR_PROVIDER`（:111，默认空串）。**每个分支都是函数内局部 import**（:113-116 等）——装不起 langchain_anthropic/boto3 的环境不选对应 provider 就不碰这些依赖；唯一例外是默认的 nv_build 顶层 import（:65）。分支尽头 `raise UnknownProviderError` 附 13 个合法名清单（:173-178）。
- 回退链三处：`resolve_chat_model_credentials`（:213-222）无凭据且无注入绑定时回落 OpenAIProvider；`get_model_config_provider`（:225-247）给**模型元数据**单独定归属——显式绑定、CLI 提供方、Bedrock 实例三家保持权威（:235-240），无凭据 API 提供方仅当 OpenAI 回退也配好 key 才借用其元数据（:241-246）；`create_chat_model_with_provider`（:250-291）构造失败（None）时先查绑定（绑定即抛 :276-277），否则 OpenAI 兜底（:279-289），全空则 `raise_no_llm_api_key_configured`（:291）抛统一文案（:67-73，指引 `--no-llm`/ollama）。

**registry.py——YAML 查询**：`_load` 用 `@functools.cache` 按路径缓存（:43-64），坏文件降级空 dict+warning 而非抛错（:62-64）；`_resolve_path`（:67-70）让 `SKILLSPECTOR_MODEL_REGISTRY` **全局覆盖一切内置注册表路径**——8 家 HTTP 提供方的 REGISTRY_PATH 都会被这一行改写；`_lookup_token_limit`（:83-101）逐条防御：条目非 dict、字段缺失、非正整数一律 warning+None；`lookup_setting`（:104-108）与 `lookup_structured_output_method`（:111-113）支撑 structured_output/tool_choice 声明（08 篇消费）。

**chat_models.py——共享构造器**：`resolve_reasoning_effort/temperature/seed`（:38-69）读三个 SKILLSPECTOR_* env，temperature 限 [0,1]（:53-54），seed 限**有符号 64 位**（:34-35, :67-68）；`resolve_sampling_parameters(include_seed)`（:72-82）——只有 Azure/OpenAI 系接 seed；`validate_base_url`（:85-105）warning 级预检（不 raise）；`create_openai_compatible_chat_model`（:108-148）是四家 OpenAI 协议族的唯一构造点——`max_completion_tokens`（:126）、effort/sampling 注入（:130-134），`register_chat_model_controls`（:136-147）登记实际生效的采样控制供用量核算对账。

**model_info.py——门面**：`_resolve_context_length`（:32-50）查不到时 warning + `DEFAULT_CONTEXT_LENGTH` 兜底；`get_max_input_tokens` = ctx × 75%（:53-55）；`get_max_output_tokens` = min(ctx×25%, 注册表显式 cap)（:58-69）。tests/conftest.py:24-31 autouse fixture 就 patch 在这。

## 三、外部连接

上游消费者：llm_utils（get_chat_model/bind_structured_output，CLI 适配判断走 has_cli_capability）、constants.py 的 `_provider.DEFAULT_MODEL` 查询、llm_analyzer_base 的 token 预算（经 model_info）、mcp_server 的 is_llm_available。下游：13 个子包 + inference_usage。注册表与提供方同目录打包（`Path(__file__).with_name(...)`，nv_build/provider.py:35），仓根另有一份 `model_registry.yaml` 供自建部署指向（含 gpt-5.6-sol/terra/luna 三档与 azure 前缀 ID）。

## 四、数据流

分析节点 → `get_chat_model` → `_select_active_provider`（ContextVar 注入 > SKILLSPECTOR_PROVIDER）→ `resolve_model` 定标签 → `create_chat_model`（resolve_credentials→None→OpenAI 兜底→统一报错）→ ChatOpenAI/ChatAnthropic/... 返回。预算侧并行：model_info → lookup_context_length → `_resolve_path`（env 覆盖生效）→ functools.cache 命中的 YAML 表 → 75%/min(25%, cap) 折算批预算。

## 五、设计决策

1. **Protocol 而非基类**：13 家无共同父类，`has_cli_capability` 纯鸭子判定——外部 provider 零改动接入；base.py:24-27 解释了为何不用 runtime_checkable。
2. **延迟 import 即依赖隔离**：选 openai 就不 import boto3/langchain_anthropic；nv_build 作为默认反而顶层 import（:65）——默认路径必须零分支可用。
3. **注册表三态语义**：查到（int）/ 不知道（None→默认+warning）/ 坏数据（warning+None）——坏 YAML 永不打断扫描。
4. **env 覆盖全局生效**：一个 `SKILLSPECTOR_MODEL_REGISTRY` 同时接管 8 份内置 YAML，加模型不用改包。

## 六、新人提示（坑与勘误）

- **分支数勘误**：README:232-246 的 provider 表只列 12 行，磁盘实际 13 个子包（表漏了 `antigravity_cli`），而 `_select_active_provider` 有**第 14 个隐藏分支** `nv_inference`（:163-171，legacy 别名：try-import 不存在的子包，ImportError 回落 nv_build）——数分支别拿 README 当清单，以 `__init__.py:173-178` 报错信息里的 13 名 + 隐藏分支为准。
- **nv_build 默认模型的血泪注释**（nv_build/provider.py:41-51）：前默认 deepseek-v4-flash 已 410 Gone；替代选 glm-5.2 不是为快——快模型（1.6s/调用）在投毒样本上**全程自信返回阴性**，安全扫描器最怕的失败形态，慢模型（16s）才报 CRITICAL。
- **202749 组合上限坑**（nv_build/model_registry.yaml:18-25，意大利语注释）：endpoint 的输入+输出**合并**上限是 202749，按名义窗口 1000000 声明时 model_info 会算出 250000 输出预算，**每次调用都 400**。注释钉版原则："高估不会优雅降级——它把 LLM 阶段整个清零；低估才是安全的错法"。
- `SKILLSPECTOR_MODEL` 优先级压过一切槽位默认（各家 resolve_model 首查），但它不校验存在性——配错名只会在 HTTP 层失败。
- 注册表 `functools.cache` 按**解析后路径**缓存：同一进程内改 `SKILLSPECTOR_MODEL_REGISTRY` 再改回，旧缓存仍命中（测试期需 monkeypatch registry._load.cache_clear）。
