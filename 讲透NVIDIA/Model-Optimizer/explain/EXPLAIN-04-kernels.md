# EXPLAIN-04 · modelopt/torch/kernels：CUDA/Triton kernel 库——伪量化的"数值宪法"与"加速器"

## 一、角色定位

`modelopt/torch/kernels/` 只做一件事：**把"模拟量化"做到与真量化数值一致、且够快**。PTQ/QAT 校准阶段权重并不真转低精度，而是做量化-反量化（fake quant/QDQ），该操作在每个 Linear 前向都执行，kernel 层把它压进单次 launch。双重角色：①**校准加速器**——`NVFP4MSECalibrator`（`calib/mse.py:175`）的 Python 126 候选尺度 sweep 被融合进单次 Triton kernel，权重只读一遍显存、候选全在寄存器评估（`nvfp4_fp8_sweep.py:91-102`）；②**数值对齐基准**——kernel 输出就是部署引擎真量化 GEMM 的数值模拟，NVFP4 两级 scale 必须与硬件逐位一致，否则校准精度与上线精度脱节（Hessian 版 sweep 用参考实现预计算候选 scale 保持残差位级一致，`nvfp4_fp8_sweep.py:270-275`）。目录三线：`quantization/`、`common/attention/`、`sparsity/`；两代实现并存——JIT CUDA 扩展（`extensions.py:38-43` 按需编译）承担 INT8/FP8/MX/GGML，Triton 承担 NVFP4 与注意力线。

## 二、内部结构

### quantization/gemm/（14 文件，四类角色）

**① 通用整数伪量化 CUDA 扩展**（`tensor_quant.cpp/.cu/.h`）：pybind 导出 `fake_tensor_quant`（新张量）/`_`（原地）/`_with_axis`（per-channel）及 NF4/INT4 量化反量化共 8 入口（`tensor_quant.cpp:63-76`）。数学核心：`scale=max_bound/amax; out=clamp(round(x*scale))/scale`（`tensor_quant_gpu.cu:43-56`），bound 按 `(1<<(bits-1+unsigned))-1`（`:38-41`）；amax<fp16 最小值置零防溢出（`:46-48`）。per-axis 版每线程 4 元素、从线性下标反推 channel（`:111-119`）。NF4 走查表：16 代表值放 `__constant__`（`:142-144`），量化用线性扫描找最近邻（`:197-208`）后两个 nibble 打包进 uint8（`:229`）。**② FP8/MX 扩展**：`fake_e4m3fy_kernel` 用 `__nv_fp8_e4m3` 硬件类型 round-trip（`tensor_quant_gpu_fp8.cu:36-45`）；`tensor_quant_mx.h` 的 `enum class Types` 列九种 MX 格式（`:34`），E2M1 值表/边界表写成常量数组（`:37-38`）。**③ Triton NVFP4 家族**：能力门控在 `gemm/__init__.py:32-41`——fp4/fp8/sweep 任意 CUDA GPU，`fp4_kernel_hopper` 要求 compute≥8.9（`tl.float8e4nv`，Hopper/Blackwell）。舍入判定抽成单一来源 `common/nvfp4_quant.py`（"Single source of truth for FP4 decision-boundary rounding"，`:16-24`）：E2M1 仅 8 个代表值，`fp4_round_magnitude` 用 7 层嵌套 `tl.where`（`:43-63`）；零 scale 整块清零、NaN/inf 回退 1.0（`:90-101`）。三入口分层：`static_blockwise_fp4_fake_quant`（amax 已冻结，kernel 调 `nvfp4_scalar_quant`（`fp4_kernel.py:212`），scale 由 `compute_fp4_scales` 算 `amax/6.0` 再过 E4M3 round-trip（`:238-249`））；`fp4_fake_quant_block`（动态，`tl.make_block_ptr` tile 寻址（`fp4_kernel_hopper.py:56-71`），块内 amax+两级 scale（`:77-87`），`global_scale=global_amax/(6.0*448.0)`（`:130`））；`nvfp4_fp8_scale_sweep(_hessian)`——126 个 `valid_fp8/448` 候选（`_fp8_scale_candidates.py:26-31`）使 scale 的 FP8 round-trip 恒等，故不需 `float8e4nv`（`nvfp4_fp8_sweep.py:22-26`）；`tl.static_range` 编译期展开+寄存器 argmin（`:91-102`），autotune 配置来自 B300 实测（`:46-54`）；Hessian 版 loss 换 `dwᵀH dw`、`tl.dot(allow_tf32=False)` 保真 fp32（`:219-220`）。**④ GPTQ 融合**：一个 program 管一行权重，`w_full` 常驻寄存器，逐列 NVFP4 QDQ+误差传播 `w_full -= err_val*hinv_row`（`gptq_fused_kernel.py:82-89`），避免 Python 逐列循环（`:22-27`）。

**勘误**：`fp8_kernel.py` 不是 FP8 伪量化——是 DeepSeek-V3 移植的 MIT 协议**权重反量化** kernel（双版权头 `fp8_kernel.py:16-18`），按 128×128 块 scale 还原 W8A8 权重（`:46-72`），服务真量化侧的 checkpoint 回读；FP8 伪量化在 `tensor_quant_gpu_fp8.cu` 与 `fp8_quant.py` 的 `fp8_scalar_qdq`（clamp±448 后 round-trip，`:41-43`）。

### common/attention/ 与 sparsity/

`triton_fa.py`（1465 行）是 varlen+GQA+causal 的 FA2 式 kernel（`:17-23`），设计核心是**单 kernel 多特性**：N:M 稀疏、skip-softmax、P/V QDQ 全作 constexpr 参数挂在同一 `_attn_fwd`（`:305-319`），特性逻辑懒加载注入避免循环 import（`:37-45`）。P 的 QDQ 模式 `{None:0,"fp8":1,"nvfp4":2}`（`:74-76`）；在线 softmax 只把量化 P 喂 BMM2、分母保持 fp32（`:458-466`）——模拟"P 低精度进 MMA、累加器高精度"。`decode_attention.py` 是 split-K 解码 kernel（splits=32，`:39-41`），P QDQ 作用在 split 局部未归一化概率、数值含固定 split 数（`:17-21`），`v_quantized_boundary` 处理不满一个 NVFP4 块的尾段（`:89`）。`sparsity/gemm/__init__.py:16` 仅占位（2:4 稀疏执行在引擎侧）；`sparsity/attention/calibrate.py` 的 `_attn_fwd_calibrate` 一次前向统计所有候选阈值下的可跳过 KV tile 数（`:44-80`）。`ggml/` 六个 IQ 格式 pack kernel 编译成单扩展（`extensions.py:94-104`）。

## 三、外部连接

`quantization/tensor_quant.py` 是总闸门：INT8 按 amax 形状分流标量/按轴（`:106-110`）；动态 NVFP4 先试 Hopper Triton 再落 MX CUDA 扩展（`:178-191`）；两个入口导出为 autograd Function、backward 用 STE（`:702-705`）。`nn/modules/tensor_quantizer.py:937/1749` 是 `TensorQuantizer` 前向调用点；`calib/mse.py:227-275` 决定 Triton fast path 或 Python 回退；`plugins/huggingface.py:34-39,68` 做能力探测并用 `weight_dequant` 支撑 FP8 checkpoint 反量化。下游：`sparsity/attention_sparsity` 及 vllm 插件消费 attention kernel；`export/trtllm/tensorrt_llm_utils.py` 导出校验用同一 kernel 对拍。

## 四、数据流

NVFP4 全链：①校准期动态路径 `fp4_fake_quant_block`（tile→块 amax→两级 scale→舍入→STE）；②尺度精修 `nvfp4_fp8_scale_sweep(_hessian)` 输出每块 best_amax；③QAT/评估期静态路径 `static_blockwise_fp4_fake_quant`（无 GPU 时 Python 参考兜底）；④部署对齐——权重侧 GPTQ 逐块调 `gptq_fused_block_scalar` 边量化边传播误差，注意力侧 P/V QDQ 模拟引擎量化 MMA，amax 直接写进 TRT-LLM scale 表；⑤反向通道 `weight_dequant`/NF4 dequant 还原已量化权重。

## 五、设计决策

- **双语言分层**：CUDA 扩展稳（老格式、ABI 稳定），Triton 活（迭代快、免 nvcc，`inline_asm_elementwise` 可嵌 PTX——`fp4_kernel.py:96-112` 一条 `cvt.rn.f16x2.e2m1x2` 解包 4 个 FP4）。
- **数值单一来源**：E2M1 舍入只写一份（`nvfp4_quant.py:18-23` 列出全部消费者），cast kernel 复刻同一套嵌套 where（`fp4_kernel.py:336-360`）——改一处全局同步。
- **能力门控而非型号白名单**：`(8,9)` 来自 `get_device_capability()`（`gemm/__init__.py:38`）。
- **防御性数值边界成对出现**：CUDA 版 `tensor_quant_gpu.cu:46-48` 与 Triton 版 `fp4_kernel_hopper.py:73-83` 语义一致，两实现可互换；候选集模块零 Triton 依赖以便参考路径共用（`_fp8_scale_candidates.py:16-21`）。

## 六、新人提示

1. **改舍入逻辑先看 `nvfp4_quant.py`**：5 个文件引用它，局部小改会全局改变数值，已校准模型精度会漂移。
2. **`IS_AVAILABLE` 三处含义不同**：gemm 的（triton 可用）、attention 的（triton attention）、`hasattr(triton_kernel,"fp4_fake_quant_block")`（Hopper 动态路径，`tensor_quant.py:179`）——A100 上第三个为假。
3. **首次运行的编译等待正常**：CUDA 扩展 JIT 编译（`precompile()` 可预热），Triton autotune 首跑也慢。
4. **排数值 bug 先确认走哪条路径**：同一 NVFP4 语义有 Triton 动态/静态、MX CUDA、Python 参考四条实现，`DISABLE_TRITON_KERNEL` 可强制切换对拍。
5. **`fp8_kernel.py` 命名误导**（见二节勘误）：grep FP8 伪量化请找 `fp8_quant.py` 与 `tensor_quant_gpu_fp8.cu`。
