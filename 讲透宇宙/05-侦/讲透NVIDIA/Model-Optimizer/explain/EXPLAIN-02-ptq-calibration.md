# EXPLAIN-02 · PTQ 校准算法中枢：model_calib 与 calib/ 包

> 对象：`modelopt/torch/quantization/model_calib.py`（实测 2410 行，任务书称 2068 行——以 `wc -l` 为准，勘误）、`calib/` 包（calibrator.py 75 行 / max.py 111 / mse.py 312 / histogram.py 434 / bias.py 179 / nvfp4_act_headroom.py 230）、`utils/layerwise_calib.py`（945 行）、`utils/calib_utils.py`（GPTQHelper）。
> 关系：model_calib 是全部校准算法的**函数级实现**（被 mode.py 的 descriptor 调用）；calib/ 是 amax/bias 统计器库；layerwise_calib 提供逐层执行框架。
> 锚点说明：短名锚均相对 `modelopt/torch/quantization/`（mode.py/config.py 指本目录文件；utils/calib_utils.py 注意与 modelopt/onnx/quantization/calib_utils.py 区分）。

## 一、角色定位

EXPLAIN-01 讲过：`mtq.calibrate` 把算法名翻译成 mode，mode 的 convert 最终落到 model_calib.py 里的普通函数。本文件因此是"算法中枢"——11 个算法函数（`max_calibrate`/`mse_calibrate`/`local_hessian_calibrate`/`smoothquant`/`awq`/`svdquant`/`gptq`/`lsq`/`nvfp4_act_headroom_calibrate`/`layerwise_calibrate`/`weight_only_quantize`）覆盖了从最朴素的取绝对最大值到 Hessian 加权补偿的全谱系。它们共享一套三段式协议：**enable_stats_collection → 前向收集 → finish_stats_collection**（model_calib.py:1135/1151）——前向期间量化器被切到校准态（disable_quant + enable_calib，model_calib.py:1145-1146），统计器在 `collect(x)` 里累积，结束后 `compute_amax()` 定标、`load_calib_amax` 写回、再 enable_quant 复原。所有算法的差异只在于"统计器是什么"和"误差怎么定义"。

`calib/` 包是统计器（calibrator）库：抽象基类 `_Calibrator` 只要求 `collect`/`reset`/`compute_amax` 三方法（calib/calibrator.py:51-69），且 `__init_subclass__` 自动把子类注册为 `torch.load(weights_only=True)` 的安全全局（calib/calibrator.py:43-49）——统计器对象随量化器 state_dict 序列化，这一行是 checkpoint 安全加载的前提。

## 二、内部结构

**基础统计器族**（calib/ 包，4 个具体类）：
- `MaxCalibrator`（calib/max.py:26）：`collect` 按量化轴 reduce 出局部 amax 再取全局 max（calib/max.py:63-83），带 nan/负值/inf 三重断言（calib/max.py:69-77）；`compute_amax` 直接返回累积值（calib/max.py:92-94）。最简单也最抗噪最差。
- `HistogramCalibrator`（calib/histogram.py:35）：一次收集、多次定标——`compute_amax(method)` 在 `entropy`/`mse`/`percentile` 三法间分派（calib/histogram.py:137-185）。直方图按需扩 bin（amax 超上界时 arange 追加，calib/histogram.py:95-107），支持 torch.histc GPU 路径（calib/histogram.py:118）。**entropy 法即 TensorRT 经典 KL 校准**：`_compute_amax_entropy`（calib/histogram.py:210-282）把候选截断 bin 量化回 128 档再算 `scipy.stats.entropy`（calib/histogram.py:273），取 KL 最小的 bin 边作 amax；`_compute_amax_mse`（calib/histogram.py:285）对每个候选 bin 中心做 `fake_tensor_quant`/`scaled_e4m3` 再按计数加权求 MSE；`_compute_amax_percentile`（calib/histogram.py:328）走 CDF 搜索。注意 axis 非 None 直接 NotImplementedError（calib/histogram.py:72-75）——直方图只支持 per-tensor。
- `MseCalibrator`（calib/mse.py:31）：与直方图 MSE 不同的**张量级搜索**——在初始 amax 的 [0.25, 4.0] 倍率区间按 step 0.1 生成候选（mse.py:71-75），每个候选跑真实量化函数 `_mse_quant_func`（model_calib.py:645-668，临时改写 quantizer 的 `_amax` 并启用 fake_quant 后调用），跨 batch 累积误差最后 argmin（mse.py:154-158）。per-channel 也支持（按通道独立 argmin）。
- `NVFP4MSECalibrator`（calib/mse.py:175）：NVFP4 静态量化的专用版，候选集不是线性倍率而是 **126 个合法 FP8 E4M3 scale 值**（`_generate_candidates` 调 `fp8_scale_candidates`，mse.py:219-225）；带两条 Triton 快路径——Hessian 加权 `nvfp4_fp8_scale_sweep_hessian` 与平差 `nvfp4_fp8_scale_sweep`（mse.py:264-279），条件不满足时回退 Python 参考 sweep（mse.py:283-293）。一次性 calibrator：二次 collect 直接 RuntimeError（mse.py:259-263）。

**bias 校正**：`BiasCalibrator`（calib/bias.py:100）走 running average（bias.py:126-144，注释明说经验上比 (max+min)/2 好）或 max_min 双计数（bias.py:145-154）；per-head per-channel 布局注释见 bias.py:114-124（attention [batch, heads, seq, dim] 用 axis=(-1,-3)）。挂载在量化器的 `bias_calibrator` 槽位（tensor_quantizer.py:495-498）。

**NVFP4 激活余量**：`NVFP4ActHeadroomCalibrator`（calib/nvfp4_act_headroom.py:36）解决"max 定标零余量"问题：`amax = max(rho * anchor, upper)`（nvfp4_act_headroom.py:47），anchor 取 per-block amax 分布的低分位、rho 默认 16384、上界 28672 恰为 FP8 E4M3 正常动态范围 448/2⁻⁶（nvfp4_act_headroom.py:27-30 的 `_FP8_NORMAL_DYNAMIC_RANGE` 与校验）。upper_percentile 默认 99.99 而非 100 的原因写在 docstring：单个 freak block 会把全局 scale 拉高到让其余 block 的 FP8 scale 落入 subnormal 清零（nvfp4_act_headroom.py:52-56）。

## 三、外部连接

- **向上**：mode.py 的 12 个 descriptor 以 `_calib_func` 类属性直连本文件函数（如 MaxCalibrateModeDescriptor._calib_func = max_calibrate，mode.py:433）；`wrapped_calib_func` 把 pydantic config dump 成 kwargs（mode.py:228-229）。
- **横向**：`_make_weight_mse_calibrator`（model_calib.py:671）按量化器形态选 calibrator：注册过 backend 的走 `_FP8_SWEEP_CALIBRATOR_REGISTRY` 工厂（model_calib.py:172 注册机制），静态 NVFP4 走 NVFP4MSECalibrator，其余走 MseCalibrator（model_calib.py:725-739）。
- **kernel 层**：NVFP4MSECalibrator 的两条 Triton 快路径 import 自 `modelopt.torch.kernels.quantization.gemm`（mse.py:243/265/273）——校准与真实 GEMM kernel 共享同一代码族（EXPLAIN-03 详述）。
- **分布式**：max_calibrate 内嵌 DP/EP/TP 三层 amax 同步（model_calib.py:367-410 区间），列并行/行并行的同步语义有整段注释推导（model_calib.py:404 起）；`sync_expert_weight_amax` 让 MoE SequentialMLP 全专家共享一个 weight amax。
- **GPTQHelper**（utils/calib_utils.py:116）：gptq 的引擎，正向 patch 收 Hessian（utils/calib_utils.py:147-165），`compute_hessian_inverse` 做阻尼 + 双 Cholesky 得上三角逆 Hessian 因子（utils/calib_utils.py:109-110），`gptq_blockwise_update`（utils/calib_utils.py:241）是列块更新本体，另有 fused Triton 版 `gptq_blockwise_update_fused_scalar`（utils/calib_utils.py:279）与 backend 注册口 `register_gptq_helper`（utils/calib_utils.py:319）。

## 四、数据流

**max 主线**（model_calib.py:317）：①`SharedWeightGlobalAmaxState.attach` 预挂共享态（model_calib.py:342-344）→ ②`enable_stats_collection` + `weight_only_quantize`（model_calib.py:348-349）——后者直接对每个 QuantModule 的权重张量调 `weight_quantizer(weight)` 完成权重定标（model_calib.py:193-207），不依赖数据前向；③`forward_loop(model)` 跑校准数据；④`finish_stats_collection` 定标回写；⑤MoE 专家 amax 本地同步（model_calib.py:361-364）；⑥`_finalize_with_shared_state` 聚合 fusible 兄弟组的全局 amax（model_calib.py:149）。`_needs_activation_forward_for_max_calib`（model_calib.py:271）判定纯权重/常数 amax 场景可跳过整个前向——experts-only 配方的省钱点。

**MSE/local_hessian 主线**：mse_calibrate（model_calib.py:739）先 max 初始化，再 `_mse_calibrate_weights`（model_calib.py:786）逐量化器换装搜索 calibrator 并 `_run_and_load_max_stats` 收权重统计（model_calib.py:808-812）。local_hessian_calibrate（model_calib.py:1011）在其上叠加三阶段：max → 禁权重假量化跑前向收集 `H = ΣXᵀX`（hooks 注册于 model_calib.py:942，前向包在 `set_quantizer_by_cfg_context` 里，model_calib.py:1067-1071）→ 把 `error_func`/`hessian` 注入 `_mse_calibrate_weights` 做 `(W−Wq)ᵀH(W−Wq)` 最小化（model_calib.py:1085-1096）。注意已知限制：per-block Hessian 不跨 rank 同步，多卡下结果可能分叉（model_calib.py:1073-1077 警告）。

**SmoothQuant 主线**（model_calib.py:1281）：先强制 input_quantizer 轴为 -1 跑 per-channel max（model_calib.py:1308-1315），然后 postprocess 里算 `scale_a = weight_scale^(1-α) / act_amax^α`（model_calib.py:1327），经 `apply_pre_quant_scale_and_smooth`（model_calib.py:1234）把 `1/scale_a` 折进权重、把 activation amax 换成 per-tensor（`_amax_for_smoothing` 留档，model_calib.py:1333-1338）。零 amax 通道 mask 与 [1e-4, 1e4] 钳制防溢出（model_calib.py:1341-1344）。

**AWQ 三变体**：统一入口 `awq`（model_calib.py:1369）在 `SequentialQuantizer.convert_to_single_quantizer` 上下文里组合 awq_lite 与 awq_clip。awq_lite（model_calib.py:1402）给每个 linear 挂 helper、patch forward，用 `get_scale = x_max^α / w_max^(1-α)` 归一化（model_calib.py:1481-1490）在 α∈[0,1] 步进 0.1 网格上按输出 MSE 择优（AWQLiteHelper 的 loss dict，model_calib.py:1443-1446）。awq_clip（model_calib.py:1732）扫 clip_ratio∈[0.5,1.0] 步进 0.05，per-block（NVFP4 时 per-tensor amax）搜索最优截断（model_calib.py:1775-1790）。

**SVDQuant**（model_calib.py:1987）：`svd` 把权重分解 float64 SVD 取 rank 截断（model_calib.py:1962-1984），低秩分支存 `svdquant_lora_a/b`，残差 `weight -= B@A` 后重置 amax（model_calib.py:2014-2020）；skip_layers 的层临时禁量化、退化为 max（model_calib.py:2023-2039）。执行顺序：换装 SVDQuantLinear → awq_lite → 逐层 SVD → max。

**GPTQ**（model_calib.py:2255）：max 定标 → 为每个量化 linear 建 GPTQHelper → **禁权重量化**跑前向收 Hessian（model_calib.py:2313-2316 的 `set_quantizer_by_cfg_context`）→ `handle.update_weights(block_size, perc_damp)` 做块式逆 Hessian 补偿更新（model_calib.py:2325-2328）。docstring 明确推荐 layerwise 模式 + batch size 1（model_calib.py:2278-2280）。

**LSQ**（model_calib.py:2362）：先 `_run_weight_scale_calibration`（model_calib.py:2340）跑 max/mse/local_hessian 之一初始化 scale，再对 `StaticBlockScaleQuantizer` 调 `enable_lsq`，把 pre/post 两个 amax 变成可学参数（`w_q = Q_STE(w/s_pre)·s_post`，model_calib.py:2375-2377）。

**逐层框架**：layerwise_calibrate（model_calib.py:2058）把任意 calib_func 逐 decoder 层执行。核心是 `LayerActivationCollector`（utils/layerwise_calib.py:190）的 skip/run/capture 三态状态机（`_patched_forward`，utils/layerwise_calib.py:308-331）：capture 态捕获入参即抛 `_EarlyStopForwardError` 截断前向（utils/layerwise_calib.py:351）；`_SkipLayer` 无参数替身让 accelerate/FSDP2 拿不到参数不做搬运（utils/layerwise_calib.py:72-79）；层外量化器由 `_OutsideQuantizerCalibrator`（utils/layerwise_calib.py:124）在隐藏 decoder 层的状态下单独校准（utils/layerwise_calib.py:160-188）。断点续跑靠 manifest + `_CheckpointState`（utils/layerwise_calib.py:565/686）。

## 五、设计决策

1. **统计器与算法解耦**：算法（model_calib）决定"怎么搜"，统计器（calib/）决定"怎么累计"。HistogramCalibrator 一次收集三种定标法复用（calib/histogram.py:207-209 注释自认这是向 collector/calibrator 分离过渡的第一步）；MseCalibrator 通过 `quant_func`/`error_func` 依赖注入（mse.py:41-42）让 local_hessian 无需子类即可加权。
2. **先 max 后精修的两段式**：mse/local_hessian/gptq/svdquant 全部以 max_calibrate 为第一阶段（model_calib.py:804/1054/2286/2063）——权重 amax 与分布式同步只需实现一次，精修算法专注误差函数。
3. **搜索空间物理约束优先**：NVFP4 的 scale 候选不是数学网格而是 FP8 E4M3 的 126 个可表示值（mse.py:220-225）——搜索解必然硬件可精确表示，避免"最优 amax 量化后自己就损失精度"的自指问题；headroom 校准的 rho 上界 28672 同样是 FP8 正常动态范围约束（nvfp4_act_headroom.py:77-80）。
4. **写回统一走 enable_weight_access_and_writeback**：Megatron 包装下权重可能是 DTensor/分片张量，所有改权重的算法（smoothquant 折 scale、GPTQ 更新、SVD 减秩）都包在这个上下文里（model_calib.py:1362/2330/2052）。
5. **layerwise 是框架不是算法**：通过 `calib_func` 参数化（model_calib.py:2060），任意算法获得"每层独立校准 + 输入激活缓存复用"能力；GPTQ/local_hessian 的 docstring 明说 layerwise+bs1 是推荐姿势（model_calib.py:2278/1091）——逐层隔离让 Hessian 更贴近该层真实输入分布。
6. **诚实告警优于静默**：Hessian 不同步（model_calib.py:1073）、awq_lite 无 forward_loop 跳过（model_calib.py:1420）、非 int8/非 per-channel 的层跳过 smoothing（model_calib.py:1347-1352）都是 warn 后继续——LLM 量化动辄几百层，单层失败不应炸整轮。

## 六、新人提示

- 读懂三段式协议（enable/forward/finish）后，任何新算法的入手点都是：选统计器 → 写误差函数 → 在 mode.py 注册 descriptor。`_Calibrator` 子类自动进 torch 安全全局（calib/calibrator.py:43-49），别漏这层含义：统计器会进 checkpoint。
- entropy/percentile 校准只在 `calibrator: histogram` 时可用（QuantizerAttributeConfig 的 calibrator 字段仅接受 "max"/"histogram"，config.py:609-613），且仅 per-tensor——per-channel 想用 entropy 会撞 NotImplementedError（calib/histogram.py:72）。
- 权重 MSE 搜索的真实成本在 `_mse_quant_func` 每候选跑一次完整量化（model_calib.py:645）；38 个候选 × 大权重是主要耗时，NVFP4 场景优先确认 Triton 快路径生效（环境变量 `MODELOPT_NVFP4_TRITON_SWEEP=0` 可关，mse.py:236）。
- 调 SmoothQuant 的 α：公式在 model_calib.py:1327，α=1 全部按激活、α=0 退化为纯权重；跳过警告（"Only int8 smoothing is supported"）说明你把 smoothquant 用在了非 INT8 配方上。
- GPTQ 想换自定义 backend 的量化函数：走 `register_gptq_helper`（utils/calib_utils.py:319），fused=True 时 NVFP4 静态量化走 Triton 标量融合路径（utils/calib_utils.py:279）。
- layerwise 断点续跑的 manifest 在 checkpoint_dir 下按层分目录（utils/layerwise_calib.py:565-605），`detect_resume_point`（utils/layerwise_calib.py:637）决定从哪层继续；`export_dir` 模式校准完的模型不能再用作推理（model_calib.py:2073-2075 警告）。
