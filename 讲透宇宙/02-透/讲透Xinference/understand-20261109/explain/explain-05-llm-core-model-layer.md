# explain-05 · model/llm/core.py——LLM 抽象基类与引擎选择工厂

## 角色定位

这个 427 行的文件是 LLM 子系统的**两层枢纽**：上半部定义所有推理引擎共有的抽象基类 `LLM`（`model/llm/core.py:47`，abc.ABC），下半部 `create_llm_model_instance`（`:324`）是被 `model/core.py:56` 调用的 LLM 工厂——完成"family 匹配 → 引擎类选定 → 权重缓存 → 投机解码配对 → 实例化"。vLLM/MLX/Transformers/llama.cpp/SGLang 等每个引擎的 `core.py` 都继承这里的 `LLM`，因此 `match_json`/`load` 等钩子契约由本文件钉死。

## 内部结构

`LLM` 基类三块：①**构造即校验**（`:52-71`）：解析 replica uid（`model_uid, rep_id = parse_replica_model_uid(...)`，`:60`）、取第一个 spec 当默认（`:63-64`），位置/关键字参数多传一个直接 ValueError（`:68-71`）——引擎子类签名漂移会在构造期暴露；②**硬件探测五兄弟**（`:86-164`）：`_has_cuda_device`（pynvml）/_has_mlu_device（cnmon 命令行）/_has_vacc_device（/dev/vacc* glob）/_has_musa_device（pymtml），全部 `lru_cache` 且注释反复强调"**不要用 torch 探测**"（torch import 副作用会污染引擎环境）；③**引擎能力协商双钩子**：`check_lib`（类方法，库装没装）+`match_json`（模型/格式/量化能否跑），`match`（`:189-197`）= check_lib 通过且 match_json 为 True。另有两个准备钩子：`prepare_parse_reasoning_content`（`:206-228`，按 model_family 的 start/end tag 配 ReasoningParser；非 hybrid 模型强制作弊告警忽略 `enable_thinking=False`，`:209-213`；Kimi-K3 专用 parser 特判 `:215-219`）与 `prepare_parse_tool_calls`（`:230-236`，从 `TOOL_PARSERS` 注册表按 family 的 tool_parser 字段装配）。模块级还有 `chat_context_var: ContextVar`（`:247`，注释说明用 contextvars 而非层层传参，把 `enable_thinking` 等请求级设置带给下游 reasoning_parser，天然按协程隔离）。

## 外部连接

上游：`model/core.py:55-67`（八模态分发）→ 本工厂；`get_llm_version_infos`（`:41`）供 supervisor 启动时灌 CacheTracker（`core/supervisor.py:1012`）。下游：`match_llm`（`llm_family.py:542`）按名称/格式/尺寸/量化找 `LLMFamilyV2`；`check_engine_by_spec_parameters`（`llm_family.py:640`）从 `LLM_ENGINES` 表（model_name→engine→参数矩阵）返回引擎 `llm_class`——引擎名先做大小写不敏感纠错（`get_model_engine_from_spell`），四元组（name/format/size/quantizations）全匹配才放行，否则 ValueError 带完整参数清单；virtualenv 模式走 `check_engine_by_spec_parameters_with_virtual_env`（`:672`）额外校验 venv 标记。权重缓存委托 `LLMCacheManager`（`:383-384`），投机解码 drafter 也走它（`:398-401`，`use_draft_model=True`）。

## 数据流

`create_llm_model_instance` 六步：①`model_engine` 为 None 直接 ValueError（`:345-346`，LLM 必须显式选引擎）；②`match_llm` 找 family，找不到报带全部四元组的错（`:347-355`）；③选引擎类：`enable_virtual_env` kwargs 弹出，None 则回退 `XINFERENCE_ENABLE_VIRTUAL_ENV` 常量（`:357-361`），两条路径分别调 with/without virtualenv 的校验器（`:362-378`）；④缓存：无 `model_path` 时 `LLMCacheManager(llm_family, multimodal_projector).cache()` 下载/定位权重（`:381-384`）；⑤投机解码：`enable_mtp` 经 `parse_bool_launch_arg`（`:269-274`，注释点破 Web UI 提交的是字符串，`"false"` 不能当 truthy）解析，引擎不支持 `support_draft_model` 则拒绝（`:391-397`），缺 drafter 路径就按 spec 配对下载（如 Gemma-4 的 `*-it-assistant` MTP 小模型，`:386-401`）；⑥实例化：peft_model 存在时用 `inspect.signature` 探测引擎构造函数是否吃 `peft_model` 参数，不吃则**降级为无 LoRA 加载并 warning**（`:409-424`）。文件还内嵌两个小配方：`GEMMA_4_NUM_SPECULATIVE_TOKENS_BY_SIZE`（`:277-283`，按模型尺寸的投机深度查表）与 `parse_num_speculative_tokens`（`:295-321`，引擎中立校验——0/负数/非整数一律拒绝而非静默换默认值）。

## 设计决策

①**契约式双钩子而非能力表**：`check_lib`/`match_json` 下放给引擎自己声明，配合 `LLM_ENGINES` 集中注册表，"模型×引擎×量化"三维矩阵不需要中心化维护所有规则；②**硬件探测去 torch 化**：五处注释同一句话，因为引擎进程里 import torch 的设备初始化副作用曾引发误判，pynvml/cnmon/glob 是零副作用探测；③**ContextVar 传请求上下文**（`:239-247` 长注释）：避免把 `enable_thinking` 穿透五六层函数签名，协程级隔离保证并发请求不串台；④**降级而非失败**：LoRA 不支持时 warning 后裸加载（`:419-424`）——服务可用性优先于配置严格性，但这意味着配错 LoRA 只有日志可见。

## 新人提示

排"Model cannot be run on engine X"报错，看 `llm_family.py:640` 的四元组匹配——最常见是 quantization 拼写（`none` vs `int8`）或 size 传 int 而 JSON 里是 str。加新引擎要在三处注册：引擎自己的 `core.py`（继承 LLM、实现 `load`/`match_json`/`check_lib`）、`LLM_ENGINES` 表（llm_family.py）、以及 `__init__.py` 的导出。`prepare_parse_reasoning_content` 的 auto_insert_start_tag 逻辑（`:220`）决定非 hybrid 模型的 `<think>` 标签是否自动补——流式输出缺/多 think 标签的 bug 通常从这查起。`parse_bool_launch_arg` 与 `parse_num_speculative_tokens` 是"Web UI 字符串参数"的统一防波堤，新参数校验应复用同款模式。
