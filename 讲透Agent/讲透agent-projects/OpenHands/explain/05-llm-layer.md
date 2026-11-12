# 05 · LLM 封装层：`llm/` 的继承链、重试与注册表

> 覆盖：`openhands/llm/llm.py`（874 行）、`llm_registry.py`（153 行）、`retry_mixin.py`/`debug_mixin.py`、`async_llm.py`/`streaming_llm.py`、`bedrock.py`（39 行）、`router/base.py`（171 行），外挂 `openhands/utils/llm.py`
> 核心文件均带 `# Tag: Legacy-V0`；`openhands/llm/llm.py:8` 明言 "V1 replacement for this module lives in the Software Agent SDK"。

## 1. 角色定位

`openhands/llm/` 是 V0 对 **litellm 的大型门面**：把"任意厂商补全"统一成带重试、计费、日志、伪函数调用转换、能力探测的 `LLM` 对象，在事件流（04 篇 `event.py:6` 反向依赖其 Metrics）与 Agent（消费 completion）之间承上启下。代际身份微妙：**它是撤离清单上最大的一块，但撤离方式是整体搬去 Software Agent SDK 仓**——V1 的 agentic core 不再含 LLM 封装。读它的价值在理解 OpenHands 工程口味（mixin 拆分/partial 预绑定/延迟 import），这些手法在 SDK 仓延续。

## 2. 内部结构

**继承链**：`LLM(RetryMixin, DebugMixin)`（`openhands/llm/llm.py:64`）→ `AsyncLLM(LLM)`（`openhands/llm/async_llm.py:24`）→ `StreamingLLM(AsyncLLM)`（`openhands/llm/streaming_llm.py:18`）；旁支 `RouterLLM(LLM)`（`openhands/llm/router/base.py:24`）。`__init__.py` 再导出三代类（`openhands/llm/__init__.py:1-5`）；litellm 类型也在此层批量引入再导出（`llm.py:26-37`：Message/ModelInfo/completion/completion_cost/ModelResponse/Usage…）——消费方基本不必直接 import litellm。

**RetryMixin**（`openhands/llm/retry_mixin.py:22`）：tenacity 组 `retry_if_exception_type+stop_after_attempt+wait_exponential`（`:10-15`），五参可调（`:35-40`）。最有味道的是 `before_sleep`（`:42-60`）：遇 `LLMNoResponseError` 且 temperature==0 时**下次尝试自动升温 1.0**（`:52-57`）——针对贪心解码偶发空响应的经验补丁；`stop_if_should_exit`（`:19`）保证关停时重试让路。

**DebugMixin**（`openhands/llm/debug_mixin.py:20`）：`log_prompt/log_response` 走独立 logger（`:14`、`:37`、`:56`），未开 DEBUG **先短路再拼串**（`:22-24`）；图片 URL 仅 vision 激活时展开（`:70-75`）；`vision_is_active` 故意抛 NotImplementedError 由宿主实现（`:78-80`）——mixin 与宿主的契约。

**LLM.__init__**（`llm.py:71-245`）174 行装配：深拷贝配置（`:88`）、`init_model_info` 先行（`:104-108`）、可选 tokenizer（`:117-118`）；随后是**能力特判矩阵**——`openhands/` 前缀改写 `litellm_proxy/`（`:136-139`）、reasoning 模型剥 temperature/top_p（`:174-177`）、Gemini 2.5 low 档映射 128 token thinking 预算（`:148-155`）、指定 Claude 4.5/4.6 变体不发 reasoning_effort（`:161-170`）、Opus 4.1 显式禁 thinking（`:200-203`，issue #10510 化石）、Claude 系 temperature 与 top_p 互斥（`:205-215`）、Bedrock 三参（`:189-198`）；最后 `partial(litellm_completion, ...)` 把全部决策**冻结成预绑定函数**（`:221-234`），裸版另存 `_completion_unwrapped`（`:236`），再叠 retry 装饰器（`:238-246`）。

**wrapper**（`:246-434`）是每次补全总闸：函数体内 `from openhands.io import json`（`:248`）——**延迟 import 断 llm↔io 环**；位置参数归一（`:257-266`）；Message 转 dict（`:276-279`）；**伪函数调用**——模型不支持原生 FC 时把 tools 烘进 prompt（`:289-302`）、加 stop words（`:304-309`）、openhands-lm 在 SGLang 下必须 `tool_choice='none'`（`:312-316`，错误消息整段贴注释）；空消息防御（`:322-325`）；响应后把伪 FC 响应**转回**标准 tool_calls（`:364-374`）——`fn_call_converter.py`（979 行）承担双向解析。其余：`completion` property（`:437`）、`init_model_info`（`:444`）、能力探测三连（`:561-612`）、`_post_completion` 记账（`:614`）、`get_token_count`（`:699`）、`_is_local`（`:749`）、`_completion_cost`（`:764`）。

**LLMRegistry**（`openhands/llm/llm_registry.py:30`）按 `service_id→LLM` 记账（`:41`），构造即注册主 LLM 为 `active_agent_llm`（`:50`）。纪律型规则：`get_llm` 同 ID 换配置直接 ValueError（`:99-105`——"换配置请换身份"防隐式漂移）；`get_llm_from_agent_config` 对委托场景同 ID 异配置**明知不管**（`:80-84` TODO 留痕）；`request_extraneous_completion` 给摘要类旁路开无监听实例（`:65-76`）。观察者 subscribe/notify（`:137-153`），异常吞成 warning。`get_router`（`:118-135`）：`'noop_router'` 直通（`:127-129`），否则 `RouterLLM.from_config`。

**RouterLLM**：持 primary+路由池（`router/base.py:53-65`），model 名伪装 `router(a,b,c)`（`:71-77`）——计费日志一眼可辨；`from_config` 类工厂（`:162`）从 `ROUTER_LLM_REGISTRY`（`:21`）选策略。`TYPE_CHECKING` import LLMRegistry（`:18-19`）+ registry 侧函数体内延迟 import RouterLLM（`llm_registry.py:122-123` 注释自认）——**双向各让一步环就解开**。

**bedrock.py 39 行两函数**：`list_foundation_models` boto3 拉 ON_DEMAND 文本模型（`openhands/llm/bedrock.py:13-28`），异常吞成空列表（`:29-35`）；`remove_error_modelId` 一行过滤 bedrock 前缀（`:38-39`）。消费方 `get_supported_llm_models`（`openhands/utils/llm.py:109`）：litellm 双源清单（`:126`）先剥 bedrock（`:127-129`），AWS 三参齐再拉真清单（`:133-142`），Ollama 探 `/api/tags` 合并（`:149-154`）——`openhands/server/routes/public.py:30` 用它出前端模型下拉。

## 3. 外部连接

- **被消费**：Agent 经 registry 取 LLM；04 篇 `setup.py:87` 把 LLMRegistry 注入 Runtime，`main.py:107-111` 建 registry 并让 conversation_stats 订阅。
- **依赖**：litellm 全家（import 套 warnings 抑制 `llm.py:22-24`）、tenacity（`retry_mixin.py:10`）、boto3（`bedrock.py:8`）、延迟的 `openhands.io.json`（`llm.py:248`）、`LLMConfig/Message`（`:18`、`:41`）、`model_features.get_features`（`:20`，按模型名查能力位 `model_features.py:164`）。
- **环**：events↔llm 经 metrics（04 篇）；llm↔io 经延迟 import。
- **AsyncLLM 重复装配**：同套配置再 `partial(litellm_acompletion)`（`async_llm.py:30-45`），自己的 retry wrapper（`:49-56`）与同步版平行——`"see llm.py for more details"`（`:62`）是两处实现的互指注释。

## 4. 数据流

一次同步补全：Agent 交 `Message` 列表+tools → wrapper 归一参数 → `_function_calling_active=False` 时伪 FC 转换（`llm.py:297-302`）+stop words（`:304-311`）→ `log_prompt`（`:328`）→ `litellm.modify_params` 全局开关（`:333`）→ 调 `_completion_unwrapped`（`:355`）→ 异常族七种（`LLM_RETRY_EXCEPTIONS` `:53-61`）触发指数退避，空响应温度自动 0→1.0（`retry_mixin.py:52-57`）→ 响应记延迟（`:358-360`）→ 伪 FC 转回（`:364-374`）→ `_post_completion` 累计成本（`:614`）→ Metrics 随事件落盘（04 篇 `serialization/event.py:69-89`）。

## 5. 设计决策（V0→V1 代际语境）

- **partial 预绑定=配置冻结**：厂商特判构造期一次算完（`llm.py:221-234`），热路径零分支——代价是**运行时改 config 无效**；V1 SDK 沿用此道。
- **特判矩阵是供应商兼容史博物馆**：Gemini thinking 预算、Claude 参数互斥、SGLang tool_choice bug……每条带 issue 编号（`:178`、`:200-203`、`:312-316`）——多厂商网关的维护成本主体不是抽象，是**长尾补丁**。
- **mixin 而非装饰器**：Retry/Debug 横切面挂进 LLM（`:64`），AsyncLLM/RouterLLM 自动继承；mixin 的 `self.retry_decorator` 能拿实例状态（retry_listener）。
- **Registry"身份不可变"纪律**（`llm_registry.py:99-105`）：同 ID 禁换配置，把配置漂移前置成显式异常——与 04 篇 add_event 的 ID 防御同一哲学。
- **RouterLLM 命名伪装**（`router/base.py:77`）：路由器对外自称 `router(a,b,c)`，下游无需感知路由存在。
- **延迟 import 的分寸**：只有真成环处才延迟（io `:248`、RouterLLM `llm_registry.py:123`），其余顶层——与 02 篇 14 处风格一致：延迟是手术刀不是默认。

## 6. 新人提示

- **坑：`litellm.modify_params` 是全局变量**（`llm.py:333`，注释自认 `:330-332`）——多实例（Router 场景天然多）互相踩脚，最后一次设置 wins。
- **坑：bedrock 清单剥除无条件**（`utils/llm.py:127`）：litellm 自带 bedrock 项先清再单独拉真清单；boto3 失败（`bedrock.py:29-35` 吞异常）下拉里 bedrock 消失——**设计行为非配置错误**。
- **勘误：`retry_listner` 拼写少 e**（`llm_registry.py:39`）——实例属性名将错就错，改名破坏外部引用，别顺手修。
- **坑：`get_llm_from_agent_config` 同 ID 异配置静默复用旧 LLM**（`llm_registry.py:80-85`，TODO 自认）——委托 agent 想换模型会拿到主模型。
- **`_completion` vs `_completion_unwrapped`**（`llm.py:221-236`）：测试直调后者可绕日志/伪 FC，但**也绕过重试与计费**。
- **温度自动升温仅 temperature 为 0/未设时触发**（`retry_mixin.py:52-57`）：0.3 的空响应不会被调。
- **DebugMixin 短路**（`debug_mixin.py:22-24`）：生产开 DEBUG 级 llm_prompt_logger 会把完整 prompt 写盘，注意日志治理。
