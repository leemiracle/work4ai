# 08 · API 云端 provider 子包群：八家 HTTP 后端的凭据、端点与结构化输出差异

## 一、角色定位

`providers/` 下 8 个 HTTP 子包——openai、openai_compatible、anthropic、anthropic_proxy、bedrock、azure_openai、nv_build、ollama——是同一份四方法契约（07 篇）的八种落地。骨架同构（DEFAULT_MODEL/SLOT_DEFAULTS/resolve_credentials/create_chat_model/registry 查询/resolve_model 瀑布，每个 80-90 行），**差异只有三处**：凭据读哪组 env、构造哪个 LangChain 类、拒绝强制 tool call 时结构化输出怎么退。四家 OpenAI 协议族共享 chat_models.py 构造器；anthropic 系三家 + azure 各持私有路径。

## 二、内部结构（逐家锚点）

**openai（provider.py）**：基线样板。`OPENAI_DEFAULT_BASE_URL` 仅文档意义（:33-34）；`_resolve_openai_project_headers`（:39-43）把 `OPENAI_PROJECT_ID` 变 `OpenAI-Project` 头；`resolve_credentials`（:52-58）读 `OPENAI_API_KEY` + 可选 `OPENAI_BASE_URL`；默认 `gpt-5.4`（:49）。

**openai_compatible（provider.py）**：Groq/Together/Mistral 等通用端。凭据用**独立命名空间** `SKILLSPECTOR_COMPAT_API_KEY` + `SKILLSPECTOR_COMPAT_BASE_URL`（:46-52），缺一返回 None——刻意不与 stock OpenAI env 混用；默认 `llama-3.1-70b-versatile`（:43）。

**nv_build（provider.py）**：`BUILD_BASE_URL = integrate.api.nvidia.com/v1`（:33），凭据 `NVIDIA_INFERENCE_KEY`（:57-60）；默认模型选型与 202749 坑见 07 篇六节。

**ollama（provider.py）**：唯一**无 key 也恒返回凭据**的家——`"ollama"` 占位串 + `OLLAMA_BASE_URL` 默认 `http://localhost:11434/v1`（:35, :46-54）。

**anthropic（provider.py）**：唯一定义**槽位默认**的家——`DEFAULT_MODEL = "claude-opus-4-6"` 而 `SLOT_DEFAULTS = {"meta_analyzer": "claude-sonnet-4-6"}`（:51-54，高频过滤 pass 用便宜模型）。构造直接 `ChatAnthropic`（:77-90）：`max_tokens_to_sample`、`stop=None`、effort（:85-87）与采样参数（:88-89）注入后登记 controls（:91-101）。`structured_output_method`（:115-120）：注册表声明优先，否则家族前缀命中 `rejects_forced_tool_call` 就返回 `"json_schema"`。

**anthropic_proxy（provider.py，284 行，八家最长）**：Vertex 风格 raw-predict 端点适配。三差异（docstring :22-28）：URL 带 `:streamRawPredict` 后缀、`Authorization: Bearer` 替代 `x-api-key`、body 带 `anthropic_version` 无 model 字段。实现是**httpx 传输层改写**而非换 SDK：`_rewrite_proxy_request`（:74-97）改 body、剥 `_PROXY_STRIPPED_HEADERS`（:66）、补 Bearer；同步 `_ProxyTransport`（:100-123）与异步 `_ProxyAsyncTransport`（:126-149）；`_ChatAnthropicProxy`（:162-209）覆写 `cached_property _client/_async_client` 注入自定义 http_client。凭据 `ANTHROPIC_PROXY_API_KEY` + `ANTHROPIC_PROXY_ENDPOINT_URL`（:218-224），真 key 用占位串（:244）。`SKILLSPECTOR_SSL_VERIFY`（:152-159）支持 false/CA 路径。默认 `claude-sonnet-4-6`（:215）。

**bedrock（provider.py，192 行）**：唯一 **SigV4 鉴权**的家——`resolve_credentials` 恒 None（:78-87，(api_key, base_url) 形状不适配；None 让上游回落 OpenAI 兜底，但真正构造在 create_chat_model）。`create_chat_model`（:89-166）：boto3.Session 探凭据链，解析不到返回 None（:126-127）；`BotocoreConfig` 把 per-call timeout 落成 read_timeout、connect 固定 10s（:66, :129-142）；**SDK 重试压到 1 次**（:67, :135-140）——重试预算归协调器管（要感知 Retry-After 与 deadline）。ARN 模型需显式 `provider="anthropic"`（:150-151）；不支持强制 toolChoice 的模型绑 `supports_tool_choice_values=("auto",)`（:152-156）。默认模型是跨区推理 profile（:63），区默认 us-west-2（:58）。`forced_tool_choice_supported`（:179-192）：注册表声明优先，否则 `claude_model_from_bedrock_id` 提取家族名判断。

**azure_openai（provider.py）**：唯一直连 `AzureChatOpenAI` 的家。凭据双变量 `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT`（:55-61）；`deployment` 默认取模型标签（:76）、`api_version` 默认 `2024-06-01`（:77）；**唯一带 seed 的家**（:87）。

**structured_output.py（共享判据）**：`FORCED_TOOL_CALL_REJECTED_MODELS = ("claude-fable-5-1", "claude-mythos-5-1")`（:35）；`rejects_forced_tool_call`（:40-44）兼容版本后缀；`claude_model_from_bedrock_id`（:47-59）剥 `us./eu./global.` 前缀与 `/` 分段——application-inference-profile ARN 提不出家族名，须注册表声明。

## 三、外部连接

向上全走 07 篇门面；`register_chat_model_controls` 全家接入 inference_usage 对账；registry 各指同目录 model_registry.yaml——anthropic（57 行 13 模型，fable/mythos-5-1 标 `structured_output: json_schema`）、anthropic_proxy（46 行同款）、bedrock（62 行，六 Claude 条目全 `tool_choice: auto`）、azure（84 行）、nv_build（42 行）、ollama（29 行）、openai（89 行）、openai_compatible（43 行）。llm_utils.bind_structured_output 消费 `structured_output_method`。

## 四、数据流

以 anthropic 为例：`SKILLSPECTOR_PROVIDER=anthropic` → `resolve_model("meta_analyzer")` → sonnet-4-6（槽位）→ `create_chat_model` → ChatAnthropic(带 effort/temperature) → `bind_structured_output` 时若模型是 fable-5-1 → registry 命中 json_schema → 走原生 JSON-schema 响应格式而非强制 tool call。Bedrock 同场景则是 `toolChoice auto` + prompt 求调用 + 散文答复重试（structured_output.py:26-29）。

## 五、设计决策

1. **同构骨架 + 私有差异**：八家逐行对齐，review 新提供方可用 diff 视角；允许各奔东西的只有构造函数内部。
2. **凭据命名空间隔离**：COMPAT_* 与 stock OpenAI 分离、PROXY_* 与直连 Anthropic 分离——一把 key 不会被两家抢读。
3. **传输层改写优于 SDK 更换**（anthropic_proxy）：保留 ChatAnthropic 全部能力（tool call/结构化输出/流式），只在 httpx transport 改协议形状。
4. **重试/超时预算上收**（bedrock :139）：SDK 重试与工作流 deadline 冲突，决策权交协调器。
5. **占位 key 两处妙用**：ollama/proxy 各用占位串让非空校验通过，真凭据路径显式改道。

## 六、新人提示（坑与勘误）

- **"8 家共用一个构造器"是错觉**：只有四家 OpenAI 协议族走共享构造器；anthropic 系三家 + azure 各自构造（参数名都不同：`max_tokens_to_sample` vs `max_tokens` vs `max_completion_tokens`）。
- anthropic 与 anthropic_proxy 的 `structured_output_method` 是**各自复制**的两份（provider.py:115 与 :279），改判据要动两处。
- bedrock `resolve_credentials` 恒 None 是**故意的**：07 篇 get_model_config_provider（:235-239）把 `isinstance(provider, BedrockProvider)` 列为权威例外，别"修"成返回真凭据。
- anthropic_proxy 剥 host/content-length 后**必须手工补 content-length**（:90）——body 长度变了，漏补被网关 400。
- nv_build 的 kimi-k2.6（256000）**没有** max_output_tokens 声明——输出预算走 25% = 64000，与 glm-5.2 的 32768 显式 cap 不同档。
- azure deployment 默认=模型标签（:76）：部署名与模型名不一致时必配 `AZURE_OPENAI_DEPLOYMENT`，报错只在 Azure 侧 404。
