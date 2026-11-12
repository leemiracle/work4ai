# EXPLAIN-01 · torch 量化主线：quantize / calibrate / auto_quantize

> 对象：`modelopt/torch/quantization/model_quant.py`（1168 行）、`modelopt/torch/quantization/config.py`（1849 行）、`modelopt/torch/quantization/mode.py`（570 行）、`modelopt/torch/quantization/conversion.py`（683 行）
> 关系：model_quant 是用户 API 门面，config 是配置 schema 与预设仓库，mode 把校准算法装进 ModelOpt 模式机，conversion 负责模型换装与量化器属性写入。
> 锚点说明：本文短名锚（config.py / mode.py / conversion.py / calib/xx.py / nn/xx.py）均相对 `modelopt/torch/quantization/`；仓内 distill/speculative/sparsity 等包存在同名文件，检索时以本目录为准。

## 一、角色定位

`model_quant.py` 是整个 torch 量化栈的唯一用户入口，`__all__` 导出 12 个符号（model_quant.py:55-67），其中三大主流程构成产品主线：

- `quantize(model, config, forward_loop)`（model_quant.py:233）——"换装 + 校准"一站式入口；
- `calibrate(model, algorithm, forward_loop)`（model_quant.py:71）——单独重跑校准；
- `auto_quantize(...)`（model_quant.py:511）——逐层格式搜索。

它不直接操作 nn.Linear 之类的算子，而是把一切委托给 ModelOpt 通用模式机：`apply_mode(model, mode=[("quantize", dict(config))], registry=QuantizeModeRegistry)`（model_quant.py:332）。`QuantizeModeRegistry` 在 mode.py:77 创建，`QuantizeModeDescriptor.convert` 指向 `convert_to_quantized_model`（mode.py:109-111），后者再调 conversion.py:63 的换装实现。也就是说：**model_quant 管协议，conversion 管手术，mode 管注册与回放**。

辅助 API 同样关键：`disable_quantizer`/`enable_quantizer`（model_quant.py:984/989）只是 `set_quantizer_attributes_partial` 的开关糖衣；`fold_weight`（model_quant.py:1014）与 `temporarily_fold_weights`（model_quant.py:1025）为快速评测把假量化折进权重再原地还原（优化器/分布式引用不失效）；`compute_quantization_mse`（model_quant.py:1095）用 forward hook 逐量化器统计 Q/DQ 误差，是排障利器。

**勘误（甄别条款）**：任务书称 config.py 含 "SearchSpace"——实际 `modelopt/torch/quantization/config.py` 中并无此类；`SearchSpace` 是 NAS 包概念（modelopt/torch/nas/utils.py:43），量化搜索空间真正载体是 `algorithms.py` 的 `QuantRecipe`（algorithms.py:278）与 `AUTO_QUANTIZE_SEARCHERS` 注册表（algorithms.py:2105），另有 `AutoQuantizeModuleSearchSpace` 在 modelopt/recipe/config.py:223。另外 config.py 的配置类不是 dataclass，而是 pydantic `ModeloptBaseConfig`（config.py:158 引入 pydantic Field/validator）。

## 二、内部结构

**config.py 三层结构**：第一层 `QuantizerCfgEntry`（config.py:165）描述一条规则——`quantizer_name` 通配符 + 可选 `cfg` + 可选 `enable` + 可选 `parent_class`；第二层 `QuantizerAttributeConfig`（config.py:322）是量化器的属性全集，核心字段包括 `num_bits`（int 或 (E,M) 浮点元组或字符串，config.py:331）、`axis`（静态 per-channel 轴，config.py:433）、`fake_quant`（config.py:447）、`block_sizes`（config.py:487，NVFP4/MX 系动态分块）、`calibrator`（config.py:599，仅允许 "max"/"histogram" 或构造器）、`rotate`（config.py:616，QuaRot/SpinQuant 类旋转）、`pass_through_bwd`（config.py:627，STE 开关——QAT 精度的关键旋钮）、`backend`（config.py:644，自定义量化后端名）；第三层 `QuantizeConfig`（config.py:1567）= `quant_cfg` 列表 + `algorithm` + 可选 `effective_bits`。校准算法各有专属 config 类，全部继承 `QuantizeAlgorithmConfig`（config.py:799）：`MaxCalibConfig`(903)、`MseCalibConfig`(950)、`LocalHessianCalibConfig`(1002)、`SmoothQuantCalibConfig`(1071)、`AWQLite/Clip/FullCalibConfig`(1093/1117/1165)、`SVDQuantConfig`(1183)、`GPTQCalibConfig`(1213)、`NVFP4ActHeadroomCalibConfig`(1250)、`LSQConfig`(1325)——共 11 个算法模式，与 mode.py 的 descriptor 一一对应。

**预设不在 Python 里硬编码**：`FP8_DEFAULT_CFG`（config.py:1682）、`NVFP4_DEFAULT_CFG`(1716)、`INT4_AWQ_CFG`(1698) 等约 40 个预设全部经 `_load_quantize_config_dict`（config.py:1647）从 YAML 现载。例如 `modelopt_recipes/configs/ptq/presets/model/nvfp4.yaml` 只有 4 个有效行：`imports` 三件套 + `quant_cfg` 里的 `$import: base_disable_all / w4a4_nvfp4_nvfp4 / default_disabled_quantizers`，数值细节在 `configs/numerics/nvfp4_bs32.yaml`（`num_bits: e2m1` + `block_sizes: {-1: 32, type: dynamic, scale_bits: e4m3}`）。合法格式名集合 `choices` 在 config.py:1778 硬列。

**mode.py 的模式机**：`BaseCalibrateModeDescriptor`（mode.py:285）要求子类挂 `_calib_func` 类属性，`convert` property 包一层 `wrapped_calib_func`（mode.py:215）——它把 pydantic config dump 成 kwargs，抽出 `layerwise` 子配置（mode.py:230-236），有 `layerwise.enable` 时改走 `layerwise_calibrate`（mode.py:264-274），否则直调算法函数；最后 `update_quantize_metadata` 收集量化器状态。算法名到模式名的映射是 `algo + "_calibrate"`（None 则 `"_no_calibrate"`，mode.py:318-325），`get_modelike_from_algo_cfg`（mode.py:381）负责把字符串/dict/list 统一成模式配置。SVDQuant 特殊：`_supports_layerwise = False`（mode.py:541），因其 `create_and_replace_svdquant_linear_on_the_fly` 需要根模型上的 ModeloptStateManager。

**conversion.py 的手术刀**：`replace_quant_module`（conversion.py:214）先 `register_custom_model_plugins_on_the_fly` 探测模型类型注册插件，再递归 `_replace_quant_module`（conversion.py:233）——对每个命中 `QuantModuleRegistry` 的子模块在**父模块上 setattr** 换成量化版（conversion.py:237-239），最后打印插入的量化器数（conversion.py:229-230）。换装后的属性写入由 `set_quantizer_by_cfg`（conversion.py:245）驱动：无 `cfg` 的条目只经 `set_quantizer_attributes_partial`（conversion.py:443）翻转开关；带 `cfg` 的条目经 `set_quantizer_attributes_full`（conversion.py:373）**整体替换**属性——未写字段回默认值，且属性为 list 时会把 `TensorQuantizer` 升级成 `SequentialQuantizer`（W4A8 双层量化的机制，conversion.py:420-432），反之单 dict 会降级回来（conversion.py:434-439）。

## 三、外部连接

- **向上**：`modelopt.torch.quantization` 包 `__init__` re-export 全部 CFG 预设与 API；examples 与 Megatron/vLLM 集成层只认这套门面。
- **模式机**：`apply_mode`（opt/conversion.py:343）接收 `ModeConfigList`，逐模式调 `descriptor.convert(model, config, **kwargs)` 并由 `ModeloptStateManager` 记录——校准时 `mode_kwargs={"forward_loop": ...}` 正是穿过这条通道（model_quant.py:120-124），不可序列化对象因此不进 checkpoint。
- **向下**：换装产物是 `nn/` 包的 `QuantModule`/`TensorQuantizer`（如 tensor_quantizer.py:1146 的 forward）；校准算法函数全部来自 `model_calib.py`（mode.py:62-73 导入 max_calibrate/mse_calibrate/smoothquant/awq/gptq/lsq/svdquant/layerwise_calibrate 等 11 个符号）。
- **auto_quantize 生态**：`QuantRecipe`/`AUTO_QUANTIZE_SEARCHERS`（algorithms.py）+ `kv_cache_auto_quant.py`（KV cache 专用搜索，`_auto_quantize_kv_cache` 在 model_quant.py:403）+ Shapley 归因（`_auto_quantize_shapley.py`）。
- **导出**：`export_quantized_model` 直接 `raise NotImplementedError`（conversion.py:674-676）——torch 侧只做假量化模拟，真量化与导出走 `modelopt/torch/export` 与 TensorRT-LLM 管线。

## 四、数据流

`mtq.quantize(model, config, forward_loop)` 一次调用的完整轨迹：

1. **规范化**：`QuantizeConfig(**dict(config))`（model_quant.py:330），`normalize_quant_cfg_list`（config.py:1441）把旧版扁平 dict、单键 dict、`nn.*` 作用域三种遗留形态统一成 `QuantizerCfgEntry` 列表（并触发 DeprecationWarning）。
2. **换装**：未量化模型走 `apply_mode([("quantize", config)])` → `convert_to_quantized_model`（conversion.py:63）= `replace_quant_module` + `set_quantizer_by_cfg`；已量化模型跳过换装直接 `set_quantizer_by_cfg`（model_quant.py:333-335）——这就是"同一模型反复套不同 config"的机制。
3. **守门**：`_check_weight_quantization_took_effect`（model_quant.py:157/337）在**校准前**拦截"config 想量化权重但通配符没匹配到任何 weight_quantizer"的静默失败。它取每 pattern 的**最后一条** entry 判定意图（model_quant.py:195-201，后写覆盖先写），再扫模型确认至少一个 weight quantizer `is_enabled`（model_quant.py:209-214）；MoE 命名不匹配、流水线并行的空阶段 rank 都会命中此检查，可设 `MODELOPT_SKIP_WEIGHT_QUANT_CHECK=1` 绕过（model_quant.py:181/227）。
4. **校准**：`calibrate`（model_quant.py:338→71）先 eval、再 `forward_with_reshard` 上下文里 `apply_mode(mode=get_modelike_from_algo_cfg(algorithm))`（model_quant.py:119-124）——每个校准算法本身也是一个 mode，convert 即执行。零参 forward_loop 的旧用法被警告并包装（model_quant.py:99-113）。校准后逐量化器校验 `_amax`/`_pre_quant_scale` 是否有效（model_quant.py:126-129），最后恢复原 train/eval 状态。
5. **运行期**：前向到达 `TensorQuantizer.forward`（tensor_quantizer.py:1146）：pre_quant_scale 缩放 → 旋转 → `_if_calib` 时 `collect` 统计 → `_if_quant` 时按 `fake_quant` 分流——`fake_quant=True` 走 `_fake_quantize`（tensor_quantizer.py:1231-1233），`fake_quant=False` 且未 dequantize 时走 `_real_quantize`（tensor_quantizer.py:1234-1235，真量化路径，EXPLAIN-03 详述）。

`auto_quantize` 的轨迹（model_quant.py:511-943）：解析 `method`（gradient/kl_div/aumann_shapley，默认 gradient，model_quant.py:797）→ 未给格式时默认 `[NVFP4_AWQ_LITE_CFG, FP8_DEFAULT_CFG]`（model_quant.py:799-800）→ 校验每个格式的 algorithm 必须在 `_AUTO_QUANTIZE_SUPPORTED_ALGORITHMS`（model_quant.py:348-357，None/max/mse/local_hessian/smoothquant/awq_lite/awq_full/awq_clip 八种）→ `apply_mode(mode="auto_quantize")` 后**先全禁再搜**（model_quant.py:930-936）→ `searcher.search(model, constraints, config)`（model_quant.py:941）。搜索器按 `quant_grouping_rules`（algorithms.py:682）把 q/k/v_proj、MoE 专家 gate/up/down 等锁成同格式组——为的是 TensorRT-LLM 会把这些线性层融合，格式必须一致。搜索完成后 `get_auto_quantize_config(search_state, constraints)`（model_quant.py:946）可在不重跑 GPU 的情况下按新 `effective_bits` 重解（model_quant.py:966-967）。

## 五、设计决策

1. **"假量化换装"而非图重写**：不碰 ONNX/编译器，直接把 nn.Linear 换成带 `input_quantizer`/`weight_quantizer` 的 QuantLinear，forward 里原地做 Q/DQ 模拟。好处是与任意训练框架（含 Megatron 并行）兼容、QAT 只是"保持 fake_quant=True 继续训练"零额外开关——STE 与零化离群梯度由 `pass_through_bwd` 一个字段控制（config.py:627-642）。PTQ→QAT 的"场景切换"因此不是模式切换，而是同一模型在 calibrate（no_grad 收 amax）与 train（amex 冻结、权重可学，或 LSQ 连 amax 一起学，config.py:1325）之间换训练循环。
2. **config 即有序规则表**：deny-all 先行、逐条覆盖、末条胜出——`set_quantizer_by_cfg` 的文档明确"每个带 cfg 的条目是完整替换"（conversion.py:261-265）。这换来了表达力（`parent_class` 限定父类、fused-experts 名字归一化 `weight_quantizers.0` → `weight_quantizer`，conversion.py:317-341 让 MoE 也能被 `*weight_quantizer` 通配）。
3. **校准算法模式化**：每个算法注册成独立 mode（mode.py:412-570 共 12 个 descriptor），换来三件事：算法可单测、可链式（apply_mode 支持模式列表）、restore 时 `restore_quantizer_state`（conversion.py:125）按 metadata 里的 `quantizer_state` 精确回放（键不匹配直接抛 ApplyModeError，conversion.py:149-152）。代价是新增算法要同时写 config 类 + descriptor + calib 函数三处。
4. **预设外置 YAML + $import 组合**：约 40 个预设置于 `modelopt_recipes/configs/`，`base_disable_all`/数值块复用——改预设不发版、数值与策略解耦。
5. **回滚原语齐全**：`preserve_quantizer_attributes_context`（conversion.py:506）与 `set_quantizer_by_cfg_context`（conversion.py:567）在 auto_quantize 试每个候选格式时反复改写量化器属性再整体回滚（连 SequentialQuantizer↔TensorQuantizer 类型升降都恢复，conversion.py:534-564）；`temporarily_fold_weights` 快照权重到 CPU 再原地 copy_ 回来（model_quant.py:1070-1092）。

## 六、新人提示

- 读入口别迷路：一切从 model_quant.py 的三个函数进，看到 `apply_mode` 就跳 opt/conversion.py:343，看到 `convert_to_quantized_model` 就跳 conversion.py:63，校准算法实体全在 model_calib.py。
- 排查"导出的 checkpoint 没有量化层"先看 `_check_weight_quantization_took_effect` 的报错文案（model_quant.py:216-230）：九成是 MoE 命名与通配符不匹配，去 `modelopt_recipes/model_type/<model_type>/` 找对应配方。
- `set_quantizer_by_cfg` 的 full 替换语义最容易踩坑：想只改 `num_bits` 保留其他属性时，用 `set_quantizer_attributes_partial`（disable/enable_quantizer 就是这么做的，model_quant.py:986/991），不要塞进带 cfg 的条目。
- auto_quantize 提速先砍 `num_score_steps`（默认 128）而非 `num_calib_steps`（默认 512）——docstring 明说评分阶段才是大头（model_quant.py:540-542）。
- 想自定义量化模块：`mtq.register(original_cls, quantized_cls)`（conversion.py:620）要求量化类实现 `_setup` 建 quantizer 并在 forward 正确位置调用（conversion.py:637-654 有 LayerNorm 完整示例）。
- 校准算法与 layerwise 组合时注意 SVDQuant 不支持（mode.py:541 会 raise）；KV-cache auto_quantize 不支持多进程（model_quant.py:427-430）。
