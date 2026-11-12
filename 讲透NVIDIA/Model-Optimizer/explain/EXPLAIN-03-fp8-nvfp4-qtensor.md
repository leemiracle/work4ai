# EXPLAIN-03 · 真实量化张量与 GEMM 后端：qtensor / backends / kernels

> 对象：`qtensor/` 包（base_qtensor.py 242 行 / fp8_tensor.py 151 / nvfp4_tensor.py 408 / int4_tensor.py 130 / mxfp4_tensor.py 144 / mxfp8_tensor.py 262 / int8 / nf4）、`backends/`（gemm_registry.py 156 / nvfp4_gemm.py 269 / fp8_per_tensor_gemm.py 214）、`kernels/quantization/gemm/`（tensor_quant.cpp + tensor_quant_gpu*.cu、fp4_kernel.py、fp4_kernel_hopper.py）。
> 关系：qtensor 定义"量化后数据长什么样"，backends 决定"量化数据怎么真算 GEMM"，kernels 提供假量化模拟与打包的底层实现——三者合起来构成假量化（模拟）与真实量化（真算）的分水岭。
> 锚点说明：qtensor/ backends/ 短名锚相对 `modelopt/torch/quantization/`；kernels 锚相对 `modelopt/torch/kernels/quantization/gemm/`；quant_linear.py / tensor_quantizer.py 指 `modelopt/torch/quantization/nn/modules/` 下同名文件。

## 一、角色定位

EXPLAIN-01/02 讲的整条链路（fake_quant 换装、校准、搜格式）都是**模拟**：前向里 Q→DQ 往返，张量仍是 float，跑在普通 CUDA GEMM 上——目的是测精度。当要真正吃掉 4bit/8bit 的显存与算力收益时，走另一条链：`TensorQuantizer.forward` 在 `fake_quant=False` 时进入 `_real_quantize`（tensor_quantizer.py:796），把 float 权重打包成**真实量化张量**（qtensor 包），module.weight 变成 `QTensorWrapper`（base_qtensor.py:96）；此后前向遇到量化张量走 dequantize 分支（tensor_quantizer.py:1160-1161），或——若启用了 real-quant GEMM——直接用低精度 kernel 真算。入口 API 是 `mtq.compress`（compress.py:196），其模式描述符 `RealQuantizeModeDescriptor.convert` 指向 `compress_convert`（mode.py:186），逐模块把 `fake_quant` 翻转后调 `pack_real_quantize_weight`（compress.py:109）。

qtensor 包是"数据格式层"：8 个 QTensor 类（FP8/INT4/INT8/NVFP4/MXFP4/MXFP8/NF4 + 基类）各自实现 `quantize`（打包）与 `dequantize`（还原）协议。backends 包是"计算派发层"：`gemm_registry` 单例（gemm_registry.py:101）按 availability check 匹配专用 GEMM。kernels 目录是"算子层"：C++/CUDA 扩展（tensor_quant.cpp:46-59 绑定 `fake_tensor_quant`/`fake_tensor_quant_with_axis`）与 Triton kernel（fp4 系列）。

## 二、内部结构

**基类协议**（base_qtensor.py）：`BaseQuantizedTensor`（base_qtensor.py:40）只存 `metadata{shape, dtype}` + `_quantized_data`（自定义 dtype 的存储张量），要求子类实现 `quantize`/`dequantize`（base_qtensor.py:76/87）；`__init_subclass__` 自动注册 torch 安全全局以便 `weights_only=True` 加载（base_qtensor.py:67-73）。`QTensorWrapper`（base_qtensor.py:96）继承 `nn.Parameter` 把量化张量伪装成参数——`__new__` 取出 `_quantized_data` 当 data、把类名写进 metadata（base_qtensor.py:103-117），`to()` 覆写换设备时重建 wrapper（base_qtensor.py:123-131），`get_qtensor()` 用 metadata 还原完整 QTensor（base_qtensor.py:133-137）。`QFSDPParam`（base_qtensor.py:148）与 `dynamically_update_state_methods`（base_qtensor.py:172）让 FSDP2 分片/load_state_dict 不丢 metadata。打包入口 `pack_real_quantize_weight`（base_qtensor.py:205）的条件是三连：weight_quantizer 启用 + **非 fake_quant** + element_size>1（base_qtensor.py:215-220），然后 `module.weight = QTensorWrapper(module.weight_quantizer(module.weight))`（base_qtensor.py:224-225）。

**FP8QTensor**（fp8_tensor.py:33）：仅支持 E4M3；scale = amax/448.0（fp8_tensor.py:74），量化即 `(input/expanded_scales).to(torch.float8_e4m3fn)`（fp8_tensor.py:107）。支持 axis（per-channel）与 block_sizes（分块）两种粒度，块不整除时先 padding 再裁剪（fp8_tensor.py:64-65/110-111）。per-tensor 是其最常见形态（FP8_DEFAULT_CFG）。

**NVFP4QTensor**（nvfp4_tensor.py:49）——**双层 scale 的块量化**：E2M1 值查表 `e2m1_values` 16 个码点 ±{0,0.5,1,1.5,2,3,4,6}（nvfp4_tensor.py:26-27）；每 block 一个 FP8 E4M3 per-block scale（`_scale`），整张量一个全局 scale（`_double_scale` = amax/(E2M1_MAX·E4M3_MAX)，nvfp4_tensor.py:206-208）。静态路径从量化器预计算 amax 取 scale（nvfp4_tensor.py:140-162），动态路径现场 `reduce_block_amax`（nvfp4_tensor.py:193）。per-block scale 转 FP8 前 clamp 到 [2⁻⁹, 448] 防下溢为零/上溢为 NaN（nvfp4_tensor.py:32-46）。打包：`_cast_fp4` 用 `torch.searchsorted` 在 E2M1 边界上找码点、奇数边界 [0.75,1.75,3.5] 处补 round（nvfp4_tensor.py:231-251），两个 uint4 移位挤进一个 uint8（`(q[...,1::2]<<4)|q[...,0::2]`，nvfp4_tensor.py:338）。解包走反向查表（nvfp4_tensor.py:350-362）。

**勘误（甄别条款）其一**：任务书称 NVFP4 为 "block-32"——默认块长实为 **16**（`modelopt_recipes/configs/numerics/nvfp4.yaml` 的 `block_sizes: {-1: 16, type: dynamic, scale_bits: e4m3}`；该文件同时标注 effective_bits 4.5 的成本口径），block-32 是变体（`nvfp4_bs32.yaml`）。且 nvfp4 真算 GEMM 的可用性检查**只接受 block 16**（nvfp4_gemm.py:259-262）。

**MX 系**（OCP MX 格式）：`MXFP8QTensor`（mxfp8_tensor.py:26）元素 E4M3、**E8M0 纯 2 的幂 scale**（biased uint8 指数，mxfp8_tensor.py:38-40）、块长 32（`_real_quantize` 里强校验 BLOCK_SIZE=32，tensor_quantizer.py:811-814）；`MXFP4QTensor`（mxfp4_tensor.py:25）同理 E2M1+E8M0。与 NVFP4 的本质区别：scale 是 2 的幂（免乘法、无舍入）但只有 8 档动态范围 vs FP8 scale 连续但需乘法。**INT4QTensor**（int4_tensor.py:28）对称/非对称 per-block 整数打包；**NF4QTensor** 支持双重量化（scale 本身再量化，tensor_quantizer.py:841-854 产出 `_scale/_double_scale/_scale_zeros` 三件套）。

**派发层**：`GEMMRegistry`（gemm_registry.py:31）是 (gemm_func, availability_check) 列表，`find_match` 顺序探测取第一个命中（gemm_registry.py:79-95）。`enable_real_quant_gemm` 给 input+weight 量化器都启用的模块打 `_use_real_quant_gemm=True` 标（gemm_registry.py:104-125）。`RealQuantLinear`（quant_linear.py:196）的 forward 先问 `_should_run_real_quant_gemm`（校准态自动退回假量化，quant_linear.py:203-207），首次调用经 `find_match` 选定实现并缓存（quant_linear.py:212-220），命中则走真算分支否则回落父类假量化（quant_linear.py:222-242）。

## 三、外部连接

- **TensorRT-LLM**：nvfp4_gemm 直接 `import tensorrt_llm._torch` 并调 `torch.ops.trtllm.fp4_quantize`/`torch.ops.trtllm.nvfp4_gemm`（nvfp4_gemm.py:30/56-60）——真算路径不自写 CUTLASS 而是复用 TRT-LLM 官方算子；NVFP4QTensor.quantize 的 `try_tensorrt=True` 快路径同样（nvfp4_tensor.py:286-314），dequantize 时若 scale 是 uint8 需做 cutlass→modelopt scale 换算（nvfp4_tensor.py:365-378）。
- **PyTorch 原生 FP8**：fp8_per_tensor_gemm 用 `torch._scaled_mm` + `use_fast_accum=True`（fp8_per_tensor_gemm.py:34-44），量化/反量化辅助函数用 `@torch.compile(dynamic=True)` 包裹（fp8_per_tensor_gemm.py:27-30）。
- **校准侧反哺**：EXPLAIN-02 的 NVFP4MSECalibrator Triton 快路径（`nvfp4_fp8_scale_sweep`）与本目录同源；`_fp8_scale_candidates.py` 提供 126 个合法 E4M3 scale 候选。
- **导出侧**：`get_activation_scaling_factor`（nvfp4_tensor.py:211-228）按 amax/(maxbound·E4M3_MAX) 计算导出 scale——TensorRT-LLM checkpoint 的 `input_scale` 字段即由此而来。
- **测试**：`tests/gpu_trtllm/torch/quantization/backends/` 是这两个 GEMM 后端的专属测试位。

## 四、数据流

**真量化权重（compress）**：`mtq.compress(model, {"default": True})` → compress_convert 翻转 `fake_quant=False`（compress.py:91）→ `pack_real_quantize_weight` 逐模块调 `weight_quantizer(weight)`，即 `TensorQuantizer.forward` 的 `_real_quantize` 分支（tensor_quantizer.py:1234-1235）。`_real_quantize`（tensor_quantizer.py:796）按格式分派：MX 系（(2,1)=MXFP4 / (4,3)+block32=MXFP8，tensor_quantizer.py:811-820）→ FP8（tensor_quantizer.py:823-835，amax 可用时作 per-tensor scale）→ INT8 → NF4 双重量化 → NVFP4（scale_bits==(4,3)，tensor_quantizer.py:855-874，`try_tensorrt=True`）→ INT4 兜底；scale 三件套 `_scale/_double_scale` 注册为量化器 buffer（tensor_quantizer.py:876-878），`_dequantize=True` 让后续前向只做解包（tensor_quantizer.py:884-885）。

**NVFP4 真算 GEMM**（nvfp4_gemm.py:28）：①输入全局 scale = 448·6/amax 并缓存（nvfp4_gemm.py:76-78）；②权重已压缩则直接取 `_quantized_data` 与 `_scale`、全局 scale 取 `_double_scale` 倒数（nvfp4_gemm.py:83-90），未压缩则现场 `trtllm.fp4_quantize`（nvfp4_gemm.py:107-109）；③`alpha = 1/(weight_gs·input_gs)` 汇总缩放（nvfp4_gemm.py:114-116）；④`_fp4_linear`：输入量化成 FP4 + block scale，调 `trtllm.nvfp4_gemm` 出高精度输出（nvfp4_gemm.py:56-60）。availability check 五关：TRT-LLM 可导入、`fp4_compatible()`（backends/utils.py:28）、模块是 RealQuantLinear、量化器属性逐项等于 NVFP4_DEFAULT_CFG 对应条目（nvfp4_gemm.py:233-251）、形状约束 input%64==0 且 weight%32==0（nvfp4_gemm.py:255）、block==16（nvfp4_gemm.py:259-262）。**反向传播**：`Nvfp4Linear.backward` 对压缩权重先 `dequantize(fast=True)`（走 Triton `fp4_dequantize` kernel，nvfp4_tensor.py:380-389）再算梯度——权重梯度在 float 域累加，支持训练态（nvfp4_gemm.py:150-184）。

**FP8 per-tensor 真算**：scale_a/scale_b = amax/448 缓存（fp8_per_tensor_gemm.py:48-66），`torch._scaled_mm(input_fp8, weight_fp8ᵀ, scale_a, scale_b, use_fast_accum)` 出结果（fp8_per_tensor_gemm.py:37-44）。**勘误（甄别条款）其二**：fp8_per_tensor_gemm.py 末尾虽有注册（`gemm_registry.register(Fp8PerTensorLinear.apply, ...)`），但 `backends/__init__.py` 只导入 `gemm_registry` 与 `nvfp4_gemm`（backends/__init__.py:18-19）——生产 import 路径不会自动注册 FP8 真算后端，目前只有 gpu_trtllm 测试直接 import 该模块；NVFP4 是唯一默认挂载的真算 GEMM。

**假量化（模拟）侧的 kernel 分工**：`TensorQuantizer._fake_quantize` 调的 `fake_tensor_quant`/`scaled_e4m3` 走 C++/CUDA 扩展（tensor_quant.py:95-124 分派，binding 在 tensor_quant.cpp:37-59，kernel `fake_tensor_quant_kernel` 在 tensor_quant_gpu.cu:59）；动态块量化（MX/NVFP4 dynamic）注册为 `torch.library` 算子 `tensorrt::dynamic_block_quantize_op`（tensor_quant.py:229-266）。Triton 侧 fp4_kernel.py 提供 `compute_fp4_scales`/`static_blockwise_fp4_fake_quant`/`static_blockwise_fp4_cast`/`fp4_dequantize`（fp4_kernel.py:217/254/366/150）。**勘误（甄别条款）其三**：任务书称 kernels 下有 "tensor_quant.cu"——实际是 tensor_quant.cpp（绑定）+ tensor_quant_gpu.cu / tensor_quant_gpu_fp8.cu / tensor_quant_mx.cu（kernel）；"Hopper/Blackwell 分版"更精确的表述是：fp4_kernel.py 适配任意 CUDA GPU，fp4_kernel_hopper.py 仅在 compute capability ≥ 8.9（Hopper 起，用 `tl.float8e4nv`）时导入（kernels/quantization/gemm/__init__.py:24-37）——Blackwell 同样满足 ≥8.9，两个文件都能跑，并非 Hopper/Blackwell 各一份。

## 五、设计决策

1. **"格式即类"而非"格式即分支"**：每种数值格式一个 QTensor 类实现打包/解包协议，`_real_quantize` 只做一次 if-elif 分派（tensor_quantizer.py:796-878）。新增格式（如未来 FP6）不动 GEMM 层——代价是 scale 语义（FP8 连续 vs E8M0 幂次 vs 双层）必须在类内自洽。
2. **metadata 伴随式存储**：QTensorWrapper 把 shape/dtype/类名藏进 metadata 字典（base_qtensor.py:110-116），使 uint8 打包数据能伪装成 Parameter 参与 `.to()`/FSDP/state_dict 而不丢还原信息——这是"压缩模型还能继续训练/保存"的关键妥协（quant_linear.py:245-265 的 RealQuantParameterDict 进一步拦截 transformers 加载）。
3. **真算不自写 kernel**：NVFP4/FP8 真算全部委托 TRT-LLM torch ops 或 `torch._scaled_mm`（nvfp4_gemm.py:56-60；fp8_per_tensor_gemm.py:37-44）。ModelOpt 的定位是量化决策层（搜格式、校准、打包），算力层交给硬件厂商库——与 TensorRT-LLM blog26 所述"TRT-LLM 反向集成 DeepGEMM"是同一哲学。
4. **可用性检查逐属性比对预设**：`_nvfp4_availability_check` 把模块量化器属性与 NVFP4_DEFAULT_CFG 逐项核对（nvfp4_gemm.py:233-251），防止"校准时是别的格式、真算时错配 kernel"的静默精度事故；形状整除约束（%64/%32）来自 kernel 内部 tile 要求（注释直说 input 不整除 64 会出 NaN，nvfp4_gemm.py:253-255）。
5. **模拟与真算共用校准产物**：`_double_scale`/`_scale` 既是假量化 forward 的 buffer，又是 GEMM 的 scale 输入与导出字段——同一次校准服务三条下游（模拟评测/真算/导出），避免"校准了两遍结果不一致"。
6. **backward 用 dequantize 近似**：FP4 权重的输入梯度在反量化后的 float 权重上计算（nvfp4_gemm.py:160-171）——承认低精度梯度不稳定的现实，用"前向真算、反向高精度"的混合策略换训练稳定性。

## 六、新人提示

- 看懂分水岭只需追两个标志：量化器 `_fake_quant` 布尔（假量化开关，base_qtensor.py:218 的打包条件取反它）与模块 `_use_real_quant_gemm`（gemm_registry.py:125）。前者管权重形态，后者管 forward 走哪条 GEMM。
- NVFP4 调试顺序：先确认 block size 是 16 还是 32（numerics/nvfp4.yaml vs nvfp4_bs32.yaml）——块 32 的配置**没有真算 GEMM**（nvfp4_gemm.py:259-262），只能模拟或导出；4/6 混合模式（four_over_six）明确不支持 compress 路径（tensor_quantizer.py:858-863 raise NotImplementedError）。
- E2M1 查表与奇数边界 round（nvfp4_tensor.py:243-248）是仿真与硬件一致性的细节：自己写 FP4 参考实现时漏掉 round 会在对比测试里出现系统性偏差。
- `_scaled_mm` 的 bias 限制：float32 输入不支持 bias 参数，fp8_per_tensor_gemm.py:83-85 手工补加——复用该函数时注意。
- 阅读顺序建议：base_qtensor.py 的 3 个类（40/96/148 行）→ fp8_tensor.py 全文（最简单的完整样例）→ nvfp4_tensor.py 的 quantize/dequantize → nvfp4_gemm.py 的 `_nvfp4_availability_check`（读懂它就读懂了整个真算准入体系）。
- 想注册自定义 GEMM：仿照 nvfp4_gemm.py:266-269 调 `gemm_registry.register(gemm_func, availability_check)`，并把 import 挂进 backends/__init__.py——别忘了 FP8 后端的前车之鉴（写了注册却没人 import）。
