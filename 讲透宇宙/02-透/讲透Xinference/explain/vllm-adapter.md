# vLLM 引擎适配层：xinference/model/llm/vllm/core.py

> commit b3de260。老版单文件 `model/llm/vllm.py` 已扩为 `vllm/` 目录：`core.py`（2751 行主体）、`distributed_executor*.py`、`xavier/`；`__init__.py` 只剩 license——注册收到 `model/llm/__init__.py:_install`（255 行导入三类，266 行填 `SUPPORTED_ENGINES["vLLM"]`）。

## 一、角色定位

11 层图谱中位于 **layer:model-llm**，六引擎适配器中最重的一个：站在统一抽象（`LLM`、`LLMFamilyV2`）与 pip 安装的 vLLM 库之间——向上实现 `check_lib/load/match_json/async_generate/async_chat` 契约，向下把 `VLLMModelConfig/VLLMGenerateConfig`（95/129 行 TypedDict）翻译成 `AsyncEngineArgs/SamplingParams`，并吞掉 vLLM 版本碎片。

## 二、内部结构

**版本探测**：模块级 try-import 探针（159-174 行）置 `VLLM_INSTALLED/VLLM_VERSION`；`_update_vllm_supported_lists`（339-488 行）按版本闸门登记架构（如 `>=0.27.0` 才加 `KimiK3ForConditionalGeneration`，482 行）。

**三个模型类（能力分型）**：`VLLMModel(LLM)`（491 行）基座，`__init__` 先 pop Xinference 私货键（`xinference_vllm_executor_backend/address/n_worker/shard`，512-518 行）保证剩余 dict 直灌 `AsyncEngineArgs`；`VLLMChatModel(+ChatModelMixin)`（2137 行）获得 `get_full_context`（utils.py:337）与全套后处理；`VLLMMultiModel`（2333 行）管 vision/omni。

**load 四级路由（685-993 行）**：xavier（781）→ native_mp（801）→ 多 worker/多卡（857）→ 单机单卡。**消毒与执行**：`_sanitize_model_config`（1301）、`_sanitize_generate_config`（1404）、`async_generate`（1768）、`async_chat`（2262，`@vllm_check` 守护）。

## 三、外部连接

- **向上**：`restful_api.py:2030` 的 `model.chat(...)` 拿到 `ModelActor`（core/model.py:205），经 `__getattr__`（362 行）透传到 `async_chat`；launch 侧由 `create_llm_model_instance`（llm/core.py:324）经 `LLM_ENGINES` 选中本层类。
- **向下**：vLLM 库本体 + 自带 `XinferenceDistributedExecutor`（按 `pool_addresses` 连 xoscar 子池）+ `xavier/engine.py`；`_check_healthy`（1161）供生命周期回调。

## 四、数据流

**launch**：构造 `VLLMChatModel(uid, family, path, kwargs)` → `ModelActor.load()`（model.py:473）`asyncio.to_thread` 调 `load()`（685 行）：`_sanitize_model_config`（736 行：DeepseekV32 特判 `tokenizer_mode` 1307、`trust_remote_code` 双重门 1313、`tensor_parallel_size=_device_count` 1318、v1 多机补 `nnodes/node_rank/master_addr` 1319-1337）→ 装配 reasoning/tool parser（739-742）→ 分支构造引擎（native_mp 后台线程 `join(1)` 后 `wait_for_load` 995 轮询；多机用 `XinferenceAsyncLLMEngine._get_executor_cls` 覆写 919-933 注入分布式执行器）→ `_set_context_length`（1034）。

**chat**：`async_chat`（2262）`prefill_messages` 补 `content=None`（2236）→ `chat_context_var.set`（2279）→ 工具族判定 tools 进不进渲染上下文（2281-2289）→ `_sanitize_chat_config`（2292：reasoning 模型删 stop 2199-2201、`response_format:json_schema` 折成 `guided_json` 2214-2223）→ `get_full_context` 渲染 full_prompt（2302-2309）→ 进 `async_generate`（2312/2322）。

**async_generate**（1768）：enable_thinking/tools 强制 `skip_special_tokens=False`（1803）；LoRA 匹配（1811）；guided 参数组装（≥0.6.3，1833-1883）；**`inspect.signature(SamplingParams)` 运行时剔除当前版本不认识的采样键**（1885-1902，版本适配核心招法）；未设 `max_tokens` 按 `context_length - prompt_len` 兜底（1965-1977）→ `self._engine.generate(...)`（1991）。

**流式**：`stream_results`（1998）逐 `RequestOutput` → `_convert_request_output_to_completion_chunk`（1633）→ `previous_texts[i]` 增量切片（2014-2017）→ 回 `async_chat`：tools 走 `_async_to_tool_completion_chunks`（2317），否则 `_async_to_chat_completion_chunks(agen, self.reasoning_parser, ...)`（2318）边流边剥 `<think>`；非流式 `_to_chat_completion`/`_post_process_completion`（2330/2327）。

## 五、设计决策

1. **三类分型而非 God class**：generate/chat/multi 各自 `match_json`（1522/2139/2335）差异化设卡——基座要求 `generate` ability + CUDA/MLU/VACC/MUSA + Linux（1525-1533）、格式-量化矩阵（1542-1551）；chat 版收 ggufv2 要 ≥0.8.2（2171）。"vllm_engine_class 选择"实为**注册期双探（check_lib+match_json）+ launch 期查表**，无运行期工厂。
2. **版本碎片三层防御**：静态版本闸门 → 构造期消毒 → 调用期签名反射剔键；新采样参数在新 vLLM 自动生效、旧版优雅降级。
3. **加载不阻塞事件循环**：native_mp 线程+`join(1)`（854）；`load()` 注释（716-722）明令禁 `os.environ` 直改（非线程安全且子池已 fork），改由 `WorkerActor._create_subpool` 的 `env=` 注入。
4. **投机解码引擎中立**：drafter 由上层下载校验，本层 `_apply_draft_model`（1240）翻译成 `speculative_config`。

## 六、新人提示

- **切入点**：先读 `VLLMChatModel.async_chat`（最短完整请求路径），再回 `load()`（685）四级分支，最后 `_update_vllm_supported_lists`（339）。
- **加新架构**：`llm_family.json` 之外还需在 `_update_vllm_supported_lists` 按引入版本 `_append_unique`（否则 `match_json` 1552 架构检查会拒）；chat 与 multi 是两张表。
- **易错点**：① 缺库导入不炸，`match_json` 1559 放行与否取决于 `_virtual_env_allows_missing_vllm()`；② 排障先搜日志 "Dropping unsupported sampling params"（1898）；③ `enable_thinking` 须强关 `skip_special_tokens`，否则 `<think>` 被 tokenizer 吞、reasoning 解析必败（1803）；④ 多机须显式 `master_addr/master_port`（1329-1337），默认 `127.0.0.1:29501` 会撞车；⑤ 流式增量靠 `previous_texts` 游标切片而非 vLLM delta 语义，改 chunk 转换别破坏它。
