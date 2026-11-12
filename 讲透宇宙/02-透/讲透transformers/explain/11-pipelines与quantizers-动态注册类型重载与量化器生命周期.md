# 11 · pipelines 与 quantizers：类型重载工厂、动态注册与量化器生命周期

## ① 角色定位

这两套子系统分别管"推理一步到位"与"权重按需降精度"。`src/transformers/pipelines/__init__.py`（1124 行）暴露 `pipeline()` 超级工厂：给个模型名，自动查任务、拉模型、组管线。`src/transformers/quantizers/auto.py` 与 `base.py` 构成量化分派层：模型 config 里一个 `quant_method` 字符串，路由到对应的 HfQuantizer 完成加载期改造。两者在 2026 版都长出了**第三方注册钩子**——库的封闭注册表时代结束。

## ② 内部结构

**pipelines**：核心是 `PIPELINE_REGISTRY = PipelineRegistry(supported_tasks=SUPPORTED_TASKS, task_aliases=TASK_ALIASES)`（__init__.py:295）+ `get_task`（L305，按模型名上 Hub 查 pipeline_tag）。文件 2/3 的篇幅（L373-434+）是 `<generated-code>` 标记的 **26 个 `def pipeline`**——25 个按任务 Literal 的 @overload（"any-to-any"→AnyToAnyPipeline、"audio-classification"→AudioClassificationPipeline……各返回精确类型）加 1 个真实现（L670）。overload 区由 `utils/check_pipeline_typing.py --fix_and_overwrite` 生成，与 modular 同款"生成文件不可手改"纪律。运行时基类 Pipeline(_ScikitCompat, PushToHubMixin)（base.py:757）定义 preprocess（L1151）→ _forward（L1159）→ postprocess（L1172）三段式与 run_single 调度（L1301）。

**quantizers**：`AUTO_QUANTIZER_MAPPING`（auto.py:77）与 `AUTO_QUANTIZATION_CONFIG_MAPPING`（L110）是两张并行注册表，`get_hf_quantizer`（L338）按 config 实例化。HfQuantizer 抽象基类（base.py:73，346 行）定义完整生命周期钩子：requires_calibration 类属性（L86）、validate_environment（L136）、update_dtype/update_device_map（L99,111）、**update_tp_plan/update_ep_plan/update_attn_implementation**（L144,148,152——量化器有权改写并行计划与注意力实现）、`_process_model_before_weight_loading`（L156）/`_process_model_after_weight_loading`（L177）前后夹击权重加载、dequantize（L212）、get_modules_to_not_convert（L238）、is_qat_trainable（L260）。

## ③ 外部连接

自定义任务的动态注册走 `clean_custom_task`（__init__.py:361-370）：无 "impl" 键直接 RuntimeError（L364-365）；有则把 task_info["pt"] 里的**类名字符串**经 `getattr(transformers, c)` 就地解析成类对象（L369）——远程模型 repo 的 custom pipeline 定义在加载时才绑定到当前进程的 transformers 命名空间。量化侧的第三方钩子是 `register_quantizer(name)` 装饰器（auto.py:322-334）：重名 **raise ValueError**（L327），非 HfQuantizer 子类 raise TypeError（L330）。上游建模侧：quantizers 目录 26 个 quantizer_*.py，但注册表 **27 键**——"mxfp8" 复用 FineGrainedFP8HfQuantizer（L102-104 注释：MXFP8=FP8(E4M3)+E8M0 块尺度，解包藏在 Fp8Dequantize._dequantize_one）；唯一不带 Hf 后缀的注册名类是 AutoRoundQuantizer（L101）。

## ④ 数据流

pipeline() 调用链：task 为 None 时 get_task 上 Hub 推断（L955）→ task 命中 custom_tasks 则 clean_custom_task（L958-959）→ registry 查 (pipeline_class, modelclass) → 依次解析 model/config/processor 并按任务自动补齐缺的组件 → Pipeline 子类实例化。量化加载链：PreTrainedModel.from_pretrained 读到 config.quantization_config → AutoQuantizationConfig.from_dict（L161）按 quant_method+load_in_4bit/8bit 后缀（L164-165）选 config 类 → get_hf_quantizer → validate_environment（缺依赖早爆）→ before 钩子把 nn.Linear 换成量化占位 → 权重加载 → after 钩子做打包/校准后处理 → update_* 钩子同步修订 device_map 与并行计划。

## ⑤ 设计决策与勘误

- **类型重载即文档**：25 个 Literal overload 让 IDE 对 `pipeline("fill-mask", ...)` 直接提示 FillMaskPipeline 的专属参数——用生成代码换类型体验，是 1124 行里占 600 行的原因。
- **勘误一**："26 种量化方法"的口径要精确：26 个 quantizer 文件 ≠ 26 个注册键，注册表实为 27 键（mxfp8 别名复用 FP8 量化器），数文件会漏、数键才准。
- **勘误二**："quantizers 只管加载权重"低估了它的权限——update_ep_plan（L148）说明量化器参与专家并行布局决策，量化与分布式在这层交汇，不是纯数值层。
- **clean_custom_task 的 getattr 是双刃剑**：模型 repo 里的字符串在本进程命名空间解析，transformers 升级删类时 custom pipeline 会在运行时才 AttributeError——报错点离根因很远。
- 注册语义不对称：register_quantizer 重名即抛错（防御性，量化正确性优先），而 exporters 侧的 register_exporter 重名仅 warning+覆盖（见第 12 篇）——同仓两种哲学，按子系统风险等级取值。

## ⑥ 新人提示

写新 pipeline 任务的清单：实现 Pipeline 子类三段式 → 注册进 SUPPORTED_TASKS → 跑 check_pipeline_typing 重新生成 overload 区。排查"量化模型加载慢/显存爆"先看 get_modules_to_not_convert 的排除名单（lm_head 等），再查 before/after 钩子里是否整模型 dequantize。第三方量化库接入优先用 register_quantizer 装饰器而非改 auto.py——升级零冲突。读量化模型代码时记住 is_serializable（base.py:274）决定 save_pretrained 是否回写量化态，QAT 训练另查 is_qat_trainable（L260）。
