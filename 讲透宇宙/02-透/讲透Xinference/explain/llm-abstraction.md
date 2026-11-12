# LLM 统一抽象与注册表：xinference/model/llm/{core,llm_family,__init__}.py

> commit b3de260。老版 `model/llm/llm.py` 已拆分：`core.py`（`LLM` 基类+工厂）、`llm_family.py`（族 Schema+匹配+注册表）、`__init__.py`（注册编排）。

## 一、角色定位

11 层图谱中同属 **layer:model-llm**（103 节点），是该层"宪法"：向下约束六引擎子包（vllm/sglang/transformers/llama_cpp/mlx/lmdeploy），向上被 `model/core.py:create_model_instance`（56 行分发）与 `launch_builtin_model`（worker.py:4129）、`ModelActor`（core/model.py:205，替代旧 `LLMModelV2`）消费。定义"什么是 Xinference 眼中的 LLM"及"由哪个引擎类承载"。

## 二、内部结构

**core.py（427 行）**：`LLM` 基类（47 行）契约四件套 `check_lib`（74）/`load`（186）/`match_json`（200）+组合器 `match`（189）；设备探测 `_has_cuda_device` 等四个（87-183 行，`@lru_cache` 且禁用 torch）；`chat_context_var`（247 行）按请求隔离传参；工厂 `create_llm_model_instance`（324）。

**llm_family.py（805 行）**：Spec 按 `model_format` 判别（`LlamaCpp/Pytorch/MLX LLMSpecV2`，73/108/136 行），聚合为 `LLMSpecV1`（370 行，**名 V1 实为 V2 类集合**）；`LLMFamilyV2`（169 行）含 `version: Literal[2]`、`model_ability` 九值（174-186 行）、`is_builtin`（202 行，`trust_remote_code` 门，CWE-94）；注册表（379-390 行）：`BUILTIN_LLM_FAMILIES`、六引擎 `*_CLASSES`、`LLM_ENGINES: [model_name][engine] -> llm_class`；匹配 `match_llm`（542）、查表 `check_engine_by_spec_parameters`（640）。

**__init__.py（335 行）**：`_install`（249）编排；`generate_engine_config_by_model_family`（75）三重循环 family×spec×引擎类，`cls.match()`（91）探测填 `LLM_ENGINES`；`load_model_family_from_json`（178）解析 163 个内置族并登记 `BUILTIN_LLM_PROMPT_STYLE`（204）。

## 三、外部连接

`llm_family.py` 入边 28 条，除本包外大量来自 transformers/legacy 手写模型文件（chatglm.py、qwen2_vl.py 等）——V1 活化石；`vllm/core.py` imports 两者。运行期上游 `core/worker.py`（3956 行 `asyncio.to_thread` 调 `create_model_instance`）、`ModelActor.__getattr__`（362 行透传 `async_chat`）；侧向依赖 `cache_manager.py` 下载权重。

## 四、数据流

**注册（启动一次）**：`_install()` 把 `llm_family.json`（163 族）经 `flatten_quantizations` → `LLMFamilyV2.parse_obj` 入 `BUILTIN_LLM_FAMILIES`（+下载模型按 `updated_at` 合并，289-321 行），再逐族逐 spec 逐引擎 `cls.match()`（仅 importlib 试探不实例化）生成 `LLM_ENGINES` 倒排索引；`register_custom_model`（132）做 `migrate_from_v1_to_v2`。

**launch**：REST `POST /v1/models` → `launch_builtin_model` → 子池建 `ModelActor` → `create_llm_model_instance`（core.py:324）：`match_llm`（347）锁 family+spec（hub 优先级 参数>环境嗅探>huggingface，587-608 行；`model_id` 的 `{}` 占位用量化名填充，566 行）→ `check_engine_by_spec_parameters`（372）查表取 `llm_class` → 缺 path 则 `LLMCacheManager.cache()` 下载（383）→ 投机解码 drafter 与门禁（391-407）→ `inspect.signature` 探测 peft 兼容（411）后构造（426）。`ModelActor.load()`（model.py:473）线程中调引擎 `load()`。

## 五、设计决策

1. **V2 vs 老版**：V1 每模型一个 Python 类、prompt 硬编码；V2 把模型变成**数据**——JSON 声明+pydantic 校验+`model_family` 字符串挂靠共享 chat_template（`BUILTIN_LLM_PROMPT_STYLE` 按 model_name 复用），163 族近乎零 Python 维护，`migrate_from_v1_to_v2` 平滑升级。
2. **能力探测放 classmethod**：`match/check_lib/match_json` 无需实例，注册期全量探测建索引、launch 期查表，把"能不能跑"从分钟级加载提前到毫秒级。
3. **多态收窄在构造参数**：基类拒收未知参数（68-71 行）、工厂按签名探测 peft（411 行），引擎类各自扩展而基类不膨胀。
4. **手写仅剩兜底**：能力挂靠校验（319-334 行）与 template 兑换（336 行）。

## 六、新人提示

- **切入点**：`_install`（249）→ `generate_engine_config_by_model_family`（75）→ `create_llm_model_instance`（324），半小时建全图。
- **加模型**：内置改 `llm_family.json` 即可（新架构需去引擎子包登记）；自定义走 `CustomLLMFamilyV2.parse_raw`（283 行），`model_family` 必填且 tools/vision 只能挂内置族，`chat_template` 传族名即继承停止符。
- **易错点**：① `"1_8"`=1.8，`validate_model_size_with_radix`（96 行）防误转 18；② 量化名大小写不敏感（558 行）；③ 未指定 quantization 取首个 spec 且 pytorch 补 `"none"`（633 行）；④ Web UI 布尔是字符串须过 `parse_bool_launch_arg`（269 行）；⑤ `is_builtin=False` 默认禁 `trust_remote_code`。
